#!/usr/bin/env python3
"""Tier 1: Core shared utilities - Panel OLS with Fixed Effects

================================================================================
SHARED MODULE: Panel OLS with Fixed Effects
================================================================================
ID: shared/panel_ols
Description: Panel OLS regression with firm + year + industry fixed effects using
             linearmodels.PanelOLS. Supports clustered standard errors, HAC
             adjustment, and comprehensive diagnostics.

Purpose: Phases 33-35 (H1/H2/H3 Regressions) need standardized panel regression
         infrastructure with proper fixed effects, interaction terms, and
         multicollinearity diagnostics.

Inputs:
    - pandas DataFrame with panel data (gvkey, year, ff48_code, dependent, exog)
    - linearmodels.PanelOLS for fixed effects estimation
    - statsmodels for VIF calculation

Outputs:
    - Fitted PanelOLS model with coefficients and standard errors
    - Summary statistics (R2, N, F-stat, fixed effects used)
    - VIF diagnostics with threshold warnings
    - Formatted console output with significance stars

Declared Inputs:
    - df: pd.DataFrame with columns [entity_col, time_col, industry_col, dependent, *exog]
    - dependent: str, name of dependent variable
    - exog: List[str], names of independent/exogenous variables

Declared Outputs:
    - run_panel_ols() function returning Dict[str, Any] with keys:
        - model: fitted PanelOLS object
        - coefficients: DataFrame with beta, SE, t-stat, p-value
        - summary: dict with R2, adj_R2, N, F-stat, fixed_effects_used
        - diagnostics: dict with VIF values, condition_number, residual_std
        - warnings: list of warning messages

Deterministic: true
Main Functions:
    - run_panel_ols(): Execute panel regression with fixed effects
    - compute_vif(): Calculate variance inflation factors
    - check_collinearity(): Detect perfect multicollinearity

Dependencies:
    - Utility module for panel OLS regression
    - Uses: linearmodels, pandas, numpy, statsmodels

Author: Thesis Author
Date: 2026-02-11
================================================================================
"""

import warnings
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


# Custom exceptions
class CollinearityError(Exception):
    """Raised when perfect collinearity is detected in the design matrix."""

    pass


class MulticollinearityError(Exception):
    """Raised when VIF threshold is exceeded (high multicollinearity)."""

    pass


# Import linearmodels - handle gracefully if not available
try:
    from linearmodels.panel.model import PanelOLS  # type: ignore[import-untyped]

    LINEARMODELS_AVAILABLE = True
except ImportError:
    PanelOLS = None  # type: ignore
    LINEARMODELS_AVAILABLE = False


def _check_thin_cells(
    df: pd.DataFrame, industry_col: str, time_col: str, min_firms: int = 5
) -> Tuple[bool, Dict[str, int]]:
    """
    Check for thin industry-year cells.

    Args:
        df: DataFrame with panel data
        industry_col: Column name for industry classification
        time_col: Column name for time period
        min_firms: Minimum firms per cell to be considered "thick"

    Returns:
        Tuple of (has_thin_cells, cell_counts dict)
    """
    if industry_col not in df.columns or time_col not in df.columns:
        return False, {}

    cell_counts = df.groupby([industry_col, time_col]).size().to_dict()

    thin_cells = {k: v for k, v in cell_counts.items() if v < min_firms}
    has_thin = len(thin_cells) > 0

    return has_thin, cell_counts


