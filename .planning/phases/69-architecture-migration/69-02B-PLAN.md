---
phase: 69-architecture-migration
plan: 02B
type: execute
wave: 2
depends_on: [69-01]
files_modified: [src/f1d/financial/, src/f1d/econometric/, docs/TIER_MANIFEST.md]
autonomous: true
user_setup: []

must_haves:
  truths:
    - "Financial stage modules are accessible via f1d.financial.v1.* and f1d.financial.v2.*"
    - "Econometric stage modules are accessible via f1d.econometric.v1.* and f1d.econometric.v2.*"
    - "Both V1 and V2 variants work as active modules"
    - "All migrated modules use new f1d.* import patterns internally"
    - "Tier manifest documents all module classifications"
  artifacts:
    - path: "src/f1d/financial/v1/"
      provides: "V1 financial methodology modules"
      contains: "Tier 2 classification"
    - path: "src/f1d/financial/v2/"
      provides: "V2 financial methodology modules"
      contains: "Tier 2 classification"
    - path: "src/f1d/econometric/v1/"
      provides: "V1 econometric methodology modules"
    - path: "src/f1d/econometric/v2/"
      provides: "V2 econometric methodology modules"
    - path: "docs/TIER_MANIFEST.md"
      provides: "Module tier classification reference"
      min_lines: 50
  key_links:
    - from: "src/f1d/financial/__init__.py"
      to: "src/f1d/financial/v1/"
      via: "subpackage imports"
    - from: "src/f1d/financial/*.py"
      to: "f1d.shared.*"
      via: "import statement"
      pattern: "from f1d\\.shared"
---

<objective>
Migrate financial (Stage 3) and econometric (Stage 4) scripts from 2_Scripts/ to src/f1d/ package with V1/V2 variants, and create the module tier manifest.

Purpose: Complete the package migration for the final two processing stages with proper V1/V2 variant structure and comprehensive tier documentation.
Output: Financial and econometric stage modules with V1/V2 variants, plus tier manifest documentation.
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
- 2_Scripts/3_Financial/ - V1 financial scripts (active)
- 2_Scripts/3_Financial_V2/ - V2 financial scripts (active)
- 2_Scripts/4_Econometric/ - V1 econometric scripts (active)
- 2_Scripts/4_Econometric_V2/ - V2 econometric scripts (active)

**Both V1 and V2 are ACTIVE variants - neither is deprecated.**

**Import Pattern Updates Required:**
- `from shared.xxx` -> `from f1d.shared.xxx`
- `import shared.xxx` -> `import f1d.shared.xxx`
</context>

<tasks>

