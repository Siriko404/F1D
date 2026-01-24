# Technology Stack

**Analysis Date:** 2026-01-24

## Languages

**Primary:**
- Python 3.8+ - All pipeline scripts and data processing logic
  - Supported versions: 3.8, 3.9, 3.10, 3.11, 3.12, 3.13
  - Minimum required: Python 3.8
  - Latest tested: Python 3.13

**Secondary:**
- C++17 - Compiled utilities for text tokenization (see `config/project.yaml` step_03.compiler)
  - Purpose: Performance optimization for text processing
  - Executable: g++
  - Standard: c++17
  - Optimization: -O2

## Runtime

**Environment:**
- Python 3.8-3.13 cross-platform (Windows, Linux, macOS)
- No containerization required (local execution)

**Package Manager:**
- pip (Python package manager)
- Lockfile: requirements.txt (strict version pinning)
- Optional dependency: rapidfuzz (not pinned, graceful degradation)

## Frameworks

**Core:**
- pandas 2.2.3 - Data manipulation and DataFrame operations
- numpy 2.3.2 - Numerical computing foundation
- scipy 1.16.1 - Scientific computing and statistical functions
- statsmodels 0.14.6 - Econometric modeling and fixed effects OLS
  - Purpose: Regression analysis, CEO fixed effects estimation
  - Pinned to 0.14.6 to avoid breaking GLM API changes
- scikit-learn 1.7.2 - Machine learning utilities (text vectorization)
  - Used in: `2_Scripts/2_Text/2.1_TokenizeAndCount.py` (CountVectorizer)
  - Future use: Available for additional ML features
- lifelines 0.30.0 - Survival analysis (hazard models)
  - Used in: `2_Scripts/4_Econometric/4.3_TakeoverHazards.py`
  - Purpose: Cox proportional hazards regression for takeover risk

**Testing:**
- pytest 8.0+ - Test framework and runner
  - Config: `pyproject.toml`
  - Markers: slow, integration, regression, unit, e2e
- pytest-cov - Code coverage reporting

**Build/Dev:**
- g++ (C++17) - Compile tokenization utilities
- subprocess (Python stdlib) - Script orchestration and subprocess validation

## Key Dependencies

**Critical:**
- pandas 2.2.3 - Core data manipulation across all scripts
- numpy 2.3.2 - Array operations and numerical computing
- statsmodels 0.14.6 - Fixed effects OLS regression for econometric analysis
  - Used in: `2_Scripts/4_Econometric/` (all regression scripts)
  - Used in: `2_Scripts/shared/regression_utils.py`
- PyArrow 21.0.0 - Parquet file I/O engine (used by pandas)
  - Purpose: Columnar data storage and retrieval
  - Pinned to 21.0.0 for Python 3.8-3.13 compatibility
  - Performance: Efficient for 1GB-10GB Parquet files
- PyYAML 6.0.2 - Configuration file parsing
  - Used in: All scripts (reads `config/project.yaml`)

**Infrastructure:**
- psutil 7.2.1 - System and process monitoring
  - Used in: All scripts (memory tracking, CPU monitoring)
  - Added in Phase 12 for observability features
- python-dateutil 2.9.0.post0 - Date parsing and manipulation
- rapidfuzz >=3.14.0 - Fuzzy string matching (optional)
  - Used in: `2_Scripts/shared/string_matching.py`
  - Used in: `2_Scripts/1_Sample/1.2_LinkEntities.py` (Tier 3 fuzzy matching)
  - Purpose: Entity matching for company names with variations
  - Graceful degradation: Pipeline runs without it (falls back to exact matching)

**Data Formats:**
- openpyxl 3.1.5 - Excel file I/O (future use)

## Configuration

**Environment:**
- Single source of truth: `config/project.yaml`
  - Paths, seeds, threads, log level, per-step parameters
  - Compiler flags for C++ utilities
  - String matching thresholds
  - Financial window parameters
- No environment variables required for basic operation
- No secrets management (local file-based data)

**Build:**
- Build configuration: `pyproject.toml` (pytest and coverage settings)
- Compiler config: `config/project.yaml` (step_03.compiler section)
- No bundling/packaging required (direct Python execution)

## Platform Requirements

**Development:**
- Python 3.8-3.13
- pip for dependency management
- g++ for C++ utilities (Linux/macOS) or compatible compiler (Windows)
- Git for version control
- 2GB+ RAM minimum (8GB+ recommended for large Parquet files)

**Production:**
- Local execution (no cloud deployment required)
- Disk space: 5GB+ for input data, 10GB+ for outputs
- No web server or API endpoints
- No containerization (optional but not required)

---

*Stack analysis: 2026-01-24*
