# Systematic Fix Plan Prompt: Suite H10 (Tone-at-the-Top)

**Purpose:** This prompt instructs an AI fix agent to systematically plan and execute fixes for all remaining issues identified in the re-verification audit.

**Target Suite:** H10 — Tone-at-the-Top Transmission (H_TT)
**Input Documents:**
- `docs/provenance/AUDIT_REVERIFICATION_H10.md` (Re-verification audit results)
- `docs/provenance/H10.md` (Provenance documentation)

**Output Deliverable:** `docs/provenance/FIX_EXECUTION_REPORT_H10.md`

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
- Running the full pipeline without explicit instruction
- Modifying test files or unrelated code

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
| **Issue ID** | From AUDIT_REVERIFICATION_H10.md |
| **Target file** | Exact path to file being modified |
| **Before state** | Exact lines before modification (with line numbers) |
| **Planned change** | Exact old_string and new_string for Edit tool |
| **After state** | Exact lines after modification (with line numbers) |
| **Verification** | Confirmation that fix addresses the issue |

---

## PART 2: ISSUE LEDGER FROM AUDIT

### 2.1 Issues Requiring Fixes

Based on `AUDIT_REVERIFICATION_H10.md`, the following issues require fixes:

| ID | Severity | Description | Status | Fix Required |
|----|----------|-------------|--------|--------------|
| H10-001 | BLOCKER | Sample filter bug - "Main" includes ALL industries | NOT FIXED | Change lines 1168-1177 to filter properly |
| H10-003 | MAJOR | Duplicate entity-time index in M1 (347 firm-quarters) | NOT FIXED | Add deduplication before set_index |
| H10-006 | MINOR | Turn_Uncertainty_pct unwinsorized (max=100%) | NOT FIXED | Add winsorization OR document as intentional |
| H10-007 | MINOR | Winsorization inconsistency doc (CEO vs CFO) | NOT FIXED | Update provenance Section G |
| H10-008 | MINOR | No LaTeX sample attrition table | NOT FIXED | Generate from reconciliation_table.csv |
| H10-009 | NOTE | CEO_Unc_Lag1 zero rate undocumented | PARTIAL | Add to provenance Known Issues |
| H10-010 | NOTE | 2002 absent from M1 undocumented | PARTIAL | Add to provenance Known Issues |

### 2.2 Issues Already Fixed (No Action Required)

| ID | Severity | Description | Status |
|----|----------|-------------|--------|
| H10-002 | BLOCKER | LaTeX clustering note incorrect for M2 | FIXED |
| H10-004 | MAJOR | Missing run_manifest.json | FIXED |
| H10-005 | MAJOR | Placebo test failure | DOCUMENTED |

---

## PART 3: DETAILED FIX SPECIFICATIONS

### 3.1 H10-001: Sample Filter Bug (BLOCKER)

**Problem:**
When `sample == "Main"`, the code returns the entire unfiltered panel instead of filtering to `sample == "Main"` rows.

**Impact:**
- M1 Main N=43,570 includes Finance (6,793) + Utility (1,378) when it should be 35,399
- M2 Main N=1,697,632 includes all industries when it should be ~1,309,955
- Results inconsistent with all other H-suites

**Target File:** `src/f1d/econometric/run_h10_tone_at_top.py`

**Current Code (lines 1168-1177):**
```python
call_sub = (
    call_panel
    if sample == "Main"
    else call_panel[call_panel["sample"] == sample]
)
turns_sub = (
    turns_panel
    if sample == "Main"
    else turns_panel[turns_panel["sample"] == sample]
)
```

**Required Fix:**
```python
call_sub = call_panel[call_panel["sample"] == sample].copy()
turns_sub = turns_panel[turns_panel["sample"] == sample].copy()
```

**Rationale:**
- "Main" should filter to `sample == "Main"` just like "Finance" and "Utility" do
- The `.copy()` prevents SettingWithCopyWarning
- This aligns with all other H-suite implementations

**Rerun impact:** Stage 4 only — panel already has correct `sample` column

---

### 3.2 H10-003: Duplicate Entity-Time Index (MAJOR)

**Problem:**
347 firm-quarters have >1 earnings call (694 rows), creating non-unique PanelOLS index.

**Impact:**
- PanelOLS behavior with non-unique index is undefined
- May silently overwrite or average observations
- Creates reproducibility risk

