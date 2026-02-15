#!/usr/bin/env python3
"""
==============================================================================
STEP 3.5: H5 Analyst Dispersion Variables
==============================================================================
ID: 3.5_H5Variables
Description: Constructs H5 dependent variable (analyst forecast dispersion at t+1),
             control variables, and uncertainty gap measure for testing whether
             hedging language predicts analyst disagreement.

Variables Computed:
    - Analyst Dispersion (refined): STDEV / |MEANEST| with NUMEST >= 3, |MEANEST| >= 0.05
    - dispersion_lead: Next quarter's dispersion (DV - forward-looking timing)
    - prior_dispersion: Current quarter's dispersion (lagged DV - persistence control)
    - earnings_surprise: |ACTUAL - MEANEST| / |MEANEST| (confounding control)
    - analyst_coverage: NUMEST (log transform)
    - loss_dummy: 1 if NI < 0
    - uncertainty_gap: Manager_QA_Uncertainty_pct - Manager_Pres_Uncertainty_pct
    - Control variables merged from H1/H2: firm_size, leverage, tobins_q, earnings_volatility
    - All 6 speech uncertainty measures from Step 2 linguistic_variables

Inputs:
    - 4_Outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet
    - 1_Inputs/tr_ibes/tr_ibes.parquet (IBES analyst forecasts)
    - 1_Inputs/CRSPCompustat_CCM/CRSPCompustat_CCM.parquet (CUSIP-GVKEY linking)
    - 1_Inputs/comp_na_daily_all/comp_na_daily_all.parquet (Compustat - for loss dummy)
    - 4_Outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_*.parquet (speech measures)
    - 4_Outputs/3_Financial_V2/latest/H1_CashHoldings.parquet (control variables)
    - 4_Outputs/3_Financial_V2/latest/H2_InvestmentEfficiency.parquet (control variables)

Outputs:
    - 4_Outputs/3_Financial_V2/3.5_H5Variables/{timestamp}/H5_AnalystDispersion.parquet
    - 4_Outputs/3_Financial_V2/3.5_H5Variables/{timestamp}/stats.json

Deterministic: true
Dependencies:
    - Requires: Step 2.2
    - Uses: shared.financial_utils, pandas, numpy

Author: Thesis Author
Date: 2026-02-11
==============================================================================
"""

import argparse
import json
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd
import yaml

# Import shared path validation utilities
# Import DualWriter from f1d.shared.observability_utils
from f1d.shared.observability_utils import (
    DualWriter,
    compute_file_checksum,
)
from f1d.shared.path_utils import (
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
    # Go up from src/f1d/financial/v2/ to project root (5 levels)
    root = Path(__file__).parent.parent.parent.parent.parent

    # Resolve manifest directory using timestamp-based resolution
    manifest_dir = get_latest_output_dir(
        root / "4_Outputs" / "1.4_AssembleManifest",
        required_file="master_sample_manifest.parquet",
    )

    # Resolve H1 and H2 outputs for control variables
    h1_dir = get_latest_output_dir(
        root / "4_Outputs" / "3_Financial_V2",
        required_file="H1_CashHoldings.parquet",
    )

    h2_dir = get_latest_output_dir(
        root / "4_Outputs" / "3_Financial_V2",
        required_file="H2_InvestmentEfficiency.parquet",
    )

    # Resolve linguistic variables directory
    linguistics_dir = get_latest_output_dir(
        root / "4_Outputs" / "2_Textual_Analysis" / "2.2_Variables",
    )

    paths = {
        "root": root,
        "manifest_dir": manifest_dir,
        "h1_dir": h1_dir,
        "h2_dir": h2_dir,
        "linguistics_dir": linguistics_dir,
        "ibes_file": root / "1_Inputs" / "tr_ibes" / "tr_ibes.parquet",
        "ccm_file": root
        / "1_Inputs"
        / "CRSPCompustat_CCM"
        / "CRSPCompustat_CCM.parquet",
        "compustat_file": root
        / "1_Inputs"
        / "comp_na_daily_all"
        / "comp_na_daily_all.parquet",
    }

    # Output directory
    output_base = root / "4_Outputs" / "3_Financial_V2" / "3.5_H5Variables"
    paths["output_dir"] = output_base / timestamp
    ensure_output_dir(paths["output_dir"])

    # Log directory
    log_base = root / "3_Logs" / "3_Financial_V2"
    ensure_output_dir(log_base)
    paths["log_file"] = log_base / f"{timestamp}_H5.log"

    return paths


# ==============================================================================
# Data Loading
# ==============================================================================


def load_manifest(manifest_dir, logger):
    """Load manifest data - the universe of firm-years in sample"""
    manifest_file = manifest_dir / "master_sample_manifest.parquet"
    if not manifest_file.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_file}")

    validate_input_file(manifest_file, must_exist=True)
    df = pd.read_parquet(manifest_file)

    logger.write(f"Loaded manifest: {len(df):,} observations")
    logger.write(f"  Columns: {df.columns.tolist()}")

    return df


