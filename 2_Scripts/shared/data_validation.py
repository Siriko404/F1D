"""
Data Validation Module

Provides schema-based validation for input files to catch corrupted or
malicious data early in the pipeline.

Security:
- Validates input files against expected schemas before processing
- Checks required columns, column types, and value ranges
- Supports strict mode (raise error) vs non-strict (warn and continue)

Note: Validation is opt-in per script. Scripts can adopt this
pattern incrementally as needed.

Source: Pandas DataFrame validation patterns
Source: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.dtypes.html
"""

import sys
from pathlib import Path
from typing import Optional

import pandas as pd

# Schemas for key input files
INPUT_SCHEMAS = {
    "Unified-info.parquet": {
        "required_columns": [
            "event_type",
            "file_name",
            "start_date",
            "speaker_record_count",
        ],
        "column_types": {
            "event_type": "object",  # String representation of event type
            "start_date": "datetime64[ns]",
            "speaker_record_count": "int64",
        },
        "value_ranges": {
            "speaker_record_count": {"min": 0},
        },
    },
    "Loughran-McDonald_MasterDictionary_1993-2024.csv": {
        "required_columns": [
            "word",
            "negative",
            "positive",
            "uncertainty",
            "litigious",
        ],
        "column_types": {
            "word": "object",
            "negative": "int",
            "positive": "int",
            "uncertainty": "int",
            "litigious": "int",
        },
    },
}


class DataValidationError(Exception):
    """Raised when input data validation fails."""

    pass


# Exception usage guidance:
# FinancialCalculationError: Use for financial calculation failures (missing gvkey, no data found)
# DataValidationError: Use for input data validation failures (schema violations, invalid values)
class FinancialCalculationError(Exception):
    """Raised when financial metric calculation fails due to missing or invalid data."""

    pass


def validate_dataframe_schema(
    df: pd.DataFrame, schema_name: str, file_path: Path, strict: bool = True
) -> None:
    """
    Validate DataFrame against expected schema.

    Args:
        df: DataFrame to validate
        schema_name: Name of schema to use (key in INPUT_SCHEMAS)
        file_path: Path to source file (for error messages)
        strict: If True, raise on validation failure; if False, warn and continue

    Raises:
        DataValidationError: If validation fails and strict=True
    """
    if schema_name not in INPUT_SCHEMAS:
        print(f"WARNING: No schema defined for {schema_name}, skipping validation")
        return

    schema = INPUT_SCHEMAS[schema_name]
    errors = []

    # Check required columns
    required = schema.get("required_columns", [])
    missing = [col for col in required if col not in df.columns]
    if missing:
        errors.append(f"Missing columns: {missing}")

    # Check column types
    for col, expected_type in schema.get("column_types", {}).items():
        if col not in df.columns:
            continue
        actual_type = str(df[col].dtype)
        if not actual_type.startswith(expected_type):
            errors.append(
                f"Column '{col}': expected {expected_type}, got {actual_type}"
            )

    # Check value ranges
    for col, range_spec in schema.get("value_ranges", {}).items():
        if col not in df.columns:
            continue

        min_val = range_spec.get("min")
        max_val = range_spec.get("max")

        try:
            if min_val is not None and (df[col] < min_val).any():
                count = (df[col] < min_val).sum()
                errors.append(f"Column '{col}': {count} values below min ({min_val})")

            if max_val is not None and (df[col] > max_val).any():
                count = (df[col] > max_val).sum()
                errors.append(f"Column '{col}': {count} values above max ({max_val})")
        except TypeError:
            # Handle case where column type doesn't support comparison (e.g., strings vs int)
            actual_type = str(df[col].dtype)
            errors.append(
                f"Column '{col}': cannot check range (type {actual_type} incompatible with range check)"
            )

    # Report errors
    if errors:
        error_msg = (
            f"Validation failed for {file_path.name}:\n"
            f"  File: {file_path}\n"
            f"  Errors:\n    - " + "\n    - ".join(errors)
        )

        if strict:
            raise DataValidationError(error_msg)
        else:
            print(f"WARNING: {error_msg}", file=sys.stderr)
    else:
        print(f"Validation passed: {file_path.name}")


def load_validated_parquet(
    file_path: Path, schema_name: Optional[str] = None, strict: bool = True
) -> pd.DataFrame:
    """
    Load Parquet file with schema validation.

    Args:
        file_path: Path to Parquet file
        schema_name: Name of schema to validate against
        strict: If True, raise on validation failure

    Returns:
        pd.DataFrame: Validated DataFrame

    Raises:
        DataValidationError: If validation fails and strict=True
    """
    df = pd.read_parquet(file_path)

    if schema_name:
        validate_dataframe_schema(df, schema_name, file_path, strict=strict)

    return df
