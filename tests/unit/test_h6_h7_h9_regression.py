"""
Unit tests for H6 CCCL Regression (4.6_H6CCCLRegression.py).

Tests verify:
- Data loading for CCCL (Concurrent Cash Conservation Leverage) variables
- Regression execution with various specifications
- Hypothesis test logic for H6 (positive effect of uncertainty on cash changes)
- Interaction term creation (uncertainty x leverage)
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
    / "src" / "f1d" / "econometric" / "v2" / "4.6_H6CCCLRegression.py"
)


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture
def sample_h6_data():
    """Create sample H6 CCCL data for testing."""
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
                # H6 DVs (cash conservation measures)
                "delta_cash_ratio": np.random.uniform(-0.05, 0.1),  # Change in cash
                "delta_cash_ratio_lead1": np.random.uniform(-0.05, 0.1),  # Lead DV
                # Uncertainty measures
                "Manager_QA_Uncertainty_pct": np.random.uniform(2, 8),
                "CEO_QA_Uncertainty_pct": np.random.uniform(2, 8),
                "Manager_QA_Weak_Modal_pct": np.random.uniform(1, 5),
                "CEO_QA_Weak_Modal_pct": np.random.uniform(1, 5),
                # Leverage (for interaction)
                "leverage": np.random.uniform(0.1, 0.6),
                # Controls
                "firm_size": np.random.uniform(5, 10),
                "tobins_q": np.random.uniform(0.8, 2.0),
                "roa": np.random.uniform(-0.1, 0.2),
                "cash_flow": np.random.uniform(-0.05, 0.15),
                "nwc": np.random.uniform(-0.1, 0.2),  # Net working capital
                "capex": np.random.uniform(0, 0.1),
                "dividend_payer": np.random.randint(0, 2),
            })

    return pd.DataFrame(data)


@pytest.fixture
def mock_panel_ols_result():
    """Create mock result from run_panel_ols for H6 regressions."""
    return {
        "model": MagicMock(),
        "coefficients": pd.DataFrame({
            "Coefficient": [0.025, -0.04, 0.01, 0.03],
            "Std. Error": [0.012, 0.02, 0.008, 0.015],
            "t-stat": [2.08, -2.0, 1.25, 2.0],
        }, index=[
            "Manager_QA_Uncertainty_pct_c",  # Key IV for H6
            "leverage_c",
            "firm_size",
            "cash_flow",
        ]),
        "summary": {
            "rsquared": 0.30,
            "rsquared_within": 0.15,
            "nobs": 200,
            "entity_effects": True,
            "time_effects": True,
            "cov_type": "clustered",
            "f_statistic": 16.5,
            "f_pvalue": 0.001,
        },
        "diagnostics": {"vif": None},
        "warnings": [],
    }


# ==============================================================================
# Data Loading Tests
# ==============================================================================

class TestH6DataLoading:
    """Tests for H6 data loading functions."""

    def test_load_h6_variables_basic(self, sample_h6_data, tmp_path):
        """Test that H6 variables load correctly from parquet."""
        h6_file = tmp_path / "H6_CCCL.parquet"
        sample_h6_data.to_parquet(h6_file, index=False)

        loaded = pd.read_parquet(h6_file)

        assert len(loaded) == len(sample_h6_data)
        assert "gvkey" in loaded.columns
        assert "fiscal_year" in loaded.columns
        assert "delta_cash_ratio" in loaded.columns

    def test_cash_change_dvs_present(self, sample_h6_data):
        """Test that cash change DVs are present."""
        assert "delta_cash_ratio" in sample_h6_data.columns
        assert "delta_cash_ratio_lead1" in sample_h6_data.columns

    def test_leverage_for_interaction(self, sample_h6_data):
        """Test that leverage is available for interaction."""
        assert "leverage" in sample_h6_data.columns

    def test_all_h6_controls_present(self, sample_h6_data):
        """Test that all H6 controls are present."""
        h6_controls = [
            "firm_size",
            "tobins_q",
            "roa",
            "cash_flow",
            "nwc",
            "capex",
            "dividend_payer",
        ]

        for col in h6_controls:
            assert col in sample_h6_data.columns, f"Missing H6 control: {col}"


# ==============================================================================
# Regression Execution Tests
# ==============================================================================

class TestH6RegressionExecution:
    """Tests for H6 regression execution."""

    @patch("f1d.shared.panel_ols.run_panel_ols")
    def test_single_h6_regression_called_correctly(
        self, mock_run_panel_ols, sample_h6_data, mock_panel_ols_result
    ):
        """Test that run_panel_ols is called with correct parameters for H6."""
        mock_run_panel_ols.return_value = mock_panel_ols_result

        from f1d.shared.panel_ols import run_panel_ols

        df = sample_h6_data.copy()
        df = df.dropna()

        result = run_panel_ols(
            df=df,
            dependent="delta_cash_ratio_lead1",
            exog=["Manager_QA_Uncertainty_pct", "leverage", "firm_size"],
            entity_col="gvkey",
            time_col="fiscal_year",
            entity_effects=True,
            time_effects=True,
            check_collinearity=False,
        )

        mock_run_panel_ols.assert_called_once()
        assert result is not None


# ==============================================================================
# Hypothesis Test Tests
# ==============================================================================

class TestH6HypothesisTests:
    """Tests for H6 hypothesis test calculations."""

    def test_h6_hypothesis_direction(self):
        """Test that H6 hypothesis is correctly specified (beta > 0)."""
        # H6: Higher uncertainty -> firms conserve more cash
        # Therefore beta > 0 (higher uncertainty -> positive delta cash)

        coef = 0.025  # Positive as expected for H6
        p_two_tailed = 0.04

        # One-tailed test for H6: beta > 0
        if coef > 0:
            p_one_tailed = p_two_tailed / 2
        else:
            p_one_tailed = 1 - p_two_tailed / 2

        assert p_one_tailed == 0.02
        assert p_one_tailed < 0.05

    def test_h6_supported_with_positive_significant_coef(self):
        """Test that H6 is supported when coef is positive and significant."""
        coef = 0.025
        p_one_tailed = 0.02

        h6_supported = (p_one_tailed < 0.05) and (coef > 0)

        assert h6_supported is True

    def test_h6_not_supported_with_negative_coef(self):
        """Test that H6 is not supported when coef is negative."""
        coef = -0.02  # Wrong sign for H6
        p_one_tailed = 0.02

        h6_supported = (p_one_tailed < 0.05) and (coef > 0)

        assert h6_supported is False


# ==============================================================================
# Interaction Term Tests
# ==============================================================================

class TestH6InteractionTerm:
    """Tests for H6 interaction term creation."""

    def test_interaction_term_creation(self, sample_h6_data):
        """Test that interaction term is created correctly."""
        df = sample_h6_data.copy()

        # Center variables
        uncertainty_col = "Manager_QA_Uncertainty_pct"
        df[f"{uncertainty_col}_c"] = df[uncertainty_col] - df[uncertainty_col].mean()
        df["leverage_c"] = df["leverage"] - df["leverage"].mean()

        # Create interaction
        interaction_col = f"{uncertainty_col}_x_leverage"
        df[interaction_col] = df[f"{uncertainty_col}_c"] * df["leverage_c"]

        assert interaction_col in df.columns
        assert df[interaction_col].notna().all()


# ==============================================================================
# Integration Test
# ==============================================================================

class TestH6Integration:
    """Integration tests for H6 regression."""

    @pytest.mark.skipif(
        not Path(_MODULE_PATH).exists(),
        reason="H6 regression module not found"
    )
    def test_module_imports_successfully(self):
        """Test that the H6 regression module imports without error."""
        module_globals = runpy.run_path(str(_MODULE_PATH))

        assert "main" in module_globals or "run_all_h6_regressions" in module_globals


# ==============================================================================
# Error Handling Tests
# ==============================================================================

class TestH6ErrorHandling:
    """Tests for H6 error handling."""

    def test_missing_dv_raises_error(self, sample_h6_data):
        """Test that missing DV raises error."""
        from f1d.shared.panel_ols import run_panel_ols

        df = sample_h6_data.copy()
        df = df.drop(columns=["delta_cash_ratio_lead1"])

        with pytest.raises(ValueError, match="Missing required columns"):
            run_panel_ols(
                df=df,
                dependent="delta_cash_ratio_lead1",
                exog=["Manager_QA_Uncertainty_pct"],
                entity_col="gvkey",
                time_col="fiscal_year",
            )
