#!/usr/bin/env python3
"""
================================================================================
OBSERVABILITY PACKAGE - MEMORY MODULE
================================================================================
ID: shared.observability.memory
Description: Provides memory tracking utilities for observability.

This module extracts memory-related functions from the original observability_utils.py.

Functions:
    - get_process_memory_mb: Get current process memory usage in MB

Deterministic: true
Main Functions:
    - get_process_memory_mb(): Get current process memory usage in MB

Dependencies:
    - Utility module for memory tracking
    - Uses: psutil, pandas

Author: Thesis Author
Date: 2026-02-11
================================================================================
"""

import logging
from typing import Dict

import psutil

# Configure logger for this module
logger = logging.getLogger(__name__)


def get_process_memory_mb() -> Dict[str, float]:
    """
    Get current process memory usage in MB.

    Returns:
        Dictionary with keys:
        - rss_mb: Resident Set Size (actual physical memory in use)
        - vms_mb: Virtual Memory Size (total memory allocated)
        - percent: Memory usage as percentage of system memory
    """
    process = psutil.Process()
    mem_info = process.memory_info()
    mem_percent = process.memory_percent()

    return {
        "rss_mb": mem_info.rss / (1024 * 1024),
        "vms_mb": mem_info.vms / (1024 * 1024),
        "percent": mem_percent,
    }


__all__ = ["get_process_memory_mb"]
