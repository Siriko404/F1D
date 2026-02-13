# Phase 66: Code Quality Standard - Research

**Researched:** 2026-02-13
**Domain:** Python code quality standards (naming conventions, docstrings, type hints, error handling)
**Confidence:** HIGH

## Summary

This phase defines the CODE_QUALITY_STANDARD.md document that establishes naming conventions and code quality standards for the F1D project. The research covers Python PEP 8 conventions, Google-style docstrings, mypy type hint requirements, custom exception patterns, and function/module organization standards.

The existing codebase already follows many conventions (SCRIPT_DOCSTANDARD.md for headers, module tier system from Phase 65). This standard will formalize and extend those patterns for consistency across all code.

**Primary recommendation:** Extend the existing SCRIPT_DOCSTANDARD.md header format with inline docstring standards (Google-style), formalize the naming conventions already in practice (Stage.Step_Description.py pattern), and align type hint requirements with the tier system from Phase 65.

---

## Prior Decisions from Phase 65 (LOCKED)

These decisions from ARCHITECTURE_STANDARD.md constrain this phase:

| Decision | Implication for Phase 66 |
|----------|--------------------------|
| src-layout pattern adopted | Naming conventions apply to src/f1d/ structure |
| Module tier system defined | Quality bars per tier: Tier 1=100%, Tier 2=80%, Tier 3=Optional |
| V1 and V2 are active variants | Version suffixes in naming (v1/, v2/ subpackages) |
| Absolute imports preferred | Import organization follows stdlib -> third-party -> local |
| __init__.py patterns defined | Public API exports with __all__ |

---

## Standard Stack

### Core (Python Language Standards)

| Standard | Version | Purpose | Why Standard |
|----------|---------|---------|--------------|
| PEP 8 | Current | Style guide for Python code | Official Python style guide, universal adoption |
| PEP 257 | Current | Docstring conventions | Official docstring format standard |
| PEP 484 | Current | Type hints | Official type hint specification |
| PEP 621 | Current | pyproject.toml metadata | Modern Python packaging standard |

### Tooling (Already in Project)

| Tool | Version | Purpose | Configuration |
|------|---------|---------|---------------|
| mypy | 1.19+ | Static type checking | pyproject.toml [tool.mypy] |
| ruff | Current | Linting + formatting | pyproject.toml [tool.ruff] |
| pytest | 8.0+ | Test framework | pyproject.toml [tool.pytest] |

### Documentation Standards

| Standard | Source | Purpose |
|----------|--------|---------|
| Google-style docstrings | [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) | Function/method documentation with Args/Returns/Raises |
| Napoleon extension | Sphinx | Supports Google-style in documentation generation |

---

## Architecture Patterns

### Naming Conventions

#### Script Naming (Stage.Step_Description.py)

**Pattern:** `{Stage}.{Step}_{Description}.py`

| Component | Format | Example |
|-----------|--------|---------|
| Stage | Single digit (1-4) | 1, 2, 3, 4 |
| Step | Single decimal | 1.0, 1.1, 3.5 |
| Description | PascalCase | BuildSampleManifest, H1Variables |
| Separator | Underscore after step | 1.0_BuildSampleManifest.py |

**Examples from current codebase:**
- `1.0_BuildSampleManifest.py` - Stage 1, step 0, orchestrator
- `3.1_H1Variables.py` - Stage 3, step 1, H1 hypothesis variables
- `4.11_H9_Regression.py` - Stage 4, step 11, H9 regression

**Rationale:** The Stage.Step prefix provides natural sort order and immediate context about where the script fits in the pipeline.

#### Module Naming (snake_case)

**Pattern:** `{descriptive_name}.py`

| Element | Convention | Example |
|---------|------------|---------|
| Module files | snake_case | `panel_ols.py`, `path_utils.py` |
| Package directories | snake_case | `shared/`, `observability/` |
| Version variants | lowercase `v` + number | `v1/`, `v2/` |

**Anti-patterns:**
- camelCase modules: `panelOls.py` (WRONG)
- Abbreviated names: `pu.py`, `ut.py` (WRONG)
- Mixed conventions: `Panel_OLS.py` (WRONG)

