"""Logging handlers for dual output configuration.

This module provides handler configuration for dual output logging:
human-readable console output and JSON-formatted file output.

Example:
    >>> from f1d.shared.logging import configure_dual_output
    >>> configure_dual_output(log_file=Path("3_Logs/pipeline.log"))
    >>> logger.info("processing_started", rows=1000)
    # Console: colored, human-readable
    # File: JSON with all fields
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import structlog


# Default log directory
DEFAULT_LOG_DIR = Path("3_Logs")


def get_log_file_path(
    script_name: str,
    log_dir: Optional[Path] = None,
    extension: str = "log"
) -> Path:
    """Generate a log file path following project conventions.

    Args:
        script_name: Name of the script (e.g., "script_32_construct_variables").
        log_dir: Directory for log files. Defaults to 3_Logs/.
        extension: File extension (default: "log").

    Returns:
        Path to the log file.

    Example:
        >>> get_log_file_path("script_32_construct_variables")
        PosixPath('3_Logs/script_32_construct_variables.log')
    """
    base_dir = log_dir or DEFAULT_LOG_DIR
    return base_dir / f"{script_name}.{extension}"


def get_timestamped_log_path(
    script_name: str,
    log_dir: Optional[Path] = None,
    extension: str = "log"
) -> Path:
    """Generate a timestamped log file path.

    Args:
        script_name: Name of the script.
        log_dir: Directory for log files. Defaults to 3_Logs/.
        extension: File extension (default: "log").

    Returns:
        Path to the timestamped log file.

    Example:
        >>> get_timestamped_log_path("script_32")
        PosixPath('3_Logs/script_32_20240115_143022.log')
    """
    base_dir = log_dir or DEFAULT_LOG_DIR
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return base_dir / f"{script_name}_{timestamp}.{extension}"


def configure_dual_output(
    log_file: Optional[Path] = None,
    log_level: str = "INFO",
    console_colors: bool = True,
    file_json: bool = True,
    log_dir: Optional[Path] = None,
) -> logging.Logger:
    """Configure logging with dual output: console (human) + file (JSON).

    This function sets up two handlers:
    1. Console handler with human-readable output (colored by default)
    2. File handler with JSON-formatted output (for machine parsing)

    Args:
        log_file: Path to log file. If None, no file logging.
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        console_colors: Enable colored console output.
        file_json: Use JSON format for file output.
        log_dir: Default directory for log files if log_file is relative.

    Returns:
        Configured root logger.

    Example:
        >>> logger = configure_dual_output(
        ...     log_file=Path("3_Logs/pipeline.log"),
        ...     log_level="DEBUG"
        ... )
        >>> logger.info("started", rows=1000)
    """
    # Shared processors
    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    # Configure structlog
    structlog.configure(
        processors=shared_processors + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Console handler - human readable
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))

    if console_colors:
        console_renderer = structlog.dev.ConsoleRenderer(colors=True)
    else:
        console_renderer = structlog.dev.ConsoleRenderer(colors=False)

    console_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=shared_processors,
            processors=[console_renderer],
        )
    )
    root_logger.addHandler(console_handler)

    # File handler - JSON format
    if log_file:
        # Ensure directory exists
        if log_dir and not log_file.is_absolute():
            log_file = log_dir / log_file
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(getattr(logging, log_level.upper()))

        if file_json:
            file_renderer = structlog.processors.JSONRenderer()
        else:
            file_renderer = structlog.dev.ConsoleRenderer(colors=False)

        file_handler.setFormatter(
            structlog.stdlib.ProcessorFormatter(
                foreign_pre_chain=shared_processors,
                processors=[file_renderer],
            )
        )
        root_logger.addHandler(file_handler)

    return root_logger


def configure_script_logging(
    script_name: str,
    log_level: str = "INFO",
    log_dir: Optional[Path] = None,
    timestamped: bool = False,
) -> logging.Logger:
    """Configure logging for a specific script.

    Convenience function that sets up dual output logging for a script
    with automatic log file path generation.

    Args:
        script_name: Name of the script (for log file naming).
        log_level: Logging level.
        log_dir: Directory for log files. Defaults to 3_Logs/.
        timestamped: If True, include timestamp in log filename.

    Returns:
        Configured root logger.

    Example:
        >>> # At the start of a script:
        >>> logger = configure_script_logging(
        ...     script_name="script_32_construct_variables",
        ...     log_level="DEBUG"
        ... )
    """
    base_dir = log_dir or DEFAULT_LOG_DIR

    if timestamped:
        log_file = get_timestamped_log_path(script_name, base_dir)
    else:
        log_file = get_log_file_path(script_name, base_dir)

    return configure_dual_output(
        log_file=log_file,
        log_level=log_level,
        log_dir=base_dir,
    )


class LogFileRotator:
    """Manages log file rotation by timestamp.

    Creates new log files based on time intervals or size thresholds.
    Designed for long-running processes.

    Attributes:
        base_path: Base path for log files.
        current_file: Current log file path.
        rotation_interval: Seconds between rotations.

    Example:
        >>> rotator = LogFileRotator(Path("3_Logs/pipeline"))
        >>> log_file = rotator.get_current_file()
    """

    def __init__(
        self,
        base_path: Path,
        rotation_interval: int = 86400,  # 24 hours in seconds
    ):
        """Initialize log file rotator.

        Args:
            base_path: Base path for log files (without extension).
            rotation_interval: Seconds between rotations.
        """
        self.base_path = base_path
        self.rotation_interval = rotation_interval
        self._current_file: Optional[Path] = None
        self._last_rotation: Optional[datetime] = None

    def get_current_file(self) -> Path:
        """Get the current log file path, rotating if needed.

        Returns:
            Path to the current log file.
        """
        now = datetime.now()

        if self._should_rotate(now):
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            self._current_file = Path(f"{self.base_path}_{timestamp}.log")
            self._last_rotation = now

        return self._current_file or self._get_initial_file(now)

    def _should_rotate(self, now: datetime) -> bool:
        """Check if log file should be rotated.

        Args:
            now: Current datetime.

        Returns:
            True if rotation is needed.
        """
        if self._last_rotation is None:
            return True

        elapsed = (now - self._last_rotation).total_seconds()
        return elapsed >= self.rotation_interval

    def _get_initial_file(self, now: datetime) -> Path:
        """Get initial log file path.

        Args:
            now: Current datetime.

        Returns:
            Path to initial log file.
        """
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        return Path(f"{self.base_path}_{timestamp}.log")


__all__ = [
    "configure_dual_output",
    "configure_script_logging",
    "get_log_file_path",
    "get_timestamped_log_path",
    "LogFileRotator",
    "DEFAULT_LOG_DIR",
]
