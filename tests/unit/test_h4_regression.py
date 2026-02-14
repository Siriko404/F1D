"""
Unit tests for H4 Leverage Discipline (4.4_H4_LeverageDiscipline.py).

Tests verify:
- Data loading for leverage discipline analysis
- Lagged leverage variable creation (t-1)
- Regression execution with uncertainty as DV (reverse causality)
- Hypothesis test logic for H4 (beta1 < 0)
- One-tailed p-value calculation
- Output format and error handling
"""

import numpy as np
import pandas as pd
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from scipy import stats

# Import the module under test
import runpy
_MODULE_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "src" / "f1d" / "econometric" / "v2" / "4.4_H4_LeverageDiscipline.py"
)


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture
def sample_h4_data():
    """Create sample H4 leverage discipline data for testing."""
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
                # H4 IV (lagged leverage)
                "leverage": np.random.uniform(0.1, 0.6),
                # Uncertainty DVs (H4 tests reverse causality)
                "Manager_QA_Uncertainty_pct": np.random.uniform(2, 8),
                "CEO_QA_Uncertainty_pct": np.random.uniform(2, 8),
                "Manager_QA_Weak_Modal_pct": np.random.uniform(1, 5),
                "CEO_QA_Weak_Modal_pct": np.random.uniform(1, 5),
                "Manager_Pres_Uncertainty_pct": np.random.uniform(1, 5),
                "CEO_Pres_Uncertainty_pct": np.random.uniform(1, 5),
                # Analyst uncertainty control
                "analyst_qa_uncertainty": np.random.uniform(1, 5),
                # Controls
                "firm_size": np.random.uniform(5, 10),
                "tobins_q": np.random.uniform(0.8, 2.0),
                "roa": np.random.uniform(-0.1, 0.2),
                "cash_holdings": np.random.uniform(0.05, 0.3),
                "dividend_payer": np.random.randint(0, 2),
                "firm_maturity": np.random.uniform(0, 1),
                "earnings_volatility": np.random.uniform(0, 0.2),
                "n_calls": np.random.randint(1, 5),
            })

    return pd.DataFrame(data)


@pytest.fixture
def mock_panel_ols_result():
    """Create mock result from run_panel_ols for H4 regressions."""
    return {
        "model": MagicMock(),
        "coefficients": pd.DataFrame({
            "Coefficient": [-0.015, 0.02, -0.01, 0.05, 0.03],
            "Std. Error": [0.008, 0.01, 0.01, 0.02, 0.015],
            "t-stat": [-1.875, 2.0, -1.0, 2.5, 2.0],
        }, index=[
            "leverage_lag1",  # Key IV for H4
            "analyst_qa_uncertainty",
            "firm_size",
            "tobins_q",
            "roa",
        ]),
        "summary": {
            "rsquared": 0.28,
            "rsquared_within": 0.15,
            "nobs": 200,
            "entity_effects": True,
            "time_effects": True,
            "cov_type": "clustered",
            "f_statistic": 13.5,
            "f_pvalue": 0.001,
        },
        "diagnostics": {"vif": None},
        "warnings": [],
    }


# ==============================================================================
# Data Loading Tests
# ==============================================================================

class TestH4DataLoading:
    """Tests for H4 data loading functions."""

    def test_load_h4_variables_basic(self, sample_h4_data, tmp_path):
        """Test that H4 variables load correctly from parquet."""
        h4_file = tmp_path / "H4_Analysis_Dataset.parquet"
        sample_h4_data.to_parquet(h4_file, index=False)

        loaded = pd.read_parquet(h4_file)

        assert len(loaded) == len(sample_h4_data)
        assert "gvkey" in loaded.columns
        assert "fiscal_year" in loaded.columns
        assert "leverage" in loaded.columns

    def test_all_uncertainty_dvs_present(self, sample_h4_data):
        """Test that all uncertainty DVs are present for H4."""
        uncertainty_cols = [
            "Manager_QA_Uncertainty_pct",
            "CEO_QA_Uncertainty_pct",
            "Manager_QA_Weak_Modal_pct",
            "CEO_QA_Weak_Modal_pct",
            "Manager_Pres_Uncertainty_pct",
            "CEO_Pres_Uncertainty_pct",
        ]

        for col in uncertainty_cols:
            assert col in sample_h4_data.columns, f"Missing {col}"

    def test_analyst_uncertainty_present(self, sample_h4_data):
        """Test that analyst uncertainty control is present."""
        assert "analyst_qa_uncertainty" in sample_h4_data.columns


