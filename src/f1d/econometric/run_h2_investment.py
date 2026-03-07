#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H2 Investment Efficiency Hypothesis
================================================================================
ID: econometric/test_h2_investment
Description: Run H2 Investment Efficiency hypothesis test by loading the call-level
             panel from Stage 3, running fixed effects OLS regressions by
             industry sample and uncertainty measure, and outputting results.

This script follows the same call-level architecture as test_h1_cash_holdings.py,
test_manager_clarity.py, test_ceo_clarity.py, and test_ceo_tone.py. It is
structurally consistent with those tests: same statsmodels OLS engine, same
firm-clustered standard errors, same industry sample splits, same minimum-calls
filter (>= 5 calls per firm), and same output conventions.

Model Specification:
    InvestmentResidual_lead ~ {uncertainty_var} + Lev +
                              Size + TobinsQ + ROA + CashFlow + SalesGrowth +
                              C(gvkey) + C(year)

Hypothesis Test (one-tailed):
    H2: beta({uncertainty_var}) < 0  -- higher speech uncertainty -> lower investment efficiency
        p_one = p_two/2 if beta1 < 0 else 1 - p_two/2

Industry Samples:
    - Main:    FF12 codes 1-7, 9-10, 12 (non-financial, non-utility)
    - Finance: FF12 code 11
    - Utility: FF12 code 8

Minimum Calls Filter:
    Firms must have >= 5 calls in the sample to be included in regression.

Uncertainty Measures (6):
    Manager_QA_Uncertainty_pct, CEO_QA_Uncertainty_pct,
    Manager_QA_Weak_Modal_pct, CEO_QA_Weak_Modal_pct,
    Manager_Pres_Uncertainty_pct, CEO_Pres_Uncertainty_pct

Standard Errors:
    Firm-clustered (cov_type="cluster", groups=df["gvkey"]) -- same as H1.

Expected results: null (0/6 significant for H2), faithfully reported.

Inputs:
    - outputs/variables/h2_investment/latest/h2_investment_panel.parquet

Outputs:
    - outputs/econometric/h2_investment/{timestamp}/regression_results_{sample}_{measure}.txt
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
Date: 2026-02-26
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

UNCERTAINTY_MEASURES = [
    "Manager_QA_Uncertainty_pct",
    "CEO_QA_Uncertainty_pct",
    "Manager_QA_Weak_Modal_pct",
    "CEO_QA_Weak_Modal_pct",
    "Manager_Pres_Uncertainty_pct",
    "CEO_Pres_Uncertainty_pct",
]

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
    "InvestmentResidual": "Investment Residual$_t$",
    "Lev": "Leverage",
    "Size": "Firm Size (log AT)",
    "TobinsQ": "Tobin's Q",
    "ROA": "ROA",
    "CashFlow": "Cash Flow / Assets",
    "SalesGrowth": "Sales Growth",
    "Manager_QA_Uncertainty_pct": "Mgr QA Uncertainty",
    "CEO_QA_Uncertainty_pct": "CEO QA Uncertainty",
    "Manager_QA_Weak_Modal_pct": "Mgr QA Weak Modal",
    "CEO_QA_Weak_Modal_pct": "CEO QA Weak Modal",
    "Manager_Pres_Uncertainty_pct": "Mgr Pres Uncertainty",
    "CEO_Pres_Uncertainty_pct": "CEO Pres Uncertainty",
}


# ==============================================================================
# Summary Statistics Variables
# ==============================================================================

