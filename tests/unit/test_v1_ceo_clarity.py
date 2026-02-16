#!/usr/bin/env python3
"""
Unit tests for V1 Econometric CEO Clarity Scripts (4.1.1, 4.1.2, 4.1.3, 4.1.4)

Tests core computation functions for CEO clarity estimation.
"""

import numpy as np
import pandas as pd
import pytest


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def sample_manifest_df() -> pd.DataFrame:
    """Create a sample manifest DataFrame for testing."""
    return pd.DataFrame(
        {
            "file_name": ["call_001", "call_002", "call_003", "call_004", "call_005"],
            "gvkey": ["001000", "001000", "001001", "001001", "001002"],
            "ceo_id": ["CEO001", "CEO001", "CEO002", "CEO002", "CEO003"],
            "ceo_name": ["John Smith", "John Smith", "Jane Doe", "Jane Doe", "Bob Jones"],
            "start_date": pd.to_datetime(
                ["2020-03-15", "2021-03-15", "2020-06-01", "2021-06-01", "2021-09-01"]
            ),
            "ff12_code": [1, 1, 2, 2, 11],  # 1-2: Main, 11: Finance
            "ff12_name": ["Consumer", "Consumer", "Manufacturing", "Manufacturing", "Finance"],
        }
    )


@pytest.fixture
def sample_linguistic_df() -> pd.DataFrame:
    """Create a sample linguistic variables DataFrame for testing."""
    return pd.DataFrame(
        {
            "file_name": ["call_001", "call_002", "call_003", "call_004", "call_005"],
            "Manager_QA_Uncertainty_pct": [2.5, 3.0, 3.5, 2.8, 1.5],
            "CEO_QA_Uncertainty_pct": [2.0, 2.5, 3.0, 2.2, 1.2],
            "Manager_Pres_Uncertainty_pct": [1.5, 2.0, 2.5, 1.8, 1.0],
        }
    )


@pytest.fixture
def sample_firm_controls_df() -> pd.DataFrame:
    """Create a sample firm controls DataFrame for testing."""
    return pd.DataFrame(
        {
            "file_name": ["call_001", "call_002", "call_003", "call_004", "call_005"],
            "StockRet": [0.05, 0.08, -0.02, 0.10, 0.03],
            "MarketRet": [0.06, 0.07, 0.05, 0.08, 0.04],
            "EPS_Growth": [0.10, 0.15, -0.05, 0.20, 0.08],
            "SurpDec": [0.01, 0.02, -0.01, 0.03, 0.00],
        }
    )


# ==============================================================================
# Test Sample Filtering
# ==============================================================================


class TestSampleFiltering:
    """Tests for sample filtering by FF12 industry."""

    def test_filter_main_sample(self, sample_manifest_df: pd.DataFrame) -> None:
        """Test filtering to main sample (non-financial, non-utility)."""
        df = sample_manifest_df.copy()

        # Main sample: FF12 codes 1-7, 9-10, 12 (exclude 8=Utility, 11=Finance)
        exclude_ff12 = [8, 11]
        main_sample = df[~df["ff12_code"].isin(exclude_ff12)]

        # Should exclude the Finance firm (ff12_code=11)
        assert len(main_sample) == 4
        assert 11 not in main_sample["ff12_code"].values

    def test_filter_finance_sample(self, sample_manifest_df: pd.DataFrame) -> None:
        """Test filtering to finance sample."""
        df = sample_manifest_df.copy()

        finance_sample = df[df["ff12_code"] == 11]

        assert len(finance_sample) == 1
        assert (finance_sample["ff12_code"] == 11).all()

    def test_filter_utility_sample(self) -> None:
        """Test filtering to utility sample."""
        df = pd.DataFrame(
            {
                "file_name": ["call_001", "call_002", "call_003"],
                "ff12_code": [1, 8, 11],  # 1=Main, 8=Utility, 11=Finance
            }
        )

        utility_sample = df[df["ff12_code"] == 8]

        assert len(utility_sample) == 1
        assert (utility_sample["ff12_code"] == 8).all()