def load_ibes(ibes_file, logger, numest_min=3, meanest_min=0.05):
    """Load IBES analyst forecast data using memory-efficient chunked processing

    For large IBES files (>20M rows), we aggregate to CUSIP8-period level within
    each row group to dramatically reduce memory usage before concatenating.
    """
    logger.write(f"\nLoading IBES data from: {ibes_file}")
    validate_input_file(ibes_file, must_exist=True)

    # Compute checksum first (file-level, not content)
    checksum = compute_file_checksum(ibes_file)
    logger.write(f"  IBES checksum: {checksum}")

    # Use PyArrow for memory-efficient reading
    try:
        import pyarrow.parquet as pq

        logger.write("  Reading with PyArrow (aggregated by row group)...")

        # Read only required columns
        cols = ["CUSIP", "FPEDATS", "FISCALP", "NUMEST", "MEANEST", "STDEV", "ACTUAL"]

        # Open file
        parquet_file = pq.ParquetFile(ibes_file)

        # Get total rows
        total_rows = parquet_file.metadata.num_rows
        logger.write(f"  Total IBES rows: {total_rows:,}")

        # Read in batches, aggregate within each batch, then combine
        logger.write("  Reading and aggregating row groups...")

        all_chunks = []
        num_row_groups = parquet_file.num_row_groups
        logger.write(f"  Row groups: {num_row_groups}")

        for i in range(num_row_groups):
            # Read one row group at a time
            table = parquet_file.read_row_group(i, columns=cols)

            # Convert to pandas
            chunk = table.to_pandas()

            # Apply filters (filter out placeholder CUSIPs)
            chunk = chunk[chunk["NUMEST"] >= numest_min].copy()
            chunk = chunk[chunk["MEANEST"].abs() >= meanest_min].copy()
            chunk = chunk.dropna(subset=["STDEV", "MEANEST", "FPEDATS", "CUSIP"])

            if len(chunk) == 0:
                continue

            # Extract CUSIP8 BEFORE converting to string
            # This ensures we can filter out invalid CUSIPs
            chunk["cusip8"] = chunk["CUSIP"].astype(str).str[:8]

            # Filter out invalid CUSIP8 values (placeholders)
            chunk = chunk[
                ~chunk["cusip8"].isin(["00000000", "nan", "NaN", "None"])
            ].copy()

            if len(chunk) == 0:
                continue

            # Compute dispersion within chunk
            chunk["dispersion"] = chunk["STDEV"] / chunk["MEANEST"].abs()

            # Extract fiscal period
            chunk["fpedats"] = pd.to_datetime(chunk["FPEDATS"])
            chunk["fiscal_year"] = chunk["fpedats"].dt.year
            chunk["fiscal_quarter"] = chunk["fpedats"].dt.quarter

            # Take the most recent forecast per CUSIP8-period (aggregate!)
            chunk = chunk.sort_values(
                ["cusip8", "fiscal_year", "fiscal_quarter", "FPEDATS"],
                ascending=[True, True, True, False],
            )
            chunk = chunk.drop_duplicates(
                subset=["cusip8", "fiscal_year", "fiscal_quarter"], keep="first"
            )

            # Select only columns we need
            chunk_agg = chunk[
                [
                    "cusip8",
                    "fiscal_year",
                    "fiscal_quarter",
                    "dispersion",
                    "NUMEST",
                    "MEANEST",
                    "STDEV",
                    "ACTUAL",
                ]
            ].copy()

            all_chunks.append(chunk_agg)

            if (i + 1) % 5 == 0 or i == num_row_groups - 1:
                kept = sum(len(c) for c in all_chunks)
                logger.write(
                    f"  Processed {i + 1}/{num_row_groups} row groups, aggregated to {kept:,} unique CUSIP8-periods"
                )

        # Concatenate aggregated chunks (much smaller now)
        if all_chunks:
            df = pd.concat(all_chunks, ignore_index=True)
            logger.write(f"  Final: {len(df):,} unique CUSIP8-period observations")
        else:
            logger.write("  Warning: No data passed filters!")
            df = pd.DataFrame(columns=cols)

    except ImportError:
        logger.write("  PyArrow not available, using pandas...")
        # Fallback: Use pandas with chunked reading
        cols = ["CUSIP", "FPEDATS", "FISCALP", "NUMEST", "MEANEST", "STDEV", "ACTUAL"]

        chunks = []
        for chunk in pd.read_parquet(ibes_file, columns=cols, chunksize=1000000):
            # Apply filters
            chunk = chunk[chunk["NUMEST"] >= numest_min].copy()
            chunk = chunk[chunk["MEANEST"].abs() >= meanest_min].copy()
            chunk = chunk.dropna(subset=["STDEV", "MEANEST", "FPEDATS", "CUSIP"])
            if len(chunk) == 0:
                continue

            # Extract CUSIP8 and filter invalid values
            chunk["cusip8"] = chunk["CUSIP"].astype(str).str[:8]
            chunk = chunk[
                ~chunk["cusip8"].isin(["00000000", "nan", "NaN", "None"])
            ].copy()
            if len(chunk) == 0:
                continue

            # Same aggregation logic as above
            chunk["dispersion"] = chunk["STDEV"] / chunk["MEANEST"].abs()
            chunk["fpedats"] = pd.to_datetime(chunk["FPEDATS"])
            chunk["fiscal_year"] = chunk["fpedats"].dt.year
            chunk["fiscal_quarter"] = chunk["fpedats"].dt.quarter

            chunk = chunk.sort_values(
                ["cusip8", "fiscal_year", "fiscal_quarter", "FPEDATS"],
                ascending=[True, True, True, False],
            )
            chunk = chunk.drop_duplicates(
                subset=["cusip8", "fiscal_year", "fiscal_quarter"], keep="first"
            )

            chunks.append(
                chunk[
                    [
                        "cusip8",
                        "fiscal_year",
                        "fiscal_quarter",
                        "dispersion",
                        "NUMEST",
                        "MEANEST",
                        "STDEV",
                        "ACTUAL",
                    ]
                ]
            )

        if chunks:
            df = pd.concat(chunks, ignore_index=True)
            logger.write(f"  Loaded {len(df):,} unique CUSIP8-period observations")
        else:
            df = pd.DataFrame(
                columns=[
                    "cusip8",
                    "fiscal_year",
                    "fiscal_quarter",
                    "dispersion",
                    "NUMEST",
                    "MEANEST",
                    "STDEV",
                    "ACTUAL",
                ]
            )

    except Exception as e:
        logger.write(f"  Error reading IBES: {e}")
        import traceback

        logger.write(traceback.format_exc())
        raise

    return df, checksum


