#!/usr/bin/env python3
"""
================================================================================
STEP 3.12: H9 PRisk x CEO Style -> Abnormal Investment (PRiskFY Construction)
================================================================================
ID: 3.12_H9_PRiskFY
Description: Construct PRiskFY (fiscal-year policy risk exposure) at firm-year
             level for H9 regression. PRiskFY aggregates Hassan quarterly PRisk
             data into fiscal-year averages using a 366-day rolling window
             with minimum 2 quarters requirement.

Purpose: Transform quarterly Hassan PRisk data into a firm-year panel format
         matching Compustat fiscal years for merging with StyleFrozen and
         investment variables.

Key Specification:
    PRiskFY_i,t = mean(PRisk quarters) where cal_q_end in (fy_end - 366 days, fy_end]
    Requires >= 2 quarters in averaging window, else set to missing
    NO forward-filling or interpolation of missing values

Inputs:
    - 1_Inputs/FirmLevelRisk/firmquarter_2022q1.csv (Hassan PRisk quarterly data)
    - 1_Inputs/comp_na_daily_all/comp_na_daily_all.parquet (fiscal year-end dates)

Outputs:
    - 4_Outputs/3_Financial_V2/3.12_H9_PRiskFY/{timestamp}/priskfy.parquet
    - 4_Outputs/3_Financial_V2/3.12_H9_PRiskFY/{timestamp}/report_step312_02.md
    - 4_Outputs/3_Financial_V2/3.12_H9_PRiskFY/{timestamp}/stats.json
    - 3_Logs/3_Financial_V2/3.12_H9_PRiskFY/{timestamp}_priskfy.log

Declared Outputs:
    - priskfy.parquet: gvkey, fyear, PRiskFY, n_quarters_used

Deterministic: true
Dependencies:
    - Requires: Step 4.x
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
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, cast

import pandas as pd
import yaml

# Import shared path validation utilities
# Import observability utilities
from f1d.shared.observability_utils import (
    calculate_throughput,
    compute_file_checksum,
    get_process_memory_mb,
    save_stats,
)
from f1d.shared.path_utils import (
    ensure_output_dir,
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
    # Go up from src/f1d/financial/v2/ to project root (5 levels)
    root = Path(__file__).parent.parent.parent.parent.parent

    paths = {
        "root": root,
        "prisk_file": root / "1_Inputs" / "FirmLevelRisk" / "firmquarter_2022q1.csv",
        "compustat_file": root
        / "1_Inputs"
        / "comp_na_daily_all"
        / "comp_na_daily_all.parquet",
    }

    # Output directory
    output_base = root / "4_Outputs" / "3_Financial_V2" / "3.12_H9_PRiskFY"
    paths["output_dir"] = output_base / timestamp
    ensure_output_dir(paths["output_dir"])

    # Log directory
    log_base = root / "3_Logs" / "3_Financial_V2" / "3.12_H9_PRiskFY"
    ensure_output_dir(log_base)
    paths["log_file"] = log_base / f"{timestamp}_priskfy.log"

    return paths


# ==============================================================================
# PRisk Data Loading
# ==============================================================================


def construct_cal_q_end(date_str):
    """
    Convert calendar quarter string "YYYYQq" to quarter-end date.

    Quarter-end dates:
        Q1 -> March 31 (03-31)
        Q2 -> June 30 (06-30)
        Q3 -> September 30 (09-30)
        Q4 -> December 31 (12-31)

    Args:
        date_str: String like "2002q1" or "2002Q1"

    Returns:
        pandas.Timestamp for quarter-end date, or NaT if parsing fails
    """
    try:
        parts = str(date_str).lower().strip().split("q")
        year = int(parts[0])
        quarter = int(parts[1]) if len(parts) > 1 else 1

        # Map quarter to month-end date
        quarter_end_months = {
            1: (3, 31),  # Q1: March 31
            2: (6, 30),  # Q2: June 30
            3: (9, 30),  # Q3: September 30
            4: (12, 31),  # Q4: December 31
        }

        if quarter in quarter_end_months:
            month, day = quarter_end_months[quarter]
            return pd.Timestamp(year=year, month=month, day=day)
        else:
            return pd.NaT

    except (ValueError, AttributeError, IndexError):
        return pd.NaT


def load_prisk_data(prisk_file):
    """
    Load Hassan PRisk quarterly data from firmquarter_2022q1.csv.

    File format: TAB-separated (sep='\t')
    Required columns: gvkey, date (e.g., "2002q1"), PRisk
    Optional columns: NPRisk, PSentiment

    Processing steps:
        1. Read CSV with gvkey, date, PRisk columns
        2. Zero-pad gvkey to 6 characters
        3. Convert date string "YYYYQq" to calendar quarter-end date (cal_q_end)
        4. Create cal_yearq string: "2002Q1", "2002Q2" for uniqueness
        5. Handle duplicates: keep row with max PRisk for each (gvkey, cal_yearq)

    Args:
        prisk_file: Path to firmquarter_2022q1.csv

    Returns:
        DataFrame with gvkey, cal_yearq, cal_q_end, PRisk, [NPRisk, PSentiment]
    """
    print("\n" + "-" * 60)
    print("Loading Hassan PRisk Quarterly Data")
    print("-" * 60)

    if not prisk_file.exists():
        raise FileNotFoundError(f"PRisk file not found: {prisk_file}")

    # Read TAB-separated file - specify dtypes for memory efficiency
    print(f"  Reading: {prisk_file.name}")
    # Read only needed columns to save memory
    usecols = ["gvkey", "date", "PRisk", "NPRisk", "PSentiment"]
    df = pd.read_csv(prisk_file, sep="\t", usecols=usecols)
    print(f"  Loaded: {len(df):,} raw quarterly observations")

    # Normalize gvkey - zero-pad to 6 characters
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)

    # Check required columns
    required_cols = ["gvkey", "date", "PRisk"]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in PRisk data: {missing}")

    # Drop rows with missing PRisk (can't compute without it)
    before_drop = len(df)
    df = df.dropna(subset=["PRisk"])
    if len(df) < before_drop:
        print(f"  Dropped {before_drop - len(df):,} rows with missing PRisk")

    # Construct calendar quarter-end dates (vectorized for speed)
    print("  Constructing cal_q_end from date format 'YYYYQq'...")
    # Vectorized parsing is much faster than apply
    df["cal_q_end"] = pd.to_datetime(
        df["date"].apply(parse_date_quarter), errors="coerce"
    )

    # Check for parsing failures
    n_failed = df["cal_q_end"].isna().sum()
    if n_failed > 0:
        print(f"  [WARNING] Failed to parse {n_failed:,} dates")
        df = df.dropna(subset=["cal_q_end"])

    # Create cal_yearq string for uniqueness (e.g., "2002Q1")
    df["cal_year"] = df["cal_q_end"].dt.year.astype("int16")
    df["cal_quarter"] = df["cal_q_end"].dt.quarter.astype("int8")
    df["cal_yearq"] = df["cal_year"].astype(str) + "Q" + df["cal_quarter"].astype(str)

    # Deduplicate: keep max PRisk for each (gvkey, cal_yearq)
    before_dedup = len(df)
    df = df.sort_values("PRisk", ascending=False).drop_duplicates(
        subset=["gvkey", "cal_yearq"], keep="first"
    )
    n_duplicates = before_dedup - len(df)

    if n_duplicates > 0:
        print(
            f"  Removed {n_duplicates:,} duplicate (gvkey, cal_yearq) rows (kept max PRisk)"
        )

    # Optional: keep NPRisk and PSentiment if available
    optional_cols = ["NPRisk", "PSentiment"]
    available_optional = [col for col in optional_cols if col in df.columns]
    if available_optional:
        print(f"  Included optional columns: {available_optional}")

    output_cols = ["gvkey", "cal_yearq", "cal_q_end", "PRisk"] + available_optional
    df = df.loc[:, output_cols].copy()

    # Downcast numeric types for memory efficiency
    df["PRisk"] = df["PRisk"].astype("float32")
    for col in available_optional:
        if col in df.columns and df[col].dtype in ["float64", "float32"]:
            df[col] = df[col].astype("float32")

    n_firms = df["gvkey"].nunique()
    n_quarters = len(df)

    print(f"  PRisk data: {n_quarters:,} firm-quarter observations ({n_firms:,} firms)")
    print(f"  Date range: {df['cal_q_end'].min()} to {df['cal_q_end'].max()}")

    gc.collect()
    return df


def parse_date_quarter(date_str):
    """
    Parse date string "YYYYQq" to pandas Timestamp.

    Vectorized helper for construct_cal_q_end.
    """
    parts = str(date_str).lower().strip().split("q")
    if len(parts) != 2:
        return None
    try:
        year = int(parts[0])
        quarter = int(parts[1])
        quarter_end_dates = {
            1: (3, 31),
            2: (6, 30),
            3: (9, 30),
            4: (12, 31),
        }
        if quarter in quarter_end_dates:
            month, day = quarter_end_dates[quarter]
            return pd.Timestamp(year=year, month=month, day=day)
    except (ValueError, AttributeError):
        pass
    return None


# ==============================================================================
# Compustat Fiscal Year Grid
# ==============================================================================


def load_compustat_dates(compustat_file, year_range=(2002, 2022)):
    """
    Load Compustat fiscal year-end dates for window construction.

    Reads datadate (fiscal year-end), fyear, gvkey from Compustat.
    Creates unique (gvkey, fyear, datadate) combinations.

    Args:
        compustat_file: Path to comp_na_daily_all.parquet
        year_range: Tuple of (min_year, max_year) for filtering

    Returns:
        DataFrame with gvkey, fyear, datadate (fiscal year-end)
    """
    print("\n" + "-" * 60)
    print("Loading Compustat Fiscal Year Grid")
    print("-" * 60)

    if not compustat_file.exists():
        raise FileNotFoundError(f"Compustat file not found: {compustat_file}")

    print(f"  Reading: {compustat_file.name}")

    # Read parquet - select only needed columns to save memory
    # Note: Compustat uses fyearq (fiscal year from quarterly data)
    cols_to_read = ["gvkey", "datadate", "fyearq"]
    df = pd.read_parquet(compustat_file, columns=cols_to_read)

    print(f"  Loaded: {len(df):,} observations")

    # Normalize gvkey
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)

    # Ensure datadate is datetime
    df["datadate"] = pd.to_datetime(df["datadate"])

    # Rename fyearq to fyear for consistency
    df = df.rename(columns={"fyearq": "fyear"})

    # Ensure fyear is integer
    df["fyear"] = df["fyear"].astype(int)

    # Filter to year range
    df = df.loc[df["fyear"].between(year_range[0], year_range[1]), :].copy()

    # Create unique (gvkey, fyear, datadate) combinations
    # Some firms may have multiple datadates per fyear (rare), keep first
    before_dedup = len(df)
    df = df.drop_duplicates(subset=["gvkey", "fyear"], keep="first")
    if len(df) < before_dedup:
        print(f"  Deduplicated: {before_dedup - len(df):,} rows removed")

    n_firms = df["gvkey"].nunique()
    n_firm_years = len(df)

    print(f"  Fiscal year grid: {n_firm_years:,} firm-years ({n_firms:,} firms)")
    print(f"  Fyear range: {df['fyear'].min()}-{df['fyear'].max()}")

    return df


# ==============================================================================
# PRiskFY Computation (Fiscal-Year Aggregation)
# ==============================================================================


def compute_prisk_fy(
    prisk_df,
    compustat_df,
    min_quarters=2,
    window_days=366,
    temp_dir=None,
    batch_size=1000,
):
    """
    Compute PRiskFY (fiscal-year PRisk) using 366-day rolling window.

    For each firm-year (gvkey, fyear) with fiscal year-end date fy_end:
        1. Define averaging window: (fy_end - window_days, fy_end]
        2. Select PRisk quarters where: lower_bound < cal_q_end <= fy_end
        3. Count quarters in window (n_quarters)
        4. If n_quarters >= min_quarters: PRiskFY = mean(PRisk of quarters)
        5. If n_quarters < min_quarters: PRiskFY = missing (DROP from output)

    KEY: NO forward-filling or interpolation. Missing quarters stay missing.

    Args:
        prisk_df: PRisk quarterly data with gvkey, cal_q_end, PRisk
        compustat_df: Compustat fiscal year grid with gvkey, fyear, datadate
        min_quarters: Minimum quarters required (default: 2)
        window_days: Rolling window size in days (default: 366)
        temp_dir: Directory for intermediate batch files
        batch_size: Number of firm-years per batch before disk write

    Returns:
        DataFrame with gvkey, fyear, datadate, PRiskFY, n_quarters_used
    """
    print("\n" + "-" * 60)
    print("Computing PRiskFY (Fiscal-Year Aggregation)")
    print("-" * 60)
    print(f"  Window: {window_days} days (approximately one year)")
    print(f"  Minimum quarters: {min_quarters}")
    print(f"  Batch size: {batch_size:,} firm-years per batch")

    # Prepare PRisk data for efficient merging - use only needed columns
    prisk_subset = prisk_df[["gvkey", "cal_q_end", "PRisk"]].copy()

    # Convert to smaller data types for memory efficiency
    prisk_subset["PRisk"] = prisk_subset["PRisk"].astype("float32")

    # Setup for batched processing
    temp_files = []
    batch_results = []
    batch_num = 0
    n_total = len(compustat_df)
    n_processed = 0
    n_valid = 0

    print("\n  Processing firm-years...")

    # Process firms in groups to minimize memory
    # First, identify firms with PRisk data (filter early)
    firms_with_prisk = set(prisk_subset["gvkey"].unique())
    compustat_subset = compustat_df[compustat_df["gvkey"].isin(firms_with_prisk)].copy()

    n_firms_filtered = len(compustat_subset) - len(compustat_df)
    print(f"  Filtered out {n_firms_filtered:,} firm-years without PRisk data")

    # Process firm by firm
    for gvkey, compustat_group in compustat_subset.groupby("gvkey"):
        # Get PRisk data for this firm
        firm_prisk = prisk_subset[prisk_subset["gvkey"] == gvkey].copy()

        if len(firm_prisk) == 0:
            continue

        # For each firm-year, find quarters in window
        for _, row in compustat_group.iterrows():
            fy_end = row["datadate"]
            fyear = row["fyear"]
            lower_bound = fy_end - timedelta(days=window_days)

            # Select quarters in window: lower_bound < cal_q_end <= fy_end
            quarters_in_window = firm_prisk[
                (firm_prisk["cal_q_end"] > lower_bound)
                & (firm_prisk["cal_q_end"] <= fy_end)
            ]

            n_quarters = len(quarters_in_window)

            # Apply minimum quarters rule
            if n_quarters >= min_quarters:
                priskfy = float(quarters_in_window["PRisk"].mean())

                batch_results.append(
                    {
                        "gvkey": gvkey,
                        "fyear": int(fyear),
                        "datadate": fy_end,
                        "PRiskFY": priskfy,
                        "n_quarters_used": int(n_quarters),
                    }
                )
                n_valid += 1

            n_processed += 1

            # Periodic progress update
            if n_processed % 10000 == 0:
                print(
                    f"    Processed: {n_processed:,}/{n_total:,} ({n_processed / n_total * 100:.1f}%)"
                )
                # Force garbage collection periodically
                gc.collect()

            # Write batch to disk and clear memory
            if len(batch_results) >= batch_size:
                batch_df = pd.DataFrame(batch_results)
                if temp_dir:
                    temp_file = temp_dir / f"temp_batch_{batch_num:04d}.parquet"
                    batch_df.to_parquet(temp_file, index=False)
                    temp_files.append(temp_file)
                    batch_num += 1
                batch_results.clear()
                gc.collect()

    # Final batch
    if batch_results:
        batch_df = pd.DataFrame(batch_results)
        if temp_dir:
            temp_file = temp_dir / f"temp_batch_{batch_num:04d}.parquet"
            batch_df.to_parquet(temp_file, index=False)
            temp_files.append(temp_file)
        batch_results.clear()
        gc.collect()

    if n_processed % 10000 != 0:
        print(
            f"    Processed: {n_processed:,}/{n_total:,} ({n_processed / n_total * 100:.1f}%)"
        )

    # Combine all batches
    print(f"\n  Combining {len(temp_files)} batches...")
    if temp_files:
        result_df = pd.concat(
            [pd.read_parquet(f) for f in temp_files], ignore_index=True
        )

        # Clean up temp files
        for f in temp_files:
            f.unlink()
        gc.collect()
    else:
        # Should not happen, but handle edge case
        result_df = pd.DataFrame(
            columns=["gvkey", "fyear", "datadate", "PRiskFY", "n_quarters_used"]
        )

    n_firm_years_valid = len(result_df)
    n_firms = result_df["gvkey"].nunique()

    print(f"\n  Valid firm-years: {n_firm_years_valid:,} ({n_firms:,} firms)")
    print(
        f"  Coverage: {n_firm_years_valid}/{n_total} ({n_firm_years_valid / n_total * 100:.1f}%)"
    )

    return result_df


def validate_prisk_fy(df):
    """
    Validate PRiskFY dataset and report statistics.

    Args:
        df: DataFrame with gvkey, fyear, PRiskFY, n_quarters_used

    Returns:
        Dictionary with validation statistics
    """
    print("\n" + "-" * 60)
    print("PRiskFY Validation")
    print("-" * 60)

    if len(df) == 0:
        print("  [ERROR] No valid firm-years in output")
        return {}

    # Basic checks
    n_missing_prisk = df["PRiskFY"].isna().sum()
    n_insufficient_quarters = (df["n_quarters_used"] < 2).sum()

    print(f"  Total observations: {len(df):,}")
    print(f"  Missing PRiskFY: {n_missing_prisk:,}")
    print(f"  Insufficient quarters (< 2): {n_insufficient_quarters:,}")

    if n_missing_prisk > 0:
        print("  [ERROR] Found missing PRiskFY values (should have been dropped)")
    if n_insufficient_quarters > 0:
        print("  [ERROR] Found n_quarters_used < 2 (should have been dropped)")

    # PRiskFY distribution
    print("\n  PRiskFY Distribution:")
    print(f"    Mean: {df['PRiskFY'].mean():.4f}")
    print(f"    Std:  {df['PRiskFY'].std():.4f}")
    print(f"    Min:  {df['PRiskFY'].min():.4f}")
    print(f"    Max:  {df['PRiskFY'].max():.4f}")
    print(f"    p1:   {df['PRiskFY'].quantile(0.01):.4f}")
    print(f"    p5:   {df['PRiskFY'].quantile(0.05):.4f}")
    print(f"    p95:  {df['PRiskFY'].quantile(0.95):.4f}")
    print(f"    p99:  {df['PRiskFY'].quantile(0.99):.4f}")

    # n_quarters_used distribution
    print("\n  n_quarters_used Distribution:")
    quarter_counts = df["n_quarters_used"].value_counts().sort_index()
    for n_q, count in quarter_counts.items():
        pct = count / len(df) * 100
        print(f"    {n_q} quarters: {count:,} ({pct:.1f}%)")

    # Coverage by year
    print("\n  Fyear Coverage:")
    year_counts = df.groupby("fyear").size()
    print(
        f"    Min year: {df['fyear'].min()} (N={year_counts.loc[df['fyear'].min()]:,})"
    )
    print(
        f"    Max year: {df['fyear'].max()} (N={year_counts.loc[df['fyear'].max()]:,})"
    )
    print(f"    Average per year: {year_counts.mean():.0f}")

    stats: Dict[str, Any] = {
        "n_obs": int(len(df)),
        "n_firms": int(df["gvkey"].nunique()),
        "fyear_min": int(df["fyear"].min()),
        "fyear_max": int(df["fyear"].max()),
        "priskfy_mean": float(df["PRiskFY"].mean()),
        "priskfy_std": float(df["PRiskFY"].std()),
        "priskfy_min": float(df["PRiskFY"].min()),
        "priskfy_max": float(df["PRiskFY"].max()),
        "priskfy_p1": float(df["PRiskFY"].quantile(0.01)),
        "priskfy_p99": float(df["PRiskFY"].quantile(0.99)),
        "n_quarters_distribution": quarter_counts.to_dict(),
        "missing_priskfy": int(n_missing_prisk),
        "insufficient_quarters": int(n_insufficient_quarters),
    }

    return stats


# ==============================================================================
# Report Generation
# ==============================================================================


def generate_report(stats, output_dir):
    """
    Generate summary report in Markdown format.

    Args:
        stats: Statistics dictionary
        output_dir: Output directory path
    """
    report_path = output_dir / "report_step312_02.md"

    content = f"""# Step 312-02: PRiskFY Construction Report

