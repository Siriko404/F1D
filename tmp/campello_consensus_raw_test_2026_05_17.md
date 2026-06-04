# CONSENSUS_EPS raw-$ test — raw vs z-score vs Campello

Builder loaders reused (FPI=6 EPS, mean-across-analysts, 4-layer CCM); raw = mean_eps ($) NO z-score; z = builder's within-firm z-score (same rows). 1% winsor within qtr, 2010Q1-2015Q4. Campello programmatic from table1_pdfpage21.

| scope | metric | raw-$ | z-score (builder) | Campello |
|--|--|--|--|--|
| UNIVERSE (A) | mean | +0.274 | +0.069 | +0.070 |
| UNIVERSE (A) | sd | +0.974 | +0.859 | +3.510 |
| UNIVERSE (A) | med | +0.251 | +0.058 | +0.090 |
| UNIVERSE (A) | iqr | +0.540 | +1.240 | +2.050 |
| UNIVERSE (A) | n | 44,592 | 44,580 | 42,031 |
| TREATED (B) | mean | +0.238 | +0.079 | +0.010 |
| TREATED (B) | sd | +1.492 | +0.887 | +3.400 |
| TREATED (B) | med | +0.157 | +0.084 | +0.010 |
| TREATED (B) | iqr | +0.466 | +1.279 | +1.830 |
| TREATED (B) | n | 8,284 | 8,278 | 8,963 |
| CONTROL (C) | mean | +0.475 | +0.088 | +0.070 |
| CONTROL (C) | sd | +0.618 | +0.838 | +2.330 |
| CONTROL (C) | med | +0.386 | +0.078 | +0.040 |
| CONTROL (C) | iqr | +0.597 | +1.233 | +2.400 |
| CONTROL (C) | n | 9,423 | 9,423 | 10,720 |

## Read (NO verdict — gated on Sina)
Decisive moment = **SD**. Campello A/B/C SD = 3.51/3.40/2.33 (≫1). A within-firm z-score ⇒ SD≈1 (cannot match). If raw-$ SD ≈ 3.5/3.4/2.3 AND med ≈ 0.09/0.01/0.04 ⇒ Campello's 'standardized' = the raw consensus (mean) EPS in $, NOT a statistical standardization; our z-score is the defect. If raw-$ also misses ⇒ next candidate (IBES standardized-basis estimate type, or small-denominator deflation). Spec change Sina-gated; this is the fingerprint evidence only.
