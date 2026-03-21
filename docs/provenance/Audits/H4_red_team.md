# H4 Leverage -- Second-Layer Red-Team Audit

**Auditor:** Automated adversarial red-team (fresh context, no trust inheritance)
**Date:** 2026-03-18
**Suite ID:** H4
**First-Layer Audit:** `docs/provenance/H4.md`
**Runner:** `src/f1d/econometric/run_h4_leverage.py`
**Panel Builder:** `src/f1d/variables/build_h4_leverage_panel.py`

---

## A. Red-Team Bottom Line

| Dimension | Assessment |
|-----------|------------|
| First-layer audit factual accuracy | Mostly accurate but contains several material errors and omissions |
| First-layer audit completeness | INCOMPLETE -- missed a critical output bug and several substantive issues |
| Material missed issues | YES -- LaTeX table drops 8 of 16 models; docstring/output inconsistencies; Moulton concern imprecisely characterized |
| Unsupported claims | YES -- audit claims "16-column LaTeX table" but code produces only 8 columns; output list includes `sample_attrition.tex` but runner docstring only lists 8 output files |
| Overall red-team verdict | **CONDITIONAL PASS -- requires fixes before submission** |

---

## B. Scope and Objects Audited

| Object | Path | Hash/Version | Audited? |
|--------|------|-------------|----------|
| First-layer audit doc | `docs/provenance/H4.md` | git modified (unstaged) | YES -- full line-by-line |
| Estimation runner | `src/f1d/econometric/run_h4_leverage.py` | git modified (unstaged) | YES -- full source |
| Panel builder | `src/f1d/variables/build_h4_leverage_panel.py` | git modified (unstaged) | YES -- full source |
| BookLev builder | `src/f1d/shared/variables/book_lev.py` | git modified (unstaged) | YES -- full source |
| DebtToCapital builder | `src/f1d/shared/variables/debt_to_capital.py` | git modified (unstaged) | YES -- full source |
| Compustat engine | `src/f1d/shared/variables/_compustat_engine.py` | git modified (unstaged) | YES -- full source |
| Panel utilities | `src/f1d/shared/variables/panel_utils.py` | stable | YES -- full source |
| Attrition table generator | `src/f1d/shared/outputs/attrition_table.py` | stable | YES -- full source |
| LaTeX table output function | `_save_latex_table()` in runner | -- | YES -- line-by-line |

---

## C. Audit-of-Audit Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Factual accuracy of claims | 3 | Several verifiably incorrect claims (16-col table, output file list, Moulton characterization) |
| Completeness of variable dictionary | 4 | DVs, IVs, and controls are correctly enumerated and formulas verified |
| Completeness of identification discussion | 3 | Missing discussion of multicollinearity among 4 simultaneous IVs; no VIF reported |
| Completeness of robustness discussion | 2 | No discussion of alternative clustering, winsorization sensitivity, or subsample stability |
| Completeness of sample accounting | 3 | Attrition table is present but incomplete (only tracks col-1 N, not DebtToCapital models) |
| Internal consistency | 2 | 16 models defined vs 8-column LaTeX table; docstring says "col{1-8}" but 16 models run |
| Boundary correctness | 4 | Suite boundary correctly identified; shared engine traced |
| Red-team adversariality | 3 | Found some real bugs (fyearq drop) but missed the LaTeX table truncation |

---

## D. Claim Verification Matrix