def load_ccm(ccm_file, logger):
    """Load CRSP-Compustat Merged file for CUSIP-GVKEY linking"""
    logger.write(f"\nLoading CCM data from: {ccm_file}")

    if not ccm_file.exists():
        logger.write("  Warning: CCM file not found, will use direct CUSIP matching")
        return None

    validate_input_file(ccm_file, must_exist=True)
    df = pd.read_parquet(ccm_file)

    logger.write(f"  Loaded {len(df):,} CCM links")
    logger.write(f"  Columns: {df.columns.tolist()}")

    # Compute checksum
    checksum = compute_file_checksum(ccm_file)
    logger.write(f"  CCM checksum: {checksum}")

    return df, checksum


def load_compustat(compustat_file, logger):
    """Load Compustat data for loss dummy computation"""
    logger.write(f"\nLoading Compustat data from: {compustat_file}")
    validate_input_file(compustat_file, must_exist=True)

    # Load required columns
    cols = ["gvkey", "cusip", "fyearq", "fqtr", "datadate", "niq", "atq"]
    df = pd.read_parquet(compustat_file, columns=cols)

    logger.write(f"  Loaded {len(df):,} Compustat quarterly observations")

    return df


def load_linguistic_variables(linguistics_dir, logger):
    """Load linguistic variables from all years"""
    logger.write(f"\nLoading linguistic variables from: {linguistics_dir}")

    # Find all linguistic_variables_*.parquet files
    parquet_files = sorted(linguistics_dir.glob("linguistic_variables_*.parquet"))

    if not parquet_files:
        raise FileNotFoundError(
            f"No linguistic_variables files found in {linguistics_dir}"
        )

    dfs = []
    for pf in parquet_files:
        df = pd.read_parquet(pf)
        dfs.append(df)

    combined = pd.concat(dfs, ignore_index=True)

    logger.write(f"  Loaded {len(dfs)} yearly files")
    logger.write(f"  Total observations: {len(combined):,}")

    # Key columns needed
    speech_cols = [
        "file_name",
        "start_date",
        "gvkey",
        "Manager_QA_Uncertainty_pct",
        "Manager_QA_Weak_Modal_pct",
        "Manager_Pres_Uncertainty_pct",
        "Manager_Pres_Weak_Modal_pct",
        "CEO_QA_Uncertainty_pct",
        "CEO_QA_Weak_Modal_pct",
        "CEO_Pres_Uncertainty_pct",
        "CEO_Pres_Weak_Modal_pct",
    ]

    # Check which columns exist
    available_cols = [c for c in speech_cols if c in combined.columns]
    missing_cols = set(speech_cols) - set(available_cols)

    if missing_cols:
        logger.write(f"  Warning: Missing columns: {missing_cols}")

    return combined[available_cols].copy()


def load_h1_controls(h1_dir, logger):
    """Load H1 control variables (firm_size, leverage)"""
    h1_file = h1_dir / "H1_CashHoldings.parquet"
    logger.write(f"\nLoading H1 controls from: {h1_file}")
    validate_input_file(h1_file, must_exist=True)

    df = pd.read_parquet(h1_file)

    logger.write(f"  Loaded {len(df):,} H1 observations")

    # Extract control variables
    controls = ["gvkey", "fiscal_year", "firm_size", "leverage", "tobins_q"]
    available_controls = [c for c in controls if c in df.columns]

    return df[available_controls].copy()


def load_h2_controls(h2_dir, logger):
    """Load H2 control variables (earnings_volatility, tobins_q)"""
    h2_file = h2_dir / "H2_InvestmentEfficiency.parquet"
    logger.write(f"\nLoading H2 controls from: {h2_file}")
    validate_input_file(h2_file, must_exist=True)

    df = pd.read_parquet(h2_file)

    logger.write(f"  Loaded {len(df):,} H2 observations")

    # Extract control variables
    controls = ["gvkey", "fiscal_year", "earnings_volatility", "tobins_q"]
    available_controls = [c for c in controls if c in df.columns]

    return df[available_controls].copy()


# ==============================================================================
# Analyst Dispersion Computation
# ==============================================================================


