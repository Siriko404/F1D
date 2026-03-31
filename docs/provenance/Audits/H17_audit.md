# AUDIT REPORT: Suite H17 Provenance Document

**Audit Date:** 2026-03-30
**Auditor:** Adversarial Code Auditor (automated)
**Provenance Doc:** `docs/provenance/H17.md`
**Runner:** `src/f1d/econometric/run_h17_repurchase_intensity.py`
**Panel Builder:** `src/f1d/variables/build_h17_repurchase_intensity_panel.py`
**Creation Prompt:** `docs/Prompts/Suite Provenance Doc.txt`

---

## AUDIT SUMMARY

| Category | Total Checks | Passed | Failed | Score |
|----------|-------------|--------|--------|-------|
| Structural Completeness (Phase 1) | 26 | 25 | 1 | 96% |
| Suite Identity (Phase 2) | 10 | 10 | 0 | 100% |
| Model Specification (Phase 3) | 7 | 7 | 0 | 100% |
| Spec Register (Phase 4) | 5 | 5 | 0 | 100% |
| Sample Construction (Phase 5) | 3 | 2 | 1 | 67% |
| Variable Dictionary (Phase 6) | 23 | 23 | 0 | 100% |
| Pipeline/Outputs/Treatment (Phase 7) | 9 | 9 | 0 | 100% |
| Table Generator Entry (Phase 8) | 5 | 5 | 0 | 100% |
| Model-Family Addendum (Phase 9) | 6 | 6 | 0 | 100% |
| Quality Gates (Phase 10) | 10 | 9 | 1 | 90% |
| Cross-Reference Consistency (Phase 11) | 8 | 8 | 0 | 100% |
| **TOTAL** | **112** | **110** | **2** | **98%** |

---

## VERDICT

**PASS WITH NOTES**: Two minor issues found that do not affect factual accuracy of the econometric specification or variable construction. Both relate to the attrition cascade table format (missing row counts) as required by the creation prompt.

---

## FAILURES (detailed)

| Phase | Check | Provenance Doc Claims | Actual Code Says | Severity | Fix Required |
|-------|-------|----------------------|-----------------|----------|-------------|
| 1 | D2 Attrition Table Format | Table has 3 columns: Step, Filter, Description | Creation prompt requires 5 columns: Step, Filter, Rows Before, Rows After, Dropped | Minor | Add row count columns (runtime-dependent; mark [UNVERIFIED] with note) |
| 10 | QG#4: Attrition cascade row counts | "Exact counts are recorded in model_diagnostics.csv at runtime" | Creation prompt Quality Gate #4 requires "row counts for each filter step" in the doc itself | Minor | Add placeholder row count columns or mark [UNVERIFIED] |

---

## PHASE 1: STRUCTURAL COMPLETENESS

Checked every section required by the creation prompt (`docs/Prompts/Suite Provenance Doc.txt`) against `docs/provenance/H17.md`.

| Section | Required by Prompt | Present in Doc | Complete | Notes |
|---------|-------------------|----------------|----------|-------|
| A. Suite Identity | Yes | Yes | Yes | YAML block with all 11 fields |
| B. Model Specification | Yes | Yes | Yes | All 7 subsections present |
| B1. Regression Equation | Yes | Yes | Yes | LaTeX equations for both contemporaneous and lead |
| B2. Dependent Variable(s) | Yes | Yes | Yes | Table with 2 DVs + de-cumulation logic |
| B3. Independent Variable(s) | Yes | Yes | Yes | Table with 4 IVs |
| B4. Control Variables | Yes | Yes | Yes | Two tables: Base (9 controls incl Lagged_DV) + Extended (4 additional) |
| B5. Fixed Effects | Yes | Yes | Yes | Table with 4 FE types |
| B6. Standard Errors | Yes | Yes | Yes | cov_type, clustering documented |
| B7. Hypothesis Test | Yes | Yes | Yes | Direction, p-value computation, legacy misnomer noted |
| C. Spec Register | Yes | Yes | Yes | 12-row table matching MODEL_SPECS |
| D. Sample Construction | Yes | Yes | Partial | D1 population present; D2 lacks row counts (see below) |
| D1. Population | Yes | Yes | Yes | Starting dataset, year range |
| D2. Exclusion Criteria | Yes | Yes | **No** | Table has Step/Filter/Description but MISSING Rows Before/Rows After/Dropped columns per creation prompt |
| D3. Sample Counts per Spec | Yes | Yes | Yes | Documents that N varies across specs; defers to model_diagnostics.csv |
| E. Variable Dictionary | Yes | Yes | Yes | 22-row table covering all variables |
| F. Data Pipeline | Yes | Yes | Yes | All 3 subsections present |
| F1. Dependency Chain | Yes | Yes | Yes | 7-step numbered chain |
| F2. Data Engines | Yes | Yes | Yes | 3 engines documented |
| F3. Merge Operations | Yes | Yes | Yes | Multiple merge tables covering panel builder + engine-level |
| G. Outputs | Yes | Yes | Yes | G1, G2, G3 all present |
| G1. Stage 3 Outputs | Yes | Yes | Yes | 3 files listed |
| G2. Stage 4 Outputs | Yes | Yes | Yes | 8 file types listed |
| G3. Summary Statistics | Yes | Yes | Yes | 18 variables with labels + metrics |
| H. Outlier/Missing Treatment | Yes | Yes | Yes | H1, H2, H3 all present |
| I. generate_all_tables Entry | Yes | Yes | Yes | Python dict + verification table |
| J. Reproduction Commands | Yes | Yes | Yes | 3 commands |
| K. Model-Family Addendum | Yes | Yes | Yes | K1 filled (PanelOLS), K2-K6 marked N/A |
| L. Known Issues | Yes | Yes | Yes | 6 issues documented |

