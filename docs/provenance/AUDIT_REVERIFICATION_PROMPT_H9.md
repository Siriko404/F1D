# Audit Re-Verification Prompt: Suite H9 (Takeover Hazards)

**Purpose:** This prompt instructs an AI auditor to re-verify all claimed issues from prior audits against the current codebase and output artifacts.

**Target Suite:** H9 — CEO Clarity and Takeover Hazards
**Input Documents:**
- `docs/provenance/H9.md` (Provenance documentation)
- `docs/provenance/AUDIT_H9.md` (Adversarial implementation audit)
- `docs/provenance/Paper_Artifacts_Audit_H9.md` (Paper-submission readiness audit)

**Output Deliverable:** `docs/provenance/AUDIT_REVERIFICATION_H9.md`

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
| **Line numbers** | Specific lines read (e.g., "lines 240-241") |
| **Command executed** | Literal command with all flags |
| **Raw output** | Exact output received (truncate if long, but show key parts) |
| **Timestamp check** | Modification time of files (if relevant to "was this fixed?") |
| **Cross-reference** | At least 2 independent sources for critical claims |

---

## PART 2: CLAIM LEDGER EXTRACTION

### 2.1 Issue Register (Extract from AUDIT_H9.md)

| ID | Severity | Description | Claimed Fix | Status Claimed |
|----|----------|-------------|-------------|----------------|
| H9-AUDIT-001 | BLOCKER | Cause-specific event coding creates phantom recurrent events | Change lines 240-241 to use `((Takeover==1) & (Type==X))` | NOT FIXED |
| H9-AUDIT-002 | BLOCKER | Negative-duration intervals in panel (8 rows with stop < start) | Filter firms where takeover_year < entry_year | NOT FIXED |
| H9-AUDIT-003 | MAJOR | Regime variant dead code in MODEL_VARIANTS | Remove or add explicit skip warning | NOT FIXED |
| H9-AUDIT-004 | MAJOR | n_firms column mislabeled (contains intervals, not firms) | Rename to n_intervals, add true n_firms | NOT FIXED |
| H9-AUDIT-005 | MAJOR | LaTeX table SE formatting broken (bunched at bottom) | Fix make_cox_hazard_table | NOT FIXED |
| H9-AUDIT-006 | MINOR | README event counts don't match panel | Update README | NOT FIXED |
| H9-AUDIT-007 | MINOR | Summary stats reference missing variables | Remove stale refs, add duration | NOT FIXED |
| H9-AUDIT-008 | NOTE | ClarityCEO is time-varying across CEO turnovers | Document as expected behavior | DOCUMENTED |
| H9-AUDIT-009 | NOTE | Concordance indices near 0.5 | N/A (substantive finding) | DOCUMENTED |

### 2.2 Issue Register (Extract from Paper_Artifacts_Audit_H9.md)

| ID | Severity | Description | Claimed Fix | Status Claimed |
|----|----------|-------------|-------------|----------------|
| H9-PAPER-001 | BLOCKER | Cause-specific event coding bug (duplicate) | Same as H9-AUDIT-001 | NOT FIXED |
| H9-PAPER-002 | BLOCKER | Negative durations (duplicate) | Same as H9-AUDIT-002 | NOT FIXED |
| H9-PAPER-003 | MAJOR | Missing PH diagnostics (Schoenfeld test) | Add proportional_hazard_test | NOT FIXED |
| H9-PAPER-004 | MAJOR | LaTeX SE formatting (duplicate) | Same as H9-AUDIT-005 | NOT FIXED |
| H9-PAPER-005 | MAJOR | n_firms mislabeled (duplicate) | Same as H9-AUDIT-004 | NOT FIXED |
| H9-PAPER-006 | MAJOR | Regime variant dead code (duplicate) | Same as H9-AUDIT-003 | NOT FIXED |
| H9-PAPER-007 | MINOR | README counts (duplicate) | Same as H9-AUDIT-006 | NOT FIXED |
| H9-PAPER-008 | MINOR | Summary stats gaps (duplicate) | Same as H9-AUDIT-007 | NOT FIXED |
| H9-PAPER-009 | NOTE | Low concordance (duplicate) | N/A | DOCUMENTED |
| H9-PAPER-010 | NOTE | ClarityCEO time-varying (duplicate) | N/A | DOCUMENTED |
| H9-PAPER-011 | NOTE | Missing run_manifest.json | Add manifest generation | NOT FIXED |

