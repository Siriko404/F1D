# Audit 03: Findings Section (III.4)
**Date:** 2026-03-13
**Auditor:** Claude Agent
**Scope:** Lines 126-164 of thesis_draft.tex
**Verdict:** PASS WITH ISSUES

---

## H0.3 Findings Audit (lines 129-136)

**Source files:**
- `outputs/econometric/ceo_clarity_extended/2026-03-13_053119/model_diagnostics.csv`
- `outputs/econometric/ceo_clarity_extended/2026-03-13_053119/regression_results_manager_baseline.txt`
- `outputs/econometric/ceo_clarity_extended/2026-03-13_053119/regression_results_ceo_baseline.txt`
- `outputs/econometric/ceo_clarity_extended/2026-03-13_053119/regression_results_manager_extended.txt`
- `outputs/econometric/ceo_clarity_extended/2026-03-13_053119/regression_results_ceo_extended.txt`

### Numbers Verified

| # | Claim in Draft | Actual Value (Source) | Match? |
|---|---|---|---|
| 1 | Manager Baseline N = 53,070 | 53070 (model_diagnostics.csv, row 2) | YES |
| 2 | Manager Baseline R^2 = 0.418 | 0.41774 (model_diagnostics.csv, row 2; regression header shows 0.418) | YES |
| 3 | Manager_Pres_Uncertainty_pct = 0.096 | 0.0962 (regression line 2499) | YES |
| 4 | Analyst_QA_Uncertainty_pct = 0.033 | 0.0326 (regression line 2500) | YES |
| 5 | Entire_All_Negative_pct = 0.077 | 0.0772 (regression line 2501) | YES |
| 6 | All three p < 0.001 | All show P>\|z\| = 0.000 (lines 2499-2501) | YES |
| 7 | CEO Baseline N = 38,671 | 38671 (model_diagnostics.csv, row 4) | YES |
| 8 | CEO Baseline R^2 = 0.372 | 0.37168 (model_diagnostics.csv, row 4; regression header shows 0.372) | YES |
| 9 | CEO_Pres_Uncertainty_pct = 0.093 | 0.0928 (regression line 1948) | YES |
| 10 | CEO Analyst_QA = 0.033 | 0.0330 (regression line 1949) | YES |
| 11 | CEO Negative_pct = 0.062 | 0.0625 (regression line 1950) | YES |
| 12 | CEO "all p < 0.001" | All show P>\|z\| = 0.000 (lines 1948-1950) | YES |
| 13 | Manager Extended N = 51,569 | 51569 (model_diagnostics.csv, row 3) | YES |
| 14 | Manager Extended R^2 = 0.420 | 0.42041 (model_diagnostics.csv, row 3) | YES |
| 15 | Manager Extended Manager_Pres = 0.097 | 0.0974 (regression line 2445) | YES |
| 16 | Manager Extended Analyst_QA = 0.033 | 0.0332 (regression line 2446) | YES |
| 17 | Manager Extended Negative = 0.079 | 0.0791 (regression line 2447) | YES |
| 18 | Manager Extended all p < 0.001 | All P>\|z\| = 0.000 (lines 2445-2447) | YES |
| 19 | Extended ROA = 0.005, p = 0.047 | coef = 0.0048, P>\|z\| = 0.047 (line 2455) | YES |
| 20 | Extended Volatility = 0.006, p = 0.007 | coef = 0.0057, P>\|z\| = 0.007 (line 2458) | YES |
| 21 | Extended CurrentRatio = 0.005, p = 0.062 | coef = 0.0055, P>\|z\| = 0.062 (line 2456) | YES |
| 22 | Lev not significant | P>\|z\| = 0.105 (line 2454) | YES |
| 23 | Size not significant | P>\|z\| = 0.994 (line 2452) | YES |
| 24 | BM not significant | P>\|z\| = 0.230 (line 2453) | YES |
| 25 | RD_Intensity not significant | P>\|z\| = 0.999 (line 2457) | YES |
| 26 | EPS_Growth Baseline p = 0.049 | P>\|z\| = 0.049 (regression_manager_baseline line 2504) | YES |
| 27 | EPS_Growth Extended p = 0.245 | P>\|z\| = 0.245 (regression_manager_extended line 2450) | YES |
| 28 | CEO Extended N = 37,517 | 37517 (model_diagnostics.csv, row 5) | YES |
| 29 | CEO Extended R^2 = 0.372 | 0.37165 (model_diagnostics.csv, row 5; regression header shows 0.372) | YES |
| 30 | CEO Extended CEO_Pres = 0.095 | 0.0946 (regression line 1906) | YES |
| 31 | CEO Extended ROA = 0.008, p = 0.012 | coef = 0.0081, P>\|z\| = 0.012 (line 1916) | YES |

