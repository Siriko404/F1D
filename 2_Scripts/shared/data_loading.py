#!/usr/bin/env python3
"""
================================================================================
SHARED MODULE: Data Loading Utilities
================================================================================
ID: shared/data_loading
Description: Provides reusable data loading and merging functions for multi-source data.

Inputs:
    - root: Root directory path
    - year_start, year_end: Year range for data loading
    - stats: Optional statistics dictionary for tracking

Outputs:
    - Combined DataFrame with all data sources merged

Deterministic: true
================================================================================
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any


def load_all_data(
    root: Path, year_start: int, year_end: int, stats: Optional[Dict[str, Any]] = None
) -> pd.DataFrame:
    """Load and merge all input data sources for Step 4.1 scripts.

    Loads and merges:
    - Manifest (master_sample_manifest.parquet)
    - Linguistic variables (per year from 2.2_Variables)
    - Firm controls (per year from 3_Financial_Features)
    - Market variables (per year from 3_Financial_Features)

    Args:
        root: Root project directory
        year_start: Start year (inclusive)
        year_end: End year (inclusive)
        stats: Optional statistics dict for tracking file checksums

    Returns:
        Combined DataFrame with all data sources merged by file_name
    """
    print("\n" + "=" * 60)
    print("Loading and merging data")
    print("=" * 60)

    # Load manifest
    manifest_path = (
        root
        / "4_Outputs"
        / "1.0_BuildSampleManifest"
        / "latest"
        / "master_sample_manifest.parquet"
    )
    manifest = pd.read_parquet(
        manifest_path,
        columns=[
            "file_name",
            "gvkey",
            "start_date",
            "ceo_id",
            "ff12_code",
            "ff12_name",
        ],
    )
    print(f"  Manifest: {len(manifest):,} calls")
    if stats:
        stats["input"]["files"].append(str(manifest_path))
        # Note: compute_file_checksum imported from observability_utils

    # Load linguistic variables, firm controls, market variables per year
    all_data = []

    for year in range(year_start, year_end + 1):
        # Linguistic variables
        lv_path = (
            root
            / "4_Outputs"
            / "2_Textual_Analysis"
            / "2.2_Variables"
            / "latest"
            / f"linguistic_variables_{year}.parquet"
        )
        if not lv_path.exists():
            print(f"  WARNING: Missing linguistic_variables_{year}.parquet")
            continue

        lv = pd.read_parquet(lv_path)

        # Drop columns that would conflict with manifest (keep manifest versions)
        lv_drop_cols = [c for c in ["gvkey", "year", "start_date"] if c in lv.columns]
        if lv_drop_cols:
            lv = lv.drop(columns=lv_drop_cols)

        # Firm controls
        fc_path = (
            root
            / "4_Outputs"
            / "3_Financial_Features"
            / "latest"
            / f"firm_controls_{year}.parquet"
        )
        fc = pd.read_parquet(fc_path) if fc_path.exists() else pd.DataFrame()

        # Market variables
        mv_path = (
            root
            / "4_Outputs"
            / "3_Financial_Features"
            / "latest"
            / f"market_variables_{year}.parquet"
        )
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
                c
                for c in fc.columns
                if c in ["StockRet", "MarketRet", "EPS_Growth", "SurpDec"]
            ]
            merged = merged.merge(fc[fc_cols], on="file_name", how="left")

        # Merge market variables
        if len(mv) > 0:
            mv_cols = ["file_name"] + [
                c
                for c in mv.columns
                if c in ["StockRet", "MarketRet", "EPS_Growth", "SurpDec"]
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
