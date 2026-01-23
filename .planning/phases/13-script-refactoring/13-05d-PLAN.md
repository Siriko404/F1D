---
phase: 13-script-refactoring
plan: 05d
type: execute
wave: 3
depends_on: [13-01]
files_modified:
  - 2_Scripts/4_Econometric/4.1.1_EstimateCeoClarity_CeoSpecific.py
  - 2_Scripts/4_Econometric/4.1.2_EstimateCeoClarity_Extended.py
  - 2_Scripts/4_Econometric/4.1.3_EstimateCeoClarity_Regime.py
  - 2_Scripts/4_Econometric/4.1.4_EstimateCeoTone.py
  - 2_Scripts/4_Econometric/4.2_LiquidityRegressions.py
  - 2_Scripts/4_Econometric/4.3_TakeoverHazards.py
  - 2_Scripts/4_Econometric/4.4_GenerateSummaryStats.py
autonomous: true
user_setup: []

must_haves:
  truths:
    - "All Step 4 scripts use shared.symlink_utils.update_latest_link() for 'latest' links"
    - "Manual symlink creation code removed from Step 4 scripts"
    - "Windows junctions used when symlinks fail (no admin required)"
    - "Clear warnings logged when fallback methods used"
  artifacts:
    - path: "2_Scripts/4_Econometric/*.py"
      provides: "Step 4 scripts with improved symlink/junction handling"
      imports: ["shared.symlink_utils"]
  key_links:
    - from: "Step 4 scripts"
      to: "shared/symlink_utils.py"
      via: "from shared.symlink_utils import update_latest_link"
      pattern: "from shared.symlink_utils import update_latest_link"
---

<objective>
Improve Windows symlink fallback in Step 4 scripts by using shared.symlink_utils module with junction support.

Purpose: Replace manual symlink creation with shared.symlink_utils.update_latest_link() which handles symlinks (Unix), junctions (Windows), and copy fallback with clear warnings.
Output: All Step 4 scripts using shared.symlink_utils for 'latest' link creation.
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
@2_Scripts/4_Econometric/4.1.1_EstimateCeoClarity_CeoSpecific.py
</context>

<tasks>

<task type="auto">
  <name>Update Step 4 scripts to use shared.symlink_utils</name>
  <files>
    2_Scripts/4_Econometric/4.1.1_EstimateCeoClarity_CeoSpecific.py
    2_Scripts/4_Econometric/4.1.2_EstimateCeoClarity_Extended.py
    2_Scripts/4_Econometric/4.1.3_EstimateCeoClarity_Regime.py
    2_Scripts/4_Econometric/4.1.4_EstimateCeoTone.py
    2_Scripts/4_Econometric/4.2_LiquidityRegressions.py
    2_Scripts/4_Econometric/4.3_TakeoverHazards.py
    2_Scripts/4_Econometric/4.4_GenerateSummaryStats.py
  </files>
  <action>
Replace manual symlink creation in Step 4 scripts with shared.symlink_utils.update_latest_link():

**For each script in 4_Econometric/:**

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
- 4.1.1_EstimateCeoClarity_CeoSpecific.py - Check for symlink creation
- 4.1.2_EstimateCeoClarity_Extended.py - Check for symlink creation
- 4.1.3_EstimateCeoClarity_Regime.py - Check for symlink creation
- 4.1.4_EstimateCeoTone.py - Check for symlink creation
- 4.2_LiquidityRegressions.py - Check for symlink creation
- 4.3_TakeoverHazards.py - Check for symlink creation
- 4.4_GenerateSummaryStats.py - Check for symlink creation

For scripts without symlink creation, skip.
  </action>
  <verify>
python 2_Scripts/4_Econometric/4.1.1_EstimateCeoClarity_CeoSpecific.py
python 2_Scripts/4_Econometric/4.1.2_EstimateCeoClarity_Extended.py
python 2_Scripts/4_Econometric/4.1.3_EstimateCeoClarity_Regime.py
python 2_Scripts/4_Econometric/4.1.4_EstimateCeoTone.py
python 2_Scripts/4_Econometric/4.2_LiquidityRegressions.py
python 2_Scripts/4_Econometric/4.3_TakeoverHazards.py
python 2_Scripts/4_Econometric/4.4_GenerateSummaryStats.py
  </verify>
  <done>All Step 4 scripts using shared.symlink_utils.update_latest_link()</done>
</task>

</tasks>

<verification>
After completing all tasks, verify:

1. All Step 4 scripts import shared.symlink_utils.update_latest_link
2. Manual symlink creation code removed from Step 4 scripts
3. Scripts still execute and create 'latest' links
4. Warnings appear when fallback methods used

Run verification:
```bash
# Check that scripts import symlink_utils
grep -l "from shared.symlink_utils import update_latest_link" \
  2_Scripts/4_Econometric/*.py
```
</verification>

<success_criteria>
1. All Step 4 scripts using shared.symlink_utils.update_latest_link() for 'latest' link creation
2. Manual symlink creation code removed from Step 4 scripts
3. Scripts execute successfully on Unix (symlinks)
4. Scripts execute successfully on Windows (junctions or copy fallback)
5. Clear warnings logged when fallback methods used
</success_criteria>

<output>
After completion, create `.planning/phases/13-script-refactoring/13-05d-SUMMARY.md`
</output>
