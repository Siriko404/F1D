# Adversarial Audit Report: Suite H17
**Auditor**: Claude Sonnet 4.6 (hostile adversarial mode)
**Date**: 2026-04-01
**Suite**: H17 — Speech Uncertainty and Repurchase Intensity
**Provenance Doc**: docs/provenance/H17.md
**Runner**: src/f1d/econometric/run_h17_repurchase_intensity.py
**Panel Builder**: src/f1d/variables/build_h17_repurchase_intensity_panel.py
**Table Generator**: outputs/generate_all_tables.py

---

## AUDIT SUMMARY

| Category | Total Checks | Passed | Failed | Score |
|----------|-------------|--------|--------|-------|
| Structural Completeness (Phase 1) | 26 | 26 | 0 | 100% |
| Suite Identity (Phase 2) | 10 | 10 | 0 | 100% |
| Model Specification (Phase 3) | 7 | 7 | 0 | 100% |
| Spec Register (Phase 4) | 14 | 14 | 0 | 100% |
| Sample Construction (Phase 5) | 5 | 5 | 0 | 100% |
| Variable Dictionary (Phase 6) | 26 | 24 | 2 | 92% |
| Pipeline/Outputs/Treatment (Phase 7) | 12 | 11 | 1 | 92% |
| Table Generator Entry (Phase 8) | 8 | 8 | 0 | 100% |
| Model-Family Addendum (Phase 9) | 7 | 7 | 0 | 100% |
| Quality Gates (Phase 10) | 10 | 8 | 2 | 80% |
| Cross-Reference Consistency (Phase 11) | 8 | 8 | 0 | 100% |
| **TOTAL** | **133** | **128** | **5** | **96%** |

---

## VERDICT

**PASS WITH NOTES**: The document is structurally complete and largely accurate. Five minor issues were found: two factual line-number errors in section L (Known Issues), one variable dictionary gap (fyearq_int not documented as required column), one pipeline note gap (cal_yearqtr orphan column in panel builder not mentioned), and one attrition table stage-count discrepancy (D2 table shows 5 conceptual steps while generated CSV has 4 stages). None of these affect the correctness of the regression specification, variable formulas, or any substantive claim. All five require corrections enumerated below.

---

## PHASE 1: STRUCTURAL COMPLETENESS

Read: docs/Prompts/Suite Provenance Doc.txt (required sections A-L).
Read: docs/provenance/H17.md end to end.

| Section | Required by Prompt | Present in Doc | Complete | Notes |
|---------|-------------------|----------------|----------|-------|
| A. Suite Identity | Yes | Yes | Yes | YAML block present, all fields filled |
| B. Model Specification | Yes | Yes | Yes | |
| B1. Regression Equation | Yes | Yes | Yes | Contemp and lead equations both shown in LaTeX |
| B2. Dependent Variable(s) | Yes | Yes | Yes | RepurchaseIntensity + lead, full de-cumulation 7-step logic |
| B3. Independent Variable(s) | Yes | Yes | Yes | All 4 IVs with formulas, no centering noted |
| B4. Control Variables | Yes | Yes | Yes | Base (9) and Extended (+4) tables |
| B5. Fixed Effects | Yes | Yes | Yes | All 4 FE variants with column usage |
| B6. Standard Errors | Yes | Yes | Yes | clustered, cluster_entity=True |
| B7. Hypothesis Test | Yes | Yes | Yes | Two-tailed; legacy _p_one field correctly noted |
| C. Spec Register | Yes | Yes | Yes | 12 rows, one per MODEL_SPECS entry |
| D. Sample Construction | Yes | Yes | Yes | |
| D1. Population | Yes | Yes | Yes | 112,968 calls, year range cited |
| D2. Exclusion Criteria | Yes | Yes | Yes | 5-step cascade; counts UNVERIFIED with explanation |
| D3. Sample Counts per Spec | Yes | Yes | Yes | N varies documented; directed to diagnostics CSV |
| E. Variable Dictionary | Yes | Yes | Yes* | 24 variables tabulated; fyearq_int MISSING — see FAIL-3 |
| F. Data Pipeline | Yes | Yes | Yes | |
| F1. Dependency Chain | Yes | Yes | Yes | 7-step chain from raw data to table |
| F2. Data Engines Used | Yes | Yes | Yes | 3 engines documented |
| F3. Merge Operations | Yes | Yes | Yes | All merges documented with keys and join type |
| G. Outputs | Yes | Yes | Yes | |
| G1. Stage 3 Outputs | Yes | Yes | Yes | 3 files (parquet + stats csv + manifest) |
| G2. Stage 4 Outputs | Yes | Yes | Yes | 8 output types; verified against runner |
| G3. Summary Statistics | Yes | Yes | Yes | 18 variables listed; lines 119-138 cited |
| H. Outlier/Missing Treatment | Yes | Yes | Yes | Winsorization, missing policy, transformations |
| I. generate_all_tables Entry | Yes | Yes | Yes | Full entry reproduced with verification table |
| J. Reproduction Commands | Yes | Yes | Yes | 3-step commands |
| K. Model-Family Addendum | Yes | Yes | Yes | K1 filled; K2-K6 N/A |
| L. Known Issues | Yes | Yes | Yes | 6 issues; 2 contain line number errors (FAIL-1, FAIL-2) |

**Structural result: PASS — 26/26 sections present and substantively populated. No placeholder text found.**

---

## PHASE 2: SUITE IDENTITY (Section A)

### A-1. Suite ID
**Doc claims**: H17
**Evidence**: "Suite ID: H17" in YAML block.
**PASS**

### A-2. Title
**Doc claims**: "H17: Speech Uncertainty and Repurchase Intensity"
**Code**: generate_all_tables.py line 320: `"caption": "H17: Speech Uncertainty and Repurchase Intensity"`. Runner docstring line 5: "Run H17 hypothesis test — quarterly RepurchaseIntensity at call level." Title is consistent with generate_all_tables.py caption.
**PASS**

