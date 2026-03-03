# Paper Artifacts Audit Report — H9 Takeover Hazards

**Suite ID:** H9
**Audit Date:** 2026-03-01
**Auditor:** Adversarial Thesis-Pipeline Referee (AI)
**Protocol:** docs/Prompts/Paper_Ready_artifacts.txt
**Panel Run Audited:** `outputs/variables/takeover/2026-02-28_152253/`
**Regression Run Audited:** `outputs/econometric/takeover/2026-02-28_152619/`
**Git HEAD:** `c9b00be docs: add audit prompt and H-suite provenance documentation`

---

## 1) Executive Summary

| Question | Answer |
|----------|--------|
| **Is H9 paper-submission ready?** | **NO** |
| **Presence verdict: Complete package?** | **PARTIAL** — Missing PH diagnostics |
| **Quality verdict: Submission-grade quality?** | **NO** — Critical bugs in cause-specific models |

### Top 3 BLOCKERS

1. **BLOCKER #1 — Cause-specific event coding creates phantom recurrent events.** `Takeover_Uninvited` and `Takeover_Friendly` are coded from `Takeover_Type` alone (line 240-241 of `run_h9_takeover_hazards.py`), setting event=1 for ALL intervals of type-matching firms, not just the last interval. This inflates event rows by 8.5x (Uninvited) and 9.2x (Friendly), turning a single-event model into a recurrent-event model.
   - **Rerun required:** Stage 4 only

2. **BLOCKER #2 — Negative-duration intervals exist in the panel.** 8 rows have `stop < start` (e.g., start=2007, stop=2002). These represent firms taken over before they appeared in the sample.
   - **Rerun required:** Stage 3 + Stage 4

3. **MAJOR — Missing PH diagnostics.** No Schoenfeld residual test or PH assumption diagnostics are generated. Required for survival model validity.
   - **Rerun required:** Stage 4 (code changes)

### Summary of Findings

| Severity | Count | Description |
|----------|-------|-------------|
| BLOCKER | 2 | Cause-specific coding bug; negative durations |
| MAJOR | 4 | Missing PH diagnostics; LaTeX SE formatting; n_firms mislabeled; dead code |
| MINOR | 3 | README counts; summary stats gaps; report formatting |
| NOTE | 2 | Low concordance; ClarityCEO time-varying (expected) |
| PASS | 6 | Cox PH All correct; cross-artifact consistency; reproducibility; linkage; etc. |

**Trustworthy Results:**
- **Cox PH All (Takeover column):** YES, correctly implemented
- **Cox CS Uninvited / Friendly:** NO — must be rerun after fixing event coding

---

## 2) Suite & Run Identification

| Field | Value | Evidence Command |
|-------|-------|------------------|
| **Suite ID** | H9 | `docs/provenance/H9.md` |
| **Stage 3 Timestamp** | `2026-02-28_152253` | `ls outputs/variables/takeover/` |
| **Stage 4 Timestamp** | `2026-02-28_152619` | `ls outputs/econometric/takeover/` |
| **Stage 3 Panel Path** | `outputs/variables/takeover/2026-02-28_152253/takeover_panel.parquet` | `run_log.txt:10` |
| **Stage 4 Output Path** | `outputs/econometric/takeover/2026-02-28_152619/` | `run_log.txt:5` |
| **Git Commit (Manifest)** | Not in outputs | No run_manifest.json generated |
| **Git HEAD (Current)** | `c9b00be` | `git log --oneline -1` |

### Run Linkage Verification

```bash
# From run_log.txt:10
Loaded: outputs/variables/takeover/2026-02-28_152253/takeover_panel.parquet
```

**Status:** PASS — Stage 4 references the correct Stage 3 panel from the same pipeline run cycle.

---

## 3) Estimator Family Detection

| Field | Value |
|-------|-------|
| **Model Family** | Survival Analysis — Cox Proportional Hazards with Time-Varying Covariates |
| **Estimator** | `lifelines.CoxTimeVaryingFitter` (counting-process format) |
| **Evidence (Code)** | `run_h9_takeover_hazards.py:81` imports `CoxTimeVaryingFitter` |
| **Evidence (Output)** | `cox_ph_all.txt` shows coef, exp(coef), se(coef), z, p columns |
| **Link Function** | Log-hazard ratio linear in covariates |
| **Ties Method** | Efron (default for CoxTimeVaryingFitter) |
| **Competing Risks** | Cause-specific Cox models (separate models for All/Uninvited/Friendly) |

