# Variable Anchor Check — Batch 13 (VAR_61 – VAR_65)

Generated: 2026-05-26 by `tmp/batched_var_verifier.py 13`
Anchor sources: PyMuPDF full main paper (45pp) + supplement (19pp); Table 1 stats anchor (300 cells).

Checks per variable: (1) definition_verbatim found in paper? (2) claimed page matches? (3) Table 1 stats (when applicable) match anchor?

## VAR_61 — capital expenditures
- **role**: Other: raw input to derived DVs/controls
- **claimed**: §Table 1 notes (within INVESTMENT definition), page 3198
- **definition (first 200ch)**: INVESTMENT is defined as capital expenditures divided by lagged total assets.…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p21 (printed p3198)
- **CHECK 2 — page match**: `MATCH` — claimed=3198, found=p3198
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper (only the scaled ratio INVESTMENT is reported)
- **VERDICT**: **PASS**

## VAR_62 — lagged total assets / total assets
- **role**: Other: raw input (scaling denominator) / Sample-filter
- **claimed**: §§IV.B + Table 1 notes, page 3192
- **definition (first 200ch)**: We use COMPUSTAT Quarterly to gather basic information on firm investment and financial data. … we drop … companies whose market value or book assets are lower than $10 million.…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p15 (printed p3192)
- **CHECK 2 — page match**: `MATCH` — claimed=3192, found=p3192
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper (only logged form SIZE reported)
- **VERDICT**: **PASS**

## VAR_63 — number of employees
- **role**: Other: raw input to EMPLOYMENT_GROWTH
- **claimed**: §§IV.B, page 3192
- **definition (first 200ch)**: Firm-level employment data are taken from COMPUSTAT's Annual Fundamentals. We measure employment growth based on the change in the number of employees of the firm.…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p15 (printed p3192)
- **CHECK 2 — page match**: `MATCH` — claimed=3192, found=p3192
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper (only EMPLOYMENT_GROWTH reported)
- **VERDICT**: **PASS**

## VAR_64 — R&D expenditures
- **role**: Other: raw input to R&D ratio
- **claimed**: §Table 1 notes (within R&D definition), page 3198
- **definition (first 200ch)**: R&D is defined as R&D expenditures divided by lagged total assets, considering only firms with non-missing R&D expenditures.…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p21 (printed p3198)
- **CHECK 2 — page match**: `MATCH` — claimed=3198, found=p3198
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper (only scaled R&D reported)
- **VERDICT**: **PASS**

## VAR_65 — sale of plant, property, and equipment (SPP&E)
- **role**: Other: raw input to DIVESTITURES
- **claimed**: §Table 3 notes, page 3202
- **definition (first 200ch)**: DIVESTITURES are defined as the value of SPP&E (Sale of Plant, Property, and Equipment) divided by lagged total assets.…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p25 (printed p3202)
- **CHECK 2 — page match**: `MATCH` — claimed=3202, found=p3202
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper (only scaled DIVESTITURES)
- **VERDICT**: **PASS**

## Batch summary
- PASS: 5
- FAIL: 0
- INCONCLUSIVE: 0
- OTHER: 0