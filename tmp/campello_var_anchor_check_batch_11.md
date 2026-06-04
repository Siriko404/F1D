# Variable Anchor Check — Batch 11 (VAR_51 – VAR_55)

Generated: 2026-05-26 by `tmp/batched_var_verifier.py 11`
Anchor sources: PyMuPDF full main paper (45pp) + supplement (19pp); Table 1 stats anchor (300 cells).

Checks per variable: (1) definition_verbatim found in paper? (2) claimed page matches? (3) Table 1 stats (when applicable) match anchor?

## VAR_51 — FX hedging dummy (prior-year)
- **role**: Control
- **claimed**: §§VI.A text + Table 9 notes, page 3209
- **definition (first 200ch)**: We include as additional controls a dummy variable for whether a firm engaged in FX hedging activity in the prior year, and the intensity of hedging in the prior year as measured by the number of keyw…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p32 (printed p3209)
- **CHECK 2 — page match**: `MATCH` — claimed=3209, found=p3209
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **PASS**

## VAR_52 — FX hedging intensity (number of keywords)
- **role**: Control
- **claimed**: §§VI.A text + Table 9 notes, page 3209
- **definition (first 200ch)**: the intensity of hedging in the prior year as measured by the number of keywords mentioned.…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p32 (printed p3209)
- **CHECK 2 — page match**: `MATCH` — claimed=3209, found=p3209
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **PASS**

## VAR_53 — existing bond yields (yields to maturity on existing bonds)
- **role**: Control
- **claimed**: §§VI.B text + Table 10 notes, page 3211
- **definition (first 200ch)**: we reestimate the analysis of Table 2 controlling for yields on existing bonds (obtained from TRACE)…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p34 (printed p3211)
- **CHECK 2 — page match**: `MATCH` — claimed=3211, found=p3211
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **PASS**

## VAR_54 — new bond yields (yields on new bond issues)
- **role**: Control
- **claimed**: §§VI.B text + Table 10 notes, page 3211
- **definition (first 200ch)**: yields on new bond issues (from SDC)…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p34 (printed p3211)
- **CHECK 2 — page match**: `MATCH` — claimed=3211, found=p3211
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **PASS**

## VAR_55 — new syndicated loan spreads / markups (all-in spread)
- **role**: Control
- **claimed**: §§VI.B text + Table 10 notes, page 3211
- **definition (first 200ch)**: markups on new syndicated loans (from DealScan)…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p34 (printed p3211)
- **CHECK 2 — page match**: `MATCH` — claimed=3211, found=p3211
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **PASS**

## Batch summary
- PASS: 5
- FAIL: 0
- INCONCLUSIVE: 0
- OTHER: 0