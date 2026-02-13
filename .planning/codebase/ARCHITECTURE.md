# Architecture

**Analysis Date:** 2026-02-12

## Pattern Overview

**Overall:** Sequential Pipeline with Shared Utilities

**Key Characteristics:**
- 4-stage sequential processing pipeline (Sample Construction -> Text Processing -> Financial Features -> Econometric Analysis)
- Shared utility layer (`2_Scripts/shared/`) providing cross-cutting functionality
- Timestamped output directories for reproducibility and versioning
- YAML-based configuration for parameter management
- Deterministic processing with explicit random seeds

## Layers

**Pipeline Scripts (Application Layer):**
- Purpose: Execute specific data transformation steps
- Location: `2_Scripts/{1_Sample,2_Text,3_Financial,4_Econometric}/`
- Contains: Numbered step scripts (e.g., `1.0_BuildSampleManifest.py`, `2.1_TokenizeAndCount.py`)
- Depends on: `shared/` utilities, `config/project.yaml`
- Used by: Manual execution or CI/CD pipeline

**Shared Utilities (Infrastructure Layer):**
- Purpose: Reusable components for data validation, regression, logging, path handling
- Location: `2_Scripts/shared/`
- Contains: Utility modules (`panel_ols.py`, `financial_utils.py`, `regression_helpers.py`, etc.)
- Depends on: pandas, numpy, linearmodels, statsmodels
- Used by: All pipeline scripts via `from shared.xxx import yyy`

**Configuration Layer:**
- Purpose: Centralized parameter management and pipeline settings
- Location: `config/project.yaml`
- Contains: Data paths, processing parameters, step configurations, output specifications
- Depends on: None (static YAML)
- Used by: All pipeline scripts via `yaml.safe_load()`

**Observability Sub-package:**
- Purpose: Logging, statistics collection, memory tracking, anomaly detection
- Location: `2_Scripts/shared/observability/`
- Contains: `logging.py`, `stats.py`, `memory.py`, `throughput.py`, `anomalies.py`, `files.py`
- Depends on: pandas, numpy, time, psutil
- Used by: All scripts via `from shared.observability_utils import DualWriter`

## Data Flow

**Main Pipeline Flow:**

1. **Step 1: Sample Construction**
   - Input: Raw earnings call transcripts (`1_Inputs/Unified-info.parquet`, `speaker_data_*.parquet`)
   - Process: Clean metadata, link entities to financial databases, build tenure maps
   - Output: `4_Outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet`

2. **Step 2: Text Processing**
   - Input: `master_sample_manifest.parquet` + Loughran-McDonald dictionary
   - Process: Tokenize text, count dictionary word categories, construct linguistic variables
   - Output: `4_Outputs/2.2_ConstructVariables/latest/linguistic_variables.parquet`

3. **Step 3: Financial Features**
   - Input: `master_sample_manifest.parquet` + CRSP/Compustat/IBES data
   - Process: Compute firm controls, market variables, event flags
   - Output: `firm_controls.parquet`, `market_variables.parquet`, `event_flags.parquet`

4. **Step 4: Econometric Analysis**
   - Input: All processed parquet files
   - Process: Estimate CEO clarity scores, run IV regressions, hazard models
   - Output: CEO scores, regression tables (`.tex`), diagnostic reports

**State Management:**
- Intermediate outputs stored in timestamped directories under `4_Outputs/{step_name}/{timestamp}/`
- Latest outputs symlinked via `latest/` subdirectory
- Checksums computed for reproducibility verification
- Processing stats saved as `stats.json` alongside outputs

## Key Abstractions

**Script Header Pattern:**
- Purpose: Standardized metadata and documentation for each script
- Examples: All scripts in `2_Scripts/*/` follow this pattern
- Pattern: Multi-line docstring with ID, Description, Inputs, Outputs, Dependencies, Deterministic flag

