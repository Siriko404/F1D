# Variable Anchor Check — Batch 2 (VAR_06 – VAR_10)

Generated: 2026-05-26 by `tmp/batched_var_verifier.py 2`
Anchor sources: PyMuPDF full main paper (45pp) + supplement (19pp); Table 1 stats anchor (300 cells).

Checks per variable: (1) definition_verbatim found in paper? (2) claimed page matches? (3) Table 1 stats (when applicable) match anchor?

## VAR_06 — NON_CASH_WORKING_CAPITAL (NWC)
- **role**: DV
- **claimed**: §Table 1 notes, page 3198
- **definition (first 200ch)**: NON_CASH_WORKING_CAPITAL is defined as working capital (net of cash) divided by lagged total assets.…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p21 (printed p3198)
- **CHECK 2 — page match**: `MATCH` — claimed=3198, found=p3198
- **CHECK 3 — Table 1 stats**: `PANEL_A_MATCH` — 4/4 cells
    - ✓ mean: inventory=0.04, anchor=0.04
    - ✓ SD: inventory=0.19, anchor=0.19
    - ✓ median: inventory=0.03, anchor=0.03
    - ✓ N: inventory=76323, anchor=76323
- **VERDICT**: **PASS**

## VAR_07 — PROFITS
- **role**: DV
- **claimed**: §Table 8 notes, page 3208
- **definition (first 200ch)**: PROFITS is defined as the quarterly percentage change in profits (operating income before depreciation divided by sales).…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p31 (printed p3208)
- **CHECK 2 — page match**: `MATCH` — claimed=3208, found=p3208
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **PASS**

## VAR_08 — ESTABLISHMENT_LEVEL_EMPLOYMENT_GROWTH (column header: 'ESTABLISHMENT_LEVEL_EMPLOYMENT_GROWTH')
- **role**: DV
- **claimed**: §§V.B.1.b text + Table 5 header/notes, page 3202
- **definition (first 200ch)**: We first repeat the analysis of Table 2 using establishment-level employment growth calculated based on YTS data on the number of employees across all establishments operated by sample firms in the Un…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p25 (printed p3202)
- **CHECK 2 — page match**: `MATCH` — claimed=3202, found=p3202
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **PASS**

## VAR_09 — ESTABLISHMENT_TURNOVER
- **role**: DV
- **claimed**: §Footnote 24, page 3203
- **definition (first 200ch)**: Establishment turnover is defined as the sum of establishment openings and closings, divided by the lagged number of total establishments.…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p26 (printed p3203)
- **CHECK 2 — page match**: `MATCH` — claimed=3203, found=p3203
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **PASS**

## VAR_10 — INVESTMENT (U.S.-based subsidiaries)
- **role**: DV
- **claimed**: §§V.B.1.a text + Table 4 notes, page 3201
- **definition (first 200ch)**: For each parent firm, in each year, we compute their U.S.-based investment by summing fixed capital spending across their U.S. subsidiaries.…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p24 (printed p3201)
- **CHECK 2 — page match**: `MATCH` — claimed=3201, found=p3201
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **PASS**

## Batch summary
- PASS: 5
- FAIL: 0
- INCONCLUSIVE: 0
- OTHER: 0