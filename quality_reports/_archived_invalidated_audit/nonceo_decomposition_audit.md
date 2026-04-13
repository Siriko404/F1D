# NoCEO Decomposition Audit

**Auditor:** Second-layer adversarial auditor  
**Date:** 2026-04-03  
**Source files:** `model_diagnostics.csv` from each suite's `nonceo_decomp` output directory  
**Method:** Every p-value read directly from CSV; significance threshold p < 0.10

---

## Verified Counts (from model_diagnostics.csv)

### H1 Cash Holdings (one-tailed, p_one)

| Col | DV             | FE          | IV            |       Beta |       SE |   p_one | Sig |
|----:|:---------------|:------------|:--------------|-----------:|---------:|--------:|:----|
|   1 | CashRatio      | industry    | UncAnsNoCEO   |  0.0007230 | 0.000688 | 0.14666 |     |
|   1 | CashRatio      | industry    | UncAnsCEO     |  0.0018973 | 0.000847 | 0.01254 | **  |
|   2 | CashRatio      | firm        | UncAnsNoCEO   |  0.0004825 | 0.000593 | 0.20780 |     |
|   2 | CashRatio      | firm        | UncAnsCEO     |  0.0011140 | 0.000678 | 0.05024 | *   |
|   3 | CashRatio      | industry    | UncAnsNoCEO   |  0.0009784 | 0.000752 | 0.09651 | *   |
|   3 | CashRatio      | industry    | UncAnsCEO     |  0.0020835 | 0.000864 | 0.00795 | *** |
|   4 | CashRatio      | firm        | UncAnsNoCEO   |  0.0006061 | 0.000615 | 0.16203 |     |
|   4 | CashRatio      | firm        | UncAnsCEO     |  0.0008565 | 0.000710 | 0.11388 |     |
|   5 | CashRatio      | industry_yq | UncAnsNoCEO   |  0.0009352 | 0.000690 | 0.08769 | *   |
|   5 | CashRatio      | industry_yq | UncAnsCEO     |  0.0021478 | 0.000979 | 0.01412 | **  |
|   6 | CashRatio      | firm_yq     | UncAnsNoCEO   |  0.0005497 | 0.000638 | 0.19447 |     |
|   6 | CashRatio      | firm_yq     | UncAnsCEO     |  0.0009393 | 0.000845 | 0.13323 |     |
|   7 | CashRatio_lead | industry    | UncAnsNoCEO   | -0.0008473 | 0.001118 | 0.77575 |     |
|   7 | CashRatio_lead | industry    | UncAnsCEO     |  0.0030870 | 0.001728 | 0.03700 | **  |
|   8 | CashRatio_lead | firm        | UncAnsNoCEO   | -0.0007751 | 0.000930 | 0.79758 |     |
|   8 | CashRatio_lead | firm        | UncAnsCEO     |  0.0033231 | 0.001088 | 0.00113 | *** |
|   9 | CashRatio_lead | industry    | UncAnsNoCEO   | -0.0006181 | 0.001116 | 0.71010 |     |
|   9 | CashRatio_lead | industry    | UncAnsCEO     |  0.0032534 | 0.001634 | 0.02323 | **  |
|  10 | CashRatio_lead | firm        | UncAnsNoCEO   | -0.0007926 | 0.000872 | 0.81834 |     |
|  10 | CashRatio_lead | firm        | UncAnsCEO     |  0.0029638 | 0.001017 | 0.00179 | *** |
|  11 | CashRatio_lead | industry_yq | UncAnsNoCEO   | -0.0006270 | 0.001021 | 0.73032 |     |
|  11 | CashRatio_lead | industry_yq | UncAnsCEO     |  0.0032386 | 0.001757 | 0.03264 | **  |
|  12 | CashRatio_lead | firm_yq     | UncAnsNoCEO   | -0.0008297 | 0.000839 | 0.83860 |     |
|  12 | CashRatio_lead | firm_yq     | UncAnsCEO     |  0.0028693 | 0.001362 | 0.01759 | **  |

