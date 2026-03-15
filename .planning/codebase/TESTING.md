# Testing Patterns

**Analysis Date:** 2026-03-15

## Test Framework

**Runner:**
- pytest >= 8.0
- Config: `pyproject.toml` `[tool.pytest.ini_options]`

**Assertion Library:**
- pytest built-in `assert`
- `pytest.approx()` for floating-point comparisons (with `rel=1e-5`)
- `pd.isna()` for NaN checks

**Run Commands:**
```bash
pytest tests/                          # Run all tests (excluding e2e)
pytest tests/ -m "not e2e"             # Run all non-e2e tests
pytest tests/unit/                     # Run unit tests only
pytest tests/integration/              # Run integration tests only
pytest tests/ -m e2e                   # Run end-to-end tests only
pytest tests/ -m slow                  # Run slow-marked tests
pytest tests/ --cov=src/f1d --cov-report=term-missing  # With coverage
```

## Test File Organization

**Location:**
- Tests are in a separate `tests/` directory (not co-located with source)
- Mirrors source structure loosely but not strictly

**Naming:**
- Pattern: `test_{module_name}.py` or `test_{feature}.py`
- Examples: `test_financial_utils.py`, `test_panel_ols.py`, `test_h1_regression.py`

**Structure:**
```
tests/
├── conftest.py                    # Root-level shared fixtures and factory fixtures
├── factories/                     # Factory fixtures for test data generation
│   ├── __init__.py
│   ├── config.py                  # Config factory fixtures
│   └── financial.py               # Financial data factory fixtures
├── fixtures/                      # Synthetic data generators
│   ├── __init__.py
│   ├── synthetic_generator.py     # E2E synthetic input generator
│   └── synthetic_panel.py         # Synthetic panel data for hypothesis tests
├── integration/                   # Integration tests (cross-module, subprocess)
│   ├── __init__.py
│   ├── test_ceo_fixed_effects.py
│   ├── test_config_integration.py
│   ├── test_error_propagation.py
│   ├── test_logging_*.py
│   ├── test_observability_integration.py
│   └── test_pipeline_e2e.py       # Full pipeline E2E test
├── performance/                   # Performance regression tests
│   ├── conftest.py
│   ├── test_performance_h2_variables.py
│   └── test_performance_link_entities.py
├── regression/                    # Output stability / regression tests
│   ├── generate_baseline_checksums.py
│   ├── test_output_stability.py
│   └── test_survival_analysis_integration.py
├── unit/                          # Unit tests (single module scope)
│   ├── shared/variables/          # Variable-specific unit tests
│   │   └── test_winsorization.py
│   ├── test_financial_utils.py
│   ├── test_panel_ols.py
│   ├── test_iv_regression.py
│   ├── test_data_validation.py
│   ├── test_h1_regression.py      # Hypothesis regression tests
│   ├── test_h2_regression.py
│   ├── ... (test_h{N}_*.py)
│   └── test_types.py
├── utils/                         # Shared test utilities
│   ├── __init__.py
│   └── regression_test_harness.py # Mock result generators for regressions
└── verification/                  # Dry-run / script verification tests
    ├── test_all_scripts_dryrun.py
    └── test_stage{N}_dryrun.py
```

## Test Structure

**Suite Organization:**
```python
"""
Unit tests for f1d.shared.financial_utils module.

Tests verify financial calculation functions work correctly with edge cases:
- Missing data handling
- NaN values in Compustat fields
- Boundary conditions (zero, negative values)
"""

import pytest
import pandas as pd
import numpy as np

from f1d.shared.financial_utils import calculate_firm_controls
from f1d.shared.data_validation import FinancialCalculationError


class TestCalculateFirmControls:
    """Tests for calculate_firm_controls() function."""

    def test_returns_size_as_log_assets(self, sample_compustat_factory):
        """Test that size (log assets) is computed correctly."""
        compustat_df = sample_compustat_factory(n_firms=1, n_years=1, seed=42)
        # ... setup ...
        result = calculate_firm_controls(row, compustat_df, 2000)
        assert result["size"] == pytest.approx(np.log(expected_at), rel=1e-5)

    def test_raises_error_on_missing_gvkey(self, sample_compustat_factory):
        """Test that missing gvkey raises FinancialCalculationError."""
        # ... setup ...
        with pytest.raises(FinancialCalculationError, match="missing gvkey"):
            calculate_firm_controls(row, compustat_df, 2000)
```

