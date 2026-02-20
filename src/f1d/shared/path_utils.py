#!/usr/bin/env python3
"""Tier 1: Core shared utilities - Path Utilities

================================================================================
SHARED MODULE: Path Utilities
================================================================================
ID: shared/path_utils
Description: Provides robust path validation and directory creation helpers
             using pathlib. Handles cross-platform path operations with
             proper error handling and validation. Supports both new (ARCH-03)
             and legacy directory structures with backward compatibility.

Inputs:
    - Path objects for validation (pathlib.Path)
    - Optional validation flags (must_exist, must_be_writable)

Outputs:
    - Validated Path objects (resolved to absolute paths)
    - Created directories (if needed)
    - Available disk space in GB

Deterministic: true
Main Functions:
    - get_latest_output_dir(): Get latest output directory by timestamp
    - ensure_output_dir(): Create output directory if not exists
    - resolve_data_path(): Resolve path with backward compatibility

Dependencies:
    - Utility module for path utilities
    - Uses: pathlib

Author: Thesis Author
Date: 2026-02-11
Updated: 2026-02-13 (added ARCH-03 data directory support)
================================================================================
"""

from pathlib import Path
from typing import List, Optional
import re
import warnings


# ==============================================================================
# TIMESTAMP VALIDATION (Phase 89-03)
# ==============================================================================

# Regex pattern for valid timestamp format: YYYY-MM-DD_HHMMSS
TIMESTAMP_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{6}$")


def is_valid_timestamp(dirname: str) -> bool:
    """
    Validate that a directory name follows the timestamp format.

    Valid format: YYYY-MM-DD_HHMMSS (e.g., 2026-02-15_143022)

    Args:
        dirname: Directory name to validate

    Returns:
        True if dirname matches timestamp format, False otherwise
    """
    if not dirname:
        return False

    # Check basic pattern
    if not TIMESTAMP_PATTERN.match(dirname):
        return False

    # Additional validation: extract parts and verify they're reasonable
    try:
        year = int(dirname[0:4])
        month = int(dirname[5:7])
        day = int(dirname[8:10])
        # hour = int(dirname[11:13])
        # minute = int(dirname[13:15])
        # second = int(dirname[15:17])

        # Basic range checks
        if not (2000 <= year <= 2100):
            return False
        if not (1 <= month <= 12):
            return False
        if not (1 <= day <= 31):
            return False

        return True
    except (ValueError, IndexError):
        return False


def filter_valid_timestamp_dirs(dirs: List[Path]) -> List[Path]:
    """
    Filter directories to only those with valid timestamp names.

    Args:
        dirs: List of directory paths to filter

    Returns:
        List of directories with valid timestamp names
    """
    return [d for d in dirs if is_valid_timestamp(d.name)]


# ==============================================================================
# NEW STRUCTURE PATHS (ARCH-03) - Preferred
# ==============================================================================

DATA_RAW = Path("data/raw")
"""Path to raw immutable data (READ-ONLY)."""

DATA_INTERIM = Path("data/interim")
"""Path to intermediate processing data (CAN REGENERATE)."""

DATA_PROCESSED = Path("data/processed")
"""Path to final cleaned data (SOURCE FOR ANALYSIS)."""

DATA_EXTERNAL = Path("data/external")
"""Path to third-party reference data."""

LOGS_DIR = Path("logs")
"""Path to execution logs."""

RESULTS_DIR = Path("results")
"""Path to analysis outputs (figures, tables, reports)."""


# ==============================================================================
# LEGACY PATHS (deprecated, will be removed in v7.0)
# ==============================================================================

INPUTS_DIR = Path("inputs")
"""Legacy path to input data. Deprecated: use DATA_RAW instead."""

OUTPUTS_DIR = Path("outputs")
"""Legacy path to outputs. Deprecated: use DATA_INTERIM or DATA_PROCESSED."""

OLD_LOGS_DIR = Path("logs")
"""Legacy path to logs. Deprecated: use LOGS_DIR instead."""


class PathValidationError(Exception):
    """Raised when path validation fails."""

    pass


class OutputResolutionError(Exception):
    """Raised when output directory resolution fails."""

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


