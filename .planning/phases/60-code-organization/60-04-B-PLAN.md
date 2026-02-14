---
phase: 60-code-organization
plan: 04-B
type: execute
wave: 4
depends_on: [60-04-A]
files_modified:
  - pyproject.toml
  - .planning/phases/60-code-organization/60-04-CODE-QUALITY-REPORT.md
autonomous: true

must_haves:
  truths:
    - "Mypy configured for shared utilities"
    - "Dead code identified via vulture (documented, not auto-deleted)"
    - "Code quality report documents all findings"
  artifacts:
    - path: "pyproject.toml"
      provides: "Mypy and vulture configuration"
      contains: "[tool.mypy]"
    - path: ".planning/phases/60-code-organization/60-04-CODE-QUALITY-REPORT.md"
      provides: "Documentation of code quality findings"
      contains: "ruff", "mypy", "vulture", "findings"
  key_links:
    - from: "pyproject.toml"
      to: "2_Scripts/shared/**/*.py"
      via: "Mypy configuration applies to shared utilities"
      pattern: "\\[tool\\.mypy\\]"
---

<objective>
Configure mypy (type checking) and vulture (dead code detection), then create a comprehensive code quality report.

Purpose: Add type checking for shared utilities with mypy and identify unused code with vulture. Document all findings from Ruff (60-04-A), mypy, and vulture in a single report.

Output: Configured pyproject.toml with mypy settings, vulture findings documented, and comprehensive code quality report.
</objective>

<execution_context>
@C:\Users\sinas\.claude\get-shit-done/workflows/execute-plan.md
@C:\Users\sinas\.claude\get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/60-code-organization/60-04-A-SUMMARY.md

# Ruff already configured and run in 60-04-A
# Add [tool.mypy] section and run analysis tools
</context>

<tasks>

<task type="auto">
  <name>Task 1: Configure and run mypy on shared utilities</name>
  <files>
    - pyproject.toml
    - 2_Scripts/shared/**/*.py
  </files>
  <action>
    Add mypy configuration to pyproject.toml:
    ```toml
    [tool.mypy]
    python_version = "3.9"
    warn_return_any = true
    warn_unused_configs = true
    ignore_missing_imports = true

    # Progressive rollout: exclude most scripts initially
    exclude = [
        "2_Scripts/[^s]*",  # Exclude all non-shared scripts
        "tests/",
        ".___archive/",
    ]

    # Follow imports for type checking
    follow_imports = "normal"

    # Enable strict mode for new shared modules only
    [[tool.mypy.overrides]]
    module = "shared.observability.*"
    strict = true
    ```

    Run mypy on shared utilities:
    ```
    mypy 2_Scripts/shared/
    ```

    Document type errors found (if any) - don't fix in this plan, just document
  </action>
  <verify>
    - pyproject.toml contains [tool.mypy] section
    - mypy runs on shared/ directory
    - Type errors documented (if any)
  </verify>
  <done>Mypy configured and run on shared utilities</done>
</task>

<task type="auto">
  <name>Task 2: Run vulture to identify dead code</name>
  <files>
    - 2_Scripts/**/*.py
  </files>
  <action>
    Run vulture to find potentially unused code:
    1. Run: vulture 2_Scripts/shared/ --min-confidence 80
    2. Run: vulture 2_Scripts/ --exclude .___archive/ --min-confidence 80
    3. Document findings for code quality report

    Note: Don't delete any code flagged by vulture - just document. False positives are common (dynamic imports, __all__ exports).

    Commands:
    ```
    vulture 2_Scripts/shared/ --min-confidence 80
    vulture 2_Scripts/ --exclude .___archive/ --min-confidence 80
    ```
  </action>
  <verify>
    - Vulture runs successfully
    - Dead code findings documented
  </verify>
  <done>Dead code identified via vulture</done>
</task>

<task type="auto">
  <name>Task 3: Create code quality report</name>
  <files>.planning/phases/60-code-organization/60-04-CODE-QUALITY-REPORT.md</files>
  <action>
    Create comprehensive code quality report documenting:
    1. **Ruff Results (from 60-04-A):**
       - Issues found: X
       - Auto-fixed: Y
       - Remaining manual fixes: Z (list them)
    2. **Mypy Results:**
       - Type errors in shared/: X
       - Files checked: Y
       - Recommendations for adding type hints
    3. **Vulture Results:**
       - Unused code candidates: X
       - False positives identified: Y
       - Recommended removals: Z (with justification)
    4. **Recommendations:**
       - Priority fixes
       - Future improvements (gradual typing expansion, etc.)
    5. **Summary:** Code quality baseline established

    Report format: Markdown with sections for each tool
  </action>
  <verify>
    - Code quality report exists
    - All tool findings documented
    - Recommendations provided
  </verify>
  <done>Code quality report created with findings</done>
</task>

</tasks>

<verification>
Overall verification steps:
1. pyproject.toml updated with [tool.mypy] section
2. Mypy runs on shared/ directory
3. Vulture identified dead code (documented, not deleted)
4. Code quality report created documenting all findings from 60-04-A, mypy, and vulture
</verification>

<success_criteria>
1. Mypy configured for shared utilities
2. Dead code identified via vulture (documented only)
3. Comprehensive code quality report created
4. Baseline established for future improvements
</success_criteria>

<output>
After completion, create `.planning/phases/60-code-organization/60-04-B-SUMMARY.md`
</output>
