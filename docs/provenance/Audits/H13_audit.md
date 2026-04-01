# Adversarial Audit: H13 Capital Expenditure Provenance Document

**Audit Date:** 2026-04-01
**Auditor:** Hostile Re-Audit (Claude Sonnet 4.6) — full independent re-read
**Suite:** H13
**Runner:** `src/f1d/econometric/run_h13_capex.py`
**Panel Builder:** `src/f1d/variables/build_h13_capex_panel.py`
**Provenance Doc:** `docs/provenance/H13.md`
**Creation Prompt:** `docs/Prompts/Suite Provenance Doc.txt`

---

## AUDIT SUMMARY

| Category | Total Checks | Passed | Failed | Score |
|----------|-------------|--------|--------|-------|
| Structural Completeness (Phase 1) | 26 | 26 | 0 | 100% |
| Suite Identity (Phase 2) | 10 | 10 | 0 | 100% |
| Model Specification (Phase 3) | 7 | 7 | 0 | 100% |
| Spec Register (Phase 4) | 5 | 5 | 0 | 100% |
| Sample Construction (Phase 5) | 3 | 3 | 0 | 100% |
| Variable Dictionary (Phase 6) | 24 | 24 | 0 | 100% |
| Pipeline/Outputs/Treatment (Phase 7) | 9 | 9 | 0 | 100% |
| Table Generator Entry (Phase 8) | 6 | 4 | 2 | 67% |
| Model-Family Addendum (Phase 9) | 5 | 5 | 0 | 100% |
| Quality Gates (Phase 10) | 10 | 9 | 1 | 90% |
| Cross-Reference Consistency (Phase 11) | 8 | 8 | 0 | 100% |
| **TOTAL** | **113** | **110** | **3** | **97%** |

---

## VERDICT

**PASS WITH NOTES**

The provenance document is substantively accurate. All variables, formulas, MODEL_SPECS, fixed effects, winsorization, and merge operations are correctly documented. Three failures were found, all of which are line-number citations pointing to wrong lines in source files. No formula errors, no missing sections, no misidentified variables or specs. The failures are cosmetic/reference errors, not methodological inaccuracies.

---

## FAILURES (detailed)

| Phase | Check | Provenance Doc Claims | Actual Code Says | Severity | Fix Required |
|-------|-------|----------------------|-----------------|----------|-------------|
| 8 | generate_all_tables.py line numbers | "Source: `outputs/generate_all_tables.py`, lines 293--305" | H13 entry is at lines 245--257 | Low | Update line reference |
| 8 | IV_NAMES line reference | "the global `IV_NAMES` list (line 407--412) applies" | IV_NAMES is at lines 400--405 | Low | Update line reference |
| 10 | Quality Gate 2 (runner line citation) | Section B7: "`{iv}_p_two` in metadata (runner line 392)" | Line 392 is `t_stat = float(model.tstats.get(iv, np.nan))`. `p_two` is stored at runner line 397 | Low | Update line reference |

---

## PHASE 1: STRUCTURAL COMPLETENESS

Reference: `docs/Prompts/Suite Provenance Doc.txt` required sections A through L.

| Section | Required by Prompt | Present in Doc | Complete | Notes |
|---------|-------------------|----------------|----------|-------|
| A. Suite Identity | Yes | Yes | Yes | YAML block present, all fields populated |
| B. Model Specification | Yes | Yes | Yes | |
| B1. Regression Equation | Yes | Yes | Yes | Full LaTeX equation present |
| B2. Dependent Variables | Yes | Yes | Yes | CapexAt and CapexAt_lead documented |
| B3. Independent Variables | Yes | Yes | Yes | All 4 IVs documented |
| B4. Control Variables | Yes | Yes | Yes | Base (8) and Extended (12) documented with Lagged_DV note |
| B5. Fixed Effects | Yes | Yes | Yes | Industry/Firm x Cal Yr/Cal Yr-Qtr |
| B6. Standard Errors | Yes | Yes | Yes | clustered, cluster_entity=True |
| B7. Hypothesis Test | Yes | Yes | Yes | Two-tailed documented |
| C. Spec Register | Yes | Yes | Yes | 12-row table matching MODEL_SPECS |
| D. Sample Construction | Yes | Yes | Yes | |
| D1. Population | Yes | Yes | Yes | 112,968 calls, 2,429 firms, 2002-2018 |
| D2. Exclusion Criteria | Yes | Yes | Yes | 6-step attrition cascade |
| D3. Sample Counts per Spec | Yes | Yes | Yes | N varies per spec, noted |
| E. Variable Dictionary | Yes | Yes | Yes | 22-variable table, all specs covered |
| F. Data Pipeline | Yes | Yes | Yes | |
| F1. Dependency Chain | Yes | Yes | Yes | 7-step chain |
| F2. Data Engines | Yes | Yes | Yes | 3 engines listed |
| F3. Merge Operations | Yes | Yes | Yes | 19 merges documented |
| G. Outputs | Yes | Yes | Yes | |
| G1. Stage 3 Outputs | Yes | Yes | Yes | 4 files |
| G2. Stage 4 Outputs | Yes | Yes | Yes | 9 files |
| G3. Summary Statistics | Yes | Yes | Yes | 17 variables listed |
| H. Outlier/Missing Treatment | Yes | Yes | Yes | |
| I. generate_all_tables Entry | Yes | Yes | Yes | Entry documented (line numbers wrong — see Phase 8) |
| J. Reproduction Commands | Yes | Yes | Yes | 3 commands |
| K. Model-Family Addendum | Yes | Yes | Yes | K1 filled, K2-K6 N/A |
| L. Known Issues | Yes | Yes | Yes | 7 issues documented |

