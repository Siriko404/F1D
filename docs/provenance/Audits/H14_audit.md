# H14 Provenance Document -- Adversarial Audit Report

**Audit Date:** 2026-03-30
**Auditor:** Hostile auditor (automated adversarial review)
**Provenance Doc:** `docs/provenance/H14.md`
**Runner:** `src/f1d/econometric/run_h14_bidask_spread.py`
**Panel Builder:** `src/f1d/variables/build_h14_bidask_spread_panel.py`
**Creation Prompt:** `docs/Prompts/Suite Provenance Doc.txt`

---

## AUDIT SUMMARY

| Category | Total Checks | Passed | Failed | Score |
|----------|-------------|--------|--------|-------|
| Structural Completeness (Phase 1) | 25 | 24 | 1 | 96.0% |
| Suite Identity (Phase 2) | 10 | 10 | 0 | 100.0% |
| Model Specification (Phase 3) | 7 | 7 | 0 | 100.0% |
| Spec Register (Phase 4) | 7 | 7 | 0 | 100.0% |
| Sample Construction (Phase 5) | 4 | 3 | 1 | 75.0% |
| Variable Dictionary (Phase 6) | 22 | 22 | 0 | 100.0% |
| Pipeline/Outputs/Treatment (Phase 7) | 9 | 9 | 0 | 100.0% |
| Table Generator Entry (Phase 8) | 6 | 5 | 1 | 83.3% |
| Model-Family Addendum (Phase 9) | 6 | 6 | 0 | 100.0% |
| Quality Gates (Phase 10) | 10 | 9 | 1 | 90.0% |
| Cross-Reference Consistency (Phase 11) | 8 | 8 | 0 | 100.0% |
| **TOTAL** | **114** | **110** | **4** | **96.5%** |

---

## VERDICT

**PASS WITH NOTES**: The provenance document is substantially accurate and complete. Four issues were found, all minor:

1. Section D2 (Attrition Cascade) omits actual row counts -- filter descriptions are present and correct, but the column structure from the creation prompt template (Rows Before / Rows After / Dropped) is not used.
2. Section I incorrectly states the main loop line number in `generate_all_tables.py` as 1215; the actual line is 1234.
3. Runner docstring says "4 columns" and lists `col{1-4}` outputs, but code has 6 MODEL_SPECS. The provenance doc correctly documents 6 columns (code is truth), but does not explicitly flag the stale docstring.
4. `fyearq_int` is included in the runner's `required` list for complete-case filtering (line 241) despite never being used as a FE column. This is not documented as a known issue.

None of these affect the document's core accuracy regarding model specification, variable construction, or regression configuration.

---

## FAILURES (detailed)

| Phase | Check | Provenance Doc Claims | Actual Code Says | Severity | Fix Required |
|-------|-------|----------------------|-----------------|----------|-------------|
| 5 | D2 attrition cascade row counts | D2 table has columns: Step, Filter, Description (no counts) | Creation prompt requires: Step, Filter, Rows Before, Rows After, Dropped | Minor | Add row counts or note them as runtime-dependent with col-1 representative values |
| 8 | I main loop line number | "falls through to generate_table() ... in the main loop at line 1215" | Main loop `for suite in SUITES:` is at line 1234; `generate_table(suite)` call at line 1259 | Minor | Change "line 1215" to "line 1234" |
| 10 | QG4 attrition row counts | No row counts in D2 | Quality Gate 4 requires row counts per filter step | Minor | Same fix as Phase 5 D2 |
| -- | Known issue (not scored) | Not documented | `fyearq_int` is in `required` list (line 241) causing complete-case drops for missing fiscal year, despite not being used as FE | Info | Add as Known Issue #8 |

---

## PHASE 1: STRUCTURAL COMPLETENESS

Read `docs/Prompts/Suite Provenance Doc.txt` to extract required sections A-L. Then verified each exists in `docs/provenance/H14.md`.

