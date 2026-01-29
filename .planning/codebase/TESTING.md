# Testing Patterns

**Analysis Date:** 2025-01-29

## Test Framework

**Runner:**
- pytest 8.0+ (specified in `pyproject.toml`)
- Config: `pyproject.toml` with pytest settings

**Assertion Library:**
- pytest's built-in `assert` statement
- `pytest.raises()` for exception testing

**Run Commands:**
```bash
# Run all tests
pytest

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only regression tests
pytest -m regression

# Exclude slow tests
pytest -m "not slow"

# Run with coverage
pytest --cov=2_Scripts --cov-report=html

# Run specific test file
pytest tests/unit/test_data_validation.py

# Verbose output
pytest -v
```

**pytest Configuration:**
```toml
[tool.pytest.ini_options]
minversion = "8.0"
addopts = ["-ra", "-q", "--strict-markers", "--strict-config", "--import-mode=importlib"]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

## Test File Organization

**Location:**
- Co-located with source: No
- Separate directory: Yes (`tests/` directory at project root)

**Naming:**
- Unit tests: `test_<module_name>.py` in `tests/unit/`
- Integration tests: `test_<feature>.py` in `tests/integration/`
- Regression tests: `test_<subject>.py` in `tests/regression/`
- Edge case tests: `test_<module>_edge_cases.py` in `tests/unit/`

**Structure:**
```
tests/
├── conftest.py                 # Shared fixtures
├── fixtures/                   # Test data and mocks
│   ├── sample_yaml/
│   │   └── project.yaml        # Sample config
│   └── baseline_checksums.json # Regression baseline
├── unit/                       # Unit tests
│   ├── test_data_validation.py
│   ├── test_env_validation.py
│   ├── test_subprocess_validation.py
│   ├── test_fuzzy_matching.py
│   ├── test_chunked_reader.py
│   ├── test_observability_helpers.py
│   └── *_edge_cases.py         # Edge case tests
├── integration/                # Integration tests
│   └── e2e_test_*.py           # End-to-end pipeline tests
└── regression/                 # Regression tests
    ├── test_output_stability.py
    └── generate_baseline_checksums.py
```

## Test Structure

**Suite Organization:**
```python
"""
Unit tests for module_name.

Tests description of what's being tested.
"""

import pytest
import pandas as pd
from pathlib import Path
import sys

# Add 2_Scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "2_Scripts"))

from shared.module_name import function_name, ExceptionClass


class TestFunctionality:
    """Tests for function_name feature group."""

    def test_success_case(self, sample_fixture):
        """Test success scenario."""
        result = function_name(sample_fixture)
        assert result == expected_value

    def test_edge_case(self, sample_fixture):
        """Test edge case (empty, null, boundary values)."""
        result = function_name(edge_case_value)
        assert result == expected_edge_result


class TestExceptions:
    """Tests for exception handling."""

    def test_raises_on_invalid_input(self):
        """Test that appropriate exception is raised."""
        with pytest.raises(ExceptionClass, match="error message"):
            function_name(invalid_input)
