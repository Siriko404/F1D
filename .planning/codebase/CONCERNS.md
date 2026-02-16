# Codebase Concerns

**Analysis Date:** 2026-02-15

## Tech Debt

**Large Monolithic Module (observability/stats.py):**
- Issue: `src/f1d/shared/observability/stats.py` is 5,309 lines - single file containing numerous statistics functions, TypedDict definitions, and analysis utilities
- Files: `src/f1d/shared/observability/stats.py`
- Impact: Difficult to navigate, maintain, and test; violates single responsibility principle
- Fix approach: Split into focused modules: `stats_calculators.py`, `stats_printers.py`, `stats_schemas.py` (TypedDicts), `stats_analysis.py`

**TODO Comment in Production Code:**
- Issue: TODO comment tracking winsorized columns in 3.1_FirmControls.py
- Files: `src/f1d/financial/v1/3.1_FirmControls.py:770`
- Impact: Indicates incomplete implementation; winsorized columns list is hardcoded rather than computed
- Fix approach: Implement dynamic tracking of winsorized columns from winsorization function, remove TODO comment

**Missing Type Stubs Reference:**
- Issue: Placeholder GitHub issue number in lifelines type ignore comment
- Files: `src/f1d/econometric/v1/4.3_TakeoverHazards.py:62`
- Impact: Comment references `github.com/CamDavidsonPilon/lifelines/issues/XXX` instead of actual issue number
- Fix approach: Replace with actual issue number or remove placeholder if issue doesn't exist

## Known Bugs

**Broad Exception Handling in Git Operations:**
- Symptoms: `get_git_sha()` function catches all exceptions and returns "unknown" without logging
- Files: `src/f1d/econometric/v2/4.4_H4_LeverageDiscipline.py:104-105`, `src/f1d/econometric/v2/4.3_H3PayoutPolicyRegression.py:108-109`, `src/f1d/econometric/v2/4.10_H2_PRiskUncertainty_Investment.py:94-95`, `src/f1d/econometric/v2/4.1_H1CashHoldingsRegression.py:101-102`
- Trigger: Any subprocess.run() failure for git rev-parse command
- Workaround: None - function silently returns "unknown"
- Fix approach: Log exception details before returning "unknown" so failures are visible

**Broad Exception Handling in Date Parsing:**
- Symptoms: `parse_date_quarter()` in 3.12_H9_PRiskFY.py catches ValueError/AttributeError and returns None without logging
- Files: `src/f1d/financial/v2/3.12_H9_PRiskFY.py:316-317`, `src/f1d/financial/v2/3.12_H9_PRiskFY.py:187-188` (construct_cal_q_end)
- Trigger: Malformed date strings in PRisk data
- Workaround: None - silent failures filtered out by downstream code
- Fix approach: Log parsing failures with the problematic input value for debugging

## Security Considerations

**CSV File Input Without Schema Validation:**
- Risk: Multiple CSV file reads (`pd.read_csv`) lack explicit column/row validation before processing
- Files: `src/f1d/sample/1.5_Utils.py:43`, `src/f1d/text/tokenize_and_count.py:771`, `src/f1d/shared/regression_helpers.py:66,163`, `src/f1d/shared/sample_utils.py:50`, `src/f1d/financial/v2/3.10_H2_PRiskUncertaintyMerge.py:196`, `src/f1d/financial/v2/3.12_H9_PRiskFY.py:222`
- Current mitigation: Some files use `on_bad_lines="skip"` for CSV reading, but no schema validation
- Recommendations: Add Pandera schema validation or explicit column existence checks before processing CSV data

**Hardcoded File Paths in Some Scripts:**
- Risk: `load_master_variable_definitions()` uses hardcoded path to `1_Inputs/master_variable_definitions.csv`
- Files: `src/f1d/sample/1.5_Utils.py:40`
- Current mitigation: None - assumes fixed directory structure
- Recommendations: Use path resolution from `shared.path_utils` or configuration file for input paths

