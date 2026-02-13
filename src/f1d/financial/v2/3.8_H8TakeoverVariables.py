#!/usr/bin/env python3
"""
==============================================================================
STEP 3.8: H8 Takeover Variables
==============================================================================
ID: 3.8_H8TakeoverVariables
Description: Construct takeover target indicator for H8 (Speech Uncertainty ->
             Takeover Target Probability). Uses SDC Platinum M&A data.

Model Specification (H8):
    logit(P(Takeover_{t+1}=1)) = beta0 + beta1*Uncertainty_t + gamma*Controls

Hypothesis:
    H8a: beta1 > 0 (Higher uncertainty -> Higher takeover probability)

Inputs:
    - SDC Platinum M&A data (1_Inputs/SDC/sdc-ma-merged.parquet)
    - V2 speech uncertainty measures (from 4_Outputs/2_Textual_Analysis/)
    - V2 firm controls (from 4_Outputs/3_Financial_Features/)
    - Sample manifest (from 4_Outputs/1.4_AssembleManifest/)

Outputs:
    - 4_Outputs/3_Financial_V2/{timestamp}/H8_Takeover.parquet
    - 4_Outputs/3_Financial_V2/{timestamp}/stats.json

Deterministic: true
Dependencies:
    - Requires: Step 2.2
    - Uses: shared.financial_utils, pandas, numpy

Author: Thesis Author
Date: 2026-02-11
==============================================================================
"""

import argparse
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import pandas as pd

# Configure logger for this module
logger = logging.getLogger(__name__)

# Add parent directory to sys.path for shared module imports
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir))

# Import shared path validation utilities
# Import DualWriter from f1d.shared.observability_utils
from f1d.shared.observability_utils import (
    DualWriter,
    calculate_throughput,
    compute_file_checksum,
    detect_anomalies_zscore,
    get_process_memory_mb,
    print_stats_summary,
    save_stats,
)
from f1d.shared.path_utils import (
    ensure_output_dir,
    get_latest_output_dir,
)

# ==============================================================================
# Configuration
# ==============================================================================

# H8 Takeover Variables Configuration
CONFIG: Dict[str, Any] = {
    "year_start": 2002,
    "year_end": 2018,
    "sdc_file": "1_Inputs/SDC/sdc-ma-merged.parquet",
    "min_firm_years": 3,
    "winsor_lower": 0.01,
    "winsor_upper": 0.99,
    # Takeover rate validation thresholds
    "takeover_rate_min": 0.005,  # 0.5% minimum annual takeover rate
    "takeover_rate_max": 0.05,  # 5% maximum annual takeover rate
    "min_takeover_events": 100,  # Minimum takeover events in sample
}

# Takeover type definitions
TAKEOVER_TYPES = {
    "primary": "completed",  # Completed deals (primary)
    "announced": "announced",  # Announced deals (robustness)
    "hostile": "hostile",  # Hostile/unsolicited deals (robustness)
}

# M&A prediction literature control variables
MNA_CONTROL_VARS = [
    "size",  # Firm size (log assets or market cap)
    "leverage",  # Debt / Assets
    "roa",  # Return on Assets
    "mtb",  # Market-to-book ratio
    "liquidity",  # Current ratio or quick ratio
    "efficiency",  # Asset turnover (Sales / Assets)
    "stock_ret",  # Stock returns (abnormal returns)
    "rd_intensity",  # R&D / Assets (if available)
]

# ==============================================================================
# Path Setup
# ==============================================================================


def setup_paths(timestamp):
    """Set up all required paths"""
    root = Path(__file__).parent.parent.parent

    # Resolve manifest directory using timestamp-based resolution
    try:
        manifest_dir = get_latest_output_dir(
            root / "4_Outputs" / "1.4_AssembleManifest",
            required_file="master_sample_manifest.parquet",
        )
    except Exception:
        # Fallback to 1.0_BuildSampleManifest
        manifest_dir = get_latest_output_dir(
            root / "4_Outputs" / "1.0_BuildSampleManifest",
            required_file="master_sample_manifest.parquet",
        )

    # Resolve H7 illiquidity output (for base dataset with uncertainty measures)
    # Find directory containing H7_Illiquidity.parquet
    v2_base = root / "4_Outputs" / "3_Financial_V2"
    h7_dir = None
    if v2_base.exists():
        for d in sorted(v2_base.iterdir(), reverse=True):
            if d.is_dir() and (d / "H7_Illiquidity.parquet").exists():
                h7_dir = d
                break

    if h7_dir is None:
        raise FileNotFoundError(f"H7_Illiquidity.parquet not found in {v2_base}")

    paths = {
        "root": root,
        "manifest_dir": manifest_dir,
        "h7_dir": h7_dir,
        "sdc_file": root / CONFIG["sdc_file"],
        "ccm_file": root
        / "1_Inputs"
        / "CRSPCompustat_CCM"
        / "CRSPCompustat_CCM.parquet",
    }

    # Output directory
    output_base = root / "4_Outputs" / "3_Financial_V2"
    paths["output_dir"] = output_base / timestamp
    ensure_output_dir(paths["output_dir"])

    # Log directory
    log_base = root / "3_Logs" / "3_Financial_V2"
    ensure_output_dir(log_base)
    paths["log_file"] = log_base / f"{timestamp}_H8.log"

    return paths


