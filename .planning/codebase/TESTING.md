# Testing Patterns

**Analysis Date:** 2026-01-24

## Test Framework

**Runner:**
- pytest 8.0+ (minversion specified in config)
- Config: `pyproject.toml` (pytest configuration)
- Run on Python 3.8-3.13 (CI matrix)

**Assertion Library:**
- Built-in pytest assertions

**Run Commands:**
```bash
# Run all tests
pytest tests/ -v

# Run specific test type
pytest tests/ -m unit -v                # Unit tests only
pytest tests/ -m integration -v          # Integration tests only
pytest tests/ -m regression -v          # Regression tests only
pytest tests/ -m e2e -v                 # End-to-end tests only

# Run excluding slow tests
pytest tests/ -m "not slow" -v

# Run with coverage
pytest tests/ -m "not e2e" --cov=2_Scripts --cov-report=xml --cov-report=html --cov-report=term -v

# Watch mode (if pytest-xdist installed)
pytest tests/ -v --watch

# Coverage view
pytest tests/ --cov=2_Scripts --cov-report=html
open htmlcov/index.html  # View coverage report
```

## Test File Organization

**Location:**
- Separate test directory: `tests/`
- Organized by type: `tests/unit/`, `tests/integration/`, `tests/regression/`
- Shared fixtures: `tests/fixtures/`

**Naming:**
- `test_<module>.py` (e.g., `test_data_validation.py`, `test_subprocess_validation.py`)
- `_test.py` pattern also supported (but less common)

**Structure:**
```
tests/
├── conftest.py                    # Shared fixtures
├── fixtures/
│   ├── baseline_checksums.json    # Regression test baselines
│   └── sample_yaml/              # Sample config files
├── unit/                         # Unit tests
│   ├── test_data_validation.py
│   ├── test_path_utils.py
│   └── ...
├── integration/                  # Integration tests
│   ├── test_pipeline_step1.py
│   ├── test_pipeline_step2.py
│   └── ...
└── regression/                   # Regression tests
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
        df = pd.DataFrame({"event_type": [1, 2]})  # Missing file_name, date, speakers
        with pytest.raises(DataValidationError, match="Missing columns"):
            validate_dataframe_schema(
                df, "Unified-info.parquet", sample_parquet_file_with_schema
            )

    @pytest.mark.parametrize(
        "strict_mode,should_raise",
        [
            (True, True),
            (False, False),
        ],
    )
    def test_validate_dataframe_schema_strict_mode_with_real_schema(
        self, strict_mode, should_raise, sample_parquet_file_with_schema
    ):
        """Test strict mode controls whether errors are raised using actual schema."""
        df = pd.DataFrame({"event_type": [1, 2]})  # Missing required columns
        if should_raise:
            with pytest.raises(DataValidationError):
                validate_dataframe_schema(
                    df,
                    "Unified-info.parquet",
                    sample_parquet_file_with_schema,
                    strict=strict_mode,
                )
        else:
            # Should not raise in non-strict mode
            validate_dataframe_schema(
                df,
                "Unified-info.parquet",
                sample_parquet_file_with_schema,
                strict=strict_mode,
            )
```

**Patterns:**
- **Setup pattern:** Use `@pytest.fixture` for shared setup
- **Teardown pattern:** Use `yield` in fixtures, or implicit cleanup
- **Assertion pattern:** Standard pytest assertions (`assert condition, message`)

**Test markers:**
```python
# File-level marker
pytestmark = pytest.mark.unit

# Class-level marker
class TestValidateScriptPath:
    """Tests for validate_script_path function."""

# Function-level marker
@pytest.mark.slow
def test_large_dataset():
    pass

@pytest.mark.integration
def test_pipeline_execution():
    pass

@pytest.mark.regression
def test_output_stability():
    pass
```

## Mocking

**Framework:**
- `unittest.mock.patch` for subprocess mocking
- No third-party mocking library detected

**Patterns:**
```python
from unittest.mock import patch

class TestRunValidatedSubprocess:
    """Tests for run_validated_subprocess function."""

    @patch("subprocess.run")
    def test_run_validated_subprocess_success(self, mock_run, tmp_path):
        """Test subprocess execution with validated path."""
        # Create test script
        script = tmp_path / "test.py"
        script.write_text("print('success')")
        allowed_dir = tmp_path

        # Mock subprocess.run to return success
        mock_run.return_value = subprocess.CompletedProcess(
            args=["python", str(script)], returncode=0, stdout="success\n", stderr=""
        )

        result = run_validated_subprocess(script, allowed_dir)

        assert result.returncode == 0
        assert result.stdout == "success\n"

        # Verify subprocess.run was called with validated path
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert sys.executable in call_args
```

