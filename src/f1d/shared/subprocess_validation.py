#!/usr/bin/env python3
"""
================================================================================
SHARED MODULE: Subprocess Validation
================================================================================
ID: shared/subprocess_validation
Description: Secure subprocess execution with path validation.

Purpose: Provides secure subprocess execution to prevent path traversal attacks
         (CWE-427: Uncontrolled Search Path Element).

Security:
    - Validates all script paths are within allowed directories
    - Uses absolute paths (Path.resolve())
    - Prevents execution of scripts outside intended directories

Inputs:
    - Script paths to validate

Outputs:
    - Validated subprocess execution

Main Functions:
    - validate_subprocess_path(): Validate subprocess script path

Dependencies:
    - Utility module for subprocess validation
    - Uses: subprocess, sys

Author: Thesis Author
Date: 2026-02-11
================================================================================
"""

import subprocess
import sys
from pathlib import Path
from typing import Union


def validate_script_path(script_path: Path, allowed_dir: Path) -> Path:
    """
    Validate that script_path is within allowed_dir and is an absolute path.

    Security: Prevents path traversal attacks (CWE-427).

    Args:
        script_path: Path to script to validate (can be relative)
        allowed_dir: Directory script must be contained within

    Raises:
        ValueError: If path is outside allowed directory or not a .py file
        FileNotFoundError: If script doesn't exist

    Returns:
        Path: Absolute, validated script path
    """
    # Convert to absolute path (resolves symlinks, .., .)
    # Relative paths are resolved against allowed_dir so that callers can pass
    # short names like Path("subdir/script.py") without depending on CWD.
    allowed_dir = allowed_dir.resolve()
    script_path = Path(script_path)
    if not script_path.is_absolute():
        script_path = (allowed_dir / script_path).resolve()
    else:
        script_path = script_path.resolve()

    # Check if script exists
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")

    # Check if path is within allowed directory
    try:
        script_path.relative_to(allowed_dir)
    except ValueError:
        raise ValueError(
            f"Script path outside allowed directory:\n"
            f"  Script: {script_path}\n"
            f"  Allowed: {allowed_dir}"
        )

    # Check file extension is .py
    if script_path.suffix != ".py":
        raise ValueError(f"Script must be .py file: {script_path}")

    return script_path


def run_validated_subprocess(
    script_path: Path,
    allowed_dir: Path,
    capture_output: bool = True,
    check: bool = False,
) -> subprocess.CompletedProcess[str]:
    """
    Run a script with validated path.

    Args:
        script_path: Path to script (can be relative)
        allowed_dir: Directory script must be within
        capture_output: Capture stdout/stderr
        check: Raise exception on non-zero exit

    Returns:
        subprocess.CompletedProcess
    """
    # Validate path before execution
    validated_path = validate_script_path(script_path, allowed_dir)

    # Execute with validated absolute path
    result = subprocess.run(
        [sys.executable, str(validated_path)],
        capture_output=capture_output,
        text=True,
        check=check,
    )

    return result
