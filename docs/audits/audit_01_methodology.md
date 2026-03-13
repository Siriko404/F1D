# Audit 01: Methodology Section (II.B)
**Date:** 2026-03-13
**Auditor:** Claude Agent
**Scope:** Lines 70-83 of thesis_draft.tex (three methodology paragraphs)
**Verdict:** PASS WITH ISSUES

---

## H0.3 Methodology Audit

### Claims Verified

- **"OLS regressions"** -- VERIFIED. Code uses `statsmodels.formula.api.smf.ols` (line 71 import, line 379 call in `run_h0_3_ceo_clarity_extended.py`).

- **"QA-section uncertainty on presentation-section uncertainty, analyst uncertainty, negative sentiment, and financial controls"** -- VERIFIED. Manager variant DV = `Manager_QA_Uncertainty_pct`, linguistic controls = `Manager_Pres_Uncertainty_pct`, `Analyst_QA_Uncertainty_pct`, `Entire_All_Negative_pct` (lines 89-93). CEO variant DV = `CEO_QA_Uncertainty_pct`, linguistic controls = `CEO_Pres_Uncertainty_pct`, `Analyst_QA_Uncertainty_pct`, `Entire_All_Negative_pct` (lines 95-99). Accurate high-level description.

- **"CEO fixed effects and year fixed effects"** -- VERIFIED. Formula at line 369: `"{dep_var} ~ C(ceo_id) + ... + C(year)"`. Both CEO and year FE are included.

- **"Standard errors clustered at the CEO level"** -- VERIFIED. Line 379-381: `smf.ols(formula, data=df_reg).fit(cov_type="cluster", cov_kwds={"groups": df_reg["ceo_id"]})`.

- **"four specifications: Manager variant and CEO variant, each in Baseline and Extended"** -- VERIFIED. MODELS dict (lines 113-138) defines exactly 4 models: `Manager_Baseline`, `Manager_Extended`, `CEO_Baseline`, `CEO_Extended`.

- **"Baseline form (replicating the original study's control set: stock return, market return, EPS growth, and earnings surprise decile)"** -- VERIFIED. `BASE_FIRM_CONTROLS = ["StockRet", "MarketRet", "EPS_Growth", "SurpDec"]` (line 101).

- **"Extended form that adds firm size, book-to-market, leverage, ROA, current ratio, R&D intensity, and stock return volatility"** -- VERIFIED. `EXTENDED_CONTROLS = ["Size", "BM", "Lev", "ROA", "CurrentRatio", "RD_Intensity", "Volatility"]` (lines 103-111). All 7 match exactly.

### Issues Found

- **MINOR: "absorbed via indicator variables" is misleading terminology.**
  - **Draft says:** "CEO fixed effects and year fixed effects, both absorbed via indicator variables"
  - **Code actually does:** Uses `C(ceo_id)` and `C(year)` in the Patsy formula, which creates explicit dummy variable columns. This is NOT absorption (within-transformation / demeaning); it is explicit dummy coding.
  - **Provenance doc confirms:** "Not absorbed -- CEO and year FE estimated as explicit dummy coefficients via Patsy C() operator" (H0.3.md, section A2).
  - **Severity:** MINOR. The phrase "absorbed via indicator variables" conflates absorption (demeaning, as in `linearmodels` or `reghdfe`) with dummy-variable inclusion. Technically these produce identical coefficient estimates for the non-FE regressors, but the terminology is imprecise. A referee familiar with high-dimensional FE software would flag this.
  - **Suggested fix:** Replace "absorbed via indicator variables" with "included as indicator (dummy) variables" or simply "included via indicator variables."

---

## H7/H14 Methodology Audit

### Claims Verified

- **"linearmodels PanelOLS estimator"** -- VERIFIED. Both files import and use `from linearmodels.panel import PanelOLS` (H7 line 75, H14 line 64).

- **"firm and time fixed effects"** -- VERIFIED. Both formulas include `+ EntityEffects + TimeEffects` (H7 line 201-204, H14 line 237-241). Entity index = `gvkey`, time index = `call_quarter_int` (H7) / `quarter_index` (H14).

- **"Standard errors clustered at the firm level"** -- VERIFIED. Both use `model_obj.fit(cov_type="clustered", cluster_entity=True)` (H7 line 221, H14 line 263-266).

- **"H7: time fixed effect is a fiscal-quarter integer"** -- VERIFIED. `call_quarter_int = call_quarter.dt.year * 4 + call_quarter.dt.quarter - 1` (H7 lines 167-169). This is an integer encoding of fiscal quarters.

- **"H14: year-quarter index defined as year x 4 + quarter"** -- VERIFIED. `quarter_index = year * 4 + quarter` (H14 line 162). Exact formula match.

- **"+-3 trading days"** -- VERIFIED. H7 uses `AmihudChangeBuilder` with default `window_days=3` (`amihud_change.py` line 49). H14 uses `BidAskSpreadChangeBuilder` with default +-3 trading day windows (confirmed in panel builder docstrings and variable config). Both DV definitions: post-call [+1,+3] minus pre-call [-3,-1].

