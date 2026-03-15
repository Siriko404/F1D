# External Integrations

**Analysis Date:** 2026-03-15

## APIs & External Services

**No external API integrations detected.**

This is a self-contained local data processing pipeline. All data is read from local files in `inputs/` and processed locally. The `F1D_API_TIMEOUT_SECONDS` env var in `src/f1d/shared/config/env.py` suggests potential API usage, but no active API client code was found in the codebase.

## Data Storage

**Databases:**
- None - All data stored as local files (no database connections)

**File Storage (Local Filesystem):**
- **Input data:** `inputs/` directory with subdirectories per data source
  - `inputs/Compustat_Annual/` - Compustat annual financial data
  - `inputs/CRSP_DSF/` - CRSP daily stock file
  - `inputs/CRSPCompustat_CCM/` - CRSP-Compustat merged linking table
  - `inputs/Earnings_Calls_Transcripts/` - Earnings call transcripts (Parquet, year-partitioned)
  - `inputs/tr_ibes/` - I/B/E/S analyst forecast data
  - `inputs/Execucomp/` - Executive compensation data
  - `inputs/SDC/` - SDC Platinum M&A/takeover data
  - `inputs/FF1248/` - Fama-French industry classification data
  - `inputs/FirmLevelRisk/` - Hassan et al. firm-level political risk data
  - `inputs/LM_dictionary/` - Loughran-McDonald sentiment dictionary
  - `inputs/Manager_roles/` - Manager role classification data
  - `inputs/CCCL_instrument/` - CCCL instrument shift intensity data
  - `inputs/comp_na_daily_all/` - Compustat North America daily data
  - `inputs/Siccodes12.zip`, `inputs/Siccodes48.zip` - SIC code classification files

- **Output data:** `outputs/` directory with timestamped subdirectories per stage
  - `outputs/1.1_CleanMetadata/` - Stage 1: Cleaned metadata
  - `outputs/1.2_LinkEntities/` - Stage 1: Entity linking results
  - `outputs/1.3_BuildTenureMap/` - Stage 1: CEO tenure maps
  - `outputs/1.4_AssembleManifest/` - Stage 1: Master sample manifest
  - `outputs/2_Textual_Analysis/` - Stage 2: Text processing and linguistic variables
  - `outputs/variables/` - Stage 3: Hypothesis-specific variable panels
  - `outputs/econometric/` - Stage 4: Regression results per hypothesis test

- **File formats:**
  - Primary: Apache Parquet (via pyarrow) for all intermediate and output data
  - Secondary: CSV for audit reports, Excel (.xlsx) for some inputs
  - Configuration: YAML (`config/project.yaml`, `config/variables.yaml`)
  - Results: Plain text (.txt) for regression output, Markdown (.md) for summary reports
  - LaTeX (.tex) for publication-ready tables

**Caching:**
- Configuration caching in `src/f1d/shared/config/loader.py` (in-memory module-level cache)
- No external caching service

## Authentication & Identity

**Auth Provider:**
- None - Local pipeline with no authentication requirements

## Monitoring & Observability

**Error Tracking:**
- Custom observability module at `src/f1d/shared/observability/`
  - `anomalies.py` - Anomaly detection in data
  - `memory.py` - Memory usage monitoring (via psutil)
  - `throughput.py` - Processing throughput tracking
  - `stats.py` - Statistical monitoring
  - `files.py` - File-level observability
  - `logging.py` - Observability logging integration

**Logs:**
- structlog-based structured logging (`src/f1d/shared/logging/`)
  - `config.py` - Logging configuration (JSON or console output)
  - `context.py` - Context binding for structured log entries
  - `handlers.py` - Custom log handlers
- Log output directory: `logs/` (configured in `config/project.yaml`)
- Log level configurable via `config/project.yaml` (default: INFO)

## CI/CD & Deployment

**Hosting:**
- Local development machine (no cloud deployment)

**CI Pipeline:**
- GitHub Actions (`.github/workflows/ci.yml`)
  - **Lint job:** Ruff linting + formatting check, mypy type checking (Tier 1 modules only)
  - **Test job:** Matrix across Python 3.9-3.13
    - Tier 1 tests: `tests/unit/test_panel_ols.py`, `tests/unit/test_iv_regression.py`, `tests/unit/test_data_validation.py`
    - Tier 2 tests: `tests/integration/`, `tests/unit/test_path_utils.py`, `tests/unit/test_chunked_reader.py`
    - Full suite with 40% coverage threshold (excluding e2e)
  - **E2E job:** Runs on push to main only, 1200s timeout
  - Coverage reports uploaded to Codecov (`.github/workflows/ci.yml` line 101-106)

- Pre-commit hooks (`.pre-commit-config.yaml`):
  - File quality checks (whitespace, YAML/TOML/JSON validation, large files, merge conflicts)
  - Security checks (private key detection, debug statements)
  - Ruff linting and formatting
  - mypy type checking on `src/f1d/shared/` only

## Environment Configuration

**Required env vars:**
- None strictly required - pipeline runs with defaults from `config/project.yaml`
- Optional: `F1D_API_TIMEOUT_SECONDS` (default: 30), `F1D_MAX_RETRIES` (default: 3)

**Env file:**
- `.env.example` present in repo root (existence noted only, contents not read)
- `.env` loaded by pydantic-settings with `F1D_` prefix (`src/f1d/shared/config/env.py`)

**Secrets location:**
- No secrets required - all data is local, no external API keys needed
- `CODECOV_TOKEN` stored in GitHub Actions secrets (CI only)

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

## Data Source Provenance

The pipeline processes academic financial datasets that are pre-downloaded locally. Key data sources referenced in variable builders (`src/f1d/shared/variables/`) and configuration (`config/variables.yaml`):

| Source | Directory | Used By |
|--------|-----------|---------|
| WRDS/Compustat | `inputs/Compustat_Annual/` | Financial controls (ROA, leverage, size, etc.) |
| WRDS/CRSP | `inputs/CRSP_DSF/` | Stock returns, volatility, liquidity measures |
| WRDS/CCM | `inputs/CRSPCompustat_CCM/` | CRSP-Compustat linking |
| Thomson Reuters/I/B/E/S | `inputs/tr_ibes/` | Analyst forecasts, dispersion |
| Seeking Alpha | `inputs/Earnings_Calls_Transcripts/` | Earnings call transcripts |
| S&P/Execucomp | `inputs/Execucomp/` | CEO identification and compensation |
| Thomson Reuters/SDC | `inputs/SDC/` | M&A/takeover events |
| Hassan et al. | `inputs/FirmLevelRisk/` | Political risk measures |
| Loughran-McDonald | `inputs/LM_dictionary/` | Sentiment/uncertainty word lists |
| Fama-French | `inputs/FF1248/` | Industry classifications (FF12, FF48) |
| Custom/CCCL | `inputs/CCCL_instrument/` | Instrumental variable for clarity |

---

*Integration audit: 2026-03-15*