# ==============================================================================
# Data Loading Functions
# ==============================================================================


def load_sdc_data(sdc_path, year_start, year_end):
    """
    Load and process SDC Platinum M&A data.

    Creates binary takeover indicator at firm-year level.

    Args:
        sdc_path: Path to SDC parquet file
        year_start, year_end: Sample period

    Returns:
        DataFrame with gvkey (from CUSIP), year, and takeover indicators
    """
    print("\nLoading SDC M&A data...")

    # Load SDC data
    df = pd.read_parquet(sdc_path)
    print(f"  Loaded SDC: {len(df):,} deals")

    # Key SDC fields from actual data:
    # - Target 6-digit CUSIP (target identifier)
    # - Date Announced (announcement date)
    # - Deal Status (Completed, Pending, Withdrawn, etc.)
    # - Deal Attitude (Friendly, Hostile, Unsolicited, Neutral, No Applicable)
    # - Target Public Status (Public, Private, Subsidiary, etc.)
    # - Deal Value (USD Millions)

    # Filter to required columns
    required_cols = [
        "Target 6-digit CUSIP",
        "Date Announced",
        "Date Effective",
        "Deal Status",
        "Deal Attitude",
        "Target Public Status",
        "Deal Value (USD Millions)",
    ]

    # Check which columns exist
    available_cols = [c for c in required_cols if c in df.columns]
    df = df[available_cols].copy()

    # Convert date and extract year
    df["Date Announced"] = pd.to_datetime(df["Date Announced"])
    df["year"] = df["Date Announced"].dt.year

    # Filter to sample period
    df = df[df["year"].between(year_start, year_end)]
    print(f"  Filtered to {year_start}-{year_end}: {len(df):,} deals")

    # Filter to public targets only (our sample is public firms)
    if "Target Public Status" in df.columns:
        df_public = df[df["Target Public Status"] == "Public"].copy()
        print(f"  Public targets: {len(df_public):,} deals")
    else:
        df_public = df.copy()
        print("  Warning: Target Public Status not available, using all deals")

    # Create takeover indicators
    # Primary: Completed deals
    if "Deal Status" in df_public.columns:
        df_public["takeover_completed"] = (
            df_public["Deal Status"] == "Completed"
        ).astype(int)
        completed_count = df_public["takeover_completed"].sum()
        print(f"  Completed deals: {completed_count:,}")
    else:
        df_public["takeover_completed"] = 1  # All rows are announced
        print("  Warning: Deal Status not available, using all as completed")

    # Robustness 1: All announced deals
    df_public["takeover_announced"] = 1  # All rows are announced by definition

    # Robustness 2: Hostile/unsolicited deals
    if "Deal Attitude" in df_public.columns:
        hostile_indicators = ["Hostile", "Unsolicited"]
        df_public["takeover_hostile"] = (
            df_public["Deal Attitude"].isin(hostile_indicators).astype(int)
        )
        hostile_count = df_public["takeover_hostile"].sum()
        print(f"  Hostile/unsolicited deals: {hostile_count:,}")
    else:
        df_public["takeover_hostile"] = 0
        print("  Warning: Deal Attitude not available, hostile = 0")

    # Aggregate to CUSIP-year level (1 if any takeover in year)
    # We use CUSIP as identifier; will map to GVKEY later
    takeover = (
        df_public.groupby(["Target 6-digit CUSIP", "year"])
        .agg(
            {
                "takeover_completed": "max",
                "takeover_announced": "max",
                "takeover_hostile": "max",
            }
        )
        .reset_index()
    )

    takeover = takeover.rename(columns={"Target 6-digit CUSIP": "cusip"})

    print(f"  Aggregated to {len(takeover):,} CUSIP-year observations")

    return takeover


def load_h7_data(h7_path):
    """
    Load H7 illiquidity data as base dataset.

    This dataset already contains:
    - gvkey, year
    - Uncertainty measures (Manager_QA_Uncertainty_pct, CEO_QA_Uncertainty_pct, etc.)
    - Some controls (Volatility, StockRet)

    Args:
        h7_path: Path to H7_Illiquidity.parquet

    Returns:
        DataFrame with gvkey, year, and IVs
    """
    print("\nLoading H7 illiquidity data (base with uncertainty measures)...")

    df = pd.read_parquet(h7_path)
    print(f"  Loaded H7: {len(df):,} observations")

    # Ensure gvkey is string
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)

    return df


