# Codebase Concerns

**Analysis Date:** 2026-02-21

## Tech Debt

**Large Utility Module:**
- Issue: `src/f1d/shared/observability/stats.py` is 5,309 lines, violating single-responsibility principle
- Files: `src/f1d/shared/observability/stats.py`
- Impact: Difficult to maintain, test, and understand; high cognitive load for developers
- Fix approach: Extract specialized modules (stats_aggregator.py, report_formatter.py, percentiles.py) with focused responsibilities

**Inefficient DataFrame Iteration:**
- Issue: 43 instances of `.iterrows()` usage across 19 files, which is extremely slow (creates Series for each row)
- Files: `src/f1d/sample/utils.py`, `src/f1d/reporting/generate_summary_stats.py`, `src/f1d/sample/link_entities.py`, `src/f1d/text/tokenize_transcripts.py`, `src/f1d/econometric/run_h0_*.py`, `src/f1d/econometric/run_h10_tone_at_top.py`, `src/f1d/shared/diagnostics.py`, `src/f1d/shared/financial_utils.py`, `src/f1d/shared/sample_utils.py`, `src/f1d/shared/iv_regression.py`, `src/f1d/shared/panel_ols.py`, `src/f1d/shared/reporting_utils.py`, `src/f1d/variables/build_h9_takeover_panel.py`
- Impact: Performance degradation (10-100x slower than vectorized operations), especially on large datasets
- Fix approach: Replace `.iterrows()` with vectorized pandas operations (melt, groupby, column-wise operations) or `.itertuples()` where row-by-row is truly necessary

**Legacy Path References:**
- Issue: Legacy directory structure paths (`inputs/`, `outputs/`) referenced in config and comments
- Files: `config/project.yaml`, `README.md`, multiple doc files
- Impact: Confusing for developers navigating codebase; potential confusion about actual vs documented structure
- Fix approach: Update all references to use new structure (`data/raw`, `data/interim`, `data/processed`, `results`)

## Known Bugs

**None Actively Reported:**
- No actively reported bugs found in current codebase
- Historical bugs documented in `_compustat_engine.py` comments with "red-team audit fixes" indicating they were addressed

## Security Considerations

**Subprocess Path Validation:**
- Risk: `subprocess.run()` used in `build_sample_manifest.py` without path validation
- Files: `src/f1d/sample/build_sample_manifest.py`
- Current mitigation: None present
- Recommendations: Add path validation to ensure subprocess executes only within allowed directories, validate absolute paths, check file extension is `.py`

**Environment Variable Validation:**
- Risk: `.env.example` exists but no schema validation for environment variables used in tests
- Files: `.env.example`, `tests/conftest.py`, `tests/factories/config.py`
- Current mitigation: None present in main codebase (only in tests)
- Recommendations: Add environment variable schema validation for future use (API timeouts, retry limits)

**Input Data Validation:**
- Risk: Scripts read Parquet/CSV files from `inputs/` without validating schemas, column types, or value ranges
- Files: All scripts that read from `inputs/` directories
- Current mitigation: Pandas error handling provides some validation but not comprehensive
- Recommendations: Add schema validation with column name, type, and value range checks for critical input files

## Performance Bottlenecks

**DataFrame Iteration with .iterrows():**
- Problem: 43 instances of `.iterrows()` across 19 files create Series objects for each row, extremely slow
- Files: Listed in Tech Debt section above
- Cause: Using iteration instead of vectorized pandas operations
- Improvement path: Replace with vectorized operations (melt, groupby, apply, column-wise) or `.itertuples()` where necessary

**Large File Processing:**
- Problem: Several scripts process large files without chunking or memory optimization
- Files: `src/f1d/text/tokenize_transcripts.py` (1,354 lines), `src/f1d/sample/link_entities.py` (1,292 lines)
- Cause: Monolithic scripts with single-pass processing
- Improvement path: Implement chunked processing with memory tracking, use `src/f1d/shared/chunked_reader.py` more consistently

**Sequential Year Processing:**
- Problem: Multiple scripts process years sequentially (2002-2018) without parallelization
- Files: `src/f1d/text/tokenize_transcripts.py`, `src/f1d/text/build_linguistic_variables.py`, multiple econometric scripts
- Cause: `thread_count: 1` in `config/project.yaml` enforces single-threaded execution for determinism
- Improvement path: Implement deterministic parallelization with sorted result combination, use `ProcessPoolExecutor` respecting config settings

## Fragile Areas

