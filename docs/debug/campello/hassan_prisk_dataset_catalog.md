# Hassan et al. (2019) PRisk Dataset — Complete Variable Catalog

**File:** `inputs/FirmLevelRisk/firmquarter_2022q1.csv`  
**Format:** Tab-separated, 76.4 MB  
**Observations:** 354,518 firm-quarters  
**Firms:** 13,149 unique gvkeys  
**Temporal coverage:** 2002Q1 – 2022Q1  
**Earnings call dates:** 01-Apr-2002 to 31-Oct-2021  
**HQ countries:** 85 (US=64%, CA=6%, GB=3%)  
**Reference:** Hassan, Hollander, van Lent & Tahoun (2019, QJE)

---

## Identifier Columns

| Column | Type | Non-Null | Coverage | Unique | Notes |
|---|---|---|---|---|---|
| `gvkey` | string | 354,518 | 100.0% | 13,149 | Compustat global company key |
| `company_name` | string | 354,518 | 100.0% | 13,710 | S&P company name |
| `hqcountrycode` | string | 354,300 | 99.9% | 85 | ISO 2-letter HQ country |
| `isin` | string | 351,992 | 99.3% | 13,289 | ISIN identifier |
| `cusip` | string | 251,817 | 71.0% | 8,435 | CUSIP (US firms only) |
| `ticker` | string | 328,159 | 92.6% | 11,283 | Stock ticker |
| `date` | string | 354,518 | 100.0% | — | Format `YYYYqQ` (e.g. `2015q3`) |
| `date_earningscall` | string | 354,518 | 100.0% | — | Actual earnings call date (DD-Mon-YYYY) |

---

## Core PRisk (6 columns)

Firm-quarter aggregate of political-risk bigrams from earnings call transcripts. All columns: 353,437 non-null (99.7%), zero negatives possible (raw counts).

### PRisk — Total Political Risk Score

| Stat | Value |
|---|---|
| Non-null | 353,437 (99.7%) |
| Mean | 131.94 |
| Std | 236.25 |
| Min | 0 |
| P01 | 0 |
| P05 | 0 |
| P25 | 19.80 |
| P50 | 65.53 |
| P75 | 153.14 |
| P95 | 469.19 |
| P99 | 1,059.64 |
| Max | 11,056.90 |
| Zero | 52,102 (14.7%) |
| >0 | 301,335 (85.3%) |

### NPRisk — Count of Political-Risk Bigrams

| Stat | Value |
|---|---|
| Non-null | 353,437 (99.7%) |
| Mean | 903.82 |
| Std | 1,448.18 |
| Min | 0 |
| P01 | 0 |
| P05 | 0 |
| P25 | 146.29 |
| P50 | 472.80 |
| P75 | 1,082.46 |
| P95 | 3,208.94 |
| P99 | 6,861.61 |
| Max | 69,623.50 |
| Zero | 26,429 (7.5%) |
| >0 | 327,008 (92.5%) |

### Risk — Risk Sub-Component

| Stat | Value |
|---|---|
| Non-null | 353,437 (99.7%) |
| Mean | 70.45 |
| Std | 66.96 |
| Min | 0 |
| P01 | 0 |
| P05 | 0 |
| P25 | 27.87 |
| P50 | 54.20 |
| P75 | 92.89 |
| P95 | 192.11 |
| P99 | 323.95 |
| Max | 1,776.43 |
| Zero | 30,743 (8.7%) |
| >0 | 322,694 (91.3%) |

### PSentiment — Positive Political Sentiment

| Stat | Value |
|---|---|
| Non-null | 353,437 (99.7%) |
| Mean | 1,124.28 |
| Std | 1,396.49 |
| Min | −22,084.30 |
| P01 | −2,486.77 |
| P05 | −798.18 |
| P25 | 376.62 |
| P50 | 1,065.81 |
| P75 | 1,818.82 |
| P95 | 3,279.21 |
| P99 | 4,964.03 |
| Max | 29,098.60 |
| Zero | 4,367 (1.2%) |
| >0 | 298,650 (84.5%) |
| <0 | 50,420 (14.3%) |

