# Codebase Concerns

**Analysis Date:** 2026-02-14

## Tech Debt

**Code Duplication:**
- Issue: Inline utility functions duplicated across ~90 scripts (DualWriter, checksum, print_stat, etc.)
- Files: `src/f1d/financial/v1/*`, `src/f1d/econometric/v1/*`, `src/f1d/sample/*`, `src/f1d/text/*`
- Impact: Inconsistent behavior, difficult maintenance, 60,800+ lines of redundant code
- Fix approach: Extract all utilities to `f1d.shared.*` modules and update imports

**Large Files:**
- Issue: Multiple files exceed 1,000 lines, reducing maintainability
- Files:
  - `src/f1d/shared/observability/stats.py` (5,304 lines)
  - `src/f1d/econometric/v2/4.4_H4_LeverageDiscipline.py` (1,770 lines)
  - `src/f1d/financial/v2/3.2_H2Variables.py` (1,695 lines)
  - `src/f1d/econometric/v2/4.6_H6CCCLRegression.py` (1,478 lines)
  - `src/f1d/financial/v2/3.13_H9_AbnormalInvestment.py` (1,359 lines)
  - `src/f1d/text/tokenize_and_count.py` (1,350 lines)
- Impact: Difficult to understand, test, and modify
- Fix approach: Break into smaller focused modules (under 500 lines each)

**Unused Code:**
- Issue: Dead code detected by vulture linter
- Files: `src/f1d/sample/1.0_BuildSampleManifest.py`, `src/f1d/sample/1.1_CleanMetadata.py`, `src/f1d/sample/1.2_LinkEntities.py`, `src/f1d/econometric/v1/4.3_TakeoverHazards.py`, `src/f1d/shared/centering.py`, `src/f1d/shared/industry_utils.py`, `src/f1d/shared/iv_regression.py`, `src/f1d/shared/observability/stats.py`, `src/f1d/shared/sample_utils.py`
- Impact: Codebase bloat, confusion about what is actually used
- Fix approach: Remove unused imports and variables

**Type Safety:**
- Issue: 50+ mypy errors remaining across codebase
- Files: `src/f1d/shared/*`, `src/f1d/regression_utils.py`, `src/f1d/env_validation.py`, `src/f1d/data_validation.py`
- Impact: Runtime type errors, reduced IDE support
- Fix approach: Fix type annotations, add proper TypedDict definitions, install missing type stubs

## Known Bugs

**Silent Symlink Failures:**
- Symptoms: `update_latest_symlink()` fails silently on Windows with only warning printed
- Files: `src/f1d/financial/v2/3.8_H8TakeoverVariables.py:854-867`
- Trigger: Creating symlinks on Windows systems
- Workaround: None - function fails without raising exception
- Impact: "latest" directory may not be updated, causing downstream scripts to read stale data
- Fix approach: Add proper error handling with sys.exit(1) or raise exception, implement Windows directory fallback

**RapidFuzz Optional Dependency:**
- Symptoms: Fuzzy matching silently disabled if rapidfuzz not installed, reducing match rates
- Files: `src/f1d/shared/string_matching.py:28-36`, `src/f1d/sample/1.2_LinkEntities.py:574-575`
- Trigger: Missing `rapidfuzz>=3.14.0` in requirements
- Workaround: Install manually: `pip install rapidfuzz>=3.14.0`
- Impact: Tier 3 entity matching skipped, ~5-10% lower entity match rates
- Fix approach: Either make rapidfuzz required or document clear warning with performance impact

## Security Considerations

**Subprocess Path Validation:**
- Risk: Subprocess execution may allow path traversal if paths are not validated
- Files: `src/f1d/sample/1.0_BuildSampleManifest.py:235-240`, `src/f1d/financial/v1/3.0_BuildFinancialFeatures.py:122-128`, `src/f1d/econometric/v2/*` (12+ files)
- Current mitigation: `src/f1d/shared/subprocess_validation.py` provides validation but not used consistently
- Recommendations:
  - Use `validate_script_path()` from `subprocess_validation.py` in all subprocess calls
  - Ensure all script paths are validated against allowed directories before execution
  - Add input validation for user-provided paths

**Environment Variable Handling:**
- Risk: Environment variables read without validation for sensitive operations
- Files: `src/f1d/shared/env_validation.py`, `.env.example`
- Current mitigation: Schema defined in `ENV_SCHEMA` but not enforced for all operations
- Recommendations:
  - Enforce env var validation before use in production code
  - Document required vs optional variables clearly
  - Add secrets management for WRDS credentials (currently in comments)

**Data Input Validation:**
- Risk: Malformed or malicious input data could cause unexpected behavior
- Files: `src/f1d/shared/data_validation.py`
- Current mitigation: Schema validation defined for only 2 files (Unified-info.parquet, LM dictionary)
- Recommendations:
  - Add schema validation for all input files (Compustat, CRSP, CCM, SDC, IBES)
  - Enable strict mode by default in production

