# Adversarial Audit Report — Suite H14 (Bid-Ask Spread Change)

**Auditor:** Claude Sonnet 4.6 (hostile adversarial mode)
**Date:** 2026-04-01
**Suite:** H14 — Speech Uncertainty and Bid-Ask Spread Changes
**Provenance doc:** `docs/provenance/H14.md`
**Runner:** `src/f1d/econometric/run_h14_bidask_spread.py`
**Panel builder:** `src/f1d/variables/build_h14_bidask_spread_panel.py`

---

## AUDIT SUMMARY

| Category | Total Checks | Passed | Failed | Score |
|----------|-------------|--------|--------|-------|
| Structural Completeness (Phase 1) | 26 | 26 | 0 | 100% |
| Suite Identity (Phase 2) | 10 | 9 | 1 | 90% |
| Model Specification (Phase 3) | 7 | 6 | 1 | 86% |
| Spec Register (Phase 4) | 4 | 4 | 0 | 100% |
| Sample Construction (Phase 5) | 3 | 2 | 1 | 67% |
| Variable Dictionary (Phase 6) | 20 | 19 | 1 | 95% |
| Pipeline/Outputs/Treatment (Phase 7) | 9 | 9 | 0 | 100% |
| Table Generator Entry (Phase 8) | 5 | 4 | 1 | 80% |
| Model-Family Addendum (Phase 9) | 6 | 6 | 0 | 100% |
| Quality Gates (Phase 10) | 10 | 9 | 1 | 90% |
| Cross-Reference Consistency (Phase 11) | 8 | 7 | 1 | 88% |
| **TOTAL** | **108** | **101** | **7** | **94%** |

---

## VERDICT

**FAIL — INACCURATE**

The document is structurally complete and mostly accurate. However, **3 factual errors** and **4 minor inaccuracies** were identified through code verification. The most significant error is an incorrect TobinsQ formula in Section B4 (the formula omits the `clip(lower=0)` and special null-handling that the engine code implements). A line-number error in Section I references the wrong line for `generate_table()`. These errors are correctible without structural changes.

---

## PHASE 1: STRUCTURAL COMPLETENESS

**Method:** Compare each required section (A through L) from the creation prompt against the actual document.

| Section | Required | Present | Complete | Notes |
|---------|----------|---------|----------|-------|
| A. Suite Identity | Yes | Yes | Yes | YAML block present, all fields populated |
| B. Model Specification | Yes | Yes | Yes | All subsections present |
| B1. Regression Equation | Yes | Yes | Yes | LaTeX equation with all 4 IVs |
| B2. Dependent Variable(s) | Yes | Yes | Yes | Table present, DSPREAD construction detailed |
| B3. Independent Variable(s) | Yes | Yes | Yes | All 4 IVs in table with source |
| B4. Control Variables | Yes | Yes | Yes | Two tables (Base 8, Extended +4) |
| B5. Fixed Effects | Yes | Yes | Yes | 4-row table with applicable cols |
| B6. Standard Errors | Yes | Yes | Yes | cov_type, cluster_entity documented |
| B7. Hypothesis Test | Yes | Yes | Yes | One-tailed p_one formula documented |
| C. Spec Register | Yes | Yes | Yes | 6-row table matching MODEL_SPECS |
| D. Sample Construction | Yes | Yes | Yes | D1, D2, D3 all present |
| D1. Population | Yes | Yes | Yes | 112,968 calls, 2002-2018 stated |
| D2. Exclusion Criteria | Yes | Yes | Yes | Attrition cascade with N values |
| D3. Sample Counts per Spec | Yes | Yes | Yes | Variation documented |
| E. Variable Dictionary | Yes | Yes | Yes | All 20 variables including FE columns |
| F. Data Pipeline | Yes | Yes | Yes | F1, F2, F3 all present |
| F1. Dependency Chain | Yes | Yes | Yes | 7-step chain |
| F2. Data Engines | Yes | Yes | Yes | 5 engines listed |
| F3. Merge Operations | Yes | Yes | Yes | 16+2 merges documented |
| G. Outputs | Yes | Yes | Yes | G1, G2, G3 present |
| G1. Stage 3 Outputs | Yes | Yes | Yes | 4 files listed |
| G2. Stage 4 Outputs | Yes | Yes | Yes | 9 files listed |
| G3. Summary Statistics | Yes | Yes | Yes | 17 variables listed with metrics |
| H. Outlier/Missing Treatment | Yes | Yes | Yes | H1, H2, H3 present |
| I. generate_all_tables Entry | Yes | Yes | Yes | Python dict present, verification table |
| J. Reproduction Commands | Yes | Yes | Yes | 3 commands |
| K. Model-Family Addendum | Yes | Yes | Yes | K1 filled, K2-K6 marked N/A |
| L. Known Issues | Yes | Yes | Yes | 9 known issues documented |

**Phase 1 Result: PASS — All 26 structural checks passed.**

---

## PHASE 2: FACTUAL ACCURACY — SECTION A (Suite Identity)

**Method:** Verify each YAML field against code.

### A-1. Suite ID
- **Claim:** H14
- **Verification:** Trivial — matches runner filename, generate_all_tables.py entry
- **Result:** PASS

### A-2. Title
- **Claim:** "Speech Uncertainty and Bid-Ask Spread Changes"
- **Verification:** Runner `_save_latex_table` (line 430): `r"\caption{Speech Uncertainty and Bid-Ask Spread Changes}"`. Also generate_all_tables.py: `"caption": "H14: Speech Uncertainty and Bid-Ask Spread Changes"`. Match.
- **Result:** PASS

### A-3. Hypothesis
- **Claim:** "Higher earnings-call language uncertainty is associated with a larger increase in bid-ask spreads around the conference call (lower market liquidity)."
- **Verification:** Runner docstring (line 36): `H14: beta(uncertainty_var) > 0 — higher uncertainty -> wider spreads.` Builder docstring (line 24-26): matches same description. The provenance doc's longer form is consistent.
- **Result:** PASS

