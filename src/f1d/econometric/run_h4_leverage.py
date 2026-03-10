#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H4 Leverage Discipline Hypothesis
================================================================================
ID: econometric/test_h4_leverage
Description: Run H4 Leverage Discipline hypothesis test by loading the call-level
             panel from Stage 3, running fixed effects OLS regressions by
             industry sample and uncertainty measure, and outputting results.

Model Specification:
    Uncertainty_t ~ Lev_{t-1} + Analyst_Uncertainty_t + [Pres_Uncertainty_t] +
                    Size + TobinsQ + ROA + CashHoldings + DividendPayer +
                    firm_maturity + earnings_volatility +
                    C(gvkey) + C(year)

Dependent Variables:
    1. Manager_QA_Uncertainty_pct
    2. CEO_QA_Uncertainty_pct
    3. Manager_QA_Weak_Modal_pct
    4. CEO_QA_Weak_Modal_pct
    5. Manager_Pres_Uncertainty_pct
    6. CEO_Pres_Uncertainty_pct

Dynamic Covariates:
    - If DV is a QA measure, the corresponding Presentation measure is added as a control.
      (e.g., Manager_QA regressions control for Manager_Pres_Uncertainty_pct)
    - Analyst_QA_Uncertainty_pct is always included as a control.

Hypothesis Tests (one-tailed):
    H4: beta(Lev_lag) < 0  -- higher prior leverage reduces current vagueness

Industry Samples:
    - Main: FF12 codes 1-7, 9-10, 12 (non-financial, non-utility)
    - Finance: FF12 code 11
    - Utility: FF12 code 8

Minimum Calls Filter:
    Firms must have >= 5 calls to be included in regression.

Inputs:
    - outputs/variables/h4_leverage/latest/h4_leverage_panel.parquet

Outputs:
    - outputs/econometric/h4_leverage/{timestamp}/regression_results_{sample}_{dv}.txt
    - outputs/econometric/h4_leverage/{timestamp}/h4_leverage_table.tex
    - outputs/econometric/h4_leverage/{timestamp}/model_diagnostics.csv
    - outputs/econometric/h4_leverage/{timestamp}/summary_stats.csv
    - outputs/econometric/h4_leverage/{timestamp}/summary_stats.tex

Deterministic: true
Dependencies:
    - Requires: Stage 3 (build_h4_leverage_panel)
    - Uses: statsmodels, linearmodels, f1d.shared.latex_tables_accounting

Author: Thesis Author
Date: 2026-02-26
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

# Silence statsmodels covariance warnings
warnings.filterwarnings(
    "ignore", message="covariance of constraints does not have full rank"
)

CONFIG = {
    "min_calls": 5,
    "dependent_variables": [
        # Original 6 uncertainty measures (112,968 calls, ~76K-108K valid per DV)
        "Manager_QA_Uncertainty_pct",
        "CEO_QA_Uncertainty_pct",
        "Manager_QA_Weak_Modal_pct",
        "CEO_QA_Weak_Modal_pct",
        "Manager_Pres_Uncertainty_pct",
        "CEO_Pres_Uncertainty_pct",
        # Clarity residuals (REDUCED SAMPLE: 42K-58K valid)
        "CEO_Clarity_Residual",
        "Manager_Clarity_Residual",
    ],
    "samples": ["Main", "Finance", "Utility"],
    "leverage_variables": ["Lev_lag", "Lev_t", "Lev_lead"],
}

BASE_CONTROLS = [
    "Analyst_QA_Uncertainty_pct",
    "Size",
    "TobinsQ",
    "ROA",
    "CashHoldings",
    "DividendPayer",
    "firm_maturity",
    "earnings_volatility",
]