| # | Claim in First-Layer Audit | Verified? | Evidence | Verdict |
|---|---------------------------|-----------|----------|---------|
| D1 | "16-column LaTeX table" (Section A6, E) | **NO** | `_save_latex_table()` sets `n_cols = 8` and only renders cols 1-8 (BookLev). DebtToCapital cols 9-16 are computed but never appear in the LaTeX output. | **FALSE** |
| D2 | BookLev = (dlcq + dlttq) / atq | YES | `_compustat_engine.py` line 1039 confirms formula. `fillna(0)` applied to both debt components. | Verified |
| D3 | DebtToCapital = total_debt / (seqq + total_debt); NaN when denom <= 0 | YES | `_compustat_engine.py` lines 1042-1048 confirm formula and NaN condition. | Verified |
| D4 | 4 simultaneous IVs | YES | `KEY_IVS` list at line 85-89 of runner contains exactly 4 variables, all enter `exog` simultaneously. | Verified |
| D5 | Industry FE absorbed via `other_effects` | YES | Runner line 337: `other_effects=industry_data` for industry specs. | Verified |
| D6 | Firm FE via `EntityEffects + TimeEffects` | YES | Runner line 345: formula includes `EntityEffects + TimeEffects`. | Verified |
| D7 | Time index = `fyearq_int` (fiscal year) | YES | Runner line 324: `df_panel = df_prepared.set_index(["gvkey", "fyearq_int"])`. | Verified |
| D8 | Firm-clustered SEs | YES | Runner lines 341, 347: `cov_type="clustered", cluster_entity=True`. | Verified |
| D9 | Two-tailed p-values | YES | Runner line 372: `p_two = float(model.pvalues.get(iv, np.nan))` -- uses raw pvalues from linearmodels which are two-tailed. | Verified |
| D10 | "Contemporaneous BookLev is constant within firm-quarter" (Moulton concern) | **PARTIAL** | BookLev is the merge_asof-matched Compustat value. It is constant within a firm-quarter but can vary across quarters within a fiscal year. The concern is valid but imprecisely stated -- the Moulton issue is about within-quarter clustering, NOT within-fiscal-year. | **Imprecise** |
| D11 | Main sample = FF12 codes 1-7, 9-10, 12 | YES | Runner line 233: `panel[~panel["ff12_code"].isin([8, 11])]`. FF12 has codes 1-12; excluding 8 and 11 leaves 1-7, 9-10, 12. | Verified |
| D12 | Minimum calls >= 5 per firm | YES | Runner line 129: `MIN_CALLS_PER_FIRM = 5`. | Verified |
| D13 | "fyearq_int dropped from panel" bug fixed | YES | Panel builder's `create_leverage_temporal_vars()` creates `fyearq_int` at line 140-142 and does not drop it. | Verified |
| D14 | Output list includes `sample_attrition.tex` | **PARTIAL** | The `generate_attrition_table()` function does produce both CSV and TEX. But the runner docstring (line 44) only lists `col{1-8}` not `col{1-16}`. | Inconsistent with docstring |
| D15 | "Requires consecutive fiscal years" for lead DVs | YES | `_create_temporal_vars_for_col()` line 101-102 checks `next_fyearq - fyearq_int == 1`. | Verified |
| D16 | `drop_absorbed=True` | YES | Runner lines 338 (industry) and 346 (firm). | Verified |

---

## E. Unsupported, Overstated, or Weakly-Evidenced Claims

| # | Claim | Problem | Severity |
|---|-------|---------|----------|
| E1 | "16-column LaTeX table" (Section A6) | The LaTeX table function hardcodes `n_cols = 8` and only renders BookLev models (cols 1-8). DebtToCapital models (cols 9-16) are computed by the regression loop but silently omitted from the LaTeX output. The first-layer audit asserts 16 columns without verifying the actual output function. | **CRITICAL** |
| E2 | Output list item "h4_leverage_table.tex -- unified 16-column LaTeX table" (Section E) | Same as E1. The table is 8 columns, not 16. | **CRITICAL** |
| E3 | Runner docstring: "regression_results_col{1-8}.txt" | The code runs 16 models and writes `regression_results_col{1-16}.txt`. The docstring is stale, reflecting an earlier version that only had BookLev. | MINOR (doc-only) |
| E4 | Audit Section E: "Results below are from the pre-4IV run" | The audit explicitly disclaims that results are stale, which is honest. But this means NO actual regression output was verified by the first-layer auditor. | MAJOR |

---

## F. False Positives in the First Audit

| # | First-Audit Finding | Assessment | Rationale |
|---|-------------------|------------|-----------|
| F1 | F14 "Moulton problem" rated MAJOR | Correctly identified but imprecisely characterized. BookLev is constant within a *Compustat quarter* (same datadate), not within a *fiscal year*. Multiple calls in different quarters of the same fiscal year WILL have different BookLev values because merge_asof matches to different Compustat reporting dates. The Moulton concern is real but overstated by implying it affects all within-firm-year observations. | Severity appropriately MAJOR, but description needs correction |
| F2 | None identified as false positive | -- | The other findings (F1 fyearq drop, F7/F8 control changes, F11 two-tailed, F21 DV flip, F23 ff12_code) are all verified as genuine issues with correct resolutions. |

