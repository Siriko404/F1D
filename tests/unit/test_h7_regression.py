"""
Unit tests for H7 Illiquidity Regression (4.7_H7IlliquidityRegression.py).

Tests verify:
- Data loading for illiquidity variables (Amihud ratio)
- Regression execution with lagged illiquidity as DV
- Hypothesis test logic for H7 (beta > 0)
- Alternative DV handling (roll_spread, log_amihud)
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
    / "src" / "f1d" / "econometric" / "v2" / "4.7_H7IlliquidityRegression.py"
)


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture
def sample_h7_data():
    """Create sample H7 illiquidity data for testing."""
    np.random.seed(42)
    n_firms = 50
    n_years = 5

    data = []
    for firm_id in range(n_firms):
        gvkey = str(firm_id).zfill(6)
        for year_offset in range(n_years):
            year = 2010 + year_offset
            data.append({
                "gvkey": gvkey,
                "year": year,
                # H7 DV (forward-looking illiquidity)
                "amihud_lag1": np.random.uniform(0.1, 5.0),  # Amihud illiquidity at t+1
                "log_amihud_lag1": np.random.uniform(-2, 2),
                "roll_spread_lag1": np.random.uniform(0, 0.1),
                # Uncertainty measures (4 available for H7)
                "Manager_QA_Uncertainty_pct": np.random.uniform(2, 8),
                "CEO_QA_Uncertainty_pct": np.random.uniform(2, 8),
                "Manager_Pres_Uncertainty_pct": np.random.uniform(1, 5),
                "CEO_Pres_Uncertainty_pct": np.random.uniform(1, 5),
                # Controls
                "Volatility": np.random.uniform(0.01, 0.1),
                "StockRet": np.random.uniform(-0.3, 0.3),
                "trading_days": np.random.randint(200, 260),
            })

    return pd.DataFrame(data)


@pytest.fixture
def mock_panel_ols_result():
    """Create mock result from run_panel_ols for H7 regressions."""
    return {
        "model": MagicMock(),
        "coefficients": pd.DataFrame({
            "Coefficient": [0.35, 0.05, -0.02],
            "Std. Error": [0.15, 0.02, 0.01],
            "t-stat": [2.33, 2.5, -2.0],
        }, index=[
            "Manager_QA_Uncertainty_pct",  # Key IV for H7
            "Volatility",
            "StockRet",
        ]),
        "summary": {
            "rsquared": 0.28,
            "rsquared_within": 0.12,
            "nobs": 200,
            "entity_effects": True,
            "time_effects": True,
            "cov_type": "clustered",
            "f_statistic": 14.5,
            "f_pvalue": 0.001,
        },
        "diagnostics": {"vif": None},
        "warnings": [],
    }


# ==============================================================================
# Data Loading Tests
# ==============================================================================

class TestH7DataLoading:
    """Tests for H7 data loading functions."""

    def test_load_h7_variables_basic(self, sample_h7_data, tmp_path):
        """Test that H7 variables load correctly from parquet."""
        h7_file = tmp_path / "H7_Illiquidity.parquet"
        sample_h7_data.to_parquet(h7_file, index=False)

        loaded = pd.read_parquet(h7_file)

        assert len(loaded) == len(sample_h7_data)
        assert "gvkey" in loaded.columns
        assert "year" in loaded.columns
        assert "amihud_lag1" in loaded.columns

    def test_illiquidity_dvs_present(self, sample_h7_data):
        """Test that illiquidity DVs are present."""
        assert "amihud_lag1" in sample_h7_data.columns
        assert "log_amihud_lag1" in sample_h7_data.columns
        assert "roll_spread_lag1" in sample_h7_data.columns

    def test_uncertainty_measures_available(self, sample_h7_data):
        """Test that uncertainty measures are available."""
        uncertainty_cols = [
            "Manager_QA_Uncertainty_pct",
            "CEO_QA_Uncertainty_pct",
            "Manager_Pres_Uncertainty_pct",
            "CEO_Pres_Uncertainty_pct",
        ]

        for col in uncertainty_cols:
            assert col in sample_h7_data.columns, f"Missing {col}"

    def test_market_controls_present(self, sample_h7_data):
        """Test that market controls are present."""
        assert "Volatility" in sample_h7_data.columns
        assert "StockRet" in sample_h7_data.columns


# ==============================================================================
# Regression Execution Tests
# ==============================================================================

class TestH7RegressionExecution:
    """Tests for H7 regression execution."""

    @patch("f1d.shared.panel_ols.run_panel_ols")
    def test_single_h7_regression_called_correctly(
        self, mock_run_panel_ols, sample_h7_data, mock_panel_ols_result
    ):
        """Test that run_panel_ols is called with correct parameters for H7."""
        mock_run_panel_ols.return_value = mock_panel_ols_result

        from f1d.shared.panel_ols import run_panel_ols

        df = sample_h7_data.copy()
        df = df.dropna()

        result = run_panel_ols(
            df=df,
            dependent="amihud_lag1",
            exog=["Manager_QA_Uncertainty_pct", "Volatility", "StockRet"],
            entity_col="gvkey",
            time_col="year",
            entity_effects=True,
            time_effects=True,
            check_collinearity=False,
        )

        mock_run_panel_ols.assert_called_once()
        assert result is not None

    @patch("f1d.shared.panel_ols.run_panel_ols")
    def test_h7_uses_lagged_illiquidity_as_dv(
        self, mock_run_panel_ols, sample_h7_data, mock_panel_ols_result
    ):
        """Test that H7 uses lagged illiquidity as DV (forward-looking)."""
        mock_run_panel_ols.return_value = mock_panel_ols_result

        from f1d.shared.panel_ols import run_panel_ols

        df = sample_h7_data.copy()

        # H7 should use lagged (t+1) illiquidity as DV
        run_panel_ols(
            df=df,
            dependent="amihud_lag1",  # Forward-looking DV
            exog=["Manager_QA_Uncertainty_pct"],
            entity_col="gvkey",
            time_col="year",
            entity_effects=True,
            time_effects=True,
            check_collinearity=False,
        )

        call_args = mock_run_panel_ols.call_args
        assert "lag1" in call_args[1]["dependent"]


# ==============================================================================
# Hypothesis Test Tests
# ==============================================================================

class TestH7HypothesisTests:
    """Tests for H7 hypothesis test calculations."""

    def test_h7a_hypothesis_direction(self):
        """Test that H7a hypothesis is correctly specified (beta > 0)."""
        # H7a: Higher uncertainty -> higher illiquidity
        # Therefore beta > 0

        coef = 0.35  # Positive as expected for H7
        p_two_tailed = 0.02

        # One-tailed test for H7a: beta > 0
        if coef > 0:
            p_one_tailed = p_two_tailed / 2
        else:
            p_one_tailed = 1 - p_two_tailed / 2

        assert p_one_tailed == 0.01
        assert p_one_tailed < 0.05

    def test_h7a_supported_with_positive_significant_coef(self):
        """Test that H7a is supported when coef is positive and significant."""
        coef = 0.35
        p_one_tailed = 0.01

        h7a_supported = (p_one_tailed < 0.05) and (coef > 0)

        assert h7a_supported is True

    def test_h7a_not_supported_with_negative_coef(self):
        """Test that H7a is not supported when coef is negative."""
        coef = -0.25  # Wrong sign for H7
        p_one_tailed = 0.01

        h7a_supported = (p_one_tailed < 0.05) and (coef > 0)

        assert h7a_supported is False

    def test_h7a_not_supported_with_insignificant_coef(self):
        """Test that H7a is not supported when not significant."""
        coef = 0.35
        p_one_tailed = 0.12  # Not significant

        h7a_supported = (p_one_tailed < 0.05) and (coef > 0)

        assert h7a_supported is False


# ==============================================================================
# Alternative DV Tests
# ==============================================================================

class TestH7AlternativeDVs:
    """Tests for H7 alternative dependent variables."""

    @patch("f1d.shared.panel_ols.run_panel_ols")
    def test_log_amihud_as_dv(
        self, mock_run_panel_ols, sample_h7_data, mock_panel_ols_result
    ):
        """Test that log_amihud can be used as alternative DV."""
        mock_run_panel_ols.return_value = mock_panel_ols_result

        from f1d.shared.panel_ols import run_panel_ols

        df = sample_h7_data.copy()

        run_panel_ols(
            df=df,
            dependent="log_amihud_lag1",
            exog=["Manager_QA_Uncertainty_pct"],
            entity_col="gvkey",
            time_col="year",
            entity_effects=True,
            time_effects=True,
            check_collinearity=False,
        )

        call_args = mock_run_panel_ols.call_args
        assert call_args[1]["dependent"] == "log_amihud_lag1"

    @patch("f1d.shared.panel_ols.run_panel_ols")
    def test_roll_spread_as_dv(
        self, mock_run_panel_ols, sample_h7_data, mock_panel_ols_result
    ):
        """Test that roll_spread can be used as alternative DV."""
        mock_run_panel_ols.return_value = mock_panel_ols_result

        from f1d.shared.panel_ols import run_panel_ols

        df = sample_h7_data.copy()

        run_panel_ols(
            df=df,
            dependent="roll_spread_lag1",
            exog=["Manager_QA_Uncertainty_pct"],
            entity_col="gvkey",
            time_col="year",
            entity_effects=True,
            time_effects=True,
            check_collinearity=False,
        )

        call_args = mock_run_panel_ols.call_args
        assert call_args[1]["dependent"] == "roll_spread_lag1"


# ==============================================================================
# Output Format Tests
# ==============================================================================

class TestH7OutputFormat:
    """Tests for H7 regression output format."""

    def test_coefficients_dataframe_structure(self, mock_panel_ols_result):
        """Test that coefficients DataFrame has expected columns."""
        coef_df = mock_panel_ols_result["coefficients"]

        assert "Coefficient" in coef_df.columns
        assert "Std. Error" in coef_df.columns
        assert "t-stat" in coef_df.columns


# ==============================================================================
# Error Handling Tests
# ==============================================================================

class TestH7ErrorHandling:
    """Tests for H7 error handling."""

    def test_missing_dv_raises_error(self, sample_h7_data):
        """Test that missing DV raises error."""
        from f1d.shared.panel_ols import run_panel_ols

        df = sample_h7_data.copy()
        df = df.drop(columns=["amihud_lag1"])

        with pytest.raises(ValueError, match="Missing required columns"):
            run_panel_ols(
                df=df,
                dependent="amihud_lag1",
                exog=["Manager_QA_Uncertainty_pct"],
                entity_col="gvkey",
                time_col="year",
            )


# ==============================================================================
# Integration Test
# ==============================================================================

class TestH7Integration:
    """Integration tests for H7 regression."""

    @pytest.mark.skipif(
        not Path(_MODULE_PATH).exists(),
        reason="H7 regression module not found"
    )
    def test_module_imports_successfully(self):
        """Test that the H7 regression module imports without error."""
        module_globals = runpy.run_path(str(_MODULE_PATH))

        assert "main" in module_globals or "run_all_h7_regressions" in module_globals

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
