# Codebase Structure

**Analysis Date:** 2026-01-22

## Directory Layout

```
[project-root]/
├── 1_Inputs/           # Raw read-only data (Parquet, CSV)
├── 2_Scripts/          # Processing logic source code
│   ├── 1_Sample/       # Sample construction scripts
│   ├── 2_Text/         # Textual analysis and tokenization
│   ├── 3_Financial/    # Financial controls and metrics
│   └── 4_Econometric/  # Regression and analysis
├── 3_Logs/             # Execution logs (mirrors script structure)
├── 4_Outputs/          # Generated artifacts (Timestamped + latest)
└── config/             # Runtime configuration
```

## Directory Purposes

**1_Inputs:**
- Purpose: Storage for immutable raw data.
- Contains: `speaker_data_{year}.parquet`, `Unified-info.parquet`, Dictionaries.

**2_Scripts:**
- Purpose: Application logic.
- Contains: Python scripts categorized by domain.
- Key files: `2.1_TokenizeAndCount.py`, `3.0_BuildFinancialFeatures.py`.

**4_Outputs:**
- Purpose: Step results.
- Structure: Subdirectories for each step, containing timestamped folders.
- Key mechanism: `latest` folder acts as the interface for dependent steps.

**config:**
- Purpose: Central control.
- Key files: `project.yaml` (Defines paths, seeds, thresholds).

## Key File Locations

**Entry Points:**
- `2_Scripts/2_Text/2.1_TokenizeAndCount.py`: Text processing entry.
- `2_Scripts/3_Financial/3.0_BuildFinancialFeatures.py`: Financial data entry.

**Configuration:**
- `config/project.yaml`: Main configuration file.

**Core Logic:**
- Logic is distributed across scripts in `2_Scripts/`. Shared utilities are often embedded or copy-pasted (e.g., `DualWriter`), though a shared lib may exist (not observed in root).

## Naming Conventions

**Files:**
- Scripts: `[Stage].[Step]_[PascalCaseName].py` (e.g., `2.1_TokenizeAndCount.py`).
- Data: `snake_case` with patterns (e.g., `speaker_data_{year}.parquet`).

**Directories:**
- Root: Numbered prefixes `1_Inputs`, `2_Scripts`, etc.
- Output: `[Stage].[Step]_[PascalCaseName]` or similar descriptive names.

**Variables:**
- Python: Standard `snake_case` for variables, `PascalCase` for classes.
- Config: `snake_case` keys (e.g., `year_start`, `min_calls_threshold`).

## Where to Add New Code

**New Processing Step:**
1. Determine category (`Text`, `Financial`, etc.).
2. Create script in `2_Scripts/{Category}/`.
3. Name it `[Stage].[NextStep]_[Name].py`.
4. Add configuration section to `config/project.yaml`.

**New Analysis/Regression:**
- Add to `2_Scripts/4_Econometric/`.

**New Data Source:**
- Place file in `1_Inputs/`.
- Update `config/project.yaml` `paths` section.

## Special Directories

**latest:**
- Purpose: Inside `4_Outputs/{Step}/`, points to the most recent successful run.
- Generated: Yes (by `update_latest_symlink`).
- Committed: No.

**__pycache__:**
- Purpose: Python bytecode.
- Generated: Yes.
- Committed: No.
