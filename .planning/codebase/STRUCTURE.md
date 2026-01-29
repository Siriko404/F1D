# Codebase Structure

**Analysis Date:** 2025-01-29

## Directory Layout

```
F1D/
├── 1_Inputs/                          # Raw data sources (read-only)
│   ├── CCCL instrument/               # SEC comment letters instrument
│   ├── Compustat/                     # Compustat quarterly data
│   ├── CRSP_DSF/                      # CRSP daily stock returns
│   ├── CRSPCompustat_CCM/             # CRSP-Compustat merged linkage
│   ├── Execucomp/                     # Executive compensation data
│   ├── SDC/                           # M&A deal data
│   ├── tr_ibes/                       # IBES analyst forecasts
│   ├── Loughran-McDonald*.csv         # Linguistic dictionary
│   ├── Unified-info.parquet           # Earnings call metadata
│   └── speaker_data_*.parquet         # Transcript data (yearly)
├── 2_Scripts/                         # Processing pipeline
│   ├── 1_Sample/                      # Phase 1: Sample construction
│   │   ├── 1.1_CleanMetadata.py
│   │   ├── 1.2_LinkEntities.py
│   │   ├── 1.3_BuildTenureMap.py
│   │   ├── 1.4_AssembleManifest.py
│   │   └── 1.5_Utils.py               # Script-specific utilities
│   ├── 2_Text/                        # Phase 2: Text processing
│   │   ├── 2.1_TokenizeAndCount.py
│   │   ├── 2.2_ConstructVariables.py
│   │   └── 2.3_Report.py              # Verification & reporting
│   ├── 3_Financial/                   # Phase 3: Financial features
│   │   ├── 3.1_FirmControls.py
│   │   ├── 3.2_MarketVariables.py
│   │   ├── 3.3_EventFlags.py
│   │   ├── 3.4_Utils.py               # Script-specific utilities
│   │   └── 3.0_BuildFinancialFeatures.py  # Orchestrator (archived)
│   ├── 4_Econometric/                 # Phase 4: Econometric analysis
│   │   ├── 4.1_EstimateCeoClarity.py
│   │   ├── 4.1.1_EstimateCeoClarity_CeoSpecific.py
│   │   ├── 4.1.2_EstimateCeoClarity_Extended.py
│   │   ├── 4.1.3_EstimateCeoClarity_Regime.py
│   │   ├── 4.1.4_EstimateCeoTone.py
│   │   ├── 4.2_LiquidityRegressions.py
│   │   ├── 4.3_TakeoverHazards.py
│   │   └── 4.4_GenerateSummaryStats.py
│   ├── shared/                        # Shared utilities (20+ modules)
│   │   ├── observability_utils.py
│   │   ├── path_utils.py
│   │   ├── data_validation.py
│   │   ├── regression_utils.py
│   │   ├── regression_helpers.py
│   │   ├── regression_validation.py
│   │   ├── string_matching.py
│   │   ├── financial_utils.py
│   │   ├── symlink_utils.py
│   │   ├── chunked_reader.py
│   │   ├── reporting_utils.py
│   │   ├── cli_validation.py
│   │   ├── env_validation.py
│   │   ├── subprocess_validation.py
│   │   ├── dependency_checker.py
│   │   ├── metadata_utils.py
│   │   ├── industry_utils.py
│   │   ├── data_loading.py
│   │   └── __init__.py
│   ├── ARCHIVE/                       # Deprecated scripts (kept for reference)
│   └── ARCHIVE_OLD/                   # Previous versions
├── 3_Logs/                            # Execution logs
│   ├── 1.1_CleanMetadata/
│   ├── 1.2_LinkEntities/
│   ├── ... (one subdir per script)
│   └── {step_name}/{timestamp}.log    # Timestamped log files
├── 4_Outputs/                         # Processed data & results
│   ├── 1.1_CleanMetadata/
│   │   └── {timestamp}/
│   │       ├── metadata_cleaned.parquet
│   │       ├── variable_reference.csv
│   │       └── latest/                # Symlink to most recent run
│   ├── 1.2_LinkEntities/
│   ├── ... (one subdir per script)
│   └── {step_name}/{timestamp}/
├── config/
│   └── project.yaml                   # Central configuration (paths, seeds, params)
├── tests/                             # Test suite
│   ├── unit/                          # Unit tests for shared modules
│   ├── integration/                   # End-to-end pipeline tests
│   ├── regression/                    # Output stability tests
│   ├── fixtures/                      # Test data
│   └── conftest.py                    # Pytest configuration & fixtures
├── .planning/                         # Project planning & docs
│   ├── codebase/                      # Codebase analysis docs (this file)
│   ├── phases/                        # Implementation phases
│   ├── quick/                         # Quick verification tasks
│   └── STATE.md                       # Project state & decisions
├── .github/
│   └── workflows/                     # CI/CD configuration
├── .claude/
│   └── settings.json                  # Claude Code project settings
├── README.md                          # Project documentation
├── prd.md                             # Product requirements document
├── DEPENDENCIES.md                    # Dependency documentation
├── UPGRADE_GUIDE.md                   # Upgrade procedures
├── pyproject.toml                     # Poetry/pytest configuration
├── requirements.txt                   # Python dependencies
└── .gitignore
```

