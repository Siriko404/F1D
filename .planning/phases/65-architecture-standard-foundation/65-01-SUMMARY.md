---
phase: 65-architecture-standard-foundation
plan: 01
subsystem: documentation
tags: [architecture, src-layout, packaging, pypa, cookiecutter-data-science]

# Dependency graph
requires: []
provides:
  - ARCHITECTURE_STANDARD.md with canonical folder structure (ARCH-01)
  - Module organization patterns with __init__.py hierarchy (ARCH-02)
  - Data directory structure with mutability rules (ARCH-03)
  - Version management with single active version policy (ARCH-04)
  - Archive and legacy code handling strategy (ARCH-05)
  - Migration guide from current flat layout to src-layout
affects:
  - 66-naming-standard (builds on folder structure)
  - 67-config-standard (builds on config directory)
  - 68-doc-standard (builds on docs directory)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - src-layout pattern (PyPA recommended)
    - Cookiecutter Data Science conventions
    - Semantic versioning
    - Module tier system

key-files:
  created:
    - docs/ARCHITECTURE_STANDARD.md
  modified: []

key-decisions:
  - "Adopt src-layout over flat layout (PyPA recommendation)"
  - "Single active version policy - no V3/V4 directories"
  - "Data separated by lifecycle: raw/interim/processed/external"
  - "30-day deprecation period before archival"
  - "Module tier system with quality bars (Tier 1-3)"
  - "Include migration guide as appendix rather than separate document"

patterns-established:
  - "Pattern: src/f1d/ package structure with stage subpackages"
  - "Pattern: __init__.py with docstring, __all__, and re-exports"
  - "Pattern: Dated subdirectories for data versioning (YYYY-MM-DD)"
  - "Pattern: ARCHIVED.md for each archived item"
  - "Pattern: manifest.json for machine-readable archive tracking"

# Metrics
duration: 45min
completed: 2026-02-13
---

# Phase 65 Plan 01: Architecture Standard Document Summary

**Complete architecture standard defining src-layout folder structure, module organization, data lifecycle, version management, and archival conventions for portfolio-ready repository quality**

## Performance

- **Duration:** 45 min
- **Started:** 2026-02-13T06:13:29Z
- **Completed:** 2026-02-13T06:58:XXZ
- **Tasks:** 7
- **Files modified:** 1

## Accomplishments

- Created comprehensive ARCHITECTURE_STANDARD.md (2318 lines)
- Defined 5 main sections covering ARCH-01 through ARCH-05 requirements
- Documented src-layout pattern with complete target structure
- Established module organization with __init__.py patterns and code examples
- Defined data lifecycle stages with mutability rules (raw/interim/processed/external)
- Created version management policy with deprecation strategy
- Documented archive structure and legacy code handling
- Added detailed migration guide from current flat layout to src-layout

## Task Commits

Each task was committed atomically:

1. **Task 1: Header and introduction** - `efd708a` (docs)
2. **Task 2: Folder Structure (ARCH-01)** - `73bdb8e` (docs)
3. **Task 3: Module Organization (ARCH-02)** - `5533e9c` (docs)
4. **Task 4: Data Directory Structure (ARCH-03)** - `40d240d` (docs)
5. **Task 5: Version Management (ARCH-04)** - `dfc9333` (docs)
6. **Task 6: Archive and Legacy Code (ARCH-05)** - `e9cd95d` (docs)
7. **Task 7: Migration Guide Appendix** - `71898f8` (docs)

**Plan metadata:** (part of task commits)

## Files Created/Modified

- `docs/ARCHITECTURE_STANDARD.md` - Comprehensive architecture standard (2318 lines)
  - Header with version, purpose, design principles
  - Section 1: Folder structure with complete directory tree
  - Section 2: Module organization with __init__.py patterns
  - Section 3: Data directory structure with mutability rules
  - Section 4: Version management with deprecation strategy
  - Section 5: Archive and legacy code handling
  - Appendix A: Migration guide (6 phases)
  - Appendix B: Related standards reference

## Decisions Made

1. **src-layout over flat layout** - PyPA recommended pattern prevents import issues, better for packaging
2. **Single active version** - No V3/V4 directories, use semantic versioning on package instead
3. **Data lifecycle stages** - raw/interim/processed/external follows Cookiecutter Data Science conventions
4. **30-day deprecation** - Standard practice for code deprecation before archival
5. **Module tier system** - Quality bars scaled by importance (Tier 1: core shared, Tier 2: stage-specific, Tier 3: scripts)
6. **Migration guide as appendix** - Keep all architecture documentation in single document
7. **Dated subdirectories** - YYYY-MM-DD format for data versioning ensures proper sorting
8. **manifest.json for archive** - Machine-readable tracking enables tooling support

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - document creation proceeded smoothly following research findings from 65-RESEARCH.md.

## User Setup Required

None - this is a definition document. Implementation of the architecture standard is deferred to v6.0+.

## Next Phase Readiness

- Architecture standard foundation complete
- Ready for Phase 66 (Naming Standard) which builds on folder structure
- Ready for Phase 67 (Config Standard) which builds on config directory conventions
- Ready for Phase 68 (Doc Standard) which builds on docs directory structure

All 35 requirements for v5.0 milestone ARCH-01 through ARCH-05 are now defined.

## Self-Check: PASSED

- [x] docs/ARCHITECTURE_STANDARD.md exists (2318 lines)
- [x] All 7 commits verified (efd708a, 73bdb8e, 5533e9c, 40d240d, dfc9333, e9cd95d, 71898f8)
- [x] 65-01-SUMMARY.md created
- [x] All 5 main sections present
- [x] Migration guide appendix present
- [x] Minimum 200 lines exceeded (2318 lines)

---
*Phase: 65-architecture-standard-foundation*
*Completed: 2026-02-13*
