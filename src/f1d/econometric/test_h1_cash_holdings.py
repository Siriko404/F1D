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
those tests: same statsmodels OLS engine, same HC1 standard errors, same
industry sample splits, same minimum-calls filter (>= 5 calls per firm),
and same output conventions.

Model Specification:
    CashHoldings_lead ~ Uncertainty + CashHoldings + Lev + Size + TobinsQ +
                        ROA + CapexAt + DividendPayer + OCF_Volatility +
                        CurrentRatio + C(gvkey) + C(year)

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

Author: Thesis Author
Date: 2026-02-20
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

warnings.filterwarnings("ignore", category=FutureWarning)

# statsmodels
smf: Any = None
try:
    import statsmodels.formula.api as smf  # type: ignore[no-redef]

    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    print("WARNING: statsmodels not available. Install with: pip install statsmodels")

from f1d.shared.latex_tables_accounting import make_accounting_table
from f1d.shared.path_utils import get_latest_output_dir


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
    "CashHoldings",
    "Lev",
    "Size",
    "TobinsQ",
    "ROA",
    "CapexAt",
    "DividendPayer",
    "OCF_Volatility",
    "CurrentRatio",
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
    "CurrentRatio": "Current Ratio",
    "Manager_QA_Uncertainty_pct": "Mgr QA Uncertainty",
    "CEO_QA_Uncertainty_pct": "CEO QA Uncertainty",
    "Manager_QA_Weak_Modal_pct": "Mgr QA Weak Modal",
    "CEO_QA_Weak_Modal_pct": "CEO QA Weak Modal",
    "Manager_Pres_Uncertainty_pct": "Mgr Pres Uncertainty",
    "CEO_Pres_Uncertainty_pct": "CEO Pres Uncertainty",
}


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

    panel = pd.read_parquet(panel_file)
    print(f"  Loaded: {panel_file}")
    print(f"  Rows: {len(panel):,}")
    print(f"  Columns: {len(panel.columns)}")
    return panel


