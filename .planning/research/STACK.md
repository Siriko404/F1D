# Stack: v3.0 Codebase Cleanup & Optimization

**Project:** F1D Data Processing Pipeline
**Research Date:** 2026-02-10
**Milestone:** v3.0 - Codebase Cleanup & Optimization

## Executive Summary

This milestone focuses on codebase health and technical debt reduction, not new features. The existing stack (pandas, numpy, statsmodels, linearmodels, PyArrow, pytest) is fundamentally sound. The cleanup requires minimal new tooling - primarily code quality utilities (Ruff), profiling tools (py-spy), and documentation enhancements.

**Key principle:** Preserve all existing functionality while improving maintainability, performance, and documentation.

---

## 1. Code Quality Tools

| Tool | Version | Purpose | Why for v3.0 |
|------|---------|---------|-------------|
| **Ruff** | 0.9+ | Linter, formatter, import sorter | Replaces Black+isort+flake8. 100x faster. Single config for consistency. |
| **mypy** | 1.15+ | Static type checking | Catch type errors during refactoring. Critical for monolithic utility split. |
| **vulture** | 2.0+ | Dead code finder | Identify unused functions during V1/V2/V3 consolidation. |

### Ruff Configuration

```toml
# pyproject.toml (add to existing)
[tool.ruff]
line-length = 100
target-version = "py38"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "N", "UP", "B", "C4"]
ignore = ["E501"]  # line too long (handled by formatter)

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

**Rationale:** Single tool for all code quality. Reduces configuration complexity. Rust-based for speed on large codebase (61 scripts).

---

## 2. Performance Profiling Tools

| Tool | Purpose | When to Use |
|------|---------|-------------|
| **py-spy** | Sampling profiler (minimal overhead) | Profile running scripts without code changes. |
| **Scalene** | Line-level CPU + memory profiling | Deep dive into memory bottlenecks. |
| **cProfile** (built-in) | Function-level profiling | Quick checks for function call overhead. |

### Profiling Strategy

1. **Baseline:** Profile each major script before optimization
2. **Target:** Top 3 bottlenecks per script
3. **Validate:** After optimization, verify improvement and identical results

**Targeted optimizations:**
- `.apply(lambda)` -> vectorized operations (10-100x speedup)
- `.iterrows()` -> vectorized or `.to_dict('records')` (50-1000x speedup)
- `.groupby().apply()` -> `.groupby().agg()` (5-50x speedup)
- Reduce `pd.concat()` calls by pre-allocating or list-of-dicts pattern

---

## 3. Documentation Tools

| Tool | Purpose | Recommendation |
|------|---------|----------------|
| **Markdown** | Documentation format | RECOMMENDED - Simple, works with existing READMEs |
| **mkdocs-material** | Optional web docs | SKIP - Overkill for single-researcher project |
| **Sphinx** | API documentation | SKIP - API docs unnecessary for research code |

**Rationale:** Academic reviewers need procedural documentation, not API docs. Existing `shared/README.md` (1,500 lines) works well. Extend with per-script docstrings.

### Documentation Structure

```
F1D/
├── README.md                          # Repo-level overview
├── 2_Scripts/
│   ├── shared/
│   │   └── README.md                  # Shared utilities docs
│   ├── 1_Sample/
│   │   └── README.md                  # Stage 1 docs
│   ├── 2_Text/
│   │   └── README.md                  # Stage 2 docs
│   ├── 3_Financial/
│   │   └── README.md                  # Stage 3 V1 docs
│   ├── 3_Financial_V2/
│   │   └── README.md                  # Stage 3 V2 docs (H1-H8)
│   ├── 5_Financial_V3/
│   │   └── README.md                  # Stage 3 V3 docs (H9)
│   ├── 4_Econometric/
│   │   └── README.md                  # Stage 4 V1 docs
│   ├── 4_Econometric_V2/
│   │   └── README.md                  # Stage 4 V2 docs (H1-H9)
│   └── 4_Econometric_V3/
│       └── README.md                  # Stage 4 V3 docs
└── docs/
    └── VARIABLE_CATALOG.md            # All constructed variables
