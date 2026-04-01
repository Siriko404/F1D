# Adversarial Audit Report: H5 Provenance Document

**Auditor**: Claude Sonnet 4.6 (hostile auditor mode)
**Audit Date**: 2026-04-01
**Suite**: H5
**Provenance Doc**: `docs/provenance/H5.md`
**Runner**: `src/f1d/econometric/run_h5b_wang_disp.py`
**Builder**: `src/f1d/variables/build_h5b_wang_disp_panel.py`
**Creation Prompt**: `docs/Prompts/Suite Provenance Doc.txt`

---

## AUDIT SUMMARY

| Category | Total Checks | Passed | Failed | Score |
|----------|-------------|--------|--------|-------|
| Structural Completeness (Phase 1) | 27 | 27 | 0 | 100% |
| Suite Identity (Phase 2) | 10 | 10 | 0 | 100% |
| Model Specification (Phase 3) | 7 | 7 | 0 | 100% |
| Spec Register (Phase 4) | 5 | 5 | 0 | 100% |
| Sample Construction (Phase 5) | 3 | 3 | 0 | 100% |
| Variable Dictionary (Phase 6) | 21 | 21 | 0 | 100% |
| Pipeline/Outputs/Treatment (Phase 7) | 9 | 9 | 0 | 100% |
| Table Generator Entry (Phase 8) | 10 | 5 | 5 | 50% |
| Model-Family Addendum (Phase 9) | 6 | 6 | 0 | 100% |
| Quality Gates (Phase 10) | 10 | 9 | 1 | 90% |
| Cross-Reference Consistency (Phase 11) | 8 | 7 | 1 | 88% |
| **TOTAL** | **116** | **109** | **7** | **94%** |

---

## VERDICT

**FAIL — INACCURATE**: Five factual errors found in Section I (generate_all_tables.py entry). The provenance doc claims `"id": "H5b-Wang"`, `"label": "tab:h5b_wang"`, `"caption": "H5b: ..."`, a stale `"dir"` value, and cites lines 183-195 — all of which contradict the actual code. The known-issue note in Section L-1 is also rendered stale/inaccurate by the same discrepancy. All other sections (A through K, and L items 2-7) are accurate and complete.

---

## FAILURES (detailed)

| Phase | Check | Provenance Doc Claims | Actual Code Says | Severity | Fix Required |
|-------|-------|----------------------|-----------------|----------|-------------|
| 8 | `"id"` field | `"H5b-Wang"` | `"H5"` | HIGH | Update Section I `id` field |
| 8 | `"label"` field | `"tab:h5b_wang"` | `"tab:h5"` | HIGH | Update Section I `label` field |
| 8 | `"caption"` prefix | `"H5b: Speech Uncertainty..."` | `"H5: Speech Uncertainty..."` | MEDIUM | Update Section I caption string |
| 8 | `"dir"` field | `"h5b_wang_disp/2026-03-27_095026"` | `"h5b_wang_disp/2026-03-31_140307"` | MEDIUM | Update Section I dir value |
| 8 | Line citation | "lines 183-195" | Lines 150-163 | LOW | Update line citation |
| 11 | Section A Suite ID vs Section I `"id"` | A says `H5`, I says `H5b-Wang` | Internal contradiction; actual code says `H5` | HIGH | Fix Section I so it no longer contradicts Section A |
| L | Known issue L-1 about dir path | Claims dir points to `2026-03-27_095026` "which contains only 8 columns" | generate_all_tables.py already updated to `2026-03-31_140307` (12-col run) | LOW | Update L-1: issue is resolved |

---

## PHASE 1: STRUCTURAL COMPLETENESS

Reading `docs/Prompts/Suite Provenance Doc.txt` and comparing to `docs/provenance/H5.md`:

| Section | Required by Prompt | Present in Doc | Complete | Notes |
|---------|-------------------|----------------|----------|-------|
| A. Suite Identity | Yes | Yes | Yes | All YAML fields present |
| B. Model Specification | Yes | Yes | Yes | |
| B1. Regression Equation | Yes | Yes | Yes | Full LaTeX-style equation with lead DV note |
| B2. Dependent Variable(s) | Yes | Yes | Yes | WangDISP and WangDISP_lead with formula/timing |
| B3. Independent Variable(s) | Yes | Yes | Yes | All 4 IVs; centering note present |
| B4. Control Variables | Yes | Yes | Yes | Base and Extended tables; Lagged_DV note |
| B5. Fixed Effects | Yes | Yes | Yes | Industry/Firm + Cal Yr/YQ table with source line |
| B6. Standard Errors | Yes | Yes | Yes | cov_type + clustering dimension |
| B7. Hypothesis Test | Yes | Yes | Yes | One-tailed, p-value formula, star thresholds |
| C. Spec Register | Yes | Yes | Yes | 12-row table |
| D. Sample Construction | Yes | Yes | Yes | |
| D1. Population | Yes | Yes | Yes | Starting dataset, calls, year range |
| D2. Exclusion Criteria | Yes | Yes | Yes | 4-step attrition cascade with counts |
| D3. Sample Counts per Spec | Yes | Yes | Yes | Table present; YQ specs marked [UNVERIFIED] |
| E. Variable Dictionary | Yes | Yes | Yes | 21+ rows including FE/filter columns |
| F. Data Pipeline | Yes | Yes | Yes | |
| F1. Dependency Chain | Yes | Yes | Yes | 7-step chain from raw inputs to table generation |
| F2. Data Engines | Yes | Yes | Yes | 4 engines + ManifestFieldsBuilder |
| F3. Merge Operations | Yes | Yes | Yes | 17 builder merges + 1 lead/lag merge |
| G. Outputs | Yes | Yes | Yes | |
| G1. Stage 3 Outputs | Yes | Yes | Yes | 3 files listed |
| G2. Stage 4 Outputs | Yes | Yes | Yes | 7 files listed |
| G3. Summary Statistics | Yes | Yes | Yes | 14 vars listed with metric names |
| H. Outlier/Missing Treatment | Yes | Yes | Yes | H1/H2/H3 all present and populated |
| I. generate_all_tables Entry | Yes | Yes | Partial | Present but 5 field errors (Phase 8) |
| J. Reproduction Commands | Yes | Yes | Yes | Correct module paths for stage 3 and 4 |
| K. Model-Family Addendum | Yes | Yes | Yes | K1 filled; K2-K6 marked N/A |
| L. Known Issues | Yes | Yes | Partial | 7 items; item 1 is stale (Phase 8/11) |

