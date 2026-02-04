# External Integrations

**Analysis Date:** 2025-02-04

## APIs & External Services

**None detected**

The codebase operates entirely on local files. No REST APIs, web services, or external HTTP calls are present.

**Future-ready infrastructure:**
- `shared/env_validation.py` defines schema for WRDS credentials and API settings
- Environment variables prepared but not yet implemented

## Data Storage

**Databases:**
- None (no SQL, NoSQL, or cloud databases)

**File Storage:**
- Local filesystem only
- Primary format: Apache Parquet (`.parquet` files)
- Secondary: CSV, Excel (`.xlsx`), text files
- Location: `1_Inputs/` for source data, `4_Outputs/` for pipeline results

**File structure:**
```
1_Inputs/
├── CRSPCompustat_CCM/           # Merged CRSP-Compustat linking table
├── CRSP_DSF/                    # CRSP daily stock returns (quarterly parquet)
├── comp_na_daily_all/           # Compustat North America daily
├── tr_ibes/                     # IBES analyst forecasts
├── Execucomp/                   # Executive compensation data
├── SDC/                         # M&A deal data
├── CCCL instrument/             # Instrumental variable data
├── Siccodes12.zip              # Fama-French 12-industry classification
├── Siccodes48.zip              # Fama-French 48-industry classification
├── speaker_data_*.parquet      # Earnings call transcripts (2002-2018)
└── Loughran-McDonald_*.csv     # Linguistic dictionary
```

**Caching:**
- None beyond OS file system cache
- Pytest caches pip dependencies in CI (GitHub Actions)

## Authentication & Identity

**Auth Provider:**
- None (no external authentication)

**Implementation:**
- All scripts run as local user
- No credentials, tokens, or API keys required
- `shared/env_validation.py` prepared for future WRDS credentials but not currently used

## Monitoring & Observability

**Error Tracking:**
- None (no Sentry, Rollbar, or external error tracking)

**Logs:**
- Local file logging to `3_Logs/` directory
- Dual-writer pattern: `shared.observability_utils.DualWriter` mirrors stdout to log files
- Log format: `%(asctime)s [%(levelname)s] %(message)s`
- Timestamped log files matching script output directories

**Memory monitoring:**
- `psutil` usage in `shared.chunked_reader.py` for memory-aware processing
- Configurable memory throttling via `config/project.yaml`

**Test reporting:**
- pytest coverage reports (XML, HTML, terminal)
- GitHub Actions uploads test artifacts (retention: 30 days)

## CI/CD & Deployment

**Hosting:**
- GitHub (source code repository only)

**CI Pipeline:**
- GitHub Actions (`.github/workflows/test.yml`)
- Matrix testing: Python 3.8, 3.9, 3.10, 3.11, 3.12, 3.13
- Separate E2E job on Python 3.10 with 30-minute timeout
- Coverage uploaded to Codecov (optional, non-blocking)

**Deployment:**
- None (research pipeline, not deployed application)

## Environment Configuration

**Required env vars:**
- None currently

**Prepared for future use:**
- `WRDS_USERNAME` - WRDS username (schema defined, not required)
- `WRDS_PASSWORD` - WRDS password (schema defined, not required, should use keyring)
- `API_TIMEOUT_SECONDS` - API request timeout (default: 30)
- `MAX_RETRIES` - Retry attempts for failed requests (default: 3)

**Secrets location:**
- No secrets currently used
- Infrastructure in place for future .env file support

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

**External data sources (manual download):**
The pipeline expects locally downloaded data files from:
- WRDS (CRSP, Compustat, IBES, Execucomp) - downloaded manually
- Loughran-McDonald - downloaded from academic source
- Fama-French industry codes - downloaded from academic source
- CCCL instrument data - provided by researchers

---

*Integration audit: 2025-02-04*
