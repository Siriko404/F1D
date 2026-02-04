# Architecture

**Analysis Date:** 2025-02-04

## Pattern Overview

**Overall:** Sequential Pipeline with Shared Utilities

**Key Characteristics:**
- Four-stage sequential data processing pipeline (Sample → Text → Financial → Econometric)
- Each stage produces timestamped outputs with `latest/` symlinks for downstream consumption
- Direct-run scripts (no orchestrator) with configuration-driven behavior from `config/project.yaml`
- Shared utility modules in `2_Scripts/shared/` for cross-cutting concerns
- Parquet-based data persistence with contract headers declaring inputs/outputs

## Layers

**Configuration Layer:**
- Purpose: Centralized runtime configuration and path management
- Location: `config/project.yaml`
- Contains: Project metadata, data paths, step-specific parameters, thresholds
- Depends on: Nothing
- Used by: All pipeline scripts via `load_config()`

**Shared Utilities Layer:**
- Purpose: Reusable functions for logging, validation, path operations, statistics
- Location: `2_Scripts/shared/`
- Contains: Observability helpers, path validation, data loading, regression utilities, string matching, financial calculations
- Depends on: Third-party libraries (pandas, numpy, statsmodels, rapidfuzz)
- Used by: All pipeline stages

**Stage 1 - Sample Construction Layer:**
- Purpose: Build master sample manifest from raw earnings call metadata
- Location: `2_Scripts/1_Sample/`
- Contains: Metadata cleaning, entity linking, tenure mapping, manifest assembly
- Depends on: `1_Inputs/Unified-info.parquet`, `CRSPCompustat_CCM/`, `shared/` utilities
- Used by: Stage 2 (Text Processing) and Stage 3 (Financial Features)

**Stage 2 - Text Processing Layer:**
- Purpose: Tokenize transcripts and construct linguistic variables
- Location: `2_Scripts/2_Text/`
- Contains: Tokenization, word counting, linguistic measure construction, verification
- Depends on: `1_Inputs/speaker_data_{year}.parquet`, `Loughran-McDonald_MasterDictionary_1993-2024.csv`, Stage 1 outputs
- Used by: Stage 4 (Econometric Analysis)

**Stage 3 - Financial Features Layer:**
- Purpose: Compute firm-level controls and market variables
- Location: `2_Scripts/3_Financial/`
- Contains: Firm controls (Size, BM, Lev, ROA, EPS_Growth), market variables (returns, surprise), event flags
- Depends on: `1_Inputs/comp_na_daily_all/`, `tr_ibes/`, `CRSP_DSF/`, `CCCL instrument/`, Stage 1 outputs
- Used by: Stage 4 (Econometric Analysis)

**Stage 4 - Econometric Analysis Layer:**
- Purpose: Estimate CEO clarity scores and run regressions
- Location: `2_Scripts/4_Econometric/`
- Contains: CEO fixed effects estimation, liquidity regressions, takeover hazards, summary statistics
- Depends on: Stage 1 (manifest), Stage 2 (linguistic variables), Stage 3 (financial controls)
- Used by: Final research outputs

**Testing Layer:**
- Purpose: Unit and integration tests for shared utilities and pipeline steps
- Location: `tests/`
- Contains: Test fixtures, unit tests for validation, fuzzy matching, environment checks
- Depends on: Shared utilities, pytest framework
- Used by: Development workflow

## Data Flow

**Sample Construction Flow:**

1. `1.1_CleanMetadata.py` loads `Unified-info.parquet`, deduplicates, filters for earnings calls (event_type='1'), validates date range (2002-2018)
2. `1.2_LinkEntities.py` links calls to firms via 4-tier strategy: PERMNO+date → CUSIP8+date → fuzzy matching → unmatched audit
3. `1.3_BuildTenureMap.py` constructs CEO tenure timeline from speaker data, builds monthly panel
4. `1.4_AssembleManifest.py` joins metadata + tenure, filters for CEOs with ≥5 calls, produces `master_sample_manifest.parquet`

**State Management:**
- Each step writes to timestamped subdirectory: `4_Outputs/{StepName}/{YYYY-MM-DD_HHMMSS}/`
- `latest/` symlink points to most recent successful output for downstream resolution
- State is immutable (timestamped outputs never modified)
- Inputs validated via `get_latest_output_dir()` with required file checks

**Text Processing Flow:**

1. `2.1_TokenizeAndCount.py` tokenizes transcripts using LM dictionary, counts word frequencies per call
2. `2.2_ConstructVariables.py` computes linguistic measures (clarity, tone, complexity) from word counts
3. `2.3_Report.py` generates verification reports and descriptive statistics

