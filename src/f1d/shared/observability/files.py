#!/usr/bin/env python3
"""
================================================================================
OBSERVABILITY PACKAGE - FILES MODULE
================================================================================
ID: shared.observability.files
Description: Provides file utility functions for observability.

This module extracts file-related functions from the original observability_utils.py.

Functions:
    - compute_file_checksum: Compute checksum for a file

Deterministic: true
Main Functions:
    - compute_file_checksum(): Compute SHA256 checksum of file

Dependencies:
    - Utility module for file operations
    - Uses: pandas, pathlib

Author: Thesis Author
Date: 2026-02-11
================================================================================
"""

import hashlib
import logging
from pathlib import Path

# Configure logger for this module
logger = logging.getLogger(__name__)


def compute_file_checksum(filepath: Path, algorithm: str = "sha256") -> str:
    """
    Compute checksum for a file.

    Args:
        filepath: Path to file to compute checksum for
        algorithm: Hash algorithm to use (default: sha256)

    Returns:
        Hexadecimal checksum string
    """
    h = hashlib.new(algorithm)
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


__all__ = ["compute_file_checksum"]
