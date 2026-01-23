# Coding Conventions

**Analysis Date:** 2026-01-22

## Naming Patterns

**Files:**
- Pattern: `<Stage>.<Step>[.<Substep>]_<PascalCaseName>.py`
- Examples: `1.1_CleanMetadata.py`, `2.1_TokenizeAndCount.py`, `4.1.1_EstimateCeoClarity_CeoSpecific.py`
- Stage mapping: 1=Inputs, 2=Scripts, 3=Logs, 4=Outputs (from naming scheme in scripts)
- Utility files: `<Stage>_<Number>_Utils.py` (e.g., `1.5_Utils.py`, `3.4_Utils.py`)

**Functions:**
- snake_case naming: `load_config()`, `setup_paths()`, `compute_file_checksum()`, `print_stat()`
- Descriptive names: `generate_variable_reference()`, `update_latest_symlink()`, `analyze_missing_values()`

**Variables:**
- snake_case naming: `df`, `config`, `paths`, `timestamp`, `stats`
- Descriptive names: `original_count`, `exact_dupes`, `year_stats`, `vocab_sets`

**Classes:**
- PascalCase naming: `DualWriter`

**Constants:**
- UPPER_CASE: `STATSMODELS_AVAILABLE`, `FUZZ_AVAILABLE`

## Code Style

**Formatting:**
- No formal formatter configured (no .prettierrc, black, or autopep8 found)
- Manual indentation (4 spaces apparent from files)
- Line length appears ~80-120 characters

**Linting:**
- No formal linter configured (no .eslintrc, .pylintrc, pyproject.toml)
- .ruff_cache directory exists but no ruff config found
- Manual code review appears to be primary enforcement

**Shebang:**
- Python scripts use: `#!/usr/bin/env python3`

## Import Organization

**Order:**
1. Standard library imports (sys, os, pathlib, datetime)
2. Third-party imports (pandas, numpy, yaml)
3. Local imports (dynamic importlib.util for utility modules)

**Pattern:**
```python
import sys
import os
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
import yaml
import importlib.util

# Dynamic import for utility modules (Python cannot import modules starting with numbers)
utils_path = Path(__file__).parent / "1.5_Utils.py"
spec = importlib.util.spec_from_file_location("utils", utils_path)
utils = importlib.util.module_from_spec(spec)
sys.modules["utils"] = utils
spec.loader.exec_module(utils)
from utils import generate_variable_reference, update_latest_symlink
```

**Path Aliases:**
- None used - all paths use explicit `Path()` objects with relative paths

## Error Handling

**Patterns:**
- Try-except with specific exception types
- Critical errors use `sys.exit(1)` after printing error message
- Optional dependencies checked with try-except and warning printed

**Import error handling:**
```python
try:
    from rapidfuzz import fuzz, process
    FUZZ_AVAILABLE = True
except ImportError:
    FUZZ_AVAILABLE = False
    print("Warning: rapidfuzz not available, skipping fuzzy matching")
```

**Critical import handling:**
```python
try:
    utils_path = Path(__file__).parent / "1.5_Utils.py"
    spec = importlib.util.spec_from_file_location("utils", utils_path)
    utils = importlib.util.module_from_spec(spec)
    sys.modules["utils"] = utils
    spec.loader.exec_module(utils)
    from utils import generate_variable_reference, update_latest_symlink
except ImportError as e:
    print(f"Criticial Error importing utils: {e}")
    sys.exit(1)
```

**File operation handling:**
```python
try:
    os.symlink(str(output_dir), str(latest_dir), target_is_directory=True)
except OSError:
    try:
        shutil.copytree(str(output_dir), str(latest_dir))
    except Exception as e:
        print_fn(f"Warning: Could not create 'latest': {e}")
```

**Optional features:**
- Optional features degraded gracefully (e.g., fuzzy matching, statsmodels)

## Logging

