#!/usr/bin/env python3
"""
==============================================================================
STEP 4.1.3: Estimate CEO Clarity (Regime Analysis)
==============================================================================
ID: 4.1.3_EstimateCeoClarity_Regime
Description: Estimate CEO "Clarity" across different time periods/regimes.

Purpose:
    Estimate CEO "Clarity" as a personal communication trait using fixed effects
    OLS regression. Runs 3 separate regressions by FF12 industry classification:
    - Main: Non-financial, non-utility firms (FF12 codes 1-7, 9-10, 12)
    - Finance: Financial firms (FF12 code 11)
    - Utility: Utility firms (FF12 code 8)

Inputs:
    - 4_Outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet
    - 4_Outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_{year}.parquet
    - 4_Outputs/3_Financial_Features/latest/firm_controls_{year}.parquet
    - 4_Outputs/3_Financial_Features/latest/market_variables_{year}.parquet

Outputs:
    - 4_Outputs/4.1_CeoClarity/{timestamp}/ceo_clarity_scores.parquet
    - 4_Outputs/4.1_CeoClarity/{timestamp}/regression_results_{sample}.txt
    - 4_Outputs/4.1_CeoClarity/{timestamp}/model_diagnostics.csv
    - 4_Outputs/4.1_CeoClarity/{timestamp}/variable_reference.csv
    - 4_Outputs/4.1_CeoClarity/{timestamp}/report_step4_1.md

Deterministic: true
Dependencies:
    - Requires: Step 3.1
    - Uses: shared.regression_utils, shared.panel_ols, linearmodels

Author: Thesis Author
Date: 2026-02-11
==============================================================================
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import pandas as pd

# Try importing statsmodels
try:
    import statsmodels.formula.api as smf

    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    print("WARNING: statsmodels not available. Install with: pip install statsmodels")

# Import shared regression and reporting utilities
from f1d.shared.data_loading import load_all_data
from f1d.shared.observability_utils import (
    DualWriter,
    analyze_missing_values,
    get_process_memory_mb,
    print_stats_summary,
    save_stats,
)

# Import shared path validation utilities
from f1d.shared.regression_utils import run_fixed_effects_ols
from f1d.shared.regression_validation import (
    validate_columns,
    validate_sample_size,
)

# ==============================================================================
# CLI Arguments & Prerequisites
# ==============================================================================


def parse_arguments():
    """Parse command-line arguments for 4.1.3_EstimateCeoClarity_Regime.py."""
    parser = argparse.ArgumentParser(
        description="""
STEP 4.1.3: Estimate Regime-Based Clarity

