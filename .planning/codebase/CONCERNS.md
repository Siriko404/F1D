# Codebase Concerns

**Analysis Date:** 2026-02-14

## Tech Debt

### Dynamic Module Imports (High Priority)
- Issue: Files use `importlib.util` to dynamically load `1.5_Utils.py` at runtime instead of standard Python imports
- Files: `src/f1d/sample/1.1_CleanMetadata.py`, `src/f1d/sample/1.2_LinkEntities.py`, `src/f1d/sample/1.3_BuildTenureMap.py`, `src/f1d/sample/1.4_AssembleManifest.py`, `src/f1d/financial/v1/3.0_BuildFinancialFeatures.py`, `src/f1d/financial/v1/3.1_FirmControls.py`, `src/f1d/financial/v1/3.2_MarketVariables.py`
- Impact: Breaks IDE autocomplete, type checking, and makes refactoring error-prone. Requires `# type: ignore` comments to suppress mypy errors
- Fix approach: Rename `1.5_Utils.py` to `sample_utils.py`, move to `src/f1d/shared/`, use standard imports

### Large Files with Mixed Responsibilities (Medium Priority)
- Issue: Single files exceed 1000+ lines with multiple responsibilities
- Files: `2_Scripts/shared/observability/stats.py` (5171 lines), `2_Scripts/4_Econometric_V2/4.4_H4_LeverageDiscipline.py` (1767 lines), `2_Scripts/3_Financial_V2/3.2_H2Variables.py` (1700 lines)
- Impact: Difficult to navigate, test, and maintain. High cognitive load for understanding
- Fix approach: Split into focused modules with single responsibilities

### Type Ignore Comments (Medium Priority)
- Issue: 40+ `# type: ignore` comments suppressing mypy errors throughout codebase
- Files: `src/f1d/sample/*.py`, `src/f1d/econometric/v1/4.3_TakeoverHazards.py`, `src/f1d/financial/v1/*.py`, `src/f1d/shared/chunked_reader.py`
- Impact: Masks real type errors that could indicate bugs
- Fix approach: Address underlying type issues instead of suppressing; track in `type_errors_baseline.txt`

### Bare `pass` Exception Handlers (Low Priority)
- Issue: Empty exception blocks that silently swallow errors
- Files: `src/f1d/econometric/v2/4.9_CEOFixedEffects.py:237`, `src/f1d/econometric/v2/4.*.py` (multiple), `src/f1d/financial/v2/3.6_H6Variables.py:689`, `src/f1d/financial/v2/3.5_H5Variables.py:1305`
- Impact: Errors go undetected, making debugging difficult
- Fix approach: Add logging or specific exception handling with context

## Known Bugs

### NotImplemented Survival Analysis Functions
- Symptoms: `run_cox_ph()` and `run_fine_gray()` raise `NotImplementedError` when called
- Files: `src/f1d/econometric/v1/4.3_TakeoverHazards.py:115-130`
- Trigger: Running Step 4.3 takeover hazard analysis
- Workaround: None - features are stubs requiring lifelines integration

### Stats Module Type Errors (56 errors)
- Symptoms: mypy reports 56 type errors in shared modules, primarily in `observability/stats.py`
- Files: `src/f1d/shared/observability/stats.py` (47 errors), `2_Scripts/shared/observability/stats.py` (47 errors)
- Trigger: Running `mypy` type checking
- Workaround: Documented in `type_errors_baseline.txt` and `type_errors_summary.md`

## Security Considerations

### WRDS Credentials Handling
- Risk: Credentials stored in environment variables without encryption
- Files: `.env.example` shows `F1D_WRDS_USERNAME` and `F1D_WRDS_PASSWORD` patterns
- Current mitigation: `.env` is in `.gitignore`, template provided without values
- Recommendations: Validate that no actual `.env` file with credentials is committed

### Dynamic Code Loading
- Risk: `importlib.util.spec_from_file_location()` and `exec_module()` could load arbitrary code if paths are manipulated
- Files: `src/f1d/sample/1.1_CleanMetadata.py:47-53`, `src/f1d/sample/1.2_LinkEntities.py:59-64`, `src/f1d/sample/1.3_BuildTenureMap.py:47-51`, `src/f1d/sample/1.4_AssembleManifest.py:47-51`
- Current mitigation: Paths are hardcoded relative to `__file__`
- Recommendations: Consider using standard imports to eliminate this pattern entirely

## Performance Bottlenecks

### Entity Linking (Step 1.2)
- Problem: Fuzzy matching is O(n^2) complexity - the slowest step in pipeline
- Files: `src/f1d/sample/1.2_LinkEntities.py` (1291 lines)
- Cause: ~11k unique companies require fuzzy name matching against CCM database
- Improvement path: Parallel workers (Phase 15-01 planned but removed in Phase 16-03, available in git history)

### Large Parquet File Reads
- Problem: Reading entire files when only subset of columns needed
- Files: Multiple scripts in `src/f1d/financial/v2/`, `src/f1d/econometric/`
- Cause: Legacy code before Phase 15 column pruning optimization
- Improvement path: Already partially addressed; ensure all scripts use `columns=` parameter in `pd.read_parquet()`

