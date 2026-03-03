# Audit Re-Verification Prompt: Suite H10 (Tone-at-the-Top)

**Purpose:** This prompt instructs an AI auditor to re-verify all claimed issues from prior audits against the current codebase and output artifacts.

**Target Suite:** H10 — Tone-at-the-Top Transmission (H_TT)
**Input Documents:**
- `docs/provenance/H10.md` (Provenance documentation)
- `docs/provenance/AUDIT_H10.md` (Adversarial implementation audit)
- `docs/provenance/Paper_Artifacts_Audit_H10.md` (Paper-submission readiness audit)

**Output Deliverable:** `docs/provenance/AUDIT_REVERIFICATION_H10.md`

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
| **Line numbers** | Specific lines read (e.g., "lines 1084-1093") |
| **Command executed** | Literal command with all flags |
| **Raw output** | Exact output received (truncate if long, but show key parts) |
| **Timestamp check** | Modification time of files (if relevant to "was this fixed?") |
| **Cross-reference** | At least 2 independent sources for critical claims |

---

## PART 2: CLAIM LEDGER EXTRACTION

### 2.1 Issue Register (Extract from AUDIT_H10.md)

| ID | Severity | Description | Claimed Fix | Status Claimed |
|----|----------|-------------|-------------|----------------|
| H10-AUDIT-001 | MAJOR | "Main" sample = ALL industries, not non-fin/non-util | Change lines 1084-1093 to `call_panel[call_panel["sample"] == sample]` | NOT FIXED |
| H10-AUDIT-002 | MAJOR | Duplicate entity-time index in M1 PanelOLS (347 firm-quarters) | Add deduplication before set_index | NOT FIXED |
| H10-AUDIT-003 | MAJOR | LaTeX table clustering note wrong for M2 (says Firm×CEO, is Firm×Call) | Update LaTeX note to be model-specific | NOT FIXED |
| H10-AUDIT-004 | MAJOR | Placebo test failure undermines causal claim (t=31.49) | Interpretive — document prominently | DOCUMENTED |
| H10-AUDIT-005 | MINOR | Turn_Uncertainty_pct unwinsorized (values to 100%) | Add winsorization at Stage 3 | NOT FIXED |
| H10-AUDIT-006 | MINOR | Winsorization inconsistency CEO vs CFO | Update provenance documentation | NOT FIXED |
| H10-AUDIT-007 | MINOR | 2002 absent from M1 regression | Document expected behavior | NOT FIXED |
| H10-AUDIT-008 | NOTE | CEO_Unc_Lag1 has 57.9% zeros | Consider NaN instead of ffill zeros | DOCUMENTED |

### 2.2 Issue Register (Extract from Paper_Artifacts_Audit_H10.md)

| ID | Severity | Description | Claimed Fix | Status Claimed |
|----|----------|-------------|-------------|----------------|
| H10-PAPER-001 | BLOCKER | Sample filter bug (duplicate of H10-AUDIT-001) | Same as H10-AUDIT-001 | NOT FIXED |
| H10-PAPER-002 | BLOCKER | LaTeX clustering note incorrect (duplicate of H10-AUDIT-003) | Same as H10-AUDIT-003 | NOT FIXED |
| H10-PAPER-003 | MAJOR | Missing run_manifest.json | Add manifest generation | NOT FIXED |
| H10-PAPER-004 | MAJOR | Placebo test (duplicate) | Same as H10-AUDIT-004 | DOCUMENTED |
| H10-PAPER-005 | MAJOR | Duplicate entity-time (duplicate of H10-AUDIT-002) | Same as H10-AUDIT-002 | NOT FIXED |
| H10-PAPER-006 | MINOR | No sample attrition table in publication format | Generate sample_attrition.tex | NOT FIXED |
| H10-PAPER-007 | MINOR | Turn_Uncertainty_pct unwinsorized (duplicate) | Same as H10-AUDIT-005 | NOT FIXED |

### 2.3 Consolidated Claim Ledger

