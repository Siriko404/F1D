# Codebase Structure

**Analysis Date:** 2025-02-04

## Directory Layout

```
F1D/
├── 1_Inputs/          # Raw data files (read-only)
├── 2_Scripts/         # Pipeline processing scripts
├── 3_Logs/            # Execution logs (timestamped)
├── 4_Outputs/         # Pipeline outputs (timestamped)
├── config/            # Configuration files
├── tests/             # Unit and integration tests
├── .___archive/       # Legacy and debug code (git-ignored)
├── .claude/           # Claude Code project settings
├── .github/           # GitHub Actions workflows
├── .planning/         # Planning documents and phase specs
├── README.md          # Project documentation
├── requirements.txt   # Python dependencies
├── pyproject.toml     # Pytest and coverage configuration
└── SCALING.md         # Scaling documentation
```

## Directory Purposes

**1_Inputs/:**
- Purpose: Raw input data files (read-only, never modified by pipeline)
- Contains: Earnings call transcripts, financial databases (Compustat, CRSP, IBES), reference dictionaries, event data
- Key files: `Unified-info.parquet`, `speaker_data_{year}.parquet`, `Loughran-McDonald_MasterDictionary_1993-2024.csv`, `CRSPCompustat_CCM/`, `comp_na_daily_all/`, `tr_ibes/`, `SDC/`, `CCCL instrument/`

**2_Scripts/:**
- Purpose: Main pipeline processing scripts organized by stage
- Contains: Stage directories (1_Sample, 2_Text, 3_Financial, 4_Econometric) and shared utility modules
- Key files: `1_Sample/1.1_CleanMetadata.py`, `1_Sample/1.2_LinkEntities.py`, `1_Sample/1.4_AssembleManifest.py`, `2_Text/2.1_TokenizeAndCount.py`, `2_Text/2.2_ConstructVariables.py`, `3_Financial/3.1_FirmControls.py`, `3_Financial/3.2_MarketVariables.py`, `4_Econometric/4.1_EstimateCeoClarity.py`, `shared/` (20+ utility modules)

**3_Logs/:**
- Purpose: Execution logs mirroring terminal output
- Contains: One subdirectory per pipeline step, each with timestamped `.log` files
- Key files: `{StepName}/{timestamp}.log` files matching script execution runs

**4_Outputs/:**
- Purpose: Pipeline outputs organized by step with timestamped runs
- Contains: One subdirectory per pipeline step, each with timestamped subdirectories and `latest/` symlink
- Key files: `1.0_BuildSampleManifest/latest/master_sample_manifest.parquet`, `2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_{year}.parquet`, `3_Financial_Features/latest/firm_controls_{year}.parquet`, `3_Financial_Features/latest/market_variables_{year}.parquet`

**config/:**
- Purpose: Centralized configuration for all pipeline steps
- Contains: `project.yaml` (paths, thresholds, parameters)
- Key files: `project.yaml`

**tests/:**
- Purpose: Unit and integration tests for shared utilities and pipeline validation
- Contains: `unit/`, `integration/`, `conftest.py` (pytest fixtures)
- Key files: `conftest.py`, `unit/test_data_validation.py`, `unit/test_fuzzy_matching.py`, `unit/test_env_validation.py`

**.planning/:**
- Purpose: Planning documents, phase specifications, quick task specs
- Contains: `codebase/`, `phases/`, `quick/`
- Generated: Yes (by GSD commands)

**.___archive/:**
- Purpose: Legacy scripts, debug code, broken implementations (preserved for reference)
- Contains: `legacy/`, `debug/`, `docs/`
- Committed: Yes (git-ignored via `.gitignore`)

## Key File Locations

**Entry Points:**
- `2_Scripts/1_Sample/1.1_CleanMetadata.py`: First step in pipeline (metadata cleaning)
- `2_Scripts/1_Sample/1.0_BuildSampleManifest.py`: Legacy manifest builder (preserved for reference)
- `2_Scripts/4_Econometric/4.1_EstimateCeoClarity.py`: Econometric analysis entry point

**Configuration:**
- `config/project.yaml`: Central configuration (all paths, seeds, thresholds, per-step params)
- `pyproject.toml`: Pytest configuration, coverage settings
- `requirements.txt`: Python dependencies
- `.claude/settings.json`: Claude Code project permissions and settings

**Core Logic:**
- `2_Scripts/1_Sample/`: Sample construction (clean, link entities, build tenure, assemble manifest)
- `2_Scripts/2_Text/`: Text processing (tokenize, count, construct linguistic variables)
- `2_Scripts/3_Financial/`: Financial features (firm controls, market variables, event flags)
- `2_Scripts/4_Econometric/`: Econometric analysis (CEO clarity, liquidity, takeover hazards)

**Testing:**
- `tests/conftest.py`: Pytest fixtures (sample DataFrames, configs, paths)
- `tests/unit/test_*.py`: Unit tests for shared utilities
- `tests/integration/`: Integration tests for pipeline workflows

