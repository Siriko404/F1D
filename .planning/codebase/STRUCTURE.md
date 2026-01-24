# Codebase Structure

**Analysis Date:** 2026-01-24

## Directory Layout

```
F1D/
├── README.md              # Main project documentation
├── pyproject.toml         # Python project configuration (pytest, coverage)
├── requirements.txt      # Python dependencies
├── prd.md                 # Product requirements document
├── 1_Inputs/              # Raw input data (read-only)
├── 2_Scripts/             # All processing scripts and shared utilities
├── 3_Logs/               # Execution logs (mirrors script structure)
├── 4_Outputs/             # Timestamped output directories
├── config/                # Configuration files
├── tests/                 # Test suite (unit, integration, regression)
├── Docs/                  # Additional documentation
├── .github/               # GitHub Actions CI/CD workflows
└── .planning/             # Planning documents and phases
```

## Directory Purposes

**1_Inputs/:**
- Purpose: Raw data files from external sources (earnings calls, financial databases, reference files)
- Contains: Parquet files, CSV files, Excel files, zip archives
- Key files:
  - `Unified-info.parquet` - Call metadata (55 MB)
  - `speaker_data_*.parquet` - Call transcripts (2002-2018, ~2.5 GB total)
  - `Loughran-McDonald_MasterDictionary_1993-2024.csv` - Text classification dictionary
  - `CRSPCompustat_CCM/` - GVKEY-PERMNO linking table
  - `CRSP_DSF/` - Daily stock returns
  - `comp_na_daily_all/` - Compustat North America daily data
  - `Execucomp/` - Executive compensation data
  - `SDC/` - M&A deal data
  - `CCCL instrument/` - Instrumental variable data

**2_Scripts/:**
- Purpose: All executable scripts and shared utility modules
- Contains: Stage-organized subdirectories, shared utilities, orchestrators
- Key files:
  - `1_Sample/` - Sample construction scripts (1.1-1.4 + orchestrator 1.0)
  - `2_Text/` - Text processing scripts (2.1-2.3)
  - `3_Financial/` - Financial feature scripts (3.0-3.4)
  - `4_Econometric/` - Econometric analysis scripts (4.1-4.4)
  - `shared/` - Reusable utilities (dual_writer, path_utils, regression_helpers, etc.)
  - `2.3_Report.py` - Report generation script

**3_Logs/:**
- Purpose: Execution logs with timestamped files mirroring script structure
- Contains: Plain text logs and optional JSONL logs
- Key files:
  - `1.0_BuildSampleManifest/*.log` - Orchestrator logs
  - `1.1_CleanMetadata/*.log` - Metadata cleaning logs
  - `2.1_TokenizeAndCount/*.log` - Tokenization logs
  - Mirrors 2_Scripts structure for log file organization

**4_Outputs/:**
- Purpose: Timestamped output directories with `latest/` symlinks
- Contains: Parquet files, reports, diagnostics, audit files
- Key files:
  - `1.4_AssembleManifest/latest/master_sample_manifest.parquet` - Final sample manifest
  - `2.2_ConstructVariables/latest/linguistic_variables_*.parquet` - Text features per year
  - `3_Financial_Features/latest/` - Firm controls and market variables
  - `4.1_CeoClarity/latest/ceo_clarity_scores.parquet` - CEO clarity estimates
  - Each step has timestamped subdirectories: `YYYY-MM-DD_HHMMSS/`

**config/:**
- Purpose: Central configuration files for runtime parameters
- Contains: YAML configuration files
- Key files:
  - `project.yaml` - Main configuration (paths, seeds, thresholds, per-step params)

**tests/:**
- Purpose: Test suite organized by type (unit, integration, regression)
- Contains: Test files, fixtures, conftest.py
- Key files:
  - `conftest.py` - Pytest configuration and shared fixtures
  - `fixtures/` - Test data and sample configs
  - `unit/` - Unit tests for shared utilities
  - `integration/` - End-to-end pipeline tests
  - `regression/` - Output stability tests with baseline checksums

**Docs/:**
- Purpose: Additional project documentation
- Contains: Design docs, guides, references

**.github/:**
- Purpose: GitHub Actions CI/CD workflows
- Contains: Workflow YAML files for automated testing

**.planning/:**
- Purpose: Development planning and phase documentation
- Contains: Phase plans, research docs, codebase analysis (this file)

## Key File Locations

**Entry Points:**
- `2_Scripts/1.0_BuildSampleManifest.py`: Orchestrates sample construction stage
- `2_Scripts/3.0_BuildFinancialFeatures.py`: Orchestrates financial features stage
- `2_Scripts/2.1_TokenizeAndCount.py`: Tokenizes call transcripts
- `2_Scripts/2.2_ConstructVariables.py`: Builds linguistic variables
- `2_Scripts/4.1_EstimateCeoClarity.py`: Estimates CEO clarity scores
- `2_Scripts/2.3_Report.py`: Generates final reports

**Configuration:**
- `config/project.yaml`: Central runtime configuration
- `pyproject.toml`: Python project configuration (pytest, coverage settings)
- `requirements.txt`: Python dependencies

