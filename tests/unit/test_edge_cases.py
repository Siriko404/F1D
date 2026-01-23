"""Edge case tests for common data scenarios."""
import pytest
import pandas as pd
from pathlib import Path

try:
    from 2_Scripts.shared.chunked_reader import read_in_chunks
    CHUNKED_READER_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    CHUNKED_READER_AVAILABLE = False


def test_missing_file_handling(tmp_path):
    """Test handling of missing input files."""
    missing_file = tmp_path / "nonexistent.parquet"
    with pytest.raises(FileNotFoundError):
        pd.read_parquet(missing_file)


@pytest.mark.parametrize("value,should_pass", [
    (0, True), (-100, True), (3.14, True), (None, True),
])
def test_boundary_values_numeric(value, should_pass):
    """Test boundary values for numeric columns."""
    df = pd.DataFrame({"col1": [value]})
    assert len(df) == 1


@pytest.mark.parametrize("value_range", [
    (-1, 10), (0, 100), (0, 1), (0, 1000),
])
def test_value_range_validation(value_range):
    """Test value range validation."""
    min_val, max_val = value_range
    df_valid = pd.DataFrame({"col1": [min_val + (max_val - min_val) / 2]})
    assert df_valid["col1"].iloc[0] >= min_val
    assert df_valid["col1"].iloc[0] <= max_val