**Target File:** `src/f1d/econometric/run_h10_tone_at_top.py`

**Current Code (line ~135):**
```python
reg_df = reg_df.set_index(["gvkey", "yq_id"])
```

**Required Fix:**
Add deduplication BEFORE set_index:
```python
# Deduplicate firm-quarters by keeping the last call per quarter
reg_df = reg_df.sort_values("start_date").drop_duplicates(
    subset=["gvkey", "yq_id"], keep="last"
)
reg_df = reg_df.set_index(["gvkey", "yq_id"])
```

**Rationale:**
- Keeps the most recent call per firm-quarter (consistent with other suites)
- 694 rows will be reduced by ~347 (0.8% of sample)
- Preserves deterministic behavior

**Rerun impact:** Stage 4 only

---

### 3.3 H10-006: Turn_Uncertainty_pct Unwinsorized (MINOR)

**Problem:**
Turn_Uncertainty_pct ranges 0-100% with 478 turns >50%. These extreme values (likely from short turns) may influence results.

**Two Options:**

**Option A: Add Winsorization (Code Change)**
Add to `build_h10_tone_at_top_panel.py` after Turn_Uncertainty_pct computation:
```python
from f1d.shared.variables.winsorization import winsorize_pooled
qa_tokens["Turn_Uncertainty_pct"] = winsorize_pooled(
    qa_tokens["Turn_Uncertainty_pct"], lower=0.01, upper=0.99
)
```
**Rerun impact:** Stage 3 + Stage 4

**Option B: Document as Intentional (Documentation Only)**
Update `H10.md` Section G to state:
> Turn_Uncertainty_pct is NOT winsorized. Extreme values (>50%) are retained because: (1) the IHS transform compresses extremes, (2) short turns with high uncertainty are valid signals of uncertainty, (3) Call + Speaker FE absorb turn-level outliers.

**Recommendation:** Option B (document as intentional) — the IHS transform already handles extremes, and winsorizing turn-level data could remove legitimate signal.

**Rerun impact:** None (documentation only)

---

### 3.4 H10-007: Winsorization Inconsistency Documentation (MINOR)

**Problem:**
Provenance Section G incorrectly claims "pooled 1/99%" for all linguistic percentages, but:
- CEO_QA_Uncertainty_pct uses per-year winsorization (via LinguisticEngine)
- CFO_QA_Uncertainty_pct uses pooled winsorization
- Turn_Uncertainty_pct uses no winsorization

**Target File:** `docs/provenance/H10.md`

**Current Text (Section G, lines ~280-285):**
```markdown
| Variable Set | Method | Thresholds | Where Applied |
|--------------|--------|------------|---------------|
| Linguistic percentages (`CFO_QA_Uncertainty_pct`, etc.) | Pooled 1%/99% | Lower=0.01, Upper=0.99 | `base.py:_finalize_data()` via `winsorize_pooled()` |
```

**Required Fix:**
Update to correctly document each variable:
```markdown
| Variable | Winsorization Method | Thresholds | Where Applied |
|----------|---------------------|------------|---------------|
| CEO_QA_Uncertainty_pct | Per-year 1%/99% | Lower=0.01, Upper=0.99 | LinguisticEngine |
| CFO_QA_Uncertainty_pct | Pooled 1%/99% | Lower=0.01, Upper=0.99 | `CFOQAUncertaintyBuilder._finalize_data()` |
| Turn_Uncertainty_pct | None (intentional) | N/A | IHS transform handles extremes |
| Financial controls (Size, BM, Lev, ROA) | Per-year 1%/99% | Lower=0.01, Upper=0.99 | CompustatEngine |
```

**Rerun impact:** Documentation only

---

### 3.5 H10-008: LaTeX Sample Attrition Table (MINOR)

**Problem:**
`reconciliation_table.csv` exists but no LaTeX version for publication.

**Target File:** `src/f1d/variables/build_h10_tone_at_top_panel.py` (or create standalone script)

**Required Fix:**
Generate `sample_attrition.tex` from `reconciliation_table.csv`:

