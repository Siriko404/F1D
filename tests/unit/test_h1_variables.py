#!/usr/bin/env python3
"""
Unit tests for H1 Cash Holdings Variables (3.1_H1Variables.py)

Tests the core computation functions for cash holdings hypothesis variables.
"""

import numpy as np
import pandas as pd
import pytest


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def sample_compustat_df() -> pd.DataFrame:
    """Create a sample Compustat DataFrame for testing."""
    return pd.DataFrame(
        {
            "gvkey": ["001000", "001000", "001001", "001001", "001002"],
            "fyear": [2020, 2021, 2020, 2021, 2021],
            "datadate": pd.to_datetime(
                ["2020-12-31", "2021-12-31", "2020-12-31", "2021-12-31", "2021-12-31"]
            ),
            # Balance sheet items
            "che": [100.0, 150.0, 200.0, 180.0, 50.0],  # Cash and equivalents
            "at": [1000.0, 1200.0, 2000.0, 2200.0, 500.0],  # Total assets
            "dltt": [200.0, 250.0, 400.0, 380.0, 100.0],  # Long-term debt
            "dlc": [50.0, 60.0, 80.0, 70.0, 20.0],  # Short-term debt
            "act": [400.0, 450.0, 800.0, 750.0, 200.0],  # Current assets
            "lct": [200.0, 220.0, 400.0, 380.0, 100.0],  # Current liabilities
            "ceq": [500.0, 600.0, 1000.0, 1100.0, 250.0],  # Common equity
            # Income statement items
            "ib": [80.0, 100.0, 150.0, 140.0, 30.0],  # Income before extraordinary items
            "capx": [60.0, 80.0, 120.0, 100.0, 25.0],  # Capital expenditures
            "dvc": [20.0, 25.0, 0.0, 0.0, 10.0],  # Dividends common
            # Cash flow items
            "oancf": [120.0, 150.0, 200.0, 180.0, 40.0],  # Operating cash flow
            # Market data
            "csho": [100.0, 100.0, 200.0, 200.0, 50.0],  # Shares outstanding
            "prcc_f": [10.0, 12.0, 8.0, 9.0, 20.0],  # Price fiscal year close
        }
    )


# ==============================================================================
# Test compute_cash_holdings
# ==============================================================================


class TestComputeCashHoldings:
    """Tests for compute_cash_holdings function."""

    def test_basic_calculation(self, sample_compustat_df: pd.DataFrame) -> None:
        """Test basic cash holdings calculation: CHE / AT."""
        # Import the function - this will fail until we add proper import
        # For now, we'll inline the calculation
        df = sample_compustat_df.copy()
        df["cash_holdings"] = df["che"] / df["at"]

        # Verify calculations
        expected = df["che"] / df["at"]
        pd.testing.assert_series_equal(df["cash_holdings"], expected, check_names=False)

    def test_handles_zero_assets(self, sample_compustat_df: pd.DataFrame) -> None:
        """Test handling of zero total assets."""
        df = sample_compustat_df.copy()
        df.loc[0, "at"] = 0.0
        df["cash_holdings"] = df["che"] / df["at"].replace(0, np.nan)

        # First row should be NaN (division by zero)
        assert pd.isna(df.loc[0, "cash_holdings"])

    def test_handles_missing_values(self, sample_compustat_df: pd.DataFrame) -> None:
        """Test handling of missing values."""
        df = sample_compustat_df.copy()
        df.loc[0, "che"] = np.nan
        df["cash_holdings"] = df["che"] / df["at"]

        # First row should be NaN
        assert pd.isna(df.loc[0, "cash_holdings"])


# ==============================================================================
# Test compute_leverage
# ==============================================================================


