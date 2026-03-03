# Audit Re-Verification Prompt: Suite H7 (Stock Illiquidity)

**Purpose:** This prompt instructs an AI auditor to re-verify all claimed issues from prior audits against the current codebase and output artifacts.

**Target Suite:** H7 — Speech Vagueness and Stock Illiquidity (Amihud 2002)
**Input Documents:**
- `docs/provenance/H7.md` (Provenance documentation)
- `docs/provenance/AUDIT_H7.md` (Initial adversarial audit)
- `docs/provenance/Paper_Artifacts_Audit_H7.md` (Paper-submission readiness audit)

**Output Deliverable:** `docs/provenance/AUDIT_REVERIFICATION_H7.md`

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
| **Line numbers** | Specific lines read (e.g., "lines 67-129") |
| **Command executed** | Literal command with all flags |
| **Raw output** | Exact output received (truncate if long, but show key parts) |
| **Timestamp check** | Modification time of files (if relevant to "was this fixed?") |
| **Cross-reference** | At least 2 independent sources for critical claims |

---

## PART 2: CLAIM LEDGER EXTRACTION

Before auditing, extract a **Claim Ledger** from the three input documents. This is your source of truth for what needs verification.

### 2.1 Issue Register (Extract from AUDIT_H7.md)

| ID | Severity | Description | Claimed Fix | Status Claimed |
|----|----------|-------------|-------------|----------------|
| H7-AUDIT-MA1 | MAJOR | DV (`amihud_illiq_lead`) not re-winsorized, extreme skew (17.4) | Post-shift winsorization or log transform | DOCUMENTED (impact low since H7 not supported) |
| H7-AUDIT-M1 | MINOR | LaTeX uses mixed p-value bases (one-tailed for Manager, two-tailed for CEO) | Unify p-value basis | NOT FIXED |
| H7-AUDIT-M2 | MINOR | min_calls filter applied pre-listwise deletion, singletons exist | Apply filter post-deletion | NOT FIXED |
| H7-AUDIT-M3 | MINOR | Dead code path — Weak_Modal_Gap | Remove lines 143-147 | NOT FIXED |
| H7-AUDIT-N1 | NOTE | Utility sample low power (N=78 firms) | Relocate to appendix | DOCUMENTED |
| H7-AUDIT-N2 | NOTE | DV transformation should be considered | Add log transform robustness check | NOT IMPLEMENTED |

### 2.2 Issue Register (Extract from Paper_Artifacts_Audit_H7.md)

| ID | Severity | Description | Claimed Fix | Status Claimed |
|----|----------|-------------|-------------|----------------|
| H7-PAPER-MA1 | MAJOR | DV extreme skew not addressed (same as AUDIT-MA1) | Same as above | DOCUMENTED |
| H7-PAPER-M1 | MINOR | LaTeX table missing standard notes | Add tablenotes block | NOT FIXED |
| H7-PAPER-M2 | MINOR | Mixed p-value basis (duplicate of AUDIT-M1) | Same as above | NOT FIXED |
| H7-PAPER-M3 | MINOR | min_calls filter timing (duplicate of AUDIT-M2) | Same as above | NOT FIXED |
| H7-PAPER-N1 | NOTE | Missing run_manifest.json | Add manifest generation | NOT FIXED |
| H7-PAPER-N2 | NOTE | Utility sample low power (duplicate of AUDIT-N1) | Same as above | DOCUMENTED |

### 2.3 Consolidated Claim Ledger

| ID | Severity | Claim | Fix Location | Audit Status Claimed |
|----|----------|-------|--------------|---------------------|
| H7-001 | MAJOR | DV extreme skew (17.4) not addressed | `build_h7_illiquidity_panel.py:67-129` | DOCUMENTED (no fix required) |
| H7-002 | MINOR | LaTeX table missing notes | `run_h7_illiquidity.py` LaTeX generator | CLAIMS NOT FIXED |
| H7-003 | NOTE | Missing run_manifest.json | Stage 3 + Stage 4 outputs | CLAIMS NOT FIXED |
| H7-004 | MINOR | Mixed p-value basis for stars | `run_h7_illiquidity.py:296, 308` | CLAIMS NOT FIXED |
| H7-005 | MINOR | min_calls filter timing | `run_h7_illiquidity.py:449-450` | CLAIMS NOT FIXED |
| H7-006 | NOTE | Utility sample low power | N/A | DOCUMENTED |

