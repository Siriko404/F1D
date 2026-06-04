# Variable Anchor Check — Batch 3 (VAR_11 – VAR_15)

Generated: 2026-05-26 by `tmp/batched_var_verifier.py 3`
Anchor sources: PyMuPDF full main paper (45pp) + supplement (19pp); Table 1 stats anchor (300 cells).

Checks per variable: (1) definition_verbatim found in paper? (2) claimed page matches? (3) Table 1 stats (when applicable) match anchor?

## VAR_11 — INVESTMENT (U.K.-based subsidiaries)
- **role**: DV
- **claimed**: §§V.B.1.a text + Table 4 notes, page 3202
- **definition (first 200ch)**: We similarly calculate the total U.K.-based investment of each U.S. parent firm by summing spending figures across U.K. subsidiaries.…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p25 (printed p3202)
- **CHECK 2 — page match**: `MATCH` — claimed=3202, found=p3202
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **PASS**

## VAR_12 — AUTOMATIONi,t
- **role**: DV
- **claimed**: §Table E.2 notes, page IA p. 18 (Internet Appendix)
- **definition (first 200ch)**: The dependent variable is AUTOMATIONi,t, which is constructed from a dictionary of keywords that capture exposure to automation at the firm level, as described in Appendix E. This text-based continuou…
- **CHECK 1 — definition in paper**: `NOT_FOUND` — definition probe not located in main+supp corpus
- **CHECK 2 — page match**: `N/A` — no found page to compare
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **FAIL (definition not in paper)**

## VAR_13 — βUK_i (β_i^UK)
- **role**: Treatment
- **claimed**: §§IV.A.1 text + equation (13), page 3191
- **definition (first 200ch)**: Following Bloom (2014), we use stock market volatility as a gauge of aggregate uncertainty and estimate equation (12) for each firm i as vol(r_it) = α_i + β_i^UK vol(FTSE100_t) + θCONTROLS_t + ϵ_it (1…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p14 (printed p3191)
- **CHECK 2 — page match**: `MATCH` — claimed=3191, found=p3191
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper (no distributional moments table)
- **VERDICT**: **PASS**

## VAR_14 — HIGH_UK_EXPOSURE_i / HIGH_βUK_i
- **role**: Treatment
- **claimed**: §§IV.C.3 text (equation (14) variable definitions), page 3196
- **definition (first 200ch)**: HIGH_UK_EXPOSURE_i is a dummy variable that equals 1 if firm i is U.K.-exposed, and 0 otherwise. A firm is considered to be U.K.-exposed according to two measures: i) if it belongs to the top tercile …
- **CHECK 1 — definition in paper**: `NOT_FOUND` — definition probe not located in main+supp corpus
- **CHECK 2 — page match**: `N/A` — no found page to compare
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **FAIL (definition not in paper)**

## VAR_15 — number of Brexit-related entries in 2015 10-K (count)
- **role**: Treatment
- **claimed**: §§IV.A.2, page 3191
- **definition (first 200ch)**: we look for the number of entries of keywords related to uncertainty about Brexit (\"Brexit,\" \"Great Britain,\" and \"Uncertainty\") in firms' disclosures, classifying firms with a \"high\" number o…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p14 (printed p3191)
- **CHECK 2 — page match**: `MATCH` — claimed=3191, found=p3191
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper (as distribution)
- **VERDICT**: **PASS**

## Batch summary
- PASS: 3
- FAIL: 2
- INCONCLUSIVE: 0
- OTHER: 0