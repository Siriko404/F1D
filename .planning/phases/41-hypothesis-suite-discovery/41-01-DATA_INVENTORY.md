# Phase 41 Plan 01: Data Inventory

**Created:** 2026-02-06
**Purpose:** Complete inventory of ALL available data sources and variables BEFORE conducting literature review

---

## 1. Input Data Sources (1_Inputs/)

### 1.1 Earnings Call Transcript Data

| Data Source | Location | Format | Size | Coverage | Notes |
|-------------|----------|--------|------|----------|-------|
| speaker_data_2002-2018 | 1_Inputs/speaker_data_*.parquet | Parquet | 4.7 GB total | 2002-2018 | 17 files, ~112,968 calls |
| | speaker_data_2002.parquet | Parquet | 100 MB | 2002 | 3,355 calls |
| | speaker_data_2003.parquet | Parquet | 180 MB | 2003 | 5,900 calls |
| | speaker_data_2004.parquet | Parquet | 234 MB | 2004 | 6,637 calls |
| | speaker_data_2005.parquet | Parquet | 229 MB | 2005 | 6,853 calls |
| | speaker_data_2006.parquet | Parquet | 288 MB | 2006 | 6,943 calls |
| | speaker_data_2007.parquet | Parquet | 307 MB | 2007 | 7,109 calls |
| | speaker_data_2008.parquet | Parquet | 331 MB | 2008 | 7,289 calls |
| | speaker_data_2009.parquet | Parquet | 335 MB | 2009 | 7,269 calls |
| | speaker_data_2010.parquet | Parquet | 359 MB | 2010 | 7,280 calls |
| | speaker_data_2011.parquet | Parquet | 365 MB | 2011 | 7,223 calls |
| | speaker_data_2012.parquet | Parquet | 340 MB | 2012 | 7,097 calls |
| | speaker_data_2013.parquet | Parquet | 321 MB | 2013 | 6,887 calls |
| | speaker_data_2014.parquet | Parquet | 342 MB | 2014 | 6,876 calls |
| | speaker_data_2015.parquet | Parquet | 340 MB | 2015 | 6,806 calls |
| | speaker_data_2016.parquet | Parquet | 323 MB | 2016 | 6,654 calls |
| | speaker_data_2017.parquet | Parquet | 382 MB | 2017 | 6,689 calls |
| | speaker_data_2018.parquet | Parquet | 421 MB | 2018 | 6,101 calls |

**Total:** 112,968 earnings call transcripts
**Unique firms:** 2,429 (from manifest)
**Speakers identified:** 9,982,346 total (Analyst: 36%, CEO: 18%, Manager: 46%)

---

### 1.2 Text Analysis Dictionary

| Data Source | Location | Format | Size | Coverage | Notes |
|-------------|----------|--------|------|----------|-------|
| Loughran-McDonald Master Dictionary | 1_Inputs/Loughran-McDonald_MasterDictionary_1993-2024.csv | CSV | 8.6 MB | 86,554 words | 8 sentiment categories |

**Categories Available:**
- Negative
- Positive
- Uncertainty
- Litigious
- Strong Modal (e.g., must, shall, will)
- Weak Modal (e.g., may, might, could)
- Constraining
- Complexity (syllables)

---

### 1.3 Market Data (CRSP)

| Data Source | Location | Format | Size | Coverage | Notes |
|-------------|----------|--------|------|----------|-------|
| CRSP Daily Stock Returns | 1_Inputs/CRSP_DSF/CRSP_DSF_*.parquet | Parquet | ~2 GB total | 1999 Q1 - 2022 Q4 | 96 quarterly files |
| | CRSP_DSF_1999_Q1 to 2022_Q4 | Parquet | ~20 MB each | 1999-2022 | ~534K obs per quarter |

**Key variables:** PERMNO, date, PRC, VOL, RET, SHROUT, vwretd, ewretd, sprtrn
**Merge key:** PERMNO (CRSP identifier)

---

### 1.4 CRSP-Compustat CCM Link Table

| Data Source | Location | Format | Size | Coverage | Notes |
|-------------|----------|--------|------|----------|-------|
| CCM Link Table | 1_Inputs/CRSPCompustat_CCM/CRSPCompustat_CCM.parquet | Parquet | ? | 32,421 links | GVKEY-PERMNO mapping |

