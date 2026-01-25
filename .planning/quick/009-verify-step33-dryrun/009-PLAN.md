---
phase: quick
plan: 009
type: execute
wave: 1
depends_on: []
files_modified:
  - 2_Scripts/3_Financial/3.3_EventFlags.py
autonomous: true
user_setup: []

must_haves:
  truths:
    - "--help flag displays usage information without encoding errors"
    - "--dry-run flag validates prerequisites (SDC directory, Step 1.4 output)"
    - "No Unicode encoding errors on Windows cp1252"
    - "Exit code 0 on successful validation"
    - "Exit code 1 on missing prerequisites with clear error messages"
  artifacts:
    - path: "2_Scripts/3_Financial/3.3_EventFlags.py"
      provides: "Event flags computation with CLI validation"
      min_lines: 600
  key_links:
    - from: "3.3_EventFlags.py"
      to: "shared/dependency_checker.py"
      via: "validate_prerequisites function"
      pattern: "from shared.dependency_checker import validate_prerequisites"
---

<objective>
Verify functionality of script 3.3_EventFlags.py with --help and --dry-run flags, and fix any Unicode character bugs for Windows cp1252 compatibility.

Purpose: Ensure the Step 3.3 script can validate its prerequisites without execution and handles Windows console encoding correctly.
Output: Working CLI flags with ASCII-only output for Windows compatibility.
</objective>

<execution_context>
@C:\Users\sinas\.claude\get-shit-done\workflows\execute-plan.md
@C:\Users\sinas\.claude\get-shit-done\templates\summary.md
</execution_context>

<context>
@.planning/quick/008-verify-step32-dryrun/008-SUMMARY.md
@2_Scripts/3_Financial/3.3_EventFlags.py
@2_Scripts/shared/dependency_checker.py

# Pattern from previous quick tasks (001-008):
All previous scripts (1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 3.0, 3.1, 3.2) had the same Windows Unicode bug:
- Line with `print("All prerequisites validated")` used Unicode checkmark (U+2713)
- Fixed by replacing with `[OK]` or removing redundant print (dependency_checker already prints [OK])

# Known issues to watch for in 3.3_EventFlags.py:
- Line 620 has Unicode checkmark character: `print("All prerequisites validated")` with checkmark (U+2713)
- The check_prerequisites() function calls validate_prerequisites() which already prints "[OK] All prerequisites validated"
- The script's own print on line 620 is redundant
</context>

<tasks>

<task type="auto">
  <name>Verify --help flag and fix Unicode bug</name>
  <files>2_Scripts/3_Financial/3.3_EventFlags.py</files>
  <action>
    1. First, verify --help flag works:
       ```bash
       python 2_Scripts/3_Financial/3.3_EventFlags.py --help
       ```

    2. Fix the Unicode checkmark bug on line 620:
       - Current: `print("All prerequisites validated")` (with Unicode checkmark U+2713)
       - Fix: Remove this redundant print statement since validate_prerequisites() already prints "[OK] All prerequisites validated"

    3. After fixing, run the script with --dry-run flag:
       ```bash
       python 2_Scripts/3_Financial/3.3_EventFlags.py --dry-run
       ```

    4. Verify the following validations occur:
       - SDC directory exists (1_Inputs/SDC)
       - Step 1.4 output exists (master_sample_manifest.parquet)

    The fix:
    ```python
    # Line 617-621, change from:
    if args.dry_run:
        print("Dry-run mode: validating inputs...")
        check_prerequisites(root)
        print("All prerequisites validated")  # <- REMOVE THIS LINE (has Unicode char U+2713)
        sys.exit(0)

    # To:
    if args.dry_run:
        print("Dry-run mode: validating inputs...")
        check_prerequisites(root)
        sys.exit(0)
    ```

    Rationale: validate_prerequisites() already prints "[OK] All prerequisites validated" in dependency_checker.py, making the script's print redundant and it contains the problematic Unicode character.
  </action>
  <verify>
    --help completes with exit code 0 and displays usage text. --dry-run completes with exit code 0 or 1 (1 if prerequisites missing, which is expected), and no UnicodeEncodeError occurs.
  </verify>
  <done>
    Unicode character removed, --help flag displays usage, --dry-run flag validates prerequisites correctly with ASCII-only output.
  </done>
</task>

</tasks>

<verification>
After completion, verify:
1. `python 2_Scripts/3_Financial/3.3_EventFlags.py --help` displays usage without encoding errors
2. `python 2_Scripts/3_Financial/3.3_EventFlags.py --dry-run` validates prerequisites and prints ASCII-only output
3. No Unicode checkmark characters remain in the script
4. Exit codes are correct (0 for success/help, 1 for missing prerequisites)
</verification>

<success_criteria>
- Script uses ASCII-only output (no Unicode checkmark)
- --help flag displays usage information
- --dry-run flag validates SDC directory and Step 1.4 output
- Clear error messages for missing prerequisites
- Exit code 1 when prerequisites fail
- Exit code 0 when validation succeeds
</success_criteria>

<output>
After completion, create `.planning/quick/009-verify-step33-dryrun/009-SUMMARY.md`
</output>
