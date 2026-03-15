# Codebase Structure

**Analysis Date:** 2026-03-15

## Directory Layout

```
F1D/
├── config/                          # YAML configuration files
│   ├── project.yaml                 # Main pipeline config (steps, paths, params)
│   └── variables.yaml               # Variable source definitions
├── src/f1d/                         # Main package (src-layout)
│   ├── __init__.py                  # Package root (v6.0.0), re-exports panel_ols, path_utils
│   ├── econometric/                 # Stage 4: Hypothesis regression scripts
│   │   ├── run_h{N}_{name}.py       # One script per hypothesis test
│   │   ├── ceo_presence_probit.py   # CEO presence probit model
│   │   └── _archived/              # Deprecated econometric scripts
│   ├── variables/                   # Stage 3: Panel builder scripts
│   │   ├── build_h{N}_{name}_panel.py  # One panel builder per hypothesis
│   │   └── _archived/              # Deprecated panel builders
│   ├── sample/                      # Stage 1: Sample construction
│   │   ├── clean_metadata.py        # Step 1.1: Clean transcript metadata
│   │   ├── link_entities.py         # Step 1.2: Link transcripts to firms
│   │   ├── build_tenure_map.py      # Step 1.3: Build CEO tenure map
│   │   ├── assemble_manifest.py     # Step 1.4: Assemble master manifest
│   │   ├── build_sample_manifest.py # Alternative manifest builder
│   │   └── utils.py                 # Sample construction utilities
│   ├── text/                        # Stage 2: Text processing
│   │   ├── tokenize_transcripts.py  # Tokenize transcripts (uses C++ compiler)
│   │   └── build_linguistic_variables.py  # Compute linguistic variables
│   ├── reporting/                   # Summary statistics generation
│   │   └── generate_summary_stats.py
│   └── shared/                      # Cross-cutting shared utilities
│       ├── __init__.py
│       ├── config/                  # Configuration subsystem
│       │   ├── base.py              # Pydantic ProjectConfig model
│       │   ├── loader.py            # Config loading with cache
│       │   ├── paths.py             # PathsSettings for directory resolution
│       │   ├── datasets.py          # Dataset config
│       │   ├── step_configs.py      # Per-step config models
│       │   ├── hashing.py           # File hashing config
│       │   ├── string_matching.py   # Fuzzy matching config
│       │   └── env.py               # Environment config
│       ├── logging/                 # Structured logging
│       │   ├── config.py            # structlog setup, TeeOutput
│       │   ├── context.py           # Logging context
│       │   └── handlers.py          # Custom log handlers
│       ├── observability/           # Runtime monitoring
│       │   ├── anomalies.py         # Anomaly detection
│       │   ├── files.py             # File tracking
│       │   ├── logging.py           # Observability logging
│       │   ├── memory.py            # Memory monitoring
│       │   ├── stats.py             # Statistics tracking
│       │   └── throughput.py        # Throughput metrics
│       ├── outputs/                 # Output generation utilities
│       │   ├── manifest_generator.py  # run_manifest.json for reproducibility
│       │   └── attrition_table.py   # Sample attrition tables
│       ├── variables/               # Individual variable builders (80+ files)
│       │   ├── base.py              # VariableBuilder base class, VariableResult, VariableStats
│       │   ├── _compustat_engine.py # Singleton Compustat data loader
│       │   ├── _crsp_engine.py      # Singleton CRSP data loader
│       │   ├── _ibes_engine.py      # Singleton IBES data loader
│       │   ├── _ibes_detail_engine.py  # IBES detail engine
│       │   ├── _linguistic_engine.py   # Singleton linguistic data loader
│       │   ├── _hassan_engine.py    # Hassan political risk data loader
│       │   ├── _clarity_residual_engine.py  # CEO clarity residual engine
│       │   ├── panel_utils.py       # assign_industry_sample(), attach_fyearq()
│       │   ├── winsorization.py     # winsorize_by_year(), winsorize_pooled()
│       │   ├── cash_holdings.py     # CashHoldingsBuilder
│       │   ├── lev.py               # LevBuilder
│       │   ├── size.py              # SizeBuilder
│       │   ├── manager_qa_uncertainty.py  # ManagerQAUncertaintyBuilder
│       │   └── ... (60+ more)       # One file per variable builder
│       ├── panel_ols.py             # run_panel_ols() with FE and clustered SEs
│       ├── iv_regression.py         # Instrumental variable regression
│       ├── path_utils.py            # get_latest_output_dir(), ensure_output_dir()
│       ├── data_loading.py          # Generic data loading utilities
│       ├── data_validation.py       # DataFrame validation helpers
│       ├── financial_utils.py       # Financial calculation utilities
│       ├── industry_utils.py        # Industry classification utilities
│       ├── latex_tables.py          # Basic LaTeX table generation
│       ├── latex_tables_accounting.py  # Accounting-style LaTeX tables
│       ├── latex_tables_complete.py # Complete multi-panel LaTeX tables
│       ├── regression_helpers.py    # Regression utility functions
│       ├── regression_validation.py # Regression output validation
│       ├── centering.py             # Variable centering/standardization
│       ├── string_matching.py       # Fuzzy string matching (rapidfuzz)
│       ├── diagnostics.py           # Model diagnostics (VIF, etc.)
│       ├── dual_writer.py           # Dual output writer
│       ├── chunked_reader.py        # Memory-efficient chunked file reading
│       ├── cli_validation.py        # CLI argument validation
│       ├── env_validation.py        # Environment validation
│       ├── metadata_utils.py        # Metadata utilities
│       ├── output_schemas.py        # Output schema definitions
│       ├── reporting_utils.py       # Reporting utilities
│       ├── sample_utils.py          # Sample utility functions
│       ├── subprocess_validation.py # Subprocess validation
│       └── dependency_checker.py    # Dependency verification
├── inputs/                          # Raw input data (NOT committed to git)
│   ├── Compustat_Annual/            # Compustat annual data
│   ├── comp_na_daily_all/           # Compustat daily data
│   ├── CRSP_DSF/                    # CRSP daily stock file
│   ├── CRSPCompustat_CCM/          # CRSP-Compustat merged link table
│   ├── Earnings_Calls_Transcripts/  # Raw transcript data (speaker_data, Unified-info)
│   ├── Execucomp/                   # Executive compensation data
│   ├── tr_ibes/                     # Thomson Reuters IBES analyst data
│   ├── FirmLevelRisk/               # Hassan political risk data
│   ├── SDC/                         # SDC Platinum M&A data
│   ├── CCCL_instrument/             # CCCL instrumental variable data
│   ├── FF1248/                      # Fama-French industry classification
│   ├── LM_dictionary/               # Loughran-McDonald master dictionary
│   └── Manager_roles/               # Manager role classification data
├── outputs/                         # Pipeline outputs (timestamped subdirs)
│   ├── 1.1_CleanMetadata/           # Stage 1 step outputs
│   ├── 1.2_LinkEntities/
│   ├── 1.3_BuildTenureMap/
│   ├── 1.4_AssembleManifest/        # Master sample manifest
│   ├── 2_Textual_Analysis/          # Stage 2 text analysis outputs
│   ├── variables/                   # Stage 3 panel outputs
│   │   ├── h1_cash_holdings/        # H1 panel (per-hypothesis)
│   │   ├── h2_investment/           # H2 panel
│   │   ├── h5_dispersion/           # H5 panel
│   │   └── ... (20+ hypothesis panels)
│   └── econometric/                 # Stage 4 regression outputs
│       ├── h1_cash_holdings/        # H1 regressions
│       ├── h7_illiquidity/          # H7 regressions
│       └── ... (15+ hypothesis results)
├── tests/                           # Test suite
│   ├── conftest.py                  # Shared pytest fixtures
│   ├── unit/                        # Unit tests
│   ├── integration/                 # Integration tests
│   ├── regression/                  # Output stability regression tests
│   ├── performance/                 # Performance benchmark tests
│   ├── verification/                # Dry-run verification tests
│   ├── factories/                   # Test data factories
│   ├── fixtures/                    # Synthetic test data generators
│   └── utils/                       # Test harness utilities
├── scripts/                         # Ad-hoc utility scripts
│   └── compute_missing_sumstats.py
├── docs/                            # Documentation
│   ├── Draft/                       # Thesis LaTeX draft
│   ├── audits/                      # Code audit reports
│   ├── plans/                       # Implementation plans
│   ├── Prompts/                     # AI prompt templates
│   ├── provenance/                  # Data provenance docs
│   └── Hypothesis Documentation/   # Hypothesis specifications
├── logs/                            # Runtime logs (timestamped per run)
├── .planning/                       # GSD planning documents
│   └── codebase/                    # Codebase analysis docs
├── .archive/                        # Archived old code (H8 removal)
├── _archived/                       # Additional archived code
├── pyproject.toml                   # Package config, pytest, ruff, mypy, coverage
├── requirements.txt                 # Pinned dependencies
├── .pre-commit-config.yaml          # Pre-commit hook config
├── .coveragerc                      # Coverage config
├── .gitignore                       # Git ignore patterns
└── README.md                        # Project documentation
```

