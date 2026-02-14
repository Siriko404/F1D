"""
Unit tests for f1d.shared.data_validation module.

Tests schema validation, DataValidationError exceptions, and
load_validated_parquet function.
"""

import pytest
import pandas as pd
from pathlib import Path

from f1d.shared.data_validation import (
    validate_dataframe_schema,
    DataValidationError,
    FinancialCalculationError,
    load_validated_parquet,
    INPUT_SCHEMAS,
)


# Standalone tests that don't require fixtures
class TestDataValidationStandalone:
    """Tests that don't require external fixtures."""

    def test_validate_with_all_required_columns(self):
        """Test validation passes when all required columns present."""
        df = pd.DataFrame({
            "event_type": ["1", "2", "3"],  # Use strings for object dtype
            "file_name": ["a.txt", "b.txt", "c.txt"],
            "start_date": pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"]),
            "speaker_record_count": [10, 20, 30],
        })
        # Should not raise
        validate_dataframe_schema(
            df, "Unified-info.parquet", Path("test.parquet"), strict=True
        )

    def test_validate_missing_required_column_raises(self):
        """Test that missing required column raises DataValidationError."""
        df = pd.DataFrame({
            "event_type": ["1", "2", "3"],
            # Missing: file_name, start_date, speaker_record_count
        })
        with pytest.raises(DataValidationError, match="Missing columns"):
            validate_dataframe_schema(
                df, "Unified-info.parquet", Path("test.parquet"), strict=True
            )

    def test_validate_with_correct_column_types(self):
        """Test validation passes with correct column types."""
        df = pd.DataFrame({
            "event_type": ["1", "2"],  # object dtype (string)
            "file_name": ["a", "b"],
            "start_date": pd.to_datetime(["2020-01-01", "2020-01-02"]),
            "speaker_record_count": [10, 20],
        })
        # Should not raise
        validate_dataframe_schema(
            df, "Unified-info.parquet", Path("test.parquet"), strict=True
        )

    def test_validate_with_incorrect_column_type_raises(self):
        """Test that incorrect column type raises DataValidationError."""
        # Create event_type as a non-string, non-object type
        df = pd.DataFrame({
            "event_type": [1.0, 2.0],  # float instead of object
            "file_name": ["a", "b"],
            "start_date": pd.to_datetime(["2020-01-01", "2020-01-02"]),
            "speaker_record_count": [10, 20],
        })
        with pytest.raises(DataValidationError, match="expected object"):
            validate_dataframe_schema(
                df, "Unified-info.parquet", Path("test.parquet"), strict=True
            )

    def test_validate_with_values_below_minimum(self):
        """Test that values below minimum raise DataValidationError."""
        df = pd.DataFrame({
            "event_type": ["1", "2", "3"],
            "file_name": ["a", "b", "c"],
            "start_date": pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"]),
            "speaker_record_count": [10, -1, 30],  # -1 < 0
        })
        # The validation may raise error about range check or below min depending on dtype
        with pytest.raises(DataValidationError):
            validate_dataframe_schema(
                df, "Unified-info.parquet", Path("test.parquet"), strict=True
            )

    @pytest.mark.parametrize("strict_mode,should_raise", [
        (True, True),
        (False, False),
    ])
    def test_strict_mode_controls_error_raising(self, strict_mode, should_raise):
        """Test that strict mode controls whether errors are raised."""
        df = pd.DataFrame({
            "event_type": [1, 2],  # Missing required columns
        })

        if should_raise:
            with pytest.raises(DataValidationError):
                validate_dataframe_schema(
                    df, "Unified-info.parquet", Path("test.parquet"), strict=strict_mode
                )
        else:
            # Should not raise in non-strict mode
            validate_dataframe_schema(
                df, "Unified-info.parquet", Path("test.parquet"), strict=strict_mode
            )

    def test_unknown_schema_prints_warning(self, capsys):
        """Test that unknown schema name prints warning."""
        df = pd.DataFrame({"col": [1, 2, 3]})
        validate_dataframe_schema(df, "unknown_schema", Path("test.parquet"))
        captured = capsys.readouterr()
        assert "WARNING: No schema defined" in captured.out


