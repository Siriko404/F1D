#!/usr/bin/env python3
"""
================================================================================
STEP 4.2: H2 PRisk x Uncertainty -> Investment Efficiency (Merge)
================================================================================
ID: 4.2_H2_PRiskUncertaintyMerge
Description: Merge PRisk (political risk) and Managerial Uncertainty measures
             with InvestmentResidual, standardize both components, and create
             the interaction term PRisk_x_Uncertainty as the independent variable.

Purpose: Construct the complete regression dataset for testing H2: whether
         compound uncertainty (PRisk x Uncertainty) predicts decreased investment
         efficiency. This plan merges three data sources (PRisk, Uncertainty,
         InvestmentResidual), standardizes the interaction components, and creates
         all required variables for regression.

Inputs:
    - 1_Inputs/FirmLevelRisk/firmquarter_2022q1.csv (PRisk data)
    - 4_Outputs/2_Textual_Analysis/2.2_Variables/latest/ (Uncertainty measures)
    - 4_Outputs/3_Financial_V3/4.1_H2_BiddleInvestmentResidual/latest/H2_InvestmentResiduals.parquet

Outputs:
    - 4_Outputs/3_Financial_V3/4.2_H2_PRiskUncertaintyMerge/{timestamp}/H2_PRiskUncertainty_Analysis.parquet
    - 4_Outputs/3_Financial_V3/4.2_H2_PRiskUncertaintyMerge/{timestamp}/stats.json
    - 3_Logs/3_Financial_V3/4.2_H2_PRiskUncertaintyMerge/{timestamp}_Merge.log

Declared Outputs:
    - PRisk_std: Standardized political risk measure
    - Uncertainty_std: Standardized managerial uncertainty measure
    - PRisk_x_Uncertainty: Interaction term (product of standardized components)
    - InvestmentResidual: Dependent variable (from Plan 53-01)
    - Biddle controls: CashFlow, Size, Leverage, TobinQ, SalesGrowth

Key Specification:
    - Standardize BEFORE creating interaction:
      PRisk_std = (PRisk - mean) / sd
      Uncertainty_std = (Uncertainty - mean) / sd
    - Interaction: PRisk_x_Uncertainty = PRisk_std * Uncertainty_std
    - Rationale: Standardization yields interpretable coefficients (one SD change)

Deterministic: true
Dependencies:
    - Requires: Step 4.1_H2_BiddleInvestmentResidual
    - Uses: pandas, numpy

Author: Thesis Author
Date: 2026-02-11
================================================================================
"""

import argparse
import gc
import sys
import time
import warnings
from datetime import datetime
from pathlib import Path

import pandas as pd
import yaml

# Add parent directory to sys.path for shared module imports
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir))

# Import shared path validation utilities
# Import diagnostics for VIF calculation
from shared.diagnostics import compute_vif

# Import observability utilities
from shared.observability_utils import (
    calculate_throughput,
    compute_file_checksum,
    get_process_memory_mb,
    save_stats,
)
from shared.path_utils import (
    ensure_output_dir,
    get_latest_output_dir,
    validate_input_file,
)

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# ==============================================================================
# Configuration
# ==============================================================================


def load_config():
    """Load configuration from project.yaml"""
    config_path = Path(__file__).parent.parent.parent / "config" / "project.yaml"
    if config_path.exists():
        validate_input_file(config_path, must_exist=True)
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    return {}


def setup_paths(config, timestamp):
    """Set up all required paths"""
    root = Path(__file__).parent.parent.parent

    # Resolve InvestmentResidual directory using timestamp-based resolution
    residual_dir = get_latest_output_dir(
        root / "4_Outputs" / "3_Financial_V3" / "4.1_H2_BiddleInvestmentResidual",
        required_file="H2_InvestmentResiduals.parquet",
    )

    # Resolve linguistic variables directory
    ling_dir = root / "4_Outputs" / "2_Textual_Analysis" / "2.2_Variables"

    paths = {
        "root": root,
        "residual_dir": residual_dir,
        "prisk_file": root / "1_Inputs" / "FirmLevelRisk" / "firmquarter_2022q1.csv",
        "ling_vars_dir": ling_dir,
    }

    # Output directory
    output_base = root / "4_Outputs" / "3_Financial_V3" / "4.2_H2_PRiskUncertaintyMerge"
    paths["output_dir"] = output_base / timestamp
    ensure_output_dir(paths["output_dir"])

    # Log directory
    log_base = root / "3_Logs" / "3_Financial_V3" / "4.2_H2_PRiskUncertaintyMerge"
    ensure_output_dir(log_base)
    paths["log_file"] = log_base / f"{timestamp}_Merge.log"

    return paths


# ==============================================================================
# Data Loading - PRisk
# ==============================================================================


