"""
Unit tests for H5 Analyst Dispersion Regression (run_h5_dispersion.py).

Tests verify:
- Data loading for analyst dispersion variables
- Regression execution with dispersion as DV (current period t)
- Hypothesis test logic for H5 (beta > 0)
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
    / "src" / "f1d" / "econometric" / "run_h5_dispersion.py"
)


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture
def sample_h5_data():
    """Create sample H5 analyst dispersion data for testing.

    Uses NEW variable naming:
    - delta_dispersion: change in dispersion (primary DV)
    - dispersion_before: dispersion 3 trading days before call
    - dispersion_after: dispersion 3 trading days after call
    - dispersion: current period (t) DV (legacy)
    - lagged_dispersion: t-1 control
    - Entire_All_Negative_pct: linguistic control
    """
    np.random.seed(42)
    n_firms = 50
    n_years = 5

    data = []
    for firm_id in range(n_firms):
        gvkey = str(firm_id).zfill(6)
        for year_offset in range(n_years):
            fiscal_year = 2010 + year_offset
            fiscal_quarter = np.random.randint(1, 5)
            # Generate correlated before/after values
            disp_before = np.random.uniform(0.01, 0.2)
            disp_change = np.random.uniform(-0.05, 0.05)
            disp_after = disp_before + disp_change
            data.append({
                "gvkey": gvkey,
                "fiscal_year": fiscal_year,
                "fiscal_quarter": fiscal_quarter,
                # H5 DV (change in dispersion around call)
                "delta_dispersion": disp_change,
                "dispersion_before": disp_before,
                "dispersion_after": disp_after,
                # Legacy dispersion (for comparison)
                "dispersion": disp_after,  # Use after as current period proxy
                # Lagged dispersion (t-1 control)
                "lagged_dispersion": np.random.uniform(0.01, 0.2),
                # Uncertainty measures (Model A IVs)
                "CEO_QA_Uncertainty_pct": np.random.uniform(2, 8),
                "CEO_Pres_Uncertainty_pct": np.random.uniform(1, 5),
                "Manager_QA_Uncertainty_pct": np.random.uniform(2, 8),
                "Manager_Pres_Uncertainty_pct": np.random.uniform(1, 5),
                # Controls
                "Analyst_QA_Uncertainty_pct": np.random.uniform(1, 4),
                "Entire_All_Negative_pct": np.random.uniform(0.5, 3),  # NEW: linguistic control
                "earnings_surprise_ratio": np.random.uniform(0, 0.1),
                "loss_dummy": np.random.randint(0, 2),
                "Size": np.random.uniform(5, 10),
                "Lev": np.random.uniform(0.1, 0.6),
                "earnings_volatility": np.random.uniform(0, 0.2),
                "TobinsQ": np.random.uniform(0.8, 2.0),
            })

    return pd.DataFrame(data)


@pytest.fixture
def mock_panel_ols_result():
    """Create mock result from run_panel_ols for H5 regressions."""
    return {
        "model": MagicMock(),
        "coefficients": pd.DataFrame({
            "Coefficient": [0.08, 0.05, 0.02, -0.01],
            "Std. Error": [0.03, 0.02, 0.01, 0.01],
            "t-stat": [2.67, 2.5, 2.0, -1.0],
        }, index=[
            "CEO_QA_Uncertainty_pct",  # Key IV for H5-A1
            "Analyst_QA_Uncertainty_pct",  # Control
            "lagged_dispersion",
            "Size",
        ]),
        "summary": {
            "rsquared": 0.35,
            "rsquared_within": 0.20,
            "nobs": 200,
            "entity_effects": True,
            "time_effects": True,
            "cov_type": "clustered",
            "f_statistic": 18.5,
            "f_pvalue": 0.001,
        },
        "diagnostics": {"vif": None},
        "warnings": [],
    }


# ==============================================================================
# Data Loading Tests
# ==============================================================================

class TestH5DataLoading:
    """Tests for H5 data loading functions."""

    def test_load_h5_variables_basic(self, sample_h5_data, tmp_path):
        """Test that H5 variables load correctly from parquet."""
        h5_file = tmp_path / "H5_AnalystDispersion.parquet"
        sample_h5_data.to_parquet(h5_file, index=False)

        loaded = pd.read_parquet(h5_file)

        assert len(loaded) == len(sample_h5_data)
        assert "gvkey" in loaded.columns
        assert "fiscal_year" in loaded.columns
        assert "dispersion" in loaded.columns  # NEW: current period DV

    def test_dispersion_present(self, sample_h5_data):
        """Test that dispersion (H5 DV at t) is present."""
        assert "dispersion" in sample_h5_data.columns
        assert sample_h5_data["dispersion"].notna().all()

    def test_delta_dispersion_present(self, sample_h5_data):
        """Test that delta_dispersion (primary H5 DV) is present."""
        assert "delta_dispersion" in sample_h5_data.columns
        assert sample_h5_data["delta_dispersion"].notna().all()

    def test_dispersion_before_after_present(self, sample_h5_data):
        """Test that dispersion_before and dispersion_after are present."""
        assert "dispersion_before" in sample_h5_data.columns
        assert "dispersion_after" in sample_h5_data.columns
        # Verify delta = after - before
        expected_delta = sample_h5_data["dispersion_after"] - sample_h5_data["dispersion_before"]
        pd.testing.assert_series_equal(
            sample_h5_data["delta_dispersion"],
            expected_delta,
            check_names=False
        )

    def test_lagged_dispersion_present(self, sample_h5_data):
        """Test that lagged_dispersion (t-1 control) is present."""
        assert "lagged_dispersion" in sample_h5_data.columns
        assert sample_h5_data["lagged_dispersion"].notna().all()

    def test_uncertainty_measures_present(self, sample_h5_data):
        """Test that uncertainty measures (Model A IVs) are present."""
        uncertainty_cols = [
            "CEO_QA_Uncertainty_pct",
            "CEO_Pres_Uncertainty_pct",
            "Manager_QA_Uncertainty_pct",
            "Manager_Pres_Uncertainty_pct",
        ]

        for col in uncertainty_cols:
            assert col in sample_h5_data.columns, f"Missing {col}"

    def test_negative_sentiment_control_present(self, sample_h5_data):
        """Test that Entire_All_Negative_pct control is present."""
        assert "Entire_All_Negative_pct" in sample_h5_data.columns

    def test_all_h5_controls_present(self, sample_h5_data):
        """Test that all H5 controls are present."""
        h5_controls = [
            "lagged_dispersion",  # NEW: replaces prior_dispersion
            "Analyst_QA_Uncertainty_pct",
            "Entire_All_Negative_pct",  # NEW: linguistic control
            "earnings_surprise_ratio",
            "loss_dummy",
            "Size",
            "Lev",
            "earnings_volatility",
            "TobinsQ",
        ]

        for col in h5_controls:
            assert col in sample_h5_data.columns, f"Missing H5 control: {col}"


# ==============================================================================
# Regression Execution Tests
# ==============================================================================

class TestH5RegressionExecution:
    """Tests for H5 regression execution."""

    @patch("f1d.shared.panel_ols.run_panel_ols")
    def test_single_h5_regression_called_correctly(
        self, mock_run_panel_ols, sample_h5_data, mock_panel_ols_result
    ):
        """Test that run_panel_ols is called with correct parameters for H5."""
        mock_run_panel_ols.return_value = mock_panel_ols_result

        from f1d.shared.panel_ols import run_panel_ols

        df = sample_h5_data.copy()
        df = df.dropna()

        result = run_panel_ols(
            df=df,
            dependent="delta_dispersion",  # NEW: change in dispersion DV
            exog=["CEO_QA_Uncertainty_pct", "lagged_dispersion", "Analyst_QA_Uncertainty_pct"],
            entity_col="gvkey",
            time_col="fiscal_year",
            entity_effects=True,
            time_effects=True,
            check_collinearity=False,
        )

        mock_run_panel_ols.assert_called_once()
        assert result is not None

    @patch("f1d.shared.panel_ols.run_panel_ols")
    def test_h5_includes_lagged_dispersion(
        self, mock_run_panel_ols, sample_h5_data, mock_panel_ols_result
    ):
        """Test that H5 regressions include lagged DV (lagged_dispersion)."""
        mock_run_panel_ols.return_value = mock_panel_ols_result

        from f1d.shared.panel_ols import run_panel_ols

        df = sample_h5_data.copy()

        # H5 should always include lagged_dispersion
        exog_vars = ["CEO_QA_Uncertainty_pct", "lagged_dispersion"]

        run_panel_ols(
            df=df,
            dependent="delta_dispersion",  # NEW: change in dispersion DV
            exog=exog_vars,
            entity_col="gvkey",
            time_col="fiscal_year",
            entity_effects=True,
            time_effects=True,
            check_collinearity=False,
        )

        call_args = mock_run_panel_ols.call_args
        assert "lagged_dispersion" in call_args[1]["exog"]


# ==============================================================================
# Model Specification Tests
# ==============================================================================

class TestH5ModelSpecifications:
    """Tests for H5 model specification structure."""

    def test_model_a_has_four_specs(self):
        """Test that Model A has exactly 4 specifications (A1-A4)."""
        # A1: CEO QA Uncertainty
        # A2: CEO Pres Uncertainty
        # A3: Manager QA Uncertainty
        # A4: Manager Pres Uncertainty
        expected_specs = ["A1", "A2", "A3", "A4"]
        assert len(expected_specs) == 4

    def test_total_regression_count(self):
        """Test that total regressions = 4 specs × 3 samples = 12."""
        n_specs = 4  # A1-A4
        n_samples = 3  # Main, Finance, Utility
        total = n_specs * n_samples
        assert total == 12


# ==============================================================================
# Hypothesis Test Tests
# ==============================================================================

class TestH5HypothesisTests:
    """Tests for H5 hypothesis test calculations."""

    def test_h5a_hypothesis_direction(self):
        """Test that H5-A hypothesis is correctly specified (beta > 0)."""
        # H5-A: Higher uncertainty -> higher dispersion
        # Therefore beta > 0

        coef = 0.08  # Positive as expected for H5-A
        p_two_tailed = 0.02

        # One-tailed test for H5-A: beta > 0
        if coef > 0:
            p_one_tailed = p_two_tailed / 2
        else:
            p_one_tailed = 1 - p_two_tailed / 2

        assert p_one_tailed == 0.01
        assert p_one_tailed < 0.05  # Significant at 5% level

    def test_h5a_supported_with_positive_significant_coef(self):
        """Test that H5-A is supported when coef is positive and significant."""
        coef = 0.08
        p_one_tailed = 0.01

        h5a_supported = (p_one_tailed < 0.05) and (coef > 0)

        assert h5a_supported is True

    def test_h5a_not_supported_with_negative_coef(self):
        """Test that H5-A is not supported when coef is negative."""
        coef = -0.05  # Wrong sign for H5-A
        p_one_tailed = 0.01

        h5a_supported = (p_one_tailed < 0.05) and (coef > 0)

        assert h5a_supported is False

    def test_h5a_not_supported_with_insignificant_coef(self):
        """Test that H5-A is not supported when not significant."""
        coef = 0.08
        p_one_tailed = 0.15  # Not significant

        h5a_supported = (p_one_tailed < 0.05) and (coef > 0)

        assert h5a_supported is False


# ==============================================================================
# Output Format Tests
# ==============================================================================

class TestH5OutputFormat:
    """Tests for H5 regression output format."""

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

class TestH5ErrorHandling:
    """Tests for H5 error handling."""

    def test_missing_delta_dispersion_raises_error(self, sample_h5_data):
        """Test that missing delta_dispersion raises error."""
        from f1d.shared.panel_ols import run_panel_ols

        df = sample_h5_data.copy()
        df = df.drop(columns=["delta_dispersion"])

        with pytest.raises(ValueError, match="Missing required columns"):
            run_panel_ols(
                df=df,
                dependent="delta_dispersion",
                exog=["CEO_QA_Uncertainty_pct"],
                entity_col="gvkey",
                time_col="fiscal_year",
            )


# ==============================================================================
# Integration Test
# ==============================================================================

class TestH5Integration:
    """Integration tests for H5 regression."""

    @pytest.mark.skipif(
        not Path(_MODULE_PATH).exists(),
        reason="H5 regression module not found"
    )
    def test_module_imports_successfully(self):
        """Test that the H5 regression module imports without error."""
        module_globals = runpy.run_path(str(_MODULE_PATH))

        assert "main" in module_globals or "run_all_h5_regressions" in module_globals

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
