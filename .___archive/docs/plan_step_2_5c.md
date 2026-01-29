# Implementation Plan - Step 2.5c: Filter CEOs

## Goal Description
Filter out CEOs who have fewer than **5 earnings calls** in total across the entire dataset (2002-2018). This ensures that subsequent analyses have sufficient data points per CEO.

## User Review Required
> [!IMPORTANT]
> **Global Threshold**: The count of 5 calls is calculated **globally** across all years (2002-2018), not per year.
> **Unmatched Calls**: Calls that are filtered out (because their CEO has < 5 calls) will be dropped from the main dataset. We should consider saving them to an audit file or just logging the count.

## Proposed Changes

### Configuration
#### [MODIFY] [config/project.yaml](file:///c:/Users/sinas/OneDrive/Desktop/Projects/Thesis_Bmad/Data/Data/Datasets/Datasets/Data_Processing/F1D/config/project.yaml)
- Add `step_02_5c` configuration.
- Define `min_calls_threshold: 5`.

### New Scripts

#### [NEW] [2.5c_FilterCeos.py](file:///c:/Users/sinas/OneDrive/Desktop/Projects/Thesis_Bmad/Data/Data/Datasets/Datasets/Data_Processing/F1D/2_Scripts/2.5c_FilterCeos.py)
- **Inputs**: `4_Outputs/2.5b_LinkCallsToCeo/latest/f1d_enriched_ceo_YYYY.parquet`
- **Logic**:
    1.  **Pass 1 (Aggregation)**: Iterate through all available years (2002-2018).
        -   Load each file.
        -   Count occurrences of each `ceo_id` (excluding Null/Unmatched).
        -   Aggregate counts into a global `ceo_counts` dictionary/Series.
    2.  **Identify Valid CEOs**: Create a set of `valid_ceo_ids` where `count >= 5`.
    3.  **Pass 2 (Filtering)**: Iterate through all years again.
        -   Load file.
        -   **Split**: Separate rows into `kept_df` (valid CEOs) and `dropped_df` (invalid CEOs).
        -   **Save Kept**: `4_Outputs/2.5c_FilterCeos/{timestamp}/f1d_enriched_ceo_filtered_YYYY.parquet`.
        -   **Save Dropped**: `4_Outputs/2.5c_FilterCeos/{timestamp}/f1d_dropped_ceo_calls_YYYY.parquet`.
    4.  **Reporting**: Log how many CEOs and calls were dropped.

### Documentation
#### [MODIFY] [README.md](file:///c:/Users/sinas/OneDrive/Desktop/Projects/Thesis_Bmad/Data/Data/Datasets/Datasets/Data_Processing/F1D/README.md)
- Add Step 02.5c documentation.

## Verification Plan

### Automated Tests
- **Run Script**: Execute `2.5c_FilterCeos.py`.
- **Verify Counts**: Check that no CEO in the output files has fewer than 5 calls total.
- **Verify Integrity**: Ensure total calls = (Original Total) - (Dropped Calls).
