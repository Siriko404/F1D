#!/usr/bin/env python3
"""
PyArrow chunked reading utilities for memory-efficient processing.

Provides functions to read large Parquet files in chunks, reducing
memory footprint while maintaining deterministic processing.

Ref: 10-RESEARCH.md Pattern 5 - PyArrow Dataset API
"""

from pathlib import Path
from typing import Iterator, Optional, List
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


def read_in_chunks(
    file_path: Path,
    columns: Optional[List[str]] = None,
    chunk_size: Optional[int] = None,
) -> Iterator[pd.DataFrame]:
    """
    Read Parquet file in chunks using PyArrow row groups.

    Args:
        file_path: Path to Parquet file
        columns: List of columns to read (None = all columns)
        chunk_size: Number of rows per chunk (None = use row groups)

    Yields:
        DataFrame chunks

    Example:
        >>> for chunk in read_in_chunks(Path("large_file.parquet")):
        ...     process_chunk(chunk)
    """
    parquet_file = pq.ParquetFile(file_path)

    # If chunk_size specified, convert to approximate row groups
    if chunk_size is not None:
        total_rows = parquet_file.metadata.num_rows
        row_group_size = parquet_file.metadata.row_group(0).num_rows
        num_row_groups = (total_rows + chunk_size - 1) // chunk_size
    else:
        num_row_groups = parquet_file.num_row_groups

    for i in range(num_row_groups):
        # Read specific row group(s) for this chunk
        if chunk_size is not None:
            # Calculate row group range for this chunk
            start_rg = (i * chunk_size) // row_group_size
            end_rg = ((i + 1) * chunk_size) // row_group_size
            if end_rg > num_row_groups:
                end_rg = num_row_groups

            # Read all row groups for this chunk
            tables = [
                parquet_file.read_row_group(rg, columns=columns)
                for rg in range(start_rg, end_rg)
            ]
            table = (
                pa.concat_tables(tables)
                if len(tables) > 1
                else (tables[0] if len(tables) == 1 else pa.table({}))
            )
        else:
            table = parquet_file.read_row_group(i, columns=columns)

        df = table.to_pandas()
        yield df


def read_selected_columns(file_path: Path, columns: List[str]) -> pd.DataFrame:
    """
    Read only selected columns to reduce memory usage.

    Args:
        file_path: Path to Parquet file
        columns: List of column names to read

    Returns:
        DataFrame with selected columns

    Example:
        >>> df = read_selected_columns(
        ...     Path("large_file.parquet"),
        ...     ["col1", "col2", "col3"]
        ... )
    """
    return pd.read_parquet(file_path, columns=columns)


def read_dataset_lazy(
    file_path: Path, columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Read Parquet file using PyArrow dataset API (lazy evaluation).

    Args:
        file_path: Path to Parquet file
        columns: List of columns to read (None = all columns)

    Returns:
        DataFrame (loads data on access)

    Example:
        >>> df = read_dataset_lazy(Path("large_file.parquet"))
    """
    import pyarrow.dataset as ds

    dataset = ds.dataset(file_path, format="parquet")
    table = dataset.to_table(columns=columns)
    return table.to_pandas()


def process_in_chunks(
    file_path: Path,
    process_func: callable,
    columns: Optional[List[str]] = None,
    chunk_size: Optional[int] = None,
    combine_func: Optional[callable] = None,
):
    """
    Process file in chunks, combining results with optional combine_func.

    Args:
        file_path: Path to Parquet file
        process_func: Function taking DataFrame chunk, returning partial result
        columns: List of columns to read
        chunk_size: Number of rows per chunk
        combine_func: Function to combine partial results (default: list concatenation)

    Returns:
        Combined result

    Example:
        >>> def count_rows(chunk):
        ...     return len(chunk)
        >>>
        >>> total = process_in_chunks(
        ...     Path("large_file.parquet"),
        ...     count_rows,
        ...     chunk_size=10000
        ... )
    """
    results = []
    for chunk in read_in_chunks(file_path, columns=columns, chunk_size=chunk_size):
        result = process_func(chunk)
        results.append(result)

    if combine_func:
        return combine_func(results)
    else:
        # Default: concatenate list results
        if results and isinstance(results[0], list):
            combined = []
            for r in results:
                combined.extend(r)
            return combined
        elif results and isinstance(results[0], pd.DataFrame):
            return pd.concat(results, ignore_index=True)
        else:
            return results
