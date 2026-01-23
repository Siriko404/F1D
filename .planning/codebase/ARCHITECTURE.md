# Architecture

**Analysis Date:** 2026-01-22

## Pattern Overview

**Overall:** Configuration-driven sequential data processing pipeline for academic research reproducibility

**Key Characteristics:**
- **Four-stage sequential pipeline** with data flowing from raw inputs through sample construction, text processing, financial feature engineering, and econometric analysis
- **Configuration-driven** single source of truth (`config/project.yaml`) - no command-line arguments
- **Self-contained scripts** - each script runs independently with no external orchestration dependencies
- **Deterministic execution** - fixed random seeds, pinned thread counts, sorted operations for bitwise-identical outputs
- **Timestamped outputs** with `latest/` symlinks for versioning
- **Dual-write logging** to both stdout and log files for complete audit trails

## Layers

**1_Inputs Layer:**
- Purpose: Raw data storage from 8 external sources (EventStudy transcripts, Loughran-McDonald dictionary, CRSP/Compustat/IBES/Execucomp/SDC, CCCL instrument)
- Location: `1_Inputs/`
- Contains: Parquet files, CSV dictionaries, Excel spreadsheets, zipped data
- Depends on: External data providers (WRDS, EventStudy)
- Used by: Stage 1 and Stage 2 scripts

**Configuration Layer:**
- Purpose: Central configuration management for paths, parameters, and settings
- Location: `config/project.yaml`
- Contains: Path definitions, year ranges, determinism settings, step-specific parameters
- Depends on: Nothing (top of dependency chain)
- Used by: All scripts via `load_config()` function

**Processing Layer (2_Scripts):**
- Purpose: Sequential transformation pipeline organized in 4 stages
- Location: `2_Scripts/`
- Contains: 4 stage subdirectories (`1_Sample/`, `2_Text/`, `3_Financial/`, `4_Econometric/`) with individual processing scripts
- Depends on: `1_Inputs/`, `config/project.yaml`, outputs from previous stages
- Used by: Researchers running the pipeline

**Logging Layer:**
- Purpose: Execution logging and audit trails
- Location: `3_Logs/`
- Contains: Timestamped log files per script (`3_Logs/<script_name>/<timestamp>.log`)
- Depends on: All scripts write here via `DualWriter` class
- Used by: Researchers for debugging and reproducibility verification

**Outputs Layer:**
- Purpose: Versioned processed data and results
- Location: `4_Outputs/`
- Contains: Timestamped subdirectories per script with `latest/` symlinks
- Depends on: All scripts write here
- Used by: Downstream scripts (as inputs) and final analysis

## Data Flow

**Stage 1: Sample Construction**

1. `1.1_CleanMetadata.py` - Load `Unified-info.parquet`, deduplicate rows, filter for earnings calls (event_type='1'), clean dates/strings
2. `1.2_LinkEntities.py` - Link calls to firms via 4-tier strategy (PERMNO+date, CUSIP8+date, fuzzy match, ticker) using CRSPCompustat_CCM
3. `1.3_BuildTenureMap.py` - Build monthly CEO tenure panel from Execucomp, resolve overlapping tenures, identify first CEOs
4. `1.4_AssembleManifest.py` - Merge all datasets, assign CEO/firm identifiers, compute industry codes, apply minimum 5-call threshold
5. Output: `master_sample_manifest.parquet` (~5,889 calls, 2,457 CEOs, 2,361 firms)

**Stage 2: Text Processing**

1. `2.1_TokenizeAndCount.py` - Tokenize Q&A text from speaker data files, count Loughran-McDonald dictionary word categories (Positive, Negative, Uncertainty, Litigious, Modal, Constraining)
2. `2.2_ConstructVariables.py` - Construct linguistic variables (Manager_QA_Uncertainty_pct, Manager_QA_Negative_pct, NetTone, etc.) as percentages of total tokens
3. Output: `linguistic_variables.parquet` with 72 text-based measures

**Stage 3: Financial Feature Engineering**

1. `3.1_FirmControls.py` - Compute firm-level controls from Compustat (Size, BM, Lev, ROA, CurrentRatio, RD_Intensity, Volatility), winsorize at 1%/99%
2. `3.2_MarketVariables.py` - Compute market variables from CRSP/IBES around call dates (StockRet, MarketRet, Volatility, Delta_Amihud)
3. `3.3_EventFlags.py` - Identify takeover events from SDC, CEO dismissal events
4. Outputs: `firm_controls.parquet`, `market_variables.parquet`, `event_flags.parquet`

