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
Main Functions:
    - load_parquet(): Load Parquet file with error handling
    - safe_merge(): Merge with validation and logging (Phase 87-01)

Dependencies:
    - Utility module for data loading
    - Uses: pandas, pathlib

Author: Thesis Author
Date: 2026-02-11
================================================================================
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd

from f1d.shared.path_utils import OutputResolutionError, get_latest_output_dir

# Configure logger
logger = logging.getLogger(__name__)


# ==============================================================================
# Merge Validation (Phase 87-01)
# ==============================================================================


def safe_merge(
    left: pd.DataFrame,
    right: pd.DataFrame,
    on: Optional[Union[str, List[str]]] = None,
    left_on: Optional[Union[str, List[str]]] = None,
    right_on: Optional[Union[str, List[str]]] = None,
    how: str = "left",
    validate: Optional[str] = None,
    merge_name: str = "unnamed_merge",
    log_stats: bool = True,
) -> pd.DataFrame:
    """
    Merge DataFrames with validation and logging.

    This wrapper around pd.merge adds:
    - Pre-merge validation of key columns
    - Post-merge statistics logging
    - Optional cardinality validation

    Args:
        left: Left DataFrame
        right: Right DataFrame
        on: Column(s) to merge on (if same in both)
        left_on: Column(s) in left DataFrame
        right_on: Column(s) in right DataFrame
        how: Type of merge ('left', 'right', 'inner', 'outer')
        validate: Merge validation ('one_to_one', 'one_to_many', 'many_to_one', 'many_to_many')
        merge_name: Name for logging purposes
        log_stats: Whether to log merge statistics

    Returns:
        Merged DataFrame

    Raises:
        ValueError: If key columns are missing or merge validation fails

    Example:
        >>> merged = safe_merge(
        ...     manifest,
        ...     linguistic_vars,
        ...     on="file_name",
        ...     merge_name="manifest_linguistic",
        ...     validate="many_to_one"
        ... )
    """
    # Determine merge keys
    if on is not None:
        left_keys = right_keys = [on] if isinstance(on, str) else list(on)
    elif left_on is not None and right_on is not None:
        left_keys = [left_on] if isinstance(left_on, str) else list(left_on)
        right_keys = [right_on] if isinstance(right_on, str) else list(right_on)
    else:
        raise ValueError("Must specify 'on' or both 'left_on' and 'right_on'")

    # Pre-merge validation
    missing_left = [k for k in left_keys if k not in left.columns]
    if missing_left:
        raise ValueError(f"Merge key(s) missing from left DataFrame: {missing_left}")

    missing_right = [k for k in right_keys if k not in right.columns]
    if missing_right:
        raise ValueError(f"Merge key(s) missing from right DataFrame: {missing_right}")

    # Log pre-merge stats
    if log_stats:
        logger.debug(
            f"Merge '{merge_name}': left={len(left):,} rows, right={len(right):,} rows, "
            f"how={how}, keys={left_keys}"
        )

    # Perform merge
    if validate:
        merged = pd.merge(
            left,
            right,
            on=on,
            left_on=left_on,
            right_on=right_on,
            how=how,
            validate=validate,
        )
    else:
        merged = pd.merge(
            left,
            right,
            on=on,
            left_on=left_on,
            right_on=right_on,
            how=how,
        )

    # Post-merge statistics
    if log_stats:
        n_before = len(left)
        n_after = len(merged)

        # Calculate match rate for left joins
        if how == "left" and n_before > 0:
            # Check how many rows got data from right
            right_cols = [c for c in right.columns if c not in (on or [])]
            if right_on:
                right_cols = [c for c in right.columns if c not in right_on]

            if right_cols:
                matched = merged[right_cols[0]].notna().sum()
                match_rate = matched / n_before * 100
                logger.info(
                    f"Merge '{merge_name}': {n_after:,} rows, "
                    f"{matched:,} matched ({match_rate:.1f}%)"
                )
            else:
                logger.info(f"Merge '{merge_name}': {n_after:,} rows")
        else:
            logger.info(f"Merge '{merge_name}': {n_after:,} rows")

    return merged


def validate_merge_keys(
    df: pd.DataFrame, keys: Union[str, List[str]], df_name: str = "DataFrame"
) -> Tuple[bool, Optional[str]]:
    """
    Validate that merge keys exist and have no excessive nulls.

    Args:
        df: DataFrame to validate
        keys: Key column name(s)
        df_name: Name for error messages

    Returns:
        Tuple of (is_valid, error_message)
    """
    key_list = [keys] if isinstance(keys, str) else list(keys)
    missing = [k for k in key_list if k not in df.columns]
    if missing:
        return False, f"{df_name}: Missing key columns: {missing}"

    for key in key_list:
        null_pct = df[key].isna().sum() / len(df) * 100 if len(df) > 0 else 0
        if null_pct > 10:  # More than 10% nulls is concerning
            logger.warning(
                f"{df_name}: Key column '{key}' has {null_pct:.1f}% null values"
            )

    return True, None


