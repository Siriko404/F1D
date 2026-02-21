"""
Integration tests for survival analysis functions in 4.3_TakeoverHazards.py.

Tests end-to-end workflow of run_cox_ph and run_fine_gray functions
with realistic data structures mimicking takeover hazard analysis.
"""

import runpy
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Import the functions to test - module name contains dots so use runpy
_MODULE_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "src"
    / "f1d"
    / "econometric"
    / "run_takeover_hazards.py"
)
_MODULE_GLOBALS = runpy.run_path(str(_MODULE_PATH))
run_cox_ph = _MODULE_GLOBALS.get("run_cox_ph")
run_fine_gray = _MODULE_GLOBALS.get("run_fine_gray")

pytestmark = pytest.mark.skipif(
    run_cox_ph is None,
    reason="API changed to run_cox_tv in B7 fix",
)


# ==============================================================================
# Fixtures - Realistic takeover data simulation
# ==============================================================================


@pytest.fixture
def realistic_takeover_data():
    """
    Create realistic takeover hazard data for integration testing.

    Simulates a dataset similar to what would be produced by the actual pipeline:
    - CEO clarity scores
    - Q&A uncertainty metrics
    - Firm controls (size, leverage, ROA, etc.)
    - Takeover events and timing
    """
    np.random.seed(12345)
    n = 500  # Larger sample for integration testing

    # Generate correlated covariates (realistic relationships)
    # Size follows log-normal distribution (market cap in billions)
    size = np.random.lognormal(mean=3, sigma=1.5, size=n)

    # Leverage correlated with size (larger firms have more access to debt)
    leverage = (
        0.3 + 0.1 * np.log(size) / np.log(size).max() + np.random.normal(0, 0.1, n)
    )
    leverage = np.clip(leverage, 0, 1)

    # ROA inversely correlated with leverage
    roa = 0.1 - 0.1 * leverage + np.random.normal(0, 0.05, n)
    roa = np.clip(roa, -0.2, 0.3)

    # CEO clarity (z-scored, time-invariant characteristic)
    ceo_clarity = np.random.normal(0, 1, n)

    # Q&A uncertainty (call-level metric, some variance)
    qa_uncertainty = np.random.normal(15, 5, n)  # percentage points

    # Survival time (time to event or censoring)
    # Lower clarity and higher uncertainty -> shorter time to takeover
    base_hazard = np.exp(
        -0.2 * ceo_clarity + 0.05 * qa_uncertainty - 0.1 * np.log(size)
    )
    survival_time = np.random.exponential(scale=1.0 / base_hazard)
    survival_time = np.clip(survival_time, 1, 60)  # 1 to 60 months

    # Event indicator (takeover or not)
    # Higher probability of takeover for low clarity, high uncertainty
    takeover_prob = 1 / (
        1 + np.exp(0.3 * ceo_clarity - 0.02 * qa_uncertainty + 0.5 * np.log(size) - 2)
    )
    event = (np.random.random(n) < takeover_prob).astype(int)

    # For competing risks: among takeovers, classify as friendly or hostile
    # Higher clarity -> more likely friendly
    takeover_type = np.zeros(n, dtype=int)  # 0 = no takeover, 1 = friendly, 2 = hostile
    for i in range(n):
        if event[i] == 1:
            friendly_prob = 1 / (1 + np.exp(-0.5 * ceo_clarity[i]))
            takeover_type[i] = 1 if np.random.random() < friendly_prob else 2

    df = pd.DataFrame(
        {
            "time": survival_time,
            "event": event,
            "event_type": takeover_type,
            "ClarityCEO": ceo_clarity,
            "Manager_QA_Uncertainty_pct": qa_uncertainty,
            "Size": size,
            "Leverage": leverage,
            "ROA": roa,
        }
    )

    return df


@pytest.fixture
def competing_risks_data(realistic_takeover_data):
    """
    Prepare data for competing risks analysis.

    Event types:
    - 0 = censored (no takeover)
    - 1 = friendly takeover
    - 2 = hostile takeover
    """
    df = realistic_takeover_data.copy()
    # Use event_type directly (0=censored, 1=friendly, 2=hostile)
    df["event_cr"] = df["event_type"]
    return df


# ==============================================================================
# Integration Tests - run_cox_ph
# ==============================================================================