**What to Mock:**
- External subprocess calls
- File I/O (using `tmp_path` fixture)
- Network calls (if any)

**What NOT to Mock:**
- Pandas operations (use real DataFrames)
- Data validation logic (test actual behavior)
- Path operations (use `tmp_path` fixture)

## Fixtures and Factories

**Test Data:**
```python
# In conftest.py
@pytest.fixture(scope="session")
def test_data_dir():
    """Path to test data directory (shared across all tests)."""
    return Path(__file__).parent / "fixtures"


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


@pytest.fixture
def sample_parquet_file(tmp_path, sample_dataframe):
    """Create a temporary Parquet file for testing."""
    file_path = tmp_path / "test_data.parquet"
    sample_dataframe.to_parquet(file_path)
    return file_path


@pytest.fixture
def mock_project_config(tmp_path):
    """Create a minimal project.yaml for testing."""
    config_data = {
        "project": {
            "name": "F1D_Test",
            "version": "1.0.0",
        },
        "data": {
            "year_start": 2002,
            "year_end": 2005,
        },
        "determinism": {
            "random_seed": 42,
            "thread_count": 1,
        },
    }
    config_path = tmp_path / "project.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config_data, f)
    return config_path
```

**Location:**
- `tests/conftest.py` for global fixtures
- Test-specific fixtures in individual test files

**Fixture scopes:**
- `session`: Shared across all tests (e.g., `test_data_dir`)
- `function`: Default, fresh for each test
- `module`: Shared across tests in a module

## Coverage

**Requirements:**
- Coverage for `2_Scripts` directory only
- Excludes: `*/tests/*`, `*/__pycache__/*`, `*/ARCHIVE*/*`, `*/ARCHIVE_OLD*/*`

**View Coverage:**
```bash
# Run tests with coverage
pytest tests/ -m "not e2e" --cov=2_Scripts --cov-report=term -v

# Generate HTML coverage report
pytest tests/ --cov=2_Scripts --cov-report=html
open htmlcov/index.html

# Coverage in CI
pytest tests/ -m "not e2e" --cov=2_Scripts --cov-report=xml --cov-report=html
```

**Exclude lines:**
```python
# In pyproject.toml
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
- **Scope:** Test individual functions and modules in isolation
- **Approach:** Test shared utilities, validation functions, path handling
- **Location:** `tests/unit/`
- **Examples:**
  - `test_data_validation.py` - Schema validation
  - `test_path_utils.py` - Path operations
  - `test_subprocess_validation.py` - Security validation

**Integration Tests:**
- **Scope:** Test end-to-end pipeline steps
- **Approach:** Execute actual scripts, verify output files and stats.json
- **Location:** `tests/integration/`
- **Examples:**
  - `test_pipeline_step1.py` - Sample construction pipeline
  - `test_pipeline_step2.py` - Text processing pipeline
  - `test_observability_integration.py` - Logging/stats.json integration

**Regression Tests:**
- **Scope:** Ensure output stability across code changes
- **Approach:** Compare SHA-256 checksums of output files to baseline
- **Location:** `tests/regression/`
- **Examples:**
  - `test_output_stability.py` - Checksum comparison

**E2E Tests:**
- **Scope:** Full pipeline execution
- **Approach:** Run complete pipeline from start to finish
- **Location:** `tests/integration/` (marked with `@pytest.mark.e2e`)
- **Status:** Not commonly run (separate CI job)

## Common Patterns

**Async Testing:**
- Not used in this codebase (no async functions detected)

**Error Testing:**
```python
def test_validate_script_path_not_py_file(self, tmp_path):
    """Test path validation rejects non-.py files."""
    # Create a non-Python file
    not_py_file = tmp_path / "test.txt"
    not_py_file.write_text("not a python file")
    allowed_dir = tmp_path

    with pytest.raises(ValueError, match="Script must be .py file"):
        validate_script_path(not_py_file, allowed_dir)

def test_validate_script_path_file_not_found(self, tmp_path):
    """Test path validation raises error for non-existent file."""
    script = tmp_path / "nonexistent.py"
    allowed_dir = tmp_path

    with pytest.raises(FileNotFoundError, match="Script not found"):
        validate_script_path(script, allowed_dir)
