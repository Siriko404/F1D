#!/usr/bin/env python3
"""
==============================================================================
STEP 3.4: Utilities for Step 3
==============================================================================
ID: 3.4_Utils
Description: Shared utilities for Step 3 scripts.

Purpose: Provides common functions for variable reference generation
         and other Step 3 operations.

Inputs:
    - Variable definition files
    - DataFrames requiring variable references

Outputs:
    - Variable reference files
    - Variable lookup dictionaries

Dependencies:
    - Utility module for Step 3
    - Uses: pandas, numpy

Deterministic: true

Author: Thesis Author
Date: 2026-02-11
==============================================================================
"""

from pathlib import Path

import pandas as pd


def load_master_variable_definitions():
    """Load the master variable definitions CSV"""
    root = Path(__file__).parent.parent.parent
    master_path = root / "1_Inputs" / "master_variable_definitions.csv"

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


def generate_variable_reference(df, output_path, print_fn=print):
    """
    Generate enhanced variable_reference.csv with source and description.
    Uses master_variable_definitions.csv for lookups.
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