## Directory Purposes

**`config/`:**
- Purpose: Central YAML configuration for the entire pipeline
- Contains: `project.yaml` (step configs, paths, parameters), `variables.yaml` (variable source definitions)
- Key files: `config/project.yaml` (loaded by all stages), `config/variables.yaml` (loaded by Stage 3 builders)

**`src/f1d/`:**
- Purpose: Main installable Python package (src-layout via setuptools)
- Contains: All pipeline code organized by stage and shared utilities
- Key files: `__init__.py` (v6.0.0, re-exports `run_panel_ols`, `get_latest_output_dir`)

**`src/f1d/shared/variables/`:**
- Purpose: Individual variable builder classes, one per financial/linguistic variable
- Contains: ~80+ builder files, 7 compute engines, base class, utilities
- Key files: `base.py` (VariableBuilder interface), `_compustat_engine.py` (singleton loader), `panel_utils.py` (industry sample assignment), `winsorization.py`

**`src/f1d/variables/`:**
- Purpose: Stage 3 panel builder scripts that orchestrate variable merging for each hypothesis
- Contains: `build_h{N}_{name}_panel.py` files
- Key files: Each hypothesis gets its own panel builder

**`src/f1d/econometric/`:**
- Purpose: Stage 4 regression scripts for hypothesis testing
- Contains: `run_h{N}_{name}.py` files, LaTeX table generation helpers
- Key files: Each hypothesis gets its own regression runner

