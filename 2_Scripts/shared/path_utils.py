#!/usr/bin/env python3
"""
================================================================================
SHARED MODULE: Path Utilities
================================================================================
ID: shared/path_utils
Description: Provides robust path validation and directory creation helpers
             using pathlib. Handles cross-platform path operations with
             proper error handling and validation.

Inputs:
    - Path objects for validation (pathlib.Path)
    - Optional validation flags (must_exist, must_be_writable)

Outputs:
    - Validated Path objects (resolved to absolute paths)
    - Created directories (if needed)
    - Available disk space in GB

Deterministic: true
================================================================================
"""

from pathlib import Path
from typing import Optional


class PathValidationError(Exception):
    """Raised when path validation fails."""

    pass


def validate_output_path(
    path: Path, must_exist: bool = False, must_be_writable: bool = True
) -> Path:
    """
    Validate output path exists and is accessible.

    Args:
        path: Path to validate
        must_exist: If True, raise error if path doesn't exist
        must_be_writable: If True, check path is writable

    Returns:
        Validated Path object (resolved to absolute)

    Raises:
        PathValidationError: If validation fails
    """
    if must_exist and not path.exists():
        raise PathValidationError(f"Path does not exist: {path}")

    if path.exists():
        if not path.is_dir():
            raise PathValidationError(f"Path is not a directory: {path}")

        if must_be_writable:
            try:
                test_file = path / ".write_test"
                test_file.touch()
                test_file.unlink()
            except OSError as e:
                raise PathValidationError(f"Path not writable: {path} ({e})")

    # Resolve to absolute path (handles symlinks, "..")
    resolved = path.resolve()
    return resolved


def ensure_output_dir(path: Path) -> Path:
    """
    Ensure output directory exists, creating if necessary.

    Args:
        path: Path to directory

    Returns:
        Resolved Path object (absolute)

    Raises:
        PathValidationError: If directory creation fails
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise PathValidationError(f"Failed to create directory {path}: {e}")

    return path.resolve()


def validate_input_file(path: Path, must_exist: bool = True) -> Path:
    """
    Validate input file exists and is readable.

    Args:
        path: Path to input file
        must_exist: If True, raise error if file doesn't exist

    Returns:
        Validated Path object (resolved to absolute)

    Raises:
        PathValidationError: If validation fails
    """
    if must_exist and not path.exists():
        raise PathValidationError(f"Input file does not exist: {path}")

    if path.exists() and not path.is_file():
        raise PathValidationError(f"Path is not a file: {path}")

    # Resolve to absolute path
    resolved = path.resolve()
    return resolved


def get_available_disk_space(path: Path) -> float:
    """
    Get available disk space in GB for a given path.

    Args:
        path: Path to check disk space

    Returns:
        Available disk space in GB (float)
    """
    import shutil

    stat = shutil.disk_usage(path)
    return stat.free / (1024**3)  # Convert to GB
