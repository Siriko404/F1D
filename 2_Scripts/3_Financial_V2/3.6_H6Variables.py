#!/usr/bin/env python3
"""
==============================================================================
STEP 3.6: H6 CCCL Speech Uncertainty Variables
==============================================================================
ID: 3.6_H6Variables
Description: Constructs H6 analysis dataset by merging CCCL shift-share instrument
             with speech uncertainty measures from earnings call transcripts.

             The CCCL (Comment Letter Count) shift-share instrument measures
             SEC scrutiny exposure at the industry level. This script creates
             the treatment variable (lagged CCCL exposure) and merges it with
             speech uncertainty measures for testing whether SEC scrutiny reduces
             managerial speech uncertainty.

Variables Computed:
    - CCCL shift-share instrument (6 variants): shift_intensity_*
    - Lagged CCCL exposure (t-1): All 6 variants with _lag suffix
    - Speech uncertainty measures (6): Manager_QA_Uncertainty_pct,
      Manager_QA_Weak_Modal_pct, CEO_QA_Uncertainty_pct, CEO_QA_Weak_Modal_pct,
      Manager_Pres_Uncertainty_pct, CEO_Pres_Uncertainty_pct
    - Uncertainty_Gap: Manager_QA_Uncertainty_pct - Manager_Pres_Uncertainty_pct
      (measures spontaneous vs. prepared speech uncertainty)

Inputs:
    - 1_Inputs/CCCL instrument/instrument_shift_intensity_2005_2022.parquet
      (145K firm-years, 6 shift-intensity variants)
    - 4_Outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_*.parquet
      (2002-2018 earnings call transcripts with linguistic measures)

Outputs:
    - 4_Outputs/3_Financial_V2/3.6_H6Variables/{timestamp}/H6_CCCL_Speech.parquet
    - 4_Outputs/3_Financial_V2/3.6_H6Variables/{timestamp}/stats.json

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
import json
import time
import warnings

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


def setup_paths(config, timestamp):
    """Set up all required paths"""
    root = Path(__file__).parent.parent.parent

    # Resolve linguistic variables directory
    linguistics_dir = get_latest_output_dir(
        root / "4_Outputs" / "2_Textual_Analysis" / "2.2_Variables",
    )

    paths = {
        "root": root,
        "linguistics_dir": linguistics_dir,
        "cccl_file": root / "1_Inputs" / "CCCL instrument" / "instrument_shift_intensity_2005_2022.parquet",
    }

    # Output directory
    output_base = root / "4_Outputs" / "3_Financial_V2" / "3.6_H6Variables"
    paths["output_dir"] = output_base / timestamp
    ensure_output_dir(paths["output_dir"])

    # Log directory
    log_base = root / "3_Logs" / "3_Financial_V2"
    ensure_output_dir(log_base)
    paths["log_file"] = log_base / f"{timestamp}_H6.log"

    return paths


# ==============================================================================
# Data Loading
# ==============================================================================


def load_cccl_instrument(cccl_file, logger):
    """
    Load CCCL shift-share instrument.

    Note: CCCL instrument is ANNUAL (year column), not quarterly.
    Merge will be on gvkey + year (not fiscal_quarter).
    """
    logger.write(f"\nLoading CCCL instrument from: {cccl_file}")

    if not cccl_file.exists():
        raise FileNotFoundError(f"CCCL instrument not found: {cccl_file}")

    validate_input_file(cccl_file, must_exist=True)
    df = pd.read_parquet(cccl_file)

    logger.write(f"  Loaded {len(df):,} observations")

    # Standardize gvkey to string with leading zeros (6-digit format)
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)

    # Rename year to fiscal_year for consistency with speech data
    df = df.rename(columns={"year": "fiscal_year"})

    # Define the 6 shift-intensity variants (instrument variants)
    cccl_variants = [
        "shift_intensity_sale_ff12",
        "shift_intensity_mkvalt_ff12",
        "shift_intensity_sale_ff48",
        "shift_intensity_mkvalt_ff48",
        "shift_intensity_sale_sic2",
        "shift_intensity_mkvalt_sic2",
    ]

    # Verify all variants exist
    missing_variants = [v for v in cccl_variants if v not in df.columns]
    if missing_variants:
        raise ValueError(f"Missing CCCL variants: {missing_variants}")

    logger.write(f"  CCCL variants ({len(cccl_variants)}): {', '.join(cccl_variants)}")

    # Log CCCL coverage statistics
    logger.write(f"\n  CCCL coverage by variant:")
    for variant in cccl_variants:
        non_null = df[variant].notna().sum()
        logger.write(f"    {variant}: {non_null:,} non-null ({non_null/len(df)*100:.1f}%)")

    # Log year range
    year_min = df["fiscal_year"].min()
    year_max = df["fiscal_year"].max()
    logger.write(f"\n  Year range: {year_min}-{year_max}")

    # Compute checksum
    checksum = compute_file_checksum(cccl_file)
    logger.write(f"  CCCL checksum: {checksum}")

    return df, cccl_variants, checksum


def load_speech_measures(linguistics_dir, logger, min_year=2002, max_year=2018):
    """
    Load speech uncertainty measures from linguistic variables.

    Loads all yearly parquet files and extracts the 6 uncertainty measures
    needed for H6 analysis.
    """
    logger.write(f"\nLoading speech measures from: {linguistics_dir}")

    # Find all linguistic_variables_*.parquet files
    parquet_files = sorted(linguistics_dir.glob("linguistic_variables_*.parquet"))

    if not parquet_files:
        raise FileNotFoundError(f"No linguistic_variables files found in {linguistics_dir}")

    # Define the 6 uncertainty measures we need
    uncertainty_measures = [
        "Manager_QA_Uncertainty_pct",
        "Manager_QA_Weak_Modal_pct",
        "CEO_QA_Uncertainty_pct",
        "CEO_QA_Weak_Modal_pct",
        "Manager_Pres_Uncertainty_pct",
        "CEO_Pres_Uncertainty_pct",
    ]

    # Required columns for merge
    required_cols = ["file_name", "start_date", "gvkey"] + uncertainty_measures

    dfs = []
    for pf in parquet_files:
        df = pd.read_parquet(pf)

        # Check which required columns exist
        available_cols = [c for c in required_cols if c in df.columns]
        df_subset = df[available_cols].copy()

        dfs.append(df_subset)

    combined = pd.concat(dfs, ignore_index=True)

    logger.write(f"  Loaded {len(dfs)} yearly files")
    logger.write(f"  Total observations: {len(combined):,}")

    # Convert start_date to datetime and extract fiscal year
    combined["start_date"] = pd.to_datetime(combined["start_date"])
    combined["fiscal_year"] = combined["start_date"].dt.year

    # Filter to year range
    combined = combined[
        (combined["fiscal_year"] >= min_year) &
        (combined["fiscal_year"] <= max_year)
    ].copy()

    logger.write(f"  After year filter ({min_year}-{max_year}): {len(combined):,}")

    # Check which uncertainty measures are available
    available_measures = [m for m in uncertainty_measures if m in combined.columns]
    logger.write(f"\n  Available uncertainty measures ({len(available_measures)}):")
    for m in available_measures:
        non_null = combined[m].notna().sum()
        logger.write(f"    {m}: {non_null:,} non-null ({non_null/len(combined)*100:.1f}%)")

    # Aggregate to firm-year level (take mean if multiple calls per year)
    # Note: CCCL is annual, so we aggregate speech to annual
    id_cols = ["gvkey", "fiscal_year"]
    agg_cols = available_measures

    speech_agg = combined[id_cols + agg_cols].groupby(id_cols)[agg_cols].mean().reset_index()

    logger.write(f"\n  Aggregated to firm-year level: {len(speech_agg):,} observations")
    logger.write(f"  Unique firms: {speech_agg['gvkey'].nunique():,}")

    return speech_agg, available_measures


# ==============================================================================
# Merge and Variable Construction
# ==============================================================================


def merge_cccl_speech(cccl_df, speech_df, logger):
    """
    Merge CCCL instrument with speech measures.

    Merge key: gvkey + fiscal_year (CCCL is annual)
    """
    logger.write("\n" + "="*80)
    logger.write("Merging CCCL Instrument with Speech Measures")
    logger.write("="*80)

    logger.write(f"\n  CCCL observations: {len(cccl_df):,}")
    logger.write(f"  Speech observations: {len(speech_df):,}")

    # Merge on gvkey + fiscal_year (inner join - complete cases only)
    merged = cccl_df.merge(
        speech_df,
        on=["gvkey", "fiscal_year"],
        how="inner"
    )

    logger.write(f"\n  Merged: {len(merged):,} observations with both CCCL and speech data")

    # Calculate merge success rate
    cccl_firms = set(cccl_df["gvkey"].unique())
    speech_firms = set(speech_df["gvkey"].unique())
    merged_firms = set(merged["gvkey"].unique())

    logger.write(f"\n  Firm overlap:")
    logger.write(f"    CCCL firms: {len(cccl_firms):,}")
    logger.write(f"    Speech firms: {len(speech_firms):,}")
    logger.write(f"    Overlap: {len(merged_firms):,} ({len(merged_firms)/len(cccl_firms)*100:.1f}% of CCCL firms)")

    # Check merge rate
    merge_rate = len(merged) / len(cccl_df) * 100
    logger.write(f"\n  Merge success rate: {merge_rate:.1f}%")

    if merge_rate < 50:
        logger.write("  WARNING: Merge rate < 50%. Check data coverage.")

    return merged


def create_lagged_cccl(df, cccl_variants, logger):
    """
    Create lagged CCCL exposure (t-1).

    Lagged treatment ensures temporal ordering: CCCL_{t-1} predicts Speech_t.
    This avoids reverse causality (speech affecting future CCCL exposure).
    """
    logger.write("\n" + "="*80)
    logger.write("Creating Lagged CCCL Exposure (t-1)")
    logger.write("="*80)

    # Sort by firm and year
    df = df.sort_values(["gvkey", "fiscal_year"]).copy()

    # Create lagged versions of all CCCL variants
    for variant in cccl_variants:
        lag_col = f"{variant}_lag"
        df[lag_col] = df.groupby("gvkey")[variant].shift(1)

        non_null = df[lag_col].notna().sum()
        logger.write(f"  {lag_col}: {non_null:,} non-null")

    # Log lag statistics
    logger.write(f"\n  After lagging: {df['shift_intensity_mkvalt_ff48_lag'].notna().sum():,} observations with lagged CCCL")

    return df


def compute_uncertainty_gap(df, logger):
    """
    Compute uncertainty gap = Manager_QA_Uncertainty_pct - Manager_Pres_Uncertainty_pct.

    Gap > 0: Manager more uncertain in spontaneous speech (Q&A)
    Gap < 0: Manager more uncertain in prepared remarks (Presentation)

    This measure captures the difference between spontaneous and prepared
    speech uncertainty, which is a mechanism test for H6.
    """
    logger.write("\n" + "="*80)
    logger.write("Computing Uncertainty Gap (Q&A - Presentation)")
    logger.write("="*80)

    if "Manager_QA_Uncertainty_pct" in df.columns and "Manager_Pres_Uncertainty_pct" in df.columns:
        df["uncertainty_gap"] = df["Manager_QA_Uncertainty_pct"] - df["Manager_Pres_Uncertainty_pct"]

        # Log statistics
        valid_gap = df["uncertainty_gap"].notna()
        logger.write(f"\n  Uncertainty gap statistics ({valid_gap.sum():,} observations):")
        logger.write(f"    Mean: {df.loc[valid_gap, 'uncertainty_gap'].mean():.4f}")
        logger.write(f"    Std: {df.loc[valid_gap, 'uncertainty_gap'].std():.4f}")
        logger.write(f"    Min: {df.loc[valid_gap, 'uncertainty_gap'].min():.4f}")
        logger.write(f"    Max: {df.loc[valid_gap, 'uncertainty_gap'].max():.4f}")

        # Percentage positive vs negative
        pos_gap = (df["uncertainty_gap"] > 0).sum()
        neg_gap = (df["uncertainty_gap"] < 0).sum()
        zero_gap = (df["uncertainty_gap"] == 0).sum()
        total = pos_gap + neg_gap + zero_gap

        logger.write(f"\n  Distribution:")
        logger.write(f"    Positive gap (more uncertain in Q&A): {pos_gap:,} ({pos_gap/total*100:.1f}%)")
        logger.write(f"    Negative gap (more uncertain in Pres): {neg_gap:,} ({neg_gap/total*100:.1f}%)")
        logger.write(f"    Zero gap: {zero_gap:,} ({zero_gap/total*100:.1f}%)")
    else:
        logger.write("  Warning: Cannot compute uncertainty_gap - missing required columns")
        df["uncertainty_gap"] = np.nan

    return df


def filter_sample(df, logger, min_year=2005, max_year=2018):
    """
    Filter to sample period (2005-2018 overlap).

    CCCL data starts in 2005, speech data ends in 2018.
    """
    logger.write("\n" + "="*80)
    logger.write("Filtering to Sample Period")
    logger.write("="*80)

    logger.write(f"\n  Before filter: {len(df):,} observations")

    df_filtered = df[
        (df["fiscal_year"] >= min_year) &
        (df["fiscal_year"] <= max_year)
    ].copy()

    logger.write(f"  After filter ({min_year}-{max_year}): {len(df_filtered):,} observations")

    # Count unique firms
    n_firms = df_filtered["gvkey"].nunique()
    logger.write(f"  Unique firms: {n_firms:,}")

    return df_filtered


# ==============================================================================
# Main Execution
# ==============================================================================


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="Construct H6 CCCL Speech Uncertainty Variables",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python 3.6_H6Variables.py              # Run with default settings
  python 3.6_H6Variables.py --dry-run    # Validate inputs without processing
        """
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and print planned operations without processing"
    )
    args = parser.parse_args()

    # Generate timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    # Load configuration
    config = load_config()

    # Setup paths
    paths = setup_paths(config, timestamp)

    # Initialize logger
    logger = DualWriter(paths["log_file"])
    logger.write("=" * 80)
    logger.write("STEP 3.6: H6 CCCL Speech Uncertainty Variables")
    logger.write("=" * 80)
    logger.write(f"Start time: {datetime.now().isoformat()}")
    logger.write(f"Timestamp: {timestamp}")
    logger.write(f"Python version: {sys.version}")

    if args.dry_run:
        logger.write("\n" + "="*80)
        logger.write("DRY RUN MODE - Validating inputs only")
        logger.write("="*80)

    # Stats collection
    stats = {
        "timestamp": timestamp,
        "script_id": "3.6_H6Variables",
        "start_time": datetime.now().isoformat(),
        "parameters": {},
        "input_files": {},
        "processing_steps": {},
        "output_stats": {},
    }

    try:
        # Step 1: Load CCCL instrument
        logger.write("\n" + "="*80)
        logger.write("STEP 1: Loading CCCL Shift-Share Instrument")
        logger.write("="*80)

        cccl_df, cccl_variants, cccl_checksum = load_cccl_instrument(paths["cccl_file"], logger)
        stats["input_files"]["cccl_instrument"] = {
            "path": str(paths["cccl_file"]),
            "rows": len(cccl_df),
            "variants": cccl_variants,
            "checksum": cccl_checksum,
        }

        # Step 2: Load speech measures
        logger.write("\n" + "="*80)
        logger.write("STEP 2: Loading Speech Uncertainty Measures")
        logger.write("="*80)

        speech_df, uncertainty_measures = load_speech_measures(
            paths["linguistics_dir"], logger,
            min_year=2005, max_year=2018
        )
        stats["input_files"]["linguistic_variables"] = {
            "path": str(paths["linguistics_dir"]),
            "rows": len(speech_df),
            "measures": uncertainty_measures,
        }

        if args.dry_run:
            logger.write("\n" + "="*80)
            logger.write("DRY RUN COMPLETE - All inputs validated successfully")
            logger.write("="*80)
            logger.write("\nPlanned operations:")
            logger.write("  1. Merge CCCL instrument with speech measures on gvkey + fiscal_year")
            logger.write("  2. Create lagged CCCL exposure (t-1) for all 6 variants")
            logger.write("  3. Compute uncertainty_gap = QA_Uncertainty - Pres_Uncertainty")
            logger.write("  4. Filter to 2005-2018 sample period")
            logger.write("  5. Output H6_CCCL_Speech.parquet")
            return 0

        # Step 3: Merge CCCL and speech
        merged_df = merge_cccl_speech(cccl_df, speech_df, logger)
        stats["processing_steps"]["merge"] = {
            "rows_after_merge": len(merged_df),
        }

        # Step 4: Create lagged CCCL
        merged_df = create_lagged_cccl(merged_df, cccl_variants, logger)

        # Step 5: Compute uncertainty gap
        merged_df = compute_uncertainty_gap(merged_df, logger)

        # Step 6: Filter to sample period
        final_df = filter_sample(merged_df, logger)

        # Step 7: Prepare output columns
        logger.write("\n" + "="*80)
        logger.write("Preparing Final Dataset")
        logger.write("="*80)

        # Keep only observations with lagged CCCL (t-1)
        final_df = final_df[final_df["shift_intensity_mkvalt_ff48_lag"].notna()].copy()

        logger.write(f"\n  Final sample (with lagged CCCL): {len(final_df):,} observations")
        logger.write(f"  Unique firms: {final_df['gvkey'].nunique():,}")

        # Define output columns
        id_cols = ["gvkey", "fiscal_year"]

        # CCCL variants (raw and lagged)
        cccl_cols = cccl_variants + [f"{v}_lag" for v in cccl_variants]

        # Speech measures
        speech_cols = uncertainty_measures + ["uncertainty_gap"]

        output_cols = id_cols + cccl_cols + speech_cols

        # Select only columns that exist
        available_cols = [c for c in output_cols if c in final_df.columns]
        final_df = final_df[available_cols].copy()

        logger.write(f"\n  Output columns ({len(available_cols)}):")
        for col in available_cols:
            logger.write(f"    - {col}")

        # Save output
        output_file = paths["output_dir"] / "H6_CCCL_Speech.parquet"
        logger.write(f"\nSaving output to: {output_file}")
        final_df.to_parquet(output_file, index=False)

        logger.write(f"  Saved {len(final_df):,} observations")
        logger.write(f"  File size: {output_file.stat().st_size / 1024 / 1024:.1f} MB")

        # Compute statistics for stats.json
        logger.write("\n" + "="*80)
        logger.write("Computing Variable Statistics")
        logger.write("="*80)

        # CCCL coverage statistics
        cccl_coverage = {}
        for variant in cccl_variants:
            lag_col = f"{variant}_lag"
            if lag_col in final_df.columns:
                valid = final_df[lag_col].notna()
                cccl_coverage[variant] = {
                    "mean": float(final_df.loc[valid, lag_col].mean()),
                    "std": float(final_df.loc[valid, lag_col].std()),
                    "min": float(final_df.loc[valid, lag_col].min()),
                    "max": float(final_df.loc[valid, lag_col].max()),
                }

        # Uncertainty measures summary
        uncertainty_summary = {}
        for measure in uncertainty_measures:
            if measure in final_df.columns:
                valid = final_df[measure].notna()
                if valid.sum() > 0:
                    uncertainty_summary[measure] = {
                        "mean": float(final_df.loc[valid, measure].mean()),
                        "std": float(final_df.loc[valid, measure].std()),
                        "min": float(final_df.loc[valid, measure].min()),
                        "max": float(final_df.loc[valid, measure].max()),
                    }

        # Uncertainty gap statistics
        gap_stats = {}
        if "uncertainty_gap" in final_df.columns:
            valid_gap = final_df["uncertainty_gap"].notna()
            if valid_gap.sum() > 0:
                gap_stats = {
                    "mean": float(final_df.loc[valid_gap, "uncertainty_gap"].mean()),
                    "std": float(final_df.loc[valid_gap, "uncertainty_gap"].std()),
                    "min": float(final_df.loc[valid_gap, "uncertainty_gap"].min()),
                    "max": float(final_df.loc[valid_gap, "uncertainty_gap"].max()),
                }

        stats["output_stats"] = {
            "n_total_observations": int(len(final_df)),
            "n_firms": int(final_df["gvkey"].nunique()),
            "year_range": {
                "min": int(final_df["fiscal_year"].min()),
                "max": int(final_df["fiscal_year"].max()),
            },
            "cccl_coverage_by_variant": cccl_coverage,
            "uncertainty_measures_summary": uncertainty_summary,
            "uncertainty_gap_stats": gap_stats,
        }

        # Save stats.json
        stats_file = paths["output_dir"] / "stats.json"

        # Custom JSON encoder to handle numpy types
        class NumpyEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, np.integer):
                    return int(obj)
                if isinstance(obj, np.floating):
                    return float(obj)
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                return super().default(obj)

        with open(stats_file, "w") as f:
            json.dump(stats, f, indent=2, cls=NumpyEncoder)

        logger.write(f"\nSaved stats to: {stats_file}")

        # Final summary
        logger.write("\n" + "="*80)
        logger.write("EXECUTION COMPLETE")
        logger.write("="*80)
        logger.write(f"Output file: {output_file}")
        logger.write(f"Final sample: {len(final_df):,} observations")
        logger.write(f"Unique firms: {final_df['gvkey'].nunique():,}")
        logger.write(f"Year range: {final_df['fiscal_year'].min()}-{final_df['fiscal_year'].max()}")
        logger.write(f"End time: {datetime.now().isoformat()}")

        stats["end_time"] = datetime.now().isoformat()
        stats["status"] = "complete"

        # Update stats file with final status
        with open(stats_file, "w") as f:
            json.dump(stats, f, indent=2, cls=NumpyEncoder)

        return 0

    except Exception as e:
        logger.write(f"\nERROR: {e}")
        import traceback
        logger.write(traceback.format_exc())
        stats["status"] = "failed"
        stats["error"] = str(e)
        stats["end_time"] = datetime.now().isoformat()

        # Try to save stats even on failure
        try:
            stats_file = paths["output_dir"] / "stats.json"
            with open(stats_file, "w") as f:
                json.dump(stats, f, indent=2, cls=NumpyEncoder)
        except:
            pass

        return 1
    finally:
        logger.close()


if __name__ == "__main__":
    sys.exit(main())
