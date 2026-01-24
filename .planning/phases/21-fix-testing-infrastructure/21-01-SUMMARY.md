---
phase: 21-fix-testing-infrastructure
plan: 01
subsystem: testing
tags: pytest, subprocess, PYTHONPATH, regex, integration-tests

# Dependency graph
requires:
  - phase: 19-scaling-infrastructure-testing-integration
    provides: Integration test path fixes with REPO_ROOT
provides:
  - SUBPROCESS_ENV constant with PYTHONPATH in all 5 integration test files
  - All subprocess.run() calls use env=SUBPROCESS_ENV parameter
  - Regex-based observability verification instead of AST parsing
  - Integration tests can now run from any directory without ModuleNotFoundError
affects:
  - Phase 22 (Recreate Missing Script & Evidence)
  - Phase 23 (Core Tech Debt Cleanup)
  - CI/CD workflow reliability

# Tech tracking
tech-stack:
  added: []
  patterns:
    - SUBPROCESS_ENV constant pattern: DRY configuration for subprocess calls with PYTHONPATH
    - Absolute PYTHONPATH via subprocess env parameter
    - Regex pattern matching for code verification (resilient to formatting)
    - os.environ spread pattern to preserve existing environment

key-files:
  created: []
  modified:
    - tests/integration/test_full_pipeline.py
    - tests/integration/test_observability_integration.py
    - tests/integration/test_pipeline_step1.py
    - tests/integration/test_pipeline_step2.py
    - tests/integration/test_pipeline_step3.py

key-decisions:
  - "Use module-level SUBPROCESS_ENV constant for all integration test subprocess calls"
  - "Replace AST parsing with regex pattern matching for robustness"

patterns-established:
  - Pattern 1: SUBPROCESS_ENV = {"PYTHONPATH": str(REPO_ROOT / "2_Scripts"), **os.environ}
  - Pattern 2: subprocess.run(..., env=SUBPROCESS_ENV, ...)
  - Pattern 3: Regex checks: re.search(r"^pattern", content, re.MULTILINE)
  - Pattern 4: Absolute paths via REPO_ROOT constant in all test files

# Metrics
duration: 8min
completed: 2026-01-24
---

# Phase 21 Plan 01: Fix Testing Infrastructure Summary

**SUBPROCESS_ENV constant with PYTHONPATH and regex-based observability checks eliminate ModuleNotFoundError and AST parsing errors in integration tests**

## Performance

- **Duration:** 8 min
- **Started:** 2026-01-24T12:31:23Z
- **Completed:** 2026-01-24T12:39:23Z
- **Tasks:** 4
- **Files modified:** 5

## Accomplishments
- Added SUBPROCESS_ENV constant with PYTHONPATH to all 5 integration test files
- Updated all 4 subprocess.run() calls to use env=SUBPROCESS_ENV parameter
- Replaced broken AST parsing with robust regex pattern matching in test_observability_integration.py
- Added REPO_ROOT constant to test_pipeline_step3.py (was missing)
- Fixed relative paths in test_pipeline_step3.py to use REPO_ROOT
- Integration tests now run without ModuleNotFoundError (PYTHONPATH configured)
- Observability integration test passes with regex pattern matching

## Task Commits

Each task was committed atomically:

1. **Task 1: Add SUBPROCESS_ENV constant to integration test files** - `471fe3b` (feat)
2. **Task 2: Update subprocess.run() calls to use SUBPROCESS_ENV** - `d66d98c` (fix)
3. **Task 3: Replace AST parsing with regex in observability tests** - `f25ea2a` (fix)

**Plan metadata:** (not yet committed)

_Note: Task 4 (verification) documented pre-existing script bugs, not infrastructure issues._

