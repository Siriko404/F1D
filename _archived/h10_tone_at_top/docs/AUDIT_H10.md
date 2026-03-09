# AUDIT_H10: Tone-at-the-Top Transmission — Adversarial Audit Report

**Audit Date:** 2026-03-01
**Suite ID:** H10 (H_TT: Tone-at-the-Top)
**Auditor:** Adversarial Pipeline Referee
**Provenance Doc:** `docs/provenance/H10.md`
**Panel Builder:** `src/f1d/variables/build_h10_tone_at_top_panel.py`
**Econometric Runner:** `src/f1d/econometric/run_h10_tone_at_top.py`
**Latest Stage 3 Run:** `outputs/variables/tone_at_top/2026-02-27_225254/`
**Latest Stage 4 Run:** `outputs/econometric/tone_at_top/2026-02-27_225837/`

---

## 1) Executive Summary (Top Risks)

1. **MAJOR — "Main" sample = ALL industries, not non-fin/non-util.** `run_h10_tone_at_top.py:1084-1093` uses `call_panel` (all 112,968 calls) when `sample == "Main"` instead of filtering to `sample == "Main"` (88,205 calls). M1 Main N=43,570 includes 6,793 Finance + 1,378 Utility observations. M2 Main N=1,697,632 includes all industries. This contradicts the README definition ("Main: FF12 codes 1-7, 9-10, 12") and the provenance Section E sample counts.

2. **MAJOR — Duplicate entity-time index in M1 PanelOLS.** 347 firm-quarters have >1 call in the M1 regression sample (694 rows, 0.8%). PanelOLS with `set_index(["gvkey", "yq_id"])` creates a non-unique MultiIndex. linearmodels may silently handle this but the behavior is undefined for within-transformation with duplicate entity-time pairs.

3. **MAJOR — LaTeX table clustering note is wrong for M2.** `tone_at_top_full.tex:53` states "Standard errors (two-way clustered by Firm × CEO)" but M2 clusters by Firm × Call per the code (`run_h10_tone_at_top.py:250-253`) and provenance Section A5. The published table would mislead readers about inference.

4. **MAJOR — Placebo test failure undermines causal claim.** M2 placebo (future CEO uncertainty → current manager uncertainty) shows β=0.0373, t=31.49, stronger than the main IV (β=0.0426, t=19.37 for expanding mean). This suggests within-call uncertainty clustering dominates the signal, not directional CEO→manager transmission.

5. **MINOR — Turn_Uncertainty_pct in M2 is unwinsorized.** Values range 0–100% with 478 turns >50%. The IHS transform mitigates but does not eliminate extreme value influence. No winsorization applied at Stage 3 or Stage 4.

6. **MINOR — Winsorization inconsistency between CEO and CFO uncertainty.** CEO_QA_Uncertainty_pct is per-year 1/99% winsorized (via LinguisticEngine); CFO_QA_Uncertainty_pct is pooled 1/99% (via `base._finalize_data()`). Provenance Section G incorrectly claims "pooled 1/99%" for all linguistic percentages.

7. **MINOR — 2002 entirely absent from M1 regression sample.** ClarityStyle_Realtime requires ≥4 prior CEO calls, eliminating all 2002 observations. N Quarters = 64 (not 68). Documented as expected behavior but not explicitly stated in provenance.

8. **NOTE — CEO_Unc_Lag1 is 57.9% zeros.** The ffill propagation means many manager turns inherit 0.0 from the first CEO turn's lag (which is NaN→0 after ffill). This affects the robustness M2_lag1 specification.

9. **NOTE — Cross-artifact consistency verified.** Coefficients, t-stats, N obs, and R² match across `coefficients_*.csv`, `results_*.csv`, `model_diagnostics.csv`, `report.md`, and `tone_at_top_full.tex`. No discrepancies found.

10. **NOTE — Reproducibility confirmed.** Prior run (2026-02-22_173053) and latest run (2026-02-27_225254) produce identical reconciliation table row counts at all 6 stages. `get_latest_output_dir()` correctly resolves the latest panel.

**Are results trustworthy as-is?**
M2 (turn-level) results are statistically valid but the "Main=All" sample definition inflates N and mixes industry effects. The placebo test failure is a serious interpretive concern acknowledged in the provenance but under-emphasized. M1 (call-level) has the additional entity-time duplicate issue. After fixing Finding #1 (sample filter), results must be rerun.

**What must be rerun?**
Stage 4 must be rerun after fixing the sample filter bug. Stage 3 does not need rerun (panel is correct; the filter is applied at Stage 4 runtime).

---

## 2) Suite Contract (What H10 Claims It Does)

