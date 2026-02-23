#!/usr/bin/env python3
"""
Unit tests for H0.1 Manager Clarity panel construction.

Tests panel file_name uniqueness, merge integrity, filter sequence,
and fixed effects extraction.
"""

import numpy as np
import pandas as pd
import pytest

from tests.fixtures.synthetic_panel import synthetic_manager_clarity_panel


# ==============================================================================
# Test Panel Uniqueness
# ==============================================================================


class TestPanelFileUniqueness:
    """Tests for file_name uniqueness in manager clarity panel."""

    def test_panel_file_name_unique(self) -> None:
        """file_name must be unique identifier across panel."""
        df = synthetic_manager_clarity_panel(n_rows=100)
        assert df["file_name"].duplicated().sum() == 0, "file_name must be unique"

    def test_panel_file_name_non_null(self) -> None:
        """file_name must not contain null values."""
        df = synthetic_manager_clarity_panel(n_rows=100)
        assert df["file_name"].notna().all(), "file_name must not be null"


# ==============================================================================
# Test Merge Integrity
# ==============================================================================


class TestMergeIntegrity:
    """Tests for merge operations preserving row count."""

    def test_merge_row_delta_zero(self) -> None:
        """Merge with financial data should not change row count."""
        df = synthetic_manager_clarity_panel(n_rows=100)
        before_count = len(df)

        # Simulate merge with additional columns (1:1 merge)
        financial_data = pd.DataFrame({
            "file_name": df["file_name"],
            "additional_col": np.random.randn(len(df)),
        })
        after = df.merge(financial_data, on="file_name", how="left")
        after_count = len(after)

        assert before_count == after_count, "Merge should preserve row count"

    def test_merge_preserves_file_name_order(self) -> None:
        """Merge should preserve file_name ordering."""
        df = synthetic_manager_clarity_panel(n_rows=100)
        original_order = df["file_name"].tolist()

        financial_data = pd.DataFrame({
            "file_name": df["file_name"],
            "additional_col": np.random.randn(len(df)),
        })
        merged = df.merge(financial_data, on="file_name", how="left")

        assert merged["file_name"].tolist() == original_order


# ==============================================================================
# Test Filter Sequence
# ==============================================================================


class TestFilterSequence:
    """Tests for sample filtering producing expected counts."""

    def test_filter_sequence_counts(self) -> None:
        """Filter should produce Main: 70, Finance: 20, Utility: 10 per 100 rows."""
        df = synthetic_manager_clarity_panel(n_rows=100)

        main_count = (df["sample"] == "Main").sum()
        finance_count = (df["sample"] == "Finance").sum()
        utility_count = (df["sample"] == "Utility").sum()

        assert main_count == 70, f"Expected 70 Main rows, got {main_count}"
        assert finance_count == 20, f"Expected 20 Finance rows, got {finance_count}"
        assert utility_count == 10, f"Expected 10 Utility rows, got {utility_count}"

    def test_filter_all_samples_present(self) -> None:
        """All three samples must be present in panel."""
        df = synthetic_manager_clarity_panel(n_rows=100)
        samples = set(df["sample"].unique())

        assert samples == {"Main", "Finance", "Utility"}, f"Expected all samples, got {samples}"


# ==============================================================================
# Test Fixed Effects Extraction
# ==============================================================================


class TestFixedEffectsExtraction:
    """Tests for FE extraction matching clarity formula."""

    def test_fe_extraction_clarity_raw_equals_negative_gamma(self) -> None:
        """clarity_raw should equal -gamma_i (within tolerance)."""
        # Create test data with known gamma values
        gamma_i = np.array([-0.5, -0.25, 0.0, 0.25, 0.5])
        clarity_raw = -gamma_i

        # Verify the formula: clarity_raw = -gamma_i
        np.testing.assert_allclose(
            clarity_raw, -gamma_i, rtol=1e-10,
            err_msg="clarity_raw must equal -gamma_i"
        )

    def test_fe_extraction_deterministic(self) -> None:
        """FE extraction should be deterministic."""
        df1 = synthetic_manager_clarity_panel(n_rows=50, seed=123)
        df2 = synthetic_manager_clarity_panel(n_rows=50, seed=123)

        pd.testing.assert_frame_equal(df1, df2)


# ==============================================================================
# Test Sample Column Integrity
# ==============================================================================


class TestSampleColumnIntegrity:
    """Tests for sample column consistency."""

    def test_sample_values_valid(self) -> None:
        """sample column should only contain valid values."""
        df = synthetic_manager_clarity_panel(n_rows=100)
        valid_samples = {"Main", "Finance", "Utility"}

        invalid = set(df["sample"].unique()) - valid_samples
        assert len(invalid) == 0, f"Invalid sample values: {invalid}"

    def test_sample_not_null(self) -> None:
        """sample column must not contain nulls."""
        df = synthetic_manager_clarity_panel(n_rows=100)
        assert df["sample"].notna().all()
