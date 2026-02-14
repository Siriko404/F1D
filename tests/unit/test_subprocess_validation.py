"""
Unit tests for subprocess_validation module.

Tests path validation, subprocess execution, and security
prevention of path traversal attacks.
"""

import pytest
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

from f1d.shared.subprocess_validation import (
    validate_script_path,
    run_validated_subprocess,
)


class TestValidateScriptPath:
    """Tests for validate_script_path function."""

    def test_validate_script_path_success(self, tmp_path):
        """Test path validation allows valid script within allowed directory."""
        # Create a test script in allowed directory
        script = tmp_path / "test_script.py"
        script.write_text("print('hello')")
        allowed_dir = tmp_path

        result = validate_script_path(script, allowed_dir)
        assert result.is_absolute()
        assert result == script.resolve()

    def test_validate_script_path_not_py_file(self, tmp_path):
        """Test path validation rejects non-.py files."""
        # Create a non-Python file
        not_py_file = tmp_path / "test.txt"
        not_py_file.write_text("not a python file")
        allowed_dir = tmp_path

        with pytest.raises(ValueError, match="Script must be .py file"):
            validate_script_path(not_py_file, allowed_dir)

    def test_validate_script_path_outside_directory(self, tmp_path):
        """Test path validation rejects script outside allowed directory."""
        # Create script in temp directory
        script = tmp_path / "test_script.py"
        script.write_text("print('outside allowed')")
        # Use different directory as allowed
        allowed_dir = tmp_path / "other_dir"

        with pytest.raises(ValueError, match="outside allowed directory"):
            validate_script_path(script, allowed_dir)

    def test_validate_script_path_not_in_allowed_dir(self, tmp_path):
        """Test path validation rejects path not under allowed directory."""
        # Create script using parent directory traversal
        script = tmp_path / "other_dir" / "test_script.py"
        script.parent.mkdir(parents=True, exist_ok=True)
        script.write_text("print('outside')")
        allowed_dir = tmp_path / "allowed_dir"

        with pytest.raises(ValueError, match="outside allowed directory"):
            validate_script_path(script, allowed_dir)

    def test_validate_script_path_file_not_found(self, tmp_path):
        """Test path validation raises error for non-existent file."""
        script = tmp_path / "nonexistent.py"
        allowed_dir = tmp_path

        with pytest.raises(FileNotFoundError, match="Script not found"):
            validate_script_path(script, allowed_dir)

    @pytest.mark.parametrize(
        "path_name,should_validate",
        [
            ("script.py", True),
            ("main.py", True),
            ("test_123.py", True),
            ("script.txt", False),
            ("script.sh", False),
        ],
    )
    def test_validate_script_path_extension_check(
        self, path_name, should_validate, tmp_path
    ):
        """Test path validation checks .py extension."""
        script = tmp_path / path_name
        script.write_text("print('test')")

        allowed_dir = tmp_path

        if should_validate:
            result = validate_script_path(script, allowed_dir)
            assert result.suffix == ".py"
        else:
            with pytest.raises(ValueError, match="Script must be .py file"):
                validate_script_path(script, allowed_dir)

    @pytest.mark.parametrize(
        "rel_path,expected_valid",
        [
            ("../script.py", False),  # Parent directory traversal
            ("../../script.py", False),  # Multi-level traversal
            (".", False),  # Current directory
            ("..", False),  # Parent directory
        ],
    )
    def test_validate_script_path_traversal_prevention(
        self, rel_path, expected_valid, tmp_path
    ):
        """Test path validation prevents directory traversal attacks."""
        # Don't create script - test that traversal is caught
        allowed_dir = tmp_path

        if not expected_valid:
            # Should not validate traversal attempts
            with pytest.raises((ValueError, FileNotFoundError)):
                validate_script_path(rel_path, allowed_dir)