```

**Patterns:**

**Setup Pattern:**
- Use `pytest.fixture` for setup
- Scope options: `function` (default), `class`, `module`, `session`
- Session-scoped fixtures for expensive operations (loading test data)

**Example from `conftest.py`:**
```python
@pytest.fixture(scope="session")
def test_data_dir():
    """Path to test data directory (shared across all tests)."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        "file_name": ["test1.docx", "test2.docx", "test3.docx"],
        "Total_Words": [100, 200, 150],
        "MaQaUnc_pct": [0.5, 0.75, 0.6],
    })


@pytest.fixture
def sample_parquet_file(tmp_path, sample_dataframe):
    """Create a temporary Parquet file for testing."""
    file_path = tmp_path / "test_data.parquet"
    sample_dataframe.to_parquet(file_path)
    return file_path
```

**Teardown Pattern:**
- Use `tmp_path` fixture for temporary files (auto-cleanup)
- Fixture cleanup via `yield`:
```python
@pytest.fixture
def capture_output():
    """Capture stdout and stderr for testing console output."""
    class Capture:
        def __init__(self):
            self.stdout_buf = StringIO()
            self.stderr_buf = StringIO()
            self.old_stdout = sys.stdout
            self.old_stderr = sys.stderr

        def start(self):
            sys.stdout = self.stdout_buf
            sys.stderr = self.stderr_buf

        def stop(self):
            sys.stdout = self.old_stdout
            sys.stderr = self.old_stderr
            return (self.stdout_buf.getvalue(), self.stderr_buf.getvalue())

    capture = Capture()
    yield capture
    # Cleanup: restore original streams
    sys.stdout = capture.old_stdout
    sys.stderr = capture.old_stderr
```

**Assertion Pattern:**
- Use `assert` for simple comparisons
- Use `pytest.raises` context manager for exceptions
- Use `capsys` fixture for capturing stdout/stderr
- Use `monkeypatch` fixture for modifying environment/dependencies

**Example:**
```python
def test_validate_dataframe_schema_success(self, sample_parquet_file):
    """Test schema validation passes for valid DataFrame."""
    df = pd.read_parquet(sample_parquet_file)
    # Should not raise for valid schema match
    validate_dataframe_schema(df, "schema_name", sample_parquet_file)


def test_validate_dataframe_schema_missing_columns(self):
    """Test schema validation fails for missing required columns."""
    df = pd.DataFrame({"col1": [1, 2]})  # Missing required columns
    with pytest.raises(DataValidationError, match="Missing columns"):
        validate_dataframe_schema(df, "schema_name", Path("test.parquet"))


def test_prints_warning(self, capsys):
    """Test that warning is printed to console."""
    function_that_warns()
    captured = capsys.readouterr()
    assert "WARNING:" in captured.out
```

## Mocking

**Framework:** pytest built-ins (monkeypatch, tmp_path, capsys, fixtures)

**Patterns:**

**Environment Variable Mocking:**
```python
def test_with_env_var(self, monkeypatch):
    """Test with specific environment variable."""
    monkeypatch.setenv("WRDS_USERNAME", "test_user")
    result = function_using_env()
    assert result == expected
```

**Module/Function Mocking:**
```python
def test_with_mocked_function(self, monkeypatch):
    """Test with mocked function."""
    def mock_validate(schema):
        raise EnvValidationError("Test error")

    import shared.env_validation as env_mod
    original_validate = env_mod.validate_env_schema
    env_mod.validate_env_schema = mock_validate

    # Test code here...

    # Restore original function
    env_mod.validate_env_schema = original_validate
```

**File System Mocking:**
```python
def test_with_temp_file(self, tmp_path):
    """Test with temporary file."""
    # tmp_path is auto-cleanup fixture
    test_file = tmp_path / "test.parquet"
    df.to_parquet(test_file)
    result = process_file(test_file)
    assert result == expected
```

**What to Mock:**
- External dependencies (WRDS API, file system, network calls)
- Environment variables
- Expensive operations (database queries, API calls)
- Time-dependent operations (use `monkeypatch.setattr` for datetime)

**What NOT to Mock:**
- Shared utility functions (test them directly)
- Simple data processing functions
- Pandas operations (use real DataFrames)

## Fixtures and Factories

**Test Data:**
```python
# From conftest.py
@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        "file_name": ["test1.docx", "test2.docx", "test3.docx"],
        "Total_Words": [100, 200, 150],
        "MaQaUnc_pct": [0.5, 0.75, 0.6],
    })


@pytest.fixture
def sample_parquet_file_with_schema(tmp_path):
    """Create a temporary Parquet file matching Unified-info schema."""
    df = pd.DataFrame({
        "event_type": [1, 1, 2],
        "file_name": ["call1.docx", "call2.docx", "call3.docx"],
        "date": ["2002-01-15", "2002-02-20", "2002-03-10"],
        "speakers": ["CEO,CFO", "CEO", "CFO"],
    })
    file_path = tmp_path / "unified_info_test.parquet"
    df.to_parquet(file_path)
    return file_path


@pytest.fixture
def mock_project_config(tmp_path):
    """Create a minimal project.yaml for testing."""
    config_data = {
        "project": {"name": "F1D_Test", "version": "1.0.0"},
        "data": {"year_start": 2002, "year_end": 2005},
        "determinism": {"random_seed": 42, "thread_count": 1},
    }
    config_path = tmp_path / "project.yaml"
    import yaml
    with open(config_path, "w") as f:
        yaml.dump(config_data, f)
    return config_path
```

**Location:**
- Shared fixtures in `tests/conftest.py`
- Test-specific fixtures in test files
- Test data in `tests/fixtures/`

**Factory Pattern:**
- Use fixture functions to create test data
- Parameterize fixtures for multiple scenarios
- Use `tmp_path` for auto-cleanup

## Coverage

**Requirements:** None enforced (no coverage thresholds in config)

**View Coverage:**
```bash
# Generate HTML coverage report
pytest --cov=2_Scripts --cov-report=html

# View report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
xdg-open htmlcov/index.html  # Linux
```

**Coverage Configuration:**
```toml
[tool.coverage.run]
source = ["2_Scripts"]
omit = [
    "*/tests/*",
    "*/__pycache__/*",
    "*/ARCHIVE*/*",
    "*/ARCHIVE_OLD*/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
```

## Test Types

**Unit Tests:**
- **Scope:** Individual functions, classes, modules
- **Approach:** Test smallest units in isolation
- **Location:** `tests/unit/`
- **Examples:**
  - `test_data_validation.py` - Schema validation functions
  - `test_env_validation.py` - Environment variable validation
  - `test_subprocess_validation.py` - Subprocess execution validation
  - `test_fuzzy_matching.py` - String matching functions
  - `test_chunked_reader.py` - Chunked data reading
  - `test_observability_helpers.py` - Statistics and monitoring helpers

**Integration Tests:**
- **Scope:** Multiple components working together
- **Approach:** Test interactions between modules
- **Location:** `tests/integration/`
- **Examples:**
  - End-to-end pipeline tests
  - Multi-step workflow tests
  - File: `e2e_test_*.py`

**Regression Tests:**
- **Scope:** Detect changes in output over time
- **Approach:** Compare SHA-256 checksums to baseline
- **Location:** `tests/regression/`
- **Example:** `test_output_stability.py`

**Regression Test Pattern:**
```python
def compute_dataframe_checksum(df: pd.DataFrame) -> str:
    """Compute SHA-256 checksum of a DataFrame."""
    return hashlib.sha256(
        pd.util.hash_pandas_object(df, index=False).values.tobytes()
    ).hexdigest()


@pytest.fixture(scope="session")
def baseline_checksums():
    """Load baseline checksums for regression testing."""
    baseline_path = Path("tests/fixtures/baseline_checksums.json")
    if not baseline_path.exists():
        pytest.skip(f"Baseline checksums not found: {baseline_path}")
    with open(baseline_path) as f:
        return json.load(f)


def test_regression_step1_output_stability(baseline_checksums):
    """Test that Step 1 output hasn't changed from baseline."""
    output_file = Path("4_Outputs/1.1_CleanMetadata/latest/cleaned_metadata.parquet")
    if not output_file.exists():
        pytest.skip(f"Output file not found (run 1.1_CleanMetadata.py first)")

    current_checksum = compute_file_checksum(output_file)
    expected_checksum = baseline_checksums.get("step1_cleaned_metadata")

    if expected_checksum is None:
        pytest.skip("No baseline checksum (run with --update-baseline)")

    assert current_checksum == expected_checksum, (
        f"Regression detected!\n"
        f"Expected: {expected_checksum}\n"
        f"Got: {current_checksum}"
    )