## Performance Bottlenecks

**O(n²) Fuzzy Matching in Entity Linking:**
- Problem: Entity linking uses fuzzy matching with O(n²) complexity
- Files: `src/f1d/sample/1.2_LinkEntities.py` (1285 lines)
- Cause: NLP-based fuzzy matching compares each transcript against all candidate firms
- Improvement path: Documented in SCALING.md - implement parallelization, better indexing, or deterministic parallel RNG (available in git history per SCALING.md)

**Single-Threaded Processing (by Default):**
- Problem: Pipeline runs single-threaded despite multi-core availability
- Files: Configuration default in `config/project.yaml` (`thread_count: 1`)
- Cause: Determinism requirements prioritize reproducibility over speed
- Improvement path: Enable `thread_count` in config for production runs; parallel RNG prototype available in git history (removed in Phase 16-03, commit 02288a0)

**Large File Reads Without Column Pruning:**
- Problem: Some scripts load full Parquet files when only subset of columns needed
- Files: Partially addressed - 13 scripts use column pruning (per SCALING.md), but remaining scripts (2.2, 2.3, some 3.x) do not
- Cause: Historically all columns loaded for simplicity
- Improvement path: Add column pruning to `pd.read_parquet()` calls with `columns=[...]` parameter

**Memory-Intensive Text Processing:**
- Problem: Tokenization loads entire transcript files into memory
- Files: `src/f1d/text/tokenize_and_count.py` (1354 lines)
- Cause: sklearn CountVectorizer requires full text corpus in memory
- Improvement path: Use `shared/chunked_reader.py` MemoryAwareThrottler for chunked processing (documented but not implemented)

## Fragile Areas

**Econometric V2 Regression Scripts:**
- Files: All scripts in `src/f1d/econometric/v2/` (11 scripts, 1000+ lines each)
- Why fragile: Complex model specifications, multiple regression types, extensive error handling with broad exception catches
- Safe modification: Add tests for new regression specifications; verify VIF diagnostics; test with sample data before production
- Test coverage: Limited - only 6 test files mention econometric/sample/financial modules; regression tests focus on v1 only

**Large Financial Variable Scripts:**
- Files: `src/f1d/financial/v2/3.2_H2Variables.py` (1694 lines), `src/f1d/financial/v2/3.13_H9_AbnormalInvestment.py` (1402 lines), `src/f1d/financial/v2/3.10_H2_PRiskUncertaintyMerge.py` (1323 lines), others 1100-1300 lines
- Why fragile: Multiple data merges, complex variable construction, extensive business logic for hypothesis variables
- Safe modification: Use existing unit tests as templates; verify output schemas match expected structure; test with subset of data first
- Test coverage: Minimal - only `tests/unit/test_v1_financial_utils.py` tests v1 financial features; v2 has dedicated tests per hypothesis but limited

**Survival Analysis Script:**
- Files: `src/f1d/econometric/v1/4.3_TakeoverHazards.py`
- Why fragile: Lifelines library lacks type stubs requiring many `# type: ignore` comments; Cox PH and Fine-Gray models sensitive to data format; event timing calculations complex
- Safe modification: Verify survival time calculations with manual checks; test with small dataset before full run; maintain type ignore comments with rationale
- Test coverage: `tests/unit/test_takeover_survival_analysis.py` exists but coverage unknown

## Scaling Limits

**Memory Constraints:**
- Current capacity: ~50K transcripts, 16GB RAM recommended per SCALING.md
- Limit: OOM errors occur on 8GB systems during entity linking; 32GB needed for 2-5x dataset size
- Scaling path: Enable column pruning everywhere, use MemoryAwareThrottler, implement parallel processing, consider Dask/Ray for 100x scaling

**Processing Time:**
- Current duration: 2-4 hours for full pipeline on modern hardware
- Limit: Single-threaded by default; fuzzy matching O(n²) bottleneck
- Scaling path: Parallelization (thread_count config), better fuzzy matching algorithms, SSD/NVMe storage