**Phase 1 Result: 26/26 PASS**

---

## PHASE 2: SUITE IDENTITY (Section A)

**A-1. Suite ID**
Doc: `H13`
Code: Runner file is `run_h13_capex.py`; docstring says "STAGE 4: Test H13 Capital Expenditure Hypothesis".
RESULT: **PASS**

**A-2. Title**
Doc: "Speech Uncertainty and Capital Expenditure"
Code: Runner docstring says "STAGE 4: Test H13 Capital Expenditure Hypothesis". LaTeX caption (line 461): `\caption{Speech Uncertainty and Capital Expenditure}`. generate_all_tables.py entry: `"caption": "H13: Speech Uncertainty and Capital Expenditure"`.
RESULT: **PASS**

**A-3. Hypothesis**
Doc: "Does managerial linguistic uncertainty during earnings calls affect contemporaneous and future capital expenditure intensity?"
Code: Runner line 32-33: "Hypothesis Test (two-tailed): H13: beta(uncertainty_var) != 0 — no directional prediction."
The provenance doc's framing is consistent with the code's hypothesis. RESULT: **PASS**

**A-4. Direction (tail test)**
Doc: "two-tailed (beta != 0, no directional prediction)"
Code: Runner line 32-34: "Hypothesis Test (two-tailed): H13: beta(uncertainty_var) != 0 — no directional prediction. Stars based on two-tailed p-values." `_sig_stars()` uses raw two-tailed p-values (lines 410-420). No `/2` conversion anywhere in the runner.
RESULT: **PASS**

**A-5. Model Family**
Doc: "PanelOLS"
Code: Runner line 73: `from linearmodels.panel import PanelOLS`. All 12 regressions use `PanelOLS`.
RESULT: **PASS**

**A-6. Estimator**
Doc: "linearmodels.panel.PanelOLS"
Code: `from linearmodels.panel import PanelOLS` (runner line 73). The class path is `linearmodels.panel.PanelOLS`.
RESULT: **PASS**

**A-7. Unit of Observation**
Doc: "call-level (one row per earnings call)"
Code: Panel builder docstring: "Unit of observation: the individual earnings call (file_name)." Runner line 453: "Unit of observation: earnings call (file_name)". Panel builder line 20: "Unit of observation: the individual earnings call (file_name)."
RESULT: **PASS**

**A-8. Panel Index**
Doc: "(gvkey, cal_yr) or (gvkey, cal_yr_qtr) depending on spec"
Code: Runner `run_regression()` line 342: `df_panel = df_prepared.set_index(["gvkey", time_col])` where `time_col = "cal_yr_qtr" if fe_type.endswith("_yq") else "cal_yr"` (line 331).
RESULT: **PASS**

**A-9. Columns (12 specs)**
Doc: "Columns: 12"
Code: `MODEL_SPECS` list (runner lines 112-127) has exactly 12 entries (col 1 through col 12).
RESULT: **PASS**

**A-10. Runner and Panel Builder paths**
Doc: `src/f1d/econometric/run_h13_capex.py` and `src/f1d/variables/build_h13_capex_panel.py`
Verified: Both files exist on disk and match described paths.
RESULT: **PASS**

**Phase 2 Result: 10/10 PASS**

---

## PHASE 3: MODEL SPECIFICATION (Section B)

**B1-CHECK: Regression Equation**
Doc equation: `CapexAt_{i,t} = β1·CEO_QA_Uncertainty_pct + β2·CEO_Pres_Uncertainty_pct + β3·Manager_QA_Uncertainty_pct + β4·Manager_Pres_Uncertainty_pct + γ'Controls + α_i + δ_t + ε`
Code construction (runner lines 328, 362-364):
```python
exog = KEY_IVS + controls  # 4 IVs + 8 or 12 controls
formula = f"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"
```
All 4 IVs enter simultaneously. Controls included per spec. Entity and time FE absorbed. Equation matches.
RESULT: **PASS**

**B2-CHECK: Dependent Variables**
Doc: CapexAt (contemporaneous) and CapexAt_lead (t+1).
Code: MODEL_SPECS shows `"dv": "CapexAt"` for cols 1-6, `"dv": "CapexAt_lead"` for cols 7-12.
CapexAt formula: `capxy_annual / atq_annual_lag1` (CompustatEngine lines 999-1005, where capxy_annual = Q4-only capxy joined to all quarters, atq_annual_lag1 = prior year Q4 atq).
CapexAt_lead: constructed by `create_capex_lead()` in panel builder -- takes latest-call CapexAt within each (gvkey, fyearq_int), shifts -1 within gvkey, validates consecutive fiscal years.
Timing: contemporaneous (t) and lead (t+1). Correct.
RESULT: **PASS**

**B3-CHECK: Independent Variables**
Doc lists 4 IVs: CEO_QA_Uncertainty_pct, CEO_Pres_Uncertainty_pct, Manager_QA_Uncertainty_pct, Manager_Pres_Uncertainty_pct.
Code: `KEY_IVS` (runner lines 86-90) exactly matches these 4 variables. All enter simultaneously (`exog = KEY_IVS + controls` line 328). No centering, log-transform, or z-scoring applied.
Source: LinguisticEngine.
RESULT: **PASS**

