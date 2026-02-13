"""F1D Data Processing Pipeline for CEO Uncertainty Research.

This package implements a 4-stage data processing pipeline:
1. Sample Construction - Build analyst-CEO manifest
2. Text Processing - Tokenize and analyze conference calls
3. Financial Features - Construct financial variables
4. Econometric Analysis - Run panel regressions

Example:
    >>> from f1d import get_latest_output_dir
    >>> output = get_latest_output_dir("data/processed/manifest")

Attributes:
    __version__: Package version (semantic versioning)
    __author__: Package author
"""

__version__ = "6.0.0"
__author__ = "Thesis Author"

# Public API re-exports from shared utilities
from f1d.shared.path_utils import OutputResolutionError, get_latest_output_dir
from f1d.shared.panel_ols import run_panel_ols

__all__ = [
    # Path utilities
    "get_latest_output_dir",
    "OutputResolutionError",
    # Econometric utilities
    "run_panel_ols",
]
