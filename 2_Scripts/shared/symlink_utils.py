#!/usr/bin/env python3
"""
================================================================================
SHARED MODULE: Symlink Utilities
================================================================================
ID: shared/symlink_utils
Description: Provides cross-platform symlink and junction creation helpers.
             Handles symlinks on Unix and junctions on Windows, with fallback
             to copy if link creation fails.

Inputs:
    - Target directory path (pathlib.Path)
    - Link path (pathlib.Path) for symlink/junction location
    - Verbose flag for logging

Outputs:
    - Created symlinks (Unix) or junctions (Windows)
    - Copies as fallback if link creation unavailable

Deterministic: true
================================================================================
"""

import sys
import warnings
from pathlib import Path
from shared.path_utils import ensure_output_dir


class SymlinkError(Exception):
    """Raised when symlink/junction creation fails."""

    pass


def update_latest_link(target_dir: Path, link_path: Path, verbose: bool = True) -> None:
    """
    Update 'latest' link using symlink or junction.

    On Unix: uses symlink
    On Windows: tries symlink first, falls back to junction, then copy

    Args:
        target_dir: Directory to link to
        link_path: Path where link should be created (e.g., 'latest')
        verbose: If True, log warnings and status

    Raises:
        SymlinkError: If all fallback methods fail

    Note:
        Windows symlinks require admin privileges.
        Junctions work without admin but only for directories.
        Copy is final fallback (uses more disk space).
    """
    target_dir = target_dir.resolve()
    link_path = link_path.resolve()

    # Ensure target directory exists
    ensure_output_dir(target_dir)

    # Remove existing link if present
    if link_path.exists() or link_path.is_symlink():
        try:
            link_path.unlink()
        except OSError as e:
            if verbose:
                warnings.warn(f"Failed to remove existing link {link_path}: {e}")
            try:
                if link_path.is_dir():
                    import shutil

                    shutil.rmtree(link_path)
                else:
                    link_path.unlink()
            except OSError as e2:
                raise SymlinkError(f"Failed to remove {link_path}: {e2}")

    # Try symlink first (works on Unix and some Windows configurations)
    try:
        link_path.symlink_to(target_dir, target_is_directory=True)
        if verbose:
            print(f"Created symlink: {link_path} -> {target_dir.name}")
        return
    except OSError as e:
        if sys.platform != "win32":
            # On non-Windows, this is a real error
            raise SymlinkError(f"Symlink creation failed: {e}")

        # On Windows, fall back to junction
        if verbose:
            warnings.warn(f"Symlink creation failed ({e}), trying junction...")

        # Try junction (Windows-specific directory link, no admin required)
        try:
            create_junction(target_dir, link_path)
            if verbose:
                warnings.warn(f"Created junction instead of symlink for {link_path}")
            return
        except OSError as je:
            if verbose:
                warnings.warn(f"Junction creation failed ({je}), copying directory...")

            # Final fallback: copy and warn
            try:
                import shutil

                shutil.copytree(str(target_dir), str(link_path), dirs_exist_ok=True)
                if verbose:
                    warnings.warn(
                        f"Copied outputs to 'latest' (link creation unavailable)"
                    )
            except OSError as ce:
                raise SymlinkError(
                    f"Failed to copy directory {target_dir} to {link_path}: {ce}"
                )


def create_junction(target: Path, link_path: Path) -> None:
    """
    Create a Windows junction (directory link).

    Args:
        target: Directory to link to
        link_path: Path where junction should be created

    Raises:
        OSError: If junction creation fails
        NotImplementedError: If not on Windows
    """
    if sys.platform != "win32":
        raise NotImplementedError("Junctions are Windows-only")

    import os

    # os.symlink with target_is_directory=False creates junction on Windows
    os.symlink(str(target), str(link_path), target_is_directory=False)


def is_junction(path: Path) -> bool:
    """
    Check if path is a Windows junction.

    Args:
        path: Path to check

    Returns:
        True if path is a junction, False otherwise

    Note:
        Path.is_junction() is available in Python 3.12+.
        This function provides fallback for older versions.
    """
    if hasattr(path, "is_junction"):
        return path.is_junction()

    # Fallback for Python <3.12
    if sys.platform == "win32" and path.is_dir():
        import os
        import ctypes

        # Get file attributes
        FILE_ATTRIBUTE_REPARSE_POINT = 0x400
        IO_REPARSE_TAG_MOUNT_POINT = 0xA0000003

        attrs = ctypes.windll.kernel32.GetFileAttributesW(str(path))
        if attrs == 0xFFFFFFFF:
            return False

        if not (attrs & FILE_ATTRIBUTE_REPARSE_POINT):
            return False

        # Check if it's a mount point (junction)
        handle = ctypes.windll.kernel32.CreateFileW(
            str(path),
            0,
            0,
            None,
            3,  # OPEN_EXISTING
            0x02000000,  # FILE_FLAG_BACKUP_SEMANTICS
            None,
        )

        if handle == -1:
            return False

        try:
            reparse_data_buffer = ctypes.create_string_buffer(16)
            bytes_returned = ctypes.c_ulong()
            success = ctypes.windll.kernelapi.DeviceIoControl(
                handle,
                0x900A4,  # FSCTL_GET_REPARSE_POINT
                None,
                0,
                reparse_data_buffer,
                16,
                ctypes.byref(bytes_returned),
                None,
            )
            if success:
                tag = ctypes.c_ulong.from_buffer(reparse_data_buffer).value
                return tag == IO_REPARSE_TAG_MOUNT_POINT
            return False
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)

    return False
