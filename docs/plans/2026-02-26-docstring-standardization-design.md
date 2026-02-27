# Docstring Standardization Design

**Date:** 2026-02-26
**Status:** Approved (post-red-team audit revision)
**Scope:** All 163 Python modules in `src/f1d/`

---

## 1. Overview

**Goal:** Standardize all docstrings across the codebase to a consistent, homogeneous format while treating code as the source of truth.

**Approach:** Clean-slate rewrite with preservation rules for high-quality existing docstrings.

---

## 2. File Inventory (Verified)

| Directory | Files | Module Type |
|-----------|------:|-------------|
| `src/f1d/sample/` | 7 | Stage 1 - Executable + libraries |
| `src/f1d/text/` | 3 | Stage 2 - Executable + libraries |
| `src/f1d/variables/` | 15 | Stage 3 - Executable + libraries |
| `src/f1d/econometric/` | 17 | Stage 4 - Executable + libraries |
| `src/f1d/reporting/` | 2 | Reporting - Executable + libraries |
| `src/f1d/shared/` | 118 | Infrastructure - Library modules |
| `src/f1d/__init__.py` | 1 | Package root |
| **Total** | **163** | |

**Entry Points (with `if __name__ == "__main__"`):** 40 files
**Library Modules:** 123 files

---

## 3. Execution Order (Dependency-Aware)

Process foundation first, then dependents:

| Phase | Directory | Files | Rationale |
|-------|-----------|------:|-----------|
| 1 | `src/f1d/__init__.py` | 1 | Package root |
| 2 | `src/f1d/shared/config/` | 6 | Configuration foundation |
| 3 | `src/f1d/shared/logging/` | 3 | Logging infrastructure |
| 4 | `src/f1d/shared/observability/` | 10 | Stats/monitoring |
| 5 | `src/f1d/shared/*.py` | 15 | Core utilities (not variables) |
| 6 | `src/f1d/shared/variables/base.py` | 1 | Variable builder base class |
| 7 | `src/f1d/shared/variables/*.py` | 83 | Individual variable builders |
| 8 | `src/f1d/sample/` | 7 | Stage 1 |
| 9 | `src/f1d/text/` | 3 | Stage 2 |
| 10 | `src/f1d/variables/` | 15 | Stage 3 |
| 11 | `src/f1d/econometric/` | 17 | Stage 4 |
| 12 | `src/f1d/reporting/` | 2 | Reporting |

---

## 4. Stage Mapping Convention

| Directory | Stage Value | Notes |
|-----------|-------------|-------|
| `src/f1d/sample/` | `1` | Sample construction |
| `src/f1d/text/` | `2` | Text processing |
| `src/f1d/variables/` | `3` | Panel building |
| `src/f1d/econometric/` | `4` | Regressions |
| `src/f1d/reporting/` | `N/A - Reporting` | Post-processing |
| `src/f1d/shared/` | `N/A - Shared Infrastructure` | Cross-stage utilities |
| `src/f1d/shared/variables/` | `3` | Variable builders (called by Stage 3) |
| `src/f1d/shared/config/` | `N/A - Configuration` | Config definitions |
| `src/f1d/shared/logging/` | `N/A - Logging` | Logging utilities |
| `src/f1d/shared/observability/` | `N/A - Observability` | Stats/monitoring |

---

## 5. Entry Point Definition

A module is marked **"Entry Point: Yes"** if and only if:
1. It contains an `if __name__ == "__main__":` block
2. It is intended for direct execution via `python -m f1d.{module_path}`

All other modules are **"Entry Point: No"** including:
- `__init__.py` files
- Class/function library modules
- Configuration modules

---

## 6. Docstring Preservation Rules

**DO NOT** strip existing docstrings if they:
1. Already follow Google-style convention (have Args/Returns/Raises sections)
2. Contain equivalent information to the required template
3. Include additional useful context (Examples, Notes, Warnings)

For preserved docstrings, only **ADD** missing required fields.

**Files with high-quality docstrings to preserve:**
- `src/f1d/sample/assemble_manifest.py` - Has structured format with ID, Description, Inputs, Outputs
- `src/f1d/shared/variables/base.py` - Has Google-style with Examples
- Any file with comprehensive existing documentation

---

## 7. Module Docstring Templates

### 7.1 Executable Script Template

For files with `if __name__ == "__main__"`:

```python
#!/usr/bin/env python3
"""{module_name} - {one-line description}.

Stage: {1|2|3|4|N/A - Reporting}
Entry Point: Yes

Purpose:
    {What this script does and why.}

Flow:
    1. {Step 1 description}
    2. {Step 2 description}
    ...

Inputs:
    - {path/to/input}: {description}

Outputs:
    - {path/to/output}: {description}

Usage:
    python -m f1d.{module_path}

Dependencies:
    - pandas, numpy (or key libraries)
    - f1d.shared.{module} (for internal deps)
"""
```

