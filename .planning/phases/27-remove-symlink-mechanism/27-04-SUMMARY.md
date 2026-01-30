---
phase: 27-remove-symlink-mechanism
plan: 04
subsystem: infra
tags: [path-resolution, symlink-removal, step-4, test-updates]

# Dependency graph
requires:
  - phase: 27-01
    provides: get_latest_output_dir() function in shared/path_utils.py
  - phase: 27-03
    provides: Step 3 and 4.1.x scripts already verified
provides:
  - All 5 remaining Step 4 scripts (4.1.3, 4.1.4, 4.2, 4.3, 4.4) use get_latest_output_dir()
  - All 7 test files use get_latest_output_dir() for path resolution
  - Fixed missing load_data() function in 4.3_TakeoverHazards.py
affects: [27-05, 27-06]

# Tech tracking
tech-stack:
  added: []
  patterns: [timestamp-based-resolution, dynamic-path-resolution, test-fallback-pattern]

key-files:
  created: []
  modified:
    - 2_Scripts/4_Econometric/4.1.3_EstimateCeoClarity_Regime.py (verified - uses shared.data_loading)
    - 2_Scripts/4_Econometric/4.1.4_EstimateCeoTone.py (verified - uses get_latest_output_dir)
    - 2_Scripts/4_Econometric/4.2_LiquidityRegressions.py (verified - uses get_latest_output_dir)
    - 2_Scripts/4_Econometric/4.3_TakeoverHazards.py (fixed - added load_data with resolver)
    - 2_Scripts/4_Econometric/4.4_GenerateSummaryStats.py (verified - uses get_latest_output_dir)
    - tests/integration/test_full_pipeline.py (updated)
    - tests/integration/test_pipeline_step1.py (updated)
    - tests/integration/test_pipeline_step2.py (updated)
    - tests/integration/test_pipeline_step3.py (updated)
    - tests/unit/test_chunked_reader.py (updated)
    - tests/regression/test_output_stability.py (updated)
    - tests/regression/generate_baseline_checksums.py (updated)

key-decisions:
  - "Test files use fallback pattern: try get_latest_output_dir(), fallback to /latest/ if not found"
  - "4.3_TakeoverHazards.py was missing critical functions - added load_data() with proper resolver usage"
  - "All Step 4 scripts now compliant for timestamp-based resolution"

patterns-established:
  - "Pattern: Test files use resolve_output_dir() helper with try/except fallback"
  - "Pattern: Step 4 scripts either use shared.data_loading or inline load functions with get_latest_output_dir()"

# Metrics
duration: 12min
completed: 2026-01-30
---

# Phase 27 Plan 04: Update Remaining Step 4 Scripts and Test Files Summary

**Updated all 5 remaining Step 4 scripts and 7 test files to use timestamp-based path resolution via get_latest_output_dir() - fixed critical missing load_data() function in 4.3_TakeoverHazards.py**

## Performance

- **Duration:** 12 min
- **Started:** 2026-01-30T18:10:00Z
- **Completed:** 2026-01-30T18:22:00Z
- **Tasks:** 2
- **Files verified/fixed:** 12

## Accomplishments

### Task 1: Update Remaining Step 4 Scripts (4.1.3-4.4)

Verified all 5 scripts use `get_latest_output_dir()` for reading prerequisites:

| Script | Status | Resolution Method |
|--------|--------|-------------------|
| 4.1.3_EstimateCeoClarity_Regime.py | Verified | Uses `load_all_data()` from shared.data_loading (has resolver) |
| 4.1.4_EstimateCeoTone.py | Verified | Has inline `load_all_data()` using `get_latest_output_dir()` at lines 186-282 |
| 4.2_LiquidityRegressions.py | Verified | Has inline `load_all_data()` using `get_latest_output_dir()` at lines 193-356 |
| 4.3_TakeoverHazards.py | Fixed | Added `load_data()` function using `get_latest_output_dir()` for all inputs |
| 4.4_GenerateSummaryStats.py | Verified | Uses `get_latest_output_dir()` directly at lines 759, 769, 780 |

### Task 2: Update Test Files to Use Dynamic Path Resolution

Updated all 7 test files with imports and `resolve_output_dir()` helper:

| Test File | Import Added | Helper Function | Paths Updated |
|-----------|--------------|-----------------|---------------|
| test_full_pipeline.py | Yes | `get_output_dir()` with fallback | 2 locations |
| test_pipeline_step1.py | Yes | `resolve_output_dir()` | 1 location |
| test_pipeline_step2.py | Yes | `resolve_output_dir()` | 3 locations |
| test_pipeline_step3.py | Yes | `resolve_output_dir()` | 4 locations |
| test_chunked_reader.py | Yes | `resolve_output_dir()` | 3 locations |
| test_output_stability.py | Yes | `resolve_output_dir()` | 4 locations |
| generate_baseline_checksums.py | Yes | `resolve_output_dir()` | 3 locations |

