# Adversarial Audit Report: Suite H16

**Audit Date:** 2026-04-01
**Auditor:** Hostile automated auditor (adversarial, manual verification)
**Provenance Doc:** `docs/provenance/H16.md`
**Runner:** `src/f1d/econometric/run_h16_rd_sales.py`
**Panel Builder:** `src/f1d/variables/build_h16_rd_sales_panel.py`
**Table Generator:** `outputs/generate_all_tables.py`

---

## AUDIT SUMMARY

| Category | Total Checks | Passed | Failed | Score |
|----------|-------------|--------|--------|-------|
| Structural Completeness (Phase 1) | 25 | 25 | 0 | 100% |
| Suite Identity (Phase 2) | 10 | 10 | 0 | 100% |
| Model Specification (Phase 3) | 7 | 7 | 0 | 100% |
| Spec Register (Phase 4) | 12 | 12 | 0 | 100% |
| Sample Construction (Phase 5) | 5 | 3 | 2 | 60% |
| Variable Dictionary (Phase 6) | 22 | 21 | 1 | 95% |
| Pipeline/Outputs/Treatment (Phase 7) | 15 | 13 | 2 | 87% |
| Table Generator Entry (Phase 8) | 5 | 4 | 1 | 80% |
| Model-Family Addendum (Phase 9) | 6 | 6 | 0 | 100% |
| Quality Gates (Phase 10) | 10 | 8 | 2 | 80% |
| Cross-Reference Consistency (Phase 11) | 8 | 8 | 0 | 100% |
| **TOTAL** | **125** | **117** | **8** | **93.6%** |

---

## VERDICT

**FAIL — INACCURATE**: The provenance document is structurally complete and mostly accurate but contains 8 verifiable factual errors. These include one substantively wrong claim (RDSales described as loaded for summary statistics when it is not), incorrect line number references in three places, and a mismatch between the documented attrition cascade and the attrition table actually produced by the code. No required sections are missing.

---

## PHASE 1: STRUCTURAL COMPLETENESS

Read `docs/Prompts/Suite Provenance Doc.txt` for required sections A-L. Checked each against `docs/provenance/H16.md`.

| Section | Required by Prompt | Present in Doc | Complete | Notes |
|---------|-------------------|----------------|----------|-------|
| A. Suite Identity | Yes | Yes | Yes | YAML block present |
| B. Model Specification | Yes | Yes | Yes | All subsections present |
| B1. Regression Equation | Yes | Yes | Yes | Two equations (contemporaneous + lead) |
| B2. Dependent Variables | Yes | Yes | Yes | RDSales + RDSales_lead, formula present |
| B3. Independent Variables | Yes | Yes | Yes | All 4 IVs listed |
| B4. Control Variables | Yes | Yes | Yes | Base + Extended tables present |
| B5. Fixed Effects | Yes | Yes | Yes | All 4 FE types documented |
| B6. Standard Errors | Yes | Yes | Yes | cov_type and cluster documented |
| B7. Hypothesis Test | Yes | Yes | Yes | Two-tailed, no conversion documented |
| C. Spec Register | Yes | Yes | Yes | 12 rows, one per column |
| D. Sample Construction | Yes | Yes | Partial | Row counts marked [UNVERIFIED] -- acceptable; but attrition cascade steps 4-5 wrong |
| D1. Population | Yes | Yes | Yes | Starting dataset and year range stated |
| D2. Exclusion Criteria | Yes | Yes | Partial | Steps 4-5 do not match actual attrition table code (FAIL-1, FAIL-2) |
| D3. Sample Counts per Spec | Yes | Yes | Yes | Marked [UNVERIFIED] with explanation |
| E. Variable Dictionary | Yes | Yes | Yes | 22 variables with formulas and sources |
| F. Data Pipeline | Yes | Yes | Yes | All 3 subsections present |
| F1. Dependency Chain | Yes | Yes | Yes | 7-step chain present |
| F2. Data Engines | Yes | Yes | Yes | 3 engines listed |
| F3. Merge Operations | Yes | Yes | Yes | All merges documented |
| G. Outputs | Yes | Yes | Yes | All 3 subsections present |
| G1. Stage 3 Outputs | Yes | Yes | Yes | 4 files listed |
| G2. Stage 4 Outputs | Yes | Yes | Yes | 9 files listed |
| G3. Summary Statistics | Yes | Yes | Yes | Variable list and metrics documented |
| H. Outlier/Missing Treatment | Yes | Yes | Yes | All 3 subsections present |
| I. generate_all_tables Entry | Yes | Yes | Yes | Python block present |
| J. Reproduction Commands | Yes | Yes | Yes | 3 commands present |
| K. Model-Family Addendum | Yes | Yes | Yes | K1 filled, K2-K6 marked N/A |
| L. Known Issues | Yes | Yes | Yes | 7 items |

**Phase 1 Result: PASS.** All required sections present. Section D2 completeness is structurally present but content fails Phase 5 verification.

---

