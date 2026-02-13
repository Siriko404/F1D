# Testing Patterns

**Analysis Date:** 2026-02-12

## Test Framework

**Runner:**
- pytest 8.0+
- Config: `pyproject.toml` `[tool.pytest.ini_options]`

**Assertion Library:**
- Built-in pytest assertions with `pytest.approx()` for floating-point comparisons
- `pytest.raises()` for exception testing

**Run Commands:**
```bash
pytest                              # Run all tests
pytest tests/unit/                  # Run unit tests only
pytest -m "not slow"                # Skip slow tests
pytest --cov=2_Scripts              # Run with coverage
pytest --cov=2_Scripts --cov-report=html  # Coverage with HTML report
pytest -v tests/unit/test_panel_ols.py    # Run specific file with verbose
```

## Test File Organization

**Location:**
- Tests are in separate `tests/` directory at project root
- Co-located with source: No (tests separate from `2_Scripts/`)

**Naming:**
- Test files: `test_{module_name}.py`
- Test classes: `Test{FeatureName}` (PascalCase)
- Test functions: `test_{description}` (snake_case)

**Structure:**
```
tests/
├── conftest.py                 # Shared fixtures
├── fixtures/                   # Test data files
│   └── baseline_checksums.json
├── unit/                       # Unit tests (isolated, fast)
│   ├── test_panel_ols.py
│   ├── test_financial_utils.py
│   └── test_data_validation.py
├── integration/                # Integration tests (multi-module)
│   ├── test_error_propagation.py
│   ├── test_pipeline_step1.py
│   └── test_full_pipeline.py
├── regression/                 # Output stability tests
│   ├── test_output_stability.py
│   └── generate_baseline_checksums.py
└── performance/                # Performance benchmarks
    ├── test_performance_h2_variables.py
    └── test_performance_link_entities.py
```

## Test Markers

**Available Markers (defined in pyproject.toml):**
```python
@pytest.mark.unit          # Fast, isolated unit tests
@pytest.mark.integration   # Multi-module integration tests
@pytest.mark.regression    # Output stability/comparison tests
@pytest.mark.e2e           # End-to-end pipeline tests
@pytest.mark.performance   # Performance regression tests
@pytest.mark.slow          # Long-running tests
@pytest.mark.mypy_testing  # Type checking tests
```

**Usage:**
```bash
pytest -m unit              # Run only unit tests
pytest -m "not slow"        # Skip slow tests
pytest -m performance       # Run only performance tests
```

## Test Structure

**Suite Organization:**
```python
"""
Unit tests for shared.panel_ols module.

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
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "2_Scripts"))

from shared.panel_ols import (
    run_panel_ols,
    CollinearityError,
)


@pytest.fixture
def sample_panel_data():
    """Create sample panel data for testing."""
    np.random.seed(42)
    n_firms = 10
    n_years = 5
    data = []
    for firm_id in range(n_firms):
        for year in range(n_years):
            data.append({
                "gvkey": str(firm_id).zfill(6),
                "year": 2000 + year,
                "dependent": np.random.rand() * 100,
                "independent1": np.random.rand() * 10,
            })
    return pd.DataFrame(data)


class TestRunPanelOls:
    """Tests for run_panel_ols() function."""

    @pytest.mark.skipif(not LINEARMODELS_AVAILABLE, reason="linearmodels not available")
    def test_validates_dependent_column_exists(self, sample_panel_data):
        """Test that missing dependent column raises appropriate error."""
        df_no_dep = sample_panel_data.drop(columns=["dependent"])
        with pytest.raises(ValueError, match="Missing required columns"):
            run_panel_ols(df_no_dep, "dependent", ["independent1"])

    def test_returns_expected_result_structure(self, sample_panel_data):
        """Test that function returns result with expected keys."""
        result = run_panel_ols(
            sample_panel_data,
            "dependent",
            ["independent1"],
            check_collinearity=False,
        )
        expected_keys = ["model", "coefficients", "summary", "diagnostics", "warnings"]
        for key in expected_keys:
            assert key in result
```

**Patterns:**
- Group related tests in classes named `Test{FeatureName}`
- Use descriptive test names that explain what is being tested
- One assertion concept per test when possible
- Use `pytest.raises()` context manager for exception testing

## Mocking

**Framework:** Built-in `unittest.mock` via pytest-mock or direct import

**Patterns:**
```python
# Skip tests when dependencies unavailable
pytestmark = []
if not LINEARMODELS_AVAILABLE:
    pytestmark.append(pytest.mark.skip(reason="linearmodels not available"))

# Patch external dependencies
from unittest.mock import patch, MagicMock

def test_external_api_call():
    with patch('module.external_api') as mock_api:
        mock_api.return_value = {"status": "ok"}
        result = function_under_test()
        assert result is not None
```

