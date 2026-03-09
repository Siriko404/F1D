#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test H13.1 Capital Expenditure Hypothesis
================================================================================
ID: econometric/run_h13_1_capex
Description: Run H13.1 Capital Expenditure hypothesis test with multi-IV, multi-DV
             specification following the H1 pattern.

Model Specifications (8 specs × 3 samples = 24 regressions):
    Dependent Variables: CapexAt_lead (t+1), CapexAt (t)
    Uncertainty Measures: CEO/Manager × Presentation/QA (4)
    Controls: Size, TobinsQ, ROA, Lev, CashHoldings, DividendPayer, OCF_Volatility
              [+ CapexAt for CapexAt_lead models]

    CRITICAL: When DV = CapexAt, exclude CapexAt from controls (would be DV on both sides)

Hypothesis Test (one-tailed):
    H13.1: beta(Uncertainty) < 0
           Higher speech uncertainty -> lower capital expenditure

Industry Samples:
    - Main:    FF12 codes 1-7, 9-10, 12 (non-financial, non-utility)
    - Finance: FF12 code 11
    - Utility: FF12 code 8

Minimum Calls Filter:
    Firms must have >= 5 calls in the sample to be included in regression.

Inputs:
    - outputs/variables/h13_1_capex/latest/h13_1_capex_panel.parquet

Outputs:
    - outputs/econometric/h13_1_capex/{timestamp}/regression_results_{sample}_{dv}_{measure}.txt
    - outputs/econometric/h13_1_capex/{timestamp}/model_diagnostics.csv
    - outputs/econometric/h13_1_capex/{timestamp}/report_step4_H13_1.md

Author: Thesis Author
Date: 2026-03-08
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

# Dependent variables (2)
DEPENDENT_VARS = [
    "CapexAt_lead",  # Future CapEx (t+1)
    "CapexAt",       # Contemporaneous CapEx (t)
]

# Uncertainty measures (4)
UNCERTAINTY_MEASURES = [
    "CEO_Pres_Uncertainty_pct",
    "CEO_QA_Uncertainty_pct",
    "Manager_Pres_Uncertainty_pct",
    "Manager_QA_Uncertainty_pct",
]

# Base control variables (common to all specs)
BASE_CONTROL_VARS = [
    "Size",
    "TobinsQ",
    "ROA",
    "Lev",
    "CashHoldings",
    "DividendPayer",
    "OCF_Volatility",
]

# CapexAt control - only included when DV is CapexAt_lead
CAPEXAT_CONTROL = "CapexAt"

# Minimum calls per firm
MIN_CALLS_PER_FIRM = 5

SAMPLES = ["Main", "Finance", "Utility"]

VARIABLE_LABELS = {
    # Dependent variables
    "CapexAt_lead": "CapEx$_{t+1}$ / Assets",
    "CapexAt": "CapEx$_t$ / Assets",
    # Uncertainty measures
    "CEO_Pres_Uncertainty_pct": "CEO Pres Uncertainty",
    "CEO_QA_Uncertainty_pct": "CEO QA Uncertainty",
    "Manager_Pres_Uncertainty_pct": "Mgr Pres Uncertainty",
    "Manager_QA_Uncertainty_pct": "Mgr QA Uncertainty",
    # Controls
    "Lev": "Leverage",
    "Size": "Firm Size (log AT)",
    "TobinsQ": "Tobin's Q",
    "ROA": "ROA",
    "CashHoldings": "Cash Holdings",
    "DividendPayer": "Dividend Payer",
    "OCF_Volatility": "OCF Volatility",
}


# ==============================================================================
# Summary Statistics Variables
# ==============================================================================

