"""
Unit tests for financial_utils exception behavior.
Tests verify that FinancialCalculationError is raised with informative messages.
"""

import pytest
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "2_Scripts"))
from shared.financial_utils import calculate_firm_controls, calculate_firm_controls_quarterly
from shared.data_validation import FinancialCalculationError


@pytest.fixture
def sample_compustat_df():
    """Create sample Compustat data for testing."""
    return pd.DataFrame({
        "gvkey": ["001234", "001234", "005678"],
        "fyear": [2017, 2018, 2018],
        "at": [1000, 1100, 500],
        "dlc": [200, 220, 100],
        "dltt": [300, 330, 150],
        "oibdp": [100, 110, 50],
        "prcc_f": [10, 11, 5],
        "csho": [100, 110, 50],
        "ceq": [400, 440, 200],
        "capx": [50, 55, 25],
        "xrd": [20, 22, 10],
        "dvc": [10, 11, 5],
    })


@pytest.fixture
def sample_compustat_quarterly_df():
    """Create sample quarterly Compustat data for testing."""
    return pd.DataFrame({
        "gvkey": ["001234", "001234", "001234"],
        "datadate": pd.to_datetime(["2018-03-31", "2018-06-30", "2018-09-30"]),
        "atq": [250, 260, 270],
        "ceqq": [100, 105, 110],
        "cshoq": [50, 51, 52],
        "prccq": [10, 11, 12],
        "ltq": [150, 155, 160],
        "niq": [25, 26, 27],
        "actq": [200, 205, 210],
        "lctq": [80, 82, 84],
        "xrdq": [5, 5, 5],
        "epspxq": [0.5, 0.52, 0.54],
    })


def test_missing_gvkey_raises_exception(sample_compustat_df):
    """Test that missing gvkey raises FinancialCalculationError."""
    row = pd.Series({"year": 2018})  # No gvkey

    with pytest.raises(FinancialCalculationError) as exc_info:
        calculate_firm_controls(row, sample_compustat_df, 2018)

    error_msg = str(exc_info.value)
    assert "missing gvkey" in error_msg.lower()
    assert "2018" in error_msg  # Check that year is in message (case-insensitive)


def test_missing_data_for_year_raises_exception(sample_compustat_df):
    """Test that missing Compustat data for year raises FinancialCalculationError."""
    row = pd.Series({"gvkey": "999999", "year": 2018})  # gvkey not in data

    with pytest.raises(FinancialCalculationError) as exc_info:
        calculate_firm_controls(row, sample_compustat_df, 2018)

    error_msg = str(exc_info.value)
    assert "no compustat data found" in error_msg.lower()
    assert "gvkey=999999" in error_msg or "gvkey = 999999" in error_msg.lower()
    assert "year=2018" in error_msg


def test_valid_data_returns_controls(sample_compustat_df):
    """Test that valid data returns control variables without error."""
    row = pd.Series({"gvkey": "001234", "year": 2018})

    result = calculate_firm_controls(row, sample_compustat_df, 2018)

    assert isinstance(result, dict)
    assert "size" in result
    assert "leverage" in result
    assert "profitability" in result
    assert result["size"] > 0  # log(1100) > 0


def test_quarterly_missing_gvkey_raises_exception(sample_compustat_quarterly_df):
    """Test that missing gvkey raises exception in quarterly function."""
    row = pd.Series({"datadate": pd.Timestamp("2018-06-30")})  # No gvkey

    with pytest.raises(FinancialCalculationError) as exc_info:
        calculate_firm_controls_quarterly(row, sample_compustat_quarterly_df, pd.Timestamp("2018-06-30"))

    error_msg = str(exc_info.value)
    assert "missing gvkey" in error_msg.lower()


def test_quarterly_valid_data_returns_controls(sample_compustat_quarterly_df):
    """Test that valid data returns quarterly controls without error."""
    row = pd.Series({"gvkey": "001234", "datadate": pd.Timestamp("2018-06-30")})

    result = calculate_firm_controls_quarterly(row, sample_compustat_quarterly_df, pd.Timestamp("2018-06-30"))

    assert isinstance(result, dict)
    assert "Size" in result
    assert "BM" in result
    assert "Lev" in result
    assert result["Size"] > 0  # log(260) > 0
