# Adversarial Audit Report: Suite H16

**Audit Date:** 2026-03-30
**Auditor:** Claude Opus 4.6 (1M context)
**Suite:** H16 -- Speech Uncertainty and R&D Investment Intensity
**Provenance Doc:** `docs/provenance/H16.md`
**Runner:** `src/f1d/econometric/run_h16_rd_sales.py`
**Panel Builder:** `src/f1d/variables/build_h16_rd_sales_panel.py`

---

## AUDIT SUMMARY

| Category | Total Checks | Passed | Failed | Score |
|----------|-------------|--------|--------|-------|
| Structural Completeness (Phase 1) | 26 | 25 | 1 | 96% |
| Suite Identity (Phase 2) | 10 | 10 | 0 | 100% |
| Model Specification (Phase 3) | 7 | 6 | 1 | 86% |
| Spec Register (Phase 4) | 13 | 13 | 0 | 100% |
| Sample Construction (Phase 5) | 5 | 4 | 1 | 80% |
| Variable Dictionary (Phase 6) | 22 | 20 | 2 | 91% |
| Pipeline/Outputs/Treatment (Phase 7) | 9 | 9 | 0 | 100% |
| Table Generator Entry (Phase 8) | 5 | 5 | 0 | 100% |
| Model-Family Addendum (Phase 9) | 6 | 6 | 0 | 100% |
| Quality Gates (Phase 10) | 10 | 9 | 1 | 90% |
| Cross-Reference Consistency (Phase 11) | 8 | 8 | 0 | 100% |
| **TOTAL** | **121** | **115** | **6** | **95%** |

---

## VERDICT

**PASS WITH NOTES**: The provenance document is substantially accurate and complete. Six minor issues were found, none of which affect the reproducibility or correctness of the documented regression pipeline. The failures are limited to: (1) a missing row-count attrition cascade, (2) a simplified TobinsQ formula description, (3) a slightly imprecise SalesGrowth division-by-zero description, and (4) minor structural omissions. No critical or high-severity errors.

---

## Phase 1: STRUCTURAL COMPLETENESS

Checked the creation prompt (`docs/Prompts/Suite Provenance Doc.txt`) for all required sections (A through L), then verified each exists in the provenance doc.

| Section | Required by Prompt | Present in Doc | Complete | Notes |
|---------|-------------------|----------------|----------|-------|
| A. Suite Identity | Yes | Yes | Yes | All YAML fields present |
| B. Model Specification | Yes | Yes | Yes | All 7 subsections present |
| B1. Regression Equation | Yes | Yes | Yes | Both contemporaneous and lead equations given |
| B2. Dependent Variable(s) | Yes | Yes | Yes | RDSales and RDSales_lead documented |
| B3. Independent Variable(s) | Yes | Yes | Yes | All 4 IVs documented |
| B4. Control Variables | Yes | Yes | Yes | Base (9) and Extended (Base+3) documented |
| B5. Fixed Effects | Yes | Yes | Yes | Industry/Firm entity + CalYr/CalYrQtr time FE |
| B6. Standard Errors | Yes | Yes | Yes | Clustered, cluster_entity=True |
| B7. Hypothesis Test | Yes | Yes | Yes | Two-tailed, no directional prediction |
| C. Spec Register | Yes | Yes | Yes | 12 rows matching 12 MODEL_SPECS |
| D. Sample Construction | Yes | Yes | Partial | D3 lacks per-spec row counts (marked UNVERIFIED) |
| D1. Population | Yes | Yes | Partial | Year range stated but total calls/firms not given |
| D2. Exclusion Criteria | Yes | Yes | Partial | FAIL: No row counts in attrition cascade |
| D3. Sample Counts per Spec | Yes | Yes | Partial | Marked UNVERIFIED with explanation |
| E. Variable Dictionary | Yes | Yes | Yes | 21 variables documented |
| F. Data Pipeline | Yes | Yes | Yes | F1-F3 all present and detailed |
| F1. Dependency Chain | Yes | Yes | Yes | 7-step chain documented |
| F2. Data Engines | Yes | Yes | Yes | 3 engines listed |
| F3. Merge Operations | Yes | Yes | Yes | All panel builder merges + lead/lag merges + match_to_manifest |
| G. Outputs | Yes | Yes | Yes | G1-G3 all present |
| G1. Stage 3 Outputs | Yes | Yes | Yes | 4 files listed |
| G2. Stage 4 Outputs | Yes | Yes | Yes | All output files listed |
| G3. Summary Statistics | Yes | Yes | Yes | 17 variables with labels |
| H. Outlier/Missing Treatment | Yes | Yes | Yes | H1-H3 all present |
| I. generate_all_tables.py Entry | Yes | Yes | Yes | Entry documented with verification table |
| J. Reproduction Commands | Yes | Yes | Yes | 3 commands listed |
| K. Model-Family Addendum | Yes | Yes | Yes | K1 filled for PanelOLS; K2-K6 marked N/A |
| L. Known Issues | Yes | Yes | Yes | 7 known issues documented |