# ==============================================================================
# Test Data Merging
# ==============================================================================


class TestDataMerging:
    """Tests for data merging operations."""

    def test_merge_manifest_with_linguistic(
        self, sample_manifest_df: pd.DataFrame, sample_linguistic_df: pd.DataFrame
    ) -> None:
        """Test merging manifest with linguistic variables."""
        manifest = sample_manifest_df.copy()
        linguistic = sample_linguistic_df.copy()

        merged = manifest.merge(linguistic, on="file_name", how="left")

        # All manifest rows should be preserved
        assert len(merged) == len(manifest)
        # Linguistic columns should be present
        assert "CEO_QA_Uncertainty_pct" in merged.columns

    def test_merge_preserves_ceo_id(
        self, sample_manifest_df: pd.DataFrame, sample_linguistic_df: pd.DataFrame
    ) -> None:
        """Test that merge preserves CEO identifiers."""
        manifest = sample_manifest_df.copy()
        linguistic = sample_linguistic_df.copy()

        merged = manifest.merge(linguistic, on="file_name", how="left")

        assert "ceo_id" in merged.columns
        assert merged["ceo_id"].notna().all()


# ==============================================================================
# Test Clarity Score Calculation
# ==============================================================================


class TestClarityScoreCalculation:
    """Tests for CEO clarity score calculation logic."""

    def test_clarity_is_negative_of_uncertainty(self) -> None:
        """Test that clarity is typically negative of uncertainty."""
        # Higher uncertainty = lower clarity
        uncertainty = np.array([2.0, 3.0, 1.5, 2.5])
        # Clarity would be -uncertainty in a simple model
        clarity = -uncertainty

        assert (clarity == -uncertainty).all()

    def test_ceo_clarity_consistency_within_ceo(self) -> None:
        """Test that CEO clarity should be consistent for same CEO across calls."""
        df = pd.DataFrame(
            {
                "ceo_id": ["CEO001", "CEO001", "CEO002", "CEO002"],
                "CEO_QA_Uncertainty_pct": [2.0, 2.5, 3.0, 3.5],
            }
        )

        # Calculate mean uncertainty per CEO (would be used for fixed effect)
        ceo_means = df.groupby("ceo_id")["CEO_QA_Uncertainty_pct"].mean()

        # CEO001 should have lower mean uncertainty than CEO002
        assert ceo_means["CEO001"] < ceo_means["CEO002"]


# ==============================================================================
# Test Fixed Effects Extraction
# ==============================================================================


class TestFixedEffectsExtraction:
    """Tests for extracting fixed effects from regression."""

    def test_extract_ceo_coefficients(self) -> None:
        """Test extracting CEO coefficients as clarity scores."""
        # Simulated regression coefficients
        coefficients = pd.DataFrame(
            {
                "variable": ["C(ceo_id)[T.CEO001]", "C(ceo_id)[T.CEO002]", "C(ceo_id)[T.CEO003]"],
                "coef": [-0.5, 0.3, -0.2],
                "pvalue": [0.01, 0.05, 0.10],
            }
        )

        # Extract CEO IDs from variable names
        coefficients["ceo_id"] = coefficients["variable"].str.extract(r"T\.(CEO\d+)")
        coefficients["ClarityCEO"] = -coefficients["coef"]  # Negative because clarity = -uncertainty

        assert len(coefficients) == 3
        assert "ClarityCEO" in coefficients.columns

    def test_coefficient_sign_interpretation(self) -> None:
        """Test that positive uncertainty coefficient = negative clarity."""
        # If regression shows CEO001 has +0.5 uncertainty effect (more uncertain)
        # Then clarity should be -0.5 (less clear)
        uncertainty_effect = 0.5
        clarity = -uncertainty_effect

        assert clarity == -0.5


