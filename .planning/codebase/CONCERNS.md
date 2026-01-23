# Codebase Concerns

**Analysis Date:** 2026-01-22

## Tech Debt

**Code Duplication - DualWriter Class:**
- Issue: DualWriter logging class is duplicated in nearly every script (73 occurrences)
- Files: `2_Scripts/1_Sample/1.0_BuildSampleManifest.py`, `2_Scripts/1_Sample/1.2_LinkEntities.py`, `2_Scripts/1_Sample/1.3_BuildTenureMap.py`, `2_Scripts/2_Text/2.1_TokenizeAndCount.py`, `2_Scripts/2_Text/2.2_ConstructVariables.py`, `2_Scripts/3_Financial/3.0_BuildFinancialFeatures.py`, and all econometric scripts
- Impact: Maintenance burden - bug fixes need to be applied in multiple places. Violates DRY principle.
- Fix approach: Extract to shared utility module in `2_Scripts/shared/` and import across all scripts

**Code Duplication - Utility Functions:**
- Issue: Helper functions (compute_file_checksum, print_stat, analyze_missing_values, update_latest_symlink) duplicated across multiple scripts
- Files: Multiple scripts in 1_Sample/, 2_Text/, 3_Financial/, and 4_Econometric/ directories
- Impact: Code drift and maintenance overhead
- Fix approach: Consolidate into `2_Scripts/shared/pipeline_utils.py` and standardize imports

**Large Script Files:**
- Issue: 5 scripts over 880 lines suggesting complex, monolithic functions
- Files: `2_Scripts/4_Econometric/4.1_EstimateCeoClarity.py` (892 lines), `2_Scripts/4_Econometric/4.1.1_EstimateCeoClarity_CeoSpecific.py` (879 lines), `2_Scripts/4_Econometric/4.2_LiquidityRegressions.py` (934 lines), `2_Scripts/4_Econometric/4.3_TakeoverHazards.py` (889 lines), `2_Scripts/ARCHIVE_OLD/2.5_LinkCcmAndIndustries.py` (1134 lines)
- Impact: Reduced readability, harder to test, increased cognitive load
- Fix approach: Break into smaller focused modules with single responsibilities

**Inconsistent Error Handling:**
- Issue: 28+ instances of bare `except:` or `except Exception:` blocks, many with `pass` statements
- Files: `2_Scripts/1_Sample/1.2_LinkEntities.py:316-317`, `2_Scripts/2_Text/2.1_TokenizeAndCount.py:51-52`, `2_Scripts/4_Econometric/4.1.2_EstimateCeoClarity_Extended.py:701-702`, `2_Scripts/4_Econometric/4.2_LiquidityRegressions.py:888-889`
- Impact: Silent failures make debugging difficult. Errors are swallowed without logging or context.
- Fix approach: Replace with specific exception types, always log error context, re-raise or handle gracefully

## Known Bugs

**Silent Failures in Symlink Operations:**
- Issue: `update_latest_symlink()` function has broad exception catching with silent failure
- Files: `2_Scripts/2_Text/2.2_ConstructVariables.py:42-59`, `2_Scripts/1_Sample/1.5_Utils.py:99-126`, `2_Scripts/3_Financial/3.4_Utils.py:99-127`
- Symptoms: 'latest' directories may not be updated, users point to stale outputs without indication
- Trigger: Running on Windows without admin privileges for symlink creation
- Workaround: Check if 'latest' was actually updated after script completes
- Fix approach: Log explicit error message, exit with non-zero code if symlink/copy fails

**Optional Dependency Not Handled Gracefully:**
- Issue: rapidsuzz (fuzzy matching) import fails silently, but functionality is skipped
- Files: `2_Scripts/1_Sample/1.2_LinkEntities.py:59-65`
- Symptoms: Entity linking may have lower match rates without clear warning to user
- Trigger: rapidsuzz not installed in environment
- Workaround: Manually install rapidsuzz: `pip install rapidfuzz`
- Fix approach: Add to requirements.txt or provide clear error if Tier 3 fuzzy matching is needed

## Security Considerations

**Subprocess Execution Without Validation:**
- Issue: Orchestrator scripts use subprocess.run() with user-controlled paths
- Files: `2_Scripts/1_Sample/1.0_BuildSampleManifest.py:164-169`
- Risk: If script paths can be tampered with, could execute arbitrary code
- Current mitigation: Paths are hardcoded in orchestrator configuration
- Recommendations: Validate script paths are within expected directory, use absolute paths

