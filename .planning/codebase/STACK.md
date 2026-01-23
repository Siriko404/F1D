# Technology Stack

**Analysis Date:** 2026-01-22

## Languages

**Primary:**
- Python 3.13.5 - Core data processing and analysis pipeline (requires 3.8+)

**Secondary:**
- C++17 - Tokenization and text processing (archived in `2_Scripts/ARCHIVE_OLD/2.3b_TokenizeText.cpp`)

## Runtime

**Environment:**
- Python 3.13.5 (MinGW-W64 on Windows)

**Package Manager:**
- pip - Python package manager
- Lockfile: Not present (requirements.txt used)

## Frameworks

**Core:**
- None (vanilla Python with data science libraries)

**Testing:**
- None (no test framework detected)

**Build/Dev:**
- g++ 15.2.0 (MinGW-W64 x86_64-ucrt-posix-seh) - C++ compiler for tokenization module
- Ruff - Python linter (indicated by `.ruff_cache/` directory)

## Key Dependencies

**Data Science Core:**
- pandas==2.2.3 - Data manipulation and analysis
- numpy==2.3.2 - Numerical computing
- scipy==1.16.1 - Scientific computing and statistical functions

**Statistical Modeling:**
- statsmodels==0.14.5 - Econometric modeling (OLS regressions, fixed effects)
- scikit-learn==1.7.2 - Machine learning utilities (CountVectorizer for text tokenization)
- lifelines==0.30.0 - Survival analysis (Cox proportional hazards for takeover risk)

**Data Formats:**
- PyYAML==6.0.2 - Configuration file parsing
- pyarrow==21.0.0 - Parquet file format support
- openpyxl==3.1.5 - Excel file read/write support

**Utilities:**
- python-dateutil==2.9.0.post0 - Date/time utilities

## Configuration

**Environment:**
- Central config: `config/project.yaml` - Single source of runtime truth
- Required: paths, seeds, thread counts, log level, step-specific parameters
- No environment variables required for runtime configuration

**Build:**
- C++ compilation configured in `config/project.yaml` under `step_03.compiler`:
  - executable: "g++"
  - standard: "c++17"
  - optimization: "-O2"
  - warnings: "-Wall -Wextra"

## Platform Requirements

**Development:**
- Python 3.8+ (tested with 3.13.5)
- g++ compiler with C++17 support
- Git (for reproducibility tracking)
- Windows, Linux, or macOS compatible

**Production:**
- Local execution (no cloud deployment)
- Disk space: ~10GB+ for input data and outputs
- RAM: 8GB+ recommended for large parquet file processing

---

*Stack analysis: 2026-01-22*
