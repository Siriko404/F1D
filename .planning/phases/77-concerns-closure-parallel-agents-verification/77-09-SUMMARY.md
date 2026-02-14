---
phase: 77-concerns-closure-parallel-agents-verification
plan: 09
subsystem: tooling
tags: [mypy, type-stubs, pandas-stubs, types-psutil, static-analysis]

# Dependency graph
requires:
  - phase: 76-stage-scripts-migration
    provides: src/f1d module structure for type checking
provides:
  - Type stub packages for pandas, psutil, requests, PyYAML
  - Updated mypy configuration to use type stubs
  - Baseline mypy output with type stubs (mypy_with_stubs.log)
affects: [mypy-configuration, type-checking, code-quality]

# Tech tracking
tech-stack:
  added:
    - pandas-stubs>=2.2.0 (type stubs for pandas)
    - types-psutil>=6.0.0 (type stubs for psutil)
    - types-requests>=2.31.0 (type stubs for requests)
    - types-PyYAML>=6.0.0 (type stubs for PyYAML)
  patterns:
    - Type stub packages for stricter mypy checking

key-files:
  created:
    - .planning/codebase/mypy_with_stubs.log
  modified:
    - requirements.txt
    - pyproject.toml

key-decisions:
  - "Use pandas-stubs instead of types-pandas (modern official package)"
  - "Remove pandas, psutil, yaml from ignore_missing_imports in pyproject.toml"

patterns-established:
  - "Type stub packages installed via requirements.txt for external dependencies"

# Metrics
duration: 9min
completed: 2026-02-14
---

# Phase 77 Plan 09: Full Type Stub Coverage Summary

**Type stub packages (pandas-stubs, types-psutil, types-requests, types-PyYAML) installed and configured to eliminate import-untyped errors in mypy output.**

## Performance

- **Duration:** 9 min
- **Started:** 2026-02-14T19:37:47Z
- **Completed:** 2026-02-14T19:46:32Z
- **Tasks:** 3
- **Files modified:** 2

## Accomplishments
- Added type stub packages to requirements.txt for pandas, psutil, requests, and PyYAML
- Updated pyproject.toml mypy configuration to remove ignore_missing_imports for typed packages
- Verified 0 import-untyped errors in mypy output after installing type stubs

## Task Commits

Each task was committed atomically:

1. **Task 1: Add type stub packages to requirements.txt** - `276153c` (feat)
2. **Task 2: Update pyproject.toml mypy configuration** - `7fd0d46` (feat)
3. **Task 3: Install and verify type stubs** - `9e60870` (feat)

## Files Created/Modified
- `requirements.txt` - Added type stub packages (pandas-stubs, types-psutil, types-requests, types-PyYAML)
- `pyproject.toml` - Updated mypy configuration to document type stubs and remove ignore_missing_imports for pandas, psutil, yaml
- `.planning/codebase/mypy_with_stubs.log` - Baseline mypy output with type stubs (1327 lines, 281 type errors, 0 import-untyped)

## Decisions Made
- Used `pandas-stubs` instead of `types-pandas` - the former is the modern official package maintained by the pandas team
- Removed pandas, psutil, and yaml from the ignore_missing_imports overrides in pyproject.toml since type stubs are now available

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Corrected type stub package name**
- **Found during:** Task 3 (Install and verify type stubs)
- **Issue:** `types-pandas` package does not exist in PyPI - the correct package is `pandas-stubs`
- **Fix:** Updated requirements.txt to use `pandas-stubs>=2.2.0` instead of `types-pandas>=2.2.0`
- **Files modified:** requirements.txt
- **Verification:** pip install succeeded, pandas-stubs provides type stubs for pandas
- **Committed in:** 9e60870 (Task 3 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Minor correction - pandas-stubs is the correct modern package name for pandas type stubs. No scope creep.

## Issues Encountered
- types-pandas package does not exist; pandas-stubs is the correct package maintained by the pandas team

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Type stub coverage complete for pandas, psutil, requests, and PyYAML
- mypy runs with 0 import-untyped errors
- 281 remaining type errors are code quality issues (var-annotated, index errors) not related to missing type stubs

---
*Phase: 77-concerns-closure-parallel-agents-verification*
*Completed: 2026-02-14*

## Self-Check: PASSED

- FOUND: requirements.txt
- FOUND: pyproject.toml
- FOUND: .planning/codebase/mypy_with_stubs.log
- FOUND: 77-09-SUMMARY.md
- FOUND: 276153c (Task 1 commit)
- FOUND: 7fd0d46 (Task 2 commit)
- FOUND: 9e60870 (Task 3 commit)
