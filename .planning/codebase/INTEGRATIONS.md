# External Integrations

**Analysis Date:** 2026-02-14

## APIs & External Services

**No external API calls:**
- Pipeline operates entirely on local data files
- No cloud service dependencies
- No real-time data fetching

## Data Storage

**Databases:**
- Parquet files via pyarrow - Primary data format
  - Location: `1_Inputs/` (input data), `4_Outputs/` (processed data)
  - Client: pandas.read_parquet(), pandas.to_parquet()
  - Schema: Defined in each step's output files

**External Data Sources (Local Files):**
- `1_Inputs/Earnings_Calls_Transcripts/Unified-info.parquet` - Earnings call metadata (55 MB)
- `1_Inputs/LM_dictionary/Loughran-McDonald_MasterDictionary_1993-2024.csv` - Text analysis dictionary (9 MB)
- `1_Inputs/CRSPCompustat_CCM/` - Linking table (GVKEY-PERMNO)
- `1_Inputs/CRSP_DSF/` - Daily stock returns
- `1_Inputs/comp_na_daily_all/` - Compustat North America daily
- `1_Inputs/tr_ibes/` - IBES analyst forecasts
- `1_Inputs/Execucomp/` - Executive compensation data
- `1_Inputs/SDC/` - M&A deal data
- `1_Inputs/CCCL_instrument/instrument_shift_intensity_2005_2022.parquet` - Instrumental variable data (15 MB)
- `1_Inputs/FirmLevelRisk/` - Firm-level risk measures
- `1_Inputs/FF1248/` - Fama-French factors
- `1_Inputs/SEC_Edgar_Letters/` - SEC correspondence data

**File Storage:**
- Local filesystem only (no cloud storage)
- Output files: Timestamped directories in `4_Outputs/`
- Log files: `3_Logs/` directory

**Caching:**
- None (data processed fresh on each run)

## Authentication & Identity

**Auth Provider:**
- None required (local data processing only)

**Implementation:**
- `src/f1d/shared/config/env.py` - Pydantic Settings for environment configuration
- `src/f1d/shared/env_validation.py` - Environment validation utilities

## Monitoring & Observability

**Error Tracking:**
- None (local execution only)

**Logs:**
- Framework: structlog (structured logging)
- Implementation: `src/f1d/shared/logging/`
  - `src/f1d/shared/logging/config.py` - Logging configuration
  - `src/f1d/shared/logging/handlers.py` - Log handlers (console, file, JSON)
  - `src/f1d/shared/logging/context.py` - Context management for structured logging
- Output: `3_Logs/` directory
- Format: Structured JSON logs with context variables
- Levels: INFO (default), configurable

## CI/CD & Deployment

**Hosting:**
- GitHub Actions (CI/CD only)
  - `.github/workflows/ci.yml` - Primary CI workflow (lint + test)
  - `.github/workflows/test.yml` - Extended test workflow

**CI Pipeline:**
- GitHub Actions
- Test matrix: Python 3.9, 3.10, 3.11, 3.12, 3.13
- Linting: Ruff (format check, lint), mypy (type checking)
- Testing: pytest with coverage
- Coverage reporting: Codecov integration
- Artifact retention: 30 days for coverage reports and test results

**Deployment:**
- None (local execution only)

## Environment Configuration

**Required env vars:**
- None (all optional)

**Optional env vars:**
- `F1D_API_TIMEOUT_SECONDS` - API timeout (default: 30)
- `F1D_MAX_RETRIES` - Max retry attempts (default: 3)

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

---

*Integration audit: 2026-02-14*