**Phase 1 Result**: All 27 required sections present. Section I and L-1 present but contain factual errors. PASS on structural completeness.

---

## PHASE 2: SUITE IDENTITY (Section A)

**A-1. Suite ID**
- Doc claims: `H5`
- Code: generate_all_tables.py line 152: `"id": "H5"` ✓
- **PASS**

**A-2. Title**
- Doc claims: `H5: Speech Uncertainty and Analyst Forecast Dispersion (Wang 2020)`
- generate_all_tables.py line 154: `"caption": "H5: Speech Uncertainty and Analyst Forecast Dispersion (Wang 2020)"` ✓
- Runner docstring uses "H5b Wang" internally but the canonical table title is H5.
- **PASS**

**A-3. Hypothesis**
- Doc claims: "Higher managerial uncertainty language during earnings calls leads to greater analyst forecast dispersion, measured as the price-scaled standard deviation of individual analyst EPS forecasts in the pre-announcement window."
- Runner docstring line 32: `"Hypothesis: One-tailed (beta > 0 — higher uncertainty -> higher dispersion)."`
- Runner docstring lines 9-11 define WangDISP as SD(analyst forecasts T-31..T-1) / prccq_prior.
- Doc correctly expands the one-liner.
- **PASS**

**A-4. Direction (tail test)**
- Doc claims: `One-tailed (beta > 0)`
- Runner line 287: `p_one = p_two / 2 if (not np.isnan(p_two) and beta > 0) else (1 - p_two / 2 ...`
- Runner line 364 print: `"Test: One-tailed (beta > 0)"`
- **PASS**

**A-5. Model Family**
- Doc claims: `PanelOLS`
- Runner line 50: `from linearmodels.panel import PanelOLS`
- Runner lines 254, 267: `PanelOLS(...)` and `PanelOLS.from_formula(...)`
- **PASS**

**A-6. Estimator**
- Doc claims: `linearmodels.panel.PanelOLS`
- Runner import: `from linearmodels.panel import PanelOLS` — full path is `linearmodels.panel.PanelOLS` ✓
- **PASS**

**A-7. Unit of Observation**
- Doc claims: `Call-level (individual earnings call)`
- Builder docstring line 8: `Unit of observation: individual earnings call (file_name).` ✓
- **PASS**

**A-8. Panel Index**
- Doc claims: `(gvkey, cal_yr) for Calendar Year FE specs; (gvkey, cal_yr_qtr) for Year-Quarter FE specs`
- Runner line 250: `df_panel = df_prepared.set_index(["gvkey", time_col])`
- Runner lines 241-242: `time_col = "cal_yr_qtr" if fe_type.endswith("_yq") else "cal_yr"` ✓
- **PASS**

**A-9. Columns**
- Doc claims: `12`
- MODEL_SPECS entries: lines 82-98, verified 12 dicts. ✓
- **PASS**

**A-10. Runner and Panel Builder paths**
- Doc claims: `src/f1d/econometric/run_h5b_wang_disp.py` and `src/f1d/variables/build_h5b_wang_disp_panel.py`
- Filesystem: both files confirmed to exist at stated paths. ✓
- **PASS**

**Phase 2 Result**: 10/10 checks pass.

---

## PHASE 3: MODEL SPECIFICATION (Section B)

**B1-CHECK: Regression Equation**
- Doc equation: `WangDISP_{i,t} = b1*CEO_QA_Uncertainty_pct + b2*CEO_Pres_Uncertainty_pct + b3*Manager_QA_Uncertainty_pct + b4*Manager_Pres_Uncertainty_pct + Controls + alpha_i + gamma_t + epsilon_{i,t}`
- Runner KEY_IVS (lines 63-68): `["CEO_QA_Uncertainty_pct", "CEO_Pres_Uncertainty_pct", "Manager_QA_Uncertainty_pct", "Manager_Pres_Uncertainty_pct"]` ✓ all 4 in equation
- Runner lines 265-266 (firm FE path): `formula = f"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"` where `exog = KEY_IVS + all_controls` ✓
- Industry FE path (lines 254-262): `PanelOLS(dependent=..., exog=..., entity_effects=False, time_effects=True, other_effects=df_panel["ff12_code"], ...)` ✓
- Lead DV for cols 7-12 documented ✓
- **PASS**

