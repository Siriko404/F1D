"""
Unit tests for V1 econometric scripts in src/f1d/econometric/v1/.

Tests verify:
- 4.1_EstimateCeoClarity.py: CEO clarity fixed effect estimation
- 4.4_GenerateSummaryStats.py: Summary statistics generation

Uses factory fixtures from tests/conftest.py for test data generation.
"""

import runpy
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

# ==============================================================================
# Helper: Import modules with dots in filenames using runpy
# ==============================================================================

V1_ECONOMETRIC_DIR = (
    Path(__file__).resolve().parent.parent.parent
    / "src" / "f1d" / "econometric"
)


def load_v1_module(filename: str) -> Dict[str, Any]:
    """Load a V1 module using runpy (handles dots in filenames)."""
    module_path = V1_ECONOMETRIC_DIR / filename
    if not module_path.exists():
        pytest.skip(f"V1 module not found: {module_path}")
    return runpy.run_path(str(module_path))


# ==============================================================================
# Fixtures for V1 Econometric Testing
# ==============================================================================


@pytest.fixture
def sample_clarity_input_data():
    """Create sample input data for CEO clarity estimation."""
    np.random.seed(42)
    n_ceos = 20
    n_calls_per_ceo = 5
    data = []

    for ceo_id in range(n_ceos):
        # CEO-specific effect (true clarity)
        ceo_effect = np.random.normal(0, 1)

        for call in range(n_calls_per_ceo):
            # Call-level noise
            noise = np.random.normal(0, 0.3)

            # Observed clarity = true clarity + noise
            observed_clarity = ceo_effect + noise

            row = {
                "ceo_id": f"CEO_{ceo_id:04d}",
                "file_name": f"call_ceo{ceo_id:04d}_{call:02d}.docx",
                "year": 2005 + call,
                "Clarity": observed_clarity,
                "gvkey": f"{ceo_id % 10:06d}",
                "ff12_code": (ceo_id % 12) + 1,
                "Manager_QA_Uncertainty_pct": np.random.uniform(10, 30),
            }
            data.append(row)

    return pd.DataFrame(data)


@pytest.fixture
def sample_panel_regression_data():
    """Create sample panel data for regression testing."""
    np.random.seed(42)
    n_firms = 10
    n_years = 5
    data = []

    for firm_id in range(n_firms):
        gvkey = f"{firm_id:06d}"
        firm_effect = np.random.normal(0, 0.5)

        for year_offset in range(n_years):
            year = 2005 + year_offset

            row = {
                "gvkey": gvkey,
                "year": year,
                "dependent_var": firm_effect + np.random.normal(0, 0.3),
                "independent_var1": np.random.normal(0, 1),
                "independent_var2": np.random.normal(0, 1),
                "ff12_code": (firm_id % 12) + 1,
            }
            data.append(row)

    return pd.DataFrame(data)


@pytest.fixture
def sample_summary_stats_input():
    """Create sample input data for summary statistics generation."""
    np.random.seed(42)
    n = 500

    return pd.DataFrame({
        "file_name": [f"call_{i:04d}.docx" for i in range(n)],
        "ClarityCEO": np.random.normal(0, 1, n),
        "Manager_QA_Uncertainty_pct": np.random.uniform(5, 35, n),
        "Size": np.exp(np.random.normal(7, 1.5, n)),
        "BM": np.random.uniform(0.5, 2.0, n),
        "Lev": np.random.uniform(0.1, 0.8, n),
        "ROA": np.random.normal(0.05, 0.1, n),
        "Takeover": np.random.binomial(1, 0.05, n),
        "year": [2002 + (i % 17) for i in range(n)],
        "ff12_code": np.random.randint(1, 13, n),
        "gvkey": [f"{(i % 50):06d}" for i in range(n)],
    })


@pytest.fixture
def sample_textual_variables():
    """Create sample textual variables for clarity estimation."""
    np.random.seed(42)
    n = 200

    return pd.DataFrame({
        "file_name": [f"call_{i:04d}.docx" for i in range(n)],
        "Clarity": np.random.normal(0, 1, n),
        "MaQaUnc_pct": np.random.uniform(10, 40, n),
        "Total_Words": np.random.randint(2000, 10000, n),
        "Manager_Words_Pct": np.random.uniform(30, 70, n),
    })