### A-4. Direction (tail test)
- **Claim:** "one-tailed beta > 0"
- **Verification:** Runner line 364: `p_one = p_two / 2 if beta > 0 else 1 - p_two / 2`. Runner docstring line 35: `Hypothesis Test (one-tailed):`. generate_all_tables.py: `"tail": "one", "hyp_dir": ">"`. All consistent.
- **Result:** PASS

### A-5. Model Family
- **Claim:** "PanelOLS"
- **Verification:** Runner line 71: `from linearmodels.panel import PanelOLS`. Runner lines 321-334: PanelOLS constructor and from_formula calls.
- **Result:** PASS

### A-6. Estimator
- **Claim:** "linearmodels.panel.PanelOLS"
- **Verification:** Runner import (line 71): `from linearmodels.panel import PanelOLS`. Exact class confirmed.
- **Result:** PASS

### A-7. Unit of Observation
- **Claim:** "call-level (individual earnings call)"
- **Verification:** Builder docstring (line 22): "Unit of observation: the individual earnings call (file_name)." Runner docstring (line 4): "CALL-LEVEL panel". `file_name` is the merge key throughout.
- **Result:** PASS

### A-8. Panel Index
- **Claim:** "(gvkey, cal_yr) for cols 1-4; (gvkey, cal_yr_qtr) for cols 5-6"
- **Verification:**
  - Runner line 304: `time_col = "cal_yr_qtr" if fe_type.endswith("_yq") else "cal_yr"`.
  - Runner line 314: `df_panel = df_prepared.set_index(["gvkey", time_col])`.
  - MODEL_SPECS cols 5-6 have `fe: "industry_yq"` and `fe: "firm_yq"` which endswith("_yq") = True → cal_yr_qtr.
  - Cols 1-4 use `cal_yr`. Split is correct.
- **Result:** PASS

### A-9. Columns
- **Claim:** "6"
- **Verification:** Runner MODEL_SPECS list (lines 115-123): 6 entries. `len(MODEL_SPECS) = 6`. CONFIRMED.
- **Note:** Runner module-level docstring (line 11) says "4 columns in one table" — stale. Provenance doc correctly follows code-is-truth (6 columns), documented as Known Issue #9.
- **Result:** PASS

### A-10. Runner and Panel Builder paths
- **Claim:** `src/f1d/econometric/run_h14_bidask_spread.py` and `src/f1d/variables/build_h14_bidask_spread_panel.py`
- **Verification:** Both files confirmed to exist on disk.
- **Result:** PASS

**Phase 2 Result: 9 explicit checks PASS. One anomaly (stale docstring) correctly documented in doc.**

---

## PHASE 3: FACTUAL ACCURACY — SECTION B (Model Specification)

### B1-CHECK: Regression Equation

- **Claim:** `DSPREAD_{i,t} = beta_1*CEO_QA_Unc + beta_2*CEO_Pres_Unc + beta_3*Mgr_QA_Unc + beta_4*Mgr_Pres_Unc + gamma'*Controls + alpha_i + delta_t + epsilon_{i,t}`
- **Verification:** Runner KEY_IVS (lines 88-92): 4 IVs in stated order. Runner line 301: `exog = KEY_IVS + controls`. All 4 IVs enter simultaneously. Entity FE (alpha_i) is either firm or industry depending on spec. Time FE (delta_t) is always present. Formula is correct.
- **Result:** PASS

### B2-CHECK: Dependent Variable

- **Claim:** DSPREAD = `mean(2*(ASK-BID)/(ASK+BID) for [+1,+3]) - mean(2*(ASK-BID)/(ASK+BID) for [-3,-1])` using closing quotes
- **Verification (builder `bidask_spread_change.py`):**
  - Line 346-348: `spread_closing = 2*(ASK-BID)/(ASK+BID)` — CONFIRMED
  - Lines 416-429: `delta_spread_closing = post_call_spread_closing - pre_call_spread_closing` — CONFIRMED
  - Lines 386-387: `pre_window = merged[pre_mask & (merged["pre_rank"] <= w)]` where `w=3` — 3 trading days — CONFIRMED
  - Lines 300-302: `min_pre = max(1, w-1) = 2` — minimum 2 days required — CONFIRMED
  - Panel builder lines 180-183: `rename({"delta_spread_closing": "DSPREAD"})` — CONFIRMED
  - Doc says "line 181 of panel builder" for the rename — line 181 is the inner dict entry `"delta_spread_closing": "DSPREAD"`. Minor line-number imprecision; functionally correct.
- **Result:** PASS

### B3-CHECK: Independent Variables

- **Claim:** 4 IVs: CEO_QA_Uncertainty_pct, CEO_Pres_Uncertainty_pct, Manager_QA_Uncertainty_pct, Manager_Pres_Uncertainty_pct
- **Verification:** Runner KEY_IVS (lines 88-92): exact 4 variable names match. Panel builder imports (lines 56-59): CEOQAUncertaintyBuilder, CEOPresUncertaintyBuilder, ManagerQAUncertaintyBuilder, ManagerPresUncertaintyBuilder — all confirmed. Bounded [0,100]: not in any winsorize_cols list — CONFIRMED.
- **Result:** PASS

### B4-CHECK: Control Variables

**BASE_CONTROLS verification (runner lines 97-106):**
```
Size, TobinsQ, ROA, BookLev, CapexAt, DividendPayer, OCF_Volatility, PreCallSpread
```
Doc B4 Base Controls table: same 8 variables — CONFIRMED.

**EXTENDED_CONTROLS (runner lines 108-113):**
```
BASE + StockPrice, Turnover, Volatility, AbsSurpDec
```
Doc B4 Extended table: same 4 additions — CONFIRMED.