**Phase 1 Result:** 25/26 PASS. D2 lacks actual row counts in the attrition cascade table (the creation prompt's template shows "Rows Before | Rows After | Dropped" columns, but the provenance doc describes filters as a step-description table without counts). The D3 section explicitly marks this [UNVERIFIED] with an explanation that exact counts require running the pipeline, which satisfies quality gate 10. However, strictly per the creation prompt template, row counts should be present.

---

## Phase 2: FACTUAL ACCURACY -- SECTION A (Suite Identity)

**A-1. Suite ID: `H16`**
- Provenance doc: `H16`
- Runner docstring line 6: `ID: econometric/test_h16_rd_sales`
- generate_all_tables.py: `"id": "H16"`
- **PASS**

**A-2. Title: "Speech Uncertainty and R&D Investment Intensity"**
- Runner docstring line 7-8: "Run H16 R&D Investment Intensity hypothesis test"
- Runner LaTeX caption (line 469): `Speech Uncertainty and R\&D Investment Intensity`
- generate_all_tables.py: `"caption": r"H16: Speech Uncertainty and R\&D Investment Intensity"`
- **PASS**

**A-3. Hypothesis: "Does managerial speech uncertainty during earnings calls affect R&D investment intensity?"**
- Runner docstring line 40-41: "H16: beta(uncertainty_var) != 0 -- no directional prediction"
- Consistent with the stated research question.
- **PASS**

**A-4. Direction: two-tailed (beta != 0)**
- Runner line 404: `p_two = float(model.pvalues.get(iv, np.nan))` -- uses two-tailed p-values directly
- Runner line 412: `stars = _sig_stars(p_two)` -- stars based on two-tailed p-values
- Runner docstring line 40-41: "H16: beta(uncertainty_var) != 0 -- no directional prediction"
- generate_all_tables.py: `"tail": "two"`, `"hyp_dir": None`
- **PASS**

**A-5. Model Family: PanelOLS**
- Runner line 81: `from linearmodels.panel import PanelOLS`
- Runner lines 363-378: PanelOLS constructor and PanelOLS.from_formula used
- **PASS**

**A-6. Estimator: `linearmodels.panel.PanelOLS`**
- Runner line 81: `from linearmodels.panel import PanelOLS`
- **PASS**

**A-7. Unit of Observation: call-level (individual earnings call)**
- Panel builder docstring line 23: "Unit of observation: the individual earnings call (file_name)"
- Runner docstring line 641: "Unit of observation: individual earnings call (call-level)"
- Panel builder merges on file_name (one row per call)
- **PASS**

**A-8. Panel Index: `(gvkey, cal_yr)` for cols 1-4, 7-10; `(gvkey, cal_yr_qtr)` for cols 5-6, 11-12**
- Runner line 334: `time_col = "cal_yr_qtr" if fe_type.endswith("_yq") else "cal_yr"`
- Runner line 355: `df_panel = df_prepared.set_index(["gvkey", time_col])`
- MODEL_SPECS: cols 5,6,11,12 have fe ending in `_yq`; cols 1-4,7-10 do not
- **PASS**

**A-9. Columns: 12**
- Runner MODEL_SPECS (lines 121-138): 12 entries (col 1 through col 12)
- **PASS**

**A-10. File paths exist**
- Runner: `src/f1d/econometric/run_h16_rd_sales.py` -- verified read successfully
- Panel builder: `src/f1d/variables/build_h16_rd_sales_panel.py` -- verified read successfully
- **PASS**

**Phase 2 Result:** 10/10 PASS.

---

## Phase 3: FACTUAL ACCURACY -- SECTION B (Model Specification)

**B1-CHECK: Regression Equation**
- The provenance doc shows the correct form: DV = b1*CEO_QA + b2*CEO_Pres + b3*Mgr_QA + b4*Mgr_Pres + Controls + alpha_i + delta_t + epsilon
- Runner line 346: `exog = KEY_IVS + controls` -- all 4 IVs + controls enter as regressors
- Runner lines 360-361/375-376: DV is the LHS; exog (IVs + controls) is the RHS; FE absorbed
- Contemporaneous uses RDSales, lead uses RDSales_lead -- correctly documented
- **PASS**

**B2-CHECK: Dependent Variable(s)**
- RDSales: Runner MODEL_SPECS cols 1-6 have `"dv": "RDSales"` -- confirmed
- RDSales_lead: Runner MODEL_SPECS cols 7-12 have `"dv": "RDSales_lead"` -- confirmed
- RDSales formula: CompustatEngine lines 969-978 show `xrdy_annual (Q4 YTD, fillna(0)) / saley_annual (Q4 YTD, fallback saleq); NaN if sales <= 0` -- matches doc
- RDSales_lead construction: panel builder `create_rdsales_lead()` lines 222-344 -- shift -1 by fyearq within gvkey, consecutive year validated -- matches doc
- **PASS**

**B3-CHECK: Independent Variable(s)**
- All 4 IVs listed in KEY_IVS (runner lines 94-99): CEO_QA_Uncertainty_pct, CEO_Pres_Uncertainty_pct, Manager_QA_Uncertainty_pct, Manager_Pres_Uncertainty_pct
- Source engine: LinguisticEngine (via CEOQAUncertaintyBuilder, CEOPresUncertaintyBuilder, ManagerQAUncertaintyBuilder, ManagerPresUncertaintyBuilder in panel builder)
- No centering/log/z-score: no transformation code found in runner or builders for these IVs
- Doc accurately states "No centering, log-transformation, or z-scoring is applied to the IVs."
- **PASS**

**B4-CHECK: Control Variables**
- BASE_CONTROLS (runner lines 103-113): Size, TobinsQ, ROA, BookLev, CashHoldings, CapexAt, DividendPayer, OCF_Volatility, Lagged_DV -- 9 items
- EXTENDED_CONTROLS (runner lines 115-119): BASE_CONTROLS + SalesGrowth, CashFlow, Volatility -- 12 items
- Provenance doc lists 9 base controls (including Lagged_DV) and 3 additional extended controls -- **matches code**
- Lagged_DV: runner lines 264-268 show `base_dv = dv.replace("_lead_qtr", "").replace("_lead", "")` then `lag_col = f"{base_dv}_lag"`, so Lagged_DV = RDSales_lag for both contemporaneous and lead specs -- doc correctly documents this
- RD_Intensity exclusion: runner line 101 confirms bad control note -- doc correctly documents this
- **PASS**

**B5-CHECK: Fixed Effects**
- Industry FE: runner lines 363-371, `other_effects=industry_data` (ff12_code), `entity_effects=False`, `time_effects=True` -- odd columns confirmed
- Firm FE: runner lines 375-378, `EntityEffects + TimeEffects` via `from_formula` -- even columns confirmed
- Time FE cal_yr: runner line 334, `time_col = "cal_yr"` for non-_yq specs (cols 1-4, 7-10)
- Time FE cal_yr_qtr: runner line 334, `time_col = "cal_yr_qtr"` for _yq specs (cols 5-6, 11-12)
- cal_yr and cal_yr_qtr derived from start_date via `build_cal_yr_qtr_index` (panel_utils.py line 195-218): `cal_yr = start_date.dt.year`, `cal_yr_qtr = cal_yr * 10 + start_date.dt.quarter` -- doc correctly states this
- **PASS**

**B6-CHECK: Standard Errors**
- Runner line 372: `model_obj.fit(cov_type="clustered", cluster_entity=True)` (industry FE specs)
- Runner line 378: `model_obj.fit(cov_type="clustered", cluster_entity=True)` (firm FE specs)
- Doc states: `cov_type="clustered"` with `cluster_entity=True` -- **matches code**
- **PASS**

**B7-CHECK: Hypothesis Test**
- Direction: Two-tailed (beta != 0)
- Runner line 404: `p_two = float(model.pvalues.get(iv, np.nan))` -- uses raw two-tailed p-values, no conversion
- Runner _sig_stars (lines 423-433): thresholds at 0.01, 0.05, 0.10 on two-tailed p-values
- Doc states: "Two-tailed p-values used directly from model.pvalues (no conversion)" -- **matches code**
- Doc line references "runner lines 400-414, 423-433" -- VERIFIED: line 400 starts the per-IV coefficient loop, line 414 is end of the loop body; lines 423-433 are the _sig_stars function

HOWEVER: The provenance doc's B7 says "Source: runner lines 400-414, 423-433." The actual lines in the runner for the p-value loop are 400-414 and _sig_stars is 423-433. These line numbers are accurate.

- **PASS**

**Phase 3 Result:** 7/7 PASS. Wait -- let me recheck the TobinsQ formula in B4.

The provenance doc B4 says: "TobinsQ: (cshoq * prccq + dlcq + dlttq) / atq; missing debt filled with 0"

Actual code (CompustatEngine lines 982-992):
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

Differences from the doc's formula:
1. The code clips negative debt to 0 (`.clip(lower=0)`) before fillna -- doc omits this
2. When BOTH dlcq and dlttq are NaN, debt_book = NaN (not 0) -- doc says "missing debt filled with 0" which is incomplete
3. TobinsQ is NaN when atq is missing/non-positive OR mktcap is missing -- doc does not mention these conditions explicitly in B4 (though the Variable Dictionary E row for TobinsQ does mention "NaN if atq missing/zero or mktcap missing")

This is a minor inaccuracy in B4's formula description. The Variable Dictionary E correctly notes the NaN conditions, but the B4 formula omits the clip(lower=0) and the both-NaN -> NaN logic.

**Revised B4 result:** FAIL (minor -- simplified TobinsQ formula description omits debt clipping and both-NaN->NaN logic)

**Phase 3 Revised Result:** 6/7 PASS, 1 FAIL.

---

## Phase 4: FACTUAL ACCURACY -- SECTION C (Spec Register)

Verified each row of the spec register against MODEL_SPECS in the runner (lines 121-138):

| Col | Doc DV | Code DV | Doc Entity FE | Code fe | Doc Time FE | Code time_col | Doc Controls | Code controls | Match |
|-----|--------|---------|---------------|---------|-------------|---------------|--------------|---------------|-------|
| 1 | RDSales | RDSales | Industry (FF12) | industry | Cal Year | cal_yr | Base | base | PASS |
| 2 | RDSales | RDSales | Firm | firm | Cal Year | cal_yr | Base | base | PASS |
| 3 | RDSales | RDSales | Industry (FF12) | industry | Cal Year | cal_yr | Extended | extended | PASS |
| 4 | RDSales | RDSales | Firm | firm | Cal Year | cal_yr | Extended | extended | PASS |
| 5 | RDSales | RDSales | Industry (FF12) | industry_yq | Cal Year-Quarter | cal_yr_qtr | Extended | extended | PASS |
| 6 | RDSales | RDSales | Firm | firm_yq | Cal Year-Quarter | cal_yr_qtr | Extended | extended | PASS |
| 7 | RDSales_lead | RDSales_lead | Industry (FF12) | industry | Cal Year | cal_yr | Base | base | PASS |
| 8 | RDSales_lead | RDSales_lead | Firm | firm | Cal Year | cal_yr | Base | base | PASS |
| 9 | RDSales_lead | RDSales_lead | Industry (FF12) | industry | Cal Year | cal_yr | Extended | extended | PASS |
| 10 | RDSales_lead | RDSales_lead | Firm | firm | Cal Year | cal_yr | Extended | extended | PASS |
| 11 | RDSales_lead | RDSales_lead | Industry (FF12) | industry_yq | Cal Year-Quarter | cal_yr_qtr | Extended | extended | PASS |
| 12 | RDSales_lead | RDSales_lead | Firm | firm_yq | Cal Year-Quarter | cal_yr_qtr | Extended | extended | PASS |

- Row count: 12 rows in doc, 12 entries in MODEL_SPECS -- **matches**
- No specs in code missing from table
- No specs in table absent from code

**Phase 4 Result:** 13/13 PASS.

---

## Phase 5: FACTUAL ACCURACY -- SECTION D (Sample Construction)

**D1-CHECK: Population**
- Doc states starting dataset is `master_sample_manifest.parquet` -- runner line 212-214 confirms
- Doc states year range 2002-2018, configurable via config/project.yaml -- consistent with project scope (112,968 calls, 2,429 firms)
- Doc does NOT state total calls or total firms explicitly -- the creation prompt template suggests "Total calls, unique firms, year range" but the doc only gives year range
- **PASS** (year range correct; total counts not given but not strictly required by creation prompt as mandatory fields -- the prompt says "Total calls, unique firms, year range" as a suggestion)

**D2-CHECK: Exclusion Criteria**
- Doc lists 5 steps in order: full manifest -> main sample filter -> DV non-missing -> complete case -> min calls per firm
- Runner code confirms this order:
  - filter_main_sample() at line 757 (exclude FF12 codes 8, 11)
  - prepare_regression_data() lines 289-306: drop DV NaN -> complete case -> min 5 calls per firm
- However, the provenance doc's D2 table has NO ROW COUNTS (the creation prompt template shows "Rows Before | Rows After | Dropped" columns)
- The runner does produce an attrition table (lines 812-821) but the provenance doc presents the steps descriptively without counts
- **FAIL** -- The creation prompt's template for D2 explicitly shows row counts are expected in the attrition cascade. The doc omits them.

**D3-CHECK: Sample Counts per Spec**
- Doc explicitly marks this [UNVERIFIED] with explanation: "exact counts require running the pipeline"
- This satisfies quality gate 10 (UNVERIFIED claims have explanations)
- **PASS**

**D-ADDITIONAL: Attrition stage description accuracy**
- The runner's attrition stages (lines 814-820) are:
  1. "Master manifest (full panel)" -- full_panel_n
  2. "Main sample filter (excl Finance/Utility)" -- main_panel_n
  3. "After nonpositive-sales exclusion (RDSales NaN)" -- panel["RDSales"].notna().sum()
  4. "After lead filter (col 5-8 only)" -- panel["RDSales_lead"].notna().sum()
  5. "After complete-case + min-calls (col 1)" -- first_meta.get("n_obs", 0)
- Note: runner step 4 says "col 5-8 only" but actually lead DV is used for cols 7-12, not 5-8. This is a bug in the runner's attrition label, not in the provenance doc.
- The provenance doc's D2 steps are a clean abstraction of the per-spec filtering logic (prepare_regression_data), which is accurate.
- **PASS** (for the doc's description accuracy)

**D-ADDITIONAL: Min calls threshold**
- Doc says ">= 5 calls per gvkey" -- runner line 140: `MIN_CALLS_PER_FIRM = 5`, line 301: `firm_counts >= MIN_CALLS_PER_FIRM`
- **PASS**

**Phase 5 Result:** 4/5 PASS, 1 FAIL (D2 missing row counts in attrition cascade).

---

## Phase 6: FACTUAL ACCURACY -- SECTION E (Variable Dictionary)

Checked every row in the Variable Dictionary against code.

**DVs:**

| Variable | Name Match | Formula Correct | Source Correct | Winsorize Correct | Timing Correct | Result |
|----------|-----------|-----------------|----------------|-------------------|----------------|--------|
| RDSales | PASS -- exact match with code | PASS -- xrdy_annual fillna(0) / saley_annual (fallback saleq); NaN if sales <= 0 matches CompustatEngine lines 969-978 | PASS -- CompustatEngine: xrdy, saley, saleq | PASS -- 1%/99% by fiscal year; RDSales is in COMPUSTAT_COLS and not in skip_winsorize | PASS -- contemporaneous | PASS |
| RDSales_lead | PASS -- exact match | PASS -- next consecutive fiscal year's RDSales, latest call per (gvkey, fyearq_int), shift -1 -- matches panel builder create_rdsales_lead() | PASS -- derived from RDSales via panel builder | PASS -- "Inherited from RDSales" (winsorization applied to base RDSales before lead construction) | PASS -- lead (t+1 fiscal year) | PASS |
| RDSales_lag | PASS -- exact match | PASS -- prior consecutive fiscal year's RDSales, shift +1 -- matches panel builder create_rdsales_lag() | PASS | PASS -- inherited from RDSales | PASS -- lag (t-1) | PASS |

**IVs:**

| Variable | Name Match | Formula Correct | Source Correct | Winsorize Correct | Timing Correct | Result |
|----------|-----------|-----------------|----------------|-------------------|----------------|--------|
| CEO_QA_Uncertainty_pct | PASS | PASS -- (uncertainty word count / total word count) * 100 in CEO Q&A section | PASS -- LinguisticEngine | PASS -- "No (bounded [0,100] by construction)" | PASS | PASS |
| CEO_Pres_Uncertainty_pct | PASS | PASS | PASS | PASS | PASS | PASS |
| Manager_QA_Uncertainty_pct | PASS | PASS | PASS | PASS | PASS | PASS |
| Manager_Pres_Uncertainty_pct | PASS | PASS | PASS | PASS | PASS | PASS |

**Controls:**

| Variable | Name Match | Formula Correct | Source Correct | Winsorize Correct | Timing Correct | Result |
|----------|-----------|-----------------|----------------|-------------------|----------------|--------|
| Size | PASS | PASS -- ln(atq); NaN if atq <= 0 matches CompustatEngine line 938 | PASS | PASS -- in COMPUSTAT_COLS, not in skip_winsorize | PASS | PASS |
| TobinsQ | PASS | **FAIL (minor)** -- Doc says "(cshoq * prccq + dlcq.fillna(0) + dlttq.fillna(0)) / atq; NaN if atq missing/zero or mktcap missing". Code actually: (1) clips negative debt to 0 before fillna, (2) sets debt_book=NaN when BOTH dlcq and dlttq are NaN, (3) requires atq > 0 AND atq notna AND mktcap notna. The clip(lower=0) and both-NaN logic are omitted. | PASS | PASS | PASS | FAIL (minor) |
| ROA | PASS | PASS -- iby_annual / avg_assets where avg_assets = (atq_t + atq_{t-1}) / 2; matches CompustatEngine lines 954-964 | PASS | PASS | PASS | PASS |
| BookLev | PASS | PASS -- (dlcq.fillna(0) + dlttq.fillna(0)) / atq matches CompustatEngine line 943 | PASS | PASS | PASS | PASS |
| CashHoldings | PASS | PASS -- cheq / atq matches CompustatEngine line 981 | PASS | PASS | PASS | PASS |
| CapexAt | PASS | PASS -- capxy_annual / atq_annual_lag1; NaN if lagged atq <= 0 matches CompustatEngine lines 994-1000 | PASS | PASS | PASS | PASS |
| DividendPayer | PASS | PASS -- 1 if dvy_annual > 0, else 0 matches CompustatEngine lines 1004-1007 | PASS | PASS -- "Not winsorized (binary)" and DividendPayer is in skip_winsorize | PASS | PASS |
| OCF_Volatility | PASS | PASS -- Rolling 5-yr std (min 3 yrs) of (oancfy / atq_{t-1}) per gvkey, Q4-only annual values | PASS | PASS | PASS | PASS |
| SalesGrowth | PASS | **FAIL (minor)** -- Doc says "NaN if gap year or lagged sale == 0". The code uses `abs(saley_{t-1})` in the denominator. The doc should say "NaN if gap year or lagged abs(sale) == 0" to be precise. Additionally, the CompustatEngine code computes SalesGrowth inside `_compute_biddle_residual` where the exact denominator is `sale_lag.abs()`. Doc description is 99% correct but the "lagged sale == 0" condition should mention the absolute value. | PASS | PASS -- "1%/99% by fiscal year (inside Biddle residual computation)" and SalesGrowth is in skip_winsorize (no double-winsorization) | PASS | FAIL (minor) |
| CashFlow | PASS | PASS -- oancfy / avg_assets with fallback to atq_t when atq_{t-1} missing | PASS | PASS -- similar to SalesGrowth, winsorized inside Biddle residual, in skip_winsorize | PASS | PASS |
| Volatility | PASS | PASS -- std(daily_ret) * sqrt(252) * 100 over [prev_call + 5d, call - 5d]; min 10 trading days | PASS -- CRSPEngine | PASS -- "No (computed at builder level)" | PASS | PASS |
| Lagged_DV | PASS | PASS -- RDSales_lag (prior consecutive fiscal year's RDSales); dynamically assigned in prepare_regression_data() -- matches runner lines 264-268 | PASS | PASS -- "Inherited from RDSales" | PASS | PASS |

**FE columns:**

| Variable | Name Match | Description Correct | Source Correct | Result |
|----------|-----------|--------------------|--------------------|--------|
| gvkey | PASS | PASS -- Compustat permanent entity identifier, zero-padded to 6 chars | PASS | PASS |
| ff12_code | PASS | PASS -- Fama-French 12-industry classification | PASS | PASS |
| cal_yr | PASS | PASS -- start_date.dt.year (from call date) matches panel_utils.py line 215 | PASS | PASS |
| cal_yr_qtr | PASS | PASS -- cal_yr * 10 + start_date.dt.quarter matches panel_utils.py line 217 | PASS | PASS |

**Completeness check:**
- All variables from MODEL_SPECS (DVs + IVs): present in dictionary -- PASS
- All variables from BASE_CONTROLS: present in dictionary -- PASS
- All variables from EXTENDED_CONTROLS: present in dictionary -- PASS
- All FE columns (gvkey, ff12_code, cal_yr, cal_yr_qtr): present in dictionary -- PASS
- No variable used in code is missing from dictionary -- PASS

**Phase 6 Result:** 20/22 PASS, 2 FAIL (minor: TobinsQ formula simplified, SalesGrowth denominator description).

---

## Phase 7: FACTUAL ACCURACY -- SECTIONS F, G, H

### F-CHECK: Data Pipeline

**F1 Dependency Chain:**
- 7-step chain from raw inputs to table generation
- Raw inputs: Compustat quarterly, linguistic variables, CRSP daily returns, manifest, FF48 Siccodes -- all confirmed used by the engines
- Engine loading: CompustatEngine, LinguisticEngine, CRSPEngine -- confirmed in panel builder imports and builder dict
- Panel builder: merge on file_name, left join, zero-row-delta enforced (builder lines 192-200)
- Runner loading: load panel parquet with explicit column list (runner lines 219-233), build cal_yr_qtr index (line 239)
- Sample filtering: main sample filter -> per-spec DV NaN -> complete case -> min calls (runner lines 757, 289-306)
- Regression: 12 PanelOLS models, firm-clustered SEs, drop_absorbed=True (runner lines 363-378)
- Table generation: runner writes its own LaTeX table + generate_all_tables.py entry
- **PASS**

**F2 Data Engines:**
- CompustatEngine: provides RDSales, Size, TobinsQ, ROA, BookLev, CashHoldings, CapexAt, DividendPayer, OCF_Volatility, RD_Intensity, CashFlow, SalesGrowth -- confirmed in COMPUSTAT_COLS and builder dict
- LinguisticEngine: provides 4 uncertainty measures -- confirmed via builder imports
- CRSPEngine: provides Volatility -- confirmed via VolatilityBuilder
- **PASS**

**F3 Merge Operations:**
- Panel builder merges: all on file_name, left join, zero-row-delta enforced -- confirmed in builder code lines 164-200
- Lead/lag merges: on (gvkey, fyearq_int), left join, row-delta enforced -- confirmed in create_rdsales_lead (line 329) and create_rdsales_lag (line 401)
- CompustatEngine match_to_manifest: merge_asof backward on (gvkey, start_date/datadate) -- standard engine pattern
- All merges documented in doc's F3 tables -- **PASS**

### G-CHECK: Outputs

**G1 Stage 3 (Panel Builder):**
- `h16_rd_sales_panel.parquet` -- builder line 484-485 -- confirmed
- `summary_stats.csv` -- builder line 493-494 -- confirmed
- `run_manifest.json` -- builder lines 498-508 -- confirmed
- `report_step3_h16_rd_sales.md` -- builder line 551-553 -- confirmed
- Output directory: `outputs/variables/h16_rd_sales/{timestamp}/` -- builder line 430 -- confirmed
- **PASS**

**G2 Stage 4 (Runner):**
- `h16_rd_sales_table.tex` -- runner line 580 -- confirmed
- `model_diagnostics.csv` -- runner line 620 -- confirmed
- `summary_stats.csv` -- runner line 778 -- confirmed
- `summary_stats.tex` -- runner line 779 -- confirmed
- `sample_attrition.csv` -- runner line 821 (via generate_attrition_table) -- confirmed
- `sample_attrition.tex` -- runner line 821 (generate_attrition_table produces both csv and tex) -- confirmed
- `regression_results_col{1-12}.txt` -- runner lines 604-614 -- confirmed
- `report_step4_H16.md` -- runner line 706 -- confirmed
- `run_manifest.json` -- runner lines 825-835 -- confirmed
- Output directory: `outputs/econometric/h16_rd_sales/{timestamp}/` -- runner line 725 -- confirmed
- **PASS**

Note: The runner docstring (line 58) omits `sample_attrition.tex` from the output list, but the code does produce it. The provenance doc correctly lists both .csv and .tex.

**G3 Summary Statistics:**
- SUMMARY_STATS_VARS (runner lines 150-171): 17 variables listed -- doc lists all 17 with matching labels
- Metrics: N, Mean, SD, Min, P25, Median, P75, Max via `make_summary_stats_table` -- confirmed
- **PASS**

### H-CHECK: Outlier/Missing Treatment

**H1 Winsorization:**
- Level: 1%/99% by fiscal year (fyearq) -- CompustatEngine `_winsorize_by_year` at line 439, applied per fyearq at lines 1133-1136
- Min 10 obs per year-group: `_winsorize_by_year` line 440: `min_obs: int = 10` -- confirmed
- Applied to: All COMPUSTAT_COLS except skip_winsorize = {DividendPayer, CashFlow, SalesGrowth, fqtr} -- lines 1123-1129. RDSales IS in COMPUSTAT_COLS (line 133) and NOT in skip_winsorize, so it IS winsorized.
- Doc correctly states: "Applied to: All COMPUSTAT_COLS except DividendPayer (binary), CashFlow, SalesGrowth (already winsorized per-year inside _compute_biddle_residual), and fqtr (identifier). This includes: Size, TobinsQ, ROA, BookLev, CashHoldings, CapexAt, OCF_Volatility, RDSales"
- Not applied to: Linguistic IVs (not computed by CompustatEngine) -- correct
- Not applied to: Volatility (computed by CRSPEngine/builder, not in COMPUSTAT_COLS) -- correct
- Not applied to: DividendPayer (in skip_winsorize) -- correct
- **PASS**

**H2 Missing Data:**
- Complete-case deletion per-spec in prepare_regression_data: runner line 295-296 (`df[required].notna().all(axis=1)`)
- Inf/-Inf replaced with NaN: runner line 281 (`df.replace([np.inf, -np.inf], np.nan)`) and CompustatEngine lines 1109-1110
- Missing xrd set to 0: CompustatEngine line 977 (`fillna(0)`) -- confirmed
- Nonpositive sales -> NaN: CompustatEngine line 978 (`np.where(sale_for_rd > 0, ..., np.nan)`) -- confirmed
- **PASS**

**H3 Transformations:**
- Size: ln(atq) -- confirmed
- DividendPayer: binary 0/1 -- confirmed
- RDSales lead/lag: fiscal-year-based shifting with consecutive-year validation -- confirmed
- "No other centering, z-scoring, or scaling applied" -- no evidence of other transformations in runner or builders
- **PASS**

**Phase 7 Result:** 9/9 PASS.

---

## Phase 8: FACTUAL ACCURACY -- SECTION I (Table Generator Entry)

Verified the generate_all_tables.py entry (around lines 377-390) against the provenance doc:

| Field | Provenance Doc | generate_all_tables.py | Match |
|-------|---------------|------------------------|-------|
| id | H16 | "H16" | PASS |
| dir | "h16_rd_sales/2026-03-27_095019" | "h16_rd_sales/2026-03-27_095019" | PASS |
| cols | 12 | 12 | PASS |
| dvs | [("RDSales", 6), ("RDSales\_lead", 6)] | [("RDSales", 6), (r"RDSales\_lead", 6)] | PASS |
| tail | "two" | "two" | PASS |
| hyp_dir | None | None | PASS |

**Verification table in provenance doc:**
- tail: "two" matches runner's two-tailed p-value usage -- PASS
- hyp_dir: None matches runner's no directional prediction -- PASS
- cols: 12 matches len(MODEL_SPECS) -- PASS
- dvs: RDSales (6 cols) + RDSales_lead (6 cols) matches MODEL_SPECS -- PASS

**Note about key_vars/key_tails:** Doc correctly notes "This entry does not have key_vars or key_tails fields." Verified: the generate_all_tables.py entry for H16 does not have these fields. PASS.

**Phase 8 Result:** 5/5 PASS.

---

## Phase 9: FACTUAL ACCURACY -- SECTION K (Model-Family Addendum)

**Model family identified in Section A:** PanelOLS

**K1 PanelOLS Specifics (filled):**

| Claim | Code Reference | Verified |
|-------|---------------|----------|
| Industry FE: absorbed via `other_effects=df_panel["ff12_code"]`, `entity_effects=False`, `time_effects=True` | Runner lines 363-371 | PASS |
| Firm FE: absorbed via `EntityEffects` in `PanelOLS.from_formula()` | Runner lines 376-377 | PASS |
| Time effects: `time_effects=True` (constructor) or `TimeEffects` (formula) | Runner lines 367, 376 | PASS |
| Time index: `cal_yr` (cols 1-4, 7-10) or `cal_yr_qtr` (cols 5-6, 11-12) via `df_panel.set_index(["gvkey", time_col])` | Runner lines 334, 355 | PASS |
| `drop_absorbed=True` for all specs | Runner lines 369, 377 | PASS |
| `check_rank=False` for industry FE specs; default for firm FE specs | Runner line 370 (industry: check_rank=False); firm FE via from_formula (line 377) does not set check_rank, so default applies | PASS |

**K2-K6:** All marked N/A -- correct, since this is a PanelOLS suite.

**Phase 9 Result:** 6/6 PASS.

---

## Phase 10: QUALITY GATE CHECKLIST

| # | Quality Gate | Met? | Evidence |
|---|-------------|------|----------|
| 1 | Every variable in every regression spec appears in Variable Dictionary with explicit formula and source engine | **YES** | Phase 6 verified all 21 variables (2 DVs, 1 lagged DV, 4 IVs, 12 controls, 4 FE columns). All have formulas and source engines. |
| 2 | The model equation matches what the code actually estimates | **YES** | Phase 3 B1-CHECK confirmed the equation matches runner's exog + DV + FE structure. |
| 3 | The specification register accounts for every model column | **YES** | Phase 4 confirmed all 12 MODEL_SPECS are in the register with correct attributes. |
| 4 | The attrition cascade has row counts for each filter step | **NO** | Phase 5 D2-CHECK: The attrition cascade in D2 describes filter steps but does not include row counts. D3 marks exact counts as [UNVERIFIED]. |
| 5 | The tail test direction matches between runner code and generate_all_tables.py | **YES** | Phase 8: runner uses two-tailed p-values; generate_all_tables.py has `"tail": "two"`. |
| 6 | The FE specification matches between docstring, code, and this document | **YES** | Phase 3 B5-CHECK: FE types, columns, and absorption methods all match across docstring, code, and provenance doc. |
| 7 | Every merge in the panel builder is documented with join keys and type | **YES** | Phase 7 F3-CHECK: all file_name merges, lead/lag merges, and match_to_manifest merges documented. |
| 8 | The output file list matches what the runner actually writes | **YES** | Phase 7 G-CHECK: all output files verified against code write operations. |
| 9 | The model-family addendum is filled for the correct family only | **YES** | Phase 9: K1 (PanelOLS) is filled; K2-K6 are N/A. |
| 10 | Any claim marked [UNVERIFIED] has an explanation of what blocks verification | **YES** | D3 marked [UNVERIFIED] with explanation: "exact counts require running the pipeline; the attrition table in the latest output captures col 1 counts only." |

**Phase 10 Result:** 9/10 PASS, 1 FAIL (quality gate 4: attrition cascade lacks row counts).

---

## Phase 11: CROSS-REFERENCE CONSISTENCY

| Check | Items Compared | Consistent? | Notes |
|-------|---------------|-------------|-------|
| 1. DVs in B2 match DVs in C | B2: RDSales, RDSales_lead; C: cols 1-6 RDSales, cols 7-12 RDSales_lead | **YES** | |
| 2. DVs in C match DVs in I | C: RDSales (6), RDSales_lead (6); I: ("RDSales", 6), ("RDSales_lead", 6) | **YES** | |
| 3. Controls in B4 match variables in E | B4 lists 9 base + 3 extended = 12 controls; E has entries for all 12 + Lagged_DV | **YES** | |
| 4. Column count in A matches rows in C | A: 12 columns; C: 12 rows | **YES** | |
| 5. Column count in A matches "cols" in I | A: 12; I: cols=12 | **YES** | |
| 6. Tail direction: A matches B7 matches I | A: two-tailed; B7: two-tailed; I: tail="two" | **YES** | |
| 7. FE in B5 matches C matches K | B5: Industry(FF12)/Firm entity + CalYr/CalYrQtr time; C: same pattern; K1: same | **YES** | |
| 8. Panel index in A matches set_index in K | A: (gvkey, cal_yr) or (gvkey, cal_yr_qtr); K1: df_panel.set_index(["gvkey", time_col]) | **YES** | |

**Phase 11 Result:** 8/8 PASS. No internal contradictions found.

---

## FAILURES (detailed)

| Phase | Check | Provenance Doc Claims | Actual Code Says | Severity | Fix Required |
|-------|-------|----------------------|-----------------|----------|-------------|
| 3 (B4) | TobinsQ formula | "(cshoq * prccq + dlcq.fillna(0) + dlttq.fillna(0)) / atq; NaN if atq missing/zero or mktcap missing" | Code clips negative debt to 0 first (.clip(lower=0)), and sets debt_book=NaN when BOTH dlcq AND dlttq are NaN (not fillna(0)). Requires atq > 0 AND atq notna AND mktcap notna. | Minor | Amend TobinsQ formula in B4 and E to note clip(lower=0) and both-NaN->NaN debt logic |
| 5 (D2) | Attrition cascade row counts | Describes filter steps without row counts | Runner produces actual attrition table with counts (lines 812-821); creation prompt template shows row count columns | Minor | Add [UNVERIFIED] row counts or note that counts are available in runner output |
| 6 (E) | TobinsQ variable dictionary | Same as B4 -- formula simplified | Same as B4 | Minor | Same fix as B4 |
| 6 (E) | SalesGrowth denominator | "NaN if gap year or lagged sale == 0" | Code uses `abs(saley_{t-1})` as denominator; NaN when abs(lagged sale) == 0 | Minor | Change to "NaN if gap year or abs(lagged sale) == 0" |
| 10 (QG4) | Attrition cascade has row counts | No row counts in D2 | Runner produces counts; creation prompt expects counts | Minor | Same as D2 fix above |

---

## CORRECTIONS REQUIRED

1. **Section B4, TobinsQ formula row:**
   - **Current:** `(cshoq * prccq + dlcq + dlttq) / atq; missing debt filled with 0`
   - **Should be:** `(cshoq * prccq + dlcq.clip(0).fillna(0) + dlttq.clip(0).fillna(0)) / atq; debt_book = NaN when BOTH dlcq and dlttq missing; NaN if atq missing/zero or mktcap missing`
   - **Code reference:** `_compute_and_winsorize()` in `src/f1d/shared/variables/_compustat_engine.py`, lines 982-992

2. **Section E, TobinsQ variable dictionary row, Formula column:**
   - **Current:** `(cshoq * prccq + dlcq.fillna(0) + dlttq.fillna(0)) / atq; NaN if atq missing/zero or mktcap missing`
   - **Should be:** `(cshoq * prccq + dlcq.clip(0).fillna(0) + dlttq.clip(0).fillna(0)) / atq; debt_book NaN if both dlcq and dlttq missing; NaN if atq missing/zero or mktcap missing`
   - **Code reference:** Same as above

3. **Section E, SalesGrowth variable dictionary row, Formula column:**
   - **Current:** `NaN if gap year or lagged sale == 0`
   - **Should be:** `NaN if gap year or abs(lagged sale) == 0`
   - **Code reference:** `_compute_biddle_residual()` in `src/f1d/shared/variables/_compustat_engine.py`, SalesGrowth denominator uses `sale_lag.abs()`

4. **Section D2, Exclusion Criteria table:**
   - **Current:** Table with Step/Filter/Description columns only
   - **Should add:** Either (a) row counts from a live pipeline run, or (b) an explicit [UNVERIFIED: row counts require running the pipeline] note within D2 itself (currently only D3 has this note)
   - **Code reference:** Runner lines 812-821 produce attrition table with counts

---

## ADDITIONAL OBSERVATIONS (non-failures)

1. **Runner docstring minor count error:** Line 28 says "Base Controls (8)" but BASE_CONTROLS has 9 items including Lagged_DV. The provenance doc correctly says "Base Controls (9, including Lagged_DV)." This is a docstring issue, not a provenance doc issue.

2. **Runner attrition label error:** Line 818 says "After lead filter (col 5-8 only)" but the lead DV (RDSales_lead) is used for cols 7-12, not 5-8. This is a bug in the runner's attrition stage label, not in the provenance doc.

3. **Docstring omits sample_attrition.tex:** Runner docstring output list (line 52-59) lists sample_attrition.csv but not sample_attrition.tex. The code produces both. The provenance doc correctly lists both.

4. **Known Issues section (L) is thorough:** All 7 documented issues are verified against code and accurately describe real quirks of the pipeline.

5. **The provenance doc's line number references are accurate:** All checked line references (MODEL_SPECS 121-138, SE clustering 372/378, p-value 400-414, _sig_stars 423-433, PanelOLS constructor 363-371, from_formula 376-377, drop_absorbed 369/377, check_rank 370, build_cal_yr_qtr_index panel_utils.py line 195) match the actual code line numbers.
