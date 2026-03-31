# AUDIT REPORT: H11-Lead Provenance Document

**Audit Date:** 2026-03-30
**Auditor:** Adversarial audit per `docs/Prompts/Audit Provenance doc.txt`
**Provenance Doc:** `docs/provenance/H11-Lead.md`
**Runner:** `src/f1d/econometric/run_h11_prisk_uncertainty_lead.py`
**Panel Builder:** `src/f1d/variables/build_h11_prisk_uncertainty_lead_panel.py`

---

## AUDIT SUMMARY

| Category | Total Checks | Passed | Failed | Score |
|----------|-------------|--------|--------|-------|
| Structural Completeness (Phase 1) | 25 | 25 | 0 | 100% |
| Suite Identity (Phase 2) | 10 | 10 | 0 | 100% |
| Model Specification (Phase 3) | 7 | 7 | 0 | 100% |
| Spec Register (Phase 4) | 4 | 4 | 0 | 100% |
| Sample Construction (Phase 5) | 3 | 3 | 0 | 100% |
| Variable Dictionary (Phase 6) | 18 | 16 | 2 | 89% |
| Pipeline/Outputs/Treatment (Phase 7) | 8 | 5 | 3 | 63% |
| Table Generator Entry (Phase 8) | 5 | 4 | 1 | 80% |
| Model-Family Addendum (Phase 9) | 3 | 3 | 0 | 100% |
| Quality Gates (Phase 10) | 10 | 9 | 1 | 90% |
| Cross-Reference Consistency (Phase 11) | 8 | 8 | 0 | 100% |
| **TOTAL** | **101** | **94** | **7** | **93%** |

---

## VERDICT

**PASS WITH NOTES**: The provenance document is substantially accurate and complete. Seven issues were found, none of which affect the core model specification, hypothesis test, or regression results. All failures are documentation-level inaccuracies (wrong winsorization grouping variable description, incorrect output file count claim, inaccurate known issue, and minor line reference errors). The document is safe to use for thesis committee review and replication, contingent on applying the corrections below.

---

## PHASE 1: STRUCTURAL COMPLETENESS

Checked the creation prompt (`docs/Prompts/Suite Provenance Doc.txt`) against the provenance document (`docs/provenance/H11-Lead.md`).

| Section | Required by Prompt | Present in Doc | Complete | Notes |
|---------|-------------------|----------------|----------|-------|
| A. Suite Identity | Yes | Yes | Yes | YAML block with all required fields |
| B. Model Specification | Yes | Yes | Yes | All B subsections present |
| B1. Regression Equation | Yes | Yes | Yes | LaTeX equation + formula string |
| B2. Dependent Variable(s) | Yes | Yes | Yes | 4 DVs documented |
| B3. Independent Variable(s) | Yes | Yes | Yes | 2 IVs with lead construction logic |
| B4. Control Variables | Yes | Yes | Yes | Base controls + dynamic Pres control map |
| B5. Fixed Effects | Yes | Yes | Yes | Entity + Time FE documented |
| B6. Standard Errors | Yes | Yes | Yes | Clustered at firm level |
| B7. Hypothesis Test | Yes | Yes | Yes | Two-tailed, p_test = p_two |
| C. Spec Register | Yes | Yes | Yes | 8-column table |
| D. Sample Construction | Yes | Yes | Yes | D1, D2, D3 all present |
| D1. Population | Yes | Yes | Yes | Manifest + year range |
| D2. Exclusion Criteria | Yes | Yes | Yes | 3-step attrition cascade |
| D3. Sample Counts per Spec | Yes | Yes | Yes | Per-column N and N(firms) |
| E. Variable Dictionary | Yes | Yes | Yes | 17 variables documented |
| F. Data Pipeline | Yes | Yes | Yes | F1, F2, F3 all present |
| F1. Dependency Chain | Yes | Yes | Yes | 7-step chain |
| F2. Data Engines | Yes | Yes | Yes | 4 engines documented |
| F3. Merge Operations | Yes | Yes | Yes | 16 panel merges + 2 PRisk builder merges |
| G. Outputs | Yes | Yes | Yes | G1, G2, G3 all present |
| G1. Stage 3 Outputs | Yes | Yes | Yes | 4 files listed |
| G2. Stage 4 Outputs | Yes | Yes | Yes | Output file list provided |
| G3. Summary Statistics | Yes | Yes | Yes | 15 variables + metrics listed |
| H. Outlier/Missing Treatment | Yes | Yes | Yes | H1, H2, H3 all present |
| I. generate_all_tables Entry | Yes | Yes | Yes | Full entry with verification table |
| J. Reproduction Commands | Yes | Yes | Yes | 3 commands listed |
| K. Model-Family Addendum | Yes | Yes | Yes | K1 filled, K2-K6 marked N/A |
| L. Known Issues | Yes | Yes | Yes | 8 issues documented |