```

**Edge Case Testing:**
```python
# From tests/unit/README_edge_cases.md
# Common edge cases:
# 1. Empty Datasets: DataFrame with no rows
# 2. Single Row DataFrames: DataFrame with one row
# 3. All-Null Columns: All values are null
# 4. Boundary Values: Min/max values for types
# 5. Type Extremes: Maximum values for types
# 6. Missing Files: File not found errors

@pytest.mark.parametrize(
    "path_name,should_validate",
    [
        ("script.py", True),
        ("main.py", True),
        ("test_123.py", True),
        ("script.txt", False),
        ("script.sh", False),
    ],
)
def test_validate_script_path_extension_check(
    self, path_name, should_validate, tmp_path
):
    """Test path validation checks .py extension."""
    script = tmp_path / path_name
    script.write_text("print('test')")

    allowed_dir = tmp_path

    if should_validate:
        result = validate_script_path(script, allowed_dir)
        assert result.suffix == ".py"
    else:
        with pytest.raises(ValueError, match="Script must be .py file"):
            validate_script_path(script, allowed_dir)
```

**Parametrization for Edge Cases:**
```python
@pytest.mark.parametrize(
    "rel_path,expected_valid",
    [
        ("../script.py", False),  # Parent directory traversal
        ("../../script.py", False),  # Multi-level traversal
        (".", False),  # Current directory
        ("..", False),  # Parent directory
    ],
)
def test_validate_script_path_traversal_prevention(
    self, rel_path, expected_valid, tmp_path
):
    """Test path validation prevents directory traversal attacks."""
    allowed_dir = tmp_path

    if not expected_valid:
        # Should not validate traversal attempts
        with pytest.raises((ValueError, FileNotFoundError)):
            validate_script_path(rel_path, allowed_dir)
```

**Deterministic Testing:**
```python
def test_deterministic_behavior():
    """Test that anomaly detection is deterministic."""
    df = pd.DataFrame({"A": [1, 2, 3, 4, 100]})

    # Run z-score detection twice
    result1 = detect_anomalies_zscore(df, ["A"], threshold=3.0)
    result2 = detect_anomalies_zscore(df, ["A"], threshold=3.0)
    assert result1 == result2, "z-score detection should be deterministic"

    # Run IQR detection twice
    result1 = detect_anomalies_iqr(df, ["A"], multiplier=3.0)
    result2 = detect_anomalies_iqr(df, ["A"], multiplier=3.0)
    assert result1 == result2, "IQR detection should be deterministic"
```

**Regression Testing (Checksum-based):**
```python
def compute_dataframe_checksum(df: pd.DataFrame) -> str:
    """Compute SHA-256 checksum of a DataFrame."""
    return hashlib.sha256(
        pd.util.hash_pandas_object(df, index=False).values.tobytes()
    ).hexdigest()


def test_regression_step1_output_stability(baseline_checksums):
    """Test that Step 1 (1.1_CleanMetadata) output hasn't changed from baseline."""
    # Arrange
    output_file = Path("4_Outputs/1.1_CleanMetadata/latest/cleaned_metadata.parquet")

    if not output_file.exists():
        pytest.skip(f"Output file not found (run 1.1_CleanMetadata.py first)")

    # Act
    current_checksum = compute_file_checksum(output_file)
    expected_checksum = baseline_checksums.get("step1_cleaned_metadata")

    # Assert
    if expected_checksum is None:
        pytest.skip(
            "No baseline checksum for step1_cleaned_metadata (run with --update-baseline)"
        )

    assert current_checksum == expected_checksum, (
        f"Regression detected in Step 1 output!\n"
        f"File: {output_file}\n"
        f"Expected: {expected_checksum}\n"
        f"Got: {current_checksum}\n"
        f"Run with --update-baseline if this change is intentional"
    )
```

**Skipping Tests:**
```python
# Skip if data not available
if not config_path.exists():
    pytest.skip(f"Config file not found: {config_path}")

# Skip if baseline missing
if expected_checksum is None:
    pytest.skip(
        "No baseline checksum for step1_cleaned_metadata (run with --update-baseline)"
    )

# Skip if output not ready
if not output_file.exists():
    pytest.skip(f"Output file not found (run 1.1_CleanMetadata.py first)")
```

---

*Testing analysis: 2026-01-24*
