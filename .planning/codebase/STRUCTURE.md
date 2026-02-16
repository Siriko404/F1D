# Codebase Structure

**Analysis Date:** 2026-02-15

## Directory Layout

```
[project-root]/
├── 1_Inputs/                 # Raw input data (immutable)
│   ├── Earnings_Calls_Transcripts/
│   │   ├── Unified-info.parquet
│   │   └── speaker_data_2002.parquet through speaker_data_2018.parquet
│   ├── LM_dictionary/
│   │   └── Loughran-McDonald_MasterDictionary_1993-2024.csv
│   ├── CRSP_DSF/
│   ├── CRSPCompustat_CCM/
│   ├── comp_na_daily_all/
│   ├── tr_ibes/
│   ├── Execucomp/
│   ├── SDC/
│   ├── CCCL_instrument/
│   ├── FF1248/
│   ├── FirmLevelRisk/
│   ├── Manager_roles/
│   └── SEC_Edgar_Letters/
├── 3_Logs/                   # Execution logs (timestamped)
│   ├── 1.1_CleanMetadata/
│   ├── 1.2_LinkEntities/
│   ├── 1.3_BuildTenureMap/
│   ├── 1.4_AssembleManifest/
│   ├── 2.1_TokenizeAndCount/
│   ├── 2.2_ConstructVariables/
│   ├── 2.3_VerifyStep2/
│   ├── 3_Financial_Features/
│   ├── 3_Financial_V2/
│   ├── 4.1_EstimateManagerClarity/
│   ├── 4.2_LiquidityRegressions/
│   ├── 4.3_TakeoverHazards/
│   ├── 4.4_GenerateSummaryStats/
│   └── 4_Econometric_V2/
├── 4_Outputs/                # Pipeline outputs (timestamped)
│   ├── 1.0_BuildSampleManifest/
│   ├── 1.1_CleanMetadata/
│   ├── 1.2_LinkEntities/
│   ├── 1.3_BuildTenureMap/
│   ├── 1.4_AssembleManifest/
│   ├── 2_Textual_Analysis/
│   ├── 3_Financial_Features/
│   ├── 3_Financial_V2/
│   ├── 4.1_ManagerClarity/
│   ├── 4.2_LiquidityRegressions/
│   ├── 4.3_TakeoverHazards/
│   └── 4_Econometric_V2/
├── .benchmarks/              # Performance benchmark results
├── .claude/                 # Claude AI assistant configuration
├── .github/                 # GitHub Actions workflows
│   └── workflows/
├── .git/                   # Git repository (excluded)
├── .planning/               # GSD planning documents
│   ├── codebase/            # Codebase analysis docs (ARCHITECTURE.md, STRUCTURE.md)
│   ├── phases/              # Phase plans and summaries
│   ├── milestones/          # Milestone tracking
│   ├── research/            # Research notes
│   └── verification/        # Verification scripts
├── _archive/                # Deprecated/archived code
│   └── legacy_archive/
├── config/                  # Project configuration
│   └── project.yaml         # Main configuration file
├── docs/                    # Documentation standards
│   ├── ARCHITECTURE_STANDARD.md
│   ├── CODE_QUALITY_STANDARD.md
│   ├── CONFIG_TESTING_STANDARD.md
│   ├── DOC_TOOLING_STANDARD.md
│   ├── DOCSTRING_COMPLIANCE.md
│   ├── SCRIPT_DOCSTANDARD.md
│   ├── TIER_MANIFEST.md
│   ├── UPGRADE_GUIDE.md
│   ├── VARIABLE_CATALOG_V1.md
│   └── VARIABLE_CATALOG_V2_V3.md
├── src/                     # Source code (src-layout package)
│   └── f1d/
│       ├── __init__.py
│       ├── sample/             # Stage 1: Sample construction
│       │   ├── __init__.py
│       │   ├── 1.0_BuildSampleManifest.py
│       │   ├── 1.1_CleanMetadata.py
│       │   ├── 1.2_LinkEntities.py
│       │   ├── 1.3_BuildTenureMap.py
│       │   ├── 1.4_AssembleManifest.py
│       │   └── 1.5_Utils.py
│       ├── text/               # Stage 2: Text processing
│       │   ├── __init__.py
│       │   ├── tokenize_and_count.py
│       │   ├── construct_variables.py
│       │   ├── report_step2.py
│       │   └── verify_step2.py
│       ├── financial/           # Stage 3: Financial features
│       │   ├── __init__.py
│       │   ├── v1/            # V1 methodology
│       │   │   ├── __init__.py
│       │   │   ├── 3.0_BuildFinancialFeatures.py
│       │   │   ├── 3.1_FirmControls.py
│       │   │   ├── 3.2_MarketVariables.py
│       │   │   ├── 3.3_EventFlags.py
│       │   │   └── 3.4_Utils.py
│       │   └── v2/            # V2 methodology (active, not deprecated)
│       │       ├── __init__.py
│       │       ├── 3.1_H1Variables.py
│       │       ├── 3.2_H2Variables.py
│       │       ├── 3.2a_AnalystDispersionPatch.py
│       │       ├── 3.3_H3Variables.py
│       │       ├── 3.5_H5Variables.py
│       │       ├── 3.6_H6Variables.py
│       │       ├── 3.7_H7IlliquidityVariables.py
│       │       ├── 3.8_H8TakeoverVariables.py
│       │       ├── 3.9_H2_BiddleInvestmentResidual.py
│       │       ├── 3.10_H2_PRiskUncertaintyMerge.py
│       │       ├── 3.11_H9_StyleFrozen.py
│       │       ├── 3.12_H9_PRiskFY.py
│       │       └── 3.13_H9_AbnormalInvestment.py
│       ├── econometric/         # Stage 4: Econometric analysis
│       │   ├── __init__.py
│       │   ├── v1/            # V1 methodology
│       │   │   ├── __init__.py
│       │   │   ├── 4.1_EstimateManagerClarity.py
│       │   │   ├── 4.1.1_EstimateCeoClarity.py
│       │   │   ├── 4.1.2_EstimateCeoClarity_Extended.py
│       │   │   ├── 4.1.3_EstimateCeoClarity_Regime.py
│       │   │   ├── 4.1.4_EstimateCeoTone.py
│       │   │   ├── 4.2_LiquidityRegressions.py
│       │   │   ├── 4.3_TakeoverHazards.py
│       │   │   └── 4.4_GenerateSummaryStats.py
│       │   └── v2/            # V2 methodology (active, not deprecated)
│       │       ├── __init__.py
│       │       ├── 4.1_H1CashHoldingsRegression.py
│       │       ├── 4.2_H2InvestmentEfficiencyRegression.py
│       │       ├── 4.3_H3PayoutPolicyRegression.py
│       │       ├── 4.4_H4_LeverageDiscipline.py
│       │       ├── 4.5_H5DispersionRegression.py
│       │       ├── 4.6_H6CCCLRegression.py
│       │       ├── 4.7_H7IlliquidityRegression.py
│       │       ├── 4.8_H8TakeoverRegression.py
│       │       ├── 4.9_CEOFixedEffects.py
│       │       ├── 4.10_H2_PRiskUncertainty_Investment.py
│       │       └── 4.11_H9_Regression.py
│       └── shared/             # Tier 1: Shared utilities
│           ├── __init__.py
│           ├── centering.py
│           ├── chunked_reader.py
│           ├── cli_validation.py
│           ├── config/
│           │   ├── __init__.py
│           │   ├── base.py
│           │   ├── datasets.py
│           │   ├── env.py
│           │   ├── hashing.py
│           │   ├── loader.py
│           │   ├── paths.py
│           │   ├── step_configs.py
│           │   └── string_matching.py
│           ├── data_loading.py
│           ├── data_validation.py
│           ├── dependency_checker.py
│           ├── diagnostics.py
│           ├── dual_writer.py
│           ├── env_validation.py
│           ├── financial_utils.py
│           ├── industry_utils.py
│           ├── iv_regression.py
│           ├── latex_tables.py
│           ├── logging/
│           │   ├── __init__.py
│           │   ├── config.py
│           │   ├── context.py
│           │   └── handlers.py
│           ├── metadata_utils.py
│           ├── observability/
│           │   ├── __init__.py
│           │   ├── anomalies.py
│           │   ├── files.py
│           │   ├── logging.py
│           │   ├── memory.py
│           │   ├── stats.py
│           │   └── throughput.py
│           ├── observability_utils.py
│           ├── output_schemas.py
│           ├── panel_ols.py
│           ├── path_utils.py
│           ├── regression_helpers.py
│           ├── regression_utils.py
│           ├── regression_validation.py
│           ├── reporting_utils.py
│           ├── sample_utils.py
│           ├── string_matching.py
│           ├── subprocess_validation.py
│           └── 3_Logs/            # Logs generated within src (data staging)
├── tests/                   # Test suite
│   ├── conftest.py          # Pytest configuration and fixtures
│   ├── factories/           # Test data factories
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── financial.py
│   ├── fixtures/           # Test fixture files
│   ├── integration/        # Integration tests
│   ├── performance/        # Performance tests
│   ├── regression/         # Regression tests
│   ├── unit/              # Unit tests
│   ├── utils/             # Test utilities
│   └── verification/       # Verification tests
├── .coveragerc             # Coverage configuration
├── .coverage               # Coverage results
├── .env.example            # Environment variable template
├── .gitignore              # Git ignore rules
├── .pre-commit-config.yaml  # Pre-commit hooks
├── pyproject.toml          # Package configuration (PEP 621)
├── README.md               # Project documentation
├── requirements.txt         # Python dependencies
├── SECURITY.md             # Security policy
└── SCALING.md             # Scaling and performance guide
```