def _format_coefficient_table(
    coefficients: pd.DataFrame,
    pvalues: pd.Series,
    vif_df: Optional[pd.DataFrame] = None,
    vif_threshold: float = 5.0,
) -> str:
    """
    Format coefficient table for console output with significance stars.

    Args:
        coefficients: DataFrame with columns ['Parameter', 'Coefficient']
        pvalues: Series of p-values indexed by variable name
        vif_df: Optional DataFrame with VIF values
        vif_threshold: VIF threshold for highlighting violations

    Returns:
        Formatted string table for console output
    """
    lines = []
    lines.append("=" * 80)
    lines.append("REGRESSION RESULTS")
    lines.append("=" * 80)
    lines.append("")

    # Coefficient section
    lines.append("Coefficients:")
    lines.append("-" * 80)

    # Header
    header = f"{'Variable':<20} {'Coefficient':>12} {'Std.Error':>12} {'t-stat':>10} {'p-value':>10}"
    lines.append(header)
    lines.append("-" * 80)

    for var in coefficients.index:
        coef = coefficients.loc[var, "Coefficient"]
        se = coefficients.loc[var, "Std. Error"]
        tstat = coefficients.loc[var, "t-stat"]

        # Get p-value
        pval = pvalues.get(var, np.nan)

        # Significance stars
        if not np.isnan(pval):
            if pval < 0.01:
                stars = "***"
            elif pval < 0.05:
                stars = "**"
            elif pval < 0.10:
                stars = "*"
            else:
                stars = ""
        else:
            stars = ""

        # Format coefficient with stars
        coef_str = f"{coef:>10.4f}{stars:>3}"

        # Format p-value
        if np.isnan(pval):
            pval_str = "N/A"
        else:
            pval_str = f"{pval:.4f}"

        lines.append(
            f"{var:<20} {coef_str:>15} {se:>12.4f} {tstat:>10.2f} {pval_str:>10}"
        )

    lines.append("-" * 80)
    lines.append("Significance: * p<0.10, ** p<0.05, *** p<0.01")
    lines.append("")

    # VIF section
    if vif_df is not None and not vif_df.empty:
        lines.append("Variance Inflation Factors:")
        lines.append("-" * 80)

        for _, row in vif_df.iterrows():
            var = row["variable"]
            vif = row["VIF"]
            exceeded = row.get("threshold_exceeded", False)

            if exceeded:
                status = f"*** WARNING: Exceeds {vif_threshold} threshold"
            else:
                status = f"acceptable (< {vif_threshold} threshold)"

            lines.append(f"  {var:<20} VIF {vif:>6.2f} -- {status}")

        lines.append("")

    return "\n".join(lines)