**Generated:** {stats.get("timestamp", datetime.now().isoformat())}

---

## Objective

Construct PRiskFY (fiscal-year policy risk exposure) at firm-year level for H9 regression. PRiskFY aggregates Hassan quarterly PRisk data into fiscal-year averages using a 366-day rolling window with minimum 2 quarters requirement.

---

## Methodology

### Data Sources

1. **Hassan PRisk Quarterly Data**
   - File: `1_Inputs/FirmLevelRisk/firmquarter_2022q1.csv`
   - Format: Tab-separated CSV
   - Columns: gvkey, date (e.g., "2002q1"), PRisk

2. **Compustat Fiscal Year Grid**
   - File: `1_Inputs/comp_na_daily_all/comp_na_daily_all.parquet`
   - Columns: gvkey, datadate (fiscal year-end), fyear

### Construction Steps

1. **Load and Clean PRisk Data**
   - Zero-pad gvkey to 6 characters
   - Convert date string "YYYYQq" to calendar quarter-end date (cal_q_end)
   - Q1 -> March 31, Q2 -> June 30, Q3 -> September 30, Q4 -> December 31
   - Create cal_yearq string for uniqueness: "2002Q1", "2002Q2"
   - Handle duplicates: Keep row with max PRisk for each (gvkey, cal_yearq)

