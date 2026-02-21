# Architecture

**Analysis Date:** 2026-02-21

## Pattern Overview

**Overall:** Four-Stage Pipeline with Data Engine Singletons

**Key Characteristics:**
- Sequential stage execution with timestamped outputs
- One module = one variable (each builder returns exactly one column)
- Zero row delta on merges (ValueError raised if panel length changes)
- Private data engine singletons for expensive data sources (Compustat, CRSP, IBES)
- Hard-fail on missing required variables

## Layers

**Stage 1: Sample Construction (`src/f1d/sample/`)**
- Purpose: Build analyst-CEO manifest linking transcripts to firms and executives
- Location: `src/f1d/sample/`
- Contains: `clean_metadata.py`, `link_entities.py`, `build_tenure_map.py`, `assemble_manifest.py`
- Depends on: Raw inputs (transcripts, CCM linktable, Execucomp)
- Used by: All subsequent stages

**Stage 2: Text Processing (`src/f1d/text/`)**
- Purpose: Tokenize transcripts and compute linguistic variables
- Location: `src/f1d/text/`
- Contains: `tokenize_transcripts.py`, `build_linguistic_variables.py`
- Depends on: Stage 1 manifest, LM dictionary
- Used by: Stage 3 panel builders

**Stage 3: Panel Builders (`src/f1d/variables/`)**
- Purpose: Merge manifest with all required variables for each hypothesis test
- Location: `src/f1d/variables/`
- Contains: `build_h{0-10}_*_panel.py` (15 panel builder scripts)
- Depends on: Stage 1 manifest, Stage 2 linguistic vars, shared variable builders
- Used by: Stage 4 econometric scripts

**Stage 4: Econometric Analysis (`src/f1d/econometric/`)**
- Purpose: Run hypothesis tests, extract fixed effects, generate LaTeX tables
- Location: `src/f1d/econometric/`
- Contains: `run_h{0-10}_*.py` (16 econometric scripts)
- Depends on: Stage 3 panels
- Used by: Final outputs (tables, scores)

**Shared Utilities (`src/f1d/shared/`)**
- Purpose: Cross-cutting utilities used across all stages
- Location: `src/f1d/shared/`
- Contains: `config/`, `logging/`, `observability/`, `variables/`, and utility modules
- Depends on: Configuration files, external libraries
- Used by: All stages

## Data Flow

**Sample Construction Flow:**

1. `clean_metadata.py` - Clean transcript metadata, filter by year range
2. `link_entities.py` - Link transcripts to firms via GVKEY using fuzzy matching
3. `build_tenure_map.py` - Build CEO tenure panel from Execucomp
4. `assemble_manifest.py` - Merge all to create `master_sample_manifest.parquet`

**Text Processing Flow:**

1. `tokenize_transcripts.py` - Tokenize speech, count LM dictionary words
2. `build_linguistic_variables.py` - Compute uncertainty/sentiment percentages

**Panel Building Flow:**

1. Load manifest from Stage 1 output (via `get_latest_output_dir()`)
2. Initialize variable builders (each returns `file_name` + one column)
3. Merge all variables sequentially with zero row delta validation
4. Output panel parquet ready for regression

**Econometric Analysis Flow:**

1. Load panel from Stage 3 output
2. Run OLS/IV/Cox regression with fixed effects
3. Extract fixed effects (gamma_i) and standardize
4. Generate LaTeX tables via `latex_tables_accounting.py`

**State Management:**
- No global state except private data engine singletons
- Each stage reads from timestamped output directories
- `get_latest_output_dir()` resolves most recent output by timestamp

## Key Abstractions

**VariableBuilder (Base Class)**
- Purpose: Define interface for building a single variable
- Examples: `src/f1d/shared/variables/base.py`, all `*_builder.py` files
- Pattern: `build(years: range, root_path: Path) -> VariableResult(data, stats, metadata)`

**Data Engines (Private Singletons)**
- Purpose: Load expensive data sources once and cache in memory
- Examples:
  - `src/f1d/shared/variables/_compustat_engine.py` - CompustatEngine
  - `src/f1d/shared/variables/_crsp_engine.py` - CRSPEngine
  - `src/f1d/shared/variables/_ibes_engine.py` - IBESEngine
  - `src/f1d/shared/variables/_hassan_engine.py` - HassanEngine (policy risk)
- Pattern: Module-level `_engine = None` with `get_engine()` factory

**safe_merge() Wrapper**
- Purpose: Merge DataFrames with validation and logging
- Examples: `src/f1d/shared/data_loading.py`
- Pattern: Pre-merge key validation, post-merge statistics, optional cardinality check

**Timestamp-Based Output Resolution**
- Purpose: Find most recent output without symlinks
- Examples: `src/f1d/shared/path_utils.py` - `get_latest_output_dir()`
- Pattern: Directories named `YYYY-MM-DD_HHMMSS`, sorted lexicographically

## Entry Points

**Stage 1 Scripts:**
- Location: `src/f1d/sample/*.py`
- Triggers: `python -m f1d.sample.clean_metadata`, etc.
- Responsibilities: Read raw inputs, write timestamped outputs

**Stage 2 Scripts:**
- Location: `src/f1d/text/*.py`
- Triggers: `python -m f1d.text.tokenize_transcripts`, etc.
- Responsibilities: Read Stage 1 outputs, write linguistic variables

**Stage 3 Scripts:**
- Location: `src/f1d/variables/build_h{N}_*_panel.py`
- Triggers: `python -m f1d.variables.build_h0_1_manager_clarity_panel`, etc.
- Responsibilities: Load manifest, build variables, merge to panel

**Stage 4 Scripts:**
- Location: `src/f1d/econometric/run_h{N}_*.py`
- Triggers: `python -m f1d.econometric.run_h0_1_manager_clarity`, etc.
- Responsibilities: Load panel, run regression, output tables and scores

**Reporting:**
- Location: `src/f1d/reporting/generate_summary_stats.py`
- Triggers: `python -m f1d.reporting.generate_summary_stats`
- Responsibilities: Generate descriptive statistics from panels

## Error Handling

**Strategy:** Hard-fail with descriptive exceptions

**Patterns:**
- `PathValidationError` - Missing or inaccessible paths
- `OutputResolutionError` - No valid output directory found
- `ValueError` - Missing required columns, merge row delta
- `CollinearityError` / `MulticollinearityError` - Regression design matrix issues
- Pre-merge validation in `safe_merge()` catches missing keys early

**Validation Layers:**
- Input file validation: `validate_input_file()` in `path_utils.py`
- Merge key validation: `validate_merge_keys()` in `data_loading.py`
- Panel column validation: Stage 4 scripts check required columns before regression
- Determinism checks: Config `determinism.sort_inputs: true` ensures reproducibility

## Cross-Cutting Concerns

**Logging:**
- Framework: `structlog` with custom handlers
- Location: `src/f1d/shared/logging/` (handlers.py, context.py, config.py)
- Pattern: `DualWriter` for console + file output

**Validation:**
- Framework: `pydantic` and `pydantic-settings`
- Location: `src/f1d/shared/config/` (base.py, step_configs.py, loader.py)
- Pattern: Type-safe config with environment variable overrides

**Observability:**
- Framework: Custom stats collection
- Location: `src/f1d/shared/observability/` (stats.py, memory.py, throughput.py)
- Pattern: Collect and output statistics per-stage execution

**Configuration:**
- Location: `config/project.yaml`, `config/variables.yaml`
- Access: `get_config()`, `load_variable_config()` from `shared/config/`
- Pattern: Pydantic models with YAML source and env var overrides

---

*Architecture analysis: 2026-02-21*
