#!/usr/bin/env python3
"""
================================================================================
SHARED MODULE: Multicollinearity Diagnostics
================================================================================
ID: shared/diagnostics
Description: Multicollinearity diagnostics for panel regressions including
             VIF calculation, condition number, and threshold-based warnings.

Purpose: High multicollinearity inflates standard errors and makes coefficient
         interpretation difficult. This module provides tools to detect and
         report multicollinearity issues before and after regression.

Inputs:
    - pandas DataFrame with independent variables
    - List of column names for VIF calculation

Outputs:
    - VIF DataFrame with variable, VIF, threshold_exceeded columns
    - Condition number of design matrix
    - Formatted console output with threshold context

Declared Inputs:
    - df: pd.DataFrame with independent variables
    - columns: List[str] of continuous variable names (excludes dummies/FE)

Declared Outputs:
    - compute_vif() returns DataFrame with VIF values and threshold flags
    - check_multicollinearity() returns dict with VIF, condition number, violations
    - format_vif_table() returns formatted string for console output

Deterministic: true
Dependencies:
    - Utility module for regression diagnostics
    - Uses: pandas, numpy, statsmodels

Author: Thesis Author
Date: 2026-02-11
================================================================================
"""

import warnings
from typing import Any, Dict, List

import numpy as np
import pandas as pd


# Custom exceptions (also defined in panel_ols.py for consistency)
class CollinearityError(Exception):
    """Raised when perfect collinearity is detected in the design matrix."""

    pass


class MulticollinearityError(Exception):
    """Raised when VIF threshold is exceeded (high multicollinearity)."""

    pass


# Import statsmodels - handle gracefully if not available
try:
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    from statsmodels.tools.tools import add_constant

    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    variance_inflation_factor = None
    add_constant = None


def compute_vif(
    df: pd.DataFrame,
    columns: List[str],
    add_constant_col: bool = True,
    vif_threshold: float = 5.0,
) -> pd.DataFrame:
    """
    Compute Variance Inflation Factor (VIF) for continuous regressors.

    VIF measures how much the variance of an estimated regression coefficient
    increases due to multicollinearity. VIF > 5 indicates moderate multicollinearity;
    VIF > 10 indicates high multicollinearity.

    Note: VIF should only be computed on continuous regressors, not on dummy
    variables or fixed effects dummies. Including dummies will artificially inflate
    VIF values due to the dummy trap.

    Args:
        df: DataFrame with independent variables.
        columns: List of column names to compute VIF for.
            Exclude dummies and FE columns.
        add_constant_col: If True, add constant column before VIF calculation.
            The constant column itself is skipped in VIF calculation.
        vif_threshold: Threshold for flagging high VIF (default 5.0).

    Returns:
        DataFrame with columns:
            - 'variable': Variable name
            - 'VIF': VIF value
            - 'threshold_exceeded': Boolean (VIF > vif_threshold)

    Raises:
        ImportError: If statsmodels is not available
        ValueError: If columns are missing or insufficient data

    Example:
        >>> df = pd.DataFrame({
        ...     'x1': [1, 2, 3, 4, 5],
        ...     'x2': [2, 4, 6, 8, 10],  # Perfectly correlated with x1
        ...     'x3': [5, 3, 7, 2, 6]
        ... })
        >>> vif_df = compute_vif(df, ['x1', 'x2', 'x3'])
        >>> vif_df[vif_df['threshold_exceeded']]
        # x1 and x2 will have high VIF due to correlation
    """
    if not STATSMODELS_AVAILABLE:
        raise ImportError(
            "statsmodels is required for VIF calculation. "
            "Install: pip install statsmodels"
        )

    # Validate columns exist
    missing = set(columns) - set(df.columns)
    if missing:
        raise ValueError(
            f"Columns not found in DataFrame: {sorted(missing)}. "
            f"Available: {sorted(df.columns)}"
        )

    # Prepare data for VIF calculation
    df_vif = df[columns].copy()

    # Drop rows with any NaN
    df_vif = df_vif.dropna()

    if len(df_vif) == 0:
        raise ValueError("No valid observations after dropping NaN values")

    # Add constant if requested
    if add_constant_col:
        df_vif = add_constant(df_vif)

    # Calculate VIF for each variable
    vif_data = []

    for col in columns:
        if col not in df_vif.columns:
            warnings.warn(
                f"Column '{col}' not in VIF DataFrame. Skipping.", stacklevel=2
            )
            continue

        try:
            # Get position of column
            col_idx = df_vif.columns.get_loc(col)

            # Compute VIF
            vif_value = float(variance_inflation_factor(df_vif.values, col_idx))

            vif_data.append(
                {
                    "variable": col,
                    "VIF": vif_value,
                    "threshold_exceeded": vif_value > vif_threshold,
                }
            )
        except Exception as e:
            warnings.warn(f"Could not compute VIF for '{col}': {e}", stacklevel=2)
            # Still add entry with NaN VIF
            vif_data.append(
                {"variable": col, "VIF": np.nan, "threshold_exceeded": False}
            )

    return pd.DataFrame(vif_data)


