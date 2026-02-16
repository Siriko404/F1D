# Codebase Structure

**Analysis Date:** 2026-02-15

## Directory Layout

```
F1D/
├── 1_Inputs/                    # Raw immutable data (READ-ONLY)
│   ├── Earnings_Calls_Transcripts/
│   │   ├── Unified-info.parquet
│   │   └── speaker_data_{YYYY}.parquet
│   ├── LM_dictionary/
│   │   └── Loughran-McDonald_MasterDictionary_1993-2024.csv
│   ├── CRSPCompustat_CCM/
│   ├── CRSP_DSF/
│   ├── comp_na_daily_all/
│   ├── Execucomp/
│   ├── tr_ibes/
│   ├── SDC/
│   └── CCCL instrument/
├── 3_Logs/                     # Execution logs
│   ├── 1.0_BuildSampleManifest/
│   ├── 2.1_TokenizeAndCount/
│   ├── 2.2_ConstructVariables/
│   ├── 3_Financial_V2/
│   └── 4_Econometric_V2/
├── 4_Outputs/                  # Timestamped processing outputs
│   ├── 1.4_AssembleManifest/
│   │   └── latest/ -> most recent timestamped run
│   ├── 2_Textual_Analysis/
│   ├── 3_Financial_V2/
│   └── 4_Econometric_V2/
├── src/                         # Package source (src-layout)
│   └── f1d/
│       ├── __init__.py
│       ├── sample/               # Stage 1: Sample construction
│       ├── text/                 # Stage 2: Text processing
│       ├── financial/             # Stage 3: Financial features
│       ├── econometric/           # Stage 4: Econometric analysis
│       └── shared/               # Tier 1: Cross-cutting utilities
├── _archive/                    # Legacy code (deprecated)
├── config/                       # Project configuration
│   └── project.yaml
├── docs/                         # Documentation
├── .planning/                    # GSD planning artifacts
│   ├── phases/                    # Individual phase plans
│   ├── milestones/                 # Phase milestones
│   ├── codebase/                   # Codebase architecture docs (this directory)
│   └── ROADMAP.md                # Project roadmap
├── tests/                        # Test suite
│   ├── unit/                       # Unit tests
│   ├── fixtures/                   # Test fixtures
│   └── conftest.py                # Pytest configuration
├── .github/workflows/           # CI/CD configuration
├── pyproject.toml                # Package configuration
├── requirements.txt                # Python dependencies
└── README.md                     # Project documentation
```

## Directory Purposes