**UncAnsNoCEO significant: 2/12** (Col 3 industry ext p=0.097; Col 5 industry_yq ext p=0.088)  
**UncAnsCEO significant: 10/12** (all except Col 4 firm ext p=0.114 and Col 6 firm_yq ext p=0.133)

---

### H4 Leverage (two-tailed, p_two, 24 total: 12 Leverage + 12 DebtToCapital)

| Col | DV                 | FE          | IV            |       Beta |       SE |   p_two | Sig |
|----:|:-------------------|:------------|:--------------|-----------:|---------:|--------:|:----|
|   1 | Leverage           | industry    | UncAnsNoCEO   | -0.0000872 | 0.000757 | 0.90829 |     |
|   1 | Leverage           | industry    | UncAnsCEO     |  0.0011461 | 0.001116 | 0.30442 |     |
|   2 | Leverage           | firm        | UncAnsNoCEO   | -0.0003205 | 0.000762 | 0.67422 |     |
|   2 | Leverage           | firm        | UncAnsCEO     | -0.0003346 | 0.001201 | 0.78057 |     |
|   3 | Leverage           | industry    | UncAnsNoCEO   |  0.0000255 | 0.000801 | 0.97463 |     |
|   3 | Leverage           | industry    | UncAnsCEO     |  0.0008306 | 0.001162 | 0.47464 |     |
|   4 | Leverage           | firm        | UncAnsNoCEO   | -0.0002717 | 0.000791 | 0.73117 |     |
|   4 | Leverage           | firm        | UncAnsCEO     | -0.0001391 | 0.001153 | 0.90399 |     |
|   5 | Leverage           | industry_yq | UncAnsNoCEO   |  0.0000408 | 0.000694 | 0.95310 |     |
|   5 | Leverage           | industry_yq | UncAnsCEO     |  0.0007175 | 0.001144 | 0.53045 |     |
|   6 | Leverage           | firm_yq     | UncAnsNoCEO   | -0.0002453 | 0.000697 | 0.72494 |     |
|   6 | Leverage           | firm_yq     | UncAnsCEO     | -0.0001901 | 0.001107 | 0.86368 |     |
|   7 | Leverage_lead      | industry    | UncAnsNoCEO   | -0.0013512 | 0.001327 | 0.30869 |     |
|   7 | Leverage_lead      | industry    | UncAnsCEO     |  0.0032345 | 0.002217 | 0.14453 |     |
|   8 | Leverage_lead      | firm        | UncAnsNoCEO   | -0.0016153 | 0.000992 | 0.10333 |     |
|   8 | Leverage_lead      | firm        | UncAnsCEO     |  0.0002175 | 0.002496 | 0.93055 |     |
|   9 | Leverage_lead      | industry    | UncAnsNoCEO   | -0.0011934 | 0.001409 | 0.39706 |     |
|   9 | Leverage_lead      | industry    | UncAnsCEO     |  0.0032798 | 0.002195 | 0.13520 |     |
|  10 | Leverage_lead      | firm        | UncAnsNoCEO   | -0.0013520 | 0.001005 | 0.17850 |     |
|  10 | Leverage_lead      | firm        | UncAnsCEO     |  0.0008573 | 0.002522 | 0.73394 |     |
|  11 | Leverage_lead      | industry_yq | UncAnsNoCEO   | -0.0010650 | 0.001347 | 0.42907 |     |
|  11 | Leverage_lead      | industry_yq | UncAnsCEO     |  0.0033593 | 0.002157 | 0.11941 |     |
|  12 | Leverage_lead      | firm_yq     | UncAnsNoCEO   | -0.0011569 | 0.001066 | 0.27800 |     |
|  12 | Leverage_lead      | firm_yq     | UncAnsCEO     |  0.0012111 | 0.002121 | 0.56800 |     |
|  13 | DebtToCapital      | industry    | UncAnsNoCEO   | -0.0005531 | 0.001126 | 0.62340 |     |
|  13 | DebtToCapital      | industry    | UncAnsCEO     |  0.0028095 | 0.001590 | 0.07726 | *   |
|  14 | DebtToCapital      | firm        | UncAnsNoCEO   | -0.0000548 | 0.000952 | 0.95410 |     |
|  14 | DebtToCapital      | firm        | UncAnsCEO     |  0.0024798 | 0.001820 | 0.17300 |     |
|  15 | DebtToCapital      | industry    | UncAnsNoCEO   | -0.0002465 | 0.001201 | 0.83739 |     |
|  15 | DebtToCapital      | industry    | UncAnsCEO     |  0.0023925 | 0.001696 | 0.15840 |     |
|  16 | DebtToCapital      | firm        | UncAnsNoCEO   | -0.0000124 | 0.001125 | 0.99118 |     |
|  16 | DebtToCapital      | firm        | UncAnsCEO     |  0.0025656 | 0.001718 | 0.13541 |     |
|  17 | DebtToCapital      | industry_yq | UncAnsNoCEO   | -0.0001841 | 0.001190 | 0.87704 |     |
|  17 | DebtToCapital      | industry_yq | UncAnsCEO     |  0.0022034 | 0.001743 | 0.20629 |     |
|  18 | DebtToCapital      | firm_yq     | UncAnsNoCEO   |  0.0000553 | 0.001109 | 0.96028 |     |
|  18 | DebtToCapital      | firm_yq     | UncAnsCEO     |  0.0024454 | 0.001657 | 0.13991 |     |
|  19 | DebtToCapital_lead | industry    | UncAnsNoCEO   | -0.0029950 | 0.002150 | 0.16369 |     |
|  19 | DebtToCapital_lead | industry    | UncAnsCEO     |  0.0002199 | 0.003720 | 0.95285 |     |
|  20 | DebtToCapital_lead | firm        | UncAnsNoCEO   | -0.0022012 | 0.001686 | 0.19163 |     |
|  20 | DebtToCapital_lead | firm        | UncAnsCEO     | -0.0000930 | 0.004095 | 0.98188 |     |
|  21 | DebtToCapital_lead | industry    | UncAnsNoCEO   | -0.0028744 | 0.002212 | 0.19371 |     |
|  21 | DebtToCapital_lead | industry    | UncAnsCEO     |  0.0003824 | 0.003817 | 0.92019 |     |
|  22 | DebtToCapital_lead | firm        | UncAnsNoCEO   | -0.0020551 | 0.001608 | 0.20121 |     |
|  22 | DebtToCapital_lead | firm        | UncAnsCEO     |  0.0006883 | 0.004018 | 0.86399 |     |
|  23 | DebtToCapital_lead | industry_yq | UncAnsNoCEO   | -0.0026417 | 0.002160 | 0.22125 |     |
|  23 | DebtToCapital_lead | industry_yq | UncAnsCEO     |  0.0005648 | 0.003571 | 0.87432 |     |
|  24 | DebtToCapital_lead | firm_yq     | UncAnsNoCEO   | -0.0017167 | 0.001548 | 0.26730 |     |
|  24 | DebtToCapital_lead | firm_yq     | UncAnsCEO     |  0.0014370 | 0.003312 | 0.66435 |     |

