# Audit Re-Verification Prompt: Suite H2 (Investment Efficiency)

**Purpose:** This prompt instructs an AI auditor to re-verify all claimed issues from prior audits against the current codebase and output artifacts.

**Target Suite:** H2 — Speech Uncertainty and Investment Efficiency
**Input Documents:**
- `docs/provenance/H2.md` (Provenance documentation)
- `docs/provenance/AUDIT_H2.md` (Initial adversarial audit)
- `docs/provenance/Paper_Artifacts_Audit_H2.md` (Paper-submission readiness audit)

**Output Deliverable:** `docs/provenance/AUDIT_REVERIFICATION_H2.md`

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
| **Line numbers** | Specific lines read (e.g., "lines 371-407") |
| **Command executed** | Literal command with all flags |
| **Raw output** | Exact output received (truncate if long, but show key parts) |
| **Timestamp check** | Modification time of files (if relevant to "was this fixed?") |
| **Cross-reference** | At least 2 independent sources for critical claims |

---

## PART 2: CLAIM LEDGER EXTRACTION

Before auditing, extract a **Claim Ledger** from the three input documents. This is your source of truth for what needs verification.

### 2.1 Issue Register (Extract from AUDIT_H2.md)

| ID | Severity | Description | Claimed Fix | Status Claimed |
|----|----------|-------------|-------------|----------------|
| H2-AUDIT-F1 | MAJOR | LaTeX within-R² inflated via B8 custom computation | Use `rsquared` instead of `within_r2` in LaTeX generator | CLAIMED FIXED (per Paper_Artifacts_Audit) |
| H2-AUDIT-F2 | MAJOR | DV specification ambiguity (README says \|DV\|, code uses signed) | Update README to remove \|...\| notation | DOCUMENTED ONLY |
| H2-AUDIT-F3 | MINOR | 78 stale merge_asof matches (start_year - fyearq > 2) | Add tolerance parameter to attach_fyearq() | DOCUMENTED ONLY |
| H2-AUDIT-F4 | NOTE | Prior run N_obs drift between 2026-02-26 and 2026-02-27 | No fix needed (explained by filtering) | ACCEPTED |
| H2-AUDIT-F5 | NOTE | B8 custom within-R² is non-standard | Remove B8 block entirely | DOCUMENTED |

### 2.2 Issue Register (Extract from Paper_Artifacts_Audit_H2.md)

| ID | Severity | Description | Claimed Fix | Status Claimed |
|----|----------|-------------|-------------|----------------|
| H2-PAPER-F1 | MAJOR | README DV notation ambiguity | Remove \|...\| notation | NOT FIXED |
| H2-PAPER-F2 | MAJOR | No run_manifest.json in output directories | Add manifest generation to Stage 3/4 | NOT FIXED |
| H2-PAPER-F3 | MINOR | Stale merge_asof matches (duplicate of AUDIT-F3) | Same as above | DOCUMENTED |
| H2-PAPER-F4 | NOTE | Missing sample attrition table | Add generator function | NOT FIXED |
| H2-PAPER-F5 | NOTE | Missing figures (forest plots, distributions) | Optional enhancement | NOT IMPLEMENTED |

### 2.3 Consolidated Claim Ledger

| ID | Severity | Claim | Fix Location | Audit Status Claimed |
|----|----------|-------|--------------|---------------------|
| H2-001 | ~~MAJOR~~ | LaTeX within-R² inflated via B8 custom | `run_h2_investment.py` lines 613, 371-407 | CLAIMS FIXED |
| H2-002 | MAJOR | README DV notation ambiguous | `README.md` line 386 | CLAIMS NOT FIXED |
| H2-003 | MAJOR | Missing run_manifest.json | Stage 3 + Stage 4 output directories | CLAIMS NOT FIXED |
| H2-004 | MINOR | Stale merge_asof matches | `panel_utils.py` attach_fyearq() | DOCUMENTED (no fix needed) |
| H2-005 | NOTE | Missing sample attrition table | Stage 4 script | CLAIMS NOT FIXED |

---

## PART 3: VERIFICATION PROCEDURES (Execute One-by-One)

### 3.1 Verification of H2-001: Within-R² Inflation (CLAIMS FIXED)

