# External Integrations

**Analysis Date:** 2026-01-22

## APIs & External Services

**None Detected:**
- No external API calls detected in codebase
- No HTTP/HTTPS network requests
- All processing is local file-based

## Data Storage

**Databases:**
- None (file-based storage only)

**File Storage:**
- Local filesystem in `1_Inputs/` directory
- Data formats: Parquet (`.parquet`), CSV (`.csv`), Excel (`.xlsx`)
- Output storage: Timestamped directories in `4_Outputs/`

**Caching:**
- None (direct file reads)

## Authentication & Identity

**Auth Provider:**
- None required (local data processing only)

## Monitoring & Observability

**Error Tracking:**
- None (manual log file review in `3_Logs/`)

**Logs:**
- Approach: Custom dual-write logger (stdout + file) in each script
- Location: `3_Logs/{step_name}/{timestamp}.log`
- Format: Plain text with optional sibling `.jsonl`
- No centralized logging service

## CI/CD & Deployment

**Hosting:**
- None (local execution only)

**CI Pipeline:**
- None (manual script execution)
- No GitHub Actions, GitLab CI, or other automation

## Environment Configuration

**Required env vars:**
- None (configuration via `config/project.yaml`)

**Secrets location:**
- No secrets required (all data is local files)
- No API keys or credentials

## Webhooks & Callbacks

**Incoming:**
- None (no webhook endpoints)

**Outgoing:**
- None (no external service notifications)

## Data Source Integrations

**WRDS Datasets (Downloaded & Local):**
The pipeline integrates with multiple financial data sources from Wharton Research Data Services (WRDS), but all data is downloaded and stored locally:

- **EventStudy** (`1_Inputs/Unified-info.parquet`, `1_Inputs/speaker_data_YYYY.parquet`)
  - Purpose: Earnings call transcripts 2002-2018
  - Access: Institutional subscription (downloaded locally)
  - No live API connection

- **Loughran-McDonald** (`1_Inputs/Loughran-McDonald_MasterDictionary_1993-2024.csv`)
  - Purpose: Financial sentiment dictionary
  - Source: Public GitHub repository
  - No authentication required

- **CRSP-Compustat CCM** (`1_Inputs/CRSPCompustat_CCM/CRSPCompustat_CCM.parquet`)
  - Purpose: GVKEY-PERMNO linkage, quarterly fundamentals
  - Access: WRDS subscription (downloaded locally)

- **CRSP DSF** (`1_Inputs/CRSP_DSF/CRSP_DSF_*.parquet`)
  - Purpose: Daily stock returns and prices
  - Access: WRDS subscription (downloaded locally)

- **Compustat North America Daily** (`1_Inputs/comp_na_daily_all/comp_na_daily_all.parquet`)
  - Purpose: Daily fundamental data
  - Access: WRDS subscription (downloaded locally)

- **IBES** (`1_Inputs/tr_ibes/`)
  - Purpose: Analyst forecasts and actuals
  - Access: WRDS subscription (downloaded locally)

- **Execucomp** (`1_Inputs/Execucomp/comp_execucomp.parquet`)
  - Purpose: Executive compensation data
  - Access: WRDS subscription (downloaded locally)

- **SDC Platinum** (`1_Inputs/SDC/sdc-ma-merged.parquet`)
  - Purpose: Merger and acquisition data
  - Access: WRDS subscription (downloaded locally)

- **CCCL Instrument** (`1_Inputs/CCCL instrument/instrument_shift_intensity_2005_2022.parquet`)
  - Purpose: Industry-level competition shift intensity
  - Source: Provided by data provider
  - No authentication required

**Integration Pattern:**
All WRDS data is downloaded manually and stored locally. The pipeline reads from these static files using pandas/pyarrow. No live database connections or API calls.

---

*Integration audit: 2026-01-22*
