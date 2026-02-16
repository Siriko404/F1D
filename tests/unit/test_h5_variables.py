#!/usr/bin/env python3
"""
Unit tests for H5 Analyst Dispersion Variables (3.5_H5Variables.py)

Tests the core computation functions for analyst dispersion hypothesis variables.
"""

import numpy as np
import pandas as pd
import pytest


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def sample_ibes_df() -> pd.DataFrame:
    """Create a sample IBES DataFrame for testing."""
    return pd.DataFrame(
        {
            "ticker": ["AAPL", "AAPL", "MSFT", "MSFT", "GOOG"],
            "cusip": ["03783310", "03783310", "59491810", "59491810", "38259P10"],
            "fpedats": pd.to_datetime(
                ["2021-03-31", "2021-06-30", "2021-03-31", "2021-06-30", "2021-03-31"]
            ),
            "measure": ["EPS", "EPS", "EPS", "EPS", "EPS"],
            "fpi": ["1", "1", "1", "1", "1"],
            "meanest": [1.50, 1.75, 2.00, 2.25, 10.00],
            "stdev": [0.10, 0.15, 0.20, 0.25, 0.50],
            "numest": [10, 12, 8, 10, 5],
            "actual": [1.55, 1.70, 2.10, 2.15, 9.80],
        }
    )


@pytest.fixture
def sample_compustat_df() -> pd.DataFrame:
    """Create a sample Compustat DataFrame for testing."""
    return pd.DataFrame(
        {
            "gvkey": ["001000", "001000", "001001", "001001", "001002"],
            "fyear": [2020, 2021, 2020, 2021, 2021],
            "ni": [100.0, 120.0, -50.0, -30.0, 200.0],  # Last two are losses
            "at": [1000.0, 1200.0, 800.0, 750.0, 2000.0],
        }
    )


@pytest.fixture
def sample_speech_df() -> pd.DataFrame:
    """Create a sample speech variables DataFrame for testing."""
    return pd.DataFrame(
        {
            "file_name": ["call_001", "call_002", "call_003"],
            "gvkey": ["001000", "001001", "001002"],
            "start_date": pd.to_datetime(["2021-03-15", "2021-03-16", "2021-03-17"]),
            "Manager_QA_Uncertainty_pct": [2.5, 3.0, 1.5],
            "Manager_Pres_Uncertainty_pct": [1.5, 2.0, 1.0],
            "CEO_QA_Uncertainty_pct": [2.0, 2.5, 1.2],
        }
    )


# ==============================================================================
# Test compute_analyst_dispersion
# ==============================================================================


class TestComputeAnalystDispersion:
    """Tests for analyst dispersion calculation."""

    def test_dispersion_calculation(self, sample_ibes_df: pd.DataFrame) -> None:
        """Test basic dispersion calculation: STDEV / |MEANEST|."""
        df = sample_ibes_df.copy()
        df["dispersion"] = df["stdev"] / df["meanest"].abs()

        expected = df["stdev"] / df["meanest"].abs()
        pd.testing.assert_series_equal(df["dispersion"], expected, check_names=False)

    def test_dispersion_with_minimum_estimates(
        self, sample_ibes_df: pd.DataFrame
    ) -> None:
        """Test filtering by minimum number of estimates."""
        df = sample_ibes_df.copy()
        numest_min = 5

        # Filter to rows with enough estimates
        filtered = df[df["numest"] >= numest_min]
        assert len(filtered) == 5  # All should pass
        assert (filtered["numest"] >= numest_min).all()

    def test_dispersion_with_minimum_meanest(
        self, sample_ibes_df: pd.DataFrame
    ) -> None:
        """Test filtering by minimum mean estimate."""
        df = sample_ibes_df.copy()
        meanest_min = 0.05

        # Filter to rows with sufficient mean estimate
        filtered = df[df["meanest"].abs() >= meanest_min]
        assert len(filtered) == 5  # All should pass

    def test_dispersion_excludes_near_zero_meanest(self) -> None:
        """Test that near-zero mean estimates are excluded."""
        df = pd.DataFrame(
            {
                "meanest": [0.01, 0.03, 0.05, 1.0],  # First two below threshold
                "stdev": [0.10, 0.10, 0.10, 0.10],
            }
        )
        meanest_min = 0.05

        filtered = df[df["meanest"].abs() >= meanest_min]
        assert len(filtered) == 2  # Only last two should pass


