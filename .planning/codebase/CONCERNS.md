# Codebase Concerns

**Analysis Date:** 2026-02-21

## Tech Debt

**stats.py Module Bloat:**
- Issue: `src/f1d/shared/observability/stats.py` is 5,309 lines — exceeds recommended module size by 50x
- Files: `src/f1d/shared/observability/stats.py`
- Impact: Slow IDE indexing, difficult navigation, merge conflicts likely, cognitive overload
- Fix approach: Split into focused submodules (e.g., `stats_core.py`, `stats_typed_dicts.py`, `stats_analysis.py`)

**Excessive Print Statements:**
- Issue: 1,284 `print()` calls in source code instead of proper logging
- Files: Throughout `src/f1d/econometric/`, `src/f1d/sample/`, `src/f1d/variables/`
- Impact: Inconsistent output, no log levels, difficult to debug in production, can't redirect output
- Fix approach: Replace with `logging` module or `structlog` (already in dependencies)

**Type Ignore Comments:**
- Issue: 30+ `# type: ignore` comments suppressing mypy warnings
- Files: `src/f1d/econometric/run_h9_takeover_hazards.py`, `src/f1d/sample/build_tenure_map.py`, `src/f1d/sample/clean_metadata.py`
- Impact: Hidden type errors, reduced type safety benefits
- Fix approach: Properly type the code or add explicit casts where type ignores are necessary

**Legacy Path Functions:**
- Issue: Deprecated path functions marked for removal in v7.0
- Files: `src/f1d/shared/path_utils.py` (lines 130, 450-455)
- Impact: Technical debt accumulation, confusing API surface
- Fix approach: Complete migration to new path utilities, remove deprecated functions

## Known Bugs

**Broad Exception Handling:**
- Issue: 40+ `except Exception as e:` blocks catching all exceptions indiscriminately
- Files: `src/f1d/econometric/run_h1_cash_holdings.py`, `src/f1d/econometric/run_h2_investment.py`, `src/f1d/shared/panel_ols.py`
- Symptoms: Silent failures, difficult debugging, exceptions swallowed without proper handling
- Trigger: Any runtime error in wrapped code blocks
- Workaround: None — requires code changes

**Empty Return Patterns:**
- Issue: Multiple functions return `None, None, set()` or `None, {}` for error conditions
- Files: `src/f1d/econometric/run_h0_1_manager_clarity.py`, `src/f1d/econometric/run_h0_2_ceo_clarity.py`, all hypothesis run scripts
- Symptoms: Callers must check for None tuple patterns, easy to miss error handling
- Trigger: Invalid data conditions, missing variables
- Workaround: Callers must explicitly check return values

**Pass Statements (Empty Implementations):**
- Issue: 20+ bare `pass` statements indicating incomplete implementations
- Files: `src/f1d/shared/config/step_configs.py`, `src/f1d/shared/data_validation.py`, `src/f1d/shared/diagnostics.py`, `src/f1d/shared/env_validation.py`
- Symptoms: Classes/functions with no behavior, silent no-ops
- Fix approach: Implement or raise `NotImplementedError` with clear message

## Security Considerations

**Import of Optional Dependencies:**
- Risk: Runtime imports with fallback to None may cause AttributeError if used incorrectly
- Files: `src/f1d/shared/panel_ols.py` (lines 76-82), `src/f1d/econometric/run_h9_takeover_hazards.py` (lines 66, 294)
- Current mitigation: `LINEARMODELS_AVAILABLE` flag pattern
- Recommendations: Add explicit checks before using optional imports, fail fast with clear error messages

**sys.exit() Calls:**
- Risk: Direct `sys.exit()` in library code makes testing difficult and can abort unexpectedly
- Files: `src/f1d/econometric/run_h0_5_ceo_tone.py` (lines 330, 355, 363, 388), all run scripts
- Current mitigation: None
- Recommendations: Raise custom exceptions instead, let caller decide exit behavior

## Performance Bottlenecks

**Unchunked Parquet Reads:**
- Problem: Large parquet files read entirely into memory
- Files: `src/f1d/econometric/run_h1_cash_holdings.py`, `src/f1d/econometric/run_h2_investment.py`, all panel builders
- Cause: `pd.read_parquet()` without `columns` parameter or chunking
- Improvement path: Use `columns` parameter to read only needed columns; implement streaming for large datasets

**pd.concat in Loops:**
- Problem: DataFrames concatenated in loops (inefficient memory allocation)
- Files: `src/f1d/econometric/run_h0_1_manager_clarity.py` (line 448)
- Cause: Appending to list then concatenating once (correct pattern), but multiple large concatenations
- Improvement path: Pre-allocate DataFrame sizes where possible; use single concatenation at end

