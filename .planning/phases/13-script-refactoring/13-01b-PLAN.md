---
phase: 13-script-refactoring
plan: 01b
type: execute
wave: 1
depends_on: []
files_modified:
  - 2_Scripts/shared/path_utils.py
  - 2_Scripts/shared/symlink_utils.py
  - 2_Scripts/shared/README.md
autonomous: true
user_setup: []

must_haves:
  truths:
    - "Path utilities exist with robust validation"
    - "Symlink utilities handle cross-platform linking (symlink/junction/copy)"
    - "Symlink utilities validate target directories before creating links"
    - "README.md documents all 5 modules (core + path/symlink)"
    - "All modules follow existing pattern (chunked_reader.py, data_validation.py)"
  artifacts:
    - path: "2_Scripts/shared/path_utils.py"
      provides: "Path validation and directory creation helpers"
      exports: ["validate_output_path", "ensure_output_dir", "validate_input_file", "get_available_disk_space"]
    - path: "2_Scripts/shared/symlink_utils.py"
      provides: "Symlink and junction creation helpers"
      exports: ["update_latest_link", "create_junction", "is_junction"]
      imports: ["shared.path_utils.ensure_output_dir"]
    - path: "2_Scripts/shared/README.md"
      provides: "Documentation for all shared modules"
      contains: "regression_utils|financial_utils|reporting_utils|path_utils|symlink_utils"
  key_links:
    - from: "path_utils.py"
      to: "pathlib"
      via: "Path class for path operations"
      pattern: "from pathlib import Path"
    - from: "symlink_utils.py"
      to: "path_utils.py"
      via: "ensure_output_dir() called in update_latest_link() to validate target directory"
      pattern: "from shared.path_utils import ensure_output_dir"
---

<objective>
Create shared utility modules for path validation and symlink/junction handling, and update shared/README.md to document all modules.

Purpose: Extract common path validation and symlink creation functionality from large scripts into reusable, focused modules following existing shared module patterns.
Output: 2 new shared modules (path, symlink) and updated README documenting all 5 modules.
</objective>

<execution_context>
@~/.config/opencode/get-shit-done/workflows/execute-plan.md
@~/.config/opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/13-script-refactoring/13-RESEARCH.md
@.planning/codebase/CONVENTIONS.md
@.planning/codebase/ARCHITECTURE.md

@2_Scripts/shared/chunked_reader.py
@2_Scripts/shared/data_validation.py
@2_Scripts/1_Sample/1.0_BuildSampleManifest.py
</context>

<tasks>

<task type="auto">
  <name>Create shared/path_utils.py</name>
  <files>2_Scripts/shared/path_utils.py</files>
  <action>
Create path validation utility module with these functions:

```python
#!/usr/bin/env python3
"""
Shared path utilities for validation and directory creation.
Provides robust path handling with pathlib.
"""

from pathlib import Path
from typing import Optional


class PathValidationError(Exception):
    """Raised when path validation fails."""
    pass


def validate_output_path(
    path: Path,
    must_exist: bool = False,
    must_be_writable: bool = True
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
```

Follow existing pattern:
- Contract header with id, description, inputs/outputs, deterministic: true
- Type hints for all function signatures
- Docstrings with Args, Returns, Raises sections
- Pathlib for path operations (Python 3.4+ standard)
  </action>
  <verify>python -c "from shared.path_utils import validate_output_path, ensure_output_dir, validate_input_file, get_available_disk_space; print('Import successful')"</verify>
  <done>All 4 functions defined with proper signatures and docstrings</done>
</task>

<task type="auto">
  <name>Create shared/symlink_utils.py</name>
  <files>2_Scripts/shared/symlink_utils.py</files>
  <action>
Create symlink/junction handling utility module with these functions:

```python
#!/usr/bin/env python3
"""
Shared symlink utilities for cross-platform link creation.
Handles symlinks (Unix) and junctions (Windows).
"""

import sys
import warnings
from pathlib import Path
from shared.path_utils import ensure_output_dir


class SymlinkError(Exception):
    """Raised when symlink/junction creation fails."""
    pass


def update_latest_link(
    target_dir: Path,
    link_path: Path,
    verbose: bool = True
) -> None:
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
        if sys.platform != 'win32':
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
                    warnings.warn(f"Copied outputs to 'latest' (link creation unavailable)")
            except OSError as ce:
                raise SymlinkError(f"Failed to copy directory {target_dir} to {link_path}: {ce}")


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
    if sys.platform != 'win32':
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
    if hasattr(path, 'is_junction'):
        return path.is_junction()

    # Fallback for Python <3.12
    if sys.platform == 'win32' and path.is_dir():
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
            None
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
                None
            )
            if success:
                tag = ctypes.c_ulong.from_buffer(reparse_data_buffer).value
                return tag == IO_REPARSE_TAG_MOUNT_POINT
            return False
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)

    return False
```

Follow existing pattern:
- Contract header with id, description, inputs/outputs, deterministic: true
- Type hints for all function signatures
- Docstrings with Args, Returns, Raises, Note sections
- Cross-platform support (Unix + Windows)
  </action>
  <verify>python -c "from shared.symlink_utils import update_latest_link, create_junction, is_junction; print('Import successful')"</verify>
  <done>All 3 functions defined with proper signatures and docstrings</done>
</task>

<task type="auto">
  <name>Update shared/README.md</name>
  <files>2_Scripts/shared/README.md</files>
  <action>
Update shared/README.md to document all 5 modules (core + path/symlink):

Read existing README.md and add sections for:
- regression_utils.py - Fixed effects OLS regression helpers
- financial_utils.py - Financial feature calculation helpers
- reporting_utils.py - Regression report generation helpers
- path_utils.py - Path validation and directory creation helpers
- symlink_utils.py - Symlink and junction creation helpers

For each module:
- Purpose (what it does)
- Key functions (list exported functions)
- Usage example (simple code snippet)
- Dependencies (external libraries if any)

Follow existing documentation style in README.md.
  </action>
  <verify>grep -q "regression_utils" 2_Scripts/shared/README.md && grep -q "financial_utils" 2_Scripts/shared/README.md && grep -q "reporting_utils" 2_Scripts/shared/README.md && grep -q "path_utils" 2_Scripts/shared/README.md && grep -q "symlink_utils" 2_Scripts/shared/README.md && echo "All modules documented"</verify>
  <done>README.md updated with documentation for all 5 modules</done>
</task>

</tasks>

<verification>
After completing all tasks, verify:

1. Both path/symlink modules exist in 2_Scripts/shared/
2. Each module can be imported without errors
3. shared/README.md documents all 5 modules
4. No syntax errors in any module

Run:
```bash
python -c "
import sys
sys.path.insert(0, '2_Scripts')

from shared.path_utils import validate_output_path
from shared.symlink_utils import update_latest_link

print('All modules imported successfully')
"
```
</verification>

<success_criteria>
1. 2 new shared modules created with complete function implementations
2. All modules follow existing pattern (contract headers, docstrings, type hints)
3. shared/README.md updated with module documentation for all 5 modules
4. All modules importable without errors
5. Functions are documented with Args, Returns, Raises sections
</success_criteria>

<output>
After completion, create `.planning/phases/13-script-refactoring/13-01b-SUMMARY.md`
</output>
