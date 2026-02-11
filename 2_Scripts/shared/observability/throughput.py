#!/usr/bin/env python3
"""
================================================================================
OBSERVABILITY PACKAGE - THROUGHPUT MODULE
================================================================================
ID: shared.observability.throughput
Description: Provides performance measurement functions for observability.

This module extracts throughput-related functions from the original observability_utils.py.

Functions:
    - calculate_throughput: Calculate throughput in rows per second

Deterministic: true
================================================================================
"""

import logging

# Configure logger for this module
logger = logging.getLogger(__name__)


def calculate_throughput(rows_processed: int, duration_seconds: float) -> float:
    """
    Calculate throughput in rows per second.

    Args:
        rows_processed: Number of rows processed
        duration_seconds: Duration in seconds

    Returns:
        Throughput in rows per second (rounded to 2 decimals)

    Raises:
        ValueError: If duration_seconds <= 0 (indicates timing error in pipeline)
    """
    if duration_seconds <= 0:
        logger.warning(
            f"Invalid duration_seconds={duration_seconds} <= 0, "
            f"rows_processed={rows_processed}. "
            f"This may indicate a timing error in the pipeline "
            f"(start_time/end_time not set correctly)."
        )
        raise ValueError(
            f"Cannot calculate throughput: duration_seconds={duration_seconds} <= 0. "
            f"rows_processed={rows_processed}. "
            f"Check script timing logic (start_time/end_time)."
        )
    return round(rows_processed / duration_seconds, 2)


__all__ = ["calculate_throughput"]
