#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H24 US Economic Policy Uncertainty -> Call Language Uncertainty
================================================================================
ID: econometric/run_h24_us_epu
Description: Reverse-direction suite - aggregate US Economic Policy Uncertainty
             (Baker, Bloom & Davis 2016, QJE) predicts call-level language
             uncertainty.

8 Model Specifications (matches H23 house pattern):
    Cols 1-4:  Industry (FF12) + Calendar Year FE  (one per DV)
    Cols 5-8:  Firm + Calendar Year FE             (one per DV)
    DVs in order: UncAnsMgr, UncPreMgr, UncAnsCEO, UncPreCEO (contemp only)

IV identification: within-year cross-firm variation in monthly-matched US_EPU.
Calendar Year FE absorbs the year-level mean of US_EPU; monthly matching
preserves substantial within-year variation across firms with calls in
different months (within-year std ~0.15-0.36 log points).

Estimator: PanelOLS.
Panel index: (gvkey, cal_yr_qtr) - preserves quarterly observations and
             enables two-way clustering by firm and calendar year-quarter.
Calendar Year FE: added via other_effects=cal_yr (NOT time_effects, which
             would create year-quarter dummies and fully absorb the IV).
Industry FE: absorbed via other_effects=ff12_code.
Firm FE: entity_effects=True.
Clustering: two-way (firm, cal_yr_qtr).

Hypothesis (one-tailed, positive):
    H24: beta(log(US EPU)) > 0

Sample: Main only (FF12 != 8, 11).

Inputs:
    - outputs/variables/h24_h24b_h25_macro/latest/h24_h24b_h25_macro_panel.parquet

Outputs:
    - outputs/econometric/h24_us_epu/{timestamp}/regression_results_col{1..8}.txt
    - outputs/econometric/h24_us_epu/{timestamp}/h24_us_epu_table.tex
    - outputs/econometric/h24_us_epu/{timestamp}/model_diagnostics.csv
    - outputs/econometric/h24_us_epu/{timestamp}/summary_stats.csv / .tex
    - outputs/econometric/h24_us_epu/{timestamp}/sample_attrition.csv / .tex
    - outputs/econometric/h24_us_epu/{timestamp}/run_manifest.json

Reference: Baker, Bloom & Davis (2016) "Measuring Economic Policy Uncertainty"
           Quarterly Journal of Economics 131(4): 1593-1636.