### Discrepancies Found

**None.** All 31 H0.3 numbers verified correct.

### Notes
- The Extended specifications for H0.3 are part of the main analysis (not robustness), consistent with the audit rules permitting "H0.3 Extended models."
- All coefficients are rounded to 3 decimal places in the draft; rounding is consistent with source values.

---

## H7 Findings Audit (lines 143-146)

**Source files:**
- `outputs/econometric/h7_illiquidity/2026-03-13_054310/model_diagnostics.csv`
- `outputs/econometric/h7_illiquidity/2026-03-13_054310/regression_Main_A1.txt` through `regression_Main_B2.txt`

### Numbers Verified

| # | Claim in Draft | Actual Value (Source) | Match? |
|---|---|---|---|
| 32 | "no uncertainty measure reaches statistical significance at 5%" | All beta1_p_one > 0.05 in diagnostics CSV; best is A3 at 0.069 | YES |
| 33 | Manager_QA beta = 0.329, one-tailed p = 0.069 | A3: beta1 = 0.3285, beta1_p_one = 0.06876 (diagnostics CSV line 4) | YES |
| 34 | Manager_Pres beta = 0.110, p = 0.135 | A4: beta1 = 0.1100, beta1_p_one = 0.13518 (diagnostics CSV line 5) | YES |
| 35 | CEO_QA beta = -0.063, p = 0.814 | A1: beta1 = -0.0630, beta1_p_one = 0.81369 (diagnostics CSV line 2) | YES |
| 36 | CEO_Pres beta = -0.023, p = 0.769 | A2: beta1 = -0.02285, beta1_p_one = 0.76937 (diagnostics CSV line 3) | YES |
| 37 | A5 Wald chi^2 = 2.757, p = 0.097 | wald_chi2 = 2.7572, wald_pval = 0.09682 (diagnostics CSV line 8) | YES |
| 38 | CEO_Clarity_Residual beta = 0.015, p = 0.165 | B1: beta1 = 0.01505, beta1_p_one = 0.16503 (diagnostics CSV line 6) | YES |
| 39 | Manager_Clarity_Residual beta = 0.007, p = 0.080 | B2: beta1 = 0.00725, beta1_p_one = 0.07957 (diagnostics CSV line 7) | YES |
| 40 | pre_call_amihud positive in manager variants, beta ~ 1.09, p = 0.016 | A3: 1.0867, p = 0.0164; A4: 1.0864, p = 0.0165 (regression files) | YES |
| 41 | pre_call_amihud negative in residual variants, beta ~ -0.71 to -0.79, p < 0.001 | B1: -0.7935, p = 0.0000; B2: -0.7136, p = 0.0000 (regression files) | YES |
| 42 | within-R^2 is very low (0.001-0.012) | A1: 0.0014, A2: 0.0014, A3: 0.0123, A4: 0.0123, A5: 0.0123 (regression files) | YES |
| 43 | Size and ROA reach significance in B1, B2 but not A1-A5 | B1 Size p=0.041, B2 Size p=0.030, B2 ROA p=0.012; A1-A5 all Size/ROA p > 0.19 | PARTIAL (see below) |

### Discrepancies Found

**D1 (MINOR): H7 B1 ROA is marginally significant, not significant at 5%.**
- Draft claims: "Size and ROA reach significance in the clarity-residual specifications (B1, B2)"
- Actual: B1 ROA p = 0.0638 (marginally significant at 10%, NOT at 5%). B2 ROA p = 0.0117 (significant).
- B1 Size p = 0.0410 (significant). B2 Size p = 0.0299 (significant).
- **Severity: MINOR.** The claim is accurate for B2 and for Size in both B1/B2, but overstates ROA significance in B1.
- **Suggested fix:** "Size reaches significance in both B1 and B2, and ROA is significant in B2 (p = 0.012) and marginally so in B1 (p = 0.064)."

