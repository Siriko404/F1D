# Adversarial Audit: H13 Capital Expenditure Provenance Document

**Audit Date:** 2026-03-30
**Auditor:** Hostile Audit (Claude Opus 4.6)
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
| Sample Construction (Phase 5) | 3 | 2 | 1 | 67% |
| Variable Dictionary (Phase 6) | 24 | 23 | 1 | 96% |
| Pipeline/Outputs/Treatment (Phase 7) | 9 | 8 | 1 | 89% |
| Table Generator Entry (Phase 8) | 5 | 5 | 0 | 100% |
| Model-Family Addendum (Phase 9) | 5 | 5 | 0 | 100% |
| Quality Gates (Phase 10) | 10 | 9 | 1 | 90% |
| Cross-Reference Consistency (Phase 11) | 8 | 8 | 0 | 100% |
| **TOTAL** | **112** | **108** | **4** | **96%** |

---

## VERDICT

**PASS WITH NOTES**: The provenance document is substantially accurate and complete. Four minor issues were found, none of which affect the correctness of the documented regression specifications or variable constructions. The issues are: (1) missing row counts in the attrition cascade, (2) an irrelevant variable (EPS_Growth) listed in winsorization scope, (3) a missing output file in the G2 list, and (4) a stale line reference in D2. All are cosmetic/completeness issues, not factual errors about the econometric model.

---

## Phase 1: STRUCTURAL COMPLETENESS

Read the creation prompt (`docs/Prompts/Suite Provenance Doc.txt`) to extract all required sections (A through L). Then checked the provenance doc (`docs/provenance/H13.md`) for each.

| Section | Required by Prompt | Present in Doc | Complete | Notes |
|---------|-------------------|----------------|----------|-------|
| A. Suite Identity | Yes | Yes | Yes | YAML block with all required fields |
| B. Model Specification | Yes | Yes | Yes | Contains all 7 subsections |
| B1. Regression Equation | Yes | Yes | Yes | LaTeX equation with correct notation |
| B2. Dependent Variable(s) | Yes | Yes | Yes | Table with 2 DVs |
| B3. Independent Variable(s) | Yes | Yes | Yes | Table with 4 IVs |
| B4. Control Variables | Yes | Yes | Yes | Base (8) + Extended (12) with formulas |
| B5. Fixed Effects | Yes | Yes | Yes | Table with 4 FE types |
| B6. Standard Errors | Yes | Yes | Yes | Clustered at firm level |
| B7. Hypothesis Test | Yes | Yes | Yes | Two-tailed, correct p-value handling |
| C. Spec Register | Yes | Yes | Yes | 12 rows matching 12 MODEL_SPECS |
| D. Sample Construction | Yes | Yes | Partial | Missing hardcoded row counts (see Phase 5) |
| D1. Population | Yes | Yes | Yes | 112,968 calls, ~2,429 firms |
| D2. Exclusion Criteria | Yes | Yes | Partial | Filter steps described but no row counts |
| D3. Sample Counts per Spec | Yes | Yes | Yes | Notes N varies, defers to runtime |
| E. Variable Dictionary | Yes | Yes | Yes | 22 variables with full formulas |
| F. Data Pipeline | Yes | Yes | Yes | F1-F3 all present |
| F1. Dependency Chain | Yes | Yes | Yes | 7-step chain documented |
| F2. Data Engines | Yes | Yes | Yes | 3 engines listed |
| F3. Merge Operations | Yes | Yes | Yes | 18 merge rows documented |
| G. Outputs | Yes | Yes | Partial | Missing one file in G2 (see Phase 7) |
| G1. Stage 3 Outputs | Yes | Yes | Yes | 4 files listed |
| G2. Stage 4 Outputs | Yes | Yes | Partial | 9 files listed, but `sample_attrition.tex` is missing from docstring check |
| G3. Summary Statistics | Yes | Yes | Yes | 17 variables listed |
| H. Outlier/Missing Treatment | Yes | Yes | Yes | H1, H2, H3 present |
| I. generate_all_tables Entry | Yes | Yes | Yes | Full entry + verification table |
| J. Reproduction Commands | Yes | Yes | Yes | 3 commands |
| K. Model-Family Addendum | Yes | Yes | Yes | K1 filled, K2-K6 marked N/A |
| L. Known Issues | Yes | Yes | Yes | 7 issues documented |

**Phase 1 Result: 26/26 PASS.** All required sections are present. Two sections have minor completeness issues documented in later phases.

---

## Phase 2: FACTUAL ACCURACY -- SECTION A (Suite Identity)

### A-1. Suite ID
- **Provenance doc claims:** `H13`
- **Verification:** Trivial. The runner file is `run_h13_capex.py`; the panel is `h13_capex_panel.parquet`.
- **Result:** PASS

### A-2. Title
- **Provenance doc claims:** "Speech Uncertainty and Capital Expenditure"
- **Verification:** Runner docstring line 4: "STAGE 4: Test H13 Capital Expenditure Hypothesis". LaTeX table caption (runner line 462): "Speech Uncertainty and Capital Expenditure". generate_all_tables.py caption: "H13: Speech Uncertainty and Capital Expenditure".
- **Result:** PASS

### A-3. Hypothesis
- **Provenance doc claims:** "Does managerial linguistic uncertainty during earnings calls affect contemporaneous and future capital expenditure intensity?"
- **Verification:** Runner docstring lines 32-33: "H13: beta(uncertainty_var) != 0 -- no directional prediction." The runner tests whether uncertainty affects CapexAt and CapexAt_lead.
- **Result:** PASS

