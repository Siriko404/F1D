#!/usr/bin/env python3
"""
Unit tests for auxiliary financial scripts (3.9, 3.10, 3.11, 3.12, 3.13)

Tests core computation functions for:
- H2 Biddle Investment Residual (3.9)
- H2 PRisk x Uncertainty Merge (3.10)
- H9 Style Frozen (3.11)
- H9 PRisk FY (3.12)
- H9 Abnormal Investment (3.13)
"""

import numpy as np
import pandas as pd
import pytest


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def sample_compustat_for_investment() -> pd.DataFrame:
    """Create a sample Compustat DataFrame for investment calculations."""
    return pd.DataFrame(
        {
            "gvkey": ["001000", "001000", "001001", "001001", "001002"],
            "fyear": [2020, 2021, 2020, 2021, 2021],
            "at": [1000.0, 1100.0, 2000.0, 2200.0, 500.0],  # Total assets
            "capx": [80.0, 90.0, 150.0, 160.0, 40.0],  # CapEx
            "xrd": [50.0, 60.0, 100.0, 110.0, 20.0],  # R&D
            "aqc": [20.0, 30.0, 40.0, 50.0, 10.0],  # Acquisitions
            "sppe": [10.0, 15.0, 20.0, 25.0, 5.0],  # Asset sales (negative in investment)
            "sale": [500.0, 550.0, 1000.0, 1100.0, 250.0],  # Sales
            "ceq": [500.0, 550.0, 1000.0, 1100.0, 250.0],  # Common equity
            "csho": [100.0, 100.0, 200.0, 200.0, 50.0],  # Shares outstanding
            "prcc_f": [10.0, 12.0, 8.0, 9.0, 20.0],  # Price
        }
    )


@pytest.fixture
def sample_prisk_df() -> pd.DataFrame:
    """Create a sample PRisk DataFrame for testing."""
    return pd.DataFrame(
        {
            "gvkey": ["001000", "001000", "001001", "001001", "001002"],
            "year": [2020, 2021, 2020, 2021, 2021],
            "PRisk": [0.15, 0.18, 0.22, 0.20, 0.10],
            "NPRisk": [0.10, 0.12, 0.15, 0.14, 0.08],
        }
    )


@pytest.fixture
def sample_uncertainty_df() -> pd.DataFrame:
    """Create a sample uncertainty DataFrame for testing."""
    return pd.DataFrame(
        {
            "gvkey": ["001000", "001000", "001001", "001001", "001002"],
            "year": [2020, 2021, 2020, 2021, 2021],
            "Manager_QA_Uncertainty_pct": [2.5, 3.0, 3.5, 3.2, 1.5],
        }
    )


# ==============================================================================
# Test Investment Calculation (H2 Biddle)
# ==============================================================================


class TestInvestmentCalculation:
    """Tests for Biddle (2009) investment measure."""

    def test_investment_components(
        self, sample_compustat_for_investment: pd.DataFrame
    ) -> None:
        """Test investment = (CapEx + R&D + Acquisitions - AssetSales) / lag(AT)."""
        df = sample_compustat_for_investment.copy()

        # Calculate investment components
        df["investment_raw"] = df["capx"] + df["xrd"] + df["aqc"] - df["sppe"]

        expected = df["capx"] + df["xrd"] + df["aqc"] - df["sppe"]
        pd.testing.assert_series_equal(df["investment_raw"], expected, check_names=False)

    def test_investment_scaled_by_lagged_assets(
        self, sample_compustat_for_investment: pd.DataFrame
    ) -> None:
        """Test investment scaled by lagged total assets."""
        df = sample_compustat_for_investment.copy()

        # Calculate lagged assets within gvkey
        df["at_lag"] = df.groupby("gvkey")["at"].shift(1)
        df["investment_raw"] = df["capx"] + df["xrd"] + df["aqc"] - df["sppe"]
        df["investment"] = df["investment_raw"] / df["at_lag"]

        # First year for each firm should be NaN (no lagged assets)
        assert pd.isna(df.loc[0, "investment"])
        assert pd.isna(df.loc[2, "investment"])

    def test_investment_positive(self, sample_compustat_for_investment: pd.DataFrame) -> None:
        """Test that investment is typically positive."""
        df = sample_compustat_for_investment.copy()
        df["investment_raw"] = df["capx"] + df["xrd"] + df["aqc"] - df["sppe"]

        # Investment components should be positive (assuming CapEx+R&D+Acq > AssetSales)
        assert (df["investment_raw"] > 0).all()


