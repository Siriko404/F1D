# Requirements: F1D Codebase Cleanup & Optimization

**Defined:** 2026-02-10
**Core Value:** Every cleanup change must preserve bitwise-identical outputs — reproducibility is non-negotiable
**Status:** Active — Defining requirements for v3.0 milestone

## v3.0 Requirements

Requirements for codebase cleanup and optimization milestone. V3 focuses on technical debt reduction, documentation, and code quality while preserving all existing functionality.

**Key Constraints:**
- **NO active code is archived** — All V1/V2/V3 scripts remain functional
- **Bitwise-identical outputs** — All changes must produce exact same results
- **Backward compatibility** — Old import paths must continue to work during transition

---

## Critical Bug Fixes

### BUG-01: H7-H8 Data Truncation — HIGH PRIORITY

- [ ] **BUG-01-01**: Calculate Volatility directly from CRSP daily returns within H7 script instead of relying on incomplete market_variables files
- [ ] **BUG-01-02**: Verify H8 sample includes full 2002-2018 period (39,408 observations, not 12,408)
- [ ] **BUG-01-03**: Add regression test to prevent recurrence of data truncation bug
- [ ] **BUG-01-04**: Document Volatility calculation methodology in code comments

**Current Issue:** Volatility and StockRet control variables are 100% missing for 2005-2018 in H7_Illiquidity.parquet, causing H8 to silently truncate to 2002-2004.

### BUG-02: Empty DataFrame Returns — HIGH PRIORITY

- [ ] **BUG-02-01**: Audit all functions returning empty dicts/None/DataFrames on error paths
- [ ] **BUG-02-02**: Replace empty returns with informative exceptions (include context about what failed)
- [ ] **BUG-02-03**: Update error handling in shared/financial_utils.py and all V2 scripts
- [ ] **BUG-02-04**: Add integration test that error messages propagate correctly

**Current Issue:** 100+ functions return empty containers on error, hiding useful debugging information.

### BUG-03: Division by Zero Guards — MEDIUM PRIORITY

- [ ] **BUG-03-01**: Identify all functions returning 0.0 for duration_seconds <= 0
- [ ] **BUG-03-02**: Replace silent masking with explicit logging + informative exceptions
- [ ] **BUG-03-03**: Fix root cause in transcript timestamp calculations (2.1_TokenizeAndCount.py, 2.2_ConstructVariables.py)

**Current Issue:** Graceful degradation to 0.0 masks underlying data quality issues with transcript timestamps.

---

## Code Organization

### ORG-01: Archive Backup Files — HIGH PRIORITY

- [ ] **ORG-01-01**: Move all `*-legacy.py` files to `.___archive/legacy/`
- [ ] **ORG-01-02**: Move all `*.bak` files to `.___archive/backups/`
- [ ] **ORG-01-03**: Move all `*_old.py` files to `.___archive/old_versions/`
- [ ] **ORG-01-04**: Create README in `.___archive/` explaining archived contents
- [ ] **ORG-01-05**: Verify no active scripts reference archived files

**Files affected:**
- `2_Scripts/1_Sample/1.0_BuildSampleManifest-legacy.py`
- `2_Scripts/3_Financial_V2/3.7_H7IlliquidityVariables.py.bak`
- Any other `*_backup.py`, `*_old.py`, `*~` files

### ORG-02: Clarify V1/V2/V3 Structure — HIGH PRIORITY

- [ ] **ORG-02-01**: Create README.md in `2_Scripts/3_Financial/` explaining V1 purpose
- [ ] **ORG-02-02**: Create README.md in `2_Scripts/3_Financial_V2/` explaining V2 purpose (H1-H8)
- [ ] **ORG-02-03**: Create README.md in `2_Scripts/5_Financial_V3/` explaining V3 purpose (H9)
- [ ] **ORG-02-04**: Create README.md in `2_Scripts/4_Econometric/` explaining V1 purpose
- [ ] **ORG-02-05**: Create README.md in `2_Scripts/4_Econometric_V2/` explaining V2 purpose
- [ ] **ORG-02-06**: Create README.md in `2_Scripts/4_Econometric_V3/` explaining V3 purpose
- [ ] **ORG-02-07**: Create README.md in `2_Scripts/shared/` explaining shared utilities
- [ ] **ORG-02-08**: Create README.md in `2_Scripts/1_Sample/` explaining sample construction
- [ ] **ORG-02-09**: Create README.md in `2_Scripts/2_Text/` explaining text processing

