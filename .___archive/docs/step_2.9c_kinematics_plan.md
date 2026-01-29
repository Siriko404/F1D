# Implementation Plan - Step 2.9c: Kinematics of Vagueness

## Goal
Implement the "Kinematics of Vagueness" analysis. This step moves beyond static levels (Step 2.9b) to examine how **changes** in CEO Clarity affect **changes** in Market Liquidity within a CEO's tenure. This approach (First Differences) effectively removes time-invariant CEO and Firm fixed effects.

## Methodology
- **Model**: First-Difference Two-Stage Least Squares (FD-2SLS).
- **Core Specification**:
  $$ \Delta Liquidity_{i,t} = \beta_1 \Delta Clarity_{i,t} + \beta_2 \Delta Controls_{i,t} + \theta_t + \Delta \epsilon_{i,t} $$
- **Instrument**: $\Delta ShiftIntensity_{i,t}$ (Change in auditor shift intensity).
- **Unit of Analysis**: Change between consecutive earnings calls for the *same* CEO at the *same* firm.

## Implementation Steps

### 1. Script Creation
**File**: `2_Scripts/2.9c_Kinematics_Liquidity.py`

### 2. Logic Flow
1.  **Load Data**:
    -   Input: `calls_with_liquidity_YYYY.parquet` (merged output from Step 2.9).
    -   Input: `CCCL Instrument` (Shift Intensity).
    -   Input: `Compustat` (Controls).
2.  **Preprocessing**:
    -   Merge all datasets (same as 2.9b).
    -   Sort data by `gvkey`, `ceo_id`, and `start_date`.
3.  **Calculate Differences (Kinematics)**:
    -   Group by `gvkey` and `ceo_id`.
    -   Compute $\Delta X_t = X_t - X_{t-1}$ for:
        -   **Endogenous**: `ClarityCEO`
        -   **Instrument**: `shift_intensity`
        -   **Dependent**: `Amihud`, `Kyle_Lambda`, `Corwin_Schultz` (Use the *level* variables to compute change, or use `Delta_` vars difference of differences?) -> *Decision*: We differenced the *level* variables ($Liquidity_t - Liquidity_{t-1}$).
        -   **Controls**: `Size`, `BM`, `Lev`, `ROA`, `UncPreCEO`, `UncQue`, `NegCall`.
    -   **Validation**: Ensure $t$ and $t-1$ are arguably consecutive (e.g., `days_since_prev_call < 180`).
4.  **Regression (2SLS)**:
    -   **First Stage**: Regress $\Delta Clarity$ on $\Delta Shift$ + $\Delta Controls$ + Year FE.
    -   **Second Stage**: Regress $\Delta Liquidity$ on $\widehat{\Delta Clarity}$ + $\Delta Controls$ + Year FE.

### 3. Verification
-   **Instrument Strength**: Check F-stat of $\Delta Shift$ in First Stage.
-   **Consistency**: Compare results with the "Levels" regression (2.9b). A significant result here suggests that *becoming* more vague hurts liquidity, even if *being* vague (on average) doesn't.

## Output Files
-   `4_Outputs/2.9_LiquidityAnalysis/latest/kinematics_results.txt`: Regression tables.
-   `4_Outputs/2.9_LiquidityAnalysis/latest/kinematics_report.md`: Summary and interpretation.
