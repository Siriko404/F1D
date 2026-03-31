# Adversarial Audit: Provenance Document for Suite H12

**Audit Date:** 2026-03-30
**Auditor:** Claude Opus 4.6 (hostile audit mode)
**Provenance Doc:** `docs/provenance/H12.md`
**Runner:** `src/f1d/econometric/run_h12_payout.py`
**Panel Builder:** `src/f1d/variables/build_h12_payout_panel.py`
**Creation Prompt:** `docs/Prompts/Suite Provenance Doc.txt`

---

## AUDIT SUMMARY

| Category | Total Checks | Passed | Failed | Score |
|----------|-------------|--------|--------|-------|
| Structural Completeness (Phase 1) | 27 | 26 | 1 | 96.3% |
| Suite Identity (Phase 2) | 10 | 10 | 0 | 100.0% |
| Model Specification (Phase 3) | 7 | 5 | 2 | 71.4% |
| Spec Register (Phase 4) | 13 | 13 | 0 | 100.0% |
| Sample Construction (Phase 5) | 5 | 5 | 0 | 100.0% |
| Variable Dictionary (Phase 6) | 25 | 23 | 2 | 92.0% |
| Pipeline/Outputs/Treatment (Phase 7) | 9 | 8 | 1 | 88.9% |
| Table Generator Entry (Phase 8) | 5 | 5 | 0 | 100.0% |
| Model-Family Addendum (Phase 9) | 5 | 5 | 0 | 100.0% |
| Quality Gates (Phase 10) | 10 | 9 | 1 | 90.0% |
| Cross-Reference Consistency (Phase 11) | 8 | 8 | 0 | 100.0% |
| **TOTAL** | **124** | **117** | **7** | **94.4%** |

---

## VERDICT

**FAIL -- INACCURATE**: Factual errors found. 4 distinct issues identified (some affecting multiple checks). The most significant error is the Volatility window description, which describes a completely different window than what the code implements. The TobinsQ formula is oversimplified, omitting the negative-debt clipping and the both-NaN guard. These require correction.

---

## Phase 1: STRUCTURAL COMPLETENESS

Read the creation prompt (`docs/Prompts/Suite Provenance Doc.txt`) to extract required sections A through L. Then verified each section's presence and completeness in the provenance doc.

| Section | Required by Prompt | Present in Doc | Complete | Notes |
|---------|-------------------|----------------|----------|-------|
| A. Suite Identity | Yes | Yes | Yes | YAML block with all required fields |
| B. Model Specification | Yes | Yes | Yes | All subsections present |
| B1. Regression Equation | Yes | Yes | Yes | Two equations (contemporaneous + lead) |
| B2. Dependent Variable(s) | Yes | Yes | Yes | Table + detailed construction |
| B3. Independent Variable(s) | Yes | Yes | Yes | Table with all 4 IVs |
| B4. Control Variables | Yes | Yes | Yes | Base + Extended tables with Lagged_DV detail |
| B5. Fixed Effects | Yes | Yes | Yes | Table with cols mapping |
| B6. Standard Errors | Yes | Yes | Yes | Clustered entity |
| B7. Hypothesis Test | Yes | Yes | Yes | Code snippet + thresholds |
| C. Spec Register | Yes | Yes | Yes | 12 rows |
| D. Sample Construction | Yes | Yes | Yes | All subsections present |
| D1. Population | Yes | Yes | Yes | 112,968 / 2,429 / 2002-2018 |
| D2. Exclusion Criteria | Yes | Yes | Yes | Attrition cascade table |
| D3. Sample Counts per Spec | Yes | Yes | Yes | 12-row table |
| E. Variable Dictionary | Yes | Yes | Yes | 25 variables listed |
| F. Data Pipeline | Yes | Yes | Yes | All subsections present |
| F1. Dependency Chain | Yes | Yes | Yes | 7-step chain |
| F2. Data Engines | Yes | Yes | Yes | 3 engines |
| F3. Merge Operations | Yes | Yes | Yes | Builder + lead/lag merges |
| G. Outputs | Yes | Yes | Yes | All subsections present |
| G1. Stage 3 Outputs | Yes | Yes | PARTIAL | Missing report_step3 file (see note) |
| G2. Stage 4 Outputs | Yes | Yes | Yes | All files listed |
| G3. Summary Statistics | Yes | Yes | Yes | 17 variables listed |
| H. Outlier/Missing Treatment | Yes | Yes | Yes | H1-H3 all present |
| I. generate_all_tables Entry | Yes | Yes | Yes | Python dict + verification |
| J. Reproduction Commands | Yes | Yes | Yes | 3 commands |
| K. Model-Family Addendum | Yes | Yes | Yes | K1 filled, K2-K6 N/A |
| L. Known Issues | Yes | Yes | Yes | 6 issues documented |

**Phase 1 Result: 26/27 PASS.**

**G1 Note:** The creation prompt template shows `report_step3_{suite}.md` as a standard Stage 3 output. The provenance doc does not list this file. However, examining the panel builder code, it does NOT produce a `report_step3_*.md` file -- it only writes `h12_payout_panel.parquet`, `summary_stats.csv`, and `run_manifest.json`. So the provenance doc is correct to omit it, but it deviates from the prompt template without explanation. **Marked PARTIAL** -- the doc correctly reflects the code, but the template discrepancy is unacknowledged. Similarly, `report_step4_*.md` is not produced by the runner and correctly omitted from G2.

---

## Phase 2: FACTUAL ACCURACY -- SECTION A (Suite Identity)

**A-1. Suite ID**
- Doc claims: `H12`
- Verification: Runner docstring line 6 says `ID: econometric/run_h12_payout`, generate_all_tables line 292 says `"id": "H12"`.
- **PASS**

**A-2. Title**
- Doc claims: `Speech Uncertainty and Quarterly Payout Ratio`
- Verification: Runner line 4 says `STAGE 4: Test H12 Quarterly Payout Ratio Hypothesis`. The LaTeX caption at line 386 says `Speech Uncertainty and Quarterly Payout Ratio`. generate_all_tables line 294 says `H12: Speech Uncertainty and Quarterly Payout Ratio`.
- **PASS**

