"""Structured logging configuration using structlog.

This module provides structured logging with JSON output support,
context binding, and multiple output formats.

Example:
    >>> from f1d.shared.logging import configure_logging, get_logger
    >>> configure_logging(log_level="INFO", json_output=False)
    >>> logger = get_logger(__name__)
    >>> logger.info("processing_started", rows=1000, stage="financial")

With LoggingSettings:
    >>> from f1d.shared.logging import configure_logging, LoggingSettings
    >>> settings = LoggingSettings(level="DEBUG")
    >>> configure_logging(settings=settings)
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any, Optional, Union, cast, TYPE_CHECKING

import structlog
from structlog.dev import ConsoleRenderer
from structlog.processors import JSONRenderer
from structlog.stdlib import BoundLogger

if TYPE_CHECKING:
    from f1d.shared.config.base import LoggingSettings


def configure_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    json_output: bool = False,
    settings: Optional["LoggingSettings"] = None,
) -> None:
    """Configure structlog with optional file output.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Optional path for log file output.
        json_output: If True, use JSON format for console; otherwise human-readable.
        settings: Optional LoggingSettings instance. If provided and log_level is default
                  ("INFO"), uses settings.level for the log level. Explicit log_level
                  parameter takes precedence over settings.level.
    """
    # If LoggingSettings provided, use its values (with parameter overrides still respected)
    if settings is not None:
        # Only use settings.level if log_level is still at default value
        if log_level == "INFO":
            log_level = settings.level

    # Shared processors for all loggers
    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if json_output:
        # JSON format for machine parsing
        renderer: Union[JSONRenderer, ConsoleRenderer] = structlog.processors.JSONRenderer()
    else:
        # Human-readable console format with colors
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=shared_processors
        + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard logging
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=shared_processors,
            processors=[renderer],
        )
    )

    root_logger = logging.getLogger()
    root_logger.handlers.clear()  # Remove existing handlers
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Optional file handler (always JSON for files)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            structlog.stdlib.ProcessorFormatter(
                foreign_pre_chain=shared_processors,
                processors=[structlog.processors.JSONRenderer()],
            )
        )
        root_logger.addHandler(file_handler)


def get_logger(name: Optional[str] = None) -> BoundLogger:
    """Get a structured logger instance.

    Args:
        name: Logger name, typically __name__.

    Returns:
        Bound logger instance.
    """
    return cast(BoundLogger, structlog.get_logger(name))


__all__ = ["configure_logging", "get_logger"]
