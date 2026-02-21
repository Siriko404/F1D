# Architecture

**Analysis Date:** 2026-02-20

## Pattern Overview

**Overall:** 4-Stage Sequential Data Processing Pipeline (ETL + Research Analysis)

**Key Characteristics:**
- Each stage consumes outputs from the prior stage via timestamped Parquet directories
- Scripts are standalone CLI executables — no web server, no API, no daemon processes
- All state is persisted to disk between stages; no shared in-memory state across scripts
- Deterministic by design: fixed random seed (42), single thread, sorted inputs
- `outputs/{step_id}/{timestamp}/` directory pattern for every stage output; `get_latest_output_dir()` resolves `latest` symlink-style

## Layers

**Tier 1 – Shared Core (`src/f1d/shared/`):**
- Purpose: Reusable utilities consumed by every stage. No business logic.
- Location: `src/f1d/shared/`
- Contains: Config loading, path utilities, data loading helpers, panel OLS engine, variable builders base classes, observability/logging, string matching, regression utilities
- Depends on: External libraries only (pydantic-settings, pandas, linearmodels, structlog)
- Used by: All Tier 2 stage modules

**Tier 2 – Stage Modules (`src/f1d/sample/`, `src/f1d/text/`, `src/f1d/variables/`, `src/f1d/econometric/`):**
- Purpose: Business logic for each of the 4 research pipeline stages
- Location: `src/f1d/{stage}/`
- Contains: Standalone Python CLI scripts (each prefixed with step ID e.g. `1.1_`, `2.2_`)
- Depends on: `src/f1d/shared/`, external data in `inputs/`, prior-stage outputs in `outputs/`
- Used by: Researchers running scripts directly; integration tests

**Tier 1 Sub-layer – Variable Builders (`src/f1d/shared/variables/`):**
- Purpose: One module per financial/linguistic variable. Each builder returns a `VariableResult` (DataFrame + stats + metadata)
- Location: `src/f1d/shared/variables/`
- Contains: ~60 individual builder classes plus two private compute engines (`_compustat_engine.py`, `_crsp_engine.py`, `_hassan_engine.py`, `_ibes_engine.py`)
- Depends on: raw `inputs/` Parquet files; Stage 2 outputs for linguistic variables
- Used by: Stage 3 panel builders in `src/f1d/variables/`

**Configuration Layer (`src/f1d/shared/config/`):**
- Purpose: Type-safe YAML-based config with env var overrides
- Location: `src/f1d/shared/config/`
- Contains: `base.py` (ProjectConfig), `loader.py` (get_config, caching), `paths.py`, `datasets.py`, `step_configs.py`, `hashing.py`, `string_matching.py`
- Depends on: `config/project.yaml`, `config/variables.yaml`
- Used by: Every stage module

## Data Flow

**Stage 1 – Sample Construction:**
1. `src/f1d/sample/clean_metadata.py` reads `inputs/Earnings_Calls_Transcripts/Unified-info.parquet`, deduplicates, filters earnings calls (event_type='1', 2002–2018) → `outputs/1.1_CleanMetadata/{ts}/metadata_cleaned.parquet`
2. `src/f1d/sample/link_entities.py` resolves CCM links (Compustat gvkey) → `outputs/1.2_LinkEntities/{ts}/`
3. `src/f1d/sample/build_tenure_map.py` constructs CEO tenure timeline → `outputs/1.3_BuildTenureMap/{ts}/`
4. `src/f1d/sample/assemble_manifest.py` assembles final call-CEO-firm manifest → `outputs/1.4_AssembleManifest/{ts}/master_sample_manifest.parquet`

**Stage 2 – Text Processing:**
1. `src/f1d/text/tokenize_transcripts.py` reads raw speaker_data Parquet files, applies LM dictionary tokenization → `outputs/2_Textual_Analysis/2.1_TokenizeAndCount/{ts}/`
2. `src/f1d/text/build_linguistic_variables.py` aggregates word counts into call-level linguistic measures → `outputs/2_Textual_Analysis/2.2_Variables/{ts}/linguistic_variables_{year}.parquet`

**Stage 3 – Variable Panel Construction:**
1. Each `src/f1d/variables/build_{hypothesis}_panel.py` script independently:
   - Loads Stage 1 manifest + Stage 2 linguistic variables
   - Invokes `VariableBuilder.build()` for each needed financial/CRSP/IBES variable
   - Merges all variables onto the call-level manifest via `file_name` key (zero row-delta enforced)
   - Saves `outputs/variables/{hypothesis}/{ts}/{hypothesis}_panel.parquet`
2. Private engines (`_compustat_engine.py`, `_crsp_engine.py`) load raw inputs once per process and cache; individual builders call `engine.get_data()`

**Stage 4 – Econometric Analysis:**
1. Each `src/f1d/econometric/test_{hypothesis}.py` script:
   - Loads Stage 3 panel via `get_latest_output_dir()`
   - Runs `PanelOLS` (from `linearmodels`) with firm + year fixed effects, HC1 standard errors
   - Produces `.txt` regression output, `.csv` diagnostics, `.tex` LaTeX table, `.md` report
   - Outputs go to `outputs/econometric/{hypothesis}/{ts}/`

**State Management:**
- No runtime state. Every script is stateless; all state is in Parquet files on disk.
- `get_latest_output_dir()` in `src/f1d/shared/path_utils.py` resolves the latest timestamped subdirectory for inter-stage references

## Key Abstractions

