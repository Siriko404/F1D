"""
Edge case tests for data_validation module.
Tests verify error handling for invalid inputs (paths, schemas, values).
"""

import pytest
import pandas as pd
from pathlib import Path

# Try to import data_validation module, skip if not available
try:
    from 2_Scripts.shared.data_validation import (
        validate_dataframe_schema,
        DataValidationError,
        load_validated_parquet,
    )
    DATA_VALIDATION_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    DATA_VALIDATION_AVAILABLE = False
    pytest.skip("data_validation module not available", allow_module_level=True)


def test_validate_dataframe_schema_empty_dataframe():
    """Test schema validation handles empty DataFrame."""
    df = pd.DataFrame()
    schema = {
        "required_columns": [],
        "column_types": {},
    }

    # Should not raise for empty DataFrame with no requirements
    validate_dataframe_schema(df, "test_schema", Path("test.parquet"), strict=False)


def test_validate_dataframe_schema_all_null_columns():
    """Test schema validation handles all-null columns."""
    df = pd.DataFrame({
        "col1": [None, None, None],
        "col2": [None, None, None],
    })
    schema = {
        "required_columns": ["col1", "col2"],
        "column_types": {"col1": "float", "col2": "float"},
    }

    # Should not raise for all-null columns (null is valid float)
    validate_dataframe_schema(df, "test_schema", Path("test.parquet"), strict=False)


def test_validate_dataframe_schema_duplicate_columns():
    """Test schema validation handles duplicate column names."""
    df = pd.DataFrame([[1, 2, 3]], columns=["col", "col", "col2"])
    schema = {
        "required_columns": ["col", "col2"],
        "column_types": {},
    }

    # Pandas handles duplicate columns, validation should work
    validate_dataframe_schema(df, "test_schema", Path("test.parquet"), strict=False)


@pytest.mark.skipif(not DATA_VALIDATION_AVAILABLE, reason="data_validation module not available")
def test_validate_dataframe_schema_value_out_of_range():
    """Test schema validation detects values outside range."""
    df = pd.DataFrame({
        "event_type": [0, 5, 15],  # 15 is outside range [0, 10]
    })
    schema = {
        "required_columns": ["event_type"],
        "column_types": {"event_type": "int"},
        "value_ranges": {"event_type": {"min": 0, "max": 10}},
    }

    # Should raise for value outside range
    with pytest.raises(DataValidationError, match="event_type.*above max"):
        validate_dataframe_schema(df, "test_schema", Path("test.parquet"))


@pytest.mark.skipif(not DATA_VALIDATION_AVAILABLE, reason="data_validation module not available")
@pytest.mark.parametrize("invalid_value,expected_error", [
    ("not_a_number", "type mismatch"),
    (-1, "below min"),
    (11, "above max"),
])
def test_validate_dataframe_schema_various_invalid_values(invalid_value, expected_error):
    """Test schema validation detects various invalid values."""
    df = pd.DataFrame({"event_type": [invalid_value]})
    schema = {
        "required_columns": ["event_type"],
        "column_types": {"event_type": "int"},
        "value_ranges": {"event_type": {"min": 0, "max": 10}},
    }

    if isinstance(invalid_value, str):
        with pytest.raises(DataValidationError, match="type"):
            validate_dataframe_schema(df, "test_schema", Path("test.parquet"))
    elif invalid_value < 0:
        with pytest.raises(DataValidationError, match="below min"):
            validate_dataframe_schema(df, "test_schema", Path("test.parquet"))
    else:
        with pytest.raises(DataValidationError, match="above max"):
            validate_dataframe_schema(df, "test_schema", Path("test.parquet"))


@pytest.mark.skipif(not DATA_VALIDATION_AVAILABLE, reason="data_validation module not available")
def test_data_validation_error_messages_are_clear():
    """Test that validation error messages are clear and actionable."""
    df = pd.DataFrame({"col1": [1, 2]})  # Missing required column
    schema = {
        "required_columns": ["missing_col"],
    }

    try:
        validate_dataframe_schema(df, "test_schema", Path("test.parquet"))
        pytest.fail("Expected DataValidationError")
    except DataValidationError as e:
        error_msg = str(e)

        # Verify error message contains helpful information
        assert "Missing columns" in error_msg, "Error should mention missing columns"
        assert "missing_col" in error_msg, "Error should identify missing column"
        assert "test.parquet" in error_msg, "Error should mention file name"