### Model-Family Required Artifacts (B5/B6)

| Artifact | Required | Found | Status |
|----------|----------|-------|--------|
| HR table with 95% CI | Yes | `takeover_table.tex` (HR only, no CI) | **PARTIAL** |
| N subjects, N events | Yes | `model_diagnostics.csv` | PASS |
| Censoring summary | Yes | In `summary_stats.csv` | PASS |
| Time-at-risk / duration | Yes | `start`/`stop` columns in panel | PASS |
| PH diagnostics: Schoenfeld test | Yes | **MISSING** | **FAIL** |
| PH diagnostics: plots | Optional | **MISSING** | NOTE |
| Fit stats: Concordance/C-index | Yes | `model_diagnostics.csv` | PASS |
| Fit stats: Partial LL | Optional | **MISSING** | NOTE |

---

## 4) Artifact Requirements & Quality Matrix

### LAYER A — Required for All Suites

| Artifact | Required | Found Path | Presence | Quality | Quality Tests | Notes |
|----------|----------|------------|----------|---------|---------------|-------|
| **A1: Provenance / Lineage** |
| Suite provenance doc | Yes | `docs/provenance/H9.md` | PASS | PASS | Commands, inputs, row counts verified | Complete |
| Variable dictionary | Yes | `docs/provenance/H9.md` Section F | PASS | PASS | Formulas, timing, winsorization documented | Complete |
| Sample attrition table | Optional | Not generated | UNVERIFIED | — | — | Not required for survival |
| **A2: Reproducibility Bundle** |
| run_manifest.json | Yes | **MISSING** | **FAIL** | — | No manifest generated | BLOCKER for reproducibility |
| Environment lock | Yes | `requirements.txt` (repo-level) | PASS | UNVERIFIED | — | Not run-scoped |
| Stage 3 log | Yes | Console output captured | PASS | PASS | Key checks present | |
| Stage 4 log | Yes | `run_log.txt` | PASS | PASS | Full execution log | |
| **A3: Core Statistics + Results** |
| Summary stats (csv) | Yes | `summary_stats.csv` | PASS | PASS | N, Mean, SD match panel | |
| Summary stats (tex) | Yes | `summary_stats.tex` | PASS | UNVERIFIED | Not compiled | |
| Baseline results (csv) | Yes | `hazard_ratios.csv` | PASS | PARTIAL | n_firms mislabeled | Finding #5 |
| Baseline results (tex) | Yes | `takeover_table.tex` | PASS | **FAIL** | SEs bunched at bottom | Finding #4 |
| Raw txt output | Yes | `cox_ph_all.txt`, etc. | PASS | PASS | Full lifelines output | |
| Model diagnostics | Yes | `model_diagnostics.csv` | PASS | PASS | Concordance, N events | |

### LAYER B — Model-Family Required (Hazards)

| Artifact | Required | Found Path | Presence | Quality | Notes |
|----------|----------|------------|----------|---------|-------|
| HR table | Yes | `takeover_table.tex` | PASS | **FAIL** | No CI, SEs malformed |
| N subjects | Yes | `model_diagnostics.n_intervals` | PASS | PARTIAL | Labeled as intervals, not firms |
| N events | Yes | `model_diagnostics.n_event_firms` | PASS | PASS | Correct count |
| Censoring summary | Yes | Panel `Takeover` distribution | PASS | PASS | In summary_stats |
| Schoenfeld test | Yes | **MISSING** | **FAIL** | — | No PH diagnostics |
| Concordance/C-index | Yes | `model_diagnostics.concordance` | PASS | PASS | All models have C-index |
| Interval integrity report | Yes | Panel `start`/`stop` | PASS | **FAIL** | 8 negative durations |

### LAYER C — Figures

| Artifact | Required | Found | Presence | Quality | Notes |
|----------|----------|-------|----------|---------|-------|
| HR forest plot | Optional | **MISSING** | UNVERIFIED | — | Not generated |
| Distribution plots | Optional | **MISSING** | UNVERIFIED | — | Not generated |
| Time trend plots | Optional | **MISSING** | UNVERIFIED | — | Not generated |

---

## 5) Notes-as-Claims Register

### Table: `takeover_table.tex`