---

## PART 3: VERIFICATION PROCEDURES (Execute One-by-One)

### 3.1 Verification of H7-001: DV Extreme Skew (DOCUMENTED)

**Background:** The DV `amihud_illiq_lead` has extreme right skew (skewness=17.4, kurtosis=378.2) because the lead-shifted values are NOT re-winsorized. The audits document this but do not require a fix since H7 is not supported (all β ≤ 0).

**Claimed Status:** Documented as known limitation; no fix required since hypothesis not supported.

#### Step 3.1.1: Verify DV Distribution

Execute EXACTLY:

```bash
python -c "
import pandas as pd
from pathlib import Path
from scipy import stats

panel_dir = Path('outputs/variables/h7_illiquidity')
subdirs = sorted([d for d in panel_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]
panel = pd.read_parquet(latest / 'h7_illiquidity_panel.parquet')

dv = panel['amihud_illiq_lead'].dropna()
print(f'Latest Stage 3 run: {latest.name}')
print(f'DV valid count: {len(dv):,}')
print(f'Mean: {dv.mean():.6f}')
print(f'Median: {dv.median():.6f}')
print(f'Mean/Median ratio: {dv.mean()/dv.median():.1f}x')
print(f'Skewness: {dv.skew():.2f}')
print(f'Kurtosis: {dv.kurtosis():.2f}')
print(f'Max: {dv.max():.6f}')
print(f'P99: {dv.quantile(0.99):.6f}')
print(f'Max/P99 ratio: {dv.max()/dv.quantile(0.99):.1f}x')
"
```

**Evidence to Record:**
- [ ] Skewness value (expected: ~17.4)
- [ ] Kurtosis value (expected: ~378)
- [ ] Mean/Median ratio (expected: ~18x)
- [ ] Max/P99 ratio (expected: ~9x)

#### Step 3.1.2: Check if DV Was Re-Winsorized

Execute EXACTLY:

```bash
# Check if any winsorization is applied after lead construction
grep -n "amihud_illiq_lead.*winsor\|winsor.*amihud_illiq_lead" src/f1d/variables/build_h7_illiquidity_panel.py

# Read the create_lead_variables function
grep -n "def create_lead\|winsorize" src/f1d/variables/build_h7_illiquidity_panel.py
```

**Evidence to Record:**
- [ ] Whether post-shift winsorization code exists
- [ ] Whether any DV transformation is applied

#### Step 3.1.3: Verdict for H7-001

- [ ] **CONFIRMED DOCUMENTED** — Skewness persists as documented, no fix applied
- [ ] **FIXED** — DV now winsorized or transformed (describe)
- [ ] **CHANGED** — Different approach taken (describe)

---

### 3.2 Verification of H7-002: LaTeX Table Missing Notes (CLAIMS NOT FIXED)

**Background:** The LaTeX table `h7_illiquidity_table.tex` has no table notes section explaining SE clustering, FE inclusion, or p-value convention.

**Claimed Status:** Not fixed.

#### Step 3.2.1: Read LaTeX Table

Execute EXACTLY:

```bash
# Find latest Stage 4 output
ls -lt outputs/econometric/h7_illiquidity/ | head -5

# Read the LaTeX table
cat outputs/econometric/h7_illiquidity/*/h7_illiquidity_table.tex

# Check for tablenotes or notes section
grep -n "tablenotes\|Notes\|Standard errors\|clustered\|one-tailed" outputs/econometric/h7_illiquidity/*/h7_illiquidity_table.tex
```