```

---

## 4. Testing & Validation Tools

| Tool | Purpose | Priority |
|------|---------|----------|
| **pytest** (existing) | Test runner | Keep |
| **pytest-cov** | Coverage reporting | ADD - missing from requirements |
| **pandera** | DataFrame schema validation | HIGH - validate parquet schemas at key points |

### Pandera Integration

```python
import pandera as pa
from pandera.typing import Series, DataFrame

# Schema for critical outputs
class MasterManifestSchema(pa.DataFrameModel):
    file_name: Series[str]
    gvkey: Series[str] = pa.Field(nullable=True)
    ceo_id: Series[str]
    start_date: Series[pd.DatetimeTZDtype]
    Total_Words: Series[int] = pa.Field(ge=0)

class ManifestValidation:
    """Validate master sample manifest schema."""
    pass
```

**Why Pandera:** Lightweight (<1MB), native pandas integration, decorator-based validation. Sufficient for research pipeline (not production data engineering).

---

## 5. What NOT to Add

| Tool | Why to Skip |
|------|-------------|
| **Polars** | Pandas 3.0 + vectorization sufficient. Migration = feature creep. |
| **Great Expectations** | Pandera is lighter. GE is production overkill. |
| **Sphinx/MkDocs** | Markdown READMEs sufficient for academic review. |
| **pre-commit** | Git hook complexity for single-user project. |
| **Docker** | Dependency pinning works. Containerization = overkill. |
| **dask/modin** | Datasets fit in memory. Unnecessary complexity. |

---

## 6. Version Updates for v3.0

### Current Stack (from requirements.txt)

```
# Core Data Science
pandas==2.2.3  -> Upgrade to 3.0.x for performance
numpy==2.3.2
scipy>=1.16.1

# Statistical Modeling - Keep pinned
statsmodels==0.14.6  # 0.14.0 had breaking GLM changes
scikit-learn>=1.7.2
lifelines>=0.30.0

# Data Formats
PyYAML>=6.0.2
pyarrow==21.0.0  # 23.0+ requires Python >=3.10
rapidfuzz>=3.14.0

# Utilities
psutil>=7.2.1
python-dateutil>=2.9.0
openpyxl>=3.1.5

# Testing (existing)
pytest
pytest-cov  # ADD
```

### New Additions for v3.0

```
# Code Quality (NEW)
ruff>=0.9.0
mypy>=1.15.0
vulture>=2.0

# Profiling (NEW)
py-spy>=0.3.14  # Optional for optimization

# Testing (NEW)
pandera>=0.21.0
```

---

## 7. Refactoring Strategy

### Splitting `observability_utils.py` (4,652 lines)

**Target structure:**
```
shared/
├── observability/
│   ├── __init__.py              # Re-exports for backward compatibility
│   ├── logging.py               # DualWriter class
│   ├── stats.py                 # print_stat, analyze_missing_values
│   ├── files.py                 # compute_file_checksum
│   ├── memory.py                # get_process_memory_mb
│   ├── throughput.py            # calculate_throughput
│   └── anomalies.py             # detect_anomalies_zscore/iqr
```

**Backward compatibility:**
```python
# __init__.py re-exports all public API
from .logging import DualWriter
from .stats import print_stat, analyze_missing_values
# ... etc

# Old imports still work:
# from shared.observability_utils import DualWriter  # Still valid
```

---

## 8. Implementation Priority

### Phase 1: Code Quality Setup
1. Configure Ruff in pyproject.toml
2. Run Ruff on entire codebase, auto-fix issues
3. Add mypy to shared utilities (progressive rollout)

### Phase 2: Performance Profiling
1. Profile top 5 scripts with py-spy
2. Identify bottlenecks
3. Vectorize targeted operations
4. Verify identical outputs

### Phase 3: Refactoring
1. Split observability_utils.py
2. Update imports across all scripts
3. Archive backup files
4. Clarify V1/V2/V3 directory documentation

### Phase 4: Documentation
1. Write repo-level README
2. Write script-level docstrings (61 scripts)
3. Write directory READMEs
4. Create variable catalog

---

## Sources

- Ruff documentation: https://docs.astral.sh/ruff/
- Pandera documentation: https://pandera.readthedocs.io/
- py-spy GitHub: https://github.com/benfred/py-spy
- Pandas 3.0 release notes: https://pandas.pydata.org/docs/whatsnew/v3.0.0.html

---

*Stack research: 2026-02-10*