**Framework:** Custom DualWriter class (not using Python's logging module)

**Patterns:**
- DualWriter class writes verbatim to both stdout and log file
- Setup at script start: `sys.stdout = DualWriter(log_path)`
- Restore before exit: `sys.stdout = dual_writer.terminal; dual_writer.close()`

**DualWriter class pattern:**
```python
class DualWriter:
    """Writes to both stdout and log file verbatim"""
    def __init__(self, log_path):
        self.terminal = sys.stdout
        self.log = open(log_path, "w", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def close(self):
        self.log.close()
```

**When/how to log:**
- Every print statement goes to both terminal and log
- Progress indicators with step descriptions
- Statistics summaries formatted with `print_stat()` helper
- Flush frequently to ensure log persistence

## Comments

**When to Comment:**
- Script headers with metadata blocks
- Section dividers: `# ==============================================================================`
- Step descriptions: `# Step 1: Removing exact duplicate rows...`
- Inline comments for complex logic

**Docstring pattern:**
```python
"""
==============================================================================
STEP 1.1: Clean Metadata & Event Filtering
==============================================================================
ID: 1.1_CleanMetadata
Description: Loads Unified-info, deduplicates exact rows, resolves file_name
             collisions, and filters for earnings calls (event_type='1') in
             the target date range (2002-2018).

Inputs:
    - 1_Inputs/Unified-info.parquet
    - config/project.yaml

Outputs:
    - 4_Outputs/1.1_CleanMetadata/{timestamp}/metadata_cleaned.parquet
    - 4_Outputs/1.1_CleanMetadata/{timestamp}/variable_reference.csv
    - 4_Outputs/1.1_CleanMetadata/{timestamp}/report_step_1_1.md
    - 3_Logs/1.1_CleanMetadata/{timestamp}.log

Deterministic: true
==============================================================================
"""
```

**JSDoc/TSDoc:**
- Not applicable (Python codebase)
- Function docstrings are plain text, not typed

## Function Design

**Size:**
- No explicit size limits observed
- Functions typically 10-30 lines
- Helper functions for statistics: `print_stat()`, `analyze_missing_values()`, `save_stats()`
- Processing functions can be longer (50-100 lines) when necessary

**Parameters:**
- Explicit parameter lists (no *args, **kwargs in main functions)
- Common parameters: `df` (DataFrame), `config` (dict), `paths` (dict), `timestamp` (str)
- Optional print function: `print_fn=print` for utilities

**Return Values:**
- DataFrames for data transformations
- Dictionaries for statistics/configurations
- Paths for directory setup
- None for side-effect functions (logging, file writing)

## Module Design

**Exports:**
- Utility modules export named functions: `generate_variable_reference`, `update_latest_symlink`, `get_latest_output_dir`, `load_master_variable_definitions`
- Main scripts are executable (no imports, just `if __name__ == "__main__": main()`)

**Barrel Files:**
- Not used
- Each step imports utility modules dynamically via importlib

**Configuration:**
- Central config: `config/project.yaml` (YAML)
- Loading pattern: `yaml.safe_load()` from `Path(__file__).parent.parent.parent / "config" / "project.yaml"`
- No environment variables used (except possibly for path resolution)

## Data Processing Patterns

**Paths:**
- Always use `pathlib.Path` for file operations
- Relative paths from project root: `root = Path(__file__).parent.parent.parent`
- Consistent directory structure: `1_Inputs/`, `2_Scripts/`, `3_Logs/`, `4_Outputs/`

**DataFrames:**
- Pandas for all data manipulation
- Parquet format for intermediate files: `.to_parquet()`, `.read_parquet()`
- CSV for references/reports: `.to_csv()`, `.read_csv()`
- JSON for statistics: `json.dump()` with `indent=2, default=str`

**Statistics Collection:**
- Consistent stats dictionary structure:
```python
stats = {
    "step_id": "1.1_CleanMetadata",
    "timestamp": timestamp,
    "input": {"files": [], "checksums": {}, "total_rows": 0},
    "processing": {},
    "output": {"final_rows": 0},
    "missing_values": {},
    "timing": {"start_time": ..., "end_time": ..., "duration_seconds": 0.0}
}
```

**Checksums:**
- SHA256 for file integrity: `compute_file_checksum(filepath, algorithm="sha256")`
- 8KB chunks for memory efficiency

**Timestamps:**
- ISO format: `datetime.now().isoformat()`
- Directory format: `datetime.now().strftime("%Y-%m-%d_%H%M%S")`

**Symlinks:**
- Latest directory is symlink to timestamped directory
- Fallback to copytree on Windows without admin rights
- Pattern: `update_latest_symlink(latest_dir, output_dir, print_fn)`

## Script Structure

**Main script template:**
1. Header docstring (ID, Description, Inputs, Outputs, Deterministic)
2. Imports (std lib, third-party, local via importlib)
3. DualWriter class definition
4. Statistics helper functions
5. Configuration/path setup functions
6. Main processing functions
7. `main()` entry point with:
   - Load config
   - Setup paths
   - Setup dual logging
   - Initialize stats
   - Processing steps
   - Generate reports
   - Update symlink
   - Save stats
8. `if __name__ == "__main__": sys.exit(main())`

---

*Convention analysis: 2026-01-22*