### 7.2 Library Module Template

For class/function modules without `__main__`:

```python
"""{module_name} - {one-line description}.

Purpose:
    {What this module provides.}

Key Classes/Functions:
    - {ClassName}: {brief description}
    - {function_name}: {brief description}

Usage:
    from f1d.{module_path} import {ClassName}
"""
```

### 7.3 Package `__init__.py` Template

```python
"""{package_name} - {one-line description}.

This package provides {summary of submodules}.

Modules:
    - {module_a}: {description}
    - {module_b}: {description}
"""
```

### 7.4 Configuration Module Template

For modules in `shared/config/`:

```python
"""{module_name} - {one-line description}.

Purpose:
    {What configuration this module defines.}

Configuration Keys:
    - {key1}: {description}
    - {key2}: {description}
"""
```

---

## 8. Function/Method Docstring Template

Google-style for all functions:

```python
def function_name(param1: Type1, param2: Type2) -> ReturnType:
    """One-line description.

    Longer description if needed for context.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of return value.

    Raises:
        ExceptionType: When this happens.
    """
```

### Private Function Rules

A private function (`_prefix`) requires a docstring if:
- It has >5 non-blank, non-comment, non-docstring lines of executable code

**Counting method:** Lines between `def` and next function/class, excluding:
- Blank lines
- Comment-only lines
- The function's own docstring
- Type annotations on separate lines

Dunder methods (`__init__`, `__str__`, etc.) follow the same rule.

---

## 9. Class Docstring Template

```python
class ClassName:
    """One-line description.

    Longer description if needed.

    Attributes:
        attr_name: Description of attribute.

    Example:
        >>> obj = ClassName(param=1)
        >>> obj.method()
    """
```

---

## 10. Verification Requirements

After each phase, run:

```bash
# Check docstring style
pydocstyle --convention=google src/f1d/{directory}/

# Check coverage
interrogate -v src/f1d/{directory}/

# Verify types preserved
mypy src/f1d/{directory}/
```

All three must pass before proceeding to next phase.

### Pre-commit Hook (to add after completion)

```yaml
repos:
  - repo: https://github.com/pycqa/pydocstyle
    rev: 2.3.0
    hooks:
      - id: pydocstyle
        args: ['--convention=google']
```

---

## 11. Report Format

**File:** `docs/DOCSTRING_AUDIT_REPORT.md`

```markdown
# Docstring Standardization Report
**Date:** YYYY-MM-DD
**Scope:** 163 Python modules in src/f1d/

## Summary
- Total files processed: X
- Files with docstrings added: Y
- Files with docstrings preserved: Z
- Files with docstrings fixed: W

## By Phase

### Phase 1: src/f1d/__init__.py
- [ADD] Module docstring added
- [ADD] Function docstrings: __version__ export documented

### Phase 2: src/f1d/shared/config/
#### loader.py
- [PRESERVE] Existing Google-style docstring kept
- [ADD] Missing Raises section for ConfigError

...

## Verification Results
- pydocstyle: PASS (0 errors)
- interrogate: PASS (100% coverage)
- mypy: PASS (types preserved)
```

---

## 12. Commit Strategy

Commit per phase for easy rollback:

```
docs: standardize docstrings in src/f1d/__init__.py
docs: standardize docstrings in shared/config
docs: standardize docstrings in shared/logging
docs: standardize docstrings in shared/observability
docs: standardize docstrings in shared utilities
docs: standardize docstrings in shared/variables
docs: standardize docstrings in sample
docs: standardize docstrings in text
docs: standardize docstrings in variables
docs: standardize docstrings in econometric
docs: standardize docstrings in reporting
```

---

## 13. Files Excluded

- `__pycache__/` directories
- Test files (`*_test.py`, `test_*.py`)
- Files in `tests/` directories
- Non-Python files (`.md`, `.yaml`, etc.)

---

## 14. Acceptance Criteria

- [ ] All 163 files have module docstrings
- [ ] All public functions have Google-style docstrings
- [ ] pydocstyle passes with zero errors
- [ ] interrogate reports 100% coverage
- [ ] No breaking changes to imports (verified by running test suite)
- [ ] mypy type checking passes (types preserved)

---

## 15. Trial Run (Before Full Implementation)

Test the approach on 3 files first:

1. `src/f1d/__init__.py` - Package init (simple)
2. `src/f1d/shared/variables/base.py` - Class module with good existing docs (preserve test)
3. `src/f1d/sample/assemble_manifest.py` - Executable with structured docs (preserve test)

Verify the templates work and preservation rules are correct before proceeding.

---

*Design document created: 2026-02-26*
*Red-team audit incorporated: 2026-02-26*
