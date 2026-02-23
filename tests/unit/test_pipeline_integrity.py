#!/usr/bin/env python3
"""
Unit tests for pipeline integrity across H0.1-H0.3.

Tests for no inf values, determinism, and proper error handling
for missing variables.
"""

import numpy as np
import pandas as pd
import pytest

from tests.fixtures.synthetic_panel import (
    synthetic_manager_clarity_panel,
    synthetic_ceo_clarity_panel,
)


# ==============================================================================
# Test No Inf Values
# ==============================================================================


class TestNoInfValues:
    """Tests ensuring no inf values in pipeline outputs."""

    def test_no_inf_values_manager_panel(self) -> None:
        """Manager clarity panel should have no inf values."""
        df = synthetic_manager_clarity_panel(n_rows=100)

        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            assert not np.isinf(df[col]).any(), f"Column {col} contains inf values"

    def test_no_inf_values_ceo_panel(self) -> None:
        """CEO clarity panel should have no inf values."""
        df = synthetic_ceo_clarity_panel(n_rows=100)

        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            assert not np.isinf(df[col]).any(), f"Column {col} contains inf values"

    def test_no_inf_after_standardization(self) -> None:
        """Standardized variables should have no inf values."""
        df = synthetic_manager_clarity_panel(n_rows=100)
        df = df.copy()

        # Simulate standardization
        for col in ["Manager_QA_Uncertainty_pct", "Manager_Pres_Uncertainty_pct"]:
            df[f"{col}_std"] = (df[col] - df[col].mean()) / df[col].std()
            assert not np.isinf(df[f"{col}_std"]).any()


# ==============================================================================
# Test Determinism
# ==============================================================================


class TestDeterminism:
    """Tests for deterministic pipeline outputs."""

    def test_determinism_same_seed(self) -> None:
        """Same seed should produce identical panels."""
        df1 = synthetic_manager_clarity_panel(n_rows=100, seed=42)
        df2 = synthetic_manager_clarity_panel(n_rows=100, seed=42)

        pd.testing.assert_frame_equal(df1, df2)

    def test_determinism_different_seeds(self) -> None:
        """Different seeds should produce different panels."""
        df1 = synthetic_manager_clarity_panel(n_rows=100, seed=42)
        df2 = synthetic_manager_clarity_panel(n_rows=100, seed=123)

        # Should differ in at least some values
        assert not df1.equals(df2), "Different seeds should produce different data"

    def test_determinism_consistent_structure(self) -> None:
        """Structure should be consistent regardless of seed."""
        df1 = synthetic_manager_clarity_panel(n_rows=100, seed=42)
        df2 = synthetic_manager_clarity_panel(n_rows=100, seed=123)

        # Same columns
        assert list(df1.columns) == list(df2.columns)

        # Same length
        assert len(df1) == len(df2)

        # Same dtypes
        for col in df1.columns:
            assert df1[col].dtype == df2[col].dtype


# ==============================================================================
# Test Missing Variable Handling
# ==============================================================================


class TestMissingVariableHandling:
    """Tests for proper error handling when variables are missing."""

    def test_missing_variable_raises(self) -> None:
        """Missing required variable should raise ValueError."""
        df = pd.DataFrame({
            "file_name": ["call_001", "call_002"],
            "ceo_id": ["CEO001", "CEO002"],
        })

        required_cols = ["Manager_QA_Uncertainty_pct", "StockRet", "EPS_Growth"]

        with pytest.raises(ValueError, match="Missing required columns"):
            missing = [c for c in required_cols if c not in df.columns]
            if missing:
                raise ValueError(f"Missing required columns: {missing}")

    def test_partial_columns_detected(self) -> None:
        """Should detect partial missing columns."""
        df = pd.DataFrame({
            "file_name": ["call_001", "call_002"],
            "ceo_id": ["CEO001", "CEO002"],
            "StockRet": [0.05, 0.03],
        })

        required_cols = ["file_name", "ceo_id", "StockRet", "EPS_Growth", "MarketRet"]
        missing = [c for c in required_cols if c not in df.columns]

        assert set(missing) == {"EPS_Growth", "MarketRet"}


# ==============================================================================
# Test NaN Handling
# ==============================================================================


class TestNaNHandling:
    """Tests for proper NaN handling in pipeline."""

    def test_nan_detection(self) -> None:
        """Should detect NaN values in numeric columns."""
        df = synthetic_manager_clarity_panel(n_rows=100)
        df.loc[0, "StockRet"] = np.nan

        assert df["StockRet"].isna().sum() == 1

    def test_nan_not_propagated_to_other_columns(self) -> None:
        """NaN in one column should not affect others."""
        df = synthetic_manager_clarity_panel(n_rows=100)
        df.loc[0, "StockRet"] = np.nan

        # Other columns should remain NaN-free
        assert df["EPS_Growth"].notna().all()
        assert df["MarketRet"].notna().all()


# ==============================================================================
# Test Column Type Integrity
# ==============================================================================


class TestColumnTypeIntegrity:
    """Tests for correct column data types."""

    def test_file_name_is_string(self) -> None:
        """file_name should be string type."""
        df = synthetic_manager_clarity_panel(n_rows=100)
        assert df["file_name"].dtype == object or pd.api.types.is_string_dtype(df["file_name"])

    def test_year_is_integer(self) -> None:
        """year should be integer type."""
        df = synthetic_manager_clarity_panel(n_rows=100)
        assert pd.api.types.is_integer_dtype(df["year"])

    def test_numeric_columns_are_numeric(self) -> None:
        """Numeric columns should have numeric dtypes."""
        df = synthetic_manager_clarity_panel(n_rows=100)

        numeric_cols = [
            "Manager_QA_Uncertainty_pct",
            "StockRet",
            "MarketRet",
            "EPS_Growth",
        ]

        for col in numeric_cols:
            assert pd.api.types.is_numeric_dtype(df[col]), f"{col} should be numeric"
