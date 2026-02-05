#!/usr/bin/env python3
"""
==============================================================================
STEP 3.2a: H2 Investment Efficiency Variables - Analyst Dispersion Patch
==============================================================================
ID: 3.2a_AnalystDispersionPatch
Description: Patches H2 Investment Efficiency output with analyst_dispersion
             control variable computed from IBES data via CCM CUSIP-GVKEY
             linking.

Purpose: The original 30-01 plan skipped analyst dispersion because CCM
         linking was unavailable. This patch uses CCM (CRSP-Compustat Merged)
         to map IBES CUSIPs to Compustat GVKEYs, enabling proper analyst
         forecast dispersion computation.

Variables Computed:
    - analyst_dispersion: STDEV / |MEANEST| from IBES, filtered by:
        * NUMEST >= 2 (meaningful dispersion requires 2+ analysts)
        * |MEANEST| >= 0.01 (avoid near-zero denominators)
      Aggregated by gvkey-year using MEDIAN (robust to outliers)

Inputs:
    - 1_Inputs/CRSPCompustat_CCM/CRSPCompustat_CCM.parquet
        CCM data with gvkey, cusip, LINKPRIM, LINKTYPE for CUSIP-GVKEY mapping
    - 1_Inputs/tr_ibes/tr_ibes.parquet
        IBES analyst forecasts with CUSIP, STATPERS, NUMEST, MEANEST, STDEV
    - 4_Outputs/3_Financial_V2/{timestamp}/H2_InvestmentEfficiency.parquet
        Existing H2 output to patch (will add analyst_dispersion column)

Outputs:
    - 4_Outputs/3_Financial_V2/{timestamp}/H2_InvestmentEfficiency.parquet
        Updated with analyst_dispersion column (14 columns total)
    - 4_Outputs/3_Financial_V2/{timestamp}/stats.json
        Updated with analyst_dispersion statistics

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
import warnings

# Add parent directory to sys.path for shared module imports
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir))

# Import shared utilities
from shared.path_utils import (
    validate_output_path,
    ensure_output_dir,
    validate_input_file,
    get_latest_output_dir,
)

from shared.observability_utils import (
    compute_file_checksum,
    get_process_memory_mb,
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


def setup_paths(config):
    """Set up all required paths"""
    root = Path(__file__).parent.parent.parent

    # Find latest H2 output
    h2_output_dir = get_latest_output_dir(
        root / "4_Outputs" / "3_Financial_V2",
        required_file="H2_InvestmentEfficiency.parquet",
    )

    paths = {
        "root": root,
        "ccm_file": root / "1_Inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet",
        "ibes_file": root / "1_Inputs" / "tr_ibes" / "tr_ibes.parquet",
        "h2_output_dir": h2_output_dir,
        "h2_parquet": h2_output_dir / "H2_InvestmentEfficiency.parquet",
        "h2_stats": h2_output_dir / "stats.json",
    }

    # Log directory
    log_base = root / "3_Logs" / "3_Financial_V2"
    ensure_output_dir(log_base)

    # Use the timestamp from the existing H2 output for consistent logging
    existing_timestamp = h2_output_dir.name
    paths["log_file"] = log_base / f"{existing_timestamp}_H2_AnalystDispersion.log"

    return paths


# ==============================================================================
# Data Loading
# ==============================================================================


def load_ccm(ccm_file, linkprim_filter=["P", "C"], linktype_filter=["LU", "LC"]):
    """Load CCM data with proper filters for valid CUSIP-GVKEY links

    Filters:
    - LINKPRIM in ['P', 'C'] (Primary or C)
    - LINKTYPE in ['LU', 'LC'] (Linktype values for valid links)

    Returns:
        DataFrame with gvkey, cusip8 columns for mapping
    """
    print(f"\nLoading CCM data...")
    print(f"  File: {ccm_file}")

    validate_input_file(ccm_file, must_exist=True)
    checksum = compute_file_checksum(ccm_file)
    print(f"  Checksum: {checksum}")

    # Load CCM
    ccm = pd.read_parquet(ccm_file)
    print(f"  Loaded: {len(ccm):,} rows")

    # Normalize CUSIP to 8 characters
    ccm["cusip"] = ccm["cusip"].astype(str).str[:8]

    # Apply filters for valid links
    before_filter = len(ccm)
    ccm = ccm[ccm["LINKPRIM"].isin(linkprim_filter)].copy()
    ccm = ccm[ccm["LINKTYPE"].isin(linktype_filter)].copy()
    after_filter = len(ccm)

    print(f"  After LINKPRIM in {linkprim_filter} AND LINKTYPE in {linktype_filter}: {after_filter:,} rows")
    print(f"  Filtered out: {before_filter - after_filter:,} rows")

    # Create gvkey_str (zero-padded to 6 chars) to match H2 output format
    ccm["gvkey_str"] = ccm["gvkey"].astype(str).str.zfill(6)

    # Keep only needed columns and deduplicate (keep first for ties)
    ccm_map = ccm[["cusip", "gvkey_str"]].drop_duplicates(subset=["cusip"], keep="first")

    print(f"  Unique CUSIP-GVKEY mappings: {len(ccm_map):,}")

    return ccm_map, checksum


def load_ibes(ibes_file, numest_min=2, meanest_abs_min=0.01):
    """Load and process IBES analyst forecast data

    Filters:
    - NUMEST >= 2 (meaningful dispersion requires 2+ analysts)
    - |MEANEST| >= 0.01 (avoid near-zero denominators)

    Returns:
        DataFrame with cusip, year, analyst_dispersion columns
    """
    print(f"\nLoading IBES data...")
    print(f"  File: {ibes_file}")

    validate_input_file(ibes_file, must_exist=True)

    # Load only required columns to save memory
    required_cols = ["CUSIP", "STATPERS", "NUMEST", "MEANEST", "STDEV"]

    import pyarrow.parquet as pq
    pf = pq.ParquetFile(ibes_file)
    available_cols = set(pf.schema_arrow.names)

    cols_to_read = [c for c in required_cols if c in available_cols]
    if len(cols_to_read) < len(required_cols):
        missing = set(required_cols) - set(cols_to_read)
        print(f"  Warning: Missing IBES columns: {missing}")

    checksum = compute_file_checksum(ibes_file)
    print(f"  Checksum: {checksum}")

    # Load IBES data
    print(f"  Reading {len(cols_to_read)} columns from {pf.metadata.num_rows:,} rows...")
    ibes = pd.read_parquet(ibes_file, columns=cols_to_read)

    print(f"  Loaded: {len(ibes):,} rows")

    # Normalize CUSIP to 8 characters
    ibes["cusip"] = ibes["CUSIP"].astype(str).str[:8]

    # Extract year from STATPERS (format: "YYYY-MM-DD")
    ibes["year"] = pd.to_datetime(ibes["STATPERS"], errors="coerce").dt.year

    # Convert numeric columns
    for col in ["NUMEST", "MEANEST", "STDEV"]:
        if col in ibes.columns:
            ibes[col] = pd.to_numeric(ibes[col], errors="coerce")

    # Apply filters
    before_filters = len(ibes)

    # Filter NUMEST >= 2
    ibes = ibes[ibes["NUMEST"] >= numest_min].copy()
    print(f"  After NUMEST >= {numest_min}: {len(ibes):,} rows")

    # Filter |MEANEST| >= 0.01
    ibes = ibes[ibes["MEANEST"].abs() >= meanest_abs_min].copy()
    print(f"  After |MEANEST| >= {meanest_abs_min}: {len(ibes):,} rows")

    after_filters = len(ibes)
    print(f"  Total filtered out: {before_filters - after_filters:,} rows")

    # Compute analyst_dispersion = STDEV / |MEANEST|
    ibes["analyst_dispersion"] = ibes["STDEV"] / ibes["MEANEST"].abs()

    # Take median by cusip-year (robust to outliers)
    dispersion = (
        ibes.groupby(["cusip", "year"])["analyst_dispersion"]
        .median()
        .reset_index()
    )

    print(f"  Unique CUSIP-year observations: {len(dispersion):,}")

    return dispersion, checksum


# ==============================================================================
# CUSIP-GVKEY Mapping
# ==============================================================================


def map_ibes_to_gvkey(ibes_dispersion, ccm_map):
    """Map IBES dispersion data to GVKEY using CCM CUSIP-GVKEY mapping

    Returns:
        DataFrame with gvkey_str, year, analyst_dispersion columns
    """
    print(f"\nMapping IBES to GVKEY via CCM...")

    # Merge on CUSIP
    dispersion_gvkey = ibes_dispersion.merge(
        ccm_map[["cusip", "gvkey_str"]],
        on="cusip",
        how="inner",
    )

    before_dedup = len(dispersion_gvkey)
    print(f"  After CUSIP-GVKEY merge: {before_dedup:,} observations")

    # Aggregate by gvkey-year (in case multiple CUSIPs map to same GVKEY)
    dispersion_gvkey = (
        dispersion_gvkey.groupby(["gvkey_str", "year"])["analyst_dispersion"]
        .median()
        .reset_index()
    )

    print(f"  After gvkey-year aggregation: {len(dispersion_gvkey):,} unique observations")
    print(f"  Deduplication removed: {before_dedup - len(dispersion_gvkey):,} rows")

    return dispersion_gvkey


# ==============================================================================
# H2 Output Patching
# ==============================================================================


def load_h2_output(h2_parquet):
    """Load existing H2 Investment Efficiency output"""
    print(f"\nLoading existing H2 output...")
    print(f"  File: {h2_parquet}")

    validate_input_file(h2_parquet, must_exist=True)
    h2 = pd.read_parquet(h2_parquet)

    print(f"  Rows: {len(h2):,}")
    print(f"  Columns: {list(h2.columns)}")

    return h2


def merge_analyst_dispersion(h2_df, dispersion_gvkey):
    """Merge analyst dispersion into H2 data

    Returns:
        Updated H2 dataframe with analyst_dispersion column
    """
    print(f"\nMerging analyst_dispersion into H2 data...")

    # Ensure fiscal_year is int for matching
    h2_df["fiscal_year"] = h2_df["fiscal_year"].astype(int)

    # Merge on gvkey and fiscal_year
    h2_merged = h2_df.merge(
        dispersion_gvkey.rename(columns={"gvkey_str": "gvkey", "year": "fiscal_year"}),
        on=["gvkey", "fiscal_year"],
        how="left",
    )

    # Count matches
    n_matched = h2_merged["analyst_dispersion"].notna().sum()
    n_total = len(h2_merged)

    print(f"  Matched: {n_matched:,} / {n_total:,} observations ({n_matched/n_total*100:.2f}%)")
    print(f"  Missing: {n_total - n_matched:,} observations ({(n_total-n_matched)/n_total*100:.2f}%)")

    return h2_merged


def winsorize_analyst_dispersion(df, lower=0.01, upper=0.99):
    """Apply winsorization to analyst_dispersion (1%, 99%)"""
    print(f"\nApplying winsorization to analyst_dispersion ({lower*100:.0f}%, {upper*100:.0f}%)...")

    dispersion = df["analyst_dispersion"].copy()
    before_mean = dispersion.mean()

    # Winsorize
    lower_bound = dispersion.quantile(lower)
    upper_bound = dispersion.quantile(upper)
    df["analyst_dispersion"] = dispersion.clip(lower=lower_bound, upper=upper_bound)

    after_mean = df["analyst_dispersion"].mean()

    print(f"  Before mean: {before_mean:.4f}")
    print(f"  After mean: {after_mean:.4f}")
    print(f"  Bounds: [{lower_bound:.4f}, {upper_bound:.4f}]")

    return df


def update_stats(stats_file, dispersion_series, ccm_checksum, ibes_checksum, processing_info):
    """Update stats.json with analyst_dispersion statistics"""
    print(f"\nUpdating stats.json...")

    # Load existing stats
    with open(stats_file, "r") as f:
        stats = json.load(f)

    # Add analyst_dispersion statistics
    n_valid = dispersion_series.notna().sum()
    n_missing = dispersion_series.isna().sum()

    stats["variables"]["analyst_dispersion"] = {
        "mean": round(float(dispersion_series.mean()), 4) if n_valid > 0 else None,
        "std": round(float(dispersion_series.std()), 4) if n_valid > 1 else None,
        "min": round(float(dispersion_series.min()), 4) if n_valid > 0 else None,
        "max": round(float(dispersion_series.max()), 4) if n_valid > 0 else None,
        "n": int(n_valid),
        "missing_count": int(n_missing),
    }

    # Add processing info
    if "processing" not in stats:
        stats["processing"] = {}
    stats["processing"]["analyst_dispersion_patch"] = {
        "timestamp": datetime.now().isoformat(),
        "ccm_checksum": ccm_checksum,
        "ibes_checksum": ibes_checksum,
        **processing_info,
    }

    # Update checksum (will change due to new column)
    stats["output"]["checksum_updated"] = True

    # Write updated stats
    with open(stats_file, "w") as f:
        json.dump(stats, f, indent=2)

    print(f"  Updated stats.json with analyst_dispersion statistics:")
    print(f"    mean: {stats['variables']['analyst_dispersion']['mean']}")
    print(f"    std: {stats['variables']['analyst_dispersion']['std']}")
    print(f"    n: {stats['variables']['analyst_dispersion']['n']}")
    print(f"    missing_count: {stats['variables']['analyst_dispersion']['missing_count']}")


# ==============================================================================
# CLI
# ==============================================================================


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="""
STEP 3.2a: H2 Investment Efficiency - Analyst Dispersion Patch