def compute_analyst_dispersion(ibes_df, ccm_df, logger, numest_min=3, meanest_min=0.05):
    """
    Process analyst forecast dispersion with forward-looking timing.

    Note: Data is already pre-aggregated in load_ibes() to reduce memory.
    This function handles CCM linking and winsorization.

    Forward-looking: Speech_t predicts Dispersion_{t+1}
    """
    logger.write("\n" + "=" * 80)
    logger.write("Processing Analyst Dispersion (H5 Dependent Variable)")
    logger.write("=" * 80)

    # Data is already aggregated from load_ibes
    df = ibes_df.copy()

    # Check if we have raw or pre-aggregated data
    if "CUSIP" in df.columns:
        # Raw data path - need to compute dispersion
        logger.write(f"  Processing raw IBES data: {len(df):,} observations")

        # Extract CUSIP8
        df["cusip8"] = df["CUSIP"].astype(str).str[:8]

        # Compute dispersion
        df["dispersion"] = df["STDEV"] / df["MEANEST"].abs()

        # Extract fiscal period
        df["fpedats"] = pd.to_datetime(df["FPEDATS"])
        df["fiscal_year"] = df["fpedats"].dt.year
        df["fiscal_quarter"] = df["fpedats"].dt.quarter

        # Aggregate to CUSIP8-period
        df = df.sort_values(
            ["cusip8", "fiscal_year", "fiscal_quarter", "FPEDATS"],
            ascending=[True, True, True, False],
        )
        df = df.drop_duplicates(
            subset=["cusip8", "fiscal_year", "fiscal_quarter"], keep="first"
        )

        # Select columns
        df = df[
            [
                "cusip8",
                "fiscal_year",
                "fiscal_quarter",
                "dispersion",
                "NUMEST",
                "MEANEST",
                "STDEV",
                "ACTUAL",
            ]
        ].copy()
    else:
        # Pre-aggregated data from load_ibes
        logger.write(
            f"  Using pre-aggregated data: {len(df):,} unique CUSIP8-period observations"
        )

        # Verify required columns
        required = ["cusip8", "fiscal_year", "fiscal_quarter", "dispersion"]
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

    logger.write(f"\n  Unique CUSIP8-period observations: {len(df):,}")

    # Winsorize at 1%/99%
    p1 = df["dispersion"].quantile(0.01)
    p99 = df["dispersion"].quantile(0.99)
    df["dispersion_winsorized"] = df["dispersion"].clip(lower=p1, upper=p99)

    logger.write("\n  Dispersion statistics (before winsorization):")
    logger.write(f"    Mean: {df['dispersion'].mean():.4f}")
    logger.write(f"    Std: {df['dispersion'].std():.4f}")
    logger.write(f"    Min: {df['dispersion'].min():.4f}")
    logger.write(f"    Max: {df['dispersion'].max():.4f}")
    logger.write(f"    P1: {p1:.4f}, P99: {p99:.4f}")

    logger.write("\n  Dispersion statistics (after winsorization):")
    logger.write(f"    Mean: {df['dispersion_winsorized'].mean():.4f}")
    logger.write(f"    Std: {df['dispersion_winsorized'].std():.4f}")
    logger.write(f"    Min: {df['dispersion_winsorized'].min():.4f}")
    logger.write(f"    Max: {df['dispersion_winsorized'].max():.4f}")

    # Create dataframe for merging
    dispersion_df = df[
        [
            "cusip8",
            "fiscal_year",
            "fiscal_quarter",
            "dispersion_winsorized",
            "NUMEST",
            "MEANEST",
            "STDEV",
            "ACTUAL",
        ]
    ].rename(columns={"dispersion_winsorized": "dispersion"})

    # Link to GVKEY using CCM
    if ccm_df is not None:
        logger.write("\nLinking IBES CUSIP8 to Compustat GVKEY via CCM...")

        # Extract CUSIP8 from CCM
        ccm = ccm_df.copy()
        ccm["cusip8"] = ccm["cusip"].astype(str).str[:8]

        # Convert GVKEY to string with leading zeros (6-digit format)
        # This ensures compatibility with Compustat and speech data
        ccm["gvkey"] = ccm["gvkey"].astype(str).str.zfill(6)

        # Create lookup: cusip8 -> gvkey (using LINKPRIM='P' for primary link)
        # LINKPRIM is a string: 'P'=Primary, 'C'=CompuSTAT, 'J'=Justification, 'N'=None
        ccm_primary = ccm[ccm["LINKPRIM"] == "P"].copy()
        cusip_to_gvkey = ccm_primary.drop_duplicates(subset=["cusip8"], keep="first")[
            ["cusip8", "gvkey"]
        ]

        # Merge
        dispersion_df = dispersion_df.merge(cusip_to_gvkey, on="cusip8", how="left")

        n_matched = dispersion_df["gvkey"].notna().sum()
        logger.write(f"  Matched {n_matched:,} observations to GVKEY")
        logger.write(f"  Unmatched: {len(dispersion_df) - n_matched:,}")
    else:
        logger.write("\nWarning: No CCM file available, skipping GVKEY linking")
        dispersion_df["gvkey"] = np.nan

    return dispersion_df


def create_forward_looking_dispersion(dispersion_df, logger):
    """
    Create forward-looking dispersion variables.

    - prior_dispersion: Current quarter dispersion (lagged DV)
    - dispersion_lead: Next quarter dispersion (DV)

    Speech at quarter t predicts dispersion at quarter t+1.
    """
    logger.write("\n" + "=" * 80)
    logger.write("Creating Forward-Looking Dispersion Variables")
    logger.write("=" * 80)

    # Filter to observations with valid GVKEY
    df = dispersion_df[dispersion_df["gvkey"].notna()].copy()

    logger.write(f"  Observations with valid GVKEY: {len(df):,}")

    # Sort by gvkey, fiscal_year, fiscal_quarter
    df = df.sort_values(["gvkey", "fiscal_year", "fiscal_quarter"])

    # Create prior_dispersion (current quarter)
    df["prior_dispersion"] = df["dispersion"]

    # Create dispersion_lead (next quarter) - shift(-1) gets next quarter
    df["dispersion_lead"] = df.groupby("gvkey")["dispersion"].shift(-1)

    logger.write(
        f"\n  Observations with dispersion_lead (t+1): {df['dispersion_lead'].notna().sum():,}"
    )
    logger.write(
        f"  Observations without lead (last quarter for firm): {df['dispersion_lead'].isna().sum():,}"
    )

    # Compute persistence correlation
    valid = df[["prior_dispersion", "dispersion_lead"]].dropna()
    if len(valid) > 0:
        persistence = valid["prior_dispersion"].corr(valid["dispersion_lead"])
        logger.write(f"\n  Dispersion persistence (correlation): {persistence:.4f}")

    return df