| Field | Value |
|-------|-------|
| **Estimation Unit** | M1: Call-level (firm-quarter); M2: Speaker-turn within Q&A |
| **Primary Keys** | M1: `file_name`; M2: (`file_name`, `turn_index`, `speaker_id`) |
| **Sample Filters** | Main (FF12 1-7, 9-10, 12), Finance (FF12=11), Utility (FF12=8) |
| **DV (M1)** | `IHS_CFO_QA_Unc` = arcsinh(CFO_QA_Uncertainty_pct) |
| **DV (M2)** | `IHS_NonCEO_Turn_Unc` = arcsinh(Turn_Uncertainty_pct) |
| **Main IV (M1)** | `ClarityStyle_Realtime` — 4-call rolling EB-shrunk CEO FE |
| **Main IV (M2)** | `IHS_CEO_Prior_QA_Unc` — arcsinh(expanding mean of prior CEO Q&A uncertainty) |
| **Controls (M1)** | Size, BM, Lev, ROA, StockRet, MarketRet, EPS_Growth, SurpDec |
| **Controls (M2)** | None (baseline); turn_index, turn_index_sq, IHS_Analyst_Unc (robustness) |
| **FE (M1)** | Firm (gvkey) + Year-Quarter (yq_id), via PanelOLS entity_effects + time_effects |
| **FE (M2)** | Call (file_name) + Speaker (speaker_id), via AbsorbingLS |
| **SEs (M1)** | Two-way clustered: Firm × CEO |
| **SEs (M2)** | Two-way clustered: Firm × Call (per Addendum C) |
| **Expected Outputs** | Call panel (112,968 rows), Turns panel (1,697,632 rows), LaTeX tables, coefficients CSVs, model_diagnostics.csv, report.md |

---

## 3) Verification Matrix (Claim → Evidence → Status)

| # | Claim | Where Claimed | Where Checked | Status | Notes |
|---|-------|---------------|---------------|--------|-------|
| 1 | Call panel = 112,968 rows | H10.md §B, §C | `python -c`: `len(cp) == 112968` | **PASS** | Verified: 112,968 unique file_names |
| 2 | file_name is unique in call panel | H10.md §I.1 | `cp["file_name"].is_unique == True` | **PASS** | Confirmed |
| 3 | Turns panel = 1,697,632 rows | H10.md §B, §C | `python -c`: `len(tp) == 1697632` | **PASS** | Verified |
| 4 | Turns primary key (file_name, turn_index, speaker_id) unique | H10.md §A1 | `tp.duplicated(subset=[...]).sum() == 0` | **PASS** | Zero duplicates |
| 5 | CEO_Prior_QA_Unc has no NaN in final turns panel | H10.md §E (stage 6 filter) | `tp["CEO_Prior_QA_Unc"].isna().sum() == 0` | **PASS** | All 1,697,632 rows have valid values |
| 6 | Main sample = FF12 1-7, 9-10, 12 (non-fin, non-util) | H10.md §E, README | `run_h10_tone_at_top.py:1084-1093` | **FAIL** | Code uses ALL samples for "Main"; see Finding #1 |
| 7 | M1 Main N = 43,570 | H10.md §H | `model_diagnostics.csv`, `results_main.csv` | **PASS** (count) / **FAIL** (composition) | N matches but includes Finance + Utility; see Finding #1 |
| 8 | M2 Main N = 1,697,632 | H10.md §H | `model_diagnostics.csv` | **PASS** (count) / **FAIL** (composition) | Same issue as #7; all samples included |
| 9 | M1 uses PanelOLS with Firm + YQ FE | H10.md §A2 | `run_h10_tone_at_top.py:138-144` | **PASS** | `entity_effects=True, time_effects=True, drop_absorbed=True` |
| 10 | M2 uses AbsorbingLS with Call + Speaker FE | H10.md §A2 | `run_h10_tone_at_top.py:242-247` | **PASS** | `absorb_df` contains speaker_id + file_name |
| 11 | M1 SEs clustered by Firm × CEO | H10.md §A5 | `run_h10_tone_at_top.py:146-153` | **PASS** | `clusters = DataFrame({"gvkey": ..., "ceo_id": ...})` |
| 12 | M2 SEs clustered by Firm × Call | H10.md §A5, Addendum C | `run_h10_tone_at_top.py:250-253` | **PASS** | `cluster_by_call=True` default; clusters = gvkey + file_name |
| 13 | LaTeX notes state correct clustering | LaTeX table | `tone_at_top_full.tex:53` | **FAIL** | Says "Firm × CEO" for all models; M2 is actually Firm × Call; see Finding #3 |
| 14 | ClarityStyle_Realtime = 4-call rolling, min 4 prior | H10.md §A4 | `ceo_style_realtime.py:93-99, 134` | **PASS** | `window=4, min_calls=4`, shift() ensures strictly prior |
| 15 | ClarityStyle_Realtime has 44.5% missing | H10.md §G | `python -c`: 50,232/112,968 = 44.5% | **PASS** | Matches exactly |
| 16 | CFO_QA_Uncertainty_pct has 12.9% missing | H10.md §G | `python -c`: 14,548/112,968 = 12.9% | **PASS** | Matches exactly |
| 17 | IHS transform = arcsinh(x) | H10.md §A3 | `run_h10_tone_at_top.py:105-107` | **PASS** | `np.arcsinh(series)` |
| 18 | Zero row-delta on call panel merges | README contract | `build_h10_tone_at_top_panel.py:141-145` | **PASS** | ValueError raised if merge changes row count |
| 19 | Deduplication removes 6,820 rows | H10.md §E | `reconciliation_table.csv` | **PASS** | 9,160,874 → 9,154,054 = -6,820 |
| 20 | Manager filter removes 7,088,581 rows | H10.md §E | `reconciliation_table.csv` | **PASS** | Verified |
| 21 | Final filter (require prior CEO) removes 367,841 | H10.md §E | `reconciliation_table.csv` | **PASS** | 2,065,473 → 1,697,632 = -367,841 |
| 22 | Reconciliation stable across runs | Implicit | Prior run (2026-02-22_173053) vs latest | **PASS** | All 6 stages match exactly |
| 23 | Winsorization: pooled 1/99% for linguistic % | H10.md §G | `cfo_qa_uncertainty.py:97`, `ceo_qa_uncertainty.py:30` | **PARTIAL** | CFO = pooled (correct); CEO = per-year via LinguisticEngine (provenance incorrect); see Finding #6 |
| 24 | Turn_Uncertainty_pct winsorized | H10.md §G ("pooled 1/99%") | `python -c`: max = 100.0 | **FAIL** | Not winsorized; raw values from tokenize; see Finding #5 |
| 25 | M2 placebo (Lead1) documented as significant | H10.md §J.1 | `coefficients_Main_M2_placebo_lead.csv` | **PASS** | β=0.0373, t=31.49 — documented; see Finding #4 |
| 26 | Wild cluster bootstrap for small samples | H10.md §A6 | `run_h10_tone_at_top.py:1141-1156` | **PASS** | Applied when `n_firms < 100`; seed=42, 9999 iterations |
| 27 | speaker_id = gvkey + "_" + speaker_name | H10.md §F | `build_h10_tone_at_top_panel.py:453` | **PASS** | Firm-specific speaker identity confirmed |
| 28 | Entity-time uniqueness for PanelOLS | Implicit (linearmodels requirement) | `python -c`: 347 duplicates | **FAIL** | See Finding #2 |
| 29 | Cross-artifact consistency (coefs match across files) | Implicit | Multiple CSVs, LaTeX, report.md | **PASS** | All values match |
| 30 | Output dir resolution correct | README | `get_latest_output_dir()` test | **PASS** | Resolves to 2026-02-27_225254 |

