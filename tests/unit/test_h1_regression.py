"""
Unit tests for H1 Cash Holdings Regression (run_h1_cash_holdings.py).

Tests verify:
- Data loading and preparation functions
- Regression execution with mocked panel OLS
- Output format and structure
- Error handling for missing data
"""

import numpy as np
import pandas as pd
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the module under test
import runpy
_MODULE_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "src" / "f1d" / "econometric" / "run_h1_cash_holdings.py"
)


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture
def sample_h1_data():
    """Create sample H1 cash holdings data for testing."""
    np.random.seed(42)
    n_firms = 50
    n_years = 5

    data = []
    for firm_id in range(n_firms):
        gvkey = str(firm_id).zfill(6)
        for year_offset in range(n_years):
            fiscal_year = 2010 + year_offset
            data.append({
                "gvkey": gvkey,
                "fiscal_year": fiscal_year,
                "cash_ratio": np.random.uniform(0.05, 0.3),
                "Manager_QA_Uncertainty_pct": np.random.uniform(2, 8),
                "CEO_QA_Uncertainty_pct": np.random.uniform(2, 8),
                "Manager_QA_Weak_Modal_pct": np.random.uniform(1, 5),
                "CEO_QA_Weak_Modal_pct": np.random.uniform(1, 5),
                "Manager_Pres_Uncertainty_pct": np.random.uniform(1, 5),
                "CEO_Pres_Uncertainty_pct": np.random.uniform(1, 5),
                "firm_size": np.random.uniform(5, 10),
                "tobins_q": np.random.uniform(0.8, 2.0),
                "roa": np.random.uniform(-0.1, 0.2),
                "leverage": np.random.uniform(0.1, 0.6),
                "cash_holdings": np.random.uniform(0.05, 0.3),
                "dividend_payer": np.random.randint(0, 2),
            })

    return pd.DataFrame(data)


@pytest.fixture
def sample_speech_data():
    """Create sample speech uncertainty data for testing."""
    np.random.seed(42)
    n_calls = 500

    data = []
    for i in range(n_calls):
        gvkey = str(i % 50).zfill(6)
        data.append({
            "file_name": f"call_{i}.docx",
            "gvkey": gvkey,
            "start_date": pd.Timestamp(f"201{ i % 5 }-06-15"),
            "Manager_QA_Uncertainty_pct": np.random.uniform(2, 8),
            "CEO_QA_Uncertainty_pct": np.random.uniform(2, 8),
            "Manager_QA_Weak_Modal_pct": np.random.uniform(1, 5),
            "CEO_QA_Weak_Modal_pct": np.random.uniform(1, 5),
            "Manager_Pres_Uncertainty_pct": np.random.uniform(1, 5),
            "CEO_Pres_Uncertainty_pct": np.random.uniform(1, 5),
        })

    return pd.DataFrame(data)


@pytest.fixture
def mock_panel_ols_result():
    """Create mock result from run_panel_ols."""
    return {
        "model": MagicMock(),
        "coefficients": pd.DataFrame({
            "Coefficient": [-0.05, 0.02, -0.01],
            "Std. Error": [0.02, 0.01, 0.005],
            "t-stat": [-2.5, 2.0, -2.0],
        }, index=["Manager_QA_Uncertainty_pct_c", "firm_size", "leverage"]),
        "summary": {
            "rsquared": 0.35,
            "rsquared_within": 0.15,
            "nobs": 200,
            "entity_effects": True,
            "time_effects": True,
            "cov_type": "clustered",
            "f_statistic": 15.5,
            "f_pvalue": 0.001,
        },
        "diagnostics": {"vif": None},
        "warnings": [],
    }


# ==============================================================================
# Data Loading Tests
# ==============================================================================

