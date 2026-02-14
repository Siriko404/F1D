#!/usr/bin/env python3
"""
================================================================================
OBSERVABILITY PACKAGE - LOGGING MODULE
================================================================================
ID: shared/observability.logging
Description: Provides dual-writer class for logging to both stdout and file.

DEPRECATED: For new code, use f1d.shared.logging instead:
    from f1d.shared.logging import configure_script_logging, get_logger

This module is maintained for backward compatibility with existing scripts.
The DualWriter class is preserved for scripts that use it for stdout capture.

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

from f1d.shared.logging import get_logger

# Configure logger for this module
logger = get_logger(__name__)


class DualWriter:
    """
    Writes to both stdout and log file verbatim.

    This class is used to capture all script output (both print statements and
    log messages) to both the terminal and a log file for reproducibility.

    Attributes:
        terminal: Reference to sys.stdout
        log: File handle for log file
    """

    def __init__(self, log_path: Path):
        """
        Initialize dual-writer.

        Args:
            log_path: Path to log file
        """
        self.terminal = sys.stdout
        self.log = open(log_path, "w", encoding="utf-8")

    def write(self, message: str) -> None:
        """
        Write message to both terminal and log file.

        Args:
            message: Message to write
        """
        self.terminal.write(message)
        self.log.write(message)

    def flush(self) -> None:
        """Flush both terminal and log file."""
        self.terminal.flush()
        self.log.flush()

    def close(self) -> None:
        """Close log file handle."""
        self.log.close()


__all__ = ["DualWriter"]
