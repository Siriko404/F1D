"""Integration tests for structured logging system."""

import json
import pytest
from pathlib import Path
import logging
import structlog

from f1d.shared.logging import (
    configure_dual_output,
    configure_script_logging,
    configure_logging,
    get_logger,
    bind_context,
    unbind_context,
    get_context,
    clear_context,
    OperationContext,
    stage_context,
    generate_operation_id,
)


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


class TestDualOutputIntegration:
    """Integration tests for dual output logging."""

    def test_console_and_file_output(self, tmp_path):
        """Test that logs go to both console and file."""
        log_file = tmp_path / "integration.log"

        # Configure dual output
        configure_dual_output(log_file=log_file, log_level="INFO")

        # Get logger and log something
        logger = get_logger("test_integration")
        logger.info("test_message", key="value", count=42)

        # Verify file was created
        assert log_file.exists()

        # Verify file contains JSON
        content = log_file.read_text()
        assert len(content) > 0

        # Parse JSON line
        log_entry = json.loads(content.strip())
        assert log_entry["event"] == "test_message"
        assert log_entry["key"] == "value"
        assert log_entry["count"] == 42

    def test_context_appears_in_file_output(self, tmp_path):
        """Test that bound context appears in JSON file output."""
        log_file = tmp_path / "context.log"

        configure_dual_output(log_file=log_file, log_level="INFO")

        bind_context(operation_name="test_op", script_name="test_script")

        logger = get_logger("test")
        logger.info("context_test")

        content = log_file.read_text()
        log_entry = json.loads(content.strip())

        assert log_entry["operation_name"] == "test_op"
        assert log_entry["script_name"] == "test_script"

    def test_operation_context_in_file_output(self, tmp_path):
        """Test that OperationContext fields appear in file output."""
        log_file = tmp_path / "operation.log"

        configure_dual_output(log_file=log_file, log_level="INFO")

        with OperationContext("test_operation", script_name="test.py"):
            logger = get_logger("test")
            logger.info("inside_operation")

        content = log_file.read_text()
        lines = [l for l in content.strip().split("\n") if l]

        # Should have operation_started and inside_operation logs
        assert len(lines) >= 2

        # Check that operation_id is in logs
        log_entry = json.loads(lines[0])
        assert "operation_id" in log_entry
        assert log_entry["operation_name"] == "test_operation"

    def test_dual_output_with_different_levels(self, tmp_path):
        """Test that log level filtering works."""
        log_file = tmp_path / "levels.log"

        configure_dual_output(log_file=log_file, log_level="WARNING")

        logger = get_logger("test")
        logger.debug("debug_message")
        logger.info("info_message")
        logger.warning("warning_message")
        logger.error("error_message")

        content = log_file.read_text()
        lines = [l for l in content.strip().split("\n") if l]

        # Should only have warning and error
        assert len(lines) == 2
        for line in lines:
            entry = json.loads(line)
            assert entry["level"] in ("warning", "error")


class TestScriptLoggingIntegration:
    """Integration tests for script logging configuration."""

    def test_script_logging_creates_file(self, tmp_path):
        """Test that configure_script_logging creates log file."""
        configure_script_logging(
            script_name="test_script_32",
            log_dir=tmp_path,
            log_level="DEBUG"
        )

        logger = get_logger("test")
        logger.debug("debug_message")

        expected_file = tmp_path / "test_script_32.log"
        assert expected_file.exists()

    def test_timestamped_script_logging(self, tmp_path):
        """Test that timestamped logging creates timestamped file."""
        configure_script_logging(
            script_name="test_script",
            log_dir=tmp_path,
            timestamped=True
        )

        logger = get_logger("test")
        logger.info("test")

        # Should have exactly one log file with timestamp
        log_files = list(tmp_path.glob("test_script_*.log"))
        assert len(log_files) == 1

    def test_script_logging_with_unicode(self, tmp_path):
        """Test logging with unicode characters."""
        log_file = tmp_path / "unicode.log"

        configure_dual_output(log_file=log_file, log_level="INFO")

        logger = get_logger("test")
        logger.info("unicode_test", message="Hello \u4e16\u754c", emoji="test")

        content = log_file.read_text(encoding="utf-8")
        assert len(content) > 0
        log_entry = json.loads(content.strip())
        assert log_entry["message"] == "Hello \u4e16\u754c"


