# F1D V5/V6 Architecture Standards Research

**Researched:** 2026-02-14
**Domain:** Code architecture, quality, testing, and configuration standards
**Confidence:** HIGH

---

## Summary

This document consolidates the V5/V6 architecture standards defined across three key documents:

1. **ARCHITECTURE_STANDARD.md (v6.1)** - Canonical folder structure, module organization, data lifecycle
2. **CODE_QUALITY_STANDARD.md (v5.0)** - Naming conventions, docstrings, type hints, error handling
3. **CONFIG_TESTING_STANDARD.md (v5.0)** - Configuration patterns, testing infrastructure, coverage targets

**Current Status:**
- v6.1 Architecture Standard is **IMPLEMENTED** - full compliance achieved in Phase 77
- v5.0 Code Quality and Config/Testing Standards are **DEFINITION documents** - target patterns for v6.0+

**Primary Recommendation:** All new code must follow V6.1 architecture (src-layout with `f1d.shared.*` imports). Code quality and testing standards are target patterns for gradual adoption.

---

## 1. Architecture Standard (v6.1 - IMPLEMENTED)

**Source:** `docs/ARCHITECTURE_STANDARD.md`

### 1.1 Folder Structure (ARCH-01)

The project uses **src-layout** pattern recommended by Python Packaging Authority:

```
F1D/
├── src/f1d/                     # Main package (src-layout pattern)
│   ├── __init__.py              # Package metadata and public API
│   ├── sample/                  # Stage 1: Sample construction
│   ├── text/                    # Stage 2: Text processing
│   ├── financial/               # Stage 3: Financial features
│   │   ├── v1/                  # V1 methodology (active variant)
│   │   └── v2/                  # V2 methodology (active variant)
│   ├── econometric/             # Stage 4: Econometric analysis
│   │   ├── v1/                  # V1 methodology (active variant)
│   │   └── v2/                  # V2 methodology (active variant)
│   └── shared/                  # Shared utilities (cross-cutting)
│       ├── config/              # Configuration utilities
│       ├── observability/       # Logging and monitoring
│       ├── path_utils.py        # Path resolution
│       └── panel_ols.py         # Panel OLS utilities
│
├── tests/                       # Test suite
├── config/                      # Configuration files
├── data/                        # Data directory
│   ├── raw/                     # READ-ONLY original data
│   ├── interim/                 # Deletable intermediate
│   ├── processed/               # Controlled final data
│   └── external/                # Reference data
├── results/                     # Analysis outputs
├── logs/                        # Execution logs
├── .___archive/                 # Archived/deprecated code
├── pyproject.toml               # Build system and tool configs
└── README.md
```

### 1.2 Module Organization (ARCH-02)

#### Import Convention (v6.1+)

```python
# CORRECT: Canonical namespace imports (v6.1 implemented)
from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.panel_ols import run_panel_ols
from f1d.shared.config import get_settings
from f1d.financial.v1.variables import construct_variables
from f1d.econometric.v2.regressions import run_panel_ols

# INCORRECT (legacy - no longer works):
# from shared.path_utils import get_latest_output_dir
# sys.path.insert(0, '2_Scripts')
```

#### Module Tier System

| Tier | Location | Test Coverage | Type Hints | Quality Bar |
|------|----------|---------------|------------|-------------|
| **Tier 1** | `src/f1d/shared/` | 100% required | Strict mypy | Highest |
| **Tier 2** | `src/f1d/{stage}/` | 80%+ recommended | Recommended | Standard |
| **Tier 3** | `scripts/` | Optional | Optional | Lower |

#### __init__.py Pattern

Every package MUST have an `__init__.py` with:
1. Docstring documenting package purpose
2. `__all__` to declare public API
3. Re-exports for convenience

```python
# src/f1d/shared/__init__.py
"""Shared utilities for F1D pipeline.

Modules:
    path_utils: Path resolution and output directory utilities
    panel_ols: Panel OLS regression utilities
"""

from f1d.shared.path_utils import get_latest_output_dir, OutputResolutionError
from f1d.shared.panel_ols import run_panel_ols, CollinearityError

__all__ = [
    "get_latest_output_dir",
    "OutputResolutionError",
    "run_panel_ols",
    "CollinearityError",
]
```

### 1.3 Data Directory Structure (ARCH-03)

