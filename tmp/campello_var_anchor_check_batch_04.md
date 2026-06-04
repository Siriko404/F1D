# Variable Anchor Check — Batch 4 (VAR_16 – VAR_20)

Generated: 2026-05-26 by `tmp/batched_var_verifier.py 4`
Anchor sources: PyMuPDF full main paper (45pp) + supplement (19pp); Table 1 stats anchor (300 cells).

Checks per variable: (1) definition_verbatim found in paper? (2) claimed page matches? (3) Table 1 stats (when applicable) match anchor?

## VAR_16 — HIGH_10K_ENTRIES (printed: 'HIGH_10K_ENTRIES' / 'Treatment is > 5 Brexit Entries in 10-Ks')
- **role**: Treatment
- **claimed**: §§IV.C.1, page 3193
- **definition (first 200ch)**: Under this approach, 807 firms are assigned to the treated category (2015 10-K mentions of Brexit terms > 5). A total of 433 firms in the control category have no mentions of Brexit-related terms in t…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p16 (printed p3193)
- **CHECK 2 — page match**: `MATCH` — claimed=3193, found=p3193
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **PASS**

## VAR_17 — POST_t
- **role**: Treatment
- **claimed**: §§IV.C.3 (equation (14) variable definitions), page 3196
- **definition (first 200ch)**: POST_t equals 1 if the time period is in the 2016:Q3–Q4 window.…
- **CHECK 1 — definition in paper**: `NOT_FOUND` — definition probe not located in main+supp corpus
- **CHECK 2 — page match**: `N/A` — no found page to compare
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **FAIL (definition not in paper)**

## VAR_18 — βUK_i,CF (β_i,CF^UK)
- **role**: Robustness
- **claimed**: §Footnote 13, page 3191
- **definition (first 200ch)**: Following Vuolteenaho (2002), we also decompose the volatility of each firm's returns into cash flow and discount rate components and reestimate equation (13) with the cash flow component (only) as th…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p14 (printed p3191)
- **CHECK 2 — page match**: `MATCH` — claimed=3191, found=p3191
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **PASS**

## VAR_19 — βEU_i (β_i^EU)
- **role**: Robustness
- **claimed**: §§VI.F text + Table 13, page 3216
- **definition (first 200ch)**: we repeat our tests classifying firms based on a given criterion (β_i^EU, β_i^CHINA, β_i^MEXICO, β_i^JAPAN, β_i^INDIA, and β_i^BRAZIL) according to the sensitivity of their equity returns volatility t…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p39 (printed p3216)
- **CHECK 2 — page match**: `MATCH` — claimed=3216, found=p3216
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **PASS**

## VAR_20 — βCHINA_i (β_i^CHINA)
- **role**: Robustness
- **claimed**: §§VI.F text + Table 13, page 3216
- **definition (first 200ch)**: we repeat our tests classifying firms based on a given criterion (β_i^EU, β_i^CHINA, β_i^MEXICO, β_i^JAPAN, β_i^INDIA, and β_i^BRAZIL) according to the sensitivity of their equity returns volatility t…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p39 (printed p3216)
- **CHECK 2 — page match**: `MATCH` — claimed=3216, found=p3216
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **PASS**

## Batch summary
- PASS: 4
- FAIL: 1
- INCONCLUSIVE: 0
- OTHER: 0