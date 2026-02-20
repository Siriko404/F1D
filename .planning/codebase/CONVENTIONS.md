# Coding Conventions

**Analysis Date:** 2026-02-15

## Naming Patterns

**Files:**
- `snake_case.py` - All Python files use lowercase with underscores
- `__init__.py` - Module initialization files (in every package directory)
- `test_*.py` - Unit test files prefixed with `test_`
- `*_test.py` - Alternative test pattern (supported by pytest config)
- Config files: `project.yaml`, `.coveragerc`, `pyproject.toml`

**Functions:**
- `snake_case` - All function names use lowercase with underscores
- `run_*` - Prefix for main execution functions (e.g., `run_panel_ols`, `run_iv2sls`)
- `calculate_*` - Functions that compute values (e.g., `calculate_firm_controls`)
- `compute_*` - Functions that derive computed features (e.g., `compute_financial_features`)
- `validate_*` - Functions that check validity (e.g., `validate_input_file`)
- `_private_function` - Internal helper functions start with underscore
- `__dunder__` - Special methods only

**Variables:**
- `snake_case` - Local variables use lowercase with underscores
- `CONSTANT_UPPERCASE` - Module-level constants use uppercase
- `CamelCase` - Classes and exceptions use CamelCase

**Types:**
- `PascalCase` - All class names (including exceptions and type aliases)
- `snake_case` - Type aliases for function return types can use snake_case
- Generic types: `T`, `K`, `V` for generic type parameters

## Code Style

**Formatting:**
- **Ruff** - Primary formatter (v0.9.0+)
  - `line-length = 88` (matches Black default)
  - `indent-width = 4` spaces
  - `quote-style = "double"` for strings
  - `indent-style = "space"` (no tabs)
- **Pre-commit hooks** enforce formatting automatically
- Configured in: `pyproject.toml [tool.ruff.format]`

**Linting:**
- **Ruff** - Primary linter (replaces flake8, isort, etc.)
  - Enabled rules: E, W, F, I, B, C4, UP, ARG, SIM
  - Key ignores: E501 (line too long), B008 (function calls in defaults)
  - Per-file ignores:
    - `__init__.py`: E402, F401 (import violations, unused imports)
    - `tests/**`: S101, ARG (allow assert, unused fixtures)
    - `._archive/**`: ALL (ignore archived code)
- **MyPy** - Type checking (v1.14.1+)
  - Tier 1 (shared modules): `strict = true`
  - Tier 2 (stage modules): Moderate mode, allow untyped definitions
  - Configured in: `pyproject.toml [tool.mypy]`

**Pre-commit:**
- Configured in: `.pre-commit-config.yaml`
- Runs before every commit: ruff lint, ruff format, mypy, YAML validation
- Hook versions match CI workflow versions for consistency

## Import Organization

**Order:**
1. Standard library imports (e.g., `os`, `sys`, `pathlib`, `typing`)
2. Third-party imports (e.g., `pandas`, `numpy`, `pydantic`, `yaml`)
3. Local project imports (`from f1d.shared...` or `from f1d.econometric...`)

**Path Aliases:**
- None explicitly configured
- Use full module paths: `from f1d.shared.financial_utils import calculate_firm_controls`

**Import Style:**
- Use absolute imports for all module imports (no relative imports)
- Group related imports together (e.g., all `pandas` and `numpy` together)
- Avoid wildcard imports (`from module import *`) - use explicit imports
- Type imports: `from typing import Any, Dict, List, Optional`
- `from __future__ import annotations` at top of files for Python 3.9+ compatibility

## Error Handling

**Patterns:**
- **Custom exceptions** defined in each module for domain-specific errors:
  - `FinancialCalculationError` - Missing gvkey or Compustat data
  - `DataValidationError` - Schema violations
  - `PathValidationError` - Path validation failures
  - `OutputResolutionError` - Output directory resolution failures
  - `CollinearityError` - Perfect multicollinearity in design matrix
  - `MulticollinearityError` - High VIF threshold exceeded
  - `WeakInstrumentError` - First-stage F-stat below threshold
- **Exception chaining**: Use `from e` syntax for exception chaining
- **Error messages**: Include context information (file paths, values, what was expected)

**Handling Missing Data:**
- Use `np.nan` for missing/undefined values
- Defensive checks: `if data.get("at") and data["at"] > 0` before calculations
- Return `np.nan` when computation cannot be performed due to missing data
- Use `pd.notna()` / `.isna()` for pandas operations

