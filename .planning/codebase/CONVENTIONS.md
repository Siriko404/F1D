# Coding Conventions

**Analysis Date:** 2026-02-21

## Naming Patterns

**Files:**
- Modules: `snake_case.py` (e.g., `chunked_reader.py`, `financial_utils.py`)
- Tests: `test_*.py` or `*_test.py` (e.g., `test_config.py`, `test_h1_regression.py`)
- Factories: `*_factory.py` in `tests/factories/` (e.g., `financial.py` for `sample_compustat_factory`)

**Functions:**
- snake_case: `read_in_chunks`, `calculate_firm_controls`, `validate_dataframe_schema`
- Public API functions start with verb: `get_`, `load_`, `compute_`, `calculate_`, `validate_`, `run_`

**Variables:**
- snake_case: `gvkey`, `fyear`, `year_start`, `max_memory_percent`
- DataFrame variables: `df`, `df_work`, `compustat_df`, `sample`
- Constants: UPPER_SNAKE_CASE: `INPUT_SCHEMAS`, `LINEARMODELS_AVAILABLE`, `TIMESTAMP_PATTERN`

**Types:**
- Classes: PascalCase: `DataSettings`, `LoggingSettings`, `MemoryAwareThrottler`, `ProjectConfig`
- Exceptions: PascalCase with `Error` suffix: `DataValidationError`, `FinancialCalculationError`, `CollinearityError`, `OutputResolutionError`, `PathValidationError`
- Type aliases: PascalCase or ALL_CAPS: `Path`, `Callable`, `F` (TypeVar)

## Code Style

**Formatting:**
- Tool: ruff (combined linter and formatter)
- Line length: 88 characters (configured in `pyproject.toml`)
- Indent width: 4 spaces
- Quote style: Double quotes for strings (`"hello"`)
- Trailing commas: Used for consistency in multi-line structures

**Linting:**
- Tool: ruff
- Enabled rules: E (pycodestyle errors), W (pycodestyle warnings), F (pyflakes), I (isort), B (flake8-bugbear), C4 (flake8-comprehensions), UP (pyupgrade), ARG (flake8-unused-arguments), SIM (flake8-simplify)
- Config: `pyproject.toml` `[tool.ruff.lint]`
- Per-file ignores: `__init__.py` allows E402, F401; `2_Scripts/**` ignores all; `tests/**` allows S101 (assert), ARG (unused fixtures)

## Import Organization

**Order:**
1. Standard library imports
2. Third-party imports
3. Local imports (`from f1d...`)

**Pattern from `src/f1d/shared/chunked_reader.py`:**
```python
import logging
import time
from functools import wraps
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    TypeVar,
    Union,
    cast,
    overload,
)

import pandas as pd
import psutil
import pyarrow as pa
import pyarrow.parquet as pq
import yaml
```

**Type imports:**
- `from __future__ import annotations` at top for Python 3.9+ forward compatibility
- Use `from typing import` for standard types
- Use `cast()` from typing when type inference needs help

**Conditional imports:**
- Pattern for optional dependencies (linearmodels, scipy, etc.):
```python
try:
    from linearmodels.panel.model import PanelOLS
    LINEARMODELS_AVAILABLE = True
except ImportError:
    PanelOLS = None  # type: ignore[misc,assignment]
    LINEARMODELS_AVAILABLE = False
```

**Path Aliases:**
- No explicit path aliases configured in `pyproject.toml`
- Imports use `from f1d.shared.module import function`
- `src-layout` is enforced: `src/f1d/` is the package root

## Error Handling

**Patterns:**
- Custom exceptions defined per module with clear intent
- Raise specific exceptions, not generic `Exception`
- Use descriptive error messages with context

**Custom Exceptions (from `src/f1d/shared/`):**
- `DataValidationError`: Input data validation failures (`src/f1d/shared/data_validation.py`)
- `FinancialCalculationError`: Financial calculation failures (missing gvkey, no data)
- `CollinearityError`: Perfect multicollinearity in regression (`src/f1d/shared/panel_ols.py`, `src/f1d/shared/diagnostics.py`)
- `MulticollinearityError`: High VIF threshold exceeded
- `EnvValidationError`: Environment variable validation errors (`src/f1d/shared/env_validation.py`)
- `WeakInstrumentError`: IV regression instrument weakness (`src/f1d/shared/iv_regression.py`)
- `PathValidationError`: Path validation failures (`src/f1d/shared/path_utils.py`)
- `OutputResolutionError`: Output directory resolution failures
- `RegressionValidationError`: Regression validation errors (`src/f1d/shared/regression_validation.py`)