**`inputs/`:**
- Purpose: Raw financial and textual data files (NOT committed to git)
- Contains: Compustat, CRSP, IBES, transcripts, dictionaries, industry classifications
- Generated: No (externally sourced)
- Committed: No (.gitignore)

**`outputs/`:**
- Purpose: All pipeline outputs organized by stage and hypothesis
- Contains: Parquet files, CSV summaries, LaTeX tables, markdown reports, run manifests
- Generated: Yes (by pipeline scripts)
- Committed: Selectively (key results committed)

**`tests/`:**
- Purpose: Comprehensive test suite organized by test type
- Contains: unit, integration, regression, performance, verification tests
- Key files: `conftest.py` (shared fixtures), `factories/` (test data factories), `fixtures/` (synthetic data generators)

## Key File Locations

**Entry Points:**
- `src/f1d/variables/build_h1_cash_holdings_panel.py`: Example Stage 3 entry point
- `src/f1d/econometric/run_h1_cash_holdings.py`: Example Stage 4 entry point
- `src/f1d/sample/assemble_manifest.py`: Stage 1 manifest assembly
- `src/f1d/text/build_linguistic_variables.py`: Stage 2 text processing

**Configuration:**
- `config/project.yaml`: Main pipeline config (year range, step parameters, paths)
- `config/variables.yaml`: Variable source definitions (where each builder loads data from)
- `pyproject.toml`: Package metadata, pytest, ruff, mypy, coverage settings

**Core Logic:**
- `src/f1d/shared/variables/base.py`: VariableBuilder base class and VariableResult dataclass
- `src/f1d/shared/variables/_compustat_engine.py`: Compustat singleton data loader
- `src/f1d/shared/panel_ols.py`: Panel OLS regression with FE and clustered SEs
- `src/f1d/shared/config/loader.py`: Config loading with caching
- `src/f1d/shared/path_utils.py`: Timestamped output directory resolution

**Testing:**
- `tests/conftest.py`: Shared pytest fixtures
- `tests/unit/`: Unit tests for shared modules
- `tests/integration/`: Integration tests for pipeline flows
- `tests/verification/`: Dry-run tests for all scripts
- `tests/factories/financial.py`: Financial data factories
- `tests/fixtures/synthetic_panel.py`: Synthetic panel data generators

## Naming Conventions

**Files:**
- Variable builders: `{variable_name}.py` in `src/f1d/shared/variables/` (e.g., `cash_holdings.py`, `manager_qa_uncertainty.py`)
- Panel builders: `build_h{N}_{hypothesis_name}_panel.py` in `src/f1d/variables/`
- Econometric scripts: `run_h{N}_{hypothesis_name}.py` in `src/f1d/econometric/`
- Compute engines: `_{source}_engine.py` with leading underscore (private modules)
- Test files: `test_{module_or_feature}.py` in `tests/unit/` or `tests/integration/`