**No Environment Variable Validation:**
- Issue: No validation of environment configuration or sensitive data access
- Files: Not found (no .env usage detected)
- Risk: WRDS credentials or API keys would be in plaintext if added later
- Recommendations: Implement environment variable schema validation if adding external services

**Missing Input Data Validation:**
- Issue: No schema validation on input Parquet/CSV files
- Files: All scripts that read from 1_Inputs/
- Risk: Malformed or poisoned data files could cause unexpected behavior
- Current mitigation: Files assumed to be from trusted WRDS sources
- Recommendations: Add data validation layer with column type and value range checks

## Performance Bottlenecks

**Inefficient DataFrame Iteration:**
- Issue: Multiple uses of `.iterrows()` which is slow for large datasets
- Files: `2_Scripts/1_Sample/1.2_LinkEntities.py:590`, `2_Scripts/1_Sample/1.3_BuildTenureMap.py:333`, `2_Scripts/3_Financial/3.1_FirmControls.py:459`, `2_Scripts/3_Financial/3.3_EventFlags.py:246`
- Problem: iterrows() creates Series for each row, ~100x slower than vectorized operations
- Improvement path: Use `.apply()`, `.itertuples()`, or vectorized pandas operations

**Sequential Processing of Years:**
- Issue: Loop through years sequentially without parallelization
- Files: `2_Scripts/2_Text/2.1_TokenizeAndCount.py`, `2_Scripts/3_Financial/3.1_FirmControls.py`
- Problem: Could process multiple years concurrently on multi-core systems
- Improvement path: Add multiprocessing with ProcessPoolExecutor, respect thread_count from config (currently pinned to 1 for determinism)

**Memory-Intensive Operations:**
- Issue: Loading full large Parquet files into memory (e.g., CRSP_DSF files)
- Files: `2_Scripts/3_Financial/3.2_MarketVariables.py` reads quarterly CRSP files
- Problem: High memory usage, could fail on systems with limited RAM
- Improvement path: Use PyArrow dataset API for streaming, or chunked processing

**Repeated Data Loading:**
- Issue: Same Parquet files read multiple times across scripts
- Files: Input files in 1_Inputs/ read by multiple steps
- Problem: I/O overhead repeated across pipeline stages
- Improvement path: Cache intermediate results, or implement lazy loading with duckdb/pyarrow

## Fragile Areas

**Output Path Dependencies:**
- Files: All scripts that use `get_latest_output_dir()` or expect `latest/` symlinks
- Why fragile: Script output depends on previous steps creating 'latest' correctly. If a step fails to update 'latest', downstream steps read stale data silently.
- Safe modification: Always validate 'latest' points to expected timestamp before use
- Test coverage: No automated tests validate 'latest' symlink correctness

**Data Assumptions - Fixed Effects Regression:**
- Files: `2_Scripts/4_Econometric/4.1_EstimateCeoClarity.py`, `2_Scripts/4_Econometric/4.1.1_EstimateCeoClarity_CeoSpecific.py`, `2_Scripts/4_Econometric/4.1.2_EstimateCeoClarity_Extended.py`
- Why fragile: Assumes specific column names and data structure in input files. Changes upstream break regressions.
- Safe modification: Add data validation before regression runs, check for required columns
- Test coverage: Only manual verification of regression outputs

**String Matching Logic:**
- Files: `2_Scripts/1_Sample/1.2_LinkEntities.py` (tier 3 fuzzy matching), `2_Scripts/2_Text/2.2_ConstructVariables.py` (CEO name matching)
- Why fragile: Fuzzy matching thresholds and heuristics are magic numbers. Slight data changes affect match rates significantly.
- Safe modification: Parameterize thresholds in config/project.yaml, document expected match rates
- Test coverage: No automated tests for matching accuracy or edge cases

**Windows Symlink Fallback:**
- Files: Multiple `update_latest_symlink()` implementations
- Why fragile: Symlink creation requires admin rights on Windows. Fallback to copytree works but doubles disk space for 'latest'.
- Safe modification: Use junctions on Windows, add user warning if using copy fallback
- Test coverage: Not tested on non-Windows platforms

