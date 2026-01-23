---
phase: 13-script-refactoring
plan: 05a
type: execute
wave: 3
depends_on: [13-01]
files_modified:
  - 2_Scripts/1_Sample/1.0_BuildSampleManifest.py
  - 2_Scripts/1_Sample/1.1_CleanMetadata.py
  - 2_Scripts/1_Sample/1.2_LinkEntities.py
  - 2_Scripts/1_Sample/1.3_BuildTenureMap.py
  - 2_Scripts/1_Sample/1.4_AssembleManifest.py
autonomous: true
user_setup: []

must_haves:
  truths:
    - "All Step 1 scripts use shared.symlink_utils.update_latest_link() for 'latest' links"
    - "Manual symlink creation code removed from Step 1 scripts"
    - "Windows junctions used when symlinks fail (no admin required)"
    - "Clear warnings logged when fallback methods used"
  artifacts:
    - path: "2_Scripts/1_Sample/*.py"
      provides: "Step 1 scripts with improved symlink/junction handling"
      imports: ["shared.symlink_utils"]
  key_links:
    - from: "Step 1 scripts"
      to: "shared/symlink_utils.py"
      via: "from shared.symlink_utils import update_latest_link"
      pattern: "from shared.symlink_utils import update_latest_link"
---

<objective>
Improve Windows symlink fallback in Step 1 scripts by using shared.symlink_utils module with junction support.

Purpose: Replace manual symlink creation with shared.symlink_utils.update_latest_link() which handles symlinks (Unix), junctions (Windows), and copy fallback with clear warnings.
Output: All Step 1 scripts using shared.symlink_utils for 'latest' link creation.
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
@2_Scripts/1_Sample/1.0_BuildSampleManifest.py
</context>

<tasks>

<task type="auto">
  <name>Update Step 1 scripts to use shared.symlink_utils</name>
  <files>
    2_Scripts/1_Sample/1.0_BuildSampleManifest.py
    2_Scripts/1_Sample/1.1_CleanMetadata.py
    2_Scripts/1_Sample/1.2_LinkEntities.py
    2_Scripts/1_Sample/1.3_BuildTenureMap.py
    2_Scripts/1_Sample/1.4_AssembleManifest.py
  </files>
  <action>
Replace manual symlink creation in Step 1 scripts with shared.symlink_utils.update_latest_link():

**For each script in 1_Sample/:**

1. Add import:
```python
from shared.symlink_utils import update_latest_link
```

2. Find symlink creation code (search for "symlink_to", "latest_dir", etc.)
   Pattern example from 1.0_BuildSampleManifest.py:
   ```python
   # Update latest symlink (directory junction on Windows)
   if paths["latest_dir"].exists():
       if paths["latest_dir"].is_symlink() or paths["latest_dir"].is_junction():
           paths["latest_dir"].unlink()
       else:
           shutil.rmtree(paths["latest_dir"])

   try:
       paths["latest_dir"].symlink_to(
           paths["output_dir"], target_is_directory=True
       )
       print_dual(f"Updated 'latest' -> {paths['output_dir'].name}")
   except OSError:
       shutil.copytree(paths["output_dir"], paths["latest_dir"])
       print_dual(f"Copied outputs to 'latest' (symlink not available)")
   ```

3. Replace with single call to update_latest_link():
   ```python
   update_latest_link(
       target_dir=paths["output_dir"],
       link_path=paths["latest_dir"],
       verbose=True
   )
   print_dual(f"Updated 'latest' -> {paths['output_dir'].name}")
   ```

**Approach:**
1. Read each script and find symlink creation code
2. Identify target_dir (usually paths["output_dir"])
3. Identify link_path (usually paths["latest_dir"])
4. Replace entire symlink block with update_latest_link() call
5. Preserve print_dual message after update
6. Test each script to verify 'latest' link created correctly

**Important:**
- Replace entire symlink creation block (not just symlink_to call)
- Remove manual cleanup code (update_latest_link handles this)
- Remove try-except blocks for symlink failures
- Keep print_dual message for user feedback
- Ensure paths are Path objects (not strings)

**Scripts to update:**
- 1.0_BuildSampleManifest.py - Has symlink creation
- 1.1_CleanMetadata.py - Check if it creates 'latest' link
- 1.2_LinkEntities.py - Check if it creates 'latest' link
- 1.3_BuildTenureMap.py - Check if it creates 'latest' link
- 1.4_AssembleManifest.py - Check if it creates 'latest' link

For scripts without symlink creation, skip (no changes needed).
  </action>
  <verify>
python 2_Scripts/1_Sample/1.0_BuildSampleManifest.py
python 2_Scripts/1_Sample/1.1_CleanMetadata.py
python 2_Scripts/1_Sample/1.2_LinkEntities.py
python 2_Scripts/1_Sample/1.3_BuildTenureMap.py
python 2_Scripts/1_Sample/1.4_AssembleManifest.py
  </verify>
  <done>All Step 1 scripts using shared.symlink_utils.update_latest_link()</done>
</task>

</tasks>

<verification>
After completing all tasks, verify:

1. All Step 1 scripts import shared.symlink_utils.update_latest_link
2. Manual symlink creation code removed from Step 1 scripts
3. Scripts still execute and create 'latest' links
4. Warnings appear when fallback methods used

Run verification:
```bash
# Check that scripts import symlink_utils
grep -l "from shared.symlink_utils import update_latest_link" \
  2_Scripts/1_Sample/*.py
```
</verification>

<success_criteria>
1. All Step 1 scripts using shared.symlink_utils.update_latest_link() for 'latest' link creation
2. Manual symlink creation code removed from Step 1 scripts
3. Scripts execute successfully on Unix (symlinks)
4. Scripts execute successfully on Windows (junctions or copy fallback)
5. Clear warnings logged when fallback methods used
</success_criteria>

<output>
After completion, create `.planning/phases/13-script-refactoring/13-05a-SUMMARY.md`
</output>
