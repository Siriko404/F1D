# Coding Conventions

**Analysis Date:** 2026-02-12

## Naming Patterns

**Files:**
- Scripts use numbered prefixes for execution order: `{step}_{substep}_{Description}.py`
  - Examples: `1.1_CleanMetadata.py`, `4.1_H1CashHoldingsRegression.py`
- Shared modules use snake_case: `financial_utils.py`, `panel_ols.py`
- Test files use `test_{module_name}.py` pattern: `test_panel_ols.py`
- Module packages use underscore: `shared/observability/logging.py`

**Functions:**
- Snake_case for all functions: `calculate_firm_controls()`, `run_panel_ols()`
- Private helper functions prefixed with underscore: `_check_thin_cells()`, `_format_coefficient_table()`
- Descriptive verb-noun pattern: `compute_financial_features()`, `validate_input_file()`

**Variables:**
- Snake_case for local variables: `sample_panel_data`, `expected_keys`
- UPPER_CASE for module-level constants: `UNCERTAINTY_MEASURES`, `CONTROL_VARS`
- Single underscore for temporarily unused variables in loops: `for _gvkey, group in df.groupby()`

**Types:**
- PascalCase for classes: `DualWriter`, `CollinearityError`
- PascalCase for custom exceptions: `FinancialCalculationError`, `DataValidationError`
- Type hints using standard library `typing`: `List[str]`, `Dict[str, Any]`, `Optional[Path]`

## Code Style

**Formatting:**
- Ruff formatter (line length 88, indent-width 4)
- Double quotes for strings: `quote-style = "double"`
- Space indentation (not tabs): `indent-style = "space"`
- Target Python 3.9: `target-version = "py39"`

**Linting:**
- Ruff with rules: E4, E7, E9, F (Pyflakes), B (flake8-bugbear), W (pycodestyle warnings), I (isort)
- E501 (line length) ignored - handled by formatter
- E402 (import violations) ignored in `__init__.py`
- S101 (assert) allowed in test files

## Import Organization

**Order:**
1. Standard library imports (argparse, json, sys, time, pathlib)
2. Third-party imports (numpy, pandas, pytest)
3. Local/shared module imports (from shared.xxx import yyy)

**Path Setup:**
All scripts add parent directory to sys.path for shared module imports:
```python
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir))
```

**Path Aliases:**
- No path aliases configured
- Use explicit imports: `from shared.panel_ols import run_panel_ols`
- For subpackages: `from shared.observability import DualWriter`

## Error Handling

**Custom Exceptions:**
Define domain-specific exceptions in relevant modules:
```python
# In shared/data_validation.py
class DataValidationError(Exception):
    """Raised when input data validation fails."""
    pass

class FinancialCalculationError(Exception):
    """Raised when financial metric calculation fails due to missing or invalid data."""
    pass

# In shared/panel_ols.py
class CollinearityError(Exception):
    """Raised when perfect collinearity is detected in the design matrix."""
    pass

class MulticollinearityError(Exception):
    """Raised when VIF threshold is exceeded (high multicollinearity)."""
    pass
```

**Exception Usage Guidance:**
- `FinancialCalculationError`: Use for financial calculation failures (missing gvkey, no data found)
- `DataValidationError`: Use for input data validation failures (schema violations, invalid values)
- `CollinearityError`: Use for regression design matrix issues
- `PathValidationError`: Use for path/file validation failures

**Error Messages:**
Include context in error messages:
```python
raise FinancialCalculationError(
    f"Cannot calculate firm controls: missing gvkey in row. "
    f"Row columns: {list(row.index)}. "
    f"Year: {year}"
)
```

**Fail-Fast Pattern:**
Do not silently catch and drop data. Let exceptions propagate:
```python
# CORRECT: Let FinancialCalculationError propagate
controls = calculate_firm_controls(row, compustat_df, year)
if controls:
    row_dict.update(controls)

# INCORRECT: Silently swallowing errors
try:
    controls = calculate_firm_controls(row, compustat_df, year)
except FinancialCalculationError:
    pass  # Don't do this - errors should propagate
```

## Logging

**Framework:** Python `logging` module with custom `DualWriter` class

**DualWriter Pattern:**
All scripts use DualWriter for simultaneous terminal and file output:
```python
from shared.observability_utils import DualWriter

log_path = output_dir / f"{timestamp}_script.log"
dual_writer = DualWriter(log_path)
sys.stdout = dual_writer

# ... script execution ...

dual_writer.close()
```

**When to Log:**
- Script start/end with timestamp
- Input file validation
- Key processing milestones (rows processed, files written)
- Warnings for data quality issues
- Error conditions with full context

**Statistics Output:**
Use `save_stats()` from observability utils to write `stats.json`:
```python
from shared.observability_utils import save_stats

stats = {
    "input_rows": len(df),
    "output_rows": len(result_df),
    "execution_time_seconds": elapsed,
    "timestamp": datetime.now().isoformat(),
}
save_stats(stats, output_dir)
```

## Comments