**What to Mock:**
- External API calls and network requests
- File system operations (for isolated unit tests)
- Expensive computations (in unit tests)
- Missing optional dependencies

**What NOT to Mock:**
- Internal business logic (test the real implementation)
- Data transformations (use real test data)
- Integration points in integration tests

## Fixtures and Factories

**Test Data:**
```python
# conftest.py - Shared fixtures
@pytest.fixture(scope="session")
def repo_root():
    """Path to repository root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def subprocess_env():
    """Provide environment variables for subprocess calls."""
    import os
    return {
        "PYTHONPATH": str(repo_root / "2_Scripts"),
        **os.environ,
    }


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        "file_name": ["test1.docx", "test2.docx"],
        "Total_Words": [100, 200],
        "MaQaUnc_pct": [0.5, 0.75],
    })


@pytest.fixture
def sample_compustat_df():
    """Create a sample Compustat DataFrame for testing."""
    return pd.DataFrame({
        "gvkey": ["001234", "001234", "001235"],
        "fyear": [2010, 2011, 2010],
        "at": [1000.0, 1100.0, 500.0],
        "dlc": [50.0, 55.0, 25.0],
        # ... more columns
    })
```

**Location:**
- Shared fixtures in `tests/conftest.py`
- Module-specific fixtures in test file
- Test data files in `tests/fixtures/`

**Fixture Scopes:**
- `scope="session"`: Expensive fixtures (repo paths, config)
- `scope="module"`: Shared test data
- Default (function scope): Isolated test data

## Coverage

**Requirements:**
- Overall minimum: 60%
- Tier 1 (critical): 90%+ for `financial_utils`, `panel_ols`, `iv_regression`
- Tier 2 (important): 80%+ for `data_validation`, `path_utils`, `chunked_reader`

**Coverage Configuration:**
```toml
# pyproject.toml
[tool.coverage.run]
source = ["2_Scripts"]
branch = true
omit = ["*/tests/*", "*/__pycache__/*", "*/V1*"]

[tool.coverage.report]
fail_under = 60
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
```

**View Coverage:**
```bash
pytest --cov=2_Scripts --cov-report=html
# Open htmlcov/index.html in browser
```

**Coverage Files:**
- `.coverage` - Binary coverage data
- `coverage.json` - JSON format coverage
- `htmlcov/` - HTML report directory

## Test Types

**Unit Tests:**
- Location: `tests/unit/`
- Scope: Single function or class
- Speed: Fast (< 1 second each)
- No external dependencies (mocked if needed)
- Example: `test_panel_ols.py` tests regression wrapper in isolation

```python
class TestCalculateFirmControls:
    """Tests for calculate_firm_controls() function."""

    def test_returns_size_as_log_assets(self, sample_compustat_row, sample_compustat_df):
        """Test that size (log assets) is computed correctly."""
        result = calculate_firm_controls(sample_compustat_row, sample_compustat_df, 2010)
        assert "size" in result
        assert result["size"] == pytest.approx(np.log(1000.0), rel=1e-5)
```

**Integration Tests:**
- Location: `tests/integration/`
- Scope: Multiple modules working together
- Speed: Medium (1-60 seconds)
- Real dependencies (databases, files)
- Example: `test_error_propagation.py` verifies exceptions flow through call stack

```python
def test_error_propagates_from_calculate_firm_controls(sample_input_df, sample_compustat_df):
    """Test that FinancialCalculationError propagates through compute_financial_features."""
    with pytest.raises(FinancialCalculationError) as exc_info:
        compute_financial_features(sample_input_df, sample_compustat_df)

    error_msg = str(exc_info.value)
    assert "no compustat data found" in error_msg.lower()
```

**E2E Tests:**
- Location: `tests/integration/test_full_pipeline.py`
- Marked with `@pytest.mark.e2e`
- Full pipeline execution via subprocess
- Verify outputs exist and have correct structure

```python
pytestmark = pytest.mark.e2e

PIPELINE_SCRIPTS = [
    "2_Scripts/1_Sample/1.1_CleanMetadata.py",
    "2_Scripts/1_Sample/1.2_LinkEntities.py",
    # ...
]

def test_full_pipeline_execution(subprocess_env, repo_root):
    """Execute full pipeline and verify outputs."""
    for script in PIPELINE_SCRIPTS:
        result = subprocess.run(
            ["python", str(repo_root / script)],
            env=subprocess_env,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Script failed: {script}"
```

## Regression Tests

**Purpose:** Detect output changes from baseline using SHA-256 checksums

