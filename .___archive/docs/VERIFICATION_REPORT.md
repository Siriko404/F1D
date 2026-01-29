# Pipeline Verification Report

**Last Updated:** 2025-12-29 19:04:09

---

# Step 1: Sample Manifest Pipeline Verification

**Generated:** 2025-12-29 19:04:00

This report verifies EACH SCRIPT in Step 1 individually, showing inputs → outputs.


---
## Script 1.1: CleanMetadata

**Purpose:** Clean Unified-info, deduplicate, filter for earnings calls (event_type='1'), date range 2002-2018

### INPUT: Unified-info.parquet

**Unified-info.parquet:** 465,434 rows × 30 columns

**Numeric Columns:**
| Column | Type | Count | Null% | Min | Max | Mean | Median | Std |
|:-------|:-----|------:|------:|----:|----:|-----:|-------:|----:|
| `processing_lag_hours` | float64 | 465,434 | 0.0% | -71.21722222222222 | 144335.1327777778 | 1034.5771 | 16.4517 | 7781.1692 |
| `source_file_year` | int32 | 465,434 | 0.0% | 2002.0 | 2018.0 | 2011.2554 | 2012.0 | 4.5176 |
| `data_quality_score` | float64 | 465,434 | 0.0% | 0.5 | 1.0 | 0.934 | 1.0 | 0.0929 |
| `speaker_record_count` | int64 | 465,434 | 0.0% | 0.0 | 3802.0 | 58.809 | 52.0 | 47.7184 |

