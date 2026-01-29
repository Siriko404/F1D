# Architecture

**Analysis Date:** 2025-01-29

## Pattern Overview

**Overall:** Sequential Pipeline with Shared Utilities

**Key Characteristics:**
- **Sequential execution**: Scripts run in dependency order (Phase 1 → 2 → 3 → 4)
- **No orchestrator**: Each script is independently executable (no parent runner)
- **Deterministic outputs**: Timestamped directories with symlinks to `latest/`
- **Dual-write logging**: All output mirrored to stdout and log files
- **Shared utilities**: Common functionality in `2_Scripts/shared/`
- **Config-driven**: Single `config/project.yaml` as source of truth

## Layers

**Pipeline Scripts (2_Scripts/):**
- Purpose: Data processing and analysis logic
- Location: `2_Scripts/{1_Sample,2_Text,3_Financial,4_Econometric}/`
- Contains: 18 active scripts across 4 phases
- Depends on: Shared utilities, input data from `1_Inputs/`
- Used by: Researchers running the pipeline

**Shared Utilities (2_Scripts/shared/):**
- Purpose: Reusable functions for validation, I/O, observability
- Location: `2_Scripts/shared/*.py`
- Contains: 20+ modules for path validation, data loading, regression, string matching
- Depends on: pandas, numpy, yaml, scipy, statsmodels
- Used by: All pipeline scripts

**Input Data Layer (1_Inputs/):**
- Purpose: Raw data sources (earnings calls, financial data, dictionaries)
- Location: `1_Inputs/{CRSP_DSF,comp_na_daily_all,Execucomp,SDC,tr_ibes,CCCL instrument}/`
- Contains: Parquet files, CSV dictionaries, Excel files
- Depends on: External data providers (WRDS, SEC)
- Used by: Phase 1 and Phase 3 scripts

**Output Layer (4_Outputs/):**
- Purpose: Processed data, regression results, reports
- Location: `4_Outputs/{step_name}/{timestamp}/`
- Contains: Parquet datasets, CSV summaries, markdown reports, LaTeX tables
- Depends on: Pipeline scripts
- Used by: Phase 4 scripts, researchers

**Log Layer (3_Logs/):**
- Purpose: Execution logs for reproducibility and debugging
- Location: `3_Logs/{step_name}/{timestamp}.log`
- Contains: Timestamped execution logs with progress stats, checksums, errors
- Depends on: Pipeline scripts (via DualWriter)
- Used by: Researchers for validation

**Test Layer (tests/):**
- Purpose: Unit, integration, regression tests
- Location: `tests/{unit,integration,regression}/`
- Contains: pytest fixtures, test data, validation scripts
- Depends on: Shared utilities, pipeline scripts
- Used by: CI/CD, developers

## Data Flow

**Phase 1: Sample Construction (1_Sample/):**

1. Load `Unified-info.parquet` (428K earnings call metadata records)
2. Clean metadata: deduplicate, validate dates, filter event_type='1' (earnings calls)
3. Link entities: 4-tier strategy (PERMNO+date → CUSIP8+date → fuzzy name → ticker)
4. Build tenure map: Track CEO tenures from Execucomp, resolve overlaps
5. Assemble manifest: Merge all datasets, apply 5-call minimum threshold
6. Output: `master_sample_manifest.parquet` (~286K calls)

**Phase 2: Text Processing (2_Text/):**

1. Load `master_sample_manifest.parquet` + `speaker_data_*.parquet` (yearly)
2. Tokenize: Split Q&A text into tokens, count LM dictionary categories
3. Aggregate: Sum counts to call level by speaker type (Manager, CEO, Analyst)
4. Construct variables: Compute percentages (e.g., Manager_QA_Uncertainty_pct = Uncertainty / word_tokens)
5. Output: `linguistic_variables_*.parquet` (one per year, 2002-2018)

**Phase 3: Financial Features (3_Financial/):**

1. Load `master_sample_manifest.parquet` + financial datasets (Compustat, CRSP, IBES, SDC)
2. Compute firm controls: Size, BM, Lev, ROA, RD_Intensity (lagged 1 fiscal year)
3. Compute market variables: StockRet, MarketRet, Volatility, Amihud liquidity (event windows)
4. Flag events: Takeover events from SDC (3-tier matching)
5. Output: `firm_controls_*.parquet`, `market_variables_*.parquet`, `event_flags_*.parquet`

**Phase 4: Econometric Analysis (4_Econometric/):**