SUMMARY_STATS_VARS = [
    # Dependent variables
    {"col": "CapexAt_lead", "label": "CapEx$_{t+1}$ / Assets"},
    {"col": "CapexAt", "label": "CapEx$_t$ / Assets"},
    # Uncertainty measures (all 4)
    {"col": "CEO_Pres_Uncertainty_pct", "label": "CEO Pres Uncertainty"},
    {"col": "CEO_QA_Uncertainty_pct", "label": "CEO QA Uncertainty"},
    {"col": "Manager_Pres_Uncertainty_pct", "label": "Mgr Pres Uncertainty"},
    {"col": "Manager_QA_Uncertainty_pct", "label": "Mgr QA Uncertainty"},
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
    """Load the call-level panel from Stage 3.

    Args:
        root_path: Project root directory
        panel_file: Optional explicit path to panel file

    Returns:
        DataFrame with panel data
    """
    print("\n" + "=" * 60)
    print("Loading H13.1 Capex Panel (call-level)")
    print("=" * 60)

    if panel_file is None:
        panel_dir = get_latest_output_dir(
            root_path / "outputs" / "variables" / "h13_1_capex",
            required_file="h13_1_capex_panel.parquet",
        )
        panel_file = panel_dir / "h13_1_capex_panel.parquet"

    if not panel_file.exists():
        raise FileNotFoundError(f"Panel file not found: {panel_file}")

    panel = pd.read_parquet(
        panel_file,
        columns=[
            "gvkey",
            "year",
            "ff12_code",
            "sample",
            # Dependent variables
            "CapexAt_lead",
            "CapexAt",
            # All 4 uncertainty measures
            "CEO_Pres_Uncertainty_pct",
            "CEO_QA_Uncertainty_pct",
            "Manager_Pres_Uncertainty_pct",
            "Manager_QA_Uncertainty_pct",
            # Controls
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


def prepare_regression_data(
    panel: pd.DataFrame,
    uncertainty_var: str,
    dependent_var: str,
) -> pd.DataFrame:
    """Prepare panel for regression with DV-specific control handling.

    CRITICAL: When dependent_var == "CapexAt", excludes CapexAt from controls.

    Args:
        panel: Full call-level panel from Stage 3
        uncertainty_var: Which uncertainty measure to use
        dependent_var: Which dependent variable ("CapexAt_lead" or "CapexAt")

    Returns:
        Prepared DataFrame ready for OLS
    """
    # Build controls list based on DV
    if dependent_var == "CapexAt":
        # Exclude CapexAt from controls when it's the DV
        controls = BASE_CONTROL_VARS.copy()
    else:
        # Include CapexAt as control for CapexAt_lead models
        controls = BASE_CONTROL_VARS + [CAPEXAT_CONTROL]

    required = (
        [dependent_var, uncertainty_var]
        + controls
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
    df = df[df[dependent_var].notna()].copy()
    print(f"  After {dependent_var} filter: {len(df):,} / {before:,}")

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
    dependent_var: str,
) -> Tuple[Any, Dict[str, Any]]:
    """Run OLS regression with firm FE + year FE, firm-clustered SEs.

    CRITICAL: Automatically excludes CapexAt from controls when DV is CapexAt.
    """
    print("\n" + "=" * 60)
    print(f"Running regression: {sample_name} | DV: {dependent_var} | IV: {uncertainty_var}")
    print("=" * 60)

    if len(df_sample) < 100:
        print(f"  WARNING: Too few observations ({len(df_sample)}), skipping")
        return None, {}

    # Build controls list based on DV
    if dependent_var == "CapexAt":
        controls = BASE_CONTROL_VARS.copy()
    else:
        controls = BASE_CONTROL_VARS + [CAPEXAT_CONTROL]

    # Filter to available controls
    controls = [c for c in controls if c in df_sample.columns]

    # Build formula
    formula = (
        f"{dependent_var} ~ 1 + "
        + uncertainty_var
        + " + "
        + " + ".join(controls)
        + " + EntityEffects + TimeEffects"
    )
    print(f"  Formula: {dependent_var} ~ {uncertainty_var} + {' + '.join(controls)} + FE")
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

    # One-tailed hypothesis test: H13.1 beta(uncertainty_var) < 0
    beta = model.params.get(uncertainty_var, np.nan)
    p_two = model.pvalues.get(uncertainty_var, np.nan)
    beta_se = model.std_errors.get(uncertainty_var, np.nan)
    beta_t = model.tstats.get(uncertainty_var, np.nan)

    # H13.1: beta < 0 (one-tailed)
    if not np.isnan(p_two) and not np.isnan(beta):
        p_one = p_two / 2 if beta < 0 else 1 - p_two / 2
    else:
        p_one = np.nan

    h13_1_sig = (not np.isnan(p_one)) and (p_one < 0.05) and (beta < 0)

    print(
        f"  beta({uncertainty_var}): {beta:.6f}  SE={beta_se:.6f}  "
        f"p(one-tail)={p_one:.4f}  H13.1={'YES' if h13_1_sig else 'no'}"
    )

    # Store metadata - INCLUDE BOTH DV AND UNCERTAINTY VAR
    meta = {
        "sample": sample_name,
        "dependent_var": dependent_var,
        "uncertainty_var": uncertainty_var,
        "beta": beta,
        "beta_se": beta_se,
        "beta_t": beta_t,
        "beta_p_two": p_two,
        "beta_p_one": p_one,
        "beta_signif": h13_1_sig,
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

    # Save regression result text files (one per regression)
    for r in all_results:
        model = r.get("model")
        meta = r.get("meta", {})
        if model is None or not meta:
            continue
        sample = meta.get("sample", "unknown")
        dv = meta.get("dependent_var", "unknown")
        measure = meta.get("uncertainty_var", "unknown")

        # FILE NAMING: regression_results_{sample}_{dv}_{measure}.txt
        fname = f"regression_results_{sample}_{dv}_{measure}.txt"
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
        "# Stage 4: H13.1 Capital Expenditure Test Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        "",
        "## Model Specification",
        "",
        "```",
        "{DV} ~ {Uncertainty} + Controls + EntityEffects + TimeEffects",
        "```",
        "",
        "**Dependent Variables:** CapexAt_lead (t+1), CapexAt (t)",
        "**Uncertainty Measures:** CEO/Manager × Pres/QA (4)",
        "**Controls:** Size, TobinsQ, ROA, Lev, CashHoldings, DividendPayer, OCF_Volatility, [+CapexAt for CapexAt_lead models]",
        "",
        "## Hypothesis Test (one-tailed)",
        "",
        "- **H13.1:** β(Uncertainty) < 0",
        "  - Higher speech uncertainty → lower capital expenditure",
        "",
        "## Results Summary",
        "",
        "| DV | Sample | Uncertainty Measure | N Obs | N Firms | β (Unc) | SE | p (one-tail) | H13.1 |",
        "|----|--------|--------------------|------:|--------:|--------:|---:|-------------:|:-----:|",
    ]

    for _, row in diag_df.iterrows():
        dv = row.get("dependent_var", "?")
        sample = row.get("sample", "?")
        measure = row.get("uncertainty_var", "?")
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

        # Shorten DV name for display
        dv_short = "CapEx_t+1" if dv == "CapexAt_lead" else "CapEx_t"
        # Shorten measure name
        measure_short = measure.replace("_Uncertainty_pct", "").replace("_", " ")

        report_lines.append(
            f"| {dv_short} | {sample} | {measure_short} | {n_obs:,} | {n_firms:,} | {beta_str} | {se_str} | {p_str} | {sig_str} |"
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

    report_path = out_dir / "report_step4_H13_1.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"  Saved: report_step4_H13_1.md")


# ==============================================================================
# Main
# ==============================================================================


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Stage 4: Test H13.1 Future Capital Expenditure Hypothesis",
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
    out_dir = root / "outputs" / "econometric" / "h13_1_capex" / timestamp

    # Setup logging
    log_dir = setup_run_logging(
        log_base_dir=root / "logs",
        suite_name="H13_1_Capex",
        timestamp=timestamp,
    )

    print("=" * 80)
    print("STAGE 4: Test H13.1 Capital Expenditure Hypothesis")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output:    {out_dir}")
    print(f"Log dir:   {log_dir}")
    print(f"DVs: {DEPENDENT_VARS}")
    print(f"Uncertainty measures: {UNCERTAINTY_MEASURES}")
    print(f"Unit of observation: earnings call (file_name)")

    # Load panel
    panel_path = Path(panel_file) if panel_file else None
    panel = load_panel(root, panel_path)

    # Assign sample if not present
    if "sample" not in panel.columns:
        panel["sample"] = assign_industry_sample(panel["ff12_code"])

    all_results: List[Dict[str, Any]] = []

    # 3-LEVEL NESTED LOOP: DV × Sample × Measure
    for dependent_var in DEPENDENT_VARS:
        print(f"\n{'='*80}")
        print(f"DEPENDENT VARIABLE: {dependent_var}")
        print("=" * 80)

        for sample in SAMPLES:
            print(f"\n{'='*60}")
            print(f"Sample: {sample}")
            print("=" * 60)

            # Filter to sample first
            df_sample_base = panel[panel["sample"] == sample].copy()
            print(f"  Base observations: {len(df_sample_base):,}")

            if len(df_sample_base) < 100:
                print(f"  Skipping {sample}: too few observations")
                continue

            for uncertainty_var in UNCERTAINTY_MEASURES:
                print(f"\n  {'--'*25}")
                print(f"  IV: {uncertainty_var}")
                print(f"  {'--'*25}")

                # Per-measure data prep (handles different missing patterns)
                df_prepared = prepare_regression_data(
                    df_sample_base, uncertainty_var, dependent_var
                )

                if len(df_prepared) < 100:
                    print(f"    Skipping: too few complete cases ({len(df_prepared)})")
                    continue

                model, meta = run_regression(
                    df_prepared, sample, uncertainty_var, dependent_var
                )
                if model is not None:
                    all_results.append({"model": model, "meta": meta})

    # Save outputs
    out_dir.mkdir(parents=True, exist_ok=True)
    diag_df = save_outputs(all_results, out_dir)

    # Generate report
    duration = (datetime.now() - start_time).total_seconds()
    generate_report(all_results, diag_df, out_dir, duration)

    # Generate run manifest
    panel_input = root / "outputs" / "variables" / "h13_1_capex" / "latest" / "h13_1_capex_panel.parquet"
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
    print("H13.1 Future Capital Expenditure Test complete.")
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