## Scaling Limits

**Single-Threaded Processing:**
- Current capacity: thread_count=1 pinned in config for determinism
- Limit: Cannot leverage multi-core CPUs, processing time grows linearly with dataset size
- Scaling path: Implement deterministic parallelization with seed propagation, or accept parallelism for non-critical steps

**Disk I/O Bottleneck:**
- Current capacity: Sequential reads from 2.5 GB of speaker data parquet files
- Limit: Limited by disk read speed for large-scale processing (e.g., expanding to 2024+ data)
- Scaling path: Use column pruning with pyarrow, compress intermediate parquet files

**Memory Requirements:**
- Current capacity: Assumes typical research workstation (8-16GB RAM)
- Limit: Loading full-year Parquet files simultaneously could exceed memory on smaller systems
- Scaling path: Implement chunked processing, add memory usage monitoring

## Dependencies at Risk

**Statsmodels Version Compatibility:**
- Risk: statsmodels 0.14.5 may have API changes in future versions
- Impact: Regression models could break or produce different results
- Migration plan: Pin exact version in requirements.txt (already done), test on minor version upgrades

**PyArrow Performance Degradation:**
- Risk: pyarrow 21.0.0 may have performance regressions in newer versions
- Impact: Parquet read/write speed could slow down significantly
- Migration plan: Benchmark newer pyarrow versions before upgrading

**Python 3.13 Compatibility:**
- Risk: Some packages (e.g., numpy 2.x) have breaking changes
- Impact: Pipeline may fail on different Python versions
- Migration plan: Test pipeline on Python 3.8-3.13, document supported versions

**rapidsuzz Optional Dependency:**
- Risk: Tier 3 fuzzy matching depends on rapidfuzz which is not in requirements.txt
- Impact: If rapidfuzz unavailable, entity linking loses Tier 3 matches reducing match rate
- Migration plan: Add to requirements.txt or make Tier 3 optional with clear documentation

## Missing Critical Features

**No Automated Testing:**
- Problem: No pytest or unittest framework found. Only manual validation scripts like `2.3_VerifyStep2.py`
- Blocks: Cannot catch regressions automatically, CI/CD not possible
- Impact: High - changes can break pipeline silently

**No Data Schema Validation:**
- Problem: Input data files not validated against expected schemas
- Blocks: Cannot detect malformed inputs early in pipeline
- Impact: Medium - could cause cryptic errors downstream

**No Data Quality Reports:**
- Problem: No comprehensive data quality checks (outliers, distributions, consistency)
- Blocks: Cannot detect data drift or anomalies in new data
- Impact: Medium - research results could be based on bad data

**No Pipeline State Tracking:**
- Problem: No mechanism to track which steps have been run successfully
- Blocks: Cannot resume from failures, must re-run entire pipeline
- Impact: Low - manageable for small pipeline but becomes painful as it grows

**No Configuration Validation:**
- Problem: `config/project.yaml` not validated against schema
- Blocks: Typos in config could cause silent misconfigurations
- Impact: Medium - could lead to incorrect results without error

## Test Coverage Gaps

**Missing Unit Tests:**
- What's not tested: Individual functions (e.g., fuzzy matching, tenure calculation, regression models)
- Files: All scripts in 2_Scripts/
- Risk: Bugs in helper functions go undetected until manual discovery
- Priority: High

**Missing Integration Tests:**
- What's not tested: End-to-end pipeline execution from raw inputs to final outputs
- Files: Pipeline orchestrators (`1.0_BuildSampleManifest.py`, `3.0_BuildFinancialFeatures.py`)
- Risk: Changes in one step break downstream steps
- Priority: High

**Missing Regression Tests:**
- What's not tested: Validation that outputs remain identical for same inputs
- Files: All output-generating scripts
- Risk: Code changes unintentionally alter results
- Priority: Medium

**Missing Data Validation Tests:**
- What's not tested: Input data conforms to expected schemas
- Files: All scripts reading from 1_Inputs/
- Risk: Bad data causes pipeline failures or silent corruption
- Priority: Medium

**Missing Edge Case Tests:**
- What's not tested: Empty datasets, single-row dataframes, all-null columns, duplicate keys
- Files: Data processing scripts
- Risk: Pipeline crashes on edge cases
- Priority: Low

---

*Concerns audit: 2026-01-22*
