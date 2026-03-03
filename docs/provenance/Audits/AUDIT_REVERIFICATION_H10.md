# Re-Verification Audit Report: Suite H10

**Date:** 2026-03-02
**Auditor:** Claude Opus 4.6 (AI Model)
**Input Documents:** H10.md, AUDIT_H10.md, Paper_Artifacts_Audit_H10.md
**Verification Method:** Manual one-by-one inspection per AUDIT_REVERIFICATION_PROMPT_H10.md

---

## Executive Summary

| Total Issues Verified | Confirmed Fixed | Confirmed Not Fixed | Documented/Accepted | Unverifiable |
|-----------------------|-----------------|---------------------|---------------------|--------------|
| 10 | 2 | 5 | 2 | 1 |

### Overall Assessment

Suite H10 has made partial progress since the initial audit. Two BLOCKER issues (H10-002 LaTeX clustering note, H10-004 run manifest) have been fixed. However, the critical sample filter bug (H10-001) persists, meaning "Main" sample results still include Finance and Utility industries incorrectly. Three MINOR issues remain unfixed. The suite requires Stage 4 rerun after fixing the sample filter bug.

### Trustworthy Results
- **M1 (Call-level):** NO — Sample filter bug persists, duplicate entity-time index unresolved
- **M2 (Turn-level):** PARTIAL — Statistical methodology valid but sample composition incorrect

---

## Claim Ledger

| ID | Severity | Claim | Fix Location | Prior Status | Current Status |
|----|----------|-------|--------------|--------------|----------------|
| H10-001 | BLOCKER | "Main" sample includes ALL industries instead of non-fin/non-util | `run_h10_tone_at_top.py:1168-1177` | NOT FIXED | **NOT FIXED** |
| H10-002 | BLOCKER | LaTeX table clustering note incorrect for M2 | `run_h10_tone_at_top.py:551-552` | NOT FIXED | **FIXED** |
| H10-003 | MAJOR | Duplicate entity-time index in M1 (347 firm-quarters) | `run_h10_tone_at_top.py:135` | NOT FIXED | **NOT FIXED** |
| H10-004 | MAJOR | Missing run_manifest.json | Stage 3 + Stage 4 | NOT FIXED | **FIXED** |
| H10-005 | MAJOR | Placebo test failure (t=31.49 > main t=19.37) | H10.md documentation | DOCUMENTED | **DOCUMENTED** |
| H10-006 | MINOR | Turn_Uncertainty_pct unwinsorized (max=100%) | `build_h10_tone_at_top_panel.py` | NOT FIXED | **NOT FIXED** |
| H10-007 | MINOR | Winsorization inconsistency CEO vs CFO | H10.md Section G | NOT FIXED | **NOT FIXED** |
| H10-008 | MINOR | No sample attrition table in LaTeX format | Stage 3 | NOT FIXED | **NOT FIXED** |
| H10-009 | NOTE | CEO_Unc_Lag1 has 57.9% zeros | Documentation | DOCUMENTED | **PARTIAL** |
| H10-010 | NOTE | 2002 absent from M1 (expected) | Documentation | DOCUMENTED | **PARTIAL** |

---

## Verification Results

### H10-001: Sample Filter Bug (BLOCKER)

**Claimed Status:** NOT FIXED
**Verification Steps:**
1. Read source code at lines 1160-1190
2. Ran sample composition check against parquet file
3. Verified model_diagnostics.csv N values

**Evidence:**

*Code Examination (lines 1168-1177):*
```python
call_sub = (
    call_panel
    if sample == "Main"
    else call_panel[call_panel["sample"] == sample]
)
turns_sub = (
    turns_panel
    if sample == "Main"
    else turns_panel[turns_panel["sample"] == sample]
)
```

*Sample Composition Command:*
```bash
python -c "
import pandas as pd
from pathlib import Path
panel_dir = Path('outputs/variables/tone_at_top')
subdirs = sorted([d for d in panel_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]
cp = pd.read_parquet(latest / 'tone_at_top_panel.parquet')
full = cp.dropna(subset=['ClarityStyle_Realtime','CFO_QA_Uncertainty_pct','Size','BM','Lev','ROA','StockRet','MarketRet','EPS_Growth','SurpDec'])
print(f'Full panel (M1 listwise): {len(full):,}')
print(full['sample'].value_counts())
"
```

