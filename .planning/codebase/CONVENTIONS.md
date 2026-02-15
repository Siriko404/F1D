# Coding Conventions

**Analysis Date:** 2026-02-14

## Naming Patterns

**Files:**
- `snake_case.py` - All Python source files use snake_case
- Pattern for scripts: `{Major}.{Minor}_{DescriptiveName}.py` (e.g., `1.0_BuildSampleManifest.py`, `3.1_H1Variables.py`)
- Shared modules: `{category}_{name}.py` in `src/f1d/shared/` (e.g., `path_utils.py`, `financial_utils.py`)
- Test files: `test_{module}.py` in `tests/unit/`, `tests/integration/`, `tests/regression/`, `tests/performance/`, `tests/verification/`
- Config files: `project.yaml`, `.coveragerc`, `.pre-commit-config.yaml`

**Functions:**
- `snake_case` for all function and method names (e.g., `calculate_firm_controls`, `load_config`, `validate_output_path`)
- Private/internal functions: `_leading_underscore` (e.g., `_format_number`, `_add_constant_to_dataframe`)
- Factory fixtures: `{name}_factory` pattern in tests

**Variables:**
- `snake_case` for all variables (e.g., `firm_data`, `compustat_df`, `missing_values`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `DATA_RAW`, `INPUT_SCHEMAS`, `ALLOWED_SCRIPT_DIR`)
- DataFrame variables: `{entity}_df` or descriptive names (e.g., `compustat_df`, `result_df`)

**Types/Classes:**
- `PascalCase` for class names (e.g., `PathValidationError`, `OutputResolutionError`, `DataValidationError`, `FinancialCalculationError`, `WeakInstrumentError`)
- Exception classes follow `{ErrorName}Error` pattern
- Abstract base classes: None observed

**Constants:**
- Module-level constants: `UPPER_SNAKE_CASE` (e.g., `DATA_RAW`, `DATA_INTERIM`, `LOGS_DIR`, `RESULTS_DIR`)
- Config keys: `snake_case` in YAML (e.g., `year_start`, `random_seed`)

## Code Style

**Formatting:**
- Tool: Ruff (acts as both linter and formatter)
- Line length: 88 characters
- Indent width: 4 spaces
- Quote style: Double quotes for strings
- Config file: `pyproject.toml` sections `[tool.ruff]` and `[tool.ruff.format]`

**Linting:**
- Tool: Ruff (pre-commit hook)
- Enabled rules: E (pycodestyle errors), W (pycodestyle warnings), F (pyflakes), I (isort), B (flake8-bugbear), C4 (flake8-comprehensions), UP (pyupgrade), ARG (flake8-unused-arguments), SIM (flake8-simplify)
- Ignored rules: E501 (line too long - handled by formatter), B008 (function calls in argument defaults)
- Per-file ignores: `__init__.py` allows E402, F401; archived code ignored entirely
- Strict mode markers: `# type: ignore[attr-defined]` for type checker issues

**Import Organization:**

**Order:**
1. Standard library imports (e.g., `import os`, `from pathlib import Path`)
2. Third-party imports (e.g., `import pandas as pd`, `import numpy as np`, `import pytest`)
3. Local imports (e.g., `from f1d.shared.config import ProjectConfig`)

**Path Aliases:**
- `from pathlib import Path` - Use Path objects throughout
- Absolute paths via module resolution: `Path(__file__).parent.parent.parent.parent / "config"`

**Type Annotations:**
- Return type hints: `-> ReturnType` pattern
- Parameter types: `param_name: Type` pattern
- Union types: `Union[str, int, None]` or `str | int | None` (Python 3.10+)
- Optional: `Optional[Type]` used for nullable parameters

## Error Handling