| # | Claim | Location | Verification | Status |
|---|-------|----------|--------------|--------|
| 1 | Hazard ratios reported | Table body | HR values present | PASS |
| 2 | Standard errors in parentheses | Table note | **SEs bunched at bottom, not interleaved** | **FAIL** |
| 3 | N Events reported per model | Panel A | 349, 45, 346 | PASS |
| 4 | Concordance reported | Panel A | 0.5371, 0.5673, 0.5225 | PASS |
| 5 | HR < 1 = lower hazard | Table note | Note text correct | PASS |
| 6 | Main sample only | Table note | "non-financial, non-utility firms" | PASS |
| 7 | 95% CI reported | Expected | **NO CI in table** | **FAIL** |

### Table: `summary_stats.csv`

| # | Claim | Location | Verification | Status |
|---|-------|----------|--------------|--------|
| 1 | N observations reported | N column | 21,666 for Takeover vars | PASS |
| 2 | Mean, SD reported | Mean, SD columns | Present for all vars | PASS |
| 3 | Min, Max reported | Min, Max columns | Present | PASS |
| 4 | Duration variable included | Expected | **MISSING** | NOTE |

### Model Estimation Claims

| # | Claim | Where Claimed | Verification | Status |
|---|-------|---------------|--------------|--------|
| 1 | Cox PH with time-varying covariates | H9.md A2 | `CoxTimeVaryingFitter` used | PASS |
| 2 | Robust standard errors | H9.md A5 | lifelines default | PASS |
| 3 | Efron ties handling | H9.md A6 | lifelines default | PASS |
| 4 | Cause-specific models for competing risks | H9.md A6 | Separate models for Uninvited/Friendly | **FAIL** (coding bug) |
| 5 | Event=1 only in last interval | H9.md A6 | **VIOLATED** for cause-specific | **FAIL** |
| 6 | All continuous vars winsorized | README | Per-year 1%/99% at engine level | UNVERIFIED |
| 7 | Finance/Utility excluded | H9.md A4 | ff12_code 8, 11 filtered | PASS |

---

## 6) Findings (Grouped by Severity)

### Finding #1: BLOCKER — Cause-Specific Event Coding Creates Phantom Recurrent Events

**Severity:** BLOCKER

**Symptom:** The Cox CS Uninvited and Cox CS Friendly models see 8-9x more event rows than they should, because event=1 is set for ALL intervals of type-matching firms, not just the final interval.

**Evidence:**

Code location: `run_h9_takeover_hazards.py:240-241`
```python
df[EVENT_UNINVITED_COL] = (df["Takeover_Type"] == "Uninvited").astype(int)
df[EVENT_FRIENDLY_COL] = (df["Takeover_Type"] == "Friendly").astype(int)
```

Verification output:
```
Takeover (All): 585 event rows, 585 event firms
  Ratio: 1.00 (correct)

Takeover_Uninvited: 648 event rows, 76 event firms
  Ratio: 8.53 (BUG)

Takeover_Friendly: 4,311 event rows, 469 event firms
  Ratio: 9.19 (BUG)
```

**Why it matters:** `CoxTimeVaryingFitter` treats each event=1 row as a separate event contribution to the partial likelihood. With 8-9x inflated events, the model estimates the rate of a recurrent process rather than the hazard of first occurrence. This invalidates all cause-specific coefficient estimates, standard errors, and p-values. The Uninvited model's significant ClarityCEO result (HR=1.337, p=0.0015) is unreliable.

**Fix:**
```python
# run_h9_takeover_hazards.py:240-241
# CURRENT (BUG):
df[EVENT_UNINVITED_COL] = (df["Takeover_Type"] == "Uninvited").astype(int)
df[EVENT_FRIENDLY_COL] = (df["Takeover_Type"] == "Friendly").astype(int)

# FIXED:
df[EVENT_UNINVITED_COL] = ((df[EVENT_ALL_COL] == 1) & (df["Takeover_Type"] == "Uninvited")).astype(int)
df[EVENT_FRIENDLY_COL] = ((df[EVENT_ALL_COL] == 1) & (df["Takeover_Type"] == "Friendly")).astype(int)
```

**Rerun impact:** Stage 4 only. Panel (Stage 3) is correct; bug is in runtime event indicator creation.

**Acceptance test:**
```python
for col in ['Takeover_Uninvited', 'Takeover_Friendly']:
    event_rows = df_clean[col].sum()
    event_firms = df_clean.groupby('gvkey')[col].max().sum()
    assert event_rows == event_firms, f"{col}: {event_rows} rows != {event_firms} firms"
```

