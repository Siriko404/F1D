---
phase: quick
plan: 004
type: execute
wave: 1
depends_on: [quick-003]
files_modified: [2_Scripts/2_Text/2.1_TokenizeAndCount.py]
autonomous: true
user_setup: []

must_haves:
  truths:
    - "User can run script with --help flag to see usage"
    - "User can run script with --dry-run flag to validate prerequisites"
    - "Prerequisite checker validates 1.4_AssembleManifest output exists"
    - "Prerequisite checker validates LM dictionary file exists"
    - "Script exits with code 0 on successful dry-run"
    - "Script works on Windows without Unicode encoding errors"
  artifacts:
    - path: "2_Scripts/2_Text/2.1_TokenizeAndCount.py"
      provides: "Tokenization script with CLI validation"
      contains: "parse_arguments, check_prerequisites"
    - path: "2_Scripts/shared/dependency_checker.py"
      provides: "Prerequisite validation utilities"
      contains: "validate_prerequisites"
  key_links:
    - from: "2_Scripts/2_Text/2.1_TokenizeAndCount.py"
      to: "2_Scripts/shared/dependency_checker.py"
      via: "import statement at line 114"
      pattern: "from shared.dependency_checker import validate_prerequisites"
---

<objective>
Verify 2.1_TokenizeAndCount.py CLI flags work correctly (--help, --dry-run)

Purpose: Ensure the first Step 2 script can be run manually with proper CLI validation
Output: Working --help and --dry-run flags with Windows-compatible output
</objective>

<execution_context>
@C:\Users\sinas\.claude\get-shit-done\workflows\execute-plan.md
@C:\Users\sinas\.claude\get-shit-done\templates\summary.md
</execution_context>

<context>
@.planning/quick/003-verify-step14-dryrun/003-SUMMARY.md
@2_Scripts/2_Text/2.1_TokenizeAndCount.py
@2_Scripts/shared/dependency_checker.py

# Known patterns from quick tasks 001-003:
- Windows cp1252 encoding does NOT support Unicode checkmarks (U+2713)
- Solution: Use [OK] instead of checkmark characters
- dependency_checker.py already uses [OK] pattern (line 77)
</context>

<tasks>

<task type="auto">
  <name>Task 1: Verify --help flag displays correctly</name>
  <files>2_Scripts/2_Text/2.1_TokenizeAndCount.py</files>
  <action>
    Run: python 2_Scripts/2_Text/2.1_TokenizeAndCount.py --help

    Verify:
    - Script name and description appear
    - --dry-run flag is documented
    - --dictionary flag is documented
    - No Unicode encoding errors on Windows

    If Unicode errors occur:
    - Find the Unicode character causing the error
    - Replace with [OK] or plain ASCII equivalent
  </action>
  <verify>python 2_Scripts/2_Text/2.1_TokenizeAndCount.py --help exits with code 0 and shows usage</verify>
  <done>--help flag shows script description and available flags without errors</done>
</task>

<task type="auto">
  <name>Task 2: Verify --dry-run validates prerequisites</name>
  <files>2_Scripts/2_Text/2.1_TokenizeAndCount.py</files>
  <action>
    Run: python 2_Scripts/2_Text/2.1_TokenizeAndCount.py --dry-run

    Verify validation checks:
    - LM dictionary exists at 1_Inputs/Loughran-McDonald_MasterDictionary_1993-2024.csv
    - 1.4_AssembleManifest output exists at 4_Outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet
    - Exit code is 0 on success
    - Message shows "[OK] All prerequisites validated" (Windows-compatible)

    Expected prerequisite failures if missing:
    - Error lists missing LM dictionary path
    - Error lists missing 1.4_AssembleManifest output

    If Unicode errors occur:
    - Check dependency_checker.py output (already uses [OK])
    - Check 2.1_TokenizeAndCount.py for any Unicode characters
  </action>
  <verify>python 2_Scripts/2_Text/2.1_TokenizeAndCount.py --dry-run exits 0 and validates both prerequisites</verify>
  <done>--dry-run flag validates LM dictionary and 1.4_AssembleManifest output, exit code 0</done>
</task>

</tasks>

<verification>
After completion:
1. --help shows usage without Unicode errors
2. --dry-run validates both LM dictionary and 1.4_AssembleManifest output
3. Exit code 0 on successful validation
4. Output is Windows-compatible (no Unicode encoding errors)
</verification>

<success_criteria>
- Both --help and --dry-run flags work correctly
- No Unicode encoding errors on Windows
- Prerequisite validation correctly identifies required inputs
- Exit code 0 on successful dry-run
</success_criteria>

<output>
After completion, create `.planning/quick/004-verify-step21-dryrun/004-SUMMARY.md`
</output>
