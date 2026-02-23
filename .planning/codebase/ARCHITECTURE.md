# Architecture

**Analysis Date:** 2026-02-21

## Pattern Overview

**Overall:** Four-Stage Sequential Data Pipeline with Centralized Shared Utilities

**Key Characteristics:**
- Strict stage dependency (Stage 1 -> Stage 2 -> Stage 3 -> Stage 4)
- Separation of domain-specific code (sample, text, variables, econometric) from shared utilities
- Variable builder pattern for composable feature construction
- Call-level panel design for hypothesis testing
- Deterministic output resolution via timestamped directories

## Layers

**Layer 1: Shared Utilities (Tier 1 - Strict Mode)**
- Purpose: Cross-cutting utilities, configuration, logging, and reusable components
- Location: `src/f1d/shared/`
- Contains:
  - `config/`: Pydantic configuration models with environment variable support
  - `logging/`: Structured logging with context propagation and dual output (console + file)
  - `variables/`: 50+ variable builders following `VariableBuilder` base class pattern
  - `observability/`: Memory tracking, throughput measurement, anomaly detection, file checksums
  - Core utilities: `panel_ols.py`, `iv_regression.py`, `data_validation.py`, `path_utils.py`, `chunked_reader.py`, `string_matching.py`
- Depends on: pandas, numpy, pydantic, structlog, linearmodels, statsmodels
- Used by: All stage-specific modules (sample, text, variables, econometric)

**Layer 2: Sample Construction (Stage 1)**
- Purpose: Build master sample manifest linking transcripts to firms
- Location: `src/f1d/sample/`
- Contains: `clean_metadata.py`, `link_entities.py`, `build_tenure_map.py`, `assemble_manifest.py`
- Depends on: `f1d.shared` (path_utils, string_matching, observability, config)
- Used by: Stage 2 text processing scripts

**Layer 3: Text Processing (Stage 2)**
- Purpose: Tokenize transcripts and compute linguistic measures
- Location: `src/f1d/text/`
- Contains: `tokenize_transcripts.py`, `build_linguistic_variables.py`
- Depends on: `f1d.shared` (chunked_reader, observability, config)
- Used by: Stage 3 panel builders

**Layer 4: Panel Builders (Stage 3)**
- Purpose: Assemble regression-ready panels by merging manifest + variables
- Location: `src/f1d/variables/`
- Contains: `build_h0_1_manager_clarity_panel.py`, `build_h0_2_ceo_clarity_panel.py`, `build_h0_3_ceo_clarity_extended_panel.py`, `build_h0_5_ceo_tone_panel.py`, `build_h1_cash_holdings_panel.py`, `build_h2_investment_panel.py`, `build_h3_payout_policy_panel.py`, `build_h4_leverage_panel.py`, `build_h5_dispersion_panel.py`, `build_h6_cccl_panel.py`, `build_h7_illiquidity_panel.py`, `build_h8_policy_risk_panel.py`, `build_h9_takeover_panel.py`, `build_h10_tone_at_top_panel.py`
- Depends on: `f1d.shared.variables` (all variable builders), `f1d.sample` (manifest output)
- Used by: Stage 4 econometric scripts

**Layer 5: Hypothesis Tests (Stage 4)**
- Purpose: Run econometric regressions and generate LaTeX tables
- Location: `src/f1d/econometric/`
- Contains: `run_h0_*.py`, `run_h1_cash_holdings.py`, `run_h2_investment.py`, `run_h3_payout_policy.py`, `run_h4_leverage.py`, `run_h5_dispersion.py`, `run_h6_cccl.py`, `run_h7_illiquidity.py`, `run_h8_policy_risk.py`, `run_h9_takeover_hazards.py`, `run_h10_tone_at_top.py`
- Depends on: `f1d.shared` (panel_ols, iv_regression, path_utils, latex_tables), `f1d.variables` (panel outputs)
- Used by: Reports, thesis analysis

## Data Flow

**Stage 1: Sample Construction Flow**

1. Clean metadata: `inputs/Earnings_Calls_Transcripts/` → `outputs/sample/1.1_CleanMetadata/{timestamp}/metadata_cleaned.parquet`
2. Link entities: Clean metadata + CCM linktable → Fuzzy matching → `outputs/sample/1.2_LinkEntities/{timestamp}/metadata_linked.parquet`
3. Build tenure map: Linked metadata → CEO tenure panel → `outputs/sample/1.3_BuildTenureMap/{timestamp}/master_tenure_map.parquet`
4. Assemble manifest: Tenure map → Unified manifest → `outputs/sample/1.4_AssembleManifest/{timestamp}/master_sample_manifest.parquet` (112,968 calls)

