---
phase: quick
plan: 006
type: execute
wave: 1
depends_on: [quick-005]
files_modified: [2_Scripts/3_Financial/3.0_BuildFinancialFeatures.py]
autonomous: true
user_setup: []

must_haves:
  truths:
    - "User can run script with --help flag to see usage"
    - "User can run script with --dry-run flag to validate prerequisites"
    - "Prerequisite checker validates Step 1.4 output (master_sample_manifest.parquet)"
    - "Prerequisite checker validates input directories (Compustat, IBES, CRSP, SDC)"
    - "Script exits with code 0 on successful dry-run"
    - "Script works on Windows without Unicode encoding errors"
  artifacts:
    - path: "2_Scripts/3_Financial/3.0_BuildFinancialFeatures.py"
      provides: "Step 3 orchestrator with CLI validation"
      contains: "parse_arguments, check_prerequisites"
    - path: "2_Scripts/shared/dependency_checker.py"
      provides: "Prerequisite validation utilities"
      contains: "validate_prerequisites"
  key_links:
    - from: "2_Scripts/3_Financial/3.0_BuildFinancialFeatures.py"
      to: "2_Scripts/shared/dependency_checker.py"
      via: "import statement at line 270"
      pattern: "from shared.dependency_checker import validate_prerequisites"
    - from: "2_Scripts/3_Financial/3.0_BuildFinancialFeatures.py"
      to: "4_Outputs/1.0_BuildSampleManifest/latest/master_sample_manifest.parquet"
      via: "check_prerequisites validates Step 1.4 output"
      pattern: "1.4_AssembleManifest.*master_sample_manifest"
    - from: "2_Scripts/3_Financial/3.0_BuildFinancialFeatures.py"
      to: "1_Inputs/ (Compustat, IBES, CRSP, SDC)"
      via: "check_prerequisites validates input directories"
      pattern: "required_files.*Compustat.*IBES.*CRSP.*SDC"
---

<objective>
Verify 3.0_BuildFinancialFeatures.py CLI flags work correctly (--help, --dry-run)

Purpose: Ensure the Step 3 orchestrator can be run manually with proper CLI validation before full execution
Output: Working --help and --dry-run flags with Windows-compatible output
</objective>

<execution_context>
@C:\Users\sinas\.claude\get-shit-done\workflows\execute-plan.md
@C:\Users\sinas\.claude\get-shit-done\templates\summary.md
</execution_context>

<context>
@.planning/quick/005-verify-step22-dryrun/005-SUMMARY.md
@2_Scripts/3_Financial/3.0_BuildFinancialFeatures.py
@2_Scripts/shared/dependency_checker.py

# Known patterns from quick tasks 001-005:
- Windows cp1252 encoding does NOT support Unicode checkmarks (U+2713)
- Solution: Use [OK] instead of checkmark characters
- dependency_checker.py already uses [OK] pattern (line 77)

# Known issue in 3.0_BuildFinancialFeatures.py:
- Line 307 contains Unicode checkmark: print("All prerequisites validated")
- This needs to be replaced with [OK] for Windows compatibility

# Prerequisites checked by 3.0:
1. Input directories: Compustat, IBES, CRSP, SDC (in 1_Inputs/)
2. Step 1.4 output: master_sample_manifest.parquet (in 4_Outputs/1.0_BuildSampleManifest/latest/)
</context>

<tasks>

<task type="auto">
  <name>Task 1: Verify --help flag displays correctly</name>
  <files>2_Scripts/3_Financial/3.0_BuildFinancialFeatures.py</files>
  <action>
    Run: python 2_Scripts/3_Financial/3.0_BuildFinancialFeatures.py --help

    Verify:
    - Script name and description appear
    - --dry-run flag is documented
    - --test flag is documented
    - No Unicode encoding errors on Windows

    If Unicode errors occur:
    - Find the Unicode character causing the error
    - Replace with [OK] or plain ASCII equivalent
  </action>
  <verify>python 2_Scripts/3_Financial/3.0_BuildFinancialFeatures.py --help exits with code 0 and shows usage</verify>
  <done>--help flag shows script description and available flags without errors</done>
</task>

<task type="auto">
  <name>Task 2: Fix Windows Unicode character and verify --dry-run</name>
  <files>2_Scripts/3_Financial/3.0_BuildFinancialFeatures.py</files>
  <action>
    Step 1: Fix the Unicode checkmark at line 307
    - Change: print("All prerequisites validated")
    - To: print("[OK] All prerequisites validated")

    Step 2: Run: python 2_Scripts/3_Financial/3.0_BuildFinancialFeatures.py --dry-run

    Verify validation checks:
    - Input directories exist (Compustat, IBES, CRSP, SDC in 1_Inputs/)
    - Step 1.4 output exists (master_sample_manifest.parquet in 4_Outputs/1.0_BuildSampleManifest/latest/)
    - Exit code is 0 on success
    - Message shows "[OK] All prerequisites validated" (Windows-compatible)

    Expected prerequisite failures if missing:
    - Error lists missing input directories
    - Error lists missing 1.4_AssembleManifest output
    - Error suggests running 1.4_AssembleManifest first
  </action>
  <verify>python 2_Scripts/3_Financial/3.0_BuildFinancialFeatures.py --dry-run exits 0 and validates prerequisites, no Unicode errors</verify>
  <done>--dry-run flag validates input directories and Step 1.4 output, exit code 0, no Unicode errors</done>
</task>

<task type="auto">
  <name>Task 3: Verify --test flag is documented and functional</name>
  <files>2_Scripts/3_Financial/3.0_BuildFinancialFeatures.py</files>
  <action>
    Verify the --test flag works correctly:
    - Run with --help to confirm --test is documented
    - Note: --test is for full execution (limits to first 3 years), not for dry-run mode
    - The flag should be described as "Run on first 3 years only for testing"

    This task is documentation verification only - do NOT run with --test as it would
    execute the full pipeline.
  </action>
  <verify>--test flag appears in --help output with correct description</verify>
  <done>--test flag is documented for testing purposes (limits processing to first 3 years)</done>
</task>

</tasks>

<verification>
After completion:
1. --help shows usage without Unicode errors
2. --dry-run validates input directories (Compustat, IBES, CRSP, SDC)
3. --dry-run validates Step 1.4 output (master_sample_manifest.parquet)
4. Exit code 0 on successful validation
5. Output is Windows-compatible (no Unicode encoding errors)
6. Unicode checkmark replaced with [OK]
7. --test flag is documented correctly
</verification>

<success_criteria>
- All CLI flags (--help, --dry-run, --test) work correctly
- No Unicode encoding errors on Windows (checkmark replaced with [OK])
- Prerequisite validation correctly identifies input directories and Step 1.4 as required
- Exit code 0 on successful dry-run
</success_criteria>

<output>
After completion, create `.planning/quick/006-verify-step30-dryrun/006-SUMMARY.md`
</output>
