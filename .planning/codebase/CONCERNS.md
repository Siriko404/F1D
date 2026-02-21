# Codebase Concerns

**Analysis Date:** 2026-02-20

## Tech Debt

**Oversized Module - stats.py:**
- Issue: `src/f1d/shared/observability/stats.py` is 5,309 lines, making it the largest file in the codebase by far (4x larger than next largest)
- Files: `src/f1d/shared/observability/stats.py`
- Impact: Difficult to navigate, maintain, and test. High cognitive load for any changes.
- Fix approach: Split into focused modules (e.g., `stats_input.py`, `stats_linking.py`, `stats_tenure.py`, `stats_tokenize.py`, `stats_financial.py`)

**Performance Anti-Pattern - iterrows():**
- Issue: 25+ uses of `df.iterrows()` which is notoriously slow in pandas (100-1000x slower than vectorized operations)
- Files: `src/f1d/reporting/generate_summary_stats.py`, `src/f1d/shared/financial_utils.py`, `src/f1d/sample/link_entities.py`, `src/f1d/shared/observability/stats.py`, `src/f1d/shared/panel_ols.py`
- Impact: Performance degradation on large datasets, especially in entity linking (~11k companies)
- Fix approach: Replace with `itertuples()`, vectorized operations, or `.apply()` where appropriate

**Performance Anti-Pattern - pd.concat in Loops:**
- Issue: 53 occurrences of `pd.concat()` often used in loops instead of pre-allocated lists
- Files: Variable builders in `src/f1d/shared/variables/*.py`, econometric scripts
- Impact: O(n²) memory allocation behavior for large datasets
- Fix approach: Collect in list then single concat, or use `pd.DataFrame.from_records()`

**Bare Except Clauses:**
- Issue: 5 occurrences of `except Exception:` or `except:` without specific exception types
- Files: `src/f1d/shared/variables/base.py:237`, `src/f1d/shared/regression_helpers.py:160`, `src/f1d/shared/observability/stats.py:691`, `src/f1d/shared/metadata_utils.py:78`, `src/f1d/shared/diagnostics.py:416`
- Impact: Silent failures, difficult debugging, potential to catch unexpected errors
- Fix approach: Catch specific exceptions (FileNotFoundError, KeyError, ValueError) and log appropriately

**Type Ignore Accumulation:**
- Issue: 80 `# type: ignore` comments throughout codebase indicating type system friction
- Files: Concentrated in `src/f1d/shared/variables/_compustat_engine.py`, `src/f1d/econometric/run_*.py`, `src/f1d/shared/panel_ols.py`
- Impact: Reduced type safety, potential runtime errors not caught during development
- Fix approach: Add proper type stubs or use `Any` explicitly where third-party libraries lack typing

## Known Bugs

**Configuration Mismatch:**
- Symptoms: `.coveragerc` references `source = 2_Scripts` but codebase uses `src/f1d` (src-layout)
- Files: `.coveragerc:5`, `pyproject.toml:102`
- Trigger: Running coverage reports may produce inconsistent results
- Workaround: pyproject.toml has correct path; coverage via pytest uses that

## Security Considerations

**Subprocess Execution:**
- Risk: Arbitrary script execution if paths not validated
- Files: `src/f1d/shared/subprocess_validation.py`, `src/f1d/sample/build_sample_manifest.py`
- Current mitigation: `validate_script_path()` validates paths are within allowed directories, uses absolute paths
- Recommendations: Security posture is adequate; consider adding allowed directories to configuration

**No Hardcoded Credentials:**
- Risk: None detected
- Files: Scanned all `.py` files
- Current mitigation: `.env.example` template provided, no secrets in code
- Recommendations: Maintain current practice; ensure `.env` is in `.gitignore` (verified present)

## Performance Bottlenecks

**Entity Linking Fuzzy Matching:**
- Problem: Fuzzy matching uses `iterrows()` loop over ~11k companies against CCM database
- Files: `src/f1d/sample/link_entities.py:617`
- Cause: Python loop overhead + string distance calculations per row
- Improvement path: Pre-compute normalized names, use vectorized fuzzy matching with `rapidfuzz.process.extract` batch mode

