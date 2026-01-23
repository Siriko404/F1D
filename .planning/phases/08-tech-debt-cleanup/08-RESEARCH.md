# Phase 8: Tech Debt Cleanup - Research

**Researched:** 2026-01-23
**Domain:** Python code refactoring, shared modules, error handling patterns
**Confidence:** HIGH

## Summary

This phase addresses three categories of technical debt in the data processing pipeline:

1. **DualWriter class duplication** - The DualWriter logging class is duplicated in 16+ scripts across 1_Sample/, 2_Text/, 3_Financial/, and 4_Econometric/ directories. Each copy is identical, creating a maintenance burden where bug fixes must be applied in multiple locations.

2. **Utility function duplication** - Helper functions (compute_file_checksum, print_stat, analyze_missing_values, update_latest_symlink) are duplicated across multiple scripts. Some utilities already exist in 1.5_Utils.py and 3.4_Utils.py, but are not consistently imported.

3. **Inconsistent error handling** - While Phase 7 improved error handling in some files, bare `except:` and `except Exception:` blocks with `pass` statements still exist in econometric scripts, making debugging difficult.

**Primary recommendation:** Create a shared utilities module structure at `2_Scripts/shared/` that all scripts can import from, using Python's standard import mechanism to preserve self-contained script execution while eliminating code duplication.

## Standard Stack

This phase uses Python's standard library and import system - no third-party packages required.

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| sys | Built-in | Exit codes, path manipulation for imports | Standard process control and import path management |
| importlib | Built-in | Programmatic imports (optional approach) | For dynamic module loading if needed |
| pathlib | Built-in | Path operations (already used) | Cross-platform filesystem paths |
| hashlib | Built-in | Checksum computation (already used) | Cryptographic hash functions |

### No Additional Dependencies Needed
For this refactoring phase, use Python's built-in module system exclusively. Do not introduce third-party utility libraries.

**Installation:**
```bash
# No pip install required - using standard library only
```

## Architecture Patterns

### Recommended Project Structure
```
2_Scripts/
├── 1_Sample/
│   ├── 1.0_BuildSampleManifest.py
│   ├── 1.1_CleanMetadata.py
│   ├── 1.2_LinkEntities.py
│   ├── 1.3_BuildTenureMap.py
│   ├── 1.4_AssembleManifest.py
│   └── 1.5_Utils.py            # Will consolidate to shared/
├── 2_Text/
│   ├── 2.1_TokenizeAndCount.py
│   ├── 2.2_ConstructVariables.py
│   └── 2.3_VerifyStep2.py
├── 3_Financial/
│   ├── 3.0_BuildFinancialFeatures.py
│   ├── 3.1_FirmControls.py
│   ├── 3.2_MarketVariables.py
│   ├── 3.3_EventFlags.py
│   └── 3.4_Utils.py            # Will consolidate to shared/
├── 4_Econometric/
│   ├── 4.1_EstimateCeoClarity.py
│   ├── 4.1.1_EstimateCeoClarity_CeoSpecific.py
│   ├── 4.1.2_EstimateCeoClarity_Extended.py
│   ├── 4.1.3_EstimateCeoClarity_Regime.py
│   ├── 4.1.4_EstimateCeoTone.py
│   ├── 4.2_LiquidityRegressions.py
│   ├── 4.3_TakeoverHazards.py
│   └── 4.4_GenerateSummaryStats.py
├── shared/                       # NEW: Shared utilities module
│   ├── __init__.py               # Package marker (can be empty)
│   ├── dual_writer.py            # DualWriter class
│   ├── pipeline_utils.py          # Utility functions
│   └── error_handling.py         # Optional: Reusable error handlers
└── 2.99_ValidateStats.py
```

### Pattern 1: Shared Module with Self-Contained Scripts

**What:** Create a shared utilities package that scripts can import from, while preserving the ability to run any script directly (e.g., `python 2_Scripts/1_Sample/1.0_BuildSampleManifest.py`).

**When to use:** For all Python scripts in 2_Scripts/ and subdirectories.

**Why this works:** Python automatically adds the script's directory to `sys.path` when a script is executed. This means scripts in subdirectories (1_Sample/, 2_Text/, etc.) can import from parent directories without additional configuration.

**Example:**

