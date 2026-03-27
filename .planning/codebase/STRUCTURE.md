# Codebase Structure

**Analysis Date:** 2026-03-25

## Directory Layout

```
F1D/
├── config/                              # YAML configuration files
│   ├── project.yaml                     # Main pipeline config (steps, paths, params)
│   └── variables.yaml                   # Variable source definitions
├── src/f1d/                             # Main package (src-layout, v6.0.0)
│   ├── __init__.py                      # Package root, re-exports panel_ols, path_utils
│   ├── econometric/                     # Stage 4: 22 active hypothesis regression scripts
│   │   ├── run_h{N}_{name}.py           # One script per hypothesis test
│   │   ├── ceo_presence_probit.py       # CEO presence probit model (H7 supplement)
│   │   ├── _save_latex_table_6col.py    # 6-column LaTeX table helper
│   │   └── _archived/                   # Deprecated econometric scripts (H0.1/H0.2/H0.5/H3/H13.2)
│   ├── variables/                       # Stage 3: 19 active panel builder scripts
│   │   ├── build_h{N}_{name}_panel.py   # One panel builder per hypothesis
│   │   └── _archived/                   # Deprecated panel builders (H0.1/H0.2/H0.5/H3/H13.2)
│   ├── sample/                          # Stage 1: Sample construction
│   │   ├── clean_metadata.py            # Step 1.1: Clean transcript metadata
│   │   ├── link_entities.py             # Step 1.2: Link transcripts to firms
│   │   ├── build_tenure_map.py          # Step 1.3: Build CEO tenure map
│   │   ├── assemble_manifest.py         # Step 1.4: Assemble master manifest
│   │   ├── build_sample_manifest.py     # Alternative manifest builder
│   │   └── utils.py                     # Sample construction utilities
│   ├── text/                            # Stage 2: Text processing
│   │   ├── tokenize_transcripts.py      # Tokenize transcripts (uses C++ compiler)
│   │   └── build_linguistic_variables.py  # Compute linguistic variables
│   ├── reporting/                       # Summary statistics generation
│   │   └── generate_summary_stats.py
│   └── shared/                          # Cross-cutting shared utilities
│       ├── __init__.py
│       ├── config/                      # Configuration subsystem
│       │   ├── base.py                  # Pydantic ProjectConfig model
│       │   ├── loader.py               # Config loading with cache + load_variable_config
│       │   ├── paths.py               # PathsSettings for directory resolution
│       │   ├── datasets.py            # Dataset config
│       │   ├── step_configs.py        # Per-step config models
│       │   ├── hashing.py            # File hashing config
│       │   ├── string_matching.py    # Fuzzy matching config
│       │   └── env.py                # Environment config
│       ├── logging/                   # Structured logging
│       │   ├── config.py             # structlog setup, TeeOutput
│       │   ├── context.py            # Logging context
│       │   └── handlers.py           # Custom log handlers
│       ├── observability/            # Runtime monitoring
│       │   ├── anomalies.py          # Anomaly detection
│       │   ├── files.py             # File tracking
│       │   ├── logging.py           # Observability logging
│       │   ├── memory.py            # Memory monitoring
│       │   ├── stats.py             # Statistics tracking
│       │   └── throughput.py        # Throughput metrics
│       ├── outputs/                  # Output generation utilities
│       │   ├── manifest_generator.py  # run_manifest.json for reproducibility
│       │   └── attrition_table.py   # Sample attrition tables
│       ├── variables/               # Individual variable builders (~90 files)
│       │   ├── base.py              # VariableBuilder base class, VariableResult, VariableStats
│       │   ├── VARIABLE_REGISTRY.md # Variable documentation
│       │   ├── _compustat_engine.py # Singleton Compustat data loader (1,342 lines)
│       │   ├── _crsp_engine.py      # Singleton CRSP data loader (518 lines)
│       │   ├── _ibes_engine.py      # Singleton IBES consensus engine (260 lines)
│       │   ├── _ibes_detail_engine.py  # IBES individual analyst engine (328 lines)
│       │   ├── _linguistic_engine.py   # Singleton linguistic data loader (316 lines)
│       │   ├── _hassan_engine.py    # Hassan political risk engine
│       │   ├── _clarity_residual_engine.py  # CEO clarity residual engine
│       │   ├── panel_utils.py       # assign_industry_sample(), attach_fyearq()
│       │   ├── winsorization.py     # winsorize_by_year(), winsorize_pooled()
│       │   ├── __init__.py          # Central registry: all builder imports + __all__
│       │   ├── _archived/           # Archived builders (div_stability, fcf_growth, etc.)
│       │   └── [~80 builder .py]    # One file per variable builder
│       ├── panel_ols.py             # run_panel_ols() with FE and clustered SEs
│       ├── iv_regression.py         # IV2SLS regression (H6 CCCL)
│       ├── path_utils.py            # get_latest_output_dir(), ensure_output_dir()
│       ├── data_loading.py          # Generic data loading utilities
│       ├── data_validation.py       # DataFrame validation helpers
│       ├── financial_utils.py       # Financial calculation utilities
│       ├── industry_utils.py        # Industry classification utilities
│       ├── latex_tables.py          # Basic LaTeX table generation
│       ├── latex_tables_accounting.py  # Accounting Review style tables
│       ├── latex_tables_complete.py # Complete multi-panel LaTeX tables
│       ├── regression_helpers.py    # Regression utility functions
│       ├── regression_validation.py # Regression output validation
│       ├── centering.py            # Variable centering/standardization
│       ├── string_matching.py      # Fuzzy string matching (rapidfuzz)
│       ├── diagnostics.py          # Model diagnostics (VIF, etc.)
│       ├── dual_writer.py          # Dual output writer
│       ├── chunked_reader.py       # Memory-efficient chunked file reading
│       ├── cli_validation.py       # CLI argument validation
│       ├── env_validation.py       # Environment validation
│       ├── metadata_utils.py       # Metadata utilities
│       ├── output_schemas.py       # Output schema definitions
│       ├── reporting_utils.py      # Reporting utilities
│       ├── sample_utils.py         # Sample utility functions
│       ├── subprocess_validation.py  # Subprocess validation
│       └── dependency_checker.py   # Dependency verification
├── inputs/                          # Raw input data (NOT committed to git)
│   ├── Compustat_Annual/            # Compustat annual data
│   ├── comp_na_daily_all/           # Compustat quarterly data (primary source)
│   ├── compustat_daily_ratings/     # S&P credit ratings (H1.2)
│   ├── CRSP_DSF/                    # CRSP daily stock file (quarterly parquets)
│   ├── CRSPCompustat_CCM/          # CRSP-Compustat merged link table
│   ├── Earnings_Calls_Transcripts/  # Raw transcript data (speaker_data, Unified-info)
│   ├── Execucomp/                   # Executive compensation data
│   ├── tr_ibes/                     # Thomson Reuters IBES analyst data (yearly parquets)
│   ├── FirmLevelRisk/               # Hassan political risk data (firmquarter CSV)
│   ├── SDC/                         # SDC Platinum M&A data (H9 takeover)
│   ├── CCCL_instrument/             # CCCL instrumental variable data (H6)
│   ├── TNIC3HHIdata/                # Hoberg-Phillips TNIC3 data (H1.1, H13.1 moderation)
│   ├── FF1248/                      # Fama-French industry classification
│   ├── LM_dictionary/               # Loughran-McDonald master dictionary
│   ├── Manager_roles/               # Manager role classification data
│   ├── Siccodes12.zip               # SIC-to-FF12 mapping
│   └── Siccodes48.zip               # SIC-to-FF48 mapping
├── outputs/                         # Pipeline outputs (timestamped subdirs)
│   ├── 1.1_CleanMetadata/           # Stage 1 step outputs
│   ├── 1.2_LinkEntities/
│   ├── 1.3_BuildTenureMap/
│   ├── 1.4_AssembleManifest/        # Master sample manifest
│   ├── 2_Textual_Analysis/          # Stage 2 text analysis outputs
│   ├── variables/                   # Stage 3 panel outputs (per-hypothesis)
│   │   ├── h1_cash_holdings/
│   │   ├── h2_investment/
│   │   ├── h4_leverage/
│   │   ├── h5_dispersion/
│   │   ├── h5b_johnson_disp/
│   │   ├── h5b_wang_disp/
│   │   ├── h6_cccl/
│   │   ├── h7_illiquidity/
│   │   ├── takeover/                # H9 (named "takeover" not "h9_")
│   │   ├── h11_prisk_uncertainty/
│   │   ├── h11_prisk_uncertainty_lag/
│   │   ├── h11_prisk_uncertainty_lead/
│   │   ├── h12_div_intensity/
│   │   ├── h12q_payout/
│   │   ├── h13_capex/
│   │   ├── h14_bidask_spread/
│   │   ├── h15_repurchase/
│   │   ├── h16_rd_sales/
│   │   ├── ceo_clarity_extended/    # H0.3
│   │   └── _archived/
│   ├── econometric/                 # Stage 4 regression outputs (per-hypothesis)
│   │   ├── h1_cash_holdings/
│   │   ├── h1_1_cash_tsimm/
│   │   ├── h1_2_cash_constraint/
│   │   ├── h2_investment/
│   │   ├── h4_leverage/
│   │   ├── h5_dispersion/
│   │   ├── h5b_johnson_disp/
│   │   ├── h5b_wang_disp/
│   │   ├── h6_cccl/
│   │   ├── h7_illiquidity/
│   │   ├── takeover/                # H9
│   │   ├── h11_prisk_uncertainty/
│   │   ├── h11_prisk_uncertainty_lag/
│   │   ├── h11_prisk_uncertainty_lead/
│   │   ├── h12_payout/             # H12 (named "h12_payout" not "h12_div_intensity")
│   │   ├── h12q_payout/
│   │   ├── h13_capex/
│   │   ├── h13_1_competition/
│   │   ├── h14_bidask_spread/
│   │   ├── h15_repurchase/
│   │   ├── h16_rd_sales/
│   │   ├── ceo_clarity_extended/    # H0.3
│   │   └── reports/
│   └── generate_all_tables.py       # 21-suite LaTeX table generator
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
├── docs/                            # Documentation
│   ├── Draft/                       # Thesis LaTeX draft
│   ├── audits/                      # Code audit reports
│   ├── plans/                       # Implementation plans
│   ├── Prompts/                     # AI prompt templates
│   └── provenance/                  # Data provenance docs (21 suites + Audits/)
│       ├── H1.md ... H16.md         # Per-suite provenance documentation
│       └── Audits/                  # Red-team audit reports per suite
├── scripts/                         # Ad-hoc utility scripts
│   └── compute_missing_sumstats.py
├── logs/                            # Runtime logs (timestamped per run)
├── .planning/                       # GSD planning documents
│   └── codebase/                    # Codebase analysis docs
├── .archive/                        # Archived H8 removal (code, outputs, docs)
│   └── h8_removal/
├── .github/workflows/               # CI configuration
│   ├── ci.yml
│   ├── test.yml
│   └── README.md
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
- Contains: `project.yaml` (step configs, paths, parameters, year range, determinism), `variables.yaml` (variable source definitions for builders)
- Key files: `config/project.yaml` (loaded by all stages via `get_config()`), `config/variables.yaml` (loaded by Stage 3 builders via `load_variable_config()`)

**`src/f1d/`:**
- Purpose: Main installable Python package (src-layout via setuptools)
- Contains: All pipeline code organized by stage and shared utilities
- Key files: `__init__.py` (v6.0.0, re-exports `run_panel_ols`, `get_latest_output_dir`, `OutputResolutionError`)

**`src/f1d/shared/variables/`:**
- Purpose: Individual variable builder classes, one per financial/linguistic variable
- Contains: ~90 builder files, 7 compute engines, base class, utilities, variable registry
- Key files: `base.py` (VariableBuilder interface), `_compustat_engine.py` (singleton loader, 1,342 lines), `panel_utils.py` (canonical industry sample + fyearq attachment), `winsorization.py`, `__init__.py` (central registry of all builders)
- Compute engines: `_compustat_engine.py`, `_crsp_engine.py`, `_ibes_engine.py`, `_ibes_detail_engine.py`, `_linguistic_engine.py`, `_hassan_engine.py`, `_clarity_residual_engine.py`

**`src/f1d/variables/`:**
- Purpose: Stage 3 panel builder scripts that orchestrate variable merging for each hypothesis
- Contains: 19 active `build_h{N}_{name}_panel.py` files, `_archived/` with 5 deprecated builders
- Note: Moderation suites (H1.1, H1.2, H13.1) do NOT have panel builders -- they reuse parent suite panels and merge moderator data at runtime in the econometric runner

**`src/f1d/econometric/`:**
- Purpose: Stage 4 regression scripts for hypothesis testing
- Contains: 22 active `run_h{N}_{name}.py` files, `ceo_presence_probit.py`, `_save_latex_table_6col.py`, `_archived/` with 5 deprecated runners
- Note: Some suites have multiple econometric runners but share a panel (H4 produces H4a + H4b tables from one runner)

**`inputs/`:**
- Purpose: Raw financial and textual data files (NOT committed to git)
- Contains: Compustat quarterly (`comp_na_daily_all/`), CRSP daily (`CRSP_DSF/`), IBES detail (`tr_ibes/`), transcripts, dictionaries, industry classifications, S&P ratings (`compustat_daily_ratings/`), TNIC3 (`TNIC3HHIdata/`)
- Generated: No (externally sourced from WRDS, CapIQ, etc.)
- Committed: No (.gitignore)

**`outputs/`:**
- Purpose: All pipeline outputs organized by stage and hypothesis
- Contains: Parquet files, CSV summaries, LaTeX tables, markdown reports, run manifests
- `outputs/variables/` — Stage 3 panel parquets (19 active hypothesis directories)
- `outputs/econometric/` — Stage 4 regression outputs (22+ hypothesis directories)
- `outputs/generate_all_tables.py` — Master table generator (21 tables)
- Generated: Yes (by pipeline scripts)
- Committed: Selectively (key results committed)

**`tests/`:**
- Purpose: Comprehensive test suite organized by test type
- Contains: unit, integration, regression, performance, verification tests
- Key files: `conftest.py` (shared fixtures), `factories/` (test data factories), `fixtures/` (synthetic data generators)

**`docs/provenance/`:**
- Purpose: Data provenance documentation for all 21 active suites
- Contains: One `.md` file per suite (H1.md, H2.md, ..., H16.md, H0.3.md, H1_1.md, H1_2.md, H13_1.md, H12Q.md) plus `Audits/` subdirectory with red-team audit reports
- Files: `H0.3.md`, `H1.md`, `H1_1.md`, `H1_2.md`, `H2.md`, `H4.md`, `H5.md`, `H6.md`, `H7.md`, `H9.md`, `H11.md`, `H11-Lag.md`, `H11-Lead.md`, `H12.md`, `H12Q.md`, `H13.md`, `H13_1.md`, `H14.md`, `H15.md`
- Red-team audits: `Audits/H{N}_red_team.md` for each suite (comprehensive adversarial review)

## Key File Locations

**Entry Points:**
- `src/f1d/variables/build_h1_cash_holdings_panel.py`: Example Stage 3 entry point
- `src/f1d/econometric/run_h1_cash_holdings.py`: Example Stage 4 entry point
- `src/f1d/sample/assemble_manifest.py`: Stage 1 manifest assembly
- `src/f1d/text/build_linguistic_variables.py`: Stage 2 text processing
- `outputs/generate_all_tables.py`: LaTeX table generation for all 21 tables

**Configuration:**
- `config/project.yaml`: Main pipeline config (year range 2002-2018, step parameters, paths)
- `config/variables.yaml`: Variable source definitions (where each builder loads data from)
- `pyproject.toml`: Package metadata, pytest, ruff, mypy, coverage settings

**Core Logic:**
- `src/f1d/shared/variables/base.py`: VariableBuilder base class, VariableResult, VariableStats dataclasses
- `src/f1d/shared/variables/_compustat_engine.py`: Compustat singleton -- the most critical engine (1,342 lines), computes ~30 accounting variables
- `src/f1d/shared/variables/_crsp_engine.py`: CRSP singleton -- stock returns, volatility, Amihud illiquidity
- `src/f1d/shared/variables/_ibes_detail_engine.py`: IBES Detail singleton -- individual analyst estimates for dispersion
- `src/f1d/shared/variables/panel_utils.py`: Canonical `assign_industry_sample()` and `attach_fyearq()` used by all builders
- `src/f1d/shared/variables/__init__.py`: Central registry of all ~90 builders with `__all__` exports
- `src/f1d/shared/panel_ols.py`: Panel OLS regression with FE and clustered SEs
- `src/f1d/shared/iv_regression.py`: IV2SLS regression for H6 CCCL
- `src/f1d/shared/path_utils.py`: Timestamped output directory resolution
- `src/f1d/shared/config/loader.py`: Config loading with caching

**LaTeX Table Generation:**
- `src/f1d/shared/latex_tables.py`: Basic LaTeX table generation (coefficient + SE format)
- `src/f1d/shared/latex_tables_accounting.py`: Accounting Review style (Estimate + t-value)
- `src/f1d/shared/latex_tables_complete.py`: Complete tables with significance stars
- `outputs/generate_all_tables.py`: Master generator for all 21 publication tables

**Testing:**
- `tests/conftest.py`: Shared pytest fixtures
- `tests/unit/`: Unit tests for shared modules
- `tests/integration/`: Integration tests for pipeline flows
- `tests/verification/`: Dry-run tests for all scripts
- `tests/factories/`: Financial data factories
- `tests/fixtures/`: Synthetic panel data generators

## Naming Conventions

**Files:**
- Variable builders: `{variable_name}.py` in `src/f1d/shared/variables/` (e.g., `cash_holdings.py`, `manager_qa_uncertainty.py`, `johnson_disp.py`, `rd_sales.py`)
- Panel builders: `build_h{N}_{hypothesis_name}_panel.py` in `src/f1d/variables/` (e.g., `build_h16_rd_sales_panel.py`, `build_h5b_johnson_disp_panel.py`)
- Econometric scripts: `run_h{N}_{hypothesis_name}.py` in `src/f1d/econometric/` (e.g., `run_h16_rd_sales.py`, `run_h1_1_cash_tsimm.py`)
- Compute engines: `_{source}_engine.py` with leading underscore (private modules) (e.g., `_compustat_engine.py`, `_ibes_detail_engine.py`)
- Test files: `test_{module_or_feature}.py` in `tests/unit/` or `tests/integration/`
- Provenance docs: `H{N}.md` or `H{N}_{suffix}.md` in `docs/provenance/`
- Red-team audits: `H{N}_red_team.md` in `docs/provenance/Audits/`

**Directories:**
- Stage outputs: `{step_number}_{StepName}/` (e.g., `1.4_AssembleManifest/`, `2_Textual_Analysis/`)
- Hypothesis variable outputs: `h{N}_{name}/` in `outputs/variables/` (e.g., `h16_rd_sales/`, `h5b_johnson_disp/`)
- Hypothesis econometric outputs: `h{N}_{name}/` or descriptive name in `outputs/econometric/` (e.g., `h1_1_cash_tsimm/`, `takeover/`, `ceo_clarity_extended/`)
- Timestamped subdirs: `{YYYY-MM-DD_HHMMSS}/` inside each output directory

**Classes:**
- Variable builders: `{VariableName}Builder` (e.g., `CashHoldingsBuilder`, `JohnsonDispBuilder`, `RDSalesBuilder`)
- Config classes: `{Section}Settings` (e.g., `DataSettings`, `PathsSettings`, `LoggingSettings`)
- Exceptions: Descriptive names (`CollinearityError`, `MulticollinearityError`, `OutputResolutionError`, `ConfigError`)
- Engines: `{Source}Engine` (e.g., `CompustatEngine`, `CRSPEngine`, `IbesDetailEngine`, `LinguisticEngine`)

**Variables/Columns:**
- Financial variables: PascalCase (e.g., `CashHoldings`, `TobinsQ`, `ROA`, `CapexAt`, `RDSales`, `BookLev`, `DebtToCapital`)
- Linguistic variables: Mixed_Case with context (e.g., `Manager_QA_Uncertainty_pct`, `CEO_Pres_Weak_Modal_pct`)
- Lead/lag variables: `{Variable}_lead` or `{Variable}_lag` suffix (e.g., `CashHoldings_lead`, `JohnsonDISP2_lag`)
- Identifiers: lowercase (e.g., `gvkey`, `file_name`, `ceo_id`, `ff12_code`, `fyearq`, `fyearq_int`)
- Industry sample: `industry_sample` column with values `"Main"`, `"Finance"`, `"Utility"`

## Where to Add New Code

**New Hypothesis Test (Standard 8-column suite):**
1. Variable builder (if new DV needed): Create `src/f1d/shared/variables/{variable_name}.py` extending `VariableBuilder`
2. Register builder: Add import and `__all__` entry in `src/f1d/shared/variables/__init__.py`
3. If Compustat-derived: Add column to `COMPUSTAT_COLS` list and computation in `src/f1d/shared/variables/_compustat_engine.py`
4. Add variable config: Add entry in `config/variables.yaml` with source path and column name (if not engine-derived)
5. Panel builder: Create `src/f1d/variables/build_h{N}_{name}_panel.py` importing needed builders. Follow pattern of `build_h16_rd_sales_panel.py` (most recently added standard suite).
6. Regression script: Create `src/f1d/econometric/run_h{N}_{name}.py` with PanelOLS regression. Follow pattern of `run_h16_rd_sales.py`.
7. Add suite to `outputs/generate_all_tables.py` SUITES list for LaTeX table generation
8. Provenance doc: Create `docs/provenance/H{N}.md`
9. Tests: Add unit test in `tests/unit/test_h{N}_variables.py`

**New Moderation/Channel Suite:**
1. Do NOT create a separate panel builder -- reuse the parent suite's panel
2. Create `src/f1d/econometric/run_h{N}_{suffix}.py` that loads parent panel and merges moderator at runtime
3. Follow pattern of `run_h1_1_cash_tsimm.py` (TNIC moderation) or `run_h1_2_cash_constraint.py` (credit constraint moderation)
4. Center the IV, z-score the moderator on Main sample, compute interaction term
5. Add to `outputs/generate_all_tables.py` with `"type": "moderation"`

**New Financial Variable (Compustat-derived):**
1. Add column name to `COMPUSTAT_COLS` list in `src/f1d/shared/variables/_compustat_engine.py` (line ~105)
2. Add raw Compustat columns needed to `REQUIRED_COMPUSTAT_COLS` (line ~146) if not already present
3. Add computation logic in the engine's `_compute_and_winsorize()` method
4. Create wrapper builder: `src/f1d/shared/variables/{variable_name}.py` extending `VariableBuilder`, calling `engine.match_to_manifest()` and extracting the column
5. Register in `src/f1d/shared/variables/__init__.py`

**New Financial Variable (CRSP-derived):**
1. Add column to `CRSP_RETURN_COLS` or `CRSP_BIDASK_COLS` in `src/f1d/shared/variables/_crsp_engine.py`
2. Add computation in engine
3. Create wrapper builder in `src/f1d/shared/variables/`

**New Linguistic Variable:**
1. Ensure the column exists in Stage 2 output (`linguistic_variables_{year}.parquet`)
2. Add column to `LINGUISTIC_PCT_COLUMNS` in `src/f1d/shared/variables/_linguistic_engine.py` if it ends with `_pct`
3. Create builder file: `src/f1d/shared/variables/{variable_name}.py` querying `LinguisticEngine`
4. Register in `src/f1d/shared/variables/__init__.py`

**New Shared Utility:**
- Place in `src/f1d/shared/{utility_name}.py`
- Add tests in `tests/unit/test_{utility_name}.py`

**New Compute Engine (new data source):**
- Create `src/f1d/shared/variables/_{source}_engine.py` with singleton pattern
- Use module-level `_INSTANCE` variable + `threading.Lock()` for thread-safe singleton
- Implement `get_engine()` module-level function (see `_compustat_engine.py` pattern)

## Module Organization

**Package Hierarchy:**
```
f1d                          # Top-level package (src-layout)
├── sample                   # Stage 1: Sample construction
├── text                     # Stage 2: Text processing
├── variables                # Stage 3: Panel builders (orchestration)
├── econometric              # Stage 4: Regression scripts
├── reporting                # Summary statistics generation
└── shared                   # Cross-cutting utilities
    ├── config               # Configuration subsystem
    ├── logging              # Structured logging
    ├── observability        # Runtime monitoring
    ├── outputs              # Output generation
    └── variables            # Variable builders + engines (the core)
