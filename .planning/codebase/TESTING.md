# Testing Patterns

**Analysis Date:** 2026-02-20

## Test Framework

**Runner:**
- pytest (v8.0+)
- Config: `pyproject.toml` `[tool.pytest.ini_options]`

**Assertion Library:**
- Built-in `assert` statements
- `pytest.approx()` for floating-point comparisons
- `pytest.raises()` for exception testing

**Run Commands:**
```bash
pytest tests/                                    # Run all tests
pytest tests/unit/                               # Run unit tests only
pytest -m "not slow"                             # Skip slow tests
pytest -m e2e                                    # Run E2E tests only
pytest tests/unit/test_financial_utils.py -v    # Verbose single file
pytest --cov=src/f1d/shared --cov-report=term   # With coverage
```

**Test Markers:**
- `slow`: Long-running tests (skip with `-m "not slow"`)
- `integration`: Integration tests
- `regression`: Regression tests
- `unit`: Unit tests
- `e2e`: End-to-end pipeline tests
- `performance`: Performance regression tests
- `mypy_testing`: Tests for mypy type checking

## Test File Organization

**Location:**
- Co-located in `tests/` directory (separate from source)
- Mirror source structure under `tests/`

**Naming:**
- Pattern: `test_{module_name}.py`
- Example: `test_financial_utils.py` tests `financial_utils.py`

**Structure:**
```
tests/
├── __init__.py
├── conftest.py                    # Shared fixtures (session-scoped)
├── factories/                     # Factory fixtures for test data
│   ├── __init__.py
│   ├── config.py                  # Configuration factories
│   └── financial.py               # Financial data factories
├── fixtures/                      # Static test data files
│   ├── baseline_checksums.json
│   └── synthetic_generator.py
├── integration/                   # Integration tests
│   ├── test_pipeline_e2e.py
│   ├── test_logging_integration.py
│   └── test_config_integration.py
├── performance/                   # Performance tests
│   ├── test_performance_h2_variables.py
│   └── conftest.py
├── regression/                    # Regression tests
│   ├── test_output_stability.py
│   └── test_survival_analysis_integration.py
├── unit/                          # Unit tests
│   ├── test_financial_utils.py
│   ├── test_data_validation.py
│   └── test_panel_ols.py
├── utils/                         # Test utilities
│   └── regression_test_harness.py
└── verification/                  # Verification/dry-run tests
    ├── test_stage1_dryrun.py
    └── test_all_scripts_dryrun.py
```

## Test Structure

**Suite Organization:**
```python
class TestCalculateFirmControls:
    """Tests for calculate_firm_controls() function."""

    def test_returns_size_as_log_assets(self, sample_compustat_factory):
        """Test that size (log assets) is computed correctly."""
        compustat_df = sample_compustat_factory(n_firms=1, n_years=1, seed=42)
        # Add required columns...
        row = pd.Series({"gvkey": "000000", "datadate": "2000-12-31"})
        result = calculate_firm_controls(row, compustat_df, 2000)
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
- Group tests by function/method in class named `Test{FunctionName}`
- Use descriptive test names: `test_{scenario}_{expected_outcome}`
- Docstring explains what is being tested
- One assertion concept per test (but multiple asserts allowed)

## Mocking

**Framework:** pytest-mock (v3.12+)

**Patterns:**
```python
# Using pytest-mock's mocker fixture
def test_file_not_found(mocker):
    mock_read = mocker.patch('pandas.read_parquet', side_effect=FileNotFoundError)
    with pytest.raises(DataValidationError):
        load_validated_parquet(Path("missing.parquet"))
    mock_read.assert_called_once()

# Environment variable mocking
def test_env_override(env_override):
    with env_override:
        os.environ['F1D_DATA__YEAR_START'] = '2010'
        # Test code...
    # Environment restored after context exits
```

**What to Mock:**
- File I/O operations for unit tests
- External API calls (none in this codebase)
- Environment variables for configuration tests
- Time-dependent behavior

**What NOT to Mock:**
- Pure calculations (test actual logic)
- DataFrame operations (test actual behavior)
- Internal function calls within same module

## Fixtures and Factories

**Test Data:**
```python
# conftest.py - Shared fixtures
@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        "file_name": ["test1.docx", "test2.docx", "test3.docx"],
        "Total_Words": [100, 200, 150],
    })

# Factory fixture pattern (callable fixtures)
@pytest.fixture
def sample_compustat_factory() -> Callable[..., pd.DataFrame]:
    """Factory fixture to generate Compustat-style panel data."""
    def _factory(n_firms: int = 10, n_years: int = 5, seed: int = 42) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        data = []
        for firm_id in range(n_firms):
            gvkey = str(firm_id).zfill(6)
            for year_offset in range(n_years):
                # Generate data...
        return pd.DataFrame(data)
    return _factory

# Usage
def test_asset_calculation(sample_compustat_factory):
    df = sample_compustat_factory(n_firms=10, n_years=5)
    assert len(df) == 50