**FORMULA ERROR — TobinsQ in B4:**

- **Doc B4 claims:** `(cshoq * prccq + dlcq + dlttq) / atq (missing debt treated as zero)`
- **Actual code (`_compustat_engine.py` lines 987-997):**
  ```python
  mktcap = comp["cshoq"] * comp["prccq"]
  debt_c = comp["dlcq"].clip(lower=0).fillna(0)
  debt_t = comp["dlttq"].clip(lower=0).fillna(0)
  debt_book = np.where(
      comp["dlcq"].isna() & comp["dlttq"].isna(), np.nan, debt_c + debt_t
  )
  comp["TobinsQ"] = np.where(
      comp["atq"].notna() & (comp["atq"] > 0) & mktcap.notna(),
      (mktcap + debt_book) / comp["atq"],
      np.nan,
  )
  ```
- **B4 formula is wrong:** It omits (1) `clip(lower=0)` applied to both debt components, (2) the special null rule — if BOTH dlcq AND dlttq are NaN, debt_book = NaN (not 0), making TobinsQ = NaN, and (3) the condition that cshoq*prccq must be non-null.
- Section E (Variable Dictionary) is closer: `(cshoq*prccq + dlcq.clip(0).fillna(0) + dlttq.clip(0).fillna(0)) / atq` — but still omits the both-null edge case and mktcap null condition.
- **Result: FAIL**

**Other formula verifications:**
- BookLev: Engine line 948: `(dlcq.fillna(0) + dlttq.fillna(0)) / atq` — Doc says same. PASS.
- ROA: Engine lines 960-969: `iby_annual(Q4) / ((atq_annual + atq_annual_lag1) / 2)` — Doc says same. PASS.
- Size: Engine line 943: `ln(atq) for atq > 0 else NaN` — Doc says same. PASS.
- CapexAt: Engine lines 999-1003: `capxy_annual(Q4) / atq_annual_lag1` — Doc says same. PASS.
- DividendPayer: Binary; skip_winsorize excludes it. Confirmed from engine CRITICAL-2 fix. PASS.
- OCF_Volatility: "rolling 5-year std (min 3 yrs) of oancfy / atq_{t-1}" — Builder docstring + changelog. PASS.
- PreCallSpread: `pre_call_spread_closing` renamed in panel builder line 182. Mean of closing spread in [-3,-1] window. PASS.
- StockPrice: CRSPEngine line 92: `crsp["PRC"] = crsp["PRC"].abs()`. Builder renames PRC→StockPrice. PASS.
- Turnover: TurnoverBuilder lines 231-233: `VOL / (SHROUT * 1000)`. PASS.
- Volatility: `std(daily RET) * sqrt(252) * 100`, min 10 days. PASS.
- AbsSurpDec: Panel builder line 187: `SurpDec.abs()`. EarningsSurpriseBuilder `_rank_surprises` confirms [-5,+5] scale. PASS.

### B5-CHECK: Fixed Effects

- Industry FE (cols 1,3,5): `entity_effects=False, time_effects=True, other_effects=df_panel["ff12_code"]` — Runner lines 323-329. CONFIRMED.
- Firm FE (cols 2,4,6): `EntityEffects + TimeEffects` in formula string — Runner line 333. CONFIRMED.
- Cal Year (cols 1-4): `time_col = "cal_yr"` for non-_yq specs — Runner line 304. CONFIRMED.
- Cal Yr-Qtr (cols 5-6): `time_col = "cal_yr_qtr"` for _yq specs — Runner line 304. CONFIRMED.
- `build_cal_yr_qtr_index()`: `cal_yr = start_date.dt.year`, `cal_yr_qtr = cal_yr * 10 + cal_qtr` — panel_utils.py lines 215-217. CONFIRMED.
- **Result:** PASS

### B6-CHECK: Standard Errors

- **Claim:** `cov_type="clustered"`, `cluster_entity=True` (firm-level), lines 330 and 335.
- **Verification:** Runner line 330: `model_obj.fit(cov_type="clustered", cluster_entity=True)` (industry specs). Runner line 335: same (firm specs). CONFIRMED.
- **Result:** PASS

### B7-CHECK: Hypothesis Test

- **Claim:** `p_one = p_two / 2 if beta > 0 else 1 - p_two / 2` (runner line 364)
- **Verification:** Runner line 364: exact code match. CONFIRMED.
- **Claim:** `_sig_stars` at lines 384-394
- **Verification:** `_sig_stars` defined at lines 384-394: `if p < 0.01: "***"; if p < 0.05: "**"; if p < 0.10: "*"`. CONFIRMED.
- **Result:** PASS

**Phase 3 Result: 6/7 PASS. One FAIL: B4 TobinsQ formula is simplified and incorrect relative to code.**

---

## PHASE 4: FACTUAL ACCURACY — SECTION C (Spec Register)

**Method:** Compare every row against MODEL_SPECS in runner (lines 115-123).

**Runner MODEL_SPECS:**
```python
{"col": 1, "dv": "DSPREAD", "fe": "industry",    "controls": "base"},
{"col": 2, "dv": "DSPREAD", "fe": "firm",         "controls": "base"},
{"col": 3, "dv": "DSPREAD", "fe": "industry",    "controls": "extended"},
{"col": 4, "dv": "DSPREAD", "fe": "firm",         "controls": "extended"},
{"col": 5, "dv": "DSPREAD", "fe": "industry_yq", "controls": "extended"},
{"col": 6, "dv": "DSPREAD", "fe": "firm_yq",     "controls": "extended"},
```

**Row-by-row verification:**

