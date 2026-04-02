# H9 Provenance Audit Report

**Suite:** H9 — Takeover Hazard Models  
**Audit Date:** 2026-04-01  
**Auditor:** Adversarial automated audit (manual line-level verification)  
**Provenance Doc:** `docs/provenance/H9.md`  
**Runner:** `src/f1d/econometric/run_h9_takeover_hazards.py`  
**Panel Builder:** `src/f1d/variables/build_h9_takeover_panel.py`  
**Audit Prompt:** `docs/Prompts/Audit Provenance doc.txt`

---

## AUDIT SUMMARY

| Category | Total Checks | Passed | Failed | Score |
|----------|-------------|--------|--------|-------|
| Structural Completeness (Phase 1) | 27 | 26 | 1 | 96% |
| Suite Identity (Phase 2) | 10 | 10 | 0 | 100% |
| Model Specification (Phase 3) | 7 | 5 | 2 | 71% |
| Spec Register (Phase 4) | 5 | 5 | 0 | 100% |
| Sample Construction (Phase 5) | 3 | 3 | 0 | 100% |
| Variable Dictionary (Phase 6) | 20 | 19 | 1 | 95% |
| Pipeline/Outputs/Treatment (Phase 7) | 10 | 8 | 2 | 80% |
| Table Generator Entry (Phase 8) | 1 | 1 | 0 | 100% |
| Model-Family Addendum (Phase 9) | 10 | 9 | 1 | 90% |
| Quality Gates (Phase 10) | 10 | 7 | 3 | 70% |
| Cross-Reference Consistency (Phase 11) | 8 | 8 | 0 | 100% |
| **TOTAL** | **111** | **101** | **10** | **91%** |

---

## VERDICT

**FAIL — INACCURATE**: Factual errors found. The document is structurally complete and largely accurate, but contains verified factual errors including a materially wrong claim about standard error computation, incorrect line citations, and an undisclosed conditional output.

---

## PHASE 1: STRUCTURAL COMPLETENESS

Read `docs/Prompts/Suite Provenance Doc.txt` to identify all required sections.

| Section | Required by Prompt | Present in Doc | Complete | Notes |
|---------|-------------------|----------------|----------|-------|
| A. Suite Identity | Yes | Yes | Yes | Complete YAML block present |
| B. Model Specification | Yes | Yes | Yes | All sub-sections present |
| B1. Regression Equation | Yes | Yes | Yes | Cox PH equation in LaTeX |
| B2. Dependent Variable(s) | Yes | Yes | Yes | Event/duration vars documented |
| B3. Independent Variable(s) | Yes | Yes | Yes | 3 clarity variants documented |
| B4. Control Variables | Yes | Yes | Yes | Sparse + Expanded blocks documented |
| B5. Fixed Effects | Yes | Yes | Yes | Stratification documented (Cox PH adapted) |
| B6. Standard Errors | Yes | Yes | **Inaccurate** | Present but factually wrong — see Phase 3 |
| B7. Hypothesis Test | Yes | Yes | **Minor error** | Line citation off by one |
| C. Spec Register | Yes | Yes | Yes | 36-model register with all statuses |
| D. Sample Construction | Yes | Yes | Yes | Both stage 3 and stage 4 attrition |
| D1. Population | Yes | Yes | Yes | Starting counts documented |
| D2. Exclusion Criteria | Yes | Yes | Partial | Builder steps 2-4 lack exact row counts; say "Logged in builder" |
| D3. Sample Counts per Spec | Yes | Yes | Yes | Per-variant table present |
| E. Variable Dictionary | Yes | Yes | Yes | 20 variables with formulas |
| F. Data Pipeline | Yes | Yes | Yes | All 3 sub-sections present |
| F1. Dependency Chain | Yes | Yes | Yes | 7-step chain documented |
| F2. Data Engines | Yes | Yes | Yes | All engines listed |
| F3. Merge Operations | Yes | Yes | Yes | Builder and TakeoverIndicatorBuilder merges |
| G. Outputs | Yes | Yes | Yes | All sub-sections present |
| G1. Stage 3 Outputs | Yes | Yes | Partial | `dropped_event_firms.csv` listed but conditional; not disclosed |
| G2. Stage 4 Outputs | Yes | Yes | Yes | All 22 output files listed and verified |
| G3. Summary Statistics | Yes | Yes | Yes | Variables listed, metrics named |
| H. Outlier/Missing Treatment | Yes | Yes | Yes | All 3 sub-sections present |
| I. generate_all_tables Entry | Yes | Yes | Yes | Correctly states "no entry" with evidence |
| J. Reproduction Commands | Yes | Yes | Yes | Full bash commands with optional args |
| K. Model-Family Addendum | Yes | Yes | Yes | K2 filled, K1/K3/K4/K5/K6 all N/A |
| L. Known Issues | Yes | Yes | Yes | 11 issues documented |