## Naming Conventions

**Files:**
- Pipeline steps: `<Stage>.<Step>_<PascalCaseName>.py` (e.g., `1.1_CleanMetadata.py`, `3.1_FirmControls.py`)
- Substeps: `<Stage>.<Step>.<Substep>_<PascalCaseName>.py` (e.g., `4.1.1_EstimateCeoClarity_CeoSpecific.py`)
- Utility modules: `<snake_case>.py` (e.g., `dual_writer.py`, `path_utils.py`)
- Test files: `test_<snake_case>.py` (e.g., `test_data_validation.py`)
- Config files: `<name>.yaml` (e.g., `project.yaml`)

**Directories:**
- Pipeline stages: `<Stage>_<PascalCaseName>/` (e.g., `1_Sample/`, `3_Financial/`)
- Output steps: `<Step>_<PascalCaseName>/` (e.g., `1.4_AssembleManifest/`)
- Timestamped runs: `YYYY-MM-DD_HHMMSS/`
- Testing: `unit/`, `integration/`, `fixtures/`

**Functions:**
- Pipeline functions: `snake_case` (e.g., `load_config()`, `setup_paths()`, `check_prerequisites()`)
- Utility functions: `snake_case` with descriptive names (e.g., `validate_input_file()`, `get_latest_output_dir()`)
- Test functions: `test_<snake_case>` (e.g., `test_validate_parquet_schema()`)

**Variables:**
- Local variables: `snake_case` (e.g., `metadata_df`, `output_dir`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `STATSMODELS_AVAILABLE`)
- Configuration keys: `snake_case` (e.g., `random_seed`, `year_start`)

## Where to Add New Code

**New Pipeline Step (e.g., new Step 3.5):**
- Primary code: `2_Scripts/3_Financial/3.5_<PascalCaseName>.py`
- Tests: `tests/unit/test_3_5_<name>.py` or `tests/integration/test_step_3_5.py`
- Outputs: `4_Outputs/3.5_<PascalCaseName>/{timestamp}/`
- Logs: `3_Logs/3.5_<PascalCaseName>/{timestamp}.log`
- Config: Add `step_03_5:` section to `config/project.yaml`

**New Shared Utility:**
- Implementation: `2_Scripts/shared/<snake_case>.py`
- Tests: `tests/unit/test_<snake_case>.py`
- Re-export: Add to `2_Scripts/shared/__init__.py` if meant for public API
- Documentation: Include contract header with ID, Description, Inputs, Outputs, Deterministic

**New Component/Module (new pipeline stage):**
- Implementation: `2_Scripts/<Stage>_<PascalCaseName>/`
- Configuration: Add to `config/project.yaml` under new top-level key
- Outputs: `4_Outputs/<Stage>_<PascalCaseName>/`
- Logs: `3_Logs/<Stage>_<PascalCaseName>/`

**Utilities:**
- Shared helpers: `2_Scripts/shared/<snake_case>.py` (e.g., `string_matching.py`, `industry_utils.py`)
- Script-specific utilities: `<Stage>_<Name>/<Step>.<Substep>_Utils.py` (e.g., `1_Sample/1.5_Utils.py`, `3_Financial/3.4_Utils.py`)

## Special Directories

**`2_Scripts/shared/`:**
- Purpose: Shared utility modules for cross-cutting concerns
- Generated: No
- Committed: Yes
- Key modules: `dual_writer.py`, `path_utils.py`, `observability_utils.py`, `data_validation.py`, `regression_utils.py`, `financial_utils.py`, `string_matching.py`, `industry_utils.py`, `chunked_reader.py`

**`4_Outputs/latest/`:**
- Purpose: Symlinks to most recent successful outputs (auto-created after each successful run)
- Generated: Yes
- Committed: No (symlinks are machine-specific)
- Pattern: Each step creates `latest/` pointing to its timestamped directory

**`3_Logs/`:**
- Purpose: Execution logs with terminal output capture
- Generated: Yes
- Committed: Yes (for audit trail)
- Pattern: `{StepName}/{YYYY-MM-DD_HHMMSS}.log`

**`.___archive/`:**
- Purpose: Legacy, debug, and broken code (not used in active pipeline)
- Generated: No
- Committed: Yes
- Contains: `legacy/` (old implementations), `debug/` (investigation scripts), `docs/` (old documentation)

**`tests/fixtures/`:**
- Purpose: Test data and sample files for unit tests
- Generated: No (hand-written test data)
- Committed: Yes
- Contains: `sample_yaml/`, sample parquet files, mock configs

**`.planning/`:**
- Purpose: GSD planning documents, phase specs, codebase analysis
- Generated: Yes (by GSD commands)
- Committed: Yes
- Contains: `codebase/` (this file), `phases/`, `quick/`

---

*Structure analysis: 2025-02-04*
