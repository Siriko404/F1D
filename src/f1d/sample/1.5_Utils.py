#!/usr/bin/env python3
"""
==============================================================================
STEP 1.5: Utilities for Step 1
==============================================================================
ID: 1.5_Utils
Description: Shared utilities for Step 1 scripts.

Purpose: Provides common functions for variable reference generation
         and other Step 1 operations.

Inputs:
    - Variable definition files
    - DataFrames requiring variable references

Outputs:
    - Variable reference files
    - Variable lookup dictionaries

Dependencies:
    - Utility module for Step 1
    - Uses: pandas, numpy

Deterministic: true

Author: Thesis Author
Date: 2026-02-11
==============================================================================
"""

from pathlib import Path
from typing import Any, Callable, Dict, Optional

import pandas as pd


def load_master_variable_definitions() -> Dict[str, Dict[str, str]]:
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


def generate_variable_reference(
    df: pd.DataFrame,
    output_path: Path,
    print_fn: Callable[[str], None] = print
) -> None:
    """
    Generate enhanced variable_reference.csv with source and description.
    Uses master_variable_definitions.csv for lookups.
    """
    # Load master definitions
    var_defs = load_master_variable_definitions()

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

        ref_data.append(
            {
                "column_name": col,
                "dtype": str(df[col].dtype),
                "null_count": int(df[col].isna().sum()),
                "null_pct": f"{df[col].isna().sum() / len(df) * 100:.2f}%",
                "unique_count": int(df[col].nunique()),
                "sample_values": str(df[col].dropna().head(3).tolist()[:3]),
                "source": source,
                "description": description,
            }
        )

    ref_df = pd.DataFrame(ref_data)
    ref_df.to_csv(output_path, index=False)
    print_fn(f"  Variable reference saved: {output_path}")
