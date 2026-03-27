# Testing Patterns

**Analysis Date:** 2026-03-25

## Test Framework & Tools

**Runner:**
- pytest >= 8.0
- Config: `pyproject.toml` `[tool.pytest.ini_options]`
- Import mode: `--import-mode=importlib` (required for src-layout)
- Strict mode: `--strict-markers` and `--strict-config` enabled

**Assertion Library:**
- pytest built-in `assert`
- `pytest.approx()` for floating-point comparisons (with `rel=1e-5`)
- `pd.isna()` for NaN checks

**Plugins:**
- `pytest-cov >= 5.0` -- coverage measurement
- `pytest-mock >= 3.12` -- mock fixtures (mocker)

**Run Commands:**
```bash
pytest tests/                          # Run all tests (excluding e2e by default)
pytest tests/ -m "not e2e"             # Run all non-e2e tests
pytest tests/unit/                     # Run unit tests only
pytest tests/integration/              # Run integration tests only
pytest tests/ -m e2e                   # Run end-to-end tests only
pytest tests/ -m slow                  # Run slow-marked tests
pytest tests/ --cov=src/f1d --cov-report=term-missing  # With coverage
pytest tests/ --cov=src/f1d --cov-report=html          # HTML coverage report in htmlcov/
```

## Test Organization

**Location:**
- Tests are in a separate `tests/` directory at project root (not co-located with source)
- Loosely mirrors source structure

**Naming:**
- Pattern: `test_{module_name}.py` or `test_{feature}.py`
- Examples: `test_financial_utils.py`, `test_panel_ols.py`, `test_h1_regression.py`

**Structure:**
```
tests/
├── __init__.py
├── conftest.py                    # Root-level shared fixtures + factory fixtures
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
│   ├── test_logging_config_integration.py
│   ├── test_logging_integration.py
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
│   ├── __init__.py
│   ├── shared/variables/          # Variable-specific unit tests
│   │   └── test_winsorization.py
│   ├── test_auxiliary_financial_variables.py
│   ├── test_calculate_throughput.py
│   ├── test_chunked_reader.py
│   ├── test_clarity_formula.py
│   ├── test_config.py
│   ├── test_data_loading.py
│   ├── test_data_validation.py
│   ├── test_data_validation_edge_cases.py
│   ├── test_edge_cases.py
│   ├── test_env_validation.py
│   ├── test_env_validation_edge_cases.py
│   ├── test_financial_utils.py
│   ├── test_financial_utils_exceptions.py
│   ├── test_fuzzy_matching.py
│   ├── test_h01_manager_clarity.py
│   ├── test_h1_regression.py
│   ├── test_h1_variables.py
│   ├── test_h2_regression.py
│   ├── test_h3_regression.py
│   ├── test_h4_regression.py
│   ├── test_h5_regression.py
│   ├── test_h5_variables.py
│   ├── test_h6_h7_h9_regression.py
│   ├── test_h7_regression.py
│   ├── test_h9_regression.py
│   ├── test_h12_div_intensity.py
│   ├── test_industry_utils.py
│   ├── test_iv_regression.py
│   ├── test_logging_context.py
│   ├── test_logging_handlers.py
│   ├── test_metadata_utils.py
│   ├── test_observability_helpers.py
│   ├── test_panel_ols.py
│   ├── test_path_utils.py
│   ├── test_pipeline_integrity.py
│   ├── test_regression_helpers.py
│   ├── test_stats_module.py
│   ├── test_subprocess_validation.py
│   ├── test_subprocess_validation_edge_cases.py
│   ├── test_summary_stats.py
│   ├── test_takeover_survival_analysis.py
│   ├── test_types.py
│   ├── test_v1_ceo_clarity.py
│   ├── test_v1_econometric.py
│   ├── test_v1_financial_features.py
│   └── test_v2_econometric.py
├── utils/                         # Shared test utilities
│   ├── __init__.py
│   └── regression_test_harness.py # Mock result generators for regressions
└── verification/                  # Dry-run / script verification tests
    ├── __init__.py
    ├── test_all_scripts_dryrun.py
    ├── test_stage1_dryrun.py
    ├── test_stage2_dryrun.py
    ├── test_stage3_dryrun.py
    └── test_stage4_dryrun.py
```

