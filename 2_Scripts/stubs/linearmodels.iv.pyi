"""
Type stubs for linearmodels.iv module.

These stubs provide type information for IV2SLS and related classes.
Generated for Phase 63 type checking.
"""
from typing import Any, Dict, List, Optional
from pandas import DataFrame, Series


class IV2SLS:
    """Two-Stage Least Squares regression."""

    def __init__(
        self,
        dependent: Series,
        exog: DataFrame,
        endog: DataFrame,
        instruments: DataFrame,
    ) -> None: ...

    def fit(
        self,
        cov_type: str = "unadjusted",
        clusters: Optional[DataFrame] = None,
        kernel: str = "bartlett",
        debiased: bool = True,
        **kwargs: Any,
    ) -> "IV2SLSResults": ...


class IV2SLSResults:
    """Results from IV2SLS estimation."""

    params: Series
    std_errors: Series
    tstats: Series
    pvalues: Series
    rsquared: float
    nobs: int
    first_stage: "FirstStageResults"
    sargan: "SarganTest"
    f_statistic: Optional["FStatistic"]


class FirstStageResults:
    """First-stage regression results."""

    individual: Dict[str, "FirstStageIndividual"]
    diagnostics: DataFrame


class FirstStageIndividual:
    """Individual first-stage results for an endogenous variable."""

    f_stat: float
    f_pval: float
    partial_rsquared: float
    fitted_values: Optional[Series]


class SarganTest:
    """Sargan overidentification test."""

    stat: float
    pval: float


class FStatistic:
    """F-statistic from regression."""

    stat: float
    pval: float
