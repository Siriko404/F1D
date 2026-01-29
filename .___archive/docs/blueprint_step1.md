# Step 1 Blueprint: Sample Construction (The Manifest)

**Objective**: To deterministically identify the "Universe of Analysis" before processing any large-scale text data. This step outputs a **Manifest** containing the `file_name` and `ceo_id` for every valid observation that meets all sample selection criteria.

**Orchestrator**: `1.0_BuildSampleManifest.py`
This script manages the execution of substeps 1.1 through 1.4, handles logging, and performs sanity checks between steps.

**Core Principles**:
1.  **Variable Preservation**: If a column matches an input column (e.g., `conm` from CCM), reserve the original input name if possible. Do not rename arbitrarily.
2.  **Self-Documentation**: Every substep MUST output a `variable_reference.csv` profiling the dataset (Column Name, Type, Null Count, Description).

---

## Substep 1.1: Metadata Cleaning & Event Filtering
**Script**: `1.1_CleanMetadata.py`

### Logic
1.  **Load Input**: `1_Inputs/Unified-info.parquet`.
2.  **Deduplicate**:
    *   Remove exact duplicate rows.
    *   Resolve `file_name` collisions (prioritize `validation_timestamp`).
3.  **Event Filter**:
    *   Keep only rows where `event_type == '1'` (Earnings Calls).
4.  **Temporal Filter**:
    *   Keep years 2002-2018.
5.  **Output**: `1_1_metadata_cleaned.parquet`
    *   **Artifact**: `1_1_variable_reference.csv`

## Substep 1.2: Entity Resolution (CCM Linking)
**Script**: `1.2_LinkEntities.py`

### Logic
Performs identity resolution to assign `GVKEY` and `PERMNO`.
1.  **Load Input**: `1_1_metadata_cleaned.parquet` + `CCM` + `SIC Codes`.
2.  **Execute 4-Tier Linking**:
    *   *Note*: Matches are performed on subsets that failed previous tiers.
    *   **Tier 1**: `permno` + Date Range (Quality: 100).
    *   **Tier 2**: `cusip` (8-digit) + Date Range (Quality: 90).
    *   **Tier 3**: Fuzzy `company_name` Match (Rapidfuzz).
        *   **Threshold: 92** (Strict).
        *   Quality: 80.
    *   **Tier 4**: `ticker` + Date Range (Quality: 60).
3.  **Industry Assignment**: Map SIC codes to FF12/FF48.
4.  **Filter**: Drop rows where no `gvkey` could be linked.
5.  **Output**: `1_2_metadata_linked.parquet`
    *   **Artifact**: `1_2_variable_reference.csv`

## Substep 1.3: CEO Tenure Map Construction
**Script**: `1.3_BuildTenureMap.py`

### Source Shift: Execucomp
Using `Execucomp` (Compustat) instead of "CEO Dismissal Data" for broader coverage and consistent ID usage.

### Logic
1.  **Load Input**: `1_Inputs/Execucomp/comp_execucomp.parquet`.
2.  **Define Tenure Episodes**:
    *   Group by `gvkey`, `execid`.
    *   **Start Date**: `min(becameceo)`. (Fallback to `joined_co` if null? No, strictly `becameceo`).
    *   **End Date**: `max(leftofc)`.
    *   *Active CEO Logic*: If `leftofc` is NULL, check if CEO is in the latest available fiscal year for that firm. If yes, impute `End Date` = `2025-12-31`.
3.  **Predecessor Linking**:
    *   Sort episodes within `gvkey` by `Start Date`.
    *   **Compute `prev_execid`**: For each episode, assign the `execid` of the immediately preceding episode.
    *   *User Constraint*: "Reserve information of the last ceo". This ensures every confirmed CEO row carries the ID of their predecessor.
4.  **Resolve Overlaps**:
    *   If Episode A ends *after* Episode B starts, assign the Month of B's start to Episode B. (Incoming CEO takes precedence).
5.  **Expand to Monthly**:
    *   Create a monthly panel `(gvkey, year, month)` for the range `[Start Date, End Date]`.
    *   Columns: `ceo_id`, `ceo_name`, `prev_ceo_id`, `prev_ceo_name`.
6.  **Output**: `1_3_tenure_monthly.parquet`
    *   **Artifact**: `1_3_variable_reference.csv`

## Substep 1.4: Manifest Assembly & CEO Filtering
**Script**: `1.4_AssembleManifest.py`

### Logic
1.  **Join**:
    *   Join `1_2_metadata_linked` with `1_3_tenure_monthly` on `(gvkey, year, month)`.
2.  **Filter Unmatched**: Drop rows where join failed.
3.  **Apply Minimum Call Threshold**:
    *   Keep only CEOs with count >= `min_calls` (5).
4.  **Output**: `master_sample_manifest.parquet`
    *   **Artifact**: `1_4_variable_reference.csv`


---

## Directory Structure
```
2_Scripts/
  1_Sample/
    1.0_BuildSampleManifest.py (Orchestrator)
    1.1_CleanMetadata.py
    1.2_LinkEntities.py
    1.3_BuildTenureMap.py
    1.4_AssembleManifest.py
    utils.py (Shared logic)
```
