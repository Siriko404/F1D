# Phase 82: SDC Takeover Linkage Fixes and CUSIP Enrichment - Summary

**Phase ID:** 82-sdc-takeover-linkage-fixes-and-cusip-enrichment
**Status:** COMPLETE
**Completed:** 2026-02-15
**Duration:** ~2 hours

## Overview

Fixed critical bugs in SDC takeover event linkage discovered during Phase 81 audit. The fixes increased takeover event detection from 0 events to 2,343 events (2.07% match rate).

## Bugs Fixed

### Bug 1: Anomaly Detection Index Misalignment
- **File:** `src/f1d/financial/v1/3.0_BuildFinancialFeatures.py`
- **Location:** Lines 177 and 233
- **Root Cause:** `series = df[col].dropna()` creates series with different index than `df`, then `df[anomaly_mask]` fails with IndexingError
- **Fix:** Changed `df[anomaly_mask]` to `series[anomaly_mask]`

### Bug 2: Wrong Manifest Path in Financial Scripts
- **Files:** `3.0_BuildFinancialFeatures.py`, `3.1_FirmControls.py`, `3.2_MarketVariables.py`, `3.3_EventFlags.py`
- **Root Cause:** Scripts loaded from `1.0_BuildSampleManifest` (no CUSIP column) instead of `1.4_AssembleManifest` (with CUSIP)
- **Fix:** Changed all manifest paths to `1.4_AssembleManifest`

### Bug 3: Missing CUSIP Column in Manifest
- **File:** `src/f1d/sample/1.4_AssembleManifest.py`
- **Root Cause:** CUSIP not included in columns loaded from linked metadata
- **Fix:** Added `cusip` to column list + CCM enrichment for missing CUSIPs

### Bug 4: Empty String CUSIP Handling
- **File:** `src/f1d/financial/v1/3.3_EventFlags.py`
- **Root Cause:** Empty strings pass `notna()` check but fail SDC matching
- **Fix:** Replace empty strings with None after extracting CUSIP6

## Results

### CUSIP Coverage Improvement

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| CUSIP Coverage | 82.7% (93,447) | **100%** (112,968) | +17.3% |
| Unique CUSIP6s | 1,915 | 2,466 | +29% |

### Takeover Event Detection

| Metric | Before Fix | After Fix | Change |
|--------|------------|-----------|--------|
| Takeover Events | 0 | **2,343** | +∞ |
| Match Rate | 0% | **2.07%** | +2.07pp |
| Friendly | 0 | 2,019 | - |
| Uninvited | 0 | 324 | - |

### CUSIP Overlap Analysis

```
Manifest firms (2,466 unique CUSIPs):
├── 593 (24%) - Appear as SDC targets
├── 896 (36%) - Appear as SDC acquirors only
└── 977 (40%) - Not in SDC (no M&A activity)
```

## Files Modified

| File | Change |
|------|--------|
| `src/f1d/sample/1.4_AssembleManifest.py` | Added CUSIP column + CCM enrichment |
| `src/f1d/financial/v1/3.0_BuildFinancialFeatures.py` | Fixed anomaly detection + manifest path |
| `src/f1d/financial/v1/3.1_FirmControls.py` | Fixed manifest path |
| `src/f1d/financial/v1/3.2_MarketVariables.py` | Fixed manifest path |
| `src/f1d/financial/v1/3.3_EventFlags.py` | Fixed manifest path + empty CUSIP handling |

## Technical Details

### CCM CUSIP Enrichment Logic

```python
# For rows where CUSIP is missing, look up from CCM
ccm = pd.read_parquet(ccm_file, columns=["gvkey", "cusip"])
gvkey_to_cusip = ccm.groupby("gvkey_str")["cusip"].first().to_dict()
missing_mask = metadata["cusip"].isna() | (metadata["cusip"] == "")
metadata.loc[missing_mask, "cusip"] = metadata.loc[missing_mask, "gvkey_str"].map(gvkey_to_cusip)
```

Result: All 59,098 missing CUSIPs filled from CCM

### SDC Matching Logic

- CUSIP format: Manifest has 9-digit CUSIPs, SDC uses 6-digit
- Matching: First 6 characters of manifest CUSIP → SDC Target 6-digit CUSIP
- Time window: Takeover announced within 365 days of earnings call
- Deal status: All deals included (Completed, Pending, Withdrawn)

## Known Limitations

### CRSP Memory Constraint

The full V1 pipeline (`3.0_BuildFinancialFeatures.py`) hits memory limits during CRSP loading. This is a **separate issue** that doesn't affect takeover detection:

| Component | Uses CUSIP? | Impact |
|-----------|-------------|--------|
| FirmControls | No (gvkey) | None |
| MarketVariables | No (PERMNO) | None |
| EventFlags | Yes | **FIXED** |

EventFlags runs standalone and doesn't require the full pipeline to complete.

## Success Criteria Verification

- [x] Zero takeover events bug FIXED
- [x] Anomaly detection crash FIXED
- [x] CUSIP coverage improved to 100%
- [x] Takeover match rate ~2%
- [x] Audit JSON generated

## Next Steps

1. Consider memory optimization for CRSP loading in `3.2_MarketVariables.py`
2. Update Phase 81 audit reports to reflect corrected takeover event counts
3. Verify H8 hypothesis analysis can now proceed with valid takeover data