**Custom Exceptions:**
- `PathValidationError`: Raised when path validation fails
- `OutputResolutionError`: Raised when output directory resolution fails
- `DataValidationError`: Raised when input data schema validation fails
- `FinancialCalculationError`: Raised when financial calculations fail due to missing data
- `RegressionValidationError`: Raised when regression input validation fails
- `ConfigError`: Raised when configuration loading/validation fails
- `WeakInstrumentError`: Raised when IV regression instruments are weak

**Error Handling Patterns:**

**Validate-then-process:**
```python
# Check input validity first
if must_exist and not path.exists():
    raise PathValidationError(f"Path does not exist: {path}")

# Process only if valid
result = process_path(path)
```

**Specific error messages:**
```python
# Include context in error messages
raise DataValidationError(
    f"Cannot calculate firm controls: missing gvkey in row. "
    f"Row columns: {list(row.index)}. "
    f"Year: {year}"
)
```

**Graceful handling:**
- Return `np.nan` for invalid calculations (e.g., dividing by zero, log of negative)
- Use `pd.notna()` and `.fillna()` for missing data handling
- Check for optional dependencies with try/except ImportError

**Logging errors:**
- Structlog configured via `f1d.shared.logging`
- Error messages logged with context
- Warnings for non-critical issues

## Logging

**Framework:** structlog
- Configured in `src/f1d/shared/logging/` module
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Structured logging with context keys

**Patterns:**
```python
# Log processing steps
print(f"Processing {step_name}")
print(f"  After filter: {len(df):,} / {initial_n:,}")

# Log errors with context
import warnings
warnings.warn(f"Missing columns: {missing}", stacklevel=2)
```

**Dual logging:**
- `DualWriter` class writes to both stdout and log file simultaneously
- Used in orchestrator scripts (e.g., `1.0_BuildSampleManifest.py`)

## Comments

**When to Comment:**
- Module docstrings with purpose, inputs, outputs, dependencies
- Function docstrings following Google/NumPy style
- Inline comments for complex calculations or business logic
- Section separators: `# =============================================================================`

**JSDoc/TSDoc:**
- **NOT used** - Python docstrings only
- Google style docstrings observed in shared modules
- NumPy style for mathematical functions

**Docstring Pattern:**
```python
"""
================================================================================
MODULE: Brief Description
================================================================================
ID: {module}/{name}
Description: {detailed description}

Inputs:
    - {input descriptions}

Outputs:
    - {output descriptions}

Deterministic: {true/false}
Main Functions:
    - {key functions}

Dependencies:
    - {dependencies description}

Author: {Author}
Date: {YYYY-MM-DD}
================================================================================
"""
```

## Function Design

**Size:**
- Functions typically 20-100 lines
- Long functions (100+ lines) for orchestration (e.g., `main()` in scripts)
- Helper functions kept concise (<50 lines)

**Parameters:**
- Type hints on all parameters
- Optional parameters with default values
- Configuration via keyword arguments

**Return Values:**
- Type hints on all return values
- Single return value (not multiple)
- Return dictionaries for complex results
- Return `None` for operations with side effects

**Validation in functions:**
```python
# Check parameters at function start
if input_file.suffix not in [".parquet", ".csv"]:
    raise ValueError(f"Unsupported file type: {input_file.suffix}")
```

## Module Design

**Exports:**
- `__init__.py` files mark packages
- Explicit imports in __init__ (e.g., `from f1d.shared.financial_utils import calculate_firm_controls`)
- Some __init__.py files are empty

**Barrel Files:**
- None observed - imports are explicit

**Module structure:**
- `src/f1d/{category}/` - Category-level modules
- `src/f1d/shared/` - Cross-cutting utilities
- `src/f1d/shared/config/` - Configuration sub-module
- `src/f1d/shared/logging/` - Logging sub-module
- `src/f1d/shared/observability/` - Observability sub-module

**Module docstring headers:**
- Standardized header with module ID, description, inputs, outputs, deterministic flag
- Dependencies listed explicitly
- Author and date included

---

*Convention analysis: 2026-02-14*