**Key variables:** gvkey, conm, tic, cusip, LPERMNO, LINKPRIM, LINKDT, LINKENDDT
**Merge keys:**
- Text measures -> Compustat: gvkey
- Text measures -> CRSP: via CCM (gvkey -> LPERMNO)

---

### 1.5 Compustat Fundamentals

| Data Source | Location | Format | Size | Coverage | Notes |
|-------------|----------|--------|------|----------|-------|
| Compustat North America Daily | 1_Inputs/comp_na_daily_all/comp_na_daily_all.parquet | Parquet | ? | ? | 956,229 observations |

**Merge key:** gvkey + fiscal year

---

### 1.6 IBES Analyst Forecasts

| Data Source | Location | Format | Size | Coverage | Notes |
|-------------|----------|--------|------|----------|-------|
| IBES Detailed Forecasts | 1_Inputs/tr_ibes/tr_ibes.parquet | Parquet | 340 MB | 25,501,215 obs | 1999-2024 |

**Key variables:**
- TICKER, CUSIP, STATPERS (statistical period), FPEDATS (fiscal period end date)
- MEANEST (mean forecast), STDEV (forecast dispersion/standard deviation)
- NUMEST (number of estimates), ACTUAL (actual earnings)
- FPI (fiscal period indicator: 6=quarterly, 7=annual)

**Coverage:**
- STATPERS: 1999-01-14 to 2023-12-14
- FPEDATS: 1995-11-30 to 2024-11-30
- Mean NUMEST: 4.57 analysts
- Max NUMEST: 62 analysts

**Merge key:** CUSIP -> gvkey (via CCM) or TICKER

---

### 1.7 Execucomp Executive Compensation

| Data Source | Location | Format | Size | Coverage | Notes |
|-------------|----------|--------|------|----------|-------|
| Execucomp | 1_Inputs/Execucomp/comp_execucomp.parquet | Parquet | 42 MB | 370,545 obs | 1992-2025 |

**Key variables:**
- gvkey, year, execid, exec_fullname
- salary, bonus, tdc1 (total compensation), tdc2
- pceo (CEO flag: "CEO" if CEO, else NaN)
- title, becameceo, leftco

**Coverage:**
- Years: 1992-2025
- Firms: 4,170 unique gvkeys
- Total observations: 370,545

**Merge key:** gvkey + year

---

### 1.8 CEO Dismissal Data

| Data Source | Location | Format | Size | Coverage | Notes |
|-------------|----------|--------|------|----------|-------|
| CEO Dismissal Dataset | 1_Inputs/CEO Dismissal Data 2021.02.03.xlsx | Excel | 2.5 MB | 9,390 obs | ?-2018 |

**Key variables:**
- gvkey, year, coname, exec_fullname
- ceo_dismissal (1=forced dismissal, 0=other departure)
- Departure Code, tenure_no, leftofc

**Coverage in 2002-2018:**
- Total departure events: 6,257
- CEO dismissals (ceo_dismissal=1): 1,059
- Non-forced departures (ceo_dismissal=0): 3,852
- Remaining: NA/uncoded

**Peak years:** 2017 (963 events), 2018 (825 events)

**Merge key:** gvkey + year

---

### 1.9 SDC M&A Data

| Data Source | Location | Format | Size | Coverage | Notes |
|-------------|----------|--------|------|----------|-------|
| SDC M&A Merged | 1_Inputs/SDC/sdc-ma-merged.parquet | Parquet | 25 MB | 142,457 deals | 1999-2025 |

**Key variables:**
- Date Announced, Date Effective, Deal Status
- Acquiror/Target 6-digit CUSIP, Ticker Symbol, SIC
- Deal Value (USD Millions)
- Percentage of Cash, Percentage of Stock
- Deal Type, M&A Type, Form of the Deal

**Coverage in 2002-2018:**
- Total deals: 95,452
- Typical annual volume: ~5,000-7,000 deals

**Merge key:** 6-digit CUSIP -> gvkey (via CCM) or ticker

---

