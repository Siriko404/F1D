# Systematic Fix Plan Prompt: Suite H1 (Cash Holdings)

**Purpose:** This prompt instructs an AI fix agent to systematically plan and execute fixes for all remaining issues identified in the re-verification audit.

**Target Suite:** H1 — Speech Uncertainty and Future Cash Holdings
**Input Documents:**
- `docs/provenance/AUDIT_REVERIFICATION_H1.md` (Re-verification audit results)
- `docs/provenance/H1.md` (Provenance documentation — target of fix)

**Output Deliverable:** `docs/provenance/FIX_EXECUTION_REPORT_H1.md`

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
- Making changes to code files (only documentation files in scope)
- Modifying files not explicitly listed in the fix plan
- Adding new content beyond what's required to fix the issue
- Removing content unless explicitly required

You **MUST**:
- Read the full file before editing
- Preserve all existing formatting and structure
- Keep changes minimal and targeted
- Verify the file still renders correctly after edits

### 1.3 Evidence Standards

For each fix, your execution report MUST include:

| Evidence Type | Required |
|--------------|----------|
| **Issue ID** | From AUDIT_REVERIFICATION_H1.md |
| **Target file** | Exact path to file being modified |
| **Before state** | Exact lines before modification (with line numbers) |
| **Planned change** | Exact old_string and new_string for Edit tool |
| **After state** | Exact lines after modification (with line numbers) |
| **Verification** | Confirmation that fix addresses the issue |

---

## PART 2: ISSUE LEDGER FROM AUDIT

### 2.1 Issues Requiring Fixes

Based on `AUDIT_REVERIFICATION_H1.md`, the following issue requires a fix:

| ID | Severity | Description | Status | Fix Required |
|----|----------|-------------|--------|--------------|
| H1-004 | NOTE | DV constancy provenance claim is ambiguous | PARTIALLY ADDRESSED | Update H1.md Section J.4 to explicitly clarify fiscal vs calendar year |

### 2.2 Detailed Issue Description

**H1-004: DV Constancy Provenance Claim**

**Current State:**
- Section J.4 of `H1.md` discusses the Moulton correction (firm-clustered SEs)
- It mentions "CashHoldings_lead is constant within firm-year clusters" with "(fiscal year)" in parentheses
- However, it does NOT explain that:
  - PanelOLS uses *calendar* year for time fixed effects (via `C(year)`)
  - ~75% of (gvkey, calendar_year) clusters have multiple unique DV values
  - This is why firm-level clustering (not firm-year clustering) is the correct approach

**Required Fix:**
- Update Section J.4 to clearly distinguish between:
  1. Fiscal year (fyearq) — where DV IS constant
  2. Calendar year (year) — where DV is NOT constant (used by PanelOLS time FE)
- Explain why firm-level clustering is still correct despite calendar-year DV variation

**Target Location:** `docs/provenance/H1.md` — Section J.4 (approximately lines 428-436)

---

## PART 3: FIX PLANNING PROCEDURE

### 3.1 Step 1: Read Current State

Execute EXACTLY:

```bash
# First, read the entire H1.md to understand context
# Then focus on Section J.4

# Identify exact line numbers for Section J.4
grep -n "Moulton\|MAJOR-1" docs/provenance/H1.md
```

Then use the Read tool to read the relevant section (approximately lines 420-445).

### 3.2 Step 2: Analyze What Needs to Change

Based on the current text, determine:
1. What paragraphs need modification
2. What new clarifying text is needed
3. Whether the existing (fiscal year) parenthetical is sufficient or needs expansion

### 3.3 Step 3: Draft the Fix

Write out EXACTLY:
- The old_string (the text to be replaced)
- The new_string (the replacement text)

**Requirements for the fix:**
- Must explicitly state that PanelOLS uses calendar year for time FE
- Must explain that fiscal year constancy ≠ calendar year constancy
- Must state that ~75% of calendar year clusters have multiple DV values
- Must reaffirm that firm-level clustering is still the correct econometric approach
- Must NOT change any other content in the section
- Must maintain the existing markdown formatting and structure

### 3.4 Step 4: Verify Plan Against Audit Findings

The AUDIT_REVERIFICATION_H1.md Section 4.4.2 contains verification data:

```
Fiscal year clusters with 1 unique value: 100% (all clusters have exactly 1)
Calendar year clusters with 1 unique value: 25.2% (~75% have >1 unique values)
```

Your fix must be consistent with these verified facts.

---

## PART 4: FIX EXECUTION PROCEDURE

### 4.1 Execute the Edit

Use the Edit tool (NOT Write) to make the change:

```
Edit(
    file_path="docs/provenance/H1.md",
    old_string="[exact text to replace]",
    new_string="[exact replacement text]"
)
```

**CRITICAL:**
- The old_string must be EXACTLY as it appears in the file (including whitespace)
- The old_string must be UNIQUE (if not, expand context to make it unique)