def load_prisk(prisk_file, year_range=(2002, 2018)):
    """
    Load PRisk (political risk) data from firmquarter_2022q1.csv.

    File format: TAB-separated (sep='\t')
    Required columns: gvkey, date, PRisk (primary measure)
    Optional columns: NPRisk, PRiskT_* for robustness

    Date format: "2002q1" -> year=2002, quarter=1

    Args:
        prisk_file: Path to firmquarter_2022q1.csv
        year_range: Tuple of (min_year, max_year) for filtering

    Returns:
        DataFrame with gvkey, year, PRisk, and optional measures
    """
    print("\n" + "-" * 60)
    print("Loading PRisk Data")
    print("-" * 60)

    if not prisk_file.exists():
        raise FileNotFoundError(f"PRisk file not found: {prisk_file}")

    # Read TAB-separated file
    print(f"  Reading: {prisk_file.name}")
    df = pd.read_csv(prisk_file, sep="\t")

    print(f"  Loaded: {len(df):,} observations")

    # Normalize gvkey - zero-pad to 6 characters
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)

    # Parse date format "2002q1" -> year, quarter
    def parse_quarter_date(date_str):
        """Parse '2002q1' format into (year, quarter)"""
        try:
            parts = date_str.lower().strip().split("q")
            year = int(parts[0])
            quarter = int(parts[1]) if len(parts) > 1 else 1
            return year, quarter
        except (ValueError, AttributeError, IndexError):
            return None, None

    # Apply date parsing
    parsed = df["date"].apply(parse_quarter_date)
    df["year"] = [x[0] if x else None for x in parsed]
    df["quarter"] = [x[1] if x else None for x in parsed]

    # Filter to valid years
    df = df[df["year"].between(year_range[0], year_range[1])]
    print(f"  Filtered to {year_range[0]}-{year_range[1]}: {len(df):,} observations")

    # Aggregate quarterly data to firm-year: mean(PRisk) across quarters
    print("  Aggregating to firm-year (mean across quarters)...")

    # Primary aggregation
    prisk_agg = df.groupby(["gvkey", "year"], as_index=False)["PRisk"].mean()

    # Optionally include NPRisk if available
    if "NPRisk" in df.columns:
        nprisk_agg = df.groupby(["gvkey", "year"], as_index=False)["NPRisk"].mean()
        prisk_agg = prisk_agg.merge(nprisk_agg, on=["gvkey", "year"], how="left")
        print("  Included NPRisk (alternative measure)")

    # Optionally include topic-specific PRisk measures
    prisk_topics = [col for col in df.columns if col.startswith("PRiskT_")]
    if prisk_topics:
        topic_agg = df.groupby(["gvkey", "year"], as_index=False)[prisk_topics].mean()
        prisk_agg = prisk_agg.merge(topic_agg, on=["gvkey", "year"], how="left")
        print(f"  Included {len(prisk_topics)} topic-specific PRisk measures")

    n_firms = prisk_agg["gvkey"].nunique()
    n_obs = len(prisk_agg)

    print(f"  PRisk aggregated to {n_obs:,} firm-year observations ({n_firms:,} firms)")

    return prisk_agg


def validate_prisk(df):
    """
    Report PRisk distribution and validate sufficient variation.

    Args:
        df: DataFrame with PRisk column

    Returns:
        Dictionary with PRisk statistics
    """
    print("\n" + "-" * 60)
    print("PRisk Distribution Validation")
    print("-" * 60)

    if "PRisk" not in df.columns:
        print("  [ERROR] PRisk column not found")
        return {}

    prisk_stats = {
        "mean": float(df["PRisk"].mean()),
        "std": float(df["PRisk"].std()),
        "min": float(df["PRisk"].min()),
        "max": float(df["PRisk"].max()),
        "n_missing": int(df["PRisk"].isna().sum()),
        "n_zero": int((df["PRisk"] == 0).sum()),
        "n": len(df),
    }

    print(f"  Mean: {prisk_stats['mean']:.2f}")
    print(f"  Std:  {prisk_stats['std']:.2f}")
    print(f"  Min:  {prisk_stats['min']:.2f}")
    print(f"  Max:  {prisk_stats['max']:.2f}")
    print(f"  Missing: {prisk_stats['n_missing']:,}")
    print(f"  Zero values: {prisk_stats['n_zero']:,}")

    # Check for sufficient variation
    if prisk_stats["std"] > 0:
        print("  [OK] Sufficient variation (std > 0)")
    else:
        print("  [WARNING] No variation in PRisk (std = 0)")

    # Check for excessive zeros
    zero_pct = prisk_stats["n_zero"] / prisk_stats["n"] * 100
    if zero_pct > 50:
        print(f"  [WARNING] {zero_pct:.1f}% of observations have PRisk = 0")

    return prisk_stats


# ==============================================================================
# Data Loading - Managerial Uncertainty
# ==============================================================================


