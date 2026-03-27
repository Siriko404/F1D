# Architecture

**Analysis Date:** 2026-03-25

## Pattern Overview

**Overall:** 4-Stage ETL Pipeline with Builder Pattern for Variable Construction

This is an academic research data pipeline for a PhD thesis analyzing how CEO speech uncertainty on earnings calls affects corporate financial outcomes. The pipeline processes raw financial data (Compustat, CRSP, IBES) and earnings call transcripts through a deterministic, reproducible 4-stage pipeline. The codebase currently contains **21 active hypothesis suites** producing 21 table entries for the thesis.

**Key Characteristics:**
- Strict 4-stage sequential pipeline: Sample Construction -> Text Processing -> Variable Building -> Econometric Analysis
- Builder pattern for variable construction: each financial/linguistic variable has a dedicated `VariableBuilder` subclass (~90 builders)
- 7 singleton compute engines for expensive data loads (Compustat, CRSP, IBES, IbesDetail, Linguistic, Hassan, ClarityResidual)
- Timestamped output directories for full reproducibility
- Call-level unit of observation (one row per earnings call, keyed by `file_name`)
- Hypothesis-organized econometric modules with 22 active runner scripts
- YAML-driven configuration with Pydantic validation and environment variable overrides
- Three suite archetypes: standard (8-column), moderation/channel, and specialized (Cox PH, Probit)

## Layers

**Configuration Layer:**
- Purpose: Load, validate, and cache project settings from YAML files
- Location: `src/f1d/shared/config/`
- Contains: `base.py` (Pydantic models), `loader.py` (caching via `_ConfigCache`), `paths.py` (path resolution), `datasets.py`, `step_configs.py`, `env.py`, `hashing.py`, `string_matching.py`
- Depends on: `pydantic-settings`, `pyyaml`
- Used by: All pipeline stages via `get_config()` and `load_variable_config()`

**Sample Construction Layer (Stage 1):**
- Purpose: Build the master sample manifest linking transcripts to firms/CEOs
- Location: `src/f1d/sample/`
- Contains: `clean_metadata.py`, `link_entities.py`, `build_tenure_map.py`, `assemble_manifest.py`, `build_sample_manifest.py`, `utils.py`
- Depends on: Raw inputs (`inputs/Earnings_Calls_Transcripts/`, `inputs/Execucomp/`, `inputs/CRSPCompustat_CCM/`)
- Used by: Stage 3 variable builders (ManifestFieldsBuilder)
- Output: `outputs/1.4_AssembleManifest/{timestamp}/master_sample_manifest.parquet`

**Text Processing Layer (Stage 2):**
- Purpose: Tokenize transcripts and compute linguistic variables (uncertainty, sentiment, modals)
- Location: `src/f1d/text/`
- Contains: `tokenize_transcripts.py`, `build_linguistic_variables.py`
- Depends on: Stage 1 outputs, `inputs/LM_dictionary/` (Loughran-McDonald)
- Used by: Stage 3 linguistic variable builders via `LinguisticEngine`
- Output: `outputs/2_Textual_Analysis/{step}/{timestamp}/linguistic_variables_{year}.parquet`

**Variable Building Layer (Stage 3):**
- Purpose: Construct hypothesis-specific call-level panels by merging linguistic and financial variables
- Location: `src/f1d/variables/` (19 panel builders), `src/f1d/shared/variables/` (~90 individual variable builders)
- Contains: Per-hypothesis panel builders (`build_h{N}_{name}_panel.py`) and individual variable builders
- Depends on: Stage 1/2 outputs, raw financial data, compute engines
- Used by: Stage 4 econometric scripts
- Output: `outputs/variables/{hypothesis}/{timestamp}/{hypothesis}_panel.parquet`

**Econometric Analysis Layer (Stage 4):**
- Purpose: Run fixed-effects panel regressions testing each hypothesis
- Location: `src/f1d/econometric/` (22 active runner scripts + 1 probit + 1 table helper)
- Contains: Per-hypothesis regression scripts (`run_h{N}_{name}.py`), LaTeX table generation
- Depends on: Stage 3 panel outputs, `linearmodels.PanelOLS` (standard), `lifelines.CoxPHFitter` (H9), `statsmodels.Probit` (CEO presence)
- Used by: Thesis draft (LaTeX tables/results)
- Output: `outputs/econometric/{hypothesis}/{timestamp}/` (regression .txt, .tex, .csv, .md, run_manifest.json)