Estimates clarity models in different regimes (pre/post crisis,
different CEO tenure periods). Identifies how clarity effects
vary across conditions.
        """.strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and prerequisites without executing",
    )

    return parser.parse_args()


def check_prerequisites(root):
    """Validate all required inputs and prerequisite steps exist."""
    from f1d.shared.dependency_checker import validate_prerequisites

    required_files: Dict[str, Any] = {}

    required_steps = {
        "2.2_ConstructVariables": "linguistic_variables.parquet",
        "3.1_FirmControls": "firm_controls.parquet",
        "3.2_MarketVariables": "market_variables.parquet",
    }

    validate_prerequisites(required_files, required_steps)


# ==============================================================================
# Configuration
# ==============================================================================

CONFIG: Dict[str, Any] = {
    "dependent_var": "NonCEO_Manager_QA_Uncertainty_pct",  # Non-CEO Manager Q&A speech
    "linguistic_controls": [
        "Manager_Pres_Uncertainty_pct",  # Same as 4.1
        "Analyst_QA_Uncertainty_pct",
        "Entire_All_Negative_pct",
    ],
    "firm_controls": ["StockRet", "MarketRet", "EPS_Growth", "SurpDec"],
    "min_calls_per_ceo": 5,
    "year_start": 2002,
    "year_end": 2018,
    "samples": {
        "Main": {"exclude_ff12": [8, 11], "include_ff12": None},
        "Finance": {"exclude_ff12": None, "include_ff12": [11]},
        "Utility": {"exclude_ff12": None, "include_ff12": [8]},
    },
}


# ==============================================================================
# ==============================================================================
# Data Preparation
# ==============================================================================
def prepare_regression_data(df, stats=None):
    """Filter to complete cases and assign industry samples."""
    print("\n" + "=" * 60)
    print("Preparing regression data")
    print("=" * 60)

    initial_n = len(df)

    # Filter to non-null ceo_id
    df = df[df["ceo_id"].notna()].copy()
    print(f"  After ceo_id filter: {len(df):,} / {initial_n:,}")
    if stats:
        stats["processing"]["ceo_id_filter"] = initial_n - len(df)

    # Define required variables
    required = (
        [CONFIG["dependent_var"]]
        + CONFIG["linguistic_controls"]
        + CONFIG["firm_controls"]
        + ["ceo_id", "year"]
    )

    # Check which variables exist
    missing_vars = [v for v in required if v not in df.columns]
    if missing_vars:
        print(f"  WARNING: Missing variables: {missing_vars}")
        required = [v for v in required if v in df.columns]

    # Filter to complete cases (vectorized)
    complete_mask = df[required].notna().all(axis=1)
    df = df[complete_mask].copy()
    print(f"  After complete cases filter: {len(df):,}")

    # Assign industry samples based on FF12
    df["sample"] = "Main"
    df.loc[df["ff12_code"] == 11, "sample"] = "Finance"
    df.loc[df["ff12_code"] == 8, "sample"] = "Utility"

    print("\n  Sample distribution:")
    for sample in ["Main", "Finance", "Utility"]:
        n = (df["sample"] == sample).sum()
        print(f"    {sample}: {n:,} calls")

    return df


# ==============================================================================
# Regression Estimation
# ==============================================================================
def run_regression(df_sample, sample_name):
    """Run OLS regression with CEO fixed effects for a single sample.

    Returns:
        model: Fitted OLS model
        df_reg: DataFrame used for regression (ceo_id converted to string)
        valid_ceos: Set of valid CEO IDs (numeric) that passed the min calls filter
    """
    print("\n" + "=" * 60)
    print(f"Running regression: {sample_name}")
    print("=" * 60)

    if not STATSMODELS_AVAILABLE:
        print("  ERROR: statsmodels not available")
        return None, None, None

    # Filter to CEOs with minimum calls
    min_calls = CONFIG["min_calls_per_ceo"]
    ceo_counts = df_sample["ceo_id"].value_counts()
    valid_ceos = set(ceo_counts[ceo_counts >= min_calls].index)
    df_reg = df_sample[df_sample["ceo_id"].isin(valid_ceos)].copy()

    print(
        f"  After >=5 calls filter: {len(df_reg):,} calls, {df_reg['ceo_id'].nunique():,} CEOs"
    )

    if len(df_reg) < 100:
        print(f"  WARNING: Too few observations ({len(df_reg)}), skipping")
        return None, None, None

    # Convert to string for categorical treatment
    df_reg["ceo_id"] = df_reg["ceo_id"].astype(str)
    df_reg["year"] = df_reg["year"].astype(str)

    # Build formula
    dep_var = CONFIG["dependent_var"]
    controls = CONFIG["linguistic_controls"] + CONFIG["firm_controls"]
    controls = [c for c in controls if c in df_reg.columns]

    formula = f"{dep_var} ~ C(ceo_id) + " + " + ".join(controls) + " + C(year)"
    print(f"  Formula: {formula[:80]}...")

    # Validate regression data before estimation
    print("  Validating regression data...")
    try:
        required_columns = [dep_var] + controls + ["ceo_id", "year"]
        validate_columns(df_reg, required_columns)
        validate_sample_size(df_reg, min_observations=100)
        print("  Validation passed")
    except Exception as e:
        print(f"  Validation failed: {e}")
        return None, None, None

    # Estimate model
    print("  Estimating... (this may take a minute)")
    start_time = datetime.now()

    try:
        model = run_fixed_effects_ols(df_reg, formula, sample_name, cov_type="HC1")
    except Exception as e:
        print(f"  ERROR: Regression failed: {e}")
        return None, None, None

    duration = (datetime.now() - start_time).total_seconds()

    print(f"  [OK] Complete in {duration:.1f}s")
    print(f"  R-squared: {model.rsquared:.4f}")
    print(f"  Adjusted R-squared: {model.rsquared_adj:.4f}")
    print(f"  N observations: {int(model.nobs):,}")
    print(f"  N parameters: {len(model.params):,}")

    return model, df_reg, valid_ceos


# ==============================================================================
# Extract CEO Fixed Effects
# ==============================================================================


def extract_ceo_fixed_effects(model, df_reg, sample_name):
    """Extract gamma_i coefficients and compute Clarity scores."""
    print(f"\n  Extracting CEO fixed effects for {sample_name}...")

    # Get CEO coefficient names
    ceo_params = {
        p: model.params[p] for p in model.params.index if p.startswith("C(ceo_id)")
    }

    # Parse CEO IDs
    ceo_effects = {}
    for param_name, gamma_i in ceo_params.items():
        if "[T." in param_name:
            ceo_id = param_name.split("[T.")[1].split("]")[0]
            ceo_effects[ceo_id] = gamma_i

    # Reference CEO (not in params) gets gamma = 0
    all_ceos = df_reg["ceo_id"].unique()
    reference_ceos = [c for c in all_ceos if c not in ceo_effects]
    for ref_ceo in reference_ceos:
        ceo_effects[ref_ceo] = 0.0

    print(f"  Found {len(ceo_effects)} CEOs (incl. {len(reference_ceos)} reference)")

    # Create DataFrame
    ceo_fe = pd.DataFrame(list(ceo_effects.items()), columns=["ceo_id", "gamma_i"])

    # Compute Clarity = -gamma_i (vectorized)
    ceo_fe["ClarityCEO_raw"] = -ceo_fe["gamma_i"]

    # Standardize (vectorized NumPy)
    mean_val = ceo_fe["ClarityCEO_raw"].mean()
    std_val = ceo_fe["ClarityCEO_raw"].std()
    ceo_fe["ClarityCEO"] = (ceo_fe["ClarityCEO_raw"] - mean_val) / std_val

    ceo_fe["sample"] = sample_name

    print(
        f"  ClarityCEO: mean={ceo_fe['ClarityCEO'].mean():.4f}, std={ceo_fe['ClarityCEO'].std():.4f}"
    )
    print(
        f"  Range: [{ceo_fe['ClarityCEO'].min():.4f}, {ceo_fe['ClarityCEO'].max():.4f}]"
    )

    return ceo_fe


# ==============================================================================
# Compute CEO-Level Statistics
# ==============================================================================


def compute_ceo_stats(df_sample_filtered, ceo_fe, sample_name):
    """Compute descriptive statistics per CEO.

    Args:
        df_sample_filtered: Original sample data (with numeric ceo_id) filtered to valid CEOs
        ceo_fe: DataFrame with ceo_id (string) and fixed effects
    """
    dep_var = CONFIG["dependent_var"]

    # Vectorized GroupBy aggregation (C-backed)
    ceo_stats = (
        df_sample_filtered.groupby("ceo_id")
        .agg(
            {
                dep_var: ["count", "mean", "std"],
                "ceo_name": "first",
                "start_date": ["min", "max"],
                "gvkey": "nunique",
            }
        )
        .reset_index()
    )

    # Flatten column names
    ceo_stats.columns = [
        "ceo_id",
        "n_calls",
        "avg_uncertainty",
        "std_uncertainty",
        "ceo_name",
        "first_call_date",
        "last_call_date",
        "n_firms",
    ]

    # Convert ceo_id to string to match ceo_fe
    ceo_stats["ceo_id"] = ceo_stats["ceo_id"].astype(str)

    # Merge with fixed effects
    ceo_scores = ceo_fe.merge(ceo_stats, on="ceo_id", how="left")

    # Sort by Clarity (descending)
    ceo_scores = ceo_scores.sort_values("ClarityCEO", ascending=False).reset_index(
        drop=True
    )

    return ceo_scores


# ==============================================================================
# Model Diagnostics
# ==============================================================================


def compute_diagnostics(model, sample_name, n_ceos, n_firms):
    """Compute model diagnostics."""
    return {
        "sample": sample_name,
        "n_observations": int(model.nobs),
        "n_ceos": n_ceos,
        "n_firms": n_firms,
        "r_squared": model.rsquared,
        "r_squared_adj": model.rsquared_adj,
        "f_statistic": model.fvalue,
        "f_pvalue": model.f_pvalue,
        "aic": model.aic,
        "bic": model.bic,
    }


# ==============================================================================
# Save Outputs
# ==============================================================================


def save_outputs(all_ceo_scores, all_diagnostics, all_models, out_dir, stats=None):
    """Save all output files."""
    print("\n" + "=" * 60)
    print("Saving outputs")
    print("=" * 60)

    # CEO Clarity Scores
    ceo_scores_df = pd.concat(all_ceo_scores, ignore_index=True)
    ceo_scores_path = out_dir / "ceo_clarity_scores.parquet"
    ceo_scores_df.to_parquet(ceo_scores_path, index=False)
    print(f"  Saved: ceo_clarity_scores.parquet ({len(ceo_scores_df):,} CEOs)")

    # Regression results (per sample)
    for sample_name, model in all_models.items():
        if model is not None:
            results_path = out_dir / f"regression_results_{sample_name.lower()}.txt"
            with open(results_path, "w") as f:
                f.write(model.summary().as_text())
            print(f"  Saved: regression_results_{sample_name.lower()}.txt")

    # Model diagnostics
    if all_diagnostics:
        diag_df = pd.DataFrame(all_diagnostics)
        diag_path = out_dir / "model_diagnostics.csv"
        diag_df.to_csv(diag_path, index=False)
        print("  Saved: model_diagnostics.csv")

    # Variable reference
    var_ref = pd.DataFrame(
        [
            {"Variable": "ceo_id", "Source": "Step 1", "Description": "CEO identifier"},
            {
                "Variable": "sample",
                "Source": "Calculated",
                "Description": "Industry sample (Main/Finance/Utility)",
            },
            {
                "Variable": "gamma_i",
                "Source": "Calculated",
                "Description": "CEO fixed effect coefficient",
            },
            {
                "Variable": "ClarityCEO_raw",
                "Source": "Calculated",
                "Description": "-gamma_i",
            },
            {
                "Variable": "ClarityCEO",
                "Source": "Calculated",
                "Description": "Standardized clarity score",
            },
            {
                "Variable": "n_calls",
                "Source": "Calculated",
                "Description": "Number of calls per CEO",
            },
            {
                "Variable": "avg_uncertainty",
                "Source": "Calculated",
                "Description": "Mean Manager_QA_Uncertainty_pct_mean",
            },
            {
                "Variable": "std_uncertainty",
                "Source": "Calculated",
                "Description": "Std of Manager_QA_Uncertainty_pct_mean",
            },
            {
                "Variable": "ceo_name",
                "Source": "Step 1",
                "Description": "CEO full name",
            },
            {
                "Variable": "first_call_date",
                "Source": "Calculated",
                "Description": "Min(start_date) per CEO",
            },
            {
                "Variable": "last_call_date",
                "Source": "Calculated",
                "Description": "Max(start_date) per CEO",
            },
            {
                "Variable": "n_firms",
                "Source": "Calculated",
                "Description": "nunique(gvkey) per CEO",
            },
        ]
    )
    var_ref_path = out_dir / "variable_reference.csv"
    var_ref.to_csv(var_ref_path, index=False)
    print("  Saved: variable_reference.csv")

    return ceo_scores_df


# ==============================================================================
# Generate Report
# ==============================================================================


def generate_report(all_ceo_scores, all_diagnostics, out_dir, duration):
    """Generate markdown report."""
    print("\n  Generating report...")

    ceo_scores = pd.concat(all_ceo_scores, ignore_index=True)

    report_lines = [
        "# Step 4.1: CEO Clarity Regression Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        "",
        "## Summary",
        "",
    ]

    # Summary table
    report_lines.append("| Sample | CEOs | Calls | R-squared |")
    report_lines.append("|--------|------|-------|-----------|")

    for diag in all_diagnostics:
        report_lines.append(
            f"| {diag['sample']} | {diag['n_ceos']:,} | {diag['n_observations']:,} | {diag['r_squared']:.4f} |"
        )

    report_lines.append("")

    # Top CEOs per sample
    for sample in ["Main", "Finance", "Utility"]:
        sample_df = ceo_scores[ceo_scores["sample"] == sample]
        if len(sample_df) == 0:
            continue

        report_lines.append(f"## {sample} Sample")
        report_lines.append("")
        report_lines.append("### Top 5 Clearest CEOs")
        report_lines.append("")
        report_lines.append("| Rank | CEO Name | Clarity | N Calls |")
        report_lines.append("|------|----------|---------|---------|")

        for i, row in sample_df.head(5).iterrows():
            ceo_name = row["ceo_name"] if pd.notna(row["ceo_name"]) else "Unknown"
            report_lines.append(
                f"| {sample_df.index.get_loc(i) + 1} | {ceo_name} | {row['ClarityCEO']:.3f} | {int(row['n_calls'])} |"
            )

        report_lines.append("")
        report_lines.append("### Top 5 Most Uncertain CEOs")
        report_lines.append("")
        report_lines.append("| Rank | CEO Name | Clarity | N Calls |")
        report_lines.append("|------|----------|---------|---------|")

        for i, row in sample_df.tail(5).iterrows():
            ceo_name = row["ceo_name"] if pd.notna(row["ceo_name"]) else "Unknown"
            report_lines.append(
                f"| {sample_df.index.get_loc(i) + 1} | {ceo_name} | {row['ClarityCEO']:.3f} | {int(row['n_calls'])} |"
            )

        report_lines.append("")

    # Write report
    report_path = out_dir / "report_step4_1.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print("  Saved: report_step4_1.md")


# ==============================================================================
# Main
# ==============================================================================


def main(year_start=None, year_end=None):
    """Main execution."""
    start_time = datetime.now()
    start_iso = start_time.isoformat()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    # Initialize observability
    mem_start = get_process_memory_mb()
    [mem_start["rss_mb"]]

    stats: Dict[str, Any] = {
        "step_id": "4.1.3_EstimateCeoClarity_Regime",
        "timestamp": timestamp,
        "input": {"files": [], "checksums": {}, "total_rows": 0, "total_columns": 0},
        "processing": {},
        "regressions": {},
        "output": {"final_rows": 0, "final_columns": 0, "files": [], "checksums": {}},
        "missing_values": {},
        "timing": {"start_iso": start_iso, "end_iso": "", "duration_seconds": 0.0},
        "memory": {
            "start_mb": mem_start["rss_mb"],
            "end_mb": 0.0,
            "peak_mb": 0.0,
            "delta_mb": 0.0,
        },
        "throughput": {
            "rows_per_second": 0.0,
            "total_rows": 0,
            "duration_seconds": 0.0,
        },
        "quality_anomalies": {},
    }

    # Override config if provided
    if year_start:
        CONFIG["year_start"] = year_start
    if year_end:
        CONFIG["year_end"] = year_end

    # Setup paths
    root = Path(__file__).resolve().parents[2]
    out_dir = root / "4_Outputs" / "4.1.3_CeoClarity_Regime" / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)
    log_dir = root / "3_Logs" / "4.1.3_CeoClarity_Regime" / timestamp
    log_dir.mkdir(parents=True, exist_ok=True)

    # Setup dual logging
    log_path = log_dir / f"step4_1_3_{timestamp}.log"
    dual_writer = DualWriter(log_path)
    sys.stdout = dual_writer

    print("=" * 80)
    print("STEP 4.1.3: CEO Regime Clarity (Non-CEO Manager Variables)")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output: {out_dir}")
    print(f"Years: {CONFIG['year_start']}-{CONFIG['year_end']}")

    # Load data
    df = load_all_data(root, CONFIG["year_start"], CONFIG["year_end"])

    # Prepare regression data
    df = prepare_regression_data(df, stats)

    # Run regressions for each sample
    all_ceo_scores = []
    all_diagnostics = []
    all_models = {}

    for sample_name in ["Main", "Finance", "Utility"]:
        df_sample = df[df["sample"] == sample_name].copy()

        if len(df_sample) < 100:
            print(
                f"\n  Skipping {sample_name}: too few observations ({len(df_sample)})"
            )
            continue

        # Run regression
        model, df_reg, valid_ceos = run_regression(df_sample, sample_name)

        if model is None:
            continue

        all_models[sample_name] = model

        # Extract CEO fixed effects
        ceo_fe = extract_ceo_fixed_effects(model, df_reg, sample_name)

        # Filter original sample to valid CEOs (before string conversion) for stats
        df_sample_filtered = df_sample[df_sample["ceo_id"].isin(valid_ceos)].copy()

        # Compute CEO stats using original data (with numeric ceo_id, start_date, gvkey)
        ceo_scores = compute_ceo_stats(df_sample_filtered, ceo_fe, sample_name)
        all_ceo_scores.append(ceo_scores)

        # Compute diagnostics
        diag = compute_diagnostics(
            model, sample_name, len(valid_ceos), df_sample_filtered["gvkey"].nunique()
        )
        all_diagnostics.append(diag)

        # Print top/bottom CEOs
        print(f"\n  Top 3 Clearest CEOs ({sample_name}):")
        for i, row in ceo_scores.head(3).iterrows():
            ceo_name = row["ceo_name"] if pd.notna(row["ceo_name"]) else "Unknown"
            print(
                f"    {i + 1}. {ceo_name}: Clarity={row['ClarityCEO']:.3f}, n={int(row['n_calls'])}"
            )

        print(f"\n  Top 3 Most Uncertain CEOs ({sample_name}):")
        for i, row in ceo_scores.tail(3).iterrows():
            ceo_name = row["ceo_name"] if pd.notna(row["ceo_name"]) else "Unknown"
            print(
                f"    {ceo_scores.index.get_loc(i) + 1}. {ceo_name}: Clarity={row['ClarityCEO']:.3f}, n={int(row['n_calls'])}"
            )

    # Save outputs
    if all_ceo_scores:
        save_outputs(all_ceo_scores, all_diagnostics, all_models, out_dir, stats)

        # Generate report
        duration = (datetime.now() - start_time).total_seconds()
        generate_report(all_ceo_scores, all_diagnostics, out_dir, duration)

    # Update symlink

    # Final summary
    duration = (datetime.now() - start_time).total_seconds()
    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.1f} seconds")
    print(f"Output: {out_dir}")

    # Final stats
    stats["timing"]["end_iso"] = datetime.now().isoformat()
    stats["timing"]["duration_seconds"] = round(
        (datetime.now() - start_time).total_seconds(), 2
    )

    if all_ceo_scores:
        ceo_scores_df = pd.concat(all_ceo_scores, ignore_index=True)
        stats["missing_values"] = analyze_missing_values(ceo_scores_df)

        if all_diagnostics:
            for diag in all_diagnostics:
                key = diag.get("sample", "unknown")
                stats["regressions"][key] = {
                    "n_observations": diag.get("n_observations", 0),
                    "n_ceos": diag.get("n_ceos", 0),
                    "n_firms": diag.get("n_firms", 0),
                    "r_squared": diag.get("r_squared", 0),
                    "r_squared_adj": diag.get("r_squared_adj", 0),
                    "f_statistic": diag.get("f_statistic", 0),
                    "f_pvalue": diag.get("f_pvalue", 0),
                    "aic": diag.get("aic", 0),
                    "bic": diag.get("bic", 0),
                }

    print_stats_summary(stats)
    save_stats(stats, out_dir)

    # Close log
    dual_writer.close()
    sys.stdout = dual_writer.terminal

    return 0


if __name__ == "__main__":
    args = parse_arguments()
    root = Path(__file__).parent.parent.parent

    if args.dry_run:
        print("Dry-run mode: validating inputs...")
        check_prerequisites(root)
        # validate_prerequisites already prints "[OK] All prerequisites validated"
        sys.exit(0)

    check_prerequisites(root)
    sys.exit(main())