**Phase 1 Result: 25/26 PASS. 1 FAIL (D2 missing row counts).**

---

## PHASE 2: FACTUAL ACCURACY -- SECTION A (Suite Identity)

### A-1. Suite ID
- **Claim:** H17
- **Verification:** Matches runner file path and generate_all_tables entry `"id": "H17"`.
- **Result:** PASS

### A-2. Title
- **Claim:** "H17: Speech Uncertainty and Repurchase Intensity"
- **Verification:** Runner docstring line 4: "STAGE 4: Test H17 Repurchase Intensity Hypothesis". Runner LaTeX caption (line 382): "Speech Uncertainty and Repurchase Intensity". generate_all_tables caption (line 395): "H17: Speech Uncertainty and Repurchase Intensity". Matches.
- **Result:** PASS

### A-3. Hypothesis
- **Claim:** "Does managerial speech uncertainty during earnings calls predict the intensity of share repurchases in the current or next fiscal quarter?"
- **Verification:** Runner docstring (lines 9-10): DV = RepurchaseIntensity (contemporaneous) and RepurchaseIntensity_lead_qtr (next quarter). IVs = 4 uncertainty measures. The hypothesis statement accurately captures the research question.
- **Result:** PASS

### A-4. Direction (tail test)
- **Claim:** "two-tailed"
- **Verification:** Runner line 30: "Hypothesis: Two-tailed." Runner line 479: "(two-tailed)". `_sig_stars()` function (line 337-346) uses direct p-value thresholds without one-tailed conversion. Line 329: `meta[f"{iv}_p_one"] = p_two` stores two-tailed p directly.
- **Result:** PASS

### A-5. Model Family
- **Claim:** "PanelOLS"
- **Verification:** Runner line 61: `from linearmodels.panel import PanelOLS`. Lines 287 and 300: `PanelOLS(...)` and `PanelOLS.from_formula(...)`.
- **Result:** PASS

### A-6. Estimator
- **Claim:** "linearmodels.panel.PanelOLS"
- **Verification:** Runner line 61: `from linearmodels.panel import PanelOLS`. Correct fully qualified import path.
- **Result:** PASS

### A-7. Unit of Observation
- **Claim:** "call-level (individual earnings call)"
- **Verification:** Panel builder docstring (line 9): "Unit of observation: individual earnings call (file_name)." Manifest is keyed by `file_name`, each row is one call.
- **Result:** PASS

### A-8. Panel Index
- **Claim:** "(gvkey, cal_yr) for cols 1-4, 7-10; (gvkey, cal_yr_qtr) for cols 5-6, 11-12"
- **Verification:** Runner line 283: `df_panel = df_prepared.set_index(["gvkey", time_col])`. Line 263: `time_col = "cal_yr_qtr" if fe_type.endswith("_yq") else "cal_yr"`. Cols 5-6 have `fe="industry_yq"/"firm_yq"`, cols 11-12 have `fe="industry_yq"/"firm_yq"`. All others are non-`_yq`. Matches.
- **Result:** PASS

### A-9. Columns (number of model specs)
- **Claim:** 12
- **Verification:** Runner lines 93-109: `MODEL_SPECS` contains exactly 12 entries with col numbers 1-12.
- **Result:** PASS

### A-10. Runner and Panel Builder paths
- **Claim:** `src/f1d/econometric/run_h17_repurchase_intensity.py` and `src/f1d/variables/build_h17_repurchase_intensity_panel.py`
- **Verification:** Both files exist and were read successfully.
- **Result:** PASS

**Phase 2 Result: 10/10 PASS.**

---

## PHASE 3: FACTUAL ACCURACY -- SECTION B (Model Specification)

### B1-CHECK: Regression Equation
- **Claim:** Two equations (contemporaneous and lead), each with 4 IVs + Controls + entity FE + time FE.
- **Verification:** Runner line 275: `exog = KEY_IVS + controls`. KEY_IVS has exactly 4 IVs. Controls include Lagged_DV. Entity FE is either Industry (ff12_code via `other_effects`) or Firm (via `EntityEffects`). Time FE is via `time_effects=True`. The equations correctly include all terms.
- **Result:** PASS

### B2-CHECK: Dependent Variable(s)
- **Claim:** RepurchaseIntensity (contemporaneous) and RepurchaseIntensity_lead_qtr (lead).
- **Verification:** Runner MODEL_SPECS: cols 1-6 use `"dv": "RepurchaseIntensity"`, cols 7-12 use `"dv": "RepurchaseIntensity_lead_qtr"`. De-cumulation logic documented in provenance (lines 50-58) matches CompustatEngine code (lines 1040-1087): Q1 = prstkcy.fillna(0), Q2-Q4 = prstkcy - prev_prstkcy within same fyearq, negatives clipped to 0, divided by lagged atq (validated consecutive, gap <= 150 days). Lead construction in panel builder (lines 253-269) matches: shift(-1) within gvkey, consecutive-quarter validation.
- **Result:** PASS