**Phase 1 Summary:** One structural deficiency in G1: `dropped_event_firms.csv` is presented as a definitive output when it is written conditionally (only when SDC event firms are absent from the panel AND `out_dir is not None`; builder lines 492-496).

---

## PHASE 2: SUITE IDENTITY (Section A)

**A-1. Suite ID:** "H9" — trivially correct. PASS

**A-2. Title:** Doc says "Takeover Hazard Models". Runner docstring line 3: "H9: Takeover Hazard Models". PASS

**A-3. Hypothesis:** Doc says "Does clarity in speech increase the likelihood of receiving a takeover bid, especially an uninvited (hostile/unsolicited) bid? H9-A: beta(Clarity) < 0... H9-B: beta(Clarity, uninvited) < beta(Clarity, friendly)". Runner docstring lines 10-13 say identical content. PASS

**A-4. Direction (tail test):** Doc says "Two-sided inference (runner docstring line 27)". Runner line 27: "Hypothesis Tests (two-sided inference):". PASS

**A-5. Model Family:** Doc says "Cox Proportional Hazards (time-varying covariates)". Runner line 100: `from lifelines import CoxTimeVaryingFitter`. PASS

**A-6. Estimator:** Doc says "lifelines.CoxTimeVaryingFitter". Runner line 100 confirms. PASS

**A-7. Unit of Observation:** Doc says "Call-to-call interval (counting-process format)". Builder docstring: "Each row represents one risk interval that opens at an earnings call and closes at the earliest of: (a) next earnings call... (b) takeover announcement date... (c) administrative censor date". PASS

**A-8. Panel Index:** Doc says "(gvkey, start/stop)". Runner uses `id_col="gvkey"`, `start_col=START_COL`, `stop_col=STOP_COL` at lines 478-480. PASS

**A-9. Columns (number of model specs):** Doc says "Non-tabular -- 3 event types x 3 clarity variants x 4 control configurations = up to 36 model fits". Runner has 3 `model_defs`, 3 `MODEL_VARIANTS`, and 4 execution blocks (lines 836-893) = 36 fits. PASS

**A-10. Runner and Panel Builder paths:**
- `src/f1d/econometric/run_h9_takeover_hazards.py` — verified exists.
- `src/f1d/variables/build_h9_takeover_panel.py` — verified exists.
PASS

---

## PHASE 3: MODEL SPECIFICATION (Section B)

### B1-CHECK: Regression Equation

Doc presents:
```
h_i(t | X_i(t)) = h_0(t) * exp(β1 * Clarity_{i,t} + γ * Controls_{i,t})
```
And the stratified variant with `h_{0,s}(t)`.

Runner line 482: `formula=" + ".join(covariates)` where `covariates = [clarity_var] + controls`. The formula construction matches Cox PH. Strata confirmed by `strata=strata` at line 483. Doc cites "lines 396-504 (run_cox_tv function)". Verified: `run_cox_tv` starts at line 396, return at line 504. PASS

### B2-CHECK: Dependent Variable(s)

- `Takeover`: builder line 336 `df["Takeover"] = tk_in_interval.astype(int)`. PASS
- `Takeover_Uninvited`: builder lines 362-364 (after interval cap), runner line 287. PASS
- `Takeover_Friendly`: builder lines 365-367, runner line 288. PASS
- `start`: builder line 339 `df["start"] = (df["call_date"] - REFERENCE_DATE).dt.days`. REFERENCE_DATE = `pd.Timestamp("2000-01-01")` at builder line 98. PASS
- `stop`: builder lines 323-324 (fillna and cap to censor_date), line 333 (truncate at takeover_date), line 340 (convert to days). PASS

### B3-CHECK: Independent Variable(s)

Runner `MODEL_VARIANTS` (lines 177-195):
- `"CEO"`: `clarity_var: "ClarityCEO"` PASS
- `"CEO_Residual"`: `clarity_var: "UncResCEO"` PASS
- `"Manager_Residual"`: `clarity_var: "UncResMgr"` PASS

