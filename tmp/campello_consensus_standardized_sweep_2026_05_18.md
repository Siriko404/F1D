# CONSENSUS_EARNINGS_FORECAST — 'standardized' candidate sweep

systematic-debugging Phase 3. ONE variable = the standardization operator; data/scopes/1%-winsor/window fixed. IBES Detail EPS/FPI=6 2009-2016, consensus = mean across analysts per (gvkey,fpedats). Campello programmatic from table1_pdfpage21. NO spec change, NO verdict (Sina-gated).

## UNIVERSE (A)
Campello target: mean +0.070 | SD 3.510 | med +0.090 | IQR 2.050 | N 42,031

| candidate | mean | SD | med | IQR | N | SD/IQR |
|--|--|--|--|--|--|--|
| raw | +0.276 | 0.973 | +0.253 | 0.540 | 44,592 | 1.80 |
| zfirm | +0.070 | 0.858 | +0.058 | 1.245 | 44,580 | 0.69 |
| zxsec | +0.005 | 0.018 | +0.017 | 0.036 | 44,592 | 0.51 |
| f_over_disp | +15.590 | 21.702 | +9.411 | 21.659 | 40,009 | 1.00 |
| sue_abs | -0.009 | 0.772 | +0.036 | 0.248 | 43,286 | 3.12 |
| sue_disp | +0.863 | 3.330 | +0.579 | 2.748 | 39,663 | 1.21 |
| rev_disp | +0.345 | 8.228 | +0.376 | 4.445 | 39,610 | 1.85 |

## TREATED (B)
Campello target: mean +0.010 | SD 3.400 | med +0.010 | IQR 1.830 | N 8,963

| candidate | mean | SD | med | IQR | N | SD/IQR |
|--|--|--|--|--|--|--|
| raw | +0.245 | 1.470 | +0.159 | 0.468 | 8,284 | 3.14 |
| zfirm | +0.081 | 0.886 | +0.092 | 1.285 | 8,278 | 0.69 |
| zxsec | +0.005 | 0.018 | +0.017 | 0.036 | 8,284 | 0.51 |
| f_over_disp | +8.478 | 16.284 | +4.549 | 13.064 | 7,380 | 1.25 |
| sue_abs | -0.040 | 1.199 | +0.027 | 0.409 | 7,982 | 2.93 |
| sue_disp | +0.403 | 4.051 | +0.277 | 2.645 | 7,281 | 1.53 |
| rev_disp | +0.247 | 6.983 | +0.252 | 3.523 | 7,285 | 1.98 |

## CONTROL (C)
Campello target: mean +0.070 | SD 2.330 | med +0.040 | IQR 2.400 | N 10,720

| candidate | mean | SD | med | IQR | N | SD/IQR |
|--|--|--|--|--|--|--|
| raw | +0.477 | 0.617 | +0.388 | 0.596 | 9,423 | 1.03 |
| zfirm | +0.090 | 0.836 | +0.075 | 1.239 | 9,423 | 0.67 |
| zxsec | +0.004 | 0.018 | +0.017 | 0.036 | 9,423 | 0.52 |
| f_over_disp | +21.789 | 24.095 | +15.132 | 26.633 | 8,653 | 0.90 |
| sue_abs | +0.006 | 0.592 | +0.032 | 0.164 | 9,171 | 3.61 |
| sue_disp | +0.932 | 3.251 | +0.674 | 2.588 | 8,585 | 1.26 |
| rev_disp | +0.294 | 9.491 | +0.491 | 4.974 | 8,619 | 1.91 |

## Read (NO verdict — Sina-gated)
Match = same SHAPE as Campello (center≈0, SD 2.3-3.5, IQR~2, SD/IQR≈1.5-1.7), not exact N (universe differs: ours = step1 ∩ βᵁᴷ-estimable, not full COMPUSTAT). A candidate that reproduces center+SD+IQR+SD/IQR on ALL THREE panels is the operationalization. If none: round 2 adds price-deflated (Compustat prccq join). Spec change Sina-gated; this is fingerprint evidence only.
