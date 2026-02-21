#!/usr/bin/env python3
"""
================================================================================
SHARED MODULE: Dual Writer for Logging
================================================================================
ID: shared.dual_writer
Description: Re-exports DualWriter class from observability module.

Purpose: DualWriter writes to both stdout and log file verbatim.
         Provides clean import path for backward compatibility.

Inputs:
    - log_path: Path to log file

Outputs:
    - DualWriter class instance

Main Functions:
    - DualWriter: Class for dual stdout/file logging

Dependencies:
    - Utility module for dual output writes
    - Re-exports: shared.observability.logging.DualWriter

Author: Thesis Author
Date: 2026-02-11
================================================================================
"""

from typing import List

# Re-export from observability_utils to avoid code duplication
from f1d.shared.observability import DualWriter

# Export symbols for direct import from this module
__all__: List[str] = ["DualWriter"]
