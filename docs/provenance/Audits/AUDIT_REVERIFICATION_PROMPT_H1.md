# Audit Re-Verification Prompt: Suite H1 (Cash Holdings)

**Purpose:** This prompt instructs an AI auditor to re-verify all claimed issues from prior audits against the current codebase and output artifacts.

**Target Suite:** H1 — Speech Uncertainty and Future Cash Holdings
**Input Documents:**
- `docs/provenance/H1.md` (Provenance documentation)
- `docs/provenance/AUDIT_H1.md` (Initial adversarial audit)
- `docs/provenance/Paper_Artifacts_Audit_H1.md` (Paper-submission readiness audit)

**Output Deliverable:** `docs/provenance/AUDIT_REVERIFICATION_H1.md`

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
| **Line numbers** | Specific lines read (e.g., "lines 385-392") |
| **Command executed** | Literal command with all flags |
| **Raw output** | Exact output received (truncate if long, but show key parts) |
| **Timestamp check** | Modification time of files (if relevant to "was this fixed?") |
| **Cross-reference** | At least 2 independent sources for critical claims |

---

## PART 2: CLAIM LEDGER EXTRACTION

Before auditing, extract a **Claim Ledger** from the three input documents. This is your source of truth for what needs verification.

### 2.1 Issue Register (Extract from AUDIT_H1.md)

| ID | Severity | Description | Claimed Fix | Status Claimed |
|----|----------|-------------|-------------|----------------|
| H1-AUDIT-001 | BLOCKER | Manual `within_r2` computation uses grand mean instead of demeaned mean, inflating R² from ~0.06 to ~0.84 | Remove manual block, use `model.rsquared_within` | FIXED (per Paper_Artifacts_Audit) |
| H1-AUDIT-002 | MINOR | Provenance claims `CashHoldings_lead` constant within firm-year, but varies within calendar year | Update H1.md Sec J.4 to clarify fiscal vs calendar year | CLARIFIED (no code fix needed) |
| H1-AUDIT-003 | NOTE | Docstring on line 13 mentions "HC1 standard errors" but code uses firm-clustered | Update docstring to "firm-clustered standard errors" | NOT FIXED |

### 2.2 Issue Register (Extract from Paper_Artifacts_Audit_H1.md)

| ID | Severity | Description | Claimed Fix | Status Claimed |
|----|----------|-------------|-------------|----------------|
| H1-PAPER-001 | MINOR | No `run_manifest.json` in output directory | Add manifest generation to Stage 4 | NOT FIXED |
| H1-PAPER-002 | NOTE | Stale docstring (duplicate of H1-AUDIT-003) | Update line 13 | NOT FIXED |
| H1-PAPER-003 | CLARIFIED | DV constancy claim in provenance (duplicate of H1-AUDIT-002) | Clarify fiscal vs calendar in H1.md | DOCUMENTED ONLY |

### 2.3 Consolidated Claim Ledger

| ID | Severity | Claim | Fix Location | Audit Status Claimed |
|----|----------|-------|--------------|---------------------|
| H1-001 | ~~BLOCKER~~ | Within-R² inflated via manual computation bug | `run_h1_cash_holdings.py` lines 389-425 | CLAIMS FIXED |
| H1-002 | MINOR | Missing `run_manifest.json` | Stage 4 output directory | CLAIMS NOT FIXED |
| H1-003 | NOTE | Stale docstring (HC1 → firm-clustered) | `run_h1_cash_holdings.py` line 13 | CLAIMS NOT FIXED |
| H1-004 | NOTE | Provenance claim about DV constancy misleading | `H1.md` Section J.4 | CLAIMS CLARIFIED |

---

## PART 3: VERIFICATION PROCEDURES (Execute One-by-One)

### 3.1 Verification of H1-001: Within-R² Bug (CLAIMS FIXED)

**Background:** The initial audit found that manual `within_r2` computation used grand mean instead of demeaned mean in the SS_tot denominator, inflating R² from ~0.06 to ~0.84.

**Claimed Fix:** Code now uses `within_r2 = float(model.rsquared_within)` directly.

#### Step 3.1.1: Verify Code Implementation

Execute EXACTLY these commands in order:

```bash
# Step A: Find the current run_h1_cash_holdings.py file
find src -name "run_h1_cash_holdings.py" -type f 2>/dev/null

# Step B: Read lines 380-430 to examine the within_r2 computation
# (Do NOT use grep. Use Read tool or cat -n with line range)
# Look for:
#   - Presence/absence of manual within_r2 block
#   - Whether model.rsquared_within is used directly
#   - Any try/except blocks around R² computation

# Step C: Search for the specific buggy pattern
grep -n "np.mean(y)" src/f1d/econometric/run_h1_cash_holdings.py

# Step D: Search for the correct pattern
grep -n "rsquared_within" src/f1d/econometric/run_h1_cash_holdings.py
```

**Evidence to Record:**
- [ ] Exact lines where `within_r2` is computed
- [ ] Whether the buggy `np.mean(y)` pattern exists
- [ ] Whether `model.rsquared_within` is used
- [ ] Any code comments referencing the fix

