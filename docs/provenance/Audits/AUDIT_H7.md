# AUDIT: H7 Speech Vagueness and Stock Illiquidity

**Audit Date:** 2026-02-28
**Auditor:** Implementation Audit (Hardnosed, Manual)
**Suite ID:** H7
**Latest Panel Run:** 2026-02-27_224426
**Latest Regression Run:** 2026-02-27_224719

---

## 0) Suite Identification

| Field | Value |
|-------|-------|
| **Suite ID** | H7 |
| **Stage 3 Builder** | `src/f1d/variables/build_h7_illiquidity_panel.py` |
| **Stage 4 Runner** | `src/f1d/econometric/run_h7_illiquidity.py` |
| **Model Family** | Panel OLS with Entity (Firm) + Time (Year) Fixed Effects |
| **Estimator** | `linearmodels.PanelOLS` with `drop_absorbed=True` |
| **Variance Estimator** | Clustered by entity (firm), one-way |

---

## 1) Suite Contract (What the suite claims it does)

Extracted from `docs/provenance/H7.md`:

- **Estimation unit:** Individual earnings call (`file_name` is the unique observation ID)
- **Primary keys:** `file_name` (unique call), `gvkey` (firm), `year` (time FE)
- **DV:** `amihud_illiq_lead` — forward Amihud (2002) illiquidity ratio at t+1 fiscal year, scaled ×10^6
- **Primary IVs:** `Manager_QA_Uncertainty_pct`, `Manager_QA_Weak_Modal_pct`, `Manager_Pres_Uncertainty_pct`
- **Secondary IVs:** `CEO_QA_Uncertainty_pct`, `CEO_QA_Weak_Modal_pct`, `CEO_Pres_Uncertainty_pct`
- **Interactions:** None
- **Controls:** Size, Lev, ROA, TobinsQ, Volatility, StockRet (BASE_CONTROLS)
- **Fixed effects:** Firm (`gvkey`) + Year (`year` from `start_date`)
- **Variance estimator:** Entity-clustered (one-way, firm)
- **Transforms:** Natural log for Size; ×100 for linguistic pct and StockRet; ×10^6 for Amihud
- **Winsorization:** Per-year 1%/99% at engine level for all continuous variables; linguistic variables winsorized 0%/99% (upper only)
- **Missingness:** Listwise deletion at regression time; NaN preserved in panel
- **Sample splits:** Main (FF12 ∉ {8,11}), Finance (FF12=11), Utility (FF12=8)
- **Min calls filter:** ≥5 calls per firm within sample (applied pre-listwise deletion)
- **Hypothesis direction:** H7-A/B: β(Manager_Uncertainty) > 0; H7-C: β(QA) > β(Pres)
- **P-values:** One-tailed for β₁ (Manager IV); two-tailed for β₂ (CEO IV)
- **9 total regressions:** 3 specs × 3 samples

---

## 2) Evidence Map (Claim → Evidence → Status)