<task type="auto">
  <name>Task 1: Migrate financial stage scripts (V1 and V2)</name>
  <files>
    src/f1d/financial/v1/*.py
    src/f1d/financial/v1/__init__.py
    src/f1d/financial/v2/*.py
    src/f1d/financial/v2/__init__.py
    src/f1d/financial/__init__.py
  </files>
  <action>
Copy both V1 and V2 financial stage scripts to the new package structure and update imports.

1. Copy V1 financial scripts from 2_Scripts/3_Financial/ to src/f1d/financial/v1/:
   - Keep original script names for now
   - Add Tier 2 classification: "Tier 2: Stage 3 (V1) - Financial feature construction"

2. Copy V2 financial scripts from 2_Scripts/3_Financial_V2/ to src/f1d/financial/v2/:
   - Keep original script names for now
   - Add Tier 2 classification: "Tier 2: Stage 3 (V2) - Financial feature construction"

3. CRITICAL: Update internal imports in all migrated files:
   - `from shared.xxx import yyy` -> `from f1d.shared.xxx import yyy`
   - `import shared.xxx` -> `import f1d.shared.xxx`
   - Use grep to find: `grep -r "from shared\." src/f1d/financial/`
   - Use sed to update: `sed -i 's/from shared\./from f1d.shared./g' src/f1d/financial/v*/*.py`

4. Update src/f1d/financial/__init__.py:
   - Document both V1 and V2 as ACTIVE variants
   - Provide import guidance

5. Update src/f1d/financial/v1/__init__.py:
   - Docstring: "V1 financial methodology - Active variant"
   - Note that V1 is NOT deprecated

6. Update src/f1d/financial/v2/__init__.py:
   - Docstring: "V2 financial methodology - Active variant"

CRITICAL: Both V1 and V2 are ACTIVE variants per ARCH-04 (Version Management). DO NOT archive or deprecate V1.
  </action>
  <verify>
ls src/f1d/financial/v1/*.py | wc -l
ls src/f1d/financial/v2/*.py | wc -l
python -c "from f1d.financial import v1, v2"
grep -r "Active variant" src/f1d/financial/*/__init__.py
grep -r "from shared\." src/f1d/financial/ | wc -l
  </verify>
  <done>
- All V1 financial scripts copied to src/f1d/financial/v1/
- All V2 financial scripts copied to src/f1d/financial/v2/
- Both variants documented as ACTIVE in __init__.py files
- Each module has Tier 2 classification in docstring
- All internal imports updated from `shared.*` to `f1d.shared.*`
  </done>
</task>

<task type="auto">
  <name>Task 2: Migrate econometric stage scripts (V1 and V2)</name>
  <files>
    src/f1d/econometric/v1/*.py
    src/f1d/econometric/v1/__init__.py
    src/f1d/econometric/v2/*.py
    src/f1d/econometric/v2/__init__.py
    src/f1d/econometric/__init__.py
  </files>
  <action>
Copy both V1 and V2 econometric stage scripts to the new package structure and update imports.

1. Copy V1 econometric scripts from 2_Scripts/4_Econometric/ to src/f1d/econometric/v1/:
   - Keep original script names for now
   - Add Tier 2 classification: "Tier 2: Stage 4 (V1) - Econometric analysis"

2. Copy V2 econometric scripts from 2_Scripts/4_Econometric_V2/ to src/f1d/econometric/v2/:
   - Keep original script names for now
   - Add Tier 2 classification: "Tier 2: Stage 4 (V2) - Econometric analysis"

3. CRITICAL: Update internal imports in all migrated files:
   - `from shared.xxx import yyy` -> `from f1d.shared.xxx import yyy`
   - `import shared.xxx` -> `import f1d.shared.xxx`
   - Use grep to find: `grep -r "from shared\." src/f1d/econometric/`
   - Use sed to update: `sed -i 's/from shared\./from f1d.shared./g' src/f1d/econometric/v*/*.py`

4. Update src/f1d/econometric/__init__.py:
   - Document both V1 and V2 as ACTIVE variants
   - Provide import guidance for both variants

5. Update src/f1d/econometric/v1/__init__.py:
   - Docstring: "V1 econometric methodology - Active variant"

6. Update src/f1d/econometric/v2/__init__.py:
   - Docstring: "V2 econometric methodology - Active variant"

CRITICAL: Both V1 and V2 are ACTIVE variants per ARCH-04.
  </action>
  <verify>
ls src/f1d/econometric/v1/*.py | wc -l
ls src/f1d/econometric/v2/*.py | wc -l
python -c "from f1d.econometric import v1, v2"
grep -r "Active variant" src/f1d/econometric/*/__init__.py
grep -r "from shared\." src/f1d/econometric/ | wc -l
  </verify>
  <done>
- All V1 econometric scripts copied to src/f1d/econometric/v1/
- All V2 econometric scripts copied to src/f1d/econometric/v2/
- Both variants documented as ACTIVE in __init__.py files
- Each module has Tier 2 classification in docstring
- All internal imports updated from `shared.*` to `f1d.shared.*`
  </done>
</task>

<task type="auto">
  <name>Task 3: Create module tier manifest</name>
  <files>
    docs/TIER_MANIFEST.md
  </files>
  <action>
Create a tier manifest document that catalogs all modules and their classifications.

Create docs/TIER_MANIFEST.md with:

1. Header explaining the tier system (from ARCH-02):
   - Tier 1: Core Shared Utilities (100% test coverage, strict quality)
   - Tier 2: Stage-Specific Modules (80%+ test coverage, standard quality)
   - Tier 3: Scripts and One-offs (optional tests, basic quality)

2. Tier 1 modules list (src/f1d/shared/):
   - path_utils.py, panel_ols.py, financial_utils.py, iv_regression.py
   - latex_tables.py, data_validation.py, data_loading.py, chunked_reader.py
   - centering.py, diagnostics.py, regression_helpers.py
   - And all other shared utilities

