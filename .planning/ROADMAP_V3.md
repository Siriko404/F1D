# Roadmap: v3.0 Codebase Cleanup & Optimization

## Overview

This roadmap defines the v3.0 milestone for the F1D Data Processing Pipeline. Unlike previous milestones which focused on new features and hypothesis testing, v3.0 is a **cleanup and optimization milestone**. The pipeline is functional (all 9 hypotheses tested, null results validated) but suffers from accumulated technical debt, organizational issues, and documentation gaps.

**Milestone:** v3.0 Codebase Cleanup & Optimization
**Start Date:** 2026-02-10
**Phases:** 5 phases (59-63)
**Requirements:** 55 requirements across bug fixes, organization, documentation, performance, and testing

**v3.0 Summary:** Fix critical bugs, improve code organization, add comprehensive documentation, optimize performance, and enhance testing while preserving **all existing functionality** and **bitwise-identical reproducibility**.

---

## v3.0 Phases (59-63)

### Phase 59: Critical Bug Fixes

**Goal:** Fix known bugs that affect data quality and error reporting

**Depends on:** Phase 58 (H9 complete)

**Requirements:** BUG-01 through BUG-03 (10 requirements)

#### Phase 59-01: H7-H8 Data Truncation Resolution

**Goal:** Fix H8 silent data truncation bug where only 2002-2004 data is used instead of full 2002-2018

**Requirements:** BUG-01-01, BUG-01-02, BUG-01-03, BUG-01-04

**Success Criteria:**
1. Volatility calculated directly from CRSP daily returns within H7 script
2. H8 sample verified to include full 2002-2018 period (39,408 observations)
3. Regression test created to prevent recurrence
4. Volatility calculation methodology documented

**Files modified:**
- `2_Scripts/3_Financial_V2/3.7_H7IlliquidityVariables.py`
- `2_Scripts/3_Financial_V2/3.8_H8TakeoverVariables.py`

**Output:** H8 dataset with full 2002-2018 coverage

#### Phase 59-02: Empty DataFrame Returns Fix

**Goal:** Replace silent empty returns with informative exceptions

**Requirements:** BUG-02-01, BUG-02-02, BUG-02-03, BUG-02-04

**Success Criteria:**
1. All functions returning empty containers audited
2. Empty returns replaced with exceptions in V2 scripts
3. Error handling in shared/financial_utils.py updated
4. Integration test validates error propagation

**Files modified:**
- `2_Scripts/shared/financial_utils.py`
- All `2_Scripts/3_Financial_V2/*.py` scripts
- `2_Scripts/4_Econometric_V2/*.py` scripts

#### Phase 59-03: Division by Zero Resolution

**Goal:** Fix silent masking of data quality issues in transcript timestamp calculations

**Requirements:** BUG-03-01, BUG-03-02, BUG-03-03

**Success Criteria:**
1. Functions returning 0.0 for invalid durations identified
2. Silent masking replaced with logging + exceptions
3. Root cause in timestamp calculations fixed
4. No regressions in transcript processing

**Files modified:**
- `2_Scripts/2_Text/2.1_TokenizeAndCount.py`
- `2_Scripts/2_Text/2.2_ConstructVariables.py`

---

### Phase 60: Code Organization

**Goal:** Clean up file clutter and improve code structure

**Depends on:** Phase 59 (bugs fixed)

**Requirements:** ORG-01 through ORG-04 (15 requirements)

#### Phase 60-01: Archive Backup Files

**Goal:** Move backup and legacy files to archive directory

**Requirements:** ORG-01-01 through ORG-01-05

**Success Criteria:**
1. All `*-legacy.py` files moved to `.___archive/legacy/`
2. All `*.bak` files moved to `.___archive/backups/`
3. All `*_old.py` files moved to `.___archive/old_versions/`
4. README created in `.___archive/` explaining contents
5. No active scripts reference archived files

**Files affected:**
- `2_Scripts/1_Sample/1.0_BuildSampleManifest-legacy.py`
- `2_Scripts/3_Financial_V2/3.7_H7IlliquidityVariables.py.bak`
- Any other `*_backup.py`, `*_old.py`, `*~` files

#### Phase 60-02: Version Structure Clarification

**Goal:** Document V1/V2/V3 directory purposes through README files

**Requirements:** ORG-02-01 through ORG-02-09

**Success Criteria:**
1. README.md created in `2_Scripts/3_Financial/` (V1: Original financial variables)
2. README.md created in `2_Scripts/3_Financial_V2/` (V2: H1-H8 hypothesis variables)
3. README.md created in `2_Scripts/5_Financial_V3/` (V3: H9 advanced variables)
4. README.md created in `2_Scripts/4_Econometric/` (V1: Original regressions)
5. README.md created in `2_Scripts/4_Econometric_V2/` (V2: H1-H9 regressions)
6. README.md created in `2_Scripts/4_Econometric_V3/` (V3: Advanced regressions)
7. README.md created in `2_Scripts/shared/` (Shared utilities)
8. README.md created in `2_Scripts/1_Sample/` (Sample construction)
9. README.md created in `2_Scripts/2_Text/` (Text processing)