**UncAnsNoCEO significant: 0/24**  
**UncAnsCEO significant: 1/24** (Col 13 DebtToCapital, industry, base, p=0.077 *)

---

### H13 Capex (two-tailed, p_two)

| Col | DV         | FE          | IV            |       Beta |       SE |   p_two | Sig |
|----:|:-----------|:------------|:--------------|-----------:|---------:|--------:|:----|
|   1 | Capex      | industry    | UncAnsNoCEO   |  0.0004452 | 0.000275 | 0.10541 |     |
|   1 | Capex      | industry    | UncAnsCEO     |  0.0006104 | 0.000437 | 0.16206 |     |
|   2 | Capex      | firm        | UncAnsNoCEO   |  0.0000193 | 0.000228 | 0.93261 |     |
|   2 | Capex      | firm        | UncAnsCEO     |  0.0008067 | 0.000353 | 0.02215 | **  |
|   3 | Capex      | industry    | UncAnsNoCEO   |  0.0005092 | 0.000264 | 0.05338 | *   |
|   3 | Capex      | industry    | UncAnsCEO     |  0.0006827 | 0.000425 | 0.10853 |     |
|   4 | Capex      | firm        | UncAnsNoCEO   |  0.0000010 | 0.000236 | 0.99647 |     |
|   4 | Capex      | firm        | UncAnsCEO     |  0.0007816 | 0.000374 | 0.03641 | **  |
|   5 | Capex      | industry_yq | UncAnsNoCEO   |  0.0004754 | 0.000272 | 0.08029 | *   |
|   5 | Capex      | industry_yq | UncAnsCEO     |  0.0006234 | 0.000412 | 0.13066 |     |
|   6 | Capex      | firm_yq     | UncAnsNoCEO   | -0.0000241 | 0.000255 | 0.92465 |     |
|   6 | Capex      | firm_yq     | UncAnsCEO     |  0.0006116 | 0.000376 | 0.10350 |     |
|   7 | Capex_lead | industry    | UncAnsNoCEO   |  0.0005260 | 0.000352 | 0.13488 |     |
|   7 | Capex_lead | industry    | UncAnsCEO     |  0.0005991 | 0.000770 | 0.43629 |     |
|   8 | Capex_lead | firm        | UncAnsNoCEO   | -0.0000707 | 0.000306 | 0.81717 |     |
|   8 | Capex_lead | firm        | UncAnsCEO     |  0.0006103 | 0.000507 | 0.22906 |     |
|   9 | Capex_lead | industry    | UncAnsNoCEO   |  0.0005328 | 0.000341 | 0.11803 |     |
|   9 | Capex_lead | industry    | UncAnsCEO     |  0.0007059 | 0.000721 | 0.32754 |     |
|  10 | Capex_lead | firm        | UncAnsNoCEO   | -0.0001460 | 0.000326 | 0.65446 |     |
|  10 | Capex_lead | firm        | UncAnsCEO     |  0.0006631 | 0.000475 | 0.16243 |     |
|  11 | Capex_lead | industry_yq | UncAnsNoCEO   |  0.0005048 | 0.000358 | 0.15860 |     |
|  11 | Capex_lead | industry_yq | UncAnsCEO     |  0.0007462 | 0.000607 | 0.21863 |     |
|  12 | Capex_lead | firm_yq     | UncAnsNoCEO   | -0.0001600 | 0.000305 | 0.60030 |     |
|  12 | Capex_lead | firm_yq     | UncAnsCEO     |  0.0006327 | 0.000435 | 0.14561 |     |

