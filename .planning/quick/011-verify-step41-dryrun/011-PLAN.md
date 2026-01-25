---
phase: quick
plan: 011
type: execute
wave: 1
depends_on: []
files_modified: []
autonomous: true
user_setup: []

must_haves:
  truths:
    - "--help flag displays usage information correctly"
    - "--dry-run flag validates prerequisites without executing"
    - "Required imports (CONFIG, update_latest_link, etc.) are present"
    - "Script has no syntax errors that prevent basic CLI validation"
  artifacts:
    - path: "2_Scripts/4_Econometric/4.1_EstimateCeoClarity.py"
      provides: "CEO Clarity estimation pipeline script"
      min_lines: 873
  key_links:
    - from: "4.1_EstimateCeoClarity.py"
      to: "shared/dependency_checker.py"
      via: "import"
      pattern: "from shared.dependency_checker import"
    - from: "4.1_EstimateCeoClarity.py"
      to: "shared/dual_writer.py"
      via: "import"
      pattern: "from shared.dual_writer import"
    - from: "4.1_EstimateCeoClarity.py"
      to: "shared/observability_utils.py"
      via: "import"
      pattern: "from shared.observability_utils import"
    - from: "4.1_EstimateCeoClarity.py"
      to: "shared/symlink_utils.py"
      via: "import"
      pattern: "from shared.symlink_utils import"
---

<objective>
Verify functionality of script 4.1_EstimateCeoClarity.py with --help and --dry-run flags.

Purpose: Validate the Step 4.1 CEO Clarity estimation script has correct CLI interface, all required imports are present, and prerequisite checking works correctly.
Output: Confirmation of CLI functionality and documentation of any issues found.
</objective>

<execution_context>
@C:\Users\sinas\.claude\get-shit-done\workflows\execute-plan.md
@C:\Users\sinas\.claude\get-shit-done\templates\summary.md
</execution_context>

<context>
@2_Scripts/4_Econometric/4.1_EstimateCeoClarity.py
@.planning/quick/010-verify-step34-dryrun/010-SUMMARY.md

# Pattern from previous quick tasks (001-009):
All previous scripts (1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 3.0, 3.1, 3.2, 3.3) were verified and fixed for Windows Unicode character bugs (UnicodeEncodeError, UnicodeDecodeError).

# Step 4.1 specific context:
This script:
- Requires statsmodels library (imports with try/except warning)
- Uses shared modules: dependency_checker, dual_writer, observability_utils, symlink_utils
- Requires CONFIG dictionary for year ranges, firm controls, linguistic controls
- Requires outputs from Steps 2.2, 3.1, 3.2 as prerequisites
- Has --model flag (baseline/extended/regime) but doesn't seem to use it

# Potential issues to check:
1. Missing CONFIG dictionary definition
2. Missing import statements for shared modules
3. Missing path_utils import needed by dependency_checker
</context>

<tasks>

<task type="auto">
  <name>Test --help flag</name>
  <files>2_Scripts/4_Econometric/4.1_EstimateCeoClarity.py</files>
  <action>
    Run the script with --help flag to verify CLI works:
    ```bash
    cd "C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D" && python 2_Scripts/4_Econometric/4.1_EstimateCeoClarity.py --help
    ```

    Expected: Help message displays showing:
    - Description: "STEP 4.1: Estimate CEO Clarity"
    - --dry-run flag
    - --model flag with choices (baseline, extended, regime)

    If error occurs, note the exact error message for diagnosis.
  </action>
  <verify>
    --help runs without syntax errors and displays usage information.
  </verify>
  <done>
    --help flag produces expected output or specific error is documented.
  </done>
</task>

<task type="auto">
  <name>Test --dry-run flag</name>
  <files>2_Scripts/4_Econometric/4.1_EstimateCeoClarity.py</files>
  <action>
    Run the script with --dry-run flag to verify prerequisite checking:
    ```bash
    cd "C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D" && python 2_Scripts/4_Econometric/4.1_EstimateCeoClarity.py --dry-run
    ```

    Expected:
    - "Dry-run mode: validating inputs..."
    - Check for prerequisites from Steps 2.2, 3.1, 3.2
    - Either "[OK] All prerequisites validated" or specific missing files

    If error occurs, note whether it's:
    - Import error (missing shared modules)
    - NameError (CONFIG undefined)
    - File path error (wrong prerequisite paths)
  </action>
  <verify>
    --dry-run completes or provides clear error about missing prerequisites.
  </verify>
  <done>
    --dry-run validation results documented (success or specific failure).
  </done>
</task>

<task type="auto">
  <name>Verify required imports and CONFIG</name>
  <files>2_Scripts/4_Econometric/4.1_EstimateCeoClarity.py</files>
  <action>
    Check the script has all required imports and definitions:

    1. Check for shared module imports:
       ```bash
       grep -n "from shared\." "C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\2_Scripts\4_Econometric\4.1_EstimateCeoClarity.py"
       ```
       Should include:
       - from shared.dependency_checker import validate_prerequisites
       - from shared.dual_writer import DualWriter
       - from shared.observability_utils import (compute_file_checksum, print_stats_summary, save_stats, analyze_missing_values)
       - from shared.symlink_utils import update_latest_link

    2. Check for CONFIG dictionary:
       ```bash
       grep -n "^CONFIG\s*=" "C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\2_Scripts\4_Econometric\4.1_EstimateCeoClarity.py"
       ```

    3. Check path to sys.path modification for shared module imports
  </action>
  <verify>
    All required imports are present or missing imports are documented.
  </verify>
  <done>
    Import status documented - list what's present and what's missing.
  </done>
</task>

</tasks>

<verification>
After completion, verify:
1. --help flag works correctly
2. --dry-run flag validates prerequisites
3. Missing imports or CONFIG are documented if found
4. Any Unicode character bugs are noted (Windows-specific)
</verification>

<success_criteria>
- CLI interface (--help, --dry-run) verified working or issues documented
- Required imports and CONFIG status documented
- Prerequisite validation tested
- SUMMARY.md created with findings
</success_criteria>

<output>
After completion, create `.planning/quick/011-verify-step41-dryrun/011-SUMMARY.md`
</output>