**Evidence to Record:**
- [ ] Full content of LaTeX table (especially bottom section)
- [ ] Whether table notes section exists
- [ ] Whether SE clustering is documented
- [ ] Whether p-value convention is documented

#### Step 3.2.2: Verdict for H7-002

- [ ] **CONFIRMED NOT FIXED** — No table notes present
- [ ] **FIXED** — Table notes now present (show evidence)

---

### 3.3 Verification of H7-003: Missing Run Manifest (CLAIMS NOT FIXED)

**Background:** No `run_manifest.json` exists in Stage 3 or Stage 4 outputs.

**Claimed Status:** Not fixed.

#### Step 3.3.1: Check Current State

Execute EXACTLY:

```bash
# Check if run_manifest.json exists in ANY H7 output
find outputs/variables/h7_illiquidity -name "run_manifest.json" -type f 2>/dev/null
find outputs/econometric/h7_illiquidity -name "run_manifest.json" -type f 2>/dev/null

# List contents of latest Stage 3 run
ls -la outputs/variables/h7_illiquidity/*/

# List contents of latest Stage 4 run
ls -la outputs/econometric/h7_illiquidity/*/
```

**Evidence to Record:**
- [ ] Whether `run_manifest.json` exists in Stage 3 outputs
- [ ] Whether `run_manifest.json` exists in Stage 4 outputs
- [ ] Files present in each output directory

#### Step 3.3.2: Verdict for H7-003

- [ ] **CONFIRMED NOT FIXED** — No manifest exists
- [ ] **FIXED** — Manifest now exists (show evidence)

---

### 3.4 Verification of H7-004: Mixed P-Value Basis (CLAIMS NOT FIXED)

**Background:** Manager IV uses one-tailed p-values for stars (`beta1_p_one`), CEO IV uses two-tailed (`beta2_p_two`).

**Claimed Status:** Not fixed.

#### Step 3.4.1: Check Code Implementation

Execute EXACTLY:

```bash
# Read the LaTeX table generation code
grep -n "fmt_coef\|beta1_p_one\|beta2_p_two" src/f1d/econometric/run_h7_illiquidity.py
```

**Evidence to Record:**
- [ ] Line number for Manager IV star assignment
- [ ] Which p-value is used for Manager IV
- [ ] Line number for CEO IV star assignment
- [ ] Which p-value is used for CEO IV

#### Step 3.4.2: Verdict for H7-004

- [ ] **CONFIRMED NOT FIXED** — Mixed p-value basis persists
- [ ] **FIXED** — Unified p-value basis (describe)

---

### 3.5 Verification of H7-005: Min_Calls Filter Timing (CLAIMS NOT FIXED)

**Background:** The `min_calls >= 5` filter is applied BEFORE listwise deletion, leaving singletons in regression.

**Claimed Status:** Not fixed.

#### Step 3.5.1: Check Code Implementation

Execute EXACTLY:

```bash
# Find the min_calls filter code
grep -n "min_calls\|MIN_CALLS\|transform.*count" src/f1d/econometric/run_h7_illiquidity.py | head -20

# Read the specific lines (around 449-450)
head -460 src/f1d/econometric/run_h7_illiquidity.py | tail -30
```

**Evidence to Record:**
- [ ] Line number where min_calls filter is applied
- [ ] Whether filter is before or after dropna
- [ ] Whether post-deletion check exists

#### Step 3.5.2: Check for Singletons

Execute EXACTLY:

```bash
python -c "
import pandas as pd
from pathlib import Path

# Load diagnostics
econ_dir = Path('outputs/econometric/h7_illiquidity')
subdirs = sorted([d for d in econ_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]
diag = pd.read_csv(latest / 'model_diagnostics.csv')

# Check Utility sample for singleton indication
util = diag[diag['sample'] == 'Utility']
print('Utility sample diagnostics:')
for _, r in util.iterrows():
    print(f\"  {r['spec_name']}: n_obs={r['n_obs']}, n_firms={r['n_firms']}\")
"
```