```python
# Source: https://docs.python.org/3/tutorial/modules.html
# Source: https://docs.python.org/3/library/sys_path_init.html

# In 2_Scripts/shared/dual_writer.py
import sys

class DualWriter:
    """Writes to both stdout and log file verbatim"""
    def __init__(self, log_path):
        self.terminal = sys.stdout
        self.log = open(log_path, 'w', encoding='utf-8')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def close(self):
        self.log.close()

def print_dual(msg):
    """Print to both terminal and log"""
    print(msg, flush=True)
```

```python
# In 2_Scripts/1_Sample/1.0_BuildSampleManifest.py
# AFTER refactoring - remove local DualWriter class

import sys
from pathlib import Path

# Import from shared module (works when script is run directly)
# Python adds 2_Scripts to sys.path automatically
from shared.dual_writer import DualWriter, print_dual

# OR (alternative approach with explicit path manipulation):
import sys
from pathlib import Path
script_dir = Path(__file__).parent
shared_dir = script_dir / ".."
sys.path.insert(0, str(shared_dir))
from dual_writer import DualWriter, print_dual
```

### Pattern 2: Consolidated Utility Functions

**What:** Move duplicated utility functions to `2_Scripts/shared/pipeline_utils.py` and import from there.

**When to use:** For utility functions duplicated across multiple scripts.

**Example:**

```python
# Source: https://docs.python.org/3/tutorial/modules.html
# Source: Current codebase analysis

# In 2_Scripts/shared/pipeline_utils.py
import hashlib
import shutil
import os
import sys
from pathlib import Path

def compute_file_checksum(filepath, algorithm="sha256"):
    """Compute checksum for a file."""
    h = hashlib.new(algorithm)
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def print_stat(label, before=None, after=None, value=None, indent=2):
    """Print a statistic with consistent formatting.

    Modes:
        - Delta mode (before/after): "  Label: 1,000 -> 800 (-20.0%)"
        - Value mode: "  Label: 1,000"
    """
    prefix = " " * indent
    if before is not None and after is not None:
        delta = after - before
        pct = (delta / before) * 100 if before != 0 else 0
        direction = "+" if delta > 0 else ""
        print(f"{prefix}{label}: {before:,} -> {after:,} ({direction}{pct:.1f}%)")
    elif value is not None:
        print(f"{prefix}{label}: {value:,}")


def analyze_missing_values(df):
    """Analyze missing values per column."""
    missing = {}
    for col in df.columns:
        null_count = df[col].isna().sum()
        if null_count > 0:
            missing[col] = {
                "count": int(null_count),
                "percent": round(null_count / len(df) * 100, 2),
            }
    return missing


def update_latest_symlink(latest_dir, output_dir, print_fn=print):
    """
    Update 'latest' to point to the output directory.
    Raises SystemExit on failure with non-zero exit code.

    Args:
        latest_dir: Path to the 'latest' symlink/directory
        output_dir: Path to the output directory to link/copy
        print_fn: Print function for logging (default: print)

    Raises:
        SystemExit: With exit code 1 on critical failure
    """
    # Remove existing latest (whether symlink, junction, or directory)
    if latest_dir.exists() or latest_dir.is_symlink():
        try:
            if latest_dir.is_symlink():
                os.unlink(str(latest_dir))
            else:
                shutil.rmtree(str(latest_dir))
        except PermissionError as e:
            print_fn(f"ERROR: Permission denied removing old 'latest': {e}")
            print_fn(f"  Path: {latest_dir}")
            sys.exit(1)
        except FileNotFoundError:
            pass  # Not an error - doesn't exist yet
        except OSError as e:
            print_fn(f"ERROR: Failed to remove old 'latest': {e}")
            print_fn(f"  Path: {latest_dir}")
            sys.exit(1)

    # Try symlink first (preferred)
    try:
        os.symlink(str(output_dir), str(latest_dir), target_is_directory=True)
        print_fn(f"\nUpdated 'latest' -> {output_dir.name}")
    except PermissionError as e:
        # Symlink failed (likely no admin rights on Windows)
        # Fall back to copytree
        print_fn(f"WARNING: Symlink creation failed (permission denied)")
        print_fn(f"  Falling back to directory copy...")
        try:
            shutil.copytree(str(output_dir), str(latest_dir))
            print_fn(f"\nCopied outputs to 'latest' (symlink not available)")
        except OSError as e2:
            print_fn(f"ERROR: Symlink and copytree both failed: {e2}")
            print_fn(f"  Symlink error: {e}")
            print_fn(f"  Output dir: {output_dir}")
            print_fn(f"  Latest dir: {latest_dir}")
            sys.exit(1)
    except OSError as e:
        # Other OSError (e.g., source doesn't exist)
        print_fn(f"ERROR: Symlink creation failed: {e}")
        print_fn(f"  Output dir: {output_dir}")
        print_fn(f"  Latest dir: {latest_dir}")
        sys.exit(1)
```

