# Technology Stack

**Analysis Date:** 2026-03-25

## Languages

**Primary:**
- Python >=3.9 - All pipeline code (`src/f1d/`), tests (`tests/`), table generation (`outputs/generate_all_tables.py`)

**Secondary:**
- C++17 - Tokenizer compiler for text processing (configured in `config/project.yaml` under `step_03.compiler`: `g++`, `-O2`, `-Wall -Wextra`)
- YAML - Configuration files (`config/project.yaml`, `config/variables.yaml`)
- LaTeX - Publication-ready regression tables and thesis document (`docs/Draft/`, `outputs/all_tables.tex`)

## Runtime

**Environment:**
- Python 3.9+ (supports 3.9, 3.10, 3.11, 3.12, 3.13 per CI matrix in `.github/workflows/ci.yml`)
- CI runs on Ubuntu latest via GitHub Actions

**Package Manager:**
- pip with setuptools build backend
- Lockfile: `requirements.txt` with pinned versions for reproducibility
- Build system: `pyproject.toml` (PEP 621, setuptools>=61.0 + wheel)
- Package version: 6.0.0 (declared in both `pyproject.toml` and `src/f1d/__init__.py`)

## Frameworks

**Core:**
- pandas 2.2.3 - Primary data manipulation framework; DataFrames are the universal data container across all 4 stages
- numpy 2.3.2 - Numerical operations (used throughout all modules)
- statsmodels 0.14.6 - OLS regression, VIF diagnostics, Probit models (`src/f1d/shared/panel_ols.py`, `src/f1d/shared/diagnostics.py`, `src/f1d/econometric/ceo_presence_probit.py`)
- linearmodels >=0.6.0 - PanelOLS with fixed effects and IV2SLS regression (`src/f1d/shared/panel_ols.py`, `src/f1d/shared/iv_regression.py`)
- scipy 1.16.1 - Statistical tests and scientific computing
- scikit-learn 1.7.2 - Machine learning utilities
- lifelines 0.30.0 - Cox Proportional Hazards survival analysis (`src/f1d/econometric/run_h9_takeover_hazards.py`)

**Data Validation:**
- pydantic >=2.0,<3.0 - Configuration models and data validation (`src/f1d/shared/config/base.py`, `src/f1d/shared/config/env.py`)
- pydantic-settings >=2.0,<3.0 - Environment variable configuration with `F1D_` prefix (`src/f1d/shared/config/env.py`)
- pandera >=0.20.0 - DataFrame schema validation (`src/f1d/shared/data_validation.py`)

**Testing:**
- pytest >=8.0 - Test runner (`pyproject.toml` [tool.pytest.ini_options])
- pytest-cov >=5.0 - Coverage reporting (30% overall threshold, 10% per tier)
- pytest-mock >=3.12 - Mocking utilities
- pytest-benchmark >=4.0.0 - Performance regression tests
- pytest-mypy >=0.10.0 - Type checking in tests

**Build/Dev:**
- ruff 0.9.0 - Linting and formatting (replaces black, flake8, isort); rule sets: E, W, F, I, B, C4, UP, ARG, SIM
- mypy 1.14.1 - Static type checking with tiered strictness (Tier 1 strict on `f1d.shared.*`, Tier 2 relaxed on stage modules)
- pre-commit 3.8+ - Git hooks for quality enforcement (`.pre-commit-config.yaml`)
- pydocstyle >=2.3.0 - Docstring verification
- interrogate >=1.5.0 - Docstring coverage

## Key Dependencies

**Critical:**
- pandas 2.2.3 - Core data structure for all pipeline stages; pinned for reproducibility
- statsmodels 0.14.6 - Pinned to 0.14.6; 0.14.0 introduced breaking GLM changes (see `requirements.txt` comments)
- linearmodels >=0.6.0 - PanelOLS and IV2SLS for all hypothesis tests; `WeakInstrumentError` enforces F>10 for instruments (`src/f1d/shared/iv_regression.py`)
- pyarrow 21.0.0 - Parquet file I/O; pinned to 21.0.0 for Python 3.8-3.13 compatibility (23.0+ requires 3.10+)
- structlog >=25.0 - Structured logging throughout pipeline (`src/f1d/shared/logging/config.py`, `src/f1d/shared/logging/context.py`, `src/f1d/shared/logging/handlers.py`)
- lifelines 0.30.0 - Cox PH and cause-specific hazard models for H9 takeover analysis