2. **Build PRiskFY (Fiscal-Year Aggregation)**
   - For each firm-year (gvkey, fyear) with fiscal year-end date (fy_end = datadate):
     - Define averaging window: (fy_end - 366 days, fy_end]
     - Select PRisk quarters where: lower_bound < cal_q_end <= fy_end
     - Count quarters in window (n_quarters)
     - If n_quarters >= 2: PRiskFY = mean(PRisk of quarters)
     - If n_quarters < 2: PRiskFY = missing, DROP from output

3. **Key Constraints**
   - **NO forward-filling:** Missing quarters stay missing
   - **NO interpolation:** Only use actual available quarters
   - **Minimum 2 quarters:** Firm-years with < 2 quarters excluded
   - **No future data:** Only quarters <= fy_end included in window

---

## Results

### Sample Characteristics

- **Total Observations:** {stats.get("output", {}).get("final_rows", "N/A"):,}
- **Unique Firms:** {stats.get("variables", {}).get("sample", {}).get("n_firms", "N/A"):,}
- **Fyear Range:** {stats.get("variables", {}).get("sample", {}).get("year_range", ["N/A", "N/A"])[0]}-{stats.get("variables", {}).get("sample", {}).get("year_range", ["N/A", "N/A"])[1]}

### PRiskFY Distribution