| # | Claim | Where Claimed | Where Verified | Status | Notes |
|---|-------|---------------|----------------|--------|-------|
| 1 | Panel has 112,968 rows | H7.md:128 | `panel.parquet` verified: 112,968 rows | **PASS** | Ad-hoc `python -c` confirmed |
| 2 | `file_name` is unique | H7.md:149 | `panel['file_name'].is_unique == True` | **PASS** | Verified ad-hoc |
| 3 | Zero row-delta on all merges | H7.md:128-131, builder:191-196 | `build_h7_illiquidity_panel.py:195-196` raises `ValueError` on delta≠0 | **PASS** | Code enforces invariant |
| 4 | Sample split: Main=88,205 / Finance=20,482 / Utility=4,281 | H7.md:253-256 | Verified ad-hoc: exact match | **PASS** | |
| 5 | DV coverage: 100,036 (88.6%) | H7.md:221, H7.md:258 | Verified: `amihud_illiq_lead.notna().sum() == 100,036` | **PASS** | |
| 6 | Main QA_Uncertainty regression: N=54,170, n_firms=1,674 | H7.md:530 | Verified by replicating listwise deletion: exact match | **PASS** | |
| 7 | Main Pres_Uncertainty regression: N=54,022, n_firms=1,664 | H7.md:532 | Verified by replicating listwise deletion: exact match | **PASS** | |
| 8 | β₁ for Main/QA_Unc = -0.0037, SE=0.0035 | model_diagnostics.csv:2 | Cross-checked vs regression_Main_QA_Uncertainty.txt:24 | **PASS** | Exact match to 4 decimal places |
| 9 | LaTeX table coefficients match CSV | h7_illiquidity_table.tex:9-12 | Cross-checked all 3 specs vs model_diagnostics.csv | **PASS** | |
| 10 | LaTeX table N values match CSV | h7_illiquidity_table.tex:18 | 54,170 / 54,170 / 54,022 — exact match | **PASS** | |
| 11 | One-tailed p-value formula correct | runner:219 | Recomputed all 9 models: exact match | **PASS** | `p_one = p_two/2 if β>0 else 1-p_two/2` |
| 12 | h7_sig flag correct | runner:220 | Recomputed: all 9 = False, all match | **PASS** | |
| 13 | Summary stats CSV matches TEX | summary_stats.csv vs summary_stats.tex | Verified Main DV row: N=78,286, Mean=0.0183 exact match | **PASS** | |
| 14 | Summary stats N matches panel | summary_stats.csv | Verified: Main DV N=78,286 == `panel[panel['sample']=='Main']['amihud_illiq_lead'].notna().sum()` | **PASS** | |
| 15 | Entity-clustered SEs | runner:198 | regression txt: "Cov. Estimator: Clustered" | **PASS** | |
| 16 | Firm + Year FE | runner:182-186 | regression txt: "Included effects: Entity, Time" | **PASS** | |
| 17 | Per-year winsorization at engine level | _crsp_engine.py:409-441 | Code calls `winsorize_by_year(result_with_year, CRSP_RETURN_COLS)` | **PASS** | |
| 18 | Linguistic variables winsorized 0%/99% (upper only) | _linguistic_engine.py:255-258 | Code: `lower=0.0, upper=0.99` | **PASS** | |
| 19 | Compustat variables winsorized per-year 1%/99% | _compustat_engine.py:1049-1057 | Code: `_winsorize_by_year(comp[col], year_col)` | **PASS** | |
| 20 | Lead variable: consecutive-year validation | builder:105-106 | Code: `is_consecutive = (next_fyearq - fyearq_int) == 1` | **PASS** | Non-consecutive → NaN |
| 21 | Lead variable: all calls in same (gvkey,fyearq) share same lead | builder:115-121 | Verified: `groupby(['gvkey','fyearq_int'])['amihud_illiq_lead'].nunique().max() == 1` | **PASS** | |
| 22 | amihud_illiq_lead is NOT re-winsorized | H7.md:337, builder code | No winsorization applied after lead construction | **PASS** | See Finding MAJOR-1 |
| 23 | Amihud denominator zero-protection | _crsp_engine.py:216-219 | `dollar_vol_masked = merged["dollar_volume"].replace(0, np.nan)` | **PASS** | |
| 24 | MIN_TRADING_DAYS = 10 guard | _crsp_engine.py:37, 247-248 | `.where(sufficient)` zeroes out under-sampled windows | **PASS** | |
| 25 | Date-bounded CCM PERMNO lookup | _crsp_engine.py:98-155 | `linkdt <= start_date <= linkenddt` enforced | **PASS** | CRITICAL-3 fix applied |
| 26 | Deterministic: no random seed usage | H7.md:89-90 | No random operations in builder or runner | **PASS** | |

---

## 3) End-to-End Implementation Audit

### A) Stage 1/2 Preconditions

**Manifest anchoring:** The builder loads the manifest via `ManifestFieldsBuilder`, which resolves to `outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet`. Join key is `file_name`. Verified: `file_name` is unique in the manifest (112,968 rows).

**Stage 2 dependency:** Linguistic variables are loaded via `LinguisticEngine.get_data()` which reads from `outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_{year}.parquet`. Join key is `file_name`.

**Hidden dependencies:** None beyond the manifest and Stage 2 outputs. H7 does NOT depend on `clarity_scores.parquet` (which is an H0.2 output). CRSP and Compustat are loaded from `inputs/` directly.

**Status:** PASS — no hidden dependency issues.

### B) Stage 3 Panel Builder Audit

**File:** `src/f1d/variables/build_h7_illiquidity_panel.py` (283 lines)

#### B1) Primary Key Uniqueness

- `file_name` uniqueness verified at 112,968 rows (ad-hoc confirmed: `panel['file_name'].is_unique == True`)
- `attach_fyearq()` in `panel_utils.py:119-128` explicitly asserts `file_name` uniqueness before `set_index`, raising `ValueError` on duplicates
- **Status:** PASS

#### B2) Merge Sequence and Zero Row-Delta

Builder performs 13 left merges on `file_name` (one per variable builder), all with zero row-delta enforcement at `build_h7_illiquidity_panel.py:191-196`:
```python
delta = after_len - before_len
if delta != 0:
    raise ValueError(f"Merge '{name}' changed rows {before_len} -> {after_len}")
```
- **Status:** PASS — invariant is hard-coded and raises on violation.

#### B3) Many-to-Many Join Risk

All merges are left joins on `file_name`, which is unique on both sides (manifest and each builder output). Many-to-many risk is **eliminated** by design.

- **Status:** PASS

#### B4) Timing Alignment and Look-Ahead Bias

**Compustat merge (`merge_asof` backward):**
- `panel_utils.py:152-159`: `merge_asof` on `_start_date_dt` (left) vs `datadate` (right), by `gvkey`, direction=`backward`
- This finds the most recent Compustat reporting date **before or on** the call date — no look-ahead bias
- **Status:** PASS