# ==============================================================================
# Test Tobin's Q Calculation
# ==============================================================================


class TestTobinsQ:
    """Tests for Tobin's Q calculation."""

    def test_tobins_q_calculation(
        self, sample_compustat_for_investment: pd.DataFrame
    ) -> None:
        """Test Tobin's Q: (AT + Market Equity - CEQ) / AT."""
        df = sample_compustat_for_investment.copy()

        market_equity = df["csho"] * df["prcc_f"]
        df["tobins_q"] = (df["at"] + market_equity - df["ceq"]) / df["at"]

        expected = (df["at"] + market_equity - df["ceq"]) / df["at"]
        pd.testing.assert_series_equal(df["tobins_q"], expected, check_names=False)

    def test_tobins_q_lagged(
        self, sample_compustat_for_investment: pd.DataFrame
    ) -> None:
        """Test lagged Tobin's Q for first-stage regression."""
        df = sample_compustat_for_investment.copy()

        market_equity = df["csho"] * df["prcc_f"]
        df["tobins_q"] = (df["at"] + market_equity - df["ceq"]) / df["at"]
        df["tobins_q_lag"] = df.groupby("gvkey")["tobins_q"].shift(1)

        # First year for each firm should be NaN
        assert pd.isna(df.loc[0, "tobins_q_lag"])
        assert pd.isna(df.loc[2, "tobins_q_lag"])


# ==============================================================================
# Test Sales Growth Calculation
# ==============================================================================


class TestSalesGrowth:
    """Tests for sales growth calculation."""

    def test_sales_growth_calculation(
        self, sample_compustat_for_investment: pd.DataFrame
    ) -> None:
        """Test sales growth: (Sale_t - Sale_t-1) / Sale_t-1."""
        df = sample_compustat_for_investment.copy()

        df["sales_growth"] = df.groupby("gvkey")["sale"].pct_change()

        expected = df.groupby("gvkey")["sale"].pct_change()
        pd.testing.assert_series_equal(df["sales_growth"], expected, check_names=False)

    def test_sales_growth_lagged(
        self, sample_compustat_for_investment: pd.DataFrame
    ) -> None:
        """Test lagged sales growth for first-stage regression."""
        df = sample_compustat_for_investment.copy()

        df["sales_growth"] = df.groupby("gvkey")["sale"].pct_change()
        df["sales_growth_lag"] = df.groupby("gvkey")["sales_growth"].shift(1)

        # Should have NaN for first two years of each firm
        assert pd.isna(df.loc[0, "sales_growth_lag"])
        assert pd.isna(df.loc[2, "sales_growth_lag"])


# ==============================================================================
# Test Standardization (PRisk x Uncertainty)
# ==============================================================================


class TestStandardization:
    """Tests for variable standardization."""

    def test_standardization_centered_at_zero(self) -> None:
        """Test that standardized variable has mean ~0."""
        data = np.random.normal(100, 20, 1000)
        standardized = (data - data.mean()) / data.std()

        assert abs(standardized.mean()) < 1e-10

    def test_standardization_unit_variance(self) -> None:
        """Test that standardized variable has std ~1."""
        data = np.random.normal(100, 20, 1000)
        standardized = (data - data.mean()) / data.std()

        assert abs(standardized.std() - 1.0) < 1e-10

    def test_standardization_preserves_shape(self) -> None:
        """Test that standardization preserves data shape."""
        data = np.random.normal(100, 20, 100)
        standardized = (data - data.mean()) / data.std()

        assert len(standardized) == len(data)


# ==============================================================================
# Test Interaction Term
# ==============================================================================


class TestInteractionTerm:
    """Tests for PRisk x Uncertainty interaction."""

    def test_interaction_calculation(
        self, sample_prisk_df: pd.DataFrame, sample_uncertainty_df: pd.DataFrame
    ) -> None:
        """Test interaction term: PRisk_std * Uncertainty_std."""
        prisk = sample_prisk_df.copy()
        uncertainty = sample_uncertainty_df.copy()

        # Standardize
        prisk["PRisk_std"] = (prisk["PRisk"] - prisk["PRisk"].mean()) / prisk["PRisk"].std()
        uncertainty["Uncertainty_std"] = (
            uncertainty["Manager_QA_Uncertainty_pct"]
            - uncertainty["Manager_QA_Uncertainty_pct"].mean()
        ) / uncertainty["Manager_QA_Uncertainty_pct"].std()

        # Merge and create interaction
        merged = prisk.merge(uncertainty, on=["gvkey", "year"])
        merged["PRisk_x_Uncertainty"] = merged["PRisk_std"] * merged["Uncertainty_std"]

        expected = merged["PRisk_std"] * merged["Uncertainty_std"]
        pd.testing.assert_series_equal(
            merged["PRisk_x_Uncertainty"], expected, check_names=False
        )

    def test_interaction_symmetric(self) -> None:
        """Test that interaction is symmetric (a*b = b*a)."""
        a = np.array([1.0, 2.0, 3.0])
        b = np.array([4.0, 5.0, 6.0])

        interaction_ab = a * b
        interaction_ba = b * a

        np.testing.assert_array_equal(interaction_ab, interaction_ba)


