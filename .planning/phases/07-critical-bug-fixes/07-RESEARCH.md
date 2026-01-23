# Phase 7: Critical Bug Fixes - Research

**Researched:** 2026-01-23
**Domain:** Python error handling and optional dependencies
**Confidence:** HIGH

## Summary

This phase addresses two critical bugs that compromise data integrity and user experience:

1. **Silent symlink/copy failures** - The `update_latest_symlink()` function in three utility files (1.5_Utils.py, 2.2_ConstructVariables.py, 3.4_Utils.py) uses broad exception catching (`except Exception: pass`) that silently ignores failures. This means the 'latest' directory may not be updated, causing users to unknowingly reference stale outputs. On Windows, symlink creation requires administrator privileges and fails silently without admin rights.

2. **Optional dependency (rapidfuzz) not handled gracefully** - The fuzzy matching functionality in Step 1.2 (LinkEntities) silently degrades when `rapidfuzz` is unavailable. While a warning is printed, it lacks context about impact and installation instructions.

**Primary recommendation:** Fix silent failures with explicit error logging and non-zero exit codes for critical operations; enhance optional dependency warnings with clear instructions and impact documentation.

## Standard Stack

This phase uses Python's standard library only - no additional packages required.

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| os | Built-in | Filesystem operations, symlink creation | Cross-platform filesystem operations |
| shutil | Built-in | Directory copying (symlink fallback) | High-level file operations |
| sys | Built-in | Exit codes, standard streams | Process control for proper error handling |
| logging | Built-in | Structured error logging | Better than print() for warnings |

### No Alternatives Needed
For this phase, use Python's built-in exception handling and logging capabilities. Do not introduce third-party error handling libraries - standard patterns are sufficient.

## Architecture Patterns

### Pattern 1: Explicit Exception Handling with Exit Codes

**What:** Catch specific exception types, log detailed error messages, exit with non-zero code on critical failures.

**When to use:** For all critical filesystem operations, especially symlinks and directory updates.

**Example:**
```python
# Source: https://docs.python.org/3/library/os.html
# https://docs.python.org/3/tutorial/errors.html

import os
import shutil
import sys

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
            # Not an error - doesn't exist yet
            pass
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

### Pattern 2: Optional Dependency with Rich Warnings

**What:** Import optional dependencies with try/except, but provide rich warnings with installation instructions and impact documentation.

**When to use:** When functionality has optional enhancements that degrade gracefully.

**Example:**
```python
# Source: https://docs.python.org/3/tutorial/errors.html

import sys

# Try optional dependency
try:
    from rapidfuzz import fuzz, process
    FUZZY_AVAILABLE = True
    FUZZY_VERSION = "unknown"  # Could check with __version__
except ImportError:
    FUZZY_AVAILABLE = False
    FUZZY_VERSION = None

