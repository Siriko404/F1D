# H4 Reverification Agent Prompt

**Purpose:** This prompt instructs an AI agent to perform a thorough, manual, one-by-one reverification of all claimed issues in the H4 Leverage Discipline suite, checking whether each issue is still present or has been fixed.

**Deliverable:** A document `REVERIFICATION_REPORT_H4.md` in `docs/provenance/` that is audit-ready, thorough, and shows zero hallucination.

---

## AGENT INSTRUCTIONS

### Role
You are a meticulous code and data auditor. Your job is to verify claims made in prior audit documents by examining the actual codebase and artifacts. You must be thorough, diligent, and evidence-based.

### Critical Rules

1. **NO BULK PROCESSING** - You must examine each claim individually, one at a time. No batch verification.

2. **ZERO HALLUCINATION** - Every statement you make must be backed by:
   - A direct file read with specific line numbers, OR
   - A specific command output you have executed, OR
   - A specific code section you have examined

3. **SHOW YOUR WORK** - For each claim, document:
   - What you checked (file path, line numbers)
   - What you found (exact output, exact code)
   - Your conclusion (PASS/FAIL/PARTIAL with reasoning)

4. **NO ASSUMPTIONS** - Do not assume anything is fixed or broken. Verify everything from first principles.

5. **AD HOC TARGETED COMMANDS ONLY** - You may run specific verification commands, but not bulk processing scripts.

---

## PHASE 1: CLAIM EXTRACTION

First, read the three source documents and extract a **Claim Ledger** - a complete list of all claimed issues with their metadata:

### Source Documents
1. `docs/provenance/H4.md` - The provenance documentation
2. `docs/provenance/AUDIT_H4.md` - The adversarial code audit
3. `docs/provenance/Paper_Artifacts_Audit_H4.md` - The paper-submission readiness audit

### Claim Ledger Format

Create a table with these columns:

| ID | Severity | Category | Claim | Source Doc | Source Section | Status |
|----|----------|----------|-------|------------|----------------|--------|

Where:
- **ID**: Unique identifier (e.g., BLK-1, MAJ-1, MIN-1, NOT-1)
- **Severity**: BLOCKER / MAJOR / MINOR / NOTE
- **Category**: Missing Artifact / Documentation Error / Code Bug / Data Quality
- **Claim**: The specific issue claimed
- **Source Doc**: Which audit document raised this
- **Source Section**: Section number in that document
- **Status**: PENDING (before verification)

---

## PHASE 2: MANUAL VERIFICATION

For each claim in the ledger, perform the following verification process:

### Step 2.1: Read the Claim Carefully
- What exactly is being claimed?
- What file/artifact is referenced?
- What would constitute "fixed" vs "still broken"?

### Step 2.2: Locate the Target
- Find the exact file path
- Identify the specific line numbers or sections
- If it's a missing artifact, confirm the expected location

### Step 2.3: Execute Verification
- Read the file(s) directly
- Run targeted commands to check artifacts
- Compare actual state to claimed state

### Step 2.4: Document Evidence
- Quote exact lines from files
- Show exact command outputs
- Note any discrepancies

### Step 2.5: Render Verdict
- **FIXED**: The issue has been resolved
- **STILL PRESENT**: The issue persists as described
- **PARTIALLY FIXED**: Some aspects fixed, others not
- **CLAIM INVALID**: The original claim was incorrect

---

## CLAIMS TO VERIFY (Pre-Extracted)

### BLOCKER Claims

#### BLK-1: Missing Run Manifest
- **Claim:** No `run_manifest.json` in Stage 4 output directory
- **Source:** Paper_Artifacts_Audit_H4.md, Section 6, BLOCKER #1
- **Expected Location:** `outputs/econometric/h4_leverage/{timestamp}/run_manifest.json`
- **Fix Verification:** Check if file exists in latest output directory

#### BLK-2: Missing Sample Attrition Table
- **Claim:** No sample attrition table showing row counts across filters
- **Source:** Paper_Artifacts_Audit_H4.md, Section 6, BLOCKER #2
- **Expected:** CSV or TeX file with attrition counts per filter per sample
- **Fix Verification:** Search for any attrition-related files in outputs

#### BLK-3: LaTeX Table Lacks Notes
- **Claim:** `h4_leverage_table.tex` has no `\begin{tablenotes}` section
- **Source:** Paper_Artifacts_Audit_H4.md, Section 6, BLOCKER #3
- **Expected Location:** `outputs/econometric/h4_leverage/{timestamp}/h4_leverage_table.tex`
- **Fix Verification:** Read the LaTeX file and check for tablenotes

