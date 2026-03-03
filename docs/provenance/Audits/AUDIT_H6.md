# AUDIT REPORT: H6 SEC Scrutiny (CCCL) and Speech Vagueness

**Suite ID:** H6
**Audit Date:** 2026-02-28
**Auditor:** Antigravity (AI Coding Assistant)
**Audit Type:** Hardnosed implementation audit per P_Audit.txt protocol

---

## 0) Suite Identification

| Field | Value |
|-------|-------|
| **Suite ID** | H6 |
| **Stage 3 Builder** | `src/f1d/variables/build_h6_cccl_panel.py` |
| **Stage 4 Runner** | `src/f1d/econometric/run_h6_cccl.py` |
| **Model Family** | Panel OLS with absorbed entity + time fixed effects |
| **Estimator** | `linearmodels.PanelOLS` with `entity_effects=True`, `time_effects=True`, `drop_absorbed=True` |
| **Provenance Doc** | `docs/provenance/H6.md` |
| **Latest Panel Output** | `outputs/variables/h6_cccl/2026-02-27_224247/h6_cccl_panel.parquet` |
| **Latest Econometric Output** | `outputs/econometric/h6_cccl/2026-02-27_224404/` |

---

## 1) Suite Contract (What the suite claims it does)

Extracted from `docs/provenance/H6.md`:

- **Estimation unit:** Call-level (individual earnings call). Primary key: `file_name`.
- **DV(s):** 7 dependent variables:
  1. `Manager_QA_Uncertainty_pct`
  2. `CEO_QA_Uncertainty_pct`
  3. `Manager_QA_Weak_Modal_pct`
  4. `CEO_QA_Weak_Modal_pct`
  5. `Manager_Pres_Uncertainty_pct`
  6. `CEO_Pres_Uncertainty_pct`
  7. `Uncertainty_Gap` (Manager QA - Manager Pres Uncertainty, computed in Stage 4)
- **IV(s):** `shift_intensity_mkvalt_ff48_lag` (lagged CCCL exposure, market-value weighted, FF48 industry)
- **Interactions:** None
- **Controls (BASE_CONTROLS):** Size, Lev, ROA, TobinsQ, CashHoldings
- **Fixed Effects:** Firm FE (`C(gvkey)`) + Year FE (`C(year)`)
- **Variance estimator:** Firm-clustered (`cluster_entity=True`, `debiased=True`)
- **Transforms:**
  - Linguistic vars: per-year 0%/99% winsorization (engine-level)
  - Compustat controls: per-year 1%/99% winsorization (engine-level)
  - CCCL instrument: no winsorization (pre-computed externally)
  - No standardization applied
- **Missingness policy:** NaN preserved in panel; `dropna` at regression time; `inf` replaced with NaN
- **Sample splits:** Main (FF12 codes 1-7, 9-10, 12), Finance (FF12=11), Utility (FF12=8)
- **Sample filter:** `min_calls >= 5` (firms with <5 calls having valid CCCL_lag excluded)
- **Pre-trends falsification:** Each spec also run with CCCL_lag + CCCL_lead1 + CCCL_lead2
- **Hypothesis tests:** One-tailed: beta(CCCL_lag) < 0

---

## 2) Evidence Map (Claim -> Evidence -> Status)

