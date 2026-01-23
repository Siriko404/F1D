# Phase 11: Testing Infrastructure - Research

**Researched:** 2026-01-23
**Domain:** Python Testing with pytest, Pandas/NumPy Testing, Data Pipeline Testing
**Confidence:** HIGH

## Summary

Phase 11 requires establishing a comprehensive testing framework for a data processing pipeline project (F1D_Clarity) that processes financial and textual data. The project uses pandas, NumPy, PyArrow, statsmodels, and sklearn, and already has a single test file (`test_chunked_reader.py`) demonstrating basic testing patterns.

The research identified **pytest 7.4+** as the standard testing framework, configured via `pyproject.toml` (modern approach) with `pytest-cov` for coverage reporting. The project structure already follows recommended patterns with `2_Scripts/` containing application code, suggesting a `tests/` directory at the root level for test organization.

**Key findings:**
- Use `pyproject.toml` for pytest configuration (not pytest.ini or setup.cfg)
- Fixtures are essential for test data management (pandas DataFrames, Parquet files)
- Parametrize edge case tests with `@pytest.mark.parametrize`
- Regression testing via checksum comparison (existing pattern in `test_parallelization.py`)
- Mock pandas operations with minimal mocking (prefer fixtures over mocks)

**Primary recommendation:** Use pytest with pyproject.toml configuration, tests/ directory structure, fixtures for test data, pytest-cov for coverage, and parametrization for edge cases. Target 80%+ coverage for shared modules and 50%+ for main pipeline scripts.

## Standard Stack

The established libraries/tools for Python testing in 2026:

### Core
| Library | Version | Purpose | Why Standard |
|----------|---------|---------|--------------|
| pytest | 8.0+ | Testing framework | Mature, extensible, excellent documentation, supports Python 3.7+ (project uses 3.13) |
| pytest-cov | 7.0+ | Coverage reporting | Industry standard for pytest, integrates seamlessly with coverage.py |
| pandas | 2.2.3 | Data manipulation | Already in project, essential for testing data pipelines |

### Supporting
| Library | Version | Purpose | When to Use |
|----------|---------|---------|-------------|
| numpy | 2.3.2 | Numerical testing | Already in project, testing array operations |
| pytest-mock | 3.12+ | Mocking fixtures | When mocking is necessary (prefer fixtures) |
| pytest-xdist | 3.6+ | Parallel test execution | For large test suites (>100 tests) |
| pytest-asyncio | 0.21+ | Async testing | If async code is added (not current) |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pytest | unittest | unittest is built-in but requires more boilerplate, less flexible fixtures |
| pytest-cov | coverage.py | pytest-cov provides better integration and reporting |
| pyproject.toml | pytest.ini | pyproject.toml is modern, supports other tool configs, pytest.ini is deprecated path |
| pytest-xdist | pytest-parallel | xdist is better maintained, supports load balancing |

**Installation:**
```bash
# Add to requirements.txt or requirements-dev.txt
pytest>=8.0.0
pytest-cov>=7.0.0
pytest-mock>=3.12.0  # Optional, for advanced mocking

# Install
pip install pytest pytest-cov pytest-mock
```

## Architecture Patterns

### Recommended Project Structure
```
F1D/
├── 2_Scripts/              # Application code (existing)
│   ├── shared/             # Shared modules (existing)
│   │   ├── chunked_reader.py
│   │   ├── data_validation.py
│   │   ├── env_validation.py
│   │   ├── subprocess_validation.py
│   │   └── test_chunked_reader.py  # Existing test (move to tests/)
│   ├── 1_Sample/
│   ├── 2_Text/
│   ├── 3_Financial/
│   └── 4_Econometric/
├── tests/                  # New: All test files
│   ├── conftest.py         # Shared fixtures
│   ├── fixtures/           # Test data files
│   │   ├── sample_parquet/
│   │   ├── sample_yaml/
│   │   └── sample_csv/
│   ├── unit/               # Unit tests
│   │   ├── test_chunked_reader.py
│   │   ├── test_data_validation.py
│   │   ├── test_env_validation.py
│   │   └── test_subprocess_validation.py
│   ├── integration/         # Integration tests
│   │   ├── test_pipeline_step1.py
│   │   ├── test_pipeline_step2.py
│   │   └── test_pipeline_end_to_end.py
│   └── regression/         # Regression tests
│       ├── test_output_stability.py
│       └── test_baseline_comparison.py
├── config/
│   └── project.yaml
├── pyproject.toml          # New: pytest configuration
└── README.md
```