### MAJOR Claims

#### MAJ-1: Provenance Doc Claims "Balanced Panel"
- **Claim:** H4.md states "Balanced panel" but panel is unbalanced
- **Source:** AUDIT_H4.md Finding #1; Paper_Artifacts_Audit_H4.md MAJOR #1
- **Expected Location:** `docs/provenance/H4.md` Section A1
- **Fix Verification:** Read H4.md and check the exact wording

#### MAJ-2: PRES_CONTROL_MAP Asymmetry Underdocumented
- **Claim:** Documentation doesn't clarify that Weak_Modal QA DVs use Pres Uncertainty control
- **Source:** Paper_Artifacts_Audit_H4.md MAJOR #2
- **Expected Location:** `docs/provenance/H4.md` Section A4
- **Fix Verification:** Read H4.md and check for clarification

#### MAJ-3: Within-R² Bug (Originally MAJOR)
- **Claim:** LaTeX table reported inflated Within-R² values (0.63-0.92 vs true 0.0002-0.027)
- **Source:** AUDIT_H4.md Finding #2
- **Status Claimed in Paper Audit:** "WITHIN-R² BUG FIXED"
- **Fix Verification:** Check BOTH:
  1. `run_h4_leverage.py` code now uses `model.rsquared_within`
  2. Latest `model_diagnostics.csv` has correct values (0.0002-0.027)
  3. Latest LaTeX table reports correct values

### MINOR Claims

#### MIN-1: No Cluster Count in Diagnostics
- **Claim:** `model_diagnostics.csv` does not include `n_clusters` column
- **Source:** Paper_Artifacts_Audit_H4.md MINOR #1
- **Fix Verification:** Read `model_diagnostics.csv` and check columns

#### MIN-2: Variable Lineage Not Machine-Readable
- **Claim:** Variable dictionary is prose in H4.md, not JSON/YAML
- **Source:** Paper_Artifacts_Audit_H4.md MINOR #2
- **Fix Verification:** Search for `variable_lineage.json` or similar

### NOTE Claims

#### NOT-1: No Coefficient Forest Plot
- **Claim:** No visualization of Lev_lag coefficients across specifications
- **Source:** Paper_Artifacts_Audit_H4.md NOTE #1
- **Fix Verification:** Check if any forest plot files exist

#### NOT-2: Linguistic Engine Log Message Misleading
- **Claim:** Log says "per-year 1%/99%" but code uses 0%/99%
- **Source:** AUDIT_H4.md Finding #5
- **Expected Location:** `src/f1d/variables/engines/_linguistic_engine.py` around line 259
- **Fix Verification:** Read the code and check log message

#### NOT-3: panel_utils.py Docstring Stale
- **Claim:** Docstring says 50% threshold but code uses 80%
- **Source:** AUDIT_H4.md Finding #6
- **Expected Location:** `src/f1d/variables/panel_utils.py` line 95 vs 170
- **Fix Verification:** Read the file and compare docstring to code

---

## VERIFICATION COMMANDS REFERENCE

Use these targeted commands (adapt paths as needed):

### File Existence Checks
```bash
# Check for run_manifest.json
find outputs/econometric/h4_leverage -name "run_manifest.json" -type f

# Check for attrition files
find outputs -name "*attrition*" -type f

# Check for forest plots
find outputs/econometric/h4_leverage -name "*forest*" -type f
find outputs/econometric/h4_leverage -name "*.png" -type f
```

### Content Verification
```bash
# Check H4.md for "Balanced" or "Unbalanced"
grep -n -i "balanced\|unbalanced" docs/provenance/H4.md

# Check LaTeX table for tablenotes
grep -n "tablenotes" outputs/econometric/h4_leverage/LATEST/h4_leverage_table.tex

# Check diagnostics columns
python -c "import pandas as pd; df = pd.read_csv('outputs/econometric/h4_leverage/LATEST/model_diagnostics.csv'); print(df.columns.tolist())"
```

### Within-R² Verification
```bash
# Check diagnostics Within-R² range
python -c "
import pandas as pd
df = pd.read_csv('outputs/econometric/h4_leverage/LATEST/model_diagnostics.csv')
r2_col = [c for c in df.columns if 'r2' in c.lower() or 'within' in c.lower()]
print(f'R² columns: {r2_col}')
for col in r2_col:
    print(f'{col}: min={df[col].min():.6f}, max={df[col].max():.6f}')
"
```

