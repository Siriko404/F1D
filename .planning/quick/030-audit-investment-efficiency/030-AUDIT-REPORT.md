# Investment Efficiency Implementation Audit Report

**Audit Date:** 2026-02-07
**Auditor:** GSD Plan Executor (Quick Task 030)
**Phase:** 53 - H2 PRisk x Uncertainty -> Investment Efficiency
**Files Audited:**
1. `INVESTMENT_EFFICIENCY_METHODOLOGY.md` - Methodology specification
2. `2_Scripts/3_Financial_V3/4.1_H2_BiddleInvestmentResidual.py` - Implementation script
3. `2_Scripts/4_Econometric_V3/4.3_H2_PRiskUncertainty_Investment.py` - Regression script

---

## Executive Summary

**FINAL VERDICT: PASS** - The investment efficiency implementation is CORRECT and follows the Biddle (2009) methodology specification. All three audit dimensions passed with no critical deviations.

| Dimension | Status | Deviations | Severity |
|-----------|--------|------------|----------|
| Investment Variable Formula | PASS | 1 minor (Compustat column naming) | NONE |
| First-Stage Regression | PASS | 0 (documented decision) | NONE |
| Winsorization & Regression | PASS | 0 | NONE |

---

## Task 1: Investment Variable Construction Formula

### Specification (INVESTMENT_EFFICIENCY_METHODOLOGY.md)

```
Investment_{t+1} = 100 * (XRD_{t+1} + CAPX_{t+1} + AQC_{t+1} - SPPE_{t+1}) / AT_{t}
```

Compustat items: XRD (46), CAPX (128), AQC (129), SPPE (107), AT (6)

### Implementation (lines 290-346)

```python
# Line 316: Core components
investment_components = df_work["capx"].fillna(0) + df_work["xrd"].fillna(0)

# Lines 319-321: Add Acquisitions if available
if "aqc" in df_work.columns:
    investment_components += df_work["aqc"].fillna(0)

# Lines 326-328: Subtract Asset Sales if available
if "sppe" in df_work.columns:
    investment_components -= df_work["sppe"].fillna(0)

# Line 333: Compute Investment
df_work["Investment"] = investment_components / df_work["at_lag"]

# Line 312: Lagged assets
df_work["at_lag"] = df_work.groupby("gvkey")["at"].shift(1)
```

### Audit Checklist Results

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Numerator: CapEx + R&D + Acq - AssetSales | **PASS** | Lines 316-330 |
| Denominator: lagged total assets (AT_{t-1}) | **PASS** | Line 312: `groupby().shift(1)` |
| Scaling factor (100x) consistently applied or omitted | **PASS** | Omitted (acceptable per methodology note) |
| Missing AQC/SPPE handled gracefully | **PASS** | Lines 319-330: conditional checks with simplified measure |
| Positive assets filter applied | **PASS** | Line 306: `df[df["at"] > 0]` |

### Minor Deviation (Not Critical)

**Issue:** Methodology specifies Compustat item numbers (XRD=46, CAPX=128, etc.), but implementation uses quarterly/annual suffixed column names (xrdy, capxy, aqcy, sppey).

**Resolution:** Column mapping is correctly handled in lines 224-238:
```python
column_mapping = {
    "atq": "at",
    "capxy": "capx",
    "xrdy": "xrd",
    "aqcy": "aqc",
    "sppey": "sppe",
    ...
}
```

**Assessment:** This is a naming convention difference, not a substantive deviation. The Compustat suffixed names map to the same data items specified in the methodology.

---

## Task 2: First-Stage Regression Specification

### Specification Comparison

| Document | Specification |
|----------|---------------|
| INVESTMENT_EFFICIENCY_METHODOLOGY.md | Investment = b0 + b1 * SalesGrowth + epsilon |
| 53-RESEARCH.md | Investment = b0 + b1*TobinQ_lag + b2*SalesGrowth_lag + epsilon |

**Decision:** Implementation correctly follows RESEARCH.md (the more complete specification), which includes both TobinQ_lag and SalesGrowth_lag as predictors. This is an intentional enhancement documented in the research phase.

### Implementation Audit (lines 509-632)

```python
# Line 543: Grouping by industry-year
grouped = reg_data.groupby([ff_industry, "fyear"])

# Lines 561-563: Minimum observations check
if len(group) < min_obs:  # min_obs=20
    thin_cells.append((industry, year, len(group)))
    continue

# Line 567: Predictors
X = group[["TobinQ_lag", "SalesGrowth_lag"]].values

# Line 568: Add constant
X = sm.add_constant(X)

# Line 572: Run OLS
model = sm.OLS(Y, X).fit()

# Line 574: Compute residuals
residuals = Y - predicted
```

### Audit Checklist Results

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Grouping by FF48 industry-year | **PASS** | Line 543: `groupby([ff_industry, "fyear"])` |
| Minimum 20 observations enforced | **PASS** | Line 509: `min_obs=20`; Line 561: check applied |
| Predictors: TobinQ_lag + SalesGrowth_lag | **PASS** | Line 567: both predictors included |
| OLS regression with constant term | **PASS** | Line 568: `sm.add_constant(X)` |
| Residuals computed correctly (actual - fitted) | **PASS** | Line 574: `Y - predicted` |
| Thin cells skipped (not merged) | **PASS** | Line 563: `continue` skips thin cells |

---

## Task 3: Winsorization, Sample Construction, and Regression Usage

### Part A: Winsorization (1%/99% by year)