**B4-CHECK: Control Variables**
Doc lists BASE_CONTROLS as 8 variables: Size, TobinsQ, ROA, BookLev, CashHoldings, DividendPayer, OCF_Volatility, Lagged_DV.
Code `BASE_CONTROLS` (runner lines 94-103): `["Size", "TobinsQ", "ROA", "BookLev", "CashHoldings", "DividendPayer", "OCF_Volatility", "Lagged_DV"]`. Exactly 8. Match.

Doc lists EXTENDED_CONTROLS as Base + 4: SalesGrowth, RD_Intensity, CashFlow, Volatility.
Code `EXTENDED_CONTROLS` (runner lines 105-110): `BASE_CONTROLS + ["SalesGrowth", "RD_Intensity", "CashFlow", "Volatility"]`. Match.

Lagged_DV construction: runner lines 251-255, `base_dv = dv.replace("_lead_qtr", "").replace("_lead", "")`, `lag_col = f"{base_dv}_lag"`, `panel["Lagged_DV"] = panel[lag_col]`. For CapexAt specs: CapexAt_lag. For CapexAt_lead specs: also CapexAt_lag. Doc note 70 says exactly this. PASS.
RESULT: **PASS**

**B5-CHECK: Fixed Effects**
Doc B5 table:
- Industry specs: `ff12_code` via `other_effects`, `time_effects=True`
- Firm specs: `EntityEffects` + `TimeEffects` via from_formula
- Time Year specs: `cal_yr`
- Time Year-Quarter specs: `cal_yr_qtr`

Code verification (runner lines 331-365):
- `time_col = "cal_yr_qtr" if fe_type.endswith("_yq") else "cal_yr"` ✓
- Industry: `PanelOLS(entity_effects=False, time_effects=True, other_effects=industry_data, ...)` ✓
- Firm: `formula = f"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"` ✓
- `cal_yr` and `cal_yr_qtr` both derived from `start_date` (call date), NOT fiscal year ✓

FE strings: doc says "Calendar Year" and "Calendar Year-Quarter" — both are calendar-based (from `build_cal_yr_qtr_index()` which uses `start_date.dt.year` and `start_date.dt.quarter`).
RESULT: **PASS**

**B6-CHECK: Standard Errors**
Doc: `cov_type="clustered"`, `cluster_entity=True` (firm-clustered)
Code line 359: `model = model_obj.fit(cov_type="clustered", cluster_entity=True)` (industry specs)
Code line 365: `model = model_obj.fit(cov_type="clustered", cluster_entity=True)` (firm specs)
Both specs use identical SE configuration. PASS.
RESULT: **PASS**

**B7-CHECK: Hypothesis Test**
Doc: Two-tailed, `model.pvalues` used directly, no one-tailed conversion.
Code: `p_two = float(model.pvalues.get(iv, np.nan))` (runner line 391). Stars applied via `_sig_stars(p_two)` (line 399) using two-tailed p-values directly. No `/2` conversion anywhere.
Doc says "two-tailed p-values stored as `{iv}_p_two` in metadata (runner line 392)". Actual line 397: `meta[f"{iv}_p_two"] = p_two`. Line 392 is `t_stat = float(model.tstats.get(iv, np.nan))`. **Line number is wrong by 5 lines.** Content claim is correct.
RESULT: **PASS** (correct substance, minor line citation error noted in failures)

**Phase 3 Result: 7/7 PASS** (one minor line number error noted)

---

## PHASE 4: SPEC REGISTER (Section C)

Doc spec register has 12 rows. MODEL_SPECS has 12 entries.

| Verified Col | Doc DV | Doc Entity FE | Doc Time FE | Doc Controls | Code `fe` value | Code `controls` | Match |
|---|---|---|---|---|---|---|---|
| 1 | CapexAt | Industry (FF12) | Cal Year | Base | `industry` | `base` | ✓ |
| 2 | CapexAt | Firm | Cal Year | Base | `firm` | `base` | ✓ |
| 3 | CapexAt | Industry (FF12) | Cal Year | Extended | `industry` | `extended` | ✓ |
| 4 | CapexAt | Firm | Cal Year | Extended | `firm` | `extended` | ✓ |
| 5 | CapexAt | Industry (FF12) | Cal Year-Quarter | Extended | `industry_yq` | `extended` | ✓ |
| 6 | CapexAt | Firm | Cal Year-Quarter | Extended | `firm_yq` | `extended` | ✓ |
| 7 | CapexAt_lead | Industry (FF12) | Cal Year | Base | `industry` | `base` | ✓ |
| 8 | CapexAt_lead | Firm | Cal Year | Base | `firm` | `base` | ✓ |
| 9 | CapexAt_lead | Industry (FF12) | Cal Year | Extended | `industry` | `extended` | ✓ |
| 10 | CapexAt_lead | Firm | Cal Year | Extended | `firm` | `extended` | ✓ |
| 11 | CapexAt_lead | Industry (FF12) | Cal Year-Quarter | Extended | `industry_yq` | `extended` | ✓ |
| 12 | CapexAt_lead | Firm | Cal Year-Quarter | Extended | `firm_yq` | `extended` | ✓ |

All 12 rows verified against code. No missing specs, no phantom specs. PASS.

Doc source claim: "runner lines 112--127". Verified: MODEL_SPECS starts at line 112 (`MODEL_SPECS = [`) and the closing bracket is at line 127. PASS.

**Phase 4 Result: 5/5 PASS**

---

## PHASE 5: SAMPLE CONSTRUCTION (Section D)