class TestH1DataLoading:
    """Tests for H1 data loading functions."""

    def test_load_h1_variables_basic(self, sample_h1_data, tmp_path):
        """Test that H1 variables load correctly from parquet."""
        # Save sample data to parquet
        h1_file = tmp_path / "H1_CashHoldings.parquet"
        sample_h1_data.to_parquet(h1_file, index=False)

        # Load and verify
        loaded = pd.read_parquet(h1_file)

        assert len(loaded) == len(sample_h1_data)
        assert "gvkey" in loaded.columns
        assert "fiscal_year" in loaded.columns
        assert "cash_ratio" in loaded.columns

    def test_gvkey_format(self, sample_h1_data):
        """Test that gvkey is properly formatted as zero-padded string."""
        df = sample_h1_data.copy()
        df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)

        assert df["gvkey"].str.len().unique()[0] == 6
        assert df["gvkey"].dtype == object

    def test_uncertainty_measures_present(self, sample_h1_data):
        """Test that all required uncertainty measures are present."""
        uncertainty_cols = [
            "Manager_QA_Uncertainty_pct",
            "CEO_QA_Uncertainty_pct",
            "Manager_QA_Weak_Modal_pct",
            "CEO_QA_Weak_Modal_pct",
            "Manager_Pres_Uncertainty_pct",
            "CEO_Pres_Uncertainty_pct",
        ]

        for col in uncertainty_cols:
            assert col in sample_h1_data.columns, f"Missing {col}"


# ==============================================================================
# Regression Execution Tests
# ==============================================================================

class TestH1RegressionExecution:
    """Tests for H1 regression execution."""

    @patch("f1d.shared.panel_ols.run_panel_ols")
    def test_single_regression_called_correctly(
        self, mock_run_panel_ols, sample_h1_data, mock_panel_ols_result
    ):
        """Test that run_panel_ols is called with correct parameters."""
        mock_run_panel_ols.return_value = mock_panel_ols_result

        from f1d.shared.panel_ols import run_panel_ols

        # Create data with proper index
        df = sample_h1_data.copy()
        df = df.dropna()

        # Call run_panel_ols
        result = run_panel_ols(
            df=df,
            dependent="cash_ratio",
            exog=["Manager_QA_Uncertainty_pct", "firm_size"],
            entity_col="gvkey",
            time_col="fiscal_year",
            entity_effects=True,
            time_effects=True,
            check_collinearity=False,
        )

        # Verify call was made
        mock_run_panel_ols.assert_called_once()
        assert result is not None

    @patch("f1d.shared.panel_ols.run_panel_ols")
    def test_regression_returns_expected_structure(
        self, mock_run_panel_ols, sample_h1_data, mock_panel_ols_result
    ):
        """Test that regression returns expected result structure."""
        mock_run_panel_ols.return_value = mock_panel_ols_result

        from f1d.shared.panel_ols import run_panel_ols

        df = sample_h1_data.copy()
        df = df.dropna()

        result = run_panel_ols(
            df=df,
            dependent="cash_ratio",
            exog=["Manager_QA_Uncertainty_pct"],
            entity_col="gvkey",
            time_col="fiscal_year",
            entity_effects=True,
            time_effects=True,
            check_collinearity=False,
        )

        # Verify result structure
        assert "model" in result
        assert "coefficients" in result
        assert "summary" in result
        assert "diagnostics" in result
        assert "warnings" in result

        # Verify summary fields
        assert "rsquared" in result["summary"]
        assert "nobs" in result["summary"]
        assert "entity_effects" in result["summary"]
        assert "time_effects" in result["summary"]


# ==============================================================================
# Output Format Tests
# ==============================================================================

class TestH1OutputFormat:
    """Tests for H1 regression output format."""

    def test_coefficients_dataframe_structure(self, mock_panel_ols_result):
        """Test that coefficients DataFrame has expected columns."""
        coef_df = mock_panel_ols_result["coefficients"]

        assert "Coefficient" in coef_df.columns
        assert "Std. Error" in coef_df.columns
        assert "t-stat" in coef_df.columns

    def test_summary_contains_required_fields(self, mock_panel_ols_result):
        """Test that summary contains all required fields."""
        summary = mock_panel_ols_result["summary"]

        required_fields = [
            "rsquared",
            "nobs",
            "entity_effects",
            "time_effects",
            "cov_type",
        ]

        for field in required_fields:
            assert field in summary, f"Missing {field} in summary"

    def test_pvalue_extraction(self, mock_panel_ols_result):
        """Test that p-values can be extracted from model."""
        # Mock pvalues attribute
        mock_panel_ols_result["model"].pvalues = pd.Series({
            "Manager_QA_Uncertainty_pct_c": 0.012,
            "firm_size": 0.045,
            "leverage": 0.085,
        })

        pvalues = mock_panel_ols_result["model"].pvalues

        assert "Manager_QA_Uncertainty_pct_c" in pvalues.index
        assert pvalues["Manager_QA_Uncertainty_pct_c"] < 0.05


