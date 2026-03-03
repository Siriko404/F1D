# Re-Verification Audit Report: Suite H9

**Date:** 2026-03-02
**Auditor:** Claude Opus 4.6 (AI)
**Input Documents:** H9.md, AUDIT_H9.md, Paper_Artifacts_Audit_H9.md
**Verification Method:** Manual one-by-one inspection per AUDIT_REVERIFICATION_PROMPT_H9.md

---

## Executive Summary

| Total Issues Verified | Confirmed Fixed | Confirmed Not Fixed | Documented/Accepted | Unverifiable |
|-----------------------|-----------------|---------------------|---------------------|--------------|
| 11 | 1 | 8 | 2 | 0 |

### Overall Assessment

Suite H9 has **ONE fix confirmed** (run_manifest.json generation) but **EIGHT critical issues remain unfixed**, including two BLOCKERs that invalidate the cause-specific Cox models. The Cox PH All model (using `Takeover` column) remains correctly implemented and trustworthy. The cause-specific models (Uninvited, Friendly) produce invalid results due to the event coding bug that inflates events by 8-9x.

### Trustworthy Results

- **Cox PH All:** YES - correctly implemented (event=1 only in last interval)
- **Cox CS Uninvited:** NO - event rows inflated 8.53x (648 rows vs 76 firms)
- **Cox CS Friendly:** NO - event rows inflated 9.19x (4,311 rows vs 469 firms)

---

## Claim Ledger

| ID | Severity | Claim | Fix Location | Original Status | Re-Verification Status |
|----|----------|-------|--------------|-----------------|------------------------|
| H9-001 | BLOCKER | Cause-specific event coding creates 8-9x inflated events | `run_h9_takeover_hazards.py:245-246` | CLAIMS NOT FIXED | **CONFIRMED NOT FIXED** |
| H9-002 | BLOCKER | Negative-duration intervals (8 rows with stop < start) | `build_h9_takeover_panel.py:384` | CLAIMS NOT FIXED | **CONFIRMED NOT FIXED** |
| H9-003 | MAJOR | Regime variant dead code in MODEL_VARIANTS | `run_h9_takeover_hazards.py:149-154` | CLAIMS NOT FIXED | **PARTIALLY FIXED** (skip warning added) |
| H9-004 | MAJOR | n_firms column mislabeled (is intervals) | `run_h9_takeover_hazards.py:479` | CLAIMS NOT FIXED | **CONFIRMED NOT FIXED** |
| H9-005 | MAJOR | LaTeX table SE formatting broken | `latex_tables_accounting.py` | CLAIMS NOT FIXED | **CONFIRMED NOT FIXED** |
| H9-006 | MAJOR | Missing PH diagnostics (Schoenfeld test) | `run_h9_takeover_hazards.py` | CLAIMS NOT FIXED | **CONFIRMED NOT FIXED** |
| H9-007 | MINOR | README event counts don't match panel | `README.md:561` | CLAIMS NOT FIXED | **CONFIRMED NOT FIXED** |
| H9-008 | MINOR | Summary stats reference missing variables | `run_h9_takeover_hazards.py:125-146` | CLAIMS NOT FIXED | **CONFIRMED NOT FIXED** |
| H9-009 | NOTE | Missing run_manifest.json | Stage 3 + Stage 4 | CLAIMS NOT FIXED | **CONFIRMED FIXED** |
| H9-010 | NOTE | ClarityCEO time-varying (expected) | H9.md documentation | DOCUMENTED | **NOT EXPLICITLY DOCUMENTED** |
| H9-011 | NOTE | Concordance near 0.5 (substantive) | N/A | DOCUMENTED | **NOT EXPLICITLY DOCUMENTED** |

---

## Verification Results

### H9-001: Cause-Specific Event Coding

**Claimed Status:** NOT FIXED
**Verification Steps:**
1. Read `run_h9_takeover_hazards.py` lines 245-246
2. Executed Python to verify event row inflation

**Evidence:**

Code at lines 245-246:
```python
df[EVENT_UNINVITED_COL] = (df["Takeover_Type"] == "Uninvited").astype(int)
df[EVENT_FRIENDLY_COL] = (df["Takeover_Type"] == "Friendly").astype(int)
```

Command executed:
```bash
python -c "...panel analysis..."
```

