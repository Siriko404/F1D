#!/usr/bin/env python3
"""
Shared utilities for Step 3 scripts.
Provides common functions for variable reference generation and symlink handling.
"""

import pandas as pd
import shutil
import os
import sys
from pathlib import Path

# Import shared observability and symlink utilities
try:
    from shared.observability_utils import DualWriter
    from shared.symlink_utils import update_latest_link as update_latest_symlink
except ImportError:
    # Add parent directory to path and retry
    from pathlib import Path as _Path

    _script_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(_script_dir))
    from shared.observability_utils import DualWriter
    from shared.symlink_utils import update_latest_link as update_latest_symlink


def get_latest_output_dir(output_base, required_file=None):
    """
    Get the latest output directory. Uses 'latest' symlink if valid,
    otherwise finds the most recent timestamped folder.

    Args:
        output_base: Path to the output base directory
        required_file: Optional filename that must exist in the directory
    """
    latest = output_base / "latest"

    # Check if latest exists and has the required file
    if latest.exists():
        if required_file is None or (latest / required_file).exists():
            return latest

    # Fall back to finding latest timestamped folder with required file
    timestamped_dirs = [
        d
        for d in output_base.iterdir()
        if d.is_dir() and d.name != "latest" and d.name[0].isdigit()
    ]

    if timestamped_dirs:
        # Sort by name (timestamp format ensures chronological order)
        sorted_dirs = sorted(timestamped_dirs, key=lambda d: d.name, reverse=True)

        # If required_file specified, find first dir that has it
        if required_file:
            for d in sorted_dirs:
                if (d / required_file).exists():
                    return d
        else:
            return sorted_dirs[0]

    return latest  # Return latest path even if it doesn't exist


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