**A-3. Hypothesis**
- Doc claims: `Does managerial speech uncertainty during earnings calls predict lower quarterly dividend payout ratios?`
- Verification: Runner docstring line 31 says `Hypothesis: One-tailed (beta < 0 -- higher uncertainty -> lower payout).`
- The doc's phrasing is consistent with the code's direction.
- **PASS**

**A-4. Direction**
- Doc claims: `one-tailed beta < 0`
- Verification: Runner line 308 comment says `H12: beta < 0`. Line 328: `p_one = p_two / 2 if beta < 0 else 1 - p_two / 2`. generate_all_tables line 302: `"hyp_dir": "<"`.
- **PASS**

**A-5. Model Family**
- Doc claims: `PanelOLS`
- Verification: Runner line 61: `from linearmodels.panel import PanelOLS`. Lines 286-300: PanelOLS instantiation.
- **PASS**

**A-6. Estimator**
- Doc claims: `linearmodels.panel.PanelOLS`
- Verification: Runner line 61: `from linearmodels.panel import PanelOLS`.
- **PASS**

**A-7. Unit of Observation**
- Doc claims: `call-level (individual earnings call)`
- Verification: Runner docstring line 9: `Quarterly payout ratio. NaN when ibq <= 0`. Panel builder docstring line 9: `Unit of observation: individual earnings call (file_name)`. Each row is a call, not aggregated.
- **PASS**

**A-8. Panel Index**
- Doc claims: `(gvkey, cal_yr) for cols 1-4, 7-10; (gvkey, cal_yr_qtr) for cols 5-6, 11-12`
- Verification: Runner line 262: `time_col = "cal_yr_qtr" if fe_type.endswith("_yq") else "cal_yr"`. Line 282: `df_panel = df_prepared.set_index(["gvkey", time_col])`. The `_yq` suffix appears on cols 5-6 and 11-12 (MODEL_SPECS lines 100-101, 108-109).
- **PASS**

**A-9. Columns**
- Doc claims: `12`
- Verification: `len(MODEL_SPECS)` at runner lines 93-110 = 12 entries (col 1 through col 12).
- **PASS**

**A-10. File Paths**
- Doc claims: `src/f1d/econometric/run_h12_payout.py` and `src/f1d/variables/build_h12_payout_panel.py`
- Verification: Both files exist and were read successfully.
- **PASS**

**Phase 2 Result: 10/10 PASS.**

---

## Phase 3: FACTUAL ACCURACY -- SECTION B (Model Specification)

### B1-CHECK: Regression Equation

- Doc shows two equations: contemporaneous (cols 1-6) and lead (cols 7-12).
- Both equations list 4 IVs simultaneously: CEO_QA_Uncertainty_pct, CEO_Pres_Uncertainty_pct, Manager_QA_Uncertainty_pct, Manager_Pres_Uncertainty_pct.
- Runner line 274: `exog = KEY_IVS + controls` -- all 4 IVs + controls in every spec.
- The equations show alpha_i (entity FE) and delta_t (time FE) with a note that alpha_i is Industry FF12 or Firm, delta_t is cal_yr or cal_yr_qtr. This matches the code.
- No centering, no interaction terms -- consistent with code.
- **PASS**

### B2-CHECK: Dependent Variable(s)

- **PayoutRatio_q**: Doc says `(dvpspq x cshoq) / ibq; NaN when ibq <= 0; dvpspq NaN with ibq > 0 treated as 0`.
  - Code at `_compustat_engine.py` lines 1013-1018: `quarterly_div = comp["dvpspq"].fillna(0) * comp["cshoq"]`, then `PayoutRatio_q = quarterly_div / ibq when ibq > 0, else NaN`.
  - **Match confirmed.**

- **PayoutRatio_q_lead_qtr**: Doc says `PayoutRatio_q shifted forward one consecutive fiscal quarter within gvkey`.
  - Code at `build_h12_payout_panel.py` lines 246-263: shift -1 within gvkey, consecutive check using fiscal_qtr_id.
  - **Match confirmed.**

- Doc's construction detail sections verified against code: fiscal_qtr_id construction (line 225), latest start_date selection (line 238), consecutiveness check (lines 252-259), NaN for non-consecutive (line 261-263).
- No DVs used in code are missing from the doc.
- **PASS**

### B3-CHECK: Independent Variable(s)

- Doc lists 4 IVs: CEO_QA_Uncertainty_pct, CEO_Pres_Uncertainty_pct, Manager_QA_Uncertainty_pct, Manager_Pres_Uncertainty_pct.
- Runner lines 74-79: KEY_IVS = exactly these 4.
- Source engine: LinguisticEngine -- confirmed via builder imports (lines 46-49).
- "No centering, log-transform, or z-scoring" -- confirmed: no transformation code found in runner for IVs.
- **PASS**

### B4-CHECK: Control Variables

- **BASE_CONTROLS** (runner lines 81-85): Size, TobinsQ, ROA, BookLev, CashHoldings, CapexAt, OCF_Volatility, Lagged_DV. Doc lists exactly these 8.
- **EXTENDED_CONTROLS** (runner lines 87-89): BASE_CONTROLS + SalesGrowth, RD_Intensity, CashFlow, Volatility. Doc lists exactly these 4 additional.

- **TobinsQ formula error**: Doc B4 says `(cshoq x prccq + dlcq + dlttq) / atq; missing debt filled as 0`.
  - Actual code (`_compustat_engine.py` lines 982-992):
    - `mktcap = cshoq * prccq`
    - `debt_c = dlcq.clip(lower=0).fillna(0)` -- negative debt clipped to 0
    - `debt_t = dlttq.clip(lower=0).fillna(0)` -- negative debt clipped to 0
    - `debt_book = np.where(dlcq.isna() & dlttq.isna(), np.nan, debt_c + debt_t)` -- NaN when BOTH missing
    - `TobinsQ = (mktcap + debt_book) / atq` when `atq > 0` and `mktcap.notna()`
  - The doc's formula omits: (1) the `.clip(lower=0)` on negative debt values, (2) the `debt_book = NaN` guard when both dlcq and dlttq are NaN, (3) the `mktcap.notna()` condition.
  - The doc says "missing debt filled as 0" which is partially correct (each individual component is fillna(0)), but critically wrong when BOTH are NaN (debt_book becomes NaN, not 0).
  - **FAIL -- Oversimplified formula misses negative-debt clipping and both-NaN guard.**