def load_uncertainty_measures(ling_vars_dir, year_range=(2002, 2018)):
    """
    Load Managerial Uncertainty measures from linguistic variables.

    Reads all years: linguistic_variables_2002.parquet through linguistic_variables_2018.parquet
    Uses pd.concat() to combine all years

    Primary measure: Manager_QA_Uncertainty_pct
    Alternative measures (for robustness):
        - CEO_QA_Uncertainty_pct
        - Manager_Pres_Uncertainty_pct
        - CEO_Pres_Uncertainty_pct

    Args:
        ling_vars_dir: Directory containing linguistic_variables_*.parquet files
        year_range: Tuple of (min_year, max_year) for loading

    Returns:
        DataFrame with gvkey, year, Manager_QA_Uncertainty_pct, and alternatives
    """
    print("\n" + "-" * 60)
    print("Loading Managerial Uncertainty Measures")
    print("-" * 60)

    if not ling_vars_dir.exists():
        raise FileNotFoundError(
            f"Linguistic variables directory not found: {ling_vars_dir}"
        )

    # Find the most recent timestamped directory with full year coverage
    timestamped_dirs = sorted(
        [d for d in ling_vars_dir.iterdir() if d.is_dir() and d.name[0].isdigit()],
        key=lambda x: x.name,
        reverse=True,
    )

    # Find a directory with all required years
    data_dir = None
    for ts_dir in timestamped_dirs:
        # Check if all years are available
        years_available = [
            int(f.name.split("_")[-1].replace(".parquet", ""))
            for f in ts_dir.glob("linguistic_variables_*.parquet")
            if f.name.startswith("linguistic_variables_")
        ]
        if all(
            year in years_available for year in range(year_range[0], year_range[1] + 1)
        ):
            data_dir = ts_dir
            print(f"  Using directory: {ts_dir.name}")
            break

    if data_dir is None:
        # Fallback: use the most recent directory
        data_dir = timestamped_dirs[0]
        print(f"  Using latest directory: {data_dir.name}")

    # Load all years and concatenate
    yearly_files = []
    for year in range(year_range[0], year_range[1] + 1):
        file_path = data_dir / f"linguistic_variables_{year}.parquet"
        if file_path.exists():
            yearly_files.append(file_path)

    print(f"  Loading {len(yearly_files)} yearly files...")

    dfs = []
    for file_path in yearly_files:
        df_year = pd.read_parquet(file_path)
        dfs.append(df_year)

    df = pd.concat(dfs, ignore_index=True)
    print(f"  Loaded: {len(df):,} call-level observations")

    # Ensure gvkey is string and zero-padded
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)

    # Extract year from start_date
    df["start_date"] = pd.to_datetime(df["start_date"])
    df["year"] = df["start_date"].dt.year

    # Primary measure: Manager_QA_Uncertainty_pct
    primary_col = "Manager_QA_Uncertainty_pct"
    if primary_col not in df.columns:
        raise ValueError(
            f"Primary measure {primary_col} not found in linguistic variables"
        )

    # Aggregate call-level to firm-year: mean(Uncertainty_pct)
    print("  Aggregating to firm-year (mean across calls)...")

    # Primary aggregation
    agg_dict = {primary_col: "mean"}

    # Alternative measures if available
    alternative_cols = [
        "CEO_QA_Uncertainty_pct",
        "Manager_Pres_Uncertainty_pct",
        "CEO_Pres_Uncertainty_pct",
    ]

    for col in alternative_cols:
        if col in df.columns:
            agg_dict[col] = "mean"
            print(f"  Included: {col}")

    uncertainty_agg = df.groupby(["gvkey", "year"], as_index=False).agg(agg_dict)

    # Flatten column names (if using agg with dict, names get preserved)
    uncertainty_agg.columns = [
        col[0] if isinstance(col, tuple) else col for col in uncertainty_agg.columns
    ]

    n_firms = uncertainty_agg["gvkey"].nunique()
    n_obs = len(uncertainty_agg)

    print(
        f"  Uncertainty aggregated to {n_obs:,} firm-year observations ({n_firms:,} firms)"
    )

    return uncertainty_agg


def validate_uncertainty(df):
    """
    Report Uncertainty distribution and validate sufficient variation.

    Args:
        df: DataFrame with Manager_QA_Uncertainty_pct column

    Returns:
        Dictionary with Uncertainty statistics
    """
    print("\n" + "-" * 60)
    print("Uncertainty Distribution Validation")
    print("-" * 60)

    primary_col = "Manager_QA_Uncertainty_pct"

    if primary_col not in df.columns:
        print(f"  [ERROR] {primary_col} column not found")
        return {}

    uncertainty_stats = {
        "mean": float(df[primary_col].mean()),
        "std": float(df[primary_col].std()),
        "min": float(df[primary_col].min()),
        "max": float(df[primary_col].max()),
        "n_missing": int(df[primary_col].isna().sum()),
        "n": len(df),
    }

    print(f"  {primary_col}:")
    print(f"    Mean: {uncertainty_stats['mean']:.4f}")
    print(f"    Std:  {uncertainty_stats['std']:.4f}")
    print(f"    Min:  {uncertainty_stats['min']:.4f}")
    print(f"    Max:  {uncertainty_stats['max']:.4f}")
    print(f"    Missing: {uncertainty_stats['n_missing']:,}")

    # Check for sufficient variation
    if uncertainty_stats["std"] > 0:
        print("  [OK] Sufficient variation (std > 0)")
    else:
        print(f"  [WARNING] No variation in {primary_col} (std = 0)")

    # Compare with alternative measures if available
    alternative_cols = ["CEO_QA_Uncertainty_pct", "Manager_Pres_Uncertainty_pct"]
    for col in alternative_cols:
        if col in df.columns:
            corr = df[[primary_col, col]].corr().iloc[0, 1]
            print(f"  Correlation({primary_col}, {col}): {corr:.3f}")

    return uncertainty_stats


