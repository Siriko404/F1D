"""
Type stubs for linearmodels.panel module.

These stubs provide type information for PanelOLS and related classes.
Generated for Phase 63 type checking.
"""
from typing import Any, Dict, List, Optional, Sequence, Union
from pandas import DataFrame, Series
from pandas.core.generic import NDFrame


class PanelOLS:
    """Panel OLS regression with entity and time effects."""

    def __init__(
        self,
        dependent: NDFrame,
        exog: NDFrame,
        entity_effects: bool = False,
        time_effects: bool = False,
        other_effects: Optional[NDFrame] = None,
        drop_absorbed: bool = False,
        check_rank: bool = True,
    ) -> None: ...

    def fit(
        self,
        debiased: bool = True,
        cov_type: str = "unadjusted",
        cluster_entity: bool = False,
        cluster_time: bool = False,
        clusters: Optional[DataFrame] = None,
        kernel: str = "bartlett",
        **kwargs: Any,
    ) -> "PanelOLSResults": ...


class PanelOLSResults:
    """Results from PanelOLS estimation."""

    params: Series
    std_errors: Series
    tstats: Series
    pvalues: Series
    rsquared: float
    rsquared_within: float
    nobs: int
    f_statistic: Optional["FStatistic"]
    resids: Series
    condition_number: Optional[float]


class FStatistic:
    """F-statistic from regression."""

    stat: float
    pval: float