| Section | Required by Prompt | Present in Doc | Complete | Notes |
|---------|-------------------|----------------|----------|-------|
| A. Suite Identity | Yes | Yes | Yes | All YAML fields present |
| B. Model Specification | Yes | Yes | Yes | All subsections present |
| B1. Regression Equation | Yes | Yes | Yes | LaTeX equation with all terms |
| B2. Dependent Variable(s) | Yes | Yes | Yes | DSPREAD with full construction detail |
| B3. Independent Variable(s) | Yes | Yes | Yes | All 4 IVs listed |
| B4. Control Variables | Yes | Yes | Yes | Base (8) + Extended (12) tables |
| B5. Fixed Effects | Yes | Yes | Yes | Full FE table with column mapping |
| B6. Standard Errors | Yes | Yes | Yes | Clustered, firm-level |
| B7. Hypothesis Test | Yes | Yes | Yes | One-tailed with p-value formula |
| C. Spec Register | Yes | Yes | Yes | 6 rows matching 6 MODEL_SPECS |
| D. Sample Construction | Yes | Yes | Partial | **D2 missing row counts** |
| D1. Population | Yes | Yes | Yes | manifest, year range stated |
| D2. Exclusion Criteria | Yes | Yes | **Partial** | Filter steps correct but no row counts per step |
| D3. Sample Counts per Spec | Yes | Yes | Yes | Documents that N varies, explains why |
| E. Variable Dictionary | Yes | Yes | Yes | All 20 variables present |
| F. Data Pipeline | Yes | Yes | Yes | Full dependency chain |
| F1. Dependency Chain | Yes | Yes | Yes | 7-step chain |
| F2. Data Engines | Yes | Yes | Yes | 5 engines listed |
| F3. Merge Operations | Yes | Yes | Yes | 16 panel builder merges + 2 within-builder merges |
| G. Outputs | Yes | Yes | Yes | Stage 3 + Stage 4 outputs |
| G1. Stage 3 Outputs | Yes | Yes | Yes | 4 files listed |
| G2. Stage 4 Outputs | Yes | Yes | Yes | 9 files listed |
| G3. Summary Statistics | Yes | Yes | Yes | 17 variables with labels |
| H. Outlier/Missing Treatment | Yes | Yes | Yes | 3 subsections |
| I. generate_all_tables Entry | Yes | Yes | Yes | Full entry with verification table |
| J. Reproduction Commands | Yes | Yes | Yes | 3 commands |
| K. Model-Family Addendum | Yes | Yes | Yes | K1 filled, K2-K6 marked N/A |
| L. Known Issues | Yes | Yes | Yes | 7 issues documented |

**Phase 1 Result: 24/25 PASS (1 partial for D2 missing row counts)**

---

## PHASE 2: FACTUAL ACCURACY -- SECTION A (Suite Identity)

### A-1. Suite ID
- **Doc claims:** H14
- **Verification:** Trivially correct.
- **Result:** PASS

### A-2. Title
- **Doc claims:** "Speech Uncertainty and Bid-Ask Spread Changes"
- **Code evidence:** Runner docstring (line 4): "Test H14 Bid-Ask Spread Hypothesis". LaTeX table caption (line 430): "Speech Uncertainty and Bid-Ask Spread Changes". generate_all_tables.py caption: "H14: Speech Uncertainty and Bid-Ask Spread Changes".
- **Result:** PASS (matches table caption)

### A-3. Hypothesis
- **Doc claims:** "Higher earnings-call language uncertainty is associated with a larger increase in bid-ask spreads around the conference call (lower market liquidity)."
- **Code evidence:** Runner docstring (lines 35-36): "H14: beta(uncertainty_var) > 0 -- higher uncertainty -> wider spreads." Panel builder docstring (lines 25-26): "Higher earnings-call language uncertainty is associated with a larger increase in bid-ask spreads around the conference call (lower market liquidity)."
- **Result:** PASS

### A-4. Direction (tail test)
- **Doc claims:** one-tailed beta > 0
- **Code evidence:** Runner line 364: `p_one = p_two / 2 if beta > 0 else 1 - p_two / 2`. Runner line 36: "H14: beta(uncertainty_var) > 0". generate_all_tables.py: `"tail": "one", "hyp_dir": ">"`.
- **Result:** PASS

### A-5. Model Family
- **Doc claims:** PanelOLS
- **Code evidence:** Runner line 71: `from linearmodels.panel import PanelOLS`. Lines 321, 334: `PanelOLS(...)` and `PanelOLS.from_formula(...)`.
- **Result:** PASS

### A-6. Estimator
- **Doc claims:** linearmodels.panel.PanelOLS
- **Code evidence:** Runner line 71: `from linearmodels.panel import PanelOLS`.
- **Result:** PASS

### A-7. Unit of Observation
- **Doc claims:** call-level (individual earnings call)
- **Code evidence:** Panel builder docstring (line 22): "Unit of observation: the individual earnings call (file_name)." Runner line 590: "Unit of observation: individual earnings call (call-level)".
- **Result:** PASS

### A-8. Panel Index
- **Doc claims:** `(gvkey, cal_yr)` for cols 1-4; `(gvkey, cal_yr_qtr)` for cols 5-6
- **Code evidence:** Runner line 304: `time_col = "cal_yr_qtr" if fe_type.endswith("_yq") else "cal_yr"`. Runner line 314: `df_panel = df_prepared.set_index(["gvkey", time_col])`. MODEL_SPECS cols 1-4 have fe="industry"/"firm" (no "_yq"), cols 5-6 have fe="industry_yq"/"firm_yq".
- **Result:** PASS

### A-9. Columns (number of model specs)
- **Doc claims:** 6
- **Code evidence:** Runner lines 115-123: `MODEL_SPECS` has exactly 6 entries (col 1 through col 6).
- **Result:** PASS

### A-10. Runner and Panel Builder paths
- **Doc claims:** Runner: `src/f1d/econometric/run_h14_bidask_spread.py`, Panel Builder: `src/f1d/variables/build_h14_bidask_spread_panel.py`
- **Verification:** Both files exist and were read during this audit.
- **Result:** PASS

**Phase 2 Result: 10/10 PASS**

---

## PHASE 3: FACTUAL ACCURACY -- SECTION B (Model Specification)

