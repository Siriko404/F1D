"""
Test utilities for F1D econometric analysis testing.

This package provides reusable utilities for testing regression scripts
across all hypothesis tests (H1-H9) and CEO fixed effects analysis.
"""

from .regression_test_harness import (
    create_mock_panel_ols_result,
    generate_panel_data,
    generate_h1_data,
    generate_h2_data,
    generate_h3_data,
    generate_h4_data,
    generate_h5_data,
    generate_ceo_data,
    calculate_one_tailed_pvalue,
    check_hypothesis_supported,
    assert_valid_regression_result,
    assert_coefficient_significant,
    assert_coefficient_direction,
    DEFAULT_TEST_CONFIG,
    get_test_config,
)

__all__ = [
    "create_mock_panel_ols_result",
    "generate_panel_data",
    "generate_h1_data",
    "generate_h2_data",
    "generate_h3_data",
    "generate_h4_data",
    "generate_h5_data",
    "generate_ceo_data",
    "calculate_one_tailed_pvalue",
    "check_hypothesis_supported",
    "assert_valid_regression_result",
    "assert_coefficient_significant",
    "assert_coefficient_direction",
    "DEFAULT_TEST_CONFIG",
    "get_test_config",
]
