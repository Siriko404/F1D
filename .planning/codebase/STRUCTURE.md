# Codebase Structure

**Analysis Date:** 2026-02-20

## Directory Layout

```
F1D/                              # Project root
├── src/
│   └── f1d/                      # Main Python package (installed as f1d)
│       ├── __init__.py            # Package entry point; exports version + public API
│       ├── sample/                # Stage 1: Sample construction scripts
│       ├── text/                  # Stage 2: Text processing scripts
│       ├── variables/             # Stage 3: Panel builder scripts (per hypothesis)
│       ├── econometric/           # Stage 4: Econometric test scripts (per hypothesis)
│       ├── financial/             # Legacy financial module (V1/V2 variants)
│       └── shared/                # Tier 1 shared utilities (imported by all stages)
│           ├── config/            # Pydantic-settings config system
│           ├── variables/         # Variable builder classes (one per variable)
│           ├── logging/           # Structured logging (structlog)
│           └── observability/     # Stats, anomaly detection, memory, throughput
├── config/
│   ├── project.yaml               # Main project config (data range, paths, step params)
│   └── variables.yaml             # Variable-level config for Stage 3 builders
├── inputs/                        # Raw data inputs (NOT committed – large Parquet files)
│   ├── Earnings_Calls_Transcripts/ # Earnings call transcripts (Unified-info.parquet, speaker_data_{year}.parquet)
│   ├── comp_na_daily_all/         # Compustat quarterly data
│   ├── CRSP_DSF/                  # CRSP daily stock data
│   ├── CRSPCompustat_CCM/         # CCM link table (gvkey ↔ permno)
│   ├── Execucomp/                 # ExecuComp CEO data
│   ├── tr_ibes/                   # IBES analyst estimates
│   ├── FirmLevelRisk/             # Hassan et al. political risk scores
│   ├── CCCL_instrument/           # CCCL IV instrument data
│   ├── SDC/                       # M&A deal data (takeover hazards)
│   ├── LM_dictionary/             # Loughran-McDonald dictionary
│   ├── Manager_roles/             # Manager role classifications
│   ├── FF1248/                    # Fama-French 12/48 industry codes
│   └── SEC_Edgar_Letters/         # SEC comment letters
├── outputs/                       # Pipeline outputs (timestamped subdirectories)
│   ├── 1.1_CleanMetadata/
│   ├── 1.2_LinkEntities/
│   ├── 1.3_BuildTenureMap/
│   ├── 1.4_AssembleManifest/
│   ├── 2_Textual_Analysis/
│   ├── 3_Financial_Features/      # Legacy Stage 3 outputs
│   ├── variables/                 # Stage 3 panel outputs (per hypothesis)
│   └── econometric/               # Stage 4 regression outputs (per hypothesis)
├── logs/                          # Per-step run logs (timestamped .log files)
├── tests/
│   ├── unit/                      # Unit tests (pytest)
│   ├── integration/               # Integration tests (full pipeline or multi-step)
│   ├── regression/                # Regression / stability tests (baseline checksums)
│   ├── performance/               # Performance benchmarks
│   ├── verification/              # Dry-run verification tests (all 4 stages)
│   ├── factories/                 # Test data factories
│   ├── fixtures/                  # Static test fixtures (JSON, checksums)
│   ├── utils/                     # Test harness utilities
│   └── conftest.py                # Shared pytest fixtures
├── docs/                          # Technical standards and planning documents
├── .github/workflows/             # CI/CD workflows
├── pyproject.toml                 # Build config, dependencies, tool settings (ruff, mypy, pytest)
├── requirements.txt               # Pinned dependency list
├── .coveragerc                    # Coverage configuration
├── .pre-commit-config.yaml        # Pre-commit hooks (ruff, mypy, black)
└── README.md                      # Project overview and pipeline instructions
```

## Directory Purposes

**`src/f1d/sample/`:**
- Purpose: Stage 1 — sample construction (filter transcripts, link firms, build tenure, assemble manifest)
- Contains: `build_sample_manifest.py` (orchestrator), `clean_metadata.py`, `link_entities.py`, `build_tenure_map.py`, `assemble_manifest.py`, `utils.py`
- Key files: `src/f1d/sample/build_sample_manifest.py` (Stage 1 entry point), `src/f1d/sample/assemble_manifest.py`

**`src/f1d/text/`:**
- Purpose: Stage 2 — tokenize call transcripts, compute LM dictionary word counts, build linguistic variable Parquet files
- Contains: `tokenize_transcripts.py`, `build_linguistic_variables.py`
- Key files: `src/f1d/text/build_linguistic_variables.py` (produces `linguistic_variables_{year}.parquet`)