**Directories:**
- Stage outputs: `{step_number}_{StepName}/` (e.g., `1.4_AssembleManifest/`, `2_Textual_Analysis/`)
- Hypothesis outputs: `h{N}_{name}/` (e.g., `h1_cash_holdings/`, `h7_illiquidity/`)
- Timestamped subdirs: `{YYYY-MM-DD_HHMMSS}/` inside each output directory

**Classes:**
- Variable builders: `{VariableName}Builder` (e.g., `CashHoldingsBuilder`, `ManagerQAUncertaintyBuilder`)
- Config classes: `{Section}Settings` (e.g., `DataSettings`, `PathsSettings`, `LoggingSettings`)
- Exceptions: Descriptive names (`CollinearityError`, `MulticollinearityError`, `OutputResolutionError`, `ConfigError`)

**Variables/Columns:**
- Financial variables: PascalCase (e.g., `CashHoldings`, `TobinsQ`, `ROA`, `CapexAt`)
- Linguistic variables: PascalCase with context (e.g., `Manager_QA_Uncertainty_pct`, `CEO_Pres_Weak_Modal_pct`)
- Lead/lag variables: `{Variable}_lead` suffix (e.g., `CashHoldings_lead`, `Dispersion_lead`)
- Identifiers: lowercase (e.g., `gvkey`, `file_name`, `ceo_id`, `ff12_code`, `fyearq`)

## Where to Add New Code

**New Hypothesis Test:**
1. Variable builder: Create individual builder in `src/f1d/shared/variables/{variable_name}.py` extending `VariableBuilder`
2. Register builder: Add import and `__all__` entry in `src/f1d/shared/variables/__init__.py`
3. Add variable config: Add entry in `config/variables.yaml` with source path and column name
4. Panel builder: Create `src/f1d/variables/build_h{N}_{name}_panel.py` importing needed builders
5. Regression script: Create `src/f1d/econometric/run_h{N}_{name}.py` with PanelOLS regression
6. Tests: Add unit test in `tests/unit/test_h{N}_regression.py` and/or `tests/unit/test_h{N}_variables.py`

**New Financial Variable:**
1. If from Compustat: Add column to `REQUIRED_COMPUSTAT_COLS` in `src/f1d/shared/variables/_compustat_engine.py`, add computation in engine
2. Create builder file: `src/f1d/shared/variables/{variable_name}.py` extending `VariableBuilder`
3. Register in `src/f1d/shared/variables/__init__.py`
4. Add config entry in `config/variables.yaml`

**New Linguistic Variable:**
1. Ensure the linguistic engine outputs the column in `src/f1d/shared/variables/_linguistic_engine.py`
2. Create builder file: `src/f1d/shared/variables/{variable_name}.py`
3. Register in `src/f1d/shared/variables/__init__.py`

**New Shared Utility:**
- Place in `src/f1d/shared/{utility_name}.py`
- Add tests in `tests/unit/test_{utility_name}.py`

**New Compute Engine (new data source):**
- Create `src/f1d/shared/variables/_{source}_engine.py` with singleton pattern
- Use module-level caching (see `_compustat_engine.py` pattern)

## Special Directories

**`.archive/` and `_archived/`:**
- Purpose: Archived/deprecated code (H8 political risk removal, old scripts)
- Generated: No (manually moved)
- Committed: Yes (for historical reference)

**`.planning/`:**
- Purpose: GSD planning documents, milestone audits, roadmaps
- Generated: By GSD tooling
- Committed: Yes

**`.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`:**
- Purpose: Tool caches
- Generated: Yes (by mypy, pytest, ruff)
- Committed: No (.gitignore)

**`outputs/` timestamped subdirectories:**
- Purpose: Each pipeline run creates a `{YYYY-MM-DD_HHMMSS}/` subdirectory
- Generated: Yes (by pipeline scripts)
- Pattern: `get_latest_output_dir()` resolves to the subdirectory with the most matching files
- Contains: parquet data, CSV stats, LaTeX tables, markdown reports, `run_manifest.json`
- Committed: Selectively

**`logs/`:**
- Purpose: Runtime logs organized by suite and timestamp
- Pattern: `logs/{suite_name}/{YYYY-MM-DD_HHMMSS}/`
- Generated: Yes (by `setup_run_logging()`)
- Committed: No

---

*Structure analysis: 2026-03-15*
