---
phase: 12-data-quality-observability
plan: 01
subsystem: observability
tags: psutil, pytest, memory-tracking, anomaly-detection, checksums, throughput

# Dependency graph
requires:
  - phase: 11-testing-infrastructure
    provides: pytest framework, test infrastructure
provides:
  - Observability infrastructure with psutil for cross-platform memory tracking
  - 5 inline helper functions for memory, throughput, checksums, anomaly detection
  - Unit tests covering all observability helper functions
affects: 12-02, 12-03 (rollout plans for all scripts)

# Tech tracking
tech-stack:
  added: psutil==7.2.1 (cross-platform process monitoring)
  patterns: Inline helper functions (Phase 1 pattern), deterministic statistical methods, z-score/IQR anomaly detection

key-files:
  created: tests/unit/test_observability_helpers.py
  modified: requirements.txt

key-decisions:
  - Use psutil instead of resource module (psutil is cross-platform, resource is Unix-only)
  - Use z-score and IQR methods for anomaly detection (deterministic, no ML randomness)
  - Store helper functions as template file for copy-paste to scripts (Phase 1 pattern)

patterns-established:
  - Pattern 1: Inline observability helpers for memory tracking (get_process_memory_mb)
  - Pattern 2: Throughput calculation (rows/second with division by zero handling)
  - Pattern 3: File checksums using hashlib with 8KB chunks for efficiency
  - Pattern 4: Anomaly detection using deterministic statistical methods (z-score, IQR)
  - Pattern 5: Edge case handling (empty DataFrames, all NaN, zero variance)

# Metrics
duration: 11 min
completed: 2026-01-23
---

# Phase 12 Plan 1: Observability Infrastructure Summary

**psutil memory tracking with inline helper functions for memory, throughput, checksums, and z-score/IQR anomaly detection**

## Performance

- **Duration:** 11 min
- **Started:** 2026-01-23T16:37:22Z
- **Completed:** 2026-01-23T16:48:52Z
- **Tasks:** 3
- **Files modified:** 2

## Accomplishments

- Added psutil==7.2.1 to requirements.txt for cross-platform memory tracking
- Created 5 inline observability helper functions following Phase 1 pattern:
  - get_process_memory_mb(): Track RSS, VMS, and percent memory usage
  - calculate_throughput(): Calculate rows/second with division by zero handling
  - compute_file_checksum(): SHA-256 file checksums using 8KB chunks
  - detect_anomalies_zscore(): Outlier detection using z-score method (deterministic)
  - detect_anomalies_iqr(): Outlier detection using IQR method (deterministic)
- All functions are deterministic (same input produces same output)
- Comprehensive unit tests covering all 5 functions with edge cases

## Task Commits

Each task was committed atomically:

1. **Task 1: Add psutil dependency to requirements.txt** - `57fe6c5` (chore)
2. **Task 2: Create inline observability helper functions** - `652a902` (feat)
3. **Task 3: Create unit tests for observability helpers** - `5470d25` (test)

**Plan metadata:** TBD (docs commit)

## Files Created/Modified

- `requirements.txt` - Added psutil==7.2.1 for cross-platform memory tracking
- `tests/unit/test_observability_helpers.py` - Observability helper functions template with unit tests

## Decisions Made

- **Use psutil instead of resource module:** psutil is cross-platform (Windows/Linux/macOS), while resource module is Unix-only. This ensures observability works on the project's Windows platform.
- **Use z-score and IQR for anomaly detection:** Deterministic statistical methods avoid the non-determinism of ML-based approaches (IsolationForest, LOF). This preserves reproducibility requirements.
- **Store helpers as template file:** Functions are in test_observability_helpers.py as a "template file" for copy-paste to scripts. This follows Phase 1 inline pattern for self-contained replication.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Fixed psutil.memory_info().percent to use process.memory_percent()**

- **Found during:** Task 3 (unit tests)
- **Issue:** psutil.memory_info() returns a named tuple with rss, vms, etc., but not 'percent' attribute. Test failed with AttributeError.
- **Fix:** Changed to use process.memory_percent() method which returns memory usage as percentage.
- **Files modified:** tests/unit/test_observability_helpers.py
- **Verification:** test_get_process_memory_mb now passes successfully
- **Committed in:** 5470d25 (Task 3 commit)

**2. [Rule 1 - Bug] Fixed test DataFrames with unequal array lengths**

- **Found during:** Task 3 (unit tests)
- **Issue:** Test DataFrames had arrays of different lengths, causing ValueError: "All arrays must be of the same length"
- **Fix:** Adjusted all test arrays to have equal length and increased data points for stable std/IQR calculations.
- **Files modified:** tests/unit/test_observability_helpers.py
- **Verification:** All 6 unit tests now pass
- **Committed in:** 5470d25 (Task 3 commit)

---

**Total deviations:** 2 auto-fixed (1 missing critical, 1 bug)
**Impact on plan:** Both fixes necessary for correctness (API error and test data issue). No scope creep.

## Issues Encountered

None - all issues were auto-fixed and tests pass.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Observability infrastructure complete with psutil, 5 helper functions, and unit tests
- Ready for rollout to Steps 1-2 scripts (8 scripts) in plan 12-02
- Ready for rollout to Steps 3-4 scripts (11 scripts) in plan 12-03
- No blockers or concerns

---
*Phase: 12-data-quality-observability*
*Completed: 2026-01-23*