**Key Point:** Clarification through documentation, NOT renaming active directories

#### Phase 60-03: Split Monolithic Utilities

**Goal:** Split 4,652-line observability_utils.py into focused modules

**Requirements:** ORG-03-01 through ORG-03-10

**Success Criteria:**
1. `shared/observability/` package created with submodules:
   - `logging.py` (DualWriter, ~500 lines)
   - `stats.py` (print_stat, analyze_missing_values, ~800 lines)
   - `files.py` (compute_file_checksum, ~200 lines)
   - `memory.py` (get_process_memory_mb, ~150 lines)
   - `throughput.py` (calculate_throughput, ~300 lines)
   - `anomalies.py` (detect_anomalies_zscore/iqr, ~400 lines)
2. `__init__.py` created with backward-compatible re-exports
3. All 61 scripts updated to use new imports
4. Old imports still work via re-exports
5. Full pipeline run verifies backward compatibility

**Files created:**
- `shared/observability/__init__.py`
- `shared/observability/logging.py`
- `shared/observability/stats.py`
- `shared/observability/files.py`
- `shared/observability/memory.py`
- `shared/observability/throughput.py`
- `shared/observability/anomalies.py`

**Files modified:**
- All 61 pipeline scripts (import updates)

#### Phase 60-04: Code Quality Setup

**Goal:** Set up code quality tools and identify improvement areas

**Requirements:** ORG-04-01 through ORG-04-05

**Success Criteria:**
1. Ruff configured in pyproject.toml
2. Ruff run on entire codebase with auto-fixes
3. Mypy added to shared utilities
4. Vulture run to identify dead code
5. Code quality findings documented

**Files created:**
- `pyproject.toml` (updated with Ruff config)

---

### Phase 61: Documentation

**Goal:** Create comprehensive documentation for academic reviewers

**Depends on:** Phase 60 (structure clarified)

**Requirements:** DOC-01 through DOC-03 (13 requirements)

#### Phase 61-01: Repository-Level README

**Goal:** Create comprehensive project overview README

**Requirements:** DOC-01-01 through DOC-01-08

**Success Criteria:**
1. README.md created in project root with:
   - Project overview and purpose
   - Installation and setup instructions
   - Quick start guide
   - Directory structure explanation
   - Data sources and availability statement
   - Computational requirements
   - Reference to thesis/paper

**Files created:**
- `README.md` (root level, comprehensive)

#### Phase 61-02: Script-Level Docstrings

**Goal:** Add standardized headers to all 61 pipeline scripts

**Requirements:** DOC-02-01 through DOC-02-05

**Success Criteria:**
1. Standardized header added to all scripts
2. Each header includes: Purpose, Inputs, Outputs, Dependencies
3. Each header includes: Deterministic flag, Author/Date
4. All scripts follow same format
5. Module docstrings added to shared utilities

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

**Files modified:**
- All 61 pipeline scripts
- All shared utility modules

#### Phase 61-03: Variable Catalog

**Goal:** Create comprehensive reference for all constructed variables

**Requirements:** DOC-03-01 through DOC-03-07

**Success Criteria:**
1. `docs/VARIABLE_CATALOG.md` created
2. Sample variables cataloged (file_name, gvkey, ceo_id, tenure)
3. Text variables cataloged (uncertainty measures, tone, word counts)
4. Financial variables cataloged (V1 controls, V2 H1-H8, V3 H9)
5. Econometric outputs cataloged (ClarityCEO, regression results)
6. Formulas and source fields included
7. Search capability added (alphabetical and category indices)

**Files created:**
- `docs/VARIABLE_CATALOG.md`

---

### Phase 62: Performance Optimization

**Goal:** Improve script performance through vectorization and anti-pattern elimination

**Depends on:** Phase 60 (structure stable)

**Requirements:** PERF-01 through PERF-03 (8 requirements)

#### Phase 62-01: Vectorization Implementation

**Goal:** Replace slow `.apply(lambda)` with vectorized operations

**Requirements:** PERF-01-01 through PERF-01-05

**Success Criteria:**
1. Scripts profiled with py-spy to identify bottlenecks
2. `.apply(lambda)` replaced in `2.1_TokenizeAndCount.py`
3. `.apply(lambda)` replaced in `3.2_MarketVariables.py`
4. Bitwise-identical outputs verified
5. Speedup documented

**Files modified:**
- `2_Scripts/2_Text/2.1_TokenizeAndCount.py`
- `2_Scripts/3_Financial/3.2_MarketVariables.py`

#### Phase 62-02: Iterrows Elimination

**Goal:** Replace `.iterrows()` with vectorized alternatives

**Requirements:** PERF-02-01 through PERF-02-04

