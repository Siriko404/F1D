---
phase: quick-033
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - 4_Outputs/4_Econometric_V2/H1_Hypothesis_Documentation.md
  - 4_Outputs/4_Econometric_V2/H2_Hypothesis_Documentation.md
  - 4_Outputs/4_Econometric_V2/H3_Hypothesis_Documentation.md
  - 4_Outputs/4_Econometric_V2/H4_Hypothesis_Documentation.md
  - 4_Outputs/4_Econometric_V2/H5_Hypothesis_Documentation.md
  - 4_Outputs/4_Econometric_V2/H6_Hypothesis_Documentation.md
  - 4_Outputs/4_Econometric_V2/H7_Hypothesis_Documentation.md
  - 4_Outputs/4_Econometric_V2/H8_Hypothesis_Documentation.md
autonomous: true

must_haves:
  truths:
    - "All table column headers use full variable names (e.g., Manager_QA_Uncertainty_pct not QA Unc.)"
    - "Variable names match the {Speaker}_{Context}_{Category}_pct pattern from the pipeline"
    - "All numeric results preserved exactly (coefficients, SEs, p-values, N, R²)"
  artifacts:
    - path: "4_Outputs/4_Econometric_V2/H1_Hypothesis_Documentation.md"
      provides: "Full variable names in H1 results tables"
      min_lines: 80
    - path: "4_Outputs/4_Econometric_V2/H2_Hypothesis_Documentation.md"
      provides: "Full variable names in H2 results tables"
      min_lines: 80
    - path: "4_Outputs/4_Econometric_V2/H3_Hypothesis_Documentation.md"
      provides: "Full variable names in H3 results tables"
      min_lines: 80
    - path: "4_Outputs/4_Econometric_V2/H4_Hypothesis_Documentation.md"
      provides: "Full variable names in H4 results tables"
      min_lines: 80
    - path: "4_Outputs/4_Econometric_V2/H5_Hypothesis_Documentation.md"
      provides: "Full variable names in H5 results tables"
      min_lines: 60
    - path: "4_Outputs/4_Econometric_V2/H6_Hypothesis_Documentation.md"
      provides: "Full variable names in H6 results tables"
      min_lines: 80
    - path: "4_Outputs/4_Econometric_V2/H7_Hypothesis_Documentation.md"
      provides: "Full variable names in H7 results tables"
      min_lines: 80
    - path: "4_Outputs/4_Econometric_V2/H8_Hypothesis_Documentation.md"
      provides: "Full variable names in H8 results tables"
      min_lines: 80
  key_links:
    - from: "4_Outputs/4_Econometric_V2/H*_Hypothesis_Documentation.md"
      to: "Pipeline variable naming convention"
      via: "Full variable name matching"
      pattern: "(Manager|CEO|NonCEO_Manager|Analyst|Entire)_(QA|Pres|All)_(Uncertainty|Weak_Modal|Strong_Modal|Negative|Positive|Litigious|Constraining)_pct"
---

<objective>
Replace abbreviated variable names in hypothesis documentation files (H1-H8) with full variable names from the pipeline.

Purpose: Eliminate ambiguity in results tables where abbreviated names like "QA Unc." could refer to multiple distinct measures (Manager_QA_Uncertainty_pct, CEO_QA_Uncertainty_pct, NonCEO_Manager_QA_Uncertainty_pct, etc.). Documentation should match the actual variable names used in the pipeline code.

Output: Eight updated hypothesis documentation files with unambiguous full variable names in all tables.
</objective>

<execution_context>
@C:\Users\sinas\.claude/get-shit-done/workflows/execute-plan.md
@C:\Users\sinas\.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md

# Variable Naming Convention
From STATE.md: {Speaker}_{Context}_{Category}_pct pattern
- Speakers: Manager, CEO, NonCEO_Manager, Analyst, Entire
- Contexts: QA, Pres, All
- Categories: Uncertainty, Weak_Modal, Strong_Modal, Negative, Positive, Litigious, Constraining

# Files to Update
All hypothesis documentation files in 4_Outputs/4_Econometric_V2/:
- H1_Hypothesis_Documentation.md (Cash Holdings)
- H2_Hypothesis_Documentation.md (Investment Efficiency)
- H3_Hypothesis_Documentation.md (Payout Policy)
- H4_Hypothesis_Documentation.md (Leverage Discipline)
- H5_Hypothesis_Documentation.md (Analyst Dispersion)
- H6_Hypothesis_Documentation.md (SEC Scrutiny/CCCL)
- H7_Hypothesis_Documentation.md (Stock Illiquidity)
- H8_Hypothesis_Documentation.md (Takeover Probability)
</context>

<tasks>

