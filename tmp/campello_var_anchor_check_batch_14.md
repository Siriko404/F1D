# Variable Anchor Check — Batch 14 (VAR_66 – VAR_70)

Generated: 2026-05-26 by `tmp/batched_var_verifier.py 14`
Anchor sources: PyMuPDF full main paper (45pp) + supplement (19pp); Table 1 stats anchor (300 cells).

Checks per variable: (1) definition_verbatim found in paper? (2) claimed page matches? (3) Table 1 stats (when applicable) match anchor?

## VAR_66 — cash and short-term investments
- **role**: Other: raw input to CASH
- **claimed**: §Table 1 notes (within CASH definition), page 3198
- **definition (first 200ch)**: CASH is defined as cash and short-term investments divided by lagged total assets.…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p21 (printed p3198)
- **CHECK 2 — page match**: `MATCH` — claimed=3198, found=p3198
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper (only scaled CASH)
- **VERDICT**: **PASS**

## VAR_67 — working capital (net of cash)
- **role**: Other: raw input to NWC
- **claimed**: §Table 1 notes (within NWC definition), page 3198
- **definition (first 200ch)**: NON_CASH_WORKING_CAPITAL is defined as working capital (net of cash) divided by lagged total assets.…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p21 (printed p3198)
- **CHECK 2 — page match**: `MATCH` — claimed=3198, found=p3198
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper (only scaled NWC)
- **VERDICT**: **PASS**

## VAR_68 — operating income before depreciation
- **role**: Other: raw input to CASH_FLOW and PROFITS
- **claimed**: §Table 1 notes (within CASH_FLOW definition), page 3198
- **definition (first 200ch)**: CASH_FLOW is defined as operating income before depreciation divided by lagged total assets.…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p21 (printed p3198)
- **CHECK 2 — page match**: `MATCH` — claimed=3198, found=p3198
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **PASS**

## VAR_69 — sales
- **role**: Other: raw input to SALES_GROWTH and PROFITS
- **claimed**: §Table 1 notes (within SALES_GROWTH definition), page 3198
- **definition (first 200ch)**: SALES_GROWTH is defined as the year-on-year percentage change in quarterly sales.…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p21 (printed p3198)
- **CHECK 2 — page match**: `MATCH` — claimed=3198, found=p3198
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **PASS**

## VAR_70 — market value of equity
- **role**: Other: raw input to TOBIN_Q (and SIZE / sample filter via market value)
- **claimed**: §Table 1 notes (within TOBIN_Q definition), page 3198
- **definition (first 200ch)**: TOBIN_Q … is calculated as the market value of equity plus the book value of assets minus book value of equity plus deferred taxes, all divided by book value of assets.…
- **CHECK 1 — definition in paper**: `NOT_FOUND` — definition probe not located in main+supp corpus
- **CHECK 2 — page match**: `N/A` — no found page to compare
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **FAIL (definition not in paper)**

## Batch summary
- PASS: 4
- FAIL: 1
- INCONCLUSIVE: 0
- OTHER: 0