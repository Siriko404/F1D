# Systematic Fix Plan Prompt: Suite H7 (Stock Illiquidity)

**Purpose:** This prompt instructs an AI fix agent to systematically plan and execute fixes for all remaining issues identified in the re-verification audit.

**Target Suite:** H7 — Speech Vagueness and Stock Illiquidity (Amihud 2002)
**Input Documents:**
- `docs/provenance/AUDIT_REVERIFICATION_H7.md` (Re-verification audit results)
- `docs/provenance/H7.md` (Provenance documentation)

**Output Deliverable:** `docs/provenance/FIX_EXECUTION_REPORT_H7.md`

---

## PART 1: FIX AGENT INSTRUCTIONS

### 1.0 Meta-Instructions (READ CAREFULLY)

You are a **systematic fix execution agent**. Your job is to:
1. **Plan before acting** — document exact changes before making them
2. **Fix precisely** — modify only what needs to be modified, nothing more
3. **Verify immediately** — confirm each fix is correctly applied
4. **Document thoroughly** — record before/after state for every change
5. **Preserve integrity** — never break existing correct functionality

### 1.1 Fix Execution Protocol

For EACH issue, you MUST follow this exact sequence:

```
1. READ the target file in its current state
2. PLAN the exact change (line numbers, old text, new text)
3. PRESENT the plan for confirmation (to your own reasoning)
4. EXECUTE the change using Edit tool (NOT Write)
5. VERIFY by re-reading the modified file
6. DOCUMENT the before/after in the execution report
```

### 1.2 Anti-Regression Safeguards

You are **FORBIDDEN** from:
- Using `Write` to overwrite entire files (use `Edit` for surgical changes)
- Making changes to files not explicitly listed in the fix plan
- Adding new features or refactoring beyond what's required
- Modifying test files or unrelated code
- Running the full pipeline without explicit instruction

You **MUST**:
- Read the full file before editing
- Preserve all existing formatting and structure
- Keep changes minimal and targeted
- Verify the code still has correct syntax after edits
- Test that the modified code can at least be imported without errors

### 1.3 Evidence Standards

For each fix, your execution report MUST include:

| Evidence Type | Required |
|--------------|----------|
| **Issue ID** | From AUDIT_REVERIFICATION_H7.md |
| **Target file** | Exact path to file being modified |
| **Before state** | Exact lines before modification (with line numbers) |
| **Planned change** | Exact old_string and new_string for Edit tool |
| **After state** | Exact lines after modification (with line numbers) |
| **Verification** | Confirmation that fix addresses the issue |

---

## PART 2: ISSUE LEDGER FROM AUDIT

### 2.1 Issues Requiring Fixes

Based on `AUDIT_REVERIFICATION_H7.md`, the following issues require fixes:

| ID | Severity | Description | Status | Fix Required |
|----|----------|-------------|--------|--------------|
| H7-004 | MINOR | Mixed p-value basis for stars in LaTeX table | NOT FIXED | Unify to use two-tailed p-values for both IVs |
| H7-005 | MINOR | min_calls filter timing incorrect | NOT FIXED | Apply filter AFTER listwise deletion |

### 2.2 Issues NOT Requiring Fixes (Documented/Accepted)

| ID | Severity | Description | Status | Reason |
|----|----------|-------------|--------|--------|
| H7-001 | MAJOR | DV extreme skew (17.4) not addressed | DOCUMENTED | H7 not supported; no transformation needed |
| H7-002 | MINOR | LaTeX table missing notes | FIXED | Already resolved |
| H7-003 | NOTE | Missing run_manifest.json | FIXED | Already resolved |
| H7-006 | NOTE | Utility sample low power | DOCUMENTED | Known limitation, N=78 firms |

---

## PART 3: DETAILED FIX SPECIFICATIONS

### 3.1 H7-004: Mixed P-Value Basis

**Problem:**
The LaTeX table uses inconsistent p-value bases for significance stars:
- Manager IV (beta1): Uses `beta1_p_one` (one-tailed) — line 300
- CEO IV (beta2): Uses `beta2_p_two` (two-tailed) — line 312

This creates inconsistent interpretation of significance stars in the table.

**Target File:** `src/f1d/econometric/run_h7_illiquidity.py`

**Current Code (line 300):**
```python
row_b += f"{fmt_coef(r['beta1'], r['beta1_p_one'])} & "
```

**Current Code (line 312):**
```python
row_b2 += f"{fmt_coef(r['beta2'], r['beta2_p_two'])} & "
```

**Required Fix:**
Change line 312 to use `beta2_p_one` (one-tailed) to match line 300, since H7 is a directional hypothesis (β₁ > 0).

