# Technology Stack

**Analysis Date:** 2026-02-15

## Languages

**Primary:**
- Python 3.9-3.13 - Data processing pipeline, econometric analysis, text analysis

**Secondary:**
- Not applicable - Python-only codebase

## Runtime

**Environment:**
- Python 3.14.2 (development), supports 3.9-3.13 per project configuration

**Package Manager:**
- pip - Standard Python package manager
- Lockfile: Not present (uses pinned versions in requirements.txt)

## Frameworks

**Core:**
- pandas 2.2.3 - Data manipulation and analysis
- numpy 2.3.2 - Numerical computing
- pyarrow 21.0.0 - Columnar data format (Parquet I/O)

**Statistical Modeling:**
- statsmodels 0.14.6 - Statistical models and regressions
- scikit-learn 1.7.2 - Machine learning utilities
- lifelines 0.30.0 - Survival analysis (Cox PH, competing risks)
- linearmodels - Panel OLS with fixed effects (optional dependency)

**Testing:**
- pytest 8.0+ - Test runner
- pytest-cov 4.1.0+ - Coverage reporting
- pytest-mock 3.12+ - Mocking utilities
- pytest-benchmark 4.0.0+ - Performance benchmarks

**Build/Dev:**
- ruff 0.9.0+ - Linting and formatting
- mypy 1.14+ - Static type checking
- pre-commit 3.8+ - Git pre-commit hooks
- pydantic 2.0+ - Data validation and settings
- pydantic-settings 2.0+ - Environment-based configuration

## Key Dependencies

**Critical:**
- pandas - Core data structure and operations throughout pipeline
- pyarrow - Parquet file I/O for all input/output data
- statsmodels - GLM, OLS regression, survival analysis
- linearmodels - Panel OLS with fixed effects for econometric models

**Infrastructure:**
- yaml - Configuration file loading (PyYAML 6.0.2)
- structlog 25.0+ - Structured logging with JSON output
- psutil 7.2.1 - System monitoring and memory tracking
- python-dateutil 2.9.0 - Date/time parsing

**Optional:**
- rapidfuzz 3.14.0+ - Fuzzy string matching for entity linking (Tier 3 feature)

## Configuration

**Environment:**
- YAML-based configuration: `config/project.yaml`
- Environment variables via `.env` (template in `.env.example`)
- Pydantic settings classes for type-safe configuration

**Build:**
- `pyproject.toml` - Project metadata, pytest config, ruff config, mypy config
- `requirements.txt` - Pinned dependency versions
- `.coveragerc` - Coverage.py configuration
- `.pre-commit-config.yaml` - Pre-commit hook definitions

## Platform Requirements

**Development:**
- Python 3.9 or higher
- 16GB RAM recommended (8GB minimum for partial pipeline)
- Modern CPU with SSD for optimal performance

**Production:**
- Desktop/laptop execution (academic research context)
- No server deployment required
- Local filesystem storage (no cloud dependencies)

---

*Stack analysis: 2026-02-15*
