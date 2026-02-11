#!/usr/bin/env python3
"""
================================================================================
SHARED MODULE: IV Regression (2SLS with Instrument Diagnostics)
================================================================================
ID: shared/iv_regression
Description: Two-stage least squares (2SLS) with instrument diagnostics for
             endogeneity concerns. Provides first-stage F-stat validation,
             Hansen J overidentification test, and comprehensive diagnostics.

Inputs:
    - pandas DataFrame with regression data
    - Dependent variable name
    - Exogenous regressors (controls)
    - Endogenous regressor (suspected endogenous variable)
    - Instrumental variables (excluded instruments)

Outputs:
    - Fitted IV2SLS model object
    - Coefficients DataFrame with beta, SE, t-stat, p-value
    - First-stage diagnostics (F-stat, partial R2, predictions)
    - Overidentification test results (Hansen J / Sargan)
    - Warnings list for any issues detected

Deterministic: true
Main Functions:
    - run_iv_regression(): Execute instrumental variables regression

Dependencies:
    - Utility module for IV regression
    - Uses: linearmodels, pandas, numpy

Author: Thesis Author
Date: 2026-02-11
================================================================================
"""

from typing import Any, Dict, List, Optional, Union

# Try importing linearmodels, provide helpful error if missing
try:
    from linearmodels.iv.model import IV2SLS  # type: ignore[import-untyped]
    from linearmodels.iv.results import IVResults  # type: ignore[import-untyped]

    LINEARMODELS_AVAILABLE = True
except ImportError:
    LINEARMODELS_AVAILABLE = False
    IV2SLS = None  # type: ignore
    IVResults = None  # type: ignore

import pandas as pd  # type: ignore[import-untyped]


class WeakInstrumentError(Exception):
    """Raised when first-stage F-stat < 10 (weak instruments).

    When first-stage F < 10, 2SLS estimates are more biased than OLS.
    This error enforces hard failure to prevent reporting invalid results.

    Attributes:
        message: Error message with actual F-stat and threshold
        f_stat: The actual first-stage F-statistic
        threshold: The threshold that was not met
    """

    def __init__(
        self,
        message: str,
        f_stat: Optional[float] = None,
        threshold: Optional[float] = None,
    ) -> None:
        super().__init__(message)
        self.f_stat = f_stat
        self.threshold = threshold