**UncAnsNoCEO significant: 2/12** (Col 3 Capex industry ext p=0.053 *; Col 5 Capex industry_yq ext p=0.080 *)  
**UncAnsCEO significant: 2/12** (Col 2 Capex firm base p=0.022 **; Col 4 Capex firm ext p=0.036 **)

---

### H16 R&D Sales (two-tailed, p_two)

| Col | DV           | FE          | IV            |       Beta |       SE |   p_two | Sig |
|----:|:-------------|:------------|:--------------|-----------:|---------:|--------:|:----|
|   1 | RDSales      | industry    | UncAnsNoCEO   |  0.0125152 | 0.006505 | 0.05438 | *   |
|   1 | RDSales      | industry    | UncAnsCEO     |  0.0143745 | 0.008040 | 0.07381 | *   |
|   2 | RDSales      | firm        | UncAnsNoCEO   |  0.0077113 | 0.005353 | 0.14969 |     |
|   2 | RDSales      | firm        | UncAnsCEO     | -0.0035577 | 0.003325 | 0.28466 |     |
|   3 | RDSales      | industry    | UncAnsNoCEO   |  0.0117950 | 0.006363 | 0.06379 | *   |
|   3 | RDSales      | industry    | UncAnsCEO     |  0.0144740 | 0.008242 | 0.07907 | *   |
|   4 | RDSales      | firm        | UncAnsNoCEO   |  0.0078265 | 0.005334 | 0.14227 |     |
|   4 | RDSales      | firm        | UncAnsCEO     | -0.0053291 | 0.003700 | 0.14975 |     |
|   5 | RDSales      | industry_yq | UncAnsNoCEO   |  0.0115448 | 0.006361 | 0.06954 | *   |
|   5 | RDSales      | industry_yq | UncAnsCEO     |  0.0143952 | 0.008308 | 0.08314 | *   |
|   6 | RDSales      | firm_yq     | UncAnsNoCEO   |  0.0074458 | 0.005123 | 0.14608 |     |
|   6 | RDSales      | firm_yq     | UncAnsCEO     | -0.0055801 | 0.004216 | 0.18568 |     |
|   7 | RDSales_lead | industry    | UncAnsNoCEO   | -0.0001408 | 0.002665 | 0.95787 |     |
|   7 | RDSales_lead | industry    | UncAnsCEO     |  0.0202218 | 0.008683 | 0.01986 | **  |
|   8 | RDSales_lead | firm        | UncAnsNoCEO   | -0.0020073 | 0.002726 | 0.46156 |     |
|   8 | RDSales_lead | firm        | UncAnsCEO     | -0.0054379 | 0.005887 | 0.35564 |     |
|   9 | RDSales_lead | industry    | UncAnsNoCEO   | -0.0010046 | 0.003080 | 0.74426 |     |
|   9 | RDSales_lead | industry    | UncAnsCEO     |  0.0191766 | 0.008782 | 0.02900 | **  |
|  10 | RDSales_lead | firm        | UncAnsNoCEO   | -0.0019427 | 0.002811 | 0.48944 |     |
|  10 | RDSales_lead | firm        | UncAnsCEO     | -0.0048018 | 0.005220 | 0.35761 |     |
|  11 | RDSales_lead | industry_yq | UncAnsNoCEO   | -0.0006867 | 0.003218 | 0.83102 |     |
|  11 | RDSales_lead | industry_yq | UncAnsCEO     |  0.0190100 | 0.009771 | 0.05172 | *   |
|  12 | RDSales_lead | firm_yq     | UncAnsNoCEO   | -0.0017787 | 0.003457 | 0.60689 |     |
|  12 | RDSales_lead | firm_yq     | UncAnsCEO     | -0.0048098 | 0.005582 | 0.38886 |     |

