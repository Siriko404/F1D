# H1 Suite -- Second-Layer Red-Team Audit

**Suite ID:** H1
**Audit date:** 2026-03-18
**Auditor mode:** Fresh-context, adversarial, independent code inspection
**First-layer audit path:** `docs/provenance/H1.md`

---

## A. Red-Team Bottom Line

The first-layer audit is **structurally competent but factually stale and materially incomplete**. Its central defect is that it documents a now-superseded 6-IV specification (run `2026-03-15_220402`, N~37,600) while claiming to describe a 4-IV redesign. The code on disk and the latest verified outputs (run `2026-03-18_185323`, N~57,200) use 4 IVs -- but the first audit's coefficient tables, sample sizes, within-R-squared values, and attrition accounting all reflect the old 6-IV run. This is not a minor versioning annoyance: the N values, significance patterns, and attrition story are materially different between the two specifications. A committee member reading the first audit would receive systematically wrong quantitative claims.

Beyond the staleness issue, the first audit missed several genuine implementation and econometric concerns, overstated its severity on some items while under-weighting others, and left key sample-accounting cells marked "pending re-run" -- a serious completeness gap for a thesis-standard document.

**Overall grade for the first-layer audit: C+ (Adequate structure, materially stale data, several missed issues)**

---

## B. Scope and Objects Audited

| Object | Path | Inspected? |
|--------|------|------------|
| First-layer audit doc | `docs/provenance/H1.md` | Yes |
| Econometric runner (Stage 4) | `src/f1d/econometric/run_h1_cash_holdings.py` | Yes, full |
| Panel builder (Stage 3) | `src/f1d/variables/build_h1_cash_holdings_panel.py` | Yes, full |
| Compustat engine | `src/f1d/shared/variables/_compustat_engine.py` | Yes, full |
| Panel utilities | `src/f1d/shared/variables/panel_utils.py` | Yes, full |
| Variable builders (__init__) | `src/f1d/shared/variables/__init__.py` | Yes |
| BookLev builder | `src/f1d/shared/variables/book_lev.py` | Yes |
| Lev builder (alias) | `src/f1d/shared/variables/lev.py` | Yes |
| Financial utils (legacy) | `src/f1d/shared/financial_utils.py` | Yes |
| Run `2026-03-15_220402` outputs | `outputs/econometric/h1_cash_holdings/2026-03-15_220402/` | Yes: model_diagnostics.csv, regression_results_col1.txt |
| Run `2026-03-18_145113` outputs | `outputs/econometric/h1_cash_holdings/2026-03-18_145113/` | Yes: model_diagnostics.csv, regression_results_col1.txt, sample_attrition.csv, h1_cash_holdings_table.tex, report_step4_H1.md |
| Run `2026-03-18_185323` outputs | `outputs/econometric/h1_cash_holdings/2026-03-18_185323/` | Yes: regression_results_col1.txt, model_diagnostics.csv |

---

## C. Audit-of-Audit Scorecard

| Dimension | Grade | Rationale |
|-----------|-------|-----------|
| Factual correctness | D | Core quantitative claims (N, R-squared, coefficients, significance patterns) match the wrong run |
| Evidence quality | C | Code references are generally correct but output references are stale |
| Completeness | C- | Sample attrition marked "pending re-run" in 4 cells; no updated coefficient table |
| Severity calibration | B- | Generally reasonable; some under-weighting (see Section H) |
| False positives | B+ | No major false positives identified |
| False negatives / omissions | C | Several genuine issues missed (see Section G) |
| Internal consistency | D | Claims "4-IV specification" throughout but all quantitative data from 6-IV run |
| Thesis-standard sufficiency | D+ | Not submission-ready due to stale data and incomplete attrition |

---

## D. Claim Verification Matrix (First Audit Claims Tested)