**Phase 1 Result:** 25/25 PASS. All required sections present and populated.

---

## PHASE 2: FACTUAL ACCURACY -- SECTION A (Suite Identity)

**A-1. Suite ID: `H11-Lead`**
- Verified: Matches the runner's docstring (line 6: `ID: econometric/test_h11_prisk_uncertainty_lead`) and generate_all_tables.py (line 249: `"id": "H11-Lead"`).
- **PASS**

**A-2. Title: `H11-Lead: Lead Political Risk and Language Uncertainty (Placebo)`**
- Runner docstring line 4: "STAGE 4: Test H11-Lead Political Risk (Lead) - Language Uncertainty Hypothesis"
- generate_all_tables.py line 252: `"caption": "H11-Lead: Lead Political Risk and Language Uncertainty (Placebo)"`
- Doc title matches the generate_all_tables caption. The runner docstring title is slightly different but the caption is the authoritative table title.
- **PASS**

**A-3. Hypothesis**
- Doc claims: "Future political risk (1- and 2-quarter leads) should NOT predict current earnings-call language uncertainty."
- Runner docstring lines 32-37: "H11-Lead: beta(PRiskQ_lead) = 0 -- future political risk should NOT predict current speech uncertainty"
- Match confirmed.
- **PASS**

**A-4. Direction: Two-tailed (beta = 0)**
- Runner line 223: `p_test = p_two` -- uses two-tailed p-value directly, no halving.
- generate_all_tables.py line 275: `"key_tails": ["two", "two"]`
- **PASS**

**A-5. Model Family: Linear panel regression with absorbed fixed effects**
- Runner line 78: `from linearmodels.panel import PanelOLS`
- Runner line 206: `PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)`
- **PASS**

**A-6. Estimator: `linearmodels.panel.PanelOLS`**
- Runner line 78: `from linearmodels.panel import PanelOLS`
- **PASS**

**A-7. Unit of Observation: Individual earnings call (file_name)**
- Builder docstring line 16: "Unit of observation: the individual earnings call (file_name)."
- Builder merges on `file_name` (line 148).
- **PASS**

**A-8. Panel Index: `(gvkey, year)` -- calendar year derived from start_date**
- Runner line 203: `df_panel = df_sample.set_index(["gvkey", "year"])`
- Builder line 156: `panel["year"] = pd.to_datetime(panel["start_date"], errors="coerce").dt.year`
- **PASS**

**A-9. Columns: 8**
- The runner iterates over 2 IVs x 4 DVs x 3 samples = 24 total regressions, but only the Main sample (2 x 4 = 8) appears in the table.
- generate_all_tables.py line 254: `"cols": 8`
- col_files dict has 8 entries (lines 255-263).
- **PASS**

**A-10. Runner and Panel Builder paths**
- `src/f1d/econometric/run_h11_prisk_uncertainty_lead.py` -- EXISTS (read in full)
- `src/f1d/variables/build_h11_prisk_uncertainty_lead_panel.py` -- EXISTS (read in full)
- **PASS**

**Phase 2 Result:** 10/10 PASS.

---

## PHASE 3: FACTUAL ACCURACY -- SECTION B (Model Specification)

**B1-CHECK: Regression Equation**
- Doc claims: `{dv_var} ~ 1 + {iv_var} + {controls} + EntityEffects + TimeEffects`
- Runner lines 187-190:
  ```python
  formula = (
      f"{dv_var} ~ 1 + {iv_var} + "
      + " + ".join(controls)
      + " + EntityEffects + TimeEffects"
  )
  ```
- Exact match.
- **PASS**

