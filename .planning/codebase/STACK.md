# Technology Stack

**Analysis Date:** 2026-02-21

## Languages

**Primary:**
- Python 3.9-3.13 - All data processing and econometric analysis

**No secondary languages detected.** Project is pure Python.

## Runtime

**Environment:**
- Python >= 3.9 required
- Tested on Python 3.9, 3.10, 3.11, 3.12, 3.13

**Package Manager:**
- pip with `requirements.txt`
- Lockfile: Not present (no requirements.lock)
- Build backend: setuptools >= 61.0

## Frameworks

**Core:**
- pandas 2.2.3 - Data manipulation and analysis
- numpy 2.3.2 - Numerical computing
- pydantic 2.x - Data validation and settings management
- pydantic-settings 2.x - Environment configuration

**Statistical/Econometric:**
- statsmodels 0.14.6 - Regression analysis (pinned - 0.14.0 had breaking changes)
- linearmodels 0.6.0 - Panel data models
- scipy 1.16.1 - Scientific computing
- scikit-learn 1.7.2 - Machine learning utilities
- lifelines 0.30.0 - Survival analysis (takeover hazards)

**Testing:**
- pytest 8.0 - Test framework
- pytest-cov 5.0 - Coverage reporting
- pytest-mock 3.12 - Mocking utilities
- pytest-benchmark 4.0 - Performance benchmarks
- pytest-mypy 0.10 - Type checking tests

**Build/Dev:**
- ruff 0.9.0 - Linting and formatting
- mypy 1.14 - Static type checking
- pre-commit 3.8 - Git hooks

## Key Dependencies

**Critical:**
- pyarrow 21.0.0 - Parquet file I/O (pinned for Python 3.8-3.13 compatibility)
- pandera 0.20.0 - DataFrame schema validation
- structlog 25.0 - Structured logging
- PyYAML 6.0.2 - Configuration file parsing
- openpyxl 3.1.5 - Excel file handling
- rapidfuzz 3.14.0 - Fuzzy string matching (optional, graceful degradation)

**Infrastructure:**
- psutil 7.2.1 - System resource monitoring
- python-dateutil 2.9.0.post0 - Date parsing utilities

**Type Stubs:**
- pandas-stubs 2.2.0 - Type hints for pandas
- types-psutil 6.0.0 - Type hints for psutil
- types-requests 2.31.0 - Type hints for requests
- types-PyYAML 6.0.0 - Type hints for PyYAML

## Configuration

**Environment:**
- Environment variables prefixed with `F1D_`
- Uses pydantic-settings for `.env` file loading
- Key configs: `F1D_API_TIMEOUT_SECONDS`, `F1D_MAX_RETRIES`
- Template file: `.env.example`

**Build:**
- `pyproject.toml` - Main configuration (build, pytest, coverage, ruff, mypy, bandit)
- `.coveragerc` - Legacy coverage config (still present)
- `config/project.yaml` - Pipeline step configuration
- `config/variables.yaml` - Variable source definitions

**Type Checking Tiers:**
- Tier 1 (shared modules): strict mypy mode
- Tier 2 (stage modules): moderate mypy mode with relaxed rules

## Platform Requirements

**Development:**
- Python 3.9+
- pip package manager
- Git with pre-commit hooks

**Production:**
- Local execution (no deployment target)
- Outputs written to `outputs/` directory
- Logs written to `logs/` directory
- Deterministic processing with `random_seed: 42`

---

*Stack analysis: 2026-02-21*