| Doc Row | DV | Entity FE | Time FE | Controls | Code Match |
|---------|-----|-----------|---------|----------|-----------|
| Col 1 | DSPREAD | Industry (FF12) | Cal Year | Base (8) | CONFIRMED: fe="industry", controls="base" |
| Col 2 | DSPREAD | Firm | Cal Year | Base (8) | CONFIRMED: fe="firm", controls="base" |
| Col 3 | DSPREAD | Industry (FF12) | Cal Year | Extended (12) | CONFIRMED: fe="industry", controls="extended" |
| Col 4 | DSPREAD | Firm | Cal Year | Extended (12) | CONFIRMED: fe="firm", controls="extended" |
| Col 5 | DSPREAD | Industry (FF12) | Cal Yr-Qtr | Extended (12) | CONFIRMED: fe="industry_yq"→time_col=cal_yr_qtr |
| Col 6 | DSPREAD | Firm | Cal Yr-Qtr | Extended (12) | CONFIRMED: fe="firm_yq"→time_col=cal_yr_qtr |

- Row count: 6 — matches len(MODEL_SPECS) = 6. CONFIRMED.
- "Extended (12)": BASE_CONTROLS=8 + 4 extended = 12. CONFIRMED.
- Doc source note "runner lines 115-123": Lines 115-123 span the MODEL_SPECS list. CONFIRMED.

**Phase 4 Result: 4/4 PASS.**

---

## PHASE 5: FACTUAL ACCURACY — SECTION D (Sample Construction)

### D1-CHECK: Population

- **Claim:** Starting from `master_sample_manifest.parquet`, 2002-2018, 112,968 total calls.
- **Verification:** Project scope: 112,968 calls, 2,429 firms, 2002-2018 (per project_thesis_scope.md). Runner line 189: loads from manifest. Panel builder lines 324-328: year range from config. Consistent with project scope.
- **Result:** PASS

### D2-CHECK: Exclusion Criteria

**Doc's 5-step cascade:**

| Step | Filter | N |
|------|--------|---|
| 1 | Full manifest | 112,968 |
| 2 | Main sample (excl FF12=8,11) | 88,205 |
| 3 | DV non-missing | 87,119 |
| 4 | Complete case | -- |
| 5 | Min calls per firm (>=5) | 57,044 |

**Runner's actual attrition output (lines 752-759):**
```python
attrition_stages = [
    ("Master manifest (full panel)", full_panel_n),
    ("Main sample filter (excl Finance/Utility)", main_panel_n),
    ("DSPREAD non-null", panel["DSPREAD"].notna().sum()),
    ("After complete-case + min-calls (col 1)", first_meta.get("n_obs", 0)),
]
```

**Issues:**
1. The runner generates EXACTLY 4 stages in `sample_attrition.csv` / `sample_attrition.tex`. The doc shows 5 conceptual steps, with steps 4+5 combined (step 4 N = "--"). The doc's note acknowledges this: "Steps 4 and 5 are applied jointly in the runner."
2. Stage 3 "DSPREAD non-null" uses `panel["DSPREAD"].notna().sum()` computed on the post-main-sample-filter panel. Doc's Step 3 N=87,119 is for this count. Correct interpretation.
3. The actual CSV output will have 4 rows, not matching the 5-row D2 table. A reader checking the file will see different structure.
4. The doc says "runner line 753-759" — correct range for the attrition_stages list (lines 752-759 in runner).
- **Result: PASS WITH CAVEAT** — Conceptually correct but actual output file has 4 stages. Doc's note is there but imprecise.

### D3-CHECK: Sample Counts per Spec

- **Claim:** N varies across specs due to different control sets.
- **Verification:** `prepare_regression_data` called per spec (runner line 735). Extended controls introduce additional missingness. CONFIRMED.
- **Result:** PASS

**Phase 5 Result: 2/3 PASS. D2 has caveat about 4-stage vs 5-step representation.**

---

## PHASE 6: FACTUAL ACCURACY — SECTION E (Variable Dictionary)

**Method:** Verify all 20 variable rows against builder and engine code.

### DSPREAD (DV)
- Formula: closing bid-ask spread change — builder confirmed. PASS.
- Winsorized 1%/99% pooled at panel builder line 202. CONFIRMED. PASS.
- Timing: Event-window. PASS.

### IV Variables (4)
- CEO_QA_Uncertainty_pct: LinguisticEngine, bounded [0,100]. CONFIRMED. PASS.
- CEO_Pres_Uncertainty_pct: same pattern. PASS.
- Manager_QA_Uncertainty_pct: same pattern. PASS.
- Manager_Pres_Uncertainty_pct: same pattern. PASS.

### Size
- Formula: `ln(atq) for atq > 0; else NaN` — Engine line 943: `np.where(comp["atq"] > 0, np.log(comp["atq"]), np.nan)`. CONFIRMED. PASS.
- Winsorized "by fiscal year": engine groups by `fyearq` (fiscal year integer per code comment line 1226). CONFIRMED. PASS.

### TobinsQ
- Formula in E: `(cshoq*prccq + dlcq.clip(0).fillna(0) + dlttq.clip(0).fillna(0)) / atq`
- **Code (`_compustat_engine.py` lines 987-997):**
  - `debt_c = dlcq.clip(lower=0).fillna(0)`
  - `debt_t = dlttq.clip(lower=0).fillna(0)`
  - `debt_book = np.where(dlcq.isna() & dlttq.isna(), np.nan, debt_c + debt_t)` ← both-null → NaN
  - `TobinsQ = np.where(atq.notna() & atq > 0 & mktcap.notna(), (mktcap + debt_book) / atq, np.nan)` ← also requires mktcap non-null
- **E formula misses:**
  1. When BOTH dlcq AND dlttq are NaN, `debt_book` is NaN (not 0), making TobinsQ = NaN. The E formula implies independently fillna(0) on each, giving 0+0=0 when both missing.
  2. The condition `mktcap.notna()` (cshoq*prccq non-null) is also required.
- **Result: FAIL** (minor — main formula logic is captured, but edge case documentation is incomplete)