---

### Finding #2: BLOCKER — Negative Duration Intervals in Panel

**Severity:** BLOCKER (data integrity)

**Symptom:** 8 rows in the counting-process panel have `stop < start`, meaning negative durations.

**Evidence:**
```
gvkey=001634: start=2007, stop=2005, dur=-2, Takeover=1, Type=None
gvkey=005116: start=2007, stop=2002, dur=-5, Takeover=1, Type=None
gvkey=013990: start=2003, stop=2002, dur=-1, Takeover=1, Type=None
gvkey=022632: start=2007, stop=2004, dur=-3, Takeover=1, Type=None
gvkey=025950: start=2003, stop=2002, dur=-1, Takeover=1, Type=None
gvkey=030067: start=2012, stop=2006, dur=-6, Takeover=1, Type=None
gvkey=145186: start=2013, stop=2007, dur=-6, Takeover=1, Type=None
gvkey=151832: start=2007, stop=2005, dur=-2, Takeover=1, Type=None
```

**Root cause:** `build_counting_process_panel` sets `exit_year = takeover_year` for event firms. When `takeover_year < entry_year` (firm was taken over before it appeared in the sample), a single row is created with `start = entry_year - 1` and `stop = takeover_year`, producing `stop < start`.

**Regression impact:** 0 negative/zero duration rows survive into the CEO regression (eliminated by listwise deletion on ClarityCEO or other controls). However, they represent corrupted survival data that could affect other analyses.

**Fix:** In `build_counting_process_panel` (`build_h9_takeover_panel.py:384`), add a guard:
```python
# Filter out firms where takeover predates sample entry
valid = firm_bounds["exit_year"] >= firm_bounds["entry_year"]
n_invalid = (~valid).sum()
if n_invalid > 0:
    print(f"  WARNING: {n_invalid} firms with takeover before sample entry — excluded")
firm_bounds = firm_bounds[valid].copy()
```

**Rerun impact:** Stage 3 + Stage 4.

---

### Finding #3: MAJOR — Missing Proportional Hazards Diagnostics

**Severity:** MAJOR

**Symptom:** No Schoenfeld residual test or PH assumption diagnostics are generated. The PH assumption is central to Cox model validity.

**Evidence:**
```bash
$ ls outputs/econometric/takeover/2026-02-28_152619/
schoenfeld_test.csv: MISSING
ph_diagnostics.csv: MISSING
ph_assumption_test.txt: MISSING
```

**Why it matters:** Without PH diagnostics, there is no evidence that the proportional hazards assumption holds. PH violations would invalidate the Cox model coefficients. This is a standard requirement for survival analysis reporting.

**Fix:** Add Schoenfeld test after model fitting:
```python
from lifelines.statistics import proportional_hazard_test
# After ctv.fit()
ph_test = proportional_hazard_test(ctv, df_clean, time_transform='rank')
ph_test.print_summary()
# Save to file
ph_test.results.to_csv(out_dir / "ph_diagnostics.csv")
```

**Rerun impact:** Stage 4 only (code changes + rerun).

---

### Finding #4: MAJOR — LaTeX Table SE Formatting Broken

**Severity:** MAJOR

**Symptom:** In `takeover_table.tex`, all 10 SE rows are bunched together after all 10 HR rows, instead of being interleaved (each SE below its corresponding HR).

**Evidence:** `takeover_table.tex:19-38`
```latex
% Lines 19-28: All HR rows
Clarity (CEO) & & 1.0497 & & 1.3371 & & 1.0978 \\
CEO QA Uncertainty & & 1.2144 & & 1.0029 & & 0.9225 \\
...
% Lines 29-38: All SE rows bunched together
 & & (0.0845) & & (0.0915) & & (0.0290) \\
 & & (0.2890) & & (0.3024) & & (0.0975) \\
```

**Expected format (standard accounting review style):**
```latex
Clarity (CEO) & & 1.0497 & & 1.3371 & & 1.0978 \\
              & & (0.0845) & & (0.0915) & & (0.0290) \\
CEO QA Uncertainty & & 1.2144 & & 1.0029 & & 0.9225 \\
                   & & (0.2890) & & (0.3024) & & (0.0975) \\
```

