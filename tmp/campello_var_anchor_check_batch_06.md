# Variable Anchor Check — Batch 6 (VAR_26 – VAR_30)

Generated: 2026-05-26 by `tmp/batched_var_verifier.py 6`
Anchor sources: PyMuPDF full main paper (45pp) + supplement (19pp); Table 1 stats anchor (300 cells).

Checks per variable: (1) definition_verbatim found in paper? (2) claimed page matches? (3) Table 1 stats (when applicable) match anchor?

## VAR_26 — U.K. Offshoring Index (Input Only)
- **role**: Treatment
- **claimed**: §§V.B.2 text + Table 6 notes, page 3206
- **definition (first 200ch)**: In the fourth column, the treatment group consists of firms with scores of greater than 5 on the Hoberg–Moon U.K. Offshoring Index summed up over years 2010–2014, considering only input offshoring act…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p29 (printed p3206)
- **CHECK 2 — page match**: `MATCH` — claimed=3206, found=p3206
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **PASS**

## VAR_27 — U.K. Offshoring Index (Output Only)
- **role**: Treatment
- **claimed**: §Table 6 notes, page 3206
- **definition (first 200ch)**: In the final specification, the treatment group consists of firms with scores of greater than 5 on the Hoberg and Moon (2017) U.K. Offshoring Index summed up over years 2010–2014, considering only out…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p29 (printed p3206)
- **CHECK 2 — page match**: `MATCH` — claimed=3206, found=p3206
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **PASS**

## VAR_28 — asset redeployability index (Kim and Kung (2016)) / HIGH_INPUT_IRREVERSIBILITY (capital)
- **role**: Moderator
- **claimed**: §§IV.A.3 text, page 3192
- **definition (first 200ch)**: To empirically measure capital irreversibility, we use an index of capital redeployability proposed by Kim and Kung (2016). That index classifies fixed capital liquidity in terms of salability of asse…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p15 (printed p3192)
- **CHECK 2 — page match**: `MATCH` — claimed=3192, found=p3192
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **PASS**

## VAR_29 — labor unionization rate (BEA) / High labor irreversibility
- **role**: Moderator
- **claimed**: §§IV.A.3 text, page 3192
- **definition (first 200ch)**: we measure the percentage of total employees who are unionized at the 4-digit SIC level using data from the Bureau of Economic Analysis.…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p15 (printed p3192)
- **CHECK 2 — page match**: `MATCH` — claimed=3192, found=p3192
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **PASS**

## VAR_30 — labor skills index (LSI) (Ghaly, Dang, and Stathopoulos (2017))
- **role**: Moderator
- **claimed**: §§V.B.1.b text, page 3203
- **definition (first 200ch)**: As a proxy for labor skills, we use the industry-level labor skills index (LSI) proposed by Ghaly, Dang, and Stathopoulos (2017). The LSI is based on data from the Occupational Employment Statistics c…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p26 (printed p3203)
- **CHECK 2 — page match**: `MATCH` — claimed=3203, found=p3203
- **CHECK 3 — Table 1 stats**: `NOT_TABLE_1` — found_in=NOT REPORTED in the paper
- **VERDICT**: **PASS**

## Batch summary
- PASS: 5
- FAIL: 0
- INCONCLUSIVE: 0
- OTHER: 0