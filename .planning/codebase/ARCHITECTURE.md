# Architecture

**Analysis Date:** 2026-02-14

## Pattern Overview

**Overall:** 4-Stage Sequential Data Processing Pipeline with Tiered Shared Utilities

**Key Characteristics:**
- Sequential processing: Step 1 -> Step 2 -> Step 3 -> Step 4 (with explicit dependencies)
- Orchestrator pattern: Each major step has an orchestrator that coordinates substeps
- Timestamped outputs: All outputs go to timestamped directories for reproducibility
- Configuration-driven: Central YAML config (`config/project.yaml`) drives pipeline behavior
- Shared utilities: Common functions abstracted to `src/f1d/shared/` for reuse
- Deterministic processing: Fixed seed, sorted inputs, reproducible outputs

## Layers

**Configuration Layer:**
- Purpose: Centralized configuration for pipeline behavior, paths, and parameters
- Location: `config/project.yaml`, `src/f1d/shared/config/`
- Contains: Path definitions, step-specific settings, dataset configurations, string matching rules
- Depends on: Pydantic settings for type-safe configuration
- Used by: All orchestrator scripts and shared utilities

**Input/Data Layer:**
- Purpose: Raw data storage for pipeline consumption
- Location: `1_Inputs/`
- Contains: Earnings call transcripts, financial data (CRSP, Compustat, IBES), executive data (Execucomp), M&A data (SDC), reference dictionaries
- Depends on: External data sources (Wharton Research Data Services, Thomson Reuters, etc.)
- Used by: Step 1 (Sample) reads Unified-info; Step 3 (Financial) reads financial datasets

**Processing Layer:**
- Purpose: Core data transformation logic organized by processing stage
- Location: `src/f1d/{sample,text,financial,econometric}/`
- Contains: Orchestrator scripts (`1.0_*.py`, `2.0_*.py`, `3.0_*.py`, `4.0_*.py`) and implementation scripts
- Depends on: Shared utilities, Input layer, Previous step outputs
- Used by: CLI execution or direct Python invocation

**Shared Utilities Layer:**
- Purpose: Common functionality shared across all processing steps
- Location: `src/f1d/shared/`
- Contains: Path resolution, data loading, regression utilities, logging, validation, observability
- Depends on: pandas, numpy, linearmodels, statsmodels, structlog
- Used by: All processing layer scripts

**Output Layer:**
- Purpose: Intermediate and final results storage with timestamped directories
- Location: `4_Outputs/` (timestamped subdirectories per step)
- Contains: Processed parquet files, reports, logs, statistics JSON
- Depends on: Processing layer produces outputs
- Used by: Next pipeline step (inputs), Final analysis

## Data Flow

**Sample Construction Flow (Step 1):**

1. `1.1_CleanMetadata.py` - Reads `Unified-info.parquet`, cleans and deduplicates
2. `1.2_LinkEntities.py` - 4-tier linking (PERMNO, CUSIP, fuzzy, ticker) to assign GVKEY
3. `1.3_BuildTenureMap.py` - Builds monthly CEO tenure panel from Execucomp
4. `1.4_AssembleManifest.py` - Joins all datasets, assigns industry codes, applies CEO filter
5. Output: `master_sample_manifest.parquet` with ~286K calls, 1.2K CEOs, 1K firms

**Text Processing Flow (Step 2):**

1. `2.1_TokenizeAndCount.py` - Tokenizes Q&A text, counts LM dictionary categories
2. `2.2_ConstructVariables.py` - Aggregates to call-level linguistic variables (Manager_QA_Uncertainty_pct, etc.)
3. `verify_step2.py` - Validates text processing outputs
4. `report_step2.py` - Generates verification report
5. Output: `linguistic_variables_YYYY.parquet` per year (2002-2018)

**Financial Features Flow (Step 3):**

1. `3.1_FirmControls.py` - Computes Size, BM, Lev, ROA, CurrentRatio, RD_Intensity from Compustat
2. `3.2_MarketVariables.py` - Computes StockRet, MarketRet, Volatility, Amihud from CRSP
3. `3.3_EventFlags.py` - Flags takeover events from SDC data
4. Output: `firm_controls_YYYY.parquet`, `market_variables_YYYY.parquet`, `event_flags_YYYY.parquet`

**Econometric Analysis Flow (Step 4):**

1. `4.1_EstimateCeoClarity.py` - CEO fixed effects regression (gamma_i extraction) -> ClarityCEO scores
2. `4.2_LiquidityRegressions.py` - Liquidity models with CCCL instrument
3. `4.3_TakeoverHazards.py` - Hazard models for takeover events
4. `4.4_GenerateSummaryStats.py` - Descriptive statistics
5. Output: CEO clarity scores, regression results, hazard model outputs