### 1.10 CCCL Instrument (H6 - SEC Scrutiny)

| Data Source | Location | Format | Size | Coverage | Notes |
|-------------|----------|--------|------|----------|-------|
| CCCL Shift-Share Instrument | 1_Inputs/CCCL instrument/instrument_shift_intensity_2005_2022.parquet | Parquet | 15 MB | 145,693 obs | 2005-2022 |

**Key variables:**
- gvkey, cik, sic, sic2, ff12, ff48
- shift_intensity_sale_ff12/ff48/sic2 (Bartik instrument)
- shift_intensity_mkvalt_ff12/ff48/sic2
- cccl_count_ff12/ff48/sic2 (CCCL treatment count)

**Coverage:** 2005-2022
**Purpose:** Shift-share design for H6 (SEC CCCL scrutiny -> reduced uncertainty)

**Merge key:** gvkey + year

---

## 2. Output Variables (4_Outputs/)

### 2.1 Text Measures (2.2_Variables)

**Location:** 4_Outputs/2_Textual_Analysis/2.2_Variables/2026-01-30_152557/

| Variable Category | Variable Name | Years | N | Firms | Notes |
|-------------------|---------------|-------|---|-------|-------|
| **Manager QA Uncertainty** | Manager_QA_Uncertainty_pct | 2002-2018 | 112,968 | 2,429 | LM uncertainty words |
| **Manager QA Weak Modal** | Manager_QA_Weak_Modal_pct | 2002-2018 | 112,968 | 2,429 | Hedging language (may/might/could) |
| **Manager QA Strong Modal** | Manager_QA_Strong_Modal_pct | 2002-2018 | 112,968 | 2,429 | Commitment language (must/shall) |
| **Manager QA Negative** | Manager_QA_Negative_pct | 2002-2018 | 112,968 | 2,429 | LM negative sentiment |
| **Manager QA Positive** | Manager_QA_Positive_pct | 2002-2018 | 112,968 | 2,429 | LM positive sentiment |
| **Manager QA Constraining** | Manager_QA_Constraining_pct | 2002-2018 | 112,968 | 2,429 | LM constraining language |
| **Manager QA Litigious** | Manager_QA_Litigious_pct | 2002-2018 | 112,968 | 2,429 | LM litigious language |
| **Manager Pres Uncertainty** | Manager_Pres_Uncertainty_pct | 2002-2018 | 112,968 | 2,429 | Presentation uncertainty |
| **Manager Pres Weak Modal** | Manager_Pres_Weak_Modal_pct | 2002-2018 | 112,968 | 2,429 | Presentation hedging |
| **Manager Pres Strong Modal** | Manager_Pres_Strong_Modal_pct | 2002-2018 | 112,968 | 2,429 | Presentation commitment |
| **Manager Pres Negative** | Manager_Pres_Negative_pct | 2002-2018 | 112,968 | 2,429 | Presentation negative |
| **Manager Pres Positive** | Manager_PAres_Positive_pct | 2002-2018 | 112,968 | 2,429 | Presentation positive |
| **Manager All Uncertainty** | Manager_All_Uncertainty_pct | 2002-2018 | 112,968 | 2,429 | Combined QA+Pres |
| **Manager All Weak Modal** | Manager_All_Weak_Modal_pct | 2002-2018 | 112,968 | 2,429 | Combined hedging |
| **CEO QA Uncertainty** | CEO_QA_Uncertainty_pct | 2002-2018 | 112,968 | 2,429 | CEO-specific uncertainty |
| **CEO QA Weak Modal** | CEO_QA_Weak_Modal_pct | 2002-2018 | 112,968 | 2,429 | CEO-specific hedging |
| **CEO QA Strong Modal** | CEO_QA_Strong_Modal_pct | 2002-2018 | 112,968 | 2,429 | CEO-specific commitment |
| **CEO Pres Uncertainty** | CEO_Pres_Uncertainty_pct | 2002-2018 | 112,968 | 2,429 | CEO presentation uncertainty |
| **CEO Pres Weak Modal** | CEO_Pres_Weak_Modal_pct | 2002-2018 | 112,968 | 2,429 | CEO presentation hedging |
| **Analyst QA Uncertainty** | Analyst_QA_Uncertainty_pct | 2002-2018 | 112,968 | 2,429 | Analyst questions uncertainty |
| **Analyst QA Weak Modal** | Analyst_QA_Weak_Modal_pct | 2002-2018 | 112,968 | 2,429 | Analyst questions hedging |