**Rationale:**
- H7 is a directional hypothesis: "Speech vagueness increases future stock illiquidity"
- All H-suites use one-tailed tests for the primary hypothesis
- The table note already states "(one-tailed for H7)"
- Consistency is critical for reviewer interpretation

**Alternative (if two-tailed is preferred):**
Change line 300 to use `beta1_p_two` (two-tailed) and update the table note accordingly.

**Recommendation:** Use one-tailed for both (change line 312).

---

### 3.2 H7-005: Min_Calls Filter Timing

**Problem:**
The `min_calls >= 5` filter is applied BEFORE listwise deletion, which can create singletons in the regression sample.

**Target File:** `src/f1d/econometric/run_h7_illiquidity.py`

**Current Code (lines 476-477):**
```python
call_counts = df_sample.groupby("gvkey")["file_name"].transform("count")
df_filtered = df_sample[call_counts >= CONFIG["min_calls"]].copy()
```

This filter is applied to `df_sample` before it's passed to `run_regression()`, which then performs listwise deletion at line 175.

**Issue:**
A firm with 5 calls might drop to 4 or fewer after listwise deletion, creating singletons or nearly-empty firm clusters.

**Required Fix:**
Move the min_calls filter to AFTER listwise deletion. This requires restructuring the code:

**Option A (Recommended):**
1. Remove lines 476-477 from the main loop
2. Add min_calls filtering inside `run_regression()` AFTER the dropna at line 175

**Pseudocode for fix:**
```python
# Inside run_regression(), after line 175:
df_reg = df_sample.replace([np.inf, -np.inf], np.nan).dropna(subset=required).copy()

# Add min_calls filter here:
if min_calls > 1:
    call_counts = df_reg.groupby("gvkey")["file_name"].transform("count")
    df_reg = df_reg[call_counts >= min_calls].copy()
```

**Note:** This may change sample sizes slightly. The execution report must document the before/after sample sizes.

---

## PART 4: FIX PLANNING PROCEDURE

### 4.1 Step 1: Read Current Code

Execute EXACTLY:

```bash
# Read the full file first
# Then focus on specific sections

# For H7-004: lines 295-320 (LaTeX table generation)
grep -n "fmt_coef\|beta1_p\|beta2_p" src/f1d/econometric/run_h7_illiquidity.py

# For H7-005: lines 470-490 (min_calls filter) and line 175 (listwise deletion)
grep -n "min_calls\|dropna\|transform.*count" src/f1d/econometric/run_h7_illiquidity.py
```

### 4.2 Step 2: Analyze Code Context

For each issue:
1. Read 10 lines before and after the target line
2. Understand the function context and data flow
3. Identify any dependencies that might be affected

### 4.3 Step 3: Draft the Fix

Write out EXACTLY:
- The `old_string` (unique text to be replaced)
- The `new_string` (replacement text)

**CRITICAL:**
- The `old_string` must be EXACTLY as it appears in the file
- The `old_string` must be UNIQUE (expand context if necessary)
- Preserve exact indentation (spaces, not tabs if file uses spaces)

### 4.4 Step 4: Verify Plan Against Audit Findings

The audit verified:
- H7-004: `beta1_p_one` at line 300, `beta2_p_two` at line 312
- H7-005: Filter at lines 476-477, listwise deletion at line 175

Your fix must address these exact locations.

---

## PART 5: FIX EXECUTION PROCEDURE

### 5.1 Order of Fixes

Execute fixes in this order:
1. **H7-004 first** (simple one-line change, low risk)
2. **H7-005 second** (requires code restructuring, higher risk)

### 5.2 Execute Each Edit

Use the Edit tool (NOT Write):

```
Edit(
    file_path="src/f1d/econometric/run_h7_illiquidity.py",
    old_string="[exact text to replace]",
    new_string="[exact replacement text]"
)
```

### 5.3 Verify Each Fix

After each edit:
1. Re-read the modified section to confirm the edit was applied correctly
2. Check that no unintended changes were made
3. Verify Python syntax is correct (try importing the module)

### 5.4 Syntax Verification

After all edits, verify the code is syntactically valid:

```bash
python -c "import ast; ast.parse(open('src/f1d/econometric/run_h7_illiquidity.py').read())"
```

---

## PART 6: OUTPUT FORMAT

Your output document must be written to:
`docs/provenance/FIX_EXECUTION_REPORT_H7.md`

### Required Sections

