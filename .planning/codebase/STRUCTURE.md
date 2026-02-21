# Codebase Structure

**Analysis Date:** 2026-02-21

## Directory Layout

```
F1D/
├── src/f1d/                    # Main package (src-layout)
│   ├── __init__.py             # Public API exports
│   ├── shared/                 # Tier 1: Cross-cutting utilities
│   │   ├── __init__.py         # Re-exports key utilities
│   │   ├── config/             # Pydantic configuration models
│   │   ├── logging/            # Structured logging infrastructure
│   │   ├── observability/      # Stats collection, memory monitoring
│   │   ├── variables/          # Variable builders (50+ modules)
│   │   ├── path_utils.py       # Path resolution, output dir helpers
│   │   ├── data_loading.py     # safe_merge(), load_all_data()
│   │   ├── panel_ols.py        # Panel OLS with fixed effects
│   │   ├── financial_utils.py  # Financial data utilities
│   │   ├── iv_regression.py    # Instrumental variable regression
│   │   ├── latex_tables*.py    # LaTeX table generation
│   │   └── [other utilities]
│   ├── sample/                 # Stage 1: Sample construction
│   ├── text/                   # Stage 2: Text processing
│   ├── variables/              # Stage 3: Panel builders
│   ├── econometric/            # Stage 4: Hypothesis tests
│   └── reporting/              # Summary statistics generation
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests (fast, isolated)
│   ├── integration/            # Integration tests (subprocess)
│   ├── regression/             # Regression tests (baseline comparison)
│   ├── verification/           # Dry-run verification tests
│   ├── performance/            # Performance regression tests
│   ├── fixtures/               # Test data fixtures
│   ├── factories/              # Test data factories
│   └── conftest.py             # Pytest fixtures and config
├── config/                     # Configuration files
│   ├── project.yaml            # Main project configuration
│   └── variables.yaml          # Variable source definitions
├── inputs/                     # Raw input data (not in repo)
├── outputs/                    # Pipeline outputs (not in repo)
├── logs/                       # Execution logs
├── docs/                       # Documentation
├── .github/workflows/          # CI/CD workflows
├── pyproject.toml              # Package configuration
├── requirements.txt            # Production dependencies
└── README.md                   # Project documentation
```

## Directory Purposes

**`src/f1d/shared/`**
- Purpose: Cross-cutting utilities used across all pipeline stages
- Contains: Config, logging, observability, variable builders, regression helpers
- Key files: `path_utils.py`, `panel_ols.py`, `data_loading.py`, `iv_regression.py`

**`src/f1d/shared/variables/`**
- Purpose: Individual variable builders (one column per builder)
- Contains: 50+ modules, each building a single variable
- Key files: `base.py`, `_compustat_engine.py`, `_crsp_engine.py`, `_ibes_engine.py`

**`src/f1d/shared/config/`**
- Purpose: Type-safe configuration management
- Contains: Pydantic models for project config, step configs, variable configs
- Key files: `base.py`, `loader.py`, `step_configs.py`

**`src/f1d/sample/`**
- Purpose: Stage 1 sample construction
- Contains: 4 scripts for building the master manifest
- Key files: `assemble_manifest.py` (final output: `master_sample_manifest.parquet`)

**`src/f1d/text/`**
- Purpose: Stage 2 text processing
- Contains: 2 scripts for tokenization and linguistic variables
- Key files: `build_linguistic_variables.py` (outputs per year)

**`src/f1d/variables/`**
- Purpose: Stage 3 panel builders
- Contains: 15 scripts building hypothesis-specific panels
- Key files: `build_h{0-10}_*_panel.py`

**`src/f1d/econometric/`**
- Purpose: Stage 4 econometric analysis
- Contains: 16 scripts running hypothesis tests
- Key files: `run_h{0-10}_*.py`

**`tests/`**
- Purpose: Comprehensive test suite
- Contains: Unit, integration, regression, verification, performance tests
- Key files: `conftest.py` (shared fixtures), `factories/` (test data)

**`config/`**
- Purpose: YAML configuration files
- Contains: Project settings, variable source definitions
- Key files: `project.yaml`, `variables.yaml`

**`inputs/`**
- Purpose: Raw input data from external sources
- Contains: Compustat, CRSP, IBES, transcripts, dictionaries
- Not committed to repository

**`outputs/`**
- Purpose: Pipeline outputs organized by stage
- Contains: Timestamped subdirectories per stage/step
- Not committed to repository

## Key File Locations