**Total variables:** 1,785 (15 speaker roles x 8 categories x 3 contexts + metadata)
**Files:** 17 yearly files (linguistic_variables_2002.parquet through 2018)

**Derived measure:**
- `uncertainty_gap`: Q&A uncertainty - Presentation uncertainty (computed in H5)

---

### 2.2 Financial Controls (H1 Cash Holdings Variables)

**Location:** 4_Outputs/3_Financial_V2/2026-02-04_192647/H1_CashHoldings.parquet

| Variable Category | Variable Name | Years | N | Firms | Notes |
|-------------------|---------------|-------|---|-------|-------|
| **Cash Holdings** | cash_holdings | 2002-2018 | 448,004 | 2,428 | CHE/AT (cash/assets) |
| **Leverage** | leverage | 2002-2018 | 448,004 | 2,428 | (DLTT+DLC)/AT |
| **Size** | firm_size | 2002-2018 | 448,004 | 2,428 | ln(assets) |
| **Profitability** | roa | 2002-2018 | 448,004 | 2,428 | ROA (return on assets) |
| **Investment** | capex_at | 2002-2018 | 448,004 | 2,428 | Capital expenditures/assets |
| **Dividend Payer** | dividend_payer | 2002-2018 | 448,004 | 2,428 | Dummy (1=pays dividend) |
| **Liquidity** | current_ratio | 2002-2018 | 448,004 | 2,428 | Current assets/current liabilities |
| **Q** | tobins_q | 2002-2018 | 448,004 | 2,428 | Tobin's Q (investment opportunities) |
| **Cash Flow Volatility** | ocf_volatility | 2002-2018 | 448,004 | 2,428 | Operating CF volatility |

---

### 2.3 H2 Investment Efficiency Variables

**Location:** 4_Outputs/3_Financial_V2/2026-02-05_125355/H2_InvestmentEfficiency.parquet

| Variable Category | Variable Name | Years | N | Firms | Notes |
|-------------------|---------------|-------|---|-------|-------|
| **Overinvestment** | overinvest_dummy | 2002-2018 | 28,887 | ? | 1 if deviates above optimal |
| **Underinvestment** | underinvest_dummy | 2002-2018 | 28,887 | ? | 1 if deviates below optimal |
| **Efficiency Score** | efficiency_score | 2002-2018 | 28,887 | ? | Investment efficiency metric |
| **ROA Residual** | roa_residual | 2002-2018 | 28,887 | ? | Performance residual |
| **Analyst Dispersion** | analyst_dispersion | 2002-2018 | 28,887 | ? | External information quality |
| **Cash Flow Volatility** | cf_volatility | 2002-2018 | 28,887 | ? | CF uncertainty |
| **Earnings Volatility** | earnings_volatility | 2002-2018 | 28,887 | ? | Earnings uncertainty |
| **Free Cash Flow** | fcf | 2002-2018 | 28,887 | ? | Free cash flow |

---

### 2.4 H3 Payout Policy Variables

**Location:** 4_Outputs/3_Financial_V2/2026-02-05_142731/H3_PayoutPolicy.parquet

| Variable Category | Variable Name | Years | N | Firms | Notes |
|-------------------|---------------|-------|---|-------|-------|
| **Dividend Stability** | div_stability | 2002-2018 | 16,616 | ? | Dividend stability measure |
| **Payout Flexibility** | payout_flexibility | 2002-2018 | 16,616 | ? | Payout flexibility measure |
| **Firm Maturity** | firm_maturity | 2002-2018 | 16,616 | ? | Lifecycle stage |
| **FCF Growth** | fcf_growth | 2002-2018 | 16,616 | ? | Free cash flow growth |
| **Dividend Payer** | is_div_payer | 2002-2018 | 16,616 | ? | Dummy (1=pays dividend) |

---

### 2.5 H5 Analyst Dispersion Variables