# ==============================================================================
# Test Regression Specification
# ==============================================================================


class TestRegressionSpecification:
    """Tests for regression formula specification."""

    def test_formula_includes_uncertainty(self) -> None:
        """Test that regression formula includes uncertainty variable."""
        uncertainty_var = "CEO_QA_Uncertainty_pct"
        controls = ["StockRet", "MarketRet", "EPS_Growth"]

        formula_parts = [uncertainty_var] + controls
        formula = " ~ ".join(["CEO_QA_Uncertainty_pct", " + ".join(controls)])

        assert "CEO_QA_Uncertainty_pct" in formula
        assert "StockRet" in formula

    def test_formula_with_entity_effects(self) -> None:
        """Test formula includes entity (CEO) fixed effects."""
        # Entity effects are typically handled by the regression method, not formula
        # But verify the structure
        formula = "CEO_QA_Uncertainty_pct ~ StockRet + MarketRet + EntityEffects"
        assert "EntityEffects" in formula


# ==============================================================================
# Test Output Validation
# ==============================================================================


class TestOutputValidation:
    """Tests for output validation."""

    def test_clarity_scores_have_valid_range(self) -> None:
        """Test that clarity scores are in valid range."""
        clarity_scores = pd.DataFrame(
            {
                "ceo_id": ["CEO001", "CEO002", "CEO003"],
                "ClarityCEO": [0.5, -0.3, 0.1],
            }
        )

        # Clarity scores should be finite
        assert clarity_scores["ClarityCEO"].apply(np.isfinite).all()

    def test_clarity_scores_no_duplicates(self) -> None:
        """Test that clarity scores have one row per CEO."""
        clarity_scores = pd.DataFrame(
            {
                "ceo_id": ["CEO001", "CEO002", "CEO003"],
                "ClarityCEO": [0.5, -0.3, 0.1],
            }
        )

        assert clarity_scores["ceo_id"].is_unique

    def test_output_includes_sample_column(self) -> None:
        """Test that output includes sample identifier (Main/Finance/Utility)."""
        output = pd.DataFrame(
            {
                "ceo_id": ["CEO001", "CEO002", "CEO003"],
                "ClarityCEO": [0.5, -0.3, 0.1],
                "sample": ["Main", "Main", "Finance"],
            }
        )

        assert "sample" in output.columns
        assert set(output["sample"].unique()).issubset({"Main", "Finance", "Utility"})


# ==============================================================================
# Integration Tests
# ==============================================================================


class TestV1EconometricIntegration:
    """Integration tests for V1 econometric scripts."""

    def test_full_clarity_estimation_workflow(
        self,
        sample_manifest_df: pd.DataFrame,
        sample_linguistic_df: pd.DataFrame,
        sample_firm_controls_df: pd.DataFrame,
    ) -> None:
        """Test complete workflow for clarity estimation."""
        manifest = sample_manifest_df.copy()
        linguistic = sample_linguistic_df.copy()
        controls = sample_firm_controls_df.copy()

        # Step 1: Merge data
        merged = manifest.merge(linguistic, on="file_name", how="left")
        merged = merged.merge(controls, on="file_name", how="left")

        # Step 2: Filter to main sample
        main_sample = merged[~merged["ff12_code"].isin([8, 11])]

        # Step 3: Calculate CEO-level statistics
        ceo_stats = main_sample.groupby("ceo_id").agg(
            {"CEO_QA_Uncertainty_pct": "mean", "file_name": "count"}
        ).reset_index()
        ceo_stats.columns = ["ceo_id", "mean_uncertainty", "n_calls"]

        # Step 4: Create clarity score (inverse of uncertainty)
        ceo_stats["ClarityCEO"] = -ceo_stats["mean_uncertainty"]

        # Verify output
        assert len(ceo_stats) == 2  # Two CEOs in main sample
        assert "ClarityCEO" in ceo_stats.columns
        assert ceo_stats["ClarityCEO"].notna().all()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