### Code Verification
```bash
# Check run_h4_leverage.py for within-R² fix
grep -n "rsquared_within" src/f1d/econometric/run_h4_leverage.py
```

---

## OUTPUT FORMAT

Your final deliverable must be written to:
```
docs/provenance/REVERIFICATION_REPORT_H4.md
```

### Required Structure

```markdown
# H4 Leverage Discipline — Reverification Report

**Verification Date:** YYYY-MM-DD
**Verifier:** AI Auditor
**Scope:** All claims from AUDIT_H4.md and Paper_Artifacts_Audit_H4.md

---

## 1. Executive Summary

| Metric | Count |
|--------|-------|
| Total Claims Verified | X |
| Claims Fixed | X |
| Claims Still Present | X |
| Claims Invalid | X |
| Claims Partially Fixed | X |

### Top 3 Outstanding Issues
1. [Most critical unresolved issue]
2. [Second most critical]
3. [Third most critical]

---

## 2. Claim Ledger (Full)

| ID | Severity | Claim | Verdict | Evidence |
|----|----------|-------|---------|----------|
| BLK-1 | BLOCKER | No run_manifest.json | FIXED/STILL PRESENT | [Link to section] |
| ... | ... | ... | ... | ... |

---

## 3. Detailed Verification Results

### 3.1) BLK-1: Missing Run Manifest

**Original Claim:** No `run_manifest.json` in Stage 4 output directory.

**Verification Method:**
- Command: `find outputs/econometric/h4_leverage -name "run_manifest.json" -type f`
- Directory listing of latest output folder

**Evidence:**
```
[Paste exact command output or file contents]
```

**Verdict:** FIXED / STILL PRESENT / CLAIM INVALID

**Reasoning:** [Explain why you reached this verdict]

---

[Continue for each claim...]

---

## 4. Cross-Verification Checks

### 4.1) Within-R² End-to-End Check

Verify that the Within-R² fix is complete across all artifacts:
1. Code uses `model.rsquared_within`
2. Diagnostics CSV has correct values
3. LaTeX table has correct values

**Code Check:**
```
[Grep output from run_h4_leverage.py]
```

**Diagnostics Check:**
```
[Python output showing min/max Within-R²]
```

**LaTeX Check:**
```
[Relevant lines from h4_leverage_table.tex]
```

**Verdict:** CONSISTENT / INCONSISTENT

---

## 5. Outstanding Issues

List all issues that are NOT fixed, ordered by severity:

### Still Blocking Paper Submission
1. [Issue description with evidence]

### Minor Issues Remaining
1. [Issue description with evidence]

---

## 6. Recommendations

### Immediate Actions Required
1. [Action 1]
2. [Action 2]

### Optional Improvements
1. [Improvement 1]
2. [Improvement 2]

---

## 7. Verification Log

Chronological log of all commands executed:

| # | Command | Purpose | Output Summary |
|---|---------|---------|----------------|
| 1 | `find ...` | Check for manifest | Not found / Found at ... |
| ... | ... | ... | ... |

---

## 8. Confidence Assessment

| Aspect | Confidence | Justification |
|--------|------------|---------------|
| Claim extraction accuracy | High/Medium/Low | [Reason] |
| Verification thoroughness | High/Medium/Low | [Reason] |
| Evidence reliability | High/Medium/Low | [Reason] |

---

*Verification complete. All claims examined individually. No bulk processing used.*
```

---

## QUALITY CHECKLIST

Before submitting your report, verify:

- [ ] Every claim from both audit documents has been addressed
- [ ] Every verdict has direct evidence (command output or file content)
- [ ] No claim was verified by assumption or inference
- [ ] File paths and line numbers are exact, not approximate
- [ ] The report is self-contained (reader doesn't need other docs)
- [ ] The executive summary accurately reflects the detailed findings
- [ ] Outstanding issues are clearly prioritized
- [ ] The verification log is complete and chronological

---

## FINAL INSTRUCTION

Begin by reading the three source documents and extracting the complete claim ledger. Then proceed to verify each claim one by one, documenting your evidence as you go. Do not skip any claim. Do not assume any fix - verify everything.

Write your final report to `docs/provenance/REVERIFICATION_REPORT_H4.md`.