## Test Structure

**Suite Organization:**
```python
"""
Unit tests for f1d.shared.panel_ols module.

Tests verify panel regression wrapper functions:
- Parameter validation
- Mock data handling
- Result formatting
- VIF calculation for multicollinearity
- Edge cases and error handling
"""

import pytest
import pandas as pd
import numpy as np

from f1d.shared.panel_ols import (
    run_panel_ols,
    _check_thin_cells,
    CollinearityError,
    LINEARMODELS_AVAILABLE,
)


class TestCheckThinCells:
    """Tests for _check_thin_cells() function."""

    def test_no_thin_cells(self):
        """Test with all cells having sufficient firms."""
        df = pd.DataFrame({...})
        has_thin, cell_counts = _check_thin_cells(df, "ff48_code", "year", min_firms=5)
        assert has_thin is True

    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
        df = pd.DataFrame({"ff48_code": [], "year": []})
        has_thin, cell_counts = _check_thin_cells(df, "ff48_code", "year", min_firms=5)
        assert has_thin is False
        assert cell_counts == {}
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

**Conditional skip for optional dependencies:**
```python
pytestmark = []
if not LINEARMODELS_AVAILABLE:
    pytestmark.append(pytest.mark.skip(reason="linearmodels not available"))
```

## Mocking

**Framework:** pytest-mock (via `mocker` fixture) and `unittest.mock`

**Patterns:**

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

Subprocess testing with env fixture:
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
Defined in `tests/conftest.py` (canonical location).

```python
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

**Available Factory Fixtures (all in `tests/conftest.py`):**

| Fixture | Returns | Purpose |
|---------|---------|---------|
| `sample_compustat_factory` | `Callable[..., pd.DataFrame]` | Compustat-style panel with gvkey, fyear, at, dlc, dltt, oancf, sale, ib |
| `sample_panel_data_factory` | `Callable[..., pd.DataFrame]` | Panel data with gvkey, year, dependent, independent vars, ff48_code |
| `sample_financial_row_factory` | `Callable[..., pd.Series]` | Single Compustat row for per-row function testing |
| `sample_config_yaml_factory` | `Callable[..., Path]` | Temporary project.yaml files with customizable settings |
| `sample_project_config_factory` | `Callable[..., ProjectConfig]` | ProjectConfig instances loaded from generated YAML |
| `sample_env_vars_factory` | `Callable[..., Dict[str, str]]` | F1D-prefixed environment variable dicts |
| `invalid_config_yaml_factory` | `Callable[..., Path]` | Invalid YAML configs for error-handling tests |

**Simple Fixtures:**

| Fixture | Scope | Purpose |
|---------|-------|---------|
| `repo_root` | session | Path to repository root |
| `subprocess_env` | session | Env vars with PYTHONPATH for subprocess calls |
| `test_data_dir` | session | Path to `tests/fixtures/` |
| `sample_dataframe` | function | Simple 3-row test DataFrame |
| `sample_parquet_file` | function | Temp parquet file from sample_dataframe |
| `sample_config` | function | Valid `ProjectConfig` instance |
| `invalid_config_yaml` | function | YAML with year_start > year_end |
| `capture_output` | function | stdout/stderr capture helper |
| `tmp_path` | function | pytest built-in temp directory |

**Synthetic Data Generators (for integration/E2E):**
- `tests/fixtures/synthetic_panel.py`: Functions like `synthetic_manager_clarity_panel(n_rows, seed)` for hypothesis-specific test data with known structure
- `tests/fixtures/synthetic_generator.py`: `generate_synthetic_inputs()` for full pipeline E2E tests