**Entry Points:**
- `src/f1d/sample/clean_metadata.py`: Stage 1 first step
- `src/f1d/text/tokenize_transcripts.py`: Stage 2 first step
- `src/f1d/variables/build_h0_1_manager_clarity_panel.py`: Stage 3 example
- `src/f1d/econometric/run_h0_1_manager_clarity.py`: Stage 4 example
- `src/f1d/reporting/generate_summary_stats.py`: Final reporting

**Configuration:**
- `config/project.yaml`: Main project config (paths, settings, step configs)
- `config/variables.yaml`: Variable source definitions for builders

**Core Shared Logic:**
- `src/f1d/shared/path_utils.py`: Output resolution, path validation
- `src/f1d/shared/data_loading.py`: `safe_merge()`, `load_all_data()`
- `src/f1d/shared/panel_ols.py`: Panel OLS with fixed effects
- `src/f1d/shared/variables/base.py`: VariableBuilder base class

**Variable Engines:**
- `src/f1d/shared/variables/_compustat_engine.py`: Compustat singleton
- `src/f1d/shared/variables/_crsp_engine.py`: CRSP singleton
- `src/f1d/shared/variables/_ibes_engine.py`: IBES singleton

**Testing:**
- `tests/conftest.py`: Shared pytest fixtures
- `tests/factories/`: Test data factories
- `tests/fixtures/`: Test data fixtures

## Naming Conventions

**Files:**
- Scripts: `{action}_{subject}.py` (e.g., `build_h1_cash_holdings_panel.py`)
- Variable builders: `{variable_name}.py` (e.g., `size.py`, `eps_growth.py`)
- Data engines: `_{source}_engine.py` (e.g., `_compustat_engine.py`)
- Test files: `test_{module_name}.py` (e.g., `test_panel_ols.py`)

**Directories:**
- Stage outputs: `{step_number}_{description}` (e.g., `1.4_AssembleManifest`)
- Timestamped outputs: `YYYY-MM-DD_HHMMSS` (e.g., `2026-02-20_143022`)

**Classes:**
- Variable builders: `{VariableName}Builder` (e.g., `SizeBuilder`, `EPSGrowthBuilder`)
- Data engines: `{Source}Engine` (e.g., `CompustatEngine`, `CRSPEngine`)
- Config models: `{Name}Config` or `{Name}Settings` (e.g., `ProjectConfig`, `DataSettings`)

**Functions:**
- Builders: `build()` returning `VariableResult`
- Loaders: `load_*()` (e.g., `load_config()`, `load_variable_config()`)
- Utilities: Verb-noun pattern (e.g., `get_latest_output_dir()`, `ensure_output_dir()`)

## Where to Add New Code

**New Hypothesis Test:**
- Panel builder: `src/f1d/variables/build_h{N}_{name}_panel.py`
- Econometric script: `src/f1d/econometric/run_h{N}_{name}.py`
- Test: `tests/unit/test_h{N}_regression.py`

**New Variable:**
- Builder: `src/f1d/shared/variables/{variable_name}.py`
- Export: Add to `src/f1d/shared/variables/__init__.py`
- Config: Add entry to `config/variables.yaml`
- Test: `tests/unit/test_{variable_name}.py`

**New Utility:**
- Core utility: `src/f1d/shared/{utility_name}.py`
- Export: Add to `src/f1d/shared/__init__.py`
- Test: `tests/unit/test_{utility_name}.py`

**New Configuration Setting:**
- Model: `src/f1d/shared/config/base.py` or `step_configs.py`
- YAML: `config/project.yaml` or `config/variables.yaml`

**New Test:**
- Unit test: `tests/unit/test_{subject}.py`
- Integration test: `tests/integration/test_{subject}.py`
- Regression test: `tests/regression/test_{subject}.py`

## Special Directories

**`src/f1d/shared/variables/`**
- Purpose: Variable builders, each returning one column
- Contains: 50+ builder modules + 4 private data engines
- Not a package namespace - builders imported directly

**`outputs/`**
- Purpose: Timestamped pipeline outputs
- Generated: Yes (by pipeline execution)
- Committed: No (in `.gitignore`)
- Structure: `{stage}/{step}/{timestamp}/`

**`inputs/`**
- Purpose: External raw data files
- Generated: No (externally provided)
- Committed: No (in `.gitignore`)
- Contains: Compustat, CRSP, IBES, transcripts, dictionaries

**`docs/`**
- Purpose: Project documentation
- Contains: Architecture standards, code quality, variable catalogs
- Key files: `ARCHITECTURE_STANDARD.md`, `CODE_QUALITY_STANDARD.md`, `VARIABLE_CATALOG_V2_V3.md`

**`.github/workflows/`**
- Purpose: CI/CD pipeline definitions
- Contains: GitHub Actions workflows
- Key files: Test matrix, security scanning, type checking

---

*Structure analysis: 2026-02-21*