**Financial Utils Row-by-Row Processing:**
- Problem: `compute_financial_features()` uses `iterrows()` for potentially large datasets
- Files: `src/f1d/shared/financial_utils.py:157`
- Cause: Sequential row processing instead of vectorized merge/join operations
- Improvement path: Use `pd.merge_asof()` for temporal joins, vectorized calculations

## Fragile Areas

**Variable Builder Engine Singletons:**
- Files: `src/f1d/shared/variables/_compustat_engine.py`, `src/f1d/shared/variables/_crsp_engine.py`, `src/f1d/shared/variables/_ibes_engine.py`
- Why fragile: Module-level singleton caching; if cache invalidation needed, difficult to reset; stateful in otherwise functional design
- Safe modification: Do not modify singleton patterns without understanding all panel builder dependencies
- Test coverage: Limited; singleton mocking can be complex

**Entity Linking Logic:**
- Files: `src/f1d/sample/link_entities.py` (1,292 lines)
- Why fragile: Complex 4-tier matching strategy (PERMNO+Date, CUSIP8+Date, Fuzzy Name, Ticker); many edge cases
- Safe modification: Any changes require full integration test run
- Test coverage: Has integration tests but edge cases may be under-tested

**LaTeX Table Generation:**
- Files: `src/f1d/shared/latex_tables.py` (553 lines), `src/f1d/shared/latex_tables_accounting.py`
- Why fragile: String concatenation for LaTeX; fragile to column changes, formatting requirements
- Safe modification: Test with actual LaTeX compilation
- Test coverage: Limited

## Scaling Limits

**Memory Usage:**
- Current capacity: Handled via chunked reading in `src/f1d/shared/chunked_reader.py`
- Limit: Large parquet files loaded entirely for some operations
- Scaling path: Increase chunk processing adoption; consider dask for very large datasets

**Fuzzy Matching:**
- Current capacity: ~11k unique companies matched in reasonable time
- Limit: O(n*m) complexity where n=companies, m=CCM names
- Scaling path: Use `rapidfuzz.process.extract` with batch processing; pre-filter candidates by industry

## Dependencies at Risk

**statsmodels (pinned to 0.14.6):**
- Risk: Version 0.14.0 introduced breaking changes (deprecated GLM link names); cannot upgrade freely
- Impact: Regression results may change with upgrade
- Migration plan: Test all regression scripts with newer version before upgrading; see DEPENDENCIES.md

**pyarrow (pinned to 21.0.0):**
- Risk: Version 23.0.0+ requires Python >= 3.10
- Impact: Python version constraints
- Migration plan: Update to Python 3.10+ for newer pyarrow; currently at Python 3.9 minimum

**linearmodels:**
- Risk: Import redefinition pattern `from linearmodels.panel import PanelOLS  # type: ignore[no-redef]`
- Impact: Type checking friction; potential runtime import issues
- Migration plan: Consolidate imports at module level; consider wrapper module

## Missing Critical Features

**No Test Coverage Gate:**
- Problem: Coverage threshold at 30% (target 40%); many modules have 0% coverage
- Blocks: Confidence in refactoring; regression detection
- Files affected: Most econometric scripts, variable builders, observability modules

**No Continuous Integration:**
- Problem: `.github/` directory exists but CI status unknown
- Blocks: Automated quality checks on pull requests

## Test Coverage Gaps

**Econometric Scripts:**
- What's not tested: Most `run_h*.py` scripts have limited direct unit tests
- Files: `src/f1d/econometric/run_*.py`
- Risk: Regression in statistical calculations could go undetected
- Priority: High (core thesis results)

**Observability Module:**
- What's not tested: `src/f1d/shared/observability/stats.py` (5,309 lines)
- Files: `src/f1d/shared/observability/*.py`
- Risk: Silent bugs in statistics reporting
- Priority: Medium (affects all reporting)

**Variable Builders:**
- What's not tested: Many individual variable builder modules in `src/f1d/shared/variables/`
- Files: `src/f1d/shared/variables/*.py` (50+ modules)
- Risk: Data quality issues in derived variables
- Priority: High (directly affects thesis variables)

**Legacy Code:**
- What's not tested: V1 scripts and `2_Scripts/` excluded from coverage
- Files: See pyproject.toml coverage omit patterns
- Risk: Cannot safely modify legacy code
- Priority: Low (legacy, scheduled for removal)

---

*Concerns audit: 2026-02-20*
