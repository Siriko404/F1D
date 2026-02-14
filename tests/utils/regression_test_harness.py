"""
Regression Test Harness Utilities for F1D Econometric Analysis.

This module provides reusable utilities for testing regression scripts
across all hypothesis tests (H1-H9) and CEO fixed effects analysis.

Key Features:
- Mock panel OLS result generation
- Sample data generation for all hypothesis tests
- Common test assertions for regression results
- Test configuration management
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from unittest.mock import MagicMock


# ==============================================================================
# Mock Panel OLS Result Generator
# ==============================================================================

def create_mock_panel_ols_result(
    coefficients: Dict[str, Tuple[float, float]],
    rsquared: float = 0.30,
    rsquared_within: float = 0.15,
    nobs: int = 200,
    entity_effects: bool = True,
    time_effects: bool = True,
    f_statistic: float = 15.0,
    f_pvalue: float = 0.001,
    warnings: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Create a mock result from run_panel_ols for testing.

    Args:
        coefficients: Dict mapping variable names to (coefficient, std_error) tuples
        rsquared: R-squared value
        rsquared_within: Within R-squared value
        nobs: Number of observations
        entity_effects: Whether entity effects were used
        time_effects: Whether time effects were used
        f_statistic: F-statistic value
        f_pvalue: F-statistic p-value
        warnings: List of warning messages

    Returns:
        Dictionary mimicking run_panel_ols result structure
    """
    # Build coefficients DataFrame
    coef_data = []
    pvalues = {}
    for var, (coef, se) in coefficients.items():
        t_stat = coef / se if se > 0 else 0.0
        coef_data.append({
            "Coefficient": coef,
            "Std. Error": se,
            "t-stat": t_stat,
        })
        # Approximate p-value based on t-stat
        from scipy import stats
        pval = 2 * (1 - stats.t.cdf(abs(t_stat), df=nobs - len(coefficients)))
        pvalues[var] = pval

    coef_df = pd.DataFrame(coef_data, index=list(coefficients.keys()))

    # Create mock model with pvalues
    mock_model = MagicMock()
    mock_model.pvalues = pd.Series(pvalues)

    return {
        "model": mock_model,
        "coefficients": coef_df,
        "summary": {
            "rsquared": rsquared,
            "rsquared_within": rsquared_within,
            "nobs": nobs,
            "entity_effects": entity_effects,
            "time_effects": time_effects,
            "cov_type": "clustered",
            "f_statistic": f_statistic,
            "f_pvalue": f_pvalue,
        },
        "diagnostics": {"vif": None},
        "warnings": warnings or [],
    }


# ==============================================================================
# Sample Data Generators
# ==============================================================================

