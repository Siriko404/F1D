# Numeric Audit Findings

No exceptions found.

## Required derived arithmetic

- Slide 8 CI: `0.0461 +/- 1.96 x 0.0172 = [0.012388, 0.079812]`, displayed as `[0.012, 0.080]`.
- Slide 8 effect-size ratio: `0.0461 / 0.3010 x 100 = 15.3156%`, displayed as `15.3%`.
- Slide 9 residual-uncertainty whiskers, using `estimate +/- 1.96 x SE`: PRE2 `[-0.028088, 0.041688]`; PRE1 `[0.012412, 0.082188]`; GAP `[-0.034852, 0.038452]`; POST `[-0.050480, 0.000480]`.
- Slide 9 cash-ratio whiskers, using `estimate +/- 1.96 x SE`: PRE2 `[-0.003904, 0.005504]`; PRE1 `[0.001396, 0.010804]`; GAP `[-0.001164, 0.012164]`; POST `[-0.019812, -0.011188]`.
- Slide 10 cash-panel whiskers, using `estimate +/- 1.96 x SE`: PRE2 `[-0.023604, 0.044604]`; PRE1 `[0.014496, 0.082704]`; GAP `[-0.029676, 0.041276]`; POST `[-0.044392, 0.005392]`.
- Slide 10 stock-panel whiskers, using `estimate +/- 1.96 x SE`: PRE2 `[-0.077728, 0.066528]`; PRE1 `[-0.099004, 0.018204]`; GAP `[-0.027028, 0.097628]`; POST `[-0.053016, 0.043416]`.
- Slide 10 pooled-arm whiskers: cash `0.0459 +/- 1.96 x 0.0185 = [0.009640, 0.082160]`; stock `-0.0524 +/- 1.96 x 0.0436 = [-0.137856, 0.033056]`.
- Slide 10 direct-Wald CI: `0.0983 +/- 1.96 x 0.0476 = [0.005004, 0.191596]`, displayed as `[0.005, 0.192]`.

Controlling locations: `_tables_from_bible.tex`, `tab:summary_stats` lines 15-65, `tab:empire_building_did` lines 73-115, `tab:empire_drop_matched` lines 123-172, `tab:empire_drop_placebo` lines 180-229, and `tab:empire_cashspec` lines 237-282; `sec34_body_from_ledgers.tex` lines 20-52; `_dwz_replication.tex` lines 18-55.

## Coverage tally

| Slide | Items checked | Exceptions |
|---:|---:|---:|
| 6 | 11 | 0 |
| 7 | 9 | 0 |
| 8 | 17 | 0 |
| 9 | 47 | 0 |
| 10 | 49 | 0 |
| 11 | 0 | 0 |
| 12 | 3 | 0 |
| 13 | 0 | 0 |
