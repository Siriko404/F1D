# Testing Patterns

**Analysis Date:** 2026-02-14

## Test Framework

**Runner:**
- pytest [version 8.0+]
- Config: `pyproject.toml` [tool.pytest.ini_options]
- Test discovery: `tests/` directory
- Import mode: `importlib` (Python 3.9+)

**Assertion Library:**
- pytest built-in assertions (`assert`, `pytest.raises`)
- No separate assertion library used

**Run Commands:**
```bash
# Run all tests
pytest

# Run specific test type
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests only
pytest -m regression    # Regression tests only
pytest -m performance    # Performance tests only
pytest -m e2e           # End-to-end tests only

# Exclude slow tests
pytest -m "not slow"

# Watch mode (not configured in pyproject.toml)
pytest -x -s

# Coverage
pytest --cov=src/f1d --cov-report=html --cov-report=term

# Coverage with specific packages
pytest --cov=src/f1d.shared --cov-report=xml

# Show extra test summary
pytest -ra
```

## Test File Organization

**Location:**
- Co-located in `tests/` directory
- Parallel structure to `src/f1d/`
- `tests/unit/` - Unit tests for shared modules
- `tests/integration/` - Integration tests for workflows
- `tests/regression/` - Regression tests for stability
- `tests/performance/` - Performance regression tests
- `tests/verification/` - Dry-run tests for pipeline stages
- `tests/fixtures/` - Test data and configuration files

**Naming:**
- `test_{module_name}.py` - Test files matching source modules
- Examples: `test_financial_utils.py`, `test_path_utils.py`, `test_data_validation.py`, `test_iv_regression.py`
- Pattern: snake_case with `test_` prefix

**Structure:**
```
tests/
├── conftest.py                    # Shared fixtures for all tests
├── unit/                          # Unit tests
│   ├── test_financial_utils.py
│   ├── test_path_utils.py
│   ├── test_data_validation.py
│   └── ...
├── integration/                   # Integration tests
│   ├── test_config_integration.py
│   ├── test_logging_integration.py
│   └── ...
├── regression/                    # Regression tests
│   ├── test_output_stability.py
│   └── ...
├── performance/                    # Performance tests
│   ├── conftest.py
│   └── test_performance_*.py
└── verification/                  # Verification tests
    ├── conftest.py
    └── test_all_scripts_dryrun.py
```

## Test Structure

**Suite Organization:**
```python
"""Module docstring with test coverage description."""

import pytest
from f1d.shared.module_name import function_to_test

# Module-level pytestmark for all tests in file
pytestmark = pytest.mark.integration


class TestFunctionalityGroup:
    """Tests grouped by functionality using class-based organization."""

    def test_descriptive_name(self, fixture_name):
        """Test case description."""
        # Arrange
        test_data = fixture_name

        # Act
        result = function_to_test(test_data)

        # Assert
        assert result == expected
```

**Patterns:**
- **Setup:** Use fixtures for test data and configuration
- **Arrange-Act-Assert:** Clear test structure
- **Teardown:** No explicit teardown (pytest handles fixture cleanup)
- **Assertion:** pytest.raises() for exception testing

**Example test function:**
```python
def test_returns_size_as_log_assets(self, sample_compustat_factory):
    """Test that size (log assets) is computed correctly."""
    # Arrange
    compustat_df = sample_compustat_factory(n_firms=1, n_years=1, seed=42)
    compustat_df["ceq"] = compustat_df["at"] * 0.3
    compustat_df["prcc_f"] = 50.0
    compustat_df["csho"] = 10.0
    compustat_df["oibdp"] = compustat_df["at"] * 0.2
    compustat_df["dvc"] = 10.0
    compustat_df["capx"] = compustat_df["at"] * 0.08
    compustat_df["xrd"] = compustat_df["at"] * 0.05

    row = pd.Series({"gvkey": "000000", "datadate": "2000-12-31"})

    # Act
    result = calculate_firm_controls(row, compustat_df, 2000)

    # Assert
    assert "size" in result
    assert result["size"] == pytest.approx(np.log(compustat_df.iloc[0]["at"]), rel=1e-5)
```

## Mocking

**Framework:** pytest-mock
- Use `unittest.mock` via `pytest` imports
- Direct imports in test files: `import pytest`
- Mocking via `pytest.fixture` with `monkeypatch`

