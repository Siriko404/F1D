# STRICT deviation ledger — all vars × panels vs Campello Table 1

Source: machine artifact `campello_summary_stats_compare_2026_05_17.md` (no rebuild). Severity = max over mean/SD/med/IQR/N; near-zero Campello mean/med also judged by |Δ|/C\_SD. NO same-ballpark masking. No spec change; no verdict (gated on Sina).

| rank | variable | panel | severity | status | driving moments |
|--|--|--|--|--|--|
| 1 | CASH_T8 (cheq/(atq-cheq)_l1) | A/Universe | SEVERE | EXPLAINED — §A net-of-cash DV defect (ratified DV; necessary-not-sufficient; DV-fix δ̂ −0.007 NS) | mean Δ+0.389 (177%, 1.56·SD); sd Δ+1.399 (560%); med Δ+0.024 (20%, 0.10·SD); iqr Δ+0.106 (39%); n Δ-18127.000 (23%) |
| 2 | CASH_T8 (cheq/(atq-cheq)_l1) | B/Treated | SEVERE | EXPLAINED — §A net-of-cash DV defect (ratified DV; necessary-not-sufficient; DV-fix δ̂ −0.007 NS) | mean Δ+0.398 (199%, 1.66·SD); sd Δ+1.518 (632%); iqr Δ+0.076 (29%); n Δ+1217.000 (11%) |
| 3 | CASH_T8 (cheq/(atq-cheq)_l1) | C/Control | SEVERE | EXPLAINED — §A net-of-cash DV defect (ratified DV; necessary-not-sufficient; DV-fix δ̂ −0.007 NS) | mean Δ+0.214 (126%, 1.19·SD); sd Δ+0.742 (412%); med Δ+0.026 (24%, 0.14·SD); iqr Δ+0.099 (52%) |
| 4 | CONSENSUS_EPS | A/Universe | SEVERE | EXPLAINED — §B within-firm z-score ≠ Campello 'standardized' (SD 0.79 vs 3.51); construction choice, not data | mean Δ-0.070 (100%, 0.02·SD); sd Δ-2.717 (77%); med Δ-0.173 (192%, 0.05·SD); iqr Δ-1.011 (49%) |
| 5 | CONSENSUS_EPS | B/Treated | SEVERE | EXPLAINED — §B within-firm z-score ≠ Campello 'standardized' (SD 0.79 vs 3.51); construction choice, not data | mean Δ+0.006 (60%, 0.00·SD); sd Δ-2.534 (75%); med Δ-0.042 (420%, 0.01·SD); iqr Δ-0.645 (35%) |
| 6 | CONSENSUS_EPS | C/Control | SEVERE | EXPLAINED — §B within-firm z-score ≠ Campello 'standardized' (SD 0.79 vs 3.51); construction choice, not data | mean Δ-0.047 (67%, 0.02·SD); sd Δ-1.584 (68%); med Δ-0.115 (287%, 0.05·SD); iqr Δ-1.448 (60%); n Δ-1297.000 (12%) |
| 7 | CASH_FLOW | A/Universe | MAJOR | **NEW — needs root-cause** | mean Δ+0.010 (100%, 0.17·SD); iqr Δ-0.007 (18%); n Δ-16123.000 (21%) |
| 8 | CASH_FLOW | B/Treated | MAJOR | **NEW — needs root-cause** | mean Δ+0.005 (50%, 0.08·SD); med Δ+0.004 (20%, 0.07·SD); n Δ+1284.000 (12%) |
| 9 | SIZE | A/Universe | MAJOR | **NEW — needs root-cause** | iqr Δ-0.420 (14%); n Δ-21615.000 (28%) |
| 10 | STOCK_RETURNS | B/Treated | MAJOR | **NEW — needs root-cause** | mean Δ-0.005 (25%, 0.02·SD); n Δ+1148.000 (10%) |
| 11 | CASH_FLOW | C/Control | MINOR | **NEW — needs root-cause** | sd Δ-0.004 (10%); med Δ+0.003 (10%, 0.08·SD) |
| 12 | CASH_T1 (cheq/atq_l1) | A/Universe | MINOR | **NEW — needs root-cause** | n Δ-18126.000 (23%) |
| 13 | CASH_T1 (cheq/atq_l1) | B/Treated | MINOR | **NEW — needs root-cause** | n Δ+1217.000 (11%) |
| 14 | SALES_GROWTH | A/Universe | MINOR | **NEW — needs root-cause** | sd Δ-0.097 (16%); n Δ-11359.000 (16%) |
| 15 | SALES_GROWTH | B/Treated | MINOR | **NEW — needs root-cause** | mean Δ+0.027 (15%, 0.04·SD); sd Δ+0.123 (17%); n Δ+1849.000 (17%) |
| 16 | SALES_GROWTH | C/Control | MINOR | **NEW — needs root-cause** | sd Δ-0.068 (19%) |
| 17 | SIZE | B/Treated | MINOR | **NEW — needs root-cause** | iqr Δ-0.292 (10%) |
| 18 | SIZE | C/Control | MINOR | **NEW — needs root-cause** | n Δ-1266.000 (10%) |
| 19 | STOCK_RETURNS | A/Universe | MINOR | **NEW — needs root-cause** | med Δ+0.003 (15%, 0.01·SD); n Δ-8680.000 (13%) |
| 20 | TOBIN_Q | A/Universe | MINOR | **NEW — needs root-cause** | n Δ-13772.000 (19%) |
| 21 | TOBIN_Q | B/Treated | MINOR | **NEW — needs root-cause** | n Δ+1230.000 (11%) |
| 22 | CASH_T1 (cheq/atq_l1) | C/Control | OK | OK | all moments <10% |
| 23 | STOCK_RETURNS | C/Control | OK | OK | all moments <10% |
| 24 | TOBIN_Q | C/Control | OK | OK | all moments <10% |

## Aggregate read (NO verdict — gated)
- SEVERE/MAJOR & already root-caused: 6 (CASH_T8 §A ×3, CONSENSUS_EPS §B ×3).
- SEVERE/MAJOR & **NEW (unexplained)**: 4 → CASH_FLOW/A/Universe, CASH_FLOW/B/Treated, SIZE/A/Universe, STOCK_RETURNS/B/Treated
- MINOR cluster: SD low in 4 cells, IQR low in 1 cells → consistent under-dispersion vs Campello (direction: our βᵁᴷ-estimable universe = larger, less-volatile firms; documented sample-composition skew, NOT garbage — but it IS a real systematic deviation to record).

## Worklist (Sina-directed: check ALL devs)
1. NEW MAJOR/SEVERE (if any above) — root-cause first.
2. CASH_T8 / CONSENSUS_EPS — already root-caused (§A/§B); remediation Sina-gated (Table-1 denom; forecast/price).
3. MINOR under-dispersion cluster — decide: accept as documented composition caveat, or audit step1/βᵁᴷ sample screens that drive the larger-firm skew. No spec change without explicit Sina authorization.