---

## G. Missed Issues (Second-Layer Discoveries)

| # | Issue | Severity | Description | Impact |
|---|-------|----------|-------------|--------|
| G1 | **LaTeX table truncated to 8 of 16 models** | **CRITICAL** | `_save_latex_table()` at line 418 hardcodes `n_cols = 8`. The function header, DV labels, and column loops all reference only BookLev (cols 1-8). DebtToCapital results (cols 9-16) are computed and saved to `model_diagnostics.csv` but are invisible in the thesis-facing LaTeX table. A committee reviewing only the LaTeX output would not see half the results. | Half of results unreported in primary output artifact |
| G2 | **No multicollinearity diagnostics** | MAJOR | Four uncertainty measures enter simultaneously but share conceptual and measurement overlap (CEO QA vs Manager QA, QA vs Presentation). No VIF or correlation matrix is computed or reported. High collinearity among IVs could inflate standard errors and make individual coefficients unreliable, which is especially problematic when the hypothesis test is on individual IV coefficients. | Potentially unreliable inference on individual IV significance |
| G3 | **`check_rank=False` suppresses rank warnings** | MAJOR | The industry FE specification uses `check_rank=False` (runner line 339), which silently suppresses warnings about near-singular design matrices. If the combination of 10 FF12 dummies + fiscal year dummies + 11 control variables creates near-collinearity, this would not be flagged. | Could mask numerical instability |
| G4 | **Asymmetric DV construction** | MODERATE | Contemporaneous DV (`BookLev`) is the raw merge_asof-matched Compustat value that varies within fiscal year. Lead DV (`BookLev_lead`) is from the temporal function which deduplicates to ONE value per gvkey-fyearq (the last call's matched value), then shifts forward. This means `BookLev` has more within-group variation than `BookLev_lead`, potentially affecting comparative R-squared and coefficient magnitudes across contemporaneous vs lead specifications. | Systematic difference in within-group variation between t and t+1 specs |
| G5 | **`fillna(0)` for missing debt components** | MODERATE | Both BookLev and DebtToCapital treat missing dlcq/dlttq as zero debt. If debt is genuinely unreported (rather than zero), this biases leverage downward for those observations. The first-layer audit mentions "Missing debt treated as zero per spec" but does not discuss the magnitude or selection implications. | Potential downward bias in leverage for firms with missing debt data |
| G6 | **No negative BookLev guard** | LOW-MODERATE | BookLev = (dlcq.fillna(0) + dlttq.fillna(0)) / atq. If either dlcq or dlttq is negative (possible for some Compustat items), BookLev could be negative. Unlike the TobinsQ formula (line 1068-1069) where debt is `.clip(lower=0)`, BookLev has no floor. Negative leverage is economically meaningless. Winsorization at 1%/99% may handle extreme cases but does not enforce a floor at zero. | Possible nonsensical values in DV |
| G7 | **Attrition table only tracks BookLev path** | LOW-MODERATE | The attrition table (runner lines 768-774) reports "After lead filter (col 5-8 only)" using `BookLev_lead` but does not separately track DebtToCapital or DebtToCapital_lead sample sizes. Since DebtToCapital has an additional NaN condition (denominator <= 0), its effective sample could be different. | Incomplete sample documentation |
| G8 | **No intercept in industry FE spec** | LOW | Industry FE spec uses constructor-based PanelOLS (not from_formula). The exog data does not include a constant. `time_effects=True` and `other_effects=industry_data` together may or may not absorb the intercept depending on linearmodels' internal handling. This should be explicitly verified. | Possibly absorbed by FE, but worth confirming |
| G9 | **Summary stats computed on pre-filter sample** | LOW | `make_summary_stats_table()` is called on the `panel` DataFrame (line 728) which has been filtered to Main sample but NOT yet filtered for complete cases or minimum calls. The regression sample may differ substantially from the summary statistics sample. | Descriptive statistics may not match the estimation sample |

---

## H. Severity Recalibration

| Issue | First-Layer Severity | Red-Team Severity | Rationale for Change |
|-------|---------------------|-------------------|---------------------|
| F1: fyearq_int dropped | CRITICAL | CRITICAL | Agree -- would have caused wrong time FE. Confirmed fixed. |
| F7: Old controls dropped | MAJOR | LOW | These were controls for a different DV direction. Dropping them is the correct design choice, not a "finding." |
| F8: Analyst_QA dropped | MAJOR | LOW | Same rationale as F7 -- correct design choice for redesigned hypothesis. |
| F11: Two-tailed p-values | MAJOR | MODERATE | The implementation is correct. The severity should reflect that this was a disclosure issue (now resolved), not an ongoing problem. |
| F14: Moulton problem | MAJOR | MAJOR | Agree on severity but the characterization needs correction (see F1 in Section F). |
| F21: Old falsification failure | MAJOR | LOW | Resolved by design. Not an ongoing issue. |
| F23: ff12_code in required cols | MAJOR | LOW | A basic data-wrangling step, not a methodological concern. |
| NEW G1: LaTeX table truncated | -- | **CRITICAL** | Half the results unreported. |
| NEW G2: No VIF/multicollinearity | -- | MAJOR | Standard econometric diagnostic missing for simultaneous IVs. |
| NEW G3: check_rank=False | -- | MAJOR | Suppresses potentially important numerical warnings. |

---

## I. Completeness Gaps

| Gap Area | What Is Missing | Severity |
|----------|----------------|----------|
| Variable construction deep-dive | Audit correctly reports formulas but does not trace the `merge_asof` matching tolerance -- there is no maximum gap restriction on how old a Compustat observation can be when matched to a call. A call in December 2015 could match to a June 2014 Compustat row if no closer data exists. | MODERATE |
| Multicollinearity among IVs | No VIF table, no correlation matrix among the 4 uncertainty measures. The audit does not discuss whether CEO_QA and Manager_QA are collinear. | MAJOR |
| Alternative clustering | No discussion of double-clustering (firm + year), which is standard for long-panel corporate finance. | MODERATE |
| Subsample analysis | No discussion of whether results hold across different time periods, industries, or firm size groups. | LOW (robustness, not core) |
| DebtToCapital coverage | Audit mentions DebtToCapital but does not verify its sample coverage rate or document NaN rates from the `denominator <= 0` condition. | MODERATE |
| Economic magnitude | No discussion of whether coefficient magnitudes are economically meaningful (e.g., a 1-SD increase in uncertainty corresponds to what change in leverage?). | MODERATE |

---

## J. Reproducibility Red-Team Assessment

| Dimension | Assessment | Notes |
|-----------|------------|-------|
| Panel build determinism | GOOD | Uses manifest-based pipeline with timestamp-versioned outputs and `run_manifest.json`. |
| Regression determinism | GOOD | PanelOLS is deterministic for the same input data. No random seed dependencies. |
| Dependency pinning | UNKNOWN | No `requirements.txt` or `pyproject.toml` verified in this audit. linearmodels version could affect results. |
| End-to-end reproducibility | NOT VERIFIED | The first-layer audit explicitly states results are from a "pre-4IV run." No fresh run output was verified by either audit layer. |
| Cross-platform reproducibility | UNKNOWN | No evidence of testing on different OS/Python versions. |

---

## K. Econometric and Thesis-Referee Meta-Audit

| Concern | Severity | Discussion |
|---------|----------|------------|
| Endogeneity of uncertainty measures | MAJOR | Speech uncertainty may reflect firm conditions that also drive leverage (omitted variable bias). No IV strategy or natural experiment is proposed. The two-tailed test acknowledges uncertainty about direction, but does not address causality. This is a fundamental limitation that the first-layer audit acknowledges indirectly (by noting the redesigned DV direction) but does not discuss as an identification threat. |
| Moulton problem | MAJOR | Correctly identified by first audit. Firm-clustered SEs partially address this, but the core issue remains: within a quarter, multiple calls from the same firm have identical BookLev. If most firms have only one call per quarter, this is moot; if multiple calls per quarter are common, the effective sample size is overstated. |
| Simultaneous IV interpretation | MODERATE | With 4 correlated uncertainty measures entering simultaneously, individual coefficients represent partial effects conditional on the others. This makes interpretation challenging -- a null coefficient on CEO_QA does not mean CEO QA uncertainty is irrelevant, only that it has no incremental effect beyond the other three measures. The thesis text must carefully distinguish partial from marginal effects. |
| Lead DV as causal test | MODERATE | Using `BookLev_lead` (t+1) is presented as a forward-looking test. But leverage is persistent (high autocorrelation), so contemporaneous uncertainty could merely proxy for current conditions that persist into next year. Lagged leverage as a control would help but is not included (understandably, as it would subsume the contemporaneous uncertainty signal). |
| No lagged DV control | MODERATE | Standard leverage regressions often include lagged leverage to capture partial adjustment dynamics (Lemmon, Roberts & Zender 2008). The absence of a lagged DV makes coefficients harder to interpret as marginal effects. |

---

## L. Audit-Safety / Academic-Integrity Assessment

| Dimension | Assessment |
|-----------|------------|
| P-hacking risk | LOW-MODERATE: Two-tailed test is appropriate. But with 4 IVs x 16 specs = 64 IV-level tests, there is substantial multiple testing exposure. No familywise error rate correction discussed. |
| Selective reporting risk | **HIGH** (due to G1): The LaTeX table only shows 8 of 16 models. If DebtToCapital results are weaker or contradictory, a reader would never know. This is a de facto selective reporting problem even if unintentional. |
| HARKing risk | LOW: The two-tailed test and explicit "no directional prediction" note mitigate HARKing. |
| Data snooping | LOW: Main sample restriction is standard and pre-registered in the research design. |

---

## M. Master Red-Team Issue Register

| ID | Severity | Category | Description | Status | Recommendation |
|----|----------|----------|-------------|--------|---------------|
| RT-H4-01 | **CRITICAL** | Output | LaTeX table `_save_latex_table()` hardcodes `n_cols=8`, omitting DebtToCapital models (cols 9-16) from the thesis-facing table. | OPEN | Either (a) produce TWO 8-column tables (Panel A: BookLev, Panel B: DebtToCapital) or (b) produce one 16-column table. Update docstring and first-layer audit accordingly. |
| RT-H4-02 | **MAJOR** | Identification | No multicollinearity diagnostics (VIF, condition number) for 4 simultaneous uncertainty IVs. | OPEN | Add VIF computation after regression. Report VIF for each IV in model_diagnostics.csv. Flag if any VIF > 10. |
| RT-H4-03 | **MAJOR** | Estimation | `check_rank=False` suppresses rank deficiency warnings in industry FE specification. | OPEN | Remove `check_rank=False` or explicitly document why rank checking is disabled and what the rank of the design matrix is. |
| RT-H4-04 | MODERATE | Construction | Asymmetric DV construction: `BookLev` (contemporaneous) is raw merge_asof value; `BookLev_lead` is fiscal-year-deduplicated then shifted. Different within-group variation. | OPEN | Document this asymmetry in the provenance doc. Consider whether `BookLev_t` (from temporal function) should be used as contemporaneous DV for consistency. |
| RT-H4-05 | MODERATE | Documentation | First-layer audit Moulton concern says "constant within firm-quarter" -- technically correct but misleading when panel is indexed by fiscal year. | OPEN | Clarify that BookLev varies across quarters within a fiscal year, so the Moulton concern applies only to within-quarter clustering, not the full fiscal-year panel index. |
| RT-H4-06 | MODERATE | Sample | Summary statistics computed on pre-complete-case sample; may not match estimation sample. | OPEN | Compute summary stats on the intersection sample (complete cases + min calls) used in estimation. |
| RT-H4-07 | MODERATE | Construction | No maximum staleness guard on merge_asof: Compustat data from arbitrarily old quarters can match to recent calls. | OPEN | Add a `tolerance` parameter to merge_asof (e.g., 180 days) or document the distribution of match gaps. |
| RT-H4-08 | MODERATE | Identification | No discussion of autocorrelation in leverage making lead-DV tests difficult to interpret. | OPEN | Acknowledge persistence in leverage and discuss implications in thesis text. |
| RT-H4-09 | LOW-MODERATE | Construction | `fillna(0)` for missing dlcq/dlttq assumes missing = zero debt. No `.clip(lower=0)` applied to BookLev (unlike TobinsQ). | OPEN | Add `.clip(lower=0)` after fillna, or document why negative leverage is acceptable. |
| RT-H4-10 | LOW-MODERATE | Output | Attrition table only tracks BookLev sample path; DebtToCapital attrition not separately documented. | OPEN | Add a DebtToCapital-specific attrition line or produce separate attrition for each DV. |
| RT-H4-11 | LOW | Documentation | Runner docstring says `col{1-8}` output files; actual code produces `col{1-16}`. | OPEN | Update docstring to reflect 16 model specifications. |
| RT-H4-12 | LOW | Robustness | No double-clustering (firm + year) sensitivity analysis. | OPEN | Add as robustness check or document why single-cluster is sufficient. |

---

## N. What a Committee Would Still Not Know

After reading both the first-layer audit and this red-team report, a thesis committee would still lack:

1. **Actual regression results** -- Both audits acknowledge that no fresh run output has been verified. The committee has no evidence that the code runs successfully or what the results look like.
2. **DebtToCapital results** -- Even if the code runs, the LaTeX table omits these. The committee would need to inspect `model_diagnostics.csv` directly.
3. **Multicollinearity severity** -- No VIF or correlation matrix among the 4 uncertainty IVs.
4. **Economic magnitude** -- No standardized coefficients or back-of-envelope calculations showing the economic significance of results.
5. **Sample overlap with other suites** -- How much does the H4 estimation sample overlap with H1 (CashHoldings)? Since they share the same IVs and similar controls, are the results independent?
6. **Leverage persistence** -- No AR(1) coefficient for BookLev reported. Without knowing how persistent leverage is, the committee cannot assess whether contemporaneous vs lead DV results are meaningfully different.
7. **DebtToCapital NaN rate** -- How many observations are lost due to the `denominator <= 0` condition? If substantial, the DebtToCapital sample may have survivorship bias toward healthy firms.

---

## O. Priority Fixes

| Priority | Issue ID | Action Required | Effort |
|----------|----------|----------------|--------|
| 1 (blocker) | RT-H4-01 | Fix `_save_latex_table()` to produce complete output for all 16 models (either one table with panels or two separate tables). | Low -- mechanical code change |
| 2 (pre-defense) | RT-H4-02 | Add VIF computation and report in diagnostics. | Low -- add ~10 lines post-regression |
| 3 (pre-defense) | RT-H4-03 | Remove `check_rank=False` or add explicit rank diagnostic. | Low -- one-line change + verification |
| 4 (pre-defense) | RT-H4-11 | Update runner docstring to reflect 16 models. | Trivial |
| 5 (recommended) | RT-H4-06 | Move summary stats to post-filter sample. | Low |
| 6 (recommended) | RT-H4-05 | Correct Moulton description in provenance doc. | Trivial |
| 7 (recommended) | RT-H4-10 | Add DebtToCapital attrition tracking. | Low |

---

## P. Final Red-Team Readiness Statement

**Verdict: CONDITIONAL PASS -- not submission-ready without fixes.**

The H4 suite has a sound econometric design (appropriate FE structure, correct clustering, honest two-tailed testing) and the first-layer audit correctly identified and resolved the critical `fyearq_int` bug. However, the first-layer audit missed a critical output defect: the LaTeX table omits half the results. Combined with missing multicollinearity diagnostics and the suppressed rank-check warning, the suite requires targeted fixes before it meets thesis-defense standards.

The minimum viable fix set is: (1) repair the LaTeX table to show all 16 models, (2) add VIF diagnostics, (3) re-enable or justify `check_rank=False`, and (4) update the runner docstring. These are all low-effort changes that do not require re-running the regressions.

The broader identification concerns (endogeneity, leverage persistence, multiple testing) are substantive limitations that should be acknowledged in the thesis text but do not constitute implementation defects.

---

*Report generated by second-layer red-team auditor. All claims verified against source code as of 2026-03-18.*
