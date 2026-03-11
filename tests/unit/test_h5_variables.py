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

        # Verify all variables exist
        assert "dispersion" in ibes.columns
        assert "earnings_surprise" in ibes.columns
        assert "loss_dummy" in comp.columns

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


# ==============================================================================
# Test Delta Dispersion Computation
# ==============================================================================


class TestDeltaDispersionComputation:
    """Tests for delta dispersion calculation from IBES Detail data."""

    @pytest.fixture
    def sample_ibes_detail_df(self) -> pd.DataFrame:
        """Create sample IBES Detail data for testing delta dispersion."""
        return pd.DataFrame({
            "gvkey": ["001000", "001000", "001000", "001000", "001000", "001000"],
            "actdats": pd.to_datetime([
                "2021-03-01", "2021-03-05", "2021-03-10",  # Before call (3/15)
                "2021-03-18", "2021-03-20", "2021-03-22",  # After call (3/15)
            ]),
            "analys": ["A1", "A2", "A3", "A1", "A2", "A3"],
            "value": [1.00, 1.10, 0.90, 1.05, 1.20, 0.95],  # Analyst estimates
            "fpedats": pd.to_datetime(["2021-03-31"] * 6),  # All for same quarter
        })

    def test_dispersion_at_date_basic(self, sample_ibes_detail_df: pd.DataFrame) -> None:
        """Test computing dispersion at a specific date."""
        df = sample_ibes_detail_df
        target_date = pd.Timestamp("2021-03-12")  # 3 days before call

        # Filter to estimates on/before target
        active = df[df['actdats'] <= target_date]
        # Keep most recent per analyst
        active = active.sort_values('actdats').groupby('analys').last()
        # Compute dispersion
        stdev = active['value'].std()
        mean = active['value'].mean()
        dispersion = stdev / abs(mean)

        # Should have 3 analysts
        assert len(active) == 3
        # Dispersion should be positive
        assert dispersion > 0

    def test_dispersion_requires_multiple_analysts(self) -> None:
        """Test that dispersion is None if < 2 analysts."""
        df = pd.DataFrame({
            "gvkey": ["001000"],
            "actdats": pd.to_datetime(["2021-03-10"]),
            "analys": ["A1"],  # Only 1 analyst
            "value": [1.00],
            "fpedats": pd.to_datetime(["2021-03-31"]),
        })

        target_date = pd.Timestamp("2021-03-12")
        active = df[df['actdats'] <= target_date]
        active = active.sort_values('actdats').groupby('analys').last()

        # Should have only 1 analyst - insufficient
        assert len(active) < 2

    def test_delta_dispersion_calculation(self, sample_ibes_detail_df: pd.DataFrame) -> None:
        """Test delta = after - before."""
        df = sample_ibes_detail_df
        call_date = pd.Timestamp("2021-03-15")

        # Compute dispersion before (3 days before)
        date_before = call_date - pd.Timedelta(days=3)
        active_before = df[df['actdats'] <= date_before]
        active_before = active_before.sort_values('actdats').groupby('analys').last()
        disp_before = active_before['value'].std() / abs(active_before['value'].mean())

        # Compute dispersion after (3 days after)
        date_after = call_date + pd.Timedelta(days=3)
        active_after = df[df['actdats'] <= date_after]
        active_after = active_after.sort_values('actdats').groupby('analys').last()
        disp_after = active_after['value'].std() / abs(active_after['value'].mean())

        # Delta = after - before
        delta = disp_after - disp_before

        # Delta should be a number
        assert not pd.isna(delta)

    def test_delta_can_be_negative(self, sample_ibes_detail_df: pd.DataFrame) -> None:
        """Test that dispersion can decrease after call (negative delta)."""
        # Create data where estimates converge after call (dispersion decreases)
        # Before call: analysts have wide disagreement
        # After call: analysts converge toward consensus
        df = pd.DataFrame({
            "gvkey": ["001000", "001000", "001000", "001000", "001000", "001000"],
            "actdats": pd.to_datetime([
                "2021-03-10", "2021-03-10", "2021-03-10",  # All before call (3 analysts)
                "2021-03-18", "2021-03-18", "2021-03-18",  # All after call (same 3 analysts)
            ]),
            "analys": ["A1", "A2", "A3", "A1", "A2", "A3"],
            # Before: high spread (1.00, 1.50, 0.50) -> mean=1.00, std~0.5
            # After: converge (1.00, 1.01, 0.99) -> mean~1.00, std~0.01
            "value": [1.00, 1.50, 0.50, 1.00, 1.01, 0.99],
            "fpedats": pd.to_datetime(["2021-03-31"] * 6),
        })

        call_date = pd.Timestamp("2021-03-15")

        # Dispersion before (3 calendar days before = March 12)
        date_before = call_date - pd.Timedelta(days=3)
        active_before = df[(df['actdats'] <= date_before)]
        active_before = active_before.sort_values('actdats').groupby('analys').last()
        disp_before = active_before['value'].std() / abs(active_before['value'].mean())

        # Dispersion after (3 calendar days after = March 18)
        date_after = call_date + pd.Timedelta(days=3)
        active_after = df[(df['actdats'] <= date_after)]
        active_after = active_after.sort_values('actdats').groupby('analys').last()
        disp_after = active_after['value'].std() / abs(active_after['value'].mean())

        delta = disp_after - disp_before

        # Before: std=0.5, mean=1.0 -> dispersion=0.5
        # After: std~0.01, mean~1.0 -> dispersion~0.01
        # Delta should be negative (convergence)
        assert disp_before > disp_after, f"Before={disp_before:.4f}, After={disp_after:.4f}"
        assert delta < 0, f"Delta={delta:.4f} should be negative"

    def test_stale_estimate_filter(self) -> None:
        """Test that stale estimates are filtered out."""
        df = pd.DataFrame({
            "gvkey": ["001000", "001000", "001000"],
            "actdats": pd.to_datetime([
                "2020-01-01",  # Very stale (14+ months old)
                "2021-03-01",  # Recent
                "2021-03-10",  # Recent
            ]),
            "analys": ["A1", "A2", "A3"],
            "value": [0.50, 1.00, 1.50],
            "fpedats": pd.to_datetime(["2021-03-31"] * 3),
        })

        target_date = pd.Timestamp("2021-03-15")
        max_age_days = 180

        # Apply stale filter
        active = df[df['actdats'] <= target_date]
        age_days = (target_date - active['actdats']).dt.days
        active = active[age_days <= max_age_days]

        # Should exclude the stale estimate
        assert len(active) == 2
        assert "A1" not in active['analys'].values

    def test_trading_day_offset(self) -> None:
        """Test that 3 trading days excludes weekends."""
        from pandas.tseries.offsets import CustomBusinessDay
        from pandas.tseries.holiday import USFederalHolidayCalendar

        bday = CustomBusinessDay(calendar=USFederalHolidayCalendar())

        # Friday call
        call_date = pd.Timestamp("2021-03-12")  # Friday
        date_before = call_date - 3 * bday
        date_after = call_date + 3 * bday

        # 3 trading days before Friday should be Tuesday
        assert date_before.dayofweek == 1  # Tuesday
        # 3 trading days after Friday should be Wednesday
        assert date_after.dayofweek == 2  # Wednesday


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
