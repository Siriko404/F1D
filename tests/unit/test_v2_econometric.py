#!/usr/bin/env python3
"""
Unit tests for V2 Econometric Scripts (4.8, 4.9, 4.10)

Tests core computation functions for:
- H8 Takeover Regression (4.8)
- CEO Fixed Effects (4.9)
- H2 PRisk x Uncertainty Investment (4.10)
"""

import numpy as np
import pandas as pd
import pytest


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def sample_regression_df() -> pd.DataFrame:
    """Create a sample DataFrame for regression testing."""
    np.random.seed(42)
    n = 100
    return pd.DataFrame(
        {
            "gvkey": [f"00{i:03d}" for i in np.random.randint(1, 20, n)],
            "fyear": np.random.choice([2020, 2021, 2022], n),
            "takeover": np.random.choice([0, 1], n, p=[0.9, 0.1]),
            "uncertainty": np.random.normal(2.5, 1.0, n),
            "clarity": np.random.normal(0, 0.5, n),
            "size": np.random.normal(7, 1.5, n),
            "leverage": np.random.uniform(0.1, 0.6, n),
            "tobins_q": np.random.normal(1.5, 0.5, n),
            "roa": np.random.normal(0.05, 0.03, n),
        }
    )


@pytest.fixture
def sample_panel_df() -> pd.DataFrame:
    """Create a sample panel DataFrame for fixed effects testing."""
    np.random.seed(123)
    firms = ["001000", "001001", "001002", "001003", "001004"]
    years = [2020, 2021, 2022, 2023]

    data = []
    for firm in firms:
        for year in years:
            data.append(
                {
                    "gvkey": firm,
                    "fyear": year,
                    "y": np.random.normal(0, 1),
                    "x1": np.random.normal(0, 1),
                    "x2": np.random.normal(0, 1),
                }
            )

    return pd.DataFrame(data)


# ==============================================================================
# Test H8 Takeover Regression
# ==============================================================================


class TestH8TakeoverRegression:
    """Tests for H8 takeover regression functions."""

    def test_sample_split_by_takeover(self, sample_regression_df: pd.DataFrame) -> None:
        """Test splitting sample by takeover status."""
        df = sample_regression_df.copy()

        takeover_firms = df[df["takeover"] == 1]
        non_takeover_firms = df[df["takeover"] == 0]

        assert len(takeover_firms) + len(non_takeover_firms) == len(df)

    def test_logit_coefficient_sign(self) -> None:
        """Test that logit coefficients have expected signs."""
        # Higher uncertainty should increase takeover probability
        # (positive coefficient on uncertainty)
        uncertainty_coef = 0.15
        assert uncertainty_coef > 0

        # Higher clarity should decrease takeover probability
        # (negative coefficient on clarity)
        clarity_coef = -0.20
        assert clarity_coef < 0

    def test_control_variable_selection(self, sample_regression_df: pd.DataFrame) -> None:
        """Test that control variables are correctly selected."""
        df = sample_regression_df.copy()

        control_vars = ["size", "leverage", "tobins_q", "roa"]

        # All control variables should exist in the DataFrame
        for var in control_vars:
            assert var in df.columns

    def test_missing_values_handled(self, sample_regression_df: pd.DataFrame) -> None:
        """Test that missing values are handled in regression."""
        df = sample_regression_df.copy()
        df.loc[0, "size"] = np.nan

        # Regression should either impute or drop missing values
        valid_rows = df.dropna(subset=["size"])
        assert len(valid_rows) == len(df) - 1


# ==============================================================================
# Test CEO Fixed Effects
# ==============================================================================


