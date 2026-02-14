#!/usr/bin/env python3
"""
================================================================================
SHARED MODULE: Regression Helpers
================================================================================
ID: shared/regression_helpers
Description: Provides reusable helpers for data loading, sample construction,
             and regression specification patterns for econometric analysis.

Inputs:
    - pandas DataFrame with regression data
    - File paths (pathlib.Path) for data loading

Outputs:
    - Filtered DataFrames for regression analysis
    - Model configuration dictionaries

Deterministic: true
Main Functions:
    -  Various regression helper functions

Dependencies:
    - Utility module for regression helpers
    - Uses: pandas, numpy, statsmodels

Author: Thesis Author
Date: 2026-02-11
================================================================================
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, cast

import pandas as pd

# Import existing shared modules
from f1d.shared.regression_validation import validate_sample_size


def load_reg_data(
    input_file: Path, required_columns: List[str], filters: Optional[List[Dict[str, Any]]] = None
) -> pd.DataFrame:
    """
    Load and filter regression data from input file.

    Args:
        input_file: Path to input file (parquet or csv)
        required_columns: List of columns that must exist
        filters: List of filter dictionaries with 'column', 'min_val', 'max_val'

    Returns:
        Filtered DataFrame

    Raises:
        FileNotFoundError: If input file not found
        ValueError: If required columns missing or unsupported file type
    """
    # Validate file exists
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    # Determine file type and load
    if input_file.suffix == ".parquet":
        df = pd.read_parquet(input_file)
    elif input_file.suffix == ".csv":
        df = pd.read_csv(input_file)
    else:
        raise ValueError(f"Unsupported file type: {input_file.suffix}")

    # Validate required columns
    missing = set(required_columns) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    # Apply filters
    if filters:
        for f in filters:
            col = f.get("column")
            min_val = f.get("min_val")
            max_val = f.get("max_val")
            if col and min_val is not None and max_val is not None:
                df = df[(df[col] >= min_val) & (df[col] <= max_val)]

    return df


def _check_missing_values(
    df: pd.DataFrame, required_vars: Dict[str, List[str]]
) -> Dict[str, int]:
    """
    Check for missing values in required variables.

    Args:
        df: DataFrame to check
        required_vars: Dictionary mapping variable types to column names
                              (e.g., {'dependent': ['y'], 'independent': ['x1'], 'controls': ['c1']})

    Returns:
        Dictionary mapping variable names to missing counts
    """
    missing_counts = {}
    all_vars = []
    for _var_type, var_list in required_vars.items():
        all_vars.extend(var_list)

    for var in all_vars:
        if var in df.columns:
            missing_count = df[var].isna().sum()
            if missing_count > 0:
                missing_counts[var] = int(missing_count)

    return missing_counts


def _assign_industry_codes(
    df: pd.DataFrame, sic_col: str, classification: str = "FF12"
) -> pd.DataFrame:
    """
    Assign Fama-French industry classification codes based on SIC code.

    Args:
        df: DataFrame with SIC codes
        sic_col: Column name containing SIC codes
        classification: Industry classification (FF12, FF48, or None)

    Returns:
        DataFrame with added 'industry_code' column

    Note:
        Loads SIC code lookup tables from 1_Inputs/ directory.
        FF12: 12 industry classifications
        FF48: 48 industry classifications
    """
    from pathlib import Path

    df = df.copy()

    # Skip if classification not requested or SIC column missing
    if classification is None or sic_col not in df.columns:
        return df

    # Determine SIC lookup file based on classification
    input_dir = Path(__file__).parent.parent.parent / "1_Inputs"

    if classification == "FF12":
        sic_file = input_dir / "Siccodes12.zip"
    elif classification == "FF48":
        sic_file = input_dir / "Siccodes48.zip"
    else:
        raise ValueError(
            f"Unsupported classification: {classification}. Use FF12 or FF48."
        )

    # Load SIC code lookup table
    if not sic_file.exists():
        raise FileNotFoundError(f"SIC code file not found: {sic_file}")

    try:
        sic_lookup = pd.read_parquet(sic_file)
    except Exception:
        # Try CSV if parquet fails
        try:
            sic_lookup = pd.read_csv(sic_file)
        except Exception as e:
            raise ValueError(f"Could not load SIC lookup file: {e}")

    # Check required columns in SIC lookup
    sic_col_lower = sic_col.lower()
    sic_lookup_cols = [col.lower() for col in sic_lookup.columns]

    if sic_col_lower not in sic_lookup_cols:
        available = [col for col in sic_lookup.columns]
        raise ValueError(
            f"SIC column '{sic_col}' not found in SIC lookup file. "
            f"Available columns: {available}"
        )

    # Find the actual column name in lookup (case-insensitive)
    lookup_sic_col = sic_lookup.columns[sic_lookup_cols.index(sic_col_lower)]

    # Identify industry code column
    industry_col_candidates = [
        col
        for col in sic_lookup.columns
        if col.lower() in ["industry", "ff", "industry_code"]
    ]
    if not industry_col_candidates:
        raise ValueError("Industry code column not found in SIC lookup file")

    industry_col = industry_col_candidates[0]

    # Merge industry codes to DataFrame
    df = df.merge(
        sic_lookup[[lookup_sic_col, industry_col]],
        left_on=sic_col,
        right_on=lookup_sic_col,
        how="left",
    )

    # Rename industry column to standard name
    df = df.rename(columns={industry_col: "industry_code"})

    return df


def build_regression_sample(
    df: pd.DataFrame,
    required_vars: Dict[str, List[str]],
    filters: Optional[List[Dict[str, Any]]] = None,
    year_range: Optional[Tuple[int, int]] = None,
    min_sample_size: int = 100,
    max_sample_size: Optional[int] = None,
    random_seed: Optional[int] = None,
    industry_classification: str = "FF12",
    sic_col: str = "sic",
) -> pd.DataFrame:
    """
    Build filtered regression sample with comprehensive validation.

    Args:
        df: Input DataFrame
        required_vars: Dictionary mapping variable types to column names
                         (e.g., {'dependent': ['y'], 'independent': ['x1', 'x2'],
                          'controls': ['c1', 'c2']})
        filters: List of filter dicts with structure:
            - column: Column name to filter on
            - operation: Comparison operation (eq, gt, lt, ge, le, ne, in, not_in)
            - value: Value to compare against (single value or list)
        year_range: Tuple of (min_year, max_year) for year filtering
        min_sample_size: Minimum sample size (raises error if below)
        max_sample_size: Maximum sample size (samples down if above)
        random_seed: Random seed for reproducibility
        industry_classification: Industry classification (FF12, FF48, or None)
        sic_col: Column name for SIC code

    Returns:
        Filtered sample DataFrame

    Raises:
        ValueError: If required variables missing or sample size insufficient

    Example:
        >>> df = pd.DataFrame({'y': [1, 2, 3], 'x1': [4, 5, 6],
        ...                      'year': [2020, 2021, 2022], 'sic': [1234, 5678, 9123]})
        >>> required_vars = {'dependent': ['y'], 'independent': ['x1'], 'controls': []}
        >>> filters = [{'column': 'year', 'operation': 'ge', 'value': 2020}]
        >>> sample = build_regression_sample(df, required_vars, filters=filters,
        ...                              min_sample_size=3)
    """
    sample = df.copy()

    # Step 1: Validate required_vars structure and check columns exist
    if not isinstance(required_vars, dict):
        raise ValueError(
            "required_vars must be a dictionary with keys: dependent, independent, controls"
        )

    all_required_columns = []
    for var_type, var_list in required_vars.items():
        if not isinstance(var_list, list):
            raise ValueError(
                f"required_vars['{var_type}'] must be a list of column names"
            )
        all_required_columns.extend(var_list)

    # Check if all required columns exist in DataFrame
    missing_columns = set(all_required_columns) - set(sample.columns)
    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}. "
            f"Available: {sorted(sample.columns)}"
        )

    # Step 2: Apply filters
    if filters:
        for f in filters:
            col = f.get("column")
            operation = f.get("operation", "eq")
            value = f.get("value")

            if not col or col not in sample.columns:
                continue

            if operation == "eq":
                sample = sample[sample[col] == value]
            elif operation == "gt":
                sample = sample[sample[col] > value]
            elif operation == "lt":
                sample = sample[sample[col] < value]
            elif operation == "ge":
                sample = sample[sample[col] >= value]
            elif operation == "le":
                sample = sample[sample[col] <= value]
            elif operation == "ne":
                sample = sample[sample[col] != value]
            elif operation == "in":
                if isinstance(value, (list, tuple, set)):
                    sample = sample[sample[col].isin(value)]
                else:
                    raise ValueError(
                        f"'in' operation requires a list of values, got {type(value)}"
                    )
            elif operation == "not_in":
                if isinstance(value, (list, tuple, set)):
                    sample = sample[~sample[col].isin(value)]
                else:
                    raise ValueError(
                        f"'not_in' operation requires a list of values, got {type(value)}"
                    )
            else:
                raise ValueError(
                    f"Unsupported filter operation: {operation}. "
                    f"Use eq, gt, lt, ge, le, ne, in, not_in"
                )

    # Step 3: Apply year_range filter if specified
    if year_range is not None:
        min_year, max_year = year_range
        if "year" in sample.columns:
            sample = sample[(sample["year"] >= min_year) & (sample["year"] <= max_year)]
        else:
            import warnings

            warnings.warn(
                "year_range specified but 'year' column not found in DataFrame",
                stacklevel=2,
            )

    # Step 4: Check for missing values in required variables
    missing_counts = _check_missing_values(sample, required_vars)
    if missing_counts:
        import warnings

        missing_str = ", ".join(
            [f"{var}: {count}" for var, count in missing_counts.items()]
        )
        warnings.warn(
            f"Missing values in required variables: {missing_str}", stacklevel=2
        )

    # Step 5: Assign industry codes if industry_classification specified
    if industry_classification is not None:
        try:
            sample = _assign_industry_codes(sample, sic_col, industry_classification)
        except (FileNotFoundError, ValueError) as e:
            import warnings

            warnings.warn(f"Could not assign industry codes: {e}", stacklevel=2)

    # Step 6: Validate sample size

    validate_sample_size(sample, min_observations=min_sample_size)

    # Step 7: Apply max_sample_size cap with random sampling if specified
    if max_sample_size is not None and len(sample) > max_sample_size:
        if random_seed is not None:
            sample = sample.sample(n=max_sample_size, random_state=random_seed)
        else:
            sample = sample.head(max_sample_size)

    # Step 8: Return sample with metadata
    return cast(pd.DataFrame, sample)


def specify_regression_models(model_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Specify regression model configurations.

    Args:
        model_configs: List of configuration dictionaries, each with:
            - name: Model name (e.g., 'baseline', 'with_controls')
            - formula: R-style formula
            - dependent_var: Dependent variable name
            - independent_vars: List of independent variable names
            - fixed_effects: List of fixed effect column names

    Returns:
        Dictionary mapping model names to configurations
    """
    return {
        config["name"]: {
            "formula": config["formula"],
            "dependent_var": config["dependent_var"],
            "independent_vars": config["independent_vars"],
            "fixed_effects": config.get("fixed_effects", []),
            "sample_filters": config.get("sample_filters", []),
        }
        for config in model_configs
    }