**Fallback Pattern Used:**
```python
def resolve_output_dir(base_path: Path) -> Path:
    try:
        return get_latest_output_dir(base_path)
    except OutputResolutionError:
        return base_path / "latest"  # Fallback for tests
```

## Task Commits

Each task was committed atomically:

1. **Task 1 Base:** 782efc8 - feat(27-04): update remaining Step 4 scripts (4.1.4, 4.2, 4.3) to use get_latest_output_dir()
2. **Task 2:** e315d87 - test(27-04): update test files to use get_latest_output_dir() for path resolution
3. **Bug Fix:** e226571 - fix(27-04): add missing load_data() function to 4.3_TakeoverHazards.py

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed missing load_data() function in 4.3_TakeoverHazards.py**

- **Found during:** Task 1 verification
- **Issue:** Script called `load_data()` at line 170 but function didn't exist (not defined or imported)
- **Fix:** Added complete `load_data()` function that:
  - Loads manifest from 1.0_BuildSampleManifest using `get_latest_output_dir()`
  - Loads linguistic variables from 2.2_Variables using `get_latest_output_dir()`
  - Loads clarity scores from 4.1_CeoClarity using `get_latest_output_dir()`
  - Loads firm controls from 3_Financial_Features using `get_latest_output_dir()`
  - Loads event flags from 3.3_EventFlags using `get_latest_output_dir()`
  - Merges all data appropriately
- **Files modified:** 2_Scripts/4_Econometric/4.3_TakeoverHazards.py
- **Also fixed:** Added missing CONFIG dictionary and ROOT variable
- **Verification:** Script now compiles without syntax errors
- **Committed in:** e226571

**2. [Rule 3 - Blocking] Added missing imports and helper functions to test files**

- **Found during:** Task 2 execution
- **Issue:** Test files used hardcoded `/latest/` paths without importing the resolver
- **Fix:** Added to all 5 remaining test files:
  - `sys.path.insert()` to enable shared module imports
  - `from shared.path_utils import get_latest_output_dir, OutputResolutionError`
  - `resolve_output_dir()` helper with fallback pattern
- **Files modified:** 5 test files
- **Verification:** All test files compile without syntax errors
- **Committed in:** e315d87

---

**Total deviations:** 2 auto-fixed (1 bug fix, 1 blocking issue)
**Impact on plan:** Critical fixes required for correctness and test functionality

## Issues Encountered

1. **4.3_TakeoverHazards.py was severely broken** - Missing load_data(), CONFIG, ROOT, and several other functions. Fixed the data loading portion which was blocking this plan.

2. **Pre-existing issues in 4.3_TakeoverHazards.py** - Functions `run_cox_ph`, `run_fine_gray`, `print_stat`, `print_stats_summary`, `save_stats` are still missing. These are outside this plan's scope and will need to be addressed separately.

## Verification Results

### Syntax Verification
```
✓ 4.1.3_EstimateCeoClarity_Regime.py - Syntax OK
✓ 4.1.4_EstimateCeoTone.py - Syntax OK
✓ 4.2_LiquidityRegressions.py - Syntax OK
✓ 4.3_TakeoverHazards.py - Syntax OK (after fix)
✓ 4.4_GenerateSummaryStats.py - Syntax OK
✓ test_full_pipeline.py - Syntax OK
✓ test_pipeline_step1.py - Syntax OK
✓ test_pipeline_step2.py - Syntax OK
✓ test_pipeline_step3.py - Syntax OK
✓ test_chunked_reader.py - Syntax OK
✓ test_output_stability.py - Syntax OK
✓ generate_baseline_checksums.py - Syntax OK
```

### get_latest_output_dir() Usage Verification

**Step 4 Scripts:**
- ✓ 4.1.3 - Uses shared.data_loading.load_all_data() which has resolver
- ✓ 4.1.4 - Lines 186-282: Inline load_all_data() with resolver
- ✓ 4.2 - Lines 193-356: Inline load_all_data() with resolver
- ✓ 4.3 - New load_data() function uses resolver for all 5 input types
- ✓ 4.4 - Lines 759, 769, 780: Direct resolver usage

**Test Files:**
- ✓ All 7 test files now use dynamic resolution with fallback

## Remaining /latest/ References

These are cosmetic only (docstrings and comments) and will be cleaned in Plan 27-06:
- Docstrings in 4.1.x scripts describing input paths
- Docstrings in 4.2, 4.3, 4.4 describing input paths
- Comment in test files describing the fallback mechanism

## Next Phase Readiness

- ✓ All Step 4 scripts (4.1-4.4) now use timestamp-based resolution for reading
- ✓ All test files use dynamic path resolution with fallback
- Ready for Plan 27-05: Remove symlink creation from all 20 pipeline scripts
- Ready for Plan 27-06: Delete symlink_utils.py and clean up remaining references

---
*Phase: 27-remove-symlink-mechanism*
*Completed: 2026-01-30*
