#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H13.2 Future Employment Growth Hypothesis
================================================================================
ID: econometric/run_h13_2_employment
Description: Run H13.2 Future Employment Growth hypothesis test by loading the
             firm-year panel from Stage 3, running fixed effects OLS regressions
             by industry sample, and outputting results.

This script follows the H12 architecture (firm-year level).
Firm-year panel with firm + year fixed effects, firm-clustered standard errors.

Model Specification (H13.2):
    EmploymentGrowth_lead ~ Avg_CEO_Pres_Uncertainty_pct +
                          Size + TobinsQ + ROA + Lev + CashHoldings +
                          DividendPayer + OCF_Volatility +
                          C(gvkey) + C(fyearq)

Note: NO CapexAt in H13.2 controls (unlike H13.1).

Hypothesis Test (one-tailed):
    H13.2: beta(Avg_CEO_Pres_Uncertainty_pct) < 0
           Higher speech uncertainty -> lower future employment growth

Industry Samples:
    - Main:    FF12 codes 1-7, 9-10, 12 (non-financial, non-utility)
    - Finance: FF12 code 11
    - Utility: FF12 code 8

Minimum Firm-Years Filter:
    Firms must have >= 5 firm-year observations to be included in regression.

Inputs:
    - outputs/variables/h13_2_employment/latest/h13_2_employment_panel.parquet

Outputs:
    - outputs/econometric/h13_2_employment/{timestamp}/regression_results_{sample}.txt
    - outputs/econometric/h13_2_employment/{timestamp}/model_diagnostics.csv
    - outputs/econometric/h13_2_employment/{timestamp}/h13_2_employment_table.tex
    - outputs/econometric/h13_2_employment/{timestamp}/report_step4_H13_2.md

Author: Thesis Author
Date: 2026-03-06
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

# Single IV (averaged CEO Presentation Uncertainty)
PRIMARY_IV = "Avg_CEO_Pres_Uncertainty_pct"

CONTROL_VARS = [
    "Size",
    "TobinsQ",
    "ROA",
    "Lev",
    "CashHoldings",
    "DividendPayer",
    "OCF_Volatility",
    # Note: NO CapexAt in H13.2 controls
]

# Minimum firm-years per firm to be included in regression
MIN_FIRM_YEARS = 5

VARIABLE_LABELS = {
    "EmploymentGrowth_lead": "Employment Growth$_{t+1}$",
    "Avg_CEO_Pres_Uncertainty_pct": "Avg CEO Pres Uncertainty",
    "Lev": "Leverage",
    "Size": "Firm Size (log AT)",
    "TobinsQ": "Tobin's Q",
    "ROA": "ROA",
    "CashHoldings": "Cash Holdings",
    "DividendPayer": "Dividend Payer",
    "OCF_Volatility": "OCF Volatility",
}

SAMPLES = ["Main", "Finance", "Utility"]


# ==============================================================================
# Summary Statistics Variables
# ==============================================================================

SUMMARY_STATS_VARS = [
    # Dependent variable (lead)
    {"col": "EmploymentGrowth_lead", "label": "Employment Growth$_{t+1}$"},
    # Main independent variable
    {"col": "Avg_CEO_Pres_Uncertainty_pct", "label": "Avg CEO Pres Uncertainty"},
    # Controls
    {"col": "Size", "label": "Firm Size (log AT)"},
    {"col": "TobinsQ", "label": "Tobin's Q"},
    {"col": "ROA", "label": "ROA"},
    {"col": "Lev", "label": "Leverage"},
    {"col": "CashHoldings", "label": "Cash Holdings"},
    {"col": "DividendPayer", "label": "Dividend Payer"},
    {"col": "OCF_Volatility", "label": "OCF Volatility"},
]


# ==============================================================================
# Data Loading
# ==============================================================================


