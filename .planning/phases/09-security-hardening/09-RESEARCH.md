# Phase 9: Security Hardening - Research

**Researched:** 2026-01-23
**Domain:** Security validation, subprocess hardening, input validation
**Confidence:** HIGH

## Summary

This phase addresses three security concerns in the data processing pipeline:

1. **Subprocess Execution Without Validation** - Orchestrator scripts use `subprocess.run()` with paths derived from configuration, which could potentially execute arbitrary code if paths are tampered with or if configuration contains malicious entries.

2. **No Environment Variable Validation** - While the current codebase doesn't use environment variables or `.env` files, adding them in the future (e.g., for WRDS credentials, API keys) would introduce security risks if not validated properly.

3. **Missing Input Data Validation** - Scripts read Parquet/CSV files from `1_Inputs/` without validating schemas, column types, or value ranges. Malicious or corrupted input files could cause unexpected behavior, data corruption, or crashes.

**Primary recommendation:** Add validation layers at three points in the pipeline:
1. Subprocess path validation before executing any script
2. Environment variable schema validation (for future use)
3. Input data schema validation with column type and range checks

## Standard Stack

This phase uses Python's standard library and common validation patterns - no additional third-party packages required.

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pathlib | Built-in | Path validation, absolute paths | Secure path manipulation |
| subprocess | Built-in | Safe subprocess execution | Already in use, add validation |
| os | Built-in | Path security checks | `os.path.abspath()`, `os.path.realpath()` |
| sys | Built-in | Exit codes, error reporting | Standard process control |
| pandas | Existing | Schema validation for input data | Already using, extend with validation |
| pydantic (optional) | 2.x | Schema validation (if needed) | Type-safe validation with Python 3.8+ |

**Installation:**
```bash
# Using existing stack - no new dependencies required
# Optional: pydantic for richer schema validation
pip install pydantic
```

## Architecture Patterns

### Pattern 1: Subprocess Path Validation

**What:** Validate that any script path passed to `subprocess.run()` is within the expected directory structure and is an absolute path.

**When to use:** For all orchestrator scripts that execute other scripts dynamically.

**Why this works:** Prevents path traversal attacks and ensures only intended scripts can be executed.

**Example:**

```python
# Source: https://docs.python.org/3/library/subprocess.html
# Source: https://docs.python.org/3/library/pathlib.html
# Source: https://cwe.mitre.org/data/definitions/427.html (CWE-427: Uncontrolled Search Path Element)

import subprocess
import sys
from pathlib import Path

def validate_script_path(script_path: Path, allowed_dir: Path) -> Path:
    """
    Validate that script_path is within allowed_dir and is an absolute path.

    Raises:
        ValueError: If path is outside allowed directory or not absolute
        FileNotFoundError: If script doesn't exist

    Returns:
        Path: Absolute, validated script path
    """
    # Convert to absolute path
    script_path = Path(script_path).resolve()
    allowed_dir = allowed_dir.resolve()

    # Check if script exists
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")

    # Check if path is within allowed directory
    try:
        script_path.relative_to(allowed_dir)
    except ValueError:
        raise ValueError(
            f"Script path outside allowed directory:\n"
            f"  Script: {script_path}\n"
            f"  Allowed: {allowed_dir}"
        )

    # Check file extension is .py
    if script_path.suffix != '.py':
        raise ValueError(f"Script must be .py file: {script_path}")

    return script_path


def run_validated_script(script_path: Path, allowed_dir: Path) -> subprocess.CompletedProcess:
    """
    Run a script with validated path.

    Returns subprocess result or raises validation errors.
    """
    # Validate path before execution
    validated_path = validate_script_path(script_path, allowed_dir)

    # Execute with validated absolute path
    result = subprocess.run(
        [sys.executable, str(validated_path)],
        capture_output=True,
        text=True,
        check=False  # Handle returncode manually
    )

    return result
```

```python
# In 2_Scripts/1_Sample/1.0_BuildSampleManifest.py
from pathlib import Path

# Define allowed directories (scripts should be within 2_Scripts/)
ALLOWED_SCRIPT_DIR = Path(__file__).parent  # 2_Scripts/

# When executing subscripts:
for step in pipeline_steps:
    script_path = Path(__file__).parent / step['script']

    # Validate before execution
    try:
        script_path = validate_script_path(script_path, ALLOWED_SCRIPT_DIR)
    except (ValueError, FileNotFoundError) as e:
        print_dual(f"ERROR: Script validation failed: {e}")
        success = False
        break

    # Execute validated script
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True
    )
```

