# External Integrations

**Analysis Date:** 2026-03-25

## APIs & External Services

**No external API integrations detected.**

This is a self-contained local data processing pipeline. All data is read from pre-downloaded local files in `inputs/` and processed locally. The `F1D_API_TIMEOUT_SECONDS` and `F1D_MAX_RETRIES` env vars in `src/f1d/shared/config/env.py` are vestigial configuration with no active API client code in the codebase.

## Data Storage

**Databases:**
- None - All data stored as local files (no database connections)

**File Storage (Local Filesystem):**

**Input data:** `inputs/` directory with subdirectories per data source:

| Directory | Format | Description |
|-----------|--------|-------------|
| `inputs/Compustat_Annual/` | Parquet | Compustat quarterly financial data (atq, ceqq, ltq, cshoq, prccq, xrdy, aqcy, sppey, saley, sic, etc.) |
| `inputs/CRSP_DSF/` | Parquet (year-quarter partitioned: `CRSP_DSF_YYYY_QN.parquet`) | CRSP daily stock file (RET, VWRETD, VOL, PRC, BIDLO, ASKHI, BID, ASK, SHROUT) |
| `inputs/CRSPCompustat_CCM/` | Parquet (`CRSPCompustat_CCM.parquet`) | CRSP-Compustat merged linking table (cusip, LPERMNO, gvkey, LINKPRIM) |
| `inputs/Earnings_Calls_Transcripts/` | Parquet (year-partitioned: `speaker_data_{year}.parquet`, `Unified-info.parquet`) | Seeking Alpha earnings call transcripts |
| `inputs/tr_ibes/` | Parquet (yearly: `tr_ibes_YYYY.parquet`) | Thomson Reuters I/B/E/S analyst forecast detail data (CUSIP, ACTDATS, ANALYS, VALUE, MEASURE, FPI, FPEDATS) |
| `inputs/Execucomp/` | Mixed | S&P Executive compensation data for CEO identification |
| `inputs/SDC/` | Mixed | Thomson Reuters SDC Platinum M&A/takeover event data |
| `inputs/FirmLevelRisk/` | CSV (tab-separated: `firmquarter_2022q1.csv`) | Hassan et al. (2019) firm-quarter political risk measures (PRisk, NPRisk, PSentiment) |
| `inputs/LM_dictionary/` | CSV (`Loughran-McDonald_MasterDictionary_1993-2024.csv`) | Loughran-McDonald sentiment/uncertainty word lists |
| `inputs/FF1248/` | ZIP (`Siccodes48.zip`) | Fama-French 48-industry classification SIC code ranges |
| `inputs/Siccodes12.zip`, `inputs/Siccodes48.zip` | ZIP | Fama-French 12 and 48 industry classification files |
| `inputs/CCCL_instrument/` | Parquet (`instrument_shift_intensity_2005_2022.parquet`) | CCCL instrumental variable for clarity (shift intensity) |
| `inputs/Manager_roles/` | Mixed | Manager role classification data for speaker identification |
| `inputs/TNIC3HHIdata/` | Text (tab-separated: `TNIC3HHIdata.txt`, ~188K rows) | Hoberg-Phillips TNIC3 product similarity and HHI data |
| `inputs/comp_na_daily_all/` | Parquet (`comp_na_daily_all.parquet`) | Compustat North America daily data |
| `inputs/compustat_daily_ratings/` | CSV (`compustat_daily_ratings.csv`) | Compustat credit ratings data |

**Output data:** `outputs/` directory with timestamped subdirectories per stage:

| Directory | Stage | Description |
|-----------|-------|-------------|
| `outputs/1.1_CleanMetadata/` | 1 | Cleaned metadata |
| `outputs/1.2_LinkEntities/` | 1 | Entity linking results |
| `outputs/1.3_BuildTenureMap/` | 1 | CEO tenure maps |
| `outputs/1.4_AssembleManifest/` | 1 | Master sample manifest |
| `outputs/2_Textual_Analysis/` | 2 | Text processing and linguistic variables (year-partitioned) |
| `outputs/variables/` | 3 | Hypothesis-specific variable panels (per-suite subdirectories) |
| `outputs/econometric/` | 4 | Regression results per hypothesis test (per-suite subdirectories) |

**File formats (read):**
- Apache Parquet (via pyarrow 21.0.0) - Primary format for all intermediate and output data
- CSV - Audit reports, Hassan PRisk data (tab-separated), Compustat ratings, Loughran-McDonald dictionary
- Excel (.xlsx via openpyxl) - Some input datasets
- ZIP - Fama-French SIC code classification files (extracted in-memory)
- Plain text (.txt, tab-separated) - TNIC3HHI data, regression output