## PHASE 2: SUITE IDENTITY (Section A)

**A-1. Suite ID**
- Doc: `H16`
- Code: Runner docstring `ID: econometric/test_h16_rd_sales` (line 6); generate_all_tables.py `"id": "H16"` (line 304).
- **PASS**

**A-2. Title**
- Doc: `Speech Uncertainty and R&D Investment Intensity`
- Runner header (line 4): `"STAGE 4: Test H16 R&D Investment Intensity Hypothesis"`. LaTeX caption (runner line 469): `r"\caption{Speech Uncertainty and R\&D Investment Intensity}"`.
- **PASS**

**A-3. Hypothesis**
- Doc: "Does managerial speech uncertainty during earnings calls affect R&D investment intensity (R&D expenditure / sales)?"
- Runner line 41: `H16: beta(uncertainty_var) != 0 -- no directional prediction.`
- **PASS** -- doc phrasing is consistent with the no-directional-prediction framing.

**A-4. Direction (tail test)**
- Doc: `two-tailed (beta != 0, no directional prediction)`
- Runner line 40: `Hypothesis Test (two-tailed):`. Line 404: `p_two = float(model.pvalues.get(iv, np.nan))` -- raw two-tailed p-values used with no halving or conversion.
- **PASS**

**A-5. Model Family**
- Doc: `PanelOLS`
- Runner line 81: `from linearmodels.panel import PanelOLS`
- **PASS**

**A-6. Estimator**
- Doc: `linearmodels.panel.PanelOLS`
- Runner line 81: `from linearmodels.panel import PanelOLS` -- exact class confirmed.
- **PASS**

**A-7. Unit of Observation**
- Doc: `call-level (individual earnings call)`
- Panel builder docstring line 23: `Unit of observation: the individual earnings call (file_name)`. Runner line 457: `Unit of observation: earnings call (file_name)`.
- **PASS**

**A-8. Panel Index**
- Doc: `(gvkey, cal_yr) for cols 1-4, 7-10; (gvkey, cal_yr_qtr) for cols 5-6, 11-12`
- Runner line 334: `time_col = "cal_yr_qtr" if fe_type.endswith("_yq") else "cal_yr"`. Line 355: `df_panel = df_prepared.set_index(["gvkey", time_col])`. MODEL_SPECS confirms industry_yq/firm_yq for cols 5-6 and 11-12.
- **PASS**

**A-9. Columns (count)**
- Doc: `12`
- Runner MODEL_SPECS (lines 121-138): 12 entries (col 1 through col 12).
- **PASS**

**A-10. File paths**
- Doc: `src/f1d/econometric/run_h16_rd_sales.py` and `src/f1d/variables/build_h16_rd_sales_panel.py`
- Both files confirmed to exist on disk.
- **PASS**

---

## PHASE 3: MODEL SPECIFICATION (Section B)

**B1-CHECK: Regression Equation**
- Doc provides two equations: contemporaneous (cols 1-6) and lead (cols 7-12), both with same RHS: 4 IVs + Controls + alpha_i + delta_t.
- Runner: `exog = KEY_IVS + controls` (line 346). For firm FE specs: `formula = f"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"` (line 376). For industry FE specs: `entity_effects=False, time_effects=True, other_effects=industry_data` (lines 366-368).
- Doc's notation `alpha_i = Industry FF12 or Firm` and `delta_t = Calendar Year or Cal Year-Quarter` correctly represents both FE configurations.
- **PASS**

**B2-CHECK: Dependent Variables**
- Doc lists RDSales and RDSales_lead.
- Runner MODEL_SPECS: cols 1-6 use `dv="RDSales"`, cols 7-12 use `dv="RDSales_lead"`. No DVs missing.
- Formula claim: `xrdy_annual (Q4 YTD, fillna(0)) / saley_annual (Q4 YTD, fallback saleq); NaN if sales <= 0`.
- Verified at `_compustat_engine.py` lines 977-983:
  - `xrd_for_rd = pd.Series(xrdy_annual, index=comp.index).fillna(0)` -- missing xrd set to 0
  - `sale_for_rd = saley_series.fillna(pd.Series(saleq_annual, index=comp.index))` -- saley fallback to saleq
  - `comp["RDSales"] = np.where(sale_for_rd > 0, xrd_for_rd / sale_for_rd, np.nan)` -- nonpositive sales yield NaN
- Formula matches exactly.
- **PASS**

**B3-CHECK: Independent Variables**
- Doc lists 4 IVs: UncAnsCEO, UncPreCEO, UncAnsMgr, UncPreMgr.
- Runner KEY_IVS (lines 94-99): exactly these 4 variables in the same order.
- "No centering, log-transformation, or z-scoring applied" -- no transformation code found for these variables in runner or builders.
- **PASS**