**Patterns:**
```python
# Mocking with monkeypatch
def test_validates_without_prior_load(self):
    """Test that reload_config raises ValueError if no config loaded."""
    clear_config_cache()
    with pytest.raises(ValueError, match="No configuration has been loaded"):
        reload_config()

# Mocking files
def test_with_missing_required_file(self, tmp_path):
    """Test FileNotFoundError for missing config file."""
    config_path = tmp_path / "nonexistent.yaml"
    with pytest.raises(FileNotFoundError, match="Configuration file not found"):
        get_config(config_path)
```

**What to Mock:**
- External dependencies: `os.environ`, `Path.exists()`, file I/O operations
- Configuration loading
- Network calls (if any)
- Time-based operations (for deterministic tests)

**What NOT to Mock:**
- Pure calculation functions (test with real inputs)
- Pandas/numpy operations
- Business logic (test end-to-end)

## Fixtures and Factories

**Test Data:**
- `sample_parquet_file` - Creates test parquet file
- `sample_dataframe` - Creates test DataFrame
- `small_parquet_file` - Creates small file for edge cases
- `empty_parquet_file` - Creates empty file
- Location: `tests/conftest.py` and local fixtures in test files

**Factory fixtures:**
```python
@pytest.fixture
def sample_compustat_factory():
    """Factory fixture to generate Compustat-style panel data."""
    def _factory(
        n_firms: int = 10,
        n_years: int = 5,
        seed: int = 42,
    ) -> pd.DataFrame:
        # Generate test data with given parameters
        ...

    return _factory


# Using the factory
def test_with_custom_data(sample_compustat_factory):
    df = sample_compustat_factory(n_firms=5, n_years=3)
    assert len(df) == 15  # 5 firms * 3 years
```

**Configuration fixtures:**
```python
@pytest.fixture
def sample_config_yaml_factory(tmp_path):
    """Factory fixture to generate temporary YAML config files."""
    def _factory(**kwargs) -> Path:
        config_data = {
            "project": {
                "name": "TestProject",
                "version": "1.0.0",
            },
            # ... additional fields
        }
        # Merge kwargs
        for key, value in kwargs.items():
            if key in config_data and isinstance(config_data[key], dict):
                config_data[key].update(value)

        config_path = tmp_path / "project.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)
        return config_path

    return _factory
```

**Environment fixtures:**
```python
@pytest.fixture(scope="session")
def subprocess_env():
    """Provide environment variables for subprocess calls in integration tests."""
    import os
    from pathlib import Path

    repo_root = Path(__file__).parent.parent
    return {
        "PYTHONPATH": str(repo_root / "src" / "f1d"),
        **os.environ,  # Preserve existing environment variables
    }


# Using subprocess_env in integration tests
def test_script_execution(subprocess_env):
    result = subprocess.run(
        ["python", str(script_path)],
        env=subprocess_env,
        ...
    )
```

**Location:**
- Shared fixtures: `tests/conftest.py`
- Module-specific fixtures: In test files using `@pytest.fixture`
- Subdirectory fixtures: `tests/{type}/conftest.py`

## Coverage

**Requirements:** 25% overall (measured across all shared modules)
- Individual tested modules have 70%+ coverage
- Tier 1 tests: 10% minimum (tested modules have 70%+)
- Tier 2 tests: 10% minimum (tested modules have 80%+)
- Coverage targets defined in `pyproject.toml` [tool.coverage.report]

**View Coverage:**
```bash
# HTML report
pytest --cov=src/f1d --cov-report=html

# Terminal report
pytest --cov=src/f1d --cov-report=term-missing

# XML report (for CI)
pytest --cov=src/f1d.shared --cov-report=xml

# Coverage configuration
# pyproject.toml [tool.coverage.*] sections
# .coveragerc file (local override)
```

**Exclusions:**
- `tests/*` - Test files excluded
- `*/__pycache__/*` - Cache excluded
- `*/ARCHIVE*/*` - Archived code excluded
- `*/ARCHIVE_OLD*/*` - Legacy archives excluded
- `*/V1*` - V1 scripts excluded
- `def __repr__` - Excluded from coverage
- `raise AssertionError` - Excluded
- `raise NotImplementedError` - Excluded
- `if __name__ == "__main__":` - Excluded
- `if TYPE_CHECKING:` - Excluded
- `@abstractmethod` - Excluded

