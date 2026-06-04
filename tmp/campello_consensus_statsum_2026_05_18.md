# CONSENSUS via IBES Summary Statistics (statsum)

Root-cause path (§G.3): IBES native MEANEST/STDEV/ACTUAL at its own STATPERS. EPS/QTR/FPI=6/USD/US, horizon≥0. SUE = (ACTUAL−consensus)/STDEV. 1% winsor within cal_yr_qtr, 2010Q1-2015Q4. Campello programmatic. NO spec change, NO verdict (Sina-gated).

## UNIVERSE (A)
Campello: mean +0.070 SD 3.510 med +0.090 IQR 2.050 N 42,031

| snapshot | cand | mean | SD | med | IQR | N | SD/IQR |
|--|--|--|--|--|--|--|--|
| snap_last | sue_mean | +0.683 | 3.559 | +0.500 | 2.931 | 37,845 | 1.21 |
| snap_last | sue_med | +0.693 | 3.567 | +0.500 | 2.900 | 37,844 | 1.23 |
| snap_last | sue_mean_f | -0.683 | 3.559 | -0.500 | 2.931 | 37,845 | 1.21 |
| snap_q | sue_mean | +0.586 | 3.584 | +0.500 | 3.000 | 37,946 | 1.19 |
| snap_q | sue_med | +0.599 | 3.596 | +0.500 | 3.000 | 37,945 | 1.20 |
| snap_q | sue_mean_f | -0.586 | 3.584 | -0.500 | 3.000 | 37,946 | 1.19 |

## TREATED (B)
Campello: mean +0.010 SD 3.400 med +0.010 IQR 1.830 N 8,963

| snapshot | cand | mean | SD | med | IQR | N | SD/IQR |
|--|--|--|--|--|--|--|--|
| snap_last | sue_mean | +0.245 | 3.884 | +0.167 | 3.125 | 6,982 | 1.24 |
| snap_last | sue_med | +0.250 | 3.888 | +0.200 | 3.125 | 6,982 | 1.24 |
| snap_last | sue_mean_f | -0.245 | 3.884 | -0.167 | 3.125 | 6,982 | 1.24 |
| snap_q | sue_mean | +0.157 | 3.807 | +0.000 | 3.000 | 7,008 | 1.27 |
| snap_q | sue_med | +0.164 | 3.811 | +0.098 | 3.019 | 7,008 | 1.26 |
| snap_q | sue_mean_f | -0.157 | 3.807 | +0.000 | 3.000 | 7,008 | 1.27 |

## CONTROL (C)
Campello: mean +0.070 SD 2.330 med +0.040 IQR 2.400 N 10,720

| snapshot | cand | mean | SD | med | IQR | N | SD/IQR |
|--|--|--|--|--|--|--|--|
| snap_last | sue_mean | +0.808 | 3.535 | +0.667 | 2.690 | 8,102 | 1.31 |
| snap_last | sue_med | +0.814 | 3.532 | +0.667 | 2.667 | 8,101 | 1.32 |
| snap_last | sue_mean_f | -0.808 | 3.535 | -0.667 | 2.690 | 8,102 | 1.31 |
| snap_q | sue_mean | +0.708 | 3.562 | +0.545 | 2.750 | 8,109 | 1.30 |
| snap_q | sue_med | +0.715 | 3.562 | +0.600 | 2.750 | 8,108 | 1.30 |
| snap_q | sue_mean_f | -0.708 | 3.562 | -0.545 | 2.750 | 8,109 | 1.30 |

## Read (NO verdict — Sina-gated)
Match = Campello SHAPE on ALL 3 panels: center≈0, SD 2.3-3.5, IQR~2. N differs (universe: ours step1∩βᵁᴷ-estimable, not full COMPUSTAT). This is IBES's native consensus+σ — the canonical source Campello almost certainly used. Spec change Sina-gated; fingerprint evidence only.
