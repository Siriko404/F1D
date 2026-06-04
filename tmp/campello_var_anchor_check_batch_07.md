# Variable Anchor Check — Batch 7 (VAR_31 – VAR_35)

Generated: 2026-05-26 by `tmp/batched_var_verifier.py 7`
Anchor sources: PyMuPDF full main paper (45pp) + supplement (19pp); Table 1 stats anchor (300 cells).

Checks per variable: (1) definition_verbatim found in paper? (2) claimed page matches? (3) Table 1 stats (when applicable) match anchor?

## VAR_31 — POST_t × βUK_i  (POST·β_i^UK, linear continuous treatment)
- **role**: Treatment
- **claimed**: §§V.A text + Table 2 col 1 header, page 3199
- **definition (first 200ch)**: We begin with a firm-fixed effects estimation in which β_i^UK enters the specification as a linear continuous-treatment variable in column 1, allowing for the entire range of β_i^UK values. The POST·β…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p22 (printed p3199)
- **CHECK 2 — page match**: `MATCH` — claimed=3199, found=p3199
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper (regression coefficient only)
- **VERDICT**: **PASS**

## VAR_32 — POST × HIGH_βUK_i  (POST·HIGH_β_i^UK)
- **role**: Treatment
- **claimed**: §equation (14), §IV.C.3, page 3196
- **definition (first 200ch)**: Y_{i,t} = α + δ[POST_t × HIGH_UK_EXPOSURE_i] + θCONTROLS_{i,t−1} + Σ_i FIRM_i + Σ_j Σ_t [INDUSTRY_j × QUARTER_t] + ϵ_{i,t}.…
- **CHECK 1 — definition in paper**: `NOT_FOUND` — definition probe not located in main+supp corpus
- **CHECK 2 — page match**: `N/A` — no found page to compare
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper (regression coefficient only)
- **VERDICT**: **FAIL (definition not in paper)**

## VAR_33 — POST × HIGH_10K_ENTRIES
- **role**: Treatment
- **claimed**: §equation (14), §IV.C.3, page 3196
- **definition (first 200ch)**: Y_{i,t} = α + δ[POST_t × HIGH_UK_EXPOSURE_i] + θCONTROLS_{i,t−1} + Σ_i FIRM_i + Σ_j Σ_t [INDUSTRY_j × QUARTER_t] + ϵ_{i,t}.…
- **CHECK 1 — definition in paper**: `NOT_FOUND` — definition probe not located in main+supp corpus
- **CHECK 2 — page match**: `N/A` — no found page to compare
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper (regression coefficient only)
- **VERDICT**: **FAIL (definition not in paper)**

## VAR_34 — POST × HIGH_UK_OFFSHORING_INDEX
- **role**: Treatment
- **claimed**: §Table 6 (column headers + notes), page 3206
- **definition (first 200ch)**: In the third column, the treatment group consists of firms with scores of greater than five on the Hoberg–Moon U.K. Offshoring Index summed up over years 2010–2014, considering both input and output o…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p29 (printed p3206)
- **CHECK 2 — page match**: `MATCH` — claimed=3206, found=p3206
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper (regression coefficient only)
- **VERDICT**: **PASS**

## VAR_35 — POST × HIGH_βUK_i × HIGH_INPUT_IRREVERSIBILITY (DIDID triple interaction)
- **role**: Moderator
- **claimed**: §§V.B.3 text + Table 7 (col 3 / col 6 rows), page 3207
- **definition (first 200ch)**: The estimation under column 3 uses the entire sample of firms, introducing a dummy variable High Irreversibility that equals 1 if the firm is in the high irreversibility group. The coefficient on this…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p30 (printed p3207)
- **CHECK 2 — page match**: `MATCH` — claimed=3207, found=p3207
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper (regression coefficient only)
- **VERDICT**: **PASS**

## Batch summary
- PASS: 3
- FAIL: 2
- INCONCLUSIVE: 0
- OTHER: 0