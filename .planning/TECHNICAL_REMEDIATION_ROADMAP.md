# Technical Remediation Roadmap

## Overview

This roadmap addresses all documented technical concerns in CONCERNS.md through systematic remediation phases. While the original project (Phases 1-6) met all functional requirements for thesis submission, this work ensures long-term maintainability, security, performance, and developer experience.

**Concerns Summary:**
- 4 Tech Debt items
- 2 Known Bugs
- 3 Security Considerations
- 4 Performance Bottlenecks
- 4 Fragile Areas
- 3 Scaling Limits
- 4 Dependencies at Risk
- 5 Missing Critical Features
- 5 Test Coverage Gaps

**Total: 34 concerns across 8 categories**

## Phases

**Phase Numbering:**
- **Phase 7**: Critical Bug Fixes (2 concerns) - MUST DO before any other work
- **Phase 8**: Tech Debt Cleanup (4 concerns) - HIGH priority for maintainability
- **Phase 9**: Security Hardening (3 concerns) - MEDIUM-HIGH priority for security
- **Phase 10**: Performance Optimization (4 concerns) - MEDIUM priority
- **Phase 11**: Testing Infrastructure (9 concerns) - HIGH priority for quality
- **Phase 12**: Data Quality & Observability (3 concerns) - LOW-MEDIUM priority
- **Phase 13**: Script Refactoring (5 concerns) - LOW priority (deferred)

---

## Phase 7: Critical Bug Fixes

**Goal**: Fix silent failures that could cause data corruption or incorrect results

**Depends on**: Nothing (first priority)

**Success Criteria**:
1. Symlink/copy failures log explicit errors and exit with non-zero code
2. rapidsuzz dependency clearly documented with installation instructions
3. Users are warned when optional dependencies are missing