| ID | Severity | Claim | Fix Location | Audit Status Claimed |
|----|----------|-------|--------------|---------------------|
| H10-001 | BLOCKER | "Main" sample includes ALL industries instead of non-fin/non-util | `run_h10_tone_at_top.py:1084-1093` | CLAIMS NOT FIXED |
| H10-002 | BLOCKER | LaTeX table clustering note incorrect for M2 | `run_h10_tone_at_top.py:523` | CLAIMS NOT FIXED |
| H10-003 | MAJOR | Duplicate entity-time index in M1 (347 firm-quarters) | `run_h10_tone_at_top.py:133` | CLAIMS NOT FIXED |
| H10-004 | MAJOR | Missing run_manifest.json | Stage 3 + Stage 4 | CLAIMS NOT FIXED |
| H10-005 | MAJOR | Placebo test failure (t=31.49 > main t=19.37) | H10.md documentation | DOCUMENTED |
| H10-006 | MINOR | Turn_Uncertainty_pct unwinsorized (max=100%) | `build_h10_tone_at_top_panel.py` | CLAIMS NOT FIXED |
| H10-007 | MINOR | Winsorization inconsistency CEO vs CFO | H10.md §G | CLAIMS NOT FIXED |
| H10-008 | MINOR | No sample attrition table in LaTeX format | Stage 3 | CLAIMS NOT FIXED |
| H10-009 | NOTE | CEO_Unc_Lag1 has 57.9% zeros | Documentation | DOCUMENTED |
| H10-010 | NOTE | 2002 absent from M1 (expected) | Documentation | DOCUMENTED |

---

## PART 3: VERIFICATION PROCEDURES (Execute One-by-One)

### 3.1 Verification of H10-001: Sample Filter Bug (BLOCKER)

**Background:** M1 Main N=43,570 includes Finance (6,793) + Utility (1,378) observations. Should be ~35,399 for true Main sample.

**Claimed Fix:** Change lines 1084-1093 to properly filter `call_panel[call_panel["sample"] == sample]`.

#### Step 3.1.1: Verify Code Implementation

Execute EXACTLY:

```bash
# Read lines 1080-1100 of run_h10_tone_at_top.py
grep -n "call_sub\|turns_sub\|sample.*Main" src/f1d/econometric/run_h10_tone_at_top.py | head -30
```

**Evidence to Record:**
- [ ] Exact code at lines 1084-1093
- [ ] Whether `if sample == "Main"` returns full panel or filters correctly
- [ ] Whether the bug pattern persists

#### Step 3.1.2: Verify Sample Composition

Execute EXACTLY:

```python
import pandas as pd
from pathlib import Path

panel_dir = Path('outputs/variables/tone_at_top')
subdirs = sorted([d for d in panel_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]
cp = pd.read_parquet(latest / 'tone_at_top_panel.parquet')

# Full panel after M1 listwise deletion
full = cp.dropna(subset=['ClarityStyle_Realtime','CFO_QA_Uncertainty_pct','Size','BM','Lev','ROA','StockRet','MarketRet','EPS_Growth','SurpDec'])
print(f'Full panel (M1 listwise): {len(full):,}')
print('Sample breakdown:')
print(full['sample'].value_counts())

# Expected: Main=35,399 Finance=6,793 Utility=1,378
```

**Evidence to Record:**
- [ ] Full M1 sample count
- [ ] Breakdown by sample (Main/Finance/Utility)
- [ ] Whether composition matches expected

#### Step 3.1.3: Check model_diagnostics for N

Execute EXACTLY:

```python
import pandas as pd
from pathlib import Path

econ_dir = Path('outputs/econometric/tone_at_top')
subdirs = sorted([d for d in econ_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]
diag = pd.read_csv(latest / 'model_diagnostics.csv')

print(diag[['model', 'n_obs', 'n_entities']])
# Main_M1 should show ~43,570 if bug persists, ~35,399 if fixed
```

#### Step 3.1.4: Verdict for H10-001

- [ ] **CONFIRMED FIXED** — Main sample now correctly excludes Finance/Utility
- [ ] **CONFIRMED NOT FIXED** — Bug still present, Main includes all industries
- [ ] **PARTIALLY FIXED** — Some change but still problematic
- [ ] **UNVERIFIABLE** — Cannot determine

---

### 3.2 Verification of H10-002: LaTeX Clustering Note (BLOCKER)

**Background:** `tone_at_top_full.tex:53` states "Firm × CEO" clustering for all models, but M2 uses "Firm × Call".

#### Step 3.2.1: Read LaTeX Table

Execute EXACTLY:

```bash
# Find latest tone_at_top_full.tex
ls -lt outputs/econometric/tone_at_top/*/tone_at_top_full.tex | head -1

# Read the notes section (typically near end of table)
grep -n "clustered\|Notes" outputs/econometric/tone_at_top/*/tone_at_top_full.tex
```

**Evidence to Record:**
- [ ] Exact text of clustering note
- [ ] Whether it's model-specific (M1 vs M2)
- [ ] Line number of note

#### Step 3.2.2: Check Source Code for M2 Clustering

Execute EXACTLY:

```bash
grep -n "cluster_by_call\|Firm.*Call\|clusters.*file_name" src/f1d/econometric/run_h10_tone_at_top.py | head -20
```

**Evidence to Record:**
- [ ] What clustering M2 actually uses
- [ ] Whether note matches implementation

#### Step 3.2.3: Verdict for H10-002

- [ ] **CONFIRMED FIXED** — Note now correctly distinguishes M1 vs M2 clustering
- [ ] **CONFIRMED NOT FIXED** — Note still says "Firm × CEO" for all models
- [ ] **UNVERIFIABLE** — Cannot determine

---

### 3.3 Verification of H10-003: Duplicate Entity-Time Index (MAJOR)

**Background:** 347 firm-quarters have >1 call in M1 sample, creating non-unique PanelOLS index.

#### Step 3.3.1: Check for Duplicate Index

Execute EXACTLY:

```python
import pandas as pd
from pathlib import Path

panel_dir = Path('outputs/variables/tone_at_top')
subdirs = sorted([d for d in panel_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]
cp = pd.read_parquet(latest / 'tone_at_top_panel.parquet')

# Create yq_id
cp['yq_id'] = (cp['year'].astype(str) + 'Q' + cp['quarter'].astype(str))

# Apply M1 listwise deletion
reg = cp.dropna(subset=['ClarityStyle_Realtime','CFO_QA_Uncertainty_pct','Size','BM','Lev','ROA','StockRet','MarketRet','EPS_Growth','SurpDec'])

# Check for duplicates
dups = reg.groupby(['gvkey','yq_id']).size()
n_dups = (dups > 1).sum()
n_rows_affected = dups[dups > 1].sum()

print(f'Firm-quarters with >1 call: {n_dups}')
print(f'Total duplicate rows: {n_rows_affected}')
```

#### Step 3.3.2: Check Source Code for Deduplication

Execute EXACTLY:

```bash
grep -n "drop_duplicates\|set_index.*gvkey.*yq\|entity.*time.*unique" src/f1d/econometric/run_h10_tone_at_top.py | head -20
```

#### Step 3.3.3: Verdict for H10-003

- [ ] **CONFIRMED FIXED** — Deduplication now applied
- [ ] **CONFIRMED NOT FIXED** — Duplicates still present
- [ ] **UNVERIFIABLE** — Cannot determine

---

### 3.4 Verification of H10-004: Missing Run Manifest (MAJOR)

**Background:** No `run_manifest.json` with git commit, timestamps, input hashes.

#### Step 3.4.1: Check for Manifest Files

Execute EXACTLY:

```bash
find outputs/variables/tone_at_top -name "run_manifest.json" 2>/dev/null
find outputs/econometric/tone_at_top -name "run_manifest.json" 2>/dev/null
```

#### Step 3.4.2: Verdict for H10-004

- [ ] **CONFIRMED FIXED** — Manifests now generated
- [ ] **CONFIRMED NOT FIXED** — Still missing

---

### 3.5 Verification of H10-005: Placebo Test Documented (MAJOR/DOCUMENTED)

**Background:** M2 placebo (future CEO uncertainty) has t=31.49, stronger than main IV (t=19.37).

#### Step 3.5.1: Verify Placebo Coefficient

Execute EXACTLY:

```python
import pandas as pd
from pathlib import Path

econ_dir = Path('outputs/econometric/tone_at_top')
subdirs = sorted([d for d in econ_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]

# Read placebo and baseline coefficients
placebo = pd.read_csv(latest / 'coefficients_Main_M2_placebo_lead.csv')
baseline = pd.read_csv(latest / 'coefficients_Main_M2_baseline.csv')

print('Placebo (CEO_Unc_Lead1):')
print(placebo[placebo['variable'].str.contains('CEO_Unc')][['variable', 'coef', 'se', 't']])

print('\nBaseline (CEO_Prior_QA_Unc):')
print(baseline[baseline['variable'].str.contains('CEO')][['variable', 'coef', 'se', 't']])
```