class TestRunValidatedSubprocess:
    """Tests for run_validated_subprocess function."""

    @patch("subprocess.run")
    def test_run_validated_subprocess_success(self, mock_run, tmp_path):
        """Test subprocess execution with validated path."""
        # Create test script
        script = tmp_path / "test.py"
        script.write_text("print('success')")
        allowed_dir = tmp_path

        # Mock subprocess.run to return success
        mock_run.return_value = subprocess.CompletedProcess(
            args=["python", str(script)], returncode=0, stdout="success\n", stderr=""
        )

        result = run_validated_subprocess(script, allowed_dir)

        assert result.returncode == 0
        assert result.stdout == "success\n"

        # Verify subprocess.run was called with validated path
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert sys.executable in call_args

    @patch("subprocess.run")
    def test_run_validated_subprocess_with_capture(self, mock_run, tmp_path):
        """Test subprocess execution with capture_output=True."""
        script = tmp_path / "test.py"
        script.write_text("print('captured')")
        allowed_dir = tmp_path

        mock_run.return_value = subprocess.CompletedProcess(
            args=["python", str(script)], returncode=0, stdout="captured\n", stderr=""
        )

        result = run_validated_subprocess(script, allowed_dir, capture_output=True)

        assert result.stdout == "captured\n"

    @patch("subprocess.run")
    def test_run_validated_subprocess_without_capture(self, mock_run, tmp_path):
        """Test subprocess execution with capture_output=False."""
        script = tmp_path / "test.py"
        script.write_text("print('output')")
        allowed_dir = tmp_path

        # When capture_output=False, stdout and stderr are empty strings
        mock_run.return_value = subprocess.CompletedProcess(
            args=["python", str(script)], returncode=0, stdout="", stderr=""
        )

        result = run_validated_subprocess(script, allowed_dir, capture_output=False)

        # When capture_output=False, stdout/stderr are empty strings
        assert result.stdout == ""

    @patch("subprocess.run")
    def test_run_validated_subprocess_check_false(self, mock_run, tmp_path):
        """Test subprocess execution with check=False (default)."""
        script = tmp_path / "test.py"
        script.write_text("print('test')")
        allowed_dir = tmp_path

        # Return non-zero exit code
        mock_run.return_value = subprocess.CompletedProcess(
            args=["python", str(script)],
            returncode=1,
            stdout="error\n",
            stderr="error message\n",
        )

        result = run_validated_subprocess(script, allowed_dir, check=False)

        assert result.returncode == 1

    def test_run_validated_subprocess_validation_failure(self, tmp_path):
        """Test subprocess doesn't run if path validation fails."""
        # Script in different directory
        script = tmp_path / "script.py"
        script.write_text("print('test')")
        allowed_dir = tmp_path / "other_dir"

        # Should raise during validation, not run subprocess
        with pytest.raises(ValueError, match="outside allowed directory"):
            run_validated_subprocess(script, allowed_dir)

    @patch("subprocess.run")
    def test_run_validated_subprocess_validates_before_exec(self, mock_run, tmp_path):
        """Test path validation happens before subprocess execution."""
        # Don't create script
        script = tmp_path / "nonexistent.py"
        allowed_dir = tmp_path

        # Should fail at validation step
        with pytest.raises(FileNotFoundError, match="Script not found"):
            run_validated_subprocess(script, allowed_dir)

        # subprocess.run should NOT be called
        mock_run.assert_not_called()


class TestSecurityFeatures:
    """Tests for security features in subprocess validation."""

    def test_prevents_path_traversal_with_dots(self, tmp_path):
        """Test path validation prevents ../../ traversal."""
        # Create script
        script = tmp_path / "safe.py"
        script.write_text("print('safe')")
        allowed_dir = tmp_path

        # Try to traverse up
        dangerous_path = tmp_path / ".." / "safe.py"

        with pytest.raises((ValueError, FileNotFoundError)):
            validate_script_path(dangerous_path, allowed_dir)

    @pytest.mark.parametrize(
        "filename",
        [
            "/etc/passwd",  # System file on Unix
            "C:\\Windows\\System32\\config",  # System file on Windows
        ],
    )
    def test_prevents_access_to_system_files(self, filename, tmp_path):
        """Test path validation prevents access to system files."""
        script = Path(filename)
        allowed_dir = tmp_path

        # Script doesn't exist in allowed directory
        with pytest.raises((FileNotFoundError, ValueError)):
            validate_script_path(script, allowed_dir)