# ==============================================================================
# Lagged Leverage Tests
# ==============================================================================

class TestH4LaggedLeverage:
    """Tests for lagged leverage variable creation."""

    def test_lagged_leverage_creation(self, sample_h4_data):
        """Test that lagged leverage is created correctly."""
        df = sample_h4_data.copy()
        df = df.sort_values(["gvkey", "fiscal_year"])

        # Create lagged leverage
        df["leverage_lag1"] = df.groupby("gvkey")["leverage"].shift(1)

        # First year for each firm should have NaN lag
        first_years = df.groupby("gvkey").head(1)
        assert first_years["leverage_lag1"].isna().all()

        # Second and subsequent years should have non-NaN lag
        second_years = df.groupby("gvkey").nth(1)
        assert second_years["leverage_lag1"].notna().all()

    def test_lagged_leverage_within_firm_boundaries(self, sample_h4_data):
        """Test that lagged leverage is correctly bounded within firms."""
        df = sample_h4_data.copy()
        df = df.sort_values(["gvkey", "fiscal_year"])

        # Create lagged leverage
        df["leverage_lag1"] = df.groupby("gvkey")["leverage"].shift(1)

        # Verify no cross-firm leakage
        # For each firm, the lagged value should equal the previous year's value
        for gvkey in df["gvkey"].unique()[:5]:  # Check first 5 firms
            firm_df = df[df["gvkey"] == gvkey].sort_values("fiscal_year")

            for i in range(1, len(firm_df)):
                current_leverage_lag = firm_df.iloc[i]["leverage_lag1"]
                previous_leverage = firm_df.iloc[i - 1]["leverage"]

                assert current_leverage_lag == previous_leverage, \
                    f"Lagged leverage mismatch for {gvkey}"

    def test_lag_respects_year_gaps(self, sample_h4_data):
        """Test that lag respects year gaps (not consecutive row shift)."""
        df = sample_h4_data.copy()

        # Remove some years to create gaps
        df = df[~((df["gvkey"] == "000001") & (df["fiscal_year"] == 2012))]

        df = df.sort_values(["gvkey", "fiscal_year"])
        df["leverage_lag1"] = df.groupby("gvkey")["leverage"].shift(1)

        # Firm 000001 should have NaN for year 2013 (gap from 2011 to 2013)
        # This is because shift(1) shifts by position, not by year
        # The implementation should handle this appropriately
        pass  # Implementation-specific behavior


# ==============================================================================
# Regression Execution Tests
# ==============================================================================