| # | Claim | Where Claimed | Where Verified | Status | Notes |
|---|-------|---------------|----------------|--------|-------|
| 1 | Panel has 112,968 rows | H6.md:107, README:10 | Ad-hoc: `len(panel) = 112,968` | **PASS** | Matches exactly |
| 2 | Panel has 25 columns | H6.md:107 | Ad-hoc: `len(panel.columns) = 25` | **PASS** | |
| 3 | Zero row-delta on all merges | H6.md:208, build_h6_cccl_panel.py:220-221 | Code raises `ValueError` if delta != 0 | **PASS** | Hard-fail enforced |
| 4 | file_name is unique (call-level) | H6.md:19 | Ad-hoc: `panel['file_name'].is_unique = True` | **PASS** | |
| 5 | Sample split: Main=88,205, Finance=20,482, Utility=4,281 | H6.md:183 | Ad-hoc: verified exactly | **PASS** | |
| 6 | CCCL_lag valid for 86,189 calls (76.3%) | H6.md:229 | Ad-hoc: `86,189 / 112,968 = 76.3%` | **PASS** | |
| 7 | CCCL_lead1 valid for 94,746 (83.9%) | H6.md:230 | Ad-hoc: verified exactly | **PASS** | |
| 8 | CCCL_lead2 valid for 90,538 (80.1%) | H6.md:231 | Ad-hoc: verified exactly | **PASS** | |
| 9 | CCCL instrument has 145,693 rows, 0 dups | H6.md:159, 178 | Ad-hoc: verified exactly | **PASS** | |
| 10 | CCCL year range 2005-2021 | H6.md:159 | Ad-hoc: `year.min()=2005, max()=2021` | **PASS** | |
| 11 | 21 regressions (7 DVs x 3 samples) | H6.md:108-111 | Ad-hoc: `len(diag) = 21` | **PASS** | |
| 12 | Main/Mgr QA Unc: N=63,902, firms=1,751 | H6.md:403, regression text | Ad-hoc: verified, CSV matches text | **PASS** | |
| 13 | Finance/Mgr QA Unc: N=15,662, firms=436 | H6.md:405 | Ad-hoc: verified | **PASS** | |
| 14 | Firm-clustered SEs used | H6.md:72, run_h6_cccl.py:201 | Code: `cov_type="clustered", cluster_entity=True` | **PASS** | |
| 15 | One-tailed p-values computed correctly | H6.md:308-309, run_h6_cccl.py:252-253 | Ad-hoc: all 21 p-values verified | **PASS** | |
| 16 | LaTeX table coefficients match diagnostics | h6_cccl_table.tex, model_diagnostics.csv | Ad-hoc: all 5 Main coefficients match to 4dp | **PASS** | |
| 17 | Pre-trends: no significant pre-trends | H6.md:475, README:475 | Ad-hoc: **MULTIPLE VIOLATIONS FOUND** | **FAIL** | See Finding #1 |
| 18 | within_r2 reported in diagnostics/LaTeX | H6.md:424 | Ad-hoc: all 21 within_r2 values are NaN | **FAIL** | See Finding #2 |
| 19 | README says "0/6 significant" | README:477 | Ad-hoc: actual=4/21 significant | **FAIL** | See Finding #3 |
| 20 | CCCL merge uses fyearq (B5 fix) | H6.md:216-217, cccl_instrument.py:77-84 | Code: merge_asof backward on gvkey | **PASS** | |
| 21 | merge_asof has tolerance guard | Expected | cccl_instrument.py:77-84 / panel_utils.py:152-158 | **FAIL** | See Finding #4 |
| 22 | Consecutive-year check on lag/lead | H6.md:222-226 | build_h6_cccl_panel.py:105-106, 113-114, 121-122 | **PASS** | Properly NaN'd if gap > 1 |
| 23 | Deduplication on CCCL instrument | H6.md:218 | cccl_instrument.py:124-129 | **PASS** | Hard-fail if duplicates found |
| 24 | gvkey zero-padded to 6 chars | H6.md:256 | Ad-hoc: all length 6 confirmed | **PASS** | |

---

## 3) End-to-End Implementation Audit

### A) Stage 1/2 Preconditions

**Manifest anchoring:** The builder loads from `outputs/1.4_AssembleManifest/` via `ManifestFieldsBuilder` (`manifest_fields.py:56-57`). Uses `get_latest_output_dir()` to resolve timestamp. Columns loaded: `file_name, ceo_id, ceo_name, gvkey, ff12_code, ff12_name, start_date`. Year filtering applied via `start_date.dt.year`.

**Linguistic outputs anchoring:** Six linguistic builders (`ManagerQAUncertaintyBuilder`, etc.) load from `outputs/2_Textual_Analysis/2.2_Variables/` via the `LinguisticEngine` singleton. Join key: `file_name`. Match rates verified: 95.8% for Manager vars, 68.0% for CEO vars.

**Hidden dependencies:** The `CCCLInstrumentBuilder` (`cccl_instrument.py:65-66`) loads the `CompustatEngine` to attach `fyearq` via `merge_asof`. This creates an implicit dependency on `inputs/comp_na_daily_all/comp_na_daily_all.parquet`. This is documented in H6.md:141 but not obvious from the builder name alone.

**PASS** — Stage 1/2 anchoring is correct.

### B) Stage 3 Panel Builder Audit

**Builder module:** `src/f1d/variables/build_h6_cccl_panel.py` (308 lines)

#### B1) Primary Key Uniqueness

`file_name` is unique across the entire panel (verified ad-hoc: `panel['file_name'].is_unique = True`). The `panel_utils.attach_fyearq()` function (`panel_utils.py:119-128`) asserts `file_name` uniqueness before `set_index` to prevent silent corruption. **PASS.**

#### B2) Merge Sequence and Zero Row-Delta

The builder merges 12 variables onto the manifest via `panel.merge(data, on="file_name", how="left")` at `build_h6_cccl_panel.py:217`. After each merge, rows are counted (`build_h6_cccl_panel.py:216-221`) and a `ValueError` is raised if `delta != 0`. All merges use `how="left"` on the unique key `file_name`, so no row expansion is possible. **PASS.**

#### B3) Many-to-Many Join Risk

The CCCL instrument merge inside `CCCLInstrumentBuilder` (`cccl_instrument.py:123-129`) explicitly checks for duplicate `(gvkey, fyearq_int)` in the CCCL data before merging, and raises `ValueError` if found. The row count is also verified after merge (`cccl_instrument.py:140-144`). **PASS.**

#### B4) Timing Alignment and Look-Ahead Bias

**merge_asof for fyearq:** Both `CCCLInstrumentBuilder` (`cccl_instrument.py:77-84`) and `panel_utils.attach_fyearq()` (`panel_utils.py:152-158`) use `pd.merge_asof(direction="backward")` to match call `start_date` to the most recent Compustat `datadate`. This is correct (no look-ahead).

