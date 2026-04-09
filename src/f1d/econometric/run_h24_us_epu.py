#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H24 US Economic Policy Uncertainty -> Call Language Uncertainty
================================================================================
ID: econometric/test_h24_us_epu
Description: Reverse-direction suite - aggregate US Economic Policy Uncertainty
             (Baker, Bloom & Davis 2016, QJE) predicts call-level language
             uncertainty. Analogous structure to H11 (PRisk -> Uncertainty).

Model Specification:
    Uncertainty_it ~ log(US_EPU)_mt + PresControl_it + Lagged_DV_i,t-1 +
                     UncQue_it + NegCall_it + lnAssets_it + TobinsQ_it +
                     ROA_it + CashRatio_it + DivDummy_it + FirmMat_it +
                     EarnVol_it + EntityEffects

Dependent variables (8 total, contemporaneous + next-quarter lead):
    Cols 1-4: UncAnsMgr, UncPreMgr, UncAnsCEO, UncPreCEO      (contemporaneous)
    Cols 5-8: UncAnsMgr_lead1, UncPreMgr_lead1,
              UncAnsCEO_lead1, UncPreCEO_lead1                (next quarter)

CRITICAL DEVIATIONS FROM THE H11 TEMPLATE:
    1. Panel index is (gvkey, cal_yr_qtr), NOT (gvkey, year).
    2. Formula ends with `+ EntityEffects` only. NO TimeEffects - it would
       absorb the monthly macro IV entirely.
    3. Standard errors are TWO-WAY clustered (firm, cal_yr_qtr) via
       cluster_entity=True, cluster_time=True.

Hypothesis (one-tailed, positive):
    H24: beta(log(US EPU)) > 0
         Higher aggregate US economic policy uncertainty -> higher call-level
         language uncertainty.

Industry Samples:
    - Main: FF12 codes 1-7, 9-10, 12 (non-financial, non-utility)
    - Finance: FF12 code 11 (reported, not in headline table)
    - Utility: FF12 code 8  (reported, not in headline table)

Minimum Calls Filter:
    Firms must have >= 5 calls to be included in regression (standard).

Inputs:
    - outputs/variables/h24_h24b_h25_macro/latest/h24_h24b_h25_macro_panel.parquet

Outputs:
    - outputs/econometric/h24_us_epu/{timestamp}/regression_results_{sample}_{dv}.txt
    - outputs/econometric/h24_us_epu/{timestamp}/h24_us_epu_table.tex
    - outputs/econometric/h24_us_epu/{timestamp}/model_diagnostics.csv
    - outputs/econometric/h24_us_epu/{timestamp}/summary_stats.csv / .tex
    - outputs/econometric/h24_us_epu/{timestamp}/sample_attrition.csv / .tex
    - outputs/econometric/h24_us_epu/{timestamp}/run_manifest.json

Deterministic: true
Dependencies:
    - Requires: Stage 3 (build_h24_h24b_h25_macro_uncertainty_panel)
    - Uses: linearmodels, f1d.shared.latex_tables_accounting

Reference: Baker, Bloom & Davis (2016) "Measuring Economic Policy Uncertainty"
           Quarterly Journal of Economics 131(4): 1593-1636.