### Pattern 1: pytest Configuration via pyproject.toml
**What:** Configure pytest using pyproject.toml (modern approach, supported since pytest 6.0)
**When to use:** Always use pyproject.toml for new projects (not pytest.ini or setup.cfg)
**Example:**
```toml
# Source: https://docs.pytest.org/en/7.4.x/reference/customize.html#configuration

[tool.pytest.ini_options]
minversion = "8.0"
addopts = [
    "-ra",  # Show extra test summary info
    "-q",   # Quiet mode (less output)
    "--strict-markers",  # Error on unknown markers
    "--strict-config",   # Error on invalid config options
    "--import-mode=importlib",  # Use importlib for import mode (recommended)
]
testpaths = [
    "tests",
]
python_files = [
    "test_*.py",
    "*_test.py",
]
python_classes = [
    "Test*",
]
python_functions = [
    "test_*",
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "regression: marks tests as regression tests",
    "unit: marks tests as unit tests",
]
```

### Pattern 2: Fixtures for Test Data Management
**What:** Use pytest fixtures to create, manage, and clean up test data
**When to use:** Any test that needs data files (Parquet, CSV, YAML)
**Example:**
```python
# tests/conftest.py - Shared fixtures
import pytest
from pathlib import Path
import pandas as pd
import pyarrow.parquet as pq

@pytest.fixture(scope="session")
def test_data_dir():
    """Path to test data directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        "file_name": ["test1.docx", "test2.docx"],
        "Total_Words": [100, 200],
        "MaQaUnc_pct": [0.5, 0.75],
    })


@pytest.fixture
def sample_parquet_file(tmp_path, sample_dataframe):
    """Create a temporary Parquet file for testing."""
    file_path = tmp_path / "test_data.parquet"
    sample_dataframe.to_parquet(file_path)
    return file_path


@pytest.fixture
def sample_config_path(test_data_dir):
    """Path to sample project.yaml for testing."""
    config_path = test_data_dir / "sample_yaml" / "project.yaml"
    if not config_path.exists():
        pytest.skip(f"Sample config not found: {config_path}")
    return config_path
```

### Pattern 3: Parametrization for Edge Cases
**What:** Use `@pytest.mark.parametrize` to run the same test with multiple inputs
**When to use:** Testing edge cases, boundary values, multiple data scenarios
**Example:**
```python
# tests/unit/test_data_validation.py

@pytest.mark.parametrize("column_type,valid_value,invalid_value", [
    ("int", 42, "not an int"),
    ("float", 3.14, "not a float"),
    ("str", "valid", None),
])
def test_column_type_validation(column_type, valid_value, invalid_value):
    """Test column type validation handles various types correctly."""
    # Test valid value
    schema = {"col1": {"type": column_type}}
    # ... validation logic
    # Test invalid value raises error


@pytest.mark.parametrize("edge_case,expected_behavior", [
    ("empty_df", "should raise DataValidationError"),
    ("single_row", "should process correctly"),
    ("all_null_columns", "should handle gracefully"),
    ("duplicate_keys", "should deduplicate or error"),
])
def test_edge_cases(edge_case, expected_behavior):
    """Test data validation handles edge cases."""
    # Implementation uses parametrized test data
```

