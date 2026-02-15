# Codebase Structure

**Analysis Date:** 2026-02-14

## Directory Layout

```
F1D/
├── 1_Inputs/          # Raw data directory (read-only inputs)
│   ├── Earnings_Calls_Transcripts/
│   ├── LM_dictionary/
│   ├── CRSP_DSF/
│   ├── CRSPCompustat_CCM/
│   ├── comp_na_daily_all/
│   ├── tr_ibes/
│   ├── Execucomp/
│   ├── SDC/
│   ├── FF1248/
│   └── managerial_roles_extracted.txt
├── 3_Logs/            # Pipeline execution logs (timestamped)
│   ├── 1.0_BuildSampleManifest/
│   ├── 2.2_ConstructVariables/
│   ├── 3_Financial_V2/
│   └── 4_Econometric_V2/
├── 4_Outputs/          # Intermediate and final outputs (timestamped)
│   ├── 1.0_BuildSampleManifest/
│   ├── 1.4_AssembleManifest/
│   ├── 2_Textual_Analysis/
│   ├── 3_Financial_Features/
│   └── 4.1_CeoClarity/
├── _archive/            # Legacy and archived code (not in active use)
├── config/             # Configuration files
├── docs/               # Documentation standards and specifications
├── src/                # Source code (src-layout package structure)
│   ├── f1d/           # Main package namespace
│   │   ├── sample/     # Step 1: Sample construction
│   │   ├── text/       # Step 2: Text processing
│   │   ├── financial/   # Step 3: Financial features (v1 and v2 versions)
│   │   ├── econometric/ # Step 4: Econometric analysis (v1 and v2 versions)
│   │   ├── shared/     # Shared utilities across all steps
│   │   ├── 3_Logs/     # Log directories inside src (per-step)
│   │   └── 4_Outputs/   # Output directories inside src (per-step)
│   └── f1d.egg-info/ # Package metadata (generated)
├── tests/              # Test suite
│   ├── unit/
│   ├── integration/
│   ├── regression/
│   ├── performance/
│   ├── verification/
│   └── utils/
├── .github/            # GitHub Actions workflows
├── .planning/          # GSD workflow planning and tracking
│   ├── phases/         # Phase planning documents
│   └── codebase/      # Codebase documentation (this directory)
├── .claude/            # Claude-specific configuration
└── pyproject.toml      # Package configuration
```

## Directory Purposes