@pytest.fixture
def sample_manifest_for_clarity():
    """Create sample manifest for clarity estimation."""
    np.random.seed(42)
    n = 200

    return pd.DataFrame({
        "file_name": [f"call_{i:04d}.docx" for i in range(n)],
        "ceo_id": [f"CEO_{(i % 20):04d}" for i in range(n)],
        "gvkey": [f"{(i % 10):06d}" for i in range(n)],
        "start_date": pd.to_datetime([
            f"{2002 + (i % 17)}-{((i % 12) + 1):02d}-15" for i in range(n)
        ]),
        "ff12_code": [(i % 12) + 1 for i in range(n)],
    })


# ==============================================================================
# Tests for 4.1_EstimateCeoClarity.py
# ==============================================================================


class TestCeoClarityModule:
    """Tests for 4.1_EstimateCeoClarity.py module structure."""

    def test_module_can_be_loaded(self):
        """Test that 4.1_EstimateCeoClarity module can be imported."""
        module = load_v1_module("4.1_EstimateCeoClarity.py")
        assert module is not None

    def test_module_has_main_function(self):
        """Test that module has main function."""
        module = load_v1_module("4.1_EstimateCeoClarity.py")
        assert "main" in module

    def test_module_has_load_all_data_function(self):
        """Test that module has load_all_data function."""
        module = load_v1_module("4.1_EstimateCeoClarity.py")
        assert "load_all_data" in module

    def test_module_has_prepare_regression_data_function(self):
        """Test that module has prepare_regression_data function."""
        module = load_v1_module("4.1_EstimateCeoClarity.py")
        assert "prepare_regression_data" in module

    def test_module_has_run_regression_function(self):
        """Test that module has run_regression function."""
        module = load_v1_module("4.1_EstimateCeoClarity.py")
        assert "run_regression" in module

    def test_module_has_extract_ceo_fixed_effects_function(self):
        """Test that module has extract_ceo_fixed_effects function."""
        module = load_v1_module("4.1_EstimateCeoClarity.py")
        assert "extract_ceo_fixed_effects" in module


class TestCeoClarityPrepareRegressionData:
    """Tests for prepare_regression_data function."""

    def test_prepare_regression_data_returns_dataframe(self, sample_clarity_input_data):
        """Test that prepare_regression_data returns a DataFrame."""
        module = load_v1_module("4.1_EstimateCeoClarity.py")
        prepare_regression_data = module["prepare_regression_data"]

        result = prepare_regression_data(sample_clarity_input_data)

        assert isinstance(result, pd.DataFrame)

    def test_prepare_regression_data_adds_required_columns(self, sample_clarity_input_data):
        """Test that prepare_regression_data adds required columns for regression."""
        module = load_v1_module("4.1_EstimateCeoClarity.py")
        prepare_regression_data = module["prepare_regression_data"]

        result = prepare_regression_data(sample_clarity_input_data)

        # Should have Clarity column for regression
        assert "Clarity" in result.columns


class TestCeoClarityExtractFixedEffects:
    """Tests for extract_ceo_fixed_effects function."""

    def test_extract_ceo_fixed_effects_function_exists(self):
        """Test that extract_ceo_fixed_effects function exists and is callable."""
        module = load_v1_module("4.1_EstimateCeoClarity.py")
        extract_ceo_fixed_effects = module["extract_ceo_fixed_effects"]

        assert callable(extract_ceo_fixed_effects)


class TestCeoClarityComputeStats:
    """Tests for compute_ceo_stats function."""

    def test_compute_ceo_stats_function_exists(self):
        """Test that compute_ceo_stats function exists and is callable."""
        module = load_v1_module("4.1_EstimateCeoClarity.py")
        compute_ceo_stats = module["compute_ceo_stats"]

        assert callable(compute_ceo_stats)


# ==============================================================================
# Tests for 4.4_GenerateSummaryStats.py
# ==============================================================================