### A-3. Hypothesis
**Doc claims**: "Does managerial speech uncertainty during earnings calls predict the intensity of share repurchases in the current or next fiscal quarter?"
**Code**: Runner docstring lines 6-22 describe RepurchaseIntensity DV with 4 uncertainty IVs across 12 specs. The one-sentence hypothesis is the provenance doc's own formulation; code does not state a single hypothesis sentence. Content is behaviorally consistent.
**PASS**

### A-4. Direction (tail test)
**Doc claims**: "two-tailed"
**Code**:
- Runner docstring line 30: "Hypothesis: Two-tailed."
- generate_all_tables.py line 327: `"tail": "two"`
- Runner line 479: `r"$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (two-tailed)."`
- `_sig_stars()` (lines 337-346): applies `p < 0.01/0.05/0.10` directly without halving.
**PASS**

### A-5. Model Family
**Doc claims**: "PanelOLS"
**Code**: Runner line 61: `from linearmodels.panel import PanelOLS`. Used at lines 287 and 300.
**PASS**

### A-6. Estimator
**Doc claims**: "linearmodels.panel.PanelOLS"
**Code**: `from linearmodels.panel import PanelOLS` — exact module path matches.
**PASS**

### A-7. Unit of Observation
**Doc claims**: "call-level (individual earnings call)"
**Code**: Panel builder docstring line 9: "Unit of observation: individual earnings call (file_name)." Manifest keyed on file_name; all merges preserve file_name rows 1:1.
**PASS**

### A-8. Panel Index
**Doc claims**: "(gvkey, cal_yr) for cols 1-4, 7-10; (gvkey, cal_yr_qtr) for cols 5-6, 11-12"
**Code**: Runner `run_regression()` lines 263 and 283:
```python
time_col = "cal_yr_qtr" if fe_type.endswith("_yq") else "cal_yr"
df_panel = df_prepared.set_index(["gvkey", time_col])
```
MODEL_SPECS: cols 5,6,11,12 have fe ending in "_yq"; cols 1-4,7-10 do not. Entity index is always gvkey (ff12_code passed as other_effects, not as entity index). Both index components verified.
**PASS**

### A-9. Column Count
**Doc claims**: 12
**Code**: MODEL_SPECS list (lines 93-110) has 12 dict entries, numbered col 1 through col 12.
**PASS**

### A-10. File Paths
**Doc claims**:
- Runner: `src/f1d/econometric/run_h17_repurchase_intensity.py`
- Panel Builder: `src/f1d/variables/build_h17_repurchase_intensity_panel.py`
**Verification**: Both files confirmed to exist on disk via filesystem check.
**PASS**

---

## PHASE 3: MODEL SPECIFICATION (Section B)

### B1-CHECK: Regression Equation

**Doc claims** (Contemporaneous, cols 1-6):
RepurchaseIntensity_{i,t} = beta1*CEO_QA + beta2*CEO_Pres + beta3*Mgr_QA + beta4*Mgr_Pres + gamma*Controls + alpha_i + delta_t + epsilon

**Code**: Runner `run_regression()` line 275: `exog = KEY_IVS + controls`. KEY_IVS = [UncAnsCEO, UncPreCEO, UncAnsMgr, UncPreMgr] (lines 74-79). Industry path (lines 287-296): `PanelOLS(dependent=dv, exog=exog, entity_effects=False, time_effects=True, other_effects=ff12_code)`. Firm path (lines 298-301): formula `= f"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"`.

Equation in doc matches all terms used in code. Lead DV equation has identical structure with RepurchaseIntensity_lead_qtr.
**PASS**

### B2-CHECK: Dependent Variable(s)

**RepurchaseIntensity**:
- Column name in MODEL_SPECS: "RepurchaseIntensity" — PASS
- Formula: `quarterly_prstkcy / atq_{t-1}` — code _compustat_engine.py line 1083: `comp["_quarterly_repurchases"] / comp["_atq_prev_q"]` — PASS
- De-cumulation Q1: `comp["prstkcy"].fillna(0)` (line 1058) — PASS
- De-cumulation Q2-Q4: `comp["prstkcy"] - comp["_prstkcy_prev"]` within same fyearq (line 1061) — PASS
- Negative clamp: `clip(lower=0)` (line 1066) — PASS
- Lagged atq validation: gap > 150 days → NaN (lines 1073-1077) — PASS
- Inf → NaN after ratio (line 1203-1204 for RepurchaseIntensity in ratio_cols list) — PASS

**RepurchaseIntensity_lead_qtr**:
- Panel builder `create_lead_variables()` lines 254-269: fiscal_qtr_id shift(-1) with consecutive check — PASS
- Consecutive check: if fqtr < 4, next = curr+1; if fqtr == 4, next = (fyearq+1)*10+1 — PASS
- Non-consecutive produces NaN — PASS

**PASS**

### B3-CHECK: Independent Variable(s)

**Doc claims**: UncAnsCEO, UncPreCEO, UncAnsMgr, UncPreMgr. No centering, log, or z-score.
**Code**: KEY_IVS list exactly matches (runner lines 74-79). These are passed directly in `exog = KEY_IVS + controls` without any transformation in the runner. Panel builder imports CEOQAUncertaintyBuilder, CEOPresUncertaintyBuilder, ManagerQAUncertaintyBuilder, ManagerPresUncertaintyBuilder — LinguisticEngine-based builders.
**PASS**

### B4-CHECK: Control Variables

**BASE_CONTROLS** doc vs code:
| Variable | In Doc | In Code (BASE_CONTROLS) | Match |
|----------|--------|------------------------|-------|
| lnAssets | Yes | Yes | PASS |
| TobinsQ | Yes | Yes | PASS |
| ROA | Yes | Yes | PASS |
| Leverage | Yes | Yes | PASS |
| Capex | Yes | Yes | PASS |
| CashRatio | Yes | Yes | PASS |
| DivDummy | Yes | Yes | PASS |
| sCFO | Yes | Yes | PASS |
| Lagged_DV | Yes | Yes | PASS |

Runner lines 81-85 list exactly these 9. No extra or missing controls.