```python
# In 2_Scripts/1_Sample/1.1_CleanMetadata.py
# AFTER refactoring - remove local utility functions

from pathlib import Path
import pandas as pd

# Import from shared module
from shared.pipeline_utils import (
    compute_file_checksum,
    print_stat,
    analyze_missing_values,
    update_latest_symlink,
)
```

### Pattern 3: Error Handling Standardization (Following Phase 7)

**What:** Apply the error handling patterns established in Phase 7 to all scripts, eliminating bare `except:` and `except Exception:` with `pass`.

**When to use:** For all scripts, especially econometric scripts that still have bare except blocks.

**Example:**

```python
# Source: Phase 7 research (07-RESEARCH.md)
# Source: https://docs.python.org/3/library/exceptions.html
# Source: https://docs.python.org/3/tutorial/errors.html

# BEFORE (bad pattern from current code):
try:
    risky_operation()
except:
    pass  # Silent failure - bad!


# AFTER (correct pattern):
import sys

try:
    risky_operation()
except FileNotFoundError as e:
    print(f"ERROR: File not found: {e}", file=sys.stderr)
    sys.exit(1)
except PermissionError as e:
    print(f"ERROR: Permission denied: {e}", file=sys.stderr)
    sys.exit(1)
except OSError as e:
    print(f"ERROR: OS error: {e}", file=sys.stderr)
    sys.exit(1)
```

### Anti-Patterns to Avoid

- **Breaking self-contained script execution:** Don't make scripts require being run from a specific directory or with specific environment variables. The shared module approach preserves direct script execution.

- **Introducing package dependencies:** Don't add `setup.py` or `requirements.txt` for this refactoring. Use only Python standard library.

- **Modifying sys.path in multiple places:** Don't add sys.path manipulation in every script. If needed, do it once in the shared module's `__init__.py` or use relative imports consistently.

- **Large refactors in single commits:** Don't change all 16+ scripts in one commit. Group by directory or function type to enable incremental testing.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Shared module discovery | Custom path manipulation logic | Python's automatic sys.path handling | When script is run, its directory is added to sys.path automatically |
| Dual-writer logging | Custom logging class | Keep DualWriter but extract to shared | Simple, well-tested, already works - just consolidate |
| Cross-platform symlinks | Custom symlink detection | `os.symlink()` + `shutil.copytree()` fallback (Phase 7 pattern) | Handles Windows junctions and Unix symlinks correctly |
| Error context | String concatenation | `print(..., file=sys.stderr)` with specific exceptions | Standard library provides stderr, exception hierarchy |
| Module imports | Dynamic imports everywhere | Standard import statements at module top | Clearer, easier to debug, works automatically with sys.path |

**Key insight:** Python's standard library has well-tested solutions for module imports, logging to multiple destinations, and cross-platform filesystem operations. Custom solutions are worse because they hide the actual behavior, make debugging harder, and don't follow Python conventions.

## Common Pitfalls

### Pitfall 1: Import Path Issues When Running Scripts Directly

**What goes wrong:** Scripts fail to import from shared modules when run directly (e.g., `python 2_Scripts/1_Sample/1.0_BuildSampleManifest.py`) because sys.path doesn't include the parent directory.

**Why it happens:** Python only adds the script's immediate directory to sys.path, not parent directories. When running `2_Scripts/1_Sample/script.py`, sys.path includes `2_Scripts/1_Sample/` but not `2_Scripts/`.

**How to avoid:** Use one of these approaches:

1. **Add parent directory to sys.path in each script (simple but repetitive):**
   ```python
   import sys
   from pathlib import Path
   script_dir = Path(__file__).parent.parent  # Go up to 2_Scripts/
   sys.path.insert(0, str(script_dir))
   from shared.dual_writer import DualWriter
   ```

2. **Or use relative import from parent directory (requires package structure):**
   ```python
   # Requires 2_Scripts/__init__.py and 2_Scripts/shared/__init__.py
   from ..shared.dual_writer import DualWriter
   ```

3. **Or modify sys.path once in shared module's __init__.py (cleanest):**
   ```python
   # In 2_Scripts/shared/__init__.py
   import sys
   from pathlib import Path
   shared_dir = Path(__file__).parent
   if str(shared_dir) not in sys.path:
       sys.path.insert(0, str(shared_dir))
   ```

**Warning signs:** Scripts run fine from one directory but fail when run from another; ImportError when running scripts directly.

### Pitfall 2: Inconsistent DualWriter Implementations

**What goes wrong:** Different scripts have slight variations in DualWriter (e.g., encoding parameter, flush frequency) making behavior inconsistent.

**Why it happens:** Copy-paste without standardization, or independent implementations by different developers.

**How to avoid:** Extract ONE canonical implementation to `2_Scripts/shared/dual_writer.py` and ensure all scripts import from there. The extracted class should match the most common, most recent implementation.

**Warning signs:** Same function name behaves differently in different scripts; bug fixes in one script don't apply to others.

### Pitfall 3: Breaking Existing Imports During Migration

**What goes wrong:** Removing `1.5_Utils.py` or `3.4_Utils.py` breaks scripts that import from them, especially scripts that use dynamic imports.

**Why it happens:** Not checking all import statements before removing the old utility files.

**How to avoid:** Audit all imports before removal. The migration should:
1. Create shared module first
2. Add imports to shared module
3. Update all scripts to import from shared
4. Only then, remove or deprecate old utility files

**Warning signs:** ImportError after migration; scripts fail that previously worked.

### Pitfall 4: Overly Broad Error Handling Replacements

**What goes wrong:** Replacing all bare `except:` blocks with `except Exception as e: print(e)` is still too broad and can hide bugs.

**Why it happens:** Automated replacements or quick fixes that don't analyze the specific error type needed.

**How to avoid:** Follow Phase 7's pattern:
- Catch specific exceptions (FileNotFoundError, PermissionError, OSError, ValueError)
- For filesystem operations: catch OSError and its subclasses
- Always log error context (what operation, what file, what parameters)
- Exit with non-zero code for critical failures
- Re-raise if error should be handled by caller

**Warning signs:** Generic error messages that don't help debugging; scripts that continue when they should fail.

## Code Examples

Verified patterns from official sources:

### Dual Writer Consolidation

```python
# Source: Current codebase (multiple scripts), Phase 7 RESEARCH.md
# Location: 2_Scripts/shared/dual_writer.py

import sys

class DualWriter:
    """
    Writes to both stdout and log file verbatim.
    This class is duplicated in 16+ scripts - consolidate here.
    """
    def __init__(self, log_path):
        self.terminal = sys.stdout
        self.log = open(log_path, 'w', encoding='utf-8')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def close(self):
        self.log.close()

def print_dual(msg):
    """Print to both terminal and log"""
    print(msg, flush=True)
```

### Utility Function Consolidation