## Fragile Areas

**Compustat Engine:**
- Files: `src/f1d/shared/variables/_compustat_engine.py` (1,099 lines)
- Why fragile: Complex business logic with multiple audit fixes documented; handles edge cases for financial data
- Safe modification: Add tests before any change; document all changes in header comment
- Test coverage: Limited — relies on downstream tests

**Entity Linking:**
- Files: `src/f1d/sample/link_entities.py` (1,292 lines)
- Why fragile: 4-tier matching strategy with fuzzy matching fallback; critical for data quality
- Safe modification: Run full entity linking after any change; verify match rates
- Test coverage: Only 1 test file (`test_fuzzy_matching.py` with 1 test)

**Panel OLS Module:**
- Files: `src/f1d/shared/panel_ols.py` (573 lines)
- Why fragile: Complex statistical computations; VIF calculations, fixed effects, clustered SEs
- Safe modification: Run full test suite (`test_panel_ols.py` has 39 tests); verify numerical outputs
- Test coverage: Good (39 tests)

**Tenure Map Builder:**
- Files: `src/f1d/sample/build_tenure_map.py` (816 lines)
- Why fragile: Complex CEO episode reconstruction; date arithmetic edge cases
- Safe modification: Test with various tenure scenarios; verify date handling
- Test coverage: No dedicated test file

## Scaling Limits

**Memory Usage:**
- Current capacity: Processes 297k calls, ~11k unique companies
- Limit: Single-process in-memory processing
- Scaling path: Implement Dask or Polars for out-of-core processing; chunk large datasets

**Entity Matching:**
- Current capacity: Fuzzy matching uses rapidfuzz with configurable threshold
- Limit: O(n²) comparison for unmatched entities; slow for large entity lists
- Scaling path: Implement blocking/indexing to reduce comparison space; consider vector embeddings

## Dependencies at Risk

**statsmodels Version Pin:**
- Risk: Pinned to 0.14.6 due to breaking changes in 0.14.0 (deprecated GLM link names)
- Impact: Can't use newer features; security patches may require upgrade
- Migration plan: Update code to use new link function names, test thoroughly

**pyarrow Version Pin:**
- Risk: Pinned to 21.0.0 for Python 3.8-3.13 compatibility; 23.0.0+ requires Python >= 3.10
- Impact: Missing performance improvements in newer versions
- Migration plan: When Python 3.9 dropped, upgrade to latest pyarrow

**lifelines Optional Dependency:**
- Risk: Used in `run_h9_takeover_hazards.py` with graceful fallback
- Impact: Survival analysis unavailable if not installed
- Migration plan: Document in requirements.txt as required for H9

## Missing Critical Features

**No Dedicated Tests for Econometric Run Scripts:**
- Problem: 15 `run_h*.py` scripts have no corresponding test files
- Files: All files in `src/f1d/econometric/run_*.py`
- Blocks: Regression testing of hypothesis-specific econometric analysis

**No Tests for Sample Assembly:**
- Problem: Sample assembly, tenure map, and clean_metadata have no test files
- Files: `src/f1d/sample/assemble_manifest.py`, `src/f1d/sample/build_tenure_map.py`, `src/f1d/sample/clean_metadata.py`
- Blocks: Confidence in sample construction changes

## Test Coverage Gaps

**Econometric Run Scripts:**
- What's not tested: All 15 hypothesis-specific regression scripts
- Files: `src/f1d/econometric/run_h0_1_manager_clarity.py` through `run_h10_tone_at_top.py`
- Risk: Regression errors in econometric analysis undetected
- Priority: Medium — tested indirectly through downstream results

**Sample Assembly Pipeline:**
- What's not tested: Entity linking, manifest assembly, metadata cleaning
- Files: `src/f1d/sample/link_entities.py`, `src/f1d/sample/assemble_manifest.py`, `src/f1d/sample/clean_metadata.py`
- Risk: Data quality issues could propagate silently
- Priority: High — critical for data pipeline integrity

**Variable Builder Modules:**
- What's not tested: Individual variable construction scripts
- Files: `src/f1d/variables/build_h*.py` (all panel builders)
- Risk: Variable construction errors not caught until econometric stage
- Priority: Medium — some coverage through regression tests

**Reporting Module:**
- What's not tested: Summary statistics generation
- Files: `src/f1d/reporting/generate_summary_stats.py`
- Risk: Incorrect summary statistics in reports
- Priority: Low — output can be verified manually

---

*Concerns audit: 2026-02-21*