**Shared Infrastructure:**
- Purpose: Cross-cutting utilities used by all stages
- Location: `src/f1d/shared/`
- Contains:
  - `panel_ols.py` — `run_panel_ols()` with entity+time FE and firm-clustered SEs
  - `iv_regression.py` — 2SLS with instrument diagnostics (used by H6 CCCL)
  - `path_utils.py` — `get_latest_output_dir()`, `ensure_output_dir()`, timestamp validation
  - `data_loading.py`, `data_validation.py` — Generic data loading and validation
  - `financial_utils.py`, `industry_utils.py` — Financial calculation and industry classification
  - `latex_tables.py` — Basic LaTeX table generation (coefficient + SE format)
  - `latex_tables_accounting.py` — Accounting Review style (Estimate + t-value, no stars)
  - `latex_tables_complete.py` — Complete multi-panel LaTeX tables with significance stars
  - `regression_helpers.py`, `regression_validation.py` — Regression utilities
  - `centering.py` — Variable centering/standardization for moderation suites
  - `string_matching.py` — Fuzzy string matching via `rapidfuzz`
  - `diagnostics.py` — Model diagnostics (VIF, condition number)
  - `dual_writer.py` — Dual console+file output
  - `chunked_reader.py` — Memory-efficient chunked file reading
  - `cli_validation.py`, `env_validation.py`, `subprocess_validation.py` — Validation utilities
  - `metadata_utils.py`, `output_schemas.py`, `reporting_utils.py`, `sample_utils.py`
  - `dependency_checker.py` — Dependency verification
- Depends on: `pandas`, `numpy`, `linearmodels`, `statsmodels`
- Used by: All stages

**Observability Layer:**
- Purpose: Runtime monitoring, memory tracking, throughput logging
- Location: `src/f1d/shared/observability/`
- Contains: `anomalies.py`, `files.py`, `logging.py`, `memory.py`, `stats.py`, `throughput.py`
- Depends on: `psutil`, `structlog`
- Used by: Pipeline scripts during execution

**Logging Layer:**
- Purpose: Structured logging with file + console output, per-run log directories
- Location: `src/f1d/shared/logging/`
- Contains: `config.py` (structlog setup, TeeOutput), `context.py`, `handlers.py`
- Depends on: `structlog`
- Used by: All pipeline stages via `setup_run_logging()`

**Output/Reporting Layer:**
- Purpose: Generate run manifests, attrition tables, summary statistics for reproducibility
- Location: `src/f1d/shared/outputs/`
- Contains: `manifest_generator.py` (run_manifest.json), `attrition_table.py`
- Used by: Stage 3/4 scripts at completion

**Table Generation Layer:**
- Purpose: Generate all 21 publication-ready LaTeX tables from regression output .txt files
- Location: `outputs/generate_all_tables.py`
- Contains: Suite definitions with table metadata, 3 generator types (standard, moderation, H0.3/special)
- Depends on: Stage 4 regression output .txt files
- Output: LaTeX .tex files ready for thesis inclusion

**Reporting Layer:**
- Purpose: Generate summary statistics
- Location: `src/f1d/reporting/`
- Contains: `generate_summary_stats.py`

## Data Flow

**Full Pipeline Flow:**