def check_multicollinearity(
    df: pd.DataFrame,
    columns: List[str],
    vif_threshold: float = 5.0,
    condition_threshold: float = 30.0,
    fail_on_violation: bool = False,
) -> Dict[str, Any]:
    """
    Comprehensive multicollinearity check with VIF and condition number.

    Performs VIF analysis on continuous regressors and computes condition
    number of the design matrix. Returns detailed results and can optionally
    raise an exception if thresholds are violated.

    Args:
        df: DataFrame with independent variables.
        columns: List of column names to check (continuous variables only).
        vif_threshold: VIF threshold for flagging multicollinearity.
        condition_threshold: Condition number threshold for ill-conditioning.
            Values > 30 indicate potential numerical issues.
        fail_on_violation: If True, raise MulticollinearityError when any
            threshold is exceeded.

    Returns:
        Dictionary with:
            - 'vif_results': DataFrame from compute_vif()
            - 'condition_number': float (or None if computation fails)
            - 'vif_violations': list of columns with VIF > vif_threshold
            - 'condition_violation': bool (condition_number > threshold)
            - 'pass': bool (no violations detected)
            - 'warnings': list of warning messages

    Raises:
        MulticollinearityError: If fail_on_violation=True and violations detected

    Example:
        >>> df = pd.DataFrame({'x1': [1,2,3,4,5], 'x2': [2,4,6,8,10], 'x3': [5,3,7,2,6]})
        >>> result = check_multicollinearity(df, ['x1', 'x2', 'x3'])
        >>> result['pass']
        False  # Due to x1-x2 correlation
    """
    warnings_list = []

    # Compute VIF
    vif_df = compute_vif(df, columns, vif_threshold=vif_threshold)

    # Find VIF violations
    vif_violations = vif_df[vif_df["threshold_exceeded"]]["variable"].tolist()

    if vif_violations:
        msg = (
            f"High VIF detected for variables: {vif_violations}. "
            f"Threshold: {vif_threshold}. "
            f"This may cause unstable coefficient estimates."
        )
        warnings_list.append(msg)
        warnings.warn(msg, UserWarning, stacklevel=2)

    # Compute condition number
    condition_number = None
    condition_violation = False

    try:
        df_clean = df[columns].dropna()
        if len(df_clean) > 0:
            # Use SVD to compute condition number
            # condition_number = max(singular_values) / min(singular_values)
            X = df_clean.values

            # Add constant for condition number (standard practice)
            X_with_const = np.column_stack([np.ones(len(X)), X])

            # Compute singular values
            singular_values = np.linalg.svd(X_with_const, compute_uv=False)

            if len(singular_values) > 0 and singular_values[-1] > 0:
                condition_number = float(singular_values[0] / singular_values[-1])

                if condition_number > condition_threshold:
                    condition_violation = True
                    msg = (
                        f"High condition number: {condition_number:.2f}. "
                        f"Threshold: {condition_threshold}. "
                        f"This indicates potential numerical instability."
                    )
                    warnings_list.append(msg)
                    warnings.warn(msg, UserWarning, stacklevel=2)

    except Exception as e:
        warnings_list.append(f"Could not compute condition number: {e}")

    # Determine overall pass/fail
    pass_check = len(vif_violations) == 0 and not condition_violation

    # Fail hard if requested
    if fail_on_violation and not pass_check:
        raise MulticollinearityError(
            f"Multicollinearity detected. VIF violations: {vif_violations}. "
            f"Condition violation: {condition_violation}. "
            f"Consider removing or combining correlated variables."
        )

    return {
        "vif_results": vif_df,
        "condition_number": condition_number,
        "vif_violations": vif_violations,
        "condition_violation": condition_violation,
        "pass": pass_check,
        "warnings": warnings_list,
    }