# ==============================================================================
# Earnings Surprise Computation
# ==============================================================================


def compute_earnings_surprise(dispersion_df, logger):
    """
    Compute earnings surprise = |ACTUAL - MEANEST| / |MEANEST|

    This is determined BEFORE the earnings call (it's the announced results),
    so it's a confounding control, not a mediator.
    """
    logger.write("\n" + "=" * 80)
    logger.write("Computing Earnings Surprise")
    logger.write("=" * 80)

    df = dispersion_df.copy()

    # Compute earnings surprise
    df["earnings_surprise"] = (df["ACTUAL"] - df["MEANEST"]).abs() / df["MEANEST"].abs()

    # Winsorize at 1%/99%
    p1 = df["earnings_surprise"].quantile(0.01)
    p99 = df["earnings_surprise"].quantile(0.99)
    df["earnings_surprise"] = df["earnings_surprise"].clip(lower=p1, upper=p99)

    logger.write("\n  Earnings surprise statistics:")
    logger.write(f"    Mean: {df['earnings_surprise'].mean():.4f}")
    logger.write(f"    Std: {df['earnings_surprise'].std():.4f}")
    logger.write(f"    Min: {df['earnings_surprise'].min():.4f}")
    logger.write(f"    Max: {df['earnings_surprise'].max():.4f}")

    return df[["gvkey", "fiscal_year", "fiscal_quarter", "earnings_surprise"]].copy()


# ==============================================================================
# Loss Dummy Computation
# ==============================================================================


def compute_loss_dummy(compustat_df, dispersion_df, logger):
    """
    Compute loss dummy = 1 if NI < 0.

    Merges from Compustat quarterly data.
    """
    logger.write("\n" + "=" * 80)
    logger.write("Computing Loss Dummy")
    logger.write("=" * 80)

    # Filter Compustat to required columns
    comp = compustat_df[["gvkey", "fyearq", "fqtr", "niq"]].dropna().copy()

    # Create loss dummy
    comp["loss_dummy"] = (comp["niq"] < 0).astype(int)

    # Rename for merging
    comp["fiscal_year"] = comp["fyearq"]
    comp["fiscal_quarter"] = comp["fqtr"]

    # Get unique gvkey-year-quarter combinations
    loss_df = comp.drop_duplicates(subset=["gvkey", "fiscal_year", "fiscal_quarter"])

    logger.write(f"  Loss dummy observations: {len(loss_df):,}")
    logger.write(
        f"  Loss firms: {loss_df['loss_dummy'].sum():,} ({loss_df['loss_dummy'].mean() * 100:.1f}%)"
    )

    return loss_df[["gvkey", "fiscal_year", "fiscal_quarter", "loss_dummy"]].copy()


# ==============================================================================
# Merge Speech Measures
# ==============================================================================


def merge_speech_measures(speech_df, dispersion_df, logger):
    """
    Merge speech measures from linguistic variables.

    The start_date in linguistic variables needs to be matched to fiscal quarter.
    """
    logger.write("\n" + "=" * 80)
    logger.write("Merging Speech Measures")
    logger.write("=" * 80)

    # Convert start_date to datetime
    speech = speech_df.copy()
    speech["start_date"] = pd.to_datetime(speech["start_date"])

    # Extract fiscal year and quarter from start_date
    # Earnings calls typically occur after quarter end
    speech["fiscal_year"] = speech["start_date"].dt.year
    speech["fiscal_quarter"] = speech["start_date"].dt.quarter

    # Handle year rollover (calls in Jan-Mar are typically for previous year Q4)
    # For simplicity, we'll use calendar year

    # Get unique gvkey-year-quarter with speech measures (take mean if multiple)
    speech_cols = [
        c
        for c in speech.columns
        if "pct" in c or c in ["gvkey", "fiscal_year", "fiscal_quarter"]
    ]

    speech_agg = (
        speech[speech_cols]
        .groupby(["gvkey", "fiscal_year", "fiscal_quarter"])
        .mean()
        .reset_index()
    )

    logger.write(f"  Speech observations: {len(speech_agg):,}")

    # Check which speech measures are available
    available_measures = [c for c in speech_agg.columns if "pct" in c]
    logger.write(f"  Available speech measures: {len(available_measures)}")
    for m in [
        "Manager_QA_Uncertainty_pct",
        "Manager_QA_Weak_Modal_pct",
        "Manager_Pres_Uncertainty_pct",
        "CEO_QA_Uncertainty_pct",
    ]:
        if m in available_measures:
            non_null = speech_agg[m].notna().sum()
            logger.write(f"    {m}: {non_null:,} non-null")

    # Merge with dispersion data
    merged = dispersion_df.merge(
        speech_agg, on=["gvkey", "fiscal_year", "fiscal_quarter"], how="left"
    )

    n_merged = merged[available_measures].notna().any(axis=1).sum()
    logger.write(f"\n  Merged speech measures: {n_merged:,} observations")
    logger.write(f"  No speech data: {len(merged) - n_merged:,}")

    return merged


