"""
Unit tests for data_validation module.

Tests schema validation, DataValidationError exceptions, and
load_validated_parquet function.
"""

import pytest
import pandas as pd
from pathlib import Path
import sys

# Add 2_Scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "2_Scripts"))

from shared.data_validation import (
    validate_dataframe_schema,
    DataValidationError,
    load_validated_parquet,
    INPUT_SCHEMAS,
)


class TestValidateDataFrameSchema:
    """Tests for validate_dataframe_schema function."""

    def test_validate_dataframe_schema_success_with_real_data(
        self, sample_parquet_file_with_schema
    ):
        """Test schema validation passes for valid DataFrame matching Unified-info schema."""
        df = pd.read_parquet(sample_parquet_file_with_schema)
        # Should not raise for valid schema match
        validate_dataframe_schema(
            df, "Unified-info.parquet", sample_parquet_file_with_schema
        )

    def test_validate_dataframe_schema_missing_columns_with_real_schema(
        self, sample_parquet_file_with_schema
    ):
        """Test schema validation fails for missing required columns using actual schema."""
        df = pd.DataFrame({"event_type": [1, 2]})  # Missing file_name, date, speakers
        with pytest.raises(DataValidationError, match="Missing columns"):
            validate_dataframe_schema(
                df, "Unified-info.parquet", sample_parquet_file_with_schema
            )

    def test_validate_dataframe_schema_column_type_mismatch_with_real_schema(
        self, sample_parquet_file_with_schema
    ):
        """Test schema validation fails for wrong column types using actual schema."""
        df = pd.DataFrame({"event_type": ["1", "2", "3"]})  # String instead of int
        with pytest.raises(DataValidationError, match="expected int"):
            validate_dataframe_schema(
                df, "Unified-info.parquet", sample_parquet_file_with_schema
            )

    def test_validate_dataframe_schema_value_range_violation_with_real_schema(
        self, sample_parquet_file_with_schema
    ):
        """Test schema validation fails for values outside range using actual schema."""
        df = pd.DataFrame({"event_type": [1, 5, 15]})  # 15 is > 10
        with pytest.raises(DataValidationError, match="above max"):
            validate_dataframe_schema(
                df, "Unified-info.parquet", sample_parquet_file_with_schema
            )

    def test_validate_dataframe_schema_value_below_min_with_real_schema(
        self, sample_parquet_file_with_schema
    ):
        """Test schema validation fails for values below minimum using actual schema."""
        df = pd.DataFrame({"event_type": [0, 5, -1]})  # -1 is < 0
        with pytest.raises(DataValidationError, match="below min"):
            validate_dataframe_schema(
                df, "Unified-info.parquet", sample_parquet_file_with_schema
            )

    @pytest.mark.parametrize(
        "strict_mode,should_raise",
        [
            (True, True),
            (False, False),
        ],
    )
    def test_validate_dataframe_schema_strict_mode_with_real_schema(
        self, strict_mode, should_raise, sample_parquet_file_with_schema
    ):
        """Test strict mode controls whether errors are raised using actual schema."""
        df = pd.DataFrame({"event_type": [1, 2]})  # Missing required columns
        if should_raise:
            with pytest.raises(DataValidationError):
                validate_dataframe_schema(
                    df,
                    "Unified-info.parquet",
                    sample_parquet_file_with_schema,
                    strict=strict_mode,
                )
        else:
            # Should not raise in non-strict mode
            validate_dataframe_schema(
                df,
                "Unified-info.parquet",
                sample_parquet_file_with_schema,
                strict=strict_mode,
            )

    def test_validate_dataframe_schema_unknown_schema(self, sample_dataframe, capsys):
        """Test validation with unknown schema name prints warning."""
        # Unknown schema name
        validate_dataframe_schema(
            sample_dataframe, "unknown_schema", Path("test.parquet")
        )
        captured = capsys.readouterr()
        assert "WARNING: No schema defined" in captured.out

    def test_validate_dataframe_schema_unified_info_schema(
        self, sample_parquet_file_with_schema
    ):
        """Test validation with actual Unified-info.parquet schema."""
        df = pd.read_parquet(sample_parquet_file_with_schema)
        # Should not raise for valid schema match
        validate_dataframe_schema(
            df, "Unified-info.parquet", sample_parquet_file_with_schema
        )

    def test_validate_dataframe_schema_loughran_schema(self, tmp_path):
        """Test validation with Loughran-McDonald dictionary schema."""
        df = pd.DataFrame(
            {
                "word": ["uncertainty", "risk", "bad"],
                "negative": [1, 1, 1],
                "positive": [0, 0, 0],
                "uncertainty": [1, 1, 0],
                "litigious": [0, 1, 0],
            }
        )
        test_file = tmp_path / "test_lm_dict.csv"
        df.to_csv(test_file, index=False)
        # Should not raise for valid schema match
        validate_dataframe_schema(
            df, "Loughran-McDonald_MasterDictionary_1993-2024.csv", test_file
        )