**Core Logic:**
- `2_Scripts/1_Sample/`: Sample construction (metadata cleaning, entity linking, tenure mapping)
- `2_Scripts/2_Text/`: Text processing (tokenization, variable construction, verification)
- `2_Scripts/3_Financial/`: Financial features (firm controls, market variables, event flags)
- `2_Scripts/4_Econometric/`: Econometric analysis (CEO clarity, liquidity, takeover models)
- `2_Scripts/shared/`: Reusable utilities used across all stages

**Testing:**
- `tests/conftest.py`: Pytest configuration and shared fixtures
- `tests/unit/test_*.py`: Unit tests for shared modules
- `tests/integration/test_*.py`: Integration tests for pipeline stages
- `tests/regression/`: Regression tests for output stability

## Naming Conventions

**Files:**
- Processing scripts: `<Stage>.<Step>_<PascalCaseName>.py` (e.g., `2.1_TokenizeAndCount.py`)
- Orchestrator scripts: `<Stage>.0_<PascalCaseName>.py` (e.g., `1.0_BuildSampleManifest.py`)
- Utility scripts: `<PascalCaseName>.py` in subdirectories (e.g., `3.4_Utils.py`)
- Test files: `test_<lowercase_name>.py` (e.g., `test_data_validation.py`)
- Configuration: `project.yaml`, `requirements.txt`

**Directories:**
- Stage directories: `<Number>_<PascalCaseName>/` (e.g., `1_Sample/`, `2_Text/`)
- Output directories: `<StepNumber>_<PascalCaseName>/` (e.g., `1.1_CleanMetadata/`)
- Log directories: Mirrors output directory structure
- Test directories: `unit/`, `integration/`, `regression/`, `fixtures/`

**Output Files:**
- Timestamped directories: `YYYY-MM-DD_HHMMSS/`
- Symlink: `latest/` points to most recent successful output
- Parquet files: `{measure}_{year}.parquet` (e.g., `linguistic_variables_2002.parquet`)
- Reports: `report_step_<number>.md`
- Diagnostics: `model_diagnostics.csv`, `regression_results.txt`

## Where to Add New Code

**New Processing Step:**
- Primary code: `2_Scripts/<Stage>_<Name>/X.<StepNumber>_<PascalCaseName>.py`
- Tests: `tests/unit/test_<step_name>.py`, `tests/integration/test_pipeline_step<X>.py`
- Outputs: `4_Outputs/X.<StepNumber>_<PascalCaseName>/`
- Config: Add section to `config/project.yaml` under `step_<number>:`

**New Stage (e.g., Step 5):**
- Implementation: `2_Scripts/5_<StageName>/`
- Orchestrator: `2_Scripts/5.0_<PascalCaseName>.py`
- Utilities: Add to `2_Scripts/shared/` if reusable across stages
- Tests: `tests/integration/test_pipeline_step5.py`

**New Shared Utility:**
- Implementation: `2_Scripts/shared/<lowercase_name>_utils.py`
- Tests: `tests/unit/test_<lowercase_name>.py`
- Exports: Add to `__all__` list in utility file if needed

**New Test Type:**
- Unit tests: `tests/unit/test_<feature>.py`
- Integration tests: `tests/integration/test_<feature>_integration.py`
- Regression tests: Add to `tests/regression/test_output_stability.py` or create new file
- Fixtures: Add to `tests/fixtures/` directory

## Special Directories

**2_Scripts/shared/:**
- Purpose: Shared utility modules for cross-stage reuse
- Generated: No (manually maintained)
- Committed: Yes
- Contains:
  - `dual_writer.py` - Re-export of DualWriter from observability_utils
  - `path_utils.py` - Path validation and directory helpers
  - `data_loading.py` - Data loading utilities
  - `data_validation.py` - Data quality validation
  - `observability_utils.py` - Logging, stats, anomaly detection
  - `regression_helpers.py` - Regression specification helpers
  - `regression_utils.py` - Core regression functions
  - `regression_validation.py` - Regression data validation
  - `financial_utils.py` - Financial calculations
  - `string_matching.py` - Fuzzy name matching
  - `chunked_reader.py` - Memory-efficient file reading
  - `symlink_utils.py` - Cross-platform symlink/junction management
  - `subprocess_validation.py` - Security validation for subprocess calls
  - `env_validation.py` - Environment validation
  - `metadata_utils.py` - Metadata processing
  - `industry_utils.py` - Industry classification helpers
  - `reporting_utils.py` - Report generation helpers

**2_Scripts/ARCHIVE/ and 2_Scripts/ARCHIVE_OLD/:**
- Purpose: Deprecated or broken scripts retained for reference
- Generated: No
- Committed: Yes
- Note: Do not modify; create new scripts instead

**4_Outputs/*/latest/:**
- Purpose: Symlink to most recent successful output directory
- Generated: Yes (created by `shared/symlink_utils.py`)
- Committed: No (gitignored)
- Note: On Windows, may be junction if symlink creation fails

**3_Logs/:**
- Purpose: Execution logs for debugging and audit trails
- Generated: Yes (created by each script)
- Committed: No (gitignored)
- Structure: Mirrors `4_Outputs/` directory structure

**tests/fixtures/:**
- Purpose: Test data files and sample configurations
- Generated: No (manually maintained)
- Committed: Yes
- Contains: Sample Parquet files, sample YAML configs, test data

---

*Structure analysis: 2026-01-24*
