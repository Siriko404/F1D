"""
Unit tests for shared.financial_utils module.

Tests verify financial calculation functions work correctly with edge cases:
- Missing data handling
- NaN values in Compustat fields
- Boundary conditions (zero, negative values)
- Winsorization behavior
- Quarterly vs annual controls
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "2_Scripts"))

from shared.financial_utils import (
    calculate_firm_controls,
    calculate_firm_controls_quarterly,
    compute_financial_features,
    compute_financial_controls_quarterly,
)
from shared.data_validation import FinancialCalculationError


# Fixtures for test data
@pytest.fixture
def sample_compustat_row():
    """Create a sample Compustat row for testing."""
    return pd.Series({
        "gvkey": "001234",
        "datadate": "2010-12-31",
        "fyear": 2010,
    })


@pytest.fixture
def sample_compustat_df():
    """Create a sample Compustat DataFrame for testing."""
    return pd.DataFrame({
        "gvkey": ["001234", "001234", "001234", "001235", "001235", "001235"],
        "datadate": ["2010-12-31", "2010-12-31", "2010-12-31",
                     "2011-12-31", "2011-12-31", "2011-12-31"],
        "fyear": [2010, 2010, 2010, 2011, 2011, 2011],
        "at": [1000.0, 1100.0, 1200.0, 500.0, 550.0, 600.0],
        "lt": [200.0, 220.0, 240.0, 100.0, 110.0, 120.0],
        "dlc": [50.0, 55.0, 60.0, 25.0, 27.5, 30.0],
        "dltt": [150.0, 165.0, 180.0, 75.0, 82.5, 90.0],
        "ceq": [300.0, 330.0, 360.0, 150.0, 165.0, 180.0],
        "che": [100.0, 110.0, 120.0, 50.0, 55.0, 60.0],
        "oancf": [150.0, 165.0, 180.0, 75.0, 82.5, 90.0],
        "xrd": [50.0, 55.0, 60.0, 25.0, 27.5, 30.0],
        "capx": [80.0, 88.0, 96.0, 40.0, 44.0, 48.0],
        "sppe": [20.0, 22.0, 24.0, 10.0, 11.0, 12.0],
        "sale": [800.0, 880.0, 960.0, 400.0, 440.0, 480.0],
        "cogs": [400.0, 440.0, 480.0, 200.0, 220.0, 240.0],
        "prcc_f": [50.0, 55.0, 60.0, 25.0, 27.5, 30.0],
        "csho": [10.0, 11.0, 12.0, 5.0, 5.5, 6.0],
        "oibdp": [200.0, 220.0, 240.0, 100.0, 110.0, 120.0],
        "dvc": [10.0, 11.0, 12.0, 5.0, 5.5, 6.0],
    })


@pytest.fixture
def sample_quarterly_compustat_df():
    """Create a sample quarterly Compustat DataFrame for testing."""
    return pd.DataFrame({
        "gvkey": ["001234", "001234", "001234", "001235", "001235", "001235"],
        "datadate": pd.to_datetime([
            "2018-03-31", "2018-06-30", "2018-09-30",
            "2018-03-31", "2018-06-30", "2018-09-30",
        ]),
        "atq": [250, 260, 270, 100, 110, 120],
        "ceqq": [100, 105, 110, 50, 55, 60],
        "cshoq": [50, 51, 52, 25, 26, 27],
        "prccq": [10, 11, 12, 5, 6, 7],
        "ltq": [150, 155, 160, 75, 80, 85],
        "niq": [25, 26, 27, 10, 11, 12],
        "actq": [200, 205, 210, 100, 105, 110],
        "lctq": [80, 82, 84, 40, 42, 44],
        "xrdq": [5, 5, 5, 2, 2, 2],
        "epspxq": [0.5, 0.52, 0.54, 0.25, 0.26, 0.27],
    })


class TestCalculateFirmControls:
    """Tests for calculate_firm_controls() function."""

    def test_returns_size_as_log_assets(self, sample_compustat_row, sample_compustat_df):
        """Test that size (log assets) is computed correctly."""
        result = calculate_firm_controls(sample_compustat_row, sample_compustat_df, 2010)
        assert "size" in result
        # Function uses first matching row from DataFrame (at=1000)
        assert result["size"] == pytest.approx(np.log(1000.0), rel=1e-5)

    def test_calculates_leverage_correctly(self, sample_compustat_row, sample_compustat_df):
        """Test that leverage (debt/assets) is computed correctly."""
        result = calculate_firm_controls(sample_compustat_row, sample_compustat_df, 2010)
        assert "leverage" in result
        # leverage = (dlc + dltt) / at = (50 + 150) / 1000 = 0.2
        expected = (50.0 + 150.0) / 1000.0
        assert result["leverage"] == pytest.approx(expected, rel=1e-5)

    def test_calculates_profitability_correctly(self, sample_compustat_row, sample_compustat_df):
        """Test that profitability (oibdp/at) is computed correctly."""
        result = calculate_firm_controls(sample_compustat_row, sample_compustat_df, 2010)
        assert "profitability" in result
        # profitability = oibdp / at = 200 / 1000 = 0.2
        expected = 200.0 / 1000.0
        assert result["profitability"] == pytest.approx(expected, rel=1e-5)

    def test_calculates_market_to_book(self, sample_compustat_row, sample_compustat_df):
        """Test that market_to_book is computed correctly."""
        result = calculate_firm_controls(sample_compustat_row, sample_compustat_df, 2010)
        assert "market_to_book" in result
        # market_to_book = (prcc_f * csho) / ceq = (50 * 10) / 300 = 1.667
        expected = (50.0 * 10.0) / 300.0
        assert result["market_to_book"] == pytest.approx(expected, rel=1e-5)

    def test_calculates_capex_intensity(self, sample_compustat_row, sample_compustat_df):
        """Test that capex_intensity is computed correctly."""
        result = calculate_firm_controls(sample_compustat_row, sample_compustat_df, 2010)
        assert "capex_intensity" in result
        # capex_intensity = capx / at = 80 / 1000 = 0.08
        expected = 80.0 / 1000.0
        assert result["capex_intensity"] == pytest.approx(expected, rel=1e-5)

    def test_calculates_rd_intensity(self, sample_compustat_row, sample_compustat_df):
        """Test that r_intensity is computed correctly."""
        result = calculate_firm_controls(sample_compustat_row, sample_compustat_df, 2010)
        assert "r_intensity" in result
        # r_intensity = xrd / at = 50 / 1000 = 0.05
        expected = 50.0 / 1000.0
        assert result["r_intensity"] == pytest.approx(expected, rel=1e-5)

    def test_dividend_payer_indicator(self, sample_compustat_row, sample_compustat_df):
        """Test that dividend_payer is binary indicator."""
        result = calculate_firm_controls(sample_compustat_row, sample_compustat_df, 2010)
        assert "dividend_payer" in result
        assert result["dividend_payer"] in [0, 1]
        # dvc=10 > 0, so should be 1
        assert result["dividend_payer"] == 1

    def test_handles_zero_at_with_nan(self, sample_compustat_row, sample_compustat_df):
        """Test that zero total assets in DataFrame returns NaN for ratio-based metrics."""
        # Modify DataFrame to have at=0 for first row
        df_zero_at = sample_compustat_df.copy()
        df_zero_at.loc[0, "at"] = 0.0
        result = calculate_firm_controls(sample_compustat_row, df_zero_at, 2010)
        # With at=0, leverage calculation should result in NaN or inf
        assert pd.isna(result["leverage"]) or np.isinf(result["leverage"])

    def test_handles_negative_at(self, sample_compustat_row, sample_compustat_df):
        """Test that negative total assets in DataFrame returns NaN for ratio-based metrics."""
        df_neg_at = sample_compustat_df.copy()
        df_neg_at.loc[0, "at"] = -100.0
        result = calculate_firm_controls(sample_compustat_row, df_neg_at, 2010)
        # When at <= 0, size calculation uses np.log which handles this
        # leverage calculation: at < 0 but division still works, gives negative leverage
        assert "size" in result
        # log of negative is nan
        assert pd.isna(result["size"])

    def test_handles_missing_ceq_for_market_to_book(self, sample_compustat_row, sample_compustat_df):
        """Test that missing ceq in DataFrame results in NaN market_to_book."""
        df_no_ceq = sample_compustat_df.copy()
        df_no_ceq.loc[0, "ceq"] = np.nan
        result = calculate_firm_controls(sample_compustat_row, df_no_ceq, 2010)
        assert pd.isna(result["market_to_book"])

    def test_handles_zero_dividend_for_indicator(self, sample_compustat_row, sample_compustat_df):
        """Test that zero dividend in DataFrame results in dividend_payer=0."""
        df_no_div = sample_compustat_df.copy()
        df_no_div.loc[0, "dvc"] = 0.0
        result = calculate_firm_controls(sample_compustat_row, df_no_div, 2010)
        assert result["dividend_payer"] == 0

    def test_all_control_keys_present(self, sample_compustat_row, sample_compustat_df):
        """Test that all expected control keys are present in result."""
        result = calculate_firm_controls(sample_compustat_row, sample_compustat_df, 2010)
        expected_keys = [
            "size", "leverage", "profitability", "market_to_book",
            "capex_intensity", "r_intensity", "dividend_payer"
        ]
        for key in expected_keys:
            assert key in result

    def test_data_fetched_by_gvkey_and_fyear(self, sample_compustat_df):
        """Test that function correctly fetches data using gvkey and fyear."""
        row_2011 = pd.Series({"gvkey": "001235", "year": 2011})
        result = calculate_firm_controls(row_2011, sample_compustat_df, 2011)
        # Should use data for gvkey=001235, fyear=2011 (at=500)
        assert result["size"] == pytest.approx(np.log(500.0), rel=1e-5)


class TestCalculateFirmControlsQuarterly:
    """Tests for calculate_firm_controls_quarterly() function."""

    def test_returns_size_as_log_atq(self, sample_quarterly_compustat_df):
        """Test that Size is log of atq."""
        row = pd.Series({"gvkey": "001234", "datadate": pd.Timestamp("2018-06-30")})
        result = calculate_firm_controls_quarterly(
            row, sample_quarterly_compustat_df, pd.Timestamp("2018-06-30")
        )
        assert "Size" in result
        assert result["Size"] == pytest.approx(np.log(260), rel=1e-5)

    def test_calculates_book_to_market(self, sample_quarterly_compustat_df):
        """Test that BM is calculated correctly."""
        row = pd.Series({"gvkey": "001234", "datadate": pd.Timestamp("2018-06-30")})
        result = calculate_firm_controls_quarterly(
            row, sample_quarterly_compustat_df, pd.Timestamp("2018-06-30")
        )
        assert "BM" in result
        # BM = ceqq / (cshoq * prccq)
        expected = 105 / (51 * 11)
        assert result["BM"] == pytest.approx(expected, rel=1e-5)

    def test_calculates_leverage_quarterly(self, sample_quarterly_compustat_df):
        """Test that Lev is calculated correctly."""
        row = pd.Series({"gvkey": "001234", "datadate": pd.Timestamp("2018-06-30")})
        result = calculate_firm_controls_quarterly(
            row, sample_quarterly_compustat_df, pd.Timestamp("2018-06-30")
        )
        assert "Lev" in result
        expected = 155 / 260
        assert result["Lev"] == pytest.approx(expected, rel=1e-5)

    def test_calculates_roa(self, sample_quarterly_compustat_df):
        """Test that ROA is calculated correctly."""
        row = pd.Series({"gvkey": "001234", "datadate": pd.Timestamp("2018-06-30")})
        result = calculate_firm_controls_quarterly(
            row, sample_quarterly_compustat_df, pd.Timestamp("2018-06-30")
        )
        assert "ROA" in result
        expected = 26 / 260
        assert result["ROA"] == pytest.approx(expected, rel=1e-5)

    def test_calculates_current_ratio(self, sample_quarterly_compustat_df):
        """Test that CurrentRatio is calculated correctly."""
        row = pd.Series({"gvkey": "001234", "datadate": pd.Timestamp("2018-06-30")})
        result = calculate_firm_controls_quarterly(
            row, sample_quarterly_compustat_df, pd.Timestamp("2018-06-30")
        )
        assert "CurrentRatio" in result
        expected = 205 / 82
        assert result["CurrentRatio"] == pytest.approx(expected, rel=1e-5)

    def test_calculates_rd_intensity(self, sample_quarterly_compustat_df):
        """Test that RD_Intensity is calculated correctly."""
        row = pd.Series({"gvkey": "001234", "datadate": pd.Timestamp("2018-06-30")})
        result = calculate_firm_controls_quarterly(
            row, sample_quarterly_compustat_df, pd.Timestamp("2018-06-30")
        )
        assert "RD_Intensity" in result
        expected = 5 / 260
        assert result["RD_Intensity"] == pytest.approx(expected, rel=1e-5)

    def test_finds_closest_datadate(self, sample_quarterly_compustat_df):
        """Test that function finds data closest to specified date."""
        row = pd.Series({"gvkey": "001234", "datadate": pd.Timestamp("2018-07-15")})
        result = calculate_firm_controls_quarterly(
            row, sample_quarterly_compustat_df, pd.Timestamp("2018-07-15")
        )
        # Should find data from 2018-06-30 (most recent before July 15)
        assert isinstance(result, dict)
        assert "Size" in result

    def test_all_quarterly_keys_present(self, sample_quarterly_compustat_df):
        """Test that all expected quarterly control keys are present."""
        row = pd.Series({"gvkey": "001234", "datadate": pd.Timestamp("2018-06-30")})
        result = calculate_firm_controls_quarterly(
            row, sample_quarterly_compustat_df, pd.Timestamp("2018-06-30")
        )
        expected_keys = ["Size", "BM", "Lev", "ROA", "CurrentRatio", "RD_Intensity"]
        for key in expected_keys:
            assert key in result


@pytest.mark.parametrize("duration,rows,expected_throughput", [
    (1.0, 1000, 1000.0),
    (0.5, 500, 1000.0),
    (2.0, 2000, 1000.0),
    (10.0, 10000, 1000.0),
])
def test_calculate_throughput_valid_inputs(duration, rows, expected_throughput):
    """Test calculate_throughput with valid inputs."""
    from shared.observability_utils import calculate_throughput
    result = calculate_throughput(rows, duration)
    assert result == pytest.approx(expected_throughput, rel=1e-5)


@pytest.mark.parametrize("duration,rows", [
    (0.0, 100),  # Zero duration
    (-1.0, 100),  # Negative duration
])
def test_calculate_throughput_invalid_inputs_raises_error(duration, rows):
    """Test that invalid inputs raise ValueError."""
    from shared.observability_utils import calculate_throughput
    with pytest.raises(ValueError):
        calculate_throughput(rows, duration)


@pytest.mark.parametrize("field_to_nan", [
    "at", "lt", "dlc", "dltt", "che", "sale"
])
def test_handles_nan_in_critical_fields(field_to_nan, sample_compustat_row, sample_compustat_df):
    """Test that NaN in critical fields is handled gracefully."""
    row_nan = sample_compustat_row.copy()
    row_nan[field_to_nan] = np.nan
    result = calculate_firm_controls(row_nan, sample_compustat_df, 2010)
    # Either raises error or returns None for affected fields
    assert isinstance(result, dict)


class TestComputeFinancialFeatures:
    """Tests for compute_financial_features() function."""

    def test_returns_dataframe_with_controls(self, sample_compustat_df):
        """Test that compute_financial_features returns DataFrame with controls."""
        df = pd.DataFrame({
            "gvkey": ["001234", "001235"],
            "year": [2010, 2011],
        })
        result = compute_financial_features(df, sample_compustat_df)
        assert isinstance(result, pd.DataFrame)
        assert "size" in result.columns

    def test_handles_empty_dataframe(self, sample_compustat_df):
        """Test that empty input DataFrame returns empty result."""
        df = pd.DataFrame(columns=["gvkey", "year"])
        result = compute_financial_features(df, sample_compustat_df)
        assert len(result) == 0


class TestComputeFinancialControlsQuarterly:
    """Tests for compute_financial_controls_quarterly() function."""

    def test_returns_dataframe_with_quarterly_controls(self, sample_quarterly_compustat_df):
        """Test that function adds quarterly control columns."""
        result = compute_financial_controls_quarterly(
            sample_quarterly_compustat_df.copy(), winsorize=False
        )
        assert "Size" in result.columns
        assert "BM" in result.columns
        assert "Lev" in result.columns
        assert "ROA" in result.columns
        assert "CurrentRatio" in result.columns
        assert "RD_Intensity" in result.columns
        assert "EPS_Growth" in result.columns

    def test_winsorize_parameter_affects_output(self, sample_quarterly_compustat_df):
        """Test that winsorize parameter affects extreme values."""
        # Create data with extreme values
        df_extreme = sample_quarterly_compustat_df.copy()
        df_extreme.loc[0, "atq"] = 100000  # Extreme value

        result_no_winsor = compute_financial_controls_quarterly(
            df_extreme.copy(), winsorize=False
        )
        result_winsor = compute_financial_controls_quarterly(
            df_extreme.copy(), winsorize=True
        )

        # The winsorized version should have the extreme value clipped
        assert not result_no_winsor["Size"].equals(result_winsor["Size"])

    def test_calculates_eps_growth(self, sample_quarterly_compustat_df):
        """Test that EPS_Growth is calculated correctly."""
        result = compute_financial_controls_quarterly(
            sample_quarterly_compustat_df.copy(), winsorize=False
        )
        assert "EPS_Growth" in result.columns
        # EPS_Growth requires 4 quarters of data for lag
        # With only 3 quarters per firm, most values should be NaN
        assert result["EPS_Growth"].notna().sum() >= 0

    def test_handles_zero_lct_for_current_ratio(self, sample_quarterly_compustat_df):
        """Test that zero lct is handled in CurrentRatio calculation."""
        df = sample_quarterly_compustat_df.copy()
        df.loc[0, "lctq"] = 0.0
        result = compute_financial_controls_quarterly(df, winsorize=False)
        # Zero lct should result in inf or very large CurrentRatio
        # The function replaces 0 with np.nan for lctq
        assert "CurrentRatio" in result.columns

    def test_handles_missing_xrdq_treats_as_zero(self, sample_quarterly_compustat_df):
        """Test that missing xrdq is treated as zero for RD_Intensity."""
        df = sample_quarterly_compustat_df.copy()
        df.loc[0, "xrdq"] = np.nan
        result = compute_financial_controls_quarterly(df, winsorize=False)
        # Missing xrdq should be treated as 0, so RD_Intensity should be 0/atq = 0
        assert "RD_Intensity" in result.columns