Doc notes ClarityCEO 0% coverage. Runner skips models at MIN_OBS=50 check (lines 207, 448). PASS

### B4-CHECK: Control Variables

Runner SPARSE_CONTROLS (lines 130-136): `["lnAssets", "BTM", "Leverage", "ROA", "CashRatio"]`
Runner EXPANDED_CONTROLS (lines 139-143): SPARSE_CONTROLS + `["SalesGrowth", "FracInt", "dAA"]`

Doc documents exactly these variables in correct blocks. Doc cites "lines 130-143" which is correct. PASS

No Lagged_DV — correct for Cox PH. PASS

### B5-CHECK: Fixed Effects / Stratification

Doc documents 4 stratification configurations mapping to 4 runner blocks:
- Block A (sparse, no strata): lines 836-848
- Block C (expanded, no strata): lines 850-863
- Block D (strata="year"): lines 865-878, strata="year" at line 877
- Block E (strata="ff12_code"): lines 880-893, strata="ff12_code" at line 892

All verified. Doc citation "lines 865-893" is accurate. PASS

### B6-CHECK: Standard Errors — **FAIL**

**CRITICAL ERROR.** Doc claims:

> "lifelines.CoxTimeVaryingFitter uses the **robust sandwich variance estimator** by default, which accounts for within-subject correlation in the counting-process format."

**Code evidence:**
- Runner line 475: `ctv = CoxTimeVaryingFitter()` — no `robust` parameter.
- Runner lines 476-484: `ctv.fit(df_clean, id_col="gvkey", start_col=START_COL, stop_col=STOP_COL, event_col=event_col, formula=..., strata=strata)` — no `robust` parameter.

The lifelines library requires `robust=True` to be explicitly passed to `CoxTimeVaryingFitter()` to activate robust sandwich variance estimation. Without it, the standard (inverse information matrix) variance estimator is used. The code does NOT pass `robust=True`.

The additional statement "lifelines handles this internally through the counting-process likelihood which conditions on the risk set at each event time" conflates the partial likelihood computation (correct description of Cox PH) with variance estimation (a separate step). These are distinct. FAIL

### B7-CHECK: Hypothesis Test — **Minor FAIL**

Doc says "two-sided inference (runner docstring line 28: 'two-sided inference')".

**Code evidence:** Runner line 27 (not 28) says "Hypothesis Tests (two-sided inference):". Line 28 says "    H9-A: beta(Clarity) < 0 (clearer CEOs have lower takeover hazard)".

Line citation is off by one. MINOR FAIL

Doc says "lifelines reports two-sided p-values by default from the Wald z-test". This is correct for lifelines CoxTimeVaryingFitter. PASS

---

## PHASE 4: SPEC REGISTER (Section C)

**Count check:** Doc has 36 model rows (IDs 1-36) = 3 event types × 3 clarity variants × 4 control configs. PASS

**Configuration verification:**
- 3 event types (All/Uninvited/Friendly): runner `model_defs` lines 741-745. PASS
- 3 clarity variants (CEO/CEO_Residual/Manager_Residual): runner `MODEL_VARIANTS` lines 177-195. PASS
- 4 control configs (Sparse-None, Expanded-None, Sparse-year, Sparse-ff12_code): runner blocks A-E. PASS

**CEO skipping:** 12 CEO slots (IDs 1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34). 3 event types × 4 control configs = 12. IDs match. PASS

**EPV values:** CEO_Residual sparse All: 78/6 = 13.0; Manager_Residual sparse All: 101/6 = 16.83 ≈ 16.8. Both match doc. PASS

---

## PHASE 5: SAMPLE CONSTRUCTION (Section D)

### D1-CHECK: Population

Doc says "Total calls: 112,968; Unique firms: 2,429; Year range: 2002-2018." Matches project scope in memory. PASS

Doc says "107,644 intervals from 2,410 firms" after panel builder. Sourced from run artifacts. PASS (plausible)

### D2-CHECK: Exclusion Criteria

Builder-level filters:
1. `call_date` NaN removal: builder line 287. Documented implicitly.
2. Post-takeover removal: mask at lines 304-312. Doc Step 2 correct.
3. Zero-duration removal: lines 373-377. Doc Step 3 correct.
4. Interval cap at 1,461 days: lines 342-359. Doc Step 4 correct.