| Directory | Mutability | Purpose |
|-----------|------------|---------|
| `data/raw/` | **READ-ONLY** | Never modify original data |
| `data/interim/` | Deletable | Can regenerate from raw |
| `data/processed/` | Controlled | Source of truth for analysis |
| `data/external/` | Reference | Third-party reference data |

### 1.4 Version Management (ARCH-04)

- **Package versioning:** Semantic versioning (MAJOR.MINOR.PATCH) in `src/f1d/__init__.py`
- **Active variants:** V1 and V2 are BOTH active methodology variants
- **Deprecation timeline:** 30-day warning period before archive

### 1.5 v6.1 Compliance Status

As of Phase 77 (2026-02-14):
- All 101 source files use `f1d.shared.*` namespace imports
- Zero `sys.path.insert()` calls in entire codebase
- mypy passes with 0 errors
- 1000+ tests with namespace imports

---

## 2. Code Quality Standard (v5.0 - DEFINITION)

**Source:** `docs/CODE_QUALITY_STANDARD.md`

### 2.1 Naming Conventions

| Entity | Convention | Example |
|--------|------------|---------|
| Script | `{Stage}.{Step}_{Description}.py` | `1.0_BuildSampleManifest.py` |
| Module | snake_case | `panel_ols.py`, `path_utils.py` |
| Package | snake_case | `shared/`, `observability/` |
| Function | snake_case | `get_latest_output_dir()` |
| Class | PascalCase | `CollinearityError`, `DualWriter` |
| Constant | UPPER_SNAKE_CASE | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |
| Private | _leading_underscore | `_check_thin_cells()` |

### 2.2 Docstring Standard (CODE-01)

**Format:** Google-style docstrings

**Tier Requirements:**

| Tier | Args | Returns | Raises | Examples |
|------|------|---------|--------|----------|
| Tier 1 (Core) | Required | Required | Required | Required |
| Tier 2 (Stage) | Required | Required | Required | Recommended |
| Tier 3 (Scripts) | Recommended | If non-void | If exceptions | Optional |

**Complete Function Docstring Pattern:**

```python
def run_panel_ols(
    df: pd.DataFrame,
    dependent: str,
    exog: List[str],
) -> Dict[str, Any]:
    """Execute panel regression with fixed effects.

    Runs a PanelOLS regression with entity and time fixed effects,
    clustered standard errors, and multicollinearity diagnostics.

    Args:
        df: DataFrame with panel data containing all variables.
        dependent: Name of the dependent variable column.
        exog: List of exogenous variable column names.

    Returns:
        Dictionary containing:
            - model: Fitted PanelOLS object
            - coefficients: DataFrame with beta, SE, t-stat, p-value
            - summary: Dict with R2, adj_R2, N, F-stat

    Raises:
        CollinearityError: If perfect collinearity detected.
        ValueError: If required columns missing.

    Examples:
        >>> result = run_panel_ols(df, "cash_holdings", ["uncertainty"])
        >>> print(result["summary"]["r2"])
        0.45
    """
    ...
```

### 2.3 Type Hint Coverage (CODE-02)

| Tier | Coverage Target | mypy Mode |
|------|-----------------|-----------|
| Tier 1 (Core Shared) | 100% | `strict = true` |
| Tier 2 (Stage-Specific) | 80%+ | `disallow_untyped_defs = false` |
| Tier 3 (Scripts) | Optional | Excluded from mypy |

**mypy Configuration:**

```toml
[tool.mypy]
python_version = "3.9"
warn_return_any = true
check_untyped_defs = true

# Strict mode for Tier 1
[[tool.mypy.overrides]]
module = ["f1d.shared.*"]
strict = true

# Gradual adoption for Tier 2
[[tool.mypy.overrides]]
module = ["f1d.financial.*", "f1d.econometric.*"]
disallow_untyped_defs = false

# Exclude Tier 3
[[tool.mypy.overrides]]
module = ["scripts.*"]
ignore_errors = true
```

### 2.4 Import Organization (CODE-03)

PEP 8 import order:

```python
# Standard library
import os
from pathlib import Path
from typing import Dict, List, Optional

# Third-party packages
import numpy as np
import pandas as pd
from linearmodels import PanelOLS

# Local imports (using f1d namespace)
from f1d.shared.path_utils import get_latest_output_dir
from f1d.shared.logging import get_logger
```

