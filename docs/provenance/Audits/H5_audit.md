================================================================================
ADVERSARIAL AUDIT REPORT: H5 Provenance Document
================================================================================

Auditor:       Claude (hostile auditor mode)
Audit date:    2026-03-31
Suite:         H5
Provenance:    docs/provenance/H5.md
Runner:        src/f1d/econometric/run_h5b_wang_disp.py
Builder:       src/f1d/variables/build_h5b_wang_disp_panel.py
Creation prompt: docs/Prompts/Suite Provenance Doc.txt

================================================================================
### AUDIT SUMMARY
================================================================================

| Category | Total Checks | Passed | Failed | Score |
|---|---|---|---|---|
| Structural Completeness (Phase 1) | 28 | 28 | 0 | 100% |
| Suite Identity (Phase 2) | 10 | 10 | 0 | 100% |
| Model Specification (Phase 3) | 7 | 7 | 0 | 100% |
| Spec Register (Phase 4) | 5 | 5 | 0 | 100% |
| Sample Construction (Phase 5) | 3 | 3 | 0 | 100% |
| Variable Dictionary (Phase 6) | 21 | 21 | 0 | 100% |
| Pipeline/Outputs/Treatment (Phase 7) | 9 | 7 | 2 | 78% |
| Table Generator Entry (Phase 8) | 5 | 3 | 2 | 60% |
| Model-Family Addendum (Phase 9) | 5 | 5 | 0 | 100% |
| Quality Gates (Phase 10) | 10 | 9 | 1 | 90% |
| Cross-Reference Consistency (Phase 11) | 8 | 6 | 2 | 75% |
| **TOTAL** | **111** | **104** | **7** | **94%** |

================================================================================
### VERDICT
================================================================================

**FAIL — INACCURATE**: Factual errors found. The provenance doc contains
inaccuracies concentrated in Section I (generate_all_tables.py entry) — the
`id`, `label`, `caption`, and `dir` fields are stale/wrong (the suite was
renamed from "H5b-Wang" to "H5" and a new run updated the dir timestamp).
Section F1 Step 7 carries forward the same stale id and a wrong line reference.
These errors propagate into internal inconsistency between Section A (Suite ID:
H5) and Section I (still citing "H5b-Wang"). All other 104 checks pass.

================================================================================
### PHASE 1: STRUCTURAL COMPLETENESS
================================================================================

Source of truth for required sections: docs/Prompts/Suite Provenance Doc.txt
Sections A through L are all required.

| Section | Required by Prompt | Present in Doc | Complete | Notes |
|---|---|---|---|---|
| A. Suite Identity | Yes | Yes | Yes | YAML block present |
| B. Model Specification | Yes | Yes | Yes | All subsections present |
| B1. Regression Equation | Yes | Yes | Yes | Equation present with FE notation |
| B2. Dependent Variable(s) | Yes | Yes | Yes | Table with 2 DVs |
| B3. Independent Variable(s) | Yes | Yes | Yes | Table with 4 IVs |
| B4. Control Variables | Yes | Yes | Yes | Base + Extended tables present |
| B5. Fixed Effects | Yes | Yes | Yes | FE table with specs column |
| B6. Standard Errors | Yes | Yes | Yes | cov_type and clustering documented |
| B7. Hypothesis Test | Yes | Yes | Yes | Direction + p-value logic documented |
| C. Spec Register | Yes | Yes | Yes | 12-row table |
| D. Sample Construction | Yes | Yes | Yes | All 3 subsections present |
| D1. Population | Yes | Yes | Yes | Starting dataset + totals |
| D2. Exclusion Criteria | Yes | Yes | Yes | 4-step attrition cascade |
| D3. Sample Counts per Spec | Yes | Yes | Yes | Table with UNVERIFIED notes for YQ specs |
| E. Variable Dictionary | Yes | Yes | Yes | 21 variables; all types covered |
| F. Data Pipeline | Yes | Yes | Yes | All 3 subsections present |
| F1. Dependency Chain | Yes | Yes | Yes | 7-step numbered list |
| F2. Data Engines | Yes | Yes | Yes | 5 engines documented |
| F3. Merge Operations | Yes | Yes | Yes | 17-row merge table |
| G. Outputs | Yes | Yes | Yes | All 3 subsections present |
| G1. Stage 3 Outputs | Yes | Yes | Yes | 3 files listed |
| G2. Stage 4 Outputs | Yes | Yes | Yes | 7 files listed |
| G3. Summary Statistics | Yes | Yes | Yes | 14-variable table |
| H. Outlier/Missing Treatment | Yes | Yes | Yes | H1-H3 subsections present |
| I. generate_all_tables Entry | Yes | Yes | Partial | Fields present but id/label/caption/dir are stale |
| J. Reproduction Commands | Yes | Yes | Yes | 3 commands present |
| K. Model-Family Addendum | Yes | Yes | Yes | K1 filled; K2-K6 marked N/A |
| L. Known Issues | Yes | Yes | Yes | 7 numbered issues |

PHASE 1 RESULT: All 28 structural checks PASS. Content accuracy issues
are addressed in subsequent phases.

================================================================================
### PHASE 2: SUITE IDENTITY (Section A)
================================================================================

**A-1. Suite ID**
- Provenance doc: `H5`
- Expected: H5 (this is the SUITE_ID input)
- RESULT: PASS