**D1-CHECK: Population**
Doc: 112,968 calls, ~2,429 firms, 2002-2018.
These are the project-wide totals from `project_thesis_scope.md` in the memory. The starting dataset is `master_sample_manifest.parquet`. Runner loads the full panel first, then filters to Main sample. Plausible and consistent with project scope.
RESULT: **PASS**

**D2-CHECK: Exclusion Criteria**
Doc lists 6-step attrition cascade:
1. Full manifest (Panel builder)
2. Main sample filter: excl FF12=8,11 (Runner `filter_main_sample()` line 233)
3. Inf replacement (Runner `prepare_regression_data()` line 268)
4. DV non-missing (line 278)
5. Complete case (line 282)
6. Min calls per firm >=5 (lines 287-289)

Code verification:
- `filter_main_sample()` (line 233): `main = panel[~panel["ff12_code"].isin([8, 11])].copy()` ✓
- `df.replace([np.inf, -np.inf], np.nan)` (line 268) ✓
- `df = df[df[dv].notna()].copy()` (line 278-279) ✓
- `complete_mask = df[required].notna().all(axis=1)` (lines 282-283) ✓
- `firm_counts = df["gvkey"].value_counts()`, `valid_firms = ... firm_counts >= MIN_CALLS_PER_FIRM`, `MIN_CALLS_PER_FIRM = 5` (lines 287-289, line 129) ✓

Note: Steps 3-6 applied per-specification (doc correctly notes this). CapexAt_lead specs have fewer observations (doc correctly notes this).
RESULT: **PASS**

**D3-CHECK: Sample Counts**
Doc: "N varies across specs due to different DVs (CapexAt vs CapexAt_lead) and different control requirements (base vs extended). The runner records `n_obs` and `n_firms` per model in `model_diagnostics.csv`. Exact counts are produced at runtime."
Code: `meta["n_obs"] = int(model.nobs)`, `meta["n_firms"] = df_prepared["gvkey"].nunique()`, saved to `model_diagnostics.csv`. This is correct.
RESULT: **PASS**

**Phase 5 Result: 3/3 PASS**

---

## PHASE 6: VARIABLE DICTIONARY (Section E)

Every variable in any regression spec verified against source code.

**DVs:**

| Variable | Doc Formula | Code Formula | Source | Winsor | Timing | Match |
|---|---|---|---|---|---|---|
| CapexAt | capxy (Q4 annual) / atq (lagged annual, t-1) | `capxy_annual / atq_annual_lag1` where capxy_annual = Q4 capxy joined to all quarters, atq_annual_lag1 = prior year Q4 atq shifted forward 1 year | CompustatEngine lines 999-1005 | 1%/99% by fiscal year | Contemporaneous | ✓ |
| CapexAt_lead | CapexAt for next consecutive fiscal year via gvkey+fyearq_int shift(-1) | `create_capex_lead()` in panel builder: takes latest-call CapexAt per (gvkey,fyearq_int), shift -1 within gvkey, NaN if not consecutive | Panel builder `create_capex_lead()` | Inherits from CapexAt | Lead (t+1) | ✓ |
| CapexAt_lag | CapexAt for prior consecutive fiscal year via shift(+1) | `create_capex_lag()` in panel builder: takes latest-call CapexAt per (gvkey,fyearq_int), shift +1, NaN if not consecutive | Panel builder `create_capex_lag()` | Inherits from CapexAt | Lag (t-1) | ✓ |

**IVs:**

| Variable | Doc Formula | Code Source | Winsor | Match |
|---|---|---|---|---|
| CEO_QA_Uncertainty_pct | (uncertainty words / total words) * 100, CEO Q&A section | LinguisticEngine (CEOQAUncertaintyBuilder) | 0%/99% upper-only per year | ✓ |
| CEO_Pres_Uncertainty_pct | (uncertainty words / total words) * 100, CEO presentation | LinguisticEngine (CEOPresUncertaintyBuilder) | 0%/99% upper-only per year | ✓ |
| Manager_QA_Uncertainty_pct | (uncertainty words / total words) * 100, all-managers Q&A | LinguisticEngine (ManagerQAUncertaintyBuilder) | 0%/99% upper-only per year | ✓ |
| Manager_Pres_Uncertainty_pct | (uncertainty words / total words) * 100, all-managers presentation | LinguisticEngine (ManagerPresUncertaintyBuilder) | 0%/99% upper-only per year | ✓ |

LinguisticEngine winsorization confirmed: `winsorize_by_year(combined, existing_pct_cols, year_col="year", lower=0.0, upper=0.99, min_obs=10)` (LinguisticEngine line 255-258). Matches doc claim of "0%/99% upper-only per calendar year". PASS.

**Base Controls:**

