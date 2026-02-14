# Codebase Structure

**Analysis Date:** 2026-02-14

## Directory Layout

```
F1D/
├── .github/workflows/      # CI/CD pipelines (ci.yml, test.yml)
├── .planning/              # Phase plans and codebase analysis
├── 1_Inputs/               # Raw input data (CRSP, Compustat, etc.)
├── 2_Scripts/              # Legacy pipeline scripts (being migrated)
├── 3_Logs/                 # Execution logs (timestamped)
├── 4_Outputs/              # Pipeline outputs (timestamped per step)
├── config/                 # Configuration files (project.yaml)
├── data/                   # New data directory structure
│   ├── raw/                # Immutable raw data
│   ├── interim/            # Intermediate processing data
│   ├── processed/          # Final cleaned data
│   └── external/           # Third-party reference data
├── docs/                   # Documentation standards
├── logs/                   # Additional log storage
├── results/                # Analysis outputs (figures, tables)
├── src/f1d/                # Main package (src-layout)
│   ├── shared/             # Cross-cutting utilities
│   ├── sample/             # Step 1: Sample construction
│   ├── text/               # Step 2: Text processing
│   ├── financial/          # Step 3: Financial features
│   └── econometric/        # Step 4: Econometric analysis
├── tests/                  # Test suite
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   ├── regression/         # Regression tests
│   ├── performance/        # Performance tests
│   └── factories/          # Test data factories
├── pyproject.toml          # Package configuration
└── requirements.txt        # Dependencies
```

## Directory Purposes

**`src/f1d/` - Main Package:**
- Purpose: Installable Python package with src-layout
- Contains: All pipeline modules organized by stage
- Key files: `shared/__init__.py`, `sample/1.0_BuildSampleManifest.py`, `financial/v2/3.1_H1Variables.py`

**`src/f1d/shared/` - Shared Utilities:**
- Purpose: Cross-cutting concerns used across all stages
- Contains: Path utilities, logging, validation, regression helpers, financial utils
- Key files: `path_utils.py`, `panel_ols.py`, `financial_utils.py`, `data_validation.py`
- Subpackages: `config/`, `logging/`, `observability/`

**`1_Inputs/` - Raw Data:**
- Purpose: Immutable source data (never modified)
- Contains: CRSP, Compustat, Execucomp, earnings call transcripts, LM dictionary
- Key files: `Unified-info.parquet`, `Loughran-McDonald_MasterDictionary_1993-2024.csv`

**`2_Scripts/` - Legacy Scripts:**
- Purpose: Historical pipeline scripts (being deprecated)
- Contains: Duplicate implementations of src/f1d modules
- Subdirectories: `1_Sample/`, `2_Text/`, `3_Financial/`, `3_Financial_V2/`, `4_Econometric/`, `4_Econometric_V2/`, `shared/`

**`4_Outputs/` - Pipeline Outputs:**
- Purpose: Timestamped outputs from each processing step
- Contains: Parquet files, stats.json, reports per step execution
- Key pattern: `{step_name}/{timestamp}/output.parquet`
- Subdirectories: `1.4_AssembleManifest/`, `3_Financial_V2/`, `4_Econometric_V2/`

**`tests/` - Test Suite:**
- Purpose: Unit, integration, regression, and performance tests
- Contains: pytest tests organized by test type
- Key files: `conftest.py`, `unit/test_path_utils.py`, `integration/test_full_pipeline.py`

**`docs/` - Documentation:**
- Purpose: Architecture and coding standards
- Contains: ARCHITECTURE_STANDARD.md, CODE_QUALITY_STANDARD.md, CONFIG_TESTING_STANDARD.md
- Key files: `ARCHITECTURE_STANDARD.md`, `VARIABLE_CATALOG_V2_V3.md`

## Key File Locations

**Entry Points:**
- `src/f1d/sample/1.0_BuildSampleManifest.py`: Main orchestrator for sample construction
- `src/f1d/financial/v2/3.1_H1Variables.py`: Financial feature construction
- `src/f1d/econometric/v2/4.1_H1CashHoldingsRegression.py`: Regression analysis