## Directory Purposes

**1_Inputs:**
- Purpose: Raw input data storage (immutable reference data)
- Contains: Earnings call transcripts, financial datasets, dictionaries, reference files
- Key files: `Unified-info.parquet`, `speaker_data_*.parquet`, `Loughran-McDonald_MasterDictionary_1993-2024.csv`

**3_Logs:**
- Purpose: Execution logs with timestamped directories
- Contains: Script execution logs, progress tracking, error logs
- Structure: `3_Logs/<script_name>/<timestamp>.log`

**4_Outputs:**
- Purpose: Pipeline outputs with timestamped directories
- Contains: Processed datasets, regression results, tables, stats.json files
- Structure: `4_Outputs/<script_name>/<timestamp>/` with `latest/` symlinks

**src/f1d:**
- Purpose: Source code package (src-layout)
- Contains: All Python modules organized by pipeline stage
- Key files: `__init__.py` (package init), shared utilities

**src/f1d/sample:**
- Purpose: Stage 1 - Sample construction scripts
- Contains: Metadata cleaning, entity linking, tenure mapping, manifest assembly
- Key files: `1.1_CleanMetadata.py`, `1.2_LinkEntities.py`, `1.3_BuildTenureMap.py`, `1.4_AssembleManifest.py`

**src/f1d/text:**
- Purpose: Stage 2 - Text processing scripts
- Contains: Tokenization, variable construction, verification
- Key files: `tokenize_and_count.py`, `construct_variables.py`, `verify_step2.py`