### B1-CHECK: Regression Equation
- **Doc claims:** `DSPREAD_{i,t} = b1*CEO_QA_Unc + b2*CEO_Pres_Unc + b3*Mgr_QA_Unc + b4*Mgr_Pres_Unc + Controls + alpha_i + delta_t + epsilon`
- **Code evidence:** Runner line 301: `exog = KEY_IVS + controls`. KEY_IVS has 4 uncertainty measures. Formula for firm FE (line 333): `"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"`. For industry FE: separate dependent, exog, other_effects, time_effects. All 4 IVs enter simultaneously.
- **Assessment:** Equation correctly represents the code. All terms present, no extra terms.
- **Result:** PASS

### B2-CHECK: Dependent Variable(s)
- **Doc claims:** DSPREAD = mean(RelSpread[+1,+3]) - mean(RelSpread[-3,-1]) using closing BID/ASK quotes.
- **Code evidence:** Panel builder line 181: `panel = panel.rename(columns={"delta_spread_closing": "DSPREAD"})`. BidAskSpreadChangeBuilder line 346-348: closing spread = `2 * (ASK - BID) / (ASK + BID)`. Lines 422-423: `delta_spread_closing = post_call_spread_closing - pre_call_spread_closing`.
- **Construction steps verification:**
  - Step 1 (CCM linkage): builder `_build_permno_map` at line 127-206. Date-bounded: line 192-194 `linkdt <= start_date <= linkenddt`. PASS.
  - Step 2 (Reference date): builder line 355-359: last trading day on or before call. PASS.
  - Step 3 (Pre-window): builder line 372-376: pre_rank by date descending. PASS.
  - Step 4 (Post-window): builder line 379-383: post_rank by date ascending. PASS.
  - Step 5 (Closing spread): builder line 346-348. PASS.
  - Step 6 (Pre/Post averages): builder lines 413-420 for closing variant. PASS.
  - Step 7 (Delta): builder line 422-423. PASS.
  - Step 8 (Min 2 days): builder lines 300-302: `min_pre = max(1, w - 1) = max(1, 3-1) = 2`. Lines 425-430: filter applied. PASS.
  - Step 9 (Rename): panel builder line 181. PASS.
- **Result:** PASS

### B3-CHECK: Independent Variable(s)
- **Doc claims:** CEO_QA_Uncertainty_pct, CEO_Pres_Uncertainty_pct, Manager_QA_Uncertainty_pct, Manager_Pres_Uncertainty_pct from LinguisticEngine.
- **Code evidence:** Runner lines 88-92: `KEY_IVS` lists all 4 exact column names. Panel builder imports CEOQAUncertaintyBuilder, CEOPresUncertaintyBuilder, ManagerQAUncertaintyBuilder, ManagerPresUncertaintyBuilder (lines 56-59). All enter simultaneously via `exog = KEY_IVS + controls` (runner line 301).
- **Missing IVs check:** No other IVs exist in the code. PASS.
- **Result:** PASS

### B4-CHECK: Control Variables
- **Doc claims:** Base Controls (8): Size, TobinsQ, ROA, BookLev, CapexAt, DividendPayer, OCF_Volatility, PreCallSpread. Extended Controls (Base + 4): + StockPrice, Turnover, Volatility, AbsSurpDec.
- **Code evidence:** Runner lines 97-106: `BASE_CONTROLS` = [Size, TobinsQ, ROA, BookLev, CapexAt, DividendPayer, OCF_Volatility, PreCallSpread]. 8 variables. PASS. Runner lines 108-113: `EXTENDED_CONTROLS` = BASE_CONTROLS + [StockPrice, Turnover, Volatility, AbsSurpDec]. 12 variables. PASS.
- **PreCallSpread as lagged-DV:** Documented as "PreCallSpread (lagged-DV control: pre-call relative spread level)". Code: PreCallSpread = `pre_call_spread_closing` = mean of closing spread for [-3,-1] window, constructed by BidAskSpreadChangeBuilder. This IS the pre-call level of the DV's denominator, functioning as a lagged-DV control. PASS.
- **Dynamic controls:** No dynamic control logic found in runner. None documented. PASS.
- **Every control in code in doc:** Verified all 8 base + 4 extended. PASS.
- **Every control in doc in code:** No extras in doc. PASS.
- **Result:** PASS

### B5-CHECK: Fixed Effects
- **Doc claims:** Industry (ff12_code via other_effects) for cols 1,3,5; Firm (gvkey via EntityEffects) for cols 2,4,6; Cal Year (cal_yr) for cols 1-4; Cal Yr-Qtr (cal_yr_qtr) for cols 5-6.
- **Code evidence:**
  - Industry FE: Runner lines 317-329: `PanelOLS(entity_effects=False, time_effects=True, other_effects=industry_data)` where `industry_data = df_panel["ff12_code"]`. PASS.
  - Firm FE: Runner line 333: `"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"`. PASS.
  - Time FE: Runner line 304: `time_col = "cal_yr_qtr" if fe_type.endswith("_yq") else "cal_yr"`. Line 314: `set_index(["gvkey", time_col])`. PASS.
  - Col mapping: MODEL_SPECS cols 1-4 use "industry"/"firm" (cal_yr), cols 5-6 use "industry_yq"/"firm_yq" (cal_yr_qtr). PASS.