PRES_CONTROL_MAP = {
    # Original DVs (require presentation control)
    "Manager_QA_Uncertainty_pct": "Manager_Pres_Uncertainty_pct",
    "CEO_QA_Uncertainty_pct": "CEO_Pres_Uncertainty_pct",
    "Manager_QA_Weak_Modal_pct": "Manager_Pres_Uncertainty_pct",
    "CEO_QA_Weak_Modal_pct": "CEO_Pres_Uncertainty_pct",
    "Manager_Pres_Uncertainty_pct": None,
    "CEO_Pres_Uncertainty_pct": None,
    # Clarity residuals: NO additional controls needed
    # Source H0.3 regression already residualized: Pres_Uncertainty, Analyst_Uncertainty,
    # Negative_Sentiment, StockRet, MarketRet, EPS_Growth, SurpDec
    "CEO_Clarity_Residual": None,
    "Manager_Clarity_Residual": None,
}


# ==============================================================================
# Summary Statistics Variables
# ==============================================================================

SUMMARY_STATS_VARS = [
    # Dependent variables (original uncertainty measures)
    {"col": "Manager_QA_Uncertainty_pct", "label": "Mgr QA Uncertainty"},
    {"col": "CEO_QA_Uncertainty_pct", "label": "CEO QA Uncertainty"},
    {"col": "Manager_QA_Weak_Modal_pct", "label": "Mgr QA Weak Modal"},
    {"col": "CEO_QA_Weak_Modal_pct", "label": "CEO QA Weak Modal"},
    {"col": "Manager_Pres_Uncertainty_pct", "label": "Mgr Pres Uncertainty"},
    {"col": "CEO_Pres_Uncertainty_pct", "label": "CEO Pres Uncertainty"},
    # NEW: Clarity residuals
    {"col": "CEO_Clarity_Residual", "label": "CEO Clarity Residual"},
    {"col": "Manager_Clarity_Residual", "label": "Mgr Clarity Residual"},
    # Main independent variables (3 temporal specs)
    {"col": "Lev_lag", "label": "Leverage$_{t-1}$"},
    {"col": "Lev_t", "label": "Leverage$_{t}$"},
    {"col": "Lev_lead", "label": "Leverage$_{t+1}$"},
    # Controls
    {"col": "Analyst_QA_Uncertainty_pct", "label": "Analyst QA Uncertainty"},
    {"col": "Size", "label": "Firm Size (log AT)"},
    {"col": "TobinsQ", "label": "Tobin's Q"},
    {"col": "ROA", "label": "ROA"},
    {"col": "CashHoldings", "label": "Cash Holdings"},
    {"col": "DividendPayer", "label": "Dividend Payer"},
    {"col": "firm_maturity", "label": "Firm Maturity"},
    {"col": "earnings_volatility", "label": "Earnings Volatility"},
]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Test H4 Leverage Discipline Hypothesis (Stage 4)"
    )
    parser.add_argument(
        "--panel-path", type=str, help="Explicit path to H4 panel parquet"
    )
    return parser.parse_args()


def prepare_regression_data(
    panel: pd.DataFrame,
    dv_var: str,
    lev_var: str = "Lev_lag",
) -> Tuple[pd.DataFrame, List[str]]:
    pres_control = PRES_CONTROL_MAP.get(dv_var)
    controls = list(BASE_CONTROLS)
    if pres_control:
        controls.append(pres_control)

    required = [dv_var, lev_var] + controls + ["gvkey", "year"]

    missing = [c for c in required if c not in panel.columns]
    if missing:
        raise ValueError(f"Missing required columns in panel: {missing}")

    df = panel.replace([np.inf, -np.inf], np.nan).dropna(subset=required).copy()

    return df, controls