**Financial Features Flow:**

1. `3.1_FirmControls.py` merges Compustat quarterly data, computes Size, BM, Lev, ROA, EPS_Growth, SurpDec
2. `3.2_MarketVariables.py` calculates stock returns, market returns, event windows around calls
3. `3.3_EventFlags.py` adds takeover flags from SDC and CEO dismissal data
4. `3.0_BuildFinancialFeatures.py` orchestrates all financial feature construction

**Econometric Analysis Flow:**

1. `4.1_EstimateCeoClarity.py` runs fixed effects OLS by FF12 industry (main/finance/utility), extracts CEO-specific clarity coefficients
2. `4.2_LiquidityRegressions.py` estimates liquidity models with CEO clarity as independent variable
3. `4.3_TakeoverHazards.py` runs hazard models for takeover probability
4. `4.4_GenerateSummaryStats.py` produces final summary statistics and tables

## Key Abstractions

**DualWriter:**
- Purpose: Synchronized stdout + file logging for progress tracking
- Examples: `2_Scripts/shared/observability_utils.py`, `2_Scripts/shared/dual_writer.py`
- Pattern: Context manager that writes identical output to terminal and log file via `sys.stdout` redirection

**Path Resolution with Timestamps:**
- Purpose: Locate outputs from prior steps without hardcoding paths
- Examples: `shared/path_utils.py:get_latest_output_dir()`
- Pattern: `get_latest_output_dir(base_dir, required_file="X.parquet")` scans timestamped subdirs, returns most recent with required file, raises `OutputResolutionError` if not found

**Contract Headers:**
- Purpose: Declare script inputs/outputs/determinism in docstring
- Examples: All scripts in `2_Scripts/*/`
- Pattern: Triple-quoted docstring with ID, Description, Inputs, Outputs, Deterministic fields

**Graceful Degradation for Optional Dependencies:**
- Purpose: Allow pipeline to run without optional packages (e.g., rapidfuzz, statsmodels)
- Examples: `shared/regression_utils.py:STATSMODELS_AVAILABLE`, `shared/string_matching.py`
- Pattern: Try-import with `STATSMODELS_AVAILABLE` flag, raise ImportError at point-of-use if missing

**Memory-Aware Processing:**
- Purpose: Handle large datasets without OOM errors
- Examples: `shared/chunked_reader.py:MemoryAwareThrottler`, column pruning in Step 2/3 scripts
- Pattern: Monitor memory via psutil, throttle batch sizes, use `usecols` parameter in `pd.read_parquet()`

## Entry Points

**Direct Script Execution:**
- Location: All `2_Scripts/*/*.py` files
- Triggers: Manual command line execution: `python 2_Scripts/1_Sample/1.1_CleanMetadata.py`
- Responsibilities: Parse CLI args (`--dry-run`), validate prerequisites, load config, execute step, write outputs

**Shared Module Imports:**
- Location: `2_Scripts/shared/*.py`
- Triggers: Imported by pipeline scripts via `from shared.x import y`
- Responsibilities: Provide reusable utilities, handle cross-cutting concerns

**Test Execution:**
- Location: `tests/unit/*.py`, `tests/integration/*.py`
- Triggers: `pytest` command
- Responsibilities: Validate shared utilities, check contract compliance

## Error Handling

**Strategy:** Fail-fast with validation → clear error messages → audit trails

**Patterns:**
- **Path Validation:** `PathValidationError` raised by `shared/path_utils.py` for missing/unwritable paths
- **Output Resolution:** `OutputResolutionError` raised when `get_latest_output_dir()` cannot find required file
- **Dependency Validation:** `ImportError` raised at point-of-use for optional dependencies (statsmodels, rapidfuzz)
- **Prerequisite Checking:** `check_prerequisites()` functions validate inputs from prior steps before execution
- **Graceful Degradation:** Try-import blocks allow pipeline to continue without optional features (e.g., Tier 3 fuzzy matching without rapidfuzz)

## Cross-Cutting Concerns

**Logging:** DualWriter pattern writes verbatim output to terminal + log file (`3_Logs/{StepName}/{timestamp}.log`)

**Validation:** Shared utilities in `shared/env_validation.py`, `shared/data_validation.py`, `shared/cli_validation.py` check environment, data schemas, CLI arguments

**Authentication:** Not applicable (local data processing, no external APIs)

**Configuration:** Centralized in `config/project.yaml`, loaded via `load_config()` in each script

**Determinism:** Seeds set from config (`random_seed: 42`), thread counts pinned, input sorting enforced, checksums computed for reproducibility

---

*Architecture analysis: 2025-02-04*
