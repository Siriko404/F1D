# External Integrations

**Analysis Date:** 2026-01-29

## APIs & External Services

**None detected** - No external API calls in codebase.

**Search Results:**
- No imports of requests, http, urllib, boto3, aws, azure, google, openai, anthropic, stripe, twilio, sendgrid, or slack
- Pipeline is fully self-contained

## Data Storage

**Databases:**
- No database servers (PostgreSQL, MySQL, MongoDB, etc.)
- No ORM or database clients

**File Storage:**
- Local filesystem only
- Parquet files (via PyArrow engine)
- CSV files for reports
- No cloud storage (S3, GCS, Azure Blob)

**Data Locations:**
- Inputs: `1_Inputs/` (Earnings call transcripts, financial data, reference files)
- Outputs: `4_Outputs/` (Timestamped directories with `latest/` symlinks)
- Logs: `3_Logs/` (Plain text + optional JSONL)

**Caching:**
- In-memory LRU caching via `@lru_cache` decorator (Python stdlib)
- No external cache (Redis, Memcached)

## Authentication & Identity

**Auth Provider:**
- None - No authentication required

**Implementation:**
- No user accounts or roles
- No OAuth, JWT, or session management
- Scripts run with local filesystem permissions

## Monitoring & Observability

**Error Tracking:**
- None (no Sentry, Rollbar, etc.)
- Custom error logging to text files in `3_Logs/`

**Logs:**
- Dual-writer pattern: stdout + log file (`shared/dual_writer.py`)
- Plain text logs with timestamps
- Optional JSONL structured logs
- No log aggregation (ELK, Splunk, Datadog)

**Metrics:**
- psutil for system metrics (CPU, memory, disk)
- Custom stats tracking via `shared/observability_utils.py`
- File checksums (SHA256) for data validation
- No external metrics (Prometheus, CloudWatch)

## CI/CD & Deployment

**Hosting:**
- None - Local execution only
- No web hosting or deployment targets

**CI Pipeline:**
- GitHub Actions (`.github/workflows/test.yml`)
- Test matrix: Python 3.8, 3.9, 3.10, 3.11, 3.12, 3.13
- Steps:
  - Install dependencies from requirements.txt
  - Run pytest (unit + integration tests)
  - Coverage reporting (pytest-cov)
  - Upload coverage artifacts (optional)
- E2E tests run separately (Python 3.10 only, 20-min timeout)

**Deployment:**
- No automated deployment
- No Docker, Kubernetes, or serverless functions
- Scripts run directly: `python 2_Scripts/<step>/<script>.py`

## Environment Configuration

**Required env vars:**
- None (all config in `config/project.yaml`)

**Secrets location:**
- No secrets (no API keys, credentials, tokens)
- No .env files, no vault integration

**Configuration:**
- `config/project.yaml` - Single source of truth
- Settings: paths, date ranges, thresholds, regression parameters
- No environment-specific configs (dev/staging/prod)

## Webhooks & Callbacks

**Incoming:**
- None (no web server or API endpoints)

**Outgoing:**
- None (no HTTP requests to external services)

**Data Sources:**
- Static files in `1_Inputs/`:
  - Earnings calls: Unified-info.parquet, speaker_data_*.parquet
  - Financial data: CRSP_DSF/, comp_na_daily_all/, CRSPCompustat_CCM/
  - Event data: SDC/ (M&A deals)
  - Reference: Loughran-McDonald dictionary, SIC codes, Execucomp

**Data Sinks:**
- Local filesystem only:
  - `4_Outputs/<step>/TIMESTAMP/` - Timestamped outputs
  - `4_Outputs/<step>/latest/` - Symlink to latest run
  - `3_Logs/<step>/TIMESTAMP.log` - Execution logs

## Third-Party Data Providers

**Financial Data (historical, static files):**
- CRSP/Compustat - Stock returns, fundamentals (via Parquet files)
- IBES - Analyst forecasts (tr_ibes/)
- Execucomp - Executive compensation
- SDC - M&A deal data
- Loughran-McDonald - Financial sentiment dictionary

**Note:** All data accessed as local files. No live market data feeds or API connections.

---

*Integration audit: 2026-01-29*