#### Step 3.5.2: Check Provenance Documentation

Execute EXACTLY:

```bash
grep -n "placebo\|Lead1\|future.*CEO\|undermines" docs/provenance/H10.md
```

#### Step 3.5.3: Verdict for H10-005

- [ ] **CONFIRMED DOCUMENTED** — Placebo issue documented in provenance
- [ ] **NOT DOCUMENTED** — Should be added

---

### 3.6 Verification of H10-006: Turn_Uncertainty_pct Unwinsorized (MINOR)

**Background:** Turn_Uncertainty_pct ranges 0-100% with 478 turns >50%.

#### Step 3.6.1: Check Turn Uncertainty Distribution

Execute EXACTLY:

```python
import pandas as pd
from pathlib import Path

panel_dir = Path('outputs/variables/tone_at_top')
subdirs = sorted([d for d in panel_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]
tp = pd.read_parquet(latest / 'tone_at_top_turns_panel.parquet')

print(f'Turn_Uncertainty_pct stats:')
print(f'  min: {tp["Turn_Uncertainty_pct"].min():.2f}')
print(f'  max: {tp["Turn_Uncertainty_pct"].max():.2f}')
print(f'  p99: {tp["Turn_Uncertainty_pct"].quantile(0.99):.2f}')
print(f'  values > 50%: {(tp["Turn_Uncertainty_pct"] > 50).sum():,}')
print(f'  values > 25%: {(tp["Turn_Uncertainty_pct"] > 25).sum():,}')
```

#### Step 3.6.2: Verdict for H10-006

- [ ] **CONFIRMED FIXED** — Winsorization now applied
- [ ] **CONFIRMED NOT FIXED** — Still unwinsorized (max=100)
- [ ] **DOCUMENTED AS INTENTIONAL** — Decision to not winsorize documented

---

### 3.7 Verification of H10-007: Winsorization Inconsistency (MINOR)

**Background:** CEO_QA uses per-year winsorization; CFO_QA uses pooled. Provenance claims "pooled" for all.

#### Step 3.7.1: Compare CEO vs CFO Max Values

Execute EXACTLY:

```python
import pandas as pd
from pathlib import Path

panel_dir = Path('outputs/variables/tone_at_top')
subdirs = sorted([d for d in panel_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]
cp = pd.read_parquet(latest / 'tone_at_top_panel.parquet')

# Check per-year max for CEO
print('CEO_QA_Uncertainty_pct max by year:')
print(cp.groupby('year')['CEO_QA_Uncertainty_pct'].max())

# Check pooled max for CFO
print(f'\nCFO_QA_Uncertainty_pct pooled max: {cp["CFO_QA_Uncertainty_pct"].max():.4f}')
```

#### Step 3.7.2: Verdict for H10-007

- [ ] **CONFIRMED FIXED** — Provenance now correctly documents difference
- [ ] **CONFIRMED NOT FIXED** — Provenance still incorrect
- [ ] **N/A** — Winsorization unified

---

### 3.8 Verification of H10-008: Sample Attrition Table (MINOR)

**Background:** `reconciliation_table.csv` exists but no LaTeX version.

#### Step 3.8.1: Check for LaTeX Attrition Table

Execute EXACTLY:

```bash
find outputs/variables/tone_at_top -name "*attrition*.tex" 2>/dev/null
ls outputs/variables/tone_at_top/*/sample_attrition*.tex 2>/dev/null
ls outputs/variables/tone_at_top/*/reconciliation*.tex 2>/dev/null
```

#### Step 3.8.2: Verdict for H10-008

- [ ] **CONFIRMED FIXED** — LaTeX attrition table now generated
- [ ] **CONFIRMED NOT FIXED** — Still missing

---

### 3.9 Verification of H10-009 & H10-010: Documented Issues (NOTE)

These are documentation-only issues:
- H10-009: CEO_Unc_Lag1 has 57.9% zeros
- H10-010: 2002 absent from M1 (expected due to min_calls=4)

#### Verdict

- [ ] **CONFIRMED DOCUMENTED** — Mentioned in provenance
- [ ] **NOT DOCUMENTED** — Should be added

---

## PART 4: ADDITIONAL ADVERSARIAL CHECKS

### 4.1 Check for New Regressions