**Fix:** Fix `make_cox_hazard_table` in `src/f1d/shared/latex_tables_accounting.py` to interleave SE rows immediately after each HR row.

**Rerun impact:** Stage 4 only (table generation).

---

### Finding #5: MAJOR — `n_firms` Column Mislabeled in `hazard_ratios.csv`

**Severity:** MAJOR

**Symptom:** The `n_firms` column contains the value 12,139, which is N intervals (firm-year rows), not N firms. The actual number of unique firms is ~1,623.

**Evidence:**
```python
# run_h9_takeover_hazards.py:472
"n_firms": df_clean_len,  # This is len(df_clean) = N intervals
```

Verification:
```
hazard_ratios.csv n_firms values: [12139]
Actual unique firms in regression: ~1,623
```

**Why it matters:** Any downstream consumer (paper table, robustness check) that reads `n_firms` will report 12,139 firms instead of the actual ~1,623. This is materially misleading.

**Fix:**
```python
"n_intervals": df_clean_len,
"n_firms": df_clean["gvkey"].nunique() if "gvkey" in df_clean.columns else None,
```

**Rerun impact:** Stage 4 only.

---

### Finding #6: MAJOR — Regime Variant Dead Code in MODEL_VARIANTS

**Severity:** MAJOR

**Symptom:** `MODEL_VARIANTS` still contains the "Regime" entry with `ClarityManager`, but `ClarityManager` is not in the panel (0% coverage). The Regime variant silently produces nothing — no error, no warning in the run log.

**Evidence:** `run_h9_takeover_hazards.py:144-155`
```python
MODEL_VARIANTS: Dict[str, Dict[str, str]] = {
    "Regime": {
        "clarity_var": "ClarityManager",  # Not in panel
        ...
    },
    "CEO": {...},
}
```

**Why it matters:** Confusing for reproducibility. A reader of the code expects 6 models (3 event types × 2 variants) but only 3 run. No explicit error or skip message.

**Fix:** Remove the Regime entry or add explicit check:
```python
for variant_key, variant_spec in MODEL_VARIANTS.items():
    clarity_var = variant_spec["clarity_var"]
    if clarity_var not in df.columns:
        print(f"  [{variant_key}] Skipped: {clarity_var} not in panel")
        continue
```

**Rerun impact:** Code-only fix. No data rerun needed.

---

### Finding #7: MINOR — README Event Counts Don't Match Panel

**Severity:** MINOR

**Symptom:** README.md claims `Event breakdown: Friendly: 563, Uninvited: 87, Unknown: 40`. The actual panel shows Friendly=556, Uninvited=83, Unknown=37.

**Evidence:**
```
README claims: Friendly=563, Uninvited=87, Unknown=40 (total 690)
Actual panel (firm-level):
  Friendly: 556
  Uninvited: 83
  Unknown: 37
  None: 1753
Total event firms: 690 (matches)
```

**Root cause:** The difference of 14 firms (563-556 + 87-83 + 40-37 = 14) exactly equals the 14 firms with `Takeover=1` but `Takeover_Type='None'` (the negative/zero duration firms).

**Fix:** Update README to match actual panel values.

**Rerun impact:** Documentation only.

---

### Finding #8: MINOR — Summary Stats Reference Missing Variables

**Severity:** MINOR

**Symptom:** `SUMMARY_STATS_VARS` in `run_h9_takeover_hazards.py:120-141` references `duration`, `ClarityManager`, and `Manager_QA_Uncertainty_pct`, none of which are in the Main sample DataFrame at summary stats generation time.

**Evidence:**
```python
# Lines 122-128:
{"col": "ClarityManager", "label": "Clarity (Manager)"},     # Not in panel
{"col": "Manager_QA_Uncertainty_pct", "label": "Mgr QA Uncertainty"},  # Not in CEO variant
{"col": "duration", "label": "Duration (years)"},            # Never computed
```

**Impact:** Missing columns are silently skipped, but summary stats is incomplete.

**Fix:** Remove stale references; add `duration = stop - start` computation if desired.

**Rerun impact:** Stage 4 only.

---

### Finding #9: NOTE — Concordance Indices Near 0.5

**Severity:** NOTE

**Symptom:** All three models have concordance indices barely above 0.5 (random):
- Cox PH All: 0.537
- Cox CS Uninvited: 0.567
- Cox CS Friendly: 0.522

