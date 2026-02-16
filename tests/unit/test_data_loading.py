#!/usr/bin/env python3
"""
Unit tests for data_loading.py (Phase 87-01)

Tests the safe_merge function and merge validation utilities.
"""

import logging
import pandas as pd
import pytest
import numpy as np

from f1d.shared.data_loading import (
    safe_merge,
    validate_merge_keys,
    get_merge_diagnostics,
)


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def left_df() -> pd.DataFrame:
    """Create a sample left DataFrame for merge testing."""
    return pd.DataFrame(
        {
            "file_name": ["call_001", "call_002", "call_003", "call_004"],
            "gvkey": ["001000", "001000", "001001", "001002"],
            "ceo_id": ["CEO001", "CEO001", "CEO002", "CEO003"],
        }
    )


@pytest.fixture
def right_df() -> pd.DataFrame:
    """Create a sample right DataFrame for merge testing."""
    return pd.DataFrame(
        {
            "file_name": ["call_001", "call_002", "call_003"],
            "uncertainty": [2.5, 3.0, 3.5],
        }
    )


# ==============================================================================
# Test safe_merge
# ==============================================================================


class TestSafeMerge:
    """Tests for safe_merge function."""

    def test_basic_left_merge(self, left_df: pd.DataFrame, right_df: pd.DataFrame) -> None:
        """Test basic left merge operation."""
        merged = safe_merge(
            left_df, right_df, on="file_name", how="left", merge_name="test_merge"
        )

        # All left rows should be preserved
        assert len(merged) == len(left_df)
        # Right column should be present
        assert "uncertainty" in merged.columns

    def test_inner_merge(self, left_df: pd.DataFrame, right_df: pd.DataFrame) -> None:
        """Test inner merge operation."""
        merged = safe_merge(
            left_df, right_df, on="file_name", how="inner", merge_name="test_inner"
        )

        # Only matching rows should be present
        assert len(merged) == 3  # call_001, call_002, call_003 match

    def test_merge_missing_key_raises_error(self, left_df: pd.DataFrame) -> None:
        """Test that missing merge key raises ValueError."""
        right = pd.DataFrame({"other_key": ["a", "b"], "value": [1, 2]})

        with pytest.raises(ValueError, match="missing from"):
            safe_merge(left_df, right, on="file_name", merge_name="test_error")

    def test_merge_with_validation(self, left_df: pd.DataFrame, right_df: pd.DataFrame) -> None:
        """Test merge with cardinality validation."""
        # This should work - many calls to one set of variables
        merged = safe_merge(
            left_df,
            right_df,
            on="file_name",
            how="left",
            validate="many_to_one",
            merge_name="test_validated",
        )

        assert len(merged) == 4

    def test_merge_logs_stats(self, left_df: pd.DataFrame, right_df: pd.DataFrame, caplog: pytest.LogCaptureFixture) -> None:
        """Test that merge logs statistics when log_stats=True."""
        with caplog.at_level(logging.INFO):
            merged = safe_merge(
                left_df,
                right_df,
                on="file_name",
                how="left",
                merge_name="test_logging",
                log_stats=True,
            )

        # Check that merge was logged
        assert any("test_logging" in record.message for record in caplog.records)

    def test_merge_with_left_on_right_on(self, left_df: pd.DataFrame) -> None:
        """Test merge with different key names in left and right."""
        right = pd.DataFrame(
            {
                "call_id": ["call_001", "call_002", "call_003"],
                "value": [1, 2, 3],
            }
        )

        merged = safe_merge(
            left_df,
            right,
            left_on="file_name",
            right_on="call_id",
            how="left",
            merge_name="test_asymmetric_keys",
        )

        assert len(merged) == 4
        assert "value" in merged.columns

    def test_merge_no_keys_error(self, left_df: pd.DataFrame, right_df: pd.DataFrame) -> None:
        """Test that merge without keys raises ValueError."""
        with pytest.raises(ValueError, match="Must specify"):
            safe_merge(left_df, right_df, merge_name="test_no_keys")


# ==============================================================================
# Test validate_merge_keys
# ==============================================================================