<task type="auto">
  <name>Replace abbreviated variable names with full pipeline names</name>
  <files>
    4_Outputs/4_Econometric_V2/H1_Hypothesis_Documentation.md
    4_Outputs/4_Econometric_V2/H2_Hypothesis_Documentation.md
    4_Outputs/4_Econometric_V2/H3_Hypothesis_Documentation.md
    4_Outputs/4_Econometric_V2/H4_Hypothesis_Documentation.md
    4_Outputs/4_Econometric_V2/H5_Hypothesis_Documentation.md
    4_Outputs/4_Econometric_V2/H6_Hypothesis_Documentation.md
    4_Outputs/4_Econometric_V2/H7_Hypothesis_Documentation.md
    4_Outputs/4_Econometric_V2/H8_Hypothesis_Documentation.md
  </files>
  <action>
    For each hypothesis documentation file:

    1. Read the file and identify all abbreviated variable names in table headers and cell contents

    2. Replace abbreviated names with full pipeline variable names following the {Speaker}_{Context}_{Category}_pct pattern:
       - "QA Unc." -> "Manager_QA_Uncertainty_pct" (or specify speaker: CEO, NonCEO_Manager, Entire)
       - "CEO QA" -> "CEO_QA_Uncertainty_pct"
       - "Weak Mod." -> "Manager_QA_Weak_Modal_pct" (or specify speaker and context)
       - "CEO Weak" -> "CEO_QA_Weak_Modal_pct"
       - "Pres Unc." -> "Manager_Pres_Uncertainty_pct" (or specify speaker)
       - "CEO Pres" -> "CEO_Pres_Uncertainty_pct"
       - "Manager Weak" -> "Manager_QA_Weak_Modal_pct" (or specify context if ambiguous)
       - "Pres Weak" -> "Manager_Pres_Weak_Modal_pct"
       - Similar patterns for other categories (Negative, Positive, Strong_Modal, Litigious, Constraining)

    3. Update table column headers in regression results tables:
       - Change abbreviated headers to full variable names
       - Maintain table alignment and Markdown formatting
       - Preserve all numeric values exactly (coefficients, SEs, p-values, t-stats, N, R²)

    4. Update text descriptions and notes sections:
       - Replace abbreviated references with full names
       - Ensure consistency throughout the document
       - Keep all interpretations and conclusions unchanged

    5. Preserve document structure:
       - Keep all LaTeX equations unchanged
       - Keep all section headings unchanged
       - Keep all control variable descriptions unchanged
       - Keep all hypothesis test outcome statements unchanged

    CRITICAL: Only change variable names - do NOT modify any numeric results, interpretations, or conclusions. The goal is clarity, not substantive revision.
  </action>
  <verify>
    For each file:
    1. grep -E "(QA Unc\.|CEO QA|Weak Mod\.|CEO Weak|Pres Unc\.|CEO Pres|Manager Weak|Pres Weak)" to confirm no abbreviated names remain
    2. grep -E "(Manager|CEO|NonCEO_Manager|Analyst|Entire)_(QA|Pres|All)_(Uncertainty|Weak_Modal)" to verify full names present
    3. Spot-check that numeric values are preserved by comparing coefficient values before/after
  </verify>
  <done>
    - All 8 hypothesis documentation files updated with full variable names
    - No abbreviated variable names remain in table headers or cells
    - All full names follow {Speaker}_{Context}_{Category}_pct pattern
    - All numeric results (coefficients, SEs, p-values, N, R²) preserved exactly
    - Table formatting and alignment maintained
    - Document structure and interpretations unchanged
  </done>
</task>

</tasks>

<verification>
Run verification across all 8 files:
```bash
# Check no abbreviated names remain
grep -E "(QA Unc\.|CEO QA|Weak Mod\.|CEO Weak|Pres Unc\.|CEO Pres)" 4_Outputs/4_Econometric_V2/H*_Hypothesis_Documentation.md

# Verify full names present
grep -E "(Manager|CEO)_(QA|Pres)_(Uncertainty|Weak_Modal)_pct" 4_Outputs/4_Econometric_V2/H*_Hypothesis_Documentation.md | wc -l

# Spot-check H1 coefficient preservation
grep "0.0036" 4_Outputs/4_Econometric_V2/H1_Hypothesis_Documentation.md
grep "0.0008" 4_Outputs/4_Econometric_V2/H1_Hypothesis_Documentation.md
```

Expected results:
- Zero matches for abbreviated names
- Multiple matches for full variable names (at least 40+ occurrences across 8 files)
- Numeric values preserved in updated files
</verification>

<success_criteria>
- [ ] All 8 hypothesis documentation files read and updated
- [ ] All abbreviated variable names replaced with full pipeline names
- [ ] Full names follow {Speaker}_{Context}_{Category}_pct convention
- [ ] No abbreviated names remain in any file (grep verification passes)
- [ ] All numeric results preserved exactly (spot-check confirms)
- [ ] Table formatting maintained (Markdown tables render correctly)
- [ ] Document structure unchanged (sections, headings, LaTeX equations intact)
- [ ] Files committed to git with descriptive message
</success_criteria>

<output>
After completion, create `.planning/quick/033-clarify-variable-names-in-hypothesis-doc/033-SUMMARY.md` with:
- List of all variable name replacements made
- Verification results (grep checks)
- File paths updated
- Commit hash
</output>