### ROA
- Formula: `iby_annual(Q4) / ((atq_annual + atq_annual_lag1) / 2)` — Engine lines 959-969. CONFIRMED. PASS.

### BookLev
- Formula: `(dlcq.fillna(0) + dlttq.fillna(0)) / atq` — Engine line 948. CONFIRMED. PASS.

### CapexAt
- Formula: `capxy_annual(Q4) / atq_annual_lag1` — Engine lines 999-1003. CONFIRMED. PASS.

### DividendPayer
- Binary; 1 if dvy_annual(Q4) > 0, else 0. Excluded from winsorization. CONFIRMED. PASS.

### OCF_Volatility
- Formula: rolling 5-year std (min 3 yrs) of oancfy/atq_{t-1}. Builder docstring + engine changelog. CONFIRMED. PASS.

### PreCallSpread
- Formula: mean(closing spread in [-3,-1] window). Panel builder line 182 rename. CONFIRMED. PASS.

### StockPrice
- Formula: abs(PRC). CRSPEngine line 92: `crsp["PRC"] = crsp["PRC"].abs()`. StockPriceBuilder renames PRC→StockPrice. CONFIRMED. PASS.
- Doc says "applied in CRSPEngine line 92" — CONFIRMED.

### Turnover
- Formula: `VOL / (SHROUT * 1000)`. TurnoverBuilder lines 231-233. CONFIRMED. PASS.

### Volatility
- Formula: `std(daily RET) * sqrt(252) * 100`, inter-call window, min 10 days. VolatilityBuilder uses `engine.get_data()`. CONFIRMED. PASS.
- Winsorized per calendar year at CRSPEngine level: CRSPEngine lines 444-447: `winsorize_by_year(..., year_col="year")` where `year = start_date.dt.year`. CONFIRMED. PASS.

### AbsSurpDec
- Formula: `abs(SurpDec)` where SurpDec is ranked ACTUAL-MEANEST into [-5,+5] within quarter. Panel builder line 187. EarningsSurpriseBuilder `_rank_surprises` function. IbesEngine `surprise_raw = actual - meanest`. CONFIRMED. PASS.

### FE Columns (gvkey, ff12_code, cal_yr, cal_yr_qtr)
- All four documented with correct sources and formulas. CONFIRMED. PASS.

**Phase 6 Result: 19/20 PASS. One FAIL: TobinsQ in E omits both-null debt edge case and mktcap null condition.**

---

## PHASE 7: FACTUAL ACCURACY — SECTIONS F, G, H

### F-CHECK: Data Pipeline

**F1. Dependency Chain (7 steps):**
1. Raw inputs: CRSP_DSF, CCM, CompustatNA, linguistic, manifest, IBES — CONFIRMED from engine source files.
2. Engine loading: 4 engines (CRSPEngine get_raw, CRSPEngine get_data, CompustatEngine, LinguisticEngine, IbesEngine). CONFIRMED.
3. Panel builder: 16 merges, rename delta_spread_closing → DSPREAD, attach fyearq_int, winsorize 5 cols. CONFIRMED.
4. Runner loading: loads parquet, builds cal_yr_qtr index via `build_cal_yr_qtr_index()`. CONFIRMED (runner lines 217-218).
5. Sample filtering: main sample filter then per-spec: DV non-null → complete case → min calls. CONFIRMED.
6. Regression: PanelOLS, 6 specs, one-tailed p-values. CONFIRMED.
7. Table generation: runner writes its own LaTeX, also in generate_all_tables.py. CONFIRMED.
- **Result:** PASS

**F2. Data Engines:**
- 5 engines listed with correct variables. All confirmed against builder source files.
- CRSPEngine (get_raw) → DSPREAD, PreCallSpread, StockPrice, Turnover. CONFIRMED.
- CRSPEngine (get_data) → Volatility. CONFIRMED (VolatilityBuilder line 38).
- CompustatEngine → 7 Compustat controls. CONFIRMED.
- LinguisticEngine → 4 IVs. CONFIRMED.
- IbesEngine → SurpDec/AbsSurpDec. CONFIRMED.
- **Result:** PASS

**F3. Merge Operations:**
- 16 panel builder merges documented. Panel builder loop at lines 153-169: iterates builder dict (17 entries - 1 manifest = 16 merges), all left on file_name, zero row-delta enforced. Order matches builder dict. CONFIRMED.
- 2 internal BidAsk builder merges (manifest→CCM, year_calls→year_crsp). CONFIRMED (builder lines 185, 309).
- **Result:** PASS

### G-CHECK: Outputs

**G1. Stage 3 (4 files):**
- `h14_bidask_spread_panel.parquet`: panel builder line 223. CONFIRMED.
- `summary_stats.csv`: panel builder line 230. CONFIRMED.
- `run_manifest.json`: panel builder `generate_manifest()` call lines 234-244. CONFIRMED.
- `report_step3_h14.md`: panel builder line 294. CONFIRMED.
- **Result:** PASS

**G2. Stage 4 (9 files):**
- `h14_bidask_spread_table.tex`: runner line 532. CONFIRMED.
- `model_diagnostics.csv`: runner lines 569-570. CONFIRMED.
- `summary_stats.csv`: runner line 720 (argument to make_summary_stats_table). CONFIRMED.
- `summary_stats.tex`: runner line 721. CONFIRMED.
- `sample_attrition.csv` + `sample_attrition.tex`: runner lines 753-760 call `generate_attrition_table()`. `attrition_table.py` lines 47, 52 write both files. CONFIRMED.
- `regression_results_col{1-6}.txt`: runner lines 554-565, iterates over all 6 MODEL_SPECS. CONFIRMED.
- `report_step4_H14.md`: runner line 652. CONFIRMED.
- `run_manifest.json`: runner lines 762-772. CONFIRMED.
- **Result:** PASS

