# Variable Anchor Check — Batch 8 (VAR_36 – VAR_40)

Generated: 2026-05-26 by `tmp/batched_var_verifier.py 8`
Anchor sources: PyMuPDF full main paper (45pp) + supplement (19pp); Table 1 stats anchor (300 cells).

Checks per variable: (1) definition_verbatim found in paper? (2) claimed page matches? (3) Table 1 stats (when applicable) match anchor?

## VAR_36 — POST × HIGH_βCOUNTRY_i  (POST·HIGH_β^COUNTRY)
- **role**: Robustness
- **claimed**: §Table 13 (row header), page 3216
- **definition (first 200ch)**: treated firms are in the highest tercile of positive values of exposure of firm-level volatility to equity index volatility in the European Union, China, Mexico, Japan, India, and Brazil, respectively…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p39 (printed p3216)
- **CHECK 2 — page match**: `MATCH` — claimed=3216, found=p3216
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper (regression coefficient only)
- **VERDICT**: **PASS**

## VAR_37 — POST × HIGH_βUK_i,CF  (POST·HIGH_β_i,CF^UK)
- **role**: Robustness
- **claimed**: §Table C.6 (row header + notes), page IA p. 11
- **definition (first 200ch)**: The treatment group is composed by the top tercile of β^UK_i,CF, while the control group is composed by firms in the bottom tercile of β^UK_i,CF.…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p23 (printed p3200)
- **CHECK 2 — page match**: `MISMATCH` — claimed=IA p. 11, found=p3200
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper (regression coefficient only)
- **VERDICT**: **FAIL (page mismatch)**

## VAR_38 — TOBIN_Q (Tobin's Q)
- **role**: Control
- **claimed**: §Table 1 notes, page 3198
- **definition (first 200ch)**: TOBIN_Q is defined as the market value of assets divided by the book value of assets, and is calculated as the market value of equity plus the book value of assets minus book value of equity plus defe…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p21 (printed p3198)
- **CHECK 2 — page match**: `MATCH` — claimed=3198, found=p3198
- **CHECK 3 — Table 1 stats**: `PANEL_A_MATCH` — 4/4 cells
    - ✓ mean: inventory=2.11, anchor=2.11
    - ✓ SD: inventory=1.59, anchor=1.59
    - ✓ median: inventory=1.57, anchor=1.57
    - ✓ N: inventory=73353, anchor=73353
- **VERDICT**: **PASS**

## VAR_39 — CASH_FLOW
- **role**: Control
- **claimed**: §Table 1 notes, page 3198
- **definition (first 200ch)**: CASH_FLOW is defined as operating income before depreciation divided by lagged total assets.…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p21 (printed p3198)
- **CHECK 2 — page match**: `MATCH` — claimed=3198, found=p3198
- **CHECK 3 — Table 1 stats**: `PANEL_A_MATCH` — 4/4 cells
    - ✓ mean: inventory=0.01, anchor=0.01
    - ✓ SD: inventory=0.06, anchor=0.06
    - ✓ median: inventory=0.03, anchor=0.03
    - ✓ N: inventory=75287, anchor=75287
- **VERDICT**: **PASS**

## VAR_40 — SIZE (Log Assets)
- **role**: Control
- **claimed**: §Table 1 notes, page 3198
- **definition (first 200ch)**: SIZE is defined as the logarithm of total assets.…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p21 (printed p3198)
- **CHECK 2 — page match**: `MATCH` — claimed=3198, found=p3198
- **CHECK 3 — Table 1 stats**: `PANEL_A_MATCH` — 4/4 cells
    - ✓ mean: inventory=6.19, anchor=6.19
    - ✓ SD: inventory=2.08, anchor=2.08
    - ✓ median: inventory=6.15, anchor=6.15
    - ✓ N: inventory=78062, anchor=78062
- **VERDICT**: **PASS**

## Batch summary
- PASS: 4
- FAIL: 1
- INCONCLUSIVE: 0
- OTHER: 0