def run_panel_ols(
    df: pd.DataFrame,
    dependent: str,
    exog: List[str],
    entity_col: str = "gvkey",
    time_col: str = "year",
    industry_col: str = "ff48_code",
    entity_effects: bool = True,
    time_effects: bool = True,
    industry_effects: bool = False,
    cov_type: str = "clustered",
    cluster_cols: Optional[List[str]] = None,
    kernel: str = "bartlett",
    min_industry_firms: int = 5,
    check_collinearity: bool = True,
    vif_threshold: float = 5.0,
) -> Dict[str, Any]:
    """
    Run panel OLS regression with fixed effects and clustered standard errors.

    This function provides a standardized interface for panel regression using
    linearmodels.PanelOLS. It handles firm, year, and industry fixed effects,
    various covariance estimators (clustered, kernel/HAC, robust), and
    comprehensive diagnostics including VIF multicollinearity checks.

    Args:
        df: DataFrame with panel data. Must contain entity_col, time_col, and
            all variables in dependent + exog.
        dependent: Name of the dependent variable column.
        exog: List of independent/exogenous variable column names.
        entity_col: Column name for entity identifier (default 'gvkey').
        time_col: Column name for time period (default 'year').
        industry_col: Column name for industry classification (default 'ff48_code').
        entity_effects: Include entity (firm) fixed effects (default True).
        time_effects: Include time (year) fixed effects (default True).
        industry_effects: Include industry fixed effects via other_effects.
            Default False because firm FE subsumes industry FE for most firms.
            Use with caution to avoid collinearity.
        cov_type: Covariance estimator type. Options:
            - 'clustered': Clustered standard errors (default)
            - 'kernel': HAC/Newey-West adjustment
            - 'robust': Heteroskedasticity-robust (HC1)
        cluster_cols: List of columns for double-clustering. If None and
            cov_type='clustered', clusters at entity level.
        kernel: Kernel type for HAC adjustment when cov_type='kernel'.
            Default 'bartlett' (Newey-West).
        min_industry_firms: Minimum firms per industry-year cell. If cells are
            thinner than this, logs warning about potential noise.
        check_collinearity: Check for multicollinearity using VIF (default True).
        vif_threshold: VIF threshold for flagging high multicollinearity.

    Returns:
        Dictionary with:
            - 'model': Fitted PanelOLS model object
            - 'coefficients': DataFrame with beta, SE, t-stat, p-value per variable
            - 'summary': Dict with R2, adj_R2, N, F-stat, fixed_effects_used
            - 'diagnostics': Dict with VIF values, condition_number, residual_std
            - 'warnings': List of warning messages generated during estimation

    Raises:
        ImportError: If linearmodels is not available
        ValueError: If required columns are missing or data invalid
        CollinearityError: If perfect collinearity detected in design matrix

    Example:
        >>> df = pd.DataFrame({
        ...     'gvkey': [1, 1, 2, 2],
        ...     'year': [2020, 2021, 2020, 2021],
        ...     'ff48_code': [10, 10, 20, 20],
        ...     'cash_ratio': [0.1, 0.12, 0.05, 0.06],
        ...     'vagueness': [0.5, 0.6, 0.3, 0.4],
        ...     'size': [10, 11, 8, 9],
        ... })
        >>> result = run_panel_ols(
        ...     df=df,
        ...     dependent='cash_ratio',
        ...     exog=['vagueness', 'size'],
        ...     entity_effects=True,
        ...     time_effects=True
        ... )
        >>> print(result['summary']['rsquared'])
    """
    # Verify linearmodels available
    if not LINEARMODELS_AVAILABLE:
        raise ImportError("linearmodels is required. Install: pip install linearmodels")

    warnings_collected: List[str] = []

    # Validate required columns exist
    required_cols = [entity_col, time_col, dependent] + exog
    if industry_effects:
        required_cols.append(industry_col)

    missing = set(required_cols) - set(df.columns)
    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}. "
            f"Available: {sorted(df.columns)}"
        )

    # Create working copy
    df_work = df.copy()

    # Check for thin industry cells if industry effects requested
    if industry_effects and industry_col in df_work.columns:
        has_thin, cell_counts = _check_thin_cells(
            df_work, industry_col, time_col, min_industry_firms
        )
        if has_thin:
            msg = (
                f"Thin industry-year cells detected: "
                f"{sum(1 for v in cell_counts.values() if v < min_industry_firms)} cells "
                f"have < {min_industry_firms} firms. "
                f"This may cause noisy estimates."
            )
            warnings_collected.append(msg)
            warnings.warn(msg, UserWarning, stacklevel=2)

    # Warn about firm + industry FE collinearity
    if entity_effects and industry_effects:
        msg = (
            "Both firm and industry fixed effects requested. "
            "Firms rarely change industries, so firm FE typically subsumes industry FE. "
            "This may cause rank deficiency. Use check_rank=True to detect."
        )
        warnings_collected.append(msg)
        warnings.warn(msg, UserWarning, stacklevel=2)

    # Set MultiIndex for panel data
    df_work = df_work.set_index([entity_col, time_col])

    # Prepare exog variables (handle missing values)
    exog_data = df_work[exog].copy()
    dependent_data = df_work[dependent]

    # Check for missing values in regression data
    missing_exog = exog_data.isna().sum()
    # Initialize complete_idx before conditional (fixes UnboundLocalError when industry_effects=True)
    complete_idx = exog_data.notna().all(axis=1) & dependent_data.notna()

    if missing_exog.sum() > 0:
        warnings_collected.append(
            f"Missing values in exog variables: {missing_exog[missing_exog > 0].to_dict()}. "
            "Dropping observations with missing values."
        )
        # Use complete cases
        exog_data = exog_data[complete_idx]
        dependent_data = dependent_data[complete_idx]

    # Build model
    model_kwargs = {
        "dependent": dependent_data,
        "exog": exog_data,
        "entity_effects": entity_effects,
        "time_effects": time_effects,
        "drop_absorbed": False,
        "check_rank": True,
    }

    # Add industry effects if requested
    if industry_effects and industry_col in df_work.columns:
        # Need to align industry column with filtered data
        # Use exog_data.index which already has complete_idx filter applied
        industry_data = df_work.loc[exog_data.index, industry_col]
        model_kwargs["other_effects"] = industry_data

    try:
        model = PanelOLS(**model_kwargs)
    except Exception as e:
        if "rank" in str(e).lower() or "collinear" in str(e).lower():
            raise CollinearityError(
                f"Perfect collinearity detected in design matrix: {e}"
            ) from e
        raise

    # Prepare fit kwargs based on covariance type
    fit_kwargs: Dict[str, Any] = {"debiased": True}

    if cov_type == "clustered":
        fit_kwargs["cov_type"] = "clustered"

        if cluster_cols is not None and len(cluster_cols) > 1:
            # Double clustering - need to get cluster columns from index
            # After set_index([entity_col, time_col]), these are in the index
            cluster_df = pd.DataFrame(index=exog_data.index)
            for col in cluster_cols:
                if col in df_work.index.names:
                    # Column is in the MultiIndex
                    cluster_df[col] = exog_data.index.get_level_values(col)
                elif col in df_work.columns:
                    # Column is still in columns (before set_index)
                    cluster_df[col] = df_work.loc[exog_data.index, col]
            fit_kwargs["clusters"] = cluster_df
        elif cluster_cols is not None and len(cluster_cols) == 1:
            # Single cluster on specific column
            if cluster_cols[0] == entity_col:
                fit_kwargs["cluster_entity"] = True
            elif cluster_cols[0] == time_col:
                fit_kwargs["cluster_time"] = True
        else:
            # Default: cluster at entity level
            fit_kwargs["cluster_entity"] = True

    elif cov_type == "kernel":
        fit_kwargs["cov_type"] = "kernel"
        fit_kwargs["kernel"] = kernel
        # bandwidth=None lets linearmodels auto-select
    else:
        fit_kwargs["cov_type"] = "robust"

    # Fit model
    try:
        result = model.fit(**fit_kwargs)
    except Exception as e:
        if "rank" in str(e).lower() or "singular" in str(e).lower():
            raise CollinearityError(
                f"Perfect collinearity during estimation: {e}"
            ) from e
        raise

    # Extract coefficients and statistics
    coefficients_df = pd.DataFrame(
        {
            "Coefficient": result.params,
            "Std. Error": result.std_errors,
            "t-stat": result.tstats,
        }
    )

    # Build summary
    f_stat = None
    f_pval = None
    if hasattr(result, "f_statistic") and result.f_statistic is not None:
        f_stat = float(result.f_statistic.stat)
        f_pval = float(result.f_statistic.pval)

    summary = {
        "rsquared": float(result.rsquared),
        "rsquared_within": float(result.rsquared_within)
        if hasattr(result, "rsquared_within")
        else None,
        "nobs": int(result.nobs),
        "entity_effects": entity_effects,
        "time_effects": time_effects,
        "industry_effects": industry_effects,
        "cov_type": cov_type,
        "f_statistic": f_stat,
        "f_pvalue": f_pval,
    }

    # Diagnostics (VIF)
    diagnostics: Dict[str, Any] = {
        "residual_std": None,
        "condition_number": None,
        "vif": None,
    }

    vif_df = None
    if check_collinearity:
        # Import VIF computation
        try:
            from f1d.shared.diagnostics import compute_vif as compute_vif_imported  # type: ignore[import-untyped]
            compute_vif = compute_vif_imported
        except ImportError:
            # If diagnostics module not yet created, compute here
            try:
                from statsmodels.stats.outliers_influence import (  # type: ignore[import-untyped]
                    variance_inflation_factor,
                )
                from statsmodels.tools.tools import add_constant  # type: ignore[import-untyped]

                def compute_vif(  # type: ignore[no-redef]
                    df_local: pd.DataFrame,
                    cols: list[str],
                    add_constant_col: bool = True,
                    vif_threshold_local: float = 5.0,
                ) -> Any:
                    df_vif = df_local[cols].dropna()
                    if add_constant_col:
                        df_vif = add_constant(df_vif)
                    vif_data = []
                    for i, col in enumerate(cols):
                        if col in df_vif.columns:
                            vif_val = variance_inflation_factor(df_vif.values, i)
                            vif_data.append(
                                {
                                    "variable": col,
                                    "VIF": vif_val,
                                    "threshold_exceeded": vif_val > vif_threshold_local,
                                }
                            )
                    return pd.DataFrame(vif_data)
            except ImportError:
                compute_vif = None  # type: ignore

        if compute_vif is not None:
            try:
                # Get original df for VIF (before index set)
                exog_for_vif = df[exog].dropna()
                # Call with appropriate parameters based on function signature
                if hasattr(compute_vif, "__code__") and "add_constant_col" in compute_vif.__code__.co_varnames:
                    vif_df = compute_vif(exog_for_vif, exog, add_constant_col=True, vif_threshold_local=vif_threshold)  # type: ignore[call-arg]
                else:
                    vif_df = compute_vif(exog_for_vif, exog, add_constant=True)  # type: ignore[call-arg]

                # Check for VIF violations
                high_vif = vif_df[vif_df["threshold_exceeded"]]
                if len(high_vif) > 0:
                    vif_warning = (
                        f"High VIF detected: {high_vif['variable'].tolist()} "
                        f"with values {high_vif['VIF'].tolist()}. "
                        f"Threshold: {vif_threshold}"
                    )
                    warnings_collected.append(vif_warning)
                    warnings.warn(f"WARNING: {vif_warning}", UserWarning, stacklevel=2)

                diagnostics["vif"] = vif_df.to_dict("records")

            except Exception as e:
                warnings_collected.append(f"VIF computation failed: {e}")

    # Condition number from result if available
    if hasattr(result, "condition_number"):
        diagnostics["condition_number"] = float(result.condition_number)

    # Residual standard deviation
    if hasattr(result, "resids"):
        diagnostics["residual_std"] = float(np.std(result.resids))

    # Print formatted output
    output_str = _format_coefficient_table(
        coefficients_df, result.pvalues, vif_df, vif_threshold
    )

    # Add summary section
    output_str += "\nModel Summary:\n"
    output_str += "-" * 40 + "\n"
    output_str += f"  Observations:     {summary['nobs']:,}\n"
    output_str += f"  R-squared:        {summary['rsquared']:.4f}\n"
    if summary["rsquared_within"] is not None:
        output_str += f"  R-squared (within): {summary['rsquared_within']:.4f}\n"
    if f_stat is not None:
        output_str += f"  F-statistic:      {f_stat:.2f} (p-value: {f_pval:.4f})\n"
    output_str += "\n  Fixed Effects:\n"
    output_str += f"    Entity (firm):   {summary['entity_effects']}\n"
    output_str += f"    Time (year):     {summary['time_effects']}\n"
    output_str += f"    Industry:        {summary['industry_effects']}\n"
    output_str += f"\n  Covariance:       {summary['cov_type']}\n"
    output_str += "=" * 80

    print(output_str)

    return {
        "model": result,
        "coefficients": coefficients_df,
        "summary": summary,
        "diagnostics": diagnostics,
        "warnings": warnings_collected,
    }


# Export symbols
__all__ = [
    "run_panel_ols",
    "CollinearityError",
    "MulticollinearityError",
]
