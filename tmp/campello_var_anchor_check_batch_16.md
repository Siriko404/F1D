# Variable Anchor Check — Batch 16 (VAR_76 – VAR_80)

Generated: 2026-05-26 by `tmp/batched_var_verifier.py 16`
Anchor sources: PyMuPDF full main paper (45pp) + supplement (19pp); Table 1 stats anchor (300 cells).

Checks per variable: (1) definition_verbatim found in paper? (2) claimed page matches? (3) Table 1 stats (when applicable) match anchor?

## VAR_76 — USD/British pound FX rate / vol(FX$£)
- **role**: Control
- **claimed**: §§IV.A.1 (equation (13) controls), page 3191
- **definition (first 200ch)**: We include control variables, CONTROLS_t, consisting of vol(SP500) and vol(FX$£) into equation (13) ……
- **CHECK 1 — definition in paper**: `NOT_FOUND` — definition probe not located in main+supp corpus
- **CHECK 2 — page match**: `N/A` — no found page to compare
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **FAIL (definition not in paper)**

## VAR_77 — equity returns / vol(r_it)
- **role**: Other: raw input (LHS of eq 13)
- **claimed**: §§IV.A.1 (equation (13)), page 3191
- **definition (first 200ch)**: Equation (13) uses the volatility of equity returns, vol(r_it), as a proxy for firm income volatility, vol(v_it).…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p14 (printed p3191)
- **CHECK 2 — page match**: `MATCH` — claimed=3191, found=p3191
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **PASS**

## VAR_78 — I/B/E/S 1-year-ahead EPS forecasts (mean and standard deviation)
- **role**: Other: raw input to forecast-uncertainty figures + CONSENSUS_EARNINGS_FORECAST
- **claimed**: §§IV.C.2 text, page 3195
- **definition (first 200ch)**: Beginning in 2015:Q1, we obtain the 1-year-ahead earnings per share (EPS) forecasts for each firm in our sample and compute the mean and standard deviation of forecasts.…
- **CHECK 1 — definition in paper**: `NOT_FOUND` — definition probe not located in main+supp corpus
- **CHECK 2 — page match**: `N/A` — no found page to compare
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper (as table); plotted in Figure 4 (p. 3195)
- **VERDICT**: **FAIL (definition not in paper)**

## VAR_79 — YTS establishment-level employment / establishment counts
- **role**: Other: raw input to establishment-level DVs
- **claimed**: §§IV.B text, page 3193
- **definition (first 200ch)**: The YTS database is compiled from historical business files from Infogroup and are linked longitudinally to track establishment location, employment, and sales information at the establishment-year le…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p16 (printed p3193)
- **CHECK 2 — page match**: `MATCH` — claimed=3193, found=p3193
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper (as moments)
- **VERDICT**: **PASS**

## VAR_80 — establishment openings and closings
- **role**: Other: raw input to ESTABLISHMENT_TURNOVER
- **claimed**: §Footnote 24, page 3203
- **definition (first 200ch)**: Establishment turnover is defined as the sum of establishment openings and closings, divided by the lagged number of total establishments.…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p26 (printed p3203)
- **CHECK 2 — page match**: `MATCH` — claimed=3203, found=p3203
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **PASS**

## Batch summary
- PASS: 3
- FAIL: 2
- INCONCLUSIVE: 0
- OTHER: 0