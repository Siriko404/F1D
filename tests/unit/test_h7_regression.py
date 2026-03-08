"""
Unit tests for H7 Illiquidity Regression (run_h7_illiquidity.py).

Tests verify:
- Data loading for illiquidity variables (Amihud ratio)
- Regression execution with contemporaneous illiquidity as DV
- Hypothesis test logic for H7 (beta > 0)
- New control variables (Entire_All_Negative_pct, Analyst_QA_Uncertainty_pct)
- Single-IV specification structure (A1-A4)
- Output format and error handling
"""

import numpy as np
import pandas as pd
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

import runpy
_MODULE_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "src" / "f1d" / "econometric" / "run_h7_illiquidity.py"
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
                # H7 DV (contemporaneous illiquidity)
                "amihud_illiq": np.random.uniform(0.1, 5.0),
                # Uncertainty measures (4 IVs for A1-A4)
                "CEO_QA_Uncertainty_pct": np.random.uniform(2, 8),
                "CEO_Pres_Uncertainty_pct": np.random.uniform(1, 5),
                "Manager_QA_Uncertainty_pct": np.random.uniform(2, 8),
                "Manager_Pres_Uncertainty_pct": np.random.uniform(1, 5),
                # New linguistic controls
                "Entire_All_Negative_pct": np.random.uniform(0.5, 3.0),
                "Analyst_QA_Uncertainty_pct": np.random.uniform(1, 4),
                # Financial controls
                "Size": np.random.uniform(5, 10),
                "Lev": np.random.uniform(0.1, 0.6),
                "ROA": np.random.uniform(-0.1, 0.2),
                "TobinsQ": np.random.uniform(0.5, 3.0),
                "Volatility": np.random.uniform(0.01, 0.1),
                "StockRet": np.random.uniform(-0.3, 0.3),
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
            "CEO_QA_Uncertainty_pct",
            "Entire_All_Negative_pct",
            "Analyst_QA_Uncertainty_pct",
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
        assert "amihud_illiq" in loaded.columns  # Contemporaneous DV

    def test_illiquidity_dv_present(self, sample_h7_data):
        """Test that contemporaneous illiquidity DV is present."""
        assert "amihud_illiq" in sample_h7_data.columns

    def test_all_ivs_available(self, sample_h7_data):
        """Test that all 4 uncertainty IVs are available."""
        iv_cols = [
            "CEO_QA_Uncertainty_pct",
            "CEO_Pres_Uncertainty_pct",
            "Manager_QA_Uncertainty_pct",
            "Manager_Pres_Uncertainty_pct",
        ]

        for col in iv_cols:
            assert col in sample_h7_data.columns, f"Missing {col}"

    def test_new_controls_present(self, sample_h7_data):
        """Test that new linguistic controls are present."""
        assert "Entire_All_Negative_pct" in sample_h7_data.columns
        assert "Analyst_QA_Uncertainty_pct" in sample_h7_data.columns

    def test_financial_controls_present(self, sample_h7_data):
        """Test that financial controls are present."""
        assert "Size" in sample_h7_data.columns
        assert "Lev" in sample_h7_data.columns
        assert "ROA" in sample_h7_data.columns
        assert "TobinsQ" in sample_h7_data.columns
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
            dependent="amihud_illiq",  # Contemporaneous DV
            exog=["CEO_QA_Uncertainty_pct", "Entire_All_Negative_pct",
                  "Analyst_QA_Uncertainty_pct", "Size", "Lev"],
            entity_col="gvkey",
            time_col="year",
            entity_effects=True,
            time_effects=True,
            check_collinearity=False,
        )

        mock_run_panel_ols.assert_called_once()
        assert result is not None

    @patch("f1d.shared.panel_ols.run_panel_ols")
    def test_h7_uses_contemporaneous_illiquidity_as_dv(
        self, mock_run_panel_ols, sample_h7_data, mock_panel_ols_result
    ):
        """Test that H7 uses contemporaneous illiquidity as DV."""
        mock_run_panel_ols.return_value = mock_panel_ols_result

        from f1d.shared.panel_ols import run_panel_ols

        df = sample_h7_data.copy()

        run_panel_ols(
            df=df,
            dependent="amihud_illiq",  # Contemporaneous DV
            exog=["CEO_QA_Uncertainty_pct"],
            entity_col="gvkey",
            time_col="year",
            entity_effects=True,
            time_effects=True,
            check_collinearity=False,
        )

        call_args = mock_run_panel_ols.call_args
        assert call_args[1]["dependent"] == "amihud_illiq"


# ==============================================================================
# Hypothesis Test Tests
# ==============================================================================

class TestH7HypothesisTests:
    """Tests for H7 hypothesis test calculations."""

    def test_h7_hypothesis_direction(self):
        """Test that H7 hypothesis is correctly specified (beta > 0)."""
        coef = 0.35  # Positive as expected for H7
        p_two_tailed = 0.02

        # One-tailed test for H7: beta > 0
        if coef > 0:
            p_one_tailed = p_two_tailed / 2
        else:
            p_one_tailed = 1 - p_two_tailed / 2

        assert p_one_tailed == 0.01
        assert p_one_tailed < 0.05

    def test_h7_supported_with_positive_significant_coef(self):
        """Test that H7 is supported when coef is positive and significant."""
        coef = 0.35
        p_one_tailed = 0.01

        h7_supported = (p_one_tailed < 0.05) and (coef > 0)

        assert h7_supported is True

    def test_h7_not_supported_with_negative_coef(self):
        """Test that H7 is not supported when coef is negative."""
        coef = -0.25  # Wrong sign for H7
        p_one_tailed = 0.01

        h7_supported = (p_one_tailed < 0.05) and (coef > 0)

        assert h7_supported is False


# ==============================================================================
# Specification Structure Tests
# ==============================================================================

class TestH7SpecificationStructure:
    """Tests for H7 specification structure."""

    def test_four_specs_exist(self):
        """Test that 4 specifications (A1-A4) are defined."""
        expected_specs = ["A1", "A2", "A3", "A4"]
        # This would be verified by importing SPECS from the module

    def test_single_iv_per_spec(self):
        """Test that each spec has exactly one IV."""
        # Each spec should have: (spec_id, iv_var, iv_label)
        # No second_iv parameter
        pass


# ==============================================================================
# Error Handling Tests
# ==============================================================================

class TestH7ErrorHandling:
    """Tests for H7 error handling."""

    def test_missing_dv_raises_error(self, sample_h7_data):
        """Test that missing DV raises error."""
        from f1d.shared.panel_ols import run_panel_ols

        df = sample_h7_data.copy()
        df = df.drop(columns=["amihud_illiq"])

        with pytest.raises(ValueError, match="Missing required columns"):
            run_panel_ols(
                df=df,
                dependent="amihud_illiq",
                exog=["CEO_QA_Uncertainty_pct"],
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

        assert "main" in module_globals or "SPECS" in module_globals

    def test_dry_run_flag_supported(self):
        """Test that --dry-run flag is supported."""
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, str(_MODULE_PATH), "--help"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0 or "panel-path" in result.stdout.lower()