def warn_if_fuzzy_missing():
    """Log warning if fuzzy matching is unavailable."""
    if not FUZZY_AVAILABLE:
        print("\n" + "=" * 60, file=sys.stderr)
        print("WARNING: Optional dependency 'rapidfuzz' not installed", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        print("\nImpact on results:", file=sys.stderr)
        print("  - Tier 3 (fuzzy name matching) will be SKIPPED", file=sys.stderr)
        print("  - Lower entity matching rates expected", file=sys.stderr)
        print("  - Companies matched via PERMNO/CUSIP are unaffected", file=sys.stderr)
        print("\nInstallation:", file=sys.stderr)
        print("  pip install rapidfuzz", file=sys.stderr)
        print("\nNote: Fuzzy matching is optional. The script will continue", file=sys.stderr)
        print("      without it, using only exact matches (Tiers 1 & 2).", file=sys.stderr)
        print("=" * 60 + "\n", file=sys.stderr)

# Call at script startup
warn_if_fuzzy_missing()
```

### Pattern 3: Exception Enrichment with Notes (Python 3.11+)

**What:** Use `add_note()` to attach context to exceptions (Python 3.11+ feature per PEP 678).

**When to use:** When re-raising exceptions with additional context.

**Example:**
```python
# Source: https://peps.python.org/pep-0678/

import sys

def create_symlink_safely(target, link_name):
    """
    Create symlink with rich error context.

    Args:
        target: Path to symlink target
        link_name: Path to symlink location

    Raises:
        OSError: With added context notes
    """
    try:
        os.symlink(str(target), str(link_name), target_is_directory=True)
    except PermissionError as e:
        e.add_note(f"User lacks permissions to create symlink")
        e.add_note(f"Target: {target}")
        e.add_note(f"Link location: {link_name}")
        e.add_note("On Windows: Run as Administrator to create symlinks")
        e.add_note("On Linux/macOS: Check directory write permissions")
        raise
    except OSError as e:
        e.add_note(f"Symlink creation failed")
        e.add_note(f"Target: {target}")
        e.add_note(f"Link location: {link_name}")
        raise
```

### Anti-Patterns to Avoid

- **Bare except with pass:**
  ```python
  # BAD: Silently hides ALL errors
  try:
      risky_operation()
  except:
      pass
  ```

- **Broad exception catching (Exception:):**
  ```python
  # BAD: Catches too much, including KeyboardInterrupt, SystemExit
  try:
      risky_operation()
  except Exception as e:
      print(f"Warning: {e}")
  ```

- **Silent continuation on critical failures:**
  ```python
  # BAD: Continues when 'latest' creation fails
  try:
      os.symlink(target, latest)
  except OSError:
      pass  # Now user references stale data without knowing
  ```

- **Minimal warnings for optional dependencies:**
  ```python
  # BAD: User doesn't know impact or how to fix
  try:
      import optional_lib
  except ImportError:
      print("Warning: optional_lib not available")
  ```

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Cross-platform symlink handling | Custom symlink detection logic | `os.symlink()` + `shutil.copytree()` fallback | os.symlink raises OSError with specific errno values |
| Exit code management | Manual sys.exit() calls | `sys.exit()` with clear error codes | Standard convention, integrates with shell scripts |
| Exception context | String concatenation in errors | `e.add_note()` (Python 3.11+) | PEP 678 standard, preserved in tracebacks |
| Error logging | print() statements | `logging` module or print to stderr with context | Better integration with log files, clearer severity levels |

**Key insight:** Python's standard library has well-tested solutions for filesystem operations and error handling. Custom error handling patterns are worse because:
- They hide the actual exception type
- They make debugging harder
- They don't follow Python conventions
- They're not maintainable by other developers

## Common Pitfalls

### Pitfall 1: Bare `except:` catches `KeyboardInterrupt` and `SystemExit`

**What goes wrong:** Using `except:` catches absolutely everything, including user interrupts (Ctrl+C) and system exit requests. This prevents users from terminating scripts and can cause infinite loops.

**Why it happens:** Developers use bare `except:` to "handle any error" without realizing it catches control-flow exceptions.

**How to avoid:** Always specify exception types or at minimum catch `Exception` (which excludes `BaseException` subclasses like `KeyboardInterrupt`).

**Warning signs:** Scripts that can't be stopped with Ctrl+C, or that print generic errors.

### Pitfall 2: Silent failures degrade data integrity

**What goes wrong:** Operations that are expected to succeed (like updating 'latest' directories) fail silently, leaving the system in an inconsistent state. Users then make decisions based on stale data.

**Why it happens:** Error handlers use `pass` or minimal warnings to avoid "noisy output", but this prevents users from knowing something went wrong.

**How to avoid:**
- For critical operations: Log error details and exit with non-zero code
- For optional operations: Provide clear, actionable warnings about what was skipped
- Never use `pass` without explaining why the error can be safely ignored

**Warning signs:** Scripts complete "successfully" but users find inconsistencies later.

### Pitfall 3: Inconsistent error handling across duplicated code

**What goes wrong:** The `update_latest_symlink()` function is duplicated in three files (1.5_Utils.py, 2.2_ConstructVariables.py, 3.4_Utils.py) with slightly different error handling. One version logs errors but continues, another uses bare `except: pass`, creating unpredictable behavior.

**Why it happens:** Copy-paste without consistent code review, or evolving the function in one place but not others.

**How to avoid:**
- Create a single shared utility module
- Import the function from one location
- If duplication is necessary, use exact copies or inheritance

**Warning signs:** Multiple files with nearly identical function names or patterns.

### Pitfall 4: Optional dependency warnings lack context

**What goes wrong:** Users see "Warning: rapidfuzz not available" but don't know:
- What functionality will be degraded
- How much impact this has on their results
- How to install the missing dependency
- Whether it's critical or optional

**Why it happens:** Quick warnings are added during development without considering user onboarding.

**How to avoid:** Structure warnings with clear sections:
1. What's missing
2. Impact on results
3. Installation instructions
4. Whether it's critical (exit) or optional (continue)

**Warning signs:** Warnings printed to stdout (should be stderr), or single-line warnings without context.

## Code Examples

Verified patterns from official sources:

### Specific Exception Types for File Operations

```python
# Source: https://docs.python.org/3/library/exceptions.html
# Source: https://docs.python.org/3/library/os.html

import os
import sys

def safe_symlink_operation(target, link_name):
    """Handle specific filesystem errors."""
    try:
        os.symlink(target, link_name, target_is_directory=True)
    except PermissionError:
        # EPERM: No permission to create symlink
        print(f"ERROR: Permission denied creating symlink: {link_name}", file=sys.stderr)
        print(f"  On Windows: Run as Administrator", file=sys.stderr)
        sys.exit(1)
    except FileExistsError:
        # EEXIST: Symlink target already exists
        # This might be OK - decide based on your use case
        print(f"WARNING: Symlink already exists: {link_name}", file=sys.stderr)
        # Could choose to remove and recreate, or log and continue
    except FileNotFoundError:
        # ENOENT: Target doesn't exist
        print(f"ERROR: Symlink target not found: {target}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        # Catch-all for other OS errors
        print(f"ERROR: OS error creating symlink: {e}", file=sys.stderr)
        print(f"  errno: {e.errno}", file=sys.stderr)
        sys.exit(1)
```

### Proper Optional Dependency Handling

```python
# Source: https://docs.python.org/3/tutorial/errors.html

import sys

# Optional dependency with clear handling
OPTIONAL_DEPS_AVAILABLE = False
OPTIONAL_DEPS_VERSION = None

try:
    import some_optional_lib
    OPTIONAL_DEPS_AVAILABLE = True
    OPTIONAL_DEPS_VERSION = getattr(some_optional_lib, '__version__', 'unknown')
except ImportError:
    pass

def check_optional_deps():
    """Print rich warning if optional dependencies missing."""
    if not OPTIONAL_DEPS_AVAILABLE:
        print("\n" + "=" * 70, file=sys.stderr)
        print("OPTIONAL DEPENDENCY MISSING: some_optional_lib", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        print("\nFunctionality Impact:", file=sys.stderr)
        print("  - Feature X will use slower fallback method", file=sys.stderr)
        print("  - Processing time may increase by 50-100%", file=sys.stderr)
        print("  - Results will still be correct", file=sys.stderr)
        print("\nInstallation:", file=sys.stderr)
        print("  pip install some-optional-lib", file=sys.stderr)
        print("\nRecommendation:", file=sys.stderr)
        print("  Install for production use. Optional for testing/development.", file=sys.stderr)
        print("=" * 70 + "\n", file=sys.stderr)

# Call at script initialization
check_optional_deps()
```

### Exception Enrichment (Python 3.11+)

```python
# Source: https://peps.python.org/pep-0678/

import os
import sys

def copy_with_fallback(src, dst):
    """Copy directory with error context."""
    try:
        shutil.copytree(src, dst)
    except PermissionError as e:
        e.add_note(f"Source directory: {src}")
        e.add_note(f"Destination directory: {dst}")
        e.add_note("Check write permissions on destination")
        e.add_note("On Windows: Ensure no files in use")
        raise
    except FileNotFoundError as e:
        e.add_note(f"Source not found: {src}")
        raise
    except OSError as e:
        e.add_note(f"Source: {src}")
        e.add_note(f"Destination: {dst}")
        e.add_note("Directory copy failed")
        raise
```

### Logging to stderr for warnings

```python
# Standard pattern for warnings (not exceptions)

import sys

def print_warning(message):
    """Print warning to stderr."""
    print(f"WARNING: {message}", file=sys.stderr)

# Usage
print_warning("Optional dependency 'foo' not installed")
print_warning("  Installation: pip install foo")
print_warning("  Impact: Feature X will be disabled")
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Bare `except: pass` | Specific exception types | Always | Bugs no longer hidden |
| `print("Warning")` | `print(..., file=sys.stderr)` | Always | Warnings go to error stream |
| Minimal dependency warnings | Rich warnings with context | Always | Users understand impact |
| Silent symlink failures | Explicit exit on failure | Phase 7 | Data integrity protected |
| No installation hints | Clear pip install instructions | Phase 7 | Easy to fix issues |

**Deprecated/outdated:**
- Bare `except:` clauses - Never catch all exceptions
- `except Exception as e: pass` - Silently hiding bugs
- Warnings to stdout - Use stderr for warnings/errors
- Silent failures for critical operations - Always exit with non-zero code

## Open Questions

1. **Should Phase 7 create a shared utilities module?**
   - What we know: The `update_latest_symlink()` function is duplicated across 3 files with minor variations
   - What's unclear: Whether this phase should consolidate the function into a shared module or fix each instance in place
   - Recommendation: Fix each instance in place for this phase (minimal change), but note that consolidation would be a Phase 7+ improvement

2. **Should symlink failures be fatal (exit code 1) or warnings (continue)?**
   - What we know: Current code silently continues, causing users to reference stale 'latest' directories
   - What's unclear: Whether the symlink/copy is critical to pipeline correctness or just a convenience
   - Recommendation: Make it fatal (exit code 1) because silent failures compromise data integrity

## Sources

### Primary (HIGH confidence)
- https://docs.python.org/3/library/exceptions.html - Built-in exception hierarchy and OSError subclasses
- https://docs.python.org/3/library/os.html - os.symlink() documentation, OSError errno values
- https://docs.python.org/3/library/shutil.html - shutil.copytree() documentation, error handling
- https://docs.python.org/3/tutorial/errors.html - Exception handling best practices, specific vs broad catching
- PEP 678 (https://peps.python.org/pep-0678/) - Exception enrichment with add_note()

### Secondary (MEDIUM confidence)
- Current codebase analysis - Identified three files with update_latest_symlink() and their error handling patterns
- grep results - Found 28+ instances of bare except blocks with pass statements

### Tertiary (LOW confidence)
- None - All research from official Python documentation

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All from official Python documentation
- Architecture: HIGH - Based on PEP 678 and official tutorial
- Pitfalls: HIGH - Documented in official Python how-to

**Research date:** 2026-01-23
**Valid until:** 30 days (Python standard library is stable, these patterns don't change frequently)