**File formats (written):**
- Apache Parquet - All intermediate and final data panels
- CSV - Audit reports, diagnostic outputs, summary statistics
- Plain text (.txt) - Regression results (formatted PanelOLS/IV2SLS/CoxPH summaries)
- Markdown (.md) - Stage-level summary reports, run logs
- LaTeX (.tex) - Publication-ready regression tables (booktabs three-line format)
- PDF - Compiled table output (`outputs/all_tables.pdf`)

**Caching:**
- Singleton engine pattern with in-memory caching: 7 engines load data once per process and cache results
  - `src/f1d/shared/variables/_compustat_engine.py` - Compustat quarterly financial data
  - `src/f1d/shared/variables/_crsp_engine.py` - CRSP daily stock returns and volatility
  - `src/f1d/shared/variables/_ibes_engine.py` - IBES consensus forecast data (FPI 6/7)
  - `src/f1d/shared/variables/_ibes_detail_engine.py` - IBES individual analyst estimates (detail-level, ~10M rows/year)
  - `src/f1d/shared/variables/_linguistic_engine.py` - Stage 2 linguistic percentage variables
  - `src/f1d/shared/variables/_hassan_engine.py` - Hassan et al. political risk measures
  - `src/f1d/shared/variables/_clarity_residual_engine.py` - CEO/Manager clarity residuals from Stage 4 output
- Configuration caching in `src/f1d/shared/config/loader.py` (in-memory module-level cache)
- Thread-safe singleton access via `threading.Lock()` in engine modules
- No external caching service

## Authentication & Identity

**Auth Provider:**
- None - Local pipeline with no authentication requirements
- No API keys, tokens, or credentials needed for pipeline execution

## Monitoring & Observability

**Error Tracking:**
- Custom observability module at `src/f1d/shared/observability/`
  - `anomalies.py` - Anomaly detection in data
  - `memory.py` - Memory usage monitoring (via psutil)
  - `throughput.py` - Processing throughput tracking
  - `stats.py` - Statistical monitoring
  - `files.py` - File-level observability
  - `logging.py` - Observability logging integration, DualWriter (stdout + file)

**Logs:**
- structlog-based structured logging (`src/f1d/shared/logging/`)
  - `config.py` - Logging configuration (JSON or console output via ConsoleRenderer/JSONRenderer)
  - `context.py` - Context binding for structured log entries
  - `handlers.py` - Custom log handlers
  - `TeeOutput` class in `config.py` captures print() to log file while still showing on console
- Log output directory: `logs/` (configured in `config/project.yaml`)
- Log level configurable via `config/project.yaml` (default: INFO)
- Per-run log files created by `setup_run_logging()` in econometric runners

## CI/CD & Deployment

**Hosting:**
- Local development machine (no cloud deployment)

**CI Pipeline:**
- GitHub Actions (`.github/workflows/ci.yml`, `.github/workflows/test.yml`)
  - **Lint job:** Python 3.11, Ruff linting + formatting check, mypy type checking (Tier 1: `src/f1d/shared/` only)
  - **Test job:** Matrix across Python 3.9-3.13, depends on lint passing
    - Tier 1 tests: `tests/unit/test_panel_ols.py`, `tests/unit/test_iv_regression.py`, `tests/unit/test_data_validation.py` (10% threshold)
    - Tier 2 tests: `tests/integration/`, `tests/unit/test_path_utils.py`, `tests/unit/test_chunked_reader.py` (10% threshold)
    - Full suite: all tests except e2e, 40% overall coverage threshold
  - **E2E job:** Runs on push to main only, Python 3.11, 1200s timeout
  - Coverage reports: XML, HTML, JSON formats uploaded to Codecov via `codecov/codecov-action@v4`
  - Artifacts retained 30 days per Python version

- Pre-commit hooks (`.pre-commit-config.yaml`):
  - `pre-commit/pre-commit-hooks` v5.0.0: trailing-whitespace, end-of-file-fixer, check-yaml, check-toml, check-json, check-added-large-files (1MB limit), check-merge-conflict, check-case-conflict, detect-private-key, debug-statements
  - `astral-sh/ruff-pre-commit` v0.9.0: ruff linting (with --fix) and formatting
  - `pre-commit/mirrors-mypy` v1.14.1: mypy on `src/f1d/shared` only (with pydantic and types-PyYAML deps)