- **H7 control variables: "firm size, leverage, ROA, Tobin's Q, pre-call Amihud illiquidity, and two linguistic controls (negative sentiment and analyst uncertainty)"** -- VERIFIED. `BASE_CONTROLS = ["Entire_All_Negative_pct", "Analyst_QA_Uncertainty_pct", "Size", "Lev", "ROA", "TobinsQ", "pre_call_amihud"]` (H7 lines 97-105). All 7 variables match the draft description exactly.

- **H14 control variables: "firm size, stock price, share turnover, return volatility, pre-call spread level, and absolute earnings surprise"** -- VERIFIED with caveat (see issue below). `BASE_CONTROLS = ["Size", "StockPrice", "Turnover", "Volatility", "PreCallSpread", "AbsSurpDec"]` (H14 lines 88-95).

- **"raw linguistic uncertainty variants (CEO QA, CEO presentation, manager QA, manager presentation) as well as clarity-residual variants"** -- VERIFIED. H7 SPECS: A1 (CEO_QA), A2 (CEO_Pres), A3 (Manager_QA), A4 (Manager_Pres), B1 (CEO_Clarity_Residual), B2 (Manager_Clarity_Residual) (lines 107-116). H14 UNCERTAINTY_MEASURES: same 6 measures (lines 98-106). Both match.

### Issues Found

- **MINOR: H14 "absolute earnings surprise" is imprecise.**
  - **Draft says:** "absolute earnings surprise"
  - **Code actually uses:** `AbsSurpDec` = |SurpDec|, i.e., the absolute value of an *earnings surprise decile* (ordinal 0-5), not the raw absolute earnings surprise.
  - **Provenance doc confirms:** "|SurpDec| -- absolute value of earnings surprise decile (ordinal 0-5)" (H14.md, section A4).
  - **Severity:** MINOR. A reader might interpret "absolute earnings surprise" as the raw surprise magnitude, when it is actually the absolute value of a decile rank. The distinction matters for interpretation of coefficient magnitudes.
  - **Suggested fix:** Replace "absolute earnings surprise" with "absolute earnings surprise decile."

- **MINOR: Draft omits the joint Manager specification (A5) for H7.**
  - **Draft says:** The methodology paragraph describes "raw linguistic uncertainty variants (CEO QA, CEO presentation, manager QA, manager presentation) as well as clarity-residual variants" -- implying 6 models.
  - **Code actually runs:** 7 specifications -- A1-A4 (raw), A5 (joint Manager QA + Pres with Wald test for H7-C), B1-B2 (residuals).
  - **Severity:** MINOR. The A5 joint spec with the H7-C Wald test is a methodological detail that could be mentioned in the results rather than methodology. Not omitting important information about the primary specs.

---

## H9 Methodology Audit

### Claims Verified

- **"Cox proportional hazards models"** -- VERIFIED. Code imports and uses `lifelines.CoxTimeVaryingFitter` (line 100). This is a Cox PH model for time-varying covariates.

- **"time-varying covariates in counting-process (start, stop) format"** -- VERIFIED. `START_COL = "start"`, `STOP_COL = "stop"` (lines 198-199). `ctv.fit(df_clean, id_col="gvkey", start_col=START_COL, stop_col=STOP_COL, ...)` (lines 476-484).

- **"three event types: all takeovers, uninvited (hostile) takeovers, and friendly takeovers"** -- VERIFIED. `model_defs` at lines 741-745: `("cox_ph_all", "Takeover", ...)`, `("cox_cs_uninvited", "Takeover_Uninvited", ...)`, `("cox_cs_friendly", "Takeover_Friendly", ...)`.

- **"Uninvited and friendly events are modeled as cause-specific hazards, treating competing event types as censored"** -- VERIFIED. Event indicators at lines 287-288: `Takeover_Uninvited = (Takeover==1) & (Takeover_Type=="Uninvited")`, `Takeover_Friendly = (Takeover==1) & (Takeover_Type=="Friendly")`. Unknown-type events (Takeover=1 but neither Uninvited nor Friendly) are set to 0 in both cause-specific indicators, correctly treating them as censored. Lines 296-311 explicitly document this.

- **"Controls include firm size, book-to-market, leverage, ROA, and cash holdings"** -- VERIFIED. `SPARSE_CONTROLS = ["Size", "BM", "Lev", "ROA", "CashHoldings"]` (lines 130-136). All 5 match exactly.

- **"robust sandwich estimators"** -- VERIFIED. `lifelines.CoxTimeVaryingFitter` uses robust sandwich SEs by default. No explicit clustering parameter is passed (lines 475-484). The provenance doc confirms: "Robust sandwich estimator (lifelines default for CoxTimeVaryingFitter)" (H9.md, section A5).

