# External Integrations

**Analysis Date:** 2026-02-15

## APIs & External Services

**None detected** - This is a local data processing pipeline with no external API calls or cloud service integrations.

## Data Storage

**Databases:**
- None (file-based data storage)

**File Storage:**
- Local filesystem only
- Parquet files (`.parquet`) - Primary data format via PyArrow
- CSV files (`.csv`) - Reference data and outputs
- Excel files (`.xlsx`) - Limited use (openpyxl installed but not actively used)
- YAML files (`.yaml`) - Configuration files

**Data Sources (Local Files):**
- `inputs/Earnings_Calls_Transcripts/` - Earnings call transcript data
- `inputs/LM_dictionary/` - Loughran-McDonald dictionary for text analysis
- `inputs/CRSPCompustat_CCM/` - CRSP-Compustat linking table
- `inputs/CRSP_DSF/` - Daily stock returns
- `inputs/comp_na_daily_all/` - Compustat North America daily data
- `inputs/tr_ibes/` - IBES analyst forecasts
- `inputs/Execucomp/` - Executive compensation data
- `inputs/SDC/` - M&A deal data
- `inputs/CCCL_instrument/` - Instrumental variable data
- `inputs/FirmLevelRisk/` - Firm-level risk measures
- `inputs/FF1248/` - Fama-French factors
- `inputs/Siccodes12.zip`, `Siccodes48.zip` - Industry classification codes
- `inputs/SEC_Edgar_Letters/` - SEC EDGAR correspondence

**Caching:**
- None (no caching layer implemented)

## Authentication & Identity

**Auth Provider:**
- Custom (none required)
- No authentication or identity services needed (local processing only)

## Monitoring & Observability

**Error Tracking:**
- None (no external error tracking service)

**Logs:**
- structlog for structured logging
- Log files written to `logs/` directory
- Console output with JSON format option
- Log level configurable via `config/project.yaml` or pydantic-settings

**Observability Utilities:**
- `src/f1d/shared/observability_utils.py` - Memory tracking, CPU monitoring
- `src/f1d/shared/diagnostics.py` - Diagnostics utilities
- `src/f1d/shared/logging/` - Structured logging configuration

## CI/CD & Deployment

**Hosting:**
- None (local execution pipeline)
- GitHub Actions for CI/CD testing only (not for hosting)

**CI Pipeline:**
- GitHub Actions
  - Primary workflow: `.github/workflows/ci.yml` - Linting and testing
  - Extended workflow: `.github/workflows/test.yml` - Extended testing, security scanning, E2E tests
  - Security scanning: Bandit SAST (medium severity)
  - Linting: Ruff (linting and formatting)
  - Type checking: mypy (Tier 1 modules only)
  - Testing: pytest with coverage (pytest-cov)
  - Coverage reporting: Codecov integration
  - Matrix testing: Python 3.9, 3.10, 3.11, 3.12, 3.13
  - E2E tests: Run on main branch pushes only

**Dependency Management:**
- Dependabot for automated dependency updates (`.github/dependabot.yml`)
  - Weekly Python dependency checks
  - Monthly GitHub Actions updates
  - Grouped updates for dev and production dependencies

**Pre-commit Hooks:**
- Pre-commit CI configured (`.pre-commit-config.yaml`)
  - Ruff (linting and formatting)
  - mypy (type checking on `src/f1d/shared`)
  - General file quality checks (trailing whitespace, YAML validation, etc.)
  - Security checks (detect-private-key, debug-statements)

## Environment Configuration

**Required env vars:**
- `F1D_API_TIMEOUT_SECONDS` - API timeout setting (default: 30)
- `F1D_MAX_RETRIES` - Maximum retries (default: 3)

**Secrets location:**
- None (no secrets required for pipeline operation)
- `.env.example` provided as template (no sensitive values)

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

## Statistical Libraries

**Econometric Analysis:**
- statsmodels 0.14.6 - Used in `src/f1d/shared/panel_ols.py`, `src/f1d/shared/iv_regression.py`, and all econometric scripts
- linearmodels - Used in panel regression scripts (`src/f1d/econometric/v1/`, `src/f1d/econometric/v2/`)
- lifelines 0.30.0 - Used for survival analysis in `src/f1d/econometric/v1/4.3_TakeoverHazards.py`

**Text Processing:**
- rapidfuzz >=3.14.0 (optional) - Fuzzy string matching in `src/f1d/shared/string_matching.py` and `src/f1d/sample/1.2_LinkEntities.py`
  - Graceful degradation: Pipeline runs without it (falls back to exact matching)
  - Improves entity match rates when installed

---

*Integration audit: 2026-02-15*
