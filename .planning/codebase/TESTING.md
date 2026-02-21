# Testing Patterns

**Analysis Date:** 2026-02-21

## Test Framework

**Runner:**
- pytest [8.0+]
- Config: `pyproject.toml` `[tool.pytest.ini_options]`

**Assertion Library:**
- pytest built-in assertions
- `pytest.approx()` for float comparisons

**Run Commands:**
```bash
pytest                    # Run all tests
pytest -m unit          # Run only unit tests
pytest -m integration    # Run only integration tests
pytest -m regression    # Run only regression tests
pytest -m e2e           # Run only end-to-end tests
pytest -m "not slow"   # Run tests excluding slow ones
pytest --cov=src/f1d   # Run with coverage
pytest -v               # Verbose mode
pytest -q               # Quiet mode (default in config)
```

## Test File Organization

**Location:**
- Test files co-located with source: `tests/unit/test_*.py` for unit tests
- Separate directory: `tests/` with subdirectories by type

**Naming:**
- Unit tests: `test_<module_name>.py` (e.g., `test_config.py`, `test_chunked_reader.py`)
- Hypothesis tests: `test_h<#>_regression.py` (e.g., `test_h1_regression.py`)
- Integration tests: `test_*.py` in `tests/integration/` (e.g., `test_config_integration.py`)
- Regression tests: `test_*.py` in `tests/regression/` (e.g., `test_output_stability.py`)
- Performance tests: `test_*.py` in `tests/performance/` (e.g., `test_performance_h2_variables.py`)
- Verification tests: `test_*.py` in `tests/verification/` (e.g., `test_all_scripts_dryrun.py`)

**Structure:**
```
tests/
├── __init__.py
├── conftest.py                    # Shared fixtures
├── factories/                     # Factory fixtures for test data
│   ├── __init__.py
│   ├── config.py
│   └── financial.py
├── fixtures/                      # Test data and utilities
│   ├── __init__.py
│   └── synthetic_generator.py
├── integration/                   # Integration tests
├── performance/                   # Performance regression tests
├── regression/                   # Output stability tests
├── unit/                         # Unit tests
└── verification/                  # Script dry-run verification
```

## Test Structure

**Suite Organization:**
```python
"""Module docstring describing what tests cover."""

import pytest
import pandas as pd
from pathlib import Path

from f1d.shared.module import function_being_tested


class TestFeatureName:
    """Tests for a specific feature/function."""

    def test_specific_behavior(self, fixture_name):
        """Test specific expected behavior."""
        result = function_being_tested(fixture_name)
        assert result == expected_value

    def test_edge_case(self, fixture_name):
        """Test edge case handling."""
        # Setup edge case
        result = function_being_tested(fixture_name)
        assert result is not None  # Or other assertion
```

**Patterns:**

**Setup with fixtures:**
```python
@pytest.fixture
def sample_parquet_file(tmp_path: Path) -> Path:
    """Create a temporary Parquet file for testing."""
    df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
    file_path = tmp_path / "test_data.parquet"
    df.to_parquet(file_path)
    return file_path
```

**Parametrized tests:**
```python
@pytest.mark.parametrize("value,expected_valid", [
    (0, True),   # At minimum
    (-1, False),  # Below minimum
    (1000000, True),  # Above minimum
])
def test_range_validation(value, expected_valid):
    """Test parameterized range validation."""
    if expected_valid:
        # Should not raise for valid values
        validate_value(value)
    else:
        # Should raise for invalid values
        with pytest.raises(ValueError):
            validate_value(value)
```

**Error testing with pytest.raises:**
```python
def test_invalid_input_raises(self):
    """Test that invalid input raises expected exception."""
    with pytest.raises(DataValidationError, match="Missing columns"):
        validate_dataframe_schema(invalid_df, schema_name)
```

**Async testing:**
- Not used in this codebase (synchronous pipeline)