**Test Execution Time:**
- Current: 72 test files, 1306 test methods
- Limit: E2E tests timeout at 1200 seconds per CI configuration
- Scaling path: Mark slow tests with `@pytest.mark.slow`, use fixtures for data loading, parallel test execution

## Dependencies at Risk

**Lifelines (No Official Type Stubs):**
- Risk: Lack of type stubs forces extensive `# type: ignore` comments, reducing type safety
- Impact: All lifelines usage in `4.3_TakeoverHazards.py` bypasses mypy checking
- Migration plan: Contribute or use community type stubs if available; monitor lifelines repo for official stub support; current workarounds are scoped with rationale comments

**Sklearn (Lacks py.typed Marker):**
- Risk: CountVectorizer and other sklearn components not type-checkable
- Impact: `src/f1d/text/tokenize_and_count.py` has multiple type ignores for sklearn operations
- Migration plan: None - upstream issue; current type ignores are scoped and documented

**Optional Dependencies:**
- Risk: RapidFuzz optional but not required; pipeline degrades gracefully without it
- Impact: Tier 3 fuzzy name matching unavailable, reducing match rates in entity linking
- Migration plan: Document in README; consider making optional dependency more prominent in installation instructions

## Missing Critical Features

**Comprehensive Integration Tests:**
- Problem: Limited integration test coverage across pipeline stages
- Blocks: Cannot verify end-to-end data flow without manual runs
- Priority: Medium - Tier 1/2 tests cover shared modules well; regression tests exist for specific hypotheses

**Performance Regression Tests:**
- Problem: No automated performance benchmarking for critical operations
- Blocks: Cannot detect performance degradations from code changes
- Priority: Low - SCALING.md documents bottlenecks but no CI enforcement of performance thresholds

**Parallel Processing Integration:**
- Problem: Parallel RNG prototype available in git history but not integrated
- Blocks: Cannot utilize multi-core systems for speedup
- Priority: Medium - documented in SCALING.md, removed in Phase 16-03 but available for resurrection

## Test Coverage Gaps

**Untested Areas:**

**Econometric V2 Scripts:**
- What's not tested: Hypothesis regression scripts (H1-H9), data preparation, VIF diagnostics
- Files: All `src/f1d/econometric/v2/*.py` files
- Risk: Regression bugs in complex regression specifications, VIF calculation errors, merge failures
- Priority: Medium

**Financial V2 Scripts:**
- What's not tested: Hypothesis variable construction scripts (3.1-3.13), PRisk data loading, abnormal investment calculations
- Files: All `src/f1d/financial/v2/*.py` files
- Risk: Incorrect variable definitions, merge errors, winsorization mistakes
- Priority: Medium

**Sample Construction Scripts:**
- What's not tested: 1.0_BuildSampleManifest, 1.1_CleanMetadata, 1.3_BuildTenureMap
- Files: `src/f1d/sample/1.0_BuildSampleManifest.py`, `src/f1d/sample/1.1_CleanMetadata.py`, `src/f1d/sample/1.3_BuildTenureMap.py`
- Risk: Manifest construction errors, metadata cleaning bugs, tenure tracking mistakes
- Priority: High - foundation for all downstream processing

**Text Processing Scripts:**
- What's not tested: tokenize_and_count (1354 lines), construct_variables
- Files: `src/f1d/text/tokenize_and_count.py`, `src/f1d/text/construct_variables.py`
- Risk: Tokenization bugs, variable calculation errors, linguistic measure mistakes
- Priority: High - core linguistic analysis depends on these

**Observability Stats Module:**
- What's not tested: Large stats.py module (5309 lines), TypedDict schemas, analysis functions
- Files: `src/f1d/shared/observability/stats.py`
- Risk: Stats calculation errors, reporting bugs, data schema mismatches
- Priority: Low - helper functions, but errors could hide data issues

---

*Concerns audit: 2026-02-15*