**D2 (MINOR): Inconsistent one-tailed p-value labeling in H7.**
- The draft labels A3 as "one-tailed p = 0.069" but does NOT label A4, A1, or A2 p-values as one-tailed, even though ALL H7 p-values reported are one-tailed values from the diagnostics CSV (beta1_p_one column).
- A4: reports p = 0.135 (actual one-tailed = 0.135; two-tailed = 0.270)
- A1: reports p = 0.814 (actual one-tailed = 0.814; two-tailed = 0.373)
- A2: reports p = 0.769 (actual one-tailed = 0.769; two-tailed = 0.461)
- B1: reports p = 0.165 (actual one-tailed = 0.165; two-tailed = 0.330)
- B2: reports p = 0.080 (actual one-tailed = 0.080; two-tailed = 0.159)
- **Severity: MINOR but potentially confusing.** Either label ALL as one-tailed or be explicit about the convention.

### Robustness Mentions Flagged

**R1: A5 Wald test -- NOT a robustness concern.**
- The draft reports the joint Wald test from Model A5 (chi^2 = 2.757, p = 0.097). Model A5 is one of the 7 main specifications listed in model_diagnostics.csv. The Wald test is a standard diagnostic within the main model, not a robustness extension. **No flag needed.**

**R2: H7 robustness_results.csv file exists in output directory.**
- The file contains two-way clustering, pre/post-GFC splits, large-firm subsample, and FF12 industry-stratified results.
- **However, NONE of these are mentioned in the draft text.** The draft only reports the 7 main models (A1-A5, B1-B2). **No robustness violation in the draft text.**

---

## H14 Findings Audit (lines 148-151)

**Source files:**
- `outputs/econometric/h14_bidask_spread/2026-03-13_053119/model_diagnostics.csv`
- `outputs/econometric/h14_bidask_spread/2026-03-13_053119/regression_results_Main_*.txt` (6 files)
- `outputs/econometric/h14_bidask_spread/2026-03-13_053119/summary_stats.csv`

### Numbers Verified

| # | Claim in Draft | Actual Value (Source) | Match? |
|---|---|---|---|
| 44 | CEO_Pres beta = 0.0004, one-tailed p = 0.024 | beta1 = 0.000405, beta1_p_one = 0.02385 (diagnostics CSV line 5) | YES |
| 45 | "0.71% standard-deviation increase" | beta * SD_x / SD_y = 0.000405 * 0.3901 / 0.0222 = 0.00712 = 0.71% (summary_stats.csv) | YES |
| 46 | Manager_QA beta = 0.0001, p = 0.353 | beta1 = 8.52e-05, beta1_p_one = 0.3529 (diagnostics CSV line 2) | YES |
| 47 | CEO_QA beta = 0.0000, p = 0.421 | beta1 = 3.84e-05, beta1_p_one = 0.4209 (diagnostics CSV line 3) | YES |
| 48 | Manager_Pres beta = 0.0002, p = 0.223 | beta1 = 0.000165, beta1_p_one = 0.2225 (diagnostics CSV line 4) | YES |
| 49 | Manager_Clarity_Residual beta = 0.0000, p = 0.418 | beta1 = 4.91e-05, beta1_p_one = 0.4175 (diagnostics CSV line 6) | YES |
| 50 | CEO_Clarity_Residual beta = 0.0001, p = 0.396 | beta1 = 5.46e-05, beta1_p_one = 0.3959 (diagnostics CSV line 7) | YES |
| 51 | PreCallSpread beta ~ -0.70 | Range across 6 models: -0.689 to -0.706 (regression files) | YES |
| 52 | R^2 ranges from 0.457 to 0.466 | Within-R^2: 0.4568, 0.4571, 0.4616, 0.4617, 0.4620, 0.4660 (regression files) | YES |

### Discrepancies Found

**D3 (MINOR): H14 p-values are one-tailed but only CEO_Pres is labeled as such.**
- Same issue as H7. The remaining 5 H14 p-values are taken from the beta1_p_one column but are not labeled "one-tailed" in the text.
- **Severity: MINOR.** All values are numerically correct; the labeling is inconsistent.

### Robustness Mentions Flagged

**None.** The draft reports only the 6 main specifications. A `robustness` subdirectory and `robustness_diagnostics.csv` file exist in the output but are not referenced in the draft text.

---

## H9 Findings Audit (lines 153-164)

**Source files:**
- `outputs/econometric/takeover/2026-03-13_053120/hazard_ratios.csv`
- `outputs/econometric/takeover/2026-03-13_053120/model_diagnostics.csv`

### Numbers Verified