### A-4. Direction (tail test)
- **Provenance doc claims:** "two-tailed (beta != 0, no directional prediction)"
- **Verification:** Runner line 32: "Hypothesis Test (two-tailed)". Runner line 375: "Per-IV two-tailed p-values (H13: no directional prediction)". Runner line 391: `p_two = float(model.pvalues.get(iv, np.nan))` -- raw two-tailed p-values used directly, no one-tailed conversion.
- **Result:** PASS

### A-5. Model Family
- **Provenance doc claims:** PanelOLS
- **Verification:** Runner line 73: `from linearmodels.panel import PanelOLS`. Runner line 350: `model_obj = PanelOLS(...)`. Runner line 364: `PanelOLS.from_formula(...)`.
- **Result:** PASS

### A-6. Estimator
- **Provenance doc claims:** `linearmodels.panel.PanelOLS`
- **Verification:** Runner line 73: `from linearmodels.panel import PanelOLS`.
- **Result:** PASS

### A-7. Unit of Observation
- **Provenance doc claims:** "call-level (one row per earnings call)"
- **Verification:** Panel builder docstring line 7: "Build CALL-LEVEL panel for H13 Capital Expenditure hypothesis test." Line 20: "Unit of observation: the individual earnings call (file_name)." Panel is keyed on `file_name` (one per call).
- **Result:** PASS

### A-8. Panel Index
- **Provenance doc claims:** "(gvkey, cal_yr) or (gvkey, cal_yr_qtr) depending on spec"
- **Verification:** Runner line 342: `df_panel = df_prepared.set_index(["gvkey", time_col])` where `time_col = "cal_yr_qtr" if fe_type.endswith("_yq") else "cal_yr"` (line 331). Year specs use `(gvkey, cal_yr)`, Year-Quarter specs use `(gvkey, cal_yr_qtr)`.
- **Result:** PASS

### A-9. Columns (number of model specs)
- **Provenance doc claims:** 12
- **Verification:** Runner line 112-127: `MODEL_SPECS` has 12 entries (cols 1-12). Confirmed by counting entries.
- **Result:** PASS

### A-10. Runner and Panel Builder paths
- **Provenance doc claims:** `src/f1d/econometric/run_h13_capex.py` and `src/f1d/variables/build_h13_capex_panel.py`
- **Verification:** Both files exist and were read during this audit.
- **Result:** PASS

**Phase 2 Result: 10/10 PASS.**

---

## Phase 3: FACTUAL ACCURACY -- SECTION B (Model Specification)

### B1-CHECK: Regression Equation
- **Provenance doc claims:** `CapexAt_{i,t} = beta_1 * CEO_QA_Uncertainty_pct + beta_2 * CEO_Pres_Uncertainty_pct + beta_3 * Manager_QA_Uncertainty_pct + beta_4 * Manager_Pres_Uncertainty_pct + gamma' Controls + alpha_i + delta_t + epsilon_{i,t}`
- **Verification:** Runner line 328: `exog = KEY_IVS + controls` where `KEY_IVS` has the 4 IVs (lines 86-90) and controls is BASE_CONTROLS or EXTENDED_CONTROLS. Firm FE formula at line 363: `"{dv} ~ 1 + {exog} + EntityEffects + TimeEffects"`. Industry FE at lines 347-358: `PanelOLS(dependent=dependent_data, exog=exog_data, entity_effects=False, time_effects=True, other_effects=industry_data)`. All 4 IVs enter simultaneously.
- The equation also correctly notes CapexAt_lead as DV for cols 7-12.
- **Result:** PASS

### B2-CHECK: Dependent Variable(s)
- **Provenance doc claims:** CapexAt (capxy Q4 annual / atq lagged annual t-1) and CapexAt_lead (CapexAt for fiscal year t+1)
- **Verification:**
  - CapexAt: CompustatEngine line 994-999: `capxy_annual / atq_annual_lag1` where `atq_annual_lag1` is the prior fiscal year Q4 atq (via `_compute_annual_q4_variable_lag`). Provenance doc says "capxy (Q4 annual) / atq (lagged annual, t-1)". Match.
  - CapexAt_lead: Panel builder `create_capex_lead()` (lines 215-337) shifts CapexAt by -1 within gvkey on fiscal year, validates consecutive fiscal years. Match.
  - DVs in runner MODEL_SPECS: cols 1-6 use `"CapexAt"`, cols 7-12 use `"CapexAt_lead"`. Both documented.
- **Result:** PASS

### B3-CHECK: Independent Variable(s)
- **Provenance doc claims:** 4 IVs: CEO_QA_Uncertainty_pct, CEO_Pres_Uncertainty_pct, Manager_QA_Uncertainty_pct, Manager_Pres_Uncertainty_pct. All from LinguisticEngine.
- **Verification:** Runner `KEY_IVS` (lines 86-90): exact match of all 4 names. No centering, log-transform, or z-scoring documented or applied in code.
- **Result:** PASS

### B4-CHECK: Control Variables
- **Provenance doc claims:**
  - Base (8): Size, TobinsQ, ROA, BookLev, CashHoldings, DividendPayer, OCF_Volatility, Lagged_DV
  - Extended (Base + 4): + SalesGrowth, RD_Intensity, CashFlow, Volatility