### B3-CHECK: Independent Variable(s)
- **Claim:** 4 IVs: CEO_QA_Uncertainty_pct, CEO_Pres_Uncertainty_pct, Manager_QA_Uncertainty_pct, Manager_Pres_Uncertainty_pct.
- **Verification:** Runner lines 74-79: `KEY_IVS = ["CEO_QA_Uncertainty_pct", "CEO_Pres_Uncertainty_pct", "Manager_QA_Uncertainty_pct", "Manager_Pres_Uncertainty_pct"]`. All 4 are from LinguisticEngine. No centering/transformation applied (correct per doc). Complete match.
- **Result:** PASS

### B4-CHECK: Control Variables
- **Claim:** Base (9 controls including Lagged_DV) + Extended (Base + 4: SalesGrowth, RD_Intensity, CashFlow, Volatility).
- **Verification:** Runner lines 81-88:
  - BASE_CONTROLS = ["Size", "TobinsQ", "ROA", "BookLev", "CapexAt", "CashHoldings", "DividendPayer", "OCF_Volatility", "Lagged_DV"] -- 9 items, matches.
  - EXTENDED_CONTROLS = BASE_CONTROLS + ["SalesGrowth", "RD_Intensity", "CashFlow", "Volatility"] -- 13 items, matches.
- Every control in the code appears in the provenance doc, and vice versa.
- Lagged_DV documented as RepurchaseIntensity_lag. Runner line 210-213 confirms: `base_dv = dv.replace("_lead_qtr", "").replace("_lead", "")`, `lag_col = f"{base_dv}_lag"`, `panel["Lagged_DV"] = panel[lag_col]`. This always lags the base DV. Correct.
- No dynamic control logic.
- **Result:** PASS

### B5-CHECK: Fixed Effects
- **Claim:** Industry (ff12_code) for odd cols, Firm (gvkey) for even cols, Cal Yr (cal_yr) for cols 1-4/7-10, Cal Yr-Qtr (cal_yr_qtr) for cols 5-6/11-12.
- **Verification:** Runner lines 286-301:
  - Industry: `PanelOLS(entity_effects=False, time_effects=True, other_effects=df_panel["ff12_code"])`. Odd cols have `fe="industry"` or `fe="industry_yq"`.
  - Firm: `PanelOLS.from_formula(... + EntityEffects + TimeEffects)`. Even cols have `fe="firm"` or `fe="firm_yq"`.
  - Time: `time_effects=True` on both paths. `time_col = "cal_yr_qtr" if fe_type.endswith("_yq") else "cal_yr"` (line 263).
  - `cal_yr` and `cal_yr_qtr` derived from `start_date` via `build_cal_yr_qtr_index()` in `panel_utils.py` (lines 195-218). Confirmed calendar, not fiscal.
- Complete match.
- **Result:** PASS

### B6-CHECK: Standard Errors
- **Claim:** `cov_type="clustered"`, `cluster_entity=True` (firm-level).
- **Verification:** Runner line 296: `model.fit(cov_type="clustered", cluster_entity=True)`. Line 301: same. Both paths use identical SE specification.
- **Result:** PASS

### B7-CHECK: Hypothesis Test
- **Claim:** Two-tailed. P-values from PanelOLS used directly. Stars: *** p<0.01, ** p<0.05, * p<0.10. Legacy `_p_one` misnomer noted.
- **Verification:** `_sig_stars()` (lines 337-346): returns "***" if p < 0.01, "**" if p < 0.05, "*" if p < 0.10, else "". Line 325: `p_two = float(model.pvalues.get(iv, np.nan))`. Line 329: `meta[f"{iv}_p_one"] = p_two`. No one-tailed conversion. LaTeX notes (line 479): "(two-tailed)". All matches.
- **Result:** PASS

**Phase 3 Result: 7/7 PASS.**

---

## PHASE 4: FACTUAL ACCURACY -- SECTION C (Spec Register)

### Check 1: Row count matches MODEL_SPECS
- Provenance doc has 12 rows (cols 1-12). Runner MODEL_SPECS has 12 entries (cols 1-12). PASS.

### Check 2: DV per row
- Cols 1-6 in doc: RepurchaseIntensity. Code: `"dv": "RepurchaseIntensity"` for cols 1-6. PASS.
- Cols 7-12 in doc: RepurchaseIntensity_lead_qtr. Code: `"dv": "RepurchaseIntensity_lead_qtr"` for cols 7-12. PASS.

### Check 3: Entity FE per row
- Doc: Odd cols = Industry (FF12), Even cols = Firm. Code: col 1 = `"fe": "industry"`, col 2 = `"fe": "firm"`, col 3 = `"fe": "industry"`, col 4 = `"fe": "firm"`, col 5 = `"fe": "industry_yq"` (industry entity + yq time), col 6 = `"fe": "firm_yq"`, etc. Doc correctly maps odd to Industry and even to Firm. PASS.

### Check 4: Time FE per row
- Doc: Cols 1-4, 7-10 = Cal Yr. Cols 5-6, 11-12 = Cal Yr-Qtr.
- Code: Cols 1-4 have `fe` without `_yq` suffix, so `time_col = "cal_yr"`. Cols 5-6 have `_yq` suffix, so `time_col = "cal_yr_qtr"`. Same pattern for 7-12. PASS.