### NPSentiment — Count of Positive-Sentiment Political Bigrams

| Stat | Value |
|---|---|
| Non-null | 353,437 (99.7%) |
| Mean | 9,586.15 |
| Std | 18,133.60 |
| Min | −310,437.00 |
| P01 | −42,141.40 |
| P05 | −16,498.60 |
| P25 | 971.29 |
| P50 | 9,086.68 |
| P75 | 18,051.90 |
| P95 | 37,238.60 |
| P99 | 59,579.80 |
| Max | 543,221.00 |
| Zero | 4,361 (1.2%) |
| >0 | 273,169 (77.3%) |
| <0 | 75,907 (21.5%) |

### Sentiment — Net Political Sentiment

| Stat | Value |
|---|---|
| Non-null | 353,437 (99.7%) |
| Mean | 739.15 |
| Std | 557.75 |
| Min | −5,804.12 |
| P01 | −645.65 |
| P05 | −157.86 |
| P25 | 388.60 |
| P50 | 736.84 |
| P75 | 1,091.85 |
| P95 | 1,645.78 |
| P99 | 2,090.62 |
| Max | 5,074.49 |
| Zero | 1,957 (0.6%) |
| >0 | 323,076 (91.4%) |
| <0 | 28,404 (8.0%) |

---

## Sub-Topical PRisk (8 columns)

Decomposes PRisk into 8 policy domains. All 353,437 non-null (99.7%). Same bigram-count × weight scale as overall PRisk. All non-negative (raw counts). All columns heavily right-skewed (mean >> median, P99 >> mean).

### Summary Table

| Column | Policy Area | Mean | Std | P50 | P95 | P99 | Max | % >0 | % =0 |
|---|---|---|---|---|---|---|---|---|---|
| `PRiskT_economic` | Economic policy | 3,908 | 7,734 | 1,817 | 13,957 | 33,854 | 491,426 | 90.4% | 9.6% |
| `PRiskT_environment` | Environment | 4,067 | 11,596 | 1,619 | 14,558 | 37,889 | 1,613,320 | 89.9% | 10.1% |
| `PRiskT_trade` | Trade policy | 2,990 | 11,630 | 980 | 10,741 | 31,102 | 1,743,780 | 87.0% | 13.0% |
| `PRiskT_institutions` | Institutions/governance | 2,465 | 5,961 | 1,043 | 8,663 | 23,724 | 429,202 | 89.6% | 10.4% |
| `PRiskT_health` | Healthcare | 3,652 | 12,127 | 1,433 | 12,659 | 34,092 | 1,103,240 | 89.8% | 10.2% |
| `PRiskT_security` | National security | 3,614 | 8,460 | 1,652 | 12,742 | 31,773 | 1,873,100 | 90.3% | 9.7% |
| `PRiskT_tax` | Tax policy | 3,781 | 9,723 | 1,556 | 13,634 | 34,323 | 936,348 | 88.9% | 11.1% |
| `PRiskT_technology` | Technology | 2,717 | 6,212 | 1,151 | 9,881 | 24,713 | 415,954 | 88.9% | 11.1% |

### Full Distributions

#### PRiskT_economic

| Stat | Value |
|---|---|
| Mean | 3,907.79 | Std | 7,734.33 | Min | 0 |
| P01 | 0 | P05 | 0 | P25 | 607.07 |
| P50 | 1,816.91 | P75 | 4,287.83 | P95 | 13,956.80 |
| P99 | 33,853.70 | Max | 491,426.00 |
| Zero | 33,967 (9.6%) | >0 | 319,470 (90.4%) |

#### PRiskT_environment