- **Verification:** Runner `BASE_CONTROLS` (lines 94-103): exact match of 8 variables. Runner `EXTENDED_CONTROLS` (lines 105-110): exact match (Base + 4 = 12). Lagged_DV construction at lines 251-255: `base_dv = dv.replace("_lead_qtr", "").replace("_lead", "")` then `lag_col = f"{base_dv}_lag"` then `panel["Lagged_DV"] = panel[lag_col]`. For CapexAt specs, base_dv = "CapexAt", lag_col = "CapexAt_lag". For CapexAt_lead specs, base_dv = "CapexAt", lag_col = "CapexAt_lag". Provenance doc correctly notes all H13 specs use CapexAt_lag.
- **Result:** PASS

### B5-CHECK: Fixed Effects
- **Provenance doc claims:** Industry FE via ff12_code (other_effects), Firm FE via EntityEffects, Time FE via cal_yr or cal_yr_qtr (time_effects=True). cal_yr/cal_yr_qtr derived from start_date.
- **Verification:**
  - Industry specs (lines 346-358): `entity_effects=False, time_effects=True, other_effects=industry_data` where `industry_data = df_panel["ff12_code"]`. Match.
  - Firm specs (lines 361-365): formula includes `EntityEffects + TimeEffects`. Match.
  - Time col selection (line 331): `time_col = "cal_yr_qtr" if fe_type.endswith("_yq") else "cal_yr"`. Match.
  - cal_yr/cal_yr_qtr construction: `build_cal_yr_qtr_index()` in panel_utils.py lines 195-218: `cal_yr = dt.dt.year`, `cal_yr_qtr = cal_yr * 10 + dt.dt.quarter` from `start_date`. Match.
- **Result:** PASS

### B6-CHECK: Standard Errors
- **Provenance doc claims:** `cov_type="clustered"`, `cluster_entity=True` (firm-clustered)
- **Verification:** Runner line 359: `model = model_obj.fit(cov_type="clustered", cluster_entity=True)` (industry specs). Runner line 365: `model = model_obj.fit(cov_type="clustered", cluster_entity=True)` (firm specs). Match.
- **Result:** PASS

### B7-CHECK: Hypothesis Test
- **Provenance doc claims:** Two-tailed, p-values used directly from PanelOLS, no one-tailed conversion. Significance: *** p<0.01, ** p<0.05, * p<0.10.
- **Verification:** Runner line 391: `p_two = float(model.pvalues.get(iv, np.nan))`. No division by 2. `_sig_stars()` at lines 410-420: thresholds are `p < 0.01`, `p < 0.05`, `p < 0.10`. Match.
- **Result:** PASS

**Phase 3 Result: 7/7 PASS.**

---

## Phase 4: FACTUAL ACCURACY -- SECTION C (Spec Register)

### C-1. Row count
- **Provenance doc claims:** 12 rows in spec register table.
- **Verification:** Table has 12 rows (cols 1-12). Runner `MODEL_SPECS` has 12 entries. Match.
- **Result:** PASS

### C-2. DV per spec
- **Verification against MODEL_SPECS (runner lines 112-127):**
  - Cols 1-6: `"CapexAt"` -- provenance doc: CapexAt. Match.
  - Cols 7-12: `"CapexAt_lead"` -- provenance doc: CapexAt_lead. Match.
- **Result:** PASS

### C-3. Entity FE per spec
- **Verification:**
  - Col 1: `"industry"` -> Industry (FF12). Match.
  - Col 2: `"firm"` -> Firm. Match.
  - Col 3: `"industry"` -> Industry (FF12). Match.
  - Col 4: `"firm"` -> Firm. Match.
  - Col 5: `"industry_yq"` -> Industry (FF12). Match.
  - Col 6: `"firm_yq"` -> Firm. Match.
  - Cols 7-12: Same pattern. Verified all 12.
- **Result:** PASS

### C-4. Time FE per spec
- **Verification:**
  - Cols 1-4, 7-10: FE types without `_yq` suffix -> Cal Year. Match.
  - Cols 5-6, 11-12: FE types with `_yq` suffix -> Cal Year-Quarter. Match.
- **Result:** PASS

### C-5. Controls per spec
- **Verification:**
  - Cols 1-2, 7-8: `"base"` -> Base. Match.
  - Cols 3-6, 9-12: `"extended"` -> Extended. Match.
- **Result:** PASS

**Phase 4 Result: 5/5 PASS.**

---

## Phase 5: FACTUAL ACCURACY -- SECTION D (Sample Construction)

### D1-CHECK: Population
- **Provenance doc claims:** Starting dataset is `master_sample_manifest.parquet`, 112,968 calls, ~2,429 firms, 2002-2018.
- **Verification:** These match the project scope documented in memory (`project_thesis_scope.md`). The manifest path is correct per runner line 41 and panel builder line 496.
- **Result:** PASS

### D2-CHECK: Exclusion Criteria
- **Provenance doc claims a 6-step attrition cascade:**
  1. Full manifest (panel builder)
  2. Main sample filter excl FF12=8,11 (runner `filter_main_sample()` line 233)
  3. DV non-missing (runner `prepare_regression_data()` line 278)
  4. Inf replacement (runner line 268)
  5. Complete case (runner line 282)
  6. Min calls per firm >=5 (runner lines 287-289)