---

## 4) Findings (Grouped by Severity)

### Finding #1 — MAJOR: "Main" Sample Includes All Industries

**Severity:** MAJOR

**Symptom:** M1 Main reports N=43,570 observations but should report ~35,399 if restricted to FF12 non-financial, non-utility firms. M2 Main reports N=1,697,632 but Main-only turns = 1,309,955.

**Evidence:**

- `run_h10_tone_at_top.py:1084-1088`:
  ```python
  call_sub = (
      call_panel
      if sample == "Main"
      else call_panel[call_panel["sample"] == sample]
  )
  ```
- Same pattern at lines 1089-1093 for `turns_sub`.
- Verification:
  ```
  Full panel after M1 listwise deletion: 43,570
    Main: 35,399 / Finance: 6,793 / Utility: 1,378
  Main-only after M1 listwise deletion: 35,399
  ```

**Why it matters:** The "Main" sample is supposed to exclude financial and utility firms (per README, all other hypothesis suites, and the provenance sample classification table). Including them:
1. Inflates sample size and statistical power
2. Mixes regulated industries with the main sample
3. Finance and Utility M1 results are ALSO included in Main, so they are double-counted (once in "Main", once in their own sample)
4. Makes the results inconsistent with all other hypothesis suites (H1–H9) which correctly filter `df_prep[df_prep["sample"] == "Main"]`

**How to verify:**
```bash
cd F1D
python -c "
import pandas as pd
cp = pd.read_parquet('outputs/variables/tone_at_top/2026-02-27_225254/tone_at_top_panel.parquet')
full = cp.dropna(subset=['ClarityStyle_Realtime','CFO_QA_Uncertainty_pct','Size','BM','Lev','ROA','StockRet','MarketRet','EPS_Growth','SurpDec'])
print(full['sample'].value_counts())
print(f'Total: {len(full):,}')  # 43,570 (includes Finance + Utility)
main_only = full[full['sample']=='Main']
print(f'Main-only: {len(main_only):,}')  # 35,399 (correct Main)
"
```