def run_regression(
    df_sample: pd.DataFrame,
    dv_var: str,
    sample_name: str,
    controls: List[str],
    lev_var: str = "Lev_lag",  # "Lev_lag", "Lev_t", or "Lev_lead"
) -> Tuple[Any, Dict[str, Any]]:
    formula = (
        f"{dv_var} ~ 1 + {lev_var} + "
        + " + ".join(controls)
        + " + EntityEffects + TimeEffects"
    )

    print(
        f"  Formula: {dv_var} ~ {lev_var} + {' + '.join(controls)} + EntityEffects + TimeEffects"
    )
    print(
        f"  N calls: {len(df_sample):,}  |  N firms: {df_sample['gvkey'].nunique():,}"
    )
    print("  Estimating with firm-clustered SEs via PanelOLS...")

    t0 = datetime.now()

    df_panel = df_sample.set_index(["gvkey", "year"])

    try:
        model_obj = PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)
        model = model_obj.fit(cov_type="clustered", cluster_entity=True)
    except Exception as e:
        print(f"  ERROR: Regression failed: {e}", file=sys.stderr)
        return None, {}

    duration = (datetime.now() - t0).total_seconds()
    print(f"  [OK] Complete in {duration:.1f}s")
    print(f"  R-squared (within): {model.rsquared_within:.4f}")
    print(f"  Adj R-squared:      {model.rsquared_inclusive:.4f}")
    print(f"  N obs:              {int(model.nobs):,}")

    within_r2 = float(model.rsquared_within)
    print(f"  Within-R²: {within_r2:.4f}")

    beta1 = model.params.get(lev_var, np.nan)
    p1_two = model.pvalues.get(lev_var, np.nan)
    beta1_se = model.std_errors.get(lev_var, np.nan)
    beta1_t = model.tstats.get(lev_var, np.nan)

    # H4: beta1 < 0 (Higher leverage reduces speech uncertainty)
    if not np.isnan(p1_two) and not np.isnan(beta1):
        p1_one = p1_two / 2 if beta1 < 0 else 1 - p1_two / 2
    else:
        p1_one = np.nan

    h4_sig = not np.isnan(p1_one) and p1_one < 0.05 and beta1 < 0
    h4_text = "YES" if h4_sig else "no"

    print(
        f"  beta1 ({lev_var}):  {beta1:.4f}  SE={beta1_se:.4f}  p(one-tail)={p1_one:.4f}  H4={h4_text}"
    )

    meta = {
        "dv": dv_var,
        "sample": sample_name,
        "lev_var": lev_var,  # track which leverage variable used
        "n_obs": int(model.nobs),
        "n_firms": df_sample["gvkey"].nunique(),
        "n_clusters": df_sample["gvkey"].nunique(),
        "cluster_var": "gvkey",
        "rsquared": float(model.rsquared_within),
        "rsquared_adj": float(model.rsquared_inclusive),
        "within_r2": within_r2,
        "beta1": float(beta1),
        "beta1_se": float(beta1_se),
        "beta1_t": float(beta1_t),
        "beta1_p_two": float(p1_two),
        "beta1_p_one": float(p1_one),
        "h4_sig": h4_sig,
    }

    return model, meta