| Stat | Value |
|---|---|
| Mean | 4,067.36 | Std | 11,596.40 | Min | 0 |
| P01 | 0 | P05 | 0 | P25 | 489.33 |
| P50 | 1,618.88 | P75 | 4,096.40 | P95 | 14,557.80 |
| P99 | 37,889.20 | Max | 1,613,320.00 |
| Zero | 35,645 (10.1%) | >0 | 317,792 (89.9%) |

#### PRiskT_trade

| Stat | Value |
|---|---|
| Mean | 2,989.65 | Std | 11,630.20 | Min | 0 |
| P01 | 0 | P05 | 0 | P25 | 228.48 |
| P50 | 980.37 | P75 | 2,747.38 | P95 | 10,741.20 |
| P99 | 31,101.90 | Max | 1,743,780.00 |
| Zero | 45,917 (13.0%) | >0 | 307,520 (87.0%) |

#### PRiskT_institutions

| Stat | Value |
|---|---|
| Mean | 2,465.21 | Std | 5,960.98 | Min | 0 |
| P01 | 0 | P05 | 0 | P25 | 326.69 |
| P50 | 1,043.12 | P75 | 2,536.60 | P95 | 8,662.69 |
| P99 | 23,723.90 | Max | 429,202.00 |
| Zero | 36,859 (10.4%) | >0 | 316,578 (89.6%) |

#### PRiskT_health

| Stat | Value |
|---|---|
| Mean | 3,651.97 | Std | 12,126.70 | Min | 0 |
| P01 | 0 | P05 | 0 | P25 | 447.38 |
| P50 | 1,432.78 | P75 | 3,531.27 | P95 | 12,659.40 |
| P99 | 34,091.70 | Max | 1,103,240.00 |
| Zero | 36,164 (10.2%) | >0 | 317,273 (89.8%) |

#### PRiskT_security

| Stat | Value |
|---|---|
| Mean | 3,613.93 | Std | 8,460.40 | Min | 0 |
| P01 | 0 | P05 | 0 | P25 | 539.46 |
| P50 | 1,651.87 | P75 | 3,905.60 | P95 | 12,741.50 |
| P99 | 31,773.40 | Max | 1,873,100.00 |
| Zero | 34,198 (9.7%) | >0 | 319,239 (90.3%) |

#### PRiskT_tax

| Stat | Value |
|---|---|
| Mean | 3,781.12 | Std | 9,722.95 | Min | 0 |
| P01 | 0 | P05 | 0 | P25 | 445.74 |
| P50 | 1,556.40 | P75 | 3,924.28 | P95 | 13,634.30 |
| P99 | 34,322.50 | Max | 936,348.00 |
| Zero | 39,131 (11.1%) | >0 | 314,306 (88.9%) |

#### PRiskT_technology

| Stat | Value |
|---|---|
| Mean | 2,717.36 | Std | 6,211.53 | Min | 0 |
| P01 | 0 | P05 | 0 | P25 | 329.14 |
| P50 | 1,151.47 | P75 | 2,902.13 | P95 | 9,881.07 |
| P99 | 24,712.90 | Max | 415,954.00 |
| Zero | 39,194 (11.1%) | >0 | 314,243 (88.9%) |

---

## Brexit-Specific (5 columns)

**Coverage:** 140,720 non-null (39.7%). Columns exist only from 2011Q1 onward (not populated for 2002–2010). Data is sparse with extreme right-skew: ~97% of non-null values = 0.

**Critical methodological finding:** Brexit columns are post-event response variables, not pre-treatment exposures. See quarterly breakdown below.

### Brexit_Risk

| Stat | Value |
|---|---|
| Non-null | 140,720 (39.7%) |
| Mean | 0.1553 |
| Std | 2.0280 |
| Min | 0 |
| P01 | 0 | P05 | 0 | P25 | 0 |
| P50 | 0 | P75 | 0 | P95 | 0 |
| P99 | 0 | Max | 233.55 |
| Zero | 139,437 (99.1%) |
| >0 | 1,283 (0.9%) |

### Brexit_Exposure