def format_vif_table(vif_df: pd.DataFrame, threshold: float = 5.0) -> str:
    """
    Format VIF results as a console table with threshold context.

    Produces human-readable output showing VIF values and whether they
    exceed acceptable thresholds. Uses asterisks for highlighting on
    Windows compatibility (no ANSI codes).

    Args:
        vif_df: DataFrame from compute_vif() with columns:
            'variable', 'VIF', 'threshold_exceeded'
        threshold: VIF threshold for highlighting violations

    Returns:
        Formatted string table for console output

    Example:
        >>> vif_df = pd.DataFrame({
        ...     'variable': ['x1', 'x2', 'x3'],
        ...     'VIF': [4.2, 12.5, 2.1],
        ...     'threshold_exceeded': [False, True, False]
        ... })
        >>> print(format_vif_table(vif_df))
        # Outputs formatted table with WARNING on x2
    """
    lines = []
    lines.append("")
    lines.append("=" * 60)
    lines.append("VIF DIAGNOSTICS")
    lines.append("=" * 60)

    # Check for any violations first
    has_violations = (
        vif_df["threshold_exceeded"].any()
        if "threshold_exceeded" in vif_df.columns
        else False
    )

    if has_violations:
        lines.append("")
        lines.append("WARNING: High multicollinearity detected!")
        lines.append("")

    # Header
    header = f"{'Variable':<25} {'VIF':>10} {'Status':>25}"
    lines.append(header)
    lines.append("-" * 60)

    # Rows
    for _, row in vif_df.iterrows():
        var = row.get("variable", "")
        vif_val = row.get("VIF", np.nan)
        exceeded = row.get("threshold_exceeded", False)

        if np.isnan(vif_val):
            vif_str = "N/A"
            status_str = "Could not compute"
        elif exceeded:
            vif_str = f"{vif_val:.2f}"
            status_str = f"*** EXCEEDS {threshold} threshold"
        else:
            vif_str = f"{vif_val:.2f}"
            status_str = f"OK (< {threshold} threshold)"

        lines.append(f"{var:<25} {vif_str:>10} {status_str:>25}")

    lines.append("-" * 60)
    lines.append("")
    lines.append("VIF Interpretation:")
    lines.append("  VIF < 5:     Low multicollinearity (acceptable)")
    lines.append("  5 <= VIF < 10: Moderate multicollinearity (caution)")
    lines.append("  VIF >= 10:    High multicollinearity (concern)")
    lines.append("")
    lines.append("High VIF variables should be considered for removal or")
    lines.append("combination with other correlated variables.")
    lines.append("=" * 60)
    lines.append("")

    return "\n".join(lines)


def compute_condition_number(
    df: pd.DataFrame, columns: List[str], add_constant: bool = True
) -> float:
    """
    Compute condition number of the design matrix.

    The condition number measures the sensitivity of the solution to
    numerical errors in the data. High values (> 30) indicate potential
    ill-conditioning.

    Args:
        df: DataFrame with independent variables.
        columns: List of column names to include.
        add_constant: If True, add constant column before computation.

    Returns:
        Condition number as float. Returns np.nan if computation fails.

    Example:
        >>> df = pd.DataFrame({'x1': [1,2,3], 'x2': [4,5,6]})
        >>> cn = compute_condition_number(df, ['x1', 'x2'])
    """
    try:
        df_clean = df[columns].dropna()
        if len(df_clean) == 0:
            return np.nan

        X = df_clean.values

        if add_constant:
            X = np.column_stack([np.ones(len(X)), X])

        singular_values = np.linalg.svd(X, compute_uv=False)

        if len(singular_values) > 0 and singular_values[-1] > 0:
            return float(singular_values[0] / singular_values[-1])
        else:
            return np.nan

    except Exception:
        return np.nan


# Export symbols
__all__ = [
    "compute_vif",
    "check_multicollinearity",
    "format_vif_table",
    "compute_condition_number",
    "CollinearityError",
    "MulticollinearityError",
]