Author: Thesis Author
Date: 2026-04-09
================================================================================
"""

from __future__ import annotations

import argparse
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

from f1d.shared.latex_tables_accounting import make_summary_stats_table
from f1d.shared.logging.config import setup_run_logging
from f1d.shared.outputs import generate_manifest, generate_attrition_table
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
SUITE_CAPTION = (
    "H24: US Economic Policy Uncertainty and Call Language Uncertainty"
)
SUITE_LABEL = "tab:h24_us_epu"

PANEL_INPUT_DIR = "h24_h24b_h25_macro"
PANEL_INPUT_FILE = "h24_h24b_h25_macro_panel.parquet"

CONFIG = {
    "min_calls": 5,
    "samples": ["Main", "Finance", "Utility"],
}

# Base 4 uncertainty DVs (contemporaneous)
BASE_DVS = ["UncAnsMgr", "UncPreMgr", "UncAnsCEO", "UncPreCEO"]
LEAD_DVS = [f"{d}_lead1" for d in BASE_DVS]
# Full DV list - 4 contemporaneous + 4 next-quarter leads = 8
ALL_DVS = BASE_DVS + LEAD_DVS

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

# Presentation-control map for Q&A dependents - when DV is a Q&A measure, the
# matching Presentation measure is added as a control. Matches H11 convention.
# For lead DVs, the lead's pres control is the lead's corresponding pres measure.
PRES_CONTROL_MAP = {
    "UncAnsMgr": "UncPreMgr",
    "UncAnsCEO": "UncPreCEO",
    "UncPreMgr": None,
    "UncPreCEO": None,
    "UncAnsMgr_lead1": "UncPreMgr_lead1",
    "UncAnsCEO_lead1": "UncPreCEO_lead1",
    "UncPreMgr_lead1": None,
    "UncPreCEO_lead1": None,
}


def _lag_column_for_dv(dv: str) -> str:
    """Return the Lagged_DV column name for a given DV.

    Contemporaneous DV: `Y_t ~ ... + Y_{t-1}` -> use `{base}_lag`
    Lead1 DV:           `Y_{t+1} ~ ... + Y_t` -> use `{base}` (contemp base)
    """
    if dv.endswith("_lead1"):
        return dv[: -len("_lead1")]
    return f"{dv}_lag"


# ==============================================================================
# Summary Statistics
# ==============================================================================

SUMMARY_STATS_VARS = [
    # DVs (contemporaneous)
    {"col": "UncAnsMgr", "label": "Mgr QA Uncertainty"},
    {"col": "UncPreMgr", "label": "Mgr Pres Uncertainty"},
    {"col": "UncAnsCEO", "label": "CEO QA Uncertainty"},
    {"col": "UncPreCEO", "label": "CEO Pres Uncertainty"},
    # DVs (next quarter)
    {"col": "UncAnsMgr_lead1", "label": r"Mgr QA Uncertainty$_{t+1}$"},
    {"col": "UncPreMgr_lead1", "label": r"Mgr Pres Uncertainty$_{t+1}$"},
    {"col": "UncAnsCEO_lead1", "label": r"CEO QA Uncertainty$_{t+1}$"},
    {"col": "UncPreCEO_lead1", "label": r"CEO Pres Uncertainty$_{t+1}$"},
    # Macro IV (raw and log)
    {"col": MACRO_IV_RAW, "label": "US EPU (raw)"},
    {"col": MACRO_IV, "label": "log(US EPU)"},
    # Controls
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
    ]
    if "sample" not in cols:
        cols.append("sample")
    # Macro IVs (raw + all log variants - we only use MACRO_IV but load raw
    # for summary stats and the other two log variants for optional comparison)
    cols += [
        "GPR",
        "US_EPU",
        "GEPU_current",
        "GPR_log",
        "US_EPU_log",
        "GEPU_log",
    ]
    # DVs and their leads/lags
    cols += BASE_DVS
    cols += LEAD_DVS
    cols += [f"{d}_lag" for d in BASE_DVS]
    # Base controls
    cols += BASE_CONTROLS
    # Dedupe while preserving order
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
    pres_control = PRES_CONTROL_MAP.get(dv_var)
    lagged_col = _lag_column_for_dv(dv_var)

    controls = list(BASE_CONTROLS)
    if pres_control:
        controls.append(pres_control)
    controls.append("Lagged_DV")

    # Stage a Lagged_DV column on the panel (dynamically per DV)
    df = panel.copy()
    df["Lagged_DV"] = df[lagged_col]

    required = (
        [dv_var, MACRO_IV]
        + [c for c in controls if c != "Lagged_DV"]
        + ["Lagged_DV", "gvkey", "cal_yr_qtr"]
    )
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in panel: {missing}")

    df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=required).copy()
    return df, controls


# ==============================================================================
# Regression
# ==============================================================================


def run_regression(
    df_sample: pd.DataFrame,
    dv_var: str,
    sample_name: str,
    controls: List[str],
) -> Tuple[Any, Dict[str, Any]]:
    """Run PanelOLS with Firm FE only (NO TimeEffects) and two-way clustering.

    Panel index: (gvkey, cal_yr_qtr). Time level = cal_yr_qtr, so
    cluster_time=True yields quarter-level clustering.
    """
    exog_str = " + ".join([MACRO_IV] + controls)
    formula = f"{dv_var} ~ 1 + {exog_str} + EntityEffects"
    #                                          ^^^^^^^^^^^^^
    # CRITICAL: no TimeEffects. Macro IV is constant across firms within any
    # calendar month; including time FE at any granularity would absorb it.

    print(f"  Formula: {dv_var} ~ {MACRO_IV} + {' + '.join(controls)} + EntityEffects")
    print(
        f"  N calls: {len(df_sample):,}  |  N firms: {df_sample['gvkey'].nunique():,}"
    )
    print("  Estimating with TWO-WAY clustered SEs (firm, cal_yr_qtr)...")

    t0 = datetime.now()

    df_panel = df_sample.set_index(["gvkey", "cal_yr_qtr"])

    try:
        model_obj = PanelOLS.from_formula(
            formula, data=df_panel, drop_absorbed=True
        )
        model = model_obj.fit(
            cov_type="clustered",
            cluster_entity=True,
            cluster_time=True,
            # ^ Upgrade vs H11's firm-only cluster. Macro IV is correlated
            #   across firms within time, so time clustering is required.
        )
    except Exception as e:
        print(f"  ERROR: Regression failed: {e}", file=sys.stderr)
        return None, {}

    duration = (datetime.now() - t0).total_seconds()
    print(f"  [OK] Complete in {duration:.1f}s")

    adj_r2 = 1 - (1 - model.rsquared) * (model.nobs - 1) / model.df_resid
    print(f"  R-squared: {model.rsquared:.4f}  Adj R-squared: {adj_r2:.4f}")
    print(f"  N obs:     {int(model.nobs):,}")

    beta = float(model.params.get(MACRO_IV, np.nan))
    p_two = float(model.pvalues.get(MACRO_IV, np.nan))
    se = float(model.std_errors.get(MACRO_IV, np.nan))
    t_stat = float(model.tstats.get(MACRO_IV, np.nan))

    # H24 is one-tailed positive: beta > 0
    if not np.isnan(p_two) and not np.isnan(beta):
        p_one = p_two / 2 if beta > 0 else 1 - p_two / 2
    else:
        p_one = np.nan

    sig = not np.isnan(p_one) and p_one < 0.05 and beta > 0
    sig_text = "YES" if sig else "no"
    print(
        f"  beta({MACRO_IV}): {beta:.4f}  SE={se:.4f}  p(one-tail)={p_one:.4f}  "
        f"{SUITE_ID} significant={sig_text}"
    )

    meta = {
        "suite": SUITE_ID,
        "dv": dv_var,
        "sample": sample_name,
        "macro_iv": MACRO_IV,
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
# LaTeX Table (8 columns - contemporaneous + next-quarter lead)
# ==============================================================================


def _save_latex_table(all_results: List[Dict[str, Any]], out_dir: Path) -> None:
    """Write 8-column LaTeX table grouped as [Contemporaneous | Next Quarter (t+1)].

    Columns 1-4: UncAnsMgr, UncPreMgr, UncAnsCEO, UncPreCEO           (Main sample, t)
    Columns 5-8: UncAnsMgr_lead1, UncPreMgr_lead1, UncAnsCEO_lead1, UncPreCEO_lead1
    """
    tex_path = out_dir / f"{SUITE_DIR}_table.tex"

    # Lookup by (sample, dv) -> meta
    def _get(dv: str) -> Dict[str, Any]:
        for r in all_results:
            if r.get("sample") == "Main" and r.get("dv") == dv:
                return r
        return {}

    ordered_dvs = BASE_DVS + LEAD_DVS  # 8
    results = [_get(d) for d in ordered_dvs]

    def fmt_coef(meta: Dict[str, Any]) -> str:
        if not meta:
            return ""
        beta = meta.get("beta", np.nan)
        p_one = meta.get("beta_p_one", np.nan)
        if np.isnan(beta):
            return ""
        if np.isnan(p_one):
            return f"{beta:.4f}"
        if p_one < 0.01:
            stars = r"^{***}"
        elif p_one < 0.05:
            stars = r"^{**}"
        elif p_one < 0.10:
            stars = r"^{*}"
        else:
            stars = ""
        return f"{beta:.4f}{stars}"

    def fmt_se(meta: Dict[str, Any]) -> str:
        if not meta:
            return ""
        se = meta.get("beta_se", np.nan)
        return "" if np.isnan(se) else f"({se:.4f})"

    def fmt_int(meta: Dict[str, Any]) -> str:
        n = meta.get("n_obs", 0) if meta else 0
        return f"{n:,}" if n else ""

    def fmt_r2(meta: Dict[str, Any], key: str) -> str:
        if not meta:
            return ""
        v = meta.get(key, np.nan)
        if np.isnan(v):
            return ""
        if abs(v) < 0.001:
            return f"{v:.2e}"
        return f"{v:.3f}"

    def row(label: str, cells: List[str]) -> str:
        return f"{label} & " + " & ".join(cells) + r" \\"

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        rf"\caption{{{SUITE_CAPTION}}}",
        rf"\label{{{SUITE_LABEL}}}",
        r"\small",
        r"\begin{tabular}{l" + "c" * 8 + r"}",
        r"\toprule",
        r" & \multicolumn{4}{c}{Contemporaneous} & \multicolumn{4}{c}{Next Quarter (t+1)} \\",
        r"\cmidrule(lr){2-5} \cmidrule(lr){6-9}",
        r" & Mgr QA & Mgr Pres & CEO QA & CEO Pres & Mgr QA & Mgr Pres & CEO QA & CEO Pres \\",
        r" & (1) & (2) & (3) & (4) & (5) & (6) & (7) & (8) \\",
        r"\midrule",
    ]

    # Main IV row - coefficient + SE
    lines.append(row(MACRO_IV_LABEL, [fmt_coef(m) for m in results]))
    lines.append(row("", [fmt_se(m) for m in results]))

    lines.append(r"\midrule")

    # Controls / FE indicator rows
    lines.append(row("BASE Controls", ["Yes"] * 8))
    lines.append(row("Pres Control", ["Yes"] * 8))
    lines.append(row("Lagged DV", ["Yes"] * 8))
    lines.append(row("Firm FE", ["Yes"] * 8))
    lines.append(
        row("Calendar Year FE", ["No"] * 8)  # crystal clear: no time FE
    )
    lines.append(row("Year-Quarter FE", ["No"] * 8))

    lines.append(r"\midrule")

    # N, R^2, Adj R^2
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
            r"Standard errors (in parentheses) are two-way clustered by firm and "
            r"calendar year-quarter. ",
            r"Dependent variables are call-level uncertainty language measures "
            r"(contemporaneous in columns 1--4; next calendar quarter's call in "
            r"columns 5--8). ",
            rf"Key regressor is $\log({MACRO_IV_RAW})$, the log of the "
            r"Baker, Bloom \& Davis (2016) news-based US Economic Policy "
            r"Uncertainty index, matched to each call by its calendar month. ",
            r"Models include firm fixed effects. ",
            r"No time fixed effects are included - they would absorb the "
            r"aggregate macro regressor. ",
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

    for dv in ALL_DVS:
        for sample in CONFIG["samples"]:
            print(f"\n--- {sample} / {dv} ---")

            df_prep, controls = prepare_regression_data(panel, dv)

            df_sample = df_prep[df_prep["sample"] == sample].copy()

            df_sample["gvkey_count"] = df_sample.groupby("gvkey")[
                "file_name"
            ].transform("count")
            df_filtered = df_sample[
                df_sample["gvkey_count"] >= CONFIG["min_calls"]
            ].copy()

            print(
                f"  After filters: {len(df_filtered):,} calls, "
                f"{df_filtered['gvkey'].nunique():,} firms"
            )

            if len(df_filtered) < 100:
                print("  Skipping: insufficient data")
                continue

            print(f"\n{'=' * 60}")
            print(f"Running regression: {sample} / {dv}")
            print(f"{'=' * 60}")

            model, meta = run_regression(df_filtered, dv, sample, controls)

            if model is not None:
                all_results.append(meta)
                with open(
                    out_dir / f"regression_results_{sample}_{dv}.txt",
                    "w",
                    encoding="utf-8",
                ) as f:
                    f.write(f"Suite: {SUITE_ID}\n")
                    f.write(f"DV: {dv}\n")
                    f.write(f"Macro IV: {MACRO_IV}\n")
                    f.write(f"Sample: {sample}\n")
                    f.write(f"Adj_R2: {meta['adj_r2']:.10f}\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(str(model.summary))

    _save_latex_table(all_results, out_dir)
    pd.DataFrame(all_results).to_csv(
        out_dir / "model_diagnostics.csv", index=False, float_format="%.10f"
    )
    print("  Saved: model_diagnostics.csv")

    # Sample attrition
    if all_results:
        main_result = next(
            (r for r in all_results if r.get("sample") == "Main"), all_results[0]
        )
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