# ==============================================================================
# Data Loading - InvestmentResiduals
# ==============================================================================


def load_investment_residuals(residual_dir):
    """
    Load InvestmentResidual data from Plan 53-01 output.

    Required columns:
        - gvkey, year (fyear), InvestmentResidual (DV)
        - TobinQ_lag, SalesGrowth_lag (first-stage predictors)
        - ff48_code (industry classification)
        - Controls: CashFlow, Size, Leverage, TobinQ, SalesGrowth

    Args:
        residual_dir: Directory containing H2_InvestmentResiduals.parquet

    Returns:
        DataFrame with InvestmentResidual and controls
    """
    print("\n" + "-" * 60)
    print("Loading InvestmentResiduals (Plan 53-01)")
    print("-" * 60)

    residuals_file = residual_dir / "H2_InvestmentResiduals.parquet"

    if not residuals_file.exists():
        raise FileNotFoundError(f"InvestmentResiduals file not found: {residuals_file}")

    print(f"  Reading: {residuals_file}")
    df = pd.read_parquet(residuals_file)

    # Normalize column names - fyear vs year
    if "fyear" in df.columns and "year" not in df.columns:
        df.rename(columns={"fyear": "year"}, inplace=True)

    # Ensure gvkey is zero-padded
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)

    # Ensure year is integer
    df["year"] = df["year"].astype(int)

    print(f"  Loaded: {len(df):,} firm-year observations")

    # Report key columns
    key_cols = [
        "InvestmentResidual",
        "TobinQ_lag",
        "SalesGrowth_lag",
        "CashFlow",
        "Size",
        "Leverage",
        "TobinQ",
        "SalesGrowth",
        "ff48_code",
    ]
    for col in key_cols:
        if col in df.columns:
            n_valid = df[col].notna().sum()
            print(f"    {col}: {n_valid:,} valid")

    return df


# ==============================================================================
# Merge and Filter
# ==============================================================================


def merge_all_sources(investment_df, prisk_df, uncertainty_df):
    """
    Merge all three data sources on [gvkey, year].

    Starts with InvestmentResiduals (base), left merges PRisk and Uncertainty.
    Drops rows with missing key variables (listwise deletion).

    Args:
        investment_df: InvestmentResiduals from Plan 53-01
        prisk_df: Aggregated PRisk by firm-year
        uncertainty_df: Aggregated Uncertainty by firm-year

    Returns:
        Merged DataFrame with all variables
    """
    print("\n" + "-" * 60)
    print("Merging All Data Sources")
    print("-" * 60)

    # Start with InvestmentResiduals as base
    print(f"  Base (InvestmentResiduals): {len(investment_df):,} observations")

    # Left merge PRisk
    merged = investment_df.merge(
        prisk_df, on=["gvkey", "year"], how="left", indicator="prisk_merge"
    )
    n_prisk_match = (merged["prisk_merge"] == "both").sum()
    print(f"  After PRisk merge: {len(merged):,} ({n_prisk_match:,} matched)")

    # Left merge Uncertainty
    merged = merged.merge(
        uncertainty_df, on=["gvkey", "year"], how="left", indicator="uncertainty_merge"
    )
    n_unc_match = (merged["uncertainty_merge"] == "both").sum()
    print(f"  After Uncertainty merge: {len(merged):,} ({n_unc_match:,} matched)")

    # Report missingness by variable
    print("\n  Missingness:")
    for col in ["InvestmentResidual", "PRisk", "Manager_QA_Uncertainty_pct"]:
        if col in merged.columns:
            n_missing = merged[col].isna().sum()
            pct_missing = n_missing / len(merged) * 100
            print(f"    {col}: {n_missing:,} ({pct_missing:.1f}%)")

    # Listwise deletion: drop rows with missing key variables
    key_vars = ["InvestmentResidual", "PRisk", "Manager_QA_Uncertainty_pct"]
    before_drop = len(merged)
    merged = merged.dropna(subset=key_vars)
    after_drop = len(merged)

    print(f"\n  Listwise deletion on {key_vars}:")
    print(f"    Before: {before_drop:,}")
    print(f"    After:  {after_drop:,}")
    print(
        f"    Dropped: {before_drop - after_drop:,} ({(before_drop - after_drop) / before_drop * 100:.1f}%)"
    )

    # Clean up indicator columns
    merged = merged.drop(columns=["prisk_merge", "uncertainty_merge"], errors="ignore")

    return merged


