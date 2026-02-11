# V1 Variable Catalog

**Catalog Version:** 1.0
**Last Updated:** 2026-02-11
**Pipeline Version:** F1D v1.0
**Total Variables:** 132

## Table of Contents

- [Overview](#overview)
- [Step 1: Sample Identifiers](#step-1-sample-identifiers) (48 variables)
- [Step 2: Text/Linguistic Variables](#step-2-textlinguistic-variables) (72 variables)
- [Step 3.1: Financial Controls](#step-31-financial-controls) (13 variables)
- [Step 3.2: Market Variables](#step-32-market-variables) (7 variables)
- [Step 4: Model Variables (CEO Clarity)](#step-4-model-variables-ceo-clarity) (13 variables)
- [Variable Naming Conventions](#variable-naming-conventions)
- [Data Dictionary](#data-dictionary)
- [Search Indices](#search-indices)

---

## Overview

This catalog provides a comprehensive reference for all 132 variables in the V1 analysis dataset. Variables are organized by their source and processing step in the F1D (Financial Clarity) pipeline.

### Summary Statistics

| Metric | Value |
|--------|-------|
| **Total Observations** | 5,889 earnings calls |
| **Total CEOs** | 2,457 unique CEOs |
| **Total Firms** | 2,361 unique firms (gvkey) |
| **Sample Period** | 2002-2018 |

### Variable Count by Source

| Source | Variable Count |
|--------|---------------|
| Step 1: Sample Identifiers | 28 |
| Step 2: Text/Linguistic Variables | 72 |
| Step 3.1: Financial Controls | 13 |
| Step 3.2: Market Variables | 6 |
| Step 4: Model Variables | 13 |
| **Total** | **132** |

---

## Step 1: Sample Identifiers

**Source Steps:** 1.1-1.4
**Variable Count:** 28
**Purpose:** Unique identifiers, metadata, and linkage keys for earnings calls and firms

### Sample Identifier Variables

| Variable | Type | Description | Source | Range/Notes |
|----------|------|-------------|--------|--------------|
| file_name | String | Unique identifier for each transcript file | Step 1 | 5,889 unique values |
| company_name | String | Company name | Step 1 | From EventStudy metadata |
| start_date | Date | Earnings call date and time | Step 1 | 2002-01-01 to 2018-12-31 |
| event_type | Integer | Event type identifier | Step 1 | Earnings announcement event |
| event_type_name | String | Event type description | Step 1 | "Earnings Call" |
| call_desc | String | Call description | Step 1 | From EventStudy metadata |
| event_title | String | Event title | Step 1 | Company + date identifier |
| city | String | Location of event | Step 1 | From EventStudy metadata |
| processing_lag_hours | Float | Hours between event and processing | Step 1 | Time lag metric |
| business_quarter | Integer | Fiscal quarter (1-4) | Step 1 | Q1-Q4 |
| processing_quarter | Integer | Processing quarter identifier | Step 1 | Administrative field |
| late_arrival_flag | Integer | Flag for delayed data arrival | Step 1 | 0/1 |
| quarter_assigned | String | Quarter assigned to | Step 1 | Administrative field |
| panel_created_at | Date | Panel creation timestamp | Step 1 | Administrative field |
| source_file_year | Integer | Source file year | Step 1 | 2002-2018 |
| data_lineage_id | String | Data lineage identifier | Step 1 | Traceability |
| original_last_update | Date | Original record update date | Step 1 | From EventStudy |
| last_update | Date | Most recent update timestamp | Step 1 | From EventStudy |
| company_id | String | Company identifier | Step 1 | From EventStudy |
| cusip | String | CUSIP (8 digits) | Step 1 | 2,361 unique values |
| sedol | String | SEDOL code | Step 1 | From EventStudy |
| isin | String | ISIN code | Step 1 | From EventStudy |
| company_ticker | String | Stock ticker symbol | Step 1 | From EventStudy |
| permno | Integer | CRSP PERMNO | Step 1 | Linkage to CRSP data |
| match_type | String | Entity match method | Step 1 | Matching quality indicator |
| match_type_desc | String | Match type description | Step 1 | Quality description |
| data_quality_score | Float | Data quality assessment | Step 1 | Quality metric |
| validation_timestamp | Date | Validation timestamp | Step 1 | Administrative field |
| has_speaker_data | Integer | Flag for speaker data availability | Step 1 | 0/1 |
| speaker_record_count | Integer | Number of speaker segments | Step 1 | Count of segments |
| gvkey | String | Compustat GVKEY (6-digit, zero-padded) | Step 1 | 2,361 unique firms |
| conm | String | Company name (Compustat) | Step 1 | From Compustat |
| sic | Integer | SIC industry code (4-digit) | Step 1 | 100-9997 |
| link_method | String | Linkage method | Step 1 | CCM/CRSP linkage |
| link_quality | String | Linkage quality indicator | Step 1 | From CCM |
| sic_int | Integer | SIC code as integer | Step 1 | Numeric SIC |
| ff12_code | Integer | Fama-French 12-industry code | Step 1 | 1-12 |
| ff12_name | String | Fama-French 12-industry name | Step 1 | Industry classification |
| ff48_code | Integer | Fama-French 48-industry code | Step 1 | 1-48 |
| ff48_name | String | Fama-French 48-industry name | Step 1 | Industry classification |
| ceo_id | String | CEO identifier | Step 1 | 2,457 unique CEOs |
| ceo_name | String | CEO full name | Step 1 | From speaker data |
| prev_ceo_id | String | Previous CEO identifier | Step 1 | CEO succession tracking |
| prev_ceo_name | String | Previous CEO name | Step 1 | CEO succession tracking |
| year | Integer | Calendar year | Step 1 | 2002-2018 |

### Key Relationships

- **gvkey** links to Compustat financial data
- **permno** links to CRSP market data
- **cusip** provides cross-source linkage
- **ceo_id** tracks CEO across multiple calls and firms
- **ff12_code** and **ff48_code** enable industry fixed effects

---

## Step 2: Text/Linguistic Variables

**Source Step:** 2.2_ConstructVariables.py
**Variable Count:** 72
**Purpose:** Linguistic measures derived from earnings call transcripts using Loughran-McDonald dictionary

### Methodology

All linguistic variables are computed as **percentages of total tokens** in the specified text segment, based on the Loughran-McDonald Master Dictionary (1993-2024).

**Formula:**
```
{Category}_pct = (category_word_count / total_tokens) * 100
```

### Variable Naming Pattern

**Pattern:** `{Speaker}_{Context}_{Category}_pct`

#### Speakers
- `Manager`: All managerial speakers (including CEO)
- `CEO`: CEO only
- `NonCEO_Manager`: Managers excluding CEO
- `Analyst`: Financial analysts during Q&A
- `Entire`: All speakers combined

#### Contexts
- `QA`: Question & Answer session
- `Pres`: Formal presentation
- `All`: Combined Q&A + Presentation

#### Linguistic Categories
- `Negative`: Negative sentiment words
- `Positive`: Positive sentiment words
- `Uncertainty`: Uncertainty/hedging words
- `Litigious`: Legal/litigious language
- `Strong_Modal`: Strong modal verbs (must, shall, will)
- `Weak_Modal`: Weak modal verbs (could, might, may)
- `Constraining`: Constraining language

### Manager Linguistic Variables (21 variables)

| Variable | Description | Mean | SD | Min | Max |
|----------|-------------|------|----|-----|-----|
| Manager_QA_Negative_pct | % negative words in manager Q&A | 0.76 | 0.33 | 0 | 4.44 |
| Manager_QA_Positive_pct | % positive words in manager Q&A | 1.19 | 0.46 | 0 | 11.11 |
| Manager_QA_Uncertainty_pct | % uncertainty words in manager Q&A | 0.91 | 0.36 | 0 | 6.25 |
| Manager_QA_Litigious_pct | % litigious words in manager Q&A | 0.15 | 0.20 | 0 | 2.83 |
| Manager_QA_Strong_Modal_pct | % strong modal words in manager Q&A | 0.68 | 0.32 | 0 | 4.55 |
| Manager_QA_Weak_Modal_pct | % weak modal words in manager Q&A | 0.37 | 0.22 | 0 | 6.25 |
| Manager_QA_Constraining_pct | % constraining words in manager Q&A | 0.11 | 0.11 | 0 | 3.13 |
| Manager_Pres_Negative_pct | % negative words in manager presentation | 0.88 | 0.48 | 0 | 4.30 |
| Manager_Pres_Positive_pct | % positive words in manager presentation | 1.76 | 0.62 | 0 | 5.37 |
| Manager_Pres_Uncertainty_pct | % uncertainty words in manager presentation | 0.88 | 0.38 | 0 | 5.59 |
| Manager_Pres_Litigious_pct | % litigious words in manager presentation | 0.20 | 0.25 | 0 | 2.86 |
| Manager_Pres_Strong_Modal_pct | % strong modal words in manager presentation | 0.65 | 0.27 | 0 | 2.61 |
| Manager_Pres_Weak_Modal_pct | % weak modal words in manager presentation | 0.24 | 0.15 | 0 | 2.72 |
| Manager_Pres_Constraining_pct | % constraining words in manager presentation | 0.13 | 0.11 | 0 | 0.95 |
| Manager_All_Negative_pct | % negative words (all manager segments) | 0.82 | 0.33 | 0 | 3.57 |
| Manager_All_Positive_pct | % positive words (all manager segments) | 1.47 | 0.44 | 0.23 | 4.14 |
| Manager_All_Uncertainty_pct | % uncertainty words (all manager segments) | 0.89 | 0.27 | 0.14 | 3.24 |
| Manager_All_Litigious_pct | % litigious words (all manager segments) | 0.17 | 0.19 | 0 | 2.12 |
| Manager_All_Strong_Modal_pct | % strong modal words (all manager segments) | 0.66 | 0.22 | 0.05 | 1.99 |
| Manager_All_Weak_Modal_pct | % weak modal words (all manager segments) | 0.31 | 0.13 | 0 | 1.39 |
| Manager_All_Constraining_pct | % constraining words (all manager segments) | 0.12 | 0.08 | 0 | 0.69 |

### CEO Linguistic Variables (21 variables)

| Variable | Description | N | Mean | SD | Min | Max |
|----------|-------------|---|------|----|-----|-----|
| CEO_QA_Negative_pct | % negative words in CEO Q&A | 4,127 | 0.75 | 0.51 | 0 | 13.33 |
| CEO_QA_Positive_pct | % positive words in CEO Q&A | - | 1.32 | 0.87 | 0 | 40.00 |
| CEO_QA_Uncertainty_pct | % uncertainty words in CEO Q&A | - | 0.87 | 0.48 | 0 | 7.41 |
| CEO_QA_Litigious_pct | % litigious words in CEO Q&A | - | 0.14 | 0.23 | 0 | 3.96 |
| CEO_QA_Strong_Modal_pct | % strong modal words in CEO Q&A | - | 0.69 | 0.46 | 0 | 8.24 |
| CEO_QA_Weak_Modal_pct | % weak modal words in CEO Q&A | - | 0.38 | 0.33 | 0 | 7.41 |
| CEO_QA_Constraining_pct | % constraining words in CEO Q&A | - | 0.11 | 0.15 | 0 | 3.13 |
| CEO_Pres_Negative_pct | % negative words in CEO presentation | 3,998 | 0.84 | 0.57 | 0 | 4.43 |
| CEO_Pres_Positive_pct | % positive words in CEO presentation | - | 2.28 | 0.93 | 0 | 7.64 |
| CEO_Pres_Uncertainty_pct | % uncertainty words in CEO presentation | - | 0.70 | 0.42 | 0 | 3.41 |
| CEO_Pres_Litigious_pct | % litigious words in CEO presentation | - | 0.17 | 0.29 | 0 | 3.63 |
| CEO_Pres_Strong_Modal_pct | % strong modal words in CEO presentation | - | 0.79 | 0.45 | 0 | 5.71 |
| CEO_Pres_Weak_Modal_pct | % weak modal words in CEO presentation | - | 0.21 | 0.19 | 0 | 2.86 |
| CEO_Pres_Constraining_pct | % constraining words in CEO presentation | - | 0.12 | 0.14 | 0 | 1.52 |
| CEO_All_Negative_pct | % negative words (all CEO segments) | 4,172 | 0.79 | 0.40 | 0 | 5.00 |
| CEO_All_Positive_pct | % positive words (all CEO segments) | - | 1.75 | 0.65 | 0 | 5.57 |
| CEO_All_Uncertainty_pct | % uncertainty words (all CEO segments) | - | 0.79 | 0.33 | 0 | 2.86 |
| CEO_All_Litigious_pct | % litigious words (all CEO segments) | - | 0.15 | 0.22 | 0 | 2.44 |
| CEO_All_Strong_Modal_pct | % strong modal words (all CEO segments) | - | 0.73 | 0.33 | 0 | 4.69 |
| CEO_All_Weak_Modal_pct | % weak modal words (all CEO segments) | - | 0.30 | 0.18 | 0 | 2.17 |
| CEO_All_Constraining_pct | % constraining words (all CEO segments) | - | 0.11 | 0.10 | 0 | 1.21 |

### Analyst Linguistic Variables (21 variables)

| Variable | Description | Mean | SD | Min | Max |
|----------|-------------|------|----|-----|-----|
| Analyst_QA_Negative_pct | % negative words in analyst Q&A | 1.29 | 0.48 | 0 | 6.10 |
| Analyst_QA_Positive_pct | % positive words in analyst Q&A | 1.01 | 0.45 | 0 | 5.36 |
| Analyst_QA_Uncertainty_pct | % uncertainty words in analyst Q&A | 1.42 | 0.49 | 0 | 5.45 |
| Analyst_QA_Litigious_pct | % litigious words in analyst Q&A | 0.14 | 0.21 | 0 | 2.30 |
| Analyst_QA_Strong_Modal_pct | % strong modal words in analyst Q&A | 0.24 | 0.20 | 0 | 2.54 |
| Analyst_QA_Weak_Modal_pct | % weak modal words in analyst Q&A | 0.96 | 0.43 | 0 | 5.13 |
| Analyst_QA_Constraining_pct | % constraining words in analyst Q&A | 0.05 | 0.09 | 0 | 1.28 |
| Analyst_Pres_Negative_pct | % negative words in analyst presentation | 0.77 | 0.61 | 0 | 2.33 |
| Analyst_Pres_Positive_pct | % positive words in analyst presentation | 0.83 | 0.61 | 0 | 2.25 |
| Analyst_Pres_Uncertainty_pct | % uncertainty words in analyst presentation | 1.19 | 1.19 | 0 | 4.65 |
| Analyst_Pres_Litigious_pct | % litigious words in analyst presentation | 0.24 | 0.35 | 0 | 1.22 |
| Analyst_Pres_Strong_Modal_pct | % strong modal words in analyst presentation | 0.84 | 0.56 | 0 | 2.16 |
| Analyst_Pres_Weak_Modal_pct | % weak modal words in analyst presentation | 0.45 | 0.52 | 0 | 2.07 |
| Analyst_Pres_Constraining_pct | % constraining words in analyst presentation | 0.10 | 0.23 | 0 | 1.01 |
| Analyst_All_Negative_pct | % negative words (all analyst segments) | 1.29 | 0.48 | 0 | 6.10 |
| Analyst_All_Positive_pct | % positive words (all analyst segments) | 1.01 | 0.45 | 0 | 5.36 |
| Analyst_All_Uncertainty_pct | % uncertainty words (all analyst segments) | 1.42 | 0.49 | 0 | 5.45 |
| Analyst_All_Litigious_pct | % litigious words (all analyst segments) | 0.14 | 0.21 | 0 | 2.30 |
| Analyst_All_Strong_Modal_pct | % strong modal words (all analyst segments) | 0.24 | 0.20 | 0 | 2.54 |
| Analyst_All_Weak_Modal_pct | % weak modal words (all analyst segments) | 0.96 | 0.43 | 0 | 5.13 |
| Analyst_All_Constraining_pct | % constraining words (all analyst segments) | 0.05 | 0.09 | 0 | 1.28 |

### Non-CEO Manager Linguistic Variables (21 variables)

| Variable | Description | Mean | SD | Min | Max |
|----------|-------------|------|----|-----|-----|
| NonCEO_Manager_QA_Negative_pct | % negative words in non-CEO manager Q&A | 0.75 | 0.46 | 0 | 5.71 |
| NonCEO_Manager_QA_Positive_pct | % positive words in non-CEO manager Q&A | 1.04 | 0.59 | 0 | 11.11 |
| NonCEO_Manager_QA_Uncertainty_pct | % uncertainty words in non-CEO manager Q&A | 0.97 | 0.88 | 0 | 50.00 |
| NonCEO_Manager_QA_Litigious_pct | % litigious words in non-CEO manager Q&A | 0.16 | 0.33 | 0 | 14.29 |
| NonCEO_Manager_QA_Strong_Modal_pct | % strong modal words in non-CEO manager Q&A | 0.67 | 0.45 | 0 | 7.14 |
| NonCEO_Manager_QA_Weak_Modal_pct | % weak modal words in non-CEO manager Q&A | 0.36 | 0.31 | 0 | 6.59 |
| NonCEO_Manager_QA_Constraining_pct | % constraining words in non-CEO manager Q&A | 0.12 | 0.17 | 0 | 4.55 |
| NonCEO_Manager_Pres_Negative_pct | % negative words in non-CEO manager presentation | 0.89 | 0.55 | 0 | 4.65 |
| NonCEO_Manager_Pres_Positive_pct | % positive words in non-CEO manager presentation | 1.44 | 0.85 | 0 | 20.00 |
| NonCEO_Manager_Pres_Uncertainty_pct | % uncertainty words in non-CEO manager presentation | 1.04 | 0.71 | 0 | 9.20 |
| NonCEO_Manager_Pres_Litigious_pct | % litigious words in non-CEO manager presentation | 0.21 | 0.28 | 0 | 3.61 |
| NonCEO_Manager_Pres_Strong_Modal_pct | % strong modal words in non-CEO manager presentation | 0.61 | 0.37 | 0 | 4.28 |
| NonCEO_Manager_Pres_Weak_Modal_pct | % weak modal words in non-CEO manager presentation | 0.28 | 0.26 | 0 | 2.80 |
| NonCEO_Manager_Pres_Constraining_pct | % constraining words in non-CEO manager presentation | 0.13 | 0.14 | 0 | 2.54 |
| NonCEO_Manager_All_Negative_pct | % negative words (all non-CEO manager segments) | 0.83 | 0.42 | 0 | 5.71 |
| NonCEO_Manager_All_Positive_pct | % positive words (all non-CEO manager segments) | 1.25 | 0.53 | 0 | 4.14 |
| NonCEO_Manager_All_Uncertainty_pct | % uncertainty words (all non-CEO manager segments) | 0.99 | 0.46 | 0 | 7.14 |
| NonCEO_Manager_All_Litigious_pct | % litigious words (all non-CEO manager segments) | 0.18 | 0.23 | 0 | 3.05 |
| NonCEO_Manager_All_Strong_Modal_pct | % strong modal words (all non-CEO manager segments) | 0.63 | 0.32 | 0 | 7.14 |
| NonCEO_Manager_All_Weak_Modal_pct | % weak modal words (all non-CEO manager segments) | 0.31 | 0.21 | 0 | 4.17 |
| NonCEO_Manager_All_Constraining_pct | % constraining words (all non-CEO manager segments) | 0.13 | 0.12 | 0 | 2.54 |

### Entire Transcript Linguistic Variables (21 variables)

| Variable | Description | Mean | SD | Min | Max |
|----------|-------------|------|----|-----|-----|
| Entire_QA_Negative_pct | % negative words in Q&A (all speakers) | 1.11 | 0.35 | 0.25 | 3.85 |
| Entire_QA_Positive_pct | % positive words in Q&A (all speakers) | 1.09 | 0.34 | 0 | 5.16 |
| Entire_QA_Uncertainty_pct | % uncertainty words in Q&A (all speakers) | 1.06 | 0.28 | 0.20 | 2.96 |
| Entire_QA_Litigious_pct | % litigious words in Q&A (all speakers) | 0.14 | 0.17 | 0 | 2.00 |
| Entire_QA_Strong_Modal_pct | % strong modal words in Q&A (all speakers) | 0.55 | 0.22 | 0 | 2.04 |
| Entire_QA_Weak_Modal_pct | % weak modal words in Q&A (all speakers) | 0.57 | 0.19 | 0 | 2.53 |
| Entire_QA_Constraining_pct | % constraining words in Q&A (all speakers) | 0.09 | 0.08 | 0 | 0.68 |
| Entire_Pres_Negative_pct | % negative words in presentation (all speakers) | 0.90 | 0.45 | 0.06 | 3.63 |
| Entire_Pres_Positive_pct | % positive words in presentation (all speakers) | 1.71 | 0.58 | 0 | 4.31 |
| Entire_Pres_Uncertainty_pct | % uncertainty words in presentation (all speakers) | 0.92 | 0.36 | 0.13 | 5.15 |
| Entire_Pres_Litigious_pct | % litigious words in presentation (all speakers) | 0.20 | 0.24 | 0 | 2.56 |
| Entire_Pres_Strong_Modal_pct | % strong modal words in presentation (all speakers) | 0.69 | 0.25 | 0 | 2.03 |
| Entire_Pres_Weak_Modal_pct | % weak modal words in presentation (all speakers) | 0.27 | 0.15 | 0 | 2.58 |
| Entire_Pres_Constraining_pct | % constraining words in presentation (all speakers) | 0.14 | 0.10 | 0 | 0.93 |
| Entire_All_Negative_pct | % negative words (all segments, all speakers) | 1.02 | 0.32 | 0.23 | 3.17 |
| Entire_All_Positive_pct | % positive words (all segments, all speakers) | 1.34 | 0.37 | 0.34 | 3.23 |
| Entire_All_Uncertainty_pct | % uncertainty words (all segments, all speakers) | 0.99 | 0.23 | 0.30 | 2.87 |
| Entire_All_Litigious_pct | % litigious words (all segments, all speakers) | 0.17 | 0.18 | 0 | 1.99 |
| Entire_All_Strong_Modal_pct | % strong modal words (all segments, all speakers) | 0.60 | 0.18 | 0.09 | 1.58 |
| Entire_All_Weak_Modal_pct | % weak modal words (all segments, all speakers) | 0.44 | 0.13 | 0.08 | 1.27 |
| Entire_All_Constraining_pct | % constraining words (all segments, all speakers) | 0.11 | 0.07 | 0 | 0.63 |

### Loughran-McDonald Dictionary Reference

The linguistic categories are based on the Loughran-McDonald Master Dictionary (2014), which includes word counts for each category:

| Category | Word Count (Approximate) | Examples |
|----------|------------------------|----------|
| Negative | ~2,300 words | loss, fail, risk, concern |
| Positive | ~350 words | growth, success, strong, benefit |
| Uncertainty | ~300 words | may, possibly, approximate, uncertain |
| Litigious | ~900 words | claim, legal, lawsuit, defendant |
| Strong Modal | ~20 words | must, shall, will, always |
| Weak Modal | ~15 words | could, might, may, possibly |
| Constraining | ~200 words | must, required, restrict, limit |

**Reference:** Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. *Journal of Finance*, 66(1), 35-65.

---

## Step 3.1: Financial Controls

**Source Step:** 3.1_ConstructFinancialControls.py
**Variable Count:** 13
**Purpose:** Firm-level financial characteristics from Compustat

### Financial Control Variables

| Variable | Type | Description | Formula | Data Field | Notes |
|----------|------|-------------|---------|------------|-------|
| Size | Continuous | Natural log of total assets | ln(atq) | atq | Clipped at 1st/99th percentile |
| BM | Continuous | Book-to-market ratio | ceqq / (cshoq * prccq) | ceqq, cshoq, prccq | Clipped at 1st/99th percentile |
| Lev | Continuous | Leverage ratio | ltq / atq | ltq, atq | Clipped at 1st/99th percentile |
| ROA | Continuous | Return on assets | niq / atq | niq, atq | Clipped at 1st/99th percentile |
| EPS_Growth | Continuous | Year-over-year EPS growth | (EPS - EPS_lag4) / \|EPS_lag4\| | epspxq | Clipped at 1st/99th percentile |
| CurrentRatio | Continuous | Current ratio (liquidity) | actq / lctq | actq, lctq | Clipped at 1st/99th percentile |
| RD_Intensity | Continuous | R&D intensity | xrdq / atq (missing R&D = 0) | xrdq, atq | Clipped at 1st/99th percentile |
| SurpDec | Categorical | Earnings surprise decile | Ranked within quarter | ActualEPS - ForecastEPS | -5 to +5 |
| ActualEPS | Continuous | Actual EPS from IBES | Matched within +/-45 days | IBES | Actual earnings per share |
| ForecastEPS | Continuous | Mean forecast EPS from IBES | Forecast made before call date | IBES | Mean analyst forecast |
| surprise_raw | Continuous | Raw earnings surprise | ActualEPS - ForecastEPS | IBES | Continuous surprise measure |
| shift_intensity_sale_ff12 | Continuous | Competition instrument (sales, FF12) | From CCCL instrument | CCCL | Industry competition measure |
| shift_intensity_mkvalt_ff12 | Continuous | Competition instrument (market cap, FF12) | From CCCL instrument | CCCL | Industry competition measure |
| shift_intensity_sale_ff48 | Continuous | Competition instrument (sales, FF48) | From CCCL instrument | CCCL | Industry competition measure |
| shift_intensity_mkvalt_ff48 | Continuous | Competition instrument (market cap, FF48) | From CCCL instrument | CCCL | Industry competition measure |
| shift_intensity_sale_sic2 | Continuous | Competition instrument (sales, SIC2) | From CCCL instrument | CCCL | Industry competition measure |
| shift_intensity_mkvalt_sic2 | Continuous | Competition instrument (market cap, SIC2) | From CCCL instrument | CCCL | Industry competition measure |

### Data Alignment and Matching

- **Matching Method:** Backward `merge_asof` (most recent quarter <= call date)
- **EPS Growth:** Requires 4-quarter lag (EPS_lag4)
- **SurpDec:** Ranked separately within each quarter across all firms
- **CCCL Instruments:** Matched on gvkey and year
- **Missing Values:** Indicate no available data for the time window

### Winsorization

All continuous financial controls are clipped at the 1st and 99th percentiles to mitigate outlier influence:
- Values below 1st percentile set to 1st percentile value
- Values above 99th percentile set to 99th percentile value

---

## Step 3.2: Market Variables

**Source Step:** 3.2_ConstructMarketVariables.py
**Variable Count:** 6
**Purpose:** Stock market performance and liquidity measures from CRSP

### Market Variable Definitions

| Variable | Type | Description | Formula/Calculation | Mean | SD | Min | Max |
|----------|------|-------------|---------------------|------|----|-----|-----|
| StockRet | Continuous | Stock return (compound, %) | Compound return from (prev_call + 5d) to (current_call - 5d) | 6.12% | 18.80% | -84.10% | +235.78% |
| MarketRet | Continuous | Value-weighted market return (%) | VWRETD from CRSP | 3.87% | 5.80% | -23.82% | +47.09% |
| Volatility | Continuous | Annualized stock volatility (%) | Std(daily ret) * sqrt(252) * 100 | - | - | - | - |
| Amihud | Continuous | Illiquidity measure (event window) | Mean(\|ret\|/volume) * 1e6 | - | - | - | - |
| Corwin_Schultz | Continuous | Bid-ask spread estimator (event) | High-low spread formula | - | - | - | - |
| Delta_Amihud | Continuous | Change in Amihud (event - baseline) | Event window - Baseline window | - | - | - | - |
| Delta_Corwin_Schultz | Continuous | Change in Corwin-Schultz (event - baseline) | Event window - Baseline window | - | - | - | - |

### Calculation Windows

**StockRet Calculation:**
- **Window:** From (previous_call_date + 5 days) to (current_call_date - 5 days)
- **Minimum Requirement:** 10 trading days required
- **Purpose:** Measures cumulative stock performance between consecutive earnings calls

**Event Windows (for Amihud, Corwin-Schultz):**
- **Event Window:** [t-5 days, t+5 days] around earnings call
- **Baseline Window:** [t-35 days, t-6 days] before earnings call
- **Delta Variables:** Event window measure minus baseline window measure

**Amihud Illiquidity Formula:**
```
Amihud = (1/n) * Σ(|ret_t| / volume_t_dollars) * 1,000,000
```
Where:
- ret_t = daily return on day t
- volume_t_dollars = daily trading volume in dollars
- n = number of observations in window

**Requirements:**
- At least 5 observations with positive dollar volume
- Daily returns and trading volume from CRSP

**Corwin-Schultz Bid-Ask Spread Formula:**
```
Spread = 2*(exp(high_low) - 1) / (1 + exp(high_low))
where high_low = [sqrt(2*beta) - sqrt(gamma)] / (3 - 2*sqrt(2))
```
Where:
- beta = absolute difference between high and low prices across 2-day periods
- gamma = high-low ratio within single day
- Requires at least 5 observations with valid bid/ask

### Data Linkage

- **CRSP Linkage:** Via permno (direct or CCM fallback)
- **Missing Values:** Insufficient trading days or invalid price data

---

## Step 4: Model Variables (CEO Clarity)

**Source Step:** 4.1_EstimateCEOClarityFixedEffects.py
**Variable Count:** 13
**Purpose:** CEO-level clarity measures from fixed effects estimation

### CEO Clarity Model Variables

| Variable | Type | Description | Range/Notes |
|----------|------|-------------|--------------|
| ceo_id | String | CEO identifier | 2,457 unique CEOs |
| sample | Categorical | Industry sample classification | Main, Finance, or Utility (based on FF12) |
| gamma_i | Continuous | CEO fixed effect coefficient | From OLS regression |
| ClarityCEO_raw | Continuous | Raw clarity score = -gamma_i | Negative of fixed effect |
| ClarityCEO | Continuous | Standardized clarity score | Z-score of ClarityCEO_raw (mean=0, SD=1) |
| n_calls | Integer | Number of calls per CEO (in sample) | CEOs with >=5 calls included |
| avg_uncertainty | Continuous | Mean Manager_QA_Uncertainty_pct per CEO | Calculated from call-level data |
| std_uncertainty | Continuous | Std of Manager_QA_Uncertainty_pct per CEO | Calculated from call-level data |
| ceo_name | String | CEO full name | From speaker data |
| first_call_date | Date | First earnings call date for CEO | Min(start_date) per CEO |
| last_call_date | Date | Last earnings call date for CEO | Max(start_date) per CEO |
| n_firms | Integer | Number of unique firms (gvkey) per CEO | CEO firm transitions |

### Regression Specification

The CEO clarity measure is estimated from the following OLS regression:

```
Manager_QA_Uncertainty_pct = α + γ_i·CEO_i + β₁·Manager_Pres_Uncertainty_pct
                            + β₂·Analyst_QA_Uncertainty_pct
                            + β₃·Entire_All_Negative_pct
                            + β₄·StockRet + β₅·MarketRet
                            + β₆·EPS_Growth + β₇·SurpDec
                            + δ_t·Year_t + ε_i,t
```

**Components:**
- **γ_i (CEO fixed effect):** Captures CEO-specific uncertainty tendency
- **Controls:** Presentation uncertainty, analyst uncertainty, sentiment, returns, earnings surprise
- **Year Fixed Effects (δ_t):** Control for time trends

### Industry Samples

Regression estimated separately for three industry samples:

| Sample | FF12 Codes | Description |
|--------|------------|-------------|
| **Main** | 1-7, 9-10, 12 | Non-financial, non-utility firms |
| **Finance** | 11 | Financial firms (banks, insurance, etc.) |
| **Utility** | 8 | Utility firms |

### Inclusion Criteria

- **Minimum Calls:** CEOs with >=5 calls in the sample
- **Observation Count:** 5,889 calls across all CEOs
- **Fixed Effects:** 2,457 CEO fixed effects estimated

### Clarity Interpretation

- **ClarityCEO_raw = -γ_i:** Negative sign because gamma_i represents uncertainty propensity
  - Higher gamma_i = higher uncertainty (less clear)
  - Lower gamma_i = lower uncertainty (more clear)

- **ClarityCEO (Standardized):** Z-score transformation
  - Mean = 0, SD = 1
  - Values > 0 = above-average clarity (more clear than typical CEO)
  - Values < 0 = below-average clarity (less clear than typical CEO)

**Example Interpretation:**
- ClarityCEO = +1.5: CEO communicates with 1.5 SD above-average clarity (low uncertainty)
- ClarityCEO = -0.8: CEO communicates with 0.8 SD below-average clarity (high uncertainty)

---

## Variable Naming Conventions

### Linguistic Variables

**Pattern:** `{Speaker}_{Context}_{Category}_pct`

**Components:**
- **Speaker**: Manager, CEO, NonCEO_Manager, Analyst, Entire
- **Context**: QA, Pres, All
- **Category**: Negative, Positive, Uncertainty, Litigious, Strong_Modal, Weak_Modal, Constraining
- **Suffix**: `_pct` indicates percentage of total tokens

**Examples:**
- `CEO_QA_Uncertainty_pct`: CEO uncertainty during Q&A
- `Analyst_Pres_Negative_pct`: Analyst negative sentiment during presentation
- `Entire_All_Strong_Modal_pct`: Strong modal usage by all speakers

### Financial Variables

- **Compustat**: Based on quarterly Compustat data (atq, niq, ltq, etc.)
- **IBES**: Earnings forecasts and actuals from IBES
- **CRSP**: Daily stock returns and liquidity measures
- **CCCL**: Competition shift intensity instruments from CCCL dataset

**Variable Name Style:**
- CamelCase for multi-word financial variables (e.g., `RD_Intensity`, `CurrentRatio`)
- All caps for acronyms (e.g., `EPS_Growth`, `RD_Intensity`)

### Model Variables

- **ClarityCEO_raw**: Raw CEO clarity score (negative of fixed effect)
- **ClarityCEO**: Standardized CEO clarity score (z-scored)
- **gamma_i**: CEO fixed effect coefficient (internal use)

---

## Data Dictionary

### Compustat Field Abbreviations

| Abbreviation | Description | Frequency |
|--------------|-------------|-----------|
| atq | Total assets | Quarterly |
| ceqq | Common equity | Quarterly |
| cshoq | Common shares outstanding | Quarterly |
| prccq | Price close | Quarterly |
| ltq | Total liabilities | Quarterly |
| niq | Net income | Quarterly |
| epspxq | EPS (basic, excluding extraordinary items) | Quarterly |
| actq | Current assets | Quarterly |
| lctq | Current liabilities | Quarterly |
| xrdq | R&D expenses | Quarterly |
| gvkey | Global company key | Identifier |
| conm | Company name | Identifier |
| sic | Standard Industrial Classification code | Identifier |

### CRSP Field Abbreviations

| Abbreviation | Description | Frequency |
|--------------|-------------|-----------|
| permno | CRSP permanent number | Identifier |
| RET | Daily return | Daily |
| VOL | Daily trading volume | Daily |
| VWRETD | Value-weighted market return | Daily |
| PRC | Price | Daily |
| SHROUT | Shares outstanding | Daily |

### IBES Field Abbreviations

| Abbreviation | Description | Frequency |
|--------------|-------------|-----------|
| ActualEPS | Actual earnings per share | Per announcement |
| ForecastEPS | Mean forecast EPS | Per forecast |
| SurpDec | Earnings surprise decile | Derived |

### Industry Classification Abbreviations

| Abbreviation | Description | Values |
|--------------|-------------|--------|
| FF12 | Fama-French 12-industry classification | 1-12 |
| FF48 | Fama-French 48-industry classification | 1-48 |
| SIC | Standard Industrial Classification | 4-digit (100-9997) |

### Other Abbreviations

| Abbreviation | Full Name | Description |
|--------------|-----------|-------------|
| CCM | CRSP-Compustat Merged database | Linkage database |
| CEO | Chief Executive Officer | Speaker type |
| QA | Question & Answer session | Call segment |
| Pres | Formal presentation | Call segment |
| pct | Percentage | Unit of measure |
| CCCL | Competition/Clarity/Change/Liquidity | Instrument dataset |

---

## Search Indices

### Alphabetical Index

<details>
<summary>Click to expand full alphabetical list (132 variables)</summary>

| # | Variable | Section |
|---|----------|---------|
| 1 | ActualEPS | Financial Controls |
| 2 | Amihud | Market Variables |
| 3 | Analyst_All_Constraining_pct | Text Variables (Analyst) |
| 4 | Analyst_All_Litigious_pct | Text Variables (Analyst) |
| 5 | Analyst_All_Negative_pct | Text Variables (Analyst) |
| 6 | Analyst_All_Positive_pct | Text Variables (Analyst) |
| 7 | Analyst_All_Strong_Modal_pct | Text Variables (Analyst) |
| 8 | Analyst_All_Uncertainty_pct | Text Variables (Analyst) |
| 9 | Analyst_All_Weak_Modal_pct | Text Variables (Analyst) |
| 10 | Analyst_Pres_Constraining_pct | Text Variables (Analyst) |
| 11 | Analyst_Pres_Litigious_pct | Text Variables (Analyst) |
| 12 | Analyst_Pres_Negative_pct | Text Variables (Analyst) |
| 13 | Analyst_Pres_Positive_pct | Text Variables (Analyst) |
| 14 | Analyst_Pres_Strong_Modal_pct | Text Variables (Analyst) |
| 15 | Analyst_Pres_Uncertainty_pct | Text Variables (Analyst) |
| 16 | Analyst_Pres_Weak_Modal_pct | Text Variables (Analyst) |
| 17 | Analyst_QA_Constraining_pct | Text Variables (Analyst) |
| 18 | Analyst_QA_Litigious_pct | Text Variables (Analyst) |
| 19 | Analyst_QA_Negative_pct | Text Variables (Analyst) |
| 20 | Analyst_QA_Positive_pct | Text Variables (Analyst) |
| 21 | Analyst_QA_Strong_Modal_pct | Text Variables (Analyst) |
| 22 | Analyst_QA_Uncertainty_pct | Text Variables (Analyst) |
| 23 | Analyst_QA_Weak_Modal_pct | Text Variables (Analyst) |
| 24 | BM | Financial Controls |
| 25 | Corwin_Schultz | Market Variables |
| 26 | CEO_All_Constraining_pct | Text Variables (CEO) |
| 27 | CEO_All_Litigious_pct | Text Variables (CEO) |
| 28 | CEO_All_Negative_pct | Text Variables (CEO) |
| 29 | CEO_All_Positive_pct | Text Variables (CEO) |
| 30 | CEO_All_Strong_Modal_pct | Text Variables (CEO) |
| 31 | CEO_All_Uncertainty_pct | Text Variables (CEO) |
| 32 | CEO_All_Weak_Modal_pct | Text Variables (CEO) |
| 33 | CEO_Pres_Constraining_pct | Text Variables (CEO) |
| 34 | CEO_Pres_Litigious_pct | Text Variables (CEO) |
| 35 | CEO_Pres_Negative_pct | Text Variables (CEO) |
| 36 | CEO_Pres_Positive_pct | Text Variables (CEO) |
| 37 | CEO_Pres_Strong_Modal_pct | Text Variables (CEO) |
| 38 | CEO_Pres_Uncertainty_pct | Text Variables (CEO) |
| 39 | CEO_Pres_Weak_Modal_pct | Text Variables (CEO) |
| 40 | CEO_QA_Constraining_pct | Text Variables (CEO) |
| 41 | CEO_QA_Litigious_pct | Text Variables (CEO) |
| 42 | CEO_QA_Negative_pct | Text Variables (CEO) |
| 43 | CEO_QA_Positive_pct | Text Variables (CEO) |
| 44 | CEO_QA_Strong_Modal_pct | Text Variables (CEO) |
| 45 | CEO_QA_Uncertainty_pct | Text Variables (CEO) |
| 46 | CEO_QA_Weak_Modal_pct | Text Variables (CEO) |
| 47 | ClarityCEO | Model Variables |
| 48 | ClarityCEO_raw | Model Variables |
| 49 | Conm | Sample Identifiers |
| 50 | Corwin_Schultz | Market Variables |
| 51 | CurrentRatio | Financial Controls |
| 52 | Delta_Amihud | Market Variables |
| 53 | Delta_Corwin_Schultz | Market Variables |
| 54 | EPS_Growth | Financial Controls |
| 55 | Entire_All_Constraining_pct | Text Variables (Entire) |
| 56 | Entire_All_Litigious_pct | Text Variables (Entire) |
| 57 | Entire_All_Negative_pct | Text Variables (Entire) |
| 58 | Entire_All_Positive_pct | Text Variables (Entire) |
| 59 | Entire_All_Strong_Modal_pct | Text Variables (Entire) |
| 60 | Entire_All_Uncertainty_pct | Text Variables (Entire) |
| 61 | Entire_All_Weak_Modal_pct | Text Variables (Entire) |
| 62 | Entire_Pres_Constraining_pct | Text Variables (Entire) |
| 63 | Entire_Pres_Litigious_pct | Text Variables (Entire) |
| 64 | Entire_Pres_Negative_pct | Text Variables (Entire) |
| 65 | Entire_Pres_Positive_pct | Text Variables (Entire) |
| 66 | Entire_Pres_Strong_Modal_pct | Text Variables (Entire) |
| 67 | Entire_Pres_Uncertainty_pct | Text Variables (Entire) |
| 68 | Entire_Pres_Weak_Modal_pct | Text Variables (Entire) |
| 69 | Entire_QA_Constraining_pct | Text Variables (Entire) |
| 70 | Entire_QA_Litigious_pct | Text Variables (Entire) |
| 71 | Entire_QA_Negative_pct | Text Variables (Entire) |
| 72 | Entire_QA_Positive_pct | Text Variables (Entire) |
| 73 | Entire_QA_Strong_Modal_pct | Text Variables (Entire) |
| 74 | Entire_QA_Uncertainty_pct | Text Variables (Entire) |
| 75 | Entire_QA_Weak_Modal_pct | Text Variables (Entire) |
| 76 | FF12_code | Sample Identifiers |
| 77 | FF12_name | Sample Identifiers |
| 78 | FF48_code | Sample Identifiers |
| 79 | FF48_name | Sample Identifiers |
| 80 | ForecastEPS | Financial Controls |
| 81 | Lev | Financial Controls |
| 82 | MarketRet | Market Variables |
| 83 | Manager_All_Constraining_pct | Text Variables (Manager) |
| 84 | Manager_All_Litigious_pct | Text Variables (Manager) |
| 85 | Manager_All_Negative_pct | Text Variables (Manager) |
| 86 | Manager_All_Positive_pct | Text Variables (Manager) |
| 87 | Manager_All_Strong_Modal_pct | Text Variables (Manager) |
| 88 | Manager_All_Uncertainty_pct | Text Variables (Manager) |
| 89 | Manager_All_Weak_Modal_pct | Text Variables (Manager) |
| 90 | Manager_Pres_Constraining_pct | Text Variables (Manager) |
| 91 | Manager_Pres_Litigious_pct | Text Variables (Manager) |
| 92 | Manager_Pres_Negative_pct | Text Variables (Manager) |
| 93 | Manager_Pres_Positive_pct | Text Variables (Manager) |
| 94 | Manager_Pres_Strong_Modal_pct | Text Variables (Manager) |
| 95 | Manager_Pres_Uncertainty_pct | Text Variables (Manager) |
| 96 | Manager_Pres_Weak_Modal_pct | Text Variables (Manager) |
| 97 | Manager_QA_Constraining_pct | Text Variables (Manager) |
| 98 | Manager_QA_Litigious_pct | Text Variables (Manager) |
| 99 | Manager_QA_Negative_pct | Text Variables (Manager) |
| 100 | Manager_QA_Positive_pct | Text Variables (Manager) |
| 101 | Manager_QA_Strong_Modal_pct | Text Variables (Manager) |
| 102 | Manager_QA_Uncertainty_pct | Text Variables (Manager) |
| 103 | Manager_QA_Weak_Modal_pct | Text Variables (Manager) |
| 104 | NonCEO_Manager_All_Constraining_pct | Text Variables (Non-CEO Manager) |
| 105 | NonCEO_Manager_All_Litigious_pct | Text Variables (Non-CEO Manager) |
| 106 | NonCEO_Manager_All_Negative_pct | Text Variables (Non-CEO Manager) |
| 107 | NonCEO_Manager_All_Positive_pct | Text Variables (Non-CEO Manager) |
| 108 | NonCEO_Manager_All_Strong_Modal_pct | Text Variables (Non-CEO Manager) |
| 109 | NonCEO_Manager_All_Uncertainty_pct | Text Variables (Non-CEO Manager) |
| 110 | NonCEO_Manager_All_Weak_Modal_pct | Text Variables (Non-CEO Manager) |
| 111 | NonCEO_Manager_Pres_Constraining_pct | Text Variables (Non-CEO Manager) |
| 112 | NonCEO_Manager_Pres_Litigious_pct | Text Variables (Non-CEO Manager) |
| 113 | NonCEO_Manager_Pres_Negative_pct | Text Variables (Non-CEO Manager) |
| 114 | NonCEO_Manager_Pres_Positive_pct | Text Variables (Non-CEO Manager) |
| 115 | NonCEO_Manager_Pres_Strong_Modal_pct | Text Variables (Non-CEO Manager) |
| 116 | NonCEO_Manager_Pres_Uncertainty_pct | Text Variables (Non-CEO Manager) |
| 117 | NonCEO_Manager_Pres_Weak_Modal_pct | Text Variables (Non-CEO Manager) |
| 118 | NonCEO_Manager_QA_Constraining_pct | Text Variables (Non-CEO Manager) |
| 119 | NonCEO_Manager_QA_Litigious_pct | Text Variables (Non-CEO Manager) |
| 120 | NonCEO_Manager_QA_Negative_pct | Text Variables (Non-CEO Manager) |
| 121 | NonCEO_Manager_QA_Positive_pct | Text Variables (Non-CEO Manager) |
| 122 | NonCEO_Manager_QA_Strong_Modal_pct | Text Variables (Non-CEO Manager) |
| 123 | NonCEO_Manager_QA_Uncertainty_pct | Text Variables (Non-CEO Manager) |
| 124 | NonCEO_Manager_QA_Weak_Modal_pct | Text Variables (Non-CEO Manager) |
| 125 | ROA | Financial Controls |
| 126 | RD_Intensity | Financial Controls |
| 127 | Size | Financial Controls |
| 128 | StockRet | Market Variables |
| 129 | SurpDec | Financial Controls |
| 130 | Volatility | Market Variables |
| 131 | gamma_i | Model Variables |
| 132 | surprise_raw | Financial Controls |

</details>

### Category Index

#### Sample Identifiers (48 variables)
- **Metadata (13):** file_name, company_name, start_date, event_type, event_type_name, call_desc, event_title, city, processing_lag_hours, business_quarter, processing_quarter, late_arrival_flag, quarter_assigned, panel_created_at, source_file_year, data_lineage_id, original_last_update, last_update, company_id
- **Quality (5):** data_quality_score, validation_timestamp, has_speaker_data, speaker_record_count, match_type, match_type_desc
- **Linkage (14):** cusip, sedol, isin, company_ticker, permno, gvkey, conm, sic, sic_int, link_method, link_quality, ff12_code, ff12_name, ff48_code, ff48_name
- **Executive (5):** ceo_id, ceo_name, prev_ceo_id, prev_ceo_name, year

#### Text/Linguistic Variables (72 variables)
- **Manager (21):** QA (7), Pres (7), All (7)
- **CEO (21):** QA (7), Pres (7), All (7)
- **Analyst (21):** QA (7), Pres (7), All (7)
- **Non-CEO Manager (21):** QA (7), Pres (7), All (7)
- **Entire (21):** QA (7), Pres (7), All (7)

**Linguistic Categories (7):** Negative, Positive, Uncertainty, Litigious, Strong_Modal, Weak_Modal, Constraining

#### Financial Controls (13 variables)
- **Firm Characteristics (6):** Size, BM, Lev, ROA, CurrentRatio, RD_Intensity
- **Earnings Measures (4):** EPS_Growth, ActualEPS, ForecastEPS, SurpDec, surprise_raw
- **Competition Instruments (6):** shift_intensity_sale_ff12, shift_intensity_mkvalt_ff12, shift_intensity_sale_ff48, shift_intensity_mkvalt_ff48, shift_intensity_sale_sic2, shift_intensity_mkvalt_sic2

#### Market Variables (7 variables)
- **Returns (2):** StockRet, MarketRet
- **Liquidity (2):** Amihud, Corwin_Schultz
- **Changes (2):** Delta_Amihud, Delta_Corwin_Schultz
- **Volatility (1):** Volatility

#### Model Variables (13 variables)
- **CEO Identification (5):** ceo_id, ceo_name, sample, first_call_date, last_call_date
- **Clarity Measures (3):** gamma_i, ClarityCEO_raw, ClarityCEO
- **CEO Statistics (3):** n_calls, n_firms, avg_uncertainty, std_uncertainty

### Variable to Source Script Mapping

| Variable Category | Source Script | File Location |
|------------------|--------------|---------------|
| Sample Identifiers | Multiple | 1.1-1.4/*.py |
| Text/Linguistic Variables | 2.2_ConstructVariables.py | 2_Step2_TextAnalysis/ |
| Financial Controls | 3.1_ConstructFinancialControls.py | 3_Step3_FinancialData/ |
| Market Variables | 3.2_ConstructMarketVariables.py | 3_Step3_FinancialData/ |
| CEO Clarity Variables | 4.1_EstimateCEOClarityFixedEffects.py | 4_Step4_EconometricAnalysis/ |

---

## Appendix

### Statistical Summary Tables

<details>
<summary>View complete descriptive statistics for all 132 variables</summary>

#### Linguistic Variable Summary by Speaker Type

| Speaker Type | Mean Uncertainty (QA) | SD Uncertainty (QA) | Mean Positive (Pres) | SD Positive (Pres) |
|--------------|----------------------|---------------------|---------------------|--------------------|
| Manager | 0.91 | 0.36 | 1.76 | 0.62 |
| CEO | 0.87 | 0.48 | 2.28 | 0.93 |
| Analyst | 1.42 | 0.49 | 0.83 | 0.61 |
| Non-CEO Manager | 0.97 | 0.88 | 1.44 | 0.85 |
| Entire | 1.06 | 0.28 | 1.71 | 0.58 |

#### Financial Variable Summary

| Variable | Mean | SD | 25th Pctl | Median | 75th Pctl |
|----------|------|----|-----------|--------|-----------|
| Size | 7.52 | 1.73 | 6.31 | 7.41 | 8.61 |
| BM | 0.62 | 0.41 | 0.35 | 0.52 | 0.78 |
| Lev | 0.54 | 0.23 | 0.38 | 0.52 | 0.67 |
| ROA | 0.03 | 0.04 | 0.01 | 0.03 | 0.05 |
| RD_Intensity | 0.02 | 0.03 | 0.00 | 0.01 | 0.03 |

#### Market Variable Summary

| Variable | Mean | SD | Min | Max |
|----------|------|----|-----|-----|
| StockRet (%) | 6.12 | 18.80 | -84.10 | +235.78 |
| MarketRet (%) | 3.87 | 5.80 | -23.82 | +47.09 |
| Volatility (%) | 0.38 | 0.15 | 0.12 | 1.24 |

</details>

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-11 | Initial catalog creation from README.md Variable Codebook (132 variables) |

---

**Document Information:**
- **Catalog Version:** 1.0
- **Last Updated:** 2026-02-11
- **Maintained By:** F1D Data Pipeline Documentation
- **Questions or Updates:** See README.md for pipeline context
