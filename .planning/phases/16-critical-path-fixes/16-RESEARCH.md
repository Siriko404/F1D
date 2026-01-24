# Phase 16: Critical Path Fixes - Research

**Researched:** January 23, 2026
**Domain:** Data pipeline integration testing, path resolution, dead code detection
**Confidence:** HIGH

## Summary

Phase 16 closes critical integration gaps identified in v1.0.0 milestone audit: (1) Step 4 path mismatches causing runtime failures, (2) lack of end-to-end pipeline verification, (3) orphaned `parallel_utils.py` dead code. The research confirms the project already has the right infrastructure—pathlib for path handling, pytest/subprocess for integration testing, and shared utilities for path validation. The fixes are straightforward: correct hardcoded docstring paths, create an E2E test following existing integration test patterns, and remove or integrate orphaned code. No new dependencies required.

**Primary recommendation:** Use existing pytest/subprocess patterns to create an E2E test, fix path mismatches in docstrings using pathlib conventions, and remove orphaned `parallel_utils.py`.

## Standard Stack

The project already uses the standard stack for this domain. No new dependencies required.

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pytest | Current (installed) | E2E test framework | De facto standard for Python testing, supports subprocess execution |
| pathlib | Python 3.10+ stdlib | Path operations | Modern, cross-platform path handling (PEP 428) |
| subprocess | Python stdlib | Script execution | Official subprocess management API |

### Supporting (for dead code detection)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| vulture | 2.14 (2024-12-08) | Dead code detection | Static analysis for finding unused code |

**No installation needed** - all dependencies already exist in the project.

## Architecture Patterns

### Recommended Test Structure
```
tests/integration/
├── conftest.py              # Shared fixtures (already exists)
├── test_pipeline_step1.py    # Step 1 tests (exists)
├── test_pipeline_step2.py    # Step 2 tests (exists)
├── test_pipeline_step3.py    # Step 3 tests (exists)
└── test_pipeline_e2e.py      # E2E test (TO BE CREATED)
```

### Pattern 1: Integration Test Using subprocess.run()
**What:** Execute scripts as subprocesses, verify exit codes and output files
**When to use:** Testing end-to-end script execution
**Source:** Python subprocess documentation + existing project patterns
**Example:**
```python
# Source: tests/integration/test_pipeline_step1.py
def test_step1_full_pipeline():
    """Test Step 1 (1.1_CleanMetadata) runs end-to-end."""
    script_path = Path("2_Scripts/1_Sample/1.1_CleanMetadata.py")

    # Act - Run script via subprocess
    result = subprocess.run(
        ["python", str(script_path)],
        capture_output=True,
        text=True,
        timeout=600,
    )

    # Assert - Script succeeded
    assert result.returncode == 0, f"Script failed: {result.stderr}"

    # Verify output files exist
    output_dir = Path("4_Outputs/1.1_CleanMetadata/latest")
    assert output_dir.exists(), "Output directory not created"

    # Check for expected output files
    expected_files = ["cleaned_metadata.parquet", "stats.json"]
    for filename in expected_files:
        file_path = output_dir / filename
        assert file_path.exists(), f"Expected output file not found: {filename}"
```

### Pattern 2: Path Resolution with pathlib
**What:** Use pathlib.Path for cross-platform path operations, resolve paths at runtime
**When to use:** All file path operations in Python 3.10+
**Source:** Python pathlib documentation (PEP 428)
**Example:**
```python
# Source: Python 3.14.2 pathlib documentation
from pathlib import Path

# Resolve absolute path (handles symlinks, "..")
resolved = path.resolve()

# Validate path exists
if not path.exists():
    raise ValueError(f"Path does not exist: {path}")

# Check if directory
if path.exists() and not path.is_dir():
    raise ValueError(f"Path is not a directory: {path}")
```

### Pattern 3: Dead Code Detection with Vulture
**What:** Static analysis to find unused code
**When to use:** Removing orphaned/dead code, cleaning up codebase
**Source:** Vulture GitHub README (v2.14, 2024-12-08)
**Example:**
```bash
# Install
pip install vulture

# Find dead code
vulture 2_Scripts/shared/parallel_utils.py

# Only report 100% dead code
vulture 2_Scripts/shared/parallel_utils.py --min-confidence 100
```

### Anti-Patterns to Avoid
- **Hardcoded docstring paths:** Embedding paths in docstrings that don't match actual directory structure. Fix by validating paths at runtime and keeping docstrings in sync with implementation.
- **Silent script failures:** Not checking `subprocess.run()` return codes. Always assert `returncode == 0` and check `stderr` for error messages.
- **Manual path concatenation:** Using `os.path.join()` or string concatenation. Use `pathlib.Path` with the `/` operator: `root / "2_Text" / "2.2_Variables"`.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Path validation | Custom `isdir()`, `exists()` checks | `pathlib.Path.resolve()`, `.exists()`, `.is_dir()` | Handles symlinks, cross-platform, edge cases |
| Dead code detection | Manual code review or grep | `vulture` (static analysis) | Finds unused imports, functions, variables automatically |
| Script execution | `os.system()`, `os.popen()` | `subprocess.run()` | Proper process management, timeout support, return code handling |
| E2E test structure | Custom test runner | `pytest` + `subprocess` markers | Standard testing framework, fixtures, parallel execution |

