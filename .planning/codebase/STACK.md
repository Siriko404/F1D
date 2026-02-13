# Technology Stack

**Analysis Date:** 2026-02-12

## Languages

**Primary:**
- Python 3.8-3.13 - Main development language for all data processing and econometric analysis

**Secondary:**
- YAML - Configuration files (`config/project.yaml`)
- Markdown - Documentation

## Runtime

**Environment:**
- Python 3.9+ (target version for mypy, tested on 3.8-3.13)

**Package Manager:**
- pip - Package installer
- requirements.txt - Dependency manifest (pinned versions)

## Frameworks

**Core:**
- pandas 2.2.3 - DataFrame operations, data manipulation
- numpy 2.3.2 - Numerical computing
- pyarrow 21.0.0 - Parquet file I/O, efficient columnar storage

**Statistical Modeling:**
- statsmodels 0.14.6 - Regression analysis, statistical tests (pinned for reproducibility)
- scipy 1.16.1 - Statistical functions, optimization
- scikit-learn 1.7.2 - Machine learning utilities (CountVectorizer for text)
- lifelines 0.30.0 - Survival analysis, Cox proportional hazards

**Econometric:**
- linearmodels (unstated in requirements, via type stubs) - Panel OLS with fixed effects, IV/2SLS regression
  - Type stubs at `2_Scripts/stubs/linearmodels*.pyi`

**Testing:**
- pytest 8.0+ - Test framework
- pytest-cov 4.1+ - Coverage reporting
- pytest-benchmark 4.0+ - Performance benchmarks
- pytest-mypy 0.10+ - Type checking integration

**Build/Dev:**
- ruff - Linting and formatting (configured in pyproject.toml)
- mypy - Static type checking (progressive rollout)

## Key Dependencies

**Critical:**
- PyYAML 6.0.2 - Configuration file parsing
- openpyxl 3.1.5 - Excel file handling
- psutil 7.2.1 - System/process monitoring, memory tracking
- python-dateutil 2.9.0 - Date parsing

**Text Processing:**
- rapidfuzz 3.14.0+ - Fuzzy string matching (optional, graceful degradation)
  - Used for company/entity name matching in `2_Scripts/shared/string_matching.py`

**Statistical:**
- statsmodels 0.14.6 - Pinned version for reproducible regression analysis
  - Note: 0.14.0 introduced breaking changes (deprecated GLM link names)

**Data Formats:**
- pyarrow 21.0.0 - Pinned for Python 3.8-3.13 compatibility
  - Note: 23.0.0+ requires Python >= 3.10

## Configuration

**Environment:**
- YAML configuration at `config/project.yaml`
- No .env files (no runtime secrets required)
- PYTHONPATH must include `2_Scripts/` for imports

**Build:**
- pyproject.toml - Main configuration for pytest, coverage, ruff, mypy
- .coveragerc - Coverage.py settings (branch coverage enabled)
- type stubs in `2_Scripts/stubs/` for external packages without typing

**Key Config Sections:**
```yaml
# config/project.yaml structure
project:        # name, version, description
data:           # year_start, year_end
paths:          # inputs, scripts, logs, outputs
determinism:    # random_seed, thread_count
chunk_processing:  # memory management
logging:        # level, format
step_XX:        # Per-pipeline-step configuration
string_matching:   # Fuzzy match thresholds
```

## Platform Requirements

**Development:**
- Python 3.8+ (3.9+ recommended)
- 8GB+ RAM for large parquet file processing
- g++ compiler for C++ tokenization utilities (optional)

**Production:**
- GitHub Actions CI/CD (ubuntu-latest)
- Multi-version testing (3.8, 3.9, 3.10, 3.11, 3.12, 3.13)

## Type Checking

**Mypy Configuration:**
- Target: Python 3.9
- Strict mode enabled for `shared.observability.*`
- Progressive rollout: most scripts excluded initially
- Custom stubs for `linearmodels` package

**Type Stubs Location:**
- `2_Scripts/stubs/linearmodels.pyi`
- `2_Scripts/stubs/linearmodels.panel.pyi`
- `2_Scripts/stubs/linearmodels.iv.pyi`

---

*Stack analysis: 2026-02-12*
