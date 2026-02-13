# Technology Stack

**Analysis Date:** 2026-02-12

## Languages

**Primary:**
- Python 3.9+ (target: 3.8-3.13) - All data processing, statistical analysis, and econometric modeling

**Secondary:**
- C++ (g++ with c++17) - Token counting compiler for performance-critical text processing (`2_Scripts/2_Text/`)

## Runtime

**Environment:**
- Python 3.8 minimum, 3.9+ recommended
- Tested on Python 3.8, 3.9, 3.10, 3.11, 3.12, 3.13 via CI matrix

**Package Manager:**
- pip with `requirements.txt`
- No lockfile present (consider adding requirements.lock for reproducibility)

## Frameworks

**Core Data Processing:**
- pandas 2.2.3 - DataFrame operations, primary data manipulation
- numpy 2.3.2 - Numerical computing foundation
- PyArrow 21.0.0 - Parquet file engine (pinned for Python 3.8-3.13 compatibility)

**Statistical Modeling:**
- statsmodels 0.14.6 - Fixed effects OLS regression, model diagnostics (pinned for API stability)
- scipy 1.16.1 - Statistical tests, distributions
- linearmodels - Panel OLS with fixed effects, IV/2SLS regression (imported with graceful fallback)
- lifelines 0.30.0 - Cox proportional hazards for takeover risk models

**Machine Learning:**
- scikit-learn 1.7.2 - Available for future use (not currently used in pipeline)

**Testing:**
- pytest 8.0+ - Test runner with markers (unit, integration, regression, e2e, performance, slow)
- pytest-cov 4.1+ - Coverage reporting
- pytest-benchmark 4.0+ - Performance regression testing
- pytest-mypy 0.10+ - Type checking integration

**Build/Dev:**
- ruff - Linting and formatting (configured in `pyproject.toml`)
- mypy - Type checking with strict mode for new modules (progressive adoption)

## Key Dependencies

**Critical:**
- pandas 2.2.3 - All scripts use for DataFrame operations
- PyArrow 21.0.0 - Parquet I/O engine (pinned for Python 3.8 compatibility; 23.0+ requires 3.10+)
- statsmodels 0.14.6 - Regression analysis (0.14.0 had breaking GLM API changes)
- PyYAML 6.0.2 - Configuration file parsing (`config/project.yaml`)

**Infrastructure:**
- psutil 7.2.1 - Memory tracking, CPU monitoring, disk space checking
- python-dateutil 2.9.0.post0 - Date parsing and manipulation
- openpyxl 3.1.5 - Excel file I/O (available for future use)

**Optional:**
- rapidfuzz 3.14.0+ - Fuzzy string matching for entity linking (graceful degradation if missing)

## Configuration

**Environment:**
- YAML-based configuration via `config/project.yaml`
- No `.env` file detected (environment validation prepared but not actively used)
- Schema-based validation available in `2_Scripts/shared/env_validation.py`

**Build:**
- `pyproject.toml` - pytest, coverage, ruff, mypy configuration
- `requirements.txt` - Pinned dependencies with version rationale comments

**Key Config Sections (`config/project.yaml`):**
- `project` - Name, version, description
- `data` - Year range (2002-2018)
- `paths` - Input/output directory structure
- `determinism` - Random seed (42), thread count (1), sort inputs (true)
- `chunk_processing` - Memory limits, chunk sizes, throttling
- `logging` - Level, format, timestamp format
- `string_matching` - Fuzzy matching thresholds (company 92%, entity 85%)

## Platform Requirements

**Development:**
- Python 3.8+ (3.10/3.11 recommended for performance)
- g++ compiler with c++17 support (for token counting)
- Windows/Unix cross-platform support via `pathlib.Path`

**Production:**
- Local execution only (no cloud deployment)
- Large Parquet files (1GB-10GB typical)
- Memory-efficient chunked processing available

---

## Gaps vs. Industry Standard Python Data Projects

### Dependency Management
- **Gap**: No `requirements.lock` or `poetry.lock` for exact reproducibility
- **Industry Standard**: Use `pip-tools` (requirements.in + requirements.txt) or `poetry` (pyproject.toml + poetry.lock)
- **Recommendation**: Add `pip-compile` workflow or migrate to `poetry`

### Virtual Environment
- **Gap**: No explicit virtual environment configuration
- **Industry Standard**: `.python-version` file, `venv/` in `.gitignore`, or `pyproject.toml` `[tool.python]`
- **Recommendation**: Add `.python-version` file (3.11) for pyenv/pyenv-win users

### Type Checking Coverage
- **Gap**: MyPy only runs on `shared/observability.*` in strict mode; most modules excluded
- **Industry Standard**: Full type coverage with `strict = true`
- **Current State**: Progressive rollout with exclusions in `pyproject.toml`
- **Recommendation**: Continue gradual adoption, add stubs for `linearmodels`

### Pre-commit Hooks
- **Gap**: No `.pre-commit-config.yaml` detected
- **Industry Standard**: Automated linting, formatting, type checking before commits
- **Recommendation**: Add pre-commit with ruff, mypy, trailing whitespace fixes

### Documentation
- **Gap**: No Sphinx/MkDocs configuration for API docs
- **Industry Standard**: Auto-generated API docs from docstrings
- **Current State**: Good inline docstrings with module headers
- **Recommendation**: Consider MkDocs with mkdocstrings for published docs

### Logging Framework
- **Gap**: Custom `DualWriter` class instead of standard `logging.handlers`
- **Industry Standard**: `logging.handlers.RotatingFileHandler` or structured logging (`structlog`)
- **Current State**: Functional but not standard
- **Recommendation**: Consider `structlog` for structured JSON logs

### Data Validation
- **Gap**: Custom `data_validation.py` instead of `pydantic` or `pandera`
- **Industry Standard**: `pandera` for DataFrame schemas, `pydantic` for config models
- **Current State**: Schema validation works but verbose
- **Recommendation**: Consider `pandera` for DataFrame schema validation

### Testing
- **Gap**: 60% coverage threshold (industry standard: 80%+ for data projects)
- **Current State**: Tiered coverage targets (90% critical, 80% important)
- **Recommendation**: Raise minimum to 70% overall, continue tiered approach

### CI/CD
- **Current State**: Good GitHub Actions setup with matrix testing
- **Gap**: No artifact upload for coverage reports, no caching of mypy results
- **Recommendation**: Add coverage artifact upload, consider `setup-python` caching

---

*Stack analysis: 2026-02-12*
