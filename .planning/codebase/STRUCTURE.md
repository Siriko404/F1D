# Codebase Structure

**Analysis Date:** 2026-02-21

## Directory Layout

```
F1D/
├── .benchmarks/          # Benchmark results (not committed)
├── .claude/               # Claude Code workspace
├── .github/workflows/      # CI/CD pipelines (GitHub Actions)
├── .git/                  # Git repository
├── .mypy_cache/           # mypy type-checking cache
├── .planning/              # Planning documents (GSD orchestration)
├── .pytest_cache/           # pytest cache
├── .ruff_cache/            # ruff linter cache
├── config/                 # YAML configuration files
│   ├── project.yaml        # Main pipeline configuration
│   ├── variables.yaml      # Variable source mappings
│   └── project.yaml.backup
├── docs/                   # Documentation (ARCHITECTURE_STANDARD.md, etc.)
├── inputs/                 # External input data (not in repo)
│   ├── Earnings_Calls_Transcripts/
│   ├── LM_dictionary/Loughran-McDonald_MasterDictionary_1993-2024.csv
│   ├── comp_na_daily_all/
│   ├── CRSP_DSF/
│   ├── tr_ibes/
│   ├── CRSPCompustat_CCM/
│   ├── FF1248/
│   ├── SDC/
│   └── CCCL_instrument/
├── logs/                   # Pipeline execution logs (timestamped)
├── outputs/                # Pipeline outputs (timestamped directories)
│   ├── sample/             # Stage 1 outputs
│   ├── text/               # Stage 2 outputs
│   ├── variables/           # Stage 3 outputs (panels)
│   └── econometric/         # Stage 4 outputs (regressions)
├── src/f1d/               # Main package (src-layout)
│   ├── __init__.py         # Public API exports
│   ├── econometric/        # Stage 4: Hypothesis test scripts
│   ├── reporting/           # Summary statistics generation
│   ├── sample/              # Stage 1: Sample construction
│   ├── shared/             # Tier 1: Cross-cutting utilities
│   │   ├── config/         # Configuration management
│   │   ├── logging/        # Structured logging
│   │   ├── observability/  # Memory/throughput/anomaly tracking
│   │   └── variables/      # 50+ variable builders
│   ├── text/               # Stage 2: Text processing
│   └── variables/          # Stage 3: Panel builders
├── tests/                  # Test suite
├── pyproject.toml          # Package configuration
├── requirements.txt         # Production dependencies
├── .pre-commit-config.yaml  # Git hooks
├── README.md               # Package documentation
└── .gitignore              # Git exclusions
```

## Directory Purposes

**config/:**
- Purpose: YAML configuration files for pipeline behavior
- Contains: `project.yaml` (main config), `variables.yaml` (variable mappings)
- Key files: `project.yaml` (year ranges, paths, determinism settings), `variables.yaml` (source locations for each variable)

**src/f1d/:**
- Purpose: Main Python package implementing the 4-stage pipeline
- Contains: Stage-specific modules + shared utilities

**src/f1d/shared/:**
- Purpose: Tier 1 shared utilities (strict mypy mode)
- Contains:
  - `config/`: Pydantic configuration models (`base.py`, `loader.py`, `datasets.py`, `env.py`, `paths.py`)
  - `logging/`: Structured logging (`config.py`, `context.py`, `handlers.py`)
  - `observability/`: Memory tracking, throughput, checksums (`memory.py`, `throughput.py`, `files.py`, `stats.py`, `anomalies.py`)
  - `variables/`: 50+ variable builders (`base.py`, `cash_holdings.py`, `size.py`, `lev.py`, `manager_qa_uncertainty.py`, etc.)
  - Core utilities: `panel_ols.py`, `iv_regression.py`, `data_validation.py`, `path_utils.py`, `chunked_reader.py`, `string_matching.py`, `financial_utils.py`, `industry_utils.py`, `centering.py`

**src/f1d/sample/:**
- Purpose: Stage 1 sample construction scripts
- Contains: `clean_metadata.py`, `link_entities.py`, `build_tenure_map.py`, `assemble_manifest.py`
- Key files: `link_entities.py` (4-tier fuzzy matching), `assemble_manifest.py` (final manifest assembly)

**src/f1d/text/:**
- Purpose: Stage 2 text processing scripts
- Contains: `tokenize_transcripts.py`, `build_linguistic_variables.py`
- Key files: `tokenize_transcripts.py` (sklearn CountVectorizer, parallel year processing)

**src/f1d/variables/:**
- Purpose: Stage 3 panel builder scripts
- Contains: `build_h0_*.py`, `build_h1_cash_holdings_panel.py`, `build_h2_investment_panel.py`, `build_h3_payout_policy_panel.py`, `build_h4_leverage_panel.py`, `build_h5_dispersion_panel.py`, `build_h6_cccl_panel.py`, `build_h7_illiquidity_panel.py`, `build_h8_policy_risk_panel.py`, `build_h9_takeover_panel.py`, `build_h10_tone_at_top_panel.py`
- Key files: `build_h1_cash_holdings_panel.py` (call-level panel with `CashHoldings_lead` via fiscal year aggregation)

