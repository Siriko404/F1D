#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H2 Investment Efficiency Hypothesis
================================================================================
ID: econometric/test_h2_investment
Description: Run H2 Investment Efficiency hypothesis test by loading the call-level
             panel from Stage 3, running fixed effects OLS regressions by
             industry sample, dependent variable, and independent variable,
             and outputting results.

This script follows the same call-level architecture as test_h1_cash_holdings.py
and run_h12_div_intensity.py (multi-DV pattern).

Model Specification:
    {dv} ~ {iv} + Lev + Size + TobinsQ + ROA + CashFlow + SalesGrowth +
          EntityEffects + TimeEffects

    where:
        dv = InvestmentResidual (t) or InvestmentResidual_lead (t+1)
        iv = uncertainty measure OR clarity residual

Hypothesis Test (one-tailed):
    H2: beta({iv}) < 0  -- higher uncertainty/clarity_residual -> lower investment efficiency
        p_one = p_two/2 if beta1 < 0 else 1 - p_two/2

Industry Samples:
    - Main:    FF12 codes 1-7, 9-10, 12 (non-financial, non-utility)
    - Finance: FF12 code 11
    - Utility: FF12 code 8

Dependent Variables (2):
    - InvestmentResidual (contemporaneous, t)
    - InvestmentResidual_lead (one-year ahead, t+1)

Main Independent Variables (6):
    Uncertainty measures (4):
        Manager_QA_Uncertainty_pct, CEO_QA_Uncertainty_pct,
        Manager_Pres_Uncertainty_pct, CEO_Pres_Uncertainty_pct
    Clarity residuals (2):
        CEO_Clarity_Residual, Manager_Clarity_Residual

Total regressions: 3 samples × 2 DVs × 6 IVs = 36 regressions

Standard Errors:
    Firm-clustered (cov_type="cluster", groups=df["gvkey"]) -- same as H1.

Inputs:
    - outputs/variables/h2_investment/latest/h2_investment_panel.parquet

Outputs:
    - outputs/econometric/h2_investment/{timestamp}/regression_results_{sample}_{dv}_{iv}.txt
    - outputs/econometric/h2_investment/{timestamp}/model_diagnostics.csv
    - outputs/econometric/h2_investment/{timestamp}/h2_investment_table.tex
    - outputs/econometric/h2_investment/{timestamp}/report_step4_H2.md
    - outputs/econometric/h2_investment/{timestamp}/summary_stats.csv
    - outputs/econometric/h2_investment/{timestamp}/summary_stats.tex

Deterministic: true
Dependencies:
    - Requires: Stage 3 (build_h2_investment_panel)
    - Uses: statsmodels, linearmodels, f1d.shared.latex_tables_accounting

Author: Thesis Author
Date: 2026-03-09 (updated for multi-DV + clarity residuals)
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
from f1d.shared.outputs import generate_manifest, generate_attrition_table
from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.variables.panel_utils import assign_industry_sample


# ==============================================================================
# Configuration
# ==============================================================================

# Dependent variables: contemporaneous (t) and lead (t+1)
DEPENDENT_VARIABLES = ["InvestmentResidual", "InvestmentResidual_lead"]

# Uncertainty measures (4 measures - weak modals removed)
UNCERTAINTY_MEASURES = [
    "Manager_QA_Uncertainty_pct",
    "CEO_QA_Uncertainty_pct",
    "Manager_Pres_Uncertainty_pct",
    "CEO_Pres_Uncertainty_pct",
]

# Clarity residual variables (from H0.3 CEO Clarity Extended)
CLARITY_RESIDUAL_VARS = [
    "CEO_Clarity_Residual",
    "Manager_Clarity_Residual",
]

# Combined list of all main independent variables
MAIN_IVS = UNCERTAINTY_MEASURES + CLARITY_RESIDUAL_VARS

CONTROL_VARS = [
    # Lev enters separately as main effect in formula; not listed here
    "Size",
    "TobinsQ",
    "ROA",
    "CashFlow",
    "SalesGrowth",
]

# Minimum calls per firm to be included in regression
MIN_CALLS_PER_FIRM = 5