def get_merge_diagnostics(
    left: pd.DataFrame,
    right: pd.DataFrame,
    on: Union[str, List[str]],
    how: str = "left",
) -> Dict[str, Any]:
    """
    Get diagnostic statistics for a potential merge.

    Args:
        left: Left DataFrame
        right: Right DataFrame
        on: Merge key(s)
        how: Type of merge

    Returns:
        Dict with diagnostic statistics
    """
    on_list = [on] if isinstance(on, str) else list(on)
    diagnostics: Dict[str, Any] = {
        "left_rows": len(left),
        "right_rows": len(right),
        "left_keys_unique": left[on_list].drop_duplicates().shape[0] if len(left) > 0 else 0,
        "right_keys_unique": right[on_list].drop_duplicates().shape[0] if len(right) > 0 else 0,
    }

    # Calculate overlap
    if len(left) > 0 and len(right) > 0:
        left_keys_set = set(left[on_list].apply(tuple, axis=1))
        right_keys_set = set(right[on_list].apply(tuple, axis=1))
        overlap = len(left_keys_set & right_keys_set)
        diagnostics["key_overlap"] = overlap
        diagnostics["left_only"] = len(left_keys_set) - overlap
        diagnostics["right_only"] = len(right_keys_set) - overlap

        if how == "left" and len(left_keys_set) > 0:
            diagnostics["expected_match_rate"] = overlap / len(left_keys_set) * 100

    return diagnostics


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
    manifest_dir = get_latest_output_dir(
        root / "4_Outputs" / "1.4_AssembleManifest",
        required_file="master_sample_manifest.parquet",
    )
    manifest_path = manifest_dir / "master_sample_manifest.parquet"
    manifest = pd.read_parquet(
        manifest_path,
        columns=[
            "file_name",
            "gvkey",
            "start_date",
            "ceo_id",
            "ceo_name",  # Required for CEO stats aggregation
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
        try:
            lv_dir = get_latest_output_dir(
                root / "4_Outputs" / "2_Textual_Analysis" / "2.2_Variables",
                required_file=f"linguistic_variables_{year}.parquet",
            )
            lv_path = lv_dir / f"linguistic_variables_{year}.parquet"
        except OutputResolutionError:
            print(f"  WARNING: Missing linguistic_variables_{year}.parquet")
            continue

        lv = pd.read_parquet(lv_path)

        # Drop columns that would conflict with manifest (keep manifest versions)
        lv_drop_cols = [c for c in ["gvkey", "year", "start_date"] if c in lv.columns]
        if lv_drop_cols:
            lv = lv.drop(columns=lv_drop_cols)

        # Firm controls
        try:
            fc_dir = get_latest_output_dir(
                root / "4_Outputs" / "3_Financial_Features",
                required_file=f"firm_controls_{year}.parquet",
            )
            fc_path = fc_dir / f"firm_controls_{year}.parquet"
            fc = pd.read_parquet(fc_path)
        except OutputResolutionError:
            fc = pd.DataFrame()

        # Market variables
        try:
            mv_dir = get_latest_output_dir(
                root / "4_Outputs" / "3_Financial_Features",
                required_file=f"market_variables_{year}.parquet",
            )
            mv_path = mv_dir / f"market_variables_{year}.parquet"
            mv = pd.read_parquet(mv_path)
        except OutputResolutionError:
            mv = pd.DataFrame()

        # Merge for this year
        # Manifest contains all files; filter to this year based on linguistic variables
        year_files = set(lv["file_name"])
        mf_year = manifest[manifest["file_name"].isin(year_files)].copy()

        # Merge linguistic variables with validation (Phase 87-01)
        merged = safe_merge(
            mf_year,  # type: ignore[arg-type]
            lv,
            on="file_name",
            how="left",
            merge_name=f"manifest_linguistic_{year}",
            log_stats=False,
        )

        # Merge firm controls with validation
        if len(fc) > 0:
            fc_cols = ["file_name"] + [
                c
                for c in fc.columns
                if c in ["StockRet", "MarketRet", "EPS_Growth", "SurpDec"]
            ]
            merged = safe_merge(
                merged,
                fc[fc_cols],  # type: ignore[arg-type]
                on="file_name",
                how="left",
                merge_name=f"firm_controls_{year}",
                log_stats=False,
            )

        # Merge market variables with validation
        if len(mv) > 0:
            mv_cols = ["file_name"] + [
                c
                for c in mv.columns
                if c in ["StockRet", "MarketRet", "EPS_Growth", "SurpDec"]
            ]
            merged = safe_merge(
                merged,
                mv[mv_cols],  # type: ignore[arg-type]
                on="file_name",
                how="left",
                merge_name=f"market_variables_{year}",
                log_stats=False,
            )

        merged["year"] = year
        all_data.append(merged)
        print(f"  {year}: {len(merged):,} calls")

    combined = pd.concat(all_data, ignore_index=True)
    print(f"\n  Total: {len(combined):,} calls")
    print(f"  Unique CEOs: {combined['ceo_id'].nunique():,}")
    print(f"  Unique firms: {combined['gvkey'].nunique():,}")

    return combined
