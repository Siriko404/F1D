# Phase 79: Test Stage 1 Sample Scripts - Research

**Researched:** 2026-02-14
**Domain:** F1D Data Processing Pipeline - Stage 1 Sample Construction
**Confidence:** HIGH

## Summary

Stage 1 of the F1D pipeline consists of 5 scripts (1.0 through 1.5) that construct the master sample manifest defining the universe of analysis. The orchestrator script (1.0_BuildSampleManifest) calls 4 substeps in sequence: cleaning metadata (1.1), linking entities to CRSP/Compustat CCM (1.2), building CEO tenure maps from Execucomp (1.3), and assembling the final manifest with CEO filtering (1.4). Each script follows a consistent architecture pattern with timestamped outputs, comprehensive statistics tracking, and markdown reporting.

**Primary recommendation:** Run scripts via the orchestrator (`python -m f1d.sample.1_0_BuildSampleManifest`) for full pipeline execution. Use `--dry-run` flag first to validate prerequisites. Full-scale testing requires all input datasets present in `1_Inputs/` directory.

---

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Testing Scope & Scale

- **Scripts to test:** All 5 sample scripts (1.0_BuildSampleManifest, 1.1_CleanMetadata, 1.2_LinkEntities, 1.3_BuildTenureMap, 1.4_AssembleManifest)
- **Data years:** All years (2002-2018) - full historical range
- **Quarters:** All quarters (Q1-Q4) - complete annual cycles
- **Data source:** Real data from inputs folder (actual production data, not synthetic fixtures)

#### Pass/Fail Criteria

- **No prior outputs to compare against** - this is first comprehensive validation
- **Primary success metric:** Code review for logical correctness + flawless execution
- **Validation approach:** Read scripts to understand expected behavior, then verify outputs match expectations
- **Schema validation:** Outputs match expected columns/types from script analysis
- **Value validation:** Values are logically consistent with script purpose and input data

#### Issue Handling

- **Fix mode:** Fix issues immediately as discovered during testing
- **Stop criteria:** Stop on first error, fix, then continue
- **Issue tracking:** Formal issue tracking (TODOs/issues in codebase)
- **Regression prevention:** Add tests for each fixed issue

#### Audit Depth & Reporting

- **Audit scope:** Comprehensive - full dataflow trace + standards compliance + performance metrics
- **Report format:** Both markdown report AND structured data file (JSON/YAML)
- **Metrics to capture:**
  - Performance timing (wall-clock time per script, throughput)
  - Data profile stats (row counts, column counts, null rates, type distribution)
  - Code quality metrics (import patterns, legacy code usage, standard compliance)
  - Resource utilization (memory usage, disk I/O)
- **Output persistence:** Keep all test outputs in dedicated folder for inspection

### Claude's Discretion

- Exact report file names and locations
- Specific performance thresholds that constitute "acceptable"
- Structured data file format (JSON vs YAML)
- Organization of output storage folder

### Deferred Ideas (OUT OF SCOPE)

None - discussion stayed within phase scope

</user_constraints>

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pandas | 2.x | DataFrame operations | All scripts use for data manipulation |
| numpy | 1.x | Numerical operations | Used for NaN handling, type conversions |
| yaml | 6.x | Configuration loading | Loads project.yaml settings |
| rapidfuzz | 3.x | Fuzzy string matching | Entity linking in 1.2 (optional, falls back gracefully) |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pyarrow | 14.x | Parquet I/O | All scripts read/write parquet files |
| pathlib | stdlib | Path handling | Cross-platform path operations |

### Internal Dependencies
| Module | Location | Purpose |
|--------|----------|---------|
| f1d.shared.path_utils | src/f1d/shared/ | Path validation, output directory resolution |
| f1d.shared.dependency_checker | src/f1d/shared/ | Prerequisite validation |
| f1d.shared.observability_utils | src/f1d/shared/ | Statistics collection, logging |
| f1d.shared.sample_utils | src/f1d/shared/ | Variable reference generation |
| f1d.shared.string_matching | src/f1d/shared/ | Fuzzy name matching configuration |
| f1d.shared.industry_utils | src/f1d/shared/ | FF industry code parsing |

**Installation:**
```bash
pip install pandas numpy pyyaml pyarrow rapidfuzz
```

---

## Architecture Patterns

### Script Structure (All Stage 1 Scripts Follow This Pattern)