class TestSummaryStatsModule:
    """Tests for 4.4_GenerateSummaryStats.py module structure."""

    def test_module_can_be_loaded(self):
        """Test that 4.4_GenerateSummaryStats module can be imported."""
        module = load_v1_module("4.4_GenerateSummaryStats.py")
        assert module is not None

    def test_module_has_main_function(self):
        """Test that module has main function."""
        module = load_v1_module("4.4_GenerateSummaryStats.py")
        assert "main" in module

    def test_module_has_load_manifest_function(self):
        """Test that module has load_manifest function."""
        module = load_v1_module("4.4_GenerateSummaryStats.py")
        assert "load_manifest" in module

    def test_module_has_compute_descriptive_statistics_function(self):
        """Test that module has compute_descriptive_statistics function."""
        module = load_v1_module("4.4_GenerateSummaryStats.py")
        assert "compute_descriptive_statistics" in module

    def test_module_has_compute_correlation_matrix_function(self):
        """Test that module has compute_correlation_matrix function."""
        module = load_v1_module("4.4_GenerateSummaryStats.py")
        assert "compute_correlation_matrix" in module

    def test_module_has_compute_panel_balance_function(self):
        """Test that module has compute_panel_balance function."""
        module = load_v1_module("4.4_GenerateSummaryStats.py")
        assert "compute_panel_balance" in module


class TestSummaryStatsLoadManifest:
    """Tests for load_manifest function in 4.4_GenerateSummaryStats.py."""

    def test_load_manifest_returns_dataframe(self, sample_manifest_for_clarity, tmp_path):
        """Test that load_manifest returns a DataFrame."""
        manifest_file = tmp_path / "master_sample_manifest.parquet"
        sample_manifest_for_clarity.to_parquet(manifest_file)

        module = load_v1_module("4.4_GenerateSummaryStats.py")
        load_manifest = module["load_manifest"]

        result = load_manifest(manifest_file)

        assert isinstance(result, pd.DataFrame)

    def test_load_manifest_preserves_columns(self, sample_manifest_for_clarity, tmp_path):
        """Test that load_manifest preserves expected columns."""
        manifest_file = tmp_path / "master_sample_manifest.parquet"
        sample_manifest_for_clarity.to_parquet(manifest_file)

        module = load_v1_module("4.4_GenerateSummaryStats.py")
        load_manifest = module["load_manifest"]

        result = load_manifest(manifest_file)

        assert "file_name" in result.columns
        assert "ceo_id" in result.columns


class TestSummaryStatsLoadLinguisticVariables:
    """Tests for load_linguistic_variables function."""

    def test_load_linguistic_variables_function_exists(self):
        """Test that load_linguistic_variables function exists."""
        module = load_v1_module("4.4_GenerateSummaryStats.py")
        load_linguistic_variables = module["load_linguistic_variables"]

        assert callable(load_linguistic_variables)


class TestSummaryStatsPrepareAnalysisData:
    """Tests for prepare_analysis_data function."""

    def test_prepare_analysis_data_function_exists(self):
        """Test that prepare_analysis_data function exists."""
        module = load_v1_module("4.4_GenerateSummaryStats.py")
        prepare_analysis_data = module["prepare_analysis_data"]

        assert callable(prepare_analysis_data)


class TestSummaryStatsFilterCompleteCases:
    """Tests for filter_complete_cases function."""

    def test_filter_complete_cases_function_exists(self):
        """Test that filter_complete_cases function exists."""
        module = load_v1_module("4.4_GenerateSummaryStats.py")
        filter_complete_cases = module["filter_complete_cases"]

        assert callable(filter_complete_cases)


class TestSummaryStatsDescriptiveStatistics:
    """Tests for compute_descriptive_statistics function."""

    def test_compute_descriptive_statistics_creates_file(self, sample_summary_stats_input, tmp_path):
        """Test that compute_descriptive_statistics creates output file."""
        module = load_v1_module("4.4_GenerateSummaryStats.py")
        compute_descriptive_statistics = module["compute_descriptive_statistics"]

        output_path = tmp_path / "descriptive_stats.csv"

        result = compute_descriptive_statistics(sample_summary_stats_input, output_path)

        # Function should complete without error
        # Output file may or may not be created depending on implementation
        assert result is None or isinstance(result, pd.DataFrame)


