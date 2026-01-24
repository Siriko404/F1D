# Coding Conventions

**Analysis Date:** 2026-01-24

## Naming Patterns

**Files:**
- Main scripts: `X.Y_<Name>.py` pattern (e.g., `1.0_BuildSampleManifest.py`, `2.1_TokenizeAndCount.py`)
- Shared modules: `2_Scripts/shared/<module>.py` using snake_case (e.g., `data_validation.py`, `path_utils.py`)
- Test files: `test_<module>.py` placed in appropriate test directories (`tests/unit/`, `tests/integration/`, `tests/regression/`)

**Functions:**
- snake_case (e.g., `validate_dataframe_schema`, `load_config`, `setup_logging`)
- Descriptive names indicating action and purpose

**Variables:**
- snake_case (e.g., `script_path`, `allowed_dir`, `config`, `timestamp`)
- Clear, descriptive names

**Classes:**
- PascalCase for classes (e.g., `DataValidationError`, `PathValidationError`, `TestValidateScriptPath`)

**Constants:**
- UPPER_SNAKE_CASE (e.g., `ALLOWED_SCRIPT_DIR`, `INPUT_SCHEMAS`, `RAPIDFUZZ_AVAILABLE`)

**Types:**
- Type hints used extensively via `typing` module
- `Dict[str, Any]`, `Optional[str]`, `Path`, `Tuple`, etc.
- All function signatures include type hints

## Code Style

**Formatting:**
- Ruff for linting (no explicit config detected, using defaults)
- Black for formatting (implied by code style, no explicit config)
- 88-character line length implied by Black default

**Linting:**
- Ruff used (`.ruff_cache` present in repo)
- No custom ruff configuration in `pyproject.toml`

**Comments:**
- Section dividers: `# =============================================================================` or `# ================================================================================`
- Inline comments for complex logic
- Inline TODO notes for future work

## Import Organization

**Order:**
1. Standard library imports (os, sys, pathlib, datetime, typing, etc.)
2. Third-party imports (pandas, numpy, yaml, scipy, sklearn, etc.)
3. Local imports (from shared.* or relative imports)

**Pattern:**
```python
# Standard library
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Third-party
import pandas as pd
import yaml

# Local (shared modules)
from shared.data_validation import validate_dataframe_schema
from shared.path_utils import validate_output_path
```

**Import fallback pattern:**
```python
try:
    from shared.observability_utils import DualWriter
except ImportError:
    # Fallback if shared/__init__.py hasn't run yet
    import sys as _sys
    from pathlib import Path as _Path
    _script_dir = _Path(__file__).parent.parent
    _sys.path.insert(0, str(_script_dir))
    from shared.observability_utils import DualWriter
```

**Path resolution:**
- Use `pathlib.Path` exclusively for file paths
- Resolve to absolute paths: `Path(file).resolve()`
- Relative to `__file__`: `Path(__file__).parent.parent / "config"`

## Error Handling

**Custom exceptions:**
- `DataValidationError`: Raised when input data validation fails
- `PathValidationError`: Raised when path validation fails
- `EnvValidationError`: Raised when environment variable validation fails

**Exception raising patterns:**
```python
# With descriptive messages
raise ValueError(f"Script must be .py file: {script_path}")
raise FileNotFoundError(f"Script not found: {script_path}")
raise PathValidationError(f"Path does not exist: {path}")
```

**Type validation:**
```python
# Check types before processing
if not isinstance(value, expected_type):
    raise TypeError(f"Expected {expected_type}, got {type(value)}")
```

**Optional dependencies:**
```python
try:
    from rapidfuzz import fuzz
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False
    warnings.warn("RapidFuzz not installed", ImportWarning)
```

## Logging

**Framework:**
- Custom `DualWriter` from `shared.observability_utils`
- Dual output: terminal stdout AND log file simultaneously

**Pattern:**
```python
from shared.observability_utils import DualWriter

# Setup dual logging
dual_writer = DualWriter(log_path)
sys.stdout = dual_writer

# Use print for all logging (mirrored to both)
print("Processing data...")
print(f"Processed {count} rows", flush=True)

# Restore stdout
sys.stdout = dual_writer.terminal
dual_writer.close()
```

**Log file locations:**
- `3_Logs/<script_name>/<timestamp>.log`
- Timestamp format: `%Y-%m-%d_%H%M%S`

**Print pattern:**
- Use `print()` with `flush=True` for immediate output
- Progress prints mirrored verbatim between terminal and log file

## Comments

**When to Comment:**
- Module headers with triple quotes describing purpose
- Section dividers with `# ===================================================================`
- Inline comments for complex logic
- Security notes for validation functions

**Module header pattern:**
```python
#!/usr/bin/env python3
"""
===============================================================================
SHARED MODULE: Path Utilities
===============================================================================
ID: shared/path_utils
Description: Provides robust path validation and directory creation helpers

Inputs:
    - Path objects for validation (pathlib.Path)
    - Optional validation flags (must_exist, must_be_writable)

Outputs:
    - Validated Path objects (resolved to absolute paths)
    - Created directories (if needed)
    - Available disk space in GB

Deterministic: true
===============================================================================
"""
```

**Contract headers for scripts:**
```python
"""
==============================================================================
STEP 1: Build Sample Manifest (Orchestrator)
==============================================================================
ID: 1.0_BuildSampleManifest
Description: Orchestrates the 4-substep process to build the master sample

Inputs:
    - config/project.yaml

Outputs:
    - 4_Outputs/1.0_BuildSampleManifest/{timestamp}/master_sample_manifest.parquet
    - 3_Logs/1.0_BuildSampleManifest/{timestamp}.log

Deterministic: true
==============================================================================
"""
```

**JSDoc/TSDoc:**
- Google-style docstrings with Args, Returns, Raises sections
```python
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
```

## Function Design

**Size:**
- Functions typically 20-50 lines
- Helper functions can be shorter (10-20 lines)
- Complex functions broken into smaller helpers

**Parameters:**
- Type hints required for all parameters
- Default values for optional parameters
- Use `Optional[T]` for nullable parameters
```python
def load_validated_parquet(
    file_path: Path,
    schema_name: Optional[str] = None,
    strict: bool = True
) -> pd.DataFrame:
```

**Return Values:**
- Type hints required for return values
- Return typed objects (DataFrames, Paths, dicts)
- Use `-> None` for void functions
```python
def validate_dataframe_schema(...) -> None:
def load_validated_parquet(...) -> pd.DataFrame:
def get_process_memory_mb() -> Dict[str, float]:
```

## Module Design

**Exports:**
- Exported via `from module import function_name`
- No `__all__` declarations detected
- All public functions exported by default

**Barrel Files:**
- `2_Scripts/shared/` contains utility modules imported by main scripts
- No explicit barrel/__init__.py detected

**Shared utilities pattern:**
- Common utilities in `2_Scripts/shared/`
- Modules: `data_validation.py`, `path_utils.py`, `subprocess_validation.py`, `string_matching.py`, etc.
- Each module has clear purpose and security notes

**Determinism:**
- All scripts declare `Deterministic: true` in contract header
- Functions use deterministic algorithms (e.g., z-score with fixed threshold)
- Hash-based checksums (SHA-256) for regression testing

---

*Convention analysis: 2026-01-24*