def _add_constant_to_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Add constant column to DataFrame for IV2SLS estimation.

    Args:
        df: DataFrame to modify

    Returns:
        DataFrame with added 'const' column (all 1.0)
    """
    df = df.copy()
    df["const"] = 1.0
    return df


def _format_star(pvalue: float) -> str:
    """Format significance stars based on p-value.

    Args:
        pvalue: P-value for coefficient

    Returns:
        String with significance stars: '***', '**', '*', or ''
    """
    if pvalue < 0.01:
        return "***"
    elif pvalue < 0.05:
        return "**"
    elif pvalue < 0.10:
        return "*"
    return ""


def _format_number(value: float, decimals: int = 3) -> str:
    """Format number with specified decimal places.

    Args:
        value: Number to format
        decimals: Number of decimal places

    Returns:
        Formatted string
    """
    return f"{value:.{decimals}f}"


def run_iv2sls(
    df: pd.DataFrame,
    dependent: str,
    exog: List[str],
    endog: str,
    instruments: List[str],
    add_constant: bool = True,
    cov_type: str = "robust",
    cluster_col: Optional[str] = None,
    f_threshold: float = 10.0,
    fail_on_weak: bool = True,
    save_first_stage: bool = True,
) -> Dict[str, Any]:
    """Run Two-Stage Least Squares (2SLS) regression with instrument validation.

    This function provides a complete 2SLS implementation with:
    - First-stage F-stat validation (weak instrument check)
    - Hansen J / Sargan overidentification test
    - Comprehensive diagnostics and formatted output

    Args:
        df: DataFrame with all variables
        dependent: Name of dependent variable (Y)
        exog: List of exogenous regressor names (controls, X)
        endog: Name of endogenous regressor (suspected endogenous variable)
        instruments: List of instrumental variable names (Z)
        add_constant: If True, add constant term to exog
        cov_type: Covariance type: 'robust', 'clustered', 'kernel', 'unadjusted'
        cluster_col: Column name for clustering (if cov_type='clustered')
        f_threshold: First-stage F-stat threshold (default 10.0)
        fail_on_weak: If True, raise WeakInstrumentError when F < threshold
        save_first_stage: If True, save first-stage predictions in return dict

    Returns:
        Dictionary containing:
            - 'model': Fitted IV2SLS model object
            - 'coefficients': DataFrame with beta, SE, t-stat, p-value, stars
            - 'summary': Dict with R2, N, F-stat, etc.
            - 'first_stage': Dict with F-stat, partial R2, predictions (optional)
            - 'overid_test': Dict with Hansen J stat and p-value (or None)
            - 'warnings': List of any warnings triggered

    Raises:
        ImportError: If linearmodels not available
        WeakInstrumentError: If first-stage F < threshold and fail_on_weak=True
        ValueError: If data validation fails

    Example:
        >>> result = run_iv2sls(
        ...     df=data,
        ...     dependent='investment',
        ...     exog=['size', 'leverage', 'roa'],
        ...     endog='vagueness',
        ...     instruments=['prior_vagueness', 'peer_vagueness']
        ... )
        >>> print(result['first_stage']['f_stat'])
        >>> print(result['coefficients'])
    """
    if not LINEARMODELS_AVAILABLE:
        raise ImportError(
            "linearmodels required for 2SLS regression. "
            "Install: pip install linearmodels"
        )

    # Input validation
    if dependent not in df.columns:
        raise ValueError(f"Dependent variable '{dependent}' not in DataFrame")
    if endog not in df.columns:
        raise ValueError(f"Endogenous variable '{endog}' not in DataFrame")
    for var in exog:
        if var not in df.columns:
            raise ValueError(f"Exogenous variable '{var}' not in DataFrame")
    for var in instruments:
        if var not in df.columns:
            raise ValueError(f"Instrument '{var}' not in DataFrame")

    warnings_list: List[str] = []

    # Prepare data - work with a copy
    df_reg = df.copy()

    # Drop missing values for regression
    all_cols = [dependent, endog] + exog + instruments
    if cluster_col and cluster_col in df_reg.columns:
        all_cols.append(cluster_col)

    df_reg = df_reg[all_cols].dropna()

    # Add constant to exog if requested
    if add_constant:
        df_reg = _add_constant_to_dataframe(df_reg)
        exog_with_const = exog + ["const"]
    else:
        exog_with_const = exog.copy()

    # Handle clustering
    cov_kwargs = {}
    if cov_type == "clustered" and cluster_col is not None:
        cov_kwargs["cov_type"] = "clustered"
        cov_kwargs["clusters"] = df_reg[[cluster_col]].reset_index(drop=True)
    elif cov_type == "kernel":
        cov_kwargs["cov_type"] = "kernel"
        cov_kwargs["kernel"] = "bartlett"
    elif cov_type == "robust":
        cov_kwargs["cov_type"] = "robust"
    else:
        cov_kwargs["cov_type"] = "unadjusted"

    # Build and fit IV2SLS model
    # IV2SLS signature: IV2SLS(dependent, exog, endog, instruments)
    model = IV2SLS(
        dependent=df_reg[dependent],
        exog=df_reg[exog_with_const],
        endog=df_reg[[endog]],
        instruments=df_reg[instruments],
    )

    result = model.fit(**cov_kwargs)

    # Extract first-stage diagnostics
    # linearmodels IV2SLS results have first_stage attribute
    first_stage = result.first_stage  # type: ignore[attr-defined]
    diagnostics_df = first_stage.diagnostics  # type: ignore[attr-defined]

    # Get first-stage F-stat for endogenous variable
    if endog in diagnostics_df.index:
        f_stat = float(diagnostics_df.loc[endog, "f.stat"])
        f_pval = float(diagnostics_df.loc[endog, "f.pval"])
        partial_rsq = float(diagnostics_df.loc[endog, "partial.rsquared"])
        shea_rsq = (
            float(diagnostics_df.loc[endog, "shea.rsquared"])
            if "shea.rsquared" in diagnostics_df.columns
            else None
        )
    else:
        # If endog not directly in diagnostics, try alternative access
        f_stat = float(first_stage.individual[endog].f_stat)  # type: ignore[attr-defined]
        f_pval = None
        partial_rsq = float(first_stage.individual[endog].partial_rsquared)  # type: ignore[attr-defined]
        shea_rsq = None

    # First-stage F validation
    print(f"\n{'=' * 70}")
    print("FIRST-STAGE DIAGNOSTICS")
    print(f"{'=' * 70}")
    print(f"Endogenous variable: {endog}")
    print(f"First-stage F-stat: {f_stat:.2f} (threshold: {f_threshold})")
    print(
        f"First-stage p-value: {f_pval:.4f}"
        if f_pval is not None
        else "First-stage p-value: N/A"
    )
    print(f"Partial R-squared: {partial_rsq:.4f}")
    if shea_rsq is not None:
        print(f"Shea's R-squared: {shea_rsq:.4f}")
    print(f"{'=' * 70}")

    # Check for weak instruments
    if f_stat < f_threshold:
        msg = (
            f"WEAK INSTRUMENTS DETECTED: First-stage F = {f_stat:.2f} < {f_threshold}. "
            f"2SLS estimates are more biased than OLS with weak instruments."
        )
        if fail_on_weak:
            raise WeakInstrumentError(msg, f_stat=f_stat, threshold=f_threshold)
        else:
            warnings_list.append(msg)
            print(f"WARNING: {msg}")

    # Overidentification test (Hansen J / Sargan)
    # Only available when over-identified: # instruments > # endogenous
    n_instr = len(instruments)
    n_endog = 1  # Currently only single endogenous supported

    overid_test: Dict[str, Any] = {"stat": None, "pval": None, "valid": False, "note": None}

    if n_instr > n_endog:
        # Over-identified: can run Sargan/Hansen J test
        sargan = result.sargan  # type: ignore[attr-defined]
        overid_test["stat"] = float(sargan.stat)
        overid_test["pval"] = float(sargan.pval)
        overid_test["valid"] = True
        overid_test["reject_null"] = sargan.pval < 0.05  # type: ignore[assignment]

        # Interpret results
        # H0: Instruments are valid (uncorrelated with error, exogenous)
        # Reject H0 (p < 0.05) -> instruments may be invalid
        if overid_test["reject_null"]:  # type: ignore[comparison-overlap]
            interpretation = (  # type: ignore[assignment]
                "p < 0.05: instruments may be invalid (correlated with error)"
            )
            warnings_list.append(
                f"Sargan test rejects null (p={sargan.pval:.3f}): "
                f"Instruments may be invalid"
            )
        else:
            interpretation = "p >= 0.05: instruments appear valid"

        print("\nOVERIDENTIFICATION TEST (Sargan / Hansen J)")
        print(f"{'=' * 70}")
        print(f"Test statistic: {overid_test['stat']:.3f}")
        print(f"p-value: {overid_test['pval']:.3f}")
        print(f"Interpretation: {interpretation}")
        print(f"{'=' * 70}")
    else:
        overid_test["note"] = (
            f"Exactly identified ({n_instr} instrument(s) for {n_endog} "
            f"endogenous variable): Sargan/Hansen J test not available"
        )
        print("\nOVERIDENTIFICATION TEST")
        print(f"{'=' * 70}")
        print(overid_test["note"])
        print(f"{'=' * 70}")

    # Build coefficients DataFrame
    coef_names = result.params.index.tolist()
    coefficients = pd.DataFrame(
        {
            "variable": coef_names,
            "coefficient": result.params.values,
            "std_error": result.std_errors.values,
            "t_stat": result.tstats.values,
            "p_value": result.pvalues.values,
            "stars": [_format_star(p) for p in result.pvalues.values],
        }
    )

    # Format for display
    coefficients["coef_formatted"] = coefficients.apply(
        lambda row: _format_number(row["coefficient"], 3) + row["stars"], axis=1
    )
    coefficients["se_formatted"] = coefficients["std_error"].apply(
        lambda x: "(" + _format_number(x, 3) + ")"
    )

    # Print coefficient table
    print("\nIV2SLS RESULTS")
    print(f"{'=' * 70}")
    print(f"Dependent variable: {dependent}")
    print(f"Endogenous variable: {endog}")
    print(f"Instruments: {', '.join(instruments)}")
    print(f"{'=' * 70}\n")

    for var in coef_names:
        row = coefficients[coefficients["variable"] == var].iloc[0]
        print(f"{var:20s} {row['coef_formatted']:>15s}")
        print(f"{'':20s} {row['se_formatted']:>15s}")

    print(f"\n{'=' * 70}")
    print(f"Observations: {int(result.nobs):,}")
    print(f"R-squared: {result.rsquared:.4f}")
    if hasattr(result, "f_statistic") and result.f_statistic is not None:
        print(f"F-statistic: {result.f_statistic.stat:.3f}")
    print(f"{'=' * 70}")

    # Build summary dictionary
    summary = {
        "n_obs": int(result.nobs),
        "rsquared": float(result.rsquared),
        "f_statistic": float(result.f_statistic.stat)
        if hasattr(result, "f_statistic") and result.f_statistic is not None
        else None,
        "cov_type": cov_type,
        "dependent": dependent,
        "endog": endog,
        "instruments": instruments,
        "exog": exog,
    }

    # Build first-stage dictionary
    first_stage_dict = {
        "f_stat": f_stat,
        "f_pval": f_pval,
        "partial_rsquared": partial_rsq,
        "shea_rsquared": shea_rsq,
        "threshold": f_threshold,
        "above_threshold": f_stat >= f_threshold,
    }

    # Optionally save first-stage predictions
    if save_first_stage:
        # Get first-stage predictions for the endogenous variable
        # first_stage is a FirstStageResults object
        # Access predictions via the fitted first-stage model
        if hasattr(first_stage, "individual"):
            first_stage_model = first_stage.individual[endog]  # type: ignore[attr-defined]
            if hasattr(first_stage_model, "fitted_values"):
                first_stage_dict["predictions"] = first_stage_model.fitted_values  # type: ignore[attr-defined]
            else:
                # Try to get predictions differently
                first_stage_dict["predictions"] = None
        else:
            first_stage_dict["predictions"] = None

    return {
        "model": result,
        "coefficients": coefficients,
        "summary": summary,
        "first_stage": first_stage_dict,
        "overid_test": overid_test,
        "warnings": warnings_list,
    }


def run_iv2sls_panel(
    df: pd.DataFrame,
    dependent: str,
    exog: List[str],
    endog: str,
    instruments: List[str],
    entity_col: str = "gvkey",
    time_col: str = "year",
    add_constant: bool = True,
    cov_type: str = "robust",
    f_threshold: float = 10.0,
    fail_on_weak: bool = True,
) -> Dict[str, Any]:
    """Run 2SLS regression with panel data structure.

    Convenience function that sets up panel index before running 2SLS.
    The IV2SLS estimator itself doesn't use panel structure directly,
    but this function ensures proper data organization.

    Args:
        df: DataFrame with panel data (must have entity_col and time_col)
        dependent: Name of dependent variable
        exog: List of exogenous regressor names
        endog: Name of endogenous regressor
        instruments: List of instrumental variable names
        entity_col: Column name for entity identifier (default 'gvkey')
        time_col: Column name for time identifier (default 'year')
        add_constant: If True, add constant term
        cov_type: Covariance type
        f_threshold: First-stage F threshold
        fail_on_weak: If True, raise WeakInstrumentError on weak instruments

    Returns:
        Dictionary with same structure as run_iv2sls()

    Note:
        This function sets MultiIndex on the DataFrame but runs the same
        IV2SLS estimator. For true panel IV with entity effects, consider
        using linearmodels.panel.IV2SLS with entity_effects=True instead.
    """
    # Set panel index
    df_panel = df.set_index([entity_col, time_col]).copy()

    # Run standard 2SLS
    result = run_iv2sls(
        df=df_panel,
        dependent=dependent,
        exog=exog,
        endog=endog,
        instruments=instruments,
        add_constant=add_constant,
        cov_type=cov_type,
        f_threshold=f_threshold,
        fail_on_weak=fail_on_weak,
        save_first_stage=True,
    )

    # Add panel metadata to summary
    result["summary"]["entity_col"] = entity_col
    result["summary"]["time_col"] = time_col
    result["summary"]["n_entities"] = df_panel.index.get_level_values(0).nunique()
    result["summary"]["n_periods"] = df_panel.index.get_level_values(1).nunique()

    return result


def summarize_iv_results(result_dict: Dict[str, Any]) -> str:
    """Generate a formatted summary string of IV regression results.

    Args:
        result_dict: Return value from run_iv2sls()

    Returns:
        Formatted multi-line summary string
    """
    lines = [
        "=" * 70,
        "IV2SLS REGRESSION SUMMARY",
        "=" * 70,
        "",
        f"Dependent Variable: {result_dict['summary']['dependent']}",
        f"Endogenous Variable: {result_dict['summary']['endog']}",
        f"Instruments: {', '.join(result_dict['summary']['instruments'])}",
        "",
        "-" * 70,
        "FIRST-STAGE DIAGNOSTICS",
        "-" * 70,
        f"F-statistic: {result_dict['first_stage']['f_stat']:.2f}",
        f"Threshold: {result_dict['first_stage']['threshold']:.0f}",
        f"Partial R-squared: {result_dict['first_stage']['partial_rsquared']:.4f}",
        f"Above Threshold: {'Yes' if result_dict['first_stage']['above_threshold'] else 'No (WEAK)'}",
        "",
        "-" * 70,
        "SECOND-STAGE RESULTS",
        "-" * 70,
        f"Observations: {result_dict['summary']['n_obs']:,}",
        f"R-squared: {result_dict['summary']['rsquared']:.4f}",
    ]

    if result_dict["summary"]["f_statistic"]:
        lines.append(f"F-statistic: {result_dict['summary']['f_statistic']:.3f}")

    lines.append("")
    lines.append("-" * 70)
    lines.append("COEFFICIENTS")
    lines.append("-" * 70)

    coef_df = result_dict["coefficients"]
    for _, row in coef_df.iterrows():
        lines.append(f"{row['variable']:20s} {row['coef_formatted']:>15s}")
        lines.append(f"{'':20s} {row['se_formatted']:>15s}")

    lines.append("")
    lines.append("=" * 70)

    return "\n".join(lines)


if __name__ == "__main__":
    # Simple usage demonstration
    print("IV Regression Module")
    print("=" * 70)
    print(f"linearmodels available: {LINEARMODELS_AVAILABLE}")
    if LINEARMODELS_AVAILABLE:
        print("Module ready for use. See docstring for run_iv2sls() usage.")
    else:
        print(
            "ERROR: linearmodels not installed. Install with: pip install linearmodels"
        )
