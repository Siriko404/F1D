# Technology Stack

**Analysis Date:** 2026-02-15

## Languages

**Primary:**
- Python 3.9-3.13 - Core data processing language (all scripts)

**Secondary:**
- C++17 - Compiled tokenization utilities (archived legacy scripts in `_archive/legacy_archive/legacy/ARCHIVE_OLD/`)

## Runtime

**Environment:**
- Python 3.9, 3.10, 3.11, 3.12, 3.13 (tested on GitHub Actions)
- Minimum required: Python 3.8 (specified in requirements.txt)
- Recommended: Python 3.10 or 3.11 for best performance

**Package Manager:**
- pip - Python package installer
- Lockfile: requirements.txt (pinned versions)

## Frameworks

**Core:**
- pandas 2.2.3 - Data manipulation and analysis
- numpy 2.3.2 - Numerical computing foundation
- scipy 1.16.1 - Scientific computing and statistical functions
- statsmodels 0.14.6 - Statistical modeling and econometrics
- linearmodels (via statsmodels) - Panel data regression models

**Testing:**
- pytest 8.0+ - Test runner and framework
- pytest-cov 5.0+ - Code coverage reporting
- pytest-mock 3.12+ - Mocking utilities
- pytest-benchmark 4.0+ - Performance benchmarking

**Build/Dev:**
- setuptools 61.0+ - Build backend (pyproject.toml)
- structlog 25.0+ - Structured logging
- pydantic 2.0+ - Data validation and settings
- pydantic-settings 2.0+ - Configuration management
- pandera 0.20.0+ - DataFrame schema validation

## Key Dependencies

**Critical:**
- pandas 2.2.3 - Primary DataFrame library used throughout all scripts
- numpy 2.3.2 - Numerical operations required by pandas and statistical libraries
- statsmodels 0.14.6 - Econometric modeling (OLS, IV regression, diagnostics)
- PyYAML 6.0.2 - Configuration file parsing (`config/project.yaml`)
- PyArrow 21.0.0 - Parquet file I/O engine (used by pandas)

**Infrastructure:**
- structlog 25.0+ - Structured logging with JSON output support (`src/f1d/shared/logging/`)
- psutil 7.2.1 - System and process monitoring (memory tracking, CPU monitoring)
- python-dateutil 2.9.0.post0 - Date parsing and manipulation
- rapidfuzz >=3.14.0 (optional) - Fast fuzzy string matching for entity linking

**Statistical Modeling:**
- scikit-learn 1.7.2 - Machine learning utilities (available for future use)
- lifelines 0.30.0 - Survival analysis (Cox proportional hazards for takeover risk models)

**Data Formats:**
- openpyxl 3.1.5 - Excel file I/O (available for future use)

**Type Checking:**
- mypy 1.14+ - Static type checking
- Type stubs: pandas-stubs, types-psutil, types-requests, types-PyYAML

## Configuration

**Environment:**
- pydantic-settings 2.0+ - Settings management via `BaseSettings`
- Environment variable support via `.env` files (`.env.example` provided)
- Required env vars (from `.env.example`):
  - `F1D_API_TIMEOUT_SECONDS=30`
  - `F1D_MAX_RETRIES=3`

**Build:**
- Build config: `pyproject.toml` (PEP 517/518 compliant)
- setuptools as build backend
- Package name: `f1d`
- Version: 6.0.0
- src-layout package structure (`src/f1d/`)

**Project Configuration:**
- `config/project.yaml` - Pipeline configuration (paths, thresholds, settings)
- `.coveragerc` - Coverage.py configuration
- `.pre-commit-config.yaml` - Pre-commit hooks configuration

## Platform Requirements

**Development:**
- Python 3.9-3.13 (recommended 3.10 or 3.11)
- pip for package management
- Git for version control
- Recommended: 16GB RAM (minimum 8GB)
- C++ compiler (g++) for compiled tokenization (legacy/archived only)

**Production:**
- Deployment target: Local execution or CI/CD (GitHub Actions)
- No cloud dependencies
- Single-threaded execution by default (`thread_count=1` in config)
- Deterministic processing (random_seed=42 in config)

**Operating Systems:**
- Windows (primary development environment per git status)
- Linux (CI/CD via GitHub Actions - ubuntu-latest)
- Cross-platform: Uses pathlib.Path throughout for path operations

---

*Stack analysis: 2026-02-15*