```bash
# Compare file modification times to audit dates
# Initial audit: 2026-03-01
git log --oneline --since="2026-03-01" -- src/f1d/econometric/run_h10_tone_at_top.py
git log --oneline --since="2026-03-01" -- src/f1d/variables/build_h10_tone_at_top_panel.py
```

### 4.2 Cross-Artifact Consistency Deep Dive

For M1 Main, verify:

| Source | Field | Expected | Actual | Match? |
|--------|-------|----------|--------|--------|
| coefficients CSV | ClarityStyle coef | ~0.0169 | — | — |
| model_diagnostics | n_obs | — | — | — |
| LaTeX table | coef | — | — | — |
| report.md | coef | — | — | — |

### 4.3 Model-Family Specific Checks (Panel FE / Absorbing LS)

```python
import pandas as pd
from pathlib import Path

econ_dir = Path('outputs/econometric/tone_at_top')
subdirs = sorted([d for d in econ_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]
diag = pd.read_csv(latest / 'model_diagnostics.csv')

# Check for required model-family artifacts
print('Model diagnostics:')
print(diag[['model', 'n_obs', 'r2', 'within_r2']])

# Verify within_r2 is present for M1 (PanelOLS) models
# Verify r2 is present for M2 (AbsorbingLS) models
```

---

## PART 5: OUTPUT FORMAT

Your output document must be written to:
`docs/provenance/AUDIT_REVERIFICATION_H10.md`

### Required Sections

```markdown
# Re-Verification Audit Report: Suite H10

**Date:** [TODAY'S DATE]
**Auditor:** [AI Model + Version]
**Input Documents:** H10.md, AUDIT_H10.md, Paper_Artifacts_Audit_H10.md
**Verification Method:** Manual one-by-one inspection per AUDIT_REVERIFICATION_PROMPT_H10.md

---

## Executive Summary

| Total Issues Verified | Confirmed Fixed | Confirmed Not Fixed | Documented/Accepted | Unverifiable |
|-----------------------|-----------------|---------------------|---------------------|--------------|
| X | Y | Z | A | B |

### Overall Assessment
[2-3 sentences on the state of the suite]

### Trustworthy Results
- **M1 (Call-level):** [YES/NO/PARTIAL]
- **M2 (Turn-level):** [YES/NO/PARTIAL]

---

## Claim Ledger

[Copy from Part 2.3 with updated status]

---

## Verification Results

### H10-001: Sample Filter Bug
**Claimed Status:** NOT FIXED
**Verification Steps:** [List steps performed]
**Evidence:**
- [Exact commands and outputs]
**Verdict:** [CONFIRMED FIXED / NOT FIXED / etc.]
**Rationale:** [1-2 sentences]

### H10-002: LaTeX Clustering Note
[Same format]

[... continue for all issues ...]

---

## Additional Findings

[List any new issues discovered during verification]

---

## Cross-Artifact Consistency Matrix

[Table from 4.2]

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
- [ ] My output document is saved to `docs/provenance/AUDIT_REVERIFICATION_H10.md`

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

## PART 7: H10-SPECIFIC VERIFICATION NOTES

### Dual Model Family

H10 uses two distinct model families:

| Model | Family | Estimator | Unit |
|-------|--------|-----------|------|
| M1 | Panel FE | PanelOLS | Call-level (firm-quarter) |
| M2 | Absorbing LS | AbsorbingLS | Turn-level (speaker-turn) |

### Key Code Locations

| Issue | File | Line(s) |
|-------|------|---------|
| Sample filter bug | `run_h10_tone_at_top.py` | 1084-1093 |
| Duplicate index | `run_h10_tone_at_top.py` | 133 |
| M2 clustering | `run_h10_tone_at_top.py` | 250-253 |
| LaTeX note | `run_h10_tone_at_top.py` | ~523 |
| Turn uncertainty unwinsorized | `build_h10_tone_at_top_panel.py` | ~221 |

### Critical Artifacts

| Artifact | Purpose |
|----------|---------|
| `tone_at_top_panel.parquet` | Call-level data (112,968 rows) |
| `tone_at_top_turns_panel.parquet` | Turn-level data (1,697,632 rows) |
| `tone_at_top_full.tex` | Main results table |
| `coefficients_Main_M2_placebo_lead.csv` | Placebo test results |
| `reconciliation_table.csv` | Row count stages |

---

END OF PROMPT
