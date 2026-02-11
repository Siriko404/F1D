#!/usr/bin/env python3
"""
================================================================================
SHARED PACKAGE: Shared Utilities
================================================================================
ID: shared
Description: Shared utilities for all pipeline scripts.

Purpose: Provides common utilities and modules used across pipeline steps.

Exports:
    - centering: Variable centering functions
    - diagnostics: Regression diagnostics
    - industry_utils: Fama-French industry classifications
    - metadata_utils: Variable descriptions
    - observability_utils: Logging and statistics
    - panel_ols: Panel OLS regression
    - path_utils: Output path resolution

Dependencies:
    - Package initialization
    - Re-exports: centering, diagnostics, panel_ols, path_utils, etc.

Author: Thesis Author
Date: 2026-02-11
================================================================================
"""

from .centering import center_continuous, create_interaction
from .diagnostics import check_multicollinearity, compute_vif
from .industry_utils import parse_ff_industries
from .metadata_utils import load_variable_descriptions
from .observability_utils import DualWriter

# Econometric infrastructure (Phase 32)
from .panel_ols import run_panel_ols
from .path_utils import OutputResolutionError, get_latest_output_dir

__all__ = [
    "DualWriter",
    "parse_ff_industries",
    "load_variable_descriptions",
    "get_latest_output_dir",
    "OutputResolutionError",
    # Econometric utilities
    "run_panel_ols",
    "center_continuous",
    "create_interaction",
    "compute_vif",
    "check_multicollinearity",
]
