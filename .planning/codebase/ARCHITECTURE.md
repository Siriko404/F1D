# Architecture

**Analysis Date:** 2026-02-15

## Pattern Overview

**Overall:** 4-Stage Data Processing Pipeline with src-layout Package Structure

**Key Characteristics:**
- Linear pipeline stages (Sample → Text → Financial → Econometric)
- Versioned methodology variants (v1 and v2 are both active)
- Shared utilities layer for cross-cutting concerns
- Immutable inputs, reproducible outputs, timestamped execution
- PyPA-compliant src-layout package with proper namespace imports

## Layers

**Shared Utilities Layer (Tier 1):**
- Purpose: Cross-cutting utilities used across all pipeline stages
- Location: `src/f1d/shared/`
- Contains: Configuration, logging, data loading, validation, path utilities, regression helpers, observability
- Depends on: Third-party libraries (pandas, numpy, pydantic, structlog, linearmodels)
- Used by: All stage modules (sample, text, financial, econometric)

**Stage 1 - Sample Construction (Tier 2):**
- Purpose: Build master sample manifest from earnings call metadata
- Location: `src/f1d/sample/`
- Contains: Metadata cleaning, entity linking, tenure mapping, manifest assembly
- Depends on: `f1d.shared.*`, pandas, input data files
- Used by: Stage 2 (text), Stage 3 (financial), Stage 4 (econometric)

**Stage 2 - Text Processing (Tier 2):**
- Purpose: Tokenize transcripts and construct linguistic variables
- Location: `src/f1d/text/`
- Contains: Tokenization, word counting, variable construction, verification
- Depends on: `f1d.shared.*`, Stage 1 outputs (master_sample_manifest), LM dictionary
- Used by: Stage 4 (econometric)

**Stage 3 - Financial Features (Tier 2):**
- Purpose: Construct firm controls, market variables, and event flags
- Location: `src/f1d/financial/`
- Contains: V1 methodology (3.0-3.4) and V2 methodology (3.1-3.13)
- Depends on: `f1d.shared.*`, Stage 1 outputs, Compustat/CRSP/IBES/SDC data
- Used by: Stage 4 (econometric)

**Stage 4 - Econometric Analysis (Tier 2):**
- Purpose: Estimate CEO clarity, test hypotheses, generate summary statistics
- Location: `src/f1d/econometric/`
- Contains: V1 methodology (4.1-4.4) and V2 hypothesis testing (4.1-4.11)
- Depends on: `f1d.shared.*`, Stage 1 outputs, Stage 2 outputs (linguistic_variables), Stage 3 outputs
- Used by: Final research outputs (tables, reports)

## Data Flow

**Step 1: Sample Construction**

1. Load `Unified-info.parquet` from `inputs/Earnings_Calls_Transcripts/`
2. Clean metadata (deduplicate, resolve collisions, filter earnings calls 2002-2018)
3. Link entities via 4-tier strategy (PERMNO+date, CUSIP8+date, fuzzy name, ticker)
4. Build CEO tenure map from Execucomp data
5. Assemble master_sample_manifest.parquet with CEO/firm identifiers and FF12/FF48 industries
6. Output: `master_sample_manifest.parquet` in `outputs/1.4_AssembleManifest/`

**State Management:** Parquet files preserve intermediate state between steps

**Step 2: Text Processing**

1. Load `master_sample_manifest.parquet` and `speaker_data_*.parquet` files
2. Tokenize Q&A text for each call using Loughran-McDonald dictionary
3. Count word categories (Negative, Positive, Uncertainty, Litigious, Modal, Constraining)
4. Aggregate to call level and construct linguistic variables (e.g., Manager_QA_Uncertainty_pct)
5. Apply quality filters (minimum tokens, percentage ranges)
6. Output: `linguistic_variables_*.parquet` (per year) in `outputs/2_Textual_Analysis/`

**State Management:** Yearly parquet files enable incremental processing

**Step 3: Financial Features (V1)**

1. Load `master_sample_manifest.parquet`
2. **Firm Controls:** Compute Size, BM, Lev, ROA, EPS_Growth, CurrentRatio, RD_Intensity from Compustat
3. **Market Variables:** Compute StockRet, MarketRet, Volatility, Amihud, Corwin-Schultz from CRSP
4. **Event Flags:** Identify takeover events from SDC and CEO dismissals
5. Winsorize at 1%/99%, apply minimum window length filters
6. Output: `firm_controls_*.parquet`, `market_variables_*.parquet`, `event_flags_*.parquet` (per year) in `outputs/3_Financial_Features/`

**State Management:** Yearly parquet files enable incremental processing

