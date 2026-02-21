# External Integrations

**Analysis Date:** 2026-02-20

## APIs & External Services

**None Detected**

This is a local data processing pipeline with no external API integrations:
- No HTTP client imports (requests, urllib, httpx, aiohttp)
- No cloud SDK imports (boto3, google-cloud, azure)
- No external service calls

All data is loaded from local files in the `inputs/` directory.

## Data Storage

**Databases:**
- None - File-based storage only

**File Storage:**
- Local filesystem only
- Primary format: Parquet (`.parquet` files)
- Secondary formats: CSV, Excel (`.xlsx`)
- Data directory: `inputs/`
- Output directory: `outputs/`

**Input Data Sources (Pre-loaded Local Files):**
- `inputs/comp_na_daily_all/` - Compustat financial data
- `inputs/CRSP_DSF/` - CRSP daily stock files (year-quarter partitioned)
- `inputs/tr_ibes/` - IBES EPS forecasts
- `inputs/CRSPCompustat_CCM/` - CCM linktable (CRSP-Compustat merge)
- `inputs/Earnings_Calls_Transcripts/` - Earnings call transcripts
- `inputs/FF1248/` - Fama-French industry classifications
- `inputs/LM_dictionary/` - Loughran-McDonald sentiment dictionary
- `inputs/CCCL_instrument/` - CCCL instrument data
- `inputs/SDC/` - SDC Platinum M&A data
- `inputs/Execucomp/` - Executive compensation data
- `inputs/FirmLevelRisk/` - Firm-level risk measures
- `inputs/SEC_Edgar_Letters/` - SEC EDGAR correspondence
- `inputs/Manager_roles/` - Manager role classifications

**Caching:**
- None - Each run reads from source files
- Optional: Module-level singleton pattern for expensive data loads
  - `_compustat_engine.py` - Caches Compustat data per session
  - `_crsp_engine.py` - Caches CRSP data per session
  - `_ibes_engine.py` - Caches IBES data per session

## Authentication & Identity

**Auth Provider:**
- None - No authentication required

**Access Control:**
- Local file system permissions only
- No user management

## Monitoring & Observability

**Logging:**
- structlog for structured logging
- Console and file output
- Context variables for operation tracking
- Config: `src/f1d/shared/logging/`

**Log Location:**
- `logs/` directory
- Format: JSON (production), colored console (development)

**Error Tracking:**
- None - Local execution only

**Performance Monitoring:**
- Built-in memory monitoring via psutil
- Chunk processing with memory throttling
- `src/f1d/shared/observability/memory.py`

**Throughput Tracking:**
- `src/f1d/shared/observability/throughput.py`
- `src/f1d/shared/observability/stats.py`

## CI/CD & Deployment

**Hosting:**
- None - Local research pipeline

**CI Pipeline:**
- GitHub Actions
- Workflow: `.github/workflows/ci.yml`
- Triggers: push/PR to main/master

**CI Jobs:**
1. **Lint**: ruff (lint + format check), mypy (Tier 1 modules)
2. **Test**: Multi-version Python matrix (3.9-3.13)
   - Tier 1 tests: unit tests with 10% coverage threshold
   - Tier 2 tests: integration tests with 10% threshold
   - Full suite: 40% coverage threshold
3. **E2E Tests**: On main branch push only

**Coverage Reporting:**
- Codecov integration (optional token)
- Coverage artifacts uploaded to GitHub

**Pre-commit Hooks:**
- Config: `.pre-commit-config.yaml`
- Hooks: trailing-whitespace, end-of-file-fixer, check-yaml, check-toml
- Ruff (lint + format), mypy (Tier 1 modules)

## Environment Configuration

**Required env vars:**
- None strictly required (all have defaults)

**Optional env vars:**
- `F1D_API_TIMEOUT_SECONDS` - Default: 30
- `F1D_MAX_RETRIES` - Default: 3

**Environment validation:**
- `src/f1d/shared/env_validation.py`
- Schema-based validation with type checking

**Secrets location:**
- None - No secrets required
- `.env.example` provided as template

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

## External Data Dependencies

**Third-Party Data Sources (Pre-downloaded):**
These datasets must be present in `inputs/` before running the pipeline:

| Dataset | Source | Purpose |
|---------|--------|---------|
| Compustat | WRDS | Financial statements |
| CRSP | WRDS | Stock prices and returns |
| IBES | WRDS | Analyst forecasts |
| CCM Linktable | WRDS | CRSP-Compustat merge |
| Earnings Calls | Provider | Transcripts (text analysis) |
| Loughran-McDonald | Web | Sentiment dictionary |
| Fama-French | Web | Industry classifications |
| CCCL Instrument | Research | Instrument for IV regression |

**Data Update Frequency:**
- Static dataset (research project)
- No automated data refresh

## Integration Architecture

```
inputs/               # Pre-loaded data (no API calls)
    ├── comp_na_daily_all/     # Compustat (local parquet)
    ├── CRSP_DSF/              # CRSP daily (local parquet)
    ├── tr_ibes/               # IBES forecasts (local parquet)
    └── ...

src/f1d/
    ├── shared/
    │   ├── variables/
    │   │   ├── _compustat_engine.py  # Singleton cache
    │   │   ├── _crsp_engine.py       # Singleton cache
    │   │   └── _ibes_engine.py       # Singleton cache
    │   └── ...
    └── ...

outputs/              # Generated results (local parquet)
```

**Key Pattern - Private Engine Singletons:**
- Expensive data loads cached at module level
- `_engine.py` files expose `get_engine()` function
- Panel builders call once; all variable builders share cache
- Compustat, CRSP, IBES each loaded once per session

---

*Integration audit: 2026-02-20*
