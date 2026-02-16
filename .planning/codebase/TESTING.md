# Testing Patterns

**Analysis Date:** 2026-02-15

## Test Framework

**Runner:**
- **Pytest** [Version >= 8.0] - Primary test runner
- Config: `pyproject.toml [tool.pytest.ini_options]`
- Minimum version: 8.0 enforced in config

**Assertion Library:**
- **Pytest** built-in assertions (no separate assertion library)
- Use `pytest.raises()` for exception testing
- Use `pytest.approx()` for floating-point comparisons

**Run Commands:**
```bash
pytest                          # Run all tests
pytest -q                       # Quiet mode (less output)
pytest -v                       # Verbose mode (show each test)
pytest tests/unit/               # Run unit tests only
pytest -m "not slow"            # Skip slow tests
pytest -m "unit or integration" # Run specific test types
pytest --cov                    # Run with coverage
pytest --cov-report=html         # Generate HTML coverage report
pytest --co                    # List tests without running
```

## Test File Organization

**Location:**
- **Co-located pattern**: Tests mirror source structure
- `tests/unit/test_*.py` - Unit tests for shared modules
- `tests/integration/test_*.py` - Integration tests
- `tests/verification/test_*.py` - Dry-run verification tests
- `tests/performance/test_*.py` - Performance regression tests
- `tests/factories/*.py` - Test data factory fixtures

**Naming:**
- `test_*.py` - Primary pattern (e.g., `test_financial_utils.py`)
- `*_test.py` - Also supported (per pytest config)
- Match module name being tested: `test_panel_ols.py` tests `panel_ols.py`

**Structure:**
```
tests/
├── conftest.py                  # Shared fixtures (session-level)
├── __init__.py
├── unit/                        # Shared module unit tests
│   ├── __init__.py
│   ├── test_*.py               # 35+ unit test files
│   └── test_data_validation_edge_cases.py  # Edge case tests
├── integration/                 # Cross-module integration tests
│   ├── test_config_integration.py
│   ├── test_full_pipeline.py
│   └── test_pipeline_step*.py
├── verification/                # Dry-run script verification
│   ├── test_all_scripts_dryrun.py
│   └── test_stage*_dryrun.py
├── performance/                 # Performance regression tests
│   └── test_performance_*.py
├── factories/                   # Test data factories
│   ├── __init__.py
│   ├── config.py               # Config fixtures
│   └── financial.py          # Financial data fixtures
├── fixtures/                   # Test data files
│   └── sample_yaml/
└── utils/                      # Test utility functions
```

## Test Structure

**Suite Organization:**
```python
"""Unit tests for f1d.shared.financial_utils module.

Tests verify financial calculation functions work correctly with edge cases:
- Missing data handling
- NaN values in Compustat fields
- Boundary conditions (zero, negative values)
- Winsorization behavior
- Quarterly vs annual controls

Uses factory fixtures from tests/factories/financial.py for test data generation.
"""

import pytest
import pandas as pd
import numpy as np

from f1d.shared.financial_utils import (
    calculate_firm_controls,
    compute_financial_features,
)
from f1d.shared.data_validation import FinancialCalculationError


class TestCalculateFirmControls:
    """Tests for calculate_firm_controls() function."""

    def test_returns_size_as_log_assets(self, sample_compustat_factory):
        """Test that size (log assets) is computed correctly."""
        # Arrange: Setup test data
        compustat_df = sample_compustat_factory(n_firms=1, n_years=1, seed=42)
        # Add required columns
        compustat_df["dlc"] = compustat_df["dlc"]
        # ...

        # Act: Execute function
        row = pd.Series({"gvkey": "000000", "datadate": "2000-12-31"})
        result = calculate_firm_controls(row, compustat_df, 2000)

        # Assert: Verify results
        assert "size" in result
        assert result["size"] == pytest.approx(np.log(compustat_df.iloc[0]["at"]), rel=1e-5)

    def test_raises_on_missing_gvkey(self, sample_compustat_factory):
        """Test that FinancialCalculationError is raised for missing gvkey."""
        compustat_df = sample_compustat_factory(n_firms=1, n_years=1)
        row = pd.Series({"datadate": "2000-12-31"})

        with pytest.raises(FinancialCalculationError) as exc_info:
            calculate_firm_controls(row, compustat_df, 2000)

        assert "missing gvkey" in str(exc_info.value)
```

**Patterns:**
- **Setup**: Use `@pytest.fixture` for test data setup
- **Arrange-Act-Assert (AAA)**: Structure test logic clearly
- **Test classes**: Group related tests in `TestClassName` classes
- **Descriptive names**: `test_what_is_expected_when_condition()`
- **Factory fixtures**: Use callable fixtures for parameterized test data
- **Autouse fixtures**: `@pytest.fixture(autouse=True)` for setup/teardown

**Setup pattern:**
```python
@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        "file_name": ["test1.docx", "test2.docx"],
        "Total_Words": [100, 200],
    })

@pytest.fixture
def tmp_config(tmp_path):
    """Create temporary config file."""
    config_path = tmp_path / "test_config.yaml"
    config_path.write_text("key: value")
    return config_path
```

