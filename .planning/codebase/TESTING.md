# Testing Patterns

**Analysis Date:** 2025-02-10

## Test Framework

**Runner:**
- pytest (version 8.0+ from `pyproject.toml`)
- Config: `pyproject.toml` with `[tool.pytest.ini_options]`

**Assertion Library:**
- pytest's built-in `assert` statement
- `pytest.raises()` for exception testing
- `pytest.approx()` for float comparison

**Run Commands:**
```bash
# Run all tests
pytest

# Verbose mode
pytest -v

# Run specific test file
pytest tests/unit/test_data_validation.py

# Run with markers
pytest -m unit
pytest -m integration
pytest -m "not slow"

# Coverage
pytest --cov=2_Scripts
```

## Test File Organization

**Location:**
- Tests are in separate `tests/` directory (not co-located)
- Structure mirrors `2_Scripts/` organization
- `tests/unit/` for unit tests
- `tests/integration/` for integration tests
- `tests/fixtures/` for test data
- `tests/conftest.py` for shared fixtures

**Naming:**
- Unit tests: `test_<module>.py` (e.g., `test_data_validation.py`)
- Edge case tests: `test_<module>_edge_cases.py` (e.g., `test_data_validation_edge_cases.py`)
- Integration tests: `test_<feature>_integration.py`

**Structure:**
```
tests/
├── conftest.py                    # Shared fixtures
├── fixtures/                      # Test data files
│   └── sample_yaml/               # Sample configs
├── unit/
│   ├── test_data_validation.py
│   ├── test_data_validation_edge_cases.py
│   ├── test_env_validation.py
│   ├── test_env_validation_edge_cases.py
│   ├── test_fuzzy_matching.py
│   ├── test_observability_helpers.py
│   ├── test_regression_helpers.py
│   ├── test_subprocess_validation.py
│   └── test_subprocess_validation_edge_cases.py
└── integration/
    └── test_observability_integration.py
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
```

**Patterns:**

1. **Class-based organization:**
   - One test class per function being tested: `class TestValidateDataFrameSchema`
   - Descriptive class names: `Test<FunctionName>`

2. **Test method naming:**
   - `test_<function>_<scenario>()`
   - Descriptive: `test_validate_dataframe_schema_missing_columns_with_real_schema`

3. **Setup pattern:**
   - Use fixtures from `conftest.py` for shared test data
   - Path manipulation in each test file for imports
   - `sys.path.insert(0, ...)` to add `2_Scripts` to Python path

4. **Teardown pattern:**
   - `tmp_path` fixture for temporary files (auto-cleanup)
   - `monkeypatch` fixture for env var cleanup
   - No explicit teardown needed - pytest handles it

5. **Assertion pattern:**
   - Use `pytest.raises(Exception, match="pattern")` for exceptions
   - Direct `assert` for simple checks
   - `pytest.approx()` for float comparisons

## Mocking

**Framework:** pytest's built-in fixtures (`monkeypatch`, `capfd`, `capsys`)

**Patterns:**

```python
# Environment variable mocking
def test_validate_env_schema_success(self, monkeypatch):
    """Test validation succeeds with valid environment variables."""
    monkeypatch.setenv("WRDS_USERNAME", "test_user")
    monkeypatch.setenv("API_TIMEOUT_SECONDS", "45")
    # Test code...

def test_validate_env_schema_missing_required(self, monkeypatch):
    """Test validation fails when required env var is missing."""
    monkeypatch.delenv("WRDS_USERNAME", raising=False)
    # Test code...

# Capturing output
def test_load_validated_parquet_strict_mode_false(self, tmp_path, capsys):
    """Load Parquet file with validation errors in non-strict mode."""
    # Test code...
    captured = capsys.readouterr()
    assert "WARNING:" in captured.err

# Mocking module functions
def test_load_and_validate_env_failure(self, monkeypatch, capsys):
    """Test load_and_validate_env exits on validation failure."""
    def mock_validate(schema):
        raise EnvValidationError("Test error")

    import shared.env_validation as env_mod
    original_validate = env_mod.validate_env_schema
    env_mod.validate_env_schema = mock_validate

    with pytest.raises(SystemExit) as exc_info:
        load_and_validate_env()

    assert exc_info.value.code == 1
    env_mod.validate_env_schema = original_validate  # Restore
```