## Files Created/Modified
- `tests/integration/test_full_pipeline.py` - Added import os, SUBPROCESS_ENV constant, updated subprocess.run with env=SUBPROCESS_ENV
- `tests/integration/test_observability_integration.py` - Replaced import ast with import re, added SUBPROCESS_ENV, replaced AST parsing with check_script_observability() helper using regex
- `tests/integration/test_pipeline_step1.py` - Added import os, SUBPROCESS_ENV constant, updated subprocess.run with env=SUBPROCESS_ENV
- `tests/integration/test_pipeline_step2.py` - Added import os, SUBPROCESS_ENV constant, updated subprocess.run with env=SUBPROCESS_ENV
- `tests/integration/test_pipeline_step3.py` - Added import os, REPO_ROOT constant, SUBPROCESS_ENV constant, fixed all relative paths to use REPO_ROOT, updated subprocess.run with env=SUBPROCESS_ENV

## Decisions Made
None - followed plan exactly as specified.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

**Integration test failures (pre-existing script bugs, not infrastructure issues):**

Integration tests were run locally with `pytest tests/integration/ -v -m integration --tb=short`. Test results showed:

**Observability test (PASSED ✓):**
- test_1_1_observability: PASSED - Regex pattern matching works correctly
- No ModuleNotFoundError in any test - PYTHONPATH configuration successful

**Step 1 tests (1 failure, 2 skipped):**
- test_stats_json_generation_step1: FAILED - Stats.json uses "input" field but test expects "inputs" (script bug)
- sample_input_data fixture: SKIPPED - Sample data not yet available
- test_row_count_validation_step1: SKIPPED - Depends on 1.1_CleanMetadata.py output

**Step 2 tests (5 failures):**
- test_step2_full_pipeline: FAILED - KeyError 'manifest' in 2.1_TokenizeAndCount.py line 670 (script bug)
- test_output_file_format_step2: FAILED - Column 'Total_Words' not found (test expects old schema)
- test_word_count_validation_step2: FAILED - Column 'Total_Words' not found (test expects old schema)
- test_step2_multiple_years[2002/2010/2018]: FAILED - Column 'Total_Words' not found (test expects old schema)

**Step 3 tests (1 failure, 3 skipped):**
- test_step3_full_pipeline: FAILED - NameError 'get_git_sha' is not defined in 3.0_BuildFinancialFeatures.py line 294 (script bug)
- test_merge_diagnostics_step3: SKIPPED - Depends on 3.0_BuildFinancialFeatures.py output
- test_financial_variables_validation: SKIPPED - Depends on 3.0_BuildFinancialFeatures.py output
- test_step3_data_source_integration: SKIPPED - Depends on 3.0_BuildFinancialFeatures.py output

**Key findings:**
1. **No ModuleNotFoundError** - All integration tests found shared modules via PYTHONPATH ✓
2. **No AST parsing errors** - Observability test uses regex pattern matching ✓
3. Test failures are due to pre-existing script bugs (KeyError 'manifest', NameError 'get_git_sha', schema mismatches)
4. These script bugs existed before Phase 21 and are not related to test infrastructure
5. Test infrastructure fixes (SUBPROCESS_ENV + regex) are working correctly

These script bugs should be addressed in future phases (Phase 22, 23, or 24) but are out of scope for Phase 21 (which focused on test infrastructure only).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 21-01 complete. Test infrastructure now properly configured:

**Ready for Phase 22 (Recreate Missing Script & Evidence):**
- Integration tests can run without ModuleNotFoundError
- Observability tests use robust regex pattern matching
- Test framework is stable and ready for additional test cases

**Pre-existing issues to address in future phases:**
- 2.1_TokenizeAndCount.py: KeyError 'manifest' at line 670
- 3.0_BuildFinancialFeatures.py: NameError 'get_git_sha' undefined at line 294
- Integration test schema mismatches (test expects different column names than scripts output)

These are separate from test infrastructure and should be prioritized in subsequent phases.

---
*Phase: 21-fix-testing-infrastructure*
*Completed: 2026-01-24*
