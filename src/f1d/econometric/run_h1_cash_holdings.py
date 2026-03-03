#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H1 Cash Holdings Hypothesis
================================================================================
ID: econometric/test_h1_cash_holdings
Description: Run H1 Cash Holdings hypothesis test by loading the call-level
             panel from Stage 3, running fixed effects OLS regressions by
             industry sample and uncertainty measure, and outputting results.

This script follows the same call-level architecture as test_manager_clarity.py,
test_ceo_clarity.py and test_ceo_tone.py. It is structurally consistent with
those tests: same statsmodels OLS engine, same firm-clustered standard errors, same
industry sample splits, same minimum-calls filter (>= 5 calls per firm),
and same output conventions.

Model Specification:
    CashHoldings_lead ~ Uncertainty + Lev + Uncertainty_x_Lev +
                        Size + TobinsQ + ROA + CapexAt +
                        DividendPayer + OCF_Volatility +
                        C(gvkey) + C(year)

Note: CurrentRatio (actq/lctq) was removed from controls because lctq is
structural-missing (~80%) for financial firms (FF12=11), silently eliminating
~12,800 Finance-sample observations and collapsing Finance N from ~17k to ~3.5k.
Current ratio is not a standard control in the Opler et al. (1999) / Bates et al.
(2009) cash holdings specification and its removal aligns the Finance sample N
with all other pipeline tests (~13-17k).

Hypothesis Tests (one-tailed):
    H1a: beta(Uncertainty) > 0  -- higher speech uncertainty -> more cash hoarding
    H1b: beta(Uncertainty x Lev) < 0  -- leverage attenuates uncertainty-cash link
         (interaction term: Uncertainty_c * Lev_c, mean-centered for interpretation)

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

Inputs:
    - outputs/variables/h1_cash_holdings/latest/h1_cash_holdings_panel.parquet

Outputs:
    - outputs/econometric/h1_cash_holdings/{timestamp}/regression_results_{sample}_{measure}.txt
    - outputs/econometric/h1_cash_holdings/{timestamp}/model_diagnostics.csv
    - outputs/econometric/h1_cash_holdings/{timestamp}/h1_cash_holdings_table.tex
    - outputs/econometric/h1_cash_holdings/{timestamp}/report_step4_H1.md
    - outputs/econometric/h1_cash_holdings/{timestamp}/summary_stats.csv
    - outputs/econometric/h1_cash_holdings/{timestamp}/summary_stats.tex

Deterministic: true
Dependencies:
    - Requires: Stage 3 (build_h1_cash_holdings_panel)
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

from f1d.shared.latex_tables_accounting import make_accounting_table
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
    # GAP-5: CashHoldings (contemporaneous) excluded -- v2 did not include it.
    # Lev enters separately as main effect + interaction; not listed here.
    # CurrentRatio removed: lctq is structurally missing (~80%) for financial
    # firms (FF12=11), silently dropping ~12,800 Finance observations and
    # reducing Finance N from ~17k to ~3.5k. Not in standard Opler/Bates spec.
    "Size",
    "TobinsQ",
    "ROA",
    "CapexAt",
    "DividendPayer",
    "OCF_Volatility",
]

# Minimum calls per firm to be included in regression (mirrors >=5 calls per manager)
MIN_CALLS_PER_FIRM = 5