def apply_sample_filters(df, year_range=(2002, 2018), winsorize=True):
    """
    Apply sample filters and winsorization.

    - Filter to year_range
    - Exclude financials (SIC 6000-6999) and utilities (SIC 4900-4999)
    - Winsorize continuous variables at 1% and 99% by year

    Note: Plan 53-01 already excluded financials/utilities, so this is a safety check.

    Args:
        df: Merged DataFrame
        year_range: Tuple of (min_year, max_year)
        winsorize: If True, winsorize continuous variables

    Returns:
        Filtered DataFrame
    """
    print("\n" + "-" * 60)
    print("Applying Sample Filters")
    print("-" * 60)

    len(df)

    # Filter to year range
    df = df[df["year"].between(year_range[0], year_range[1])].copy()
    print(f"  After year filter ({year_range[0]}-{year_range[1]}): {len(df):,}")

    # Note: Financial/utility exclusions already applied in Plan 53-01
    print("  Note: Financial/utility exclusions applied in Plan 53-01")

    # Winsorize key continuous variables at 1%/99% by year
    if winsorize:
        vars_to_winsorize = [
            "InvestmentResidual",
            "PRisk",
            "Manager_QA_Uncertainty_pct",
            "CashFlow",
            "Size",
            "Leverage",
            "TobinQ",
            "SalesGrowth",
        ]

        for var in vars_to_winsorize:
            if var in df.columns:
                df[var] = df.groupby("year")[var].transform(
                    lambda x: x.clip(lower=x.quantile(0.01), upper=x.quantile(0.99))
                    if x.notna().sum() > 0
                    else x
                )

        print(f"  Winsorized at 1%/99% by year: {vars_to_winsorize}")

    after_filter = len(df)
    print(f"\n  Final sample: {after_filter:,} observations")

    return df


# ==============================================================================
# Standardization and Interaction
# ==============================================================================


def standardize_variables(df, columns=None):
    """
    Standardize variables: (x - mean) / std

    Computes mean and std from the SAMPLE, stores parameters in stats.

    Args:
        df: DataFrame with variables to standardize
        columns: List of column names to standardize (default: ['PRisk', 'Manager_QA_Uncertainty_pct'])

    Returns:
        Tuple of (df_with_std, standardization_params)
    """
    print("\n" + "-" * 60)
    print("Standardizing Variables")
    print("-" * 60)

    if columns is None:
        columns = ["PRisk", "Manager_QA_Uncertainty_pct"]

    df_std = df.copy()
    std_params = {}

    for col in columns:
        if col not in df.columns:
            print(f"  [WARNING] Column {col} not found, skipping")
            continue

        # Compute mean and std from sample
        mean_val = df[col].mean()
        std_val = df[col].std()

        std_params[col] = {"mean": float(mean_val), "std": float(std_val)}

        # Create standardized column
        std_col_name = f"{col}_std"
        df_std[std_col_name] = (df[col] - mean_val) / std_val

        # Verify standardization
        actual_mean = df_std[std_col_name].mean()
        actual_std = df_std[std_col_name].std()

        print(f"  {col}:")
        print(f"    Mean (raw): {mean_val:.4f}, Std (raw): {std_val:.4f}")
        print(f"    Mean (std): {actual_mean:.6f} (expected ~0)")
        print(f"    Std (std):  {actual_std:.6f} (expected ~1)")

    return df_std, std_params


def create_interaction_term(
    df,
    col1="PRisk_std",
    col2="Manager_QA_Uncertainty_pct_std",
    interaction_name="PRisk_x_Uncertainty",
):
    """
    Create interaction term as product of standardized variables.

    IMPORTANT: Uses standardized components (NOT raw variables).

    Args:
        df: DataFrame with standardized columns
        col1: First standardized variable
        col2: Second standardized variable
        interaction_name: Name for interaction column

    Returns:
        DataFrame with interaction column added
    """
    print("\n" + "-" * 60)
    print("Creating Interaction Term")
    print("-" * 60)

    if col1 not in df.columns:
        raise ValueError(f"Column {col1} not found in DataFrame")
    if col2 not in df.columns:
        raise ValueError(f"Column {col2} not found in DataFrame")

    # Create interaction as product of standardized variables
    df[interaction_name] = df[col1] * df[col2]

    print(f"  {interaction_name} = {col1} * {col2}")
    print(f"  Mean: {df[interaction_name].mean():.6f}")
    print(f"  Std:  {df[interaction_name].std():.6f}")
    print(f"  Min:  {df[interaction_name].min():.6f}")
    print(f"  Max:  {df[interaction_name].max():.6f}")

    return df