### Check 5: Controls per row
- Doc: Cols 1-2, 7-8 = Base. Cols 3-6, 9-12 = Extended.
- Code: col 1 = `"controls": "base"`, col 2 = `"controls": "base"`, col 3 = `"controls": "extended"`, etc. Col 7 = base, col 8 = base, col 9 = extended, col 10 = extended, col 11 = extended, col 12 = extended. Matches doc layout. PASS.

**Phase 4 Result: 5/5 PASS.**

---

## PHASE 5: FACTUAL ACCURACY -- SECTION D (Sample Construction)

### D1-CHECK: Population
- **Claim:** Starting from `master_sample_manifest.parquet` (Stage 1.4), ~112,968 calls, 2002-2018.
- **Verification:** Panel builder line 21: `outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet`. Year range from config (variable, but project scope is 2002-2018 per memory). Call count of ~112,968 consistent with project scope.
- **Result:** PASS

### D2-CHECK: Exclusion Criteria
- **Filter order claim:** Full panel -> Main sample (excl FF12=8,11) -> DV non-missing -> Complete case -> Min calls per firm (>=5).
- **Verification against runner code:**
  1. `load_panel()` loads full panel (line 178).
  2. `filter_main_sample()` (line 565): `panel[~panel["ff12_code"].isin([8, 11])]`. Correct.
  3. `prepare_regression_data()`, line 229: `df = df[df[dv].notna()]`. Correct.
  4. Line 233: `complete_mask = df[required].notna().all(axis=1)`. Correct.
  5. Lines 237-239: `firm_counts >= MIN_CALLS_PER_FIRM` (=5). Correct.
- **Filter order matches code execution order.** PASS.
- **Row counts:** The provenance doc does NOT include row count columns (Rows Before, Rows After, Dropped) in the attrition table. The creation prompt specifies these columns. The doc says "Exact counts are recorded in `model_diagnostics.csv` at runtime" which is reasonable since counts are runtime-dependent, but the creation prompt template shows row count columns.
- **Result:** FAIL (missing row count columns per creation prompt requirement)

### D3-CHECK: Sample Counts per Spec
- **Claim:** N varies across specs due to different DVs, extended controls missingness, and cal_yr_qtr coverage.
- **Verification:** This is accurate. Different DVs (contemporaneous vs lead) have different non-null counts. Extended controls add SalesGrowth/RD_Intensity/CashFlow/Volatility which may have additional NaN. YQ specs require cal_yr_qtr. Accurate reasoning.
- **Result:** PASS

**Phase 5 Result: 2/3 PASS, 1 FAIL.**

---

## PHASE 6: FACTUAL ACCURACY -- SECTION E (Variable Dictionary)

Checked EVERY row in the Variable Dictionary against source code.

### DVs

| Variable | Name Match | Formula Correct | Source Correct | Winsorized Correct | Timing Correct | Result |
|----------|-----------|----------------|---------------|-------------------|---------------|--------|
| RepurchaseIntensity | Yes | Yes: quarterly_prstkcy / atq_{t-1}, de-cumulated, negatives clamped | Yes: CompustatEngine, prstkcy, atq, fqtr, fyearq | Yes: 1%/99% by fyearq (in COMPUSTAT_COLS, not in skip_winsorize) | Yes: Contemporaneous | PASS |
| RepurchaseIntensity_lead_qtr | Yes | Yes: Next consecutive fiscal quarter's RI, via fiscal_qtr_id shifting | Yes: Panel builder shift(-1) with consecutive validation | Yes: Inherited from RI | Yes: Lead (t+1 qtr) | PASS |
| RepurchaseIntensity_lag | Yes | Yes: Previous consecutive fiscal quarter's RI | Yes: Panel builder shift(+1) with consecutive validation | Yes: Inherited | Yes: Lag (t-1 qtr) | PASS |

### Lagged_DV

| Variable | Name Match | Formula Correct | Source Correct | Winsorized Correct | Timing Correct | Result |
|----------|-----------|----------------|---------------|-------------------|---------------|--------|
| Lagged_DV | Yes | Yes: = RepurchaseIntensity_lag (always lags base DV) | Yes: Runner line 213: panel["RepurchaseIntensity_lag"] | Yes: Inherited | Yes: Lag (t-1 qtr) | PASS |

### IVs

| Variable | Name Match | Formula Correct | Source Correct | Winsorized Correct | Timing Correct | Result |
|----------|-----------|----------------|---------------|-------------------|---------------|--------|
| CEO_QA_Uncertainty_pct | Yes: exact string in KEY_IVS | Yes: (unc words / total words) * 100, CEO QA | Yes: LinguisticEngine | Yes: No (bounded [0,100]) | Yes: Contemporaneous | PASS |
| CEO_Pres_Uncertainty_pct | Yes | Yes | Yes: LinguisticEngine | Yes: No | Yes | PASS |
| Manager_QA_Uncertainty_pct | Yes | Yes | Yes: LinguisticEngine | Yes: No | Yes | PASS |
| Manager_Pres_Uncertainty_pct | Yes | Yes | Yes: LinguisticEngine | Yes: No | Yes | PASS |

### Controls