## Environment Configuration

**Required env vars:**
- None strictly required - pipeline runs with defaults from `config/project.yaml`
- Optional: `F1D_API_TIMEOUT_SECONDS` (default: 30), `F1D_MAX_RETRIES` (default: 3)

**Env file:**
- `.env.example` present in repo root (existence noted only, contents not read)
- `.env` loaded by pydantic-settings with `F1D_` prefix (`src/f1d/shared/config/env.py`)

**Secrets location:**
- No secrets required for pipeline execution - all data is local, no external API keys needed
- `CODECOV_TOKEN` stored in GitHub Actions secrets (CI only)

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

## Data Source Provenance

The pipeline processes academic financial datasets that are pre-downloaded locally. Data sources loaded by singleton engines in `src/f1d/shared/variables/`:

| Source | Directory | Engine | Used By (Suites) |
|--------|-----------|--------|-------------------|
| WRDS/Compustat Quarterly | `inputs/Compustat_Annual/` | `_compustat_engine.py` | All suites (financial controls: Size, ROA, Lev, BM, TobinsQ, CashHoldings, etc.) |
| WRDS/CRSP Daily | `inputs/CRSP_DSF/` | `_crsp_engine.py` | H7 (Illiquidity), H14 (Bid-Ask), all suites (StockRet, Volatility controls) |
| WRDS/CCM | `inputs/CRSPCompustat_CCM/` | Used by `_crsp_engine.py`, `_ibes_engine.py` | PERMNO-GVKEY and CUSIP-GVKEY linking |
| Thomson Reuters/I/B/E/S Summary | `inputs/tr_ibes/` | `_ibes_engine.py` | H5 (Dispersion), all suites (EPS surprise controls) |
| Thomson Reuters/I/B/E/S Detail | `inputs/tr_ibes/` | `_ibes_detail_engine.py` | H5b (Johnson DISP2), H14 (point-in-time dispersion) |
| Seeking Alpha | `inputs/Earnings_Calls_Transcripts/` | `_linguistic_engine.py` | All suites (linguistic variables: uncertainty, sentiment, modal) |
| S&P/Execucomp | `inputs/Execucomp/` | Sample construction | CEO identification and tenure |
| Thomson Reuters/SDC | `inputs/SDC/` | `build_h9_takeover_panel.py` | H9 (Takeover hazard events) |
| Hassan et al. (2019) | `inputs/FirmLevelRisk/` | `_hassan_engine.py` | H9 (PRiskFY control), H11 (Political risk DV) |
| Loughran-McDonald (2024) | `inputs/LM_dictionary/` | Step 01 dictionary builder | Text tokenization (uncertainty, negative, modal word lists) |
| Fama-French | `inputs/FF1248/`, `inputs/Siccodes*.zip` | `_compustat_engine.py`, industry_utils | FF12/FF48 industry classification for FE and subsamples |
| Custom/CCCL | `inputs/CCCL_instrument/` | `cccl_instrument.py` builder | H6 (IV for clarity: shift intensity instrument) |
| Hoberg-Phillips TNIC3 | `inputs/TNIC3HHIdata/` | `run_h1_1_cash_tsimm.py`, `run_h13_1_competition.py` | H1.1, H13.1 (product similarity/HHI moderation) |
| Compustat Daily | `inputs/comp_na_daily_all/` | Various | Stock price and daily financial data |
| Compustat Ratings | `inputs/compustat_daily_ratings/` | Various | Credit ratings data |
| Clarity Residuals (internal) | `outputs/econometric/ceo_clarity_extended/` | `_clarity_residual_engine.py` | H6, H7, H9 (CEO/Manager clarity residual as IV) |

## LaTeX Table Generation

**Table pipeline:**
- `outputs/generate_all_tables.py` - Master table generator that reads regression `.txt` files and produces LaTeX
- `src/f1d/shared/latex_tables.py` - Core LaTeX formatting (coefficient with significance stars, SE in parentheses)
- `src/f1d/shared/latex_tables_complete.py` - Full Accounting Review style tables (booktabs three-line format)
- `src/f1d/shared/latex_tables_accounting.py` - Accounting-specific formatting variants
- Output: `outputs/all_tables.tex` compiled to `outputs/all_tables.pdf`
- 21 hypothesis suites with 3 table types: standard (8-column), moderation (2-4 column), and custom

---

*Integration audit: 2026-03-25*
