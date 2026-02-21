# Coding Conventions

**Analysis Date:** 2026-02-20

## Naming Patterns

**Files:**
- Use `snake_case` for module names: `financial_utils.py`, `data_validation.py`
- Test files use `test_` prefix: `test_financial_utils.py`, `test_panel_ols.py`
- Submodules use single underscore prefix for internal modules: `_crsp_engine.py`

**Functions:**
- Use `snake_case` for function names: `calculate_firm_controls()`, `validate_dataframe_schema()`
- Factory fixtures include `_factory` suffix: `sample_compustat_factory()`
- Boolean-returning functions use `is_`, `has_`, `can_` prefixes: `is_valid_timestamp()`

**Variables:**
- Use `snake_case` for variables: `compustat_df`, `firm_data`, `output_base`
- Constants use `UPPER_SNAKE_CASE`: `DATA_RAW`, `TIMESTAMP_PATTERN`, `INPUT_SCHEMAS`

**Types:**
- Use `PascalCase` for class names: `FinancialCalculationError`, `DualWriter`
- Exception classes end with `Error`: `DataValidationError`, `PathValidationError`
- Type aliases use `PascalCase`: `from typing import Callable, Dict, Any`

**Private/Internal:**
- Single underscore prefix for internal modules: `_crsp_engine.py`
- Double underscore for dunders only: `__init__.py`, `__all__`

## Code Style

**Formatting:**
- Ruff (v0.9.0) for both linting and formatting
- Line length: 88 characters (Black default)
- Indent: 4 spaces
- Quotes: Double quotes preferred
- Config: `pyproject.toml` `[tool.ruff]` section

**Linting:**
- Ruff with extended rule set: `E`, `W`, `F`, `I`, `B`, `C4`, `UP`, `ARG`, `SIM`
- Ignored rules: `E501` (line too long), `B008` (function call in argument defaults)
- Per-file ignores in `pyproject.toml`:
  - `__init__.py`: `E402`, `F401` (import violations, unused imports)
  - `tests/**`: `S101`, `ARG` (allow assert, unused fixtures)

**Type Checking:**
- mypy (v1.14.1) with tier-based strictness
- Tier 1 (shared modules): `strict = true` - full type annotations required
- Tier 2 (stage modules): relaxed mode - `disallow_untyped_defs = false`
- Run command: `mypy src/f1d/shared --config-file pyproject.toml`

## Import Organization

**Order:**
1. Standard library imports: `import sys`, `from pathlib import Path`
2. Third-party imports: `import pandas as pd`, `import numpy as np`
3. First-party imports: `from f1d.shared.data_validation import DataValidationError`
4. Local imports: `from . import logging as observability_logging`

**Path Aliases:**
- Known first-party: `f1d` (configured in `pyproject.toml` ruff.isort)
- No custom path aliases defined
- Use explicit imports: `from f1d.shared.path_utils import get_latest_output_dir`

**Import Style:**
```python
# Standard library
from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Optional, Union

# Third-party
import numpy as np
import pandas as pd
import pytest

# First-party
from f1d.shared.data_validation import FinancialCalculationError
```

## Error Handling

**Patterns:**
- Custom exception classes for domain-specific errors
- Raise exceptions with descriptive messages including context
- Use strict vs non-strict mode for validation failures

**Custom Exceptions:**
- `FinancialCalculationError`: Missing or invalid financial data
- `DataValidationError`: Schema validation failures
- `PathValidationError`: Path access/creation failures
- `OutputResolutionError`: Output directory resolution failures

**Exception Messages:**
Include full context in error messages:
```python
raise FinancialCalculationError(
    f"Cannot calculate firm controls: missing gvkey in row. "
    f"Row columns: {list(row.index)}. "
    f"Year: {year}"
)
```

**Validation Pattern:**
```python
def validate_dataframe_schema(df, schema_name, file_path, strict=True):
    if strict:
        raise DataValidationError(error_msg)
    else:
        print(f"WARNING: {error_msg}", file=sys.stderr)
```

## Logging

**Framework:** structlog (v25.0) + standard logging

**Configuration:**
- Config file: `pyproject.toml` logging section
- Module: `src/f1d/shared/logging/config.py`, `handlers.py`