**HOWEVER — No tolerance parameter:** Neither merge_asof call specifies a `tolerance` parameter. This means a call in 2017 for a firm whose last Compustat observation was in 2007 will match to the 2007 datadate, producing `fyearq=2007` for a 2017 call. **78 stale matches found** (|calendar_year - fyearq| > 2), with 72 of those having valid CCCL_lag values that are from the **wrong fiscal year**. This is a real data contamination issue. See Finding #4.

**Lag construction:** The lag/lead creation in `create_lag_variables()` (`build_h6_cccl_panel.py:66-153`) correctly:
- Takes last call per (gvkey, fyearq) by start_date (`build_h6_cccl_panel.py:91-95`)
- Shifts within gvkey groups (`build_h6_cccl_panel.py:101-104`)
- Enforces consecutive fiscal years (gap == 1) or NaN (`build_h6_cccl_panel.py:105-106`)

**CCCL_lag starts at fyearq=2006:** Verified — the instrument begins in 2005, so lag(2005) = NaN, lag(2006) = value from 2005. This is correct. **PASS** for lag logic, **FAIL** for merge_asof tolerance.

#### B5) Outlier Handling

| Engine | Winsorization | Where | Consistent? |
|--------|--------------|-------|-------------|
| CompustatEngine | Per-year 1%/99% on fyearq | `_compustat_engine.py:1055-1057` | Yes |
| LinguisticEngine | Per-year 0%/99% (lower=0.0) | `_linguistic_engine.py:255-258` | Yes — lower bound intentionally 0 for pct vars |
| CCCL Instrument | None | Pre-computed externally | Acceptable — documented |

No double-winsorization. Panel builders receive already-winsorized data. **PASS.**

#### B6) Missingness

Missing values are preserved as NaN in the panel (left joins). The panel has 112,968 rows regardless of missingness. Regression-time `dropna` reduces the sample (e.g., Main/Mgr QA Unc drops from 88,205 to 63,902). The `inf` → `NaN` replacement at `run_h6_cccl.py:161` prevents inf values from surviving into regressions. **PASS.**

#### B7) Variable Semantics

| Variable | Provenance Definition | Implementation | Match? |
|----------|----------------------|----------------|--------|
| `shift_intensity_mkvalt_ff48_lag` | Lagged CCCL exposure (mkvalt-weighted, FF48) | `build_h6_cccl_panel.py:100-106`, shifted by 1 fyearq | **PASS** |
| `Manager_QA_Uncertainty_pct` | Manager uncertainty % in Q&A | `_linguistic_engine.py` via Stage 2 | **PASS** |
| `Size` | `ln(atq)` where atq > 0 | `_compustat_engine.py:940` | **PASS** |
| `Lev` | `(dlcq + dlttq) / atq` | `_compustat_engine.py:945` | **PASS** |
| `ROA` | `iby_annual / avg(atq)` | `_compustat_engine.py:946-956` | **PASS** |
| `TobinsQ` | `(mktcap + debt_book) / atq` | `_compustat_engine.py:969-973` | **PASS** |
| `CashHoldings` | `cheq / atq` | `_compustat_engine.py:962` | **PASS** |
| `Uncertainty_Gap` | `Manager_QA - Manager_Pres Uncertainty` | `run_h6_cccl.py:139-141` | **PASS** |

### C) Shared Engines / Variable Builders Audit

#### CompustatEngine (`_compustat_engine.py`)

- **Dedup logic:** `drop_duplicates(subset=["gvkey", "datadate"], keep="last")` at line 1107. Deterministic (keeps most recent restatement). **PASS.**
- **Winsorization:** Per-year (fyearq) 1%/99% via `_winsorize_by_year()` (line 1055-1057). Min 10 obs per year-group. Skips binary variables (DividendPayer, is_div_payer_5yr) and already-winsorized Biddle vars. **PASS.**
- **Date matching:** merge_asof backward on (gvkey, datadate ≤ start_date). No tolerance specified — same stale-match risk as CCCL builder. However, for H6 purposes, the Compustat variables are contemporaneous controls, so a stale match (wrong-year Size/Lev/ROA) is less critical than a stale CCCL match.
- **Known footguns:** Lev uses `fillna(0)` for dlcq/dlttq before summing (`_compustat_engine.py:945`). This treats missing debt as zero debt, which is standard Compustat practice but worth noting.

#### LinguisticEngine (`_linguistic_engine.py`)

- **Dedup logic:** No dedup needed — Stage 2 outputs have unique `file_name` per year file. Concat across years. **PASS.**
- **Winsorization:** Per-year 0%/99% (lower=0.0, upper=0.99, min_obs=1) via `winsorize_by_year()` at line 255-258. The lower=0.0 means no floor clipping (linguistic percentages cannot be negative). **PASS.**
- **Date matching:** Not applicable — linguistic vars join on `file_name` directly. **PASS.**

#### CCCLInstrumentBuilder (`cccl_instrument.py`)

