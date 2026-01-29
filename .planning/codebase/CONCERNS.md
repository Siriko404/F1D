# Codebase Concerns

**Analysis Date:** 2025-01-29

## Tech Debt

**Archive Proliferation:**
- Issue: Multiple archive directories (`___Archive`, `ARCHIVE`, `ARCHIVE_OLD`, `OLD`, `ARCHIVE_BROKEN_STEP2`, `ARCHIVE_BROKEN_STEP4`) with inconsistent naming conventions
- Files: `2_Scripts/___Archive/`, `2_Scripts/ARCHIVE/`, `2_Scripts/ARCHIVE_OLD/`, `3_Logs/OLD/`, `4_Outputs/OLD/`
- Impact: Navigation confusion, unclear what's safe to delete, potential for mixing archived/active code
- Fix approach: Consolidate to single `archive/` directory with timestamped subdirectories, document retention policy in README

**Hardcoded Timestamps in Verification Scripts:**
- Issue: `2_Scripts/ARCHIVE/ARCHIVE_BROKEN_STEP2/verify_extended.py:8` contains hardcoded path `2025-12-25_222300`
- Files: `2_Scripts/ARCHIVE/ARCHIVE_BROKEN_STEP2/verify_extended.py`
- Impact: Script breaks when run in different contexts, not reproducible
- Fix approach: Replace with dynamic resolution using `latest/` symlink or command-line argument

**Return None/Empty Pattern Overuse:**
- Issue: Multiple functions return `None`, `[]`, or `{}` on error paths without logging or raising exceptions
- Files: `2_Scripts/4_Econometric/4.2_LiquidityRegressions.py` (6 instances), `2_Scripts/4_Econometric/4.1.4_EstimateCeoTone.py` (2 instances), `2_Scripts/2_Text/2.1_TokenizeAndCount.py` (2 instances)
- Impact: Silent failures, difficult debugging, data may be incomplete without warning
- Fix approach: Replace with explicit exceptions (ValueError, DataValidationError) or logging warnings

**Large Script Files:**
- Issue: `3_Financial/3.2_MarketVariables.py` is 1,731 lines, violating single responsibility principle
- Files: `2_Scripts/3_Financial/3.2_MarketVariables.py` (1,731 lines)
- Impact: Difficult to navigate, test, and maintain; high cognitive load
- Fix approach: Extract market return computation, liquidity measures, and spread estimation into separate modules in `shared/`

## Known Bugs

**CSV Format Assumptions in Shared Utils:**
- Symptoms: Code assumes CSV format in some paths but pipeline primarily uses Parquet
- Files: `2_Scripts/3_Financial/3.4_Utils.py`, `2_Scripts/shared/regression_helpers.py`
- Trigger: Input files in unexpected format
- Workaround: Ensure all intermediate files are Parquet format
- Fix approach: Standardize on Parquet throughout, remove CSV reading code from shared utilities

**Unicode Compatibility on Windows (Historical):**
- Symptoms: Characters display incorrectly on Windows with cp1252 encoding
- Files: Recent commits indicate fixes in `2_Scripts/` (see git history 2025-01-24)
- Trigger: Windows console with non-UTF-8 default encoding
- Workaround: Set console encoding to UTF-8 before running scripts
- Fix approach: Recent commits addressed this; validate fix across all scripts

## Security Considerations

**Input Validation Gaps:**
- Risk: Malformed parquet files or path traversal attacks in user-provided paths
- Files: `2_Scripts/shared/path_utils.py`, `2_Scripts/shared/data_validation.py`
- Current mitigation: Basic path validation in `path_utils.py:63`, `path_utils.py:86`
- Recommendations:
  - Add schema validation for all Parquet inputs using PyArrow schema checks
  - Implement strict path sanitization (reject `../` in user paths)
  - Add file size checks to prevent memory exhaustion attacks

**Dependency Pinning:**
- Risk: Outdated dependencies may have known vulnerabilities (e.g., pandas==2.2.3, numpy==2.3.2)
- Files: `requirements.txt`
- Current mitigation: Explicit version pinning
- Recommendations:
  - Run `pip-audit` or `safety check` regularly
  - Automate dependency scanning in CI/CD
  - Document security upgrade process in DEPENDENCIES.md