**Fix:**
```python
# run_h10_tone_at_top.py, lines 1084-1093
# BEFORE (buggy):
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

# AFTER (correct):
call_sub = call_panel[call_panel["sample"] == sample].copy()
turns_sub = turns_panel[turns_panel["sample"] == sample].copy()
```

**Rerun impact:** Stage 4 only. Stage 3 panel is correct (sample column is present). After fix:
- Main M1 N will drop from ~43,570 to ~35,399
- Main M2 N will drop from ~1,697,632 to ~1,309,955
- Finance and Utility results are unaffected (already correctly filtered)

---

### Finding #2 — MAJOR: Duplicate Entity-Time Index in M1 PanelOLS

**Severity:** MAJOR

**Symptom:** 347 firm-quarters have >1 earnings call in the M1 regression sample, creating 694 duplicate rows in the PanelOLS entity-time index.

**Evidence:**

- `run_h10_tone_at_top.py:133`: `reg_df = reg_df.set_index(["gvkey", "yq_id"])`
- Verification:
  ```
  Firm-quarters with >1 call in M1 sample: 347
  Total duplicate rows: 694 (0.80% of 43,570)
  ```
- Multiple calls per firm-quarter occur when a firm holds two earnings calls in the same calendar quarter (e.g., preliminary + final, or delayed filings).

**Why it matters:** linearmodels `PanelOLS` behavior with non-unique entity-time MultiIndex is implementation-dependent. It may:
1. Silently overwrite duplicate rows during within-transformation
2. Average duplicate observations
3. Treat them as separate observations (inflating effective sample size)
The exact behavior depends on the pandas version and linearmodels internals, creating a reproducibility risk.

**How to verify:**
```bash
python -c "
import pandas as pd
cp = pd.read_parquet('outputs/variables/tone_at_top/2026-02-27_225254/tone_at_top_panel.parquet')
cp['yq_id'] = (cp['year'].astype(str) + 'Q' + cp['quarter'].astype(str)).astype('category').cat.codes
reg = cp.dropna(subset=['ClarityStyle_Realtime','CFO_QA_Uncertainty_pct','Size','BM','Lev','ROA','StockRet','MarketRet','EPS_Growth','SurpDec'])
dups = reg.groupby(['gvkey','yq_id']).size()
print(dups[dups>1].describe())
"
```

**Fix:** Two options:
1. **Keep last call per firm-quarter** (consistent with other suites):
   ```python
   reg_df = reg_df.sort_values("start_date").drop_duplicates(
       subset=["gvkey", "yq_id"], keep="last"
   )
   ```
2. **Average calls within firm-quarter** (preserves information):
   ```python
   numeric_cols = [dv, iv] + controls
   reg_df = reg_df.groupby(["gvkey", "yq_id", "ceo_id"])[numeric_cols].mean().reset_index()
   ```

**Rerun impact:** Stage 4 only. M1 results may change slightly (347 duplicate obs removed or averaged). M2 unaffected (uses turn-level keys, not entity-time).

---

### Finding #3 — MAJOR: LaTeX Table Clustering Note Incorrect for M2

**Severity:** MAJOR

**Symptom:** `tone_at_top_full.tex:53` states: "Standard errors (two-way clustered by Firm × CEO) in parentheses." This applies to M1 but NOT M2, which uses Firm × Call clustering.

**Evidence:**

- `tone_at_top_full.tex:53`:
  ```latex
  \multicolumn{7}{l}{\parbox{\linewidth}{\footnotesize \textit{Notes:} Standard errors (two-way clustered by Firm $\times$ CEO) in parentheses.}}
  ```
- `run_h10_tone_at_top.py:249-253`: M2 uses `cluster_by_call=True` → clusters = (gvkey, file_name)
- Provenance H10.md §A5 correctly documents Firm × Call for M2

**Why it matters:** Published tables would mislead readers about the variance estimator used for the M2 turn-level results. Reviewers may question the clustering choice.

**Fix:**
```python
# run_h10_tone_at_top.py, line 523 (in generate_accounting_review_latex)
# BEFORE:
lines.append(f"\\multicolumn{{{n_models + 1}}}{{l}}{{\\parbox{{\\linewidth}}{{\\footnotesize \\textit{{Notes:}} Standard errors (two-way clustered by Firm $\\times$ CEO) in parentheses.}}}} \\\\")

# AFTER:
lines.append(f"\\multicolumn{{{n_models + 1}}}{{l}}{{\\parbox{{\\linewidth}}{{\\footnotesize \\textit{{Notes:}} Standard errors in parentheses. M1: two-way clustered (Firm $\\times$ CEO). M2: two-way clustered (Firm $\\times$ Call).}}}} \\\\")
```

**Rerun impact:** Stage 4 only (LaTeX generation).

---

### Finding #4 — MAJOR: Placebo Test Failure Undermines Causal Claim

**Severity:** MAJOR (interpretive, not code bug)

