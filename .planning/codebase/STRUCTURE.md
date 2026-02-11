# Codebase Structure

**Analysis Date:** 2025-02-10

## Directory Layout

```
F1D/
├── 1_Inputs/                  # Raw data files (read-only)
├── 2_Scripts/                 # All processing scripts
├── 3_Logs/                    # Execution logs
├── 4_Outputs/                 # Timestamped output directories
├── .___archive/               # Legacy and debug scripts
├── .claude/                   # Claude Code configuration
├── .github/                   # GitHub Actions workflows
├── .git/                      # Git repository
├── .planning/                 # Project planning and phase documentation
├── .pytest_cache/             # Pytest cache
├── .ruff_cache/               # Ruff linter cache
├── config/                    # Configuration files
├── papers/                    # Reference papers
├── tests/                     # Unit, integration, regression tests
├── pyproject.toml             # Pytest configuration
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
└── SCALING.md                 # Scaling documentation
```

## Directory Purposes

**1_Inputs/:**
- Purpose: Raw, immutable input data
- Contains: Earnings call transcripts, financial databases (CRSP, Compustat), reference files
- Key files: `Unified-info.parquet`, `speaker_data_*.parquet`, `Loughran-McDonald_MasterDictionary_1993-2024.csv`, `CRSPCompustat_CCM/`, `comp_na_daily_all/`

**2_Scripts/:**
- Purpose: All executable processing code organized by pipeline step
- Contains: Step directories (1_Sample, 2_Text, 3_Financial, 4_Econometric) and shared utilities
- Key files: `shared/` (common utilities), numbered step scripts per hypothesis

**3_Logs/:**
- Purpose: Execution logs with dual-writer output (console + file)
- Contains: Timestamped log files per script execution
- Key pattern: `<StepName>/<timestamp>.log`

**4_Outputs/:**
- Purpose: Timestamped outputs from each pipeline step
- Contains: Subdirectories per step, each containing timestamped run directories
- Key pattern: `<StepName>/<YYYY-MM-DD_HHMMSS>/output.parquet`

**.planning/:**
- Purpose: Project planning, phase documentation, GSD command artifacts
- Contains: Phase plans (`phases/`), quick tasks (`quick/`), codebase analysis (`codebase/`)
- Key files: `PROJECT.md`, `REQUIREMENTS.md`, `MILESTONES.md`

**config/:**
- Purpose: Project configuration and parameters
- Contains: `project.yaml` (main config), backups
- Key settings: Paths, determinism parameters, step configurations

**tests/:**
- Purpose: Unit, integration, and regression tests
- Contains: `unit/`, `integration/`, `regression/`, `fixtures/`, `conftest.py`
- Key files: Shared fixtures in `conftest.py`, test data in `fixtures/`

**.___archive/:**
- Purpose: Legacy scripts and debug code (not actively used)
- Contains: `legacy/`, `debug/` subdirectories
- Generated: Yes (accumulated over time)
- Committed: Yes

## Key File Locations

**Entry Points:**
- `2_Scripts/1_Sample/1.1_CleanMetadata.py`: First step in pipeline (cleans call metadata)
- `2_Scripts/2.0_ValidateV2Structure.py`: Validates V2 pipeline structure
- `README.md`: Project overview and execution guide

**Configuration:**
- `config/project.yaml`: Main configuration (paths, determinism, step parameters)
- `pyproject.toml`: Pytest configuration (test paths, markers, coverage)
- `requirements.txt`: Python package dependencies

**Core Logic:**
- `2_Scripts/shared/`: Shared utilities (path_utils, observability_utils, regression_helpers)
- `2_Scripts/1_Sample/`: Sample construction (entity linking, tenure mapping)
- `2_Scripts/3_Financial_V2/`: Hypothesis variable construction (H1-H8)
- `2_Scripts/4_Econometric_V2/`: Panel regressions (H1-H9)
- `2_Scripts/5_Financial_V3/`: H9 advanced variable construction

**Testing:**
- `tests/conftest.py`: Pytest fixtures (sample_dataframe, mock_project_config)
- `tests/unit/`: Unit tests for shared utilities
- `tests/integration/`: End-to-end pipeline tests
- `tests/fixtures/`: Test data and sample configs

## Naming Conventions

**Files:**
- Pipeline scripts: `{step}.{substep}_{PascalCaseDescription}.py`
  - Examples: `1.1_CleanMetadata.py`, `3.1_H1Variables.py`, `4.1_H1CashHoldingsRegression.py`
- Shared utilities: `snake_case.py`
  - Examples: `path_utils.py`, `observability_utils.py`, `regression_helpers.py`
- Test files: `test_<module>_test.py` or `test_<module>.py`
  - Examples: `test_data_validation.py`, `test_env_validation.py`