| Variable | Name Match | Formula Correct | Source Correct | Winsorized Correct | Timing Correct | Result |
|----------|-----------|----------------|---------------|-------------------|---------------|--------|
| Size | Yes | Yes: ln(atq), NaN when atq <= 0 | Yes: CompustatEngine: atq | Yes: 1%/99% by fyearq (in COMPUSTAT_COLS) | Yes | PASS |
| TobinsQ | Yes | Yes: (cshoq * prccq + dlcq + dlttq) / atq | Yes: CompustatEngine | Yes: 1%/99% by fyearq | Yes | PASS |
| ROA | Yes | Yes: iby_annual (Q4) / avg_assets | Yes: CompustatEngine | Yes: 1%/99% by fyearq | Yes | PASS |
| BookLev | Yes | Yes: (dlcq.fillna(0) + dlttq.fillna(0)) / atq | Yes: CompustatEngine | Yes: 1%/99% by fyearq | Yes | PASS |
| CapexAt | Yes | Yes: capxy_annual (Q4) / atq_lag1_annual | Yes: CompustatEngine | Yes: 1%/99% by fyearq | Yes | PASS |
| CashHoldings | Yes | Yes: cheq / atq | Yes: CompustatEngine | Yes: 1%/99% by fyearq | Yes | PASS |
| DividendPayer | Yes | Yes: 1 if dvy_annual > 0, else 0 | Yes: CompustatEngine | Yes: No (binary, in skip_winsorize) | Yes | PASS |
| OCF_Volatility | Yes | Yes: Rolling 5-yr std (min 3 yrs) of oancfy/atq_{t-1} | Yes: CompustatEngine | Yes: 1%/99% by fyearq | Yes | PASS |
| SalesGrowth | Yes | Yes: (saley_t - saley_{t-1}) / abs(saley_{t-1}), Q4 saley with saleq fallback | Yes: CompustatEngine | Yes: 1%/99% by fyearq inside Biddle (in skip_winsorize for main loop) | Yes | PASS |
| RD_Intensity | Yes | Yes: xrdq.fillna(0) / atq | Yes: CompustatEngine | Yes: 1%/99% by fyearq | Yes | PASS |
| CashFlow | Yes | Yes: oancfy / avg_assets, fallback to atq_t | Yes: CompustatEngine | Yes: 1%/99% by fyearq inside Biddle (in skip_winsorize for main loop) | Yes | PASS |
| Volatility | Yes | Yes: std(daily_ret) * sqrt(252) * 100 | Yes: CRSPEngine | Yes: No | Yes | PASS |

### FE Columns

| Variable | Name Match | Formula Correct | Source Correct | Winsorized Correct | Timing Correct | Result |
|----------|-----------|----------------|---------------|-------------------|---------------|--------|
| ff12_code | Yes | Yes: SIC-based industry classification | Yes: ManifestFieldsBuilder | Yes: No | Yes: Static | PASS |
| gvkey | Yes | Yes: Compustat firm identifier, zero-padded 6 digits | Yes: ManifestFieldsBuilder | Yes: No | Yes: Static | PASS |
| cal_yr | Yes | Yes: start_date.dt.year | Yes: panel_utils.build_cal_yr_qtr_index (line 215) | Yes: No | Yes: Contemporaneous | PASS |
| cal_yr_qtr | Yes | Yes: cal_yr * 10 + start_date.dt.quarter | Yes: panel_utils.build_cal_yr_qtr_index (line 217) | Yes: No | Yes: Contemporaneous | PASS |

### Completeness Check
All variables in MODEL_SPECS are covered:
- DVs: RepurchaseIntensity, RepurchaseIntensity_lead_qtr -- in dictionary
- IVs: CEO_QA_Uncertainty_pct, CEO_Pres_Uncertainty_pct, Manager_QA_Uncertainty_pct, Manager_Pres_Uncertainty_pct -- in dictionary
- BASE_CONTROLS: Size, TobinsQ, ROA, BookLev, CapexAt, CashHoldings, DividendPayer, OCF_Volatility, Lagged_DV -- all in dictionary
- EXTENDED add-ons: SalesGrowth, RD_Intensity, CashFlow, Volatility -- all in dictionary
- FE columns: gvkey, ff12_code, cal_yr, cal_yr_qtr -- all in dictionary
- Lagged_DV source (RepurchaseIntensity_lag) -- in dictionary
- No variables missing.

**Phase 6 Result: 23/23 PASS.**

---

## PHASE 7: FACTUAL ACCURACY -- SECTIONS F, G, H

### F-CHECK: Data Pipeline

**F1: Dependency Chain (7 steps)**
1. Raw inputs: Compustat parquet, linguistic outputs, CRSP, manifest. Verified correct file paths.
2. Engine loading: CompustatEngine, LinguisticEngine, CRSPEngine. All three are used by the panel builder's 18 builders.
3. Panel builder: Merges all builder outputs via `file_name` (left join). Creates lead/lag via fiscal_qtr_id. Assigns sample. Saves parquet. All correct per builder code.
4. Runner loading: Loads panel parquet, calls `build_cal_yr_qtr_index()`. Verified at runner lines 178-186.
5. Sample filtering: Creates Lagged_DV, replaces inf, drops DV-missing, complete-case, min calls. Verified at runner lines 199-243.
6. Regression: 12 PanelOLS models. Verified at runner lines 250-334.
7. Table generation: generate_all_tables.py entry. Verified entry exists at line 392.
- **Result:** PASS

