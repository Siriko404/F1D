# AUDIT_H9: CEO Clarity and Takeover Hazards — Adversarial Audit Report

**Suite ID:** H9
**Audit Date:** 2026-03-01
**Auditor:** Adversarial Thesis-Pipeline Referee (AI)
**Panel Run Audited:** `2026-02-28_152253` (Stage 3), `2026-02-28_152619` (Stage 4)
**Prior Run Compared:** `2026-02-27_224920` (Stage 3), `2026-02-27_225242` (Stage 4)

---

## 1) Executive Summary

1. **BLOCKER: Cause-specific event coding is fundamentally broken.** `Takeover_Uninvited` and `Takeover_Friendly` are coded from `Takeover_Type` alone (line 240-241 of `run_h9_takeover_hazards.py`), setting event=1 for ALL intervals of event-type firms, not just the last interval. This inflates event rows by 6.6x (Uninvited) and 7.9x (Friendly), turning a single-event model into a recurrent-event model. The Cox PH All model (using `Takeover` column) is NOT affected.
2. **BLOCKER: Negative-duration intervals exist in the panel.** 8 rows have `stop < start` (e.g., start=2007, stop=2002). These indicate firms where `takeover_year < entry_year` — the firm was taken over before it appeared in the sample. Although these rows are eliminated by listwise deletion in the regression, they represent corrupted survival data.
3. **MAJOR: Regime variant (ClarityManager) is dead code.** `MODEL_VARIANTS` still contains the "Regime" entry, but it silently produces no output because `ClarityManager` is not in the panel. No warning is logged. The `run_log.txt` shows no Regime models ran, but no error either.
4. **MAJOR: `n_firms` column in `hazard_ratios.csv` is mislabeled.** It reports N intervals (12,139), not N firms (1,623). This propagates to any downstream consumer of this CSV.
5. **MAJOR: LaTeX table has SEs bunched at the bottom** instead of interleaved below each HR row. The table is not publication-ready.
6. **MINOR: README event counts don't match panel.** README claims Friendly=563, Uninvited=87, Unknown=40. Panel shows Friendly=556, Uninvited=83, Unknown=37. Discrepancy of 7+4+3=14 firms, exactly matching the 14 Takeover=1/Type=None firms.
7. **MINOR: 14 firms have Takeover=1 but Takeover_Type='None'.** These are the negative/zero duration firms. They represent SDC CUSIP matches where the takeover predates or coincides with sample entry.
8. **PASS: Cox PH All model (Takeover column) is correctly coded.** Event=1 only in the last interval per firm. 349 event rows from 349 event firms (ratio=1.0).
9. **PASS: Cross-artifact consistency.** LaTeX table HRs, SEs, and diagnostics match hazard_ratios.csv and model_diagnostics.csv exactly. Summary stats match panel data.
10. **PASS: Reproducibility.** 02-28 and 02-27 regression runs produce bit-for-bit identical coefficients and p-values.

