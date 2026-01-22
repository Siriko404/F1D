# External Integrations

**Analysis Date:** 2026-01-22

## APIs & External Services

**None Detected:**
- The codebase operates entirely on local data files. No external API calls (HTTP/REST) were identified in the scanned scripts.

## Data Storage

**Databases:**
- **Local Filesystem Only** - Data is stored primarily in Parquet files.
  - Intermediate format: Parquet (`.parquet`)
  - Input format: CSV, Parquet

**File Storage:**
- **Local Filesystem**
  - Inputs: `1_Inputs/`
  - Outputs: `4_Outputs/`
  - Logs: `3_Logs/`

**Caching:**
- **None** - Direct file I/O.

## Authentication & Identity

**Auth Provider:**
- **None** - Single-user local execution environment.

## Monitoring & Observability

**Error Tracking:**
- **None** - Relies on console output and local logs.

**Logs:**
- **Dual-Writer Pattern** - Custom implementation (`utils.DualWriter`) mirroring stdout to log files in `3_Logs/`.
- Log level and format configured in `config/project.yaml`.

## CI/CD & Deployment

**Hosting:**
- **Local Machine** - Designed for local execution.

**CI Pipeline:**
- **None detected**

## Environment Configuration

**Required env vars:**
- None detected. All configuration is file-based (`config/project.yaml`).

**Secrets location:**
- No secrets management detected (likely not required for local data processing).

## Webhooks & Callbacks

**Incoming:**
- **None**

**Outgoing:**
- **None**

---

*Integration audit: 2026-01-22*
