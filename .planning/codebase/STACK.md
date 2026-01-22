# Technology Stack

**Analysis Date:** 2026-01-22

## Languages

**Primary:**
- Python 3.x - Used for all data processing, econometric analysis, and orchestration scripts.

**Secondary:**
- C++ (C++17) - Used for high-performance tokenization (configured in `config/project.yaml` step_03).

## Runtime

**Environment:**
- Python 3.x Environment
- C++ Compiler (`g++` or similar supporting C++17)

**Package Manager:**
- Standard Python `pip` (inferred, no lockfile detected in root)
- No lockfile present in root

## Frameworks

**Core:**
- None - The project uses standalone Python scripts orchestrated via a configuration file.

**Testing:**
- None detected - Verification scripts exist (e.g., `2.3_VerifyStep2.py`), but no standard framework like `pytest` or `unittest` is explicitly configured.

**Build/Dev:**
- `g++` - For compiling C++ tokenization components.

## Key Dependencies

**Critical:**
- `pandas` - Core data manipulation and Parquet I/O.
- `numpy` - Numerical computations.
- `statsmodels` - Econometric models and regression analysis.
- `linearmodels` - Advanced econometric models (IV/2SLS).
- `lifelines` - Survival analysis (CoxPHFitter).
- `rapidfuzz` - Fuzzy string matching for entity linking.
- `pyyaml` - Parsing `config/project.yaml`.

**Infrastructure:**
- `pyarrow` - Implicit dependency for Parquet file handling via pandas.
- `matplotlib` - Visualization and plotting.

## Configuration

**Environment:**
- `config/project.yaml` - Central source of truth for paths, parameters, and execution flags.
- `CLAUDE.md` - Developer instructions and project philosophy.

**Build:**
- C++ compiler flags defined in `config/project.yaml` (Step 03).

## Platform Requirements

**Development:**
- Python 3 environment with data science libraries.
- C++ compiler.
- Sufficient RAM for processing large Parquet datasets.

**Production:**
- Same as development (local execution model).

---

*Stack analysis: 2026-01-22*