**CRSP window:**
- `_crsp_engine.py:351-356`: `window_start = prev_call_date + 5 days`, `window_end = start_date - 5 days`
- This uses returns from **before** the current call, excluding 5 days around both calls — clean identification window
- **Status:** PASS

**Lead variable (`amihud_illiq_lead`):**
- `build_h7_illiquidity_panel.py:67-129`: Takes last call's `amihud_illiq` per (gvkey, fyearq), shifts forward 1 fiscal year
- Consecutive-year validation at line 105-106: non-consecutive years → NaN
- Verified by tracing firm 005047: FY2003's amihud is correctly assigned as FY2002's lead
- **Status:** PASS — no look-ahead bias in lead construction

**Fiscal vs calendar alignment:**
- `fyearq` is attached via `merge_asof` from Compustat (fiscal year), not calendar year
- `year` (for time FE) is derived from `start_date.dt.year` (calendar year)
- The lead is computed on `fyearq` (fiscal year), which is correct for the forward-looking DV
- **Status:** PASS

#### B5) Outlier Handling

| Layer | Variables | Method | Code Location |
|-------|-----------|--------|---------------|
| CompustatEngine | Size, Lev, ROA, TobinsQ | Per-year 1%/99% via `_winsorize_by_year` | `_compustat_engine.py:1049-1057` |
| CRSPEngine | StockRet, Volatility, amihud_illiq | Per-year 1%/99% via `winsorize_by_year` | `_crsp_engine.py:435-437` |
| LinguisticEngine | All _pct columns | Per-year 0%/99% (upper only) | `_linguistic_engine.py:255-258` |
| Panel Builder | amihud_illiq_lead | **NOT winsorized** | N/A — see Finding MAJOR-1 |

**Status:** See Finding MAJOR-1 (DV not re-winsorized after lead shift)

#### B6) Missingness

- Missing values are **preserved** in the panel (NaN carried through all merges)
- Listwise deletion happens only at regression time (`run_h7_illiquidity.py:173`)
- No silent drops during merges (left joins preserve all rows)
- Coverage verified ad-hoc:
  - `amihud_illiq_lead`: 88.6% (100,036/112,968)
  - `CEO_QA_Uncertainty_pct`: 68.0% (76,818/112,968) — lowest coverage variable
  - `Size`: 99.8%, `Volatility`: 93.3%
- **Status:** PASS — missingness policy correctly implemented

#### B7) Variable Semantics

| Variable | Provenance Definition | Implementation | Match? |
|----------|----------------------|----------------|--------|
| `amihud_illiq_lead` | `mean(\|RET\| / dollar_vol) × 10^6`, shifted +1 FY | `_crsp_engine.py:217,252`: `merged["RET"].abs() / dollar_vol_masked` then `mean_illiq * 1e6` | **PASS** |
| `Manager_QA_Uncertainty_pct` | `(Uncertainty_tokens / total_tokens) × 100` | Via LinguisticEngine from Stage 2 outputs | **PASS** |
| `Size` | `ln(atq)` for atq > 0 | `_compustat_engine.py:940`: `np.where(comp['atq'] > 0, np.log(comp['atq']), np.nan)` | **PASS** |
| `Lev` | `(dlcq + dlttq) / atq` | `_compustat_engine.py:945`: `(comp['dlcq'].fillna(0) + comp['dlttq'].fillna(0)) / comp['atq']` | **PASS** |
| `ROA` | `iby / avg_assets` (annualized) | `_compustat_engine.py:954-956`: Uses Q4 annual values, average assets | **PASS** |
| `TobinsQ` | `(atq + cshoq×prccq - ceqq) / atq` | `_compustat_engine.py:969-973`: `(mktcap + debt_book) / comp['atq']` — uses `(cshoq*prccq + debt)` not `(atq + cshoq*prccq - ceqq)` | **MINOR DIFF** — see Note 1 |
| `Volatility` | `std(daily_RET) × √252 × 100` | `_crsp_engine.py:251`: `std_ret * np.sqrt(252) * 100` | **PASS** |
| `StockRet` | `(exp(sum(log1p(RET))) - 1) × 100` | `_crsp_engine.py:249`: `(np.expm1(sum_log_ret)) * 100` | **PASS** |

**Note 1:** TobinsQ in CompustatEngine uses `(market_cap + book_debt) / atq` which is `(cshoq*prccq + dlcq + dlttq) / atq`. The provenance says `(atq + cshoq*prccq - ceqq) / atq`. These are algebraically equivalent when `ceqq = atq - (dlcq + dlttq)` (book equity = assets minus debt), which holds by accounting identity. Not a bug.

### C) Shared Engines / Variable Builders Audit

#### C1) CompustatEngine (`_compustat_engine.py`)

