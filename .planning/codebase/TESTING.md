# Testing Patterns

**Analysis Date:** 2026-02-14

## Test Framework

**Runner:**
- pytest 8.0+
- Config: `pyproject.toml` `[tool.pytest.ini_options]`

**Assertion Library:**
- Built-in `assert` statements
- `pytest.approx()` for floating-point comparisons
- `pytest.raises()` for exception testing

**Run Commands:**
```bash
pytest                              # Run all tests
pytest tests/unit/                  # Run unit tests only
pytest tests/integration/           # Run integration tests only
pytest -m "not slow"                # Skip slow tests
pytest -v                           # Verbose output
pytest --cov=src/f1d --cov-report=html  # Coverage with HTML report
pytest -x                           # Stop on first failure
pytest -k "test_pattern"            # Run tests matching pattern
```

**Test Markers:**
```toml
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "regression: marks tests as regression tests",
    "unit: marks tests as unit tests",
    "e2e: marks tests as end-to-end pipeline tests",
    "performance: marks tests as performance regression tests",
    "mypy_testing: marks tests for mypy type checking",
]
```

## Test File Organization

**Location:**
- Tests in separate `tests/` directory (not co-located)
- Mirrors source structure: `tests/unit/`, `tests/integration/`, `tests/regression/`, `tests/performance/`

**Naming:**
- Test files: `test_<module_name>.py`
- Test classes: `Test<FeatureName>` (PascalCase)
- Test functions: `test_<description>` (snake_case)

**Structure:**
```
tests/
├── conftest.py                    # Shared fixtures (session + function scope)
├── unit/                          # Unit tests
│   ├── test_financial_utils.py
│   ├── test_data_validation.py
│   ├── test_panel_ols.py
│   └── ...
├── integration/                   # Integration tests
│   ├── test_full_pipeline.py
│   ├── test_pipeline_step1.py
│   └── ...
├── regression/                    # Regression tests
│   ├── test_output_stability.py
│   └── ...
├── performance/                   # Performance tests
│   └── test_performance_*.py
├── factories/                     # Test data factories
│   ├── financial.py
│   └── config.py
└── fixtures/                      # Static test data files
```

## Test Structure

**Suite Organization:**
```python
class TestCalculateFirmControls:
    """Tests for calculate_firm_controls() function."""

    def test_returns_size_as_log_assets(self, sample_compustat_factory):
        """Test that size (log assets) is computed correctly."""
        # Arrange
        compustat_df = sample_compustat_factory(n_firms=1, n_years=1, seed=42)
        row = pd.Series({"gvkey": "000000", "datadate": "2000-12-31"})

        # Act
        result = calculate_firm_controls(row, compustat_df, 2000)

        # Assert
        assert "size" in result
        assert result["size"] == pytest.approx(np.log(compustat_df.iloc[0]["at"]), rel=1e-5)

    def test_raises_error_on_missing_gvkey(self, sample_compustat_factory):
        """Test that missing gvkey raises FinancialCalculationError."""
        compustat_df = sample_compustat_factory(n_firms=1, n_years=1, seed=42)
        row = pd.Series({"datadate": "2000-12-31"})  # Missing gvkey

        with pytest.raises(FinancialCalculationError, match="missing gvkey"):
            calculate_firm_controls(row, compustat_df, 2000)
```

**Patterns:**
- Group related tests in classes
- Use descriptive test names that document expected behavior
- Follow Arrange-Act-Assert pattern
- One concept per test

## Fixtures

**Shared Fixtures** (from `tests/conftest.py`):

```python
@pytest.fixture(scope="session")
def repo_root():
    """Path to repository root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def subprocess_env():
    """Environment variables for subprocess calls in integration tests."""
    repo_root = Path(__file__).parent.parent
    return {
        "PYTHONPATH": str(repo_root / "src" / "f1d"),
        **os.environ,
    }


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        "file_name": ["test1.docx", "test2.docx", "test3.docx"],
        "Total_Words": [100, 200, 150],
    })


@pytest.fixture
def sample_config_yaml(tmp_path: Path) -> Path:
    """Create a temporary project.yaml with minimal valid config."""
    config_path = tmp_path / "project.yaml"
    config_path.write_text("""
project:
  name: TestProject
  version: "1.0.0"
data:
  year_start: 2002
  year_end: 2018
""")
    return config_path
```

**Factory Fixtures:**
```python
@pytest.fixture
def sample_compustat_factory() -> Callable[..., pd.DataFrame]:
    """Factory fixture to generate Compustat-style panel data.

    Args (via factory call):
        n_firms: Number of unique firms (default 10)
        n_years: Number of years per firm (default 5)
        seed: Random seed for reproducibility (default 42)
    """
    def _factory(n_firms: int = 10, n_years: int = 5, seed: int = 42) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        # ... generate data
        return pd.DataFrame(data)
    return _factory
```

**Usage in tests:**
```python
def test_with_factory(sample_compustat_factory):
    df = sample_compustat_factory(n_firms=10, n_years=5, seed=42)
    assert len(df) == 50
```

## Mocking

**Framework:** pytest-mock (wrapper around unittest.mock)

**Patterns:**
```python
def test_with_mock(mocker):
    """Mock external dependency."""
    mock_logger = mocker.patch("f1d.shared.logging.config.get_logger")
    # Test code that uses get_logger
    mock_logger.info.assert_called_once_with("expected_message")


def test_with_patch_object(mocker):
    """Patch object method."""
    mocker.patch.object(SomeClass, "method_name", return_value="mocked")
    # Test code
```

**What to Mock:**
- External services and APIs
- File I/O for unit tests
- Time-dependent functions
- Network calls
- Expensive computations

**What NOT to Mock:**
- The code under test
- Simple data structures
- Pure functions with deterministic output