| Stat | Value |
|---|---|
| Non-null | 140,720 (39.7%) |
| Mean | 0.9543 | Std | 7.4591 | Min | 0 |
| P99 | 30.70 | Max | 486.89 |
| Zero | 136,202 (96.8%) | >0 | 4,518 (3.2%) |

### Brexit_Neg_Sentiment

| Stat | Value |
|---|---|
| Non-null | 140,720 (39.7%) |
| Mean | 0.3186 | Std | 3.3602 | Min | 0 |
| P99 | 11.63 | Max | 221.24 |
| Zero | 138,585 (98.5%) | >0 | 2,135 (1.5%) |

### Brexit_Pos_Sentiment

| Stat | Value |
|---|---|
| Non-null | 140,720 (39.7%) |
| Mean | 0.1899 | Std | 2.4379 | Min | 0 |
| P99 | 5.62 | Max | 265.53 |
| Zero | 139,289 (99.0%) | >0 | 1,431 (1.0%) |

### Brexit_Net_Sentiment

| Stat | Value |
|---|---|
| Non-null | 140,720 (39.7%) |
| Mean | −0.1287 | Std | 3.1965 | Min | −221.24 |
| P99 | 0 | Max | 151.29 |
| Zero | 138,283 (98.3%) | >0 | 818 (0.6%) | <0 | 1,619 (1.2%) |

### Brexit_Risk Quarterly Detail (2015–2016)

| Quarter | Rows | >0 | Mean |
|---|---|---|---|
| 2015Q1 | 4,696 | 0 | 0.0000 |
| 2015Q2 | 4,258 | 0 | 0.0000 |
| 2015Q3 | 4,771 | 1 | 0.0011 |
| 2015Q4 | 4,198 | 0 | 0.0000 |
| 2016Q1 | 4,612 | 11 | 0.0340 |
| 2016Q2 | 4,081 | 37 | 0.1438 |
| 2016Q3 | 4,638 | 325 | 1.2776 |
| 2016Q4 | 4,094 | 102 | 0.3754 |

**Jump point:** 2016Q3 (referendum quarter). Pre-referendum: essentially zero. Post-referendum: spikes to mean 1.28, 325 firms with non-zero.

---

## COVID-19 (5 columns)

All 354,507 non-null (100.0% coverage). Loaded as zero-filled for pre-2020 periods. Only relevant 2020+.

| Column | Mean | Std | P50 | P95 | P99 | Max | % >0 |
|---|---|---|---|---|---|---|---|
| `Covid_Exposure` | 0.156 | 0.587 | 0 | 1.14 | 3.01 | 13.40 | 12.4% |
| `Covid_Neg_Sentiment` | 0.061 | 0.270 | 0 | 0.42 | 1.35 | 10.22 | 9.6% |
| `Covid_Pos_Sentiment` | 0.041 | 0.191 | 0 | 0.27 | 0.97 | 9.66 | 8.2% |
| `Covid_Net_Sentiment` | −0.020 | 0.202 | 0 | 0 | 0.38 | 9.66 | — |
| `Covid_Risk` | 0.010 | 0.065 | 0 | 0 | 0.31 | 2.98 | 3.7% |

---

## Disease Exposures (4 columns)

All 354,507 non-null (100.0%). Extremely sparse — <1% non-zero in all cases.

| Column | Mean | Std | Max | % >0 | Non-Zero Count |
|---|---|---|---|---|---|
| `SARS_Exposure` | 0.0024 | 0.0440 | 4.86 | 0.73% | 2,584 |
| `H1N1_Exposure` | 0.0025 | 0.0582 | 7.92 | 0.51% | 1,814 |
| `Zika_Exposure` | 0.0006 | 0.0285 | 4.67 | 0.11% | 386 |
| `Ebola_Exposure` | 0.0008 | 0.0337 | 4.73 | 0.16% | 564 |

---

## Temporal Coverage by Year (2010–2016)

