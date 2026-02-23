# External Integrations

**Analysis Date:** 2026-02-21

## APIs & External Services

**Financial Data Providers:**
- WRDS (Wharton Research Data Services) - Source of Compustat, CRSP, IBES, and CCM data
  - Input data location: `inputs/comp_na_daily_all/`, `inputs/CRSP_DSF/`, `inputs/tr_ibes/`, `inputs/CRSPCompustat_CCM/`
  - No SDK/API client - data provided as static parquet files
  - Data processing engines: `src/f1d/shared/variables/_compustat_engine.py`, `src/f1d/shared/variables/_crsp_engine.py`, `src/f1d/shared/variables/_ibes_engine.py`

- Refinitiv SDC - M&A data source
  - Input data location: `inputs/SDC/`
  - Used for takeover hazard analysis in `src/f1d/econometric/run_h9_takeover_hazards.py`

**Academic Data Sources:**
- Loughran-McDonald Master Dictionary (1993-2024) - Sentiment word lists
  - Input: `inputs/LM_dictionary/Loughran-McDonald_MasterDictionary_1993-2024.csv`
  - Source: [McDonald Word Lists](https://sraf.nd.edu/textual-analysis/resources/)
  - Used for linguistic variable construction in `src/f1d/text/build_linguistic_variables.py`

- Hassan et al. (2019) Political Risk Data - Firm-level political risk measures
  - Input: `inputs/FirmLevelRisk/firmquarter_2022q1.csv` (TAB-separated)
  - Processing: `src/f1d/shared/variables/_hassan_engine.py`

**No real-time APIs:**
- This project uses static datasets downloaded from external providers
- No API keys or authentication required for data access
- No cloud service SDKs

## Data Storage

**Databases:**
- None - All data stored as flat files (parquet, CSV)

**File Storage:**
- Local filesystem only
- Parquet format for large datasets (via PyArrow 21.0.0)
- Excel files for metadata and summaries (via openpyxl)
- Input data location: `inputs/`
- Output data location: `outputs/`
- Logs location: `logs/`

**Caching:**
- In-memory singleton pattern for data engines
  - `CompustatEngine`: `src/f1d/shared/variables/_compustat_engine.py`
  - `CrspEngine`: `src/f1d/shared/variables/_crsp_engine.py`
  - `IbesEngine`: `src/f1d/shared/variables/_ibes_engine.py`
  - `HassanEngine`: `src/f1d/shared/variables/_hassan_engine.py`
- No distributed cache (Redis, Memcached not used)

## Authentication & Identity

**Auth Provider:**
- None - No external authentication required
- All data is publicly available academic datasets

**Implementation:**
- No OAuth, JWT, or API key management
- Environment variables only for timeout/retry configuration (not secrets)

## Monitoring & Observability

**Error Tracking:**
- None - No external error tracking service (Sentry, Rollbar not used)
- Structured logging via structlog (25.0) with console and file output
  - Log configuration: `src/f1d/shared/logging/config.py`

**Logs:**
- Structured logging with structlog
- Dual output to console and log files
- Memory tracking via psutil in `src/f1d/shared/observability/memory.py`
- Throughput tracking in `src/f1d/shared/observability/throughput.py`

**Coverage Reporting:**
- Coverage.py with thresholds
- CI uploads coverage to Codecov via `codecov/codecov-action@v4`
- Token: `secrets.CODECOV_TOKEN` (optional, fail_ci_if_error=false)

## CI/CD & Deployment

**Hosting:**
- GitHub for source control
  - Repository: `https://github.com/user/f1d`
  - CI runs on GitHub Actions (ubuntu-latest)

**CI Pipeline:**
- GitHub Actions
  - Lint job: Ruff (check and format), mypy strict mode
  - Test job: Multi-matrix Python 3.9-3.13, pytest with coverage thresholds
  - E2E test job: Runs on main branch only
  - Config: `.github/workflows/ci.yml`, `.github/workflows/test.yml`

**Deployment:**
- Not applicable - Research pipeline, not deployed service

## Environment Configuration

**Required env vars:**
- `F1D_API_TIMEOUT_SECONDS` - API timeout setting (default 30)
- `F1D_MAX_RETRIES` - Maximum retry attempts (default 3)
- `CODECOV_TOKEN` - Optional Codecov token for coverage uploads

**Secrets location:**
- No secrets required for core functionality
- GitHub secrets for CI/CD (CODECOV_TOKEN)
- `.env` file for local development (template in `.env.example`)

**Configuration files:**
- `.env.example` - Template for environment variables
- `config/project.yaml` - Pipeline configuration (paths, thresholds, step settings)
- `config/variables.yaml` - Variable definitions
- `pyproject.toml` - Tool configuration (pytest, ruff, mypy, coverage)

## Webhooks & Callbacks

**Incoming:**
- None - No webhooks or API endpoints

**Outgoing:**
- None - No external webhooks or callbacks
- All processing is batch-oriented with local file I/O

## NLP and Text Processing

**Libraries:**
- RapidFuzz 3.14.0+ - Fuzzy string matching for entity linking
  - Used in: `src/f1d/shared/string_matching.py`
  - Graceful degradation if not installed (pipeline runs without it)
  - Config-driven thresholds via `config/project.yaml` (string_matching section)

- Tokenization: Python sklearn.CountVectorizer with custom regex patterns
  - Used in: `src/f1d/text/tokenize_transcripts.py`

- No LLM or transformer-based models
- No cloud NLP services (OpenAI, HuggingFace not used)

## Statistical Libraries

**Panel Regression:**
- linearmodels - PanelOLS for fixed effects models
  - Entity and time fixed effects for CEO-level analysis
  - AbsorbingLS for high-dimensional fixed effects
  - IV2SLS for instrumental variable regression
  - Used in: `src/f1d/shared/panel_ols.py`, `src/f1d/shared/iv_regression.py`

- statsmodels - Classical econometrics
  - GLM regression for Biddle (2009) investment residuals
  - VIF (variance inflation factor) for multicollinearity detection
  - Formula API for model specification
  - Used in: `src/f1d/shared/diagnostics.py`, `src/f1d/econometric/*.py`

**Survival Analysis:**
- lifelines - Cox proportional hazards model
  - CoxTimeVaryingFitter for takeover hazard analysis
  - Used in: `src/f1d/econometric/run_h9_takeover_hazards.py`

**Data Validation:**
- pandera - DataFrame schema validation
  - Output schemas for regression results
  - Used in: `src/f1d/shared/output_schemas.py`

---

*Integration audit: 2026-02-21*