**F2: Data Engines**
- CompustatEngine provides RepurchaseIntensity + all Compustat controls + fqtr. Verified via RepurchaseIntensityBuilder (returns `["file_name", "RepurchaseIntensity", "fqtr"]`) and all control builders.
- LinguisticEngine provides 4 uncertainty IVs. Verified via 4 uncertainty builders.
- CRSPEngine provides Volatility. Verified via VolatilityBuilder.
- **Result:** PASS

**F3: Merge Operations**
- Panel builder: manifest base merged with each builder output on `file_name` (left join, 1:1). Verified at builder lines 137-153.
- Lead merge: panel merged with lead_lookup on `["gvkey", "fiscal_qtr_id"]` (left join). Verified at builder line 278.
- Lag merge: panel merged with lag_lookup on `["gvkey", "fiscal_qtr_id"]` (left join). Verified at builder line 305.
- CompustatEngine internal: merge_asof backward on gvkey (by), start_date/datadate (asof). Verified via engine match_to_manifest pattern.
- fqtr attachment: merge_asof per gvkey group when fqtr missing. Verified at builder lines 196-226.
- All merge keys and types are documented correctly.
- **Result:** PASS

### G-CHECK: Outputs

**G1: Stage 3 Outputs (Panel Builder)**
Code writes (builder lines 380-395):
1. `h17_repurchase_intensity_panel.parquet` -- line 381. Documented. PASS.
2. `summary_stats.csv` -- line 386. Documented. PASS.
3. `run_manifest.json` -- line 390 (`generate_manifest`). Documented. PASS.
No `report_step3_*.md` is written (confirmed by grep). Provenance doc correctly omits it.

**G2: Stage 4 Outputs (Runner)**
Code writes (runner lines 491-630):
1. `h17_repurchase_intensity_table.tex` -- line 491. Documented. PASS.
2. `model_diagnostics.csv` -- line 526. Documented. PASS.
3. `summary_stats.csv` + `summary_stats.tex` -- lines 582-583. Documented. PASS.
4. `sample_attrition.csv` + `sample_attrition.tex` -- line 620 (`generate_attrition_table`). Documented. PASS.
5. `regression_results_col{1-12}.txt` -- line 511. Documented. PASS.
6. `run_manifest.json` -- line 624 (`generate_manifest`). Documented. PASS.
No files in code are missing from doc. No files in doc are absent from code.
- **Result:** PASS

**G3: Summary Statistics**
- 18 variables listed in provenance doc's G3 table.
- Runner lines 119-138: `SUMMARY_STATS_VARS` has exactly 18 entries.
- Every variable/label pair matches between doc and code.
- Minor note: RD_Intensity label in code is `r"R\&D Intensity"` (LaTeX escaped), doc shows `R&D Intensity`. This is a rendering difference, not a factual error -- the same label will appear in the LaTeX output.
- Metrics: "N, Mean, SD, Min, P25, Median, P75, Max (via make_summary_stats_table)". This is standard for the shared utility.
- **Result:** PASS

### H-CHECK: Outlier/Missing Treatment

**H1: Winsorization**
- **Claim:** 1%/99% by fiscal year (fyearq) at CompustatEngine level, min 10 obs per year group.
- **Verification:** `_winsorize_by_year()` at engine line 439: 1%/99%, `min_obs=10`. Grouping column is `comp["fyearq"]` (line 1133). Correct.
- **Applied to:** Doc lists Size, TobinsQ, ROA, BookLev, CapexAt, CashHoldings, OCF_Volatility, RD_Intensity, RepurchaseIntensity. Code: `winsorize_cols = [c for c in COMPUSTAT_COLS if c not in skip_winsorize]` where skip_winsorize = {DividendPayer, CashFlow, SalesGrowth, fqtr}. RepurchaseIntensity IS in COMPUSTAT_COLS (line 135) and NOT in skip_winsorize, so it IS winsorized. All other listed variables are in COMPUSTAT_COLS and not skipped. Correct.
- **NOT applied to:** Linguistic IVs (bounded), DividendPayer (binary, in skip), Volatility (CRSP), fqtr (identifier, in skip). CashFlow and SalesGrowth winsorized inside Biddle, skipped in main loop. All correct.
- **Result:** PASS

**H2: Missing Data Policy**
- Complete-case deletion: runner line 233. Inf/NaN replacement: runner line 224 (`df.replace([np.inf, -np.inf], np.nan)`) and engine lines 1109-1110. RepurchaseIntensity set to NaN conditions: all correctly documented.
- **Result:** PASS

**H3: Transformations**
- Size = ln(atq). Correct.
- OCF_Volatility = rolling std. Correct.
- Volatility = annualized (sqrt(252) * 100). Correct.
- No centering/z-scoring on IVs or DV. Correct.
- **Result:** PASS

**Phase 7 Result: 9/9 PASS.**

---

## PHASE 8: FACTUAL ACCURACY -- SECTION I (Table Generator Entry)

### Entry verification against `outputs/generate_all_tables.py` lines 391-404:

| Field | Provenance Doc Claims | generate_all_tables.py Actual | Match? |
|-------|----------------------|------------------------------|--------|
| id | "H17" | "H17" | PASS |
| dir | "h17_repurchase_intensity/2026-03-27_095020" | "h17_repurchase_intensity/2026-03-27_095020" | PASS |
| caption | "H17: Speech Uncertainty and Repurchase Intensity" | "H17: Speech Uncertainty and Repurchase Intensity" | PASS |
| label | "tab:h17" | "tab:h17" | PASS |
| cols | 12 | 12 | PASS |
| dvs | [("RepurchaseIntensity", 6), (r"RepurchaseIntensity\_lead\_qtr", 6)] | [("RepurchaseIntensity", 6), (r"RepurchaseIntensity\_lead\_qtr", 6)] | PASS |
| tail | "two" | "two" | PASS |
| hyp_dir | None | None | PASS |

### Cross-verification with runner:
- tail = "two" matches runner line 30 "Hypothesis: Two-tailed." PASS.
- hyp_dir = None matches two-tailed (no direction). PASS.
- cols = 12 matches `len(MODEL_SPECS) = 12`. PASS.
- dvs: 6 contemporaneous + 6 lead matches MODEL_SPECS (cols 1-6 = RepurchaseIntensity, cols 7-12 = RepurchaseIntensity_lead_qtr). PASS.

Note: H17 entry has no `key_vars` or `key_tails` fields, which is correct -- only certain suites (e.g., H0.3, H1.1) use these. The provenance doc correctly does not mention them.

**Phase 8 Result: 5/5 PASS.**

---

## PHASE 9: FACTUAL ACCURACY -- SECTION K (Model-Family Addendum)

### K1. PanelOLS Specifics (FILLED -- correct family)

| Claim | Verification | Result |
|-------|-------------|--------|
| Industry FE: `other_effects=df_panel["ff12_code"]`, `entity_effects=False`, `time_effects=True` | Runner lines 287-295: `PanelOLS(entity_effects=False, time_effects=True, other_effects=df_panel["ff12_code"], drop_absorbed=True, check_rank=False)` | PASS |
| Firm FE: `EntityEffects` in `PanelOLS.from_formula()` with `TimeEffects` | Runner lines 298-300: `formula = f"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"`, `PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)` | PASS |
| `time_effects=True` for both paths | API path: explicit. Formula path: via `+ TimeEffects`. | PASS |
| `drop_absorbed=True` for all specifications | Runner line 293 (API path) and line 300 (formula path). Both True. | PASS |
| `check_rank=False` for industry FE; default for firm FE | Runner line 294: `check_rank=False` (industry path only). Formula path does not specify `check_rank`, so defaults. | PASS |
| R-squared: overall R2 + manual Adj R2 = 1 - (1-R2)*(nobs-1)/df_resid | Runner line 307: `model.rsquared` and `1 - (1 - model.rsquared) * (model.nobs - 1) / model.df_resid`. | PASS |

### K2-K6: All marked N/A. Correct (model family is PanelOLS only).

**Phase 9 Result: 6/6 PASS.**

---

## PHASE 10: QUALITY GATE CHECKLIST

| # | Quality Gate | Met? | Evidence |
|---|-------------|------|----------|
| 1 | Every variable in every regression spec appears in Variable Dictionary with explicit formula and source engine | **Yes** | All 22 variables verified in Phase 6 with formulas and sources |
| 2 | The model equation matches what the code actually estimates | **Yes** | Phase 3 B1-CHECK confirmed all terms present |
| 3 | The specification register accounts for every model column | **Yes** | Phase 4: 12 rows match 12 MODEL_SPECS entries |
| 4 | The attrition cascade has row counts for each filter step | **No** | Section D2 has filter descriptions but no row count columns (Rows Before/Rows After/Dropped). Doc defers to runtime model_diagnostics.csv. |
| 5 | The tail test direction matches between runner code and generate_all_tables.py | **Yes** | Phase 8: "two" in both; runner line 30 confirms |
| 6 | The FE specification matches between docstring, code, and this document | **Yes** | Runner docstring (lines 21-22, 38), code (lines 263, 283, 287-301), doc Section B5 -- all consistent |
| 7 | Every merge in the panel builder is documented with join keys and type | **Yes** | Phase 7 F3: all 5 merge operations documented with correct keys |
| 8 | The output file list matches what the runner actually writes | **Yes** | Phase 7 G1+G2: all files verified, none missing, none extra |
| 9 | The model-family addendum is filled for the correct family only | **Yes** | Phase 9: K1 (PanelOLS) filled, K2-K6 marked N/A |
| 10 | Any claim marked [UNVERIFIED] has an explanation of what blocks verification | **Yes** | No [UNVERIFIED] claims exist in the document |