**Evidence to Record:**
- [ ] Whether singletons still exist in Utility sample
- [ ] N_obs / n_firms ratio for Utility

#### Step 3.5.3: Verdict for H7-005

- [ ] **CONFIRMED NOT FIXED** — Filter timing unchanged
- [ ] **FIXED** — Filter now applied post-deletion

---

### 3.6 Verification of H7-006: Utility Sample Low Power (DOCUMENTED)

**Background:** Utility sample has only 78 firms, low statistical power.

**Claimed Status:** Documented as known limitation.

#### Step 3.6.1: Verify Current State

Execute EXACTLY:

```bash
python -c "
import pandas as pd
from pathlib import Path

# Load diagnostics
econ_dir = Path('outputs/econometric/h7_illiquidity')
subdirs = sorted([d for d in econ_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]
diag = pd.read_csv(latest / 'model_diagnostics.csv')

# Summary by sample
for sample in ['Main', 'Finance', 'Utility']:
    sample_diag = diag[diag['sample'] == sample]
    print(f'{sample}:')
    print(f\"  N_obs range: {sample_diag['n_obs'].min():,} - {sample_diag['n_obs'].max():,}\")
    print(f\"  N_firms: {sample_diag['n_firms'].iloc[0]:,}\")
    print(f\"  Within-R2 range: {sample_diag['within_r2'].min():.4f} - {sample_diag['within_r2'].max():.4f}\")
    print()
"
```

**Evidence to Record:**
- [ ] Utility sample n_firms count
- [ ] Utility sample n_obs range
- [ ] Comparison to Main sample

#### Step 3.6.2: Verdict for H7-006

- [ ] **CONFIRMED DOCUMENTED** — Low power persists, documented
- [ ] **CHANGED** — Sample merged or excluded (describe)

---

## PART 4: ADDITIONAL ADVERSARIAL CHECKS

### 4.1 Check for New Regressions

```bash
# Compare file modification times to audit dates
# AUDIT_H7.md was dated 2026-02-28
# Paper_Artifacts_Audit_H7.md was dated 2026-03-01

git log --oneline --since="2026-02-28" -- src/f1d/econometric/run_h7_illiquidity.py
git log --oneline --since="2026-02-28" -- src/f1d/variables/build_h7_illiquidity_panel.py
```

### 4.2 Cross-Artifact Consistency Deep Dive

Pick Main / QA_Uncertainty regression and verify:

| Source | Field | Expected Value | Actual Value | Match? |
|--------|-------|----------------|--------------|--------|
| Raw .txt | beta1 (Manager) | ≈ -0.0037 | — | — |
| model_diagnostics.csv | beta1 | — | — | — |
| LaTeX table | Manager IV coef | — | — | — |
| Raw .txt | N | 54,170 | — | — |
| model_diagnostics.csv | n_obs | — | — | — |
| LaTeX table | N | — | — | — |
| Raw .txt | Within-R² | ≈ 0.0077 | — | — |
| model_diagnostics.csv | within_r2 | — | — | — |
| LaTeX table | R² | — | — | — |

### 4.3 Hypothesis Results Verification

```bash
python -c "
import pandas as pd
from pathlib import Path

econ_dir = Path('outputs/econometric/h7_illiquidity')
subdirs = sorted([d for d in econ_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]
diag = pd.read_csv(latest / 'model_diagnostics.csv')

# Count H7 supported
supported = diag['h7_sig'].sum()
negative_betas = (diag['beta1'] < 0).sum()

print(f'Total specs: {len(diag)}')
print(f'H7 supported (h7_sig=True): {supported}')
print(f'Negative beta1 coefficients: {negative_betas}')
print()
print('Expected: 0/9 supported, all beta1 ≤ 0 (H7 NOT SUPPORTED)')
print()

# Show all beta1 values
print('All beta1 values:')
for _, r in diag.iterrows():
    sig = '*' if r['h7_sig'] else ''
    print(f\"  {r['sample'][:7]:7} {r['spec_name'][:15]:15}: beta1={r['beta1']:.6f}{sig}\")
"
```

