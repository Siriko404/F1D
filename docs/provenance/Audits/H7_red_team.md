# H7 Post-Call Illiquidity -- Second-Layer Red-Team Audit

**Audit Date:** 2026-03-18
**Auditor Context:** Fresh -- no prior involvement with H7 implementation or first-layer audit
**First-Layer Audit Doc:** `docs/provenance/H7.md`
**Suite Entrypoint:** `src/f1d/econometric/run_h7_illiquidity.py`
**Panel Builder:** `src/f1d/variables/build_h7_illiquidity_panel.py`
**DV Builder:** `src/f1d/shared/variables/amihud_change.py`
**CRSP Engine:** `src/f1d/shared/variables/_crsp_engine.py`
**Selection Supplement:** `src/f1d/econometric/ceo_presence_probit.py`

---

## A. Red-Team Bottom Line

| Dimension | Assessment |
|-----------|------------|
| First-layer audit factual accuracy | Mostly correct on surface claims; misses critical implementation detail on winsorization |
| First-layer audit completeness | INSUFFICIENT for thesis-standard review -- omits DV construction provenance, winsorization gap, event-window mechanics, panel-index semantics, selection-analysis coverage |
| Material issues missed | 2 CRITICAL, 2 MAJOR, 3 MINOR (detailed below) |
| Unsupported/exaggerated claims | 1 -- LaTeX table's winsorization note is false for DV and lagged-DV control |
| Overall readiness | CONDITIONAL PASS -- fixable issues, no fatal design flaw, but the winsorization gap must be resolved before submission |

---

## B. Scope and Objects Audited

| Object | Path | Lines | Audited |
|--------|------|-------|---------|
| First-layer audit | `docs/provenance/H7.md` | 48 | Full |
| Regression runner | `src/f1d/econometric/run_h7_illiquidity.py` | 467 | Full |
| Panel builder | `src/f1d/variables/build_h7_illiquidity_panel.py` | 259 | Full |
| AmihudChangeBuilder | `src/f1d/shared/variables/amihud_change.py` | 374 | Full |
| CRSPEngine | `src/f1d/shared/variables/_crsp_engine.py` | 519 | Targeted (winsorization, raw daily path, Amihud computation) |
| CompustatEngine | `src/f1d/shared/variables/_compustat_engine.py` | ~1100 | Targeted (BookLev, control variable construction) |
| CEO Presence Probit | `src/f1d/econometric/ceo_presence_probit.py` | 179 | Full |
| Panel utilities | `src/f1d/shared/variables/panel_utils.py` | 193 | Full |
| BookLevBuilder | `src/f1d/shared/variables/book_lev.py` | 57 | Full |
| H14 runner (comparator) | `src/f1d/econometric/run_h14_bidask_spread.py` | targeted | Targeted (winsorization, controls) |
| H14 panel builder (comparator) | `src/f1d/variables/build_h14_bidask_spread_panel.py` | targeted | Targeted (winsorization) |
| Shared __init__ | `src/f1d/shared/variables/__init__.py` | 330 | Targeted |

---

## C. Audit-of-Audit Scorecard

| Criterion | First-Layer Score | Red-Team Assessment |
|-----------|-------------------|---------------------|
| Specification table accuracy | Correct | VERIFIED -- all fields match code |
| Variable dictionary | Absent | MISSED -- no formal definitions for DV, IVs, or controls |
| Sample accounting / attrition | Mentioned in code but not documented | MISSED -- audit doc has no attrition table or sample sizes |
| Merge provenance | Not discussed | MISSED -- no documentation of merge chain (manifest -> CRSP -> Compustat) |
| Winsorization documentation | Absent | CRITICAL MISS -- DV is unwinsorized; audit does not note this |
| Event-window mechanics | Superficial ("[+1,+3] - [-3,-1]") | MISSED -- no discussion of reference date logic, call-day exclusion, trading-day assignment |
| Selection analysis coverage | Not mentioned | MISSED -- probit supplement exists but audit doc does not reference it |
| Identification strategy | Not discussed | MISSED -- no discussion of what variation identifies the effect |
| Robustness | Dropped variants noted | Adequate |
| Reproducibility | Code files listed | Minimal -- no run output checksums, no sample sizes |

---