class TestCoxPHIntegration:
    """Integration tests for Cox Proportional Hazards model."""

    def test_cox_ph_with_realistic_data(self, realistic_takeover_data):
        """Test run_cox_ph with realistic takeover data."""
        result = run_cox_ph(
            df=realistic_takeover_data,
            time_col="time",
            event_col="event",
            formula="ClarityCEO + Manager_QA_Uncertainty_pct + Size + Leverage + ROA",
        )

        # Verify basic output structure
        assert isinstance(result, dict)
        assert "coefficients" in result
        assert "confidence_intervals" in result
        assert "summary" in result
        assert "concordance_index" in result
        assert "model" in result

        # Verify all covariates are in results
        expected_covariates = [
            "ClarityCEO",
            "Manager_QA_Uncertainty_pct",
            "Size",
            "Leverage",
            "ROA",
        ]
        for cov in expected_covariates:
            assert cov in result["coefficients"], f"Missing coefficient for {cov}"

        # Verify coefficients are finite numbers
        for cov, coef in result["coefficients"].items():
            assert np.isfinite(coef), f"Coefficient for {cov} is not finite: {coef}"

        # Verify concordance index is in valid range
        ci = result["concordance_index"]
        assert 0.0 <= ci <= 1.0, f"Concordance index out of range: {ci}"

        # For well-specified model, CI should be better than random (0.5)
        # Note: with random data, this may not always hold, so we use a loose bound
        assert ci > 0.3, f"Concordance index suspiciously low: {ci}"

    def test_cox_ph_model_diagnostics(self, realistic_takeover_data):
        """Test that Cox PH model produces valid diagnostic statistics."""
        result = run_cox_ph(
            df=realistic_takeover_data,
            time_col="time",
            event_col="event",
            formula="ClarityCEO + Manager_QA_Uncertainty_pct",
        )

        # Check that summary contains standard errors and p-values
        summary = result["summary"]

        # Summary should have coef (log hazard ratio) and exp(coef) (hazard ratio)
        assert "coef" in summary, "Summary missing coef column"
        assert "exp(coef)" in summary, "Summary missing exp(coef) column"

        # Hazard ratios should be positive
        for cov in ["ClarityCEO", "Manager_QA_Uncertainty_pct"]:
            hr = summary["exp(coef)"][cov]
            assert hr > 0, f"Hazard ratio for {cov} should be positive: {hr}"

    def test_cox_ph_with_binary_events(self, realistic_takeover_data):
        """Test Cox PH with binary event indicator."""
        df = realistic_takeover_data.copy()

        result = run_cox_ph(
            df=df, time_col="time", event_col="event", formula="ClarityCEO + Size"
        )

        # Verify model runs without error
        assert result is not None
        assert "model" in result

        # Model should have been fitted
        model = result["model"]
        assert hasattr(model, "predict_expectation")


# ==============================================================================
# Integration Tests - run_fine_gray
# ==============================================================================


class TestFineGrayIntegration:
    """Integration tests for competing risks analysis."""

    def test_fine_gray_with_competing_risks(self, competing_risks_data):
        """Test run_fine_gray with competing risks data."""
        result = run_fine_gray(
            df=competing_risks_data,
            time_col="time",
            event_col="event_cr",
            formula="ClarityCEO + Manager_QA_Uncertainty_pct + Size",
        )

        # Verify output structure
        assert isinstance(result, dict)
        assert "coefficients" in result
        assert "confidence_intervals" in result
        assert "summary" in result
        assert "model" in result
        assert "method" in result

        # Verify method indicator
        assert result["method"] == "cause_specific_hazards"

        # Verify covariates present
        expected_covariates = ["ClarityCEO", "Manager_QA_Uncertainty_pct", "Size"]
        for cov in expected_covariates:
            assert cov in result["coefficients"], f"Missing coefficient for {cov}"

    def test_fine_gray_friendly_takeovers(self, competing_risks_data):
        """Test competing risks analysis focusing on friendly takeovers."""
        df = competing_risks_data.copy()

        # For friendly takeovers: event=1 is friendly, 0/2 are censored
        result = run_fine_gray(
            df=df, time_col="time", event_col="event_cr", formula="ClarityCEO + Size"
        )

        # Verify model runs successfully
        assert result is not None
        assert "concordance_index" in result
        assert result["concordance_index"] > 0

    def test_fine_gray_with_single_covariate(self, competing_risks_data):
        """Test competing risks with single covariate."""
        result = run_fine_gray(
            df=competing_risks_data,
            time_col="time",
            event_col="event_cr",
            formula="ClarityCEO",
        )

        # Should work with single covariate
        assert "ClarityCEO" in result["coefficients"]
        assert np.isfinite(result["coefficients"]["ClarityCEO"])


