# Coding Conventions

**Analysis Date:** 2026-02-14

## Language and Version

**Primary:** Python 3.9+ - All new code targets Python 3.9 minimum

**Type Hints:** Required for all shared modules (Tier 1), optional for stage modules (Tier 2)

## Naming Patterns

**Files:**
- Shared modules: `snake_case.py` (e.g., `financial_utils.py`, `data_validation.py`)
- Stage scripts: `N.N_Description.py` (e.g., `1.0_BuildSampleManifest.py`, `3.1_FirmControls.py`)
- Test files: `test_<module_name>.py` (e.g., `test_financial_utils.py`)
- Config files: `snake_case.py` (e.g., `paths.py`, `env.py`)

**Functions:**
- Use `snake_case` for all function names
- Example: `calculate_firm_controls`, `compute_financial_features`, `run_panel_ols`
- Private helpers prefixed with underscore: `_check_thin_cells`, `_format_coefficient_table`

**Variables:**
- Use `snake_case` for local variables and parameters
- DataFrame variables include suffix indicating type: `df`, `series`, `factory`
- Example: `compustat_df`, `sample_compustat_factory`, `result`

**Types:**
- Use `PascalCase` for class names
- Example: `DataValidationError`, `FinancialCalculationError`, `ProjectConfig`
- Settings classes suffixed with `Settings`: `LoggingSettings`, `DataSettings`

**Constants:**
- Use `UPPER_SNAKE_CASE` for module-level constants
- Example: `INPUT_SCHEMAS`, `LINEARMODELS_AVAILABLE`

## Code Style

**Formatting:**
- Tool: Ruff (replaces Black)
- Line length: 88 characters
- Indent: 4 spaces
- Quote style: double quotes

**Key Ruff settings** (from `pyproject.toml`):
```toml
[tool.ruff]
line-length = 88
indent-width = 4
target-version = "py39"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP", "ARG", "SIM"]
ignore = ["E501", "B008"]
```

**Linting:**
- Tool: Ruff with extended rule set
- Rules enabled: pycodestyle (E/W), pyflakes (F), isort (I), bugbear (B), comprehensions (C4), pyupgrade (UP), unused-arguments (ARG), simplify (SIM)
- Per-file ignores:
  - `__init__.py`: E402, F401 (import violations allowed)
  - `tests/**`: S101, ARG (assert allowed, unused fixtures allowed)
  - `2_Scripts/**`: ALL (legacy scripts not enforced)

## Import Organization

**Order:**
1. Standard library imports (alphabetical)
2. Third-party imports (alphabetical)
3. Local imports from `f1d.shared.*`
4. Relative imports (avoid when possible)

**Example:**
```python
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
import structlog

from f1d.shared.data_validation import FinancialCalculationError
```

**Path Aliases:**
- Use full package paths: `from f1d.shared.config import ProjectConfig`
- No custom path aliases configured
- isort configured with `known-first-party = ["f1d"]`

## Error Handling

**Custom Exceptions:**
- Define domain-specific exception classes
- Example from `src/f1d/shared/data_validation.py`:
```python
class DataValidationError(Exception):
    """Raised when input data validation fails."""
    pass


class FinancialCalculationError(Exception):
    """Raised when financial metric calculation fails due to missing or invalid data."""
    pass
```

**Exception Messages:**
- Include context for debugging: variable names, values, available alternatives
- Example:
```python
raise FinancialCalculationError(
    f"Cannot calculate firm controls: missing gvkey in row. "
    f"Row columns: {list(row.index)}. "
    f"Year: {year}"
)
```

**Exception Documentation:**
- Document all raised exceptions in docstring
- Use `Raises:` section in docstrings

## Logging

**Framework:** structlog for structured logging

**Configuration** (from `src/f1d/shared/logging/config.py`):
```python
def configure_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    json_output: bool = False,
    settings: Optional["LoggingSettings"] = None,
) -> None:
    """Configure structlog with optional file output."""
```

