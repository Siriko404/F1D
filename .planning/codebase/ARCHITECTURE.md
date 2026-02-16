# Architecture

**Analysis Date:** 2026-02-15

## Pattern Overview

**Overall:** 4-Stage Sequential Pipeline with Cross-Cutting Shared Utilities

**Key Characteristics:**
- Sequential data processing: Sample -> Text -> Financial -> Econometric
- Stage modularity: Each stage independent with versioned variants (V1/V2)
- Shared utilities: Cross-cutting concerns centralized in `src/f1d/shared/`
- Deterministic outputs: Timestamped directories with latest symlinks
- Observable: Structured logging, memory tracking, and metrics collection

## Layers

**Tier 0: Configuration & Coordination**
- Purpose: Centralized configuration and project-level settings
- Location: `config/`, `.planning/`
- Contains: `config/project.yaml` (pipeline config), `.planning/` (phases, roadmap, milestones)
- Depends on: None (root layer)
- Used by: All stages (via `f1d.shared.config`)

**Tier 1: Shared Utilities (Cross-Cutting Concerns)**
- Purpose: Reusable utilities for all pipeline stages
- Location: `src/f1d/shared/`
- Contains: Configuration loading, path utilities, logging, data validation, regression helpers, observability
- Depends on: Tier 0
- Used by: All Tier 2 stage modules

**Tier 2: Stage-Specific Modules**
- Purpose: Domain-specific processing for each pipeline stage
- Location: `src/f1d/sample/`, `src/f1d/text/`, `src/f1d/financial/`, `src/f1d/econometric/`
- Contains: Processing scripts organized by stage and version (V1/V2)
- Depends on: Tier 1 (shared utilities) + Tier 0 (config)
- Used by: Users (direct execution) and orchestrator scripts

**Tier 3: Data Storage**
- Purpose: Immutable inputs, processing outputs, execution logs
- Location: `1_Inputs/`, `4_Outputs/`, `3_Logs/`
- Contains: Raw data files, timestamped output directories, execution logs
- Depends on: Tier 2 (producers)
- Used by: Tier 2 (consumers) and Tier 4 (analysis)

**Tier 4: Documentation & Planning**
- Purpose: Project planning, roadmap tracking, technical documentation
- Location: `.planning/`, `docs/`
- Contains: Phase plans, milestones, architecture standards, codebase docs
- Depends on: All tiers (documentation source)
- Used by: Developers, orchestrator

## Data Flow

**Stage 1: Sample Construction**
1. Load `1_Inputs/Earnings_Calls_Transcripts/Unified-info.parquet` (raw call metadata)
2. Clean metadata (`src/f1d/sample/1.1_CleanMetadata.py`) - deduplicate events, validate
3. Link entities (`src/f1d/sample/1.2_LinkEntities.py`) - 4-tier CCM linking for GVKEY
4. Build tenure map (`src/f1d/sample/1.3_BuildTenureMap.py`) - CEO tenure from Execucomp
5. Assemble manifest (`src/f1d/sample/1.4_AssembleManifest.py`) - merge, filter, final sample
6. Output: `4_Outputs/1.4_AssembleManifest/master_sample_manifest.parquet`

**Stage 2: Text Processing**
1. Load master sample manifest
2. Tokenize transcripts (`src/f1d/text/tokenize_and_count.py`) - LM dictionary word counts
3. Construct variables (`src/f1d/text/construct_variables.py`) - compute linguistic measures
4. Verify outputs (`src/f1d/text/verify_step2.py`)
5. Output: `4_Outputs/2_Textual_Analysis/*/linguistic_variables_*.parquet`

**Stage 3: Financial Features**
1. V1 Methodology (`src/f1d/financial/v1/`): Legacy approach
   - `3.0_BuildFinancialFeatures.py` - Orchestrator
   - `3.1_FirmControls.py` - Firm-level financial controls
   - `3.2_MarketVariables.py` - Market returns, volatility, liquidity
   - `3.3_EventFlags.py` - Takeover events, CEO turnover
2. V2 Methodology (`src/f1d/financial/v2/`): Active hypothesis testing
   - `3.1_H1Variables.py` - Cash holdings, leverage controls
   - `3.2_H2Variables.py` - Investment efficiency variables
   - `3.3_H3Variables.py` - Payout policy variables
   - `3.4_H4_LeverageDiscipline.py` - Leverage discipline variables
   - `3.5_H5DispersionRegression.py` - Analyst dispersion
   - `3.6_H6CCCLRegression.py` - CCCL instrument data
   - `3.7_H7IlliquidityVariables.py` - Illiquidity measures
   - `3.8_H8TakeoverVariables.py` - Takeover hazard variables
   - Additional scripts: H9 regression variants
3. Output: `4_Outputs/3_Financial_V2/*/*.parquet`

**Stage 4: Econometric Analysis**
1. V1 Methodology (`src/f1d/econometric/v1/`): CEO clarity estimation
   - `4.1.1_EstimateCeoClarity.py` - CEO fixed effects estimation
   - `4.1.2_EstimateCeoClarity_Extended.py` - Extended model
   - `4.1.3_EstimateCeoClarity_Regime.py` - Firm-level regime
   - `4.1.4_EstimateCeoTone.py` - Tone estimation
   - `4.2_LiquidityRegressions.py` - IV liquidity analysis
   - `4.3_TakeoverHazards.py` - Survival analysis
   - `4.4_GenerateSummaryStats.py` - Summary statistics