**UncAnsNoCEO significant: 3/12** (Cols 1,3,5 -- all current RDSales at Industry FE, p = 0.054, 0.064, 0.070)  
**UncAnsCEO significant: 6/12** (Cols 1,3,5 at *, Cols 7,9 at **, Col 11 at *)

---

## Reviewer Claim Verification

| # | Reviewer | Claim | Actual | Result | Severity |
|--:|:---------|:------|:-------|:-------|:---------|
| 1 | DA | UncAnsNoCEO null across ALL 60 specs (0/60) | 7/60 significant (H1:2, H4:0, H13:2, H16:3) | **MISMATCH** | CRITICAL |
| 2 | DA | UncAnsNoCEO H1: 0/12 | 2/12 | **MISMATCH** | CRITICAL |
| 3 | DA | UncAnsNoCEO H4: 0/24 | 0/24 | MATCH | -- |
| 4 | DA | UncAnsNoCEO H16: 0/12 | 3/12 | **MISMATCH** | CRITICAL |
| 5 | DA | UncAnsNoCEO H13: 0/12 | 2/12 | **MISMATCH** | CRITICAL |
| 6 | DA | UncAnsCEO H1: 9/12 | 10/12 | **MISMATCH** | MODERATE |
| 7 | DA | UncAnsCEO H16: 2/12 | 6/12 | **MISMATCH** | CRITICAL |
| 8 | DA | UncAnsCEO H13: 2/12 | 2/12 | MATCH | -- |
| 9 | thesis_findings | H1 UncAnsNoCEO 2/12 marginal * | 2/12 * | MATCH | -- |
| 10 | thesis_findings | H1 UncAnsCEO 10/12 | 10/12 | MATCH | -- |
| 11 | thesis_findings | H16 UncAnsCEO 6/12 | 6/12 | MATCH | -- |
| 12 | thesis_findings | H16 UncAnsNoCEO 3/12 marginal * | 3/12 * | MATCH | -- |
| 13 | thesis_findings | H13 UncAnsCEO 2/12 (**) | 2/12 (**) | MATCH | -- |
| 14 | thesis_findings | H13 UncAnsNoCEO 2/12 marginal * | 2/12 (*) | MATCH | -- |
| 15 | thesis_findings | H4 UncAnsCEO 1/24 marginal | 1/24 (*) | MATCH | -- |
| 16 | thesis_findings | H4 UncAnsNoCEO 0/24 | 0/24 | MATCH | -- |
| 17 | R3 | H1 UncAnsCEO 10/12 | 10/12 | MATCH | -- |
| 18 | R3 | H1 UncAnsNoCEO 2/12 (Industry FE only, p~0.09-0.15) | 2/12 (Industry FE, p=0.088-0.097) | PARTIAL MATCH | MINOR (p range wrong) |
| 19 | R3 | H16 UncAnsCEO 6/12 | 6/12 | MATCH | -- |
| 20 | R3 | H16 UncAnsNoCEO 3/12 (current-DV, Industry FE, p~0.05-0.07) | 3/12 (current RDSales, Industry FE, p=0.054-0.070) | MATCH | -- |
| 21 | R3 | H13 UncAnsCEO 2/12 (Firm FE only, **) | 2/12 (Firm FE, **) | MATCH | -- |
| 22 | R3 | H13 UncAnsNoCEO 2/12 (Industry FE only, marginal) | 2/12 (Industry FE, *) | MATCH | -- |
| 23 | R3 | H4 UncAnsCEO 1/24 marginal | 1/24 (*) | MATCH | -- |
| 24 | R3 | H4 UncAnsNoCEO 0/24 | 0/24 | MATCH | -- |
| 25 | EIC | UncAnsCEO 10/12 for H1 | 10/12 | MATCH | -- |
| 26 | EIC | UncAnsCEO 6/12 for H16 | 6/12 | MATCH | -- |
| 27 | R1 | CEO drives signal 10/12 vs 2/12 in H1 | 10/12 vs 2/12 | MATCH | -- |