**Categorical Columns:**
| Column | Type | Count | Null% | Unique | Top 5 Values |
|:-------|:-----|------:|------:|-------:|:-------------|
| `file_name` | object | 465,434 | 0.0% | 428330 | 5394796_T(15), 6126573_T(8), 5622838_T(8), 7171123... |
| `company_name` | object | 465,434 | 0.0% | 14456 | Federal Government of United States of America(661... |
| `start_date` | datetime64[ns] | 465,434 | 0.0% | 111570 | 2015-07-31 00:00:00(145), 2015-05-01 01:00:00(126)... |
| `event_type` | object | 465,434 | 0.0% | 17 | 1(327428), 7(83071), 5(18301), 33(8386), 34(7757) |
| `event_type_name` | object | 465,434 | 0.0% | 16 | Earning Conference Call/Presentation(327428), Conf... |
| `call_desc` | object | 465,434 | 0.0% | 424294 | Edited Transcript of US***  29-Oct-09 4:00pm GMT(6... |
| `event_title` | object | 465,434 | 0.0% | 407383 | U.S. President Barack Obama Delivers Weekly Radio ... |
| `city` | object | 465,434 | 0.0% | 4253 | New York(38417), (18898), London(11464), NEW YORK(... |
| `business_quarter` | object | 465,434 | 0.0% | 68 | 2016Q2(10590), 2017Q2(10372), 2015Q2(10311), 2016Q... |
| `processing_quarter` | object | 465,434 | 0.0% | 70 | 2017Q3(10562), 2015Q3(10490), 2016Q1(10328), 2017Q... |

### OUTPUT: metadata_cleaned.parquet

**metadata_cleaned.parquet:** 297,547 rows × 30 columns

**Numeric Columns:**
| Column | Type | Count | Null% | Min | Max | Mean | Median | Std |
|:-------|:-----|------:|------:|----:|----:|-----:|-------:|----:|
| `processing_lag_hours` | float64 | 297,547 | 0.0% | -16.717222222222222 | 144335.1327777778 | 719.5316 | 14.0775 | 6257.9443 |
| `source_file_year` | int32 | 297,547 | 0.0% | 2002.0 | 2018.0 | 2010.7379 | 2011.0 | 4.654 |
| `data_quality_score` | float64 | 297,547 | 0.0% | 0.5 | 1.0 | 0.9271 | 1.0 | 0.0959 |
| `speaker_record_count` | int64 | 297,547 | 0.0% | 0.0 | 534.0 | 68.5996 | 63.0 | 44.6205 |

**Categorical Columns:**
| Column | Type | Count | Null% | Unique | Top 5 Values |
|:-------|:-----|------:|------:|-------:|:-------------|
| `file_name` | object | 297,547 | 0.0% | 297547 | 2134418_T(1), 2093541_T(1), 935608_T(1), 2301639_T... |
| `company_name` | object | 297,547 | 0.0% | 13404 | Oracle Corp(205), McKesson Corp(142), General Elec... |
| `start_date` | datetime64[ns] | 297,547 | 0.0% | 67832 | 2010-08-06 01:00:00(88), 2011-08-05 01:00:00(88), ... |
| `event_type` | object | 297,547 | 0.0% | 1 | 1(297547) |
| `event_type_name` | object | 297,547 | 0.0% | 1 | Earning Conference Call/Presentation(297547) |
| `call_desc` | object | 297,547 | 0.0% | 295998 | Edited Transcript of 4523.T earnings conference ca... |
| `event_title` | object | 297,547 | 0.0% | 296886 | The Progressive Corporation Investor Relations Con... |
| `city` | object | 297,547 | 0.0% | 3640 | NEW YORK(8430), (7393), London(6297), HOUSTON(5884... |
| `business_quarter` | object | 297,547 | 0.0% | 68 | 2018Q3(6096), 2018Q1(5668), 2017Q3(5660), 2018Q4(5... |
| `processing_quarter` | object | 297,547 | 0.0% | 70 | 2018Q3(6255), 2017Q3(5932), 2018Q2(5841), 2018Q1(5... |

**Schema Changes:**
- Rows: 465,434 → 297,547 (63.9% retained)
- Columns added (0): 
- Columns removed (0): 

---
## Script 1.2: LinkEntities

**Purpose:** Link metadata to Compustat/CRSP via GVKEY matching (PERMNO, CUSIP, fuzzy name)

### INPUT 1: metadata_cleaned.parquet (from 1.1)

**From previous step:** 297,547 rows

### INPUT 2: CRSPCompustat_CCM.parquet

**CRSPCompustat_CCM.parquet:** 32,421 rows × 15 columns

**Numeric Columns:**
| Column | Type | Count | Null% | Min | Max | Mean | Median | Std |
|:-------|:-----|------:|------:|----:|----:|-----:|-------:|----:|
| `gvkey` | int64 | 32,421 | 0.0% | 1000.0 | 356289.0 | 46266.5705 | 21731.0 | 58941.3271 |
| `cik` | float64 | 32,421 | 10.89% | 8.0 | 2074176.0 | 881631.4464 | 894705.0 | 531054.426 |
| `sic` | int64 | 32,421 | 0.0% | 100.0 | 9997.0 | 4936.6567 | 4923.0 | 2120.9533 |
| `naics` | float64 | 32,421 | 9.28% | 21.0 | 999990.0 | 417615.8016 | 448150.0 | 183169.0588 |
| `LPERMNO` | int64 | 32,421 | 0.0% | 10000.0 | 93436.0 | 56075.7669 | 66966.0 | 29801.6516 |
| `LPERMCO` | int64 | 32,421 | 0.0% | 2.0 | 60123.0 | 24505.6841 | 20061.0 | 19135.8283 |

**Categorical Columns:**
| Column | Type | Count | Null% | Unique | Top 5 Values |
|:-------|:-----|------:|------:|-------:|:-------------|
| `conm` | object | 32,421 | 0.0% | 27898 | STARZ(10), COMCAST CORP(9), MITCHELL ENERGY & DEV ... |
| `tic` | object | 32,421 | 0.01% | 27898 | STRZA(10), CMCSA(9), DAIEY(8), LSXMK(8), MND.2(8) |
| `cusip` | object | 32,421 | 0.0% | 27899 | 85571Q102(10), 20030N101(9), 233798404(8), 5312297... |
| `LINKPRIM` | object | 32,421 | 0.0% | 4 | P(24096), C(7821), J(411), N(93) |
| `LIID` | object | 32,421 | 0.0% | 24 | 01(26580), 00X(2292), 02(1542), 90(1269), 03(355) |
| `LINKTYPE` | object | 32,421 | 0.0% | 2 | LC(16485), LU(15936) |
| `LINKDT` | object | 32,421 | 0.0% | 10314 | 1972-12-14(1327), 1962-01-31(678), 1979-01-31(337)... |
| `LINKENDDT` | object | 32,421 | 0.0% | 6879 | E(6153), 1962-01-30(549), 1979-01-30(171), 1978-01... |
| `CONML` | object | 32,421 | 0.0% | 27814 | Starz(10), Comcast Corp(9), Crawford & Co(8), BBX ... |

### OUTPUT: metadata_linked.parquet

**metadata_linked.parquet:** 212,389 rows × 40 columns

**Numeric Columns:**
| Column | Type | Count | Null% | Min | Max | Mean | Median | Std |
|:-------|:-----|------:|------:|----:|----:|-----:|-------:|----:|
| `processing_lag_hours` | float64 | 212,389 | 0.0% | -6.562222222222222 | 144335.1327777778 | 683.7201 | 12.1792 | 6205.6993 |
| `source_file_year` | int32 | 212,389 | 0.0% | 2002.0 | 2018.0 | 2010.5155 | 2011.0 | 4.6399 |
| `data_quality_score` | float64 | 212,389 | 0.0% | 0.8333333333333334 | 1.0 | 0.9645 | 1.0 | 0.0682 |
| `speaker_record_count` | int64 | 212,389 | 0.0% | 0.0 | 534.0 | 71.5647 | 67.0 | 43.4378 |
| `gvkey` | int64 | 212,389 | 0.0% | 1004.0 | 328795.0 | 70385.9665 | 29830.0 | 69507.9751 |
| `sic` | int64 | 212,389 | 0.0% | 100.0 | 9997.0 | 4829.8137 | 4813.0 | 1995.9586 |
| `link_quality` | float64 | 212,389 | 0.0% | 80.0 | 100.0 | 95.1232 | 100.0 | 7.8474 |
| `sic_int` | Int64 | 212,389 | 0.0% | 100.0 | 9997.0 | 4829.8137 | 4813.0 | 1995.9586 |
| `ff12_code` | float64 | 212,389 | 13.57% | 1.0 | 11.0 | 7.0787 | 6.0 | 3.1067 |
| `ff48_code` | float64 | 212,389 | 1.22% | 1.0 | 48.0 | 30.4367 | 34.0 | 12.4081 |

**Categorical Columns:**
| Column | Type | Count | Null% | Unique | Top 5 Values |
|:-------|:-----|------:|------:|-------:|:-------------|
| `file_name` | object | 212,389 | 0.0% | 212389 | 2134418_T(1), 2093541_T(1), 935608_T(1), 2301639_T... |
| `company_name` | object | 212,389 | 0.0% | 7308 | Oracle Corp(205), McKesson Corp(142), General Elec... |
| `start_date` | datetime64[ns] | 212,389 | 0.0% | 46195 | 2012-05-04 00:00:00(82), 2010-07-30 01:00:00(80), ... |
| `event_type` | object | 212,389 | 0.0% | 1 | 1(212389) |
| `event_type_name` | object | 212,389 | 0.0% | 1 | Earning Conference Call/Presentation(212389) |
| `call_desc` | object | 212,389 | 0.0% | 211949 | Edited Transcript of 6762.T earnings conference ca... |
| `event_title` | object | 212,389 | 0.0% | 211930 | The Progressive Corporation Investor Relations Con... |
| `city` | object | 212,389 | 0.0% | 2163 | NEW YORK(7469), HOUSTON(5331), New York(3139), (26... |
| `business_quarter` | object | 212,389 | 0.0% | 68 | 2011Q3(3603), 2012Q1(3596), 2008Q2(3582), 2009Q2(3... |
| `processing_quarter` | object | 212,389 | 0.0% | 70 | 2017Q3(3690), 2018Q3(3690), 2011Q2(3648), 2008Q2(3... |

**Schema Changes:**
- Rows: 297,547 → 212,389 (71.4% retained)
- Columns added (10): conm, ff12_code, ff12_name, ff48_code, ff48_name, gvkey, link_method, link_quality, sic, sic_int
- Columns removed (0): 
- **GVKEY match rate:** 100.0%

---
## Script 1.3: BuildTenureMap

**Purpose:** Build CEO tenure map from Execucomp (identify CEO periods per GVKEY)

### INPUT: comp_execucomp.parquet

**comp_execucomp.parquet:** 370,545 rows × 107 columns

**Numeric Columns:**
| Column | Type | Count | Null% | Min | Max | Mean | Median | Std |
|:-------|:-----|------:|------:|----:|----:|-----:|-------:|----:|
| `year` | float64 | 370,545 | 0.0% | 1992.0 | 2025.0 | 2007.8474 | 2008.0 | 9.1791 |
| `sic` | float64 | 370,545 | 0.0% | 100.0 | 9997.0 | 4767.0391 | 4841.0 | 1906.7064 |
| `spindex` | float64 | 370,545 | 0.02% | 1010.0 | 6020.0 | 3290.3473 | 3510.0 | 1310.043 |
| `sub_tele` | float64 | 370,545 | 12.96% | 31.0 | 989.0 | 565.4017 | 607.0 | 249.9448 |
| `page` | float64 | 370,545 | 12.94% | 30.0 | 119.0 | 68.2278 | 67.0 | 10.7479 |
| `co_per_rol` | float64 | 370,545 | 0.0% | 1.0 | 74979.0 | 32616.2485 | 30260.0 | 20692.0194 |
| `execrank` | float64 | 370,545 | 94.16% | 1.0 | 10.0 | 3.2028 | 3.0 | 1.6448 |
| `age` | float64 | 370,545 | 29.01% | 25.0 | 102.0 | 53.3659 | 53.0 | 7.8454 |
| `allothpd` | float64 | 370,545 | 57.78% | -234.533 | 95107.134 | 37.1892 | 0.0 | 602.038 |
| `allothtot` | float64 | 370,545 | 57.78% | -96.992 | 95195.5 | 77.9863 | 9.882 | 700.2435 |

**Categorical Columns:**
| Column | Type | Count | Null% | Unique | Top 5 Values |
|:-------|:-----|------:|------:|-------:|:-------------|
| `gvkey` | object | 370,545 | 0.0% | 4170 | 008264(291), 008539(254), 009846(249), 008549(240)... |
| `address` | object | 370,545 | 0.0% | 4030 | 1200 Main Street(500), 233 South Wacker Drive(453)... |
| `city` | object | 370,545 | 0.0% | 999 | New York(19078), Houston(14787), Chicago(8225), Da... |
| `coname` | object | 370,545 | 0.0% | 4170 | PG&E CORP(291), EXELON CORP(254), EDISON INTERNATI... |
| `cusip` | object | 370,545 | 100.0% | 0 |  |
| `exchange` | object | 370,545 | 0.0% | 5 | NYS(208433), NAS(127967), OTH(30710), OTC(1827), A... |
| `inddesc` | object | 370,545 | 0.02% | 179 | Regional Banks(16252), Health Care Equipment(9576)... |
| `naics` | object | 370,545 | 0.0% | 781 | 522110(19444), 334413(9392), 531120(8071), 524126(... |
| `naicsdesc` | object | 370,545 | 0.0% | 759 | Commercial Banking(19444), Semiconductor and Relat... |
| `sicdesc` | object | 370,545 | 0.0% | 393 | COMMERCIAL BANKS(19320), REAL ESTATE INVESTMENT TR... |

### OUTPUT: tenure_monthly.parquet

**tenure_monthly.parquet:** 997,699 rows × 8 columns

**Numeric Columns:**
| Column | Type | Count | Null% | Min | Max | Mean | Median | Std |
|:-------|:-----|------:|------:|----:|----:|-----:|-------:|----:|
| `year` | int64 | 997,699 | 0.0% | 1945.0 | 2025.0 | 2004.2071 | 2005.0 | 12.2922 |
| `month` | int64 | 997,699 | 0.0% | 1.0 | 12.0 | 6.5247 | 7.0 | 3.4523 |

**Categorical Columns:**
| Column | Type | Count | Null% | Unique | Top 5 Values |
|:-------|:-----|------:|------:|-------:|:-------------|
| `gvkey` | object | 997,699 | 0.0% | 4052 | 006326(958), 003639(853), 001004(840), 010639(839)... |
| `date` | datetime64[ns] | 997,699 | 0.0% | 972 | 2004-12-01 00:00:00(2449), 2006-12-01 00:00:00(244... |
| `ceo_id` | object | 997,699 | 0.0% | 10262 | 08337(984), 34308(804), 25326(737), 00555(688), 00... |
| `ceo_name` | object | 997,699 | 0.0% | 10243 | Alan B. Miller(984), Miles Jay Allison, J.D.(804),... |
| `prev_ceo_id` | object | 997,699 | 58.62% | 6686 | 00430(516), 00816(487), 22916(414), 07786(403), 00... |
| `prev_ceo_name` | object | 997,699 | 58.62% | 6677 | Herbert M. Sandler(516), Ronald Randall Rollins, S... |

**Transformation:** 370,545 exec records -> 997,699 tenure-month records
- **Unique CEOs:** 10,262

---
## Script 1.4: AssembleManifest

**Purpose:** Merge linked metadata with CEO tenure, filter to CEOs with 5+ calls

### INPUT 1: metadata_linked.parquet (from 1.2)

**From Step 1.2:** 212,389 rows

### INPUT 2: tenure_monthly.parquet (from 1.3)

**From Step 1.3:** 997,699 rows

### OUTPUT: master_sample_manifest.parquet

**master_sample_manifest.parquet:** 112,968 rows × 44 columns

**Numeric Columns:**
| Column | Type | Count | Null% | Min | Max | Mean | Median | Std |
|:-------|:-----|------:|------:|----:|----:|-----:|-------:|----:|
| `processing_lag_hours` | float64 | 112,968 | 0.0% | -6.562222222222222 | 144335.1327777778 | 524.5997 | 10.5851 | 5357.0751 |
| `source_file_year` | int32 | 112,968 | 0.0% | 2002.0 | 2018.0 | 2010.2301 | 2010.0 | 4.6619 |
| `data_quality_score` | float64 | 112,968 | 0.0% | 0.8333333333333334 | 1.0 | 0.98 | 1.0 | 0.0542 |
| `speaker_record_count` | int64 | 112,968 | 0.0% | 0.0 | 534.0 | 81.4119 | 77.0 | 43.3889 |
| `sic` | int64 | 112,968 | 0.0% | 100.0 | 9997.0 | 4795.0125 | 4813.0 | 1930.2709 |
| `link_quality` | float64 | 112,968 | 0.0% | 80.0 | 100.0 | 97.5624 | 100.0 | 5.6519 |
| `sic_int` | Int64 | 112,968 | 0.0% | 100.0 | 9997.0 | 4795.0125 | 4813.0 | 1930.2709 |
| `ff12_code` | float64 | 112,968 | 11.74% | 1.0 | 11.0 | 6.9839 | 6.0 | 3.2077 |
| `ff48_code` | float64 | 112,968 | 0.58% | 1.0 | 48.0 | 30.692 | 34.0 | 12.7117 |

**Categorical Columns:**
| Column | Type | Count | Null% | Unique | Top 5 Values |
|:-------|:-----|------:|------:|-------:|:-------------|
| `file_name` | object | 112,968 | 0.0% | 112968 | 1000000_T(1), 1000011_T(1), 1000015_T(1), 1000023_... |
| `company_name` | object | 112,968 | 0.0% | 2803 | Oracle Corp(205), McKesson Corp(142), General Elec... |
| `start_date` | datetime64[ns] | 112,968 | 0.0% | 30068 | 2009-05-01 01:00:00(57), 2006-07-28 00:00:00(54), ... |
| `event_type` | object | 112,968 | 0.0% | 1 | 1(112968) |
| `event_type_name` | object | 112,968 | 0.0% | 1 | Earning Conference Call/Presentation(112968) |
| `call_desc` | object | 112,968 | 0.0% | 112922 | Edited Transcript of VRSK earnings conference call... |
| `event_title` | object | 112,968 | 0.0% | 112768 | The Progressive Corporation Investor Relations Con... |
| `city` | object | 112,968 | 0.0% | 1080 | NEW YORK(4544), HOUSTON(3040), ATLANTA(1609), SAN ... |
| `business_quarter` | object | 112,968 | 0.0% | 68 | 2008Q3(1840), 2009Q2(1840), 2010Q3(1835), 2008Q2(1... |
| `processing_quarter` | object | 112,968 | 0.0% | 70 | 2011Q2(1867), 2012Q2(1866), 2010Q3(1865), 2010Q2(1... |

**Schema Changes:**
- Rows: 212,389 → 112,968 (53.2% retained)
- Columns added (4): ceo_id, ceo_name, prev_ceo_id, prev_ceo_name
- Columns removed (0): 
- **CEO ID coverage:** 100.0%
- **Unique CEOs in sample:** 4,466

---
## Summary

| Script | Input Rows | Output Rows | Retention |
|:-------|----------:|----------:|----------:|
| 1.1_CleanMetadata | 465,434 | 297,547 | 63.9% |
| 1.2_LinkEntities | 297,547 | 212,389 | 71.4% |
| 1.4_AssembleManifest | 212,389 | 112,968 | 53.2% |