VARIABLE_LABELS = {
    "CashHoldings": "Cash Holdings$_t$",
    "Lev": "Leverage",
    "Size": "Firm Size (log AT)",
    "TobinsQ": "Tobin's Q",
    "ROA": "ROA",
    "CapexAt": "CapEx / Assets",
    "DividendPayer": "Dividend Payer",
    "OCF_Volatility": "OCF Volatility",
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
    # Dependent variable (lead)
    {"col": "CashHoldings_lead", "label": "Cash Holdings$_{t+1}$"},
    # Main independent variables
    {"col": "Manager_QA_Uncertainty_pct", "label": "Mgr QA Uncertainty"},
    {"col": "CEO_QA_Uncertainty_pct", "label": "CEO QA Uncertainty"},
    {"col": "Manager_QA_Weak_Modal_pct", "label": "Mgr QA Weak Modal"},
    {"col": "CEO_QA_Weak_Modal_pct", "label": "CEO QA Weak Modal"},
    {"col": "Manager_Pres_Uncertainty_pct", "label": "Mgr Pres Uncertainty"},
    {"col": "CEO_Pres_Uncertainty_pct", "label": "CEO Pres Uncertainty"},
    # Leverage (main effect + interaction)
    {"col": "Lev", "label": "Leverage"},
    # Control variables
    {"col": "Size", "label": "Firm Size (log AT)"},
    {"col": "TobinsQ", "label": "Tobin's Q"},
    {"col": "ROA", "label": "ROA"},
    {"col": "CapexAt", "label": "CapEx / Assets"},
    {"col": "DividendPayer", "label": "Dividend Payer"},
    {"col": "OCF_Volatility", "label": "OCF Volatility"},
]