- **Time FE source:** `build_cal_yr_qtr_index` in `panel_utils.py` lines 195-218 creates `cal_yr = start_date.dt.year` and `cal_yr_qtr = cal_yr * 10 + cal_qtr`. These are calendar, not fiscal. PASS.
- **Result:** PASS

### B6-CHECK: Standard Errors and Clustering
- **Doc claims:** cov_type="clustered", cluster_entity=True (firm-level, gvkey). Lines 330, 335.
- **Code evidence:** Runner line 330: `model_obj.fit(cov_type="clustered", cluster_entity=True)`. Line 335: same. Both industry and firm FE specs use identical clustering.
- **Result:** PASS

### B7-CHECK: Hypothesis Test
- **Doc claims:** One-tailed beta > 0. `p_one = p_two / 2 if beta > 0 else 1 - p_two / 2` at line 364. Stars: *** p<0.01, ** p<0.05, * p<0.10 at lines 384-394.
- **Code evidence:** Runner line 364: `p_one = p_two / 2 if beta > 0 else 1 - p_two / 2`. PASS. Runner lines 384-394: `_sig_stars` function with exact thresholds. PASS.
- **Result:** PASS

**Phase 3 Result: 7/7 PASS**

---

## PHASE 4: FACTUAL ACCURACY -- SECTION C (Spec Register)

- **Row count:** Doc has 6 rows (cols 1-6). MODEL_SPECS has 6 entries. PASS.
- **Col 1:** DV=DSPREAD, Entity=Industry(FF12), Time=Cal Year, Controls=Base(8). Code: `{"col": 1, "dv": "DSPREAD", "fe": "industry", "controls": "base"}`. PASS.
- **Col 2:** DV=DSPREAD, Entity=Firm, Time=Cal Year, Controls=Base(8). Code: `{"col": 2, "dv": "DSPREAD", "fe": "firm", "controls": "base"}`. PASS.
- **Col 3:** DV=DSPREAD, Entity=Industry(FF12), Time=Cal Year, Controls=Extended(12). Code: `{"col": 3, "dv": "DSPREAD", "fe": "industry", "controls": "extended"}`. PASS.
- **Col 4:** DV=DSPREAD, Entity=Firm, Time=Cal Year, Controls=Extended(12). Code: `{"col": 4, "dv": "DSPREAD", "fe": "firm", "controls": "extended"}`. PASS.
- **Col 5:** DV=DSPREAD, Entity=Industry(FF12), Time=Cal Yr-Qtr, Controls=Extended(12). Code: `{"col": 5, "dv": "DSPREAD", "fe": "industry_yq", "controls": "extended"}`. PASS.
- **Col 6:** DV=DSPREAD, Entity=Firm, Time=Cal Yr-Qtr, Controls=Extended(12). Code: `{"col": 6, "dv": "DSPREAD", "fe": "firm_yq", "controls": "extended"}`. PASS.

**Phase 4 Result: 7/7 PASS**

---

## PHASE 5: FACTUAL ACCURACY -- SECTION D (Sample Construction)

### D1-CHECK: Population
- **Doc claims:** Starting dataset: master_sample_manifest.parquet, year range 2002-2018.
- **Code evidence:** Runner line 186-191: loads from `outputs/variables/h14_bidask_spread/latest/h14_bidask_spread_panel.parquet`. Panel builder loads manifest from `outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet`. Project scope: 112,968 calls, 2,429 firms, 2002-2018.
- **Result:** PASS

### D2-CHECK: Exclusion Criteria
- **Doc claims 5 filter steps:**
  1. Full manifest -- Code: panel builder loads all calls from manifest. PASS.
  2. Main sample filter (excl FF12=8,11) -- Code: runner line 227: `panel[~panel["ff12_code"].isin([8, 11])]`. PASS.
  3. DV non-missing (DSPREAD NaN) -- Code: runner line 260: `df[df[dv].notna()]`. PASS.
  4. Complete case (all vars NaN) -- Code: runner lines 263-264: `df[required].notna().all(axis=1)`. PASS.
  5. Min 5 calls per firm -- Code: runner lines 267-269: `firm_counts >= MIN_CALLS_PER_FIRM` where `MIN_CALLS_PER_FIRM = 5` (line 125). PASS.
- **Filter order:** Matches code order in `prepare_regression_data` (lines 252-273). PASS.
- **Missing row counts:** The creation prompt template requires columns "Rows Before | Rows After | Dropped". The provenance doc D2 table has only "Step | Filter | Description" -- **no actual counts**. The doc notes: "Attrition counts vary by specification... The runner's generate_attrition_table records col-1 counts as representative (runner line 753-759)." This is informative but does not meet the creation prompt's template.
- **Result:** FAIL (row counts missing from D2 table)