**Step 3: Financial Features (V2)**

1. Load `master_sample_manifest.parquet`
2. Construct hypothesis-specific variables (H1-H9) with additional control sets
3. Apply enhanced transformations (e.g., Biddle investment residuals, policy risk variables)
4. Output: Hypothesis-specific parquet files in `outputs/3_Financial_V2/`

**State Management:** Per-hypothesis variable files support modular analysis

**Step 4: Econometric Analysis (V1)**

1. **CEO Clarity:** Estimate Manager_QA_Uncertainty_pct ~ C(ceo_id) + controls + FE
2. **Liquidity Regressions:** 2SLS with CCCL shift_intensity instrument
3. **Takeover Hazards:** Cox proportional hazards model on takeover events
4. **Summary Stats:** Generate descriptive statistics and correlation matrix
5. Output: `ceo_clarity_scores.parquet`, regression results, LaTeX tables in `outputs/4.*_*/`

**State Management:** CEO-level clarity scores persist across all regression specifications

**Step 4: Econometric Analysis (V2)**

1. **Hypothesis Testing:** Run 9 hypothesis-specific regressions (H1-H9)
2. Each hypothesis tests CEO clarity impact on different outcomes (cash holdings, investment, payout, etc.)
3. Output: Hypothesis-specific results in `outputs/4_Econometric_V2/`

**State Management:** Per-hypothesis results support flexible analysis

## Key Abstractions

**Package Namespace (f1d):**
- Purpose: Installable Python package following PyPA src-layout
- Examples: `src/f1d/__init__.py`, `src/f1d/shared/__init__.py`
- Pattern: All imports use `f1d.shared.*` namespace (no sys.path manipulation)

**Shared Utilities Abstraction:**
- Purpose: Reusable cross-cutting functionality
- Examples: `src/f1d/shared/config/`, `src/f1d/shared/logging/`, `src/f1d/shared/path_utils.py`
- Pattern: Tier 1 modules imported by all stage modules

**Stage Module Abstraction:**
- Purpose: Encapsulate pipeline stage logic
- Examples: `src/f1d/sample/1.1_CleanMetadata.py`, `src/f1d/text/tokenize_and_count.py`
- Pattern: Each script is a standalone module executable via `python -m f1d.<module_path>`

**Configuration Abstraction:**
- Purpose: Type-safe configuration management with pydantic-settings
- Examples: `src/f1d/shared/config/base.py`, `config/project.yaml`
- Pattern: Load via `from f1d.shared.config import get_config`, override with environment variables

**Output Schema Abstraction:**
- Purpose: Validate outputs with Pandera schemas
- Examples: `src/f1d/shared/output_schemas.py`
- Pattern: Call `validate_*` functions before writing outputs

**Merge Validation Abstraction:**
- Purpose: Safe pandas merge with logging and validation
- Examples: `src/f1d/shared/data_loading.py` - `safe_merge()` function
- Pattern: Use `safe_merge()` instead of `pd.merge()` for all dataframe joins

## Entry Points

**Pipeline Scripts (Module Execution):**
- Location: `src/f1d/sample/`, `src/f1d/text/`, `src/f1d/financial/`, `src/f1d/econometric/`
- Triggers: Manual execution via `python -m f1d.<module_path>`
- Responsibilities: Each script performs one pipeline step, reads config, logs progress, writes outputs

**Sample Construction Entry Points:**
- `python -m f1d.sample.1.1_CleanMetadata` - Clean Unified-info metadata
- `python -m f1d.sample.1.2_LinkEntities` - Link calls to firms via 4-tier strategy
- `python -m f1d.sample.1.3_BuildTenureMap` - Build CEO tenure panel from Execucomp
- `python -m f1d.sample.1.4_AssembleManifest` - Assemble final sample manifest

**Text Processing Entry Points:**
- `python -m f1d.text.tokenize_and_count` - Tokenize and count LM dictionary words
- `python -m f1d.text.construct_variables` - Construct linguistic variables
- `python -m f1d.text.verify_step2` - Validate Step 2 outputs

**Financial Features Entry Points (V1):**
- `python -m f1d.financial.v1.3.0_BuildFinancialFeatures` - Orchestrator for all V1 features
- `python -m f1d.financial.v1.3.1_FirmControls` - Compute firm controls
- `python -m f1d.financial.v1.3.2_MarketVariables` - Compute market variables
- `python -m f1d.financial.v1.3.3_EventFlags` - Create takeover/dismissal flags