### 2.3 Consolidated Claim Ledger

| ID | Severity | Claim | Fix Location | Audit Status Claimed |
|----|----------|-------|--------------|---------------------|
| H9-001 | BLOCKER | Cause-specific event coding creates 8-9x inflated events | `run_h9_takeover_hazards.py:240-241` | CLAIMS NOT FIXED |
| H9-002 | BLOCKER | Negative-duration intervals (8 rows with stop < start) | `build_h9_takeover_panel.py:384` | CLAIMS NOT FIXED |
| H9-003 | MAJOR | Regime variant dead code in MODEL_VARIANTS | `run_h9_takeover_hazards.py:144-155` | CLAIMS NOT FIXED |
| H9-004 | MAJOR | n_firms column mislabeled (is intervals) | `run_h9_takeover_hazards.py:472` | CLAIMS NOT FIXED |
| H9-005 | MAJOR | LaTeX table SE formatting broken | `latex_tables_accounting.py` | CLAIMS NOT FIXED |
| H9-006 | MAJOR | Missing PH diagnostics (Schoenfeld test) | `run_h9_takeover_hazards.py` | CLAIMS NOT FIXED |
| H9-007 | MINOR | README event counts don't match panel | `README.md:559` | CLAIMS NOT FIXED |
| H9-008 | MINOR | Summary stats reference missing variables | `run_h9_takeover_hazards.py:120-141` | CLAIMS NOT FIXED |
| H9-009 | NOTE | Missing run_manifest.json | Stage 3 + Stage 4 | CLAIMS NOT FIXED |
| H9-010 | NOTE | ClarityCEO time-varying (expected) | H9.md documentation | DOCUMENTED |
| H9-011 | NOTE | Concordance near 0.5 (substantive) | N/A | DOCUMENTED |

---

## PART 3: VERIFICATION PROCEDURES (Execute One-by-One)

### 3.1 Verification of H9-001: Cause-Specific Event Coding (BLOCKER)

**Background:** The cause-specific event indicators (`Takeover_Uninvited`, `Takeover_Friendly`) are coded from `Takeover_Type` alone, setting event=1 for ALL intervals of type-matching firms, not just the final interval. This inflates events by 8-9x.

**Claimed Fix:** Change lines 240-241 to use `((Takeover==1) & (Type==X))`.

#### Step 3.1.1: Verify Code Implementation

Execute EXACTLY:

```bash
# Read lines 235-245 of run_h9_takeover_hazards.py
grep -n "Takeover_Uninvited\|Takeover_Friendly\|EVENT_UNINVITED\|EVENT_FRIENDLY" src/f1d/econometric/run_h9_takeover_hazards.py
```

**Evidence to Record:**
- [ ] Exact code at lines 240-241
- [ ] Whether `Takeover==1` condition is included
- [ ] Whether the bug pattern `(df["Takeover_Type"] == "X").astype(int)` is still present

#### Step 3.1.2: Verify Event Row Inflation

Execute EXACTLY:

```python
import pandas as pd
from pathlib import Path

# Load latest Stage 4 output
econ_dir = Path('outputs/econometric/takeover')
subdirs = sorted([d for d in econ_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]

# Load panel
panel_path = latest / 'h9_panel_used.parquet'  # If saved
# Or load from Stage 3 and trace the logic

# For now, check model_diagnostics for event counts
diag = pd.read_csv(latest / 'model_diagnostics.csv')
print(diag[['model', 'n_event_firms']])

# Check raw output files for evidence of inflation
# Read cox_cs_uninvited.txt and check N_events
```

**Evidence to Record:**
- [ ] n_event_firms for each model
- [ ] Whether Uninvited shows 45 events or fewer (corrected)
- [ ] Any evidence of inflated event counts in raw outputs

#### Step 3.1.3: Verdict for H9-001

- [ ] **CONFIRMED FIXED** — Code now uses `((Takeover==1) & (Type==X))`
- [ ] **CONFIRMED NOT FIXED** — Original bug still present
- [ ] **PARTIALLY FIXED** — Some change but still problematic
- [ ] **UNVERIFIABLE** — Cannot determine (explain why)

---

### 3.2 Verification of H9-002: Negative Duration Intervals (BLOCKER)