### D3-CHECK: Sample Counts per Spec
- **Doc claims:** N varies across specifications due to different control sets and FE granularity.
- **Code evidence:** Runner line 240: `controls = BASE_CONTROLS if spec["controls"] == "base" else EXTENDED_CONTROLS`. Different required lists per spec. Complete-case filter drops different rows per spec. PASS.
- **Result:** PASS

### Note on fyearq_int in required list
- Runner line 241: `required = [dv] + KEY_IVS + controls + ["gvkey", "fyearq_int", "ff12_code"]`. The `fyearq_int` column is included in the complete-case check, meaning rows with missing fiscal year mappings are dropped even though `fyearq_int` is never used as a FE or regression variable. This is not documented as a known issue in the provenance doc. This causes some unnecessary sample attrition. Flagged as informational finding.

**Phase 5 Result: 3/4 PASS**

---

## PHASE 6: FACTUAL ACCURACY -- SECTION E (Variable Dictionary)

Verified each of the 20 variables (+ 4 FE columns = 24 rows) in the dictionary.

### DV
| Variable | Name Match | Formula Match | Source Match | Winsorization Match | Timing Match | Result |
|----------|-----------|---------------|-------------|---------------------|-------------|--------|
| DSPREAD | Yes (runner line 200, MODEL_SPECS line 116) | Yes (closing BID/ASK verified in builder lines 340-348) | Yes (CRSPEngine via BidAskSpreadChangeBuilder) | Yes (1%/99% pooled, panel builder line 202) | Yes (event-window) | PASS |

### IVs (4)
| Variable | Name Match | Formula Match | Source Match | Winsorization Match | Timing Match | Result |
|----------|-----------|---------------|-------------|---------------------|-------------|--------|
| CEO_QA_Uncertainty_pct | Yes (runner KEY_IVS line 89) | Yes (% uncertainty words) | Yes (LinguisticEngine) | Yes (No, bounded [0,100]) | Yes (contemporaneous) | PASS |
| CEO_Pres_Uncertainty_pct | Yes (runner KEY_IVS line 90) | Yes | Yes | Yes | Yes | PASS |
| Manager_QA_Uncertainty_pct | Yes (runner KEY_IVS line 91) | Yes | Yes | Yes | Yes | PASS |
| Manager_Pres_Uncertainty_pct | Yes (runner KEY_IVS line 92) | Yes | Yes | Yes | Yes | PASS |

### Base Controls (8)
| Variable | Name Match | Formula Match | Source Match | Winsorization Match | Timing Match | Result |
|----------|-----------|---------------|-------------|---------------------|-------------|--------|
| Size | Yes (runner BASE_CONTROLS line 98) | Yes (ln(atq)) | Yes (CompustatEngine) | Yes (1%/99% by fyearq) | Yes | PASS |
| TobinsQ | Yes (line 99) | Yes ((cshoq*prccq + dlcq + dlttq)/atq) | Yes | Yes | Yes | PASS |
| ROA | Yes (line 100) | Yes (iby_annual/avg_assets) | Yes | Yes | Yes | PASS |
| BookLev | Yes (line 101) | Yes ((dlcq+dlttq)/atq, missing as 0) | Yes | Yes | Yes | PASS |
| CapexAt | Yes (line 102) | Yes (capxy_annual/atq_lag) | Yes | Yes | Yes | PASS |
| DividendPayer | Yes (line 103) | Yes (1 if dvy_annual>0) | Yes | Yes (No, binary; in skip_winsorize) | Yes | PASS |
| OCF_Volatility | Yes (line 104) | Yes (rolling 5yr std, min 3) | Yes | Yes (1%/99% by fyearq) | Yes | PASS |
| PreCallSpread | Yes (line 105) | Yes (mean of closing spread [-3,-1]) | Yes (CRSPEngine via BidAskSpreadChangeBuilder) | Yes (1%/99% pooled, line 202) | Yes (pre-event) | PASS |

### Extended Controls (additional 4)
| Variable | Name Match | Formula Match | Source Match | Winsorization Match | Timing Match | Result |
|----------|-----------|---------------|-------------|---------------------|-------------|--------|
| StockPrice | Yes (runner EXTENDED line 109) | Yes (abs(PRC), CRSPEngine line 92) | Yes (CRSPEngine via StockPriceBuilder) | Yes (1%/99% pooled, line 202) | Yes | PASS |
| Turnover | Yes (line 110) | Yes (VOL/(SHROUT*1000)) | Yes (CRSPEngine via TurnoverBuilder) | Yes (1%/99% pooled, line 202) | Yes | PASS |
| Volatility | Yes (line 111) | Yes (std(RET)*sqrt(252)*100) | Yes (CRSPEngine via VolatilityBuilder) | Yes (1%/99% by calendar year at CRSPEngine level, line 445) | Yes (inter-call window) | PASS |
| AbsSurpDec | Yes (line 112) | Yes (abs(SurpDec), panel builder line 187) | Yes (IbesEngine via EarningsSurpriseBuilder) | Yes (1%/99% pooled, line 202) | Yes | PASS |