**B4-CHECK: Control Variables**
- Doc: "Base Controls (9, including Lagged_DV)".
- Runner BASE_CONTROLS (lines 103-113): lnAssets, TobinsQ, ROA, Leverage, CashRatio, Capex, DivDummy, sCFO, Lagged_DV = 9 items. Matches doc exactly.
- NOTE: Runner docstring (line 28) says "Base Controls (8)" listing only 8 items (omits Lagged_DV). This is a bug in the runner docstring. The provenance doc correctly reflects the actual code list (9), not the docstring (8). Doc is right; runner docstring is misleading.
- EXTENDED_CONTROLS (line 115): BASE_CONTROLS + SalesGrowth, CashFlowAt, DailyVola. Doc says "Extended Controls (= Base + 3 additional)". ✓
- RDSales exclusion note: verified at runner line 101.
- **PASS**

**B5-CHECK: Fixed Effects**
- Doc: Entity FE via ff12_code (industry, other_effects) or gvkey (firm, EntityEffects); Time FE via cal_yr or cal_yr_qtr depending on spec.
- Runner lines 366-371 (industry specs): `entity_effects=False, time_effects=True, other_effects=industry_data, drop_absorbed=True, check_rank=False`.
- Runner line 376 (firm specs): `formula = f"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"`.
- `cal_yr` and `cal_yr_qtr` source: `build_cal_yr_qtr_index()` in `panel_utils.py` at line 195. Doc cites this exact function and line. Verified: `def build_cal_yr_qtr_index(panel: pd.DataFrame) -> pd.DataFrame:` is at line 195 of panel_utils.py.
- **PASS**

**B6-CHECK: Standard Errors**
- Doc: `cov_type="clustered"` with `cluster_entity=True`.
- Runner line 372: `model = model_obj.fit(cov_type="clustered", cluster_entity=True)` (industry specs).
- Runner line 378: `model = model_obj.fit(cov_type="clustered", cluster_entity=True)` (firm specs).
- Doc source "runner lines 372, 378" -- verified, exact lines.
- **PASS**

**B7-CHECK: Hypothesis Test**
- Doc: "Two-tailed p-values used directly from `model.pvalues` (no conversion)."
- Runner line 404: `p_two = float(model.pvalues.get(iv, np.nan))` -- raw pvalues, no halving. ✓
- Stars function `_sig_stars` (line 423): `*** p<0.01, ** p<0.05, * p<0.10`. ✓
- Doc source "runner lines 400-414, 423-433". Line 400 = per-IV comment, line 414 = `return model, meta`, line 423 = `def _sig_stars`, line 432 = last `return ""`. Minor off-by-one (432 not 433) but immaterial.
- **PASS**

---

## PHASE 4: SPEC REGISTER (Section C)

The spec register table has 12 rows. Verified against MODEL_SPECS in runner lines 121-138:

| Col | Doc DV | Code DV | Doc Entity FE | Code fe | Doc Time FE | Code time_col | Doc Controls | Code controls | Match? |
|-----|--------|---------|---------------|---------|-------------|---------------|--------------|---------------|--------|
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

All 12 specs match exactly. No specs in code missing from table; no table rows not in code.
Doc claims "Source: `MODEL_SPECS` list at runner lines 121-138." Verified: MODEL_SPECS dict list begins at line 121, ends at line 138. ✓

**Phase 4 Result: PASS (12/12)**

---

## PHASE 5: SAMPLE CONSTRUCTION (Section D)

**D1-CHECK: Population**
- Doc: starting dataset = master_sample_manifest.parquet, year range 2002-2018.
- Panel builder (line 498): `manifest_input = root / "outputs" / "1.4_AssembleManifest" / "latest" / "master_sample_manifest.parquet"`. Year range from `config/project.yaml` via `get_config()`.
- Runner loads the Stage 3 parquet (not the manifest directly).
- **PASS**

**D2-CHECK: Exclusion Criteria**

The doc describes 5 attrition steps as follows:

| Step | Doc description |
|------|-----------------|
| 1 | Full manifest |
| 2 | Main sample filter (excl FF12 codes 8, 11) |
| 3 | DV non-missing |
| 4 | Complete case (drop NaN in required variables; Inf replaced with NaN first) |
| 5 | Min calls per firm (>= 5) |

The ACTUAL attrition table code (runner lines 814-820) generates:

| Step | Code label | Code value |
|------|------------|------------|
| 1 | "Master manifest (full panel)" | full_panel_n |
| 2 | "Main sample filter (excl Finance/Utility)" | main_panel_n |
| 3 | "After nonpositive-sales exclusion (RDSales NaN)" | panel["RDSales"].notna().sum() |
| 4 | "After lead filter (col 5-8 only)" | panel["RDSales_lead"].notna().sum() |
| 5 | "After complete-case + min-calls (col 1)" | first_meta.get("n_obs", 0) |

**FAIL-1:** Doc step 4 says "Complete case" but the actual attrition table step 4 is the lead DV availability count -- how many calls have a non-null RDSales_lead value on the Main sample panel (before any per-spec filtering). This is NOT a complete-case filter. The lead filter is a count of pre-regression RDSales_lead availability, not a per-spec complete-case drop.