def generate_panel_data(
    n_firms: int = 50,
    n_years: int = 5,
    seed: int = 42,
    extra_columns: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    """
    Generate synthetic panel data for testing.

    Args:
        n_firms: Number of firms
        n_years: Number of years
        seed: Random seed
        extra_columns: Dict of column_name -> generator function or constant

    Returns:
        DataFrame with gvkey, fiscal_year, and extra columns
    """
    np.random.seed(seed)

    data = []
    for firm_id in range(n_firms):
        gvkey = str(firm_id).zfill(6)
        for year_offset in range(n_years):
            fiscal_year = 2010 + year_offset
            row = {"gvkey": gvkey, "fiscal_year": fiscal_year}

            if extra_columns:
                for col, spec in extra_columns.items():
                    if callable(spec):
                        row[col] = spec()
                    else:
                        row[col] = spec

            data.append(row)

    return pd.DataFrame(data)


def generate_h1_data(n_firms: int = 50, n_years: int = 5, seed: int = 42) -> pd.DataFrame:
    """Generate sample data for H1 (Cash Holdings) tests."""
    extra_cols = {
        "cash_ratio": lambda: np.random.uniform(0.05, 0.3),
        "Manager_QA_Uncertainty_pct": lambda: np.random.uniform(2, 8),
        "CEO_QA_Uncertainty_pct": lambda: np.random.uniform(2, 8),
        "firm_size": lambda: np.random.uniform(5, 10),
        "tobins_q": lambda: np.random.uniform(0.8, 2.0),
        "roa": lambda: np.random.uniform(-0.1, 0.2),
        "leverage": lambda: np.random.uniform(0.1, 0.6),
    }
    return generate_panel_data(n_firms, n_years, seed, extra_cols)


def generate_h2_data(n_firms: int = 50, n_years: int = 5, seed: int = 42) -> pd.DataFrame:
    """Generate sample data for H2 (Investment Efficiency) tests."""
    extra_cols = {
        "investment_q": lambda: np.random.uniform(0.8, 1.5),
        "Manager_QA_Uncertainty_pct": lambda: np.random.uniform(2, 8),
        "analyst_qa_uncertainty": lambda: np.random.uniform(1, 5),
        "firm_size": lambda: np.random.uniform(5, 10),
        "tobins_q": lambda: np.random.uniform(0.8, 2.0),
        "roa": lambda: np.random.uniform(-0.1, 0.2),
        "leverage": lambda: np.random.uniform(0.1, 0.6),
    }
    return generate_panel_data(n_firms, n_years, seed, extra_cols)


def generate_h3_data(n_firms: int = 50, n_years: int = 5, seed: int = 42) -> pd.DataFrame:
    """Generate sample data for H3 (Payout Policy) tests."""
    extra_cols = {
        "div_stability": lambda: np.random.uniform(0, 1),
        "payout_flexibility": lambda: np.random.uniform(0, 1),
        "Manager_QA_Uncertainty_pct": lambda: np.random.uniform(2, 8),
        "leverage": lambda: np.random.uniform(0.1, 0.6),
        "earnings_volatility": lambda: np.random.uniform(0, 0.2),
        "firm_size": lambda: np.random.uniform(5, 10),
    }
    return generate_panel_data(n_firms, n_years, seed, extra_cols)


def generate_h4_data(n_firms: int = 50, n_years: int = 5, seed: int = 42) -> pd.DataFrame:
    """Generate sample data for H4 (Leverage Discipline) tests."""
    extra_cols = {
        "leverage": lambda: np.random.uniform(0.1, 0.6),
        "Manager_QA_Uncertainty_pct": lambda: np.random.uniform(2, 8),
        "analyst_qa_uncertainty": lambda: np.random.uniform(1, 5),
        "firm_size": lambda: np.random.uniform(5, 10),
        "tobins_q": lambda: np.random.uniform(0.8, 2.0),
    }
    return generate_panel_data(n_firms, n_years, seed, extra_cols)


def generate_h5_data(n_firms: int = 50, n_years: int = 5, seed: int = 42) -> pd.DataFrame:
    """Generate sample data for H5 (Analyst Dispersion) tests."""
    extra_cols = {
        "dispersion_lead": lambda: np.random.uniform(0.01, 0.2),
        "Manager_QA_Weak_Modal_pct": lambda: np.random.uniform(1, 5),
        "Manager_QA_Uncertainty_pct": lambda: np.random.uniform(2, 8),
        "prior_dispersion": lambda: np.random.uniform(0.01, 0.2),
        "analyst_coverage": lambda: np.random.uniform(1, 4),
        "firm_size": lambda: np.random.uniform(5, 10),
    }
    return generate_panel_data(n_firms, n_years, seed, extra_cols)


def generate_ceo_data(
    n_ceos: int = 20,
    calls_range: Tuple[int, int] = (3, 15),
    seed: int = 42,
) -> pd.DataFrame:
    """Generate sample data for CEO fixed effects tests."""
    np.random.seed(seed)

    data = []
    call_id = 0
    for ceo_idx in range(n_ceos):
        ceo_id = f"CEO_{ceo_idx:03d}"
        n_calls = np.random.randint(calls_range[0], calls_range[1] + 1)

        for call_offset in range(n_calls):
            year = 2010 + (call_offset % 9)
            call_id += 1
            data.append({
                "ceo_id": ceo_id,
                "gvkey": str(ceo_idx % 10).zfill(6),
                "year": year,
                "CEO_QA_Uncertainty_pct": np.random.uniform(2, 8),
                "CEO_Pres_Uncertainty_pct": np.random.uniform(1, 5),
                "Analyst_QA_Uncertainty_pct": np.random.uniform(1, 5),
            })

    return pd.DataFrame(data)


# ==============================================================================
# Hypothesis Test Helpers
# ==============================================================================

def calculate_one_tailed_pvalue(
    coefficient: float,
    p_two_tailed: float,
    hypothesis_direction: str = "positive",
) -> float:
    """
    Calculate one-tailed p-value from two-tailed p-value.

    Args:
        coefficient: The regression coefficient
        p_two_tailed: Two-tailed p-value
        hypothesis_direction: "positive" for beta > 0, "negative" for beta < 0

    Returns:
        One-tailed p-value
    """
    if hypothesis_direction == "positive":
        if coefficient > 0:
            return p_two_tailed / 2
        else:
            return 1 - p_two_tailed / 2
    else:  # negative
        if coefficient < 0:
            return p_two_tailed / 2
        else:
            return 1 - p_two_tailed / 2


def check_hypothesis_supported(
    coefficient: float,
    p_one_tailed: float,
    alpha: float = 0.05,
    expected_sign: str = "positive",
) -> bool:
    """
    Check if hypothesis is supported based on coefficient and p-value.

    Args:
        coefficient: The regression coefficient
        p_one_tailed: One-tailed p-value
        alpha: Significance level
        expected_sign: "positive" or "negative"

    Returns:
        True if hypothesis is supported
    """
    is_significant = p_one_tailed < alpha

    if expected_sign == "positive":
        correct_sign = coefficient > 0
    else:
        correct_sign = coefficient < 0

    return is_significant and correct_sign


# ==============================================================================
# Common Assertions
# ==============================================================================

def assert_valid_regression_result(result: Dict[str, Any]) -> None:
    """Assert that a regression result has the expected structure."""
    required_keys = ["model", "coefficients", "summary", "diagnostics", "warnings"]
    for key in required_keys:
        assert key in result, f"Missing key: {key}"

    # Check coefficients structure
    coef_df = result["coefficients"]
    required_coef_cols = ["Coefficient", "Std. Error", "t-stat"]
    for col in required_coef_cols:
        assert col in coef_df.columns, f"Missing coefficient column: {col}"

    # Check summary structure
    summary = result["summary"]
    required_summary_keys = ["rsquared", "nobs", "entity_effects", "time_effects"]
    for key in required_summary_keys:
        assert key in summary, f"Missing summary key: {key}"


def assert_coefficient_significant(
    result: Dict[str, Any],
    variable: str,
    alpha: float = 0.05,
) -> None:
    """Assert that a coefficient is statistically significant."""
    pvalues = result["model"].pvalues
    assert variable in pvalues.index, f"Variable {variable} not in p-values"
    assert pvalues[variable] < alpha, f"Coefficient {variable} not significant at {alpha}"


def assert_coefficient_direction(
    result: Dict[str, Any],
    variable: str,
    expected_sign: str,
) -> None:
    """Assert that a coefficient has the expected sign."""
    coef = result["coefficients"].loc[variable, "Coefficient"]

    if expected_sign == "positive":
        assert coef > 0, f"Coefficient {variable} should be positive, got {coef}"
    else:
        assert coef < 0, f"Coefficient {variable} should be negative, got {coef}"


# ==============================================================================
# Test Configuration
# ==============================================================================

DEFAULT_TEST_CONFIG = {
    "n_firms": 50,
    "n_years": 5,
    "seed": 42,
    "alpha": 0.05,
    "min_obs": 100,
}


def get_test_config(overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Get test configuration with optional overrides."""
    config = DEFAULT_TEST_CONFIG.copy()
    if overrides:
        config.update(overrides)
    return config


# ==============================================================================
# Export Symbols
# ==============================================================================

__all__ = [
    # Mock generators
    "create_mock_panel_ols_result",
    # Data generators
    "generate_panel_data",
    "generate_h1_data",
    "generate_h2_data",
    "generate_h3_data",
    "generate_h4_data",
    "generate_h5_data",
    "generate_ceo_data",
    # Hypothesis helpers
    "calculate_one_tailed_pvalue",
    "check_hypothesis_supported",
    # Assertions
    "assert_valid_regression_result",
    "assert_coefficient_significant",
    "assert_coefficient_direction",
    # Configuration
    "DEFAULT_TEST_CONFIG",
    "get_test_config",
]