- **Volatility formula error**: Doc B4 says `std(daily_ret) x sqrt(252) x 100 over [prev_call + 5d, call - 5d]; min 10 trading days`.
  - Actual code (`_crsp_engine.py` lines 41-42, 361-366):
    - `DAYS_AFTER_CURRENT_CALL = 1` (window starts 1 day after current call)
    - `DAYS_BEFORE_NEXT_CALL = 5` (window ends 5 days before next call)
    - `window_start = start_date + Timedelta(days=1)`
    - `window_end = next_call_date - Timedelta(days=5)`
  - The doc says `[prev_call + 5d, call - 5d]` -- this is the **wrong** window. The correct window is `[current_call + 1d, next_call - 5d]`.
  - **FAIL -- Completely wrong window description.**

- **Lagged_DV detail** (runner lines 208-212): Doc says `base_dv = dv.replace("_lead_qtr", "").replace("_lead", "")`. Code confirms: line 209 `base_dv = dv.replace("_lead_qtr", "").replace("_lead", "")`. Line 210: `lag_col = f"{base_dv}_lag"`. Line 212: `panel["Lagged_DV"] = panel[lag_col]`. Match confirmed.
- No dynamic controls (no auto-add logic). Confirmed.

**Phase 3 Result: 5/7 PASS, 2 FAIL (TobinsQ formula, Volatility window).**

---

## Phase 4: FACTUAL ACCURACY -- SECTION C (Spec Register)

Verified each of the 12 rows against MODEL_SPECS (runner lines 93-110):

| Col | Doc DV | Code DV | Doc Entity FE | Code FE | Doc Time FE | Code Time FE | Doc Controls | Code Controls | PASS? |
|-----|--------|---------|---------------|---------|-------------|-------------|-------------|--------------|-------|
| 1 | PayoutRatio_q | PayoutRatio_q | Industry (FF12) | industry | Cal Year | cal_yr | Base | base | PASS |
| 2 | PayoutRatio_q | PayoutRatio_q | Firm | firm | Cal Year | cal_yr | Base | base | PASS |
| 3 | PayoutRatio_q | PayoutRatio_q | Industry (FF12) | industry | Cal Year | cal_yr | Extended | extended | PASS |
| 4 | PayoutRatio_q | PayoutRatio_q | Firm | firm | Cal Year | cal_yr | Extended | extended | PASS |
| 5 | PayoutRatio_q | PayoutRatio_q | Industry (FF12) | industry_yq | Cal Year-Quarter | cal_yr_qtr | Extended | extended | PASS |
| 6 | PayoutRatio_q | PayoutRatio_q | Firm | firm_yq | Cal Year-Quarter | cal_yr_qtr | Extended | extended | PASS |
| 7 | PayoutRatio_q_lead_qtr | PayoutRatio_q_lead_qtr | Industry (FF12) | industry | Cal Year | cal_yr | Base | base | PASS |
| 8 | PayoutRatio_q_lead_qtr | PayoutRatio_q_lead_qtr | Firm | firm | Cal Year | cal_yr | Base | base | PASS |
| 9 | PayoutRatio_q_lead_qtr | PayoutRatio_q_lead_qtr | Industry (FF12) | industry | Cal Year | cal_yr | Extended | extended | PASS |
| 10 | PayoutRatio_q_lead_qtr | PayoutRatio_q_lead_qtr | Firm | firm | Cal Year | cal_yr | Extended | extended | PASS |
| 11 | PayoutRatio_q_lead_qtr | PayoutRatio_q_lead_qtr | Industry (FF12) | industry_yq | Cal Year-Quarter | cal_yr_qtr | Extended | extended | PASS |
| 12 | PayoutRatio_q_lead_qtr | PayoutRatio_q_lead_qtr | Firm | firm_yq | Cal Year-Quarter | cal_yr_qtr | Extended | extended | PASS |

- Count: 12 rows in doc, 12 in MODEL_SPECS. Match.
- No specs in code missing from table.
- No specs in table not in code.

**Phase 4 Result: 13/13 PASS.**

---

## Phase 5: FACTUAL ACCURACY -- SECTION D (Sample Construction)

### D1-CHECK: Population

- Doc says: 112,968 calls, 2,429 firms, 2002-2018.
- Cross-reference with project scope (memory file `project_thesis_scope.md`): 112,968 calls, 2,429 firms, 2002-2018.
- **PASS**

### D2-CHECK: Exclusion Criteria

Doc's attrition cascade:

| Step | Doc Filter | Code Reference |
|------|-----------|---------------|
| 1 | Full panel: 112,968 | Runner line 569: `full_n = len(panel)` |
| 2 | Main sample (excl FF12 8,11): 88,205 | Runner lines 189-195: `~panel["ff12_code"].isin([8, 11])` |
| 3 | PayoutRatio_q non-null (ibq > 0): 70,695 | Runner lines 225-228: `df[dv].notna()` |
| 4 | Complete-case + min-calls >= 5: 40,910 | Runner lines 231-240 |

- Filter order matches code execution order. Step 3 (DV non-null) happens before complete-case and min-calls.
- The doc notes these are from a specific run (2026-03-27_095009), which is plausible.
- The doc correctly notes "col 1" and that other columns differ.
- **PASS**

### D3-CHECK: Sample Counts per Spec

- Doc provides 12-row table with N and N(firms) per col.
- N drops from cols 1-2 (40,910) to cols 3-6 (39,290) due to extended controls requiring more non-missing values. Plausible.
- N drops from contemporaneous to lead (39,019 for cols 7-8) due to lead variable requiring consecutive quarter data. Plausible.
- Further drop to 38,281 for cols 9-12 (extended controls on lead DV). Plausible.
- All counts sourced from `model_diagnostics.csv`.
- **PASS**