#### Step 3.1.2: Verify Output Artifacts Match

Execute EXACTLY these commands:

```bash
# Step A: Find latest Stage 4 output
ls -lt outputs/econometric/h1_cash_holdings/ | head -5

# Step B: Read model_diagnostics.csv and check within_r2 column
# Use Python to get actual values:
python -c "
import pandas as pd
from pathlib import Path

econ_dir = Path('outputs/econometric/h1_cash_holdings')
subdirs = sorted([d for d in econ_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]
diag = pd.read_csv(latest / 'model_diagnostics.csv')

print(f'Latest run: {latest.name}')
print(f'Columns: {list(diag.columns)}')
print(f'within_r2 range: {diag[\"within_r2\"].min():.4f} - {diag[\"within_r2\"].max():.4f}')
print(f'rsquared range: {diag[\"rsquared\"].min():.4f} - {diag[\"rsquared\"].max():.4f}')
"

# Step C: Read one raw regression output and compare
# Find a .txt file and grep for R-squared
ls outputs/econometric/h1_cash_holdings/*/regression_results_Main_CEO_QA_Uncertainty_pct.txt
# Then read lines 1-30 to find "R-squared (Within)"
```

**Evidence to Record:**
- [ ] `within_r2` values from `model_diagnostics.csv` (should be ~0.05-0.06)
- [ ] `rsquared` values from `model_diagnostics.csv`
- [ ] Raw PanelOLS output showing "R-squared (Within)"
- [ ] Whether these three values match

#### Step 3.1.3: Verify LaTeX Table

Execute EXACTLY:

```bash
# Find and read the LaTeX table, focusing on R² row
ls outputs/econometric/h1_cash_holdings/*/h1_cash_holdings_table.tex

# Read the file and search for "Within-R" or "R\$\\^2"
grep -n "Within-R\|R\$.*2" outputs/econometric/h1_cash_holdings/*/h1_cash_holdings_table.tex
```

**Evidence to Record:**
- [ ] R² values reported in LaTeX table
- [ ] Whether they match the raw output (~0.05-0.06, NOT ~0.84)

#### Step 3.1.4: Verdict for H1-001

Based on evidence collected, mark one:

- [ ] **CONFIRMED FIXED** — Code uses `rsquared_within`, outputs match, LaTeX correct
- [ ] **PARTIALLY FIXED** — Code fixed but outputs not regenerated
- [ ] **NOT FIXED** — Buggy code still present
- [ ] **REGRESSION** — Was fixed but broken again
- [ ] **UNVERIFIABLE** — Cannot determine (explain why)

---

### 3.2 Verification of H1-002: Missing Run Manifest (CLAIMS NOT FIXED)

**Background:** No `run_manifest.json` exists in Stage 4 outputs with git commit, config snapshot, or input fingerprints.

**Claimed Fix:** Not implemented; recommendation only.

#### Step 3.2.1: Check Current State

Execute EXACTLY:

```bash
# Check if run_manifest.json exists in ANY Stage 4 output
find outputs/econometric/h1_cash_holdings -name "run_manifest.json" -type f 2>/dev/null

# List contents of latest Stage 4 run to see what files exist
ls -la outputs/econometric/h1_cash_holdings/*/
```

**Evidence to Record:**
- [ ] Whether `run_manifest.json` exists anywhere
- [ ] Files present in latest Stage 4 output directory
- [ ] Whether any alternative manifest mechanism exists (e.g., in report files)

#### Step 3.2.2: Check if Code Generates Manifest

Execute EXACTLY:

```bash
# Search for manifest generation code
grep -n "run_manifest\|manifest" src/f1d/econometric/run_h1_cash_holdings.py

# Check if any other Stage 4 script has manifest generation
grep -r "run_manifest" src/f1d/econometric/
```

**Evidence to Record:**
- [ ] Presence/absence of manifest generation code
- [ ] Whether any PR/commit added this feature

#### Step 3.2.3: Verdict for H1-002

- [ ] **CONFIRMED NOT FIXED** — No manifest exists, no code to generate it
- [ ] **FIXED** — Manifest now exists (show evidence)
- [ ] **ALTERNATIVE IMPLEMENTED** — Different reproducibility mechanism (describe)

---

### 3.3 Verification of H1-003: Stale Docstring (CLAIMS NOT FIXED)

**Background:** Line 13 of `run_h1_cash_holdings.py` mentions "HC1 standard errors" but code uses firm-clustered SEs.

**Claimed Fix:** Update docstring.

#### Step 3.3.1: Read the Actual Docstring

Execute EXACTLY:

```bash
# Read lines 1-20 of run_h1_cash_holdings.py
head -20 src/f1d/econometric/run_h1_cash_holdings.py
```

**Evidence to Record:**
- [ ] Exact text of docstring on line 13 (or nearby)
- [ ] Whether "HC1" is mentioned
- [ ] Whether "firm-clustered" is mentioned

#### Step 3.3.2: Verify Actual SE Implementation

Execute EXACTLY:

```bash
# Find where standard errors are configured
grep -n "cov_type\|cluster_entity\|HC1" src/f1d/econometric/run_h1_cash_holdings.py
```