**Background:** 8 rows in the counting-process panel have `stop < start`, meaning negative durations. These represent firms taken over before sample entry.

**Claimed Fix:** Filter firms where `takeover_year < entry_year` in `build_h9_takeover_panel.py:384`.

#### Step 3.2.1: Check Panel for Negative Durations

Execute EXACTLY:

```python
import pandas as pd
from pathlib import Path

panel_dir = Path('outputs/variables/takeover')
subdirs = sorted([d for d in panel_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]
panel = pd.read_parquet(latest / 'takeover_panel.parquet')

# Check for negative durations
durations = panel['stop'] - panel['start']
neg_count = (durations < 0).sum()
zero_count = (durations == 0).sum()

print(f'Panel: {latest.name}')
print(f'Total rows: {len(panel):,}')
print(f'Negative durations: {neg_count}')
print(f'Zero durations: {zero_count}')

if neg_count > 0:
    print('\nNegative duration rows:')
    neg_rows = panel[durations < 0]
    print(neg_rows[['gvkey', 'start', 'stop', 'Takeover', 'Takeover_Type']].to_string())
```

**Evidence to Record:**
- [ ] Count of negative durations (should be 0 if fixed)
- [ ] Count of zero durations
- [ ] Sample of any problematic rows

#### Step 3.2.2: Check Source Code for Guard

Execute EXACTLY:

```bash
grep -n "exit_year.*entry_year\|takeover_year.*entry\|valid.*firm_bounds" src/f1d/variables/build_h9_takeover_panel.py
```

**Evidence to Record:**
- [ ] Whether guard code exists
- [ ] Exact implementation if present

#### Step 3.2.3: Verdict for H9-002

- [ ] **CONFIRMED FIXED** — No negative durations in panel
- [ ] **CONFIRMED NOT FIXED** — Negative durations still present
- [ ] **PARTIALLY FIXED** — Fewer but some remain
- [ ] **UNVERIFIABLE** — Cannot determine

---

### 3.3 Verification of H9-003: Regime Variant Dead Code (MAJOR)

**Background:** `MODEL_VARIANTS` still contains "Regime" entry with `ClarityManager`, but ClarityManager is not in the panel. The variant silently produces nothing.

**Claimed Fix:** Remove Regime entry or add explicit skip warning.

#### Step 3.3.1: Check MODEL_VARIANTS Definition

Execute EXACTLY:

```bash
# Read lines 140-160
grep -n "MODEL_VARIANTS\|Regime\|ClarityManager" src/f1d/econometric/run_h9_takeover_hazards.py | head -20
```

**Evidence to Record:**
- [ ] Whether "Regime" entry exists in MODEL_VARIANTS
- [ ] Whether skip warning logic exists

#### Step 3.3.2: Check Run Log for Regime Processing

Execute EXACTLY:

```bash
# Find latest run_log.txt
ls -lt outputs/econometric/takeover/*/run_log.txt | head -1

# Search for Regime mentions
grep -i "regime\|manager.*clarity" outputs/econometric/takeover/*/run_log.txt
```

**Evidence to Record:**
- [ ] Whether Regime variant is mentioned in run log
- [ ] Whether any warning is logged

#### Step 3.3.3: Verdict for H9-003

- [ ] **CONFIRMED FIXED** — Regime removed or explicit skip logged
- [ ] **CONFIRMED NOT FIXED** — Dead code still present, silent skip
- [ ] **N/A** — Different solution implemented

---

### 3.4 Verification of H9-004: n_firms Column Mislabeled (MAJOR)

**Background:** The `n_firms` column in `hazard_ratios.csv` contains N intervals (12,139), not N firms (~1,623).

**Claimed Fix:** Rename to `n_intervals`, add true `n_firms` field.

#### Step 3.4.1: Check hazard_ratios.csv

Execute EXACTLY:

```python
import pandas as pd
from pathlib import Path

econ_dir = Path('outputs/econometric/takeover')
subdirs = sorted([d for d in econ_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]
hr = pd.read_csv(latest / 'hazard_ratios.csv')

print(f'Columns: {list(hr.columns)}')
print(f'\nn_firms values: {hr["n_firms"].unique() if "n_firms" in hr.columns else "N/A"}')
print(f'n_intervals values: {hr["n_intervals"].unique() if "n_intervals" in hr.columns else "N/A"}')

# Sanity check: n_firms should be ~1600, not ~12000
if 'n_firms' in hr.columns:
    val = hr['n_firms'].iloc[0]
    if val > 5000:
        print(f'\nWARNING: n_firms={val} looks like N intervals, not N firms!')
```