Author: Thesis Author
Date: 2026-04-10
================================================================================
"""

from __future__ import annotations

import argparse
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

from f1d.shared.latex_tables_accounting import make_summary_stats_table
from f1d.shared.logging.config import setup_run_logging
from f1d.shared.outputs import (
    extract_coefs_panelols,
    generate_attrition_table,
    generate_manifest,
    write_suite_spec,
)
from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.variables.panel_utils import assign_industry_sample

warnings.filterwarnings(
    "ignore", message="covariance of constraints does not have full rank"
)

# ==============================================================================
# Suite-specific configuration
# ==============================================================================

# Macro IV column (the ONLY thing that differs between H24, H24b, H25 runners)
MACRO_IV = "US_EPU_log"
MACRO_IV_RAW = "US_EPU"
MACRO_IV_LABEL = r"$\log(\text{US EPU})_{t}$"

SUITE_ID = "H24"
SUITE_NAME = "H24_US_EPU"
SUITE_DIR = "h24_us_epu"
SUITE_TITLE = "US Economic Policy Uncertainty and Call Language Uncertainty"
SUITE_CAPTION = (
    "H24: US Economic Policy Uncertainty and Call Language Uncertainty"
)
SUITE_LABEL = "tab:h24_us_epu"

# ------------------------------------------------------------------
# Suite metadata for suite_spec.json emission (single sub-table, 2-row header).
# Macro IV suites use two-way clustering (firm, cal_yr_qtr) and no
# Year-Quarter FE (would absorb the macro IV).
# ------------------------------------------------------------------
SAMPLE_LABEL = (
    "Main sample (excludes financial and utility firms). "
    "Firms with fewer than 5 calls are excluded."
)
HYP_DIR = "positive"  # H24: log(US EPU) -> higher speech uncertainty
CLUSTERING = {"entity": True, "time": True}
TAIL = {"direction": HYP_DIR, "applies_to": "ivs_only"}
EXTENDED_ONLY_CONTROLS: List[str] = []  # Macro suites have no extended set

PANEL_INPUT_DIR = "h24_h24b_h25_macro"
PANEL_INPUT_FILE = "h24_h24b_h25_macro_panel.parquet"

CONFIG = {
    "min_calls": 5,
}

# 4 contemporaneous uncertainty DVs (used across 2 FE types = 8 cols)
DVS = ["UncAnsMgr", "UncPreMgr", "UncAnsCEO", "UncPreCEO", "UncAnsNoCEO", "UncPreNoCEO"]

DV_LABELS = {
    "UncAnsMgr": "Mgr QA",
    "UncPreMgr": "Mgr Pres",
    "UncAnsCEO": "CEO QA",
    "UncPreCEO": "CEO Pres",
    "UncAnsNoCEO": "NoCEO QA",
    "UncPreNoCEO": "NoCEO Pres",
}

# H11-style base controls (excluding presentation control, which is DV-dependent,
# and Lagged_DV, which is also DV-dependent)
BASE_CONTROLS = [
    "UncQue",
    "NegCall",
    "lnAssets",
    "TobinsQ",
    "ROA",
    "CashRatio",
    "DivDummy",
    "FirmMat",
    "EarnVol",
]

# Presentation-control map: when DV is a Q&A measure, the matching
# contemporaneous Presentation measure is added as a control.
PRES_CONTROL_MAP = {
    "UncAnsMgr": "UncPreMgr",
    "UncAnsCEO": "UncPreCEO",
    "UncAnsNoCEO": "UncPreNoCEO",
    "UncPreMgr": None,
    "UncPreCEO": None,
    "UncPreNoCEO": None,
}

# 12 model specifications: 6 DVs x 2 FE types
MODEL_SPECS = [
    # Industry + Calendar Year FE (cols 1-6)
    {"col": 1, "dv": "UncAnsMgr", "fe": "industry"},
    {"col": 2, "dv": "UncPreMgr", "fe": "industry"},
    {"col": 3, "dv": "UncAnsCEO", "fe": "industry"},
    {"col": 4, "dv": "UncPreCEO", "fe": "industry"},
    {"col": 5, "dv": "UncAnsNoCEO", "fe": "industry"},
    {"col": 6, "dv": "UncPreNoCEO", "fe": "industry"},
    # Firm + Calendar Year FE (cols 7-12)
    {"col": 7, "dv": "UncAnsMgr", "fe": "firm"},
    {"col": 8, "dv": "UncPreMgr", "fe": "firm"},
    {"col": 9, "dv": "UncAnsCEO", "fe": "firm"},
    {"col": 10, "dv": "UncPreCEO", "fe": "firm"},
    {"col": 11, "dv": "UncAnsNoCEO", "fe": "firm"},
    {"col": 12, "dv": "UncPreNoCEO", "fe": "firm"},
]


# ==============================================================================
# Summary Statistics
# ==============================================================================

SUMMARY_STATS_VARS = [
    {"col": "UncAnsMgr", "label": "Mgr QA Uncertainty"},
    {"col": "UncPreMgr", "label": "Mgr Pres Uncertainty"},
    {"col": "UncAnsNoCEO", "label": "Non-CEO Mgr QA Uncertainty"},
    {"col": "UncPreNoCEO", "label": "Non-CEO Mgr Pres Uncertainty"},
    {"col": "UncAnsCEO", "label": "CEO QA Uncertainty"},
    {"col": "UncPreCEO", "label": "CEO Pres Uncertainty"},
    {"col": MACRO_IV_RAW, "label": "US EPU (raw)"},
    {"col": MACRO_IV, "label": "log(US EPU)"},
    {"col": "UncQue", "label": "Analyst QA Uncertainty"},
    {"col": "NegCall", "label": "Negative Sentiment"},
    {"col": "lnAssets", "label": "Firm Size (log AT)"},
    {"col": "TobinsQ", "label": "Tobin's Q"},
    {"col": "ROA", "label": "ROA"},
    {"col": "CashRatio", "label": "Cash Holdings"},
    {"col": "DivDummy", "label": "Dividend Payer"},
    {"col": "FirmMat", "label": "Firm Maturity"},
    {"col": "EarnVol", "label": "Earnings Volatility"},
]


# ==============================================================================
# CLI Arguments
# ==============================================================================


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=f"Stage 4: Test {SUITE_ID} {MACRO_IV} -> Language Uncertainty",
    )
    parser.add_argument(
        "--panel-path",
        type=str,
        default=None,
        help="Explicit path to shared H24/H24b/H25 panel parquet",
    )
    return parser.parse_args()


# ==============================================================================
# Data Loading & Preparation
# ==============================================================================


def _required_columns() -> List[str]:
    """All columns needed from the panel."""
    cols: List[str] = [
        "file_name",
        "gvkey",
        "start_date",
        "cal_yr",
        "cal_qtr",
        "cal_yr_qtr",
        "ff12_code",
        "sample",
    ]
    cols += [
        "GPR",
        "US_EPU",
        "GEPU_current",
        "GPR_log",
        "US_EPU_log",
        "GEPU_log",
    ]
    cols += DVS
    cols += [f"{d}_lag" for d in DVS]
    cols += BASE_CONTROLS
    seen = set()
    unique: List[str] = []
    for c in cols:
        if c not in seen:
            seen.add(c)
            unique.append(c)
    return unique


def prepare_regression_data(
    panel: pd.DataFrame,
    dv_var: str,
) -> Tuple[pd.DataFrame, List[str]]:
    """Complete-case filter for a specific DV + its dynamic controls."""
    pres_source = PRES_CONTROL_MAP.get(dv_var)

    controls = list(BASE_CONTROLS)
    if pres_source:
        controls.append(pres_source)
    controls.append("Lagged_DV")

    df = panel.copy()
    df["Lagged_DV"] = df[f"{dv_var}_lag"]

    required = (
        [dv_var, MACRO_IV]
        + list(BASE_CONTROLS)
        + ([pres_source] if pres_source else [])
        + ["Lagged_DV", "gvkey", "cal_yr_qtr", "cal_yr", "ff12_code"]
    )
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in panel: {missing}")

    df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=required).copy()
    df["cal_yr"] = df["cal_yr"].astype(int)
    df["ff12_code"] = df["ff12_code"].astype(int)
    return df, controls


# ==============================================================================
# Regression
# ==============================================================================


def run_regression(
    df_sample: pd.DataFrame,
    spec: Dict[str, Any],
    controls: List[str],
) -> Tuple[Any, Dict[str, Any]]:
    """Run PanelOLS with Industry or Firm FE + Calendar Year FE.

    Industry FE branch: entity_effects=False, other_effects=[ff12_code, cal_yr]
    Firm FE branch:     entity_effects=True,  other_effects=[cal_yr]

    Panel index (gvkey, cal_yr_qtr) is preserved for two-way clustering
    (firm, cal_yr_qtr). Calendar Year FE is added via other_effects (not
    via time_effects, which would be year-quarter FE and fully absorb the
    monthly macro IV).
    """
    col_num = spec["col"]
    dv_var = spec["dv"]
    fe_type = spec["fe"]

    exog = [MACRO_IV] + controls

    print(f"\n{'=' * 60}")
    print(f"Col ({col_num}) | DV={DV_LABELS.get(dv_var, dv_var)} | FE={fe_type}")
    print(f"{'=' * 60}")
    print(
        f"  N calls: {len(df_sample):,}  |  N firms: {df_sample['gvkey'].nunique():,}"
    )
    print(f"  Controls: {controls}")
    print("  Two-way clustered SEs (firm, cal_yr_qtr)")

    t0 = datetime.now()

    df_panel = df_sample.set_index(["gvkey", "cal_yr_qtr"])

    try:
        if fe_type == "industry":
            other_effects = df_panel[["ff12_code", "cal_yr"]]
            model_obj = PanelOLS(
                dependent=df_panel[dv_var],
                exog=df_panel[exog],
                entity_effects=False,
                time_effects=False,
                other_effects=other_effects,
                drop_absorbed=True,
                check_rank=False,
            )
        else:  # firm
            other_effects = df_panel[["cal_yr"]]
            model_obj = PanelOLS(
                dependent=df_panel[dv_var],
                exog=df_panel[exog],
                entity_effects=True,
                time_effects=False,
                other_effects=other_effects,
                drop_absorbed=True,
                check_rank=False,
            )

        model = model_obj.fit(
            cov_type="clustered",
            cluster_entity=True,
            cluster_time=True,
        )
    except Exception as e:
        print(f"  ERROR: Regression failed: {e}", file=sys.stderr)
        return None, {}

    duration = (datetime.now() - t0).total_seconds()
    adj_r2 = 1 - (1 - model.rsquared) * (model.nobs - 1) / model.df_resid
    print(f"  [OK] {duration:.1f}s  R2={model.rsquared:.4f}  AdjR2={adj_r2:.4f}  N={int(model.nobs):,}")

    beta = float(model.params.get(MACRO_IV, np.nan))
    p_two = float(model.pvalues.get(MACRO_IV, np.nan))
    se = float(model.std_errors.get(MACRO_IV, np.nan))
    t_stat = float(model.tstats.get(MACRO_IV, np.nan))

    if not np.isnan(p_two) and not np.isnan(beta):
        p_one = p_two / 2 if beta > 0 else 1 - p_two / 2
    else:
        p_one = np.nan

    sig = not np.isnan(p_one) and p_one < 0.05 and beta > 0
    print(
        f"  beta({MACRO_IV}): {beta:.4f}  SE={se:.4f}  p(1-tail)={p_one:.4f}  "
        f"sig={'YES' if sig else 'no'}"
    )

    meta = {
        "col": col_num,
        "suite": SUITE_ID,
        "dv": dv_var,
        "fe": fe_type,
        "macro_iv": MACRO_IV,
        "pres_control": PRES_CONTROL_MAP.get(dv_var) or "",
        "n_obs": int(model.nobs),
        "n_firms": df_sample["gvkey"].nunique(),
        "n_clusters_entity": df_sample["gvkey"].nunique(),
        "n_clusters_time": df_sample["cal_yr_qtr"].nunique(),
        "cluster_type": "two-way (gvkey, cal_yr_qtr)",
        "r2": float(model.rsquared),
        "adj_r2": float(adj_r2),
        "beta": beta,
        "beta_se": se,
        "beta_t": t_stat,
        "beta_p_two": p_two,
        "beta_p_one": p_one,
        "sig_one_tail": bool(sig),
    }

    return model, meta


# ==============================================================================
# LaTeX Table (8 columns: 4 DVs x Industry/Firm FE)
# ==============================================================================


def _sig_stars_one(p: float, beta: float) -> str:
    if np.isnan(p) or np.isnan(beta):
        return ""
    if beta <= 0:
        return ""
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return ""


def _save_latex_table(all_results: List[Dict[str, Any]], out_dir: Path) -> None:
    """Write 8-column LaTeX table: 4 DVs x Industry/Firm FE groups."""
    tex_path = out_dir / f"{SUITE_DIR}_table.tex"

    by_col = {r["col"]: r for r in all_results if r.get("col")}

    def fmt_coef(m: Dict[str, Any]) -> str:
        beta = m.get("beta", np.nan)
        p_one = m.get("beta_p_one", np.nan)
        if np.isnan(beta):
            return ""
        stars = _sig_stars_one(p_one, beta)
        return f"{beta:.4f}{('^{' + stars + '}') if stars else ''}"

    def fmt_se(m: Dict[str, Any]) -> str:
        se = m.get("beta_se", np.nan)
        return "" if np.isnan(se) else f"({se:.4f})"

    def fmt_int(m: Dict[str, Any]) -> str:
        n = m.get("n_obs", 0)
        return f"{n:,}" if n else ""

    def fmt_r2(m: Dict[str, Any], key: str) -> str:
        v = m.get(key, np.nan)
        if np.isnan(v):
            return ""
        return f"{v:.2e}" if abs(v) < 0.001 else f"{v:.3f}"

    def row(label: str, cells: List[str]) -> str:
        return f"{label} & " + " & ".join(cells) + r" \\"

    cols = list(range(1, 13))
    results = [by_col.get(c, {}) for c in cols]

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        rf"\caption{{{SUITE_CAPTION}}}",
        rf"\label{{{SUITE_LABEL}}}",
        r"\small",
        r"\begin{tabular}{l" + "c" * 12 + r"}",
        r"\toprule",
        r" & \multicolumn{6}{c}{Industry + Cal.~Year FE} & \multicolumn{6}{c}{Firm + Cal.~Year FE} \\",
        r"\cmidrule(lr){2-7} \cmidrule(lr){8-13}",
        r" & "
        + " & ".join([DV_LABELS[MODEL_SPECS[c - 1]["dv"]] for c in cols])
        + r" \\",
        r" & " + " & ".join(f"({c})" for c in cols) + r" \\",
        r"\midrule",
    ]

    lines.append(row(MACRO_IV_LABEL, [fmt_coef(m) for m in results]))
    lines.append(row("", [fmt_se(m) for m in results]))

    lines.append(r"\midrule")

    lines.append(row("BASE Controls", ["Yes"] * 8))
    pres_cells = [
        ("Yes" if PRES_CONTROL_MAP.get(MODEL_SPECS[c - 1]["dv"]) else "")
        for c in cols
    ]
    lines.append(row("Pres Control", pres_cells))
    lines.append(row("Lagged DV", ["Yes"] * 8))

    ind_cells = ["Yes" if MODEL_SPECS[c - 1]["fe"] == "industry" else "" for c in cols]
    firm_cells = ["Yes" if MODEL_SPECS[c - 1]["fe"] == "firm" else "" for c in cols]
    lines.append(row("Industry FE", ind_cells))
    lines.append(row("Firm FE", firm_cells))
    lines.append(row("Calendar Year FE", ["Yes"] * 8))

    lines.append(r"\midrule")
    lines.append(row("Observations", [fmt_int(m) for m in results]))
    lines.append(row(r"$R^{2}$", [fmt_r2(m, "r2") for m in results]))
    lines.append(row(r"Adj.~$R^{2}$", [fmt_r2(m, "adj_r2") for m in results]))

    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\begin{minipage}{\linewidth}",
            r"\vspace{2pt}\scriptsize",
            r"\textit{Notes:} ",
            r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ "
            rf"(one-tailed test: {SUITE_ID} predicts $\beta > 0$). ",
            r"Standard errors (in parentheses) are two-way clustered by firm "
            r"and calendar year-quarter. ",
            r"Dependent variables are contemporaneous call-level uncertainty "
            r"language measures. ",
            rf"Key regressor is $\log({MACRO_IV_RAW})$, the log of the "
            r"Baker, Bloom \& Davis (2016) news-based US Economic Policy "
            r"Uncertainty index, matched to each call by its calendar month. ",
            r"Models include Industry (FF12) or Firm fixed effects AND "
            r"Calendar Year fixed effects. ",
            r"Year-quarter fixed effects are NOT included as they would "
            r"absorb the aggregate macro regressor; Calendar Year FE only "
            r"absorbs year-to-year variation, preserving within-year "
            r"cross-firm variation from monthly macro matching. ",
            r"Main sample (excludes financial and utility firms). ",
            r"Controls include the presentation-context sibling of Q\&A DVs, "
            r"the lagged dependent variable, analyst Q\&A uncertainty, negative "
            r"sentiment, log assets, Tobin's Q, ROA, cash holdings, dividend "
            r"dummy, firm maturity, and earnings volatility. ",
            r"Firms with fewer than 5 calls are excluded. ",
            r"Unit of observation: individual earnings call.",
            r"\end{minipage}",
            r"\end{table}",
        ]
    )

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Saved: {tex_path.name}")


def _write_suite_spec_json(
    all_models: List[Tuple[int, Any, Dict[str, Any]]],
    col_controls: Dict[int, List[str]],
    out_dir: Path,
) -> None:
    """Emit canonical suite_spec.json for a macro-IV suite (H24/H24b/H25).

    Macro suites have:
    - Two-way clustering (firm, cal_yr_qtr) — driven by CLUSTERING
    - Calendar Year FE only (NOT year-quarter; would absorb the IV)
    - Single IV (MACRO_IV) per table, 8 cols = 4 DVs x 2 FE types
    - Per-col control_vars via PRES_CONTROL_MAP (Ans DVs get pres sibling;
      Pres DVs get no pres sibling)
    - Two-row header: FE groups on top, pipeline DV names on bottom
    """
    col_metadata: List[Dict[str, Any]] = []
    coefs_per_col: List[Dict[str, Dict[str, Any]]] = []

    models_by_col = {col: (model, meta) for col, model, meta in all_models}

    for spec in MODEL_SPECS:
        col_num = spec["col"]
        if col_num not in models_by_col:
            raise RuntimeError(
                f"{SUITE_ID} spec build: missing result for col {col_num}"
            )
        model, meta = models_by_col[col_num]
        controls = col_controls.get(col_num, [])

        fe_type = spec["fe"]
        fe_entity = "industry" if fe_type == "industry" else "firm"

        try:
            dv_mean: Optional[float] = float(
                model.model.dependent.dataframe.mean().iloc[0]
            )
        except Exception:
            dv_mean = None

        col_metadata.append(
            {
                "col": col_num,
                "dv": spec["dv"],
                "fe_entity": fe_entity,
                "fe_time": "calendar_year",  # driven by other_effects=cal_yr
                "control_vars": list(controls),
                "n_obs": int(meta["n_obs"]),
                "n_firms": int(meta.get("n_firms", 0)) or None,
                "r2": float(meta["r2"]),
                "adj_r2": float(meta.get("adj_r2", float("nan"))),
                "dv_mean": dv_mean,
                "cluster_fallback": False,
            }
        )

        coefs_per_col.append(
            extract_coefs_panelols(
                model=model,
                key_ivs=[MACRO_IV],
                all_vars=[MACRO_IV] + controls,
                hyp_dir=HYP_DIR,
            )
        )

    # Base controls for the spec: BASE_CONTROLS + both Pres siblings +
    # Lagged_DV. The renderer emits a row for each; per-col masking via
    # col.control_vars hides the cell in columns where the var isn't used.
    base_plus_dynamic = list(BASE_CONTROLS) + ["UncPreMgr", "UncPreCEO", "UncPreNoCEO", "Lagged_DV"]

    # Two-row header: top = FE groups, bottom = DV pipeline names.
    header_rows = [
        [
            {"label": r"Industry + Cal. Year FE", "span": 6},
            {"label": r"Firm + Cal. Year FE", "span": 6},
        ],
        [
            {"label": spec["dv"], "span": 1} for spec in MODEL_SPECS
        ],
    ]

    paths = write_suite_spec(
        output_dir=out_dir,
        runner_id=SUITE_DIR,
        sub_tables=[
            {
                "suite_id": SUITE_ID,
                "dir_name": SUITE_DIR,
                "title": SUITE_TITLE,
                "caption": SUITE_CAPTION,
                "label": SUITE_LABEL,
                "col_range": [s["col"] for s in MODEL_SPECS],
                "header_rows": header_rows,
                "suite_type": "moderation",
            }
        ],
        coefs_per_col=coefs_per_col,
        col_metadata=col_metadata,
        sample_label=SAMPLE_LABEL,
        clustering=CLUSTERING,
        tail=TAIL,
        ivs=[{"name": MACRO_IV, "label": MACRO_IV_LABEL, "tail": "one_pos"}],
        controls={
            "base": base_plus_dynamic,
            "extended_only": list(EXTENDED_ONLY_CONTROLS),
            "labels": {
                "UncPreMgr": "UncPreMgr",
                "UncPreCEO": "UncPreCEO",
                "UncPreNoCEO": "UncPreNoCEO",
                "Lagged_DV": r"Lagged\_DV",
            },
        },
        model_family="PanelOLS",
    )
    for path in paths:
        print(f"  Saved: {path.name}")


# ==============================================================================
# Main
# ==============================================================================


def main(panel_path: str | None = None) -> int:
    t0 = datetime.now()
    timestamp = t0.strftime("%Y-%m-%d_%H%M%S")
    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / SUITE_DIR / timestamp

    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name=SUITE_NAME,
        timestamp=timestamp,
    )

    print("=" * 80)
    print(f"STAGE 4: {SUITE_ID} - {MACRO_IV} -> Call Language Uncertainty")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Log dir:   {log_dir}")
    print(f"Macro IV:  {MACRO_IV}")

    if not panel_path:
        try:
            panel_dir = get_latest_output_dir(
                root / "outputs" / "variables" / PANEL_INPUT_DIR,
                required_file=PANEL_INPUT_FILE,
            )
            panel_file = panel_dir / PANEL_INPUT_FILE
        except Exception as e:
            print(f"ERROR: Could not find Stage 3 panel: {e}")
            return 1
    else:
        panel_file = Path(panel_path)

    print("\n" + "=" * 60)
    print("Loading panel")
    print("=" * 60)

    panel = pd.read_parquet(panel_file, columns=_required_columns())
    print(f"  Loaded: {panel_file}")
    print(f"  Rows: {len(panel):,}")
    print(f"  Columns: {len(panel.columns)}")

    if "sample" not in panel.columns or panel["sample"].isna().all():
        panel["sample"] = assign_industry_sample(panel["ff12_code"])

    out_dir.mkdir(parents=True, exist_ok=True)

    # Summary stats
    print("\n" + "=" * 60)
    print("Generating summary statistics")
    print("=" * 60)
    summary_vars = [v for v in SUMMARY_STATS_VARS if v["col"] in panel.columns]
    make_summary_stats_table(
        df=panel,
        variables=summary_vars,
        sample_names=["Main", "Finance", "Utility"],
        sample_col="sample",
        output_csv=out_dir / "summary_stats.csv",
        output_tex=out_dir / "summary_stats.tex",
        caption=f"Summary Statistics - {SUITE_ID} US EPU",
        label=f"tab:summary_stats_{SUITE_DIR}",
    )
    print("  Saved: summary_stats.csv / .tex")

    all_results: List[Dict[str, Any]] = []
    all_models: List[Tuple[int, Any, Dict[str, Any]]] = []
    # Track per-col control lists so the spec builder can emit per-col
    # control_vars (PRES_CONTROL_MAP asymmetry) without recomputing them.
    col_controls: Dict[int, List[str]] = {}

    # Main sample only for headline 8-col table
    panel_main = panel[panel["sample"] == "Main"].copy()
    print(f"\n  Main sample: {len(panel_main):,} rows")

    for spec in MODEL_SPECS:
        dv_var = spec["dv"]
        print(f"\n--- Spec col {spec['col']}: DV={dv_var} FE={spec['fe']} ---")

        df_prep, controls = prepare_regression_data(panel_main, dv_var)

        # Min calls filter
        df_prep["gvkey_count"] = df_prep.groupby("gvkey")["file_name"].transform("count")
        df_sample = df_prep[df_prep["gvkey_count"] >= CONFIG["min_calls"]].copy()
        print(
            f"  After filters: {len(df_sample):,} calls, "
            f"{df_sample['gvkey'].nunique():,} firms"
        )

        if len(df_sample) < 100:
            print("  Skipping: insufficient data")
            continue

        model, meta = run_regression(df_sample, spec, controls)

        if model is not None:
            all_results.append(meta)
            all_models.append((spec["col"], model, meta))
            col_controls[spec["col"]] = list(controls)
            fname = f"regression_results_col{spec['col']}.txt"
            with open(out_dir / fname, "w", encoding="utf-8") as f:
                f.write(f"Suite: {SUITE_ID}\n")
                f.write(f"Col: ({spec['col']})\n")
                f.write(f"DV: {dv_var} ({DV_LABELS.get(dv_var, '')})\n")
                f.write(f"Macro IV: {MACRO_IV}\n")
                f.write(f"FE: {spec['fe']}\n")
                f.write(f"Pres control: {meta.get('pres_control', '')}\n")
                f.write(f"Adj_R2: {meta['adj_r2']:.10f}\n")
                f.write("=" * 60 + "\n\n")
                f.write(str(model.summary))

    _save_latex_table(all_results, out_dir)
    _write_suite_spec_json(all_models, col_controls, out_dir)
    pd.DataFrame(all_results).to_csv(
        out_dir / "model_diagnostics.csv", index=False, float_format="%.10f"
    )
    print("  Saved: model_diagnostics.csv")

    # Sample attrition
    if all_results:
        main_result = all_results[0]
        attrition_stages = [
            ("Master manifest", len(panel)),
            ("Main sample filter", int((panel["sample"] == "Main").sum())),
            (
                "After complete-case + min-calls filter",
                main_result.get("n_obs", 0),
            ),
        ]
        generate_attrition_table(
            attrition_stages, out_dir, f"{SUITE_ID} US EPU"
        )
        print("  Saved: sample_attrition.csv / .tex")

    generate_manifest(
        output_dir=out_dir,
        stage="stage4",
        timestamp=timestamp,
        input_paths={"panel": panel_file},
        output_files={
            "diagnostics": out_dir / "model_diagnostics.csv",
            "table": out_dir / f"{SUITE_DIR}_table.tex",
        },
        panel_path=panel_file,
    )
    print("  Saved: run_manifest.json")

    print("\n" + "=" * 80)
    print(f"{SUITE_ID} COMPLETE in {(datetime.now() - t0).total_seconds():.1f}s")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    args = parse_arguments()
    sys.exit(main(panel_path=args.panel_path))
