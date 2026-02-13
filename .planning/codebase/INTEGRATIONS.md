# External Integrations

**Analysis Date:** 2026-02-12

## APIs & External Services

**None** - This is a local data processing pipeline with no external API integrations.

The codebase processes pre-downloaded datasets from academic/commercial data providers (CRSP, Compustat, IBES, etc.). All data is read from local Parquet files in `1_Inputs/`.

## Data Storage

**Databases:**
- None - No database connections (SQLite, PostgreSQL, etc.)

**File Storage:**
- Local filesystem only
- Primary format: Parquet (via pyarrow)
- Secondary formats: CSV, Excel (.xlsx)
- All data stored in `1_Inputs/` (source) and `4_Outputs/` (results)

**Caching:**
- None - No Redis, memcached, or similar

## Data Sources (Local Files)

**Financial Data:**
- CRSP_DSF - Daily stock returns, prices, volumes
  - Location: `1_Inputs/CRSP_DSF/`
- Compustat (comp_na_daily_all) - Annual/quarterly financials
  - Location: `1_Inputs/comp_na_daily_all/`
- CRSP-Compustat CCM Link Table
  - Location: `1_Inputs/CRSPCompustat_CCM/`

**Analyst Data:**
- I/B/E/S (tr_ibes) - Analyst forecasts, dispersion
  - Location: `1_Inputs/tr_ibes/`

**Executive Data:**
- Execucomp - Executive compensation, CEO identification
  - Location: `1_Inputs/Execucomp/`

**Text Data:**
- Earnings Call Transcripts
  - Location: `1_Inputs/Earnings_Calls_Transcripts/`
  - Files: `Unified-info.parquet`, `speaker_data_{year}.parquet`

**Reference Data:**
- Loughran-McDonald Master Dictionary - Sentiment word lists
  - Location: `1_Inputs/LM_dictionary/Loughran-McDonald_MasterDictionary_1993-2024.csv`
- Fama-French Industry Classifications (FF1248)
  - Location: `1_Inputs/FF1248/`
- Manager Roles - Executive title patterns
  - Location: `1_Inputs/Manager_roles/`

**M&A Data:**
- SDC Platinum - Mergers and acquisitions
  - Location: `1_Inputs/SDC/`

**Instruments:**
- CCCL Instrument - Exogenous variation instrument
  - Location: `1_Inputs/CCCL_instrument/instrument_shift_intensity_2005_2022.parquet`

**Risk Data:**
- Firm-Level Risk Measures (PRisk)
  - Location: `1_Inputs/FirmLevelRisk/`

## Authentication & Identity

**Auth Provider:**
- None - No authentication required
- All data is pre-authenticated (licensed academic datasets)

## Monitoring & Observability

**Error Tracking:**
- None - No Sentry, Rollbar, etc.

**Logging:**
- Custom `DualWriter` class at `2_Scripts/shared/observability/logging.py`
- Logs to both stdout and file simultaneously
- Log files written to `3_Logs/`
- Format: `%(asctime)s [%(levelname)s] %(message)s`

**Memory Monitoring:**
- `get_process_memory_mb()` in `2_Scripts/shared/observability/memory.py`
- Uses psutil for process memory tracking

**Performance:**
- Throughput calculation in `2_Scripts/shared/observability/throughput.py`
- Benchmark tests in `tests/performance/`

## CI/CD & Deployment

**Hosting:**
- GitHub (repository hosting)
- GitHub Actions (CI/CD runner: ubuntu-latest)

**CI Pipeline:**
- GitHub Actions at `.github/workflows/test.yml`
- Multi-version testing (Python 3.8-3.13)
- Coverage reporting to Codecov
- Artifacts uploaded for test results and coverage

**CI Stages:**
1. Checkout code
2. Set up Python (matrix: 3.8, 3.9, 3.10, 3.11, 3.12, 3.13)
3. Cache pip dependencies
4. Install dependencies
5. Type check with mypy (continue-on-error)
6. Run unit/integration tests (coverage threshold: 60%)
7. Generate coverage summary
8. Upload to Codecov
9. Upload artifacts

**E2E Tests:**
- Separate job, runs only on Python 3.10
- 30-minute timeout
- Depends on unit tests passing

## Environment Configuration

**Required env vars:**
- `PYTHONPATH` - Must include `2_Scripts/` directory for module imports
  - Used in CI: `PYTHONPATH: ${{ github.workspace }}/2_Scripts`
  - Required for subprocess integration tests (see `tests/conftest.py`)

**Secrets:**
- `CODECOV_TOKEN` - Optional, for Codecov uploads (private repos)

**No .env files** - No runtime secrets or configuration

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

## External Python Packages

**Typed via Stubs:**
- linearmodels - Panel OLS, IV regression (no official type stubs)
  - Custom stubs at `2_Scripts/stubs/`

**Graceful Degradation:**
- rapidfuzz - Fuzzy string matching
  - Warning if missing, pipeline continues with reduced match quality
  - See `2_Scripts/shared/string_matching.py:RAPIDFUZZ_AVAILABLE`

- linearmodels - Econometric models
  - ImportError handled in `2_Scripts/shared/panel_ols.py` and `iv_regression.py`
  - `LINEARMODELS_AVAILABLE` flag for conditional imports

## Data Flow Architecture

```
1_Inputs/ (Parquet/CSV) --> 2_Scripts/ (Processing) --> 4_Outputs/ (Results)
        |                         |                            |
        v                         v                            v
    CRSP/Compustat         shared/ utilities            Regression tables
    Earnings calls         Step-specific scripts       Summary statistics
    LM Dictionary          Econometric models          Diagnostics
```

**Key Processing Steps:**
1. Sample Manifest (1.x scripts) - Entity linking, tenure mapping
2. Text Processing (2.x scripts) - Tokenization, variable construction
3. Financial Features (3.x scripts) - Control variables, event flags
4. Econometric Analysis (4.x scripts) - Panel OLS, IV, survival analysis

---

*Integration audit: 2026-02-12*