```
src/f1d/sample/
├── __init__.py                    # Package marker
├── 1.0_BuildSampleManifest.py     # ORCHESTRATOR - calls substeps
├── 1.1_CleanMetadata.py           # SUBSTEP - data cleaning
├── 1.2_LinkEntities.py            # SUBSTEP - entity resolution
├── 1.3_BuildTenureMap.py          # SUBSTEP - tenure panel construction
├── 1.4_AssembleManifest.py        # SUBSTEP - final assembly
└── 1.5_Utils.py                   # UTILITIES (legacy, moved to shared)
```

### Output Directory Structure

```
4_Outputs/
├── 1.0_BuildSampleManifest/
│   └── {YYYY-MM-DD_HHMMSS}/
│       ├── master_sample_manifest.parquet  # Final output (copied from 1.4)
│       └── report_step_1_0.md              # Execution summary
├── 1.1_CleanMetadata/
│   └── {YYYY-MM-DD_HHMMSS}/
│       ├── metadata_cleaned.parquet
│       ├── variable_reference.csv
│       ├── stats.json
│       └── report_step_1_1.md
├── 1.2_LinkEntities/
│   └── {YYYY-MM-DD_HHMMSS}/
│       ├── metadata_linked.parquet
│       ├── variable_reference.csv
│       ├── stats.json
│       └── report_step_1_2.md
├── 1.3_BuildTenureMap/
│   └── {YYYY-MM-DD_HHMMSS}/
│       ├── tenure_monthly.parquet
│       ├── variable_reference.csv
│       ├── stats.json
│       └── report_step_1_3.md
└── 1.4_AssembleManifest/
    └── {YYYY-MM-DD_HHMMSS}/
        ├── master_sample_manifest.parquet
        ├── variable_reference.csv
        ├── stats.json
        └── report_step_1_4.md
```

### Script Header Pattern

Each script follows a consistent docstring pattern:

```python
"""
==============================================================================
STEP X.Y: {Script Name}
==============================================================================
ID: {script_id}
Description: {what the script does}

Inputs:
    - {input_path_1}
    - {input_path_2}

Outputs:
    - {output_path_1}
    - {output_path_2}

Deterministic: true
Dependencies:
    - Requires: {prerequisite_step}
    - Uses: {libraries}

Author: Thesis Author
Date: 2026-02-11
==============================================================================
"""
```

### CLI Pattern

All scripts support:
```bash
python -m f1d.sample.{script_name} --dry-run   # Validate prerequisites
python -m f1d.sample.{script_name}             # Execute
```

### Statistics Collection Pattern

Each script collects comprehensive statistics:

```python
stats: Dict[str, Any] = {
    "step_id": "X.Y_ScriptName",
    "timestamp": timestamp,
    "input": {"files": [], "checksums": {}, "total_rows": 0, "total_columns": 0},
    "processing": {},  # Step-specific metrics
    "output": {"final_rows": 0, "final_columns": 0, "files": [], "checksums": {}},
    "missing_values": {},
    "timing": {"start_iso": "", "end_iso": "", "duration_seconds": 0.0},
    "memory_mb": {},  # Operation-level memory tracking
    "throughput": {},  # Rows per second
}
```

---

## Dataflow Analysis

### Complete Data Pipeline