Raw output:
```
Panel: 2026-03-02_001100
Total rows: 21,666

Takeover:
  Event rows: 585
  Event firms: 585
  Ratio: 1.00

Takeover_Uninvited:
  Event rows: 648
  Event firms: 76
  Ratio: 8.53
  >>> BUG: Event rows inflated by 8.5x

Takeover_Friendly:
  Event rows: 4,311
  Event firms: 469
  Ratio: 9.19
  >>> BUG: Event rows inflated by 9.2x
```

**Verdict:** CONFIRMED NOT FIXED
**Rationale:** The code still uses `(df["Takeover_Type"] == "X")` without the `Takeover==1` condition, causing 8.53x inflation for Uninvited and 9.19x for Friendly.

---

### H9-002: Negative Duration Intervals

**Claimed Status:** NOT FIXED
**Verification Steps:**
1. Executed Python to check panel for negative durations
2. Searched source code for guard logic

**Evidence:**

Command executed:
```bash
python -c "...duration check..."
```

Raw output:
```
Panel: 2026-03-02_001100
Total rows: 27,787
Negative durations: 8
Zero durations: 6

Negative duration rows:
        gvkey  start  stop  Takeover Takeover_Type
464    001634   2007  2005         1          None
3758   005116   2007  2002         1          None
11231  013990   2003  2002         1          None
13489  022632   2007  2004         1          None
15454  025950   2003  2002         1          None
17323  030067   2012  2006         1          None
23781  145186   2013  2007         1          None
24323  151832   2007  2005         1          None
```

Code search:
```bash
grep -n "exit_year.*entry_year|takeover_year.*entry|valid.*firm_bounds" src/f1d/variables/build_h9_takeover_panel.py
# Output: 25:  - Duration = exit_year - entry_year + 1 (minimum 1)
# No guard code found
```

**Verdict:** CONFIRMED NOT FIXED
**Rationale:** 8 rows with negative durations still exist. No guard code in `build_h9_takeover_panel.py` to filter firms where takeover_year < entry_year.

---

### H9-003: Regime Variant Dead Code

**Claimed Status:** NOT FIXED
**Verification Steps:**
1. Read `run_h9_takeover_hazards.py` lines 149-154
2. Searched run log for Regime mentions

**Evidence:**

Code at lines 149-154:
```python
MODEL_VARIANTS: Dict[str, Dict[str, str]] = {
    "Regime": {
        "clarity_var": "ClarityManager",
        "uncertainty_var": "Manager_QA_Uncertainty_pct",
        "description": "Manager Clarity (4.1) model",
    },
    ...
}
```

Run log search:
```bash
grep -i "regime\|manager.*clarity" outputs/econometric/takeover/2026-03-02_003145/run_log.txt
```

Output:
```
  Cox TV: Cox PH All — Manager Clarity (4.1) model
  [Regime] Model not fitted — insufficient data
  Cox TV: Cox CS Uninvited — Manager Clarity (4.1) model
  [Regime] Model not fitted — insufficient data
  Cox TV: Cox CS Friendly — Manager Clarity (4.1) model
  [Regime] Model not fitted — insufficient data
```

**Verdict:** PARTIALLY FIXED
**Rationale:** Dead code still exists in MODEL_VARIANTS, but an explicit skip warning is now logged ("Model not fitted — insufficient data"). The Regime variant no longer silently fails.

---

### H9-004: n_firms Column Mislabeled

**Claimed Status:** NOT FIXED
**Verification Steps:**
1. Checked hazard_ratios.csv columns and values
2. Read source code at line 479

**Evidence:**

Command executed:
```bash
python -c "...hazard_ratios analysis..."
```

Output:
```
Latest run: 2026-03-02_003145
Columns: ['model', 'variant', 'event_type', 'variable', 'coef', 'exp_coef', 'se_coef', 'z', 'p', 'n_firms', 'n_events', 'concordance']

n_firms values: [12139]

WARNING: n_firms=12139 looks like N intervals, not N firms!
```

Code at line 479:
```python
"n_firms": df_clean_len,
```

**Verdict:** CONFIRMED NOT FIXED
**Rationale:** n_firms=12,139 is N intervals, not N firms (~1,623). No n_intervals column added.

---

### H9-005: LaTeX Table SE Formatting

**Claimed Status:** NOT FIXED
**Verification Steps:**
1. Read takeover_table.tex from latest run

**Evidence:**

File: `outputs/econometric/takeover/2026-03-02_003145/takeover_table.tex`