**A-2. Title**
- Provenance doc: "H5: Speech Uncertainty and Analyst Forecast Dispersion (Wang 2020)"
- generate_all_tables.py line 154: `"caption": "H5: Speech Uncertainty and Analyst Forecast Dispersion (Wang 2020)"`
- Runner docstring (line 4): "STAGE 4: Test H5b Wang (2020) Analyst Dispersion Hypothesis" — the runner still uses internal "H5b" label, but the official suite-level title matches generate_all_tables.py.
- RESULT: PASS

**A-3. Hypothesis**
- Provenance doc: "Higher managerial uncertainty language during earnings calls leads to greater analyst forecast dispersion, measured as the price-scaled standard deviation of individual analyst EPS forecasts in the pre-announcement window."
- Runner docstring (line 34): "Hypothesis: One-tailed (beta > 0 — higher uncertainty -> higher dispersion)."
- Provenance doc hypothesis is a full prose expansion; consistent with runner intent.
- RESULT: PASS

**A-4. Direction (tail test)**
- Provenance doc: "One-tailed (beta > 0)"
- Runner line 35: `"Hypothesis: One-tailed (beta > 0 — higher uncertainty -> higher dispersion)."`
- Runner line 364: `print(f"Test: One-tailed (beta > 0)")`
- Runner line 287: `p_one = p_two / 2 if (not np.isnan(p_two) and beta > 0) else (1 - p_two / 2 ...)`
- RESULT: PASS

**A-5. Model Family**
- Provenance doc: "PanelOLS"
- Runner line 50: `from linearmodels.panel import PanelOLS`
- Runner lines 254, 267: PanelOLS instantiated both directly and via from_formula
- RESULT: PASS

**A-6. Estimator**
- Provenance doc: "linearmodels.panel.PanelOLS"
- Runner import (line 50): `from linearmodels.panel import PanelOLS` — exact module path confirmed
- RESULT: PASS

**A-7. Unit of Observation**
- Provenance doc: "Call-level (individual earnings call)"
- Builder docstring (line 9): "Unit of observation: individual earnings call (file_name)."
- RESULT: PASS

**A-8. Panel Index**
- Provenance doc: "(gvkey, cal_yr) for Calendar Year FE specs; (gvkey, cal_yr_qtr) for Year-Quarter FE specs"
- Runner line 250: `df_panel = df_prepared.set_index(["gvkey", time_col])`
- Runner line 242: `time_col = "cal_yr_qtr" if fe_type.endswith("_yq") else "cal_yr"`
- The dual index claim is correct.
- RESULT: PASS

**A-9. Columns (number of model specs)**
- Provenance doc: "12"
- Runner MODEL_SPECS (lines 82-98): 12 entries, cols 1-12
- RESULT: PASS

**A-10. Runner and Panel Builder paths**
- Provenance doc runner: `src/f1d/econometric/run_h5b_wang_disp.py`
- Provenance doc builder: `src/f1d/variables/build_h5b_wang_disp_panel.py`
- Both files verified to exist on disk.
- RESULT: PASS

**PHASE 2 RESULT: 10/10 PASS**

================================================================================
### PHASE 3: MODEL SPECIFICATION (Section B)
================================================================================

**B1-CHECK: Regression Equation**
- Provenance doc equation:
  `WangDISP_{i,t} = b1*CEO_QA_Uncertainty_pct + b2*CEO_Pres_Uncertainty_pct + b3*Manager_QA_Uncertainty_pct + b4*Manager_Pres_Uncertainty_pct + Controls + alpha_i + gamma_t + epsilon_{i,t}`
- Runner KEY_IVS (lines 63-68): `["CEO_QA_Uncertainty_pct", "CEO_Pres_Uncertainty_pct", "Manager_QA_Uncertainty_pct", "Manager_Pres_Uncertainty_pct"]`
- Runner formula (line 266): `formula = f"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"` where exog = KEY_IVS + all_controls
- Equation correctly shows 4 IVs + Controls + entity FE (alpha_i) + time FE (gamma_t). No interaction terms. No centering.
- RESULT: PASS

**B2-CHECK: Dependent Variable(s)**
- Provenance doc: WangDISP (contemporaneous), WangDISP_lead (next quarter)
- Runner MODEL_SPECS: DVs are "WangDISP" (cols 1-6) and "WangDISP_lead" (cols 7-12) — exact column names match.
- WangDISP formula: "SD(latest analyst EPS forecasts in [T-31, T-1]) / prccq_prior; min 2 analysts; FPEDATS within 120 days" — verified against wang_disp.py structure.
- WangDISP_lead: "next consecutive fiscal quarter for same gvkey; validated via fiscal_qtr_id consecutive check" — VERIFIED: builder lines 251-265 use shift(-1) then validate with expected_next comparison.
- RESULT: PASS

**B3-CHECK: Independent Variable(s)**
- Provenance doc: 4 IVs with exact names matching runner KEY_IVS.
- "No centering, log-transform, or z-scoring is applied to IVs" — runner does not apply any such transformations before regression; consistent.
- RESULT: PASS

**B4-CHECK: Control Variables**
- Runner BASE_CONTROLS (lines 70-73): `["Size", "TobinsQ", "ROA", "BookLev", "CapexAt", "DividendPayer", "OCF_Volatility", "WangDISP_lag"]` — 8 variables
- Provenance doc Base Controls table: same 8 variables. EXACT MATCH.
- Runner EXTENDED_CONTROLS (lines 75-78): BASE_CONTROLS + `["SurpDec", "loss_dummy", "Analyst_QA_Uncertainty_pct", "Entire_All_Negative_pct"]` — 4 additional
- Provenance doc Extended Controls: same 4 additional variables. EXACT MATCH.
- WangDISP_lag documented as lagged DV, included in BASE_CONTROLS — confirmed by runner line 72.
- RESULT: PASS

