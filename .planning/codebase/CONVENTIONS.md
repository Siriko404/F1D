# Coding Conventions

**Analysis Date:** 2026-02-20

## Naming Patterns

**Files:**
- Source modules: `snake_case.py` (e.g., `financial_utils.py`, `panel_ols.py`, `path_utils.py`)
- Test files: `test_<module_name>.py` prefix (e.g., `test_financial_utils.py`, `test_data_validation.py`)
- Config modules: `snake_case.py` in `src/f1d/shared/config/` subpackage
- Script/pipeline files in `src/f1d/econometric/` use `test_<hypothesis>.py` naming (not test files — this is domain naming)

**Functions:**
- `snake_case` for all functions (e.g., `calculate_firm_controls()`, `run_panel_ols()`, `is_valid_timestamp()`)
- Private/internal helpers prefixed with `_` (e.g., `_check_thin_cells()`, `_format_coefficient_table()`)
- Factory functions returning callables: `_factory()` inner function name pattern

**Variables:**
- `snake_case` for all variables
- Uppercase for module-level constants (e.g., `TIMESTAMP_PATTERN`, `INPUT_SCHEMAS`, `LINEARMODELS_AVAILABLE`)
- DataFrame columns that represent financial/statistical outputs use CamelCase when matching domain conventions (e.g., `Size`, `BM`, `Lev`, `ROA`, `CurrentRatio`, `RD_Intensity`)

**Types/Classes:**
- `PascalCase` for all classes (e.g., `DataValidationError`, `FinancialCalculationError`, `CollinearityError`, `ConfigError`)
- Custom exception classes: suffix `Error` (e.g., `DataValidationError`, `PathValidationError`, `OutputResolutionError`)
- Pydantic config classes: suffix `Settings` or `Config` (e.g., `DataSettings`, `LoggingSettings`, `DeterminismSettings`, `ProjectConfig`)

## Code Style

**Formatter:** Ruff (configured in `pyproject.toml`)
- Line length: 88 characters (Black-compatible default)
- Indent: 4 spaces
- Quote style: double quotes (`"`)
- Magic trailing comma: preserved
- Line endings: auto

**Linter:** Ruff (configured in `pyproject.toml`)
- Enabled rule sets: `E`, `W` (pycodestyle), `F` (pyflakes), `I` (isort), `B` (bugbear), `C4` (comprehensions), `UP` (pyupgrade), `ARG` (unused arguments), `SIM` (simplify)
- `E501` disabled (line length handled by formatter)
- `B008` disabled (function calls in argument defaults)
- `__init__.py` files: `E402`, `F401` ignored
- Test files: `S101` (assert), `ARG` (unused fixtures) ignored

**Type Checking:** mypy (configured in `pyproject.toml`)
- `src/f1d/shared/` — strict mode (`strict = true`)
- `src/f1d/sample/`, `src/f1d/text/`, `src/f1d/financial/`, `src/f1d/econometric/` — relaxed mode (allows untyped defs)
- `type: ignore[...]` used inline for third-party libraries lacking stubs (e.g., `linearmodels`, `scipy`, `statsmodels`)

## Import Organization

**Order (enforced by ruff/isort):**
1. `from __future__ import annotations` (if used — present in 75+ files in `src/f1d/shared/`)
2. Standard library imports
3. Third-party imports (`numpy`, `pandas`, `pydantic`, `yaml`, `structlog`)
4. First-party imports (`from f1d.shared.*`)

**Path Aliases:**
- `known-first-party = ["f1d"]` configured in ruff isort

**Example from `src/f1d/shared/financial_utils.py`:**
```python
from typing import Dict, Mapping, Union, cast

import numpy as np
import pandas as pd

from f1d.shared.data_validation import FinancialCalculationError
```

**Example from `src/f1d/shared/config/base.py`:**
```python
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Type

import yaml
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict

from f1d.shared.config.datasets import DatasetsConfig
```

## Error Handling

**Custom Exception Hierarchy:**
- Domain errors subclass `Exception` directly (no shared base class)
- `DataValidationError` — schema/validation failures (`src/f1d/shared/data_validation.py`)
- `FinancialCalculationError` — missing/invalid Compustat data (`src/f1d/shared/data_validation.py`)
- `PathValidationError`, `OutputResolutionError` — path/directory failures (`src/f1d/shared/path_utils.py`)
- `CollinearityError`, `MulticollinearityError` — regression failures (`src/f1d/shared/panel_ols.py`)
- `ConfigError` — configuration loading failures (`src/f1d/shared/config/loader.py`)

