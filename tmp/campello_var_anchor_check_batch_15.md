# Variable Anchor Check — Batch 15 (VAR_71 – VAR_75)

Generated: 2026-05-26 by `tmp/batched_var_verifier.py 15`
Anchor sources: PyMuPDF full main paper (45pp) + supplement (19pp); Table 1 stats anchor (300 cells).

Checks per variable: (1) definition_verbatim found in paper? (2) claimed page matches? (3) Table 1 stats (when applicable) match anchor?

## VAR_71 — book value of assets
- **role**: Other: raw input to TOBIN_Q
- **claimed**: §Table 1 notes (within TOBIN_Q definition), page 3198
- **definition (first 200ch)**: TOBIN_Q is defined as the market value of assets divided by the book value of assets ……
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p21 (printed p3198)
- **CHECK 2 — page match**: `MATCH` — claimed=3198, found=p3198
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **PASS**

## VAR_72 — book value of equity
- **role**: Other: raw input to TOBIN_Q
- **claimed**: §Table 1 notes (within TOBIN_Q definition), page 3198
- **definition (first 200ch)**: … the market value of equity plus the book value of assets minus book value of equity plus deferred taxes, all divided by book value of assets.…
- **CHECK 1 — definition in paper**: `NOT_FOUND` — definition probe not located in main+supp corpus
- **CHECK 2 — page match**: `N/A` — no found page to compare
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **FAIL (definition not in paper)**

## VAR_73 — deferred taxes
- **role**: Other: raw input to TOBIN_Q
- **claimed**: §Table 1 notes (within TOBIN_Q definition), page 3198
- **definition (first 200ch)**: … minus book value of equity plus deferred taxes, all divided by book value of assets.…
- **CHECK 1 — definition in paper**: `NOT_FOUND` — definition probe not located in main+supp corpus
- **CHECK 2 — page match**: `N/A` — no found page to compare
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **FAIL (definition not in paper)**

## VAR_74 — FTSE100 Index / vol(FTSE100_t)
- **role**: Other: raw input to β_i^UK (eq 13)
- **claimed**: §§IV.A.1 (equation (13) discussion), page 3191
- **definition (first 200ch)**: It also uses the volatility of the FTSE100 Index as a proxy for uncertainty in the U.K. (the relevant source of aggregate uncertainty in our setting).…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p14 (printed p3191)
- **CHECK 2 — page match**: `MATCH` — claimed=3191, found=p3191
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper (as summary stats)
- **VERDICT**: **PASS**

## VAR_75 — S&P 500 Index / vol(SP500)
- **role**: Control
- **claimed**: §§IV.A.1 (equation (13) controls), page 3191
- **definition (first 200ch)**: We include control variables, CONTROLS_t, consisting of vol(SP500) and vol(FX$£) into equation (13) to absorb effects arising through firms' exposure to the domestic U.S. market and exchange rate fluc…
- **CHECK 1 — definition in paper**: `NOT_FOUND` — definition probe not located in main+supp corpus
- **CHECK 2 — page match**: `N/A` — no found page to compare
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **FAIL (definition not in paper)**

## Batch summary
- PASS: 2
- FAIL: 3
- INCONCLUSIVE: 0
- OTHER: 0