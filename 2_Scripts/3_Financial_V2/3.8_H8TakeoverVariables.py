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
==============================================================================
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
import yaml
import hashlib
import json
import time

# Add parent directory to sys.path for shared module imports
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir))

# Import shared path validation utilities
from shared.path_utils import (
    validate_output_path,
    ensure_output_dir,
    validate_input_file,
    get_latest_output_dir,
)

# Import DualWriter from shared.observability_utils
from shared.observability_utils import (
    DualWriter,
    compute_file_checksum,
    print_stat,
    print_stats_summary,
    save_stats,
    get_process_memory_mb,
    calculate_throughput,
    detect_anomalies_zscore,
)

# ==============================================================================
# Configuration
# ==============================================================================

# H8 Takeover Variables Configuration
CONFIG = {
    'year_start': 2002,
    'year_end': 2018,
    'sdc_file': '1_Inputs/SDC/sdc-ma-merged.parquet',
    'min_firm_years': 3,
    'winsor_lower': 0.01,
    'winsor_upper': 0.99,
    # Takeover rate validation thresholds
    'takeover_rate_min': 0.005,  # 0.5% minimum annual takeover rate
    'takeover_rate_max': 0.05,   # 5% maximum annual takeover rate
    'min_takeover_events': 100,   # Minimum takeover events in sample
}

# Takeover type definitions
TAKEOVER_TYPES = {
    'primary': 'completed',     # Completed deals (primary)
    'announced': 'announced',   # Announced deals (robustness)
    'hostile': 'hostile',       # Hostile/unsolicited deals (robustness)
}