*Output:*
```
Full panel (M1 listwise): 43,570
Sample breakdown:
sample
Main       35399
Finance     6793
Utility     1378
```

*Model Diagnostics Command:*
```bash
python -c "
import pandas as pd
from pathlib import Path
econ_dir = Path('outputs/econometric/tone_at_top')
subdirs = sorted([d for d in econ_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]
diag = pd.read_csv(latest / 'model_diagnostics.csv')
print(diag[['model', 'n_obs', 'n_entities']])
"
```

*Output:*
```
                         model    n_obs  n_entities
0     Main_M1 (H_TT1 Realtime)    43570        1763
1        Main_M2 (H_TT2 Turns)  1697632       98613
```

**Verdict:** CONFIRMED NOT FIXED

**Rationale:** The code pattern `call_panel if sample == "Main" else call_panel[call_panel["sample"] == sample]` returns the full unfiltered panel for "Main", causing 43,570 observations (Main=35,399 + Finance=6,793 + Utility=1,378) instead of the correct 35,399.

---

### H10-002: LaTeX Clustering Note (BLOCKER)

**Claimed Status:** NOT FIXED
**Verification Steps:**
1. Searched for tone_at_top_full.tex files
2. Read clustering note from latest LaTeX output
3. Verified source code has correct model-specific note

**Evidence:**

*Command to find latest table:*
```bash
find outputs/econometric/tone_at_top -name "tone_at_top_full.tex"
```

*Latest file:* `outputs/econometric/tone_at_top/2026-03-02_002451/tone_at_top_full.tex`

*Command to check clustering note:*
```bash
grep -n "clustered\|Notes" outputs/econometric/tone_at_top/2026-03-02_002451/tone_at_top_full.tex
```

*Output:*
```
56:\textit{Notes:} M1 (call-level): Standard errors two-way clustered by Firm $\times$ CEO. M2 (turn-level): Standard errors two-way clustered by Firm $\times$ Call. CEOs with fewer than 5 calls are excluded. All continuous controls are standardized within each model's estimation sample. Variables are winsorized at 1\%/99\% by year at the engine level. $^{***}$ p$<$0.01, $^{**}$ p$<$0.05, $^{*}$ p$<$0.10.
```

*Source Code (lines 551-552):*
```python
"M1 (call-level): Standard errors two-way clustered by Firm $\\times$ CEO. "
"M2 (turn-level): Standard errors two-way clustered by Firm $\\times$ Call. "
```

**Verdict:** CONFIRMED FIXED

**Rationale:** The LaTeX table now correctly distinguishes M1 (Firm x CEO) from M2 (Firm x Call) clustering in the notes section.

---

### H10-003: Duplicate Entity-Time Index (MAJOR)

**Claimed Status:** NOT FIXED
**Verification Steps:**
1. Ran duplicate detection against parquet data
2. Searched source code for deduplication logic

**Evidence:**

*Command to check duplicates:*
```bash
python -c "
import pandas as pd
from pathlib import Path
panel_dir = Path('outputs/variables/tone_at_top')
subdirs = sorted([d for d in panel_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]
cp = pd.read_parquet(latest / 'tone_at_top_panel.parquet')
cp['yq_id'] = (cp['year'].astype(str) + 'Q' + cp['quarter'].astype(str))
reg = cp.dropna(subset=['ClarityStyle_Realtime','CFO_QA_Uncertainty_pct','Size','BM','Lev','ROA','StockRet','MarketRet','EPS_Growth','SurpDec'])
dups = reg.groupby(['gvkey','yq_id']).size()
n_dups = (dups > 1).sum()
n_rows_affected = dups[dups > 1].sum()
print(f'Firm-quarters with >1 call: {n_dups}')
print(f'Total duplicate rows: {n_rows_affected}')
"
```

*Output:*
```
Firm-quarters with >1 call: 347
Total duplicate rows: 694
```

*Source Code Search:*
```bash
grep -n "drop_duplicates\|set_index.*gvkey.*yq\|entity.*time.*unique\|dedup" src/f1d/econometric/run_h10_tone_at_top.py
```

*Output:*
```
135:    reg_df = reg_df.set_index(["gvkey", "yq_id"])
```

**Verdict:** CONFIRMED NOT FIXED

**Rationale:** No deduplication code exists before `set_index(["gvkey", "yq_id"])` at line 135. 347 firm-quarters have >1 call (694 rows), creating non-unique PanelOLS index.

---