### Pattern 2: Environment Variable Schema Validation (Future-Ready)

**What:** Create a schema definition for environment variables and validate them on startup.

**When to use:** When adding `.env` support for WRDS credentials, API keys, or other sensitive configuration.

**Why this works:** Prevents typos, ensures required values are present, validates types early.

**Example:**

```python
# Source: https://docs.python.org/3/library/os.html#os.environ
# Source: https://pydantic-docs.helpmanual.io/ (optional pattern)

import os
import sys
from typing import Optional, List
from pathlib import Path

# Schema definition for environment variables
ENV_SCHEMA = {
    "WRDS_USERNAME": {
        "required": False,  # Optional for now - using WRDS via different method
        "type": str,
        "description": "WRDS username for data access",
    },
    "WRDS_PASSWORD": {
        "required": False,
        "type": str,
        "description": "WRDS password (WARNING: Should not be in .env)",
    },
    "API_TIMEOUT_SECONDS": {
        "required": False,
        "type": int,
        "description": "API request timeout in seconds",
        "default": 30,
    },
    "MAX_RETRIES": {
        "required": False,
        "type": int,
        "description": "Maximum retry attempts for failed requests",
        "default": 3,
    },
}


class EnvValidationError(Exception):
    """Raised when environment validation fails."""
    pass


def validate_env_schema(schema: dict) -> dict:
    """
    Validate environment variables against schema.

    Args:
        schema: Dictionary defining expected env vars

    Returns:
        dict: Validated env var values (with defaults applied)

    Raises:
        EnvValidationError: If required vars missing or type validation fails
    """
    validated = {}

    for var_name, var_spec in schema.items():
        value = os.environ.get(var_name, var_spec.get("default"))

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
                value = value.lower() in ("true", "1", "yes")
            elif expected_type == str:
                value = str(value)
            elif expected_type == Path:
                value = Path(value)
            else:
                raise EnvValidationError(f"Unsupported type: {expected_type}")
        except (ValueError, TypeError) as e:
            raise EnvValidationError(
                f"Invalid type for {var_name}: expected {expected_type.__name__}, got {value}\n"
                f"  Error: {e}"
            )

        validated[var_name] = value

    return validated


def load_and_validate_env() -> dict:
    """
    Load and validate environment variables.

    Returns validated env dict or raises EnvValidationError.
    """
    try:
        env = validate_env_schema(ENV_SCHEMA)
        print(f"Environment validated: {len(env)} variables")
        return env
    except EnvValidationError as e:
        print(f"ERROR: Environment validation failed: {e}", file=sys.stderr)
        sys.exit(1)
```

```python
# At startup of any script (if .env support is added)
# from 2_Scripts/shared/env_validation import load_and_validate_env

# Validate environment
ENV = load_and_validate_env()
```

### Pattern 3: Input Data Schema Validation

**What:** Validate input files against expected schemas including column names, types, and value ranges.

**When to use:** For all scripts that read data from `1_Inputs/`.

**Why this works:** Catches corrupted or malicious input files early, provides clear error messages, documents expected data structure.

**Example:**