def load_ccm_link(ccm_path):
    """
    Load CRSP-Compustat link table for CUSIP-GVKEY mapping.

    Creates a mapping from 6-digit CUSIP to GVKEY using the CCM link table.
    Filters to primary links (LINKPRIM='P' or 'C') and active links.

    Args:
        ccm_path: Path to CRSPCompustat_CCM.parquet

    Returns:
        DataFrame with cusip6, gvkey mapping
    """
    print("\nLoading CRSP-Compustat CCM link table...")

    ccm = pd.read_parquet(ccm_path)
    print(f"  Loaded CCM: {len(ccm):,} link records")

    # Standardize column names (handle case variations)
    ccm.columns = [c.lower() for c in ccm.columns]

    # Ensure cusip is 6-digit string
    if "cusip" in ccm.columns:
        ccm["cusip"] = ccm["cusip"].astype(str).str[:6].str.upper()
        # Filter out invalid CUSIPs
        ccm = ccm[~ccm["cusip"].isin(["nan", "none", ""])]
    else:
        raise ValueError("CCM data missing 'cusip' column")

    # Filter to primary links (LINKPRIM='P' or 'C')
    if "linkprim" in ccm.columns:
        ccm = ccm[ccm["linkprim"].isin(["P", "C", "p", "c"])]
        print(f"  Filtered to primary links: {len(ccm):,}")

    # Get most recent GVKEY for each CUSIP (in case of multiple matches)
    ccm_map = ccm.groupby("cusip")["gvkey"].last().reset_index()
    ccm_map.columns = ["cusip6", "gvkey"]
    ccm_map["gvkey"] = ccm_map["gvkey"].astype(str).str.zfill(6)

    print(f"  Unique CUSIP-GVKEY mappings: {len(ccm_map):,}")

    return ccm_map


def create_forward_takeover(takeover_df):
    """
    Create forward-looking takeover indicator.

    Takeover_{t+1} indicates whether firm becomes target in NEXT year.
    This allows for causal interpretation: uncertainty_t affects takeover_{t+1}.

    Args:
        takeover_df: DataFrame with takeover indicators

    Returns:
        DataFrame with added takeover_fwd column
    """
    print("\nCreating forward-looking takeover indicator (t -> t+1)...")

    takeover_df = takeover_df.sort_values(["cusip", "year"])
    takeover_df["takeover_fwd"] = takeover_df.groupby("cusip")[
        "takeover_completed"
    ].shift(-1)
    takeover_df["takeover_fwd"] = takeover_df["takeover_fwd"].fillna(0).astype(int)

    # Also create forward versions of alternative definitions
    takeover_df["takeover_announced_fwd"] = takeover_df.groupby("cusip")[
        "takeover_announced"
    ].shift(-1)
    takeover_df["takeover_announced_fwd"] = (
        takeover_df["takeover_announced_fwd"].fillna(0).astype(int)
    )

    takeover_df["takeover_hostile_fwd"] = takeover_df.groupby("cusip")[
        "takeover_hostile"
    ].shift(-1)
    takeover_df["takeover_hostile_fwd"] = (
        takeover_df["takeover_hostile_fwd"].fillna(0).astype(int)
    )

    n_takeovers = takeover_df["takeover_fwd"].sum()
    takeover_rate = takeover_df["takeover_fwd"].mean()
    print(f"  Forward takeover events (t+1): {n_takeovers:,}")
    print(f"  Takeover rate: {takeover_rate:.2%}")

    return takeover_df


def load_firm_controls(firm_controls_dir, year_start, year_end):
    """
    Load and merge firm controls from V2 pipeline.

    Args:
        firm_controls_dir: Path to firm controls directory
        year_start, year_end: Sample period

    Returns:
        DataFrame with firm controls at gvkey-year level
    """
    print("\nLoading firm controls...")

    # Find all firm_controls_*.parquet files
    control_files = sorted(firm_controls_dir.glob("firm_controls_*.parquet"))

    if not control_files:
        print("  Warning: No firm_controls files found")
        return pd.DataFrame()

    dfs = []
    for f in control_files:
        df = pd.read_parquet(f)
        dfs.append(df)

    combined = pd.concat(dfs, ignore_index=True)
    print(f"  Combined firm controls: {len(combined):,} rows")

    # Ensure gvkey is string
    combined["gvkey"] = combined["gvkey"].astype(str).str.zfill(6)

    # Filter to sample period
    combined = combined[combined["year"].between(year_start, year_end)]

    return combined