**Success Criteria:**
1. `.iterrows()` replaced in `1.3_BuildTenureMap.py`
2. `.iterrows()` replaced in `shared/financial_utils.py`
3. Bitwise-identical outputs verified
4. Speedup documented

**Files modified:**
- `2_Scripts/1_Sample/1.3_BuildTenureMap.py`
- `2_Scripts/shared/financial_utils.py`

#### Phase 62-03: GroupBy Optimization

**Goal:** Optimize `.groupby().apply()` calls

**Requirements:** PERF-03-01 through PERF-03-04

**Success Criteria:**
1. `.groupby().apply()` replaced with `.groupby().agg()` where applicable
2. Rolling window calculations optimized in `3.2_H2Variables.py`
3. Bitwise-identical outputs verified
4. Speedup documented

**Files modified:**
- `2_Scripts/3_Financial_V2/3.2_H2Variables.py`

---

### Phase 63: Testing & Validation

**Goal:** Ensure all changes preserve reproducibility and catch regressions

**Depends on:** All previous phases

**Requirements:** TEST-01 through TEST-03 (9 requirements)

#### Phase 63-01: Regression Tests

**Goal:** Add tests to prevent bug recurrence and verify bitwise-identical outputs

**Requirements:** TEST-01-01 through TEST-01-04

**Success Criteria:**
1. H7-H8 regression test created
2. Bitwise comparison tests for critical outputs
3. Integration tests for multi-step workflows
4. Full pipeline end-to-end run verified

**Files created:**
- `tests/regression/test_h7_h8_data_truncation.py`

#### Phase 63-02: Schema Validation

**Goal:** Add Pandera schema validation for critical datasets

**Requirements:** TEST-02-01 through TEST-02-03

**Success Criteria:**
1. Pandera schemas added for critical parquet outputs
2. Schema validation added to key merge operations
3. Schema validation approach documented

**Files created:**
- `tests/schemas/` (schema definitions)

#### Phase 63-03: Coverage Expansion

**Goal:** Improve test coverage on shared utilities

**Requirements:** TEST-03-01 through TEST-03-03

**Success Criteria:**
1. Current coverage measured
2. 70% coverage achieved on shared utilities
3. Coverage report documented

**Files created:**
- `tests/coverage/.coverage` (coverage reports)

---

## Progress Tracking

| Phase | Name | Requirements | Success Criteria | Status |
|-------|------|-------------|------------------|--------|
| 59 | Critical Bug Fixes | BUG-01 through BUG-03 (10) | 4 per sub-phase | COMPLETE |
| 60 | Code Organization | ORG-01 through ORG-04 (15) | 5 per sub-phase | TBD |
| 61 | Documentation | DOC-01 through DOC-03 (13) | 3-8 per sub-phase | TBD |
| 62 | Performance Optimization | PERF-01 through PERF-03 (8) | 4-5 per sub-phase | TBD |
| 63 | Testing & Validation | TEST-01 through TEST-03 (9) | 3-4 per sub-phase | TBD |

---

## Requirements Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| BUG-01-01 through BUG-01-04 | 59-01 | COMPLETE |
| BUG-02-01 through BUG-02-04 | 59-02 | COMPLETE |
| BUG-03-01 through BUG-03-03 | 59-03 | COMPLETE |
| ORG-01-01 through ORG-01-05 | 60-01 | Pending |
| ORG-02-01 through ORG-02-09 | 60-02 | Pending |
| ORG-03-01 through ORG-03-10 | 60-03 | Pending |
| ORG-04-01 through ORG-04-05 | 60-04 | Pending |
| DOC-01-01 through DOC-01-08 | 61-01 | Pending |
| DOC-02-01 through DOC-02-05 | 61-02 | Pending |
| DOC-03-01 through DOC-03-07 | 61-03 | Pending |
| PERF-01-01 through PERF-01-05 | 62-01 | Pending |
| PERF-02-01 through PERF-02-04 | 62-02 | Pending |
| PERF-03-01 through PERF-03-04 | 62-03 | Pending |
| TEST-01-01 through TEST-01-04 | 63-01 | Pending |
| TEST-02-01 through TEST-02-03 | 63-02 | Pending |
| TEST-03-01 through TEST-03-03 | 63-03 | Pending |

**Coverage:** 55/55 requirements mapped to phases (100%)

---

## Milestone Completion Criteria

v3.0 milestone is complete when:

1. [x] All critical bugs fixed (H7-H8 data truncation resolved, empty returns fixed)
2. [ ] Backup files archived, V1/V2/V3 structure documented
3. [ ] Monolithic utilities split with backward compatibility
4. [ ] Comprehensive documentation (repo README, script docstrings, variable catalog)
5. [ ] Performance optimizations applied with verified identical outputs
6. [ ] Testing enhanced (regression tests, coverage improved)
7. [ ] Full pipeline runs end-to-end with bitwise-identical outputs

---

*Roadmap created: 2026-02-10*
*v3.0 roadmap: 5 phases, 55 requirements*