| # | Claim in First Audit | Verdict | Evidence |
|---|---------------------|---------|----------|
| D1 | "4 simultaneous uncertainty IVs" in current code | VERIFIED FACT | `run_h1_cash_holdings.py` lines 80-84: KEY_IVS has exactly 4 entries |
| D2 | "8 model specifications (2 DVs x 2 FE x 2 controls)" | VERIFIED FACT | `MODEL_SPECS` list at lines 103-112 has 8 entries |
| D3 | "Results from verified run 2026-03-15_220402" | VERIFIED ERROR IN FIRST AUDIT | That run output contains 6 IVs (CEO_Clarity_Residual, Manager_Clarity_Residual present in model_diagnostics.csv). The audit claims 4-IV results from a 6-IV run. |
| D4 | "Col 1 N = 37,661" | VERIFIED ERROR IN FIRST AUDIT | 37,661 is from the 6-IV run. The 4-IV code produces N=57,216 (verified in run 2026-03-18_185323) |
| D5 | "Within-R-squared Col 1 = -0.064" | VERIFIED ERROR IN FIRST AUDIT | The 4-IV run gives -0.030. The -0.064 value is from the stale 6-IV run. |
| D6 | "CEO QA Unc shows significance only under Firm FE with lead DV (cols 6, 8)" | VERIFIED ERROR IN FIRST AUDIT | In the 4-IV run (2026-03-18), CEO_QA has no significance at p<0.05 one-tailed in any column. Significance patterns completely changed. |
| D7 | "Manager Pres Unc shows significance only under Industry FE (cols 1,3,5)" | PARTIALLY VERIFIED | In the 4-IV run, Mgr Pres Unc is significant in cols 1, 3, 5, 7 (Industry FE) -- pattern generally holds but extends to col 7 |
| D8 | "Mgr QA Unc: 0/8 significant" | VERIFIED ERROR IN FIRST AUDIT | In 4-IV run, Mgr QA Unc is significant at p<0.01 in cols 2 and 4 (Firm FE, contemp DV) |
| D9 | "FF12 codes 1-7, 9-10, 12 for Main sample" | VERIFIED FACT | `filter_main_sample()` at line 214: `~panel["ff12_code"].isin([8, 11])` excludes FF12=8 (Utility) and 11 (Finance). Remaining codes are 1-7, 9-10, 12. |
| D10 | "Firm-clustered SEs in all 8 specs" | VERIFIED FACT | `run_regression()` lines 345, 351: `cov_type="clustered", cluster_entity=True` |
| D11 | "One-tailed: H1 beta > 0" | VERIFIED FACT | Lines 379-380: `p_one = p_two / 2 if beta > 0 else 1 - p_two / 2` -- correct one-tailed transform |
| D12 | "Stars: *** p<0.01, ** p<0.05, * p<0.10 (one-tailed)" | VERIFIED FACT | `_sig_stars()` at lines 400-410 matches |
| D13 | "BookLev = (dlcq.fillna(0) + dlttq.fillna(0)) / atq" | VERIFIED FACT | `_compustat_engine.py` line 1039 |
| D14 | "CashHoldings = cheq / atq" | VERIFIED FACT | `_compustat_engine.py` line 1066 |
| D15 | "TobinsQ = (mktcap + debt_book) / atq" | VERIFIED FACT (code); VERIFIED INCONSISTENCY (project docs) | Code at lines 1073-1076 uses `(mktcap + debt_book) / atq` where `mktcap = cshoq*prccq`, `debt_book = dlcq+dlttq`. But `__init__.py` architecture comment says `TobinsQ = (atq + cshoq*prccq - ceqq) / atq` -- different formula |
| D16 | "ROA = iby_annual / avg_assets" | VERIFIED FACT | `_compustat_engine.py` lines 1051-1060 |
| D17 | "112,968 rows x 33 columns in panel" | UNVERIFIED CONCERN | Cannot verify column count without loading parquet; the code has 22 builders but "33 columns" plausible with manifest fields |
| D18 | "Negative within-R2 expected for industry FE" | VERIFIED FACT | Confirmed in both 6-IV and 4-IV outputs |
| D19 | "Panel builder uses 20 builders total" | VERIFIED ERROR IN FIRST AUDIT | Builder dict at lines 121-158 has 21 entries (manifest + 20 variable builders), not 20 |
| D20 | "Lead variable validates fiscal-year continuity" | VERIFIED FACT | `create_lead_variable()` lines 330-334: consecutive check with NaN assignment for gaps |
| D21 | "DividendPayer uses dvy (annual common dividends)" | VERIFIED FACT | `_compustat_engine.py` line 1089-1092: uses Q4 dvy annual value |
| D22 | "OCF_Volatility: 5-year rolling min 3 periods" | VERIFIED FACT | `_compute_ocf_volatility()` line 338: `rolling("1826D", min_periods=3)` |
| D23 | "Linguistic _pct columns winsorized 0%/99% by year" | UNVERIFIED CONCERN | Not independently verified in linguistic engine code |
| D24 | "Min 5 calls per firm filter" | VERIFIED FACT | `MIN_CALLS_PER_FIRM = 5` at line 114; enforced at lines 270-276 |
| D25 | "drop_absorbed=True" | VERIFIED FACT | Lines 343, 350 |