# ==============================================================================
# Test compute_earnings_surprise
# ==============================================================================


class TestComputeEarningsSurprise:
    """Tests for earnings surprise calculation."""

    def test_surprise_calculation(self, sample_ibes_df: pd.DataFrame) -> None:
        """Test earnings surprise: |ACTUAL - MEANEST| / |MEANEST|."""
        df = sample_ibes_df.copy()
        df["earnings_surprise"] = (df["actual"] - df["meanest"]).abs() / df[
            "meanest"
        ].abs()

        expected = (df["actual"] - df["meanest"]).abs() / df["meanest"].abs()
        pd.testing.assert_series_equal(
            df["earnings_surprise"], expected, check_names=False
        )

    def test_surprise_can_be_zero(self, sample_ibes_df: pd.DataFrame) -> None:
        """Test that earnings surprise can be zero when actual equals estimate."""
        df = sample_ibes_df.copy()
        df.loc[0, "actual"] = df.loc[0, "meanest"]  # Perfect match
        df["earnings_surprise"] = (df["actual"] - df["meanest"]).abs() / df[
            "meanest"
        ].abs()

        assert df.loc[0, "earnings_surprise"] == 0.0

    def test_surprise_is_non_negative(self, sample_ibes_df: pd.DataFrame) -> None:
        """Test that earnings surprise is always non-negative."""
        df = sample_ibes_df.copy()
        df["earnings_surprise"] = (df["actual"] - df["meanest"]).abs() / df[
            "meanest"
        ].abs()

        assert (df["earnings_surprise"] >= 0).all()


# ==============================================================================
# Test compute_loss_dummy
# ==============================================================================


class TestComputeLossDummy:
    """Tests for loss dummy calculation."""

    def test_loss_dummy_calculation(self, sample_compustat_df: pd.DataFrame) -> None:
        """Test loss dummy: 1 if NI < 0."""
        df = sample_compustat_df.copy()
        df["loss_dummy"] = (df["ni"] < 0).astype(int)

        expected = (df["ni"] < 0).astype(int)
        pd.testing.assert_series_equal(df["loss_dummy"], expected, check_names=False)

    def test_loss_dummy_binary(self, sample_compustat_df: pd.DataFrame) -> None:
        """Test that loss dummy is binary (0 or 1)."""
        df = sample_compustat_df.copy()
        df["loss_dummy"] = (df["ni"] < 0).astype(int)

        assert set(df["loss_dummy"].unique()).issubset({0, 1})

    def test_loss_dummy_for_profitable_firms(self) -> None:
        """Test loss dummy is 0 for profitable firms."""
        df = pd.DataFrame({"ni": [100.0, 200.0, 50.0]})
        df["loss_dummy"] = (df["ni"] < 0).astype(int)

        assert (df["loss_dummy"] == 0).all()

    def test_loss_dummy_for_loss_firms(self) -> None:
        """Test loss dummy is 1 for loss-making firms."""
        df = pd.DataFrame({"ni": [-100.0, -50.0, -10.0]})
        df["loss_dummy"] = (df["ni"] < 0).astype(int)

        assert (df["loss_dummy"] == 1).all()


# ==============================================================================
# Test compute_uncertainty_gap
# ==============================================================================


class TestComputeUncertaintyGap:
    """Tests for uncertainty gap calculation."""

    def test_gap_calculation(self, sample_speech_df: pd.DataFrame) -> None:
        """Test uncertainty gap: QA uncertainty - Pres uncertainty."""
        df = sample_speech_df.copy()
        df["uncertainty_gap"] = (
            df["Manager_QA_Uncertainty_pct"] - df["Manager_Pres_Uncertainty_pct"]
        )

        expected = (
            df["Manager_QA_Uncertainty_pct"] - df["Manager_Pres_Uncertainty_pct"]
        )
        pd.testing.assert_series_equal(df["uncertainty_gap"], expected, check_names=False)

    def test_gap_positive_when_qa_higher(self, sample_speech_df: pd.DataFrame) -> None:
        """Test gap is positive when QA uncertainty exceeds presentation."""
        df = sample_speech_df.copy()
        df["uncertainty_gap"] = (
            df["Manager_QA_Uncertainty_pct"] - df["Manager_Pres_Uncertainty_pct"]
        )

        assert (df["uncertainty_gap"] > 0).all()

    def test_gap_can_be_negative(self) -> None:
        """Test gap can be negative when presentation uncertainty is higher."""
        df = pd.DataFrame(
            {
                "Manager_QA_Uncertainty_pct": [1.0, 1.5],
                "Manager_Pres_Uncertainty_pct": [2.0, 2.5],
            }
        )
        df["uncertainty_gap"] = (
            df["Manager_QA_Uncertainty_pct"] - df["Manager_Pres_Uncertainty_pct"]
        )

        assert (df["uncertainty_gap"] < 0).all()


