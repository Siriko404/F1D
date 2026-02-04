# Coding Conventions

**Analysis Date:** 2025-02-04

## Naming Patterns

**Files:**
- Follow strict naming pattern: `<Stage>.<Step>[.<Substep>]_<PascalCaseName>[.<ext>]`
- Examples: `1.1_CleanMetadata.py`, `3.1_FirmControls.py`, `4.1.2_EstimateCeoClarity_Extended.py`
- Regex: `^(1|2|3|4)\.(\d+)(?:\.(\d+))?_[A-Z][A-Za-z0-9]*(?:_[A-Z][A-Za-z0-9]*)*(?:\.[A-Za-z0-9]+)?$`
- Stage mapping: `1=Inputs`, `2=Scripts`, `3=Logs`, `4=Outputs`

**Functions:**
- snake_case for all function names
- Descriptive verbs: `load_manifest`, `compute_compustat_controls`, `validate_dataframe_schema`
- Test functions: `test_<function_name>_<scenario>`

**Variables:**
- snake_case for local variables: `manifest_df`, `compustat_df`, `stats`
- Constants: UPPER_SNAKE_CASE: `INPUT_SCHEMAS`, `ALLOWED_SCRIPT_DIR`
- Private module-level: leading underscore not commonly used

**Types:**
- Type hints used extensively in function signatures
- Example: `def load_manifest(manifest_dir) -> pd.DataFrame:`
- Example: `def compute_firm_controls(row: pd.Series, compustat_df: pd.DataFrame, year: int) -> dict:`
- Use `from typing import Dict, List, Optional, Any, Tuple`

**Classes:**
- PascalCase for class names: `DataValidationError`, `DualWriter`, `MemoryAwareThrottler`
- Test classes: `Test<FunctionName>` (e.g., `TestValidateDataFrameSchema`)

## Code Style

**Formatting:**
- No explicit formatter detected (no .prettierrc, black.toml, or similar)
- Use 4-space indentation (Python PEP 8 standard)
- Line length appears to follow standard Python conventions

**Linting:**
- No explicit linter config file (.eslintrc, ruff.toml)
- Code follows clean Python conventions with consistent patterns

## Import Organization

**Order:**
1. Standard library imports (`import sys`, `import os`, `from pathlib import Path`)
2. Third-party imports (`import pandas as pd`, `import yaml`, `import pytest`)
3. Local/shared module imports (`from shared.observability_utils import DualWriter`)

**Path setup for shared modules:**
```python
# Add parent directory to sys.path for shared module imports
import sys as _sys
from pathlib import Path as _Path

_script_dir = Path(__file__).parent.parent
_sys.path.insert(0, str(_script_dir))

from shared.observability_utils import DualWriter
from shared.path_utils import validate_input_file
```

**Path Aliases:**
- Use absolute paths from project root
- Root directory: `Path(__file__).parent.parent.parent` (from script in `2_Scripts/`)
- Config: `root / "config" / "project.yaml"`
- Inputs: `root / "1_Inputs"`
- Outputs: `root / "4_Outputs"`
- Logs: `root / "3_Logs"`

## Error Handling

**Patterns:**

1. **Custom Exception Classes:**
```python
class DataValidationError(Exception):
    """Raised when input data validation fails."""
    pass

class OutputResolutionError(Exception):
    """Raised when output directory resolution fails."""
    pass
```

2. **File Validation with Errors:**
```python
from shared.path_utils import validate_input_file, OutputResolutionError

def load_config():
    config_path = Path(__file__).parent.parent.parent / "config" / "project.yaml"
    validate_input_file(config_path, must_exist=True)
    with open(config_path, "r") as f:
        return yaml.safe_load(f)
```

3. **Fail-Fast on Missing Inputs:**
```python
if not manifest_file.exists():
    raise FileNotFoundError(f"Manifest not found: {manifest_file}")
```

4. **Graceful Degradation (optional):**
```python
# In non-strict mode, warn instead of raising
if strict:
    raise DataValidationError(error_msg)
else:
    print(f"WARNING: {error_msg}", file=sys.stderr)
```

5. **Subprocess Error Handling:**
```python
if result.returncode != 0:
    print_dual(
        f"\nERROR: Substep {step['id']} failed with exit code {result.returncode}"
    )
    if result.stderr:
        print_dual(f"STDERR:\n{result.stderr}")
    success = False
    break
```

## Logging

**Framework:** DualWriter (custom in `shared/observability_utils.py`)

**Pattern:**
```python
from shared.observability_utils import DualWriter

# Setup dual logging (stdout + file)
log_file = paths["log_file"]
dual_writer = DualWriter(log_file)
sys.stdout = dual_writer

# All print statements go to both terminal and log file
print("Processing data...")
print_dual("Message with custom function")

# Restore stdout when done
sys.stdout = dual_writer.terminal
dual_writer.close()
```

**Log location:** `3_Logs/<StepName>/<timestamp>.log`

**When to log:**
- Script start/end with timestamp
- Major processing steps
- Row counts before/after operations
- Merge/join statistics
- Error conditions
- Warnings for non-fatal issues

## Comments

**When to Comment:**
- Module header with contract block (required)
- Complex business logic explanations
- Algorithm justifications
- Data source references
- External library citations