Lines 19-38:
```latex
Clarity (CEO) &  & 1.0497 &  & 1.3371 &  & 1.0978 \\
CEO QA Uncertainty &  & 1.2144 &  & 1.0029 &  & 0.9225 \\
...
Earnings Surprise Decile &  & 0.9715 &  & 0.9877 &  & 0.9956 \\
 &  & (0.0845) &  & (0.0915) &  & (0.0290) \\
 &  & (0.2890) &  & (0.3024) &  & (0.0975) \\
...
```

**Verdict:** CONFIRMED NOT FIXED
**Rationale:** All 10 SE rows are bunched together at lines 29-38, after all HR rows (lines 19-28). SEs should be interleaved below each corresponding HR.

---

### H9-006: Missing PH Diagnostics

**Claimed Status:** NOT FIXED
**Verification Steps:**
1. Searched for PH diagnostic files
2. Searched source code for PH test calls

**Evidence:**

File search:
```bash
find outputs/econometric/takeover -name "*ph*" -o -name "*schoenfeld*"
# No PH diagnostic files found (only cox_ph_*.txt model outputs)
```

Code search:
```bash
grep -n "proportional_hazard|schoenfeld|check_assumption|ph_test" src/f1d/econometric/run_h9_takeover_hazards.py
# No matches found
```

**Verdict:** CONFIRMED NOT FIXED
**Rationale:** No Schoenfeld test or PH diagnostics generated. No PH test code in source.

---

### H9-007: README Event Counts

**Claimed Status:** NOT FIXED
**Verification Steps:**
1. Read README.md line 561
2. Verified panel Takeover_Type distribution

**Evidence:**

README.md line 561:
```
Event breakdown: Friendly: 563, Uninvited: 87, Unknown: 40.
```

Panel verification:
```bash
python -c "...Takeover_Type distribution..."
```

Output:
```
Takeover_Type distribution (firm-level):
Takeover_Type
None         1753
Friendly      556
Uninvited      83
Unknown        37
```

**Verdict:** CONFIRMED NOT FIXED
**Rationale:** README claims Friendly=563, Uninvited=87, Unknown=40. Panel shows Friendly=556, Uninvited=83, Unknown=37. Discrepancy of 7+4+3=14 firms.

---

### H9-008: Summary Stats Missing Variables

**Claimed Status:** NOT FIXED
**Verification Steps:**
1. Read SUMMARY_STATS_VARS definition
2. Checked summary_stats.csv output

**Evidence:**

Code lines 125-146 includes:
```python
{"col": "ClarityManager", "label": "Clarity (Manager)"},  # Not in panel
{"col": "Manager_QA_Uncertainty_pct", "label": "Mgr QA Uncertainty"},
{"col": "duration", "label": "Duration (years)"},  # Never computed
```

Summary stats output (lines 2, 7-8):
```csv
All,Clarity (Manager),ClarityManager,0,,,,,,,
All,Uninvited Takeover,Takeover_Uninvited,"21,666",0.0299,0.1703,...
All,Friendly Takeover,Takeover_Friendly,"21,666",0.1990,0.3992,...
```

**Verdict:** CONFIRMED NOT FIXED
**Rationale:** Stale references to ClarityManager (N=0), missing duration column, and inflated Takeover_Uninvited/Friendly counts (due to H9-001 bug).

---

### H9-009: Missing Run Manifest

**Claimed Status:** NOT FIXED
**Verification Steps:**
1. Searched for run_manifest.json in Stage 3 and Stage 4 outputs

**Evidence:**

```bash
find outputs/variables/takeover -name "run_manifest.json"
# Output: outputs/variables/takeover/2026-03-02_001100/run_manifest.json

find outputs/econometric/takeover -name "run_manifest.json"
# Output: outputs/econometric/takeover/2026-03-01_232121/run_manifest.json
#         outputs/econometric/takeover/2026-03-02_003145/run_manifest.json
```

**Verdict:** CONFIRMED FIXED
**Rationale:** run_manifest.json files now exist in both Stage 3 and Stage 4 latest outputs.

---

### H9-010: ClarityCEO Time-Varying Documentation

**Claimed Status:** DOCUMENTED
**Verification Steps:**
1. Searched H9.md for explicit documentation

**Evidence:**

Search for "time-varying.*CEO|CEO.*turnover|varying.*turnover":
- No explicit documentation found explaining that ClarityCEO is time-varying across CEO turnovers

