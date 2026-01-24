# Location: 2_Scripts/shared/dual_writer.py
"""
================================================================================
SHARED MODULE: Dual Writer for Logging
================================================================================
ID: shared.dual_writer
Description: Re-exports DualWriter class from observability_utils module.
             Provides clean import path: from shared.dual_writer import DualWriter

Purpose: DualWriter writes to both stdout and log file verbatim.
         Extracted to eliminate duplication across 12+ scripts.

Inputs:
    - log_path: Path to log file

Outputs:
    - DualWriter class instance

Deterministic: true
================================================================================
"""

# Re-export from observability_utils to avoid code duplication
from shared.observability_utils import DualWriter

# Export symbols for direct import from this module
__all__ = ["DualWriter"]
