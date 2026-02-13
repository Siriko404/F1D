---
phase: 69-architecture-migration
plan: 02A
type: execute
wave: 2
depends_on: [69-01]
files_modified: [src/f1d/sample/, src/f1d/text/]
autonomous: true
user_setup: []

must_haves:
  truths:
    - "Sample stage modules are accessible via f1d.sample.* imports"
    - "Text stage modules are accessible via f1d.text.* imports"
    - "All migrated modules have documented tier classification (1/2/3) in docstrings"
    - "Migrated modules use new f1d.* import patterns internally"
  artifacts:
    - path: "src/f1d/sample/"
      provides: "Stage 1 - Sample construction modules"
      contains: "Tier 2 classification"
    - path: "src/f1d/text/"
      provides: "Stage 2 - Text processing modules"
      contains: "Tier 2 classification"
    - path: "src/f1d/sample/__init__.py"
      provides: "Sample package entry point"
      min_lines: 10
    - path: "src/f1d/text/__init__.py"
      provides: "Text package entry point"
      min_lines: 10
  key_links:
    - from: "src/f1d/sample/*.py"
      to: "f1d.shared.*"
      via: "import statement"
      pattern: "from f1d\\.shared"
    - from: "src/f1d/text/*.py"
      to: "f1d.shared.*"
      via: "import statement"
      pattern: "from f1d\\.shared"
---

<objective>
Migrate sample (Stage 1) and text (Stage 2) scripts from 2_Scripts/ to src/f1d/ package structure.

Purpose: Complete the package migration for the first two processing stages with proper module tier classifications and updated import patterns.
Output: Sample and text stage modules organized under src/f1d/{stage}/ with Tier 2 classifications and new f1d.* imports.
</objective>

<execution_context>
@C:/Users/sinas/.claude/get-shit-done/workflows/execute-plan.md
@C:/Users/sinas/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@docs/ARCHITECTURE_STANDARD.md

**Module Tier System (from ARCH-02):**
- Tier 1 (Core Shared): src/f1d/shared/ - 100% test coverage, comprehensive docs
- Tier 2 (Stage-Specific): src/f1d/{stage}/ - 80%+ test coverage, standard docs
- Tier 3 (Scripts/One-offs): scripts/ - Optional tests, basic docs

**Current Scripts:**
- 2_Scripts/1_Sample/ - Sample construction scripts
- 2_Scripts/2_Text/ - Text processing scripts

**Import Pattern Updates Required:**
- `from shared.xxx` -> `from f1d.shared.xxx`
- `import shared.xxx` -> `import f1d.shared.xxx`
</context>

<tasks>