3. Tier 2 modules list by stage:
   - Stage 1 (Sample): src/f1d/sample/*.py
   - Stage 2 (Text): src/f1d/text/*.py
   - Stage 3 (Financial V1): src/f1d/financial/v1/*.py
   - Stage 3 (Financial V2): src/f1d/financial/v2/*.py
   - Stage 4 (Econometric V1): src/f1d/econometric/v1/*.py
   - Stage 4 (Econometric V2): src/f1d/econometric/v2/*.py

4. Quality requirements per tier (from CODE_QUALITY_STANDARD.md CODE-02):
   - Tier 1: 100% type hints, strict mypy, comprehensive docstrings
   - Tier 2: 80%+ type hints, moderate mypy, standard docstrings
   - Tier 3: Optional type hints, basic documentation
  </action>
  <verify>
ls docs/TIER_MANIFEST.md
grep -c "Tier 1" docs/TIER_MANIFEST.md
grep -c "Tier 2" docs/TIER_MANIFEST.md
  </verify>
  <done>
- docs/TIER_MANIFEST.md exists and documents all modules
- All shared utilities listed as Tier 1
- All stage modules listed as Tier 2
- Quality requirements clearly documented
  </done>
</task>

<task type="auto">
  <name>Task 4: Verify financial and econometric imports work</name>
  <files>
    src/f1d/financial/__init__.py
    src/f1d/econometric/__init__.py
  </files>
  <action>
Verify that the migrated financial and econometric modules can be imported successfully.

1. Test financial stage imports (both variants):
   ```bash
   python -c "from f1d.financial import v1, v2; print('f1d.financial OK')"
   ```

2. Test econometric stage imports (both variants):
   ```bash
   python -c "from f1d.econometric import v1, v2; print('f1d.econometric OK')"
   ```

3. Verify no old import patterns remain:
   ```bash
   grep -r "from shared\." src/f1d/financial/ && echo "ERROR: old imports in financial" || echo "OK"
   grep -r "from shared\." src/f1d/econometric/ && echo "ERROR: old imports in econometric" || echo "OK"
   ```

4. Verify V1 and V2 are both accessible:
   ```bash
   python -c "import f1d.financial.v1; import f1d.financial.v2; print('Both V1 and V2 accessible')"
   ```

DO NOT execute any processing scripts - just verify import chains.
  </action>
  <verify>
python -c "from f1d.financial import v1, v2" 2>&1 | grep -v "Error\|Traceback"
python -c "from f1d.econometric import v1, v2" 2>&1 | grep -v "Error\|Traceback"
grep -r "from shared\." src/f1d/financial/ src/f1d/econometric/ 2>/dev/null | wc -l
  </verify>
  <done>
- f1d.financial.v1 and v2 packages import successfully
- f1d.econometric.v1 and v2 packages import successfully
- No old import patterns (`from shared.`) found in migrated files
- Both V1 and V2 variants are accessible
  </done>
</task>

</tasks>

<verification>
After all tasks complete, verify the stage migration:

1. All stages have modules:
   ```bash
   ls src/f1d/financial/v1/*.py
   ls src/f1d/financial/v2/*.py
   ls src/f1d/econometric/v1/*.py
   ls src/f1d/econometric/v2/*.py
   ```

2. Both variants importable:
   ```bash
   python -c "from f1d.financial import v1, v2"
   python -c "from f1d.econometric import v1, v2"
   ```

3. Tier manifest exists:
   ```bash
   cat docs/TIER_MANIFEST.md | head -50
   ```

4. No old import patterns:
   ```bash
   grep -r "from shared\." src/f1d/financial/ src/f1d/econometric/ && echo "ERROR" || echo "OK"
   ```
</verification>

<success_criteria>
- All 4 stage variant directories populated with Python modules
- Both V1 and V2 variants accessible via package imports
- Each module has documented tier classification
- All migrated modules use new f1d.* import patterns internally
- Tier manifest documents all modules with quality requirements
- No import errors when loading migrated modules
</success_criteria>

<output>
After completion, create `.planning/phases/69-architecture-migration/69-02B-SUMMARY.md`
</output>