**Background:** The initial audit found that LaTeX table reported within-R² values ~0.04 higher than PanelOLS's `rsquared_within`. The B8 custom computation (lines 371-407) was producing inflated values. Paper_Artifacts_Audit states this is FIXED.

**Claimed Fix:** LaTeX table now uses `rsquared` (PanelOLS's rsquared_within) instead of `within_r2` (B8 custom).

#### Step 3.1.1: Verify Code Implementation

Execute EXACTLY these commands in order:

```bash
# Step A: Find the current run_h2_investment.py file
find src -name "run_h2_investment.py" -type f 2>/dev/null

# Step B: Read lines 600-650 to examine the LaTeX table generator
# Look for:
#   - Whether within_r2 or rsquared is used in _save_latex_table
#   - The exact line where R² is extracted from meta dict

# Step C: Search for the B8 custom within_r2 block
grep -n "within_r2\|rsquared_within" src/f1d/econometric/run_h2_investment.py

# Step D: Check if B8 block still exists (lines 371-407)
# Read that specific section
```

**Evidence to Record:**
- [ ] Exact lines where within-R² is extracted for LaTeX table
- [ ] Whether `rsquared` or `within_r2` is used
- [ ] Whether the B8 custom computation block still exists (lines 371-407)
- [ ] Any code comments referencing the fix

#### Step 3.1.2: Verify Output Artifacts Match

Execute EXACTLY these commands:

```bash
# Step A: Find latest Stage 4 output
ls -lt outputs/econometric/h2_investment/ | head -5

# Step B: Read model_diagnostics.csv and check within_r2 vs rsquared columns
python -c "
import pandas as pd
from pathlib import Path

econ_dir = Path('outputs/econometric/h2_investment')
subdirs = sorted([d for d in econ_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]
diag = pd.read_csv(latest / 'model_diagnostics.csv')

print(f'Latest run: {latest.name}')
print(f'Columns: {list(diag.columns)}')
print()

# Check if within_r2 and rsquared columns exist
if 'within_r2' in diag.columns and 'rsquared' in diag.columns:
    print('Both columns present. Checking values...')
    for _, r in diag.head(3).iterrows():
        diff = abs(r['rsquared'] - r['within_r2'])
        print(f\"{r['sample']}/{r['uncertainty_var']}: rsquared={r['rsquared']:.4f}, within_r2={r['within_r2']:.4f}, diff={diff:.4f}\")
elif 'rsquared' in diag.columns:
    print('Only rsquared column present.')
else:
    print('Neither column found!')
"

# Step C: Read the LaTeX table and extract Within-R² values
grep -n "Within-R" outputs/econometric/h2_investment/*/h2_investment_table.tex

# Step D: Read one raw regression output to get true PanelOLS within-R²
ls outputs/econometric/h2_investment/*/regression_results_Main_Manager_QA_Uncertainty_pct.txt
# Then read lines 1-30 to find "R-squared (Within)"
```

**Evidence to Record:**
- [ ] `rsquared` values from `model_diagnostics.csv`
- [ ] `within_r2` values from `model_diagnostics.csv` (if column exists)
- [ ] Within-R² values from LaTeX table
- [ ] R-squared (Within) from raw PanelOLS output
- [ ] Whether LaTeX matches PanelOLS (diff < 0.001)

#### Step 3.1.3: Verdict for H2-001

Based on evidence collected, mark one:

- [ ] **CONFIRMED FIXED** — LaTeX uses `rsquared`, matches PanelOLS output exactly
- [ ] **PARTIALLY FIXED** — Code changed but outputs not regenerated
- [ ] **NOT FIXED** — LaTeX still uses B8 custom `within_r2`
- [ ] **REGRESSION** — Was fixed but broken again
- [ ] **UNVERIFIABLE** — Cannot determine (explain why)

---

### 3.2 Verification of H2-002: README DV Notation (CLAIMS NOT FIXED)

**Background:** README line 386 says "DV: `|InvestmentResidual|_{t+1}`" but the code uses the signed residual (not absolute value).

**Claimed Fix:** Update README to remove absolute value notation.

#### Step 3.2.1: Read the README Entry

Execute EXACTLY:

```bash
# Read lines 380-395 of README.md to find the H2 DV specification
sed -n '380,395p' README.md

# Alternative: grep for InvestmentResidual
grep -n "InvestmentResidual" README.md
```

**Evidence to Record:**
- [ ] Exact text of H2 DV specification in README
- [ ] Whether `|...|` notation is present
- [ ] Line number of the specification

#### Step 3.2.2: Verify Code Implementation

Execute EXACTLY:

```bash
# Search for abs() in the H2 panel builder
grep -n "abs\|InvestmentResidual" src/f1d/variables/build_h2_investment_panel.py | head -20

# Check the InvestmentResidual_lead distribution (should have negative values if signed)
python -c "
import pandas as pd
from pathlib import Path

panel_dir = Path('outputs/variables/h2_investment')
subdirs = sorted([d for d in panel_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]
panel = pd.read_parquet(latest / 'h2_investment_panel.parquet')

ir_lead = panel['InvestmentResidual_lead'].dropna()
print(f'Total valid: {len(ir_lead):,}')
print(f'Mean: {ir_lead.mean():.4f}')
print(f'Min: {ir_lead.min():.4f}')
print(f'Max: {ir_lead.max():.4f}')
print(f'% negative: {(ir_lead < 0).mean():.1%}')
print(f'% positive: {(ir_lead > 0).mean():.1%}')
"
```

**Evidence to Record:**
- [ ] Whether `abs()` is used anywhere in the panel builder
- [ ] Distribution of InvestmentResidual_lead (presence of negative values confirms signed)
- [ ] Whether README matches implementation

#### Step 3.2.3: Verdict for H2-002

- [ ] **CONFIRMED NOT FIXED** — README still has `|...|` notation
- [ ] **FIXED** — README now correctly describes signed residual
- [ ] **N/A** — README changed but differently (describe)

---

### 3.3 Verification of H2-003: Missing Run Manifest (CLAIMS NOT FIXED)

**Background:** No `run_manifest.json` exists in Stage 3 or Stage 4 outputs.

**Claimed Fix:** Not implemented; recommendation only.

#### Step 3.3.1: Check Current State

Execute EXACTLY:

```bash
# Check if run_manifest.json exists in ANY H2 output
find outputs/variables/h2_investment -name "run_manifest.json" -type f 2>/dev/null
find outputs/econometric/h2_investment -name "run_manifest.json" -type f 2>/dev/null

# List contents of latest Stage 3 run
ls -la outputs/variables/h2_investment/*/

# List contents of latest Stage 4 run
ls -la outputs/econometric/h2_investment/*/
```

**Evidence to Record:**
- [ ] Whether `run_manifest.json` exists anywhere in H2 outputs
- [ ] Files present in latest Stage 3 output directory
- [ ] Files present in latest Stage 4 output directory

#### Step 3.3.2: Check if Code Generates Manifest

Execute EXACTLY:

```bash
# Search for manifest generation code in H2 scripts
grep -n "run_manifest\|manifest" src/f1d/variables/build_h2_investment_panel.py
grep -n "run_manifest\|manifest" src/f1d/econometric/run_h2_investment.py

# Check if any Stage 3/4 script has manifest generation
grep -r "run_manifest" src/f1d/variables/
grep -r "run_manifest" src/f1d/econometric/
```

**Evidence to Record:**
- [ ] Presence/absence of manifest generation code
- [ ] Whether any PR/commit added this feature

#### Step 3.3.3: Verdict for H2-003

- [ ] **CONFIRMED NOT FIXED** — No manifest exists, no code to generate it
- [ ] **FIXED** — Manifest now exists (show evidence)
- [ ] **ALTERNATIVE IMPLEMENTED** — Different reproducibility mechanism (describe)

---

### 3.4 Verification of H2-004: Stale merge_asof Matches (DOCUMENTED)

**Background:** 78 calls (6 firms, 0.07%) have `start_year - fyearq > 2`, matched to 3-12 year old Compustat data. None have valid InvestmentResidual_lead, so they don't affect regressions.

**Claimed Status:** Documented as accepted behavior.

#### Step 3.4.1: Verify Stale Matches Still Exist

Execute EXACTLY:

```bash
python -c "
import pandas as pd
from pathlib import Path

panel_dir = Path('outputs/variables/h2_investment')
subdirs = sorted([d for d in panel_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]
panel = pd.read_parquet(latest / 'h2_investment_panel.parquet')

# Recreate start_year
panel['start_year'] = pd.to_datetime(panel['start_date']).dt.year

# Find stale matches
stale = panel[panel['start_year'] - panel['fyearq_int'] > 2]
print(f'Stale matches: {len(stale)} ({100*len(stale)/len(panel):.2f}%)')
print(f'Unique firms with stale: {stale[\"gvkey\"].nunique()}')
print(f'Stale with valid lead: {stale[\"InvestmentResidual_lead\"].notna().sum()}')
print()
print('Examples of stale matches:')
for _, r in stale.head(5).iterrows():
    gap = r['start_year'] - r['fyearq_int']
    print(f'  gvkey={r[\"gvkey\"]}, start={r[\"start_date\"]}, fyearq={r[\"fyearq_int\"]}, gap={gap}y')
"
```

**Evidence to Record:**
- [ ] Number of stale matches
- [ ] Number of stale matches with valid InvestmentResidual_lead
- [ ] Whether this matches audit findings (78 stale, 0 with valid lead)

#### Step 3.4.2: Check if Tolerance Parameter Added

Execute EXACTLY:

```bash
# Check attach_fyearq function for tolerance parameter
grep -n "tolerance\|max_gap\|days" src/f1d/shared/utils/panel_utils.py
```

**Evidence to Record:**
- [ ] Whether tolerance parameter exists
- [ ] If so, what is the default value

#### Step 3.4.3: Verdict for H2-004

- [ ] **CONFIRMED DOCUMENTED** — Stale matches exist as documented, no regression impact
- [ ] **FIXED** — Tolerance parameter added
- [ ] **CHANGED** — Different behavior (describe)

---

### 3.5 Verification of H2-005: Missing Sample Attrition Table (CLAIMS NOT FIXED)

**Background:** Sample attrition is documented in `report_step3_h2.md` but not as a standalone publication-ready table.

**Claimed Fix:** Not implemented; recommendation only.

#### Step 3.5.1: Check for Attrition Table

Execute EXACTLY:

```bash
# Search for sample attrition table in H2 outputs
find outputs/variables/h2_investment -name "*attrition*" -type f 2>/dev/null
find outputs/econometric/h2_investment -name "*attrition*" -type f 2>/dev/null

# Check Stage 3 report for attrition documentation
ls outputs/variables/h2_investment/*/report_step3_h2.md
# Read a portion of the report
head -50 outputs/variables/h2_investment/*/report_step3_h2.md
```

**Evidence to Record:**
- [ ] Whether `sample_attrition.csv` or `sample_attrition.tex` exists
- [ ] Whether attrition is documented in report
- [ ] Format of attrition documentation

#### Step 3.5.2: Verdict for H2-005

- [ ] **CONFIRMED NOT FIXED** — No standalone attrition table
- [ ] **FIXED** — Attrition table now generated (show evidence)
- [ ] **ALTERNATIVE** — Attrition documented differently (describe)

---

## PART 4: ADDITIONAL ADVERSARIAL CHECKS

Beyond verifying the known issues, perform these proactive checks:

### 4.1 Check for New Regressions

```bash
# Compare file modification times to audit dates
# The initial audit was dated 2026-02-28
# Check if any files were modified AFTER this date

git log --oneline --since="2026-02-28" -- src/f1d/econometric/run_h2_investment.py
git log --oneline --since="2026-02-28" -- src/f1d/variables/build_h2_investment_panel.py
```

### 4.2 Check for Undocumented Changes

```bash
# Compare current code to what audits describe
# Read the full run_h2_investment.py and note any discrepancies
# from what the audits claim to have found
```

### 4.3 Cross-Artifact Consistency Deep Dive

Pick ONE regression (e.g., Main / Manager_QA_Uncertainty_pct) and verify:

| Source | Field | Expected Value | Actual Value | Match? |
|--------|-------|----------------|--------------|--------|
| Raw .txt | beta1 | — | — | — |
| model_diagnostics.csv | beta1 | — | — | — |
| LaTeX table | beta1 coef | — | — | — |
| Raw .txt | beta1_SE | — | — | — |
| LaTeX table | (SE) | — | — | — |
| Raw .txt | N | — | — | — |
| model_diagnostics.csv | n_obs | — | — | — |
| LaTeX table | N | — | — | — |
| Raw .txt | R² (Within) | — | — | — |
| model_diagnostics.csv | rsquared | — | — | — |
| LaTeX table | Within-R² | — | — | — |

### 4.4 Hypothesis Results Verification

Verify the hypothesis results match across all sources:

```bash
python -c "
import pandas as pd
from pathlib import Path

econ_dir = Path('outputs/econometric/h2_investment')
subdirs = sorted([d for d in econ_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]
diag = pd.read_csv(latest / 'model_diagnostics.csv')

h2a_count = diag['beta1_signif'].sum()
h2b_count = diag['beta3_signif'].sum()

print(f'H2a significant (β₁<0, p<0.05): {h2a_count}/18')
print(f'H2b significant (β₃>0, p<0.05): {h2b_count}/18')
print()
print('H2b significant details:')
if h2b_count > 0:
    sig = diag[diag['beta3_signif'] == True]
    for _, r in sig.iterrows():
        print(f\"  {r['sample']}/{r['uncertainty_var']}: β₃={r['beta3']:.4f}, p={r['beta3_p_one']:.3f}\")
"
```

**Expected results (per provenance H2.md §K):**
- H2a: 0/18 significant
- H2b: 1/18 significant (Finance/CEO_QA_Weak_Modal)

---

## PART 5: OUTPUT FORMAT

Your output document must be written to:
`docs/provenance/AUDIT_REVERIFICATION_H2.md`

### Required Sections

```markdown
# Re-Verification Audit Report: Suite H2

**Date:** [TODAY'S DATE]
**Auditor:** [AI Model + Version]
**Input Documents:** H2.md, AUDIT_H2.md, Paper_Artifacts_Audit_H2.md
**Verification Method:** Manual one-by-one inspection per AUDIT_REVERIFICATION_PROMPT_H2.md

---

## Executive Summary

| Total Issues Verified | Confirmed Fixed | Confirmed Not Fixed | New Issues Found | Unverifiable |
|-----------------------|-----------------|---------------------|------------------|--------------|
| X | Y | Z | A | B |

### Overall Assessment
[2-3 sentences on the state of the suite]

---

## Claim Ledger

[Copy from Part 2.3 with updated status]

---

## Verification Results

### H2-001: Within-R² Inflation
**Claimed Status:** FIXED
**Verification Steps:** [List steps performed]
**Evidence:**
- [Exact commands and outputs]
**Verdict:** [CONFIRMED FIXED / NOT FIXED / etc.]
**Rationale:** [1-2 sentences]

### H2-002: README DV Notation
[Same format]

### H2-003: Missing Run Manifest
[Same format]

### H2-004: Stale merge_asof Matches
[Same format]

### H2-005: Missing Sample Attrition Table
[Same format]

---

## Additional Findings

[List any new issues discovered during verification]

---

## Cross-Artifact Consistency Matrix

[Table from 4.3]

---

## Hypothesis Results Verification

[Table comparing expected vs actual results]

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
- [ ] My output document is saved to `docs/provenance/AUDIT_REVERIFICATION_H2.md`

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

## PART 7: SPECIAL VERIFICATION NOTES FOR H2

### H2-Specific Verification: Biddle Investment Residual

The H2 suite uses the Biddle et al. (2009) investment residual methodology. Verify:

1. **Investment formula**: `(capxy + xrdy + aqcy - sppey) / atq_{t-1}`
2. **First-stage OLS**: `Investment ~ SalesGrowth_lag` within FF48-year cells
3. **Residual extraction**: Actual - Predicted investment
4. **Winsorization**: Applied post-OLS by fiscal year

```bash
# Verify Biddle implementation
grep -n "InvestmentResidual\|SalesGrowth_lag\|FF48" src/f1d/shared/variables/_compustat_engine.py | head -30
```

### H2-Specific Verification: One-Tailed Tests

H2 uses directional one-tailed tests:
- H2a: β₁ < 0 (uncertainty → more underinvestment)
- H2b: β₃ > 0 (leverage attenuates effect)

```bash
# Verify one-tailed p-value logic
grep -n "p_one\|p_two\|beta1\|beta3" src/f1d/econometric/run_h2_investment.py | head -30
```

---

END OF PROMPT