**Teardown pattern:**
```python
@pytest.fixture
def temp_file(tmp_path):
    """Create temp file and cleanup automatically."""
    file_path = tmp_path / "test.txt"
    file_path.write_text("content")
    yield file_path  # Test runs here
    # Cleanup automatic via tmp_path fixture
```

**Assertion pattern:**
```python
# Basic assertion
assert result == expected

# Approximate for floats
assert result == pytest.approx(expected, rel=1e-5)

# Exception testing
with pytest.raises(ExpectedError) as exc_info:
    function_call()
assert "expected message" in str(exc_info.value)

# Type checking
assert isinstance(result, pd.DataFrame)
assert result.dtype == "int64"
```

## Mocking

**Framework:** **pytest-mock** [Version >= 3.12]
- Provides `mocker` fixture for creating mocks
- Also supports `unittest.mock` standard library

**Patterns:**
```python
# Mock a function
def test_with_mock(mocker):
    mock_func = mocker.patch("module.function", return_value="mocked")
    result = call_function()
    assert result == "mocked"
    mock_func.assert_called_once()

# Mock subprocess calls
def test_subprocess_call(mocker):
    mocker.patch("subprocess.run", return_value=CompletedProcess(...))
    # ... test code ...

# Mock file operations
def test_file_read(mocker, tmp_path):
    mocker.patch("pathlib.Path.read_text", return_value="test content")
    # ... test code ...
```

**What to Mock:**
- External API calls (requests, database connections)
- File system operations (Path.read_text, Path.write_text)
- Subprocess calls (subprocess.run)
- Time-dependent functions (datetime.now, time.time)
- Random number generation (np.random, random module)

**What NOT to Mock:**
- Shared utility functions being tested
- Core pandas/numpy operations (test with real data)
- Configuration loading (use test fixtures for config)
- Simple pure Python functions

## Fixtures and Factories

**Test Data:**
```python
# Factory fixture from tests/factories/financial.py
@pytest.fixture
def sample_compustat_factory():
    """Factory fixture to generate Compustat-style panel data.

    Returns a callable that generates a DataFrame with standard Compustat
    columns for testing financial data processing functions.

    Args (via factory call):
        n_firms: Number of unique firms (default 10)
        n_years: Number of years per firm (default 5)
        seed: Random seed for reproducibility (default 42)

    Returns:
        pd.DataFrame with columns: gvkey, fyear, at, dlc, dltt, ...

    Example:
        def test_asset_calculation(sample_compustat_factory):
            df = sample_compustat_factory(n_firms=10, n_years=5)
            assert len(df) == 50
    """
    def _factory(n_firms=10, n_years=5, seed=42):
        rng = np.random.default_rng(seed)
        data = []
        # ... generate data ...
        return pd.DataFrame(data)
    return _factory

# Usage in test
def test_with_factory(sample_compustat_factory):
    df = sample_compustat_factory(n_firms=5, n_years=3)
    assert len(df) == 15
```

**Location:**
- `tests/factories/config.py` - Config-related fixtures
- `tests/factories/financial.py` - Financial data fixtures
- `tests/conftest.py` - Shared fixtures (repo_root, subprocess_env, etc.)

**Key Fixtures in conftest.py:**
- `repo_root` - Path to repository root (session-scoped)
- `subprocess_env` - Environment with PYTHONPATH set for subprocess calls
- `test_data_dir` - Path to test fixtures directory
- `sample_dataframe` - Basic DataFrame fixture
- `sample_config_yaml` - Temporary valid YAML config
- `invalid_config_yaml` - Temporary invalid YAML config
- `capture_output` - Capture stdout/stderr

**Callable Factory Pattern:**
```python
@pytest.fixture
def sample_config_yaml_factory(tmp_path):
    """Factory fixture to generate temporary YAML config files.

    Returns a callable that creates a temporary project.yaml file
    with customizable configuration values.
    """
    def _factory(year_start=2002, year_end=2018, **kwargs):
        config_data = {
            "project": {"name": "TestProject"},
            "data": {"year_start": year_start, "year_end": year_end},
        }
        config_data.update(kwargs)
        config_path = tmp_path / "project.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)
        return config_path
    return _factory
```

## Coverage

**Requirements:**
- **Target: 30% minimum** (enforced in CI)
- **Tier 1 modules (shared)**: 70%+ individually (currently ~97% for tested modules)
- **Tier 2 modules (stage)**: 80%+ individually for tested modules
- **Overall target**: 40% (currently ~25%)
- Configured in: `.coveragerc` and `pyproject.toml [tool.coverage.report]`

**View Coverage:**
```bash
pytest --cov                   # Run tests with coverage
pytest --cov-report=html       # Generate HTML report at htmlcov/
pytest --cov-report=xml        # Generate XML report at coverage.xml
pytest --cov-report=json       # Generate JSON report at coverage.json
pytest --cov-report=term-missing # Show missing lines in terminal
coverage html                  # Alternative way to view HTML report
coverage report -m            # Show missing lines
```

**Coverage Exclusions:**
```python
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@abstractmethod",
]
```

