# Raw Data Sources

**IMPORTANT: This directory contains IMMUTABLE source data. NEVER modify or delete files here.**

This directory follows the Cookiecutter Data Science convention for raw data storage.
All files here are the original source data and should never be modified.

---

## Data Sources

### Earnings Call Transcripts
- **Directory:** `Earnings_Calls_Transcripts/`
- **Source:** Thomson Reuters StreetEvents / Capital IQ
- **Description:** Raw earnings call transcripts for S&P 1500 firms
- **Format:** Parquet
- **Date Range:** 2010-2023

### CRSP Daily Stock File (DSF)
- **Directory:** `CRSP_DSF/`
- **Source:** CRSP (Center for Research in Security Prices)
- **Description:** Daily stock returns, prices, and trading volumes
- **Format:** Parquet
- **Date Range:** 2000-2023

### CRSP-Compustat Merged (CCM)
- **Directory:** `CRSPCompustat_CCM/`
- **Source:** CRSP-Compustat Merged Database
- **Description:** Linked CRSP and Compustat data with PERMCO-GVKEY mapping
- **Format:** Parquet
- **Date Range:** 2000-2023

### Compustat Daily
- **Directory:** `comp_na_daily_all/`
- **Source:** Compustat (S&P Global)
- **Description:** Daily fundamental data (prices, shares outstanding, etc.)
- **Format:** Parquet
- **Date Range:** 2000-2023

### Executive Compensation
- **Directory:** `Execucomp/`
- **Source:** ExecuComp (S&P Global)
- **Description:** Executive compensation data including CEO information
- **Format:** Parquet
- **Date Range:** 2000-2023

### IBES Analyst Forecasts
- **Directory:** `tr_ibes/`
- **Source:** I/B/E/S (Institutional Brokers' Estimate System)
- **Description:** Analyst earnings forecasts and recommendations
- **Format:** Parquet
- **Date Range:** 2000-2023

### Fama-French Factors
- **Directory:** `FF1248/`
- **Source:** Kenneth French Data Library
- **Description:** Fama-French 3-factor, 5-factor, and momentum factors
- **Format:** CSV
- **Date Range:** 2000-2023

### Loughran-McDonald Dictionary
- **Directory:** `LM_dictionary/`
- **Source:** Loughran-McDonald Master Dictionary
- **Description:** Sentiment word lists for financial text analysis
- **Format:** CSV
- **URL:** https://sraf.nd.edu/loughranmcdonald-master-dictionary/

### SEC Edgar Letters
- **Directory:** `SEC_Edgar_Letters/`
- **Source:** SEC EDGAR
- **Description:** SEC comment letters and company responses
- **Format:** Parquet/Text
- **Date Range:** 2000-2023

### CCCL Instrument
- **Directory:** `CCCL_instrument/`
- **Source:** Constructed from SEC correspondence
- **Description:** SEC scrutiny instrument for causal identification
- **Format:** Parquet

### Manager Roles
- **Directory:** `Manager_roles/`
- **Source:** BoardEx / proprietary
- **Description:** Manager role identification data
- **Format:** Parquet

### SDC Platinum M&A Data
- **Directory:** `SDC/`
- **Source:** Refinitiv SDC Platinum
- **Description:** Mergers and acquisitions data
- **Format:** Parquet
- **Date Range:** 2000-2023

### Firm-Level Risk
- **Directory:** `FirmLevelRisk/`
- **Source:** Constructed from CRSP
- **Description:** Firm-level risk measures (volatility, beta, etc.)
- **Format:** Parquet

---

## Mutability Rules

| Rule | Description |
|------|-------------|
| NEVER modify | Files in this directory are immutable |
| NEVER delete | Preserve original data for reproducibility |
| NEVER overwrite | If updating, create a new dated file |
| Document changes | Update this README when adding new data sources |

## Adding New Data

When adding new data sources:

1. Create a subdirectory with descriptive name
2. Add original data files (prefer Parquet format)
3. Document source, date range, format in this README
4. Include download date in filename or metadata

---

**Last Updated:** 2026-02-13