---

## E. Unsupported, Overstated, or Weakly-Evidenced Claims in the First Audit

| # | Claim | Problem | Severity |
|---|-------|---------|----------|
| E1 | "Results from verified run 2026-03-15_220402" with 4-IV specification | Run 2026-03-15_220402 is a 6-IV run (includes CEO_Clarity_Residual and Manager_Clarity_Residual). ALL quantitative claims derived from this run are wrong for the current 4-IV code. | Critical |
| E2 | "N values 37,661 / 37,656 / 35,776 / 35,772" in Section A6 | These are 6-IV Ns. Actual 4-IV Ns are ~57,216 / 54,915 / 53,288 / 52,254. Nearly 50% more observations. | Critical |
| E3 | Coefficient table in Section H reporting CEO QA Unc = 0.034* in Col 1 | From 6-IV run. In 4-IV run, CEO QA Unc Col 1 beta = 0.0011 (not significant). | Critical |
| E4 | "CEO_QA_Uncertainty_pct: 2/8 significant" | In 4-IV run: CEO QA Unc is 0/8 significant at p<0.05. | High |
| E5 | "Manager_Pres_Uncertainty_pct: 3/8 significant (cols 1, 3, 5)" | In 4-IV run: Mgr Pres Unc significant at p<0.05 in cols 1, 3, 5, 7 (4/8 Industry FE cols). | Medium |
| E6 | Sample attrition cells marked "pending re-run" (Section E5) | Four cells left blank with placeholder text. Unacceptable for a thesis-standard audit. | High |
| E7 | "CEO QA Uncertainty shows significance only under Firm FE with lead DV -- consistent with within-firm variation driving the result" | Incorrect interpretation because based on stale data. In 4-IV run CEO QA is never significant. | High |

---

## F. False Positives in the First Audit

| # | Claim | Assessment |
|---|-------|------------|
| F1 | "L7: CEO variable selection (32% missing, endogenous)" rated Medium | REFEREE JUDGMENT: This is a fair concern -- CEO variables have ~30% missing. Not a false positive. |
| F2 | "L1: Reverse causality -- no IV or exogenous variation" rated High, Blocks Thesis | REFEREE JUDGMENT: While true, characterizing this as "blocks thesis" may be overly harsh for a descriptive/associational study that explicitly disclaims causal identification. Standard for the genre. This is more of a limitation to acknowledge than a blocker. |

No clear false positives identified. The first audit is if anything too lenient (see missed issues).

---

## G. Missed Issues (Second-Layer Discoveries)