```python
# Source: Current codebase (1.5_Utils.py, 3.4_Utils.py), multiple scripts
# Location: 2_Scripts/shared/pipeline_utils.py

import hashlib
import shutil
import os
import sys
from pathlib import Path
from typing import Dict, Any
import pandas as pd


def compute_file_checksum(filepath: Path, algorithm: str = "sha256") -> str:
    """Compute checksum for a file."""
    h = hashlib.new(algorithm)
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def print_stat(
    label: str,
    before: Any = None,
    after: Any = None,
    value: Any = None,
    indent: int = 2,
) -> None:
    """Print a statistic with consistent formatting."""
    prefix = " " * indent
    if before is not None and after is not None:
        delta = after - before
        pct = (delta / before) * 100 if before != 0 else 0
        direction = "+" if delta > 0 else ""
        print(f"{prefix}{label}: {before:,} -> {after:,} ({direction}{pct:.1f}%)")
    elif value is not None:
        print(f"{prefix}{label}: {value:,}")


def analyze_missing_values(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """Analyze missing values per column."""
    missing = {}
    for col in df.columns:
        null_count = df[col].isna().sum()
        if null_count > 0:
            missing[col] = {
                "count": int(null_count),
                "percent": round(null_count / len(df) * 100, 2),
            }
    return missing


def update_latest_symlink(
    latest_dir: Path,
    output_dir: Path,
    print_fn = print,
) -> None:
    """
    Update 'latest' to point to the output directory.
    Pattern from Phase 7 RESEARCH.md.

    Raises:
        SystemExit: With exit code 1 on critical failure
    """
    # Remove existing latest (whether symlink, junction, or directory)
    if latest_dir.exists() or latest_dir.is_symlink():
        try:
            if latest_dir.is_symlink():
                os.unlink(str(latest_dir))
            else:
                shutil.rmtree(str(latest_dir))
        except PermissionError as e:
            print_fn(f"ERROR: Permission denied removing old 'latest': {e}")
            print_fn(f"  Path: {latest_dir}")
            sys.exit(1)
        except FileNotFoundError:
            pass  # Not an error - doesn't exist yet
        except OSError as e:
            print_fn(f"ERROR: Failed to remove old 'latest': {e}")
            print_fn(f"  Path: {latest_dir}")
            sys.exit(1)

    # Try symlink first (preferred)
    try:
        os.symlink(str(output_dir), str(latest_dir), target_is_directory=True)
        print_fn(f"\nUpdated 'latest' -> {output_dir.name}")
    except PermissionError as e:
        # Symlink failed (likely no admin rights on Windows)
        # Fall back to copytree
        print_fn(f"WARNING: Symlink creation failed (permission denied)")
        print_fn(f"  Falling back to directory copy...")
        try:
            shutil.copytree(str(output_dir), str(latest_dir))
            print_fn(f"\nCopied outputs to 'latest' (symlink not available)")
        except OSError as e2:
            print_fn(f"ERROR: Symlink and copytree both failed: {e2}")
            print_fn(f"  Symlink error: {e}")
            print_fn(f"  Output dir: {output_dir}")
            print_fn(f"  Latest dir: {latest_dir}")
            sys.exit(1)
    except OSError as e:
        # Other OSError (e.g., source doesn't exist)
        print_fn(f"ERROR: Symlink creation failed: {e}")
        print_fn(f"  Output dir: {output_dir}")
        print_fn(f"  Latest dir: {latest_dir}")
        sys.exit(1)
```

### Error Handling Replacement (Following Phase 7)

```python
# Source: Phase 7 RESEARCH.md
# Source: https://docs.python.org/3/tutorial/errors.html

import sys
from pathlib import Path

# BEFORE (bare except - BAD):
def load_data_bad(filepath):
    try:
        data = pd.read_csv(filepath)
    except:
        pass  # Silent failure!

# AFTER (specific exceptions - GOOD):
def load_data_good(filepath: Path) -> pd.DataFrame:
    """
    Load data with proper error handling.
    Phase 7 pattern.
    """
    try:
        data = pd.read_csv(filepath)
    except FileNotFoundError as e:
        print(f"ERROR: File not found: {e}", file=sys.stderr)
        print(f"  Path: {filepath}", file=sys.stderr)
        sys.exit(1)
    except PermissionError as e:
        print(f"ERROR: Permission denied: {e}", file=sys.stderr)
        print(f"  Path: {filepath}", file=sys.stderr)
        sys.exit(1)
    except pd.errors.EmptyDataError as e:
        print(f"ERROR: File is empty: {e}", file=sys.stderr)
        print(f"  Path: {filepath}", file=sys.stderr)
        sys.exit(1)
    except pd.errors.ParserError as e:
        print(f"ERROR: CSV parsing failed: {e}", file=sys.stderr)
        print(f"  Path: {filepath}", file=sys.stderr)
        sys.exit(1)

    return data
```

### Import Path Setup

```python
# Source: https://docs.python.org/3/library/sys_path_init.html
# Location: 2_Scripts/shared/__init__.py

import sys
from pathlib import Path

# Add 2_Scripts directory to sys.path if not already present
# This enables imports like `from shared.dual_writer import DualWriter`
# when scripts in subdirectories are run directly
shared_dir = Path(__file__).parent
if str(shared_dir) not in sys.path:
    sys.path.insert(0, str(shared_dir))
```