```python
def generate_attrition_tex(recon_df: pd.DataFrame, output_path: Path):
    """Generate LaTeX sample attrition table."""
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Sample Attrition: H10 Tone-at-the-Top}",
        r"\label{tab:h10_attrition}",
        r"\begin{tabular}{lrr}",
        r"\toprule",
        r"Stage & N Rows & Delta \\",
        r"\midrule",
    ]
    for _, row in recon_df.iterrows():
        delta_str = f"({row['Delta']:+,})" if pd.notna(row['Delta']) else "—"
        lines.append(f"{row['Stage']} & {row['n_rows']:,} & {delta_str} \\\\")
    lines.extend([
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}",
    ])
    with open(output_path, "w") as f:
        f.write("\n".join(lines))
```

**Rerun impact:** Stage 3 (or generate from existing CSV without rerun)

---

### 3.6 H10-009 & H10-010: Documentation Updates (NOTE)

**H10-009: CEO_Unc_Lag1 Zero Rate**

Add to `H10.md` Section J (Known Issues):
```markdown
### Issue X: CEO_Unc_Lag1 Has High Zero Rate

**Description:** CEO_Unc_Lag1 (used in robustness spec M2_lag1) is 57.9% zeros.

**Cause:** The ffill propagation means many manager turns inherit 0.0 from the first CEO turn's lag (which is NaN→0 after ffill).

**Impact:** The M2_lag1 specification (β=0.0167) has lower coefficient than baseline (β=0.0426), possibly due to the mass of zeros.

**Recommendation:** Interpret M2_lag1 results with caution. The baseline expanding mean specification is preferred.
```

**H10-010: 2002 Absent from M1**

Add to `H10.md` Section J (Known Issues):
```markdown
### Issue Y: Year 2002 Excluded from M1 Sample

**Description:** All four quarters of 2002 are absent from the M1 regression sample (N quarters = 64, not 68).

**Cause:** ClarityStyle_Realtime requires ≥4 prior CEO calls. Since the dataset starts in 2002, CEOs don't accumulate 4 calls until late 2002/early 2003. Combined with listwise deletion on ClarityStyle_Realtime NaN (44.5%), all 2002 observations are eliminated.

**Impact:** Effective estimation period for M1 is 2003Q1–2018Q4.

**Recommendation:** This is expected behavior. Document clearly in paper.
```

---

## PART 4: FIX PLANNING PROCEDURE

### 4.1 Order of Fixes

Execute fixes in this order:
1. **H10-001 (BLOCKER)** — Sample filter bug (code)
2. **H10-003 (MAJOR)** — Duplicate entity-time index (code)
3. **H10-007 (MINOR)** — Winsorization documentation (provenance)
4. **H10-006 (MINOR)** — Turn uncertainty winsorization decision (documentation)
5. **H10-009/010 (NOTE)** — Additional known issues documentation
6. **H10-008 (MINOR)** — LaTeX attrition table (optional, can be deferred)

### 4.2 Step 1: Read Current Code

Execute EXACTLY:

```bash
# Read sample filter section
grep -n "call_sub\|turns_sub\|sample.*Main" src/f1d/econometric/run_h10_tone_at_top.py | head -20

# Read entity-time index section
grep -n "set_index.*gvkey.*yq\|yq_id" src/f1d/econometric/run_h10_tone_at_top.py | head -10
```

### 4.3 Step 2: Draft Exact Changes

For each code fix, write out EXACTLY:
- The `old_string` (unique text to be replaced)
- The `new_string` (replacement text)

**CRITICAL:**
- The `old_string` must be EXACTLY as it appears in the file (including whitespace)
- The `old_string` must be UNIQUE (expand context if necessary)
- Preserve exact indentation

### 4.4 Step 3: Execute Edits

Use the Edit tool (NOT Write):

```
Edit(
    file_path="src/f1d/econometric/run_h10_tone_at_top.py",
    old_string="[exact text to replace]",
    new_string="[exact replacement text]"
)
```

### 4.5 Step 4: Verify Syntax

After all code edits, verify Python syntax:

```bash
python -c "import ast; ast.parse(open('src/f1d/econometric/run_h10_tone_at_top.py').read())"
```

---

## PART 5: OUTPUT FORMAT

Your output document must be written to:
`docs/provenance/FIX_EXECUTION_REPORT_H10.md`

### Required Sections

