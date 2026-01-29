# Walkthrough: Step 2.9 (Liquidity & Regression)

I have implemented the liquidity channel analysis (Step 2.9) as requested. This involves two new scripts and configuration updates.

## 1. Configuration
Updated `config/project.yaml` to include `step_09` settings, defining the event window ([-5, +5] days) and linking the CCCL instrument.

## 2. Scripts

### `2.9_BuildLiquidityMeasures.py`
**Purpose**: Constructs liquidity proxies around earnings calls.
- **Inputs**: `calls_with_clarity` (Step 2.8 output), `CRSP_DSF`.
- **Measures Computed**:
    - `Amihud`: Daily absolute return divided by dollar volume.
    - `Kyle_Lambda`: Slope of `|Ret|` on `Volume`.
    - `Corwin_Schultz`: High-Low spread estimator.
    - **Deltas**: Difference between Event Window ([-5, +5]) and Baseline ([-35, -6]).

### `2.9b_Regression_Liquidity.py`
**Purpose**: Performs the econometric analysis.
- **Inputs**: `calls_with_liquidity`, `CCCL Instrument`, `Compustat`.
- **First Stage**: `ClarityCEO ~ shift_intensity + Controls`.
- **Second Stage**: `Delta_Amihud ~ Instrumented_Clarity + Controls`.

## 3. Execution Instructions
1.  **Build Data**: The script `2.9_BuildLiquidityMeasures.py` is currently running. Wait for it to complete.
2.  **Run Analysis**:
    ```bash
    python 2_Scripts/2.9b_Regression_Liquidity.py
    ```
3.  **Review Results**: Check `4_Outputs/2.9_LiquidityAnalysis/latest/regression_results_liquidity.txt`.