**Getting a Logger:**
```python
from f1d.shared.logging import get_logger
logger = get_logger(__name__)
logger.info("processing_started", rows=1000, stage="financial")
```

**Logging Patterns:**
- Use key-value pairs for structured data
- Log at appropriate levels: DEBUG for detailed tracing, INFO for milestones, WARNING for recoverable issues, ERROR for failures
- Include context: stage name, row counts, file paths

## Comments

**Module Headers:**
- Use standardized docstring block at top of files
- Example from `src/f1d/shared/financial_utils.py`:
```python
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
Author: Thesis Author
Date: 2026-02-11
================================================================================
"""
```

**Function Docstrings:**
- Use Google-style docstrings
- Include Args, Returns, Raises, Example sections
- Example:
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

    Example:
        >>> row = pd.Series({"gvkey": "000001", "datadate": "2010-12-31"})
        >>> controls = calculate_firm_controls(row, compustat_df, 2010)
    """
```

## Function Design

**Size:** Functions should be focused and testable. Complex logic split into helper functions.

**Parameters:**
- Use type hints for all parameters in shared modules
- Use `Optional[T]` for optional parameters
- Provide default values where sensible
- Use `Field()` from pydantic for validation

**Return Values:**
- Return typed dictionaries or DataFrames for structured results
- Use `Dict[str, Any]` for complex result structures
- Document return structure in docstring

**Example:**
```python
def run_panel_ols(
    df: pd.DataFrame,
    dependent: str,
    exog: List[str],
    entity_col: str = "gvkey",
    time_col: str = "year",
    entity_effects: bool = True,
    time_effects: bool = True,
) -> Dict[str, Any]:
    """Returns dict with 'model', 'coefficients', 'summary', 'diagnostics', 'warnings'."""
```

## Module Design

**Exports:**
- Use `__all__` to define public API
- Example from `src/f1d/shared/__init__.py`:
```python
__all__ = [
    "DualWriter",
    "parse_ff_industries",
    "load_variable_descriptions",
    "get_latest_output_dir",
    "OutputResolutionError",
    "run_panel_ols",
    "center_continuous",
    "create_interaction",
    "compute_vif",
    "check_multicollinearity",
]
```

**Barrel Files:**
- Use `__init__.py` to re-export from submodules
- Keep public API explicit via `__all__`
- Re-export commonly used items at package level

**Package Structure:**
- `src/f1d/` - Main package
- `src/f1d/shared/` - Tier 1: Core utilities (strict typing required)
- `src/f1d/shared/config/` - Configuration classes
- `src/f1d/shared/logging/` - Logging utilities
- `src/f1d/shared/observability/` - Monitoring utilities
- `src/f1d/sample/`, `src/f1d/financial/`, `src/f1d/econometric/` - Tier 2: Stage modules

## Type Checking

**Tool:** mypy with tiered strictness

**Tier 1 (shared modules):** Strict mode enabled
```toml
[[tool.mypy.overrides]]
module = ["f1d.shared.*"]
strict = true
ignore_missing_imports = true
```

**Tier 2 (stage modules):** Moderate mode
```toml
[[tool.mypy.overrides]]
module = ["f1d.sample.*", "f1d.text.*", "f1d.financial.*", "f1d.econometric.*"]
disallow_untyped_defs = false
allow_untyped_defs = true
```

**Pattern for TYPE_CHECKING:**
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from f1d.shared.config.base import LoggingSettings
```

## Pre-commit Hooks

**Configuration:** `.pre-commit-config.yaml`

**Hooks enabled:**
- trailing-whitespace
- end-of-file-fixer
- check-yaml, check-toml, check-json
- check-added-large-files (max 1000KB)
- check-merge-conflict
- detect-private-key
- debug-statements
- ruff (linter + formatter)
- mypy (for `src/f1d/shared` only)

---

*Convention analysis: 2026-02-14*
