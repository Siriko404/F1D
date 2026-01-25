---
phase: quick
plan: 001
type: execute
wave: 1
depends_on: []
files_modified: []
autonomous: true
user_setup: []

must_haves:
  truths:
    - "The --help flag displays usage information"
    - "The --dry-run flag validates prerequisites without processing data"
    - "All prerequisite checks pass (input files exist)"
    - "Error messages provide clear next steps when prerequisites are missing"
  artifacts: []
  key_links: []
---

<objective>
Verify the first pipeline script (1.1_CleanMetadata.py) works correctly with --help and --dry-run flags.

Purpose: Ensure the script's CLI interface functions as expected and validates inputs properly before processing data.
Output: Confirmation that --help shows usage, --dry-run validates successfully, and prerequisite checks work correctly.
</objective>

<execution_context>
@C:\Users\sinas\.claude\get-shit-done\workflows\execute-plan.md
@C:\Users\sinas\.claude\get-shit-done\templates\summary.md
</execution_context>

<context>
@2_Scripts/1_Sample/1.1_CleanMetadata.py
@config/project.yaml
</context>

<tasks>

<task type="auto">
  <name>Task 1: Verify --help flag shows usage information</name>
  <files>2_Scripts/1_Sample/1.1_CleanMetadata.py</files>
  <action>Run the script with --help flag and verify it displays usage information including:
  - Script description
  - Available flags (--dry-run, --year-start, --year-end, --help)
  - Proper formatting (no errors, clean output)

  Command:
  python 2_Scripts/1_Sample/1.1_CleanMetadata.py --help

  Expected output should show argparse help with all options documented.
  </action>
  <verify>python 2_Scripts/1_Sample/1.1_CleanMetadata.py --help</verify>
  <done>Help text displays showing description, usage, and all available CLI flags</done>
</task>

<task type="auto">
  <name>Task 2: Verify --dry-run validates prerequisites successfully</name>
  <files>2_Scripts/1_Sample/1.1_CleanMetadata.py, 2_Scripts/shared/dependency_checker.py</files>
  <action>Run the script with --dry-run flag and verify:
  1. Prerequisites are checked (Unified-info.parquet exists in 1_Inputs/)
  2. Validation passes with success message
  3. No data processing occurs (script exits after validation)
  4. Exit code is 0

  Command:
  python 2_Scripts/1_Sample/1.1_CleanMetadata.py --dry-run

  The script should:
  - Print "Dry-run mode: validating inputs..."
  - Call validate_prerequisites() which checks required_files
  - Print "All prerequisites validated" (check_mark from dependency_checker.py)
  - Exit with code 0

  DO NOT make any modifications to input files or outputs.
  </action>
  <verify>python 2_Scripts/1_Sample/1.1_CleanMetadata.py --dry-run && echo "Exit code: $?"</verify>
  <done>Dry-run completes successfully with "All prerequisites validated" message and exit code 0</done>
</task>

<task type="checkpoint:human-verify">
  <what-built>CLI verification of 1.1_CleanMetadata.py --help and --dry-run flags</what-built>
  <how-to-verify>
  1. Review the output from --help to confirm it shows proper usage
  2. Review the output from --dry-run to confirm validation passes
  3. Verify the messages are clear and helpful
  4. Confirm no data processing occurred during dry-run
  </how-to-verify>
  <resume-signal>Type "approved" if both flags work correctly, or describe any issues</resume-signal>
</task>

</tasks>

<verification>
- [ ] --help flag displays usage information
- [ ] --dry-run flag validates inputs without processing
- [ ] All prerequisite checks pass (input file exists)
- [ ] Exit code 0 for successful dry-run
- [ ] Clear, helpful error messages if prerequisites fail
</verification>

<success_criteria>
1. The --help flag shows script description and all available CLI arguments
2. The --dry-run flag validates that Unified-info.parquet exists in 1_Inputs/
3. Validation completes with "All prerequisites validated" or similar success message
4. No data processing occurs during dry-run (script exits early)
5. Exit code 0 indicates successful validation
</success_criteria>

<output>
After completion, create `.planning/quick/001-verify-step1-dryrun/001-SUMMARY.md`
</output>