**Location:** 4_Outputs/3_Financial_V2/3.5_H5Variables/2026-02-05_212750/H5_AnalystDispersion.parquet

| Variable Category | Variable Name | Years | N | Firms | Notes |
|-------------------|---------------|-------|---|-------|-------|
| **Dependent Variable** | dispersion_lead | 1999-2024 | 850,889 | 8,693 | Forward dispersion (t+1 quarter) |
| **Lagged DV** | prior_dispersion | 1999-2024 | 850,889 | 8,693 | Prior dispersion |
| **Control: Earnings Surprise** | earnings_surprise | 1999-2024 | 850,889 | 8,693 | Earnings surprise |
| **Control: Loss Dummy** | loss_dummy | 1999-2024 | 850,889 | 8,693 | 1 if negative earnings |
| **Control: Firm Size** | firm_size | 1999-2024 | 850,889 | 8,693 | ln(market cap) |
| **Control: Leverage** | leverage | 1999-2024 | 850,889 | 8,693 | Debt ratio |
| **Control: Earnings Volatility** | earnings_volatility | 1999-2024 | 850,889 | 8,693 | Earnings SD |
| **Control: Analyst Coverage** | analyst_coverage | 1999-2024 | 850,889 | 8,693 | NUMEST |
| **IV: Manager QA Uncertainty** | Manager_QA_Uncertainty_pct | 2002-2017 | 264,504* | ? | LM uncertainty in QA |
| **IV: Manager QA Weak Modal** | Manager_QA_Weak_Modal_pct | 2002-2017 | 264,504* | ? | Hedging in QA |
| **IV: Manager Pres Uncertainty** | Manager_Pres_Uncertainty_pct | 2002-2017 | 264,504* | ? | LM uncertainty in Pres |
| **IV: Manager Pres Weak Modal** | Manager_Pres_Weak_Modal_pct | 2002-2017 | 264,504* | ? | Hedging in Pres |
| **IV: CEO QA Uncertainty** | CEO_QA_Uncertainty_pct | 2002-2017 | 264,504* | ? | CEO uncertainty in QA |
| **IV: CEO QA Weak Modal** | CEO_QA_Weak_Modal_pct | 2002-2017 | 264,504* | ? | CEO hedging in QA |
| **Derived: Uncertainty Gap** | uncertainty_gap | 2002-2017 | 264,504* | ? | QA uncertainty - Pres uncertainty |

*Complete cases (all variables non-missing)

**Coverage:**
- Total observations: 850,889
- Complete cases: 264,504
- Unique firms: 8,693
- Fiscal years: 1996-2024 (29 years)
- Fiscal quarters: Q1-Q4

---

## 3. Merge Feasibility Matrix

| Dataset A | Dataset B | Merge Key | Feasibility | Expected Overlap | Notes |
|-----------|-----------|-----------|-------------|------------------|-------|
| Text measures (2.2) | H1 controls (3.2) | gvkey + fiscal_year | HIGH | ~25K firm-years | Direct merge |
| Text measures (2.2) | Execucomp | gvkey + year | MEDIUM | ~15K firm-years | 4,170 firms in Execucomp |
| Text measures (2.2) | IBES (via CCM) | CUSIP -> gvkey + date | HIGH | ~264K obs (H5 verified) | H5 achieved 264K complete |
| Text measures (2.2) | SDC M&A | CUSIP -> gvkey + year | HIGH | ~1K+ events | 95K deals 2002-2018 |
| Text measures (2.2) | CEO dismissal | gvkey + year | MEDIUM | ~1K events | 1,059 dismissals 2002-2018 |
| Text measures (2.2) | CRSP DSF | gvkey -> PERMNO + date | HIGH | ~2,429 firms | Requires CCM link |
| Text measures (2.2) | CCCL instrument | gvkey + year | HIGH | ~1,500 firm-years | CCCL covers 2005-2022 |
| H1 controls | Execucomp | gvkey + year | HIGH | ~15K firm-years | Both use gvkey |
| H5 dispersion | Text measures | gvkey + fiscal_year/quarter | HIGH | 264K verified | Achieved in H5 |

---

## 4. Verified Data Source Details