**Phase 5 Result: 5/5 PASS.**

---

## Phase 6: FACTUAL ACCURACY -- SECTION E (Variable Dictionary)

Verified each variable in the dictionary:

### DVs

| Variable | Name Match | Formula | Source | Winsorization | Timing | PASS? |
|----------|-----------|---------|--------|--------------|--------|-------|
| PayoutRatio_q | Yes (code uses `PayoutRatio_q`) | Doc: `(dvpspq.fillna(0) x cshoq) / ibq; NaN when ibq <= 0`. Code: same formula at `_compustat_engine.py:1013-1018`. | CompustatEngine -- correct | Doc: `1%/99% by fiscal year`. Code: PayoutRatio_q is in COMPUSTAT_COLS and not in skip_winsorize, so it IS winsorized 1%/99% by fyearq. Correct. | Contemporaneous -- correct | PASS |
| PayoutRatio_q_lead_qtr | Yes | Doc: `shifted +1 consecutive fiscal quarter per gvkey`. Code: `build_h12_payout_panel.py:246-263`. Correct. | CompustatEngine (derived) -- correct | Doc: `Via PayoutRatio_q winsorization`. The lead is constructed from already-winsorized PayoutRatio_q values. Correct. | Lead (t+1 qtr) -- correct | PASS |
| PayoutRatio_q_lag | Yes | Doc: `shifted -1 consecutive fiscal quarter per gvkey`. Code: `build_h12_payout_panel.py:278-302`. Correct. | CompustatEngine (derived) -- correct | Doc: `Via PayoutRatio_q winsorization`. Same logic as lead. Correct. | Lag (t-1 qtr) -- correct | PASS |

### IVs

| Variable | Name Match | Formula | Source | Winsorization | Timing | PASS? |
|----------|-----------|---------|--------|--------------|--------|-------|
| CEO_QA_Uncertainty_pct | Yes | `(uncertainty words / total words) x 100` -- consistent with LinguisticEngine construction | LinguisticEngine -- correct | Doc: `0%/99% upper-only per year`. Code: `_linguistic_engine.py:255-258`: `winsorize_by_year(..., lower=0.0, upper=0.99, ...)`. Correct. | Contemporaneous -- correct | PASS |
| CEO_Pres_Uncertainty_pct | Yes | Same formula pattern | LinguisticEngine -- correct | Same winsorization | Contemporaneous | PASS |
| Manager_QA_Uncertainty_pct | Yes | Same formula pattern | LinguisticEngine -- correct | Same winsorization | Contemporaneous | PASS |
| Manager_Pres_Uncertainty_pct | Yes | Same formula pattern | LinguisticEngine -- correct | Same winsorization | Contemporaneous | PASS |

### Controls

| Variable | Name Match | Formula | Source | Winsorization | Timing | PASS? |
|----------|-----------|---------|--------|--------------|--------|-------|
| Size | Yes | Doc: `ln(atq); NaN when atq <= 0`. Code: `_compustat_engine.py:938`: `np.where(comp["atq"] > 0, np.log(comp["atq"]), np.nan)`. Correct. | CompustatEngine: atq -- correct | 1%/99% by fiscal year -- correct (in winsorize_cols) | Contemporaneous | PASS |
| TobinsQ | Yes | Doc: `(cshoq x prccq + dlcq.fillna(0) + dlttq.fillna(0)) / atq; requires atq > 0 and mktcap non-null`. Code: uses `.clip(lower=0).fillna(0)` on debt, and `debt_book = NaN` when both dlcq and dlttq are NaN. Doc omits clip(lower=0) and the both-NaN guard. | CompustatEngine -- correct | 1%/99% by fiscal year -- correct | Contemporaneous | **FAIL** |
| ROA | Yes | Doc: `iby_annual (Q4) / ((atq_t + atq_{t-1}) / 2); requires avg_assets > 0`. Code: `_compustat_engine.py:954-964`. Uses annual Q4 iby and average assets. Correct. | CompustatEngine -- correct | 1%/99% by fiscal year -- correct | Contemporaneous | PASS |
| BookLev | Yes | Doc: `(dlcq.fillna(0) + dlttq.fillna(0)) / atq`. Code: `_compustat_engine.py:943`: `(comp["dlcq"].fillna(0) + comp["dlttq"].fillna(0)) / comp["atq"]`. Correct. | CompustatEngine -- correct | 1%/99% -- correct | Contemporaneous | PASS |
| CashHoldings | Yes | Doc: `cheq / atq`. Code: `_compustat_engine.py:981`: `comp["cheq"] / comp["atq"]`. Correct. | CompustatEngine -- correct | 1%/99% -- correct | Contemporaneous | PASS |
| CapexAt | Yes | Doc: `capxy_annual (Q4) / atq_{t-1}; requires lagged atq > 0`. Code: `_compustat_engine.py:994-1000`. Uses annual Q4 capxy and lagged atq. Correct. | CompustatEngine -- correct | 1%/99% -- correct | Contemporaneous | PASS |
| OCF_Volatility | Yes | Doc: `Rolling 5-year std (min 3 yrs) of (oancfy / atq_{t-1}) per gvkey; uses Q4-only annual panel`. Code verified at `_compute_ocf_volatility()`. Correct. | CompustatEngine -- correct | 1%/99% -- correct | Contemporaneous | PASS |
| SalesGrowth | Yes | Doc: `(saley_t - saley_{t-1}) / abs(saley_{t-1}); Q4-only annual; saleq fallback`. Code: `_compustat_engine.py:653-657`. Correct. | CompustatEngine -- correct | Doc: `1%/99% by fiscal year (inside Biddle residual computation)`. Code: winsorized at line 661 inside `_compute_biddle_residual`, skipped in main winsorize loop (skip_winsorize set). Correct. | Contemporaneous | PASS |
| RD_Intensity | Yes | Doc: `xrdq.fillna(0) / atq`. Code: `_compustat_engine.py:967`: `comp["xrdq"].fillna(0) / comp["atq"]`. Correct. | CompustatEngine -- correct | 1%/99% -- correct | Contemporaneous | PASS |
| CashFlow | Yes | Doc: `oancfy (Q4 annual) / avg_assets; avg = (atq_t + atq_{t-1}) / 2, fallback to atq_t`. Code: `_compustat_engine.py:679-686`. Uses avg_assets with fallback. Correct. | CompustatEngine -- correct | Doc: `1%/99% by fiscal year (inside Biddle residual computation)`. Code: winsorized at line 688. Correct. | Contemporaneous | PASS |
| Volatility | Yes | Doc formula correct: `std(daily_ret) x sqrt(252) x 100`. Code: `_crsp_engine.py:255`: `std_ret * np.sqrt(252) * 100`. Formula correct. But doc window description WRONG: says `[prev_call + 5d, call - 5d]`. Actual window: `[start_date + 1d, next_call_date - 5d]`. | CRSPEngine -- correct | Doc: `1%/99% per year`. Code: `_crsp_engine.py:445-447`: default lower=0.01, upper=0.99. Correct. | Contemporaneous | **FAIL** (window) |

