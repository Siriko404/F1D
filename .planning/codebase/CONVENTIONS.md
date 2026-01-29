# Coding Conventions

**Analysis Date:** 2025-01-29

## Naming Patterns

**Files:**
- Pattern: `<Stage>.<Step>[.<Substep>]_<PascalCaseName>.py`
- Examples:
  - `1.1_CleanMetadata.py` - Step 1.1 script
  - `2.1_TokenizeAndCount.py` - Step 2.1 script
  - `4.1.1_EstimateCeoClarity_CeoSpecific.py` - Step 4.1.1 script
- Shared modules: `shared/<module_name>.py` (e.g., `shared/path_utils.py`)
- Test files: `test_<module_name>.py` in `tests/unit/`, `tests/integration/`, `tests/regression/`

**Functions:**
- snake_case for all function names
- Descriptive verbs: `validate_output_path`, `compute_file_checksum`, `load_matching_config`
- Private/internal functions prefix with underscore: `_match_many_to_many_fallback()`

**Variables:**
- snake_case for variables
- Constants: UPPER_SNAKE_CASE (e.g., `RAPIDFUZZ_AVAILABLE`, `ENV_SCHEMA`)
- DataFrame variables: descriptive names like `metadata_cleaned`, `linguistic_counts`
- Configuration keys: snake_case in YAML (e.g., `random_seed`, `thread_count`)

**Types/Classes:**
- PascalCase for exceptions: `PathValidationError`, `DataValidationError`, `EnvValidationError`
- PascalCase for classes: `DualWriter`, `Capture`
- Schema constants: UPPER_SNAKE_CASE (e.g., `INPUT_SCHEMAS`, `ENV_SCHEMA`)

## Code Style

**Formatting:**
- No explicit formatter detected (no `.black`, `.isort`, or `.ruff` config files found)
- Manual formatting appears consistent with 4-space indentation
- Line length: Not explicitly enforced, but generally under 100-120 characters

**Linting:**
- No explicit linter configuration found in root directory
- Code follows clean, readable Python conventions

**Shebang:**
- Executable scripts use: `#!/usr/bin/env python3`
- All main processing scripts include this

**Import Organization:**

**Order:**
1. Standard library imports (sys, os, pathlib, argparse, datetime)
2. Third-party imports (pandas, numpy, yaml, psutil)
3. Local imports (shared modules, project-specific imports)

**Path manipulation for imports:**
```python
# Add 2_Scripts to sys.path for shared module imports
sys.path.insert(0, str(Path(__file__).parent.parent))
```

**Path Aliases:**
- None used - direct imports via `sys.path.insert(0, ...)` pattern
- Shared modules imported as `from shared.module_name import function_name`

## Error Handling

**Custom Exceptions:**
- Define project-specific exception classes inheriting from `Exception`
- Examples:
  - `PathValidationError` - Path validation failures in `shared/path_utils.py`
  - `DataValidationError` - Schema validation failures in `shared/data_validation.py`
  - `EnvValidationError` - Environment variable validation in `shared/env_validation.py`

**Exception Pattern:**
```python
class PathValidationError(Exception):
    """Raised when path validation fails."""
    pass

# Usage
if must_exist and not path.exists():
    raise PathValidationError(f"Path does not exist: {path}")
```

**Graceful Degradation:**
- Optional dependencies (like RapidFuzz) use try/except with fallbacks
```python
try:
    from rapidfuzz import fuzz, process, utils
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False
```

**Validation Pattern:**
- Validate early, fail fast
- Check prerequisites before main processing
- Use `argparse` for CLI argument validation

## Logging

**Framework:** Dual output pattern (terminal + log file)

**Patterns:**
- Use `DualWriter` class from `shared/observability_utils.py`
- Writes identical output to stdout and log file simultaneously

**Example:**
```python
from shared.observability_utils import DualWriter
from pathlib import Path

log_path = logs_dir / f"{timestamp}.log"
dual_writer = DualWriter(log_path)
sys.stdout = dual_writer  # Redirect stdout to write to both

# Now all print statements go to both terminal and log
print("Processing complete")
dual_writer.close()
```

**Log Header:**
Each script logs:
- Script ID (e.g., `1.1_CleanMetadata`)
- Start/end timestamps (ISO format)
- Git SHA
- Configuration snapshot
- Input file checksums
- Progress statistics (row counts, timing, missing values)