### 4.1 IBES Analyst Data Verification

**File:** 1_Inputs/tr_ibes/tr_ibes.parquet
**Shape:** 25,501,215 rows x 24 columns

**Key columns verified:**
- TICKER, CUSIP, OFTIC, CNAME
- STATPERS (statistical period), FPEDATS (fiscal period end)
- FPI (fiscal period indicator: 6=quarterly, 7=annual)
- NUMEST, MEANEST, STDEV, HIGHEST, LOWEST
- ACTUAL, ANNDATS_ACT, ANNTIMS_ACT

**Date ranges:**
- STATPERS: 1999-01-14 to 2023-12-14
- FPEDATS: 1995-11-30 to 2024-11-30

**NUMEST distribution:**
- Mean: 4.57 analysts
- Median: 3 analysts
- Max: 62 analysts
- 25th percentile: 1 analyst

**Key insight:** IBES provides excellent coverage for analyst forecast dispersion (STDEV/|MEANEST|) and forecast error.

---

### 4.2 Execucomp Verification

**File:** 1_Inputs/Execucomp/comp_execucomp.parquet
**Shape:** 370,545 rows x 107 columns

**Key compensation variables:**
- salary: Base salary ($ thousands)
- bonus: Cash bonus ($ thousands)
- tdc1: Total direct compensation (salary + bonus + other)
- tdc2: Total compensation (includes equity, options)
- pceo: CEO flag ("CEO" if CEO, NaN otherwise)
- title, becameceo, leftco: Tenure information

**Coverage:**
- Years: 1992-2025
- Firms: 4,170 unique gvkeys
- CEO observations: Available (pceo flag)

**Key insight:** Execucomp allows for CEO compensation tests, pay-for-performance sensitivity, and compensation-uncertainty relationships.

---

### 4.3 CEO Dismissal Data Verification

**File:** 1_Inputs/CEO Dismissal Data 2021.02.03.xlsx
**Shape:** 9,390 rows x 16 columns

**Key variables:**
- gvkey, year, coname, exec_fullname
- ceo_dismissal (1=forced, 0=other)
- Departure Code, tenure_no, leftofc

**Events in 2002-2018:**
- Total events: 6,257
- CEO dismissals: 1,059
- Non-forced departures: 3,852
- Remaining: Unclassified

**Annual distribution:** 258-963 events per year, with spikes in 2017 (963) and 2018 (825)

**Key insight:** Sufficient events for survival analysis or logistic regression on CEO turnover.

---

### 4.4 SDC M&A Data Verification

**File:** 1_Inputs/SDC/sdc-ma-merged.parquet
**Shape:** 142,457 rows x 34 columns

**Key variables:**
- Date Announced, Date Effective, Deal Status
- Acquiror/Target 6-digit CUSIP, Ticker Symbol
- Deal Value (USD Millions)
- Percentage of Cash, Percentage of Stock
- M&A Type, Deal Type

**Deals in 2002-2018:** 95,452 total deals
**Typical volume:** 5,000-7,000 deals/year

**Key insight:** Large sample for M&A target dummy, deal premium, acquisition likelihood tests.

---

### 4.5 CRSP DSF Verification

**Location:** 1_Inputs/CRSP_DSF/
**Files:** 96 quarterly files (CRSP_DSF_1999_Q1 through 2022_Q4)
**Format:** Parquet (~20 MB each)
**Sample file shape:** 534,684 rows x 63 columns

**Key variables:**
- PERMNO, date, RET, PRC, VOL, SHROUT
- vwretd, vwretx (value-weighted returns)
- ewretd, ewretx (equal-weighted returns)
- sprtrn (S&P 500 return)

**Coverage:** 1999 Q1 through 2022 Q4

**Key insight:** Sufficient for future stock returns, abnormal returns, volatility calculations.

---

### 4.6 CCCL Instrument Verification

**File:** 1_Inputs/CCCL instrument/instrument_shift_intensity_2005_2022.parquet
**Shape:** 145,693 rows x 24 columns

**Key variables:**
- gvkey, cik, sic, sic2, ff12, ff48
- shift_intensity_sale_ff12/ff48/sic2 (Bartik instrument)
- cccl_count_ff12/ff48/sic2 (treatment count)