**`src/f1d/variables/`:**
- Purpose: Stage 3 — merge manifest + linguistic + financial variables into one call-level panel per hypothesis
- Contains: `build_{hypothesis}_panel.py` scripts (14 scripts)
- Key files: `src/f1d/variables/build_ceo_clarity_extended_panel.py` (canonical full-feature panel used by summary stats), `src/f1d/variables/build_h1_cash_holdings_panel.py` through `build_h8_policy_risk_panel.py`

**`src/f1d/econometric/`:**
- Purpose: Stage 4 — run panel OLS regressions, output LaTeX tables, diagnostics, Markdown reports
- Contains: `test_{hypothesis}.py` scripts (13 scripts) + `generate_summary_stats.py`
- Key files: `src/f1d/econometric/test_ceo_clarity.py`, `src/f1d/econometric/generate_summary_stats.py`

**`src/f1d/shared/`:**
- Purpose: Shared utilities — imported by every stage; no business logic
- Key files:
  - `src/f1d/shared/path_utils.py` — `get_latest_output_dir()`, `ensure_output_dir()`, `validate_input_file()`
  - `src/f1d/shared/data_loading.py` — `load_parquet()`, `safe_merge()`
  - `src/f1d/shared/panel_ols.py` — `run_panel_ols()`, `CollinearityError`
  - `src/f1d/shared/financial_utils.py` — winsorization, financial ratio helpers
  - `src/f1d/shared/regression_utils.py` — regression helpers
  - `src/f1d/shared/latex_tables.py`, `src/f1d/shared/latex_tables_accounting.py` — LaTeX table generation
  - `src/f1d/shared/string_matching.py` — fuzzy string matching (rapidfuzz)
  - `src/f1d/shared/chunked_reader.py` — memory-aware chunked Parquet reading

**`src/f1d/shared/config/`:**
- Purpose: All configuration loading and validation
- Key files:
  - `src/f1d/shared/config/base.py` — `ProjectConfig` (root pydantic-settings class)
  - `src/f1d/shared/config/loader.py` — `get_config()` (cached singleton), `load_variable_config()`
  - `src/f1d/shared/config/paths.py` — `PathsSettings`
  - `src/f1d/shared/config/step_configs.py` — per-step config classes (Step00Config..Step09Config)

**`src/f1d/shared/variables/`:**
- Purpose: One module per variable; Builder pattern; private compute engines loaded once
- Key files:
  - `src/f1d/shared/variables/base.py` — `VariableBuilder`, `VariableResult`, `VariableStats`
  - `src/f1d/shared/variables/__init__.py` — re-exports all ~60 builders
  - `src/f1d/shared/variables/_compustat_engine.py` — `CompustatEngine` (loads Compustat once, caches)
  - `src/f1d/shared/variables/_crsp_engine.py` — `CRSPEngine` (loads CRSP yearly)
  - `src/f1d/shared/variables/_ibes_engine.py` — `IBESEngine`
  - `src/f1d/shared/variables/_hassan_engine.py` — Hassan political risk engine

**`src/f1d/shared/observability/`:**
- Purpose: Observability utilities (stats, anomalies, memory, throughput, dual-writer logging)
- Key files:
  - `src/f1d/shared/observability/logging.py` — `DualWriter` class
  - `src/f1d/shared/observability/stats.py` — per-step stats functions
  - `src/f1d/shared/observability/anomalies.py` — `detect_anomalies_zscore()`, `detect_anomalies_iqr()`

**`config/`:**
- Purpose: YAML configuration files (NOT secrets)
- Key files: `config/project.yaml`, `config/variables.yaml`

**`outputs/`:**
- Purpose: All pipeline outputs. Each sub-step creates a `{YYYY-MM-DD_HHMMSS}/` subdirectory
- Generated: Yes (at runtime). NOT committed to git (in `.gitignore`)

**`logs/`:**
- Purpose: Per-run log files for each pipeline step
- Generated: Yes (at runtime). NOT committed to git

**`inputs/`:**
- Purpose: Raw research data (Compustat, CRSP, IBES, earnings call transcripts, etc.)
- Generated: No (must be provided externally). NOT committed to git

**`tests/`:**
- Purpose: Full test suite across unit, integration, regression, performance, and verification tiers
- Key files: `tests/conftest.py`, `tests/unit/`, `tests/integration/`, `tests/verification/`

**`docs/`:**
- Purpose: Architecture standards, variable catalogs, refactor plans — reference documentation
- Contains: `ARCHITECTURE_STANDARD.md`, `CODE_QUALITY_STANDARD.md`, `VARIABLE_CATALOG_V1.md`, `VARIABLE_CATALOG_V2_V3.md`, `TIER_MANIFEST.md`, etc.

## Naming Conventions