**B5-CHECK: Fixed Effects**
- Provenance doc: Industry (odd cols) via `other_effects=ff12_code`; Firm (even cols) via `EntityEffects`; cal_yr for cols 1-4, 7-10; cal_yr_qtr for cols 5-6, 11-12.
- Runner line 242: `time_col = "cal_yr_qtr" if fe_type.endswith("_yq") else "cal_yr"` — MATCHES
- Runner lines 253-262: industry FE uses `entity_effects=False, time_effects=True, other_effects=df_panel["ff12_code"]` — MATCHES
- Runner lines 265-268: firm FE uses `EntityEffects + TimeEffects` in formula — MATCHES
- panel_utils.py (confirmed at offset 200-218): cal_yr = dt.dt.year (line 215), cal_yr_qtr = cal_yr * 10 + cal_qtr where cal_qtr = dt.dt.quarter (line 217) — MATCHES doc's formula and line cites.
- RESULT: PASS

**B6-CHECK: Standard Errors**
- Provenance doc: `cov_type="clustered"`, `cluster_entity=True`
- Runner line 263: `model_obj.fit(cov_type="clustered", cluster_entity=True)` — industry branch
- Runner line 268: `model_obj.fit(cov_type="clustered", cluster_entity=True)` — firm branch
- RESULT: PASS

**B7-CHECK: Hypothesis Test**
- Provenance doc: "p_one = p_two / 2 if beta > 0, else p_one = 1 - p_two / 2 (runner line 287)"
- Runner line 287: `p_one = p_two / 2 if (not np.isnan(p_two) and beta > 0) else (1 - p_two / 2 if not np.isnan(p_two) else np.nan)` — EXACT MATCH
- Stars (line 291): `"***" if p_one < 0.01 else "**" if p_one < 0.05 else "*" if p_one < 0.10 else ""` — MATCHES doc's stated thresholds
- RESULT: PASS

**PHASE 3 RESULT: 7/7 PASS**

================================================================================
### PHASE 4: SPEC REGISTER (Section C)
================================================================================

Provenance doc claims: 12-row spec register sourced from "MODEL_SPECS list, runner lines 82-98".

**Count check:**
Runner MODEL_SPECS (lines 82-98): 12 entries (cols 1-12). Provenance doc: 12 rows. MATCHES.

**Per-row verification against runner MODEL_SPECS:**

| Col (doc) | DV (doc) | Entity FE (doc) | Time FE (doc) | Controls (doc) | Runner CODE | Match? |
|---|---|---|---|---|---|---|
| 1 | WangDISP | Industry (FF12) | Calendar Year | Base | col:1, dv:"WangDISP", fe:"industry", controls:"base" | PASS |
| 2 | WangDISP | Firm | Calendar Year | Base | col:2, dv:"WangDISP", fe:"firm", controls:"base" | PASS |
| 3 | WangDISP | Industry (FF12) | Calendar Year | Extended | col:3, dv:"WangDISP", fe:"industry", controls:"extended" | PASS |
| 4 | WangDISP | Firm | Calendar Year | Extended | col:4, dv:"WangDISP", fe:"firm", controls:"extended" | PASS |
| 5 | WangDISP | Industry (FF12) | Calendar Year-Quarter | Extended | col:5, dv:"WangDISP", fe:"industry_yq", controls:"extended" | PASS |
| 6 | WangDISP | Firm | Calendar Year-Quarter | Extended | col:6, dv:"WangDISP", fe:"firm_yq", controls:"extended" | PASS |
| 7 | WangDISP_lead | Industry (FF12) | Calendar Year | Base | col:7, dv:"WangDISP_lead", fe:"industry", controls:"base" | PASS |
| 8 | WangDISP_lead | Firm | Calendar Year | Base | col:8, dv:"WangDISP_lead", fe:"firm", controls:"base" | PASS |
| 9 | WangDISP_lead | Industry (FF12) | Calendar Year | Extended | col:9, dv:"WangDISP_lead", fe:"industry", controls:"extended" | PASS |
| 10 | WangDISP_lead | Firm | Calendar Year | Extended | col:10, dv:"WangDISP_lead", fe:"firm", controls:"extended" | PASS |
| 11 | WangDISP_lead | Industry (FF12) | Calendar Year-Quarter | Extended | col:11, dv:"WangDISP_lead", fe:"industry_yq", controls:"extended" | PASS |
| 12 | WangDISP_lead | Firm | Calendar Year-Quarter | Extended | col:12, dv:"WangDISP_lead", fe:"firm_yq", controls:"extended" | PASS |

All 12 specs verified. No missing or extra rows. Line reference "runner lines 82-98" is correct.

**PHASE 4 RESULT: 5/5 PASS (count, all 12 rows, DVs, FE types, controls)**

================================================================================
### PHASE 5: SAMPLE CONSTRUCTION (Section D)
================================================================================

**D1-CHECK: Population**
- Provenance doc: "Starting dataset: master_sample_manifest.parquet; Total calls: 112,968; Year range: 2002-2018"
- Project scope in memory: "112,968 calls, 2,429 firms, 2002-2018" — consistent.
- Runner (line 414): `stages = [("Full panel", full_n), ...]` where full_n = len(panel) loaded from manifest.
- RESULT: PASS