**Coverage:** 2005-2022

**Key insight:** Provides shift-share instrument for H6 (SEC CCCL scrutiny -> reduced uncertainty).

---

## 5. Summary Statistics by Data Category

| Category | Sources | Primary Variables | Firm Coverage | Time Coverage |
|----------|---------|-------------------|---------------|---------------|
| **Text Measures (IVs)** | 2.2_Variables | 1,785 linguistic variables | 2,429 | 2002-2018 |
| **Financial Controls** | 3_Financial_V2 | 9 core controls | 2,428 | 2002-2018 |
| **Analyst Forecasts** | IBES | Dispersion, forecast error | 8,693 (via H5) | 1996-2024 |
| **Executive Comp** | Execucomp | tdc1, salary, bonus | 4,170 | 1992-2025 |
| **CEO Turnover** | Dismissal data | ceo_dismissal | 1,059 events | 2002-2018 |
| **M&A Activity** | SDC | Deal status, premium | ~95K deals | 2002-2018 |
| **Stock Returns** | CRSP DSF | RET, volatility | ~2,400+ | 1999-2022 |
| **SEC Scrutiny** | CCCL instrument | Shift intensity | ~1,500+ | 2005-2022 |

---

## 6. Variable Availability for Hypothesis Testing

### 6.1 Independent Variables (Speech Measures)

| IV Category | Available Variables | Sample (N) |
|-------------|-------------------|-----------|
| **Uncertainty** | Manager_QA_Uncertainty_pct, CEO_QA_Uncertainty_pct, Manager_Pres_Uncertainty_pct, CEO_Pres_Uncertainty_pct, uncertainty_gap | 112,968 calls |
| **Hedging (Weak Modal)** | Manager_QA_Weak_Modal_pct, CEO_QA_Weak_Modal_pct, Manager_Pres_Weak_Modal_pct, CEO_Pres_Weak_Modal_pct | 112,968 calls |
| **Commitment (Strong Modal)** | Manager_QA_Strong_Modal_pct, CEO_QA_Strong_Modal_pct, Manager_Pres_Strong_Modal_pct, CEO_Pres_Strong_Modal_pct | 112,968 calls |
| **Sentiment** | *_Negative_pct, *_Positive_pct (for all speaker types) | 112,968 calls |
| **Constraining** | *_Constraining_pct (all speaker types) | 112,968 calls |
| **Litigious** | *_Litigious_pct (all speaker types) | 112,968 calls |

### 6.2 Dependent Variables (Outcomes)

| DV Category | Available Measures | Data Source | Feasibility |
|-------------|-------------------|-------------|-------------|
| **Analyst Dispersion** | dispersion_lead (STDEV/|MEANEST|) | IBES (via H5) | HIGH - 264K complete |
| **Forecast Error** | |MEANEST - ACTUAL|/|ACTUAL| | IBES | HIGH - available |
| **Analyst Coverage** | NUMEST | IBES | HIGH - available |
| **Cash Holdings** | cash_holdings (CHE/AT) | Compustat | HIGH - 448K obs |
| **Leverage** | leverage (DLTT+DLC)/AT | Compustat | HIGH - 448K obs |
| **Investment Efficiency** | overinvest/underinvest dummy, efficiency_score | H2 | HIGH - 28K obs |
| **Payout Stability** | div_stability, payout_flexibility | H3 | HIGH - 16K obs |
| **CEO Turnover** | ceo_dismissal | Dismissal data | MEDIUM - 1,059 events |
| **CEO Compensation** | tdc1, salary, bonus | Execucomp | MEDIUM - 370K obs, 4,170 firms |
| **M&A Target** | Target dummy | SDC | HIGH - 95K deals |
| **Deal Premium** | Deal value metrics | SDC | HIGH - available |
| **Stock Returns** | RET, abnormal returns | CRSP DSF | HIGH - 1999-2022 |
| **Volatility** | SD(RET) | CRSP DSF | HIGH - can compute |
| **SEC Scrutiny Effect** | shift_intensity_* | CCCL | HIGH - for H6 |

---

*End of Data Inventory*
