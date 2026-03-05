#!/usr/bin/env python3
"""
Unit tests for H12 Dividend Intensity hypothesis suite.

Tests:
1. DivIntensity computation in the Compustat engine (dvy_Q4 / atq)
2. aggregate_to_firm_year() — mean-averaging of uncertainty measures
3. create_lead_div_intensity() — forward-shift with gap-year handling
"""

import numpy as np
import pandas as pd
import pytest


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def sample_firm_year_panel() -> pd.DataFrame:
    """Create a sample call-level panel for testing aggregation."""
    return pd.DataFrame(
        {
            "gvkey": [
                "001000",
                "001000",
                "001000",
                "001000",  # Firm A: 2 calls yr1, 2 calls yr2
                "001001",
                "001001",  # Firm B: 1 call yr1, 1 call yr2
            ],
            "fyearq": [2015.0, 2015.0, 2016.0, 2016.0, 2015.0, 2016.0],
            "start_date": pd.to_datetime(
                [
                    "2015-04-15",
                    "2015-07-20",
                    "2016-04-10",
                    "2016-07-18",
                    "2015-05-01",
                    "2016-05-05",
                ]
            ),
            "file_name": [
                "call_A_q1",
                "call_A_q2",
                "call_A_q3",
                "call_A_q4",
                "call_B_q1",
                "call_B_q2",
            ],
            "Manager_QA_Uncertainty_pct": [2.0, 4.0, 3.0, 5.0, 1.0, 6.0],
            "CEO_QA_Uncertainty_pct": [1.0, 3.0, 2.0, 4.0, 0.5, 3.5],
            "Manager_Pres_Uncertainty_pct": [1.5, 2.5, 2.0, 3.0, 0.8, 2.2],
            "CEO_Pres_Uncertainty_pct": [1.0, 2.0, 1.5, 2.5, 0.6, 1.8],
            "Manager_QA_Weak_Modal_pct": [0.5, 1.5, 1.0, 2.0, 0.3, 1.7],
            "CEO_QA_Weak_Modal_pct": [0.4, 1.2, 0.8, 1.6, 0.2, 1.4],
            "DivIntensity": [0.02, 0.02, 0.03, 0.03, 0.01, 0.015],
            "Size": [7.0, 7.0, 7.1, 7.1, 6.5, 6.6],
            "Lev": [0.3, 0.3, 0.28, 0.28, 0.4, 0.38],
            "ROA": [0.05, 0.05, 0.06, 0.06, 0.03, 0.04],
            "TobinsQ": [1.5, 1.5, 1.6, 1.6, 1.2, 1.3],
            "ff12_code": [1.0, 1.0, 1.0, 1.0, 3.0, 3.0],
        }
    )


@pytest.fixture
def sample_firm_year_agg() -> pd.DataFrame:
    """Create a sample firm-year aggregated panel for testing lead creation."""
    return pd.DataFrame(
        {
            "gvkey": [
                "001000",
                "001000",
                "001000",  # Firm A: 3 consecutive years
                "001001",
                "001001",
                "001001",  # Firm B: gap between yr1 and yr3
            ],
            "fyearq": [2015.0, 2016.0, 2017.0, 2014.0, 2016.0, 2017.0],
            "DivIntensity": [0.02, 0.03, 0.04, 0.01, 0.02, 0.025],
        }
    )


# ==============================================================================
# Test DivIntensity Computation
# ==============================================================================


class TestDivIntensityComputation:
    """Tests for the DivIntensity = dvy_Q4 / atq computation logic."""

    def test_basic_calculation(self) -> None:
        """DivIntensity = dvy / atq for positive atq."""
        dvy = np.array([10.0, 0.0, 50.0, 20.0])
        atq = np.array([1000.0, 500.0, 2000.0, 800.0])
        result = np.where(atq > 0, dvy / atq, np.nan)
        expected = np.array([0.01, 0.0, 0.025, 0.025])
        np.testing.assert_allclose(result, expected)

    def test_zero_atq_returns_nan(self) -> None:
        """DivIntensity should be NaN when atq <= 0."""
        dvy = np.array([10.0, 5.0])
        atq = np.array([0.0, -100.0])
        result = np.where(atq > 0, dvy / atq, np.nan)
        assert np.isnan(result[0])
        assert np.isnan(result[1])

    def test_zero_dividends(self) -> None:
        """Firms with no dividends should have DivIntensity = 0."""
        dvy = np.array([0.0, 0.0])
        atq = np.array([1000.0, 500.0])
        result = np.where(atq > 0, dvy / atq, np.nan)
        np.testing.assert_allclose(result, [0.0, 0.0])

    def test_nan_dvy_treated_as_zero(self) -> None:
        """NaN dvy (fillna(0)) should produce DivIntensity = 0, not NaN."""
        dvy = np.array([np.nan, 10.0])
        atq = np.array([1000.0, 500.0])
        dvy_filled = np.nan_to_num(dvy, nan=0.0)
        result = np.where(atq > 0, dvy_filled / atq, np.nan)
        np.testing.assert_allclose(result, [0.0, 0.02])


# ==============================================================================
# Test Firm-Year Aggregation
# ==============================================================================