**src/f1d/econometric/:**
- Purpose: Stage 4 econometric regression scripts
- Contains: `run_h0_*.py`, `run_h1_cash_holdings.py`, `run_h2_investment.py`, `run_h3_payout_policy.py`, `run_h4_leverage.py`, `run_h5_dispersion.py`, `run_h6_cccl.py`, `run_h7_illiquidity.py`, `run_h8_policy_risk.py`, `run_h9_takeover_hazards.py`, `run_h10_tone_at_top.py`
- Key files: `run_h1_cash_holdings.py` (firm-clustered SEs, one-tailed hypothesis tests, LaTeX table generation)

**src/f1d/reporting/:**
- Purpose: Summary statistics and descriptive tables
- Contains: `generate_summary_stats.py`
- Key files: `generate_summary_stats.py` (descriptive statistics, correlation matrix)

**tests/:**
- Purpose: Test suite for all pipeline stages
- Contains:
  - `conftest.py`: pytest fixtures
  - `unit/`: Unit tests (fast, isolated)
  - `integration/`: Integration tests (subprocess execution)
  - `regression/`: Regression tests (baseline comparisons)
  - `performance/`: Performance regression tests
  - `fixtures/`: Test data fixtures
  - `factories/`: Test data factories

**.planning/codebase/:**
- Purpose: Codebase mapping documents for GSD orchestration
- Contains: `STACK.md`, `INTEGRATIONS.md`, `ARCHITECTURE.md`, `STRUCTURE.md`, `CONVENTIONS.md`, `TESTING.md`, `CONCERNS.md`

## Key File Locations

**Entry Points:**
- `src/f1d/__init__.py`: Package initialization, public API exports (`get_latest_output_dir`, `run_panel_ols`)
- `src/f1d/shared/panel_ols.py`: Panel OLS regression interface
- `src/f1d/shared/config/loader.py`: Configuration loading with caching

**Configuration:**
- `config/project.yaml`: Main pipeline configuration (year ranges, paths, determinism, logging)
- `config/variables.yaml`: Variable source mappings
- `pyproject.toml`: Package metadata, dependencies, tool configurations (pytest, ruff, mypy, coverage)

**Core Logic:**
- `src/f1d/shared/variables/`: All variable builders (50+ files, one per variable)
- `src/f1d/shared/panel_ols.py`: Panel OLS with fixed effects
- `src/f1d/shared/iv_regression.py`: IV regression utilities
- `src/f1d/shared/data_validation.py`: Pandera schema validation
- `src/f1d/shared/string_matching.py`: Fuzzy matching utilities

**Testing:**
- `tests/conftest.py`: Shared pytest fixtures
- `tests/factories/`: Test data factories
- `tests/fixtures/`: Test data fixtures

## Naming Conventions

**Files:**
- Scripts: `run_{hypothesis}.py` (Stage 4), `build_{hypothesis}_panel.py` (Stage 3)
- Variable builders: `{variable_name}.py` (snake_case)
- Tests: `test_{module}.py` or `test_{subject}.py`

**Directories:**
- Stage outputs: `{stage_name}/` (e.g., `sample/`, `text/`, `variables/`, `econometric/`)
- Timestamped outputs: `{YYYY-MM-DD_HHMMSS}/` subdirectories under stage directories
- Shared subdirectories: `config/`, `logging/`, `observability/`, `variables/`

## Where to Add New Code

**New Feature:**
- Primary code: `src/f1d/econometric/` (for hypothesis tests)
- Test code: `tests/unit/test_{feature}.py` (for unit tests)
- Variable builder (if new variable needed): `src/f1d/shared/variables/{variable_name}.py`
- Export from `src/f1d/shared/variables/__init__.py`

**New Component/Module:**
- Implementation: `src/f1d/shared/{subdirectory}/` (for shared utilities)
- Type-checking: mypy strict mode enforced for `f1d.shared.*` modules

**Utilities:**
- Shared helpers: `src/f1d/shared/{utility_name}.py` (e.g., `path_utils.py`, `data_validation.py`)
- Add to `src/f1d/shared/__init__.py` if public API needed

**New Hypothesis Test:**
- Panel builder: `src/f1d/variables/build_h{N}_{name}_panel.py` (follow existing pattern)
- Econometric script: `src/f1d/econometric/run_h{N}_{name}.py` (follow existing pattern)
- Integration test: `tests/integration/test_{feature}_integration.py`
- Unit test: `tests/unit/test_h{N}_{name}.py`

**New Variable Builder:**
- Implementation: `src/f1d/shared/variables/{variable_name}.py`
- Inherit from `VariableBuilder` base class
- Implement `build()` method returning `VariableResult`
- Use data engine singleton pattern if accessing expensive data sources
- Export from `src/f1d/shared/variables/__init__.py`

## Special Directories

**.mypy_cache/:**
- Purpose: mypy type-checking cache
- Generated: Yes
- Committed: No

**.pytest_cache/:**
- Purpose: pytest cache
- Generated: Yes
- Committed: No

**.ruff_cache/:**
- Purpose: ruff linter cache
- Generated: Yes
- Committed: No

**.benchmarks/:
- Purpose: Benchmark results from performance tests
- Generated: Yes
- Committed: No

**logs/:**
- Purpose: Pipeline execution logs (one timestamped log file per script run)
- Generated: Yes
- Committed: No

**outputs/:**
- Purpose: Pipeline outputs (timestamped directories per stage)
- Generated: Yes
- Committed: No

**inputs/:**
- Purpose: External input data (not included in repo)
- Generated: No
- Committed: No (contains external datasets)

---

*Structure analysis: 2026-02-21*