```
EXTERNAL INPUTS (1_Inputs/)
    |
    v
+--------------------------------------------------------+
| 1_Inputs/Unified-info.parquet                          |
| - Raw earnings call metadata                           |
| - ~500K+ records, all event types                      |
| - Fields: file_name, company_id, permno, cusip, etc.  |
+--------------------------------------------------------+
    |
    | 1.1_CleanMetadata.py
    | - Deduplicate exact rows
    | - Resolve file_name collisions (keep earliest timestamp)
    | - Filter event_type='1' (earnings calls only)
    | - Filter years 2002-2018
    v
+--------------------------------------------------------+
| 4_Outputs/1.1_CleanMetadata/{ts}/metadata_cleaned.parquet |
| - Cleaned earnings call metadata                       |
| - ~200K-300K records                                   |
+--------------------------------------------------------+
    |
    | 1.2_LinkEntities.py
    | - 4-tier linking strategy:
    |   Tier 1: PERMNO + Date Range (quality=100)
    |   Tier 2: CUSIP8 + Date Range (quality=90)
    |   Tier 3: Fuzzy Name Match (quality=80, threshold=92)
    | - Maps SIC to FF12/FF48 industries
    | - Uses dedup-index optimization (~11K unique companies vs 297K calls)
    v
+--------------------------------------------------------+
| 4_Outputs/1.2_LinkEntities/{ts}/metadata_linked.parquet |
| - Linked metadata with GVKEY, industry codes           |
| - ~150K-200K records (unmatched removed)              |
+--------------------------------------------------------+
    |
    |                       +------------------------------------------------+
    |                       | 1_Inputs/Execucomp/comp_execucomp.parquet     |
    |                       | - CEO executive data                           |
    |                       | - Fields: gvkey, execid, becameceo, leftofc   |
    |                       +------------------------------------------------+
    |                                          |
    |                                          | 1.3_BuildTenureMap.py
    |                                          | - Build CEO tenure episodes
    |                                          | - Link predecessors
    |                                          | - Expand to monthly panel
    |                                          | - Resolve overlaps
    |                                          v
    |                       +------------------------------------------------+
    |                       | 4_Outputs/1.3_BuildTenureMap/{ts}/            |
    |                       |   tenure_monthly.parquet                       |
    |                       | - Monthly CEO panel                            |
    |                       | - Fields: gvkey, year, month, ceo_id, etc.    |
    |                       +------------------------------------------------+
    |                                          |
    | 1.4_AssembleManifest.py                  |
    | - Join on (gvkey, year, month)           |
    | - 6-digit zero-padded gvkey for join     |
    | - Filter CEOs with >= 5 calls            |
    v
+--------------------------------------------------------+
| 4_Outputs/1.4_AssembleManifest/{ts}/                   |
|   master_sample_manifest.parquet                       |
| - Final sample universe                                |
| - ~100K-150K records                                   |
| - Defines universe for all subsequent analysis         |
+--------------------------------------------------------+
    |
    | 1.0_BuildSampleManifest.py (ORCHESTRATOR)
    | - Copies final manifest to own output dir
    v
+--------------------------------------------------------+
| 4_Outputs/1.0_BuildSampleManifest/{ts}/                |
|   master_sample_manifest.parquet                       |
+--------------------------------------------------------+
```

### Key Join Logic (1.4_AssembleManifest)

```python
# Join key: (gvkey, year, month)
# GVKEY normalization: 6-digit zero-padding for consistency
metadata["gvkey"] = metadata["gvkey"].apply(
    lambda x: str(int(x)).zfill(6) if pd.notna(x) else None
)
tenure["gvkey"] = tenure["gvkey"].astype(str).str.zfill(6)

merged = metadata.merge(
    tenure[["gvkey", "year", "month", "ceo_id", "ceo_name", "prev_ceo_id", "prev_ceo_name"]],
    on=["gvkey", "year", "month"],
    how="left"
)
```

---

## Input Data Requirements

### Required External Data Files

| File | Location | Size | Purpose |
|------|----------|------|---------|
| Unified-info.parquet | 1_Inputs/ | ~55MB | Raw earnings call metadata |
| CRSPCompustat_CCM.parquet | 1_Inputs/CRSPCompustat_CCM/ | ~2.4MB | Entity linking reference |
| comp_execucomp.parquet | 1_Inputs/Execucomp/ | ~44MB | CEO tenure data |
| Siccodes12.zip | 1_Inputs/FF1248/ | ~1KB | FF12 industry mapping |
| Siccodes48.zip | 1_Inputs/FF1248/ | ~10KB | FF48 industry mapping |
| master_variable_definitions.csv | 1_Inputs/ | Optional | Variable metadata |

### Configuration File

`config/project.yaml` must contain:
```yaml
data:
  year_start: 2002
  year_end: 2018
paths:
  inputs: 1_Inputs
  outputs: 4_Outputs
  logs: 3_Logs
step_02_5c:
  min_calls_threshold: 5  # CEO filtering threshold
```

---

## Script Details

### 1.0_BuildSampleManifest.py (Orchestrator)

**Purpose:** Sequential execution of 4 substeps with logging and error handling.

**Key Features:**
- Validates prerequisites before execution
- Sets PYTHONPATH for subprocess imports
- Security: validates script paths before execution
- Copies final manifest to orchestrator output directory

**Execution:**
```bash
python -m f1d.sample.1_0_BuildSampleManifest --dry-run  # Validate
python -m f1d.sample.1_0_BuildSampleManifest            # Execute
```

### 1.1_CleanMetadata.py

**Purpose:** Clean and filter raw metadata from Unified-info.parquet.

**Operations:**
1. Load Unified-info.parquet
2. Deduplicate exact row duplicates
3. Resolve file_name collisions (keep earliest validation_timestamp)
4. Filter event_type='1' (earnings calls only)
5. Filter years 2002-2018 (configurable)

**Output Columns:** All original columns from Unified-info, cleaned

**Statistics Tracked:**
- exact_duplicates_removed
- collision_rows_resolved
- non_earnings_removed
- out_of_range_removed
- Temporal coverage (year/month/quarter distribution)
- Entity characteristics (unique companies, cities)