**Module Docstrings:**
All modules use a standardized header format:
```python
#!/usr/bin/env python3
"""
================================================================================
SHARED MODULE: Financial Utilities
================================================================================
ID: shared/financial_utils
Description: Provides common financial metrics and control variable
             calculations from Compustat data. Handles missing data gracefully
             with NaN values.

Inputs:
    - pandas DataFrame with firm identifiers (gvkey, datadate)
    - Compustat DataFrame with firm metrics
    - Fiscal year for data selection

Outputs:
    - Dictionary with firm-level control variables
    - DataFrame with computed financial features

Deterministic: true
Main Functions:
    - calculate_firm_controls(): Compute firm-level controls
    - compute_financial_features(): Batch processing wrapper

Dependencies:
    - Utility module for financial calculations
    - Uses: pandas, numpy

Author: Thesis Author
Date: 2026-02-11
================================================================================
"""
```

**Function Docstrings:**
Use Google-style docstrings with Args, Returns, Raises, Example:
```python
def run_panel_ols(
    df: pd.DataFrame,
    dependent: str,
    exog: List[str],
    entity_col: str = "gvkey",
    ...
) -> Dict[str, Any]:
    """
    Run panel OLS regression with fixed effects and clustered standard errors.

    Args:
        df: DataFrame with panel data. Must contain entity_col, time_col, and
            all variables in dependent + exog.
        dependent: Name of the dependent variable column.
        exog: List of independent/exogenous variable column names.
        entity_col: Column name for entity identifier (default 'gvkey').

    Returns:
        Dictionary with:
            - 'model': Fitted PanelOLS model object
            - 'coefficients': DataFrame with beta, SE, t-stat, p-value
            - 'summary': Dict with R2, adj_R2, N, F-stat
            - 'warnings': List of warning messages

    Raises:
        ImportError: If linearmodels is not available
        ValueError: If required columns are missing
        CollinearityError: If perfect collinearity detected

    Example:
        >>> result = run_panel_ols(
        ...     df=df,
        ...     dependent='cash_ratio',
        ...     exog=['vagueness', 'size'],
        ... )
    """
```

**When to Comment:**
- All public functions require docstrings
- Complex algorithms need inline explanation
- Non-obvious data transformations require comments
- Workarounds and technical debt need TODO/FIXME markers

**JSDoc/TSDoc:**
Not applicable (Python codebase). Use Google-style Python docstrings.

## Function Design

**Size:**
- Functions should be small enough to fit on one screen (approximately 30-50 lines)
- Extract complex logic into helper functions with underscore prefix

**Parameters:**
- Group related parameters into dictionaries/config objects when >5 params
- Use keyword arguments for optional parameters with sensible defaults
- Type hints required for all parameters

```python
def run_panel_ols(
    df: pd.DataFrame,
    dependent: str,
    exog: List[str],
    entity_col: str = "gvkey",
    time_col: str = "year",
    industry_col: str = "ff48_code",
    entity_effects: bool = True,
    time_effects: bool = True,
) -> Dict[str, Any]:
```

**Return Values:**
- Return dictionaries for complex results with multiple pieces of data
- Return DataFrames for data transformations
- Return tuples only for 2-3 closely related values
- Always document return structure in docstring

## Module Design

**Exports:**
Define explicit `__all__` lists in all modules:
```python
__all__ = [
    "run_panel_ols",
    "CollinearityError",
    "MulticollinearityError",
]
```

**Barrel Files:**
Use `__init__.py` for package-level re-exports:
```python
# shared/__init__.py
from .centering import center_continuous, create_interaction
from .panel_ols import run_panel_ols

__all__ = [
    "run_panel_ols",
    "center_continuous",
    "create_interaction",
]
```

**Deprecation Pattern:**
When moving functionality to subpackages, leave backward-compatible re-exports:
```python
# shared/observability_utils.py (deprecated)
"""
[DEPRECATED] Provides backward compatibility for existing imports.
Please update your imports to use the new package structure:
    OLD: from shared.observability_utils import DualWriter
    NEW: from shared.observability import DualWriter
"""
from shared.observability import DualWriter, save_stats, ...
```

## Type Annotations

**Requirements:**
- Use Python 3.9+ type hint syntax (no `typing.List` needed, use `list`)
- Import from `typing` for complex types: `Optional`, `Union`, `Dict`, `Any`
- Use `TYPE_CHECKING` block for forward references

**Mypy Configuration:**
- Python version 3.9
- `warn_return_any = true`
- `check_untyped_defs = true`
- Strict mode enabled for new modules: `shared.observability.*`

**Example:**
```python
from typing import Any, Dict, List, Optional, Tuple

def calculate_firm_controls(
    row: pd.Series,
    compustat_df: pd.DataFrame,
    year: int
) -> Dict[str, Union[float, int, None]]:
    ...
```

## Configuration

**Environment:**
- Config loaded from `config/project.yaml`
- Git commit SHA captured for reproducibility
- Timestamp format: `YYYY-MM-DD_HHMMSS`

**Output Directories:**
- Use `ensure_output_dir()` from `shared.path_utils`
- Follow pattern: `4_Outputs/{step_name}/{timestamp}/`
- Create `latest` symlink or copy for most recent output

---

*Convention analysis: 2026-02-12*