**Omitted paths:**
- `*/tests/*` - Test files themselves
- `*/__pycache__/*` - Python cache
- `*/ARCHIVE*/*` - Archived code
- `*/ARCHIVE_OLD*/*` - Old archives
- `*/V1*` - Version 1 scripts

## Test Types

**Unit Tests:**
- **Scope**: Test individual functions/classes in isolation
- **Location**: `tests/unit/test_*.py`
- **Approach**: Use factory fixtures for test data, mock external dependencies
- **Target**: Shared modules (financial_utils, panel_ols, etc.)
- **Examples**:
  - `test_financial_utils.py` - Financial calculation functions
  - `test_data_validation.py` - Schema validation
  - `test_panel_ols.py` - Panel OLS regression

**Integration Tests:**
- **Scope**: Test interactions between modules/components
- **Location**: `tests/integration/test_*.py`
- **Approach**: Test end-to-end workflows, real dependencies
- **Examples**:
  - `test_full_pipeline.py` - Complete pipeline execution
  - `test_config_integration.py` - Config loading and overrides
  - `test_logging_integration.py` - Logging system integration

**E2E Tests:**
- **Scope**: Test complete execution of pipeline scripts
- **Framework**: Subprocess invocation of scripts
- **Location**: `tests/integration/` (e2e tests integrated with integration)
- **Pattern**:
  ```python
  def test_script_execution(subprocess_env):
      """Test that script executes successfully."""
      script_path = Path("src/f1d/sample/script.py")
      result = subprocess.run(
          ["python", str(script_path)],
          env=subprocess_env,  # Sets PYTHONPATH for f1d.shared imports
          capture_output=True,
          text=True,
      )
      assert result.returncode == 0
  ```

**Performance Tests:**
- **Scope**: Benchmark execution time and memory usage
- **Location**: `tests/performance/test_*.py`
- **Approach**: Measure performance, track regressions over time
- **Examples**:
  - `test_performance_h2_variables.py`
  - `test_performance_link_entities.py`

**Dry-Run Verification Tests:**
- **Scope**: Verify scripts can be parsed and run without data
- **Location**: `tests/verification/test_*_dryrun.py`
- **Purpose**: Catch import errors, syntax issues, basic execution paths
- **Examples**:
  - `test_all_scripts_dryrun.py` - All scripts dry-run
  - `test_stage1_dryrun.py` - Stage 1 scripts dry-run

## Common Patterns

**Async Testing:**
- Not applicable (this project is synchronous Python)

**Error Testing:**
```python
# Test expected exception
def test_raises_on_invalid_input():
    with pytest.raises(FinancialCalculationError) as exc_info:
        calculate_firm_controls(invalid_row, df, 2000)
    assert "missing gvkey" in str(exc_info.value)

# Test exception with specific attributes
def test_weak_instrument_error():
    with pytest.raises(WeakInstrumentError) as exc_info:
        run_iv2sls(...)
    assert exc_info.value.f_stat < 10.0
    assert exc_info.value.threshold == 10.0

# Test error message content
def test_error_message_includes_context():
    with pytest.raises(PathValidationError) as exc_info:
        validate_input_file(nonexistent_path)
    assert "Input file does not exist" in str(exc_info.value)
    assert str(nonexistent_path) in str(exc_info.value)
```

**Data Frame Testing:**
```python
# Check DataFrame structure
assert isinstance(result, pd.DataFrame)
assert result.shape == (expected_rows, expected_cols)
assert list(result.columns) == ["col1", "col2", "col3"]

# Check values
assert result["value"].sum() == pytest.approx(expected_sum, rel=1e-5)
assert all(result["column"] > 0)

# Check for missing values
assert result["column"].isna().sum() == 0

# Check data types
assert result["date"].dtype == "datetime64[ns]"
assert result["count"].dtype == "int64"
```

**Deterministic Testing:**
```python
def test_deterministic_behavior():
    """Test that function produces same output for same input."""
    df = pd.DataFrame({"A": [1, 2, 3]})

    result1 = function_under_test(df)
    result2 = function_under_test(df)

    # Should be identical
    assert result1.equals(result2)

    # For numeric results with floating point
    assert result1 == pytest.approx(result2)
```

**Parametrized Testing:**
```python
@pytest.mark.parametrize("year,expected", [
    (2002, True),
    (1999, False),
    (2031, False),
])
def test_year_validation(year, expected):
    """Test year validation with multiple inputs."""
    settings = DataSettings(year_start=year, year_end=2020)
    assert validation_result == expected
```

## Test Markers

**Available Markers:**
- `@pytest.mark.slow` - Marks tests as slow (deselect with `-m "not slow"`)
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.regression` - Regression tests
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.performance` - Performance regression tests
- `@pytest.mark.mypy_testing` - Tests for mypy type checking

**Usage:**
```python
@pytest.mark.slow
def test_large_dataset_processing():
    # Slow test - skip with pytest -m "not slow"
    ...

@pytest.mark.integration
def test_module_integration():
    # Integration test - run with pytest -m integration
    ...
```

---

*Testing analysis: 2026-02-15*
