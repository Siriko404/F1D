# Technology Stack

**Analysis Date:** 2026-02-14

## Languages

**Primary:**
- Python 3.9+ - Core language for data processing, analysis, and econometric modeling

**Secondary:**
- C++17 - Native compilation for text tokenization performance (`src/f1d/text/tokenize_and_count.py`)
- YAML - Configuration files
- Markdown - Documentation

## Runtime

**Environment:**
- Python 3.9, 3.10, 3.11, 3.12, 3.13 (tested versions)

**Package Manager:**
- pip (via setuptools)
- Lockfile: Not present (version pins in `requirements.txt`)

## Frameworks

**Core:**
- pandas==2.2.3 - DataFrame operations and data manipulation
- numpy==2.3.2 - Numerical computing and array operations
- scipy==1.16.1 - Scientific computing and statistical functions

**Testing:**
- pytest>=8.0.0 - Test runner and framework
- pytest-cov>=4.1.0 - Coverage reporting
- pytest-mock>=3.12 - Mocking utilities
- pytest-benchmark>=4.0.0 - Performance benchmarking

**Build/Dev:**
- setuptools>=61.0 - Package building and installation
- ruff>=0.9.0 - Linting and formatting
- mypy>=1.14 - Static type checking
- pre-commit>=3.8 - Pre-commit hooks

**Statistical Modeling:**
- statsmodels==0.14.6 - Econometric regression models
- scikit-learn==1.7.2 - Machine learning utilities (tokenization)
- lifelines==0.30.0 - Survival analysis (takeover hazards)

## Key Dependencies

**Critical:**
- pyarrow==21.0.0 - Parquet file I/O (pinned for Python 3.8-3.13 compatibility)
- PyYAML==6.0.2 - Configuration file parsing
- structlog>=25.0 - Structured logging with context variables

**Infrastructure:**
- pydantic>=2.0,<3.0 - Data validation and settings management
- pydantic-settings>=2.0,<3.0 - Environment variable configuration
- psutil==7.2.1 - System resource monitoring
- python-dateutil==2.9.0.post0 - Date/time utilities

**Optional:**
- rapidfuzz>=3.14.0 - Fuzzy string matching for entity linking (graceful degradation)

**Type Stubs (for mypy):**
- pandas-stubs>=2.2.0
- types-psutil>=6.0.0
- types-requests>=2.31.0
- types-PyYAML>=6.0.0

## Configuration

**Environment:**
- Pydantic Settings for type-safe environment variables
- `src/f1d/shared/config/env.py` - Environment configuration
- `src/f1d/shared/config/loader.py` - YAML config loader
- `src/f1d/shared/config/step_configs.py` - Step-specific configs

**Build:**
- `pyproject.toml` - Project metadata, tooling config, dependency management
- `requirements.txt` - Pinned dependency versions
- `.coveragerc` - Coverage.py configuration
- `.pre-commit-config.yaml` - Pre-commit hook configuration

**Paths:**
- `config/project.yaml` - Main pipeline configuration
- `1_Inputs/` - Raw data inputs
- `3_Logs/` - Execution logs
- `4_Outputs/` - Pipeline outputs

## Platform Requirements

**Development:**
- Python 3.9+
- Git for version control
- g++ compiler (for C++ tokenization module, requires C++17 standard)
- Unix-like environment recommended (Windows MSYS/Git Bash supported)

**Production:**
- Local execution (no cloud deployment)
- Data stored locally in Parquet format
- Outputs to timestamped directories in `4_Outputs/`

---

*Stack analysis: 2026-02-14*
