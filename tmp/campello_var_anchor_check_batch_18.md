# Variable Anchor Check — Batch 18 (VAR_86 – VAR_88)

Generated: 2026-05-26 by `tmp/batched_var_verifier.py 18`
Anchor sources: PyMuPDF full main paper (45pp) + supplement (19pp); Table 1 stats anchor (300 cells).

Checks per variable: (1) definition_verbatim found in paper? (2) claimed page matches? (3) Table 1 stats (when applicable) match anchor?

## VAR_86 — TIME (time fixed effects)
- **role**: Fixed effect
- **claimed**: §Table 7 Fixed-effects rows + Table 5 notes, page 3207
- **definition (first 200ch)**: NOT DEFINED IN TEXT — appears in Table 5 and Table 7 'Fixed effects' rows as separate 'Industry' and 'Time' entries (used in employment-growth specifications in place of Firm + Industry×time).…
- **CHECK 1 — definition in paper**: `N/A` — no definition text to check
- **CHECK 2 — page match**: `N/A` — no found page to compare
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **INCONCLUSIVE**

## VAR_87 — firm (standard-error cluster group)
- **role**: Standard error cluster group
- **claimed**: §Table 2 notes (recurring in all regression tables), page 3200
- **definition (first 200ch)**: T-statistics are computed using robust standard errors (in parentheses) double-clustered at the firm and calendar quarter levels.…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p23 (printed p3200)
- **CHECK 2 — page match**: `MATCH` — claimed=3200, found=p3200
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=N/A (not a measured variable)
- **VERDICT**: **PASS**

## VAR_88 — calendar quarter (standard-error cluster group)
- **role**: Standard error cluster group
- **claimed**: §Table 2 notes (recurring in all regression tables), page 3200
- **definition (first 200ch)**: T-statistics are computed using robust standard errors (in parentheses) double-clustered at the firm and calendar quarter levels.…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p23 (printed p3200)
- **CHECK 2 — page match**: `MATCH` — claimed=3200, found=p3200
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=N/A (not a measured variable)
- **VERDICT**: **PASS**

## Batch summary
- PASS: 2
- FAIL: 0
- INCONCLUSIVE: 1
- OTHER: 0