```

## Common Patterns

**Async Testing:**
- Not applicable (no async code in codebase)

**Error Testing:**
```python
def test_raises_exception_with_message(self):
    """Test exception is raised with specific message."""
    with pytest.raises(DataValidationError, match="Missing columns"):
        validate_dataframe_schema(invalid_df, "schema_name", Path("test.parquet"))


def test_exception_message_format(self):
    """Test exception message includes required information."""
    with pytest.raises(EnvValidationError) as exc_info:
        validate_env_schema(test_schema)
    error_msg = str(exc_info.value)
    assert "Required environment variable not set" in error_msg
    assert "TEST_VAR" in error_msg
    assert "Important test variable" in error_msg
```

**Parameterized Tests:**
```python
@pytest.mark.parametrize(
    "env_name,env_spec",
    [
        ("WRDS_USERNAME", {"required": False, "type": str, "description": "WRDS username"}),
        ("API_TIMEOUT_SECONDS", {"required": False, "type": int, "default": 30}),
    ],
)
def test_validate_env_with_actual_schema(self, env_name, env_spec, monkeypatch):
    """Test validation with actual ENV_SCHEMA entries."""
    # Test code using env_name and env_spec...
```

**Skipping Tests:**
```python
def test_with_conditional_skip(self, sample_fixture):
    """Skip test if condition not met."""
    if not sample_fixture.exists():
        pytest.skip(f"Sample fixture not found: {sample_fixture}")
    # Test code...


def test_skip_if_module_missing(self):
    """Skip test if optional dependency not available."""
    pytest.importorskip("rapidfuzz")  # Skip if rapidfuzz not installed
    # Test code using rapidfuzz...
```

**Testing with Missing Optional Dependencies:**
```python
def test_graceful_degradation_without_rapidfuzz(self, monkeypatch):
    """Test fallback behavior when RapidFuzz is unavailable."""
    # Mock rapidfuzz as unavailable
    monkeypatch.setattr("shared.string_matching.RAPIDFUZZ_AVAILABLE, False)

    result = match_company_names("Test", ["Candidate1", "Candidate2"])

    # Should return query with 0.0 score (fallback behavior)
    assert result == ("Test", 0.0)
```

## Test Markers

**Available Markers:**
- `slow` - Marks tests as slow (deselect with `-m "not slow"`)
- `integration` - Marks integration tests
- `regression` - Marks regression tests
- `unit` - Marks unit tests
- `e2e` - Marks end-to-end pipeline tests

**Usage:**
```python
@pytest.mark.slow
def test_slow_operation():
    """Test that takes a long time."""
    # Slow test code...


@pytest.mark.regression  # Mark all tests in file
def test_regression_step1_output_stability():
    """Regression test for Step 1."""
    # Regression test code...
```

**Running with Markers:**
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only regression tests
pytest -m regression

# Exclude slow tests
pytest -m "not slow"

# Run only fast unit tests
pytest -m "unit and not slow"
```

---

*Testing analysis: 2025-01-29*
