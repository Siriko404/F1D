"""Shared utilities for F1D pipeline.

This package provides cross-cutting utilities used across all
pipeline stages.

Key Modules:
    - panel_ols: Panel OLS regression with fixed effects
    - iv_regression: Instrumental variable regression (2SLS)
    - data_validation: DataFrame validation against schemas
    - path_utils: Path resolution and timestamped output utilities
    - variables: Variable builder framework
    - observability: Logging and monitoring utilities

Public API:
    - run_panel_ols: Execute panel regression with fixed effects
    - get_latest_output_dir: Resolve timestamped output directories
    - DualWriter: Console + file logging
    - compute_vif: Calculate variance inflation factors
    - check_multicollinearity: Detect multicollinearity issues
    - center_continuous: Mean-center variables for interaction terms
    - create_interaction: Create interaction terms from centered variables

Example:
    from f1d.shared import run_panel_ols, get_latest_output_dir, DualWriter
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