### 2.5 Error Handling (CODE-04)

- Use custom exceptions (inherit from project base)
- **NO bare except clauses** (PEP 760)
- Always specify exception type
- Document raised exceptions in docstrings

```python
# Custom exception hierarchy
class F1DError(Exception):
    """Base exception for F1D pipeline."""
    pass

class CollinearityError(F1DError):
    """Raised when perfect collinearity detected."""
    pass

class OutputResolutionError(F1DError):
    """Raised when output directory cannot be resolved."""
    pass
```

### 2.6 Function Size Limits (CODE-05)

- Maximum function length: 50 lines (excluding docstrings)
- Maximum cyclomatic complexity: 10
- Extract helper functions for complex logic

---

## 3. Configuration and Testing Standard (v5.0 - DEFINITION)

**Source:** `docs/CONFIG_TESTING_STANDARD.md`

### 3.1 Configuration File Structure (CONF-01)

**Pattern:** YAML with pydantic-settings validation

```yaml
# config/project.yaml
project:
  name: F1D_Clarity
  version: "5.0.0"

data:
  year_start: 2002
  year_end: 2022

logging:
  level: INFO

determinism:
  random_seed: 42
  thread_count: 1
```

**Pydantic Settings Model:**

```python
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator

class DataSettings(BaseSettings):
    year_start: int = Field(ge=2000, le=2030)
    year_end: int = Field(ge=2000, le=2030)

    @model_validator(mode='after')
    def validate_year_range(self):
        if self.year_end < self.year_start:
            raise ValueError('year_end must be >= year_start')
        return self
```

### 3.2 Environment Variable Handling (CONF-02)

**Pattern:** SecretStr for secrets, F1D_ prefix for overrides

```python
from pydantic import SecretStr

class EnvConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="F1D_")

    wrds_username: Optional[str] = None
    wrds_password: Optional[SecretStr] = None  # Never logged

    def get_wrds_password(self) -> Optional[str]:
        if self.wrds_password:
            return self.wrds_password.get_secret_value()
        return None
```

**Environment Variable Naming:**

| Env Variable | Config Path |
|--------------|-------------|
| `F1D_DATA__YEAR_START=2005` | `config.data.year_start` |
| `F1D_LOGGING__LEVEL=DEBUG` | `config.logging.level` |

### 3.3 Path Resolution Pattern (CONF-03)

**Eliminate sys.path.insert with src-layout:**

```bash
# Install package in editable mode
pip install -e .
```

```python
# Clean imports - no sys.path manipulation
from f1d.shared.panel_ols import run_panel_ols
from f1d.financial.v1.variables import construct_variables
```

### 3.4 Output Directory Pattern (CONF-04)

**Pattern:** Timestamped directories with checksums

```python
# OutputManager pattern
manager = OutputManager(Path("results/financial"))
output_dir = manager.create_output_dir()  # Creates YYYY-MM-DD_HHMMSS

# Register outputs with checksums
manager.register_output(output_file, "Financial variables")
manager.save_checksums()  # Creates checksums.json
```

### 3.5 Logging Pattern (CONF-05)

**Pattern:** Structured logging with structlog

```python
from f1d.shared.logging import configure_logging, get_logger

configure_logging(log_level="INFO", json_output=False)
logger = get_logger(__name__)

# Structured logging with context
logger.info("processing_started", rows=1000, stage="financial")
```

### 3.6 Test Structure (TEST-01)

```
tests/
├── conftest.py           # Root-level shared fixtures
├── fixtures/             # Test data files
├── factories/            # Test data factories
├── unit/                 # Fast, isolated tests
├── integration/          # Module interaction tests
├── regression/           # Output stability tests
├── e2e/                  # End-to-end pipeline tests
└── performance/          # Performance benchmarks
```

### 3.7 Coverage Targets (TEST-02)

| Module Tier | Location | Target Coverage |
|-------------|----------|-----------------|
| Tier 1 (Core Shared) | `src/f1d/shared/` | 90% minimum |
| Tier 2 (Stage-Specific) | `src/f1d/{stage}/` | 80% minimum |
| Tier 3 (Scripts) | `scripts/` | No requirement |
| **Overall Project** | All | 70% minimum |