## D. Claim Verification Matrix

| # | Claim (from H7.md) | Source Checked | Verdict | Detail |
|---|---------------------|----------------|---------|--------|
| D1 | DV = delta_amihud, event-window [+1,+3] - [-3,-1] | `amihud_change.py` L345-346 | VERIFIED FACT | Window uses `w=3` trading days pre and post reference date; reference = last trading day on/before call |
| D2 | Key IVs: 4 simultaneous CEO/Manager x QA/Pres | `run_h7_illiquidity.py` L66-70 | VERIFIED FACT | All 4 enter simultaneously in KEY_IVS list |
| D3 | Base Controls (8): Size, TobinsQ, ROA, BookLev, CapexAt, DividendPayer, OCF_Volatility, pre_call_amihud | `run_h7_illiquidity.py` L73-82 | VERIFIED FACT | Exact match |
| D4 | Extended Controls (+4): Volatility, StockPrice, Turnover, Analyst_QA_Uncertainty_pct | `run_h7_illiquidity.py` L84-89 | VERIFIED FACT | Exact match |
| D5 | FE: Industry(FF12) + FiscalYear / Firm + FiscalYear | `run_h7_illiquidity.py` L91-96, L222-235 | VERIFIED FACT | Industry FE via other_effects on ff12_code; Firm FE via EntityEffects; both include TimeEffects on fyearq_int |
| D6 | Time Index: fyearq_int | `run_h7_illiquidity.py` L220 | VERIFIED FACT | set_index(["gvkey", "fyearq_int"]) |
| D7 | SEs: Firm-clustered | `run_h7_illiquidity.py` L230, L235 | VERIFIED FACT | cov_type="clustered", cluster_entity=True |
| D8 | Hypothesis: One-tailed beta > 0 | `run_h7_illiquidity.py` L251-258 | VERIFIED FACT | p_one = p_two/2 if beta>0 else 1-p_two/2 -- correct one-tailed conversion |
| D9 | Sample: Main only (FF12 not in {8,11}) | `run_h7_illiquidity.py` L163 | VERIFIED FACT | `panel[~panel["ff12_code"].isin([8, 11])]` |
| D10 | 4 model specs (1 DV x 2 FE x 2 controls) | `run_h7_illiquidity.py` L91-96 | VERIFIED FACT | MODEL_SPECS has 4 entries |
| D11 | "Mirrors H14 pattern" | H14 code checked | VERIFIED FACT with CAVEAT | Structure matches (4 IVs, 2 FE, 2 control sets, lagged-DV), but H14 panel builder winsorizes event-window variables while H7 does not |
| D12 | 4/4 regressions complete, no significant results at p<0.05 | Cannot re-run | UNVERIFIED -- plausible given code structure but no output artifacts available for independent verification |
| D13 | "Variables winsorized at 1%/99% by year at engine level" (LaTeX table) | `build_h7_illiquidity_panel.py`, `amihud_change.py` | VERIFIED ERROR | delta_amihud and pre_call_amihud are NOT winsorized anywhere in the pipeline (see G1) |
| D14 | Manager QA Uncertainty p=0.072 in firm FE extended spec | Cannot re-run | UNVERIFIED |

---

## E. Unsupported/Overstated Claims

| # | Claim | Location | Problem | Severity |
|---|-------|----------|---------|----------|
| E1 | "Variables winsorized at 1%/99% by year at engine level" | `run_h7_illiquidity.py` L334 (LaTeX table notes) | FALSE for delta_amihud and pre_call_amihud. AmihudChangeBuilder calls `engine.get_raw_daily_data()` and computes DV from scratch -- no winsorization is applied. The CRSPEngine only winsorizes StockRet/MarketRet/Volatility/amihud_illiq in `get_data()`, not `get_raw_daily_data()`. The H7 panel builder (`build_h7_illiquidity_panel.py`) contains zero references to winsorization. Compustat controls (Size, BookLev, etc.) ARE winsorized at engine level, but the claim as written misleads the reader into thinking all variables including the DV are covered. | CRITICAL |

---

## F. False Positives