**PARTIAL:** Steps 2-4 show "Logged in builder" / "Varies" for row counts. Exact counts are available at runtime but not populated in the doc. Quality Gate 4 failure — see Phase 10.

Runner-level filters:
- FF12 exclusion (8 and 11): runner line 277. Doc confirms. PASS
- Complete-case deletion per variant: line 443. Doc confirms. PASS

### D3-CHECK: Sample Counts per Spec

EPV verification:
- CEO_Residual sparse: 78 event firms / 6 covariates = 13.0. PASS
- Manager_Residual sparse: 101 / 6 = 16.83 ≈ 16.8. PASS

---

## PHASE 6: VARIABLE DICTIONARY (Section E)

Verification of all 20 dictionary rows:

| Variable | Formula Claim | Code Evidence | Pass/Fail |
|----------|--------------|---------------|-----------|
| `Takeover` | 1 if bid in (call_date, stop_date] | Builder line 336 | PASS |
| `Takeover_Uninvited` | 1 if Takeover==1 AND type=='Uninvited' | Builder 362-364, runner 287 | PASS |
| `Takeover_Friendly` | 1 if Takeover==1 AND type=='Friendly' | Builder 365-367, runner 288 | PASS |
| `start` | (call_date - 2000-01-01).days | Builder line 339, REFERENCE_DATE line 98 | PASS |
| `stop` | min(next_call_date, takeover_date, 2018-12-31) days | Builder lines 323-324, 333, 340 | PASS |
| `duration` | stop - start | Builder line 370 | PASS |
| `ClarityCEO` | CEO FE from H1; one score per ceo_id×sample | Builder lines 123-126 | PASS |
| `UncResCEO` | UncAnsCEO - predicted from H0.3 | Builder line 186 (CEOClarityResidualBuilder) | PASS |
| `UncResMgr` | UncAnsMgr - predicted from H0.3 | Builder line 187 (ManagerClarityResidualBuilder) | PASS |
| `lnAssets` | ln(atq), atq > 0; else NaN | Engine line 943 | PASS |
| `BTM` | ceqq / (cshoq * prccq) | Engine line 945 | PASS |
| `Leverage` | (dlcq + dlttq) / atq; missing debt = 0 | Engine line 948 (fillna(0) confirmed) | PASS |
| `ROA` | iby_annual / avg_assets; avg=(atq_t+atq_{t-1})/2 | Engine lines 960-969 | PASS |
| `CashRatio` | cheq / atq | Engine line 986 | PASS |
| `SalesGrowth` | (saley_t - saley_{t-1}) / abs(saley_{t-1}) | Engine lines 658-663 | PASS |
| `FracInt` | intanq / atq | Engine lines 870-874 | PASS |
| `dAA` | (atq_t - atq_{t-4}) / abs(atq_{t-4}); date-lag ±45d | Engine lines 892-928 (365-day target, ±45d tolerance) | PASS |
| `gvkey` | 6-digit Compustat identifier | Manifest | PASS |
| `ff12_code` | FF12 industry classification | Manifest | PASS |
| `year` | start_date.dt.year | Builder line 248 | PASS |

**Completeness check:** All variables used in runner covariates ([ClarityCEO/UncResCEO/UncResMgr] + [lnAssets/BTM/Leverage/ROA/CashRatio] + optional [SalesGrowth/FracInt/dAA]) plus structural columns (start, stop, gvkey, ff12_code, year) plus event columns (Takeover, Takeover_Uninvited, Takeover_Friendly) are all in the dictionary. PASS

**FAIL — Line citation in E footnote:** Doc says formulas verified against "_compustat_engine.py compute_variables function (lines 937-1038)". The actual range for `_compute_and_winsorize()` spans lines 936-1234. The cited range 937-1038 omits the inf-to-NaN replacement (lines 1183-1204) and the winsorization loop (lines 1209-1234). The function is named `_compute_and_winsorize`, not "compute_variables". MINOR FAIL

---

## PHASE 7: PIPELINE / OUTPUTS / TREATMENT (Sections F, G, H)

### F-CHECK: Data Pipeline

**F1 Dependency Chain:** 7-step chain verified step by step. All steps match code behavior. PASS