| # | Claim in Draft | Actual Value (Source) | Match? |
|---|---|---|---|
| 53 | ClarityCEO -> All: HR = 0.997, p = 0.964 | exp_coef = 0.99739, p = 0.9644 (hazard_ratios.csv line 2) | YES |
| 54 | CEO_Clarity_Residual -> All: HR = 1.110, p = 0.600 | exp_coef = 1.10962, p = 0.6001 (hazard_ratios.csv line 8) | YES |
| 55 | Manager_Clarity_Residual -> All: HR = 0.940, p = 0.787 | exp_coef = 0.94039, p = 0.7865 (hazard_ratios.csv line 14) | YES |
| 56 | ClarityCEO -> Uninvited: HR = 1.112, p = 0.529 | exp_coef = 1.11176, p = 0.5285 (hazard_ratios.csv line 20) | YES |
| 57 | CEO_Clarity_Residual -> Uninvited: HR = 1.002, p = 0.997 | exp_coef = 1.00178, p = 0.9974 (hazard_ratios.csv line 26) | YES |
| 58 | Manager_Clarity_Residual -> Uninvited: HR = 1.339, p = 0.646 | exp_coef = 1.33852, p = 0.6456 (hazard_ratios.csv line 32) | YES |
| 59 | Uninvited sample: "36-46 events" | CEO=40, CEO_Residual=36, Manager_Residual=46 (model_diagnostics.csv lines 5-7) | YES |
| 60 | ClarityCEO -> Friendly: HR = 1.008, p = 0.908 | exp_coef = 1.00754, p = 0.9079 (hazard_ratios.csv line 38) | YES |
| 61 | CEO_Clarity_Residual -> Friendly: HR = 1.127, p = 0.584 | exp_coef = 1.12739, p = 0.5839 (hazard_ratios.csv line 44) | YES |
| 62 | Manager_Clarity_Residual -> Friendly: HR = 0.902, p = 0.679 | exp_coef = 0.90178, p = 0.6795 (hazard_ratios.csv line 50) | YES |
| 63 | Friendly events: "224-289 events" | CEO=250, CEO_Residual=224, Manager_Residual=289 (model_diagnostics.csv lines 8-10) | YES |

### Discrepancies Found

**None.** All 11 H9 numbers verified correct.

### Robustness Mentions Flagged

**None.** The draft correctly limits H9 discussion to the 9 sparse-specification models. The output directory contains expanded, strata_year, and strata_industry results (27 additional models visible in model_diagnostics.csv), but none of these are mentioned in the draft text.

---

## Cross-Section Checks

### One-tailed vs Two-tailed Labeling
**D4 (MODERATE): Inconsistent labeling of one-tailed p-values across H7 and H14.**

All p-values reported for H7 and H14 are one-tailed (from the beta1_p_one column in diagnostics CSVs), but only two instances are explicitly labeled:
- H7 A3: "one-tailed p = 0.069" -- labeled
- H14 CEO_Pres: "one-tailed p = 0.024" -- labeled
- All other H7 and H14 p-values: NOT labeled as one-tailed

This is problematic because:
1. For negative coefficients in H7 (A1, A2), the one-tailed p-values (0.814, 0.769) are LARGER than two-tailed (0.373, 0.461). A reader unfamiliar with the convention might assume these are two-tailed.
2. A consistent convention statement (e.g., "all p-values are one-tailed in the predicted direction") would resolve this.

### Significance Stars
No significance stars are used in the prose text; p-values are reported directly. This is appropriate.

### Summary Paragraph Accuracy
- H7/H14 summary (line 151): Accurately characterizes the overall null pattern with the one marginal H7 and one significant H14 result. Correct.
- H9 summary (line 164): Accurately describes uniformly null results. Correct.

---

## Summary

| Metric | Count |
|---|---|
| **Total numbers audited** | 63 |
| **Verified correct** | 62 |
| **Discrepancies found** | 4 |
| **-- Critical (wrong number)** | 0 |
| **-- Moderate** | 1 (D4: inconsistent one-tailed labeling) |
| **-- Minor** | 3 (D1: B1 ROA overstatement; D2: H7 p-value labeling; D3: H14 p-value labeling) |
| **Robustness mentions flagged** | 0 |

### Recommended Actions

1. **D1:** Qualify the claim about ROA in H7 B1 (p = 0.064, not < 0.05).
2. **D2/D3/D4 (combined):** Add a footnote or parenthetical stating: "All H7 and H14 p-values are one-tailed in the predicted direction (beta > 0)." This resolves the labeling inconsistency across all three discrepancies.

### Verdict: PASS WITH ISSUES
All 63 numerical claims are traced to source output files and are numerically correct. The four issues are all about labeling/characterization, not about wrong numbers. No prohibited robustness content was found for H7, H14, or H9.