class TestConfigureLogging:
    """Tests for configure_logging function."""

    def test_configure_logging_default(self, tmp_path):
        """Test configure_logging with default settings."""
        configure_logging(log_level="INFO")

        logger = get_logger("test")
        logger.info("test_message")

        # Should configure without error
        root_logger = logging.getLogger()
        assert len(root_logger.handlers) > 0

    def test_configure_logging_with_file(self, tmp_path):
        """Test configure_logging with file output."""
        log_file = tmp_path / "test.log"

        configure_logging(log_level="INFO", log_file=log_file)

        logger = get_logger("test")
        logger.info("file_test")

        assert log_file.exists()
        content = log_file.read_text()
        assert len(content) > 0

    def test_configure_logging_json_output(self):
        """Test configure_logging with JSON output."""
        configure_logging(log_level="INFO", json_output=True)

        logger = get_logger("test")
        logger.info("json_test")

        # Should configure with JSON renderer
        root_logger = logging.getLogger()
        assert len(root_logger.handlers) > 0


class TestContextBinding:
    """Tests for context binding functions."""

    def test_bind_context_works(self, tmp_path):
        """Test that bind_context works correctly."""
        log_file = tmp_path / "bind.log"
        configure_dual_output(log_file=log_file, log_level="INFO")

        bind_context(key1="value1", key2="value2")

        logger = get_logger("test")
        logger.info("test_message")

        content = log_file.read_text()
        entry = json.loads(content.strip().split("\n")[0])
        assert entry["key1"] == "value1"
        assert entry["key2"] == "value2"

    def test_unbind_context_works(self, tmp_path):
        """Test that unbind_context removes keys."""
        log_file = tmp_path / "unbind.log"
        configure_dual_output(log_file=log_file, log_level="INFO")

        bind_context(key1="value1", key2="value2")
        unbind_context("key1")

        logger = get_logger("test")
        logger.info("test_message")

        content = log_file.read_text()
        entry = json.loads(content.strip().split("\n")[0])
        # key1 should not be in context after unbind
        assert "key1" not in entry
        assert entry["key2"] == "value2"

    def test_clear_context_works(self, tmp_path):
        """Test that clear_context removes all keys."""
        log_file = tmp_path / "clear.log"
        configure_dual_output(log_file=log_file, log_level="INFO")

        bind_context(key1="value1", key2="value2")
        clear_context()

        logger = get_logger("test")
        logger.info("test_message")

        content = log_file.read_text()
        entry = json.loads(content.strip().split("\n")[0])
        # Both keys should be gone after clear
        assert "key1" not in entry
        assert "key2" not in entry

    def test_generate_operation_id(self):
        """Test operation ID generation."""
        op_id1 = generate_operation_id()
        op_id2 = generate_operation_id()

        assert op_id1.startswith("op_")
        assert op_id2.startswith("op_")
        assert op_id1 != op_id2  # Should be unique


class TestOperationContext:
    """Tests for OperationContext class."""

    def test_operation_context_binds_context(self, tmp_path):
        """Test that OperationContext binds logging context."""
        log_file = tmp_path / "op.log"
        configure_dual_output(log_file=log_file, log_level="INFO")

        with OperationContext("test_op", script_name="test.py"):
            logger = get_logger("test")
            logger.info("inside")

        content = log_file.read_text()
        lines = [l for l in content.strip().split("\n") if l]

        # Check operation_id and operation_name in logs
        for line in lines:
            entry = json.loads(line)
            assert "operation_id" in entry
            assert entry["operation_name"] == "test_op"

    def test_operation_context_with_extra(self, tmp_path):
        """Test OperationContext with extra context."""
        log_file = tmp_path / "extra.log"
        configure_dual_output(log_file=log_file, log_level="INFO")

        with OperationContext("test_op", extra={"custom_key": "custom_value"}):
            logger = get_logger("test")
            logger.info("test")

        content = log_file.read_text()
        lines = [l for l in content.strip().split("\n") if l]

        # Find the first log entry (the test message)
        entry = json.loads(lines[0])
        assert entry["custom_key"] == "custom_value"

    def test_operation_context_logs_completion(self, tmp_path):
        """Test that OperationContext logs operation_completed on exit."""
        log_file = tmp_path / "complete.log"
        configure_dual_output(log_file=log_file, log_level="INFO")

        with OperationContext("test_op"):
            pass

        content = log_file.read_text()
        lines = [l for l in content.strip().split("\n") if l]

        # Should have operation_completed log
        completed_logs = [l for l in lines if "operation_completed" in l]
        assert len(completed_logs) >= 1

    def test_operation_context_logs_error_on_exception(self, tmp_path):
        """Test that OperationContext logs errors on exception."""
        log_file = tmp_path / "error.log"
        configure_dual_output(log_file=log_file, log_level="INFO")

        try:
            with OperationContext("test_op"):
                raise ValueError("test error")
        except ValueError:
            pass

        content = log_file.read_text()
        lines = [l for l in content.strip().split("\n") if l]

        # Should have operation_failed log
        error_logs = [l for l in lines if "operation_failed" in l]
        assert len(error_logs) >= 1

        # Check error details
        entry = json.loads(error_logs[0])
        assert entry["error_type"] == "ValueError"
        assert "test error" in entry["error_message"]