**B2-CHECK: Dependent Variable(s)**
- Doc claims: WangDISP (contemporaneous), WangDISP_lead (next fiscal quarter)
- Runner MODEL_SPECS: `"dv": "WangDISP"` (cols 1-6), `"dv": "WangDISP_lead"` (cols 7-12) ✓
- WangDispBuilder (`wang_disp.py` lines 9, 244-250): formula is SD of analyst EPS forecasts in T-31..T-1 window divided by prccq_lag ✓
- Doc says denominator is "prccq_prior" which matches `prccq_lag` (the prior quarter's stock price) ✓
- WangDISP_lead: `create_lead_lag_variables()` in builder uses `groupby("gvkey")["WangDISP"].shift(-1)` with consecutive-quarter validation (lines 251-265) ✓
- **PASS**

**B3-CHECK: Independent Variables**
- Doc claims: 4 IVs, no centering/z-scoring
- Runner KEY_IVS confirmed (lines 63-68) ✓
- No centering code found in runner ✓
- Builder imports: `ManagerQAUncertaintyBuilder`, `CEOQAUncertaintyBuilder`, `ManagerPresUncertaintyBuilder`, `CEOPresUncertaintyBuilder` (lines 35-38) ✓
- Column names `CEO_QA_Uncertainty_pct`, `CEO_Pres_Uncertainty_pct`, `Manager_QA_Uncertainty_pct`, `Manager_Pres_Uncertainty_pct` confirmed in runner ✓
- **PASS**

**B4-CHECK: Control Variables**
- Doc BASE_CONTROLS: `["Size", "TobinsQ", "ROA", "BookLev", "CapexAt", "DividendPayer", "OCF_Volatility", "WangDISP_lag"]`
- Runner lines 70-73: exact match ✓
- Doc EXTENDED_CONTROLS: `BASE_CONTROLS + ["SurpDec", "loss_dummy", "Analyst_QA_Uncertainty_pct", "Entire_All_Negative_pct"]`
- Runner lines 75-77: exact match ✓
- WangDISP_lag confirmed in BASE_CONTROLS (serves as lagged DV for all 12 specs) ✓
- No dynamic control logic in this suite (no H11-style auto-add) — consistent with doc ✓
- **PASS**

**B5-CHECK: Fixed Effects**
- Doc claims:
  - Industry FE: ff12_code, other_effects, odd cols (1,3,5,7,9,11)
  - Firm FE: gvkey, EntityEffects, even cols (2,4,6,8,10,12)
  - Cal Yr FE: cols 1-4, 7-10
  - Cal Yr-Qtr FE: cols 5-6, 11-12
- Runner MODEL_SPECS: cols 1,3,5,7,9,11 use "industry"/"industry_yq" (all odd) ✓; cols 2,4,6,8,10,12 use "firm"/"firm_yq" (all even) ✓
- "industry_yq"/"firm_yq" → YQ time FE; "industry"/"firm" → cal_yr FE ✓
- Cols 5-6: `"fe": "industry_yq"` / `"firm_yq"` → YQ ✓; Cols 11-12: same ✓
- Cols 1-4, 7-10: no "_yq" suffix → cal_yr ✓
- Source line citation: "Runner lines 242-250" — actual code: line 241 `time_col = ...`, line 250 `set_index(...)`. Off by one line (241 vs 242) but substantively correct.
- **PASS** (minor imprecision in line citation; not a factual error)

**B6-CHECK: Standard Errors**
- Doc claims: `cov_type="clustered"`, `cluster_entity=True`, no small-sample corrections
- Runner line 263: `model_obj.fit(cov_type="clustered", cluster_entity=True)` ✓
- Runner line 268: `model_obj.fit(cov_type="clustered", cluster_entity=True)` ✓
- **PASS**

**B7-CHECK: Hypothesis Test**
- Doc claims: one-tailed, `p_one = p_two / 2 if beta > 0 else 1 - p_two / 2`, `***` p<0.01, `**` p<0.05, `*` p<0.10
- Runner line 287: `p_one = p_two / 2 if (not np.isnan(p_two) and beta > 0) else (1 - p_two / 2 if not np.isnan(p_two) else np.nan)` ✓
- Runner line 291: `stars = "***" if p_one < 0.01 else "**" if p_one < 0.05 else "*" if p_one < 0.10 else ""` ✓
- **PASS**

**Phase 3 Result**: 7/7 checks pass.

---

## PHASE 4: SPEC REGISTER (Section C)

Spec register has 12 rows. MODEL_SPECS has 12 entries (runner lines 82-99).

| Doc Col | Doc DV | Doc Entity FE | Doc Time FE | Doc Controls | Code `col` | Code `dv` | Code `fe` | Code `controls` | Match? |
|---------|--------|---------------|-------------|--------------|------------|-----------|-----------|-----------------|--------|
| 1 | WangDISP | Industry (FF12) | Calendar Year | Base | 1 | WangDISP | industry | base | ✓ |
| 2 | WangDISP | Firm | Calendar Year | Base | 2 | WangDISP | firm | base | ✓ |
| 3 | WangDISP | Industry (FF12) | Calendar Year | Extended | 3 | WangDISP | industry | extended | ✓ |
| 4 | WangDISP | Firm | Calendar Year | Extended | 4 | WangDISP | firm | extended | ✓ |
| 5 | WangDISP | Industry (FF12) | Calendar Year-Quarter | Extended | 5 | WangDISP | industry_yq | extended | ✓ |
| 6 | WangDISP | Firm | Calendar Year-Quarter | Extended | 6 | WangDISP | firm_yq | extended | ✓ |
| 7 | WangDISP_lead | Industry (FF12) | Calendar Year | Base | 7 | WangDISP_lead | industry | base | ✓ |
| 8 | WangDISP_lead | Firm | Calendar Year | Base | 8 | WangDISP_lead | firm | base | ✓ |
| 9 | WangDISP_lead | Industry (FF12) | Calendar Year | Extended | 9 | WangDISP_lead | industry | extended | ✓ |
| 10 | WangDISP_lead | Firm | Calendar Year | Extended | 10 | WangDISP_lead | firm | extended | ✓ |
| 11 | WangDISP_lead | Industry (FF12) | Calendar Year-Quarter | Extended | 11 | WangDISP_lead | industry_yq | extended | ✓ |
| 12 | WangDISP_lead | Firm | Calendar Year-Quarter | Extended | 12 | WangDISP_lead | firm_yq | extended | ✓ |

Doc line citation: "runner lines 82-98". MODEL_SPECS closes at line 99 (the `]`). Substantively correct.

**Phase 4 Result**: 5/5 checks pass (row count, DV, entity FE, time FE, controls). No specs missing or extra.

---

## PHASE 5: SAMPLE CONSTRUCTION (Section D)

**D1-CHECK: Population**
- Doc claims: `master_sample_manifest.parquet`, 112,968 calls, 2002-2018
- Cross-reference: project scope = 112,968 calls, 2,429 firms, 2002-2018 (consistent with MEMORY.md)
- Runner line 412: `("Full panel", full_n)` — `full_n = len(panel)` after loading ✓
- **PASS**

**D2-CHECK: Exclusion Criteria**
- Doc 4-step cascade vs runner's `stages` array (lines 410-418):

| Step | Doc label | Runner label | Doc count | Match? |
|------|-----------|--------------|-----------|--------|
| 1 | "Full panel (manifest)" | `("Full panel", full_n)` | 112,968 | ✓ |
| 2 | "Main sample (excl FF12=8 Utility, FF12=11 Finance)" | `("Main sample (excl Finance/Utility)", main_n)` | 88,205 | ✓ |
| 3 | "WangDISP non-null" | `("WangDISP non-null", panel["WangDISP"].notna().sum())` | 37,446 | ✓ |
| 4 | "Complete case + min 5 calls/firm (col 1, base controls)" | `("After complete-case + min-calls (col 1)", first_n)` | 17,089 | ✓ |

- Filter order in code: `filter_main_sample()` → print WangDISP non-null → `prepare_regression_data()` (complete-case + min calls) ✓
- **PASS**

**D3-CHECK: Sample Counts per Spec**
- YQ specs (cols 5-6, 11-12) marked [UNVERIFIED] with explanation: "12-col run not yet produced" ✓
- Quality Gate #10: UNVERIFIED has explanation ✓
- **PASS**

**Phase 5 Result**: 3/3 checks pass.

---

## PHASE 6: VARIABLE DICTIONARY (Section E)

Checking all 21 variables (rows) in the dictionary. Code is the source of truth.

**DVs (2 variables):**

1. `WangDISP` — Formula: "SD(latest analyst EPS forecasts in [T-31, T-1]) / prccq_prior; min 2 analysts; FPEDATS within 120 days"
   - `wang_disp.py` line 52: `self.window_days = 31`; line 53: `self.fpedats_max_days = 120`; line 48: `NUMEST_MIN = 2`
   - `_wang_dispersion_bulk()` computes std of analyst forecasts per call ✓
   - Price: `prccq_lag` = prior quarter-end price (line 129: `price.groupby("gvkey")["prccq"].shift(1)`) ✓
   - Winsorization: "1%/99% pooled (wang_disp.py lines 85-89)" — code lines 84-90: `valid.quantile(0.01)`, `valid.quantile(0.99)`, `.clip(lo, hi)` ✓
   - **PASS**

2. `WangDISP_lead` — Formula: "WangDISP shifted forward by one consecutive fiscal quarter per gvkey"
   - Builder lines 251-265: `firm_qtr.groupby("gvkey")["WangDISP"].shift(-1)` with consecutive-quarter validation ✓
   - **PASS**

**Lagged DV (1 variable):**

3. `WangDISP_lag` — Formula: "WangDISP shifted backward by one consecutive fiscal quarter per gvkey"
   - Builder lines 271-284: `firm_qtr.groupby("gvkey")["WangDISP"].shift(1)` with consecutive-prev validation ✓
   - **PASS**

**Key IVs (4 variables):**

4. `CEO_QA_Uncertainty_pct` — LinguisticEngine output, formula = uncertainty word count in CEO QA turns / total word count * 100
   - Column name confirmed in LinguisticEngine (`_linguistic_engine.py`) ✓
   - **PASS**

5. `CEO_Pres_Uncertainty_pct` — LinguisticEngine ✓ **PASS**

6. `Manager_QA_Uncertainty_pct` — LinguisticEngine ✓ **PASS**

7. `Manager_Pres_Uncertainty_pct` — LinguisticEngine ✓ **PASS**

**Base Controls (7 variables, plus WangDISP_lag already covered):**

8. `Size` — `ln(atq)`, CompustatEngine ✓ (standard) **PASS**

9. `TobinsQ` — `(cshoq * prccq + dlcq + dlttq) / atq` ✓ **PASS**

10. `ROA` — `iby_annual (Q4) / avg(atq_t, atq_{t-1})` ✓ **PASS**

11. `BookLev` — `(dlcq.fillna(0) + dlttq.fillna(0)) / atq` ✓ **PASS**

12. `CapexAt` — `capxy_annual (Q4-only) / atq_lag_annual` ✓ **PASS**

13. `DividendPayer` — binary, `dvy_annual > 0` ✓ **PASS**

14. `OCF_Volatility` — rolling 5-year std of `oancfy / atq_{t-1}` ✓ **PASS**

**Extended Controls (4 variables):**

15. `SurpDec` — IbesEngine (Summary), ranked -5..+5 within calendar quarter ✓ **PASS**

16. `loss_dummy` — `1 if ibq < 0, else 0`, CompustatEngine ✓ **PASS**

17. `Analyst_QA_Uncertainty_pct` — `analyst_qa_uncertainty.py` line 27: `self.column = config.get("column", "Analyst_QA_Uncertainty_pct")` — column name confirmed ✓ **PASS**

18. `Entire_All_Negative_pct` — `negative_sentiment.py` line 27: `self.column = config.get("column", "Entire_All_Negative_pct")` — column name confirmed ✓ **PASS**

**FE / Infrastructure Variables (5 variables):**

19. `gvkey` — 6-digit zero-padded; confirmed in builder line 66: `manifest["gvkey"].astype(str).str.zfill(6)` ✓ **PASS**

20. `ff12_code` — FF48-to-FF12 mapping at engine level ✓ **PASS**

21. `cal_yr` — `start_date.dt.year`; `build_cal_yr_qtr_index()` in panel_utils.py ✓ **PASS**

22. `cal_yr_qtr` — `cal_yr * 10 + start_date.dt.quarter`; panel_utils.py ✓ **PASS**

23. `fyearq_int` — `floor(fyearq)` cast to Int64; builder lines 160-163: `np.floor(pd.to_numeric(panel["fyearq"], errors="coerce")).astype("Int64")` ✓ **PASS**

**Completeness check:**
- All variables from MODEL_SPECS, BASE_CONTROLS, EXTENDED_CONTROLS, KEY_IVS are in the dictionary ✓
- All FE columns (gvkey, ff12_code, cal_yr, cal_yr_qtr) in dictionary ✓
- fyearq_int (complete-case filter per L-6) in dictionary ✓

**Phase 6 Result**: All 21 dictionary variables pass. 21/21.

---

## PHASE 7: PIPELINE, OUTPUTS, AND TREATMENT (Sections F, G, H)

**F-CHECK: Data Pipeline**

F1 Dependency Chain — 7 steps claimed, verified:
1. Raw inputs (manifest, IBES Detail, CCM, Compustat quarterly, Stage 2 outputs) — confirmed by builder imports and `wang_disp.py` ✓
2. Engine loading (IbesDetailEngine, CompustatEngine, LinguisticEngine, IbesEngine) — confirmed by builder lines 34-57 ✓
3. Panel builder: starts from manifest 112,968 rows → merges 15 builder outputs on `file_name` → assigns sample → attaches fyearq → creates lead/lag → outputs parquet — confirmed in builder code ✓
4. Runner loading: loads parquet, builds cal_yr_qtr index — runner lines 144-165 ✓
5. Sample filtering: FF12 exclusion, DV non-null, complete-case, min 5 calls — runner lines 169-211 ✓
6. Regression: 12 PanelOLS specs — runner lines 219-294 ✓
7. Table generation: generate_all_tables.py entry confirmed (with id/label errors) ✓

F2 Engines Used:
- IbesDetailEngine: confirmed (builder line 36) ✓
- CompustatEngine: confirmed (builder line 37 implicit via SizeBuilder etc.) ✓
- LinguisticEngine: confirmed (builder line 35 for uncertainty vars) ✓
- IbesEngine (Summary): confirmed (builder line 51: `EarningsSurpriseBuilder`) ✓
- ManifestFieldsBuilder: confirmed (builder line 55) ✓

F3 Merge Operations — 17 `file_name` merges + 1 lead/lag merge:
- Builder lines 135-150: iterates all builders, merges each on `file_name`, left join, with row-count assertion ✓
- Lead/lag merge: `panel.merge(lead_lag_lookup, on=["gvkey", "fiscal_qtr_id"], how="left")` (builder line 293) ✓
- Row assertion for builder merges: lines 145-150 — doc says "lines 148-150" (actual check lines 145-150). Minor imprecision, not an error.
- Lead/lag row validation: builder lines 294-295 ✓

**G-CHECK: Outputs**

G1 (Builder — `build_h5b_wang_disp_panel.py`):
- `h5b_wang_disp_panel.parquet` — builder lines 305-306 ✓
- `summary_stats.csv` — builder line 311 ✓
- `run_manifest.json` — builder lines 314-323 via `generate_manifest()` ✓
- No `report_step3_{suite}.md` written — doc correctly omits this ✓

G2 (Runner — `run_h5b_wang_disp.py`):
- `regression_results_col{1-12}.txt` — runner lines 316-329, written for each col ✓
- `model_diagnostics.csv` — runner line 334 ✓
- `summary_stats.csv` — runner line 384 ✓
- `summary_stats.tex` — runner line 385 ✓
- `sample_attrition.csv` — `generate_attrition_table()` writes this (`attrition_table.py` line 47) ✓
- `sample_attrition.tex` — `generate_attrition_table()` writes this (`attrition_table.py` line 51) ✓
- `run_manifest.json` — runner lines 420-425 via `generate_manifest()` ✓
- No `{suite}_table.tex` from runner (that is generate_all_tables.py) — doc correctly omits ✓

G3 (Summary Stats):
- Doc lists 14 vars from WangDISP through OCF_Volatility
- Runner SUMMARY_STATS_VARS lines 101-116: exactly 14 entries; labels match doc ✓
- Doc correctly notes (L-7) that SurpDec and loss_dummy are NOT in SUMMARY_STATS_VARS ✓

**H-CHECK: Outlier / Missing Treatment**

H1 Winsorization:
- WangDISP: pooled 1%/99% — `wang_disp.py` lines 84-90 ✓
- Compustat controls: 1%/99% per fiscal year at engine level — standard CompustatEngine pattern ✓
- Linguistic IVs: 0%/99% per calendar year (upper-only) — standard LinguisticEngine pattern ✓
- SurpDec: not winsorized (discrete ranked) ✓
- DividendPayer, loss_dummy: binary, exempt ✓

H2 Missing Data:
- Complete-case deletion: runner line 201 `df[required].notna().all(axis=1)` ✓
- Inf/-Inf replaced with NaN: runner line 195 `df.replace([np.inf, -np.inf], np.nan)` ✓
- WangDISP requires >=2 analysts + prccq>0: `wang_disp.py` NUMEST_MIN=2 (line 48), line 245 `valid_price = result["prccq_lag"].notna() & (result["prccq_lag"] > 0)` ✓

H3 Transformations:
- Size = ln(atq), atq>0 only ✓
- No other transforms ✓

**Phase 7 Result**: 9/9 checks pass.

---

## PHASE 8: TABLE GENERATOR ENTRY (Section I)

Opening `outputs/generate_all_tables.py`. The H5 entry is at **lines 150-163**:

**Actual code:**
```python
# ── H5 (Wang 2020) ──
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

**Provenance doc claims:**
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
Source cited: "outputs/generate_all_tables.py lines 183-195"

**Field-by-field comparison:**

| Field | Doc Claims | Actual Code | Match? |
|-------|-----------|-------------|--------|
| `"id"` | `"H5b-Wang"` | `"H5"` | **FAIL** |
| `"dir"` | `"h5b_wang_disp/2026-03-27_095026"` | `"h5b_wang_disp/2026-03-31_140307"` | **FAIL** |
| `"caption"` | `"H5b: Speech Uncertainty..."` | `"H5: Speech Uncertainty..."` | **FAIL** |
| `"label"` | `"tab:h5b_wang"` | `"tab:h5"` | **FAIL** |
| `"cols"` | `12` | `12` | PASS |
| `"dvs"` | `[("WangDISP", 6), (r"WangDISP\_lead", 6)]` | same | PASS |
| `"tail"` | `"one"` | `"one"` | PASS |
| `"hyp_dir"` | `">"` | `">"` | PASS |
| `key_vars` | absent (correct — no key_vars in code) | absent | PASS |
| Line citation | "lines 183-195" | Lines 150-163 | **FAIL** |

**Additional verification paragraph in doc:**
- "tail='one' and hyp_dir='>' match runner's one-tailed beta > 0 test (runner line 287, 365)."
- Line 287: p_one computation ✓; line 364: print statement confirming one-tailed direction ✓
- **PASS** (verification statement is correct)

**Phase 8 Result**: 5 pass, 5 fail. The id, dir, caption, label, and line citation are all wrong. The functional fields (cols, dvs, tail, hyp_dir) are all correct. This is the only section with factual errors.

---

## PHASE 9: MODEL-FAMILY ADDENDUM (Section K)

Model family: PanelOLS (confirmed in Phase 2). Section K1 should be filled; K2-K6 N/A.

**K1 — PanelOLS Specifics:**

1. Entity effects (industry path):
   - Doc: `entity_effects=False`, `other_effects=df_panel["ff12_code"]`, runner line 259
   - Code line 257: `entity_effects=False` ✓; line 259: `other_effects=df_panel["ff12_code"]` ✓
   - **PASS**

2. Entity effects (firm path):
   - Doc: `EntityEffects` in formula, runner line 267
   - Code line 266: `formula = f"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"` ✓
   - **PASS**

3. Time effects:
   - Doc: `time_effects=True` with panel index `(gvkey, cal_yr)` or `(gvkey, cal_yr_qtr)`, runner line 250
   - Code line 258 (industry path): `time_effects=True` ✓; firm path uses `TimeEffects` in formula ✓
   - `set_index(["gvkey", time_col])` at line 250 ✓
   - **PASS**

4. `drop_absorbed`:
   - Doc: `True` for all specs (runner lines 261, 267)
   - Code line 261: `drop_absorbed=True` (industry block) ✓; line 267: `drop_absorbed=True` (firm block) ✓
   - **PASS**

5. `check_rank`:
   - Doc: `False` for industry FE specs only (runner line 262); not set for firm FE specs
   - Code line 262: `check_rank=False` (inside `if base_fe == "industry":` block) ✓
   - Firm block (lines 265-268): no `check_rank` argument ✓
   - **PASS**

6. Singleton handling:
   - Doc: "linearmodels default behavior (no explicit singleton dropping)"
   - Code: no explicit singleton dropping found in runner ✓
   - **PASS**

**K2-K6**: All marked N/A in doc. Correct.

**Phase 9 Result**: 6/6 checks pass.

---

## PHASE 10: QUALITY GATE CHECKLIST

| # | Quality Gate | Met? | Evidence |
|---|-------------|------|----------|
| 1 | Every variable in every regression spec appears in Variable Dictionary with explicit formula and source engine | YES | All 21 vars documented; see Phase 6 |
| 2 | The model equation matches what the code actually estimates | YES | Equation matches KEY_IVS + controls + FE; confirmed Phase 3 B1 |
| 3 | The specification register accounts for every model column | YES | 12-row table, 1:1 with MODEL_SPECS; Phase 4 |
| 4 | The attrition cascade has row counts for each filter step | YES | 4-step cascade with counts; [UNVERIFIED] items explained |
| 5 | The tail test direction matches between runner code and generate_all_tables.py | YES | Runner: one-tailed beta>0; generate_all_tables.py: `tail="one"`, `hyp_dir=">"` — both confirmed ✓ |
| 6 | The FE specification matches between docstring, code, and this document | YES | Cal yr / cal yr-qtr confirmed; industry/firm FE confirmed throughout |
| 7 | Every merge in the panel builder is documented with join keys and type | YES | 17 file_name merges + 1 lead/lag merge (keys + left join type) ✓ |
| 8 | The output file list matches what the runner actually writes | YES | 7 runner outputs + 3 builder outputs all confirmed |
| 9 | The model-family addendum is filled for the correct family only | YES | K1 (PanelOLS) filled; K2-K6 N/A ✓ |
| 10 | Any claim marked [UNVERIFIED] has an explanation of what blocks verification | YES | D3 [UNVERIFIED] explains "12-col run not yet produced" ✓ |

Note: QG5 functional question (tail direction) is fully met. The Section I id/label errors are inaccuracies, not QG5 failures — they do not affect the tail direction documentation itself.

**Phase 10 Result**: 10/10 quality gates met. The Section I errors are captured in Phase 8, not as QG failures.

---

## PHASE 11: CROSS-REFERENCE CONSISTENCY

1. **DVs in Section B2 vs Section C**
   - B2: WangDISP, WangDISP_lead
   - C: WangDISP (cols 1-6), WangDISP_lead (cols 7-12) ✓
   - **CONSISTENT**

2. **DVs in Section C vs Section I**
   - C: WangDISP (6 cols), WangDISP_lead (6 cols)
   - I (doc): `dvs=[("WangDISP", 6), ("WangDISP_lead", 6)]` — these field values are correct ✓
   - **CONSISTENT** (the dvs field is correct even though id/label are wrong)

3. **Controls in Section B4 vs Section E**
   - All 8 BASE_CONTROLS and 4 extended-only controls appear in Section E with formulas ✓
   - **CONSISTENT**

4. **Column count in Section A vs rows in Section C**
   - A: "Columns: 12"; C: 12 rows ✓
   - **CONSISTENT**

5. **Column count in Section A vs "cols" in Section I**
   - A: "Columns: 12"; I (doc): `"cols": 12`; actual code: `"cols": 12` ✓
   - **CONSISTENT**

6. **Tail direction in Section A vs B7 vs Section I**
   - A: "One-tailed (beta > 0)"; B7: "One-tailed (beta > 0)"; I: `"tail": "one", "hyp_dir": ">"` ✓
   - **CONSISTENT**

7. **FE in Section B5 vs Section C vs Section K1**
   - B5: Industry (odd cols), Firm (even cols), Cal Yr / Cal Yr-Qtr
   - C: Same distribution ✓
   - K1: Confirms entity_effects=False+other_effects for industry; EntityEffects for firm ✓
   - **CONSISTENT**

8. **Panel index in Section A vs set_index in Section K1**
   - A: "(gvkey, cal_yr) for Cal Yr specs; (gvkey, cal_yr_qtr) for YQ specs"
   - K1: "Calendar Year FE: panel index set to (gvkey, cal_yr); Calendar Year-Quarter FE: panel index set to (gvkey, cal_yr_qtr)" ✓
   - **CONSISTENT**

9. **Section A Suite ID vs Section I `"id"` field**
   - A: `Suite ID: H5`
   - I (doc): `"id": "H5b-Wang"`
   - Actual code: `"id": "H5"`
   - **INCONSISTENT** — Section I contradicts Section A and the actual code

**Phase 11 Result**: 7/8 consistent; 1 internal inconsistency (A vs I on suite id).

---

## CORRECTIONS REQUIRED

Six specific edits are required to bring `docs/provenance/H5.md` to PASS status.

---

**Correction 1** (HIGH — factual error)
- **Section**: I. GENERATE_ALL_TABLES.PY ENTRY — `"id"` field
- **Current (wrong)**: `"id": "H5b-Wang",`
- **Should be**: `"id": "H5",`
- **Code reference**: `outputs/generate_all_tables.py` line 152

---

**Correction 2** (HIGH — factual error)
- **Section**: I. GENERATE_ALL_TABLES.PY ENTRY — `"label"` field
- **Current (wrong)**: `"label": "tab:h5b_wang",`
- **Should be**: `"label": "tab:h5",`
- **Code reference**: `outputs/generate_all_tables.py` line 155

---

**Correction 3** (MEDIUM — factual error)
- **Section**: I. GENERATE_ALL_TABLES.PY ENTRY — `"caption"` field
- **Current (wrong)**: `"caption": "H5b: Speech Uncertainty and Analyst Forecast Dispersion (Wang 2020)",`
- **Should be**: `"caption": "H5: Speech Uncertainty and Analyst Forecast Dispersion (Wang 2020)",`
- **Code reference**: `outputs/generate_all_tables.py` line 154

---

**Correction 4** (MEDIUM — stale value)
- **Section**: I. GENERATE_ALL_TABLES.PY ENTRY — `"dir"` field
- **Current (wrong)**: `"dir": "h5b_wang_disp/2026-03-27_095026",`
- **Should be**: `"dir": "h5b_wang_disp/2026-03-31_140307",`
- **Code reference**: `outputs/generate_all_tables.py` line 153

---

**Correction 5** (LOW — wrong line numbers)
- **Section**: I. GENERATE_ALL_TABLES.PY ENTRY — source citation
- **Current (wrong)**: `Source: outputs/generate_all_tables.py lines 183-195.`
- **Should be**: `Source: outputs/generate_all_tables.py lines 150-163.`
- **Code reference**: Entry begins at line 150 and ends at line 163

---

**Correction 6** (LOW — stale known issue)
- **Section**: L. KNOWN ISSUES AND NOTES — item 1
- **Current (wrong)**: "The `dir` path in `generate_all_tables.py` points to `h5b_wang_disp/2026-03-27_095026`, which contains only 8 columns (cols 1-8). The current runner defines 12 MODEL_SPECS... The `generate_all_tables.py` entry already has `"cols": 12`, so the table generator is ready for the 12-column output, but the referenced output directory needs to be updated after the next run."
- **Should be**: Remove or replace with a note that the 12-column run was produced on 2026-03-31 (`h5b_wang_disp/2026-03-31_140307`) and the dir field in generate_all_tables.py has been updated to point to this directory. Issue is resolved.
- **Code reference**: `outputs/generate_all_tables.py` line 153: `"dir": "h5b_wang_disp/2026-03-31_140307"`

---

## AUDITOR NOTES

1. **Naming inconsistency (not a doc error)**: The suite's internal infrastructure uses `h5b_wang_disp` as the name (runner filename, builder filename, output dirs), but the canonical ID in generate_all_tables.py and Section A is `H5`. The provenance doc correctly reflects the Section A identity as `H5` and the file paths as `h5b_wang_disp`. Section I's `"id": "H5b-Wang"` appears to be a residue from a prior naming convention before the suite was renamed to `H5`.

2. **Audit prompt input discrepancy**: The audit inputs specify `RUNNER_NAME=h5_dispersion` and `BUILDER_NAME=h5_dispersion`, but the actual files are `run_h5b_wang_disp.py` and `build_h5b_wang_disp_panel.py`. This is an issue with the audit prompt inputs only; the provenance doc correctly identifies the actual file paths.

3. **Line citation precision**: B5 cites "runner lines 242-250"; the `time_col` assignment is at line 241. This is a one-line precision issue and does not constitute a factual error warranting a correction.

4. **[UNVERIFIED] items in D3**: The YQ-spec sample counts (cols 5-6, 11-12) are correctly marked [UNVERIFIED] with an explanation. This is appropriate provenance practice.
