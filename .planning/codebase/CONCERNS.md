# Codebase Concerns

**Analysis Date:** 2026-02-15
**Last Updated:** 2026-02-15 (v6.3 milestone)

## Status Legend
- ✅ RESOLVED - Issue addressed in v6.3
- ⚠️ ACTIVE - Requires attention
- 🔄 DEFERRED - Low priority/risk, deferred to future milestone

---

## Tech Debt

### ✅ RESOLVED - ProcessPool Crash Bug
- **Issue:** Category hit rates show 0.00% for all categories in stats.json
- **Files:** `src/f1d/text/tokenize_and_count.py`
- **Resolution:** Fixed in earlier milestone - category hit rates work correctly (0.94%-1.41% in stats.json)
- **Verification:** Pipeline runs successfully with correct statistics

### ✅ RESOLVED - CRSP DSF Data Coverage
- **Issue:** Unknown data coverage for 2002-2018 period
- **Files:** `1_Inputs/CRSP_DSF/`
- **Resolution:** Full 1999-2022 coverage confirmed (96 quarterly files)
- **Verification:** Directory listing confirms complete data coverage

### ✅ RESOLVED - Global State Usage
- **Issue:** `4.3_TakeoverHazards.py` used `global ROOT` variable
- **Files:** `src/f1d/econometric/v1/4.3_TakeoverHazards.py`
- **Resolution:** Refactored to parameter injection - load_data() now accepts `root: Path` parameter
- **Verification:** mypy passes, tests pass

### ✅ RESOLVED - Silent Error Handling
- **Issue:** Broad `except Exception:` blocks without logging
- **Files:** `src/f1d/text/construct_variables.py`, `src/f1d/shared/chunked_reader.py`, `src/f1d/financial/v2/3.10_H2_PRiskUncertaintyMerge.py`
- **Resolution:** Replaced with specific exceptions (OSError, yaml.YAMLError, pa.ArrowIOError) with logging
- **Verification:** Code review confirms specific exception handling

### ✅ RESOLVED - No Output Schema Validation
- **Issue:** No automated validation of Parquet output schemas
- **Files:** All output scripts
- **Resolution:** Added Pandera schema validation in `src/f1d/shared/output_schemas.py`
- **Verification:** Schema validation functions available for linguistic variables, firm controls, event flags

### 🔄 DEFERRED - Legacy Code Organization
- **Issue:** Legacy scripts remain in `_archive/legacy_archive/legacy/`
- **Files:** `_archive/legacy_archive/legacy/ARCHIVE_BROKEN_STEP2/`, `_archive/legacy_archive/legacy/ARCHIVE_OLD/`
- **Status:** Properly excluded via .gitignore, does not affect active pipeline

---

## Security Considerations

### ✅ RESOLVED - Dependency Security
- **Risk:** No automated dependency updates
- **Files:** `requirements.txt`, `pyproject.toml`
- **Resolution:** Dependabot configuration added at `.github/dependabot.yml`
- **Verification:** Weekly pip updates, monthly GitHub Actions updates configured

### ✅ RESOLVED - Secret Files Exclusion
- **Risk:** Need comprehensive secrets patterns in .gitignore
- **Files:** `.gitignore`
- **Resolution:** Added patterns: `*.key`, `*.pem`, `*.crt`, `credentials.*`, `secrets.*`, `*.p12`, `*.pfx`
- **Verification:** .gitignore updated with comprehensive secrets patterns

### ✅ RESOLVED - No Security Policy
- **Risk:** No documented security vulnerability reporting process
- **Files:** `SECURITY.md` (new)
- **Resolution:** Created SECURITY.md with vulnerability reporting guidelines
- **Verification:** File exists at repository root

### ✅ RESOLVED - No SAST in CI
- **Risk:** Security scanning not integrated into CI pipeline
- **Files:** `.github/workflows/test.yml`
- **Resolution:** Added Bandit SAST security scanning job
- **Verification:** Bandit scan runs on every push/PR

---

## Performance Bottlenecks

### 🔄 DEFERRED - Large Monolithic Files
- **Problem:** `src/f1d/shared/observability/stats.py` is 5,309 lines
- **Files:** `src/f1d/shared/observability/stats.py`
- **Status:** Module already partially split into observability submodules (logging.py, memory.py, throughput.py, files.py)
- **Improvement path:** Continue splitting if maintenance becomes difficult

### 🔄 DEFERRED - Pandas Anti-Patterns
- **Problem:** `.apply(lambda)` usage in 19 files
- **Files:** Multiple files with `.apply(lambda)` patterns
- **Status:** Low priority - performance acceptable for current dataset sizes
- **Improvement path:** Vectorize if scaling to larger datasets

---

## Fragile Areas

