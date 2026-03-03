# Audit Re-Verification Prompt: Suite H5 (Analyst Dispersion)

**Purpose:** This prompt instructs an AI auditor to re-verify all claimed issues from prior audits against the current codebase and output artifacts.

**Target Suite:** H5 — Speech Uncertainty and Analyst Forecast Dispersion
**Input Documents:**
- `docs/provenance/H5.md` (Provenance documentation)
- `docs/provenance/AUDIT_H5.md` (Initial adversarial audit)
- `docs/provenance/Paper_Artifacts_Audit_H5.md` (Paper-submission readiness audit)

**Output Deliverable:** `docs/provenance/AUDIT_REVERIFICATION_H5.md`

---

## PART 1: AUDITOR INSTRUCTIONS

### 1.0 Meta-Instructions (READ CAREFULLY)

You are an **adversarial code auditor**. Your job is to:
1. **Distrust everything** — verify every claim yourself
2. **Never assume** — read actual files, run actual commands
3. **Never bulk-process** — examine each issue individually, one at a time
4. **Never hallucinate** — if you cannot verify something, state "UNVERIFIED" with reason
5. **Be exhaustive** — check every line, every value, every assertion

### 1.1 What "Manually One-by-One" Means

You are **FORBIDDEN** from:
- Running a single grep across all files and declaring "done"
- Using `rg` or `grep` with wildcards to check multiple issues simultaneously
- Assuming that because one artifact is correct, all are correct
- Skipping verification because "the audit said so"

You **MUST**:
- For EACH issue: open the specific file, read the specific lines, run the specific command
- Document the EXACT command you ran and the EXACT output you received
- If a file has been modified, note the modification date and compare to audit dates
- Cross-reference multiple sources for each claim (e.g., code + output file + LaTeX table)

### 1.2 Evidence Standards

For each issue, your verification MUST include:

| Evidence Type | Required |
|--------------|----------|
| **File path** | Exact path to file examined |
| **Line numbers** | Specific lines read (e.g., "lines 353-357") |
| **Command executed** | Literal command with all flags |
| **Raw output** | Exact output received (truncate if long, but show key parts) |
| **Timestamp check** | Modification time of files (if relevant to "was this fixed?") |
| **Cross-reference** | At least 2 independent sources for critical claims |

---

## PART 2: CLAIM LEDGER EXTRACTION

Before auditing, extract a **Claim Ledger** from the three input documents. This is your source of truth for what needs verification.

### 2.1 Issue Register (Extract from AUDIT_H5.md)

| ID | Severity | Description | Claimed Fix | Status Claimed |
|----|----------|-------------|-------------|----------------|
| H5-AUDIT-MA1 | MAJOR | LaTeX Within-R² is blank (custom computation returns NaN) | Use `rsquared` instead of `within_r2` in LaTeX generator | Paper audit says WITHIN-R² NOW POPULATED |
| H5-AUDIT-MA2 | MAJOR | LaTeX stars use one-tailed p-values without documentation | Add clear footnote about one-tailed tests | NOT FIXED |
| H5-AUDIT-M1 | MINOR | prior_dispersion backward merge has no tolerance | Add tolerance parameter | DOCUMENTED ONLY |
| H5-AUDIT-M2 | MINOR | Custom within-R² computation is dead code | Remove lines 199-224 | RELATED TO MA1 |
| H5-AUDIT-m1 | NOTE | loss_dummy.py docstring says "niq" but code uses "ibq" | Fix docstring | NOT FIXED |
| H5-AUDIT-m2 | NOTE | earnings_volatility provenance says "quarterly" but code uses annual | Update provenance | NOT FIXED |
| H5-AUDIT-m3 | NOTE | CEO variables built into panel but not used | Either remove or include in summary stats | NOT FIXED |

### 2.2 Issue Register (Extract from Paper_Artifacts_Audit_H5.md)