**Location:** `tests/regression/test_output_stability.py`

**Baseline File:** `tests/fixtures/baseline_checksums.json`

```python
pytestmark = pytest.mark.regression

def compute_dataframe_checksum(df: pd.DataFrame) -> str:
    """Compute SHA-256 checksum of a DataFrame."""
    return hashlib.sha256(
        pd.util.hash_pandas_object(df, index=False).values.tobytes()
    ).hexdigest()

def test_regression_step2_output_stability(baseline_checksums):
    """Test that Step 2 output hasn't changed from baseline."""
    output_file = resolve_output_dir(REPO_ROOT / "4_Outputs/2_Textual_Analysis/2.1_Tokenized")

    current_checksum = compute_file_checksum(output_file)
    expected_checksum = baseline_checksums.get("step2_linguistic_counts_2002")

    assert current_checksum == expected_checksum, (
        f"Regression detected!\n"
        f"Expected: {expected_checksum}\n"
        f"Got: {current_checksum}\n"
        f"Run with --update-baseline if this change is intentional"
    )
```

**Update Baselines:**
```bash
python tests/regression/generate_baseline_checksums.py --update
```

## Performance Tests

**Framework:** pytest-benchmark

**Location:** `tests/performance/`

**Pattern:**
```python
pytestmark = pytest.mark.performance

def _rolling_std_naive(df: pd.DataFrame, ...) -> pd.Series:
    """Naive implementation for baseline comparison."""
    results = []
    for _gvkey, group in df.groupby(group_col):
        # ... slow loop-based implementation
    return pd.concat(results)

def _rolling_std_vectorized(df: pd.DataFrame, ...) -> pd.Series:
    """Optimized implementation."""
    return df.groupby(group_col)[value_col].transform(
        lambda x: x.rolling(window=window).std()
    )

def test_rolling_window_naive_baseline(benchmark, sample_compustat_for_rolling):
    """Establish baseline performance for naive implementation."""
    result = benchmark(
        _rolling_std_naive,
        sample_compustat_for_rolling,
        "gvkey",
        "ocf_at",
    )

def test_rolling_window_vectorized_faster(benchmark, sample_compustat_for_rolling):
    """Verify vectorized implementation is faster."""
    result = benchmark(
        _rolling_std_vectorized,
        sample_compustat_for_rolling,
        "gvkey",
        "ocf_at",
    )
```

## Common Patterns

**Async Testing:**
Not applicable - this codebase is synchronous Python.

**Error Testing:**
```python
def test_missing_gvkey_raises_error(sample_compustat_df):
    """Test that missing gvkey raises FinancialCalculationError."""
    row = pd.Series({"year": 2018})  # No gvkey

    with pytest.raises(FinancialCalculationError) as exc_info:
        calculate_firm_controls(row, sample_compustat_df, 2018)

    assert "missing gvkey" in str(exc_info.value).lower()
```

**Parametrized Tests:**
```python
@pytest.mark.parametrize("entity_effects,time_effects", [
    (True, True),
    (True, False),
    (False, True),
    (False, False),
])
def test_different_fixed_effects_combinations(
    self, sample_panel_data, entity_effects, time_effects
):
    """Test different fixed effect combinations."""
    result = run_panel_ols(
        sample_panel_data,
        "dependent",
        ["independent1"],
        entity_effects=entity_effects,
        time_effects=time_effects,
    )
    assert result["summary"]["entity_effects"] == entity_effects
    assert result["summary"]["time_effects"] == time_effects
```

**Floating-Point Comparison:**
```python
def test_calculates_leverage_correctly(sample_compustat_row, sample_compustat_df):
    """Test that leverage is computed correctly."""
    result = calculate_firm_controls(sample_compustat_row, sample_compustat_df, 2010)
    expected = (50.0 + 150.0) / 1000.0
    assert result["leverage"] == pytest.approx(expected, rel=1e-5)
```

**Skip Tests Conditionally:**
```python
@pytest.mark.skipif(not LINEARMODELS_AVAILABLE, reason="linearmodels not available")
def test_requires_linearmodels():
    """Test that requires linearmodels package."""
    ...

# Or at module level
pytestmark = []
if not OPTIONAL_DEP_AVAILABLE:
    pytestmark.append(pytest.mark.skip(reason="optional dependency not available"))
```

**Subprocess Testing:**
```python
def test_script_execution(subprocess_env, repo_root):
    """Test that script runs successfully via subprocess."""
    result = subprocess.run(
        ["python", str(repo_root / "2_Scripts/1_Sample/1.1_CleanMetadata.py")],
        env=subprocess_env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Script failed: {result.stderr}"
```

---

*Testing analysis: 2026-02-12*