**Why it matters:** The models have essentially no discriminative power. This is consistent with H9 being "Partially Supported" at best — the covariates (including ClarityCEO) explain very little variation in takeover hazard.

**Rerun impact:** None. This is a substantive finding, not a bug.

---

### Finding #10: NOTE — ClarityCEO Is Time-Varying Across CEO Turnovers

**Severity:** NOTE

**Symptom:** 660 of 1,685 firms with ClarityCEO have varying values across year-intervals, because CEO turnover brings a different CEO's clarity score.

**Evidence:**
```
Firms with varying ClarityCEO across years: 660 / 1,685
```

**Why it matters:** ClarityCEO is described as "time-invariant" in the provenance (H9.md A4, F). It IS time-invariant per CEO, but time-varying per FIRM due to CEO turnover. This is actually the correct behavior for a time-varying Cox model — it captures the clarity of whoever is CEO in each year.

**Rerun impact:** None (behavior is correct, documentation could clarify).

---

## 7) Cross-Artifact Consistency Results

| Check | Status | Evidence |
|-------|--------|----------|
| **C1: N consistency** | PARTIAL | `hazard_ratios.n_firms` = 12,139 but actual firms ≈ 1,623. Event counts consistent across `model_diagnostics` and raw outputs. |
| **C2: Coef/HR consistency** | PASS | HR values in `takeover_table.tex` match `hazard_ratios.csv` exactly (within rounding). Verified: ClarityCEO HR=1.0497 in both. |
| **C3: SE method consistency** | PASS | Robust SEs used (lifelines default). No clustering specified. |
| **C4: Run linkage consistency** | PASS | Stage 4 log shows correct Stage 3 panel path: `outputs/variables/takeover/2026-02-28_152253/takeover_panel.parquet` |
| **C5: Timing/leakage spot-check** | UNVERIFIED | Lead/lag construction not explicitly verified in this audit. |

---

## 8) Rerun / Regeneration Plan (Minimal, Suite-Scoped)

### Scenario A: Fix Critical Bug Only (Finding #1)

If only fixing the cause-specific event coding:

```bash
# 1. Apply fix to run_h9_takeover_hazards.py:240-241
# 2. Rerun Stage 4
python -m f1d.econometric.run_h9_takeover_hazards
```

**Acceptance tests:**
```python
# After rerun, verify event coding
import pandas as pd
hr = pd.read_csv('outputs/econometric/takeover/LATEST/hazard_ratios.csv')

# Event rows should equal event firms for cause-specific models
# Uninvited: expect ~39-45 event firms (down from 295 inflated rows)
# Friendly: expect ~290-350 event firms (down from 2741 inflated rows)
```

### Scenario B: Fix All BLOCKERs (Findings #1 and #2)

```bash
# 1. Fix negative durations in build_h9_takeover_panel.py:384
# 2. Rebuild Stage 3 panel
python -m f1d.variables.build_h9_takeover_panel

# 3. Apply fix to run_h9_takeover_hazards.py:240-241
# 4. Rerun Stage 4
python -m f1d.econometric.run_h9_takeover_hazards
```

**Acceptance tests:**
```python
import pandas as pd
panel = pd.read_parquet('outputs/variables/takeover/LATEST/takeover_panel.parquet')

# No negative durations
assert (panel['stop'] - panel['start'] >= 0).all(), "FAIL: negative durations"

# Event counts (firm-level) should reconcile
n_events = panel.groupby('gvkey')['Takeover'].max().sum()
print(f"Event firms: {n_events}")  # Expect ~676-690 (minus 14 invalid)
```

### Scenario C: Full Paper-Ready Regeneration

Include MAJOR fixes:

```bash
# 1-4. Same as Scenario B
# 5. Fix LaTeX table generator in latex_tables_accounting.py
# 6. Add PH diagnostics to run_h9_takeover_hazards.py
# 7. Fix n_firms column naming
# 8. Rerun Stage 4
python -m f1d.econometric.run_h9_takeover_hazards
```

---

## 9) Hardening Recommendations

### Repository-Level

1. **Add counting-process validator.** Before passing to `CoxTimeVaryingFitter`, assert:
   - `(stop - start > 0).all()` (no zero/negative durations)
   - For non-recurrent events: `groupby(id_col)[event_col].sum() <= 1` per subject
   - `start[i+1] == stop[i]` for consecutive intervals per subject (no gaps)