| Year | Firm-Quarters | Firms |
|---|---|---|
| 2010 | 17,758 | 5,173 |
| 2011 | 18,219 | 5,395 |
| 2012 | 18,394 | 5,708 |
| 2013 | 16,474 | 4,976 |
| 2014 | 17,687 | 5,473 |
| 2015 | 17,923 | 5,487 |
| 2016 | 17,425 | 5,369 |

**Drop in 2013:** 16,474 (−10.4% vs 2012). No structural explanation in the dataset — may reflect Compustat coverage or earnings-call availability.

---

## Top-10 HQ Countries

| Country | Rows | % |
|---|---|---|
| US | 225,971 | 63.8% |
| CA | 22,387 | 6.3% |
| GB | 10,423 | 2.9% |
| IN | 6,276 | 1.8% |
| DE | 6,274 | 1.8% |
| JP | 6,207 | 1.8% |
| CN | 5,705 | 1.6% |
| BR | 5,259 | 1.5% |
| SE | 4,898 | 1.4% |
| AU | 4,693 | 1.3% |

---

## F1D Pipeline Integration

### Active Consumers (Code That Reads This File)

| Module | Columns Used | Purpose |
|---|---|---|
| `_hassan_engine.py` | PRisk, NPRisk, gvkey, date | Quarterly → fiscal-year aggregation engine |
| `prisk_q.py` | PRisk | Contemporaneous quarterly PRisk |
| `prisk_q_lag.py` | PRisk | Lagged 1Q |
| `prisk_q_lag2.py` | PRisk | Lagged 2Q |
| `prisk_q_lead.py` | PRisk | Lead 1Q |
| `prisk_q_lead2.py` | PRisk | Lead 2Q |
| `political_risk_subtopics.py` | PRiskT_trade, PRiskT_tax (+6 others) | Trump 2016 DiD treatment (H1.5) |
| `trump_did_treatment.py` | PRiskT_trade, PRiskT_tax | Trump DiD treatment label construction |
| `redistricting_treatment.py` | PRisk | Redistricting DiD control (H1.6) |
| `redistricting_treatment_geocode.py` | PRisk | Geocode-based redistricting control |
| `macro_uncertainty.py` | PRisk | Macro-uncertainty measurement |

### Unused Columns (Present But No Consumer)

- `Brexit_Exposure`, `Brexit_Neg_Sentiment`, `Brexit_Pos_Sentiment`, `Brexit_Net_Sentiment`, `Brexit_Risk`
- `Covid_Exposure`, `Covid_Neg_Sentiment`, `Covid_Pos_Sentiment`, `Covid_Net_Sentiment`, `Covid_Risk`
- `SARS_Exposure`, `H1N1_Exposure`, `Zika_Exposure`, `Ebola_Exposure`
- `Risk`, `PSentiment`, `NPSentiment`, `Sentiment` (core sentiment columns — PRisk and NPRisk used, but sentiment sub-components are not)
- `company_name`, `isin`, `cusip`, `ticker` (identifiers — gvkey is the merge key)

---

## Campello Brexit DiD — Suitability Assessment

| Requirement | Met? | Detail |
|---|---|---|
| Pre-2016Q3 measurement | **No** | Brexit_Risk = 0 for 99.998% of 2015 rows (1/17,923 > 0) |
| Firm-level cross-sectional variation | **No** | 99.1% of all non-null values are zero |
| Stable pre-treatment distribution | **No** | Data doesn't exist before 2011; jumps 300× at 2016Q3 |
| Pre-existing exposure (not post-event response) | **No** | Spikes sharply at referendum quarter — measures reaction, not vulnerability |

**Verdict:** Hassan Brexit columns are post-referendum outcome variables. They measure which firms began discussing Brexit after the vote. They cannot substitute for Campello's pre-referendum treatment measures (β^UK 2010–2014, or textual 2015 10-K mentions). The 8 sub-topics are available and stable pre-2016 but measure generic policy sensitivity, not Brexit-specific exposure.

---

**Generated:** 2026-05-29 | **For:** Supervisor Cat2 audit