**Key Point:** Clarification through documentation, NOT renaming or consolidating active directories.

### ORG-03: Split Monolithic Utilities — MEDIUM PRIORITY

- [ ] **ORG-03-01**: Create `shared/observability/` package directory
- [ ] **ORG-03-02**: Extract DualWriter and logging code to `shared/observability/logging.py` (~500 lines)
- [ ] **ORG-03-03**: Extract stats functions to `shared/observability/stats.py` (~800 lines)
- [ ] **ORG-03-04**: Extract file utilities to `shared/observability/files.py` (~200 lines)
- [ ] **ORG-03-05**: Extract memory utilities to `shared/observability/memory.py` (~150 lines)
- [ ] **ORG-03-06**: Extract throughput utilities to `shared/observability/throughput.py` (~300 lines)
- [ ] **ORG-03-07**: Extract anomaly detection to `shared/observability/anomalies.py` (~400 lines)
- [ ] **ORG-03-08**: Create `shared/observability/__init__.py` with re-exports for backward compatibility
- [ ] **ORG-03-09**: Update all 61 scripts to use new imports (old imports still work via re-export)
- [ ] **ORG-03-10**: Run full pipeline to verify backward compatibility

**Backward compatibility preserved:**
```python
# Old import (still works):
from shared.observability_utils import DualWriter

# New import (preferred):
from shared.observability import DualWriter
```

### ORG-04: Code Quality Setup — MEDIUM PRIORITY

- [ ] **ORG-04-01**: Install and configure Ruff in pyproject.toml
- [ ] **ORG-04-02**: Run Ruff on entire codebase and auto-fix issues
- [ ] **ORG-04-03**: Add mypy to shared utilities (progressive rollout)
- [ ] **ORG-04-04**: Run vulture to identify dead code
- [ ] **ORG-04-05**: Document code quality findings in report

---

## Documentation

### DOC-01: Repository-Level README — HIGH PRIORITY

- [ ] **DOC-01-01**: Create comprehensive README.md in project root
- [ ] **DOC-01-02**: Include project overview and purpose
- [ ] **DOC-01-03**: Include installation and setup instructions
- [ ] **DOC-01-04**: Include quick start guide for running pipeline
- [ ] **DOC-01-05**: Include directory structure explanation
- [ ] **DOC-01-06**: Include data sources and availability statement
- [ ] **DOC-01-07**: Include computational requirements (Python version, RAM, runtime)
- [ ] **DOC-01-08**: Include reference to thesis/paper if applicable

### DOC-02: Script-Level Docstrings — HIGH PRIORITY

- [ ] **DOC-02-01**: Add standardized header to all 61 pipeline scripts
- [ ] **DOC-02-02**: Each script header includes: Purpose, Inputs, Outputs, Dependencies
- [ ] **DOC-02-03**: Each script header includes: Deterministic flag, Author/Date
- [ ] **DOC-02-04**: Verify all scripts follow same header format
- [ ] **DOC-02-05**: Add module-level docstrings to shared utility modules

**Template:**
```python
#!/usr/bin/env python3
"""
STEP X.Y: {Script Name}
===============================================================================

Purpose:
    {One-sentence description}

Inputs:
    - 4_Outputs/{PreviousStep}/latest/{file1.parquet}
    - 4_Outputs/{PreviousStep}/latest/{file2.parquet}

Outputs:
    - 4_Outputs/{CurrentStep}/{timestamp}/{output.parquet}
    - stats.json
    - {timestamp}.log

Dependencies:
    - Requires Step X.{Y-1}
    - Uses: shared.module1, shared.module2

Deterministic: true
==============================================================================
"""
```

### DOC-03: Variable Catalog — MEDIUM PRIORITY