**Key insight:** Path validation and subprocess execution are well-solved problems. The project already has the right patterns (see `shared/path_utils.py` and existing integration tests). Don't reinvent these—use existing infrastructure.

## Common Pitfalls

### Pitfall 1: Path Mismatch Between Docstring and Implementation
**What goes wrong:** Scripts reference non-existent directories in docstring "Inputs" section, causing confusion but not immediate failures (only when consumers try to use those paths).
**Why it happens:** Docstrings not updated after directory restructure (e.g., `2.4_Linguistic_Variables` → `2_Textual_Analysis/2.2_Variables`).
**How to avoid:**
1. Always validate paths at runtime using `shared/path_utils.py` helpers
2. Keep docstrings in sync with actual directory structure
3. Consider adding a pre-commit hook to validate docstring paths
**Warning signs:** Scripts reference directories that don't exist in `4_Outputs/`, grep finds paths that don't match filesystem structure.

### Pitfall 2: E2E Test Doesn't Catch Data Flow Issues
**What goes wrong:** Individual step tests pass, but data doesn't flow correctly between steps (e.g., Step 4 expects files Step 2 doesn't create).
**Why it happens:** Tests run steps in isolation, not verifying inter-step dependencies.
**How to avoid:**
1. Create a true E2E test that runs all steps in sequence
2. Verify output of Step N is readable by Step N+1
3. Test with realistic data size to catch edge cases
**Warning signs:** Milestone audit shows "Integration Health" < 100%, scripts fail when run in sequence.

### Pitfall 3: Removing Code That Might Be Used
**What goes wrong:** Delete `parallel_utils.py`, but later refactoring needs deterministic parallel RNG.
**Why it happens:** Code is orphaned now, but could be useful in future.
**How to avoid:**
1. Use `vulture` to confirm code is truly unused (no imports, no references)
2. Check if code is in ARCHIVE or referenced in any planning docs
3. Consider deprecation notice before deletion
**Warning signs:** Vulture reports code at 100% confidence, `grep -r` finds no imports or references in active code.

### Pitfall 4: subprocess.run() Timeout Issues
**What goes wrong:** E2E test hangs indefinitely because a script takes longer than expected.
**Why it happens:** Scripts process large datasets, no timeout set on `subprocess.run()`.
**How to avoid:**
1. Always set `timeout` parameter on `subprocess.run()`
2. Use generous timeouts (10+ minutes for data processing)
3. Document expected runtime in test docstrings
**Warning signs:** Tests hang indefinitely, CI jobs time out after default duration.

## Code Examples

Verified patterns from official sources and existing codebase:

### Running Script with subprocess.run()
```python
# Source: Python subprocess documentation + existing tests
import subprocess
from pathlib import Path

def test_script_execution():
    script_path = Path("2_Scripts/1_Sample/1.1_CleanMetadata.py")

    result = subprocess.run(
        ["python", str(script_path)],
        capture_output=True,
        text=True,
        timeout=600,  # 10 minute timeout
    )

    # Check return code
    assert result.returncode == 0, f"Script failed: {result.stderr}"
```

### Validating Paths with pathlib
```python
# Source: Python pathlib documentation
from pathlib import Path

def validate_path_exists(path_str: str) -> Path:
    """Validate path exists and return resolved Path object."""
    path = Path(path_str)

    if not path.exists():
        raise ValueError(f"Path does not exist: {path}")

    # Resolve symlinks and ".." components
    return path.resolve()
```

### Checking for Dead Code with Vulture
```bash
# Source: Vulture GitHub README (v2.14, 2024-12-08)
# Check for unused code
vulture 2_Scripts/shared/parallel_utils.py

# Only report 100% dead code (no false positives)
vulture 2_Scripts/shared/parallel_utils.py --min-confidence 100
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `os.path` for paths | `pathlib.Path` (PEP 428) | Python 3.4+ | Cleaner, cross-platform path handling |
| `os.system()` for subprocess | `subprocess.run()` | Python 3.5+ | Better process control, timeout support, return code handling |
| Manual code review | Vulture static analysis | 2012+ | Automated dead code detection, configurable confidence |

**Deprecated/outdated:**
- **`os.path` for new code:** Use `pathlib.Path` for all new path operations
- **`os.system()` for script execution:** Use `subprocess.run()` with proper error handling
- **Manual dead code detection:** Use `vulture` for systematic detection

## Open Questions

None. All research domains have clear, verified solutions using existing project infrastructure.

## Sources

### Primary (HIGH confidence)
- **Python 3.14.2 subprocess documentation** - subprocess.run() API, timeout handling, return code checking
- **Python 3.14.2 pathlib documentation** - Path operations, resolve(), exists(), is_dir()
- **Vulture GitHub README** - Dead code detection, confidence levels, usage patterns
- **Existing codebase patterns** - `tests/integration/test_pipeline_step*.py`, `shared/path_utils.py`

### Secondary (MEDIUM confidence)
- **Existing project infrastructure** - pytest configuration (conftest.py), integration test patterns

### Tertiary (LOW confidence)
- None used for this phase

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All tools exist in project, no new dependencies needed
- Architecture: HIGH - Patterns verified with official documentation and existing codebase
- Pitfalls: HIGH - Issues observed in current codebase, fixes are straightforward

**Research date:** January 23, 2026
**Valid until:** 30 days (Python ecosystem stable, but verify vulture version if deferring removal of parallel_utils.py)
