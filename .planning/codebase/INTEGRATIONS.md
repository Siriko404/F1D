# External Integrations

**Analysis Date:** 2026-02-20

## APIs & External Services

**None detected at runtime.**
The pipeline is fully offline. All data is pre-downloaded into the `inputs/` directory as Parquet files before execution begins. No HTTP client libraries (requests, httpx, aiohttp) are used in the `src/` tree. The `types-requests` stub is installed for type checking only.

## Data Storage

**Databases:**
- None — no database server (PostgreSQL, SQLite, etc.) is used.
- All persistence is via local Parquet files using PyArrow/pandas `read_parquet` / `to_parquet`.

**Primary data format:** Apache Parquet (`.parquet`) throughout all stages.

**Secondary data format:** CSV for audit/reporting outputs; `.xlsx` written via openpyxl for select reports.

**Input data files (pre-supplied, not fetched at runtime):**

| Dataset | Local path | Engine class |
|---------|-----------|--------------|
| Compustat NA Daily All | `inputs/comp_na_daily_all/comp_na_daily_all.parquet` | `src/f1d/shared/variables/_compustat_engine.py` → `CompustatEngine` |
| CRSP Daily Stock File | `inputs/CRSP_DSF/CRSP_DSF_{year}_Q{q}.parquet` | `src/f1d/shared/variables/_crsp_engine.py` → `CRSPEngine` |
| IBES Consensus Estimates | `inputs/tr_ibes/tr_ibes.parquet` (~25M rows) | `src/f1d/shared/variables/_ibes_engine.py` → `IBESEngine` |
| SDC M&A | `inputs/SDC/sdc-ma-merged.parquet` | `src/f1d/shared/variables/takeover_indicator.py` |
| Loughran-McDonald Dictionary | `inputs/Loughran-McDonald_MasterDictionary_1993-2024.csv` | `config/project.yaml` → `paths.lm_dictionary` |
| Earnings Call Transcripts (Unified Info) | `inputs/Earnings_Calls_Transcripts/Unified-info.parquet` | `config/project.yaml` → `paths.unified_info` |
| Earnings Call Transcripts (Speaker Data) | `inputs/Earnings_Calls_Transcripts/speaker_data_{year}.parquet` | `config/project.yaml` → `paths.speaker_data_pattern` |
| CCCL Shift-Share Instrument | `inputs/CCCL_instrument/instrument_shift_intensity_2005_2022.parquet` | `src/f1d/shared/variables/cccl_instrument.py` |
| Hassan et al. (2019) Policy Risk | `inputs/FirmLevelRisk/` | `src/f1d/shared/variables/_hassan_engine.py` |

All engines use a lazy-load + cache singleton pattern (`get_engine()` returning a module-level instance).

**File Storage:**
- Local filesystem only.
- Outputs written to timestamped subdirectories under `outputs/`.
- Logs written to `logs/`.

**Caching:**
- In-process singleton caches in Python engine objects (Compustat, CRSP, IBES, Hassan).
- No Redis, Memcached, or file-based caching layer.

## Authentication & Identity

**Auth Provider:**
- None — no authentication systems, user management, or identity providers.
- The only secrets are CI tokens (Codecov) stored as GitHub Actions secrets (`CODECOV_TOKEN`).

## Monitoring & Observability

**Error Tracking:**
- No external service (Sentry, Datadog, etc.).
- Errors are captured to log files via the internal `DualWriter` class (`src/f1d/shared/observability/logging.py`) and structlog (`src/f1d/shared/logging/`).

**Logs:**
- Dual output: structured JSON to `logs/` files + human-readable console output via structlog's `ConsoleRenderer`.
- Log level configurable via `config/project.yaml` (`logging.level`) or `F1D_LOGGING__LEVEL` env var.
- Script-specific logs written to `outputs/<step_subdir>/` alongside output data.

**Metrics / Observability:**
- In-process throughput, memory, anomaly detection utilities in `src/f1d/shared/observability/` (throughput.py, memory.py, stats.py, anomalies.py).
- psutil used for real-time memory-percent monitoring during chunked reads (`chunked_reader.py`; threshold: 80% per `config/project.yaml → chunk_processing.max_memory_percent`).

## CI/CD & Deployment

**Hosting:**
- Local research workstation only. No cloud deployment.

**CI Pipeline:**
- GitHub Actions — two workflows:
  - `.github/workflows/ci.yml`: lint (ruff + mypy) → test matrix (3.9–3.13) → E2E tests (main branch only). Uploads coverage to Codecov.
  - `.github/workflows/test.yml`: extended workflow — bandit SAST → test matrix → E2E tests.
- Dependabot configured via `.github/dependabot.yml` for automated dependency updates.
- Pre-commit hooks: ruff lint + format + mypy (Tier 1 only) + file safety checks.

**Coverage Reporting:**
- Codecov integration via `codecov/codecov-action@v4` — token: `secrets.CODECOV_TOKEN`.
- Coverage artifacts (XML, HTML, JSON) uploaded as GitHub Actions artifacts (30-day retention).

## Webhooks & Callbacks

**Incoming:**
- None.

**Outgoing:**
- None (excluding Codecov upload in CI).

## Environment Configuration

**Required env vars (from `.env.example`):**
- `F1D_API_TIMEOUT_SECONDS` — currently unused at runtime (no live API); reserved for future use
- `F1D_MAX_RETRIES` — currently unused at runtime; reserved for future use

**Other `F1D_`-prefixed vars** are read by pydantic-settings models in `src/f1d/shared/config/` (e.g., `F1D_LOGGING__LEVEL`, `F1D_LOGGING__FORMAT` per `src/f1d/shared/config/loader.py`).

**Secrets location:**
- `.env` (not committed; `.env.example` committed as template).
- GitHub Actions `secrets.CODECOV_TOKEN` for CI coverage uploads.

---

*Integration audit: 2026-02-20*
