#!/usr/bin/env python3
"""
================================================================================
SHARED MODULE: Regression Utilities
================================================================================
ID: shared/regression_utils
Description: Provides common fixed effects OLS regression patterns for
             econometric analysis. Handles statsmodels import errors gracefully
             and extracts CEO fixed effects and model diagnostics.

Inputs:
    - pandas DataFrame with regression data
    - statsmodels.formula.api (optional, raises ImportError if missing)

Outputs:
    - Fitted statsmodels OLS models
    - CEO fixed effects as pandas Series
    - Regression diagnostics as dictionary

Deterministic: true
Main Functions:
    - run_fixed_effects_ols(): Run OLS regression with fixed effects
    - extract_ceo_fixed_effects(): Extract CEO fixed effects from regression

Dependencies:
    - Utility module for regression utilities
    - Uses: pandas, numpy, statsmodels

Author: Thesis Author
Date: 2026-02-11
================================================================================
"""

from typing import Any, Dict, Optional, cast

import pandas as pd

try:
    import statsmodels.formula.api as smf

    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False


def run_fixed_effects_ols(
    df: pd.DataFrame,
    formula: str,
    sample_name: str,
    cov_type: str = "HC1",
    cluster_col: Optional[str] = None,
) -> Any:
    """
    Run fixed effects OLS regression with statsmodels.

    Args:
        df: DataFrame with regression data
        formula: R-style formula (e.g., "y ~ x1 + x2")
        sample_name: Name of sample for logging
        cov_type: Covariance type (HC1, cluster, etc.)
        cluster_col: Column to cluster standard errors (if cov_type='cluster')

    Returns:
        Fitted statsmodels OLS model

    Raises:
        ImportError: If statsmodels not available
        ValueError: If formula or data invalid
    """
    if not STATSMODELS_AVAILABLE:
        raise ImportError("statsmodels required. Install: pip install statsmodels")

    if cov_type == "cluster" and cluster_col is not None:
        model = smf.ols(formula, data=df).fit(
            cov_type="cluster", cov_kwds={"groups": df[cluster_col]}
        )
    else:
        model = smf.ols(formula, data=df).fit(cov_type=cov_type)

    return model


def extract_ceo_fixed_effects(model: Any, ceo_col: str = "ceo_id") -> pd.Series:
    """
    Extract CEO fixed effects from fitted model.

    Args:
        model: Fitted statsmodels model
        ceo_col: Name of CEO column used in formula C(ceo_col)

    Returns:
        Series of CEO fixed effects indexed by CEO ID
    """
    fe_params = model.params.filter(like=f"C({ceo_col})")
    # Extract CEO IDs from parameter names (format: C(ceo_id)[T.12345])
    fe_params.index = fe_params.index.str.extract(r"\[T\.(.*)\]")[0]
    return cast(pd.Series[Any], fe_params)


def extract_regression_diagnostics(model: Any) -> Dict[str, Any]:
    """
    Extract common regression diagnostics from fitted model.

    Args:
        model: Fitted statsmodels model

    Returns:
        Dictionary with: n_obs, rsquared, rsquared_adj, f_statistic,
        aic, bic, condno
    """
    return {
        "n_obs": int(model.nobs),
        "rsquared": float(model.rsquared),
        "rsquared_adj": float(model.rsquared_adj),
        "f_statistic": float(model.fvalue) if hasattr(model, "fvalue") else None,
        "aic": float(model.aic),
        "bic": float(model.bic),
        "condno": float(model.condition_number),
    }