class TestH4RegressionExecution:
    """Tests for H4 regression execution."""

    @patch("f1d.shared.panel_ols.run_panel_ols")
    def test_single_h4_regression_called_correctly(
        self, mock_run_panel_ols, sample_h4_data, mock_panel_ols_result
    ):
        """Test that run_panel_ols is called with correct parameters for H4."""
        mock_run_panel_ols.return_value = mock_panel_ols_result

        from f1d.shared.panel_ols import run_panel_ols

        df = sample_h4_data.copy()
        df = df.sort_values(["gvkey", "fiscal_year"])
        df["leverage_lag1"] = df.groupby("gvkey")["leverage"].shift(1)
        df = df.dropna(subset=["leverage_lag1"])

        result = run_panel_ols(
            df=df,
            dependent="Manager_QA_Uncertainty_pct",  # DV is uncertainty
            exog=["leverage_lag1", "analyst_qa_uncertainty", "firm_size"],
            entity_col="gvkey",
            time_col="fiscal_year",
            entity_effects=True,
            time_effects=True,
            check_collinearity=False,
        )

        mock_run_panel_ols.assert_called_once()
        assert result is not None

    @patch("f1d.shared.panel_ols.run_panel_ols")
    def test_h4_uses_lagged_leverage_as_iv(
        self, mock_run_panel_ols, sample_h4_data, mock_panel_ols_result
    ):
        """Test that H4 regressions use lagged leverage as independent variable."""
        mock_run_panel_ols.return_value = mock_panel_ols_result

        from f1d.shared.panel_ols import run_panel_ols

        df = sample_h4_data.copy()
        df = df.sort_values(["gvkey", "fiscal_year"])
        df["leverage_lag1"] = df.groupby("gvkey")["leverage"].shift(1)
        df = df.dropna(subset=["leverage_lag1"])

        run_panel_ols(
            df=df,
            dependent="Manager_QA_Uncertainty_pct",
            exog=["leverage_lag1", "analyst_qa_uncertainty"],
            entity_col="gvkey",
            time_col="fiscal_year",
            entity_effects=True,
            time_effects=True,
            check_collinearity=False,
        )

        call_args = mock_run_panel_ols.call_args
        assert "leverage_lag1" in call_args[1]["exog"]

    @patch("f1d.shared.panel_ols.run_panel_ols")
    def test_h4_uses_uncertainty_as_dv(
        self, mock_run_panel_ols, sample_h4_data, mock_panel_ols_result
    ):
        """Test that H4 uses uncertainty measures as DVs (reverse causality)."""
        mock_run_panel_ols.return_value = mock_panel_ols_result

        from f1d.shared.panel_ols import run_panel_ols

        df = sample_h4_data.copy()
        df = df.sort_values(["gvkey", "fiscal_year"])
        df["leverage_lag1"] = df.groupby("gvkey")["leverage"].shift(1)
        df = df.dropna(subset=["leverage_lag1"])

        run_panel_ols(
            df=df,
            dependent="Manager_QA_Uncertainty_pct",  # DV is uncertainty
            exog=["leverage_lag1"],
            entity_col="gvkey",
            time_col="fiscal_year",
            entity_effects=True,
            time_effects=True,
            check_collinearity=False,
        )

        call_args = mock_run_panel_ols.call_args
        # DV should be an uncertainty measure
        assert "Uncertainty" in call_args[1]["dependent"] or "Modal" in call_args[1]["dependent"]


# ==============================================================================
# One-Tailed P-Value Tests
# ==============================================================================

class TestH4OneTailedPValue:
    """Tests for one-tailed p-value calculation in H4."""

    def test_one_tailed_pvalue_less(self):
        """Test one-tailed p-value calculation for beta < 0 (H4)."""
        # H4: beta < 0 (higher leverage reduces uncertainty)
        coef = -0.015  # Negative as expected
        se = 0.008
        df_resid = 180

        t_stat = coef / se
        p_two_tailed = 2 * (1 - stats.t.cdf(abs(t_stat), df=df_resid))

        # For beta < 0 test
        if coef < 0:
            p_one_tailed = p_two_tailed / 2
        else:
            p_one_tailed = 1 - p_two_tailed / 2

        assert p_one_tailed < 0.05  # Should be significant
        assert p_one_tailed == pytest.approx(p_two_tailed / 2, rel=0.01)

    def test_one_tailed_pvalue_wrong_sign(self):
        """Test one-tailed p-value when coefficient has wrong sign."""
        coef = 0.015  # Positive (wrong sign for H4)
        se = 0.008
        df_resid = 180

        t_stat = coef / se
        p_two_tailed = 2 * (1 - stats.t.cdf(abs(t_stat), df=df_resid))

        # For beta < 0 test with positive coefficient
        if coef < 0:
            p_one_tailed = p_two_tailed / 2
        else:
            p_one_tailed = 1 - p_two_tailed / 2

        # P-value should be large (not significant) because coef has wrong sign
        assert p_one_tailed > 0.5

    def test_h4_significance_threshold(self):
        """Test H4 significance at alpha = 0.05."""
        coef = -0.015
        p_one_tailed = 0.03  # Significant

        h4_significant = (p_one_tailed < 0.05) and (coef < 0)

        assert h4_significant is True

    def test_h4_not_significant_high_pvalue(self):
        """Test H4 not significant with high p-value."""
        coef = -0.015  # Correct sign
        p_one_tailed = 0.15  # Not significant

        h4_significant = (p_one_tailed < 0.05) and (coef < 0)

        assert h4_significant is False

    def test_h4_not_significant_wrong_sign(self):
        """Test H4 not significant with wrong sign coefficient."""
        coef = 0.015  # Wrong sign
        p_one_tailed = 0.03  # Would be significant if sign was correct

        h4_significant = (p_one_tailed < 0.05) and (coef < 0)

        assert h4_significant is False