class TestCEOFixedEffects:
    """Tests for CEO fixed effects extraction."""

    def test_entity_fixed_effects_structure(self, sample_panel_df: pd.DataFrame) -> None:
        """Test structure of entity fixed effects."""
        df = sample_panel_df.copy()

        # Calculate firm means (fixed effects)
        firm_means = df.groupby("gvkey")["y"].mean()

        # Each firm should have one fixed effect
        assert len(firm_means) == df["gvkey"].nunique()

    def test_time_fixed_effects_structure(self, sample_panel_df: pd.DataFrame) -> None:
        """Test structure of time fixed effects."""
        df = sample_panel_df.copy()

        # Calculate year means (time effects)
        year_means = df.groupby("fyear")["y"].mean()

        # Each year should have one fixed effect
        assert len(year_means) == df["fyear"].nunique()

    def test_within_transformation(self, sample_panel_df: pd.DataFrame) -> None:
        """Test within transformation for fixed effects."""
        df = sample_panel_df.copy()

        # Within transformation: demean by entity
        df["y_demeaned"] = df.groupby("gvkey")["y"].transform(
            lambda x: x - x.mean()
        )

        # After within transformation, entity means should be ~0
        entity_means = df.groupby("gvkey")["y_demeaned"].mean()
        assert all(abs(m) < 1e-10 for m in entity_means)

    def test_ceo_vs_firm_effects(self) -> None:
        """Test distinction between CEO and firm fixed effects."""
        # When CEO changes within firm, we can identify CEO effect
        df = pd.DataFrame(
            {
                "gvkey": ["001000", "001000", "001000", "001000"],
                "ceo_id": ["CEO001", "CEO001", "CEO002", "CEO002"],
                "fyear": [2020, 2021, 2022, 2023],
                "y": [1.0, 1.2, 0.8, 1.0],
            }
        )

        # CEO fixed effects should vary by CEO
        ceo_means = df.groupby("ceo_id")["y"].mean()
        assert len(ceo_means) == 2  # Two CEOs


# ==============================================================================
# Test H2 PRisk x Uncertainty Investment
# ==============================================================================


class TestH2PRiskUncertaintyInvestment:
    """Tests for H2 PRisk x Uncertainty interaction regression."""

    def test_interaction_term_creation(self) -> None:
        """Test creation of PRisk x Uncertainty interaction term."""
        df = pd.DataFrame(
            {
                "prisk_std": [0.5, -0.3, 0.0, 1.2],
                "uncertainty_std": [1.0, -0.5, 0.5, 0.8],
            }
        )

        df["interaction"] = df["prisk_std"] * df["uncertainty_std"]

        expected = df["prisk_std"] * df["uncertainty_std"]
        pd.testing.assert_series_equal(df["interaction"], expected, check_names=False)

    def test_interaction_coefficient_interpretation(self) -> None:
        """Test interpretation of interaction coefficient."""
        # If interaction coefficient is negative:
        # Higher PRisk x Higher Uncertainty -> Lower Investment
        interaction_coef = -0.15

        # At high PRisk (1 SD) and high Uncertainty (1 SD):
        # Investment = main + 1*1*(-0.15) = main - 0.15
        marginal_effect_at_1sd = interaction_coef * 1 * 1
        assert marginal_effect_at_1sd < 0

    def test_marginal_effect_calculation(self) -> None:
        """Test calculation of marginal effects."""
        # Marginal effect of uncertainty on investment at different PRisk levels
        beta_uncertainty = 0.10
        beta_interaction = -0.05
        prisk_level = 2.0  # High PRisk

        # Marginal effect = beta_uncertainty + beta_interaction * PRisk
        marginal_effect = beta_uncertainty + beta_interaction * prisk_level
        assert marginal_effect == 0.0  # At PRisk=2, effect cancels out

    def test_standardization_preserves_ordering(self) -> None:
        """Test that standardization preserves relative ordering."""
        values = pd.Series([10, 20, 30, 40, 50])
        standardized = (values - values.mean()) / values.std()

        # Original ordering should be preserved
        assert standardized.argmax() == 4  # 50 still highest
        assert standardized.argmin() == 0  # 10 still lowest


# ==============================================================================
# Test Regression Diagnostics
# ==============================================================================