def validate_interaction(df):
    """
    Report correlation matrix and check for extreme multicollinearity.

    Computes VIF for main effects and interaction term.

    Args:
        df: DataFrame with PRisk_std, Uncertainty_std, PRisk_x_Uncertainty

    Returns:
        Dictionary with correlation matrix and VIF results
    """
    print("\n" + "-" * 60)
    print("Validating Interaction Term")
    print("-" * 60)

    # Key variables
    key_vars = ["PRisk_std", "Manager_QA_Uncertainty_pct_std", "PRisk_x_Uncertainty"]

    # Check all exist
    missing = [v for v in key_vars if v not in df.columns]
    if missing:
        print(f"  [WARNING] Missing columns: {missing}")
        return {}

    # Correlation matrix
    corr_matrix = df[key_vars].corr()

    print("  Correlation Matrix:")
    print("  " + "-" * 50)
    for i, var1 in enumerate(key_vars):
        row = []
        for j, _var2 in enumerate(key_vars):
            val = corr_matrix.iloc[i, j]
            row.append(f"{val:.3f}")
        print(f"    {var1:<35} {'  '.join(row)}")

    # VIF calculation
    print("\n  VIF Analysis:")
    try:
        vif_df = compute_vif(df, key_vars, vif_threshold=10.0)

        for _, row in vif_df.iterrows():
            var = row["variable"]
            vif = row["VIF"]
            exceeded = row["threshold_exceeded"]
            status = "*** EXCEEDS 10" if exceeded else "OK"
            print(f"    {var:<35} VIF={vif:.2f}  {status}")

        vif_results = vif_df.to_dict("records")

    except Exception as e:
        print(f"    Could not compute VIF: {e}")
        vif_results = []

    # Note on mean-centering vs standardization
    print("\n  Note: Standardization is used for interpretability (1 SD change),")
    print("        not for multicollinearity reduction. Mean-centering does NOT")
    print("        reduce interaction multicollinearity (it's an expected property).")

    return {
        "correlation_matrix": corr_matrix.to_dict(),
        "vif_results": vif_results,
    }


# ==============================================================================
# Output Preparation
# ==============================================================================


def prepare_final_dataset(df):
    """
    Prepare final regression dataset with all required variables.

    Selects columns for regression:
        - Identifiers: gvkey, year, ff48_code
        - DV: InvestmentResidual
        - IV (primary): PRisk_x_Uncertainty
        - Main effects: PRisk_std, Manager_QA_Uncertainty_pct_std
        - Controls: CashFlow, Size, Leverage, TobinQ, SalesGrowth

    Alternative measures (for robustness):
        - Uncertainty alternatives: CEO_QA_Uncertainty_std, Manager_Pres_Uncertainty_std
        - PRisk alternatives: NPRisk_std, PRiskT_*_std

    Args:
        df: DataFrame with all variables

    Returns:
        DataFrame with selected columns for regression
    """
    print("\n" + "-" * 60)
    print("Preparing Final Dataset")
    print("-" * 60)

    # Core columns for regression
    core_cols = [
        "gvkey",
        "year",
        "ff48_code",
        "InvestmentResidual",
        "PRisk_x_Uncertainty",
        "PRisk_std",
        "Manager_QA_Uncertainty_pct_std",
        "CashFlow",
        "Size",
        "Leverage",
        "TobinQ",
        "SalesGrowth",
        "TobinQ_lag",
        "SalesGrowth_lag",
    ]

    # Select available columns
    output_cols = [col for col in core_cols if col in df.columns]

    # Add alternative measures if available
    alternative_uncertainty = [
        "CEO_QA_Uncertainty_pct",
        "Manager_Pres_Uncertainty_pct",
        "CEO_Pres_Uncertainty_pct",
    ]
    for col in alternative_uncertainty:
        if col in df.columns:
            output_cols.append(col)

    # Add NPRisk if available
    if "NPRisk" in df.columns:
        output_cols.append("NPRisk")

    # Add topic-specific PRisk if available
    prisk_topics = [col for col in df.columns if col.startswith("PRiskT_")]
    output_cols.extend(prisk_topics)

    # Remove duplicates and create final dataset
    output_cols = list(dict.fromkeys(output_cols))
    final_df = df[output_cols].copy()

    print(f"  Final dataset: {len(final_df):,} observations")
    print(f"  Columns: {len(final_df.columns)}")

    return final_df


# ==============================================================================
# CLI and Main
# ==============================================================================


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="""
STEP 4.2: H2 PRisk x Uncertainty -> Investment Efficiency (Merge)

Merge PRisk (political risk) and Managerial Uncertainty measures with
InvestmentResidual, standardize both components, and create the interaction
term PRisk_x_Uncertainty as the independent variable.

Standardization:
    PRisk_std = (PRisk - mean) / sd
    Uncertainty_std = (Uncertainty - mean) / sd
    PRisk_x_Uncertainty = PRisk_std * Uncertainty_std
        """.strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--config",
        type=str,
        default="config/project.yaml",
        help="Path to project.yaml config file",
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Override output directory",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and print merge plan without executing",
    )

    parser.add_argument(
        "--primary-measure",
        type=str,
        default="Manager_QA_Uncertainty_pct",
        help="Primary uncertainty measure (default: Manager_QA_Uncertainty_pct)",
    )

    parser.add_argument(
        "--prisk-measure",
        type=str,
        default="PRisk",
        help="Primary PRisk measure (default: PRisk)",
    )

    return parser.parse_args()


def check_prerequisites(paths, args):
    """Validate all required inputs exist"""
    print("\nChecking prerequisites...")

    required_files = {
        "InvestmentResiduals": paths["residual_dir"] / "H2_InvestmentResiduals.parquet",
        "PRisk": paths["prisk_file"],
        "Linguistic Variables": paths["ling_vars_dir"],
    }

    all_ok = True
    for name, path in required_files.items():
        if path.exists():
            if path.is_dir():
                n_files = len(list(path.glob("*.parquet")))
                print(f"  [OK] {name}: {path} ({n_files} parquet files)")
            else:
                print(f"  [OK] {name}: {path}")
        else:
            print(f"  [MISSING] {name}: {path}")
            all_ok = False

    return all_ok