**Location:**
- Factory fixtures: `tests/conftest.py` (also duplicated in `tests/factories/`)
- Synthetic generators: `tests/fixtures/`
- Test utilities: `tests/utils/`

## Coverage

**Requirements (tiered):**
- Tier 1 tests (core shared): 10% threshold (individual tested modules have 70%+ individually)
- Tier 2 tests (integration + utilities): 10% threshold (individual tested modules have 80%+ individually)
- Full suite: 40% overall (CI target, measured across ALL `src/f1d/` modules)
- Minimum floor in pyproject.toml: `fail_under = 30`
- Branch coverage: enabled (`branch = true`)

**Individual module coverage (reference):**
- `financial_utils.py`: 97.75%
- `data_validation.py`: 92.00%
- `iv_regression.py`: 88.21%
- `chunked_reader.py`: 88.24%
- `path_utils.py`: 86.09%
- `panel_ols.py`: 72.08%

**Note:** The low aggregate threshold (10-40%) is because coverage measures ALL modules in `src/f1d/`, including many untested engines and variable builders. The individually tested modules have strong coverage.

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
- V1 scripts: `*/V1*`

## Test Types

**Unit Tests (`tests/unit/`):**
- Scope: single function or class
- No filesystem I/O except `tmp_path`
- No subprocess calls
- Use factory fixtures for test data
- ~48 test files covering shared modules and hypothesis-specific logic
- Tests both positive cases and edge cases (NaN, empty, missing columns, zero values)

**Integration Tests (`tests/integration/`):**
- Scope: cross-module interactions
- May use `subprocess_env` fixture for script invocation
- Test config loading, logging integration, error propagation, CEO fixed effects
- 7 test files

**E2E Tests (`tests/integration/test_pipeline_e2e.py`):**
- Scope: full pipeline on synthetic data
- Creates temporary workspace with `synthetic_workspace` fixture (session-scoped)
- Copies `src/` and `config/` to temp dir, generates synthetic inputs via `generate_synthetic_inputs()`
- Runs pipeline scripts via `subprocess.run()` with proper `PYTHONPATH`
- Marked with `@pytest.mark.e2e`, excluded from default test runs
- Only runs on push to main in CI (`if: github.event_name == 'push' && github.ref == 'refs/heads/main'`)

**Performance Tests (`tests/performance/`):**
- Scope: execution time regression detection
- Use `.benchmarks/` baseline files for comparison
- Has own `conftest.py` for performance-specific fixtures
- Marked with `@pytest.mark.performance`

**Regression Tests (`tests/regression/`):**
- Scope: output stability via SHA-256 checksums
- `generate_baseline_checksums.py`: creates baseline checksum file at `tests/fixtures/baseline_checksums.json`
- `test_output_stability.py`: compares current output checksums against baselines
- Uses `pd.util.hash_pandas_object()` for deterministic DataFrame hashing
- Skips gracefully when outputs or baselines not present
- Marked with `@pytest.mark.regression`

**Verification Tests (`tests/verification/`):**
- Scope: dry-run all pipeline scripts to verify imports, CLI parsing, and `--dry-run` flag
- Stage-specific: `test_stage1_dryrun.py` through `test_stage4_dryrun.py`
- `test_all_scripts_dryrun.py`: comprehensive sweep of all scripts
- Tests that scripts exist, can be imported, and handle `--dry-run` without errors

## Common Test Patterns

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
def test_script_exists(self, script: str):
    script_path = REPO_ROOT / script
    assert script_path.exists(), f"Script not found: {script_path}"

