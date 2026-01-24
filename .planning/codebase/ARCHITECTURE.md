# Architecture

**Analysis Date:** 2026-01-24

## Pattern Overview

**Overall:** Sequential Pipeline with Orchestrator Pattern

**Key Characteristics:**
- **Four-stage pipeline** with linear data flow (Sample → Text → Financial → Econometric)
- **Direct-run scripts** (no CLI flags) that read configuration from central `config/project.yaml`
- **Orchestrator scripts** coordinate substeps via `subprocess.run()` with validated paths
- **Deterministic processing** enforced through seeds, sorted inputs, and checksums
- **Shared utilities** extracted to `2_Scripts/shared/` for cross-stage reuse
- **Dual output logging** to both terminal and timestamped log files
- **Immutable outputs** written to timestamped directories with `latest/` symlinks

## Layers

**Orchestration Layer:**
- Purpose: Coordinate execution of substeps within a stage
- Location: `2_Scripts/1.0_BuildSampleManifest.py`, `2_Scripts/3.0_BuildFinancialFeatures.py`
- Contains: Substep definitions, subprocess execution, validation, error handling
- Depends on: `config/project.yaml`, `shared/subprocess_validation.py`, `shared/symlink_utils.py`
- Used by: User runs orchestrator scripts directly

**Data Processing Layer:**
- Purpose: Transform data according to stage-specific logic
- Location: `2_Scripts/1_Sample/`, `2_Scripts/2_Text/`, `2_Scripts/3_Financial/`, `2_Scripts/4_Econometric/`
- Contains: Tokenization, variable construction, regression analysis, entity linking
- Depends on: `shared/` utilities, `1_Inputs/` data, outputs from previous stages
- Used by: Orchestrator scripts, downstream stages

**Shared Utilities Layer:**
- Purpose: Provide reusable functions across stages
- Location: `2_Scripts/shared/`
- Contains: Path validation, data loading, logging, regression helpers, string matching
- Depends on: Standard library, pandas, numpy, statsmodels, optional dependencies (rapidfuzz)
- Used by: All processing scripts and orchestrators

**Testing Layer:**
- Purpose: Validate correctness and stability of pipeline components
- Location: `tests/unit/`, `tests/integration/`, `tests/regression/`
- Contains: Unit tests for shared utilities, integration tests for pipeline stages, regression tests for output stability
- Depends on: pytest, test fixtures in `tests/fixtures/`
- Used by: CI/CD pipeline (`.github/workflows/`)

**Configuration Layer:**
- Purpose: Centralize all runtime parameters
- Location: `config/project.yaml`
- Contains: Paths, seeds, thread counts, per-step parameters, thresholds
- Depends on: None (single source of truth)
- Used by: All scripts at startup

## Data Flow

**Complete Pipeline Flow:**

1. **Raw Input Stage** (`1_Inputs/`)
   - Earnings call transcripts (speaker_data_*.parquet, Unified-info.parquet)
   - Financial databases (CRSP, Compustat, Execucomp, SDC)
   - Reference files (LM dictionary, industry codes, variable definitions)

2. **Sample Construction** (`2_Scripts/1_Sample/`)
   - 1.1_CleanMetadata: Validate and clean call metadata
   - 1.2_LinkEntities: Link calls to firms via 4-tier strategy (PERMNO, CUSIP, fuzzy, ticker)
   - 1.3_BuildTenureMap: Build CEO tenure timeline
   - 1.4_AssembleManifest: Merge into `master_sample_manifest.parquet` (~286K calls)

3. **Text Processing** (`2_Scripts/2_Text/`)
   - 2.1_TokenizeAndCount: Tokenize Q&A text, count LM dictionary categories
   - 2.2_ConstructVariables: Compute linguistic variables (MaQaUnc_pct, NetTone, etc.)
   - Output: `linguistic_variables.parquet` per year

4. **Financial Features** (`2_Scripts/3_Financial/`)
   - 3.1_FirmControls: Stock returns, EPS growth, earnings surprise deciles
   - 3.2_MarketVariables: Market returns, industry returns
   - 3.3_EventFlags: Liquidity events, takeover events
   - Output: `firm_controls.parquet`, `market_variables.parquet` per year

5. **Econometric Analysis** (`2_Scripts/4_Econometric/`)
   - 4.1_EstimateCeoClarity: Fixed effects OLS to extract CEO clarity trait
   - 4.2_LiquidityRegressions: Test clarity-liquidity relationship
   - 4.3_TakeoverHazards: Hazard models for takeover probability
   - Output: CEO scores, regression results, diagnostic tables