## Logging

**Framework:** **structlog** (structured logging)
- Configured in: `src/f1d/shared/logging/config.py`
- Context-aware logging with `f1d.shared.logging.context`
- Dual-writer pattern: logs to both console and file simultaneously

**Patterns:**
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Use structured logging with context variables
- Subprocess execution: Use `DualWriter` to capture stdout/stderr
- Execution logs saved to: `logs/` with timestamp naming

**When to log:**
- INFO: Normal operation milestones, configuration loading, start/end of steps
- WARNING: Non-critical issues, fallbacks, deprecated feature usage
- ERROR: Exceptions that don't halt execution but should be investigated
- CRITICAL: Errors that halt pipeline execution

## Comments

**When to Comment:**
- **Module docstrings**: Required for all `.py` files (see template below)
- **Function docstrings**: Required for all public functions using Google style
- **Inline comments**: For complex logic, non-obvious calculations, or workarounds
- **TODO/FIXME**: For known issues requiring future work

**JSDoc/TSDoc:**
- Use **Google-style docstrings** (not NumPy or reStructuredText)
- Triple quotes `"""` for docstrings
- Include: Description, Args, Returns, Raises, Example sections
- Type hints in function signatures, not docstrings (use typing module)

**Docstring Template (Shared Modules):**
```python
#!/usr/bin/env python3
"""
================================================================================
SHARED MODULE: [Module Name]
================================================================================
ID: shared/[module_name]
Description: [What this module does]

Inputs:
    - [Input 1]
    - [Input 2]

Outputs:
    - [Output 1]
    - [Output 2]

Deterministic: [true/false]
Main Functions:
    - [Function 1]
    - [Function 2]

Dependencies:
    - Uses: [libraries]

Author: Thesis Author
Date: YYYY-MM-DD
================================================================================
"""
```

**Docstring Template (Stage Scripts):**
```python
"""
==============================================================================
STEP X.Y: [Step Name]
==============================================================================
ID: X.Y_[ScriptName]
Description: [What this step does]

Model Specification:
    [Mathematical model if applicable]

Hypothesis Tests:
    - [Hypothesis 1]
    - [Hypothesis 2]

Inputs:
    - [Input file paths]

Outputs:
    - [Output file paths]

Deterministic: [true/false]
Dependencies:
    - Requires: [Previous step]
    - Uses: [shared modules]

Author: Thesis Author
Date: YYYY-MM-DD
==============================================================================
"""
```

## Function Design

**Size:**
- No hard limit, but prefer functions under 50 lines
- Helper functions for complex logic (extract to `_private_function`)
- Large functions: Document sections with comment dividers

**Parameters:**
- Use type hints for all parameters
- Default values: Use `=` in function signature (not `None` in body)
- Optional parameters: Annotate with `Optional[T]` or `T | None`
- Config objects: Pass as parameters, not global variables

**Return Values:**
- Always use return type annotations
- Return `None` explicitly for no-value returns (not implicit)
- Dictionary returns: Use `Dict[str, Any]` for complex returns
- Data structures: Return typed collections (`List[T]`, `pd.DataFrame`, etc.)

**Type Annotations:**
- Use `from __future__ import annotations` for Python 3.9+ compatibility
- Required for `src/f1d/shared` modules (strict mypy mode)
- Optional for stage modules (`src/f1d/{sample,text,financial,econometric}`)

## Module Design

**Exports:**
- Use `__all__` to define public API for shared modules
- Example: `__all__ = ["calculate_firm_controls", "FinancialCalculationError"]`
- Internal functions: Start with `_` to indicate private

**Barrel Files:**
- `__init__.py` in each package directory
- Re-export key symbols for convenience
- Example pattern in `src/f1d/shared/__init__.py`

**Module Categories:**
1. **Tier 1 (Shared)** - `src/f1d/shared/*.py`
   - Strict type checking, 100% coverage target
   - Examples: `financial_utils.py`, `panel_ols.py`, `iv_regression.py`
2. **Tier 2 (Stage-specific)** - `src/f1d/{sample,text,financial,econometric}/*`
   - Moderate type checking, 80%+ coverage target
   - Examples: `4.1_H1CashHoldingsRegression.py`, `3.1_FirmControls.py`
3. **Scripts** - Entry point files for execution
   - May use `if __name__ == "__main__":` guard
   - Include CLI argument parsing with `argparse`

---

*Convention analysis: 2026-02-15*
