# Technology Stack

**Analysis Date:** 2026-01-29

## Languages

**Primary:**
- Python 3.8-3.13 - Core pipeline processing, data manipulation, statistical modeling

**Secondary:**
- C++17 - Tokenization compiler (configured but not currently implemented)
- YAML - Configuration management (`config/project.yaml`)
- Markdown - Documentation and reports

## Runtime

**Environment:**
- Python 3.8+ (minimum)
- Python 3.13.5 (current development environment)
- Cross-platform: Windows (MSYS), Unix, macOS

**Package Manager:**
- pip (standard Python package manager)
- Lockfile: Present (`requirements.txt` with pinned versions)
- No package.json, go.mod, or Cargo.toml

## Frameworks

**Core:**
- pandas 2.2.3 - Data manipulation and analysis
- NumPy 2.3.2 - Numerical computing foundation
- PyArrow 21.0.0 - Parquet file I/O engine

**Statistical Modeling:**
- statsmodels 0.14.6 - Econometric analysis (fixed effects OLS regression)
- lifelines 0.30.0 - Survival analysis (Cox PH, competing risks)
- SciPy 1.16.1 - Statistical tests and distributions
- scikit-learn 1.7.2 - Machine learning utilities (available, future use)

**Testing:**
- pytest 8.0+ - Test runner (configured in `pyproject.toml`)
- pytest-cov - Coverage reporting

**Build/Dev:**
- PyYAML 6.0.2 - Configuration parsing
- openpyxl 3.1.5 - Excel file I/O
- psutil 7.2.1 - System monitoring (memory, CPU, disk)
- python-dateutil 2.9.0.post0 - Date parsing

## Key Dependencies

**Critical:**
- pandas - Data pipeline core (all scripts)
- PyArrow - Parquet storage format (all scripts)
- statsmodels - Step 4 econometric models (`2_Scripts/4_Econometric/4.1_EstimateCeoClarity.py`)
- lifelines - Takeover hazard models (`2_Scripts/4_Econometric/4.3_TakeoverHazards.py`)

**Infrastructure:**
- psutil - Observability features (all scripts via `shared/observability_utils.py`)
- PyYAML - Config loading (`config/project.yaml`)
- RapidFuzz (optional) - Fuzzy entity matching (`2_Scripts/shared/string_matching.py`)

**Data Sources:**
- pandas.read_parquet() - Parquet files via PyArrow engine
- pandas.to_parquet() - Output writing

## Configuration

**Environment:**
- Single config file: `config/project.yaml`
- Centralized settings: paths, seeds, threads, per-step parameters
- No environment variables required for core pipeline
- No .env file usage

**Build:**
- pyproject.toml - pytest configuration
- requirements.txt - Pinned dependencies
- No setup.py or setup.cfg (not a package)
- No Dockerfile or containerization

## Platform Requirements

**Development:**
- Python 3.8+ required
- Git for version control
- 8GB+ RAM recommended (large Parquet files)
- Windows: MSYS/Git Bash for symlink support

**Production:**
- Standalone Python scripts (no web server)
- Local filesystem storage (1_Inputs/, 4_Outputs/)
- No cloud deployment targets
- No API endpoints or web services

---

*Stack analysis: 2026-01-29*
