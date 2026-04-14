#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H23 Competition → Uncertainty Language Hypothesis
================================================================================
ID: econometric/run_h23_competition_uncertainty
Description: Does product-market competition predict managerial uncertainty
             language? Tests whether Hoberg-Phillips TNIC3 TotalSimilarity
             predicts speech uncertainty in earnings calls.

DV: UncAnsMgr, UncAnsCEO, UncPreMgr, UncPreCEO (firm-year averages).

8 Model Specifications:
    Cols 1-4:  Industry + Fiscal Year FE (one per DV)
    Cols 5-8:  Firm + Fiscal Year FE (one per DV)
    QA DVs (cols 1,2,5,6): add corresponding Pres uncertainty as control

Key IV: log(TotalSimilarity) — log-transformed TNIC3TSIMM.
    Higher TSIMM = more product-market competitors with similar products.

Hypothesis: Two-tailed (no prior on direction).
No Lagged_DV (H11 precedent — linguistic DV, not financial stock).

Estimator: PanelOLS with firm or industry FE + fiscal year FE.
Unit of observation: firm-fiscal-year.

Sample: Main only (FF12 != 8, 11).
SEs: Firm-clustered.
FE time: cal_yr (= fyearq_int, set in panel builder).

Inputs:
    - outputs/variables/h23_competition_uncertainty/latest/h23_competition_uncertainty_panel.parquet

Outputs:
    - outputs/econometric/h23_competition_uncertainty/{timestamp}/...

Reference: Hoberg, G. & Phillips, G. (2016). Text-Based Network Industries and
           Endogenous Product Differentiation. JPE, 124(5), 1423-1465.