**VariableBuilder / VariableResult:**
- Purpose: Uniform interface for computing any single variable (financial, linguistic, IBES)
- Examples: `src/f1d/shared/variables/size.py`, `src/f1d/shared/variables/ceo_qa_uncertainty.py`, `src/f1d/shared/variables/earnings_surprise.py`
- Pattern: `class XBuilder(VariableBuilder): def build(self, years, root_path) -> VariableResult`

**Private Compute Engines:**
- Purpose: Load large raw Parquet files ONCE per process; cache and share across all builder instances
- Examples: `src/f1d/shared/variables/_compustat_engine.py` (CompustatEngine), `src/f1d/shared/variables/_crsp_engine.py` (CRSPEngine), `src/f1d/shared/variables/_ibes_engine.py`
- Pattern: `Engine.get_data()` returns cached DataFrame; individual builders call engine, select columns

**ProjectConfig:**
- Purpose: Root pydantic-settings config object; loaded once from `config/project.yaml`; env vars with `F1D_` prefix override YAML values
- Examples: `src/f1d/shared/config/base.py`
- Pattern: `config = get_config()` (cached singleton via `src/f1d/shared/config/loader.py`)

**Timestamped Output Pattern:**
- Purpose: Reproducibility – every run creates a new `YYYY-MM-DD_HHMMSS` subdirectory
- Pattern: `ensure_output_dir(base / step_id / datetime.now().strftime(...))` → `get_latest_output_dir(base / step_id)` resolves the most recent run
- Utilities: `src/f1d/shared/path_utils.py`

**DualWriter:**
- Purpose: Tee stdout to both console and a `{ts}.log` file inside the run's log directory
- Location: `src/f1d/shared/observability/logging.py` (re-exported via `src/f1d/shared/observability_utils.py` and `src/f1d/shared/dual_writer.py`)

## Entry Points

**Stage 1 – Sample Construction Orchestrator:**
- Location: `src/f1d/sample/build_sample_manifest.py`
- Triggers: `python -m f1d.sample.build_sample_manifest` or direct CLI
- Responsibilities: Calls substeps 1.1–1.4 via subprocess; orchestrates the full sample build

**Stage 1 Sub-scripts:**
- `src/f1d/sample/clean_metadata.py` (Step 1.1)
- `src/f1d/sample/link_entities.py` (Step 1.2)
- `src/f1d/sample/build_tenure_map.py` (Step 1.3)
- `src/f1d/sample/assemble_manifest.py` (Step 1.4)

**Stage 2 – Text Processing:**
- `src/f1d/text/tokenize_transcripts.py` (Step 2.1)
- `src/f1d/text/build_linguistic_variables.py` (Step 2.2)

**Stage 3 – Panel Builders (one per hypothesis):**
- `src/f1d/variables/build_ceo_clarity_panel.py`
- `src/f1d/variables/build_ceo_clarity_extended_panel.py`
- `src/f1d/variables/build_ceo_tone_panel.py`
- `src/f1d/variables/build_manager_clarity_panel.py`
- `src/f1d/variables/build_h1_cash_holdings_panel.py` through `build_h8_policy_risk_panel.py`
- `src/f1d/variables/build_takeover_panel.py`

**Stage 4 – Econometric Tests (one per hypothesis):**
- `src/f1d/econometric/test_ceo_clarity.py`
- `src/f1d/econometric/test_ceo_clarity_extended.py`
- `src/f1d/econometric/test_ceo_clarity_regime.py`
- `src/f1d/econometric/test_ceo_tone.py`
- `src/f1d/econometric/test_manager_clarity.py`
- `src/f1d/econometric/test_h1_cash_holdings.py` through `test_h8_policy_risk.py`
- `src/f1d/econometric/test_takeover_hazards.py`
- `src/f1d/econometric/generate_summary_stats.py`

## Error Handling

**Strategy:** Fail-fast with informative messages. Scripts exit with non-zero code on any unrecoverable error. No silent swallowing of exceptions.

**Patterns:**
- `validate_input_file()` / `validate_output_path()` in `src/f1d/shared/path_utils.py` raise `FileNotFoundError` or `OutputResolutionError` before any processing begins
- `safe_merge()` in `src/f1d/shared/data_loading.py` logs row counts before/after and raises on unexpected row deltas
- `get_latest_output_dir()` raises `OutputResolutionError` if no timestamped subdirectory exists
- Pydantic `ValidationError` raised at config load time for invalid YAML or env vars
- Custom exceptions: `CollinearityError`, `MulticollinearityError` in `src/f1d/shared/panel_ols.py`

## Cross-Cutting Concerns

**Logging:**
- `DualWriter` class tees all print output to console + timestamped `.log` file in `logs/{step_id}/{ts}.log`
- Structured logging via `structlog` available through `src/f1d/shared/logging/` package; `configure_logging()` in `src/f1d/shared/logging/config.py`

**Validation:**
- Config: pydantic-settings validators in `src/f1d/shared/config/base.py` (year range, log level patterns, etc.)
- Data: `src/f1d/shared/data_validation.py` for DataFrame schema checks; `src/f1d/shared/env_validation.py` for environment
- CLI: `src/f1d/shared/cli_validation.py`, `src/f1d/shared/subprocess_validation.py`

**Determinism:**
- `config.determinism.random_seed = 42`, `sort_inputs = True`, `thread_count = 1`
- All scripts sort inputs before processing; numpy/pandas operations use fixed seed where random

**Observability:**
- `src/f1d/shared/observability/` package: stats, anomaly detection (z-score, IQR), memory tracking, throughput calculation, per-step stats functions (e.g. `compute_step31_input_stats`)
- Outputs include `stats.json` / `report_stepX_Y.md` Markdown summaries per run

---

*Architecture analysis: 2026-02-20*
