# Campello Table 1 vs rebuild — full summary-stats compare

step1=`2026-05-17_193245`  step3=`2026-05-17_193353`  window 2010Q1–2015Q4  1% winsor within qtr (Campello convention).

Campello publishes **only mean/SD/median/IQR/N** (no min/max/pctiles). `ours` = winsorized (apples-to-apples). `RAWmin/RAWmax/RAWn` = pre-winsor garbage sniff, **no Campello benchmark**. FLAG = crude same-ballpark HINT (mean&med within 25% & same sign), NOT a verdict. Universe differs (ours = step1 ∩ βᵁᴷ-estimable, larger-firm skew) — gaps may be composition, not garbage; perfect match is NOT the bar (symptom-chasing forbidden).

## UNIVERSE  (~Campello Panel A)

| variable | RAWn | RAWmin | RAWmax | ours:mean | SD | med | IQR | p1 | p99 | C:mean | C:SD | C:med | C:IQR | C:N | FLAG |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CASH_T1 (cheq/atq_l1) | 59,918 | +0.000 | +953.000 | +0.212 | +0.236 | +0.126 | +0.253 | +0.001 | +1.010 | +0.220 | +0.250 | +0.120 | +0.270 | 78,044 | MATCH |
| CASH_T8 (cheq/(atq-cheq)_l1) | 59,917 | +0.000 | +1409.250 | +0.609 | +1.649 | +0.144 | +0.376 | +0.001 | +10.751 | +0.220 | +0.250 | +0.120 | +0.270 | 78,044 | CHECK |
| SIZE | 56,447 | +2.306 | +13.564 | +6.622 | +1.909 | +6.577 | +2.660 | +2.819 | +11.170 | +6.190 | +2.080 | +6.150 | +3.080 | 78,062 | MATCH |
| STOCK_RETURNS | 58,546 | -0.691 | +1.078 | +0.031 | +0.221 | +0.023 | +0.240 | -0.487 | +0.719 | +0.030 | +0.240 | +0.020 | +0.250 | 67,226 | MATCH |
| TOBIN_Q | 59,581 | +0.266 | +268.840 | +2.153 | +1.569 | +1.627 | +1.209 | +0.725 | +9.132 | +2.110 | +1.590 | +1.570 | +1.260 | 73,353 | MATCH |
| CASH_FLOW | 59,164 | -3.985 | +0.161 | +0.020 | +0.055 | +0.029 | +0.033 | -0.220 | +0.126 | +0.010 | +0.060 | +0.030 | +0.040 | 75,287 | MATCH |
| SALES_GROWTH | 60,278 | -1.000 | +9.963 | +0.153 | +0.523 | +0.065 | +0.231 | -0.698 | +2.968 | +0.160 | +0.620 | +0.060 | +0.230 | 71,637 | MATCH |
| CONSENSUS_EPS | 44,444 | -10.630 | +0.611 | +0.069 | +0.137 | +0.067 | +0.072 | -0.608 | +0.412 | +0.070 | +3.510 | +0.090 | +2.050 | 42,031 | CHECK |

## TREATED  (~Campello Panel B)

