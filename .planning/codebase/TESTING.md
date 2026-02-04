# Testing Patterns

**Analysis Date:** 2025-02-04

## Test Framework

**Runner:**
- pytest 8.3.3
- Config: `pyproject.toml`

**Configuration (`pyproject.toml`):**
```toml
[tool.pytest.ini_options]
minversion = "8.0"
addopts = [
    "-ra",  # Show extra test summary info
    "-q",   # Quiet mode
    "--strict-markers",
    "--strict-config",
    "--import-mode=importlib",
]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "regression: marks tests as regression tests",
    "unit: marks tests as unit tests",
    "e2e: marks tests as end-to-end pipeline tests",
]
```

**Assertion Library:**
- pytest built-in assertions
- pytest.raises for exception testing

**Run Commands:**
```bash
# Run all tests
pytest

# Run with coverage (configured in pyproject.toml)
pytest --cov=2_Scripts

# Run specific test types
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only
pytest -m "not slow"        # Exclude slow tests

# Run specific file
pytest tests/unit/test_data_validation.py

# Verbose mode
pytest -v

# Quiet mode (default in config)
pytest -q
```

## Test File Organization

**Location:**
- Co-located in `tests/` directory at project root
- Separated by type: `tests/unit/`, `tests/integration/`, `tests/regression/`

**Naming:**
- Pattern: `test_<module_name>.py`
- Examples: `test_data_validation.py`, `test_chunked_reader.py`, `test_full_pipeline.py`

**Structure:**
```
tests/
├── conftest.py                 # Shared fixtures
├── fixtures/                   # Test data and fixtures
│   └── baseline_checksums.json # Regression baselines
├── unit/                       # Unit tests for shared modules
│   ├── test_data_validation.py
│   ├── test_chunked_reader.py
│   ├── test_env_validation.py
│   └── test_observability_helpers.py
├── integration/                # Integration tests for pipeline steps
│   ├── test_pipeline_step1.py
│   ├── test_pipeline_step2.py
│   ├── test_pipeline_step3.py
│   ├── test_full_pipeline.py
│   └── test_observability_integration.py
└── regression/                 # Regression tests (checksum-based)
    ├── test_output_stability.py
    └── generate_baseline_checksums.py
```

## Test Structure

**Suite Organization:**
```python
"""
Unit tests for data_validation module.

Tests schema validation, DataValidationError exceptions, and
load_validated_parquet function.
"""

import pytest
import pandas as pd
from pathlib import Path
import sys

# Add 2_Scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "2_Scripts"))

from shared.data_validation import (
    validate_dataframe_schema,
    DataValidationError,
    load_validated_parquet,
    INPUT_SCHEMAS,
)


class TestValidateDataFrameSchema:
    """Tests for validate_dataframe_schema function."""

    def test_validate_dataframe_schema_success_with_real_data(
        self, sample_parquet_file_with_schema
    ):
        """Test schema validation passes for valid DataFrame matching Unified-info schema."""
        df = pd.read_parquet(sample_parquet_file_with_schema)
        # Should not raise for valid schema match
        validate_dataframe_schema(
            df, "Unified-info.parquet", sample_parquet_file_with_schema
        )

    def test_validate_dataframe_schema_missing_columns_with_real_schema(
        self, sample_parquet_file_with_schema
    ):
        """Test schema validation fails for missing required columns using actual schema."""
        df = pd.DataFrame({"event_type": [1, 2]})
        with pytest.raises(DataValidationError, match="Missing columns"):
            validate_dataframe_schema(
                df, "Unified-info.parquet", sample_parquet_file_with_schema
            )
```

**Patterns:**

1. **Setup:**
   - Add `2_Scripts` to sys.path at module level
   - Import functions and classes from shared modules
   - Use descriptive test class names: `Test<FunctionName>`

2. **Teardown:**
   - No explicit teardown needed (pytest handles fixtures automatically)
   - Temporary files created with `tmp_path` fixture auto-cleaned

3. **Assertion Pattern:**
   - Use pytest's context managers for exceptions:
   ```python
   with pytest.raises(DataValidationError, match="Missing columns"):
       validate_dataframe_schema(invalid_df, schema_name, file_path)
   ```

   - Direct assertions for return values:
   ```python
   assert len(df) == 3
   assert "file_name" in df.columns
   assert current_checksum == expected_checksum
   ```

