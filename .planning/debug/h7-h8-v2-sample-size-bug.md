---
status: investigating
trigger: "Investigate H7 and H8 V2 failure to replicate V1 sample sizes - Phase 55 is REPLICATION study"
created: 2026-02-06T10:00:00Z
updated: 2026-02-06T10:30:00Z
---

## Current Focus
hypothesis: H7_Illiquidity.parquet is missing Volatility/StockRet controls for 2005-2018, causing H8 to drop all data from those years due to missing data filtering
test: Analyze H7_Illiquidity.parquet control variable completeness by year
expecting: Will find 100% missing Volatility/StockRet for 2005-2018
next_action: Identify why H7 construction failed to include controls for 2005-2018

## Symptoms
expected: V2 should produce IDENTICAL sample sizes and time period as V1 (2002-2018) - this is a REPLICATION
actual: V2 only uses 2002-2004, producing much smaller sample
errors: No explicit errors - silent data truncation
reproduction: Compare V1 vs V2 H7/H8 implementations
timeline: Discovered during Phase 55 when user noticed huge sample discrepancy

## Prior Eliminated (from previous session - re-evaluating)
- Different manifest sources (1.0 vs 1.4): Both have same row count - eliminated
- V2 uses different year_range config: Both have 2002-2018 in CONFIG - eliminated
- H7 raw data issue: H7 has 39,408 rows across 2002-2018 - eliminated
- SDC takeover data limitation: SDC has full 2002-2018 coverage - eliminated

## Evidence

- timestamp: 2026-02-06T00:00:00Z
  checked: H7_Illiquidity.parquet actual file
  found: H7_Illiquidity.parquet has **39,408 rows, year_range=2002-2018, 2,302 firms**
  implication: H7 raw data has full period - filtering must be elsewhere

- timestamp: 2026-02-06T00:00:00Z
  checked: H8_Takeover.parquet actual file
  found: H8_Takeover.parquet has **12,408 rows, year_range=2002-2004, 1,484 firms**
  implication: H8 is filtered to 2002-2004 - need to find WHERE this filtering occurs

- timestamp: 2026-02-06T10:30:00Z
  checked: H7_Illiquidity.parquet control variable missingness by year
  found: **Volatility and StockRet are 100% missing for years 2005-2018**
  - 2002: ~99% missing controls (1% have data)
  - 2003: ~37% missing controls
  - 2004: ~30% missing controls
  - 2005-2018: 100% missing controls
  implication: H8 script filters out rows with >20% missing controls, dropping all 2005-2018 data

- timestamp: 2026-02-06T10:30:00Z
  checked: H8 merge_h8_data() function Step 7 missing data handling
  found: Lines 550-556 filter: `h8_df = h8_df[h8_df['n_missing_controls'] <= max_missing]`
    where max_missing = len(control_cols_in_df) * 0.2 = 2 * 0.2 = 0.4
  implication: With 2 control variables (Volatility, StockRet), NO missing controls allowed

- timestamp: 2026-02-06T10:30:00Z
  checked: H8 log file (3_Logs/3_Financial_V2/2026-02-06_200736_H8.log)
  found: Line 73-75: "Dropped 713 observations with missing IV/DV" then
    "Dropped observations with >20% missing controls" resulting in "Final sample: 12,408"
  implication: 39,408 - 713 = 38,695, then 38,695 -> 12,408 = 26,287 rows dropped by control filter

## Resolution
root_cause: **ROOT CAUSE IDENTIFIED - DATA PIPELINE ISSUE**:
1. The H7 script (3.7_H7IlliquidityVariables.py) loads market_variables expecting Volatility and StockRet
2. The V2 data pipeline (`3_Financial_Features`) directories have INCOMPLETE data:
   - `2026-01-22_224312` (latest): Has Volatility but only 2002-2004 files
   - `2026-01-14_combined`: Has 2002-2018 files but NO Volatility column
3. V1 scripts properly generate market_variables with Volatility, but V2 scripts don't
4. Result: H7_Illiquidity.parquet only has controls for 2002-2004
5. H8 script filters out rows with missing controls, dropping all 2005-2018 data

**UPDATE**: Actually found that `2026-01-22_224312` IS a V1 output (has Volatility) but only has 2002-2004 data because V1 scripts were only run for partial period in V2 context.

fix: **Fix required in 3.7_H7IlliquidityVariables.py**: Calculate Volatility directly from CRSP data within the H7 script instead of relying on external market_variables. This ensures complete 2002-2018 coverage.

Implementation:
1. Calculate annualized stock return volatility from CRSP daily returns in H7 script
2. Merge calculated Volatility with H7 data at firm-year level
3. No dependency on incomplete external market_variables files

verification: TBD
files_changed:
- 2_Scripts/3_Financial_V2/3.7_H7IlliquidityVariables.py