### 1.2_LinkEntities.py

**Purpose:** Link earnings calls to CRSP/Compustat CCM database for firm identifiers.

**4-Tier Linking Strategy:**
| Tier | Method | Quality Score | Typical Match Rate |
|------|--------|---------------|-------------------|
| 1 | PERMNO + Date Range | 100 | ~70-80% |
| 2 | CUSIP8 + Date Range | 90 | ~10-15% |
| 3 | Fuzzy Name Match | 80 | ~5-10% |

**Dedup-Index Optimization:**
- Groups calls by company_id before matching
- Reduces ~297K individual calls to ~11K unique company lookups
- Broadcasts results back to all related calls

**Output Columns:**
- All columns from metadata_cleaned
- gvkey (Compustat firm identifier)
- conm (Company name from CCM)
- sic (Industry code)
- link_method (which tier matched)
- link_quality (score 80/90/100)
- fuzzy_score (if Tier 3 matched)
- ff12_code, ff12_name, ff48_code, ff48_name

### 1.3_BuildTenureMap.py

**Purpose:** Build monthly CEO tenure panel from Execucomp data.

**Operations:**
1. Filter Execucomp for CEO records (ceoann='CEO' or becameceo not null)
2. Build tenure episodes per (gvkey, execid)
3. Link predecessor CEOs
4. Expand to monthly panel
5. Resolve overlaps (keep most recent CEO)

**Active CEO Handling:**
- If CEO's max year >= latest dataset year: impute end_date as 2025-12-31
- Otherwise: use last fiscal year end

**Output Columns:**
- gvkey, year, month, date
- ceo_id (execid)
- ceo_name (exec_fullname)
- prev_ceo_id
- prev_ceo_name

### 1.4_AssembleManifest.py

**Purpose:** Join linked metadata with CEO tenure panel and apply final filtering.

**Operations:**
1. Load metadata_linked.parquet
2. Load tenure_monthly.parquet
3. Join on (gvkey, year, month) with 6-digit zero-padded gvkey
4. Filter unmatched calls
5. Apply minimum call threshold (>= 5 calls per CEO, configurable)
6. Sort by file_name for determinism

**Output Columns:**
- file_name (unique call identifier)
- gvkey, start_date, conm, sic
- ff12_code, ff12_name, ff48_code, ff48_name
- ceo_id, ceo_name
- prev_ceo_id, prev_ceo_name

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Timestamped output directory | Manual timestamp handling | `get_latest_output_dir()` from path_utils | Handles edge cases, sorting, required file checks |
| Prerequisite validation | Custom file checks | `validate_prerequisites()` from dependency_checker | Clear error messages, actionable guidance |
| Variable reference generation | Manual column profiling | `generate_variable_reference()` from sample_utils | Handles master definitions lookup |
| Fuzzy string matching | Custom similarity algorithms | `match_company_names()` from string_matching | Configurable threshold, multiple scorers |
| Industry code mapping | Manual SIC to FF lookup | `parse_ff_industries()` from industry_utils | Handles zip files, edge cases |

**Key insight:** All shared utilities exist in `src/f1d/shared/` - import from there, never create local copies.

---

## Common Pitfalls

### Pitfall 1: Missing Prerequisite Step Output

**What goes wrong:** Script fails with "Missing prerequisite output from X.Y"

**Why it happens:** Pipeline steps must run in order; each step depends on previous output.

**How to avoid:** Always run via orchestrator (1.0_BuildSampleManifest.py) or use `--dry-run` first.

**Warning signs:** Output directory for previous step is empty or missing.

### Pitfall 2: GVKEY Type Mismatch in Join

**What goes wrong:** 1.4_AssembleManifest produces 0% match rate on join.

**Why it happens:** Metadata gvkey is numeric, tenure gvkey is zero-padded string.

**How to avoid:** Script handles this with 6-digit zero-padding:
```python
metadata["gvkey"] = metadata["gvkey"].apply(
    lambda x: str(int(x)).zfill(6) if pd.notna(x) else None
)
```

**Warning signs:** Match rate < 50% in join statistics.

### Pitfall 3: RapidFuzz Not Available

**What goes wrong:** Tier 3 (fuzzy name matching) skipped with warning.

**Why it happens:** RapidFuzz is optional dependency, may not be installed.

**How to avoid:** Install rapidfuzz or accept lower match rate.

**Warning signs:** Log shows "WARNING: rapidfuzz not available, skipping".

