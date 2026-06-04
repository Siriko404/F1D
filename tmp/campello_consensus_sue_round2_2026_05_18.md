# CONSENSUS SUE round 2 — clean 1Q-ahead snapshot

Root cause (Phase-1 data inspect): round-1 +0.6 offset = averaging stale+post-period analyst rows. Here consensus+σ use each analyst's LATEST pre-period estimate. ACTUAL period-aligned (verified 1/(gvkey,fpedats)). NO spec change, NO verdict (Sina-gated).

## UNIVERSE (A)
Campello: mean +0.070 SD 3.510 med +0.090 IQR 2.050 N 42,031

| variant | mean | SD | med | IQR | N | SD/IQR |
|--|--|--|--|--|--|--|
| sue_pre | +0.898 | 3.792 | +0.645 | 3.015 | 38,086 | 1.26 |
| sue_120 | +0.897 | 3.795 | +0.645 | 3.015 | 38,088 | 1.26 |
| fcst_z120 | +0.003 | 0.019 | +0.016 | 0.036 | 43,754 | 0.52 |
| sue_ts | +0.246 | 1.010 | +0.206 | 1.067 | 42,941 | 0.95 |
| sue_absF | +0.018 | 1.190 | +0.038 | 0.271 | 42,780 | 4.39 |
| sue_ts_f | -0.246 | 1.010 | -0.206 | 1.067 | 42,941 | 0.95 |

## TREATED (B)
Campello: mean +0.010 SD 3.400 med +0.010 IQR 1.830 N 8,963

| variant | mean | SD | med | IQR | N | SD/IQR |
|--|--|--|--|--|--|--|
| sue_pre | +0.431 | 4.251 | +0.339 | 2.969 | 6,956 | 1.43 |
| sue_120 | +0.433 | 4.252 | +0.340 | 2.970 | 6,955 | 1.43 |
| fcst_z120 | +0.003 | 0.019 | +0.016 | 0.036 | 8,083 | 0.52 |
| sue_ts | +0.102 | 1.022 | +0.092 | 1.060 | 7,892 | 0.96 |
| sue_absF | -0.067 | 2.090 | +0.030 | 0.450 | 7,851 | 4.65 |
| sue_ts_f | -0.102 | 1.022 | -0.092 | 1.060 | 7,892 | 0.96 |

## CONTROL (C)
Campello: mean +0.070 SD 2.330 med +0.040 IQR 2.400 N 10,720

| variant | mean | SD | med | IQR | N | SD/IQR |
|--|--|--|--|--|--|--|
| sue_pre | +0.968 | 3.740 | +0.713 | 2.788 | 8,328 | 1.34 |
| sue_120 | +0.960 | 3.765 | +0.713 | 2.792 | 8,327 | 1.35 |
| fcst_z120 | +0.002 | 0.019 | +0.016 | 0.036 | 9,299 | 0.52 |
| sue_ts | +0.328 | 0.998 | +0.271 | 1.068 | 9,126 | 0.93 |
| sue_absF | +0.014 | 0.976 | +0.034 | 0.183 | 9,107 | 5.33 |
| sue_ts_f | -0.328 | 0.998 | -0.271 | 1.068 | 9,126 | 0.93 |

## Read (NO verdict — Sina-gated)
Match = Campello SHAPE on ALL 3 panels: center≈0, SD 2.3-3.5, IQR~2. N differs (universe: ours step1∩βᵁᴷ-estimable). fcst_z120 included to fairly test Sina's literal 'standardized=z-score of the forecast' on a clean snapshot. Spec change Sina-gated; fingerprint evidence only.
