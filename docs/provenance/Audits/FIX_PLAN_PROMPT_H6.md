# H6 Systematic Fix Planning Prompt

**Purpose:** This prompt instructs an AI agent to plan and execute systematic fixes for all outstanding issues identified in the H6 reverification audit.

**Deliverable:**
1. A fix plan document `FIX_PLAN_H6.md` in `docs/provenance/`
2. Execution of all fixes
3. A verification report confirming fixes are complete

---

## AGENT INSTRUCTIONS

### Role
You are a meticulous software engineer tasked with fixing documented issues in the H6 SEC Scrutiny (CCCL) suite. You must be systematic, thorough, and verify each fix before moving to the next.

### Critical Rules

1. **ONE FIX AT A TIME** — Complete each fix fully before starting the next.

2. **VERIFY BEFORE AND AFTER** — For each fix:
   - Document the "before" state (what's wrong)
   - Make the fix
   - Document the "after" state (proof it's fixed)

3. **NO SPECULATION** — Only fix what is explicitly documented as broken. Do not make "improvements" or refactors.

4. **PRESERVE EXISTING FUNCTIONALITY** — Do not break working code. Make minimal surgical changes.

5. **ATOMIC COMMITS** — Each fix should be a separate, atomic change that can be reviewed independently.

---

## PHASE 1: READ THE REVERIFICATION REPORT

First, read the reverification report to understand exactly what needs to be fixed:

```
docs/provenance/REVERIFICATION_REPORT_H6.md
```

Extract the **Outstanding Issues** section and create a fix checklist.

---

## PHASE 2: CREATE FIX PLAN

Create a file `docs/provenance/FIX_PLAN_H6.md` with the following structure:

```markdown
# H6 Systematic Fix Plan

**Created:** YYYY-MM-DD
**Based On:** REVERIFICATION_REPORT_H6.md
**Status:** PENDING

---

## Fix Checklist

| # | ID | Severity | Issue | Target File | Status |
|---|-----|----------|-------|-------------|--------|
| 1 | BLK-1 | BLOCKER | README detailed table wrong values | README.md | PENDING |
| 2 | MIN-1 | MINOR | LaTeX table missing Finance sample | run_h6_cccl.py, h6_cccl_table.tex | PENDING |
| 3 | MIN-2 | MINOR | merge_asof tolerance missing | panel_utils.py | PENDING |

---

## Fix #1: BLK-1 README Detailed Table

### Problem Statement
[Exact description of what's wrong]

### Root Cause
[Why it's wrong]

### Fix Strategy
[What changes will be made]

### Target File(s)
- README.md (lines X-Y)

### Verification Method
[How to verify the fix worked]

### Status: PENDING / IN PROGRESS / COMPLETE

---

[Repeat for each fix]
```

---

## PHASE 3: EXECUTE FIXES

For each fix in priority order (BLOCKER → MAJOR → MINOR), follow this workflow:

### Step 3.1: Document Before State
Read the problematic file and capture the exact current state:

```
BEFORE:
[Exact lines from file showing the problem]
```

### Step 3.2: Identify Correct Values
If the fix requires correct data values (e.g., coefficients, N values):
1. Read the authoritative source (e.g., `model_diagnostics.csv`)
2. Extract the exact correct values
3. Document them

```
CORRECT VALUES (from model_diagnostics.csv):
- Main Mgr QA Unc: beta1 = -0.0865, p = 0.089, N = 63902
- Main CEO QA Unc: beta1 = 0.0227, p = 0.599, N = 48091
- Finance Mgr QA Unc: beta1 = -1.3066, p = 0.014, N = 15662
...
```

### Step 3.3: Make the Fix
Edit the file with the minimal change needed. Use surgical edits, not rewrites.

### Step 3.4: Document After State
Read the file again and capture the new state:

```
AFTER:
[Exact lines from file showing the fix]
```

### Step 3.5: Verify the Fix
Run any verification commands needed to confirm the fix is correct:

```
VERIFICATION:
[Command output showing fix is correct]
```

### Step 3.6: Update Fix Plan
Mark the fix as COMPLETE in `FIX_PLAN_H6.md`

---

## DETAILED FIX SPECIFICATIONS

### Fix #1: BLK-1 README Detailed Table (BLOCKER)

**Problem:** The README H6 detailed table (lines 469-474) contains incorrect values that misrepresent the actual findings.

**Current Wrong Values (from reverification):**
| Row | Current (Wrong) | Correct Value |
|-----|-----------------|---------------|
| Main Mgr QA Unc β | -0.0007 | -0.0865 |
| Main Mgr QA Unc p | 0.414 | 0.089 |
| Main CEO QA Unc N | 63,902 | 48,091 |
| Finance N | 12,376 | 15,662 |

**Authoritative Source:** `outputs/econometric/h6_cccl/{latest}/model_diagnostics.csv`

**Fix Steps:**
1. Read README.md lines 465-480 to understand the full table context
2. Read model_diagnostics.csv to get exact correct values
3. Edit README.md to replace incorrect values with correct ones
4. Preserve table formatting exactly
5. Verify by re-reading the edited section

**Verification Command:**
```python
# After fix, verify README values match diagnostics
import pandas as pd
# Read the correct values from diagnostics
# Compare to README table
```

---

### Fix #2: MIN-1 LaTeX Table Missing Finance Sample (MINOR)

**Problem:** The LaTeX table `h6_cccl_table.tex` only shows Main sample results. The 4 significant Finance results are not included in any publication table.

**Options:**
1. **Option A:** Add a second LaTeX table for Finance sample
2. **Option B:** Add Finance columns to existing table
3. **Option C:** Add a note to table caption referencing Finance results

**Recommendation:** Option C is the least invasive and provides paper-ready documentation without code changes.

**Fix Steps (Option C):**
1. Read the current table caption/notes in `h6_cccl_table.tex`
2. Add a note: "Finance sample shows 4/7 significant results (p<0.05); see model_diagnostics.csv for full results."
3. This requires regenerating the table OR manual edit

**Note:** If the LaTeX table is auto-generated by `run_h6_cccl.py`, this fix may require:
- Editing `run_h6_cccl.py` to add the note, OR
- Manual edit of the generated `.tex` file

**Assessment:** Determine if this is a code change or documentation change. If code change, assess whether rerun is needed.

---

### Fix #3: MIN-2 merge_asof Tolerance (MINOR)

**Problem:** The `merge_asof` calls in `panel_utils.py` and `cccl_instrument.py` lack a tolerance parameter, allowing 78 stale matches where calls are matched to Compustat data from the wrong fiscal year.

**Target Files:**
- `src/f1d/variables/panel_utils.py` (merge_asof call around line 152-158)
- `src/f1d/variables/builders/cccl_instrument.py` (merge_asof call around line 77-84)

**Fix:**
Add `tolerance=pd.Timedelta(days=548)` (1.5 years) to the merge_asof calls.

**Code Change:**
```python
# BEFORE:
merged = pd.merge_asof(
    panel_sorted_valid, fyearq_df,
    left_on="_start_date_dt", right_on="datadate",
    by="gvkey", direction="backward"
)

# AFTER:
merged = pd.merge_asof(
    panel_sorted_valid, fyearq_df,
    left_on="_start_date_dt", right_on="datadate",
    by="gvkey", direction="backward",
    tolerance=pd.Timedelta(days=548)  # ~1.5 years max gap
)
```

**Impact:** This requires:
1. Stage 3 rerun (`python -m f1d.variables.build_h6_cccl_panel`)
2. Stage 4 rerun (`python -m f1d.econometric.run_h6_cccl`)
3. Verification that results are stable (coefficient changes < 0.001 expected)

**Assessment:** This is a low-priority fix with minimal impact on results (0.07% of data). Consider whether to fix now or defer.

---

## PHASE 4: FINAL VERIFICATION

After all fixes are complete:

1. **Re-run the reverification checks** for each fixed issue
2. **Update the reverification report** to reflect new status
3. **Create a summary** of what was changed

---

## PHASE 5: OUTPUT DELIVERABLES

At the end, you must have created/updated:

1. ✅ `docs/provenance/FIX_PLAN_H6.md` — The fix plan
2. ✅ `README.md` — Fixed detailed table
3. ✅ `docs/provenance/FIX_EXECUTION_REPORT_H6.md` — Summary of what was done

---

## QUALITY CHECKLIST

Before reporting completion:

- [ ] All BLOCKER issues fixed and verified
- [ ] Each fix documented with before/after evidence
- [ ] No unintended changes to working code
- [ ] Fix plan updated with completion status
- [ ] Final verification confirms all targeted issues resolved

---

## PRIORITY ORDER

Execute fixes in this order:

1. **BLK-1** (BLOCKER) — README detailed table
2. **MIN-1** (MINOR) — LaTeX table Finance note (if simple)
3. **MIN-2** (MINOR) — merge_asof tolerance (assess effort vs impact)

**Important:** Fix #3 (merge_asof) requires a full Stage 3+4 rerun. Only proceed if:
- The user explicitly wants this fix, OR
- You determine it's critical for paper submission

Otherwise, document it as a "deferred" fix in the execution report.

---

## FINAL INSTRUCTION

1. Read `docs/provenance/REVERIFICATION_REPORT_H6.md` to understand the issues
2. Create `docs/provenance/FIX_PLAN_H6.md` with the fix plan
3. Execute Fix #1 (BLK-1) — this is mandatory
4. Assess and optionally execute Fix #2 and Fix #3
5. Create `docs/provenance/FIX_EXECUTION_REPORT_H6.md` summarizing what was done

Focus first on fixing the BLOCKER (BLK-1). The MINOR issues can be deferred if they require significant effort or reruns.