def merge_h8_data(takeover_df, h7_df, controls_df, manifest_df, ccm_map):
    """
    Merge takeover data with uncertainty and controls.

    Args:
        takeover_df: SDC takeover data (with cusip, year)
        h7_df: H7 data with uncertainty measures (with gvkey, year)
        controls_df: Firm controls
        manifest_df: Sample manifest for filtering
        ccm_map: CUSIP-GVKEY mapping from CCM link table

    Returns:
        Analysis-ready dataset for H8
    """
    print("\n" + "=" * 60)
    print("Merging H8 Data")
    print("=" * 60)

    # Step 1: Prepare manifest for GVKEY filtering
    print("\nStep 1: Preparing manifest for sample firms...")
    # Add year to manifest from start_date
    manifest_df = manifest_df.copy()
    manifest_df["start_date"] = pd.to_datetime(manifest_df["start_date"])
    manifest_df["year"] = manifest_df["start_date"].dt.year

    # Get sample GVKEYs
    sample_gvkeys = manifest_df["gvkey"].unique()
    print(f"  Sample firms: {len(sample_gvkeys):,}")

    # Step 2: Map takeover CUSIPs to GVKEYs using CCM link table
    print("\nStep 2: Mapping CUSIPs to GVKEYs using CCM...")
    print(f"  CCM mappings available: {len(ccm_map):,}")

    # Merge takeover data with CCM mapping
    takeover_with_gvkey = takeover_df.merge(
        ccm_map, left_on="cusip", right_on="cusip6", how="inner"
    )
    print(f"  Matched CUSIPs: {len(takeover_with_gvkey):,} observations")
    print(f"  Unique GVKEYs: {takeover_with_gvkey['gvkey'].nunique():,}")

    # Create forward-looking takeover indicator at firm-year level
    takeover_with_gvkey = takeover_with_gvkey.sort_values(["gvkey", "year"])
    takeover_with_gvkey["takeover_fwd"] = takeover_with_gvkey.groupby("gvkey")[
        "takeover_completed"
    ].shift(-1)
    takeover_with_gvkey["takeover_fwd"] = (
        takeover_with_gvkey["takeover_fwd"].fillna(0).astype(int)
    )

    # Aggregate to firm-year level (1 if any takeover in year)
    takeover_firm_year = (
        takeover_with_gvkey.groupby(["gvkey", "year"])
        .agg(
            {
                "takeover_fwd": "max",
                "takeover_announced": "max",
                "takeover_hostile": "max",
            }
        )
        .reset_index()
    )

    print(f"  Firm-year takeover observations: {len(takeover_firm_year):,}")
    print(f"  Takeover events (t+1): {takeover_firm_year['takeover_fwd'].sum():,}")

    # Also create market-wide takeover rate for robustness
    takeover_by_year = (
        takeover_with_gvkey.groupby("year")
        .agg({"takeover_fwd": "mean", "gvkey": "count"})
        .reset_index()
    )
    takeover_by_year.columns = ["year", "takeover_rate_year", "n_takeovers_year"]
    print(
        f"  Annual takeover rate range: {takeover_by_year['takeover_rate_year'].min():.2%} - {takeover_by_year['takeover_rate_year'].max():.2%}"
    )

    # Step 3: Start with H7 data (has uncertainty measures and some controls)
    print("\nStep 3: Preparing H7 base data...")
    h8_df = h7_df.copy()

    # Select H7 columns we need
    h7_cols = ["gvkey", "year"]
    # Add uncertainty measures
    uncertainty_cols = [c for c in h7_df.columns if "Uncertainty_pct" in c]
    h7_cols.extend(uncertainty_cols)
    # Add existing controls
    control_cols = [
        c for c in h7_df.columns if c in ["Volatility", "StockRet", "trading_days"]
    ]
    h7_cols.extend(control_cols)

    h8_df = h7_df[h7_cols].copy()
    print(f"  H7 base: {len(h8_df):,} observations")

    # Step 4: Merge firm-level takeover indicators
    print("\nStep 4: Merging firm-level takeover indicators...")

    h8_df = h8_df.merge(takeover_firm_year, on=["gvkey", "year"], how="left")
    h8_df = h8_df.merge(takeover_by_year, on="year", how="left")

    # Fill missing takeover_fwd with 0 (not a target)
    h8_df["takeover_fwd"] = h8_df["takeover_fwd"].fillna(0).astype(int)
    h8_df["takeover_announced"] = h8_df["takeover_announced"].fillna(0).astype(int)
    h8_df["takeover_hostile"] = h8_df["takeover_hostile"].fillna(0).astype(int)

    n_takeovers = h8_df["takeover_fwd"].sum()
    takeover_rate = h8_df["takeover_fwd"].mean()
    print(
        f"  Firms with takeover data: {(h8_df['takeover_fwd'].notna() | (h8_df['takeover_fwd'] == 0)).sum():,}"
    )
    print(f"  Takeover targets (t+1): {n_takeovers:,}")
    print(f"  Takeover rate: {takeover_rate:.2%}")

    # Step 5: Merge additional firm controls if available
    if controls_df is not None and len(controls_df) > 0:
        print("\nStep 5: Merging additional firm controls...")
        # Get control columns that exist
        available_controls = []
        for cv in MNA_CONTROL_VARS:
            # Map generic names to actual column names
            if cv == "size" and "Size" in controls_df.columns:
                available_controls.append("Size")
            elif cv == "leverage" and "Lev" in controls_df.columns:
                available_controls.append("Lev")
            elif cv == "roa" and "ROA" in controls_df.columns:
                available_controls.append("ROA")
            elif cv == "mtb" and "BM" in controls_df.columns:
                available_controls.append("BM")
            elif cv == "liquidity" and "CurrentRatio" in controls_df.columns:
                available_controls.append("CurrentRatio")
            elif cv == "efficiency" and "Efficiency" in controls_df.columns:
                available_controls.append("Efficiency")
            elif cv == "stock_ret" and "StockRet" in controls_df.columns:
                available_controls.append("StockRet")
            elif cv == "rd_intensity" and "RD_Intensity" in controls_df.columns:
                available_controls.append("RD_Intensity")

        if available_controls:
            controls_merge = controls_df[
                ["gvkey", "year"] + available_controls
            ].drop_duplicates()
            h8_df = h8_df.merge(controls_merge, on=["gvkey", "year"], how="left")
            print(f"  Merged controls: {available_controls}")

    # Step 6: Filter to sample firms
    print("\nStep 6: Filtering to sample firms...")
    h8_df = h8_df[h8_df["gvkey"].isin(sample_gvkeys)]
    print(f"  After sample filter: {len(h8_df):,} observations")

    # Step 7: Apply missing data handling
    print("\nStep 7: Handling missing data...")

    # For logistic regression, require DV and primary IV
    required_vars = ["takeover_fwd"]  # Now we have firm-level takeover data
    primary_iv = (
        "Manager_QA_Uncertainty_pct"
        if "Manager_QA_Uncertainty_pct" in h8_df.columns
        else uncertainty_cols[0]
        if uncertainty_cols
        else None
    )
    if primary_iv:
        required_vars.append(primary_iv)

    if required_vars:
        n_before_missing = len(h8_df)
        h8_df = h8_df.dropna(subset=required_vars)
        n_after_missing = len(h8_df)
        print(
            f"  Dropped {n_before_missing - n_after_missing:,} observations with missing IV/DV"
        )

    # For controls, require at least 80% availability
    control_cols_in_df = [
        c
        for c in h8_df.columns
        if c
        in [
            "Size",
            "Lev",
            "ROA",
            "BM",
            "CurrentRatio",
            "Efficiency",
            "StockRet",
            "RD_Intensity",
            "Volatility",
        ]
    ]
    if control_cols_in_df:
        h8_df["n_missing_controls"] = h8_df[control_cols_in_df].isna().sum(axis=1)
        max_missing = len(control_cols_in_df) * 0.2  # Allow up to 20% missing
        h8_df = h8_df[h8_df["n_missing_controls"] <= max_missing].copy()
        print("  Dropped observations with >20% missing controls")
        h8_df = h8_df.drop(columns=["n_missing_controls"])

    print(f"  Final sample: {len(h8_df):,} observations")

    # Validate takeover variation
    takeover_var = h8_df["takeover_fwd"].var()
    if takeover_var == 0:
        print("  WARNING: No variation in takeover_fwd (all zeros)")
        print("  Regression will not be possible without takeover events")
    else:
        print(f"  Takeover_fwd variance: {takeover_var:.6f}")

    return h8_df