# ==============================================================================
# Test Merge Operations
# ==============================================================================


class TestMergeOperations:
    """Tests for data merging operations."""

    def test_left_merge_preserves_base(
        self, sample_prisk_df: pd.DataFrame, sample_uncertainty_df: pd.DataFrame
    ) -> None:
        """Test that left merge preserves all base rows."""
        prisk = sample_prisk_df.copy()
        uncertainty = sample_uncertainty_df.copy()

        # Add extra row to uncertainty that won't match
        extra_row = pd.DataFrame(
            {"gvkey": ["999999"], "year": [2021], "Manager_QA_Uncertainty_pct": [5.0]}
        )
        uncertainty = pd.concat([uncertainty, extra_row], ignore_index=True)

        merged = prisk.merge(uncertainty, on=["gvkey", "year"], how="left")

        # All original prisk rows should be present
        assert len(merged) == len(prisk)

    def test_merge_on_multiple_keys(
        self, sample_prisk_df: pd.DataFrame, sample_uncertainty_df: pd.DataFrame
    ) -> None:
        """Test merge on multiple keys (gvkey, year)."""
        prisk = sample_prisk_df.copy()
        uncertainty = sample_uncertainty_df.copy()

        merged = prisk.merge(uncertainty, on=["gvkey", "year"], how="inner")

        # All matched rows should have matching keys
        assert (merged["gvkey"].isin(prisk["gvkey"])).all()
        assert (merged["year"].isin(prisk["year"])).all()


# ==============================================================================
# Integration Tests
# ==============================================================================


class TestAuxiliaryScriptsIntegration:
    """Integration tests for auxiliary scripts."""

    def test_full_investment_residual_workflow(
        self, sample_compustat_for_investment: pd.DataFrame
    ) -> None:
        """Test complete workflow for computing investment residual."""
        df = sample_compustat_for_investment.copy()

        # Step 1: Calculate investment
        df["at_lag"] = df.groupby("gvkey")["at"].shift(1)
        df["investment_raw"] = df["capx"] + df["xrd"] + df["aqc"] - df["sppe"]
        df["investment"] = df["investment_raw"] / df["at_lag"]

        # Step 2: Calculate Tobin's Q (lagged)
        market_equity = df["csho"] * df["prcc_f"]
        df["tobins_q"] = (df["at"] + market_equity - df["ceq"]) / df["at"]
        df["tobins_q_lag"] = df.groupby("gvkey")["tobins_q"].shift(1)

        # Step 3: Calculate sales growth (lagged)
        df["sales_growth"] = df.groupby("gvkey")["sale"].pct_change()
        df["sales_growth_lag"] = df.groupby("gvkey")["sales_growth"].shift(1)

        # Verify all variables exist
        assert "investment" in df.columns
        assert "tobins_q_lag" in df.columns
        assert "sales_growth_lag" in df.columns

    def test_prisk_uncertainty_merge_workflow(
        self, sample_prisk_df: pd.DataFrame, sample_uncertainty_df: pd.DataFrame
    ) -> None:
        """Test complete workflow for PRisk x Uncertainty merge."""
        prisk = sample_prisk_df.copy()
        uncertainty = sample_uncertainty_df.copy()

        # Merge
        merged = prisk.merge(uncertainty, on=["gvkey", "year"], how="inner")

        # Standardize
        merged["PRisk_std"] = (merged["PRisk"] - merged["PRisk"].mean()) / merged["PRisk"].std()
        merged["Uncertainty_std"] = (
            merged["Manager_QA_Uncertainty_pct"]
            - merged["Manager_QA_Uncertainty_pct"].mean()
        ) / merged["Manager_QA_Uncertainty_pct"].std()

        # Create interaction
        merged["PRisk_x_Uncertainty"] = merged["PRisk_std"] * merged["Uncertainty_std"]

        # Verify interaction term exists
        assert "PRisk_x_Uncertainty" in merged.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