**Symptom:** The M2 placebo specification using FUTURE CEO uncertainty (IHS_CEO_Unc_Lead1) shows β=0.0373, t=31.49 — stronger than most robustness specifications and nearly as large as the baseline expanding mean (β=0.0426, t=19.37).

**Evidence:**

- `coefficients_Main_M2_placebo_lead.csv`:
  ```
  IHS_CEO_Unc_Lead1, 0.0373, 0.00118, 31.49, 0.0
  ```
- Comparison with baseline: `coefficients_Main_M2_baseline.csv`:
  ```
  IHS_CEO_Prior_QA_Unc, 0.0426, 0.00220, 19.37, 0.0
  ```
- The lead coefficient has a **smaller SE** (0.0012 vs 0.0022) and **larger t-stat** (31.49 vs 19.37).

**Why it matters:** If future CEO uncertainty predicts current manager uncertainty nearly as well as past CEO uncertainty, the causal interpretation (CEO → manager transmission) is undermined. The signal likely reflects:
1. Call-level uncertainty clustering (high-uncertainty calls have high uncertainty for all speakers)
2. Within-call time trends not fully absorbed by Call FE
3. Common shocks affecting all speakers simultaneously

The Call FE absorbs the call-level mean, but the **within-call variance** is what drives both the baseline and placebo results. The fact that the lead is significant at t=31 suggests the "transmission" finding is substantially confounded by within-call common factors.

**How to verify:** Already verified from artifact files. Additional check:
```bash
python -c "
import pandas as pd
# Compare N obs between baseline and placebo (different NaN patterns)
baseline = pd.read_csv('outputs/econometric/tone_at_top/2026-02-27_225837/coefficients_Main_M2_baseline.csv')
placebo = pd.read_csv('outputs/econometric/tone_at_top/2026-02-27_225837/coefficients_Main_M2_placebo_lead.csv')
print('Baseline intercept:', baseline[baseline['variable']=='Intercept']['coef'].values)
print('Placebo intercept:', placebo[placebo['variable']=='Intercept']['coef'].values)
"
```

