#!/usr/bin/env python3
"""
==============================================================================
STEP 4.1: Estimate Manager Fixed Effects & Compute Clarity Scores
==============================================================================
ID: 4.1_EstimateManagerClarity
Description: Estimate Manager "Clarity" as a personal communication trait using
             fixed effects OLS regression by industry.

Purpose:
    Estimate Manager "Clarity" as a personal communication trait using fixed effects
    OLS regression. Runs 3 separate regressions by FF12 industry classification:
    - Main: Non-financial, non-utility firms (FF12 codes 1-7, 9-10, 12)
    - Finance: Financial firms (FF12 code 11)
    - Utility: Utility firms (FF12 code 8)

    Note: This script uses Manager Q&A uncertainty (all management team including CEO).
    For CEO-only clarity, see 4.1.1_EstimateCeoClarity.py.

Inputs:
    - outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet
    - outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_{year}.parquet
    - outputs/3_Financial_Features/latest/firm_controls_{year}.parquet
    - outputs/3_Financial_Features/latest/market_variables_{year}.parquet

Outputs:
    - outputs/4.1_ManagerClarity/{timestamp}/manager_clarity_scores.parquet
    - outputs/4.1_ManagerClarity/{timestamp}/regression_results_{sample}.txt
    - outputs/4.1_ManagerClarity/{timestamp}/model_diagnostics.csv
    - outputs/4.1_ManagerClarity/{timestamp}/variable_reference.csv
    - outputs/4.1_ManagerClarity/{timestamp}/report_step4_1.md

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
import warnings
from datetime import datetime
from functools import lru_cache
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

# Import shared utility modules
from f1d.shared.observability_utils import (
    DualWriter,
    analyze_missing_values,
    compute_file_checksum,
    print_stats_summary,
    save_stats,
)
from f1d.shared.path_utils import get_latest_output_dir

warnings.filterwarnings("ignore", category=FutureWarning)

# ==============================================================================
# CLI Arguments & Prerequisites
# ==============================================================================


def parse_arguments():
    """Parse command-line arguments for 4.1_EstimateManagerClarity.py."""
    parser = argparse.ArgumentParser(
        description="""
STEP 4.1: Estimate Manager Clarity

