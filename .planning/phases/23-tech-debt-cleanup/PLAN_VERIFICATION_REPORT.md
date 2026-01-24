# Phase 23 Plan Verification Report

## Status: ISSUES FOUND

**Phase:** 23-tech-debt-cleanup
**Plans checked:** 4
**Issues:** 2 blocker(s), 1 warning(s)

---

## Blockers (must fix)

### 1. [requirement_coverage] Success Criterion 2 (Utility functions consolidated) not covered

**Dimension:** requirement_coverage
**Severity:** blocker
**Plan:** null (phase-level gap)
**Description:**
Phase success criterion 2 requires: "Utility functions consolidated (compute_file_checksum, print_stat, analyze_missing_values, update_latest_symlink)"

Current state shows inline copies remain in scripts:
- `compute_file_checksum`: Inline copies in 10 scripts (1.1, 1.3, 1.4, 2.1, 2.2, 2.3_VerifyStep2, 3.2, 3.3, 4.1, 4.4)
- `print_stat`: Inline copies in 14 scripts (same 10 plus 4 more)
- `analyze_missing_values`: Inline copies in 10 scripts (same as compute_file_checksum)
- `update_latest_symlink`: Inline copies in 2 scripts (1.5_Utils, 3.4_Utils)

While these functions exist in `shared/observability_utils.py` (Phase 12) and `shared/symlink_utils.py` (Phase 13), none of the 4 plans in Phase 23 remove the inline copies from scripts.

- Plan 23-01: Creates standalone dual_writer.py (DualWriter only)
- Plan 23-02: Documents utilities in README.md (documentation only, no code removal)
- Plan 23-03: Removes inline DualWriter from 12 scripts (DualWriter only, NOT other utilities)
- Plan 23-04: Error handling improvements (unrelated to utility function consolidation)

**Fix hint:**
Either:
1. **Add a new plan (23-05)** to migrate utility functions (compute_file_checksum, print_stat, analyze_missing_values) from inline copies to imports from `shared.observability_utils`
2. **Expand Plan 23-03 scope** to include removing all inline utility functions, not just DualWriter

This would involve:
- For each script with inline utility function, add `from shared.observability_utils import compute_file_checksum, print_stat, analyze_missing_values`
- Remove inline function definitions
- For Utils files (1.5_Utils, 3.4_Utils), either keep unique functions or migrate to shared modules

---

### 2. [requirement_coverage] Success Criterion 3 (All scripts import from shared modules) partially covered

**Dimension:** requirement_coverage
**Severity:** blocker
**Plan:** 23-03
**Description:**
Phase success criterion 3 requires: "All scripts import from shared modules (no duplicate code)"

Plan 23-03 only addresses DualWriter class (12 scripts migrated). It does NOT address utility functions:
- 10 scripts still have inline `compute_file_checksum`
- 14 scripts still have inline `print_stat`
- 10 scripts still have inline `analyze_missing_values`
- 2 Utils scripts have inline `update_latest_symlink`

Additionally, verification in Task 6 has a gap: it uses `grep -r` on subdirectories but doesn't check `2.3_Report.py` (which is in `2_Scripts/` root, not in a subdirectory), so verification could pass even if `2.3_Report.py` still has inline code.

**Fix hint:**
Same as issue #1 above - expand scope to include all inline utility functions, not just DualWriter.

Also fix verification in Task 6 to include `2.3_Report.py`:
```bash
grep -r "class DualWriter:" 2_Scripts/1_Sample/ 2_Scripts/2_Text/ 2_Scripts/3_Financial/ 2_Scripts/4_Econometric/ --include="*.py"
grep "class DualWriter:" 2_Scripts/2.3_Report.py
```

---

## Warnings (should fix)

### 3. [dependency_correctness] Plan 23-04 has wrong dependency configuration

**Dimension:** dependency_correctness
**Severity:** warning
**Plan:** 23-04
**Description:**
Plan 23-04 has `depends_on: []` (Wave 1 dependency pattern) but is assigned to `wave: 2`. Additionally, this plan targets scripts that are modified by Plan 23-03 (same 4 econometric scripts: 4.1.4, 4.1, 4.3, 4.4), so there's an implicit dependency that should be explicit.

The conflict:
- `depends_on: []` = Should be Wave 1 (can run parallel)
- `wave: 2` = Must wait for Wave 1
- Implicit dependency: Plan 23-04 improves error handling in scripts that Plan 23-03 migrates DualWriter from

**Fix hint:**
Change Plan 23-04 frontmatter to:
```yaml
depends_on:
  - 23-03  # Wait for DualWriter migration before improving error handling
```

This correctly reflects that Plan 23-04 should run after Plan 23-03.

---

## Structured Issues

```yaml
issues:
  - plan: null
    dimension: "requirement_coverage"
    severity: "blocker"
    description: "Success Criterion 2 (Utility functions consolidated) not covered - inline copies of compute_file_checksum, print_stat, analyze_missing_values remain in 10-14 scripts"
    fix_hint: "Add plan 23-05 or expand 23-03 to migrate utility functions from inline copies to imports from shared.observability_utils"

  - plan: "23-03"
    dimension: "requirement_coverage"
    severity: "blocker"
    description: "Success Criterion 3 partially covered - only DualWriter addressed, utility functions (compute_file_checksum, print_stat, analyze_missing_values) still inline in 10-14 scripts"
    fix_hint: "Expand Plan 23-03 scope to include all inline utility functions, or add plan 23-05 for utility migration. Fix Task 6 verification to check 2.3_Report.py"

  - plan: "23-04"
    dimension: "dependency_correctness"
    severity: "warning"
    description: "Plan 23-04 has depends_on: [] but is in wave: 2, and implicitly depends on 23-03 (targets same scripts)"
    fix_hint: "Add depends_on: [23-03] to Plan 23-04 frontmatter to reflect implicit dependency"
```

---

## Recommendation

**2 blocker(s) require revision** before execution. The plans fail to address the core tech debt of utility function consolidation, which is explicitly required in the phase success criteria.

The primary issue is that while observability_utils.py and symlink_utils.py contain the consolidated utility functions (from Phases 12 and 13), inline copies of these functions still exist in 10-14 scripts. None of the 4 plans address removing these duplicates.

**Options:**
1. **Add Plan 23-05** to migrate utility functions (create new plan)
2. **Expand Plan 23-03** to include all utility functions (modify existing plan)
3. **Reinterpret success criteria** to mean "consolidated utilities exist in shared modules" rather than "no inline copies remain" (update ROADMAP)

Option 1 or 2 recommended to achieve the stated goal of "eliminate code duplication."

---

## What IS Well-Planned

The following aspects of the plans are solid:
- ✅ Plan 23-01: DualWriter extraction with re-export pattern is good design
- ✅ Plan 23-02: Documentation approach is appropriate for discoverability
- ✅ Plan 23-04: Error handling improvements follow Phase 7 patterns correctly
- ✅ Task completeness: All tasks have files, action, verify, done
- ✅ Key links: All plans have clear wiring between artifacts
- ✅ Must-haves derivation: Truths are user-observable and specific

The gap is primarily in scope - the plans don't address all inline code duplication required by the phase success criteria.
