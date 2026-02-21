# Codebase Structure

**Analysis Date:** 2026-02-20

## Directory Layout

```
F1D/
├── src/f1d/                    # Main package (src-layout)
│   ├── shared/                 # Tier 1: Cross-cutting utilities
│   │   ├── config/             # Pydantic config models
│   │   ├── logging/            # Logging infrastructure
│   │   ├── observability/      # Monitoring, throughput, memory
│   │   └── variables/          # Variable builders (50+ files)
│   ├── sample/                 # Stage 1: Sample construction
│   ├── text/                   # Stage 2: Text processing
│   ├── variables/              # Stage 3: Panel builders
│   └── econometric/            # Stage 4: Hypothesis tests
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests (fast, isolated)
│   ├── integration/            # Integration tests (subprocess)
│   ├── regression/             # Regression/baseline tests
│   ├── verification/           # Dry-run verification tests
│   ├── performance/            # Performance benchmarks
│   ├── factories/              # Test data factories
│   ├── fixtures/               # Test fixtures
│   └── utils/                  # Test utilities
├── config/                     # Configuration files
├── inputs/                     # Raw input data (not in repo)
├── outputs/                    # Pipeline outputs (not in repo)
├── logs/                       # Execution logs
├── docs/                       # Documentation
└── .planning/                  # Planning documents
```

## Directory Purposes

**`src/f1d/shared/`:**
- Purpose: Tier 1 cross-cutting utilities
- Contains: Path utils, panel OLS, config, logging, observability, all variable builders
- Key files: `path_utils.py`, `panel_ols.py`, `__init__.py`

**`src/f1d/shared/variables/`:**
- Purpose: Individual variable builders (one file per variable)
- Contains: 50+ builder files, base classes, private engines
- Key files: `base.py`, `_compustat_engine.py`, `_crsp_engine.py`

**`src/f1d/sample/`:**
- Purpose: Stage 1 - Sample construction scripts
- Contains: Entity linking, tenure mapping, manifest assembly
- Key files: `assemble_manifest.py`, `link_entities.py`, `build_tenure_map.py`

**`src/f1d/text/`:**
- Purpose: Stage 2 - Text processing scripts
- Contains: Tokenization, linguistic variable construction
- Key files: `tokenize_transcripts.py`, `build_linguistic_variables.py`

**`src/f1d/variables/`:**
- Purpose: Stage 3 - Panel builders for each hypothesis
- Contains: Scripts that load variables and merge into panels
- Key files: `build_h1_cash_holdings_panel.py`, `build_h0_1_manager_clarity_panel.py`

**`src/f1d/econometric/`:**
- Purpose: Stage 4 - Hypothesis test scripts
- Contains: OLS regressions, LaTeX output generation
- Key files: `run_h1_cash_holdings.py`, `run_h0_1_manager_clarity.py`

**`tests/`:**
- Purpose: Comprehensive test coverage
- Contains: Unit, integration, regression, verification tests
- Key files: `conftest.py` (shared fixtures)

**`config/`:**
- Purpose: Centralized configuration
- Contains: `project.yaml` (main config), `variables.yaml` (variable definitions)
- Key files: `project.yaml`

**`docs/`:**
- Purpose: Architecture and standards documentation
- Contains: Standards docs, variable catalogs, upgrade guides
- Key files: `ARCHITECTURE_STANDARD.md`, `TIER_MANIFEST.md`

## Key File Locations

**Entry Points:**
- `src/f1d/__init__.py`: Package entry point, re-exports core utilities
- `src/f1d/sample/assemble_manifest.py`: Stage 1 final step
- `src/f1d/text/build_linguistic_variables.py`: Stage 2 main output
- `src/f1d/variables/build_*.py`: Stage 3 panel builders
- `src/f1d/econometric/run_*.py`: Stage 4 hypothesis tests

