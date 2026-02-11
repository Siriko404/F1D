# Technology Stack

**Analysis Date:** 2025-02-10

## Languages

**Primary:**
- Python 3.8-3.13 - All pipeline scripts, shared utilities, and tests

**Secondary:**
- YAML - Configuration (`config/project.yaml`)
- Markdown - Documentation and reports
- Shell (Git Bash/MSYS) - CI/CD workflows

## Runtime

**Environment:**
- Python >= 3.8 (tested on 3.8, 3.9, 3.10, 3.11, 3.12, 3.13)
- Windows (MSYS_NT-10.0-26200), Linux (GitHub Actions ubuntu-latest)

**Package Manager:**
- pip
- Lockfile: present (pinned versions in `requirements.txt`)

## Frameworks

**Core:**
- pandas 2.2.3 - Data manipulation and analysis
- numpy 2.3.2 - Numerical computing
- scipy 1.16.1 - Scientific computing

**Statistical Modeling:**
- statsmodels 0.14.6 - Econometric regression, fixed effects, OLS
- scikit-learn 1.7.2 - Feature extraction (CountVectorizer), ML utilities
- lifelines 0.30.0 - Survival analysis (takeover hazard models)

**Testing:**
- pytest >= 8.0 - Test framework
- pytest-cov - Coverage reporting

**Build/Dev:**
- PyYAML 6.0.2 - Configuration parsing
- openpyxl 3.1.5 - Excel file I/O

## Key Dependencies

**Critical:**
- pyarrow 21.0.0 - Parquet file format (pinned for Python 3.8-3.13 compatibility)
  - Note: 23.0.0+ requires Python >= 3.10
  - Performance notes documented in `DEPENDENCIES.md`

**Infrastructure:**
- psutil 7.2.1 - System memory monitoring, throttling
- python-dateutil 2.9.0.post0 - Date parsing
- rapidfuzz >= 3.14.0 - Fuzzy string matching (optional, Tier 3 entity linking)
  - Pipeline degrades gracefully without it
  - Improves match rates for company names with spelling variations

## Configuration

**Environment:**
- YAML-based configuration (`config/project.yaml`)
- No .env file required (no API keys or external services)
- Environment validation via `2_Scripts/shared/env_validation.py`

**Build:**
- No build system required (pure Python)
- Pytest configuration in `pyproject.toml`
- Ruff configuration (caching in `.ruff_cache/`)

**Key configs:**
- `config/project.yaml` - Pipeline configuration, thresholds, paths
- `pyproject.toml` - Pytest settings, coverage configuration
- `.github/workflows/test.yml` - CI/CD matrix testing across Python versions

## Platform Requirements

**Development:**
- 8GB RAM minimum (small datasets, partial pipeline)
- 16GB RAM recommended (full pipeline, all steps)
- 32GB RAM for 2x-10x dataset scaling
- SSD/NVMe storage recommended for large dataset I/O

**Production:**
- Local execution (no cloud deployment target)
- Deterministic single-threaded processing (`thread_count=1`)
- Optional parallel processing for scaling (`thread_count=4`)

**Python Version Matrix:**
- Tested on: 3.8, 3.9, 3.10, 3.11, 3.12, 3.13
- CI runs tests on all versions via GitHub Actions

---

*Stack analysis: 2025-02-10*