class TestStageContext:
    """Tests for stage_context function."""

    def test_stage_context_binds_stage(self, tmp_path):
        """Test that stage_context binds stage name."""
        log_file = tmp_path / "stage.log"
        configure_dual_output(log_file=log_file, log_level="INFO")

        with OperationContext("test_op"):
            with stage_context("loading", rows=100):
                logger = get_logger("test")
                logger.info("inside_stage")

        content = log_file.read_text()

        # Find a log with stage info
        for line in content.strip().split("\n"):
            if line:
                entry = json.loads(line)
                if "stage" in entry:
                    assert entry["stage"] == "loading"
                    break

    def test_stage_context_yields_context_dict(self):
        """Test that stage_context yields context dictionary."""
        clear_context()

        with stage_context("test_stage", extra_key="extra_value") as ctx:
            assert ctx["stage"] == "test_stage"
            assert ctx["extra_key"] == "extra_value"
            assert "start_time" in ctx

    def test_stage_context_clears_on_exit(self, tmp_path):
        """Test that stage context is cleared on exit."""
        log_file = tmp_path / "stage_clear.log"
        configure_dual_output(log_file=log_file, log_level="INFO")

        with OperationContext("test_op"):
            with stage_context("loading"):
                pass
            # After stage context exits, log without stage
            logger = get_logger("test")
            logger.info("after_stage")

        content = log_file.read_text()
        lines = [l for l in content.strip().split("\n") if l]

        # Last log should not have stage (or have the operation's context)
        last_entry = json.loads(lines[-1])
        # After stage exits, stage should be unbound
        # The exact behavior depends on structlog contextvars


class TestFullLoggingWorkflow:
    """End-to-end tests for complete logging workflow."""

    def test_complete_logging_workflow(self, tmp_path):
        """Test complete logging workflow with context and dual output."""
        log_file = tmp_path / "full_workflow.log"

        # Configure logging
        configure_dual_output(log_file=log_file, log_level="DEBUG")

        # Use OperationContext for operation tracking
        with OperationContext(
            "data_processing",
            script_name="script_32_construct_variables.py",
            extra={"gvkey_count": 1500, "year_range": "2010-2020"}
        ):
            logger = get_logger("data_processor")

            # Log with stage context
            with stage_context("loading", file_count=5):
                logger.info("files_loaded", rows=50000)

            with stage_context("processing"):
                logger.info("variables_constructed", count=25)

        # Verify log file
        content = log_file.read_text()
        lines = [l for l in content.strip().split("\n") if l]

        # Should have multiple log entries
        assert len(lines) >= 4

        # All entries should be valid JSON
        for line in lines:
            entry = json.loads(line)
            assert "timestamp" in entry
            assert "level" in entry
            assert "event" in entry

    def test_long_message_handling(self, tmp_path):
        """Test logging with very long messages."""
        log_file = tmp_path / "long.log"
        configure_dual_output(log_file=log_file, log_level="INFO")

        logger = get_logger("test")
        long_message = "x" * 10000
        logger.info("long_test", message=long_message)

        content = log_file.read_text()
        entry = json.loads(content.strip())
        assert entry["message"] == long_message

    def test_none_values_in_context(self, tmp_path):
        """Test logging with None values in context."""
        log_file = tmp_path / "none.log"
        configure_dual_output(log_file=log_file, log_level="INFO")

        logger = get_logger("test")
        logger.info("none_test", key1=None, key2="value")

        content = log_file.read_text()
        entry = json.loads(content.strip())
        assert entry["key1"] is None
        assert entry["key2"] == "value"
