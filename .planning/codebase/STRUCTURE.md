# Codebase Structure

**Analysis Date:** 2026-01-22

## Directory Layout

```
F1D/
├── README.md                          # Comprehensive pipeline documentation
├── requirements.txt                   # Python dependencies (pandas, numpy, statsmodels, etc.)
├── CLAUDE.md                          # Project conventions and design principles
├── .claude/                           # Claude AI assistant configuration
│   └── settings.json                 # Project-specific settings
├── config/                            # Configuration layer
│   └── project.yaml                   # Central configuration (paths, params, seeds)
├── 1_Inputs/                          # Raw data storage
│   ├── Unified-info.parquet           # Earnings call metadata (55 MB)
│   ├── speaker_data_2002.parquet ... speaker_data_2018.parquet  # Transcript text (2.5 GB)
│   ├── Loughran-McDonald_MasterDictionary_1993-2024.csv  # Financial sentiment dict
│   ├── CRSPCompustat_CCM/            # WRDS linking table
│   ├── CRSP_DSF/                     # Daily stock returns
│   ├── comp_na_daily_all/            # Compustat North America daily
│   ├── tr_ibes/                      # IBES analyst forecasts
│   ├── Execucomp/                    # Executive compensation data
│   ├── SDC/                          # M&A deal data
│   ├── CCCL instrument/              # Instrumental variable data
│   └── master_variable_definitions.csv  # Variable metadata
├── 2_Scripts/                        # Processing pipeline
│   ├── 1_Sample/                     # Stage 1: Sample construction
│   │   ├── 1.0_BuildSampleManifest.py  # Orchestrator for 1.1-1.4
│   │   ├── 1.1_CleanMetadata.py       # Deduplicate and filter metadata
│   │   ├── 1.2_LinkEntities.py        # Entity resolution (4-tier linking)
│   │   ├── 1.3_BuildTenureMap.py      # CEO tenure panel construction
│   │   ├── 1.4_AssembleManifest.py    # Final manifest assembly
│   │   └── 1.5_Utils.py               # Shared utilities (dual writer, symlinks)
│   ├── 2_Text/                       # Stage 2: Text processing
│   │   ├── 2.1_TokenizeAndCount.py    # Tokenize and count LM dict words
│   │   ├── 2.2_ConstructVariables.py  # Build linguistic variables
│   │   ├── 2.3_VerifyStep2.py        # Validation script
│   │   └── __pycache__/               # Python cache
│   ├── 3_Financial/                  # Stage 3: Financial features
│   │   ├── 3.0_BuildFinancialFeatures.py  # Orchestrator
│   │   ├── 3.1_FirmControls.py        # Compute firm-level controls
│   │   ├── 3.2_MarketVariables.py     # Compute market variables
│   │   ├── 3.3_EventFlags.py          # Identify takeover/dismissal events
│   │   ├── 3.4_Utils.py               # Shared utilities
│   │   └── __pycache__/               # Python cache
│   ├── 4_Econometric/                 # Stage 4: Econometric analysis
│   │   ├── 4.1_EstimateCeoClarity.py       # Baseline CEO clarity model
│   │   ├── 4.1.1_EstimateCeoClarity_CeoSpecific.py  # CEO-specific model
│   │   ├── 4.1.2_EstimateCeoClarity_Extended.py    # Extended controls
│   │   ├── 4.1.3_EstimateCeoClarity_Regime.py      # Firm regime model
│   │   ├── 4.1.4_EstimateCeoTone.py                # CEO tone model
│   │   ├── 4.2_LiquidityRegressions.py     # IV analysis
│   │   ├── 4.3_TakeoverHazards.py          # Survival analysis
│   │   ├── 4.4_GenerateSummaryStats.py      # Descriptive statistics
│   │   ├── apply_all_stats.py              # Apply stats to all outputs
│   │   ├── apply_stats.py                  # Stats utility
│   │   └── ARCHIVE_BROKEN_STEP4/           # Archived broken code
│   ├── 2.99_ValidateStats.py           # Pipeline validation script
│   ├── ARCHIVE/                        # Historical/archived code
│   │   ├── 0_Visualization/
│   │   ├── 1.5_Utils.py
│   │   ├── 3.4_Utils.py
│   │   ├── 4.2_RedTeamAudit.py
│   │   ├── ARCHIVE_BROKEN_STEP2/
│   │   └── debug_*.py                   # Debug scripts
│   └── ARCHIVE_OLD/                    # Older archived versions
│       ├── 2.0b_BuildMasterTenureMap.py
│       ├── 2.0c_BuildMonthlyTenurePanel.py
│       └── ... (other deprecated scripts)
├── 3_Logs/                           # Execution logs
│   ├── 1.0_BuildSampleManifest/       # Log files per script
│   │   └── YYYY-MM-DD_HHMMSS.log
│   ├── 1.1_CleanMetadata/
│   ├── 1.2_LinkEntities/
│   ├── ... (one directory per script)
│   └── OLD/                            # Archived logs
├── 4_Outputs/                        # Processed data and results
│   ├── 1.0_BuildSampleManifest/
│   │   ├── YYYY-MM-DD_HHMMSS/          # Timestamped output directory
│   │   │   ├── master_sample_manifest.parquet
│   │   │   ├── report_step_1_0.md
│   │   │   └── variable_reference.csv
│   │   └── latest/                      # Symlink to most recent run
│   ├── 1.1_CleanMetadata/
│   ├── ... (one directory per script)
│   └── OLD/                            # Archived outputs
├── .planning/                        # Project documentation (internal)
│   ├── codebase/                      # Codebase analysis documents
│   │   ├── ARCHITECTURE.md            # This analysis
│   │   └── STRUCTURE.md               # This analysis
│   ├── phases/                        # GSD project phases
│   │   ├── 01-template-pilot/
│   │   ├── 02-sample-enhancement/
│   │   ├── 03-text-processing/
│   │   ├── 04-financial-econometric/
│   │   ├── 05-readme-documentation/
│   │   └── 06-pre-submission/
│   ├── research/                      # Research documents
│   │   ├── ARCHITECTURE.md
│   │   ├── FEATURES.md
│   │   ├── PITFALLS.md
│   │   ├── STACK.md
│   │   └── SUMMARY.md
│   ├── PROJECT.md                     # Project overview
│   ├── REQUIREMENTS.md                # Requirements specification
│   ├── ROADMAP.md                     # Development roadmap
│   ├── STATE.md                       # Current state
│   └── config.json                    # Configuration metadata
├── BACKUP_20260114_191340/           # Backup snapshot
├── Docs/                             # Additional documentation
├── ___Archive/                       # Misc archived files
└── .git/                             # Git repository
```