### Pattern 4: Testing Pandas Operations
**What:** Test pandas operations without mocking (prefer real DataFrames)
**When to use:** Testing data manipulation, filtering, aggregation
**Example:**
```python
# tests/unit/test_chunked_reader.py

import pytest
from pathlib import Path
import pandas as pd
from 2_Scripts.shared.chunked_reader import read_in_chunks


def test_read_in_chunks_produces_identical_results(sample_parquet_file):
    """Test that read_in_chunks produces same result as full read."""
    # Arrange
    df_full = pd.read_parquet(sample_parquet_file)

    # Act
    chunks = list(read_in_chunks(sample_parquet_file))
    df_chunks = pd.concat(chunks, ignore_index=True)

    # Assert
    assert df_full.equals(df_chunks), "Chunked read differs from full read!"


@pytest.mark.parametrize("chunk_size", [100, 500, 1000])
def test_read_in_chunks_with_different_chunk_sizes(sample_parquet_file, chunk_size):
    """Test that read_in_chunks works with various chunk sizes."""
    chunks = list(read_in_chunks(sample_parquet_file, chunk_size=chunk_size))
    assert len(chunks) > 0, "No chunks produced"

    # Verify total rows match
    df_full = pd.read_parquet(sample_parquet_file)
    df_chunks = pd.concat(chunks, ignore_index=True)
    assert len(df_chunks) == len(df_full), "Row count mismatch!"
```

### Pattern 5: Regression Testing via Checksums
**What:** Compare output checksums to detect regressions (existing pattern)
**When to use:** Validating output stability across code changes
**Example:**
```python
# tests/regression/test_output_stability.py

import hashlib
import pandas as pd
from pathlib import Path


def compute_dataframe_checksum(df: pd.DataFrame) -> str:
    """Compute SHA-256 checksum of a DataFrame."""
    return hashlib.sha256(
        pd.util.hash_pandas_object(df, index=False).values.tobytes()
    ).hexdigest()


@pytest.fixture(scope="session")
def baseline_checksums(test_data_dir):
    """Load baseline checksums for regression testing."""
    baseline_path = test_data_dir / "baseline_checksums.json"
    if not baseline_path.exists():
        pytest.skip(f"Baseline checksums not found: {baseline_path}")

    import json
    with open(baseline_path) as f:
        return json.load(f)


def test_regression_output_stability(baseline_checksums, sample_parquet_file):
    """Test that output hasn't changed from baseline."""
    # Arrange
    df = pd.read_parquet(sample_parquet_file)
    current_checksum = compute_dataframe_checksum(df)

    # Assert
    expected_checksum = baseline_checksums.get(sample_parquet_file.name)
    assert expected_checksum is not None, f"No baseline for {sample_parquet_file.name}"
    assert current_checksum == expected_checksum, (
        f"Regression detected for {sample_parquet_file.name}\n"
        f"Expected: {expected_checksum}\n"
        f"Got: {current_checksum}"
    )
```

### Anti-Patterns to Avoid
- **Mocking pandas DataFrames:** Use real DataFrames from fixtures, not Mock objects
- **Hard-coded test data paths:** Use `test_data_dir` fixture, not relative paths
- **Tests in application code:** Move `test_chunked_reader.py` from `2_Scripts/shared/` to `tests/unit/`
- **No test isolation:** Ensure tests don't depend on each other (use `tmp_path` fixture)
- **Ignoring edge cases:** Explicitly test empty, single-row, all-null, duplicate scenarios
- **Testing implementation details:** Test behavior, not internal implementation

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Test runner | Custom main() with assertions | pytest | Auto-discovery, fixtures, parametrization, reporting |
| Coverage reporting | Manual line counting | pytest-cov | Automatic coverage, HTML reports, integration |
| Test data management | Ad-hoc file loading | Fixtures (conftest.py) | Automatic cleanup, reuse, session/function scope |
| Test data generation | Manual DataFrame creation | pandas factories + pytest fixtures | Type safety, reuse, parametrization |
| Mocking pandas operations | Custom Mock classes | Real DataFrames from fixtures | Pandas is already tested, focus on your logic |
| Regression detection | Manual comparison | Checksum comparison with pytest | Fast, bitwise-identical detection |
| Test organization | All tests in one file | tests/ with unit/integration/regression/ | Clarity, faster test runs (skip integration) |
| Test configuration | pytest.ini | pyproject.toml | Modern, supports multiple tools |
| Subprocess testing | subprocess.run with assert | subprocess_validation module | Security, path validation |
| Floating point comparison | assert a == b | pytest.approx | Handles precision, tolerance |