2. V2 Methodology (`src/f1d/econometric/v2/`): Hypothesis testing regressions
   - `4.1_H1CashHoldingsRegression.py` - H1: Cash holdings test
   - `4.2_H2InvestmentEfficiencyRegression.py` - H2: Investment efficiency
   - `4.3_H3PayoutPolicyRegression.py` - H3: Payout policy
   - `4.4_H4_LeverageDiscipline.py` - H4: Leverage discipline
   - `4.5_H5DispersionRegression.py` - H5: Analyst dispersion
   - `4.6_H6CCCLRegression.py` - H6: CCCL instrument
   - `4.7_H7IlliquidityRegression.py` - H7: Illiquidity
   - `4.8_H8TakeoverRegression.py` - H8: Takeover hazards
   - `4.9_CEOFixedEffects.py` - CEO fixed effects estimation
   - `4.10_H2_PRiskUncertainty_Investment.py` - H2 extensions
   - `4.11_H9_Regression.py` - H9 additional tests
3. Output: `4_Outputs/4_Econometric_V2/*/*.parquet` + regression tables

**State Management:**
- All scripts use timestamped output directories: `4_Outputs/{script_name}/{YYYY-MM-DD_HHMMSS}/`
- Latest outputs accessible via `latest/` symlinks
- `get_latest_output_dir()` from `f1d.shared.path_utils` resolves latest
- State propagated through manifest linking (master_sample_manifest.parquet references downstream outputs)

## Key Abstractions

**Configuration Abstraction:**
- Purpose: Centralized settings management
- Examples: `src/f1d/shared/config/loader.py`, `src/f1d/shared/config/paths.py`
- Pattern: Pydantic settings classes + YAML loading + environment variable support

**Path Resolution:**
- Purpose: Deterministic output location resolution across scripts
- Examples: `src/f1d/shared/path_utils.py`
- Pattern: Timestamp-based directories with `get_latest_output_dir()` for latest
- Key functions: `get_latest_output_dir()`, `ensure_output_dir()`, `validate_input_file()`

**Logging Abstraction:**
- Purpose: Structured logging with dual terminal/file output
- Examples: `src/f1d/shared/observability_utils.py`, `src/f1d/shared/logging/`
- Pattern: `DualWriter` wraps `sys.stdout`, structlog with context binding
- Key functions: `configure_logging()`, `get_logger()`, `setup_script_logging()`

**Data Validation:**
- Purpose: Input/output validation with file existence checks
- Examples: `src/f1d/shared/data_validation.py`
- Pattern: Decorator-based validation + checksums

**Panel OLS Wrapper:**
- Purpose: Unified interface for panel regressions with fixed effects
- Examples: `src/f1d/shared/panel_ols.py`, `src/f1d/shared/regression_utils.py`
- Pattern: `run_panel_ols()` wraps `linearmodels.PanelOLS`
- Features: Entity/time effects, clustered SE, VIF checking, diagnostic extraction

## Entry Points

**Orchestrator Scripts:**
- Location: `src/f1d/sample/1.0_BuildSampleManifest.py` (Stage 1 orchestrator)
- Location: `src/f1d/financial/v1/3.0_BuildFinancialFeatures.py` (Stage 3 V1 orchestrator)
- Triggers: Direct script execution by user or pipeline runner
- Responsibilities: Orchestrate substeps sequentially, validate prerequisites, copy final outputs

**Stage Scripts (Direct Execution):**
- All numbered scripts: `src/f1d/sample/1.*.py`, `src/f1d/text/2.*.py`, `src/f1d/financial/v1/3.*.py`, `src/f1d/financial/v2/3.*.py`, `src/f1d/econometric/v1/4.*.py`, `src/f1d/econometric/v2/4.*.py`
- Triggers: Direct CLI execution, orchestrator subprocess calls
- Responsibilities: Load inputs, process data, write timestamped outputs, generate stats/logs

**Package Entry Point:**
- Location: `src/f1d/__init__.py`
- Triggers: Package imports (`from f1d import ...`)
- Responsibilities: Package version, public API re-exports (`get_latest_output_dir`, `run_panel_ols`)

## Error Handling

**Strategy:** Validation-first approach with dual-terminal/file logging

**Patterns:**
- **Prerequisite validation:** Scripts check inputs exist before processing (`check_prerequisites()`)
- **Path validation:** All file paths validated before use (`validate_input_file()`, `ensure_output_dir()`)
- **Output validation:** File existence required (`get_latest_output_dir()` checks for specific files)
- **Structured errors:** Custom exceptions (`PathValidationError`, `OutputResolutionError`)
- **Graceful degradation:** Missing data handled with NaN, not hard failures
- **Dual logging:** All output written to both terminal and log file simultaneously

## Cross-Cutting Concerns

**Logging:** Structured logging with structlog + context binding
- Configuration: `src/f1d/shared/logging/config.py`, `src/f1d/shared/logging/`
- Pattern: `get_logger()` with context, log levels from config/project.yaml
- Dual output: Terminal + file via `DualWriter` wrapper

**Validation:** Multi-level validation (files, data, dependencies)
- File validation: `src/f1d/shared/data_validation.py`
- Dependency checking: `src/f1d/shared/dependency_checker.py`
- CLI validation: `src/f1d/shared/cli_validation.py`, `src/f1d/shared/subprocess_validation.py`

**Observability:** Memory tracking, throughput measurement, anomaly detection
- Implementation: `src/f1d/shared/observability/`
- Memory: `get_process_memory_mb()`, `@track_memory_usage` decorator
- Throughput: `calculate_throughput()`, `stats["throughput"]` in all scripts
- Anomalies: `detect_anomalies_zscore()`, `detect_anomalies_iqr()`

**Data Determinism:** Random seed, thread count, input sorting configured
- Configuration: `config/project.yaml` sets `determinism.random_seed: 42`, `determinism.thread_count: 1`
- Enforcement: All sorting operations use explicit sort, parallel results sorted before aggregation

---

*Architecture analysis: 2026-02-15*