def load_panel(root_path: Path, panel_file: Optional[Path] = None) -> pd.DataFrame:
    """Load the firm-year panel from Stage 3.

    Args:
        root_path: Project root directory
        panel_file: Optional explicit path to panel file

    Returns:
        DataFrame with panel data
    """
    print("\n" + "=" * 60)
    print("Loading H13.2 Employment Growth Panel (firm-year)")
    print("=" * 60)

    if panel_file is None:
        panel_dir = get_latest_output_dir(
            root_path / "outputs" / "variables" / "h13_2_employment",
            required_file="h13_2_employment_panel.parquet",
        )
        panel_file = panel_dir / "h13_2_employment_panel.parquet"

    if not panel_file.exists():
        raise FileNotFoundError(f"Panel file not found: {panel_file}")

    panel = pd.read_parquet(
        panel_file,
        columns=[
            "gvkey",
            "fyearq",
            "ff12_code",
            "sample",
            "EmploymentGrowth_lead",
            "Avg_CEO_Pres_Uncertainty_pct",
            "Size",
            "TobinsQ",
            "ROA",
            "Lev",
            "CashHoldings",
            "DividendPayer",
            "OCF_Volatility",
        ],
    )
    print(f"  Loaded: {panel_file}")
    print(f"  Rows: {len(panel):,}")
    print(f"  Columns: {len(panel.columns)}")
    return panel


def prepare_regression_data(panel: pd.DataFrame) -> pd.DataFrame:
    """Prepare panel for regression.

    - Drops rows where EmploymentGrowth_lead is NaN (last-year/gap-year firms)
    - Drops rows missing required variables (complete cases)
    - Applies minimum-firm-years-per-firm filter

    Args:
        panel: Full firm-year panel from Stage 3

    Returns:
        Prepared DataFrame ready for OLS
    """
    required = (
        ["EmploymentGrowth_lead", PRIMARY_IV]
        + CONTROL_VARS
        + ["gvkey", "fyearq"]
    )

    # Check required columns exist
    missing = [c for c in required if c not in panel.columns]
    if missing:
        raise ValueError(
            f"Required columns missing from panel: {missing}. Check Stage 3 output."
        )

    df = panel.copy()

    # Drop last-year and gap-year firms (no valid lead)
    before = len(df)
    df = df[df["EmploymentGrowth_lead"].notna()].copy()
    print(f"  After lead filter: {len(df):,} / {before:,}")

    # Complete cases on required variables
    df = df.replace([np.inf, -np.inf], np.nan)
    complete_mask = df[required].notna().all(axis=1)
    df = df[complete_mask].copy()
    print(f"  After complete cases: {len(df):,}")

    # Minimum firm-years per firm (5)
    firm_counts = df["gvkey"].value_counts()
    valid_firms = set(firm_counts[firm_counts >= MIN_FIRM_YEARS].index)
    df = df[df["gvkey"].isin(valid_firms)].copy()
    print(
        f"  After >={MIN_FIRM_YEARS} firm-years/firm filter: "
        f"{len(df):,} firm-years, {df['gvkey'].nunique():,} firms"
    )

    return df


# ==============================================================================
# Regression
# ==============================================================================