## Directory Purposes

**1_Inputs/:**
- Purpose: Storage for all raw data files from external sources
- Contains: Parquet files (metadata, speaker transcripts), CSV dictionaries, Excel files, zipped data
- Key files: `Unified-info.parquet`, `speaker_data_*.parquet`, `Loughran-McDonald_MasterDictionary_1993-2024.csv`, `master_variable_definitions.csv`

**2_Scripts/:**
- Purpose: All processing scripts organized by pipeline stage
- Contains: 4 stage subdirectories (1_Sample, 2_Text, 3_Financial, 4_Econometric), orchestrators, utilities, archived code
- Key files: Orchestrators (1.0, 3.0), transformation scripts (1.1-1.4, 2.1-2.2, 3.1-3.3, 4.1-4.3), validation scripts, utilities (1.5, 3.4)

**3_Logs/:**
- Purpose: Execution logs for all pipeline runs with complete audit trails
- Contains: One subdirectory per script with timestamped log files
- Key files: `*.log` files with script execution history, git SHA, config snapshots, input checksums

**4_Outputs/:**
- Purpose: Versioned processed data, intermediate datasets, and final results
- Contains: One subdirectory per script with timestamped runs and `latest/` symlinks
- Key files: `master_sample_manifest.parquet`, `linguistic_variables.parquet`, `firm_controls.parquet`, `ceo_clarity_scores.parquet`, regression results, LaTeX tables

**config/:**
- Purpose: Central configuration management
- Contains: `project.yaml` with all paths, parameters, and settings
- Key files: `project.yaml` (single source of truth for runtime behavior)

**.planning/:**
- Purpose: Project planning, research notes, and GSD workflow documents
- Contains: Phase plans, research documents, codebase analysis, project metadata
- Key files: `PROJECT.md`, `REQUIREMENTS.md`, `ROADMAP.md`, phase plans, codebase analysis

## Key File Locations

**Entry Points:**
- `2_Scripts/1_Sample/1.0_BuildSampleManifest.py`: Orchestrator for Stage 1 sample construction
- `2_Scripts/2_Text/2.1_TokenizeAndCount.py`: Stage 2 text processing entry point
- `2_Scripts/3_Financial/3.0_BuildFinancialFeatures.py`: Orchestrator for Stage 3 financial features
- `2_Scripts/4_Econometric/4.1_EstimateCeoClarity.py`: Stage 4 econometric analysis entry point
- `2_Scripts/2.99_ValidateStats.py`: Pipeline validation script

**Configuration:**
- `config/project.yaml`: Central configuration with paths, year ranges, determinism settings, step-specific parameters

**Core Logic:**
- `2_Scripts/1_Sample/`: Sample construction (metadata cleaning, entity linking, tenure mapping, manifest assembly)
- `2_Scripts/2_Text/`: Text processing (tokenization, word counting, variable construction)
- `2_Scripts/3_Financial/`: Financial feature engineering (firm controls, market variables, event flags)
- `2_Scripts/4_Econometric/`: Econometric analysis (CEO clarity estimation, liquidity regressions, takeover hazards)