def test_dry_run(subprocess_env):
    result = subprocess.run(
        [sys.executable, str(script_path), "--dry-run"],
        env=subprocess_env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
```

**Output String Assertions (for formatting tests):**
```python
output = _format_coefficient_table(sample_coefficients, sample_pvalues)
assert "REGRESSION RESULTS" in output
assert "***" in output  # Significance stars
assert "Variance Inflation Factors:" in output  # VIF section
```

## Verification Approach

### Automated Testing (pytest)

The pytest test suite covers shared utilities, financial calculations, panel regression wrappers, config loading, logging, and data validation. Tests use synthetic data generated by factory fixtures -- no real data in the test suite.

### Provenance Auditing (manual + systematic)

The primary quality verification mechanism is **provenance documentation** -- systematic audit documents for each of 19 active hypothesis suites.

**Provenance doc structure (per suite):**
- `docs/provenance/{SUITE_ID}.md`: Definitive provenance document
  - Suite overview, model specification, variable definitions
  - Data flow with exact file paths and line numbers
  - Identification strategy and limitations table
  - Sample attrition accounting
  - Version-controlled with amendment history
- `docs/provenance/Audits/{SUITE_ID}_red_team.md`: Adversarial red-team audit
  - Hostile-but-fair review of the provenance doc AND the code
  - Claim verification matrix (audit claim vs code location vs verified status)
  - Scorecard grading: factual accuracy, completeness, econometric rigor, reproducibility
  - Findings classified: CRITICAL, MAJOR, MINOR, STYLE
  - Verdict: PASS/FAIL with corrections

**Suites with full provenance + red-team audit (19):**
H0.3, H1, H1.1, H1.2, H2, H4, H5, H5b (Johnson), H6, H7, H9, H11, H11-Lag, H11-Lead, H12, H12Q, H13, H13.1, H14, H15, H16

**Red-team audit protocol:**
1. Independent code-and-output verification
2. Every quantitative claim traced to specific code line
3. Variable formulas verified against source (Compustat engine, CRSP engine, etc.)
4. Sample sizes, coefficient signs, significance patterns checked
5. Limitation identification (reverse causality, OVB, multiple testing, etc.)
6. Graded on 6 dimensions: factual accuracy, completeness, skepticism, econometric rigor, reproducibility, transparency

### Regression Stability Testing

- SHA-256 checksums of output Parquet files compared against baselines
- Detects unintended changes to data processing logic
- Baselines generated by `tests/regression/generate_baseline_checksums.py`
- Tests in `tests/regression/test_output_stability.py`

### Dry-Run Verification

- Every pipeline script supports `--dry-run` flag
- Dry-run validates inputs, imports, and CLI parsing without executing
- Automated via `tests/verification/test_stage{N}_dryrun.py`
- Catches import errors, missing config files, and broken CLI interfaces

### Additional Quality Artifacts

- `docs/audits/`: Cross-cutting methodology and data audits (5 documents)
- `outputs/econometric/{suite}/{timestamp}/model_diagnostics.csv`: Per-run regression diagnostics
- `outputs/econometric/{suite}/{timestamp}/sample_attrition.csv`: Sample filter accounting
- `outputs/econometric/{suite}/{timestamp}/run_manifest.json`: Input/output provenance per run

## CI Pipeline

**Workflows:**
- `.github/workflows/ci.yml` -- Primary CI (lint + test + e2e)
- `.github/workflows/test.yml` -- Extended test workflow (security + multi-python + e2e)

**CI stages (sequential, from `ci.yml`):**
1. **Lint** (Python 3.11):
   - `ruff check --output-format=github` (linting)
   - `ruff format --diff` (formatting check)
   - `mypy src/f1d/shared --config-file pyproject.toml` (type checking Tier 1)
2. **Test** (matrix: 3.9, 3.10, 3.11, 3.12, 3.13):
   - Tier 1 tests (panel_ols, iv_regression, data_validation): 10% coverage threshold
   - Tier 2 tests (integration, path_utils, chunked_reader): 10% coverage threshold
   - Full suite (excl. e2e): 40% coverage threshold
   - Upload coverage to Codecov
3. **E2E** (Python 3.11, push to main only): `pytest tests/ -m e2e -v --timeout=1200`

**Extended test workflow (`test.yml`) adds:**
- Bandit security scanning before tests
- Coverage summary in GitHub Step Summary
- HTML coverage report as artifact

---

*Testing analysis: 2026-03-25*
