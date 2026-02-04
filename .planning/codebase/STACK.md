# Technology Stack

**Analysis Date:** 2025-02-04

## Languages

**Primary:**
- Python 3.8-3.13 - All pipeline scripts, testing, and shared modules

**Secondary:**
- C++17 - Tokenization compiler (g++ executable for text processing performance)

## Runtime

**Environment:**
- Python 3.13.5 (development environment)
- Supports Python 3.8 through 3.13 (CI tested matrix)

**Package Manager:**
- pip with `requirements.txt`
- Lockfile: Present (`requirements.txt` with pinned versions)
- pyproject.toml for pytest configuration

## Frameworks

**Core:**
- pandas 2.2.3 - Data manipulation and analysis
- numpy 2.3.2 - Numerical computing
- scipy 1.16.1 - Scientific computing
- PyYAML 6.0.2 - Configuration file parsing

**Statistical Modeling:**
- statsmodels 0.14.6 - Econometric regression (GLM, OLS, fixed effects)
- scikit-learn 1.7.2 - Feature extraction (CountVectorizer)
- lifelines 0.30.0 - Survival analysis (available, usage unclear from exploration)

**Testing:**
- pytest 8.0+ (configured via pyproject.toml) - Test runner with markers for unit/integration/regression/e2e
- pytest-cov - Coverage reporting

**Build/Dev:**
- g++ (C++17 standard, -O2 optimization) - Compiles tokenization compiler
- RapidFuzz >=3.14.0 (optional) - Fuzzy string matching with graceful degradation

**Data Formats:**
- pyarrow 21.0.0 - Parquet file I/O
- openpyxl 3.1.5 - Excel file reading

## Key Dependencies

**Critical:**
- pandas 2.2.3 - Core data structure throughout pipeline
- pyarrow 21.0.0 - All intermediate data persistence (parquet format)
- PyYAML 6.0.2 - Config loading from `config/project.yaml`

**Infrastructure:**
- psutil 7.2.1 - Memory monitoring and throttling in chunked processing
- python-dateutil 2.9.0.post0 - Date parsing utilities
- RapidFuzz (optional) - Entity linking with fuzzy name matching

**Acquired Data Sources (not installed):**
- Loughran-McDonald MasterDictionary (local CSV file)
- CRSP/Compustat merged data (local parquet files)
- IBES analyst forecasts (local parquet files)
- Execucomp (local parquet files)
- SDC M&A deals (local files)
- Fama-French industry codes (local zip files)

## Configuration

**Environment:**
- Central config: `config/project.yaml`
- No environment variables currently used (infrastructure in place via `shared/env_validation.py` for future WRDS/API keys)
- No .env files present

**Build:**
- pyproject.toml - pytest configuration and markers
- requirements.txt - Pinned dependency versions

**Determinism:**
- Random seed: 42 (configured in project.yaml)
- Thread count: 1 (configurable, defaults to 1)
- Input sorting: enabled for reproducible ordering

## Platform Requirements

**Development:**
- Python 3.8+ required
- g++ compiler with C++17 support for tokenization
- 8GB+ RAM recommended (large parquet processing)
- Windows/Mac/Linux supported (Python paths use pathlib)

**Production:**
- Local execution only (no web server or API)
- Data files expected in `1_Inputs/` directory structure
- Outputs written to `4_Outputs/` with timestamped subdirectories

---

*Stack analysis: 2025-02-04*