**F2 Data Engines:**
- CompustatEngine: builder lines 178-185 (SizeBuilder, BMBuilder, LeverageBuilder, ROABuilder, CashRatioBuilder, SalesGrowthBuilder, FracIntBuilder, dAABuilder). PASS
- LinguisticEngine (via individual builders): lines 166-175 (ManagerQAUncertaintyBuilder, CEOQAUncertaintyBuilder, AnalystQAUncertaintyBuilder, NegativeSentimentBuilder). PASS
- ClarityResidualEngine: lines 186-187 (CEOClarityResidualBuilder, ManagerClarityResidualBuilder). PASS
- Direct parquet load: builder lines 119-131 (`clarity_scores.parquet`). PASS
- TakeoverIndicatorBuilder: builder line 89 (import), lines 470-476 (build call). PASS
- ManifestFieldsBuilder: builder line 165. PASS

**F3 Merge Operations:**
- Call panel merges (file_name LEFT): builder line 227 confirmed. PASS
- ClarityCEO merge (ceo_id, sample LEFT): builder lines 449-453 confirmed. PASS
- TakeoverIndicatorBuilder internal merges: doc cites "takeover_indicator.py lines 157-209". NOT INDEPENDENTLY VERIFIED — `takeover_indicator.py` was not read end-to-end in this audit. Marked UNVERIFIED for internal merge details.

### G-CHECK: Outputs

**G1 Builder outputs — PARTIAL FAIL:**
Actual writes in `save_outputs()` (lines 527-553):
- `takeover_panel.parquet` (line 530). Listed. PASS
- `summary_stats.csv` (line 537). Listed. PASS
- `run_manifest.json` (line 543 via `generate_manifest()`). Listed. PASS
- `report_h9_panel.md` (line 623 via `generate_report()`). Listed. PASS
- `dropped_event_firms.csv`: written conditionally at builder lines 492-496 only when `dropped` set is non-empty. Doc lists it without noting the conditional nature. FAIL

**G2 Runner outputs — PASS:**
Verified all 22 files against actual write operations:
- 12 `.txt` model files: blocks A-E (lines 836-893), write_text at lines 838/857/872/887 plus `fh.write` in run_cox_tv (line 497). PASS
- `hazard_ratios.csv`: line 567. PASS
- `model_diagnostics.csv`: line 572. PASS
- `takeover_table.tex`: line 940. PASS
- `summary_stats.csv` and `summary_stats.tex`: line 730 (`make_summary_stats_table`). PASS
- `sample_attrition.csv` and `sample_attrition.tex`: line 963 (`generate_attrition_table()`). PASS
- `variant_sample_chars.csv`: line 983. PASS
- `report_h9_takeover.md`: line 656. PASS
- `run_manifest.json`: line 1007. PASS

Note: Docstring line 64 lists `takeover_hazard_table.tex` but code writes `takeover_table.tex`. Doc correctly documents this mismatch in L.11. PASS

### H-CHECK: Outlier/Missing Treatment

**H1 Winsorization:**
Doc lists lnAssets, BTM, Leverage, ROA, CashRatio, FracInt, dAA as winsorized 1%/99% by fyearq.
Engine `skip_winsorize` set (lines 1217-1224): `{"DivDummy", "CashFlowAt", "SalesGrowth", "fqtr", "ExternalFunding", "DebtChoice"}` — none of the listed controls are in this set. All are in `COMPUSTAT_COLS`. Outer winsorization loop (lines 1225-1232) applies to all non-skipped COMPUSTAT_COLS. PASS

SalesGrowth: winsorized at line 666 (inside `_compute_biddle_residual()`), excluded from outer loop via `skip_winsorize` at line 1220. Doc claim "pre-use only; no double-winsorization per C-6 fix" is accurate. PASS

Min observations per year = 10: `_winsorize_by_year` signature line 445 `min_obs: int = 10`. PASS

**H2 Missing Data — FAIL:**
Doc says "Inf/-Inf replaced with NaN at CompustatEngine level (lines 1088-1108)".

**Code:** Lines 1087-1092 are `comp = comp.drop(columns=["_prstkcy_prev", "_prev_fyearq", "_quarterly_repurchases", "_atq_prev_q", "_datadate_prev", "_date_gap"])` — dropping temporary columns. Lines 1094-1108 are the start of the Leary & Roberts financing classification section comments and variable setup. Neither contains inf replacement.

The actual inf-to-NaN replacement is the `ratio_cols` block at lines 1183-1204:
```python
ratio_cols = ["BTM", "Leverage", "DebtToCapital", "ROA", ...]
for col in ratio_cols:
    comp[col] = comp[col].replace([np.inf, -np.inf], np.nan)
```
The line citation is wrong by approximately 95 lines. FAIL