1. **Stage 1 - Sample Construction:** Raw transcript metadata + Execucomp + CCM link table -> cleaned metadata -> entity linking -> CEO tenure map -> `master_sample_manifest.parquet` (output: `outputs/1.4_AssembleManifest/{timestamp}/`)
2. **Stage 2 - Text Processing:** Transcripts + LM dictionary -> tokenization (C++ compiler for speed) -> word counts -> linguistic variables per call per year (output: `outputs/2_Textual_Analysis/{step}/{timestamp}/`)
3. **Stage 3 - Variable Building:** Manifest + linguistic variables + raw financial data (Compustat, CRSP, IBES) -> individual VariableBuilder classes load one column each -> merged on `file_name` with zero-row-delta enforcement -> hypothesis-specific panel parquet (output: `outputs/variables/{hypothesis}/{timestamp}/`)
4. **Stage 4 - Econometric Analysis:** Panel parquet -> prepare regression data (lead DV, complete cases, min-calls filter, sample assignment) -> PanelOLS with entity+time FE and firm-clustered SEs -> regression results + LaTeX tables + diagnostics CSV + markdown reports (output: `outputs/econometric/{hypothesis}/{timestamp}/`)
5. **Table Generation:** Regression output .txt files -> `outputs/generate_all_tables.py` -> 21 publication-ready LaTeX tables

**Variable Building Flow (Stage 3 detail):**

1. Load `config/variables.yaml` for variable source paths
2. Instantiate `VariableBuilder` subclasses with config dicts
3. Each builder calls `.build(years, root_path)` returning `VariableResult(data, stats, metadata)`
4. Compute engines (`CompustatEngine`, `CRSPEngine`, `IbesDetailEngine`, etc.) load raw data once and cache
5. Panel builder merges all results on `file_name` (left join, zero-row-delta enforced via `ValueError`)
6. Lead variables computed via fiscal-year grouping and shift (consecutive-year validated)
7. Industry sample assigned (Main/Finance/Utility based on FF12 codes)

**Econometric Flow (Stage 4 detail):**

For standard suites (H1, H2, H4, H5, H5b, H12, H12Q, H13, H14, H15, H16):
1. Load panel parquet from `outputs/variables/{suite}/latest/`
2. Apply sample filter (Main only: `industry_sample == 'Main'`)
3. Prepare regression data: compute lead DV, apply min-calls filter, set multi-index `(gvkey, fyearq_int)`
4. Run 8-column specification matrix: 4 IVs simultaneous, 2 DV variants (contemporaneous + lead), 2 FE types (Industry+FY / Firm+FY), 2 control sets (Base / Extended)
5. Lead specs include lagged DV as unified control row
6. Save outputs: regression .txt per column, diagnostics .csv, summary stats .csv/.tex, report .md, run_manifest.json, LaTeX table

For moderation suites (H1.1, H1.2, H6, H11, H11-Lag, H11-Lead, H13.1):
1. Load parent suite's panel, merge external moderator data at load time
2. Center interaction IV, z-score moderator on Main sample
3. Run reduced specification (2-4 columns) with interaction term
4. Key coefficient: interaction term (b3)

For H9 (Takeover Hazards):
1. Load call-to-call counting-process panel from Stage 3
2. Run Cox Proportional Hazards via `lifelines.CoxPHFitter`
3. Three models: All Takeovers, Cause-specific Uninvited, Cause-specific Friendly

**State Management:**
- No runtime state persistence between stages -- each stage reads from disk
- Compute engines use module-level singleton caching within a single process (thread-safe via `threading.Lock()`)
- Configuration cached via `_ConfigCache` singleton in `loader.py`
- All outputs are immutable timestamped directories
- Latest output resolved by `get_latest_output_dir()` which finds subdirectory with most matching files

## Key Abstractions

**VariableBuilder (Base Class):**
- Purpose: Standard interface for constructing a single variable column from source data
- Base: `src/f1d/shared/variables/base.py`
- Pattern: Template Method -- subclasses implement `build()`, base provides `get_stats()`, `_finalize_data()` (winsorization), `resolve_source_dir()`, `load_year_file()`
- Returns: `VariableResult` dataclass with `data` (DataFrame with `file_name` + variable column), `stats` (VariableStats), `metadata` (dict)
- ~90 concrete implementations in `src/f1d/shared/variables/`
- Winsorization: applied automatically via `_finalize_data()` unless `_skip_winsorization = True`

**VariableResult / VariableStats (Dataclasses):**
- Purpose: Standard return type from all builders
- `VariableResult`: `data` (DataFrame), `stats` (VariableStats), `metadata` (dict)
- `VariableStats`: `name`, `n`, `mean`, `std`, `min`, `p25`, `median`, `p75`, `max`, `n_missing`, `pct_missing`

