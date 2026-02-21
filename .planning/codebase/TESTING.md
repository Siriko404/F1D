# Testing Patterns

**Analysis Date:** 2026-02-21

## Test Framework

**Runner:**
- pytest >= 8.0
- Config: `pyproject.toml` → `[tool.pytest.ini_options]`

**Assertion Library:**
- Built-in `assert` statements
- `pytest.approx()` for floating-point comparisons
- `np.testing.assert_allclose()` for array comparisons

**Run Commands:**
```bash
pytest                              # Run all tests
pytest tests/unit/                  # Run unit tests only
pytest -m "not slow"                # Skip slow tests
pytest --cov=src/f1d --cov-report=html  # Run with coverage
pytest -v tests/unit/test_financial_utils.py  # Run specific file
```

## Test File Organization

**Location:**
- Tests co-located in `tests/` directory (separate from source)
- Test types organized into subdirectories

**Structure:**
```
tests/
├── conftest.py              # Shared fixtures
├── __init__.py
├── unit/                    # Unit tests (fast, isolated)
│   ├── test_financial_utils.py
│   ├── test_path_utils.py
│   └── test_<module>.py
├── integration/             # Integration tests (subprocess, multi-module)
│   ├── test_pipeline_e2e.py
│   └── test_config_integration.py
├── regression/              # Regression tests (output stability)
│   ├── test_output_stability.py
│   └── generate_baseline_checksums.py
├── verification/            # Verification tests (dry-run, imports)
│   ├── test_stage1_dryrun.py
│   └── test_stage2_dryrun.py
├── performance/             # Performance benchmarks
│   ├── test_performance_h2_variables.py
│   └── conftest.py
├── factories/               # Test data factories
│   ├── financial.py
│   └── config.py
├── fixtures/                # Test data files
│   └── synthetic_generator.py
└── utils/                   # Test utilities
    └── regression_test_harness.py
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
        # ... test implementation
        assert result["size"] == pytest.approx(expected, rel=1e-5)

    def test_raises_error_on_missing_gvkey(self, sample_compustat_factory):
        """Test that missing gvkey raises FinancialCalculationError."""
        with pytest.raises(FinancialCalculationError, match="missing gvkey"):
            calculate_firm_controls(row, compustat_df, 2000)
```

**Patterns:**
- Group related tests in classes named `Test<FunctionName>`
- Use descriptive test method names: `test_<what_is_tested>`
- Include docstrings explaining test purpose

## Test Markers

**Defined markers (from `pyproject.toml`):**
```python
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

**Usage:**
```python
pytestmark = pytest.mark.regression  # Mark all tests in module

@pytest.mark.parametrize("n_firms,n_years", [
    (50, 10),
    (100, 20),
    (500, 20),
])
def test_rolling_window_scaling(benchmark, n_firms, n_years):
    ...
```

## Mocking

**Framework:** pytest-mock (via `pytest-mock>=3.12`)

**Patterns:**
```python
def test_script_importable(self, script: str, subprocess_env: dict, monkeypatch):
    """Test that script can be imported without errors."""
    import sys
    
    script_path = REPO_ROOT / script
    result = subprocess.run(
        [sys.executable, "-c", f"import runpy; runpy.run_path('{script_path}')"],
        capture_output=True,
        text=True,
        env=subprocess_env,
        timeout=30,
    )
    assert "ImportError" not in result.stderr
```

**What to Mock:**
- File system operations for unit tests
- External dependencies (network, databases)
- Time-dependent functions

**What NOT to Mock:**
- Core business logic (test real implementation)
- Internal function calls within the same module

## Fixtures and Factories

**Test Data:**
```python
# Factory fixture pattern (recommended)
@pytest.fixture
def sample_compustat_factory() -> Callable[..., pd.DataFrame]:
    """Factory fixture to generate Compustat-style panel data.

    Returns:
        Callable that creates DataFrame with configurable parameters.

    Example:
        df = sample_compustat_factory(n_firms=10, n_years=5, seed=42)
    """
    def _factory(
        n_firms: int = 10,
        n_years: int = 5,
        seed: int = 42,
    ) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        # ... generate data
        return pd.DataFrame(data)

    return _factory


# Usage in tests
def test_asset_calculation(sample_compustat_factory):
    df = sample_compustat_factory(n_firms=10, n_years=5)
    assert len(df) == 50
```

**Location:**
- Shared fixtures: `tests/conftest.py`
- Domain fixtures: `tests/factories/financial.py`, `tests/factories/config.py`
- Performance fixtures: `tests/performance/conftest.py`

**Key fixtures from `tests/conftest.py`:**
- `repo_root`: Path to repository root
- `subprocess_env`: Environment for subprocess calls (sets PYTHONPATH)
- `test_data_dir`: Path to test data fixtures
- `sample_dataframe`: Basic test DataFrame
- `sample_config_yaml`: Temporary project.yaml
- `sample_config`: Valid ProjectConfig instance

## Coverage

**Requirements:** 30% minimum (target: 40%)

**Configuration:**
```toml
[tool.coverage.run]
source = ["src/f1d"]
branch = true
omit = ["*/tests/*", "*/__pycache__/*", "*/V1*"]

