# H6 Reverification Agent Prompt

**Purpose:** This prompt instructs an AI agent to perform a thorough, manual, one-by-one reverification of all claimed issues in the H6 SEC Scrutiny (CCCL) suite, checking whether each issue is still present or has been fixed.

**Deliverable:** A document `REVERIFICATION_REPORT_H6.md` in `docs/provenance/` that is audit-ready, thorough, and shows zero hallucination.

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
1. `docs/provenance/H6.md` - The provenance documentation
2. `docs/provenance/AUDIT_H6.md` - The adversarial code audit
3. `docs/provenance/Paper_Artifacts_Audit_H6.md` - The paper-submission readiness audit

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

#### BLK-1: README H6 Detailed Table Has Incorrect Coefficient Values
- **Claim:** README lines 469-474 show within-R² values (-0.0007) instead of actual beta coefficients (-0.0865), wrong N values, and wrong p-values
- **Source:** Paper_Artifacts_Audit_H6.md, Section 6, Finding #1
- **Expected Location:** `README.md` lines 469-474
- **Fix Verification:**
  1. Read README.md lines 469-474
  2. Compare to `model_diagnostics.csv` actual values
  3. Check if coefficients match beta1 column or within_r2 column

### MAJOR Claims

#### MAJ-1: Pre-Trends Violations Undocumented/Incorrect
- **Claim:** 7 significant lead coefficients (p<0.10) found in pre-trends tests, but H6.md:475 says "no significant pre-trends detected"
- **Source:** AUDIT_H6.md Finding #1, Paper_Artifacts_Audit_H6.md Finding #2
- **Expected Location:**
  - H6.md line 475-478 (documentation)
  - `regression_results_*_PRETRENDS.txt` files (actual results)
- **Fix Verification:**
  1. Read H6.md section on pre-trends
  2. Parse PRETRENDS files for significant lead coefficients
  3. Check if documentation now reflects actual findings

#### MAJ-2: within_r2 Bug (All NaN)
- **Claim:** `within_r2` column in `model_diagnostics.csv` is NaN for all 21 specifications due to index alignment error
- **Source:** AUDIT_H6.md Finding #2
- **Expected Location:**
  - `run_h6_cccl.py` lines 212-238 (code)
  - `model_diagnostics.csv` (output)
- **Fix Verification:**
  1. Check if code now uses `model.rsquared_within` directly
  2. Read latest `model_diagnostics.csv` and check `within_r2` column values
  3. Verify values are in valid range (not NaN, not inflated)

#### MAJ-3: README Summary Inconsistency
- **Claim:** README says "0/6 significant" but actual results show 4/21 significant (Finance sample)
- **Source:** AUDIT_H6.md Finding #3
- **Expected Location:** `README.md` line 477
- **Fix Verification:**
  1. Read README.md H6 summary section
  2. Count significant results in `model_diagnostics.csv`
  3. Compare README text to actual counts

#### MAJ-4: Missing Reproducibility Artifacts
- **Claim:** Missing run_manifest.json, sample attrition table, variable lineage JSON
- **Source:** Paper_Artifacts_Audit_H6.md Finding #3
- **Expected Location:**
  - `outputs/econometric/h6_cccl/{timestamp}/run_manifest.json`
  - Attrition table file
  - Variable lineage JSON
- **Fix Verification:**
  1. Search for run_manifest.json in h6 output directories
  2. Search for attrition files
  3. Search for lineage JSON files

### MINOR Claims

#### MIN-1: LaTeX Table Only Shows Main Sample
- **Claim:** `h6_cccl_table.tex` only shows Main sample; Finance significant results not shown
- **Source:** Paper_Artifacts_Audit_H6.md Finding #4, AUDIT_H6.md Finding #6
- **Expected Location:** `outputs/econometric/h6_cccl/{timestamp}/h6_cccl_table.tex`
- **Fix Verification:**
  1. Read the LaTeX table
  2. Check which samples are included
  3. Check if Finance results are present

#### MIN-2: Stale merge_asof Matches (78 rows)
- **Claim:** 78 calls have |calendar_year - fyearq| > 2 due to merge_asof without tolerance
- **Source:** AUDIT_H6.md Finding #4, Paper_Artifacts_Audit_H6.md Finding #5
- **Expected Location:**
  - `panel_utils.py` merge_asof call
  - Panel data (can verify with Python)
- **Fix Verification:**
  1. Check if tolerance parameter added to merge_asof
  2. Optionally verify stale match count in panel

#### MIN-3: CCCL mkvalt Zero-Inflation
- **Claim:** Heavy zero-inflation (47.9% Main, 36.6% Finance, 77.7% Utility) in CCCL mkvalt weighting
- **Source:** AUDIT_H6.md Finding #5, Paper_Artifacts_Audit_H6.md Finding #6
- **Notes:** This is a methodological note, not a bug
- **Fix Verification:** Document status (acknowledged/unchanged)