**B2-CHECK: Dependent Variables**
- Doc lists 4 DVs: `Manager_QA_Uncertainty_pct`, `CEO_QA_Uncertainty_pct`, `Manager_Pres_Uncertainty_pct`, `CEO_Pres_Uncertainty_pct`
- Runner CONFIG lines 93-98 lists the same 4 DVs in the same order.
- All 4 appear as the LHS of the formula via `{dv_var}`.
- Timing: contemporaneous (call-level) -- correct, these are measured at the call.
- Source: LinguisticEngine -- confirmed, these are `_pct` columns from linguistic variables.
- No DVs are missing from the doc.
- **PASS**

**B3-CHECK: Independent Variables**
- Doc lists 2 IVs: `PRiskQ_lead` (t+1) and `PRiskQ_lead2` (t+2)
- Runner CONFIG line 100: `"iv_vars": ["PRiskQ_lead", "PRiskQ_lead2"]`
- Both appear as the first RHS term in the formula via `{iv_var}`.
- Source engine: PRiskQLeadBuilder and PRiskQLead2Builder -- confirmed from builder imports (lines 61-62).
- Lead construction logic documented with `_get_next_quarter` and `_get_next2_quarter` -- verified against `prisk_q_lead.py` lines 69-82 and `prisk_q_lead2.py` lines 69-85.
- No IVs are missing.
- **PASS**

**B4-CHECK: Control Variables**
- Doc lists BASE_CONTROLS: `Analyst_QA_Uncertainty_pct`, `Entire_All_Negative_pct`, `Size`, `TobinsQ`, `ROA`, `CashHoldings`, `DividendPayer`, `firm_maturity`, `earnings_volatility`
- Runner lines 103-113 lists exactly these 9 controls in the same order.
- Dynamic Presentation Control (PRES_CONTROL_MAP) documented correctly:
  - Runner lines 115-120 matches the doc's table exactly.
  - QA DVs get corresponding Pres control; Pres DVs get None.
- "No Lagged_DV" documented -- confirmed: no `Lagged_DV` appears in `BASE_CONTROLS` or anywhere in the runner.
- **PASS**

**B5-CHECK: Fixed Effects**
- Doc claims: Entity FE via `gvkey` (EntityEffects) and Time FE via `year` (TimeEffects, calendar year)
- Runner line 203: `df_panel = df_sample.set_index(["gvkey", "year"])`
- Runner line 206: `PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)` with `EntityEffects + TimeEffects` in formula.
- Builder line 156: `panel["year"] = pd.to_datetime(panel["start_date"], errors="coerce").dt.year`
- Calendar year derived from `start_date` -- CORRECT, this is calendar year.
- Doc claims "no Industry FE specs" -- confirmed, all specs use firm FE only.
- **PASS**

**B6-CHECK: Standard Errors and Clustering**
- Doc claims: `cov_type="clustered"`, `cluster_entity=True`, firm-level clustering.
- Runner line 207: `model = model_obj.fit(cov_type="clustered", cluster_entity=True)`
- No `cluster_time` argument -- defaults to False.
- **PASS**

**B7-CHECK: Hypothesis Test**
- Doc claims: Two-tailed, `p_test = p_two` (no halving), significance thresholds `***<0.01, **<0.05, *<0.10`.
- Runner line 223: `p_test = p_two` -- confirmed.
- Runner lines 287-293 (fmt_coef function): `if pval < 0.01: stars = "^{***}"`, `elif pval < 0.05: stars = "^{**}"`, `elif pval < 0.10: stars = "^{*}"` -- confirmed.
- Doc claims `h_sig = not np.isnan(p_test) and p_test < 0.05` (runner line 225) -- confirmed.
- **PASS**

**Phase 3 Result:** 7/7 PASS.

---

## PHASE 4: FACTUAL ACCURACY -- SECTION C (Spec Register)

**Row count check:**
- Doc has 8 rows (columns 1-8).
- Runner: 4 DVs x 2 IVs = 8 Main sample specs (confirmed from generate_all_tables.py `cols: 8`).
- **PASS**

**Per-row verification:**