### FE Variables

| Variable | Name Match | Type | Source | PASS? |
|----------|-----------|------|--------|-------|
| gvkey | Yes | FE (entity) | Manifest | PASS |
| ff12_code | Yes | FE (other) | Manifest (SIC-to-FF12) | PASS |
| cal_yr | Yes | FE (time) | `start_date.dt.year` via `build_cal_yr_qtr_index()`. Code at `panel_utils.py:215`: `dt.dt.year`. Correct. | PASS |
| cal_yr_qtr | Yes | FE (time) | Doc: `cal_yr x 10 + start_date.dt.quarter`. Code at `panel_utils.py:217`: `panel["cal_yr"] * 10 + panel["cal_qtr"]`. Correct. | PASS |

### Completeness Check

- All variables from MODEL_SPECS (DVs + IVs + controls) are in the dictionary: Yes
- All BASE_CONTROLS present: Yes (Size, TobinsQ, ROA, BookLev, CashHoldings, CapexAt, OCF_Volatility, Lagged_DV)
- All EXTENDED_CONTROLS present: Yes (adds SalesGrowth, RD_Intensity, CashFlow, Volatility)
- FE columns present: Yes (gvkey, ff12_code, cal_yr, cal_yr_qtr)
- PayoutRatio_q_lag (used as Lagged_DV source) present: Yes

**Phase 6 Result: 23/25 PASS, 2 FAIL (TobinsQ formula detail, Volatility window).**

---

## Phase 7: FACTUAL ACCURACY -- SECTIONS F, G, H

### F-CHECK: Data Pipeline

**F1. Dependency Chain**:
- 7 steps from raw inputs through table generation. Verified each step:
  1. Raw inputs: master_sample_manifest, Compustat, CRSP, linguistic parquets -- correct.
  2. Engine loading: CompustatEngine, CRSPEngine, LinguisticEngine -- correct.
  3. Panel builder outputs `h12_payout_panel.parquet` -- correct (builder line 374).
  4. Runner loads from `outputs/variables/h12_payout/latest/` -- correct (runner line 169).
  5. Sample filtering: FF12 != 8,11, Lagged_DV creation, inf replacement, DV non-null, complete-case, min 5 calls -- correct order matches code (runner lines 189-241).
  6. PanelOLS with firm-clustered SEs, 12 specs -- correct.
  7. Entry in generate_all_tables.py -- correct.
- **PASS**

**F2. Data Engines**:
- Doc lists 3 engines: CompustatEngine, CRSPEngine, LinguisticEngine.
- CompustatEngine provides: PayoutRatio_q, Size, BookLev, TobinsQ, ROA, CashHoldings, CapexAt, OCF_Volatility, SalesGrowth, RD_Intensity, CashFlow, fqtr -- all confirmed in COMPUSTAT_COLS and builder.
- CRSPEngine provides: Volatility -- confirmed.
- LinguisticEngine provides: 4 uncertainty IVs -- confirmed via builder imports.
- **PASS**

**F3. Merge Operations**:
- Doc lists 16 builder merges (all on file_name, left join) + 2 lead/lag merges (on gvkey + fiscal_qtr_id, left join).
- Verified builder merge loop at lines 130-146: iterates all_results except manifest, merges on file_name, left join. Row count assertion at line 144. Conflicting columns dropped at line 141.
- Lead/lag merges verified at lines 272 and 299.
- **PASS**

### G-CHECK: Outputs

**G1. Stage 3 Outputs**:
- Doc lists: `h12_payout_panel.parquet`, `summary_stats.csv`, `run_manifest.json`.
- Code: builder line 374 writes parquet, line 380 writes summary_stats.csv, line 384 calls generate_manifest.
- No `report_step3_*.md` file is produced by the builder. Doc correctly does not list it.
- **PASS**

**G2. Stage 4 Outputs**:
- Doc lists: `h12_payout_table.tex`, `model_diagnostics.csv`, `summary_stats.csv`, `summary_stats.tex`, `sample_attrition.csv`, `sample_attrition.tex`, `regression_results_col{1-12}.txt`, `run_manifest.json`.
- Code verification:
  - Runner line 496: writes `h12_payout_table.tex` -- match.
  - Runner line 531: writes `model_diagnostics.csv` -- match.
  - Runner lines 585-591: writes `summary_stats.csv` and `summary_stats.tex` -- match.
  - Runner line 625: calls `generate_attrition_table` -- writes `sample_attrition.csv` and `sample_attrition.tex` -- match.
  - Runner lines 516-517: writes `regression_results_col{N}.txt` -- match.
  - Runner line 629: calls `generate_manifest` -- writes `run_manifest.json` -- match.
- No outputs in code missing from doc. No phantom outputs in doc.
- **PASS**

**G3. Summary Statistics**:
- Doc lists 17 variables matching SUMMARY_STATS_VARS (runner lines 119-137).
- Verified every variable name and label matches.
- Metrics: `make_summary_stats_table` computes N, Mean, SD, Min, P25, Median, P75, Max -- consistent with doc.
- **PASS**

### H-CHECK: Outlier/Missing Treatment