**1_Inputs/**:
- Purpose: Read-only storage for all raw data sources
- Contains: Earnings calls (transcripts), financial databases (CRSP, Compustat, IBES), executive data (Execucomp), M&A data (SDC), reference files (LM dictionary, SIC codes, CCCL instrument)
- Key files: `Unified-info.parquet`, `speaker_data_YYYY.parquet`, `Loughran-McDonald_MasterDictionary_1993-2024.csv`
- Note: Large files (multi-GB), committed to git-lfs or referenced externally

**3_Logs/**:
- Purpose: Execution logs for all pipeline steps
- Contains: Timestamped log files (YYYY-MM-DD_HHMMSS.log) per step
- Key files: `{timestamp}.log` in step-specific subdirectories
- Note: Logs persist for debugging and audit trails

**4_Outputs/**:
- Purpose: Intermediate and final processing results
- Contains: Timestamped directories with parquet files, markdown reports, JSON stats
- Key files: `master_sample_manifest.parquet`, `linguistic_variables_YYYY.parquet`, `firm_controls_YYYY.parquet`, `ceo_clarity_scores.parquet`
- Note: Timestamped directories enable reproducibility and prevent data loss

**_archive/**:
- Purpose: Historical code preservation (legacy implementations)
- Contains: `legacy_archive/`, `2_Scripts_v5.1_legacy/`, debug scripts
- Key directories: Backups, old implementations, investigation scripts
- Note: Not referenced by active pipeline, preserved for reference

**config/**:
- Purpose: Centralized configuration management
- Contains: `project.yaml` (pipeline-wide settings)
- Key files: `project.yaml` with paths, step configs, dataset definitions
- Note: Single source of truth for pipeline parameters

**docs/**:
- Purpose: Code quality standards and specifications
- Contains: ARCHITECTURE_STANDARD.md, CODE_QUALITY_STANDARD.md, CONFIG_TESTING_STANDARD.md, DOC_TOOLING_STANDARD.md
- Key files: TIER_MANIFEST.md (module organization), VARIABLE_CATALOG_V1.md, VARIABLE_CATALOG_V2_V3.md
- Note: Defines architecture standards, coding conventions, testing requirements

**src/f1d/sample/**:
- Purpose: Step 1 sample construction logic
- Contains: Orchestrator `1.0_BuildSampleManifest.py`, substeps `1.1_CleanMetadata.py`, `1.2_LinkEntities.py`, `1.3_BuildTenureMap.py`, `1.4_AssembleManifest.py`
- Key files: All Step 1 processing scripts
- Note: Uses shared utilities for data loading and validation

**src/f1d/text/**:
- Purpose: Step 2 text processing logic
- Contains: `tokenize_and_count.py`, `construct_variables.py`, `verify_step2.py`, `report_step2.py`
- Key files: Tokenization, linguistic variable construction, verification
- Note: Processes Q&A text against LM dictionary

**src/f1d/financial/**:
- Purpose: Step 3 financial feature computation
- Contains: `v1/` (legacy) and `v2/` (current) subdirectories
- Key files (v2): `3.1_H1Variables.py`, `3.2_H2Variables.py`, `3.3_H3Variables.py`, hypothesis-specific scripts (H5-H9)
- Note: Versioned to support different research phases

**src/f1d/econometric/**:
- Purpose: Step 4 econometric analysis
- Contains: `v1/` (legacy CEO clarity regressions) and `v2/` (hypothesis-specific regressions)
- Key files (v1): `4.1_EstimateCeoClarity.py`, `4.2_LiquidityRegressions.py`, `4.3_TakeoverHazards.py`
- Key files (v2): `4.1_H1CashHoldingsRegression.py` through `4.11_H9_Regression.py`
- Note: Fixed effects regressions using linearmodels.PanelOLS

**src/f1d/shared/**:
- Purpose: Reusable utilities shared across all processing steps
- Contains: `config/` (settings), `logging/` (structlog setup), `observability/` (monitoring), utility modules
- Key modules: `path_utils.py`, `data_loading.py`, `data_validation.py`, `panel_ols.py`, `iv_regression.py`, `regression_utils.py`, `financial_utils.py`, `string_matching.py`
- Note: Core abstraction layer for pipeline operations

**src/f1d/shared/config/**:
- Purpose: Type-safe configuration management with Pydantic
- Contains: `base.py` (BaseSettings), `paths.py` (PathsSettings), `datasets.py`, `step_configs.py`, `env.py`
- Key files: Schema definitions for config validation
- Note: Enables centralized, validated configuration

**src/f1d/shared/logging/**:
- Purpose: Structured logging configuration
- Contains: `config.py` (configure_logging, get_logger), `handlers.py`, `context.py`
- Key files: Structlog setup with JSON file output
- Note: Replaces raw print statements with structured logs

**src/f1d/shared/observability/**:
- Purpose: Performance monitoring and quality tracking
- Contains: `stats.py`, `throughput.py`, `memory.py`, `files.py`, `anomalies.py`
- Key functions: Memory tracking, throughput calculation, anomaly detection
- Note: Generates `stats.json` in output directories

**tests/**:
- Purpose: Automated test suite
- Contains: `unit/`, `integration/`, `regression/`, `performance/`, `verification/`, `utils/`, `factories/`
- Key files: `conftest.py`, test modules per shared utility
- Note: pytest-based with fixtures and factories

**.planning/phases/**:
- Purpose: GSD workflow phase planning documents
- Contains: PLAN.md and SUMMARY.md for each numbered phase
- Key files: Phase-specific implementation plans and completion summaries
- Note: Used by /gsd:plan-phase and /gsd:execute-phase

## Key File Locations

**Entry Points:**
- `src/f1d/sample/1.0_BuildSampleManifest.py`: Sample construction orchestrator
- `src/f1d/text/tokenize_and_count.py`: Text tokenization
- `src/f1d/text/construct_variables.py`: Linguistic variable construction
- `src/f1d/financial/v1/3.0_BuildFinancialFeatures.py`: Financial features orchestrator
- `src/f1d/econometric/v1/4.1_EstimateCeoClarity.py`: CEO clarity estimation

**Configuration:**
- `config/project.yaml`: Pipeline-wide configuration (paths, steps, datasets)
- `src/f1d/shared/config/paths.py`: Path resolution with validation
- `src/f1d/shared/config/env.py`: Environment variable schema

**Core Logic:**
- `src/f1d/shared/panel_ols.py`: Panel regression with fixed effects
- `src/f1d/shared/iv_regression.py`: IV regression utilities
- `src/f1d/shared/financial_utils.py`: Financial ratio calculations
- `src/f1d/shared/string_matching.py`: Fuzzy entity matching

**Testing:**
- `tests/conftest.py`: Pytest fixtures and configuration
- `tests/unit/test_*.py`: Unit tests for shared utilities
- `tests/integration/test_*.py`: Integration tests across steps
- `tests/regression/test_*.py`: Regression tests for reproducibility

**Documentation:**
- `README.md`: Project overview and pipeline flow diagram
- `docs/ARCHITECTURE_STANDARD.md`: Architecture standards
- `docs/CODE_QUALITY_STANDARD.md`: Code quality requirements
- `docs/TIER_MANIFEST.md`: Module organization manifest

## Naming Conventions

**Files:**
- Orchestrators: `{step_number}.{substep}_{description}.py` (e.g., `1.0_BuildSampleManifest.py`, `3.0_BuildFinancialFeatures.py`)
- Substeps: `{step_number}.{substep}_{description}.py` (e.g., `1.1_CleanMetadata.py`, `3.1_H1Variables.py`)
- Shared utilities: `{domain}.py` (e.g., `panel_ols.py`, `data_validation.py`)
- Test files: `test_{module}.py` or `{test_type}/test_{feature}.py`
- Configuration: `{name}.yaml` or `{name}.py` (e.g., `project.yaml`, `paths.py`)

**Directories:**
- Processing steps: `{step_number}_{description}/` (e.g., `1_Sample/`, `2_Text/`)
- Versioned modules: `v{number}/` (e.g., `financial/v1/`, `econometric/v2/`)
- Timestamped outputs: `YYYY-MM-DD_HHMMSS/` (e.g., `2026-02-14_151716/`)
- Output files by year: `{prefix}_{YYYY}.parquet` (e.g., `linguistic_variables_2002.parquet`)

## Where to Add New Code

**New Feature (processing step):**
- Primary code: `src/f1d/{domain}/` (create new domain or add to existing)
- Tests: `tests/{unit,integration}/test_{feature}.py`
- Example: New text processing logic goes in `src/f1d/text/`

**New Component/Module (shared utility):**
- Implementation: `src/f1d/shared/{domain}.py`
- Tests: `tests/unit/test_{domain}.py`
- Example: New string matching function goes in `src/f1d/shared/string_matching.py`

**New Hypothesis (econometric regression):**
- Implementation: `src/f1d/econometric/v2/4.X_H{number}_{name}.py`
- Example: New hypothesis regression uses pattern `4.X_H{number}_{description}.py`

**Utilities:**
- Shared helpers: `src/f1d/shared/{domain}.py`
- Path utilities: `src/f1d/shared/path_utils.py`
- Validation: `src/f1d/shared/data_validation.py`

**Tests:**
- Unit tests: `tests/unit/test_{module}.py`
- Integration tests: `tests/integration/test_{feature}.py`
- Fixtures: `tests/factories/` (test data builders)

## Special Directories

**.planning/codebase/**:
- Purpose: Codebase documentation for GSD workflow
- Generated: Yes (by codebase mappers)
- Committed: Yes
- Contains: STACK.md, INTEGRATIONS.md, ARCHITECTURE.md, STRUCTURE.md, CONVENTIONS.md, TESTING.md, CONCERNS.md

**src/f1d/3_Logs/**:
- Purpose: Per-step log directories within src tree
- Generated: Yes (by pipeline execution)
- Committed: No (logs are runtime artifacts)
- Contains: Timestamped log files for each step

**src/f1d/4_Outputs/**:
- Purpose: Per-step output directories within src tree
- Generated: Yes (by pipeline execution)
- Committed: No (outputs are runtime artifacts)
- Contains: Timestamped parquet files, reports, stats

**tests/factories/**:
- Purpose: Test data builders and fixtures
- Generated: No (manual creation)
- Committed: Yes
- Contains: Reusable test data construction functions

**tests/fixtures/**:
- Purpose: Pytest conftest and shared fixtures
- Generated: No (manual creation)
- Committed: Yes
- Contains: `conftest.py` with pytest hooks

---

*Structure analysis: 2026-02-14*