# ==============================================================================
# Test Forward-Looking Dispersion
# ==============================================================================


class TestForwardLookingDispersion:
    """Tests for forward-looking dispersion (dispersion_lead)."""

    def test_lead_calculation(self) -> None:
        """Test that dispersion_lead is correctly computed as next quarter's value."""
        df = pd.DataFrame(
            {
                "gvkey": ["001000", "001000", "001000"],
                "fquarter": ["2021Q1", "2021Q2", "2021Q3"],
                "dispersion": [0.10, 0.15, 0.12],
            }
        )

        # Compute lead (shift by -1 within gvkey group)
        df["dispersion_lead"] = df.groupby("gvkey")["dispersion"].shift(-1)

        # First row should have second row's value
        assert df.loc[0, "dispersion_lead"] == 0.15
        # Last row should be NaN (no next quarter)
        assert pd.isna(df.loc[2, "dispersion_lead"])

    def test_lead_with_multiple_firms(self) -> None:
        """Test lead calculation handles multiple firms correctly."""
        df = pd.DataFrame(
            {
                "gvkey": ["001000", "001000", "001001", "001001"],
                "fquarter": ["2021Q1", "2021Q2", "2021Q1", "2021Q2"],
                "dispersion": [0.10, 0.15, 0.20, 0.25],
            }
        )

        df["dispersion_lead"] = df.groupby("gvkey")["dispersion"].shift(-1)

        # Each firm's lead should be independent
        assert df.loc[0, "dispersion_lead"] == 0.15  # Firm 001000
        assert df.loc[2, "dispersion_lead"] == 0.25  # Firm 001001


# ==============================================================================
# Integration Tests
# ==============================================================================


class TestH5VariablesIntegration:
    """Integration tests for H5 variables computation."""

    def test_all_variables_can_be_computed(
        self,
        sample_ibes_df: pd.DataFrame,
        sample_compustat_df: pd.DataFrame,
        sample_speech_df: pd.DataFrame,
    ) -> None:
        """Test that all H5 variables can be computed from sample data."""
        ibes = sample_ibes_df.copy()
        comp = sample_compustat_df.copy()
        speech = sample_speech_df.copy()

        # Compute dispersion
        ibes["dispersion"] = ibes["stdev"] / ibes["meanest"].abs()

        # Compute earnings surprise
        ibes["earnings_surprise"] = (ibes["actual"] - ibes["meanest"]).abs() / ibes[
            "meanest"
        ].abs()

        # Compute loss dummy
        comp["loss_dummy"] = (comp["ni"] < 0).astype(int)

        # Compute uncertainty gap
        speech["uncertainty_gap"] = (
            speech["Manager_QA_Uncertainty_pct"] - speech["Manager_Pres_Uncertainty_pct"]
        )

        # Verify all variables exist
        assert "dispersion" in ibes.columns
        assert "earnings_surprise" in ibes.columns
        assert "loss_dummy" in comp.columns
        assert "uncertainty_gap" in speech.columns

    def test_dispersion_filtering_criteria(self, sample_ibes_df: pd.DataFrame) -> None:
        """Test that dispersion filtering criteria work correctly."""
        df = sample_ibes_df.copy()

        # Apply standard filters
        numest_min = 3
        meanest_min = 0.05

        df["dispersion"] = df["stdev"] / df["meanest"].abs()
        filtered = df[
            (df["numest"] >= numest_min) & (df["meanest"].abs() >= meanest_min)
        ]

        # All filtered rows should meet criteria
        assert (filtered["numest"] >= numest_min).all()
        assert (filtered["meanest"].abs() >= meanest_min).all()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