**Compute Engines (7 Singleton Data Loaders):**
- Purpose: Load expensive raw data files once per process and cache, shared by all individual builders
- Thread-safe via `threading.Lock()` at module level
- Files:
  - `src/f1d/shared/variables/_compustat_engine.py` — Loads Compustat quarterly, computes ~30 accounting variables (Size, BM, ROA, CashHoldings, TobinsQ, CapexAt, etc.), FF48 codes, YTD-to-annual conversion for capxy/dvy/xrdy/saley. The largest engine (1,342 lines).
  - `src/f1d/shared/variables/_crsp_engine.py` — Loads CRSP daily stock files year-by-year, computes StockRet, MarketRet, Volatility, amihud_illiq over call windows. Date-bounded CCM PERMNO lookup.
  - `src/f1d/shared/variables/_ibes_engine.py` — Loads IBES Detail yearly files, computes consensus summary (NUMEST, MEANEST, STDEV, dispersion, earnings_surprise) linked via CUSIP->GVKEY through CCM.
  - `src/f1d/shared/variables/_ibes_detail_engine.py` — Loads raw individual analyst estimates for point-in-time dispersion computation. Used by H5 PostCallDispersion, H5b JohnsonDISP2.
  - `src/f1d/shared/variables/_linguistic_engine.py` — Loads Stage 2 linguistic variable parquets, applies per-year winsorization to all _pct columns. All textual builders query this engine.
  - `src/f1d/shared/variables/_hassan_engine.py` — Loads Hassan et al. (2019) PRisk quarterly CSV, aggregates to fiscal-year averages via rolling 366-day window. Reuses CompustatEngine for fiscal year-end dates. Used by H11.
  - `src/f1d/shared/variables/_clarity_residual_engine.py` — Loads clarity residuals from H0.3 econometric output. Used by H9 (ClarityCEO score).

**ProjectConfig (Pydantic Settings):**
- Purpose: Type-safe, validated configuration loaded from YAML with env var overrides
- File: `src/f1d/shared/config/base.py`
- Pattern: Composite -- aggregates `DataSettings`, `PathsSettings`, `LoggingSettings`, `DeterminismSettings`, `ChunkProcessingSettings`, `StepsConfig`, `DatasetsConfig`
- Usage: `config = get_config(Path("config/project.yaml"))`

**Panel Builder Scripts:**
- Purpose: Orchestrate variable loading and merging for a specific hypothesis
- Location: `src/f1d/variables/build_h{N}_{name}_panel.py` (19 active)
- Pattern: Each script imports the specific builders it needs, builds all variables, merges on `file_name`, creates lead/lag variables, assigns industry sample, saves panel
- Standard structure: `parse_arguments()` -> `build_panel()` -> `main()`
- All scripts support `--dry-run`, `--year-start`, `--year-end` CLI arguments

**Econometric Runner Scripts:**
- Purpose: Load a panel, run regressions across specifications, generate outputs
- Location: `src/f1d/econometric/run_h{N}_{name}.py` (22 active)
- Pattern: Load panel -> prepare data -> loop over specification matrix -> run PanelOLS -> save outputs
- All scripts support `--dry-run` and `--panel-path` CLI arguments
- Standard IVs: 4 uncertainty measures enter simultaneously (CEO_QA, CEO_Pres, Manager_QA, Manager_Pres)
- Panel index: `["gvkey", "fyearq_int"]` (fiscal year integer)
- Standard errors: firm-clustered (`clusters=gvkey`)

## Entry Points

**Panel Builder Scripts (Stage 3):**
- Location: `src/f1d/variables/build_h{N}_{name}_panel.py`
- Triggers: Run directly via `python -m f1d.variables.build_h1_cash_holdings_panel`
- Responsibilities: Load config, instantiate builders, merge variables, save panel parquet
- Root resolution: `Path(__file__).resolve().parents[3]` (3 levels up from `src/f1d/variables/`)

