"""Integration tests for LoggingSettings with configure_logging()."""

import logging
import pytest
import structlog

from f1d.shared.logging import configure_logging, LoggingSettings
from f1d.shared.config.base import LoggingSettings as BaseLoggingSettings


@pytest.fixture(autouse=True)
def reset_logging():
    """Reset logging configuration before and after each test."""
    # Clear structlog context
    structlog.contextvars.clear_contextvars()

    # Reset root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    yield

    # Clean up after test
    structlog.contextvars.clear_contextvars()
    root_logger = logging.getLogger()
    root_logger.handlers.clear()


class TestLoggingSettingsIntegration:
    """Tests for LoggingSettings integration with configure_logging()."""

    def test_configure_logging_accepts_settings(self):
        """Test that configure_logging accepts LoggingSettings parameter."""
        settings = LoggingSettings(level="DEBUG")
        configure_logging(settings=settings)
        logger = logging.getLogger()
        assert logger.level == logging.DEBUG

    def test_configure_logging_backward_compatible(self):
        """Test that configure_logging works without settings parameter."""
        configure_logging(log_level="WARNING")
        logger = logging.getLogger()
        assert logger.level == logging.WARNING

    def test_explicit_parameter_overrides_settings(self):
        """Test that explicit log_level parameter overrides settings.level."""
        settings = LoggingSettings(level="DEBUG")
        configure_logging(log_level="ERROR", settings=settings)
        logger = logging.getLogger()
        assert logger.level == logging.ERROR  # Parameter wins

    def test_logging_settings_from_config_module(self):
        """Test that LoggingSettings from config.base works with configure_logging."""
        settings = BaseLoggingSettings(level="CRITICAL")
        configure_logging(settings=settings)
        logger = logging.getLogger()
        assert logger.level == logging.CRITICAL

    def test_default_level_uses_settings_when_provided(self):
        """Test that default log_level uses settings.level when provided."""
        settings = LoggingSettings(level="WARNING")
        configure_logging(settings=settings)
        # Since log_level is not specified, it should use settings.level
        logger = logging.getLogger()
        assert logger.level == logging.WARNING

    def test_settings_level_case_insensitive(self):
        """Test that LoggingSettings normalizes level to uppercase."""
        settings = LoggingSettings(level="debug")  # lowercase
        configure_logging(settings=settings)
        logger = logging.getLogger()
        assert logger.level == logging.DEBUG

    def test_non_default_level_uses_parameter_not_settings(self):
        """Test that non-default log_level parameter overrides settings.

        When user passes a non-default log_level (not "INFO"),
        the explicit parameter should be used instead of settings.level.
        """
        settings = LoggingSettings(level="DEBUG")
        # Explicit WARNING (not default INFO) should override settings
        configure_logging(log_level="WARNING", settings=settings)
        logger = logging.getLogger()
        assert logger.level == logging.WARNING

    def test_logging_settings_default_level(self):
        """Test that LoggingSettings defaults to INFO."""
        settings = LoggingSettings()
        configure_logging(settings=settings)
        logger = logging.getLogger()
        assert logger.level == logging.INFO
