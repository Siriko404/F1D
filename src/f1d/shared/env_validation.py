#!/usr/bin/env python3
"""
================================================================================
SHARED MODULE: Environment Variable Validation
================================================================================
ID: shared/env_validation
Description: Schema-based validation for environment variables.

Purpose: Validates environment variables against defined schema.

Security:
    - Validates environment variables against defined schema
    - Applies defaults for optional variables
    - Raises clear errors on validation failures

Inputs:
    - Environment variable names and schemas

Outputs:
    - Validated environment variables

Main Functions:
    - validate_env_vars(): Validate environment variables

Dependencies:
    - Utility module for environment validation
    - Uses: os, sys

Author: Thesis Author
Date: 2026-02-11
================================================================================
"""

import os
import sys
from typing import Any, Dict

# Define environment variable schema
ENV_SCHEMA = {
    "API_TIMEOUT_SECONDS": {
        "required": False,
        "type": int,
        "default": 30,
        "description": "API request timeout in seconds",
    },
    "MAX_RETRIES": {
        "required": False,
        "type": int,
        "default": 3,
        "description": "Maximum retry attempts for failed requests",
    },
}


class EnvValidationError(Exception):
    """Raised when environment validation fails."""

    pass


def validate_env_schema(schema: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate environment variables against schema.

    Args:
        schema: Dictionary defining expected env vars

    Returns:
        dict: Validated env var values (with defaults applied)

    Raises:
        EnvValidationError: If required vars missing or type validation fails
    """
    validated: Dict[str, Any] = {}

    for var_name, var_spec in schema.items():
        raw_value = os.environ.get(var_name, var_spec.get("default"))
        value: Any = raw_value

        # Check required vars
        if var_spec.get("required", True) and value is None:
            raise EnvValidationError(
                f"Required environment variable not set: {var_name}\n"
                f"  Description: {var_spec.get('description')}"
            )

        # Skip type check if None (for optional vars)
        if value is None:
            continue

        # Type validation
        expected_type = var_spec["type"]
        try:
            if expected_type == int:
                value = int(value)
            elif expected_type == float:
                value = float(value)
            elif expected_type == bool:
                value = str(value).lower() in ("true", "1", "yes")
            elif expected_type == str:
                value = str(value)
            else:
                raise EnvValidationError(f"Unsupported type: {expected_type}")
        except (ValueError, TypeError) as e:
            raise EnvValidationError(
                f"Invalid type for {var_name}: expected {expected_type.__name__}, got {value}\n"
                f"  Error: {e}"
            )

        validated[var_name] = value

    return validated


def load_and_validate_env() -> Dict[str, Any]:
    """
    Load and validate environment variables.

    Returns validated env dict or exits on failure.

    This is the entry point for environment validation.
    Call this at script startup if using environment variables.
    """
    try:
        env = validate_env_schema(ENV_SCHEMA)
        print(f"Environment validated: {len(env)} variables")
        return env
    except EnvValidationError as e:
        print(f"ERROR: Environment validation failed: {e}", file=sys.stderr)
        sys.exit(1)