class TestLoadValidatedParquet:
    """Tests for load_validated_parquet function."""

    def test_load_validated_parquet_with_schema(self, sample_parquet_file):
        """Load Parquet file with schema validation."""
        df = load_validated_parquet(sample_parquet_file, schema_name=None)
        assert len(df) == 3
        assert "file_name" in df.columns

    def test_load_validated_parquet_without_schema(self, sample_parquet_file):
        """Load Parquet file without schema validation."""
        df = load_validated_parquet(sample_parquet_file, schema_name=None)
        assert len(df) == 3

    def test_load_validated_parquet_validation_failure(self, tmp_path):
        """Load Parquet file with invalid schema raises error."""
        # Create invalid DataFrame (missing required columns)
        df = pd.DataFrame({"col1": [1, 2, 3]})
        invalid_file = tmp_path / "invalid.parquet"
        df.to_parquet(invalid_file)

        with pytest.raises(DataValidationError, match="Missing columns"):
            load_validated_parquet(invalid_file, schema_name="Unified-info.parquet")

    def test_load_validated_parquet_strict_mode_false(self, tmp_path, capsys):
        """Load Parquet file with validation errors in non-strict mode."""
        df = pd.DataFrame({"col1": [1, 2, 3]})
        invalid_file = tmp_path / "invalid.parquet"
        df.to_parquet(invalid_file)

        # Should not raise in non-strict mode
        result = load_validated_parquet(
            invalid_file, schema_name="Unified-info.parquet", strict=False
        )
        assert len(result) == 3

        # Check warning was printed
        captured = capsys.readouterr()
        assert "WARNING:" in captured.err


class TestInputSchemas:
    """Tests for INPUT_SCHEMAS constant."""

    def test_input_schemas_has_unified_info(self):
        """Test INPUT_SCHEMAS contains Unified-info.parquet schema."""
        assert "Unified-info.parquet" in INPUT_SCHEMAS

        schema = INPUT_SCHEMAS["Unified-info.parquet"]
        assert "required_columns" in schema
        assert "column_types" in schema
        assert "value_ranges" in schema

    def test_input_schemas_has_loughran_dictionary(self):
        """Test INPUT_SCHEMAS contains Loughran-McDonald schema."""
        assert "Loughran-McDonald_MasterDictionary_1993-2024.csv" in INPUT_SCHEMAS

        schema = INPUT_SCHEMAS["Loughran-McDonald_MasterDictionary_1993-2024.csv"]
        assert "required_columns" in schema
        assert "column_types" in schema

    @pytest.mark.parametrize(
        "schema_name,expected_columns",
        [
            ("Unified-info.parquet", ["event_type", "file_name", "date", "speakers"]),
            (
                "Loughran-McDonald_MasterDictionary_1993-2024.csv",
                ["word", "negative", "positive"],
            ),
        ],
    )
    def test_input_schemas_required_columns(self, schema_name, expected_columns):
        """Test schemas define expected required columns."""
        schema = INPUT_SCHEMAS[schema_name]
        for col in expected_columns:
            assert col in schema["required_columns"]


class TestDataValidationError:
    """Tests for DataValidationError exception."""

    def test_data_validation_error_is_exception(self):
        """Test DataValidationError is an Exception subclass."""
        assert issubclass(DataValidationError, Exception)

    def test_data_validation_error_message(self):
        """Test DataValidationError stores error message."""
        msg = "Test error message"
        exc = DataValidationError(msg)
        assert str(exc) == msg
        assert exc.args[0] == msg