| # | Issue | Severity | Category |
|---|-------|----------|----------|
| G1 | **STALE REFERENCE RUN**: The first audit's "verified run" (2026-03-15_220402) is a 6-IV specification. The current code is 4-IV. ALL numeric results in the audit are wrong. | Critical | Audit-craft failure |
| G2 | **Variable naming inconsistency**: The `2026-03-18_145113` run shows the leverage variable as "Lev" in regression outputs, while the code and audit call it "BookLev". The latest run `2026-03-18_185323` corrected this to "BookLev". This indicates the panel data column name was changed between runs. The audit does not document this renaming. | Medium | Variable-dictionary failure |
| G3 | **TobinsQ formula inconsistency in project docs**: The `__init__.py` architecture comment says `TobinsQ = (atq + cshoq*prccq - ceqq) / atq`, but the actual engine code computes `(cshoq*prccq + dlcq + dlttq) / atq`. These are different formulas. The first audit correctly documents the code formula but does not flag the internal project documentation inconsistency. | Medium | Variable-dictionary failure |
| G4 | **NEW significance pattern in 4-IV results**: `Manager_QA_Uncertainty_pct` is now significant (p<0.01, one-tailed) in Firm FE contemporaneous cols (2, 4) -- a new finding not documented by the first audit. This is a substantively important result. | High | Completeness failure |
| G5 | **Effective degrees of freedom inflation from call-level analysis**: With 57,216 observations but only ~1,615 firms and ~18 time periods, the effective number of independent observations is much lower. The first audit mentions Moulton problem (L5, L8) but does not quantify the DV clustering structure: how many calls per firm-year? If mean is ~3-4, the "57,216" N is inflating apparent precision by sqrt(3-4)x. This deserves a higher severity than "Low" (L8). | Medium-High | Inference failure |
| G6 | **No constant in Industry FE specification**: The PanelOLS constructor API (lines 336-344) does not include an intercept. For the industry FE model, `entity_effects=False` and `exog_data` does not include a constant. PanelOLS may add a constant automatically depending on the configuration, but this should be verified. The formula-based Firm FE model (line 349) includes `1 +` explicitly. | Medium | Identification failure |
| G7 | **`check_rank=False` suppresses rank deficiency warnings**: Line 343 sets `check_rank=False` for Industry FE models. This could mask collinearity issues, especially with 10 industry dummies plus controls. | Low-Medium | Robustness failure |
| G8 | **Attrition table in runner is incomplete**: `generate_attrition_table()` at lines 776-782 reports only 4 stages, with the last being col 1's N. It does not separately report the complete-case step and the min-calls step, making it impossible to decompose attrition. | Medium | Sample-accounting failure |
| G9 | **Multiple testing correction not applied**: 32 hypothesis tests (4 IVs x 8 specs) with no Bonferroni, Holm, or FDR correction. The first audit mentions this (Priority Fix #5) but does not quantify the impact. With 32 tests at nominal alpha=0.05, expected false positives under the null = 1.6. | Medium | Inference failure |
| G10 | **Summary stats generated on Main sample before complete-case filtering**: `make_summary_stats_table()` at line 735 runs on the full Main sample (88,205), not on the regression sample (~57,000). Summary stats may not match the estimation sample. | Medium | Reproducibility failure |
| G11 | **Report header says "All 6 key IVs" in 2026-03-18 run output**: `report_step4_H1.md` from run `2026-03-18_145113` line 10 says "All 6 key IVs enter each model simultaneously" but only 4 IVs are used. This is a hardcoded string that was not updated. | Low | Audit-craft / code hygiene |

---

## H. Severity Recalibration

| First Audit ID | First Audit Severity | Red-Team Severity | Rationale |
|----------------|---------------------|-------------------|-----------|
| L1 (Reverse causality) | High, blocks thesis | High, does NOT block thesis | Standard for descriptive corporate finance; acknowledged limitation |
| L2 (OVB) | High, blocks thesis | Medium-High, does NOT block thesis | Extended controls mitigate; analyst/earnings surprise controls would help but are not thesis-blocking |
| L3 (No lagged DV) | Medium-High, blocks thesis | High, blocks thesis | Agree this is severe given AR(1)>0.9 in cash holdings. But "blocks thesis" is correct only if causal claims are made. |
| L5 (Effective N overstated) | Medium | Medium-High | Should be elevated: 57k calls / 1,615 firms = ~35 calls/firm. Standard errors may be substantially overstated. |
| L8 (Moulton) | Low | Medium | L5 and L8 are the same problem restated. Combined, this is Medium or higher. |
| L9 (Negative within-R2) | Low | Low | Agree |
| J5 (No lagged DV) | Medium-High | High | Same as L3 above |

---

## I. Completeness Gaps in the First Audit

| # | Gap | Impact |
|---|-----|--------|
| I1 | Sample attrition table has 4 cells marked "pending re-run" | Referee cannot trace observation loss through the pipeline |
| I2 | Coefficient table labeled "pre-4IV run" with no updated 4-IV coefficients | Referee has no valid quantitative results to evaluate |
| I3 | No documentation of the 4-IV significance pattern changes vs 6-IV | Referee cannot assess whether the specification change is result-driven |
| I4 | No VIF or multicollinearity diagnostics reported | With 4 correlated uncertainty measures entering simultaneously, VIF is essential |
| I5 | No documentation of how many firms/calls have CEO present on call | The ~30% CEO missing rate is acknowledged but not investigated (selection on CEO participation) |
| I6 | No comparison to literature benchmarks for coefficient magnitudes | Is a 0.022 effect of Mgr Pres Unc on Cash Holdings economically meaningful? No effect-size discussion. |
| I7 | No time-series plot or temporal stability check | Are the results driven by a specific subperiod (e.g., 2008-2009 crisis)? |
| I8 | TobinsQ formula inconsistency between engine code and __init__.py not flagged | Potential data integrity issue if other suites use the wrong formula understanding |

---

## J. Reproducibility Red-Team Assessment

| # | Check | Result |
|---|-------|--------|
| J1 | Can runner be invoked from current code? | YES -- code runs and produces valid 4-IV output (verified from `2026-03-18_185323` artifacts) |
| J2 | Does latest output match code on disk? | YES -- `2026-03-18_185323` regression shows 4 IVs, BookLev column name, correct N |
| J3 | Does the first audit's "verified run" match code on disk? | NO -- `2026-03-15_220402` is a 6-IV run; code now has 4 IVs |
| J4 | Are output paths deterministic? | YES -- timestamped directories |
| J5 | Can Stage 3 + Stage 4 be re-run from commands in the audit? | LIKELY YES but not independently verified (would require raw data access) |
| J6 | Is there a "latest" symlink or pointer? | YES -- `get_latest_output_dir()` used |
| J7 | Seed / determinism | Deterministic per audit claim; OLS is deterministic given fixed inputs |

---

## K. Econometric and Thesis-Referee Meta-Audit

### K1. Identification Strategy Assessment

The first audit correctly identifies the absence of causal identification (no IV, no exogenous shock, no RDD). This is the dominant limitation. The audit's characterization is fair but the "blocks thesis" label may be too strong for what appears to be a descriptive/associational study.

### K2. Specification Choice Assessment

The 4-IV simultaneous specification is a meaningful improvement over one-at-a-time entry. However, the first audit does not discuss:
- Why these 4 measures were chosen (theoretical justification for speaker x section decomposition)
- Whether the CEO and Manager measures are mechanically correlated (CEO is a subset of Manager)
- What the correlation structure among the 4 IVs looks like (VIF analysis)
- Whether horse-racing 4 correlated IVs inflates SE and reduces power for each

### K3. Fixed Effects Assessment

The industry FE vs firm FE comparison is well-designed and informative. The pattern where Mgr Pres Unc is significant under Industry FE but not Firm FE suggests the effect operates through between-firm variation, which is econometrically weaker for causal identification. The first audit notes this but does not discuss the Mundlak (1978) interpretation.

### K4. Standard Error Assessment

Firm-clustering is appropriate but may not be sufficient. The first audit does not consider:
- Double-clustering by firm and time (Petersen 2009) as a robustness check
- The panel is unbalanced (5-67 obs/firm); clustered SEs with small clusters can be biased (MacKinnon/White)

### K5. Multiple Testing

32 tests without correction is a real concern. At 5% significance: E[false positives] = 1.6 under the null. The 4-IV run shows approximately 6-8 significant results across 32 tests, which is above the null expectation but not overwhelmingly so.

---

## L. Audit-Safety / Academic-Integrity Assessment of the First Audit

| # | Concern | Severity |
|---|---------|----------|
| L1 | First audit reports results from a superseded specification without clear labeling as obsolete | High -- could mislead a reader into citing wrong numbers |
| L2 | Multiple "pending re-run" placeholders left in a published audit document | Medium -- signals incomplete review |
| L3 | No explicit statement that the coefficient tables are from a different IV specification than the one described | High -- internal inconsistency that borders on misleading |
| L4 | The audit acknowledges the staleness in parenthetical notes ("Results from pre-4IV run") but does not REMOVE the stale numbers | Medium -- half-measure that creates confusion |

No evidence of deliberate misrepresentation. The staleness appears to result from a rapid redesign cycle where the audit was not fully updated after the specification change.

---

## M. Master Red-Team Issue Register

| ID | Source | Severity | Description | Blocks Thesis? |
|----|--------|----------|-------------|----------------|
| RT-1 | G1 | Critical | First audit references stale 6-IV run; all quantitative claims invalid for current 4-IV code | N (implementation is fine; audit needs update) |
| RT-2 | G4 | High | New Mgr QA Unc significance in Firm FE cols (2, 4) undocumented | N |
| RT-3 | E1/E2/E3 | Critical | N values, coefficients, and significance patterns in audit are from wrong specification | N (audit-only) |
| RT-4 | I1/E6 | High | Sample attrition incomplete (4 cells pending) | N (fixable) |
| RT-5 | G5 | Medium-High | Effective N inflation from call-level analysis inadequately addressed | Y (needs robustness: firm-year collapse) |
| RT-6 | G9 | Medium | 32 tests without multiple-testing correction | Y (needs at minimum FDR discussion) |
| RT-7 | G3 | Medium | TobinsQ formula discrepancy between code and project docs | N |
| RT-8 | L3 (first audit) | High | No lagged DV control for highly persistent series | Y |
| RT-9 | G6 | Medium | No explicit constant in Industry FE constructor; potential intercept issue | N (PanelOLS likely handles) |
| RT-10 | I4 | Medium | No VIF/multicollinearity diagnostics for 4 correlated IVs | N |
| RT-11 | I6 | Medium | No economic magnitude / effect-size discussion | N |
| RT-12 | G10 | Medium | Summary stats on full Main sample, not estimation sample | N |
| RT-13 | G11 | Low | Report template still says "6 key IVs" in latest run | N |
| RT-14 | G2 | Medium | Variable renaming (Lev -> BookLev) not documented across runs | N |

---

## N. What a Committee / Referee Would Still Not Know if They Read Only the First Audit

1. **The actual sample sizes, coefficients, and significance patterns for the current 4-IV specification.** The audit provides 6-IV numbers throughout.
2. **That Manager QA Uncertainty is now significant under Firm FE** -- a potentially important result for the hypothesis.
3. **That CEO QA Uncertainty is no longer significant in any specification** -- the key finding highlighted by the first audit has evaporated.
4. **How many calls per firm-year exist** (the DV clustering density that drives the Moulton problem).
5. **VIF values for the 4 simultaneously-entered IVs** (are CEO and Manager measures too correlated to disentangle?).
6. **Whether the TobinsQ formula in the code matches the one described in the project architecture documentation.**
7. **The complete sample attrition from full panel to estimation sample**, with separate rows for each filtering step.
8. **Economic magnitude of the effects** -- what does a 1-standard-deviation increase in Mgr Pres Unc mean for cash holdings in dollar or percentage terms?

---

## O. Priority Fixes to the First Audit

| # | Fix | Effort | Impact |
|---|-----|--------|--------|
| 1 | **Re-run verification with current 4-IV code and update ALL quantitative claims** (N, R2, coefficients, significance counts, attrition) | Medium | Critical -- nothing else matters until this is done |
| 2 | **Complete the sample attrition table** with actual numbers for each filtering step | Low | High |
| 3 | **Update the result summary and key patterns section** to reflect 4-IV findings (Mgr QA now significant in Firm FE; CEO QA no longer significant) | Low | High |
| 4 | **Add VIF diagnostics** for the 4 simultaneous IVs and discuss multicollinearity | Low | Medium |
| 5 | **Fix TobinsQ formula inconsistency** in `__init__.py` architecture comment vs engine code | Low | Medium |
| 6 | **Add firm-year collapse robustness check** to address effective-N concerns | Medium | High |
| 7 | **Add multiple-testing discussion** (at minimum Holm-Bonferroni bounds on the 32 tests) | Low | Medium |
| 8 | **Add economic magnitude interpretation** for significant coefficients | Low | Medium |
| 9 | **Fix report template string** that says "6 key IVs" in generated report | Trivial | Low |
| 10 | **Resolve whether L1/L2 truly "block thesis"** or are standard acknowledged limitations | Low | Medium (framing) |

---

## P. Final Red-Team Readiness Statement

**Is the first-layer audit ready for thesis submission?** NO.

**Primary reason:** The audit's quantitative claims are entirely based on a superseded 6-IV specification. Every number in Sections A6, E5, and H (the core tables) is wrong for the current codebase. A committee member relying on this audit would be misled about sample sizes (off by ~50%), significance patterns (CEO QA significance has disappeared; Mgr QA significance has appeared), and within-R-squared values.

**What must happen before the audit is submission-ready:**
1. Re-run the verification with the current code and replace ALL stale numbers.
2. Complete the "pending re-run" cells in the attrition table.
3. Update the result interpretation to match the new significance pattern.
4. Add VIF diagnostics and economic magnitude discussion.

**What must happen before the UNDERLYING SUITE is thesis-ready:**
1. Add lagged DV control for lead specifications (L3/RT-8).
2. Provide firm-year-collapsed robustness as a supplement (RT-5).
3. Add multiple-testing discussion or correction (RT-6).
4. Resolve the TobinsQ formula inconsistency in project documentation (RT-7).

**Bottom line:** The suite implementation is sound. The audit document is structurally competent but quantitatively stale and therefore not trustworthy in its current form. One full verification pass with the current code would bring it to thesis standard.

---

## Revision History

- **2026-03-18 (v1):** Initial second-layer red-team audit by independent reviewer.