**pyproject.toml Coverage Config:**

```toml
[tool.coverage.run]
branch = true
source = ["src/f1d"]

[tool.coverage.report]
fail_under = 70
show_missing = true
```

### 3.8 Test Naming Convention (TEST-03)

**Pattern:** `test_<module>_<function>_<scenario>`

```python
# GOOD examples
def test_run_panel_ols_valid_input_returns_results():
    ...

def test_run_panel_ols_missing_columns_raises_error():
    ...

def test_validate_output_path_nonexistent_raises_error():
    ...

# BAD examples (avoid)
def test_regression():  # Too vague
def test_error():       # No context
def test_1():           # Numeric, no meaning
```

### 3.9 Fixture Organization (TEST-04)

**Pattern:** Hierarchical conftest.py with factory fixtures

```
tests/
├── conftest.py           # Session-scoped fixtures
├── unit/
│   └── conftest.py       # Unit-test-specific fixtures
├── integration/
│   └── conftest.py       # Integration-test-specific fixtures
```

### 3.10 Mocking and Test Data (TEST-05)

- Use `pytest-mock` for mocking
- Use factory fixtures for test data
- Keep test data in `tests/fixtures/`

---

## 4. Key Implementation Requirements

### 4.1 Prerequisites for All Development

```bash
# One-time setup
pip install -e .
```

### 4.2 Mandatory Patterns

| Area | Requirement | Source |
|------|-------------|--------|
| Imports | Use `f1d.shared.*` namespace | ARCH-02 |
| Data | Never modify `data/raw/` | ARCH-03 |
| Tests | Mirror `src/` structure in `tests/` | ARCH-01 |
| Coverage | 70% overall minimum | TEST-02 |
| Naming | snake_case for functions/modules | NAM-02/03 |
| Docstrings | Google-style for Tier 1/2 | CODE-01 |
| Type hints | Required for Tier 1 | CODE-02 |

### 4.3 Anti-Patterns to Avoid

| Anti-Pattern | Correct Pattern |
|--------------|-----------------|
| `sys.path.insert()` | Use `pip install -e .` |
| `from shared.xxx import` | Use `from f1d.shared.xxx import` |
| Modifying `data/raw/` | Write to `data/processed/` |
| Bare `except:` | Specify exception type |
| `import *` | Import specific names |
| `utils.py` catch-all | Use descriptive module names |

---

## 5. Standards Hierarchy

```
ARCHITECTURE_STANDARD.md (v6.1 - IMPLEMENTED)
    ├── Folder structure, module organization
    ├── Data lifecycle management
    └── Version management
        │
        ├── Referenced by:
        │   ├── CODE_QUALITY_STANDARD.md (v5.0 - DEFINITION)
        │   │   ├── Naming conventions
        │   │   ├── Docstring format
        │   │   ├── Type hint requirements
        │   │   └── Error handling patterns
        │   │
        │   └── CONFIG_TESTING_STANDARD.md (v5.0 - DEFINITION)
        │       ├── Configuration patterns
        │       ├── Testing infrastructure
        │       └── Coverage targets
```

---

## 6. Open Questions

1. **Timeline for v5.0 Code Quality/Testing adoption:**
   - Current status: Definition documents only
   - Question: When should full compliance be targeted?

2. **CI/CD integration:**
   - Current: mypy passes with 0 errors
   - Question: Should coverage thresholds be enforced in CI?

---

## Sources

### Primary (HIGH confidence)
- `docs/ARCHITECTURE_STANDARD.md` - v6.1 (2026-02-14) - IMPLEMENTED
- `docs/CODE_QUALITY_STANDARD.md` - v5.0 (2026-02-13) - DEFINITION
- `docs/CONFIG_TESTING_STANDARD.md` - v5.0 (2026-02-13) - DEFINITION

### References
- [Python Packaging Authority - src-layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)
- [PEP 8 - Style Guide](https://peps.python.org/pep-0008/)
- [Google Python Style Guide - Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)

---

## Metadata

**Confidence breakdown:**
- Architecture Standard: HIGH - v6.1 implemented and verified
- Code Quality Standard: HIGH - Well-documented definition
- Testing Standard: HIGH - Clear requirements documented

**Research date:** 2026-02-14
**Valid until:** 30 days (stable standards)