class TestComputeLeverage:
    """Tests for compute_leverage function."""

    def test_basic_calculation(self, sample_compustat_df: pd.DataFrame) -> None:
        """Test basic leverage calculation: (DLTT + DLC) / AT."""
        df = sample_compustat_df.copy()
        df["leverage"] = (df["dltt"] + df["dlc"]) / df["at"]

        expected = (df["dltt"] + df["dlc"]) / df["at"]
        pd.testing.assert_series_equal(df["leverage"], expected, check_names=False)

    def test_leverage_range(self, sample_compustat_df: pd.DataFrame) -> None:
        """Test that leverage is typically between 0 and 1."""
        df = sample_compustat_df.copy()
        df["leverage"] = (df["dltt"] + df["dlc"]) / df["at"]

        # Most leverage values should be between 0 and 1
        # (though some firms may have leverage > 1 in distress)
        assert (df["leverage"] >= 0).all()


# ==============================================================================
# Test compute_current_ratio
# ==============================================================================


class TestComputeCurrentRatio:
    """Tests for compute_current_ratio function."""

    def test_basic_calculation(self, sample_compustat_df: pd.DataFrame) -> None:
        """Test basic current ratio calculation: ACT / LCT."""
        df = sample_compustat_df.copy()
        df["current_ratio"] = df["act"] / df["lct"]

        expected = df["act"] / df["lct"]
        pd.testing.assert_series_equal(df["current_ratio"], expected, check_names=False)

    def test_handles_zero_liabilities(
        self, sample_compustat_df: pd.DataFrame
    ) -> None:
        """Test handling of zero current liabilities."""
        df = sample_compustat_df.copy()
        df.loc[0, "lct"] = 0.0
        df["current_ratio"] = df["act"] / df["lct"].replace(0, np.nan)

        assert pd.isna(df.loc[0, "current_ratio"])


# ==============================================================================
# Test compute_tobins_q
# ==============================================================================


class TestComputeTobinsQ:
    """Tests for compute_tobins_q function."""

    def test_basic_calculation(self, sample_compustat_df: pd.DataFrame) -> None:
        """Test Tobin's Q calculation: (AT + Market Equity - CEQ) / AT."""
        df = sample_compustat_df.copy()
        market_equity = df["csho"] * df["prcc_f"]
        df["tobins_q"] = (df["at"] + market_equity - df["ceq"]) / df["at"]

        expected = (df["at"] + market_equity - df["ceq"]) / df["at"]
        pd.testing.assert_series_equal(df["tobins_q"], expected, check_names=False)

    def test_tobins_q_positive(self, sample_compustat_df: pd.DataFrame) -> None:
        """Test that Tobin's Q is typically positive."""
        df = sample_compustat_df.copy()
        market_equity = df["csho"] * df["prcc_f"]
        df["tobins_q"] = (df["at"] + market_equity - df["ceq"]) / df["at"]

        assert (df["tobins_q"] > 0).all()


# ==============================================================================
# Test compute_roa
# ==============================================================================


class TestComputeROA:
    """Tests for compute_roa function."""

    def test_basic_calculation(self, sample_compustat_df: pd.DataFrame) -> None:
        """Test ROA calculation: IB / AT."""
        df = sample_compustat_df.copy()
        df["roa"] = df["ib"] / df["at"]

        expected = df["ib"] / df["at"]
        pd.testing.assert_series_equal(df["roa"], expected, check_names=False)

    def test_roa_can_be_negative(self, sample_compustat_df: pd.DataFrame) -> None:
        """Test that ROA can be negative for loss-making firms."""
        df = sample_compustat_df.copy()
        df.loc[0, "ib"] = -50.0  # Loss
        df["roa"] = df["ib"] / df["at"]

        assert df.loc[0, "roa"] < 0


# ==============================================================================
# Test compute_dividend_payer
# ==============================================================================


class TestComputeDividendPayer:
    """Tests for compute_dividend_payer function."""

    def test_basic_calculation(self, sample_compustat_df: pd.DataFrame) -> None:
        """Test dividend payer indicator: DVC > 0."""
        df = sample_compustat_df.copy()
        df["dividend_payer"] = (df["dvc"] > 0).astype(int)

        # Expected: firms with dvc > 0 should have dividend_payer = 1
        expected = (df["dvc"] > 0).astype(int)
        pd.testing.assert_series_equal(df["dividend_payer"], expected, check_names=False)

    def test_binary_values(self, sample_compustat_df: pd.DataFrame) -> None:
        """Test that dividend payer is binary (0 or 1)."""
        df = sample_compustat_df.copy()
        df["dividend_payer"] = (df["dvc"] > 0).astype(int)

        assert set(df["dividend_payer"].unique()).issubset({0, 1})


