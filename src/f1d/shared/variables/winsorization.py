"""Centralized winsorization utilities for F1D project.

This module provides standardized winsorization functions used across all
panel builders to ensure consistent outlier treatment.

Usage:
    from f1d.shared.variables.winsorization import winsorize_by_year, winsorize_pooled

    # CRSP variables: per-year 1%/99%
    panel = winsorize_by_year(panel, ["StockRet", "MarketRet", "Volatility"])

    # Linguistic variables: pooled 1%/99%
    panel = winsorize_pooled(panel, ["Manager_QA_Uncertainty_pct", ...])
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import List


def winsorize_by_year(
    df: pd.DataFrame,
    columns: List[str],
    year_col: str = "year",
    lower: float = 0.01,
    upper: float = 0.99,
    min_obs: int = 10,
) -> pd.DataFrame:
    """Winsorize columns at lower/upper percentiles within each year group.

    This function:
    1. Converts inf values to NaN (preserves missingness)
    2. Groups by year and clips each group to its year-specific percentiles
    3. Skips years with fewer than min_obs valid observations
    4. Skips NaN year group (does not cause error)

    Args:
        df: DataFrame to winsorize
        columns: List of column names to winsorize
        year_col: Name of the year column for grouping
        lower: Lower percentile (default 0.01 = 1st percentile)
        upper: Upper percentile (default 0.99 = 99th percentile)
        min_obs: Minimum observations required per year (default 10)

    Returns:
        Copy of DataFrame with winsorized columns

    Note:
        Returns a copy; does not modify the original DataFrame.
    """
    df = df.copy()

    # Convert inf values to NaN for all target columns
    for col in columns:
        if col in df.columns:
            df[col] = df[col].replace([np.inf, -np.inf], np.nan)
            # Convert to float to avoid pandas FutureWarning when assigning clipped float values
            if df[col].dtype != np.float64:
                df[col] = df[col].astype(float)

    # Process each year group
    # First, handle non-NaN years using standard groupby
    for year, group in df.groupby(year_col, dropna=True):
        idx = group.index

        for col in columns:
            if col not in df.columns:
                continue

            vals = df.loc[idx, col]
            valid = vals.notna()

            if valid.sum() < min_obs:
                # Not enough observations - skip this year for this column
                continue

            p_lower = vals[valid].quantile(lower)
            p_upper = vals[valid].quantile(upper)
            # Explicitly cast to float to avoid pandas FutureWarning about dtype incompatibility
            df.loc[idx, col] = vals.clip(lower=p_lower, upper=p_upper).astype(float)

    return df


def winsorize_pooled(
    df: pd.DataFrame,
    columns: List[str],
    lower: float = 0.01,
    upper: float = 0.99,
    min_obs: int = 100,
) -> pd.DataFrame:
    """Winsorize columns at lower/upper percentiles across all observations.

    This function:
    1. Converts inf values to NaN (preserves missingness)
    2. Clips all values to global percentiles
    3. Skips columns with fewer than min_obs valid observations

    Args:
        df: DataFrame to winsorize
        columns: List of column names to winsorize
        lower: Lower percentile (default 0.01 = 1st percentile)
        upper: Upper percentile (default 0.99 = 99th percentile)
        min_obs: Minimum observations required (default 100)

    Returns:
        Copy of DataFrame with winsorized columns

    Note:
        Returns a copy; does not modify the original DataFrame.
    """
    df = df.copy()

    for col in columns:
        if col not in df.columns:
            continue

        # Convert inf values to NaN
        df[col] = df[col].replace([np.inf, -np.inf], np.nan)

        valid = df[col].notna()

        if valid.sum() < min_obs:
            # Not enough observations - skip this column
            continue

        p_lower = df.loc[valid, col].quantile(lower)
        p_upper = df.loc[valid, col].quantile(upper)
        # Explicitly cast to float to avoid pandas FutureWarning about dtype incompatibility
        df[col] = df[col].clip(lower=p_lower, upper=p_upper).astype(float)

    return df