```python
# Source: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.dtypes.html
# Source: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.isin.html

import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys

# Schema definitions for key input files
INPUT_SCHEMAS = {
    "Unified-info.parquet": {
        "required_columns": [
            "event_type",
            "file_name",
            "date",
            "speakers",
            # Add all required columns
        ],
        "column_types": {
            "event_type": "int64",  # or int32
            "date": "object",  # or datetime64
            "speakers": "object",
        },
        "value_ranges": {
            "event_type": {"min": 0, "max": 10},  # Assuming event_type is 0-10
        },
    },
    "Loughran-McDonald_MasterDictionary_1993-2024.csv": {
        "required_columns": ["word", "negative", "positive", "uncertainty", "litigious"],
        "column_types": {
            "word": "object",
            "negative": "int64",
            "positive": "int64",
        },
    },
    # Add schemas for other input files
}


class DataValidationError(Exception):
    """Raised when input data validation fails."""
    pass


def validate_dataframe_schema(
    df: pd.DataFrame,
    schema_name: str,
    file_path: Path,
    strict: bool = True
) -> None:
    """
    Validate DataFrame against expected schema.

    Args:
        df: DataFrame to validate
        schema_name: Name of schema to use (key in INPUT_SCHEMAS)
        file_path: Path to source file (for error messages)
        strict: If True, raise on validation failure; if False, warn and continue

    Raises:
        DataValidationError: If validation fails and strict=True
    """
    if schema_name not in INPUT_SCHEMAS:
        print(f"WARNING: No schema defined for {schema_name}, skipping validation")
        return

    schema = INPUT_SCHEMAS[schema_name]
    errors = []

    # Check required columns
    required = schema.get("required_columns", [])
    missing = [col for col in required if col not in df.columns]
    if missing:
        errors.append(f"Missing columns: {missing}")

    # Check column types
    for col, expected_type in schema.get("column_types", {}).items():
        if col not in df.columns:
            continue
        actual_type = str(df[col].dtype)
        if not actual_type.startswith(expected_type):
            errors.append(
                f"Column '{col}' has wrong type: expected {expected_type}, got {actual_type}"
            )

    # Check value ranges
    for col, range_spec in schema.get("value_ranges", {}).items():
        if col not in df.columns:
            continue

        min_val = range_spec.get("min")
        max_val = range_spec.get("max")

        if min_val is not None and (df[col] < min_val).any():
            count = (df[col] < min_val).sum()
            errors.append(
                f"Column '{col}' has {count} values below min ({min_val})"
            )

        if max_val is not None and (df[col] > max_val).any():
            count = (df[col] > max_val).sum()
            errors.append(
                f"Column '{col}' has {count} values above max ({max_val})"
            )

    # Report errors
    if errors:
        error_msg = (
            f"Data validation failed for {file_path.name}:\n"
            f"  File: {file_path}\n"
            f"  Errors:\n    - " + "\n    - ".join(errors)
        )

        if strict:
            raise DataValidationError(error_msg)
        else:
            print(f"WARNING: {error_msg}", file=sys.stderr)
    else:
        print(f"Validation passed for {file_path.name}")


def load_validated_parquet(
    file_path: Path,
    schema_name: Optional[str] = None,
    strict: bool = True
) -> pd.DataFrame:
    """
    Load Parquet file with schema validation.

    Args:
        file_path: Path to Parquet file
        schema_name: Name of schema to validate against
        strict: If True, raise on validation failure

    Returns:
        pd.DataFrame: Validated DataFrame

    Raises:
        DataValidationError: If validation fails and strict=True
    """
    # Load file
    df = pd.read_parquet(file_path)

    # Validate schema
    if schema_name:
        validate_dataframe_schema(df, schema_name, file_path, strict=strict)

    return df
```

```python
# In scripts that read input files
from pathlib import Path

# Example: 1.1_CleanMetadata.py
input_file = Path("1_Inputs/Unified-info.parquet")

# Load with validation
df = load_validated_parquet(input_file, schema_name="Unified-info.parquet", strict=True)
```

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Path traversal validation | Custom string parsing | `Path.resolve()` + `.relative_to()` | Handles symlinks, `..`, canonical paths correctly |
| Schema validation | Manual type checking | Pydantic (optional) or pandas type checking | Well-tested, clear error messages, supports complex types |
| Environment loading | `os.getenv()` everywhere | Centralized schema validation | Single source of truth, easier to maintain |
| Data validation | Custom column checks | pandas dtypes + custom range checks | Already using pandas, extend with validation |

**Key insight:** Python's pathlib provides secure path manipulation that handles edge cases correctly. Schema validation doesn't require heavy libraries - can be done with pandas types and simple checks.

## Common Pitfalls

### Pitfall 1: Insufficient Path Validation

**What goes wrong:** Only checking that a path ends with `.py` or that it exists, without verifying it's within allowed directories.

**Why it happens:** Oversimplifying path validation, not understanding path traversal attacks (e.g., `../../malicious.py`).

**How to avoid:** Always resolve to absolute paths first, then use `relative_to()` to check containment within allowed directory.

```python
# BAD - only checks file exists
if script_path.exists() and script_path.suffix == '.py':
    subprocess.run([sys.executable, str(script_path)])  # Vulnerable!

# GOOD - validates containment
script_path = script_path.resolve()
script_path.relative_to(allowed_dir)  # Raises ValueError if outside allowed dir
subprocess.run([sys.executable, str(script_path)])
```

### Pitfall 2: Overly Strict Validation Breaking Legitimate Workflows

**What goes wrong:** Validation rules are too strict, rejecting valid data or paths that users legitimately need.

**Why it happens:** Schema is defined too rigidly without understanding data variability.

**How to avoid:** Use `strict=False` for non-critical validation, log warnings instead of raising errors, make schemas configurable.

### Pitfall 3: Not Validating on First Load

**What goes wrong:** Adding validation only after experiencing issues, not proactively at data load time.