**Concerns Addressed**:
- ✅ Silent Failures in Symlink Operations (Known Bugs #1)
- ✅ Optional Dependency Not Handled Gracefully (Known Bugs #2)

**Plans**:
- [ ] **07-01-PLAN.md**: Fix update_latest_symlink() silent failures
- [ ] **07-02-PLAN.md**: Document and handle rapidsuzz optional dependency

---

## Phase 8: Tech Debt Cleanup

**Goal**: Eliminate code duplication and improve maintainability

**Depends on**: Phase 7

**Success Criteria**:
1. DualWriter class extracted to shared module (2_Scripts/shared/dual_writer.py)
2. Utility functions consolidated (compute_file_checksum, print_stat, analyze_missing_values, update_latest_symlink)
3. All scripts import from shared modules (no duplicate code)
4. Error handling improved (specific exceptions, logging, re-raise or graceful handling)

**Concerns Addressed**:
- ✅ Code Duplication - DualWriter Class (Tech Debt #1)
- ✅ Code Duplication - Utility Functions (Tech Debt #2)
- ✅ Inconsistent Error Handling (Tech Debt #4)

**Plans**:
- [ ] **08-01-PLAN.md**: Extract DualWriter to shared module
- [ ] **08-02-PLAN.md**: Consolidate utility functions to shared module
- [ ] **08-03-PLAN.md**: Update all scripts to import shared modules
- [ ] **08-04-PLAN.md**: Improve error handling consistency across all scripts

---

## Phase 9: Security Hardening

**Goal**: Address security vulnerabilities and prevent future issues

**Depends on**: Phase 8 (requires shared module structure)

**Success Criteria**:
1. All subprocess paths validated (within expected directory, absolute paths)
2. Environment variable schema validation implemented (if env vars added)
3. Input data validation layer with column type and value range checks

**Concerns Addressed**:
- ✅ Subprocess Execution Without Validation (Security #1)
- ✅ No Environment Variable Validation (Security #2)
- ✅ Missing Input Data Validation (Security #3)

**Plans**:
- [ ] **09-01-PLAN.md**: Add subprocess path validation
- [ ] **09-02-PLAN.md**: Implement environment variable validation
- [ ] **09-03-PLAN.md**: Add input data schema validation layer

---

## Phase 10: Performance Optimization

**Goal**: Improve processing speed and reduce resource usage

**Depends on**: Phase 8 (requires refactored modules)

**Success Criteria**:
1. All .iterrows() replaced with vectorized operations or .itertuples()
2. Year loops use parallelization with ProcessPoolExecutor (respect thread_count config)
3. Large Parquet files use PyArrow dataset API for streaming or chunked processing
4. Repeated file reads use caching or lazy loading with duckdb/pyarrow

**Concerns Addressed**:
- ✅ Inefficient DataFrame Iteration (Performance #1)
- ✅ Sequential Processing of Years (Performance #2)
- ✅ Memory-Intensive Operations (Performance #3)
- ✅ Repeated Data Loading (Performance #4)

**Plans**:
- [ ] **10-01-PLAN.md**: Replace iterrows() with vectorized operations
- [ ] **10-02-PLAN.md**: Add parallelization for year loops
- [ ] **10-03-PLAN.md**: Implement chunked processing for large files
- [ ] **10-04-PLAN.md**: Add caching for repeated data loads

---

## Phase 11: Testing Infrastructure

**Goal**: Establish comprehensive testing framework to prevent regressions

**Depends on**: Phase 8 (requires shared modules for testability)

**Success Criteria**:
1. pytest framework configured with test discovery
2. Unit tests for key functions (fuzzy matching, tenure calculation, regression models)
3. Integration tests for end-to-end pipeline execution
4. Regression tests validating output stability
5. Data validation tests for input schemas
6. Edge case tests (empty datasets, single rows, all-null columns, duplicate keys)
7. All tests pass in CI/CD or manual test runs

**Concerns Addressed**:
- ✅ No Automated Testing (Missing Features #1)
- ✅ Missing Unit Tests (Test Coverage #1)
- ✅ Missing Integration Tests (Test Coverage #2)
- ✅ Missing Regression Tests (Test Coverage #3)
- ✅ Missing Data Validation Tests (Test Coverage #4)
- ✅ Missing Edge Case Tests (Test Coverage #5)

**Plans**:
- [ ] **11-01-PLAN.md**: Set up pytest framework and test structure
- [ ] **11-02-PLAN.md**: Add unit tests for key functions
- [ ] **11-03-PLAN.md**: Add integration tests for pipeline
- [ ] **11-04-PLAN.md**: Add regression tests for output stability
- [ ] **11-05-PLAN.md**: Add data validation tests
- [ ] **11-06-PLAN.md**: Add edge case tests
- [ ] **11-07-PLAN.md**: Configure CI/CD (if applicable)

---

## Phase 12: Data Quality & Observability

**Goal**: Add monitoring and quality checks to detect issues early

**Depends on**: Phase 11 (requires testing framework)

**Success Criteria**:
1. Data quality reports generated (outliers, distributions, consistency checks)
2. Pipeline state tracking implemented (which steps completed successfully)
3. Configuration validation implemented (config/project.yaml schema validation)
4. Quality alerts generated for anomalies

**Concerns Addressed**:
- ✅ No Data Quality Reports (Missing Features #3)
- ✅ No Pipeline State Tracking (Missing Features #4)
- ✅ No Configuration Validation (Missing Features #5)

**Plans**:
- [ ] **12-01-PLAN.md**: Add data quality reporting
- [ ] **12-02-PLAN.md**: Implement pipeline state tracking
- [ ] **12-03-PLAN.md**: Add configuration schema validation

---

## Phase 13: Script Refactoring

**Goal**: Improve code organization and reduce cognitive load

**Depends on**: Phase 10 (performance improvements first, then refactor)

**Success Criteria**:
1. Large scripts (800+ lines) broken into smaller focused modules
2. Each module has single responsibility
3. Fragile areas identified and made more robust
4. Output path dependencies validated before use
5. Data assumptions for regression validated
6. String matching logic parameterized in config
7. Windows symlink fallback improved (use junctions, add warnings)

**Concerns Addressed**:
- ✅ Large Script Files (Tech Debt #3)
- ✅ Output Path Dependencies (Fragile Areas #1)
- ✅ Data Assumptions - Fixed Effects Regression (Fragile Areas #2)
- ✅ String Matching Logic (Fragile Areas #3)
- ✅ Windows Symlink Fallback (Fragile Areas #4)

**Plans**:
- [ ] **13-01-PLAN.md**: Break down large scripts into modules
- [ ] **13-02-PLAN.md**: Validate output path dependencies
- [ ] **13-03-PLAN.md**: Add regression input validation
- [ ] **13-04-PLAN.md**: Parameterize string matching thresholds
- [ ] **13-05-PLAN.md**: Improve Windows symlink fallback

---

## Phase 14: Dependency Management

**Goal**: Ensure long-term stability and compatibility

**Depends on**: Phase 11 (testing framework to validate changes)

**Success Criteria**:
1. statsmodels version pinned in requirements.txt with upgrade path documented
2. PyArrow performance tested on newer versions before upgrading
3. Pipeline tested on Python 3.8-3.13, supported versions documented
4. rapidsuzz optional dependency properly documented or made required

**Concerns Addressed**:
- ✅ Statsmodels Version Compatibility (Dependencies at Risk #1)
- ✅ PyArrow Performance Degradation (Dependencies at Risk #2)
- ✅ Python 3.13 Compatibility (Dependencies at Risk #3)
- ✅ rapidsuzz Optional Dependency (Dependencies at Risk #4)

**Status**: 📝 PLANNED (4 plans in 2 waves)
**Plans**: 4 plans

Plans:
- [ ] 14-01: Pin statsmodels to 0.14.6 and document versioning strategy (Wave 1)
- [ ] 14-02: Document PyArrow 21.0.0 compatibility and performance (Wave 1)
- [ ] 14-03: Test pipeline on Python 3.8-3.13 with GitHub Actions matrix (Wave 2)
- [ ] 14-04: Document RapidFuzz optional dependency with installation instructions (Wave 1)

---

## Phase 15: Scaling Preparation

**Goal**: Remove scaling limits for future growth

**Depends on**: Phase 10 (performance optimizations required first)

**Success Criteria**:
1. Deterministic parallelization implemented with seed propagation
2. Column pruning with pyarrow implemented for large datasets
3. Chunked processing implemented for memory-constrained systems
4. Memory usage monitoring added to scripts
5. Scaling limits documented with improvement paths

**Concerns Addressed**:
- ✅ Single-Threaded Processing (Scaling Limits #1)
- ✅ Disk I/O Bottleneck (Scaling Limits #2)
- ✅ Memory Requirements (Scaling Limits #3)

**Plans**:
- [ ] **15-01-PLAN.md**: Implement deterministic parallelization
- [ ] **15-02-PLAN.md**: Add column pruning for Parquet files
- [ ] **15-03-PLAN.md**: Implement chunked processing for large files
- [ ] **15-04-PLAN.md**: Add memory usage monitoring
- [ ] **15-05-PLAN.md**: Document scaling limits and improvement paths

---

## Progress Tracking

**Execution Order**: 7 → 8 → 9 → 10 → 11 → 12 → 13 → 14 → 15

| Phase | Plans | Concerns | Priority | Status |
|-------|-------|----------|----------|--------|
| 7. Critical Bug Fixes | 2 | 2 | MUST DO | ○ Pending |
| 8. Tech Debt Cleanup | 4 | 3 | HIGH | ○ Pending |
| 9. Security Hardening | 3 | 3 | MEDIUM-HIGH | ○ Pending |
| 10. Performance Optimization | 4 | 4 | MEDIUM | ○ Pending |
| 11. Testing Infrastructure | 7 | 6 | HIGH | ○ Pending |
| 12. Data Quality & Observability | 3 | 3 | LOW-MEDIUM | ○ Pending |
| 13. Script Refactoring | 5 | 5 | LOW | ○ Pending |
| 14. Dependency Management | 4 | 4 | MEDIUM | ○ Pending |
| 15. Scaling Preparation | 5 | 3 | LOW-MEDIUM | ○ Pending |

**Summary**:
- Total phases: 9
- Total plans: 37
- Total concerns: 34
- All concerns mapped ✓

**Priority Breakdown**:
- MUST DO: 2 concerns (6%)
- HIGH: 9 concerns (26%)
- MEDIUM: 8 concerns (24%)
- LOW-MEDIUM: 6 concerns (18%)
- LOW: 9 concerns (26%)

---

## Risk Assessment

**Low Risk** (Can proceed immediately):
- Phase 7: Critical Bug Fixes - straightforward fixes
- Phase 8: Tech Debt Cleanup - standard refactoring

**Medium Risk** (Requires careful testing):
- Phase 10: Performance Optimization - changes may affect results
- Phase 11: Testing Infrastructure - needs comprehensive test design
- Phase 13: Script Refactoring - large structural changes

**High Risk** (Needs validation):
- Phase 14: Dependency Management - version changes may break compatibility
- Phase 15: Scaling Preparation - parallelization may affect determinism

---

**Roadmap created:** 2026-01-23
**Total concerns addressed:** 34/34 (100%)
**Total plans:** 37
**Estimated effort:** Phases 7-9 (MUST DO + HIGH) = 13 plans, ~2-3 weeks

