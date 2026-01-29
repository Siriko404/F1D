# Harmonization Map: Liquidity (2.9) & Takeover (2.10)

This document maps the exact logic, inputs, and models for each script under the harmonized plan.

## Global Rules (All Analysis)
1.  **Linguistic Variable**: Use **ONLY** `MaPresUnc_pct` (Presentation Uncertainty). Drop `MaQaUnc_pct`.
2.  **Peer Comparison**: Use **FF48 Industry Codes** (`ff48_code`) for all peer-relative calculations.
3.  **Surprise Terms**: Calculate `F1`, `F1_PO`, `F1_HO`, `F1_POxHO`. **NO** velocity/acceleration (`_v`, `_a`) for these terms.
4.  **Kinematics**: Calculate differences `D1`, `D2`, `D3` (1st, 2nd, 3rd derivs) for `MaPresUnc_pct` within CEO tenure.

---

## 1. Script: `2.9b_Regression_Liquidity.py`
**Goal**: Analyze the impact of CEO Clarity on Market Liquidity (Levels).

### Inputs
*   `MaPresUnc_pct`
*   `ClarityCEO` (Fixed Effect)
*   `ff48_code`
*   Liquidity Measures: `Amihud`, `QuotedSpread`, `EffectiveSpread`
*   Controls: `Size`, `BM`, `Lev`, `ROA`

### Transformations
1.  **Add Surprises**: Calculate `F1_PO`, `F1_HO`, `F1_POxHO` for `MaPresUnc_pct`.

### Models (OLS)
*   **Dependent**: `Change_Illiquidity` (e.g., $\Delta Amihud$)
*   **Independent**:
    *   `ClarityCEO`
    *   `MaPresUnc_pct`
    *   `F1_PO` (Peer Surprise)
    *   `F1_HO` (History Surprise)
    *   `F1_POxHO` (Interaction)
    *   Controls (`Size`, `BM`...)

---

## 2. Script: `2.9c_Kinematics_Liquidity.py`
**Goal**: Analyze how *changes* in clarity affect *changes* in liquidity (Kinematics).

### Inputs
*   `MaPresUnc_pct`
*   Liquidity Measures
*   **NO** `ClarityCEO` (Time-invariant, drops out in differencing)

### Transformations
1.  **Group by CEO_ID**: Focus on within-CEO variation.
2.  **Calculate Kinematics (Differences)**:
    *   `D1_MaPresUnc_pct` ($t - t_{-1}$)
    *   `D2_MaPresUnc_pct` ($t - t_{-2}$)
    *   `D3_MaPresUnc_pct` ($t - t_{-3}$)
    *   (Same differences for Liquidity Dependent Vars)

### Models (OLS on Differences)
*   **Dependent**: `D1_Amihud`, `D2_Amihud`, `D3_Amihud`
*   **Independent**:
    *   `D1_MaPresUnc_pct`
    *   `D2_MaPresUnc_pct`
    *   `D3_MaPresUnc_pct`
    *   (Run separate regressions for each Difference Order 1, 2, 3)

---

## 3. Script: `2.9d_Extended_Liquidity.py`
**Goal**: Advanced analysis using Instrumental Variables (IV) and "Uncertainty Residuals".

### Inputs
*   `MaPresUnc_pct`
*   `ClarityCEO`
*   `ff48_code`
*   Instrument: `shift_intensity` (CCCL)

### Transformations
1.  **Add Surprises**: `F1_PO`, `F1_HO`, `F1_POxHO`.
2.  **Calculate UncResid**: Use IV approach to isolate "Unexpected Uncertainty".
3.  **Add Kinematics**: `D1_MaPresUnc_pct`.

### Models
#### A. Levels (IV/OLS)
*   **Dependent**: `Change_Illiquidity`
*   **Independent**:
    *   `ClarityCEO`
    *   `Instrumented(MaPresUnc_pct)` (or OLS `MaPresUnc_pct`)
    *   `F1_PO`, `F1_HO`, `F1_POxHO`
    *   `UncResid`

#### B. Kinematics (IV/OLS)
*   **Dependent**: `D1_Illiquidity`
*   **Independent**:
    *   `D1_MaPresUnc_pct`
    *   (Note: IV is generally less valid for kinematics/differences)

---

## 4. Script: `2.10_Takeover_Hazards.py`
**Goal**: Analyze how clarity features predict Takeover Risk.

### Inputs
*   `MaPresUnc_pct`
*   `ClarityCEO`
*   `ff48_code`

### Transformations
1.  **Add Surprises**: Calculate `F1_PO`, `F1_HO`, `F1_POxHO` using `ff48_code`.
2.  **Add Kinematics**: Calculate `D1_MaPresUnc_pct`, `D2_...`, `D3_...`.

### Models (Cox Proportional Hazards)
Predicting event: `Takeover_Target` (All / Friendly / Uninvited)

*   **Covariates**:
    *   **Baseline**: `ClarityCEO` (Long-term trait)
    *   **Current State**: `MaPresUnc_pct`
    *   **Surprises**: `F1_PO`, `F1_HO`, `F1_POxHO` (Is this unusual?)
    *   **Dynamics**: `D1_MaPresUnc_pct`, `D2_MaPresUnc_pct` (Is it getting worse?)
    *   **Controls**: `Size`, `BM`, `Lev`, `ROA`, `AbnormRet`...

---

## Implementation Checklist Summary

| Feature | 2.9b (Levels) | 2.9c (Kinematics) | 2.9d (IV/Ext) | 2.10 (Hazards) |
|:---|:---:|:---:|:---:|:---:|
| **Base Var** | `MaPres` | `MaPres` | `MaPres` | `MaPres` |
| **Drop QA** | ✅ | ✅ | ✅ | ✅ |
| **Use FF48** | ✅ | N/A | ✅ | ✅ |
| **Surprises (PO/HO)** | ✅ **Add** | ❌ | ✅ **Add** | ✅ **Add** |
| **Kinematics (D1..)** | ❌ | ✅ **Keep** | ✅ **Add** | ✅ **Add** |
| **Surprise Kin. (_v)**| ❌ **No** | ❌ **No** | ❌ **No** | ❌ **Remove** |