def compute_uncertainty_gap(merged_df, logger):
    """
    Compute uncertainty gap = Manager_QA_Uncertainty_pct - Manager_Pres_Uncertainty_pct

    Gap > 0: Manager more uncertain in spontaneous speech (Q&A)
    Gap < 0: Manager more uncertain in prepared remarks (Presentation)
    """
    logger.write("\n" + "=" * 80)
    logger.write("Computing Uncertainty Gap (H5-B)")
    logger.write("=" * 80)

    df = merged_df.copy()

    # Compute uncertainty gap
    if (
        "Manager_QA_Uncertainty_pct" in df.columns
        and "Manager_Pres_Uncertainty_pct" in df.columns
    ):
        df["uncertainty_gap"] = (
            df["Manager_QA_Uncertainty_pct"] - df["Manager_Pres_Uncertainty_pct"]
        )

        logger.write("\n  Uncertainty gap statistics:")
        logger.write(f"    Mean: {df['uncertainty_gap'].mean():.4f}")
        logger.write(f"    Std: {df['uncertainty_gap'].std():.4f}")
        logger.write(f"    Min: {df['uncertainty_gap'].min():.4f}")
        logger.write(f"    Max: {df['uncertainty_gap'].max():.4f}")

        # Percentage positive vs negative
        pos_gap = (df["uncertainty_gap"] > 0).sum()
        neg_gap = (df["uncertainty_gap"] < 0).sum()
        logger.write(
            f"\n    Positive gap (more uncertain in Q&A): {pos_gap:,} ({pos_gap / df['uncertainty_gap'].notna().sum() * 100:.1f}%)"
        )
        logger.write(
            f"    Negative gap (more uncertain in Pres): {neg_gap:,} ({neg_gap / df['uncertainty_gap'].notna().sum() * 100:.1f}%)"
        )
    else:
        logger.write(
            "  Warning: Cannot compute uncertainty_gap - missing required columns"
        )
        df["uncertainty_gap"] = np.nan

    return df


# ==============================================================================
# Merge Control Variables
# ==============================================================================


def merge_control_variables(merged_df, h1_df, h2_df, logger):
    """
    Merge control variables from H1 and H2 outputs.
    """
    logger.write("\n" + "=" * 80)
    logger.write("Merging Control Variables")
    logger.write("=" * 80)

    df = merged_df.copy()

    # Merge H1 controls (firm_size, leverage)
    if h1_df is not None:
        h1_cols = ["gvkey", "fiscal_year"]
        available_h1 = [
            c
            for c in h1_df.columns
            if c in ["firm_size", "leverage", "tobins_q", "roa", "capex_at"]
        ]
        h1_merge = h1_df[h1_cols + available_h1].drop_duplicates()

        df = df.merge(h1_merge, on=["gvkey", "fiscal_year"], how="left")
        logger.write(f"  Merged H1 controls: {available_h1}")

    # Merge H2 controls (earnings_volatility, tobins_q if not in H1)
    if h2_df is not None:
        h2_cols = ["gvkey", "fiscal_year"]
        available_h2 = [
            c
            for c in h2_df.columns
            if c in ["earnings_volatility", "tobins_q", "cf_volatility"]
        ]
        h2_merge = h2_df[h2_cols + available_h2].drop_duplicates()

        df = df.merge(h2_merge, on=["gvkey", "fiscal_year"], how="left")
        logger.write(f"  Merged H2 controls: {available_h2}")

    return df


# ==============================================================================
# Final Output Preparation
# ==============================================================================


def prepare_final_dataset(df, logger):
    """
    Prepare final H5 analysis dataset.

    Required columns:
        - gvkey, fiscal_year, fiscal_quarter
        - dispersion_lead (DV - next quarter)
        - prior_dispersion (lagged DV - current quarter)
        - earnings_surprise
        - analyst_coverage (NUMEST)
        - loss_dummy
        - uncertainty_gap
        - firm_size, leverage, tobins_q, earnings_volatility
        - All 6 speech uncertainty measures
    """
    logger.write("\n" + "=" * 80)
    logger.write("Preparing Final H5 Analysis Dataset")
    logger.write("=" * 80)

    # Define required columns
    id_cols = ["gvkey", "fiscal_year", "fiscal_quarter"]
    dv_cols = ["dispersion_lead", "prior_dispersion"]
    control_cols = [
        "earnings_surprise",
        "loss_dummy",
        "firm_size",
        "leverage",
        "tobins_q",
        "earnings_volatility",
    ]

    # Speech measures - all uncertainty-related
    speech_measure_cols = [
        "Manager_QA_Uncertainty_pct",
        "Manager_QA_Weak_Modal_pct",
        "Manager_Pres_Uncertainty_pct",
        "Manager_Pres_Weak_Modal_pct",
        "CEO_QA_Uncertainty_pct",
        "CEO_QA_Weak_Modal_pct",
        "uncertainty_gap",
    ]

    # Get analyst coverage from NUMEST (log transform)
    if "NUMEST" in df.columns:
        df["analyst_coverage"] = np.log(df["NUMEST"])
        control_cols.append("analyst_coverage")

    # Build column list (only include existing columns)
    output_cols = id_cols + dv_cols + control_cols
    existing_speech = [c for c in speech_measure_cols if c in df.columns]
    output_cols.extend(existing_speech)

    # Filter to observations with dispersion_lead (forward-looking)
    df_final = df[df["dispersion_lead"].notna()].copy()

    logger.write(f"\n  Final sample size: {len(df_final):,} observations")

    # Count unique firms
    n_firms = df_final["gvkey"].nunique()
    logger.write(f"  Unique firms: {n_firms:,}")

    # Average quarters per firm
    avg_quarters = len(df_final) / n_firms if n_firms > 0 else 0
    logger.write(f"  Average quarters per firm: {avg_quarters:.1f}")

    # Check missing data for key variables
    logger.write("\n  Missing data analysis:")
    for col in dv_cols + control_cols[:4]:
        if col in df_final.columns:
            n_missing = df_final[col].isna().sum()
            n_total = len(df_final)
            logger.write(
                f"    {col}: {n_missing:,} missing ({n_missing / n_total * 100:.1f}%)"
            )

    # Select output columns
    available_cols = [c for c in output_cols if c in df_final.columns]
    df_final = df_final[available_cols].copy()

    logger.write(f"\n  Output columns ({len(available_cols)}):")
    for col in available_cols:
        logger.write(f"    - {col}")

    # Check sample size warning
    if len(df_final) < 2000:
        logger.write("\n  WARNING: Sample size < 2,000. May need to relax filters.")
    elif len(df_final) < 5000:
        logger.write("\n  WARNING: Sample size < 5,000. Consider relaxing filters.")

    return df_final