| ID | Severity | Description | Claimed Fix | Status Claimed |
|----|----------|-------------|-------------|----------------|
| H5-PAPER-B1 | BLOCKER | No run_manifest.json in Stage 4 outputs | Add manifest generation | NOT FIXED |
| H5-PAPER-B2 | BLOCKER | No sample attrition table | Generate attrition table | NOT FIXED |
| H5-PAPER-B3 | BLOCKER | Stage 4 panel path not logged | Log panel path in manifest | NOT FIXED |
| H5-PAPER-M1 | MAJOR | Variable dictionary missing machine-readable lineage | Generate lineage JSON | NOT FIXED |
| H5-PAPER-m1 | MINOR | Report Step 3 minimal content | Enhance report | NOT FIXED |
| H5-PAPER-m2 | MINOR | Summary stats missing CEO variables | Fix or remove CEO vars | NOT FIXED |

### 2.3 Consolidated Claim Ledger

| ID | Severity | Claim | Fix Location | Audit Status Claimed |
|----|----------|-------|--------------|---------------------|
| H5-001 | ~~MAJOR~~ | LaTeX Within-R² blank | `run_h5_dispersion.py` lines 353-357 | CLAIMS FIXED |
| H5-002 | MAJOR | LaTeX stars one-tailed undocumented | Table footnote or code | CLAIMS NOT FIXED |
| H5-003 | BLOCKER | Missing run_manifest.json | Stage 3 + Stage 4 outputs | CLAIMS NOT FIXED |
| H5-004 | BLOCKER | Missing sample attrition table | Stage 4 output | CLAIMS NOT FIXED |
| H5-005 | MINOR | prior_dispersion backward merge no tolerance | `prior_dispersion.py` | DOCUMENTED |
| H5-006 | NOTE | loss_dummy docstring wrong | `loss_dummy.py` | CLAIMS NOT FIXED |

---

## PART 3: VERIFICATION PROCEDURES (Execute One-by-One)

### 3.1 Verification of H5-001: Within-R² Blank in LaTeX (CLAIMS FIXED)