**Evidence to Record:**
- [ ] Whether `n_intervals` column exists
- [ ] Value of n_firms (should be ~1,600)
- [ ] Whether the mislabeling persists

#### Step 3.4.2: Check Source Code

Execute EXACTLY:

```bash
grep -n "n_firms\|n_intervals\|df_clean_len" src/f1d/econometric/run_h9_takeover_hazards.py | head -20
```

**Evidence to Record:**
- [ ] Exact code at line 472
- [ ] Whether gvkey.nunique() is now used

#### Step 3.4.3: Verdict for H9-004

- [ ] **CONFIRMED FIXED** — n_firms now reports actual firm count
- [ ] **CONFIRMED NOT FIXED** — Still mislabeled as intervals
- [ ] **PARTIALLY FIXED** — Different solution

---

### 3.5 Verification of H9-005: LaTeX Table SE Formatting (MAJOR)

**Background:** In `takeover_table.tex`, all SE rows are bunched together after all HR rows, instead of interleaved.

**Claimed Fix:** Fix `make_cox_hazard_table` in `latex_tables_accounting.py`.

#### Step 3.5.1: Read LaTeX Table

Execute EXACTLY:

```bash
# Find latest takeover_table.tex
ls -lt outputs/econometric/takeover/*/takeover_table.tex | head -1

# Read lines 15-40 (table body)
head -50 outputs/econometric/takeover/*/takeover_table.tex | tail -35
```

**Evidence to Record:**
- [ ] Structure of HR and SE rows
- [ ] Whether SEs are interleaved or bunched

#### Step 3.5.2: Check Source Code

Execute EXACTLY:

```bash
grep -n "make_cox_hazard_table\|fmt_coef\|SE.*row\|se_row" src/f1d/shared/latex_tables_accounting.py
```

**Evidence to Record:**
- [ ] How SE rows are generated
- [ ] Whether interleaving logic exists

#### Step 3.5.3: Verdict for H9-005

- [ ] **CONFIRMED FIXED** — SEs interleaved below each HR
- [ ] **CONFIRMED NOT FIXED** — SEs still bunched at bottom
- [ ] **UNVERIFIABLE** — Cannot determine

---

### 3.6 Verification of H9-006: Missing PH Diagnostics (MAJOR)

**Background:** No Schoenfeld residual test or PH assumption diagnostics are generated.

**Claimed Fix:** Add `proportional_hazard_test` after model fitting.

#### Step 3.6.1: Check for PH Diagnostic Files

Execute EXACTLY:

```bash
# Check if PH diagnostics exist
find outputs/econometric/takeover -name "*ph*" -o -name "*schoenfeld*" 2>/dev/null

ls outputs/econometric/takeover/*/ph_diagnostics.csv 2>/dev/null
ls outputs/econometric/takeover/*/schoenfeld*.csv 2>/dev/null
```

**Evidence to Record:**
- [ ] Whether ph_diagnostics.csv exists
- [ ] Whether any PH test output exists

#### Step 3.6.2: Check Source Code

Execute EXACTLY:

```bash
grep -n "proportional_hazard\|schoenfeld\|check_assumption\|ph_test" src/f1d/econometric/run_h9_takeover_hazards.py
```

**Evidence to Record:**
- [ ] Whether PH test code exists
- [ ] Whether it's called after model fitting

#### Step 3.6.3: Verdict for H9-006

- [ ] **CONFIRMED FIXED** — PH diagnostics now generated
- [ ] **CONFIRMED NOT FIXED** — Still missing
- [ ] **UNVERIFIABLE** — Cannot determine

---

### 3.7 Verification of H9-007: README Event Counts (MINOR)

**Background:** README claims Friendly=563, Uninvited=87, Unknown=40 but panel shows Friendly=556, Uninvited=83, Unknown=37.

#### Step 3.7.1: Check README

Execute EXACTLY:

```bash
grep -n "Friendly.*563\|Uninvited.*87\|Unknown.*40" README.md
grep -n "Event breakdown" README.md
```

**Evidence to Record:**
- [ ] Current README values
- [ ] Whether they match panel