**src/f1d/financial:**
- Purpose: Stage 3 - Financial feature construction
- Contains: V1 methodology (base financial features) and V2 methodology (hypothesis-specific variables)
- Key files: `v1/3.1_FirmControls.py`, `v1/3.2_MarketVariables.py`, `v2/3.1_H1Variables.py`

**src/f1d/econometric:**
- Purpose: Stage 4 - Econometric analysis scripts
- Contains: V1 methodology (CEO clarity, liquidity, takeover) and V2 methodology (hypothesis testing)
- Key files: `v1/4.1_EstimateManagerClarity.py`, `v2/4.1_H1CashHoldingsRegression.py`

**src/f1d/shared:**
- Purpose: Tier 1 - Cross-cutting utilities
- Contains: Configuration, logging, data loading, validation, path utilities, regression helpers
- Key files: `config/`, `logging/`, `path_utils.py`, `data_loading.py`, `panel_ols.py`

**config:**
- Purpose: Project configuration
- Contains: YAML configuration files
- Key files: `project.yaml`

**docs:**
- Purpose: Documentation standards and guides
- Contains: Architecture standard, code quality standard, testing standards
- Key files: `ARCHITECTURE_STANDARD.md`, `CODE_QUALITY_STANDARD.md`, `CONFIG_TESTING_STANDARD.md`

**tests:**
- Purpose: Test suite
- Contains: Unit tests, integration tests, regression tests, performance tests, verification tests
- Key files: `conftest.py`, `factories/`, `unit/`, `integration/`

**_archive:**
- Purpose: Deprecated/archived code
- Contains: Legacy scripts and implementations no longer in active use
- Generated: No (manually maintained)
- Committed: Yes (for historical reference)

**.planning:**
- Purpose: GSD planning and documentation
- Contains: Phase plans, milestones, research notes, codebase analysis
- Generated: Yes (by GSD workflow)
- Committed: Yes

## Key File Locations

**Entry Points:**
- `src/f1d/sample/1.1_CleanMetadata.py`: Sample construction entry point
- `src/f1d/text/tokenize_and_count.py`: Text processing entry point
- `src/f1d/financial/v1/3.0_BuildFinancialFeatures.py`: Financial features orchestrator
- `src/f1d/econometric/v1/4.1_EstimateManagerClarity.py`: Econometric analysis entry point