**EXTENDED_CONTROLS** = BASE + [SalesGrowth, RDSales, CashFlowAt, DailyVola]:
Runner lines 87-89: identical. **PASS**

**Lagged_DV construction** (runner lines 210-213):
```python
base_dv = dv.replace("_lead_qtr", "").replace("_lead", "")
lag_col = f"{base_dv}_lag"
panel["Lagged_DV"] = panel[lag_col]
```
For lead specs, base_dv = "RepurchaseIntensity", lag_col = "RepurchaseIntensity_lag". PASS.

**PASS**

### B5-CHECK: Fixed Effects

**Doc claims**:
- Cols 1,3,5,7,9,11: Industry FE (ff12_code) via other_effects, entity_effects=False, time_effects=True
- Cols 2,4,6,8,10,12: Firm FE (gvkey) via EntityEffects in formula + TimeEffects
- Cols 1-4,7-10: Time = cal_yr
- Cols 5-6,11-12: Time = cal_yr_qtr

**Code** (runner lines 263-301):
- `time_col = "cal_yr_qtr" if fe_type.endswith("_yq") else "cal_yr"` — verified
- Industry path: `PanelOLS(entity_effects=False, time_effects=True, other_effects=df_panel["ff12_code"])` — verified
- Firm path: formula with `EntityEffects + TimeEffects` — verified
- MODEL_SPECS: cols with fe="industry" or fe="firm" use cal_yr; fe="industry_yq" or fe="firm_yq" use cal_yr_qtr — verified

**PASS**

Doc claim about cal_yr/cal_yr_qtr source (build_cal_yr_qtr_index in panel_utils.py):
- panel_utils.py lines 195-217: `cal_yr = dt.dt.year`, `cal_yr_qtr = cal_yr * 10 + cal_qtr` — PASS
- Runner line 183: `panel = build_cal_yr_qtr_index(panel)` — PASS
- Column is derived from `start_date` (calendar date), not Compustat fiscal date — PASS

### B6-CHECK: Standard Errors

**Doc claims**: cov_type="clustered", cluster_entity=True
**Code** (lines 296 and 301):
```python
model = model_obj.fit(cov_type="clustered", cluster_entity=True)
```
Both industry and firm paths use identical call.
**PASS**

### B7-CHECK: Hypothesis Test

**Doc claims**: Two-tailed. model.pvalues used directly (no halving). `{iv}_p_one` stores two-tailed values (legacy name).
**Code**:
- Line 325: `p_two = float(model.pvalues.get(iv, np.nan))`
- Line 329: `meta[f"{iv}_p_one"] = p_two  # two-tailed`
- Line 331: `stars = _sig_stars(p_two)` using two-tailed thresholds
- `_sig_stars()` (lines 337-346): `< 0.01 → ***`, `< 0.05 → **`, `< 0.10 → *` — no one-tailed conversion
**PASS**

---

## PHASE 4: SPEC REGISTER (Section C)

Counted MODEL_SPECS in runner: 12 entries (cols 1-12).
Counted rows in provenance doc Section C table: 12 rows.
Every row verified:

| Col | Doc DV | Code DV | Doc Entity FE | Code fe | Doc Time FE | Code time_col | Doc Controls | Code controls | Match? |
|-----|--------|---------|--------------|---------|-------------|--------------|-------------|--------------|--------|
| 1 | RepurchaseIntensity | RepurchaseIntensity | Industry (FF12) | industry | Cal Yr | cal_yr | Base | base | PASS |
| 2 | RepurchaseIntensity | RepurchaseIntensity | Firm | firm | Cal Yr | cal_yr | Base | base | PASS |
| 3 | RepurchaseIntensity | RepurchaseIntensity | Industry (FF12) | industry | Cal Yr | cal_yr | Extended | extended | PASS |
| 4 | RepurchaseIntensity | RepurchaseIntensity | Firm | firm | Cal Yr | cal_yr | Extended | extended | PASS |
| 5 | RepurchaseIntensity | RepurchaseIntensity | Industry (FF12) | industry_yq | Cal Yr-Qtr | cal_yr_qtr | Extended | extended | PASS |
| 6 | RepurchaseIntensity | RepurchaseIntensity | Firm | firm_yq | Cal Yr-Qtr | cal_yr_qtr | Extended | extended | PASS |
| 7 | RepurchaseIntensity_lead_qtr | RepurchaseIntensity_lead_qtr | Industry (FF12) | industry | Cal Yr | cal_yr | Base | base | PASS |
| 8 | RepurchaseIntensity_lead_qtr | RepurchaseIntensity_lead_qtr | Firm | firm | Cal Yr | cal_yr | Base | base | PASS |
| 9 | RepurchaseIntensity_lead_qtr | RepurchaseIntensity_lead_qtr | Industry (FF12) | industry | Cal Yr | cal_yr | Extended | extended | PASS |
| 10 | RepurchaseIntensity_lead_qtr | RepurchaseIntensity_lead_qtr | Firm | firm | Cal Yr | cal_yr | Extended | extended | PASS |
| 11 | RepurchaseIntensity_lead_qtr | RepurchaseIntensity_lead_qtr | Industry (FF12) | industry_yq | Cal Yr-Qtr | cal_yr_qtr | Extended | extended | PASS |
| 12 | RepurchaseIntensity_lead_qtr | RepurchaseIntensity_lead_qtr | Firm | firm_yq | Cal Yr-Qtr | cal_yr_qtr | Extended | extended | PASS |

Layout note (doc): "Odd = Industry FE, Even = Firm FE" — verified. PASS.
Layout note (doc): "Cols 1-2, 7-8 = Base; Cols 3-6, 9-12 = Extended" — verified. PASS.

**Phase 4: PASS — 14/14**

---

## PHASE 5: SAMPLE CONSTRUCTION (Section D)

### D1-CHECK: Population
**Doc claims**: ~112,968 calls, year range 2002-2018.
**Verification**: Consistent with project-wide scope (memory/project_thesis_scope.md: 112,968 calls, 2,429 firms, 2002-2018). Runner does not independently print firm count at startup. PASS.