def main():
    """Main execution"""
    args = parse_arguments()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    config = load_config()
    paths = setup_paths(config, timestamp)

    # Handle output-dir override
    if args.output_dir:
        paths["output_dir"] = Path(args.output_dir)
        ensure_output_dir(paths["output_dir"])

    # Handle dry-run mode
    if args.dry_run:
        print("=" * 60)
        print("STEP 4.2: H2 PRisk x Uncertainty Merge - DRY RUN")
        print(f"Timestamp: {timestamp}")
        print("=" * 60)

        prereq_ok = check_prerequisites(paths, args)
        if prereq_ok:
            print("\n[OK] All prerequisites validated")
            print("\nWould compute:")
            print("  1. Load PRisk from firmquarter_2022q1.csv (tab-separated)")
            print("  2. Load Uncertainty from linguistic variables (2002-2018)")
            print("  3. Load InvestmentResiduals from Plan 53-01 output")
            print("  4. Merge on [gvkey, year]")
            print("  5. Standardize: PRisk_std, Uncertainty_std")
            print(
                "  6. Create interaction: PRisk_x_Uncertainty = PRisk_std * Uncertainty_std"
            )
            print("  7. Validate: correlation matrix, VIF")
            print(f"\nOutput would be written to: {paths['output_dir']}")
            sys.exit(0)
        else:
            print("\n[ERROR] Prerequisites not met")
            sys.exit(1)

    # Check prerequisites
    prereq_ok = check_prerequisites(paths, args)
    if not prereq_ok:
        print("\n[ERROR] Prerequisites not met. Exiting.")
        sys.exit(1)

    # Setup logging with dual-writer
    log_file = open(paths["log_file"], "w", buffering=1)

    import builtins

    builtin_print = builtins.print

    def print_both(*args_log, **kwargs):
        builtin_print(*args_log, **kwargs)
        kwargs.pop("flush", None)
        builtin_print(*args_log, file=log_file, flush=True, **kwargs)

    builtins.print = print_both

    print("=" * 60)
    print("STEP 4.2: H2 PRisk x Uncertainty Merge")
    print(f"Timestamp: {timestamp}")
    print("=" * 60)

    # Initialize statistics
    start_time = time.perf_counter()
    start_iso = datetime.now().isoformat()
    mem_start = get_process_memory_mb()
    memory_readings = [mem_start["rss_mb"]]

    stats = {
        "step_id": "4.2_H2_PRiskUncertaintyMerge",
        "timestamp": timestamp,
        "input": {"files": [], "checksums": {}, "total_rows": 0},
        "processing": {},
        "output": {"final_rows": 0, "files": [], "checksums": {}},
        "variables": {},
        "timing": {"start_iso": start_iso, "end_iso": "", "duration_seconds": 0.0},
        "memory": {
            "start_mb": mem_start["rss_mb"],
            "end_mb": 0.0,
            "peak_mb": 0.0,
            "delta_mb": 0.0,
        },
    }

    # ========================================================================
    # Load Data
    # ========================================================================

    print("\n" + "=" * 60)
    print("LOADING DATA")
    print("=" * 60)

    # Load PRisk
    prisk_file = paths["prisk_file"]
    stats["input"]["files"].append(str(prisk_file))
    stats["input"]["checksums"][prisk_file.name] = compute_file_checksum(prisk_file)

    prisk_df = load_prisk(prisk_file, year_range=(2002, 2018))
    prisk_stats = validate_prisk(prisk_df)
    stats["processing"]["prisk"] = prisk_stats

    # Load Uncertainty
    uncertainty_df = load_uncertainty_measures(
        paths["ling_vars_dir"], year_range=(2002, 2018)
    )
    uncertainty_stats = validate_uncertainty(uncertainty_df)
    stats["processing"]["uncertainty"] = uncertainty_stats

    # Load InvestmentResiduals
    residuals_file = paths["residual_dir"] / "H2_InvestmentResiduals.parquet"
    stats["input"]["files"].append(str(residuals_file))
    stats["input"]["checksums"][residuals_file.name] = compute_file_checksum(
        residuals_file
    )

    investment_df = load_investment_residuals(paths["residual_dir"])
    print(f"\n  Base sample: {len(investment_df):,} observations")

    # ========================================================================
    # Merge and Filter
    # ========================================================================

    print("\n" + "=" * 60)
    print("MERGING DATA")
    print("=" * 60)

    merged_df = merge_all_sources(investment_df, prisk_df, uncertainty_df)
    stats["processing"]["merge"] = {
        "before_merge": len(investment_df),
        "after_merge": len(merged_df),
        "final_sample": len(merged_df),
    }

    # Clean up intermediate dataframes
    del investment_df, prisk_df, uncertainty_df
    gc.collect()

    # Apply sample filters
    filtered_df = apply_sample_filters(
        merged_df, year_range=(2002, 2018), winsorize=True
    )
    stats["processing"]["filters"] = {
        "before_filters": len(merged_df),
        "after_filters": len(filtered_df),
    }

    # ========================================================================
    # Standardize and Create Interaction
    # ========================================================================

    print("\n" + "=" * 60)
    print("STANDARDIZING AND CREATING INTERACTION")
    print("=" * 60)

    # Standardize
    std_df, std_params = standardize_variables(
        filtered_df, columns=["PRisk", "Manager_QA_Uncertainty_pct"]
    )
    stats["processing"]["standardization_params"] = std_params

    # Create interaction term
    interaction_df = create_interaction_term(
        std_df,
        col1="PRisk_std",
        col2="Manager_QA_Uncertainty_pct_std",
        interaction_name="PRisk_x_Uncertainty",
    )

    # Validate interaction
    interaction_validation = validate_interaction(interaction_df)
    stats["processing"]["interaction_validation"] = interaction_validation

    # Clean up
    del filtered_df, std_df
    gc.collect()

    # ========================================================================
    # Prepare Final Dataset
    # ========================================================================

    print("\n" + "=" * 60)
    print("PREPARING FINAL DATASET")
    print("=" * 60)

    final_df = prepare_final_dataset(interaction_df)

    # Sort by gvkey and year
    final_df = final_df.sort_values(["gvkey", "year"]).reset_index(drop=True)

    # Clean up
    del interaction_df
    gc.collect()

    # ========================================================================
    # Write Outputs
    # ========================================================================

    print("\n" + "=" * 60)
    print("WRITING OUTPUTS")
    print("=" * 60)

    # Write parquet
    output_file = paths["output_dir"] / "H2_PRiskUncertainty_Analysis.parquet"
    final_df.to_parquet(output_file, index=False)
    print(f"  Wrote: {output_file.name}")
    stats["output"]["files"].append(output_file.name)
    stats["output"]["checksums"][output_file.name] = compute_file_checksum(output_file)
    stats["output"]["final_rows"] = len(final_df)

    # Add variable statistics
    stats["variables"] = {
        "PRisk_x_Uncertainty": {
            "mean": float(final_df["PRisk_x_Uncertainty"].mean()),
            "std": float(final_df["PRisk_x_Uncertainty"].std()),
            "min": float(final_df["PRisk_x_Uncertainty"].min()),
            "max": float(final_df["PRisk_x_Uncertainty"].max()),
        },
        "InvestmentResidual": {
            "mean": float(final_df["InvestmentResidual"].mean()),
            "std": float(final_df["InvestmentResidual"].std()),
            "min": float(final_df["InvestmentResidual"].min()),
            "max": float(final_df["InvestmentResidual"].max()),
        },
        "sample": {
            "n_obs": len(final_df),
            "n_firms": final_df["gvkey"].nunique(),
            "year_range": [int(final_df["year"].min()), int(final_df["year"].max())],
        },
    }

    # Write stats.json
    save_stats(stats, paths["output_dir"])

    # Update latest/ symlink
    output_base = paths["output_dir"].parent
    latest_link = output_base / "latest"
    if latest_link.exists():
        latest_link.unlink()
    try:
        latest_link.symlink_to(paths["output_dir"])
        print("  Updated latest/ symlink")
    except OSError:
        # Symlink creation may fail on Windows
        pass

    # ========================================================================
    # Final Summary
    # ========================================================================

    end_time = time.perf_counter()
    stats["timing"]["end_iso"] = datetime.now().isoformat()
    stats["timing"]["duration_seconds"] = round(end_time - start_time, 2)

    mem_end = get_process_memory_mb()
    memory_readings.append(mem_end["rss_mb"])
    stats["memory"]["end_mb"] = mem_end["rss_mb"]
    stats["memory"]["peak_mb"] = round(max(memory_readings), 2)
    stats["memory"]["delta_mb"] = round(mem_end["rss_mb"] - mem_start["rss_mb"], 2)

    duration_seconds = end_time - start_time
    if duration_seconds > 0:
        throughput = calculate_throughput(len(final_df), duration_seconds)
        stats["throughput"] = {
            "rows_per_second": throughput,
            "total_rows": len(final_df),
            "duration_seconds": round(duration_seconds, 3),
        }

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Final dataset: {len(final_df):,} observations")
    print(f"  Firms: {final_df['gvkey'].nunique():,}")
    print(f"  Years: {final_df['year'].min()}-{final_df['year'].max()}")
    print("\nKey variables:")
    print(
        f"  PRisk_x_Uncertainty: mean={stats['variables']['PRisk_x_Uncertainty']['mean']:.4f}, std={stats['variables']['PRisk_x_Uncertainty']['std']:.4f}"
    )
    print(
        f"  InvestmentResidual: mean={stats['variables']['InvestmentResidual']['mean']:.4f}, std={stats['variables']['InvestmentResidual']['std']:.4f}"
    )
    print(f"\nOutputs saved to: {paths['output_dir']}")
    print(f"Log saved to: {paths['log_file']}")

    log_file.close()


if __name__ == "__main__":
    main()