**Stage 4: Econometric Analysis**

1. `4.1_EstimateCeoClarity.py` - Baseline model: Estimate CEO fixed effects from Manager_QA_Uncertainty_pct with CEO×Year and Industry×Year fixed effects
2. `4.1.1-4.1.4_EstimateCeoClarity_*.py` - Robustness checks: CEO-specific, extended, regime, tone models
3. `4.2_LiquidityRegressions.py` - IV analysis testing CEO clarity impact on liquidity using CCCL instrument
4. `4.3_TakeoverHazards.py` - Cox proportional hazards model testing CEO clarity impact on takeover risk
5. Outputs: CEO clarity scores, regression tables, LaTeX tables for paper

**State Management:**
- Data passed between stages via parquet files in `4_Outputs/<stage>/latest/`
- Scripts use `get_latest_output_dir()` utility to locate dependencies
- Versioning via timestamps enables reproducibility without overwriting previous runs

## Key Abstractions

**DualWriter Class:**
- Purpose: Synchronous writing to stdout and log file
- Examples: `2_Scripts/1_Sample/1.1_CleanMetadata.py`, `2_Scripts/3_Financial/3.4_Utils.py`
- Pattern: Each script instantiates `DualWriter(log_path)` and replaces `sys.stdout`

**get_latest_output_dir() Function:**
- Purpose: Resolve output directory using `latest/` symlink or find most recent timestamped folder
- Examples: `2_Scripts/1_Sample/1.5_Utils.py`, `2_Scripts/3_Financial/3.4_Utils.py`
- Pattern: Utility for scripts to find outputs from previous stages

**generate_variable_reference() Function:**
- Purpose: Generate `variable_reference.csv` with column metadata (dtype, null count, unique values, source, description)
- Examples: `2_Scripts/1_Sample/1.5_Utils.py`, `2_Scripts/3_Financial/3.4_Utils.py`
- Pattern: Looks up definitions from `1_Inputs/master_variable_definitions.csv`

**Orchestrator Pattern:**
- Purpose: Coordinate multi-step processes with subprocess execution
- Examples: `2_Scripts/1_Sample/1.0_BuildSampleManifest.py` (orchestrates 1.1-1.4 substeps)
- Pattern: Define substep list, execute sequentially via `subprocess.run()`, handle failures

**Stats Helper Pattern:**
- Purpose: Consistent statistics printing (before/after deltas, single values)
- Examples: `compute_file_checksum()`, `print_stat()`, `analyze_missing_values()`
- Pattern: Reusable inlined functions (not shared module) for self-contained replication

## Entry Points

**Individual Scripts (Primary Entry Points):**
- Location: `2_Scripts/<stage>/<step>_<Name>.py`
- Triggers: Direct execution via `python <script>`
- Responsibilities: Single transformation step with descriptive statistics and validation

**Orchestrators:**
- Location: `2_Scripts/1_Sample/1.0_BuildSampleManifest.py`
- Triggers: Direct execution coordinates multiple substeps
- Responsibilities: Run 1.1-1.4 sequentially, aggregate results, update final output

**Validation Scripts:**
- Location: `2_Scripts/2.99_ValidateStats.py`
- Triggers: Manual execution for pipeline verification
- Responsibilities: Validate statistical outputs across pipeline stages

## Error Handling

**Strategy:** Fail fast with explicit error messages and complete context

**Patterns:**
- Schema validation: Scripts validate input parquet schemas before processing
- Missing file checks: Clear errors if required inputs not found
- Subprocess failure propagation: Orchestrators exit immediately on substep failure
- Output validation: Each script verifies output files exist and are non-empty

**Cross-Cutting Concerns:**

**Logging:**
- Approach: DualWriter class writes verbatim output to stdout and log file
- Log format: `[TIMESTAMP] [LEVEL] Message` as configured in `project.yaml`
- Log header: Script ID, execution timestamps, git SHA, config snapshot, input checksums

**Validation:**
- Approach: Each script validates inputs, processes, and outputs with descriptive statistics
- Statistics: Row counts, missing value analysis, column distributions, data quality checks
- Validation files: `variable_reference.csv`, `report_step_*.md`, CSV statistics

**Determinism:**
- Random seeds: Fixed at 42 in `config/project.yaml`
- Thread counts: Pinned at 1 for reproducibility
- Sorting: All data operations sorted to avoid filesystem order dependencies
- Hashing: SHA256 checksums computed for all inputs

---

*Architecture analysis: 2026-01-22*