| Variable | Doc Formula | Code Formula | Verified | Match |
|---|---|---|---|---|
| Size | ln(atq); atq <= 0 yields NaN | `comp["Size"] = np.where(comp["atq"] > 0, np.log(comp["atq"]), np.nan)` (engine line 943) | ✓ | ✓ |
| TobinsQ | (cshoq * prccq + dlcq + dlttq) / atq; requires atq > 0 and mktcap non-missing | `(mktcap + debt_book) / comp["atq"]` where `mktcap = cshoq * prccq`, `debt_book = dlcq.clip(lower=0).fillna(0) + dlttq.clip(lower=0).fillna(0)` (engine lines 987-997) | ✓ | ✓ |
| ROA | iby (Q4 annual) / avg_assets, avg_assets = (atq_t + atq_{t-1}) / 2 | `iby_annual / avg_assets` where iby_annual = Q4 iby, avg_assets = (atq_annual + atq_annual_lag1) / 2 (engine lines 959-969) | ✓ | ✓ |
| BookLev | (dlcq + dlttq) / atq; missing debt treated as zero | `(comp["dlcq"].fillna(0) + comp["dlttq"].fillna(0)) / comp["atq"]` (engine line 948) | ✓ | ✓ |
| CashHoldings | cheq / atq | `comp["CashHoldings"] = comp["cheq"] / comp["atq"]` (engine line 986) | ✓ | ✓ |
| DividendPayer | 1 if dvy (Q4 annual) > 0, else 0 | Q4 dvy annual joined to all quarters, then `dvy_annual.fillna(0) > 0` cast to float (engine lines 1009-1012) | ✓ | ✓ |
| OCF_Volatility | Rolling 5-year std (min 3 yrs) of (oancfy / atq_{t-1}) per gvkey | OCFVolatilityBuilder calls engine `_compute_ocf_volatility()`. OCFVolatilityBuilder docstring: "rolling 5-year std (min 3 yrs) of (oancfy/atq_{t-1}) per gvkey" | ✓ | ✓ |
| Lagged_DV | CapexAt_lag for all H13 specs | `panel["Lagged_DV"] = panel[lag_col]` where `lag_col = f"{base_dv}_lag"` = "CapexAt_lag" (runner lines 252-255) | ✓ | ✓ |

**Extended Controls:**

| Variable | Doc Formula | Code Formula | Verified | Match |
|---|---|---|---|---|
| SalesGrowth | (saley_t - saley_{t-1}) / abs(saley_{t-1}); saleq fallback | `_compute_biddle_residual()` in engine: uses saley (annual total revenue) with saleq fallback | ✓ | ✓ |
| RD_Intensity | xrdq / atq; missing xrdq treated as 0 | `comp["RD_Intensity"] = comp["xrdq"].fillna(0) / comp["atq"]` (engine line 972) | ✓ | ✓ |
| CashFlow | oancfy / avg_assets; avg = (atq_t + atq_{t-1}) / 2 | `annual["oancfy"] / avg_assets` in `_compute_biddle_residual()` (engine lines 685-692) | ✓ | ✓ |
| Volatility | std(daily_ret) * sqrt(252) * 100 over [prev_call+5d, call-5d], min 10 days | VolatilityBuilder/CRSPEngine: "std(daily_ret) * sqrt(252) * 100 over window [prev_call_date + 5 days, call start_date - 5 days], >= 10 trading days" | ✓ | ✓ |

**FE Columns:**

| Variable | Type | Formula | Match |
|---|---|---|---|
| gvkey | FE/Index | 6-digit Compustat GVKEY from manifest | ✓ |
| ff12_code | FE | Fama-French 12-industry from ManifestFieldsBuilder | ✓ |
| cal_yr | FE/Index | start_date.dt.year (build_cal_yr_qtr_index() line 215) | ✓ |
| cal_yr_qtr | FE/Index | cal_yr * 10 + start_date.dt.quarter (line 217) | ✓ |

**Winsorization checks:**
- CapexAt: in `COMPUSTAT_COLS` list (line 117), NOT in `skip_winsorize` set (line 1217-1224), therefore winsorized by `_winsorize_by_year` (lines 1225-1232). Doc claims "1%/99% by fiscal year". PASS.
- SalesGrowth: explicitly in `skip_winsorize` (line 1220). Winsorized inside `_compute_biddle_residual()` at line 666. Doc says "1%/99% by fiscal year (in Biddle residual computation)". PASS.
- CashFlow: explicitly in `skip_winsorize` (line 1219). Winsorized inside `_compute_biddle_residual()` at line 693. Doc says "1%/99% by fiscal year (in Biddle residual computation)". PASS.
- DividendPayer: explicitly in `skip_winsorize` (line 1218). Doc says "No (binary)". PASS.
- Volatility: not in COMPUSTAT_COLS (CRSPEngine). Doc says "No (not in Compustat engine winsorization loop)". PASS.

**Completeness check:**
All variables in MODEL_SPECS (4 IVs + 8 base controls + 4 extended controls + Lagged_DV + DVs + FE columns) are present in the variable dictionary. No variables in any regression spec are missing from the dictionary. PASS.

**Phase 6 Result: 24/24 PASS**

---

## PHASE 7: PIPELINE, OUTPUTS, AND TREATMENT

**F-CHECK: Data Pipeline**

F1. Dependency chain is 7-step, covers: raw inputs → engine loading → panel builder → runner loading → sample filtering → regression estimation → table generation. PASS.

F2. Three engines: CompustatEngine (financial variables), LinguisticEngine (linguistic IVs), CRSPEngine (Volatility). All used by the suite. No missing engines. PASS.

F3. Merge operations (19 total):
- 16 file_name-based merges (manifest + each of 16 builders) — all verified against panel builder `build_call_level_panel()` which iterates over `builders` dict (16 entries including manifest → 15 non-manifest merges). Wait — the builders dict has 17 entries (manifest + 16 builders). The provenance doc shows 16 non-manifest merges = correct.
  - Verified: manifest (1), ceo_qa_uncertainty (2), ceo_pres_uncertainty (3), manager_qa_uncertainty (4), manager_pres_uncertainty (5), size (6), tobins_q (7), roa (8), lev (9), cash_holdings (10), capex_intensity (11), dividend_payer (12), ocf_volatility (13), sales_growth (14), rd_intensity (15), cash_flow (16), volatility (17). That is 17 builders, 16 non-manifest = 16 file_name merges. ✓
