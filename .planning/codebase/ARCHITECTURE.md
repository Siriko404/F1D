# Architecture

**Analysis Date:** 2026-03-15

## Pattern Overview

**Overall:** 4-Stage ETL Pipeline with Builder Pattern for Variable Construction

This is an academic research data pipeline for a PhD thesis analyzing how CEO speech uncertainty on earnings calls affects corporate financial outcomes. The pipeline processes raw financial data (Compustat, CRSP, IBES) and earnings call transcripts through a deterministic, reproducible 4-stage pipeline.

**Key Characteristics:**
- Strict 4-stage sequential pipeline: Sample Construction -> Text Processing -> Variable Building -> Econometric Analysis
- Builder pattern for variable construction: each financial/linguistic variable has a dedicated `VariableBuilder` subclass
- Singleton compute engines for expensive data loads (Compustat, CRSP, IBES)
- Timestamped output directories for full reproducibility
- Call-level unit of observation (one row per earnings call)
- Hypothesis-organized econometric modules (H1-H14)
- YAML-driven configuration with Pydantic validation and environment variable overrides

## Layers

**Configuration Layer:**
- Purpose: Load, validate, and cache project settings from YAML files
- Location: `src/f1d/shared/config/`
- Contains: `base.py` (Pydantic models), `loader.py` (caching), `paths.py` (path resolution), `datasets.py`, `step_configs.py`, `env.py`
- Depends on: `pydantic-settings`, `pyyaml`
- Used by: All pipeline stages via `get_config()` and `load_variable_config()`

**Sample Construction Layer (Stage 1):**
- Purpose: Build the master sample manifest linking transcripts to firms/CEOs
- Location: `src/f1d/sample/`
- Contains: `clean_metadata.py`, `link_entities.py`, `build_tenure_map.py`, `assemble_manifest.py`, `build_sample_manifest.py`
- Depends on: Raw inputs (`inputs/Earnings_Calls_Transcripts/`, `inputs/Execucomp/`, `inputs/CRSPCompustat_CCM/`)
- Used by: Stage 3 variable builders (ManifestFieldsBuilder)

**Text Processing Layer (Stage 2):**
- Purpose: Tokenize transcripts and compute linguistic variables (uncertainty, sentiment)
- Location: `src/f1d/text/`
- Contains: `tokenize_transcripts.py`, `build_linguistic_variables.py`
- Depends on: Stage 1 outputs, `inputs/LM_dictionary/`
- Used by: Stage 3 linguistic variable builders

**Variable Building Layer (Stage 3):**
- Purpose: Construct hypothesis-specific call-level panels by merging linguistic and financial variables
- Location: `src/f1d/variables/` (panel builders), `src/f1d/shared/variables/` (individual variable builders)
- Contains: Per-hypothesis panel builders (`build_h{N}_{name}_panel.py`) and ~80+ individual variable builders
- Depends on: Stage 1/2 outputs, raw financial data, compute engines
- Used by: Stage 4 econometric scripts

**Econometric Analysis Layer (Stage 4):**
- Purpose: Run fixed-effects panel regressions testing each hypothesis
- Location: `src/f1d/econometric/`
- Contains: Per-hypothesis regression scripts (`run_h{N}_{name}.py`), LaTeX table generation
- Depends on: Stage 3 panel outputs, `linearmodels.PanelOLS`
- Used by: Thesis draft (LaTeX tables/results)

**Shared Infrastructure:**
- Purpose: Cross-cutting utilities used by all stages
- Location: `src/f1d/shared/`
- Contains: `panel_ols.py` (regression runner), `path_utils.py` (directory resolution), `data_loading.py`, `data_validation.py`, `financial_utils.py`, `industry_utils.py`, `latex_tables.py`, `latex_tables_accounting.py`, `latex_tables_complete.py`, `iv_regression.py`, `regression_helpers.py`, `regression_validation.py`, `centering.py`, `string_matching.py`, `diagnostics.py`, `dual_writer.py`
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
- Depends on: `pandas`
- Used by: Stage 3/4 scripts at completion

## Data Flow

**Full Pipeline Flow:**

1. **Stage 1 - Sample Construction:** Raw transcript metadata + Execucomp + CCM link table -> cleaned metadata -> entity linking -> CEO tenure map -> `master_sample_manifest.parquet` (output: `outputs/1.4_AssembleManifest/{timestamp}/`)
2. **Stage 2 - Text Processing:** Transcripts + LM dictionary -> tokenization (C++ compiler for speed) -> word counts -> linguistic variables per call per year (output: `outputs/2_Textual_Analysis/{step}/{timestamp}/`)
3. **Stage 3 - Variable Building:** Manifest + linguistic variables + raw financial data (Compustat, CRSP, IBES) -> individual VariableBuilder classes load one column each -> merged on `file_name` with zero-row-delta enforcement -> hypothesis-specific panel parquet (output: `outputs/variables/{hypothesis}/{timestamp}/`)
4. **Stage 4 - Econometric Analysis:** Panel parquet -> prepare regression data (lead DV, complete cases, min-calls filter, sample assignment) -> PanelOLS with entity+time FE and firm-clustered SEs -> regression results + LaTeX tables + diagnostics CSV + markdown reports (output: `outputs/econometric/{hypothesis}/{timestamp}/`)

