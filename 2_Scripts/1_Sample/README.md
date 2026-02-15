# Sample Construction (Step 1)

> **Note:** This folder contains legacy scripts kept for reference. The active versions have been migrated to `src/f1d/sample/` as part of the v6.1 architecture standard. New development should use the `f1d.sample.*` namespace imports.

## Purpose and Scope

This folder contains scripts for constructing the master sample, linking entities (CEOs to firms), and building tenure maps. Sample construction is the **first step** in the F1D pipeline, creating the foundation for all subsequent text processing, financial variable construction, and econometric analyses.

**Status:** LEGACY - Migrated to src/f1d/sample/
**Prerequisites:** Raw input data (metadata, transcripts)
**Outputs:** `4_Outputs/1_Sample/`

---

## Scripts Overview

| Script | Purpose | Key Outputs |
|--------|---------|-------------|
| `1.0_BuildSampleManifest.py` | Main sample construction orchestration | Master sample manifest |
| `1.1_CleanMetadata.py` | Clean and validate event metadata | Cleaned metadata |
| `1.2_LinkEntities.py` | Entity linking (CEO-firm matching) | Linked entities |
| `1.3_BuildTenureMap.py` | Build CEO tenure mapping | Tenure data |
| `1.4_AssembleManifest.py` | Assemble final manifest | Final sample manifest |
| `1.5_Utils.py` | Utility functions for sample construction | Helper functions |

---

## Sample Construction Flow

```
Raw Event Metadata
         |
         v
[1.1] CleanMetadata
         |
         v
Cleaned Metadata
         |
         v
[1.2] LinkEntities (CEO-firm matching)
         |
         v
Linked Entities
         |
         v
[1.3] BuildTenureMap (tenure calculation)
         |
         v
Tenure Maps
         |
         v
[1.4] AssembleManifest (merge all)
         |
         v
Final Sample Manifest (sample_manifest.parquet)
```

---

## Key Variables

### Sample Manifest Columns

| Column | Description | Source |
|--------|-------------|--------|
| gvkey | Firm identifier (Compustat) | Entity linking |
| cusip | CUSIP identifier | Compustat |
| conm | Company name | Compustat |
| ceo_id | Unique CEO identifier | Entity linking |
| ceo_name | CEO name | Entity linking |
| fyear | Fiscal year | Metadata |
| fyrq | Fiscal year quarter | Compustat |
| datadate | Fiscal date | Compustat |
| n_calls | Number of earnings calls | Transcript data |
| start_date | CEO start date | Tenure mapping |
| end_date | CEO end date | Tenure mapping |
| tenure_years | CEO tenure in years | Calculated |

---

## Entity Linking (1.2_LinkEntities.py)

### Purpose

Match CEOs to firms using fuzzy string matching and manual validation.

### Matching Process

1. **Name Extraction:** Extract CEO names from transcript metadata
2. **Fuzzy Matching:** Match CEO names to Execucomp database
3. **Manual Validation:** Review and validate edge cases
4. **Tenure Calculation:** Calculate CEO-firm tenure dates

### Matching Statistics

| Metric | Value |
|--------|-------|
| Total CEOs | ~500 unique CEOs |
| Total Firms | ~1,500 unique firms |
| CEO-Firm Matches | ~2,000 unique pairs |
| Matching Rate | ~85% (fuzzy + manual) |

### Tenure Mapping (1.3_BuildTenureMap.py)

**Purpose:** Create CEO tenure dates for each firm association.

**Tenure Calculation:**
```
tenure_days = min(end_date, current_date) - start_date
tenure_years = tenure_days / 365.25
```

**Tenure Buckets:**
- New: < 2 years
- Medium: 2-5 years
- Established: 5+ years

---

## Input/Output Mapping

### Inputs

| Source | Location | Content |
|--------|----------|---------|
| Event Metadata | `1_Inputs/Unified-info.parquet` | Earnings call metadata |
| Compustat | `1_Inputs/compustat/` | Firm identifiers, dates |
| Execucomp | `1_Inputs/execucomp/` | CEO names, tenure |
| Transcripts | `1_Inputs/transcripts/` | Call text, speakers |

### Outputs

```
4_Outputs/1_Sample/
├── 1.1_CleanMetadata/
│   ├── metadata_cleaned.parquet
│   └── stats.json
├── 1.2_LinkEntities/
│   ├── metadata_linked.parquet
│   └── stats.json
├── 1.3_BuildTenureMap/
│   ├── tenure_map.parquet
│   └── stats.json
└── 1.4_AssembleManifest/
    ├── sample_manifest.parquet
    └── stats.json
```

