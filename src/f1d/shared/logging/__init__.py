"""Structured logging module using structlog.

This module provides structured logging with JSON output support,
context binding, and multiple output formats.

Example:
    >>> from f1d.shared.logging import configure_logging, get_logger
    >>> configure_logging(log_level="INFO")
    >>> logger = get_logger(__name__)
    >>> logger.info("processing_started", rows=1000)

Context binding for correlated logging:
    >>> from f1d.shared.logging import bind_context, OperationContext
    >>> with OperationContext("financial_processing", script_name="script_32"):
    ...     logger.info("processing_started")  # Includes operation_id, script_name
"""

from f1d.shared.logging.config import configure_logging, get_logger
from f1d.shared.logging.context import (
    bind_context,
    clear_context,
    generate_operation_id,
    get_context,
    OperationContext,
    stage_context,
    unbind_context,
)

__all__ = [
    # Configuration
    "configure_logging",
    "get_logger",
    # Context binding
    "bind_context",
    "unbind_context",
    "get_context",
    "clear_context",
    "generate_operation_id",
    "OperationContext",
    "stage_context",
]