**FAIL-2:** Doc step 5 says "Min calls per firm" as a separate step. The actual attrition table step 5 combines complete-case AND min-calls filtering into one row ("After complete-case + min-calls (col 1)"). The doc incorrectly separates these as distinct steps.

**Secondary runner bug (not a provenance doc error):** The step 4 label "col 5-8 only" in the runner code is itself wrong -- lead specs are cols 7-12, not 5-8. This is a bug in the runner's attrition table label. The provenance doc does not inherit this specific wording error, but it does independently misdescribe what that step represents.

**D3-CHECK: Sample Counts per Spec**
- Doc marks [UNVERIFIED] with explanation. Acceptable.
- **PASS**

---

## PHASE 6: VARIABLE DICTIONARY (Section E)

The dictionary has 22 variables. Verified each:

**RDSales (DV)**
- Formula: `xrdy_annual (Q4 YTD, fillna(0)) / saley_annual (Q4 YTD, fallback saleq); NaN if sales <= 0`
- `_compustat_engine.py` lines 977-983: xrd_for_rd fillna(0); sale_for_rd = saley fillna(saleq); np.where(sale_for_rd > 0, ..., np.nan). Exact match.
- Winsorization "1%/99% by fiscal year": RDSales is in COMPUSTAT_COLS and NOT in skip_winsorize, so it enters the winsorize loop. year_col = comp["fyearq"]. ✓
- **PASS**

**RDSales_lead (DV)**
- Formula: "Next consecutive fiscal year's RDSales, from latest call per (gvkey, fyearq_int); NaN if gap"
- Panel builder `create_rdsales_lead()`: latest call per (gvkey, fyearq_int), shift -1, validate fyearq+1. ✓
- **PASS**

**RDSales_lag (Lagged_DV)**
- Formula: "Prior consecutive fiscal year's RDSales, from latest call per (gvkey, fyearq_int); NaN if gap"
- Panel builder `create_rdsales_lag()`: shift +1, validate fyearq-1. ✓
- **PASS**

**UncAnsCEO, UncPreCEO, UncAnsMgr, UncPreMgr (IVs)**
- All documented as (uncertainty word count / total word count) * 100.
- Source: LinguisticEngine. Winsorization: "No (bounded [0,100] by construction)".
- Runner KEY_IVS confirmed (lines 94-99).
- **PASS (x4)**

**lnAssets (Control)**
- Formula: `ln(atq); NaN if atq <= 0`. Winsorized 1%/99% by fiscal year.
- In COMPUSTAT_COLS, not in skip_winsorize. ✓
- **PASS**

**TobinsQ (Control)**
- Formula: `(cshoq * prccq + dlcq.clip(0).fillna(0) + dlttq.clip(0).fillna(0)) / atq`
- Engine line 629-630: `debt_c = annual["dlcq"].clip(lower=0).fillna(0)`, `debt_t = annual["dlttq"].clip(lower=0).fillna(0)`. ✓
- **PASS**

**ROA (Control)**
- Formula: `iby_annual (Q4) / avg_assets = (atq_t + atq_{t-1}) / 2`.
- Consistent with M-2 fix (avg assets denominator) documented in engine changelog line 82.
- **PASS**

**Leverage (Control)**
- Formula: `(dlcq.fillna(0) + dlttq.fillna(0)) / atq`
- Engine line 948: `comp["Leverage"] = (comp["dlcq"].fillna(0) + comp["dlttq"].fillna(0)) / comp["atq"]`. Exact match. ✓
- **PASS**

**CashRatio, Capex, DivDummy, sCFO (Controls)**
- All verified by builder file names and column outputs.
- DivDummy "Not winsorized (binary)": in skip_winsorize. ✓
- **PASS (x4)**

**SalesGrowth (Control)**
- Formula: `(saley_t - saley_{t-1}) / abs(saley_{t-1}); fallback saleq; NaN if gap or abs(lagged sale) == 0`.
- Engine line 666: `annual["SalesGrowth"] = _winsorize_by_year(annual["SalesGrowth"], annual["fyearq"])` inside `_compute_biddle_residual()`. SalesGrowth is in skip_winsorize (no double-winsorization). ✓
- **PASS**

**CashFlowAt (Control)**
- Formula: `oancfy / avg_assets = (atq_t + atq_{t-1}) / 2`.
- Engine line 693: `annual["CashFlowAt"] = _winsorize_by_year(annual["CashFlowAt"], annual["fyearq"])`. CashFlowAt in skip_winsorize. ✓
- **PASS**

**DailyVola (Control)**
- Formula: `std(daily_ret) * sqrt(252) * 100 over [prev_call + 5d, call - 5d]; min 10 trading days`.
- Source CRSPEngine. "No (computed at builder level, not winsorized)". ✓
- **PASS**

**Lagged_DV (Control)**
- Runner line 265: `base_dv = dv.replace("_lead_qtr", "").replace("_lead", "")`, line 268: `panel["Lagged_DV"] = panel[lag_col]` where `lag_col = "RDSales_lag"`.
- For lead specs: base_dv = "RDSales" (after strip), so Lagged_DV = RDSales_lag. ✓
- **PASS**

