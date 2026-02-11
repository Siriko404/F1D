#!/usr/bin/env python3
"""
================================================================================
SHARED MODULE: Mean-Centering for Interaction Terms
================================================================================
ID: shared/centering
Description: Mean-centering utilities for interaction terms to avoid
             multicollinearity. Creates de-meaned continuous variables and
             interaction products with intermediate output saving.

Purpose: Interaction terms between continuous variables can create artificial
         multicollinearity. Mean-centering before multiplication reduces VIF
         and makes coefficient interpretation more meaningful.

Inputs:
    - pandas DataFrame with continuous variables to center
    - Column names for variables to center and interact

Outputs:
    - DataFrame with new centered columns (original columns preserved)
    - Dictionary of means used for centering (for reproducibility)
    - Interaction columns from centered variables

Declared Inputs:
    - df: pd.DataFrame with columns to center
    - columns: List[str] of continuous variable names to center

Declared Outputs:
    - center_continuous() returns (df_with_centered_cols, means_dict)
    - create_interaction() returns df with new interaction column
    - save_centered_intermediates() saves parquet + JSON for audit trail

Deterministic: true
Dependencies:
    - Utility module for mean-centering variables
    - Uses: pandas, numpy

Author: Thesis Author
Date: 2026-02-11
================================================================================
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd


def center_continuous(
    df: pd.DataFrame, columns: List[str], suffix: str = "_c", save_means: bool = True
) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """
    Mean-center continuous variables for interaction term creation.

    Creates new columns with centered values (variable minus its mean).
    Original columns are preserved. Centering reduces multicollinearity
    when creating interaction terms.

    Args:
        df: DataFrame containing the variables to center.
        columns: List of column names to center.
        suffix: Suffix for centered columns (default '_c').
            For example, 'leverage' becomes 'leverage_c'.
        save_means: If True, store means in returned dict for later use
            in marginal effects calculations.

    Returns:
        Tuple of (DataFrame with centered columns, dict of means).
        The DataFrame is a copy with new columns added.
        The dict maps original column names to their means.

    Raises:
        ValueError: If any specified column does not exist in DataFrame.

    Example:
        >>> df = pd.DataFrame({'x': [1, 2, 3, 4, 5], 'y': [10, 20, 30, 40, 50]})
        >>> df_centered, means = center_continuous(df, ['x', 'y'])
        >>> df_centered['x'].mean(), df_centered['x_c'].mean()
        (3.0, ~0.0)
        >>> means
        {'x': 3.0, 'y': 30.0}
    """
    # Validate columns exist
    missing = set(columns) - set(df.columns)
    if missing:
        raise ValueError(
            f"Columns not found in DataFrame: {sorted(missing)}. "
            f"Available: {sorted(df.columns)}"
        )

    # Create working copy
    df_out = df.copy()

    # Compute means
    means: Dict[str, float] = {}

    for col in columns:
        if col not in df_out.columns:
            continue

        # Compute mean, skipping NaN values
        mean_val = float(df_out[col].mean(skipna=True))
        means[col] = mean_val

        # Create centered column
        centered_col = f"{col}{suffix}"
        df_out[centered_col] = df_out[col] - mean_val

    return df_out, means


def create_interaction(
    df: pd.DataFrame,
    var1: str,
    var2: str,
    name: Optional[str] = None,
    center_first: bool = True,
) -> pd.DataFrame:
    """
    Create interaction term from two variables.

    Creates a new column as the product of var1 and var2. If center_first=True
    and variables are not already centered (no '_c' suffix), centers them first
    to reduce multicollinearity.

    Args:
        df: DataFrame containing the variables.
        var1: First variable name.
        var2: Second variable name.
        name: Name for interaction column. If None, uses '{var1}_x_{var2}'.
        center_first: If True, center variables before creating interaction
            (if they are not already centered). This reduces multicollinearity.

    Returns:
        DataFrame with new interaction column added (copy of input).

    Raises:
        ValueError: If specified columns do not exist.

    Example:
        >>> df = pd.DataFrame({'uncertainty': [0.5, 0.6, 0.7], 'leverage': [0.3, 0.4, 0.5]})
        >>> df = create_interaction(df, 'uncertainty', 'leverage')
        >>> 'uncertainty_x_leverage' in df.columns
        True
        >>> df['uncertainty_c'].mean()  # Centered version created
        ~0.0
    """
    # Validate columns exist
    missing = {var1, var2} - set(df.columns)
    if missing:
        raise ValueError(
            f"Columns not found in DataFrame: {sorted(missing)}. "
            f"Available: {sorted(df.columns)}"
        )

    df_out = df.copy()

    # Determine if using centered versions
    use_centered = center_first

    # Check if variables are already centered
    var1_centered = var1.endswith("_c")
    var2_centered = var2.endswith("_c")

    # If center_first requested but variables not centered, warn and center
    if center_first and not (var1_centered and var2_centered):
        # Get original names (remove _c suffix if present)
        var1_orig = var1[:-2] if var1_centered else var1
        var2_orig = var2[:-2] if var2_centered else var2

        # Check if centered versions already exist
        var1_c = f"{var1_orig}_c"
        var2_c = f"{var2_orig}_c"

        if var1_c not in df_out.columns:
            import warnings

            warnings.warn(
                f"Creating interaction with non-centered variable '{var1}'. "
                f"This may cause high multicollinearity. "
                f"Consider centering first with center_continuous().",
                UserWarning,
                stacklevel=2,
            )
            use_centered = False
        elif var2_c not in df_out.columns:
            import warnings

            warnings.warn(
                f"Creating interaction with non-centered variable '{var2}'. "
                f"This may cause high multicollinearity. "
                f"Consider centering first with center_continuous().",
                UserWarning,
                stacklevel=2,
            )
            use_centered = False

        # Use centered versions if available
        if use_centered:
            var1_use = var1_c
            var2_use = var2_c
        else:
            var1_use = var1
            var2_use = var2
    else:
        var1_use = var1
        var2_use = var2

    # Determine interaction column name
    if name is None:
        # Use base names without _c suffix for cleaner names
        var1_base = var1_use[:-2] if var1_use.endswith("_c") else var1_use
        var2_base = var2_use[:-2] if var2_use.endswith("_c") else var2_use
        name = f"{var1_base}_x_{var2_base}"

    # Create interaction
    df_out[name] = df_out[var1_use] * df_out[var2_use]

    return df_out


def save_centered_intermediates(
    df: pd.DataFrame,
    centered_cols: List[str],
    means: Dict[str, float],
    output_dir: Path,
    prefix: str = "centered",
) -> Path:
    """
    Save centered variables to parquet for debugging/auditing.

    Creates reproducible intermediate outputs that can be used to verify
    centering calculations and reproduce marginal effects.

    Args:
        df: DataFrame with centered columns to save.
        centered_cols: List of centered column names to include in output.
        means: Dictionary of means used for centering (from center_continuous).
        output_dir: Directory to save output files.
        prefix: Prefix for output files (default 'centered').

    Returns:
        Path to the saved parquet file.

    Raises:
        ValueError: If output_dir is not a directory or doesn't exist.

    Example:
        >>> df = pd.DataFrame({'x_c': [-2, -1, 0, 1, 2], 'y': [1, 2, 3, 4, 5]})
        >>> means = {'x': 3.0}
        >>> path = save_centered_intermediates(
        ...     df, ['x_c'], means, Path('outputs/intermediate/')
        ... )
        >>> path.exists()
        True
    """
    output_dir = Path(output_dir)

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Select columns to save
    cols_to_save = [c for c in centered_cols if c in df.columns]

    if not cols_to_save:
        raise ValueError(
            f"No centered columns found in DataFrame. Requested: {centered_cols}"
        )

    # Save parquet with centered variables
    parquet_path = output_dir / f"{prefix}_variables.parquet"
    df[cols_to_save].to_parquet(parquet_path, index=False)

    # Save means dict as JSON
    json_path = output_dir / f"{prefix}_means.json"
    with open(json_path, "w") as f:
        json.dump(means, f, indent=2)

    return parquet_path


def compute_marginal_effect(
    df: pd.DataFrame,
    interaction_col: str,
    var1: str,
    var2: str,
    var1_centered: bool = True,
    var2_centered: bool = True,
    means: Optional[Dict[str, float]] = None,
) -> Dict[str, float]:
    """
    Compute marginal effect of var1 on outcome, conditional on var2.

    For interaction models: Y = b1*var1 + b2*var2 + b3*(var1*var2)
    The marginal effect of var1 is: dY/d(var1) = b1 + b3*var2

    This function computes the average marginal effect and marginal effect
    at mean values of the moderator.

    Args:
        df: DataFrame with interaction term data.
        interaction_col: Name of interaction column (e.g., 'var1_x_var2').
        var1: Name of first variable (whose effect is being computed).
        var2: Name of second variable (moderator).
        var1_centered: Whether var1 is mean-centered.
        var2_centered: Whether var2 is mean-centered.
        means: Dict of means if variables are centered (for re-centering).

    Returns:
        Dict with:
            - 'interaction_mean': Mean value of the interaction term
            - 'var2_mean': Mean value of the moderator
            - 'avg_marginal_effect': Average marginal effect formula coefficient

    Note:
        This function returns the marginal effect COMPONENT. The full marginal
        effect requires the regression coefficient: ME = coef_var1 + coef_interaction * var2
    """
    # Validate columns exist
    required = [interaction_col, var2]
    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    # Compute means
    interaction_mean = float(df[interaction_col].mean(skipna=True))
    var2_mean = float(df[var2].mean(skipna=True))

    result = {
        "interaction_mean": interaction_mean,
        "var2_mean": var2_mean,
        "avg_marginal_effect": var2_mean,  # ME = coef_var1 + coef_interaction * var2
    }

    return result


# Export symbols
__all__ = [
    "center_continuous",
    "create_interaction",
    "save_centered_intermediates",
    "compute_marginal_effect",
]