---

## Sample Construction Details

### Sample Period

| Dimension | Value |
|-----------|-------|
| Start Year | 2002 |
| End Year | 2018 |
| Total Years | 17 years |

### Firm Coverage

| Metric | Value |
|--------|-------|
| Total Firms | ~1,500 firms |
| SIC Coverage | All non-financial sectors |
| Excluded | Financial (SIC 6000-6999), Utilities (SIC 4900-4999) |

### CEO Coverage

| Metric | Value |
|--------|-------|
| Total CEOs | ~500 unique CEOs |
| CEOs per Firm (avg) | 1.3 |
| Single-CEO Firms | ~70% |
| Multi-CEO Firms | ~30% |

### Call Coverage

| Metric | Value |
|--------|-------|
| Total Calls | ~112,000 earnings calls |
| Calls per Year | ~6,500 |
| Calls per Firm (avg) | ~75 |
| QA Segments | ~2/3 of calls |
| Presentation Segments | ~1/3 of calls |

---

## Execution Notes

### Execution Order

**Sequential (must run in order):**

1. **1.0_BuildSampleManifest.py** - Orchestration (runs 1.1-1.4)
2. **1.1_CleanMetadata.py** - Clean and validate metadata
3. **1.2_LinkEntities.py** - Entity linking (CEO-firm matching)
4. **1.3_BuildTenureMap.py** - Tenure calculation
5. **1.4_AssembleManifest.py** - Final assembly

**Note:** Script 1.0 is the main orchestration script that calls 1.1-1.4 in sequence. You can run 1.0 alone, or run 1.1-1.4 individually for debugging.

### Execution Commands

```bash
# Run full sample construction
python 2_Scripts/1_Sample/1.0_BuildSampleManifest.py

# Or run individual scripts (for debugging)
python 2_Scripts/1_Sample/1.1_CleanMetadata.py
python 2_Scripts/1_Sample/1.2_LinkEntities.py
python 2_Scripts/1_Sample/1.3_BuildTenureMap.py
python 2_Scripts/1_Sample/1.4_AssembleManifest.py
```

### Dependencies

- **Event Metadata:** Required for all sample construction
- **Compustat:** Required for firm identifiers and dates
- **Execucomp:** Required for CEO names and tenure
- **Transcripts:** Required for call metadata

---

## Data Validation

### Quality Checks

1. **Missing Values:** No missing GVKEY, CEO_ID, or fyear
2. **Duplicate Records:** No duplicate (gvkey, fyear, ceo_id) triples
3. **Date Consistency:** start_date <= end_date for all tenures
4. **Fiscal Year Alignment:** fyrq matches fiscal year periods

### Validation Scripts

```bash
# Validate sample manifest
python tests/test_sample_manifest.py
```

---

## Relationship to Other Steps

### Downstream Dependencies

All subsequent steps depend on the sample manifest:

| Step | Dependency | Usage |
|------|------------|-------|
| Step 2 (Text) | sample_manifest.parquet | GVKEY-year matching for text measures |
| Step 3 (Financial V1) | sample_manifest.parquet | Firm control construction |
| Step 3 (Financial V2) | sample_manifest.parquet | Hypothesis variable construction |
| Step 3 (Financial V3) | sample_manifest.parquet | PRisk and style variables |
| Step 4 (Econometric) | sample_manifest.parquet | Regression sample construction |

### Sample Consistency

**Critical:** The sample manifest is the single source of truth for all analyses. All subsequent steps MUST use the same (gvkey, fyear) pairs to ensure sample consistency.

**Version Control:**
- Each run creates a new timestamped output directory
- `latest/` symlink points to most recent output
- Downstream scripts use `get_latest_output_dir()` to find manifest

---

## Known Issues

**Entity Linking Ambiguity:**
- Some CEOs have common names (e.g., "John Smith")
- Manual validation required for ambiguous cases
- Matching rate ~85% (reasonable for manual validation)

**Turnover Detection:**
- CEO turnover detected from transcript metadata
- May miss unannounced transitions
- Tenure dates validated against Execucomp when available

---

## References

Entity linking methodology:

- **Fuzzy matching:** RapidFuzz library for approximate string matching
- **Manual validation:** Execucomp database for CEO-firm matching
- **Tenure calculation:** Standard HR tenure measures

---

## Contact and Replication

For replication questions:
- `README.md` (root): Project overview
- `CLAUDE.md`: Coding conventions
- Individual script headers: Implementation details

---

*Last updated: 2026-02-14*
*Phase: 78-documentation-synchronization*
*Version: v1.0 Sample Construction*