**Logger Creation:**
```python
import logging
logger = logging.getLogger(__name__)
```

**Patterns:**
- Use module-level logger: `logger = logging.getLogger(__name__)`
- Dual output: stdout + file via `DualWriter`
- Structured logging with structlog for JSON output
- Console renderer for development, JSON for production

**Log Levels:**
- INFO: Normal operation progress
- WARNING: Non-critical issues, fallback behavior
- ERROR: Operation failures with context
- DEBUG: Detailed diagnostic information

**Example:**
```python
# Standard logging
logger = logging.getLogger(__name__)
logger.info(f"Validation passed: {file_path.name}")

# structlog (in logging/context.py)
import structlog
log = structlog.get_logger()
log.info("processing_started", stage="sample", records=len(df))
```

## Comments

**When to Comment:**
- Module-level docstrings explaining purpose, inputs, outputs
- Complex financial formulas with source references
- Non-obvious business logic decisions
- TODO/FIXME for known issues

**JSDoc/TSDoc:**
- Google-style docstrings for all public functions
- Include Args, Returns, Raises, Example sections

**Docstring Pattern:**
```python
def calculate_firm_controls(
    row: pd.Series, compustat_df: pd.DataFrame, year: int
) -> Dict[str, Union[float, int, None]]:
    """
    Calculate firm-level control variables from Compustat data.

    Args:
        row: DataFrame row with firm identifiers (gvkey, datadate)
        compustat_df: Compustat data with firm metrics
        year: Fiscal year for data selection

    Returns:
        Dictionary with: size (log assets), leverage, profitability,
        market_to_book, capex_intensity, r_intensity, dividend_payer

    Raises:
        FinancialCalculationError: If gvkey is missing or Compustat data not found
    """
```

**Module Header:**
```python
#!/usr/bin/env python3
"""
================================================================================
SHARED MODULE: Financial Utilities
================================================================================
ID: shared/financial_utils
Description: Provides common financial metrics and control variable
             calculations from Compustat data.

Inputs:
    - pandas DataFrame with firm identifiers (gvkey, datadate)
    - Compustat DataFrame with firm financial metrics

Outputs:
    - Dictionary with firm-level control variables
    - DataFrame with computed financial features

Deterministic: true
Main Functions:
    - calculate_firm_controls()
    - compute_financial_features()

Dependencies:
    - pandas, numpy

Author: Thesis Author
Date: 2026-02-11
================================================================================
"""
```

## Function Design

**Size:** Functions typically 10-50 lines; complex financial calculations may be longer

**Parameters:**
- Type hints required for Tier 1 (shared) modules
- Optional parameters with defaults last
- Use `Optional[T]` for nullable parameters

**Return Values:**
- Return `Dict` for multiple related values (control variables)
- Return `pd.DataFrame` for data transformations
- Return `None` or empty containers for edge cases (not raising)
- Use `np.nan` for invalid numeric calculations

**Pattern for Financial Calculations:**
```python
def calculate_metric(row: pd.Series, data: pd.DataFrame) -> float:
    """Calculate metric with graceful NaN handling."""
    if data.empty:
        return np.nan
    if row.get("required_field") is None:
        return np.nan
    return calculated_value
```

## Module Design

**Exports:**
- Define `__all__` in `__init__.py` for public API
- Re-export commonly used functions from parent package

**Barrel Files:**
Use `__init__.py` to re-export public API:
```python
# src/f1d/shared/__init__.py
from f1d.shared.panel_ols import run_panel_ols
from f1d.shared.path_utils import get_latest_output_dir

__all__ = [
    "run_panel_ols",
    "get_latest_output_dir",
]
```

**Package Structure:**
```
src/f1d/
├── __init__.py          # Public API exports
├── shared/              # Tier 1: Core utilities (strict typing)
│   ├── __init__.py
│   ├── variables/       # Financial variable calculations
│   ├── observability/   # Logging, monitoring
│   └── logging/         # Logging configuration
├── sample/              # Tier 2: Stage-specific (relaxed typing)
├── text/
├── financial/
└── econometric/
```

---

*Convention analysis: 2026-02-20*