# M&A prediction literature control variables
MNA_CONTROL_VARS = [
    'size',          # Firm size (log assets or market cap)
    'leverage',      # Debt / Assets
    'roa',           # Return on Assets
    'mtb',           # Market-to-book ratio
    'liquidity',     # Current ratio or quick ratio
    'efficiency',    # Asset turnover (Sales / Assets)
    'stock_ret',     # Stock returns (abnormal returns)
    'rd_intensity',  # R&D / Assets (if available)
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
    except Exception as e:
        # Fallback to 1.0_BuildSampleManifest
        manifest_dir = get_latest_output_dir(
            root / "4_Outputs" / "1.0_BuildSampleManifest",
            required_file="master_sample_manifest.parquet",
        )

    # Resolve textual analysis directory
    text_dir = get_latest_output_dir(
        root / "4_Outputs" / "2_Textual_Analysis" / "2.2_Variables",
        required_file_pattern="linguistic_variables_",
    )

    # Resolve H7 illiquidity output (for base dataset with uncertainty measures)
    h7_dir = get_latest_output_dir(
        root / "4_Outputs" / "3_Financial_V2",
        required_file="H7_Illiquidity.parquet",
    )

    paths = {
        "root": root,
        "manifest_dir": manifest_dir,
        "text_dir": text_dir,
        "h7_dir": h7_dir,
        "sdc_file": root / CONFIG['sdc_file'],
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
        'Target 6-digit CUSIP',
        'Date Announced',
        'Date Effective',
        'Deal Status',
        'Deal Attitude',
        'Target Public Status',
        'Deal Value (USD Millions)',
    ]

    # Check which columns exist
    available_cols = [c for c in required_cols if c in df.columns]
    df = df[available_cols].copy()

    # Convert date and extract year
    df['Date Announced'] = pd.to_datetime(df['Date Announced'])
    df['year'] = df['Date Announced'].dt.year

    # Filter to sample period
    df = df[df['year'].between(year_start, year_end)]
    print(f"  Filtered to {year_start}-{year_end}: {len(df):,} deals")

    # Filter to public targets only (our sample is public firms)
    if 'Target Public Status' in df.columns:
        df_public = df[df['Target Public Status'] == 'Public'].copy()
        print(f"  Public targets: {len(df_public):,} deals")
    else:
        df_public = df.copy()
        print("  Warning: Target Public Status not available, using all deals")

    # Create takeover indicators
    # Primary: Completed deals
    if 'Deal Status' in df_public.columns:
        df_public['takeover_completed'] = (df_public['Deal Status'] == 'Completed').astype(int)
        completed_count = df_public['takeover_completed'].sum()
        print(f"  Completed deals: {completed_count:,}")
    else:
        df_public['takeover_completed'] = 1  # All rows are announced
        print("  Warning: Deal Status not available, using all as completed")

    # Robustness 1: All announced deals
    df_public['takeover_announced'] = 1  # All rows are announced by definition

    # Robustness 2: Hostile/unsolicited deals
    if 'Deal Attitude' in df_public.columns:
        hostile_indicators = ['Hostile', 'Unsolicited']
        df_public['takeover_hostile'] = df_public['Deal Attitude'].isin(hostile_indicators).astype(int)
        hostile_count = df_public['takeover_hostile'].sum()
        print(f"  Hostile/unsolicited deals: {hostile_count:,}")
    else:
        df_public['takeover_hostile'] = 0
        print("  Warning: Deal Attitude not available, hostile = 0")

    # Aggregate to CUSIP-year level (1 if any takeover in year)
    # We use CUSIP as identifier; will map to GVKEY later
    takeover = df_public.groupby(['Target 6-digit CUSIP', 'year']).agg({
        'takeover_completed': 'max',
        'takeover_announced': 'max',
        'takeover_hostile': 'max',
    }).reset_index()

    takeover = takeover.rename(columns={'Target 6-digit CUSIP': 'cusip'})

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
    df['gvkey'] = df['gvkey'].astype(str).str.zfill(6)

    return df


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

    takeover_df = takeover_df.sort_values(['cusip', 'year'])
    takeover_df['takeover_fwd'] = takeover_df.groupby('cusip')['takeover_completed'].shift(-1)
    takeover_df['takeover_fwd'] = takeover_df['takeover_fwd'].fillna(0).astype(int)

    # Also create forward versions of alternative definitions
    takeover_df['takeover_announced_fwd'] = takeover_df.groupby('cusip')['takeover_announced'].shift(-1)
    takeover_df['takeover_announced_fwd'] = takeover_df['takeover_announced_fwd'].fillna(0).astype(int)

    takeover_df['takeover_hostile_fwd'] = takeover_df.groupby('cusip')['takeover_hostile'].shift(-1)
    takeover_df['takeover_hostile_fwd'] = takeover_df['takeover_hostile_fwd'].fillna(0).astype(int)

    n_takeovers = takeover_df['takeover_fwd'].sum()
    takeover_rate = takeover_df['takeover_fwd'].mean()
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
    combined['gvkey'] = combined['gvkey'].astype(str).str.zfill(6)

    # Filter to sample period
    combined = combined[combined['year'].between(year_start, year_end)]

    return combined


def merge_h8_data(takeover_df, h7_df, controls_df, manifest_df):
    """
    Merge takeover data with uncertainty and controls.

    Args:
        takeover_df: SDC takeover data (with cusip, year)
        h7_df: H7 data with uncertainty measures (with gvkey, year)
        controls_df: Firm controls
        manifest_df: Sample manifest for filtering

    Returns:
        Analysis-ready dataset for H8
    """
    print("\n" + "=" * 60)
    print("Merging H8 Data")
    print("=" * 60)

    # Step 1: Load manifest to get CUSIP-GVKEY mapping
    print("\nStep 1: Loading manifest for CUSIP-GVKEY mapping...")
    manifest_cols = ['gvkey', 'cusip', 'year'] if 'cusip' in manifest_df.columns else ['gvkey', 'year']
    manifest_subset = manifest_df[manifest_cols].drop_duplicates() if 'cusip' in manifest_df.columns else manifest_df[['gvkey', 'year']].drop_duplicates()

    # Ensure consistent types
    manifest_subset['gvkey'] = manifest_subset['gvkey'].astype(str).str.zfill(6)
    if 'cusip' in manifest_subset.columns:
        manifest_subset['cusip'] = manifest_subset['cusip'].astype(str).str[:6]

    print(f"  Manifest: {len(manifest_subset):,} unique gvkey-years")

    # Step 2: Map takeover CUSIPs to GVKEYs using manifest
    print("\nStep 2: Mapping CUSIPs to GVKEYs...")
    takeover_df['cusip'] = takeover_df['cusip'].astype(str).str[:6]

    # Merge takeover with manifest to get gvkey
    takeover_with_gvkey = takeover_df.merge(
        manifest_subset,
        on=['cusip', 'year'],
        how='left'
    )

    # Drop observations without GVKEY match
    n_before = len(takeover_with_gvkey)
    takeover_with_gvkey = takeover_with_gvkey[takeover_with_gvkey['gvkey'].notna()].copy()
    takeover_with_gvkey['gvkey'] = takeover_with_gvkey['gvkey'].astype(str).str.zfill(6)
    print(f"  Matched {len(takeover_with_gvkey):,}/{n_before:,} takeover observations to GVKEYs")

    # Step 3: Start with H7 data (has uncertainty measures and some controls)
    print("\nStep 3: Merging with H7 base data...")
    h8_df = h7_df.copy()

    # Select H7 columns we need
    h7_cols = ['gvkey', 'year']
    # Add uncertainty measures
    uncertainty_cols = [c for c in h7_df.columns if 'Uncertainty_pct' in c]
    h7_cols.extend(uncertainty_cols)
    # Add existing controls
    control_cols = [c for c in h7_df.columns if c in ['Volatility', 'StockRet', 'trading_days']]
    h7_cols.extend(control_cols)

    h8_df = h7_df[h7_cols].copy()
    print(f"  H7 base: {len(h8_df):,} observations")

    # Step 4: Merge takeover indicators
    print("\nStep 4: Merging takeover indicators...")
    takeover_merge = takeover_with_gvkey[['gvkey', 'year', 'takeover_fwd', 'takeover_announced_fwd', 'takeover_hostile_fwd']].copy()
    h8_df = h8_df.merge(takeover_merge, on=['gvkey', 'year'], how='left')
    h8_df['takeover_fwd'] = h8_df['takeover_fwd'].fillna(0).astype(int)
    h8_df['takeover_announced_fwd'] = h8_df['takeover_announced_fwd'].fillna(0).astype(int)
    h8_df['takeover_hostile_fwd'] = h8_df['takeover_hostile_fwd'].fillna(0).astype(int)
    print(f"  After takeover merge: {len(h8_df):,} observations")
    print(f"  Takeover targets (t+1): {h8_df['takeover_fwd'].sum():,}")

    # Step 5: Merge additional firm controls if available
    if controls_df is not None and len(controls_df) > 0:
        print("\nStep 5: Merging additional firm controls...")
        # Get control columns that exist
        available_controls = []
        for cv in MNA_CONTROL_VARS:
            # Map generic names to actual column names
            if cv == 'size' and 'Size' in controls_df.columns:
                available_controls.append('Size')
            elif cv == 'leverage' and 'Lev' in controls_df.columns:
                available_controls.append('Lev')
            elif cv == 'roa' and 'ROA' in controls_df.columns:
                available_controls.append('ROA')
            elif cv == 'mtb' and 'BM' in controls_df.columns:
                available_controls.append('BM')
            elif cv == 'liquidity' and 'CurrentRatio' in controls_df.columns:
                available_controls.append('CurrentRatio')
            elif cv == 'efficiency' and 'Efficiency' in controls_df.columns:
                available_controls.append('Efficiency')
            elif cv == 'stock_ret' and 'StockRet' in controls_df.columns:
                available_controls.append('StockRet')
            elif cv == 'rd_intensity' and 'RD_Intensity' in controls_df.columns:
                available_controls.append('RD_Intensity')

        if available_controls:
            controls_merge = controls_df[['gvkey', 'year'] + available_controls].drop_duplicates()
            h8_df = h8_df.merge(controls_merge, on=['gvkey', 'year'], how='left')
            print(f"  Merged controls: {available_controls}")

    # Step 6: Filter to sample firms
    print("\nStep 6: Filtering to sample firms...")
    sample_firms = manifest_subset['gvkey'].unique()
    h8_df = h8_df[h8_df['gvkey'].isin(sample_firms)]
    print(f"  After sample filter: {len(h8_df):,} observations")

    # Step 7: Apply missing data handling
    print("\nStep 7: Handling missing data...")

    # For logistic regression, require DV and primary IV
    required_vars = ['takeover_fwd']
    primary_iv = 'Manager_QA_Uncertainty_pct' if 'Manager_QA_Uncertainty_pct' in h8_df.columns else uncertainty_cols[0] if uncertainty_cols else None
    if primary_iv:
        required_vars.append(primary_iv)

    n_before_missing = len(h8_df)
    h8_df = h8_df.dropna(subset=required_vars)
    n_after_missing = len(h8_df)
    print(f"  Dropped {n_before_missing - n_after_missing:,} observations with missing DV/IV")

    # For controls, require at least 80% availability
    control_cols_in_df = [c for c in h8_df.columns if c in ['Size', 'Lev', 'ROA', 'BM', 'CurrentRatio', 'Efficiency', 'StockRet', 'RD_Intensity', 'Volatility']]
    if control_cols_in_df:
        h8_df['n_missing_controls'] = h8_df[control_cols_in_df].isna().sum(axis=1)
        max_missing = len(control_cols_in_df) * 0.2  # Allow up to 20% missing
        h8_df = h8_df[h8_df['n_missing_controls'] <= max_missing].copy()
        print(f"  Dropped observations with >20% missing controls")
        h8_df = h8_df.drop(columns=['n_missing_controls'])

    print(f"  Final sample: {len(h8_df):,} observations")

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

    n_before = len(df)

    # For H8, we rely on H7 sample which already has exclusions applied
    print(f"  Using H7 sample (exclusions already applied)")
    print(f"  Sample: {len(df):,} firm-year observations")

    # Count unique firms and years
    n_firms = df['gvkey'].nunique()
    n_years = df['year'].nunique()
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
        if path.exists():
            print(f"  [OK] {name}: {path}")
        else:
            print(f"  [MISSING] {name}: {path}")
            all_ok = False

    return all_ok


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

    stats = {
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

    print("\n[TODO] Implementation continues in next tasks...")
    print("This is Task 1: Script header and setup")

    # Close logging
    dual_writer.close()
    sys.stdout = dual_writer.terminal


if __name__ == "__main__":
    main()