### Memory Requirements
- Problem: Peak memory ~4GB during entity linking may exceed smaller systems
- Files: `src/f1d/sample/1.2_LinkEntities.py`
- Cause: Loading entire CCM database and transcript metadata into memory
- Improvement path: Use chunked reading (already implemented in `chunked_reader.py`), memory-aware throttling

## Fragile Areas

### V1/V2 Variant Coexistence
- Files: `src/f1d/econometric/v1/`, `src/f1d/econometric/v2/`, `src/f1d/financial/v1/`, `src/f1d/financial/v2/`
- Why fragile: Two parallel implementations of same pipeline steps must be kept in sync; changes may need to be applied to both
- Safe modification: Changes to shared utilities (`src/f1d/shared/`) are safe; changes to step scripts should check both versions
- Test coverage: V1 scripts excluded from coverage calculation (`pyproject.toml` omit pattern `*/V1*`)

### Dynamic Utils Import Pattern
- Files: All files in `src/f1d/sample/` and some in `src/f1d/financial/v1/`
- Why fragile: Relies on filesystem path at runtime; breaks if file structure changes
- Safe modification: Do not rename or move `1.5_Utils.py` without updating all import sites
- Test coverage: Limited - dynamic imports difficult to mock

### Stats Module Dictionary Typing
- Files: `src/f1d/shared/observability/stats.py` (5171 lines in 2_Scripts version)
- Why fragile: Complex nested dictionary structures with inconsistent typing; 47/56 of all type errors originate here
- Safe modification: Add explicit type annotations before modifying
- Test coverage: Limited - complex return types make testing difficult

## Scaling Limits

### Current Capacity
- Transcripts: ~50K (2002-2018)
- Total rows: ~25M across pipeline
- Memory: 8GB minimum, 16GB recommended
- Processing time: 2-4 hours full pipeline

### Breaking Points
- Entity linking (1.2): Single-threaded fuzzy matching becomes bottleneck at 100K+ companies
- Memory: Systems with <8GB RAM will fail on Step 1.2
- Storage: Parquet files 100MB - 1GB per year; 5GB total CRSP/Compustat data

### Scaling Path
- Parallel processing: `parallel_utils.py` available in git history (commit 02288a0)
- Column pruning: Implemented in Phase 15-02, 30-50% memory reduction
- Memory-aware throttling: Phase 15-03 monitors and pauses if memory > 80%

## Dependencies at Risk

### statsmodels Version Pinning
- Risk: Pinned to 0.14.6 due to breaking changes in 0.14.0 (deprecated GLM link names)
- Impact: Upgrading breaks regression analysis
- Migration plan: See `DEPENDENCIES.md` for upgrade strategy

### pyarrow Version Constraint
- Risk: Pinned to 21.0.0 for Python 3.8-3.13 compatibility; 23.0.0+ requires Python >= 3.10
- Impact: Cannot upgrade without dropping Python 3.8/3.9 support
- Migration plan: Documented in `DEPENDENCIES.md`

### rapidfuzz Optional Dependency
- Risk: Graceful degradation if not installed, but lower entity match rates
- Impact: Tier 3 entity linking falls back to slower algorithm
- Migration plan: Optional in `requirements.txt`, recommended for improved matching

## Missing Critical Features

### Survival Analysis Implementation
- Problem: `run_cox_ph()` and `run_fine_gray()` are stubs - full implementation missing
- Blocks: Step 4.3 takeover hazard analysis cannot run
- Required: lifelines library integration

### Full Type Stub Coverage
- Problem: Missing type stubs for pandas, psutil cause `import-untyped` errors
- Blocks: Stricter mypy configuration
- Required: `pip install types-pandas types-psutil`

## Test Coverage Gaps

### Stage Modules (Hypothesis Tests)
- What's not tested: All `src/f1d/econometric/v2/4.*.py` hypothesis regression scripts
- Files: `4.1_H1CashHoldingsRegression.py` through `4.11_H9_Regression.py`
- Risk: Regressions may produce incorrect coefficients without detection
- Priority: High - these produce final research outputs

### V1 Legacy Code
- What's not tested: All `src/f1d/econometric/v1/` and `src/f1d/financial/v1/` scripts
- Files: Entire v1 directories excluded from coverage
- Risk: V1 still used; bugs may go undetected
- Priority: Medium - V1 is maintained alongside V2

### Large Stats Module
- What's not tested: `src/f1d/shared/observability/stats.py` complex nested structures
- Files: 47 type errors indicate likely runtime issues
- Risk: Silent data corruption in statistics output
- Priority: Medium - observability functions affect all steps

### Coverage Threshold Gap
- What's not tested: Current 25% overall threshold is below target 60%
- Files: `pyproject.toml` documents gap between current (25%) and target (60%)
- Risk: Technical debt accumulation without enforcement
- Priority: Low - gradual improvement path documented

---

*Concerns audit: 2026-02-14*
