# Architecture

**Analysis Date:** 2025-02-10

## Pattern Overview

**Overall:** 4-Stage Sequential Pipeline with Shared Utilities Layer

**Key Characteristics:**
- Sequential data flow where each stage consumes outputs from prior stages
- Timestamped output directories enabling reproducibility and audit trails
- Hypothesis-driven variable construction (H1-H9) for econometric testing
- Graceful degradation (optional dependencies like RapidFuzz, statsmodels)
- Deterministic execution (fixed seeds, single-threaded, sorted inputs)

## Layers

**Shared Utilities Layer:**
- Purpose: Provides common functions for path validation, observability, regression, data loading, and validation
- Location: `2_Scripts/shared/`
- Contains: Reusable modules imported by all pipeline scripts
- Depends on: pandas, numpy, optional dependencies (statsmodels, linearmodels, rapidfuzz)
- Used by: All step scripts (1_Sample, 2_Text, 3_Financial, 4_Econometric)

**Step 1 - Sample Construction Layer:**
- Purpose: Build master sample manifest linking earnings calls to firms and CEOs
- Location: `2_Scripts/1_Sample/`
- Contains: Entity linking, tenure mapping, manifest assembly
- Depends on: Raw inputs (`1_Inputs/`), shared utilities
- Used by: All downstream steps (text processing, financial, econometric)

**Step 2 - Text Processing Layer:**
- Purpose: Tokenize transcripts and construct linguistic variables (uncertainty, tone)
- Location: `2_Scripts/2_Text/`
- Contains: Tokenization, LM dictionary word counting, variable construction
- Depends on: `1_Sample` outputs, LM dictionary, shared utilities
- Used by: Financial V2 (hypothesis variable construction)

**Step 3 - Financial Features Layer:**
- Purpose: Three sub-layers for different variable generations

**Legacy Financial (3_Financial):**
- Location: `2_Scripts/3_Financial/`
- Contains: Firm controls, market variables, event flags
- Purpose: Original financial variables for general analysis

**Financial V2 (3_Financial_V2):**
- Location: `2_Scripts/3_Financial_V2/`
- Contains: H1-H8 hypothesis-specific variables
- Purpose: Constructs dependent variables, moderators, controls for each hypothesis
- Depends on: `1_Sample` outputs, `2_Text` outputs, Compustat/CRSP data

**Financial V3 (5_Financial_V3):**
- Location: `2_Scripts/5_Financial_V3/`
- Contains: H9 hypothesis variables (CEO style, abnormal investment)
- Purpose: Advanced hypothesis requiring multi-step construction
- Depends on: Prior financial variables, PRisk data, CEO tenure data

**Step 4 - Econometric Analysis Layer:**
- Purpose: Estimate panel regressions and generate publication-ready output

**Legacy Econometric (4_Econometric):**
- Location: `2_Scripts/4_Econometric/`
- Contains: CEO clarity estimation, liquidity regressions, takeover hazards
- Purpose: Original econometric models

**Econometric V2 (4_Econometric_V2):**
- Location: `2_Scripts/4_Econometric_V2/`
- Contains: H1-H9 regression scripts, CEO fixed effects
- Purpose: Hypothesis testing with firm/year/industry fixed effects
- Depends on: `3_Financial_V2` outputs, `5_Financial_V3` outputs (for H9)

**Econometric V3 (4_Econometric_V3):**
- Location: `2_Scripts/4_Econometric_V3/`
- Contains: Specialized regressions (e.g., H2 PRisk x Uncertainty)
- Purpose: Advanced econometric specifications

## Data Flow

**Primary Flow:**

1. Raw inputs (`1_Inputs/`) contain earnings calls, financial data, dictionaries
2. `1_Sample` builds `master_sample_manifest.parquet` (call-firm-CEO linkage)
3. `2_Text` consumes manifest + transcript text, produces `linguistic_variables.parquet`
4. `3_Financial_V2` consumes manifest + linguistic variables + Compustat/CRSP, produces hypothesis-specific datasets (H1-H8)
5. `4_Econometric_V2` consumes financial variables, runs panel regressions, produces coefficient tables and results

**Timestamp Resolution:**
- Each script creates timestamped output directory: `4_Outputs/<StepName>/<YYYY-MM-DD_HHMMSS>/`
- Downstream scripts use `get_latest_output_dir()` to locate inputs
- Enables reproducibility: same inputs + same code = same outputs

**State Management:**
- No global state between scripts
- All state passed through parquet files
- YAML config (`config/project.yaml`) defines paths and parameters
- Logs written to `3_Logs/<StepName>/<timestamp>.log` with dual-writer (console + file)