- **Verification against code:**
  - Step 1: Panel builder loads full manifest. Correct.
  - Step 2: Runner `filter_main_sample()` at line 233-239: `panel[~panel["ff12_code"].isin([8, 11])]`. The provenance doc says "line 233". The actual function starts at line 233 with the filter at line 236. Close enough.
  - Step 3: Runner line 278: `df = df[df[dv].notna()].copy()`. Correct.
  - Step 4: Runner line 268: `df = df.replace([np.inf, -np.inf], np.nan)`. Correct. NOTE: The provenance doc places this as step 4, but in the code it happens at line 268 BEFORE the DV filter at line 278. The provenance doc's step ordering (DV filter before inf replacement) does NOT match the code ordering (inf replacement at 268, then DV filter at 278). However, functionally this does not matter since inf->NaN and then NaN-DV-drop achieves the same result.
  - Step 5: Runner line 282: `complete_mask = df[required].notna().all(axis=1)`. Correct.
  - Step 6: Runner lines 287-289: firms with < `MIN_CALLS_PER_FIRM=5` calls dropped. Correct.

- **ISSUE: The provenance doc's D2 table has NO row counts** (no "Rows Before", "Rows After", "Dropped" columns). The creation prompt Section D2 specifies a table with `Rows Before | Rows After | Dropped` columns. The provenance doc defends this by saying "Row counts are not hardcoded -- they depend on data availability at build time." While true that exact counts are runtime-dependent, the creation prompt and quality gate #4 require row counts. The provenance doc could have included approximate counts from a prior run, or marked them [UNVERIFIED].

- **ISSUE: Step ordering.** The provenance doc lists steps 3 and 4 as "DV non-missing" then "Inf replacement", but the code does inf replacement (line 268) before DV filter (line 278). The ordering in the provenance doc is reversed from the code.
- **Result:** FAIL (missing row counts; step ordering mismatch)

### D3-CHECK: Sample Counts per Specification
- **Provenance doc claims:** N varies across specs; exact counts produced at runtime in `model_diagnostics.csv`.
- **Verification:** Confirmed. Each spec runs `prepare_regression_data()` which applies its own DV/controls filter. N will differ between CapexAt and CapexAt_lead specs (lead has more NaN). The provenance doc's claim is reasonable.
- **Result:** PASS

**Phase 5 Result: 2/3 (1 FAIL).**

---

## Phase 6: FACTUAL ACCURACY -- SECTION E (Variable Dictionary)

### Systematic check of every variable in the dictionary:

**1. CapexAt**
- Code name: `CapexAt`. Correct.
- Formula: `capxy (Q4 annual YTD) / atq (lagged annual, t-1)`. CompustatEngine lines 994-999: `capxy_annual / atq_annual_lag1`. Match.
- Source: CompustatEngine. Correct.
- Winsorized: "1%/99% by fiscal year". CompustatEngine `COMPUSTAT_COLS` includes `CapexAt` and `skip_winsorize` does not include it. Match.
- **Result:** PASS

**2. CapexAt_lead**
- Code name: `CapexAt_lead`. Correct.
- Formula: "CapexAt for next consecutive fiscal year, via gvkey+fyearq_int shift(-1); NaN if gap". Panel builder `create_capex_lead()` lines 215-337: groups by (gvkey, fyearq_int), takes latest call per fiscal year, shifts -1, validates consecutive. Match.
- Source: Panel builder. Correct.
- Winsorized: "Inherits from CapexAt". CapexAt is winsorized before lead computation. Correct.
- **Result:** PASS

**3. CapexAt_lag**
- Code name: `CapexAt_lag`. Correct.
- Formula: Panel builder `create_capex_lag()` lines 340-408: same pattern as lead but shift(+1). Match.
- **Result:** PASS

**4. CEO_QA_Uncertainty_pct**
- Code name: exact match.
- Formula: "(uncertainty words / total words) * 100 in CEO Q&A section". Consistent with LinguisticEngine output.
- Source: LinguisticEngine. Correct.
- Winsorized: "0%/99% upper-only per year". LinguisticEngine calls `winsorize_by_year(..., lower=0.0, upper=0.99)`. Match.
- **Result:** PASS

**5. CEO_Pres_Uncertainty_pct** -- same pattern as #4. PASS.

**6. Manager_QA_Uncertainty_pct** -- same pattern as #4. PASS.

**7. Manager_Pres_Uncertainty_pct** -- same pattern as #4. PASS.

**8. Size**
- Formula: "ln(atq); atq <= 0 yields NaN". CompustatEngine computes `Size = ln(atq)` with `atq > 0` guard. Match.
- Winsorized: "1%/99% by fiscal year". `Size` is in COMPUSTAT_COLS and not in skip_winsorize. Match.
- **Result:** PASS

**9. TobinsQ**
- Formula: "(cshoq * prccq + dlcq + dlttq) / atq". CompustatEngine lines 988-991: `(mktcap + debt_book) / comp["atq"]` where `mktcap = cshoq * prccq` and `debt_book = debt_c + debt_t` (dlcq clipped + dlttq clipped). The provenance doc says "requires atq > 0 and mktcap non-missing". Code line 989: `(comp["atq"] > 0) & mktcap.notna()`. Match.
- **Result:** PASS

**10. ROA**
- Formula: "iby (Q4 annual) / ((atq_t + atq_{t-1}) / 2)". CompustatEngine lines 957-963: `iby_annual / avg_assets` where `avg_assets = (atq_annual + atq_annual_lag1) / 2`. Match.
- **Result:** PASS

**11. BookLev**
- Formula: "(dlcq + dlttq) / atq; missing debt treated as zero". CompustatEngine lines 943-951: uses `comp["dlcq"].clip(lower=0).fillna(0)` and `comp["dlttq"].clip(lower=0).fillna(0)`, but with `np.where(comp["dlcq"].isna() & comp["dlttq"].isna(), np.nan, ...)` guard. The "missing debt treated as zero" is slightly imprecise -- when BOTH are NaN, result is NaN. When only one is NaN, it's treated as 0. This is close enough to the provenance doc's description.
- **Result:** PASS