### D2-CHECK: Exclusion Criteria
**Doc claims 5 steps in order**:
1. Full panel (year range)
2. Main sample: `ff12_code not in [8, 11]`
3. DV non-missing
4. Complete case (Inf→NaN, then dropna)
5. Min calls >= 5 per gvkey

**Code verification**:
- Step 2: `filter_main_sample()` line 193: `panel[~panel["ff12_code"].isin([8, 11])]` — PASS
- Step 3: `prepare_regression_data()` lines 227-229: `df[df[dv].notna()]` — PASS
- Step 4: lines 224, 232-233: `df.replace([np.inf, -np.inf], np.nan)` then `df[required].notna().all(axis=1)` — PASS
- Step 5: lines 236-240: `firm_counts[firm_counts >= 5]` — PASS
- Order: Inf→NaN first, then DV filter, then complete case, then min calls — PASS

**All counts marked [UNVERIFIED] with explanation "runtime-dependent"**: Acceptable per audit rules. PASS.

### D3-CHECK: Sample Counts per Spec
Doc says N varies due to DV differences, extended controls, and cal_yr_qtr non-null requirement. Code confirms this: `prepare_regression_data()` runs independently per spec with different required column lists. PASS.

**Phase 5: PASS — 5/5**

---

## PHASE 6: VARIABLE DICTIONARY (Section E)

26 variables in the dictionary. Verified each against code.

### DV Variables (4 entries)

**RepurchaseIntensity** (code name: "RepurchaseIntensity"):
- Formula: quarterly_prstkcy / atq_{t-1}, de-cumulated, negatives clamped
- Code: _compustat_engine.py lines 1056-1085 — PASS
- Winsorized: "1%/99% by fiscal year" — RepurchaseIntensity IS in COMPUSTAT_COLS (line 135), NOT in skip_winsorize (lines 1217-1224), IS winsorized via `_winsorize_by_year` with fyearq as year column — PASS
- Timing: contemporaneous — PASS

**RepurchaseIntensity_lead_qtr** (code name used in MODEL_SPECS):
- Formula: next consecutive fiscal quarter's RepurchaseIntensity
- Code: panel builder lines 254-269: `firm_qtr.groupby("gvkey")["RepurchaseIntensity"].shift(-1)` with consecutive check — PASS
- Winsorized: "Inherited from RepurchaseIntensity" — correct; no additional winsorization applied to the shifted column — PASS

**RepurchaseIntensity_lag** (source for Lagged_DV):
- Code: panel builder lines 285-308: `firm_qtr.groupby("gvkey")["RepurchaseIntensity"].shift(1)` with consecutive prev check — PASS

**Lagged_DV**:
- Code: runner lines 210-213: `panel["Lagged_DV"] = panel["RepurchaseIntensity_lag"]` (for all specs, including lead specs) — PASS

### IV Variables (4 entries)

All four uncertainty IVs (UncAnsCEO, UncPreCEO, UncAnsMgr, UncPreMgr):
- In KEY_IVS list: PASS
- Formula (uncertainty words / total words) * 100 by section: consistent with LinguisticEngine pattern — PASS
- Winsorized: No (bounded [0,100] by construction): PASS — no winsorization applied to linguistic variables
- Timing: Contemporaneous: PASS

### Control Variables — Base (9 variables)

**lnAssets**: ln(atq); NaN when atq <= 0
- Code line 943: `np.where(comp["atq"] > 0, np.log(comp["atq"]), np.nan)` — PASS
- Winsorized: 1%/99% by fyearq — PASS

**TobinsQ**: (cshoq * prccq + dlcq + dlttq) / atq
- Code: uses mktcap = cshoq*prccq, debt = dlcq.fillna(0)+dlttq.fillna(0), TobinsQ = (mktcap+debt)/atq — PASS
- Winsorized: 1%/99% — PASS

**ROA**: iby_annual (Q4) / avg_assets where avg_assets = (atq_annual + atq_annual_lag1) / 2
- Code lines 960-969: _compute_annual_q4_variable for iby; avg_assets from annual atq values — PASS
- Note: Doc says "avg_assets = (atq_t + atq_{t-1}) / 2" without clarifying these are Q4-annual values, not quarterly. This is slightly ambiguous but not factually incorrect given the broader context of "iby_annual (Q4)". Not a failure.
- Winsorized: 1%/99% — PASS

**Leverage**: (dlcq.fillna(0) + dlttq.fillna(0)) / atq — PASS. Winsorized: 1%/99% — PASS.

**Capex**: capxy_annual (Q4) / atq_lag1_annual
- Code lines 999-1005: `capxy_annual / atq_annual_lag1` — PASS
- Winsorized: 1%/99% — PASS

**CashRatio**: cheq / atq — PASS. Winsorized: 1%/99% — PASS.

**DivDummy**: 1 if dvy_annual (Q4) > 0, else 0
- Code: `_compute_annual_q4_variable(comp, "dvy")` then indicator — PASS
- Winsorized: No (binary) — DivDummy in skip_winsorize (line 1218) — PASS

**sCFO**: Rolling 5-yr std (min 3 yrs) of (oancfy / atq_{t-1}) per firm
- Code: `_compute_ocf_volatility()` line 340: rolling("1826D", min_periods=3).std() — PASS
- "1826D" = approximately 5 years in days — PASS
- Winsorized: 1%/99% — PASS

**Lagged_DV**: see DV section above. PASS.

### Control Variables — Extended additional (4 variables)

**SalesGrowth**: (saley_t - saley_{t-1}) / abs(saley_{t-1}); Q4-only; saley with saleq fallback
- Code: _compute_biddle_residual() lines 649-666 — PASS
- Winsorized: "1%/99% by fiscal year (inside Biddle)" — PASS. SalesGrowth in skip_winsorize (line 1220) to prevent double-winsorization.

**RDSales**: xrdq.fillna(0) / atq
- Code line 972: `comp["RDSales"] = comp["xrdq"].fillna(0) / comp["atq"]` — PASS
- Winsorized: 1%/99% — PASS