### 4.4 Panel Data Verification

```bash
python -c "
import pandas as pd
from pathlib import Path

panel_dir = Path('outputs/variables/h7_illiquidity')
subdirs = sorted([d for d in panel_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]
panel = pd.read_parquet(latest / 'h7_illiquidity_panel.parquet')

print(f'Total rows: {len(panel):,}')
print(f'Columns: {len(panel.columns)}')
print(f'file_name unique: {panel[\"file_name\"].is_unique}')
print()
print('Sample distribution:')
print(panel['sample'].value_counts())
print()
print('DV coverage:')
valid = panel['amihud_illiq_lead'].notna().sum()
print(f'  Valid: {valid:,} ({100*valid/len(panel):.1f}%)')
"
```

**Expected values:**
- Total rows: 112,968
- Columns: 24
- Sample distribution: Main=88,205, Finance=20,482, Utility=4,281
- DV coverage: ~88.6%

---

## PART 5: OUTPUT FORMAT

Your output document must be written to:
`docs/provenance/AUDIT_REVERIFICATION_H7.md`

### Required Sections

```markdown
# Re-Verification Audit Report: Suite H7

**Date:** [TODAY'S DATE]
**Auditor:** [AI Model + Version]
**Input Documents:** H7.md, AUDIT_H7.md, Paper_Artifacts_Audit_H7.md
**Verification Method:** Manual one-by-one inspection per AUDIT_REVERIFICATION_PROMPT_H7.md

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

### H7-001: DV Extreme Skew
**Claimed Status:** DOCUMENTED
**Verification Steps:** [List steps performed]
**Evidence:**
- [Exact commands and outputs]
**Verdict:** [CONFIRMED DOCUMENTED / FIXED / etc.]
**Rationale:** [1-2 sentences]

### H7-002: LaTeX Table Missing Notes
[Same format]

### H7-003: Missing Run Manifest
[Same format]

### H7-004: Mixed P-Value Basis
[Same format]

### H7-005: Min_Calls Filter Timing
[Same format]

### H7-006: Utility Sample Low Power
[Same format]

---

## Additional Findings

[List any new issues discovered during verification]

---

## Cross-Artifact Consistency Matrix

[Table from 4.2]

---

## Hypothesis Results Verification

[Expected vs actual results]

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
- [ ] My output document is saved to `docs/provenance/AUDIT_REVERIFICATION_H7.md`

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

## PART 7: SPECIAL VERIFICATION NOTES FOR H7

### H7-Specific: Amihud Illiquidity Measure

The H7 suite uses the Amihud (2002) illiquidity measure:
- Formula: `mean(|RET| / dollar_volume) × 10^6`
- Computed over inter-call window `[prev_call+5d, call-5d]`
- Lead construction: shifted forward 1 fiscal year

```bash
# Verify Amihud computation
grep -n "amihud\|dollar_volume\|RET.abs" src/f1d/shared/variables/_crsp_engine.py | head -30
```

### H7-Specific: Two IV Types (Manager and CEO)

H7 includes both Manager and CEO uncertainty variables:
- Manager variables: primary hypothesis tests (one-tailed p-values)
- CEO variables: secondary tests (two-tailed p-values per current implementation)

```bash
# Verify both IV types in diagnostics
python -c "
import pandas as pd
from pathlib import Path
econ_dir = Path('outputs/econometric/h7_illiquidity')
subdirs = sorted([d for d in econ_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]
diag = pd.read_csv(latest / 'model_diagnostics.csv')
print(diag[['spec_name', 'iv_var', 'second_iv']].to_string())
"
```

### H7-Specific: Hypothesis Direction

H7 hypothesis: β₁ > 0 (higher vagueness → higher illiquidity).
All 9 coefficients should be checked for sign and significance.

---

END OF PROMPT