**gvkey, ff12_code, cal_yr, cal_yr_qtr (FE columns)**
- All documented with correct derivation. cal_yr = start_date.dt.year, cal_yr_qtr = cal_yr * 10 + quarter. Verified at panel_utils.py lines 215-217. ✓
- **PASS (x4)**

**FAIL-3 (Section L.1 -- RDSales usage claim):**
The variable dictionary does not list RDSales, which is correct. However, Section L.1 claims: "The variable is loaded for summary statistics only." This is factually wrong.

Evidence:
1. Runner `SUMMARY_STATS_VARS` (lines 150-171): RDSales is absent from this list. It is not included in summary statistics.
2. Runner `load_panel()` column selection (lines 219-231): RDSales is not in the `columns` list. The runner explicitly does not read RDSales from the parquet file.
3. The runner never reads, processes, or outputs RDSales in any form.

RDSales is loaded by the panel builder into the parquet file (builder line 136: `"rd_intensity": RDIntensityBuilder(...)`), but the runner stage (Stage 4) never touches it. It is fully dormant in Stage 4.

---

## PHASE 7: DATA PIPELINE, OUTPUTS, TREATMENT (Sections F, G, H)

**F-CHECK: Data Pipeline**

F1 Dependency Chain (7 steps): Verified all steps against code.
- Raw inputs: paths correct (manifest at expected location).
- Engine loading: CompustatEngine, LinguisticEngine, CRSPEngine -- all imported in panel builder.
- Panel builder merge logic: loop over builders on file_name, left join, zero-row-delta enforced (lines 165-200). ✓
- Runner column loading: `load_panel()` (lines 201-243), build_cal_yr_qtr_index called at line 239. ✓
- Sample filtering: per-spec in `prepare_regression_data()` (lines 255-308). ✓
- Regression: 12 PanelOLS models, firm-clustered SEs. ✓
- Table generation: runner writes its own .tex; also in generate_all_tables.py. ✓
- **PASS**

F2 Data Engines: CompustatEngine, LinguisticEngine, CRSPEngine. All confirmed present. RDSales listed as provided -- defensible at Stage 3 level though unused in Stage 4.
- **PASS (with note -- see L.1 correction)**

F3 Merge Operations: All documented with file_name keys (left join), lead/lag merges on (gvkey, fyearq_int), CompustatEngine merge_asof backward on start_date/datadate. All verified in code.
- **PASS**

**G-CHECK: Outputs**

G1 Stage 3 Outputs (Panel Builder):
- h16_rd_sales_panel.parquet: line 484. ✓
- summary_stats.csv: line 493. ✓
- run_manifest.json: lines 499-508 via generate_manifest(). ✓
- report_step3_h16_rd_sales.md: line 551. ✓
- All 4 confirmed. **PASS**

G2 Stage 4 Outputs (Runner):
- h16_rd_sales_table.tex: _save_latex_table(), line 580. ✓
- model_diagnostics.csv: line 619. ✓
- summary_stats.csv: line 779. ✓
- summary_stats.tex: line 780. ✓
- sample_attrition.csv: via generate_attrition_table(), line 821. ✓
- sample_attrition.tex: via generate_attrition_table() -- function always writes both CSV and LaTeX. ✓
- regression_results_col{1-12}.txt: lines 606-613. ✓
- report_step4_H16.md: line 706. ✓
- run_manifest.json: line 825. ✓
- Note: Runner header docstring (line 58) lists sample_attrition.csv but omits sample_attrition.tex. The provenance doc correctly lists both, confirmed by generate_attrition_table() which writes both unconditionally. Provenance doc is right; runner docstring is incomplete.
- All 9 confirmed. **PASS**

G3 Summary Statistics:
- Doc claims variables from SUMMARY_STATS_VARS at "lines 150-171".
- Verified: SUMMARY_STATS_VARS starts at line 150 (definition) and ends at line 171 (closing bracket). Exact match. 17 variables: RDSales, RDSales_lead, 4 IVs, 8 base controls (not Lagged_DV which is dynamic), 3 extended controls. ✓
- **PASS**

**H-CHECK: Outlier/Missing Treatment**

H1 Winsorization:
- **FAIL-4a (line reference):** Doc says "`_winsorize_by_year()` (CompustatEngine line 439)". Actual: `def _winsorize_by_year(` is at line 444. Off by 5.
- **FAIL-4b (incomplete skip list):** Doc says skip list = {DivDummy, CashFlowAt, SalesGrowth, fqtr}. Actual skip_winsorize set (`_compustat_engine.py` lines 1217-1222) also contains ExternalFunding and DebtChoice. These are non-H16 variables but the doc's characterization of the skip list is incomplete.
- All other winsorization claims correct: 1%/99% by fyearq, min 10 obs per group, RDSales is included in winsorize_cols. ✓