**Teardown patterns:**
- Automatic: `tmp_path` fixture provides temporary directories cleaned up after test
- Context managers: Custom cleanup via `yield` in fixtures

## Mocking

**Framework:** `unittest.mock` (patch, MagicMock)

**Patterns:**

**Mocking dependencies:**
```python
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_panel_ols():
    """Mock run_panel_ols for testing."""
    with patch('f1d.econometric.v2.4.1_H1CashHoldingsRegression.run_panel_ols') as mock_ols:
        mock_ols.return_value = {
            'model': MagicMock(),
            'coefficients': pd.DataFrame(...),
            'summary': {...},
            'diagnostics': {...},
            'warnings': [],
        }
        yield mock_ols

def test_with_mock_panel_ols(mock_panel_ols):
    """Test regression execution with mocked panel OLS."""
    # Code that calls run_panel_ols will use the mock
    run_regression()
    assert mock_panel_ols.called
```

**Mocking subprocess calls:**
```python
def test_script_execution(self, subprocess_env):
    """Test script execution via subprocess."""
    result = subprocess.run(
        ["python", str(script_path)],
        env=subprocess_env,
        capture_output=True,
    )
    assert result.returncode == 0
```

**What to Mock:**
- External dependencies: file I/O, network calls, subprocess execution
- Heavy computations: panel OLS regression, IV regression
- Optional libraries: linearmodels (if not installed for test)

**What NOT to Mock:**
- Core business logic: validation, calculation functions
- Pandas operations (except for file I/O)
- Path resolution utilities

## Fixtures and Factories

**Test Data:**

**Factory fixtures (from `tests/factories/`):**

```python
@pytest.fixture
def sample_compustat_factory() -> Callable[..., pd.DataFrame]:
    """Factory fixture to generate Compustat-style panel data.

    Returns a callable that generates a DataFrame with standard Compustat
    columns for testing financial data processing functions.

    Args (via factory call):
        n_firms: Number of unique firms (default 10)
        n_years: Number of years per firm (default 5)
        seed: Random seed for reproducibility (default 42)

    Returns:
        pd.DataFrame with columns: gvkey, fyear, at, dlc, dltt, oancf, sale, ib
    """
    def _factory(
        n_firms: int = 10,
        n_years: int = 5,
        seed: int = 42,
    ) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        # Generate realistic financial values...
        return pd.DataFrame(data)

    return _factory
```

**Usage of factories:**
```python
def test_financial_calculation(sample_compustat_factory):
    """Test financial calculations using factory data."""
    df = sample_compustat_factory(n_firms=20, n_years=10)
    assert len(df) == 200
    # ... test logic
```

**Available factories:**
- `sample_compustat_factory`: Compustat panel data (tests/factories/financial.py)
- `sample_panel_data_factory`: Panel regression test data (tests/factories/financial.py)
- `sample_financial_row_factory`: Single Compustat row (tests/factories/financial.py)
- `sample_config_yaml_factory`: YAML config files (tests/conftest.py, tests/factories/config.py)
- `sample_project_config_factory`: ProjectConfig instances (tests/conftest.py)
- `invalid_config_yaml_factory`: Invalid configs for error testing

**Location:**
- `tests/factories/`: Factory fixtures
- `tests/fixtures/`: Synthetic data generators and test data
- `tests/conftest.py`: Shared session-scoped fixtures

**Environment fixtures:**
- `subprocess_env`: Provides environment variables for subprocess calls (sets PYTHONPATH)
- `env_override`: Context manager for temporary env var changes
- `repo_root`: Path to repository root
- `test_data_dir`: Path to test data directory

## Coverage

**Requirements:** 30% overall (target 40%), tier-specific:
- Tier 1 (shared modules): 100% target, strict mypy mode
- Tier 2 (stage modules): 80% target, moderate mypy mode
- Current: ~25% overall

**View Coverage:**
```bash
pytest --cov=src/f1d --cov-report=html --cov-report=term
```