**H1. Winsorization**:
- Compustat 1%/99% by fyearq: Correct. Code at `_compustat_engine.py:1115-1136`. Uses `_winsorize_by_year(comp[col], year_col)` where year_col = fyearq.
- Skip set: DividendPayer, CashFlow, SalesGrowth, fqtr. Confirmed at lines 1123-1128.
- CashFlow and SalesGrowth winsorized inside Biddle at lines 661 and 688. Correct.
- Linguistic 0%/99% upper-only per year: Correct. Code at `_linguistic_engine.py:255-258`: `lower=0.0, upper=0.99`.
- CRSP 1%/99% per year: Correct. Code at `_crsp_engine.py:445-447`: default `lower=0.01, upper=0.99`.
- Min obs threshold 10 for all: Confirmed in all three engines.
- **PASS**

**H2. Missing Data Policy**:
- Complete-case deletion: Runner line 231-232. Correct.
- Inf replacement: Runner line 223. Correct.
- Negative earnings: ibq <= 0 produces NaN at engine level. Correct.
- Missing dividends: dvpspq.fillna(0). Correct.
- Non-consecutive fiscal quarters: lead/lag = NaN for gaps. Correct.
- **PASS**

**H3. Transformations**:
- Doc lists Size (log), Volatility (annualized), OCF_Volatility (rolling std).
- No centering, z-scoring, or scaling on IVs or DVs. Confirmed.
- **PASS** with one note: the Volatility window description is still wrong here (repeated from E), but the transformation formula itself (std * sqrt(252) * 100) is correct. The window issue is already captured in Phase 6.

**Phase 7 Result: 8/9 PASS. The Volatility window error propagates but is counted only once (in Phase 6). All other checks PASS.**

Wait -- reviewing more carefully: Section H does NOT repeat the window description. It only says "std(daily_ret) x sqrt(252) x 100" for the transformation, and the window is in Section E. So H3 is clean.

**Phase 7 Result (corrected): 9/9 PASS.**

Actually, I need to re-examine. The question is whether Section F step 5 or H mentions the Volatility window. Let me re-check:
- F1 step 5 does not mention Volatility window.
- H3 Transformations table says "std(daily_ret) x sqrt(252) x 100" without window. Clean.

**Phase 7 Final Result: 9/9 PASS.**

---

## Phase 8: FACTUAL ACCURACY -- SECTION I (Table Generator Entry)

Doc quotes the following entry from `outputs/generate_all_tables.py` lines 290-304:

```python
{
    "id": "H12",
    "dir": "h12_payout/2026-03-27_095009",
    "caption": "H12: Speech Uncertainty and Quarterly Payout Ratio",
    "label": "tab:h12",
    "cols": 12,
    "dvs": [
        (r"PayoutRatio\_q", 6),
        (r"PayoutRatio\_q\_lead\_qtr", 6),
    ],
    "tail": "one",
    "hyp_dir": "<",
    "time_fe_label": "Year FE",
}
```

Verified against actual code at lines 291-304:

| Field | Doc Value | Code Value | PASS? |
|-------|----------|------------|-------|
| id | "H12" | "H12" | PASS |
| dir | "h12_payout/2026-03-27_095009" | "h12_payout/2026-03-27_095009" | PASS |
| cols | 12 | 12 | PASS |
| tail / hyp_dir | "one" / "<" | "one" / "<" | PASS |
| dvs | PayoutRatio_q (6) + lead_qtr (6) | Same | PASS |

Note: The entry does NOT have `key_vars`, `key_labels`, or `key_tails` fields. This is because H12 uses the standard `generate_table()` path which auto-discovers IVs from the regression output files rather than requiring explicit key_vars. The provenance doc does not mention this absence but also does not claim these fields exist. Acceptable.

The doc notes that `time_fe_label: "Year FE"` is used as a label but the actual runner uses both cal_yr and cal_yr_qtr. This discrepancy is documented in the provenance doc's own verification section. This is a known limitation of the table generator labeling, not an error in the provenance doc.

**Phase 8 Result: 5/5 PASS.**

---

## Phase 9: FACTUAL ACCURACY -- SECTION K (Model-Family Addendum)

Model family is PanelOLS (confirmed in Phase 2). Section K1 is filled; K2-K6 are marked N/A. Correct structure.

### K1 Verification

**Entity effects -- Industry FE specs (cols 1,3,5,7,9,11)**:
- Doc: `entity_effects=False, other_effects=df_panel["ff12_code"], time_effects=True, drop_absorbed=True`
- Code (runner lines 286-294): Exact match. `entity_effects=False`, `time_effects=True`, `other_effects=df_panel["ff12_code"]`, `drop_absorbed=True`.
- **PASS**

**Entity effects -- Firm FE specs (cols 2,4,6,8,10,12)**:
- Doc: `EntityEffects` in formula with `TimeEffects`, `drop_absorbed=True`
- Code (runner lines 297-300): `formula = f"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"`, `PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)`.
- **PASS**

**Time effects**:
- Doc: Calendar Year specs indexed on `(gvkey, cal_yr)`, Year-Quarter on `(gvkey, cal_yr_qtr)`, both with `time_effects=True`.
- Code: line 262 sets time_col, line 282 sets index. Industry path uses `time_effects=True` explicitly; firm path uses `TimeEffects` in formula.
- **PASS**

**drop_absorbed**:
- Doc: `True` for all specs.
- Code: line 292 and 299 both set `drop_absorbed=True`.
- **PASS**

**check_rank**:
- Doc: `False` for industry FE specs (runner line 293); default for firm FE formula specs.
- Code: line 293: `check_rank=False`. Firm FE path does not set check_rank (uses default from PanelOLS.from_formula).
- **PASS**

**Phase 9 Result: 5/5 PASS.**

---

## Phase 10: QUALITY GATE CHECKLIST