**Files (pipeline scripts):**
- Stage scripts: `{stage_number}_{descriptive_name}.py` — e.g. `clean_metadata.py` (Step 1.1), `build_linguistic_variables.py` (Step 2.2)
- Variable builders: `{variable_snake_case}.py` — e.g. `cash_holdings.py`, `ceo_qa_uncertainty.py`
- Panel builders: `build_{hypothesis}_panel.py` — e.g. `build_h1_cash_holdings_panel.py`
- Econometric tests: `test_{hypothesis}.py` — e.g. `test_h1_cash_holdings.py`, `test_ceo_clarity.py`
- Shared utilities: `{domain}_utils.py` or `{domain}.py` — e.g. `path_utils.py`, `financial_utils.py`, `panel_ols.py`
- Private compute engines: `_{source}_engine.py` — e.g. `_compustat_engine.py`, `_crsp_engine.py`

**Directories:**
- Stage output dirs match the step ID label: `1.1_CleanMetadata`, `2_Textual_Analysis`, `variables`, `econometric`
- Timestamped run dirs: `YYYY-MM-DD_HHMMSS` (e.g. `2026-02-19_150340`)

**Python classes:**
- Variable builders: `{VariableName}Builder` — e.g. `CashHoldingsBuilder`, `CEOQAUncertaintyBuilder`
- Config classes: `{Scope}Settings` or `{Scope}Config` — e.g. `DataSettings`, `ProjectConfig`, `StepsConfig`
- Exceptions: `{Issue}Error` — e.g. `OutputResolutionError`, `CollinearityError`

**Log IDs (step identifiers):**
- Format: `{major}.{minor}_{DescriptiveName}` — e.g. `1.1_CleanMetadata`, `4.1.1_CeoClarity`

## Key File Locations

**Entry Points:**
- Stage 1: `src/f1d/sample/build_sample_manifest.py`
- Stage 2: `src/f1d/text/tokenize_transcripts.py`, `src/f1d/text/build_linguistic_variables.py`
- Stage 3: `src/f1d/variables/build_{hypothesis}_panel.py`
- Stage 4: `src/f1d/econometric/test_{hypothesis}.py`

**Configuration:**
- `config/project.yaml` — all runtime config (year range, paths, step parameters)
- `config/variables.yaml` — per-variable config for Stage 3 builders
- `src/f1d/shared/config/base.py` — `ProjectConfig` class definition
- `src/f1d/shared/config/loader.py` — `get_config()`, `load_variable_config()`
- `pyproject.toml` — build, lint, type-check, test settings

**Core Logic:**
- `src/f1d/shared/path_utils.py` — inter-stage output resolution
- `src/f1d/shared/panel_ols.py` — panel regression engine
- `src/f1d/shared/variables/base.py` — VariableBuilder base class
- `src/f1d/shared/variables/_compustat_engine.py` — Compustat data loading
- `src/f1d/shared/data_loading.py` — `safe_merge()`, `load_parquet()`

**Testing:**
- `tests/conftest.py` — shared pytest fixtures
- `tests/factories/` — test data factories for config and financial data
- `tests/fixtures/baseline_checksums.json` — regression baseline checksums

## Where to Add New Code

**New hypothesis panel (Stage 3):**
- Primary script: `src/f1d/variables/build_{hypothesis}_panel.py`
- Individual variable builders: `src/f1d/shared/variables/{variable_name}.py` (one per new variable)
- Register in: `src/f1d/shared/variables/__init__.py`
- Tests: `tests/unit/test_{hypothesis}_variables.py`

**New econometric test (Stage 4):**
- Script: `src/f1d/econometric/test_{hypothesis}.py`
- Tests: `tests/unit/test_{hypothesis}_regression.py`

**New shared variable builder:**
- Implementation: `src/f1d/shared/variables/{variable_name}.py` (subclass `VariableBuilder`)
- Register: add import and `__all__` entry in `src/f1d/shared/variables/__init__.py`

**New shared utility:**
- Location: `src/f1d/shared/{domain}_utils.py` or `src/f1d/shared/{domain}.py`
- Test: `tests/unit/test_{domain}.py`

**New config setting:**
- For project-wide settings: add field to appropriate class in `src/f1d/shared/config/base.py`
- For per-step settings: add to `src/f1d/shared/config/step_configs.py`
- Add YAML entry to `config/project.yaml`

## Special Directories

**`.planning/`:**
- Purpose: GSD planning documents, milestones, phases, roadmap
- Generated: Yes (by planning tools)
- Committed: Yes

**`.benchmarks/`:**
- Purpose: Performance benchmark results
- Generated: Yes (at test runtime)
- Committed: Partially

**`src/f1d.egg-info/`:**
- Purpose: Python package metadata (generated by `pip install -e .`)
- Generated: Yes
- Committed: No (in `.gitignore`)

**`.mypy_cache/`:**
- Purpose: mypy type-check cache
- Generated: Yes
- Committed: No

---

*Structure analysis: 2026-02-20*