## Mocking

**Framework:** No explicit mocking framework detected (unittest.mock not used in patterns)

**Patterns:**
- Use real data files from `tests/fixtures/`
- Skip tests if fixtures not available:
```python
@pytest.fixture(scope="session")
def sample_config_path(test_data_dir):
    """Path to sample project.yaml for testing."""
    config_path = test_data_dir / "sample_yaml" / "project.yaml"
    if not config_path.exists():
        pytest.skip(f"Sample config not found: {config_path}")
    return config_path
```

**What to Mock:**
- External file I/O (not common - prefer real fixtures)
- Time-dependent operations (not currently mocked)

**What NOT to Mock:**
- pandas operations (use real DataFrames)
- File path resolution (use real paths with tmp_path)
- Data validation logic (test actual behavior)

## Fixtures and Factories

**Test Data:**
Located in `tests/fixtures/`:
- `baseline_checksums.json` - Regression test baselines
- `sample_yaml/` - Sample configuration files
- Parquet files created dynamically in tests

**Location:**
```python
@pytest.fixture(scope="session")
def test_data_dir():
    """Path to test data directory (shared across all tests)."""
    return Path(__file__).parent / "fixtures"
```

**Fixture Patterns from `conftest.py`:**

1. **Sample DataFrame:**
```python
@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame(
        {
            "file_name": ["test1.docx", "test2.docx", "test3.docx"],
            "Total_Words": [100, 200, 150],
            "MaQaUnc_pct": [0.5, 0.75, 0.6],
        }
    )
```

2. **Temporary Parquet File:**
```python
@pytest.fixture
def sample_parquet_file(tmp_path, sample_dataframe):
    """Create a temporary Parquet file for testing."""
    file_path = tmp_path / "test_data.parquet"
    sample_dataframe.to_parquet(file_path)
    return file_path
```

3. **Mock Configuration:**
```python
@pytest.fixture
def mock_project_config(tmp_path):
    """Create a minimal project.yaml for testing."""
    config_data = {
        "project": {"name": "F1D_Test", "version": "1.0.0"},
        "data": {"year_start": 2002, "year_end": 2005},
        "determinism": {"random_seed": 42, "thread_count": 1},
    }
    config_path = tmp_path / "project.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config_data, f)
    return config_path
```

4. **Output Capture:**
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

## Coverage

**Requirements:**
- No explicit coverage target enforced
- Coverage configured in `pyproject.toml`:
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

**View Coverage:**
```bash
pytest --cov=2_Scripts --cov-report=html
# Open htmlcov/index.html for detailed report
```

## Test Types

**Unit Tests:**
- Scope: Individual functions and classes in shared modules
- Approach: Isolated testing with sample data
- Location: `tests/unit/`
- Examples:
  - `test_data_validation.py` - Schema validation logic
  - `test_chunked_reader.py` - Chunked reading utilities
  - `test_env_validation.py` - Environment validation

**Integration Tests:**
- Scope: End-to-end execution of individual pipeline steps
- Approach: Run scripts via subprocess, verify outputs
- Location: `tests/integration/`
- Marked with: `@pytest.mark.integration`
- Pattern:
```python
def test_step1_full_pipeline(sample_input_data, config, tmp_path):
    """Test Step 1 (1.1_CleanMetadata) runs end-to-end."""
    script_path = REPO_ROOT / "2_Scripts/1_Sample/1.1_CleanMetadata.py"

    # Run script via subprocess
    result = subprocess.run(
        ["python", str(script_path)],
        env=SUBPROCESS_ENV,
        capture_output=True,
        text=True,
    )

    # Assert
    assert result.returncode == 0
    assert output_dir.exists()
```

**E2E Tests:**
- Scope: Full pipeline execution (all 17 scripts)
- Framework: pytest with subprocess execution
- Location: `tests/integration/test_full_pipeline.py`
- Marked with: `@pytest.mark.e2e` and `@pytest.mark.slow`
- Purpose: Close critical testing gap identified in milestone audit
- Runtime: ~15-20 minutes for full pipeline
- Pattern:
```python
@pytest.mark.slow
def test_full_pipeline_execution():
    """Test end-to-end execution of the full pipeline (all 17 scripts)."""
    for script_path in PIPELINE_SCRIPTS:
        result = subprocess.run(
            ["python", str(script_path)],
            env=SUBPROCESS_ENV,
            timeout=600,
        )
        assert result.returncode == 0
        # Verify expected outputs exist
```