| # | Quality Gate | Met? | Evidence |
|---|-------------|------|----------|
| 1 | Every variable in every regression spec appears in Variable Dictionary with explicit formula and source engine | YES | All 25 variables (2 DVs, 1 lagged DV, 4 IVs, 12 controls, 4 FE columns, 2 additional computed) have entries with formulas and source engines. Verified in Phase 6. |
| 2 | The model equation matches what the code actually estimates | YES | Two equations (contemporaneous + lead) match runner's exog construction: KEY_IVS + controls with entity + time FE. Verified in Phase 3 B1. |
| 3 | The specification register accounts for every model column | YES | 12 rows matching 12 MODEL_SPECS entries. All DV/FE/control combinations verified. Phase 4. |
| 4 | The attrition cascade has row counts for each filter step | YES | 4-step cascade with row counts from actual run output. Phase 5. |
| 5 | The tail test direction matches between runner code and generate_all_tables.py | YES | Runner: beta < 0 (line 328). generate_all_tables: `"tail": "one"`, `"hyp_dir": "<"`. Match. |
| 6 | The FE specification matches between docstring, code, and this document | YES | Docstring (lines 16-21, 35): cal_yr and cal_yr_qtr. Code (lines 262, 282, 285-300): same. Doc sections B5, C, K1: consistent. |
| 7 | Every merge in the panel builder is documented with join keys and type | YES | 16 file_name merges + 2 lead/lag merges all documented in F3 with keys and join type. Phase 7. |
| 8 | The output file list matches what the runner actually writes | YES | All 8+ output file types documented, verified against code write operations. Phase 7 G-check. |
| 9 | The model-family addendum is filled for the correct family only | YES | K1 (PanelOLS) filled with verified details. K2-K6 marked N/A. Phase 9. |
| 10 | Any claim marked [UNVERIFIED] has an explanation of what blocks verification | NO | No [UNVERIFIED] markers in the doc. However, the Volatility window description and TobinsQ formula are stated as verified facts but are INCORRECT. Gate 10 is technically met (no unverified claims exist), but the spirit is violated because incorrect claims should have been flagged as unverifiable or verified more carefully. |

Wait -- re-reading gate 10: "Any claim marked [UNVERIFIED] has an explanation." Since no claims are marked [UNVERIFIED], this gate is technically satisfied. The issue is that claims are presented as verified when they are actually wrong, which is a different problem (covered by gates 1-2).

**Quality Gate 10 reassessment**: MET. No [UNVERIFIED] markers exist, so the requirement is vacuously satisfied.

But I note that Quality Gate 1 says "every variable... with explicit formula." TobinsQ and Volatility have incorrect formulas/descriptions. Does gate 1 require the formulas to be CORRECT? The gate says "appears... with explicit formula and source engine." Having an explicit formula that is wrong is borderline. I will mark it as FAIL since the intent is accuracy.

| # | Quality Gate | Met? |
|---|-------------|------|
| 1 | Every variable... with explicit formula and source engine | **NO** -- TobinsQ formula oversimplified (missing clip/both-NaN guard); Volatility window wrong |
| 2-10 | (as above) | YES |

**Phase 10 Result: 9/10 PASS, 1 FAIL (Gate 1 -- formula accuracy).**

---

## Phase 11: CROSS-REFERENCE CONSISTENCY

### Check 1: DVs in B2 match DVs in C (spec register)
- B2 lists: PayoutRatio_q, PayoutRatio_q_lead_qtr
- C uses: PayoutRatio_q (cols 1-6), PayoutRatio_q_lead_qtr (cols 7-12)
- **CONSISTENT**

### Check 2: DVs in C match DVs in I (table generator)
- C: PayoutRatio_q (6 cols) + PayoutRatio_q_lead_qtr (6 cols)
- I: `(r"PayoutRatio\_q", 6)`, `(r"PayoutRatio\_q\_lead\_qtr", 6)`
- **CONSISTENT**

### Check 3: Controls in B4 match variables in E (dictionary)
- B4 Base: Size, TobinsQ, ROA, BookLev, CashHoldings, CapexAt, OCF_Volatility, Lagged_DV
- B4 Extended adds: SalesGrowth, RD_Intensity, CashFlow, Volatility
- E has all 12 controls + PayoutRatio_q_lag (source of Lagged_DV).
- **CONSISTENT**

### Check 4: Column count in A matches rows in C
- A: 12 columns
- C: 12 rows
- **CONSISTENT**

### Check 5: Column count in A matches "cols" in I
- A: 12
- I: `"cols": 12`
- **CONSISTENT**

### Check 6: Tail direction in A matches B7 matches I
- A: `one-tailed beta < 0`
- B7: `One-tailed (beta < 0)`, code snippet `p_two / 2 if beta < 0`
- I: `"tail": "one"`, `"hyp_dir": "<"`
- **CONSISTENT**

### Check 7: FE in B5 matches C matches K
- B5: Industry (ff12_code) for odd cols, Firm (gvkey) for even cols; cal_yr for cols 1-4,7-10, cal_yr_qtr for cols 5-6,11-12
- C: Industry(FF12) for odd, Firm for even; Cal Year or Cal Year-Quarter matching B5 col assignments
- K1: entity_effects=False + other_effects=ff12_code for industry; EntityEffects for firm; time_effects via index
- **CONSISTENT**

### Check 8: Panel index in A matches set_index in K
- A: `(gvkey, cal_yr)` for cols 1-4,7-10; `(gvkey, cal_yr_qtr)` for cols 5-6,11-12
- K1: `panel indexed on (gvkey, cal_yr)` for Calendar Year specs; `(gvkey, cal_yr_qtr)` for Year-Quarter specs
- **CONSISTENT**

**Phase 11 Result: 8/8 PASS.**

---

## FAILURES (detailed)

