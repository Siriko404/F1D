---
phase: quick
plan: 005
type: execute
wave: 1
depends_on: [quick-004]
files_modified: [2_Scripts/2_Text/2.2_ConstructVariables.py]
autonomous: true
user_setup: []

must_haves:
  truths:
    - "User can run script with --help flag to see usage"
    - "User can run script with --dry-run flag to validate prerequisites"
    - "Prerequisite checker validates 2.1_TokenizeAndCount output exists"
    - "Script exits with code 0 on successful dry-run"
    - "Script works on Windows without Unicode encoding errors"
  artifacts:
    - path: "2_Scripts/2_Text/2.2_ConstructVariables.py"
      provides: "Text variable construction script with CLI validation"
      contains: "parse_arguments, check_prerequisites"
    - path: "2_Scripts/shared/dependency_checker.py"
      provides: "Prerequisite validation utilities"
      contains: "validate_prerequisites"
  key_links:
    - from: "2_Scripts/2_Text/2.2_ConstructVariables.py"
      to: "2_Scripts/shared/dependency_checker.py"
      via: "import statement at line 85"
      pattern: "from shared.dependency_checker import validate_prerequisites"
    - from: "2_Scripts/2_Text/2.2_ConstructVariables.py"
      to: "4_Outputs/2_Textual_Analysis/2.1_Tokenized/latest/linguistic_counts.parquet"
      via: "check_prerequisites validates prerequisite step output"
      pattern: "2.1_TokenizeAndCount.*linguistic_counts"
---

<objective>
Verify 2.2_ConstructVariables.py CLI flags work correctly (--help, --dry-run)

Purpose: Ensure the second Step 2 script can be run manually with proper CLI validation
Output: Working --help and --dry-run flags with Windows-compatible output
</objective>

<execution_context>
@C:\Users\sinas\.claude\get-shit-done\workflows\execute-plan.md
@C:\Users\sinas\.claude\get-shit-done\templates\summary.md
</execution_context>

<context>
@.planning/quick/004-verify-step21-dryrun/004-SUMMARY.md
@2_Scripts/2_Text/2.2_ConstructVariables.py
@2_Scripts/shared/dependency_checker.py

# Known patterns from quick tasks 001-004:
- Windows cp1252 encoding does NOT support Unicode checkmarks (U+2713)
- Solution: Use [OK] instead of checkmark characters
- dependency_checker.py already uses [OK] pattern (line 77)

# Known issue in 2.2_ConstructVariables.py:
- Line 669 contains Unicode checkmark: print("All prerequisites validated")
- This needs to be replaced with [OK] for Windows compatibility
</context>

<tasks>

<task type="auto">
  <name>Task 1: Verify --help flag displays correctly</name>
  <files>2_Scripts/2_Text/2.2_ConstructVariables.py</files>
  <action>
    Run: python 2_Scripts/2_Text/2.2_ConstructVariables.py --help

    Verify:
    - Script name and description appear
    - --dry-run flag is documented
    - No Unicode encoding errors on Windows

    If Unicode errors occur:
    - Find the Unicode character causing the error
    - Replace with [OK] or plain ASCII equivalent
  </action>
  <verify>python 2_Scripts/2_Text/2.2_ConstructVariables.py --help exits with code 0 and shows usage</verify>
  <done>--help flag shows script description and available flags without errors</done>
</task>

<task type="auto">
  <name>Task 2: Fix Windows Unicode character and verify --dry-run</name>
  <files>2_Scripts/2_Text/2.2_ConstructVariables.py</files>
  <action>
    Step 1: Fix the Unicode checkmark at line 669
    - Change: print("All prerequisites validated")
    - To: print("[OK] All prerequisites validated")

    Step 2: Run: python 2_Scripts/2_Text/2.2_ConstructVariables.py --dry-run

    Verify validation checks:
    - 2.1_TokenizeAndCount output exists at 4_Outputs/2_Textual_Analysis/2.1_Tokenized/latest/linguistic_counts*.parquet
    - Exit code is 0 on success
    - Message shows "[OK] All prerequisites validated" (Windows-compatible)

    Expected prerequisite failures if missing:
    - Error lists missing 2.1_TokenizeAndCount output
    - Error suggests running 2.1_TokenizeAndCount first
  </action>
  <verify>python 2_Scripts/2_Text/2.2_ConstructVariables.py --dry-run exits 0 and validates prerequisite, no Unicode errors</verify>
  <done>--dry-run flag validates 2.1_TokenizeAndCount output, exit code 0, no Unicode errors</done>
</task>

</tasks>

<verification>
After completion:
1. --help shows usage without Unicode errors
2. --dry-run validates 2.1_TokenizeAndCount output (linguistic_counts.parquet)
3. Exit code 0 on successful validation
4. Output is Windows-compatible (no Unicode encoding errors)
5. Unicode checkmark replaced with [OK]
</verification>

<success_criteria>
- Both --help and --dry-run flags work correctly
- No Unicode encoding errors on Windows (checkmark replaced with [OK])
- Prerequisite validation correctly identifies 2.1_TokenizeAndCount as required
- Exit code 0 on successful dry-run
</success_criteria>

<output>
After completion, create `.planning/quick/005-verify-step22-dryrun/005-SUMMARY.md`
</output>
