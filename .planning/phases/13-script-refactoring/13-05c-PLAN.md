---
phase: 13-script-refactoring
plan: 05c
type: execute
wave: 3
depends_on: [13-01]
files_modified:
  - 2_Scripts/3_Financial/3.0_BuildFinancialFeatures.py
  - 2_Scripts/3_Financial/3.1_FirmControls.py
  - 2_Scripts/3_Financial/3.2_MarketVariables.py
  - 2_Scripts/3_Financial/3.3_EventFlags.py
autonomous: true
user_setup: []

must_haves:
  truths:
    - "All Step 3 scripts use shared.symlink_utils.update_latest_link() for 'latest' links"
    - "Manual symlink creation code removed from Step 3 scripts"
    - "Windows junctions used when symlinks fail (no admin required)"
    - "Clear warnings logged when fallback methods used"
  artifacts:
    - path: "2_Scripts/3_Financial/*.py"
      provides: "Step 3 scripts with improved symlink/junction handling"
      imports: ["shared.symlink_utils"]
  key_links:
    - from: "Step 3 scripts"
      to: "shared/symlink_utils.py"
      via: "from shared.symlink_utils import update_latest_link"
      pattern: "from shared.symlink_utils import update_latest_link"
---

<objective>
Improve Windows symlink fallback in Step 3 scripts by using shared.symlink_utils module with junction support.

Purpose: Replace manual symlink creation with shared.symlink_utils.update_latest_link() which handles symlinks (Unix), junctions (Windows), and copy fallback with clear warnings.
Output: All Step 3 scripts using shared.symlink_utils for 'latest' link creation.
</objective>

<execution_context>
@~/.config/opencode/get-shit-done/workflows/execute-plan.md
@~/.config/opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/13-script-refactoring/13-RESEARCH.md
@.planning/phases/13-script-refactoring/13-01b-SUMMARY.md

@2_Scripts/shared/symlink_utils.py
@2_Scripts/3_Financial/3.0_BuildFinancialFeatures.py
</context>

<tasks>

<task type="auto">
  <name>Update Step 3 scripts to use shared.symlink_utils</name>
  <files>
    2_Scripts/3_Financial/3.0_BuildFinancialFeatures.py
    2_Scripts/3_Financial/3.1_FirmControls.py
    2_Scripts/3_Financial/3.2_MarketVariables.py
    2_Scripts/3_Financial/3.3_EventFlags.py
  </files>
  <action>
Replace manual symlink creation in Step 3 scripts with shared.symlink_utils.update_latest_link():

**For each script in 3_Financial/:**

1. Add import: from shared.symlink_utils import update_latest_link

2. Find symlink creation code
3. Identify target_dir and link_path
4. Replace entire symlink block with update_latest_link() call
5. Preserve print message after update

**Approach:**
Same as Step 1 task:
1. Read script and find symlink creation
2. Replace with update_latest_link() call
3. Test script to verify 'latest' link works

**Scripts to update:**
- 3.0_BuildFinancialFeatures.py - Check for symlink creation
- 3.1_FirmControls.py - Check for symlink creation
- 3.2_MarketVariables.py - Check for symlink creation
- 3.3_EventFlags.py - Check for symlink creation

For scripts without symlink creation, skip.
  </action>
  <verify>
python 2_Scripts/3_Financial/3.0_BuildFinancialFeatures.py
python 2_Scripts/3_Financial/3.1_FirmControls.py
python 2_Scripts/3_Financial/3.2_MarketVariables.py
python 2_Scripts/3_Financial/3.3_EventFlags.py
  </verify>
  <done>All Step 3 scripts using shared.symlink_utils.update_latest_link()</done>
</task>

</tasks>

<verification>
After completing all tasks, verify:

1. All Step 3 scripts import shared.symlink_utils.update_latest_link
2. Manual symlink creation code removed from Step 3 scripts
3. Scripts still execute and create 'latest' links
4. Warnings appear when fallback methods used

Run verification:
```bash
# Check that scripts import symlink_utils
grep -l "from shared.symlink_utils import update_latest_link" \
  2_Scripts/3_Financial/*.py
```
</verification>

<success_criteria>
1. All Step 3 scripts using shared.symlink_utils.update_latest_link() for 'latest' link creation
2. Manual symlink creation code removed from Step 3 scripts
3. Scripts execute successfully on Unix (symlinks)
4. Scripts execute successfully on Windows (junctions or copy fallback)
5. Clear warnings logged when fallback methods used
</success_criteria>

<output>
After completion, create `.planning/phases/13-script-refactoring/13-05c-SUMMARY.md`
</output>
