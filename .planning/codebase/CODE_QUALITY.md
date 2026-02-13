# Code Quality Analysis

**Analysis Date:** 2026-02-12

## Executive Summary

This document analyzes code quality patterns across the F1D Python data processing pipeline. The codebase demonstrates strong documentation practices in shared modules and test coverage, with opportunities for improvement in type hint coverage and code duplication reduction.

---

## 1. Docstring Coverage and Style

### 1.1 Module-Level Docstrings

**Coverage:** High (100% for active `2_Scripts/` files)

**Style Pattern:** Custom structured docstring format with standardized sections:

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
    - Uses: pandas, numpy

Author: Thesis Author
Date: 2026-02-11
================================================================================
"""
```

**Files with this pattern:**
- `2_Scripts/shared/financial_utils.py`
- `2_Scripts/shared/panel_ols.py`
- `2_Scripts/shared/data_validation.py`
- `2_Scripts/shared/path_utils.py`
- `2_Scripts/shared/iv_regression.py`
- `2_Scripts/shared/observability/logging.py`
- `2_Scripts/shared/observability/stats.py`
- `2_Scripts/1_Sample/1.0_BuildSampleManifest.py`
- `2_Scripts/3_Financial_V2/3.1_H1Variables.py`

### 1.2 Function-Level Docstrings

**Coverage:** High in shared modules, variable in scripts

**Style:** Google-style docstrings with Args, Returns, Raises, and Examples:

```python
def run_panel_ols(
    df: pd.DataFrame,
    dependent: str,
    exog: List[str],
    ...
) -> Dict[str, Any]:
    """
    Run panel OLS regression with fixed effects and clustered standard errors.

    This function provides a standardized interface for panel regression using
    linearmodels.PanelOLS. It handles firm, year, and industry fixed effects,
    various covariance estimators (clustered, kernel/HAC, robust), and
    comprehensive diagnostics including VIF multicollinearity checks.

    Args:
        df: DataFrame with panel data. Must contain entity_col, time_col, and
            all variables in dependent + exog.
        dependent: Name of the dependent variable column.
        exog: List of independent/exogenous variable column names.
        ...

    Returns:
        Dictionary with:
            - 'model': Fitted PanelOLS model object
            - 'coefficients': DataFrame with beta, SE, t-stat, p-value per variable
            - 'summary': Dict with R2, adj_R2, N, F-stat, fixed_effects_used
            ...

    Raises:
        ImportError: If linearmodels is not available
        ValueError: If required columns are missing or data invalid
        CollinearityError: If perfect collinearity detected in design matrix

    Example:
        >>> df = pd.DataFrame({...})
        >>> result = run_panel_ols(df=df, dependent='cash_ratio', exog=['vagueness'])
        >>> print(result['summary']['rsquared'])
    """
```

**Strong examples in:**
- `2_Scripts/shared/panel_ols.py` (lines 203-284)
- `2_Scripts/shared/financial_utils.py` (lines 41-58, 136-154)
- `2_Scripts/shared/path_utils.py` (lines 50-66, 87-99)
- `2_Scripts/shared/iv_regression.py` (lines 122-179)

### 1.3 Docstring Gaps

**Minimal docstrings found in:**
- `2_Scripts/2_Text/2.1_TokenizeAndCount.py` - Some functions lack full Args/Returns
- Legacy/archive files (expected, not analyzed)

---

## 2. Type Hint Usage

### 2.1 Configuration

**Type checking configured in:** `pyproject.toml` (lines 98-146)

```toml
[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
ignore_missing_imports = false
check_untyped_defs = true

# Progressive rollout: exclude most scripts initially
exclude = [
    "2_Scripts/[^s]*",  # Exclude all non-shared scripts
    "tests/",
    ".___archive/",
]

# Strict mode for new shared modules only
[[tool.mypy.overrides]]
module = "shared.observability.*"
strict = true
```

### 2.2 Coverage Assessment

**High Coverage (shared modules):**

```python
# 2_Scripts/shared/panel_ols.py
from typing import Any, Dict, List, Optional, Tuple

def _check_thin_cells(
    df: pd.DataFrame, industry_col: str, time_col: str, min_firms: int = 5
) -> Tuple[bool, Dict[str, int]]:
    """Check for thin industry-year cells."""
    ...

def run_panel_ols(
    df: pd.DataFrame,
    dependent: str,
    exog: List[str],
    entity_col: str = "gvkey",
    ...
) -> Dict[str, Any]:
    """Run panel OLS regression with fixed effects."""
    ...
```

**Medium Coverage (V2 scripts):**

```python
# 2_Scripts/3_Financial_V2/3.1_H1Variables.py
def compute_cash_holdings(compustat_df: pd.DataFrame) -> pd.DataFrame:
    """Compute Cash Holdings = CHE / AT"""
    ...

def winsorize_series(
    s: pd.Series, lower: float = 0.01, upper: float = 0.99
) -> pd.Series:
    """Winsorize a series at specified percentiles."""
    ...
```

**Low Coverage (orchestrator and older scripts):**

```python
# 2_Scripts/1_Sample/1.0_BuildSampleManifest.py
def parse_arguments():  # No return type
    """Parse command-line arguments."""
    ...

def check_prerequisites(root):  # No type hints
    """Validate all required inputs exist."""
    ...
```

### 2.3 Type Stub Files

Custom stubs for external libraries in `2_Scripts/stubs/`:
- `linearmodels.panel.pyi` - Type stubs for linearmodels PanelOLS

---

## 3. Code Style Consistency

### 3.1 Linting Configuration

**Configured in:** `pyproject.toml` (lines 72-96)

```toml
[tool.ruff]
line-length = 88
indent-width = 4
target-version = "py39"

[tool.ruff.lint]
select = ["E4", "E7", "E9", "F", "B", "W", "I"]
ignore = ["E501"]  # Line length handled by formatter

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

### 3.2 Observed Patterns

**Naming Conventions:**
- Functions: `snake_case` (e.g., `calculate_firm_controls`, `compute_cash_holdings`)
- Classes: `PascalCase` (e.g., `DualWriter`, `CollinearityError`, `WeakInstrumentError`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `LINEARMODELS_AVAILABLE`, `INPUT_SCHEMAS`)
- Private functions: `_leading_underscore` (e.g., `_check_thin_cells`, `_format_star`)

**Import Organization:**
```python
# Standard library
import argparse
import sys
from pathlib import Path
from typing import Optional, Dict, List, Any

# Third-party
import numpy as np
import pandas as pd
import yaml

# Local imports
from shared.path_utils import ensure_output_dir, validate_input_file
from shared.observability_utils import DualWriter, print_stat
```

**Line Length:** Generally adheres to 88 characters (Black default)

---

## 4. Error Handling Patterns

### 4.1 Custom Exceptions

**Well-defined exception hierarchy:**

```python
# 2_Scripts/shared/data_validation.py
class DataValidationError(Exception):
    """Raised when input data validation fails."""
    pass

class FinancialCalculationError(Exception):
    """Raised when financial metric calculation fails due to missing or invalid data."""
    pass

# 2_Scripts/shared/panel_ols.py
class CollinearityError(Exception):
    """Raised when perfect collinearity is detected in the design matrix."""
    pass

class MulticollinearityError(Exception):
    """Raised when VIF threshold is exceeded (high multicollinearity)."""
    pass

# 2_Scripts/shared/iv_regression.py
class WeakInstrumentError(Exception):
    """Raised when first-stage F-stat < 10 (weak instruments)."""
    def __init__(self, message: str, f_stat: Optional[float] = None, threshold: Optional[float] = None):
        super().__init__(message)
        self.f_stat = f_stat
        self.threshold = threshold

# 2_Scripts/shared/path_utils.py
class PathValidationError(Exception):
    """Raised when path validation fails."""
    pass

class OutputResolutionError(Exception):
    """Raised when output directory resolution fails."""
    pass
```

### 4.2 Error Messages

**Informative error messages with context:**

```python
# 2_Scripts/shared/financial_utils.py (lines 60-83)
def calculate_firm_controls(row, compustat_df, year):
    gvkey = row.get("gvkey")
    if gvkey is None:
        raise FinancialCalculationError(
            f"Cannot calculate firm controls: missing gvkey in row. "
            f"Row columns: {list(row.index)}. "
            f"Year: {year}"
        )

    if firm_data.empty:
        available_years = compustat_df[compustat_df["gvkey"] == str(gvkey).zfill(6)]["fyear"].unique()
        raise FinancialCalculationError(
            f"Cannot calculate firm controls: no Compustat data found. "
            f"gvkey={gvkey}, year={year}. "
            f"Available years for this gvkey: {list(available_years)}. "
            f"Total Compustat records: {len(compustat_df)}"
        )
```

### 4.3 Exception Documentation

**Raises documented in docstrings:**

```python
def validate_output_path(...) -> Path:
    """
    Validate output path exists and is accessible.

    Raises:
        PathValidationError: If validation fails
    """
```

---

## 5. Function/Method Organization

### 5.1 Script Structure Pattern

Most scripts follow this organizational pattern:

```python
#!/usr/bin/env python3
"""Module docstring"""

# 1. Imports
import argparse
import sys
from pathlib import Path

# 2. Configuration functions
def load_config(): ...
def setup_paths(config): ...

# 3. Data loading functions
def load_manifest(manifest_dir): ...
def load_compustat(compustat_file): ...

# 4. Processing functions (in dependency order)
def compute_cash_holdings(df): ...
def compute_leverage(df): ...
def winsorize_series(s): ...

# 5. CLI functions
def parse_arguments(): ...
def check_prerequisites(paths): ...

# 6. Main entry point
def main(): ...

if __name__ == "__main__":
    main()
```

**Example files:**
- `2_Scripts/3_Financial_V2/3.1_H1Variables.py` (1055 lines, well-organized)
- `2_Scripts/1_Sample/1.0_BuildSampleManifest.py` (337 lines)

### 5.2 Function Size

**Typical function lengths:**
- Utility functions: 10-30 lines
- Computation functions: 20-50 lines
- Main functions: 100-300 lines

**Large functions observed:**
- `2_Scripts/3_Financial_V2/3.1_H1Variables.py::main()` - ~400 lines (acceptable for orchestration)

---

## 6. Comments and Documentation

### 6.1 Inline Comments

**Section headers with visual separators:**

```python
# ==============================================================================
# Configuration and setup
# ==============================================================================

# ==============================================================================
# Data Loading
# ==============================================================================

# ==============================================================================
# Variable Computation Functions
# ==============================================================================
```

**Inline explanations for complex logic:**

```python
# 2_Scripts/shared/panel_ols.py (lines 340-341)
# Initialize complete_idx before conditional (fixes UnboundLocalError when industry_effects=True)
complete_idx = exog_data.notna().all(axis=1) & dependent_data.notna()
```

### 6.2 TODO Comments

**Only 1 TODO found in active code:**
```python
# 2_Scripts/3_Financial/3.1_FirmControls.py:778
# TODO: Track actual winsorized cols
```

This indicates good maintenance with minimal deferred work.

### 6.3 Documentation Files

The codebase generates markdown reports:
- `4_Outputs/{script_name}/{timestamp}/report_step_X_Y.md`

---

## 7. Code Duplication Analysis

### 7.1 Identified Duplication

**Observability utilities duplicated across files:**

Multiple scripts contain local copies of observability functions before the shared module extraction:

- `2_Scripts/2_Text/2.1_TokenizeAndCount.py` has local definitions of:
  - `compute_file_checksum()`
  - `print_stat()`
  - `analyze_missing_values()`
  - `print_stats_summary()`
  - `save_stats()`
  - `get_process_memory_mb()`
  - `calculate_throughput()`
  - `detect_anomalies_zscore()`
  - `detect_anomalies_iqr()`

**Resolution in progress:** The `shared/observability_utils.py` now re-exports from `shared/observability/` package, but some older scripts still have local copies.

### 7.2 Similar Patterns Across Hypothesis Scripts

Files in `2_Scripts/3_Financial_V2/` follow similar patterns:
- `3.1_H1Variables.py`
- `3.2_H2Variables.py`
- `3.3_H3Variables.py`
- etc.

Each contains similar:
- `load_config()` functions
- `setup_paths()` functions
- `parse_arguments()` functions
- Statistics tracking structures

**Recommendation:** Consider creating a base class or shared utilities for hypothesis variable scripts.

### 7.3 Import Pattern Duplication

Multiple scripts have identical import fallback patterns:

```python
# Repeated in multiple files:
try:
    from shared.observability_utils import DualWriter
except ImportError:
    import sys as _sys
    from pathlib import Path as _Path
    _script_dir = _Path(__file__).parent.parent
    _sys.path.insert(0, str(_script_dir))
    from shared.observability_utils import DualWriter
```

---

## 8. Gaps vs Industry Standard Python

### 8.1 Coverage Gaps

| Standard | Current Status | Gap |
|----------|---------------|-----|
| Type hints on all functions | Partial (shared modules good, scripts partial) | Medium |
| Docstrings on all functions | High in shared, variable in scripts | Low |
| 100% test coverage | Target 60%, tiered approach | Expected for research code |
| mypy strict mode | Enabled for observability.* only | Progressive rollout |
| Pre-commit hooks | Not detected | Consider adding |

### 8.2 Strengths

1. **Comprehensive module-level documentation** with standardized format
2. **Custom exception hierarchy** with informative error messages
3. **Well-organized shared utilities** with clean exports
4. **Test fixtures and shared test utilities** in `tests/conftest.py`
5. **Backward compatibility layer** for refactored modules
6. **Deterministic processing** documented in docstrings

### 8.3 Improvement Opportunities

1. **Type hint coverage:**
   - Add type hints to orchestrator scripts (`1.0_BuildSampleManifest.py`)
   - Enable `disallow_untyped_defs` progressively for more modules

2. **Code duplication:**
   - Remove local observability functions from `2.1_TokenizeAndCount.py`
   - Create base class for hypothesis variable scripts

3. **Import fallbacks:**
   - Consolidate import fallback patterns into shared utility
   - Or fix PYTHONPATH configuration

4. **Testing:**
   - Increase coverage from 60% target toward 80%
   - Add property-based tests for financial calculations

---

## 9. Recommendations

### 9.1 Immediate Actions

1. **Remove duplicated observability functions** from `2_Text/2.1_TokenizeAndCount.py` - use shared imports
2. **Add type hints** to orchestrator scripts in `1_Sample/`
3. **Create base class** for hypothesis variable computation scripts

### 9.2 Medium-Term Actions

1. **Enable mypy strict mode** for `shared.panel_ols` and `shared.iv_regression`
2. **Add pre-commit hooks** for ruff and mypy
3. **Document testing strategy** in TESTING.md (separate document)

### 9.3 Code Review Checklist

When reviewing new code, verify:
- [ ] Module docstring follows established format
- [ ] Function docstrings include Args, Returns, Raises
- [ ] Type hints on function signatures
- [ ] Custom exceptions for domain-specific errors
- [ ] Informative error messages with context
- [ ] Imports organized: stdlib -> third-party -> local
- [ ] No new code duplication introduced

---

*Code quality analysis complete. For testing patterns, see TESTING.md (to be generated).*