**CashFlowAt**: oancfy / avg_assets; avg = (atq_t + atq_{t-1})/2, fallback to atq_t
- Code: _compute_biddle_residual() lines 680-693 — PASS
- Winsorized: "1%/99% by fiscal year (inside Biddle)" — PASS. CashFlowAt in skip_winsorize (line 1219).

**DailyVola**: std(daily_ret) * sqrt(252) * 100; window [prev_call+5d, call-5d]; min 10 days
- Source: CRSPEngine: RET — PASS
- Winsorized: No — PASS (CRSPEngine-derived, not in _compute_and_winsorize loop)

### FE Identifier Columns (4 entries)

**ff12_code**: from ManifestFieldsBuilder (from manifest) — PASS
**gvkey**: from ManifestFieldsBuilder — PASS
**cal_yr**: start_date.dt.year from panel_utils.build_cal_yr_qtr_index — PASS
**cal_yr_qtr**: cal_yr * 10 + start_date.dt.quarter from panel_utils — PASS

---

### FAIL-3: MISSING VARIABLE — fyearq_int

**Provenance doc claims**: fyearq_int is not listed in the variable dictionary.
**Code**:
- Panel builder line 186: `panel["fyearq_int"] = pd.to_numeric(panel["fyearq"], errors="coerce")`
- Runner line 215: `required = [dv] + KEY_IVS + controls + ["gvkey", "fyearq_int", "ff12_code"]`
- fyearq_int is a required non-null column that participates in complete-case filtering.
- Rows where fyearq_int is NaN are dropped during complete-case, silently affecting sample size.
**Severity**: Minor. fyearq_int is a derived integer identifier, not a substantive regression variable or FE column. Its effect on sample is small (fyearq is largely complete in Compustat). But it should appear in the dictionary as a required identifier.

---

### FAIL-4: MISSING NOTE — cal_yearqtr orphan column in panel builder

**Provenance doc claims**: No mention anywhere of the `cal_yearqtr` column.
**Code**: Panel builder `create_lead_variables()` lines 311-315:
```python
panel["start_date_dt"] = pd.to_datetime(panel["start_date"], errors="coerce")
panel["cal_yearqtr"] = (
    panel["start_date_dt"].dt.year * 10 + panel["start_date_dt"].dt.quarter
)
panel = panel.drop(columns=["start_date_dt"], errors="ignore")
```
This `cal_yearqtr` column is saved into the panel parquet but is never used by the runner. The runner obtains `cal_yr_qtr` (and `cal_yr`, `cal_qtr`) from `build_cal_yr_qtr_index()` called at runner line 183. The two columns are computed identically, but the name difference creates a redundant column in the parquet.
**Comparison**: H12 provenance doc (docs/provenance/H12.md) Known Issue 6 explicitly documents this pattern: "cal_yearqtr vs cal_yr_qtr: The panel builder creates a cal_yearqtr column (line 306-308), while the runner creates cal_yr_qtr via build_cal_yr_qtr_index()..."
**Severity**: Minor — no impact on results. Documentation gap compared to H12 standard.

---

## PHASE 7: PIPELINE, OUTPUTS, TREATMENT (Sections F, G, H)

### F-CHECK: Data Pipeline

**F1 — Dependency Chain (7 steps)**:
Verified each step against code:
1. Raw inputs: Compustat parquet, linguistic output dir, CRSP files, master_sample_manifest.parquet — consistent with panel builder imports and file paths in docstring. PASS.
2. Engine loading: CompustatEngine (RepurchaseIntensity + controls), LinguisticEngine (4 IVs), CRSPEngine (DailyVola) — builders dict in panel builder lines 93-120. PASS.
3. Panel builder: 18 builders (counted: manifest + 4 IVs + repurchase_intensity + size + book_lev + tobins_q + roa + cash_holdings + capex_intensity + dividend_payer + ocf_volatility + sales_growth + rd_intensity + cash_flow + volatility = 18), file_name merges, fiscal_qtr_id lead/lag creation. PASS.
4. Runner loading: loads parquet (lines 169-173), calls build_cal_yr_qtr_index (line 183), filter_main_sample (line 565). PASS.
5. Sample filtering: Lagged_DV creation (line 213), Inf→NaN (line 224), DV filter (lines 227-229), complete case (lines 232-233), min calls (lines 236-240). PASS.
6. Regression: 12 PanelOLS specs in MODEL_SPECS loop. PASS.
7. Table generation: generate_all_tables.py entry. PASS.

**F2 — Data Engines**: CompustatEngine, LinguisticEngine, CRSPEngine — all verified against builder imports (panel builder lines 50-70). PASS.

**F3 — Merge Operations**:
All 4 merge types documented:
- Manifest base + each builder via file_name (left join, 1:1 validated): code lines 150-153. PASS.
- lead_lookup merge: `on=["gvkey", "fiscal_qtr_id"], how="left"` (line 278). PASS.
- lag_lookup merge: `on=["gvkey", "fiscal_qtr_id"], how="left"` (line 305). PASS.
- CompustatEngine merge_asof backward within gvkey: code pattern verified. PASS.
- fqtr attachment per-gvkey merge_asof (lines 196-226): matches doc description. PASS.

### G-CHECK: Outputs

**G1 (Panel Builder)**:
Doc lists: h17_repurchase_intensity_panel.parquet, summary_stats.csv, run_manifest.json
Code: panel builder lines 380-394 writes exactly these 3 files. No extra files. PASS.
Builder does NOT write a report.md file — doc correctly omits it. PASS.

**G2 (Runner)**:
Doc lists: h17_repurchase_intensity_table.tex, model_diagnostics.csv, summary_stats.csv, summary_stats.tex, sample_attrition.csv, sample_attrition.tex, regression_results_col{1-12}.txt, run_manifest.json.