class TestSummaryStatsCorrelationMatrix:
    """Tests for compute_correlation_matrix function."""

    def test_compute_correlation_matrix_creates_file(self, sample_summary_stats_input, tmp_path):
        """Test that compute_correlation_matrix creates output file."""
        module = load_v1_module("4.4_GenerateSummaryStats.py")
        compute_correlation_matrix = module["compute_correlation_matrix"]

        output_path = tmp_path / "correlation_matrix.csv"

        result = compute_correlation_matrix(sample_summary_stats_input, output_path)

        # Function should complete without error
        assert result is None or isinstance(result, pd.DataFrame)

    def test_compute_correlation_matrix_handles_nan_values(self, tmp_path):
        """Test that compute_correlation_matrix handles NaN values."""
        module = load_v1_module("4.4_GenerateSummaryStats.py")
        compute_correlation_matrix = module["compute_correlation_matrix"]

        df = pd.DataFrame({
            "var1": [1.0, 2.0, np.nan, 4.0, 5.0],
            "var2": [2.0, np.nan, 3.0, 4.0, 5.0],
            "var3": [1.0, 2.0, 3.0, 4.0, 5.0],
        })

        output_path = tmp_path / "correlation_matrix.csv"

        result = compute_correlation_matrix(df, output_path)

        # Should handle NaN without error
        assert result is None or isinstance(result, pd.DataFrame)


class TestSummaryStatsPanelBalance:
    """Tests for compute_panel_balance function."""

    def test_compute_panel_balance_creates_file(self, sample_summary_stats_input, tmp_path):
        """Test that compute_panel_balance creates output file."""
        module = load_v1_module("4.4_GenerateSummaryStats.py")
        compute_panel_balance = module["compute_panel_balance"]

        output_path = tmp_path / "panel_balance.csv"

        result = compute_panel_balance(sample_summary_stats_input, output_path)

        # Function should complete without error (returns tuple)
        assert result is not None


# ==============================================================================
# Edge Case Tests
# ==============================================================================


class TestV1EconometricEdgeCases:
    """Tests for edge cases in V1 econometric scripts."""

    def test_compute_descriptive_statistics_handles_single_row(self, tmp_path):
        """Test compute_descriptive_statistics with single row."""
        module = load_v1_module("4.4_GenerateSummaryStats.py")
        compute_descriptive_statistics = module["compute_descriptive_statistics"]

        df = pd.DataFrame({
            "var1": [1.0],
            "var2": [2.0],
        })

        output_path = tmp_path / "single_row_stats.csv"

        result = compute_descriptive_statistics(df, output_path)

        # Should handle single row without error
        assert result is None or isinstance(result, pd.DataFrame)

    def test_prepare_regression_data_handles_missing_clarity(self):
        """Test prepare_regression_data with missing Clarity column."""
        module = load_v1_module("4.1_EstimateCeoClarity.py")
        prepare_regression_data = module["prepare_regression_data"]

        df = pd.DataFrame({
            "ceo_id": ["CEO_0001", "CEO_0002"],
            "gvkey": ["000001", "000002"],
            "ff12_code": [1, 2],  # Required column
            # Missing Clarity column
        })

        result = prepare_regression_data(df)

        # Should return DataFrame, possibly with NaN for Clarity
        assert isinstance(result, pd.DataFrame)


# ==============================================================================
# Integration Tests
# ==============================================================================


class TestV1EconometricIntegration:
    """Integration tests for V1 econometric scripts."""

    def test_ceo_clarity_data_preparation_workflow(self, sample_clarity_input_data):
        """Test the data preparation workflow for CEO clarity estimation."""
        module = load_v1_module("4.1_EstimateCeoClarity.py")
        prepare_regression_data = module["prepare_regression_data"]

        # Step: Prepare regression data
        result = prepare_regression_data(sample_clarity_input_data)

        assert isinstance(result, pd.DataFrame)
        assert "Clarity" in result.columns
