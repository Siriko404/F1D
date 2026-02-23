# Technology Stack

**Analysis Date:** 2026-02-21

## Languages

**Primary:**
- Python 3.9+ - All source code in `src/`

**Secondary:**
- YAML - Configuration files in `config/`
- LaTeX - Report generation templates

## Runtime

**Environment:**
- Python 3.9, 3.10, 3.11, 3.12, 3.13

**Package Manager:**
- pip - Dependency management
- Lockfile: `requirements.txt` (pinned versions)
- Build system: setuptools (via `pyproject.toml`)

## Frameworks

**Core:**
- pandas 2.2.3 - Data manipulation and analysis
- numpy 2.3.2 - Numerical computing
- scipy 1.16.1 - Scientific computing
- PyYAML 6.0.2 - Configuration file parsing
- pydantic 2.0+ - Data validation and settings management
- pydantic-settings 2.0+ - Environment-based configuration

**Statistical Modeling:**
- statsmodels 0.14.6 - Econometric modeling (pinned for GLM backward compatibility)
- linearmodels 0.6.0+ - Panel data regression (PanelOLS, AbsorbingLS, IV2SLS)
- scikit-learn 1.7.2 - CountVectorizer for text tokenization (src/f1d/text/tokenize_transcripts.py)
- lifelines 0.30.0 - Survival analysis (CoxTimeVaryingFitter for takeover hazards)

**Text Processing:**
- RapidFuzz 3.14.0+ - Fuzzy string matching for entity linking (optional, graceful degradation)
- openpyxl 3.1.5 - Excel file reading

**Data Formats:**
- pyarrow 21.0.0 - Parquet file I/O (pinned for Python 3.8-3.13 compatibility)
- openpyxl 3.1.5 - Excel file format support

**Testing:**
- pytest 8.0+ - Test runner and framework
- pytest-cov 5.0+ - Coverage reporting
- pytest-mock 3.12+ - Mocking support
- pytest-benchmark 4.0.0+ - Performance benchmarking

**Build/Dev:**
- ruff 0.9.0+ - Linter and code formatter
- mypy 1.14+ - Static type checker
- pre-commit 3.8+ - Git pre-commit hooks
- coverage.py - Test coverage tool

## Key Dependencies

**Critical:**
- linearmodels >= 0.6.0 - Panel OLS with entity and time fixed effects for CEO-level analysis
- statsmodels == 0.14.6 - GLM regression, VIF diagnostics, formula API (pinned for backward compatibility)
- pandas >= 2.0 - Core data structure for 112,968 earnings call observations
- pyarrow == 21.0.0 - Efficient parquet file reading for large datasets
- pydantic >= 2.0 - Type-safe configuration loading via `pydantic-settings`

**Infrastructure:**
- psutil 7.2.1 - Memory monitoring and throttling in `src/f1d/shared/chunked_reader.py`
- structlog 25.0 - Structured logging framework
- python-dateutil 2.9.0.post0 - Date parsing utilities
- pandera >= 0.20.0 - Data validation schemas in `src/f1d/shared/output_schemas.py`

**Type Stubs (for mypy strict checking):**
- pandas-stubs >= 2.2.0 - Type stubs for pandas
- types-psutil >= 6.0.0 - Type stubs for psutil
- types-requests >= 2.31.0 - Type stubs for requests
- types-PyYAML >= 6.0.0 - Type stubs for PyYAML

## Configuration

**Environment:**
- pydantic-settings-based configuration
- Env vars loaded from `.env` (template in `.env.example`)
- Key configs required:
  - `F1D_API_TIMEOUT_SECONDS` - API request timeout
  - `F1D_MAX_RETRIES` - Maximum retry attempts

**Build:**
- `pyproject.toml` - Main project configuration (build system, pytest, ruff, mypy, coverage)
- `config/project.yaml` - Pipeline configuration (paths, steps, thresholds)
- `config/variables.yaml` - Variable definitions and metadata

**Pre-commit:**
- `.pre-commit-config.yaml` - Ruff lint/format, mypy strict mode for shared modules

## Platform Requirements

**Development:**
- Python 3.9+ (tested on 3.9-3.13)
- 16GB RAM minimum, 32GB recommended for full pipeline
- ~50GB disk for input data, ~10GB for outputs

**Production:**
- Ubuntu/Linux recommended (CI runs on ubuntu-latest via GitHub Actions)
- Windows and macOS supported

---

*Stack analysis: 2026-02-21*