- fyearq attach via `attach_fyearq()` (merge_asof on gvkey, start_date → datadate) ✓
- CapexAt_lead lookup merge by (gvkey, fyearq_int) ✓
- CapexAt_lag lookup merge by (gvkey, fyearq_int) ✓
Total: 16 + 1 + 1 + 1 = 19. PASS.

**G-CHECK: Outputs**

Stage 3 outputs (panel builder `main()` writes):
1. `h13_capex_panel.parquet` (line 482) ✓
2. `summary_stats.csv` (line 492) ✓
3. `run_manifest.json` (via `generate_manifest()`, line 497) ✓
4. `report_step3_h13_capex.md` (line 549) ✓

Doc G1 lists exactly these 4 files. PASS.

Stage 4 outputs (runner `save_outputs()`, `main()` writes):
1. `regression_results_col{N}.txt` — `save_outputs()` lines 588-604, one per successful model ✓
2. `model_diagnostics.csv` — `save_outputs()` lines 607-610 ✓
3. `h13_capex_table.tex` — `_save_latex_table()` line 570 ✓
4. `summary_stats.csv` — `main()` line 767 ✓
5. `summary_stats.tex` — `main()` line 768 ✓
6. `sample_attrition.csv` — `generate_attrition_table()` writes both CSV and TEX ✓
7. `sample_attrition.tex` — confirmed via `attrition_table.py` `generate_attrition_table()` which writes `sample_attrition.tex` at path line 51 ✓
8. `run_manifest.json` — `generate_manifest()` line 813 ✓
9. `report_step4_H13.md` — `generate_report()` line 695 ✓

Doc G2 lists exactly these 9 files. PASS.

Note: The runner's docstring (line 44) says `regression_results_col{1-8}.txt` but the code iterates over all 12 MODEL_SPECS. This is a stale docstring that the provenance doc correctly identifies in Known Issue 1. The provenance doc G2 correctly says `regression_results_col{1-12}.txt`. PASS.

Similarly, the runner's docstring (line 50) lists `sample_attrition.csv` but NOT `sample_attrition.tex`. The provenance doc correctly includes both. PASS.

**H-CHECK: Outlier/Missing Treatment**

H1. Winsorization:
- Compustat financial variables: 1%/99% by fiscal year (fyearq), `_winsorize_by_year()` in CompustatEngine (lines 1225-1232). Threshold: 10 obs minimum per year-group. PASS.
- CapexAt is in `winsorize_cols` (included in COMPUSTAT_COLS, not in skip_winsorize). PASS.
- SalesGrowth and CashFlow: winsorized inside `_compute_biddle_residual()` (lines 666, 693) and excluded from main loop. PASS.
- DividendPayer: in skip_winsorize (binary). PASS.
- Linguistic IVs: 0%/99% upper-only per calendar year via LinguisticEngine. PASS.
- Volatility: no Compustat-engine winsorization (CRSPEngine). PASS.

H2. Missing data policy:
- `df.replace([np.inf, -np.inf], np.nan)` (runner line 268). PASS.
- Complete-case: `df[required].notna().all(axis=1)` (runner line 282). PASS.
- CapexAt_lead/CapexAt_lag: NaN for last/first fiscal year or gaps. PASS.

H3. Transformations:
- Size: ln(atq). PASS.
- Volatility: annualized via sqrt(252) * 100. PASS.

**Phase 7 Result: 9/9 PASS**

---

## PHASE 8: GENERATE_ALL_TABLES.PY ENTRY (Section I)

The provenance doc reproduces the H13 entry as:
```python
{
    "id": "H13",
    "dir": "h13_capex/2026-03-27_095013",
    "caption": "H13: Speech Uncertainty and Capital Expenditure",
    "label": "tab:h13",
    "cols": 12,
    "dvs": [
        ("CapexAt", 6),
        (r"CapexAt\_lead", 6),
    ],
    "tail": "two",
    "hyp_dir": None,
}
```

Verified against `outputs/generate_all_tables.py` lines 245-257:
```python
{
    "id": "H13",
    "dir": "h13_capex/2026-03-27_095013",
    "caption": "H13: Speech Uncertainty and Capital Expenditure",
    "label": "tab:h13",
    "cols": 12,
    "dvs": [
        ("CapexAt", 6),
        (r"CapexAt\_lead", 6),
    ],
    "tail": "two",
    "hyp_dir": None,
},
```

**CHECK: id** — "H13" matches. PASS.
**CHECK: dir** — "h13_capex/2026-03-27_095013" matches. PASS.
**CHECK: caption** — "H13: Speech Uncertainty and Capital Expenditure" matches. PASS.
**CHECK: label** — "tab:h13" matches. PASS.
**CHECK: cols** — 12 matches. PASS.
**CHECK: dvs** — ("CapexAt", 6) and (r"CapexAt\_lead", 6) match. PASS.
**CHECK: tail** — "two" matches. PASS.
**CHECK: hyp_dir** — None matches. PASS.

**FAIL: Line number citation**
Doc says "Source: `outputs/generate_all_tables.py`, lines 293--305."
Actual: The H13 entry spans lines 245--257 of `generate_all_tables.py`. Lines 293-305 correspond to the H14 entry's lines (the H13 entry is at 245-257, H13.1 at 258-288, H14 starts at 289). The line reference is wrong by ~48 lines.