**Verdict:** NOT EXPLICITLY DOCUMENTED
**Rationale:** H9.md mentions "Cox PH (time-varying)" as model type but does not explicitly document that ClarityCEO varies within-firm across CEO turnovers (660 of 1,685 firms have varying ClarityCEO).

---

### H9-011: Concordance Near 0.5

**Claimed Status:** DOCUMENTED
**Verification Steps:**
1. Searched H9.md for discussion of low concordance

**Evidence:**

Search for "concordance.*0\\.5|discriminative|predictive power":
- Concordance values shown in verification output (0.537, 0.567, 0.522)
- No explicit discussion of low discriminative power as substantive finding

**Verdict:** NOT EXPLICITLY DOCUMENTED
**Rationale:** Concordance values are reported but not discussed as a substantive finding (models have essentially no discriminative power).

---

## Additional Findings

### New Issues Discovered

1. **Model-Family Specific Checks - PASS:**
   - Counting-process monotonicity: 0 gaps detected
   - Event-in-last-row (Takeover column): 0 violations
   - FF12 filter: Correctly applied at Stage 4 (Finance/Utility excluded from regression)

2. **Cross-Artifact Consistency - PASS:**
   - Raw txt output matches hazard_ratios.csv exactly
   - ClarityCEO HR=1.0497, p=0.566304, N events=349, Concordance=0.5371

3. **Stage 3 Panel Contains All FF12 Codes:**
   - Panel includes FF12 8 (Utility) and 11 (Finance)
   - Filter is correctly applied at Stage 4 runtime
   - This is expected behavior but worth noting

---

## Cross-Artifact Consistency Matrix

| Source | Field | Expected Value | Actual Value | Match? |
|--------|-------|----------------|--------------|--------|
| Raw cox_ph_all.txt | ClarityCEO HR | — | 1.049667 | — |
| hazard_ratios.csv | exp_coef | 1.049667 | 1.0497 | YES |
| LaTeX table | HR value | 1.0497 | 1.0497 | YES |
| Raw cox_ph_all.txt | N events | 349 | 349 | YES |
| model_diagnostics.csv | n_event_firms | 349 | 349 | YES |
| Raw cox_ph_all.txt | Concordance | 0.5371 | 0.5371 | YES |
| hazard_ratios.csv | concordance | 0.5371 | 0.5371 | YES |

---

## Model-Family Specific Checks

| Check | Result | Evidence |
|-------|--------|----------|
| Counting-process monotonicity (no gaps) | PASS | 0 firms with gaps |
| Event=1 only in last interval (Takeover) | PASS | 0 firms with multiple event rows |
| FF12 filter (exclude 8, 11) | PASS | Applied at Stage 4, 21,666 Main sample rows |
| Negative durations | FAIL | 8 rows with stop < start |
| Zero durations | NOTE | 6 rows with stop == start |

---

## Recommendations

### Priority 1 - BLOCKERs (Must Fix Before Any Results Used)

1. **H9-001: Fix cause-specific event coding**
   ```python
   # run_h9_takeover_hazards.py:245-246
   # CURRENT (BUG):
   df[EVENT_UNINVITED_COL] = (df["Takeover_Type"] == "Uninvited").astype(int)
   df[EVENT_FRIENDLY_COL] = (df["Takeover_Type"] == "Friendly").astype(int)

   # FIXED:
   df[EVENT_UNINVITED_COL] = ((df[EVENT_ALL_COL] == 1) & (df["Takeover_Type"] == "Uninvited")).astype(int)
   df[EVENT_FRIENDLY_COL] = ((df[EVENT_ALL_COL] == 1) & (df["Takeover_Type"] == "Friendly")).astype(int)
   ```
   - **Rerun:** Stage 4 only

2. **H9-002: Filter negative duration firms**
   - Add guard in `build_h9_takeover_panel.py` after line 386
   - **Rerun:** Stage 3 + Stage 4

### Priority 2 - MAJOR (Required for Paper Submission)

3. **H9-004: Rename n_firms to n_intervals, add true n_firms**
   - **Rerun:** Stage 4 only

4. **H9-005: Fix LaTeX SE interleaving**
   - Modify `make_cox_hazard_table` in `latex_tables_accounting.py`
   - **Rerun:** Stage 4 only

5. **H9-006: Add PH diagnostics**
   - Add `proportional_hazard_test` after model fitting
   - **Rerun:** Stage 4 only

6. **H9-003: Remove Regime variant dead code**
   - Delete Regime entry from MODEL_VARIANTS
   - **Rerun:** None (code-only fix)