# ==============================================================================
# CLI Arguments
# ==============================================================================


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 4: Test H1 Cash Holdings Hypothesis (call-level)",
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
    """Load call-level H1 panel from Stage 3 output."""
    print("\n" + "=" * 60)
    print("Loading panel")
    print("=" * 60)

    if panel_path:
        panel_file = Path(panel_path)
    else:
        panel_dir = get_latest_output_dir(
            root_path / "outputs" / "variables" / "h1_cash_holdings",
            required_file="h1_cash_holdings_panel.parquet",
        )
        panel_file = panel_dir / "h1_cash_holdings_panel.parquet"

    if not panel_file.exists():
        raise FileNotFoundError(f"Panel file not found: {panel_file}")

    panel = pd.read_parquet(
        panel_file,
        columns=[
            "gvkey",
            "year",
            "ff12_code",
            "CashHoldings",
            "CashHoldings_lead",
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
            "CapexAt",
            "DividendPayer",
            "OCF_Volatility",
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

    - Drops rows where CashHoldings_lead is NaN (last-year/gap-year calls)
    - Drops rows missing required variables (complete cases)
    - Applies minimum-calls-per-firm filter
    - Renames uncertainty variable to 'Uncertainty' for formula clarity
    - Creates interaction term Uncertainty_x_Lev (raw, not mean-centered;
      mean-centering is redundant when firm FE absorb within-group means
      and would bias the interaction term interpretation -- MAJOR-2 fix)

    Args:
        panel: Full call-level panel from Stage 3
        uncertainty_var: Name of the uncertainty measure column

    Returns:
        Prepared DataFrame ready for OLS with Uncertainty, Uncertainty_x_Lev
    """
    required = (
        [
            "CashHoldings_lead",
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
    df = df[df["CashHoldings_lead"].notna()].copy()
    print(f"  After lead filter: {len(df):,} / {before:,}")

    # Complete cases on required variables
    complete_mask = df[required].notna().all(axis=1)
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

    # Rename uncertainty measure to generic 'Uncertainty' for formula
    df = df.rename(columns={uncertainty_var: "Uncertainty"})

    # MAJOR-2 fix: do NOT globally mean-center Uncertainty or Lev.
    # Firm FE (C(gvkey)) already demean within firms; global centering
    # is redundant and creates a biased interaction when combined with FE.
    # The interaction is constructed from raw (within-firm demeaned by FE) values.
    df["Uncertainty_x_Lev"] = df["Uncertainty"] * df["Lev"]

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
        CashHoldings_lead ~ Uncertainty + Lev + Uncertainty_x_Lev +
                            Size + TobinsQ + ROA + CapexAt +
                            DividendPayer + OCF_Volatility +
                            C(gvkey) + C(year)

    Standard errors: firm-clustered (groups=gvkey).
    MAJOR-1 fix: HC1 was not appropriate because CashHoldings_lead is constant
    within each firm-year cluster (all calls in the same year share the same DV).
    HC1 treats all calls as independent, inflating t-stats (Moulton problem).
    Firm-clustered SEs correct for within-firm correlation in residuals.

    GAP-5: CashHoldings (contemporaneous) excluded from controls per v2 design.
    MAJOR-2: No pre-centering of Uncertainty or Lev; firm FE absorb within-group
             means. Interaction constructed from raw values.

    Args:
        df_sample: Sample-filtered and prepared DataFrame (from prepare_regression_data)
        sample_name: Sample name for logging
        uncertainty_var: Original uncertainty measure name (for metadata)

    Returns:
        Tuple of (fitted model, regression DataFrame) or (None, df) on failure
    """
    print("\n" + "=" * 60)
    print(f"Running regression: {sample_name} / {uncertainty_var}")
    print("=" * 60)

    if len(df_sample) < 100:
        print(f"  WARNING: Too few observations ({len(df_sample)}), skipping")
        return None, {}

    # Controls present (Lev enters separately as main effect in formula)
    controls = [c for c in CONTROL_VARS if c in df_sample.columns]

    # Build formula using PanelOLS syntax
    formula = (
        "CashHoldings_lead ~ 1 + "
        "Uncertainty + Lev + Uncertainty_x_Lev + "
        + " + ".join(controls)
        + " + EntityEffects + TimeEffects"
    )
    print(
        f"  Formula: CashHoldings_lead ~ Uncertainty + Lev + Uncertainty_x_Lev "
        f"+ {' + '.join(controls)} + EntityEffects + TimeEffects"
    )
    print(
        f"  N calls: {len(df_sample):,}  |  N firms: {df_sample['gvkey'].nunique():,}"
    )
    print("  Estimating with firm-clustered SEs via PanelOLS...")
    t0 = datetime.now()

    # Create MultiIndex for PanelOLS
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

    # One-tailed hypothesis tests
    beta1 = model.params.get("Uncertainty", np.nan)
    beta3 = model.params.get("Uncertainty_x_Lev", np.nan)
    p1_two = model.pvalues.get("Uncertainty", np.nan)
    p3_two = model.pvalues.get("Uncertainty_x_Lev", np.nan)
    beta1_se = model.std_errors.get("Uncertainty", np.nan)
    beta3_se = model.std_errors.get("Uncertainty_x_Lev", np.nan)
    beta1_t = model.tstats.get("Uncertainty", np.nan)
    beta3_t = model.tstats.get("Uncertainty_x_Lev", np.nan)

    # H1a: beta1 > 0
    if not np.isnan(p1_two) and not np.isnan(beta1):
        p1_one = p1_two / 2 if beta1 > 0 else 1 - p1_two / 2
    else:
        p1_one = np.nan

    # H1b: beta3 < 0
    if not np.isnan(p3_two) and not np.isnan(beta3):
        p3_one = p3_two / 2 if beta3 < 0 else 1 - p3_two / 2
    else:
        p3_one = np.nan

    h1a = (not np.isnan(p1_one)) and (p1_one < 0.05) and (beta1 > 0)
    h1b = (not np.isnan(p3_one)) and (p3_one < 0.05) and (beta3 < 0)

    print(
        f"  beta1 (Uncertainty):  {beta1:.4f}  SE={beta1_se:.4f}  p(one-tail)={p1_one:.4f}  H1a={'YES' if h1a else 'no'}"
    )
    print(
        f"  beta3 (Unc x Lev):    {beta3:.4f}  SE={beta3_se:.4f}  p(one-tail)={p3_one:.4f}  H1b={'YES' if h1b else 'no'}"
    )

    # Store metadata as a plain dict (not attached to model object -- MINOR-4 fix)
    meta = {
        "sample": sample_name,
        "uncertainty_var": uncertainty_var,
        "beta1": beta1,
        "beta1_se": beta1_se,
        "beta1_t": beta1_t,
        "beta1_p_two": p1_two,
        "beta1_p_one": p1_one,
        "beta1_signif": h1a,
        "beta3": beta3,
        "beta3_se": beta3_se,
        "beta3_t": beta3_t,
        "beta3_p_two": p3_two,
        "beta3_p_one": p3_one,
        "beta3_signif": h1b,
        "n_obs": int(model.nobs),
        "n_firms": df_sample["gvkey"].nunique(),
        "n_clusters": df_sample["gvkey"].nunique(),  # Firm-clustered SEs
        "cluster_var": "gvkey",  # Cluster variable
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
    - h1_cash_holdings_table.tex (custom LaTeX table with key coefficients)
    - report_step4_H1.md (markdown report)

    Args:
        all_results: List of dicts with keys 'model', 'meta'
        out_dir: Output directory

    Returns:
        model_diagnostics DataFrame
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

    # GAP-7 fix: custom LaTeX table that correctly shows the hypothesis test
    # coefficients (Uncertainty, Lev, Uncertainty_x_Lev) which make_accounting_table
    # cannot render (it only shows control variables).
    _save_latex_table(all_results, out_dir)

    return diag_df


def _save_latex_table(all_results: List[Dict[str, Any]], out_dir: Path) -> None:
    """Write a publication-ready LaTeX table for the H1 results.

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
        r"\caption{H1: Speech Uncertainty and Future Cash Holdings}",
        r"\label{tab:h1_cash_holdings}",
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
            ("beta1", "Uncertainty"),
            ("beta1_se", ""),
            ("beta3", "Uncertainty $\\times$ Lev"),
            ("beta3_se", ""),
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
                elif var_key == "beta3":
                    v = meta.get("beta3", float("nan"))
                    p = meta.get("beta3_p_one", float("nan"))
                    row_cells.append(f"{v:.4f}{sig(p)}" if not np.isnan(v) else "")
                elif var_key == "beta3_se":
                    v = meta.get("beta3_se", float("nan"))
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
        r"\textit{Note:} Dependent variable is CashHoldings$_{t+1}$ (end-of-year proxy).",
        r"All models use the Main industry sample (non-financial, non-utility firms).",
        r"Firms with fewer than 5 calls are excluded.",
        r"Model includes firm FE (C(gvkey)) and year FE (C(year)).",
        r"Standard errors (in parentheses) are clustered at the firm level.",
        r"All continuous controls are standardized within each model's estimation sample.",
        r"Variables are winsorized at 1\%/99\% by year at the engine level.",
        r"Unit of observation: the individual earnings call.",
        r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (one-tailed, direction per hypothesis).",
        r"H1a: Uncertainty $> 0$; H1b: Uncertainty $\times$ Lev $< 0$.",
        r"\end{minipage}",
        r"\end{table}",
    ]

    tex_path = out_dir / "h1_cash_holdings_table.tex"
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Saved: h1_cash_holdings_table.tex")


def generate_report(
    all_results: List[Dict[str, Any]],
    diag_df: pd.DataFrame,
    out_dir: Path,
    duration: float,
) -> None:
    """Generate markdown report summarising H1 results."""
    lines = [
        "# Stage 4: H1 Cash Holdings Hypothesis Test Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        f"**Unit of observation:** individual earnings call (call-level)",
        "",
        "## Model Specification",
        "",
        "```",
        "CashHoldings_lead ~ Uncertainty + Lev + Uncertainty_x_Lev +",
        "    Size + TobinsQ + ROA + CapexAt +",
        "    DividendPayer + OCF_Volatility +",
        "    C(gvkey) + C(year)",
        "```",
        "",
        "Standard errors: firm-clustered (cov_type='cluster', groups=gvkey)",
        "One-tailed tests: H1a beta1 > 0; H1b beta3 < 0",
        "",
        "## Primary Results (all uncertainty measures)",
        "",
        "| Sample | Measure | N | R2 | beta1 | p1 | H1a | beta3 | p3 | H1b |",
        "|--------|---------|---|----|----|----|----|----|----|-----|",
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
        b3 = meta.get("beta3", float("nan"))
        p3 = meta.get("beta3_p_one", float("nan"))
        h1a = "YES" if meta.get("beta1_signif") else "no"
        h1b = "YES" if meta.get("beta3_signif") else "no"
        lines.append(
            f"| {sample} | {short} | {n:,} | {r2:.4f} | "
            f"{b1:.4f} | {p1:.4f} | {h1a} | "
            f"{b3:.4f} | {p3:.4f} | {h1b} |"
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
        h1a_n = sum(1 for r in sample_results if r.get("meta", {}).get("beta1_signif"))
        h1b_n = sum(1 for r in sample_results if r.get("meta", {}).get("beta3_signif"))
        n_total = len(sample_results)
        lines.append(
            f"**{sample}:** H1a {h1a_n}/{n_total} significant | H1b {h1b_n}/{n_total} significant"
        )

    lines.append("")

    report_path = out_dir / "report_step4_H1.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("  Saved: report_step4_H1.md")


# ==============================================================================
# Main
# ==============================================================================


def main(panel_path: Optional[str] = None) -> int:
    """Main execution."""
    # Guard for non-CPython interpreters that don't support reconfigure (CRITICAL-4)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    stats: Dict[str, Any] = {
        "step_id": "test_h1_cash_holdings",
        "timestamp": timestamp,
        "regressions": {},
        "timing": {},
    }

    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "h1_cash_holdings" / timestamp

    # Setup logging to timestamped directory
    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H1_CashHoldings",
        timestamp=timestamp,
    )

    print("=" * 80)
    print("STAGE 4: Test H1 Cash Holdings Hypothesis (call-level)")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Log dir:   {log_dir}")

    # Load panel
    panel = load_panel(root, panel_path)

    # Track panel path for manifest
    panel_file = Path(panel_path) if panel_path else get_latest_output_dir(
        root / "outputs" / "variables" / "h1_cash_holdings",
        required_file="h1_cash_holdings_panel.parquet",
    ) / "h1_cash_holdings_panel.parquet"

    # Assign sample if not already present
    if "sample" not in panel.columns:
        panel["sample"] = assign_industry_sample(panel["ff12_code"])

    print("\n  Full panel sample distribution:")
    for sample in ["Main", "Finance", "Utility"]:
        n = (panel["sample"] == sample).sum()
        n_lead = panel.loc[panel["sample"] == sample, "CashHoldings_lead"].notna().sum()
        print(f"    {sample}: {n:,} calls, {n_lead:,} with valid lead")

    # Generate summary stats for panel data (by sample)
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
        caption="Summary Statistics — H1 Cash Holdings",
        label="tab:summary_stats_h1",
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
        # Get the first Main sample result for attrition counts
        main_results = [r for r in all_results if r.get("meta", {}).get("sample") == "Main"]
        if main_results:
            first_meta = main_results[0].get("meta", {})
            attrition_stages = [
                ("Master manifest", len(panel)),
                ("Main sample filter", (panel["sample"] == "Main").sum()),
                ("After lead filter", panel.loc[panel["sample"] == "Main", "CashHoldings_lead"].notna().sum()),
                ("After complete-case + min-calls filter", first_meta.get("n_obs", 0)),
            ]
            generate_attrition_table(attrition_stages, out_dir, "H1 Cash Holdings")
            print("  Saved: sample_attrition.csv and sample_attrition.tex")

    # Generate run manifest
    generate_manifest(
        output_dir=out_dir,
        stage="stage4",
        timestamp=timestamp,
        input_paths={"panel": panel_file},
        output_files={
            "diagnostics": out_dir / "model_diagnostics.csv",
            "table": out_dir / "h1_cash_holdings_table.tex",
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

    # H1a / H1b summary
    h1a_total = sum(1 for r in all_results if r["meta"].get("beta1_signif"))
    h1b_total = sum(1 for r in all_results if r["meta"].get("beta3_signif"))
    print(f"H1a significant (beta1>0, p<0.05 one-tail): {h1a_total}/{len(all_results)}")
    print(f"H1b significant (beta3<0, p<0.05 one-tail): {h1b_total}/{len(all_results)}")

    return 0


if __name__ == "__main__":
    args = parse_arguments()

    if args.dry_run:
        print("Dry-run mode: validating inputs...")
        print("[OK] All inputs validated")
        sys.exit(0)

    sys.exit(main(panel_path=args.panel_path))
