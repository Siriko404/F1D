# Implementation Plan - Step 2.9: CEO Clarity & Market Liquidity

## Goal
Implement "Step 2.9" to test the relationship between CEO Clarity (Vagueness) and Market Liquidity, as defined in `Proposal Text.txt`. This involves:
1.  **Constructing Liquidity Measures**: Computing changes in Amihud, Kyle's Lambda, and Corwin-Schultz spread around earnings calls.
2.  **Running Regressions**:
    -   **M3-A**: Impact of CEO Clarity on Liquidity (2SLS with CCCL instrument).
    -   **M3-B**: Mediation analysis (Liquidity channel for Valuation).

## Critical Prerequisites
-   **CCCL Shift Intensity Data**: Confirmed at `1_Inputs/CCCL instrument/instrument_shift_intensity_2005_2022.parquet`. Columns: `['sic2', 'year', 'cccl_count', 'total_sales', 'shift_intensity']`.
-   **CRSP Columns**: Confirmed columns `PRC`, `VOL`, `ASKHI`, `BIDLO` in `CRSP_DSF`.

## Implementation Steps

### 1. Update Configuration
Modify `config/project.yaml` to include:
-   `step_09`: Settings for liquidity windows (default `[-5, +5] days`), input paths, and regression specs.

### 2. Build Liquidity Measures (`2.9_BuildLiquidityMeasures.py`)
Create a new script to:
-   Load `calls_with_clarity` (output of Step 2.8).
-   Load `CRSP_DSF` daily data.
-   **Compute Proxies** ([−5, +5] window):
    -   **Amihud**: Average of scaled absolute return / dollar volume.
    -   **Kyle's Lambda**: Regression slope of |Ret| on Volume.
    -   **Corwin-Schultz**: High-Low spread estimator.
-   **Compute Delta**: Level in window (primary) and potential Change vs pre-event baseline.
-   Save to `4_Outputs/2.9_BuildLiquidityMeasures/calls_with_liquidity_YYYY.parquet`.

### 3. Run Analysis (`2.9b_Regression_Liquidity.py`)
Create a new script to:
-   Load `calls_with_liquidity`.
-   Merge **CCCL Instrument** (`shift_intensity`) by `sic2` and `year`.
-   **First Stage (M1)**: `F1D_u ~ shift_intensity + Controls`.
-   **Second Stage (M3-A)**: `Liquidity ~ F1D_u_hat + Controls`.
-   **Mediation (M3-B)**: `LogQ ~ F1D_u + Liquidity + Controls`.
-   Output results to summary reports and text files.

## Verification
-   **Data Validation**: Check descriptive stats of computed Amihud/Corwin measures.
-   **Model Diagnostics**: Check First-Stage F-stat (IV strength).