| Col | DV (doc) | DV (code) | IV (doc) | IV (code) | Entity FE | Time FE | Controls | Match |
|-----|----------|-----------|----------|-----------|-----------|---------|----------|-------|
| 1 | Manager_QA_Uncertainty_pct | Manager_QA_Uncertainty_pct | PRiskQ_lead | PRiskQ_lead | Firm | Cal Year | Base + Pres | YES |
| 2 | CEO_QA_Uncertainty_pct | CEO_QA_Uncertainty_pct | PRiskQ_lead | PRiskQ_lead | Firm | Cal Year | Base + Pres | YES |
| 3 | Manager_Pres_Uncertainty_pct | Manager_Pres_Uncertainty_pct | PRiskQ_lead | PRiskQ_lead | Firm | Cal Year | Base | YES |
| 4 | CEO_Pres_Uncertainty_pct | CEO_Pres_Uncertainty_pct | PRiskQ_lead | PRiskQ_lead | Firm | Cal Year | Base | YES |
| 5 | Manager_QA_Uncertainty_pct | Manager_QA_Uncertainty_pct | PRiskQ_lead2 | PRiskQ_lead2 | Firm | Cal Year | Base + Pres | YES |
| 6 | CEO_QA_Uncertainty_pct | CEO_QA_Uncertainty_pct | PRiskQ_lead2 | PRiskQ_lead2 | Firm | Cal Year | Base + Pres | YES |
| 7 | Manager_Pres_Uncertainty_pct | Manager_Pres_Uncertainty_pct | PRiskQ_lead2 | PRiskQ_lead2 | Firm | Cal Year | Base | YES |
| 8 | CEO_Pres_Uncertainty_pct | CEO_Pres_Uncertainty_pct | PRiskQ_lead2 | PRiskQ_lead2 | Firm | Cal Year | Base | YES |

Verification method: Runner iterates `iv_vars` (outer) then `dependent_variables` (inner). The `col_files` in generate_all_tables.py confirms ordering: lead1 cols 1-4, lead2 cols 5-8, with DV order Manager_QA, CEO_QA, Manager_Pres, CEO_Pres.

- No specs missing from the table.
- No phantom specs in the table.
- **PASS** (all 4 sub-checks: row count, DV match, FE match, controls match)

**Phase 4 Result:** 4/4 PASS.

---

## PHASE 5: FACTUAL ACCURACY -- SECTION D (Sample Construction)

**D1-CHECK: Population**
- Doc claims: Starting dataset `master_sample_manifest.parquet`, year range 2002-2018.
- Runner loads from Stage 3 panel which is built from the manifest. Project scope is 112,968 calls, 2,429 firms, 2002-2018.
- Attrition table starts at 112,968 -- matches project scope.
- **PASS**

**D2-CHECK: Exclusion Criteria**
- Doc claims 3-step attrition:
  1. Master manifest (full): 112,968
  2. Main sample filter (FF12 excl 8, 11): 88,205
  3. Complete-case + min-calls filter (>= 5): 75,224
- Runner lines 565-570 generate attrition with exactly 3 stages:
  ```python
  attrition_stages = [
      ("Master manifest", len(panel)),
      ("Main sample filter", (panel["sample"] == "Main").sum()),
      ("After complete-case + min-calls filter", main_result.get("n_obs", 0)),
  ]
  ```
- The filter order in code: (a) sample assignment via `assign_industry_sample`, (b) `prepare_regression_data` replaces inf->NaN and drops NaN rows, (c) min_calls >= 5 filter. Doc captures this sequence accurately.
- **PASS**

**D3-CHECK: Sample Counts per Spec**
- Doc provides N and N(firms) for all 8 columns. Claims sourced from `model_diagnostics.csv`.
- CEO DVs having fewer observations (~54K vs ~75K) is plausible due to CEO identification yielding more NaN.
- Lead2 having slightly fewer than lead1 is plausible due to edge-of-sample loss.
- Values cannot be independently verified without running the code, but the patterns are internally consistent.
- **PASS**

**Phase 5 Result:** 3/3 PASS.

---

## PHASE 6: FACTUAL ACCURACY -- SECTION E (Variable Dictionary)

Checked all 17 variables in the dictionary against source code.

