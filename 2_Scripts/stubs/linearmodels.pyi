"""
Type stubs for linearmodels package.
"""
from linearmodels.panel import PanelOLS, PanelOLSResults  # type: ignore
from linearmodels.iv import IV2SLS, IV2SLSResults  # type: ignore

__all__ = ["PanelOLS", "PanelOLSResults", "IV2SLS", "IV2SLSResults"]