## Performance Bottlenecks

**Sequential Year Processing in Financial Scripts:**
- Problem: `3_Financial/3.2_MarketVariables.py` processes years sequentially instead of parallel
- Files: `2_Scripts/3_Financial/3.2_MarketVariables.py`
- Cause: Single-threaded design despite `config/project.yaml` allowing `thread_count` configuration
- Improvement path: Implement parallel year processing using `concurrent.futures.ThreadPoolExecutor` with configurable thread count from YAML

**Non-Vectorized String Operations:**
- Problem: Entity linking in `1_Sample/1.2_LinkEntities.py` uses row-wise string matching
- Files: `2_Scripts/1_Sample/1.2_LinkEntities.py`, `2_Scripts/shared/string_matching.py`
- Cause: Iterative fuzzy matching instead of vectorized operations
- Improvement path: Use RapidFuzz's `process.cdist` for batch distance computation, or implement vectorized pandas string operations for Tier 1-2 matching

**Chunked Reader Without Progress Feedback:**
- Problem: `shared/chunked_reader.py` doesn't emit progress signals during long reads
- Files: `2_Scripts/shared/chunked_reader.py`
- Cause: Simple iterator design without callback hooks
- Improvement path: Add optional progress callback parameter, integrate with `observability_utils.py` memory monitoring

## Fragile Areas

**Entity Linking (Step 1.2):**
- Files: `2_Scripts/1_Sample/1.2_LinkEntities.py`, `2_Scripts/shared/string_matching.py`
- Why fragile: 4-tier matching strategy with hardcoded thresholds (92% default, 85% minimum), dependent on RapidFuzz availability (optional dependency)
- Safe modification:
  - Adjust thresholds via `config/project.yaml` only (currently hardcoded)
  - Add fallback to Tier 4 (ticker) when Tier 3 fuzzy matching unavailable
  - Validate match quality with post-linking audit (call count stability)
- Test coverage: `tests/unit/test_fuzzy_matching.py` (33 lines) - minimal coverage

**Regression Output Stability:**
- Files: `2_Scripts/4_Econometric/4.1_EstimateCeoClarity.py`, `4.2_LiquidityRegressions.py`, `4.3_TakeoverHazards.py`
- Why fragile: Depends on statsmodels 0.14.6 (pinned in requirements.txt), sensitive to algorithm changes, floating-point precision
- Safe modification:
  - Pin statsmodels version in requirements.txt (already done)
  - Add regression coefficient tolerance checks in tests
  - Set random seeds in survival analysis (lifelines)
- Test coverage: `tests/unit/test_regression_helpers.py` (695 lines) - good coverage, but lacks numerical stability tests

**Market Variable Calculation Windows:**
- Files: `2_Scripts/3_Financial/3.2_MarketVariables.py`
- Why fragile: Trading day windows (prev_call+5d to call-5d) assume sufficient data, minimum trading day thresholds may drop observations silently
- Safe modification:
  - Log warnings when windows are truncated
  - Add diagnostics for dropped observations
  - Validate against CRSP calendar (holiday handling)
- Test coverage: No integration tests for edge cases (earnings calls near trading halts, IPO dates)

## Scaling Limits

**Single-Threaded Tokenization:**
- Current capacity: ~300K transcripts processed in 2-3 minutes on single core
- Limit: CPU-bound tokenization in `2_Text/2.1_TokenizeAndCount.py` doesn't utilize multi-core systems
- Scaling path: Implement multiprocessing with shared memory for dictionary lookup, or migrate tokenization to C++ (already using C++17 compiler in config)

**Memory-Heavy Linguistic Variable Construction:**
- Current capacity: Designed for 8GB RAM minimum, 16GB recommended
- Limit: `2_Text/2.2_ConstructVariables.py` loads full-year datasets into memory
- Scaling path: Already has `shared/chunked_reader.py` infrastructure, but not used consistently; implement chunked aggregation with reduce operation