Code:
- h17_repurchase_intensity_table.tex: line 491 `with open(tex_path, "w")` — PASS
- model_diagnostics.csv: line 526 `diag_df.to_csv(out_dir / "model_diagnostics.csv")` — PASS
- summary_stats.csv: line 582 `output_csv=out_dir / "summary_stats.csv"` — PASS
- summary_stats.tex: line 583 `output_tex=out_dir / "summary_stats.tex"` — PASS
- sample_attrition.csv/.tex: line 620 `generate_attrition_table(attrition_stages, out_dir, ...)` — PASS (function writes both)
- regression_results_col{N}.txt: lines 511-522 `open(out_dir / fname, "w")` — PASS
- run_manifest.json: lines 624-629 `generate_manifest(...)` — PASS

Runner does NOT write a report_step4 file — doc correctly omits it. PASS.

**G3 — Summary Statistics**:
Doc claims 18 variables from "runner lines 119-138". Code: SUMMARY_STATS_VARS defined at lines 119-138 with exactly 18 entries. All 18 variable names and labels match the doc's G3 table exactly. PASS.

### H-CHECK: Outlier/Missing Treatment

**H1 — Winsorization**:
- Level: "1%/99% by fiscal year (fyearq)" — code uses `year_col = comp["fyearq"]` (line 1229), `_winsorize_by_year` with min_obs=10 (line 453). PASS.
- Applied to (from doc): lnAssets, TobinsQ, ROA, Leverage, Capex, CashRatio, sCFO, RDSales, RepurchaseIntensity — all in COMPUSTAT_COLS, none in skip_winsorize. PASS.
- CashFlowAt/SalesGrowth in skip_winsorize (lines 1219-1220) because already winsorized in Biddle. PASS.
- NOT applied: linguistic IVs (no winsorization in LinguisticEngine), DivDummy (in skip_winsorize line 1218), DailyVola (CRSPEngine, not in _compute_and_winsorize). PASS.

**H2 — Missing Data**:
- Inf/-Inf → NaN in CompustatEngine (line 1203-1204 for ratio_cols) and runner (line 224). PASS.
- Complete-case deletion via `df[required].notna().all(axis=1)` (line 233). PASS.
- RepurchaseIntensity-specific NaN rules (bad de-cumulation, missing/non-positive lagged atq, non-consecutive gap): all documented and code-verified. PASS.

**H3 — Transformations**:
- lnAssets: ln(atq) — code line 943. PASS.
- sCFO: rolling std — code function `_compute_ocf_volatility()`. PASS.
- DailyVola: annualized std(daily_ret) * sqrt(252) * 100 — from CRSPEngine/VolatilityBuilder. PASS.

---

### FAIL-5: ATTRITION TABLE STAGE COUNT DISCREPANCY

**Provenance doc claims (D2)**: 5-step attrition cascade with complete-case (step 4) and min-calls (step 5) as separate steps.
**Code**: Runner lines 614-619 generate the actual attrition CSV/TEX with 4 stages:
```python
attrition_stages = [
    ("Full panel", full_n),
    ("Main sample (excl Finance/Utility)", main_n),
    ("RepurchaseIntensity non-null", n_dv_valid),
    ("After complete-case + min-calls (col 1)", first["n_obs"]),
]
generate_attrition_table(attrition_stages, out_dir, "H17 Repurchase Intensity")
```
The actual output files (`sample_attrition.csv`, `sample_attrition.tex`) contain 4 rows, collapsing steps 4 and 5 into one entry labeled "After complete-case + min-calls (col 1)".
**Impact**: The 5-step conceptual description in D2 is accurate about what the code logically does. The discrepancy is that anyone reading the output CSV will see 4 rows, not 5.
**Severity**: Minor.

---

## PHASE 8: GENERATE_ALL_TABLES.PY ENTRY (Section I)

**Provenance doc shows**:
```python
{
    "id": "H17",
    "dir": "h17_repurchase_intensity/2026-03-27_095020",
    "caption": "H17: Speech Uncertainty and Repurchase Intensity",
    "label": "tab:h17",
    "cols": 12,
    "dvs": [
        ("RepurchaseIntensity", 6),
        (r"RepurchaseIntensity\_lead\_qtr", 6),
    ],
    "tail": "two",
    "hyp_dir": None,
}
```

**Actual code** (generate_all_tables.py lines 317-329): Character-for-character identical.

**Field verification**:
| Field | Doc | Code | Match |
|-------|-----|------|-------|
| id | "H17" | "H17" | PASS |
| dir | "h17_repurchase_intensity/2026-03-27_095020" | same | PASS |
| caption | "H17: Speech Uncertainty and Repurchase Intensity" | same | PASS |
| label | "tab:h17" | "tab:h17" | PASS |
| cols | 12 | 12 | PASS |
| dvs[0] | ("RepurchaseIntensity", 6) | same | PASS |
| dvs[1] | (r"RepurchaseIntensity\_lead\_qtr", 6) | same | PASS |
| tail | "two" | "two" | PASS |
| hyp_dir | None | None | PASS |

No key_vars or key_tails fields in the actual entry; doc correctly omits them.

Doc verification table checks:
- tail matches runner two-tailed hypothesis: PASS
- hyp_dir None for two-tailed: PASS
- cols 12 = len(MODEL_SPECS) = 12: PASS
- dvs: 6 contemp + 6 lead = 12: PASS

**Phase 8: PASS — 8/8**

---

## PHASE 9: MODEL-FAMILY ADDENDUM (Section K)

Identified model family: PanelOLS. K1 should be filled; K2-K6 should be N/A.

### K1 — PanelOLS Specifics

**Entity effects (Industry FE)**:
- Doc: `other_effects=df_panel["ff12_code"]` with `entity_effects=False, time_effects=True`
- Code lines 287-293: `PanelOLS(entity_effects=False, time_effects=True, other_effects=df_panel["ff12_code"])`
- **PASS**

**Entity effects (Firm FE)**:
- Doc: `EntityEffects` in `PanelOLS.from_formula()` with `TimeEffects`
- Code lines 298-300: `formula = f"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"` followed by `PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)`
- **PASS**

**Time effects**:
- Doc: `time_effects=True` for both paths; cal_yr for YrFE specs; cal_yr_qtr for YQ specs
- Code: industry path has explicit `time_effects=True` (line 291); firm path uses `TimeEffects` keyword in formula (line 299); time index set via `set_index(["gvkey", time_col])` (line 283) where time_col switches per spec
- **PASS**

