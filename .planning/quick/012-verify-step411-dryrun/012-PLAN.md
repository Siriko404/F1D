---
phase: quick
plan: 012
type: execute
wave: 1
depends_on: [011]
files_modified: [2_Scripts/4_Econometric/4.1.1_EstimateCeoClarity_CeoSpecific.py]
autonomous: true
gap_closure: false

must_haves:
  truths:
    - "Script accepts --help flag and displays usage"
    - "Script accepts --dry-run flag and validates prerequisites"
    - "Script validates Steps 2.2, 3.1, 3.2 outputs exist"
    - "No Unicode encoding errors on Windows terminal"
  artifacts:
    - path: "2_Scripts/4_Econometric/4.1.1_EstimateCeoClarity_CeoSpecific.py"
      provides: "CEO-specific clarity estimation script"
      min_lines: 860
  key_links:
    - from: "4.1.1_EstimateCeoClarity_CeoSpecific.py"
      to: "shared.dependency_checker"
      via: "from shared.dependency_checker import validate_prerequisites"
      pattern: "from shared\\.dependency_checker"
---

# Quick Task 012: Verify Step 4.1.1 Dry Run

## Objective

Verify that `4.1.1_EstimateCeoClarity_CeoSpecific.py` works correctly with `--help` and `--dry-run` flags. This script estimates CEO-specific clarity scores using CEO fixed effects regression.

**Purpose:** Ensure CLI validation and prerequisite checking work before full execution.

**Output:** Working --help and --dry-run modes, identified encoding issues fixed.

## Context

@.planning/quick/011-verify-step41-dryrun/011-SUMMARY.md

**Pattern from task 011:**
- sys.path.insert already present (lines 46-47)
- CONFIG dictionary defined (lines 156-172)
- All required imports present (lines 100-128)
- **Known issue:** Unicode checkmark at line 857 (Windows cp1252 incompatibility)

**Prerequisites checked by this script:**
- Step 2.2: `linguistic_variables.parquet`
- Step 3.1: `firm_controls.parquet`
- Step 3.2: `market_variables.parquet`

## Tasks

<task type="auto">
  <name>Task 1: Test --help flag</name>
  <files>2_Scripts/4_Econometric/4.1.1_EstimateCeoClarity_CeoSpecific.py</files>
  <action>Run: python 2_Scripts/4_Econometric/4.1.1_EstimateCeoClarity_CeoSpecific.py --help

Expected output should show:
- Script description
- --dry-run flag with help text

Do NOT fix anything yet - just verify help displays correctly.
  </action>
  <verify>Exit code 0, help text displays showing --dry-run option</verify>
  <done>--help flag works and shows proper usage information</done>
</task>

<task type="auto">
  <name>Task 2: Test --dry-run flag and fix any issues</name>
  <files>2_Scripts/4_Econometric/4.1.1_EstimateCeoClarity_CeoSpecific.py</files>
  <action>Run: python 2_Scripts/4_Econometric/4.1.1_EstimateCeoClarity_CeoSpecific.py --dry-run

Expected behavior:
1. Validates prerequisites (Steps 2.2, 3.1, 3.2)
2. Reports missing or present files
3. Exits with code 0 if validation passes

**Known bug from line 857:** Unicode checkmark (✓) causes Windows encoding error.
Fix: Replace "✓" with "[OK]" on line 857 for Windows cp1252 compatibility.

If any other issues emerge:
- Missing imports: Add to import block
- Missing sys.path.insert: Already present at lines 46-47
- Missing CONFIG: Already defined at lines 156-172
  </action>
  <verify>--dry-run completes without UnicodeEncodeError, shows prerequisite validation results</verify>
  <done>--dry-run flag works correctly, prerequisites are validated</done>
</task>

<task type="checkpoint:human-verify">
  <what-built>Fixed --help and --dry-run functionality for 4.1.1_EstimateCeoClarity_CeoSpecific.py</what-built>
  <how-to-verify>
1. Run: python 2_Scripts/4_Econometric/4.1.1_EstimateCeoClarity_CeoSpecific.py --help
   - Should display usage information

2. Run: python 2_Scripts/4_Econometric/4.1.1_EstimateCeoClarity_CeoSpecific.py --dry-run
   - Should validate prerequisites for Steps 2.2, 3.1, 3.2
   - Should show no Unicode encoding errors on Windows

If both commands work correctly, type "approved" to continue.
  </how-to-verify>
  <resume-signal>Type "approved" or describe issues</resume-signal>
</task>

## Success Criteria

- `--help` flag displays usage without errors
- `--dry-run` flag validates prerequisites and exits cleanly
- No Unicode encoding errors on Windows (checkmark replaced with [OK])
- Pattern established from task 011 is applied

## Output

After completion, create `.planning/quick/012-verify-step411-dryrun/012-SUMMARY.md`