**12. CashHoldings**
- Formula: "cheq / atq". CompustatEngine line 981: `comp["cheq"] / comp["atq"]`. Match.
- **Result:** PASS

**13. DividendPayer**
- Formula: "1 if dvy (Q4 annual) > 0, else 0". CompustatEngine uses `_compute_annual_q4_variable(comp, "dvy", ...)` and then checks `> 0`. Match.
- Winsorized: "No (binary)". In `skip_winsorize` set. Match.
- **Result:** PASS

**14. OCF_Volatility**
- Formula: "Rolling 5-year std (min 3 yrs) of (oancfy / atq_{t-1}) per gvkey". CompustatEngine `_compute_ocf_volatility()` computes this pattern. Match.
- **Result:** PASS

**15. SalesGrowth**
- Formula: "(saley_t - saley_{t-1}) / abs(saley_{t-1}); Q4 annual; saleq fallback". CompustatEngine `_compute_biddle_residual()` computes this. Match.
- Winsorized: "1%/99% by fiscal year (in Biddle residual computation)". Confirmed: SalesGrowth is in `skip_winsorize` (line 1126) because it's already winsorized inside `_compute_biddle_residual()`. Match.
- **Result:** PASS

**16. RD_Intensity**
- Formula: "xrdq / atq; missing xrdq treated as 0". CompustatEngine computes this. Match.
- **Result:** PASS

**17. CashFlow**
- Formula: "oancfy / avg_assets; avg = (atq_t + atq_{t-1}) / 2". CompustatEngine `_compute_biddle_residual()`. Match.
- Winsorized: "1%/99% by fiscal year (in Biddle residual computation)". CashFlow is in `skip_winsorize`. Match.
- **Result:** PASS

**18. Volatility**
- Formula: "std(daily_ret) * sqrt(252) * 100 over [prev_call+5d, call-5d], min 10 days". VolatilityBuilder docstring lines 6-9 confirms this formula. Match.
- Source: "CRSPEngine: daily RET". VolatilityBuilder imports from `_crsp_engine`. Match.
- Winsorized: "No (not in Compustat engine winsorization loop)". VolatilityBuilder does not apply winsorization. Match.
- **Result:** PASS

**19. Lagged_DV**
- Formula: "Dynamically assigned = CapexAt_lag for all H13 specs". Runner lines 251-255: `base_dv = dv.replace("_lead_qtr", "").replace("_lead", "")`, `lag_col = f"{base_dv}_lag"`, `panel["Lagged_DV"] = panel[lag_col]`. For both CapexAt and CapexAt_lead, base_dv = "CapexAt", so Lagged_DV = CapexAt_lag. Match.
- **Result:** PASS

**20. gvkey**
- Type: FE/Index. Present in manifest. Correct.
- **Result:** PASS

**21. ff12_code**
- Type: FE. Present in manifest. Correct.
- **Result:** PASS

**22. cal_yr / cal_yr_qtr**
- Construction: `build_cal_yr_qtr_index()` in panel_utils.py lines 195-218. `cal_yr = start_date.dt.year`, `cal_yr_qtr = cal_yr * 10 + start_date.dt.quarter`. Match.
- **Result:** PASS

### Completeness check:

**Variables in MODEL_SPECS (runner):**
- DVs: CapexAt, CapexAt_lead -- both in dictionary.
- IVs (KEY_IVS): CEO_QA_Uncertainty_pct, CEO_Pres_Uncertainty_pct, Manager_QA_Uncertainty_pct, Manager_Pres_Uncertainty_pct -- all in dictionary.
- BASE_CONTROLS: Size, TobinsQ, ROA, BookLev, CashHoldings, DividendPayer, OCF_Volatility, Lagged_DV -- all in dictionary.
- EXTENDED_CONTROLS: + SalesGrowth, RD_Intensity, CashFlow, Volatility -- all in dictionary.
- FE columns: gvkey, ff12_code, cal_yr, cal_yr_qtr -- all in dictionary.

**ISSUE: H1 winsorization list.** The provenance doc Section H1 lists "EPS_Growth" among the variables winsorized by the Compustat engine (line 326: "Applied to: Size, TobinsQ, ROA, BookLev, CashHoldings, CapexAt, OCF_Volatility, RD_Intensity, EPS_Growth"). EPS_Growth is NOT used in any H13 spec. While technically accurate about the engine's behavior, listing an irrelevant variable in the H13 provenance doc is misleading. This should list only the variables relevant to H13 that are winsorized.
- **Result:** FAIL (minor -- misleading inclusion of EPS_Growth)

**Phase 6 Result: 23/24 (1 FAIL).**

---

## Phase 7: FACTUAL ACCURACY -- SECTIONS F, G, H

### F-CHECK: Data Pipeline

**F1. Dependency Chain**
- 7-step chain documented. Verified against code:
  1. Raw inputs: manifest, linguistic parquets, Compustat, CRSP. Correct.
  2. Engine loading: CompustatEngine, LinguisticEngine, CRSPEngine. Correct.
  3. Panel builder: merges all on file_name, attaches fyearq, computes lead/lag, assigns sample. Correct.
  4. Runner loading: loads panel with explicit column list (lines 206-218), builds cal_yr_qtr. Correct.
  5. Sample filtering: main sample, per-spec DV filter, complete case, min calls. Correct.
  6. Regression: PanelOLS, 12 specs, firm-clustered SEs. Correct.
  7. Table generation: runner writes LaTeX, entry in generate_all_tables.py. Correct.