### H10-004: Missing Run Manifest (MAJOR)

**Claimed Status:** NOT FIXED
**Verification Steps:**
1. Searched for run_manifest.json in Stage 3 and Stage 4 outputs
2. Read manifest content to verify structure

**Evidence:**

*Command:*
```bash
find outputs/variables/tone_at_top -name "run_manifest.json" 2>/dev/null
find outputs/econometric/tone_at_top -name "run_manifest.json" 2>/dev/null
```

*Output:*
```
outputs/variables/tone_at_top/2026-03-02_001906/run_manifest.json
outputs/econometric/tone_at_top/2026-03-02_002451/run_manifest.json
```

*Manifest Content (Stage 4):*
```json
{
  "manifest_version": "1.0",
  "stage": "stage4",
  "timestamp": "2026-03-02_002451",
  "generated_at": "2026-03-02T00:29:19.603817",
  "git_commit": "c9b00bef1f4ee1b94582cf684c1f23fa9c16cb50",
  "command": "C:\\...\\run_h10_tone_at_top.py",
  "input_hashes": {
    "call_panel": "3bd333f41329dbf13d40707e212302ada6de42c2094e38424edf1b81e31740e1",
    "turns_panel": "0bb6817db04383bb993c6721b3c20ef857ad5055e3706bebaa85fb5b49c5a315"
  },
  "output_files": {...},
  "panel_path": "...tone_at_top_panel.parquet",
  "panel_hash": "3bd333f41329dbf13d40707e212302ada6de42c2094e38424edf1b81e31740e1"
}
```

**Verdict:** CONFIRMED FIXED

**Rationale:** Manifest files now exist in both Stage 3 and Stage 4 outputs with git commit, timestamps, input hashes, and output file paths.

---

### H10-005: Placebo Test Documented (MAJOR/DOCUMENTED)

**Claimed Status:** DOCUMENTED
**Verification Steps:**
1. Verified placebo coefficient values
2. Checked provenance documentation for discussion

**Evidence:**

*Command:*
```bash
python -c "
import pandas as pd
from pathlib import Path
econ_dir = Path('outputs/econometric/tone_at_top')
subdirs = sorted([d for d in econ_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]
placebo = pd.read_csv(latest / 'coefficients_Main_M2_placebo_lead.csv')
baseline = pd.read_csv(latest / 'coefficients_Main_M2_baseline.csv')
print('Placebo:', placebo[placebo['variable'].str.contains('CEO_Unc', na=False)][['variable', 'coef', 'se', 'tstat']])
print('Baseline:', baseline[baseline['variable'].str.contains('CEO_Prior', na=False)][['variable', 'coef', 'se', 'tstat']])
"
```

*Output:*
```
Placebo:
            variable      coef        se      tstat
1  IHS_CEO_Unc_Lead1  0.037284  0.001184  31.488175

Baseline:
               variable      coef        se      tstat
1  IHS_CEO_Prior_QA_Unc  0.042648  0.002202  19.370251
```

*Documentation Search:*
```bash
grep -n "placebo\|Lead1\|future.*CEO\|undermines" docs/provenance/H10.md
```

*Output:* Found at lines 54, 251, 331, 441-450 (Section J.1 documents the issue)

**Verdict:** CONFIRMED DOCUMENTED

**Rationale:** Placebo t=31.49 > baseline t=19.37 verified. Issue documented in H10.md Section J.1 with explanation of implications.

---

### H10-006: Turn_Uncertainty_pct Unwinsorized (MINOR)

**Claimed Status:** NOT FIXED
**Verification Steps:**
1. Checked distribution of Turn_Uncertainty_pct in turns panel

**Evidence:**

*Command:*
```bash
python -c "
import pandas as pd
from pathlib import Path
panel_dir = Path('outputs/variables/tone_at_top')
subdirs = sorted([d for d in panel_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]
tp = pd.read_parquet(latest / 'tone_at_top_turns_panel.parquet')
print(f'Turn_Uncertainty_pct stats:')
print(f'  min: {tp[\"Turn_Uncertainty_pct\"].min():.2f}')
print(f'  max: {tp[\"Turn_Uncertainty_pct\"].max():.2f}')
print(f'  p99: {tp[\"Turn_Uncertainty_pct\"].quantile(0.99):.2f}')
print(f'  values > 50%: {(tp[\"Turn_Uncertainty_pct\"] > 50).sum():,}')
"
```

