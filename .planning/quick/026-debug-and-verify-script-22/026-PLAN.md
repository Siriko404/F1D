---
phase: quick
plan: 026
type: execute
wave: 1
depends_on: []
files_modified:
  - 2_Scripts/2_Text/2.2_ConstructVariables.py
autonomous: true
user_setup: []

must_haves:
  truths:
    - Script correctly reports number of linguistic variables created
    - All linguistic percentage variables are present in output files
    - Variable count matches expected: 5 samples × 3 contexts × 7 categories = 105 (or subset thereof)
  artifacts:
    - path: 2_Scripts/2_Text/2.2_ConstructVariables.py
      provides: Fixed variable counting logic
      min_lines: 1
  key_links:
    - from: process_year function
      to: main function
      via: return dictionary
      pattern: variables_created.*return
---

<objective>
Debug and fix the "0 variables created" reporting issue in script 2.2_ConstructVariables.py

Purpose: The script is successfully creating linguistic variables (84 per year as confirmed by inspecting output files), but the logging incorrectly reports "0 variables created". This is a reporting bug, not a functional bug, but it needs to be fixed for accurate observability.

Root Cause: The `process_year()` function creates a local `variables_created` counter (line 528) and increments it for each sample-context combination (line 536), but this value is NOT returned in the result dictionary (lines 548-557). Therefore, the main() function cannot accumulate the total.

Output: Fixed script that accurately reports variable creation counts in logs and stats.
</objective>

<execution_context>
@C:\Users\sinas\.claude\get-shit-done\workflows\execute-plan.md
@C:\Users\sinas\.claude\get-shit-done\templates\summary.md
</execution_context>

<context>
@.planning/STATE.md
@2_Scripts/2_Text/2.2_ConstructVariables.py

Current Behavior:
- Input files: linguistic_counts_YYYY.parquet with 7 count columns (Negative, Positive, Uncertainty, Litigious, Strong_Modal, Weak_Modal, Constraining)
- Processing: 5 samples × 3 contexts = 15 combinations per year
- Expected variables: 15 × 7 = 105 per year (minus any combinations with no data)
- Actual output: 84 linguistic variables per year confirmed by inspection (89 cols - 5 metadata = 84 vars)
- Bug: Log shows "0 variables created" but files contain correct variables

Fix Required:
Add `variables_created` to the return dictionary in `process_year()` function
</context>

<tasks>

<task type="auto">
  <name>Fix variable count reporting in process_year function</name>
  <files>2_Scripts/2_Text/2.2_ConstructVariables.py</files>
  <action>
  In the `process_year()` function, modify the return statement (lines 548-557) to include the `variables_created` counter:

  Current return:
  ```python
  return {
      "rows": len(meta),
      "cols": len(meta.columns),
      "speaker_flags": {
          "analyst": int(analyst_count),
          "manager": int(manager_count),
          "ceo": int(ceo_count),
          "operator": int(operator_count),
      },
  }
  ```

  Change to:
  ```python
  return {
      "rows": len(meta),
      "cols": len(meta.columns),
      "variables_created": variables_created,
      "speaker_flags": {
          "analyst": int(analyst_count),
          "manager": int(manager_count),
          "ceo": int(ceo_count),
          "operator": int(operator_count),
      },
  }
  ```

  This ensures the variable count is propagated to main() for accumulation.
  </action>
  <verify>
  Run: python 2_Scripts/2_Text/2.2_ConstructVariables.py
  Check log output for "Saved linguistic_variables_YYYY.parquet: X,XXX rows, YYY variables"
  Verify YYY > 0 (should be ~84 per year)
  </verify>
  <done>
  Log accurately reports variables created per year (e.g., "84 variables" instead of "0 variables")
  Total variables created in process stats is correct (should be ~84 × 17 years = 1,428 total)
  </done>
</task>

<task type="auto">
  <name>Verify output files contain all expected linguistic variables</name>
  <files>4_Outputs/2_Textual_Analysis/2.2_Variables</files>
  <action>
  After running the fixed script, verify the output files contain the correct linguistic variables:

  1. Check the latest timestamped directory in 4_Outputs/2_Textual_Analysis/2.2_Variables/
  2. Load linguistic_variables_2002.parquet
  3. Verify:
     - Shape has 89 columns (5 metadata + 84 linguistic variables)
     - Columns follow naming pattern: {Sample}_{Context}_{Category}_pct
     - Sample prefixes include: Manager, Analyst, CEO, NonCEO_Manager, Entire
     - Context suffixes include: QA, Pres, All
     - Category suffixes include: Negative, Positive, Uncertainty, Litigious, Strong_Modal, Weak_Modal, Constraining

  4. Check that values are reasonable percentages (0-100 range)
  5. Verify no all-NaN columns (unless that sample-context combination truly has no data)
  </action>
  <verify>
  Run verification in Python:
  ```python
  import pandas as pd
  df = pd.read_parquet('4_Outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_2002.parquet')
  print(f"Shape: {df.shape}")
  print(f"Linguistic columns: {len([c for c in df.columns if '_pct' in c])}")
  print(f"Sample prefixes: {set(c.split('_')[0] for c in df.columns if '_pct' in c)}")
  print(f"Context suffixes: {set(c.split('_')[1] for c in df.columns if '_pct' in c)}")
  print(f"Category suffixes: {set(c.split('_')[2].replace('_pct', '') for c in df.columns if '_pct' in c)}")
  ```
  </verify>
  <done>
  Output files contain expected linguistic variables with correct naming
  All percentage values are in valid range (0-100)
  Variable count matches log output
  </done>
</task>

<task type="checkpoint:human-verify">
  <what-built>Fixed script 2.2 with accurate variable counting and verified output files</what-built>
  <how-to-verify>
  1. Check the log file in 3_Logs/2.2_ConstructVariables/ for the latest run
  2. Verify each year shows realistic variable counts (e.g., "84 variables" not "0 variables")
  3. Check the report_step_2_2.md in the output directory
  4. Verify "Total variables created" in Variable Creation Breakdown section is correct
  5. Spot-check one year's parquet file to ensure columns are present and values look reasonable
  </how-to-verify>
  <resume-signal>Type "approved" if variables are correctly counted and outputs are valid</resume-signal>
</task>

</tasks>

<verification>
- All years processed successfully without errors
- Variable count in logs matches expected (~84 per year)
- Output parquet files have correct shape and column names
- Percentage values are in valid range (0-100)
- Report accurately reflects total variables created
</verification>

<success_criteria>
Script runs to completion and accurately reports:
- Variables created per year (non-zero)
- Total variables created across all years
- Output files contain correct linguistic variables with proper naming
- All verification checks pass
</success_criteria>

<output>
After completion, create `.planning/quick/026-debug-and-verify-script-22/026-SUMMARY.md`
</output>