### FE Columns (4)
| Variable | Name Match | Source Match | Result |
|----------|-----------|-------------|--------|
| gvkey | Yes | Yes (manifest) | PASS |
| ff12_code | Yes | Yes (manifest) | PASS |
| cal_yr | Yes (start_date.dt.year) | Yes (panel_utils.py line 215) | PASS |
| cal_yr_qtr | Yes (cal_yr*10+cal_qtr) | Yes (panel_utils.py line 217) | PASS |

### Completeness Check
- **Every variable from MODEL_SPECS in dictionary?** DSPREAD (DV) + 4 IVs + 8 base + 4 extended = 17. All present. PASS.
- **Every variable from BASE_CONTROLS and EXTENDED_CONTROLS in dictionary?** All 12 present. PASS.
- **FE columns in dictionary?** gvkey, ff12_code, cal_yr, cal_yr_qtr. All present. PASS.

**Phase 6 Result: 22/22 PASS**

---

## PHASE 7: FACTUAL ACCURACY -- SECTIONS F, G, H

### F-CHECK: Data Pipeline

**F1. Dependency Chain:**
- 7 numbered steps: raw inputs, engine loading, panel builder, runner loading, sample filtering, regression estimation, table generation. All verified against code. PASS.

**F2. Data Engines:**
- CRSPEngine (get_raw_daily_data): provides DSPREAD, PreCallSpread, StockPrice, Turnover. Verified: BidAskSpreadChangeBuilder uses `engine.get_raw_daily_data()` (builder line 76). StockPriceBuilder and TurnoverBuilder also use raw daily data. PASS.
- CRSPEngine (get_data): provides Volatility. Verified: VolatilityBuilder uses `CRSPEngine.get_data()` (separate cache `_cache` at CRSPEngine line 453). PASS.
- CompustatEngine: provides Size, TobinsQ, ROA, BookLev, CapexAt, DividendPayer, OCF_Volatility. Verified: all builders import from CompustatEngine. PASS.
- LinguisticEngine: provides 4 uncertainty IVs. Verified: builders import from LinguisticEngine. PASS.
- IbesEngine: provides SurpDec -> AbsSurpDec. Verified: EarningsSurpriseBuilder uses IbesEngine. PASS.

**F3. Merge Operations:**
- 16 panel builder merges documented, all on `file_name` with `left` join and zero row-delta enforced.
- Code verification: Panel builder lines 153-170 show the merge loop. Every builder result is merged via `panel.merge(data, on="file_name", how="left")` with delta check `if delta != 0: raise ValueError`. PASS.
- Within-builder merges (CCM linkage + per-year CRSP): builder line 185 (manifest to CCM on gvkey), line 309-314 (year_calls to year_crsp on permno_int=PERMNO, inner). Documented correctly. PASS.

### G-CHECK: Outputs

**G1. Stage 3 Outputs:**
| Claimed File | Code Evidence | Match |
|---|---|---|
| h14_bidask_spread_panel.parquet | Panel builder line 223-224: `panel.to_parquet(panel_path)` | PASS |
| summary_stats.csv | Panel builder line 230-231: `stats_df.to_csv(stats_path)` | PASS |
| run_manifest.json | Panel builder line 235-244: `generate_manifest(...)` | PASS |
| report_step3_h14.md | Panel builder line 294: `report_path = out_dir / "report_step3_h14.md"` | PASS |

**G2. Stage 4 Outputs:**
| Claimed File | Code Evidence | Match |
|---|---|---|
| h14_bidask_spread_table.tex | Runner line 532: `tex_path = out_dir / "h14_bidask_spread_table.tex"` | PASS |
| model_diagnostics.csv | Runner line 569-570: `diag_path = out_dir / "model_diagnostics.csv"` | PASS |
| summary_stats.csv | Runner line 720: `output_csv=out_dir / "summary_stats.csv"` | PASS |
| summary_stats.tex | Runner line 721: `output_tex=out_dir / "summary_stats.tex"` | PASS |
| sample_attrition.csv | attrition_table.py line 47: writes `sample_attrition.csv` | PASS |
| sample_attrition.tex | attrition_table.py line 51: writes `sample_attrition.tex` | PASS |
| regression_results_col{1-6}.txt | Runner line 555: `f"regression_results_col{col_num}.txt"` (iterates 6 specs) | PASS |
| report_step4_H14.md | Runner line 652: `report_path = out_dir / "report_step4_H14.md"` | PASS |
| run_manifest.json | Runner line 762-772: `generate_manifest(...)` | PASS |

- **Extra files in doc not written by code?** No. PASS.
- **Files written by code not in doc?** No. PASS.

### H-CHECK: Outlier/Missing Treatment

**H1. Winsorization:**
- Compustat vars by fiscal year: Code confirms `_winsorize_by_year(comp[col], year_col)` where `year_col = comp["fyearq"]` (CompustatEngine line 1133-1136). Doc correctly says "1%/99% by fiscal year". PASS.
- CRSP Volatility by calendar year: Code confirms `winsorize_by_year(result_with_year, CRSP_RETURN_COLS, year_col="year")` where year = start_date.dt.year (CRSPEngine lines 444-446). PASS.
- Panel builder pooled: Code confirms `winsorize_pooled(panel, ["DSPREAD", "PreCallSpread", "StockPrice", "Turnover", "AbsSurpDec"])` at panel builder line 203. PASS.
- Linguistic IVs NOT winsorized: Not in any winsorize list. PASS.
- DividendPayer NOT winsorized: In CompustatEngine `skip_winsorize` set (line 1124). PASS.