**State Management:**
- Parquet files used for intermediate state persistence (fast columnar I/O)
- Timestamped directories prevent overwrites and enable reproducibility
- No in-memory state carried between steps (each step is idempotent)

## Key Abstractions

**Path Resolution Abstraction:**
- Purpose: Resolve output paths with timestamp-based directory lookup
- Examples: `src/f1d/shared/path_utils.py:get_latest_output_dir()`
- Pattern: `get_latest_output_dir(base_path, required_file="*.parquet")` returns most recent timestamped directory

**Orchestrator Abstraction:**
- Purpose: Coordinate multiple substeps into unified processing
- Examples: `src/f1d/sample/1.0_BuildSampleManifest.py`, `src/f1d/financial/v1/3.0_BuildFinancialFeatures.py`
- Pattern: Main script loads config, iterates substeps via subprocess or direct import, aggregates outputs

**Panel Regression Abstraction:**
- Purpose: Standardized interface for fixed effects panel regressions
- Examples: `src/f1d/shared/panel_ols.py:run_panel_ols()`
- Pattern: `run_panel_ols(df, dependent, exog, entity_col, time_col, cov_type)` returns model, coefficients, diagnostics

**Observability Abstraction:**
- Purpose: Track memory, timing, throughput, anomalies for pipeline monitoring
- Examples: `src/f1d/shared/observability/`, `src/f1d/shared/observability_utils.py`
- Pattern: Stats dictionary with input/processing/output/memory/timing/throughput/quality_anomalies keys, saved as JSON

**Dual Writer Abstraction:**
- Purpose: Simultaneous stdout and file logging
- Examples: `src/f1d/shared/dual_writer.py`
- Pattern: `DualWriter(log_file).write(msg)` writes to both console and log file, replaces sys.stdout

**Entity Matching Abstraction:**
- Purpose: Multi-tier fuzzy name matching for company/speaker linking
- Examples: `src/f1d/shared/string_matching.py`
- Pattern: 4-tier strategy (exact, CUSIP, fuzzy >=92%, ticker) with configurable thresholds

## Entry Points

**Orchestrator Entry Points:**
- Location: `src/f1d/{sample,text,financial,econometric}/*_0_*.py`
- Triggers: CLI execution (`python -m f1d.sample.1_0_BuildSampleManifest`)
- Responsibilities: Coordinate substeps, validate prerequisites, generate summary reports

**Direct Script Entry Points:**
- Location: `src/f1d/{sample,text,financial,econometric}/{step_number}.{substep}.py`
- Triggers: Called by orchestrators or direct execution
- Responsibilities: Perform specific transformation (e.g., load parquet, compute variable, save parquet)

**Shared Utility Entry Points:**
- Location: `src/f1d/shared/*.py`
- Triggers: Imported by processing scripts
- Responsibilities: Provide reusable functions (path resolution, validation, regression, logging)

**Module Entry Points:**
- Location: `src/f1d/__init__.py`
- Triggers: `from f1d import get_latest_output_dir, run_panel_ols`
- Responsibilities: Public API re-exports for external usage

## Error Handling

**Strategy:** Graceful degradation with informative messages

**Patterns:**
- **Prerequisite validation:** `validate_prerequisites()` checks for missing inputs/outputs before execution
- **Graceful import handling:** `try: import linearmodels except ImportError: LINEARMODELS_AVAILABLE = False`
- **Custom exceptions:** `CollinearityError`, `MulticollinearityError`, `DataValidationError`, `EnvValidationError`, `OutputResolutionError`
- **Validation functions:** `validate_dataframe_schema()`, `load_validated_parquet()` for schema enforcement
- **Checkpoints:** Substep-level success/failure detection in orchestrators
- **Detailed error reporting:** Error messages include context (file paths, column names, row counts)

## Cross-Cutting Concerns

**Logging:** Structured logging using structlog with JSON file output and colored console
- Configuration: `src/f1d/shared/logging/config.py:configure_logging()`
- Pattern: `get_logger(__name__)` with context binding (event, rows, stage)
- Outputs: Console (human-readable) + file (JSON) in `3_Logs/` timestamped directories

**Validation:** Multi-layer validation (env, data, prerequisites, regression)
- Environment: `env_validation.py` validates schema
- Data: `data_validation.py` validates schema and calculations
- Prerequisites: `dependency_checker.py` validates file/step dependencies
- Regression: `regression_validation.py` validates VIF, collinearity

**Authentication:** Not applicable (local data processing, no external API auth)

---

*Architecture analysis: 2026-02-14*