## Test Types

**Unit Tests:**
- Location: `tests/unit/`
- Scope: Test individual functions and classes
- Approach: Isolate unit under test, use fixtures for inputs
- Examples: `test_financial_utils.py`, `test_path_utils.py`, `test_data_validation.py`
- Coverage: Shared utility modules

**Integration Tests:**
- Location: `tests/integration/`
- Scope: Test module interactions and real workflows
- Approach: Use subprocess to run scripts, test with real files
- Examples: `test_config_integration.py`, `test_full_pipeline.py`, `test_logging_integration.py`
- Use `subprocess_env` fixture for PYTHONPATH

**E2E Tests:**
- Location: `tests/verification/` (also some integration tests)
- Framework: pytest with subprocess invocation
- Scope: Test entire pipeline stages end-to-end
- Approach: Dry-run mode, actual execution with real data
- Examples: `test_stage1_dryrun.py`, `test_stage2_dryrun.py`, `test_stage3_dryrun.py`, `test_stage4_dryrun.py`

**Performance Tests:**
- Location: `tests/performance/`
- Scope: Performance regression detection
- Approach: Measure execution time and memory
- Marked with: `@pytest.mark.slow`
- Separate conftest.py for performance fixtures

## Common Patterns

**Parametrized Tests:**
```python
@pytest.mark.parametrize("value,expected", [
    (0.001, "***"),   # p < 0.01
    (0.04, "**"),    # p < 0.05
    (0.09, "*"),      # p < 0.10
    (0.10, ""),      # p >= 0.10
])
def test_significance_stars(self, value, expected):
    """Test that significance stars are assigned correctly."""
    result = _format_star(value)
    assert result == expected
```

**Async Testing:**
- NOT used - This is a synchronous data processing pipeline

**Error Testing:**
```python
def test_raises_error_on_missing_data(self, sample_compustat_factory):
    """Test that missing gvkey raises FinancialCalculationError."""
    compustat_df = sample_compustat_factory(n_firms=1, n_years=1, seed=42)

    row = pd.Series({"datadate": "2000-12-31"})  # Missing gvkey

    with pytest.raises(FinancialCalculationError, match="missing gvkey"):
        calculate_firm_controls(row, compustat_df, 2000)

def test_handles_missing_values_with_nan(self, sample_compustat_factory):
    """Test that missing data returns NaN for calculations."""
    compustat_df = sample_compustat_factory(n_firms=1, n_years=1, seed=42)
    compustat_df.loc[0, "ceq"] = np.nan

    row = pd.Series({"gvkey": "000000", "datadate": "2000-12-31"})
    result = calculate_firm_controls(row, compustat_df, 2000)

    assert pd.isna(result["market_to_book"])

def test_strict_mode_controls_error_raising(self):
    """Test that strict mode controls whether errors are raised."""
    with pytest.raises(DataValidationError):
        validate_dataframe_schema(
            df, "Unified-info.parquet", Path("test.parquet"), strict=True
        )

def test_strict_mode_false_allows_continuation(self, tmp_path, capsys):
    """Test loading with validation failure in non-strict mode."""
    df = pd.DataFrame({"col1": [1, 2, 3]})
    test_file = tmp_path / "test.parquet"
    df.to_parquet(test_file)

    result = load_validated_parquet(
        test_file, schema_name="Unified-info.parquet", strict=False
    )
    assert len(result) == 3  # Should return data despite validation failure

    captured = capsys.readouterr()
    assert "WARNING" in captured.err
```

**Floating-point comparison:**
```python
# Use pytest.approx for floating point assertions
assert result == pytest.approx(expected, rel=1e-5)

# Absolute tolerance
assert result == pytest.approx(expected, abs=0.001)
```

**Markers:**
```python
# Module-level marker
pytestmark = pytest.mark.integration

# Function-level markers
@pytest.mark.slow
def test_slow_operation(self):
    ...

@pytest.mark.skipif(not LINEARMODELS_AVAILABLE, reason="linearmodels not available")
def test_iv_regression(self):
    ...

@pytest.mark.xfail(reason="pandas/numpy compatibility issue")
def test_winsorization(self):
    ...
```

---

*Testing analysis: 2026-02-14*