- **Dedup:** `drop_duplicates(subset=['gvkey','datadate'], keep='last')` at line 1107 — deterministic (most recent restatement)
- **Winsorization:** Per-year 1%/99% via `_winsorize_by_year(series, year_col)` at lines 1049-1057, using `fyearq` as year grouping
- **Date matching:** `merge_asof` backward on `(gvkey, datadate ≤ start_date)` at line 1143-1150
- **Footguns:** `dlcq.fillna(0)` and `dlttq.fillna(0)` in Lev formula (line 945) — treats missing debt as zero. Standard practice but worth noting.
- **Status:** PASS

#### C2) CRSPEngine (`_crsp_engine.py`)

- **Dedup:** CRSP daily file inherently has one row per (PERMNO, date). No explicit dedup needed; `PERMNO` coerced and NaN dropped at lines 91-93.
- **Winsorization:** Per-year 1%/99% via `winsorize_by_year()` at lines 435-437, using `year` from manifest
- **Date matching:** Date-bounded CCM link (`linkdt ≤ start_date ≤ linkenddt`) at lines 141-143. Multiple valid links resolved by taking most recent `linkdt` (line 147-153).
- **Window:** `[prev_call + 5d, call - 5d]` — clean inter-call window, no event-day contamination
- **prev_call_date:** Computed on FULL manifest (MAJOR-2 fix) at lines 314-318 — first call of each year correctly uses prior-year call
- **Amihud zero-protection:** `dollar_volume.replace(0, np.nan)` at line 216; inf replaced at line 219
- **MIN_TRADING_DAYS=10:** Applied via `.where(sufficient)` at lines 247-252
- **Status:** PASS

#### C3) LinguisticEngine (`_linguistic_engine.py`)

- **Loading:** Year-partitioned parquet files from Stage 2 outputs
- **Winsorization:** Per-year upper-only (0%/99%) via `winsorize_by_year(combined, cols, lower=0.0, upper=0.99, min_obs=1)` at lines 255-258
- **`min_obs=1`:** This means even years with a single observation get "winsorized" — effectively a no-op for small groups since `quantile(0.99)` on 1 observation returns the value itself. Not harmful but unconventional.
- **Status:** PASS (minor: `min_obs=1` is lenient but harmless)

### D) Stage 4 Runner / Estimation Audit

**File:** `src/f1d/econometric/run_h7_illiquidity.py` (520 lines)

#### D1) Model Specification Match

**RHS terms (from code lines 182-186):**
```
amihud_illiq_lead ~ _iv1 + _iv2 + Size + Lev + ROA + TobinsQ + Volatility + StockRet + EntityEffects + TimeEffects
```
Where `_iv1` = Manager uncertainty measure, `_iv2` = CEO uncertainty measure.

**Provenance spec (H7.md Section H):**
```
amihud_illiq_lead ~ Manager_*_pct + CEO_*_pct + Size + Lev + ROA + TobinsQ + Volatility + StockRet + FirmFE + YearFE
```

**Match:** PASS — exact correspondence.

**Note:** The provenance doc (Section A4) mentions `Manager_QA_Uncertainty_pct` as "primary IVs" and `CEO_QA_Uncertainty_pct` as "secondary IVs." The code correctly includes BOTH in each regression (`_iv1` + `_iv2`), with the Manager variable as the hypothesis-testing coefficient (β₁).

#### D2) Fixed Effects and Sample Splits

- **FE:** `EntityEffects + TimeEffects` in formula (line 186); index is `[gvkey, year]` (line 194)
- **Sample splits:** `CONFIG['samples'] = ['Main', 'Finance', 'Utility']` (line 81); filter at line 446
- **Min calls:** `CONFIG['min_calls'] = 5` (line 80); filter at lines 449-450

**Verified from regression txt:**
- Main QA: "Included effects: Entity, Time", Entities=1,674, Time periods=17
- Utility QA: Entities=78, Time periods=17
- **Status:** PASS

#### D3) Variance Estimator

- Code: `model_obj.fit(cov_type='clustered', cluster_entity=True)` at line 198
- Regression txt: "Cov. Estimator: Clustered"
- One-way entity clustering (firm) — matches provenance spec
- **Status:** PASS

#### D4) One-Tailed P-Values

- Code at line 219: `p1_one = p1_two / 2 if beta1 > 0 else 1 - p1_two / 2`
- This is the correct sign-conditional one-tailed transformation:
  - If β₁ > 0 (correct direction for H7): p_one = p_two / 2
  - If β₁ < 0 (wrong direction): p_one = 1 - p_two / 2 (penalizes wrong sign)
- **Verified:** All 9 models recomputed, all match to 10 decimal places
- **Status:** PASS

#### D5) H7-C Spontaneity Gap Test

- Code at lines 474-500: Compares β(QA_Uncertainty) vs β(Pres_Uncertainty) for Main sample
- Test logic: `gap_sig = beta_qa > beta_pres and qa_main['h7_sig']`
- This requires BOTH conditions: QA > Pres magnitude AND QA is individually significant
- **Status:** PASS — logic is correct and conservative