**Phase 10 Result: 9/10 PASS, 1 FAIL (QG#4).**

---

## PHASE 11: CROSS-REFERENCE CONSISTENCY

### 1. DVs in Section B2 match Section C (spec register)?
- B2: RepurchaseIntensity, RepurchaseIntensity_lead_qtr.
- C: Cols 1-6 = RepurchaseIntensity, Cols 7-12 = RepurchaseIntensity_lead_qtr.
- **CONSISTENT.** PASS.

### 2. DVs in Section C match Section I (table generator)?
- C: RepurchaseIntensity (6 cols), RepurchaseIntensity_lead_qtr (6 cols).
- I: `"dvs": [("RepurchaseIntensity", 6), ("RepurchaseIntensity\_lead\_qtr", 6)]`.
- **CONSISTENT.** PASS.

### 3. Controls in Section B4 match Section E (variable dictionary)?
- B4 Base: Size, TobinsQ, ROA, BookLev, CapexAt, CashHoldings, DividendPayer, OCF_Volatility, Lagged_DV.
- B4 Extended adds: SalesGrowth, RD_Intensity, CashFlow, Volatility.
- E: All 13 control variables present with formulas + Lagged_DV source (RepurchaseIntensity_lag).
- **CONSISTENT.** PASS.

### 4. Column count in Section A matches rows in Section C?
- A: Columns = 12.
- C: 12 rows (cols 1-12).
- **CONSISTENT.** PASS.

### 5. Column count in Section A matches "cols" in Section I?
- A: Columns = 12.
- I: `"cols": 12`.
- **CONSISTENT.** PASS.

### 6. Tail direction in Section A matches B7 matches I?
- A: "two-tailed".
- B7: "Direction: Two-tailed".
- I: `"tail": "two"`, `"hyp_dir": None`.
- **CONSISTENT.** PASS.

### 7. FE in Section B5 matches Section C matches Section K?
- B5: Industry (ff12_code) for odd cols, Firm (gvkey) for even cols, Cal Yr or Cal Yr-Qtr.
- C: Odd = Industry (FF12), Even = Firm. Cols 1-4/7-10 = Cal Yr, Cols 5-6/11-12 = Cal Yr-Qtr.
- K1: Industry FE via `other_effects`, Firm FE via `EntityEffects`, time via `time_effects=True`.
- **CONSISTENT.** PASS.

### 8. Panel index in Section A matches set_index in Section K?
- A: `(gvkey, cal_yr)` for cols 1-4/7-10; `(gvkey, cal_yr_qtr)` for cols 5-6/11-12.
- K1: `cal_yr` used as time index for Calendar Year FE; `cal_yr_qtr` for Year-Quarter FE.
- Code: `df_panel = df_prepared.set_index(["gvkey", time_col])` where `time_col` switches.
- **CONSISTENT.** PASS.

**Phase 11 Result: 8/8 PASS.**

---

## CORRECTIONS REQUIRED

### Correction 1: Section D2 -- Add Row Count Columns to Attrition Table

**Section:** D. Sample Construction > D2. Exclusion Criteria
**Current (wrong) text:**

```
| Step | Filter | Description |
|------|--------|-------------|
| 1 | Full panel | All calls from master manifest within year range |
| 2 | Main sample | Exclude FF12 = 8 (Utility) and FF12 = 11 (Finance) |
| 3 | DV non-missing | Drop rows where DV ... is NaN |
| 4 | Complete case | Drop rows where any required variable ... is NaN |
| 5 | Min calls per firm | Require >= 5 calls per firm (gvkey) |
```

**Should say instead:** Add "Rows Before", "Rows After", and "Dropped" columns per the creation prompt template. Since exact counts are runtime-dependent (the pipeline was run at a specific point in time), the doc should either:
- (a) Include the actual counts from the most recent run, or
- (b) Mark the counts as [UNVERIFIED -- runtime-dependent; see `sample_attrition.csv` and `model_diagnostics.csv` for actual values], which satisfies Quality Gate #10.

**Code reference:** Runner lines 614-620 call `generate_attrition_table()` which writes `sample_attrition.csv` with the actual row counts. The values passed are `full_n`, `main_n`, `n_dv_valid`, and `first["n_obs"]`. These are runtime values.

**Severity:** Minor. The filter descriptions and ordering are correct. Only the row count columns are missing.

---

## ADDITIONAL NOTES (not failures)

1. **RD_Intensity summary stats label**: The code uses `r"R\&D Intensity"` (LaTeX-escaped), while the provenance doc Section G3 shows `R&D Intensity` (unescaped). This is a rendering-level difference -- both represent the same string in LaTeX output. Not a factual error.

2. **LaTeX label discrepancy (informational)**: The runner's own table uses `\label{tab:h17_repurchase_intensity}` (line 382), while generate_all_tables.py uses `"label": "tab:h17"` (line 396). These are two different output contexts (runner's standalone table vs generate_all_tables regenerated table). The provenance doc correctly documents the generate_all_tables entry, which is the canonical publication label.

3. **`fyearq_int` in required columns**: The runner's `prepare_regression_data()` at line 215 includes `"fyearq_int"` in the `required` list, meaning rows with NaN `fyearq_int` are dropped at the complete-case step. This column is not used as an FE or in regressions, but it IS required for the data to pass the complete-case filter. The provenance doc does not explicitly call this out in the variable dictionary or attrition description. However, `fyearq_int` is derived from `fyearq` (panel builder line 186: `panel["fyearq_int"] = pd.to_numeric(panel["fyearq"], errors="coerce")`), and its presence is a consequence of the fiscal quarter identification needed for lead/lag construction. This is a minor documentation gap but does not affect accuracy of any regression claim.

4. **`cal_yr` not in required list for non-YQ specs**: For non-YQ specifications, `cal_yr` is used as the time index (`set_index(["gvkey", "cal_yr"])`) but is NOT in the `required` list at line 215. This means rows with NaN `cal_yr` would not be filtered out at the complete-case step, but would cause issues at `set_index`. In practice, `cal_yr` is derived from `start_date.dt.year` and would only be NaN if `start_date` cannot be parsed, which would also cause other failures. This is a minor robustness note, not a provenance doc error.