| Variable | Name Match | Formula Correct | Source Correct | Winsorization Correct | Timing Correct | Result |
|----------|-----------|-----------------|---------------|----------------------|---------------|--------|
| `Manager_QA_Uncertainty_pct` | YES | YES (LM uncertainty words by mgrs in QA / total mgr QA words * 100) | YES (LinguisticEngine) | YES (0%/99% upper-only per year) | YES (contemporaneous) | PASS |
| `CEO_QA_Uncertainty_pct` | YES | YES | YES | YES | YES | PASS |
| `Manager_Pres_Uncertainty_pct` | YES | YES | YES | YES | YES | PASS |
| `CEO_Pres_Uncertainty_pct` | YES | YES | YES | YES | YES | PASS |
| `PRiskQ_lead` | YES | YES (Hassan PRisk from Q+1 via `_get_next_quarter`) | YES (firmquarter_2022q1.csv) | YES (1%/99% per year via `winsorize_by_year`) | YES (Lead Q+1) | PASS |
| `PRiskQ_lead2` | YES | YES (Hassan PRisk from Q+2 via `_get_next2_quarter`) | YES (firmquarter_2022q1.csv) | YES (1%/99% per year via `winsorize_by_year`) | YES (Lead Q+2) | PASS |
| `Analyst_QA_Uncertainty_pct` | YES | YES | YES (LinguisticEngine) | YES (0%/99% upper-only per year) | YES | PASS |
| `Entire_All_Negative_pct` | YES | YES | YES (LinguisticEngine) | YES (0%/99% upper-only per year) | YES | PASS |
| `Size` | YES | YES (ln(atq) where atq > 0) | YES (CompustatEngine: atq) | **FAIL** (see below) | YES | **FAIL** |
| `TobinsQ` | YES | YES (simplified; code clips negative debt and handles NaN more carefully but economic formula is equivalent) | YES (CompustatEngine) | **FAIL** (see below) | YES | **FAIL** |
| `ROA` | YES | YES (iby_annual Q4 / avg_assets) | YES (CompustatEngine) | (same fail as above) | YES | (FAIL inherited) |
| `CashHoldings` | YES | YES (cheq / atq) | YES (CompustatEngine) | (same fail) | YES | (FAIL inherited) |
| `DividendPayer` | YES | YES (1 if dvy_annual > 0, else 0) | YES (CompustatEngine) | YES (No, binary -- correctly excluded from winsorization) | YES | PASS |
| `firm_maturity` | YES | YES (req / atq) | YES (CompustatEngine) | (same fail) | YES | (FAIL inherited) |
| `earnings_volatility` | YES | YES (rolling 5-fiscal-year std of annual ROA, min 3 obs) | YES (CompustatEngine) | (same fail) | YES | (FAIL inherited) |
| `gvkey` | YES | YES (6-digit zero-padded Compustat identifier) | YES (Manifest) | N/A | N/A | PASS |
| `year` | YES | YES (derived from start_date via `.dt.year`) | YES (Manifest: start_date) | N/A | N/A | PASS |

**Winsorization failure for Compustat variables:**

The provenance doc states Compustat variables are winsorized at "1%/99% per year" and the variable dictionary says "1%/99% per year" for Size, TobinsQ, ROA, CashHoldings, firm_maturity, earnings_volatility.

**Actual code:** `_compustat_engine.py` line 1133: `year_col = comp["fyearq"]` -- winsorization is done per **fiscal year** (`fyearq`), NOT per calendar year. The doc's phrase "per year" is ambiguous but the Section H1 text says "per calendar year" explicitly, which is WRONG. The Compustat engine winsorizes by fiscal year.

**Completeness check:**
- All variables from `BASE_CONTROLS` (runner lines 103-113): all 9 present in dictionary.
- All DVs from CONFIG (runner lines 93-98): all 4 present.
- All IVs from CONFIG (runner line 100): both present.
- Dynamic Pres controls (`Manager_Pres_Uncertainty_pct`, `CEO_Pres_Uncertainty_pct`): already present as DVs.
- FE columns (`gvkey`, `year`): both present.
- No variables missing from the dictionary.

**Phase 6 Result:** 16/18 PASS (2 FAIL: Compustat winsorization grouping year claim affects Size + all Compustat-derived variables, counted as one systematic error affecting multiple rows).

---

## PHASE 7: FACTUAL ACCURACY -- SECTIONS F, G, H

### F-CHECK: Data Pipeline

**F1. Dependency Chain:** The 7-step chain from raw inputs through regression estimation to table generation is complete and accurate.
- Step 1 (raw inputs): firmquarter_2022q1.csv, master_sample_manifest.parquet, linguistic year-partitioned parquets, Compustat via engine -- all confirmed.
- Step 4 (runner loading): Runner line 447-473 loads panel with explicit column selection -- confirmed.
- Step 7 (table generation): generate_all_tables.py uses `"type": "moderation"` with 8 col_files -- confirmed at line 250.
- **PASS**

