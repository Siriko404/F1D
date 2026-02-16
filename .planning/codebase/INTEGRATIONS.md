# External Integrations

**Analysis Date:** 2026-02-15

## APIs & External Services

**Code Analysis Services:**
- GitHub Actions - CI/CD pipeline for testing and linting
  - Location: `.github/workflows/ci.yml`, `.github/workflows/test.yml`
  - Features: Multi-version Python testing, coverage reporting, type checking
  - Token: `CODECOV_TOKEN` (for Codecov integration)

- Codecov - Coverage reporting
  - Uploads coverage reports from CI runs
  - Token: `CODECOV_TOKEN` stored in GitHub secrets

## Data Storage

**Local Filesystem (Primary):**
- Parquet files - Columnar data format for all pipeline I/O
  - Location: `1_Inputs/` (input data), `4_Outputs/` (output data)
  - Client: `pyarrow.parquet` via pandas read_parquet/to_parquet

**Input Data Sources:**
- Earnings call transcripts: `1_Inputs/Earnings_Calls_Transcripts/`
  - Files: `Unified-info.parquet`, `speaker_data_{year}.parquet`
- Loughran-McDonald dictionary: `1_Inputs/LM_dictionary/`
  - File: `Loughran-McDonald_MasterDictionary_1993-2024.csv`
- CRSP data: `1_Inputs/CRSP_DSF/`
  - Files: `CRSP_DSF_{year}_Q{Q}.parquet` (daily stock returns)
- Compustat/CCM: `1_Inputs/CRSPCompustat_CCM/`
  - Linking table for CRSP-Compustat merger
- SDC M&A data: `1_Inputs/SDC/`
  - File: `sdc-ma-merged.parquet`
- Execucomp: `1_Inputs/Execucomp/`
  - Executive compensation data
- SEC Edgar Letters: `1_Inputs/SEC_Edgar_Letters/`
  - Files: `letters_{year}_Q{Q}.parquet`
- I/B/E/S: `1_Inputs/tr_ibes/`
  - Analyst forecast data

**File Storage:**
- Local filesystem only - No cloud storage (S3, GCS, Azure)
- Configuration-based path management via `config/project.yaml`

**Caching:**
- None - No external caching services (Redis, Memcached)

## Authentication & Identity

**Auth Provider:**
- None - No authentication required (local pipeline execution)

**Implementation:**
- Scripts run with local file system permissions
- No user authentication or authorization layers

## Monitoring & Observability

**Error Tracking:**
- None - No external error tracking (Sentry, Rollbar)

**Logs:**
- Structured logging via structlog
- Dual output: Human-readable console + JSON file
- Location: `3_Logs/` directory
- Configuration: `src/f1d/shared/logging/handlers.py`
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

## CI/CD & Deployment

**Hosting:**
- None - Desktop/laptop execution only
- No cloud deployment targets (AWS, GCP, Azure)

**CI Pipeline:**
- GitHub Actions (`.github/workflows/ci.yml`)
  - Lint job: Ruff (linting + formatting), mypy (type checking)
  - Test job: Multi-version Python (3.9-3.13), tiered coverage testing
  - E2E job: End-to-end pipeline tests
  - Coverage upload: Codecov integration

**Pre-commit Hooks:**
- `.pre-commit-config.yaml` defines local hooks
- Ruff (linting + formatting)
- mypy (type checking on shared modules)
- File quality checks (whitespace, YAML/TOML validation, large file detection)

## Environment Configuration

**Required env vars:**
- `F1D_API_TIMEOUT_SECONDS` - API timeout (default: 30)
- `F1D_MAX_RETRIES` - Maximum retry attempts (default: 3)
- `CODECOV_TOKEN` - Codecov authentication (GitHub secret, CI only)

**Secrets location:**
- No secrets required for pipeline execution
- `.env.example` provides template for optional API settings
- No credential files or secret storage services

## Webhooks & Callbacks

**Incoming:**
- None - No webhook endpoints

**Outgoing:**
- None - No external API calls or webhooks

---

*Integration audit: 2026-02-15*