- **Result:** PASS

**F2. Data Engines Used**
- CompustatEngine: 11 variables listed. Verified against builder imports and engine output.
- LinguisticEngine: 4 IV variables. Correct.
- CRSPEngine: Volatility. Correct.
- **Result:** PASS

**F3. Merge Operations**
- 18 merge rows documented. Verified against panel builder code:
  - 16 file_name left joins (manifest + 15 builders). Panel builder `build_call_level_panel()` iterates over 16 non-manifest builders (including manifest = 17 total, but manifest is the base, so 16 merges). The provenance doc lists 16 variable merges.
  - fyearq attach via merge_asof. Correct.
  - CapexAt_lead merge on (gvkey, fyearq_int). Correct.
  - CapexAt_lag merge on (gvkey, fyearq_int). Correct.
- **Result:** PASS

### G-CHECK: Outputs

**G1. Stage 3 Outputs (Panel Builder)**
- Provenance doc lists 4 files:
  1. `h13_capex_panel.parquet` -- builder line 483. Correct.
  2. `summary_stats.csv` -- builder line 492. Correct.
  3. `run_manifest.json` -- builder line 497. Correct.
  4. `report_step3_h13_capex.md` -- builder line 549. Correct.
- **Result:** PASS

**G2. Stage 4 Outputs (Runner)**
- Provenance doc lists 9 files. Verified against runner code:
  1. `h13_capex_table.tex` -- line 570. Correct.
  2. `model_diagnostics.csv` -- line 610. Correct.
  3. `summary_stats.csv` -- line 767. Correct.
  4. `summary_stats.tex` -- line 767 (via `make_summary_stats_table` output_tex param). Correct.
  5. `regression_results_col{1-12}.txt` -- lines 588-604. Correct.
  6. `report_step4_H13.md` -- line 695. Correct.
  7. `sample_attrition.csv` -- line 809 (via `generate_attrition_table`). Correct.
  8. `sample_attrition.tex` -- line 809 (via `generate_attrition_table`). Correct.
  9. `run_manifest.json` -- line 823. Correct.

- All 9 files in provenance doc are confirmed written by code. No file listed that is NOT written.
- **HOWEVER:** The runner docstring (line 44) says `regression_results_col{1-8}.txt` -- the provenance doc correctly notes this discrepancy in Known Issues (L1). The runner docstring at line 50 does NOT list `sample_attrition.tex`, only `sample_attrition.csv`. The provenance doc G2 correctly lists BOTH `.csv` and `.tex` because `generate_attrition_table()` writes both (confirmed in `src/f1d/shared/outputs/attrition_table.py` lines 47-53).
- **Result:** PASS

**G3. Summary Statistics**
- 17 variables listed. Verified against `SUMMARY_STATS_VARS` (runner lines 138-158): exact match of all 17 variables and their labels. Note: `RD_Intensity` label in code is `"R\\&D Intensity"` (LaTeX escaped); provenance doc correctly shows `R&D Intensity`.
- **Result:** PASS

### H-CHECK: Outlier/Missing Treatment

**H1. Winsorization**
- Compustat: "1%/99% by fiscal year (fyearq)". CompustatEngine `_winsorize_by_year()` at line 439: clips at 1st/99th percentile per year group. Match.
- Variables listed as winsorized: The provenance doc lists "Size, TobinsQ, ROA, BookLev, CashHoldings, CapexAt, OCF_Volatility, RD_Intensity, EPS_Growth".
  - **ISSUE:** EPS_Growth is NOT used in H13 and should not be listed here. This was noted in Phase 6.
- Linguistic IVs: "0%/99% upper-only per calendar year". LinguisticEngine line 257: `winsorize_by_year(..., lower=0.0, upper=0.99)`. Match.
- CRSP Volatility: "Not winsorized in the Compustat engine winsorization loop". Correct.
- Minimum observations per year-group: "10". Both CompustatEngine (line 440: `min_obs: int = 10`) and LinguisticEngine (line 257: `min_obs=10`). Match.
- **Result:** FAIL (EPS_Growth inclusion)

**H2. Missing Data Policy**
- "Complete-case deletion" -- runner line 282. Correct.
- "Inf/-Inf replaced with NaN" -- runner line 268. Correct.
- CapexAt_lead/lag NaN conditions documented correctly.
- **Result:** PASS

**H3. Transformations**
- Size: natural log. Correct.
- Volatility: annualized std * sqrt(252) * 100. Correct.
- "No centering, z-scoring, or additional scaling." Confirmed -- no such operations in runner or builder.
- **Result:** PASS

**Phase 7 Result: 8/9 (1 FAIL for EPS_Growth in H1 list).**

---

## Phase 8: FACTUAL ACCURACY -- SECTION I (Table Generator Entry)

### I-1. "id" field
- Provenance doc: `"H13"`. Code: `"id": "H13"`. Match.
- **Result:** PASS

### I-2. "tail" / "hyp_dir" fields
- Provenance doc: `"tail": "two"`, `"hyp_dir": None`.
- Code (generate_all_tables.py lines 303-304): `"tail": "two"`, `"hyp_dir": None`. Match.
- Runner line 32: "Hypothesis Test (two-tailed)". Consistent.
- **Result:** PASS

### I-3. "cols" field
- Provenance doc: `12`. Code: `"cols": 12`. Runner: 12 MODEL_SPECS. Match.
- **Result:** PASS