- Legacy/deprecated: `*legacy.py`, `*_backup.py`

**Directories:**
- Step directories: `{number}_{Name}/`
  - Examples: `1_Sample/`, `2_Text/`, `3_Financial_V2/`, `4_Econometric_V2/`
- Output directories: `{StepName}/{timestamp}/`
  - Example: `1.4_AssembleManifest/2026-01-30_102328/`
- Log directories: Same as output directories, mirrored under `3_Logs/`
- Phase planning: `{two_digit}-{kebab-case-description}/`
  - Example: `28-v2-structure-setup/`, `33-h1-cash-holdings-regression/`

**Versioning:**
- V2, V3 suffixes indicate major refactors with incompatible interfaces
  - `3_Financial/` (legacy), `3_Financial_V2/` (hypothesis-driven), `5_Financial_V3/` (H9)
- `4_Econometric/` (legacy), `4_Econometric_V2/` (hypothesis regressions)

**Output Files:**
- Parquet datasets: `{Description}_{Hypothesis}.parquet`
  - Examples: `H1_CashHoldings.parquet`, `H2_InvestmentEfficiency.parquet`
- Reports: `report_step_{step}_{substep}.md` or `H{#}_Hypothesis_Documentation.md`
- Statistics: `stats.json` (JSON with distributions, diagnostics)
- Logs: `{timestamp}_{step}.log` or `{timestamp}.log`

## Where to Add New Code

**New Feature (New Hypothesis H10):**
- Primary code: `2_Scripts/3_Financial_V2/3.X_H10Variables.py` (variable construction)
- Tests: `tests/unit/test_h10_variables.py`
- Regression: `2_Scripts/4_Econometric_V2/4.10_H10Regression.py`
- Documentation: Add to `4_Outputs/4_Econometric_V2/H10_Hypothesis_Documentation.md`

**New Component/Module (Shared Utility):**
- Implementation: `2_Scripts/shared/<module_name>.py`
- Tests: `tests/unit/test_<module_name>.py`
- Import pattern: `from shared.<module_name> import function_name`

**New Pipeline Step (e.g., text preprocessing):**
- Implementation: `2_Scripts/2_Text/2.{next}_<StepName>.py`
- Outputs: `4_Outputs/2_Text/<StepName>/timestamp/`
- Logs: `3_Logs/2_Text/<StepName>/timestamp.log`

**Utilities:**
- Shared helpers: `2_Scripts/shared/<utility_name>.py`
- Path utilities: Extend `2_Scripts/shared/path_utils.py`
- Validation: Extend `2_Scripts/shared/data_validation.py`

**Tests:**
- Unit tests: `tests/unit/test_<module>.py`
- Integration tests: `tests/integration/test_<pipeline_step>.py`
- Fixtures: `tests/fixtures/` (sample data files)

## Special Directories

**.planning/phases/:**
- Purpose: GSD command phase plans and documentation
- Contains: `PLAN.md`, `CONTEXT.md`, `RESEARCH.md`, `SUMMARY.md` per phase
- Generated: Yes (by `/gsd:plan-phase`)
- Committed: Yes
- Numbered: Two-digit phase numbers (01-60)

**.planning/codebase/:**
- Purpose: Codebase analysis documents for orchestrator reference
- Contains: `ARCHITECTURE.md`, `STRUCTURE.md`, `STACK.md`, `CONVENTIONS.md`, etc.
- Generated: Yes (by `/gsd:map-codebase`)
- Committed: Yes

**.planning/quick/:**
- Purpose: Quick task plans (smaller than full phases)
- Contains: `0XX-PLAN.md` (3-digit task numbers)
- Generated: Yes

**.___archive/legacy/:**
- Purpose: Old scripts retained for reference but not executed
- Contains: Original Step 2 implementations (2.0, 2.1, etc.)
- Generated: Yes (archived during refactors)
- Committed: Yes

**.___archive/debug/:**
- Purpose: Debug and investigation scripts
- Contains: `verification/`, `investigations/` subdirectories
- Generated: Yes (ad-hoc debugging)
- Committed: Yes

**.claude/:**
- Purpose: Claude Code configuration and state
- Contains: Claude's internal files
- Generated: Yes (by Claude Code)
- Committed: Sometimes (configuration yes, cache no)

**4_Outputs/backup_*/
- Purpose: Backups created before major changes
- Generated: Yes (manual backups before refactoring)
- Committed: Yes (for safety)

**tests/fixtures/:**
- Purpose: Test data and sample configurations
- Contains: `sample_yaml/`, parquet files for testing
- Generated: Partially (sample configs, some test data)
- Committed: Yes

---

*Structure analysis: 2025-02-10*