```python
# Location: Any script in subdirectories (e.g., 2_Scripts/1_Sample/1.0_BuildSampleManifest.py)

# Import shared module (works because shared/__init__.py added 2_Scripts to sys.path)
from shared.dual_writer import DualWriter, print_dual
from shared.pipeline_utils import update_latest_symlink
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Inline DualWriter in each script | Shared module at 2_Scripts/shared/dual_writer.py | Phase 8 | Single source of truth, easier maintenance |
| Duplicated utility functions | Consolidated in 2_Scripts/shared/pipeline_utils.py | Phase 8 | Bug fixes apply everywhere, consistent behavior |
| Bare except: blocks with pass | Specific exception types with logging | Phase 7 | Errors no longer hidden, easier debugging |
| Silent symlink failures | Explicit error logging and exit | Phase 7 | Data integrity protected, users know when operations fail |
| Manual path manipulation | Automatic sys.path + shared/__init__.py | Phase 8 | Scripts work when run from any directory |

**Deprecated/outdated:**
- Inline DualWriter class in individual scripts - Extract to shared module
- Local utility functions that are duplicated - Consolidate to shared/pipeline_utils.py
- Bare `except:` and `except Exception:` with `pass` - Use specific exceptions (Phase 7 pattern)
- Scripts that only work when run from specific directory - Fix import paths to work from anywhere

## Open Questions

1. **Should old utility files (1.5_Utils.py, 3.4_Utils.py) be removed or deprecated?**
   - What we know: They contain some unique functions (generate_variable_reference, get_latest_output_dir, load_master_variable_definitions) that may be script-specific
   - What's unclear: Whether these functions should also be moved to shared/ or if they should stay local
   - Recommendation: Audit the unique functions. If they're genuinely script-specific, keep them. If they're generally useful, move to shared/ too. Create deprecation notice if removing.

2. **What's the best approach for sys.path manipulation?**
   - What we know: Scripts need to import from 2_Scripts/shared/ when run from subdirectories
   - What's unclear: Whether to add sys.path manipulation in each script, in shared/__init__.py, or use relative imports
   - Recommendation: Use shared/__init__.py approach as it's cleanest and requires no changes to each script. Test thoroughly that it works when scripts are run from various directories.

3. **How to handle the migration incrementally to avoid breaking all scripts at once?**
   - What we know: 16+ scripts need updates, plus econometric scripts need error handling fixes
   - What's unclear: Optimal grouping of changes to enable testing between commits
   - Recommendation: Migrate by directory (1_Sample/, then 2_Text/, then 3_Financial/, then 4_Econometric/). Within each directory: create shared module imports first, test, then remove old duplicate code. Separate error handling into its own pass through econometric scripts.

## Sources

### Primary (HIGH confidence)
- https://docs.python.org/3/tutorial/modules.html - Python module system, imports, packages
- https://docs.python.org/3/library/sys_path_init.html - Initialization of sys.path, how Python finds modules
- https://docs.python.org/3/library/importlib.html - Programmatic imports (for reference)
- https://docs.python.org/3/library/exceptions.html - Exception hierarchy, specific exception types
- https://docs.python.org/3/tutorial/errors.html - Exception handling best practices
- Phase 7 RESEARCH.md (.planning/phases/07-critical-bug-fixes/07-RESEARCH.md) - Error handling patterns already established

### Secondary (MEDIUM confidence)
- Current codebase analysis - Identified 16+ files with DualWriter duplication, utility function patterns, error handling issues
- 1.5_Utils.py and 3.4_Utils.py - Existing utility implementations to consolidate

### Tertiary (LOW confidence)
- https://realpython.com/python-refactoring/ - General refactoring principles (verified with Python docs)
- None - All critical patterns from official Python documentation

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All from official Python documentation
- Architecture: HIGH - Based on Python's module system tutorial and sys.path initialization
- Pitfalls: HIGH - Documented in current codebase analysis and Phase 7 research

**Research date:** 2026-01-23
**Valid until:** 60 days (Python's standard library is stable, these patterns are fundamental and don't change)