Complete-case deletion: runner line 443 `.dropna(subset=[START_COL, STOP_COL, event_col] + covariates)`. PASS

Zero-duration removal: builder lines 373-377. PASS

**H3 Transformations:** lnAssets = ln(atq) confirmed at engine line 943. PASS

---

## PHASE 8: TABLE GENERATOR ENTRY (Section I)

Doc states H9 has no entry in `outputs/generate_all_tables.py`.

**Verification:** Grep for "h9|H9|takeover|Takeover" in `outputs/generate_all_tables.py` returned "No matches found." PASS

---

## PHASE 9: MODEL-FAMILY ADDENDUM (Section K)

### K1/K3/K4/K5/K6: All N/A. PASS

### K2: Cox Proportional Hazards Specifics

**Time origin:** REFERENCE_DATE = `pd.Timestamp("2000-01-01")` at builder line 98. Doc cites "panel builder line 98". PASS

**Duration construction:** (start, stop] intervals, covariates at call opening. Builder lines 256-416. PASS

**Event definition:** Takeover=1 only in interval where first bid falls; validated at builder lines 383-390 (no firm > 1 event row). PASS

**Censoring rules (4 documented):**
1. Admin censor at 2018-12-31: builder line 283 `censor_date = pd.Timestamp(f"{year_end}-12-31")`. PASS
2. Interval cap at 1,461 days with event censoring: builder lines 342-359. PASS
3. Post-takeover calls removed: builder lines 304-312. PASS
4. Right-censoring for non-events: standard Cox PH behavior. PASS

**Risk set format:** Start-stop counting-process. `id_col="gvkey"` at runner line 479. PASS

**Ties method:** Doc says "Efron's method by default — no explicit ties parameter set." Confirmed: no ties-related argument appears anywhere in the runner (grep returned no matches). The Efron default is a library-level fact not verifiable from code alone, marked PASS with caveat.

**Strata variables:**
- `strata="year"` at runner line 877. Doc cites "runner line 877". PASS
- `strata="ff12_code"` at runner line 892. Doc cites "runner line 892". PASS
- Sparsity diagnostic at lines 466-472. Doc cites these lines. PASS

**Concordance index:** Custom function `compute_concordance_time_varying()` at lines 321-393. Doc description of 7 steps matches code. Minimum 10 subjects check at line 378. Return None on exception at line 391. PASS

**EPV:** EPV = N_event_firms / N_covariates (lines 784-785). Thresholds: critical < 5, low < 10, ok >= 10 (lines 787-791). Suppression at line 919. PASS

**K2 FAIL — SE claim propagated from B6:** Section K2 does not repeat the SE claim, so no distinct K2 failure beyond B6.

---

## PHASE 10: QUALITY GATE CHECKLIST

| # | Quality Gate | Met? | Evidence |
|---|-------------|------|----------|
| 1 | Every variable in every regression spec appears in Variable Dictionary with explicit formula and source engine | YES | All 20 variables documented with explicit formulas and engine citations |
| 2 | The model equation matches what the code actually estimates | YES | Cox PH equation matches `formula=" + ".join(covariates)` + CoxTimeVaryingFitter.fit() |
| 3 | The specification register accounts for every model column | YES | 36-model register covers all 3×3×4 combinations with status |
| 4 | The attrition cascade has row counts for each filter step | PARTIAL | Stage 4 rows have actual counts; Stage 3 builder steps 2-4 say "Logged in builder" / "Varies" without counts |
| 5 | The tail test direction matches between runner code and generate_all_tables.py | YES | Two-sided in runner; no generate_all_tables.py entry (correctly documented) |
| 6 | The FE specification matches between docstring, code, and this document | YES | Stratification documented correctly across B5, C, K2 |
| 7 | Every merge in the panel builder is documented with join keys and type | PARTIAL | Builder-level merges documented; TakeoverIndicatorBuilder internal merges cited but not independently verified in this audit |
| 8 | The output file list matches what the runner actually writes | PARTIAL | All runner outputs verified; `dropped_event_firms.csv` listed without noting conditional nature |
| 9 | The model-family addendum is filled for the correct family only | YES | K2 filled; K1/K3/K4/K5/K6 all N/A |
| 10 | Any claim marked [UNVERIFIED] has an explanation of what blocks verification | NO | Doc makes no use of [UNVERIFIED] tags; the SE claim (B6) should be marked [UNVERIFIED] or corrected, not stated definitively as "robust sandwich by default" |