**Error message patterns:**
- Include context: what failed, identifier values, and available alternatives
```python
raise FinancialCalculationError(
    f"Cannot calculate firm controls: no Compustat data found. "
    f"gvkey={gvkey}, year={year}. "
    f"Available years for this gvkey: {list(available_years)}. "
    f"Total Compustat records: {len(compustat_df)}"
)
```

**Graceful degradation with NaN:**
- Financial calculations return `np.nan` (not raise) for missing/zero denominator inputs
- Guards use `if data.get("at") and data["at"] > 0` pattern before division
- Use `pd.isna()` checks in tests to verify NaN propagation

**Strict vs. non-strict modes:**
- Validation functions accept `strict: bool = True` parameter
- Strict mode: raise exception; non-strict mode: print warning and continue
- Example: `validate_dataframe_schema(df, ..., strict=False)` logs to `sys.stderr`

**Optional dependency guard pattern:**
```python
try:
    from linearmodels.panel.model import PanelOLS
    LINEARMODELS_AVAILABLE = True
except ImportError:
    LINEARMODELS_AVAILABLE = False
    PanelOLS = None  # type: ignore[misc,assignment]
```

## Logging

**Framework:** `structlog` (configured in `src/f1d/shared/logging/config.py`)
- JSON output in production, ConsoleRenderer for development
- Standard library `logging.getLogger(__name__)` used in data_loading and chunked_reader

**Patterns:**
- Module-level logger: `logger = logging.getLogger(__name__)` for stdlib modules
- `structlog` used for structured/contextual logging in the logging subsystem
- Timestamps in ISO format via `structlog.processors.TimeStamper(fmt="iso")`
- Do not log sensitive data

## Comments

**Module Docstrings:**
- All `src/f1d/shared/` modules open with a banner block:
```python
#!/usr/bin/env python3
"""
================================================================================
SHARED MODULE: <Name>
================================================================================
ID: shared/<module_name>
Description: <multi-line description>

Inputs:
    - ...

Outputs:
    - ...

Deterministic: true/false
Main Functions:
    - <function>(): <description>

Dependencies:
    - ...

Author: Thesis Author
Date: YYYY-MM-DD
================================================================================
"""
```

**Class Docstrings:**
- All Pydantic model classes include `Attributes:` section and `Example:` with `>>>` doctest format
```python
class DataSettings(BaseSettings):
    """Configuration for data range settings.

    Attributes:
        year_start: Starting year for data processing (2000-2030).
        year_end: Ending year for data processing (2000-2030).

    Example:
        >>> settings = DataSettings(year_start=2002, year_end=2018)
        >>> settings.year_start
        2002
    """
```

**Function Docstrings:**
- All public functions include `Args:`, `Returns:`, `Raises:` sections
- Inline comments used for non-obvious logic (e.g., `# Size: log total assets`)

**Code Annotations:**
- `# type: ignore[<code>]` with specific error code (never bare `# type: ignore`)
- `# pragma: no cover` excluded from coverage in `pyproject.toml`

**Section separators:**
- `# ====...====` (80-char) banners used to delimit logical sections within files

## Function Design

**Size:** Functions are generally single-responsibility and focused. Calculation functions (e.g., `calculate_firm_controls`) handle one entity at a time; batch processing is done by wrapper functions (`compute_financial_features`).

**Parameters:**
- Explicit typed parameters with type annotations on all `src/f1d/shared/` functions
- Factory callables accept keyword arguments with sensible defaults (`n_firms=10`, `seed=42`)
- Boolean flags use `strict: bool = True` or `winsorize: bool = False` naming

**Return Values:**
- `Dict[str, Union[float, int, None]]` for calculation results
- `pd.DataFrame` for batch-processed output
- `None` return type declared explicitly where applicable
- Functions that modify in place are rare; preference for returning new objects

## Module Design

**Exports:**
- `src/f1d/shared/__init__.py` controls public API
- Specific named imports preferred over wildcard imports
- `__all__` not widely used; rely on naming conventions

**Barrel Files:**
- `src/f1d/shared/config/__init__.py` re-exports `ProjectConfig`, `load_config`, `get_config`, `clear_config_cache`, `reload_config`

**Pydantic Settings:**
- Config models inherit from `pydantic_settings.BaseSettings` for env var support
- Env var prefix: `F1D_` (e.g., `F1D_DATA__YEAR_START`)
- Double underscore `__` separates nested config levels in env var names
- `@field_validator` and `@model_validator` used for cross-field validation

---

*Convention analysis: 2026-02-20*
