"""
Shared utilities for all pipeline scripts.
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