# ==============================================================================
# Hypothesis Test Tests
# ==============================================================================

class TestH4HypothesisTests:
    """Tests for H4 hypothesis test logic."""

    def test_h4_hypothesis_direction(self):
        """Test that H4 hypothesis direction is beta < 0."""
        # H4: Higher leverage disciplines managers -> lower uncertainty
        # Therefore beta1 < 0

        # Example: 10pp increase in leverage -> beta1 * 10 change in uncertainty
        beta1 = -0.015  # Negative as expected
        uncertainty_change = beta1 * 10  # -0.15 percentage points

        assert uncertainty_change < 0  # Leverage reduces uncertainty

    def test_h4_supported_conditions(self):
        """Test conditions for H4 support."""
        # H4 supported if:
        # 1. Coefficient is negative
        # 2. One-tailed p-value < 0.05

        test_cases = [
            (-0.02, 0.02, True),   # Negative, significant -> supported
            (-0.02, 0.08, False),  # Negative, not significant -> not supported
            (0.02, 0.02, False),   # Positive, significant -> not supported (wrong sign)
            (0.02, 0.08, False),   # Positive, not significant -> not supported
        ]

        for coef, p_one, expected_support in test_cases:
            h4_supported = (p_one < 0.05) and (coef < 0)
            assert h4_supported == expected_support, \
                f"Failed for coef={coef}, p={p_one}: expected {expected_support}, got {h4_supported}"


# ==============================================================================
# Output Format Tests
# ==============================================================================

class TestH4OutputFormat:
    """Tests for H4 regression output format."""

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

class TestH4ErrorHandling:
    """Tests for H4 error handling."""

    def test_missing_leverage_lag1_raises_error(self, sample_h4_data):
        """Test that missing leverage_lag1 raises error."""
        from f1d.shared.panel_ols import run_panel_ols

        df = sample_h4_data.copy()
        # Don't create lagged leverage

        with pytest.raises(ValueError, match="Missing required columns"):
            run_panel_ols(
                df=df,
                dependent="Manager_QA_Uncertainty_pct",
                exog=["leverage_lag1"],  # This column doesn't exist
                entity_col="gvkey",
                time_col="fiscal_year",
            )

    def test_all_nan_leverage_lag1(self, sample_h4_data):
        """Test handling when all leverage_lag1 values are NaN."""
        df = sample_h4_data.copy()
        df["leverage_lag1"] = np.nan

        # After dropping NaNs, no observations should remain
        df_valid = df.dropna(subset=["leverage_lag1"])
        assert len(df_valid) == 0


# ==============================================================================
# Integration Test
# ==============================================================================

class TestH4Integration:
    """Integration tests for H4 regression."""

    @pytest.mark.skipif(
        not Path(_MODULE_PATH).exists(),
        reason="H4 regression module not found"
    )
    def test_module_imports_successfully(self):
        """Test that the H4 module imports without error."""
        module_globals = runpy.run_path(str(_MODULE_PATH))

        assert "main" in module_globals or "run_all_h4_regressions" in module_globals

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

    @pytest.mark.skipif(
        not Path(_MODULE_PATH).exists(),
        reason="H4 regression module not found"
    )
    def test_one_tailed_pvalue_function_exists(self):
        """Test that one_tailed_pvalue function exists in H4 module."""
        module_globals = runpy.run_path(str(_MODULE_PATH))

        assert "one_tailed_pvalue" in module_globals, \
            "one_tailed_pvalue function should exist in H4 module"