### 4.2 Verify the Fix

After editing:
1. Re-read the modified section to confirm the edit was applied correctly
2. Check that no unintended changes were made
3. Verify the markdown structure is intact

### 4.3 Cross-Check with Code

Verify that the updated documentation accurately reflects the actual implementation:

```bash
# Confirm PanelOLS uses calendar year for time FE
grep -n "C(year)\|TimeEffects" src/f1d/econometric/run_h1_cash_holdings.py

# Confirm firm-level clustering is used
grep -n "cluster_entity" src/f1d/econometric/run_h1_cash_holdings.py
```

---

## PART 5: OUTPUT FORMAT

Your output document must be written to:
`docs/provenance/FIX_EXECUTION_REPORT_H1.md`

### Required Sections

```markdown
# Fix Execution Report: Suite H1

**Date:** [TODAY'S DATE]
**Executor:** [AI Model + Version]
**Input Document:** AUDIT_REVERIFICATION_H1.md
**Target Files Modified:** docs/provenance/H1.md

---

## Executive Summary

| Issues Fixed | Issues Unfixable | Issues Skipped |
|--------------|------------------|----------------|
| X | Y | Z |

### Files Modified
- [List each file with full path]

---

## Issue Fix Details

### H1-004: DV Constancy Provenance Claim

**Status Before Fix:** PARTIALLY ADDRESSED

**Target File:** docs/provenance/H1.md
**Target Section:** J.4 (Moulton Correction / MAJOR-1 Fix)

#### Before State
```
[Exact text before modification, with line numbers]
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
[Exact text after modification, with line numbers]
```

#### Verification
- [ ] Edit was applied successfully
- [ ] No unintended changes made
- [ ] Documentation now accurately reflects implementation
- [ ] Markdown formatting preserved

**Verdict:** [FIXED / FAILED / SKIPPED]

---

## Code Cross-Reference

### PanelOLS Time FE Implementation
```
[Output of grep for C(year)/TimeEffects]
```

### Firm-Clustering Implementation
```
[Output of grep for cluster_entity]
```

---

## Post-Fix Verification

### Documentation Accuracy Check
[Confirm that updated text accurately describes the code behavior]

### Regression Prevention
[Note any steps that should be taken to prevent this documentation from becoming stale]

---

## Command Log

[Complete list of every command executed]

---

## Appendix: Full File Diff

[Optional: unified diff of changes made]
```

---

## PART 6: EXECUTION CHECKLIST

Before completing your fix, confirm:

- [ ] I have read the target file in full before making changes
- [ ] I have planned the exact change with specific line numbers
- [ ] I have used Edit tool (not Write) for surgical modification
- [ ] I have verified the edit was applied correctly by re-reading
- [ ] I have confirmed no unintended changes were made
- [ ] I have cross-checked the documentation against actual code
- [ ] I have documented the before/after state with evidence
- [ ] My execution report follows the Part 5 format exactly
- [ ] My execution report is saved to `docs/provenance/FIX_EXECUTION_REPORT_H1.md`

---

## ANTI-HALLUCINATION PROTOCOL

If you make any of the following statements, you MUST provide exact evidence:

| Statement | Required Evidence |
|-----------|------------------|
| "The file contains X" | Exact line numbers and text |
| "I changed Y to Z" | Before/after snippets with line numbers |
| "The fix is correct" | Cross-reference to code and audit data |
| "No other changes were made" | Re-read of file showing only intended modification |

**FAILURE TO PROVIDE EVIDENCE = HALLUCINATION = FIX INVALID**

---

## PART 7: SAMPLE FIX TEXT

For reference, here is a sample of what the updated Section J.4 might look like:

```markdown
### 4. Moulton Correction (MAJOR-1 Fix)

**Issue:** HC1 standard errors were initially used, but `CashHoldings_lead` exhibits clustering structure that requires correction.

**Clarification on clustering structure:**
- `CashHoldings_lead` is measured at fiscal year end (`fyearq`) and is **constant within (gvkey, fyearq) clusters** — all calls in the same fiscal year share the same DV value.
- However, the PanelOLS estimator uses **calendar year** (`year`) for time fixed effects, not fiscal year.
- Because calls within a calendar year can span two fiscal years (for non-December FYE firms), approximately **75% of (gvkey, calendar_year) clusters contain multiple unique DV values**.
- Despite this calendar-year variation, **firm-level clustering** (`cluster_entity=True`) remains the econometrically correct approach, as it captures arbitrary within-firm serial correlation regardless of time dimension.

**Fix:** Changed to firm-clustered SEs (`cluster_entity=True`) to correct within-firm correlation.

**Verification:** All Stage 4 regressions now use `cov_type="clustered", cluster_entity=True`.
```

**Note:** This is a SAMPLE. You must verify the exact current text and craft your fix accordingly.

---

END OF PROMPT
