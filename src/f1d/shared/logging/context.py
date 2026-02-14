"""Context binding utilities for structured logging.

This module provides context management for correlating log messages
across operations, stages, and functions using structlog contextvars.

Example:
    >>> from f1d.shared.logging import bind_context, OperationContext
    >>> with OperationContext("financial_processing", script_name="script_32"):
    ...     logger.info("processing_started")  # Includes operation_id, script_name
"""

from __future__ import annotations

import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generator, Optional, cast

import structlog


def generate_operation_id() -> str:
    """Generate a unique operation ID.

    Returns:
        UUID-based operation ID in format 'op_{short_uuid}'.
    """
    return f"op_{uuid.uuid4().hex[:12]}"


def bind_context(**kwargs: Any) -> None:
    """Bind key-value pairs to the current logging context.

    Context is inherited by all log messages in the current scope
    and any child scopes.

    Args:
        **kwargs: Key-value pairs to bind to context.

    Example:
        >>> bind_context(gvkey_count=1500, stage="financial")
        >>> logger.info("processing_started")  # Includes gvkey_count, stage
    """
    structlog.contextvars.bind_contextvars(**kwargs)


def unbind_context(*keys: str) -> None:
    """Remove keys from the current logging context.

    Args:
        *keys: Context keys to remove.
    """
    structlog.contextvars.unbind_contextvars(*keys)


def get_context() -> dict[str, Any]:
    """Get the current logging context.

    Returns:
        Dictionary of current context bindings.
    """
    # structlog doesn't expose get directly, so we use a workaround
    # by accessing the internal context var
    # TYPE ERROR BASELINE: structlog.contextvars._context is internal API
    # with no public equivalent. Using cast for type safety.
    try:
        context_var = getattr(structlog.contextvars, "_context", None)
        if context_var is not None:
            context_val = context_var.get()
            if context_val is not None:
                return cast(dict[str, Any], context_val.copy())
    except (AttributeError, TypeError):
        pass
    return {}


def clear_context() -> None:
    """Clear all context bindings.

    Warning: This removes ALL context. Use sparingly.
    """
    structlog.contextvars.clear_contextvars()


@dataclass
class OperationContext:
    """Context manager for operation-scoped logging context.

    Automatically generates operation ID, tracks timing, and binds
    script/stage information for correlated logging.

    Attributes:
        operation_name: Human-readable operation name.
        operation_id: Unique operation identifier (auto-generated if not provided).
        script_name: Name of the script executing this operation.
        stage: Processing stage name.
        parent_id: Parent operation ID for nested operations.
        extra: Additional context key-value pairs.
        start_time: When the operation started (auto-set).

    Example:
        >>> with OperationContext("regression_analysis", script_name="script_44"):
        ...     run_regressions()  # All logs include operation_id, script_name
    """

    operation_name: str
    operation_id: str = field(default_factory=generate_operation_id)
    script_name: Optional[str] = None
    stage: Optional[str] = None
    parent_id: Optional[str] = None
    extra: dict[str, Any] = field(default_factory=dict)
    start_time: Optional[datetime] = None
    _logger: Any = field(default=None, repr=False)

    def __enter__(self) -> "OperationContext":
        """Enter the operation context, binding all context vars."""
        self.start_time = datetime.now()

        # Build context dictionary
        context: dict[str, Any] = {
            "operation_name": self.operation_name,
            "operation_id": self.operation_id,
        }

        if self.script_name:
            context["script_name"] = self.script_name
        if self.stage:
            context["stage"] = self.stage
        if self.parent_id:
            context["parent_id"] = self.parent_id

        # Add any extra context
        context.update(self.extra)

        # Bind to structlog contextvars
        bind_context(**context)

        # Get logger for this operation
        self._logger = structlog.get_logger()

        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the operation context, logging completion."""
        if self._logger is None:
            return

        # Calculate duration
        duration_seconds: Optional[float] = None
        if self.start_time:
            duration_seconds = (datetime.now() - self.start_time).total_seconds()

        if exc_type is not None:
            self._logger.error(
                "operation_failed",
                error_type=exc_type.__name__,
                error_message=str(exc_val),
                duration_seconds=duration_seconds,
            )
        else:
            self._logger.info(
                "operation_completed",
                duration_seconds=duration_seconds,
            )

        # Clear this operation's context (but preserve parent context)
        keys_to_clear = ["operation_name", "operation_id", "script_name", "stage"]
        if self.extra:
            keys_to_clear.extend(self.extra.keys())
        unbind_context(*keys_to_clear)


@contextmanager
def stage_context(stage_name: str, **extra: Any) -> Generator[dict[str, Any], None, None]:
    """Context manager for stage-scoped logging within an operation.

    Use this for sub-operations within a larger operation.

    Args:
        stage_name: Name of the processing stage.
        **extra: Additional context for this stage.

    Yields:
        Dictionary with stage context info.

    Example:
        >>> with OperationContext("pipeline", script_name="main"):
        ...     with stage_context("data_loading", rows=1000):
        ...         load_data()  # Logs include operation_id AND stage
    """
    stage_start = datetime.now()
    bind_context(stage=stage_name, **extra)

    logger = structlog.get_logger()
    logger.info("stage_started")

    try:
        yield {"stage": stage_name, "start_time": stage_start, **extra}
    finally:
        duration = (datetime.now() - stage_start).total_seconds()
        logger.info("stage_completed", duration_seconds=duration)

        # Clear stage-specific context
        keys = ["stage"] + list(extra.keys())
        unbind_context(*keys)


__all__ = [
    "bind_context",
    "unbind_context",
    "get_context",
    "clear_context",
    "generate_operation_id",
    "OperationContext",
    "stage_context",
]
