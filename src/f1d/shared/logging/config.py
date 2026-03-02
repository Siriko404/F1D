"""config - Structured logging configuration using structlog.

Purpose:
    Provides structured logging configuration with JSON output support,
    context binding, and multiple output formats.

Key Functions:
    - configure_logging: Configure structlog with optional file output.
    - get_logger: Get a structured logger instance.

Usage:
    from f1d.shared.logging.config import configure_logging, get_logger

    configure_logging(log_level="INFO", json_output=False)
    logger = get_logger(__name__)
    logger.info("processing_started", rows=1000, stage="financial")

With LoggingSettings:
    from f1d.shared.config.base import LoggingSettings
    settings = LoggingSettings(level="DEBUG")
    configure_logging(settings=settings)
"""

from __future__ import annotations

import atexit
import logging
import sys
from pathlib import Path
from typing import Any, IO, Optional, Union, cast, TYPE_CHECKING

import structlog
from structlog.dev import ConsoleRenderer
from structlog.processors import JSONRenderer
from structlog.stdlib import BoundLogger

if TYPE_CHECKING:
    from f1d.shared.config.base import LoggingSettings


# ==============================================================================
# TeeOutput: Capture print() to log file while still showing on console
# ==============================================================================

_original_stdout: IO[str] = sys.stdout
_original_stderr: IO[str] = sys.stderr
_tee_active: bool = False


class TeeOutput:
    """Tee stdout/stderr to both console and log file.

    This class allows print() statements to be captured to a log file
    while still displaying on the console. Used by setup_run_logging()
    to ensure all output is captured.

    Attributes:
        log_file: The file handle to write logs to.
        original: The original stream (stdout or stderr).
        prefix: Optional prefix for log lines (e.g., "[STDERR]").
    """

    def __init__(
        self,
        log_file: IO[str],
        original_stream: IO[str],
        prefix: str = "",
    ):
        self.log_file = log_file
        self.original = original_stream
        self.prefix = prefix

    def write(self, message: str) -> int:
        """Write message to both original stream and log file."""
        # Write to original stream (console)
        written = self.original.write(message)

        # Write to log file with optional prefix for stderr
        if message.strip():  # Only add prefix for non-empty lines
            if self.prefix:
                self.log_file.write(f"[{self.prefix}] ")
            self.log_file.write(message)
            # Add newline if message doesn't end with one
            if not message.endswith("\n"):
                self.log_file.write("\n")
        else:
            # Preserve empty lines
            self.log_file.write(message)

        return written

    def flush(self) -> None:
        """Flush both streams."""
        self.original.flush()
        self.log_file.flush()

    def __enter__(self) -> "TeeOutput":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        """Context manager exit."""
        self.flush()
        return False


def _restore_streams() -> None:
    """Restore original stdout/stderr on exit.

    This is registered as an atexit handler to ensure streams are
    restored even if the script exits abnormally.
    """
    global _tee_active
    if _tee_active:
        sys.stdout = _original_stdout
        sys.stderr = _original_stderr
        _tee_active = False


# Register cleanup handler
atexit.register(_restore_streams)


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


def setup_run_logging(
    log_base_dir: Path,
    suite_name: str,
    timestamp: Optional[str] = None,
    log_level: str = "INFO",
    tee_output: bool = True,
) -> Path:
    """Setup logging to timestamped directory for pipeline runs.

    Creates a log directory under log_base_dir/suite_name/timestamp/
    and configures both console and file logging (file is JSON format).

    This function also tees stdout and stderr to the log file so that
    print() statements are captured alongside structured logger output.

    Args:
        log_base_dir: Base directory for logs (e.g., Path("logs"))
        suite_name: Hypothesis suite name (e.g., "H1_CashHoldings")
        timestamp: Optional timestamp string. If None, generates current timestamp.
        log_level: Logging level (default: "INFO")
        tee_output: If True, capture print() output to log file (default: True)

    Returns:
        Path to the log directory created.
    """
    global _tee_active
    from datetime import datetime as dt

    if timestamp is None:
        timestamp = dt.now().strftime("%Y-%m-%d_%H%M%S")

    log_dir = log_base_dir / suite_name / timestamp
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "run.log"

    # Reconfigure with file output (configure_logging handles handler cleanup)
    configure_logging(log_level=log_level, log_file=log_file)

    # Tee stdout and stderr to log file so print() statements are captured
    # This is crucial for econometric scripts that use print() for all output
    if tee_output:
        try:
            # Open in append mode since configure_logging already created the file
            # Use UTF-8 encoding for Windows compatibility
            log_handle = open(log_file, "a", encoding="utf-8")

            # Install tee for stdout (no prefix)
            sys.stdout = TeeOutput(log_handle, _original_stdout, prefix="")

            # Install tee for stderr with prefix for clarity
            sys.stderr = TeeOutput(log_handle, _original_stderr, prefix="STDERR")

            _tee_active = True

        except IOError as e:
            # If we can't open the log file for tee, continue without tee
            # Don't crash the entire run just because logging tee failed
            print(
                f"WARNING: Could not tee stdout to log file: {e}",
                file=_original_stderr,
            )

    return log_dir


__all__ = ["configure_logging", "get_logger", "setup_run_logging", "TeeOutput"]