[tool.coverage.report]
fail_under = 30
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
]
```

**View Coverage:**
```bash
pytest --cov=src/f1d --cov-report=html
open htmlcov/index.html
```

**Individual module coverage (for reference):**
- `financial_utils.py`: 97.75%
- `data_validation.py`: 92.00%
- `iv_regression.py`: 88.21%
- `panel_ols.py`: 72.08%
- `chunked_reader.py`: 88.24%
- `path_utils.py`: 86.09%

## Test Types

**Unit Tests:**
- Location: `tests/unit/`
- Fast execution, isolated testing
- Use factory fixtures for test data
- Test edge cases: NaN, zero, negative, missing values

**Integration Tests:**
- Location: `tests/integration/`
- Test module interactions
- Use subprocess for script invocation
- Use `subprocess_env` fixture for PYTHONPATH

**Regression Tests:**
- Location: `tests/regression/`
- Verify output stability via checksum comparison
- Use SHA-256 checksums of parquet files
- Skip if baseline or output not found

**Verification Tests:**
- Location: `tests/verification/`
- Dry-run tests for scripts
- Import validation
- CLI argument parsing validation

**Performance Tests:**
- Location: `tests/performance/`
- Use pytest-benchmark
- Compare naive vs vectorized implementations
- Verify bitwise-identical results

## Common Patterns

**Async Testing:**
```python
# Not used in this codebase (synchronous only)
```

**Error Testing:**
```python
def test_raises_error_on_missing_gvkey(self, sample_compustat_factory):
    """Test that missing gvkey raises FinancialCalculationError."""
    row = pd.Series({"datadate": "2000-12-31"})  # Missing gvkey
    with pytest.raises(FinancialCalculationError, match="missing gvkey"):
        calculate_firm_controls(row, compustat_df, 2000)
```

**Floating-Point Comparison:**
```python
def test_size_calculation(self, sample_compustat_factory):
    result = calculate_firm_controls(row, compustat_df, 2000)
    assert result["size"] == pytest.approx(np.log(expected_at), rel=1e-5)
```

**Parameterized Tests:**
```python
@pytest.mark.parametrize("output_dir,filename,baseline_key", [
    ("outputs/1.1_CleanMetadata", "cleaned_metadata.parquet", "step1_cleaned_metadata"),
    ("outputs/2_Textual_Analysis/2.1_Tokenized", "linguistic_counts_2002.parquet", "step2_linguistic_counts_2002"),
])
def test_regression_key_outputs(output_dir, filename, baseline_key, baseline_checksums):
    ...
```

**Performance Benchmark:**
```python
def test_rolling_window_vectorized(benchmark, sample_compustat_for_rolling):
    """Benchmark vectorized rolling window transform."""
    result = benchmark(
        _rolling_std_vectorized,
        sample_compustat_for_rolling,
        "gvkey", "ocf_at", 5, 3,
    )
    assert result.notna().sum() > 0
```

**Subprocess Testing:**
```python
def test_script_importable(self, script: str, subprocess_env: dict):
    """Test that script can be imported without errors."""
    result = subprocess.run(
        [sys.executable, "-c", f"import runpy; runpy.run_path('{script_path}')"],
        capture_output=True,
        text=True,
        env=subprocess_env,
        timeout=30,
        cwd=str(REPO_ROOT),
    )
    assert "ImportError" not in result.stderr
```

## Edge Case Testing

**From `tests/unit/README_edge_cases.md`:**

1. **Zero-row delta assertion:** Test that duplicate file_name rows raise ValueError
2. **Hard-fail on missing variables:** Test that missing required columns raise ValueError
3. **CUSIP alphanumeric join:** Test IBES alphanumeric CUSIPs join correctly
4. **Missing year files:** Test graceful handling of missing partitioned files
5. **Reference entity normalization:** Test that reference CEOs are excluded from output

**Example edge case test:**
```python
def test_handles_zero_at_returns_nan(self, sample_compustat_factory):
    """Test that zero total assets returns NaN for ratio-based metrics."""
    compustat_df = sample_compustat_factory(n_firms=1, n_years=1, seed=42)
    compustat_df.loc[0, "at"] = 0.0  # Set assets to zero
    
    result = calculate_firm_controls(row, compustat_df, 2000)
    
    assert pd.isna(result["size"])
    assert pd.isna(result["leverage"])
```

---

*Testing analysis: 2026-02-21*