```

**Location:**
- `tests/conftest.py`: Shared fixtures (session/function scoped)
- `tests/factories/`: Factory fixtures for complex test data
- `tests/fixtures/`: Static test data files (JSON, Parquet)

**Common Fixtures:**
- `tmp_path`: Built-in pytest fixture for temporary directories
- `sample_compustat_factory`: Generate Compustat-style panel data
- `sample_panel_data_factory`: Generate panel regression test data
- `sample_config_yaml`: Create temporary project.yaml
- `subprocess_env`: Environment for subprocess calls (PYTHONPATH set)

## Coverage

**Requirements:**
- Tier 1 (shared modules): 10% threshold in CI (individual tested modules: 70%+)
- Tier 2 (integration tests): 10% threshold
- Overall: 40% threshold for full test suite

**View Coverage:**
```bash
pytest tests/ --cov=src/f1d --cov-report=html
open htmlcov/index.html
```

**Coverage Config:**
```toml
# pyproject.toml
[tool.coverage.run]
source = ["src/f1d"]
branch = true
omit = ["*/tests/*", "*/__pycache__/*"]

[tool.coverage.report]
fail_under = 30
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
]
```

**Coverage Exclusions:**
- `pragma: no cover` comments
- `__repr__` methods
- `raise NotImplementedError`
- `if TYPE_CHECKING:` blocks
- `@abstractmethod` decorators

## Test Types

**Unit Tests:**
- Location: `tests/unit/`
- Focus: Individual functions in isolation
- Pattern: One test class per function, multiple test methods
- Example: `test_financial_utils.py` - tests each calculation function

**Integration Tests:**
- Location: `tests/integration/`
- Focus: Module interactions, config loading, logging setup
- Pattern: Test script execution, subprocess calls
- Example: `test_config_integration.py` - tests config loading from YAML

**E2E Tests:**
- Location: `tests/integration/` with `@pytest.mark.e2e`
- Focus: Full pipeline execution on synthetic data
- Pattern: Generate synthetic inputs, run scripts, verify outputs
- Example: `test_pipeline_e2e.py`

**Regression Tests:**
- Location: `tests/regression/`
- Focus: Output stability across changes
- Pattern: Compare outputs to baseline checksums
- Example: `test_output_stability.py`

**Performance Tests:**
- Location: `tests/performance/`
- Focus: Execution time, memory usage
- Pattern: Measure and assert thresholds
- Example: `test_performance_h2_variables.py`

## Common Patterns

**Async Testing:**
Not used in this codebase (synchronous processing only).

**Error Testing:**
```python
def test_raises_error_on_missing_gvkey(sample_compustat_factory):
    """Test that missing gvkey raises FinancialCalculationError."""
    compustat_df = sample_compustat_factory(n_firms=1, n_years=1, seed=42)
    row = pd.Series({"datadate": "2000-12-31"})  # Missing gvkey
    with pytest.raises(FinancialCalculationError, match="missing gvkey"):
        calculate_firm_controls(row, compustat_df, 2000)

def test_validation_strict_mode():
    """Test that strict mode raises on validation failure."""
    df = pd.DataFrame({"col": [1, 2]})  # Invalid schema
    with pytest.raises(DataValidationError):
        validate_dataframe_schema(df, "Unified-info.parquet", Path("test.parquet"), strict=True)
```

**Parametrized Tests:**
```python
@pytest.mark.parametrize("strict_mode,should_raise", [
    (True, True),
    (False, False),
])
def test_strict_mode_controls_error_raising(self, strict_mode, should_raise):
    """Test that strict mode controls whether errors are raised."""
    df = pd.DataFrame({"event_type": [1, 2]})  # Invalid
    if should_raise:
        with pytest.raises(DataValidationError):
            validate_dataframe_schema(df, "Unified-info.parquet", Path("test.parquet"), strict=strict_mode)
    else:
        # Should not raise in non-strict mode
        validate_dataframe_schema(df, "Unified-info.parquet", Path("test.parquet"), strict=strict_mode)

@pytest.mark.parametrize("value,expected_valid", [
    (0, True),      # At minimum
    (-1, False),    # Below minimum
    (1000000, True) # Above minimum
])
def test_speaker_record_count_range(value, expected_valid):
    """Test speaker_record_count range validation."""
    df = pd.DataFrame({
        "event_type": ["1"],
        "file_name": ["test"],
        "start_date": pd.to_datetime(["2020-01-01"]),
        "speaker_record_count": [value],
    })
    if expected_valid:
        validate_dataframe_schema(df, "Unified-info.parquet", Path("test.parquet"))
    else:
        with pytest.raises(DataValidationError):
            validate_dataframe_schema(df, "Unified-info.parquet", Path("test.parquet"))
```

**Fixture Scope:**
```python
@pytest.fixture(scope="session")
def repo_root():
    """Path to repository root directory (created once per session)."""
    return Path(__file__).parent.parent

@pytest.fixture
def sample_dataframe():
    """Create fresh DataFrame for each test."""
    return pd.DataFrame({"col": [1, 2, 3]})
```

**Subprocess Testing:**
```python
def test_script_execution(subprocess_env):
    """Test that script runs successfully via subprocess."""
    result = subprocess.run(
        [sys.executable, str(script_path)],
        env=subprocess_env,  # Critical: enables f1d.shared imports
        capture_output=True,
        text=True,
        cwd=str(workspace),
    )
    assert result.returncode == 0, f"Script failed: {result.stderr}"
```

**Temporary Files:**
```python
def test_load_validated_parquet(self, tmp_path):
    """Test loading with schema validation."""
    df = pd.DataFrame({"col": [1, 2, 3]})
    test_file = tmp_path / "test.parquet"
    df.to_parquet(test_file)
    
    result = load_validated_parquet(test_file, schema_name=None)
    assert len(result) == 3
```

---

*Testing analysis: 2026-02-20*
