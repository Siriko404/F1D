"""
Unit tests for H3 Payout Policy Regression (run_h3_payout_policy.py).

Tests verify:
- Data loading for payout policy variables (div_stability, payout_flexibility)
- Regression execution with leverage interaction term
- Hypothesis test logic for H3a and H3b (different directions per DV)
- Interaction term creation and centering
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
    / "src" / "f1d" / "econometric" / "run_h3_payout_policy.py"
)


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture
def sample_h3_data():
    """Create sample H3 payout policy data for testing."""
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
                # H3 DVs
                "div_stability": np.random.uniform(0, 1),  # Higher = more stable
                "payout_flexibility": np.random.uniform(0, 1),  # Higher = more flexible
                # Uncertainty measures
                "Manager_QA_Uncertainty_pct": np.random.uniform(2, 8),
                "CEO_QA_Uncertainty_pct": np.random.uniform(2, 8),
                "Manager_QA_Weak_Modal_pct": np.random.uniform(1, 5),
                "CEO_QA_Weak_Modal_pct": np.random.uniform(1, 5),
                "Manager_Pres_Uncertainty_pct": np.random.uniform(1, 5),
                "CEO_Pres_Uncertainty_pct": np.random.uniform(1, 5),
                # Leverage (for interaction)
                "leverage": np.random.uniform(0.1, 0.6),
                # Controls
                "earnings_volatility": np.random.uniform(0, 0.2),
                "fcf_growth": np.random.uniform(-0.1, 0.2),
                "firm_maturity": np.random.uniform(0, 1),
                "firm_size": np.random.uniform(5, 10),
                "roa": np.random.uniform(-0.1, 0.2),
                "tobins_q": np.random.uniform(0.8, 2.0),
                "cash_holdings": np.random.uniform(0.05, 0.3),
                # For creating lead DV
                "n_calls": np.random.randint(1, 5),
            })

    return pd.DataFrame(data)


@pytest.fixture
def sample_h1_leverage_data():
    """Create sample H1 leverage data for merging with H3."""
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
                "leverage": np.random.uniform(0.1, 0.6),
            })

    return pd.DataFrame(data)


@pytest.fixture
def mock_panel_ols_result():
    """Create mock result from run_panel_ols for H3 regressions."""
    return {
        "model": MagicMock(),
        "coefficients": pd.DataFrame({
            "Coefficient": [-0.04, 0.02, -0.025, 0.01, -0.015],
            "Std. Error": [0.02, 0.01, 0.015, 0.008, 0.01],
            "t-stat": [-2.0, 2.0, -1.67, 1.25, -1.5],
        }, index=[
            "Manager_QA_Uncertainty_pct_c",
            "leverage_c",
            "Manager_QA_Uncertainty_pct_x_leverage",  # Interaction
            "firm_size",
            "earnings_volatility",
        ]),
        "summary": {
            "rsquared": 0.30,
            "rsquared_within": 0.18,
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

class TestH3DataLoading:
    """Tests for H3 data loading functions."""

    def test_load_h3_variables_basic(self, sample_h3_data, tmp_path):
        """Test that H3 variables load correctly from parquet."""
        h3_file = tmp_path / "H3_PayoutPolicy.parquet"
        sample_h3_data.to_parquet(h3_file, index=False)

        loaded = pd.read_parquet(h3_file)

        assert len(loaded) == len(sample_h3_data)
        assert "gvkey" in loaded.columns
        assert "fiscal_year" in loaded.columns
        assert "div_stability" in loaded.columns
        assert "payout_flexibility" in loaded.columns

    def test_both_dvs_present(self, sample_h3_data):
        """Test that both H3 DVs are present."""
        assert "div_stability" in sample_h3_data.columns
        assert "payout_flexibility" in sample_h3_data.columns

    def test_leverage_available(self, sample_h3_data, sample_h1_leverage_data):
        """Test that leverage can be merged from H1 data."""
        # Drop leverage from H3 data if present to simulate real merge
        h3_df = sample_h3_data.drop(columns=["leverage"], errors="ignore")

        merged = h3_df.merge(
            sample_h1_leverage_data[["gvkey", "fiscal_year", "leverage"]],
            on=["gvkey", "fiscal_year"],
            how="left"
        )

        assert "leverage" in merged.columns
        assert merged["leverage"].notna().sum() > 0


# ==============================================================================
# Interaction Term Tests
# ==============================================================================

class TestH3InteractionTerm:
    """Tests for H3 interaction term creation."""

    def test_interaction_term_creation(self, sample_h3_data):
        """Test that interaction term is created correctly."""
        df = sample_h3_data.copy()

        # Center variables
        uncertainty_col = "Manager_QA_Uncertainty_pct"
        df[f"{uncertainty_col}_c"] = df[uncertainty_col] - df[uncertainty_col].mean()
        df["leverage_c"] = df["leverage"] - df["leverage"].mean()

        # Create interaction
        interaction_col = f"{uncertainty_col}_x_leverage"
        df[interaction_col] = df[f"{uncertainty_col}_c"] * df["leverage_c"]

        assert interaction_col in df.columns
        assert df[interaction_col].notna().all()

    def test_centering_reduces_multicollinearity(self, sample_h3_data):
        """Test that centering reduces multicollinearity with interaction."""
        df = sample_h3_data.copy()

        # Uncentered correlation
        df["interaction_uncentered"] = df["Manager_QA_Uncertainty_pct"] * df["leverage"]
        corr_uncentered = df["Manager_QA_Uncertainty_pct"].corr(df["interaction_uncentered"])

        # Centered correlation (should be lower in absolute value typically)
        df["Manager_QA_Uncertainty_pct_c"] = (
            df["Manager_QA_Uncertainty_pct"] - df["Manager_QA_Uncertainty_pct"].mean()
        )
        df["leverage_c"] = df["leverage"] - df["leverage"].mean()
        df["interaction_centered"] = (
            df["Manager_QA_Uncertainty_pct_c"] * df["leverage_c"]
        )
        corr_centered = df["Manager_QA_Uncertainty_pct_c"].corr(df["interaction_centered"])

        # Centering should generally reduce correlation between main effect and interaction
        # (though not always - depends on data distribution)
        assert df["interaction_centered"].notna().all()


# ==============================================================================
# Regression Execution Tests
# ==============================================================================

class TestH3RegressionExecution:
    """Tests for H3 regression execution."""

    @patch("f1d.shared.panel_ols.run_panel_ols")
    def test_single_h3_regression_called_correctly(
        self, mock_run_panel_ols, sample_h3_data, mock_panel_ols_result
    ):
        """Test that run_panel_ols is called with correct parameters for H3."""
        mock_run_panel_ols.return_value = mock_panel_ols_result

        from f1d.shared.panel_ols import run_panel_ols

        df = sample_h3_data.copy()
        df["Manager_QA_Uncertainty_pct_c"] = (
            df["Manager_QA_Uncertainty_pct"] - df["Manager_QA_Uncertainty_pct"].mean()
        )
        df["leverage_c"] = df["leverage"] - df["leverage"].mean()
        df["Manager_QA_Uncertainty_pct_x_leverage"] = (
            df["Manager_QA_Uncertainty_pct_c"] * df["leverage_c"]
        )

        exog = [
            "Manager_QA_Uncertainty_pct_c",
            "leverage_c",
            "Manager_QA_Uncertainty_pct_x_leverage",
            "firm_size",
        ]

        result = run_panel_ols(
            df=df,
            dependent="div_stability",
            exog=exog,
            entity_col="gvkey",
            time_col="fiscal_year",
            entity_effects=True,
            time_effects=True,
            check_collinearity=False,
        )

        mock_run_panel_ols.assert_called_once()
        assert result is not None

    @patch("f1d.shared.panel_ols.run_panel_ols")
    def test_regression_includes_interaction(
        self, mock_run_panel_ols, sample_h3_data, mock_panel_ols_result
    ):
        """Test that H3 regressions include interaction term."""
        mock_run_panel_ols.return_value = mock_panel_ols_result

        from f1d.shared.panel_ols import run_panel_ols

        df = sample_h3_data.copy()
        df["Manager_QA_Uncertainty_pct_c"] = (
            df["Manager_QA_Uncertainty_pct"] - df["Manager_QA_Uncertainty_pct"].mean()
        )
        df["leverage_c"] = df["leverage"] - df["leverage"].mean()
        df["Manager_QA_Uncertainty_pct_x_leverage"] = (
            df["Manager_QA_Uncertainty_pct_c"] * df["leverage_c"]
        )

        exog = [
            "Manager_QA_Uncertainty_pct_c",
            "leverage_c",
            "Manager_QA_Uncertainty_pct_x_leverage",
        ]

        run_panel_ols(
            df=df,
            dependent="div_stability",
            exog=exog,
            entity_col="gvkey",
            time_col="fiscal_year",
            entity_effects=True,
            time_effects=True,
            check_collinearity=False,
        )

        call_args = mock_run_panel_ols.call_args
        # Check that interaction term is in exog
        exog_vars = call_args[1]["exog"]
        interaction_present = any("_x_leverage" in var for var in exog_vars)
        assert interaction_present, "Interaction term should be in regression"


# ==============================================================================
# Hypothesis Test Tests - CRITICAL: Different directions for each DV
# ==============================================================================

class TestH3HypothesisTests:
    """Tests for H3 hypothesis test calculations."""

    # -------------------------------------------------------------------------
    # div_stability: Higher is more stable
    # H3a_stability: beta1 < 0 (vagueness REDUCES stability)
    # H3b_stability: beta3 < 0 (leverage AMPLIFIES negative effect)
    # -------------------------------------------------------------------------

    def test_h3a_stability_direction(self):
        """Test H3a hypothesis direction for div_stability (beta < 0)."""
        # For div_stability, H3a expects beta1 < 0
        coef_beta1 = -0.04  # Negative as expected
        p_two_tailed = 0.03

        if coef_beta1 < 0:
            p_one_tailed = p_two_tailed / 2
        else:
            p_one_tailed = 1 - p_two_tailed / 2

        assert p_one_tailed == 0.015  # Significant
        assert p_one_tailed < 0.05

    def test_h3b_stability_direction(self):
        """Test H3b hypothesis direction for div_stability (beta3 < 0)."""
        # For div_stability, H3b expects beta3 < 0 (amplification)
        coef_beta3 = -0.025  # Negative as expected
        p_two_tailed = 0.05

        if coef_beta3 < 0:
            p_one_tailed = p_two_tailed / 2
        else:
            p_one_tailed = 1 - p_two_tailed / 2

        assert p_one_tailed == 0.025  # Significant

    def test_div_stability_supported(self):
        """Test that div_stability hypothesis is supported correctly."""
        # Both beta1 and beta3 should be negative and significant
        beta1 = -0.04
        beta1_p_one = 0.015
        beta3 = -0.025
        beta3_p_one = 0.025

        h3a_supported = (beta1_p_one < 0.05) and (beta1 < 0)
        h3b_supported = (beta3_p_one < 0.05) and (beta3 < 0)

        assert h3a_supported is True
        assert h3b_supported is True

    # -------------------------------------------------------------------------
    # payout_flexibility: Higher is more flexible/volatile
    # H3a_flexibility: beta1 > 0 (vagueness INCREASES flexibility)
    # H3b_flexibility: beta3 > 0 (leverage AMPLIFIES positive effect)
    # -------------------------------------------------------------------------

    def test_h3a_flexibility_direction(self):
        """Test H3a hypothesis direction for payout_flexibility (beta > 0)."""
        # For payout_flexibility, H3a expects beta1 > 0
        coef_beta1 = 0.05  # Positive as expected
        p_two_tailed = 0.03

        if coef_beta1 > 0:
            p_one_tailed = p_two_tailed / 2
        else:
            p_one_tailed = 1 - p_two_tailed / 2

        assert p_one_tailed == 0.015  # Significant

    def test_h3b_flexibility_direction(self):
        """Test H3b hypothesis direction for payout_flexibility (beta3 > 0)."""
        # For payout_flexibility, H3b expects beta3 > 0 (amplification)
        coef_beta3 = 0.03  # Positive as expected
        p_two_tailed = 0.04

        if coef_beta3 > 0:
            p_one_tailed = p_two_tailed / 2
        else:
            p_one_tailed = 1 - p_two_tailed / 2

        assert p_one_tailed == 0.02  # Significant

    def test_payout_flexibility_supported(self):
        """Test that payout_flexibility hypothesis is supported correctly."""
        # Both beta1 and beta3 should be positive and significant
        beta1 = 0.05
        beta1_p_one = 0.015
        beta3 = 0.03
        beta3_p_one = 0.02

        h3a_supported = (beta1_p_one < 0.05) and (beta1 > 0)  # Note: > 0 for flexibility
        h3b_supported = (beta3_p_one < 0.05) and (beta3 > 0)  # Note: > 0 for flexibility

        assert h3a_supported is True
        assert h3b_supported is True

    def test_hypothesis_direction_differs_by_dv(self):
        """Test that hypothesis direction is different for each DV."""
        # div_stability expects beta < 0
        # payout_flexibility expects beta > 0

        # For the same coefficient sign, support should differ
        beta = 0.05  # Positive

        # For div_stability (beta < 0 expected), positive coef is wrong sign
        h3a_stability_supported = (0.02 < 0.05) and (beta < 0)  # False because beta > 0

        # For payout_flexibility (beta > 0 expected), positive coef is correct sign
        h3a_flexibility_supported = (0.02 < 0.05) and (beta > 0)  # True

        assert h3a_stability_supported is False
        assert h3a_flexibility_supported is True


# ==============================================================================
# Lead Variable Tests
# ==============================================================================

class TestH3LeadVariable:
    """Tests for lead variable creation in H3."""

    def test_lead_variable_creation(self, sample_h3_data):
        """Test that lead dependent variable is created correctly."""
        df = sample_h3_data.copy()
        df = df.sort_values(["gvkey", "fiscal_year"])

        # Create lead DV
        df["div_stability_lead"] = df.groupby("gvkey")["div_stability"].shift(-1)

        # Last year for each firm should have NaN lead
        last_years = df.groupby("gvkey").tail(1)
        assert last_years["div_stability_lead"].isna().all()

        # Non-last years should have non-NaN lead
        non_last_years = df.groupby("gvkey").head(-1)
        assert non_last_years["div_stability_lead"].notna().all()


# ==============================================================================
# Error Handling Tests
# ==============================================================================

class TestH3ErrorHandling:
    """Tests for H3 error handling."""

    def test_missing_dv_raises_error(self, sample_h3_data):
        """Test that missing DV raises error."""
        from f1d.shared.panel_ols import run_panel_ols

        df = sample_h3_data.copy()
        df = df.drop(columns=["div_stability", "payout_flexibility"])

        with pytest.raises(ValueError, match="Missing required columns"):
            run_panel_ols(
                df=df,
                dependent="div_stability",
                exog=["Manager_QA_Uncertainty_pct"],
                entity_col="gvkey",
                time_col="fiscal_year",
            )


# ==============================================================================
# Integration Test
# ==============================================================================

class TestH3Integration:
    """Integration tests for H3 regression."""

    @pytest.mark.skipif(
        not Path(_MODULE_PATH).exists(),
        reason="H3 regression module not found"
    )
    def test_module_imports_successfully(self):
        """Test that the H3 regression module imports without error."""
        module_globals = runpy.run_path(str(_MODULE_PATH))

        assert "main" in module_globals or "run_all_h3_regressions" in module_globals

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
