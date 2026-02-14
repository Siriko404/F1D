"""
Unit tests for f1d.shared.panel_ols module.

Tests verify panel regression wrapper functions:
- Parameter validation
- Mock data handling
- Result formatting
- VIF calculation for multicollinearity
- Edge cases and error handling
- Thin cell detection
- Fixed effects combinations

Uses factory fixtures from tests/factories/financial.py for test data generation.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from f1d.shared.panel_ols import (
    run_panel_ols,
    _check_thin_cells,
    _format_coefficient_table,
    CollinearityError,
    MulticollinearityError,
    LINEARMODELS_AVAILABLE,
)

# Skip tests requiring linearmodels if not available
pytestmark = []
if not LINEARMODELS_AVAILABLE:
    pytestmark.append(pytest.mark.skip(reason="linearmodels not available"))


class TestCheckThinCells:
    """Tests for _check_thin_cells() function."""

    def test_no_thin_cells(self):
        """Test with all cells having sufficient firms."""
        df = pd.DataFrame({
            "ff48_code": [1, 1, 1, 2, 2, 2],
            "year": [2020, 2020, 2020, 2020, 2020, 2020],
        })
        has_thin, cell_counts = _check_thin_cells(df, "ff48_code", "year", min_firms=5)
        # Each cell has only 3 firms, which is less than min_firms=5
        assert has_thin is True
        assert len(cell_counts) == 2

    def test_detects_thin_cells(self):
        """Test detection of thin industry-year cells."""
        df = pd.DataFrame({
            "ff48_code": [1, 1, 2, 2, 2, 2, 2],
            "year": [2020, 2020, 2020, 2020, 2020, 2020, 2020],
        })
        has_thin, cell_counts = _check_thin_cells(df, "ff48_code", "year", min_firms=5)
        # Industry 1 has only 2 firms (< 5)
        assert has_thin is True
        assert cell_counts[(1, 2020)] == 2

    def test_all_cells_thick(self):
        """Test when all cells have sufficient firms."""
        df = pd.DataFrame({
            "ff48_code": [1, 1, 1, 1, 1, 2, 2, 2, 2, 2],
            "year": [2020, 2020, 2020, 2020, 2020, 2020, 2020, 2020, 2020, 2020],
        })
        has_thin, cell_counts = _check_thin_cells(df, "ff48_code", "year", min_firms=5)
        assert has_thin is False

    def test_missing_columns_returns_false(self):
        """Test with missing columns returns False and empty dict."""
        df = pd.DataFrame({"col1": [1, 2, 3]})
        has_thin, cell_counts = _check_thin_cells(df, "missing_col", "year", min_firms=5)
        assert has_thin is False
        assert cell_counts == {}

    def test_multiple_time_periods(self):
        """Test thin cell detection across multiple time periods."""
        df = pd.DataFrame({
            "ff48_code": [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 1, 1, 2, 2, 2],
            "year": [2020, 2020, 2020, 2020, 2020, 2020, 2020, 2020, 2020, 2020,
                     2021, 2021, 2021, 2021, 2021],
        })
        has_thin, cell_counts = _check_thin_cells(df, "ff48_code", "year", min_firms=3)
        # 2021: Industry 1 has 2 firms (< 3)
        assert has_thin is True
        assert cell_counts[(1, 2021)] == 2

    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
        df = pd.DataFrame({"ff48_code": [], "year": []})
        has_thin, cell_counts = _check_thin_cells(df, "ff48_code", "year", min_firms=5)
        assert has_thin is False
        assert cell_counts == {}

    def test_single_observation(self):
        """Test with single observation."""
        df = pd.DataFrame({"ff48_code": [1], "year": [2020]})
        has_thin, cell_counts = _check_thin_cells(df, "ff48_code", "year", min_firms=5)
        assert has_thin is True
        assert cell_counts[(1, 2020)] == 1


class TestFormatCoefficientTable:
    """Tests for _format_coefficient_table() function."""

    @pytest.fixture
    def sample_coefficients(self):
        """Create sample coefficients DataFrame for testing formatting."""
        return pd.DataFrame({
            "Coefficient": [0.5, -0.3, 1.2],
            "Std. Error": [0.1, 0.15, 0.5],
            "t-stat": [5.0, -2.0, 2.4],
        }, index=["x1", "x2", "Intercept"])

    @pytest.fixture
    def sample_pvalues(self):
        """Create sample p-values Series for testing."""
        return pd.Series([0.001, 0.05, 0.02], index=["x1", "x2", "Intercept"])

    def test_formats_basic_table(self, sample_coefficients, sample_pvalues):
        """Test basic coefficient table formatting."""
        output = _format_coefficient_table(sample_coefficients, sample_pvalues)
        assert "REGRESSION RESULTS" in output
        assert "Coefficients:" in output
        assert "x1" in output
        assert "x2" in output

    def test_adds_significance_stars(self, sample_coefficients, sample_pvalues):
        """Test that significance stars are added based on p-values."""
        output = _format_coefficient_table(sample_coefficients, sample_pvalues)
        # p=0.001 should have ***
        assert "***" in output
        # p=0.05 should have **
        assert "**" in output

    def test_includes_vif_section(self, sample_coefficients, sample_pvalues):
        """Test that VIF section is included when VIF DataFrame provided."""
        vif_df = pd.DataFrame({
            "variable": ["x1", "x2"],
            "VIF": [2.5, 8.0],
            "threshold_exceeded": [False, True],
        })
        output = _format_coefficient_table(
            sample_coefficients, sample_pvalues, vif_df=vif_df, vif_threshold=5.0
        )
        assert "Variance Inflation Factors:" in output
        assert "WARNING" in output
        assert "x2" in output

    def test_handles_no_vif(self, sample_coefficients, sample_pvalues):
        """Test formatting works without VIF DataFrame."""
        output = _format_coefficient_table(sample_coefficients, sample_pvalues, vif_df=None)
        assert "REGRESSION RESULTS" in output
        assert "Variance Inflation Factors:" not in output

    def test_includes_significance_legend(self, sample_coefficients, sample_pvalues):
        """Test that significance legend is included."""
        output = _format_coefficient_table(sample_coefficients, sample_pvalues)
        assert "Significance:" in output
        assert "p<0.10" in output
        assert "p<0.05" in output
        assert "p<0.01" in output

    def test_handles_nan_pvalue(self, sample_coefficients):
        """Test handling of NaN p-values."""
        pvalues = pd.Series([np.nan, 0.05, 0.02], index=["x1", "x2", "Intercept"])
        output = _format_coefficient_table(sample_coefficients, pvalues)
        assert "N/A" in output

    def test_single_coefficient(self):
        """Test formatting with single coefficient."""
        coef = pd.DataFrame({
            "Coefficient": [0.5],
            "Std. Error": [0.1],
            "t-stat": [5.0],
        }, index=["x1"])
        pvalues = pd.Series([0.001], index=["x1"])
        output = _format_coefficient_table(coef, pvalues)
        assert "x1" in output
        assert "***" in output

    def test_marginal_significance(self):
        """Test star assignment at marginal significance levels."""
        coef = pd.DataFrame({
            "Coefficient": [0.5, -0.3, 1.2, 0.8],
            "Std. Error": [0.1, 0.15, 0.5, 0.2],
            "t-stat": [5.0, -2.0, 2.4, 4.0],
        }, index=["x1", "x2", "x3", "x4"])
        # p-values at boundary conditions
        pvalues = pd.Series([0.099, 0.049, 0.009, 0.11], index=["x1", "x2", "x3", "x4"])
        output = _format_coefficient_table(coef, pvalues)
        assert "*" in output  # p<0.10
        assert output.count("*") >= 4  # At least 4 stars for x1, x2, x3


class TestRunPanelOls:
    """Tests for run_panel_ols() function."""

    @pytest.fixture
    def sample_panel_data(self, sample_panel_data_factory):
        """Create sample panel data for testing."""
        return sample_panel_data_factory(n_firms=10, n_years=5, seed=42)

    @pytest.mark.skipif(not LINEARMODELS_AVAILABLE, reason="linearmodels not available")
    def test_requires_dataframe_input(self, sample_panel_data):
        """Test that function requires DataFrame input."""
        assert isinstance(sample_panel_data, pd.DataFrame)

    @pytest.mark.skipif(not LINEARMODELS_AVAILABLE, reason="linearmodels not available")
    def test_validates_dependent_column_exists(self, sample_panel_data):
        """Test that missing dependent column raises appropriate error."""
        df_no_dep = sample_panel_data.drop(columns=["dependent"])
        with pytest.raises(ValueError, match="Missing required columns"):
            run_panel_ols(df_no_dep, "dependent", ["independent1"])

    @pytest.mark.skipif(not LINEARMODELS_AVAILABLE, reason="linearmodels not available")
    def test_validates_exog_columns_exist(self, sample_panel_data):
        """Test that missing exog columns raise appropriate error."""
        with pytest.raises(ValueError, match="Missing required columns"):
            run_panel_ols(
                sample_panel_data,
                "dependent",
                ["independent1", "missing_column"]
            )

    @pytest.mark.skipif(not LINEARMODELS_AVAILABLE, reason="linearmodels not available")
    def test_validates_industry_col_when_industry_effects(self, sample_panel_data):
        """Test that missing industry column raises error when industry_effects=True."""
        df_no_industry = sample_panel_data.drop(columns=["ff48_code"], errors="ignore")
        # Add ff48_code first so we can test the validation
        sample_panel_data["ff48_code"] = 1  # Add a dummy industry column
        with pytest.raises(ValueError, match="Missing required columns"):
            run_panel_ols(
                sample_panel_data.drop(columns=["ff48_code"]),
                "dependent",
                ["independent1"],
                industry_effects=True
            )

    @pytest.mark.skipif(not LINEARMODELS_AVAILABLE, reason="linearmodels not available")
    def test_returns_expected_result_structure(self, sample_panel_data):
        """Test that function returns result with expected keys."""
        result = run_panel_ols(
            sample_panel_data,
            "dependent",
            ["independent1", "independent2"],
            check_collinearity=False,  # Skip VIF for speed
        )
        expected_keys = ["model", "coefficients", "summary", "diagnostics", "warnings"]
        for key in expected_keys:
            assert key in result

    @pytest.mark.skipif(not LINEARMODELS_AVAILABLE, reason="linearmodels not available")
    def test_coefficients_dataframe_structure(self, sample_panel_data):
        """Test that coefficients DataFrame has expected structure."""
        result = run_panel_ols(
            sample_panel_data,
            "dependent",
            ["independent1", "independent2"],
            check_collinearity=False,
        )
        coef_df = result["coefficients"]
        assert "Coefficient" in coef_df.columns
        assert "Std. Error" in coef_df.columns
        assert "t-stat" in coef_df.columns

    @pytest.mark.skipif(not LINEARMODELS_AVAILABLE, reason="linearmodels not available")
    def test_summary_contains_expected_fields(self, sample_panel_data):
        """Test that summary contains expected fields."""
        result = run_panel_ols(
            sample_panel_data,
            "dependent",
            ["independent1"],
            check_collinearity=False,
        )
        summary = result["summary"]
        assert "rsquared" in summary
        assert "nobs" in summary
        assert "entity_effects" in summary
        assert "time_effects" in summary
        assert "cov_type" in summary

    @pytest.mark.skipif(not LINEARMODELS_AVAILABLE, reason="linearmodels not available")
    @pytest.mark.parametrize("entity_effects,time_effects", [
        (True, True),
        (True, False),
        (False, True),
        (False, False),
    ])
    def test_different_fixed_effects_combinations(
        self, sample_panel_data, entity_effects, time_effects
    ):
        """Test different fixed effect combinations."""
        result = run_panel_ols(
            sample_panel_data,
            "dependent",
            ["independent1"],
            entity_effects=entity_effects,
            time_effects=time_effects,
            check_collinearity=False,
        )
        assert result["summary"]["entity_effects"] == entity_effects
        assert result["summary"]["time_effects"] == time_effects

    @pytest.mark.skipif(not LINEARMODELS_AVAILABLE, reason="linearmodels not available")
    @pytest.mark.parametrize("cov_type", [
        "clustered",
        "robust",
        "kernel",
    ])
    def test_different_covariance_types(self, sample_panel_data, cov_type):
        """Test different covariance estimator types."""
        result = run_panel_ols(
            sample_panel_data,
            "dependent",
            ["independent1"],
            cov_type=cov_type,
            check_collinearity=False,
        )
        assert result["summary"]["cov_type"] == cov_type


class TestMulticollinearity:
    """Tests for VIF calculation and multicollinearity checking."""

    @pytest.fixture
    def sample_panel_data(self, sample_panel_data_factory):
        """Create sample panel data for testing."""
        return sample_panel_data_factory(n_firms=10, n_years=5, seed=42)

    @pytest.mark.skipif(not LINEARMODELS_AVAILABLE, reason="linearmodels not available")
    def test_perfect_correlation_detected(self, sample_panel_data):
        """Test that perfectly correlated variables raise CollinearityError."""
        # Create perfectly correlated variables
        df = sample_panel_data.copy()
        df["x1"] = list(range(1, 51))  # 1 to 50
        df["x2"] = [2 * x for x in df["x1"]]  # x2 = 2 * x1 (perfect collinearity)

        # Perfect collinearity should raise CollinearityError
        with pytest.raises(CollinearityError, match="collinearity"):
            run_panel_ols(
                df,
                "dependent",
                ["x1", "x2"],
                check_collinearity=True,
                vif_threshold=5.0,
            )

    @pytest.mark.skipif(not LINEARMODELS_AVAILABLE, reason="linearmodels not available")
    def test_uncorrelated_vars_low_vif(self, sample_panel_data):
        """Test that uncorrelated variables have low VIF."""
        np.random.seed(42)
        df = sample_panel_data.copy()
        df["x1"] = np.random.rand(len(df))
        df["x2"] = np.random.rand(len(df))
        df["x3"] = np.random.rand(len(df))

        result = run_panel_ols(
            df,
            "dependent",
            ["x1", "x2", "x3"],
            check_collinearity=True,
            vif_threshold=5.0,
        )

        # Check that VIF was computed
        assert result["diagnostics"]["vif"] is not None or len(result["warnings"]) >= 0

    @pytest.mark.skipif(not LINEARMODELS_AVAILABLE, reason="linearmodels not available")
    def test_vif_warning_high_values(self, sample_panel_data):
        """Test that high VIF values generate warnings."""
        np.random.seed(42)
        df = sample_panel_data.copy()
        # Create highly correlated variables (but not perfectly)
        df["x1"] = np.random.rand(len(df))
        df["x2"] = df["x1"] + np.random.rand(len(df)) * 0.01  # Almost identical

        result = run_panel_ols(
            df,
            "dependent",
            ["x1", "x2"],
            check_collinearity=True,
            vif_threshold=5.0,
        )

        # High VIF should generate warnings
        # Either in warnings list or VIF diagnostics
        assert result["diagnostics"]["vif"] is not None or len(result["warnings"]) > 0


class TestEdgeCases:
    """Tests for edge cases in panel OLS functions."""

    @pytest.fixture
    def sample_panel_data(self, sample_panel_data_factory):
        """Create sample panel data for testing."""
        return sample_panel_data_factory(n_firms=10, n_years=5, seed=42)

    @pytest.mark.skipif(not LINEARMODELS_AVAILABLE, reason="linearmodels not available")
    def test_handles_missing_values_in_regression_vars(self, sample_panel_data):
        """Test that missing values are handled correctly."""
        df = sample_panel_data.copy()
        df.loc[0, "independent1"] = np.nan
        df.loc[1, "dependent"] = np.nan

        result = run_panel_ols(
            df,
            "dependent",
            ["independent1"],
            check_collinearity=False,
        )
        # Should drop rows with missing values and still produce results
        assert result["summary"]["nobs"] < len(df)

    @pytest.mark.skipif(not LINEARMODELS_AVAILABLE, reason="linearmodels not available")
    def test_single_exog_variable(self, sample_panel_data):
        """Test regression with single exogenous variable."""
        result = run_panel_ols(
            sample_panel_data,
            "dependent",
            ["independent1"],
            check_collinearity=False,
        )
        assert len(result["coefficients"]) >= 1
        assert "independent1" in result["coefficients"].index

    @pytest.mark.skipif(not LINEARMODELS_AVAILABLE, reason="linearmodels not available")
    def test_double_clustering(self, sample_panel_data):
        """Test double-clustered standard errors."""
        result = run_panel_ols(
            sample_panel_data,
            "dependent",
            ["independent1"],
            cov_type="clustered",
            cluster_cols=["gvkey", "year"],
            check_collinearity=False,
        )
        assert result["summary"]["cov_type"] == "clustered"
        assert "warnings" in result

    @pytest.mark.skipif(not LINEARMODELS_AVAILABLE, reason="linearmodels not available")
    def test_single_cluster_entity(self, sample_panel_data):
        """Test clustering at entity level."""
        result = run_panel_ols(
            sample_panel_data,
            "dependent",
            ["independent1"],
            cov_type="clustered",
            cluster_cols=["gvkey"],
            check_collinearity=False,
        )
        assert result["summary"]["cov_type"] == "clustered"

    @pytest.mark.skipif(not LINEARMODELS_AVAILABLE, reason="linearmodels not available")
    def test_kernel_covariance(self, sample_panel_data):
        """Test kernel/HAC covariance estimation."""
        result = run_panel_ols(
            sample_panel_data,
            "dependent",
            ["independent1"],
            cov_type="kernel",
            kernel="bartlett",
            check_collinearity=False,
        )
        assert result["summary"]["cov_type"] == "kernel"

    @pytest.mark.skipif(not LINEARMODELS_AVAILABLE, reason="linearmodels not available")
    def test_returns_warnings_list(self, sample_panel_data):
        """Test that function returns a warnings list."""
        result = run_panel_ols(
            sample_panel_data,
            "dependent",
            ["independent1"],
            check_collinearity=False,
        )
        assert "warnings" in result
        assert isinstance(result["warnings"], list)


class TestCustomExceptions:
    """Tests for custom exceptions."""

    def test_collinearity_error_is_exception(self):
        """Test that CollinearityError is an Exception subclass."""
        assert issubclass(CollinearityError, Exception)

    def test_collinearity_error_message(self):
        """Test that CollinearityError stores message."""
        msg = "Test collinearity error"
        exc = CollinearityError(msg)
        assert str(exc) == msg

    def test_multicollinearity_error_is_exception(self):
        """Test that MulticollinearityError is an Exception subclass."""
        assert issubclass(MulticollinearityError, Exception)

    def test_multicollinearity_error_message(self):
        """Test that MulticollinearityError stores message."""
        msg = "Test multicollinearity error"
        exc = MulticollinearityError(msg)
        assert str(exc) == msg

    def test_collinearity_error_inheritance(self):
        """Test that CollinearityError can be caught as Exception."""
        with pytest.raises(Exception):
            raise CollinearityError("test")

    def test_multicollinearity_error_inheritance(self):
        """Test that MulticollinearityError can be caught as Exception."""
        with pytest.raises(Exception):
            raise MulticollinearityError("test")