def prepare_regression_data(
    df: pd.DataFrame,
    dependent_var: str,
    linguistic_controls: List[str],
    firm_controls: List[str],
    stats: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    """
    Filter to complete cases and assign industry samples.

    Args:
        df: DataFrame with regression data
        dependent_var: Name of dependent variable
        linguistic_controls: List of linguistic control variable names
        firm_controls: List of firm control variable names
        stats: Optional statistics dict to record filter counts

    Returns:
        Filtered DataFrame with 'sample' column assigned
    """
    print("\n" + "=" * 60)
    print("Preparing regression data")
    print("=" * 60)

    initial_n = len(df)

    # Filter to non-null ceo_id
    df = df.loc[df["ceo_id"].notna(), :].copy()
    print(f"  After ceo_id filter: {len(df):,} / {initial_n:,}")
    if stats:
        stats["processing"]["ceo_id_filter"] = initial_n - len(df)

    # Define required variables
    required = (
        [dependent_var] + linguistic_controls + firm_controls + ["ceo_id", "year"]
    )

    # Check which variables exist
    missing_vars = [v for v in required if v not in df.columns]
    if missing_vars:
        print(f"  WARNING: Missing variables: {missing_vars}")
        required = [v for v in required if v in df.columns]

    # Filter to complete cases (vectorized)
    complete_mask = df[required].notna().all(axis=1)
    df = df.loc[complete_mask, :].copy()
    print(f"  After complete cases filter: {len(df):,}")

    # Assign industry samples based on FF12
    df["sample"] = "Main"
    df.loc[df["ff12_code"] == 11, "sample"] = "Finance"
    df.loc[df["ff12_code"] == 8, "sample"] = "Utility"

    print("\n  Sample distribution:")
    for sample in ["Main", "Finance", "Utility"]:
        n = (df["sample"] == sample).sum()
        print(f"    {sample}: {n:,} calls")

    return df