**H2. Missing Data Policy:**
- Complete-case deletion: Runner line 263-264. PASS.
- Inf replaced: Runner line 252: `df.replace([np.inf, -np.inf], np.nan)`. PASS.
- BidAskSpreadChangeBuilder min days: builder lines 300-302 (min_pre=min_post=2), lines 404-409 (filter applied). PASS.

**H3. Transformations:**
- Size = ln(atq): verified in CompustatEngine. PASS.
- AbsSurpDec = abs(SurpDec): panel builder line 187. PASS.
- StockPrice = abs(PRC): CRSPEngine line 92. PASS.
- No centering/z-scoring documented, none found in code. PASS.

**Phase 7 Result: 9/9 PASS**

---

## PHASE 8: FACTUAL ACCURACY -- SECTION I (Table Generator Entry)

- **"id" = "H14":** Code line 366: `"id": "H14"`. PASS.
- **"tail" = "one":** Code line 374: `"tail": "one"`. PASS.
- **"hyp_dir" = ">":** Code line 375: `"hyp_dir": ">"`. PASS.
- **"cols" = 6:** Code line 370: `"cols": 6`. PASS.
- **"dvs" = [("DSPREAD", 6)]:** Code lines 371-373: `"dvs": [("DSPREAD", 6)]`. PASS.
- **Main loop line number:** Doc claims "falls through to generate_table() (standard 4-IV suite handler) in the main loop at line 1215." Code: `for suite in SUITES:` is at line 1234. `generate_table(suite)` call is at line 1259. **FAIL -- wrong line number.**
  - The factual claim about behavior is correct (no `type` key, falls through to `generate_table`), but the line reference is wrong.

**Phase 8 Result: 5/6 PASS**

---

## PHASE 9: FACTUAL ACCURACY -- SECTION K (Model-Family Addendum)

### K1: PanelOLS Specifics

**Industry FE specs (cols 1, 3, 5):**
- entity_effects=False: Code line 325. PASS.
- time_effects=True: Code line 326. PASS.
- other_effects=df_panel["ff12_code"]: Code line 327. PASS.
- drop_absorbed=True: Code line 328. PASS.
- check_rank=False: Code line 329. PASS.
- SE: cov_type="clustered", cluster_entity=True: Code line 330. PASS.

**Firm FE specs (cols 2, 4, 6):**
- EntityEffects + TimeEffects in formula: Code line 333: `f"{dv} ~ 1 + {exog_str} + EntityEffects + TimeEffects"`. PASS.
- drop_absorbed=True: Code line 334: `PanelOLS.from_formula(formula, data=df_panel, drop_absorbed=True)`. PASS.
- SE: cov_type="clustered", cluster_entity=True: Code line 335. PASS.

**Time index construction:**
- Cols 1-4 use cal_yr, cols 5-6 use cal_yr_qtr: Code line 304 and 314. PASS.

**R-squared reporting:**
- R2 = model.rsquared: Code line 353. PASS.
- Adj R2 manually computed: Code line 354: `1 - (1 - model.rsquared) * (model.nobs - 1) / model.df_resid`. PASS.

**K2-K6 marked N/A:** Correct, not PanelOLS. PASS.

**Phase 9 Result: 6/6 PASS**

---

## PHASE 10: QUALITY GATE CHECKLIST

