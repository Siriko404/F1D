"""Shared utilities for F1D pipeline.

Tier 1: Core shared utilities - cross-cutting concerns.

This package contains cross-cutting utilities used across
all stages of the data processing pipeline.

Modules:
    path_utils: Path resolution and output directory utilities
    panel_ols: Panel OLS regression utilities
    financial_utils: Financial data loading utilities
    data_validation: Data validation utilities
    observability: Logging and monitoring
"""

from f1d.shared.centering import center_continuous, create_interaction
from f1d.shared.diagnostics import check_multicollinearity, compute_vif
from f1d.shared.industry_utils import parse_ff_industries
from f1d.shared.metadata_utils import load_variable_descriptions
from f1d.shared.observability import DualWriter
from f1d.shared.panel_ols import run_panel_ols
from f1d.shared.path_utils import OutputResolutionError, get_latest_output_dir

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