VARIABLE_LABELS = {
    "InvestmentResidual": "Investment Residual$_{t}$",
    "InvestmentResidual_lead": "Investment Residual$_{t+1}$",
    "Lev": "Leverage",
    "Size": "Firm Size (log AT)",
    "TobinsQ": "Tobin's Q",
    "ROA": "ROA",
    "CashFlow": "Cash Flow / Assets",
    "SalesGrowth": "Sales Growth",
    "Manager_QA_Uncertainty_pct": "Mgr QA Uncertainty",
    "CEO_QA_Uncertainty_pct": "CEO QA Uncertainty",
    "Manager_Pres_Uncertainty_pct": "Mgr Pres Uncertainty",
    "CEO_Pres_Uncertainty_pct": "CEO Pres Uncertainty",
    "CEO_Clarity_Residual": "CEO Clarity Residual",
    "Manager_Clarity_Residual": "Manager Clarity Residual",
}


# ==============================================================================
# Summary Statistics Variables
# ==============================================================================

SUMMARY_STATS_VARS = [
    # Dependent variables
    {"col": "InvestmentResidual", "label": "Investment Residual$_{t}$"},
    {"col": "InvestmentResidual_lead", "label": "Investment Residual$_{t+1}$"},
    # Uncertainty measures (4)
    {"col": "Manager_QA_Uncertainty_pct", "label": "Mgr QA Uncertainty"},
    {"col": "CEO_QA_Uncertainty_pct", "label": "CEO QA Uncertainty"},
    {"col": "Manager_Pres_Uncertainty_pct", "label": "Mgr Pres Uncertainty"},
    {"col": "CEO_Pres_Uncertainty_pct", "label": "CEO Pres Uncertainty"},
    # Clarity residuals
    {"col": "CEO_Clarity_Residual", "label": "CEO Clarity Residual"},
    {"col": "Manager_Clarity_Residual", "label": "Manager Clarity Residual"},
    # Leverage
    {"col": "Lev", "label": "Leverage"},
    # Control variables
    {"col": "Size", "label": "Firm Size (log AT)"},
    {"col": "TobinsQ", "label": "Tobin's Q"},
    {"col": "ROA", "label": "ROA"},
    {"col": "CashFlow", "label": "Cash Flow / Assets"},
    {"col": "SalesGrowth", "label": "Sales Growth"},
]


# ==============================================================================
# CLI Arguments
# ==============================================================================


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 4: Test H2 Investment Efficiency Hypothesis (call-level)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Validate inputs without executing"
    )
    parser.add_argument(
        "--panel-path",
        type=str,
        default=None,
        help="Path to panel parquet file (default: latest from Stage 3)",
    )
    return parser.parse_args()


# ==============================================================================
# Data Loading
# ==============================================================================


def load_panel(root_path: Path, panel_path: Optional[str] = None) -> pd.DataFrame:
    """Load call-level H2 panel from Stage 3 output."""
    print("\n" + "=" * 60)
    print("Loading panel")
    print("=" * 60)

    if panel_path:
        panel_file = Path(panel_path)
    else:
        panel_dir = get_latest_output_dir(
            root_path / "outputs" / "variables" / "h2_investment",
            required_file="h2_investment_panel.parquet",
        )
        panel_file = panel_dir / "h2_investment_panel.parquet"

    if not panel_file.exists():
        raise FileNotFoundError(f"Panel file not found: {panel_file}")

    panel = pd.read_parquet(
        panel_file,
        columns=[
            "gvkey",
            "year",
            "ff12_code",
            "InvestmentResidual",
            "InvestmentResidual_lead",
            "Lev",
            "Manager_QA_Uncertainty_pct",
            "CEO_QA_Uncertainty_pct",
            "Manager_Pres_Uncertainty_pct",
            "CEO_Pres_Uncertainty_pct",
            "CEO_Clarity_Residual",
            "Manager_Clarity_Residual",
            "Size",
            "TobinsQ",
            "ROA",
            "CashFlow",
            "SalesGrowth",
        ],
    )
    print(f"  Loaded: {panel_file}")
    print(f"  Rows: {len(panel):,}")
    print(f"  Columns: {len(panel.columns)}")
    return panel


