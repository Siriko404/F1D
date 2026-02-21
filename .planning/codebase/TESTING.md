# Testing Patterns

**Analysis Date:** 2026-02-20

## Test Framework

**Runner:**
- pytest >= 8.0
- Config: `pyproject.toml` `[tool.pytest.ini_options]`
- Import mode: `importlib` (recommended for src-layout)

**Assertion Library:**
- pytest built-in (`assert`) + `pytest.approx()` for floating-point comparisons
- `pd.isna()` / `pd.util.hash_pandas_object()` for DataFrame assertions

**Coverage:**
- `pytest-cov` >= 5.0 with branch coverage enabled
- Coverage source: `src/f1d`

**Run Commands:**
```bash
pytest tests/                                              # Run all (excludes e2e)
pytest tests/ -m "not e2e"                                # Exclude E2E tests
pytest tests/unit/                                        # Unit tests only
pytest tests/integration/                                 # Integration tests
pytest tests/ -m "not e2e" --cov=src/f1d --cov-report=term-missing  # With coverage
pytest tests/ -m slow                                     # Slow tests
pytest tests/ -m "not slow"                               # Fast tests only
pytest tests/performance/ -m performance                  # Performance benchmarks
pytest tests/regression/ -m regression                    # Regression tests
```

## Test File Organization

**Location:** Separate `tests/` directory (not co-located with source)

**Directory structure:**
```
tests/
├── conftest.py            # Shared fixtures (session/function scope)
├── factories/             # Reusable factory fixtures
│   ├── config.py          # Config factory fixtures
│   └── financial.py       # Financial data factory fixtures
├── fixtures/              # Static test data files
│   ├── baseline_checksums.json
│   └── stats_golden_output.json
├── unit/                  # Tier 1/2 unit tests
│   ├── __init__.py
│   ├── test_financial_utils.py
│   ├── test_data_validation.py
│   ├── test_panel_ols.py
│   ├── test_path_utils.py
│   ├── test_config.py
│   └── ... (44 files total)
├── integration/           # Integration + E2E tests
│   ├── test_config_integration.py
│   ├── test_full_pipeline.py
│   └── ... (13 files total)
├── performance/           # Performance regression benchmarks
│   ├── conftest.py
│   └── test_performance_*.py
├── regression/            # Output stability/regression tests
│   ├── test_output_stability.py
│   └── test_h7_h8_data_coverage.py
├── verification/          # Dry-run smoke tests
│   └── test_stage*_dryrun.py
└── utils/                 # Test utilities/harnesses
    └── regression_test_harness.py
```

**Naming:**
- Test files: `test_<module_name>.py`
- Test classes: `Test<FunctionOrFeatureName>` (PascalCase)
- Test functions: `test_<what_it_tests>` (snake_case, descriptive)

## Test Structure

**Suite Organization:**
```python
class TestCalculateFirmControls:
    """Tests for calculate_firm_controls() function."""

    def test_returns_size_as_log_assets(self, sample_compustat_factory):
        """Test that size (log assets) is computed correctly."""
        # Arrange
        compustat_df = sample_compustat_factory(n_firms=1, n_years=1, seed=42)
        compustat_df["ceq"] = compustat_df["at"] * 0.3
        row = pd.Series({"gvkey": "000000", "datadate": "2000-12-31"})

        # Act
        result = calculate_firm_controls(row, compustat_df, 2000)

        # Assert
        assert "size" in result
        assert result["size"] == pytest.approx(np.log(compustat_df.iloc[0]["at"]), rel=1e-5)
```

**Patterns:**
- One class per function/feature being tested
- Class docstring states what function is under test
- Each test method has a single-sentence docstring explaining what it tests
- Arrange/Act/Assert structure (no explicit comment labels, but implicit structure)
- `tmp_path` pytest built-in fixture for temporary files/directories
- `capsys` for capturing stdout/stderr
- `monkeypatch` for environment variable manipulation

## Mocking

**Frameworks:**
- `pytest` `monkeypatch` fixture for env vars
- `unittest.mock.patch` / `MagicMock` for integration tests
- `patch.dict(os.environ, env_vars)` for env var context managers