**Fix (interpretive, not code):**
1. The paper must prominently discuss the placebo failure and what it implies
2. Consider a difference-in-differences specification: `IHS_CEO_Prior_QA_Unc - IHS_CEO_Unc_Lead1` as IV
3. Consider lagged CEO uncertainty (CEO_Unc_Lag1) as primary IV instead of expanding mean (it's more plausibly causal but has lower power: β=0.0167, t=15.64)
4. Consider adding `IHS_CEO_Unc_Lead1` as a control in the baseline model to partial out within-call correlation

**Rerun impact:** Interpretive changes only; no rerun needed for current specifications.

---

### Finding #5 — MINOR: Turn_Uncertainty_pct Unwinsorized in M2

**Severity:** MINOR

**Symptom:** The M2 DV (`Turn_Uncertainty_pct`, transformed to IHS) ranges from 0 to 100% with 478 values >50% and 2,422 values >25%.

**Evidence:**
```
Turn_Uncertainty_pct stats:
  min: 0.000000
  max: 100.000000
  p99: 10.000000
  values > 50%: 478
  values > 25%: 2,422
```

**Why it matters:** Extreme values (e.g., 100% uncertainty = every word is an uncertainty word) are likely noise from very short turns (e.g., 1-2 words). While the IHS transform compresses extremes, these outliers can still influence the within-call fixed effects estimation. The provenance incorrectly claims "pooled 1/99%" winsorization for linguistic percentages (Section G), but Turn_Uncertainty_pct is computed at Stage 3 from raw tokenize counts and no winsorization is applied.

**Fix:**
```python
# build_h10_tone_at_top_panel.py, after line 221 (Turn_Uncertainty_pct computation)
# Add per-year or pooled winsorization:
from f1d.shared.variables.winsorization import winsorize_pooled
qa_tokens = winsorize_pooled(qa_tokens, ["Turn_Uncertainty_pct"])
```

**Rerun impact:** Stage 3 + Stage 4.

---

### Finding #6 — MINOR: Winsorization Inconsistency Between CEO and CFO Uncertainty

**Severity:** MINOR

**Symptom:** CEO_QA_Uncertainty_pct is per-year 1/99% winsorized (max varies by year: 1.89–2.51); CFO_QA_Uncertainty_pct is pooled 1/99% winsorized (max = 3.378 for all years).

**Evidence:**
- `ceo_qa_uncertainty.py:30`: uses `get_engine()` → LinguisticEngine → per-year winsorization
- `cfo_qa_uncertainty.py:97`: calls `self._finalize_data(combined)` → `winsorize_pooled()`
- Per-year max for CEO varies: 1.89 (2018) to 2.51 (2002)
- Pooled max for CFO: 3.378 constant across all years
- Provenance H10.md §G claims "Pooled 1%/99%" for all linguistic percentages — this is incorrect for CEO variables that go through the LinguisticEngine

**Why it matters:** Different winsorization methods between the M1 DV (IHS of CFO, pooled winsorized) and the ClarityStyle_Realtime input variable (built from CEO_QA_Uncertainty_pct, per-year winsorized) creates a subtle inconsistency. For M2, the Turn_Uncertainty_pct is not winsorized at all (Finding #5). The provenance documentation is misleading.

**Fix:** Update H10.md §G to accurately reflect:
- CEO_QA_Uncertainty_pct: per-year 1/99% (LinguisticEngine)
- CFO_QA_Uncertainty_pct: pooled 1/99% (CFOQAUncertaintyBuilder)
- Turn_Uncertainty_pct: unwinsorized

**Rerun impact:** Documentation only (no code/data change unless policy is unified).

---

### Finding #7 — MINOR: 2002 Missing from M1 Regression Sample

**Severity:** MINOR

**Symptom:** The M1 regression sample has 64 unique year-quarters, not 68. All four 2002 quarters are absent.

**Evidence:**
```
Missing quarters from regression sample: ['2002Q1', '2002Q2', '2002Q3', '2002Q4']
PanelOLS reported 64 time FE
```

**Why it matters:** ClarityStyle_Realtime requires ≥4 prior CEO calls (min_calls=4, window=4). Since the dataset starts in 2002, CEOs don't accumulate 4 calls until late 2002/early 2003. Combined with the ClarityStyle_Realtime NaN rate (44.5%), all 2002 observations are eliminated via listwise deletion. This is expected behavior but creates a slight misalignment between the panel's stated coverage (2002–2018) and the effective estimation window (2003–2018).

**Fix:** Document in provenance that M1 effective estimation period is 2003Q1–2018Q4 (64 quarters).

**Rerun impact:** None (documentation only).

---

### Finding #8 — NOTE: CEO_Unc_Lag1 Has 57.9% Zeros

**Severity:** NOTE

**Symptom:** CEO_Unc_Lag1 (used in robustness spec M2_lag1) is 57.9% zeros, 7.6% NaN, 34.6% non-zero.

**Evidence:**
```
CEO_Unc_Lag1 distribution:
  NaN: 128,658 (7.6%)
  Zero: 982,167 (57.9%)
  Non-zero: 586,807 (34.6%)
```

**Why it matters:** The high zero rate comes from ffill propagation. When the most recent CEO turn before a manager turn has CEO_Unc_Lag1 = NaN (first CEO turn in the call), ffill propagates 0.0 from a previous CEO turn's lag value. After IHS transform, IHS(0) = 0, creating a large mass point at zero. This may explain the lower coefficient for M2_lag1 (β=0.0167) versus M2_baseline (β=0.0426).

**Fix:** Consider using NaN instead of ffill-propagated zeros for CEO_Unc_Lag1 when the CEO has no prior turn. This would reduce the M2_lag1 sample but produce a cleaner IV.

**Rerun impact:** Stage 3 + Stage 4 if fix applied.

---

## 5) Rerun Plan

### Minimal Rerun Commands

```bash
# Step 0: Apply fix to run_h10_tone_at_top.py (Finding #1 + #3)
# (manual edit required — see fix in Finding #1 and #3)

# Step 1: Stage 3 is NOT needed (panel is correct)
# The sample column is already in the panel

# Step 2: Rerun Stage 4
cd F1D
python -m f1d.econometric.run_h10_tone_at_top
```

### Acceptance Tests

After rerun, verify:

1. **Main M1 N should decrease:**
   ```python
   # Expected: ~35,399 (Main-only after listwise deletion)
   diag = pd.read_csv('outputs/econometric/tone_at_top/<new_timestamp>/model_diagnostics.csv')
   main_m1 = diag[diag['model'].str.contains('Main_M1')]
   assert 34000 < main_m1['n_obs'].values[0] < 37000, f"Main M1 N = {main_m1['n_obs'].values[0]}"
   ```

2. **Main M2 N should decrease:**
   ```python
   main_m2 = diag[diag['model'].str.contains('Main_M2')]
   assert 1200000 < main_m2['n_obs'].values[0] < 1400000, f"Main M2 N = {main_m2['n_obs'].values[0]}"
   ```

3. **Finance and Utility N should be unchanged:**
   ```python
   fin_m1 = diag[diag['model'].str.contains('Finance_M1')]
   assert fin_m1['n_obs'].values[0] == 6793
   util_m2 = diag[diag['model'].str.contains('Utility_M2')]
   assert util_m2['n_obs'].values[0] == 62453
   ```

4. **LaTeX clustering note should be model-specific:**
   ```bash
   grep "Firm.*Call" outputs/econometric/tone_at_top/<new_timestamp>/tone_at_top_full.tex
   # Should find M2 clustering note
   ```

5. **Coefficient signs should be preserved:**
   - M1 Main ClarityStyle_Realtime: positive (expected β > 0)
   - M2 Main IHS_CEO_Prior_QA_Unc: positive (expected β > 0)

---

## 6) Hardening Recommendations

### Repo-Level

1. **Add sample filter assertion to all econometric runners:**
   ```python
   # After sample filtering, verify no cross-contamination
   if sample != "Main":
       assert (df_sample["sample"] == sample).all(), f"Sample leak: non-{sample} rows found"
   else:
       assert not df_sample["sample"].isin(["Finance", "Utility"]).any(), "Main includes Finance/Utility"
   ```

2. **Add entity-time uniqueness check before PanelOLS:**
   ```python
   reg_df = reg_df.set_index(["gvkey", "yq_id"])
   if not reg_df.index.is_unique:
       n_dups = reg_df.index.duplicated().sum()
       warnings.warn(f"Non-unique entity-time index: {n_dups} duplicates")
       reg_df = reg_df[~reg_df.index.duplicated(keep='last')]
   ```

3. **Standardize winsorization documentation:** Create a single table in the README or a dedicated `WINSORIZATION.md` that maps each variable to its exact winsorization method (per-year vs pooled, thresholds).

### Suite-Level (H10)

4. **Add Turn_Uncertainty_pct winsorization** at Stage 3 before IHS transform (or document the intentional lack of winsorization with justification).

5. **Add placebo difference test:** Compute `β_baseline - β_placebo` with bootstrap CI to quantify how much of the "transmission" effect is attributable to within-call correlation vs. directional CEO→manager influence.

6. **Log CEO_Unc_Lag1 zero/NaN rates** in the reconciliation table to track the ffill propagation issue.

7. **Add entity-time dedup step** for M1 before `set_index()`:
   ```python
   reg_df = reg_df.sort_values("start_date").drop_duplicates(
       subset=["gvkey", "yq_id"], keep="last"
   )
   ```

8. **Add integration test** for sample filtering:
   ```python
   def test_main_sample_excludes_finance_utility():
       # After sample filtering in Stage 4
       assert not main_sub["sample"].isin(["Finance", "Utility"]).any()
   ```

---

## 7) Command Log

| # | Command | Purpose | Result |
|---|---------|---------|--------|
| 1 | `read README.md` | Extract pipeline contract, stage boundaries, invariants | 932-line README with 4-stage architecture, zero-row-delta, engine-level winsorization |
| 2 | `read docs/Prompts/P_Audit.txt` | Load audit protocol | 246-line adversarial audit prompt |
| 3 | `read docs/provenance/` | List provenance files | Found H10.md, no AUDIT_H10.md |
| 4 | `glob **/*h10*` | Find all H10 source files | Panel builder + econometric runner |
| 5 | `glob **/*tone*` | Find tone-related files | 4 files (2 active, 2 archived) |
| 6 | `read docs/provenance/H10.md` | Extract claim register | 504-line provenance with full spec register |
| 7 | `read build_h10_tone_at_top_panel.py` | Audit Stage 3 code | 599 lines, call + turns panel builder |
| 8 | `read run_h10_tone_at_top.py` | Audit Stage 4 code | 1,281 lines, PanelOLS + AbsorbingLS |
| 9 | `ls outputs/variables/tone_at_top` | Identify output directories | 24 runs; latest = 2026-02-27_225254 |
| 10 | `ls outputs/econometric/tone_at_top` | Identify econometric output directories | 30 runs; latest = 2026-02-27_225837 |
| 11 | `ls outputs/variables/tone_at_top/2026-02-27_225254` | Check Stage 3 artifacts | 4 files: panel, turns_panel, stats, reconciliation |
| 12 | `ls outputs/econometric/tone_at_top/2026-02-27_225837` | Check Stage 4 artifacts | 46 files: coefficients, tables, diagnostics, report |
| 13 | `read ceo_style_realtime.py` | Audit ClarityStyle_Realtime construction | 149 lines; 4-call rolling, EB shrinkage, shift() for strictly prior |
| 14 | `read cfo_qa_uncertainty.py` | Audit CFO uncertainty builder | 112 lines; pooled winsorization via _finalize_data |
| 15 | `python -c` call panel structure | Verify 112,968 rows, unique file_names, 2,429 gvkeys, 4,466 ceo_ids | PASS |
| 16 | `python -c` missingness check | Verify ClarityStyle 44.5%, CFO 12.9%, SurpDec 25.5% | PASS |
| 17 | `python -c` turns panel structure | Verify 1,697,632 rows, 0 duplicates on primary key | PASS |
| 18 | `python -c` M1 sample filter check | Compare full vs Main-only listwise deletion N | FOUND: Full=43,570 vs Main-only=35,399 |
| 19 | `python -c` M2 sample filter check | Confirm Main M2 uses all turns | FOUND: All 1,697,632 = reported N |
| 20 | `grep "call_sub\|sample.*Main"` in econometric/ | Check other suites' Main filtering | H4,H5,H6 correctly filter `df_prep[df_prep["sample"]=="Main"]` |
| 21 | `python -c` Main sample composition | Breakdown of M1 43,570 by sample | Main: 35,399 + Finance: 6,793 + Utility: 1,378 = 43,570 |
| 22 | `python -c` look-ahead bias ClarityStyle | Spot-check CEO with first NaN then non-NaN calls | First 5 calls NaN, 6th non-NaN — PASS (min_calls=4, but needs 5 calls to get 4 prior) |
| 23 | `python -c` look-ahead bias M2 | Print call turns with CEO_Prior_QA_Unc | Prior values monotonically update — PASS |
| 24 | `python -c` winsorization check CFO | Verify pooled max = 3.378 across all years | PASS: constant max |
| 25 | `python -c` CEO winsorization type | Check per-year max variation | FOUND: varies 1.89–2.51 → per-year, not pooled |
| 26 | `read ceo_qa_uncertainty.py` | Verify CEO uses LinguisticEngine | Confirmed: `get_engine()` → per-year winsorization |
| 27 | `read model_diagnostics.csv` | Cross-check N, R² | Matches results_*.csv and report.md |
| 28 | `read results_main.csv` | Verify Main M1/M2 coefficients | M1: 0.0169/4.65, M2: 0.0426/19.37 |
| 29 | `read results_finance.csv` | Verify Finance results | M1: 0.001/0.12, M2: 0.0312/6.27 |
| 30 | `read results_utility.csv` | Verify Utility results | M1: -0.0156/-1.31, M2: 0.0247/3.50 |
| 31 | `read tone_at_top_full.tex` | Audit LaTeX table | FOUND: wrong clustering note |
| 32 | `read report.md` | Cross-check report with CSVs | All values match |
| 33 | `python -c` cross-artifact consistency | Compare coefficients, results, diagnostics | PASS: all match |
| 34 | `python -c` M2 N verification | Check valid obs after listwise deletion | PASS: Main=1,697,632, Finance=325,224, Utility=62,453 |
| 35 | `python -c` entity-time uniqueness | Check PanelOLS index duplicates | FOUND: 347 duplicate firm-quarters (694 rows) |
| 36 | `python -c` N Quarters check | Verify time periods | FOUND: 64, missing all 2002 quarters |
| 37 | `python -c` CEO_Unc_Lag1 zeros | Check zero/NaN distribution | 57.9% zeros, 7.6% NaN |
| 38 | `python -c` Turn_Uncertainty_pct range | Check extremes | max=100, 478 values >50% |
| 39 | `python -c` reproducibility | Compare prior and latest reconciliation tables | PASS: all 6 stages match |
| 40 | `python -c` output dir resolution | Test get_latest_output_dir | PASS: resolves to 2026-02-27_225254 |
| 41 | `read coefficients_Main_M2_placebo_lead.csv` | Verify placebo coefficient | β=0.0373, t=31.49 |
| 42 | `read coefficients_Main_M2_baseline.csv` | Verify baseline coefficient | β=0.0426, t=19.37 |
| 43 | `python -c` M2 baseline vs H_TT2 match | Verify identical results | PASS: intercepts match exactly |

---

## 8) Open Gaps

| # | Gap | What Would Close It |
|---|-----|---------------------|
| 1 | **CFO role regex miss rate** — 12.9% of calls have no CFO-matched speaker. Unknown whether these are genuine absences or regex misses. | Manual inspection of 100 random unmatched calls' raw speaker_name + role fields in Stage 2.1 tokenize output. |
| 2 | **Deduplication divergent values** — 6,820 duplicate (file_name, speaker_number) pairs deduplicated with stable sort. Some groups have divergent uncertainty values. Source of duplicates unknown. | Trace duplicates to Stage 2.1 tokenize_and_count to identify whether they originate from overlapping transcript segments, speaker re-identification, or file-level issues. |
| 3 | **Wild cluster bootstrap vs AbsorbingLS discrepancy** — Bootstrap uses simple OLS (no FE) while the main M2 uses AbsorbingLS with Call + Speaker FE. Bootstrap p-values may not be comparable to the main regression. | Implement bootstrap within the AbsorbingLS framework (computationally expensive but correct), or document the discrepancy explicitly. |
| 4 | **linearmodels behavior with duplicate entity-time index** — Exact behavior of PanelOLS with non-unique MultiIndex not verified empirically for this pandas/linearmodels version combination. | Run a controlled test with synthetic data: create duplicate entity-time rows and compare PanelOLS results with and without deduplication. |
| 5 | **Prior run coefficient stability** — Only reconciliation table counts compared across runs, not coefficient values. Unknown if coefficient drift exists between runs. | Compare `coefficients_*.csv` files from 2026-02-22 and 2026-02-27 runs for each model. |

---

*End of Audit Report*