Patches H2 Investment Efficiency output with analyst_dispersion control variable
computed from IBES data via CCM CUSIP-GVKEY linking.
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
        "--dry-run",
        action="store_true",
        help="Validate inputs and report match counts without modifying files",
    )

    return parser.parse_args()


def check_prerequisites(paths):
    """Validate all required inputs exist"""
    print("\nChecking prerequisites...")

    required_files = {
        "CCM": paths["ccm_file"],
        "IBES": paths["ibes_file"],
        "H2 Output": paths["h2_parquet"],
        "H2 Stats": paths["h2_stats"],
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

    config = load_config()
    paths = setup_paths(config)

    # Setup logging
    log_file = open(paths["log_file"], "w", buffering=1)
    import builtins
    builtin_print = builtins.print

    def print_both(*args, **kwargs):
        kwargs.pop("flush", None)
        builtin_print(*args, **kwargs)
        builtin_print(*args, file=log_file, flush=True, **kwargs)

    builtins.print = print_both

    print("=" * 70)
    print("STEP 3.2a: H2 Investment Efficiency - Analyst Dispersion Patch")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 70)

    # Track processing info
    processing_info = {}
    start_time = time.perf_counter()
    mem_start = get_process_memory_mb()

    # Check prerequisites
    prereq_ok = check_prerequisites(paths)
    if not prereq_ok:
        print("\n[ERROR] Prerequisites not met. Exiting.")
        log_file.close()
        sys.exit(1)

    # Handle dry-run mode
    if args.dry_run:
        print("\n" + "=" * 70)
        print("DRY RUN MODE")
        print("=" * 70)

        # Load and check CCM
        ccm_map, ccm_checksum = load_ccm(paths["ccm_file"])
        processing_info["ccm_rows_loaded"] = len(ccm_map)
        processing_info["ccm_unique_mappings"] = len(ccm_map)

        # Load and check IBES
        dispersion, ibes_checksum = load_ibes(paths["ibes_file"])
        processing_info["ibes_rows_after_filters"] = len(dispersion)

        # Check CUSIP overlap
        ccm_cusips = set(ccm_map["cusip"])
        ibes_cusips = set(dispersion["cusip"])
        overlap = ccm_cusips & ibes_cusips
        processing_info["cusip_overlap_count"] = len(overlap)
        processing_info["ccm_unique_cusips"] = len(ccm_cusips)
        processing_info["ibes_unique_cusips"] = len(ibes_cusips)
        processing_info["cusip_match_rate"] = round(len(overlap) / len(ibes_cusips) * 100, 2) if len(ibes_cusips) > 0 else 0

        print(f"\n  CCM unique CUSIPs: {len(ccm_cusips):,}")
        print(f"  IBES unique CUSIPs: {len(ibes_cusips):,}")
        print(f"  Overlap (matched): {len(overlap):,} ({len(overlap)/len(ibes_cusips)*100:.2f}% of IBES)")

        # Check H2 output
        h2 = load_h2_output(paths["h2_parquet"])
        h2_gvkeys = set(h2["gvkey"])

        # Map and check potential matches
        dispersion_gvkey = map_ibes_to_gvkey(dispersion, ccm_map)
        matched_gvkeys = set(dispersion_gvkey["gvkey_str"])
        potential_matches = h2_gvkeys & matched_gvkeys
        processing_info["potential_h2_matches"] = len(potential_matches)

        print(f"\n  H2 GVKEYs: {len(h2_gvkeys):,}")
        print(f"  Dispersion GVKEYs: {len(matched_gvkeys):,}")
        print(f"  Potential H2 matches: {len(potential_matches):,} ({len(potential_matches)/len(h2_gvkeys)*100:.2f}% of H2)")

        print(f"\n[OK] Dry run complete. Would add analyst_dispersion to:")
        print(f"  {paths['h2_parquet']}")
        print(f"\nExpected coverage: ~{len(potential_matches)} firm-years")

        log_file.close()
        sys.exit(0)

    # ========================================================================
    # Load Data
    # ========================================================================

    print("\n" + "=" * 70)
    print("LOADING DATA")
    print("=" * 70)

    # Load CCM
    ccm_map, ccm_checksum = load_ccm(paths["ccm_file"])
    processing_info["ccm_rows_loaded"] = len(ccm_map)
    processing_info["ccm_unique_mappings"] = len(ccm_map)

    # Load IBES
    dispersion, ibes_checksum = load_ibes(paths["ibes_file"])
    processing_info["ibes_rows_after_filters"] = len(dispersion)

    # ========================================================================
    # Map IBES to GVKEY
    # ========================================================================

    print("\n" + "=" * 70)
    print("MAPPING IBES TO GVKEY")
    print("=" * 70)

    dispersion_gvkey = map_ibes_to_gvkey(dispersion, ccm_map)
    processing_info["gvkey_year_observations"] = len(dispersion_gvkey)

    # ========================================================================
    # Load and Patch H2 Output
    # ========================================================================

    print("\n" + "=" * 70)
    print("PATCHING H2 OUTPUT")
    print("=" * 70)

    h2 = load_h2_output(paths["h2_parquet"])
    processing_info["h2_rows_before"] = len(h2)

    h2_merged = merge_analyst_dispersion(h2, dispersion_gvkey)
    processing_info["h2_rows_after"] = len(h2_merged)
    processing_info["analyst_dispersion_matched"] = int(h2_merged["analyst_dispersion"].notna().sum())
    processing_info["analyst_dispersion_coverage"] = round(
        processing_info["analyst_dispersion_matched"] / len(h2_merged) * 100, 2
    )

    # Apply winsorization
    h2_final = winsorize_analyst_dispersion(h2_merged)
    processing_info["winsorization_applied"] = True

    # ========================================================================
    # Write Outputs
    # ========================================================================

    print("\n" + "=" * 70)
    print("WRITING OUTPUTS")
    print("=" * 70)

    # Write updated parquet (overwrite existing)
    output_file = paths["h2_parquet"]
    h2_final.to_parquet(output_file, index=False)
    print(f"  Updated: {output_file}")
    print(f"  Rows: {len(h2_final):,}")
    print(f"  Columns: {len(h2_final.columns)}")

    # Update stats.json
    update_stats(
        paths["h2_stats"],
        h2_final["analyst_dispersion"],
        ccm_checksum,
        ibes_checksum,
        processing_info,
    )
    print(f"  Updated: {paths['h2_stats']}")

    # ========================================================================
    # Final Summary
    # ========================================================================

    end_time = time.perf_counter()
    duration = end_time - start_time
    mem_end = get_process_memory_mb()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Execution time: {duration:.2f} seconds")
    print(f"Memory delta: {mem_end['rss_mb'] - mem_start['rss_mb']:.2f} MB")
    print(f"\n analyst_dispersion added:")
    print(f"  Matched: {processing_info['analyst_dispersion_matched']:,} observations")
    print(f"  Coverage: {processing_info['analyst_dispersion_coverage']:.2f}%")
    print(f"\nOutputs:")
    print(f"  Parquet: {output_file}")
    print(f"  Stats: {paths['h2_stats']}")
    print(f"  Log: {paths['log_file']}")

    log_file.close()


if __name__ == "__main__":
    main()