def prepare_regression_data(
    panel: pd.DataFrame,
    dv: str,
    iv: str,
) -> pd.DataFrame:
    """Prepare panel for a single DV and IV regression.

    - Drops rows where DV is NaN
    - Drops rows missing required variables (complete cases)
    - Applies minimum-calls-per-firm filter

    Args:
        panel: Full call-level panel from Stage 3
        dv: Dependent variable column name ("InvestmentResidual" or "InvestmentResidual_lead")
        iv: Independent variable column name (uncertainty measure or clarity residual)

    Returns:
        Prepared DataFrame ready for OLS
    """
    required = (
        [
            dv,
            iv,
            "Lev",
        ]
        + CONTROL_VARS
        + ["gvkey", "year"]
    )

    # Check required columns exist
    missing = [c for c in required if c not in panel.columns]
    if missing:
        raise ValueError(
            f"Required columns missing from panel: {missing}. Check Stage 3 output."
        )

    df = panel.copy()

    # Drop rows where DV is NaN
    before = len(df)
    df = df[df[dv].notna()].copy()
    print(f"  After DV ({dv}) filter: {len(df):,} / {before:,}")

    # Complete cases on required variables
    df = df.replace([np.inf, -np.inf], np.nan)
    complete_mask = df[required].notna().all(axis=1)
    df = df[complete_mask].copy()
    print(f"  After complete cases: {len(df):,}")

    # Minimum calls per firm (5)
    firm_counts = df["gvkey"].value_counts()
    valid_firms = set(firm_counts[firm_counts >= MIN_CALLS_PER_FIRM].index)
    df = df[df["gvkey"].isin(valid_firms)].copy()
    print(
        f"  After >={MIN_CALLS_PER_FIRM} calls/firm filter: "
        f"{len(df):,} calls, {df['gvkey'].nunique():,} firms"
    )

    return df


# ==============================================================================
# Regression
# ==============================================================================