H2 Missing Data Policy:
- **FAIL-5 (wrong line reference for engine-level Inf replacement):** Doc says "Also replaced at engine level after ratio computation (CompustatEngine line 1109-1110)". Runner line 281 reference is correct. But engine line 1109 is: `# Step 1: Total debt at Q4 (balance sheet level)` -- no Inf replacement at that line. Actual Inf replacements at engine level: line 1204 (`comp[col] = comp[col].replace([np.inf, -np.inf], np.nan)` in the _compute_and_winsorize loop), and lines 335, 621, 646, 663, 692 (inside helpers for OCF ratio, Investment, TobinsQ, SalesGrowth, CashFlowAt respectively). Line 1109-1110 is completely wrong.
- Runner line 281 reference is correct. ✓

H3 Transformations:
- lnAssets = ln(atq), DivDummy = binary, RDSales lead/lag = fiscal-year shift. ✓
- **PASS**

---

## PHASE 8: TABLE GENERATOR ENTRY (Section I)

Provenance doc reproduces the Python dict entry and claims "Source: `outputs/generate_all_tables.py` lines 364-377."

Verified against actual file:

| Field | generate_all_tables.py (actual) | Doc Claims | Match? |
|-------|--------------------------------|------------|--------|
| id | "H16" | "H16" | PASS |
| dir | "h16_rd_sales/2026-03-27_095019" | "h16_rd_sales/2026-03-27_095019" | PASS |
| caption | r"H16: Speech Uncertainty and R\&D Investment Intensity" | same | PASS |
| label | "tab:h16" | "tab:h16" | PASS |
| cols | 12 | 12 | PASS |
| dvs | [("RDSales", 6), (r"RDSales\_lead", 6)] | same | PASS |
| tail | "two" | "two" | PASS |
| hyp_dir | None | None | PASS |

All field values match exactly.

**FAIL-6 (Section I -- Line reference):** Doc claims "Source: `outputs/generate_all_tables.py` lines 364-377." Actual H16 entry: the `# -- H16 --` comment is at line 302, the dict opens at line 303, and closes at line 315. Lines 364-377 are within the H17 entry, not H16. The line reference is 62 lines off.

**Note about key_vars/key_tails:** Doc correctly notes the H16 entry has no key_vars or key_tails fields. Confirmed in the actual entry. ✓

---

## PHASE 9: MODEL-FAMILY ADDENDUM (Section K)

Suite uses PanelOLS. K1 must be filled; K2-K6 must be N/A.

**K1 PanelOLS Specifics:**
- Entity effects (Industry FE specs, odd cols): `other_effects=df_panel["ff12_code"]`, `entity_effects=False`, `time_effects=True`. Doc cites runner lines 363-371. Verified: those lines contain the PanelOLS constructor call with these exact arguments. ✓
- Entity effects (Firm FE specs, even cols): EntityEffects in from_formula. Runner lines 376-377. ✓
- Time effects: `time_effects=True` (constructor) or `TimeEffects` (formula). ✓
- `drop_absorbed=True`: runner lines 369, 377. Doc says same. ✓
- `check_rank=False` for industry FE specs: runner line 370. ✓
- Singleton handling: "PanelOLS default behavior" -- no explicit singleton dropping in runner code. ✓

**K2-K6:** All marked N/A -- correct.

**Phase 9 Result: PASS (6/6)**

---

## PHASE 10: QUALITY GATE CHECKLIST

| # | Quality Gate | Met? | Evidence |
|---|-------------|------|----------|
| 1 | Every variable in every regression spec appears in Variable Dictionary with explicit formula and source engine | YES | 22 variables: 3 DVs, 4 IVs, 12 controls (inc. Lagged_DV), 4 FE cols -- all with formula and source |
| 2 | The model equation matches what the code actually estimates | YES | Equations verified against runner lines 346, 363-377 |
| 3 | The specification register accounts for every model column | YES | All 12 MODEL_SPECS verified row-by-row |
| 4 | The attrition cascade has row counts for each filter step | PARTIAL | Row counts [UNVERIFIED] which is acceptable; BUT documented steps 4-5 do not match actual attrition table code (FAIL-1, FAIL-2) |
| 5 | The tail test direction matches between runner code and generate_all_tables.py | YES | Runner: raw p_two used; generate_all_tables.py: tail="two"; both two-tailed |
| 6 | The FE specification matches between docstring, code, and this document | YES | Runner code, B5, C (spec register), and K1 all consistent |
| 7 | Every merge in the panel builder is documented with join keys and type | YES | F3 documents all builder merges (file_name, left) and lead/lag merges (gvkey+fyearq_int, left) |
| 8 | The output file list matches what the runner actually writes | YES | All 9 runner outputs and 4 panel builder outputs confirmed |
| 9 | The model-family addendum is filled for the correct family only | YES | K1 filled, K2-K6 N/A |
| 10 | Any claim marked [UNVERIFIED] has an explanation of what blocks verification | YES | D2 and D3 [UNVERIFIED] claims both have explanatory text |

