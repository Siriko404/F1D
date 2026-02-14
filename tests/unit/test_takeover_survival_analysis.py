"""
Unit tests for survival analysis functions in 4.3_TakeoverHazards.py.

Tests run_cox_ph and run_fine_gray functions for:
- Valid input handling
- Missing column error handling
- Output format validation
"""

import runpy
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Import the functions to test - module name contains dots so use runpy
# The file is named "4.3_TakeoverHazards.py" which is not a valid Python identifier
# tests/unit/ -> src/f1d/econometric/v1/ (go up 3 levels to project root, then into src)
_MODULE_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "src" / "f1d" / "econometric" / "v1" / "4.3_TakeoverHazards.py"
)
_MODULE_GLOBALS = runpy.run_path(str(_MODULE_PATH))
run_cox_ph = _MODULE_GLOBALS["run_cox_ph"]
run_fine_gray = _MODULE_GLOBALS["run_fine_gray"]


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture
def sample_survival_data():
    """Create sample survival data for testing."""
    np.random.seed(42)
    n = 100

    df = pd.DataFrame({
        "time": np.random.exponential(10, n),
        "event": np.random.binomial(1, 0.3, n),
        "clarity": np.random.normal(0, 1, n),
        "uncertainty": np.random.normal(0, 1, n),
        "size": np.random.lognormal(0, 1, n),
    })

    return df


@pytest.fixture
def sample_competing_risks_data():
    """Create sample competing risks data for Fine-Gray model."""
    np.random.seed(42)
    n = 100

    # Event types: 0=censored, 1=event of interest, 2=competing event
    event_types = np.random.choice([0, 1, 2], n, p=[0.5, 0.3, 0.2])

    df = pd.DataFrame({
        "time": np.random.exponential(10, n),
        "event": event_types,
        "clarity": np.random.normal(0, 1, n),
        "uncertainty": np.random.normal(0, 1, n),
        "size": np.random.lognormal(0, 1, n),
    })

    return df


# ==============================================================================
# Tests for run_cox_ph
# ==============================================================================

class TestRunCoxPH:
    """Tests for run_cox_ph function."""

    def test_run_cox_ph_with_valid_input_returns_result(self, sample_survival_data):
        """Test that run_cox_ph returns a valid result dictionary.

        GREEN phase: Function is implemented and returns expected output.
        """
        result = run_cox_ph(
            df=sample_survival_data,
            time_col="time",
            event_col="event",
            formula="clarity + uncertainty + size"
        )

        # Verify output structure
        assert isinstance(result, dict)
        assert "coefficients" in result
        assert "confidence_intervals" in result
        assert "summary" in result
        assert "concordance_index" in result
        assert "model" in result

        # Verify coefficients contain expected covariates
        assert "clarity" in result["coefficients"]
        assert "uncertainty" in result["coefficients"]
        assert "size" in result["coefficients"]

        # Verify concordance index is valid (0.5 to 1.0)
        assert 0.0 <= result["concordance_index"] <= 1.0

    def test_run_cox_ph_missing_time_col_raises_value_error(self, sample_survival_data):
        """Test that missing time_col raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            run_cox_ph(
                df=sample_survival_data,
                time_col="nonexistent_time",
                event_col="event",
                formula="clarity + uncertainty"
            )

        assert "Missing columns" in str(exc_info.value)

    def test_run_cox_ph_missing_event_col_raises_value_error(self, sample_survival_data):
        """Test that missing event_col raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            run_cox_ph(
                df=sample_survival_data,
                time_col="time",
                event_col="nonexistent_event",
                formula="clarity + uncertainty"
            )

        assert "Missing columns" in str(exc_info.value)

    def test_run_cox_ph_missing_covariate_raises_value_error(self, sample_survival_data):
        """Test that missing covariate in formula raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            run_cox_ph(
                df=sample_survival_data,
                time_col="time",
                event_col="event",
                formula="nonexistent_covariate"
            )

        assert "Missing covariate columns" in str(exc_info.value)


# ==============================================================================
# Tests for run_fine_gray
# ==============================================================================

class TestRunFineGray:
    """Tests for run_fine_gray function."""

    def test_run_fine_gray_with_valid_input_returns_result(self, sample_competing_risks_data):
        """Test that run_fine_gray returns a valid result dictionary.

        GREEN phase: Function is implemented and returns expected output.
        Note: Uses cause-specific hazards approach (not true Fine-Gray).
        """
        result = run_fine_gray(
            df=sample_competing_risks_data,
            time_col="time",
            event_col="event",
            formula="clarity + uncertainty + size"
        )

        # Verify output structure
        assert isinstance(result, dict)
        assert "coefficients" in result
        assert "confidence_intervals" in result
        assert "summary" in result
        assert "concordance_index" in result
        assert "model" in result
        assert "method" in result

        # Verify method indicates cause-specific hazards
        assert result["method"] == "cause_specific_hazards"

        # Verify coefficients contain expected covariates
        assert "clarity" in result["coefficients"]
        assert "uncertainty" in result["coefficients"]
        assert "size" in result["coefficients"]

        # Verify concordance index is valid (0.5 to 1.0)
        assert 0.0 <= result["concordance_index"] <= 1.0

    def test_run_fine_gray_missing_time_col_raises_value_error(self, sample_competing_risks_data):
        """Test that missing time_col raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            run_fine_gray(
                df=sample_competing_risks_data,
                time_col="nonexistent_time",
                event_col="event",
                formula="clarity + uncertainty"
            )

        assert "Missing columns" in str(exc_info.value)

    def test_run_fine_gray_missing_event_col_raises_value_error(self, sample_competing_risks_data):
        """Test that missing event_col raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            run_fine_gray(
                df=sample_competing_risks_data,
                time_col="time",
                event_col="nonexistent_event",
                formula="clarity + uncertainty"
            )

        assert "Missing columns" in str(exc_info.value)

    def test_run_fine_gray_missing_covariate_raises_value_error(self, sample_competing_risks_data):
        """Test that missing covariate in formula raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            run_fine_gray(
                df=sample_competing_risks_data,
                time_col="time",
                event_col="event",
                formula="nonexistent_covariate"
            )

        assert "Missing covariate columns" in str(exc_info.value)


# ==============================================================================
# Integration-style tests for output format
# ==============================================================================

class TestOutputFormat:
    """Tests for output format validation."""

    def test_cox_ph_output_format(self, sample_survival_data):
        """Test that run_cox_ph returns expected output format."""
        result = run_cox_ph(
            df=sample_survival_data,
            time_col="time",
            event_col="event",
            formula="clarity + uncertainty"
        )

        assert isinstance(result, dict)
        assert "coefficients" in result
        assert "confidence_intervals" in result
        assert "summary" in result
        assert "concordance_index" in result
        assert "model" in result

    def test_fine_gray_output_format(self, sample_competing_risks_data):
        """Test that run_fine_gray returns expected output format."""
        result = run_fine_gray(
            df=sample_competing_risks_data,
            time_col="time",
            event_col="event",
            formula="clarity + uncertainty"
        )

        assert isinstance(result, dict)
        assert "coefficients" in result
        assert "confidence_intervals" in result
        assert "summary" in result
        assert "model" in result
        assert "concordance_index" in result
        assert "method" in result