class TestValidateMergeKeys:
    """Tests for validate_merge_keys function."""

    def test_valid_keys(self) -> None:
        """Test validation with valid keys."""
        df = pd.DataFrame(
            {
                "file_name": ["a", "b", "c"],
                "gvkey": ["001", "002", "003"],
            }
        )

        is_valid, error = validate_merge_keys(df, ["file_name", "gvkey"], "test_df")

        assert is_valid is True
        assert error is None

    def test_missing_key(self) -> None:
        """Test validation with missing key."""
        df = pd.DataFrame(
            {
                "file_name": ["a", "b", "c"],
            }
        )

        is_valid, error = validate_merge_keys(df, ["file_name", "missing_key"], "test_df")

        assert is_valid is False
        assert "missing_key" in error

    def test_high_null_rate_warning(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test warning for high null rate in key columns."""
        df = pd.DataFrame(
            {
                "file_name": ["a", None, None, None],  # 75% null
                "gvkey": ["001", "002", "003", "004"],
            }
        )

        with caplog.at_level(logging.WARNING):
            validate_merge_keys(df, ["file_name"], "test_df")

        # Should log warning about null rate
        assert any("null" in record.message.lower() for record in caplog.records)


# ==============================================================================
# Test get_merge_diagnostics
# ==============================================================================


class TestGetMergeDiagnostics:
    """Tests for get_merge_diagnostics function."""

    def test_basic_diagnostics(self, left_df: pd.DataFrame, right_df: pd.DataFrame) -> None:
        """Test basic diagnostics calculation."""
        diagnostics = get_merge_diagnostics(left_df, right_df, on=["file_name"])

        assert diagnostics["left_rows"] == 4
        assert diagnostics["right_rows"] == 3
        assert diagnostics["key_overlap"] == 3
        assert diagnostics["left_only"] == 1
        assert diagnostics["right_only"] == 0

    def test_expected_match_rate(self, left_df: pd.DataFrame, right_df: pd.DataFrame) -> None:
        """Test expected match rate calculation."""
        diagnostics = get_merge_diagnostics(left_df, right_df, on=["file_name"], how="left")

        # 3 out of 4 left keys match = 75%
        assert "expected_match_rate" in diagnostics
        assert diagnostics["expected_match_rate"] == 75.0

    def test_empty_dataframe_diagnostics(self) -> None:
        """Test diagnostics with empty DataFrame."""
        left = pd.DataFrame(columns=["file_name", "value"])
        right = pd.DataFrame({"file_name": ["a"], "other": [1]})

        diagnostics = get_merge_diagnostics(left, right, on=["file_name"])

        assert diagnostics["left_rows"] == 0
        assert diagnostics["right_rows"] == 1

    def test_no_overlap_diagnostics(self) -> None:
        """Test diagnostics with no key overlap."""
        left = pd.DataFrame({"file_name": ["a", "b"]})
        right = pd.DataFrame({"file_name": ["x", "y"]})

        diagnostics = get_merge_diagnostics(left, right, on=["file_name"])

        assert diagnostics["key_overlap"] == 0
        assert diagnostics["left_only"] == 2
        assert diagnostics["right_only"] == 2


# ==============================================================================
# Integration Tests
# ==============================================================================


class TestDataLoadingIntegration:
    """Integration tests for data loading utilities."""

    def test_full_merge_workflow(self) -> None:
        """Test complete merge workflow with all utilities."""
        # Create test data
        manifest = pd.DataFrame(
            {
                "file_name": ["call_001", "call_002", "call_003", "call_004"],
                "gvkey": ["001", "001", "002", "003"],
            }
        )

        linguistic = pd.DataFrame(
            {
                "file_name": ["call_001", "call_002", "call_003"],
                "uncertainty": [2.5, 3.0, 3.5],
            }
        )

        # Step 1: Validate keys
        is_valid, _ = validate_merge_keys(manifest, ["file_name"], "manifest")
        assert is_valid

        is_valid, _ = validate_merge_keys(linguistic, ["file_name"], "linguistic")
        assert is_valid

        # Step 2: Get diagnostics
        diagnostics = get_merge_diagnostics(manifest, linguistic, on=["file_name"])
        assert diagnostics["key_overlap"] == 3

        # Step 3: Perform merge
        merged = safe_merge(
            manifest, linguistic, on="file_name", how="left", merge_name="test_workflow"
        )

        assert len(merged) == 4
        assert merged["uncertainty"].notna().sum() == 3

    def test_multi_key_merge(self) -> None:
        """Test merge on multiple keys."""
        left = pd.DataFrame(
            {
                "gvkey": ["001", "001", "002", "002"],
                "year": [2020, 2021, 2020, 2021],
                "value_left": [1, 2, 3, 4],
            }
        )

        right = pd.DataFrame(
            {
                "gvkey": ["001", "001", "002"],
                "year": [2020, 2021, 2020],
                "value_right": [10, 20, 30],
            }
        )

        merged = safe_merge(
            left, right, on=["gvkey", "year"], how="left", merge_name="test_multi_key"
        )

        assert len(merged) == 4
        # Last row (002, 2021) should have NaN for value_right
        assert pd.isna(merged.iloc[-1]["value_right"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
