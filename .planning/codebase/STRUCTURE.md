# Codebase Structure

**Analysis Date:** 2026-02-12

## Directory Layout

```
F1D/
├── 1_Inputs/                    # Raw data sources (not version controlled)
│   ├── CRSP_DSF/                # Daily stock returns
│   ├── CRSPCompustat_CCM/       # GVKEY-PERMNO linking table
│   ├── comp_na_daily_all/       # Compustat North America
│   ├── Earnings_Calls_Transcripts/
│   ├── Execucomp/               # Executive compensation
│   ├── FF1248/                  # Fama-French industry codes
│   ├── FirmLevelRisk/
│   ├── LM_dictionary/           # Loughran-McDonald sentiment dictionary
│   ├── Manager_roles/
│   ├── SDC/                     # M&A deal data
│   ├── SEC_Edgar_Letters/
│   ├── tr_ibes/                 # IBES analyst forecasts
│   └── CCCL_instrument/         # Instrumental variable data
├── 2_Scripts/                   # All Python processing code
│   ├── shared/                  # Reusable utilities (imported by all scripts)
│   ├── 1_Sample/                # Step 1: Sample construction scripts
│   ├── 2_Text/                  # Step 2: Text processing scripts
│   ├── 3_Financial/             # Step 3: Financial feature scripts
│   ├── 3_Financial_V2/          # Alternative implementations
│   ├── 3_Financial_V3/
│   ├── 4_Econometric/           # Step 4: Econometric analysis scripts
│   ├── 4_Econometric_V2/
│   ├── 4_Econometric_V3/
│   ├── 5_Financial_V3/
│   └── stubs/                   # Type stubs for untyped packages
├── 3_Logs/                      # Execution logs (timestamped)
├── 4_Outputs/                   # Pipeline outputs (timestamped directories)
├── config/                      # Configuration files
├── docs/                        # Documentation
├── tests/                       # Test suite
│   ├── unit/
│   ├── integration/
│   ├── regression/
│   ├── performance/
│   └── fixtures/
├── .___archive/                 # Archived/deprecated code
├── .planning/                   # Planning documents and phase tracking
├── pyproject.toml               # Project configuration (pytest, ruff, mypy, coverage)
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

## Directory Purposes

**1_Inputs:**
- Purpose: Raw data sources from external providers (CRSP, Compustat, IBES, etc.)
- Contains: Parquet files, CSV files, Excel files organized by data source
- Key files: `Unified-info.parquet`, `speaker_data_*.parquet`, `CRSPCompustat_CCM.parquet`
- Note: Large files, not committed to git

**2_Scripts:**
- Purpose: All executable Python code for data processing
- Contains: Pipeline step scripts and shared utilities
- Key files: Organized by processing stage (1_Sample, 2_Text, etc.)

**2_Scripts/shared:**
- Purpose: Reusable utility modules imported by all pipeline scripts
- Contains: 20+ utility modules for validation, regression, logging, etc.
- Key files: `panel_ols.py`, `financial_utils.py`, `regression_helpers.py`, `path_utils.py`, `observability_utils.py`

**2_Scripts/shared/observability:**
- Purpose: Logging, statistics, memory tracking sub-package
- Contains: Modular observability components
- Key files: `stats.py` (197KB - extensive step-specific stats functions), `logging.py`, `memory.py`

**3_Logs:**
- Purpose: Execution logs organized by script name
- Contains: Timestamped `.log` files
- Key files: `{script_name}/{timestamp}.log`

**4_Outputs:**
- Purpose: Pipeline outputs organized by step
- Contains: Timestamped subdirectories with parquet files, stats.json, reports
- Key files: `{step_name}/{timestamp}/output.parquet`

**config:**
- Purpose: Centralized configuration
- Contains: YAML configuration files
- Key files: `project.yaml` (main configuration)

**tests:**
- Purpose: Test suite with multiple test categories
- Contains: Unit, integration, regression, performance tests
- Key files: `conftest.py` (shared fixtures), `test_*.py` files

**docs:**
- Purpose: Documentation files
- Contains: Variable catalogs, docstring compliance guides
- Key files: `VARIABLE_CATALOG_V1.md`, `VARIABLE_CATALOG_V2_V3.md`

## Key File Locations

**Entry Points:**
- `2_Scripts/1_Sample/1.0_BuildSampleManifest.py`: Build sample manifest
- `2_Scripts/2_Text/2.1_TokenizeAndCount.py`: Tokenize transcripts
- `2_Scripts/3_Financial/3.0_BuildFinancialFeatures.py`: Compute financial features
- `2_Scripts/4_Econometric/4.1_EstimateCeoClarity.py`: Estimate CEO clarity

**Configuration:**
- `config/project.yaml`: Main pipeline configuration
- `pyproject.toml`: Tool configuration (pytest, ruff, mypy, coverage)

**Core Logic:**
- `2_Scripts/shared/panel_ols.py`: Panel OLS with fixed effects (544 lines)
- `2_Scripts/shared/financial_utils.py`: Financial calculations (350+ lines)
- `2_Scripts/shared/regression_helpers.py`: Data loading and sample construction
- `2_Scripts/shared/data_validation.py`: Schema validation
- `2_Scripts/shared/path_utils.py`: Path handling utilities

**Observability:**
- `2_Scripts/shared/observability/stats.py`: Step-specific statistics (197KB)
- `2_Scripts/shared/observability/logging.py`: DualWriter class
- `2_Scripts/shared/observability_utils.py`: Backward-compatibility re-exports

**Testing:**
- `tests/conftest.py`: Shared pytest fixtures
- `tests/unit/test_panel_ols.py`: Panel OLS unit tests
- `tests/integration/test_pipeline_step1.py`: Step 1 integration tests
- `tests/regression/test_output_stability.py`: Output stability tests

**Type Stubs:**
- `2_Scripts/stubs/linearmodels.panel.pyi`: PanelOLS type hints
- `2_Scripts/stubs/linearmodels.iv.pyi`: IV regression type hints

## Naming Conventions

**Files:**
- Scripts: `{step}.{substep}_{DescriptiveName}.py` (e.g., `1.2_LinkEntities.py`, `4.1.1_EstimateCeoClarity_CeoSpecific.py`)
- Utilities: `{category}_utils.py` (e.g., `financial_utils.py`, `industry_utils.py`)
- Tests: `test_{module_or_feature}.py` (e.g., `test_panel_ols.py`, `test_fuzzy_matching.py`)

**Directories:**
- Processing stages: `{step_number}_{stage_name}` (e.g., `1_Sample`, `2_Text`, `3_Financial`, `4_Econometric`)
- Output directories: `{step}.{substep}_{descriptive_name}` (e.g., `1.1_CleanMetadata`, `2.1_TokenizeAndCount`)
- Version variants: `{name}_V{version}` (e.g., `3_Financial_V2`, `4_Econometric_V3`)

**Python Modules:**
- Package: `__init__.py` with `__all__` exports
- Classes: PascalCase (e.g., `DualWriter`, `OutputResolutionError`)
- Functions: snake_case (e.g., `get_latest_output_dir`, `run_panel_ols`)
- Constants: UPPER_SNAKE_CASE (e.g., `INPUT_SCHEMAS`, `LINEARMODELS_AVAILABLE`)

## Where to Add New Code

**New Pipeline Step:**
- Script: `2_Scripts/{stage_number}_{stage_name}/{step}.{substep}_{descriptive_name}.py`
- Output: `4_Outputs/{step}.{substep}_{descriptive_name}/{timestamp}/`
- Log: `3_Logs/{step}.{substep}_{descriptive_name}/{timestamp}.log`
- Config: Add section to `config/project.yaml` under `step_{step_number}`

**New Shared Utility:**
- Module: `2_Scripts/shared/{category}_utils.py`
- Update: `2_Scripts/shared/__init__.py` to add to `__all__`
- Tests: `tests/unit/test_{category}_utils.py`

**New Regression Analysis:**
- Script: `2_Scripts/4_Econometric/{step}.{substep}_{analysis_name}.py`
- Uses: `shared.panel_ols`, `shared.iv_regression`, `shared.regression_helpers`
- Output: `4_Outputs/{step}.{substep}_{analysis_name}/`

**New Test:**
- Unit: `tests/unit/test_{feature}.py`
- Integration: `tests/integration/test_pipeline_{step}.py`
- Regression: `tests/regression/test_{stability_aspect}.py`

**New Configuration:**
- Add step section to `config/project.yaml`
- Follow existing pattern: `enabled`, `output_subdir`, `outputs`, step-specific params

## Special Directories

**.___archive:**
- Purpose: Archived/deprecated code kept for reference
- Contains: Legacy implementations, debug scripts, old utilities
- Generated: No (manual migration)
- Committed: Yes (but excluded from linting/type checking)

**.planning:**
- Purpose: Project planning documents and phase tracking
- Contains: `phases/` (phase-specific plans), `codebase/` (analysis docs), `quick/` (quick tasks)
- Generated: Partially (STATE.md managed by orchestrator)
- Committed: Yes

**tests/fixtures:**
- Purpose: Test data and mock configurations
- Contains: Sample parquet files, sample YAML configs
- Generated: No
- Committed: Yes

**2_Scripts/stubs:**
- Purpose: Type stubs for untyped third-party packages
- Contains: `.pyi` files for linearmodels
- Generated: No (manually written)
- Committed: Yes
- Used by: mypy via `mypy_path` in `pyproject.toml`

**htmlcov/ (generated):**
- Purpose: HTML coverage report
- Generated: Yes (by `pytest --cov`)
- Committed: No (in `.gitignore`)

**Output Directory Pattern:**
```
4_Outputs/{step_name}/
├── {timestamp_1}/
│   ├── output_file.parquet
│   ├── stats.json
│   └── report.md
├── {timestamp_2}/
│   └── ...
└── latest/              # Symlink to most recent
```

---

*Structure analysis: 2026-02-12*