**G3. Summary Statistics:**
- SUMMARY_STATS_VARS (runner lines 133-150): 17 variables. All 17 listed in doc's G3 table. Labels match. CONFIRMED.
- **Result:** PASS

### H-CHECK: Outlier/Missing Treatment

**H1. Winsorization:**
- Compustat (Size, TobinsQ, ROA, BookLev, CapexAt, OCF_Volatility): `_winsorize_by_year(comp[col], comp["fyearq"])` — engine lines 1229-1232. DividendPayer excluded (skip_winsorize). CONFIRMED.
- Volatility: CRSPEngine lines 444-447: `winsorize_by_year(result_with_year, CRSP_RETURN_COLS, year_col="year")`. Calendar year. CONFIRMED.
- DSPREAD, PreCallSpread, StockPrice, Turnover, AbsSurpDec: `winsorize_pooled()` at panel builder line 202. CONFIRMED.
- Linguistic IVs: not in any winsorize_cols list. CONFIRMED.
- **Result:** PASS

**H2. Missing Data Policy:**
- `df.replace([np.inf, -np.inf], np.nan)`: runner line 252. CONFIRMED.
- Complete-case deletion: runner lines 263-264. CONFIRMED.
- BidAsk min 2 days: builder `_process_year_calls` lines 300-302, 404-409. CONFIRMED.
- **Result:** PASS

**H3. Transformations:**
- Size: ln(atq). CONFIRMED.
- AbsSurpDec: abs(SurpDec). Panel builder line 187. CONFIRMED.
- StockPrice: abs(PRC). CRSPEngine line 92. CONFIRMED.
- No centering, z-scoring, scaling. No evidence in code. CONFIRMED.
- **Result:** PASS

**Phase 7 Result: 9/9 PASS.**

---

## PHASE 8: FACTUAL ACCURACY — SECTION I (Table Generator Entry)

**Actual entry from `outputs/generate_all_tables.py` (lines 289-301):**
```python
# ── H14 ──
{
    "id": "H14",
    "dir": "h14_bidask_spread/2026-03-27_095017",
    "caption": "H14: Speech Uncertainty and Bid-Ask Spread Changes",
    "label": "tab:h14",
    "cols": 6,
    "dvs": [
        ("DSPREAD", 6),
    ],
    "tail": "one",
    "hyp_dir": ">",
},
```

**Field-by-field comparison:**

| Field | Doc Claims | Actual Code | Match? |
|-------|-----------|-------------|--------|
| id | "H14" | "H14" | YES |
| dir | "h14_bidask_spread/2026-03-27_095017" | same | YES |
| caption | "H14: Speech Uncertainty and Bid-Ask Spread Changes" | same | YES |
| label | "tab:h14" | "tab:h14" | YES |
| cols | 6 | 6 | YES |
| dvs | [("DSPREAD", 6)] | same | YES |
| tail | "one" | "one" | YES |
| hyp_dir | ">" | ">" | YES |
| key_vars | (absent) | (absent) | YES |

**Line number error in Section I note:**
- **Doc claims:** "falls through to `generate_table()` (standard 4-IV suite handler) in the main loop at **line 1234**"
- **Actual code:** Line 1234: `tex = generate_interaction_table(suite)` (for `type == "interaction"` branch). Line **1241**: `tex = generate_table(suite)` (the `else` clause).
- **ERROR:** Line number is wrong. 1234 is for the interaction handler, not generate_table(). The correct line is 1241.
- The functional description is correct (H14 has no "type" key, falls to else → generate_table()).
- **Result: FAIL** (wrong line number in note)

**Phase 8 Result: 4/5 PASS. One FAIL: line number for generate_table() is 1241, not 1234.**

---

## PHASE 9: FACTUAL ACCURACY — SECTION K (Model-Family Addendum)

### K1. PanelOLS Specifics

**Industry FE specs (cols 1, 3, 5):**
- `entity_effects=False`: runner line 324. CONFIRMED.
- `time_effects=True`: runner line 325. CONFIRMED.
- `other_effects=df_panel["ff12_code"]`: runner lines 320-328. CONFIRMED.
- `drop_absorbed=True`: runner line 327. CONFIRMED.
- `check_rank=False`: runner line 328. CONFIRMED.
- SE: runner line 330: `model_obj.fit(cov_type="clustered", cluster_entity=True)`. CONFIRMED.
- Doc says "runner lines 321-329" — the PanelOLS constructor spans lines 321-329. CONFIRMED.

**Firm FE specs (cols 2, 4, 6):**
- Formula: `f"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"` — runner line 333. CONFIRMED.
- `drop_absorbed=True`: runner line 334 (`PanelOLS.from_formula(..., drop_absorbed=True)`). CONFIRMED.
- SE: runner line 335. CONFIRMED.

**Time index construction:**
- Cols 1-4: `time_col = "cal_yr"`, `set_index(["gvkey", "cal_yr"])` — runner lines 304, 314. CONFIRMED.
- Cols 5-6: `time_col = "cal_yr_qtr"`, `set_index(["gvkey", "cal_yr_qtr"])` — runner lines 304, 314. CONFIRMED.

**R-squared:**
- `model.rsquared` — runner line 342, 353. CONFIRMED.
- Adj R-squared: `1 - (1 - model.rsquared) * (model.nobs - 1) / model.df_resid` — runner line 354 (in meta dict). CONFIRMED.

**K2-K6:** All marked N/A. Suite is PanelOLS — correct.

**Phase 9 Result: 6/6 PASS.**

---

## PHASE 10: QUALITY GATE CHECKLIST

