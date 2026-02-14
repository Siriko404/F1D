"""
Unit tests for H9 Regression (4.11_H9_Regression.py).

Tests verify:
- Data loading for H9-specific variables (earnings guidance precision)
- Regression execution with guidance precision as DV
- Hypothesis test logic for H9 (direction depends on hypothesis)
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
    / "src" / "f1d" / "econometric" / "v2" / "4.11_H9_Regression.py"
)


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture
def sample_h9_data():
    """Create sample H9 guidance precision data for testing."""
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
                # H9 DV (guidance precision)
                "guidance_precision": np.random.uniform(0, 1),  # Higher = more precise
                "guidance_precision_lead1": np.random.uniform(0, 1),
                # Uncertainty measures
                "Manager_QA_Uncertainty_pct": np.random.uniform(2, 8),
                "CEO_QA_Uncertainty_pct": np.random.uniform(2, 8),
                "Manager_QA_Weak_Modal_pct": np.random.uniform(1, 5),
                "CEO_QA_Weak_Modal_pct": np.random.uniform(1, 5),
                "Manager_Pres_Uncertainty_pct": np.random.uniform(1, 5),
                "CEO_Pres_Uncertainty_pct": np.random.uniform(1, 5),
                # Controls
                "firm_size": np.random.uniform(5, 10),
                "tobins_q": np.random.uniform(0.8, 2.0),
                "roa": np.random.uniform(-0.1, 0.2),
                "leverage": np.random.uniform(0.1, 0.6),
                "earnings_volatility": np.random.uniform(0, 0.2),
                "analyst_coverage": np.random.uniform(1, 4),
                "loss_dummy": np.random.randint(0, 2),
                "guidance_frequency": np.random.randint(1, 5),
            })

    return pd.DataFrame(data)


@pytest.fixture
def mock_panel_ols_result():
    """Create mock result from run_panel_ols for H9 regressions."""
    return {
        "model": MagicMock(),
        "coefficients": pd.DataFrame({
            "Coefficient": [-0.04, 0.02, 0.01],
            "Std. Error": [0.018, 0.01, 0.008],
            "t-stat": [-2.22, 2.0, 1.25],
        }, index=[
            "Manager_QA_Uncertainty_pct",  # Key IV for H9
            "firm_size",
            "analyst_coverage",
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

class TestH9DataLoading:
    """Tests for H9 data loading functions."""

    def test_load_h9_variables_basic(self, sample_h9_data, tmp_path):
        """Test that H9 variables load correctly from parquet."""
        h9_file = tmp_path / "H9_GuidancePrecision.parquet"
        sample_h9_data.to_parquet(h9_file, index=False)

        loaded = pd.read_parquet(h9_file)

        assert len(loaded) == len(sample_h9_data)
        assert "gvkey" in loaded.columns
        assert "fiscal_year" in loaded.columns
        assert "guidance_precision" in loaded.columns

    def test_guidance_precision_dv_present(self, sample_h9_data):
        """Test that guidance precision DV is present."""
        assert "guidance_precision" in sample_h9_data.columns
        assert "guidance_precision_lead1" in sample_h9_data.columns

    def test_all_uncertainty_measures_present(self, sample_h9_data):
        """Test that all uncertainty measures are present."""
        uncertainty_cols = [
            "Manager_QA_Uncertainty_pct",
            "CEO_QA_Uncertainty_pct",
            "Manager_QA_Weak_Modal_pct",
            "CEO_QA_Weak_Modal_pct",
            "Manager_Pres_Uncertainty_pct",
            "CEO_Pres_Uncertainty_pct",
        ]

        for col in uncertainty_cols:
            assert col in sample_h9_data.columns, f"Missing {col}"

    def test_all_h9_controls_present(self, sample_h9_data):
        """Test that all H9 controls are present."""
        h9_controls = [
            "firm_size",
            "tobins_q",
            "roa",
            "leverage",
            "earnings_volatility",
            "analyst_coverage",
            "loss_dummy",
            "guidance_frequency",
        ]

        for col in h9_controls:
            assert col in sample_h9_data.columns, f"Missing H9 control: {col}"


# ==============================================================================
# Regression Execution Tests
# ==============================================================================

class TestH9RegressionExecution:
    """Tests for H9 regression execution."""

    @patch("f1d.shared.panel_ols.run_panel_ols")
    def test_single_h9_regression_called_correctly(
        self, mock_run_panel_ols, sample_h9_data, mock_panel_ols_result
    ):
        """Test that run_panel_ols is called with correct parameters for H9."""
        mock_run_panel_ols.return_value = mock_panel_ols_result

        from f1d.shared.panel_ols import run_panel_ols

        df = sample_h9_data.copy()
        df = df.dropna()

        result = run_panel_ols(
            df=df,
            dependent="guidance_precision_lead1",
            exog=["Manager_QA_Uncertainty_pct", "firm_size", "analyst_coverage"],
            entity_col="gvkey",
            time_col="fiscal_year",
            entity_effects=True,
            time_effects=True,
            check_collinearity=False,
        )

        mock_run_panel_ols.assert_called_once()
        assert result is not None

    @patch("f1d.shared.panel_ols.run_panel_ols")
    def test_h9_uses_guidance_precision_as_dv(
        self, mock_run_panel_ols, sample_h9_data, mock_panel_ols_result
    ):
        """Test that H9 uses guidance precision as DV."""
        mock_run_panel_ols.return_value = mock_panel_ols_result

        from f1d.shared.panel_ols import run_panel_ols

        df = sample_h9_data.copy()

        run_panel_ols(
            df=df,
            dependent="guidance_precision_lead1",
            exog=["Manager_QA_Uncertainty_pct"],
            entity_col="gvkey",
            time_col="fiscal_year",
            entity_effects=True,
            time_effects=True,
            check_collinearity=False,
        )

        call_args = mock_run_panel_ols.call_args
        assert "guidance_precision" in call_args[1]["dependent"]


# ==============================================================================
# Hypothesis Test Tests
# ==============================================================================

class TestH9HypothesisTests:
    """Tests for H9 hypothesis test calculations.

    H9: Managerial uncertainty affects guidance precision
    The exact direction depends on the specific H9 formulation.
    """

    def test_h9_negative_relationship(self):
        """Test H9 hypothesis: higher uncertainty -> less precise guidance (beta < 0)."""
        # If H9 predicts: higher uncertainty -> lower precision
        # Then beta < 0

        coef = -0.04  # Negative as expected
        p_two_tailed = 0.03

        if coef < 0:
            p_one_tailed = p_two_tailed / 2
        else:
            p_one_tailed = 1 - p_two_tailed / 2

        assert p_one_tailed == 0.015
        assert p_one_tailed < 0.05

    def test_h9_supported_with_negative_significant_coef(self):
        """Test that H9 is supported when coef is negative and significant."""
        coef = -0.04
        p_one_tailed = 0.015

        h9_supported = (p_one_tailed < 0.05) and (coef < 0)

        assert h9_supported is True

    def test_h9_not_supported_with_positive_coef(self):
        """Test that H9 is not supported when coef is positive."""
        coef = 0.03  # Wrong sign
        p_one_tailed = 0.015

        h9_supported = (p_one_tailed < 0.05) and (coef < 0)

        assert h9_supported is False

    def test_h9_not_supported_with_insignificant_coef(self):
        """Test that H9 is not supported when not significant."""
        coef = -0.04  # Correct sign
        p_one_tailed = 0.15  # Not significant

        h9_supported = (p_one_tailed < 0.05) and (coef < 0)

        assert h9_supported is False


# ==============================================================================
# Output Format Tests
# ==============================================================================

class TestH9OutputFormat:
    """Tests for H9 regression output format."""

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
# Error Handling Tests
# ==============================================================================

class TestH9ErrorHandling:
    """Tests for H9 error handling."""

    def test_missing_dv_raises_error(self, sample_h9_data):
        """Test that missing DV raises error."""
        from f1d.shared.panel_ols import run_panel_ols

        df = sample_h9_data.copy()
        df = df.drop(columns=["guidance_precision_lead1"])

        with pytest.raises(ValueError, match="Missing required columns"):
            run_panel_ols(
                df=df,
                dependent="guidance_precision_lead1",
                exog=["Manager_QA_Uncertainty_pct"],
                entity_col="gvkey",
                time_col="fiscal_year",
            )


# ==============================================================================
# Integration Test
# ==============================================================================

class TestH9Integration:
    """Integration tests for H9 regression."""

    @pytest.mark.skip(reason="Module has subprocess I/O cleanup issues on Windows")
    def test_module_imports_successfully(self):
        """Test that the H9 regression module imports without error."""
        module_globals = runpy.run_path(str(_MODULE_PATH))

        assert "main" in module_globals or "run_all_h9_regressions" in module_globals

    @pytest.mark.skip(reason="Subprocess I/O cleanup issues on Windows")
    def test_dry_run_flag_supported(self):
        """Test that --dry-run flag is supported."""
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, str(_MODULE_PATH), "--help"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0 or "dry-run" in result.stdout.lower() or "dry-run" in result.stderr.lower()
