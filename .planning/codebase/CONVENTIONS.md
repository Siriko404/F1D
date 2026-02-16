# Coding Conventions

**Analysis Date:** 2026-02-15

## Naming Patterns

**Files:**
- Use `snake_case` for all Python source files: `financial_utils.py`, `data_validation.py`, `path_utils.py`
- Test files use `test_` prefix: `test_financial_utils.py`, `test_data_validation.py`
- Stage scripts use numbered naming: `1.0_BuildSampleManifest.py`, `3.1_H1Variables.py`, `4.1_H1CashHoldingsRegression.py`
- Versioned modules use `v1/`, `v2/` subdirectories: `src/f1d/financial/v1/`, `src/f1d/econometric/v2/`
- Private functions use `_prefix`: `_check_thin_cells()`, `_format_star()`, `_add_constant_to_dataframe()`

**Functions:**
- Use `snake_case` for function names: `calculate_firm_controls()`, `compute_financial_features()`, `validate_dataframe_schema()`
- Private/implementation functions use `_prefix`: `_check_thin_cells()`, `_format_number()`

**Variables:**
- Use `snake_case` for variables: `gvkey`, `fyear`, `compustat_df`
- Constants use `UPPER_SNAKE_CASE`: `INPUT_SCHEMAS`, `LINEARMODELS_AVAILABLE`, `DATA_RAW`

**Types:**
- Use `PascalCase` for class names: `DataValidationError`, `FinancialCalculationError`, `PathValidationError`
- Exception classes end with `Error`: `MulticollinearityError`, `WeakInstrumentError`, `OutputResolutionError`

## Code Style

**Formatting:**
- Tool: Ruff (configured in `pyproject.toml`)
- Line length: 88 characters
- Indentation: 4 spaces (no tabs)
- Quote style: Double quotes for strings

**Linting:**
- Tool: Ruff (configured in `pyproject.toml`)
- Enabled rules: E, W, F, I, B, C4, UP, ARG, SIM (pycodestyle, pyflakes, isort, flake8-bugbear, flake8-comprehensions, pyupgrade, flake8-unused-arguments, flake8-simplify)
- Ignored rules: E501 (line too long, handled by formatter), B008 (function calls in argument defaults)
- Per-file ignores: `__init__.py` allows import violations/unused imports

**Type Checking:**
- Tool: mypy (configured in `pyproject.toml`)
- Tier 1 (shared modules): Strict mode (`strict = true`)
- Tier 2 (stage modules): Moderate mode (allow untyped definitions)
- Third-party libraries: Ignore missing imports (pandas, numpy, statsmodels, linearmodels, scipy, pyarrow)

## Import Organization

**Order:**
1. Standard library imports
2. Third-party library imports
3. Local/F1D imports (from `f1d.shared`, `f1d.sample`, etc.)

**Path Aliases:**
- Use `pathlib.Path` for all file operations
- Resolve paths using `.resolve()` for absolute paths
- Use `from f1d.shared import` for shared utilities

**Example:**
```python
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from f1d.shared.observability_utils import DualWriter
from f1d.shared.path_utils import ensure_output_dir, get_latest_output_dir
```

## Error Handling

**Patterns:**
- Custom exceptions for domain-specific errors: `FinancialCalculationError`, `DataValidationError`, `PathValidationError`, `WeakInstrumentError`
- Exceptions include descriptive messages with context: `f"Cannot calculate firm controls: missing gvkey in row. Row columns: {list(row.index)}. Year: {year}"`
- Handle missing data gracefully with `np.nan` return values
- Use optional imports with availability flags: `LINEARMODELS_AVAILABLE`, `STATSMODELS_AVAILABLE`

**Custom Exceptions:**
- `DataValidationError`: Schema validation failures
- `FinancialCalculationError`: Financial calculation failures (missing gvkey, no data found)
- `PathValidationError`: Path validation failures
- `OutputResolutionError`: Output directory resolution failures
- `CollinearityError`: Perfect collinearity in design matrix
- `MulticollinearityError`: High VIF values detected
- `WeakInstrumentError`: First-stage F-stat below threshold

## Logging

**Framework:** structlog (configured in `pyproject.toml`)

**Patterns:**
- Use `logger = logging.getLogger(__name__)` at module level
- Use `DualWriter` class for dual stdout/file logging in scripts
- Import `from f1d.shared.observability_utils import DualWriter` for dual-writer functionality

**DualWriter Pattern:**
```python
from f1d.shared.observability_utils import DualWriter
from pathlib import Path

# Initialize dual-writer
writer = DualWriter(log_path=Path("3_Logs/script.log"))
# Redirect stdout
sys.stdout = writer
# All output goes to both terminal and file
print("Processing...")
# Restore original stdout
writer.close()
```

## Comments

**When to Comment:**
- Explain financial formulas and Compustat variable mappings
- Document data structure transformations
- Clarify complex pandas operations
- Note edge cases and workarounds

**JSDoc/TSDoc:**
- Use Google-style docstrings for functions
- Include `Args:`, `Returns:`, `Raises:` sections
- Include `Example:` for complex functions

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
        FinancialCalculationError: If gvkey is missing or Compustat data not found for year
    """
```

## Function Design

**Size:** Functions typically 20-100 lines. Complex functions (e.g., `run_panel_ols()`) may be longer but follow single responsibility.

**Parameters:**
- Use type hints for all parameters and return values
- Use `Optional[T]` for nullable parameters
- Use default values for optional parameters: `cov_type: str = "HC1"`, `cluster_col: Optional[str] = None`

**Return Values:**
- Functions return single typed values: `Dict[str, Union[float, int, None]]`, `pd.DataFrame`, `pd.Series`
- Error cases raise exceptions rather than returning error codes
- Missing data returns `np.nan` for numerical values

## Module Design

**Exports:**
- Use `__all__` in `__init__.py` to define public API
- `__all__` lists exported functions/classes: `["DualWriter", "parse_ff_industries", "run_panel_ols"]`

**Barrel Files:**
- `src/f1d/shared/__init__.py`: Exports core shared utilities
- `src/f1d/__init__.py`: Package-level exports

**Module Documentation:**
- Include header block with module ID, description, inputs, outputs, determinism, main functions, dependencies, author, date
- Header uses 80-character border lines

**Module Header Pattern:**
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
    -  Various financial calculation utilities

Dependencies:
    - Utility module for financial calculations
    - Uses: pandas, numpy

Author: Thesis Author
Date: 2026-02-11
================================================================================
"""
```

## Configuration Patterns

**YAML Configuration:**
- Use `project.yaml` for project-wide configuration
- Load with `yaml.safe_load()`
- Use pydantic settings for typed configuration with validation

**Environment Variables:**
- Use `F1D_*` prefix for environment variable overrides
- Use `pydantic-settings` for environment variable loading

---

*Convention analysis: 2026-02-15*
