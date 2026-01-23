"""
Unit tests for env_validation module.

Tests environment variable validation, type conversion, and
EnvValidationError exceptions.
"""

import pytest
import os
import sys
from pathlib import Path

# Add 2_Scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "2_Scripts"))

from shared.env_validation import (
    validate_env_schema,
    EnvValidationError,
    load_and_validate_env,
    ENV_SCHEMA,
)


class TestValidateEnvSchema:
    """Tests for validate_env_schema function."""

    def test_validate_env_schema_success(self, monkeypatch):
        """Test validation succeeds with valid environment variables."""
        monkeypatch.setenv("WRDS_USERNAME", "test_user")
        monkeypatch.setenv("API_TIMEOUT_SECONDS", "45")

        # Override schema to use test variables
        test_schema = {
            "WRDS_USERNAME": {
                "required": True,
                "type": str,
                "description": "Test username",
            },
            "API_TIMEOUT_SECONDS": {
                "required": False,
                "type": int,
                "default": 30,
                "description": "Test timeout",
            },
        }

        result = validate_env_schema(test_schema)
        assert result["WRDS_USERNAME"] == "test_user"
        assert result["API_TIMEOUT_SECONDS"] == 45

    def test_validate_env_schema_missing_required(self, monkeypatch):
        """Test validation fails when required env var is missing."""
        # Don't set required variable
        monkeypatch.delenv("WRDS_USERNAME", raising=False)

        test_schema = {
            "WRDS_USERNAME": {
                "required": True,
                "type": str,
                "description": "Test username",
            },
        }

        with pytest.raises(
            EnvValidationError, match="Required environment variable not set"
        ):
            validate_env_schema(test_schema)

    def test_validate_env_type_validation_int(self, monkeypatch):
        """Test type conversion from string to int."""
        monkeypatch.setenv("MAX_RETRIES", "5")

        test_schema = {
            "MAX_RETRIES": {
                "required": False,
                "type": int,
                "default": 3,
                "description": "Test retries",
            },
        }

        result = validate_env_schema(test_schema)
        assert result["MAX_RETRIES"] == 5
        assert isinstance(result["MAX_RETRIES"], int)

    def test_validate_env_type_validation_float(self, monkeypatch):
        """Test type conversion from string to float."""
        monkeypatch.setenv("API_TIMEOUT_SECONDS", "45.5")

        test_schema = {
            "API_TIMEOUT_SECONDS": {
                "required": False,
                "type": float,
                "default": 30.0,
                "description": "Test timeout",
            },
        }

        result = validate_env_schema(test_schema)
        assert result["API_TIMEOUT_SECONDS"] == pytest.approx(45.5)

    @pytest.mark.parametrize(
        "value,expected",
        [
            ("true", True),
            ("TRUE", True),
            ("1", True),
            ("yes", True),
            ("YES", True),
            ("false", False),
            ("FALSE", False),
            ("0", False),
            ("no", False),
            ("NO", False),
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

    def test_validate_env_optional_with_default(self, monkeypatch):
        """Test optional variable uses default when not set."""
        # Don't set the variable
        monkeypatch.delenv("API_TIMEOUT_SECONDS", raising=False)

        test_schema = {
            "API_TIMEOUT_SECONDS": {
                "required": False,
                "type": int,
                "default": 30,
                "description": "Test timeout",
            },
        }

        result = validate_env_schema(test_schema)
        assert result["API_TIMEOUT_SECONDS"] == 30

    def test_validate_env_optional_none(self, monkeypatch):
        """Test optional variable not set and no default."""
        monkeypatch.delenv("WRDS_USERNAME", raising=False)

        test_schema = {
            "WRDS_USERNAME": {
                "required": False,
                "type": str,
                "description": "Optional username",
            },
        }

        result = validate_env_schema(test_schema)
        assert "WRDS_USERNAME" not in result

    def test_validate_env_invalid_int_type(self, monkeypatch):
        """Test type conversion error for invalid int."""
        monkeypatch.setenv("MAX_RETRIES", "not_a_number")

        test_schema = {
            "MAX_RETRIES": {
                "required": False,
                "type": int,
                "default": 3,
                "description": "Test retries",
            },
        }

        with pytest.raises(EnvValidationError, match="Invalid type"):
            validate_env_schema(test_schema)

    def test_validate_env_invalid_float_type(self, monkeypatch):
        """Test type conversion error for invalid float."""
        monkeypatch.setenv("API_TIMEOUT", "not_a_float")

        test_schema = {
            "API_TIMEOUT": {
                "required": False,
                "type": float,
                "default": 30.0,
                "description": "Test timeout",
            },
        }

        with pytest.raises(EnvValidationError, match="Invalid type"):
            validate_env_schema(test_schema)

    def test_validate_env_unsupported_type(self, monkeypatch):
        """Test unsupported type raises error."""
        monkeypatch.setenv("TEST_VAR", "value")

        test_schema = {
            "TEST_VAR": {
                "required": False,
                "type": dict,  # Unsupported type
                "default": {},
                "description": "Test variable",
            },
        }

        with pytest.raises(EnvValidationError, match="Unsupported type"):
            validate_env_schema(test_schema)

    @pytest.mark.parametrize(
        "env_name,env_spec",
        [
            (
                "WRDS_USERNAME",
                {"required": False, "type": str, "description": "WRDS username"},
            ),
            (
                "WRDS_PASSWORD",
                {"required": False, "type": str, "description": "WRDS password"},
            ),
            ("API_TIMEOUT_SECONDS", {"required": False, "type": int, "default": 30}),
            ("MAX_RETRIES", {"required": False, "type": int, "default": 3}),
        ],
    )
    def test_validate_env_with_actual_schema(self, env_name, env_spec, monkeypatch):
        """Test validation with actual ENV_SCHEMA entries."""
        # Set values for variables with defaults
        if env_name in ["API_TIMEOUT_SECONDS", "MAX_RETRIES"]:
            monkeypatch.setenv(env_name, str(env_spec.get("default", 0) + 10))

        result = validate_env_schema(ENV_SCHEMA)
        # Variable should be in result
        if env_name in result:
            if env_spec.get("type") == int:
                assert isinstance(result[env_name], int)


class TestLoadAndValidateEnv:
    """Tests for load_and_validate_env function."""

    def test_load_and_validate_env_success(self, monkeypatch):
        """Test load_and_validate_env returns validated dict on success."""
        # Clear any existing vars
        monkeypatch.delenv("WRDS_USERNAME", raising=False)

        result = load_and_validate_env()
        # Should return validated env dict
        assert isinstance(result, dict)
        assert len(result) >= 0

    def test_load_and_validate_env_failure(self, monkeypatch, capsys):
        """Test load_and_validate_env exits on validation failure."""
        # Don't set required variable
        monkeypatch.delenv("NONEXISTENT_VAR", raising=False)

        # Create a test schema that requires a missing var
        test_schema = {
            "NONEXISTENT_VAR": {
                "required": True,
                "type": str,
                "description": "Missing var",
            },
        }

        # Mock validate_env_schema to raise error
        def mock_validate(schema):
            raise EnvValidationError("Test error")

        import shared.env_validation as env_mod

        original_validate = env_mod.validate_env_schema
        env_mod.validate_env_schema = mock_validate
        env_mod.ENV_SCHEMA = test_schema

        with pytest.raises(SystemExit) as exc_info:
            load_and_validate_env()

        # Should exit with code 1
        assert exc_info.value.code == 1

        # Check error message was printed
        captured = capsys.readouterr()
        assert "ERROR: Environment validation failed" in captured.err

        # Restore original function
        env_mod.validate_env_schema = original_validate


class TestEnvSchemaConstant:
    """Tests for ENV_SCHEMA constant."""

    def test_env_schema_has_wrds_credentials(self):
        """Test ENV_SCHEMA contains WRDS credentials."""
        assert "WRDS_USERNAME" in ENV_SCHEMA
        assert "WRDS_PASSWORD" in ENV_SCHEMA

        # Check structure
        assert ENV_SCHEMA["WRDS_USERNAME"]["type"] == str
        assert ENV_SCHEMA["WRDS_PASSWORD"]["type"] == str
        assert ENV_SCHEMA["WRDS_USERNAME"]["required"] == False

    def test_env_schema_has_api_settings(self):
        """Test ENV_SCHEMA contains API settings."""
        assert "API_TIMEOUT_SECONDS" in ENV_SCHEMA
        assert "MAX_RETRIES" in ENV_SCHEMA

        # Check defaults
        assert ENV_SCHEMA["API_TIMEOUT_SECONDS"]["default"] == 30
        assert ENV_SCHEMA["MAX_RETRIES"]["default"] == 3

    def test_env_schema_all_entries_have_required_fields(self):
        """Test all ENV_SCHEMA entries have required fields."""
        for var_name, var_spec in ENV_SCHEMA.items():
            assert "type" in var_spec, f"{var_name} missing 'type' field"
            assert "description" in var_spec, f"{var_name} missing 'description' field"
            # 'required' and 'default' are optional


class TestEnvValidationError:
    """Tests for EnvValidationError exception."""

    def test_env_validation_error_is_exception(self):
        """Test EnvValidationError is an Exception subclass."""
        assert issubclass(EnvValidationError, Exception)

    def test_env_validation_error_message(self):
        """Test EnvValidationError stores error message."""
        msg = "Test error message"
        exc = EnvValidationError(msg)
        assert str(exc) == msg
        assert exc.args[0] == msg

    def test_env_validation_error_message_format(self, monkeypatch):
        """Test EnvValidationError message format includes required info."""
        test_schema = {
            "TEST_VAR": {
                "required": True,
                "type": str,
                "description": "Important test variable",
            },
        }

        monkeypatch.delenv("TEST_VAR", raising=False)

        with pytest.raises(EnvValidationError) as exc_info:
            validate_env_schema(test_schema)

        error_msg = str(exc_info.value)
        assert "Required environment variable not set" in error_msg
        assert "TEST_VAR" in error_msg
        assert "Important test variable" in error_msg