**F2. Data Engines:** 4 engines listed (LinguisticEngine, CompustatEngine, PRiskQLeadBuilder, PRiskQLead2Builder). All verified from builder imports.
- **PASS**

**F3. Merge Operations:** 16 panel-level merges documented, all on `file_name`, all left joins, all zero row-delta enforced. Plus 2 intra-builder merges for PRisk data. Verified against builder code lines 136-153 and prisk builder code.
- **PASS**

### G-CHECK: Outputs

**G1. Stage 3 Outputs:**
- `h11_prisk_uncertainty_lead_panel.parquet` -- builder line 190: confirmed.
- `summary_stats.csv` -- builder line 197-198: confirmed.
- `report_step3_h11_lead.md` -- builder line 240: confirmed.
- `run_manifest.json` -- builder line 203-212: confirmed.
- **PASS**

**G2. Stage 4 Outputs:**
- `h11_prisk_uncertainty_lead_table.tex` -- runner line 257, 556: confirmed.
- `model_diagnostics.csv` -- runner line 557: confirmed.
- `summary_stats.csv` and `summary_stats.tex` -- runner lines 498-499: confirmed.
- `sample_attrition.csv` and `sample_attrition.tex` -- runner line 570: confirmed.
- `regression_results_{sample}_{dv}_{lead}.txt` -- runner line 552: confirmed.
- `run_manifest.json` -- runner lines 574-584: confirmed.

**FAIL: Doc claims "26 individual regression .txt files" from the 2026-03-27 run.** The maximum possible is 3 samples x 4 DVs x 2 leads = 24. The number 26 is impossible unless additional files exist for a different reason. The doc text should say 24, not 26.

**G3. Summary Statistics:**
- 15 variables listed in doc match `SUMMARY_STATS_VARS` (runner lines 127-146) exactly.
- Metrics: N, Mean, SD, Min, P25, Median, P75, Max via `make_summary_stats_table` -- confirmed.
- Stratification by sample (Main, Finance, Utility) -- confirmed (runner line 496).
- **PASS**

### H-CHECK: Outlier/Missing Treatment

**H1. Winsorization:**
- Linguistic variables: 0%/99% upper-only per year -- confirmed (`_linguistic_engine.py` line 255-258).
- PRiskQ_lead and PRiskQ_lead2: 1%/99% per year via `winsorize_by_year` -- confirmed (`prisk_q_lead.py` line 170; `prisk_q_lead2.py` line 173).
- **FAIL: Compustat variables.** Doc says "1%/99% per calendar year." Actual code: `_compustat_engine.py` line 1133 uses `year_col = comp["fyearq"]`, which is **fiscal year**, not calendar year. The claim "per calendar year" is factually incorrect. (Same finding as Phase 6.)
- DividendPayer skip -- confirmed (`_compustat_engine.py` line 1124).

**H2. Missing Data Policy:**
- Doc claims: `panel.replace([np.inf, -np.inf], np.nan).dropna(subset=required)` at runner line 175.
- Runner line 175: `df = panel.replace([np.inf, -np.inf], np.nan).dropna(subset=required).copy()` -- confirmed.
- **PASS**

**H3. Transformations:**
- Doc claims `Size = ln(atq)` -- confirmed (`_compustat_engine.py` line 938).
- Doc claims "No centering or z-scoring" -- confirmed (no evidence of centering in runner).
- Doc claims LaTeX table note "All continuous controls are standardized" is inaccurate per the code -- confirmed. The runner line 399 contains this note but no standardization occurs.
- **PASS**

**FAIL: Known Issue #5.** Doc says "Diagnostics CSV contains `beta_prisk_p_one` column." Searching the runner for `p_one` yields zero matches. The meta dict (runner lines 235-251) has NO `beta_prisk_p_one` key. The only p-value key is `beta_prisk_p_two` (duplicated on lines 248-249). Known Issue #5 is factually incorrect -- there is no `p_one` column in the diagnostics output for this runner.