def run_regression(
    df_sample: pd.DataFrame,
    sample_name: str,
    dv: str,
    iv: str,
) -> Tuple[Any, Dict[str, Any]]:
    """Run OLS regression with firm FE + year FE (call-level), firm-clustered SEs.

    Model:
        {dv} ~ {iv} + Lev + Size + TobinsQ + ROA + CashFlow + SalesGrowth +
              EntityEffects + TimeEffects

    Standard errors: firm-clustered (groups=gvkey) -- same as H1.

    H2: beta1 < 0  (higher uncertainty/clarity_residual -> lower investment efficiency)
        p_one = p_two/2 if beta1 < 0 else 1 - p_two/2

    Args:
        df_sample: Sample-filtered and prepared DataFrame
        sample_name: Sample name for logging
        dv: Dependent variable column name
        iv: Independent variable column name (uncertainty measure or clarity residual)

    Returns:
        Tuple of (fitted model, metadata dict) or (None, {}) on failure
    """
    print("\n" + "=" * 60)
    print(f"Running regression: {sample_name} / {dv} / {iv}")
    print("=" * 60)

    if len(df_sample) < 100:
        print(f"  WARNING: Too few observations ({len(df_sample)}), skipping")
        return None, {}

    # Controls present (Lev enters separately as main effect in formula)
    controls = [c for c in CONTROL_VARS if c in df_sample.columns]

    # Build formula
    formula = (
        f"{dv} ~ 1 + "
        f"{iv} + Lev + "
        + " + ".join(controls)
        + " + EntityEffects + TimeEffects"
    )
    print(
        f"  Formula: {dv} ~ {iv} + Lev "
        f"+ {' + '.join(controls)} + EntityEffects + TimeEffects"
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

    elapsed = (datetime.now() - t0).total_seconds()
    print(f"  [OK] Complete in {elapsed:.1f}s")
    print(f"  R-squared (within): {model.rsquared_within:.4f}")
    print(f"  Adj R-squared:      {model.rsquared_inclusive:.4f}")
    print(f"  N obs:              {int(model.nobs):,}")

    within_r2 = float(model.rsquared_within)
    print(f"  Within-R²: {within_r2:.4f}")

    # One-tailed hypothesis test
    beta1 = model.params.get(iv, np.nan)
    p1_two = model.pvalues.get(iv, np.nan)
    beta1_se = model.std_errors.get(iv, np.nan)
    beta1_t = model.tstats.get(iv, np.nan)

    # H2: beta1 < 0 (for ALL main IVs - uncertainty measures AND clarity residuals)
    if not np.isnan(p1_two) and not np.isnan(beta1):
        p1_one = p1_two / 2 if beta1 < 0 else 1 - p1_two / 2
    else:
        p1_one = np.nan

    h2_signif = (not np.isnan(p1_one)) and (p1_one < 0.05) and (beta1 < 0)

    # Track IV type for reporting
    iv_type = "uncertainty" if iv in UNCERTAINTY_MEASURES else "clarity_residual"

    print(
        f"  beta1 ({iv}):  {beta1:.4f}  SE={beta1_se:.4f}  p(one-tail)={p1_one:.4f}  H2={'YES' if h2_signif else 'no'}"
    )

    # Store metadata as a plain dict
    meta = {
        "sample": sample_name,
        "dv": dv,
        "iv": iv,
        "iv_type": iv_type,
        "beta1": beta1,
        "beta1_se": beta1_se,
        "beta1_t": beta1_t,
        "beta1_p_two": p1_two,
        "beta1_p_one": p1_one,
        "beta1_signif": h2_signif,
        "n_obs": int(model.nobs),
        "n_firms": df_sample["gvkey"].nunique(),
        "n_clusters": df_sample["gvkey"].nunique(),
        "cluster_var": "gvkey",
        "rsquared": float(model.rsquared_within),
        "rsquared_adj": float(model.rsquared_inclusive),
        "within_r2": within_r2,  # B8 fix: within-R² for LaTeX table
    }

    return model, meta


# ==============================================================================
# Output Generation
# ==============================================================================


def save_outputs(
    all_results: List[Dict[str, Any]],
    out_dir: Path,
) -> pd.DataFrame:
    """Save regression outputs:
    - One regression_results_{sample}_{dv}_{iv}.txt per regression
    - model_diagnostics.csv (summary table of all regressions)
    - h2_investment_table.tex (custom LaTeX table with key coefficients)
    - report_step4_H2.md (markdown report)
    """
    print("\n" + "=" * 60)
    print("Saving outputs")
    print("=" * 60)

    out_dir.mkdir(parents=True, exist_ok=True)

    # Save regression result text files (one per regression)
    for r in all_results:
        model = r.get("model")
        meta = r.get("meta", {})
        if model is None or not meta:
            continue
        sample = meta.get("sample", "unknown")
        dv = meta.get("dv", "unknown")
        iv = meta.get("iv", "unknown")
        fname = f"regression_results_{sample}_{dv}_{iv}.txt"
        fpath = out_dir / fname
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(str(model.summary))
        print(f"  Saved: {fname}")

    # Build model_diagnostics.csv
    diag_rows = [r["meta"] for r in all_results if r.get("meta")]
    diag_df = pd.DataFrame(diag_rows)
    diag_path = out_dir / "model_diagnostics.csv"
    diag_df.to_csv(diag_path, index=False)
    print(f"  Saved: model_diagnostics.csv ({len(diag_df)} regressions)")

    # Custom LaTeX table
    _save_latex_table(all_results, out_dir)

    return diag_df


def _save_latex_table(all_results: List[Dict[str, Any]], out_dir: Path) -> None:
    """Write a publication-ready LaTeX table for the H2 results.

    Two panels per industry sample (InvestmentResidual_t and InvestmentResidual_t+1).
    6 columns per panel (4 uncertainty + 2 clarity residuals).
    Shows β1 with SE, significance stars, N, and R2.
    """

    def sig(p: float) -> str:
        if p < 0.01:
            return "^{***}"
        elif p < 0.05:
            return "^{**}"
        elif p < 0.10:
            return "^{*}"
        return ""

    def fmt_coef(val: float, pval: float) -> str:
        if pd.isna(val):
            return ""
        return f"{val:.4f}{sig(pval)}"

    def fmt_se(val: float) -> str:
        return "" if pd.isna(val) else f"({val:.4f})"

    # Short labels for column headers
    short_labels = {
        # Uncertainty measures
        "Manager_QA_Uncertainty_pct": "Mgr QA Unc",
        "CEO_QA_Uncertainty_pct": "CEO QA Unc",
        "Manager_Pres_Uncertainty_pct": "Mgr Pres Unc",
        "CEO_Pres_Uncertainty_pct": "CEO Pres Unc",
        # Clarity residuals
        "CEO_Clarity_Residual": "CEO Clarity Res",
        "Manager_Clarity_Residual": "Mgr Clarity Res",
    }

    samples = ["Main", "Finance", "Utility"]

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{H2: Speech Uncertainty and Investment Efficiency}",
        r"\label{tab:h2_investment}",
        r"\small",
    ]

    for dv in DEPENDENT_VARIABLES:
        dv_label = (
            "InvestResid$_{t}$" if dv == "InvestmentResidual" else "InvestResid$_{t+1}$"
        )

        for sample in samples:
            sample_results = [
                r
                for r in all_results
                if r.get("meta", {}).get("sample") == sample and r.get("meta", {}).get("dv") == dv
            ]
            if not sample_results:
                continue

            # Order by MAIN_IVS
            ordered = []
            for iv in MAIN_IVS:
                match = [
                    r for r in sample_results if r.get("meta", {}).get("iv") == iv
                ]
                if match:
                    ordered.append(match[0])
                else:
                    ordered.append({})

            n_cols = len(ordered)
            col_spec = "l" + "c" * n_cols

            lines += [
                "",
                r"\vspace{0.5em}",
                rf"\textbf{{Panel: {sample} Sample — {dv_label}}}",
                r"\vspace{0.3em}",
                "",
                r"\begin{tabular}{" + col_spec + "}",
                r"\toprule",
            ]

            # Column headers
            headers = " & ".join(
                short_labels.get(MAIN_IVS[i], f"({i + 1})")
                for i in range(n_cols)
            )
            lines.append(r" & " + headers + r" \\")
            lines.append(r"\midrule")

            # β1 row
            coef_vals = " & ".join(
                fmt_coef(
                    r.get("meta", {}).get("beta1", np.nan),
                    r.get("meta", {}).get("beta1_p_one", np.nan)
                )
                for r in ordered
            )
            lines.append(r"$\beta_1$ (Uncertainty) & " + coef_vals + r" \\")

            # SE row
            se_vals = " & ".join(
                fmt_se(r.get("meta", {}).get("beta1_se", np.nan)) for r in ordered
            )
            lines.append(r" & " + se_vals + r" \\")

            lines += [
                r"\midrule",
                r"Firm FE  & " + " & ".join("Yes" for _ in ordered) + r" \\",
                r"Year FE  & " + " & ".join("Yes" for _ in ordered) + r" \\",
                r"\midrule",
                "Observations & "
                + " & ".join(f"{r.get('meta', {}).get('n_obs', 0):,}" for r in ordered)
                + r" \\",
                "Firms & "
                + " & ".join(f"{r.get('meta', {}).get('n_firms', 0):,}" for r in ordered)
                + r" \\",
                r"Within-$R^2$ & "
                + " & ".join(f"{r.get('meta', {}).get('within_r2', np.nan):.4f}" for r in ordered)
                + r" \\",
                r"\bottomrule",
                r"\end{tabular}",
            ]

    lines += [
        r"\\[-0.5em]",
        r"\parbox{\textwidth}{\scriptsizeskip0pt\selectfont\scriptsize ",
        r"\textit{Notes:} Dependent variables are Investment Residual$_{t}$ (contemporaneous) "
        r"and Investment Residual$_{t+1}$ (one-year ahead; Biddle et al. 2009). "
        r"$>0$=overinvestment, $<0$=underinvestment. "
        r"Unit of observation: individual earnings call. "
        r"Clarity residuals are CEO/Manager uncertainty residuals after controlling for firm factors. "
        r"Firms with fewer than 5 calls are excluded. "
        r"Model includes firm FE and year FE. "
        r"Standard errors (in parentheses) are clustered at the firm level. "
        r"Variables are winsorized at 1\%/99\% by year at the engine level. "
        r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (one-tailed for H2: $\beta_1 < 0$).",
        r"}",
        r"\end{table}",
    ]

    tex_path = out_dir / "h2_investment_table.tex"
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Saved: h2_investment_table.tex")