**Progress Messages:**
- Consistent formatting with `print_stat()` helper
```python
print_stat("Rows Processed", value=len(df))
print_stat("Duration (seconds)", value=duration)
```

## Comments

**When to Comment:**
- Module headers: Every script includes detailed docstring header
- Function docstrings: All public functions have docstrings
- Inline comments: Complex logic, data transformations, validation rules

**Module Header Format:**
```python
"""
==============================================================================
STEP X.Y: Step Name
==============================================================================
ID: X.Y_StepName
Description: Multi-line description of what the script does

Inputs:
    - input_file_path

Outputs:
    - output_file_path

Deterministic: true
==============================================================================
"""
```

**Function Docstring Format:**
```python
def validate_output_path(path: Path, must_exist: bool = False) -> Path:
    """
    Validate output path exists and is accessible.

    Args:
        path: Path to validate
        must_exist: If True, raise error if path doesn't exist

    Returns:
        Validated Path object (resolved to absolute)

    Raises:
        PathValidationError: If validation fails
    """
```

**JSDoc/TSDoc:**
- Not applicable (Python codebase, not TypeScript)

## Function Design

**Size:** No strict limit, but generally:
- Helper functions: 10-50 lines
- Main processing functions: 50-200 lines
- Scripts: 200-500 lines total (split into multiple functions)

**Parameters:**
- Type hints required for all function parameters
- Use keyword arguments for optional parameters
- Default values specified in function signature

**Return Values:**
- Always specify return type in type hints
- Return early for error conditions
- Use tuples for multiple return values: `return (best_match, score)`

**Example:**
```python
def match_company_names(
    query: str,
    candidates: List[str],
    threshold: Optional[float] = None,
    scorer_name: str = "WRatio",
    preprocess: bool = True,
) -> Tuple[str, float]:
    """
    Find best matching company name using RapidFuzz.

    Returns:
        (best_match, score) tuple. Returns (query, 0.0) if no match.
    """
    # Implementation...
```

## Module Design

**Exports:**
- Public functions exported directly
- Internal functions prefixed with underscore
- Constants (schemas, configurations) exported as UPPER_SNAKE_CASE

**Barrel Files:**
- `shared/` directory acts as a barrel for common utilities
- Individual modules in `shared/` imported directly

**Example:**
```python
# In shared/path_utils.py
def validate_output_path(...) -> Path: ...
def ensure_output_dir(...) -> Path: ...
class PathValidationError(Exception): ...

# Usage in scripts
from shared.path_utils import validate_output_path, ensure_output_dir
```

## Configuration

**Central Config:**
- All configuration in `config/project.yaml`
- Loaded via `yaml.safe_load()`
- Structure: top-level sections (project, data, paths, determinism, logging, step_XX)

**Config Loading Pattern:**
```python
config_path = Path(__file__).parent.parent / "config" / "project.yaml"
with open(config_path) as f:
    config = yaml.safe_load(f)

year_start = config["data"]["year_start"]
year_end = config["data"]["year_end"]
```

**Determinism Settings:**
- `random_seed: 42` - Fixed seed for RNG
- `thread_count: 1` - Single-threaded for reproducibility
- `sort_inputs: true` - Sort dataframes before processing

## Data Processing Conventions

**DataFrame Operations:**
- Use pandas for all data manipulation
- Validate schemas before processing (using `shared/data_validation.py`)
- Compute checksums for outputs (SHA-256)

**File Naming:**
- Timestamped output directories: `YYYY-MM-DD_HHMMSS/`
- `latest/` symlink points to most recent run
- Parquet format for data files (`.parquet`)
- CSV for human-readable outputs

**Path Resolution:**
- Use `pathlib.Path` for all path operations
- Resolve paths to absolute: `path.resolve()`
- Use `pathlib` for cross-platform compatibility

**Script Structure:**
1. Shebang and docstring header
2. Imports (standard, third-party, local)
3. CLI argument parsing
4. Prerequisite validation
5. Main processing logic
6. Output generation and statistics
7. Symlink update to `latest/`

**Contract Header (each script):**
```python
"""
==============================================================================
STEP X.Y: Step Name
==============================================================================
ID: X.Y_StepName
Description: ...

Inputs:
    - path/to/input

Outputs:
    - path/to/output

Deterministic: true
==============================================================================
"""
```

---

*Convention analysis: 2025-01-29*
