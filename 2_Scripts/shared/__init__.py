"""
Shared utilities for all pipeline scripts.
"""

from .observability_utils import DualWriter
from .industry_utils import parse_ff_industries
from .metadata_utils import load_variable_descriptions
from .path_utils import get_latest_output_dir, OutputResolutionError

# Econometric infrastructure (Phase 32)
from .panel_ols import run_panel_ols
from .centering import center_continuous, create_interaction
from .diagnostics import compute_vif, check_multicollinearity

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