**Evidence to Record:**
- [ ] Exact `cov_type` setting
- [ ] Exact `cluster_entity` setting
- [ ] Whether docstring matches implementation

#### Step 3.3.3: Verdict for H1-003

- [ ] **CONFIRMED NOT FIXED** — Docstring still says HC1
- [ ] **FIXED** — Docstring now correct (show exact text)
- [ ] **N/A** — Docstring changed but differently (describe)

---

### 3.4 Verification of H1-004: DV Constancy Provenance Claim (CLAIMS CLARIFIED)

**Background:** `H1.md` Section J.4 claims `CashHoldings_lead` is "constant within firm-year clusters" but this is only true for fiscal year, not calendar year used by PanelOLS.

**Claimed Fix:** Clarification in documentation (no code change).

#### Step 3.4.1: Read Current Provenance Document

Execute EXACTLY:

```bash
# Read Section J (Known Issues) of H1.md
# Look for lines 428-446 approximately
sed -n '428,446p' docs/provenance/H1.md
```

**Evidence to Record:**
- [ ] Exact text of J.4 section
- [ ] Whether "fiscal year" vs "calendar year" distinction is made
- [ ] Whether the claim has been clarified or is still misleading

#### Step 3.4.2: Verify the Underlying Data Property

Execute EXACTLY:

```bash
python -c "
import pandas as pd
from pathlib import Path

panel_dir = Path('outputs/variables/h1_cash_holdings')
subdirs = sorted([d for d in panel_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]
panel = pd.read_parquet(latest / 'h1_cash_holdings_panel.parquet')

# Check constancy within fiscal year (fyearq_int)
fiscal_unique = panel.groupby(['gvkey', 'fyearq_int'])['CashHoldings_lead'].nunique()
print(f'Fiscal year clusters with 1 unique value: {(fiscal_unique == 1).sum():,}')
print(f'Fiscal year clusters with >1 unique values: {(fiscal_unique > 1).sum():,}')

# Check constancy within calendar year
calendar_unique = panel.groupby(['gvkey', 'year'])['CashHoldings_lead'].nunique()
print(f'Calendar year clusters with 1 unique value: {(calendar_unique == 1).sum():,}')
print(f'Calendar year clusters with >1 unique values: {(calendar_unique > 1).sum():,}')
"
```

**Evidence to Record:**
- [ ] Fiscal year cluster constancy results
- [ ] Calendar year cluster constancy results
- [ ] Whether provenance claim accurately reflects this

#### Step 3.4.3: Verdict for H1-004

- [ ] **CONFIRMED CLARIFIED** — Provenance now correctly distinguishes fiscal vs calendar
- [ ] **NOT ADDRESSED** — Original misleading claim still present
- [ ] **PARTIALLY ADDRESSED** — Some change but still ambiguous (describe)

---

## PART 4: ADDITIONAL ADVERSARIAL CHECKS

Beyond verifying the known issues, perform these proactive checks:

### 4.1 Check for New Regressions

```bash
# Compare file modification times to audit dates
# The initial audit was dated 2026-02-28
# Paper audit was dated 2026-02-28
# Check if any files were modified AFTER these dates

git log --oneline --since="2026-02-28" -- src/f1d/econometric/run_h1_cash_holdings.py
git log --oneline --since="2026-02-28" -- src/f1d/variables/build_h1_cash_holdings_panel.py
```

### 4.2 Check for Undocumented Changes

```bash
# Compare current code to what audits describe
# Read the full run_h1_cash_holdings.py and note any discrepancies
# from what the audits claim to have found
```

### 4.3 Cross-Artifact Consistency Deep Dive

Pick ONE regression (e.g., Main / CEO_QA_Uncertainty_pct) and verify:

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
| model_diagnostics.csv | within_r2 | — | — | — |
| LaTeX table | Within-R² | — | — | — |

---

## PART 5: OUTPUT FORMAT

Your output document must be written to:
`docs/provenance/AUDIT_REVERIFICATION_H1.md`

### Required Sections

```markdown
# Re-Verification Audit Report: Suite H1

**Date:** [TODAY'S DATE]
**Auditor:** [AI Model + Version]
**Input Documents:** H1.md, AUDIT_H1.md, Paper_Artifacts_Audit_H1.md
**Verification Method:** Manual one-by-one inspection per AUDIT_REVERIFICATION_PROMPT_H1.md

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

### H1-001: Within-R² Bug
**Claimed Status:** FIXED
**Verification Steps:** [List steps performed]
**Evidence:**
- [Exact commands and outputs]
**Verdict:** [CONFIRMED FIXED / NOT FIXED / etc.]
**Rationale:** [1-2 sentences]

### H1-002: Missing Run Manifest
[Same format]

### H1-003: Stale Docstring
[Same format]

### H1-004: DV Constancy Provenance
[Same format]

---

## Additional Findings

[List any new issues discovered during verification]

---

## Cross-Artifact Consistency Matrix

[Table from 4.3]

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
- [ ] My output document is saved to `docs/provenance/AUDIT_REVERIFICATION_H1.md`

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

END OF PROMPT