**Stage 2: Text Processing Flow**

1. Tokenize transcripts: Manifest + LM dictionary → Word counts per document → `outputs/text/2.1_TokenizeAndCount/{timestamp}/linguistic_counts_{year}.parquet`
2. Build linguistic variables: Token counts → Uncertainty/sentiment percentages → `outputs/text/2.2_Variables/{timestamp}/linguistic_variables_{year}.parquet`

**Stage 3: Panel Building Flow**

1. Load manifest from Stage 1 (`master_sample_manifest.parquet`)
2. Load variable builders from `f1d.shared.variables` (each returns one column)
3. Merge all variables onto manifest by `file_name` (zero-row-delta enforced)
4. Create lead variables where needed (e.g., `CashHoldings_lead` via fiscal year aggregation)
5. Assign industry sample (Main/Finance/Utility based on FF12 codes)
6. Save: `outputs/variables/{hypothesis}/{timestamp}/{hypothesis}_panel.parquet`

**State Management:**
- All intermediate outputs written to timestamped directories
- Latest output resolved via `get_latest_output_dir()` (timestamp comparison)
- No symlinks used - directory discovery by timestamp

## Key Abstractions

**VariableBuilder Pattern:**
- Purpose: Composable single-column feature construction
- Examples: `src/f1d/shared/variables/cash_holdings.py`, `size.py`, `lev.py`, `manager_qa_uncertainty.py`
- Pattern:
  - Inherit from `VariableBuilder` base class
  - Implement `build(years: range, root_path: Path) -> VariableResult`
  - Return `VariableResult(data, stats, metadata)` where data contains `file_name` + variable column
  - Auto-resolve timestamped source directories via `resolve_source_dir()`

**Private Data Engines (Singleton Pattern):**
- Purpose: Load expensive data sources once and cache
- Examples: `CompustatEngine`, `CRSPEngine`, `IbesEngine`, `HassanEngine` (in private modules under `variables/`)
- Pattern:
  - Module-level `_engine = None`
  - `get_engine()` function initializes if None, returns cached instance
  - All variable builders call same engine, ensuring single load per panel build

**Entity Linking (Tiered Matching Strategy):**
- Purpose: Match earnings call companies to CCM/CRSP identifiers
- Location: `src/f1d/sample/link_entities.py`
- Pattern:
  - Tier 1: PERMNO + date range (highest quality, link_quality=100)
  - Tier 2: CUSIP8 + date range (medium quality, link_quality=90)
  - Tier 3: Fuzzy name matching (lowest quality, link_quality=80)
  - Broadcast matched results to all related calls via dedup-index

**Panel Regression Interface:**
- Purpose: Standardized panel OLS with fixed effects
- Location: `src/f1d/shared/panel_ols.py`
- Pattern:
  - `run_panel_ols(df, dependent, exog, entity_col, time_col, cov_type, cluster_cols)`
  - Uses `linearmodels.PanelOLS` for estimation
  - Supports firm, year, industry fixed effects
  - Returns dict with coefficients, summary, diagnostics, warnings
  - VIF multicollinearity checking included

**Structured Logging:**
- Purpose: Dual-output (console + file) with context propagation
- Location: `src/f1d/shared/observability/logging.py` (DualWriter)
- Pattern:
  - `DualWriter(log_path)` wraps sys.stdout
  - Context propagation via `OperationContext` for request/operation metadata
  - Configured via `config/project.yaml` (level, format, timestamp_format)

## Entry Points

**Stage 1 Entry Points:**
- `python -m f1d.sample.clean_metadata` - Clean transcript metadata
- `python -m f1d.sample.link_entities` - Link companies to CCM/CRSP
- `python -m f1d.sample.build_tenure_map` - Build CEO tenure panel
- `python -m f1d.sample.assemble_manifest` - Assemble final sample manifest

**Stage 2 Entry Points:**
- `python -m f1d.text.tokenize_transcripts` - Tokenize transcripts using LM dictionary
- `python -m f1d.text.build_linguistic_variables` - Compute uncertainty/sentiment percentages