#### D6) LaTeX Table

- **Manager IV stars use one-tailed p** (`beta1_p_one`) at line 296: CORRECT for directional hypothesis
- **CEO IV stars use two-tailed p** (`beta2_p_two`) at line 308: See Finding MINOR-1
- **N and R² values:** Cross-verified against model_diagnostics.csv — exact match
- **Status:** See Finding MINOR-1

#### D7) Output Files

All expected output files present:
- 9 regression txt files (3 specs × 3 samples): PRESENT
- `model_diagnostics.csv`: PRESENT, 9 rows (correct)
- `h7_illiquidity_table.tex`: PRESENT
- `summary_stats.csv`: PRESENT (3 panels × 13 variables)
- `summary_stats.tex`: PRESENT, matches CSV

### E) Artifact Integrity & Cross-Consistency

#### E1) model_diagnostics.csv vs regression txt

| Check | Main/QA_Unc | Utility/QA_Unc | Status |
|-------|-------------|----------------|--------|
| β₁ | csv=-0.0037, txt=-0.0037 | csv=-0.0000, txt=-4.978e-05 | **PASS** |
| SE₁ | csv=0.0035, txt=0.0035 | csv=0.0001, txt=6.429e-05 | **PASS** |
| T-stat | csv=-1.0431, txt=-1.0431 | csv=-0.7743, txt=-0.7743 | **PASS** |
| P-value | csv=0.2969, txt=0.2969 | csv=0.4388, txt=0.4388 | **PASS** |
| N obs | csv=54,170, txt=54,170 | csv=2,240, txt=2,240 | **PASS** |
| Within R² | csv=0.0077, txt=0.0077 | csv=0.1223, txt=0.1223 | **PASS** |

#### E2) LaTeX table vs model_diagnostics.csv

| Column | LaTeX | CSV | Status |
|--------|-------|-----|--------|
| Manager IV (1) | -0.0037 | -0.0037 | **PASS** |
| Manager SE (1) | (0.0035) | 0.0035 | **PASS** |
| Manager IV (2) | -0.0085 | -0.0085 | **PASS** |
| CEO IV (1) | -0.0007 | -0.0007 | **PASS** |
| N (1) | 54,170 | 54,170 | **PASS** |
| N (3) | 54,022 | 54,022 | **PASS** |
| R² (1) | 0.0077 | 0.0077 | **PASS** |

#### E3) summary_stats.csv vs summary_stats.tex

Verified Main sample DV row: N=78,286, Mean=0.0183, SD=0.1218 — exact match between CSV and TEX.

#### E4) Provenance row counts vs actual

| Checkpoint | Provenance Claim | Actual | Status |
|------------|-----------------|--------|--------|
| Panel rows | 112,968 | 112,968 | **PASS** |
| file_name unique | Yes | Yes | **PASS** |
| DV valid | 100,036 (88.6%) | 100,036 (88.6%) | **PASS** |
| Main sample | 88,205 | 88,205 | **PASS** |
| Finance sample | 20,482 | 20,482 | **PASS** |
| Utility sample | 4,281 | 4,281 | **PASS** |

**Status:** PASS — all artifacts are internally consistent.

---

## 4) Findings (Grouped by Severity)

### MAJOR-1: DV (`amihud_illiq_lead`) Not Re-Winsorized After Lead Shift — Extreme Right Skew

**Severity:** MAJOR

**Symptom:** The DV `amihud_illiq_lead` has extreme right skew (skewness=17.4, kurtosis=378.2) with Max/P99 ratio of 8.9×. The mean is 18.4× the median. This is driven by the lead construction: `amihud_illiq` is per-year winsorized at the engine level, but when shifted forward 1 fiscal year to create `amihud_illiq_lead`, the shifted values are NOT re-winsorized. Values from a high-volatility year (e.g., 2008 crisis, P99=2.44) can land in a low-volatility year's row (e.g., 2007, P99=0.20), creating extreme outliers in the DV.

**Evidence:**
- `build_h7_illiquidity_panel.py:67-129`: `create_lead_variables()` does not apply any winsorization
- Ad-hoc check: In year 2007, 372 out of 6,616 lead values exceed 2007's own P99 of the contemporaneous `amihud_illiq` (because they are 2008 crisis values)
- DV statistics: mean=0.0154, median=0.0008, skew=17.4, kurtosis=378.2

**Why it matters:** OLS is sensitive to extreme outliers. With skewness of 17.4, a handful of extreme observations could dominate the regression estimates, inflating standard errors and potentially masking or creating spurious effects. This is a standard concern in Amihud illiquidity regressions, and most published papers address it with log or IHS transforms.