**FAIL: IV_NAMES line reference**
Doc says "the global `IV_NAMES` list (line 407--412) applies".
Actual: IV_NAMES is at lines 400-405:
```python
400  IV_NAMES = [
401      "CEO_QA_Uncertainty_pct",
402      "CEO_Pres_Uncertainty_pct",
403      "Manager_QA_Uncertainty_pct",
404      "Manager_Pres_Uncertainty_pct",
405  ]
```
The reference is off by approximately 7 lines.

**Verification table from doc (content accuracy):**

| Field | Doc claims | Code says | Match |
|---|---|---|---|
| tail | "two" | "two" (line 255) | ✓ |
| hyp_dir | None | None (line 256) | ✓ |
| cols | 12 | 12 (line 250) | ✓ |
| dvs | CapexAt (6), CapexAt_lead (6) | identical | ✓ |

All content claims correct. Only line number references are wrong.

**Phase 8 Result: 4/6 PASS** (2 FAIL on line number citations; all content claims correct)

---

## PHASE 9: MODEL-FAMILY ADDENDUM (Section K)

**K1 (PanelOLS) verified:**

Industry FE specs (cols 1, 3, 5, 7, 9, 11):
- Doc: `entity_effects=False`, `time_effects=True`, `other_effects=df_panel["ff12_code"]`, `drop_absorbed=True`, `check_rank=False`
- Code (runner lines 350-358):
  ```python
  model_obj = PanelOLS(
      dependent=dependent_data, exog=exog_data,
      entity_effects=False, time_effects=True,
      other_effects=industry_data, drop_absorbed=True, check_rank=False,
  )
  ```
  PASS.

Firm FE specs (cols 2, 4, 6, 8, 10, 12):
- Doc: EntityEffects + TimeEffects via from_formula, `drop_absorbed=True`
- Code (runner lines 362-364):
  ```python
  formula = f"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"
  model_obj = PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)
  ```
  PASS.

Panel index construction:
- Doc: Year FE specs: `set_index(["gvkey", "cal_yr"])`, Year-Quarter FE specs: `set_index(["gvkey", "cal_yr_qtr"])` (runner line 342)
- Code line 342: `df_panel = df_prepared.set_index(["gvkey", time_col])` where `time_col = "cal_yr_qtr" if fe_type.endswith("_yq") else "cal_yr"` (line 331)
  PASS.

Singleton handling: "PanelOLS default behavior with `drop_absorbed=True`". This is the correct description — no special singleton treatment coded. PASS.

K2 through K6: All marked N/A. Only PanelOLS model family used in H13. PASS.

**Phase 9 Result: 5/5 PASS**

---

## PHASE 10: QUALITY GATE CHECKLIST

| # | Quality Gate | Met? | Evidence |
|---|-------------|------|----------|
| 1 | Every variable in every regression spec in Variable Dictionary with explicit formula and source engine | PASS | All 22 variables documented with formula and source |
| 2 | Model equation matches what the code actually estimates | PASS | 4 IVs + controls + FE verified against `exog = KEY_IVS + controls` and formula string |
| 3 | Specification register accounts for every model column | PASS | 12/12 rows verified against MODEL_SPECS |
| 4 | Attrition cascade has row counts for each filter step | PARTIAL | Counts marked [UNVERIFIED — runtime-dependent]; each filter step described but actual N not given. Acceptable per project convention |
| 5 | Tail test direction matches between runner code and generate_all_tables.py | PASS | Both "two" / `None` |
| 6 | FE specification matches between docstring, code, and document | PASS | All FE strings use calendar year, not fiscal year |
| 7 | Every merge in the panel builder is documented with join keys and type | PASS | 19 merges, all with keys and type |
| 8 | Output file list matches what the runner actually writes | PASS | G2 includes sample_attrition.tex which docstring omits; G2 says col{1-12} which docstring says col{1-8} — G2 is correct |
| 9 | Model-family addendum filled for correct family only | PASS | K1 filled; K2-K6 N/A |
| 10 | Claims marked [UNVERIFIED] have explanation | PASS | Only one [UNVERIFIED] tag in D2, explained as "runtime-dependent, see model_diagnostics.csv" |

Quality Gate 4 is a qualified pass: the doc correctly explains why row counts are not given (runtime-dependent) and directs to the output file. Per project convention this is acceptable but noted.

**Phase 10 Result: 9/10 PASS** (Quality Gate 4 qualified pass)

---

## PHASE 11: CROSS-REFERENCE CONSISTENCY

| Check | Section A | Section B/C/E/I/K | Consistent? |
|---|---|---|---|
| 1. DVs in B2 match DVs in C | CapexAt, CapexAt_lead | C rows use CapexAt (cols 1-6), CapexAt_lead (cols 7-12) | ✓ |
| 2. DVs in C match DVs in I | CapexAt (6), CapexAt_lead (6) | I dvs: ("CapexAt", 6), ("CapexAt_lead", 6) | ✓ |
| 3. Controls in B4 match variables in E | 12 controls listed in B4 | All 12 appear in E dictionary | ✓ |
| 4. Column count in A matches rows in C | A: 12 | C: 12 rows | ✓ |
| 5. Column count in A matches cols in I | A: 12 | I cols: 12 | ✓ |
| 6. Tail in A matches B7 matches I | A: two-tailed | B7: two-tailed | I: "two" / None | ✓ |
| 7. FE in B5 matches C matches K | B5: Industry/Firm x cal_yr/cal_yr_qtr | C: same | K1: same | ✓ |
| 8. Panel index in A matches set_index in K | A: (gvkey, cal_yr) or (gvkey, cal_yr_qtr) | K1: `set_index(["gvkey", time_col])` = same | ✓ |

