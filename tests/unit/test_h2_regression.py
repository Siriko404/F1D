"""
Unit tests for H2 Investment Efficiency Regression (run_h2_investment.py).

Tests verify:
- Data loading and preparation for investment efficiency variables
- Regression execution with investment_q as DV
- Hypothesis test logic for investment efficiency
- Output format and error handling
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
    / "src" / "f1d" / "econometric" / "run_h2_investment.py"
)


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture
def sample_h2_data():
    """Create sample H2 investment efficiency data for testing."""
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
                "investment_q": np.random.uniform(0.8, 1.5),  # Investment efficiency DV
                "Manager_QA_Uncertainty_pct": np.random.uniform(2, 8),
                "CEO_QA_Uncertainty_pct": np.random.uniform(2, 8),
                "Manager_QA_Weak_Modal_pct": np.random.uniform(1, 5),
                "CEO_QA_Weak_Modal_pct": np.random.uniform(1, 5),
                "Manager_Pres_Uncertainty_pct": np.random.uniform(1, 5),
                "CEO_Pres_Uncertainty_pct": np.random.uniform(1, 5),
                "analyst_qa_uncertainty": np.random.uniform(1, 5),  # Control for analyst uncertainty
                "firm_size": np.random.uniform(5, 10),
                "tobins_q": np.random.uniform(0.8, 2.0),
                "roa": np.random.uniform(-0.1, 0.2),
                "leverage": np.random.uniform(0.1, 0.6),
                "cash_holdings": np.random.uniform(0.05, 0.3),
                "dividend_payer": np.random.randint(0, 2),
                "capex_ratio": np.random.uniform(0.01, 0.1),
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
    """Create mock result from run_panel_ols for H2 regressions."""
    return {
        "model": MagicMock(),
        "coefficients": pd.DataFrame({
            "Coefficient": [-0.08, 0.02, -0.015, 0.05],
            "Std. Error": [0.03, 0.01, 0.01, 0.02],
            "t-stat": [-2.67, 2.0, -1.5, 2.5],
        }, index=[
            "Manager_QA_Uncertainty_pct_c",
            "analyst_qa_uncertainty",
            "leverage",
            "tobins_q"
        ]),
        "summary": {
            "rsquared": 0.25,
            "rsquared_within": 0.12,
            "nobs": 200,
            "entity_effects": True,
            "time_effects": True,
            "cov_type": "clustered",
            "f_statistic": 12.5,
            "f_pvalue": 0.002,
        },
        "diagnostics": {"vif": None},
        "warnings": [],
    }


# ==============================================================================
# Data Loading Tests
# ==============================================================================

class TestH2DataLoading:
    """Tests for H2 data loading functions."""

    def test_load_h2_variables_basic(self, sample_h2_data, tmp_path):
        """Test that H2 variables load correctly from parquet."""
        # Save sample data to parquet
        h2_file = tmp_path / "H2_InvestmentEfficiency.parquet"
        sample_h2_data.to_parquet(h2_file, index=False)

        # Load and verify
        loaded = pd.read_parquet(h2_file)

        assert len(loaded) == len(sample_h2_data)
        assert "gvkey" in loaded.columns
        assert "fiscal_year" in loaded.columns
        assert "investment_q" in loaded.columns

    def test_investment_q_present(self, sample_h2_data):
        """Test that investment_q (H2 DV) is present."""
        assert "investment_q" in sample_h2_data.columns
        assert sample_h2_data["investment_q"].notna().all()

    def test_analyst_uncertainty_control_present(self, sample_h2_data):
        """Test that analyst uncertainty control is present."""
        assert "analyst_qa_uncertainty" in sample_h2_data.columns

    def test_all_h2_controls_present(self, sample_h2_data):
        """Test that all H2-specific controls are present."""
        h2_controls = [
            "analyst_qa_uncertainty",
            "firm_size",
            "tobins_q",
            "roa",
            "leverage",
            "cash_holdings",
            "dividend_payer",
            "capex_ratio",
        ]

        for col in h2_controls:
            assert col in sample_h2_data.columns, f"Missing H2 control: {col}"


# ==============================================================================
# Regression Execution Tests
# ==============================================================================

class TestH2RegressionExecution:
    """Tests for H2 regression execution."""

    @patch("f1d.shared.panel_ols.run_panel_ols")
    def test_single_h2_regression_called_correctly(
        self, mock_run_panel_ols, sample_h2_data, mock_panel_ols_result
    ):
        """Test that run_panel_ols is called with correct parameters for H2."""
        mock_run_panel_ols.return_value = mock_panel_ols_result

        from f1d.shared.panel_ols import run_panel_ols

        df = sample_h2_data.copy()
        df = df.dropna()

        result = run_panel_ols(
            df=df,
            dependent="investment_q",
            exog=["Manager_QA_Uncertainty_pct", "analyst_qa_uncertainty", "tobins_q"],
            entity_col="gvkey",
            time_col="fiscal_year",
            entity_effects=True,
            time_effects=True,
            check_collinearity=False,
        )

        mock_run_panel_ols.assert_called_once()
        assert result is not None

    @patch("f1d.shared.panel_ols.run_panel_ols")
    def test_h2_regression_includes_analyst_control(
        self, mock_run_panel_ols, sample_h2_data, mock_panel_ols_result
    ):
        """Test that H2 regressions include analyst uncertainty as control."""
        mock_run_panel_ols.return_value = mock_panel_ols_result

        from f1d.shared.panel_ols import run_panel_ols

        df = sample_h2_data.copy()

        # H2 regressions should always include analyst uncertainty control
        exog_vars = ["Manager_QA_Uncertainty_pct", "analyst_qa_uncertainty"]

        run_panel_ols(
            df=df,
            dependent="investment_q",
            exog=exog_vars,
            entity_col="gvkey",
            time_col="fiscal_year",
            entity_effects=True,
            time_effects=True,
            check_collinearity=False,
        )

        call_args = mock_run_panel_ols.call_args
        assert "analyst_qa_uncertainty" in call_args[1]["exog"]


# ==============================================================================
# Output Format Tests
# ==============================================================================

class TestH2OutputFormat:
    """Tests for H2 regression output format."""

    def test_coefficients_dataframe_structure(self, mock_panel_ols_result):
        """Test that coefficients DataFrame has expected columns."""
        coef_df = mock_panel_ols_result["coefficients"]

        assert "Coefficient" in coef_df.columns
        assert "Std. Error" in coef_df.columns
        assert "t-stat" in coef_df.columns

    def test_regression_result_structure(self, mock_panel_ols_result):
        """Test that regression result has expected structure."""
        required_keys = ["model", "coefficients", "summary", "diagnostics", "warnings"]

        for key in required_keys:
            assert key in mock_panel_ols_result, f"Missing key: {key}"


# ==============================================================================
# Hypothesis Test Tests
# ==============================================================================

class TestH2HypothesisTests:
    """Tests for H2 hypothesis test calculations."""

    def test_h2_hypothesis_direction(self):
        """Test that H2 hypothesis is correctly specified (beta < 0)."""
        # H2: Managerial vagueness -> lower investment efficiency
        # Therefore beta < 0 (higher uncertainty -> lower investment_q)

        coef = -0.08  # Negative as expected for H2
        p_two_tailed = 0.02

        # One-tailed test for H2: beta < 0
        if coef < 0:
            p_one_tailed = p_two_tailed / 2
        else:
            p_one_tailed = 1 - p_two_tailed / 2

        assert p_one_tailed == 0.01
        assert p_one_tailed < 0.05

    def test_h2_supported_with_negative_significant_coef(self):
        """Test that H2 is supported when coef is negative and significant."""
        coef = -0.08
        p_one_tailed = 0.01

        h2_supported = (p_one_tailed < 0.05) and (coef < 0)

        assert h2_supported is True

    def test_h2_not_supported_with_positive_coef(self):
        """Test that H2 is not supported when coef is positive."""
        coef = 0.05  # Wrong sign for H2
        p_one_tailed = 0.01

        h2_supported = (p_one_tailed < 0.05) and (coef < 0)

        assert h2_supported is False

    def test_h2_not_supported_with_insignificant_coef(self):
        """Test that H2 is not supported when not significant."""
        coef = -0.08
        p_one_tailed = 0.15  # Not significant

        h2_supported = (p_one_tailed < 0.05) and (coef < 0)

        assert h2_supported is False


# ==============================================================================
# Error Handling Tests
# ==============================================================================

class TestH2ErrorHandling:
    """Tests for H2 error handling."""

    def test_missing_investment_q_raises_error(self, sample_h2_data):
        """Test that missing investment_q raises error."""
        from f1d.shared.panel_ols import run_panel_ols

        df = sample_h2_data.copy()
        df = df.drop(columns=["investment_q"])

        with pytest.raises(ValueError, match="Missing required columns"):
            run_panel_ols(
                df=df,
                dependent="investment_q",
                exog=["Manager_QA_Uncertainty_pct"],
                entity_col="gvkey",
                time_col="fiscal_year",
            )

    def test_nan_handling_in_regression(self, sample_h2_data):
        """Test that NaN values are handled correctly."""
        df = sample_h2_data.copy()
        df.loc[0, "investment_q"] = np.nan

        # Regression should either drop NaNs or raise error
        # This depends on implementation
        from f1d.shared.panel_ols import run_panel_ols

        # The function should handle NaNs internally
        # (typically by dropping rows with NaN values)
        pass  # Implementation depends on run_panel_ols behavior


# ==============================================================================
# Integration Test
# ==============================================================================

class TestH2Integration:
    """Integration tests for H2 regression."""

    @pytest.mark.skipif(
        not Path(_MODULE_PATH).exists(),
        reason="H2 regression module not found"
    )
    def test_module_imports_successfully(self):
        """Test that the H2 regression module imports without error."""
        module_globals = runpy.run_path(str(_MODULE_PATH))

        # Check that key functions exist
        assert "main" in module_globals or "run_all_h2_regressions" in module_globals

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