**How to verify:**
```python
dv = panel['amihud_illiq_lead'].dropna()
print(f"Skewness: {dv.skew():.2f}")  # Expected: ~17.4
print(f"Max/P99: {dv.max()/dv.quantile(0.99):.1f}")  # Expected: ~8.9
```

**Fix:** Apply one of:
1. Post-shift per-year winsorization of `amihud_illiq_lead` (simplest, preserves current approach)
2. Log or IHS transform of the DV (standard in liquidity literature: `ln(1 + Amihud×10^6)`)
3. Both: winsorize then transform

**Rerun impact:** Stage 3 rebuild + Stage 4 rerun required. Results may change.

---

### MINOR-1: LaTeX Table Uses Mixed P-Value Bases for Star Notation

**Severity:** MINOR

**Symptom:** In the LaTeX table (`h7_illiquidity_table.tex`), the Manager IV row uses **one-tailed** p-values (`beta1_p_one`) for star assignment, while the CEO IV row uses **two-tailed** p-values (`beta2_p_two`). This is inconsistent and potentially confusing to readers.

**Evidence:**
- `run_h7_illiquidity.py:296`: `fmt_coef(r['beta1'], r['beta1_p_one'])` — one-tailed for Manager
- `run_h7_illiquidity.py:308`: `fmt_coef(r['beta2'], r['beta2_p_two'])` — two-tailed for CEO

**Why it matters:** A reader seeing stars on the CEO IV coefficient would assume the same p-value basis as the Manager IV. In practice, since all coefficients are insignificant in H7, this has zero practical impact on this suite. But it could mislead in other suites if this pattern is copied.

**How to verify:** Read `run_h7_illiquidity.py:296` and `run_h7_illiquidity.py:308`.

**Fix:** Either:
1. Use two-tailed p-values for both (standard in tables), with a footnote noting the one-tailed test for the directional hypothesis
2. Use one-tailed for both Manager and CEO rows, since H7 has a directional prediction for both

**Rerun impact:** Stage 4 rerun only (LaTeX generation).

---

### MINOR-2: `min_calls` Filter Applied Pre-Listwise Deletion — Post-Deletion Singletons Exist

**Severity:** MINOR

**Symptom:** The `min_calls >= 5` filter is applied BEFORE listwise deletion (`run_h7_illiquidity.py:449-450`). After listwise deletion removes rows with missing required variables, some firms end up with fewer than 5 observations in the regression. In the Utility sample, 5 firms have <5 calls and 1 firm has exactly 1 call in the actual regression.

**Evidence:**
- `run_h7_illiquidity.py:449-450`: `call_counts = df_sample.groupby('gvkey')['file_name'].transform('count')`; filter applied on `df_sample` (pre-dropna)
- Ad-hoc verification: Utility sample has 1 firm with 1 obs, 5 firms with <5 obs in the regression sample
- Regression txt for Utility: `Min Obs: 1.0000`

**Why it matters:** Firms with 1-2 observations contribute little to within-entity variation but consume degrees of freedom. With `drop_absorbed=True`, singleton entities with only one time period may be absorbed. The impact is negligible for Main (34 singletons out of 1,674 firms) but non-trivial for Utility (1 singleton out of 78 firms ≈ 1.3%).

**How to verify:**
```python
# After listwise deletion:
calls_per_firm = df_reg.groupby('gvkey').size()
print(f"Singletons: {(calls_per_firm == 1).sum()}")
```

**Fix:** Apply `min_calls` filter AFTER listwise deletion, or add a post-deletion singleton check:
```python
# After dropna:
post_counts = df_reg.groupby('gvkey')['file_name'].transform('count')
df_reg = df_reg[post_counts >= CONFIG['min_calls']]
```

**Rerun impact:** Stage 4 rerun only. Marginal impact on results.

---

### MINOR-3: Dead Code Path — `Weak_Modal_Gap` in `prepare_regression_data()`

**Severity:** MINOR

**Symptom:** `prepare_regression_data()` computes `Weak_Modal_Gap = Manager_QA_Weak_Modal_pct - Manager_Pres_Weak_Modal_pct` (line 144), but `Manager_Pres_Weak_Modal_pct` is not in the panel (verified: column does not exist). The code falls through to `np.nan` via the `if ... in df.columns else np.nan` guard. The variable is never used anywhere.

**Evidence:**
- `run_h7_illiquidity.py:144-147`: `df['Weak_Modal_Gap'] = (df['Manager_QA_Weak_Modal_pct'] - df['Manager_Pres_Weak_Modal_pct']) if 'Manager_Pres_Weak_Modal_pct' in df.columns else np.nan`
- Ad-hoc: `'Manager_Pres_Weak_Modal_pct' in panel.columns` → `False`
- `Weak_Modal_Gap` is never referenced in SPECS or any regression formula

**Why it matters:** Dead code clutter. No functional impact.

**Fix:** Remove lines 143-147 from `prepare_regression_data()`.

**Rerun impact:** None.

---

### NOTE-1: Utility Sample Has Very Low Statistical Power (N=78 Firms)