## Fixtures and Factories

**Test Data Location:**
- Static fixtures: `tests/fixtures/`
- Dynamic factories: `tests/factories/`
- Inline in conftest.py for shared fixtures

**Factory Pattern:**
```python
# tests/factories/financial.py
@pytest.fixture
def sample_panel_data_factory() -> Callable[..., pd.DataFrame]:
    """Factory to generate panel regression test data."""
    def _factory(
        n_firms: int = 10,
        n_years: int = 5,
        n_independent: int = 2,
        seed: int = 42,
    ) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        # Generate realistic test data
        return pd.DataFrame(data)
    return _factory
```

**Reproducibility:**
- Always use explicit random seeds
- Default seed: 42
- Document seed in fixture docstring

## Coverage

**Requirements:**
- Overall minimum: 25% (from `pyproject.toml`)
- Individual tested modules: 70%+ for shared utilities
- Branch coverage enabled

**Configuration** (from `pyproject.toml`):
```toml
[tool.coverage.run]
source = ["src/f1d"]
branch = true
omit = ["*/tests/*", "*/__pycache__/*", "*/ARCHIVE*/*"]

[tool.coverage.report]
fail_under = 25
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@abstractmethod",
]
show_missing = true
```

**View Coverage:**
```bash
pytest --cov=src/f1d --cov-report=html
open htmlcov/index.html
```

**Excluded from Coverage:**
- `if TYPE_CHECKING:` blocks
- `__repr__` methods
- Abstract methods
- `if __name__ == "__main__":` blocks

## Test Types

**Unit Tests:**
- Location: `tests/unit/`
- Scope: Individual functions/classes
- Dependencies: Mocked or minimal
- Fast execution (< 1 second each)

**Integration Tests:**
- Location: `tests/integration/`
- Scope: Multiple components working together
- Dependencies: Real implementations where possible
- May use temporary files/directories

**Regression Tests:**
- Location: `tests/regression/`
- Scope: Output stability across changes
- Compare against baseline checksums
- Mark with `@pytest.mark.regression`

**E2E Tests:**
- Location: `tests/integration/`
- Scope: Full pipeline execution
- Mark with `@pytest.mark.e2e`
- May be slow, mark with `@pytest.mark.slow`

**Performance Tests:**
- Location: `tests/performance/`
- Scope: Execution time benchmarks
- Mark with `@pytest.mark.performance`

## Common Patterns

**Async Testing:**
Not used in this codebase (synchronous processing).

**Error Testing:**
```python
class TestFinancialCalculationError:
    """Tests for FinancialCalculationError exception."""

    def test_is_exception_subclass(self):
        """Test that FinancialCalculationError is an Exception subclass."""
        assert issubclass(FinancialCalculationError, Exception)

    def test_can_be_raised_and_caught(self):
        """Test that exception can be raised and caught properly."""
        with pytest.raises(FinancialCalculationError, match="GVKEY"):
            raise FinancialCalculationError("GVKEY not found")
```

**Parametrized Tests:**
```python
@pytest.mark.parametrize("strict_mode,should_raise", [
    (True, True),
    (False, False),
])
def test_strict_mode_controls_error_raising(self, strict_mode, should_raise):
    """Test that strict mode controls whether errors are raised."""
    if should_raise:
        with pytest.raises(DataValidationError):
            validate_dataframe_schema(df, schema, path, strict=strict_mode)
    else:
        validate_dataframe_schema(df, schema, path, strict=strict_mode)


@pytest.mark.parametrize("value,expected_valid", [
    (0, True),      # At minimum
    (-1, False),    # Below minimum
    (1000000, True),  # Above minimum
])
def test_speaker_record_count_range(value, expected_valid):
    """Test speaker_record_count range validation."""
    # ...
```

**Edge Case Testing:**
```python
class TestCalculateFirmControls:
    def test_handles_zero_at_returns_nan(self, sample_compustat_factory):
        """Test that zero total assets returns NaN for ratio-based metrics."""
        compustat_df = sample_compustat_factory(n_firms=1, n_years=1)
        compustat_df.loc[0, "at"] = 0.0
        row = pd.Series({"gvkey": "000000", "datadate": "2000-12-31"})

        result = calculate_firm_controls(row, compustat_df, 2000)

        assert pd.isna(result["size"])
        assert pd.isna(result["leverage"])

    def test_handles_missing_gvkey_raises_error(self, sample_compustat_factory):
        """Test that missing gvkey raises FinancialCalculationError."""
        # ...
```

**Skipping Tests:**
```python
# Skip if optional dependency not available
pytestmark = []
if not LINEARMODELS_AVAILABLE:
    pytestmark.append(pytest.mark.skip(reason="linearmodels not available"))


# Skip with pytest.skip in fixture
@pytest.fixture
def sample_config_path(test_data_dir):
    config_path = test_data_dir / "sample_yaml" / "project.yaml"
    if not config_path.exists():
        pytest.skip(f"Sample config not found: {config_path}")
    return config_path
```

**Expected Failures:**
```python
@pytest.mark.xfail(reason="pandas/numpy compatibility issue with .clip() internal sum()")
def test_winsorize_parameter_affects_output(self, sample_quarterly_df):
    """Test that winsorize parameter affects extreme values."""
    # Known issue - test documents expected behavior
```

## Subprocess Testing Pattern

For integration tests that invoke scripts:

```python
def test_script_execution(subprocess_env):
    """Test script can be executed via subprocess."""
    result = subprocess.run(
        ["python", str(script_path)],
        env=subprocess_env,  # Critical: enables f1d.shared imports
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
```

**Note:** Always use `subprocess_env` fixture for subprocess calls to ensure PYTHONPATH is set correctly for src-layout imports.

---

*Testing analysis: 2026-02-14*