**Contract Header (each script):**
```python
#!/usr/bin/env python3
"""
==============================================================================
STEP <X>.<Y>: <PascalCase Name>
==============================================================================
ID: <X>_<Y>_<Name>
Description: <What this step does>

<Additional details about inputs/outputs/methodology>

Inputs:
    - <path to input 1>
    - <path to input 2>

Outputs:
    - <path to output 1>
    - <path to output 2>

Deterministic: true
==============================================================================
"""
```

**Documentation Comments:**
```python
def calculate_firm_controls(
    row: pd.Series, compustat_df: pd.DataFrame, year: int
) -> dict:
    """
    Calculate firm-level control variables from Compustat data.

    Args:
        row: DataFrame row with firm identifiers (gvkey, datadate)
        compustat_df: Compustat data with firm metrics
        year: Fiscal year for data selection

    Returns:
        Dictionary with: size (log assets), leverage, profitability,
        market_to_book, capex_intensity, r_intensity, dividend_payer
    """
```

**Inline Comments:**
- Use for explaining WHY, not WHAT
- Example: `# Treat missing R&D as 0 (common practice in finance literature)`

## Function Design

**Size:**
- Prefer functions under 50 lines
- Large functions allowed for orchestration (e.g., `main()` functions)
- Shared module utilities kept focused

**Parameters:**
- Use type hints for all parameters
- Default values for optional parameters: `strict: bool = True`
- Use `**kwargs` sparingly

**Return Values:**
- Always return concrete types (dict, DataFrame, tuple)
- Use `None` for failure/missing data cases
- Return early for error conditions

**Pattern:**
```python
def function_name(param1: Type, param2: Type) -> ReturnType:
    """Brief description."""
    # Setup
    result = []

    # Processing
    for item in items:
        processed = transform(item)
        result.append(processed)

    # Return
    return pd.DataFrame(result)
```

## Module Design

**Exports:**
- Shared modules use `__all__` for explicit exports
- Example from `shared/dual_writer.py`:
```python
__all__ = ["DualWriter"]
```

**Barrel Files:**
- `shared/__init__.py` exports commonly used utilities:
```python
from .observability_utils import DualWriter
from .industry_utils import parse_ff_industries
from .metadata_utils import load_variable_descriptions
from .path_utils import get_latest_output_dir, OutputResolutionError
```

**Shared Module Organization:**
- `shared/observability_utils.py` - Statistics, monitoring, logging
- `shared/path_utils.py` - Path resolution, validation
- `shared/data_validation.py` - Schema validation
- `shared/financial_utils.py` - Financial calculations
- `shared/regression_helpers.py` - Statistical modeling
- `shared/dual_writer.py` - Logging re-export

## Determinism Guidelines

**Randomness Control:**
- Read seeds from `config/project.yaml`:
```python
config = yaml.safe_load(config_file)
random_seed = config["determinism"]["random_seed"]
np.random.seed(random_seed)
```

**Thread Count:**
- Pin thread counts from config:
```python
thread_count = config["determinism"]["thread_count"]
```

**Sort Order:**
- Always sort before processing to avoid filesystem order effects:
```python
compustat_df = compustat_df.sort_values(["gvkey", "datadate"])
```

**Checksum Tracking:**
- Compute input file checksums for reproducibility:
```python
from shared.observability_utils import compute_file_checksum
checksum = compute_file_checksum(input_path)
stats["input"]["checksums"][filename] = checksum
```

## Data Processing Patterns

**Column Pruning:**
```python
# Load only required columns to save memory
required_cols = ["gvkey", "datadate", "atq", "ceqq"]
df = pd.read_parquet(file_path, columns=required_cols)
```

**Vectorized Operations:**
```python
# Use merge_asof instead of iterrows for matching
merged = pd.merge_asof(
    manifest_sorted,
    compustat_sorted,
    left_on="start_date",
    right_on="datadate",
    by="gvkey",
    direction="backward",
)
```

**Winsorization:**
```python
if winsorize:
    p1, p99 = df[col].quantile([0.01, 0.99])
    df[col] = df[col].clip(lower=p1, upper=p99)
```

## Observable Patterns

**Statistics Collection:**
```python
stats = {
    "step_id": "3.1_FirmControls",
    "timestamp": timestamp,
    "input": {"files": [], "checksums": {}, "total_rows": 0},
    "processing": {},
    "output": {"final_rows": 0, "files": [], "checksums": {}},
    "timing": {"start_iso": start_iso, "end_iso": "", "duration_seconds": 0.0},
    "memory": {"start_mb": mem_start, "end_mb": 0.0, "peak_mb": 0.0},
    "throughput": {"rows_per_second": 0.0},
}
```

**Memory Tracking:**
```python
from shared.observability_utils import get_process_memory_mb
mem_start = get_process_memory_mb()
# ... processing ...
mem_end = get_process_memory_mb()
stats["memory"]["delta_mb"] = mem_end["rss_mb"] - mem_start["rss_mb"]
```

**Timing:**
```python
import time
start_time = time.perf_counter()
# ... processing ...
duration = time.perf_counter() - start_time
stats["timing"]["duration_seconds"] = round(duration, 2)
```

---

*Convention analysis: 2025-02-04*
