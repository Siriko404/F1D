# Variable Anchor Check — Batch 1 (VAR_01 – VAR_05)

Generated: 2026-05-26 by `tmp/batched_var_verifier.py 1`
Anchor sources: PyMuPDF full main paper (45pp) + supplement (19pp); Table 1 stats anchor (300 cells).

Checks per variable: (1) definition_verbatim found in paper? (2) claimed page matches? (3) Table 1 stats (when applicable) match anchor?

## VAR_01 — INVESTMENT
- **role**: DV
- **claimed**: §Table 1 notes, page 3198
- **definition (first 200ch)**: INVESTMENT is defined as capital expenditures divided by lagged total assets.…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p21 (printed p3198)
- **CHECK 2 — page match**: `MATCH` — claimed=3198, found=p3198
- **CHECK 3 — Table 1 stats**: `PANEL_A_MATCH` — 4/4 cells
    - ✓ mean: inventory=0.01, anchor=0.01
    - ✓ SD: inventory=0.02, anchor=0.02
    - ✓ median: inventory=0.01, anchor=0.01
    - ✓ N: inventory=76094, anchor=76094
- **VERDICT**: **PASS**

## VAR_02 — EMPLOYMENT_GROWTH
- **role**: DV
- **claimed**: §Table 1 notes, page 3198
- **definition (first 200ch)**: EMPLOYMENT_GROWTH is defined as the percentage change in the number of employees (annual).…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p21 (printed p3198)
- **CHECK 2 — page match**: `MATCH` — claimed=3198, found=p3198
- **CHECK 3 — Table 1 stats**: `PANEL_A_MATCH` — 4/4 cells
    - ✓ mean: inventory=0.08, anchor=0.08
    - ✓ SD: inventory=0.28, anchor=0.28
    - ✓ median: inventory=0.03, anchor=0.03
    - ✓ N: inventory=17620, anchor=17620
- **VERDICT**: **PASS**

## VAR_03 — R&D
- **role**: DV
- **claimed**: §Table 1 notes, page 3198
- **definition (first 200ch)**: R&D is defined as R&D expenditures divided by lagged total assets, considering only firms with non-missing R&D expenditures.…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p21 (printed p3198)
- **CHECK 2 — page match**: `MATCH` — claimed=3198, found=p3198
- **CHECK 3 — Table 1 stats**: `PANEL_A_MATCH` — 4/4 cells
    - ✓ mean: inventory=0.03, anchor=0.03
    - ✓ SD: inventory=0.04, anchor=0.04
    - ✓ median: inventory=0.02, anchor=0.02
    - ✓ N: inventory=40864, anchor=40864
- **VERDICT**: **PASS**

## VAR_04 — DIVESTITURES
- **role**: DV
- **claimed**: §Table 1 notes, page 3198
- **definition (first 200ch)**: DIVESTITURES is defined as the value of sale of plant, property, and equipment divided by lagged total assets.…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p21 (printed p3198)
- **CHECK 2 — page match**: `MATCH` — claimed=3198, found=p3198
- **CHECK 3 — Table 1 stats**: `PANEL_A_MATCH` — 4/4 cells
    - ✓ mean: inventory=0.06, anchor=0.06
    - ✓ SD: inventory=0.28, anchor=0.28
    - ✓ median: inventory=0.00, anchor=0.00
    - ✓ N: inventory=61151, anchor=61151
- **VERDICT**: **PASS**

## VAR_05 — CASH
- **role**: DV
- **claimed**: §Table 1 notes, page 3198
- **definition (first 200ch)**: CASH is defined as cash and short-term investments divided by lagged total assets.…
- **CHECK 1 — definition in paper**: `FOUND` — main pdf p21 (printed p3198)
- **CHECK 2 — page match**: `MATCH` — claimed=3198, found=p3198
- **CHECK 3 — Table 1 stats**: `PANEL_A_MATCH` — 4/4 cells
    - ✓ mean: inventory=0.22, anchor=0.22
    - ✓ SD: inventory=0.25, anchor=0.25
    - ✓ median: inventory=0.12, anchor=0.12
    - ✓ N: inventory=78044, anchor=78044
- **VERDICT**: **PASS**

## Batch summary
- PASS: 5
- FAIL: 0
- INCONCLUSIVE: 0
- OTHER: 0