Author: Thesis Author
Date: 2026-04-05
================================================================================
"""

from __future__ import annotations

import argparse
import sys
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


# ==============================================================================
# Configuration
# ==============================================================================

IV = "z_log_TotalSimilarity"

DVS = ["UncAnsMgr", "UncAnsCEO", "UncPreMgr", "UncPreCEO"]

# ------------------------------------------------------------------
# Suite metadata for suite_spec.json emission (single sub-table, 2-row header).
# HYP_DIR="positive" fixes Bug 3 from project_latex_audit_2026_04_13.md
# (legacy SUITES dict had key_tails=["two"] but the runner computes p_one
# with beta>0 halving — the legacy was ignoring the runner's directional
# hypothesis).
# ------------------------------------------------------------------
SUITE_ID = "H23"
SUITE_DIR_NAME = "h23_competition_uncertainty"
SUITE_TITLE = "Product-Market Competition and Uncertainty Language"
SUITE_CAPTION = "H23: Product-Market Competition and Uncertainty Language"
SUITE_LABEL = "tab:h23_competition_uncertainty"
SAMPLE_LABEL = (
    "Main sample (excludes financial and utility firms). "
    "Unit of observation: firm-fiscal-year."
)
HYP_DIR = "positive"  # H23: higher competition -> higher uncertainty (one-tailed)
CLUSTERING = {"entity": True, "time": False}
TAIL = {"direction": HYP_DIR, "applies_to": "ivs_only"}
EXTENDED_ONLY_CONTROLS: List[str] = []  # H23 has no extended set

# Dynamic Pres control for QA DVs (from H11 pattern)
PRES_CONTROL_MAP = {
    "UncAnsMgr": "UncPreMgr",
    "UncAnsCEO": "UncPreCEO",
    "UncPreMgr": None,
    "UncPreCEO": None,
}

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

MIN_FIRM_YEARS = 5

MODEL_SPECS = [
    # Industry + Fiscal Year FE (cols 1-4)
    {"col": 1, "dv": "UncAnsMgr", "fe": "industry"},
    {"col": 2, "dv": "UncAnsCEO", "fe": "industry"},
    {"col": 3, "dv": "UncPreMgr", "fe": "industry"},
    {"col": 4, "dv": "UncPreCEO", "fe": "industry"},
    # Firm + Fiscal Year FE (cols 5-8)
    {"col": 5, "dv": "UncAnsMgr", "fe": "firm"},
    {"col": 6, "dv": "UncAnsCEO", "fe": "firm"},
    {"col": 7, "dv": "UncPreMgr", "fe": "firm"},
    {"col": 8, "dv": "UncPreCEO", "fe": "firm"},
]

DV_LABELS = {
    "UncAnsMgr": "Mgr QA Uncertainty",
    "UncAnsCEO": "CEO QA Uncertainty",
    "UncPreMgr": "Mgr Pres Uncertainty",
    "UncPreCEO": "CEO Pres Uncertainty",
}

SUMMARY_STATS_VARS = [
    {"col": "UncAnsMgr", "label": "Mgr QA Uncertainty"},
    {"col": "UncAnsCEO", "label": "CEO QA Uncertainty"},
    {"col": "UncPreMgr", "label": "Mgr Pres Uncertainty"},
    {"col": "UncPreCEO", "label": "CEO Pres Uncertainty"},
    {"col": "TotalSimilarity", "label": "TNIC3TSIMM (raw)"},
    {"col": "log_TotalSimilarity", "label": "$\\log(\\mathrm{TSIMM})$"},
    {"col": "z_log_TotalSimilarity", "label": "$z(\\log(\\mathrm{TSIMM}))$"},
    {"col": "UncQue", "label": "Analyst QA Uncertainty"},
    {"col": "NegCall", "label": "Negative Sentiment"},
    {"col": "lnAssets", "label": "Firm Size (log AT)"},
    {"col": "TobinsQ", "label": "Tobin's Q"},
    {"col": "ROA", "label": "ROA"},
    {"col": "CashRatio", "label": "Cash Holdings"},
    {"col": "DivDummy", "label": "Dividend Payer"},
    {"col": "FirmMat", "label": "Firm Maturity"},
    {"col": "EarnVol", "label": "Earnings Volatility"},
    {"col": "n_calls_in_year", "label": "Calls per Firm-Year"},
]


# ==============================================================================
# CLI
# ==============================================================================


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 4: H23 Competition → Uncertainty (firm-year)",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--panel-path", type=str, default=None)
    return parser.parse_args()


# ==============================================================================
# Data Loading
# ==============================================================================


def load_panel(root_path: Path, panel_path: Optional[str] = None) -> Tuple[pd.DataFrame, Path]:
    """Load firm-year H23 panel."""
    print("\n" + "=" * 60)
    print("Loading H23 panel")
    print("=" * 60)

    if panel_path:
        panel_file = Path(panel_path)
    else:
        panel_dir = get_latest_output_dir(
            root_path / "outputs" / "variables" / "h23_competition_uncertainty",
            required_file="h23_competition_uncertainty_panel.parquet",
        )
        panel_file = panel_dir / "h23_competition_uncertainty_panel.parquet"

    if not panel_file.exists():
        raise FileNotFoundError(f"Panel file not found: {panel_file}")

    panel = pd.read_parquet(panel_file)
    print(f"  Loaded: {panel_file}")
    print(f"  Rows: {len(panel):,}, Columns: {len(panel.columns)}")
    print(f"  Unique firms: {panel['gvkey'].nunique():,}")
    print(f"  Fiscal year range: {panel['fyearq_int'].min()}-{panel['fyearq_int'].max()}")

    # Verify cal_yr exists (calendar year of latest call, NOT fyearq_int)
    if "cal_yr" not in panel.columns:
        raise ValueError("cal_yr column missing from panel. Rebuild panel.")
    n_cal_yr = panel["cal_yr"].notna().sum()
    print(f"  cal_yr range: {panel['cal_yr'].min():.0f}-{panel['cal_yr'].max():.0f} "
          f"({n_cal_yr:,}/{len(panel):,} non-null)")

    return panel, panel_file


def filter_main_sample(panel: pd.DataFrame) -> pd.DataFrame:
    """Filter to Main sample only."""
    before = len(panel)
    main = panel[~panel["ff12_code"].isin([8, 11])].copy()
    print(f"  Main sample: {len(main):,} / {before:,} "
          f"(dropped {before - len(main):,} Finance/Utility)")
    return main


def prepare_regression_data(
    panel: pd.DataFrame, spec: Dict[str, Any],
) -> pd.DataFrame:
    """Prepare panel for a specific model specification."""
    dv = spec["dv"]

    # Build controls: base + dynamic Pres control for QA DVs
    controls = list(BASE_CONTROLS)
    pres_ctrl = PRES_CONTROL_MAP.get(dv)
    if pres_ctrl:
        controls.append(pres_ctrl)

    required = [dv, IV] + controls + ["gvkey", "cal_yr", "ff12_code"]

    missing = [c for c in required if c not in panel.columns]
    if missing:
        raise ValueError(f"Required columns missing: {missing}")

    df = panel.copy()
    df = df.replace([np.inf, -np.inf], np.nan)

    # Drop NaN in DV
    before = len(df)
    df = df[df[dv].notna()].copy()
    print(f"  After DV ({dv}) filter: {len(df):,} / {before:,}")

    # Complete cases
    complete_mask = df[required].notna().all(axis=1)
    df = df[complete_mask].copy()
    print(f"  After complete cases: {len(df):,}")

    # Min firm-years per firm
    firm_counts = df["gvkey"].value_counts()
    valid_firms = set(firm_counts[firm_counts >= MIN_FIRM_YEARS].index)
    df = df[df["gvkey"].isin(valid_firms)].copy()
    print(f"  After >={MIN_FIRM_YEARS} firm-years/firm: "
          f"{len(df):,} obs, {df['gvkey'].nunique():,} firms")

    return df


# ==============================================================================
# Regression
# ==============================================================================


def run_regression(
    df_prepared: pd.DataFrame, spec: Dict[str, Any],
) -> Tuple[Any, Dict[str, Any]]:
    """Run PanelOLS with FE and firm-clustered SEs."""
    col_num = spec["col"]
    dv = spec["dv"]
    fe_type = spec["fe"]

    # Build exog: IV + controls (with dynamic Pres if QA DV)
    controls = list(BASE_CONTROLS)
    pres_ctrl = PRES_CONTROL_MAP.get(dv)
    if pres_ctrl:
        controls.append(pres_ctrl)
    exog = [IV] + controls

    time_col = "cal_yr"
    fe_label = f"{'Industry(FF12)' if fe_type == 'industry' else 'Firm'} + CalYear"

    print(f"\n{'=' * 60}")
    print(f"Col ({col_num}) | DV={DV_LABELS.get(dv, dv)} | FE={fe_label}")
    print(f"{'=' * 60}")

    if len(df_prepared) < 100:
        print(f"  Too few obs ({len(df_prepared)}), skipping")
        return None, {}

    n_firms = df_prepared["gvkey"].nunique()
    print(f"  N={len(df_prepared):,}, firms={n_firms:,}")
    if pres_ctrl:
        print(f"  Dynamic control: + {pres_ctrl}")
    t0 = datetime.now()

    df_panel = df_prepared.set_index(["gvkey", time_col])

    try:
        if fe_type == "industry":
            model_obj = PanelOLS(
                dependent=df_panel[dv],
                exog=df_panel[exog],
                entity_effects=False,
                time_effects=True,
                other_effects=df_panel["ff12_code"],
                drop_absorbed=True,
                check_rank=False,
            )
            model = model_obj.fit(cov_type="clustered", cluster_entity=True)
        else:
            exog_str = " + ".join(exog)
            formula = f"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"
            model_obj = PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)
            model = model_obj.fit(cov_type="clustered", cluster_entity=True)
    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        return None, {}

    elapsed = (datetime.now() - t0).total_seconds()
    adj_r2 = 1 - (1 - model.rsquared) * (model.nobs - 1) / model.df_resid

    # Extract IV coefficient — one-tailed (H23: β>0, higher competition → more uncertainty)
    beta_iv = float(model.params.get(IV, np.nan))
    se_iv = float(model.std_errors.get(IV, np.nan))
    p_two_iv = float(model.pvalues.get(IV, np.nan))

    # One-tailed β>0: halve p if β>0 (supports H23), else 1 - p/2
    if not np.isnan(p_two_iv) and not np.isnan(beta_iv):
        p_one_iv = p_two_iv / 2 if beta_iv > 0 else 1 - p_two_iv / 2
    else:
        p_one_iv = np.nan

    # DV mean in regression sample
    dv_mean = float(df_prepared[dv].mean())

    print(f"  R-squared: {model.rsquared:.4f}  Adj R-squared: {adj_r2:.4f}  ({elapsed:.1f}s)")
    print(f"  {IV}: b={beta_iv:.6f} se={se_iv:.6f} p1={p_one_iv:.4f} {_sig_stars(p_one_iv)}")
    print(f"  DV mean: {dv_mean:.4f}")

    meta: Dict[str, Any] = {
        "col": col_num,
        "dv": dv,
        "fe": fe_type,
        "n_obs": int(model.nobs),
        "n_firms": n_firms,
        "r2": float(model.rsquared),
        "adj_r2": adj_r2,
        "dv_mean": dv_mean,
        "beta_iv": beta_iv,
        "se_iv": se_iv,
        "p_two_iv": p_two_iv,
        "p_one_iv": p_one_iv,
        "pres_control": pres_ctrl or "",
    }

    # Also extract all control coefficients for the output file
    for var in exog:
        meta[f"{var}_beta"] = float(model.params.get(var, np.nan))
        meta[f"{var}_se"] = float(model.std_errors.get(var, np.nan))
        meta[f"{var}_p_two"] = float(model.pvalues.get(var, np.nan))

    return model, meta


def _sig_stars(p: float) -> str:
    """Significance stars for one-tailed p-value."""
    if np.isnan(p):
        return ""
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return ""


# ==============================================================================
# Output
# ==============================================================================


def _save_latex_table(all_results: List[Dict[str, Any]], out_dir: Path) -> None:
    """Write 8-column LaTeX table."""
    results_by_col = {}
    for r in all_results:
        meta = r.get("meta", {})
        if meta:
            results_by_col[meta["col"]] = meta

    n_cols = 8

    def fmt_coef(val, stars):
        return f"{val:.4f}{stars}" if not np.isnan(val) else ""

    def fmt_se(val):
        return f"({val:.4f})" if not np.isnan(val) else ""

    def fmt_int(val):
        return f"{val:,}"

    def fmt_r2(val):
        if np.isnan(val):
            return ""
        return f"{val:.2e}" if abs(val) < 0.001 else f"{val:.3f}"

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{H23: Product-Market Competition and Uncertainty Language}",
        r"\label{tab:h23_competition_uncertainty}",
        r"\scriptsize",
        r"\begin{tabular}{l" + "c" * n_cols + "}",
        r"\toprule",
    ]

    # Column numbers
    col_nums = " & ".join(f"({i})" for i in range(1, n_cols + 1))
    lines.append(f" & {col_nums} " + r"\\")

    # DV headers
    dv_labels = " & ".join(
        DV_LABELS.get(results_by_col.get(c, {}).get("dv", ""), "?")
        for c in range(1, n_cols + 1)
    )
    lines.append(f" & {dv_labels} " + r"\\")

    # FE group headers
    lines.append(
        r" & \multicolumn{4}{c}{Industry + Year FE}"
        r" & \multicolumn{4}{c}{Firm + Year FE} \\"
    )
    lines.append(r"\cmidrule(lr){2-5} \cmidrule(lr){6-9}")
    lines.append(r"\midrule")

    # IV coefficient
    coef_cells = []
    for c in range(1, n_cols + 1):
        meta = results_by_col.get(c, {})
        beta = meta.get("beta_iv", np.nan)
        p = meta.get("p_one_iv", np.nan)
        coef_cells.append(fmt_coef(beta, _sig_stars(p)))
    lines.append(r"$z(\log(\mathrm{TSIMM}))$ & " + " & ".join(coef_cells) + r" \\")

    se_cells = []
    for c in range(1, n_cols + 1):
        meta = results_by_col.get(c, {})
        se_cells.append(fmt_se(meta.get("se_iv", np.nan)))
    lines.append(r" & " + " & ".join(se_cells) + r" \\")

    lines.append(r"\midrule")

    # Controls indicator
    lines.append(r"Controls & " + " & ".join(["Yes"] * n_cols) + r" \\")

    # Pres control indicator
    pres_cells = []
    for c in range(1, n_cols + 1):
        meta = results_by_col.get(c, {})
        pres_cells.append("Yes" if meta.get("pres_control") else "")
    lines.append(r"Pres Uncertainty ctrl & " + " & ".join(pres_cells) + r" \\")

    # FE indicators
    ind_fe_cells, firm_fe_cells, year_fe_cells = [], [], []
    for c in range(1, n_cols + 1):
        meta = results_by_col.get(c, {})
        fe = meta.get("fe", "")
        ind_fe_cells.append("Yes" if fe == "industry" else "")
        firm_fe_cells.append("Yes" if fe == "firm" else "")
        year_fe_cells.append("Yes")
    lines.append(r"Industry FE & " + " & ".join(ind_fe_cells) + r" \\")
    lines.append(r"Firm FE & " + " & ".join(firm_fe_cells) + r" \\")
    lines.append(r"Year FE & " + " & ".join(year_fe_cells) + r" \\")

    lines.append(r"\midrule")

    # N
    n_cells = []
    for c in range(1, n_cols + 1):
        meta = results_by_col.get(c, {})
        n_val = meta.get("n_obs", 0)
        n_cells.append(fmt_int(n_val) if n_val else "")
    lines.append(r"N & " + " & ".join(n_cells) + r" \\")

    # R-squared
    r2_cells = []
    for c in range(1, n_cols + 1):
        meta = results_by_col.get(c, {})
        r2_cells.append(fmt_r2(meta.get("r2", np.nan)))
    lines.append(r"$R^2$ & " + " & ".join(r2_cells) + r" \\")

    adj_r2_cells = []
    for c in range(1, n_cols + 1):
        meta = results_by_col.get(c, {})
        adj_r2_cells.append(fmt_r2(meta.get("adj_r2", np.nan)))
    lines.append(r"Adj.~$R^2$ & " + " & ".join(adj_r2_cells) + r" \\")

    # DV mean
    dv_mean_cells = []
    for c in range(1, n_cols + 1):
        meta = results_by_col.get(c, {})
        dv_m = meta.get("dv_mean", np.nan)
        dv_mean_cells.append(f"{dv_m:.4f}" if not np.isnan(dv_m) else "")
    lines.append(r"DV Mean & " + " & ".join(dv_mean_cells) + r" \\")

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\begin{minipage}{\linewidth}",
        r"\vspace{2pt}\scriptsize",
        r"\textit{Notes:} ",
        r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (one-tailed). ",
        r"Standard errors (in parentheses) clustered at firm level. ",
        r"DV is fiscal-year average of call-level LM uncertainty word percentage. ",
        r"IV is $z(\log(\mathrm{TSIMM}))$, standardized log of Hoberg \& Phillips (2016) TNIC3 total product similarity. ",
        r"Controls: analyst QA uncertainty, negative sentiment, firm size, Tobin's Q, ROA, ",
        r"cash holdings, dividend payer, firm maturity, earnings volatility. ",
        r"QA DVs additionally control for corresponding presentation uncertainty. ",
        r"Unit of observation: firm-fiscal-year. ",
        r"Main sample (excludes financial and utility firms).",
        r"\end{minipage}",
        r"\end{table}",
    ]

    tex_path = out_dir / "h23_competition_uncertainty_table.tex"
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Saved: {tex_path.name}")


def save_outputs(all_results: List[Dict[str, Any]], out_dir: Path) -> pd.DataFrame:
    """Save all outputs."""
    print("\n" + "=" * 60)
    print("Saving outputs")
    print("=" * 60)

    out_dir.mkdir(parents=True, exist_ok=True)

    for r in all_results:
        model = r.get("model")
        meta = r.get("meta", {})
        if model is None or not meta:
            continue
        col_num = meta["col"]
        fname = f"regression_results_col{col_num}.txt"
        with open(out_dir / fname, "w", encoding="utf-8") as f:
            f.write(f"H23 Competition → Uncertainty Regression\n")
            f.write(f"Col: ({col_num})\n")
            f.write(f"DV: {meta['dv']} ({DV_LABELS.get(meta['dv'], '')})\n")
            f.write(f"IV: {IV}\n")
            f.write(f"FE: {meta['fe']}\n")
            f.write(f"Pres control: {meta.get('pres_control', '')}\n")
            f.write(f"Adj_R2: {meta['adj_r2']:.10f}\n")
            f.write("=" * 60 + "\n\n")
            f.write(str(model.summary))
        print(f"  Saved: {fname}")

    diag_rows = [r["meta"] for r in all_results if r.get("meta")]
    diag_df = pd.DataFrame(diag_rows)
    diag_df.to_csv(out_dir / "model_diagnostics.csv", index=False, float_format="%.10f")
    print(f"  Saved: model_diagnostics.csv ({len(diag_df)} models)")

    _save_latex_table(all_results, out_dir)

    return diag_df


def _write_suite_spec_json(
    all_results: List[Dict[str, Any]],
    out_dir: Path,
) -> None:
    """Emit canonical suite_spec_H23.json from runner state.

    Layout: 8 cols = 4 DVs x 2 FE types. Two-row header groups
    Industry FE / Firm FE on top, pipeline DV names on bottom.
    Per-col control_vars via PRES_CONTROL_MAP (Ans DVs get matching
    Pres sibling as control; Pres DVs get no sibling).
    """
    col_metadata: List[Dict[str, Any]] = []
    coefs_per_col: List[Dict[str, Dict[str, Any]]] = []

    results_by_col = {
        r["meta"]["col"]: r for r in all_results if r.get("meta")
    }

    for spec in MODEL_SPECS:
        col_num = spec["col"]
        if col_num not in results_by_col:
            raise RuntimeError(
                f"H23 spec build: missing result for col {col_num}"
            )
        result = results_by_col[col_num]
        model = result["model"]
        meta = result["meta"]

        dv = spec["dv"]
        fe_type = spec["fe"]
        pres_ctrl = PRES_CONTROL_MAP.get(dv)
        control_vars = list(BASE_CONTROLS)
        if pres_ctrl:
            control_vars.append(pres_ctrl)

        try:
            dv_mean: Optional[float] = float(
                model.model.dependent.dataframe.mean().iloc[0]
            )
        except Exception:
            dv_mean = None

        col_metadata.append(
            {
                "col": col_num,
                "dv": dv,
                "fe_entity": "industry" if fe_type == "industry" else "firm",
                "fe_time": "calendar_year",
                "control_vars": control_vars,
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
                key_ivs=[IV],
                all_vars=[IV] + control_vars,
                hyp_dir=HYP_DIR,
            )
        )

    base_plus_siblings = list(BASE_CONTROLS) + ["UncPreMgr", "UncPreCEO"]

    header_rows = [
        [
            {"label": "Industry FE", "span": 4},
            {"label": "Firm FE", "span": 4},
        ],
        [{"label": spec["dv"], "span": 1} for spec in MODEL_SPECS],
    ]

    paths = write_suite_spec(
        output_dir=out_dir,
        runner_id=SUITE_DIR_NAME,
        sub_tables=[
            {
                "suite_id": SUITE_ID,
                "dir_name": SUITE_DIR_NAME,
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
        ivs=[
            {
                "name": IV,
                "label": r"$z(\log(\mathrm{TSIMM}))$",
                "tail": "one_pos",
            }
        ],
        controls={
            "base": base_plus_siblings,
            "extended_only": list(EXTENDED_ONLY_CONTROLS),
            "labels": {
                "UncPreMgr": "UncPreMgr",
                "UncPreCEO": "UncPreCEO",
            },
        },
        model_family="PanelOLS",
    )
    for path in paths:
        print(f"  Saved: {path.name}")


# ==============================================================================
# Main
# ==============================================================================


def main(panel_path: Optional[str] = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "h23_competition_uncertainty" / timestamp

    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H23_CompetitionUncertainty",
        timestamp=timestamp,
    )

    print("=" * 80)
    print("STAGE 4: H23 Competition → Uncertainty Language")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Design:    1 IV x 4 DVs x 2 FE types = 8 models")
    print(f"IV:        {IV}")
    print(f"FE time:   cal_yr (calendar year of latest call)")
    print(f"Unit:      firm-year (collapsed from calls)")

    panel, panel_file = load_panel(root, panel_path)

    full_n = len(panel)
    panel = filter_main_sample(panel)
    main_n = len(panel)

    # Diagnostics
    print(f"\n  Main sample: {main_n:,} firm-years, {panel['gvkey'].nunique():,} firms")
    print(f"  {IV} non-null: {panel[IV].notna().sum():,}")
    for dv in DVS:
        n_valid = panel[dv].notna().sum()
        print(f"  {dv}: {n_valid:,} ({100 * n_valid / main_n:.1f}%)")

    # Summary statistics
    out_dir.mkdir(parents=True, exist_ok=True)
    make_summary_stats_table(
        df=panel, variables=SUMMARY_STATS_VARS, sample_names=None,
        output_csv=out_dir / "summary_stats.csv",
        output_tex=out_dir / "summary_stats.tex",
        caption="Summary Statistics --- H23 Competition and Uncertainty (Main Sample)",
        label="tab:summary_stats_h23",
    )
    print("  Saved: summary_stats.csv/.tex")

    all_results: List[Dict[str, Any]] = []

    for spec in MODEL_SPECS:
        dv = spec["dv"]
        print(f"\n--- Model ({spec['col']}): DV={DV_LABELS.get(dv, dv)} FE={spec['fe']} ---")
        try:
            df_prepared = prepare_regression_data(panel, spec)
        except ValueError as e:
            print(f"  ERROR: {e}", file=sys.stderr)
            continue
        if len(df_prepared) < 100:
            print(f"  Skipping: too few obs")
            continue

        model, meta = run_regression(df_prepared, spec)
        if model is not None and meta:
            all_results.append({"model": model, "meta": meta})

    diag_df = save_outputs(all_results, out_dir)

    # Emit canonical suite_spec.json (consumed by generate_all_tables.py)
    _write_suite_spec_json(all_results, out_dir)

    # Attrition table
    if all_results:
        first = all_results[0]["meta"]
        n_tnic = panel[IV].notna().sum()
        attrition_stages = [
            ("Full panel (all firm-years)", full_n),
            ("Main sample (excl Finance/Utility)", main_n),
            ("log(TotalSimilarity) non-null", n_tnic),
            ("After complete-case + min-firm-years (col 1)", first["n_obs"]),
        ]
        generate_attrition_table(
            attrition_stages, out_dir, "H23 Competition → Uncertainty",
        )
        print("  Saved: sample_attrition.csv/.tex")

    generate_manifest(
        output_dir=out_dir, stage="stage4", timestamp=timestamp,
        input_paths={"panel": panel_file},
        output_files={"diagnostics": out_dir / "model_diagnostics.csv"},
        panel_path=panel_file,
    )
    print("  Saved: run_manifest.json")

    duration = (datetime.now() - start_time).total_seconds()
    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.1f}s")
    print(f"Regressions: {len(all_results)}/{len(MODEL_SPECS)}")

    # Summary of IV significance
    for r in all_results:
        m = r["meta"]
        stars = _sig_stars(m["p_one_iv"])
        print(f"  Col ({m['col']}) {DV_LABELS.get(m['dv'], m['dv'])} [{m['fe']}]: "
              f"b={m['beta_iv']:.6f} p1={m['p_one_iv']:.4f} {stars}")

    return 0


if __name__ == "__main__":
    args = parse_arguments()
    if args.dry_run:
        print("Dry-run: validating...")
        print(f"  IV: {IV}")
        print(f"  DVs: {DVS}")
        print(f"  Specs: {len(MODEL_SPECS)}")
        print(f"  Controls: {len(BASE_CONTROLS)}")
        print("[OK]")
        sys.exit(0)
    sys.exit(main(panel_path=args.panel_path))