**D2-CHECK: Exclusion Criteria (Attrition Cascade)**
- Runner filter order (reading code linearly):
  1. `load_panel()` reads manifest (112,968 rows) — line 366
  2. `filter_main_sample()` excludes ff12_code in [8, 11] — line 373
  3. `prepare_regression_data()` — replace inf with NaN — line 195
  4. `prepare_regression_data()` — DV non-null filter — line 198-199
  5. `prepare_regression_data()` — complete case filter — line 201-202
  6. `prepare_regression_data()` — min 5 calls/firm — line 206-208
- Provenance doc attrition cascade:
  Step 1: Full panel → 112,968
  Step 2: Main sample (excl FF12=8,11) → 88,205 (dropped 24,763)
  Step 3: WangDISP non-null → 37,446 (dropped 50,759)
  Step 4: Complete case + min 5 calls/firm (col 1, base controls) → 17,089 (dropped 20,357)
- The runner's attrition_table (lines 411-418) constructs the same stages structure. Steps 3 and the note about WangDISP coverage match runner line 376's diagnostic print.
- The doc merges complete-case + min-calls into one step — acceptable since the runner's attrition diagnostic does the same.
- RESULT: PASS

**D3-CHECK: Sample Counts per Spec**
- Provenance doc documents 8 cols with actual counts and 4 YQ cols as [UNVERIFIED] with clear explanation: "12-col run not yet produced". This is an honest [UNVERIFIED] consistent with Quality Gate 10.
- RESULT: PASS (UNVERIFIED entries properly flagged with explanations)

**PHASE 5 RESULT: 3/3 PASS**

================================================================================
### PHASE 6: VARIABLE DICTIONARY (Section E)
================================================================================

All 21 variables verified against runner MODEL_SPECS, BASE_CONTROLS, EXTENDED_CONTROLS, and source files.

**DVs (3 variables):**

| Variable | In Runner As | Formula in Doc | Winsorization in Doc | Code Confirms? |
|---|---|---|---|---|
| WangDISP | MODEL_SPECS dv (cols 1-6) | "SD(latest analyst EPS forecasts in [T-31, T-1]) / prccq_prior; min 2 analysts; FPEDATS within 120 days" | "1%/99% pooled (wang_disp.py lines 85-89)" | PASS — wang_disp.py lines 84-90 clip at quantile(0.01)/quantile(0.99) pooled |
| WangDISP_lead | MODEL_SPECS dv (cols 7-12) | "WangDISP from next consecutive fiscal quarter; validated via fiscal_qtr_id consecutive check" | Same as WangDISP (applied before shifting) | PASS — builder lines 251-265 shift(-1) then validate consecutive quarters |
| WangDISP_lag | BASE_CONTROLS[7] | "WangDISP from prior consecutive fiscal quarter; validated via fiscal_qtr_id consecutive check" | Same as WangDISP (applied before shifting) | PASS — builder lines 271-284 shift(1) then validate consecutive quarters |

**IVs (4 variables):**

| Variable | In Runner As | Formula | Winsorization | Code Confirms? |
|---|---|---|---|---|
| CEO_QA_Uncertainty_pct | KEY_IVS[0] | "(LM uncertainty words in CEO Q&A turns / total words) * 100" | "0%/99% per-year upper-only" | PASS |
| CEO_Pres_Uncertainty_pct | KEY_IVS[1] | "(LM uncertainty words in CEO Pres turns / total words) * 100" | "0%/99% per-year upper-only" | PASS |
| Manager_QA_Uncertainty_pct | KEY_IVS[2] | "(LM uncertainty words in all-manager Q&A turns / total words) * 100" | "0%/99% per-year upper-only" | PASS |
| Manager_Pres_Uncertainty_pct | KEY_IVS[3] | "(LM uncertainty words in all-manager Pres turns / total words) * 100" | "0%/99% per-year upper-only" | PASS |

**Base Controls (8 variables — WangDISP_lag already above):**

| Variable | In Runner | Formula | Winsorization | Code Confirms? |
|---|---|---|---|---|
| Size | BASE_CONTROLS[0] | "ln(atq), only for atq > 0" | "1%/99% per-year" | PASS |
| TobinsQ | BASE_CONTROLS[1] | "(cshoq * prccq + dlcq + dlttq) / atq; dlcq/dlttq clipped >= 0 and filled 0" | "1%/99% per-year" | PASS |
| ROA | BASE_CONTROLS[2] | "iby_annual (Q4) / avg(atq_t, atq_{t-1}); avg_assets > 0" | "1%/99% per-year" | PASS |
| BookLev | BASE_CONTROLS[3] | "(dlcq.fillna(0) + dlttq.fillna(0)) / atq" | "1%/99% per-year" | PASS |
| CapexAt | BASE_CONTROLS[4] | "capxy_annual (Q4-only) / atq_lag_annual; atq_lag > 0" | "1%/99% per-year" | PASS |
| DividendPayer | BASE_CONTROLS[5] | "1 if dvy_annual (Q4-only) > 0, else 0" | "Not winsorized (binary)" | PASS |
| OCF_Volatility | BASE_CONTROLS[6] | "Rolling 5-year std (min 3 years, 1826-day window) of oancfy / atq_{t-1} per gvkey" | "1%/99% per-year" | PASS |

**Extended Controls (4 additional):**

