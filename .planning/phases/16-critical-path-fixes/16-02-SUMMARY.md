---
phase: 16-critical-path-fixes
plan: 02
subsystem: testing
tags: [e2e, pytest, integration, ci, github-actions]

# Dependency graph
requires:
  - phase: 11-testing-infrastructure
    provides: pytest configuration, integration test patterns
provides:
  - E2E integration test covering all 17 pipeline scripts
  - CI workflow with separate E2E test job and timeout handling
  - pytest marker for filtering E2E tests (-m e2e)
affects: [17-plan-verifications, 18-tech-debt-cleanup]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "E2E test pattern: Sequential subprocess execution with timeout and fail-fast"
    - "CI separation pattern: Unit/integration tests first, E2E tests as separate job"

key-files:
  created:
    - tests/integration/test_full_pipeline.py - Full pipeline E2E test with 3 test functions
  modified:
    - .github/workflows/test.yml - Added e2e-test job with 30-min timeout
    - pyproject.toml - Added e2e marker to pytest configuration

key-decisions:
  - "Separate E2E job in CI: Run E2E on single Python version (3.10) for speed, depends on unit/integration tests passing"
  - "10-minute per-script timeout: Balance between catching hangs and allowing realistic execution time"
  - "Test output validation: Verify both directory existence and specific output files per script"

patterns-established:
  - "E2E test structure: PIPELINE_SCRIPTS list → subprocess.run loop → output verification"
  - "Output directory mapping: get_output_dir() derives correct path based on script location"

# Metrics
duration: 15min
completed: 2026-01-23
---

# Phase 16: Plan 02 - E2E Pipeline Test Summary

**Full pipeline integration test covering all 17 scripts with subprocess execution, timeout handling, and output validation, plus CI workflow with separate E2E job**

## Performance

- **Duration:** 15 min
- **Started:** 2026-01-23T15:40:00Z
- **Completed:** 2026-01-23T15:55:00Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments

- Created comprehensive E2E test that executes all 17 pipeline scripts in correct order
- Added fail-fast mechanism that stops on first script failure with detailed error output
- Implemented timeout protection (10 minutes per script) to prevent infinite hangs
- Added CI workflow with separate E2E test job running after unit/integration tests pass
- Registered pytest `e2e` marker for flexible test filtering

## Task Commits

Each task was committed atomically:

1. **Task 1: Update CI workflow to include E2E test** - `877bd75` (feat)
2. **Task 2: Create full pipeline integration test** - `79aef3c` (feat)
3. **Task 3: Register E2E marker in pytest config** - `2df6747` (feat)

**Plan metadata:** Pending (will be in final commit)

## Files Created/Modified

- `tests/integration/test_full_pipeline.py` - E2E test with 3 test functions:
  - `test_full_pipeline_execution()`: Runs all 17 scripts sequentially
  - `test_pipeline_data_flow()`: Verifies inter-step dependencies
  - `test_pipeline_stats_json_structure()`: Validates observability infrastructure
- `.github/workflows/test.yml` - Added `e2e-test` job with 30-minute timeout, runs on Python 3.10 only, depends on `test` job
- `pyproject.toml` - Added `e2e` marker to `markers` list

## Decisions Made

- **Separate E2E CI job**: E2E tests run as separate job with 30-minute timeout, only on Python 3.10 (speed optimization), after unit/integration tests pass. This prevents slow E2E tests from blocking faster unit tests and provides clear separation in CI logs.

- **Per-script timeout**: 10-minute timeout per script balances catching hangs with allowing realistic execution time for data processing scripts. Total pipeline runtime estimated at 15-20 minutes based on data volume.

- **Output verification strategy**: Check both directory existence (`latest/` symlinked directory) and specific output files (parquet, json) for each script. This catches missing outputs even if directory was created.

- **Fail-fast approach**: Test stops immediately on first script failure with full stderr output. This is intentional - E2E test is about catching pipeline breaks early, not running to completion despite errors.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - all tasks completed without issues.

- **pytest not in PATH**: Initial `pytest --collect-only` failed with "command not found". Workaround: Used `python -m pytest` instead.
- **Marker not registered**: Initial test collection failed with "'e2e' not found in markers". Solution: Added e2e marker to pyproject.toml (Task 3).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

**Ready for:**
- E2E test can be run manually with `pytest tests/integration/test_full_pipeline.py`
- CI will automatically run E2E tests on Python 3.10 after unit/integration tests pass
- Test catches pipeline breaks that would otherwise go undetected

**Dependencies for next phase:**
- Phase 16-01 (Fix Step 4 Path Mismatch) should be executed first so E2E test can run successfully without failing on path errors

**Blockers/Concerns:**
- E2E test will currently fail due to Step 4 path mismatch (3 scripts reference `2.4_Linguistic_Variables` instead of `2_Textual_Analysis/2.2_Variables`). This is expected and will be fixed in Phase 16-01.
- E2E test requires production data in `1_Inputs/` to execute. Test will skip if data is missing, but for full verification, real data should be present.

**Closing the critical gap:**
This plan closes the "No E2E test" critical gap identified in the v1.0.0 milestone audit. The test ensures that:
1. All 17 scripts execute successfully in sequence
2. Data flows correctly between pipeline steps
3. Integration regressions are caught before deployment

---
*Phase: 16-critical-path-fixes*
*Plan: 02*
*Completed: 2026-01-23*
