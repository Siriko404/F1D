# Codebase Concerns

**Analysis Date:** 2026-02-15

## Tech Debt

**Data Coverage Truncation (H7-H8):**
- Issue: H8TakeoverVariables.py expects Volatility/StockRet from H7 output but H7 only calculates these for years with CRSP DSF data. Full sample period is 2002-2018 but only 2002-2004 data may be present in CRSP_DSF directory. This causes silent data truncation.
- Files: `src/f1d/financial/v2/3.7_H7IlliquidityVariables.py`, `src/f1d/financial/v2/3.8_H8TakeoverVariables.py`
- Impact: H8 dataset truncated to partial year range (verified via ROADMAP_V3.md BUG-01-01). Regression analysis on incomplete data invalidates results.
- Fix approach: Calculate Volatility/StockRet directly from CRSP DSF data within H7 script (as already implemented in `calculate_stock_volatility_and_returns` function). Verify CRSP DSF data availability for full 2002-2018 period. Create regression test to ensure full coverage after fix.

**ProcessPool Crash Bug:**
- Issue: Category hit rates show 0.00% for all categories in stats.json because `compute_tokenize_process_stats` initializes with zeros but workaround runs too late. Post-load workaround at lines 1093-1104 executes after function returns zeros.
- Files: `.planning/debug/category-hit-rates-bug.md`, `src/f1d/text/tokenize_and_count.py`
- Impact: Incorrect statistics reporting, ProcessPool crashes on re-run with "terminated abruptly" error
- Fix approach: Move workaround before `compute_tokenize_process_stats` call (before line 1073), or modify function to accept output_dfs parameter for in-place calculation.

**Global State Usage:**
- Issue: `src/f1d/econometric/v1/4.3_TakeoverHazards.py` uses `global ROOT` variable in main() function (line 441).
- Files: `src/f1d/econometric/v1/4.3_TakeoverHazards.py`
- Impact: Makes module testing difficult, introduces side effects, violates encapsulation principles
- Fix approach: Pass root path as parameter to main() or use dependency injection pattern

**Silent Error Handling:**
- Issue: Multiple scripts use broad `except Exception:` without logging or re-raising, suppressing errors that should halt execution
- Files: `src/f1d/text/construct_variables.py:1038`, `src/f1d/shared/chunked_reader.py:195,369`, `src/f1d/financial/v2/3.10_H2_PRiskUncertaintyMerge.py:208,823,1264`
- Impact: Errors continue silently, producing incorrect outputs without user awareness
- Fix approach: Replace silent except blocks with specific exception types, log errors appropriately, and re-raise when appropriate

**Legacy Code in Active Directory:**
- Issue: Multiple legacy scripts remain in `_archive/legacy_archive/legacy/` directory with outdated patterns
- Files: `_archive/legacy_archive/legacy/ARCHIVE_BROKEN_STEP2/`, `_archive/legacy_archive/legacy/ARCHIVE_OLD/`
- Impact: Directory clutter, potential confusion about which code is current
- Fix approach: Archive organization per ROADMAP_V3.md Phase 60-01

## Known Bugs

**Category Hit Rates Zero:**
- Symptoms: category_hit_rates in stats.json shows 0.00% for all categories
- Files: `.planning/debug/category-hit-rates-bug.md`, `src/f1d/text/tokenize_and_count.py`
- Trigger: Running 2.1_TokenizeAndCount.py
- Workaround: Not currently working (workaround executes after function returns zeros)
- Fix: Move workaround before compute_tokenize_process_stats call

**ProcessPool Crash on Re-run:**
- Symptoms: "A process in the process pool was terminated abruptly while the future was running or pending"
- Files: `.planning/debug/category-hit-rates-bug.md`
- Trigger: Re-running 2.1_TokenizeAndCount.py after initial run
- Workaround: None documented
- Fix: Related to category hit rates bug - requires same fix

## Security Considerations

**Secret Files Exclusion:**
- Risk: Environment variables and credentials files present in repository but excluded from git via .gitignore
- Files: `.env`, `.env.*`, `credentials.*`, `secrets.*` (not in repo but should remain excluded)
- Current mitigation: .gitignore contains patterns for secrets (verified by <forbidden_files> documentation)
- Recommendations: Ensure .gitignore is comprehensive and audited regularly

**Dependency Security:**
- Risk: Outdated or vulnerable dependencies
- Files: `requirements.txt`, `pyproject.toml`
- Current mitigation: Bandit configured in pyproject.toml but scans may not be run
- Recommendations: Enable Dependabot or Renovate for automated dependency updates, run security scanning regularly

## Performance Bottlenecks

**Large Monolithic Files:**
- Problem: `src/f1d/shared/observability/stats.py` is 5,309 lines - difficult to navigate and maintain
- Files: `src/f1d/shared/observability/stats.py`
- Cause: Accumulation of statistics functions without modularization
- Improvement path: Already addressed in ROADMAP_V3.md Phase 60-03 (Split Monolithic Utilities). Module split into observability submodules already partially complete.