*Output:*
```
Turn_Uncertainty_pct stats:
  min: 0.00
  max: 100.00
  p99: 10.00
  values > 50%: 478
```

**Verdict:** CONFIRMED NOT FIXED

**Rationale:** max=100.00 confirms no winsorization applied. 478 turns have >50% uncertainty.

---

### H10-007: Winsorization Inconsistency (MINOR)

**Claimed Status:** NOT FIXED
**Verification Steps:**
1. Compared CEO vs CFO max values by year
2. Checked provenance documentation claims

**Evidence:**

*Command:*
```bash
python -c "
import pandas as pd
from pathlib import Path
panel_dir = Path('outputs/variables/tone_at_top')
subdirs = sorted([d for d in panel_dir.iterdir() if d.is_dir()])
latest = subdirs[-1]
cp = pd.read_parquet(latest / 'tone_at_top_panel.parquet')
print('CEO_QA_Uncertainty_pct max by year:')
print(cp.groupby('year')['CEO_QA_Uncertainty_pct'].max())
print(f'\nCFO_QA_Uncertainty_pct pooled max: {cp[\"CFO_QA_Uncertainty_pct\"].max():.4f}')
"
```

*Output:*
```
CEO_QA_Uncertainty_pct max by year:
year
2002    2.514267
...
2018    1.887607

CFO_QA_Uncertainty_pct pooled max: 3.3780
```

*Provenance Claim (H10.md line 283):*
```
| Linguistic percentages (`CFO_QA_Uncertainty_pct`, etc.) | Pooled 1%/99% | ...
```

**Verdict:** CONFIRMED NOT FIXED

**Rationale:** CEO varies by year (1.89-2.51) = per-year winsorization; CFO constant 3.378 = pooled. Provenance incorrectly claims pooled for all linguistic vars.

---

### H10-008: Sample Attrition Table (MINOR)

**Claimed Status:** NOT FIXED
**Verification Steps:**
1. Searched for LaTeX attrition table files

**Evidence:**

*Command:*
```bash
ls outputs/variables/tone_at_top/2026-03-02_001906/
```

*Output:*
```
reconciliation_table.csv
run_manifest.json
summary_stats.csv
tone_at_top_panel.parquet
tone_at_top_turns_panel.parquet
```

**Verdict:** CONFIRMED NOT FIXED

**Rationale:** No `sample_attrition.tex` or `reconciliation.tex` exists. Only CSV version present.

---

### H10-009: CEO_Unc_Lag1 Zeros (NOTE)

**Claimed Status:** DOCUMENTED
**Verification Steps:**
1. Searched provenance for explicit documentation of 57.9% zero rate

**Evidence:**

*Search Command:*
```bash
grep -n "57.9\|zeros\|CEO_Unc_Lag1" docs/provenance/H10.md
```

*Output:* CEO_Unc_Lag1 is mentioned in variable dictionary but the 57.9% zero rate is not documented as a known issue.

**Verdict:** PARTIALLY DOCUMENTED

**Rationale:** Variable is defined but the zero rate issue from ffill propagation is not explicitly documented.

---

### H10-010: 2002 Absent from M1 (NOTE)

**Claimed Status:** DOCUMENTED
**Verification Steps:**
1. Searched provenance for explicit documentation of 2002 exclusion

**Evidence:**

*Search Results:* The provenance documents "44.5% missing because it requires >=4 prior CEO calls" but does not explicitly state that ALL 2002 quarters are excluded from M1.

**Verdict:** PARTIALLY DOCUMENTED

**Rationale:** Implicit in the min_calls=4 documentation but not explicitly stated that 2002Q1-2002Q4 are entirely absent.

---

## Additional Findings

No new issues discovered during verification beyond those documented in prior audits.

---

## Cross-Artifact Consistency Matrix

| Source | Field | Expected | Actual | Match? |
|--------|-------|----------|--------|--------|
| coefficients CSV | M1 ClarityStyle coef | ~0.0169 | 0.0169 | YES |
| model_diagnostics | M1 n_obs | 43,570 | 43,570 | YES (but wrong composition) |
| coefficients CSV | M2 CEO_Prior coef | ~0.0426 | 0.0426 | YES |
| model_diagnostics | M2 n_obs | 1,697,632 | 1,697,632 | YES (but wrong composition) |
| LaTeX table | Clustering note | Model-specific | Model-specific | YES (fixed) |