**Configuration:**
- `config/project.yaml`: Main configuration file
- `pyproject.toml`: Package metadata, tool config (pytest, ruff, mypy, coverage)
- `requirements.txt`: Pinned dependencies

**Core Logic:**
- `src/f1d/shared/path_utils.py`: Path resolution and validation
- `src/f1d/shared/panel_ols.py`: Panel OLS regression with fixed effects
- `src/f1d/shared/financial_utils.py`: Financial metric calculations
- `src/f1d/shared/data_validation.py`: Schema-based input validation
- `src/f1d/shared/config/loader.py`: Configuration loading with caching

**Testing:**
- `tests/conftest.py`: Shared fixtures and pytest configuration
- `tests/unit/`: Unit tests for shared utilities
- `tests/integration/`: Pipeline integration tests
- `tests/regression/`: Output stability tests
- `tests/fixtures/`: Test data files (sample configs, checksums)

## Naming Conventions

**Files:**
- Pipeline steps: `{stage}.{step}_{description}.py` (e.g., `1.2_LinkEntities.py`, `3.1_H1Variables.py`)
- Test files: `test_{module}.py` (e.g., `test_path_utils.py`, `test_financial_utils.py`)
- Configuration: `project.yaml`, `pyproject.toml`

**Directories:**
- Stage directories: `{step_number}_{name}/` (e.g., `1_Sample/`, `3_Financial_V2/`)
- Output directories: `{step_name}/{timestamp}/` (e.g., `1.4_AssembleManifest/2026-01-30_102931/`)
- Version directories: `v{number}/` (e.g., `v1/`, `v2/`)

**Modules:**
- Shared utilities: `{purpose}_utils.py` (e.g., `financial_utils.py`, `path_utils.py`)
- Step modules: `{step}_{description}.py` (e.g., `3.1_H1Variables.py`)
- Config modules: `{domain}.py` (e.g., `paths.py`, `loader.py`, `base.py`)

## Where to Add New Code

**New Pipeline Step:**
- Primary code: `src/f1d/{stage}/{step}_{description}.py`
- Legacy duplicate: `2_Scripts/{stage_dir}/{step}_{description}.py`
- Output directory: `4_Outputs/{step_name}/`

**New Shared Utility:**
- Implementation: `src/f1d/shared/{purpose}_utils.py`
- Export: Add to `src/f1d/shared/__init__.py`
- Tests: `tests/unit/test_{purpose}_utils.py`

**New Hypothesis Variables:**
- Implementation: `src/f1d/financial/v2/3.{n}_H{n}Variables.py`
- Regression: `src/f1d/econometric/v2/4.{n}_H{n}{description}Regression.py`

**New Configuration Setting:**
- Schema: `src/f1d/shared/config/{domain}.py`
- YAML: `config/project.yaml`
- Test: `tests/unit/test_config.py`

**New Test:**
- Unit test: `tests/unit/test_{module}.py`
- Integration test: `tests/integration/test_{feature}.py`
- Test fixture: `tests/fixtures/` or `tests/factories/`

## Special Directories

**`.___archive/` - Archived Code:**
- Purpose: Deprecated code preserved for reference
- Contains: Legacy implementations, debug scripts, backup files
- Committed: Yes
- Generated: No (manually archived)

**`data/` - New Data Structure:**
- Purpose: Cookiecutter-style data organization
- Contains: `raw/`, `interim/`, `processed/`, `external/`
- Note: Transitioning from `1_Inputs/`/`4_Outputs/` to this structure

**`.planning/` - Phase Plans:**
- Purpose: GSD workflow phase documentation
- Contains: Phase plans, verification docs, codebase analysis
- Generated: By GSD workflow commands
- Committed: Yes

**`htmlcov/` - Coverage Reports:**
- Purpose: HTML coverage reports from pytest-cov
- Generated: Yes (by `pytest --cov`)
- Committed: No (in .gitignore)

---

*Structure analysis: 2026-02-14*