def run_regression(
    df_sample: pd.DataFrame,
    sample_name: str,
) -> Tuple[Any, Dict[str, Any]]:
    """Run OLS regression with firm FE + year FE (firm-year), firm-clustered SEs.

    Model (NO interactions):
        EmploymentGrowth_lead ~ Avg_CEO_Pres_Uncertainty_pct +
                               Size + TobinsQ + ROA + Lev + CashHoldings +
                               DividendPayer + OCF_Volatility +
                               EntityEffects + TimeEffects

    Standard errors: firm-clustered (groups=gvkey).
    Index: (gvkey, fyearq) - firm-year level.

    Args:
        df_sample: Sample-filtered and prepared DataFrame
        sample_name: Sample name for logging

    Returns:
        Tuple of (fitted model, metadata dict) or (None, {}) on failure
    """
    print("\n" + "=" * 60)
    print(f"Running regression: {sample_name}")
    print("=" * 60)

    if len(df_sample) < 100:
        print(f"  WARNING: Too few observations ({len(df_sample)}), skipping")
        return None, {}

    # Controls present
    controls = [c for c in CONTROL_VARS if c in df_sample.columns]

    # Build formula using PanelOLS syntax (NO interaction terms)
    formula = (
        "EmploymentGrowth_lead ~ 1 + "
        + PRIMARY_IV
        + " + "
        + " + ".join(controls)
        + " + EntityEffects + TimeEffects"
    )
    print(
        f"  Formula: EmploymentGrowth_lead ~ {PRIMARY_IV} + {' + '.join(controls)} "
        f"+ EntityEffects + TimeEffects"
    )
    print(
        f"  N firm-years: {len(df_sample):,}  |  N firms: {df_sample['gvkey'].nunique():,}"
    )
    print("  Estimating with firm-clustered SEs via PanelOLS...")
    t0 = datetime.now()

    # Create MultiIndex for PanelOLS (firm-year level: gvkey, fyearq)
    df_panel = df_sample.set_index(["gvkey", "fyearq"])

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

    # One-tailed hypothesis test: H13.2 beta(Avg_CEO_Pres_Uncertainty_pct) < 0
    beta = model.params.get(PRIMARY_IV, np.nan)
    p_two = model.pvalues.get(PRIMARY_IV, np.nan)
    beta_se = model.std_errors.get(PRIMARY_IV, np.nan)
    beta_t = model.tstats.get(PRIMARY_IV, np.nan)

    # H13.2: beta < 0 (one-tailed)
    if not np.isnan(p_two) and not np.isnan(beta):
        p_one = p_two / 2 if beta < 0 else 1 - p_two / 2
    else:
        p_one = np.nan

    h13_2_sig = (not np.isnan(p_one)) and (p_one < 0.05) and (beta < 0)

    print(
        f"  beta({PRIMARY_IV}): {beta:.6f}  SE={beta_se:.6f}  "
        f"p(one-tail)={p_one:.4f}  H13.2={'YES' if h13_2_sig else 'no'}"
    )

    # Store metadata
    meta = {
        "sample": sample_name,
        "primary_iv": PRIMARY_IV,
        "beta": beta,
        "beta_se": beta_se,
        "beta_t": beta_t,
        "beta_p_two": p_two,
        "beta_p_one": p_one,
        "beta_signif": h13_2_sig,
        "n_obs": int(model.nobs),
        "n_firms": df_sample["gvkey"].nunique(),
        "n_clusters": df_sample["gvkey"].nunique(),
        "cluster_var": "gvkey",
        "rsquared": float(model.rsquared_within),
        "rsquared_adj": float(model.rsquared_inclusive),
        "within_r2": within_r2,
    }

    return model, meta


# ==============================================================================
# Output Generation
# ==============================================================================