## Performance Bottlenecks

**Row Iteration:**
- Problem: 40+ instances of `.iterrows()` used instead of vectorized operations
- Files: `src/f1d/sample/1.2_LinkEntities.py:605,617`, `src/f1d/sample/1.3_BuildTenureMap.py:646`, `src/f1d/financial/v1/3.4_Utils.py:50`, `src/f1d/shared/diagnostics.py:345`, `src/f1d/financial/v1/3.3_EventFlags.py:315,332`, `src/f1d/econometric/v1/4.1.1_EstimateCeoClarity_CeoSpecific.py:605,617,748,755`, `src/f1d/shared/financial_utils.py:157`, `src/f1d/shared/iv_regression.py:535`, `src/f1d/shared/panel_ols.py:187`, `src/f1d/econometric/v1/4.4_GenerateSummaryStats.py:543,589,629,656,678`, `src/f1d/shared/reporting_utils.py:76`, `src/f1d/shared/observability/stats.py:1131,1153,1211,1238,1304,1869,1894,1927,1980,2490,2510,2539`, `src/f1d/financial/v2/3.1_H1Variables.py:344`, `src/f1d/financial/v2/3.3_H3Variables.py:340,430,496,578,668`, `src/f1d/financial/v2/3.12_H9_PRiskFY.py:430`, `src/f1d/financial/v2/3.2_H2Variables.py:662`
- Cause: Iterative row-by-row processing instead of vectorized pandas operations
- Improvement path: Replace `.iterrows()` with vectorized operations, `.apply()`, or `.loc[]` filtering

**Sequential Year Processing:**
- Problem: Year loops processed sequentially despite `config['thread_count'] = 1` setting
- Files: `src/f1d/financial/v1/3.1_FirmControls.py:775-780`, `src/f1d/text/tokenize_and_count.py`, `src/f1d/econometric/v2/*`
- Cause: No parallelization despite config setting
- Improvement path: Implement `concurrent.futures` for year-level parallelization with deterministic ordering

**Memory-Intensive Operations:**
- Problem: Large DataFrames loaded entirely into memory without chunking
- Files: `src/f1d/text/tokenize_and_count.py`, `src/f1d/sample/1.2_LinkEntities.py`
- Cause: `pd.read_parquet()` loads entire file, no chunking for large datasets
- Improvement path: Use `MemoryAwareThrottler` from `chunked_reader.py` for incremental processing

**Lambda Functions in Group Operations:**
- Problem: `.apply(lambda)` used in groupby operations
- Files: `src/f1d/financial/v1/3.1_FirmControls.py:444`, `src/f1d/text/tokenize_and_count.py:918,1014`
- Cause: Lambda functions slower than vectorized methods
- Improvement path: Replace with `.transform()` or pre-defined functions

## Fragile Areas

**Entity Linking Pipeline:**
- Files: `src/f1d/sample/1.2_LinkEntities.py` (1,285 lines)
- Why fragile: Complex 3-tier matching strategy, fuzzy matching sensitive to threshold, dedup-index pattern assumes specific data structure
- Safe modification: Add comprehensive logging at each tier, validate match quality statistics, add unit tests for each tier
- Test coverage: Limited - only integration tests, no unit tests for fuzzy matching logic

**Tenure Map Construction:**
- Files: `src/f1d/sample/1.3_BuildTenureMap.py`
- Why fragile: Date handling complexity, episode construction assumptions about Execucomp data structure, multiple `.iloc[]` operations
- Safe modification: Add date range validation, verify episode continuity, add tests for edge cases (overlapping tenures, missing dates)
- Test coverage: Partial - basic tests exist

**Financial Variable Computation:**
- Files: `src/f1d/financial/v2/3.1_H1Variables.py`, `src/f1d/financial/v2/3.2_H2Variables.py`, `src/f1d/financial/v2/3.3_H3Variables.py`
- Why fragile: Complex variable calculations dependent on merge results, missing value handling not consistent across variables
- Safe modification: Standardize missing value handling, add validation for output ranges, add regression tests
- Test coverage: V2 scripts have unit tests but coverage unknown

**Regression Models:**
- Files: `src/f1d/econometric/v2/4.*_H*Regression.py` (9 files, 1,000+ lines each)
- Why fragile: Model specifications hardcoded, fixed effects handling varies by script, results parsing depends on statsmodels output format
- Safe modification: Use shared regression utilities, add model specification validation, add unit tests for coefficient extraction
- Test coverage: Unit tests exist for each H script but may not cover edge cases