**Financial Features Entry Points (V2):**
- `python -m f1d.financial.v2.3.1_H1Variables` - H1 cash holdings variables
- `python -m f1d.financial.v2.3.2_H2Variables` - H2 investment efficiency variables
- `python -m f1d.financial.v2.3.3_H3Variables` - H3 payout policy variables
- `python -m f1d.financial.v2.3.5_H5Variables` - H5 dispersion variables
- `python -m f1d.financial.v2.3.6_H6Variables` - H6 CCCL regression variables
- `python -m f1d.financial.v2.3.7_H7IlliquidityVariables` - H7 illiquidity variables
- `python -m f1d.financial.v2.3.8_H8TakeoverVariables` - H8 takeover variables

**Econometric Analysis Entry Points (V1):**
- `python -m f1d.econometric.v1.4.1_EstimateManagerClarity` - Estimate CEO fixed effects
- `python -m f1d.econometric.v1.4.1.1_EstimateCeoClarity` - CEO-specific clarity
- `python -m f1d.econometric.v1.4.1.2_EstimateCeoClarity_Extended` - Extended controls
- `python -m f1d.econometric.v1.4.1.3_EstimateCeoClarity_Regime` - Firm-level regime
- `python -m f1d.econometric.v1.4.1.4_EstimateCeoTone` - CEO tone estimation
- `python -m f1d.econometric.v1.4.2_LiquidityRegressions` - IV liquidity analysis
- `python -m f1d.econometric.v1.4.3_TakeoverHazards` - Cox proportional hazards
- `python -m f1d.econometric.v1.4.4_GenerateSummaryStats` - Descriptive statistics

**Econometric Analysis Entry Points (V2):**
- `python -m f1d.econometric.v2.4.1_H1CashHoldingsRegression` - Test H1 cash holdings
- `python -m f1d.econometric.v2.4.2_H2InvestmentEfficiencyRegression` - Test H2 investment
- `python -m f1d.econometric.v2.4.3_H3PayoutPolicyRegression` - Test H3 payout policy
- `python -m f1d.econometric.v2.4.4_H4_LeverageDiscipline` - Test H4 leverage
- `python -m f1d.econometric.v2.4.5_H5DispersionRegression` - Test H5 dispersion
- `python -m f1d.econometric.v2.4.6_H6CCCLRegression` - Test H6 CCCL instrument
- `python -m f1d.econometric.v2.4.7_H7IlliquidityRegression` - Test H7 illiquidity
- `python -m f1d.econometric.v2.4.8_H8TakeoverRegression` - Test H8 takeover
- `python -m f1d.econometric.v2.4.9_CEOFixedEffects` - CEO fixed effects estimation
- `python -m f1d.econometric.v2.4.10_H2_PRiskUncertainty_Investment` - H2 policy risk interaction
- `python -m f1d.econometric.v2.4.11_H9_Regression` - H9 comprehensive regression

**Test Entry Points:**
- Location: `tests/unit/`, `tests/integration/`, `tests/regression/`, `tests/performance/`, `tests/verification/`
- Triggers: `pytest` command
- Responsibilities: Unit tests, integration tests, regression tests, performance tests, verification tests

## Error Handling

**Strategy:** Specific exception types with logging using structlog

**Patterns:**
- `safe_merge()` wrapper validates merge keys and logs statistics
- Custom exceptions in `panel_ols.py`: `CollinearityError`, `MulticollinearityError`
- Pandera schema validation raises `SchemaError` with detailed messages
- `load_validated_parquet()` validates file existence and schema
- `OutputResolutionError` raised when output directory cannot be resolved

## Cross-Cutting Concerns

**Logging:** structlog with `DualWriter` for simultaneous console and file output
- Configuration in `src/f1d/shared/logging/`
- Logs written to `logs/<script_name>/<timestamp>.log`
- Structured logs with context (script, phase, step)

**Validation:** Pandera schemas for output validation, data validation utilities
- `src/f1d/shared/data_validation.py` - load and validation functions
- `src/f1d/shared/output_schemas.py` - Pandera schemas for all outputs
- `safe_merge()` validates merge operations

**Authentication:** Not applicable (local data processing, no external services)

**Observability:** Memory tracking, throughput measurement, anomaly detection
- `src/f1d/shared/observability/` - tracking utilities
- `src/f1d/shared/chunked_reader.py` - memory-aware chunked processing
- Stats JSON files with memory_mb, throughput_mb_s, anomaly detection

**Configuration:** Centralized YAML config with pydantic-settings and environment variable overrides
- `config/project.yaml` - main configuration file
- `src/f1d/shared/config/` - configuration classes and loaders
- Environment variable support: `F1D_DATA__YEAR_START` format

---

*Architecture analysis: 2026-02-15*
