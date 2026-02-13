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
  - Version management with active variants policy (ARCH-04)
  - Archive and deprecated code handling strategy (ARCH-05)
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
    - Version variants (V1/V2) as active subpackages

key-files:
  created:
    - docs/ARCHITECTURE_STANDARD.md
  modified: []

key-decisions:
  - "Adopt src-layout over flat layout (PyPA recommendation)"
  - "BOTH V1 and V2 are active variants - no legacy/canonical distinction"
  - "Version suffixes (V1, V2) become subpackages under stage packages"
  - "Data separated by lifecycle: raw/interim/processed/external"
  - "30-day deprecation period before archival"
  - "Module tier system with quality bars (Tier 1-3)"
  - "Include migration guide as appendix rather than separate document"

patterns-established:
  - "Pattern: src/f1d/ package structure with stage subpackages"
  - "Pattern: Version variants as v1/ and v2/ subpackages (both active)"
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
- Documented archive structure and deprecated code handling
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
  - Section 5: Archive and deprecated code handling
  - Appendix A: Migration guide (6 phases)
  - Appendix B: Related standards reference

## Decisions Made

1. **src-layout over flat layout** - PyPA recommended pattern prevents import issues, better for packaging
2. **Both V1 and V2 as active variants** - Version suffixes distinguish methodology variants, both remain active
3. **Version variants as subpackages** - V1 becomes v1/ subpackage, V2 becomes v2/ subpackage
4. **Data lifecycle stages** - raw/interim/processed/external follows Cookiecutter Data Science conventions
5. **30-day deprecation** - Standard practice for code deprecation before archival
6. **Module tier system** - Quality bars scaled by importance (Tier 1: core shared, Tier 2: stage-specific, Tier 3: scripts)
7. **Migration guide as appendix** - Keep all architecture documentation in single document
8. **Dated subdirectories** - YYYY-MM-DD format for data versioning ensures proper sorting
9. **manifest.json for archive** - Machine-readable tracking enables tooling support

## Post-Completion Correction (2026-02-13)

After initial completion, the user clarified that:
- **BOTH V1 and V2 scripts are active in the pipeline**
- There is **NO V1 legacy / V2 canonical distinction**
- Both versions represent different processing approaches, both actively maintained

### Corrections Applied

1. **Section 4: Version Management** - Rewrote from "Single Active Version Policy" to "Active Versions Policy"
   - Both V1 and V2 described as active pipeline variants
   - Version suffixes distinguish methodology variants, not legacy/canonical
   - Target state shows v1/ and v2/ as subpackages under each stage

2. **Section 5: Archive and Deprecated Code** - Updated archive references
   - Removed `legacy/` subdirectory (not needed - V1 is active)
   - Archive only for truly deprecated/abandoned code
   - Added explicit note that V1 is NOT archived

3. **Migration Guide (Appendix A)** - Updated migration path
   - Both V1 and V2 migrate to src/f1d/*/v1/ and src/f1d/*/v2/
   - No archival of V1 planned
   - Phase 5 now cleans up old directories (not archives V1)

4. **Document Structure (Section 1)** - Updated target structure
   - Added v1/ and v2/ subpackages under financial/ and econometric/
   - Changed `.___archive/legacy/` to `.___archive/deprecated/`

### Key Changes to Terminology

| Before | After |
|--------|-------|
| "Single Active Version Policy" | "Active Versions Policy" |
| "V1 - Legacy" | "V1 - Active variant" |
| "V2 - Canonical/Current" | "V2 - Active variant" |
| "Archive V1 code" | "Clean up old directories (both variants migrated)" |
| `.___archive/legacy/` | `.___archive/deprecated/` (only truly deprecated code) |

## Deviations from Plan

Correction made post-completion based on user clarification that both V1 and V2 are active in the pipeline.

## Issues Encountered

Initial document incorrectly described V1 as legacy and V2 as canonical. This was corrected after user clarification.

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
- [x] No reference to V1 as "legacy" or "archived"
- [x] No reference to V2 as "canonical" or "single active version"
- [x] Both V1 and V2 described as active pipeline variants

---
*Phase: 65-architecture-standard-foundation*
*Completed: 2026-02-13*
*Corrected: 2026-02-13*