**1_Inputs/** (Raw Data)**
- Purpose: Immutable input datasets - READ ONLY
- Contains: Earnings call transcripts, LM dictionary, CRSP/Compustat/CCM, IBES, Execucomp, SDC, CCCL instrument
- Key files: `Unified-info.parquet`, `speaker_data_*.parquet`, `Loughran-McDonald_MasterDictionary_1993-2024.csv`

**3_Logs/** (Execution Logs)**
- Purpose: Structured execution logs with dual terminal/file output
- Contains: Timestamped log files per script execution
- Organization: `3_Logs/{script_name}/{timestamp}.log`

**4_Outputs/** (Processing Results)**
- Purpose: Timestamped output directories with latest symlinks
- Contains: All script outputs organized by stage and script name
- Organization: `4_Outputs/{stage}/{script_name}/{timestamp}/` + `latest/` symlink
- Pattern: Scripts create `output_dir/timestamp/` for each run

**src/f1d/sample/** (Stage 1)**
- Purpose: Sample construction and entity linking
- Contains: Clean metadata, CCM linking, CEO tenure map, manifest assembly
- Key scripts: `1.0_BuildSampleManifest.py` (orchestrator), `1.1_CleanMetadata.py`, `1.2_LinkEntities.py`, `1.3_BuildTenureMap.py`, `1.4_AssembleManifest.py`

**src/f1d/text/** (Stage 2)**
- Purpose: Text processing and linguistic analysis
- Contains: Tokenization, variable construction, verification
- Key scripts: `tokenize_and_count.py`, `construct_variables.py`, `verify_step2.py`

**src/f1d/financial/** (Stage 3)**
- Purpose: Financial feature engineering with V1/V2 variants
- Contains: Firm controls, market variables, event flags, hypothesis-specific variables
- V1: `3.0_BuildFinancialFeatures.py`, `3.1_FirmControls.py`, `3.2_MarketVariables.py`, `3.3_EventFlags.py`
- V2: `3.1_H1Variables.py` through `3.11_H9_StyleFrozen.py` (Hypothesis H1-H9)

**src/f1d/econometric/** (Stage 4)**
- Purpose: Econometric analysis and hypothesis testing
- Contains: CEO clarity estimation, regressions, survival analysis
- V1: `4.1.1_EstimateCeoClarity.py`, `4.1.2_EstimateCeoClarity_Extended.py`, `4.1.3_EstimateCeoClarity_Regime.py`, `4.1.4_EstimateCeoTone.py`, `4.2_LiquidityRegressions.py`, `4.3_TakeoverHazards.py`, `4.4_GenerateSummaryStats.py`
- V2: `4.1_H1CashHoldingsRegression.py` through `4.11_H9_Regression.py` (Hypothesis H1-H9)

**src/f1d/shared/** (Tier 1)**
- Purpose: Cross-cutting utilities for all stages
- Contains: Configuration, logging, path utilities, data validation, regression helpers, observability
- Key modules: `config/` (loader, paths, step_configs), `logging/` (config, handlers, context), `observability/` (files, memory, throughput, logging, stats), `path_utils.py`, `panel_ols.py`, `data_validation.py`, `regression_utils.py`, `centering.py`, `industry_utils.py`

**_archive/** (Legacy Code)**
- Purpose: Deprecated code preserved for reference
- Contains: `legacy_archive/`, `2_Scripts_v5.1_legacy`
- Generated: Not to be modified, only for historical reference

**config/** (Configuration)**
- Purpose: Project-level configuration
- Key files: `project.yaml` (main config), `datasets.py` (dataset definitions)

**docs/** (Documentation)**
- Purpose: Technical documentation
- Contains: Architecture standards, coding conventions, testing patterns

**.planning/** (GSD Artifacts)**
- Purpose: GSD workflow planning and tracking
- Contains: `phases/` (individual plans), `milestones/` (progress tracking), `codebase/` (this directory), `ROADMAP.md`, `PROJECT.md`

**tests/** (Test Suite)**
- Purpose: Unit, integration, and regression tests
- Contains: `unit/` (Tier 1/2 tests), `fixtures/` (baseline checksums), `conftest.py` (pytest config)

## Key File Locations

**Entry Points:**
- `src/f1d/__init__.py`: Package entry point with public API
- `src/f1d/sample/1.0_BuildSampleManifest.py`: Stage 1 orchestrator
- `src/f1d/sample/1.4_AssembleManifest.py`: Final sample manifest output

**Configuration:**
- `config/project.yaml`: Main pipeline configuration
- `pyproject.toml`: Package dependencies and tooling configuration

**Core Utilities:**
- `src/f1d/shared/path_utils.py`: Path resolution and output directory handling
- `src/f1d/shared/config/loader.py`: Configuration loading from YAML
- `src/f1d/shared/observability_utils.py`: DualWriter, memory tracking, stats
- `src/f1d/shared/panel_ols.py`: Panel OLS wrapper for regressions

**Stage 1 Key Files:**
- `src/f1d/sample/1.1_CleanMetadata.py`: Metadata cleaning
- `src/f1d/sample/1.2_LinkEntities.py`: CCM entity linking (4-tier)
- `src/f1d/sample/1.3_BuildTenureMap.py`: CEO tenure panel construction
- `src/f1d/sample/1.4_AssembleManifest.py`: Final manifest assembly

**Stage 2 Key Files:**
- `src/f1d/text/tokenize_and_count.py`: LM dictionary tokenization
- `src/f1d/text/construct_variables.py`: Linguistic variable construction
- `src/f1d/text/verify_step2.py`: Stage 2 output verification

**Stage 3 Key Files:**
- `src/f1d/financial/v1/3.0_BuildFinancialFeatures.py`: V1 orchestrator
- `src/f1d/financial/v2/3.1_H1Variables.py`: H1 cash holdings variables
- `src/f1d/financial/v2/3.2_H2Variables.py`: H2 investment efficiency
- `src/f1d/financial/v2/3.8_H8TakeoverVariables.py`: H8 takeover hazard variables

**Stage 4 Key Files:**
- `src/f1d/econometric/v2/4.1_H1CashHoldingsRegression.py`: H1 regression (cash holdings)
- `src/f1d/econometric/v2/4.2_H2InvestmentEfficiencyRegression.py`: H2 regression
- `src/f1d/econometric/v2/4.6_H6CCCLRegression.py`: H6 IV regression (CCCL instrument)
- `src/f1d/econometric/v2/4.8_H8TakeoverRegression.py`: H8 takeover hazard regression
- `src/f1d/econometric/v2/4.9_CEOFixedEffects.py`: CEO fixed effects estimation

**Testing:**
- `tests/conftest.py`: Pytest configuration
- `tests/unit/test_observability_helpers.py`: Unit tests for observability utilities

## Naming Conventions

**Files:**
- Stage scripts: `{number}.{description}.py` (e.g., `1.0_BuildSampleManifest.py`, `2.1_TokenizeAndCount.py`)
- Hypothesis scripts: `{number}_H{number}_{Description}.py` (V2 Stage 3/4)
- Utility modules: `{description}.py` (e.g., `path_utils.py`, `data_validation.py`)
- Log files: `{timestamp}.log` (YYYY-MM-DD_HHMMSS format)
- Output directories: `{timestamp}/` (YYYY-MM-DD_HHMMSS format)

**Directories:**
- Stage-specific: `1_Inputs/`, `2_Text/` (legacy), `3_Financial/` (legacy)
- Organized: `src/f1d/{stage}/` with `v1/` and `v2/` subdirectories
- Logging: `3_Logs/{script_name}/`
- Outputs: `4_Outputs/{stage}/{script_name}/`

## Where to Add New Code

**New Feature (New Hypothesis):**
- Primary code: `src/f1d/financial/v2/` (Stage 3: Hypothesis variables)
- Regression code: `src/f1d/econometric/v2/` (Stage 4: Hypothesis tests)
- Tests: `tests/unit/test_{feature_name}.py`
- Follow pattern: Numbered scripts `4.X_H{number}_{Description}.py`

**New Shared Utility:**
- Implementation: `src/f1d/shared/{utility_name}.py`
- Tests: `tests/unit/test_{utility_name}.py`
- Export in: `src/f1d/shared/__init__.py` for public API

**New Stage 1 (Sample) Functionality:**
- Implementation: `src/f1d/sample/{number}.{description}.py`
- Tests: `tests/unit/test_sample_{description}.py`

**New Stage 2 (Text) Functionality:**
- Implementation: `src/f1d/text/{description}.py`
- Tests: `tests/unit/test_text_{description}.py`

**New Stage 3 (Financial) Functionality:**
- Implementation: `src/f1d/financial/v2/{number}_H{number}_{Description}.py`
- Tests: `tests/unit/test_financial_{description}.py`

**New Stage 4 (Econometric) Functionality:**
- Implementation: `src/f1d/econometric/v2/{number}_H{number}_{Description}.py`
- Tests: `tests/unit/test_econometric_{description}.py`

**New Configuration:**
- Add to: `config/project.yaml`
- Schema: Follow existing YAML structure with section naming

**Documentation:**
- Add to: `docs/`
- Follow existing documentation patterns

## Special Directories

**_archive/**
- Purpose: Legacy code preservation (deprecated, read-only)
- Generated: No (manual archiving)
- Committed: Yes (for reference)

**1_Inputs/**
- Purpose: Raw immutable data (READ-ONLY)
- Generated: No (external data sources)
- Modified: Never (inputs are treated as immutable)

**tests/**
- Purpose: Test suite execution and fixtures
- Generated: Code + fixtures
- Committed: Yes

**.planning/**
- Purpose: GSD workflow artifacts (phase plans, milestones, roadmap)
- Generated: GSD agents (automatic)
- Committed: Yes (tracked in version control)

**.github/workflows/**
- Purpose: GitHub Actions CI/CD pipeline
- Generated: Manual configuration
- Committed: Yes

---

*Structure analysis: 2026-02-15*
