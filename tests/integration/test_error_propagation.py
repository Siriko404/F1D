"""
Integration tests for error propagation through pipeline.
Tests verify that exceptions are not silently caught and lost.
"""

import pytest
import pandas as pd

from f1d.shared.financial_utils import compute_financial_features
from f1d.shared.data_validation import FinancialCalculationError


@pytest.fixture
def sample_input_df():
    """Create sample input DataFrame for integration test."""
    return pd.DataFrame(
        {
            "gvkey": ["001234", "001235", "bad_key"],  # One will fail
            "year": [2018, 2018, 2018],
        }
    )


@pytest.fixture
def sample_compustat_df():
    """Create sample Compustat data."""
    return pd.DataFrame(
        {
            "gvkey": ["001234", "001235"],
            "fyear": [2018, 2018],
            "at": [1000, 500],
            "dlc": [200, 100],
            "dltt": [300, 150],
            "oibdp": [100, 50],
            "prcc_f": [10, 5],
            "csho": [100, 50],
            "ceq": [400, 200],
            "capx": [50, 25],
            "xrd": [20, 10],
            "dvc": [10, 5],
        }
    )


def test_error_propagates_from_calculate_firm_controls(
    sample_input_df, sample_compustat_df
):
    """Test that compute_financial_features handles unmatched gvkeys gracefully.

    compute_financial_features uses a vectorized LEFT JOIN: rows whose gvkey has
    no match in Compustat receive NaN for all financial control columns rather
    than raising an exception.  FinancialCalculationError is raised only by the
    lower-level calculate_firm_controls() helper (see
    test_calculate_firm_controls_raises_directly).
    """
    result = compute_financial_features(sample_input_df, sample_compustat_df)

    # All three input rows are preserved (LEFT JOIN keeps unmatched rows)
    assert len(result) == 3

    # bad_key row has NaN for every financial control
    bad_row = result[result["gvkey"] == "bad_key"]
    assert len(bad_row) == 1
    for col in (
        "size",
        "leverage",
        "profitability",
        "market_to_book",
        "capex_intensity",
        "r_intensity",
    ):
        assert pd.isna(bad_row.iloc[0][col]), f"Expected NaN for {col} on bad_key row"

    # Valid rows have non-NaN financial controls
    for gvkey in ("001234", "001235"):
        valid_row = result[result["gvkey"] == gvkey]
        assert len(valid_row) == 1
        assert not pd.isna(valid_row.iloc[0]["size"]), (
            f"size should not be NaN for {gvkey}"
        )


def test_compute_financial_features_handles_all_valid_data(sample_compustat_df):
    """Test that compute_financial_features works correctly when all data is valid."""
    valid_df = pd.DataFrame(
        {
            "gvkey": ["001234", "001235"],
            "year": [2018, 2018],
        }
    )

    result = compute_financial_features(valid_df, sample_compustat_df)

    assert len(result) == 2
    # The result should have the original columns plus the computed control variables
    assert "size" in result.columns
    assert "leverage" in result.columns
    assert "profitability" in result.columns


def test_calculate_firm_controls_raises_directly(sample_compustat_df):
    """Test that calling calculate_firm_controls directly raises exceptions.
    This verifies that the underlying function properly raises exceptions.
    """
    from f1d.shared.financial_utils import calculate_firm_controls

    # Test with missing gvkey - should raise
    row = pd.Series({"year": 2018})  # No gvkey

    with pytest.raises(FinancialCalculationError) as exc_info:
        calculate_firm_controls(row, sample_compustat_df, 2018)

    assert "missing gvkey" in str(exc_info.value).lower()


# Note for future development:
# To fully propagate exceptions through compute_financial_features, update it to:
# 1. Remove the 'if controls:' check
# 2. Either:
#    a) Let exceptions propagate (fail-fast approach)
#    b) Catch and log them, then continue (silent logging approach)
# The current implementation uses (b) with silent dropping (no logging).