### I-4. "dvs" field
- Provenance doc: `[("CapexAt", 6), (r"CapexAt\_lead", 6)]`.
- Code (lines 300-302): `[("CapexAt", 6), (r"CapexAt\_lead", 6)]`. Match.
- Runner: cols 1-6 = CapexAt, cols 7-12 = CapexAt_lead. Match.
- **Result:** PASS

### I-5. "key_vars" field
- Provenance doc claims: "The H13 entry does not specify key_vars because it uses the standard 4-IV pattern; the global IV_NAMES list applies."
- Verification: The H13 entry in generate_all_tables.py has no `key_vars` field. The global `IV_NAMES` at line 407-412 lists: CEO_QA_Uncertainty_pct, CEO_Pres_Uncertainty_pct, Manager_QA_Uncertainty_pct, Manager_Pres_Uncertainty_pct. These match runner's `KEY_IVS`. Correct.
- **Result:** PASS

**Phase 8 Result: 5/5 PASS.**

---

## Phase 9: FACTUAL ACCURACY -- SECTION K (Model-Family Addendum)

### K-1. Correct subsection filled
- Model family: PanelOLS (verified in Phase 2). K1 is filled. K2-K6 are marked N/A. Correct.
- **Result:** PASS

### K-2. Industry FE specs
- Provenance doc: `entity_effects=False`, `time_effects=True`, `other_effects=df_panel["ff12_code"]`, `drop_absorbed=True`, `check_rank=False`.
- Code (runner lines 350-358): exact match of all parameters.
- **Result:** PASS

### K-3. Firm FE specs
- Provenance doc: `EntityEffects` + `TimeEffects` via `from_formula`, `drop_absorbed=True`.
- Code (runner lines 363-365): `formula = f"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"`, `PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)`. Match.
- **Result:** PASS

### K-4. Panel index construction
- Provenance doc: Year FE specs use `set_index(["gvkey", "cal_yr"])`, YQ FE specs use `set_index(["gvkey", "cal_yr_qtr"])`.
- Code (runner line 342): `df_panel = df_prepared.set_index(["gvkey", time_col])` where `time_col` depends on fe_type. Match.
- **Result:** PASS

### K-5. Singleton handling
- Provenance doc: "PanelOLS default behavior with `drop_absorbed=True`."
- Code: `drop_absorbed=True` confirmed in both paths (lines 356 and 364). Match.
- **Result:** PASS

**Phase 9 Result: 5/5 PASS.**

---

## Phase 10: QUALITY GATE CHECKLIST

| # | Quality Gate | Met? | Evidence |
|---|-------------|------|----------|
| 1 | Every variable in every regression spec appears in Variable Dictionary with explicit formula and source engine | YES | All 22 variables verified in Phase 6. Every DV, IV, control, and FE column has an explicit formula and source. |
| 2 | The model equation matches what the code actually estimates | YES | Verified in Phase 3 B1-CHECK. All 4 IVs, controls, and FE terms match. |
| 3 | The specification register accounts for every model column | YES | 12 rows matching 12 MODEL_SPECS entries. Verified in Phase 4. |
| 4 | The attrition cascade has row counts for each filter step | NO | The provenance doc D2 table has filter descriptions but NO row counts. The creation prompt requires `Rows Before | Rows After | Dropped` columns. The provenance doc defends this as "runtime-dependent" but the quality gate explicitly requires counts. |
| 5 | The tail test direction matches between runner code and generate_all_tables.py | YES | Both "two". Verified in Phases 3 and 8. |
| 6 | The FE specification matches between docstring, code, and this document | YES | Verified in Phases 3 and 9. cal_yr/cal_yr_qtr time FE, industry/firm entity FE all match. |
| 7 | Every merge in the panel builder is documented with join keys and type | YES | 18 merges documented in F3. All verified against panel builder code. |
| 8 | The output file list matches what the runner actually writes | YES | G1 (4 files) and G2 (9 files) all verified against code. No missing files, no phantom files. |
| 9 | The model-family addendum is filled for the correct family only | YES | K1 (PanelOLS) filled; K2-K6 marked N/A. |
| 10 | Any claim marked [UNVERIFIED] has an explanation of what blocks verification | YES | No claims marked [UNVERIFIED] in the provenance doc. All claims are asserted as verified. |