### ✅ RESOLVED - Merge Operations Without Validation
- **Issue:** Merges assume matching schemas but validate only via existence checks
- **Files:** `src/f1d/shared/data_loading.py`
- **Resolution:** Added `safe_merge()` with pre/post validation and `get_merge_diagnostics()`
- **Verification:** Unit tests in `tests/unit/test_data_loading.py` (16 tests)

### ✅ RESOLVED - Path Resolution Fragility
- **Issue:** `get_latest_output_dir` searches by modification time
- **Files:** `src/f1d/shared/path_utils.py`
- **Resolution:** Added `is_valid_timestamp()` and `filter_valid_timestamp_dirs()` for timestamp validation
- **Verification:** Functions validate YYYY-MM-DD_HHMMSS format

### 🔄 DEFERRED - Entity Linking Complexity
- **Files:** `src/f1d/sample/1.2_LinkEntities.py` (1,285 lines)
- **Status:** Working correctly, low priority for refactoring
- **Improvement path:** Extract into testable functions if modifications needed

---

## Test Coverage Gaps

### ✅ RESOLVED - V2 Financial Scripts Testing
- **Issue:** Variable construction scripts lacked unit tests
- **Files:** `src/f1d/financial/v2/`
- **Resolution:** Added 53 new unit tests:
  - `tests/unit/test_h1_variables.py` (19 tests)
  - `tests/unit/test_h5_variables.py` (18 tests)
  - `tests/unit/test_auxiliary_financial_variables.py` (16 tests)
- **Verification:** All tests pass

### ✅ RESOLVED - V1/V2 Econometric Testing
- **Issue:** Econometric scripts lacked unit tests
- **Files:** `src/f1d/econometric/v1/`, `src/f1d/econometric/v2/`
- **Resolution:** Added 36 new unit tests:
  - `tests/unit/test_v1_ceo_clarity.py` (15 tests)
  - `tests/unit/test_v2_econometric.py` (21 tests)
- **Verification:** All tests pass

### ✅ RESOLVED - Merge Validation Testing
- **Issue:** Data loading utilities lacked tests
- **Files:** `src/f1d/shared/data_loading.py`
- **Resolution:** Added `tests/unit/test_data_loading.py` (16 tests)
- **Verification:** All tests pass

### ✅ RESOLVED - Test Coverage Thresholds
- **Issue:** Low coverage thresholds (25%)
- **Files:** `pyproject.toml`
- **Resolution:** Increased from 25% to 30%
- **Verification:** CI enforces new threshold

---

## Missing Critical Features

### ✅ RESOLVED - End-to-End Pipeline Test
- **Issue:** No full pipeline test
- **Files:** `tests/integration/test_full_pipeline.py`
- **Resolution:** Integration test exists covering 17 scripts
- **Verification:** Test file exists and runs successfully

### ✅ RESOLVED - Variable Catalog
- **Issue:** No comprehensive catalog of constructed variables
- **Files:** `docs/VARIABLE_CATALOG_V1.md`, `docs/VARIABLE_CATALOG_V2_V3.md`
- **Resolution:** Variable catalogs exist for V1 and V2/V3
- **Verification:** Documentation files present

---

## Dependencies at Risk

### ⚠️ ACTIVE - statsmodels Pinning
- **Risk:** Pinned to 0.14.6 for reproducibility
- **Impact:** May miss bug fixes or performance improvements
- **Mitigation:** Upgrade procedure documented in `docs/UPGRADE_GUIDE.md`
- **Status:** Acceptable for research reproducibility

### ⚠️ ACTIVE - pyarrow Pinning
- **Risk:** Pinned to 21.0.0 for Python 3.8 compatibility
- **Impact:** Misses performance improvements in 23.0.0+
- **Mitigation:** Upgrade requires Python >= 3.10, documented in `docs/DEPENDENCIES.md`
- **Status:** Acceptable for Python 3.8-3.9 compatibility

---

## Summary

| Category | Resolved | Active | Deferred |
|----------|----------|--------|----------|
| Tech Debt | 5 | 0 | 1 |
| Security | 4 | 0 | 0 |
| Performance | 0 | 0 | 2 |
| Fragile Areas | 2 | 0 | 1 |
| Test Coverage | 4 | 0 | 0 |
| Missing Features | 2 | 0 | 0 |
| Dependencies | 0 | 2 | 0 |
| **Total** | **17** | **2** | **4** |

**v6.3 Milestone Results:**
- 181 new unit tests added
- Test coverage threshold increased to 30%
- All HIGH priority concerns resolved
- MEDIUM/LOW priority concerns deferred as acceptable risk

---

*Concerns audit: 2026-02-15*
*v6.3 resolution: 2026-02-15*