def apply_sample_construction(df, config):
    """
    Apply sample construction filters.

    - Exclude financial firms (if SIC available)
    - Exclude utilities (if SIC available)
    - Require minimum firm years (not implemented without additional data)

    Args:
        df: Input dataframe
        config: Configuration dict

    Returns:
        Filtered dataframe
    """
    print("\n" + "=" * 60)
    print("Applying Sample Construction")
    print("=" * 60)

    len(df)

    # For H8, we rely on H7 sample which already has exclusions applied
    print("  Using H7 sample (exclusions already applied)")
    print(f"  Sample: {len(df):,} firm-year observations")

    # Count unique firms and years
    n_firms = df["gvkey"].nunique()
    n_years = df["year"].nunique()
    year_range = f"{df['year'].min()}-{df['year'].max()}"

    print(f"  Firms: {n_firms:,}")
    print(f"  Years: {n_years} ({year_range})")

    return df


def winsorize_series(s, lower=0.01, upper=0.99):
    """
    Winsorize a series at specified percentiles.

    Args:
        s: Series to winsorize
        lower: Lower percentile (default: 0.01)
        upper: Upper percentile (default: 0.99)

    Returns:
        Winsorized series
    """
    if s.notna().sum() == 0:
        return s

    lower_bound = s.quantile(lower)
    upper_bound = s.quantile(upper)
    return s.clip(lower=lower_bound, upper=upper_bound)


# ==============================================================================
# CLI and Prerequisites
# ==============================================================================


def parse_arguments():
    """Parse command-line arguments for 3.8_H8TakeoverVariables.py."""
    parser = argparse.ArgumentParser(
        description="""
STEP 3.8: H8 Takeover Variables

Construct takeover target indicator for H8 hypothesis testing.
Creates dependent variable (takeover target at t+1) and merges
with speech uncertainty measures and M&A control variables.
        """.strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and prerequisites without executing",
    )

    return parser.parse_args()