def _save_latex_tables(all_results: List[Dict[str, Any]], out_dir: Path) -> None:
    """
    Generate THREE LaTeX tables:
    1. Original 6 uncertainty measures (h4_leverage_table_uncertainty.tex)
    2. Clarity residuals (h4_leverage_table_residuals.tex)
    3. Full comparison with all leverage specs (h4_leverage_table_full.tex)
    """

    # Separate results by DV type
    original_dvs = [
        "Manager_QA_Uncertainty_pct",
        "CEO_QA_Uncertainty_pct",
        "Manager_QA_Weak_Modal_pct",
        "CEO_QA_Weak_Modal_pct",
        "Manager_Pres_Uncertainty_pct",
        "CEO_Pres_Uncertainty_pct",
    ]
    residual_dvs = ["CEO_Clarity_Residual", "Manager_Clarity_Residual"]

    # Helper functions
    def get_res(dv, sample="Main", lev_var="Lev_lag"):
        for r in all_results:
            if r["sample"] == sample and r["dv"] == dv and r["lev_var"] == lev_var:
                return r
        return None

    def fmt_coef(val, pval):
        if val is None or pd.isna(val):
            return ""
        stars = ""
        if pval < 0.01:
            stars = "^{***}"
        elif pval < 0.05:
            stars = "^{**}"
        elif pval < 0.10:
            stars = "^{*}"
        return f"{val:.4f}{stars}"

    def fmt_se(val):
        if val is None or pd.isna(val):
            return ""
        return f"({val:.4f})"

    def fmt_r2(val):
        if val is None or pd.isna(val):
            return ""
        return f"{val:.4f}"

    # =========================================================================
    # Table 1: Original 6 Uncertainty Measures (Main sample, Lev_lag only)
    # =========================================================================
    dv_labels = [
        ("Manager_QA_Uncertainty_pct", "Mgr QA Unc"),
        ("CEO_QA_Uncertainty_pct", "CEO QA Unc"),
        ("Manager_QA_Weak_Modal_pct", "Mgr QA Weak"),
        ("CEO_QA_Weak_Modal_pct", "CEO QA Weak"),
        ("Manager_Pres_Uncertainty_pct", "Mgr Pres Unc"),
        ("CEO_Pres_Uncertainty_pct", "CEO Pres Unc"),
    ]

    results = [get_res(dv, "Main", "Lev_lag") for dv, _ in dv_labels]

    lines = [
        "\\begin{table}[htbp]",
        "\\centering",
        "\\caption{H4: Leverage Discipline and Speech Vagueness}",
        "\\label{tab:h4_leverage}",
        "\\begin{tabular}{lcccccc}",
        "\\toprule",
        " & \\multicolumn{4}{c}{Q\\&A Session} & \\multicolumn{2}{c}{Presentation} \\\\",
        "\\cmidrule(lr){2-5} \\cmidrule(lr){6-7}",
        " & (1) & (2) & (3) & (4) & (5) & (6) \\\\",
        "\\midrule",
    ]

    # Row: Lev_lag coefficient
    row = "Leverage$_{t-1}$ & "
    row += " & ".join([fmt_coef(r["beta1"], r["beta1_p_one"]) if r else "" for r in results])
    row += " \\\\"
    lines.append(row)

    # Row: SE
    row = " & " + " & ".join([fmt_se(r["beta1_se"]) if r else "" for r in results]) + " \\\\"
    lines.append(row)

    lines.extend([
        "\\midrule",
        "Pres. Uncertainty & Yes & Yes & Yes & Yes & No & No \\\\",
        "Controls & Yes & Yes & Yes & Yes & Yes & Yes \\\\",
        "Firm FE & Yes & Yes & Yes & Yes & Yes & Yes \\\\",
        "Year FE & Yes & Yes & Yes & Yes & Yes & Yes \\\\",
        "\\midrule",
    ])

    # Observations row
    row = "Observations & " + " & ".join([f"{r['n_obs']:,}" if r else "" for r in results]) + " \\\\"
    lines.append(row)

    # Within-R² row
    row = "Within-$R^2$ & " + " & ".join([fmt_r2(r["within_r2"]) if r else "" for r in results]) + " \\\\"
    lines.append(row)

    lines.extend([
        "\\bottomrule",
        "\\end{tabular}",
        "\\\\[-0.5em]",
        "\\parbox{\\textwidth}{\\scriptsize ",
        "\\textit{Notes:} "
        "This table reports the effect of prior leverage on speech vagueness. "
        "Columns (1)--(4) use Q\\&A session measures; columns (5)--(6) use presentation measures. "
        "All models use the Main industry sample (non-financial, non-utility firms). "
        "Firms with fewer than 5 calls are excluded. "
        "Standard errors are clustered at the firm level. "
        "Variables are winsorized at 1\\%/99\\% by year.",
        "}",
        "\\end{table}",
    ])

    with open(out_dir / "h4_leverage_table_uncertainty.tex", "w") as f:
        f.write("\n".join(lines))
    print("  Saved: h4_leverage_table_uncertainty.tex")

    # =========================================================================
    # Table 2: Clarity Residuals (with explicit N documentation)
    # =========================================================================
    residual_labels = [
        ("CEO_Clarity_Residual", "CEO Clarity"),
        ("Manager_Clarity_Residual", "Mgr Clarity"),
    ]

    residual_results = {dv: get_res(dv, "Main", "Lev_lag") for dv, _ in residual_labels}

    lines = [
        "\\begin{table}[htbp]",
        "\\centering",
        "\\caption{H4: Leverage Discipline and CEO Clarity Residuals}",
        "\\label{tab:h4_leverage_residuals}",
        "\\begin{tabular}{lcc}",
        "\\toprule",
        " & (1) & (2) \\\\",
        " & CEO Clarity & Mgr Clarity \\\\",
        "\\midrule",
    ]

    # Row: Lev_lag coefficient
    row = "Leverage$_{t-1}$ & "
    r1 = residual_results.get("CEO_Clarity_Residual")
    r2 = residual_results.get("Manager_Clarity_Residual")
    row += f"{fmt_coef(r1['beta1'], r1['beta1_p_one']) if r1 else ''} & "
    row += f"{fmt_coef(r2['beta1'], r2['beta1_p_one']) if r2 else ''} \\\\"
    lines.append(row)

    # Row: SE
    row = " & "
    row += f"{fmt_se(r1['beta1_se']) if r1 else ''} & "
    row += f"{fmt_se(r2['beta1_se']) if r2 else ''} \\\\"
    lines.append(row)

    lines.extend([
        "\\midrule",
        "Firm FE & Yes & Yes \\\\",
        "Year FE & Yes & Yes \\\\",
        "\\midrule",
    ])

    # Observations row with explicit N
    row = f"Observations & {r1['n_obs']:,} & {r2['n_obs']:,} \\\\" if r1 and r2 else "Observations &  &  \\\\"
    lines.append(row)

    # Within-R² row
    row = "Within-$R^2$ & "
    row += f"{fmt_r2(r1['within_r2']) if r1 else ''} & "
    row += f"{fmt_r2(r2['within_r2']) if r2 else ''} \\\\"
    lines.append(row)

    lines.extend([
        "\\bottomrule",
        "\\end{tabular}",
        "\\\\[-0.5em]",
        "\\parbox{\\textwidth}{\\scriptsize ",
        "\\textit{Notes:} "
        "This table reports the effect of prior leverage on CEO and Manager clarity residuals. "
        "Clarity residuals are pre-computed from H0.3 regressions that residualized "
        "presentation uncertainty, analyst uncertainty, negative sentiment, stock returns, "
        "market returns, EPS growth, and earnings surprise. "
        "\\textbf{Note:} The sample is significantly smaller than the main table "
        "(CEO: N~42K; Manager: N~58K vs. full panel N=112,968) due to clarity residual availability. "
        "Firms with fewer than 5 calls are excluded. "
        "Standard errors are clustered at the firm level.",
        "}",
        "\\end{table}",
    ])

    with open(out_dir / "h4_leverage_table_residuals.tex", "w") as f:
        f.write("\n".join(lines))
    print("  Saved: h4_leverage_table_residuals.tex")

    # =========================================================================
    # Table 3: Full Comparison (all 8 DVs × 3 lev_vars) as appendix
    # =========================================================================
    all_dvs = original_dvs + residual_dvs
    lev_labels = [
        ("Lev_lag", "Leverage$_{t-1}$"),
        ("Lev_t", "Leverage$_{t}$"),
        ("Lev_lead", "Leverage$_{t+1}$"),
    ]

    # Create a wide table with 8 columns (one per DV)
    lines = [
        "\\begin{table}[htbp]",
        "\\centering",
        "\\caption{H4: Leverage Discipline — Full Temporal Comparison (Appendix)}",
        "\\label{tab:h4_leverage_full}",
        "\\resizebox{\\textwidth}{!}{%",
        "\\begin{tabular}{l" + "c" * len(all_dvs) + "}",
        "\\toprule",
    ]

    # Header row with DV names (abbreviated)
    dv_short = [
        "Mgr QA", "CEO QA", "Mgr WM", "CEO WM", "Mgr Pres", "CEO Pres",
        "CEO Clr", "Mgr Clr"
    ]
    lines.append(" & " + " & ".join(dv_short) + " \\\\")
    lines.append("\\midrule")

    # For each leverage variable, add coefficient and SE rows
    for lev_var, lev_label in lev_labels:
        results_row = [get_res(dv, "Main", lev_var) for dv in all_dvs]

        # Coefficient row
        row = f"{lev_label} & "
        row += " & ".join([fmt_coef(r["beta1"], r["beta1_p_one"]) if r else "" for r in results_row])
        row += " \\\\"
        lines.append(row)

        # SE row
        row = " & " + " & ".join([fmt_se(r["beta1_se"]) if r else "" for r in results_row]) + " \\\\"
        lines.append(row)

    lines.extend([
        "\\midrule",
        "Controls & Yes & Yes & Yes & Yes & Yes & Yes & Yes & Yes \\\\",
        "Firm FE & Yes & Yes & Yes & Yes & Yes & Yes & Yes & Yes \\\\",
        "Year FE & Yes & Yes & Yes & Yes & Yes & Yes & Yes & Yes \\\\",
        "\\bottomrule",
        "\\end{tabular}",
        "}",
        "\\\\[-0.5em]",
        "\\parbox{\\textwidth}{\\scriptsize ",
        "\\textit{Notes:} "
        "This appendix table compares the effect of lagged (t-1), contemporaneous (t), "
        "and forward (t+1) leverage on all uncertainty measures and clarity residuals. "
        "All models use the Main industry sample. "
        "Clarity residual columns have significantly smaller N (42K-58K vs 76K-108K). "
        "Firms with fewer than 5 calls are excluded. "
        "Standard errors are clustered at the firm level.",
        "}",
        "\\end{table}",
    ])

    with open(out_dir / "h4_leverage_table_full.tex", "w") as f:
        f.write("\n".join(lines))
    print("  Saved: h4_leverage_table_full.tex")