**State Management:**
- All intermediate data persisted as Parquet files in `4_Outputs/`
- Each output in timestamped directory: `YYYY-MM-DD_HHMMSS/`
- `latest/` symlink points to most recent successful run
- No in-memory state between stages; full checkpoint restart capability

## Key Abstractions

**DualWriter:**
- Purpose: Mirror output to both stdout and log file
- Examples: `2_Scripts/shared/observability_utils.py: DualWriter`
- Pattern: Context manager that captures print() calls and writes to both streams
- Usage: Every script calls `sys.stdout = DualWriter(log_path)` at startup

**Orchestrator-Substep Pattern:**
- Purpose: Execute related scripts sequentially with validation
- Examples: `2_Scripts/1_Sample/1.0_BuildSampleManifest.py`
- Pattern: Define substeps in list, validate paths, `subprocess.run()`, capture output
- Security: `shared/subprocess_validation.py` prevents path traversal attacks

**Tiered Entity Linking:**
- Purpose: Match company names across databases with fallback strategies
- Examples: `2_Scripts/1_Sample/1.2_LinkEntities.py`
- Pattern:
  - Tier 1: PERMNO + exact date match (highest confidence)
  - Tier 2: CUSIP8 + date match
  - Tier 3: Fuzzy string match (>=92% similarity, requires rapidfuzz)
  - Tier 4: Ticker symbol match (lowest confidence)
- Used: Sample construction stage only

**File Caching with lru_cache:**
- Purpose: Eliminate redundant I/O in regression loops
- Examples: `2_Scripts/4_Econometric/4.1_EstimateCeoClarity.py: load_cached_parquet()`
- Pattern: `@lru_cache(maxsize=32)` decorator on file loading function
- Used: Econometric stage when processing multiple regression specifications

**Latest Symlink Pattern:**
- Purpose: Provide stable reference to most recent successful output
- Examples: `2_Scripts/shared/symlink_utils.py: update_latest_link()`
- Pattern: Create/update symlink (Windows: junction) to timestamped directory
- Cross-platform: Falls back to directory copy on Windows Admin failures

## Entry Points

**Orchestrator Scripts:**
- Location: `2_Scripts/1.0_BuildSampleManifest.py`, `2_Scripts/3.0_BuildFinancialFeatures.py`
- Triggers: User runs directly: `python 2_Scripts/1.0_BuildSampleManifest.py`
- Responsibilities: Coordinate substeps, validate paths, update latest symlink, aggregate outputs

**Individual Processing Scripts:**
- Location: All scripts in `2_Scripts/1_Sample/`, `2_Scripts/2_Text/`, `2_Scripts/3_Financial/`, `2_Scripts/4_Econometric/`
- Triggers: Called by orchestrator or run directly for debugging
- Responsibilities: Load config, read inputs, transform data, write outputs, generate reports

**Shared Utilities:**
- Location: `2_Scripts/shared/*.py`
- Triggers: Imported by processing scripts
- Responsibilities: Path validation, data loading, regression helpers, logging

**Test Suite:**
- Location: `tests/` directory
- Triggers: `pytest` command, CI/CD workflows
- Responsibilities: Validate functionality, detect regressions, ensure stability

**Report Generation:**
- Location: `2_Scripts/2.3_Report.py`
- Triggers: User runs after pipeline completion
- Responsibilities: Aggregate outputs, generate markdown reports

## Error Handling

**Strategy:** Fail-fast with detailed logging

**Patterns:**
- **Path Validation:** `shared/path_utils.py: validate_input_file()`, `validate_output_path()` raises `PathValidationError` with descriptive messages
- **Subprocess Orchestration:** Captures stderr from subprocess calls, prints to both stdout and log, exits on non-zero return code
- **Data Validation:** Schema checks (column existence, non-null requirements) before processing
- **Memory Management:** `shared/chunked_reader.py` provides chunked reading and column pruning for large datasets
- **Graceful Degradation:** Optional dependencies (rapidfuzz) have try/except imports with fallback to basic implementations

**Cross-Cutting Concerns:**

**Logging:** DualWriter writes verbatim to terminal and `3_Logs/<step>/<timestamp>.log`
**Validation:** Path validation, schema validation, script path validation (security)
**Authentication:** None (data is public finance databases)
**Configuration:** Central `config/project.yaml` loaded at script startup via `yaml.safe_load()`

---

*Architecture analysis: 2026-01-24*
