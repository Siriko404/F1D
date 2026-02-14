"""Structured logging module using structlog.

This module provides structured logging with JSON output support,
context binding, and multiple output formats.

Example:
    >>> from f1d.shared.logging import configure_logging, get_logger
    >>> configure_logging(log_level="INFO")
    >>> logger = get_logger(__name__)
    >>> logger.info("processing_started", rows=1000)
"""

from f1d.shared.logging.config import configure_logging, get_logger

__all__ = ["configure_logging", "get_logger"]