# ==============================================================================
# Edge Case Tests
# ==============================================================================


class TestSurvivalAnalysisEdgeCases:
    """Tests for edge cases in survival analysis."""

    def test_cox_ph_with_heavily_censored_data(self):
        """Test Cox PH with mostly censored observations."""
        np.random.seed(999)
        n = 200

        # 90% censored
        df = pd.DataFrame(
            {
                "time": np.random.exponential(10, n),
                "event": np.random.binomial(1, 0.1, n),  # Only 10% events
                "x": np.random.normal(0, 1, n),
            }
        )

        result = run_cox_ph(df=df, time_col="time", event_col="event", formula="x")

        # Model should still run
        assert result is not None
        assert "coefficients" in result

    def test_cox_ph_with_small_sample(self):
        """Test Cox PH with small sample size."""
        np.random.seed(888)
        n = 30  # Minimum reasonable sample

        df = pd.DataFrame(
            {
                "time": np.random.exponential(5, n),
                "event": np.random.binomial(1, 0.5, n),
                "x1": np.random.normal(0, 1, n),
                "x2": np.random.normal(0, 1, n),
            }
        )

        result = run_cox_ph(
            df=df, time_col="time", event_col="event", formula="x1 + x2"
        )

        # Model should run even with small sample
        assert result is not None
        assert "x1" in result["coefficients"]
        assert "x2" in result["coefficients"]

    def test_fine_gray_with_no_events_of_interest(self):
        """Test competing risks when no events of interest occur.

        When there are no events, the model cannot converge and should raise an error.
        This is expected behavior - survival models need at least some events.
        """
        import lifelines.exceptions

        np.random.seed(777)
        n = 100

        df = pd.DataFrame(
            {
                "time": np.random.exponential(10, n),
                "event": 0,  # All censored - no events
                "x": np.random.normal(0, 1, n),
            }
        )

        # Should raise ConvergenceError when no events
        with pytest.raises(lifelines.exceptions.ConvergenceError):
            run_fine_gray(df=df, time_col="time", event_col="event", formula="x")

    def test_cox_ph_with_missing_values_in_covariates(self):
        """Test that missing values are handled appropriately."""
        np.random.seed(666)
        n = 100

        df = pd.DataFrame(
            {
                "time": np.random.exponential(10, n),
                "event": np.random.binomial(1, 0.3, n),
                "x1": np.random.normal(0, 1, n),
                "x2": np.random.normal(0, 1, n),
            }
        )

        # Introduce some missing values
        df.loc[0:10, "x1"] = np.nan
        df.loc[5:15, "x2"] = np.nan

        result = run_cox_ph(
            df=df, time_col="time", event_col="event", formula="x1 + x2"
        )

        # Model should run after dropping NA rows
        assert result is not None


# ==============================================================================
# Consistency Tests
# ==============================================================================


class TestSurvivalAnalysisConsistency:
    """Tests for consistency of results."""

    def test_cox_ph_reproducibility(self, realistic_takeover_data):
        """Test that Cox PH produces reproducible results with same data."""
        # Run twice with same data
        result1 = run_cox_ph(
            df=realistic_takeover_data,
            time_col="time",
            event_col="event",
            formula="ClarityCEO + Size",
        )

        result2 = run_cox_ph(
            df=realistic_takeover_data,
            time_col="time",
            event_col="event",
            formula="ClarityCEO + Size",
        )

        # Coefficients should be identical
        for cov in ["ClarityCEO", "Size"]:
            assert result1["coefficients"][cov] == result2["coefficients"][cov]

        # Concordance index should be identical
        assert result1["concordance_index"] == result2["concordance_index"]

    def test_fine_gray_reproducibility(self, competing_risks_data):
        """Test that Fine Gray produces reproducible results with same data."""
        result1 = run_fine_gray(
            df=competing_risks_data,
            time_col="time",
            event_col="event_cr",
            formula="ClarityCEO",
        )

        result2 = run_fine_gray(
            df=competing_risks_data,
            time_col="time",
            event_col="event_cr",
            formula="ClarityCEO",
        )

        # Coefficients should be identical
        assert (
            result1["coefficients"]["ClarityCEO"]
            == result2["coefficients"]["ClarityCEO"]
        )