**What to Mock:**
- Environment variables: use `monkeypatch.setenv/delenv`
- Module functions: replace temporarily, then restore
- File I/O: use `tmp_path` fixture for real temporary files

**What NOT to Mock:**
- Don't mock pandas operations - use real DataFrames
- Don't mock data validation logic - test the real implementation
- Don't mock `DualWriter` - use `capsys` to capture output

## Fixtures and Factories

**Test Data:**

```python
# In conftest.py
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
    }
    config_path = tmp_path / "project.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config_data, f)
    return config_path
```

**Location:**
- `tests/conftest.py` for globally shared fixtures
- Test files can have local fixtures too
- `tests/fixtures/` directory for static test data files (YAML, etc.)

## Coverage

**Requirements:** No explicit coverage target configured

**View Coverage:**
```bash
pytest --cov=2_Scripts --cov-report=html
```

**Configuration in `pyproject.toml`:**
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
- Scope: Test individual functions in isolation
- Location: `tests/unit/`
- Focus: `shared/` module functions, validation logic
- No external dependencies (no file system, network, subprocess)

**Integration Tests:**
- Scope: Test features work end-to-end across scripts
- Location: `tests/integration/`
- Focus: Observability features, subprocess execution
- Use subprocess to run scripts and verify output

**E2E Tests:**
- Framework: Not used (no playwright/selenium/etc.)
- Full pipeline tests run via scripts manually

## Common Patterns

**Async Testing:**
- Not applicable (synchronous codebase)

**Error Testing:**

```python
# Test exceptions with pytest.raises
def test_data_validation_error_is_exception(self):
    """Test DataValidationError is an Exception subclass."""
    assert issubclass(DataValidationError, Exception)

def test_data_validation_error_message(self):
    """Test DataValidationError stores error message."""
    msg = "Test error message"
    exc = DataValidationError(msg)
    assert str(exc) == msg
    assert exc.args[0] == msg

def test_validate_dataframe_schema_value_range_violation_with_real_schema(
    self, sample_parquet_file_with_schema
):
    """Test schema validation fails for values outside range using actual schema."""
    df = pd.DataFrame({"event_type": [1, 5, 15]})  # 15 is > 10
    with pytest.raises(DataValidationError, match="above max"):
        validate_dataframe_schema(
            df, "Unified-info.parquet", sample_parquet_file_with_schema
        )
```

**Parametrized Tests:**

```python
@pytest.mark.parametrize(
    "value,expected",
    [
        ("true", True),
        ("TRUE", True),
        ("1", True),
        ("yes", True),
        ("false", False),
        ("0", False),
        ("no", False),
    ],
)
def test_validate_env_type_validation_bool(self, value, expected, monkeypatch):
    """Test type conversion from string to bool."""
    monkeypatch.setenv("ENABLE_FEATURE", value)
    test_schema = {
        "ENABLE_FEATURE": {
            "required": False,
            "type": bool,
            "default": False,
            "description": "Test flag",
        },
    }
    result = validate_env_schema(test_schema)
    assert result["ENABLE_FEATURE"] == expected
```

**Missing Value Testing:**

```python
def test_missing_values_in_some_columns(self):
    """Test with missing values in some columns."""
    df = pd.DataFrame(
        {
            "y": [1, None, 3],
            "x1": [4, 5, 6],
            "c1": [7, 8, None],
        }
    )

    required_vars = {
        "dependent": ["y"],
        "independent": ["x1"],
        "controls": ["c1"],
    }

    result = _check_missing_values(df, required_vars)

    assert "y" in result
    assert result["y"] == 1
    assert "c1" in result
    assert result["c1"] == 1
    assert "x1" not in result
```

---

*Testing analysis: 2025-02-10*
