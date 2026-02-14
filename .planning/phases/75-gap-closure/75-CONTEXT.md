# Phase 75: Architecture Compliance Gap Closure - Context

**Gathered:** 2026-02-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Eliminate all legacy import patterns and integration gaps to achieve 100% src-layout compliance per ARCHITECTURE_STANDARD.md. This is a gap closure phase addressing technical debt identified in the v6.0 milestone audit.

Scope is fixed by audit findings — no new capabilities, only migration of existing code to standards.

</domain>

<decisions>
## Implementation Decisions

### Migration Approach
- Standard migration patterns from Phase 69-74 apply
- Incremental migration with per-plan verification
- Each plan targets specific gap with clear scope

### Claude's Discretion
- Import migration order within each plan
- Specific file-by-file migration approach
- Test execution timing (per-file or batched)
- Error handling during migration

</decisions>

<specifics>
## Specific Ideas

No specific requirements — this is technical debt closure following established patterns from Phases 69-74.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

## Gap Summary (from v6.0 Audit)

| Gap | Files Affected | Resolution Plan |
|-----|----------------|-----------------|
| sys.path.insert() workarounds | 5 sample scripts | 75-01 |
| Legacy `from shared.*` imports | 21 test files | 75-02 |
| LoggingSettings not consumed | logging/config.py | 75-03 |
| pandas/numpy version in tests | panel_ols tests | 75-04 |
| Final verification | All migrated files | 75-05 |

## Success Criteria

1. Zero `sys.path.insert()` calls in src/f1d/ codebase
2. Zero `from shared.*` imports in tests/ (all use `from f1d.shared.*`)
3. LoggingSettings integrated with configure_logging() for unified config
4. All sample scripts import using proper `f1d.shared.*` namespace
5. All tests execute without PYTHONPATH manipulation
6. mypy passes on all migrated files

---

*Phase: 75-gap-closure*
*Context gathered: 2026-02-14*