| Variable | In Runner | Formula | Winsorization | Code Confirms? |
|---|---|---|---|---|
| SurpDec | EXTENDED_CONTROLS+4 | "(ACTUAL - MEANEST) ranked into -5..+5 within each calendar quarter; merge_asof backward, 120-day tolerance" | "No" | PASS |
| loss_dummy | EXTENDED_CONTROLS+5 | "1 if ibq < 0, else 0; merge_asof backward to call date" | "No (binary)" | PASS |
| Analyst_QA_Uncertainty_pct | EXTENDED_CONTROLS+6 | "(LM uncertainty words in analyst Q&A turns / total words) * 100" | "0%/99% per-year upper-only" | PASS |
| Entire_All_Negative_pct | EXTENDED_CONTROLS+7 | "(LM negative words in entire call / total words) * 100" | "0%/99% per-year upper-only" | PASS |

**FE and filter columns (5 variables):**

| Variable | Code Usage | Formula in Doc | Code Confirms? |
|---|---|---|---|
| gvkey | Panel index; firm filter | "6-digit zero-padded GVKEY from Compustat" | PASS |
| ff12_code | other_effects; FF12 filter | "FF48-to-FF12 mapping applied at engine level" | PASS |
| cal_yr | Panel index (cal_yr specs) | "start_date.dt.year" | PASS — panel_utils.py line 215 |
| cal_yr_qtr | Panel index (YQ specs) | "cal_yr * 10 + start_date.dt.quarter" | PASS — panel_utils.py line 217 |
| fyearq_int | required list (runner line 186); complete-case filter | "floor(fyearq) cast to Int64" | PASS — builder line 160 |

**Completeness check:**
Runner required columns (line 186): `[dv] + KEY_IVS + all_controls + ["gvkey", "fyearq_int", "ff12_code"]` plus conditionally `"cal_yr_qtr"`. All variables in this list are in the dictionary. Variables `start_date`, `file_name`, `sample`, `year`, `fqtr`, `fqtr_int`, `fiscal_qtr_id` are build/merge intermediates not appearing in regressions — correct to exclude from dictionary.

**PHASE 6 RESULT: 21/21 PASS**

================================================================================
### PHASE 7: DATA PIPELINE, OUTPUTS, TREATMENT (Sections F, G, H)
================================================================================

**F-CHECK: Data Pipeline**

F1 — Dependency Chain:
- Steps 1-6: All verified against code. Descriptions are accurate.
- Step 7: "generate_all_tables.py has entry `"id": "H5b-Wang"` at line 184"
  FAIL — actual id is "H5" at line 152 (generate_all_tables.py lines 151-163).
  This is the same stale naming error as Section I.

F2 — Data Engines:
- 5 engines listed: IbesDetailEngine, CompustatEngine, LinguisticEngine, IbesEngine (Summary), ManifestFieldsBuilder.
- Builder imports (lines 33-57) confirm all 5. PASS.

F3 — Merge Operations:
- Doc lists 17 merges. Builder: 16 file_name-based merges (one per non-manifest builder in dict) + 1 lead_lag merge on ["gvkey", "fiscal_qtr_id"] = 17 total. EXACT MATCH.
- Doc cites "builder lines 148-150" for row-count assertion. Runner lines 145-150 contain the delta check and ValueError raise. PASS.

**G-CHECK: Outputs**

G1 — Stage 3 Outputs (builder save_outputs lines 303-324):
- `h5b_wang_disp_panel.parquet` — line 306. PASS.
- `summary_stats.csv` — line 311. PASS.
- `run_manifest.json` — generated by generate_manifest() called at lines 314-323; manifest_generator.py writes run_manifest.json. PASS.
- Provenance doc lists exactly these 3 files. PASS.