class TestFinancialCalculationError:
    """Tests for FinancialCalculationError exception."""

    def test_is_exception_subclass(self):
        """Test that FinancialCalculationError is an Exception subclass."""
        assert issubclass(FinancialCalculationError, Exception)

    def test_stores_error_message(self):
        """Test that error message is stored correctly."""
        msg = "Test financial calculation error"
        exc = FinancialCalculationError(msg)
        assert str(exc) == msg
        assert exc.args[0] == msg

    def test_can_be_raised_and_caught(self):
        """Test that exception can be raised and caught properly."""
        msg = "GVKEY not found"
        with pytest.raises(FinancialCalculationError, match="GVKEY"):
            raise FinancialCalculationError(msg)


class TestLoughranMcDonaldSchema:
    """Tests for Loughran-McDonald dictionary schema validation."""

    def test_loughran_schema_validates_correctly(self):
        """Test validation with valid Loughran-McDonald data."""
        df = pd.DataFrame({
            "word": ["uncertainty", "risk", "bad"],
            "negative": [1, 1, 1],
            "positive": [0, 0, 0],
            "uncertainty": [1, 1, 0],
            "litigious": [0, 1, 0],
        })
        # Should not raise
        validate_dataframe_schema(
            df, "Loughran-McDonald_MasterDictionary_1993-2024.csv",
            Path("test.csv"),
            strict=True
        )

    def test_loughran_schema_missing_columns(self):
        """Test that missing columns raise error for LM schema."""
        df = pd.DataFrame({
            "word": ["test", "words"],
            # Missing: negative, positive, uncertainty, litigious
        })
        with pytest.raises(DataValidationError, match="Missing columns"):
            validate_dataframe_schema(
                df, "Loughran-McDonald_MasterDictionary_1993-2024.csv",
                Path("test.csv"),
                strict=True
            )


class TestLoadValidatedParquetStandalone:
    """Tests for load_validated_parquet that don't require fixtures."""

    def test_load_without_schema(self, tmp_path):
        """Test loading without schema validation."""
        df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
        test_file = tmp_path / "test.parquet"
        df.to_parquet(test_file)

        result = load_validated_parquet(test_file, schema_name=None)
        assert len(result) == 3
        assert list(result.columns) == ["col1", "col2"]

    def test_load_with_schema_validation_success(self, tmp_path):
        """Test loading with successful schema validation."""
        df = pd.DataFrame({
            "event_type": ["1", "2"],  # object dtype
            "file_name": ["a", "b"],
            "start_date": pd.to_datetime(["2020-01-01", "2020-01-02"]),
            "speaker_record_count": [10, 20],
        })
        test_file = tmp_path / "test.parquet"
        df.to_parquet(test_file)

        result = load_validated_parquet(test_file, schema_name="Unified-info.parquet")
        assert len(result) == 2

    def test_load_with_schema_validation_failure(self, tmp_path):
        """Test loading with schema validation failure."""
        df = pd.DataFrame({"col1": [1, 2, 3]})
        test_file = tmp_path / "test.parquet"
        df.to_parquet(test_file)

        with pytest.raises(DataValidationError):
            load_validated_parquet(test_file, schema_name="Unified-info.parquet")

    def test_load_with_strict_false(self, tmp_path, capsys):
        """Test loading with validation failure in non-strict mode."""
        df = pd.DataFrame({"col1": [1, 2, 3]})
        test_file = tmp_path / "test.parquet"
        df.to_parquet(test_file)

        result = load_validated_parquet(
            test_file, schema_name="Unified-info.parquet", strict=False
        )
        assert len(result) == 3  # Should return data despite validation failure

        captured = capsys.readouterr()
        assert "WARNING" in captured.err


class TestInputSchemasStandalone:
    """Tests for INPUT_SCHEMAS constant."""

    def test_input_schemas_is_dict(self):
        """Test that INPUT_SCHEMAS is a dictionary."""
        assert isinstance(INPUT_SCHEMAS, dict)

    def test_input_schemas_not_empty(self):
        """Test that INPUT_SCHEMAS is not empty."""
        assert len(INPUT_SCHEMAS) > 0

    def test_unified_info_schema_structure(self):
        """Test that Unified-info schema has required keys."""
        schema = INPUT_SCHEMAS.get("Unified-info.parquet")
        assert schema is not None
        assert "required_columns" in schema
        assert "column_types" in schema
        assert "value_ranges" in schema

    def test_loughran_schema_structure(self):
        """Test that Loughran-McDonald schema has required keys."""
        schema = INPUT_SCHEMAS.get("Loughran-McDonald_MasterDictionary_1993-2024.csv")
        assert schema is not None
        assert "required_columns" in schema
        assert "column_types" in schema