**Stage 3 Entry Points:**
- `python -m f1d.variables.build_h0_1_manager_clarity_panel` - Manager clarity panel
- `python -m f1d.variables.build_h0_2_ceo_clarity_panel` - CEO clarity panel
- `python -m f1d.variables.build_h1_cash_holdings_panel` - Cash holdings panel (with lead variable)
- `python -m f1d.variables.build_h2_investment_panel` - Investment efficiency panel
- `python -m f1d.variables.build_h3_payout_policy_panel` - Payout policy panel
- `python -m f1d.variables.build_h4_leverage_panel` - Leverage panel
- `python -m f1d.variables.build_h5_dispersion_panel` - Analyst dispersion panel
- `python -m f1d.variables.build_h6_cccl_panel` - CCCL instrument panel
- `python -m f1d.variables.build_h7_illiquidity_panel` - Illiquidity panel
- `python -m f1d.variables.build_h8_policy_risk_panel` - Policy risk panel
- `python -m f1d.variables.build_h9_takeover_panel` - Takeover hazard panel
- `python -m f1d.variables.build_h10_tone_at_top_panel` - Tone-at-top panel

**Stage 4 Entry Points:**
- `python -m f1d.econometric.run_h0_1_manager_clarity` - Manager clarity fixed effects regression
- `python -m f1d.econometric.run_h0_2_ceo_clarity` - CEO clarity fixed effects regression
- `python -m f1d.econometric.run_h0_3_ceo_clarity_extended` - Extended controls robustness
- `python -m f1d.econometric.run_h0_4_ceo_clarity_regime` - Regime analysis
- `python -m f1d.econometric.run_h0_5_ceo_tone` - CEO tone regressions
- `python -m f1d.econometric.run_h1_cash_holdings` - Cash holdings hypothesis test
- `python -m f1d.econometric.run_h2_investment` - Investment efficiency test
- `python -m f1d.econometric.run_h3_payout_policy` - Payout policy test
- `python -m f1d.econometric.run_h4_leverage` - Leverage test
- `python -m f1d.econometric.run_h5_dispersion` - Analyst dispersion test
- `python -m f1d.econometric.run_h6_cccl` - CCCL instrument IV regression
- `python -m f1d.econometric.run_h7_illiquidity` - Illiquidity regressions
- `python -m f1d.econometric.run_h8_policy_risk` - Policy risk interaction test
- `python -m f1d.econometric.run_h9_takeover_hazards` - Cox PH survival analysis
- `python -m f1d.econometric.run_h10_tone_at_top` - Tone-at-top Granger causality test
- `python -m f1d.reporting.generate_summary_stats` - Descriptive statistics

**Reporting Entry Point:**
- `python -m f1d.reporting.generate_summary_stats` - Generate summary tables

**Responsibilities:**
- Entry points are top-level modules with `if __name__ == "__main__"` blocks
- Each entry point defines argparse arguments (`--dry-run`, `--year-start`, `--year-end`, `--panel-path`)
- Dependency validation via `check_prerequisites()` before execution
- All write to timestamped output directories

## Error Handling

**Strategy:** Hard-fail with clear error messages + validation

**Patterns:**
- `ConfigError` (in `f1d.shared.config.loader`) for configuration issues
- `CollinearityError`, `MulticollinearityError` (in `f1d.shared.panel_ols`) for regression issues
- `ValueError` raised with descriptive messages for:
  - Missing required columns
  - Zero-row-delta violations during merges
  - Duplicate `file_name` in manifest or builder outputs
  - Missing input files
- Pre-execution validation via `check_prerequisites()` function
- Dry-run mode via `--dry-run` flag for validation without execution

## Cross-Cutting Concerns

**Logging:** Structured logging with `DualWriter` (console + file) and `OperationContext` (metadata propagation). Configured via `config/project.yaml` (level, format).

**Validation:** Multi-layer validation:
  - Input file existence via `validate_input_file()`
  - Output path creation via `ensure_output_dir()`
  - Prerequisites via `check_prerequisites()`
  - Column existence checks before regression
  - Panel integrity checks (zero-row-delta enforcement)

**Authentication:** Not applicable (no external authentication - all data is local files)

**Observability:** Memory tracking decorators (`@track_memory_usage`), throughput measurement, file checksums, anomaly detection (z-score, IQR), comprehensive statistics collection in all scripts.

---

*Architecture analysis: 2026-02-21*
