#!/usr/bin/env python3
"""
================================================================================
SHARED MODULE: Regression Validation
================================================================================
ID: shared/regression_validation
Description: Provides regression input validation to catch data issues.

Purpose: Ensure regression models run correctly and produce valid results
         by validating inputs before estimation.

Inputs:
    - Regression DataFrames
    - Variable specifications

Outputs:
    - Validation results
    - Error messages for debugging

Main Functions:
    - validate_regression_inputs(): Validate inputs before regression

Dependencies:
    - Utility module for regression validation
    - Uses: pandas, numpy

Author: Thesis Author
Date: 2026-02-11
================================================================================
"""

from typing import Dict, List, Optional

import numpy as np
import pandas as pd


class RegressionValidationError(Exception):
    """Raised when regression input validation fails."""

    pass


def validate_columns(
    df: pd.DataFrame, required_columns: List[str], optional_columns: Optional[List[str]] = None
) -> None:
    """
    Validate that all required columns exist in DataFrame.

    Args:
        df: DataFrame to validate
        required_columns: List of columns that must exist
        optional_columns: List of columns that may exist (for validation only)

    Raises:
        RegressionValidationError: If required columns missing
    """
    missing = set(required_columns) - set(df.columns)
    if missing:
        raise RegressionValidationError(
            f"Missing required columns: {sorted(missing)}. "
            f"Available: {sorted(df.columns)}"
        )

    if optional_columns:
        optional_missing = set(optional_columns) - set(df.columns)
        if optional_missing:
            import warnings

            warnings.warn(
                f"Optional columns missing: {sorted(optional_missing)}. "
                f"Proceeding without them.",
                stacklevel=2,
            )


def validate_data_types(df: pd.DataFrame, type_requirements: Dict[str, str]) -> None:
    """
    Validate DataFrame columns have expected data types.

    Args:
        df: DataFrame to validate
        type_requirements: Dict mapping column name to expected type
                          (e.g., {'year': 'int', 'ceo_id': 'int', 'returns': 'float'})

    Raises:
        RegressionValidationError: If columns have unexpected types
    """
    type_map = {
        "int": [np.integer],
        "float": [np.floating],
        "str": [object],
        "bool": [bool],
    }

    for col, expected_type in type_requirements.items():
        if col not in df.columns:
            continue  # Skip missing columns (validate_columns handles this)

        col_type = df[col].dtype
        expected_types = type_map.get(expected_type, [])

        if not any(np.issubdtype(col_type, t) for t in expected_types):  # type: ignore[attr-defined]
            raise RegressionValidationError(
                f"Column '{col}' has unexpected type: {col_type}. "
                f"Expected: {expected_type}"
            )


def validate_no_missing_independent(
    df: pd.DataFrame, independent_vars: List[str], allow_na_ratio: float = 0.0
) -> None:
    """
    Validate independent variables have no missing values (or within threshold).

    Args:
        df: DataFrame to validate
        independent_vars: List of independent variable column names
        allow_na_ratio: Maximum ratio of missing values allowed (0.0 = none allowed)

    Raises:
        RegressionValidationError: If missing values exceed threshold
    """
    for var in independent_vars:
        if var not in df.columns:
            continue

        missing_count = df[var].isna().sum()
        total_count = len(df)
        missing_ratio = missing_count / total_count

        if missing_ratio > allow_na_ratio:
            raise RegressionValidationError(
                f"Independent variable '{var}' has too many missing values: "
                f"{missing_count}/{total_count} ({missing_ratio:.1%}). "
                f"Maximum allowed: {allow_na_ratio:.1%}"
            )


def validate_regression_data(
    df: pd.DataFrame,
    formula: str,
    required_columns: Optional[List[str]] = None,
    type_requirements: Optional[Dict[str, str]] = None,
    allow_na_independent: float = 0.0,
) -> pd.DataFrame:
    """
    Comprehensive validation of regression data before model estimation.

    Args:
        df: DataFrame to validate
        formula: Regression formula (for parsing variable names)
        required_columns: List of columns that must exist
        type_requirements: Dict mapping column names to expected types
        allow_na_independent: Max missing ratio for independent variables

    Returns:
        Validated DataFrame

    Raises:
        RegressionValidationError: If validation fails

    Note:
        Parses formula to extract dependent and independent variables.
    """
    # Parse formula to extract variable names
    import re

    match = re.match(r"(.+?)\s*~\s*(.+)", formula)
    if not match:
        raise RegressionValidationError(f"Invalid formula: {formula}")

    dependent_var = match.group(1).strip()
    independent_vars_str = match.group(2).strip()

    # Extract independent variables from formula
    # Handle simple cases: "x1 + x2 + x3"
    independent_vars = [
        var.strip()
        for var in re.split(r"\s*\+\s*", independent_vars_str)
        if not var.startswith("C(") and not var.strip() == "1"
    ]

    # Validate required columns
    if required_columns:
        validate_columns(df, required_columns)

    # Validate data types
    if type_requirements:
        validate_data_types(df, type_requirements)

    # Validate no missing in dependent variable
    if dependent_var in df.columns and df[dependent_var].isna().any():
        raise RegressionValidationError(
            f"Dependent variable '{dependent_var}' has missing values: "
            f"{df[dependent_var].isna().sum()} out of {len(df)}"
        )

    # Validate no missing in independent variables
    if allow_na_independent == 0.0:
        validate_no_missing_independent(df, independent_vars, allow_na_ratio=0.0)
    else:
        validate_no_missing_independent(
            df, independent_vars, allow_na_ratio=allow_na_independent
        )

    return df


def validate_sample_size(df: pd.DataFrame, min_observations: int = 30) -> None:
    """
    Validate DataFrame has minimum number of observations for regression.

    Args:
        df: DataFrame to validate
        min_observations: Minimum number of observations required

    Raises:
        RegressionValidationError: If sample size insufficient
    """
    n_obs = len(df)

    if n_obs < min_observations:
        raise RegressionValidationError(
            f"Insufficient observations for regression: {n_obs}. "
            f"Minimum required: {min_observations}"
        )


def check_multicollinearity(
    df: pd.DataFrame, independent_vars: List[str], vif_threshold: float = 10.0
) -> Dict[str, float]:
    """
    Check for multicollinearity using VIF (Variance Inflation Factor).

    Args:
        df: DataFrame with independent variables
        independent_vars: List of independent variable names
        vif_threshold: VIF threshold for warning

    Returns:
        Dict mapping variable names to VIF values

    Warning:
        Logs warning if any variable has VIF > vif_threshold
    """
    try:
        from statsmodels.stats.outliers_influence import variance_inflation_factor
        from statsmodels.tools.tools import add_constant
    except ImportError:
        import warnings

        warnings.warn("statsmodels not available. Skipping VIF check.", stacklevel=2)
        return {}

    # Prepare data (add constant, handle missing values)
    df_vif = df[independent_vars].copy().dropna()
    df_vif = add_constant(df_vif)

    # Calculate VIF for each variable
    vif_dict = {}
    for var in independent_vars:
        if var in df_vif.columns:
            try:
                vif = variance_inflation_factor(
                    df_vif.values, df_vif.columns.get_loc(var)
                )
                vif_dict[var] = vif

                if vif > vif_threshold:
                    import warnings

                    warnings.warn(
                        f"High multicollinearity detected for var: VIF is {vif:.2f}, threshold is {vif_threshold}",
                        stacklevel=2,
                    )
            except Exception as e:
                import warnings

                warnings.warn(f"Could not calculate VIF for var: {e}", stacklevel=2)

    return vif_dict
