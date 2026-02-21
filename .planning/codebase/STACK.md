# Technology Stack

**Analysis Date:** 2026-02-20

## Languages

**Primary:**
- Python 3.13.5 (runtime) — all pipeline code; project targets >=3.9 for CI matrix

**Secondary:**
- C++ (c++17, g++ via subprocess) — invoked from `src/f1d/sample/build_sample_manifest.py` for a compiled tokenisation step configured via `config/project.yaml` (`step_03.compiler`)

## Runtime

**Environment:**
- CPython 3.13.5 (dev machine); CI matrix tests 3.9 / 3.10 / 3.11 / 3.12 / 3.13

**Package Manager:**
- pip (standard)
- Lockfile: `requirements.txt` (pinned versions for reproducibility — not a pip-lock format)

## Frameworks

**Core:**
- pandas 2.2.3 — all tabular data manipulation throughout the pipeline
- numpy 2.3.2 — numerical operations; array math
- pydantic 2.12.5 + pydantic-settings 2.10.1 — type-safe configuration models in `src/f1d/shared/config/`

**Statistical / Econometric:**
- scipy 1.16.1 — statistical tests, winsorisation helpers
- statsmodels 0.14.6 (pinned) — OLS baseline regressions; GLM; see `requirements.txt` note on 0.14.0 breaking changes
- scikit-learn 1.7.2 — utility transforms (StandardScaler, etc.)
- linearmodels 7.0 — Panel OLS with fixed effects (`src/f1d/shared/panel_ols.py`) and IV/2SLS (`src/f1d/shared/iv_regression.py`); used by all econometric test scripts
- lifelines 0.30.0 — Cox time-varying survival model for takeover hazard (`src/f1d/econometric/test_takeover_hazards.py`)

**Schema Validation:**
- pandera 0.26.1 — output DataFrame schema validation in `src/f1d/shared/output_schemas.py`

**Testing:**
- pytest 8.0+ — test runner; config in `pyproject.toml [tool.pytest.ini_options]`
- pytest-cov 4.1+ — coverage measurement; thresholds enforced in CI
- pytest-mock 3.12+ — mocking utilities
- pytest-benchmark 5.2.3 — performance regression tests in `.benchmarks/`
- pytest-mypy 0.10+ — mypy checks run as pytest tests

**Build/Dev:**
- setuptools >=61.0 / wheel — `src`-layout package build (`pyproject.toml [build-system]`)
- ruff 0.9.0 — linting (E/W/F/I/B/C4/UP/ARG/SIM rules) and formatting (Black-compatible 88-char lines)
- mypy 1.14.1 — static type checking; Tier 1 (`src/f1d/shared`) in strict mode, Tier 2 modules moderate
- pre-commit 3.8+ — runs ruff and mypy on commit via `.pre-commit-config.yaml`
- bandit 1.7.9 — SAST security scanning; configured in `pyproject.toml [tool.bandit]`

## Key Dependencies

**Critical:**
- `linearmodels` 7.0 — *not* in `requirements.txt`; must be installed separately. Required for all panel OLS and IV regressions. Import failures handled gracefully with `ImportError`.
- `statsmodels` 0.14.6 — pinned; `0.14.0` introduced breaking GLM changes. See `requirements.txt` comment.
- `pyarrow` 21.0.0 — Parquet I/O throughout; pinned for Python 3.8–3.13 compat (23.0+ requires >=3.10).
- `rapidfuzz` >=3.14.0 — optional fuzzy string matching for entity linking (`src/f1d/shared/string_matching.py`); pipeline degrades gracefully if missing.
- `lifelines` 0.30.0 — optional survival analysis; graceful degradation in `test_takeover_hazards.py`.

**Infrastructure:**
- `psutil` 6.1.0 — memory monitoring in `src/f1d/shared/observability/memory.py` and `chunked_reader.py`
- `structlog` 25.5.0 — structured JSON + console logging in `src/f1d/shared/logging/`
- `PyYAML` 6.0.2 — config file parsing (`config/project.yaml`, `config/variables.yaml`)
- `python-dateutil` 2.9.0 — date arithmetic in financial windows
- `openpyxl` 3.1.5 — Excel read/write (auxiliary reporting)
- `pydantic-settings` 2.10.1 — env-var → config model binding in `src/f1d/shared/config/`

## Configuration

**Environment:**
- `.env.example` documents two env vars: `F1D_API_TIMEOUT_SECONDS` and `F1D_MAX_RETRIES`
- `pydantic-settings` reads env vars with `F1D_` prefix; models live in `src/f1d/shared/config/env.py`, `base.py`, etc.
- Primary pipeline configuration via `config/project.yaml` (paths, step settings, compiler config)
- Variable source mappings via `config/variables.yaml` (stage/column/formula definitions)

**Build:**
- `pyproject.toml` — single source for build-system, project metadata, pytest, coverage, ruff, mypy, bandit config
- `.coveragerc` — legacy coverage config (targets old `2_Scripts` dir); superseded by `pyproject.toml [tool.coverage]`

## Platform Requirements

**Development:**
- Python >=3.9 (3.13.5 on dev machine)
- g++ with C++17 support (for tokenisation subprocess in step_03)
- pre-commit installed and initialised

**Production:**
- Local batch processing only — no server deployment detected
- Ubuntu-based CI (GitHub Actions `ubuntu-latest`)
- Input data files must be placed in `inputs/` directory before running (Compustat, CRSP, IBES, SDC — all local Parquet files; no live API calls)

---

*Stack analysis: 2026-02-20*