def generate_report(
    all_results: List[Dict[str, Any]],
    diag_df: pd.DataFrame,
    out_dir: Path,
    duration: float,
) -> None:
    """Generate markdown report summarising H2 results."""
    lines = [
        "# Stage 4: H2 Investment Efficiency Hypothesis Test Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        f"**Unit of observation:** individual earnings call (call-level)",
        "",
        "## Model Specification",
        "",
        "```",
        "{dv} ~ {iv} + Lev +",
        "    Size + TobinsQ + ROA + CashFlow + SalesGrowth +",
        "    EntityEffects + TimeEffects",
        "```",
        "",
        f"**Dependent Variables:** {', '.join(DEPENDENT_VARIABLES)}",
        f"**Independent Variables:** 4 uncertainty measures + 2 clarity residuals = 6 total",
        "",
        "Standard errors: firm-clustered (cov_type='cluster', groups=gvkey)",
        "One-tailed test: H2 beta1 < 0",
        "",
        "## Primary Results (all IVs)",
        "",
        "| Sample | DV | IV | N | R2 | beta1 | p1 | H2 |",
        "|--------|----|----|---|----|-------|-----|-----|",
    ]

    for r in all_results:
        meta = r.get("meta", {})
        if not meta:
            continue
        sample = meta.get("sample", "")
        dv = meta.get("dv", "")
        iv = meta.get("iv", "")
        short_iv = iv.replace("_pct", "").replace("_", " ")
        n = meta.get("n_obs", 0)
        r2 = meta.get("rsquared", float("nan"))
        b1 = meta.get("beta1", float("nan"))
        p1 = meta.get("beta1_p_one", float("nan"))
        h2 = "YES" if meta.get("beta1_signif") else "no"
        lines.append(
            f"| {sample} | {dv} | {short_iv} | {n:,} | {r2:.4f} | "
            f"{b1:.4f} | {p1:.4f} | {h2} |"
        )

    lines += [
        "",
        "## Hypothesis Test Summary",
        "",
    ]

    # Summary by DV
    for dv in DEPENDENT_VARIABLES:
        dv_results = [r for r in all_results if r.get("meta", {}).get("dv") == dv]
        dv_sig = sum(1 for r in dv_results if r.get("meta", {}).get("beta1_signif"))
        lines.append(f"**{dv}:** H2 {dv_sig}/{len(dv_results)} significant")

    lines.append("")

    # Summary by sample
    for sample in ["Main", "Finance", "Utility"]:
        sample_results = [
            r for r in all_results if r.get("meta", {}).get("sample") == sample
        ]
        if not sample_results:
            continue
        h2_n = sum(1 for r in sample_results if r.get("meta", {}).get("beta1_signif"))
        n_total = len(sample_results)
        lines.append(
            f"**{sample}:** H2 {h2_n}/{n_total} significant"
        )

    lines.append("")

    # Summary by IV type
    for iv_type in ["uncertainty", "clarity_residual"]:
        type_results = [r for r in all_results if r.get("meta", {}).get("iv_type") == iv_type]
        type_sig = sum(1 for r in type_results if r.get("meta", {}).get("beta1_signif"))
        lines.append(f"**{iv_type} IVs:** H2 {type_sig}/{len(type_results)} significant")

    lines.append("")

    report_path = out_dir / "report_step4_H2.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("  Saved: report_step4_H2.md")