- [ ] **DOC-03-01**: Create `docs/VARIABLE_CATALOG.md` with all constructed variables
- [ ] **DOC-03-02**: Catalog Sample variables (file_name, gvkey, ceo_id, tenure, etc.)
- [ ] **DOC-03-03**: Catalog Text variables (uncertainty measures, tone, word counts)
- [ ] **DOC-03-04**: Catalog Financial variables (V1 controls, V2 hypothesis variables, V3 H9 variables)
- [ ] **DOC-03-05**: Catalog Econometric outputs (ClarityCEO, regression results)
- [ ] **DOC-03-06**: Include formulas, source data fields, and construction methodology
- [ ] **DOC-03-07**: Add search capability (alphabetical index, category index)

---

## Performance Optimization

### PERF-01: Vectorization — MEDIUM PRIORITY

- [ ] **PERF-01-01**: Profile scripts with py-spy to identify `.apply(lambda)` bottlenecks
- [ ] **PERF-01-02**: Replace `.apply(lambda)` with vectorized operations in `2.1_TokenizeAndCount.py`
- [ ] **PERF-01-03**: Replace `.apply(lambda)` with vectorized operations in `3.2_MarketVariables.py`
- [ ] **PERF-01-04**: Verify bitwise identical outputs after vectorization
- [ ] **PERF-01-05**: Document speedup improvements

### PERF-02: Eliminate Iterrows — MEDIUM PRIORITY

- [ ] **PERF-02-01**: Replace `.iterrows()` in `1.3_BuildTenureMap.py` with vectorized alternative
- [ ] **PERF-02-02**: Replace `.iterrows()` in `shared/financial_utils.py` with vectorized alternative
- [ ] **PERF-02-03**: Verify bitwise identical outputs after replacement
- [ ] **PERF-02-04**: Document speedup improvements

### PERF-03: Optimize GroupBy — LOW PRIORITY

- [ ] **PERF-03-01**: Replace `.groupby().apply()` with `.groupby().agg()` where applicable
- [ ] **PERF-03-02**: Optimize rolling window calculations in `3.2_H2Variables.py`
- [ ] **PERF-03-03**: Verify bitwise identical outputs after optimization
- [ ] **PERF-03-04**: Document speedup improvements

---

## Testing & Validation

### TEST-01: Regression Tests — HIGH PRIORITY

- [ ] **TEST-01-01**: Create regression test for H7-H8 data truncation bug
- [ ] **TEST-01-02**: Add bitwise comparison tests for critical outputs before/after cleanup
- [ ] **TEST-01-03**: Create integration tests for multi-step workflows
- [ ] **TEST-01-04**: Run full pipeline end-to-end and verify outputs

### TEST-02: Schema Validation — LOW PRIORITY

- [ ] **TEST-02-01**: Add Pandera schemas for critical parquet outputs (master manifest, H1-H8 datasets)
- [ ] **TEST-02-02**: Add schema validation to key merge operations
- [ ] **TEST-02-03**: Document schema validation approach

### TEST-03: Coverage Expansion — LOW PRIORITY

- [ ] **TEST-03-01**: Measure current test coverage on shared utilities
- [ ] **TEST-03-02**: Target 70% coverage on shared utilities (add tests if needed)
- [ ] **TEST-03-03**: Document coverage report

---

## Out of Scope

Explicitly excluded from v3.0 cleanup:

| Feature | Reason |
|---------|--------|
| Renaming active directories | V1/V2/V3 clarification through docs only |
| Consolidating V1/V2/V3 | All versions serve different legitimate purposes |
| Polars migration | Pandas 3.0 + vectorization sufficient |
| Sphinx/MkDocs documentation | Markdown READMEs sufficient for academic review |
| Docker containerization | Unnecessary for single-researcher project |
| Great Expectations | Pandera is lighter, sufficient for research |

---

## Traceability

Requirements mapped to phases in ROADMAP_V3.md.

| Requirement Category | Requirements | Phase |
|---------------------|--------------|-------|
| BUG-01 through BUG-03 | Critical bug fixes | 59 |
| ORG-01 through ORG-04 | Code organization | 60 |
| DOC-01 through DOC-03 | Documentation | 61 |
| PERF-01 through PERF-03 | Performance optimization | 62 |
| TEST-01 through TEST-03 | Testing & validation | 63 |

**Total Requirements:** 55 (100% mapped to phases)

---

*Requirements defined: 2026-02-10*
*Last updated: 2026-02-10 (roadmap created)*