- **Mean:** {stats.get("variables", {}).get("PRiskFY", {}).get("mean", "N/A")}
- **Std Dev:** {stats.get("variables", {}).get("PRiskFY", {}).get("std", "N/A")}
- **Min:** {stats.get("variables", {}).get("PRiskFY", {}).get("min", "N/A")}
- **Max:** {stats.get("variables", {}).get("PRiskFY", {}).get("max", "N/A")}
- **1st percentile:** {stats.get("variables", {}).get("PRiskFY", {}).get("p1", "N/A")}
- **99th percentile:** {stats.get("variables", {}).get("PRiskFY", {}).get("p99", "N/A")}

### Quarters Used Distribution

{_format_quarter_dist(stats.get("variables", {}).get("n_quarters_distribution", {}))}

### Data Quality Checks

- **Missing PRiskFY:** {stats.get("variables", {}).get("missing_priskfy", "N/A"):,} (should be 0)
- **Insufficient quarters (< 2):** {stats.get("variables", {}).get("insufficient_quarters", "N/A"):,} (should be 0)

---

## Output Files

1. **priskfy.parquet** - Main dataset with columns:
   - gvkey: Firm identifier (6-digit, zero-padded)
   - fyear: Fiscal year
   - datadate: Fiscal year-end date
   - PRiskFY: Fiscal-year policy risk exposure
   - n_quarters_used: Number of quarters in averaging window