**drop_absorbed**:
- Doc: True for all specifications
- Code: line 293 (industry path) and line 300 (firm path) both have `drop_absorbed=True`
- **PASS**

**check_rank**:
- Doc: False for industry FE (API path); default for firm FE (formula path)
- Code: line 294 has `check_rank=False` in industry path; no check_rank argument in firm path (line 300)
- **PASS**

**Singleton handling**:
- Doc: Default PanelOLS behavior via drop_absorbed=True
- Code: No explicit singleton handling; drop_absorbed=True handles absorbed parameters
- **PASS**

**R-squared reporting**:
- Doc: Overall R² (model.rsquared) + manually computed Adj R²: `1 - (1-R2)*(nobs-1)/df_resid`
- Code lines 307 and 318: `model.rsquared` and `1 - (1 - model.rsquared) * (model.nobs - 1) / model.df_resid`
- **PASS**

**K2-K6**: All N/A. Correct — suite uses PanelOLS only.

**Phase 9: PASS — 7/7**

---

## PHASE 10: QUALITY GATE CHECKLIST

| # | Quality Gate | Met? | Evidence |
|---|-------------|------|----------|
| 1 | Every variable in every regression spec appears in Variable Dictionary with explicit formula and source engine | PARTIAL | fyearq_int is a required non-null column (runner line 215) not in the dict. 24/25 required variables covered. |
| 2 | The model equation matches what the code actually estimates | YES | B1 equations verified against exog construction and FE paths in runner |
| 3 | The specification register accounts for every model column | YES | 12 rows in C verified against 12 MODEL_SPECS entries; all fields match |
| 4 | The attrition cascade has row counts for each filter step | PARTIAL | Counts correctly marked [UNVERIFIED]; but cascade shows 5 steps while actual output CSV has 4 stages (complete-case + min-calls combined) |
| 5 | The tail test direction matches between runner code and generate_all_tables.py | YES | Runner docstring: "Two-tailed"; generate_all_tables: "tail": "two"; _sig_stars uses two-tailed thresholds |
| 6 | The FE specification matches between docstring, code, and this document | YES | Docstring (lines 17-22), code (lines 263-301), doc (B5, K1) all agree |
| 7 | Every merge in the panel builder is documented with join keys and type | YES | F3 documents all 5 merge operations with correct keys and join types |
| 8 | The output file list matches what the runner actually writes | YES | G1 (3 files) and G2 (8 file types) verified against all write operations in runner/builder |
| 9 | The model-family addendum is filled for the correct family only | YES | K1 (PanelOLS) filled with all sub-checks; K2-K6 all N/A |
| 10 | Any claim marked [UNVERIFIED] has an explanation of what blocks verification | YES | All 15 [UNVERIFIED] cells in D2 explained as "runtime-dependent; see sample_attrition.csv" |

**Phase 10: 8/10** (QG-1 partial: fyearq_int gap; QG-4 partial: stage count mismatch)

---

## PHASE 11: CROSS-REFERENCE CONSISTENCY

### Check 1: DVs in B2 match DVs in C
B2: RepurchaseIntensity, RepurchaseIntensity_lead_qtr.
C: cols 1-6 DV = RepurchaseIntensity; cols 7-12 DV = RepurchaseIntensity_lead_qtr.
**PASS**

### Check 2: DVs in C match DVs in I
C: RepurchaseIntensity (6 cols) + RepurchaseIntensity_lead_qtr (6 cols).
I: `("RepurchaseIntensity", 6), (r"RepurchaseIntensity\_lead\_qtr", 6)`.
**PASS**

### Check 3: Controls in B4 match variables in E
B4 Base 9 controls: all 9 appear in E with formulas. B4 Extended +4: SalesGrowth, RDSales, CashFlowAt, DailyVola all in E.
Lagged_DV and RepurchaseIntensity_lag both in E.
**PASS**

### Check 4: Column count in A matches rows in C
A: "Columns: 12". C table: 12 rows.
**PASS**

### Check 5: Column count in A matches "cols" in I
A: 12. I: `"cols": 12`.
**PASS**

### Check 6: Tail direction in A matches B7 matches I
A: "two-tailed". B7: "Two-tailed. P-value computation: Two-tailed p-values used directly from PanelOLS output." I: `"tail": "two"`.
**PASS**

### Check 7: FE in B5 matches C matches K1
B5: Industry (ff12_code) via other_effects; Firm (gvkey) via EntityEffects; time = cal_yr or cal_yr_qtr.
C: FE columns clearly specify Industry/Firm and Cal Yr/Cal Yr-Qtr per spec.
K1: entity_effects=False + other_effects=ff12_code (industry); EntityEffects + TimeEffects formula (firm); time_effects=True for both; cal_yr or cal_yr_qtr as panel time index.
All three sections consistent.
**PASS**

### Check 8: Panel index in A matches set_index in K1
A: "(gvkey, cal_yr) for cols 1-4, 7-10; (gvkey, cal_yr_qtr) for cols 5-6, 11-12"
K1: "cal_yr used as panel time index for Calendar Year FE specs. cal_yr_qtr used as panel time index for Year-Quarter FE specs."
Code (runner line 283): `df_panel = df_prepared.set_index(["gvkey", time_col])` where time_col switches per spec.
**PASS**

**Phase 11: PASS — 8/8**

---

## FAILURES (DETAILED)