## Directory Purposes

**1_Inputs/:**
- Purpose: Raw, immutable data sources from external providers
- Contains: Earnings call transcripts, financial data (CRSP, Compustat, IBES), reference files (LM dictionary, CEO data)
- Key files: `Unified-info.parquet`, `speaker_data_*.parquet`, `Loughran-McDonald_MasterDictionary_1993-2024.csv`

**2_Scripts/:**
- Purpose: Data processing pipeline (4 phases, 18 active scripts)
- Contains: Sequential scripts for sample building, text processing, financial features, econometric analysis
- Key files: `1_Sample/1.4_AssembleManifest.py` (outputs master_sample_manifest), `4_Econometric/4.1_EstimateCeoClarity.py` (estimates CEO clarity)

**2_Scripts/shared/:**
- Purpose: Reusable utilities for I/O, validation, regression, string matching
- Contains: 20+ modules providing common functionality across pipeline scripts
- Key files: `observability_utils.py` (DualWriter), `data_validation.py` (schema validation), `string_matching.py` (fuzzy matching)

**3_Logs/:**
- Purpose: Execution logs with progress stats, errors, checksums
- Contains: One subdirectory per script with timestamped `.log` files
- Key files: `3_Logs/{step_name}/{timestamp}.log` (full execution trace)

**4_Outputs/:**
- Purpose: Processed datasets, regression results, reports
- Contains: One subdirectory per script, each with timestamped runs and `latest/` symlink
- Key files: `master_sample_manifest.parquet`, `ceo_clarity_scores.parquet`, `regression_results.txt`

**tests/:**
- Purpose: Unit, integration, and regression tests
- Contains: Test files, fixtures, pytest configuration
- Key files: `conftest.py` (shared fixtures), `unit/test_data_validation.py`, `regression/test_output_stability.py`

**config/:**
- Purpose: Central configuration for the entire pipeline
- Contains: `project.yaml` (single source of truth for paths, seeds, processing parameters)
- Key files: `config/project.yaml`

## Key File Locations

**Entry Points:**
- `2_Scripts/1_Sample/1.1_CleanMetadata.py`: First script in pipeline (cleans metadata)
- `2_Scripts/4_Econometric/4.4_GenerateSummaryStats.py`: Final script (generates summary statistics)

**Configuration:**
- `config/project.yaml`: Central configuration (paths, seeds, thread count, step-specific params)
- `pyproject.toml`: Pytest configuration, coverage settings
- `requirements.txt`: Python dependencies

**Core Logic:**
- `2_Scripts/1_Sample/1.4_AssembleManifest.py`: Assembles final sample manifest
- `2_Scripts/4_Econometric/4.1_EstimateCeoClarity.py`: Estimates CEO clarity (main model)
- `2_Scripts/shared/regression_utils.py`: Fixed effects regression helpers
- `2_Scripts/shared/string_matching.py`: Company name fuzzy matching

**Testing:**
- `tests/conftest.py`: Pytest fixtures and configuration
- `tests/unit/test_data_validation.py`: Schema validation tests
- `tests/regression/test_output_stability.py`: Bitwise output reproducibility tests