### Priority 3 - MINOR (Quality Improvements)

7. **H9-007: Update README event counts**
   - **Rerun:** None (documentation only)

8. **H9-008: Clean up SUMMARY_STATS_VARS**
   - Remove stale references, add duration computation
   - **Rerun:** Stage 4 only

---

## Command Log

| # | Timestamp | Command | Purpose |
|---|-----------|---------|---------|
| 1 | 2026-03-02 | `grep -n "Takeover_Uninvited\|..." run_h9_takeover_hazards.py` | Find event coding lines |
| 2 | 2026-03-02 | `python -c "panel analysis..."` | Verify event row inflation |
| 3 | 2026-03-02 | `python -c "duration check..."` | Check negative durations |
| 4 | 2026-03-02 | `grep -n "exit_year.*entry_year..." build_h9_takeover_panel.py` | Search for guard code |
| 5 | 2026-03-02 | `grep -n "MODEL_VARIANTS\|Regime..." run_h9_takeover_hazards.py` | Check MODEL_VARIANTS |
| 6 | 2026-03-02 | `grep -i "regime..." run_log.txt` | Check run log for Regime |
| 7 | 2026-03-02 | `python -c "hazard_ratios analysis..."` | Check n_firms column |
| 8 | 2026-03-02 | `cat takeover_table.tex` | Check LaTeX SE formatting |
| 9 | 2026-03-02 | `find outputs/... -name "*ph*"` | Search for PH diagnostics |
| 10 | 2026-03-02 | `grep -n "proportional_hazard..." run_h9_takeover_hazards.py` | Check for PH test code |
| 11 | 2026-03-02 | `grep -n "Event breakdown" README.md` | Check README event counts |
| 12 | 2026-03-02 | `python -c "Takeover_Type distribution..."` | Verify panel event counts |
| 13 | 2026-03-02 | `find outputs/... -name "run_manifest.json"` | Check for manifests |
| 14 | 2026-03-02 | `python -c "cross-artifact consistency..."` | Verify HR consistency |
| 15 | 2026-03-02 | `python -c "model-family checks..."` | Survival-specific checks |
| 16 | 2026-03-02 | `git log --oneline --since="2026-03-01" ...` | Check for recent commits |
| 17 | 2026-03-02 | `cat model_diagnostics.csv` | Verify model diagnostics |
| 18 | 2026-03-02 | `cat cox_ph_all.txt` | Verify raw model output |
| 19 | 2026-03-02 | `cat summary_stats.csv` | Check summary stats |

---

## Appendix: Raw Evidence

### A. Event Row Inflation (H9-001)

```
Panel: 2026-03-02_001100
Total rows: 21,666

Takeover:
  Event rows: 585
  Event firms: 585
  Ratio: 1.00

Takeover_Uninvited:
  Event rows: 648
  Event firms: 76
  Ratio: 8.53
  >>> BUG: Event rows inflated by 8.5x

Takeover_Friendly:
  Event rows: 4,311
  Event firms: 469
  Ratio: 9.19
  >>> BUG: Event rows inflated by 9.2x
```

### B. Negative Duration Rows (H9-002)

```
gvkey  start  stop  dur   Takeover  Takeover_Type
001634  2007  2005   -2        1           None
005116  2007  2002   -5        1           None
013990  2003  2002   -1        1           None
022632  2007  2004   -3        1           None
025950  2003  2002   -1        1           None
030067  2012  2006   -6        1           None
145186  2013  2007   -6        1           None
151832  2007  2005   -2        1           None
```

### C. Model Diagnostics (Latest Run)

```
model,variant,event_type,event_col,n_intervals,n_event_firms,n_clusters,cluster_var,concordance
Cox PH All,CEO,All,Takeover,12139,349,1322,gvkey,0.5371124820548636
Cox CS Uninvited,CEO,Uninvited,Takeover_Uninvited,12139,45,1322,gvkey,0.5673015193665739
Cox CS Friendly,CEO,Friendly,Takeover_Friendly,12139,346,1322,gvkey,0.5224718025315486
```

---

**Document Generated:** 2026-03-02
**Panel Audited:** `outputs/variables/takeover/2026-03-02_001100/takeover_panel.parquet`
**Regression Audited:** `outputs/econometric/takeover/2026-03-02_003145/`
**Audit Protocol:** `docs/provenance/AUDIT_REVERIFICATION_PROMPT_H9.md`