---

## Summary of Errors Found

### CRITICAL errors (6 total, all from Devil's Advocate)

1. **DA claimed UncAnsNoCEO is null across ALL 60 specs (0/60).** Actual: 7/60 are significant at p<0.10. The DA fabricated a blanket-null claim that is wrong in 3 of 4 suites.

2. **DA claimed UncAnsNoCEO H1: 0/12.** Actual: 2/12 significant (Col 3 p=0.097, Col 5 p=0.088, both one-tailed).

3. **DA claimed UncAnsNoCEO H16: 0/12.** Actual: 3/12 significant (Cols 1,3,5 at p=0.054, 0.064, 0.070, all two-tailed). This is the worst miss -- three specs with p-values well below 0.10.

4. **DA claimed UncAnsNoCEO H13: 0/12.** Actual: 2/12 significant (Col 3 p=0.053, Col 5 p=0.080, both two-tailed). Col 3 at p=0.053 is particularly notable.

5. **DA claimed UncAnsCEO H1: 9/12.** Actual: 10/12. Off by 1.

6. **DA claimed UncAnsCEO H16: 2/12.** Actual: 6/12. Off by 4. This is a severe counting error that drastically understates CEO significance in H16.

### MINOR issues (1 total)

7. **R3 stated H1 UncAnsNoCEO p range as "approximately 0.09-0.15".** Actual range is 0.088-0.097. Both values are below 0.10 (i.e., formally significant at 10%), yet R3 framed them as if some fell above 0.10. The count of 2/12 is correct; the characterization as "marginal" is slightly misleading since both pass the 10% threshold.

### Reviewers with zero errors

- **thesis_findings.txt**: All 8 claims verified correct.
- **EIC**: Both claims verified correct.
- **R1**: Claim verified correct.
- **R3**: All counts correct; one minor p-range characterization issue.

### Root cause of DA errors

The Devil's Advocate appears to have either (a) not actually read the model_diagnostics.csv files, or (b) applied an incorrect significance threshold (e.g., using p<0.05 instead of p<0.10 for the * cutoff). The blanket "null across ALL 60 specs" claim is factually false and materially misleading about the NoCEO decomposition results.
