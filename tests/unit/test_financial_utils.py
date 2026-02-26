"""
Unit tests for f1d.shared.financial_utils module.

Tests verify financial calculation functions work correctly with edge cases:
- Missing data handling
- NaN values in Compustat fields
- Boundary conditions (zero, negative values)
- Winsorization behavior
- Quarterly vs annual controls

Uses factory fixtures from tests/factories/financial.py for test data generation.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from f1d.shared.financial_utils import (
    calculate_firm_controls,
    calculate_firm_controls_quarterly,
    compute_financial_features,
    compute_financial_controls_quarterly,
)
from f1d.shared.data_validation import FinancialCalculationError


class TestCalculateFirmControls:
    """Tests for calculate_firm_controls() function."""

    def test_returns_size_as_log_assets(self, sample_compustat_factory):
        """Test that size (log assets) is computed correctly."""
        compustat_df = sample_compustat_factory(n_firms=1, n_years=1, seed=42)
        # Add required columns for calculate_firm_controls
        compustat_df["dlc"] = compustat_df["dlc"]
        compustat_df["dltt"] = compustat_df["dltt"]
        compustat_df["ceq"] = compustat_df["at"] * 0.3
        compustat_df["prcc_f"] = 50.0
        compustat_df["csho"] = 10.0
        compustat_df["oibdp"] = compustat_df["at"] * 0.2
        compustat_df["dvc"] = 10.0
        compustat_df["capx"] = compustat_df["at"] * 0.08
        compustat_df["xrd"] = compustat_df["at"] * 0.05

        row = pd.Series({"gvkey": "000000", "datadate": "2000-12-31"})
        result = calculate_firm_controls(row, compustat_df, 2000)
        assert "size" in result
        # Should use first matching row
        assert result["size"] == pytest.approx(np.log(compustat_df.iloc[0]["at"]), rel=1e-5)

    def test_calculates_leverage_correctly(self, sample_compustat_factory):
        """Test that leverage (debt/assets) is computed correctly."""
        compustat_df = sample_compustat_factory(n_firms=1, n_years=1, seed=42)
        compustat_df["ceq"] = compustat_df["at"] * 0.3
        compustat_df["prcc_f"] = 50.0
        compustat_df["csho"] = 10.0
        compustat_df["oibdp"] = compustat_df["at"] * 0.2
        compustat_df["dvc"] = 10.0
        compustat_df["capx"] = compustat_df["at"] * 0.08
        compustat_df["xrd"] = compustat_df["at"] * 0.05

        row = pd.Series({"gvkey": "000000", "datadate": "2000-12-31"})
        result = calculate_firm_controls(row, compustat_df, 2000)
        assert "leverage" in result
        # leverage = (dlc + dltt) / at
        expected = (compustat_df.iloc[0]["dlc"] + compustat_df.iloc[0]["dltt"]) / compustat_df.iloc[0]["at"]
        assert result["leverage"] == pytest.approx(expected, rel=1e-5)

    def test_calculates_profitability_correctly(self, sample_compustat_factory):
        """Test that profitability (oibdp/at) is computed correctly."""
        compustat_df = sample_compustat_factory(n_firms=1, n_years=1, seed=42)
        compustat_df["ceq"] = compustat_df["at"] * 0.3
        compustat_df["prcc_f"] = 50.0
        compustat_df["csho"] = 10.0
        compustat_df["oibdp"] = compustat_df["at"] * 0.2
        compustat_df["dvc"] = 10.0
        compustat_df["capx"] = compustat_df["at"] * 0.08
        compustat_df["xrd"] = compustat_df["at"] * 0.05

        row = pd.Series({"gvkey": "000000", "datadate": "2000-12-31"})
        result = calculate_firm_controls(row, compustat_df, 2000)
        assert "profitability" in result
        expected = compustat_df.iloc[0]["oibdp"] / compustat_df.iloc[0]["at"]
        assert result["profitability"] == pytest.approx(expected, rel=1e-5)

    def test_calculates_market_to_book(self, sample_compustat_factory):
        """Test that market_to_book is computed correctly."""
        compustat_df = sample_compustat_factory(n_firms=1, n_years=1, seed=42)
        compustat_df["ceq"] = compustat_df["at"] * 0.3
        compustat_df["prcc_f"] = 50.0
        compustat_df["csho"] = 10.0
        compustat_df["oibdp"] = compustat_df["at"] * 0.2
        compustat_df["dvc"] = 10.0
        compustat_df["capx"] = compustat_df["at"] * 0.08
        compustat_df["xrd"] = compustat_df["at"] * 0.05

        row = pd.Series({"gvkey": "000000", "datadate": "2000-12-31"})
        result = calculate_firm_controls(row, compustat_df, 2000)
        assert "market_to_book" in result
        # market_to_book = (prcc_f * csho) / ceq
        expected = (50.0 * 10.0) / compustat_df.iloc[0]["ceq"]
        assert result["market_to_book"] == pytest.approx(expected, rel=1e-5)

    def test_calculates_capex_intensity(self, sample_compustat_factory):
        """Test that capex_intensity is computed correctly."""
        compustat_df = sample_compustat_factory(n_firms=1, n_years=1, seed=42)
        compustat_df["ceq"] = compustat_df["at"] * 0.3
        compustat_df["prcc_f"] = 50.0
        compustat_df["csho"] = 10.0
        compustat_df["oibdp"] = compustat_df["at"] * 0.2
        compustat_df["dvc"] = 10.0
        compustat_df["capx"] = compustat_df["at"] * 0.08
        compustat_df["xrd"] = compustat_df["at"] * 0.05

        row = pd.Series({"gvkey": "000000", "datadate": "2000-12-31"})
        result = calculate_firm_controls(row, compustat_df, 2000)
        assert "capex_intensity" in result
        expected = compustat_df.iloc[0]["capx"] / compustat_df.iloc[0]["at"]
        assert result["capex_intensity"] == pytest.approx(expected, rel=1e-5)

    def test_calculates_rd_intensity(self, sample_compustat_factory):
        """Test that r_intensity is computed correctly."""
        compustat_df = sample_compustat_factory(n_firms=1, n_years=1, seed=42)
        compustat_df["ceq"] = compustat_df["at"] * 0.3
        compustat_df["prcc_f"] = 50.0
        compustat_df["csho"] = 10.0
        compustat_df["oibdp"] = compustat_df["at"] * 0.2
        compustat_df["dvc"] = 10.0
        compustat_df["capx"] = compustat_df["at"] * 0.08
        compustat_df["xrd"] = compustat_df["at"] * 0.05

        row = pd.Series({"gvkey": "000000", "datadate": "2000-12-31"})
        result = calculate_firm_controls(row, compustat_df, 2000)
        assert "r_intensity" in result
        expected = compustat_df.iloc[0]["xrd"] / compustat_df.iloc[0]["at"]
        assert result["r_intensity"] == pytest.approx(expected, rel=1e-5)

    def test_dividend_payer_indicator_positive(self, sample_compustat_factory):
        """Test that dividend_payer is 1 when dvc > 0."""
        compustat_df = sample_compustat_factory(n_firms=1, n_years=1, seed=42)
        compustat_df["ceq"] = compustat_df["at"] * 0.3
        compustat_df["prcc_f"] = 50.0
        compustat_df["csho"] = 10.0
        compustat_df["oibdp"] = compustat_df["at"] * 0.2
        compustat_df["dvc"] = 10.0
        compustat_df["capx"] = compustat_df["at"] * 0.08
        compustat_df["xrd"] = compustat_df["at"] * 0.05

        row = pd.Series({"gvkey": "000000", "datadate": "2000-12-31"})
        result = calculate_firm_controls(row, compustat_df, 2000)
        assert "dividend_payer" in result
        assert result["dividend_payer"] in [0, 1]
        assert result["dividend_payer"] == 1  # dvc > 0

    def test_dividend_payer_indicator_zero(self, sample_compustat_factory):
        """Test that dividend_payer is 0 when dvc = 0."""
        compustat_df = sample_compustat_factory(n_firms=1, n_years=1, seed=42)
        compustat_df["ceq"] = compustat_df["at"] * 0.3
        compustat_df["prcc_f"] = 50.0
        compustat_df["csho"] = 10.0
        compustat_df["oibdp"] = compustat_df["at"] * 0.2
        compustat_df["dvc"] = 0.0
        compustat_df["capx"] = compustat_df["at"] * 0.08
        compustat_df["xrd"] = compustat_df["at"] * 0.05

        row = pd.Series({"gvkey": "000000", "datadate": "2000-12-31"})
        result = calculate_firm_controls(row, compustat_df, 2000)
        assert result["dividend_payer"] == 0

    def test_handles_zero_at_returns_nan(self, sample_compustat_factory):
        """Test that zero total assets returns NaN for ratio-based metrics."""
        compustat_df = sample_compustat_factory(n_firms=1, n_years=1, seed=42)
        compustat_df.loc[0, "at"] = 0.0
        compustat_df["ceq"] = compustat_df["at"] * 0.3
        compustat_df["prcc_f"] = 50.0
        compustat_df["csho"] = 10.0
        compustat_df["oibdp"] = compustat_df["at"] * 0.2
        compustat_df["dvc"] = 10.0
        compustat_df["capx"] = compustat_df["at"] * 0.08
        compustat_df["xrd"] = compustat_df["at"] * 0.05

        row = pd.Series({"gvkey": "000000", "datadate": "2000-12-31"})
        result = calculate_firm_controls(row, compustat_df, 2000)
        # With at=0, leverage calculation should result in NaN
        assert pd.isna(result["size"])
        assert pd.isna(result["leverage"])

    def test_handles_negative_at_returns_nan(self, sample_compustat_factory):
        """Test that negative total assets returns NaN for size (log)."""
        compustat_df = sample_compustat_factory(n_firms=1, n_years=1, seed=42)
        compustat_df.loc[0, "at"] = -100.0
        compustat_df["ceq"] = 300.0
        compustat_df["prcc_f"] = 50.0
        compustat_df["csho"] = 10.0
        compustat_df["oibdp"] = 200.0
        compustat_df["dvc"] = 10.0
        compustat_df["capx"] = 80.0
        compustat_df["xrd"] = 50.0

        row = pd.Series({"gvkey": "000000", "datadate": "2000-12-31"})
        result = calculate_firm_controls(row, compustat_df, 2000)
        # log of negative is nan
        assert pd.isna(result["size"])

    def test_handles_missing_ceq_returns_nan(self, sample_compustat_factory):
        """Test that missing ceq results in NaN market_to_book."""
        compustat_df = sample_compustat_factory(n_firms=1, n_years=1, seed=42)
        compustat_df["ceq"] = np.nan
        compustat_df["prcc_f"] = 50.0
        compustat_df["csho"] = 10.0
        compustat_df["oibdp"] = compustat_df["at"] * 0.2
        compustat_df["dvc"] = 10.0
        compustat_df["capx"] = compustat_df["at"] * 0.08
        compustat_df["xrd"] = compustat_df["at"] * 0.05

        row = pd.Series({"gvkey": "000000", "datadate": "2000-12-31"})
        result = calculate_firm_controls(row, compustat_df, 2000)
        assert pd.isna(result["market_to_book"])

    def test_handles_missing_prcc_f_returns_nan(self, sample_compustat_factory):
        """Test that missing prcc_f results in NaN market_to_book."""
        compustat_df = sample_compustat_factory(n_firms=1, n_years=1, seed=42)
        compustat_df["ceq"] = 300.0
        compustat_df["prcc_f"] = np.nan
        compustat_df["csho"] = 10.0
        compustat_df["oibdp"] = compustat_df["at"] * 0.2
        compustat_df["dvc"] = 10.0
        compustat_df["capx"] = compustat_df["at"] * 0.08
        compustat_df["xrd"] = compustat_df["at"] * 0.05

        row = pd.Series({"gvkey": "000000", "datadate": "2000-12-31"})
        result = calculate_firm_controls(row, compustat_df, 2000)
        assert pd.isna(result["market_to_book"])

    def test_handles_missing_csho_returns_nan(self, sample_compustat_factory):
        """Test that missing csho results in NaN market_to_book."""
        compustat_df = sample_compustat_factory(n_firms=1, n_years=1, seed=42)
        compustat_df["ceq"] = 300.0
        compustat_df["prcc_f"] = 50.0
        compustat_df["csho"] = np.nan
        compustat_df["oibdp"] = compustat_df["at"] * 0.2
        compustat_df["dvc"] = 10.0
        compustat_df["capx"] = compustat_df["at"] * 0.08
        compustat_df["xrd"] = compustat_df["at"] * 0.05

        row = pd.Series({"gvkey": "000000", "datadate": "2000-12-31"})
        result = calculate_firm_controls(row, compustat_df, 2000)
        assert pd.isna(result["market_to_book"])

    def test_all_control_keys_present(self, sample_compustat_factory):
        """Test that all expected control keys are present in result."""
        compustat_df = sample_compustat_factory(n_firms=1, n_years=1, seed=42)
        compustat_df["ceq"] = compustat_df["at"] * 0.3
        compustat_df["prcc_f"] = 50.0
        compustat_df["csho"] = 10.0
        compustat_df["oibdp"] = compustat_df["at"] * 0.2
        compustat_df["dvc"] = 10.0
        compustat_df["capx"] = compustat_df["at"] * 0.08
        compustat_df["xrd"] = compustat_df["at"] * 0.05

        row = pd.Series({"gvkey": "000000", "datadate": "2000-12-31"})
        result = calculate_firm_controls(row, compustat_df, 2000)
        expected_keys = [
            "size", "leverage", "profitability", "market_to_book",
            "capex_intensity", "r_intensity", "dividend_payer"
        ]
        for key in expected_keys:
            assert key in result, f"Missing key: {key}"

    def test_raises_error_on_missing_gvkey(self, sample_compustat_factory):
        """Test that missing gvkey raises FinancialCalculationError."""
        compustat_df = sample_compustat_factory(n_firms=1, n_years=1, seed=42)
        compustat_df["ceq"] = compustat_df["at"] * 0.3
        compustat_df["prcc_f"] = 50.0
        compustat_df["csho"] = 10.0
        compustat_df["oibdp"] = compustat_df["at"] * 0.2
        compustat_df["dvc"] = 10.0
        compustat_df["capx"] = compustat_df["at"] * 0.08
        compustat_df["xrd"] = compustat_df["at"] * 0.05

        row = pd.Series({"datadate": "2000-12-31"})  # Missing gvkey
        with pytest.raises(FinancialCalculationError, match="missing gvkey"):
            calculate_firm_controls(row, compustat_df, 2000)

    def test_raises_error_on_gvkey_none(self, sample_compustat_factory):
        """Test that None gvkey raises FinancialCalculationError."""
        compustat_df = sample_compustat_factory(n_firms=1, n_years=1, seed=42)
        compustat_df["ceq"] = compustat_df["at"] * 0.3
        compustat_df["prcc_f"] = 50.0
        compustat_df["csho"] = 10.0
        compustat_df["oibdp"] = compustat_df["at"] * 0.2
        compustat_df["dvc"] = 10.0
        compustat_df["capx"] = compustat_df["at"] * 0.08
        compustat_df["xrd"] = compustat_df["at"] * 0.05

        row = pd.Series({"gvkey": None, "datadate": "2000-12-31"})
        with pytest.raises(FinancialCalculationError, match="missing gvkey"):
            calculate_firm_controls(row, compustat_df, 2000)

    def test_raises_error_on_no_matching_data(self, sample_compustat_factory):
        """Test that no matching Compustat data raises FinancialCalculationError."""
        compustat_df = sample_compustat_factory(n_firms=1, n_years=1, seed=42)
        compustat_df["ceq"] = compustat_df["at"] * 0.3
        compustat_df["prcc_f"] = 50.0
        compustat_df["csho"] = 10.0
        compustat_df["oibdp"] = compustat_df["at"] * 0.2
        compustat_df["dvc"] = 10.0
        compustat_df["capx"] = compustat_df["at"] * 0.08
        compustat_df["xrd"] = compustat_df["at"] * 0.05

        # Request year that doesn't exist
        row = pd.Series({"gvkey": "000000", "datadate": "1999-12-31"})
        with pytest.raises(FinancialCalculationError, match="no Compustat data found"):
            calculate_firm_controls(row, compustat_df, 1999)

    def test_raises_error_on_gvkey_not_in_compustat(self, sample_compustat_factory):
        """Test that gvkey not in Compustat raises FinancialCalculationError."""
        compustat_df = sample_compustat_factory(n_firms=1, n_years=1, seed=42)
        compustat_df["ceq"] = compustat_df["at"] * 0.3
        compustat_df["prcc_f"] = 50.0
        compustat_df["csho"] = 10.0
        compustat_df["oibdp"] = compustat_df["at"] * 0.2
        compustat_df["dvc"] = 10.0
        compustat_df["capx"] = compustat_df["at"] * 0.08
        compustat_df["xrd"] = compustat_df["at"] * 0.05

        row = pd.Series({"gvkey": "999999", "datadate": "2000-12-31"})
        with pytest.raises(FinancialCalculationError, match="no Compustat data found"):
            calculate_firm_controls(row, compustat_df, 2000)

    def test_data_fetched_by_gvkey_and_fyear(self, sample_compustat_factory):
        """Test that function correctly fetches data using gvkey and fyear."""
        compustat_df = sample_compustat_factory(n_firms=2, n_years=2, seed=42)
        compustat_df["ceq"] = compustat_df["at"] * 0.3
        compustat_df["prcc_f"] = 50.0
        compustat_df["csho"] = 10.0
        compustat_df["oibdp"] = compustat_df["at"] * 0.2
        compustat_df["dvc"] = 10.0
        compustat_df["capx"] = compustat_df["at"] * 0.08
        compustat_df["xrd"] = compustat_df["at"] * 0.05

        # Test second firm, second year
        row = pd.Series({"gvkey": "000001", "datadate": "2001-12-31"})
        result = calculate_firm_controls(row, compustat_df, 2001)
        # Should get data for gvkey=000001, fyear=2001
        expected_at = compustat_df[(compustat_df["gvkey"] == "000001") & (compustat_df["fyear"] == 2001)].iloc[0]["at"]
        assert result["size"] == pytest.approx(np.log(expected_at), rel=1e-5)

    def test_negative_ceq_returns_nan_market_to_book(self, sample_compustat_factory):
        """Test that negative ceq returns NaN for market_to_book."""
        compustat_df = sample_compustat_factory(n_firms=1, n_years=1, seed=42)
        compustat_df["ceq"] = -300.0  # Negative book equity
        compustat_df["prcc_f"] = 50.0
        compustat_df["csho"] = 10.0
        compustat_df["oibdp"] = compustat_df["at"] * 0.2
        compustat_df["dvc"] = 10.0
        compustat_df["capx"] = compustat_df["at"] * 0.08
        compustat_df["xrd"] = compustat_df["at"] * 0.05

        row = pd.Series({"gvkey": "000000", "datadate": "2000-12-31"})
        result = calculate_firm_controls(row, compustat_df, 2000)
        assert pd.isna(result["market_to_book"])

    def test_zero_ceq_returns_nan_market_to_book(self, sample_compustat_factory):
        """Test that zero ceq returns NaN for market_to_book."""
        compustat_df = sample_compustat_factory(n_firms=1, n_years=1, seed=42)
        compustat_df["ceq"] = 0.0
        compustat_df["prcc_f"] = 50.0
        compustat_df["csho"] = 10.0
        compustat_df["oibdp"] = compustat_df["at"] * 0.2
        compustat_df["dvc"] = 10.0
        compustat_df["capx"] = compustat_df["at"] * 0.08
        compustat_df["xrd"] = compustat_df["at"] * 0.05

        row = pd.Series({"gvkey": "000000", "datadate": "2000-12-31"})
        result = calculate_firm_controls(row, compustat_df, 2000)
        assert pd.isna(result["market_to_book"])

    def test_missing_rd_treated_correctly(self, sample_compustat_factory):
        """Test that missing xrd (R&D) results in NaN for r_intensity."""
        compustat_df = sample_compustat_factory(n_firms=1, n_years=1, seed=42)
        compustat_df["ceq"] = compustat_df["at"] * 0.3
        compustat_df["prcc_f"] = 50.0
        compustat_df["csho"] = 10.0
        compustat_df["oibdp"] = compustat_df["at"] * 0.2
        compustat_df["dvc"] = 10.0
        compustat_df["capx"] = compustat_df["at"] * 0.08
        compustat_df["xrd"] = np.nan  # Missing R&D

        row = pd.Series({"gvkey": "000000", "datadate": "2000-12-31"})
        result = calculate_firm_controls(row, compustat_df, 2000)
        # When xrd is NaN, r_intensity should be NaN (not get() returns None -> nan)
        assert pd.isna(result["r_intensity"])


class TestCalculateFirmControlsQuarterly:
    """Tests for calculate_firm_controls_quarterly() function."""

    @pytest.fixture
    def sample_quarterly_compustat(self):
        """Create sample quarterly Compustat data for testing."""
        return pd.DataFrame({
            "gvkey": ["000001", "000001", "000001", "000002", "000002", "000002"],
            "datadate": pd.to_datetime([
                "2020-03-31", "2020-06-30", "2020-09-30",
                "2020-03-31", "2020-06-30", "2020-09-30",
            ]),
            "atq": [1000, 1050, 1100, 500, 525, 550],
            "ceqq": [400, 420, 440, 200, 210, 220],
            "cshoq": [100, 100, 100, 50, 50, 50],
            "prccq": [20, 22, 24, 10, 11, 12],
            "ltq": [600, 630, 660, 300, 315, 330],  # Total liabilities (kept for reference)
            "dlcq": [75, 80, 85, 40, 42, 45],      # Short-term interest-bearing debt
            "dlttq": [200, 210, 220, 100, 105, 110],  # Long-term debt
            "niq": [50, 55, 60, 25, 27, 30],
            "actq": [500, 525, 550, 250, 262, 275],
            "lctq": [200, 210, 220, 100, 105, 110],
            "xrdq": [20, 22, 24, 10, 11, 12],
        })

    def test_returns_size_as_log_atq(self, sample_quarterly_compustat):
        """Test that Size is log of atq."""
        row = pd.Series({"gvkey": "000001", "datadate": pd.Timestamp("2020-06-30")})
        result = calculate_firm_controls_quarterly(
            row, sample_quarterly_compustat, pd.Timestamp("2020-06-30")
        )
        assert "Size" in result
        assert result["Size"] == pytest.approx(np.log(1050), rel=1e-5)

    def test_calculates_book_to_market(self, sample_quarterly_compustat):
        """Test that BM is calculated correctly."""
        row = pd.Series({"gvkey": "000001", "datadate": pd.Timestamp("2020-06-30")})
        result = calculate_firm_controls_quarterly(
            row, sample_quarterly_compustat, pd.Timestamp("2020-06-30")
        )
        assert "BM" in result
        # BM = ceqq / (cshoq * prccq)
        expected = 420 / (100 * 22)
        assert result["BM"] == pytest.approx(expected, rel=1e-5)

    def test_calculates_leverage_quarterly(self, sample_quarterly_compustat):
        """Test that Lev is calculated correctly as (dlcq + dlttq) / atq."""
        row = pd.Series({"gvkey": "000001", "datadate": pd.Timestamp("2020-06-30")})
        result = calculate_firm_controls_quarterly(
            row, sample_quarterly_compustat, pd.Timestamp("2020-06-30")
        )
        assert "Lev" in result
        # Lev = (dlcq + dlttq) / atq = (80 + 210) / 1050
        expected = (80 + 210) / 1050
        assert result["Lev"] == pytest.approx(expected, rel=1e-5)

    def test_calculates_roa(self, sample_quarterly_compustat):
        """Test that ROA is calculated correctly."""
        row = pd.Series({"gvkey": "000001", "datadate": pd.Timestamp("2020-06-30")})
        result = calculate_firm_controls_quarterly(
            row, sample_quarterly_compustat, pd.Timestamp("2020-06-30")
        )
        assert "ROA" in result
        expected = 55 / 1050
        assert result["ROA"] == pytest.approx(expected, rel=1e-5)

    def test_calculates_current_ratio(self, sample_quarterly_compustat):
        """Test that CurrentRatio is calculated correctly."""
        row = pd.Series({"gvkey": "000001", "datadate": pd.Timestamp("2020-06-30")})
        result = calculate_firm_controls_quarterly(
            row, sample_quarterly_compustat, pd.Timestamp("2020-06-30")
        )
        assert "CurrentRatio" in result
        expected = 525 / 210
        assert result["CurrentRatio"] == pytest.approx(expected, rel=1e-5)

    def test_calculates_rd_intensity(self, sample_quarterly_compustat):
        """Test that RD_Intensity is calculated correctly."""
        row = pd.Series({"gvkey": "000001", "datadate": pd.Timestamp("2020-06-30")})
        result = calculate_firm_controls_quarterly(
            row, sample_quarterly_compustat, pd.Timestamp("2020-06-30")
        )
        assert "RD_Intensity" in result
        expected = 22 / 1050
        assert result["RD_Intensity"] == pytest.approx(expected, rel=1e-5)

    def test_finds_closest_datadate(self, sample_quarterly_compustat):
        """Test that function finds data closest to specified date."""
        # Request data after last available date
        row = pd.Series({"gvkey": "000001", "datadate": pd.Timestamp("2020-12-15")})
        result = calculate_firm_controls_quarterly(
            row, sample_quarterly_compustat, pd.Timestamp("2020-12-15")
        )
        # Should find data from 2020-09-30 (most recent before Dec 15)
        assert isinstance(result, dict)
        assert "Size" in result
        assert result["Size"] == pytest.approx(np.log(1100), rel=1e-5)

    def test_all_quarterly_keys_present(self, sample_quarterly_compustat):
        """Test that all expected quarterly control keys are present."""
        row = pd.Series({"gvkey": "000001", "datadate": pd.Timestamp("2020-06-30")})
        result = calculate_firm_controls_quarterly(
            row, sample_quarterly_compustat, pd.Timestamp("2020-06-30")
        )
        expected_keys = ["Size", "BM", "Lev", "ROA", "CurrentRatio", "RD_Intensity"]
        for key in expected_keys:
            assert key in result, f"Missing key: {key}"

    def test_raises_error_on_missing_gvkey(self, sample_quarterly_compustat):
        """Test that missing gvkey raises FinancialCalculationError."""
        row = pd.Series({"datadate": pd.Timestamp("2020-06-30")})
        with pytest.raises(FinancialCalculationError, match="missing gvkey"):
            calculate_firm_controls_quarterly(
                row, sample_quarterly_compustat, pd.Timestamp("2020-06-30")
            )

    def test_raises_error_on_no_data_found(self, sample_quarterly_compustat):
        """Test that no matching data raises FinancialCalculationError."""
        row = pd.Series({"gvkey": "999999", "datadate": pd.Timestamp("2020-06-30")})
        with pytest.raises(FinancialCalculationError, match="no Compustat data found"):
            calculate_firm_controls_quarterly(
                row, sample_quarterly_compustat, pd.Timestamp("2020-06-30")
            )

    def test_handles_zero_lctq_for_current_ratio(self, sample_quarterly_compustat):
        """Test that zero lctq returns NaN for CurrentRatio."""
        df = sample_quarterly_compustat.copy()
        df.loc[1, "lctq"] = 0.0
        row = pd.Series({"gvkey": "000001", "datadate": pd.Timestamp("2020-06-30")})
        result = calculate_firm_controls_quarterly(
            row, df, pd.Timestamp("2020-06-30")
        )
        assert pd.isna(result["CurrentRatio"])

    def test_handles_missing_xrdq_treats_as_zero(self, sample_quarterly_compustat):
        """Test that missing xrdq is treated as zero for RD_Intensity."""
        df = sample_quarterly_compustat.copy()
        df.loc[1, "xrdq"] = np.nan
        row = pd.Series({"gvkey": "000001", "datadate": pd.Timestamp("2020-06-30")})
        result = calculate_firm_controls_quarterly(
            row, df, pd.Timestamp("2020-06-30")
        )
        # Missing xrdq should be treated as 0
        expected = 0 / 1050
        assert result["RD_Intensity"] == pytest.approx(expected, rel=1e-5)

    def test_handles_zero_atq_returns_nan_size(self, sample_quarterly_compustat):
        """Test that zero atq returns NaN for Size."""
        df = sample_quarterly_compustat.copy()
        df.loc[1, "atq"] = 0.0
        row = pd.Series({"gvkey": "000001", "datadate": pd.Timestamp("2020-06-30")})
        result = calculate_firm_controls_quarterly(
            row, df, pd.Timestamp("2020-06-30")
        )
        assert pd.isna(result["Size"])

    def test_handles_negative_atq_returns_nan_size(self, sample_quarterly_compustat):
        """Test that negative atq returns NaN for Size."""
        df = sample_quarterly_compustat.copy()
        df.loc[1, "atq"] = -100.0
        row = pd.Series({"gvkey": "000001", "datadate": pd.Timestamp("2020-06-30")})
        result = calculate_firm_controls_quarterly(
            row, df, pd.Timestamp("2020-06-30")
        )
        assert pd.isna(result["Size"])

    def test_handles_zero_cshoq_or_prccq_returns_nan_bm(self, sample_quarterly_compustat):
        """Test that zero cshoq or prccq returns NaN for BM."""
        df = sample_quarterly_compustat.copy()
        df.loc[1, "cshoq"] = 0.0
        row = pd.Series({"gvkey": "000001", "datadate": pd.Timestamp("2020-06-30")})
        result = calculate_firm_controls_quarterly(
            row, df, pd.Timestamp("2020-06-30")
        )
        assert pd.isna(result["BM"])

    def test_handles_negative_ceqq_returns_nan_bm(self, sample_quarterly_compustat):
        """Test that negative ceqq returns NaN for BM."""
        df = sample_quarterly_compustat.copy()
        df.loc[1, "ceqq"] = -100.0
        row = pd.Series({"gvkey": "000001", "datadate": pd.Timestamp("2020-06-30")})
        result = calculate_firm_controls_quarterly(
            row, df, pd.Timestamp("2020-06-30")
        )
        assert pd.isna(result["BM"])


class TestComputeFinancialFeatures:
    """Tests for compute_financial_features() function."""

    def test_returns_dataframe_with_controls(self, sample_compustat_factory):
        """Test that compute_financial_features returns DataFrame with controls."""
        compustat_df = sample_compustat_factory(n_firms=2, n_years=1, seed=42)
        compustat_df["ceq"] = compustat_df["at"] * 0.3
        compustat_df["prcc_f"] = 50.0
        compustat_df["csho"] = 10.0
        compustat_df["oibdp"] = compustat_df["at"] * 0.2
        compustat_df["dvc"] = 10.0
        compustat_df["capx"] = compustat_df["at"] * 0.08
        compustat_df["xrd"] = compustat_df["at"] * 0.05

        # Create firm_df with matching gvkeys and years (factory uses years starting from 2000)
        firm_df = pd.DataFrame({
            "gvkey": ["000000", "000001"],
            "year": [2000, 2000],
        })

        result = compute_financial_features(firm_df, compustat_df)
        assert isinstance(result, pd.DataFrame)
        assert "size" in result.columns
        assert "leverage" in result.columns

    def test_handles_empty_dataframe(self, sample_compustat_factory):
        """Test that empty input DataFrame returns empty result."""
        compustat_df = sample_compustat_factory(n_firms=1, n_years=1, seed=42)
        compustat_df["ceq"] = compustat_df["at"] * 0.3
        compustat_df["prcc_f"] = 50.0
        compustat_df["csho"] = 10.0
        compustat_df["oibdp"] = compustat_df["at"] * 0.2
        compustat_df["dvc"] = 10.0
        compustat_df["capx"] = compustat_df["at"] * 0.08
        compustat_df["xrd"] = compustat_df["at"] * 0.05

        df = pd.DataFrame(columns=["gvkey", "year"])
        result = compute_financial_features(df, compustat_df)
        assert len(result) == 0

    def test_skips_rows_without_year(self, sample_compustat_factory):
        """Test that rows without year (None) are skipped."""
        compustat_df = sample_compustat_factory(n_firms=1, n_years=1, seed=42)
        compustat_df["ceq"] = compustat_df["at"] * 0.3
        compustat_df["prcc_f"] = 50.0
        compustat_df["csho"] = 10.0
        compustat_df["oibdp"] = compustat_df["at"] * 0.2
        compustat_df["dvc"] = 10.0
        compustat_df["capx"] = compustat_df["at"] * 0.08
        compustat_df["xrd"] = compustat_df["at"] * 0.05

        # Create DataFrame with explicit object dtype to preserve None values
        df = pd.DataFrame({
            "gvkey": ["000000", "000000"],
            "year": pd.Series([2000, None], dtype=object),  # Second row has None year
        })
        result = compute_financial_features(df, compustat_df)
        assert len(result) == 1  # Only one row processed


class TestComputeFinancialControlsQuarterly:
    """Tests for compute_financial_controls_quarterly() function."""

    @pytest.fixture
    def sample_quarterly_df(self):
        """Create sample quarterly Compustat DataFrame for testing."""
        # Create data with proper structure for EPS lag calculations
        # Each firm needs at least 5 quarters for lag4 to work
        data = []
        for firm_id in range(2):
            gvkey = f"{firm_id:06d}"
            for quarter in range(8):  # 8 quarters per firm
                row = {
                    "gvkey": gvkey,
                    "datadate": pd.Timestamp("2020-03-31") + pd.DateOffset(months=quarter * 3),
                    "atq": 1000 + firm_id * 500 + quarter * 50,
                    "ceqq": 400 + firm_id * 200 + quarter * 20,
                    "cshoq": 100,
                    "prccq": 20 + quarter,
                    "ltq": 600 + firm_id * 300 + quarter * 30,  # Total liabilities (kept for reference)
                    "dlcq": 75 + firm_id * 37 + quarter * 4,    # Short-term interest-bearing debt
                    "dlttq": 200 + firm_id * 100 + quarter * 10,  # Long-term debt
                    "niq": 50 + firm_id * 25 + quarter * 5,
                    "actq": 500 + firm_id * 250 + quarter * 25,
                    "lctq": 200 + firm_id * 100 + quarter * 10,
                    "xrdq": 20 + firm_id * 10 + quarter * 2,
                    "epspxq": 0.5 + firm_id * 0.25 + quarter * 0.1,
                }
                data.append(row)
        return pd.DataFrame(data)

    def test_returns_dataframe_with_quarterly_controls(self, sample_quarterly_df):
        """Test that function adds quarterly control columns."""
        result = compute_financial_controls_quarterly(
            sample_quarterly_df.copy(), winsorize=False
        )
        assert "Size" in result.columns
        assert "BM" in result.columns
        assert "Lev" in result.columns
        assert "ROA" in result.columns
        assert "CurrentRatio" in result.columns
        assert "RD_Intensity" in result.columns
        assert "EPS_Growth" in result.columns

    @pytest.mark.xfail(reason="pandas/numpy compatibility issue with .clip() internal sum()")
    def test_winsorize_parameter_affects_output(self, sample_quarterly_df):
        """Test that winsorize parameter affects extreme values."""
        # Create data with extreme values
        df_extreme = sample_quarterly_df.copy()
        df_extreme.loc[0, "atq"] = 100000  # Extreme value

        result_no_winsor = compute_financial_controls_quarterly(
            df_extreme.copy(), winsorize=False
        )
        result_winsor = compute_financial_controls_quarterly(
            df_extreme.copy(), winsorize=True
        )

        # The winsorized version should have the extreme value clipped
        # Compare the Size values - winsorized should be different
        assert not result_no_winsor["Size"].equals(result_winsor["Size"])

    def test_calculates_eps_growth(self, sample_quarterly_df):
        """Test that EPS_Growth is calculated correctly."""
        result = compute_financial_controls_quarterly(
            sample_quarterly_df.copy(), winsorize=False
        )
        assert "EPS_Growth" in result.columns
        # EPS_Growth requires 4 quarters of data for lag
        # Rows with lag4 data should have non-NaN values
        # Use any() to check for at least one non-NaN value
        assert result["EPS_Growth"].notna().any()

    def test_handles_zero_lctq_for_current_ratio(self, sample_quarterly_df):
        """Test that zero lctq is handled in CurrentRatio calculation."""
        df = sample_quarterly_df.copy()
        df.loc[0, "lctq"] = 0.0
        result = compute_financial_controls_quarterly(df, winsorize=False)
        # Zero lctq should result in NaN CurrentRatio (division by 0 -> replaced with nan)
        assert pd.isna(result.loc[0, "CurrentRatio"])

    @pytest.mark.xfail(reason="pandas/numpy compatibility issue with .fillna() internal sum()")
    def test_handles_missing_xrdq_treats_as_zero(self, sample_quarterly_df):
        """Test that missing xrdq is treated as zero for RD_Intensity."""
        df = sample_quarterly_df.copy()
        # Set a single xrdq value to NaN to test fillna behavior
        df.loc[df.index[0], "xrdq"] = np.nan
        result = compute_financial_controls_quarterly(df, winsorize=False)
        # Missing xrdq should be treated as 0, so RD_Intensity should be 0/atq
        # Check that RD_Intensity was computed (not NaN from division by 0)
        assert "RD_Intensity" in result.columns
        assert not pd.isna(result.loc[df.index[0], "RD_Intensity"])

    def test_size_is_log_atq(self, sample_quarterly_df):
        """Test that Size is calculated as log(atq)."""
        result = compute_financial_controls_quarterly(
            sample_quarterly_df.copy(), winsorize=False
        )
        expected_size = np.log(sample_quarterly_df.loc[0, "atq"])
        assert result.loc[0, "Size"] == pytest.approx(expected_size, rel=1e-5)

    def test_bm_calculation(self, sample_quarterly_df):
        """Test that BM is calculated correctly."""
        result = compute_financial_controls_quarterly(
            sample_quarterly_df.copy(), winsorize=False
        )
        # BM = ceqq / (cshoq * prccq)
        expected_bm = sample_quarterly_df.loc[0, "ceqq"] / (
            sample_quarterly_df.loc[0, "cshoq"] * sample_quarterly_df.loc[0, "prccq"]
        )
        assert result.loc[0, "BM"] == pytest.approx(expected_bm, rel=1e-5)

    def test_lev_calculation(self, sample_quarterly_df):
        """Test that Lev is calculated correctly as (dlcq + dlttq) / atq."""
        result = compute_financial_controls_quarterly(
            sample_quarterly_df.copy(), winsorize=False
        )
        # Lev = (dlcq + dlttq) / atq
        expected_lev = (
            sample_quarterly_df.loc[0, "dlcq"] + sample_quarterly_df.loc[0, "dlttq"]
        ) / sample_quarterly_df.loc[0, "atq"]
        assert result.loc[0, "Lev"] == pytest.approx(expected_lev, rel=1e-5)

    def test_roa_calculation(self, sample_quarterly_df):
        """Test that ROA is calculated correctly."""
        result = compute_financial_controls_quarterly(
            sample_quarterly_df.copy(), winsorize=False
        )
        expected_roa = sample_quarterly_df.loc[0, "niq"] / sample_quarterly_df.loc[0, "atq"]
        assert result.loc[0, "ROA"] == pytest.approx(expected_roa, rel=1e-5)

    def test_preserves_original_columns(self, sample_quarterly_df):
        """Test that original columns are preserved."""
        result = compute_financial_controls_quarterly(
            sample_quarterly_df.copy(), winsorize=False
        )
        for col in sample_quarterly_df.columns:
            assert col in result.columns

    def test_sorts_by_gvkey_and_datadate(self, sample_quarterly_df):
        """Test that result is sorted by gvkey and datadate."""
        # Shuffle input
        df_shuffled = sample_quarterly_df.sample(frac=1, random_state=42).reset_index(drop=True)
        result = compute_financial_controls_quarterly(df_shuffled, winsorize=False)
        # Check that result is sorted
        assert result["gvkey"].is_monotonic_increasing or result.groupby("gvkey")["datadate"].is_monotonic_increasing.all()