**Background:** The initial audit found that LaTeX table Within-R² row was blank because `within_r2` (custom computation) returned NaN. The fix should use `rsquared` (PanelOLS's rsquared_within) instead.

**Claimed Fix:** LaTeX table now correctly reports Within-R² values (0.3079, 0.1637, etc.).

#### Step 3.1.1: Verify LaTeX Table

Execute EXACTLY:

```bash
# Step A: Find latest Stage 4 output
ls -lt outputs/econometric/h5_dispersion/ | head -5

# Step B: Read the LaTeX table and extract Within-R² row
grep -n "Within-R\|Within-\$R" outputs/econometric/h5_dispersion/*/h5_dispersion_table.tex

# Step C: Read the full LaTeX table line 20 (or wherever Within-R² appears)
# Look for actual values vs blank cells
head -25 outputs/econometric/h5_dispersion/*/h5_dispersion_table.tex
```

**Evidence to Record:**
- [ ] Exact Within-R² row content from LaTeX table
- [ ] Whether values are populated or blank
- [ ] Values for Model A (Lagged DV) and Model B (Lagged DV)

#### Step 3.1.2: Verify model_diagnostics.csv

Execute EXACTLY:

```bash
python -c "
import pandas as pd
from pathlib import Path

econ_dir = Path('outputs/econometric/h5_dispersion')
subdirs = sorted([d for d in econ_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]
diag = pd.read_csv(latest / 'model_diagnostics.csv')

print(f'Latest run: {latest.name}')
print(f'Columns: {list(diag.columns)}')
print()

# Check within_r2 and rsquared columns
for _, r in diag.iterrows():
    within = r.get('within_r2', 'N/A')
    rsq = r.get('rsquared', 'N/A')
    print(f\"{r['spec_name'][:20]:20} ({r['sample'][:5]:5}): within_r2={within}, rsquared={rsq}\")
"
```

**Evidence to Record:**
- [ ] Values in `within_r2` column (NaN or populated?)
- [ ] Values in `rsquared` column
- [ ] Which column the LaTeX table uses

#### Step 3.1.3: Verify Code Implementation

Execute EXACTLY:

```bash
# Search for Within-R² usage in LaTeX generator
grep -n "within_r2\|rsquared" src/f1d/econometric/run_h5_dispersion.py | head -30

# Read the specific lines where LaTeX table is generated
# Look for fmt_r2() calls and which field they use
```

**Evidence to Record:**
- [ ] Exact code for R² row in LaTeX generator
- [ ] Whether `within_r2` or `rsquared` is used
- [ ] Whether custom within-R² computation block still exists

#### Step 3.1.4: Cross-Check Values

Execute EXACTLY:

```bash
python -c "
import pandas as pd
from pathlib import Path

# Get latest diagnostics
econ_dir = Path('outputs/econometric/h5_dispersion')
subdirs = sorted([d for d in econ_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]
diag = pd.read_csv(latest / 'model_diagnostics.csv')

# Get Main sample, Model A and B (Lagged DV)
main_lag = diag[(diag['sample'] == 'Main') & (diag['spec_name'].str.contains('Lagged'))]
print('Main Sample, Lagged DV specs:')
for _, r in main_lag.iterrows():
    print(f\"  {r['spec_name']}: rsquared={r['rsquared']:.4f}, within_r2={r.get('within_r2', 'NaN')}\")
"
```

**Expected values (per provenance H5.md §I.4):**
- Model A (Lagged DV): R² ≈ 0.308
- Model B (Lagged DV): R² ≈ 0.308

#### Step 3.1.5: Verdict for H5-001

- [ ] **CONFIRMED FIXED** — LaTeX reports Within-R² values matching PanelOLS
- [ ] **PARTIALLY FIXED** — Code changed but outputs not regenerated
- [ ] **NOT FIXED** — LaTeX Within-R² still blank
- [ ] **REGRESSION** — Was fixed but broken again
- [ ] **UNVERIFIABLE** — Cannot determine (explain why)

---

### 3.2 Verification of H5-002: One-Tailed P-values Undocumented (CLAIMS NOT FIXED)

**Background:** LaTeX table shows significance stars based on ONE-TAILED p-values, but this is not clearly documented in the table footnote.

**Claimed Status:** Not fixed.

#### Step 3.2.1: Read LaTeX Table Footnotes

Execute EXACTLY:

```bash
# Read the table notes section
grep -n "p<\|p\$<\|one-tail\|one-tailed\|One-tail" outputs/econometric/h5_dispersion/*/h5_dispersion_table.tex

# Alternative: read lines 20-30 which typically contain footnotes
tail -20 outputs/econometric/h5_dispersion/*/h5_dispersion_table.tex
```

**Evidence to Record:**
- [ ] Exact footnote text about p-values
- [ ] Whether "one-tailed" is mentioned
- [ ] Whether the footnote is clear enough for readers

#### Step 3.2.2: Verify Code Implementation

Execute EXACTLY:

```bash
# Check what p-value is used for stars
grep -n "beta1_p_one\|beta1_p_two\|fmt_coef" src/f1d/econometric/run_h5_dispersion.py | head -20
```

**Evidence to Record:**
- [ ] Which p-value is passed to `fmt_coef()` for star assignment
- [ ] Whether one-tailed or two-tailed p-values are used

#### Step 3.2.3: Verdict for H5-002

- [ ] **CONFIRMED NOT FIXED** — Footnote does not clearly document one-tailed test
- [ ] **FIXED** — Footnote now clearly states one-tailed p-values used
- [ ] **N/A** — Different approach taken (describe)

---

### 3.3 Verification of H5-003: Missing Run Manifest (CLAIMS NOT FIXED)

**Background:** No `run_manifest.json` exists in Stage 3 or Stage 4 outputs.

**Claimed Status:** Not fixed.

#### Step 3.3.1: Check Current State

Execute EXACTLY:

```bash
# Check if run_manifest.json exists in ANY H5 output
find outputs/variables/h5_dispersion -name "run_manifest.json" -type f 2>/dev/null
find outputs/econometric/h5_dispersion -name "run_manifest.json" -type f 2>/dev/null

# List contents of latest Stage 3 run
ls -la outputs/variables/h5_dispersion/*/

# List contents of latest Stage 4 run
ls -la outputs/econometric/h5_dispersion/*/
```

**Evidence to Record:**
- [ ] Whether `run_manifest.json` exists in Stage 3 outputs
- [ ] Whether `run_manifest.json` exists in Stage 4 outputs
- [ ] Files present in each output directory

#### Step 3.3.2: Check if Code Generates Manifest

Execute EXACTLY:

```bash
# Search for manifest generation code in H5 scripts
grep -n "run_manifest\|manifest" src/f1d/variables/build_h5_dispersion_panel.py
grep -n "run_manifest\|manifest" src/f1d/econometric/run_h5_dispersion.py
```

**Evidence to Record:**
- [ ] Presence/absence of manifest generation code

#### Step 3.3.3: Verdict for H5-003

- [ ] **CONFIRMED NOT FIXED** — No manifest exists, no code to generate it
- [ ] **FIXED** — Manifest now exists (show evidence)
- [ ] **ALTERNATIVE IMPLEMENTED** — Different reproducibility mechanism (describe)

---

### 3.4 Verification of H5-004: Missing Sample Attrition Table (CLAIMS NOT FIXED)

**Background:** No explicit table documenting row count changes from manifest (N=112,968) to regression sample (N=60,506).

**Claimed Status:** Not fixed.

#### Step 3.4.1: Check for Attrition Table

Execute EXACTLY:

```bash
# Search for sample attrition table in H5 outputs
find outputs/variables/h5_dispersion -name "*attrition*" -type f 2>/dev/null
find outputs/econometric/h5_dispersion -name "*attrition*" -type f 2>/dev/null

# Check Stage 3 report for attrition documentation
ls outputs/variables/h5_dispersion/*/report_step3_h5.md
head -50 outputs/variables/h5_dispersion/*/report_step3_h5.md
```

**Evidence to Record:**
- [ ] Whether `sample_attrition.csv` or `sample_attrition.tex` exists
- [ ] Whether attrition is documented in Stage 3 report
- [ ] Expected attrition: 112,968 → 85,107 (valid DV) → 60,506 (regression)

#### Step 3.4.2: Verdict for H5-004

- [ ] **CONFIRMED NOT FIXED** — No standalone attrition table
- [ ] **FIXED** — Attrition table now generated (show evidence)
- [ ] **ALTERNATIVE** — Attrition documented differently (describe)

---

### 3.5 Verification of H5-005: Backward Merge No Tolerance (DOCUMENTED)

**Background:** `prior_dispersion` and `earnings_surprise_ratio` use backward merge_asof with NO tolerance, potentially matching stale data.

**Claimed Status:** Documented as known limitation.

#### Step 3.5.1: Check Code Implementation

Execute EXACTLY:

```bash
# Check prior_dispersion merge implementation
grep -n "merge_asof\|tolerance" src/f1d/shared/variables/prior_dispersion.py

# Check earnings_surprise_ratio merge implementation
grep -n "merge_asof\|tolerance" src/f1d/shared/variables/earnings_surprise_ratio.py
```

**Evidence to Record:**
- [ ] Whether tolerance parameter is present
- [ ] If so, what is the value

#### Step 3.5.2: Verdict for H5-005

- [ ] **CONFIRMED DOCUMENTED** — No tolerance, documented as known limitation
- [ ] **FIXED** — Tolerance parameter added
- [ ] **CHANGED** — Different behavior (describe)

---

### 3.6 Verification of H5-006: Docstring Mismatch (CLAIMS NOT FIXED)

**Background:** `loss_dummy.py` docstring says "1 if niq < 0" but code uses "ibq".

**Claimed Status:** Not fixed.

#### Step 3.6.1: Check Docstring

Execute EXACTLY:

```bash
# Read the docstring and code for loss_dummy
head -50 src/f1d/shared/variables/loss_dummy.py
```

**Evidence to Record:**
- [ ] Exact docstring text
- [ ] Exact code implementation
- [ ] Whether they match

#### Step 3.6.2: Verdict for H5-006

- [ ] **CONFIRMED NOT FIXED** — Docstring still says "niq"
- [ ] **FIXED** — Docstring now says "ibq"

---

## PART 4: ADDITIONAL ADVERSARIAL CHECKS

### 4.1 Check for New Regressions

```bash
# Compare file modification times to audit dates
# Initial audit was 2026-02-28
# Paper audit was 2026-03-01

git log --oneline --since="2026-02-28" -- src/f1d/econometric/run_h5_dispersion.py
git log --oneline --since="2026-02-28" -- src/f1d/variables/build_h5_dispersion_panel.py
```

### 4.2 Cross-Artifact Consistency Deep Dive

Pick Main Model A (Lagged DV) and verify:

| Source | Field | Expected Value | Actual Value | Match? |
|--------|-------|----------------|--------------|--------|
| Raw .txt | beta1 | ≈ -0.0153 | — | — |
| model_diagnostics.csv | beta1 | — | — | — |
| LaTeX table | beta1 coef | — | — | — |
| Raw .txt | N | 60,506 | — | — |
| model_diagnostics.csv | n_obs | — | — | — |
| LaTeX table | N | — | — | — |
| Raw .txt | R² (Within) | ≈ 0.308 | — | — |
| model_diagnostics.csv | rsquared | — | — | — |
| LaTeX table | Within-R² | — | — | — |

### 4.3 Hypothesis Results Verification

```bash
python -c "
import pandas as pd
from pathlib import Path

econ_dir = Path('outputs/econometric/h5_dispersion')
subdirs = sorted([d for d in econ_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]
diag = pd.read_csv(latest / 'model_diagnostics.csv')

# Count significant results at p<0.05 one-tailed
sig_count = (diag['beta1_p_one'] < 0.05).sum()
marginal_count = ((diag['beta1_p_one'] >= 0.05) & (diag['beta1_p_one'] < 0.10)).sum()

print(f'Total specs: {len(diag)}')
print(f'Significant at p<0.05 (one-tailed): {sig_count}')
print(f'Marginal at p<0.10 (one-tailed): {marginal_count}')
print()
print('Expected: 0/12 significant (H5 NOT SUPPORTED)')
"
```

### 4.4 Panel Data Verification

```bash
python -c "
import pandas as pd
from pathlib import Path

panel_dir = Path('outputs/variables/h5_dispersion')
subdirs = sorted([d for d in panel_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]
panel = pd.read_parquet(latest / 'h5_dispersion_panel.parquet')

print(f'Total rows: {len(panel):,}')
print(f'Columns: {len(panel.columns)}')
print(f'file_name unique: {panel[\"file_name\"].is_unique}')
print()
print('Sample distribution:')
print(panel['sample'].value_counts())
print()
print('dispersion_lead coverage:')
valid = panel['dispersion_lead'].notna().sum()
print(f'  Valid: {valid:,} ({100*valid/len(panel):.1f}%)')
"
```

**Expected values:**
- Total rows: 112,968
- Columns: 24
- Sample distribution: Main=88,205, Finance=20,482, Utility=4,281
- dispersion_lead coverage: ~75%

---

## PART 5: OUTPUT FORMAT

Your output document must be written to:
`docs/provenance/AUDIT_REVERIFICATION_H5.md`

### Required Sections

```markdown
# Re-Verification Audit Report: Suite H5

**Date:** [TODAY'S DATE]
**Auditor:** [AI Model + Version]
**Input Documents:** H5.md, AUDIT_H5.md, Paper_Artifacts_Audit_H5.md
**Verification Method:** Manual one-by-one inspection per AUDIT_REVERIFICATION_PROMPT_H5.md

---

## Executive Summary

| Total Issues Verified | Confirmed Fixed | Confirmed Not Fixed | Documented/Accepted | Unverifiable |
|-----------------------|-----------------|---------------------|---------------------|--------------|
| X | Y | Z | A | B |

### Overall Assessment
[2-3 sentences on the state of the suite]

---

## Claim Ledger

[Copy from Part 2.3 with updated status]

---

## Verification Results

### H5-001: Within-R² Blank in LaTeX
**Claimed Status:** FIXED
**Verification Steps:** [List steps performed]
**Evidence:**
- [Exact commands and outputs]
**Verdict:** [CONFIRMED FIXED / NOT FIXED / etc.]
**Rationale:** [1-2 sentences]

### H5-002: One-Tailed P-values Undocumented
[Same format]

### H5-003: Missing Run Manifest
[Same format]

### H5-004: Missing Sample Attrition Table
[Same format]

### H5-005: Backward Merge No Tolerance
[Same format]

### H5-006: Docstring Mismatch
[Same format]

---

## Additional Findings

[List any new issues discovered during verification]

---

## Cross-Artifact Consistency Matrix

[Table from 4.2]

---

## Hypothesis Results Verification

[Expected vs actual significance counts]

---

## Recommendations

[Prioritized list of remaining actions]

---

## Command Log

[Complete list of every command executed with timestamps]

---

## Appendix: Raw Evidence

[Full outputs of key commands]
```

---

## PART 6: EXECUTION CHECKLIST

Before completing your audit, confirm:

- [ ] I have read the actual source code files, not just searched them
- [ ] I have executed Python commands against actual parquet files
- [ ] I have compared values across at least 3 sources (raw output, CSV, LaTeX)
- [ ] I have checked file modification dates against audit dates
- [ ] I have not assumed any claim is true without verification
- [ ] I have documented every command with its exact output
- [ ] I have noted "UNVERIFIABLE" where evidence is insufficient
- [ ] My output document is formatted per Part 5 requirements
- [ ] My output document is saved to `docs/provenance/AUDIT_REVERIFICATION_H5.md`

---

## ANTI-HALLUCINATION PROTOCOL

If you make any of the following statements, you MUST provide the exact evidence:

| Statement | Required Evidence |
|-----------|------------------|
| "The code uses X" | Exact line number and code snippet |
| "The output shows Y" | Exact command and output text |
| "File Z contains W" | Exact path and relevant excerpt |
| "Value is N" | Exact command to retrieve and exact output |
| "This was fixed" | Git diff, commit hash, or before/after code |
| "This is correct" | Cross-reference to at least 2 independent sources |

**FAILURE TO PROVIDE EVIDENCE = HALLUCINATION = AUDIT FAILURE**

---

## PART 7: SPECIAL VERIFICATION NOTES FOR H5

### H5-Specific: IBES Merge Logic

The H5 suite uses forward merge_asof for dispersion_lead (t+1 outcome) and backward merge_asof for prior_dispersion and earnings_surprise_ratio. Verify:

1. **dispersion_lead direction:** `direction="forward"` with `tolerance=pd.Timedelta(days=180)`
2. **prior_dispersion direction:** `direction="backward"` with NO tolerance
3. **Denominator protection:** IBES MEANEST must be ≥ 0.05

```bash
# Verify IBES merge logic
grep -n "direction\|tolerance\|MEANEST" src/f1d/shared/variables/dispersion_lead.py
grep -n "direction\|tolerance" src/f1d/shared/variables/prior_dispersion.py
```

### H5-Specific: Two Model Types

H5 tests two distinct model specifications:
- **Model A (Hedging):** Target = `Manager_QA_Weak_Modal_pct`, Base = `Manager_QA_Uncertainty_pct`
- **Model B (Gap):** Target = `Uncertainty_Gap` (computed), Base = `Manager_Pres_Uncertainty_pct`

Verify both models appear in output.

```bash
# Check for both models in diagnostics
python -c "
import pandas as pd
from pathlib import Path
econ_dir = Path('outputs/econometric/h5_dispersion')
subdirs = sorted([d for d in econ_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]
diag = pd.read_csv(latest / 'model_diagnostics.csv')
print(diag['spec_name'].unique())
"
```

### H5-Specific: H5 Hypothesis Direction

H5 hypothesis: β₁ > 0 (higher vagueness → higher dispersion). Note that Model A coefficients are NEGATIVE (opposite to hypothesis), which is why p_one ≈ 0.99 for wrong direction.

---

END OF PROMPT