# ==============================================================================
# Main Execution
# ==============================================================================


def main() -> int:
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="Construct H5 Analyst Dispersion Variables",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python 3.5_H5Variables.py              # Run with default settings
  python 3.5_H5Variables.py --dry-run    # Validate inputs without processing
  python 3.5_H5Variables.py --numest-min 2  # Use NUMEST >= 2 instead of 3
        """,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and print planned operations without processing",
    )
    parser.add_argument(
        "--numest-min",
        type=int,
        default=3,
        help="Minimum NUMEST threshold (default: 3)",
    )
    parser.add_argument(
        "--meanest-min",
        type=float,
        default=0.05,
        help="Minimum |MEANEST| threshold (default: 0.05)",
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
    logger.write("STEP 3.5: H5 Analyst Dispersion Variables")
    logger.write("=" * 80)
    logger.write(f"Start time: {datetime.now().isoformat()}")
    logger.write(f"Timestamp: {timestamp}")
    logger.write(f"Python version: {sys.version}")

    if args.dry_run:
        logger.write("\n" + "=" * 80)
        logger.write("DRY RUN MODE - Validating inputs only")
        logger.write("=" * 80)

    # Stats collection
    stats: Dict[str, Any] = {
        "timestamp": timestamp,
        "script_id": "3.5_H5Variables",
        "start_time": datetime.now().isoformat(),
        "parameters": {
            "numest_min": args.numest_min,
            "meanest_min": args.meanest_min,
        },
        "input_files": {},
        "processing_steps": {},
        "output_stats": {},
    }

    try:
        # Step 1: Load inputs
        logger.write("\n" + "=" * 80)
        logger.write("STEP 1: Loading Input Data")
        logger.write("=" * 80)

        manifest = load_manifest(paths["manifest_dir"], logger)
        stats["input_files"]["manifest"] = {
            "path": str(paths["manifest_dir"]),
            "rows": len(manifest),
        }

        ibes_df, ibes_checksum = load_ibes(
            paths["ibes_file"],
            logger,
            numest_min=args.numest_min,
            meanest_min=args.meanest_min,
        )
        stats["input_files"]["ibes"] = {
            "path": str(paths["ibes_file"]),
            "rows": len(ibes_df),
            "checksum": ibes_checksum,
        }

        ccm_result = load_ccm(paths["ccm_file"], logger)
        if ccm_result is not None:
            ccm_df, ccm_checksum = ccm_result
            stats["input_files"]["ccm"] = {
                "path": str(paths["ccm_file"]),
                "rows": len(ccm_df),
                "checksum": ccm_checksum,
            }
        else:
            ccm_df = None

        compustat_df = load_compustat(paths["compustat_file"], logger)
        stats["input_files"]["compustat"] = {
            "path": str(paths["compustat_file"]),
            "rows": len(compustat_df),
        }

        speech_df = load_linguistic_variables(paths["linguistics_dir"], logger)
        stats["input_files"]["linguistic_variables"] = {
            "path": str(paths["linguistics_dir"]),
            "rows": len(speech_df),
        }

        h1_df = load_h1_controls(paths["h1_dir"], logger)
        stats["input_files"]["h1_controls"] = {
            "path": str(paths["h1_dir"]),
            "rows": len(h1_df),
        }

        h2_df = load_h2_controls(paths["h2_dir"], logger)
        stats["input_files"]["h2_controls"] = {
            "path": str(paths["h2_dir"]),
            "rows": len(h2_df),
        }

        if args.dry_run:
            logger.write("\n" + "=" * 80)
            logger.write("DRY RUN COMPLETE - All inputs validated successfully")
            logger.write("=" * 80)
            logger.write("\nPlanned operations:")
            logger.write("  1. Compute analyst dispersion with filters:")
            logger.write(f"     - NUMEST >= {args.numest_min}")
            logger.write(f"     - |MEANEST| >= {args.meanest_min}")
            logger.write("  2. Winsorize dispersion at 1%/99%")
            logger.write("  3. Link IBES to GVKEY via CCM")
            logger.write("  4. Create forward-looking dispersion_lead (t+1)")
            logger.write(
                "  5. Compute earnings_surprise = |ACTUAL - MEANEST| / |MEANEST|"
            )
            logger.write("  6. Compute loss_dummy from Compustat")
            logger.write("  7. Merge speech measures from linguistic variables")
            logger.write(
                "  8. Compute uncertainty_gap = QA_Uncertainty - Pres_Uncertainty"
            )
            logger.write("  9. Merge control variables from H1/H2")
            logger.write("  10. Output H5_AnalystDispersion.parquet")
            return 0

        # Step 2: Compute analyst dispersion
        dispersion_df = compute_analyst_dispersion(
            ibes_df,
            ccm_df,
            logger,
            numest_min=args.numest_min,
            meanest_min=args.meanest_min,
        )
        stats["processing_steps"]["analyst_dispersion"] = {
            "rows": len(dispersion_df),
            "gvkey_matched": dispersion_df["gvkey"].notna().sum(),
        }

        # Step 3: Create forward-looking dispersion
        forward_df = create_forward_looking_dispersion(dispersion_df, logger)

        # Step 4: Compute earnings surprise
        surprise_df = compute_earnings_surprise(forward_df, logger)

        # Step 5: Compute loss dummy
        loss_df = compute_loss_dummy(compustat_df, forward_df, logger)

        # Step 6: Merge all components
        logger.write("\n" + "=" * 80)
        logger.write("Merging All Variables")
        logger.write("=" * 80)

        # Start with forward dispersion
        merged = forward_df[
            [
                "gvkey",
                "fiscal_year",
                "fiscal_quarter",
                "dispersion",
                "prior_dispersion",
                "dispersion_lead",
                "NUMEST",
            ]
        ].copy()

        # Merge earnings surprise
        merged = merged.merge(
            surprise_df, on=["gvkey", "fiscal_year", "fiscal_quarter"], how="left"
        )
        logger.write(f"  After merging earnings_surprise: {len(merged):,}")

        # Merge loss dummy
        merged = merged.merge(
            loss_df, on=["gvkey", "fiscal_year", "fiscal_quarter"], how="left"
        )
        logger.write(f"  After merging loss_dummy: {len(merged):,}")

        # Step 7: Merge speech measures
        merged = merge_speech_measures(speech_df, merged, logger)

        # Step 8: Compute uncertainty gap
        merged = compute_uncertainty_gap(merged, logger)

        # Step 9: Merge control variables
        merged = merge_control_variables(merged, h1_df, h2_df, logger)

        # Step 10: Prepare final dataset
        final_df = prepare_final_dataset(merged, logger)

        # Step 11: Filter to manifest sample firms
        logger.write("\n" + "=" * 80)
        logger.write("Filtering to Manifest Sample")
        logger.write("=" * 80)
        manifest_gvkeys = manifest["gvkey"].drop_duplicates()
        n_before = len(final_df)
        final_df = final_df[final_df["gvkey"].isin(manifest_gvkeys)]
        logger.write(f"  Before filter: {n_before:,} observations")
        logger.write(f"  After filter: {len(final_df):,} observations")
        logger.write(f"  Filtered out: {n_before - len(final_df):,} non-sample firms")

        # Save output
        output_file = paths["output_dir"] / "H5_AnalystDispersion.parquet"
        logger.write(f"\nSaving output to: {output_file}")
        final_df.to_parquet(output_file, index=False)

        logger.write(f"  Saved {len(final_df):,} observations")
        logger.write(f"  File size: {output_file.stat().st_size / 1024 / 1024:.1f} MB")

        # Compute variable statistics for stats.json
        logger.write("\n" + "=" * 80)
        logger.write("Computing Variable Statistics")
        logger.write("=" * 80)

        var_stats = {}
        for col in final_df.columns:
            if col in ["gvkey"]:
                continue
            if pd.api.types.is_numeric_dtype(final_df[col]):
                non_null_count = int(final_df[col].notna().sum())
                if non_null_count > 0:
                    var_stats[col] = {
                        "count": non_null_count,
                        "mean": float(final_df[col].mean()),
                        "std": float(final_df[col].std()),
                        "min": float(final_df[col].min()),
                        "max": float(final_df[col].max()),
                        "p1": float(final_df[col].quantile(0.01)),
                        "p25": float(final_df[col].quantile(0.25)),
                        "p50": float(final_df[col].quantile(0.50)),
                        "p75": float(final_df[col].quantile(0.75)),
                        "p99": float(final_df[col].quantile(0.99)),
                    }
                else:
                    var_stats[col] = {"count": 0}

        stats["output_stats"]["variables"] = var_stats
        stats["output_stats"]["sample"] = {
            "n_total": int(len(final_df)),
            "n_firms": int(final_df["gvkey"].nunique())
            if "gvkey" in final_df.columns
            else 0,
            "n_quarters": int(final_df["fiscal_quarter"].nunique())
            if "fiscal_quarter" in final_df.columns
            else 0,
            "years": [int(y) for y in sorted(final_df["fiscal_year"].unique())]
            if "fiscal_year" in final_df.columns
            else [],
        }

        # Compute dispersion persistence
        if (
            "dispersion_lead" in final_df.columns
            and "prior_dispersion" in final_df.columns
        ):
            valid = final_df[["dispersion_lead", "prior_dispersion"]].dropna()
            if len(valid) > 1:
                persistence = valid["dispersion_lead"].corr(valid["prior_dispersion"])
                stats["output_stats"]["sample"]["dispersion_persistence"] = float(
                    persistence
                )

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
        logger.write("\n" + "=" * 80)
        logger.write("EXECUTION COMPLETE")
        logger.write("=" * 80)
        logger.write(f"Output file: {output_file}")
        logger.write(f"Final sample: {len(final_df):,} observations")
        logger.write(f"Unique firms: {final_df['gvkey'].nunique():,}")
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