```python
#!/usr/bin/env python3
"""
================================================================================
STEP X.Y: Script Name
================================================================================
ID: X.Y_ScriptName
Description: What this script does

Inputs:
    - Input file paths

Outputs:
    - Output file paths

Deterministic: true
Dependencies:
    - Requires: Previous step
    - Uses: pandas, numpy

Author: Thesis Author
Date: YYYY-MM-DD
================================================================================
"""
```

**DualWriter Pattern:**
- Purpose: Simultaneous logging to stdout and file
- Examples: All pipeline scripts
- Pattern: Context manager wrapping stdout/stderr

```python
from shared.observability_utils import DualWriter

with DualWriter(log_path):
    # All print() statements go to both console and log file
    print("Processing...")
```

**Output Directory Resolution:**
- Purpose: Find most recent output from previous step
- Examples: All downstream scripts
- Pattern: `get_latest_output_dir()` from `shared.path_utils`

```python
from shared.path_utils import get_latest_output_dir

input_dir = get_latest_output_dir(base_dir / "1.4_AssembleManifest")
input_file = input_dir / "master_sample_manifest.parquet"
```

**Panel OLS Regression:**
- Purpose: Standardized panel regression with fixed effects and diagnostics
- Examples: `4_Econometric/` scripts
- Pattern: `run_panel_ols()` from `shared.panel_ols`

```python
from shared.panel_ols import run_panel_ols

result = run_panel_ols(
    df=panel_df,
    dependent="MaQaUnc_pct",
    exog=["SurpDec", "EPS_Growth", "StockRet"],
    entity_col="gvkey",
    time_col="year",
    industry_col="ff48_code",
    cluster_by_entity=True,
)
```

## Entry Points

**Pipeline Scripts:**
- Location: `2_Scripts/{1_Sample,2_Text,3_Financial,4_Econometric}/*.py`
- Triggers: Direct execution via `python script.py` or `python -m script`
- Responsibilities: Load config, validate inputs, transform data, save outputs

**Validation Script:**
- Location: `2_Scripts/2.0_ValidateV2Structure.py`
- Triggers: Manual validation or CI/CD
- Responsibilities: Verify pipeline structure, check dependencies, validate configuration

**Test Runner:**
- Location: `tests/` (via pytest)
- Triggers: `pytest tests/` command
- Responsibilities: Unit tests, integration tests, regression tests

**CLI Arguments:**
- Most scripts accept `--config` for custom YAML path
- All scripts use argparse for command-line interface
- Deterministic mode enforced via `--seed` or config setting

## Error Handling

**Strategy:** Explicit validation with custom exceptions

**Patterns:**
- `PathValidationError` - Invalid file paths
- `OutputResolutionError` - Cannot find output directory
- `DataValidationError` - Schema mismatch in input data
- `FinancialCalculationError` - Invalid financial metric computation
- `CollinearityError` / `MulticollinearityError` - Regression design matrix issues

**Example from `shared/financial_utils.py`:**
```python
from shared.data_validation import FinancialCalculationError

if gvkey is None:
    raise FinancialCalculationError(
        f"Cannot calculate firm controls: missing gvkey in row. "
        f"Row columns: {list(row.index)}. Year: {year}"
    )
```

## Cross-Cutting Concerns

**Logging:** DualWriter class in `shared/observability/logging.py` - writes to both console and timestamped log file in `3_Logs/`

**Validation:** Schema-based validation in `shared/data_validation.py` - checks required columns, types, value ranges before processing

**Authentication:** Not applicable (no external API authentication)

**Memory Management:** `track_memory_usage` decorator and `MemoryAwareThrottler` in `shared/chunked_reader.py` - monitors memory and throttles processing

**Configuration:** Centralized YAML in `config/project.yaml` with step-specific sections (e.g., `step_01`, `step_02`)

**Checksums:** SHA-256 file checksums computed via `compute_file_checksum()` for reproducibility verification

**Type Hints:** Gradual mypy adoption with stubs for untyped packages (`2_Scripts/stubs/linearmodels*.pyi`)

---

*Architecture analysis: 2026-02-12*
