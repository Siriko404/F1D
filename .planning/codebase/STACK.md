# Technology Stack

**Analysis Date:** 2026-02-14

## Languages

**Primary:**
- Python 3.9+ - All data processing, econometric analysis, and pipeline scripts
- Python 3.11 recommended for development (CI default)

**Secondary:**
- YAML - Configuration files (`config/project.yaml`)
- Markdown - Documentation

## Runtime

**Environment:**
- Python 3.9 - 3.13 supported
- CPython reference implementation

**Package Manager:**
- pip with requirements.txt
- Build backend: setuptools >= 61.0
- Lockfile: Not present (requirements.txt pins versions)

## Frameworks

**Core:**
- pandas 2.2.3 - DataFrame manipulation and data processing
- numpy 2.3.2 - Numerical computing
- scipy 1.16.1 - Statistical functions, optimization

**Econometric/Statistical:**
- statsmodels 0.14.6 - Regression analysis, statistical tests (pinned for reproducibility)
- linearmodels (optional) - Panel OLS with fixed effects, IV/2SLS regression
- lifelines 0.30.0 - Survival analysis for takeover hazard models
- scikit-learn 1.7.2 - Machine learning utilities

**Testing:**
- pytest >= 8.0 - Test runner
- pytest-cov >= 4.1.0 - Coverage reporting
- pytest-benchmark >= 4.0 - Performance benchmarks
- pytest-mock >= 3.12 - Mocking utilities

**Build/Dev:**
- ruff 0.9.0 - Linting and formatting (replaces flake8/black)
- mypy 1.14+ - Static type checking
- pre-commit 3.8+ - Git hooks for quality gates

## Key Dependencies

**Critical:**
- pyarrow 21.0.0 - Parquet file I/O, chunked reading (pinned for Python 3.8-3.13 compatibility)
- PyYAML 6.0.2 - Configuration file parsing
- structlog 25.0+ - Structured logging with JSON support
- pydantic 2.0+ / pydantic-settings 2.0+ - Data validation, settings management

**Infrastructure:**
- psutil 7.2.1 - Memory monitoring, system utilities
- rapidfuzz 3.14.0+ - Fuzzy string matching for entity linking (optional, graceful degradation)
- openpyxl 3.1.5 - Excel file support
- python-dateutil 2.9.0.post0 - Date parsing

**Type Stubs:**
- types-PyYAML - mypy type hints for YAML

## Configuration

**Environment:**
- pydantic-settings with `.env` file support
- Environment variable prefix: `F1D_`
- Key configs: `config/project.yaml` (main pipeline configuration)

**Build:**
- `pyproject.toml` - Project metadata, tool configuration (pytest, ruff, mypy, coverage, bandit)
- `requirements.txt` - Production dependencies with pinned versions
- `.pre-commit-config.yaml` - Git hooks configuration

**Tool Configuration (pyproject.toml):**
- pytest: importlib mode, strict markers, tier markers (unit, integration, e2e, slow, regression)
- ruff: 88 char line length, extended ruleset (E, W, F, I, B, C4, UP, ARG, SIM)
- mypy: Tier-based strictness (Tier 1 shared modules strict, Tier 2 stage modules moderate)
- coverage: 25% overall threshold, branch coverage enabled

## Platform Requirements

**Development:**
- Python 3.9+ with pip
- Git with pre-commit hooks
- Recommended: Python 3.11 for CI consistency

**Production:**
- Local execution (no deployment target)
- Memory-aware processing with configurable chunk sizes
- Deterministic execution with fixed random seed (42) and single-threaded processing

---

*Stack analysis: 2026-02-14*