1. Load all Phase 1-3 outputs + linguistic variables
2. Estimate CEO clarity: OLS with CEO fixed effects, extract gamma_i, standardize
3. Robustness checks: CEO-specific controls, extended controls, firm regime effects
4. IV analysis: First-stage ClarityCEO ~ CCCL instrument, second-stage Delta_Amihud
5. Survival analysis: Cox PH takeover hazards, Fine-Gray competing risks
6. Generate summary: Descriptive stats, correlation matrices, balance tables
7. Output: `ceo_clarity_scores.parquet`, regression results (TXT, CSV, LaTeX)

**State Management:**
- No global state (each script loads config from `config/project.yaml`)
- Outputs are immutable (timestamped directories never modified)
- Symlinks (`latest/`) provide stable references to most recent outputs
- Logs capture full execution state (git SHA, config snapshot, input checksums)

## Key Abstractions

**DualWriter (observability_utils.py):**
- Purpose: Synchronized output to stdout and log file
- Examples: `2_Scripts/shared/observability_utils.py:303`
- Pattern: Context manager that writes identical content to two streams

**Variable Reference (reporting_utils.py):**
- Purpose: Track variable definitions, sources, and transformations
- Examples: `2_Scripts/shared/reporting_utils.py:109`
- Pattern: Generate CSV documenting all variables created by a script

**Schema Validation (data_validation.py):**
- Purpose: Validate DataFrames against expected columns and types
- Examples: `2_Scripts/shared/data_validation.py:68`
- Pattern: Decorator/wrapper around `pd.read_parquet()` with schema checks

**Four-Tier Entity Linking (string_matching.py):**
- Purpose: Match company names across datasets with fallback strategy
- Examples: `2_Scripts/shared/string_matching.py:104`
- Pattern: Try exact match → fuzzy match (RapidFuzz) → ticker match → fail

**Fixed Effects Extraction (regression_utils.py):**
- Purpose: Extract CEO-specific coefficients from OLS with entity dummies
- Examples: `2_Scripts/shared/regression_utils.py:71`
- Pattern: Fit `y ~ C(ceo_id) + X`, extract gamma_i, compute ClarityCEO = -gamma_i

## Entry Points

**Pipeline Scripts:**
- Location: `2_Scripts/{1_Sample,2_Text,3_Financial,4_Econometric}/*.py`
- Triggers: Manual execution by researcher or CI/CD
- Responsibilities:
  - Load config from `config/project.yaml`
  - Validate prerequisites (input files, dependencies)
  - Execute data processing
  - Write outputs to `4_Outputs/{step_name}/{timestamp}/`
  - Update `latest/` symlink
  - Log progress to `3_Logs/{step_name}/{timestamp}.log`

**Test Suite:**
- Location: `tests/{unit,integration,regression}/test_*.py`
- Triggers: `pytest` command
- Responsibilities:
  - Validate shared utility functions
  - Check data pipeline integrity
  - Regression testing (output stability)

**Shared Modules:**
- Location: `2_Scripts/shared/*.py`
- Triggers: Imported by pipeline scripts
- Responsibilities:
  - Path validation (`path_utils.py`)
  - Data loading with validation (`data_validation.py`)
  - Observability (`observability_utils.py`)
  - Regression helpers (`regression_helpers.py`)
  - String matching (`string_matching.py`)

## Error Handling

**Strategy:** Explicit validation with clear error messages, fail-fast on contract violations

**Patterns:**
- **Path validation**: Raise `PathValidationError` if input files missing
- **Schema validation**: Raise `DataValidationError` if DataFrame columns/types incorrect
- **Regression validation**: Raise `RegressionValidationError` if insufficient data, multicollinearity
- **Subprocess validation**: Validate script paths before `subprocess.run()` (security)
- **Environment validation**: Schema-based env var checking (preparatory for .env support)

**Logging:**
- All exceptions logged with full traceback to `3_Logs/`
- DualWriter ensures errors visible in terminal and log file
- Progress stats (row counts, memory usage, timing) logged at each major step

## Cross-Cutting Concerns

**Logging:** DualWriter pattern ensures identical stdout and log file output

**Validation:**
- Input files: `validate_input_file()` from `path_utils.py`
- Data schemas: `validate_dataframe_schema()` from `data_validation.py`
- Regression data: `validate_regression_data()` from `regression_validation.py`
- CLI arguments: `parse_arguments_*()` functions in `cli_validation.py`

**Authentication:** Not currently used (no external API calls in current codebase)

**Determinism:**
- Random seed set from `config/project.yaml` (default: 42)
- Single-threaded execution by default (thread_count: 1)
- Input sorting before processing (sort_inputs: true)
- Output checksums (SHA-256) logged for verification

**Reproducibility:**
- Each script logs: git SHA, config snapshot, input file checksums
- Timestamped outputs preserve execution history
- `latest/` symlinks provide convenient access to recent outputs
- Regression tests compare checksums to detect drift

---

*Architecture analysis: 2025-01-29*