**Infrastructure:**
- psutil 7.2.1 - Memory monitoring for chunked processing (`src/f1d/shared/chunked_reader.py`, `src/f1d/shared/observability/memory.py`)
- PyYAML 6.0.2 - YAML config file loading (`src/f1d/shared/config/loader.py`)
- openpyxl 3.1.5 - Excel file reading for input data
- rapidfuzz >=3.14.0 - Fuzzy string matching for entity linking (`src/f1d/shared/string_matching.py`, `src/f1d/sample/link_entities.py`); optional with graceful degradation
- python-dateutil 2.9.0 - Date parsing utilities

**Type Stubs:**
- pandas-stubs >=2.2.0 - Type stubs for pandas
- types-psutil >=6.0.0 - Type stubs for psutil
- types-requests >=2.31.0 - Type stubs for requests
- types-PyYAML >=6.0.0 - Type stubs for PyYAML

## Configuration

**Environment:**
- Environment variables prefixed with `F1D_` (loaded via pydantic-settings in `src/f1d/shared/config/env.py`)
- `.env` file support (`.env.example` present in repo root)
- Optional env vars: `F1D_API_TIMEOUT_SECONDS` (default: 30), `F1D_MAX_RETRIES` (default: 3)

**Project Config:**
- `config/project.yaml` - Main pipeline configuration (steps, paths, parameters, determinism settings, chunk processing, string matching thresholds)
- `config/variables.yaml` - Variable source definitions mapping outputs to columns (stage 1-4 output paths and file patterns)
- `pyproject.toml` - Build system, tool configuration (ruff, mypy, pytest, coverage, bandit)
- `.pre-commit-config.yaml` - Pre-commit hook configuration (pre-commit-hooks v5.0.0, ruff v0.9.0, mypy v1.14.1)

**Build:**
- `pyproject.toml` - PEP 621 project metadata, setuptools src-layout
- Source layout: `src/f1d/` (declared via `[tool.setuptools.packages.find] where = ["src"]`)

## Platform Requirements

**Development:**
- Python >=3.9
- pip for dependency installation
- g++ compiler (C++17) for tokenizer compilation (step_03)
- pre-commit for git hooks
- Windows (MSYS2/Git Bash) or Linux/macOS

**Production:**
- No deployment target - local research pipeline
- Deterministic execution: random_seed=42, thread_count=1, sort_inputs=true (configured in `config/project.yaml`)
- Memory-aware chunked processing: max_memory_percent=80%, base_chunk_size=10000, enable_throttling=true

**CI/CD:**
- GitHub Actions (`.github/workflows/ci.yml`)
- Matrix testing: Python 3.9, 3.10, 3.11, 3.12, 3.13
- Pipeline: Lint (ruff check + format + mypy Tier 1) -> Test (tiered coverage) -> E2E (on push to main only, 1200s timeout)
- Coverage upload to Codecov via `codecov/codecov-action@v4`
- Artifacts: coverage XML, HTML, JSON reports retained 30 days

**Econometric Methods Supported:**
- PanelOLS with firm-clustered SEs and entity/time/industry FE (`src/f1d/shared/panel_ols.py`)
- IV2SLS with instrument diagnostics and weak-instrument detection (`src/f1d/shared/iv_regression.py`)
- Cox Proportional Hazards / cause-specific hazard models (`src/f1d/econometric/run_h9_takeover_hazards.py` via lifelines)
- Probit with marginal effects (`src/f1d/econometric/ceo_presence_probit.py` via statsmodels)
- OLS first-stage residualization (Biddle 2009 investment residual in `src/f1d/shared/variables/_compustat_engine.py`)
- Mean-centering for interaction terms (`src/f1d/shared/centering.py`)

---

*Stack analysis: 2026-03-25*
