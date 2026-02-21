# Technology Stack

**Analysis Date:** 2026-02-20

## Languages

**Primary:**
- Python 3.9-3.13 - Main language for all data processing, econometric analysis, and pipeline orchestration

**Version Support:**
- Minimum: Python 3.9
- Tested: Python 3.9, 3.10, 3.11, 3.12, 3.13 (CI matrix)

## Runtime

**Environment:**
- CPython (standard Python interpreter)
- Virtual environment recommended (venv)

**Package Manager:**
- pip (primary)
- Project uses src-layout with editable install: `pip install -e .`
- Lockfile: requirements.txt with pinned versions

**Build System:**
- setuptools >= 61.0
- Build backend: setuptools.build_meta
- Config: `pyproject.toml`

## Frameworks

**Core Data Processing:**
- pandas 2.2.3 - DataFrame operations, data manipulation
- numpy 2.3.2 - Numerical computations
- pyarrow 21.0.0 - Parquet file I/O (pinned for Python 3.8-3.13 compatibility)

**Statistical Modeling:**
- statsmodels 0.14.6 - Econometric models (pinned for GLM compatibility)
- linearmodels >= 0.6.0 - Panel data regression (PanelOLS, IV2SLS)
- scipy 1.16.1 - Scientific computing, optimization
- scikit-learn 1.7.2 - Machine learning utilities
- lifelines 0.30.0 - Survival analysis (hazard models)

**Testing:**
- pytest >= 8.0 - Test framework
- pytest-cov >= 4.1 - Coverage reporting
- pytest-mock >= 3.12 - Mocking utilities
- pytest-benchmark >= 4.0 - Performance benchmarks

**Code Quality:**
- ruff >= 0.9.0 - Linting and formatting (replaces black, isort, flake8)
- mypy >= 1.14 - Static type checking
- pre-commit >= 3.8 - Git hooks for quality checks

## Key Dependencies

**Configuration Management:**
- pydantic >= 2.0 - Data validation and settings management
- pydantic-settings >= 2.0 - Environment variable loading
- PyYAML 6.0.2 - YAML config file parsing

**Logging & Observability:**
- structlog >= 25.0 - Structured logging with contextvars

**Data Validation:**
- pandera >= 0.20.0 - DataFrame schema validation

**Utilities:**
- psutil 7.2.1 - System/process monitoring
- rapidfuzz >= 3.14.0 - Fuzzy string matching (optional, graceful degradation)
- python-dateutil 2.9.0.post0 - Date parsing
- openpyxl 3.1.5 - Excel file handling

**Type Stubs (for mypy):**
- pandas-stubs >= 2.2.0
- types-psutil >= 6.0.0
- types-requests >= 2.31.0
- types-PyYAML >= 6.0.0

## Configuration

**Environment Variables:**
- `.env.example` template provided
- Variables loaded via pydantic-settings
- Key vars: `F1D_API_TIMEOUT_SECONDS`, `F1D_MAX_RETRIES`

**Configuration Files:**
- `pyproject.toml` - Project metadata, tool configs (pytest, ruff, mypy, coverage)
- `config/project.yaml` - Pipeline step configurations
- `config/variables.yaml` - Variable source definitions
- `requirements.txt` - Pinned dependencies

**YAML Configuration Structure:**
- Project settings: `config/project.yaml`
- Variable definitions: `config/variables.yaml`
- Loaded via: `src/f1d/shared/config/` modules

## Platform Requirements

**Development:**
- Python 3.9+
- Git
- pip

**Operating System:**
- Cross-platform (Windows, macOS, Linux)
- CI runs on ubuntu-latest
- Developed on Windows (path handling accounts for this)

**Production:**
- Local execution (no deployment target)
- File-based data pipeline (no database required)
- Memory-intensive operations (chunked processing available)

## Version Constraints

**Pinned Packages (do not upgrade without review):**
- `statsmodels==0.14.6` - Version 0.14.0 introduced breaking GLM changes
- `pyarrow==21.0.0` - Version 23.0.0+ requires Python >= 3.10

**Python Compatibility:**
- Supports Python 3.9 through 3.13
- Uses modern type hints and pattern matching where available

---

*Stack analysis: 2026-02-20*