**Why it happens:** "It works now, why add overhead?" mindset.

**How to avoid:** Validate immediately when reading files. Early detection prevents silent corruption later.

### Pitfall 4: Environment Variables in Plaintext

**What goes wrong:** Storing sensitive credentials (WRDS password, API keys) in `.env` files without encryption or proper access controls.

**Why it happens:** Convenience over security, not understanding that `.env` files can leak (committed to git, logged in CI).

**How to avoid:**
- Never store passwords in `.env` - use keyring or secure credential manager
- If using `.env`, add to `.gitignore`
- Document that `.env` contains sensitive data

## Code Examples

Verified patterns from official sources:

### Subprocess Validation

```python
# Source: 2_Scripts/1_Sample/1.0_BuildSampleManifest.py (line 164-169)
# Location: 2_Scripts/shared/subprocess_validation.py (new file)

import subprocess
import sys
from pathlib import Path
from typing import Optional

def validate_script_path(script_path: Path, allowed_dir: Path) -> Path:
    """
    Validate script path is within allowed directory.

    Security: Prevents path traversal attacks (CWE-427).
    """
    # Resolve to absolute path (handles symlinks, .., .)
    script_path = Path(script_path).resolve()
    allowed_dir = allowed_dir.resolve()

    # Check existence
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")

    # Check containment within allowed directory
    try:
        script_path.relative_to(allowed_dir)
    except ValueError:
        raise ValueError(
            f"Script path outside allowed directory:\n"
            f"  Script: {script_path}\n"
            f"  Allowed: {allowed_dir}"
        )

    # Check extension
    if script_path.suffix != '.py':
        raise ValueError(f"Script must be .py file: {script_path}")

    return script_path


def run_validated_subprocess(
    script_path: Path,
    allowed_dir: Path,
    capture_output: bool = True,
    check: bool = False
) -> subprocess.CompletedProcess:
    """
    Run script with validated path.

    Args:
        script_path: Path to script (can be relative)
        allowed_dir: Directory script must be within
        capture_output: Capture stdout/stderr
        check: Raise exception on non-zero exit

    Returns:
        subprocess.CompletedProcess
    """
    # Validate before execution
    validated_path = validate_script_path(script_path, allowed_dir)

    # Execute
    result = subprocess.run(
        [sys.executable, str(validated_path)],
        capture_output=capture_output,
        text=True,
        check=check
    )

    return result
```

### Environment Schema Validation

```python
# Source: CONCERNS.md (SEC-02)
# Location: 2_Scripts/shared/env_validation.py (new file)

import os
import sys
from typing import Dict, Any, Optional

# Define environment variable schema
ENV_SCHEMA = {
    "WRDS_USERNAME": {
        "required": False,
        "type": str,
        "description": "WRDS username",
    },
    "WRDS_PASSWORD": {
        "required": False,
        "type": str,
        "description": "WRDS password (use keyring instead)",
    },
    "API_TIMEOUT_SECONDS": {
        "required": False,
        "type": int,
        "default": 30,
    },
    "MAX_RETRIES": {
        "required": False,
        "type": int,
        "default": 3,
    },
}


class EnvValidationError(Exception):
    """Environment validation failed."""
    pass


def validate_env_schema(schema: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate environment variables against schema.

    Returns validated dict with defaults applied.
    """
    validated = {}

    for var_name, var_spec in schema.items():
        value = os.environ.get(var_name, var_spec.get("default"))

        # Required check
        if var_spec.get("required", True) and value is None:
            raise EnvValidationError(
                f"Required environment variable not set: {var_name}\n"
                f"  Description: {var_spec.get('description')}"
            )

        # Skip type check for None (optional vars)
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
                value = value.lower() in ("true", "1", "yes")
            elif expected_type == str:
                value = str(value)
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
    """
    try:
        env = validate_env_schema(ENV_SCHEMA)
        print(f"Environment validated: {len(env)} variables")
        return env
    except EnvValidationError as e:
        print(f"ERROR: Environment validation failed: {e}", file=sys.stderr)
        sys.exit(1)
```

### Input Data Validation