## Naming Conventions

**Files:**
- Pipeline scripts: `{Step}.{Substep}_{PascalCaseName}.py` (e.g., `1.1_CleanMetadata.py`)
- Shared modules: `{category}_{utility}.py` (e.g., `observability_utils.py`, `path_utils.py`)
- Test files: `test_{module}.py` (e.g., `test_data_validation.py`)
- Outputs: `{dataset}_{year}.parquet` or `{description}.parquet` (e.g., `linguistic_variables_2002.parquet`)

**Directories:**
- Phase directories: `{PhaseNumber}_{Theme}/` (e.g., `1_Sample/`, `2_Text/`, `3_Financial/`, `4_Econometric/`)
- Log directories: `{Step}_{Description}/` (e.g., `1.1_CleanMetadata/`, `4.1_EstimateCeoClarity/`)
- Output directories: `{Step}_{Description}/{timestamp}/` (e.g., `1.4_AssembleManifest/2025-01-24_153000/`)

**Variables:**
- Linguistic variables: `{Speaker}_{Context}_{Category}_pct` (e.g., `Manager_QA_Uncertainty_pct`)
- Financial controls: PascalCase from Compustat fields (e.g., `Size`, `BM`, `Lev`, `ROA`)
- Regression outputs: `{Measure}_{suffix}` (e.g., `ClarityCEO`, `ClarityRegime`, `StockRet`)

## Where to Add New Code

**New Feature (New Processing Step):**
- Primary code: `2_Scripts/{PhaseNumber}_{Theme}/{Step}.{Substep}_{PascalCaseName}.py`
- Tests: `tests/unit/test_{step_name}.py`
- If script is 4.1.5 (variant of 4.1): Place in `2_Scripts/4_Econometric/4.1.5_{Description}.py`

**New Component/Module (Shared Utility):**
- Implementation: `2_Scripts/shared/{category}_{utility}.py`
- Tests: `tests/unit/test_{utility}.py`
- Example: `2_Scripts/shared/timing_utils.py` → `tests/unit/test_timing_utils.py`

**New Regression Model (Variant of Existing):**
- Implementation: `2_Scripts/4_Econometric/4.{StepNumber}.{Variant}_{Description}.py`
- Example: `4.1.5_EstimateCeoClarity_WithBoardIndependence.py`
- Update regression helpers: `2_Scripts/shared/regression_helpers.py` if new data patterns

**Utilities:**
- Shared helpers: `2_Scripts/shared/{category}_utils.py`
- Example: `2_Scripts/shared/nlp_utils.py` for text processing helpers

**Test Fixtures:**
- Test data: `tests/fixtures/{dataset}.{extension}`
- Shared fixtures: `tests/conftest.py` (add new `@pytest.fixture` functions)

## Special Directories

**ARCHIVE/:**
- Purpose: Deprecated scripts kept for reference (not executed)
- Generated: No (manually moved when deprecated)
- Committed: Yes
- Example: Old orchestrator scripts, broken iterations

**ARCHIVE_OLD/:**
- Purpose: Previous versions of scripts (before major refactoring)
- Generated: No (manually moved when superseded)
- Committed: Yes
- Example: `2.0b_BuildMasterTenureMap.py` (superseded by Phase 1 scripts)

**___Archive/ (root level):**
- Purpose: Temporary exploration/debug scripts
- Generated: No (ad-hoc development)
- Committed: Yes (for traceability)
- Example: `investigate_linking.py`, `debug_coverage.py`

**.planning/:**
- Purpose: Project planning documents, phase plans, quick verification tasks
- Generated: Yes (by GSD commands)
- Committed: Yes
- Subdirectories: `codebase/` (analysis docs), `phases/` (implementation plans), `quick/` (verification tasks)

**BACKUP_*:**
- Purpose: Timestamped backups of critical files (e.g., `config/project.yaml`)
- Generated: Yes (before major changes)
- Committed: Yes
- Example: `BACKUP_20260114_191340/project.yaml`

**.github/workflows/:**
- Purpose: CI/CD pipeline configuration (GitHub Actions)
- Generated: No (manually created)
- Committed: Yes
- Used by: GitHub Actions on push/PR

---

*Structure analysis: 2025-01-29*