| # | Quality Gate | Met? | Evidence |
|---|-------------|------|----------|
| 1 | Every variable in every regression spec appears in Variable Dictionary with explicit formula and source engine | MOSTLY | All variables present. TobinsQ formula in E misses both-null edge case and mktcap null condition. |
| 2 | The model equation matches what the code actually estimates | YES | B1 equation verified: 4 IVs + controls + entity FE + time FE. |
| 3 | The specification register accounts for every model column | YES | 6-row spec register matches 6 MODEL_SPECS exactly. |
| 4 | The attrition cascade has row counts for each filter step | PARTIAL | D2 Step 4 N = "--" (no count for complete-case alone). Actual output CSV has 4 stages not 5. |
| 5 | The tail test direction matches between runner code and generate_all_tables.py | YES | Runner: `p_two/2 if beta > 0`. GAT: `"tail": "one", "hyp_dir": ">"`. |
| 6 | The FE specification matches between docstring, code, and this document | YES | B5, C, K1 all consistent with runner code. |
| 7 | Every merge in the panel builder is documented with join keys and type | YES | F3: 16 panel builder merges + 2 internal BidAsk builder merges. All verified. |
| 8 | The output file list matches what the runner actually writes | YES | G2: 9 files listed; all confirmed against runner write operations. |
| 9 | The model-family addendum is filled for the correct family only | YES | K1 (PanelOLS) filled; K2-K6 = N/A. |
| 10 | Any claim marked [UNVERIFIED] has an explanation of what blocks verification | YES | No [UNVERIFIED] markers in doc. All claims verified or flagged as known issues. |

**Phase 10 Result: 9/10 PASS. Quality gate #4 partially met.**

---

## PHASE 11: CROSS-REFERENCE CONSISTENCY

### Check 1: DVs in B2 match DVs in C
- B2: DSPREAD. C: all 6 rows = DSPREAD. PASS.

### Check 2: DVs in C match DVs in I
- C: DSPREAD across all 6 cols. I: `"dvs": [("DSPREAD", 6)]`. PASS.

### Check 3: Controls in B4 match variables in E
- B4 Base (8) + Extended (+4) = 12 controls. All 12 appear in E with formulas. PASS.

### Check 4: Column count in A matches rows in C
- A: 6. C: 6 rows. PASS.

### Check 5: Column count in A matches "cols" in I
- A: 6. I: `"cols": 6`. PASS.

### Check 6: Tail direction in A matches B7 matches I
- A: "one-tailed beta > 0". B7: `p_two/2 if beta > 0`. I: `"tail": "one", "hyp_dir": ">"`. PASS.

### Check 7: FE in B5 matches C matches K
- B5 table: Industry (ff12_code), Firm (gvkey), Cal Year (cal_yr), Cal Yr-Qtr (cal_yr_qtr).
- C: cols 1,3,5 = Industry; 2,4,6 = Firm; 1-4 = Cal Year; 5-6 = Cal Yr-Qtr.
- K1: other_effects=ff12_code for industry, EntityEffects for firm, time_effects=True for both, cal_yr/cal_yr_qtr as time index.
- All consistent. PASS.

### Check 8: Panel index in A matches set_index in K
- A: "(gvkey, cal_yr) for cols 1-4; (gvkey, cal_yr_qtr) for cols 5-6"
- K1: "Cols 1-4: Panel index = (gvkey, cal_yr) ... (runner line 304, 314); Cols 5-6: (gvkey, cal_yr_qtr)"
- Code: runner line 314: `df_prepared.set_index(["gvkey", time_col])`. CONFIRMED. PASS.

**INTERNAL INCONSISTENCY DETECTED:**
- B4 TobinsQ formula: `(cshoq * prccq + dlcq + dlttq) / atq`
- E TobinsQ formula: `(cshoq*prccq + dlcq.clip(0).fillna(0) + dlttq.clip(0).fillna(0)) / atq`
- These describe the same variable with different precision. B4 is an oversimplification of E. A reader relying on B4 would have a wrong formula.
- **Result: FAIL** (internal B4 vs E TobinsQ inconsistency)

**Phase 11 Result: 7/8 PASS. One FAIL: B4 vs E TobinsQ formula inconsistency.**

---

## FAILURES (Detailed)

| Phase | Check | Provenance Doc Claims | Actual Code Says | Severity | Fix Required |
|-------|-------|----------------------|-----------------|----------|-------------|
| 3 / 11 | TobinsQ formula in Section B4 | `(cshoq * prccq + dlcq + dlttq) / atq (missing debt treated as zero)` | `(mktcap + debt_book) / atq` where `debt_c = dlcq.clip(lower=0).fillna(0)`, `debt_t = dlttq.clip(lower=0).fillna(0)`, `debt_book = np.where(dlcq.isna() & dlttq.isna(), np.nan, debt_c + debt_t)`; also requires `mktcap.notna()` | Medium — B4 formula omits clip(lower=0), the both-null-NaN rule, and mktcap non-null requirement | Update B4 formula |
| 6 | TobinsQ formula in Section E (Variable Dictionary) | `(cshoq*prccq + dlcq.clip(0).fillna(0) + dlttq.clip(0).fillna(0)) / atq` | Same as above — additionally, when both dlcq AND dlttq are NaN, debt_book = NaN (not 0), making TobinsQ = NaN; also requires mktcap non-null | Minor — E is better than B4 but still incomplete | Add both-null edge case note |
| 8 | generate_table() line number in Section I note | "in the main loop at **line 1234**" | `generate_table()` is at line **1241** (else clause). Line 1234 is `generate_interaction_table()` for type=="interaction" | Low — functional description correct, line number wrong | Fix line number to 1241 |
| 5 / 10 | D2 attrition cascade stages | 5-step conceptual cascade (step 4 N = "--") | Runner `generate_attrition_table()` writes 4-stage CSV/TEX. Steps 4+5 combined into one stage. | Low — note in doc partially covers; actual output file structure differs from doc | Clarify D2 note |

---

## CORRECTIONS REQUIRED

### Correction 1 — Section B4: TobinsQ formula