**Exception Usage Pattern:**
```python
# Check for specific error conditions and raise with context
if gvkey is None:
    raise FinancialCalculationError(
        f"Cannot calculate firm controls: missing gvkey in row. "
        f"Row columns: {list(row.index)}. "
        f"Year: {year}"
    )

# Raise and catch specific exceptions in tests
with pytest.raises(FinancialCalculationError, match="GVKEY"):
    raise FinancialCalculationError(msg)
```

**No bare except:**
- Bare `except:` is prohibited
- Always specify exception types
- Use `finally` for cleanup

## Logging

**Framework:** Python standard library `logging`

**Patterns:**
- Module-level logger: `logger = logging.getLogger(__name__)`
- Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Structlog configured via `pyproject.toml` logging settings

**Example from `src/f1d/shared/chunked_reader.py`:**
```python
import logging
logger = logging.getLogger(__name__)

# Logging in functions
logger.debug(f"Could not load chunk processing config, using defaults: {e}")
logger.warning(f"Unexpected error reading parquet metadata: {type(e).__name__}: {e}")
logger.info(f"Memory status for {operation_name}: ...")
```

**Console output for regression results:**
- Use `print()` for formatted regression output (`_format_coefficient_table` in `src/f1d/shared/panel_ols.py`)
- Use `warnings.warn()` for warnings

## Comments

**When to Comment:**
- Explain non-obvious business logic
- Document algorithm choices
- Note limitations or workarounds
- Reference related standards/PHASE numbers

**Module headers:**
- Standardized format in all shared modules:
```python
#!/usr/bin/env python3
"""
================================================================================
SHARED MODULE: [Module Name]
================================================================================
ID: shared/[module_id]
Description: [One-line summary]

Purpose: [Purpose description]

Inputs:
    - [Input descriptions]

Outputs:
    - [Output descriptions]

Deterministic: true/false
Main Functions:
    - [Function names]

Dependencies:
    - Utility module for [purpose]
    - Uses: [libraries]

Author: Thesis Author
Date: 2026-02-11
================================================================================
"""
```

**Inline comments:**
- Used sparingly, only when code is not self-explanatory
- Prefer clear variable names over explanatory comments

**JSDoc/TSDoc:**
- Not used (Python codebase)
- Google-style docstrings used instead (see CODE_QUALITY_STANDARD.md)

## Function Design

**Size:**
- No strict line limit enforced
- Functions should be focused on single responsibility
- Complex functions split into helper functions (e.g., `_check_thin_cells`, `_format_coefficient_table`)

**Parameters:**
- Positional args first, then keyword args
- Use `Optional[Type]` for nullable parameters
- Provide defaults where appropriate
- Type hints required for all parameters

**Return Values:**
- Always typed with `-> ReturnType`
- Returns `Dict[str, Any]` for complex outputs from analysis functions
- Return tuples for multiple related values

**Example signature pattern:**
```python
def read_in_chunks(
    file_path: Path,
    columns: Optional[List[str]] = None,
    chunk_size: Optional[int] = None,
) -> Iterator[pd.DataFrame]:
    """Read Parquet file in chunks using PyArrow row groups.

    Args:
        file_path: Path to Parquet file
        columns: List of columns to read (None = all columns)
        chunk_size: Number of rows per chunk (None = use row groups)

    Yields:
        DataFrame chunks
    """
```

## Module Design

**Exports:**
- `__all__` lists public API symbols
- Pattern from `src/f1d/shared/__init__.py`:
```python
__all__ = [
    "DualWriter",
    "parse_ff_industries",
    "load_variable_descriptions",
    "get_latest_output_dir",
    "OutputResolutionError",
    # Econometric utilities
    "run_panel_ols",
    "center_continuous",
    "create_interaction",
    "compute_vif",
    "check_multicollinearity",
]
```

**Barrel Files:**
- `src/f1d/shared/__init__.py`: Main shared module exports
- `tests/factories/__init__.py`: Test fixture exports
- Not heavily used elsewhere - direct imports preferred

**Module organization (from `src/f1d/shared/`):**
- `config/`: Configuration loading and validation
- Data handling: `chunked_reader.py`, `data_loading.py`, `data_validation.py`
- Financial: `financial_utils.py`
- Econometric: `panel_ols.py`, `iv_regression.py`, `regression_helpers.py`
- Utilities: `path_utils.py`, `centering.py`, `diagnostics.py`

---

*Convention analysis: 2026-02-21*