### Pitfall 4: Active CEO Date Imputation

**What goes wrong:** Tenure panel shows unexpected future dates (2025-12-31).

**Why it happens:** Active CEOs get imputed end date for panel construction.

**How to avoid:** This is expected behavior; filter in analysis if needed.

**Warning signs:** end_date column contains 2025 dates - this is intentional.

### Pitfall 5: Timestamp Collision in Output Directories

**What goes wrong:** Two runs in same second create duplicate directories.

**Why it happens:** Timestamp granularity is seconds; rapid re-runs collide.

**How to avoid:** Wait >1 second between runs or use unique identifiers.

**Warning signs:** Multiple directories with same timestamp prefix.

---

## Code Examples

### Running Full Pipeline

```bash
# From project root
cd /path/to/F1D

# Validate prerequisites first
python -m f1d.sample.1_0_BuildSampleManifest --dry-run

# Execute full pipeline
python -m f1d.sample.1_0_BuildSampleManifest

# Check outputs
ls -la 4_Outputs/1.0_BuildSampleManifest/
```

### Running Individual Step

```bash
# Run step 1.1 only (requires no prerequisites)
python -m f1d.sample.1_1_CleanMetadata --dry-run
python -m f1d.sample.1_1_CleanMetadata

# Run step 1.2 (requires 1.1 output)
python -m f1d.sample.1_2_LinkEntities --dry-run  # Validates 1.1 output exists
python -m f1d.sample.1_2_LinkEntities
```

### Checking Prerequisites Programmatically

```python
from pathlib import Path
from f1d.shared.dependency_checker import validate_prerequisites

root = Path(__file__).parent

required_files = {
    "Unified-info.parquet": root / "1_Inputs" / "Unified-info.parquet",
}

required_steps = {
    "1.1_CleanMetadata": "metadata_cleaned.parquet",
}

validate_prerequisites(required_files, required_steps)
```

### Getting Latest Output Directory

```python
from pathlib import Path
from f1d.shared.path_utils import get_latest_output_dir

output_base = Path("4_Outputs") / "1.1_CleanMetadata"

# Get latest directory with required file
latest_dir = get_latest_output_dir(
    output_base,
    required_file="metadata_cleaned.parquet"
)

print(f"Latest output: {latest_dir}")
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Symlinks for "latest" output | Timestamp-based resolution with `get_latest_output_dir()` | Phase 62 | More reliable on Windows, no permission issues |
| Chained .loc assignments | Vectorized `df.update()` | Phase 62-01 | 2-5x speedup for bulk updates |
| Individual company matching | Dedup-index optimization | Phase 62 | ~27x reduction in matching operations |
| Separate utility files per step | Consolidated shared utilities | Phase 78 | Single source of truth, easier maintenance |

**Deprecated/outdated:**
- `1.5_Utils.py` in sample directory: Functions moved to `src/f1d/shared/sample_utils.py`
- Symlink-based latest resolution: Replaced with timestamp sorting

---

## Open Questions

1. **What is the expected row count range for each step?**
   - What we know: Unified-info is ~500K+ records, filtered to earnings calls only
   - What's unclear: Exact expected counts after each transformation
   - Recommendation: First run establishes baseline; compare subsequent runs

2. **What constitutes acceptable match rate in 1.2?**
   - What we know: Tier 1 typically 70-80%, Tier 2 10-15%, Tier 3 5-10%
   - What's unclear: Threshold for "acceptable" overall match rate
   - Recommendation: Flag if total match rate < 70% for investigation

3. **Memory requirements for full-scale run?**
   - What we know: Scripts track memory usage, use chunked operations where possible
   - What's unclear: Peak memory on full 2002-2018 dataset
   - Recommendation: Monitor first run; may need chunking if memory constrained

---

## Sources

### Primary (HIGH confidence)
- Script source code analysis: `src/f1d/sample/*.py` (5 scripts analyzed)
- Configuration: `config/project.yaml`
- Shared utilities: `src/f1d/shared/*.py` (6 key modules reviewed)

### Secondary (MEDIUM confidence)
- Input data inventory: `1_Inputs/` directory structure
- Output directory structure: `4_Outputs/` (currently empty, expected)

### Tertiary (LOW confidence)
- None - all findings based on direct code analysis

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Direct analysis of imports and dependencies
- Architecture: HIGH - All 5 scripts follow consistent pattern
- Dataflow: HIGH - Traced through all transformation steps
- Pitfalls: MEDIUM - Based on code review, not execution experience

**Research date:** 2026-02-14
**Valid until:** 30 days (stable codebase, infrequent changes)