## Key Abstractions

**DualWriter (Observability):**
- Purpose: Synchronized output to stdout and log file
- Examples: `2_Scripts/shared/observability_utils.py`
- Pattern: Context manager that wraps stdout, ensures log file receives identical output

**Timestamp-Based Output Resolution:**
- Purpose: Locate latest outputs without hardcoding paths
- Examples: `2_Scripts/shared/path_utils.py:get_latest_output_dir()`
- Pattern: Scan directory for timestamped subdirs, validate required file exists, return path

**Panel OLS with Fixed Effects:**
- Purpose: Standardized regression interface for hypothesis testing
- Examples: `2_Scripts/shared/panel_ols.py:run_panel_ols()`
- Pattern: Wrap linearmodels.PanelOLS with firm/year/industry FE, clustered SEs, VIF diagnostics

**Variable Reference Pattern:**
- Purpose: Document all constructed variables with formulas and sources
- Examples: `1_Sample/1.5_Utils.py:generate_variable_reference()`
- Pattern: Function generates CSV with variable_name, formula, source, description

**Hypothesis-Specific Variable Construction:**
- Purpose: Isolate dependent/moderator/control variables by hypothesis
- Examples: `3_Financial_V2/3.1_H1Variables.py`, `3.2_H2Variables.py`, etc.
- Pattern: Each script produces `<H#>_<Outcome>.parquet` with variables for that hypothesis

## Entry Points

**Manual Script Execution:**
- Location: Individual scripts in `2_Scripts/<Step>/`
- Triggers: `python 2_Scripts/1_Sample/1.1_CleanMetadata.py`
- Responsibilities: Each script is executable directly, validates inputs via `validate_input_file()`

**Pipeline Orchestration (Manual):**
- Location: No orchestrator script - scripts run sequentially by user
- Triggers: User executes scripts in numbered order (1.1, 1.2, 1.3, ...)
- Responsibilities: User manages dependencies, monitors timestamps

**Testing Entry Points:**
- Location: `tests/unit/`, `tests/integration/`, `tests/regression/`
- Triggers: `pytest tests/unit/test_data_validation.py`
- Responsibilities: Verify shared utilities, edge cases, subprocess validation

**Validation Script:**
- Location: `2_Scripts/2.0_ValidateV2Structure.py`
- Triggers: Run after structural changes to verify V2 pipeline integrity
- Responsibilities: Validate output existence, schema compatibility, data quality

## Error Handling

**Strategy:** Validation + Logging + Graceful Degradation

**Patterns:**
- **Input validation:** `validate_input_file()` checks file existence and permissions before reading
- **Output validation:** `validate_output_path()` ensures output directories are writable
- **Dependency checking:** Optional imports wrapped in try/except with STATSMODELS_AVAILABLE flags
- **Subprocess validation:** `shared/subprocess_validation.py` captures and logs subprocess errors
- **Anomaly detection:** `observability_utils.py` provides z-score and IQR-based outlier detection

**Missing Data Handling:**
- Scripts explicitly check for missing required files using `get_latest_output_dir()`
- Graceful error messages point to missing prerequisite steps
- Example: "Required output from Step 1.2 not found. Run 1.2_LinkEntities.py first."

**Optional Dependency Graceful Degradation:**
- RapidFuzz: Tier 3 fuzzy matching degrades to ticker-only matching if unavailable
- statsmodels/linearmodels: Regression scripts raise ImportError with clear install instructions
- Subprocess calls wrapped in try/except with stderr capture

## Cross-Cutting Concerns

**Logging:** DualWriter pattern writes to both stdout and `3_Logs/<StepName>/<timestamp>.log`. All scripts use `setup_logging()` to initialize.

**Validation:** Shared utilities in `shared/data_validation.py`, `shared/env_validation.py` check file existence, schema compatibility, environment configuration.

**Path Management:** All paths use `pathlib.Path`, resolved relative to project root via `Path(__file__).parent.parent.parent`. Centralized in `shared/path_utils.py`.

**Memory Management:** Column pruning in parquet reads (`columns=[...]`), chunked processing available in `shared/chunked_reader.py`, memory-aware throttling in `config/project.yaml`.

**Determinism:** Fixed random seeds (42 in config), single-threaded execution by default (`thread_count: 1`), sorted inputs (`sort_inputs: true`).

**Observability:** `print_stat()`, `analyze_missing_values()`, `compute_file_checksum()` provide standardized metrics collection across all scripts.

---

*Architecture analysis: 2025-02-10*
