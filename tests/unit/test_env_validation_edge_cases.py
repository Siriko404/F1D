"""Edge case tests for env_validation module."""
import pytest

try:
    from 2_Scripts.shared.env_validation import (
        validate_env_schema,
        EnvValidationError,
    )
    ENV_VALIDATION_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    ENV_VALIDATION_AVAILABLE = False
    pytest.skip("env_validation module not available", allow_module_level=True)


@pytest.mark.skipif(not ENV_VALIDATION_AVAILABLE, reason="env_validation module not available")
def test_validate_env_schema_empty_string(monkeypatch):
    """Test environment validation handles empty string values."""
    monkeypatch.setenv("TEST_VAR", "")
    schema = {"TEST_VAR": {"required": False, "type": str}}
    validated = validate_env_schema(schema)
    assert validated["TEST_VAR"] == ""