- **"not clustered at the firm level"** -- VERIFIED. The `CoxTimeVaryingFitter.fit()` call does not pass any clustering parameter. `lifelines` CoxTimeVaryingFitter does not support firm-level clustering. Provenance doc confirms: "NOT CLUSTERED -- lifelines CoxTimeVaryingFitter uses robust sandwich SE but does NOT cluster by firm" (H9.md, section A5).

- **"sparse specification across three clarity variants: the CEO clarity score, the CEO clarity residual, and the manager clarity residual"** -- VERIFIED. `MODEL_VARIANTS` (lines 177-195): CEO -> `ClarityCEO`, CEO_Residual -> `CEO_Clarity_Residual`, Manager_Residual -> `Manager_Clarity_Residual`. These are run with `SPARSE_CONTROLS` as the primary specification (line 847).

### Issues Found

- **MAJOR: Draft describes estimator as "lifelines CoxPH" -- code actually uses `CoxTimeVaryingFitter`, not `CoxPHFitter`.**
  - **Draft says:** "the default in the lifelines CoxPH implementation"
  - **Code actually uses:** `lifelines.CoxTimeVaryingFitter` (line 100), which is distinct from `CoxPHFitter`. `CoxTimeVaryingFitter` is specifically designed for counting-process (start, stop) data with time-varying covariates. `CoxPHFitter` is for static covariates.
  - **Severity:** MAJOR. While both are Cox PH models, the specific class name matters for reproducibility and for readers who want to replicate the analysis. The phrase "lifelines CoxPH implementation" could be interpreted as `CoxPHFitter`, which would be incorrect.
  - **Suggested fix:** Replace "lifelines CoxPH implementation" with "lifelines CoxTimeVaryingFitter implementation" or "lifelines Cox time-varying fitter."

- **MINOR: Draft omits the expanded robustness control block.**
  - **Draft says:** Only mentions the sparse control set (Size, BM, Lev, ROA, CashHoldings).
  - **Code also runs:** An expanded robustness block adding SalesGrowth, Intangibility, AssetGrowth (lines 139-143, and the expanded robustness loop at lines 850-863).
  - **Severity:** MINOR. The methodology paragraph focuses on the primary specification, which is the sparse block. Robustness tests are typically described in results sections.

- **MINOR: Draft omits year-stratified and industry-stratified robustness models.**
  - **Code runs:** Year-stratified (strata="year") and industry-stratified (strata="ff12_code") robustness models (lines 865-893).
  - **Severity:** MINOR. These are robustness checks, appropriately described in results rather than methodology.

---

## Summary

| Metric | Count |
|--------|-------|
| **Total claims audited** | 25 |
| **Verified correct** | 21 |
| **Issues found** | 4 (0 critical, 1 major, 3 minor) |

### Issue Inventory

| # | Hypothesis | Severity | Description |
|---|-----------|----------|-------------|
| 1 | H0.3 | MINOR | "absorbed via indicator variables" should be "included via indicator variables" -- code uses explicit C() dummies, not FE absorption |
| 2 | H14 | MINOR | "absolute earnings surprise" should be "absolute earnings surprise decile" (AbsSurpDec is ordinal 0-5) |
| 3 | H7 | MINOR | Draft omits joint Manager A5 specification with H7-C Wald test (7 specs run, not 6) |
| 4 | H9 | MAJOR | "lifelines CoxPH" should be "lifelines CoxTimeVaryingFitter" -- different class for time-varying covariates |

### Robustness Mentions

- **H7:** Robustness battery runs (two-way cluster, subperiod, large-firm, industry subsamples) -- NOT mentioned in methodology paragraph. Appropriate for results section.
- **H14:** Robustness battery runs (DV variants, control variants, clustering variants) -- NOT mentioned in methodology paragraph. Appropriate for results section.
- **H9:** Expanded controls, year-stratified, and industry-stratified robustness models -- NOT mentioned in methodology paragraph. Appropriate for results section.

### Files Audited

| File | Path |
|------|------|
| Thesis draft | `docs/Draft/thesis_draft.tex` (lines 70-83) |
| H0.3 runner | `src/f1d/econometric/run_h0_3_ceo_clarity_extended.py` |
| H7 runner | `src/f1d/econometric/run_h7_illiquidity.py` |
| H14 runner | `src/f1d/econometric/run_h14_bidask_spread.py` |
| H9 runner | `src/f1d/econometric/run_h9_takeover_hazards.py` |
| H7 panel builder | `src/f1d/variables/build_h7_illiquidity_panel.py` |
| H14 panel builder | `src/f1d/variables/build_h14_bidask_spread_panel.py` |
| Amihud change engine | `src/f1d/shared/variables/amihud_change.py` |
| H0.3 provenance | `docs/provenance/H0.3.md` |
| H7 provenance | `docs/provenance/H7.md` |
| H14 provenance | `docs/provenance/H14.md` |
| H9 provenance | `docs/provenance/H9.md` |