**Section:** B4 Control Variables, Base Controls table row for TobinsQ

**Current text:**
```
| TobinsQ | Tobin's Q | (cshoq * prccq + dlcq + dlttq) / atq | CompustatEngine: cshoq, prccq, dlcq, dlttq, atq |
```
Note in cell says "(missing debt treated as zero)" after the formula.

**Replace with:**
```
| TobinsQ | Tobin's Q | (cshoq * prccq + dlcq.clip(0).fillna(0) + dlttq.clip(0).fillna(0)) / atq; NaN when both dlcq and dlttq are NaN, or when cshoq*prccq is NaN | CompustatEngine: cshoq, prccq, dlcq, dlttq, atq |
```

**Code reference:** `src/f1d/shared/variables/_compustat_engine.py` lines 987-997:
```python
mktcap = comp["cshoq"] * comp["prccq"]
debt_c = comp["dlcq"].clip(lower=0).fillna(0)
debt_t = comp["dlttq"].clip(lower=0).fillna(0)
debt_book = np.where(comp["dlcq"].isna() & comp["dlttq"].isna(), np.nan, debt_c + debt_t)
comp["TobinsQ"] = np.where(
    comp["atq"].notna() & (comp["atq"] > 0) & mktcap.notna(),
    (mktcap + debt_book) / comp["atq"], np.nan,
)
```

---

### Correction 2 — Section E: TobinsQ formula (Variable Dictionary)

**Section:** E. Variable Dictionary, TobinsQ row

**Current text (Formula column):**
```
(cshoq*prccq + dlcq.clip(0).fillna(0) + dlttq.clip(0).fillna(0)) / atq
```

**Replace with:**
```
(cshoq*prccq + dlcq.clip(0).fillna(0) + dlttq.clip(0).fillna(0)) / atq; NaN if both dlcq and dlttq are simultaneously NaN (preserves null rather than treating as 0), or if cshoq*prccq is NaN
```

**Code reference:** `_compustat_engine.py` lines 990-992: `debt_book = np.where(comp["dlcq"].isna() & comp["dlttq"].isna(), np.nan, debt_c + debt_t)` and lines 993-996 requiring `mktcap.notna()`.

---

### Correction 3 — Section I: Wrong line number for generate_table()

**Section:** I. generate_all_tables.py Entry — Note paragraph at bottom

**Current text:**
```
Note: No `key_vars` field is specified in the entry. H14 has no `"type"` key, so it falls through to `generate_table()` (standard 4-IV suite handler) in the main loop at line 1234.
```

**Replace with:**
```
Note: No `key_vars` field is specified in the entry. H14 has no `"type"` key, so it falls through to `generate_table()` (standard 4-IV suite handler) in the main loop at line 1241.
```

**Code reference:** `outputs/generate_all_tables.py` line 1234 is `tex = generate_interaction_table(suite)` (for type=="interaction" branch). Line 1241: `tex = generate_table(suite)` (in the `else` clause, which H14 reaches because it has no "type" key).

---

### Correction 4 — Section D2: Clarify attrition cascade output vs conceptual view

**Section:** D2. Exclusion Criteria — note paragraph

**Current text (append to existing note):**

Add the following sentence at the end of the note:

```
Note: The 5-step D2 table above is a conceptual breakdown for clarity. The actual `sample_attrition.csv` and `sample_attrition.tex` files written to disk contain exactly 4 stages: (1) Master manifest, (2) Main sample filter, (3) DSPREAD non-null, (4) After complete-case + min-calls (col 1). Steps 4 and 5 of the conceptual cascade are combined into a single stage in the output files.
```

**Code reference:** Runner lines 752-759: `attrition_stages` list has exactly 4 tuples. `attrition_table.py` `generate_attrition_table()` iterates this list to produce the output files.

---

## ADDITIONAL NOTES (Non-Blocking)

### Note A: Stale runner docstring — correctly handled

The runner module-level docstring (line 11) says "4 columns" and the Outputs section (line 46) lists `regression_results_col{1-4}.txt`. The actual MODEL_SPECS has 6 entries. The provenance doc follows code-is-truth (documents 6 columns) and flags this as Known Issue #9. No correction needed.

### Note B: Panel builder docstring FiscalYear FE — correctly handled

The panel builder docstring (line 34) says "Fixed Effects: Industry(FF12)/Firm FE + FiscalYear FE (fyearq_int)". The runner actually uses `cal_yr`/`cal_yr_qtr`, not `fyearq_int`, as the panel time index. The provenance doc correctly identifies this in Known Issue #1. No correction needed.

### Note C: Compustat winsorization grouping

The doc says Compustat variables are winsorized "by fiscal year." The engine groups by `comp["fyearq"]`, which is the 4-digit fiscal year integer (e.g., 2003) per code comment at line 1226: "Use fyearq as the year grouping column (integer fiscal year)." The doc's description "by fiscal year" is accurate — `fyearq` here is fiscal year, not fiscal year-quarter.

### Note D: TobinsQ builder docstring discrepancy from engine

The `tobins_q.py` builder docstring says `(AT + cshoq*prccq - CEQ) / AT` — this was an older formula that was replaced during the H1 audit (engine changelog: "TobinsQ: was (mkvaltq+ltq)/atq -- mkvaltq has 41% missing rate. Fixed to (atq + cshoq*prccq - ceqq)/atq"). The actual engine code now computes `(cshoq*prccq + debt_book) / atq`. The builder docstring is stale relative to the engine. The provenance doc's E formula is closer to the actual engine code than the builder docstring. This is correctly identified via code-is-truth principle.

### Note E: fyearq_int in complete-case required list — correctly documented

Known Issue #8 correctly identifies that `fyearq_int` is included in the `required` list for complete-case filtering (runner line 241) despite not being used as a FE column. This causes rows without Compustat fiscal year mappings to be dropped. Well-documented.