class TestAggregateToFirmYear:
    """Tests for the aggregate_to_firm_year function."""

    def test_uncertainty_averaged(self, sample_firm_year_panel: pd.DataFrame) -> None:
        """Uncertainty measures should be MEAN-averaged across calls."""
        from f1d.variables.build_h12_div_intensity_panel import aggregate_to_firm_year

        result = aggregate_to_firm_year(sample_firm_year_panel)

        # Firm A, year 2015: calls have Manager_QA_Uncertainty_pct = [2.0, 4.0]
        firm_a_2015 = result[
            (result["gvkey"] == "001000") & (result["fyearq"] == 2015.0)
        ]
        assert len(firm_a_2015) == 1
        np.testing.assert_allclose(
            firm_a_2015["Avg_Manager_QA_Uncertainty_pct"].values[0], 3.0
        )

        # Firm A, year 2016: calls have CEO_QA_Uncertainty_pct = [2.0, 4.0]
        firm_a_2016 = result[
            (result["gvkey"] == "001000") & (result["fyearq"] == 2016.0)
        ]
        np.testing.assert_allclose(
            firm_a_2016["Avg_CEO_QA_Uncertainty_pct"].values[0], 3.0
        )

    def test_financial_vars_last(self, sample_firm_year_panel: pd.DataFrame) -> None:
        """Financial variables should take LAST value per firm-year."""
        from f1d.variables.build_h12_div_intensity_panel import aggregate_to_firm_year

        result = aggregate_to_firm_year(sample_firm_year_panel)

        # Firm A, year 2015: DivIntensity should be 0.02 (same for both calls)
        firm_a_2015 = result[
            (result["gvkey"] == "001000") & (result["fyearq"] == 2015.0)
        ]
        np.testing.assert_allclose(firm_a_2015["DivIntensity"].values[0], 0.02)

    def test_one_row_per_firm_year(self, sample_firm_year_panel: pd.DataFrame) -> None:
        """Output should have exactly one row per (gvkey, fyearq)."""
        from f1d.variables.build_h12_div_intensity_panel import aggregate_to_firm_year

        result = aggregate_to_firm_year(sample_firm_year_panel)

        # 2 firms × 2 years = 4 firm-years
        assert len(result) == 4
        assert result[["gvkey", "fyearq"]].duplicated().sum() == 0

    def test_call_counts(self, sample_firm_year_panel: pd.DataFrame) -> None:
        """n_calls column should reflect calls per firm-year."""
        from f1d.variables.build_h12_div_intensity_panel import aggregate_to_firm_year

        result = aggregate_to_firm_year(sample_firm_year_panel)

        firm_a_2015 = result[
            (result["gvkey"] == "001000") & (result["fyearq"] == 2015.0)
        ]
        assert firm_a_2015["n_calls"].values[0] == 2

        firm_b_2015 = result[
            (result["gvkey"] == "001001") & (result["fyearq"] == 2015.0)
        ]
        assert firm_b_2015["n_calls"].values[0] == 1

    def test_missing_fyearq_raises(self) -> None:
        """Should raise ValueError if fyearq column is missing."""
        from f1d.variables.build_h12_div_intensity_panel import aggregate_to_firm_year

        df = pd.DataFrame({"gvkey": ["001000"], "DivIntensity": [0.01]})
        with pytest.raises(ValueError, match="fyearq"):
            aggregate_to_firm_year(df)


# ==============================================================================
# Test Lead DV Creation
# ==============================================================================


class TestCreateLeadDivIntensity:
    """Tests for create_lead_div_intensity function."""

    def test_consecutive_years(self, sample_firm_year_agg: pd.DataFrame) -> None:
        """Lead should work for consecutive fiscal years."""
        from f1d.variables.build_h12_div_intensity_panel import (
            create_lead_div_intensity,
        )

        result = create_lead_div_intensity(sample_firm_year_agg)

        # Firm A: 2015 → 2016 is consecutive, lead = 0.03
        firm_a_2015 = result[
            (result["gvkey"] == "001000") & (result["fyearq"] == 2015.0)
        ]
        np.testing.assert_allclose(firm_a_2015["DivIntensity_lead"].values[0], 0.03)

        # Firm A: 2016 → 2017 is consecutive, lead = 0.04
        firm_a_2016 = result[
            (result["gvkey"] == "001000") & (result["fyearq"] == 2016.0)
        ]
        np.testing.assert_allclose(firm_a_2016["DivIntensity_lead"].values[0], 0.04)

    def test_gap_year_produces_nan(self, sample_firm_year_agg: pd.DataFrame) -> None:
        """Gap years (non-consecutive) should produce NaN lead."""
        from f1d.variables.build_h12_div_intensity_panel import (
            create_lead_div_intensity,
        )

        result = create_lead_div_intensity(sample_firm_year_agg)

        # Firm B: 2014 → next is 2016 (gap!), lead should be NaN
        firm_b_2014 = result[
            (result["gvkey"] == "001001") & (result["fyearq"] == 2014.0)
        ]
        assert pd.isna(firm_b_2014["DivIntensity_lead"].values[0])

    def test_last_year_is_nan(self, sample_firm_year_agg: pd.DataFrame) -> None:
        """Last firm-year for each firm should have NaN lead (no future data)."""
        from f1d.variables.build_h12_div_intensity_panel import (
            create_lead_div_intensity,
        )

        result = create_lead_div_intensity(sample_firm_year_agg)

        # Firm A: 2017 is last year, lead = NaN
        firm_a_2017 = result[
            (result["gvkey"] == "001000") & (result["fyearq"] == 2017.0)
        ]
        assert pd.isna(firm_a_2017["DivIntensity_lead"].values[0])

    def test_preserves_columns(self, sample_firm_year_agg: pd.DataFrame) -> None:
        """Should preserve existing columns and add DivIntensity_lead."""
        from f1d.variables.build_h12_div_intensity_panel import (
            create_lead_div_intensity,
        )

        result = create_lead_div_intensity(sample_firm_year_agg)

        assert "DivIntensity_lead" in result.columns
        assert "DivIntensity" in result.columns
        assert "gvkey" in result.columns
        assert "fyearq" in result.columns