- **Dedup logic:** Explicit uniqueness assertion on `(gvkey, fyearq_int)` at line 124-129. Hard-fail if duplicates found. **PASS.**
- **Winsorization:** None applied. The CCCL instrument is pre-computed externally and heavily zero-inflated (46.9% zeros in lag, 61.2% zeros in raw mkvalt_ff48). Not winsorizing is acceptable but notable.
- **Date matching:** Uses merge_asof backward to attach fyearq, then merges CCCL on `(gvkey, fyearq_int)`. The B5 fix correctly aligns fiscal year. **PASS** for logic, **FAIL** for tolerance (see Finding #4).
- **Known footgun:** The builder's default column is `shift_intensity_sale_ff48` (line 45) but `build_h6_cccl_panel.py` passes config key `cccl_instrument_mkvalt` which overrides to `shift_intensity_mkvalt_ff48`. The mkvalt weighting is 61.2% zeros vs 0.0% zeros for sale weighting. This is a methodological choice, not a bug, but the heavy zero-inflation may attenuate regression coefficients.

### D) Stage 4 Runner / Estimation Audit

**Runner module:** `src/f1d/econometric/run_h6_cccl.py` (524 lines)

#### D1) Model Specification

**Formula (non-pretrends):** `{DV} ~ 1 + shift_intensity_mkvalt_ff48_lag + Size + Lev + ROA + TobinsQ + CashHoldings + EntityEffects + TimeEffects`

Verified at `run_h6_cccl.py:176-180`. Matches provenance H6.md exactly. **PASS.**

**Formula (pretrends):** Adds `+ shift_intensity_mkvalt_ff48_lead1 + shift_intensity_mkvalt_ff48_lead2`. Verified at `run_h6_cccl.py:167-171`. **PASS.**

#### D2) Fixed Effects and Clustering

- Entity FE absorbed via `PanelOLS(..., entity_effects=True)` — absorbs gvkey means.
- Time FE absorbed via `TimeEffects` in formula with `drop_absorbed=True`.
- SEs: `cov_type="clustered", cluster_entity=True` at `run_h6_cccl.py:201`.
- `debiased=True` is the linearmodels default.

**Non-unique (gvkey, year) multi-index:** The panel is call-level (3.9 calls per gvkey-year on average, up to 38). PanelOLS with `set_index(["gvkey", "year"])` allows non-unique entries — each row is treated as a separate observation. Entity effects demean within gvkey; time effects demean within year. This is methodologically equivalent to including C(gvkey) + C(year) dummies, which is what the provenance specifies. **PASS** — linearmodels handles this correctly.

#### D3) Sample Splits and Filters

- Industry splits via `assign_industry_sample()` from `panel_utils.py:46-73`. FF12=11 → Finance, FF12=8 → Utility, else → Main. **PASS.**
- `min_calls >= 5` filter at `run_h6_cccl.py:486-491`: counts valid (non-null) CCCL_lag per gvkey, excludes firms with < 5 valid calls. Verified ad-hoc: Main drops from 88,205 to 86,820 rows. **PASS.**

#### D4) One-Tailed P-Values

At `run_h6_cccl.py:252-253`:
```python
p1_one = p1_two / 2 if beta1 < 0 else 1 - p1_two / 2
```

H6 hypothesis: beta < 0 (scrutiny reduces uncertainty). If beta < 0: p_one = p_two/2 (correct). If beta >= 0: p_one = 1 - p_two/2 (correct — makes it nearly impossible to be significant in the wrong direction). All 21 p-values verified to match this formula. **PASS.**

#### D5) Within-R² Computation

The custom within-R² computation at `run_h6_cccl.py:212-238` has an **index alignment bug**: `df_reg[dv_var]` has an integer index (from the original DataFrame), but `model.fitted_values` has a MultiIndex `(gvkey, year)` from `set_index`. The `intersection()` call returns an empty index, producing NaN for all 21 specifications. The `within_r2` column in `model_diagnostics.csv` is entirely NaN, and the LaTeX table shows empty Within-R² cells. See Finding #2.

#### D6) Output Validation

| Output | Expected | Actual | Match |
|--------|----------|--------|-------|
| Regression text files | 42 (21 base + 21 pretrends) | 42 files present | **PASS** |
| `model_diagnostics.csv` | 21 rows | 21 rows | **PASS** |
| `h6_cccl_table.tex` | LaTeX table, Main sample, 5 DVs | Present, coefficients match CSV | **PASS** |
| `summary_stats.csv` | By-sample variable stats | Present, N/mean verified vs panel | **PASS** |
| `summary_stats.tex` | LaTeX version | Present | **PASS** |

### E) Artifact Integrity & Cross-Consistency

#### E1) Diagnostics CSV vs Regression Text

| Spec | CSV beta1 | Text beta1 | CSV SE | Text SE | CSV N | Text N | Match |
|------|-----------|------------|--------|---------|-------|--------|-------|
| Main/Mgr QA Unc | -0.0865 | -0.0865 | 0.0642 | 0.0642 | 63,902 | 63,902 | **PASS** |
| Fin/Mgr QA Unc | -1.3066 | -1.3066 | 0.5961 | 0.5961 | 15,662 | 15,662 | **PASS** |

All checked specifications match exactly.

#### E2) LaTeX Table vs Diagnostics CSV

All 5 Main-sample coefficients in the LaTeX table match the diagnostics CSV to 4 decimal places. Stars in the LaTeX table use **one-tailed p-values** (`beta1_p_one`), which is consistent with the directional hypothesis. **PASS.**

#### E3) Summary Stats vs Panel

The `summary_stats.csv` reports N and Mean for each variable by sample. Cross-checked Main/Uncertainty_Gap: N=84,366 (matches panel computation), Mean=-0.0419 (matches). **PASS.**

#### E4) README vs Provenance vs Diagnostics

**INCONSISTENCY FOUND:**
- **README** (`README.md:477`): States "H6 CCCL Speech: **Null** — 0/6 significant treatment effects"
- **Provenance** (`H6.md:412`): States "H6 PARTIALLY SUPPORTED — 4/21 specifications show significant negative β₁"
- **Diagnostics CSV**: Shows 4/21 significant at one-tailed p<0.05, all in Finance sample

The README reports "0/6" which likely reflects an earlier run or summarizes only the Main sample. The provenance doc's "4/21" matches the actual diagnostics. See Finding #3.

---

## 4) Findings (Grouped by Severity)

### Finding #1 — MAJOR: Pre-Trends Violations Undermine Causal Interpretation

**Severity:** MAJOR

**Symptom:** Multiple pre-trends falsification tests show statistically significant lead coefficients. Future CCCL exposure predicts current uncertainty language, which should not happen if the instrument is exogenous.

**Evidence:**
- Main/Mgr QA Uncertainty: `CCCL_lead1 beta=-0.1021, p=0.0052` (***) — `regression_results_Main_Manager_QA_Uncertainty_pct_PRETRENDS.txt:26`
- Main/Mgr QA Weak Modal: `CCCL_lead1 beta=-0.0770, p=0.0013` (***) — PRETRENDS output
- Main/CEO QA Weak Modal: `CCCL_lead1 beta=-0.1504, p=0.0032` (***) — PRETRENDS output
- Main/Uncertainty Gap: `CCCL_lead2 beta=-0.1733, p=0.0164` (**) — PRETRENDS output
- Finance/Uncertainty Gap: `CCCL_lead1 beta=-1.4316, p=0.0412` (**) — PRETRENDS output
- Finance/CEO QA Uncertainty: `CCCL_lead1 beta=-1.3281, p=0.0803` (*) — PRETRENDS output
- Utility/CEO Pres Uncertainty: `CCCL_lead1 beta=-2.1202, p=0.0074` (***) — PRETRENDS output

**Why it matters:** Pre-trends violations indicate that the CCCL instrument may not satisfy the exclusion restriction. Firms that will face future SEC scrutiny already show lower uncertainty language today, suggesting reverse causality or confounding. This undermines the causal interpretation of H6 results, particularly the Finance-sample significance. The provenance doc (`H6.md:475`) states "no significant pre-trends detected" which is **factually incorrect** — 7 lead coefficients are significant at p<0.10, with 5 at p<0.05 and 4 at p<0.01.

**How to verify:**
```bash
# Parse all PRETRENDS files for significant lead coefficients
python -c "
import os
for f in sorted(os.listdir('outputs/econometric/h6_cccl/2026-02-27_224404')):
    if 'PRETRENDS' in f:
        with open(f'outputs/econometric/h6_cccl/2026-02-27_224404/{f}') as fh:
            for line in fh:
                if 'lead' in line and any(x in line for x in ['lead1', 'lead2']):
                    parts = line.strip().split()
                    if len(parts)>=5 and float(parts[4])<0.10:
                        print(f'{f}: {line.strip()}')
"
```

**Fix:**
1. Update `H6.md:475` to accurately document the pre-trends violations.
2. Add automated pre-trends parsing to `run_h6_cccl.py` that flags significant leads in `model_diagnostics.csv`.
3. In the thesis, discuss pre-trends violations and their implications for causal inference. Consider alternative instruments or robustness checks (e.g., restricting sample to firms without significant pre-trends).

**Rerun impact:** No rerun needed for code — this is an interpretation/documentation issue. The pre-trends results are already generated and saved.

---

### Finding #2 — MAJOR: within_r2 Computation Bug (All NaN)

**Severity:** MAJOR

**Symptom:** The `within_r2` column in `model_diagnostics.csv` is NaN for all 21 specifications. The LaTeX table shows empty Within-R² cells.

**Evidence:** `run_h6_cccl.py:212-238`:
```python
y_full = df_reg[dv_var]          # integer index (0, 1, 2, ...)
y_hat_full = model.fitted_values  # MultiIndex (gvkey, year)
common_idx = y_full.index.intersection(y_hat_full.index)  # EMPTY
```

Ad-hoc verification confirmed: `within_r2` is NaN for all 21 rows in `model_diagnostics.csv`.

The `model.rsquared_within` field from linearmodels IS available and contains valid values (e.g., 0.0007 for Main/Mgr QA Unc), but the code tries to compute a custom within-R² that fails due to index mismatch.

**Why it matters:** Within-R² is a key model fit diagnostic for panel FE regressions. Its absence from the LaTeX table and diagnostics makes the paper incomplete. The `rsquared` column in the CSV contains `model.rsquared_within` values (which ARE valid), but these are not used in the LaTeX table's Within-R² row.

**How to verify:**
```python
diag = pd.read_csv('outputs/econometric/h6_cccl/2026-02-27_224404/model_diagnostics.csv')
print(diag['within_r2'].isna().all())  # True
print(diag['rsquared'].notna().all())  # True — these ARE valid within-R²
```

**Fix:** In `run_h6_cccl.py`, replace the custom within-R² computation with `model.rsquared_within` directly:
```python
# run_h6_cccl.py:212-238 — replace entire try/except block with:
within_r2 = float(model.rsquared_within)
```
Or fix the index alignment:
```python
# After set_index at line 192, df_reg index is (gvkey, year)
# fitted_values also has (gvkey, year) index
# So use df_panel (which has the multi-index) instead of df_reg:
y_full = df_panel[dv_var]
y_hat_full = model.fitted_values
```

**Rerun impact:** Stage 4 rerun required to regenerate `model_diagnostics.csv` and `h6_cccl_table.tex` with correct within-R² values.

---

### Finding #3 — MAJOR: README vs Provenance Results Inconsistency

**Severity:** MAJOR

**Symptom:** README states H6 is "Null — 0/6 significant treatment effects" but the actual results show 4/21 significant specifications, all in Finance sample.

**Evidence:**
- `README.md:477`: "H6 CCCL Speech — **Null** | 0/6 significant treatment effects"
- `H6.md:412`: "H6 PARTIALLY SUPPORTED — 4/21 specifications show significant negative β₁ at p<0.05"
- `model_diagnostics.csv`: 4 rows with `h6_sig=True` (Finance/Mgr QA Unc, Finance/Mgr QA Weak Modal, Finance/CEO Pres Unc, Finance/Uncertainty Gap)

**Why it matters:** The README is the primary entry point for readers. An incorrect summary ("Null") when Finance sample shows partial support is misleading. The README may reflect an earlier run with different results (the provenance doc was updated to 2026-02-28 but the README was last updated 2026-02-23).

**How to verify:**
```python
diag = pd.read_csv('outputs/econometric/h6_cccl/2026-02-27_224404/model_diagnostics.csv')
print(f"Significant: {diag['h6_sig'].sum()}/21")
```

**Fix:** Update `README.md:477` to match the provenance doc:
```
| H6 CCCL Speech | **Partial** | 4/21 sig (Finance sample only; pre-trends concerns) |
```

**Rerun impact:** Documentation update only — no code rerun needed.

---

### Finding #4 — MINOR: merge_asof Without Tolerance Creates 78 Stale Matches

**Severity:** MINOR

**Symptom:** 78 calls have `|calendar_year - fyearq| > 2`, with the worst case being a 12-year gap (2018 call matched to fyearq=2006 Compustat data). 72 of these stale-match rows have valid CCCL_lag values that are from the **wrong fiscal year**.

**Evidence:**
- `panel_utils.py:152-158`: `pd.merge_asof(..., direction="backward")` — no `tolerance` parameter.
- `cccl_instrument.py:77-84`: Same pattern — no tolerance.
- Ad-hoc verification: 78 stale matches found (all in Main sample), e.g., `gvkey=003087, cal_year=2017, fyearq=2007.0` (10-year gap).

**Why it matters:** For these 78 rows, the CCCL_lag value comes from the wrong fiscal year (e.g., a 2017 call gets CCCL_lag from 2006 instead of 2016). This is data contamination. However, the impact is small: 78/112,968 = 0.07% of the panel, and 72/63,902 = 0.11% of the Main regression sample. These are likely firms that left Compustat but continued holding earnings calls.

**How to verify:**
```python
panel = pd.read_parquet('outputs/variables/h6_cccl/2026-02-27_224247/h6_cccl_panel.parquet')
panel['start_date_dt'] = pd.to_datetime(panel['start_date'])
panel['cal_year'] = panel['start_date_dt'].dt.year
stale = panel[abs(panel['cal_year'] - panel['fyearq']) > 2]
print(f"Stale matches: {len(stale)}")
```

**Fix:** Add a tolerance of ~548 days (1.5 years) to `panel_utils.attach_fyearq()`:
```python
merged = pd.merge_asof(
    panel_sorted_valid, fyearq_df,
    left_on="_start_date_dt", right_on="datadate",
    by="gvkey", direction="backward",
    tolerance=pd.Timedelta(days=548)  # 1.5 years max gap
)
```

**Rerun impact:** Stage 3 + Stage 4 rerun required. Impact on results: negligible (0.07% of data).

---

### Finding #5 — MINOR: CCCL mkvalt Weighting Creates Heavy Zero-Inflation

**Severity:** MINOR (methodological note)

**Symptom:** The `shift_intensity_mkvalt_ff48` variable is 61.2% zeros in the raw data (46.9% zeros in the lag). By contrast, the sale-weighted version (`shift_intensity_sale_ff48`) has 0.0% zeros.

**Evidence:**
- Ad-hoc: `cccl['shift_intensity_mkvalt_ff48']: zeros=61.2%`
- Ad-hoc: `cccl['shift_intensity_sale_ff48']: zeros=0.0%`
- Panel lag: `shift_intensity_mkvalt_ff48_lag: zeros=46.9%, mean=0.006565`

**Why it matters:** Heavy zero-inflation in the IV means the regression is largely driven by variation among the 53.1% of non-zero observations. For nearly half the sample, the instrument is zero — these observations contribute nothing to the coefficient estimate but inflate the sample size and deflate standard errors. This may attenuate the treatment effect and bias toward null results in the Main sample. The significant Finance results may be driven by a different zero-inflation rate in that subsample.

**How to verify:**
```python
for sample in ['Main', 'Finance', 'Utility']:
    s = panel[panel['sample']==sample]['shift_intensity_mkvalt_ff48_lag'].dropna()
    print(f"{sample}: zeros={100*(s==0).mean():.1f}%, mean={s.mean():.6f}")
```

**Fix:** Consider running a sensitivity analysis with `shift_intensity_sale_ff48` (sale-weighted, 0% zeros) alongside the mkvalt-weighted version. Document the choice and its implications.

**Rerun impact:** Optional — would require adding sale-weighted variable to Stage 3 panel and Stage 4 regressions.

---

### Finding #6 — NOTE: LaTeX Table Only Shows Main Sample

**Severity:** NOTE

**Symptom:** The LaTeX table (`h6_cccl_table.tex`) only shows Main sample results for 5 of 7 DVs (excludes Weak Modal measures). Finance and Utility sample results, including the 4 significant Finance results, are not shown in the table.

**Evidence:** `run_h6_cccl.py:286-290`:
```python
r_1 = get_res("Manager_QA_Uncertainty_pct")  # defaults to Main
r_2 = get_res("CEO_QA_Uncertainty_pct")
# ... only Main sample queried
```

**Why it matters:** The most interesting results (Finance sample significance) are only visible in the diagnostics CSV and individual regression text files, not in the publication table. A reader looking at the LaTeX table alone would conclude H6 is entirely null.

**Fix:** Expand the LaTeX table to include Finance sample results, or create a separate Finance-sample table. At minimum, add a note to the table caption referencing Finance results.

**Rerun impact:** Stage 4 code change + rerun.

---

### Finding #7 — NOTE: Provenance Doc Claims "No Significant Pre-Trends" — Incorrect

**Severity:** NOTE (overlaps with Finding #1, but specifically about the provenance doc)

**Symptom:** `H6.md:475` states: "Pre-trends test: CCCL_lag vs CCCL_lead1/lead2 — no significant pre-trends detected."

**Evidence:** See Finding #1 — at least 7 significant lead coefficients found across samples. The provenance doc assertion is factually incorrect based on the actual output files in the same run directory.

**Fix:** Update `H6.md:475` to accurately describe the pre-trends findings.

---

## 5) Rerun Plan (Minimal, Deterministic)

### Prerequisites
Stages 1 and 2 must have been run previously (outputs present in `outputs/1.4_AssembleManifest/` and `outputs/2_Textual_Analysis/2.2_Variables/`).

### Commands
```bash
# Step 1: Rebuild H6 panel (Stage 3)
python -m f1d.variables.build_h6_cccl_panel

# Step 2: Run H6 regressions (Stage 4)
python -m f1d.econometric.run_h6_cccl
```

### Acceptance Tests

| Check | Expected | Command |
|-------|----------|---------|
| Panel row count | 112,968 | `python -c "import pandas as pd; p=pd.read_parquet('outputs/variables/h6_cccl/LATEST/h6_cccl_panel.parquet'); assert len(p)==112968"` |
| Panel columns | 25 | `assert len(p.columns) == 25` |
| file_name unique | True | `assert p['file_name'].is_unique` |
| CCCL_lag valid | ~86,189 | `assert abs(p['shift_intensity_mkvalt_ff48_lag'].notna().sum() - 86189) < 10` |
| Sample split | Main=88,205, Fin=20,482, Util=4,281 | `assert p['sample'].value_counts()['Main'] == 88205` |
| Diagnostics rows | 21 | `d=pd.read_csv('.../model_diagnostics.csv'); assert len(d)==21` |
| Main/Mgr QA Unc N | 63,902 | `r=d[(d['sample']=='Main')&(d['dv']=='Manager_QA_Uncertainty_pct')]; assert r.iloc[0]['n_obs']==63902` |
| Main/Mgr QA Unc beta1 | -0.0865 ± 0.0005 | `assert abs(r.iloc[0]['beta1'] - (-0.0865)) < 0.0005` |
| within_r2 not all NaN (after fix) | True | `assert d['within_r2'].notna().any()` |

**Determinism:** Expected with `random_seed: 42` and `thread_count: 1` (no stochastic elements in panel construction or OLS). Exact coefficient match expected to 4+ decimal places.

---

## 6) Refactor & Hardening Recommendations

### 6.1 Assertions to Add

1. **merge_asof tolerance in `panel_utils.attach_fyearq()`** — Add `tolerance=pd.Timedelta(days=548)` to prevent stale matches. File: `panel_utils.py:152`.

2. **Pre-trends significance auto-detection in `run_h6_cccl.py`** — After running pretrends regressions, extract lead coefficients and flag significant ones in `model_diagnostics.csv`:
```python
if model_pt is not None:
    for lead_var in ['shift_intensity_mkvalt_ff48_lead1', 'shift_intensity_mkvalt_ff48_lead2']:
        lead_p = model_pt.pvalues.get(lead_var, np.nan)
        if not np.isnan(lead_p) and lead_p < 0.05:
            print(f"  WARNING: Pre-trend violation: {lead_var} p={lead_p:.4f}")
```

3. **CCCL zero-inflation diagnostic** — Print the zero-inflation rate of CCCL_lag per sample in the regression output.

### 6.2 Logging/Provenance Improvements

1. **Print stale match count** in `attach_fyearq()` — log how many rows have |cal_year - fyearq| > 2.
2. **Print zero-inflation rate** of CCCL_lag in the regression loop.
3. **Save pre-trends summary** to `model_diagnostics.csv` (add columns for lead1_beta, lead1_p, lead2_beta, lead2_p).

### 6.3 Tests to Add

1. **Unit test: within-R² computation** — Test that within_r2 is not NaN for a simple synthetic panel.
2. **Unit test: one-tailed p-value logic** — Test sign-conditional halving with known beta/p values.
3. **Integration test: stale merge_asof detection** — Test with synthetic data where a firm has a 5-year gap in Compustat coverage.
4. **Regression test: coefficient stability** — Compare Main/Mgr QA Unc beta1 against baseline (-0.0865 ± 0.001).

### 6.4 Simplifications

1. **Use `model.rsquared_within` directly** instead of the custom within-R² computation (`run_h6_cccl.py:212-238`). The entire try/except block can be replaced with one line.
2. **Centralize merge_asof tolerance** in `panel_utils.py` so all builders use the same policy.

---

## 7) Open Questions / Unverified Items

| # | Item | What's Missing | How to Close |
|---|------|----------------|--------------|
| 1 | **CCCL instrument construction methodology** | The instrument file is pre-computed externally. Cannot verify the shift-share construction formula from repo artifacts alone. | Obtain the CCCL construction script or paper citation and verify the market-value weighting formula matches the thesis description. |
| 2 | **CCCL year = fyearq assumption** | `cccl_instrument.py:118-120` renames CCCL `year` to `fyearq_int`, assuming the CCCL instrument year is the Compustat fiscal year. If the CCCL instrument year is calendar year for some firms, this misaligns for non-December FYE firms. | Verify with the CCCL data provider whether `year` in the instrument file is fiscal year or calendar year. |
| 3 | **Finance sample pre-trends** | The 4 significant H6 results are all in the Finance sample. Finance/Uncertainty_Gap shows significant lead1 (p=0.0412). Do the significant base results survive after conditioning on clean pre-trends? | Run the base regression on the subsample where lead1 and lead2 are both insignificant. |
| 4 | **Moulton correction applicability** | H6 uses firm-clustered SEs. The CCCL instrument varies at the firm-year level but the data is call-level (~3.9 calls per firm-year). Firm clustering addresses within-firm correlation but the instrument's true variation is at the industry-year level (FF48 × year). | Consider two-way clustering (firm × year) or industry-year clustering to account for the instrument's group-level variation. |
| 5 | **Effective sample for Finance significance** | Finance sample has 436 firms and 15,662 obs. With CCCL_lag 46.9% zeros, only ~8,300 non-zero-instrument observations drive the coefficient. Is this sufficient for reliable inference? | Report effective sample size (non-zero CCCL_lag) for Finance and test robustness to excluding zero-instrument observations. |

---

## Summary

The H6 CCCL suite is **mechanically sound** in its panel construction (zero row-delta, unique primary keys, correct merge logic, proper lag construction). The code is well-structured with appropriate hard-fail guards. Cross-consistency between diagnostics CSV, regression text outputs, and LaTeX table is excellent.

**Three substantive issues require attention:**

1. **Pre-trends violations** (MAJOR) — Multiple significant lead coefficients undermine the causal interpretation. The provenance doc incorrectly states no pre-trends detected.
2. **within_r2 bug** (MAJOR) — Index alignment error produces all-NaN within-R² values. Simple fix available.
3. **README inconsistency** (MAJOR) — Reports "0/6 significant" when actual results show 4/21 significant (Finance sample).

**Two minor data quality issues:**

4. **Stale merge_asof matches** (MINOR) — 78 rows with wrong fyearq; negligible impact on results.
5. **Heavy zero-inflation in mkvalt weighting** (MINOR) — Methodological choice that may attenuate effects.

The most critical finding is the pre-trends violations, which affect the scientific validity of the H6 causal claims, not just the implementation correctness.