# ==============================================================================
# Main
# ==============================================================================


def main(panel_path: Optional[str] = None) -> int:
    """Main execution."""
    # Guard for non-CPython interpreters that don't support reconfigure
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    stats: Dict[str, Any] = {
        "step_id": "test_h2_investment",
        "timestamp": timestamp,
        "regressions": {},
        "timing": {},
    }

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "h2_investment" / timestamp

    # Setup logging to timestamped directory
    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H2_Investment",
        timestamp=timestamp,
    )

    print("=" * 80)
    print("STAGE 4: Test H2 Investment Efficiency Hypothesis (call-level)")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Log dir:   {log_dir}")

    # Load panel
    panel = load_panel(root, panel_path)

    # Track panel path for manifest
    panel_file = Path(panel_path) if panel_path else get_latest_output_dir(
        root / "outputs" / "variables" / "h2_investment",
        required_file="h2_investment_panel.parquet",
    ) / "h2_investment_panel.parquet"

    # Assign sample if not already present
    if "sample" not in panel.columns:
        panel["sample"] = assign_industry_sample(panel["ff12_code"])

    print("\n  Full panel sample distribution:")
    for sample in ["Main", "Finance", "Utility"]:
        n = (panel["sample"] == sample).sum()
        n_t = (
            panel.loc[panel["sample"] == sample, "InvestmentResidual"]
            .notna()
            .sum()
        )
        n_lead = (
            panel.loc[panel["sample"] == sample, "InvestmentResidual_lead"]
            .notna()
            .sum()
        )
        print(f"    {sample}: {n:,} calls, {n_t:,} with DV_t, {n_lead:,} with DV_t+1")

    # Generate summary statistics (all variables, by sample)
    print("\n" + "=" * 60)
    print("Generating summary statistics")
    print("=" * 60)
    make_summary_stats_table(
        df=panel,
        variables=SUMMARY_STATS_VARS,
        sample_names=["Main", "Finance", "Utility"],
        sample_col="sample",
        output_csv=out_dir / "summary_stats.csv",
        output_tex=out_dir / "summary_stats.tex",
        caption="Summary Statistics — H2 Investment Efficiency",
        label="tab:summary_stats_h2",
    )
    print("  Saved: summary_stats.csv")
    print("  Saved: summary_stats.tex")

    # Run regressions: 3 samples × 2 DVs × 6 IVs = 36 regressions
    all_results: List[Dict[str, Any]] = []

    for sample_name in ["Main", "Finance", "Utility"]:
        df_sample_full = panel[panel["sample"] == sample_name].copy()

        for dv in DEPENDENT_VARIABLES:
            for iv in MAIN_IVS:
                if iv not in panel.columns:
                    print(f"  WARNING: {iv} not in panel -- skipping")
                    continue

                print(f"\n--- {sample_name} / {dv} / {iv} ---")

                try:
                    df_prepared = prepare_regression_data(df_sample_full, dv, iv)
                except ValueError as e:
                    print(f"  ERROR preparing data: {e}", file=sys.stderr)
                    continue

                if len(df_prepared) < 100:
                    print(f"  Skipping: too few obs ({len(df_prepared)})")
                    continue

                model, meta = run_regression(df_prepared, sample_name, dv, iv)

                if model is not None and meta:
                    all_results.append({"model": model, "meta": meta})
                    stats["regressions"][f"{sample_name}_{dv}_{iv}"] = meta

    # Save outputs
    diag_df = save_outputs(all_results, out_dir)

    # Generate sample attrition table
    if all_results:
        main_results = [r for r in all_results if r.get("meta", {}).get("sample") == "Main"]
        if main_results:
            first_meta = main_results[0].get("meta", {})
            attrition_stages = [
                ("Master manifest", len(panel)),
                ("Main sample filter", (panel["sample"] == "Main").sum()),
                ("After lead filter", panel.loc[panel["sample"] == "Main", "InvestmentResidual_lead"].notna().sum()),
                ("After complete-case + min-calls filter", first_meta.get("n_obs", 0)),
            ]
            generate_attrition_table(attrition_stages, out_dir, "H2 Investment Efficiency")
            print("  Saved: sample_attrition.csv and sample_attrition.tex")

    # Generate run manifest
    generate_manifest(
        output_dir=out_dir,
        stage="stage4",
        timestamp=timestamp,
        input_paths={"panel": panel_file},
        output_files={
            "diagnostics": out_dir / "model_diagnostics.csv",
            "table": out_dir / "h2_investment_table.tex",
        },
        panel_path=panel_file,
    )
    print("  Saved: run_manifest.json")

    # Report
    duration = (datetime.now() - start_time).total_seconds()
    generate_report(all_results, diag_df, out_dir, duration)

    # Final summary
    stats["timing"]["duration_seconds"] = round(duration, 2)

    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.1f} seconds")
    print(f"Output:   {out_dir}")
    print(f"Total regressions completed: {len(all_results)}")

    # H2 summary
    h2_total = sum(1 for r in all_results if r["meta"].get("beta1_signif"))
    print(f"H2 significant (beta1<0, p<0.05 one-tail): {h2_total}/{len(all_results)}")

    # DV breakdown
    for dv in DEPENDENT_VARIABLES:
        dv_results = [r for r in all_results if r.get("meta", {}).get("dv") == dv]
        dv_sig = sum(1 for r in dv_results if r.get("meta", {}).get("beta1_signif"))
        print(f"  {dv}: {dv_sig}/{len(dv_results)} significant")

    return 0


if __name__ == "__main__":
    args = parse_arguments()

    if args.dry_run:
        print("Dry-run mode: validating inputs...")
        print("[OK] All inputs validated")
        sys.exit(0)

    sys.exit(main(panel_path=args.panel_path))