**Variable Building Flow (Stage 3 detail):**

1. Load `config/variables.yaml` for variable source paths
2. Instantiate `VariableBuilder` subclasses with config dicts
3. Each builder calls `.build(years, root_path)` returning `VariableResult(data, stats, metadata)`
4. Compute engines (`CompustatEngine`, `CRSPEngine`, `IBESDetailEngine`) load raw data once and cache
5. Panel builder merges all results on `file_name` (left join, zero-row-delta enforced via `ValueError`)
6. Lead variables computed via fiscal-year grouping and shift
7. Industry sample assigned (Main/Finance/Utility based on FF12 codes)

**State Management:**
- No runtime state persistence between stages -- each stage reads from disk
- Compute engines use module-level singleton caching within a single process
- Configuration cached via `_ConfigCache` singleton in `loader.py`
- All outputs are immutable timestamped directories

## Key Abstractions

**VariableBuilder (Base Class):**
- Purpose: Standard interface for constructing a single variable column from source data
- Base: `src/f1d/shared/variables/base.py`
- Pattern: Template Method -- subclasses implement `build()`, base provides `get_stats()`, `_finalize_data()` (winsorization), `resolve_source_dir()`, `load_year_file()`
- Returns: `VariableResult` dataclass with `data` (DataFrame), `stats` (VariableStats), `metadata` (dict)
- Examples: `src/f1d/shared/variables/cash_holdings.py`, `src/f1d/shared/variables/manager_qa_uncertainty.py`

**Compute Engines (Singleton Data Loaders):**
- Purpose: Load expensive raw data files once per process and cache
- Files: `src/f1d/shared/variables/_compustat_engine.py`, `src/f1d/shared/variables/_crsp_engine.py`, `src/f1d/shared/variables/_ibes_engine.py`, `src/f1d/shared/variables/_ibes_detail_engine.py`, `src/f1d/shared/variables/_linguistic_engine.py`, `src/f1d/shared/variables/_hassan_engine.py`, `src/f1d/shared/variables/_clarity_residual_engine.py`
- Pattern: Module-level singleton -- all individual builders (e.g., `SizeBuilder`, `LevBuilder`) share one `CompustatEngine` load

**ProjectConfig (Pydantic Settings):**
- Purpose: Type-safe, validated configuration loaded from YAML with env var overrides
- File: `src/f1d/shared/config/base.py`
- Pattern: Composite -- aggregates `DataSettings`, `PathsSettings`, `LoggingSettings`, `DeterminismSettings`, `ChunkProcessingSettings`, `StepsConfig`, `DatasetsConfig`
- Usage: `config = get_config(Path("config/project.yaml"))`

**Panel Builder Scripts:**
- Purpose: Orchestrate variable loading and merging for a specific hypothesis
- Location: `src/f1d/variables/build_h{N}_{name}_panel.py`
- Pattern: Each script imports the specific builders it needs, builds all variables, merges on `file_name`, creates lead/lag variables, assigns industry sample, saves panel
- Examples: `src/f1d/variables/build_h1_cash_holdings_panel.py`, `src/f1d/variables/build_h9_takeover_panel.py`

**Econometric Runner Scripts:**
- Purpose: Load a panel, run regressions across uncertainty measures and industry samples, generate outputs
- Location: `src/f1d/econometric/run_h{N}_{name}.py`
- Pattern: Load panel -> prepare data -> loop over (sample, measure) -> run PanelOLS -> save outputs (text, CSV, LaTeX, markdown)
- All scripts support `--dry-run` and `--panel-path` CLI arguments

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

**Utility Script:**
- Location: `scripts/compute_missing_sumstats.py`
- Purpose: Compute summary statistics for missing variables

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

## Cross-Cutting Concerns

**Logging:** Structured logging via `structlog` with `TeeOutput` for dual console+file output. Per-run log directories under `logs/{suite_name}/{timestamp}/`. Setup via `setup_run_logging()` in `src/f1d/shared/logging/config.py`.

**Validation:** Multi-layer: Pydantic for config validation, Pandera for DataFrame schemas (dependency present), custom checks for merge integrity (zero-row-delta), explicit column existence checks, fiscal year continuity validation.

**Winsorization:** Centralized in `src/f1d/shared/variables/winsorization.py` with two modes: `winsorize_by_year` (within-year percentile clipping) and `winsorize_pooled` (pooled across all years). Applied automatically via `VariableBuilder._finalize_data()` unless `_skip_winsorization = True`.

**Industry Classification:** FF12/FF48 Fama-French industry codes derived from SIC codes. Industry sample assignment (Main/Finance/Utility) in `src/f1d/shared/variables/panel_utils.py` via `assign_industry_sample()`. FF48 mapping loaded from `inputs/FF1248/Siccodes48.zip`.

**Determinism:** Enforced via `config/project.yaml` settings: `random_seed: 42`, `thread_count: 1`, `sort_inputs: true`. All outputs must be reproducible.

**Output Convention:** All outputs written to timestamped subdirectories: `outputs/{category}/{hypothesis}/{YYYY-MM-DD_HHMMSS}/`. Latest output resolved by `get_latest_output_dir()` in `src/f1d/shared/path_utils.py`.

---

*Architecture analysis: 2026-03-15*
