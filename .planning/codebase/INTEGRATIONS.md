# External Integrations

**Analysis Date:** 2026-02-14

## APIs & External Services

**WRDS (Wharton Research Data Services):**
- Purpose: Download financial data (CRSP, Compustat, IBES)
- SDK/Client: Direct API access via `EnvConfig.wrds_username` / `EnvConfig.wrds_password`
- Auth: Environment variables `F1D_WRDS_USERNAME`, `F1D_WRDS_PASSWORD`
- Implementation: `src/f1d/shared/config/env.py` (SecretStr for password protection)
- Status: Optional - pipeline can run with pre-downloaded data

**SEC EDGAR:**
- Purpose: Source of earnings call transcripts and SEC letters
- Data format: Pre-downloaded Parquet files in `1_Inputs/` directories
- No runtime API calls - data is locally stored

## Data Storage

**Databases:**
- None - File-based data pipeline
- All data stored as Parquet files for efficiency

**File Storage:**
- Local filesystem only
- Parquet format (via pyarrow) for large datasets
- CSV for reference data (Loughran-McDonald dictionary)
- Directory structure:
  - `1_Inputs/` - Source data files
  - `4_Outputs/` - Pipeline outputs
  - `3_Logs/` - Execution logs

**Caching:**
- None - Deterministic processing without caching

## Data Sources (Input Files)

**Financial Data:**
- `1_Inputs/CRSP_DSF/` - Daily stock returns (CRSP)
- `1_Inputs/comp_na_daily_all/` - Compustat daily fundamentals
- `1_Inputs/CRSPCompustat_CCM/` - CRSP-Compustat Merged (CCM) linking table
- `1_Inputs/Execucomp/` - Executive compensation data
- `1_Inputs/tr_ibes/` - I/B/E/S analyst forecasts

**Textual Data:**
- `1_Inputs/Earnings_Calls_Transcripts/` - Earnings call transcripts (speaker_data_{year}.parquet)
- `1_Inputs/SEC_Edgar_Letters/` - SEC comment letters
- `1_Inputs/LM_dictionary/` - Loughran-McDonald Master Dictionary (sentiment word lists)

**Reference Data:**
- `1_Inputs/FF1248/` - Fama-French 12/48 industry classifications
- `1_Inputs/Manager_roles/` - Managerial role definitions
- `1_Inputs/SDC/` - SDC M&A transaction data
- `1_Inputs/FirmLevelRisk/` - Firm-level risk measures
- `1_Inputs/CCCL_instrument/` - CCCL instrument for IV regression

## Authentication & Identity

**Auth Provider:**
- None - Local application
- WRDS credentials optional for data download

**Implementation:**
- `src/f1d/shared/config/env.py` - Environment-based configuration
- `pydantic-settings` with SecretStr for sensitive values
- `.env` file for local development (git-ignored)

## Monitoring & Observability

**Error Tracking:**
- None - Local console logging

**Logs:**
- structlog-based structured logging
- JSON format optional for machine parsing
- Context binding for stage/step tracking
- Implementation: `src/f1d/shared/logging/config.py`
- Memory tracking: `src/f1d/shared/observability/memory.py`
- Throughput tracking: `src/f1d/shared/observability/throughput.py`
- Anomaly detection: `src/f1d/shared/observability/anomalies.py`

## CI/CD & Deployment

**Hosting:**
- None - Local data processing pipeline

**CI Pipeline:**
- GitHub Actions (`.github/workflows/ci.yml`)
  - Lint job: ruff linting, ruff format check, mypy type checking
  - Test job: Matrix testing on Python 3.9-3.13
  - E2E job: End-to-end tests on main branch pushes
- Codecov integration for coverage reporting
- Pre-commit hooks for local quality gates

**Coverage Thresholds:**
- Tier 1 tests: 10% (measures all shared modules, tested modules have 70%+)
- Tier 2 tests: 10%
- Overall: 25%

## Environment Configuration

**Required env vars:**
- None required (pipeline runs with defaults)

**Optional env vars:**
- `F1D_WRDS_USERNAME` - WRDS username
- `F1D_WRDS_PASSWORD` - WRDS password (stored as SecretStr)
- `F1D_API_TIMEOUT_SECONDS` - API timeout (default: 30)
- `F1D_MAX_RETRIES` - Max API retries (default: 3)

**Secrets location:**
- `.env` file (git-ignored, template in `.env.example`)
- GitHub Secrets for CI (`CODECOV_TOKEN`)

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

## External Libraries (Optional)

**linearmodels:**
- Purpose: Panel OLS with fixed effects, IV/2SLS regression
- Import pattern: Try/except with graceful degradation
- Implementation: `src/f1d/shared/panel_ols.py`, `src/f1d/shared/iv_regression.py`
- Install: `pip install linearmodels`

**rapidfuzz:**
- Purpose: Fuzzy string matching for entity name linking
- Import pattern: Try/except with warning on missing
- Implementation: `src/f1d/shared/string_matching.py`
- Install: `pip install rapidfuzz>=3.14.0`
- Fallback: Pipeline runs without it (lower match rate)

---

*Integration audit: 2026-02-14*