**Patterns:**
```python
# Environment variable mocking with monkeypatch (unit tests)
def test_validate_env_schema_success(self, monkeypatch):
    monkeypatch.setenv("WRDS_USERNAME", "test_user")
    monkeypatch.setenv("API_TIMEOUT_SECONDS", "45")
    result = validate_env_schema(schema)
    assert result["WRDS_USERNAME"] == "test_user"

# Environment variable mocking with patch.dict (factory pattern)
with patch.dict(os.environ, env_vars):
    config = EnvConfig()
    assert config.data.year_start == 2010

# MagicMock for complex objects (integration tests)
from unittest.mock import patch, MagicMock
mock_model = MagicMock()
mock_model.params = {"x1": 0.5}
```

**What to Mock:**
- Environment variables (use `monkeypatch.setenv`/`monkeypatch.delenv`)
- External services/APIs (no real network calls in tests)
- Complex fitted model objects when testing output formatting

**What NOT to Mock:**
- pandas/numpy operations (use real DataFrames)
- File I/O (use `tmp_path` with real file writes)
- Pydantic validation (test against actual models)

## Fixtures and Factories

**Factory Pattern:**
The dominant pattern is "factory fixtures" — fixtures that return callables, allowing per-test customization:

```python
# Definition in tests/factories/financial.py or tests/conftest.py
@pytest.fixture
def sample_compustat_factory() -> Callable[..., pd.DataFrame]:
    """Factory fixture to generate Compustat-style panel data."""

    def _factory(
        n_firms: int = 10,
        n_years: int = 5,
        seed: int = 42,
    ) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        # ... generate data ...
        return pd.DataFrame(data)

    return _factory

# Usage in test
def test_something(sample_compustat_factory):
    df = sample_compustat_factory(n_firms=1, n_years=1, seed=42)
```

**Available factory fixtures (in `tests/conftest.py` and `tests/factories/`):**
- `sample_compustat_factory` — Compustat panel data (gvkey, fyear, at, dlc, dltt, oancf, sale, ib)
- `sample_panel_data_factory` — panel regression data (gvkey, year, dependent, independent1..N, ff48_code)
- `sample_financial_row_factory` — single Compustat row as `pd.Series`
- `sample_config_yaml_factory` — generates temporary `project.yaml` with configurable fields
- `sample_project_config_factory` — generates `ProjectConfig` instances from factory YAML
- `sample_env_vars_factory` — generates `F1D_*` env var dicts
- `invalid_config_yaml_factory` — generates intentionally invalid configs by error type

**Static fixtures (in `tests/conftest.py`):**
- `repo_root` — session-scoped `Path` to repository root
- `subprocess_env` — session-scoped env dict with `PYTHONPATH` set for subprocess calls
- `test_data_dir` — session-scoped `Path` to `tests/fixtures/`
- `sample_dataframe` — simple 3-row DataFrame
- `sample_parquet_file` — `tmp_path`-based parquet file from `sample_dataframe`
- `sample_parquet_file_with_schema` — parquet with Unified-info schema columns
- `mock_project_config` — minimal `project.yaml` in `tmp_path`
- `sample_config_yaml` / `sample_config` — valid config fixtures
- `invalid_config_yaml` — invalid year-order config

**Location:**
- Shared/cross-test fixtures: `tests/conftest.py`
- Domain-specific factories: `tests/factories/financial.py`, `tests/factories/config.py`
- Performance-specific fixtures: `tests/performance/conftest.py`
- Static test data: `tests/fixtures/` (JSON files for checksums/golden output)

**Random seed pattern:** Always pass explicit `seed=42` (or configurable `seed` parameter) to factory fixtures for deterministic test data:
```python
rng = np.random.default_rng(seed)  # NOT np.random.seed() — use Generator API
```

## Coverage

**Requirements:**
- Overall: 30% minimum (configured in `pyproject.toml` `fail_under = 30`)
- Tier 1 CI (unit tests): 10% threshold (measured across all shared modules)
- Tier 2 CI (integration tests): 10% threshold
- Full CI suite (not e2e): 25% threshold
- Individual module targets (not enforced): `financial_utils.py` ~97%, `data_validation.py` ~92%, `iv_regression.py` ~88%, `chunked_reader.py` ~88%, `path_utils.py` ~86%, `panel_ols.py` ~72%

**Excluded from coverage:**
```
pragma: no cover
def __repr__
raise AssertionError
raise NotImplementedError
if __name__ == "__main__":
if TYPE_CHECKING:
@abstractmethod
```

