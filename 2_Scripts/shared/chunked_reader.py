#!/usr/bin/env python3
"""
================================================================================
SHARED MODULE: Chunked Reader for Memory-Efficient Processing
================================================================================
ID: shared/chunked_reader
Description: PyArrow chunked reading utilities for memory-efficient processing.

Purpose: Provides functions to read large Parquet files in chunks, reducing
         memory footprint while maintaining deterministic processing.

Inputs:
    - Large Parquet file paths
    - Chunk size specifications

Outputs:
    - Chunked data iterators
    - Memory tracking decorators

Main Functions:
    - read_in_chunks(): Read Parquet file in chunks using PyArrow
    - track_memory_usage(): Decorator for memory tracking during execution

Dependencies:
    - Utility module for memory-aware chunked processing
    - Uses: pandas, numpy, psutil, pyarrow

Deterministic: true

Author: Thesis Author
Date: 2026-02-11
================================================================================
"""

import time
from pathlib import Path
from typing import Iterator, List, Optional

import pandas as pd
import psutil
import pyarrow as pa
import pyarrow.parquet as pq
import yaml

from f1d.shared.logging import get_logger

# Configure logger
logger = get_logger(__name__)


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
    enable_throttling: bool = True,
):
    """
    Process file in chunks with optional memory-aware throttling.

    Args:
        file_path: Path to Parquet file
        process_func: Function taking DataFrame chunk, returning partial result
        columns: List of columns to read
        chunk_size: Number of rows per chunk (None = use row groups or config default)
        combine_func: Function to combine partial results (default: list concatenation)
        enable_throttling: Enable dynamic chunk size adjustment based on memory

    Returns:
        Combined result

    Example:
        >>> def count_rows(chunk):
        ...     return len(chunk)
        >>>
        >>> total = process_in_chunks(
        ...     Path("large_file.parquet"),
        ...     count_rows,
        ...     chunk_size=10000,
        ...     enable_throttling=True
        ... )
    """
    # Load config for throttling parameters
    try:
        config_path = Path(__file__).parent.parent.parent / "config" / "project.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)
            chunk_config = config.get("chunk_processing", {})
    except Exception:
        chunk_config = {}

    # Initialize throttler if enabled
    throttler = None
    if enable_throttling and chunk_config.get("enable_throttling", True):
        throttler = MemoryAwareThrottler(
            max_memory_percent=chunk_config.get("max_memory_percent", 80.0)
        )
        if chunk_config.get("log_memory_status", True):
            throttler.log_memory_status("chunked_processing_start")

    # Determine chunk size
    if chunk_size is None:
        chunk_size = chunk_config.get("base_chunk_size", 10000)

    # Adjust chunk size based on memory
    if throttler:
        chunk_size = throttler.get_recommended_chunk_size(chunk_size, file_path)

    results = []
    chunk_num = 0
    for chunk in read_in_chunks(file_path, columns=columns, chunk_size=chunk_size):
        # Log memory status periodically
        if (
            throttler
            and chunk_num % 10 == 0
            and chunk_config.get("log_memory_status", True)
        ):
            throttler.log_memory_status(f"chunk_{chunk_num}")

        result = process_func(chunk)
        results.append(result)
        chunk_num += 1

    # Log final memory status
    if throttler and chunk_config.get("log_memory_status", True):
        throttler.log_memory_status("chunked_processing_complete")

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


def track_memory_usage(operation_name: str):
    """
    Decorator to track memory usage and timing of an operation.

    Returns dict with result, memory stats, and timing.

    Args:
        operation_name: Name of operation being tracked

    Returns:
        Dict with keys: result, memory_mb (start/end/peak/delta), timing_seconds

    Ref: 15-RESEARCH.md Pattern 5 (Memory Monitoring Integration)
    Builds on Phase 12's get_process_memory_mb() pattern (see 12-01-SUMMARY.md)
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            process = psutil.Process()
            mem_start = process.memory_info().rss / (1024 * 1024)
            start_time = time.perf_counter()

            result = func(*args, **kwargs)

            mem_end = process.memory_info().rss / (1024 * 1024)
            end_time = time.perf_counter()

            return {
                "result": result,
                "memory_mb": {
                    "start": mem_start,
                    "end": mem_end,
                    "peak": max(mem_start, mem_end),
                    "delta": mem_end - mem_start,
                },
                "timing_seconds": end_time - start_time,
            }

        return wrapper

    return decorator


class MemoryAwareThrottler:
    """
    Adjusts processing parameters based on available memory.

    Monitors system memory usage and recommends chunk size adjustments
    to prevent OOM errors on memory-constrained systems.

    Ref: 15-RESEARCH.md Pattern 4 - Memory-Aware Throttling
    Builds on track_memory_usage from 15-04.
    """

    def __init__(self, max_memory_percent: float = 80.0):
        """
        Initialize memory throttler.

        Args:
            max_memory_percent: Memory usage percentage that triggers throttling
        """
        self.max_memory_percent = max_memory_percent
        self.process = psutil.Process()

    def get_available_memory_mb(self) -> float:
        """Get available system memory in MB."""
        mem = psutil.virtual_memory()
        return mem.available / (1024 * 1024)

    def get_memory_usage_mb(self) -> float:
        """Get current process memory usage in MB."""
        mem_info = self.process.memory_info()
        return mem_info.rss / (1024 * 1024)

    def get_memory_percent(self) -> float:
        """Get memory usage as percentage of system memory."""
        return self.process.memory_percent()

    def should_throttle(self) -> bool:
        """
        Check if processing should be throttled.

        Returns:
            True if memory usage exceeds max_memory_percent threshold
        """
        return self.get_memory_percent() > self.max_memory_percent

    def get_recommended_chunk_size(
        self, base_size: int = 10000, file_path: Path = None
    ) -> int:
        """
        Adjust chunk size based on memory pressure.

        Args:
            base_size: Base chunk size (rows per chunk)
            file_path: Optional path to Parquet file for row group size

        Returns:
            Recommended chunk size (rows per chunk)
        """
        if self.should_throttle():
            # Reduce chunk size to 50% when memory is constrained
            recommended = base_size // 2
        else:
            recommended = base_size

        # If file provided, adjust to multiple of row group size
        if file_path and file_path.exists():
            try:
                parquet_file = pq.ParquetFile(file_path)
                row_group_size = parquet_file.metadata.row_group(0).num_rows
                # Round to nearest multiple of row group size
                recommended = max(
                    row_group_size, (recommended // row_group_size) * row_group_size
                )
            except Exception:
                pass

        return recommended

    def log_memory_status(self, operation_name: str):
        """
        Log current memory status for observability.

        Args:
            operation_name: Name of operation being logged
        """
        logger.info(
            f"Memory status for {operation_name}: "
            f"{self.get_memory_usage_mb():.2f} MB "
            f"({self.get_memory_percent():.1f}%), "
            f"available: {self.get_available_memory_mb():.2f} MB"
        )