### NOTE Claims

#### NOT-1: Provenance Doc Claims "No Significant Pre-Trends" (Incorrect)
- **Claim:** H6.md line 475 states "no significant pre-trends detected" which is factually incorrect
- **Source:** AUDIT_H6.md Finding #7
- **Expected Location:** `docs/provenance/H6.md` line 475
- **Fix Verification:** Read H6.md and check the pre-trends documentation

---

## VERIFICATION COMMANDS REFERENCE

Use these targeted commands (adapt paths as needed):

### File Existence Checks
```bash
# Check for run_manifest.json
find outputs/econometric/h6_cccl -name "run_manifest.json" -type f

# Check for attrition files
find outputs -name "*attrition*" -type f

# List latest Stage 4 output directory
ls -la outputs/econometric/h6_cccl/ | tail -5
```

### README Verification
```bash
# Read H6 section of README
grep -n -A 10 "H6" README.md | head -30

# Read specific lines
sed -n '469,474p' README.md
```

### Diagnostics Verification
```bash
# Check within_r2 values
python -c "
import pandas as pd
from pathlib import Path

# Find latest output directory
out_dirs = sorted(Path('outputs/econometric/h6_cccl').iterdir())
latest = out_dirs[-1]
diag = pd.read_csv(latest / 'model_diagnostics.csv')

print(f'Diagnostics rows: {len(diag)}')
print(f'within_r2 NaN count: {diag[\"within_r2\"].isna().sum()}')
print(f'within_r2 range: {diag[\"within_r2\"].min():.6f} to {diag[\"within_r2\"].max():.6f}')
print(f'Significant count: {diag[\"h6_sig\"].sum()}')
"
```

### Pre-Trends Verification
```bash
# Check for significant leads in PRETRENDS files
python -c "
import os
from pathlib import Path

out_dirs = sorted(Path('outputs/econometric/h6_cccl').iterdir())
latest = out_dirs[-1]

sig_leads = []
for f in latest.glob('*PRETRENDS*.txt'):
    with open(f) as fh:
        for line in fh:
            if 'shift_intensity' in line and ('lead1' in line or 'lead2' in line):
                parts = line.strip().split()
                if len(parts) >= 5:
                    try:
                        p_val = float(parts[4])
                        if p_val < 0.10:
                            sig_leads.append((f.name, parts[0][-5:], parts[1], p_val))
                    except: pass

print(f'Significant leads found: {len(sig_leads)}')
for name, var, beta, p in sig_leads:
    print(f'  {name}: {var} beta={beta} p={p:.4f}')
"
```

### Code Verification
```bash
# Check run_h6_cccl.py for within-R² fix
grep -n "rsquared_within" src/f1d/econometric/run_h6_cccl.py

# Check for merge_asof tolerance
grep -n "tolerance" src/f1d/variables/panel_utils.py
grep -n "merge_asof" src/f1d/variables/panel_utils.py
```

---

## OUTPUT FORMAT

Your final deliverable must be written to:
```
docs/provenance/REVERIFICATION_REPORT_H6.md
```

### Required Structure

```markdown
# H6 SEC Scrutiny (CCCL) — Reverification Report

**Verification Date:** YYYY-MM-DD
**Verifier:** AI Auditor
**Scope:** All claims from AUDIT_H6.md and Paper_Artifacts_Audit_H6.md

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

### Paper-Submission Readiness Verdict
**READY / NOT READY** — [Brief justification]

---

## 2. Claim Ledger (Full)

| ID | Severity | Claim | Verdict | Evidence |
|----|----------|-------|---------|----------|
| BLK-1 | BLOCKER | README has wrong coefficients | FIXED/STILL PRESENT | [Link to section] |
| ... | ... | ... | ... | ... |

---

## 3. Detailed Verification Results

### 3.1) BLK-1: README H6 Detailed Table Has Incorrect Coefficient Values

**Original Claim:** README lines 469-474 show within-R² values instead of actual beta coefficients.

**Verification Method:**
- Read README.md lines 469-474
- Compare to model_diagnostics.csv values

**Evidence:**
```
README content (lines 469-474):
[Paste exact content]

model_diagnostics.csv values:
[Paste relevant rows]
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
3. LaTeX table has correct values (if applicable)

**Code Check:**
```
[Grep output from run_h6_cccl.py]
```

**Diagnostics Check:**
```
[Python output showing within_r2 values]
```

**Verdict:** CONSISTENT / INCONSISTENT

---

### 4.2) Pre-Trends Documentation vs Reality

Compare documented pre-trends claims against actual PRETRENDS output.

**Documentation Claims:**
[Quote from H6.md]

**Actual PRETRENDS Results:**
[Summary of significant leads found]

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

Write your final report to `docs/provenance/REVERIFICATION_REPORT_H6.md`.