**Regression Tests:**
- Scope: Detect regressions via checksum comparison
- Approach: Compare SHA-256 checksums of output files to baseline
- Location: `tests/regression/test_output_stability.py`
- Marked with: `@pytest.mark.regression`
- Pattern:
```python
def test_regression_step1_output_stability(baseline_checksums):
    """Test that Step 1 output hasn't changed from baseline."""
    current_checksum = compute_file_checksum(output_file)
    expected_checksum = baseline_checksums.get("step1_cleaned_metadata")

    assert current_checksum == expected_checksum, (
        f"Regression detected!\n"
        f"Expected: {expected_checksum}\n"
        f"Got: {current_checksum}\n"
    )
```

## Common Patterns

**Async Testing:**
- Not used (synchronous Python codebase)

**Error Testing:**
```python
def test_load_validated_parquet_validation_failure(self, tmp_path):
    """Load Parquet file with invalid schema raises error."""
    df = pd.DataFrame({"col1": [1, 2, 3]})
    invalid_file = tmp_path / "invalid.parquet"
    df.to_parquet(invalid_file)

    with pytest.raises(DataValidationError, match="Missing columns"):
        load_validated_parquet(invalid_file, schema_name="Unified-info.parquet")
```

**Parameterized Tests:**
```python
@pytest.mark.parametrize(
    "strict_mode,should_raise",
    [
        (True, True),
        (False, False),
    ],
)
def test_validate_dataframe_schema_strict_mode(
    self, strict_mode, should_raise, sample_parquet_file_with_schema
):
    """Test strict mode controls whether errors are raised."""
    if should_raise:
        with pytest.raises(DataValidationError):
            validate_dataframe_schema(
                df, "Unified-info.parquet",
                sample_parquet_file_with_schema,
                strict=strict_mode,
            )
```

**Skip Conditions:**
```python
def test_step1_full_pipeline(sample_input_data, config, tmp_path):
    if not script_path.exists():
        pytest.skip(f"Script not found: {script_path}")
```

**Integration Test Environment:**
```python
# Environment for subprocess calls (includes PYTHONPATH)
SUBPROCESS_ENV = {
    "PYTHONPATH": str(REPO_ROOT / "2_Scripts"),
    **os.environ,
}
```

**Subprocess Testing:**
```python
result = subprocess.run(
    ["python", str(script_path)],
    env=SUBPROCESS_ENV,
    capture_output=True,
    text=True,
    timeout=600,
)

assert result.returncode == 0, f"Script failed: {result.stderr}"
```

## Test Markers

**Usage:**
```python
# Mark entire test file
pytestmark = pytest.mark.integration

# Mark individual test
@pytest.mark.slow
def test_full_pipeline_execution():
    ...

# Mark parameterized tests
@pytest.mark.regression
def test_regression_step1_output_stability():
    ...
```

**Running by marker:**
```bash
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests only
pytest -m "not slow"     # Exclude slow tests
pytest -m "e2e or slow"  # E2E or slow tests
```

## Baseline Management

**Generating Baselines:**
Located at `tests/regression/generate_baseline_checksums.py`
- Computes SHA-256 checksums for key output files
- Updates `tests/fixtures/baseline_checksums.json`
- Run after intentional changes to expected outputs

**Pattern:**
```python
def compute_dataframe_checksum(df: pd.DataFrame) -> str:
    """Compute SHA-256 checksum of a DataFrame."""
    return hashlib.sha256(
        pd.util.hash_pandas_object(df, index=False).values.tobytes()
    ).hexdigest()
```

**Key Outputs Tracked:**
- `step1_cleaned_metadata` - Step 1 cleaned metadata
- `step2_linguistic_counts_<year>` - Step 2 yearly outputs (2002-2018)
- `step3_financial_features` - Step 3 financial features

---

*Testing analysis: 2025-02-04*