**Configuration:**
- `config/project.yaml`: Main project configuration
- `pyproject.toml`: Package configuration and dependencies
- `.coveragerc`: Coverage configuration
- `requirements.txt`: Python dependencies list

**Core Logic:**
- `src/f1d/shared/config/`: Configuration loading and validation
- `src/f1d/shared/logging/`: Logging infrastructure
- `src/f1d/shared/data_loading.py`: Data loading and merge utilities
- `src/f1d/shared/panel_ols.py`: Panel OLS regression with fixed effects
- `src/f1d/shared/path_utils.py`: Path resolution and validation

**Testing:**
- `tests/conftest.py`: Pytest configuration and fixtures
- `tests/unit/`: Unit tests for shared utilities
- `tests/integration/`: Integration tests for pipeline steps
- `tests/regression/`: Regression tests for output stability
- `tests/performance/`: Performance tests

## Naming Conventions

**Files:**
- Stage scripts: `{step_number}.{sub_step}_{description}.py` (e.g., `1.1_CleanMetadata.py`)
- V1 scripts: `3.{substep}_{description}.py` (e.g., `3.1_FirmControls.py`)
- V2 scripts: `3.{hyp}_{description}.py` (e.g., `3.1_H1Variables.py`)
- Shared utilities: `{purpose}.py` (e.g., `path_utils.py`, `data_loading.py`)
- Tests: `test_{module}.py` (e.g., `test_path_utils.py`)

**Directories:**
- Input data: `{number}_{description}/` (e.g., `1_Inputs`, `3_Logs`, `4_Outputs`)
- Output scripts: `{description}/` (e.g., `sample`, `text`, `financial`, `econometric`)
- Version variants: `v1/` and `v2/` (both active, neither deprecated)
- Shared utilities: `shared/` and subdirectories by function (e.g., `config/`, `logging/`)

## Where to Add New Code

**New Stage/Step:**
- Primary code: `src/f1d/{stage}/{step_number}_{description}.py`
- Tests: `tests/unit/test_{description}.py` and `tests/integration/test_{step}.py`

**New Shared Utility:**
- Implementation: `src/f1d/shared/{utility_name}.py`
- Tests: `tests/unit/test_{utility_name}.py`
- Re-export: Add to `src/f1d/shared/__init__.py` if public API

**New Hypothesis (V2 Financial):**
- Variables: `src/f1d/financial/v2/3.{hyp}_{description}Variables.py`
- Regression: `src/f1d/econometric/v2/4.{hyp}_{description}Regression.py`
- Tests: `tests/unit/test_{hyp}_variables.py` and `tests/integration/test_{hyp}_regression.py`

**New Config Section:**
- Schema: `src/f1d/shared/config/base.py` (add Pydantic model)
- Values: `config/project.yaml` (add YAML section)
- Loader: `src/f1d/shared/config/loader.py` (if needed)

**New Output Schema:**
- Schema: `src/f1d/shared/output_schemas.py` (add Pandera model)
- Validation: Call validation function in script before writing output

**Utilities:**
- Shared helpers: `src/f1d/shared/{category}_utils.py`
- Test helpers: `tests/utils/`
- Fixtures: `tests/factories/`

## Special Directories

**1_Inputs:**
- Purpose: Raw input data (immutable, read-only during processing)
- Generated: No (external data sources)
- Committed: Yes (reference data is versioned)

**3_Logs:**
- Purpose: Script execution logs (timestamped directories)
- Generated: Yes (by each script execution)
- Committed: Yes (for reproducibility and debugging)

**4_Outputs:**
- Purpose: Pipeline outputs (timestamped directories with `latest/` symlinks)
- Generated: Yes (by each script execution)
- Committed: Yes (for reproducibility)

**_archive:**
- Purpose: Deprecated/archived code (legacy implementations)
- Generated: No (manually maintained)
- Committed: Yes (for historical reference)

**.planning:**
- Purpose: GSD planning and documentation
- Generated: Yes (by GSD workflow commands)
- Committed: Yes (for project tracking)

**.benchmarks:**
- Purpose: Performance benchmark results
- Generated: Yes (by performance tests)
- Committed: Yes (for performance tracking)

**tests/fixtures:**
- Purpose: Test fixture data (sample inputs for testing)
- Generated: No (hand-crafted test data)
- Committed: Yes (for test reproducibility)

---

*Structure analysis: 2026-02-15*
