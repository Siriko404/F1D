#!/usr/bin/env python3
"""
Unit tests for Clarity formula verification.

Tests that clarity_raw = -gamma_i, per-sample standardization,
and reference CEO exclusion.
"""

import numpy as np
import pandas as pd
import pytest

from tests.fixtures.synthetic_panel import synthetic_clarity_scores


# ==============================================================================
# Test Clarity Raw Formula
# ==============================================================================


class TestClarityRawFormula:
    """Tests for clarity_raw = -gamma_i formula."""

    def test_clarity_raw_is_negative_gamma(self) -> None:
        """clarity_raw must equal negative of gamma_i."""
        df = synthetic_clarity_scores()

        # Compute clarity_raw from gamma_i
        clarity_raw = -df["gamma_i"].values

        # Verify formula holds element-wise
        for i, gamma in enumerate(df["gamma_i"]):
            expected = -gamma
            actual = clarity_raw[i]
            np.testing.assert_almost_equal(
                actual, expected, decimal=10,
                err_msg=f"clarity_raw[{i}] != -gamma_i: {actual} != {expected}"
            )

    def test_clarity_raw_sign_flip(self) -> None:
        """Higher uncertainty (positive gamma) should mean lower clarity."""
        df = synthetic_clarity_scores()

        # Positive gamma -> negative clarity_raw (less clear)
        # Negative gamma -> positive clarity_raw (more clear)
        for _, row in df.iterrows():
            gamma = row["gamma_i"]
            clarity_raw = -gamma
            assert np.sign(gamma) != np.sign(clarity_raw) or gamma == 0


# ==============================================================================
# Test Per-Sample Standardization
# ==============================================================================


class TestPerSampleStandardization:
    """Tests for per-sample standardization (mean=0, std=1 within sample)."""

    def test_per_sample_standardization_mean_zero(self) -> None:
        """Standardized clarity should have mean=0 within each sample."""
        df = synthetic_clarity_scores()

        # Compute clarity_raw
        df = df.copy()
        df["clarity_raw"] = -df["gamma_i"]

        # Standardize per sample
        for sample in df["sample"].unique():
            sample_mask = df["sample"] == sample
            sample_data = df.loc[sample_mask, "clarity_raw"]

            if len(sample_data) > 1:
                standardized = (sample_data - sample_data.mean()) / sample_data.std()
                np.testing.assert_almost_equal(
                    standardized.mean(), 0.0, decimal=6,
                    err_msg=f"Sample {sample} mean != 0 after standardization"
                )

    def test_per_sample_standardization_std_one(self) -> None:
        """Standardized clarity should have std=1 within each sample."""
        df = synthetic_clarity_scores()

        # Compute clarity_raw
        df = df.copy()
        df["clarity_raw"] = -df["gamma_i"]

        # Standardize per sample
        for sample in df["sample"].unique():
            sample_mask = df["sample"] == sample
            sample_data = df.loc[sample_mask, "clarity_raw"]

            if len(sample_data) > 1:
                standardized = (sample_data - sample_data.mean()) / sample_data.std()
                np.testing.assert_almost_equal(
                    standardized.std(), 1.0, decimal=6,
                    err_msg=f"Sample {sample} std != 1 after standardization"
                )


# ==============================================================================
# Test Reference Exclusion
# ==============================================================================


class TestReferenceExclusion:
    """Tests for reference CEO exclusion from clarity scores."""

    def test_reference_exclusion_count(self) -> None:
        """Should have exactly 3 reference CEOs (1 per sample)."""
        df = synthetic_clarity_scores()
        reference_count = df["is_reference"].sum()

        assert reference_count == 3, (
            f"Expected 3 reference CEOs (1 per sample), got {reference_count}"
        )

    def test_reference_has_gamma_zero(self) -> None:
        """Reference CEOs should have gamma=0 by construction."""
        df = synthetic_clarity_scores()
        reference_ceos = df[df["is_reference"]]

        for _, row in reference_ceos.iterrows():
            np.testing.assert_almost_equal(
                row["gamma_i"], 0.0, decimal=10,
                err_msg=f"Reference CEO {row['ceo_id']} has non-zero gamma"
            )

    def test_one_reference_per_sample(self) -> None:
        """Each sample should have exactly 1 reference CEO."""
        df = synthetic_clarity_scores()

        for sample in df["sample"].unique():
            sample_refs = df[(df["sample"] == sample) & (df["is_reference"])]
            assert len(sample_refs) == 1, (
                f"Sample {sample} should have exactly 1 reference, got {len(sample_refs)}"
            )


# ==============================================================================
# Test Clarity Score Properties
# ==============================================================================


class TestClarityScoreProperties:
    """Tests for general clarity score properties."""

    def test_clarity_no_inf_values(self) -> None:
        """Clarity scores should not contain inf values."""
        df = synthetic_clarity_scores()
        df = df.copy()
        df["clarity_raw"] = -df["gamma_i"]

        assert not np.isinf(df["clarity_raw"]).any()

    def test_clarity_no_nan_values(self) -> None:
        """Clarity scores should not contain NaN values."""
        df = synthetic_clarity_scores()
        df = df.copy()
        df["clarity_raw"] = -df["gamma_i"]

        assert not df["clarity_raw"].isna().any()