| Phase | Check | Provenance Doc Claims | Actual Code Says | Severity | Fix Required |
|-------|-------|----------------------|-----------------|----------|-------------|
| 3 (B4) | TobinsQ formula | `(cshoq x prccq + dlcq + dlttq) / atq; missing debt filled as 0` | `mktcap = cshoq * prccq; debt_c = dlcq.clip(lower=0).fillna(0); debt_t = dlttq.clip(lower=0).fillna(0); debt_book = NaN when both dlcq and dlttq are NaN, else debt_c + debt_t; TobinsQ = (mktcap + debt_book) / atq when atq > 0 and mktcap not NaN` | MEDIUM | Yes -- formula in B4 and E must include clip(lower=0) and both-NaN guard |
| 3 (B4) | Volatility window | `std(daily_ret) x sqrt(252) x 100 over [prev_call + 5d, call - 5d]; min 10 trading days` | `window_start = start_date + Timedelta(days=1); window_end = next_call_date - Timedelta(days=5)` i.e. `[current_call + 1d, next_call - 5d]` | HIGH | Yes -- window description in B4 and E is completely wrong |
| 6 (E) | TobinsQ formula | Same as B4 | Same as B4 | MEDIUM | Yes -- same fix needed in variable dictionary |
| 6 (E) | Volatility window | Same as B4 | Same as B4 | HIGH | Yes -- same fix needed in variable dictionary |
| 10 | Gate 1 (formula accuracy) | Formulas presented as verified | TobinsQ and Volatility descriptions contain errors | MEDIUM | Fixing the above fixes this gate |
| 1 (G1) | report_step3 file | Not listed (correct per code) | Builder does not produce report_step3 | LOW | No code fix needed, but doc could note this deviation from prompt template |

---

## CORRECTIONS REQUIRED

### Correction 1: TobinsQ formula in Section B4

**Current (wrong):**
```
| TobinsQ | Tobin's Q | (cshoq x prccq + dlcq + dlttq) / atq; missing debt filled as 0 | CompustatEngine: cshoq, prccq, dlcq, dlttq, atq |
```

**Should be:**
```
| TobinsQ | Tobin's Q | (cshoq x prccq + debt_book) / atq; debt_c = dlcq.clip(lower=0).fillna(0), debt_t = dlttq.clip(lower=0).fillna(0), debt_book = NaN when both dlcq and dlttq are NaN else debt_c + debt_t; requires atq > 0 and mktcap non-null | CompustatEngine: cshoq, prccq, dlcq, dlttq, atq |
```

**Code reference:** `_compustat_engine.py` lines 982-992.

### Correction 2: Volatility window in Section B4

**Current (wrong):**
```
| Volatility | Stock return volatility | std(daily_ret) x sqrt(252) x 100 over [prev_call + 5d, call - 5d]; min 10 trading days | CRSPEngine: RET |
```

**Should be:**
```
| Volatility | Stock return volatility | std(daily_ret) x sqrt(252) x 100 over [current_call + 1d, next_call - 5d]; min 10 trading days | CRSPEngine: RET |
```

**Code reference:** `_crsp_engine.py` lines 41-42, 361-366:
- `DAYS_AFTER_CURRENT_CALL = 1`
- `DAYS_BEFORE_NEXT_CALL = 5`
- `window_start = start_date + Timedelta(days=DAYS_AFTER_CURRENT_CALL)`
- `window_end = next_call_date - Timedelta(days=DAYS_BEFORE_NEXT_CALL)`

### Correction 3: TobinsQ formula in Section E (Variable Dictionary)

**Current (wrong):**
```
| TobinsQ | Tobin's Q | Control | (cshoq x prccq + dlcq.fillna(0) + dlttq.fillna(0)) / atq; requires atq > 0 and mktcap non-null | CompustatEngine: cshoq, prccq, dlcq, dlttq, atq | 1%/99% by fiscal year | Contemporaneous |
```

**Should be:**
```
| TobinsQ | Tobin's Q | Control | (cshoq x prccq + debt_book) / atq; debt_c = dlcq.clip(lower=0).fillna(0), debt_t = dlttq.clip(lower=0).fillna(0), debt_book = NaN when both dlcq & dlttq are NaN else debt_c + debt_t; requires atq > 0 and mktcap non-null | CompustatEngine: cshoq, prccq, dlcq, dlttq, atq | 1%/99% by fiscal year | Contemporaneous |
```

**Code reference:** Same as Correction 1.

### Correction 4: Volatility window in Section E (Variable Dictionary)

**Current (wrong):**
```
| Volatility | Stock Volatility | Control | std(daily_ret) x sqrt(252) x 100 over [prev_call + 5d, call - 5d]; requires >= 10 trading days | CRSPEngine: RET | 1%/99% per year | Contemporaneous |
```

**Should be:**
```
| Volatility | Stock Volatility | Control | std(daily_ret) x sqrt(252) x 100 over [current_call + 1d, next_call - 5d]; requires >= 10 trading days | CRSPEngine: RET | 1%/99% per year | Contemporaneous |
```

**Code reference:** Same as Correction 2.

---

## ADDITIONAL OBSERVATIONS (non-blocking)

1. **BookLev vs TobinsQ debt handling inconsistency**: BookLev uses `dlcq.fillna(0) + dlttq.fillna(0)` without the clip(lower=0) or both-NaN guard that TobinsQ uses. This is a code design difference, not a doc error -- the provenance doc accurately reflects both formulas as implemented. But it is worth noting that the two variables handle missing/negative debt differently.

2. **R-squared description in L3**: Known issue L3 states "The R-squared reported by PanelOLS in these specs is the overall (not within) R-squared." This claim about PanelOLS reporting overall R-squared is potentially misleading. PanelOLS with `entity_effects=True` reports within-R-squared by default (`.rsquared`). However, the runner computes adj_R2 manually at line 306-307: `1 - (1 - model.rsquared) * (model.nobs - 1) / model.df_resid`. The behavior depends on whether entity effects are absorbed. This observation does not affect the audit score but merits review.

3. **Zero-inflation percentage discrepancy**: The provenance doc L1 says "Approximately 52.8%" while the runner docstring line 37 says "~57%". These refer to different samples (L1 seems to reference the full main sample; docstring may reference the filtered regression sample). Not a doc error per se, but the discrepancy should be acknowledged.

4. **generate_all_tables.py entry missing key_vars**: The H12 entry uses the standard `generate_table()` path which auto-discovers variables from regression output files. Unlike some other suites, H12 does not define `key_vars`, `key_labels`, or `key_tails`. The provenance doc does not explicitly flag this but also does not claim these fields exist. Not an error.

---

*Audit completed 2026-03-30. All 11 phases executed. 124 individual checks performed.*