**Key insight:** pytest already solves test discovery, fixtures, parametrization, markers, and coverage. Focus on writing tests, not test infrastructure. Pandas/NumPy are already tested by their maintainers; test your business logic with real data structures.

## Common Pitfalls

### Pitfall 1: Tests in Application Code Directory
**What goes wrong:** Tests in `2_Scripts/shared/` get mixed with production code
**Why it happens:** Quick test creation, following existing pattern (`test_chunked_reader.py`)
**How to avoid:** Always place tests in `tests/` directory, use `pytest` discovery
**Warning signs:** `2_Scripts/` contains `test_*.py` files, importing tests as modules

### Pitfall 2: No Test Data Management
**What goes wrong:** Hard-coded file paths, test data scattered across tests
**Why it happens:** Quick testing, not planning for fixture reuse
**How to avoid:** Use `tests/fixtures/` directory, `conftest.py` for shared fixtures
**Warning signs:** Multiple tests loading same data files with different paths

### Pitfall 3: Mocking Pandas DataFrames
**What goes wrong:** Mocking pandas methods, brittle tests, no real-world validation
**Why it happens:** Thinking you need to mock everything for "unit" tests
**How to avoid:** Use real DataFrames from fixtures, test logic not pandas internals
**Warning signs:** `from unittest.mock import Mock` with `pd.DataFrame` usage

### Pitfall 4: Missing Edge Case Tests
**What goes wrong:** Bugs surface in production with edge case data
**Why it happens:** Testing only "happy path" with sample data
**How to avoid:** Explicitly test empty, single-row, all-null, duplicate scenarios
**Warning signs:** No `@pytest.mark.parametrize` for edge cases

### Pitfall 5: Ignoring Regression Testing
**What goes wrong:** Code changes silently break existing behavior
**Why it happens:** Focusing only on new features, not stability
**How to avoid:** Use checksum-based regression tests for output validation
**Warning signs:** No baseline comparison, checksum tests in `test_parallelization.py` only

### Pitfall 6: Inconsistent Test Naming
**What goes wrong:** Tests don't follow naming conventions, not discovered by pytest
**Why it happens:** No enforcement of naming patterns
**How to avoid:** Configure `python_files` in `pyproject.toml`, run `pytest --collect-only`
**Warning signs:** Tests in files not starting with `test_` or ending with `_test.py`

### Pitfall 7: Test Dependencies
**What goes wrong:** Tests fail when run in isolation but pass when run together
**Why it happens:** Tests depend on shared state, order-dependent
**How to avoid:** Use fixtures for setup/teardown, `tmp_path` for file isolation
**Warning signs:** Tests pass with `pytest tests/` but fail with `pytest tests/test_specific.py`

## Code Examples

Verified patterns from official sources:

### pytest Configuration (pyproject.toml)
```toml
# Source: https://docs.pytest.org/en/7.4.x/reference/customize.html#configuration

[tool.pytest.ini_options]
minversion = "8.0"
addopts = [
    "-ra",
    "-q",
    "--strict-markers",
    "--strict-config",
    "--import-mode=importlib",
]
testpaths = ["tests"]
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
    "regression: marks tests as regression tests",
]
```