**TODO Tracking:**
- Issue: Winsorized column tracking not implemented (commented as TODO)
- Files: `src/f1d/financial/v1/3.1_FirmControls.py:770`
- Impact: Cannot verify which columns were winsorized, affects reproducibility
- Fix approach: Track actual winsorized columns and log to stats.json

## Scaling Limits

**Year Range Hardcoded:**
- Current capacity: Fixed range 2002-2018
- Limit: Cannot process data outside this range without modifying multiple scripts
- Scaling path: Make year range fully configurable via `config/project.yaml`, remove hardcoded year loops

**Memory Constraints:**
- Current capacity: 80% max memory percent configured but no actual throttling
- Files: `src/f1d/shared/chunked_reader.py`, `config/project.yaml`
- Limit: Large datasets may cause OOM on systems with <16GB RAM
- Scaling path: Implement actual `MemoryAwareThrottler` usage in all scripts, add memory monitoring alerts

**Thread Count Configured but Unused:**
- Current capacity: `config['thread_count'] = 1` but parallelization not implemented
- Limit: Cannot leverage multi-core systems
- Scaling path: Implement concurrent year processing with deterministic results (seeded random, ordered results)

**Subprocess Dependency Chain:**
- Current capacity: Linear script execution via subprocess calls
- Limit: Cannot parallelize independent script steps
- Scaling path: Implement directed acyclic graph (DAG) execution engine with dependency tracking

## Dependencies at Risk

**statsmodels Pinning:**
- Risk: Pinned to 0.14.6 due to breaking changes in 0.14.0
- Files: `requirements.txt:10-11`
- Impact: Cannot upgrade to newer versions with potential bug fixes
- Migration plan: Document regression results with 0.14.6, test 0.15.0+ migration, update GLM link names

**PyArrow Version Pinning:**
- Risk: Pinned to 21.0.0 for Python 3.8-3.13 compatibility
- Files: `requirements.txt:17-18`
- Impact: Missing performance improvements and features in 23.0.0+
- Migration plan: Test Python 3.10+ with PyArrow 23.0.0+, document version compatibility matrix

**sklearn Type Stubs Missing:**
- Risk: sklearn lacks `py.typed` marker, mypy cannot verify sklearn imports
- Files: `src/f1d/text/tokenize_and_count.py:57`, 40+ type: ignore comments
- Impact: Type errors go undetected in sklearn usage
- Migration plan: Wait for sklearn to add type stubs, or install `types-scikit-learn` community stubs

**lifelines Type Stubs Missing:**
- Risk: lifelines lacks official type stubs
- Files: `src/f1d/econometric/v1/4.3_TakeoverHazards.py:62`, multiple type: ignore comments
- Impact: Type errors go undetected in survival analysis code
- Migration plan: Contribute type stubs to lifelines repo or create local stubs in `src/f1d/stubs/`

## Missing Critical Features

**Incremental Output Updates:**
- Problem: Cannot resume failed pipeline from intermediate step
- Blocks: Long-running pipelines must restart from beginning if any step fails
- Priority: Medium

**Data Versioning:**
- Problem: No data version tracking beyond timestamps
- Blocks: Cannot reproduce exact outputs from specific pipeline versions
- Priority: Low

**Comprehensive Schema Validation:**
- Problem: Only 2 input files have schema validation defined
- Blocks: Cannot detect malformed input data early in pipeline
- Priority: High (security concern)

## Test Coverage Gaps

**Entity Linking Logic:**
- What's not tested: Tier 3 fuzzy matching edge cases, threshold sensitivity, company name normalization
- Files: `src/f1d/sample/1.2_LinkEntities.py`
- Risk: Entity matching failures go undetected, data quality issues propagate downstream
- Priority: High

**Financial Calculations:**
- What's not tested: Winsorization logic, EPS growth calculation with edge cases, missing value handling in merges
- Files: `src/f1d/financial/v1/3.1_FirmControls.py`, `src/f1d/financial/v1/3.2_MarketVariables.py`
- Risk: Incorrect financial metrics affect all downstream analysis
- Priority: High

**Regression Output Parsing:**
- What's not tested: Coefficient extraction from statsmodels, standard error calculation, p-value formatting
- Files: `src/f1d/econometric/v2/4.*_H*Regression.py`
- Risk: Incorrect coefficients invalidate research findings
- Priority: High

**Survival Analysis Models:**
- What's not tested: CoxPHFitter convergence edge cases, Fine-Gray competing risks calculation
- Files: `src/f1d/econometric/v1/4.3_TakeoverHazards.py`
- Risk: Incorrect hazard ratios affect takeover analysis
- Priority: Medium

**Data Pipeline End-to-End:**
- What's not tested: Full pipeline from raw inputs to final outputs, error propagation across steps
- Files: Integration tests exist but limited scope
- Risk: Pipeline failures may not be caught until production
- Priority: Medium

---

*Concerns audit: 2026-02-14*