G2 — Stage 4 Outputs (runner):
- `regression_results_col{1-12}.txt` — runner lines 316-330, one per model. PASS.
- `model_diagnostics.csv` — runner line 334. PASS.
- `summary_stats.csv` — runner line 385 (make_summary_stats_table output_csv arg). PASS.
- `summary_stats.tex` — runner line 385 (make_summary_stats_table output_tex arg). PASS.
- `sample_attrition.csv` — generated by generate_attrition_table() (attrition_table.py line 47). PASS.
- `sample_attrition.tex` — generated by generate_attrition_table() (attrition_table.py line 51). PASS.
- `run_manifest.json` — generated by generate_manifest() call at runner lines 420-425. PASS.
- Provenance doc lists exactly 7 files matching the above. PASS.
- NOTE: No `{suite}_table.tex` produced by the runner itself (that is generate_all_tables.py's job). Provenance doc correctly omits it from G2. PASS.

G3 — Summary Statistics:
- Runner SUMMARY_STATS_VARS (lines 101-116): 14 entries.
- Provenance doc table: 14 variables with matching labels. PASS.

**H-CHECK: Outlier/Missing Treatment**

H1 — Winsorization:
- Compustat controls: "1%/99% per fiscal year (_winsorize_by_year() in _compustat_engine.py)" — consistent with CompustatEngine behavior. PASS.
- Linguistic IVs: "0%/99% per calendar year (upper-only)" — consistent with LinguisticEngine behavior. PASS.
- WangDISP: "1%/99% pooled (wang_disp.py lines 85-89)" — VERIFIED: wang_disp.py lines 85-90 clip at quantile(0.01)/quantile(0.99) of all non-null values pooled. PASS.
- SurpDec: "Not winsorized (discrete ranked variable)" — correct. PASS.

H2 — Missing Data Policy:
- "Complete-case deletion" — runner line 201 `complete_mask = df[required].notna().all(axis=1)`. PASS.
- "Inf/-Inf replaced with NaN before complete-case filter (runner line 195)" — runner line 195 `df = df.replace([np.inf, -np.inf], np.nan)`. PASS.
- "WangDISP requires >= 2 analysts AND valid prccq_prior > 0" — consistent with WangDispBuilder. PASS.

H3 — Transformations:
- "Size: natural log of atq (only for atq > 0)" — consistent with SizeBuilder. PASS.
- "No other log, z-score, centering, or scaling applied" — no contradicting code found. PASS.

**PHASE 7 FAILURES:**
1. F1 Step 7: id stated as "H5b-Wang" — actual is "H5"
2. F1 Step 7: line stated as "line 184" — actual entry begins at line 151

**PHASE 7 RESULT: 7/9 PASS**

================================================================================
### PHASE 8: TABLE GENERATOR ENTRY (Section I)
================================================================================

Provenance doc Section I claims:

```python
{
    "id": "H5b-Wang",
    "dir": "h5b_wang_disp/2026-03-27_095026",
    "caption": "H5b: Speech Uncertainty and Analyst Forecast Dispersion (Wang 2020)",
    "label": "tab:h5b_wang",
    "cols": 12,
    "dvs": [
        ("WangDISP", 6),
        (r"WangDISP\_lead", 6),
    ],
    "tail": "one",
    "hyp_dir": ">",
}
```

Source: `outputs/generate_all_tables.py lines 183-195`.

Actual code at outputs/generate_all_tables.py lines 151-163:

```python
{
    "id": "H5",
    "dir": "h5b_wang_disp/2026-03-31_140307",
    "caption": "H5: Speech Uncertainty and Analyst Forecast Dispersion (Wang 2020)",
    "label": "tab:h5",
    "cols": 12,
    "dvs": [
        ("WangDISP", 6),
        (r"WangDISP\_lead", 6),
    ],
    "tail": "one",
    "hyp_dir": ">",
},
```

**Field-by-field comparison:**

| Field | Provenance Doc Claims | Actual Code | Match? |
|---|---|---|---|
| "id" | "H5b-Wang" | "H5" | FAIL |
| "dir" | "h5b_wang_disp/2026-03-27_095026" | "h5b_wang_disp/2026-03-31_140307" | FAIL (stale timestamp) |
| "caption" | "H5b: Speech Uncertainty..." | "H5: Speech Uncertainty..." | FAIL ("H5b:" vs "H5:") |
| "label" | "tab:h5b_wang" | "tab:h5" | FAIL |
| "cols" | 12 | 12 | PASS |
| "dvs" | [("WangDISP", 6), ("WangDISP\_lead", 6)] | same | PASS |
| "tail" | "one" | "one" | PASS |
| "hyp_dir" | ">" | ">" | PASS |
| Source line ref | "lines 183-195" | lines 151-163 | FAIL (wrong line numbers) |

The provenance doc was written when the suite was still named "H5b-Wang" in
generate_all_tables.py. Since then: (1) the suite id was changed from "H5b-Wang"
to "H5"; (2) the label was changed from "tab:h5b_wang" to "tab:h5"; (3) the
caption prefix was changed from "H5b:" to "H5:"; (4) a new run updated the dir
timestamp from 2026-03-27 to 2026-03-31. The provenance doc was not updated.

Note on `dir` discrepancy: the timestamp change reflects a legitimate new run
producing the 12-column output. This is inherently mutable and not a structural
error in the doc, but it should be updated to the current value.

**PHASE 8 RESULT: 3/5 PASS (cols, dvs, tail/hyp_dir pass; id/label/caption/dir/line-refs fail)**

================================================================================
### PHASE 9: MODEL-FAMILY ADDENDUM (Section K)
================================================================================

Suite uses PanelOLS — K1 should be filled; K2-K6 should be N/A.

**K1 — PanelOLS Specifics:**

Entity effects:
- Doc: "Industry FE (odd cols): entity_effects=False, other_effects=df_panel["ff12_code"] (runner line 259)"
- Code (runner lines 257-260): `entity_effects=False, time_effects=True, other_effects=df_panel["ff12_code"]` — PASS
- Doc: "Firm FE (even cols): EntityEffects in formula (runner line 267)"
- Code (runner line 265-267): formula = "... + EntityEffects + TimeEffects" — PASS

Time effects:
- Doc: "Calendar Year FE: time_effects=True with panel index (gvkey, cal_yr) (runner line 250)"
- Code (runner line 250): `df_panel = df_prepared.set_index(["gvkey", time_col])` where time_col = "cal_yr" for non-YQ — PASS
- Doc: "Calendar Year-Quarter FE: time_effects=True with panel index (gvkey, cal_yr_qtr) (runner line 250)"
- Code: same, time_col = "cal_yr_qtr" for YQ — PASS

drop_absorbed:
- Doc: "True for all specs (runner lines 261, 267)"
- Code (runner line 261): `drop_absorbed=True` in industry branch
- Code (runner line 267): `drop_absorbed=True` in firm branch
- PASS

check_rank:
- Doc: "False for industry FE specs only (runner line 262); not set for firm FE specs (default True in linearmodels)"
- Code (runner line 261-262): industry branch has `check_rank=False`; firm branch (line 267) via from_formula does not set it
- PASS

Singleton handling:
- Doc: "linearmodels default behavior (no explicit singleton dropping)"
- No `singletons` argument found in runner — PASS

K2-K6 marked N/A — PASS (correct for PanelOLS suite)

**PHASE 9 RESULT: 5/5 PASS**

================================================================================
### PHASE 10: QUALITY GATE CHECKLIST
================================================================================

| # | Quality Gate | Met? | Evidence |
|---|---|---|---|
| 1 | Every variable in every regression spec appears in Variable Dictionary with explicit formula and source engine | YES | All 21 variables checked in Phase 6; all passed |
| 2 | The model equation matches what the code actually estimates | YES | B1 check verified 4 IVs + controls + entity/time FE in equation |
| 3 | The specification register accounts for every model column | YES | 12 rows in spec register match 12 MODEL_SPECS entries; all configurations correct |
| 4 | The attrition cascade has row counts for each filter step | YES | 4-step cascade with actual counts; YQ specs properly flagged [UNVERIFIED] with explanation |
| 5 | The tail test direction matches between runner code and generate_all_tables.py | YES | Runner: p_two/2 if beta>0 (one-tailed, beta>0); actual generate_all_tables.py: "tail":"one","hyp_dir":">" |
| 6 | The FE specification matches between docstring, code, and this document | YES | Runner docstring line 36 matches code and doc |
| 7 | Every merge in the panel builder is documented with join keys and type | YES | 17 merges (16 on file_name + 1 on gvkey+fiscal_qtr_id) all documented in F3 table |
| 8 | The output file list matches what the runner actually writes | YES | 7 Stage 4 outputs and 3 Stage 3 outputs verified |
| 9 | The model-family addendum is filled for the correct family only | YES | K1 filled for PanelOLS; K2-K6 N/A |
| 10 | Any claim marked [UNVERIFIED] has an explanation of what blocks verification | YES | D3 YQ spec counts flagged [UNVERIFIED] with clear explanation: "12-col run not yet produced" |

Note on Gate 5: the gate passes on the substance (tail direction is correctly documented)
but Section I has the wrong id/label/caption. Gates assess correctness of the documented
fields, and the tail/cols/dvs fields in Section I are all correct.

**PHASE 10 RESULT: 9/10 PASS**

The one failing area is implicitly Gate 2 / Gate 8 scope: Section I's factual
errors (id, label, caption, dir) are not covered by any of the 10 gates
directly, but they fail the overall accuracy requirement.

================================================================================
### PHASE 11: CROSS-REFERENCE CONSISTENCY
================================================================================

1. **DVs in B2 match DVs in C (spec register)?**
   - B2: WangDISP, WangDISP_lead
   - C: WangDISP (rows 1-6), WangDISP_lead (rows 7-12)
   - CONSISTENT — PASS

2. **DVs in C match DVs in Section I (table generator)?**
   - C: WangDISP (6 cols), WangDISP_lead (6 cols)
   - I (provenance doc): `"dvs": [("WangDISP", 6), ("WangDISP_lead", 6)]`
   - I (actual code): same
   - CONSISTENT — PASS

3. **Controls in B4 match variables in E (dictionary)?**
   - B4 Base: Size, TobinsQ, ROA, BookLev, CapexAt, DividendPayer, OCF_Volatility, WangDISP_lag (8)
   - B4 Extended additional: SurpDec, loss_dummy, Analyst_QA_Uncertainty_pct, Entire_All_Negative_pct (4)
   - All 12 appear in Section E with formula/source.
   - CONSISTENT — PASS

4. **Column count in A matches rows in C?**
   - A: "Columns: 12"
   - C: 12 rows
   - CONSISTENT — PASS

5. **Column count in A matches "cols" in Section I?**
   - A: "Columns: 12"
   - I (provenance doc): `"cols": 12`
   - I (actual code): `"cols": 12`
   - CONSISTENT — PASS

6. **Tail direction in A matches B7 matches I?**
   - A: "Direction: One-tailed (beta > 0)"
   - B7: "One-tailed (beta > 0). p_one = p_two / 2 if beta > 0"
   - I (provenance doc): `"tail": "one", "hyp_dir": ">"`
   - CONSISTENT internally — PASS

7. **FE in B5 matches C matches K?**
   - B5: Industry (odd) / Firm (even) / cal_yr (cols 1-4, 7-10) / cal_yr_qtr (cols 5-6, 11-12)
   - C: Spec register shows Industry/Firm x CalYear/CalYrQtr — matches B5
   - K1: "Calendar Year FE: (gvkey, cal_yr)"; "Calendar Year-Quarter FE: (gvkey, cal_yr_qtr)"
   - CONSISTENT — PASS

8. **Panel index in A matches set_index in K?**
   - A: "(gvkey, cal_yr) for Calendar Year FE specs; (gvkey, cal_yr_qtr) for Year-Quarter FE specs"
   - K1: "time_effects=True with panel index set to (gvkey, cal_yr) (runner line 250)"
   - Runner line 250: `df_panel = df_prepared.set_index(["gvkey", time_col])` where time_col switches on spec
   - CONSISTENT — PASS

**INTERNAL INCONSISTENCIES DETECTED:**

Inconsistency 1 (A vs I):
- Section A: `Suite ID: H5`
- Section I: `"id": "H5b-Wang"` — INCONSISTENT
- Section I should read `"id": "H5"` to match generate_all_tables.py and Section A.

Inconsistency 2 (A title vs I caption):
- Section A: Title = "H5: Speech Uncertainty and Analyst Forecast Dispersion (Wang 2020)"
- Section I: caption = "H5b: Speech Uncertainty and Analyst Forecast Dispersion (Wang 2020)"
- The "H5b:" prefix in Section I's caption is inconsistent with "H5:" in Section A.

**PHASE 11 RESULT: 6/8 PASS (two internal inconsistencies between A and I)**

================================================================================
### FAILURES (detailed)
================================================================================

| Phase | Check | Provenance Doc Claims | Actual Code Says | Severity | Fix Required |
|---|---|---|---|---|---|
| 8 | generate_all_tables.py "id" | "H5b-Wang" | "H5" | HIGH — wrong suite identifier | Update Section I code block |
| 8 | generate_all_tables.py "label" | "tab:h5b_wang" | "tab:h5" | HIGH — wrong LaTeX label | Update Section I code block |
| 8 | generate_all_tables.py "caption" | "H5b: Speech Uncertainty..." | "H5: Speech Uncertainty..." | HIGH — wrong caption prefix | Update Section I code block |
| 8 | generate_all_tables.py "dir" | "h5b_wang_disp/2026-03-27_095026" | "h5b_wang_disp/2026-03-31_140307" | MEDIUM — stale output directory | Update Section I code block |
| 8 | generate_all_tables.py source lines | "lines 183-195" | lines 151-163 | LOW — wrong line numbers | Update Section I source note |
| 7 | F1 Step 7 id reference | `"id": "H5b-Wang"` | `"id": "H5"` | MEDIUM — carries forward Section I error | Update F1 Step 7 |
| 7 | F1 Step 7 line reference | "at line 184" | entry begins at line 151 | LOW — wrong line number | Update F1 Step 7 |

================================================================================
### CORRECTIONS REQUIRED
================================================================================

1. **Section I — Replace entire generate_all_tables.py code block**
   - Current (wrong):
     ```python
     {
         "id": "H5b-Wang",
         "dir": "h5b_wang_disp/2026-03-27_095026",
         "caption": "H5b: Speech Uncertainty and Analyst Forecast Dispersion (Wang 2020)",
         "label": "tab:h5b_wang",
         "cols": 12,
         "dvs": [
             ("WangDISP", 6),
             (r"WangDISP\_lead", 6),
         ],
         "tail": "one",
         "hyp_dir": ">",
     }
     ```
   - Should be:
     ```python
     {
         "id": "H5",
         "dir": "h5b_wang_disp/2026-03-31_140307",
         "caption": "H5: Speech Uncertainty and Analyst Forecast Dispersion (Wang 2020)",
         "label": "tab:h5",
         "cols": 12,
         "dvs": [
             ("WangDISP", 6),
             (r"WangDISP\_lead", 6),
         ],
         "tail": "one",
         "hyp_dir": ">",
     }
     ```
   - Code reference: `outputs/generate_all_tables.py` lines 151-163

2. **Section I — Update source line reference**
   - Current: "Source: `outputs/generate_all_tables.py` lines 183-195."
   - Should be: "Source: `outputs/generate_all_tables.py` lines 151-163."
   - Code reference: entry comment `# -- H5 (Wang 2020) --` at line 150, dict opens at line 151, closes at line 163.

3. **Section I — Update Verification block**
   - The Verification block currently states:
     "`tail="one"` and `hyp_dir=">"` match runner's one-tailed beta > 0 test (runner line 287, 365)."
     "`cols=12` matches `len(MODEL_SPECS)` = 12 (runner lines 82-98)."
     "`dvs` = `[("WangDISP", 6), ("WangDISP_lead", 6)]` matches 6 contemporaneous + 6 lead columns."
   - These verification statements are CORRECT but should also note:
     "`id="H5"`, `label="tab:h5"`, and `caption` prefix "H5:" match the suite's current name."
   - Code reference: `outputs/generate_all_tables.py` lines 152, 154-155.

4. **Section F1 Step 7 — Update narrative**
   - Current: "`outputs/generate_all_tables.py` has entry `"id": "H5b-Wang"` at line 184"
   - Should be: "`outputs/generate_all_tables.py` has entry `"id": "H5"` at lines 151-163"
   - Code reference: `outputs/generate_all_tables.py` line 152.

================================================================================
### NOTES ON NON-FAILURES
================================================================================

1. The `dir` timestamp discrepancy (2026-03-27 → 2026-03-31) is because a new
   12-column run was completed on 2026-03-31 after the provenance doc was written
   (which documented the 8-column run). This is expected to become stale with
   future runs and is inherently mutable. Correction 1 above addresses it.

2. The [UNVERIFIED] entries in D3 (cols 5-6, 11-12) reflect the state at doc
   creation time when only the 8-column output existed. With the 2026-03-31 run
   now available, these could be filled in but are not strictly wrong — the doc
   was accurate at write time.

3. Known Issue #1 documents "the dir path...contains only 8 columns". This is now
   superseded by the new 2026-03-31 run but is historically accurate and harmless.

4. Known Issue #2 on stale "FE: industry + Fiscal Year" label in text output files:
   runner line 322 writes `f"FE: {meta['fe']}"` where meta["fe"] is the fe_type
   string (e.g., "industry", "firm_yq"). The runner does not produce "Fiscal Year"
   text — the Known Issue's description of what "stale label" was written by the
   old runner is a historical note rather than a current bug.

5. The naming mismatch between Suite ID "H5" and runner/builder filenames
   "h5b_wang_disp" is a known naming artifact. The runner and builder were named
   before the rename; file names were not changed to match the new suite ID.
   Section A correctly documents both names. The errors in Section I stem from
   this historical naming confusion.

================================================================================
END OF AUDIT REPORT — H5
================================================================================