**Econometric Scripts with Hardcoded Values:**
- Files: `src/f1d/econometric/run_h0_*.py` scripts
- Why fragile: Multiple hypothesis test scripts have duplicated code patterns; changes require updates in multiple files
- Safe modification: Extract shared regression infrastructure from `run_h0_1_manager_clarity.py` and `run_h0_2_ceo_clarity.py` into reusable modules
- Test coverage: High (dedicated unit tests in `tests/unit/test_h*_regression.py`)

**Compustat Engine:**
- Files: `src/f1d/shared/variables/_compustat_engine.py` (1,099 lines)
- Why fragile: Complex financial calculations with multiple edge cases (EPS lag, Tobin's Q, winsorization, Q4-only variables); documented as having "red-team audit fixes"
- Safe modification: Keep the extensive audit comments as guidance; any changes require regression testing with `tests/unit/test_financial_utils.py`
- Test coverage: Moderate (unit tests exist for financial utilities)

**String Matching Thresholds:**
- Files: `config/project.yaml`, `src/f1d/sample/link_entities.py`
- Why fragile: Hardcoded thresholds (company name: 92.0 default, entity name: 85.0 min) that may need tuning
- Safe modification: Make thresholds configurable via YAML; document tuning process
- Test coverage: Low (no dedicated fuzzy matching tests beyond `tests/unit/test_fuzzy_matching.py`)

## Scaling Limits

**Memory Usage:**
- Current capacity: 16GB RAM minimum, 32GB recommended per README
- Limit: Large Parquet files (2-6MB each, ~100MB total) loaded entirely into memory
- Scaling path: Implement chunked processing with PyArrow dataset API, use memory throttling from `config/project.yaml.chunk_processing`

**CPU Utilization:**
- Current capacity: `thread_count: 1` enforced by config for determinism
- Limit: Sequential processing limits throughput on multi-core systems
- Scaling path: Implement deterministic parallelization (ProcessPoolExecutor) with sorted output combination

**Dataset Size:**
- Current capacity: 112,968 earnings call observations (2002-2018)
- Limit: Processing scales linearly with dataset size; current implementation handles current range
- Scaling path: No fundamental limits identified; extension to new years requires updating `config/project.yaml.data.year_start/end`

## Dependencies at Risk

**statsmodels Version:**
- Risk: Pinned to 0.14.6 to avoid breaking changes (deprecated GLM link names in 0.14.0+)
- Impact: Cannot upgrade without API validation and regression testing
- Migration plan: Documented in `docs/DEPENDENCIES.md`; requires testing new API and updating all regression code

**PyArrow Version:**
- Risk: Pinned to 21.0.0 (23.0.0+ requires Python >= 3.10, incompatible with target range 3.8-3.9)
- Impact: Stuck on older PyArrow for Python 3.8-3.9 support
- Migration plan: Documented in `docs/DEPENDENCIES.md`; upgrade requires Python 3.10+ or benchmarking performance

**linearmodels:**
- Risk: Optional dependency with graceful failure but critical for panel OLS and IV regression
- Impact: Scripts fail with ImportError if not available
- Migration plan: No alternative identified; linearmodels is de facto standard for panel econometrics

## Missing Critical Features

**Schema Validation Layer:**
- Problem: No comprehensive schema validation for input/output data files
- Blocks: Early detection of corrupted/malformed data, automated data contract enforcement
- Priority: High

**Automated Performance Profiling:**
- Problem: No built-in performance profiling or benchmarking infrastructure
- Blocks: Identification of new performance bottlenecks as codebase grows
- Priority: Medium

**Integration Tests for Full Pipeline:**
- Problem: Unit tests exist (63 files) but full end-to-end pipeline integration testing is limited
- Blocks: Verification that all stages work together with real data
- Priority: Medium (currently exists in `tests/verification/test_*_dryrun.py`)

## Test Coverage Gaps

**Untested Areas:**
- What's not tested: Monolithic scripts like `tokenize_transcripts.py` (1,354 lines), `link_entities.py` (1,292 lines), `generate_summary_stats.py` have limited unit test coverage
- Files: `src/f1d/text/tokenize_transcripts.py`, `src/f1d/sample/link_entities.py`, `src/f1d/reporting/generate_summary_stats.py`
- Risk: Regression bugs in complex scripts could go unnoticed
- Priority: High

**Econometric Output Consistency:**
- What's not tested: Cross-model consistency of fixed effects estimates across different samples
- Files: `tests/unit/test_h*_regression.py` test individual models but not cross-model consistency
- Risk: Inconsistencies between Main/Finance/Utility samples could go undetected
- Priority: Medium

**Observable State Tracking:**
- What's not tested: Pipeline state tracking and observability features
- Files: `src/f1d/shared/observability/*` modules have limited test coverage
- Risk: Anomaly detection and diagnostics could fail silently
- Priority: Low

---

*Concerns audit: 2026-02-21*
