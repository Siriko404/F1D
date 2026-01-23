---
phase: 07-critical-bug-fixes
plan: 02
subsystem: error-handling
tags: optional-dependencies, rapidfuzz, error-handling, warnings, stderr

# Dependency graph
requires:
  - phase: 07-01
    provides: Enhanced error handling pattern for critical operations
provides:
  - Rich warning for optional rapidfuzz dependency
  - Structured warning output to stderr
  - Clear installation instructions for users
  - Impact documentation for missing dependencies
affects: All scripts using optional dependencies

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Optional dependency flag pattern (FUZZY_AVAILABLE)
    - Rich warning with sections (impact, installation, note)
    - Warning to stderr (separates warnings from normal output)

key-files:
  created: []
  modified:
    - 2_Scripts/1_Sample/1.2_LinkEntities.py - Enhanced warning for rapidfuzz

key-decisions:
  - Use FUZZY_AVAILABLE flag to track optional dependency
  - Print warnings to stderr (not stdout) for proper separation
  - Structure warnings with clear sections: impact, installation, optional note

patterns-established:
  - Pattern: Optional dependency with flag-based availability check
  - Pattern: Rich warnings using file=sys.stderr parameter
  - Pattern: Multi-section warning output for user clarity

# Metrics
duration: 0 min (already completed)
completed: 2026-01-23
---

# Phase 7 Plan 2: Enhanced Optional Dependency Warning Summary

**Rich warning for optional rapidfuzz dependency with impact documentation and installation instructions**

## Performance

- **Duration:** 0 min (changes already committed)
- **Started:** N/A
- **Completed:** 2026-01-23
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments

- Updated import section to use `FUZZY_AVAILABLE` flag instead of `FUZZ_AVAILABLE`
- Added `FUZZY_VERSION` variable for future version tracking
- Removed minimal print statement from import block
- Created `warn_if_fuzzy_missing()` function with structured warning output
- Warning includes 4 sections: header, impact on results, installation, optional note
- All warning output goes to stderr (file=sys.stderr) for proper separation
- Function called at script startup to warn immediately if rapidfuzz missing

## Task Commits

Changes were already committed in a single atomic commit:

1. **Task 1-2 combined: Enhance optional dependency warning** - `cb157ad` (feat)

**Plan metadata:** N/A (not created yet)

## Files Created/Modified

- `2_Scripts/1_Sample/1.2_LinkEntities.py`
  - Lines 59-66: Enhanced import section with FUZZY_AVAILABLE and FUZZY_VERSION
  - Lines 69-88: warn_if_fuzzy_missing() function with rich warning
  - Line 92: warn_if_fuzzy_missing() call at script startup

## Decisions Made

None - followed plan as specified from RESEARCH.md Pattern 2.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Plan 07-02 complete, ready for next phase. No blockers or concerns.

The enhanced warning pattern can be applied to other optional dependencies if needed in future phases.

---
*Phase: 07-critical-bug-fixes*
*Completed: 2026-01-23*