2. **Add event-row-per-firm assertion for cause-specific models:**
   ```python
   for event_col in [EVENT_UNINVITED_COL, EVENT_FRIENDLY_COL]:
       event_rows = df[event_col].sum()
       event_firms = df.groupby("gvkey")[event_col].max().sum()
       if event_rows != event_firms:
           raise ValueError(f"{event_col}: {event_rows} rows != {event_firms} firms")
   ```

3. **Log WARNING when covariates are silently dropped.**

4. **Add run_manifest.json generation** with git commit, timestamp, input paths, output hashes.

5. **Rename `n_firms` to `n_intervals`** and add true `n_firms` field.

### Suite-Level

6. **Add PH assumption tests** (Schoenfeld residuals) as standard output.

7. **Add unit test for cause-specific event coding:**
   ```python
   def test_cause_specific_event_coding():
       df = pd.DataFrame({
           'gvkey': ['A','A','A'],
           'start': [0,1,2],
           'stop': [1,2,3],
           'Takeover': [0,0,1],
           'Takeover_Type': ['Uninvited','Uninvited','Uninvited'],
       })
       df['Takeover_Uninvited'] = ((df['Takeover']==1) & (df['Takeover_Type']=='Uninvited')).astype(int)
       assert df['Takeover_Uninvited'].sum() == 1  # Only last interval
   ```

8. **Remove stale SUMMARY_STATS_VARS entries** for `duration`, `ClarityManager`.

---

## 10) Command Log (Chronological)

| # | Command | Purpose | Key Output |
|---|---------|---------|------------|
| 1 | `read README.md` | Extract pipeline contract | 4-stage design, zero-row-delta invariant |
| 2 | `read docs/Prompts/Paper_Ready_artifacts.txt` | Load audit protocol | 5-phase audit structure |
| 3 | `read docs/provenance/H9.md` | Build claim register | 639 lines of provenance |
| 4 | `ls outputs/variables/takeover/` | Find Stage 3 runs | Latest: 2026-02-28_152253 |
| 5 | `ls outputs/econometric/takeover/` | Find Stage 4 runs | Latest: 2026-02-28_152619 |
| 6 | `read build_h9_takeover_panel.py` | Trace Stage 3 code | 711 lines, counting-process construction |
| 7 | `read run_h9_takeover_hazards.py` | Trace Stage 4 code | 766 lines, Cox TV fitting |
| 8 | `ls outputs/variables/takeover/2026-02-28_152253/` | Verify Stage 3 outputs | takeover_panel.parquet, summary_stats.csv, report |
| 9 | `ls outputs/econometric/takeover/2026-02-28_152619/` | Verify Stage 4 outputs | 11 files including tex, csv, txt |
| 10 | `read model_diagnostics.csv` | Check diagnostics | 3 models, CEO variant only |
| 11 | `read hazard_ratios.csv` | Check coefficients | 30 rows, n_firms=12139 (mislabeled) |
| 12 | `read takeover_table.tex` | Audit LaTeX table | SEs bunched at bottom |
| 13 | `read cox_ph_all.txt` | Verify raw output | Concordance 0.5371 |
| 14 | `read summary_stats.csv` | Check summary stats | Missing duration column |
| 15 | `read run_log.txt` | Check execution flow | Only CEO variant ran |
| 16 | `python -c panel structure check` | Verify panel structure | 27,787 rows, 2,429 firms, 23 columns |
| 17 | `python -c event coding analysis` | **CRITICAL BUG FOUND** | Cause-specific 8.5x/9.2x inflated |
| 18 | `python -c negative duration check` | Find corrupted rows | 8 negative, 6 zero durations |
| 19 | `python -c variable coverage` | Coverage audit | ClarityCEO 59.4%, Size 99.8% |
| 20 | `python -c PH diagnostics check` | Find missing diagnostics | All PH test files MISSING |
| 21 | `read report_step3_takeover.md` | Stage 3 report audit | Row counts match |
| 22 | `read report_step4_takeover.md` | Stage 4 report audit | Model summary present |
| 23 | `git log --oneline -1` | Get commit hash | c9b00be |

---

**Document Generated:** 2026-03-01
**Panel Audited:** `outputs/variables/takeover/2026-02-28_152253/takeover_panel.parquet`
**Regression Audited:** `outputs/econometric/takeover/2026-02-28_152619/`
**Audit Protocol:** `docs/Prompts/Paper_Ready_artifacts.txt`