**Severity:** NOTE

**Symptom:** The Utility sample has only 78 unique firms and 2,240-2,296 observations after filtering. The robust F-statistic p-value is 0.1044 (insignificant), suggesting the model has marginal overall explanatory power.

**Evidence:** `model_diagnostics.csv` rows 7-9: n_firms=78, within_r2=0.12-0.12
- Regression txt: "F-statistic (robust): 1.6555, P-value: 0.1044"

**Why it matters:** Results in the Utility sample should be interpreted with extreme caution. The failure to reject H7 in Utility could be due to low power rather than a true null effect.

**Fix:** Consider dropping the Utility sample from the primary analysis and relegating it to an appendix, or at minimum noting the power limitation.

**Rerun impact:** None (interpretive recommendation).

---

### NOTE-2: DV Transformation Should Be Considered (Standard in Amihud Literature)

**Severity:** NOTE

**Symptom:** The raw Amihud measure is used as the DV without log or IHS transformation. The measure has extreme right skew (17.4) and heavy tails (kurtosis 378). Even with IHS transform, skewness remains at 13.1, and with log(1+x), at 11.9. This is a known property of the Amihud measure.

**Evidence:** Ad-hoc distribution analysis: Mean/Median ratio = 18.4×, P99/P50 ratio = 373.5×

**Why it matters:** Many published papers using Amihud (2002) apply `log(1 + ILLIQ)` or rank transformations. While OLS with raw Amihud is not technically wrong, the extreme skew means the regression is effectively fitting a handful of high-illiquidity observations, which may not be representative.

**Fix:** Consider adding a robustness check with `log(1 + amihud_illiq_lead)` as the DV.

**Rerun impact:** Would require new regression specification (Stage 4 only).

---

### NOTE-3: `n_firms` in Diagnostics CSV May Differ from linearmodels Entity Count When Entities Are Absorbed

**Severity:** NOTE

**Symptom:** `model_diagnostics.csv` reports `n_firms = df_reg['gvkey'].nunique()` (computed pre-estimation at `run_h7_illiquidity.py:234`), while the regression txt reports `Entities` from linearmodels (which may differ if `drop_absorbed=True` absorbs entities). In the current run, these happen to match for all 9 models (verified for Main/QA_Unc: both report 1,674).

**Evidence:**
- `run_h7_illiquidity.py:234`: `"n_firms": df_reg['gvkey'].nunique()`
- Regression txt Main/QA: "Entities: 1674"
- Both match: 1,674

**Why it matters:** If entities are ever absorbed in a future run (e.g., data changes), the CSV `n_firms` would be higher than the actual number of entities in the regression, creating an inconsistency.

**Fix:** Compute `n_firms` from `model.entity_info` or similar post-estimation attribute instead of `df_reg['gvkey'].nunique()`.

**Rerun impact:** None currently (values already match).

---

## 5) Rerun Plan (Minimal, Deterministic)

### Commands to Regenerate

```bash
# Stage 3: Build H7 Illiquidity Panel
python -m f1d.variables.build_h7_illiquidity_panel

# Stage 4: Run H7 Illiquidity Hypothesis Test
python -m f1d.econometric.run_h7_illiquidity
```

### Acceptance Tests

#### Stage 3 Checkpoints

| Check | Expected | Command |
|-------|----------|---------|
| Panel row count | 112,968 | `python -c "import pandas as pd; p=pd.read_parquet('<panel_path>'); assert len(p)==112968"` |
| `file_name` uniqueness | True | `python -c "import pandas as pd; p=pd.read_parquet('<panel_path>'); assert p['file_name'].is_unique"` |
| Column count | 24 | `python -c "import pandas as pd; p=pd.read_parquet('<panel_path>'); assert len(p.columns)==24"` |
| Sample split | Main=88205, Finance=20482, Utility=4281 | `python -c "import pandas as pd; p=pd.read_parquet('<panel_path>'); v=p['sample'].value_counts(); assert v['Main']==88205 and v['Finance']==20482 and v['Utility']==4281"` |
| DV coverage | ~100,036 (88.6%) | `python -c "import pandas as pd; p=pd.read_parquet('<panel_path>'); n=p['amihud_illiq_lead'].notna().sum(); assert abs(n-100036)<100"` |

#### Stage 4 Checkpoints

| Check | Expected | Tolerance |
|-------|----------|-----------|
| Number of regression models | 9 | Exact |
| Main/QA_Unc N obs | 54,170 | Exact (deterministic) |
| Main/QA_Unc β₁ | -0.0037 | ±0.0001 |
| Main/QA_Unc within R² | 0.0077 | ±0.0005 |
| All h7_sig flags | False | Exact |
| 9 regression txt files | Present | Exact |
| model_diagnostics.csv rows | 9 | Exact |
| summary_stats.csv rows | 39 (3 samples × 13 vars) | Exact |

### Determinism Note

