#!/usr/bin/env python3
"""
==============================================================================
Sample Utilities Module
==============================================================================
ID: sample_utils
Description: Shared utilities for sample and financial scripts.

Purpose: Provides common functions for variable reference generation
         and master variable definitions loading. Consolidated from
         legacy 1_Sample/1.5_Utils.py to enable standard Python imports.

Inputs:
    - Variable definition files
    - DataFrames requiring variable references

Outputs:
    - Variable reference files
    - Variable lookup dictionaries

Dependencies:
    - Uses: pandas

Deterministic: true

Author: Thesis Author
Date: 2026-02-14
==============================================================================
"""

from pathlib import Path
from typing import Any, Callable, Dict

import pandas as pd


def load_master_variable_definitions() -> Dict[str, Dict[str, str]]:
    """Load the master variable definitions CSV.

    Returns:
        Dict mapping variable names (lowercase) to their source and description.
        Empty dict if the master file does not exist.
    """
    # Path from src/f1d/shared/sample_utils.py to project root
    # src/f1d/shared/ -> ../../../ = project root (4 levels up)
    root = Path(__file__).parent.parent.parent.parent
    master_path = root / "inputs" / "master_variable_definitions.csv"

    if master_path.exists():
        df = pd.read_csv(master_path)
        # Build lookup dict: variable -> {source, description}
        return {
            row["variable"].lower(): {
                "source": row["source"],
                "description": row["description"],
            }
            for _, row in df.iterrows()
        }
    else:
        return {}


def generate_variable_reference(
    df: pd.DataFrame,
    output_path: Path,
    print_fn: Callable[[str], None] = print
) -> None:
    """
    Generate enhanced variable_reference.csv with source and description.
    Uses master_variable_definitions.csv for lookups.

    Args:
        df: DataFrame to analyze
        output_path: Path to save the variable reference CSV
        print_fn: Print function to use for logging (defaults to print)
    """
    # Load master definitions
    var_defs = load_master_variable_definitions()

    # Deduplicate columns if any
    if not df.columns.is_unique:
        df = df.loc[:, ~df.columns.duplicated()]

    ref_data = []

    for col in df.columns:
        col_lower = col.lower()

        # Look up in master definitions
        if col_lower in var_defs:
            source = var_defs[col_lower]["source"]
            description = var_defs[col_lower]["description"]
        else:
            source = "Unknown"
            description = f"Column: {col}"

        # Handle potential edge case where column access might still be weird
        series = df[col]
        dtype_str = str(series.dtype)

        ref_data.append(
            {
                "column_name": col,
                "dtype": dtype_str,
                "null_count": int(series.isna().sum()),
                "null_pct": f"{series.isna().sum() / len(df) * 100:.2f}%",
                "unique_count": int(series.nunique()),
                "sample_values": str(series.dropna().head(3).tolist()[:3]),
                "source": source,
                "description": description,
            }
        )

    ref_df = pd.DataFrame(ref_data)
    ref_df.to_csv(output_path, index=False)
    print_fn(f"  Variable reference saved: {output_path}")
