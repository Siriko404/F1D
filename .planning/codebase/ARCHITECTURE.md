# Architecture

**Analysis Date:** 2026-01-22

## Pattern Overview

**Overall:** Linear Data Processing Pipeline

**Key Characteristics:**
- **Stage-Based Execution:** discrete processing steps numbered sequentially (Step 1, Step 2, etc.)
- **Configuration-Driven:** Central `project.yaml` controls all parameters, paths, and toggles.
- **Strict I/O Isolation:** Inputs, Scripts, Logs, and Outputs are strictly separated at the root level.
- **Timestamped Versioning:** Outputs are saved in timestamped directories with `latest` symlinks for downstream consumption.
- **Dual Logging:** Execution progress is mirrored verbatim to both stdout and log files.

## Layers

**Configuration:**
- Purpose: Single source of truth for runtime parameters.
- Location: `config/project.yaml`
- Contains: Paths, toggle flags, algorithm parameters (e.g., thresholds, windows), and determinism settings.

**Data Source (Inputs):**
- Purpose: Read-only raw data.
- Location: `1_Inputs/`
- Contains: Parquet files (`speaker_data`, `Unified-info`) and CSV dictionaries.

**Processing (Scripts):**
- Purpose: Core logic transformation.
- Location: `2_Scripts/`
- Contains: Python scripts organized by domain (`2_Text`, `3_Financial`, etc.).
- Depends on: `config/project.yaml` and files in `1_Inputs` or upstream `4_Outputs`.

**Artifacts (Outputs):**
- Purpose: Persisted results of processing steps.
- Location: `4_Outputs/`
- Structure: `{Category}/{Step_Name}/{Timestamp}/`.
- Used by: Downstream scripts (via `latest` symlink).

**Observability (Logs):**
- Purpose: Execution audit trails.
- Location: `3_Logs/`
- Pattern: Matches script hierarchy.

## Data Flow

**Standard Pipeline Step:**

1. **Load Config:** Script reads `config/project.yaml` to get paths and parameters.
2. **Setup Logging:** Initialize `DualWriter` to capture stdout to `3_Logs/...`.
3. **Read Inputs:** Load raw data from `1_Inputs` or previous step's output from `4_Outputs/.../latest`.
4. **Process:** Apply logic (Tokenization, Regression, Filtering) using `pandas`/`sklearn`.
5. **Write Output:** Save results to `4_Outputs/.../{Timestamp}/`.
6. **Update State:** Update `latest` symlink to point to the new timestamped folder.

**State Management:**
- Stateless execution; each run is independent.
- State is passed via file system artifacts (Parquet/CSV).

## Key Abstractions

**DualWriter:**
- Purpose: Mirrors console output to a log file.
- Examples: `setup_logging` function in scripts.
- Pattern: Wrapper around `sys.stdout`.

**Configuration Loader:**
- Purpose: Standardized loading of YAML config.
- Examples: `load_config()` in scripts.

**Output Versioning:**
- Purpose: Manages the `latest` pointer for chaining steps.
- Examples: `update_latest_symlink()`.

## Entry Points

**Script Execution:**
- Location: `2_Scripts/{Category}/{Stage}.{Step}_{Name}.py`
- Triggers: Manual execution or shell orchestration (e.g., `python 2_Scripts/2_Text/2.1_TokenizeAndCount.py`).
- Responsibilities: Load data, process year-by-year, save results.

## Error Handling

**Strategy:** Fail Fast & Log
- Scripts tend to stop on missing inputs or critical errors.
- Exceptions are caught during file operations (e.g., symlink creation) but generally bubble up for logic errors.

## Cross-Cutting Concerns

**Logging:**
- Implemented in every script via `setup_logging`.
- Writes to `3_Logs/{Step_Name}/{Timestamp}.log`.

**Determinism:**
- Enforced via config (Seed `42`, Thread count `1`).
- Scripts expected to sort inputs and set seeds.

**File Formats:**
- Parquet used for high-performance dataframes.
- CSV used for dictionaries and audit reports.