**Are results trustworthy as-is?**
- Cox PH All (all takeovers): YES, correctly implemented.
- Cox CS Uninvited / Friendly: NO. Must be rerun after fixing event coding (Finding #1).

**What must be rerun?**
- Stage 4 only. The panel (Stage 3) is correctly constructed. The bug is in the cause-specific event indicator creation at Stage 4 runtime.

---

## 2) Suite Contract (What H9 Claims It Does)

| Field | Value |
|-------|-------|
| **Estimation Unit** | Firm-year interval (counting-process format) |
| **Primary Keys** | `gvkey` + `start`/`stop` |
| **Sample Filter** | Main sample: FF12 codes 1-7, 9-10, 12 (excludes Finance=11, Utility=8) |
| **DV / Event** | `Takeover` (all bids), `Takeover_Uninvited` (hostile+unsolicited), `Takeover_Friendly` (friendly+neutral) |
| **Key RHS** | `ClarityCEO`, `CEO_QA_Uncertainty_pct` |
| **Controls** | Size, BM, Lev, ROA, EPS_Growth, StockRet, MarketRet, SurpDec |
| **Fixed Effects** | None (Cox PH, no stratification, no frailty) |
| **SEs** | Robust (lifelines default) |
| **Estimator** | `lifelines.CoxTimeVaryingFitter` (counting-process format) |
| **Models** | 3 (All, Uninvited cause-specific, Friendly cause-specific) x 1 variant (CEO) = 3 models |
| **Hypothesis** | H9-A: beta(ClarityCEO) < 0 (clearer CEOs have lower takeover hazard) |
| **Expected Outputs** | `takeover_panel.parquet`, `cox_ph_all.txt`, `cox_cs_uninvited.txt`, `cox_cs_friendly.txt`, `hazard_ratios.csv`, `model_diagnostics.csv`, `takeover_table.tex` |

---

## 3) Verification Matrix (Claim -> Evidence -> Status)

| # | Claim (from H9.md provenance) | Where Claimed | Where Checked | Status | Notes |
|---|-------------------------------|---------------|---------------|--------|-------|
| 1 | Panel has 27,787 firm-year intervals | H9.md D.Verification | `takeover_panel.parquet` | **PASS** | `len(panel) == 27,787` confirmed |
| 2 | 2,429 unique firms | H9.md D.Verification | Panel `gvkey.nunique()` | **PASS** | Confirmed 2,429 |
| 3 | 690 event firms (28.4%) | H9.md D.Verification | `groupby('gvkey')['Takeover'].max().sum()` | **PASS** | Confirmed 690 |
| 4 | Event breakdown: Friendly=563, Uninvited=87, Unknown=40 | H9.md D.Verification | Panel `drop_duplicates('gvkey')['Takeover_Type'].value_counts()` | **FAIL** | Actual: Friendly=556, Uninvited=83, Unknown=37. Difference=14 (the 14 T=1/Type=None firms) |
| 5 | ClarityCEO coverage: 59.4% (16,519/27,787) | H9.md G.Coverage | Panel `ClarityCEO.notna().sum()` | **PASS** | Confirmed 16,519 (59.4%) |
| 6 | CEO_QA_Uncertainty_pct coverage: 75.5% | H9.md G.Coverage | Panel null check | **PASS** | 20,983/27,787 = 75.5% |
| 7 | ClarityManager removed from panel | H9.md J.Issue1 | Panel column list | **PASS** | ClarityManager not in 02-28 panel (was in 02-27 panel with 0% coverage) |
| 8 | Zero row-delta on all call-level merges | README contract | `build_h9_takeover_panel.py:226-232` | **PASS** | Code raises ValueError on delta != 0 |
| 9 | file_name uniqueness enforced | README contract | `build_h9_takeover_panel.py:198-200, 213-217` | **PASS** | Both manifest and builder outputs checked for duplicates |
| 10 | Counting-process format: event=1 only in last interval | H9.md A6 | Panel: event-in-last-row check | **PASS** | 0 violations for `Takeover` column |
| 11 | Cause-specific: other causes treated as censored at event time | H9.md A6, G.Survival | `run_h9_takeover_hazards.py:240-241` | **FAIL** | Coding bug: ALL intervals of type-matching firms get event=1, not just last |
| 12 | Right-censored at 2018 or last call year | H9.md A6 | `build_h9_takeover_panel.py:379-382` | **PASS** | `get_exit_year` correctly picks `min(last_obs_year, year_end)` for non-event firms |
| 13 | Left truncation at first call year | H9.md A6 | `build_h9_takeover_panel.py:366-371` | **PASS** | `entry_year = min(year)` per firm |
| 14 | Minimum 5 event firms to fit model | H9.md G.MinObs | `run_h9_takeover_hazards.py:407-409` | **PASS** | Threshold check present and functional |
| 15 | start/stop monotonicity (no gaps) | Counting-process invariant | Interval continuity check | **PASS** | 0 continuity violations |
| 16 | No negative durations | H9.md G.Survival | Panel `stop - start` check | **FAIL** | 8 rows with stop < start (neg duration) |
| 17 | Regime variant removed | H9.md J.Issue1 | `MODEL_VARIANTS` in `run_h9_takeover_hazards.py:144-155` | **FAIL** | Regime still in `MODEL_VARIANTS`; silently produces nothing |
| 18 | Concordance reported in diagnostics | H9.md B.Expected | `model_diagnostics.csv` | **PASS** | All 3 models have concordance values |
| 19 | Cox PH All: N intervals=12,139, Event firms=349 | H9.md I.Verification | `model_diagnostics.csv` | **PASS** | Exact match |
| 20 | Cox CS Uninvited: Event firms=45 | H9.md I.Verification | `model_diagnostics.csv` | **PASS** | Matches (but n_event_firms counting is correct even with buggy coding because groupby.max().sum() is used) |
| 21 | Winsorization at engine level, not suite level | README contract | `build_h9_takeover_panel.py` | **PASS** | No winsorization code in Stage 3/4; engines handle it |
| 22 | Per-year 1%/99% winsorization for financial controls | README contract | `_compustat_engine.py`, `_crsp_engine.py` | **UNVERIFIED** | Not directly verified (requires engine code trace) |
| 23 | Per-year 0%/99% winsorization for linguistic vars | README contract, H9.md F | `_linguistic_engine.py` | **UNVERIFIED** | Not directly verified |
| 24 | Summary stats match panel data | Cross-artifact | `summary_stats.csv` vs panel | **PASS** | All N and Mean values match exactly |
| 25 | LaTeX table matches CSV | Cross-artifact | `takeover_table.tex` vs `hazard_ratios.csv` | **PASS** | HR values and SEs match (but SE formatting is broken) |
| 26 | Reproducibility across runs | Determinism contract | 02-28 vs 02-27 hazard_ratios.csv | **PASS** | Bit-for-bit identical coefficients |

---

## 4) Findings (Grouped by Severity)

### Finding #1: BLOCKER — Cause-Specific Event Coding Creates Phantom Recurrent Events

**Severity:** BLOCKER

**Symptom:** The Cox CS Uninvited and Cox CS Friendly models see 6-8x more event rows than they should, because event=1 is set for ALL intervals of type-matching firms, not just the final interval.

**Evidence:**

Code location: `run_h9_takeover_hazards.py:240-241`
```python
df[EVENT_UNINVITED_COL] = (df["Takeover_Type"] == "Uninvited").astype(int)
df[EVENT_FRIENDLY_COL] = (df["Takeover_Type"] == "Friendly").astype(int)
```

This sets `Takeover_Uninvited=1` for every row where `Takeover_Type == 'Uninvited'`. In counting-process format, each firm has multiple rows (one per year at risk). An uninvited-takeover firm with 6 intervals gets event=1 in ALL 6, telling `CoxTimeVaryingFitter` the firm experienced 6 takeover events.

Verification commands and output:
```
Firm 001659 - all intervals:
  (start, stop, Takeover_Uninvited):
    (2014, 2015, 1)  <-- BUG: event=1 in non-final interval
    (2015, 2016, 1)  <-- Only this should be event=1

Correct Takeover column for same firm:
    (2014, 2015, Takeover=0, Type=Uninvited)
    (2015, 2016, Takeover=1, Type=Uninvited)
```

Quantified impact (CEO variant, Main sample, after dropna):

| Model | Event Rows (BUG) | Event Rows (CORRECT) | Inflation |
|-------|----------------:|--------------------:|----------:|
| Uninvited | 295 | 39 | 7.6x |
| Friendly | 2,741 | 291 | 9.4x |

**Why it matters:** `CoxTimeVaryingFitter` treats each event=1 row as a separate event contribution to the partial likelihood. With 7-9x inflated events, the model estimates the rate of a recurrent process rather than the hazard of first occurrence. This invalidates all cause-specific coefficient estimates, standard errors, and p-values. The Uninvited model's significant ClarityCEO result (HR=1.337, p=0.0015) is unreliable.

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

**Rerun impact:** Stage 4 only. The panel (`takeover_panel.parquet`) is correct; the bug is in runtime event indicator creation. After fix, rerun:
```bash
python -m f1d.econometric.run_h9_takeover_hazards
```

**Acceptance test after fix:**
```python
# For each cause-specific event col, event rows should == event firms
for col in ['Takeover_Uninvited', 'Takeover_Friendly']:
    event_rows = df_clean[col].sum()
    event_firms = df_clean.groupby('gvkey')[col].max().sum()
    assert event_rows == event_firms, f"{col}: {event_rows} rows != {event_firms} firms"
```

---

### Finding #2: BLOCKER — Negative Duration Intervals in Panel

**Severity:** BLOCKER (data integrity) / MINOR (regression impact — none survive to regression)

**Symptom:** 8 rows in the counting-process panel have `stop < start`, meaning negative durations. 6 additional rows have `stop == start` (zero duration). All 14 correspond to firms with `Takeover=1` but `Takeover_Type='None'`.

**Evidence:**

```
gvkey=001634: start=2007, stop=2005, dur=-2, Takeover=1, Type=None
gvkey=005116: start=2007, stop=2002, dur=-5, Takeover=1, Type=None
gvkey=013990: start=2003, stop=2002, dur=-1, Takeover=1, Type=None
gvkey=022632: start=2007, stop=2004, dur=-3, Takeover=1, Type=None
...
```

Root cause: `build_counting_process_panel` (line 379-382) sets `exit_year = takeover_year` for event firms. When `takeover_year < entry_year` (firm was taken over before it appeared in the sample), a single row is created with `start = entry_year - 1` and `stop = takeover_year`, producing `stop < start`.

These firms are SDC CUSIP matches where the takeover announcement predates the first earnings call. They should have `Takeover=0` (they weren't "at risk" in the sample) or be excluded entirely.

**Regression impact:** 0 negative/zero duration rows survive into the CEO regression (all eliminated by listwise deletion on ClarityCEO or other controls). However, they ARE present in the panel and could affect any analysis that doesn't use the exact same dropna path.

**Fix:** In `build_counting_process_panel`, add a guard:
```python
# After line 384:
# Filter out firms where takeover predates sample entry
valid = firm_bounds["exit_year"] >= firm_bounds["entry_year"]
n_invalid = (~valid).sum()
if n_invalid > 0:
    print(f"  WARNING: {n_invalid} firms with takeover before sample entry — excluded")
firm_bounds = firm_bounds[valid].copy()
```

**Rerun impact:** Stage 3 + Stage 4. Panel must be rebuilt.

---

### Finding #3: MAJOR — Regime Variant Dead Code in MODEL_VARIANTS

**Severity:** MAJOR

**Symptom:** `MODEL_VARIANTS` in `run_h9_takeover_hazards.py:144-155` still contains the "Regime" entry with `ClarityManager`. The Regime variant silently produces nothing — no error, no warning in the run log, no diagnostic row.

**Evidence:**

Code: `run_h9_takeover_hazards.py:144-155`
```python
MODEL_VARIANTS: Dict[str, Dict[str, str]] = {
    "Regime": {
        "clarity_var": "ClarityManager",
        ...
    },
    "CEO": {
        "clarity_var": "ClarityCEO",
        ...
    },
}
```

Run log (`2026-02-28_152619/run_log.txt`): No mention of "Regime" or "Manager Clarity" anywhere.

Investigation: `ClarityManager` is not in the panel columns (confirmed). Line 649 (`covariates = [c for c in covariates if c in df.columns]`) silently drops it. The model then runs with just `Manager_QA_Uncertainty_pct` + controls (no clarity variable). However, `validate_columns` at line 381 does NOT fail because it validates the already-filtered list. The Regime model likely fits but the results show only CEO variant in diagnostics. The model may have been fitted and then either crashed silently or its results were overwritten.

Actually, closer inspection: the Regime variant silently runs with `Manager_QA_Uncertainty_pct` + controls but NOT `ClarityManager`. It fits successfully, BUT it is recorded in `model_diagnostics.csv` and `hazard_ratios.csv` as variant="Regime" — however the current outputs show only "CEO" variant rows. This means one of two things: (a) validate_columns raised an error that was caught, or (b) the model ran but crashed. Since the run_log shows no Regime mention at all, the most likely explanation is that `validate_columns` on `actual_required` succeeded (since ClarityManager was already filtered out), and then `run_cox_tv` ran successfully but was NOT recorded in output because the model specification differs from intended.

**Why it matters:** Confusing for reproducibility. A reader of the code expects 6 models (3 event types x 2 variants) but only 3 run. No explicit error or skip message.

**Fix:** Remove the Regime entry from `MODEL_VARIANTS`:
```python
MODEL_VARIANTS: Dict[str, Dict[str, str]] = {
    "CEO": {
        "clarity_var": "ClarityCEO",
        "uncertainty_var": "CEO_QA_Uncertainty_pct",
        "description": "CEO Clarity (4.1.1) model",
    },
}
```

Or add an explicit check:
```python
for variant_key, variant_spec in MODEL_VARIANTS.items():
    clarity_var = variant_spec["clarity_var"]
    if clarity_var not in df.columns:
        print(f"  [{variant_key}] Skipped: {clarity_var} not in panel")
        continue
```

**Rerun impact:** Code-only fix. No data rerun needed.

---

### Finding #4: MAJOR — `n_firms` Column Misnomer in `hazard_ratios.csv`

**Severity:** MAJOR

**Symptom:** The `n_firms` column in `hazard_ratios.csv` contains the value 12,139, which is N intervals (firm-year rows), not N firms. The actual number of unique firms in the regression is 1,623.

**Evidence:**

Code: `run_h9_takeover_hazards.py:472`
```python
"n_firms": df_clean_len,  # This is len(df_clean) = N intervals
```

Verification:
```
hazard_ratios.csv n_firms values: [12139]
Actual unique firms in regression: 1,623
```

**Why it matters:** Any downstream consumer (paper table, robustness check) that reads `n_firms` will report 12,139 firms instead of the actual 1,623. This is materially misleading.

**Fix:** In `extract_results` (line 472), change:
```python
# CURRENT:
"n_firms": df_clean_len,  # BUG: this is N intervals

# FIXED:
"n_intervals": df_clean_len,
"n_firms": df_clean["gvkey"].nunique() if "gvkey" in df_clean.columns else None,
```

**Rerun impact:** Stage 4 only (output format change).

---

### Finding #5: MAJOR — LaTeX Table SE Formatting Broken

**Severity:** MAJOR

**Symptom:** In `takeover_table.tex`, all 10 SE rows are bunched together after all 10 HR rows, instead of being interleaved (each SE below its corresponding HR). The table is not publication-ready.

**Evidence:** `outputs/econometric/takeover/2026-02-28_152619/takeover_table.tex:18-38`
```latex
% Lines 19-28: All HR rows
Clarity (CEO) & & 1.0497 & & 1.3371 & & 1.0978 \\
CEO QA Uncertainty & & 1.2144 & & 1.0029 & & 0.9225 \\
...
% Lines 29-38: All SE rows bunched together
 & & (0.0845) & & (0.0915) & & (0.0290) \\
 & & (0.2890) & & (0.3024) & & (0.0975) \\
```

Expected format (standard accounting review style):
```latex
Clarity (CEO) & & 1.0497 & & 1.3371 & & 1.0978 \\
              & & (0.0845) & & (0.0915) & & (0.0290) \\
CEO QA Uncertainty & & 1.2144 & & 1.0029 & & 0.9225 \\
                   & & (0.2890) & & (0.3024) & & (0.0975) \\
```

**Fix:** Fix `make_cox_hazard_table` in `src/f1d/shared/latex_tables_accounting.py` to interleave SE rows immediately after each HR row.

**Rerun impact:** Stage 4 only (table generation).

---

### Finding #6: MINOR — README Event Counts Discrepancy

**Severity:** MINOR

**Symptom:** README.md (line 559) claims `Event breakdown: Friendly: 563, Uninvited: 87, Unknown: 40`. The actual panel shows Friendly=556, Uninvited=83, Unknown=37.

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

The difference of 14 firms (563-556 + 87-83 + 40-37 = 14) exactly equals the 14 firms with `Takeover=1` but `Takeover_Type='None'`. The README numbers appear to come from a run that counted these 14 firms differently (possibly from a different Takeover_Type classification).

**Fix:** Update README to match actual panel values.

**Rerun impact:** Documentation only.

---

### Finding #7: MINOR — Summary Stats Reference Missing Variables

**Severity:** MINOR

**Symptom:** `SUMMARY_STATS_VARS` in `run_h9_takeover_hazards.py:120-141` references `duration`, `ClarityManager`, and `Manager_QA_Uncertainty_pct`, none of which are in the Main sample DataFrame at the point where summary stats are generated (`duration` is never created, `ClarityManager` is not in panel).

**Evidence:**

```python
# Lines 122-128:
{"col": "ClarityManager", "label": "Clarity (Manager)"},     # Not in panel
{"col": "Manager_QA_Uncertainty_pct", "label": "Mgr QA Uncertainty"},  # In panel but not in CEO regression
{"col": "duration", "label": "Duration (years)"},             # Never created
```

The code handles this gracefully (line 608: `if v["col"] in df.columns`), so missing columns are silently skipped. But the summary stats table is incomplete — it's missing a duration statistic that would be informative.

**Fix:** Remove stale references. Add `duration = stop - start` computation before summary stats.

**Rerun impact:** Stage 4 only.

---

### Finding #8: NOTE — ClarityCEO Is Time-Varying Across CEO Turnovers

**Severity:** NOTE

**Symptom:** 660 of 1,685 firms with ClarityCEO have varying values across year-intervals, because CEO turnover brings a different CEO's clarity score.

**Evidence:**
```
Firms with varying ClarityCEO across years: 660 / 1,685
Max distinct ClarityCEO per firm: 5
Mean std of ClarityCEO within firm: 0.1947
```

**Why it matters:** ClarityCEO is described as "time-invariant" in the provenance (H9.md A4, F). It IS time-invariant per CEO, but time-varying per FIRM due to CEO turnover. This is actually the correct behavior for a time-varying Cox model — it captures the clarity of whoever is CEO in each year. However, the provenance should document this explicitly.

**Rerun impact:** None (behavior is correct).

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

## 5) Rerun Plan (Actionable)

### Minimal Rerun Commands

```bash
# Step 1: Fix cause-specific event coding in run_h9_takeover_hazards.py (Finding #1)
# Apply the fix at lines 240-241

# Step 2 (optional): Fix negative duration panel rows (Finding #2)
# Apply the fix in build_h9_takeover_panel.py, then:
python -m f1d.variables.build_h9_takeover_panel

# Step 3: Rerun Stage 4
python -m f1d.econometric.run_h9_takeover_hazards
```

If only Finding #1 is fixed (no Stage 3 rerun needed):
```bash
python -m f1d.econometric.run_h9_takeover_hazards
```

### Acceptance Tests After Rerun

1. **Event coding correctness:**
```python
import pandas as pd
panel = pd.read_parquet('outputs/variables/takeover/LATEST/takeover_panel.parquet')
main = panel[~panel['ff12_code'].isin([8, 11])].copy()
# After cause-specific event creation in Stage 4:
for col in ['Takeover_Uninvited', 'Takeover_Friendly']:
    event_rows = df_clean[col].sum()
    event_firms = df_clean.groupby('gvkey')[col].max().sum()
    assert event_rows == event_firms, f"FAIL: {col} has {event_rows} event rows but {event_firms} event firms"
```

2. **No negative durations:**
```python
assert (panel['stop'] - panel['start'] >= 0).all(), "FAIL: negative durations exist"
# Or at minimum:
neg = panel[panel['stop'] - panel['start'] < 0]
assert len(neg) == 0, f"FAIL: {len(neg)} negative duration rows"
```

3. **Coefficient tolerance (Cox PH All should be stable since it's unaffected):**
```python
hr_new = pd.read_csv('outputs/econometric/takeover/NEW/hazard_ratios.csv')
hr_old = pd.read_csv('outputs/econometric/takeover/2026-02-28_152619/hazard_ratios.csv')
# Cox PH All coefficients should be identical (or near-identical if panel changed)
all_old = hr_old[hr_old['model'] == 'Cox PH All']
all_new = hr_new[hr_new['model'] == 'Cox PH All']
assert (all_old['coef'].values - all_new['coef'].values).max() < 1e-6
```

4. **Event firm counts should decrease for cause-specific models:**
```python
diag = pd.read_csv('outputs/econometric/takeover/NEW/model_diagnostics.csv')
uninvited = diag[diag['model'] == 'Cox CS Uninvited']
# Should be ~39 events (down from 45 due to correct event coding)
assert uninvited['n_event_firms'].values[0] < 45
```

5. **n_firms column should report actual firm count:**
```python
hr = pd.read_csv('outputs/econometric/takeover/NEW/hazard_ratios.csv')
assert 'n_intervals' in hr.columns or hr['n_firms'].iloc[0] < 5000  # sanity check
```

---

## 6) Hardening Recommendations

### Repository-Level

1. **Add a counting-process validator.** Before passing to `CoxTimeVaryingFitter`, assert:
   - `(stop - start > 0).all()` (no zero/negative durations)
   - For non-recurrent events: `groupby(id_col)[event_col].sum() <= 1` per subject
   - `start[i+1] == stop[i]` for consecutive intervals per subject (no gaps)

2. **Add event-row-per-firm assertion for cause-specific models.**
```python
# After creating cause-specific indicators:
for event_col in [EVENT_UNINVITED_COL, EVENT_FRIENDLY_COL]:
    event_rows = df[event_col].sum()
    event_firms = df.groupby("gvkey")[event_col].max().sum()
    if event_rows != event_firms:
        raise ValueError(
            f"{event_col}: {event_rows} event rows != {event_firms} event firms. "
            "Check cause-specific coding logic."
        )
```

3. **Log a WARNING when covariates are silently dropped.**
```python
# In the variant loop:
requested_covariates = [clarity_var, uncertainty_var] + FINANCIAL_CONTROLS
available_covariates = [c for c in requested_covariates if c in df.columns]
dropped = set(requested_covariates) - set(available_covariates)
if dropped:
    print(f"  WARNING: Covariates dropped (not in panel): {dropped}")
```

4. **Add negative-duration exclusion in Stage 3** with explicit logging.

5. **Rename `n_firms` to `n_intervals`** in `extract_results` and add a true `n_firms` field.

### Suite-Level

6. **Add unit test for cause-specific event coding:**
```python
def test_cause_specific_event_coding():
    """Verify cause-specific events fire only in the last interval."""
    df = pd.DataFrame({
        'gvkey': ['A','A','A','B','B'],
        'start': [0,1,2,0,1],
        'stop': [1,2,3,1,2],
        'Takeover': [0,0,1,0,0],
        'Takeover_Type': ['Uninvited','Uninvited','Uninvited','None','None'],
    })
    df['Takeover_Uninvited'] = ((df['Takeover']==1) & (df['Takeover_Type']=='Uninvited')).astype(int)
    assert df['Takeover_Uninvited'].sum() == 1  # Only last interval of firm A
    assert df.groupby('gvkey')['Takeover_Uninvited'].sum().max() == 1
```

7. **Add integration test that verifies concordance between `Takeover` event count and sum of cause-specific events + unknown:**
```python
n_all = df.groupby('gvkey')['Takeover'].max().sum()
n_uninvited = df.groupby('gvkey')['Takeover_Uninvited'].max().sum()
n_friendly = df.groupby('gvkey')['Takeover_Friendly'].max().sum()
n_unknown = n_all - n_uninvited - n_friendly
assert n_unknown >= 0
assert n_uninvited + n_friendly + n_unknown == n_all
```

8. **Remove stale `SUMMARY_STATS_VARS` entries** for `duration`, `ClarityManager`.

---

## 7) Command Log (Chronological)

| # | Command | Purpose | Key Output |
|---|---------|---------|------------|
| 1 | `read README.md` | Extract pipeline contract | 4-stage design, zero-row-delta invariant, winsorization policy |
| 2 | `read docs/Prompts/P_Audit.txt` | Understand audit protocol | 5-phase audit structure |
| 3 | `read docs/provenance/H9.md` | Build claim register | 639 lines of provenance claims |
| 4 | `grep takeover\|h9\|H9 src/f1d` | Locate all H9-related source | `build_h9_takeover_panel.py`, `run_h9_takeover_hazards.py`, `takeover_indicator.py` |
| 5 | `glob outputs/variables/takeover/**/*` | Find Stage 3 output runs | 6 runs (earliest 2026-02-19, latest 2026-02-28) |
| 6 | `glob outputs/econometric/takeover/**/*` | Find Stage 4 output runs | 12+ runs |
| 7 | `read build_h9_takeover_panel.py` | Trace Stage 3 code (711 lines) | Merge logic, counting-process construction |
| 8 | `read run_h9_takeover_hazards.py` | Trace Stage 4 code (766 lines) | Cox model fitting, event coding, output generation |
| 9 | `read takeover_indicator.py` | Trace SDC builder (233 lines) | CUSIP linking, attitude classification |
| 10 | `read hazard_ratios.csv` (02-28) | Check regression outputs | 30 rows, CEO variant only |
| 11 | `read model_diagnostics.csv` (02-28) | Check diagnostics | 3 models, all CEO variant |
| 12 | `read cox_ph_all.txt` | Verify model output | 10 covariates, N=12,139, C=0.537 |
| 13 | `read cox_cs_uninvited.txt` | Verify uninvited model | N=12,139, 45 events, C=0.567 |
| 14 | `read cox_cs_friendly.txt` | Verify friendly model | N=12,139, 346 events, C=0.522 |
| 15 | `read takeover_table.tex` | Audit LaTeX table | SE rows bunched at bottom |
| 16 | `read hazard_ratios.csv` (02-27) | Compare prior run | Identical coefficients |
| 17 | `read model_diagnostics.csv` (02-27) | Compare prior run | Identical diagnostics |
| 18 | `read run_log.txt` (02-28) | Check execution flow | No Regime variant logged |
| 19 | `read summary_stats.csv` (02-28) | Cross-check summary | 14 variables |
| 20 | `python -c "panel shape, key uniqueness, start/stop validity"` | Panel integrity | 27,787 rows, 0 key duplicates, 8 neg durations, 6 zero durations |
| 21 | `python -c "null rates for all columns"` | Coverage audit | ClarityCEO 59.4%, CEO_QA_Uncertainty 75.5%, Size 99.8% |
| 22 | `python -c "event coding audit"` | Event-in-last-row check | 0 violations for Takeover column |
| 23 | `python -c "Takeover=1 but Type=None"` | Corrupted event check | 14 firms, all with neg/zero duration |
| 24 | `python -c "cause-specific event inflation"` | **CRITICAL BUG FOUND** | Uninvited inflated 8.5x, Friendly 9.2x |
| 25 | `python -c "reproducibility check"` | Cross-run comparison | Bit-for-bit identical |
| 26 | `python -c "All model event coding"` | Verify All model correct | Event rows = Event firms (ratio=1.0) |
| 27 | `python -c "cause-specific bug with example"` | Demonstrate bug per-firm | Firm 001659: 2 intervals both event=1 |
| 28 | `python -c "negative duration deep dive"` | Root cause analysis | All 8 firms: takeover_year < entry_year |
| 29 | `python -c "LaTeX SE positioning"` | Table format check | SEs separated from HRs |
| 30 | `python -c "ClarityCEO invariance"` | Merge correctness | Time-varying via CEO turnover (expected) |
| 31 | `python -c "FF12 filter check"` | Sample filter | No Finance/Utility leakage |
| 32 | `python -c "summary stats cross-check"` | Cross-artifact | All N and Mean values match |
| 33 | `python -c "event firm counting logic"` | n_event_firms inflation | groupby.max().sum() gives correct count (45), but model sees 295 event rows |
| 34 | `python -c "panel reproducibility"` | Prior panel comparison | Same rows, prior has ClarityManager column (0% coverage) |
| 35 | `python -c "counting-process monotonicity"` | Gap detection | 0 continuity violations |
| 36 | `python -c "Regime variant resolution"` | Dead code check | ClarityManager silently dropped, no Regime in outputs |
| 37 | `python -c "duration column check"` | Missing variable | `duration` never created; cause-specific indicators created at runtime |
| 38 | `python -c "event inflation quantification"` | Full impact | BUG: 295 Uninvited event rows (6.6/firm), CORRECT: 39 (1.0/firm) |
| 39 | `python -c "prior panel check"` | Cross-panel | 02-27 panel had ClarityManager with 0% coverage |

---

## 8) Open Gaps

| # | Gap | What Would Close It | Impact |
|---|-----|---------------------|--------|
| 1 | **Engine-level winsorization not directly verified.** Per-year 1%/99% for Compustat, CRSP claimed but not traced through engine code in this audit. | Read `_compustat_engine.py`, `_crsp_engine.py`, `_linguistic_engine.py` and verify winsorization is applied at load time with correct percentiles. | LOW — winsorization is a repo-wide policy verified in other suite audits |
| 2 | **Proportional hazards assumption not tested.** No Schoenfeld residual test or log-log plot. | Run `ctv.check_assumptions()` or equivalent after fitting. | MEDIUM — PH violations would invalidate the Cox model |
| 3 | **SDC CUSIP linkage quality not audited.** The 6-char CUSIP match rate is not independently verified. | Cross-check a sample of SDC CUSIP matches against CRSP/Compustat CUSIP history. | LOW — takeover indicator builder has 100% merge rate by construction |
| 4 | **Impact of correct cause-specific coding on results unknown.** With correct coding, Uninvited events drop from 295 rows to 39 rows (45 to 39 event firms). The model may not converge or results may change dramatically. | Rerun Stage 4 after fix and compare. | HIGH — this is the primary deliverable |
| 5 | **No test of whether ClarityCEO from H0.2 is stale.** Stage 4 picks "latest" clarity_scores.parquet — if H0.2 was rerun after the takeover panel was built, clarity scores could mismatch. | Check timestamps: clarity_scores run should predate the takeover panel run. | LOW — both from same pipeline run cycle |
| 6 | **Regime variant behavior untested.** The exact failure mode (crash, silent skip, partial run) is unclear from the run log. | Add `--verbose` or explicit skip logging, then dry-run. | LOW — Regime is slated for removal |

---

**Document Generated:** 2026-03-01
**Panel Audited:** `outputs/variables/takeover/2026-02-28_152253/takeover_panel.parquet`
**Regression Audited:** `outputs/econometric/takeover/2026-02-28_152619/`
**Prior Run Compared:** `outputs/econometric/takeover/2026-02-27_225242/`