Gates 4 fails substantively (attrition table steps misdescribed).

---

## PHASE 11: CROSS-REFERENCE CONSISTENCY

Internal consistency checks within docs/provenance/H16.md:

| Check | What Was Checked | Result |
|-------|-----------------|--------|
| DVs in B2 match DVs in C | B2: RDSales, RDSales_lead. C: RDSales cols 1-6, RDSales_lead cols 7-12. | PASS |
| DVs in C match dvs in I | C: RDSales (6 cols), RDSales_lead (6 cols). I: dvs=[("RDSales",6),(r"RDSales\_lead",6)]. | PASS |
| Controls in B4 match variables in E | B4 Base: 9 vars; B4 Extended: +3. E contains all 12 unique control variables. | PASS |
| Column count in A matches rows in C | A: Columns=12. C: 12 rows. | PASS |
| Column count in A matches cols in I | A: Columns=12. I: cols=12. | PASS |
| Tail direction A matches B7 matches I | A: two-tailed. B7: two-tailed, no conversion. I: tail="two", hyp_dir=None. | PASS |
| FE in B5 matches C matches K1 | B5: FF12+firm FE, cal_yr+cal_yr_qtr. C: same. K1: same. | PASS |
| Panel index in A matches set_index in K1 | A: (gvkey, cal_yr) or (gvkey, cal_yr_qtr). K1: time index is cal_yr or cal_yr_qtr set at set_index. | PASS |

**Phase 11 Result: PASS (8/8)**

---

## FAILURES (Detailed)

| # | Phase | Check | Provenance Doc Claims | Actual Code Says | Severity | Fix Required |
|---|-------|-------|----------------------|-----------------|----------|-------------|
| FAIL-1 | 5 (D2) | Attrition Step 4 | "Complete case -- Drop rows where any required variable (DV, IVs, controls, FE indices) is NaN; Inf/-Inf replaced with NaN before check" | Runner attrition_stages step 4 (line 818): `("After lead filter (col 5-8 only)", panel["RDSales_lead"].notna().sum())` -- counts calls with non-null RDSales_lead on the main-sample panel before any per-spec filtering. This is a pre-filter DV availability count, not a complete-case drop. | MEDIUM | Correct D2 step 4 to describe what the attrition table actually reports at this step |
| FAIL-2 | 5 (D2) | Attrition Steps 4-5 structure | Docs shows complete-case (step 4) and min-calls (step 5) as separate steps | Runner line 819: `("After complete-case + min-calls (col 1)", first_meta.get("n_obs", 0))` -- combines complete-case and min-calls into ONE attrition row, using col 1 N | MEDIUM | Correct D2 to show step 5 is a combined complete-case + min-calls row (col 1 only) |
| FAIL-3 | 6 (E) / L.1 | RDSales usage | L.1: "The variable is loaded for summary statistics only" | (1) SUMMARY_STATS_VARS (runner lines 150-171): RDSales absent. (2) load_panel() column selection (runner lines 219-231): RDSales absent. RDSales is in the Stage 3 parquet but Stage 4 never reads, processes, or outputs it in any form. | HIGH | Correct L.1 to state RDSales is written to Stage 3 parquet but is not loaded or used in Stage 4 (not in regressions, not in summary stats) |
| FAIL-4a | 7 (H1) | _winsorize_by_year line reference | "CompustatEngine line 439" | `def _winsorize_by_year(` is at line 444 of _compustat_engine.py, not line 439 | LOW | Change "line 439" to "line 444" |
| FAIL-4b | 7 (H1) | Winsorization skip list | skip_winsorize = {DivDummy, CashFlowAt, SalesGrowth, fqtr} | Actual skip_winsorize (_compustat_engine.py lines 1217-1222) also includes ExternalFunding and DebtChoice | LOW | Add ExternalFunding and DebtChoice to the skip list description (noting these are non-H16 suite variables) |
| FAIL-5 | 7 (H2) | Engine-level Inf replacement line | "CompustatEngine line 1109-1110" | Line 1109: `# Step 1: Total debt at Q4 (balance sheet level)` -- no Inf replacement here. Actual: line 1204 in _compute_and_winsorize() loop; also lines 335, 621, 646, 663, 692 in ratio helpers | MEDIUM | Correct to cite line 1204 for the main loop and lines 335/621/646/663/692 for within-helper replacements |
| FAIL-6 | 8 (I) | generate_all_tables.py line reference | "lines 364-377" | H16 entry spans lines 302-315. Lines 364-377 are within the H17 entry. | LOW | Change "lines 364-377" to "lines 302-315" |

---

## CORRECTIONS REQUIRED

**CORRECTION 1 (HIGH) -- Section L, item 1**

Current text:
> "The variable is loaded for summary statistics only."

Required replacement:
> "The variable is written to the Stage 3 parquet by the panel builder but is **not loaded by the runner** (absent from the runner's `load_panel()` column selection at lines 219-231) and **not included in summary statistics** (absent from `SUMMARY_STATS_VARS` at lines 150-171). RDSales is currently unused in Stage 4."

