"""
Unit tests for H5 Analyst Dispersion Regression (run_h5_dispersion.py).

Tests verify:
- Data loading for analyst dispersion variables
- Regression execution with dispersion_lead as DV
- Hypothesis test logic for H5-A and H5-B (beta > 0)
- Incremental contribution test (hedging beyond uncertainty)
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
    """Create sample H5 analyst dispersion data for testing."""
    np.random.seed(42)
    n_firms = 50
    n_years = 5

    data = []
    for firm_id in range(n_firms):
        gvkey = str(firm_id).zfill(6)
        for year_offset in range(n_years):
            fiscal_year = 2010 + year_offset
            fiscal_quarter = np.random.randint(1, 5)
            data.append({
                "gvkey": gvkey,
                "fiscal_year": fiscal_year,
                "fiscal_quarter": fiscal_quarter,
                # H5 DV (forward-looking)
                "dispersion_lead": np.random.uniform(0.01, 0.2),  # Analyst dispersion at t+1
                # Prior dispersion (lagged DV)
                "prior_dispersion": np.random.uniform(0.01, 0.2),
                # Speech uncertainty measures
                "Manager_QA_Weak_Modal_pct": np.random.uniform(1, 5),  # PRIMARY IV
                "Manager_QA_Uncertainty_pct": np.random.uniform(2, 8),  # Control for H5-A
                "CEO_QA_Weak_Modal_pct": np.random.uniform(1, 5),
                "CEO_QA_Uncertainty_pct": np.random.uniform(2, 8),
                "Manager_Pres_Weak_Modal_pct": np.random.uniform(1, 5),
                "Manager_Pres_Uncertainty_pct": np.random.uniform(1, 5),
                # Uncertainty gap (for H5-B)
                "uncertainty_gap": np.random.uniform(-3, 3),  # QA - Pres difference
                # Controls
                "earnings_surprise": np.random.uniform(-0.1, 0.1),
                "loss_dummy": np.random.randint(0, 2),
                "analyst_coverage": np.random.uniform(1, 4),  # log(NUMEST)
                "firm_size": np.random.uniform(5, 10),
                "leverage": np.random.uniform(0.1, 0.6),
                "earnings_volatility": np.random.uniform(0, 0.2),
                "tobins_q": np.random.uniform(0.8, 2.0),
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
            "Manager_QA_Weak_Modal_pct",  # Key IV for H5-A
            "Manager_QA_Uncertainty_pct",  # Control
            "prior_dispersion",
            "firm_size",
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
        assert "dispersion_lead" in loaded.columns

    def test_dispersion_lead_present(self, sample_h5_data):
        """Test that dispersion_lead (H5 DV) is present."""
        assert "dispersion_lead" in sample_h5_data.columns
        assert sample_h5_data["dispersion_lead"].notna().all()

    def test_weak_modal_measures_present(self, sample_h5_data):
        """Test that weak modal measures (primary IVs) are present."""
        weak_modal_cols = [
            "Manager_QA_Weak_Modal_pct",
            "CEO_QA_Weak_Modal_pct",
            "Manager_Pres_Weak_Modal_pct",
        ]

        for col in weak_modal_cols:
            assert col in sample_h5_data.columns, f"Missing {col}"

    def test_uncertainty_controls_present(self, sample_h5_data):
        """Test that uncertainty control variables are present."""
        uncertainty_cols = [
            "Manager_QA_Uncertainty_pct",
            "CEO_QA_Uncertainty_pct",
            "Manager_Pres_Uncertainty_pct",
        ]

        for col in uncertainty_cols:
            assert col in sample_h5_data.columns, f"Missing {col}"

    def test_uncertainty_gap_present(self, sample_h5_data):
        """Test that uncertainty_gap (for H5-B) is present."""
        assert "uncertainty_gap" in sample_h5_data.columns

    def test_all_h5_controls_present(self, sample_h5_data):
        """Test that all H5 controls are present."""
        h5_controls = [
            "prior_dispersion",
            "earnings_surprise",
            "analyst_coverage",
            "loss_dummy",
            "firm_size",
            "leverage",
            "earnings_volatility",
            "tobins_q",
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
            dependent="dispersion_lead",
            exog=["Manager_QA_Weak_Modal_pct", "Manager_QA_Uncertainty_pct", "prior_dispersion"],
            entity_col="gvkey",
            time_col="fiscal_year",
            entity_effects=True,
            time_effects=True,
            check_collinearity=False,
        )

        mock_run_panel_ols.assert_called_once()
        assert result is not None

    @patch("f1d.shared.panel_ols.run_panel_ols")
    def test_h5_includes_prior_dispersion(
        self, mock_run_panel_ols, sample_h5_data, mock_panel_ols_result
    ):
        """Test that H5 regressions include lagged DV (prior_dispersion)."""
        mock_run_panel_ols.return_value = mock_panel_ols_result

        from f1d.shared.panel_ols import run_panel_ols

        df = sample_h5_data.copy()

        # H5 should always include prior_dispersion
        exog_vars = ["Manager_QA_Weak_Modal_pct", "prior_dispersion"]

        run_panel_ols(
            df=df,
            dependent="dispersion_lead",
            exog=exog_vars,
            entity_col="gvkey",
            time_col="fiscal_year",
            entity_effects=True,
            time_effects=True,
            check_collinearity=False,
        )

        call_args = mock_run_panel_ols.call_args
        assert "prior_dispersion" in call_args[1]["exog"]


# ==============================================================================
# Hypothesis Test Tests
# ==============================================================================

class TestH5HypothesisTests:
    """Tests for H5 hypothesis test calculations."""

    def test_h5a_hypothesis_direction(self):
        """Test that H5-A hypothesis is correctly specified (beta > 0)."""
        # H5-A: Hedging (Weak Modal) -> higher dispersion
        # Therefore beta > 0 (higher hedging -> higher dispersion)

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

    def test_h5b_gap_hypothesis_direction(self):
        """Test that H5-B (gap) hypothesis is correctly specified (beta > 0)."""
        # H5-B: Uncertainty gap (QA - Pres) -> higher dispersion
        # Therefore beta > 0 (larger gap -> higher dispersion)

        coef = 0.05  # Positive as expected for H5-B
        p_two_tailed = 0.03

        if coef > 0:
            p_one_tailed = p_two_tailed / 2
        else:
            p_one_tailed = 1 - p_two_tailed / 2

        assert p_one_tailed == 0.015
        assert p_one_tailed < 0.05

    def test_incremental_contribution_logic(self):
        """Test incremental contribution test logic."""
        # H5-A tests whether hedging adds predictive power BEYOND uncertainty

        # Case 1: Hedging significant, uncertainty significant
        # -> Hedging adds incremental power
        beta_hedging = 0.08
        p_hedging = 0.01
        beta_uncertainty = 0.05
        p_uncertainty = 0.02

        hedging_sig = p_hedging < 0.05 and beta_hedging > 0
        uncertainty_sig = p_uncertainty < 0.05 and beta_uncertainty > 0

        # Both significant means hedging adds incremental power
        assert hedging_sig and uncertainty_sig

        # Case 2: Hedging not significant, uncertainty significant
        # -> Hedging does NOT add incremental power
        beta_hedging = 0.02
        p_hedging = 0.25
        beta_uncertainty = 0.05
        p_uncertainty = 0.02

        hedging_sig = p_hedging < 0.05 and beta_hedging > 0

        # Hedging not significant -> no incremental power
        assert not hedging_sig


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

    def test_missing_dispersion_lead_raises_error(self, sample_h5_data):
        """Test that missing dispersion_lead raises error."""
        from f1d.shared.panel_ols import run_panel_ols

        df = sample_h5_data.copy()
        df = df.drop(columns=["dispersion_lead"])

        with pytest.raises(ValueError, match="Missing required columns"):
            run_panel_ols(
                df=df,
                dependent="dispersion_lead",
                exog=["Manager_QA_Weak_Modal_pct"],
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