#### Step 3.7.2: Verify Panel Values

Execute EXACTLY:

```python
import pandas as pd
from pathlib import Path

panel_dir = Path('outputs/variables/takeover')
subdirs = sorted([d for d in panel_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]
panel = pd.read_parquet(latest / 'takeover_panel.parquet')

print('Takeover_Type distribution (firm-level):')
print(panel.drop_duplicates('gvkey')['Takeover_Type'].value_counts())
```

#### Step 3.7.3: Verdict for H9-007

- [ ] **CONFIRMED FIXED** — README now matches panel
- [ ] **CONFIRMED NOT FIXED** — Discrepancy persists
- [ ] **N/A** — Issue no longer relevant

---

### 3.8 Verification of H9-008: Summary Stats Missing Variables (MINOR)

**Background:** `SUMMARY_STATS_VARS` references `duration`, `ClarityManager`, `Manager_QA_Uncertainty_pct` which may not exist.

#### Step 3.8.1: Check Source Code

Execute EXACTLY:

```bash
grep -n "SUMMARY_STATS_VARS\|duration\|ClarityManager" src/f1d/econometric/run_h9_takeover_hazards.py | head -30
```

#### Step 3.8.2: Check Summary Stats Output

Execute EXACTLY:

```python
import pandas as pd
from pathlib import Path

econ_dir = Path('outputs/econometric/takeover')
subdirs = sorted([d for d in econ_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]
ss = pd.read_csv(latest / 'summary_stats.csv')

print(f'Variables in summary_stats.csv:')
print(ss['variable'].tolist())
print(f'\nDuration present: {"duration" in ss["variable"].values}')
```

#### Step 3.8.3: Verdict for H9-008

- [ ] **CONFIRMED FIXED** — Stale refs removed, duration added
- [ ] **CONFIRMED NOT FIXED** — Still has stale refs
- [ ] **N/A** — Different solution

---

### 3.9 Verification of H9-009: Missing Run Manifest (NOTE)

**Background:** No `run_manifest.json` with git commit, timestamps, input hashes.

#### Step 3.9.1: Check for Manifest Files

Execute EXACTLY:

```bash
find outputs/variables/takeover -name "run_manifest.json" 2>/dev/null
find outputs/econometric/takeover -name "run_manifest.json" 2>/dev/null
```

#### Step 3.9.2: Verdict for H9-009

- [ ] **CONFIRMED FIXED** — Manifests now generated
- [ ] **CONFIRMED NOT FIXED** — Still missing

---

### 3.10 Verification of H9-010 & H9-011: Documented Issues (NOTE)

These are documentation-only issues:
- H9-010: ClarityCEO time-varying across CEO turnovers (expected behavior)
- H9-011: Concordance near 0.5 (substantive finding, not a bug)

Just verify they are documented in H9.md.

#### Verdict

- [ ] **CONFIRMED DOCUMENTED** — Mentioned in provenance
- [ ] **NOT DOCUMENTED** — Should be added

---

## PART 4: ADDITIONAL ADVERSARIAL CHECKS

### 4.1 Check for New Regressions

```bash
# Compare file modification times to audit dates
# Initial audit: 2026-03-01
# Check if files were modified AFTER this date
git log --oneline --since="2026-03-01" -- src/f1d/econometric/run_h9_takeover_hazards.py
git log --oneline --since="2026-03-01" -- src/f1d/variables/build_h9_takeover_panel.py
```

### 4.2 Cross-Artifact Consistency Deep Dive

Pick ONE model (Cox PH All) and verify:

| Source | Field | Expected Value | Actual Value | Match? |
|--------|-------|----------------|--------------|--------|
| Raw .txt | ClarityCEO HR | — | — | — |
| hazard_ratios.csv | exp_coef | — | — | — |
| LaTeX table | HR value | — | — | — |
| Raw .txt | N events | 349 | — | — |
| model_diagnostics.csv | n_event_firms | 349 | — | — |

### 4.3 Model-Family Specific Checks (Survival)

