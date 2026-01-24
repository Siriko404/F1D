# External Integrations

**Analysis Date:** 2026-01-24

## APIs & External Services

**None detected**

The pipeline operates entirely on local files and does not integrate with any external APIs or web services.

- No HTTP requests to external services
- No webhooks or callbacks
- No API keys or authentication tokens required

## Data Storage

**Databases:**
- None (no external database connections)

**Local Data Files:**
All data stored locally in `1_Inputs/` directory:
- **Earnings Call Data:**
  - `Unified-info.parquet` (55 MB) - Call metadata
  - `speaker_data_2002.parquet` through `speaker_data_2018.parquet` (2.5 GB total) - Transcript data
  - `managerial_roles_extracted.txt` - Role definitions

- **Text Processing Resources:**
  - `Loughran-McDonald_MasterDictionary_1993-2024.csv` (9 MB) - Financial sentiment dictionary
  - Format: CSV (text file)

- **Financial Data:**
  - `CRSPCompustat_CCM/` - Linking table (GVKEY-PERMNO)
  - `CRSP_DSF/` - Daily stock returns
  - `comp_na_daily_all/` - Compustat North America daily
  - `tr_ibes/` - IBES analyst forecasts
  - `Execucomp/` - Executive compensation data
  - Format: Parquet files

- **Event Data:**
  - `SDC/` - M&A deal data (Thomson Reuters SDC database files)
  - `CEO Dismissal Data 2021.02.03.xlsx` - Excel file
  - Format: Proprietary data files, Excel

- **Reference Data:**
  - `Siccodes12.zip`, `Siccodes48.zip` - Industry classification codes
  - `CCCL instrument/instrument_shift_intensity_2005_2022.parquet` - Instrumental variable data
  - `master_variable_definitions.csv` - Variable definitions

**File Storage:**
- **Primary:** Local filesystem
- **Format:** Parquet (columnar), CSV, Excel, ZIP
- **Client:** pandas.read_parquet() (PyArrow engine), pandas.read_csv(), pandas.read_excel()

**Caching:**
- None (no external caching services)
- Local file caching via Parquet format

## Authentication & Identity

**Auth Provider:**
- None (no authentication required)

**Implementation:**
- No user accounts or identity management
- No third-party auth (OAuth, SSO, etc.)
- All data access is local file-based

## Monitoring & Observability

**Error Tracking:**
- None (no external error tracking services)

**Logs:**
- **Approach:** Local file logging to `3_Logs/` directory
- **Format:** Plain text logs with timestamps
- **Implementation:** DualWriter class in `2_Scripts/shared/observability_utils.py`
  - Writes same output to stdout and log file
  - No remote logging or aggregation

**System Monitoring:**
- psutil 7.2.1 for local memory/CPU tracking
- Logged to console and log files
- No external monitoring dashboards or APM tools

## CI/CD & Deployment

**Hosting:**
- GitHub (version control and issue tracking)
- No production hosting required (local execution pipeline)

**CI Pipeline:**
- **Service:** GitHub Actions (`.github/workflows/test.yml`)
- **Trigger:** Push to main/master branches, pull requests
- **Matrix Testing:** Python 3.8, 3.9, 3.10, 3.11, 3.12, 3.13
- **Test Types:**
  - Unit and integration tests (pytest, skip E2E)
  - E2E tests (separate job, Python 3.10 only)
- **Coverage:**
  - pytest-cov for coverage reports
  - Optional Codecov upload (fail_on_error: false)
  - Coverage artifacts uploaded as GitHub artifacts
- **Timeout:** 30 minutes for E2E tests

**Deployment:**
- None (local execution only)
- No Docker containers
- No cloud platforms (AWS, GCP, Azure)

## Environment Configuration

**Required env vars:**
- None for basic operation

**Optional env vars:**
- None detected

**Secrets location:**
- No secrets required
- No .env files
- No secret management (no external secrets vaults)
- All data is local files in `1_Inputs/`

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

## Third-Party Data Sources

**Commercial Data Providers:**
- **Capital IQ** - Earnings call transcripts (source data in `1_Inputs/`)
  - Format: Local Parquet files (pre-downloaded)
  - No API integration (offline processing)
- **CRSP** - Stock return data (source data in `1_Inputs/`)
  - Format: Local Parquet files (pre-downloaded)
  - No API integration
- **Compustat** - Financial statement data (source data in `1_Inputs/`)
  - Format: Local Parquet files (pre-downloaded)
  - No API integration
- **IBES** - Analyst forecasts (source data in `1_Inputs/`)
  - Format: Local files (pre-downloaded)
  - No API integration
- **Execucomp** - Executive compensation data (source data in `1_Inputs/`)
  - Format: Local files (pre-downloaded)
  - No API integration
- **Thomson Reuters SDC** - M&A deal data (source data in `1_Inputs/SDC/`)
  - Format: Proprietary database files (pre-downloaded)
  - No API integration

**Note:** All commercial data sources are provided as pre-downloaded local files. No live API connections to data providers.

## Build Dependencies

**External Compilers:**
- g++ (GNU C++ compiler) or compatible
  - Used for compiling C++ tokenization utilities
  - Configured in `config/project.yaml` (step_03.compiler)
  - Flags: -std=c++17 -O2 -Wall -Wextra
  - Required for: Step 3 text processing (2.1_TokenizeAndCount.py)

---

*Integration audit: 2026-01-24*
