# Codebase Concerns

**Analysis Date:** 2026-02-10

## Tech Debt

**H7-H8 Data Pipeline Issue:**
- Issue: Volatility and StockRet control variables are 100% missing for years 2005-2018 in H7_Illiquidity.parquet, causing H8 to silently truncate to 2002-2004 data only
- Files: `2_Scripts/3_Financial_V2/3.7_H7IlliquidityVariables.py`, `2_Scripts/3_Financial_V2/3.8_H8TakeoverVariables.py`
- Impact: H7 and H8 V2 results cannot replicate V1 sample sizes (39,408 -> 12,408 rows), invalidating cross-version comparisons
- Fix approach: Calculate Volatility directly from CRSP daily returns within H7 script instead of relying on incomplete external market_variables files

**Legacy Backup Files:**
- Issue: Backup files left in source directories create confusion about what's current
- Files: `2_Scripts/1_Sample/1.0_BuildSampleManifest-legacy.py`, `2_Scripts/3_Financial_V2/3.7_H7IlliquidityVariables.py.bak`
- Impact: Risk of accidentally editing wrong file; unclear which version is authoritative
- Fix approach: Move all `*-legacy.py`, `*.bak`, `*_old.py` files to `.___archive/` directory

**Mixed V1/V2 Directory Convention:**
- Issue: Three parallel financial directories (`3_Financial`, `3_Financial_V2`, `3_Financial_V3`) with unclear ownership
- Files: `2_Scripts/3_Financial/`, `2_Scripts/3_Financial_V2/`, `2_Scripts/3_Financial_V3/`
- Impact: Developers uncertain which version to modify; risk of V3 being another parallel implementation instead of consolidation
- Fix approach: Document V3 purpose (H9-specific only) and enforce V2 as primary; archive V1 scripts

**Large Single-File Utilities:**
- Issue: `observability_utils.py` is 4,652 lines - monolithic file mixing concerns (logging, stats, checksums, memory tracking)
- Files: `2_Scripts/shared/observability_utils.py`
- Impact: Difficult to navigate, test, and maintain; high merge conflict risk
- Fix approach: Split into focused modules: `logging_utils.py`, `stats_utils.py`, `checksum_utils.py`, `memory_utils.py`

**Inefficient DataFrame Operations:**
- Issue: Multiple scripts use `df.loc[update_df.index, col] = update_df[col]` pattern for bulk updates
- Files: `2_Scripts/1_Sample/1.2_LinkEntities.py`, `2_Scripts/3_Financial_V2/3.2_H2Variables.py`
- Impact: Slow on large datasets; pandas SettingWithCopyWarning risk
- Fix approach: Use `pd.merge()` with `how='left'` or `df.update()` for bulk column updates

## Known Bugs

**Silent Data Truncation in H8:**
- Symptoms: H8 produces 12,408 observations across 2002-2004 instead of expected 39,408 across 2002-2018 with no explicit error
- Files: `2_Scripts/3_Financial_V2/3.8_H8TakeoverVariables.py` (lines 550-556)
- Trigger: Missing control variable filtering (`n_missing_controls <= max_missing`) drops all rows with >20% missing data
- Workaround: The `.planning/debug/h7-h8-v2-sample-size-bug.md` documents fix approach (calculate Volatility inline in H7)

**Empty DataFrame Returns:**
- Symptoms: 100+ functions return empty dicts/None/DataFrames on error paths instead of raising exceptions
- Files: `2_Scripts/shared/financial_utils.py`, `2_Scripts/3_Financial_V2/*.py`, `2_Scripts/4_Econometric_V2/*.py`
- Trigger: Data validation failures propagate as empty containers
- Workaround: Downstream scripts check for empty returns but error messages are lost

**Division by Zero Guards:**
- Symptoms: Multiple functions return 0.0 for `duration_seconds <= 0` to avoid division by zero
- Files: `2_Scripts/2_Text/2.1_TokenizeAndCount.py` (line 575), `2_Scripts/2_Text/2.2_ConstructVariables.py` (line 216)
- Trigger: Invalid duration calculations from transcript timestamps
- Workaround: Graceful degradation to 0.0 masks underlying data quality issues