def _save_latex_table(all_results: List[Dict[str, Any]], out_dir: Path) -> None:
    """Legacy wrapper - calls _save_latex_tables for backwards compatibility."""
    _save_latex_tables(all_results, out_dir)


def main(panel_path: str | None = None) -> int:
    t0 = datetime.now()
    timestamp = t0.strftime("%Y-%m-%d_%H%M%S")
    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "h4_leverage" / timestamp

    # Setup logging to timestamped directory
    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H4_Leverage",
        timestamp=timestamp,
    )

    print("=" * 80)
    print("STAGE 4: Test H4 Leverage Discipline Hypothesis (call-level)")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Log dir:   {log_dir}")

    if not panel_path:
        try:
            panel_dir = get_latest_output_dir(
                root / "outputs" / "variables" / "h4_leverage",
                required_file="h4_leverage_panel.parquet",
            )
            panel_file = panel_dir / "h4_leverage_panel.parquet"
        except Exception as e:
            print(f"ERROR: Could not find Stage 3 panel: {e}")
            return 1
    else:
        panel_file = Path(panel_path)

    print("\n" + "=" * 60)
    print("Loading panel")
    print("=" * 60)
    print(f"  Loaded: {panel_file}")
    panel = pd.read_parquet(
        panel_file,
        columns=[
            "file_name",
            "gvkey",
            "year",
            "ff12_code",
            # Dependent variables (original 6)
            "Manager_QA_Uncertainty_pct",
            "CEO_QA_Uncertainty_pct",
            "Manager_QA_Weak_Modal_pct",
            "CEO_QA_Weak_Modal_pct",
            "Manager_Pres_Uncertainty_pct",
            "CEO_Pres_Uncertainty_pct",
            # Dependent variables (clarity residuals)
            "CEO_Clarity_Residual",
            "Manager_Clarity_Residual",
            # Leverage variables (3 temporal specs)
            "Lev_lag",
            "Lev_t",
            "Lev_lead",
            # Base controls
            "Analyst_QA_Uncertainty_pct",
            "Size",
            "TobinsQ",
            "ROA",
            "CashHoldings",
            "DividendPayer",
            "firm_maturity",
            "earnings_volatility",
        ],
    )
    print(f"  Rows: {len(panel):,}")
    print(f"  Columns: {len(panel.columns)}")

    if "sample" not in panel.columns:
        panel["sample"] = assign_industry_sample(panel["ff12_code"])

    out_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Summary Statistics (call-level, by sample)
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("Generating summary statistics")
    print("=" * 60)
    summary_vars = [
        {"col": v["col"], "label": v["label"]}
        for v in SUMMARY_STATS_VARS
        if v["col"] in panel.columns
    ]
    make_summary_stats_table(
        df=panel,
        variables=summary_vars,
        sample_names=["Main", "Finance", "Utility"],
        sample_col="sample",
        output_csv=out_dir / "summary_stats.csv",
        output_tex=out_dir / "summary_stats.tex",
        caption="Summary Statistics — H4 Leverage Discipline",
        label="tab:summary_stats_h4",
    )
    print("  Saved: summary_stats.csv")
    print("  Saved: summary_stats.tex")

    all_results = []

    LEV_VARS = CONFIG["leverage_variables"]  # ["Lev_lag", "Lev_t", "Lev_lead"]

    for lev_var in LEV_VARS:
        for dv in CONFIG["dependent_variables"]:
            for sample in CONFIG["samples"]:
                print(f"\n--- {lev_var} / {sample} / {dv} ---")

                df_prep, controls = prepare_regression_data(panel, dv, lev_var)

                if sample == "Main":
                    df_sample = df_prep[df_prep["sample"] == "Main"].copy()
                elif sample == "Finance":
                    df_sample = df_prep[df_prep["sample"] == "Finance"].copy()
                else:
                    df_sample = df_prep[df_prep["sample"] == "Utility"].copy()

                df_sample["gvkey_count"] = df_sample.groupby("gvkey")[
                    "file_name"
                ].transform("count")
                df_filtered = df_sample[
                    df_sample["gvkey_count"] >= CONFIG["min_calls"]
                ].copy()

                print(
                    f"  After filters: {len(df_filtered):,} calls, {df_filtered['gvkey'].nunique():,} firms"
                )

                if len(df_filtered) < 100:
                    print("  Skipping: insufficient data")
                    continue

                print(f"\n============================================================")
                print(f"Running regression: {lev_var} / {sample} / {dv}")
                print(f"============================================================")

                model, meta = run_regression(df_filtered, dv, sample, controls, lev_var)

                if model is not None:
                    all_results.append(meta)
                    with open(out_dir / f"regression_results_{lev_var}_{sample}_{dv}.txt", "w") as f:
                        f.write(str(model.summary))

    _save_latex_table(all_results, out_dir)
    pd.DataFrame(all_results).to_csv(out_dir / "model_diagnostics.csv", index=False)

    # Generate sample attrition table
    if all_results:
        main_result = next((r for r in all_results if r.get("sample") == "Main"), all_results[0])
        attrition_stages = [
            ("Master manifest", len(panel)),
            ("Main sample filter", (panel["sample"] == "Main").sum()),
            ("After complete-case + min-calls filter", main_result.get("n_obs", 0)),
        ]
        generate_attrition_table(attrition_stages, out_dir, "H4 Leverage Discipline")
        print("  Saved: sample_attrition.csv and sample_attrition.tex")

    # Generate run manifest
    generate_manifest(
        output_dir=out_dir,
        stage="stage4",
        timestamp=timestamp,
        input_paths={"panel": panel_file},
        output_files={
            "diagnostics": out_dir / "model_diagnostics.csv",
            "table": out_dir / "h4_leverage_table.tex",
        },
        panel_path=panel_file,
    )
    print("  Saved: run_manifest.json")

    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    parser = parse_arguments()
    sys.exit(main(panel_path=parser.panel_path))