**Patterns:**
- Group tests by class per function/feature: `class TestCalculateFirmControls:`
- One assertion per test (generally); multiple related assertions in "all keys present" tests
- Descriptive test names: `test_{what_it_does}` or `test_handles_{edge_case}`
- Docstrings on every test method: brief one-line description

**Markers (defined in `pyproject.toml`):**
```python
@pytest.mark.slow        # Deselect with -m "not slow"
@pytest.mark.integration # Integration tests
@pytest.mark.regression  # Output stability tests
@pytest.mark.unit        # Unit tests
@pytest.mark.e2e         # End-to-end pipeline tests
@pytest.mark.performance # Performance regression tests
@pytest.mark.mypy_testing # Type checking tests
```

**xfail usage for known issues:**
```python
@pytest.mark.xfail(reason="pandas/numpy compatibility issue with .clip() internal sum()")
def test_winsorize_parameter_affects_output(self, sample_quarterly_df):
    ...
```

## Mocking

**Framework:** pytest-mock (via `mocker` fixture) and `unittest.mock`

**Patterns:**

Skip tests when optional dependency missing:
```python
pytestmark = []
if not LINEARMODELS_AVAILABLE:
    pytestmark.append(pytest.mark.skip(reason="linearmodels not available"))
```

Mock panel OLS results (from `tests/utils/regression_test_harness.py`):
```python
from tests.utils.regression_test_harness import create_mock_panel_ols_result

mock_result = create_mock_panel_ols_result(
    coefficients={
        "Manager_QA_Uncertainty_pct": (0.05, 0.02),
        "Size": (-0.03, 0.01),
    },
    rsquared=0.30,
    nobs=200,
)
```

**What to Mock:**
- External subprocess calls (via `subprocess_env` fixture)
- Optional dependencies not guaranteed available (`linearmodels`)
- Complex regression model fits (use `create_mock_panel_ols_result()`)

**What NOT to Mock:**
- pandas/numpy operations (test the actual computations)
- Config loading (use real YAML fixtures via factory fixtures)
- Financial calculations (these are the core logic being tested)

## Fixtures and Factories

**Factory Pattern (primary approach):**
Factory fixtures return callables that generate test data with customizable parameters.
Defined in both `tests/conftest.py` and `tests/factories/`.

```python
# From tests/conftest.py
@pytest.fixture
def sample_compustat_factory() -> Callable[..., pd.DataFrame]:
    """Factory fixture to generate Compustat-style panel data."""
    def _factory(
        n_firms: int = 10,
        n_years: int = 5,
        seed: int = 42,
    ) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        # ... generate realistic financial data ...
        return pd.DataFrame(data)
    return _factory

# Usage in tests:
def test_asset_calculation(sample_compustat_factory):
    df = sample_compustat_factory(n_firms=10, n_years=5)
    assert len(df) == 50
```

**Available Factory Fixtures:**

| Fixture | Returns | Location |
|---------|---------|----------|
| `sample_compustat_factory` | `Callable[..., pd.DataFrame]` | `tests/conftest.py`, `tests/factories/financial.py` |
| `sample_panel_data_factory` | `Callable[..., pd.DataFrame]` | `tests/conftest.py`, `tests/factories/financial.py` |
| `sample_financial_row_factory` | `Callable[..., pd.Series]` | `tests/conftest.py`, `tests/factories/financial.py` |
| `sample_config_yaml_factory` | `Callable[..., Path]` | `tests/conftest.py` |
| `sample_project_config_factory` | `Callable[..., ProjectConfig]` | `tests/conftest.py` |
| `sample_env_vars_factory` | `Callable[..., Dict[str, str]]` | `tests/conftest.py` |
| `invalid_config_yaml_factory` | `Callable[..., Path]` | `tests/conftest.py` |

**Simple Fixtures:**

| Fixture | Scope | Purpose |
|---------|-------|---------|
| `repo_root` | session | Path to repository root |
| `subprocess_env` | session | Env vars with PYTHONPATH for subprocess calls |
| `test_data_dir` | session | Path to `tests/fixtures/` |
| `sample_dataframe` | function | Simple 3-row test DataFrame |
| `sample_parquet_file` | function | Temp parquet file from sample_dataframe |
| `sample_config` | function | Valid `ProjectConfig` instance |
| `capture_output` | function | stdout/stderr capture helper |
| `tmp_path` | function | pytest built-in temp directory |

**Synthetic Data Generators (for integration/E2E):**
- `tests/fixtures/synthetic_panel.py`: Functions like `synthetic_manager_clarity_panel()` for hypothesis-specific test data
- `tests/fixtures/synthetic_generator.py`: `generate_synthetic_inputs()` for full pipeline E2E tests

