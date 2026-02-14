"""Integration tests for structured logging system."""

import json
import pytest
from pathlib import Path
import logging

from f1d.shared.logging import (
    configure_dual_output,
    configure_script_logging,
    get_logger,
    bind_context,
    OperationContext,
    stage_context,
)


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