## Security Considerations

**Subprocess Calls Without Input Validation:**
- Risk: subprocess.run() calls don't validate file paths before execution
- Files: `2_Scripts/shared/iv_regression.py`, `2_Scripts/shared/panel_ols.py`
- Current mitigation: No shell=True usage reduces injection risk
- Recommendations: Add path validation via `validate_input_file()` before subprocess calls

**CSV File Parsing:**
- Risk: `pd.read_csv()` calls without explicit encoding or size limits
- Files: `2_Scripts/2_Text/2.1_TokenizeAndCount.py` (line 695), `2_Scripts/shared/regression_helpers.py` (line 58)
- Current mitigation: All CSV reads are from trusted data directories
- Recommendations: Add `encoding='utf-8'` and `max_rows` guards for external dictionary files

## Performance Bottlenecks

**Chunked Processing Without Proper Consolidation:**
- Problem: Scripts process data in chunks but don't always optimize consolidation frequency
- Files: `2_Scripts/3_Financial_V2/3.2_H2Variables.py` (lines 510-570), `2_Scripts/shared/chunked_reader.py`
- Cause: Fixed chunk_size=1000 may not be optimal for all dataset sizes
- Improvement path: Make chunk_size configurable via project.yaml and benchmark optimal values per step

**Excessive pd.concat() Calls:**
- Problem: 60+ instances of `pd.concat(..., ignore_index=True)` create memory pressure
- Files: All regression scripts, variable construction scripts
- Cause: Incremental DataFrame building pattern
- Improvement path: Pre-allocate DataFrame with known size when possible, or use list-of-dicts aggregation then single concat

**Duplicate Computations in Rolling Windows:**
- Problem: `3_Financial_V2/3.2_H2Variables.py` computes rolling windows per-firm without vectorization
- Files: `2_Scripts/3_Financial_V2/3.2_H2Variables.py` (lines 517-543)
- Cause: Loop-based `groupby("gvkey")` with rolling operations
- Improvement path: Use pandas `.groupby().rolling()` with `transform()` for vectorized computation

## Fragile Areas

**String Matching Thresholds:**
- Files: `2_Scripts/shared/string_matching.py`, `2_Scripts/1_Sample/1.2_LinkEntities.py`
- Why fragile: Entity matching success rate depends on hardcoded similarity thresholds (default: 92)
- Safe modification: Threshold values are now config-driven via `config/project.yaml`, not hardcoded in code
- Test coverage: Unit tests in `tests/unit/test_fuzzy_matching.py` cover threshold variations

**Regression Specification:**
- Files: `2_Scripts/shared/panel_ols.py`, `2_Scripts/4_Econometric_V2/*.py`
- Why fragile: Panel OLS requires exact column names and data types; multicollinearity can silently drop variables
- Safe modification: Always run `check_multicollinearity()` before `run_panel_ols()`; review VIF warnings
- Test coverage: Integration tests verify regression output structure but not coefficient stability

**Path Resolution:**
- Files: `2_Scripts/shared/path_utils.py`, all scripts using `get_latest_output_dir()`
- Why fragile: Timestamp-based path resolution fails if output directories have non-timestamp names
- Safe modification: All scripts now use `get_latest_output_dir()` instead of hardcoded `/latest/` symlinks (Phase 27 complete)
- Test coverage: `tests/unit/test_data_validation.py` covers path validation

**Year Range Filtering:**
- Files: All financial variable construction scripts
- Why fragile: Year_range inconsistencies between steps cause sample size mismatches
- Safe modification: Centralize year_range in `config/project.yaml` and validate at script startup
- Test coverage: No automated tests; manual verification via Phase 54 implementation audits

## Scaling Limits

**Memory Usage:**
- Current capacity: Scripts handle 40K-80K observation datasets comfortably on 16GB RAM
- Limit: Large transcript files (all years) may exceed memory if loaded without chunking
- Scaling path: All scripts use `chunked_reader.py` or Parquet column selection; document in README