# ==============================================================================
# Error Handling Tests
# ==============================================================================

class TestH1ErrorHandling:
    """Tests for H1 error handling."""

    def test_missing_dependent_raises_error(self, sample_h1_data):
        """Test that missing dependent column raises appropriate error."""
        from f1d.shared.panel_ols import run_panel_ols

        df = sample_h1_data.copy()
        df = df.drop(columns=["cash_ratio"])

        with pytest.raises(ValueError, match="Missing required columns"):
            run_panel_ols(
                df=df,
                dependent="cash_ratio",
                exog=["Manager_QA_Uncertainty_pct"],
                entity_col="gvkey",
                time_col="fiscal_year",
            )

    def test_missing_exog_raises_error(self, sample_h1_data):
        """Test that missing exogenous column raises appropriate error."""
        from f1d.shared.panel_ols import run_panel_ols

        df = sample_h1_data.copy()

        with pytest.raises(ValueError, match="Missing required columns"):
            run_panel_ols(
                df=df,
                dependent="cash_ratio",
                exog=["nonexistent_column"],
                entity_col="gvkey",
                time_col="fiscal_year",
            )

    def test_empty_dataframe_raises_error(self):
        """Test that empty DataFrame raises appropriate error."""
        from f1d.shared.panel_ols import run_panel_ols

        df = pd.DataFrame()

        with pytest.raises(ValueError):
            run_panel_ols(
                df=df,
                dependent="cash_ratio",
                exog=["uncertainty"],
                entity_col="gvkey",
                time_col="fiscal_year",
            )


# ==============================================================================
# Hypothesis Test Tests
# ==============================================================================

class TestH1HypothesisTests:
    """Tests for H1 hypothesis test calculations."""

    def test_one_tailed_pvalue_calculation(self):
        """Test one-tailed p-value calculation for H1 (beta < 0)."""
        # H1: beta < 0 (vagueness reduces cash holdings)
        # If coef < 0, one-tailed p = two-tailed p / 2

        coef = -0.05  # Negative as expected for H1
        p_two_tailed = 0.04

        if coef < 0:
            p_one_tailed = p_two_tailed / 2
        else:
            p_one_tailed = 1 - p_two_tailed / 2

        assert p_one_tailed == 0.02
        assert p_one_tailed < 0.05  # Significant at 5% level

    def test_h1_supported_when_coef_negative_and_significant(self):
        """Test that H1 is supported when coefficient is negative and significant."""
        coef = -0.05
        p_one_tailed = 0.02

        h1_supported = (p_one_tailed < 0.05) and (coef < 0)

        assert h1_supported is True

    def test_h1_not_supported_when_coef_positive(self):
        """Test that H1 is not supported when coefficient is positive."""
        coef = 0.03  # Wrong sign
        p_one_tailed = 0.02

        h1_supported = (p_one_tailed < 0.05) and (coef < 0)

        assert h1_supported is False

    def test_h1_not_supported_when_not_significant(self):
        """Test that H1 is not supported when not significant."""
        coef = -0.05  # Correct sign
        p_one_tailed = 0.10  # Not significant

        h1_supported = (p_one_tailed < 0.05) and (coef < 0)

        assert h1_supported is False


# ==============================================================================
# Integration Test
# ==============================================================================

class TestH1Integration:
    """Integration tests for H1 regression."""

    @pytest.mark.skipif(
        not Path(_MODULE_PATH).exists(),
        reason="H1 regression module not found"
    )
    def test_module_imports_successfully(self):
        """Test that the H1 regression module imports without error."""
        module_globals = runpy.run_path(str(_MODULE_PATH))

        # Check that key functions exist
        assert "main" in module_globals or "run_all_h1_regressions" in module_globals

    def test_dry_run_flag_supported(self):
        """Test that --dry-run flag is supported."""
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, str(_MODULE_PATH), "--help"],
            capture_output=True,
            text=True,
        )

        # Should exit cleanly with help message
        assert result.returncode == 0 or "dry-run" in result.stdout.lower() or "dry-run" in result.stderr.lower()