def save_outputs(
    all_results: List[Dict[str, Any]],
    out_dir: Path,
) -> pd.DataFrame:
    """Save regression outputs.

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

    # Save regression result text files (one per sample)
    for r in all_results:
        model = r.get("model")
        meta = r.get("meta", {})
        if model is None or not meta:
            continue
        sample = meta.get("sample", "unknown")
        fname = f"regression_results_{sample}.txt"
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

    return diag_df


def generate_report(
    all_results: List[Dict[str, Any]],
    diag_df: pd.DataFrame,
    out_dir: Path,
    duration: float,
) -> None:
    """Generate markdown report summarizing results."""
    report_lines = [
        "# Stage 4: H13.2 Future Employment Growth Test Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        "",
        "## Model Specification",
        "",
        "```",
        f"EmploymentGrowth_lead ~ {PRIMARY_IV} + Controls + EntityEffects + TimeEffects",
        "```",
        "",
        "**Controls:** " + ", ".join(CONTROL_VARS),
        "",
        "**Note:** NO CapexAt in H13.2 controls (unlike H13.1).",
        "",
        "## Hypothesis Test (one-tailed)",
        "",
        "- **H13.2:** β(Avg_CEO_Pres_Uncertainty_pct) < 0",
        "  - Higher CEO presentation uncertainty → lower future employment growth",
        "",
        "## Results Summary",
        "",
        "| Sample | N Obs | N Firms | β (Uncertainty) | SE | p (one-tail) | H13.2 Supported |",
        "|--------|------:|--------:|----------------:|---:|-------------:|:---------------:|",
    ]

    for _, row in diag_df.iterrows():
        sample = row.get("sample", "?")
        n_obs = row.get("n_obs", 0)
        n_firms = row.get("n_firms", 0)
        beta = row.get("beta", np.nan)
        se = row.get("beta_se", np.nan)
        p_one = row.get("beta_p_one", np.nan)
        sig = row.get("beta_signif", False)

        beta_str = f"{beta:.6f}" if not np.isnan(beta) else "—"
        se_str = f"{se:.6f}" if not np.isnan(se) else "—"
        p_str = f"{p_one:.4f}" if not np.isnan(p_one) else "—"
        sig_str = "✓" if sig else "—"

        report_lines.append(
            f"| {sample} | {n_obs:,} | {n_firms:,} | {beta_str} | {se_str} | {p_str} | {sig_str} |"
        )

    # Summary statistics
    n_sig = diag_df["beta_signif"].sum() if "beta_signif" in diag_df.columns else 0
    n_total = len(diag_df)
    report_lines.extend([
        "",
        "## Summary",
        "",
        f"**Significant results (p < 0.05, one-tailed):** {n_sig}/{n_total}",
        "",
    ])

    report_path = out_dir / "report_step4_H13_2.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"  Saved: report_step4_H13_2.md")


# ==============================================================================
# Main
# ==============================================================================


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 4: Test H13.2 Future Employment Growth Hypothesis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Validate inputs without executing"
    )
    parser.add_argument("--panel-file", type=str, default=None)
    return parser.parse_args()


def main(panel_file: Optional[str] = None) -> int:
    """Main execution."""
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    # Setup paths
    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "h13_2_employment" / timestamp

    # Setup logging
    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H13_2_Employment",
        timestamp=timestamp,
    )

    print("=" * 80)
    print("STAGE 4: Test H13.2 Future Employment Growth Hypothesis")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Log dir:   {log_dir}")
    print(f"Primary IV: {PRIMARY_IV}")
    print(f"Unit of observation: firm-fiscal-year (gvkey, fyearq)")

    # Load panel
    panel_path = Path(panel_file) if panel_file else None
    panel = load_panel(root, panel_path)

    # Prepare data
    print("\n" + "=" * 60)
    print("Preparing data")
    print("=" * 60)
    df_prepared = prepare_regression_data(panel)

    # Run regressions by sample
    all_results: List[Dict[str, Any]] = []

    for sample in SAMPLES:
        print(f"\n{'='*60}")
        print(f"Sample: {sample}")
        print("=" * 60)

        # Filter to sample
        if "sample" not in df_prepared.columns:
            # Recompute sample if not present
            df_prepared["sample"] = assign_industry_sample(df_prepared["ff12_code"])

        df_sample = df_prepared[df_prepared["sample"] == sample].copy()
        print(f"  Observations: {len(df_sample):,}")

        if len(df_sample) < 100:
            print(f"  Skipping {sample}: too few observations")
            continue

        model, meta = run_regression(df_sample, sample)
        if model is not None:
            all_results.append({"model": model, "meta": meta})

    # Save outputs
    out_dir.mkdir(parents=True, exist_ok=True)
    diag_df = save_outputs(all_results, out_dir)

    # Generate report
    duration = (datetime.now() - start_time).total_seconds()
    generate_report(all_results, diag_df, out_dir, duration)

    # Generate run manifest
    panel_input = root / "outputs" / "variables" / "h13_2_employment" / "latest" / "h13_2_employment_panel.parquet"
    generate_manifest(
        output_dir=out_dir,
        stage="stage4",
        timestamp=timestamp,
        input_paths={"panel": panel_input},
        output_files={"diagnostics": out_dir / "model_diagnostics.csv"},
    )
    print("  Saved: run_manifest.json")

    # Summary
    print("\n" + "=" * 80)
    print("H13.2 Future Employment Growth Test complete.")
    print(f"Duration: {duration:.1f} seconds")
    n_sig = diag_df["beta_signif"].sum() if "beta_signif" in diag_df.columns else 0
    print(f"Significant results: {n_sig}/{len(diag_df)}")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    args = parse_arguments()
    if args.dry_run:
        print("DRY-RUN mode -- validating inputs only")
        print("DRY-RUN complete.")
        sys.exit(0)

    sys.exit(main(args.panel_file))