def check_prerequisites(paths):
    """Validate all required inputs and prerequisite steps exist."""
    print("\nChecking prerequisites...")

    required_files = {
        "SDC M&A data": paths["sdc_file"],
        "Manifest": paths["manifest_dir"] / "master_sample_manifest.parquet",
        "H7 Illiquidity": paths["h7_dir"] / "H7_Illiquidity.parquet",
    }

    all_ok = True
    for name, path in required_files.items():
        path_exists = (
            path.exists()
            if not isinstance(path, dict)
            else any(p.exists() for p in path.values())
        )
        if path_exists:
            print(f"  [OK] {name}: {path}")
        else:
            print(f"  [MISSING] {name}: {path}")
            all_ok = False

    return all_ok


# ==============================================================================
# Descriptive Statistics and Output
# ==============================================================================


def compute_h8_stats(df, config):
    """
    Compute descriptive statistics for H8 dataset.

    Special handling for binary takeover indicator.

    Args:
        df: H8 dataset
        config: Configuration dict

    Returns:
        Dictionary of statistics
    """
    print("\n" + "=" * 60)
    print("Computing H8 Statistics")
    print("=" * 60)

    stats: Dict[str, Any] = {
        "n_obs": len(df),
        "n_firms": df["gvkey"].nunique(),
        "n_years": df["year"].nunique(),
        "year_range": (int(df["year"].min()), int(df["year"].max())),
    }

    # Takeover rate (DV)
    stats["takeover_rate"] = float(df["takeover_fwd"].mean())
    stats["n_takeovers"] = int(df["takeover_fwd"].sum())

    print(f"  Observations: {stats['n_obs']:,}")
    print(f"  Firms: {stats['n_firms']:,}")
    print(f"  Years: {stats['year_range'][0]}-{stats['year_range'][1]}")
    print(f"  Takeover events (t+1): {stats['n_takeovers']:,}")
    print(f"  Takeover rate: {stats['takeover_rate']:.2%}")

    # Validate takeover rate
    if stats["takeover_rate"] < config["takeover_rate_min"]:
        print(
            f"  WARNING: Takeover rate {stats['takeover_rate']:.2%} below minimum {config['takeover_rate_min']:.2%}"
        )
    if stats["takeover_rate"] > config["takeover_rate_max"]:
        print(
            f"  WARNING: Takeover rate {stats['takeover_rate']:.2%} above maximum {config['takeover_rate_max']:.2%}"
        )
    if stats["n_takeovers"] < config["min_takeover_events"]:
        print(
            f"  WARNING: Takeover events {stats['n_takeovers']} below minimum {config['min_takeover_events']}"
        )

    # Alternative takeover definitions
    if "takeover_announced_fwd" in df.columns:
        stats["takeover_announced_rate"] = float(df["takeover_announced_fwd"].mean())
        stats["n_announced"] = int(df["takeover_announced_fwd"].sum())
        print(f"  Announced takeover rate: {stats['takeover_announced_rate']:.2%}")

    if "takeover_hostile_fwd" in df.columns:
        stats["takeover_hostile_rate"] = float(df["takeover_hostile_fwd"].mean())
        stats["n_hostile"] = int(df["takeover_hostile_fwd"].sum())
        print(f"  Hostile takeover rate: {stats['takeover_hostile_rate']:.2%}")

    # Uncertainty measures (IVs)
    print("\n  Uncertainty Measures:")
    uncertainty_measures = [c for c in df.columns if "Uncertainty_pct" in c]
    stats["uncertainty_measures"] = {}
    for uv in uncertainty_measures:
        if uv in df.columns and df[uv].notna().sum() > 0:
            stats["uncertainty_measures"][uv] = {
                "mean": float(df[uv].mean()),
                "std": float(df[uv].std()),
                "min": float(df[uv].min()),
                "max": float(df[uv].max()),
                "n": int(df[uv].notna().sum()),
                "missing": int(df[uv].isna().sum()),
            }
            print(
                f"    {uv}: mean={stats['uncertainty_measures'][uv]['mean']:.4f}, n={stats['uncertainty_measures'][uv]['n']:,}"
            )

    # Controls
    control_vars = [
        "Size",
        "Lev",
        "ROA",
        "BM",
        "CurrentRatio",
        "Efficiency",
        "StockRet",
        "Volatility",
        "RD_Intensity",
    ]
    print("\n  Control Variables:")
    stats["controls"] = {}
    for cv in control_vars:
        if cv in df.columns and df[cv].notna().sum() > 0:
            stats["controls"][cv] = {
                "mean": float(df[cv].mean()),
                "std": float(df[cv].std()),
                "min": float(df[cv].min()),
                "max": float(df[cv].max()),
                "n": int(df[cv].notna().sum()),
                "missing": int(df[cv].isna().sum()),
            }
            print(
                f"    {cv}: mean={stats['controls'][cv]['mean']:.4f}, n={stats['controls'][cv]['n']:,}"
            )

    return stats