```markdown
# Fix Execution Report: Suite H7

**Date:** [TODAY'S DATE]
**Executor:** [AI Model + Version]
**Input Document:** AUDIT_REVERIFICATION_H7.md
**Target Files Modified:** [List all modified files with full paths]

---

## Executive Summary

| Issues Fixed | Issues Unfixable | Issues Skipped |
|--------------|------------------|----------------|
| X | Y | Z |

### Files Modified
- [List each file with full path]

---

## Issue Fix Details

### H7-004: Mixed P-Value Basis

**Status Before Fix:** NOT FIXED

**Target File:** src/f1d/econometric/run_h7_illiquidity.py
**Target Line:** 312

#### Before State
```
[Exact line 312 before modification]
```

#### Planned Change
```
old_string: |
  [exact old_string used in Edit tool]

new_string: |
  [exact new_string used in Edit tool]
```

#### After State
```
[Exact line 312 after modification]
```

#### Verification
- [ ] Edit was applied successfully
- [ ] No unintended changes made
- [ ] Both IVs now use consistent p-value basis

**Verdict:** [FIXED / FAILED / SKIPPED]

---

### H7-005: Min_Calls Filter Timing

**Status Before Fix:** NOT FIXED

**Target File:** src/f1d/econometric/run_h7_illiquidity.py
**Target Lines:** [Specify exact lines modified]

#### Before State
```
[Exact code before modification, with line numbers]
```

#### Planned Change
```
old_string: |
  [exact old_string used in Edit tool]

new_string: |
  [exact new_string used in Edit tool]
```

#### After State
```
[Exact code after modification, with line numbers]
```

#### Verification
- [ ] Edit was applied successfully
- [ ] No unintended changes made
- [ ] Filter now applied after listwise deletion
- [ ] Code is syntactically valid

**Verdict:** [FIXED / FAILED / SKIPPED]

---

## Syntax Verification

```bash
python -c "import ast; ast.parse(open('src/f1d/econometric/run_h7_illiquidity.py').read())"
```

Result: [SUCCESS / FAILURE]

---

## Impact Assessment

### Sample Size Changes (if H7-005 fixed)
[Document any changes to sample sizes after re-running]

### Table Output Changes
[Document any changes to significance stars or coefficients]

---

## Post-Fix Verification

### Code Consistency Check
[Confirm that the code follows the same patterns as other H-suites]

### Regression Prevention
[Note any steps to prevent these issues from recurring]

---

## Command Log

[Complete list of every command executed]

---

## Appendix: Full File Diff

[Optional: unified diff of all changes made]
```

---

## PART 7: EXECUTION CHECKLIST

Before completing your fix, confirm:

- [ ] I have read the target file in full before making changes
- [ ] I have planned each exact change with specific line numbers
- [ ] I have used Edit tool (not Write) for surgical modifications
- [ ] I have verified each edit was applied correctly by re-reading
- [ ] I have confirmed no unintended changes were made
- [ ] I have verified Python syntax is still valid after edits
- [ ] I have documented the before/after state with evidence
- [ ] My execution report follows the Part 6 format exactly
- [ ] My execution report is saved to `docs/provenance/FIX_EXECUTION_REPORT_H7.md`

---

## ANTI-HALLUCINATION PROTOCOL

If you make any of the following statements, you MUST provide exact evidence:

| Statement | Required Evidence |
|-----------|------------------|
| "The file contains X" | Exact line numbers and text |
| "I changed Y to Z" | Before/after snippets with line numbers |
| "The fix is correct" | Cross-reference to code and audit data |
| "No other changes were made" | Re-read of file showing only intended modification |
| "The code is syntactically valid" | Output of ast.parse or import attempt |

**FAILURE TO PROVIDE EVIDENCE = HALLUCINATION = FIX INVALID**

---

## PART 8: RISK ASSESSMENT

### H7-004 (P-Value Basis)
- **Risk Level:** LOW
- **Impact:** Changes which p-values determine significance stars
- **Reversibility:** Easy (single line change)
- **Testing:** Visual inspection of LaTeX table output

### H7-005 (Min_Calls Filter)
- **Risk Level:** MEDIUM
- **Impact:** May change sample sizes and regression results
- **Reversibility:** Moderate (code restructuring)
- **Testing:** Compare sample sizes before/after; ensure no new errors

---

## PART 9: POST-FIX RECOMMENDATIONS

After completing the fixes:

1. **Re-run the pipeline** (optional but recommended):
   ```bash
   python src/f1d/variables/build_h7_illiquidity_panel.py
   python src/f1d/econometric/run_h7_illiquidity.py
   ```

2. **Verify output changes**:
   - Check if sample sizes changed
   - Check if significance stars changed
   - Verify cross-artifact consistency still holds

3. **Update provenance documentation**:
   - Update `H7.md` if sample sizes or methodology changed
   - Document the fixes in the "Known Issues" or "Changelog" section

---

END OF PROMPT
