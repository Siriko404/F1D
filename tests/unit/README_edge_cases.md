# F1D Unit Testing — Edge Cases

## Purpose

This guide documents the specific data edge cases the F1D pipeline must handle, how the architecture protects against them, and how to write tests to verify them.

## 1. Zero-row delta assertion (Panel Builders)

**Edge Case:** A merge in `build_<name>_panel.py` results in duplicate rows (fan-out) because the `file_name` key in the variable builder output is not unique.

**Protection:** Stage 3 panel builders enforce a strict zero-row-delta rule. Before every merge, `len(df)` is captured. After the merge, if `len(df)` changes, the script must `raise ValueError`.

**Test Pattern:**
```python
def test_duplicate_file_name_raises_error():
    # Mock a builder that returns a dataframe with duplicate file_name rows
    # Call the build panel function
    # Assert ValueError is raised with "Row count changed"
```

## 2. Hard-fail on missing required variables (Stage 4)

**Edge Case:** A variable builder runs but returns all-NaNs or fails to attach its column to the panel. The panel is written to disk successfully. A Stage 4 script loads the panel and runs a regression. Statsmodels silently drops all rows with missing variables, running the model on 0 observations or a heavily biased subset.

**Protection:** Stage 4 scripts must define a `required` list of all columns used in the regression formula. Before dropping NAs, they must check `if v not in df.columns` and `raise ValueError` if any are missing.

**Test Pattern:**
```python
def test_missing_required_variable_raises():
    # Mock a panel dataframe missing 'CEO_QA_Uncertainty_pct'
    # Call test_ceo_clarity.prepare_regression_data()
    # Assert ValueError is raised explicitly mentioning the missing variable
```

## 3. CUSIP Alphanumeric Join (IBES / CCM)

**Edge Case:** IBES uses 8-character alphanumeric CUSIPs (e.g. `'87482X10'`). Compustat CCM uses 9-character numeric CUSIPs (e.g. `'000032102'`). An overzealous `.zfill(8)` applied to IBES corrupts alphanumeric values to `087482X1`, preventing the join.

**Protection:** The `EarningsSurpriseBuilder` strips to 8 chars but does **not** z-fill the IBES side. It only zero-fills the CCM side if it is purely numeric.

**Test Pattern:**
```python
def test_alphanumeric_cusip_match():
    # Mock IBES with '87482X10'
    # Mock CCM with '87482X10' or '87482X104'
    # Assert they join successfully and the IBES value is not mangled
```

## 4. Missing Year Files (CRSP / Text)

**Edge Case:** `CRSPEngine` or `TextBuilder` looks for a partitioned file (e.g., `CRSP_DSF_2018_Q4.parquet`) and it doesn't exist on disk.

**Protection:** The engines gracefully catch `FileNotFoundError` for specific year partitions, log a warning, and continue returning `NaN` for that year's calls, rather than crashing the entire pipeline build.

**Test Pattern:**
```python
def test_missing_crsp_year_returns_nans():
    # Mock filesystem where 2018 is missing
    # Assert engine successfully computes 2017 calls
    # Assert 2018 calls are returned with np.nan for StockRet
```

## 5. Reference Entity Normalization (Stage 4)

**Edge Case:** Statsmodels OLS with `C(ceo_id)` picks the alphabetically first CEO as the reference category and assigns them `gamma = 0`. If this raw score is pooled with other regimes and standardized, the zero becomes a meaningful number, biasing the distribution.

**Protection:** `extract_clarity_scores()` identifies reference CEOs by finding `ceo_id`s present in the input dataframe but absent from `model.params`. It tags them `is_reference = True`. `save_outputs()` explicitly filters them out before computing means/stds or writing to disk.

**Test Pattern:**
```python
def test_reference_ceo_is_tagged_and_excluded():
    # Provide tiny mock panel with 3 CEOs
    # Run regression
    # Assert output dataframe has 2 rows and the alphabetically first is omitted
```