**View Coverage:**
```bash
pytest tests/ -m "not e2e" --cov=src/f1d --cov-report=html
# Open htmlcov/index.html

pytest tests/ -m "not e2e" --cov=src/f1d --cov-report=term-missing
# Show missing lines in terminal
```

## Test Types

**Unit Tests (`tests/unit/`, marker `unit`):**
- Test individual functions in isolation
- Use factory fixtures for controlled data
- Cover happy path, edge cases, and error conditions
- Each public function typically has its own test class
- Focus on `src/f1d/shared/` modules (Tier 1: strict typing, high coverage targets)

**Integration Tests (`tests/integration/`, marker `integration`):**
- Test interaction between modules (config loading, pipeline steps)
- Use `autouse` fixtures for environment cleanup:
  ```python
  @pytest.fixture(autouse=True)
  def clean_environment() -> Generator[None, None, None]:
      clear_config_cache()
      # ... cleanup env vars ...
      yield
      # ... restore ...
  ```
- `pytestmark = pytest.mark.integration` at module level
- May use `pytest.skip()` for tests requiring real data files:
  ```python
  if not config_path.exists():
      pytest.skip(f"Config file not found: {config_path}")
  ```

**E2E Tests (`tests/integration/test_full_pipeline.py`, marker `e2e`):**
- `pytestmark = pytest.mark.e2e`
- Run only on `main` branch push in CI
- `--timeout=1200` (20 minutes) in CI

**Performance Tests (`tests/performance/`, marker `performance`):**
- Compare naive vs. vectorized implementations
- Use `@pytest.mark.benchmark` for timing
- Seed fixed at 42 for reproducible benchmarks
- Demonstrate speedup ratio:
  ```python
  pytestmark = pytest.mark.performance
  # Tests measure both correctness AND performance ratio
  ```

**Regression Tests (`tests/regression/`, marker `regression`):**
- SHA-256 checksum comparison against `tests/fixtures/baseline_checksums.json`
- Pattern: load output parquet → compute checksum → compare to baseline
- Use `pytest.skip()` when baseline not set or output file missing

**Verification/Dry-run Tests (`tests/verification/`):**
- Smoke tests for pipeline scripts via subprocess
- Use `subprocess_env` fixture for correct `PYTHONPATH`

## Common Patterns

**Floating-point comparison:**
```python
assert result["size"] == pytest.approx(np.log(expected_at), rel=1e-5)
assert result["leverage"] == pytest.approx(expected, rel=1e-5)
```

**NaN assertion:**
```python
assert pd.isna(result["size"])
assert pd.isna(result["market_to_book"])
```

**Exception testing with match string:**
```python
with pytest.raises(FinancialCalculationError, match="missing gvkey"):
    calculate_firm_controls(row, compustat_df, 2000)

with pytest.raises(DataValidationError, match="Missing columns"):
    validate_dataframe_schema(df, "Unified-info.parquet", Path("test.parquet"), strict=True)
```

**Parametrized tests:**
```python
@pytest.mark.parametrize("strict_mode,should_raise", [
    (True, True),
    (False, False),
])
def test_strict_mode_controls_error_raising(self, strict_mode, should_raise):
    ...
```

**Conditional skip for optional dependencies:**
```python
pytestmark = []
if not LINEARMODELS_AVAILABLE:
    pytestmark.append(pytest.mark.skip(reason="linearmodels not available"))
```

**Expected failure for known compatibility issues:**
```python
@pytest.mark.xfail(reason="pandas/numpy compatibility issue with .clip() internal sum()")
def test_winsorize_parameter_affects_output(self, sample_quarterly_df):
    ...
```

**Async Testing:** Not used — all code is synchronous.

**Subprocess testing (integration):**
```python
def test_pipeline_step(subprocess_env):
    result = subprocess.run(
        ["python", str(script_path)],
        env=subprocess_env,   # Critical: sets PYTHONPATH for src-layout
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
```

**Inline fixture definition inside test class:**
```python
class TestCalculateFirmControlsQuarterly:
    @pytest.fixture
    def sample_quarterly_compustat(self):
        """Create sample quarterly Compustat data for testing."""
        return pd.DataFrame({...})

    def test_returns_size_as_log_atq(self, sample_quarterly_compustat):
        ...
```

---

*Testing analysis: 2026-02-20*