| variable | RAWn | RAWmin | RAWmax | ours:mean | SD | med | IQR | p1 | p99 | C:mean | C:SD | C:med | C:IQR | C:N | FLAG |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CASH_T1 (cheq/atq_l1) | 12,393 | +0.000 | +25.467 | +0.195 | +0.237 | +0.102 | +0.240 | +0.000 | +0.957 | +0.200 | +0.240 | +0.110 | +0.260 | 11,176 | MATCH |
| CASH_T8 (cheq/(atq-cheq)_l1) | 12,393 | +0.000 | +162.862 | +0.598 | +1.758 | +0.113 | +0.336 | +0.000 | +10.726 | +0.200 | +0.240 | +0.110 | +0.260 | 11,176 | CHECK |
| SIZE | 11,614 | +2.306 | +11.178 | +6.319 | +1.769 | +6.328 | +2.568 | +2.774 | +10.284 | +6.110 | +1.870 | +6.120 | +2.860 | 11,176 | MATCH |
| STOCK_RETURNS | 12,236 | -0.691 | +1.078 | +0.015 | +0.260 | +0.003 | +0.301 | -0.576 | +0.782 | +0.020 | +0.270 | +0.000 | +0.300 | 11,088 | MATCH |
| TOBIN_Q | 12,320 | +0.280 | +34.175 | +2.034 | +1.627 | +1.467 | +1.085 | +0.691 | +9.060 | +1.920 | +1.510 | +1.410 | +1.010 | 11,090 | MATCH |
| CASH_FLOW | 12,256 | -1.071 | +0.161 | +0.015 | +0.059 | +0.024 | +0.038 | -0.227 | +0.136 | +0.010 | +0.060 | +0.020 | +0.040 | 10,972 | MATCH |
| SALES_GROWTH | 12,473 | -1.000 | +9.414 | +0.207 | +0.833 | +0.064 | +0.318 | -0.784 | +4.611 | +0.180 | +0.710 | +0.060 | +0.310 | 10,624 | MATCH |
| CONSENSUS_EPS | 8,263 | -10.630 | +0.611 | +0.057 | +0.178 | +0.055 | +0.063 | -0.561 | +0.484 | +0.010 | +3.400 | +0.010 | +1.830 | 8,963 | CHECK |

## CONTROL  (~Campello Panel C)

| variable | RAWn | RAWmin | RAWmax | ours:mean | SD | med | IQR | p1 | p99 | C:mean | C:SD | C:med | C:IQR | C:N | FLAG |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CASH_T1 (cheq/atq_l1) | 11,198 | +0.000 | +26.485 | +0.181 | +0.188 | +0.119 | +0.208 | +0.001 | +0.844 | +0.170 | +0.180 | +0.110 | +0.190 | 12,097 | MATCH |
| CASH_T8 (cheq/(atq-cheq)_l1) | 11,198 | +0.000 | +508.720 | +0.384 | +0.922 | +0.136 | +0.289 | +0.001 | +5.772 | +0.170 | +0.180 | +0.110 | +0.190 | 12,097 | CHECK |
| SIZE | 10,831 | +2.420 | +13.564 | +7.221 | +1.986 | +7.181 | +2.753 | +3.086 | +11.939 | +7.250 | +1.990 | +7.250 | +2.650 | 12,097 | MATCH |
| STOCK_RETURNS | 11,167 | -0.691 | +1.078 | +0.037 | +0.183 | +0.032 | +0.203 | -0.399 | +0.566 | +0.040 | +0.180 | +0.030 | +0.200 | 12,063 | MATCH |
| TOBIN_Q | 11,166 | +0.342 | +46.368 | +2.131 | +1.371 | +1.711 | +1.149 | +0.823 | +8.008 | +1.980 | +1.250 | +1.620 | +1.070 | 12,055 | MATCH |
| CASH_FLOW | 11,021 | -3.833 | +0.161 | +0.030 | +0.036 | +0.033 | +0.027 | -0.120 | +0.107 | +0.030 | +0.040 | +0.030 | +0.030 | 11,871 | MATCH |
| SALES_GROWTH | 11,200 | -1.000 | +9.963 | +0.100 | +0.292 | +0.061 | +0.173 | -0.552 | +1.183 | +0.100 | +0.360 | +0.060 | +0.160 | 11,969 | MATCH |
| CONSENSUS_EPS | 9,366 | -10.630 | +0.611 | +0.096 | +0.085 | +0.085 | +0.082 | -0.190 | +0.373 | +0.070 | +2.330 | +0.040 | +2.400 | 10,720 | CHECK |

## How to read FLAG=CHECK
CHECK = winsorized mean/median NOT in Campello's ballpark for that panel. Could be (a) real construction deviation, (b) sample-composition (βᵁᴷ-estimable ≠ full COMPUSTAT), or (c) a Sina-ratified documented non-replication: CONSENSUS_EPS = IBES-summary statsum MEANEST z-score (forecast-only; §G.8; z ⇒ SD≈1 vs Campello reported 3.51) / CASH_T8 = superseded net-of-cash reading (canonical DV = CASH_T1, §F.2). All on record in campello_variable_audit_2026_05_17.md. No verdict (gated on Sina).
