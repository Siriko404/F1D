# Variable Anchor Check — Batch 9 (VAR_41 – VAR_45)

Generated: 2026-05-26 by `tmp/batched_var_verifier.py 9`
Anchor sources: PyMuPDF full main paper (45pp) + supplement (19pp); Table 1 stats anchor (300 cells).

Checks per variable: (1) definition_verbatim found in paper? (2) claimed page matches? (3) Table 1 stats (when applicable) match anchor?

## VAR_41 — SALES_GROWTH
- **role**: Control
- **claimed**: §Table 1 notes, page 3198
- **definition (first 200ch)**: SALES_GROWTH is defined as the year-on-year percentage change in quarterly sales.…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p21 (printed p3198)
- **CHECK 2 — page match**: `MATCH` — claimed=3198, found=p3198
- **CHECK 3 — Table 1 stats**: `PANEL_A_MATCH` — 4/4 cells
    - ✓ mean: inventory=0.16, anchor=0.16
    - ✓ SD: inventory=0.62, anchor=0.62
    - ✓ median: inventory=0.06, anchor=0.06
    - ✓ N: inventory=71637, anchor=71637
- **VERDICT**: **PASS**

## VAR_42 — CONSENSUS_EARNINGS_FORECAST
- **role**: Control
- **claimed**: §Table 1 notes, page 3198
- **definition (first 200ch)**: CONSENSUS_EARNINGS_FORECAST is defined as the standardized mean 1-quarter ahead earnings per share forecast.…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p21 (printed p3198)
- **CHECK 2 — page match**: `MATCH` — claimed=3198, found=p3198
- **CHECK 3 — Table 1 stats**: `PANEL_A_MATCH` — 4/4 cells
    - ✓ mean: inventory=0.07, anchor=0.07
    - ✓ SD: inventory=3.51, anchor=3.51
    - ✓ median: inventory=0.09, anchor=0.09
    - ✓ N: inventory=42031, anchor=42031
- **VERDICT**: **PASS**

## VAR_43 — STOCK_RETURNS (lagged stock returns)
- **role**: Control
- **claimed**: §Table 1 notes, page 3198
- **definition (first 200ch)**: STOCK_RETURNS are defined as the quarterly buy-and-hold return.…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p21 (printed p3198)
- **CHECK 2 — page match**: `MATCH` — claimed=3198, found=p3198
- **CHECK 3 — Table 1 stats**: `NAME_MISMATCH` — normalized=STOCKRETURNSLAGGEDSTOCKRETURNS, no anchor variant matched
- **VERDICT**: **INCONCLUSIVE**

## VAR_44 — lagged U.S. dollar/British pound FX rate
- **role**: Control
- **claimed**: §§IV.C.3 (Empirical Model, control list), page 3197
- **definition (first 200ch)**: Macro controls include the lagged U.S. dollar/British pound FX rate, the lagged VIX implied volatility index, the lagged mean GDP growth 1-year-ahead forecast from the Federal Reserve Bank of Philadel…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p20 (printed p3197)
- **CHECK 2 — page match**: `MATCH` — claimed=3197, found=p3197
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **PASS**

## VAR_45 — lagged VIX implied volatility index
- **role**: Control
- **claimed**: §§IV.C.3 (control list), page 3197
- **definition (first 200ch)**: Macro controls include the lagged U.S. dollar/British pound FX rate, the lagged VIX implied volatility index, the lagged mean GDP growth 1-year-ahead forecast from the Federal Reserve Bank of Philadel…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p20 (printed p3197)
- **CHECK 2 — page match**: `MATCH` — claimed=3197, found=p3197
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **PASS**

## Batch summary
- PASS: 4
- FAIL: 0
- INCONCLUSIVE: 1
- OTHER: 0