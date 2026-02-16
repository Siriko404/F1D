# Testing Patterns

**Analysis Date:** 2026-02-15

## Test Framework

**Runner:**
- pytest 8.0+ (configured in `pyproject.toml`)
- Config: `[tool.pytest.ini_options]` in `pyproject.toml`

**Assertion Library:**
- pytest built-in assertions
- `pytest.approx()` for floating-point comparisons

**Run Commands:**
```bash
pytest                           # Run all tests
pytest -q                        # Quiet mode (less output)
pytest -v                        # Verbose output
pytest -m "not slow"            # Skip slow tests
pytest --cov=src/f1d            # Run with coverage
pytest --cov=src/f1d --cov-report=html  # Generate HTML coverage report
```

## Test File Organization

**Location:**
- Co-located in `tests/` directory (separate from source)
- Unit tests: `tests/unit/test_*.py`
- Integration tests: `tests/integration/test_*.py`
- Regression tests: `tests/regression/test_*.py`
- Performance tests: `tests/performance/test_*.py`
- Verification tests: `tests/verification/test_*.py`
- Factories: `tests/factories/*.py`

**Naming:**
- Test files: `test_<module_name>.py` (e.g., `test_financial_utils.py`)
- Test classes: `Test<Functionality>` (e.g., `TestCalculateFirmControls`, `TestCheckThinCells`)
- Test methods: `test_<specific_behavior>()` (e.g., `test_returns_size_as_log_assets`, `test_detects_thin_cells`)

**Structure:**
```
tests/
├── conftest.py                    # Shared fixtures for all tests
├── factories/                     # Test data factories
│   ├── financial.py               # Financial data factories
│   └── config.py                 # Configuration factories
├── unit/                         # Unit tests for shared modules
│   ├── test_financial_utils.py
│   ├── test_data_validation.py
│   └── test_panel_ols.py
├── integration/                   # Multi-module integration tests
│   ├── test_full_pipeline.py
│   └── test_config_integration.py
├── regression/                   # Output stability tests
│   ├── test_output_stability.py
│   └── generate_baseline_checksums.py
├── performance/                  # Performance regression tests
│   └── test_performance_h2_variables.py
└── verification/                  # Script dry-run verification
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
        # ... test implementation

    def test_calculates_leverage_correctly(self, sample_compustat_factory):
        """Test that leverage (debt/assets) is computed correctly."""
        # ... test implementation
```

**Patterns:**
- **Setup pattern**: Use factory fixtures for test data: `sample_compustat_factory()`, `sample_config_yaml_factory()`
- **Teardown pattern**: Use `tmp_path` fixture for automatic cleanup
- **Assertion pattern**: Use `pytest.approx()` for floating-point comparisons: `assert result["size"] == pytest.approx(expected, rel=1e-5)`

## Mocking

**Framework:** pytest-mock (configured in `pyproject.toml`)

**Patterns:**
```python
# For optional imports that may not be available
pytestmark = []
if not LINEARMODELS_AVAILABLE:
    pytestmark.append(pytest.mark.skip(reason="linearmodels not available"))

# For environment variable mocking
from unittest.mock import patch
import os

def test_env_override(sample_env_vars_factory):
    env_vars = sample_env_vars_factory(data__year_start="2010")
    with patch.dict(os.environ, env_vars):
        config = EnvConfig()
        assert config.data.year_start == 2010
```

**What to Mock:**
- External file I/O in unit tests
- Network calls (if any)
- Environment variables

**What NOT to Mock:**
- pandas/numpy operations
- Internal shared module functions (test the real implementation)

## Fixtures and Factories

**Test Data:**
```python
# Factory fixture pattern (from tests/factories/financial.py)
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
    def _factory(n_firms: int = 10, n_years: int = 5, seed: int = 42) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        data = []
        for firm_id in range(n_firms):
            gvkey = str(firm_id).zfill(6)
            # ... generate data
        return pd.DataFrame(data)
    return _factory
```

**Location:**
- `tests/conftest.py`: Core fixtures (session-scoped)
- `tests/factories/financial.py`: Financial data factories
- `tests/factories/config.py`: Configuration factories

## Coverage

**Requirements:** 25% overall minimum (configured in `pyproject.toml`)

**View Coverage:**
```bash
pytest --cov=src/f1d                          # Terminal report
pytest --cov=src/f1d --cov-report=html     # HTML report
pytest --cov=src/f1d --cov-report=xml      # XML report (for CI)
```