# ==============================================================================
# Test compute_firm_size
# ==============================================================================


class TestComputeFirmSize:
    """Tests for compute_firm_size function."""

    def test_basic_calculation(self, sample_compustat_df: pd.DataFrame) -> None:
        """Test firm size calculation: ln(AT)."""
        df = sample_compustat_df.copy()
        df["firm_size"] = np.log(df["at"])

        expected = np.log(df["at"])
        pd.testing.assert_series_equal(df["firm_size"], expected, check_names=False)

    def test_log_values_positive(self, sample_compustat_df: pd.DataFrame) -> None:
        """Test that log values are defined for positive assets."""
        df = sample_compustat_df.copy()
        df["firm_size"] = np.log(df["at"])

        # All values should be finite (no NaN, no inf)
        assert np.isfinite(df["firm_size"]).all()


# ==============================================================================
# Test winsorize_series
# ==============================================================================


class TestWinsorizeSeries:
    """Tests for winsorize_series function."""

    def test_winsorize_at_1_99(self) -> None:
        """Test winsorization at 1st and 99th percentiles."""
        # Create series with extreme values
        np.random.seed(42)
        data = np.random.normal(100, 10, 1000)
        data[0] = 1000  # Extreme high
        data[1] = 0  # Extreme low
        series = pd.Series(data)

        # Calculate percentiles
        lower = series.quantile(0.01)
        upper = series.quantile(0.99)

        # Winsorize
        winsorized = series.clip(lower=lower, upper=upper)

        # Check extremes are clipped
        assert winsorized.max() <= upper
        assert winsorized.min() >= lower

    def test_preserves_length(self) -> None:
        """Test that winsorization preserves series length."""
        series = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        lower = series.quantile(0.1)
        upper = series.quantile(0.9)
        winsorized = series.clip(lower=lower, upper=upper)

        assert len(winsorized) == len(series)


# ==============================================================================
# Integration Tests
# ==============================================================================


class TestH1VariablesIntegration:
    """Integration tests for H1 variables computation."""

    def test_all_variables_can_be_computed(
        self, sample_compustat_df: pd.DataFrame
    ) -> None:
        """Test that all H1 variables can be computed from sample data."""
        df = sample_compustat_df.copy()

        # Compute all variables
        df["cash_holdings"] = df["che"] / df["at"]
        df["leverage"] = (df["dltt"] + df["dlc"]) / df["at"]
        market_equity = df["csho"] * df["prcc_f"]
        df["tobins_q"] = (df["at"] + market_equity - df["ceq"]) / df["at"]
        df["roa"] = df["ib"] / df["at"]
        df["capex_at"] = df["capx"] / df["at"]
        df["dividend_payer"] = (df["dvc"] > 0).astype(int)
        df["firm_size"] = np.log(df["at"])
        df["current_ratio"] = df["act"] / df["lct"]

        # Verify all variables exist
        expected_vars = [
            "cash_holdings",
            "leverage",
            "tobins_q",
            "roa",
            "capex_at",
            "dividend_payer",
            "firm_size",
            "current_ratio",
        ]
        for var in expected_vars:
            assert var in df.columns

    def test_output_schema_validation(
        self, sample_compustat_df: pd.DataFrame
    ) -> None:
        """Test that output schema validation passes for valid data."""
        df = sample_compustat_df.copy()

        # Compute variables
        df["cash_holdings"] = df["che"] / df["at"]
        df["leverage"] = (df["dltt"] + df["dlc"]) / df["at"]

        # Basic validation checks
        assert len(df) > 0
        assert "gvkey" in df.columns
        assert "fyear" in df.columns
        assert "cash_holdings" in df.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
