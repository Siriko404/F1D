"""Logging package for F1D pipeline.

This package provides structured logging with context propagation
and dual output (console + file) using structlog.

Modules:
    - config: Logging configuration and logger factory.
    - context: Operation context management for correlated logging.
    - handlers: Dual output handlers for console and file logging.

Example:
    >>> from f1d.shared.logging import configure_logging, get_logger
    >>> configure_logging(log_level="INFO")
    >>> logger = get_logger(__name__)
    >>> logger.info("processing_started", rows=1000)

Context binding for correlated logging:
    >>> from f1d.shared.logging import bind_context, OperationContext
    >>> with OperationContext("financial_processing", script_name="script_32"):
    ...     logger.info("processing_started")  # Includes operation_id, script_name

Dual output (console + file):
    >>> from f1d.shared.logging import configure_dual_output
    >>> configure_dual_output(log_file=Path("logs/pipeline.log"))
    >>> logger.info("processing_started", rows=1000)  # Console colored, file JSON
"""

from f1d.shared.config.base import LoggingSettings
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
from f1d.shared.logging.handlers import (
    configure_dual_output,
    configure_script_logging,
    DEFAULT_LOG_DIR,
    get_log_file_path,
    get_timestamped_log_path,
    LogFileRotator,
)

__all__ = [
    # Configuration
    "configure_logging",
    "get_logger",
    "LoggingSettings",
    # Context binding
    "bind_context",
    "unbind_context",
    "get_context",
    "clear_context",
    "generate_operation_id",
    "OperationContext",
    "stage_context",
    # Dual output handlers
    "configure_dual_output",
    "configure_script_logging",
    "get_log_file_path",
    "get_timestamped_log_path",
    "LogFileRotator",
    "DEFAULT_LOG_DIR",
]