```python
import pandas as pd
from pathlib import Path

panel_dir = Path('outputs/variables/takeover')
subdirs = sorted([d for d in panel_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]
panel = pd.read_parquet(latest / 'takeover_panel.parquet')

# 1. Counting-process monotonicity (no gaps)
for gvkey, group in panel.groupby('gvkey'):
    if len(group) > 1:
        group = group.sort_values('start')
        gaps = group['start'].iloc[1:].values != group['stop'].iloc[:-1].values
        if gaps.any():
            print(f'Gap detected in gvkey={gvkey}')
            break

# 2. Event=1 only in last interval (for Takeover column)
event_firms = panel[panel['Takeover'] == 1]['gvkey'].unique()
for gvkey in event_firms[:5]:  # Check first 5
    firm_data = panel[panel['gvkey'] == gvkey].sort_values('stop')
    events = firm_data[firm_data['Takeover'] == 1]
    if len(events) > 1:
        print(f'WARNING: {gvkey} has {len(events)} event rows')

# 3. Sample filter check
ff12_counts = panel['ff12_code'].value_counts().sort_index()
print('FF12 distribution:')
print(ff12_counts)
print(f'\nFinance (11) present: {11 in ff12_counts}')
print(f'Utility (8) present: {8 in ff12_counts}')
```

---

## PART 5: OUTPUT FORMAT

Your output document must be written to:
`docs/provenance/AUDIT_REVERIFICATION_H9.md`

### Required Sections

```markdown
# Re-Verification Audit Report: Suite H9

**Date:** [TODAY'S DATE]
**Auditor:** [AI Model + Version]
**Input Documents:** H9.md, AUDIT_H9.md, Paper_Artifacts_Audit_H9.md
**Verification Method:** Manual one-by-one inspection per AUDIT_REVERIFICATION_PROMPT_H9.md

---

## Executive Summary

| Total Issues Verified | Confirmed Fixed | Confirmed Not Fixed | Documented/Accepted | Unverifiable |
|-----------------------|-----------------|---------------------|---------------------|--------------|
| X | Y | Z | A | B |

### Overall Assessment
[2-3 sentences on the state of the suite]

### Trustworthy Results
- **Cox PH All:** [YES/NO/PARTIAL]
- **Cox CS Uninvited:** [YES/NO/PARTIAL]
- **Cox CS Friendly:** [YES/NO/PARTIAL]

---

## Claim Ledger

[Copy from Part 2.3 with updated status]

---

## Verification Results

### H9-001: Cause-Specific Event Coding
**Claimed Status:** NOT FIXED
**Verification Steps:** [List steps performed]
**Evidence:**
- [Exact commands and outputs]
**Verdict:** [CONFIRMED FIXED / NOT FIXED / etc.]
**Rationale:** [1-2 sentences]

### H9-002: Negative Duration Intervals
[Same format]

### H9-003: Regime Variant Dead Code
[Same format]

[... continue for all issues ...]

---

## Additional Findings

[List any new issues discovered during verification]

---

## Cross-Artifact Consistency Matrix

[Table from 4.2]

---

## Model-Family Specific Checks

[Results from 4.3]

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
- [ ] My output document is saved to `docs/provenance/AUDIT_REVERIFICATION_H9.md`

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

## PART 7: H9-SPECIFIC VERIFICATION NOTES

### Survival Analysis Model Family

H9 uses `lifelines.CoxTimeVaryingFitter` which is fundamentally different from PanelOLS:

1. **No within-transformation** — PH assumption handles time-invariance
2. **Counting-process format** — (start, stop, event) tuples, one row per firm-year
3. **Event semantics** — For single-event models, event=1 should appear only in the LAST interval per firm
4. **Cause-specific models** — Events of other causes are censored at event time

### Key Files

| File | Purpose |
|------|---------|
| `build_h9_takeover_panel.py` | Stage 3: Builds counting-process panel |
| `run_h9_takeover_hazards.py` | Stage 4: Fits Cox models |
| `takeover_indicator.py` | SDC CUSIP matching and attitude classification |
| `latex_tables_accounting.py` | LaTeX table generation (SE formatting bug) |

### Critical Code Locations

| Issue | File | Line(s) |
|-------|------|---------|
| Cause-specific bug | `run_h9_takeover_hazards.py` | 240-241 |
| Negative durations | `build_h9_takeover_panel.py` | 384 |
| MODEL_VARIANTS | `run_h9_takeover_hazards.py` | 144-155 |
| n_firms column | `run_h9_takeover_hazards.py` | 472 |
| SE formatting | `latex_tables_accounting.py` | make_cox_hazard_table |

---

END OF PROMPT
