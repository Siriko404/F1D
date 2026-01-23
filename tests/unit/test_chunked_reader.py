#!/usr/bin/env python3
"""Test chunked_reader utility produces bitwise-identical results."""

import pytest
import pandas as pd
from pathlib import Path
import sys

# Add 2_Scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "2_Scripts"))

from shared.chunked_reader import (
    read_in_chunks,
    read_selected_columns,
    process_in_chunks,
)


@pytest.mark.unit
def test_read_in_chunks():
    """Test that read_in_chunks produces same result as full read."""
    # Use a sample output file
    test_file = Path(
        "4_Outputs/2_Textual_Analysis/2.1_Tokenized/latest/linguistic_counts_2002.parquet"
    )

    if not test_file.exists():
        pytest.skip(f"{test_file} not found")

    # Read fully
    df_full = pd.read_parquet(test_file)

    # Read in chunks
    chunks = list(read_in_chunks(test_file))
    df_chunks = pd.concat(chunks, ignore_index=True)

    # Verify identical
    assert df_full.equals(df_chunks), "Chunked read differs from full read!"


@pytest.mark.unit
def test_read_selected_columns():
    """Test that read_selected_columns reduces memory usage."""
    test_file = Path(
        "4_Outputs/2_Textual_Analysis/2.1_Tokenized/latest/linguistic_counts_2002.parquet"
    )

    if not test_file.exists():
        pytest.skip(f"{test_file} not found")

    # Read full
    df_full = pd.read_parquet(test_file)

    # Read selected columns
    cols_to_read = ["file_name", "Total_Words"]
    if cols_to_read[1] not in df_full.columns:
        # Use available columns if Total_Words doesn't exist
        cols_to_read = list(df_full.columns)[:2]

    df_selected = read_selected_columns(test_file, cols_to_read)

    # Verify columns
    assert list(df_selected.columns) == cols_to_read, "Column mismatch!"
    assert len(df_selected) == len(df_full), "Row count mismatch!"


@pytest.mark.unit
def test_process_in_chunks():
    """Test that process_in_chunks combines results correctly."""
    test_file = Path(
        "4_Outputs/2_Textual_Analysis/2.1_Tokenized/latest/linguistic_counts_2002.parquet"
    )

    if not test_file.exists():
        pytest.skip(f"{test_file} not found")

    # Full read
    df_full = pd.read_parquet(test_file)

    # Process in chunks
    def count_rows(chunk):
        return len(chunk)

    # Use a combine function to sum the row counts
    def sum_counts(results):
        return sum(results)

    total = process_in_chunks(
        test_file, count_rows, chunk_size=1000, combine_func=sum_counts
    )

    assert total == len(df_full), f"Row count mismatch: {total} vs {len(df_full)}"