#### Function/Class Naming

| Element | Convention | Example |
|---------|------------|---------|
| Functions | snake_case | `get_latest_output_dir()`, `run_panel_ols()` |
| Classes | PascalCase | `CollinearityError`, `DualWriter` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |
| Private functions | _leading_underscore | `_check_thin_cells()`, `_format_coefficient_table()` |

**Source:** [PEP 8 - Naming Conventions](https://peps.python.org/pep-0008/#naming-conventions)

#### Variable Naming

| Context | Pattern | Example |
|---------|---------|---------|
| DataFrame | descriptive_df or just descriptive | `df`, `manifest_df`, `panel_df` |
| Series | descriptive_s or just descriptive | `returns_s`, `uncertainty` |
| Counts | n_ prefix or _count suffix | `n_firms`, `record_count` |
| Indices | i_, j_, k_ for simple loops | `i_row`, `j_col` |
| Boolean | is_, has_, should_ prefixes | `is_valid`, `has_missing`, `should_retry` |
| Paths | _path or _dir suffix | `output_path`, `input_dir` |

### Docstring Standard (Google-style)

#### Module Header (Existing Standard)

The project already uses a custom header format defined in SCRIPT_DOCSTANDARD.md. This should be retained for script-level documentation:

```python
#!/usr/bin/env python3
"""
==============================================================================
STEP X.Y: {Script Name}
==============================================================================
ID: X.Y_ScriptName
Description: {One-line description}

Inputs:
    - 4_Outputs/{path}/{file.parquet}

Outputs:
    - 4_Outputs/{path}/{output.parquet}

Deterministic: true
Dependencies:
    - Requires: Step X.{Y-1}
    - Uses: shared.module1

Author: Thesis Author
Date: YYYY-MM-DD
==============================================================================
"""
```

#### Function/Method Docstrings (Google-style)

**Source:** [Google Python Style Guide - Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)

```python
def run_panel_ols(
    df: pd.DataFrame,
    dependent: str,
    exog: List[str],
    entity_col: str = "gvkey",
    time_col: str = "year",
) -> Dict[str, Any]:
    """Execute panel regression with fixed effects.

    Runs a PanelOLS regression with entity and time fixed effects,
    clustered standard errors, and multicollinearity diagnostics.

    Args:
        df: DataFrame with panel data containing all variables.
        dependent: Name of the dependent variable column.
        exog: List of exogenous variable column names.
        entity_col: Column name for entity identifier. Defaults to "gvkey".
        time_col: Column name for time period. Defaults to "year".

    Returns:
        Dictionary containing:
            - model: Fitted PanelOLS object
            - coefficients: DataFrame with beta, SE, t-stat, p-value
            - summary: Dict with R2, adj_R2, N, F-stat
            - diagnostics: Dict with VIF values, condition_number
            - warnings: List of warning messages

    Raises:
        CollinearityError: If perfect collinearity detected in design matrix.
        MulticollinearityError: If VIF threshold exceeded.
        ValueError: If required columns missing from DataFrame.

    Examples:
        >>> result = run_panel_ols(df, "cash_holdings", ["uncertainty", "leverage"])
        >>> print(result["summary"]["r2"])
        0.45
    """
```

**Required sections by module tier:**

| Tier | Args | Returns | Raises | Examples |
|------|------|---------|--------|----------|
| Tier 1 (Core) | Required | Required | Required | Required |
| Tier 2 (Stage) | Required | Required | Required | Recommended |
| Tier 3 (Scripts) | Recommended | If non-void | If exceptions | Optional |

### Type Hint Coverage

**Source:** [mypy documentation](https://mypy.readthedocs.io/)

#### Tier Requirements

| Tier | Coverage Target | mypy Mode | Enforcement |
|------|-----------------|-----------|-------------|
| Tier 1 (Core Shared) | 100% | `strict = true` | CI blocking |
| Tier 2 (Stage-Specific) | 80%+ | `disallow_untyped_defs = false` | Warning |
| Tier 3 (Scripts) | Optional | Excluded from mypy | None |

#### mypy Configuration Pattern

```toml
[tool.mypy]
python_version = "3.9"
warn_return_any = true
check_untyped_defs = true

# Strict mode for Tier 1
[[tool.mypy.overrides]]
module = "shared.observability.*"
strict = true

# Gradual adoption for Tier 2
[[tool.mypy.overrides]]
module = "shared.panel_ols"
disallow_untyped_defs = false
```

### Import Organization

**Pattern (PEP 8 standard):**

```python
# 1. Standard library (alphabetical)
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# 2. Third-party packages (alphabetical)
import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

# 3. Local imports (absolute, alphabetical)
from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.panel_ols import run_panel_ols
```

**Rules:**
1. Absolute imports over relative: `from f1d.shared.path_utils` not `from ..path_utils`
2. Group imports with blank lines between sections
3. Sort alphabetically within each section
4. Use `from X import Y` for specific items, `import X` for module-level access

### Error Handling Pattern

**Source:** [PEP 760 - No More Bare Excepts](https://peps.python.org/pep-0760/) (2024), [Real Python - Exception Handling](https://realpython.com/ref/best-practices/exception-handling/)

#### Custom Exceptions

**Pattern:** Inherit from `Exception`, use descriptive names ending in `Error`

```python
# src/f1d/shared/exceptions.py (consolidated location)
"""Custom exceptions for F1D pipeline."""


class F1DError(Exception):
    """Base exception for all F1D-specific errors."""
    pass


class DataValidationError(F1DError):
    """Raised when data validation fails."""
    pass


class CollinearityError(F1DError):
    """Raised when perfect collinearity detected in design matrix."""
    pass


class OutputResolutionError(F1DError):
    """Raised when output directory cannot be resolved."""
    pass


class RegressionValidationError(F1DError):
    """Raised when regression inputs fail validation."""
    pass
```

**Current exceptions in codebase:**
- `CollinearityError` - panel_ols.py, diagnostics.py
- `MulticollinearityError` - panel_ols.py, diagnostics.py
- `PathValidationError` - path_utils.py
- `OutputResolutionError` - path_utils.py
- `DataValidationError` - data_validation.py
- `FinancialCalculationError` - data_validation.py
- `EnvValidationError` - env_validation.py
- `WeakInstrumentError` - iv_regression.py
- `RegressionValidationError` - regression_validation.py

**Recommendation:** Consolidate all custom exceptions into `src/f1d/shared/exceptions.py` for central management.

#### No Bare Except

**Anti-pattern (never use):**
```python
try:
    operation()
except:  # WRONG - catches SystemExit, KeyboardInterrupt
    pass
```

**Correct patterns:**
```python
# Specific exception
try:
    operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise

# Multiple specific exceptions
try:
    operation()
except (ValueError, TypeError) as e:
    logger.error(f"Input error: {e}")
    raise DataValidationError(str(e)) from e

# Re-raise with context
try:
    risky_operation()
except FileNotFoundError as e:
    raise DataValidationError(f"Required file not found: {e}") from e
```

**Key rules:**
1. Never use bare `except:` (will be enforced by PEP 760)
2. Always specify exception type(s)
3. Either handle the exception or re-raise it
4. Use `raise ... from e` for exception chaining
5. Log exceptions before re-raising when appropriate

### Function Size Limits

**Source:** [Clean Code principles](https://codezone.blog/how-to-write-readable-python-functions-ultimate-clean-code-guide-with-examples/)

| Guideline | Recommendation | Rationale |
|-----------|----------------|-----------|
| Target length | 20-30 lines | Readability, testability |
| Maximum length | 50 lines | Hard limit requiring justification |
| Single Responsibility | One thing well | More important than line count |
| Cognitive complexity | < 10 | Avoid nested conditionals |

**Warning signs:**
- Function requires scrolling to read
- Multiple levels of indentation (>3)
- More than 3-4 parameters
- "And" in function name (`load_and_validate_and_transform`)

### Output File Naming

**Pattern:** `{descriptor}_{timestamp}_{checksum}.{extension}`

| Component | Format | Example |
|-----------|--------|---------|
| Timestamp | ISO 8601 compact | `20260213_143052` |
| Date-only | ISO 8601 | `2026-02-13` |
| Checksum | SHA-256 (12 chars) | `a3f2b8c91d2f` |
| Version | v + number | `v1`, `v2` |

**Examples:**
```
# With timestamp directory
4_Outputs/1.0_BuildSampleManifest/2026-02-13-143052/master_manifest.parquet

# With checksum (for data integrity)
data/processed/manifest_20260213_a3f2b8c91d2f.parquet

# With version
results/regressions/H1_results_v2.parquet
```

---

## Common Pitfalls

### Pitfall 1: Inconsistent Naming Between Script and Module

**What goes wrong:** Script named `3.1_H1Variables.py` exports function `construct_h1_vars()` instead of `construct_h1_variables()`.

**Why it happens:** Developers use abbreviations inconsistently.

**How to avoid:** Use full words in all naming; establish abbreviation list (e.g., always `variables` not `vars`).

**Warning signs:** `vars`, `vals`, `utils` without specific descriptor.

### Pitfall 2: Missing Type Hints on Public API

**What goes wrong:** Tier 1 module exports function without type hints, breaking downstream type checking.

**Why it happens:** Adding type hints after the fact is tedious.

**How to avoid:** Require type hints on all public functions before merge; use `strict = true` for Tier 1.

**Warning signs:** mypy errors in downstream modules that import from Tier 1.

### Pitfall 3: Bare Except Catching SystemExit

**What goes wrong:** `except:` catches `SystemExit` and `KeyboardInterrupt`, preventing clean shutdown.

**Why it happens:** Developers want to catch "all errors."

**How to avoid:** Always specify exception types; use `except Exception` for broad catching (still allows SystemExit).

**Warning signs:** `except:` with no exception type specified.

### Pitfall 4: Module-Level Docstring Missing

**What goes wrong:** Module has no docstring, making `help(module)` useless.

**Why it happens:** Scripts are written quickly without documentation.

**How to avoid:** Require module docstring as part of SCRIPT_DOCSTANDARD.md compliance.

**Warning signs:** Empty `__init__.py` files, scripts starting with imports only.

---

## Code Examples

### Complete Module Example (Tier 1)

```python
#!/usr/bin/env python3
"""
================================================================================
SHARED MODULE: Path Utilities
================================================================================
ID: shared/path_utils
Description: Path validation and directory creation helpers using pathlib.

Purpose: Provides robust path handling for the F1D pipeline with proper
         error handling and cross-platform compatibility.

Inputs:
    - Path objects for validation (pathlib.Path)

Outputs:
    - Validated Path objects (resolved to absolute paths)
    - Created directories (if needed)

Main Functions:
    - get_latest_output_dir(): Get latest output directory by timestamp
    - ensure_output_dir(): Create output directory if not exists

Dependencies:
    - Uses: pathlib

Author: Thesis Author
Date: 2026-02-13
================================================================================
"""

from pathlib import Path
from typing import Optional

from f1d.shared.exceptions import F1DError


class PathValidationError(F1DError):
    """Raised when path validation fails."""
    pass


class OutputResolutionError(F1DError):
    """Raised when output directory resolution fails."""
    pass


def validate_output_path(
    path: Path,
    must_exist: bool = False,
    must_be_writable: bool = True,
) -> Path:
    """Validate output path exists and is accessible.

    Args:
        path: Path to validate.
        must_exist: If True, raise error if path doesn't exist.
        must_be_writable: If True, check path is writable.

    Returns:
        Validated Path object (resolved to absolute).

    Raises:
        PathValidationError: If validation fails.

    Examples:
        >>> from pathlib import Path
        >>> path = validate_output_path(Path("/tmp/output"), must_exist=False)
        >>> str(path).startswith("/")
        True
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
                raise PathValidationError(f"Path not writable: {path}") from e

    return path.resolve()


def get_latest_output_dir(base_path: Path) -> Path:
    """Find the most recent output directory.

    Args:
        base_path: Base directory containing dated subdirectories.

    Returns:
        Path to the most recent dated subdirectory.

    Raises:
        OutputResolutionError: If no valid directories found.

    Examples:
        >>> from pathlib import Path
        >>> # Assuming directories: 2026-02-10, 2026-02-13
        >>> latest = get_latest_output_dir(Path("data/processed/manifest"))
        >>> latest.name
        '2026-02-13'
    """
    if not base_path.exists():
        raise OutputResolutionError(f"Base path does not exist: {base_path}")

    dated_dirs = [d for d in base_path.iterdir() if d.is_dir()]

    if not dated_dirs:
        raise OutputResolutionError(f"No output directories in {base_path}")

    # Sort by name (assumes YYYY-MM-DD format)
    dated_dirs.sort(reverse=True)
    return dated_dirs[0]
```

### __init__.py with Public API

```python
"""Shared utilities for F1D pipeline.

This package contains cross-cutting utilities used across all stages
of the data processing pipeline.

Modules:
    path_utils: Path resolution and output directory utilities
    panel_ols: Panel OLS regression utilities
    exceptions: Custom exception classes
"""

from f1d.shared.path_utils import (
    get_latest_output_dir,
    validate_output_path,
    OutputResolutionError,
    PathValidationError,
)
from f1d.shared.exceptions import F1DError

__all__ = [
    # Path utilities
    "get_latest_output_dir",
    "validate_output_path",
    "OutputResolutionError",
    "PathValidationError",
    # Base exception
    "F1DError",
]
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Squat docstrings | Google-style with Args/Returns | 2025+ | Better IDE support, documentation generation |
| No type hints | Gradual typing with mypy | PEP 484 (2014), mainstream 2020+ | Catch errors before runtime |
| Bare `except:` | Explicit exception types | PEP 760 (2024) | No more masking system exceptions |
| Flat imports | Absolute imports with sections | PEP 8 | Clearer dependency structure |

**Deprecated/outdated:**
- `# type: ignore` comments without justification: Use specific error codes
- `Any` type hints: Use specific types or `Protocol`
- Relative imports in production code: Use absolute imports

---

## Open Questions

1. **Should we consolidate all exceptions into one file?**
   - What we know: 11 exception classes across 6 files currently
   - What's unclear: Whether consolidation would break existing imports
   - Recommendation: Create `src/f1d/shared/exceptions.py` and deprecate per-module exceptions gradually

2. **What is the exact mypy strict mode rollout plan?**
   - What we know: Tier 1 already has `strict = true` for observability modules
   - What's unclear: Timeline for other Tier 1 modules
   - Recommendation: Add one Tier 1 module at a time to strict mode, fix errors, commit

---

## Sources

### Primary (HIGH confidence)
- [PEP 8 - Style Guide for Python Code](https://peps.python.org/pep-0008/) - Naming conventions, import organization
- [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/) - Docstring format
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/) - Type hint specification
- [PEP 760 - No More Bare Excepts](https://peps.python.org/pep-0760/) - Exception handling
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) - Google-style docstrings
- [mypy documentation](https://mypy.readthedocs.io/) - Type checking configuration

### Secondary (MEDIUM confidence)
- [Sphinx Napoleon - Google Style Examples](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) - Docstring examples
- [Real Python - Exception Handling Best Practices](https://realpython.com/ref/best-practices/exception-handling/) - Error handling patterns
- Project's existing SCRIPT_DOCSTANDARD.md - Header documentation standard

### Tertiary (Contextual)
- ARCHITECTURE_STANDARD.md (Phase 65 output) - Module tier system, import conventions
- pyproject.toml - Current mypy, ruff, pytest configuration

---

## Metadata

**Confidence breakdown:**
- Naming conventions: HIGH - PEP 8 is authoritative, current codebase patterns verified
- Docstrings: HIGH - Google-style is well-documented, Napoleon examples available
- Type hints: HIGH - mypy documentation is comprehensive, project has existing config
- Error handling: HIGH - PEP 760 is recent (2024), community consensus clear
- Function size: MEDIUM - Guidelines are recommendations, not standards

**Research date:** 2026-02-13
**Valid until:** 30 days (stable standards, but PEP 760 status may change)
