# Step 2.7 Data Coverage Analysis

**Date**: 2025-12-04
**Status**: Step 2.7 completed successfully, investigating data coverage

---

## Current Status

### Step 2.7: Build Financial Controls - COMPLETED ✓

**Execution Details:**
- **Runtime**: 193.7 seconds (~3.2 minutes)
- **Total calls processed**: 127,782 calls (2002-2018)
- **Output location**: `4_Outputs/2.7_BuildFinancialControls/2025-12-04_163409/`

**Key Optimizations Applied:**
1. **Chunked processing**: Process 100 stocks at a time to avoid memory issues
2. **Binary search for market returns**: O(n log m) instead of O(n×m) cross joins
3. **Vectorized operations**: Pandas merges instead of row-by-row loops

**Bug Fixes Applied:**
1. Fixed LPERMNO propagation from Step 2.5 (now 100% coverage)
2. Fixed Unicode encoding errors (→, ≥, ✓ characters)
3. Fixed numpy/pandas type compatibility in binary search

---

## Data Coverage Results

### Overall Coverage Summary

| Metric | Coverage | Count |
|--------|----------|-------|
| **Total calls** | 100.0% | 127,782 |
| **LPERMNO available** | 100.0% | 127,782 |
| **prev_call_date available** | 98.3% | 125,644 |
| **StockRet computed** | 65.1% | 83,156 |
| **MarketRet computed** | 68.1% | 87,040 |

### Missing Data Breakdown

**Calls without StockRet: 44,626 (34.9%)**

Breaking down the 44,626 calls missing StockRet:
- **2,138 calls** (1.7%): No previous call date (first-time calls for each firm)
- **42,488 calls** (33.2%): Have both prev_call_date AND LPERMNO, but 0 trading days

---

## Investigation: Why 42,488 calls have 0 trading days?

### Discovery 1: All 42,488 calls have exactly 0 trading days

Even though these calls have:
- ✓ Valid LPERMNO (100% coverage from CCM)
- ✓ Valid previous call date
- ✓ Sufficient calendar gap (13-160 days between calls)

**Example cases:**
```
file_name: 666892_T - 96 calendar days between calls → 0 trading days
file_name: 646095_T - 30 calendar days between calls → 0 trading days
file_name: 671629_T - 13 calendar days between calls → 0 trading days
file_name: 644799_T - 160 calendar days between calls → 0 trading days
file_name: 665973_T - 91 calendar days between calls → 0 trading days
```

### Configuration Check

**Return window parameters** (from `config/project.yaml`):
```yaml
days_after_prev_call: 5
days_before_current_call: 5
min_trading_days: 20
```

**Window calculation:**
```
window_start = prev_call_date + 5 days
window_end = current_call_date - 5 days
Minimum calendar gap needed = 11 days
```

**Expected behavior:**
- 13 days apart → 3 day window (valid, but < 20 trading days needed)
- 30 days apart → 20 day window (valid, meets minimum)
- 91 days apart → 81 day window (valid, should have plenty of trading days)

**Conclusion**: Windows should be valid based on calendar gaps. The issue must be elsewhere.

---

## Hypotheses Under Investigation

### Hypothesis 1: CRSP PERMNO matching issue
**Symptom**: 0 trading days despite valid windows
**Possible cause**: LPERMNO from CCM may not match PERMNO in CRSP

**Test in progress**: Loading a sample call and checking:
1. Does the LPERMNO exist in CRSP at all?
2. Is there CRSP data during the return window dates?
3. Is there a data type mismatch preventing the merge?

### Hypothesis 2: Date filtering issue
**Possible cause**: Window dates may be calculated incorrectly or filtered out

### Hypothesis 3: CRSP data gaps
**Possible cause**: Stock may be delisted, trading halted, or missing CRSP coverage during window

---

## Current Investigation Step

**Running diagnostic script** (process ID: 45faec):
```python
# 1. Load a sample call with 0 trading days
# 2. Calculate its return window
# 3. Check if LPERMNO exists in CRSP
# 4. Check if CRSP has data during the window dates
# 5. Identify the root cause
```

**Expected output will show:**
- Whether LPERMNO exists in CRSP
- Date range of CRSP data for that PERMNO
- Number of CRSP records in the return window
- Root cause of 0 trading days

---

## Code Location Reference

**Optimized return computation**: `2_Scripts/compute_returns_vectorized.py`

**Key sections:**
- Lines 64-133: Chunked stock return processing
- Lines 135-180: Binary search market return processing
- Line 61: LPERMNO type conversion to int
- Lines 96-104: Window date filtering

**Original script**: `2_Scripts/2.7_BuildFinancialControls.py`
- Line 731: Calls `compute_stock_returns_vectorized()`
- Lines 50-66: Dual-write logging function

---

## Next Steps

1. **Complete diagnostic** - Determine why 42,488 calls have 0 trading days
2. **Fix root cause** - Implement solution based on findings
3. **Re-run Step 2.7** if changes are needed
4. **Verify coverage improvement**
5. **Proceed to Step 2.8** - Estimate CEO Clarity

---

## Performance Metrics

**Step 2.7 performance breakdown:**
- Loading call data: ~5 seconds
- Loading CRSP (30M records): ~120 seconds
- Computing stock returns (2,102 stocks, chunked): ~30 seconds
- Computing market returns (113,444 calls, binary search): ~20 seconds
- Data validation & saving: ~18 seconds

**Total**: 193.7 seconds

---

## Expected vs Actual Coverage

**Expected after LPERMNO bug fix:**
- ~99% coverage (all calls with CCM linkage + previous call)
- Only missing: first-time calls (1.7%)

**Actual:**
- 65.1% StockRet coverage
- 68.1% MarketRet coverage
- Gap: 33.2% of calls with valid inputs but 0 trading days

**Coverage gap to explain**: 42,488 calls

---

## ROOT CAUSE IDENTIFIED ✓

**Date**: 2025-12-04 16:43

### Bug: CRSP date column type mismatch

**Sample Call Analysis (AAR CORP, PERMNO 54594):**
```
Return window: 2015-03-01 to 2015-03-26 (25 calendar days)
CRSP records in window: 19 trading days (all with valid returns)
Step 2.7 reported: 0 trading days
```

**The Bug (Line 103 in 2.7_ComputeReturnsVectorized.py):**
```python
# This comparison fails because date types dont match!
merged = merged[(merged['date'] >= merged['window_start']) &
                (merged['date'] <= merged['window_end'])]
```

- `merged['date']`: **STRING** (from CRSP parquet files)
- `merged['window_start']`: **pandas Timestamp**
- `merged['window_end']`: **pandas Timestamp**

**Result**: String vs Timestamp comparison fails silently, drops all 42,488 records

**The Fix (Added Line 63):**
```python
# CRITICAL: Convert date to datetime (CRSP dates are strings!)
crsp_clean['date'] = pd.to_datetime(crsp_clean['date'])
```

**Status**: Bug fixed, re-running Step 2.7...