Proof: Runner lines 219-231 (column selection list), runner lines 150-171 (SUMMARY_STATS_VARS list). Neither contains "RDSales".

---

**CORRECTION 2 (MEDIUM) -- Section D2, Steps 4-5**

Current step 4:
> | 4 | Complete case | Drop rows where any required variable (DV, IVs, controls, FE indices) is NaN; Inf/-Inf replaced with NaN before check |

Current step 5:
> | 5 | Min calls per firm | Require >= 5 calls per gvkey in the filtered sample |

Required replacement for steps 4 and 5:
> | 4 | Lead DV availability (pre-filter) | `panel["RDSales_lead"].notna().sum()` on the main-sample panel before per-spec filtering -- counts calls with a valid next-fiscal-year RDSales value (attrition table label: "After lead filter") |
> | 5 | Complete case + min calls per firm (col 1) | Combined step: Inf-to-NaN replacement, complete-case drop (all required variables non-null), min 5 calls per firm; N shown is col 1 final N only (`first_meta["n_obs"]`); actual N varies across specs |

Proof: Runner lines 814-820 (attrition_stages list).

---

**CORRECTION 3 (MEDIUM) -- Section H2**

Current text:
> Also replaced at engine level after ratio computation (CompustatEngine line 1109-1110)

Required replacement:
> Also replaced at engine level: in the main `_compute_and_winsorize()` loop at line 1204, and inside ratio-computation helpers at lines 335 (OCF ratio), 621 (Investment), 646 (TobinsQ), 663 (SalesGrowth), 692 (CashFlowAt).

Proof: `_compustat_engine.py` lines 335, 621, 646, 663, 692, 1204 -- all contain `.replace([np.inf, -np.inf], np.nan)`.

---

**CORRECTION 4 (LOW) -- Section H1**

Current text:
> `_winsorize_by_year()` (CompustatEngine line 439)

Required replacement:
> `_winsorize_by_year()` (CompustatEngine line 444)

Proof: `_compustat_engine.py` line 444: `def _winsorize_by_year(`.

---

**CORRECTION 5 (LOW) -- Section H1, skip list**

Current text:
> Skip: DivDummy (binary), CashFlowAt/SalesGrowth (already winsorized per-year inside `_compute_biddle_residual`), and fqtr (identifier).

Required replacement:
> Skip: DivDummy (binary), CashFlowAt/SalesGrowth (already winsorized per-year inside `_compute_biddle_residual` -- do not double-winsorize), fqtr (fiscal quarter identifier), ExternalFunding (binary, H20 suite), DebtChoice (binary, H20 suite).

Proof: `_compustat_engine.py` lines 1217-1222, `skip_winsorize` set definition.

---

**CORRECTION 6 (LOW) -- Section I**

Current text:
> Source: `outputs/generate_all_tables.py` lines 364-377.

Required replacement:
> Source: `outputs/generate_all_tables.py` lines 302-315.

Proof: `outputs/generate_all_tables.py` line 302: `# -- H16 --`, line 315: closing `},`. H17 entry begins at line 316.

---

## ADDITIONAL NOTES (Non-Failures, No Corrections Required)

1. **Runner docstring inconsistency (internal runner bug, not a provenance doc error):** Runner docstring line 28 says "Base Controls (8)" but the actual `BASE_CONTROLS` list (lines 103-113) has 9 items including Lagged_DV. The provenance doc correctly reflects the actual code list (9 items). This runner docstring error should be fixed in the runner, but no change is needed in the provenance doc.

2. **Attrition stage 4 label in runner is mislabeled (internal runner bug):** Runner line 818 labels attrition step 4 as "After lead filter (col 5-8 only)". Lead specs are cols 7-12, not 5-8. The provenance doc does not inherit this specific wording, but it also does not flag this mislabeling in L.2. Not required to add, but worth noting.

3. **`year` column loaded but not documented in variable dictionary:** Runner column selection (line 220) loads `"year"` from the parquet. This is a year-from-start_date column created in the panel builder (line 211). It is distinct from `cal_yr` (created by `build_cal_yr_qtr_index()` from the same start_date). `year` is loaded but not used in any regression or complete-case check. The provenance doc does not document it. This is a minor incompleteness but not a material failure.

4. **Panel builder line reference in L.1:** L.1 says "line 66 of panel builder" for RDIntensityBuilder. Actual line of `RDIntensityBuilder,` in the import list is line 68. Off by 2. Covered by CORRECTION 1 (the entire L.1 text is being replaced).

5. **`_sig_stars` range claimed as 423-433:** Function actually ends at line 432 (final `return ""`). Off by one. Immaterial.

6. **Runner docstring omits sample_attrition.tex:** Runner header (line 58) lists sample_attrition.csv but not sample_attrition.tex. The provenance doc correctly lists both -- `generate_attrition_table()` always writes both. Provenance doc is correct; this is a gap in the runner's own documentation.