**Pandas Anti-Patterns:**
- Problem: `.apply(lambda)` and `.iterrows()` usage in performance-critical code paths
- Files: `src/f1d/text/tokenize_and_count.py:920,1018`, `src/f1d/sample/1.4_AssembleManifest.py:227`, `src/f1d/sample/1.2_LinkEntities.py:605,617`
- Cause: Python-level loops over DataFrame rows instead of vectorized operations
- Improvement path: Replace with vectorized pandas operations per ROADMAP_V3.md Phase 62-01 and 62-02. Comments in code indicate awareness (line 790: "OPTIMIZATION: Vectorized melt replaces .iterrows()")

**Memory Usage in Large File Processing:**
- Problem: Chunked reading exists but not consistently applied across all data loading operations
- Files: `src/f1d/shared/chunked_reader.py`, various loading functions
- Cause: Inconsistent application of chunking pattern
- Improvement path: Standardize chunked reading usage across all large Parquet file loads

## Fragile Areas

**Path Resolution for Latest Output:**
- Files: `src/f1d/financial/v2/3.8_H8TakeoverVariables.py:113-136`, `src/f1d/shared/path_utils.py`
- Why fragile: `get_latest_output_dir` searches for directories by modification time, which can fail if multiple directories exist with similar timestamps or if symlink logic breaks
- Safe modification: Use explicit timestamp-based directory naming throughout pipeline
- Test coverage: Test coverage exists in `tests/unit/test_path_utils.py` but may not cover edge cases

**Merge Operations Without Schema Validation:**
- Files: `src/f1d/shared/data_loading.py`, multiple merge operations in financial scripts
- Why fragile: Merges assume matching schemas but validate only via existence checks
- Safe modification: Add Pandera schema validation to critical merge operations per ROADMAP_V3.md Phase 63-02
- Test coverage: Gaps in merge validation coverage

**Entity Linking (Sample Stage 1.2):**
- Files: `src/f1d/sample/1.2_LinkEntities.py` (1,285 lines)
- Why fragile: Complex fuzzy matching and CCM linking logic with multiple fallback paths
- Safe modification: Extract into smaller testable functions, add unit tests for each matching tier
- Test coverage: Partial coverage exists in integration tests

## Scaling Limits

**CRSP DSF Data Coverage:**
- Current capacity: CRSP DSF data available from 1999 through at least 2003 (confirmed by directory listing)
- Limit: Unknown whether data exists for full 2002-2018 period required by H7-H8
- Scaling path: Verify CRSP DSF data completeness for required year range, add data validation step that checks for missing years before processing

**Test Coverage Thresholds:**
- Current capacity: CI requires only 10% Tier 1, 10% Tier 2, 25% overall coverage (pyproject.toml lines 73, 86, 99)
- Limit: Low thresholds mask quality issues in untested modules
- Scaling path: Gradually increase thresholds as more tests are added per ROADMAP_V3.md Phase 63-03

## Dependencies at Risk

**statsmodels Pinning:**
- Risk: Pinned to 0.14.6 for reproducibility but outdated (requirements.txt line 11)
- Impact: May miss bug fixes or performance improvements in newer versions
- Migration plan: Documented in ROADMAP_V3.md requires careful upgrade due to breaking changes in 0.14.0

**pyarrow Pinning:**
- Risk: Pinned to 21.0.0 for Python 3.8 compatibility (requirements.txt line 18)
- Impact: Misses performance improvements in 23.0.0+ and 24.0.0
- Migration plan: Upgrade requires Python >= 3.10, documented in DEPENDENCIES.md

## Missing Critical Features

**Schema Validation on Outputs:**
- Problem: No automated validation of Parquet output schemas
- Blocks: Data quality issues not caught until downstream processing fails
- Risk: High - could produce incorrect research results

**End-to-End Pipeline Test:**
- Problem: No full pipeline test that verifies all 4 stages work together
- Blocks: Confidence in pipeline reproducibility
- Risk: Medium - integration gaps may exist

**Variable Catalog:**
- Problem: No comprehensive catalog of all constructed variables
- Blocks: Easy reference for researchers and auditors
- Risk: Low - documentation gap but not functional blocker

## Test Coverage Gaps

**Untested V1 Scripts:**
- What's not tested: Most V1 econometric scripts (4.1_*.py, 4.2_*.py, 4.3_*.py, 4.4_*.py)
- Files: `src/f1d/econometric/v1/` (all scripts)
- Risk: High - V1 scripts produce research outputs but lack verification
- Priority: High

**Untested Financial V2 Scripts:**
- What's not tested: Variable construction scripts (3.1_H1Variables.py through 3.8_H8TakeoverVariables.py)
- Files: `src/f1d/financial/v2/` (all scripts)
- Risk: High - These scripts construct all variables used in hypothesis testing
- Priority: High

**Untested Text Processing Scripts:**
- What's not tested: Tokenization and variable construction (2.1_*.py, 2.2_*.py)
- Files: `src/f1d/text/` (all scripts except verification)
- Risk: Medium - Test coverage exists in integration tests but not at unit level
- Priority: Medium

**Untested Observability Functions:**
- What's not tested: Many stats functions in observability/stats.py
- Files: `src/f1d/shared/observability/stats.py`
- Risk: Low - Support functions, not critical path
- Priority: Low

**Untested Regression Analysis Scripts:**
- What's not tested: V2 regression scripts (4.1_*.py through 4.11_*.py)
- Files: `src/f1d/econometric/v2/` (all regression scripts)
- Risk: High - These scripts produce all research findings
- Priority: High

---

*Concerns audit: 2026-02-15*