```

**Import Patterns:**
- Panel builders import from `f1d.shared.variables` (individual builders) and `f1d.shared.config` (config loading)
- Econometric scripts import from `f1d.shared.panel_ols`, `f1d.shared.path_utils`, `f1d.shared.latex_tables_*`, `f1d.shared.logging.config`, `f1d.shared.outputs`
- Variable builders import their engine from `f1d.shared.variables._{engine}_engine`
- All scripts use `f1d.shared.path_utils.get_latest_output_dir()` to resolve outputs

**Dependency Direction:**
```
econometric → shared.panel_ols, shared.path_utils, shared.latex_tables_*
           → shared.logging, shared.outputs
variables   → shared.variables.*, shared.config, shared.logging, shared.outputs
shared.variables.builders → shared.variables._engines
shared.variables._engines → raw input files (inputs/)
shared.config → config/*.yaml
```

## Special Directories

**`.archive/h8_removal/`:**
- Purpose: Archived H8 Political Risk code, outputs, and docs (replaced by H11)
- Generated: No (manually moved during archive operation)
- Committed: Yes (for historical reference)
- Contains: `src/`, `cache/`, `docs_provenance/`, `outputs_econometric/`, `outputs_variables/`, `tests_regression/`, `planning_debug/`

**`_archived/` (root level):**
- Purpose: Additional archived hypothesis suites not pursued
- Contains: `h10_tone_at_top/` (code, docs -- currently in deleted state per git status)

**`src/f1d/econometric/_archived/`:**
- Purpose: Deprecated econometric scripts
- Contains: `run_h0_1_manager_clarity.py`, `run_h0_2_ceo_clarity.py`, `run_h0_4_ceo_clarity_regime.py`, `run_h0_5_ceo_tone.py`, `run_h3_payout_policy.py`, `run_h13_2_employment.py`, `generate_h03_complete_table.py`

**`src/f1d/variables/_archived/`:**
- Purpose: Deprecated panel builders
- Contains: `build_h0_1_manager_clarity_panel.py`, `build_h0_2_ceo_clarity_panel.py`, `build_h0_5_ceo_tone_panel.py`, `build_h3_payout_policy_panel.py`, `build_h13_2_employment_panel.py`

**`src/f1d/shared/variables/_archived/`:**
- Purpose: Deprecated variable builders
- Contains: `div_stability.py`, `employment_growth_lead.py`, `fcf_growth.py`, `is_div_payer_5yr.py`, `payout_flexibility.py`

**`.planning/`:**
- Purpose: GSD planning documents, codebase analysis
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

*Structure analysis: 2026-03-25*
