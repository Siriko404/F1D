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
================================================================================
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Import existing shared modules
from shared.regression_utils import run_fixed_effects_ols
from shared.regression_validation import validate_regression_data, validate_sample_size


def load_reg_data(
    input_file: Path, required_columns: List[str], filters: Optional[List[Dict]] = None
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


def build_regression_sample(
    df: pd.DataFrame,
    filters: List[Dict],
    sample_size: Optional[int] = None,
    random_seed: Optional[int] = None,
) -> pd.DataFrame:
    """
    Build filtered regression sample from DataFrame.

    Args:
        df: Input DataFrame
        filters: List of filter dictionaries
        sample_size: Maximum sample size (None = use all)
        random_seed: Random seed for reproducibility

    Returns:
        Filtered sample DataFrame
    """
    sample = df.copy()

    # Apply filters
    for f in filters:
        col = f.get("column")
        values = f.get("values")
        min_val = f.get("min_val")
        max_val = f.get("max_val")

        if col and values is not None:
            sample = sample[sample[col].isin(values)]
        if col and min_val is not None and max_val is not None:
            sample = sample[(sample[col] >= min_val) & (sample[col] <= max_val)]

    # Apply sample size limit
    if sample_size and len(sample) > sample_size:
        if random_seed is not None:
            sample = sample.sample(n=sample_size, random_state=random_seed)
        else:
            sample = sample.head(sample_size)

    return sample


def specify_regression_models(model_configs: List[Dict[str, any]]) -> Dict[str, any]:
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