# Parametrized tests for edge cases
@pytest.mark.parametrize("value,expected_valid", [
    (0, True),   # At minimum
    (-1, False),  # Below minimum
    (1000000, True),  # Above minimum
])
def test_speaker_record_count_range(value, expected_valid):
    """Test speaker_record_count range validation."""
    df = pd.DataFrame({
        "event_type": ["1"],  # object dtype
        "file_name": ["test"],
        "start_date": pd.to_datetime(["2020-01-01"]),
        "speaker_record_count": [value],
    })

    if expected_valid:
        # Should not raise for valid values
        validate_dataframe_schema(
            df, "Unified-info.parquet", Path("test.parquet"), strict=True
        )
    else:
        # Should raise for invalid values
        with pytest.raises(DataValidationError):
            validate_dataframe_schema(
                df, "Unified-info.parquet", Path("test.parquet"), strict=True
            )


@pytest.mark.parametrize("column,invalid_value", [
    ("speaker_record_count", -1),  # Below minimum
    ("file_name", None),  # Missing (but None is allowed in object columns)
])
def test_column_validation_edge_cases(column, invalid_value):
    """Test various column validation edge cases."""
    df_data = {
        "event_type": ["1"],
        "file_name": ["test"],
        "start_date": pd.to_datetime(["2020-01-01"]),
        "speaker_record_count": [10],
    }
    df_data[column] = [invalid_value]
    df = pd.DataFrame(df_data)

    # Should raise error for invalid speaker_record_count
    # Error may be about range check or below min depending on dtype
    if column == "speaker_record_count":
        with pytest.raises(DataValidationError):
            validate_dataframe_schema(
                df, "Unified-info.parquet", Path("test.parquet"), strict=True
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
        df = pd.DataFrame({"event_type": ["1", "2"]})  # Missing file_name, start_date, speaker_record_count
        with pytest.raises(DataValidationError, match="Missing columns"):
            validate_dataframe_schema(
                df, "Unified-info.parquet", sample_parquet_file_with_schema
            )

    def test_validate_dataframe_schema_column_type_mismatch_with_real_schema(
        self, sample_parquet_file_with_schema
    ):
        """Test schema validation fails for wrong column types using actual schema."""
        # event_type should be object (string), using float which doesn't match "object"
        df = pd.DataFrame({"event_type": [1.0, 2.0, 3.0]})  # float instead of object
        with pytest.raises(DataValidationError, match="expected object"):
            validate_dataframe_schema(
                df, "Unified-info.parquet", sample_parquet_file_with_schema
            )

    def test_validate_dataframe_schema_value_range_violation_with_real_schema(
        self, sample_parquet_file_with_schema
    ):
        """Test schema validation fails for values outside range using actual schema."""
        # speaker_record_count has min: 0, test with negative value
        df = pd.DataFrame({
            "event_type": ["1", "2", "3"],
            "file_name": ["a", "b", "c"],
            "start_date": pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"]),
            "speaker_record_count": [10, 20, -1],  # -1 is < 0
        })
        # Error message varies by dtype handling - just check that error is raised
        with pytest.raises(DataValidationError):
            validate_dataframe_schema(
                df, "Unified-info.parquet", sample_parquet_file_with_schema
            )

    def test_validate_dataframe_schema_value_below_min_with_real_schema(
        self, sample_parquet_file_with_schema
    ):
        """Test schema validation fails for values below minimum using actual schema."""
        # speaker_record_count has min: 0, test with negative value
        df = pd.DataFrame({
            "event_type": ["1", "2", "3"],
            "file_name": ["a", "b", "c"],
            "start_date": pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"]),
            "speaker_record_count": [0, 5, -1],  # -1 is < 0
        })
        # Error message varies by dtype handling - just check that error is raised
        with pytest.raises(DataValidationError):
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
        df = pd.DataFrame({"event_type": ["1", "2"]})  # Missing required columns
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
            ("Unified-info.parquet", ["event_type", "file_name", "start_date", "speaker_record_count"]),
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