### Fixture for Test Data
```python
# Source: https://docs.pytest.org/en/7.4.x/explanation/fixtures.html

@pytest.fixture(scope="session")
def test_data_dir():
    """Path to test data directory (shared across all tests)."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        "file_name": ["test1.docx", "test2.docx"],
        "Total_Words": [100, 200],
    })
```

### Parametrized Edge Case Tests
```python
# Source: https://docs.pytest.org/en/7.4.x/how-to/parametrize.html

@pytest.mark.parametrize("edge_case,expected", [
    ("empty_df", "should raise error"),
    ("single_row", "should pass"),
    ("all_null_columns", "should handle gracefully"),
])
def test_edge_cases(edge_case, expected):
    """Test handling of edge cases."""
    # Implementation
```

### Pandas Testing (No Mocking)
```python
# Source: Existing pattern in 2_Scripts/shared/test_chunked_reader.py

def test_read_in_chunks_produces_identical_results(sample_parquet_file):
    """Test that read_in_chunks produces same result as full read."""
    df_full = pd.read_parquet(sample_parquet_file)
    chunks = list(read_in_chunks(sample_parquet_file))
    df_chunks = pd.concat(chunks, ignore_index=True)
    assert df_full.equals(df_chunks), "Chunked read differs from full read!"
```

### Regression Testing with Checksums
```python
# Source: Existing pattern in test_parallelization.py

def compute_dataframe_checksum(df: pd.DataFrame) -> str:
    """Compute SHA-256 checksum of a DataFrame."""
    return hashlib.sha256(
        pd.util.hash_pandas_object(df, index=False).values.tobytes()
    ).hexdigest()


def test_regression_output_stability(baseline_checksums, sample_parquet_file):
    """Test that output hasn't changed from baseline."""
    df = pd.read_parquet(sample_parquet_file)
    current_checksum = compute_dataframe_checksum(df)
    expected_checksum = baseline_checksums.get(sample_parquet_file.name)
    assert current_checksum == expected_checksum, "Regression detected!"
```

### Testing Schema Validation
```python
# Source: 2_Scripts/shared/data_validation.py

from 2_Scripts.shared.data_validation import (
    validate_dataframe_schema,
    DataValidationError,
    load_validated_parquet,
)

def test_validate_dataframe_schema_success(sample_dataframe):
    """Test schema validation passes for valid DataFrame."""
    schema = {
        "required_columns": ["file_name", "Total_Words"],
        "column_types": {"file_name": "object", "Total_Words": "int"},
    }
    # Should not raise
    validate_dataframe_schema(sample_dataframe, "test_schema", Path("test.parquet"))


def test_validate_dataframe_schema_missing_columns():
    """Test schema validation fails for missing columns."""
    df = pd.DataFrame({"col1": [1, 2]})
    schema = {"required_columns": ["missing_col"]}

    with pytest.raises(DataValidationError, match="Missing columns"):
        validate_dataframe_schema(df, "test_schema", Path("test.parquet"))
```

