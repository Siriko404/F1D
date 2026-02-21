# External Integrations

**Analysis Date:** 2026-02-21

## APIs & External Services

**No external APIs.** The project processes local data files only.

**API Configuration:**
- `F1D_API_TIMEOUT_SECONDS` - Timeout setting (default 30s)
- `F1D_MAX_RETRIES` - Retry count (default 3)
- These appear to be infrastructure settings for potential future API use

## Data Storage

**Databases:**
- None - All data stored as flat files

**File Storage:**
- Local filesystem only
- Input data in `inputs/` directory
- Output data in `outputs/` directory (timestamped subdirectories)
- Primary format: Parquet files (`.parquet`)
- Secondary formats: CSV, Excel (`.xlsx`)

**Caching:**
- None implemented

## Data Sources (inputs/ directory)

**Financial Data:**
- `inputs/comp_na_daily_all/` - Compustat quarterly data (firm financials)
- `inputs/CRSP_DSF/` - CRSP daily stock file (prices, returns, volume)
- `inputs/CRSPCompustat_CCM/` - CRSP-Compustat Merged (linking table)
- `inputs/tr_ibes/` - Thomson Reuters IBES (analyst forecasts)

**Textual Data:**
- `inputs/Earnings_Calls_Transcripts/` - Earnings call transcripts
  - `Unified-info.parquet` - Call metadata
  - `speaker_data_{year}.parquet` - Speaker-level text
- `inputs/LM_dictionary/` - Loughran-McDonald sentiment dictionary

**M&A Data:**
- `inputs/SDC/` - SDC Platinum M&A data (`sdc-ma-merged.parquet`)
  - Takeover events, dates, attitudes

**Executive Data:**
- `inputs/Execucomp/` - Executive compensation data
- `inputs/Manager_roles/` - Manager role classifications

**Industry/Risk Data:**
- `inputs/FF1248/` - Fama-French 12/48 industry classifications
- `inputs/FirmLevelRisk/` - Policy risk measures (Hassan et al. 2019)
- `inputs/SEC_Edgar_Letters/` - SEC comment letters

**Instrument Data:**
- `inputs/CCCL_instrument/` - Shift-share instrument for IV regression
  - `instrument_shift_intensity_2005_2022.parquet`

## Authentication & Identity

**Auth Provider:**
- None - All data is local

**Access Control:**
- File system permissions only
- No user authentication

## Monitoring & Observability

**Error Tracking:**
- None (local development only)

**Logs:**
- Structured logging via `structlog`
- Dual-writer pattern: logs to both stdout and file
- Log directory: `logs/`
- Log module: `src/f1d/shared/observability/logging.py`
- `DualWriter` class captures all output

**Coverage Reporting:**
- Codecov integration via GitHub Actions
- Coverage reports uploaded as artifacts
- Token: `secrets.CODECOV_TOKEN`

## CI/CD & Deployment

**Hosting:**
- None - Local execution only

**CI Pipeline:**
- GitHub Actions
  - `.github/workflows/ci.yml` - Main CI (lint, test, coverage)
  - `.github/workflows/test.yml` - Extended tests (security scan)
- Python versions tested: 3.9, 3.10, 3.11, 3.12, 3.13
- Coverage thresholds:
  - Tier 1 tests: 10%
  - Tier 2 tests: 10%
  - Full suite: 40%

**Security Scanning:**
- Bandit SAST scanner (runs in CI)
- Configuration: `pyproject.toml` [tool.bandit]

**Dependency Management:**
- Dependabot (weekly for pip, monthly for GitHub Actions)
- Configuration: `.github/dependabot.yml`
- Groups: dev-dependencies, production-dependencies

## Environment Configuration

**Required env vars:**
- None required (all have defaults)

**Optional env vars:**
- `F1D_API_TIMEOUT_SECONDS` - API timeout (default: 30)
- `F1D_MAX_RETRIES` - Retry attempts (default: 3)

**Secrets location:**
- GitHub Actions secrets: `CODECOV_TOKEN`
- No other secrets required

**Configuration files:**
- `config/project.yaml` - Pipeline configuration
- `config/variables.yaml` - Variable source definitions
- `.env` - Local environment (optional, from `.env.example`)

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

## Key Data Flow

```
inputs/                    # External data sources (manual import)
    ├── comp_na_daily_all/ # Compustat
    ├── CRSP_DSF/          # CRSP daily
    ├── tr_ibes/           # IBES analyst forecasts
    ├── SDC/               # M&A events
    └── ...
        │
        ▼
src/f1d/                   # Processing pipeline
    ├── sample/            # Stage 1: Build manifest
    ├── text/              # Stage 2: Tokenize & analyze
    ├── variables/         # Stage 3: Build panels
    └── econometric/       # Stage 4: Run regressions
        │
        ▼
outputs/                   # Processed outputs
    ├── 1.4_AssembleManifest/
    ├── 2_Textual_Analysis/
    ├── 3_Financial_Features/
    └── econometric/
```

---

*Integration audit: 2026-02-21*