**Econometric Scripts (Stage 4):**
- Location: `src/f1d/econometric/run_h{N}_{name}.py`
- Triggers: Run directly via `python -m f1d.econometric.run_h1_cash_holdings`
- Responsibilities: Load panel, run regressions, save results + LaTeX tables + reports
- Root resolution: `Path(__file__).resolve().parents[3]`

**Sample Construction Scripts (Stage 1):**
- Location: `src/f1d/sample/` (`clean_metadata.py`, `link_entities.py`, `build_tenure_map.py`, `assemble_manifest.py`)
- Triggers: Run sequentially as pipeline steps

**Text Processing Scripts (Stage 2):**
- Location: `src/f1d/text/` (`tokenize_transcripts.py`, `build_linguistic_variables.py`)
- Triggers: Run after Stage 1

**Table Generation:**
- Location: `outputs/generate_all_tables.py`
- Purpose: Generate all 21 LaTeX tables from regression output .txt files

**Utility Scripts:**
- `scripts/compute_missing_sumstats.py` — Compute summary statistics for missing variables
- `src/f1d/econometric/ceo_presence_probit.py` — CEO presence characterization for H7 discussion
- `src/f1d/econometric/_save_latex_table_6col.py` — Helper for 6-column LaTeX table format

## Suite Inventory (21 Active Table Entries)

| Suite ID | Panel Builder | Runner | Type | DV |
|----------|--------------|--------|------|-----|
| H0.3 | `build_h0_3_ceo_clarity_extended_panel.py` | `run_h0_3_ceo_clarity_extended.py` | Clarity FE | Manager/CEO QA Uncertainty |
| H1 | `build_h1_cash_holdings_panel.py` | `run_h1_cash_holdings.py` | Standard 8-col | CashHoldings |
| H1.1 | (uses H1 panel) | `run_h1_1_cash_tsimm.py` | Moderation 2-col | CashHoldings (TNIC moderated) |
| H1.2 | (uses H1 panel) | `run_h1_2_cash_constraint.py` | Moderation 2-col | CashHoldings (credit constraint) |
| H2 | `build_h2_investment_panel.py` | `run_h2_investment.py` | Standard 8-col | InvestmentResidual |
| H4a/H4b | `build_h4_leverage_panel.py` | `run_h4_leverage.py` | Standard 16-col | BookLev / DebtToCapital |
| H5 | `build_h5_dispersion_panel.py` | `run_h5_dispersion.py` | Standard 4-col | PostCallDispersion |
| H5b | `build_h5b_johnson_disp_panel.py` | `run_h5b_johnson_disp.py` | Standard 8-col | JohnsonDISP2 |
| H6 | `build_h6_cccl_panel.py` | `run_h6_cccl.py` | IV/Moderation 4-col | QA/Pres Uncertainty (CCCL) |
| H7 | `build_h7_illiquidity_panel.py` | `run_h7_illiquidity.py` | Standard 4-col | delta_amihud |
| H9 | `build_h9_takeover_panel.py` | `run_h9_takeover_hazards.py` | Cox PH | Takeover hazard |
| H11 | `build_h11_prisk_uncertainty_panel.py` | `run_h11_prisk_uncertainty.py` | Moderation 4-col | QA/Pres Uncertainty (PRisk) |
| H11-Lag | `build_h11_prisk_uncertainty_lag_panel.py` | `run_h11_prisk_uncertainty_lag.py` | Moderation 8-col | PRiskQ_lag/lag2 |
| H11-Lead | `build_h11_prisk_uncertainty_lead_panel.py` | `run_h11_prisk_uncertainty_lead.py` | Moderation 8-col | PRiskQ_lead/lead2 (placebo) |
| H12 | `build_h12_div_intensity_panel.py` | `run_h12_div_intensity.py` | Standard 8-col | PayoutRatio |
| H12Q | `build_h12q_payout_panel.py` | `run_h12q_payout.py` | Standard 8-col | PayoutRatio_q |
| H13 | `build_h13_capex_panel.py` | `run_h13_capex.py` | Standard 8-col | CapexAt |
| H13.1 | (uses H13 panel) | `run_h13_1_competition.py` | Moderation 4-col | CapexAt (TNIC moderated) |
| H14 | `build_h14_bidask_spread_panel.py` | `run_h14_bidask_spread.py` | Standard 4-col | DSPREAD |
| H15 | `build_h15_repurchase_panel.py` | `run_h15_repurchase.py` | Standard 4-col | REPO_callqtr |
| H16 | `build_h16_rd_sales_panel.py` | `run_h16_rd_sales.py` | Standard 8-col | RDSales |