```python
# Source: CONCERNS.md (SEC-03)
# Location: 2_Scripts/shared/data_validation.py (new file)

import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional
import sys

# Schemas for key input files
INPUT_SCHEMAS = {
    "Unified-info.parquet": {
        "required_columns": [
            "event_type",
            "file_name",
            "date",
            "speakers",
        ],
        "column_types": {
            "event_type": "int",
            "date": "object",  # String date representation
            "speakers": "object",
        },
        "value_ranges": {
            "event_type": {"min": 0, "max": 10},
        },
    },
    "Loughran-McDonald_MasterDictionary_1993-2024.csv": {
        "required_columns": ["word", "negative", "positive", "uncertainty", "litigious"],
        "column_types": {
            "word": "object",
            "negative": "int",
            "positive": "int",
            "uncertainty": "int",
            "litigious": "int",
        },
    },
}


class DataValidationError(Exception):
    """Data validation failed."""
    pass


def validate_dataframe_schema(
    df: pd.DataFrame,
    schema_name: str,
    file_path: Path,
    strict: bool = True
) -> None:
    """
    Validate DataFrame against schema.

    Raises DataValidationError if strict=True and validation fails.
    Logs warning if strict=False.
    """
    if schema_name not in INPUT_SCHEMAS:
        print(f"WARNING: No schema for {schema_name}, skipping validation")
        return

    schema = INPUT_SCHEMAS[schema_name]
    errors = []

    # Check required columns
    required = schema.get("required_columns", [])
    missing = [col for col in required if col not in df.columns]
    if missing:
        errors.append(f"Missing columns: {missing}")

    # Check column types
    for col, expected_type in schema.get("column_types", {}).items():
        if col not in df.columns:
            continue
        actual_type = str(df[col].dtype)
        if not actual_type.startswith(expected_type):
            errors.append(
                f"Column '{col}': expected {expected_type}, got {actual_type}"
            )

    # Check value ranges
    for col, range_spec in schema.get("value_ranges", {}).items():
        if col not in df.columns:
            continue

        min_val = range_spec.get("min")
        max_val = range_spec.get("max")

        if min_val is not None and (df[col] < min_val).any():
            count = (df[col] < min_val).sum()
            errors.append(
                f"Column '{col}': {count} values below min ({min_val})"
            )

        if max_val is not None and (df[col] > max_val).any():
            count = (df[col] > max_val).sum()
            errors.append(
                f"Column '{col}': {count} values above max ({max_val})"
            )

    # Report
    if errors:
        error_msg = (
            f"Validation failed for {file_path.name}:\n"
            f"  File: {file_path}\n"
            f"  Errors:\n    - " + "\n    - ".join(errors)
        )

        if strict:
            raise DataValidationError(error_msg)
        else:
            print(f"WARNING: {error_msg}", file=sys.stderr)
    else:
        print(f"Validation passed: {file_path.name}")


def load_validated_parquet(
    file_path: Path,
    schema_name: Optional[str] = None,
    strict: bool = True
) -> pd.DataFrame:
    """
    Load Parquet file with schema validation.

    Returns validated DataFrame or raises DataValidationError.
    """
    df = pd.read_parquet(file_path)

    if schema_name:
        validate_dataframe_schema(df, schema_name, file_path, strict=strict)

    return df
```

## State of the Art

| Old Approach | New Approach | When Changed | Impact |
|--------------|--------------|--------------|--------|
| subprocess.run() with unchecked paths | Validated absolute paths within allowed directory | Phase 9 | Prevents path traversal attacks |
| No .env support | Schema validation ready for future .env usage | Phase 9 | Future-proof, secure credential handling |
| Data files loaded without validation | Schema validation with column/type/range checks | Phase 9 | Early detection of corrupted/malicious data |

**Deprecated/outdated:**
- `subprocess.run()` without path validation - Add validation
- Loading data files directly - Wrap with validation
- No environment variable schema - Define schema for future use

## Sources

### Primary (HIGH confidence)
- https://docs.python.org/3/library/subprocess.html - subprocess module, security considerations
- https://docs.python.org/3/library/pathlib.html - Path manipulation, security
- https://docs.python.org/3/library/os.html#os.environ - Environment variables
- https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.dtypes.html - DataFrame type checking
- https://cwe.mitre.org/data/definitions/427.html - CWE-427: Uncontrolled Search Path Element

### Secondary (MEDIUM confidence)
- CONCERNS.md - Security concerns SEC-01, SEC-02, SEC-03
- Current codebase analysis - Identified subprocess usage, input file patterns

### Tertiary (LOW confidence)
- https://pydantic-docs.helpmanual.io/ - Pydantic schema validation (optional pattern)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Python standard library and pandas (already using)
- Architecture: HIGH - Based on Python docs and security best practices
- Patterns: HIGH - Well-established security patterns

**Research date:** 2026-01-23
**Valid until:** 90 days (security patterns are fundamental, Python stdlib is stable)