def get_latest_output_dir(
    output_base: Path, required_file: Optional[str] = None, validate_timestamp: bool = True
) -> Path:
    """
    Find the most recent timestamped output directory.

    Directories are expected to follow YYYY-MM-DD_HHMMSS naming convention.
    Sorting by name ensures chronological order without parsing timestamps.

    Args:
        output_base: Base directory containing timestamped subdirectories
        required_file: If provided, only consider directories containing this file
        validate_timestamp: If True, validate timestamp format (Phase 89-03)

    Returns:
        Path to the most recent valid timestamped directory

    Raises:
        OutputResolutionError: If no valid directory found
    """
    if not output_base.exists():
        raise OutputResolutionError(f"Output base directory not found: {output_base}")

    # Find directories starting with a digit (timestamp pattern)
    timestamped_dirs = [
        d for d in output_base.iterdir() if d.is_dir() and d.name[0].isdigit()
    ]

    if not timestamped_dirs:
        raise OutputResolutionError(
            f"No timestamped directories found in: {output_base}"
        )

    # Validate timestamp format if requested (Phase 89-03)
    if validate_timestamp:
        valid_dirs = filter_valid_timestamp_dirs(timestamped_dirs)
        if not valid_dirs:
            # Fall back to all digit-prefixed dirs if none match pattern
            warnings.warn(
                f"No directories match YYYY-MM-DD_HHMMSS format in {output_base}, "
                "using fallback matching",
                UserWarning,
            )
            valid_dirs = timestamped_dirs
        timestamped_dirs = valid_dirs

    # Sort by name descending (newest first)
    sorted_dirs = sorted(timestamped_dirs, key=lambda d: d.name, reverse=True)

    # Filter by required file if specified
    if required_file:
        for d in sorted_dirs:
            if (d / required_file).exists():
                return d
        raise OutputResolutionError(
            f"No directory contains required file '{required_file}' in: {output_base}"
        )

    return sorted_dirs[0]


# ==============================================================================
# BACKWARD COMPATIBILITY FUNCTIONS
# ==============================================================================


def resolve_data_path(path_name: str, prefer_new: bool = True) -> Path:
    """
    Resolve path to data, checking new structure first.

    Provides backward compatibility during migration by checking both
    old (inputs, outputs) and new (data/raw, data/interim, etc.)
    directory structures.

    Args:
        path_name: Name of data directory (e.g., "transcripts", "raw", "interim")
        prefer_new: If True, check new structure first (default: True)

    Returns:
        Path to the data directory

    Raises:
        FileNotFoundError: If data not found in either location

    Example:
        >>> # Get raw data directory (backward compatible)
        >>> raw_path = resolve_data_path("raw")
        >>> # Get specific data subdirectory
        >>> transcripts = resolve_data_path("transcripts")
    """
    # Map of canonical names to new paths
    new_paths = {
        "raw": DATA_RAW,
        "interim": DATA_INTERIM,
        "processed": DATA_PROCESSED,
        "external": DATA_EXTERNAL,
        "logs": LOGS_DIR,
        "results": RESULTS_DIR,
    }

    # Map of old names to new names for backward compatibility
    legacy_mapping = {
        "inputs": "raw",  # old numbered/short name
        "outputs": "interim",  # old numbered/short name
        "logs": "logs",  # old numbered/short name
    }

    # Handle canonical names directly
    if path_name in new_paths:
        return new_paths[path_name]

    # Handle legacy names with backward compatibility
    if path_name in legacy_mapping:
        canonical = legacy_mapping[path_name]
        if prefer_new:
            new_path = new_paths[canonical]
            if new_path.exists():
                return new_path
        # Fallback to old path if new doesn't exist
        return Path(path_name)

    # Generic fallback: check both locations
    new_path = DATA_RAW / path_name
    old_path = INPUTS_DIR / path_name

    if prefer_new:
        if new_path.exists():
            return new_path
        elif old_path.exists():
            return old_path
    else:
        if old_path.exists():
            return old_path
        elif new_path.exists():
            return new_path

    raise FileNotFoundError(
        f"Data '{path_name}' not found in old ({old_path}) or new ({new_path}) locations"
    )


def get_output_dir(stage: str, date: Optional[str] = None, prefer_new: bool = True) -> Path:
    """
    Get output directory for a processing stage.

    Provides backward compatibility by returning paths in either new
    (data/interim/ or data/processed/) or legacy (outputs/) structure.

    Args:
        stage: Processing stage name (e.g., "sample", "text", "financial")
        date: Optional date string for versioned output (YYYY-MM-DD format)
        prefer_new: If True, prefer new structure (default: True)

    Returns:
        Path to the output directory

    Example:
        >>> # Get interim output directory for sample stage
        >>> output_dir = get_output_dir("sample")
        >>> # Get dated output directory
        >>> dated_output = get_output_dir("sample", date="2024-01-15")
    """
    if prefer_new:
        # Use new structure: data/interim/{stage}/
        base_dir = DATA_INTERIM / stage
    else:
        # Use legacy structure: outputs/{stage}/
        base_dir = OUTPUTS_DIR / stage

    if date:
        return base_dir / date
    return base_dir


def get_results_subdir(subdir: str) -> Path:
    """
    Get path to results subdirectory (figures, tables, reports).

    Args:
        subdir: Subdirectory name ("figures", "tables", or "reports")

    Returns:
        Path to the results subdirectory

    Example:
        >>> figures_dir = get_results_subdir("figures")
        >>> tables_dir = get_results_subdir("tables")
    """
    return RESULTS_DIR / subdir


def deprecation_warning(old_name: str, new_name: str, version: str = "7.0") -> None:
    """
    Issue a deprecation warning for legacy path usage.

    Args:
        old_name: Name of deprecated path/function
        new_name: Name of replacement path/function
        version: Version when removal will occur (default: "7.0")
    """
    warnings.warn(
        f"'{old_name}' is deprecated and will be removed in v{version}. "
        f"Use '{new_name}' instead.",
        DeprecationWarning,
        stacklevel=3,
    )