**Configuration:**
- Source: `src/f1d`
- Branch coverage: Enabled
- Exclude patterns: `tests/*`, `__pycache__/*`, `ARCHIVE*/*`, `ARCHIVE_OLD*/*`, `*/V1*`

## Test Types

**Unit Tests:**
- Scope: Individual functions/classes in shared modules
- Location: `tests/unit/test_*.py`
- Approach: Isolated testing with mock/factory data
- Examples: `test_financial_utils.py`, `test_data_validation.py`, `test_panel_ols.py`

**Integration Tests:**
- Scope: Multi-module interactions, pipeline stages
- Location: `tests/integration/test_*.py`
- Approach: Real file I/O, subprocess script execution
- Examples: `test_full_pipeline.py`, `test_config_integration.py`, `test_ceo_fixed_effects.py`
- Pattern: Use `subprocess_env` fixture for PYTHONPATH setup:
```python
@pytest.fixture(scope="session")
def subprocess_env():
    """Provide environment variables for subprocess calls in integration tests."""
    from pathlib import Path
    repo_root = Path(__file__).parent.parent.parent
    return {
        "PYTHONPATH": str(repo_root / "src" / "f1d"),
        **os.environ,
    }
```

**E2E Tests:**
- Framework: pytest (no separate E2E framework)
- Marker: `@pytest.mark.e2e`
- Purpose: Full pipeline execution verification
- Examples: `tests/integration/test_full_pipeline.py`

**Performance Tests:**
- Marker: `@pytest.mark.performance`
- Framework: pytest-benchmark (implied from `test_performance_h2_variables.py`)
- Purpose: Benchmark optimization changes
- Location: `tests/performance/test_*.py`
- Pattern: Compare naive vs optimized implementations

**Regression Tests:**
- Marker: `@pytest.mark.regression`
- Purpose: Detect output changes from baseline
- Method: SHA-256 checksum comparison
- Location: `tests/regression/test_*.py`
- Script: `tests/regression/generate_baseline_checksums.py` generates baselines
- Pattern:
```python
def test_regression_step1_output_stability(baseline_checksums):
    """Test that Step 1 output hasn't changed from baseline."""
    current_checksum = compute_file_checksum(output_file)
    expected_checksum = baseline_checksums.get("step1_cleaned_metadata")
    assert current_checksum == expected_checksum
```

**Verification Tests:**
- Marker: `@pytest.mark.mypy_testing`
- Purpose: Script dry-run validation, import checking
- Location: `tests/verification/test_*.py`
- Pattern: Use subprocess to test script with `--dry-run` flag

## Common Patterns

**Async Testing:**
- Not used in this codebase (synchronous pipeline)

**Error Testing:**
```python
def test_missing_required_column_raises(self):
    """Test that missing required column raises DataValidationError."""
    df = pd.DataFrame({"event_type": [1, 2]})
    with pytest.raises(DataValidationError, match="Missing columns"):
        validate_dataframe_schema(
            df, "Unified-info.parquet", Path("test.parquet"), strict=True
        )
```

**Parametrized Tests:**
```python
@pytest.mark.parametrize("pvalue,expected_stars", [
    (0.001, "***"),
    (0.04, "**"),
    (0.09, "*"),
    (0.10, ""),
    (0.11, ""),
])
def test_significance_stars(self, pvalue, expected_stars):
    """Test that significance stars are assigned correctly."""
    result = _format_star(pvalue)
    assert result == expected_stars
```

**Skip Conditions:**
```python
# Module-level skip
pytestmark = []
if not LINEARMODELS_AVAILABLE:
    pytestmark.append(pytest.mark.skip(reason="linearmodels not available"))

# Test-level skip
def test_requires_input_file(test_data_dir):
    """Test that requires input file."""
    config_path = test_data_dir / "sample_yaml" / "project.yaml"
    if not config_path.exists():
        pytest.skip(f"Sample config not found: {config_path}")
```

## Markers

**Configured Markers (from pyproject.toml):**
- `slow`: Marks tests as slow (deselect with `-m "not slow"`)
- `integration`: Marks tests as integration tests
- `regression`: Marks tests as regression tests
- `unit`: Marks tests as unit tests
- `e2e`: Marks tests as end-to-end pipeline tests
- `performance`: Marks tests as performance regression tests
- `mypy_testing`: Marks tests for mypy type checking

---

*Testing analysis: 2026-02-15*