def update_latest_symlink(output_dir):
    """Update the latest/ symlink to point to the new output directory."""
    try:
        latest_link = output_dir.parent / "latest"
        if latest_link.exists():
            if latest_link.is_symlink():
                latest_link.unlink()
            elif latest_link.is_dir():
                import shutil

                shutil.rmtree(latest_link)
        latest_link.symlink_to(output_dir)
    except Exception as e:
        print(f"  Warning: Could not create latest symlink: {e}")


# ==============================================================================
# Main
# ==============================================================================


def main():
    """Main execution"""
    args = parse_arguments()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    paths = setup_paths(timestamp)

    # Handle dry-run mode
    if args.dry_run:
        print("=" * 60)
        print("STEP 3.8: H8 Takeover Variables - DRY RUN")
        print(f"Timestamp: {timestamp}")
        print("=" * 60)

        prereq_ok = check_prerequisites(paths)
        if prereq_ok:
            print("\n[OK] All prerequisites validated")
            print("\nWould compute:")
            print("  - Takeover target indicator (completed deals)")
            print("  - Alternative takeover definitions (announced, hostile)")
            print("  - Forward-looking takeover indicator (t+1)")
            print("  - Merge with V2 uncertainty measures")
            print("  - M&A control variables from literature")
            print(f"\nOutput would be written to: {paths['output_dir']}")
            sys.exit(0)
        else:
            print("\n[ERROR] Prerequisites not met")
            sys.exit(1)

    # Check prerequisites before processing
    prereq_ok = check_prerequisites(paths)
    if not prereq_ok:
        print("\n[ERROR] Prerequisites not met. Exiting.")
        sys.exit(1)

    # Setup logging
    dual_writer = DualWriter(paths["log_file"])
    sys.stdout = dual_writer

    print("=" * 60)
    print("STEP 3.8: H8 Takeover Variables")
    print(f"Timestamp: {timestamp}")
    print("=" * 60)

    # Initialize statistics
    start_time = time.perf_counter()
    start_iso = datetime.now().isoformat()
    mem_start = get_process_memory_mb()
    memory_readings = [mem_start["rss_mb"]]

    stats: Dict[str, Any] = {
        "step_id": "3.8_H8TakeoverVariables",
        "timestamp": timestamp,
        "input": {"files": [], "checksums": {}, "total_rows": 0},
        "processing": {
            "takeover_indicators": [],
            "winsorization": {},
            "missing_dropped": 0,
        },
        "output": {"final_rows": 0, "files": [], "checksums": {}},
        "variables": {},
        "takeover_stats": {},
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

    print("\nLoading data...")

    # Load manifest
    print("\nManifest:")
    manifest_file = paths["manifest_dir"] / "master_sample_manifest.parquet"
    stats["input"]["files"].append(str(manifest_file))
    stats["input"]["checksums"][manifest_file.name] = compute_file_checksum(
        manifest_file
    )
    manifest = pd.read_parquet(manifest_file)
    manifest["gvkey"] = manifest["gvkey"].astype(str).str.zfill(6)
    print(f"  Manifest: {len(manifest):,} observations")

    # Load SDC data
    print("\nSDC M&A Data:")
    stats["input"]["files"].append(str(paths["sdc_file"]))
    stats["input"]["checksums"][paths["sdc_file"].name] = compute_file_checksum(
        paths["sdc_file"]
    )
    sdc_df = load_sdc_data(paths["sdc_file"], CONFIG["year_start"], CONFIG["year_end"])
    stats["input"]["total_rows"] += len(sdc_df)

    # Create forward takeover indicator
    sdc_df = create_forward_takeover(sdc_df)
    stats["processing"]["takeover_indicators"] = [
        "takeover_fwd",
        "takeover_announced_fwd",
        "takeover_hostile_fwd",
    ]

    # Load H7 data (base with uncertainty measures)
    print("\nH7 Illiquidity Data:")
    h7_file = paths["h7_dir"] / "H7_Illiquidity.parquet"
    stats["input"]["files"].append(str(h7_file))
    stats["input"]["checksums"][h7_file.name] = compute_file_checksum(h7_file)
    h7_df = load_h7_data(h7_file)
    stats["input"]["total_rows"] += len(h7_df)

    # Load firm controls
    print("\nFirm Controls:")
    try:
        controls_df = load_firm_controls(
            paths["root"] / "4_Outputs" / "3_Financial_Features",
            CONFIG["year_start"],
            CONFIG["year_end"],
        )
    except Exception as e:
        print(f"  Warning: Could not load firm controls: {e}")
        controls_df = pd.DataFrame()

    # Load CCM link table for CUSIP-GVKEY mapping
    print("\nCRSP-Compustat CCM Link Table:")
    stats["input"]["files"].append(str(paths["ccm_file"]))
    stats["input"]["checksums"][paths["ccm_file"].name] = compute_file_checksum(
        paths["ccm_file"]
    )
    ccm_map = load_ccm_link(paths["ccm_file"])

    # ========================================================================
    # Merge Data
    # ========================================================================

    print("\n" + "=" * 60)
    print("Merging and Constructing Sample")
    print("=" * 60)

    h8_df = merge_h8_data(sdc_df, h7_df, controls_df, manifest, ccm_map)
    h8_df = apply_sample_construction(h8_df, CONFIG)

    # ========================================================================
    # Apply Winsorization
    # ========================================================================

    print("\n" + "=" * 60)
    print("Applying Winsorization (1%/99%)")
    print("=" * 60)

    continuous_vars = [
        c
        for c in h8_df.columns
        if c
        in [
            "Size",
            "Lev",
            "ROA",
            "BM",
            "CurrentRatio",
            "Efficiency",
            "StockRet",
            "Volatility",
        ]
    ]

    for var in continuous_vars:
        if var in h8_df.columns and h8_df[var].notna().sum() > 0:
            before_mean = h8_df[var].mean()
            h8_df[var] = winsorize_series(
                h8_df[var], lower=CONFIG["winsor_lower"], upper=CONFIG["winsor_upper"]
            )
            after_mean = h8_df[var].mean()
            stats["processing"]["winsorization"][var] = {
                "before_mean": round(float(before_mean), 4),
                "after_mean": round(float(after_mean), 4),
            }
            print(f"  {var}: winsorized")

    # ========================================================================
    # Compute Statistics
    # ========================================================================

    h8_stats = compute_h8_stats(h8_df, CONFIG)
    stats["takeover_stats"] = {
        "n_obs": h8_stats["n_obs"],
        "n_firms": h8_stats["n_firms"],
        "n_years": h8_stats["n_years"],
        "year_range": h8_stats["year_range"],
        "takeover_rate": h8_stats["takeover_rate"],
        "n_takeovers": h8_stats["n_takeovers"],
    }

    # ========================================================================
    # Prepare Output
    # ========================================================================

    print("\n" + "=" * 60)
    print("Preparing Output")
    print("=" * 60)

    # Sort by gvkey, year
    final_output = h8_df.sort_values(["gvkey", "year"]).reset_index(drop=True)

    print(f"  Final output rows: {len(final_output):,}")

    # ========================================================================
    # Write Outputs
    # ========================================================================

    print("\n" + "=" * 60)
    print("Writing Outputs")
    print("=" * 60)

    # Write parquet file
    output_file = paths["output_dir"] / "H8_Takeover.parquet"
    final_output.to_parquet(output_file, index=False)
    print(f"  Wrote: {output_file.name}")
    stats["output"]["files"].append(output_file.name)
    stats["output"]["checksums"][output_file.name] = compute_file_checksum(output_file)
    stats["output"]["final_rows"] = len(final_output)

    # Write stats.json
    stats["processing"]["h8_stats"] = h8_stats
    save_stats(stats, paths["output_dir"])
    print("  Wrote: stats.json")

    # Update latest symlink
    update_latest_symlink(paths["output_dir"])

    # ========================================================================
    # Final Summary
    # ========================================================================

    # Timing
    end_time = time.perf_counter()
    stats["timing"]["end_iso"] = datetime.now().isoformat()
    stats["timing"]["duration_seconds"] = round(end_time - start_time, 2)

    # Memory tracking
    mem_end = get_process_memory_mb()
    memory_readings.append(mem_end["rss_mb"])
    stats["memory"]["end_mb"] = mem_end["rss_mb"]
    stats["memory"]["peak_mb"] = round(max(memory_readings), 2)
    stats["memory"]["delta_mb"] = round(mem_end["rss_mb"] - mem_start["rss_mb"], 2)

    # Throughput
    duration_seconds = end_time - start_time
    try:
        throughput = calculate_throughput(len(final_output), duration_seconds)
        stats["throughput"] = {
            "rows_per_second": throughput,
            "total_rows": len(final_output),
            "duration_seconds": round(duration_seconds, 3),
        }
    except ValueError as e:
        # Log but don't fail - throughput is not critical
        logger.warning(f"Could not calculate throughput: {e}")
        stats["throughput"] = {
            "error": str(e),
            "total_rows": len(final_output),
            "duration_seconds": round(duration_seconds, 3),
        }

    # Detect anomalies
    print("\nDetecting anomalies...")
    numeric_cols = [
        c for c in final_output.columns if final_output[c].dtype in ["float64", "int64"]
    ]
    anomalies = detect_anomalies_zscore(final_output, numeric_cols, threshold=3.0)
    total_anomalies = sum(a["count"] for a in anomalies.values())
    print(f"  Anomalies detected (z>3): {total_anomalies}")

    # Print summary
    print_stats_summary(stats)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"H8 Takeover Variables constructed: {len(final_output):,} observations")
    print(f"Takeover rate: {h8_stats['takeover_rate']:.2%}")
    print(f"Takeover events: {h8_stats['n_takeovers']:,}")
    print(f"\nOutputs saved to: {paths['output_dir']}")
    print(f"Log saved to: {paths['log_file']}")

    dual_writer.close()
    sys.stdout = dual_writer.terminal


if __name__ == "__main__":
    main()