**Archived Suites:** H3 (distributional payout), H8 (replaced by H11), H10 (tone at top, not pursued), H0.1/H0.2/H0.5 (clarity variants), H13.2 (employment growth)

## Error Handling

**Strategy:** Fail-fast with descriptive ValueError/FileNotFoundError messages. No silent fallbacks for critical data issues.

**Patterns:**
- Zero-row-delta enforcement on all merges in panel builders: `if after_len != before_len: raise ValueError(...)` -- prevents silent fan-out from duplicate keys
- Duplicate `file_name` checks before merge: builder output and manifest both validated for uniqueness
- Missing column validation: explicit check for required columns with list of missing names in error message
- Minimum observation thresholds: skip regression if N < 100 with warning
- Fiscal year continuity validation: lead variables nulled for non-consecutive years (gap detection)
- `CollinearityError` / `MulticollinearityError` custom exceptions in `panel_ols.py`
- Configuration validation via Pydantic `field_validator` and `model_validator`
- Graceful degradation for VIF computation (try/except with warning)
- Memory-safe builder pattern: per-gvkey loops with explicit `gc.collect()` for large engines (CRSP, IBES Detail)

## Cross-Cutting Concerns

**Logging:** Structured logging via `structlog` with `TeeOutput` for dual console+file output. Per-run log directories under `logs/{suite_name}/{timestamp}/`. Setup via `setup_run_logging()` in `src/f1d/shared/logging/config.py`.

**Validation:** Multi-layer: Pydantic for config validation, custom checks for merge integrity (zero-row-delta), explicit column existence checks, fiscal year continuity validation. Pandera dependency present but not heavily used.

**Winsorization:** Centralized in `src/f1d/shared/variables/winsorization.py` with two modes: `winsorize_by_year` (within-year percentile clipping, for linguistic variables via `LinguisticEngine`) and `winsorize_pooled` (pooled across all years, applied by `VariableBuilder._finalize_data()`). Applied automatically unless `_skip_winsorization = True`.

**Industry Classification:** FF12/FF48 Fama-French industry codes derived from SIC codes. Industry sample assignment (Main/Finance/Utility) canonically defined in `src/f1d/shared/variables/panel_utils.py` via `assign_industry_sample()`. FF12 code 11 = Finance, FF12 code 8 = Utility, all others = Main. FF48 mapping loaded from `inputs/FF1248/Siccodes48.zip`.

**Fiscal Year Alignment:** `attach_fyearq()` in `src/f1d/shared/variables/panel_utils.py` uses backward `merge_asof` on `(gvkey, start_date)` to Compustat `datadate`, attaching `fyearq` (fiscal year integer). All suites use `fyearq_int` as the time FE index.

**Determinism:** Enforced via `config/project.yaml` settings: `random_seed: 42`, `thread_count: 1`, `sort_inputs: true`. All outputs must be reproducible.

**Output Convention:** All outputs written to timestamped subdirectories: `outputs/{category}/{hypothesis}/{YYYY-MM-DD_HHMMSS}/`. Latest output resolved by `get_latest_output_dir()` in `src/f1d/shared/path_utils.py`. Timestamp format validated by regex `^\d{4}-\d{2}-\d{2}_\d{6}$`.

**Moderation Suite Pattern:** Moderation suites (H1.1, H1.2, H13.1) reuse the parent suite's panel and merge external moderator data at runtime. The IV is mean-centered, the moderator is z-scored on the Main sample, and the interaction term is the product of centered IV and z-scored moderator. This avoids building separate panels for each moderation test.

---

*Architecture analysis: 2026-03-25*