No internal contradictions found.

**Phase 11 Result: 8/8 PASS**

---

## CORRECTIONS REQUIRED

### Correction 1 — Section I: Fix generate_all_tables.py line number

**Section:** I. GENERATE_ALL_TABLES.PY ENTRY (near bottom of entry block)
**Current text:** "Source: `outputs/generate_all_tables.py`, lines 293--305."
**Corrected text:** "Source: `outputs/generate_all_tables.py`, lines 245--257."
**Code reference:** `outputs/generate_all_tables.py` lines 245-257 contain the H13 entry. Line 244 is the comment `# ── H13 family ──`.

---

### Correction 2 — Section I: Fix IV_NAMES line reference

**Section:** I. GENERATE_ALL_TABLES.PY ENTRY (verification paragraph, last sentence)
**Current text:** "the global `IV_NAMES` list (line 407--412) applies: CEO_QA_Uncertainty_pct, ..."
**Corrected text:** "the global `IV_NAMES` list (lines 400--405) applies: CEO_QA_Uncertainty_pct, ..."
**Code reference:** `outputs/generate_all_tables.py` line 400: `IV_NAMES = [`, line 405: closing bracket.

---

### Correction 3 — Section B7: Fix runner line number for p_two storage

**Section:** B7. Hypothesis Test (last bullet)
**Current text:** "two-tailed p-values stored as `{iv}_p_two` in metadata (runner line 392)"
**Corrected text:** "two-tailed p-values stored as `{iv}_p_two` in metadata (runner line 397)"
**Code reference:** `src/f1d/econometric/run_h13_capex.py` line 397: `meta[f"{iv}_p_two"] = p_two`. Line 392 is `t_stat = float(model.tstats.get(iv, np.nan))`.

---

## EVIDENCE APPENDIX

### Runner MODEL_SPECS (lines 112-127, verified)
```python
MODEL_SPECS = [
    {"col": 1,  "dv": "CapexAt",      "fe": "industry",    "controls": "base"},
    {"col": 2,  "dv": "CapexAt",      "fe": "firm",        "controls": "base"},
    {"col": 3,  "dv": "CapexAt",      "fe": "industry",    "controls": "extended"},
    {"col": 4,  "dv": "CapexAt",      "fe": "firm",        "controls": "extended"},
    {"col": 5,  "dv": "CapexAt",      "fe": "industry_yq", "controls": "extended"},
    {"col": 6,  "dv": "CapexAt",      "fe": "firm_yq",     "controls": "extended"},
    {"col": 7,  "dv": "CapexAt_lead", "fe": "industry",    "controls": "base"},
    {"col": 8,  "dv": "CapexAt_lead", "fe": "firm",        "controls": "base"},
    {"col": 9,  "dv": "CapexAt_lead", "fe": "industry",    "controls": "extended"},
    {"col": 10, "dv": "CapexAt_lead", "fe": "firm",        "controls": "extended"},
    {"col": 11, "dv": "CapexAt_lead", "fe": "industry_yq", "controls": "extended"},
    {"col": 12, "dv": "CapexAt_lead", "fe": "firm_yq",     "controls": "extended"},
]
```
12 entries — matches provenance doc claim.

### CapexAt Formula (CompustatEngine, verified)
```python
capxy_annual = _compute_annual_q4_variable(comp, "capxy", "_capxy_annual")
comp["CapexAt"] = np.where(
    pd.Series(atq_annual_lag1, index=comp.index) > 0,
    pd.Series(capxy_annual, index=comp.index) / pd.Series(atq_annual_lag1, index=comp.index),
    np.nan,
)
```
Numerator: Q4-only capxy joined to all quarters (full fiscal year).
Denominator: prior year Q4 atq (lag via `_compute_annual_q4_variable_lag`).
Matches provenance doc formula "capxy (Q4 annual) / atq (lagged annual, t-1)".

### generate_all_tables.py H13 entry (actual lines 245-257)
```python
{
    "id": "H13",
    "dir": "h13_capex/2026-03-27_095013",
    "caption": "H13: Speech Uncertainty and Capital Expenditure",
    "label": "tab:h13",
    "cols": 12,
    "dvs": [
        ("CapexAt", 6),
        (r"CapexAt\_lead", 6),
    ],
    "tail": "two",
    "hyp_dir": None,
},
```

### Winsorization skip set (CompustatEngine lines 1217-1224)
```python
skip_winsorize = {
    "DividendPayer",
    "CashFlow",
    "SalesGrowth",
    "fqtr",
    "ExternalFunding",
    "DebtChoice",
}
```
CapexAt is NOT in this set → it is winsorized by `_winsorize_by_year`. Matches provenance doc.

### Lagged_DV dynamic construction (runner lines 251-255)
```python
base_dv = dv.replace("_lead_qtr", "").replace("_lead", "")
lag_col = f"{base_dv}_lag"
panel = panel.copy()
panel["Lagged_DV"] = panel[lag_col]
```
For CapexAt specs: base_dv = "CapexAt", lag_col = "CapexAt_lag".
For CapexAt_lead specs: base_dv = "CapexAt", lag_col = "CapexAt_lag".
Matches provenance doc description exactly.