**Location:**
- Factory fixtures: `tests/conftest.py` (duplicated in `tests/factories/`)
- Synthetic generators: `tests/fixtures/`
- Test utilities: `tests/utils/`

## Coverage

**Requirements:**
- Tier 1 tests: 10% threshold (individual tested modules have 70%+ coverage)
- Tier 2 tests: 10% threshold (individual tested modules have 80%+ coverage)
- Full suite: 40% overall (measured across ALL `src/f1d/` modules)
- Branch coverage: enabled (`branch = true`)
- Current actual coverage: ~25-30% across all modules

**Configuration:** `pyproject.toml` `[tool.coverage.*]` sections

**View Coverage:**
```bash
pytest tests/ --cov=src/f1d --cov-report=html    # Generate HTML report in htmlcov/
pytest tests/ --cov=src/f1d --cov-report=term-missing  # Terminal with missing lines
```

**Excluded from coverage:**
- `pragma: no cover` comments
- `__repr__` methods
- `raise NotImplementedError` / `raise AssertionError`
- `if __name__ == "__main__":` blocks
- `if TYPE_CHECKING:` blocks
- `@abstractmethod` decorated methods

## Test Types

**Unit Tests (`tests/unit/`):**
- Scope: single function or class
- No filesystem I/O except `tmp_path`
- No subprocess calls
- Use factory fixtures for test data
- ~45 test files covering shared modules and hypothesis-specific logic

**Integration Tests (`tests/integration/`):**
- Scope: cross-module interactions
- May use `subprocess_env` fixture for script invocation
- Test config loading, logging integration, error propagation
- ~7 test files

**E2E Tests (`tests/integration/test_pipeline_e2e.py`):**
- Scope: full pipeline on synthetic data
- Creates temporary workspace with `synthetic_workspace` fixture
- Copies `src/` and `config/` to temp dir, generates synthetic inputs
- Runs pipeline scripts via `subprocess.run()`
- Marked with `@pytest.mark.e2e`, excluded from default test runs
- Only runs on push to main in CI

**Performance Tests (`tests/performance/`):**
- Scope: execution time regression detection
- Use `.benchmarks/` baseline files for comparison
- Marked with `@pytest.mark.performance`

**Regression Tests (`tests/regression/`):**
- Scope: output stability (checksums match baselines)
- `generate_baseline_checksums.py` creates baselines
- `test_output_stability.py` verifies outputs match

**Verification Tests (`tests/verification/`):**
- Scope: dry-run all pipeline scripts to verify imports and CLI parsing
- Stage-specific: `test_stage{N}_dryrun.py`

## Common Patterns

**Floating-Point Assertions:**
```python
assert result["size"] == pytest.approx(np.log(expected_at), rel=1e-5)
assert result["leverage"] == pytest.approx(expected, rel=1e-5)
```

**NaN Assertions:**
```python
assert pd.isna(result["market_to_book"])
assert pd.isna(result["Size"])
```

**Error Testing:**
```python
with pytest.raises(FinancialCalculationError, match="missing gvkey"):
    calculate_firm_controls(row, compustat_df, 2000)

with pytest.raises(FinancialCalculationError, match="no Compustat data found"):
    calculate_firm_controls(row, compustat_df, 1999)
```

**Testing All Expected Keys:**
```python
expected_keys = ["size", "leverage", "profitability", "market_to_book",
                 "capex_intensity", "r_intensity", "dividend_payer"]
for key in expected_keys:
    assert key in result, f"Missing key: {key}"
```

**Subprocess Integration Tests:**
```python
def test_my_script(subprocess_env):
    result = subprocess.run(
        [sys.executable, str(script_path)],
        env=subprocess_env,  # Critical: enables f1d.shared imports
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
```

## CI Pipeline

**Workflow:** `.github/workflows/ci.yml`

**Stages (sequential):**
1. **Lint** (Python 3.11): `ruff check`, `ruff format --diff`, `mypy src/f1d/shared`
2. **Test** (matrix: 3.9, 3.10, 3.11, 3.12, 3.13):
   - Tier 1 tests (core shared modules): 10% coverage threshold
   - Tier 2 tests (integration + utilities): 10% coverage threshold
   - Full suite (excl. e2e): 40% coverage threshold
   - Upload coverage to Codecov
3. **E2E** (Python 3.11, push to main only): `pytest tests/ -m e2e --timeout=1200`

**Import mode:** `--import-mode=importlib` (recommended for src-layout)

**Strict markers:** `--strict-markers` and `--strict-config` enabled

---

*Testing analysis: 2026-03-15*
