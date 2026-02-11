# Coding Conventions

**Analysis Date:** 2025-02-10

## Naming Patterns

**Files:**
- `snake_case.py` for all Python files
- Test files: `test_<module>.py` in `tests/unit/` or `tests/integration/`
- Edge case tests: `test_<module>_edge_cases.py`
- Script naming: `<major>.<minor>_DescriptiveName.py` (e.g., `3.1_H1Variables.py`)
- Shared utilities: `descriptive_name.py` in `2_Scripts/shared/`

**Functions:**
- `snake_case` for all functions
- Private/internal functions: `_leading_underscore` (e.g., `_check_missing_values`, `_assign_industry_codes`)
- Class methods: `snake_case` (not camelCase)
- Functions that compute: prefix with `compute_` (e.g., `compute_cash_holdings`, `compute_leverage`)
- Functions that validate: prefix with `validate_` (e.g., `validate_dataframe_schema`, `validate_columns`)

**Variables:**
- `snake_case` for all variables
- Constants: `UPPER_SNAKE_CASE` (e.g., `INPUT_SCHEMAS`, `ENV_SCHEMA`, `STATSMODELS_AVAILABLE`)
- DataFrames: `df` for generic, `result_<name>` for return values (e.g., `result = df.merge()`)
- Temporary loop variables: single letters or short names (e.g., `for gvkey, group in df.groupby()`)

**Types/Classes:**
- `PascalCase` for class names (rare - mostly exceptions in this codebase)
- Exception suffix: `Error` for custom exceptions (e.g., `DataValidationError`, `RegressionValidationError`, `PathValidationError`)

## Code Style

**Formatting:**
- Ruff is used for linting (`.ruff_cache/` present)
- No explicit `.ruff.toml` or `.pylintrc` - using Ruff defaults
- Line length appears to be standard (80-120 characters based on code)
- Indentation: 4 spaces (Python standard)

**Import Organization:**

Standard order observed in `2_Scripts/3_Financial_V2/3.1_H1Variables.py`:

```python
#!/usr/bin/env python3

# 1. Standard library imports (grouped)
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime
import hashlib
import json
import time

# 2. Third-party imports
import pandas as pd
import numpy as np
import yaml
import psutil

# 3. Local/application imports (absolute from 2_Scripts)
from shared.path_utils import (
    validate_output_path,
    ensure_output_dir,
)
from shared.observability_utils import (
    DualWriter,
    compute_file_checksum,
)
```

**Path Aliases:**
- No path aliases configured
- Use `from shared.<module> import <name>` for shared utilities
- Add to sys.path when needed: `sys.path.insert(0, str(Path(__file__).parent.parent))`

## Error Handling

**Patterns:**

1. **Custom Exceptions:**
```python
class DataValidationError(Exception):
    """Raised when input data validation fails."""
    pass

class RegressionValidationError(Exception):
    """Raised when regression input validation fails."""
    pass

class PathValidationError(Exception):
    """Raised when path validation fails."""
    pass
```

2. **Exception Raising:**
```python
# Clear, descriptive messages with context
raise RegressionValidationError(
    f"Missing required columns: {sorted(missing)}. "
    f"Available: {sorted(df.columns)}"
)

# Include what went wrong AND what was expected
raise DataValidationError(
    f"Validation failed for {file_path.name}:\n"
    f"  File: {file_path}\n"
    f"  Errors:\n    - " + "\n    - ".join(errors)
)
```

3. **Graceful Import Handling:**
```python
try:
    import statsmodels.formula.api as smf
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False

# Later check before use
if not STATSMODELS_AVAILABLE:
    raise ImportError("statsmodels required. Install: pip install statsmodels")
```

4. **Validation Functions Return or Raise:**
- Validation functions either return normally (success) or raise custom exception
- Use `strict` parameter to control behavior: `strict=True` raises, `strict=False` warns

## Logging

**Framework:** Custom `DualWriter` from `shared.observability_utils`

**Patterns:**

```python
# Setup logging to both file and terminal
from shared.observability_utils import DualWriter
dual_writer = DualWriter(log_file_path)
sys.stdout = dual_writer

# Print output goes to both destinations
print("=" * 60)
print("STEP 3.1: H1 Cash Holdings Variables")
print(f"Timestamp: {timestamp}")
print("=" * 60)

# Cleanup at end
dual_writer.close()
sys.stdout = dual_writer.terminal
```

**When to Log:**
- Section headers with `===` separators
- Progress updates with row counts: `print(f"  Loaded manifest: {len(df):,} calls")`
- Warnings to stderr: `print(f"WARNING: {message}", file=sys.stderr)`
- Statistics via helper: `print_stat("Manifest rows", value=len(manifest))`

**Helper Functions:**
- `print_stat(label, before/after/value, indent=2)` - formatted statistics
- `print_stats_summary(stats_dict)` - summary table from statistics dict
- `save_stats(stats_dict, output_dir)` - write `stats.json`

## Comments

**When to Comment:**
- Module-level docstrings explaining purpose, security notes, determinism
- Function docstrings with Args/Returns/Raises (Google style)
- Inline comments for non-obvious logic (financial formulas, data transformations)
- Section separators in scripts: `# ==============================================================================`

**Docstring Pattern:**

```python
def compute_cash_holdings(compustat_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Cash Holdings = CHE / AT

    Args:
        compustat_df: Compustat data with atq, cheq columns

    Returns:
        DataFrame with gvkey, fiscal_year, cash_holdings
    """
```

**Module Docstring Pattern:**

```python
#!/usr/bin/env python3
"""
================================================================================
SHARED MODULE: Regression Utilities
================================================================================
ID: shared/regression_utils
Description: Provides common fixed effects OLS regression patterns for
             econometric analysis. Handles statsmodels import errors gracefully
             and extracts CEO fixed effects and model diagnostics.

Inputs:
    - pandas DataFrame with regression data
    - statsmodels.formula.api (optional, raises ImportError if missing)

Outputs:
    - Fitted statsmodels OLS models
    - CEO fixed effects as pandas Series
    - Regression diagnostics as dictionary

Deterministic: true
================================================================================
"""
```

**JSDoc/TSDoc:**
- Not applicable (Python codebase)
- Use Google-style Python docstrings with Args/Returns/Raises sections

## Function Design

**Size:**
- Functions should be < 50 lines
- Split large computations into multiple helper functions
- Each function does one thing well

**Parameters:**
- Use type hints for all parameters: `df: pd.DataFrame`, `strict: bool = True`
- Optional parameters with sensible defaults
- DataFrames passed as first argument (method chaining style)

**Return Values:**
- Always return typed values: `-> pd.DataFrame`, `-> Dict[str, Any]`
- Return None for validation functions (raise on error)
- Return Series/DataFrame for data transformations
- Return dict for statistics/results

## Module Design

**Exports:**
- `__init__.py` in `shared/` defines explicit `__all__` list
- Re-export commonly used utilities at package level

**Barrel Files:**
- `2_Scripts/shared/__init__.py` acts as barrel for shared utilities
- Explicit exports: `DualWriter`, `parse_ff_industries`, `run_panel_ols`, etc.

**Shared Utilities Location:**
- `2_Scripts/shared/<module>.py` for reusable code
- Organized by purpose: `regression_utils.py`, `data_validation.py`, `path_utils.py`
- Import as: `from shared.<module> import <function>`

---

*Convention analysis: 2025-02-10*