| # | Potential Concern | Resolution |
|---|-------------------|------------|
| F1 | Duplicate (gvkey, fyearq_int) index might break PanelOLS | VERIFIED FALSE POSITIVE: PanelOLS v7.0 handles non-unique multi-index. Tested empirically -- runs successfully, treats each row as a separate observation. The entity demeaning averages over all calls for the firm (correct for call-level data), and time demeaning averages over all calls in that fiscal year. This is a defensible design for call-level regressions. However, this should be disclosed in the thesis methodology. |
| F2 | Call-day return excluded from both windows might bias results | VERIFIED FALSE POSITIVE (judgment): Reference date is set to last trading day on or before call. days_from_ref == 0 is excluded from both pre and post windows. This is conservative and avoids ambiguity about whether the call happened before or after market close. Standard in event-study literature. |

---

## G. Missed Issues

### CRITICAL

| # | Issue | Evidence | Impact | Recommendation |
|---|-------|----------|--------|----------------|
| G1 | **delta_amihud and pre_call_amihud are not winsorized** | `build_h7_illiquidity_panel.py` has zero winsorization calls. `amihud_change.py` has zero winsorization calls. Contrast with `build_h14_bidask_spread_panel.py` L200-203 which explicitly winsorizes DSPREAD and PreCallSpread via `winsorize_pooled()`. | Amihud illiquidity is notoriously right-skewed (|return|/dollar_volume * 1e6). Extreme outliers in the DV will inflate standard errors, reduce power, and potentially distort OLS coefficients. The LaTeX table note falsely claims winsorization occurs. This is a direct comparability failure with H14. | Add `winsorize_pooled(panel, ["delta_amihud", "pre_call_amihud"])` to `build_h7_illiquidity_panel.py` (matching H14 pattern), OR add `winsorize_by_year()` if per-year treatment is preferred. Fix the LaTeX table note to accurately describe what is winsorized. |
| G2 | **First-layer audit entirely omits DV construction provenance** | H7.md has no mention of AmihudChangeBuilder, CRSP data source, daily_illiq formula, reference-date logic, minimum-days filter (MIN_PRE_DAYS=2, MIN_POST_DAYS=2), or the 1e6 scaling factor. The DV construction is the most consequential implementation detail for this hypothesis. | A committee member cannot verify the Amihud measure construction from the audit doc alone. The formula `daily_illiq = |RET| / (VOL * |PRC|) * 1e6` should be documented and compared to Amihud (2002). | Document the full DV construction chain: raw CRSP -> daily_illiq -> window assignment -> mean aggregation -> delta. Include the minimum-days filter and scaling. |

### MAJOR

| # | Issue | Evidence | Impact | Recommendation |
|---|-------|----------|--------|----------------|
| G3 | **No sample sizes or attrition table in audit doc** | H7.md reports "4/4 regressions complete" but no N for the panel, no N for the regression sample, no attrition from full panel -> main sample -> complete cases -> min-calls filter. The runner produces an attrition table (L429-434) but the audit doc does not include it. | Committee cannot assess external validity or sample adequacy. The min-calls filter (MIN_CALLS_PER_FIRM=5) may substantially reduce N; this is undocumented. | Include the attrition table from the last run in the audit doc. |
| G4 | **CEO Presence Probit not referenced in first-layer audit** | `ceo_presence_probit.py` exists as an explicit supplement for H7 ("H7 Selection Characterisation" in its docstring) but H7.md makes no mention of selection concerns, CEO absence rates (~29.6%), or the probit analysis. | The probit shows CEO absence is non-random (correlated with firm characteristics). Since CEO_QA_Uncertainty_pct and CEO_Pres_Uncertainty_pct are NaN when CEO is absent, this creates a selection-on-observables concern that the audit should document. The complete-case filter in the runner drops all CEO-absent calls, systematically excluding smaller/more-volatile firms. | Add a section to H7.md documenting: (a) CEO absence rate and its determinants, (b) how CEO-IV missingness interacts with the complete-case filter, (c) reference to the probit supplement, (d) discussion of whether this affects interpretation. |

### MINOR

