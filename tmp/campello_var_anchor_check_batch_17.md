# Variable Anchor Check — Batch 17 (VAR_81 – VAR_85)

Generated: 2026-05-26 by `tmp/batched_var_verifier.py 17`
Anchor sources: PyMuPDF full main paper (45pp) + supplement (19pp); Table 1 stats anchor (300 cells).

Checks per variable: (1) definition_verbatim found in paper? (2) claimed page matches? (3) Table 1 stats (when applicable) match anchor?

## VAR_81 — Hoberg and Moon (2017) Input and Output offshoring indices (raw counts)
- **role**: Other: raw input to U.K. offshoring treatment dummies
- **claimed**: §§V.B.2 text, page 3205
- **definition (first 200ch)**: This index, derived from firms' 10-K filings, counts mentions of words related to the purchase of inputs (\"Input\") and sale of outputs (\"Output\") from each country a firm does business with within…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p28 (printed p3205)
- **CHECK 2 — page match**: `MATCH` — claimed=3205, found=p3205
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **PASS**

## VAR_82 — FIRM_i (firm-fixed effects)
- **role**: Fixed effect
- **claimed**: §§IV.C.3 (equation (14) discussion), page 3197
- **definition (first 200ch)**: FIRM_i represents firm-fixed effects, INDUSTRY_j is a dummy for each industry category j of the Hoberg and Phillips (2016) classification (FIC 100), and QUARTER_t are calendar-quarter dummies.…
- **CHECK 1 — definition in paper**: `NOT_FOUND` — definition probe not located in main+supp corpus
- **CHECK 2 — page match**: `N/A` — no found page to compare
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **FAIL (definition not in paper)**

## VAR_83 — INDUSTRY_j (Hoberg and Phillips (2016) FIC 100)
- **role**: Fixed effect
- **claimed**: §§IV.C.3 (equation (14) discussion), page 3197
- **definition (first 200ch)**: INDUSTRY_j is a dummy for each industry category j of the Hoberg and Phillips (2016) classification (FIC 100)…
- **CHECK 1 — definition in paper**: `NOT_FOUND` — definition probe not located in main+supp corpus
- **CHECK 2 — page match**: `N/A` — no found page to compare
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **FAIL (definition not in paper)**

## VAR_84 — QUARTER_t (calendar-quarter dummies)
- **role**: Fixed effect
- **claimed**: §§IV.C.3 (equation (14) discussion), page 3197
- **definition (first 200ch)**: QUARTER_t are calendar-quarter dummies.…
- **CHECK 1 — definition in paper**: `NOT_FOUND` — definition probe not located in main+supp corpus
- **CHECK 2 — page match**: `N/A` — no found page to compare
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **FAIL (definition not in paper)**

## VAR_85 — INDUSTRY_j × QUARTER_t (Industry × time fixed effects)
- **role**: Fixed effect
- **claimed**: §equation (14), page 3196
- **definition (first 200ch)**: Y_{i,t} = α + δ[POST_t × HIGH_UK_EXPOSURE_i] + θCONTROLS_{i,t−1} + Σ_i FIRM_i + Σ_j Σ_t [INDUSTRY_j × QUARTER_t] + ϵ_{i,t}.…
- **CHECK 1 — definition in paper**: `NOT_FOUND` — definition probe not located in main+supp corpus
- **CHECK 2 — page match**: `N/A` — no found page to compare
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **FAIL (definition not in paper)**

## Batch summary
- PASS: 1
- FAIL: 4
- INCONCLUSIVE: 0
- OTHER: 0