| # | Phase | Check | Provenance Doc Claims | Actual Code Says | Severity | Fix Required |
|---|-------|-------|----------------------|-----------------|----------|-------------|
| 1 | L | L.6 — line number for fillna(0) | "line 1053: `comp["prstkcy"].fillna(0)`" | Line 1053 = `is_q1 = comp["fqtr"] == 1`; fillna(0) is at line 1058 | Minor | Change "line 1053" to "line 1058" |
| 2 | B2 | De-cumulation line range | "(CompustatEngine, lines 1040-1087)" | H17 extension begins at line 1045; comp.drop() runs through line 1092 | Minor | Change to "lines 1045-1092" |
| 3 | E | Variable dictionary completeness | fyearq_int absent | Runner line 215 requires fyearq_int non-null; panel builder line 186 creates it | Minor | Add fyearq_int to dictionary as Identifier type |
| 4 | L | Known Issues | No mention of cal_yearqtr orphan column | Panel builder line 312 creates cal_yearqtr; runner never uses it (uses cal_yr_qtr from build_cal_yr_qtr_index) | Minor | Add known issue matching H12.md Known Issue 6 |
| 5 | D2/G | Attrition stage count | D2 table has 5 separate steps | Runner attrition_stages (lines 614-619) has 4 entries: complete-case and min-calls combined into one | Minor | Add note: actual sample_attrition.csv has 4 stages, combining steps 4-5 |

---

## CORRECTIONS REQUIRED

### Correction 1: Fix line reference in L.6 (Known Issues)

**Section**: L — Known Issues, item 6, last sentence
**Current text**: `"(line 1053: comp["prstkcy"].fillna(0))"`
**Correct text**: `"(line 1058: comp["prstkcy"].fillna(0))"`
**Code reference**: `_compustat_engine.py` line 1053 = `is_q1 = comp["fqtr"] == 1`; line 1058 = `comp["prstkcy"].fillna(0)` (inside the np.where for is_q1 branch).

### Correction 2: Fix de-cumulation line range in B2

**Section**: B2 — Dependent Variable(s), de-cumulation logic header
**Current text**: `"De-cumulation logic (CompustatEngine, lines 1040-1087):"`
**Correct text**: `"De-cumulation logic (CompustatEngine, lines 1045-1092):"`
**Code reference**: `_compustat_engine.py` line 1045 = `# --- H17 extension: RepurchaseIntensity...`; lines run through `comp = comp.drop(columns=[...])` at 1087-1092. Logical block ends at 1092.

### Correction 3: Add fyearq_int to Variable Dictionary (Section E)

**Section**: E — Variable Dictionary, at end of FE identifier rows
**Current text**: Table ends after `cal_yr_qtr` row.
**Add row**:
```
| fyearq_int | Fiscal Year (integer) | Identifier | pd.to_numeric(fyearq, errors="coerce") | Panel builder: fyearq from CompustatEngine | No | Static per fiscal quarter |
```
**Code reference**: Panel builder line 186: `panel["fyearq_int"] = pd.to_numeric(panel["fyearq"], errors="coerce")`. Runner line 215: `required = [..., "fyearq_int", ...]` — fyearq_int must be non-null to pass complete-case filter.

### Correction 4: Add cal_yearqtr Known Issue (Section L)

**Section**: L — Known Issues
**Current text**: 6 issues listed; none mentions cal_yearqtr.
**Add** (new item 7):
> 7. **cal_yearqtr vs cal_yr_qtr**: The panel builder's `create_lead_variables()` function (lines 311-314) creates a `cal_yearqtr` column (computed as `start_date.dt.year * 10 + start_date.dt.quarter` from start_date). This column is stored in the panel parquet but is never read by the runner. The runner independently creates `cal_yr_qtr` (and `cal_yr`, `cal_qtr`) via `build_cal_yr_qtr_index()` (panel_utils.py, called at runner line 183). Both formulas are identical, so results are unaffected. The redundant `cal_yearqtr` column appears in the panel parquet alongside the correct `cal_yr_qtr` column. This is also documented in H12.md Known Issue 6 as a pattern shared across panel builders.
**Code reference**: Panel builder lines 311-314 create `cal_yearqtr`; runner line 183 calls `build_cal_yr_qtr_index()` which creates `cal_yr_qtr`.

### Correction 5: Add attrition stage count note (Section D2)

**Section**: D2 — Exclusion Criteria, end note paragraph
**Current text**: "Note: Steps 3-5 are applied independently per model specification in `prepare_regression_data()`. N may vary across columns due to different DVs and different required columns (e.g., cal_yr_qtr for YQ specs)."
**Add** after this paragraph:
> Note on output file: The `sample_attrition.csv` and `sample_attrition.tex` files generated at runtime (runner lines 614-619) contain only 4 stages, combining steps 4 and 5 into a single entry labeled "After complete-case + min-calls (col 1)". The 5-step conceptual cascade above describes the code's filter logic; the 4-stage output table is what appears in the actual files.
**Code reference**: Runner lines 614-619, `attrition_stages` list with 4 tuples passed to `generate_attrition_table()`.

---

## ADDITIONAL OBSERVATIONS (NOT FAILURES)

1. **ROA avg_assets precision**: B4 describes "avg_assets = (atq_t + atq_{t-1}) / 2" without clarifying these are annual (Q4) atq values. The leading phrase "iby_annual (Q4)" implies annual context, so this is mildly ambiguous but consistent. No correction required.

2. **Builder count verification**: Doc claims "18 builders" in F1. Code has exactly 18 entries in the `builders` dict (lines 93-120): manifest + 4 IVs + repurchase_intensity + size + book_lev + tobins_q + roa + cash_holdings + capex_intensity + dividend_payer + ocf_volatility + sales_growth + rd_intensity + cash_flow + volatility. CORRECT.

3. **Legacy _p_one field**: B7 and L.3 correctly identify and explain the legacy naming. Line 329 reference in B7/L.3 is accurate (`meta[f"{iv}_p_one"] = p_two  # two-tailed`). This documentation is a genuine aid to future readers.

4. **Extended-only for YQ specs (cols 5-6, 11-12)**: Correctly documented in C layout note. Consistent with MODEL_SPECS entries.

5. **77% zero mass point**: Correctly cited from runner docstring line 32. Noted in both L.1 and runner LaTeX notes line 483.

6. **prstkcy scope (common + preferred)**: Correctly noted as L.2. Runner docstring line 33 confirms: "prstkcy includes both common AND preferred stock repurchases (standard)."

7. **Inf→NaN double handling**: Doc H2 notes Inf→NaN in both CompustatEngine (line 1203-1204) and runner (line 224). Both locations verified in code. Correctly documented.
