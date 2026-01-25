---
phase: quick
plan: 003
type: execute
wave: 1
depends_on: []
files_modified: []
autonomous: false
user_setup: []

must_haves:
  truths:
    - "The --help flag displays usage information for 1.4_AssembleManifest.py"
    - "The --dry-run flag validates prerequisites without processing data"
    - "All prerequisite checks pass (1.2 and 1.3 outputs exist)"
    - "Error messages provide clear next steps when prerequisites are missing"
    - "No Unicode character issues on Windows (using [OK] not checkmark)"
  artifacts: []
  key_links: []
---

<objective>
Verify the fourth pipeline script (1.4_AssembleManifest.py) works correctly with --help and --dry-run flags.

Purpose: Ensure the script's CLI interface functions as expected and validates inputs properly before processing the final manifest assembly.
Output: Confirmation that --help shows usage, --dry-run validates successfully, and prerequisite checks work correctly.
</objective>

<execution_context>
@C:\Users\sinas\.claude\get-shit-done\workflows\execute-plan.md
@C:\Users\sinas\.claude\get-shit-done\templates\summary.md
</execution_context>

<context>
@2_Scripts/1_Sample/1.4_AssembleManifest.py
@2_Scripts/shared/dependency_checker.py
@config/project.yaml
@.planning/quick/001-verify-step1-dryrun/001-SUMMARY.md
@.planning/quick/002-verify-step13-dryrun/002-SUMMARY.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Verify --help flag shows usage information</name>
  <files>2_Scripts/1_Sample/1.4_AssembleManifest.py</files>
  <action>Run the script with --help flag and verify it displays usage information including:
  - Script description ("STEP 1.4: Assemble Manifest")
  - Available flags (--dry-run, --help)
  - Proper formatting (no errors, clean output)

  Command:
  python 2_Scripts/1_Sample/1.4_AssembleManifest.py --help

  Expected output should show argparse help with all options documented.
  </action>
  <verify>python 2_Scripts/1_Sample/1.4_AssembleManifest.py --help</verify>
  <done>Help text displays showing description, usage, and all available CLI flags</done>
</task>

<task type="auto">
  <name>Task 2: Verify --dry-run validates prerequisites successfully</name>
  <files>2_Scripts/1_Sample/1.4_AssembleManifest.py, 2_Scripts/shared/dependency_checker.py</files>
  <action>Run the script with --dry-run flag and verify:
  1. Prerequisites are checked for:
     - metadata_linked.parquet exists (output from 1.2_LinkEntities)
     - tenure_monthly.parquet exists (output from 1.3_BuildTenureMap)
  2. Validation passes with success message
  3. No data processing occurs (script exits after validation)
  4. Exit code is 0
  5. Unicode character handling (check for Windows compatibility - should use [OK] not Unicode checkmark)

  Command:
  python 2_Scripts/1_Sample/1.4_AssembleManifest.py --dry-run

  Note: Based on previous tasks 001 and 002 findings, check for the Unicode checkmark () issue on Windows.
  The script at line 483 uses print("All prerequisites validated") - verify this prints correctly on Windows.

  DO NOT make any modifications to input files or outputs.

  If any issues are found (bugs, Unicode errors, path issues), fix them inline following Rule 1 (auto-fix bugs).
  </action>
  <verify>python 2_Scripts/1_Sample/1.4_AssembleManifest.py --dry-run && echo "Exit code: $?"</verify>
  <done>Dry-run completes successfully with prerequisites validated message and exit code 0</done>
</task>

<task type="checkpoint:human-verify">
  <what-built>CLI verification of 1.4_AssembleManifest.py --help and --dry-run flags</what-built>
  <how-to-verify>
  1. Review the output from --help to confirm it shows proper usage
  2. Review the output from --dry-run to confirm validation passes
  3. Verify the messages are clear and helpful
  4. Confirm no data processing occurred during dry-run
  5. Check if any bugs were found and fixed (document in summary)
  </how-to-verify>
  <resume-signal>Type "approved" if both flags work correctly, or describe any issues</resume-signal>
</task>

</tasks>

<verification>
- [ ] --help flag displays usage information
- [ ] --dry-run flag validates inputs without processing
- [ ] All prerequisite checks pass (1.2 and 1.3 outputs exist)
- [ ] Exit code 0 for successful dry-run
- [ ] Clear, helpful error messages if prerequisites fail
- [ ] No Unicode character issues on Windows
</verification>

<success_criteria>
1. The --help flag shows script description and all available CLI arguments
2. The --dry-run flag validates that metadata_linked.parquet exists (1.2 output)
3. The --dry-run flag validates that tenure_monthly.parquet exists (1.3 output)
4. Validation completes with success message and exit code 0
5. No data processing occurs during dry-run (script exits early)
6. Any bugs found are fixed and documented (expecting potential Unicode checkmark issue based on previous tasks)
</success_criteria>

<output>
After completion, create `.planning/quick/003-verify-step14-dryrun/003-SUMMARY.md`
</output>
