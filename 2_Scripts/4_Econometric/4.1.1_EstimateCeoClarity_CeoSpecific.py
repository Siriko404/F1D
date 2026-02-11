#!/usr/bin/env python3
"""
==============================================================================
STEP 4.1: Estimate CEO Fixed Effects & Compute Clarity Scores
==============================================================================

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
==============================================================================
"""

import argparse
import sys
import warnings
from datetime import datetime
from pathlib import Path

import pandas as pd

# Add 2_Scripts to Python path for shared module imports (MUST be before shared imports)
# Script is in 2_Scripts/4_Econometric/, need to add 2_Scripts/ to path
scripts_dir = Path(__file__).parent.parent
sys.path.insert(0, str(scripts_dir))

# ==============================================================================
# CLI Arguments & Prerequisites
# ==============================================================================


def parse_arguments():
    """Parse command-line arguments for 4.1.1_EstimateCeoClarity_CeoSpecific.py."""
    parser = argparse.ArgumentParser(
        description="""
STEP 4.1.1: Estimate CEO-Specific Clarity

Estimates CEO-specific clarity scores using CEO fixed effects
regression. Extracts CEO coefficients as time-invariant
clarity measures.
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
    from shared.dependency_checker import validate_prerequisites

    required_files = {}

    required_steps = {
        "2.2_ConstructVariables": "linguistic_variables.parquet",
        "3.1_FirmControls": "firm_controls.parquet",
        "3.2_MarketVariables": "market_variables.parquet",
    }

    validate_prerequisites(required_files, required_steps)


# Try importing statsmodels
try:
    import statsmodels.formula.api as smf

    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    print("WARNING: statsmodels not available. Install with: pip install statsmodels")

# Import shared regression and reporting utilities
from shared.data_loading import load_all_data
from shared.observability_utils import (
    DualWriter,
    analyze_missing_values,
    compute_file_checksum,
    get_process_memory_mb,
    print_stats_summary,
    save_stats,
)
from shared.regression_helpers import (
    prepare_regression_data,
)
from shared.regression_utils import run_fixed_effects_ols
from shared.regression_validation import (
    validate_columns,
    validate_sample_size,
)
from shared.reporting_utils import (
    generate_regression_report,
    save_model_diagnostics,
)

# Import shared path validation utilities
try:
    from shared.path_utils import (
        ensure_output_dir,
        get_latest_output_dir,
        validate_input_file,
        validate_output_path,
    )
except ImportError:
    import sys as _sys

    _script_dir = Path(__file__).parent.parent
    _sys.path.insert(0, str(_script_dir))
    from shared.path_utils import (
        get_latest_output_dir,
    )

warnings.filterwarnings("ignore", category=FutureWarning)

# ==============================================================================
# Configuration
# ==============================================================================

CONFIG = {
    "dependent_var": "CEO_QA_Uncertainty_pct",
    "linguistic_controls": [
        "CEO_Pres_Uncertainty_pct",
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
# Data Preparation
# ==============================================================================


def load_all_data(root, year_start, year_end, stats=None):
    """Load and merge all input data sources."""
    print("\n" + "=" * 60)
    print("Loading and merging data")
    print("=" * 60)

    # Resolve directories using timestamp-based resolution
    manifest_dir = get_latest_output_dir(
        root / "4_Outputs" / "1.0_BuildSampleManifest",
        required_file="master_sample_manifest.parquet",
    )
    lv_dir = get_latest_output_dir(
        root / "4_Outputs" / "2_Textual_Analysis" / "2.2_Variables"
    )
    fc_dir = get_latest_output_dir(root / "4_Outputs" / "3_Financial_Features")

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

    # Load linguistic variables, firm controls, market variables per year
    all_data = []

    for year in range(year_start, year_end + 1):
        # Linguistic variables
        lv_path = lv_dir / f"linguistic_variables_{year}.parquet"
        if not lv_path.exists():
            print(f"  WARNING: Missing linguistic_variables_{year}.parquet")
            continue

        lv = pd.read_parquet(lv_path)

        # Drop columns that would conflict with manifest (keep manifest versions)
        lv_drop_cols = [c for c in ["gvkey", "year", "start_date"] if c in lv.columns]
        if lv_drop_cols:
            lv = lv.drop(columns=lv_drop_cols)

        # Firm controls
        fc_path = fc_dir / f"firm_controls_{year}.parquet"
        fc = pd.read_parquet(fc_path) if fc_path.exists() else pd.DataFrame()

        # Market variables
        mv_path = fc_dir / f"market_variables_{year}.parquet"
        mv = pd.read_parquet(mv_path) if mv_path.exists() else pd.DataFrame()

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

    # Estimate model using shared function
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
            report_path = generate_regression_report(model, sample_name, out_dir)
            print(f"  Saved: {report_path.name}")

    # Model diagnostics
    if all_diagnostics:
        pd.DataFrame(all_diagnostics)
        # Combine all model diagnostics into single CSV
        for sample_name, model in all_models.items():
            if model is not None:
                save_model_diagnostics(model, sample_name, out_dir)
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

    stats = {
        "step_id": "4.1.1_EstimateCeoClarity_CeoSpecific",
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
    out_dir = root / "4_Outputs" / "4.1.1_CeoClarity_CEO_Only" / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)
    log_dir = root / "3_Logs" / "4.1.1_CeoClarity_CEO_Only" / timestamp
    log_dir.mkdir(parents=True, exist_ok=True)

    # Setup dual logging
    log_path = log_dir / f"step4_1_1_{timestamp}.log"
    dual_writer = DualWriter(log_path)
    sys.stdout = dual_writer

    print("=" * 80)
    print("STEP 4.1.1: CEO Clarity Regression (CEO-Only Variables)")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output: {out_dir}")
    print(f"Years: {CONFIG['year_start']}-{CONFIG['year_end']}")

    # Load data
    df = load_all_data(root, CONFIG["year_start"], CONFIG["year_end"], stats)

    # Prepare regression data
    df = prepare_regression_data(
        df=df,
        dependent_var=CONFIG["dependent_var"],
        linguistic_controls=CONFIG["linguistic_controls"],
        firm_controls=CONFIG["firm_controls"],
        stats=stats,
    )

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
        print("[OK] All prerequisites validated")
        sys.exit(0)

    check_prerequisites(root)
    sys.exit(main())
