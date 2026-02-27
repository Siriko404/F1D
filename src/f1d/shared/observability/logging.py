#!/usr/bin/env python3
"""
================================================================================
OBSERVABILITY PACKAGE - LOGGING MODULE
================================================================================
ID: shared/observability.logging
Description: Provides dual-writer class for logging to both stdout and file.

This module extracts the DualWriter class from the original observability_utils.py.
DualWriter writes messages to both terminal and log file verbatim.

Deterministic: true
Main Functions:
    - DualWriter: Class for dual stdout/file logging

Dependencies:
    - Utility module for logging configuration
    - Uses: logging, sys

Author: Thesis Author
Date: 2026-02-11
================================================================================
"""

import logging
import sys
from pathlib import Path
from typing import Any, TextIO

# Configure logger for this module
logger = logging.getLogger(__name__)


class DualWriter:
    """
    Writes to both stdout and log file verbatim.

    This class is used to capture all script output (both print statements and
    log messages) to both the terminal and a log file for reproducibility.

    Attributes:
        terminal: Reference to sys.stdout
        log: File handle for log file
        original_stdout: Stored original stdout for restoration
    """

    original_stdout: Any  # TextIO | None

    def __init__(self, log_path: Path):
        """
        Initialize dual-writer.

        Args:
            log_path: Path to log file

        Raises:
            OSError: If the log file cannot be opened for writing
        """
        self.original_stdout = sys.stdout
        self.terminal = sys.stdout
        self.log = open(log_path, "w", encoding="utf-8")

    def write(self, message: str) -> None:
        """
        Write message to both terminal and log file.

        Args:
            message: Message to write

        Returns:
            None
        """
        self.terminal.write(message)
        self.log.write(message)

    def flush(self) -> None:
        """
        Flush both terminal and log file.

        Args:
            None

        Returns:
            None
        """
        self.terminal.flush()
        self.log.flush()

    def close(self) -> None:
        """
        Close log file handle.

        Args:
            None

        Returns:
            None
        """
        self.log.close()


__all__ = ["DualWriter"]
