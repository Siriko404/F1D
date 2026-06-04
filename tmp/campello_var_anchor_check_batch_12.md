# Variable Anchor Check — Batch 12 (VAR_56 – VAR_60)

Generated: 2026-05-26 by `tmp/batched_var_verifier.py 12`
Anchor sources: PyMuPDF full main paper (45pp) + supplement (19pp); Table 1 stats anchor (300 cells).

Checks per variable: (1) definition_verbatim found in paper? (2) claimed page matches? (3) Table 1 stats (when applicable) match anchor?

## VAR_56 — discount rate news component of returns (equity discount rate news)
- **role**: Control
- **claimed**: §§VI.B text + Table 10 notes, page 3211
- **definition (first 200ch)**: for the discount rate news component of returns (from the decomposition of returns news into cash flow news and discount rate news components as in Vuolteenaho (2002)).…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p34 (printed p3211)
- **CHECK 2 — page match**: `MATCH` — claimed=3211, found=p3211
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **PASS**

## VAR_57 — first-moment instruments for USD–GBP exchange rate, price of oil, and Treasury rate (Alfaro et al. (2018))
- **role**: Control
- **claimed**: §Footnote 23 (main); IA Table C.7 notes, page 3200
- **definition (first 200ch)**: we include the firm-level first-moment instruments for the USD–GBP exchange rate, the price of oil, and the Treasury rate from alfaro2018. These variables jointly serve as proxies for changes in firms…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p23 (printed p3200)
- **CHECK 2 — page match**: `MATCH` — claimed=3200, found=p3200
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper (as distribution)
- **VERDICT**: **PASS**

## VAR_58 — AUTOMATION{i∈CZ} (AUTOMATION_{i∈CZ})
- **role**: Robustness
- **claimed**: §§VI.C text + Table 11 notes, page 3211
- **definition (first 200ch)**: We define our first, geography-based variable capturing firms' exposure to automation technologies, AUTOMATION{i∈CZ}, by matching each firm i in our sample to a CZ (based on the firm's headquarters lo…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p34 (printed p3211)
- **CHECK 2 — page match**: `MATCH` — claimed=3211, found=p3211
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **PASS**

## VAR_59 — AUTOMATIONi (AUTOMATION_i, text-based)
- **role**: Robustness
- **claimed**: §§VI.C text (full construction in IA Appendix E.1 ¶2), page 3211
- **definition (first 200ch)**: We define AUTOMATIONi as a continuous variable that measures how frequently the top 100 automation keywords appear in each firm's business description (10-K Section 1) and management discussion (10-K …
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p34 (printed p3211)
- **CHECK 2 — page match**: `MATCH` — claimed=3211, found=p3211
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper (numeric)
- **VERDICT**: **PASS**

## VAR_60 — AUTOMATION_KEYWORDSi
- **role**: Other: intermediate input to AUTOMATIONi
- **claimed**: §IA Appendix E.1 ¶2, page IA p. 16
- **definition (first 200ch)**: AUTOMATIONi = log(1 + AUTOMATION_KEYWORDSi), where AUTOMATION_KEYWORDSi is the number of mentions of the top 100 automation-related keywords in firm i's 10-K forms.…
- **CHECK 1 — definition in paper**: `FOUND` — supp pdf p16 (printed p16)
- **CHECK 2 — page match**: `MATCH` — claimed=IA p. 16, found=p16
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **PASS**

## Batch summary
- PASS: 5
- FAIL: 0
- INCONCLUSIVE: 0
- OTHER: 0