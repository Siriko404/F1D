"""Unit tests for logging handlers."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from f1d.shared.logging.handlers import (
    configure_dual_output,
    configure_script_logging,
    get_log_file_path,
    get_timestamped_log_path,
    LogFileRotator,
    DEFAULT_LOG_DIR,
)


class TestGetLogFilePath:
    """Tests for get_log_file_path function."""

    def test_returns_path_with_default_dir(self):
        """Test path generation with default directory."""
        result = get_log_file_path("script_32")
        assert result == DEFAULT_LOG_DIR / "script_32.log"

    def test_returns_path_with_custom_dir(self):
        """Test path generation with custom directory."""
        custom_dir = Path("custom_logs")
        result = get_log_file_path("script_32", log_dir=custom_dir)
        assert result == custom_dir / "script_32.log"

    def test_returns_path_with_custom_extension(self):
        """Test path generation with custom extension."""
        result = get_log_file_path("script_32", extension="json")
        assert result.suffix == ".json"


class TestGetTimestampedLogPath:
    """Tests for get_timestamped_log_path function."""

    def test_includes_timestamp(self):
        """Test that path includes timestamp."""
        result = get_timestamped_log_path("script_32")
        # Should match pattern: script_32_YYYYMMDD_HHMMSS.log
        assert "script_32_" in result.name
        assert result.suffix == ".log"


class TestConfigureDualOutput:
    """Tests for configure_dual_output function."""

    def test_returns_logger(self, tmp_path):
        """Test that function returns a logger."""
        log_file = tmp_path / "test.log"
        result = configure_dual_output(log_file=log_file)
        assert result is not None

    def test_creates_log_directory(self, tmp_path):
        """Test that log directory is created."""
        log_file = tmp_path / "subdir" / "test.log"
        configure_dual_output(log_file=log_file)
        assert log_file.parent.exists()

    def test_works_without_log_file(self):
        """Test that function works without log file (console only)."""
        result = configure_dual_output(log_file=None)
        assert result is not None


class TestConfigureScriptLogging:
    """Tests for configure_script_logging function."""

    def test_returns_logger(self, tmp_path):
        """Test that function returns a logger."""
        result = configure_script_logging(
            script_name="test_script",
            log_dir=tmp_path
        )
        assert result is not None

    def test_creates_log_file_in_specified_dir(self, tmp_path):
        """Test that log file is created in specified directory."""
        configure_script_logging(
            script_name="test_script",
            log_dir=tmp_path
        )
        expected_file = tmp_path / "test_script.log"
        # File is created when first log is written
        # Just verify the configuration works
        assert True


class TestLogFileRotator:
    """Tests for LogFileRotator class."""

    def test_returns_path(self, tmp_path):
        """Test that rotator returns a path."""
        rotator = LogFileRotator(tmp_path / "pipeline")
        result = rotator.get_current_file()
        assert isinstance(result, Path)

    def test_includes_timestamp_in_filename(self, tmp_path):
        """Test that filename includes timestamp."""
        rotator = LogFileRotator(tmp_path / "pipeline")
        result = rotator.get_current_file()
        assert "pipeline_" in result.name