**Coverage configuration:**
- `pyproject.toml` `[tool.coverage.*]`
- Branch coverage enabled
- Source: `src/f1d`
- Omit: `*/tests/*`, `*/__pycache__/*`, `*/ARCHIVE*/*`, `*/V1*`

**Coverage thresholds (from `pyproject.toml`):**
```toml
[tool.coverage.report]
fail_under = 30  # Minimum 30% coverage
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

**Individual module coverage (reference from config):**
- `financial_utils.py`: 97.75%
- `data_validation.py`: 92.00%
- `iv_regression.py`: 88.21%
- `panel_ols.py`: 72.08%
- `chunked_reader.py`: 88.24%
- `path_utils.py`: 86.09%

## Test Types

**Unit Tests:**
- Scope: Single function/method, isolated from dependencies
- Location: `tests/unit/test_*.py`
- Approach: Mock external dependencies, test logic directly
- Example: `test_chunked_reader.py` tests read_in_chunks, process_in_chunks

**Integration Tests:**
- Scope: Multiple modules working together, real config/project.yaml
- Location: `tests/integration/`
- Approach: Load actual config, test full workflows
- Example: `test_config_integration.py` loads real `config/project.yaml`

**E2E Tests:**
- Framework: pytest (not a separate E2E framework)
- Scope: Full pipeline execution on synthetic data
- Location: `tests/integration/test_pipeline_e2e.py`
- Pattern: Generate synthetic inputs, run scripts sequentially
- Example:
```python
@pytest.fixture(scope="session")
def synthetic_workspace():
    """Create temporary workspace with synthetic inputs."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Copy src/config, generate synthetic inputs
        generate_synthetic_inputs(temp_path)
        yield temp_path

def test_full_pipeline_e2e(synthetic_workspace):
    """Run all pipeline scripts sequentially on synthetic data."""
    run_script(src_dir / "sample" / "build_sample_manifest.py", root_dir)
    # If we made it here, pipeline ran without crashing
```

## Common Patterns

**Async Testing:**
- Not used (synchronous codebase)

**Error Testing:**
```python
def test_validation_error(self):
    """Test that validation raises expected error."""
    with pytest.raises(DataValidationError, match="Missing columns"):
        validate_dataframe_schema(invalid_df, schema_name)

def test_exception_properties(self):
    """Test exception stores error message correctly."""
    msg = "Test error message"
    exc = FinancialCalculationError(msg)
    assert str(exc) == msg
    assert exc.args[0] == msg
```

**Subprocess testing pattern:**
```python
def test_script_with_subprocess_env(subprocess_env):
    """Test script execution with proper PYTHONPATH."""
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
        cwd=str(cwd),
        env=subprocess_env  # Critical: enables f1d.shared imports
    )
    assert result.returncode == 0
```

**Regression testing with checksums:**
```python
@pytest.fixture(scope="session")
def baseline_checksums():
    """Load baseline checksums for regression testing."""
    baseline_path = Path("tests/fixtures/baseline_checksums.json")
    with open(baseline_path) as f:
        return json.load(f)

def test_regression_output_stability(baseline_checksums):
    """Test that output hasn't changed from baseline."""
    current_checksum = compute_file_checksum(output_file)
    expected_checksum = baseline_checksums.get("key")
    assert current_checksum == expected_checksum, (
        f"Regression detected! Expected: {expected_checksum}, Got: {current_checksum}"
    )
```

**Performance regression pattern:**
```python
@pytest.mark.slow
@pytest.mark.performance
def test_processing_performance(benchmark):
    """Test performance of processing function."""
    result = benchmark(process_function, test_data)
    assert len(result) > 0
```

**Dry-run verification pattern:**
```python
def test_all_scripts_dryrun():
    """Verify all scripts can be parsed and imported without errors."""
    script_dir = Path("src/f1d")
    for script_path in script_dir.rglob("*.py"):
        # Import module to check syntax
        importlib.import_module(f"f1d.{module_name}")
```

---

*Testing analysis: 2026-02-21*