**Utilities:**
- `2_Scripts/1_Sample/1.5_Utils.py`: Shared utilities for Stage 1 (DualWriter, get_latest_output_dir, generate_variable_reference, update_latest_symlink)
- `2_Scripts/3_Financial/3.4_Utils.py`: Shared utilities for Stage 3 (same utilities as 1.5)

**Testing:**
- `2_Scripts/2.99_ValidateStats.py`: Validation script for statistical outputs
- `2_Scripts/4_Econometric/apply_all_stats.py`: Apply statistics to all output files
- `2_Scripts/4_Econometric/apply_stats.py`: Statistics utility

## Naming Conventions

**Files:**
- Pattern: `<Stage>.<Step>_<PascalCaseName>.<ext>`
- Examples: `1.1_CleanMetadata.py`, `2.1_TokenizeAndCount.py`, `3.1_FirmControls.py`, `4.1_EstimateCeoClarity.py`
- Regex: `^(1|2|3|4)\.(\d+)(?:\.(\d+))?_[A-Z][A-Za-z0-9]*(?:_[A-Z][A-Za-z0-9]*)*(?:\.[A-Za-z0-9]+)?$`

**Directories:**
- Pattern: `<Stage>_<PascalCaseName>/` or `<Step>_<PascalCaseName>/`
- Examples: `1_Sample/`, `2_Text/`, `3_Financial/`, `4_Econometric/`
- Output directories: Same as script name (e.g., `1.1_CleanMetadata/`, `2.2_ConstructVariables/`)
- Log directories: Same as script name (e.g., `1.1_CleanMetadata/`, `4.1_EstimateCeoClarity/`)

**Output Files:**
- Pattern: `<descriptive_name>.parquet` or `<descriptive_name>.csv` or `report_step_<stage>_<step>.md`
- Examples: `metadata_cleaned.parquet`, `linguistic_variables.parquet`, `ceo_clarity_scores.parquet`, `regression_results.txt`

**Timestamped Directories:**
- Pattern: `YYYY-MM-DD_HHMMSS`
- Example: `2026-01-22_211302`

## Where to Add New Code

**New Feature in Existing Stage:**
- Primary code: `2_Scripts/<stage>/<next_step>_<FeatureName>.py`
- Example: New Stage 2 feature → `2_Scripts/2_Text/2.4_NewFeature.py`
- Utilities: Add to stage's Utils.py file if shared across multiple scripts (e.g., `2_Scripts/2_Text/2.5_Utils.py`)

**New Stage:**
- Implementation: Create `2_Scripts/<N>_<StageName>/` directory
- Scripts: Add `<N>.0_<StageName>Orchestrator.py` for coordination, then `<N>.1_*`, `<N>.2_*`, etc. for substeps
- Utils: Create `<N>.5_Utils.py` for shared utilities
- Example: New "Visualization" stage → `2_Scripts/5_Visualization/5.0_VisualizeResults.py`, `5.1_GeneratePlots.py`, `5.5_Utils.py`

**New Output:**
- Location: `4_Outputs/<script_name>/YYYY-MM-DD_HHMMSS/`
- Symlink: Automatically creates `latest/` via `update_latest_symlink()` utility

**Utility Functions:**
- Stage-specific: Add to `<stage>.5_Utils.py` in the stage directory
- Cross-stage: Duplicate in both stage Utils.py files (per self-contained replication principle)

## Special Directories

**ARCHIVE/ and ARCHIVE_OLD/:**
- Purpose: Historical code, deprecated scripts, and broken implementations
- Generated: No (manually maintained)
- Committed: Yes
- Note: Contains reference implementations and debugging scripts

**__pycache__:**
- Purpose: Python bytecode cache
- Generated: Yes (automatically by Python)
- Committed: No (in `.gitignore`)
- Location: In each stage subdirectory

**.planning/:**
- Purpose: Project documentation, GSD workflow artifacts, research notes
- Generated: No (manually maintained)
- Committed: Yes
- Contains: Codebase analysis, phase plans, project metadata

**.claude/:**
- Purpose: Claude AI assistant configuration for this project
- Generated: Yes (initially by Claude, then maintained)
- Committed: Yes (except `settings.local.json` which is gitignored)

**BACKUP_20260114_191340/:**
- Purpose: Project backup snapshot
- Generated: Yes (manual backup)
- Committed: Yes
- Note: Timestamped backup directory

**Docs/ and ___Archive/:**
- Purpose: Additional documentation and misc archived files
- Generated: No
- Committed: Yes
- Note: Legacy directories, may be consolidated

---

*Structure analysis: 2026-01-22*