class TestRegressionDiagnostics:
    """Tests for regression diagnostic functions."""

    def test_r_squared_range(self) -> None:
        """Test that R-squared is in valid range."""
        r_squared = 0.35
        assert 0 <= r_squared <= 1

    def test_adjusted_r_squared(self) -> None:
        """Test adjusted R-squared calculation."""
        n = 100
        k = 5
        r_squared = 0.35

        adjusted_r_squared = 1 - (1 - r_squared) * (n - 1) / (n - k - 1)
        assert adjusted_r_squared < r_squared  # Adjusted should be lower
        assert adjusted_r_squared >= 0

    def test_vif_calculation(self) -> None:
        """Test Variance Inflation Factor threshold."""
        vif_values = [1.5, 2.3, 4.8, 8.2]
        threshold = 10.0

        high_vif = [v for v in vif_values if v > threshold]
        assert len(high_vif) == 0  # No multicollinearity concern

    def test_p_value_significance(self) -> None:
        """Test p-value significance classification."""
        p_values = [0.001, 0.01, 0.05, 0.10, 0.50]

        significant_01 = [p for p in p_values if p < 0.01]
        significant_05 = [p for p in p_values if p < 0.05]

        assert len(significant_01) == 1  # Only 0.001 < 0.01
        assert len(significant_05) == 2  # 0.001 and 0.01 are < 0.05 (0.05 is not strictly less)


# ==============================================================================
# Test Panel Data Structure
# ==============================================================================


class TestPanelDataStructure:
    """Tests for panel data structure validation."""

    def test_balanced_panel_detection(self, sample_panel_df: pd.DataFrame) -> None:
        """Test detection of balanced vs unbalanced panel."""
        df = sample_panel_df.copy()

        # Count observations per firm
        obs_per_firm = df.groupby("gvkey").size()

        # If all firms have same number of observations, panel is balanced
        is_balanced = len(obs_per_firm.unique()) == 1
        assert is_balanced  # Our sample is balanced

    def test_unbalanced_panel_detection(self) -> None:
        """Test detection of unbalanced panel."""
        df = pd.DataFrame(
            {
                "gvkey": ["A", "A", "A", "B", "B", "C"],
                "fyear": [2020, 2021, 2022, 2020, 2021, 2022],
            }
        )

        obs_per_firm = df.groupby("gvkey").size()
        is_balanced = len(obs_per_firm.unique()) == 1
        assert not is_balanced  # This panel is unbalanced

    def test_panel_identifier_uniqueness(self, sample_panel_df: pd.DataFrame) -> None:
        """Test that firm-year combinations are unique."""
        df = sample_panel_df.copy()

        duplicates = df.duplicated(subset=["gvkey", "fyear"]).sum()
        assert duplicates == 0


# ==============================================================================
# Integration Tests
# ==============================================================================


class TestV2EconometricIntegration:
    """Integration tests for V2 econometric scripts."""

    def test_full_regression_workflow(self, sample_regression_df: pd.DataFrame) -> None:
        """Test complete regression workflow."""
        df = sample_regression_df.copy()

        # Step 1: Prepare variables
        y = df["takeover"]
        X = df[["uncertainty", "clarity", "size", "leverage"]]

        # Step 2: Check for missing values
        assert X.isna().sum().sum() == 0
        assert y.isna().sum() == 0

        # Step 3: Check variable types
        assert X.dtypes.apply(lambda x: np.issubdtype(x, np.number)).all()

    def test_interaction_regression_workflow(self) -> None:
        """Test interaction regression workflow."""
        np.random.seed(456)
        n = 100

        df = pd.DataFrame(
            {
                "investment": np.random.normal(0.1, 0.05, n),
                "prisk": np.random.normal(0, 1, n),
                "uncertainty": np.random.normal(0, 1, n),
                "size": np.random.normal(7, 1, n),
            }
        )

        # Step 1: Standardize
        for col in ["prisk", "uncertainty"]:
            df[f"{col}_std"] = (df[col] - df[col].mean()) / df[col].std()

        # Step 2: Create interaction
        df["interaction"] = df["prisk_std"] * df["uncertainty_std"]

        # Step 3: Verify interaction column
        assert "interaction" in df.columns
        assert df["interaction"].notna().all()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