2. **stats.json** - Detailed statistics and metadata

3. **report_step312_02.md** - This report

---

## Next Steps

This PRiskFY dataset will be merged with:
- StyleFrozen (from 3.11): CEO communication style at firm-year level
- AbsAbInv + Controls (from 3.13): Biddle abnormal investment measures

The merged dataset will be used for H9 regression:
```
AbsAbInv_(i,t+1) = beta0 + beta1*PRiskFY_(i,t) + beta2*StyleFrozen_(i,t)
                + beta3*(PRiskFY_(i,t) x StyleFrozen_(i,t))
                + gamma'*Controls_(i,t)
                + FirmFE_i + YearFE_t + epsilon
```

---

*Step 312-02: PRiskFY Construction*
"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"\n  Wrote report: {report_path.name}")


def _format_quarter_dist(quarter_dist):
    """Helper to format quarter distribution for report"""
    if not quarter_dist:
        return "N/A"

    lines = []
    for n_q in sorted(quarter_dist.keys()):
        count = quarter_dist[n_q]
        lines.append(f"- **{n_q} quarters:** {count:,} observations")
    return "\n".join(lines)


# ==============================================================================
# CLI and Main
# ==============================================================================


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="""
STEP 3.12: H9 PRisk x CEO Style -> Abnormal Investment (PRiskFY Construction)

Construct PRiskFY (fiscal-year policy risk exposure) at firm-year level.
PRiskFY aggregates Hassan quarterly PRisk data into fiscal-year averages
using a 366-day rolling window with minimum 2 quarters requirement.

Key Specification:
    PRiskFY_i,t = mean(PRisk quarters) where cal_q_end in (fy_end - 366 days, fy_end]
    Requires >= 2 quarters in averaging window, else set to missing
    NO forward-filling or interpolation
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
        help="Validate inputs and print plan without executing",
    )

    parser.add_argument(
        "--min-quarters",
        type=int,
        default=2,
        help="Minimum quarters required for PRiskFY (default: 2)",
    )

    parser.add_argument(
        "--window-days",
        type=int,
        default=366,
        help="Rolling window size in days (default: 366)",
    )

    parser.add_argument(
        "--prisk-var",
        type=str,
        default="PRisk",
        help="PRisk variable name (default: PRisk)",
    )

    return parser.parse_args()


def check_prerequisites(paths, args):
    """Validate all required inputs exist"""
    print("\nChecking prerequisites...")

    required_files = {
        "PRisk data": paths["prisk_file"],
        "Compustat": paths["compustat_file"],
    }

    all_ok = True
    for name, path in required_files.items():
        if path.exists():
            size_mb = path.stat().st_size / (1024**2)
            print(f"  [OK] {name}: {path} ({size_mb:.1f} MB)")
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
        print("STEP 3.12: H9 PRiskFY Construction - DRY RUN")
        print(f"Timestamp: {timestamp}")
        print("=" * 60)

        prereq_ok = check_prerequisites(paths, args)
        if prereq_ok:
            print("\n[OK] All prerequisites validated")
            print("\nWould compute:")
            print("  1. Load Hassan PRisk quarterly data from firmquarter_2022q1.csv")
            print("  2. Construct cal_q_end from 'YYYYQq' format")
            print("  3. Deduplicate (gvkey, cal_yearq) keeping max PRisk")
            print("  4. Load Compustat fiscal year-end dates")
            print("  5. For each firm-year:")
            print(
                f"     - Define {args.window_days}-day window: (fy_end - {args.window_days}d, fy_end]"
            )
            print(
                f"     - Select quarters in window (min {args.min_quarters} required)"
            )
            print("     - Compute PRiskFY = mean(PRisk of quarters)")
            print("  6. Validate: no missing values, all n_quarters_used >= 2")
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
    print("STEP 3.12: H9 PRiskFY Construction")
    print(f"Timestamp: {timestamp}")
    print("=" * 60)

    # Initialize statistics
    start_time = time.perf_counter()
    start_iso = datetime.now().isoformat()
    mem_start = get_process_memory_mb()
    memory_readings = [mem_start["rss_mb"]]

    stats: Dict[str, Any] = {
        "step_id": "3.12_H9_PRiskFY",
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

    # Load PRisk data
    prisk_file = paths["prisk_file"]
    stats["input"]["files"].append(str(prisk_file))
    stats["input"]["checksums"][prisk_file.name] = compute_file_checksum(prisk_file)

    prisk_df = load_prisk_data(prisk_file)
    stats["processing"]["prisk"] = {
        "n_raw_quarters": len(prisk_df),
        "n_firms": int(prisk_df["gvkey"].nunique()),
        "date_range": [
            str(prisk_df["cal_q_end"].min()),
            str(prisk_df["cal_q_end"].max()),
        ],
    }

    # Load Compustat
    compustat_file = paths["compustat_file"]
    stats["input"]["files"].append(str(compustat_file))
    stats["input"]["checksums"][compustat_file.name] = compute_file_checksum(
        compustat_file
    )

    compustat_df = load_compustat_dates(compustat_file, year_range=(2002, 2022))
    stats["processing"]["compustat"] = {
        "n_firm_years": len(compustat_df),
        "n_firms": int(compustat_df["gvkey"].nunique()),
    }

    # ========================================================================
    # Compute PRiskFY
    # ========================================================================

    print("\n" + "=" * 60)
    print("COMPUTING PRISKFY")
    print("=" * 60)

    # Create temp directory for batched processing
    temp_dir = paths["output_dir"] / "temp_batches"
    ensure_output_dir(temp_dir)

    priskfy_df = compute_prisk_fy(
        prisk_df,
        compustat_df,
        min_quarters=args.min_quarters,
        window_days=args.window_days,
        temp_dir=temp_dir,
        batch_size=2000,  # Process 2000 firm-years per batch
    )

    # Clean up intermediate dataframes
    del prisk_df, compustat_df
    gc.collect()

    # ========================================================================
    # Validate
    # ========================================================================

    print("\n" + "=" * 60)
    print("VALIDATING OUTPUT")
    print("=" * 60)

    validation_stats = validate_prisk_fy(priskfy_df)
    stats["variables"] = validation_stats

    # Add sample info
    stats["variables"]["sample"] = {
        "n_obs": len(priskfy_df),
        "n_firms": priskfy_df["gvkey"].nunique(),
        "year_range": [int(priskfy_df["fyear"].min()), int(priskfy_df["fyear"].max())],
    }

    # Add PRiskFY stats
    stats["variables"]["PRiskFY"] = {
        "mean": float(priskfy_df["PRiskFY"].mean()),
        "std": float(priskfy_df["PRiskFY"].std()),
        "min": float(priskfy_df["PRiskFY"].min()),
        "max": float(priskfy_df["PRiskFY"].max()),
        "p1": float(priskfy_df["PRiskFY"].quantile(0.01)),
        "p99": float(priskfy_df["PRiskFY"].quantile(0.99)),
    }

    # Sort by gvkey and fyear
    priskfy_df = priskfy_df.sort_values(["gvkey", "fyear"]).reset_index(drop=True)

    # ========================================================================
    # Write Outputs
    # ========================================================================

    print("\n" + "=" * 60)
    print("WRITING OUTPUTS")
    print("=" * 60)

    # Write parquet
    output_file = paths["output_dir"] / "priskfy.parquet"
    priskfy_df.to_parquet(output_file, index=False)
    print(f"  Wrote: {output_file.name}")
    stats["output"]["files"].append(output_file.name)
    stats["output"]["checksums"][output_file.name] = compute_file_checksum(output_file)
    stats["output"]["final_rows"] = len(priskfy_df)

    # Write stats.json
    save_stats(stats, paths["output_dir"])

    # Generate report
    generate_report(stats, paths["output_dir"])

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
        throughput = calculate_throughput(len(priskfy_df), duration_seconds)
        stats["throughput"] = {
            "rows_per_second": throughput,
            "total_rows": len(priskfy_df),
            "duration_seconds": round(duration_seconds, 3),
        }

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Output dataset: {len(priskfy_df):,} observations")
    print(f"  Firms: {priskfy_df['gvkey'].nunique():,}")
    print(f"  Fyears: {priskfy_df['fyear'].min()}-{priskfy_df['fyear'].max()}")
    print("\nPRiskFY statistics:")
    print(f"  Mean: {stats['variables']['PRiskFY']['mean']:.4f}")
    print(f"  Std:  {stats['variables']['PRiskFY']['std']:.4f}")
    print(f"  Min:  {stats['variables']['PRiskFY']['min']:.4f}")
    print(f"  Max:  {stats['variables']['PRiskFY']['max']:.4f}")
    print(f"\nOutputs saved to: {paths['output_dir']}")
    print(f"Log saved to: {paths['log_file']}")

    log_file.close()


if __name__ == "__main__":
    main()
