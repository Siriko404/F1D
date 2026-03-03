# H8 Reverification Agent Prompt

**Purpose:** This prompt instructs an AI agent to perform a thorough, manual, one-by-one reverification of all claimed issues in the H8 Political Risk × CEO Speech Vagueness suite, checking whether each issue is still present or has been fixed.

**Deliverable:** A document `REVERIFICATION_REPORT_H8.md` in `docs/provenance/` that is audit-ready, thorough, and shows zero hallucination.

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

## CLAIMS TO VERIFY (Pre-Extracted)

### MAJOR Claims

#### MAJ-1: LaTeX Table Displays Key Coefficients as "0.0000"
- **Claim:** LaTeX table (`h8_political_risk_table.tex`) displays PRiskFY and interact coefficients as "0.0000" because they are O(1e-6) formatted with `.4f`
- **Source:** AUDIT_H8.md Finding #3, Paper_Artifacts_Audit_H8.md Finding #1
- **Expected Location:** `outputs/econometric/h8_political_risk/{timestamp}/h8_political_risk_table.tex`
- **Fix Verification:**
  1. Read the LaTeX table
  2. Check if PRiskFY and interact coefficients are displayed as "0.0000" or in scientific notation
  3. Check `run_h8_political_risk.py` for the formatting function

#### MAJ-2: Provenance Claims "Pooled" Winsorization; Code Uses Per-Year
- **Claim:** H8.md Section G claims "1/99% pooled" winsorization but code uses per-year winsorization
- **Source:** AUDIT_H8.md Finding #2, Paper_Artifacts_Audit_H8.md Finding #2
- **Expected Location:** `docs/provenance/H8.md` Section G (around line 227)
- **Fix Verification:**
  1. Read H8.md Section G
  2. Check if it says "pooled" or "per-year"

#### MAJ-3: Missing Reproducibility Artifacts
- **Claim:** Missing run_manifest.json, sample attrition table, variable lineage JSON
- **Source:** Paper_Artifacts_Audit_H8.md Finding #3
- **Expected Location:** `outputs/econometric/h8_political_risk/{timestamp}/run_manifest.json`
- **Fix Verification:** Search for these files in the output directories

### MINOR Claims

#### MIN-1: LaTeX Summary Stats Claims "Call Level"
- **Claim:** `summary_stats.tex` note says "call level" but H8 is firm-year level
- **Source:** Paper_Artifacts_Audit_H8.md Finding #4
- **Expected Location:** `outputs/econometric/h8_political_risk/{timestamp}/summary_stats.tex`
- **Fix Verification:**
  1. Read summary_stats.tex
  2. Check the table note for "call level" or "firm-year level"

#### MIN-2: Panel Includes Fiscal Years Outside Config Range
- **Claim:** Panel contains fyearq=2000 and fyearq=2019 outside the configured 2002-2018 range
- **Source:** AUDIT_H8.md Finding #4, Paper_Artifacts_Audit_H8.md Finding #5
- **Notes:** This is a documentation note, not a bug
- **Fix Verification:** Document status (acknowledged/unchanged)

#### MIN-3: style_frozen Absorbed by Firm FE for 84.5% of Firms
- **Claim:** Only 258/1,665 firms have within-firm variation in style_frozen; identification concern
- **Source:** AUDIT_H8.md Finding #1, Paper_Artifacts_Audit_H8.md Finding #6
- **Notes:** This is an identification concern, not a bug
- **Fix Verification:** Check if documented in provenance Known Issues

### NOTE Claims

#### NOT-1: LaTeX Table Missing SE Cluster Documentation
- **Claim:** LaTeX table does not document that SEs are clustered at firm level
- **Source:** Paper_Artifacts_Audit_H8.md Finding #7
- **Expected Location:** `h8_political_risk_table.tex`
- **Fix Verification:** Check if tablenotes section exists with SE clustering info

#### NOT-2: aggregate_to_firm_year Uses .last() Without Explicit skipna
- **Claim:** Latent fragility - `.last()` behavior varies across pandas versions
- **Source:** AUDIT_H8.md Finding #7
- **Expected Location:** `build_h8_political_risk_panel.py` around line 103
- **Fix Verification:** Check if code has explicit skipna or comment

---

## VERIFICATION COMMANDS REFERENCE

Use these targeted commands:

### LaTeX Table Verification
```bash
# Check LaTeX table for 0.0000 vs scientific notation
cat outputs/econometric/h8_political_risk/LATEST/h8_political_risk_table.tex

# Check formatting function in code
grep -n "fmt_coef\|:.4f\|:.2e" src/f1d/econometric/run_h8_political_risk.py
```

### Provenance Documentation
```bash
# Check winsorization claim in H8.md
grep -n -i "pooled\|per-year" docs/provenance/H8.md

# Read Section G
sed -n '220,235p' docs/provenance/H8.md
```

### Missing Artifacts
```bash
# Check for run_manifest.json
find outputs/econometric/h8_political_risk -name "run_manifest.json" -type f

# Check for attrition files
find outputs -name "*attrition*" -path "*h8*" -type f
```

### Summary Stats Level
```bash
# Check summary_stats.tex table note
grep -n "call level\|firm-year" outputs/econometric/h8_political_risk/LATEST/summary_stats.tex
```

### Diagnostics
```bash
# Check model diagnostics
python -c "
import pandas as pd
from pathlib import Path
out_dirs = sorted(Path('outputs/econometric/h8_political_risk').iterdir())
latest = out_dirs[-1]
diag = pd.read_csv(latest / 'model_diagnostics.csv')
print(f'Diagnostics rows: {len(diag)}')
print(f'Columns: {list(diag.columns)}')
print(diag[['spec', 'n_obs', 'n_firms', 'within_r2']].to_string())
"
```

---

## OUTPUT FORMAT

Your final deliverable must be written to:
```
docs/provenance/REVERIFICATION_REPORT_H8.md
```

### Required Structure

```markdown
# H8 Political Risk × CEO Speech Vagueness — Reverification Report

**Verification Date:** YYYY-MM-DD
**Verifier:** AI Auditor
**Scope:** All claims from AUDIT_H8.md and Paper_Artifacts_Audit_H8.md

---

## 1. Executive Summary

| Metric | Count |
|--------|-------|
| Total Claims Verified | X |
| Claims Fixed | X |
| Claims Still Present | X |
| Claims Invalid | X |
| Claims Partially Fixed | X |

### Paper-Submission Readiness Verdict
**READY / NOT READY** — [Brief justification]

### Top Outstanding Issues
1. [Most critical issue]
2. [Second most critical]
3. [Third most critical]

---

## 2. Claim Ledger (Full)

| ID | Severity | Claim | Verdict | Evidence |
|----|----------|-------|---------|----------|
| MAJ-1 | MAJOR | LaTeX displays 0.0000 | FIXED/STILL PRESENT | [Link] |
| ... | ... | ... | ... | ... |

---

## 3. Detailed Verification Results

[For each claim, provide before/after evidence and verdict]

---

## 4. Recommendations

### Immediate Actions Required
1. [Action 1]

### Optional Improvements
1. [Improvement 1]

---

*Verification complete. All claims examined individually.*
```

---

## FINAL INSTRUCTION

Begin by reading the three source documents to understand the claims. Then proceed to verify each claim one by one. Write your final report to `docs/provenance/REVERIFICATION_REPORT_H8.md`.