**Configuration:**
- `config/project.yaml`: Main configuration (paths, parameters, thresholds)
- `config/variables.yaml`: Variable definitions and metadata
- `pyproject.toml`: Python package configuration, tool settings
- `requirements.txt`: Production dependencies

**Core Logic:**
- `src/f1d/shared/path_utils.py`: Path resolution, timestamp handling
- `src/f1d/shared/panel_ols.py`: Panel regression with fixed effects
- `src/f1d/shared/variables/base.py`: VariableBuilder base class
- `src/f1d/shared/variables/_compustat_engine.py`: Compustat data engine
- `src/f1d/shared/variables/_crsp_engine.py`: CRSP data engine

**Testing:**
- `tests/conftest.py`: Pytest fixtures (subprocess_env, factories)
- `tests/factories/`: Test data factories for config, financial data
- `tests/verification/`: Dry-run tests for CI validation

## Naming Conventions

**Files:**
- Scripts: `build_{hypothesis}_panel.py` (Stage 3), `run_{hypothesis}.py` (Stage 4)
- Variable builders: `{variable_name}.py` (snake_case, matches variable name)
- Private engines: `_{source}_engine.py` (underscore prefix for internal)
- Tests: `test_{module}_{feature}.py`

**Directories:**
- Package directories: `snake_case` (e.g., `shared`, `variables`, `econometric`)
- Output directories: `{step_id}` with dots (e.g., `1.4_AssembleManifest`, `2.2_Variables`)
- Timestamped outputs: `YYYY-MM-DD_HHMMSS` format

**Classes:**
- Variable builders: `{VariableName}Builder` (PascalCase, matches file)
- Config models: `{Section}Config` (e.g., `DataConfig`, `LoggingConfig`)
- Exceptions: `{ErrorType}Error` (e.g., `PathValidationError`)

**Functions:**
- Public: `snake_case` (e.g., `get_latest_output_dir`, `run_panel_ols`)
- Private: `_leading_underscore` (e.g., `_check_thin_cells`, `_format_coefficient_table`)

## Where to Add New Code

**New Variable Builder:**
1. Create `src/f1d/shared/variables/{variable_name}.py`
2. Inherit from `VariableBuilder`, implement `build()` method
3. Export from `src/f1d/shared/variables/__init__.py`
4. Add test file `tests/unit/test_{variable_name}.py`

**New Hypothesis Test:**
1. Stage 3: Create `src/f1d/variables/build_{hypothesis}_panel.py`
2. Stage 4: Create `src/f1d/econometric/run_{hypothesis}.py`
3. Add tests in `tests/unit/test_{hypothesis}_regression.py`
4. Update `README.md` with run commands

**New Utility Function:**
1. Add to appropriate file in `src/f1d/shared/`
2. Export from `src/f1d/shared/__init__.py`
3. Add unit test in `tests/unit/test_{module}.py`

**New Configuration Option:**
1. Add to `config/project.yaml` under appropriate section
2. Add Pydantic model in `src/f1d/shared/config/`
3. Update any affected scripts

## Special Directories

**`src/f1d/shared/variables/`:**
- Purpose: All variable builders (50+ files)
- Generated: No
- Committed: Yes
- Note: Private engines (`_*.py`) are internal, not exported

**`inputs/`:**
- Purpose: Raw data files (Compustat, CRSP, IBES, transcripts)
- Generated: No (externally provided)
- Committed: No (in .gitignore)

**`outputs/`:**
- Purpose: Pipeline outputs organized by stage
- Generated: Yes (by pipeline scripts)
- Committed: No (in .gitignore)
- Structure: `{step_id}/{timestamp}/`

**`logs/`:**
- Purpose: Execution logs
- Generated: Yes
- Committed: No

**`tests/fixtures/`:**
- Purpose: Test data fixtures
- Generated: Can be (see `synthetic_generator.py`)
- Committed: Yes (small fixtures)

**`docs/plans/`:**
- Purpose: Planning documents for future work
- Generated: No
- Committed: Yes

---

*Structure analysis: 2026-02-20*