**CRSP Daily Data Processing:**
- Current capacity: H7/H8 process CRSP daily stock data in chunks (see `chunked_reader.py`)
- Limit: Full CRSP history (1926-present) would require incremental processing redesign
- Scaling path: Current year_range=2002-2018 is manageable; document constraint

**Null Result Reproducibility:**
- Current capacity: Can replicate all 9 hypotheses with identical null results
- Limit: No framework for detecting if null results are due to implementation bugs vs genuine effects
- Scaling path: Phase 54-55 implementation audits validate specification correctness

## Dependencies at Risk

**statsmodels 0.14.6:**
- Risk: 0.14.0 introduced breaking GLM link name changes; future versions may deprecate features
- Impact: All regression scripts depend on statsmodels OLS/IV functions
- Migration plan: Documented in `.___archive/docs/DEPENDENCIES.md` - requires API validation testing before upgrade

**PyArrow 21.0.0:**
- Risk: 23.0.0+ requires Python >= 3.10 (incompatible with target 3.8-3.13 range)
- Impact: All Parquet I/O operations; upgrade would require dropping Python 3.8 support
- Migration plan: `DEPENDENCIES.md` notes performance testing required; 21.0.0 supports target Python range

**linearmodels (unpinned):**
- Risk: No version specified in requirements.txt; PanelOLS API changes could break regressions
- Impact: `shared/panel_ols.py`, all econometric scripts (H1-H9)
- Migration plan: Pin to tested version (likely 5.x series) and add to requirements.txt

**numpy 2.3.2:**
- Risk: numpy 2.x API has breaking changes from 1.x; Python 3.8 requires numpy<2
- Impact: All numerical computing
- Migration plan: Conditional requirement: `numpy<2` for Python 3.8, `numpy>=2` for Python 3.9+

## Missing Critical Features

**Automated Regression Coefficient Validation:**
- Problem: No automated checks that regression results are numerically stable across runs
- Blocks: Confidence that code changes don't subtly alter results
- Priority: Medium - manual verification via Phase 54-55 audits

**Data Freshness Monitoring:**
- Problem: No automated detection of stale intermediate outputs (e.g., if inputs change but outputs don't rebuild)
- Blocks: Reproducibility guarantees for incremental pipeline runs
- Priority: Low - current timestamp-based output directories prevent overwrites

**End-to-End Pipeline Test:**
- Problem: No single script runs entire pipeline and validates all outputs
- Blocks: Quick validation that all steps work together after changes
- Priority: Medium - `tests/integration/test_full_pipeline.py` exists but may not be comprehensive

## Test Coverage Gaps

**Econometric Model Outputs:**
- What's not tested: Numerical stability of regression coefficients, VIF calculations, FDR corrections
- Files: `2_Scripts/4_Econometric_V2/*.py`, `2_Scripts/shared/panel_ols.py`
- Risk: Implementation bugs could produce misleading results without detection
- Priority: High - add golden file tests for regression outputs (documented in Phase 54)

**Text Processing Pipeline:**
- What's not tested: Tokenization correctness, variable construction from transcripts, edge cases (empty transcripts)
- Files: `2_Scripts/2_Text/2.1_TokenizeAndCount.py`, `2_Scripts/2_Text/2.2_ConstructVariables.py`
- Risk: Silent data quality issues propagate to regressions
- Priority: Medium - existing tests cover paths/validators but not content correctness

**Entity Linking:**
- What's not tested: Fuzzy match quality, CUSIP/ticker linking accuracy
- Files: `2_Scripts/1_Sample/1.2_LinkEntities.py`
- Risk: Low match rates reduce sample size
- Priority: Low - `tests/unit/test_fuzzy_matching.py` tests threshold logic but not real data

**Financial Variable Construction:**
- What's not tested: Correctness of Compustat/CRSP calculations (ROA, leverage, market cap, illiquidity)
- Files: `2_Scripts/3_Financial_V2/*.py`, `2_Scripts/3_Financial_V3/*.py`
- Risk: Calculation errors could invalidate all regression results
- Priority: High - manually validated via Phase 54-55 audits but no automated tests

---

*Concerns audit: 2026-02-10*