```markdown
# Fix Execution Report: Suite H10

**Date:** [TODAY'S DATE]
**Executor:** [AI Model + Version]
**Input Document:** AUDIT_REVERIFICATION_H10.md
**Target Files Modified:** [List all modified files with full paths]

---

## Executive Summary

| Issues Fixed | Issues Unfixable | Issues Skipped |
|--------------|------------------|----------------|
| X | Y | Z |

### Files Modified
- [List each file with full path]

### Rerun Required
- [ ] Stage 3
- [ ] Stage 4
- [x] None (documentation only)

---

## Issue Fix Details

### H10-001: Sample Filter Bug

**Status Before Fix:** NOT FIXED (BLOCKER)

**Target File:** src/f1d/econometric/run_h10_tone_at_top.py
**Target Lines:** 1168-1177

#### Before State
```python
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
```python
[Exact code after modification, with line numbers]
```

#### Verification
- [ ] Edit was applied successfully
- [ ] Sample filter now correctly filters "Main" to Main-only
- [ ] No unintended changes made

**Verdict:** [FIXED / FAILED / SKIPPED]

---

### H10-003: Duplicate Entity-Time Index

[Same format]

---

[Continue for all issues]

---

## Syntax Verification

```bash
python -c "import ast; ast.parse(open('src/f1d/econometric/run_h10_tone_at_top.py').read())"
```

Result: [SUCCESS / FAILURE]

---

## Post-Fix Verification

### Expected Changes After Stage 4 Rerun

| Metric | Before Fix | After Fix |
|--------|------------|-----------|
| M1 Main N | 43,570 | ~35,399 |
| M2 Main N | 1,697,632 | ~1,309,955 |
| M1 duplicate entity-time | 347 | 0 |

---

## Command Log

[Complete list of every command executed]

---

## Appendix: Full File Diff

[Optional: unified diff of all changes made]
```

---

## PART 6: EXECUTION CHECKLIST

Before completing your fix, confirm:

- [ ] I have read the target file in full before making changes
- [ ] I have planned each exact change with specific line numbers
- [ ] I have used Edit tool (not Write) for surgical modifications
- [ ] I have verified each edit was applied correctly by re-reading
- [ ] I have confirmed no unintended changes were made
- [ ] I have verified Python syntax is still valid after edits
- [ ] I have documented the before/after state with evidence
- [ ] My execution report follows the Part 5 format exactly
- [ ] My execution report is saved to `docs/provenance/FIX_EXECUTION_REPORT_H10.md`

---

## ANTI-HALLUCINATION PROTOCOL

If you make any of the following statements, you MUST provide exact evidence:

| Statement | Required Evidence |
|-----------|------------------|
| "The file contains X" | Exact line numbers and text |
| "I changed Y to Z" | Before/after snippets with line numbers |
| "The fix is correct" | Cross-reference to audit data |
| "No other changes were made" | Re-read of file showing only intended modification |

**FAILURE TO PROVIDE EVIDENCE = HALLUCINATION = FIX INVALID**

---

## PART 7: H10-SPECIFIC FIX NOTES

### Model Family Context

H10 uses two distinct model families:
- **M1 (Call-level):** PanelOLS with Firm + Year-Quarter FE
- **M2 (Turn-level):** AbsorbingLS with Call + Speaker FE

### Key Code Locations

| Issue | File | Line(s) |
|-------|------|---------|
| Sample filter bug | `run_h10_tone_at_top.py` | 1168-1177 |
| Duplicate index | `run_h10_tone_at_top.py` | ~135 |
| Winsorization doc | `H10.md` | ~280-285 |
| Known issues | `H10.md` | Section J |

### Critical Acceptance Tests

After fixes are applied and Stage 4 is rerun:

```python
# Test 1: Sample filter
import pandas as pd
diag = pd.read_csv('outputs/econometric/tone_at_top/LATEST/model_diagnostics.csv')
main_m1 = diag[diag['model'].str.contains('Main_M1')]
assert 34000 < main_m1['n_obs'].values[0] < 37000, f"Main M1 N = {main_m1['n_obs'].values[0]}"

# Test 2: No duplicates
cp = pd.read_parquet('outputs/variables/tone_at_top/LATEST/tone_at_top_panel.parquet')
cp['yq_id'] = (cp['year'].astype(str) + 'Q' + cp['quarter'].astype(str))
reg = cp[cp['sample'] == 'Main'].dropna(subset=['ClarityStyle_Realtime','CFO_QA_Uncertainty_pct'])
dups = reg.groupby(['gvkey','yq_id']).size()
assert (dups > 1).sum() == 0, "Duplicate entity-time still exists"
```

---

END OF PROMPT