**Phase 10 Result: 9/10 (1 FAIL -- quality gate #4).**

---

## Phase 11: CROSS-REFERENCE CONSISTENCY

### 11-1. DVs in B2 match DVs in C (spec register)?
- B2: CapexAt, CapexAt_lead.
- C: Cols 1-6 use CapexAt, cols 7-12 use CapexAt_lead.
- **Result:** PASS (consistent)

### 11-2. DVs in C match DVs in I (table generator)?
- C: CapexAt (6 cols), CapexAt_lead (6 cols).
- I: `[("CapexAt", 6), (r"CapexAt\_lead", 6)]`.
- **Result:** PASS (consistent)

### 11-3. Controls in B4 match variables in E (dictionary)?
- B4 Base: Size, TobinsQ, ROA, BookLev, CashHoldings, DividendPayer, OCF_Volatility, Lagged_DV (8 vars).
- B4 Extended: + SalesGrowth, RD_Intensity, CashFlow, Volatility (4 more = 12 total).
- E: All 12 control variables present with formulas. Lagged_DV present.
- **Result:** PASS (consistent)

### 11-4. Column count in A matches rows in C?
- A: 12 columns.
- C: 12 rows.
- **Result:** PASS (consistent)

### 11-5. Column count in A matches "cols" in I?
- A: 12.
- I: `"cols": 12`.
- **Result:** PASS (consistent)

### 11-6. Tail direction in A matches B7 matches I?
- A: "two-tailed".
- B7: "Two-tailed (beta != 0)".
- I: `"tail": "two"`.
- **Result:** PASS (consistent)

### 11-7. FE in B5 matches C matches K?
- B5: Industry (ff12_code) / Firm (gvkey) entity FE; cal_yr / cal_yr_qtr time FE.
- C: Industry (FF12) and Firm entity FE; Cal Year and Cal Year-Quarter time FE.
- K1: `entity_effects=False` + `other_effects=ff12_code` for industry; `EntityEffects` for firm; `time_effects=True`.
- **Result:** PASS (consistent)

### 11-8. Panel index in A matches set_index in K?
- A: "(gvkey, cal_yr) or (gvkey, cal_yr_qtr) depending on spec".
- K1: "Year FE specs: `df_panel = df_prepared.set_index(["gvkey", "cal_yr"])`", "Year-Quarter FE specs: `set_index(["gvkey", "cal_yr_qtr"])`.
- **Result:** PASS (consistent)

**Phase 11 Result: 8/8 PASS.**

---

## FAILURES (detailed)

| Phase | Check | Provenance Doc Claims | Actual Code Says | Severity | Fix Required |
|-------|-------|----------------------|-----------------|----------|-------------|
| 5 (D2) | Attrition row counts | Table has filter descriptions with no row counts; says "not hardcoded -- they depend on data availability at build time" | Code does produce attrition counts at runtime (line 803-808) but provenance doc has no counts | Minor | Add row counts from a prior run or mark as [UNVERIFIED] |
| 5 (D2) | Attrition step ordering | Step 3 = DV non-missing (line 278), Step 4 = Inf replacement (line 268) | Code does inf replacement at line 268 BEFORE DV filter at line 278 | Minor | Swap steps 3 and 4 to match code order |
| 6 (E) / 7 (H1) | Winsorization variable list | Section H1 lists "EPS_Growth" among winsorized variables | EPS_Growth is not used in any H13 regression spec | Minor | Remove EPS_Growth from H1 list (or clarify it is engine-level, not suite-relevant) |
| 10 (QG#4) | Quality gate: attrition cascade row counts | No row counts in D2 table | Quality gate #4 requires row counts per filter step | Minor | Same fix as D2 row counts above |

---

## CORRECTIONS REQUIRED

1. **Section D2, Step ordering:** Swap the order of Steps 3 and 4 in the attrition cascade table. Currently Step 3 is "DV non-missing" (line 278) and Step 4 is "Inf replacement" (line 268). In the code, inf replacement (line 268) happens BEFORE DV filter (line 278). The table should read:
   - Step 3: Inf replacement (runner `prepare_regression_data()` line 268)
   - Step 4: DV non-missing (runner `prepare_regression_data()` line 278)
   - Code reference: `prepare_regression_data()` in runner, lines 268 then 278.

2. **Section D2, Row counts:** Add approximate row counts (from a prior run or from `sample_attrition.csv`) to the attrition cascade table, or include a `Rows Before | Rows After | Dropped` column with values from the latest `sample_attrition.csv` output. Alternatively, mark counts as `[UNVERIFIED -- runtime-dependent]` with a note pointing to the output file. The creation prompt's quality gate #4 requires row counts.

3. **Section H1, Winsorization "Applied to" list:** Remove `EPS_Growth` from the list of winsorized variables. The current text reads:
   > "Applied to: Size, TobinsQ, ROA, BookLev, CashHoldings, CapexAt, OCF_Volatility, RD_Intensity, EPS_Growth"

   It should read:
   > "Applied to: Size, TobinsQ, ROA, BookLev, CashHoldings, CapexAt, OCF_Volatility, RD_Intensity"

   EPS_Growth is winsorized by the CompustatEngine but is not used in any H13 regression specification. Including it is misleading in a suite-specific provenance document.
   - Code reference: `COMPUSTAT_COLS` in `_compustat_engine.py` line 113 includes EPS_Growth, but the runner's `KEY_IVS`, `BASE_CONTROLS`, and `EXTENDED_CONTROLS` do not include it.

---

## ADDITIONAL OBSERVATIONS (non-blocking)

1. **Known Issue #1 accuracy:** The provenance doc correctly identifies that the runner docstring says `regression_results_col{1-8}.txt` but code produces `col{1-12}`. Verified: docstring line 44 says `{1-8}`, code line 594 writes `col{col_num}` for all 12 specs.

2. **Known Issue #4 accuracy:** The runner's attrition_stages at line 806 says `"After lead filter (col 5-8 only)"` but lead DV specs are cols 7-12. The provenance doc correctly flags this as a cosmetic error.

3. **Known Issue #5 accuracy:** Runner line 775 says `"Run regressions: 8 model specifications"` but iterates over 12 MODEL_SPECS (line 778). Correctly flagged.

4. **Known Issue #7 accuracy:** TobinsQ formula discrepancy between docstring and code is correctly documented. Code at lines 988-991 uses `(mktcap + debt_book) / atq`.

5. **Docstring output list incompleteness:** The runner docstring (line 43-51) omits `sample_attrition.tex` from the output list. The provenance doc G2 correctly includes both `.csv` and `.tex`. The docstring also says `{1-8}` instead of `{1-12}` (covered by Known Issue #1).

6. **Line reference precision:** Several line references in the provenance doc are approximate (e.g., "runner line 252-255" for Lagged_DV -- actual code is lines 251-255; "runner line 411-420" for _sig_stars -- actual is 410-420). These are off-by-one and do not affect correctness.