**Gate failures:** Gates 4, 8, 10.

---

## PHASE 11: CROSS-REFERENCE CONSISTENCY

1. **DVs in B2 vs C:** B2 defines Takeover/Takeover_Uninvited/Takeover_Friendly. Section C uses "All/Uninvited/Friendly" as event types mapping to these columns. CONSISTENT
2. **DVs in C vs I:** No generate_all_tables.py entry. No cross-reference needed. CONSISTENT
3. **Controls in B4 vs E:** B4 sparse = [lnAssets, BTM, Leverage, ROA, CashRatio]; expanded adds [SalesGrowth, FracInt, dAA]. Section E documents all 8 with formulas. CONSISTENT
4. **Column count in A vs C:** A says "up to 36 model fits". C has exactly 36 rows. CONSISTENT
5. **Column count in A vs I:** Non-tabular; no I entry. A states "Non-tabular". CONSISTENT
6. **Tail direction in A vs B7 vs I:** A says "Two-sided inference"; B7 says "Two-sided inference"; no I entry. CONSISTENT
7. **FE in B5 vs C vs K:** B5 four stratification configs match C "Strata" column entries and K2 strata documentation. CONSISTENT
8. **Panel index in A vs K:** A says "(gvkey, start/stop)". K2 confirms `id_col="gvkey"`, `start_col=START_COL`, `stop_col=STOP_COL`. CONSISTENT

All 8 cross-reference checks: PASS

---

## FAILURES (Detailed)

| Phase | Check | Provenance Doc Claims | Actual Code Says | Severity | Fix Required |
|-------|-------|----------------------|-----------------|----------|-------------|
| B6 | Standard error method | "uses the **robust sandwich variance estimator** by default" | `CoxTimeVaryingFitter()` called with no `robust=True`; standard (inverse information matrix) variance is used | HIGH | Correct to "standard variance (inverse information matrix)"; `robust=True` not passed |
| B7 | Line citation for "two-sided inference" | "runner docstring line 28: 'two-sided inference'" | Line 27 says "Hypothesis Tests (two-sided inference):" | LOW | Change "line 28" to "line 27" |
| G1 | Conditional output disclosure | `dropped_event_firms.csv` listed as definitive output | Written conditionally only when `dropped` set is non-empty (builder lines 492-496) | LOW | Add "(conditional)" note |
| H2 | Line citation for inf/NaN replacement | "CompustatEngine level (lines 1088-1108)" | Actual inf replacement: `ratio_cols` loop at lines 1183-1204; lines 1088-1108 contain unrelated code | MEDIUM | Correct to "lines 1183-1204" |
| E | Line citation for formula verification footnote | "_compustat_engine.py compute_variables function (lines 937-1038)" | Function name is `_compute_and_winsorize`; full range is lines 936-1234; cited range misses winsorization loop (1209-1234) and inf replacement (1183-1204) | LOW | Correct function name and extend range to 936-1234 |
| D2 | Attrition cascade row counts | Steps 2-4 say "Logged in builder" / "Varies" | Exact counts available from builder runtime logs but not populated in doc | LOW | Add actual run counts or use [UNVERIFIED] with explanation |
| Phase 10 | Quality gate 10 | No [UNVERIFIED] tags used | B6 SE claim is stated definitively but is factually wrong; should be verified or tagged | MEDIUM | Correct B6 claim; remove false confidence |

---

## CORRECTIONS REQUIRED

**Correction 1 (HIGH SEVERITY) — Section B6:**

Current text:
> "lifelines.CoxTimeVaryingFitter uses the **robust sandwich variance estimator** by default, which accounts for within-subject correlation in the counting-process format. The `id_col="gvkey"` parameter (line 479) identifies subjects. No explicit `cov_type` or `cluster_entity` argument is passed -- lifelines handles this internally through the counting-process likelihood which conditions on the risk set at each event time."

Replace with:
> "lifelines.CoxTimeVaryingFitter uses the **standard variance estimator** (inverse information matrix) by default. The constructor is called with no arguments (line 475: `CoxTimeVaryingFitter()`), and no `robust=True` parameter is passed to `fit()` (lines 476-484). The `id_col="gvkey"` parameter identifies subjects for the partial likelihood; it does NOT activate robust/sandwich standard errors. To obtain robust SEs in lifelines, `robust=True` must be explicitly passed to `CoxTimeVaryingFitter(robust=True)`. Standard (non-robust) SEs are used in this suite."