| # | Quality Gate | Met? | Evidence |
|---|-------------|------|----------|
| 1 | Every variable in every regression spec appears in Variable Dictionary with explicit formula and source engine | **PASS** | All 17 regression variables + 4 FE columns present in Section E with formulas and sources |
| 2 | The model equation matches what the code actually estimates | **PASS** | B1 equation verified against runner exog construction (line 301) and PanelOLS specifications |
| 3 | The specification register accounts for every model column | **PASS** | 6 rows in Section C matching 6 MODEL_SPECS entries |
| 4 | The attrition cascade has row counts for each filter step | **FAIL** | Section D2 has filter descriptions but no row counts. Doc notes counts are runtime-dependent but does not provide representative counts. |
| 5 | The tail test direction matches between runner code and generate_all_tables.py | **PASS** | Runner: one-tailed beta>0 (line 364). generate_all_tables.py: tail="one", hyp_dir=">" (lines 374-375). Section B7, Section I, Section A all consistent. |
| 6 | The FE specification matches between docstring, code, and this document | **PASS** | Doc B5 matches runner code (lines 304, 314, 321-335). Panel builder docstring mentions fyearq_int but code uses cal_yr -- doc correctly notes code is truth (Known Issue #1). |
| 7 | Every merge in the panel builder is documented with join keys and type | **PASS** | F3 documents all 16 panel builder merges on file_name + 2 within-builder merges with correct keys and types |
| 8 | The output file list matches what the runner actually writes | **PASS** | G1 (4 files) + G2 (9 files) verified against code file-write operations |
| 9 | The model-family addendum is filled for the correct family only | **PASS** | K1 (PanelOLS) filled with verified claims. K2-K6 marked N/A. |
| 10 | Any claim marked [UNVERIFIED] has an explanation of what blocks verification | **PASS** | No [UNVERIFIED] markers in the document; all claims are supported by code references |

**Phase 10 Result: 9/10 PASS**

---

## PHASE 11: CROSS-REFERENCE CONSISTENCY

| Check | Sections Compared | Consistent? | Notes |
|-------|------------------|-------------|-------|
| 1. DVs in B2 match DVs in C | B2: DSPREAD. C: all 6 rows have DSPREAD. | PASS | |
| 2. DVs in C match DVs in I | C: DSPREAD x 6. I: dvs=[("DSPREAD", 6)]. | PASS | |
| 3. Controls in B4 match variables in E | B4: 8 base + 4 extended = 12 control vars. E: all 12 present with Type=Control. | PASS | |
| 4. Column count in A matches rows in C | A: 6 columns. C: 6 rows. | PASS | |
| 5. Column count in A matches "cols" in I | A: 6. I: cols=6. | PASS | |
| 6. Tail direction: A matches B7 matches I | A: one-tailed beta>0. B7: one-tailed beta>0. I: tail="one", hyp_dir=">". | PASS | |
| 7. FE in B5 matches C matches K | B5: Industry/Firm + CalYr/CalYrQtr by col. C: same mapping. K1: same split. | PASS | |
| 8. Panel index in A matches set_index in K | A: (gvkey, cal_yr) for 1-4, (gvkey, cal_yr_qtr) for 5-6. K1: same via time_col logic. | PASS | |

**Phase 11 Result: 8/8 PASS**

---

## CORRECTIONS REQUIRED

### Correction 1: Section D2 -- Add Row Counts

**Current text (D2 table structure):**
```
| Step | Filter | Description |
```

**Should be:**
```
| Step | Filter | Description | N (representative, col-1) |
```
With actual row counts from a representative run added. Alternatively, add a note that exact counts are runtime-dependent and point to `sample_attrition.csv` in the Stage 4 output directory, but the creation prompt template expects inline counts.

**Code reference:** Runner lines 753-758 show the attrition stages with actual counts for col 1. The provenance doc should include either these counts from a representative run or restructure to match the creation prompt template.

### Correction 2: Section I -- Fix Line Number

**Current text:**
> "H14 has no `"type"` key, so it falls through to `generate_table()` (standard 4-IV suite handler) in the main loop at line 1215."

**Should say:**
> "H14 has no `"type"` key, so it falls through to `generate_table()` (standard 4-IV suite handler) in the main loop at line 1234."

**Code reference:** `outputs/generate_all_tables.py` line 1234: `for suite in SUITES:`.

### Correction 3 (Optional): Section L -- Add Known Issue #8

**Add to Known Issues:**
> 8. **fyearq_int included in complete-case required list despite not being a FE column.** The runner's `prepare_regression_data` (line 241) includes `fyearq_int` in the `required` list used for complete-case filtering. However, `fyearq_int` is never used as a panel index or FE dimension (cal_yr and cal_yr_qtr are used instead). This causes rows with missing fiscal year mappings (from Compustat) to be dropped unnecessarily, potentially reducing sample size slightly.

### Correction 4 (Optional): Section L -- Note Stale Docstring

**Strengthen Known Issue #1 or add separate entry:**
The runner docstring at line 11 says "4 columns in one table" and line 46 lists `regression_results_col{1-4}.txt`, but the actual code has 6 MODEL_SPECS generating col{1-6} outputs. The provenance doc correctly documents 6 columns (following code-is-truth), but could explicitly flag this docstring staleness.

---

## ADDITIONAL NOTES

1. **BidAskSpreadChangeBuilder placebo line range:** The provenance doc Known Issue #3 cites "builder lines 439-448" for the placebo. The actual code spans lines 436-443 (logic) through 448-449 (output selection). The range is approximately correct but slightly imprecise. Not scored as a failure since the content is accurate.

2. **Panel builder attach_fyearq line reference:** The provenance doc F1 correctly distinguishes between `attach_fyearq()` (panel builder line 194) and `build_cal_yr_qtr_index()` (runner line 217). The reference to panel_utils.py lines 195-218 for `build_cal_yr_qtr_index` is also correct.

3. **Double winsorization avoidance for Volatility:** The provenance doc Known Issue #5 correctly documents that Volatility is winsorized per-year at CRSPEngine level and is NOT in the panel builder's `winsorize_cols` list. This prevents double winsorization. Verified against panel builder line 202 (Volatility not in list) and CRSPEngine lines 444-446 (winsorized there). Correct.

4. **Closing vs high-low spread variants:** The provenance doc Known Issue #2 correctly notes that the builder computes both `delta_spread` (ASKHI/BIDLO) and `delta_spread_closing` (ASK/BID), and only the closing variant is renamed to DSPREAD. Verified at panel builder lines 180-183 and builder lines 327-348 vs 340-348.