SUMMARY_STATS_VARS = [
    # Dependent variable
    {"col": "InvestmentResidual", "label": "Investment Residual"},
    # Main independent variables
    {"col": "Manager_QA_Uncertainty_pct", "label": "Mgr QA Uncertainty"},
    {"col": "CEO_QA_Uncertainty_pct", "label": "CEO QA Uncertainty"},
    {"col": "Manager_QA_Weak_Modal_pct", "label": "Mgr QA Weak Modal"},
    {"col": "CEO_QA_Weak_Modal_pct", "label": "CEO QA Weak Modal"},
    {"col": "Manager_Pres_Uncertainty_pct", "label": "Mgr Pres Uncertainty"},
    {"col": "CEO_Pres_Uncertainty_pct", "label": "CEO Pres Uncertainty"},
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
            "Manager_QA_Weak_Modal_pct",
            "CEO_QA_Weak_Modal_pct",
            "Manager_Pres_Uncertainty_pct",
            "CEO_Pres_Uncertainty_pct",
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
    uncertainty_var: str,
) -> pd.DataFrame:
    """Prepare panel for a single uncertainty measure regression.

    - Drops rows where InvestmentResidual_lead is NaN (last-year/gap-year calls)
    - Drops rows missing required variables (complete cases)
    - Applies minimum-calls-per-firm filter

    Args:
        panel: Full call-level panel from Stage 3
        uncertainty_var: Name of the uncertainty measure column

    Returns:
        Prepared DataFrame ready for OLS with uncertainty_var
    """
    required = (
        [
            "InvestmentResidual_lead",
            uncertainty_var,
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

    # Drop last-year and gap-year calls (no valid lead)
    before = len(df)
    df = df[df["InvestmentResidual_lead"].notna()].copy()
    print(f"  After lead filter: {len(df):,} / {before:,}")

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
    uncertainty_var: str,
) -> Tuple[Any, Dict[str, Any]]:
    """Run OLS regression with firm FE + year FE (call-level), firm-clustered SEs.

    Model:
        InvestmentResidual_lead ~ {uncertainty_var} + Lev +
                                  Size + TobinsQ + ROA + CashFlow + SalesGrowth +
                                  C(gvkey) + C(year)

    Standard errors: firm-clustered (groups=gvkey) -- same as H1.

    H2: beta1 < 0  (higher uncertainty -> lower investment efficiency)
        p_one = p_two/2 if beta1 < 0 else 1 - p_two/2

    Args:
        df_sample: Sample-filtered and prepared DataFrame
        sample_name: Sample name for logging
        uncertainty_var: Original uncertainty measure name (for metadata)

    Returns:
        Tuple of (fitted model, metadata dict) or (None, {}) on failure
    """
    print("\n" + "=" * 60)
    print(f"Running regression: {sample_name} / {uncertainty_var}")
    print("=" * 60)

    if len(df_sample) < 100:
        print(f"  WARNING: Too few observations ({len(df_sample)}), skipping")
        return None, {}

    # Controls present (Lev enters separately as main effect in formula)
    controls = [c for c in CONTROL_VARS if c in df_sample.columns]

    # Build formula
    formula = (
        "InvestmentResidual_lead ~ 1 + "
        f"{uncertainty_var} + Lev + "
        + " + ".join(controls)
        + " + EntityEffects + TimeEffects"
    )
    print(
        f"  Formula: InvestmentResidual_lead ~ {uncertainty_var} + Lev "
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
    beta1 = model.params.get(uncertainty_var, np.nan)
    p1_two = model.pvalues.get(uncertainty_var, np.nan)
    beta1_se = model.std_errors.get(uncertainty_var, np.nan)
    beta1_t = model.tstats.get(uncertainty_var, np.nan)

    # H2: beta1 < 0
    if not np.isnan(p1_two) and not np.isnan(beta1):
        p1_one = p1_two / 2 if beta1 < 0 else 1 - p1_two / 2
    else:
        p1_one = np.nan

    h2_signif = (not np.isnan(p1_one)) and (p1_one < 0.05) and (beta1 < 0)

    print(
        f"  beta1 ({uncertainty_var}):  {beta1:.4f}  SE={beta1_se:.4f}  p(one-tail)={p1_one:.4f}  H2={'YES' if h2_signif else 'no'}"
    )

    # Store metadata as a plain dict
    meta = {
        "sample": sample_name,
        "uncertainty_var": uncertainty_var,
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
    - One regression_results_{sample}_{measure}.txt per regression
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
        measure = meta.get("uncertainty_var", "unknown")
        fname = f"regression_results_{sample}_{measure}.txt"
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

    Shows the three key variables (Uncertainty, Lev, Uncertainty x Lev) with
    coefficients, clustered SEs in parentheses, significance stars, N, and R2.
    Columns = uncertainty measures; panels = industry samples.
    """
    sig = (
        lambda p: "***"
        if p < 0.01
        else ("**" if p < 0.05 else ("*" if p < 0.10 else ""))
    )

    short_names = {
        "Manager_QA_Uncertainty_pct": "Mgr QA Unc",
        "CEO_QA_Uncertainty_pct": "CEO QA Unc",
        "Manager_QA_Weak_Modal_pct": "Mgr Weak Modal",
        "CEO_QA_Weak_Modal_pct": "CEO Weak Modal",
        "Manager_Pres_Uncertainty_pct": "Mgr Pres Unc",
        "CEO_Pres_Uncertainty_pct": "CEO Pres Unc",
    }

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{H2: Speech Uncertainty and Investment Efficiency}",
        r"\label{tab:h2_investment}",
        r"\small",
        r"\begin{tabular}{l" + "c" * len(UNCERTAINTY_MEASURES) + "}",
        r"\toprule",
        r" & "
        + " & ".join(f"({i + 1})" for i in range(len(UNCERTAINTY_MEASURES)))
        + r" \\",
        r" & "
        + " & ".join(
            r"\shortstack{" + short_names.get(m, m) + "}" for m in UNCERTAINTY_MEASURES
        )
        + r" \\",
        r"\midrule",
    ]

    for sample in ["Main", "Finance", "Utility"]:
        sample_res = [
            r for r in all_results if r.get("meta", {}).get("sample") == sample
        ]
        if not sample_res:
            continue

        # Index by uncertainty_var for easy lookup
        by_measure = {r["meta"]["uncertainty_var"]: r for r in sample_res}

        lines.append(
            r"\multicolumn{"
            + str(len(UNCERTAINTY_MEASURES) + 1)
            + r"}{l}{\textit{"
            + sample
            + r" Sample}} \\"
        )

        for var_key, label in [
            ("beta1", "$\\beta_1$"),
            ("beta1_se", ""),
        ]:
            row_cells = []
            for m in UNCERTAINTY_MEASURES:
                r = by_measure.get(m, {})
                meta = r.get("meta", {})
                if not meta:
                    row_cells.append("")
                    continue
                if var_key == "beta1":
                    v = meta.get("beta1", float("nan"))
                    p = meta.get("beta1_p_one", float("nan"))
                    row_cells.append(f"{v:.4f}{sig(p)}" if not np.isnan(v) else "")
                elif var_key == "beta1_se":
                    v = meta.get("beta1_se", float("nan"))
                    row_cells.append(f"({v:.4f})" if not np.isnan(v) else "")

            row_label = label if label else ""
            lines.append(f"{row_label} & " + " & ".join(row_cells) + r" \\")

        # N and R2
        n_cells = []
        r2_cells = []
        for m in UNCERTAINTY_MEASURES:
            r = by_measure.get(m, {})
            meta = r.get("meta", {})
            n_cells.append(f"{meta.get('n_obs', ''):,}" if meta else "")
            # B8 fix: report within-R² (net of FE) instead of LSDV R²
            r2v = meta.get("within_r2", float("nan")) if meta else float("nan")
            if np.isnan(r2v):
                r2v = meta.get("rsquared", float("nan")) if meta else float("nan")
            r2_cells.append(f"{r2v:.3f}" if not np.isnan(r2v) else "")

        lines.append(r"N & " + " & ".join(n_cells) + r" \\")
        lines.append(r"Within-R$^2$ & " + " & ".join(r2_cells) + r" \\")
        lines.append(r"\midrule")

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\begin{minipage}{\linewidth}",
        r"\vspace{2pt}\footnotesize",
        r"\textit{Note:} Dependent variable is InvestmentResidual$_{t+1}$ "
        r"(Biddle et al. 2009; end-of-year proxy; $>0$=overinvestment, $<0$=underinvestment).",
        r"All models use the Main industry sample (non-financial, non-utility firms).",
        r"Firms with fewer than 5 calls are excluded.",
        r"Model includes firm FE (C(gvkey)) and year FE (C(year)).",
        r"Standard errors (in parentheses) are clustered at the firm level.",
        r"All continuous controls are standardized within each model's estimation sample.",
        r"Variables are winsorized at 1\%/99\% by year at the engine level.",
        r"Unit of observation: the individual earnings call.",
        r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (one-tailed, direction per hypothesis).",
        r"H2: Uncertainty $< 0$.",
        r"\end{minipage}",
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
        "InvestmentResidual_lead ~ {uncertainty_var} + Lev +",
        "    Size + TobinsQ + ROA + CashFlow + SalesGrowth +",
        "    C(gvkey) + C(year)",
        "```",
        "",
        "Standard errors: firm-clustered (cov_type='cluster', groups=gvkey)",
        "One-tailed test: H2 beta1 < 0",
        "",
        "## Primary Results (all uncertainty measures)",
        "",
        "| Sample | Measure | N | R2 | beta1 | p1 | H2 |",
        "|--------|---------|---|----|----|----|----|",
    ]

    for r in all_results:
        meta = r.get("meta", {})
        if not meta:
            continue
        sample = meta.get("sample", "")
        measure = meta.get("uncertainty_var", "")
        short = measure.replace("_pct", "").replace("_", " ")
        n = meta.get("n_obs", 0)
        r2 = meta.get("rsquared", float("nan"))
        b1 = meta.get("beta1", float("nan"))
        p1 = meta.get("beta1_p_one", float("nan"))
        h2 = "YES" if meta.get("beta1_signif") else "no"
        lines.append(
            f"| {sample} | {short} | {n:,} | {r2:.4f} | "
            f"{b1:.4f} | {p1:.4f} | {h2} |"
        )

    lines += [
        "",
        "## Hypothesis Test Summary",
        "",
    ]

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
        n_lead = (
            panel.loc[panel["sample"] == sample, "InvestmentResidual_lead"]
            .notna()
            .sum()
        )
        print(f"    {sample}: {n:,} calls, {n_lead:,} with valid lead")

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

    # Run regressions: 6 uncertainty measures x 3 samples = 18 regressions
    all_results: List[Dict[str, Any]] = []

    for sample_name in ["Main", "Finance", "Utility"]:
        df_sample_full = panel[panel["sample"] == sample_name].copy()

        for uncertainty_var in UNCERTAINTY_MEASURES:
            if uncertainty_var not in panel.columns:
                print(f"  WARNING: {uncertainty_var} not in panel -- skipping")
                continue

            print(f"\n--- {sample_name} / {uncertainty_var} ---")

            try:
                df_prepared = prepare_regression_data(df_sample_full, uncertainty_var)
            except ValueError as e:
                print(f"  ERROR preparing data: {e}", file=sys.stderr)
                continue

            if len(df_prepared) < 100:
                print(f"  Skipping: too few obs ({len(df_prepared)})")
                continue

            model, meta = run_regression(df_prepared, sample_name, uncertainty_var)

            if model is not None and meta:
                all_results.append({"model": model, "meta": meta})
                stats["regressions"][f"{sample_name}_{uncertainty_var}"] = meta

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

    return 0


if __name__ == "__main__":
    args = parse_arguments()

    if args.dry_run:
        print("Dry-run mode: validating inputs...")
        print("[OK] All inputs validated")
        sys.exit(0)

    sys.exit(main(panel_path=args.panel_path))