### Testing Subprocess Validation
```python
# Source: 2_Scripts/shared/subprocess_validation.py

from 2_Scripts.shared.subprocess_validation import (
    validate_script_path,
    run_validated_subprocess,
)

def test_validate_script_path_success(test_data_dir):
    """Test path validation allows valid scripts."""
    valid_script = test_data_dir / "sample_yaml" / "project.yaml"
    allowed_dir = test_data_dir

    # Should not raise
    result = validate_script_path(valid_script, allowed_dir)
    assert result.is_absolute()


def test_validate_script_path_outside_directory():
    """Test path validation rejects scripts outside allowed directory."""
    from pathlib import Path

    script = Path("/etc/passwd")  # Outside allowed directory
    allowed_dir = Path("/tmp")

    with pytest.raises(ValueError, match="outside allowed directory"):
        validate_script_path(script, allowed_dir)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| unittest.TestCase | pytest functions | ~2015 | Simpler syntax, better fixtures |
| pytest.ini | pyproject.toml | 2020 (pytest 6.0) | Single config file, supports multiple tools |
| Manual coverage | pytest-cov | ~2016 | Integrated coverage, HTML reports |
| Ad-hoc test data | conftest.py fixtures | ~2016 | Reusable fixtures, automatic cleanup |
| setup.cfg | pyproject.toml | 2022+ | setup.cfg deprecated for pytest |

**Deprecated/outdated:**
- **setup.cfg for pytest:** Not recommended (uses different parser, hard to debug) - use pyproject.toml
- **pytest.ini:** Still works but pyproject.toml is preferred for new projects
- **mocking pandas:** Prefer real DataFrames over mocks (pandas is already tested)
- **test files in application code:** Move to tests/ directory

## Open Questions

Things that couldn't be fully resolved:

1. **CI/CD Integration (GitHub Actions)**
   - What we know: No `.github/` directory exists, no GitHub Actions workflow
   - What's unclear: Should GitHub Actions be configured in Phase 11 or later?
   - Recommendation: Add GitHub Actions workflow in Phase 12 (CI/CD), focus on test infrastructure in Phase 11

2. **Test Coverage Targets**
   - What we know: Coverage reporting via pytest-cov is standard
   - What's unclear: What coverage percentage targets are appropriate?
   - Recommendation: Target 80%+ for shared modules, 50%+ for main pipeline scripts (adjust based on complexity)

3. **Parallel Test Execution**
   - What we know: pytest-xdist supports parallel test execution
   - What's unclear: Is parallel test execution needed (test suite size unknown)?
   - Recommendation: Defer pytest-xdist until test suite grows (>100 tests)

4. **Mocking Strategy for External Dependencies**
   - What we know: pytest-mock provides mocking fixtures
   - What's unclear: What external dependencies need mocking (database, APIs)?
   - Recommendation: Current codebase is self-contained, defer mocking until Phase 12+ (CI/CD, WRDS integration)

## Sources

### Primary (HIGH confidence)
- **pytest 7.4 documentation** - Configuration, fixtures, parametrization, test discovery
  - https://docs.pytest.org/en/7.4.x/
  - https://docs.pytest.org/en/7.4.x/reference/customize.html#configuration
  - https://docs.pytest.org/en/7.4.x/explanation/fixtures.html
  - https://docs.pytest.org/en/7.4.x/how-to/parametrize.html

- **pytest-cov 7.0 documentation** - Coverage reporting configuration
  - https://pytest-cov.readthedocs.io/en/latest/

### Secondary (MEDIUM confidence)
- **Existing codebase analysis** - Current patterns and structure
  - `2_Scripts/shared/test_chunked_reader.py` - Basic testing pattern
  - `test_parallelization.py` - Regression testing with checksums
  - `2_Scripts/shared/chunked_reader.py` - Function to test
  - `2_Scripts/shared/data_validation.py` - Function to test
  - `2_Scripts/shared/env_validation.py` - Function to test
  - `2_Scripts/shared/subprocess_validation.py` - Function to test

- **Project dependencies** (verified via `requirements.txt`)
  - pandas==2.2.3
  - numpy==2.3.2
  - scipy==1.16.1
  - statsmodels==0.14.5
  - scikit-learn==1.7.2
  - lifelines==0.30.0
  - PyYAML==6.0.2
  - pyarrow==21.0.0

### Tertiary (LOW confidence)
- **Community patterns** (need validation with official sources)
  - pytest-xdist for parallel test execution (deferred - test suite size unknown)
  - pytest-mock for advanced mocking (deferred - no current need)
  - pytest-asyncio for async testing (deferred - no async code)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Official pytest documentation, verified with codebase dependencies
- Architecture: HIGH - Official pytest documentation, existing codebase patterns
- Pitfalls: HIGH - Official pytest documentation, observed issues in existing test files

**Research date:** 2026-01-23
**Valid until:** 2026-02-23 (30 days - pytest ecosystem is stable)