<task type="auto">
  <name>Task 1: Migrate sample stage scripts</name>
  <files>
    src/f1d/sample/*.py
    src/f1d/sample/__init__.py
  </files>
  <action>
Copy Stage 1 (Sample) scripts to the new package structure and update imports.

1. List all Python scripts in 2_Scripts/1_Sample/ and copy to src/f1d/sample/:
   - Keep original script names for now (migration to module names happens later)
   - Add Tier 2 classification to each file's docstring: "Tier 2: Stage 1 - Sample construction"

2. Update src/f1d/sample/__init__.py:
   - Add docstring describing Stage 1 purpose
   - Add note about Tier 2 classification for all modules

3. CRITICAL: Update internal imports in all migrated files from old patterns to new:
   - `from shared.xxx import yyy` -> `from f1d.shared.xxx import yyy`
   - `import shared.xxx` -> `import f1d.shared.xxx`
   - Also update any cross-stage imports: `from 2_Scripts.xxx` patterns
   - Use grep to find: `grep -r "from shared\." src/f1d/sample/`
   - Use sed to update: `sed -i 's/from shared\./from f1d.shared./g' src/f1d/sample/*.py`

DO NOT delete original files - they will be removed after full migration verification.
  </action>
  <verify>
ls src/f1d/sample/*.py | wc -l
head -5 src/f1d/sample/*.py | grep -i "tier"
grep -L "from shared\." src/f1d/sample/*.py 2>/dev/null | wc -l
  </verify>
  <done>
- All sample scripts copied to src/f1d/sample/
- Each module has Tier 2 classification in docstring
- __init__.py documents stage purpose
- All internal imports updated from `shared.*` to `f1d.shared.*`
  </done>
</task>

<task type="auto">
  <name>Task 2: Migrate text stage scripts</name>
  <files>
    src/f1d/text/*.py
    src/f1d/text/__init__.py
  </files>
  <action>
Copy Stage 2 (Text) scripts to the new package structure and update imports.

1. List all Python scripts in 2_Scripts/2_Text/ and copy to src/f1d/text/:
   - Keep original script names for now
   - Add Tier 2 classification to each file's docstring: "Tier 2: Stage 2 - Text processing"

2. Update src/f1d/text/__init__.py:
   - Add docstring describing Stage 2 purpose
   - Add note about Tier 2 classification for all modules

3. CRITICAL: Update internal imports in all migrated files from old patterns to new:
   - `from shared.xxx import yyy` -> `from f1d.shared.xxx import yyy`
   - `import shared.xxx` -> `import f1d.shared.xxx`
   - Also update any cross-stage imports
   - Use grep to find: `grep -r "from shared\." src/f1d/text/`
   - Use sed to update: `sed -i 's/from shared\./from f1d.shared./g' src/f1d/text/*.py`

DO NOT delete original files - they will be removed after full migration verification.
  </action>
  <verify>
ls src/f1d/text/*.py | wc -l
head -5 src/f1d/text/*.py | grep -i "tier"
grep -L "from shared\." src/f1d/text/*.py 2>/dev/null | wc -l
  </verify>
  <done>
- All text scripts copied to src/f1d/text/
- Each module has Tier 2 classification in docstring
- __init__.py documents stage purpose
- All internal imports updated from `shared.*` to `f1d.shared.*`
  </done>
</task>

<task type="auto">
  <name>Task 3: Verify sample and text imports work</name>
  <files>
    src/f1d/sample/__init__.py
    src/f1d/text/__init__.py
  </files>
  <action>
Verify that the migrated sample and text modules can be imported successfully.

1. Test sample stage imports:
   ```bash
   python -c "import f1d.sample; print('f1d.sample OK')"
   ```

2. Test text stage imports:
   ```bash
   python -c "import f1d.text; print('f1d.text OK')"
   ```

3. Verify no old import patterns remain:
   ```bash
   grep -r "from shared\." src/f1d/sample/ && echo "ERROR: old imports in sample" || echo "OK"
   grep -r "from shared\." src/f1d/text/ && echo "ERROR: old imports in text" || echo "OK"
   ```

4. Test a representative module import if any exist:
   - Check for actual module files
   - Attempt to import one to verify the import chain

DO NOT execute any processing scripts - just verify import chains.
  </action>
  <verify>
python -c "import f1d.sample" 2>&1 | grep -v "Error\|Traceback"
python -c "import f1d.text" 2>&1 | grep -v "Error\|Traceback"
grep -r "from shared\." src/f1d/sample/ src/f1d/text/ 2>/dev/null | wc -l
  </verify>
  <done>
- f1d.sample package imports successfully
- f1d.text package imports successfully
- No old import patterns (`from shared.`) found in migrated files
- Import chain from f1d.shared.* works correctly
  </done>
</task>

</tasks>

<verification>
After all tasks complete, verify the stage migration:

1. All stages have modules:
   ```bash
   ls src/f1d/sample/*.py
   ls src/f1d/text/*.py
   ```

2. Both stages importable:
   ```bash
   python -c "import f1d.sample; import f1d.text"
   ```

3. No old import patterns:
   ```bash
   grep -r "from shared\." src/f1d/sample/ src/f1d/text/ && echo "ERROR" || echo "OK"
   ```
</verification>

<success_criteria>
- All sample and text modules copied to src/f1d/sample/ and src/f1d/text/
- Each module has documented tier classification
- Both stages accessible via package imports
- All migrated modules use new f1d.* import patterns internally
- No import errors when loading migrated modules
</success_criteria>

<output>
After completion, create `.planning/phases/69-architecture-migration/69-02A-SUMMARY.md`
</output>
