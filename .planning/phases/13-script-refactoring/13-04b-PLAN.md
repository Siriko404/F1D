---
phase: 13-script-refactoring
plan: 04b
type: execute
wave: 3
depends_on: [13-04]
files_modified:
  - 2_Scripts/1_Sample/1.2_LinkEntities.py
  - 2_Scripts/1_Sample/1.4_AssembleManifest.py
autonomous: true
user_setup: []

must_haves:
  truths:
    - "Scripts use config-driven string matching thresholds"
    - "RapidFuzz library used for fuzzy matching operations"
    - "Hardcoded thresholds replaced with config-driven values"
    - "Behavior unchanged (outputs identical to before refactoring)"
  artifacts:
    - path: "2_Scripts/1_Sample/1.2_LinkEntities.py"
      provides: "Refactored LinkEntities with config-driven matching"
      imports: ["shared.string_matching"]
    - path: "2_Scripts/1_Sample/1.4_AssembleManifest.py"
      provides: "Refactored AssembleManifest with config-driven matching (if it uses fuzzy matching)"
      imports: ["shared.string_matching"]
  key_links:
    - from: "1.2_LinkEntities.py"
      to: "shared/string_matching.py"
      via: "from shared.string_matching import"
      pattern: "from shared.string_matching import"
    - from: "1.2_LinkEntities.py"
      to: "config/project.yaml"
      via: "load_matching_config() reads thresholds"
      pattern: "load_matching_config"
---

<objective>
Refactor Step 1 scripts to use config-driven string matching with RapidFuzz.

Purpose: Replace hardcoded string matching thresholds with config-driven values from config/project.yaml and use RapidFuzz library for fuzzy matching.
Output: 1.2 and 1.4 scripts refactored to use shared.string_matching module.
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
@.planning/phases/13-script-refactoring/13-04-SUMMARY.md

@2_Scripts/shared/string_matching.py
@2_Scripts/1_Sample/1.2_LinkEntities.py
@2_Scripts/1_Sample/1.4_AssembleManifest.py
</context>

<tasks>

<task type="auto">
  <name>Refactor 1.2_LinkEntities.py to use config-driven matching</name>
  <files>2_Scripts/1_Sample/1.2_LinkEntities.py</files>
  <action>
Refactor 1.2_LinkEntities.py to use shared.string_matching:

1. Add import:
```python
from shared.string_matching import (
    load_matching_config,
    get_scorer,
    match_company_names,
    match_many_to_many,
    RAPIDFUZZ_AVAILABLE
)
```

2. Remove existing FUZZY_AVAILABLE import (replaced by RAPIDFUZZ_AVAILABLE)

3. Replace hardcoded threshold usage:
   - Find lines with hardcoded similarity scores (e.g., `if score > 85:`)
   - Replace with config-driven thresholds:
     ```python
     config = load_matching_config()
     threshold = config.get("company_name", {}).get("default_threshold", 85.0)
     if score >= threshold:
         # Match logic
     ```

4. Replace manual fuzzy matching with RapidFuzz:
   - Find existing fuzzy matching logic (likely using FuzzyWuzzy or custom implementation)
   - Replace with `match_company_names()` or `match_many_to_many()`
   - Preserve existing matching tiers (Tier 1: PERMNO/CUSIP exact match, Tier 2: name match, Tier 3: fuzzy name match)

5. Update warning message:
   ```python
   if not RAPIDFUZZ_AVAILABLE:
       print("\n" + "=" * 60, file=sys.stderr)
       print("WARNING: Optional dependency 'rapidfuzz' not installed", file=sys.stderr)
       print("=" * 60, file=sys.stderr)
       print("\nImpact on results:", file=sys.stderr)
       print("  - Tier 3 (fuzzy name matching) will be SKIPPED", file=sys.stderr)
       print("\nInstallation:", file=sys.stderr)
       print("  pip install rapidfuzz", file=sys.stderr)
       print("=" * 60 + "\n", file=sys.stderr)
   ```

**Approach:**
1. Read script and identify fuzzy matching sections
2. Identify hardcoded thresholds (search for numbers like 85, 90, 95)
3. Replace with config-driven thresholds
4. Replace manual fuzzy matching with RapidFuzz functions
5. Preserve all existing logic (exact matches, tiered matching)
6. Test script to ensure behavior unchanged

**Important:**
- Preserve exact match logic (Tier 1)
- Preserve name matching logic (Tier 2)
- Only replace fuzzy matching (Tier 3) with RapidFuzz
- Maintain backward compatibility with existing outputs
- Use config defaults if config section missing
  </action>
  <verify>python 2_Scripts/1_Sample/1.2_LinkEntities.py</verify>
  <done>1.2_LinkEntities.py refactored to use config-driven RapidFuzz matching</done>
</task>

<task type="auto">
  <name>Refactor 1.4_AssembleManifest.py to use config-driven matching</name>
  <files>2_Scripts/1_Sample/1.4_AssembleManifest.py</files>
  <action>
Refactor 1.4_AssembleManifest.py to use shared.string_matching:

1. Check if script uses fuzzy matching (grep for "fuzz", "match", "similarity")
2. If fuzzy matching exists:
   a. Add import from shared.string_matching
   b. Replace hardcoded thresholds with config-driven values
   c. Replace manual fuzzy matching with RapidFuzz functions
   d. Update warning messages if needed

3. If no fuzzy matching in this script:
   - Skip this task (task complete with no changes)

**Approach:**
1. Search for fuzzy matching patterns in script
2. If found, apply same refactoring as 1.2_LinkEntities.py
3. If not found, mark task as complete (no changes needed)

**Important:**
- Preserve all existing logic
- Only replace fuzzy matching with RapidFuzz
- Use config defaults if config section missing
  </action>
  <verify>python 2_Scripts/1_Sample/1.4_AssembleManifest.py</verify>
  <done>1.4_AssembleManifest.py refactored to use config-driven matching (or skipped if no fuzzy matching)</done>
</task>

</tasks>

<verification>
After completing all tasks, verify:

1. Scripts import from shared.string_matching
2. Scripts use config-driven thresholds
3. Scripts still execute successfully

Run verification:
```bash
grep -q "from shared.string_matching import" 2_Scripts/1_Sample/1.2_LinkEntities.py && echo "1.2 updated"
```
</verification>

<success_criteria>
1. 1.2_LinkEntities.py refactored to use config-driven matching
2. 1.4_AssembleManifest.py refactored (if it uses fuzzy matching)
3. All fuzzy matching thresholds now configurable
4. Scripts execute successfully with identical outputs
</success_criteria>

<output>
After completion, create `.planning/phases/13-script-refactoring/13-04b-SUMMARY.md`
</output>
