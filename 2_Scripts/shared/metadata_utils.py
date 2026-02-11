#!/usr/bin/env python3
"""
================================================================================
SHARED MODULE: Metadata Utilities
================================================================================
ID: shared/metadata_utils
Description: Variable description loading utilities.

Purpose: Load and manage variable descriptions from reference files.

Inputs:
    - Variable reference files (tab-separated with headers)

Outputs:
    - load_variable_descriptions() function

Dependencies:
    - Utility module for metadata handling
    - Uses: json, pathlib

Deterministic: true

Author: Thesis Author
Date: 2026-02-11
================================================================================
"""

from pathlib import Path
from typing import Dict


def load_variable_descriptions(ref_files: Dict[str, Path]) -> Dict[str, Dict[str, str]]:
    """
    Load variable descriptions from reference files.

    Reads tab-separated variable reference files and extracts variable names
    and descriptions. Skips header row and gracefully handles file read errors.

    Args:
        ref_files: Dictionary mapping source names to file paths.
                   Example: {"ccm": Path("ccm_varref.txt")}
                   Files are tab-separated with columns: [var_name, ..., var_desc]

    Returns:
        Dictionary mapping lowercase variable names to metadata dictionaries.
        Each metadata dictionary contains:
            - "source": The source key from ref_files
            - "description": The variable description string

        Example output:
        {
            "gvkey": {"source": "ccm", "description": "Global Company Key"},
            "lpermno": {"source": "ccm", "description": "Link permanent number"}
        }

    Raises:
        Does not raise exceptions. Files that fail to load are silently skipped.
    """
    descriptions = {}

    for source, path in ref_files.items():
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                for line in lines[1:]:  # Skip header
                    parts = line.strip().split("\t")
                    if len(parts) >= 3:
                        var_name = parts[0].lower()
                        var_desc = parts[2]
                        descriptions[var_name] = {
                            "source": source,
                            "description": var_desc,
                        }
            except Exception:
                # Gracefully skip files that fail to load
                pass

    return descriptions
