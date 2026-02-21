# Coding Conventions

**Analysis Date:** 2026-02-21

## Naming Patterns

**Files:**
- Source modules: `snake_case.py` (e.g., `financial_utils.py`, `path_utils.py`)
- Test files: `test_<module_name>.py` (e.g., `test_financial_utils.py`)
- Panel builders: `build_h<#>_<name>_panel.py` (e.g., `build_h1_cash_holdings_panel.py`)
- Econometric runners: `run_h<#>_<name>.py` (e.g., `run_h1_cash_holdings.py`)
- Stage scripts: `<stage>.<step>_<Name>.py` (e.g., `1.1_CleanMetadata.py`)

**Functions:**
- Use `snake_case` for all function names
- Factory fixtures: `<name>_factory` (e.g., `sample_compustat_factory`)
- Boolean functions: Use `is_`, `has_`, `can_` prefixes (e.g., `is_valid_timestamp`)
- Computation functions: Use verb prefixes (e.g., `calculate_firm_controls`, `compute_financial_features`)

**Variables:**
- Use `snake_case` for all variables
- Compustat variables preserve original naming (e.g., `gvkey`, `fyear`, `at`, `dlc`, `dltt`)
- Control variables use descriptive names (e.g., `size`, `leverage`, `profitability`)

**Types:**
- Use `PascalCase` for class names
- Exception classes: `<Purpose>Error` (e.g., `FinancialCalculationError`, `DataValidationError`)
- Use `typing` module imports for type hints

## Code Style

**Formatting:**
- Formatter: Ruff (configured in `pyproject.toml`)
- Line length: 88 characters (Black default)
- Indent: 4 spaces
- Quote style: double quotes
- Target Python version: 3.9+

**Linting:**
- Linter: Ruff with extended rule set
- Enabled rules: E, W, F, I, B, C4, UP, ARG, SIM
- Ignored rules: E501 (line too long), B008 (function calls in defaults)

**Key linting configurations from `pyproject.toml`:**
```toml
[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP", "ARG", "SIM"]
ignore = ["E501", "B008"]
fixable = ["ALL"]
```

## Import Organization

**Order:**
1. Standard library imports (e.g., `os`, `sys`, `pathlib`, `typing`)
2. Third-party imports (e.g., `pandas`, `numpy`, `pytest`)
3. Local imports from `f1d.shared.*`

**Path Aliases:**
- Use `f1d.shared.*` namespace for all shared imports
- Example: `from f1d.shared.financial_utils import calculate_firm_controls`

**Import pattern:**
```python
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
import pytest

from f1d.shared.financial_utils import calculate_firm_controls
from f1d.shared.data_validation import FinancialCalculationError
```

**Forbidden patterns:**
- Do NOT use `sys.path.insert()` or `sys.path.append()` - use proper `f1d.shared.*` imports

## Error Handling

**Exception Hierarchy:**
- `FinancialCalculationError`: Financial calculation failures (missing gvkey, no data found)
- `DataValidationError`: Input data validation failures (schema violations, invalid values)
- `PathValidationError`: Path validation failures
- `OutputResolutionError`: Output directory resolution failures

**Raising exceptions:**
```python
def calculate_firm_controls(row: pd.Series, compustat_df: pd.DataFrame, year: int):
    gvkey = row.get("gvkey")
    if gvkey is None:
        raise FinancialCalculationError(
            f"Cannot calculate firm controls: missing gvkey in row. "
            f"Row columns: {list(row.index)}. "
            f"Year: {year}"
        )
```

**Error messages:**
- Include context in error messages (what failed, what was expected, what was found)
- Include relevant identifiers (gvkey, year, file path)
- Use multi-line f-strings for complex messages

**NaN handling:**
- Return `np.nan` for invalid computations rather than raising exceptions for expected edge cases
- Example: Zero or negative assets return `np.nan` for log calculations

## Logging

**Framework:** structlog (configured via `pyproject.toml`)

**Logging patterns:**
```python
import structlog
logger = structlog.get_logger()

logger.info("Processing financial data", gvkey=gvkey, year=year)
logger.warning("Missing R&D data, treating as zero", gvkey=gvkey)
logger.error("Failed to load data", file_path=str(path), error=str(e))
```

**Console output for validation:**
- Use `print()` for validation success messages
- Use `print(..., file=sys.stderr)` for warnings in non-strict mode

## Comments

**When to Comment:**
- Module-level docstrings are required for all source files
- Function docstrings for all public functions
- Inline comments for non-obvious logic (e.g., winsorization, lag calculations)

**Docstring format:**
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
        FinancialCalculationError: If gvkey is missing or Compustat data not found for year
    """
```

**Module docstring format:**
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

Outputs:
    - Dictionary with firm-level control variables

Deterministic: true

Author: Thesis Author
Date: 2026-02-11
================================================================================
"""
```

## Function Design

**Size:** Keep functions focused on a single responsibility. Complex functions should be decomposed.

**Parameters:**
- Use type hints for all parameters
- Use `Optional[T]` for optional parameters
- Use `Callable[..., T]` for factory fixtures that return callables

**Return Values:**
- Use typed return annotations
- Return `Dict[str, Union[float, int, None]]` for financial calculations
- Return `pd.DataFrame` for data transformation functions

**Example pattern:**
```python
def compute_financial_controls_quarterly(
    compustat_df: pd.DataFrame,
    winsorize: bool = True,
) -> pd.DataFrame:
    """
    Compute quarterly financial controls for all firms.
    
    Vectorized calculation using quarterly Compustat variables.
    """
```

## Module Design

**Exports:**
- Define `__all__` in `__init__.py` for public API
- Re-export commonly used functions from shared modules

**Example from `src/f1d/shared/__init__.py`:**
```python
from f1d.shared.financial_utils import calculate_firm_controls
from f1d.shared.path_utils import get_latest_output_dir

__all__ = [
    "calculate_firm_controls",
    "get_latest_output_dir",
    # ...
]
```

**Barrel Files:**
- Use `__init__.py` to re-export public API
- Keep imports explicit and documented

## Type Checking

**Configuration:**
- mypy strict mode for `f1d.shared.*` modules (Tier 1)
- Moderate mode for stage-specific modules (Tier 2)
- Target Python 3.9

**Tier 1 (strict mode) - `src/f1d/shared/`:**
```toml
[[tool.mypy.overrides]]
module = ["f1d.shared.*"]
strict = true
```

**Tier 2 (moderate mode) - stage modules:**
```toml
[[tool.mypy.overrides]]
module = [
    "f1d.sample.*",
    "f1d.text.*",
    "f1d.financial.*",
    "f1d.econometric.*",
]
disallow_untyped_defs = false
allow_untyped_defs = true
```

**Type stubs installed:**
- `pandas-stubs>=2.2.0`
- `types-psutil>=6.0.0`
- `types-requests>=2.31.0`
- `types-PyYAML>=6.0.0`

---

*Convention analysis: 2026-02-21*