| # | Issue | Evidence | Impact | Recommendation |
|---|-------|----------|--------|----------------|
| G5 | **Panel builder docstring says DV is "amihud_illiq" but actual DV is "delta_amihud"** | `build_h7_illiquidity_panel.py` L18: "DV: amihud_illiq (contemporaneous Amihud illiquidity measure)" but the actual DV loaded and used is delta_amihud from AmihudChangeBuilder. | Misleading documentation; no code impact. | Fix docstring to: "DV: delta_amihud (post-call minus pre-call Amihud illiquidity change)". |
| G6 | **Amihud daily_illiq formula uses VOL (shares) not dollar volume directly** | `amihud_change.py` L304: `dollar_volume = VOL * |PRC|` then `daily_illiq = |RET| / dollar_volume * 1e6`. Amihud (2002) defines illiquidity as |return| / dollar_volume where dollar_volume = price * volume. The code uses VOL (CRSP's daily volume in shares) * |PRC| (absolute closing price), which is correct. However, CRSP's VOL may be in 100s of shares for some periods; this would cause a systematic scaling error if present. | Low risk -- CRSP DSF VOL is in actual shares for the modern period (post-2001), but should be verified for earlier years in the sample. | Add a comment in AmihudChangeBuilder documenting that CRSP VOL is assumed to be in actual shares, not 100s. |
| G7 | **No log-transform or alternative specification for Amihud measure** | Amihud illiquidity is well-known to be extremely right-skewed. The standard practice in the literature (e.g., Amihud 2002, Chordia et al. 2001) is to log-transform the measure or winsorize aggressively. H7 does neither. | Reduced power and potential coefficient instability due to extreme values in both the DV and lagged-DV control. Combined with G1, this may explain the null results. | Consider adding a log(1+delta_amihud) or rank-transform robustness check. At minimum, fix the winsorization gap (G1). |

---

## H. Severity Recalibration

| Issue | First-Layer Severity | Red-Team Severity | Rationale |
|-------|---------------------|-------------------|-----------|
| G1 (no winsorization of DV) | Not identified | CRITICAL | Amihud measure is known to have extreme outliers. False claim in LaTeX notes. Direct comparability failure with H14. |
| G2 (no DV provenance) | Not identified | CRITICAL (audit-craft) | The single most important implementation detail for H7 is not documented. |
| G3 (no sample sizes) | Not identified | MAJOR | Standard thesis requirement; committee will ask. |
| G4 (probit not referenced) | Not identified | MAJOR | Selection concern is material; supplement exists but is orphaned from the audit. |
| G5 (docstring error) | Not identified | MINOR | Documentation only. |
| G6 (VOL units) | Not identified | MINOR | Low risk for modern CRSP data. |
| G7 (no log-transform) | Not identified | MINOR (design choice) | Defensible if winsorization is applied; becomes more concerning without it. |

---

## I. Completeness Gaps

| Topic | Covered in H7.md? | Required for Thesis? | Gap Severity |
|-------|-------------------|---------------------|--------------|
| Specification table | Yes | Yes | None |
| Variable definitions (formal) | No | Yes | HIGH |
| DV construction provenance | No | Yes | HIGH |
| Sample sizes and attrition | No | Yes | HIGH |
| Merge chain documentation | No | Yes | MEDIUM |
| Winsorization treatment | No (false claim in LaTeX) | Yes | HIGH |
| Event-window mechanics | Superficial | Yes | MEDIUM |
| Selection analysis (CEO absence) | No | Yes (given probit exists) | MEDIUM |
| Identification strategy | No | Recommended | MEDIUM |
| Robustness variants | Partially (dropped variants noted) | Yes | LOW |
| Run reproducibility (timestamps, checksums) | No | Recommended | LOW |
| Comparison to Amihud (2002) | No | Yes (for DV definition) | MEDIUM |

---

## J. Reproducibility Assessment

| Criterion | Status | Detail |
|-----------|--------|--------|
| Code runs without modification | PLAUSIBLE | Standard patterns, correct imports, no obvious runtime errors |
| Data dependencies documented | PARTIAL | Code references CRSP_DSF parquets and CCM linkage, but audit doc does not list input files |
| Output artifacts verifiable | NO | No run outputs (model_diagnostics.csv, regression results) are committed or checksummed |
| Panel builder deterministic | YES | Left-join merge chain with zero-delta enforcement; AmihudChangeBuilder is deterministic given CRSP input |
| Random seed required | NO | No randomization in pipeline |
| Version pinning | PARTIAL | linearmodels v7.0 confirmed; pandas/numpy versions not documented |

---

## K. Econometric Meta-Audit

| Concern | Assessment | Detail |
|---------|------------|--------|
| Identification | WEAK | H7 relies on within-firm variation in uncertainty predicting within-firm variation in illiquidity change. No instrument, no natural experiment, no RDD. This is standard for the literature but the first-layer audit should acknowledge the endogeneity concern (uncertainty and illiquidity may co-move due to common information shocks). |
| Simultaneity | CONCERN | All 4 uncertainty IVs enter simultaneously. CEO and Manager QA/Pres measures are mechanically correlated (CEO is a subset of Manager). Multicollinearity may inflate standard errors, contributing to null results. VIF diagnostics are not computed or reported. |
| One-tailed test justification | ADEQUATE | Theory predicts beta > 0 (higher uncertainty -> more illiquidity). One-tailed test is appropriate given directional hypothesis. Implementation is correct (p_two/2 when beta>0, 1-p_two/2 otherwise). |
| Fixed effects | ADEQUATE | Industry(FF12) + FiscalYear and Firm + FiscalYear are standard. Firm FE absorbs time-invariant firm heterogeneity. FiscalYear FE absorbs aggregate time trends. |
| Clustering | ADEQUATE | Firm-clustered SEs via PanelOLS are appropriate for call-level data with repeated firm observations. |
| Functional form | CONCERN | Raw delta_amihud is likely to have heavy tails. Without winsorization (G1), OLS may be dominated by outliers. Consider quantile regression or log-transform as robustness. |
| Pre-call control | GOOD | pre_call_amihud as a lagged-DV control is appropriate -- it accounts for baseline illiquidity levels and absorbs firm-level liquidity heterogeneity not captured by firm FE alone. |
| Selection (CEO absence) | MATERIAL CONCERN | ~29.6% of Main-sample calls lack CEO participation in Q&A. CEO_QA_Uncertainty_pct is NaN for these calls. Complete-case analysis drops them, creating a non-random subsample (larger, less volatile firms are over-represented). The probit supplement characterizes this but is not integrated into the regression analysis (no Heckman correction or inverse-probability weighting). |

---

## L. Audit-Safety Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| False winsorization claim published in thesis | HIGH (if not fixed) | Reputational -- factual error in table notes | Fix LaTeX note OR add actual winsorization |
| Null results due to DV outliers rather than true null | MEDIUM | Incorrect inference (Type II error) | Winsorize DV, report robustness with/without |
| Committee questions DV construction without documentation | HIGH | Delay/revision | Add DV provenance to audit doc |
| Reviewer asks about CEO selection bias | HIGH | Requires substantive response | Document probit results, discuss limitations |

---

## M. Master Issue Register

| ID | Category | Severity | Summary | Status | Owner |
|----|----------|----------|---------|--------|-------|
| G1 | Implementation | CRITICAL | delta_amihud and pre_call_amihud not winsorized; LaTeX note falsely claims otherwise | OPEN | Panel builder |
| G2 | Audit-craft | CRITICAL | DV construction provenance entirely absent from first-layer audit | OPEN | Audit doc |
| G3 | Audit-craft | MAJOR | No sample sizes or attrition table in audit doc | OPEN | Audit doc |
| G4 | Audit-craft | MAJOR | CEO Presence Probit supplement not referenced; selection concerns undocumented | OPEN | Audit doc |
| G5 | Documentation | MINOR | Panel builder docstring incorrectly says DV is "amihud_illiq" | OPEN | Panel builder |
| G6 | Documentation | MINOR | CRSP VOL units assumption not documented | OPEN | AmihudChangeBuilder |
| G7 | Design | MINOR | No log-transform or alternative DV specification | OPEN | Design choice |
| E1 | Accuracy | CRITICAL | LaTeX table note claims winsorization that does not occur | OPEN | Runner |

Note: G1 and E1 refer to the same underlying problem (missing winsorization) from different angles (implementation vs. documentation).

---

## N. What Committee Would Not Know (from first-layer audit alone)

1. **How the Amihud measure is actually computed.** The audit doc says "delta_amihud (event-window: [+1,+3] - [-3,-1] Amihud illiquidity change)" but provides no formula, no reference-date logic, no minimum-days filter, no scaling factor. The actual computation is: `daily_illiq = |RET| / (VOL * |PRC|) * 1e6`, averaged over 3 trading days in each window, with a minimum of 2 valid days required per window.

2. **That the DV is not winsorized.** The Amihud measure is infamous for extreme right-tail values. The committee would assume standard outlier treatment is applied (especially given the LaTeX note claiming it is). In fact, no winsorization occurs for delta_amihud or pre_call_amihud.

3. **That ~30% of calls are missing CEO uncertainty measures.** The complete-case filter drops all calls where any IV is NaN. Since CEO_QA_Uncertainty_pct is NaN when the CEO does not participate in Q&A (~29.6% of Main calls), the effective sample is systematically biased toward firms where the CEO participates. A probit analysis exists characterizing this selection, but the audit doc does not mention it.

4. **The precise N for each regression column.** The audit doc reports 4/4 regressions complete but no observation counts. The min-calls filter (MIN_CALLS_PER_FIRM=5) further reduces the sample from the complete-case set.

5. **That the panel index (gvkey, fyearq_int) has duplicate entries.** Multiple calls per firm per fiscal year create non-unique panel indices. While PanelOLS handles this correctly, the committee should know the unit of observation is the individual call, not the firm-year.

6. **Whether VIF diagnostics were computed.** With 4 correlated uncertainty measures entering simultaneously, multicollinearity is a concern. No VIF or condition-number diagnostics are reported.

---

## O. Priority Fixes

| Priority | Issue ID | Action | Effort |
|----------|----------|--------|--------|
| 1 (BLOCKING) | G1/E1 | Add winsorization of delta_amihud and pre_call_amihud to `build_h7_illiquidity_panel.py` (following H14's `winsorize_pooled` pattern). Fix LaTeX table note to accurately describe treatment. Re-run regressions. | Low (5 lines of code + re-run) |
| 2 (HIGH) | G2 | Add DV construction provenance section to H7.md: formula, reference-date logic, trading-day assignment, minimum-days filter, scaling factor, CRSP data source. | Medium (documentation) |
| 3 (HIGH) | G3 | Include attrition table from last run (full panel -> main sample -> DV non-null -> complete cases -> min-calls filter) with exact N at each stage. | Low (copy from run output) |
| 4 (HIGH) | G4 | Add selection-analysis section to H7.md referencing `ceo_presence_probit.py`, documenting CEO absence rate, probit findings, and implications for interpretation. | Medium (documentation) |
| 5 (MEDIUM) | G5 | Fix panel builder docstring: change "amihud_illiq" to "delta_amihud". | Trivial |
| 6 (LOW) | G7 | Consider adding log(1+Amihud) robustness specification. | Medium (code + re-run) |

---

## P. Final Readiness Statement

**Verdict: CONDITIONAL PASS -- requires fixes before thesis submission.**

The H7 implementation is architecturally sound: it correctly computes the Amihud illiquidity change from CRSP daily data, uses appropriate PanelOLS specifications with firm-clustered standard errors, and correctly implements one-tailed hypothesis testing. The code is well-structured and follows consistent patterns shared across suites.

However, two critical deficiencies must be addressed:

1. **Winsorization gap (G1/E1):** The dependent variable (delta_amihud) and its lagged control (pre_call_amihud) are not winsorized anywhere in the pipeline. The LaTeX table note falsely claims winsorization occurs. This is both a correctness issue (Amihud measure has extreme outliers that dominate OLS) and an accuracy issue (false claim in output). The fix is straightforward: add `winsorize_pooled()` to the panel builder, matching the H14 pattern. After winsorization, regressions must be re-run -- the null results may change.

2. **Audit documentation gaps (G2-G4):** The first-layer audit is a sparse specification summary that omits the DV construction chain, sample sizes, and the existing CEO selection analysis. It does not meet thesis-standard provenance requirements. A committee member reading only H7.md cannot verify or critically evaluate the implementation.

Neither issue represents a fatal design flaw. The core econometric approach (event-window Amihud change regressed on speech uncertainty with firm/industry FE) is defensible. The null results are interpretable regardless of fixes, but the current lack of winsorization means the null could be an artifact of outlier-driven variance inflation rather than a true null effect. Fixing G1 and re-running is necessary to make a credible inference either way.