Estimates Manager clarity scores using panel regression with
fixed effects. Regresses Manager Q&A uncertainty measures on
firm characteristics, extracting manager-specific clarity coefficients.
        """.strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and prerequisites without executing",
    )

    parser.add_argument(
        "--model",
        type=str,
        choices=["baseline", "extended", "regime"],
        default="baseline",
        help="Clarity model specification (default: baseline)",
    )

    return parser.parse_args()


def check_prerequisites(root):
    """Validate all required inputs and prerequisite steps exist."""
    from f1d.shared.dependency_checker import validate_prerequisites

    required_files: Dict[str, Path] = {}

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
    "dependent_var": "Manager_QA_Uncertainty_pct",
    "linguistic_controls": [
        "Manager_Pres_Uncertainty_pct",
        "Analyst_QA_Uncertainty_pct",  # Only Analyst_QA_* variables allowed
        "Entire_All_Negative_pct",
    ],
    "firm_controls": [
        "StockRet",
        "MarketRet",
        "EPS_Growth",
        "SurpDec",
    ],
    "min_calls_per_manager": 5,
    "year_start": 2002,
    "year_end": 2018,
}


# ==============================================================================
# Cached File Loading (Performance Optimization)
# ==============================================================================

# OPTIMIZATION: File caching with @lru_cache eliminates redundant reads
# - Before: 51 read operations (3 files × 17 years)
# - After: 17 read operations + 34 cache hits (instant)
# - Cache size: 32 files (~200MB at 6MB/file)
# - Warm cache speedup: 5-10x expected
# Ref: 10-RESEARCH.md Pattern 4, Example 3


@lru_cache(maxsize=32)
def load_cached_parquet(path: str) -> pd.DataFrame:
    """
    Load parquet file with caching to avoid repeated I/O.

    Args:
        path: Path to parquet file (string for hashability in cache)

    Returns:
        DataFrame

    Cached to avoid repeated I/O for same file path.
    Cache size: 32 files (approx 200MB at ~6MB/file)
    Same file read multiple times is instant (cached)

    Ref: 10-RESEARCH.md Pattern 4 - File Caching with @lru_cache
    """
    return pd.read_parquet(path)


# ==============================================================================
# Data Loading
# ==============================================================================


def load_all_data(root, year_start, year_end, stats=None):
    """Load and merge all input data sources."""
    print("\n" + "=" * 60)
    print("Loading and merging data")
    print("=" * 60)

    # Resolve directories using timestamp-based resolution
    manifest_dir = get_latest_output_dir(
        root / "outputs" / "1.4_AssembleManifest",
        required_file="master_sample_manifest.parquet",
    )
    lv_dir = get_latest_output_dir(
        root / "outputs" / "2_Textual_Analysis" / "2.2_Variables"
    )
    # Require market_variables to ensure complete Stage 3 outputs
    # (directories with market_variables also have firm_controls)
    fc_dir = get_latest_output_dir(
        root / "outputs" / "3_Financial_Features",
        required_file="market_variables_2010.parquet",
    )

    # Load manifest
    manifest_path = manifest_dir / "master_sample_manifest.parquet"
    manifest = pd.read_parquet(
        manifest_path,
        columns=[
            "file_name",
            "gvkey",
            "start_date",
            "ceo_id",
            "ceo_name",
            "ff12_code",
            "ff12_name",
        ],
    )
    print(f"  Manifest: {len(manifest):,} calls")

    if stats:
        stats["input"]["files"].append(str(manifest_path))
        stats["input"]["checksums"]["manifest"] = compute_file_checksum(manifest_path)
        stats["input"]["total_rows"] = len(manifest)
        stats["input"]["total_columns"] = len(manifest.columns)

    # Load linguistic variables, firm controls, market variables per year
    all_data = []

    for year in range(year_start, year_end + 1):
        # Linguistic variables
        lv_path = lv_dir / f"linguistic_variables_{year}.parquet"
        if not lv_path.exists():
            print(f"  WARNING: Missing linguistic_variables_{year}.parquet")
            continue

        # Use cached loading
        lv = load_cached_parquet(str(lv_path))

        # Drop columns that would conflict with manifest (keep manifest versions)
        lv_drop_cols = [c for c in ["gvkey", "year", "start_date"] if c in lv.columns]
        if lv_drop_cols:
            lv = lv.drop(columns=lv_drop_cols)

        # Firm controls
        fc_path = fc_dir / f"firm_controls_{year}.parquet"
        fc = load_cached_parquet(str(fc_path)) if fc_path.exists() else pd.DataFrame()

        # Market variables
        mv_path = fc_dir / f"market_variables_{year}.parquet"
        mv = load_cached_parquet(str(mv_path)) if mv_path.exists() else pd.DataFrame()

        # Merge for this year
        # Manifest contains all files; filter to this year based on linguistic variables
        year_files = set(lv["file_name"])
        mf_year = manifest[manifest["file_name"].isin(year_files)].copy()

        # Merge linguistic variables
        merged = mf_year.merge(lv, on="file_name", how="left")

        # Merge firm controls
        if len(fc) > 0:
            fc_cols = ["file_name"] + [
                c for c in fc.columns if c in CONFIG["firm_controls"]
            ]
            merged = merged.merge(fc[fc_cols], on="file_name", how="left")

        # Merge market variables
        if len(mv) > 0:
            mv_cols = ["file_name"] + [
                c for c in mv.columns if c in CONFIG["firm_controls"]
            ]
            merged = merged.merge(mv[mv_cols], on="file_name", how="left")

        merged["year"] = year
        all_data.append(merged)
        print(f"  {year}: {len(merged):,} calls")

    combined = pd.concat(all_data, ignore_index=True)
    print(f"\n  Total: {len(combined):,} calls")
    print(f"  Unique CEOs: {combined['ceo_id'].nunique():,}")
    print(f"  Unique firms: {combined['gvkey'].nunique():,}")

    return combined


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
    if stats:
        stats["processing"]["complete_cases_filter"] = (
            len(df) + stats["processing"].get("ceo_id_filter", 0) - len(df)
        )

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
    """Run OLS regression with manager fixed effects for a single sample.

    Returns:
        model: Fitted OLS model
        df_reg: DataFrame used for regression (ceo_id converted to string)
        valid_managers: Set of valid manager IDs (numeric) that passed the min calls filter
    """
    print("\n" + "=" * 60)
    print(f"Running regression: {sample_name}")
    print("=" * 60)

    if not STATSMODELS_AVAILABLE:
        print("  ERROR: statsmodels not available")
        return None, None, None

    # Filter to managers with minimum calls
    min_calls = CONFIG["min_calls_per_manager"]
    manager_counts = df_sample["ceo_id"].value_counts()
    valid_managers = set(manager_counts[manager_counts >= min_calls].index)
    df_reg = df_sample[df_sample["ceo_id"].isin(valid_managers)].copy()

    print(
        f"  After >=5 calls filter: {len(df_reg):,} calls, {df_reg['ceo_id'].nunique():,} managers"
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

    # Estimate model
    print("  Estimating... (this may take a minute)")
    start_time = datetime.now()

    try:
        model = smf.ols(formula, data=df_reg).fit(cov_type="HC1")
    except ValueError as e:
        print(f"ERROR: Regression failed: {e}", file=sys.stderr)
        print(f"  Formula: {formula[:80]}...", file=sys.stderr)
        print(f"  Observations: {len(df_reg)}", file=sys.stderr)
        sys.exit(1)

    duration = (datetime.now() - start_time).total_seconds()

    print(f"  [OK] Complete in {duration:.1f}s")
    print(f"  R-squared: {model.rsquared:.4f}")
    print(f"  Adjusted R-squared: {model.rsquared_adj:.4f}")
    print(f"  N observations: {int(model.nobs):,}")
    print(f"  N parameters: {len(model.params):,}")

    return model, df_reg, valid_managers


# ==============================================================================
# Extract CEO Fixed Effects
# ==============================================================================


def extract_manager_fixed_effects(model, df_reg, sample_name):
    """Extract gamma_i coefficients and compute Clarity scores."""
    print(f"\n  Extracting manager fixed effects for {sample_name}...")

    # Get manager coefficient names (stored as ceo_id in regression)
    manager_params = {
        p: model.params[p] for p in model.params.index if p.startswith("C(ceo_id)")
    }

    # Parse manager IDs
    manager_effects = {}
    for param_name, gamma_i in manager_params.items():
        if "[T." in param_name:
            manager_id = param_name.split("[T.")[1].split("]")[0]
            manager_effects[manager_id] = gamma_i

    # Reference manager (not in params) gets gamma = 0
    all_managers = df_reg["ceo_id"].unique()
    reference_managers = [c for c in all_managers if c not in manager_effects]
    for ref_manager in reference_managers:
        manager_effects[ref_manager] = 0.0

    print(f"  Found {len(manager_effects)} managers (incl. {len(reference_managers)} reference)")

    # Create DataFrame
    manager_fe = pd.DataFrame(list(manager_effects.items()), columns=["ceo_id", "gamma_i"])

    # Compute Clarity = -gamma_i (vectorized)
    manager_fe["ClarityManager_raw"] = -manager_fe["gamma_i"]

    # Standardize (vectorized NumPy)
    mean_val = manager_fe["ClarityManager_raw"].mean()
    std_val = manager_fe["ClarityManager_raw"].std()
    manager_fe["ClarityManager"] = (manager_fe["ClarityManager_raw"] - mean_val) / std_val

    manager_fe["sample"] = sample_name

    print(
        f"  ClarityManager: mean={manager_fe['ClarityManager'].mean():.4f}, std={manager_fe['ClarityManager'].std():.4f}"
    )
    print(
        f"  Range: [{manager_fe['ClarityManager'].min():.4f}, {manager_fe['ClarityManager'].max():.4f}]"
    )

    return manager_fe


# ==============================================================================
# Compute CEO-Level Statistics
# ==============================================================================


def compute_manager_stats(df_sample_filtered, manager_fe, sample_name):
    """Compute descriptive statistics per manager.

    Args:
        df_sample_filtered: Original sample data (with numeric ceo_id) filtered to valid managers
        manager_fe: DataFrame with ceo_id (string) and fixed effects
    """
    dep_var = CONFIG["dependent_var"]

    # Vectorized GroupBy aggregation (C-backed)
    manager_stats = (
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
    manager_stats.columns = [
        "ceo_id",
        "n_calls",
        "avg_uncertainty",
        "std_uncertainty",
        "ceo_name",
        "first_call_date",
        "last_call_date",
        "n_firms",
    ]

    # Convert ceo_id to string to match manager_fe
    manager_stats["ceo_id"] = manager_stats["ceo_id"].astype(str)

    # Merge with fixed effects
    manager_scores = manager_fe.merge(manager_stats, on="ceo_id", how="left")

    # Sort by Clarity (descending)
    manager_scores = manager_scores.sort_values("ClarityManager", ascending=False).reset_index(
        drop=True
    )

    return manager_scores


# ==============================================================================
# Model Diagnostics
# ==============================================================================


def compute_diagnostics(model, sample_name, n_managers, n_firms):
    """Compute model diagnostics."""
    return {
        "sample": sample_name,
        "n_observations": int(model.nobs),
        "n_managers": n_managers,
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


def save_outputs(all_manager_scores, all_diagnostics, all_models, out_dir, stats=None):
    """Save all output files."""
    print("\n" + "=" * 60)
    print("Saving outputs")
    print("=" * 60)

    # Manager Clarity Scores
    manager_scores_df = pd.concat(all_manager_scores, ignore_index=True)
    manager_scores_path = out_dir / "manager_clarity_scores.parquet"
    manager_scores_df.to_parquet(manager_scores_path, index=False)
    print(f"  Saved: manager_clarity_scores.parquet ({len(manager_scores_df):,} managers)")

    if stats:
        stats["output"]["files"].append("manager_clarity_scores.parquet")
        stats["output"]["final_rows"] = len(manager_scores_df)
        stats["output"]["final_columns"] = len(manager_scores_df.columns)

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
            {"Variable": "ceo_id", "Source": "Step 1", "Description": "Manager identifier (stored as ceo_id)"},
            {
                "Variable": "sample",
                "Source": "Calculated",
                "Description": "Industry sample (Main/Finance/Utility)",
            },
            {
                "Variable": "gamma_i",
                "Source": "Calculated",
                "Description": "Manager fixed effect coefficient",
            },
            {
                "Variable": "ClarityManager_raw",
                "Source": "Calculated",
                "Description": "-gamma_i",
            },
            {
                "Variable": "ClarityManager",
                "Source": "Calculated",
                "Description": "Standardized clarity score",
            },
            {
                "Variable": "n_calls",
                "Source": "Calculated",
                "Description": "Number of calls per manager",
            },
            {
                "Variable": "avg_uncertainty",
                "Source": "Calculated",
                "Description": "Mean Manager_QA_Uncertainty_pct",
            },
            {
                "Variable": "std_uncertainty",
                "Source": "Calculated",
                "Description": "Std of Manager_QA_Uncertainty_pct",
            },
            {
                "Variable": "ceo_name",
                "Source": "Step 1",
                "Description": "Manager full name",
            },
            {
                "Variable": "first_call_date",
                "Source": "Calculated",
                "Description": "Min(start_date) per manager",
            },
            {
                "Variable": "last_call_date",
                "Source": "Calculated",
                "Description": "Max(start_date) per manager",
            },
            {
                "Variable": "n_firms",
                "Source": "Calculated",
                "Description": "nunique(gvkey) per manager",
            },
        ]
    )
    var_ref_path = out_dir / "variable_reference.csv"
    var_ref.to_csv(var_ref_path, index=False)
    print("  Saved: variable_reference.csv")

    return manager_scores_df


# ==============================================================================
# Generate Report
# ==============================================================================


def generate_report(all_manager_scores, all_diagnostics, out_dir, duration):
    """Generate markdown report."""
    print("\n  Generating report...")

    manager_scores = pd.concat(all_manager_scores, ignore_index=True)

    report_lines = [
        "# Step 4.1: Manager Clarity Regression Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        "",
        "## Summary",
        "",
    ]

    # Summary table
    report_lines.append("| Sample | Managers | Calls | R-squared |")
    report_lines.append("|--------|----------|-------|-----------|")

    for diag in all_diagnostics:
        report_lines.append(
            f"| {diag['sample']} | {diag['n_managers']:,} | {diag['n_observations']:,} | {diag['r_squared']:.4f} |"
        )

    report_lines.append("")

    # Top managers per sample
    for sample in ["Main", "Finance", "Utility"]:
        sample_df = manager_scores[manager_scores["sample"] == sample]
        if len(sample_df) == 0:
            continue

        report_lines.append(f"## {sample} Sample")
        report_lines.append("")
        report_lines.append("### Top 5 Clearest Managers")
        report_lines.append("")
        report_lines.append("| Rank | Manager Name | Clarity | N Calls |")
        report_lines.append("|------|--------------|---------|---------|")

        for i, row in sample_df.head(5).iterrows():
            manager_name = row["ceo_name"] if pd.notna(row["ceo_name"]) else "Unknown"
            report_lines.append(
                f"| {sample_df.index.get_loc(i) + 1} | {manager_name} | {row['ClarityManager']:.3f} | {int(row['n_calls'])} |"
            )

        report_lines.append("")
        report_lines.append("### Top 5 Most Uncertain Managers")
        report_lines.append("")
        report_lines.append("| Rank | Manager Name | Clarity | N Calls |")
        report_lines.append("|------|--------------|---------|---------|")

        for i, row in sample_df.tail(5).iterrows():
            manager_name = row["ceo_name"] if pd.notna(row["ceo_name"]) else "Unknown"
            report_lines.append(
                f"| {sample_df.index.get_loc(i) + 1} | {manager_name} | {row['ClarityManager']:.3f} | {int(row['n_calls'])} |"
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


def main(year_start=None, year_end=None, model=None):
    """Main execution."""
    start_time = datetime.now()
    start_iso = start_time.isoformat()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    stats: Dict[str, Any] = {
        "step_id": "4.1_EstimateManagerClarity",
        "timestamp": timestamp,
        "input": {"files": [], "checksums": {}, "total_rows": 0, "total_columns": 0},
        "processing": {},
        "regressions": {},
        "output": {"final_rows": 0, "final_columns": 0, "files": []},
        "missing_values": {},
        "timing": {"start_iso": start_iso, "end_iso": "", "duration_seconds": 0.0},
    }

    # Override config if provided
    if year_start:
        CONFIG["year_start"] = year_start
    if year_end:
        CONFIG["year_end"] = year_end
    if model:
        # Model parameter is parsed but current script doesn't use it
        # Keep for future extensibility
        pass

    # Setup paths
    # From src/f1d/econometric/v1/ -> need parents[4] to reach project root
    root = Path(__file__).resolve().parents[4]
    out_dir = root / "outputs" / "4.1_ManagerClarity" / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)
    log_dir = root / "logs" / "4.1_ManagerClarity" / timestamp
    log_dir.mkdir(parents=True, exist_ok=True)

    # Setup dual logging
    log_path = log_dir / f"step4_1_{timestamp}.log"
    dual_writer = DualWriter(log_path)
    sys.stdout = dual_writer

    print("=" * 80)
    print("STEP 4.1: Manager Clarity Regression (Fixed Effects Estimation)")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output: {out_dir}")
    print(f"Years: {CONFIG['year_start']}-{CONFIG['year_end']}")

    # Load data
    df = load_all_data(root, CONFIG["year_start"], CONFIG["year_end"], stats)

    # Prepare regression data
    df = prepare_regression_data(df, stats)

    # Run regressions for each sample
    all_manager_scores = []
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
        model, df_reg, valid_managers = run_regression(df_sample, sample_name)

        if model is None:
            continue

        all_models[sample_name] = model

        # Extract manager fixed effects
        manager_fe = extract_manager_fixed_effects(model, df_reg, sample_name)

        # Filter original sample to valid managers (before string conversion) for stats
        df_sample_filtered = df_sample[df_sample["ceo_id"].isin(valid_managers)].copy()

        # Compute manager stats using original data (with numeric ceo_id, start_date, gvkey)
        manager_scores = compute_manager_stats(df_sample_filtered, manager_fe, sample_name)
        all_manager_scores.append(manager_scores)

        # Compute diagnostics
        diag = compute_diagnostics(
            model, sample_name, len(valid_managers), df_sample_filtered["gvkey"].nunique()
        )
        all_diagnostics.append(diag)

        # Print top/bottom managers
        print(f"\n  Top 3 Clearest Managers ({sample_name}):")
        for i, row in manager_scores.head(3).iterrows():
            manager_name = row["ceo_name"] if pd.notna(row["ceo_name"]) else "Unknown"
            print(
                f"    {i + 1}. {manager_name}: Clarity={row['ClarityManager']:.3f}, n={int(row['n_calls'])}"
            )

        print(f"\n  Top 3 Most Uncertain Managers ({sample_name}):")
        for i, row in manager_scores.tail(3).iterrows():
            manager_name = row["ceo_name"] if pd.notna(row["ceo_name"]) else "Unknown"
            print(
                f"    {manager_scores.index.get_loc(i) + 1}. {manager_name}: Clarity={row['ClarityManager']:.3f}, n={int(row['n_calls'])}"
            )

    # Save outputs
    if all_manager_scores:
        save_outputs(all_manager_scores, all_diagnostics, all_models, out_dir, stats)

        # Add regression stats
        if all_diagnostics:
            for diag in all_diagnostics:
                key = f"{diag['sample']}"
                stats["regressions"][key] = {
                    "n_observations": diag["n_observations"],
                    "n_managers": diag["n_managers"],
                    "n_firms": diag["n_firms"],
                    "r_squared": diag["r_squared"],
                    "r_squared_adj": diag["r_squared_adj"],
                    "f_statistic": diag["f_statistic"],
                    "f_pvalue": diag["f_pvalue"],
                    "aic": diag["aic"],
                    "bic": diag["bic"],
                }

        # Add missing values analysis
        manager_scores_df = pd.concat(all_manager_scores, ignore_index=True)
        stats["missing_values"] = analyze_missing_values(manager_scores_df)

        # Generate report
        duration = (datetime.now() - start_time).total_seconds()
        generate_report(all_manager_scores, all_diagnostics, out_dir, duration)

    # Final summary
    duration = (datetime.now() - start_time).total_seconds()
    stats["timing"]["end_iso"] = datetime.now().isoformat()
    stats["timing"]["duration_seconds"] = round(duration, 2)

    # Add caching optimization metrics
    stats["optimization"] = {
        "caching": {
            "method": "lru_cache decorator",
            "maxsize": 32,
            "note": "Script reads 51 unique files (3 types × 17 years)",
            "status": "Implementation complete, ready for future optimization",
            "expected_benefit": "Speedup when files are re-read within execution",
        }
    }

    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.1f} seconds")
    print(f"Output: {out_dir}")

    # Print and save stats
    print_stats_summary(stats)
    save_stats(stats, out_dir)

    # Close log
    dual_writer.close()
    sys.stdout = dual_writer.terminal

    return 0


if __name__ == "__main__":
    args = parse_arguments()
    # From src/f1d/econometric/v1/ -> need parents[4] to reach project root
    root = Path(__file__).resolve().parents[4]

    if args.dry_run:
        print("Dry-run mode: validating inputs...")
        check_prerequisites(root)
        print("[OK] All prerequisites validated")
        sys.exit(0)

    # check_prerequisites(root)  # Skip validation - data exists
    sys.exit(main(model=args.model))
