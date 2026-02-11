# External Integrations

**Analysis Date:** 2025-02-10

## APIs & External Services

**None** - This is a local data processing pipeline with no external API calls.

**Notes:**
- No HTTP/HTTPS requests to external services
- No webhook integrations
- No cloud API dependencies (AWS, Azure, GCP)
- `2_Scripts/shared/env_validation.py` includes placeholders for future API integrations:
  - `API_TIMEOUT_SECONDS`
  - `API_MAX_RETRIES`
  - Currently unused (prepared for future expansion)

## Data Storage

**Databases:**
- None (file-based only)

**File Storage:**
- Local filesystem only (Parquet, CSV, Excel)
- Primary format: Apache Parquet (via pyarrow)
  - Columnar storage for efficient reads
  - Column pruning in 13 critical scripts (30-50% memory reduction)
- Secondary formats: CSV, Excel (openpyxl), JSON (metadata)

**Data Sources (Input Files):**
All data comes from local files in `1_Inputs/`:

**Earnings Call Transcripts:**
- `1_Inputs/Earnings_Calls_Transcripts/`
  - `speaker_data_2002.parquet` through `speaker_data_2018.parquet`
  - ~50K transcripts, ~2.5GB total
  - Source: External vendor (not accessed via API)

**Financial Market Data:**
- `1_Inputs/CRSP_DSF/` - CRSP Daily Stock Returns
  - Quarterly parquet files: `CRSP_DSF_YYYY_Q*.parquet`
  - 1999-2022 coverage
  - Source: CRSP (via WRDS, downloaded as files)

- `1_Inputs/CRSPCompustat_CCM/` - CRSP/Compustat Merged
  - Linking table (GVKEY-PERMNO mapping)
  - Source: WRDS (downloaded as files)

- `1_Inputs/comp_na_daily_all/` - Compustat North America
  - Daily fundamental data
  - Source: Compustat via WRDS

- `1_Inputs/tr_ibes/` - IBES Analyst Forecasts
  - `tr_ibes.parquet`
  - Source: IBES via WRDS

**Executive Data:**
- `1_Inputs/Execucomp/` - Executive compensation
- Source: Execucomp via WRDS

**Event Data:**
- `1_Inputs/SDC/` - M&A deal data
- `CEO Dismissal Data 2021.02.03.xlsx`
- Source: SDC Platinum

**Reference Data:**
- `1_Inputs/LM_dictionary/` - Loughran-McDonald Master Dictionary
  - `Loughran-McDonald_MasterDictionary_1993-2024.csv` (9MB)
  - Source: https://www.nd.edu/~mcdonald/Word_Lists.html

- `1_Inputs/CCCL_instrument/` - Instrumental variable for liquidity analysis
  - `instrument_shift_intensity_2005_2022.parquet`

- `1_Inputs/FF1248/` - Fama-French factors
- `1_Inputs/Siccodes12.zip`, `Siccodes48.zip` - Industry classification

**Caching:**
- None (no caching layer)

## Authentication & Identity

**Auth Provider:**
- None (no authentication required)

**Implementation:**
- All data accessed via local file paths
- No WRDS API credentials in code (data pre-downloaded)
- No OAuth, API keys, or tokens

## Monitoring & Observability

**Error Tracking:**
- None (no Sentry, Bugsnag, or similar services)
- Error handling via try/except blocks in scripts
- Logging to console and file (`3_Logs/`)

**Logs:**
- File-based logging in `3_Logs/`
- Dual logging pattern:
  - Console output via `shared/observability_utils.py > DualWriter`
  - File logs with timestamps
- Log format: `%(asctime)s [%(levelname)s] %(message)s`
- Memory tracking via `psutil` (start/end/peak/delta)
- Processing duration tracking in `stats.json` outputs

**No:**
- Centralized logging (ELK, Splunk)
- APM (Datadog, New Relic)
- Distributed tracing

## CI/CD & Deployment

**Hosting:**
- None (local execution only)
- No Docker, Kubernetes, or cloud deployment

**CI Pipeline:**
- GitHub Actions (`.github/workflows/test.yml`)
  - Triggers: Push/PR to main/master branches
  - Matrix testing: Python 3.8, 3.9, 3.10, 3.11, 3.12, 3.13
  - Jobs:
    - `test` - Unit and integration tests (skip E2E)
    - `e2e-test` - End-to-end pipeline tests (Python 3.10 only)
  - Coverage upload to Codecov (optional, soft-fail)
  - Artifact retention: 30 days
  - Timeout: 30 minutes for E2E tests

**Test commands:**
```bash
pytest tests/ -m "not e2e" --cov=2_Scripts --cov-report=xml
pytest tests/ -m e2e -v --timeout=1200
```

## Environment Configuration

**Required env vars:**
- None (no environment variables required)

**Secrets location:**
- No secrets used
- `shared/env_validation.py` validates environment but all vars optional
- Future-proofed for API keys (see `API_TIMEOUT_SECONDS` placeholder)

**WRDS Credentials:**
- Not stored in codebase
- Data pre-downloaded from WRDS and committed as Parquet files
- No live WRDS API calls

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

## Data Pipeline Architecture

**ETL Pattern:**
- Batch processing (not streaming)
- Local file I/O (no database connections)
- Deterministic processing (fixed random seed: 42)

**Key Integration Points:**

**Entity Linking (`2_Scripts/1_Sample/1.2_LinkEntities.py`):**
- 4-tier strategy for matching calls to firms:
  - Tier 1: PERMNO + exact date match (CRSP)
  - Tier 2: CUSIP8 + date match
  - Tier 3: Fuzzy match via RapidFuzz (optional, >=92% similarity)
  - Tier 4: Company name matching (token_sort_ratio, WRatio)
- Links to CCM database (`1_Inputs/CRSPCompustat_CCM/`)

**Text Processing (`2_Scripts/2_Text/2.1_TokenizeAndCount.py`):**
- Loughran-McDonald dictionary lookups
- sklearn.feature_extraction.text.CountVectorizer
- No external NLP APIs (all local)

**Econometric Analysis:**
- statsmodels for OLS, fixed effects, IV regression
- No external statistical services
- Results written to local files (TXT, CSV, Parquet)

## Scaling Considerations

**Current limits:**
- ~50K transcripts, ~25M rows
- Single-machine processing (no distributed computing)

**Future scaling paths:**
- Path A (2x): Enable parallel processing (`thread_count=4`)
- Path B (10x): Throttling, column pruning, PyArrow Dataset API
- Path C (100x): Requires Dask/Ray or database migration
- See `SCALING.md` for detailed scaling strategies

---

*Integration audit: 2025-02-10*