**Phase 7 Result:** 5/8 PASS, 3 FAIL (Compustat winsorization year type, output file count "26", Known Issue #5 inaccuracy).

---

## PHASE 8: FACTUAL ACCURACY -- SECTION I (Table Generator Entry)

Verified against `outputs/generate_all_tables.py` lines 248-276.

| Check | Doc Claims | Code Says | Match |
|-------|-----------|-----------|-------|
| `id` = "H11-Lead" | H11-Lead | Line 249: `"id": "H11-Lead"` | YES |
| `type` = "moderation" | moderation | Line 250: `"type": "moderation"` | YES |
| `cols` = 8 | 8 | Line 254: `"cols": 8` | YES |
| `key_tails` = ["two", "two"] | ["two", "two"] | Line 275: `"key_tails": ["two", "two"]` | YES |
| `key_vars` = ["PRiskQ_lead", "PRiskQ_lead2"] | ["PRiskQ_lead", "PRiskQ_lead2"] | Line 273: same | YES |

**FAIL: Line reference.** Doc says "Source: generate_all_tables.py, lines 273--300." The entry actually spans lines 248-276. This is a line reference error. The factual content of the entry is correct.

**Phase 8 Result:** 4/5 PASS, 1 FAIL (line reference).

---

## PHASE 9: FACTUAL ACCURACY -- SECTION K (Model-Family Addendum)

**K1. PanelOLS Specifics (filled):**
- Entity effects absorbed via EntityEffects: Runner formula includes `EntityEffects`, line 190 -- confirmed.
- Time effects absorbed via TimeEffects: Runner formula includes `TimeEffects`, line 190 -- confirmed.
- `other_effects` not used: No `other_effects` in formula. No Industry FE specs. -- confirmed.
- `drop_absorbed=True`: Runner line 206: `PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)` -- confirmed.
- R-squared: `model.rsquared` on line 214 and 243 (`"r2": float(model.rsquared)`). Adj R-squared formula on line 244: `1 - (1 - model.rsquared) * (model.nobs - 1) / model.df_resid` -- confirmed.
- **PASS**

**K2-K6 (N/A):**
- All marked N/A as expected for a PanelOLS suite.
- **PASS**

**Panel Index consistency:**
- Doc K1 says MultiIndex `["gvkey", "year"]` set at runner line 203.
- Runner line 203: `df_panel = df_sample.set_index(["gvkey", "year"])` -- confirmed.
- **PASS**

**Phase 9 Result:** 3/3 PASS.

---

## PHASE 10: QUALITY GATE CHECKLIST

| # | Quality Gate | Met? | Evidence |
|---|-------------|------|----------|
| 1 | Every variable in every regression spec appears in Variable Dictionary with explicit formula and source engine | YES | All 17 variables verified. All 4 DVs, 2 IVs, 9 base controls, 2 FE columns present with formulas. |
| 2 | The model equation matches what the code actually estimates | YES | Formula string `{dv_var} ~ 1 + {iv_var} + {controls} + EntityEffects + TimeEffects` verified against runner lines 187-190. |
| 3 | The specification register accounts for every model column | YES | 8 rows matching 8 col_files in generate_all_tables.py. All (DV, IV) combinations accounted for. |
| 4 | The attrition cascade has row counts for each filter step | YES | 3-step cascade with counts (112,968 -> 88,205 -> 75,224). |
| 5 | The tail test direction matches between runner code and generate_all_tables.py | YES | Runner: `p_test = p_two` (two-tailed). generate_all_tables: `key_tails: ["two", "two"]`. |
| 6 | The FE specification matches between docstring, code, and this document | YES | Docstring: EntityEffects + TimeEffects. Code: same in formula. Doc: Firm + Cal Year FE. All consistent. |
| 7 | Every merge in the panel builder is documented with join keys and type | YES | 16 panel merges + 2 PRisk builder merges, all documented with keys (`file_name` or `gvkey, cal_q_lead*`) and type (left). |
| 8 | The output file list matches what the runner actually writes | **NO** | Doc claims "26 individual regression .txt files" but max is 24 (3 samples x 4 DVs x 2 leads). |
| 9 | The model-family addendum is filled for the correct family only | YES | K1 (PanelOLS) filled; K2-K6 marked N/A. |
| 10 | Any claim marked [UNVERIFIED] has an explanation of what blocks verification | YES | No [UNVERIFIED] claims found in the document. All claims are stated as verified. |

**Phase 10 Result:** 9/10 PASS, 1 FAIL (Quality Gate 8: output file count mismatch).

---

## PHASE 11: CROSS-REFERENCE CONSISTENCY

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | DVs in B2 match DVs in C (spec register) | PASS | B2: 4 DVs. C: same 4 DVs across 8 columns. |
| 2 | DVs in C match DVs in I (table generator) | PASS | C: 4 unique DVs. I: col_dv_labels map to same 4 DVs, col_files reference same DV names. |
| 3 | Controls in B4 match variables in E (dictionary) | PASS | B4: 9 base controls + 2 dynamic Pres controls. All 11 appear in E. |
| 4 | Column count in A matches rows in C | PASS | A: 8. C: 8 rows. |
| 5 | Column count in A matches "cols" in I | PASS | A: 8. I: `"cols": 8`. |
| 6 | Tail direction in A matches B7 matches I | PASS | A: two-tailed. B7: two-tailed (`p_test = p_two`). I: `key_tails: ["two", "two"]`. |
| 7 | FE in B5 matches C matches K | PASS | B5: Firm + Cal Year. C: all rows say Firm + Cal Year. K1: EntityEffects + TimeEffects via `["gvkey", "year"]` index. |
| 8 | Panel index in A matches set_index in K | PASS | A: `(gvkey, year)`. K1: `set_index(["gvkey", "year"])` at runner line 203. |

**Phase 11 Result:** 8/8 PASS.

---

## FAILURES (detailed)

| Phase | Check | Provenance Doc Claims | Actual Code Says | Severity | Fix Required |
|-------|-------|----------------------|-----------------|----------|-------------|
| 6, 7 | Compustat winsorization grouping | "1%/99% per calendar year" (Section H1: "Applied at CompustatEngine level before merge to manifest" with "per calendar year") | `_compustat_engine.py` line 1133: `year_col = comp["fyearq"]` -- winsorization is per **fiscal year** (`fyearq`), not calendar year | MEDIUM | Change "per calendar year" to "per fiscal year (fyearq)" in Sections E and H1 |
| 7 | G2 output file count | "26 individual regression .txt files" (G2 section) | Max 3 samples x 4 DVs x 2 leads = 24 regression .txt files | LOW | Change "26" to "24" |
| 7 | Known Issue #5 | "Diagnostics CSV contains `beta_prisk_p_one` column" | No `p_one` reference exists anywhere in the runner. Meta dict has only `beta_prisk_p_two` (duplicated). There is no `beta_prisk_p_one` column. | LOW | Remove Known Issue #5 entirely or rewrite to note the `beta_prisk_p_two` duplicate key instead |
| 8 | Line reference for generate_all_tables | "Source: generate_all_tables.py, lines 273--300" | Entry spans lines 248-276 | TRIVIAL | Update line reference to "lines 248--276" |

---

## CORRECTIONS REQUIRED

1. **Section E (Variable Dictionary) -- Winsorization column for Compustat variables**
   - Current: "1%/99% per year" for Size, TobinsQ, ROA, CashHoldings, firm_maturity, earnings_volatility
   - Should be: "1%/99% per fiscal year (fyearq)"
   - Code reference: `_compustat_engine.py` line 1133: `year_col = comp["fyearq"]`

2. **Section H1 (Winsorization) -- Compustat variables description**
   - Current: "Level: 1%/99% per calendar year"
   - Should be: "Level: 1%/99% per fiscal year (fyearq)"
   - Code reference: `_compustat_engine.py` line 1133

3. **Section G2 (Stage 4 Outputs) -- Regression file count**
   - Current: "26 individual regression .txt files"
   - Should be: "24 individual regression .txt files" (or up to 24, if some combinations are skipped for insufficient data)
   - Code reference: 3 samples x 4 DVs x 2 leads = 24

4. **Section L, Known Issue #5 -- Inaccurate claim about `beta_prisk_p_one`**
   - Current: "Diagnostics CSV contains `beta_prisk_p_one` column. Despite this being a two-tailed test, the CSV output has a `beta_prisk_p_one` column..."
   - Should be: Either delete this issue entirely or replace with: "The meta dict has a duplicate key `beta_prisk_p_two` (runner lines 248-249). The second assignment (`float(p_test)`) overwrites the first (`float(p_two)`). Since `p_test = p_two` for this two-tailed suite, this has no effect."
   - Code reference: Runner lines 248-249, no `p_one` anywhere in runner.

5. **Section I -- Line reference**
   - Current: "Source: generate_all_tables.py, lines 273--300."
   - Should be: "Source: generate_all_tables.py, lines 248--276."
   - Code reference: Entry starts at line 248 (`{`) and ends at line 276 (`},`)