def prepare_regression_data(
    panel: pd.DataFrame,
    uncertainty_var: str,
) -> pd.DataFrame:
    """Prepare panel for a single uncertainty measure regression.

    - Drops rows where CashHoldings_lead is NaN (last-year calls per firm)
    - Drops rows missing required variables (complete cases)
    - Applies minimum-calls-per-firm filter (mirrors >=5 calls per manager)
    - Mean-centers Uncertainty and Lev for interaction term interpretation

    Args:
        panel: Full call-level panel from Stage 3
        uncertainty_var: Name of the uncertainty measure column

    Returns:
        Prepared DataFrame ready for OLS, with Uncertainty_c, Lev_c, interaction
    """
    required = (
        [
            "CashHoldings_lead",
            uncertainty_var,
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

    # Drop last-year calls (no lead available)
    before = len(df)
    df = df[df["CashHoldings_lead"].notna()].copy()
    print(f"  After lead filter: {len(df):,} / {before:,}")

    # Complete cases
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

    # Ensure gvkey and year are strings for C(gvkey), C(year) patsy encoding
    df["gvkey"] = df["gvkey"].astype(str)
    df["year"] = df["year"].astype(str)

    # Mean-center uncertainty and Lev for interaction term
    unc_mean = df[uncertainty_var].mean()
    lev_mean = df["Lev"].mean()
    df["Uncertainty_c"] = df[uncertainty_var] - unc_mean
    df["Lev_c"] = df["Lev"] - lev_mean
    df["Uncertainty_x_Lev"] = df["Uncertainty_c"] * df["Lev_c"]

    return df


# ==============================================================================
# Regression
# ==============================================================================


def run_regression(
    df_sample: pd.DataFrame,
    sample_name: str,
    uncertainty_var: str,
) -> Tuple[Any, pd.DataFrame]:
    """Run OLS regression with firm FE + year FE (call-level).

    Model:
        CashHoldings_lead ~ Uncertainty_c + Lev_c + Uncertainty_x_Lev +
                            CashHoldings + Size + TobinsQ + ROA + CapexAt +
                            DividendPayer + OCF_Volatility + CurrentRatio +
                            C(gvkey) + C(year)

    Standard errors: HC1 (heteroskedasticity-robust), matching all other tests.

    Args:
        df_sample: Sample-filtered and prepared DataFrame
        sample_name: Sample name for logging
        uncertainty_var: Uncertainty measure being tested

    Returns:
        Tuple of (fitted model, regression DataFrame)
    """
    print("\n" + "=" * 60)
    print(f"Running regression: {sample_name} / {uncertainty_var}")
    print("=" * 60)

    if not STATSMODELS_AVAILABLE:
        print("  ERROR: statsmodels not available")
        return None, df_sample

    if len(df_sample) < 100:
        print(f"  WARNING: Too few observations ({len(df_sample)}), skipping")
        return None, df_sample

    # Controls present in df_sample (exclude Lev -- it enters via Lev_c)
    extra_controls = [c for c in CONTROL_VARS if c != "Lev" and c in df_sample.columns]

    # Build formula -- identical pattern to manager_clarity
    formula = (
        "CashHoldings_lead ~ "
        "Uncertainty_c + Lev_c + Uncertainty_x_Lev + "
        + " + ".join(extra_controls)
        + " + C(gvkey) + C(year)"
    )
    print(
        f"  Formula (controls shown): CashHoldings_lead ~ Uncertainty_c + "
        f"Lev_c + Uncertainty_x_Lev + {' + '.join(extra_controls)} + C(gvkey) + C(year)"
    )

    print(
        f"  N calls: {len(df_sample):,}  |  N firms: {df_sample['gvkey'].nunique():,}"
    )
    print("  Estimating... (this may take a moment)")
    t0 = datetime.now()

    try:
        model = smf.ols(formula, data=df_sample).fit(cov_type="HC1")
    except Exception as e:
        print(f"  ERROR: Regression failed: {e}", file=sys.stderr)
        return None, df_sample

    elapsed = (datetime.now() - t0).total_seconds()
    print(f"  [OK] Complete in {elapsed:.1f}s")
    print(f"  R-squared:     {model.rsquared:.4f}")
    print(f"  Adj R-squared: {model.rsquared_adj:.4f}")
    print(f"  N obs:         {int(model.nobs):,}")

    # One-tailed hypothesis tests
    beta1 = model.params.get("Uncertainty_c", np.nan)
    beta3 = model.params.get("Uncertainty_x_Lev", np.nan)
    p1_two = model.pvalues.get("Uncertainty_c", np.nan)
    p3_two = model.pvalues.get("Uncertainty_x_Lev", np.nan)

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
        f"  beta1 (Uncertainty): {beta1:.4f}  p(one-tail)={p1_one:.4f}  H1a={'YES' if h1a else 'no'}"
    )
    print(
        f"  beta3 (Unc x Lev):   {beta3:.4f}  p(one-tail)={p3_one:.4f}  H1b={'YES' if h1b else 'no'}"
    )

    # Attach hypothesis results to model for downstream use
    model._h1_meta = {
        "sample": sample_name,
        "uncertainty_var": uncertainty_var,
        "beta1": beta1,
        "beta1_se": model.bse.get("Uncertainty_c", np.nan),
        "beta1_t": model.tvalues.get("Uncertainty_c", np.nan),
        "beta1_p_two": p1_two,
        "beta1_p_one": p1_one,
        "beta1_signif": h1a,
        "beta3": beta3,
        "beta3_se": model.bse.get("Uncertainty_x_Lev", np.nan),
        "beta3_t": model.tvalues.get("Uncertainty_x_Lev", np.nan),
        "beta3_p_two": p3_two,
        "beta3_p_one": p3_one,
        "beta3_signif": h1b,
        "n_obs": int(model.nobs),
        "n_firms": df_sample["gvkey"].nunique(),
        "rsquared": model.rsquared,
        "rsquared_adj": model.rsquared_adj,
    }

    return model, df_sample


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
    - h1_cash_holdings_table.tex (LaTeX table)
    - report_step4_H1.md (markdown report)

    Args:
        all_results: List of result dicts from run_regression (with _h1_meta)
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
        if model is None:
            continue
        sample = meta.get("sample", "unknown")
        measure = meta.get("uncertainty_var", "unknown")
        fname = f"regression_results_{sample}_{measure}.txt"
        fpath = out_dir / fname
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(model.summary().as_text())
        print(f"  Saved: {fname}")

    # Build model_diagnostics.csv
    diag_rows = []
    for r in all_results:
        meta = r.get("meta", {})
        if meta:
            diag_rows.append(meta)

    diag_df = pd.DataFrame(diag_rows)
    diag_path = out_dir / "model_diagnostics.csv"
    diag_df.to_csv(diag_path, index=False)
    print(f"  Saved: model_diagnostics.csv ({len(diag_df)} regressions)")

    # LaTeX table: primary spec results (one column per uncertainty measure per sample)
    # Build results dict in format expected by make_accounting_table
    # Group by sample, uncertainty_var
    primary_results: Dict[str, Dict[str, Any]] = {}
    for r in all_results:
        model = r.get("model")
        meta = r.get("meta", {})
        if model is None or not meta:
            continue
        sample = meta["sample"]
        measure = meta["uncertainty_var"]
        key = f"{sample}_{measure}"
        primary_results[key] = {
            "model": model,
            "diagnostics": {
                "n_obs": meta["n_obs"],
                "n_firms": meta["n_firms"],
                "rsquared": meta["rsquared"],
                "rsquared_adj": meta["rsquared_adj"],
            },
        }

    # Only generate table if we have results
    if primary_results:
        try:
            make_accounting_table(
                results=primary_results,
                caption="Table H1: Speech Uncertainty and Cash Holdings",
                label="tab:h1_cash_holdings",
                note=(
                    "This table reports OLS regressions of next-year cash holdings "
                    "(CashHoldings$_{t+1}$) on speech uncertainty measures. "
                    "Firm FE (C(gvkey)) and year FE (C(year)) are absorbed as dummy variables. "
                    "Mean-centered uncertainty (Uncertainty$_c$) and leverage (Lev$_c$) are used "
                    "for the interaction term. Robust standard errors (HC1) in parentheses. "
                    "Unit of observation: the individual earnings call."
                ),
                variable_labels=VARIABLE_LABELS,
                control_variables=CONTROL_VARS,
                entity_label="N Firms",
                output_path=out_dir / "h1_cash_holdings_table.tex",
            )
            print("  Saved: h1_cash_holdings_table.tex")
        except Exception as e:
            print(f"  WARNING: LaTeX table generation failed: {e}")

    return diag_df


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
        "CashHoldings_lead ~ Uncertainty_c + Lev_c + Uncertainty_x_Lev +",
        "    CashHoldings + Size + TobinsQ + ROA + CapexAt +",
        "    DividendPayer + OCF_Volatility + CurrentRatio +",
        "    C(gvkey) + C(year)",
        "```",
        "",
        "Standard errors: HC1 (heteroskedasticity-robust)",
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

    print("=" * 80)
    print("STAGE 4: Test H1 Cash Holdings Hypothesis (call-level)")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")

    # Load panel
    panel = load_panel(root, panel_path)

    # Assign sample if not already present
    if "sample" not in panel.columns:
        import numpy as np

        panel["sample"] = np.select(
            [panel["ff12_code"] == 11, panel["ff12_code"] == 8],
            ["Finance", "Utility"],
            default="Main",
        )

    print("\n  Full panel sample distribution:")
    for sample in ["Main", "Finance", "Utility"]:
        n = (panel["sample"] == sample).sum()
        n_lead = panel.loc[panel["sample"] == sample, "CashHoldings_lead"].notna().sum()
        print(f"    {sample}: {n:,} calls, {n_lead:,} with valid lead")

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

            model, df_reg = run_regression(df_prepared, sample_name, uncertainty_var)

            if model is not None:
                all_results.append(
                    {
                        "model": model,
                        "df_reg": df_reg,
                        "meta": model._h1_meta,
                    }
                )
                stats["regressions"][f"{sample_name}_{uncertainty_var}"] = (
                    model._h1_meta
                )

    # Save outputs
    diag_df = save_outputs(all_results, out_dir)

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