All operations are deterministic (no random sampling, no parallel non-determinism). Exact coefficient reproduction is expected across runs on the same data.

---

## 6) Refactor & Hardening Recommendations

### Assertions to Add

1. **Post-lead winsorization or transform (MAJOR-1 fix):**
   ```python
   # In create_lead_variables(), after constructing amihud_illiq_lead:
   # Option A: Re-winsorize
   from f1d.shared.variables.winsorization import winsorize_by_year
   panel = winsorize_by_year(panel, ['amihud_illiq_lead'], year_col='year')
   # Option B: Log-transform
   panel['amihud_illiq_lead'] = np.log1p(panel['amihud_illiq_lead'])
   ```

2. **Post-deletion min_calls check (MINOR-2 fix):**
   ```python
   # In run_regression(), after dropna:
   post_counts = df_reg.groupby('gvkey')['file_name'].transform('count')
   df_reg = df_reg[post_counts >= 5]
   ```

3. **Entity count from model output (NOTE-3 fix):**
   ```python
   # In run_regression(), after model.fit():
   meta['n_firms'] = int(model.entity_info.total)  # or model.nentity
   ```

### Logging / Provenance Improvements

1. Log the number of entities absorbed by `drop_absorbed=True` (currently silent)
2. Log the DV distribution statistics (skewness, kurtosis, mean/median ratio) as a diagnostic in the regression output
3. Add a post-listwise-deletion firm count to the regression printout

### Tests to Add

1. **Unit test:** Verify `create_lead_variables()` correctly shifts forward by 1 fiscal year on a synthetic 3-firm, 5-year panel
2. **Unit test:** Verify one-tailed p-value formula `p_two/2 if β>0 else 1-p_two/2` for both positive and negative β
3. **Integration test:** Run H7 on a small synthetic panel and verify:
   - N obs matches after listwise deletion
   - Coefficients match OLS computed manually with `statsmodels`
   - LaTeX table renders valid LaTeX (compile check)

### Simplifications

1. Remove dead `Weak_Modal_Gap` computation from `prepare_regression_data()` (MINOR-3)
2. Consider unifying the star-notation p-value basis (one-tailed vs two-tailed) across Manager and CEO IVs in the LaTeX table (MINOR-1)

---

## 7) Open Questions / Unverified Items

| # | Item | Status | Missing Artifact / Verification Needed |
|---|------|--------|---------------------------------------|
| 1 | Raw Compustat quarterly row count | UNVERIFIED | Cannot verify without loading `inputs/comp_na_daily_all/comp_na_daily_all.parquet` (large file, not loaded in this audit) |
| 2 | Raw CRSP daily row count | UNVERIFIED | Cannot verify without loading all 96 CRSP quarterly parquet files |
| 3 | CCM linktable row count (32,421 per provenance) | UNVERIFIED | Would need: `python -c "import pandas as pd; print(len(pd.read_parquet('inputs/CRSPCompustat_CCM/CRSPCompustat_CCM.parquet')))"` |
| 4 | Stage 2 linguistic variables 2002 has 3,355 rows | UNVERIFIED | Would need: `python -c "import pandas as pd; print(len(pd.read_parquet('outputs/2_Textual_Analysis/2.2_Variables/2026-02-27_200910/linguistic_variables_2002.parquet')))"` |
| 5 | Whether `drop_absorbed=True` absorbed any entities in the current run | UNVERIFIED but LIKELY NO | The entity count in regression txt matches `df_reg.gvkey.nunique()` for all checked models, suggesting no absorption occurred. Would need to check all 9 models systematically. |
| 6 | Whether the 50 rows where `amihud_illiq_lead == amihud_illiq` are genuine coincidences or a lead-construction bug | LOW RISK | Spot-checked: these are firms where illiquidity happened to be approximately equal in consecutive fiscal years. 50/95,771 = 0.05% — plausible coincidence rate. |
| 7 | Impact of IHS/log DV transform on H7 results | NOT TESTED | Requires new regression specification. Since all β₁ are negative/zero (opposite to predicted direction), a transform is unlikely to change the qualitative conclusion (H7 NOT SUPPORTED). |

---

**Audit Conclusion:**

The H7 suite is **correctly implemented** with respect to its provenance specification. All merge operations, variable constructions, regression specifications, p-value computations, and output artifacts are internally consistent and match their documented claims. The primary finding (**MAJOR-1: DV not re-winsorized, extreme skew**) is a methodological concern that is standard in the Amihud illiquidity literature and should be addressed with a log or winsorization treatment. However, given that all 9 regression models produce β₁ coefficients in the **opposite direction** to the hypothesis (negative rather than positive) with no model approaching significance, the qualitative conclusion — **H7 NOT SUPPORTED** — is robust to this concern. A DV transformation would reduce noise but is unlikely to flip the sign of all 9 coefficients.

No BLOCKERs identified. The suite is safe for reporting with the caveats noted above.