**Year-Based File Organization:**
- Current capacity: 17 years (2002-2018) of data
- Limit: Hardcoded year range assumptions in multiple scripts, assumes ~17 output files per step
- Scaling path: Refactor to use data-driven file discovery (glob patterns) instead of year iteration

## Dependencies at Risk

**statsmodels 0.14.6:**
- Risk: Pinned to specific version due to breaking changes in 0.14.0+ (deprecated GLM link names)
- Impact: Cannot upgrade statsmodels without refactoring regression code (`4_Econometric/`)
- Migration plan: See DEPENDENCIES.md; requires updating all `smf.ols()` calls to use new API, testing coefficient stability

**pyarrow 21.0.0:**
- Risk: Pinned for Python 3.8-3.13 compatibility; 23.0.0+ requires Python >= 3.10
- Impact: Missing out on performance improvements in newer pyarrow versions
- Migration plan: Upgrade minimum Python version to 3.10, update pin in requirements.txt, benchmark parquet read performance

**RapidFuzz (Optional):**
- Risk: Graceful degradation when missing, but Tier 3 entity linking silently disabled
- Impact: Lower entity match rates in `1_Sample/1.2_LinkEntities.py`
- Migration plan: Make RapidFuzz required rather than optional, add clear error message if unavailable

**lifelines 0.30.0:**
- Risk: Survival analysis library used in `4.3_TakeoverHazards.py` for Cox proportional hazards
- Impact: API changes in lifelines could break Fine-Gray competing risks models
- Migration plan: Pin version in requirements.txt (already done), add version compatibility checks in script

## Missing Critical Features

**Automated Data Validation Pipeline:**
- Problem: No automated validation that outputs match expected schemas and value ranges
- Blocks: Confidence in regression results, reproducibility guarantees
- Recommendations: Implement schema validation using PyArrow metadata, add value range checks for key variables (Uncertainty_pct should be 0-100, etc.)

**Incremental Processing Support:**
- Problem: Cannot re-run individual years without reprocessing entire pipeline
- Blocks: Efficient updates when new data arrives, iterative development
- Recommendations: Implement dependency tracking (e.g., using `luigi` or `make`), add skip-if-exists logic with checksum validation

**Comprehensive Logging Standardization:**
- Problem: Inconsistent logging patterns across scripts (some use print, some use logging module)
- Blocks: Production monitoring, debugging distributed runs
- Recommendations: Mandate `shared/observability_utils.py` usage across all scripts, add structured logging (JSON format) for log aggregation

## Test Coverage Gaps

**Untested E2E Pipeline Execution:**
- What's not tested: Full pipeline from `1.1_CleanMetadata.py` through `4.4_GenerateSummaryStats.py` with real data
- Files: `tests/integration/test_full_pipeline.py` exists but likely uses mock fixtures
- Risk: Integration failures between steps, data lineage breaks
- Priority: High - should validate each step's outputs can be consumed by next step

**Untested Edge Cases in Entity Linking:**
- What's not tested: Fuzzy matching with typos, abbreviations (Inc vs Incorporated), multi-word company names
- Files: `2_Scripts/1_Sample/1.2_LinkEntities.py`, `tests/unit/test_fuzzy_matching.py` (33 lines)
- Risk: Incorrect GVKEY assignments, biased sample
- Priority: High - entity linking is foundational to all downstream analysis

**Untested Error Recovery in Chunked Reading:**
- What's not tested: Behavior when Parquet files are corrupted, incomplete row groups, memory pressure during chunking
- Files: `2_Scripts/shared/chunked_reader.py`, `tests/unit/test_chunked_reader.py` (92 lines)
- Risk: Silent data loss, incomplete processing
- Priority: Medium - add fault injection tests

**Untested Windows-Specific Behaviors:**
- What's not tested: Symlink creation on Windows (requires admin), path length limits (260 char), case-insensitive filesystem issues
- Files: `2_Scripts/shared/symlink_utils.py`, tests no Windows-specific fixtures
- Risk: Pipeline fails on Windows environments despite README claiming Windows support
- Priority: Medium - document Windows limitations or add Windows CI

---

*Concerns audit: 2025-01-29*