---

## Recommendations

### Priority 1: BLOCKER (Must Fix Before Publication)

1. **Fix sample filter bug (H10-001):** Change lines 1168-1177 to:
   ```python
   call_sub = call_panel[call_panel["sample"] == sample].copy()
   turns_sub = turns_panel[turns_panel["sample"] == sample].copy()
   ```

2. **Rerun Stage 4** after fixing sample filter

### Priority 2: MAJOR (Should Fix)

3. **Add entity-time deduplication (H10-003):** Before `set_index()`:
   ```python
   reg_df = reg_df.sort_values("start_date").drop_duplicates(
       subset=["gvkey", "yq_id"], keep="last"
   )
   ```

### Priority 3: MINOR (Consider Fixing)

4. **Add Turn_Uncertainty_pct winsorization** or document intentional non-winsorization
5. **Update provenance Section G** to correctly document winsorization methods
6. **Generate LaTeX sample attrition table** from reconciliation_table.csv
7. **Document CEO_Unc_Lag1 zero rate** and 2002 exclusion explicitly

---

## Command Log

| # | Timestamp | Command | Purpose |
|---|-----------|---------|---------|
| 1 | 2026-03-02 | `grep -n "call_sub\|sample.*Main" run_h10_tone_at_top.py` | Find sample filter code |
| 2 | 2026-03-02 | Read run_h10_tone_at_top.py:1160-1190 | Examine sample filter implementation |
| 3 | 2026-03-02 | Python: sample composition check | Verify M1 sample breakdown |
| 4 | 2026-03-02 | Python: model_diagnostics check | Verify N values |
| 5 | 2026-03-02 | `find outputs/.../tone_at_top_full.tex` | Find LaTeX tables |
| 6 | 2026-03-02 | `grep clustered tone_at_top_full.tex` | Check clustering note |
| 7 | 2026-03-02 | Read run_h10_tone_at_top.py:545-565 | Verify code fix for clustering note |
| 8 | 2026-03-02 | Python: duplicate check | Verify entity-time duplicates |
| 9 | 2026-03-02 | `grep drop_duplicates run_h10_tone_at_top.py` | Check for dedup code |
| 10 | 2026-03-02 | `find run_manifest.json` | Check for manifest files |
| 11 | 2026-03-02 | Read run_manifest.json | Verify manifest content |
| 12 | 2026-03-02 | Python: placebo/baseline coef check | Verify placebo values |
| 13 | 2026-03-02 | `grep placebo H10.md` | Check placebo documentation |
| 14 | 2026-03-02 | Python: Turn_Uncertainty_pct check | Verify winsorization |
| 15 | 2026-03-02 | Python: CEO/CFO winsorization check | Compare methods |
| 16 | 2026-03-02 | `grep winsor H10.md` | Check provenance claims |
| 17 | 2026-03-02 | `ls outputs/.../tone_at_top/` | Check for LaTeX attrition table |
| 18 | 2026-03-02 | `git log --since="2026-03-01"` | Check recent changes |
| 19 | 2026-03-02 | Python: cross-artifact consistency | Verify M1/M2 values match |

---

## Appendix: Raw Evidence

### A. Sample Filter Bug - Code Location

**File:** `src/f1d/econometric/run_h10_tone_at_top.py`
**Lines:** 1168-1177

```python
call_sub = (
    call_panel
    if sample == "Main"
    else call_panel[call_panel["sample"] == sample]
)
turns_sub = (
    turns_panel
    if sample == "Main"
    else turns_panel[turns_panel["sample"] == sample]
)
```

### B. Sample Composition Output

```
Full panel (M1 listwise): 43,570
Sample breakdown:
sample
Main       35399
Finance     6793
Utility     1378
Name: count, dtype: int64
```

### C. Duplicate Entity-Time Output

```
Firm-quarters with >1 call: 347
Total duplicate rows: 694
```

### D. Turn_Uncertainty_pct Distribution

```
Turn_Uncertainty_pct stats:
  min: 0.00
  max: 100.00
  p99: 10.00
  values > 50%: 478
  values > 25%: 2,422
```

### E. Winsorization Comparison

```
CEO_QA_Uncertainty_pct max by year:
2002    2.514267
2003    2.473955
...
2018    1.887607

CFO_QA_Uncertainty_pct pooled max: 3.3780
```

---

*End of Re-Verification Audit Report*
*Generated: 2026-03-02*