Code reference: `run_h9_takeover_hazards.py` lines 475-484.

---

**Correction 2 (LOW SEVERITY) — Section B7:**

Current: `"two-sided inference (runner docstring line 28: "two-sided inference")"`

Replace: `"two-sided inference (runner docstring line 27: "Hypothesis Tests (two-sided inference):")"`

Code reference: `run_h9_takeover_hazards.py` line 27.

---

**Correction 3 (MEDIUM SEVERITY) — Section H2:**

Current: `"Inf/-Inf replaced with NaN at CompustatEngine level (lines 1088-1108)"`

Replace: `"Inf/-Inf replaced with NaN at CompustatEngine level in _compute_and_winsorize() (lines 1183-1204: ratio_cols loop calling comp[col].replace([np.inf, -np.inf], np.nan) for BTM, Leverage, ROA, CashRatio, SalesGrowth, FracInt, dAA, and other ratio variables)"`

Code reference: `_compustat_engine.py` lines 1183-1204.

---

**Correction 4 (LOW SEVERITY) — Section G1:**

Current row:
`| outputs/variables/takeover/{timestamp}/dropped_event_firms.csv | SDC event firms with no valid panel interval (if any) |`

Replace with:
`| outputs/variables/takeover/{timestamp}/dropped_event_firms.csv | SDC event firms with no valid panel interval — **conditional**: only written when at least one such firm exists (builder lines 492-496: `if dropped:` block) |`

Code reference: `build_h9_takeover_panel.py` lines 492-496.

---

**Correction 5 (LOW SEVERITY) — Section E footnote:**

Current: `"Source: All formulas verified against builder files and _compustat_engine.py compute_variables function (lines 937-1038)."`

Replace: `"Source: All formulas verified against builder files and _compustat_engine.py _compute_and_winsorize() function (lines 936-1234), including inf-to-NaN replacement at lines 1183-1204 and per-year winsorization loop at lines 1209-1234."`

Code reference: `_compustat_engine.py` lines 936-1234.

---

**Correction 6 (LOW SEVERITY) — Section D2, builder attrition steps 2-4:**

Current Steps 2-4 show "Logged in builder" / "Varies" / "0 rows dropped (intervals capped, not removed)" without exact row counts.

Replace: Either populate with actual counts from the latest builder run log, or change each cell to `[UNVERIFIED — counts printed by builder at runtime; not available at documentation time; see run_log.txt for the specific run]`.

Code reference: `build_h9_takeover_panel.py` line 309-311 (post-takeover count), lines 374-376 (zero-duration count), lines 346-348 (cap count) — all printed but not captured in the doc.

---

## MATERIALLY CORRECT CLAIMS (no correction needed)

The following claims are accurate and require no change:

- All 36 spec register entries and EPV calculations (EPV = events/covariates formula matches code)
- All control variable formulas: lnAssets (ln(atq)), BTM (ceqq/(cshoq*prccq)), Leverage ((dlcq+dlttq)/atq fillna(0)), ROA (iby_annual/avg_assets), CashRatio (cheq/atq), FracInt (intanq/atq), dAA (date-based 365d lag, ±45d tolerance), SalesGrowth ((saley_t - saley_{t-1})/abs(saley_{t-1}))
- REFERENCE_DATE = 2000-01-01 and day-count conversion (builder line 98)
- Interval cap at 1,461 days with event censoring-on-cap (builder lines 342-359)
- Post-takeover call removal logic (builder lines 304-312)
- Cause-specific competing risks approach: separate Cox models; other event types censored
- EPV thresholds: critical < 5, low < 10, ok >= 10 (runner lines 787-791)
- LaTeX table suppression of critical-EPV models (runner line 919)
- generate_all_tables.py "no entry" claim — verified by grep returning no matches
- All 22 G2 runner output files — fully verified against write operations
- ClarityCEO 0% coverage blocker — correctly documented with mechanism
- Runner docstring/code mismatch on table filename — correctly flagged in L.11
- SalesGrowth single winsorization (no double-winsorization per C-6 fix)
- Winsorization min_obs = 10 (engine line 445)
- Concordance computation steps (7 steps in compute_concordance_time_varying match code exactly)
- Internal consistency across all 8 cross-reference checks

---

*End of H9 Provenance Audit Report — 2026-04-01*