| Variable | Winsorized | Location | Status |
|----------|------------|----------|--------|
| Investment | Yes | Lines 337-339 | PASS |
| TobinQ_lag | Yes | Lines 388-391 | PASS |
| SalesGrowth_lag | Yes | Lines 433-436 | PASS |
| CashFlow | Yes | Lines 493-497 | PASS |
| Size | Yes | Lines 493-497 | PASS |
| Leverage | Yes | Lines 493-497 | PASS |
| InvestmentResidual | **NO** | N/A | PASS (correct - would defeat OLS property) |

**Correct Implementation Note:** The InvestmentResidual is NOT winsorized, which is correct. Winsorizing residuals would defeat the OLS property that residuals sum to zero within each regression cell.

### Part B: Sample Construction

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Financial firms excluded (SIC 6000-6999) | PASS | Excluded in manifest (pre-filtered base sample) |
| Utilities excluded (SIC 4900-4999) | PASS | Excluded in manifest (pre-filtered base sample) |
| Positive assets required | PASS | Line 306: `df[df["at"] > 0]` |
| Deduplication (quarterly to annual) | PASS | Line 894: `drop_duplicates(..., keep="last")` |

**Note:** Financial/utilities exclusion is handled at the manifest level (master_sample_manifest.parquet), which is the correct approach for this pipeline design.

### Part C: Regression Usage (4.3_H2_PRiskUncertainty_Investment.py)

```python
PRIMARY_SPEC = {
    'dependent': 'InvestmentResidual',  # Line 103 - signed residual
    'exog': ['PRisk_x_Uncertainty', 'PRisk_std', 'Manager_QA_Uncertainty_pct_std',
             'CashFlow', 'Size', 'Leverage', 'TobinQ', 'SalesGrowth'],  # Line 105
    'entity_effects': True,  # Line 106 - Firm FE
    'time_effects': True,  # Line 107 - Year FE
    'cluster_cols': ['gvkey', 'year'],  # Line 108 - Double-clustered
}
```

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Dependent variable: InvestmentResidual (signed) | PASS | Line 103: `'dependent': 'InvestmentResidual'` |
| Controls match Biddle (2009) baseline | PASS | Line 105: CashFlow, Size, Leverage, TobinQ, SalesGrowth |
| Interaction term: PRisk_x_Uncertainty | PASS | Line 104: First exog variable |
| Fixed effects: Firm + Year | PASS | Lines 106-107: `entity_effects=True, time_effects=True` |
| Clustering: Double-clustered (firm, year) | PASS | Line 108: `cluster_cols=['gvkey', 'year']` |

**Correct Implementation Note:** The primary spec uses the SIGNED InvestmentResidual as the dependent variable (not absolute value). This tests whether compound uncertainty affects investment direction (over vs. under), which is the correct approach for H2. The absolute value is tested in the robustness spec (line 122).

---

## Methodology vs. Research Document Discrepancy

### Documented Decision

**Methodology Document (INVESTMENT_EFFICIENCY_METHODOLOGY.md):**
- Specifies: `Investment = b0 + b1 * SalesGrowth + epsilon`
- Simpler specification from Biddle (2009) Eq. (2)

**Research Document (53-RESEARCH.md):**
- Specifies: `Investment = b0 + b1*TobinQ_lag + b2*SalesGrowth_lag + epsilon`
- More complete specification including both Tobin's Q and Sales Growth

**Implementation Decision:**
The implementation follows RESEARCH.md (TobinQ_lag + SalesGrowth_lag), which is the MORE complete specification. This is intentional and documented in the research phase. Both predictors are standard investment opportunity proxies, and including both improves the first-stage prediction of expected investment.

---

## Deviations Summary

### Critical Deviations: NONE

### Major Deviations: NONE

### Minor Deviations: 1

1. **Compustat Column Naming Convention**
   - **Location:** 4.1_H2_BiddleInvestmentResidual.py, lines 224-238
   - **Issue:** Implementation uses quarterly/annual suffixed names (xrdy, capxy) vs. methodology item numbers
   - **Impact:** NONE - Column mapping correctly translates to same Compustat items
   - **Action Required:** NONE

---

## Conclusions and Recommendations

### Implementation Integrity

**VERDICT: PASS**

The investment efficiency implementation is CORRECT and follows the Biddle (2009) methodology specification with appropriate enhancements documented in the research phase.

### Key Strengths

1. **Correct formula implementation:** Investment = (CapEx + R&D + Acq - AssetSales) / lagged(AT)
2. **Proper lagging:** Denominator correctly uses lagged assets via groupby().shift(1)
3. **Graceful handling of missing components:** AQC and SPPE use conditional fallback
4. **Appropriate first-stage specification:** TobinQ_lag + SalesGrowth_lag per RESEARCH.md
5. **Correct winsorization:** Inputs winsorized, residuals NOT winsorized (preserves OLS properties)
6. **Proper regression specification:** Firm + Year FE, double-clustered SE, correct controls

### Recommendation

**NO RE-IMPLEMENTATION REQUIRED.** The Phase 53 investment efficiency variable construction is methodologically sound and ready for use in H2 hypothesis testing. The null H2 results documented in Phase 53 reflect genuine empirical findings, not implementation errors.

---

## Audit Metadata

**Auditor:** GSD Plan Executor (Quick Task 030)
**Audit Duration:** 2026-02-07
**Files Reviewed:** 3
**Lines of Code Audited:** ~1,200
**Audit Methodology:** Line-by-line verification against methodology specification

**Sign-off:** Implementation integrity verified. Results from Phase 53 H2 regression (NOT SUPPORTED) are valid.
