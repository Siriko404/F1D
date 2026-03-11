# H15 Variable Mapping: Spec → F1D Pipeline Implementation

**Generated:** 2026-03-10
**Purpose:** Map H15 spec variable names to existing F1D pipeline implementations, flagging gaps requiring new development.

---

## Overview

This document maps the H15 hypothesis specification ("Real-Time Abnormal CEO Q&A Hedging and Subsequent Downside Operating Shortfalls") to the existing F1D pipeline variable implementations.

**Key Findings:**
- **Already Implemented:** 21 variables
- **Needs New Implementation:** 12 variables (flagged with 🆕)
- **Needs Modification:** 3 variables (flagged with ⚠️)

---

## 1. Main Explanatory Variable

### `AbnHedgeCEO_{i,t}`: Real-time Abnormal CEO Q&A Hedging

| Spec Variable | F1D Implementation | Status | Notes |
|--------------|-------------------|--------|-------|
| `HedgeAnsCEO_{i,t}` | `CEO_QA_Uncertainty_pct` | ✅ EXISTS | CEO Q&A uncertainty word fraction × 100 |
| `HedgePreCEO_{i,t}` | `CEO_Pres_Uncertainty_pct` | ✅ EXISTS | CEO presentation uncertainty word fraction × 100 |
| `HedgeQue_{i,t}` | `Analyst_QA_Uncertainty_pct` | ✅ EXISTS | Analyst question uncertainty word fraction × 100 |
| `ToneCall_{i,t}` | `NegativeSentiment` (Entire_All_Negative_pct) | ✅ EXISTS | Overall call negativity |
| `AbnHedgeCEO_{i,t}` (residual) | — | 🆕 NEW | Requires **recursive first-stage regression** (expanding window) |

**Recursive Construction Rule (NOT YET IMPLEMENTED):**
```
HedgeAnsCEO_{i,t} = α_t + θ̂_{CEO(i),t-1} + β₁·HedgePreCEO + β₂·HedgeQue + β₃·ToneCall + β₄·Q&AControls + β₅·CurrentFundamentals + u_{i,t}
AbnHedgeCEO_{i,t} = û_{i,t}
```

Where `θ̂_{CEO(i),t-1}` is the CEO-specific expected-style term estimated using **only calls observed up to quarter (t-1)** (expanding window).

---

## 2. Main Dependent Variables

### Downside Operating Outcomes (OCF-based)

| Spec Variable | F1D Implementation | Status | Notes |
|--------------|-------------------|--------|-------|
| `NegOCFAny4_{i,t}` | — | 🆕 NEW | Indicator: ≥1 negative OCF quarter in t+1 to t+4 |
| `WorstOCF4_{i,t}` | — | 🆕 NEW | Minimum quarterly OCF over t+1 to t+4, scaled by assets |
| `MeanOCF4_{i,t}` | — | 🆕 NEW | Average quarterly OCF over t+1 to t+4, scaled by assets |

**Base Data Source:** `CashFlow` builder uses `oancfy / avg_assets` from Compustat.
**New Implementation Required:** Forward-looking OCF aggregation at 4-quarter horizon.

---

## 3. Secondary Downside Outcome

| Spec Variable | F1D Implementation | Status | Notes |
|--------------|-------------------|--------|-------|
| `LPM0_OCF4_{i,t}` | — | 🆕 NEW | Lower partial moment of future OCF around zero: (1/4)·Σ max(0, -OCF_{t+h})² |

**Note:** This is optional and secondary per spec.

---

## 4. Mechanism Variable

### `PostDispersion_{i,t}`: Post-call Analyst Forecast Dispersion

| Spec Variable | F1D Implementation | Status | Notes |
|--------------|-------------------|--------|-------|
| `PostDispersion_{i,t}` | — | 🆕 NEW | Analyst forecast dispersion measured shortly **after** the call |

**Related Existing:**
- `DispersionLead` (IBES-based) — exists but timing is different
- `PriorDispersion` (IBES-based) — exists but timing is different
- `_ibes_engine.py` computes `dispersion = STDEV / |MEANEST|` per gvkey-statpers

**New Implementation Required:** Match post-call analyst dispersion using `statpers` dates **after** the call's `start_date`.

---

## 5. Secondary Continuation Outcomes

| Spec Variable | F1D Implementation | Status | Notes |
|--------------|-------------------|--------|-------|
| `SurpriseNext_{i,t}` | — | 🆕 NEW | Negative earnings surprise indicator in next period |
| `GuidanceMissNext_{i,t}` | — | 🆕 NEW | Indicator for missing previously issued guidance |

**Related Existing:**
- `SurpDec` — earnings surprise decile (-5..+5), exists but is contemporaneous
- No guidance data currently in pipeline

---

## 6. Core Call-Language Controls

### A. Call-Language Controls

| Spec Variable | F1D Implementation | Status | Notes |
|--------------|-------------------|--------|-------|
| `HedgePreCEO_{i,t}` | `CEO_Pres_Uncertainty_pct` | ✅ EXISTS | CEO presentation uncertainty |
| `HedgeQue_{i,t}` | `Analyst_QA_Uncertainty_pct` | ✅ EXISTS | Analyst question uncertainty |
| `ToneCall_{i,t}` | `NegativeSentiment` / `Entire_All_Negative_pct` | ✅ EXISTS | Overall call negativity |
| `ToneChange_{i,t}` | — | 🆕 NEW | Change in negativity relative to prior call |
| `WordsCall_{i,t}` | — | ⚠️ PARTIAL | Not currently exposed as standalone variable |
| `NumCall_{i,t}` | — | 🆕 NEW | Numerical-density measure |
| `ComplexCall_{i,t}` | — | 🆕 NEW | Sentence length / complexity proxy |

### B. Alternative Q&A Friction Controls

| Spec Variable | F1D Implementation | Status | Notes |
|--------------|-------------------|--------|-------|
| `Scriptedness_{i,t}` | — | 🆕 NEW | Similarity of answers to prepared language |
| `NonAnswer_{i,t}` | — | 🆕 NEW | Fraction of answers classified as nonanswers |
| `Avoidance_{i,t}` | — | 🆕 NEW | Answer-avoidance measure |
| `QuestionNegativity_{i,t}` | `Analyst_QA_Negative_pct` | ✅ EXISTS | Analyst question negativity |
| `QuestionDifficulty_{i,t}` | — | 🆕 NEW | Proxy for questioning pressure/complexity |

### C. Current-Quarter Disclosed Fundamentals

| Spec Variable | F1D Implementation | Status | Notes |
|--------------|-------------------|--------|-------|
| Current OCF / assets | `CashFlow` | ✅ EXISTS | oancfy / avg_assets |
| Revenue growth | `SalesGrowth` | ✅ EXISTS | via `_compustat_engine.py` |
| Gross/Operating margin | — | ⚠️ PARTIAL | ROA exists but not gross margin |
| Accruals / working-capital pressure | — | 🆕 NEW | Not currently implemented |
| Cash holdings | `CashHoldings` | ✅ EXISTS | cheq / atq |
| Leverage | `Lev` | ✅ EXISTS | (dlcq + dlttq) / atq |
| Recent return volatility | `Volatility` | ✅ EXISTS | via `_crsp_engine.py` |
| Earnings surprise | `SurpDec` | ✅ EXISTS | Decile -5..+5 |
| Guidance indicator | — | 🆕 NEW | Not currently in pipeline |
| Size | `Size` | ✅ EXISTS | ln(atq) |
| Market-to-book / Tobin's Q | `TobinsQ` or `BM` | ✅ EXISTS | Both available |
| Industry demand controls | — | 🆕 NEW | Not currently in pipeline |

---

## 7. Residual/Clarity Measures (Related)

| Spec Concept | F1D Implementation | Status | Notes |
|--------------|-------------------|--------|-------|
| CEO clarity residual | `CEO_Clarity_Residual` | ✅ EXISTS | Residual from H0.3 regression |
| Manager clarity residual | `Manager_Clarity_Residual` | ✅ EXISTS | Residual from H0.3 regression |
| CEO fixed effect (clarity) | `ClarityCEO` | ✅ EXISTS | From `run_h0_2_ceo_clarity.py` output |

**Important Distinction:** H15's `AbnHedgeCEO` is **NOT** the same as `CEO_Clarity_Residual`. H15 requires:
1. **Recursive** (real-time) estimation, not full-sample
2. **Explicit controls** for prepared remarks, analyst questions, tone, etc.
3. The residual from a **predictive** first stage

---

## Summary: Implementation Status

### ✅ Already Implemented (21 variables)

| Category | Variables |
|----------|-----------|
| **Linguistic (CEO)** | `CEO_QA_Uncertainty_pct`, `CEO_Pres_Uncertainty_pct`, `CEO_QA_Negative_pct` |
| **Linguistic (Manager)** | `Manager_QA_Uncertainty_pct`, `Manager_Pres_Uncertainty_pct` |
| **Linguistic (Analyst)** | `Analyst_QA_Uncertainty_pct`, `Analyst_QA_Negative_pct` |
| **Sentiment** | `NegativeSentiment` (Entire_All_Negative_pct) |
| **Financial** | `Size`, `Lev`, `ROA`, `TobinsQ`, `BM`, `CashHoldings`, `CashFlow`, `SalesGrowth`, `Volatility` |
| **Earnings** | `SurpDec` |
| **Clarity Residuals** | `CEO_Clarity_Residual`, `Manager_Clarity_Residual` |
| **CEO FE** | `ClarityCEO` |

### 🆕 Needs New Implementation (12 variables)

| Priority | Variable | Description |
|----------|----------|-------------|
| **HIGH** | `AbnHedgeCEO_{i,t}` | Recursive first-stage residual (core regressor) |
| **HIGH** | `NegOCFAny4_{i,t}` | Forward OCF negative indicator |
| **HIGH** | `WorstOCF4_{i,t}` | Forward minimum OCF |
| **HIGH** | `MeanOCF4_{i,t}` | Forward mean OCF |
| **HIGH** | `PostDispersion_{i,t}` | Post-call analyst dispersion |
| **MEDIUM** | `LPM0_OCF4_{i,t}` | Lower partial moment (secondary) |
| **MEDIUM** | `ToneChange_{i,t}` | Change in tone vs prior call |
| **MEDIUM** | `SurpriseNext_{i,t}` | Next-period negative surprise |
| **MEDIUM** | `GuidanceMissNext_{i,t}` | Next-period guidance miss |
| **LOW** | `Scriptedness_{i,t}` | Answer similarity to prep |
| **LOW** | `NonAnswer_{i,t}` | Nonanswer fraction |
| **LOW** | `Avoidance_{i,t}` | Answer avoidance measure |

### ⚠️ Needs Modification/Extension (3 variables)

| Variable | Issue |
|----------|-------|
| `WordsCall` | Token counts exist in Stage 2 but not exposed as variable |
| `NumCall` | Numerical density could be derived from existing tokens |
| `ComplexCall` | Sentence length could be derived but not computed |

---

## Model Specifications Mapping

### Model 1: Recursive First-Stage Construction

**Spec:**
```
HedgeAnsCEO_{i,t} = α_t + θ̂_{CEO(i),t-1} + β₁·HedgePreCEO + β₂·HedgeQue + β₃·ToneCall + β₄·Q&AControls + β₅·CurrentFundamentals + u_{i,t}
AbnHedgeCEO_{i,t} = û_{i,t}
```

**F1D Variables Mapping:**
- LHS: `CEO_QA_Uncertainty_pct` ✅
- RHS: `CEO_Pres_Uncertainty_pct` ✅, `Analyst_QA_Uncertainty_pct` ✅, `NegativeSentiment` ✅
- Fundamentals: `Size` ✅, `Lev` ✅, `ROA` ✅, `TobinsQ` ✅, `CashHoldings` ✅, `SurpDec` ✅

**New Code Required:** Recursive expanding-window OLS with CEO-specific benchmark estimation.

### Model 2: Main Predictive Downside Specification

**Spec:**
```
Y_{i,t→t+4} = α + β·AbnHedgeCEO_{i,t} + Γ'·CurrentFundamentals + Λ'·CallControls + μ_i + τ_t + ε_{i,t}
```

**F1D Variables Mapping:**
- `AbnHedgeCEO` 🆕 NEW (requires Model 1 first)
- Outcomes `NegOCFAny4`, `WorstOCF4`, `MeanOCF4` 🆕 NEW
- Controls: All fundamentals ✅

### Model 3: Horse-Race Specification

**Spec:** Adds `Scriptedness`, `NonAnswer`, `Avoidance`, `QuestionNegativity`

**F1D Variables Mapping:**
- `QuestionNegativity` → `Analyst_QA_Negative_pct` ✅
- Others 🆕 NEW

### Model 4: Mechanism Specification

**Spec:**
```
PostDispersion_{i,t} = α + β·AbnHedgeCEO_{i,t} + Γ'·X_{i,t} + μ_i + τ_t + ε_{i,t}
```

**F1D Variables Mapping:**
- `PostDispersion` 🆕 NEW (requires matching IBES dispersion to post-call dates)
- `AbnHedgeCEO` 🆕 NEW (requires Model 1)

### Model 5: Beyond-Dispersion Specification

Combines Model 2 + `PostDispersion` control.

---

## Data Dependencies

### Existing Data Sources

| Source | Variables |
|--------|-----------|
| Compustat (`_compustat_engine.py`) | Size, Lev, ROA, TobinsQ, BM, CashHoldings, CashFlow, SalesGrowth, EPS_Growth |
| CRSP (`_crsp_engine.py`) | StockRet, MarketRet, Volatility |
| IBES (`_ibes_engine.py`) | SurpDec, Dispersion (raw), earnings_surprise_ratio |
| Linguistic (`_linguistic_engine.py`) | All uncertainty, tone, modal variables |
| Clarity Residuals (`_clarity_residual_engine.py`) | CEO_Clarity_Residual, Manager_Clarity_Residual |

### New Data Sources Needed

| Source | Variables | Notes |
|--------|-----------|-------|
| Compustat (extended) | OANCFY (already exists), forward quarters | Need to build forward OCF variables |
| IBES (extended usage) | Post-call dispersion | Need date-matching logic |
| Guidance data | Guidance indicator, actuals vs guidance | May require new data source |

---

## Recommended Implementation Order

1. **Phase 1: Core Variables**
   - Implement forward OCF variables (`NegOCFAny4`, `WorstOCF4`, `MeanOCF4`)
   - Implement `PostDispersion` using existing IBES data

2. **Phase 2: First-Stage Construction**
   - Build recursive first-stage model for `AbnHedgeCEO`
   - Create new builder: `AbnormalHedgeBuilder`

3. **Phase 3: Panel Construction**
   - Build `build_h15_downside_panel.py`
   - Merge all variables to call-level panel

4. **Phase 4: Hypothesis Tests**
   - Implement `run_h15_downside.py` for Models 1-5
   - Generate LaTeX tables per spec

5. **Phase 5: Friction Controls (Optional)**
   - Implement `Scriptedness`, `NonAnswer`, `Avoidance` if needed for horse-race tests

---

## Appendix: Full Variable Crosswalk Table

| H15 Spec Name | F1D Pipeline Name | Type | Status |
|---------------|-------------------|------|--------|
| `AbnHedgeCEO` | — | Residual | 🆕 NEW |
| `HedgeAnsCEO` | `CEO_QA_Uncertainty_pct` | Linguistic | ✅ EXISTS |
| `HedgePreCEO` | `CEO_Pres_Uncertainty_pct` | Linguistic | ✅ EXISTS |
| `HedgeQue` | `Analyst_QA_Uncertainty_pct` | Linguistic | ✅ EXISTS |
| `ToneCall` | `NegativeSentiment` | Linguistic | ✅ EXISTS |
| `ToneChange` | — | Linguistic | 🆕 NEW |
| `NegOCFAny4` | — | Outcome | 🆕 NEW |
| `WorstOCF4` | — | Outcome | 🆕 NEW |
| `MeanOCF4` | — | Outcome | 🆕 NEW |
| `LPM0_OCF4` | — | Outcome (secondary) | 🆕 NEW |
| `PostDispersion` | — | Mechanism | 🆕 NEW |
| `SurpriseNext` | — | Outcome (secondary) | 🆕 NEW |
| `GuidanceMissNext` | — | Outcome (secondary) | 🆕 NEW |
| `WordsCall` | — | Control | ⚠️ PARTIAL |
| `NumCall` | — | Control | 🆕 NEW |
| `ComplexCall` | — | Control | 🆕 NEW |
| `Scriptedness` | — | Friction | 🆕 NEW |
| `NonAnswer` | — | Friction | 🆕 NEW |
| `Avoidance` | — | Friction | 🆕 NEW |
| `QuestionNegativity` | `Analyst_QA_Negative_pct` | Friction | ✅ EXISTS |
| `QuestionDifficulty` | — | Friction | 🆕 NEW |
| Size | `Size` | Fundamental | ✅ EXISTS |
| Leverage | `Lev` | Fundamental | ✅ EXISTS |
| ROA | `ROA` | Fundamental | ✅ EXISTS |
| Tobin's Q | `TobinsQ` | Fundamental | ✅ EXISTS |
| Book-to-Market | `BM` | Fundamental | ✅ EXISTS |
| Cash Holdings | `CashHoldings` | Fundamental | ✅ EXISTS |
| OCF / Assets | `CashFlow` | Fundamental | ✅ EXISTS |
| Sales Growth | `SalesGrowth` | Fundamental | ✅ EXISTS |
| Earnings Surprise | `SurpDec` | Fundamental | ✅ EXISTS |
| Volatility | `Volatility` | Fundamental | ✅ EXISTS |
| CEO Clarity FE | `ClarityCEO` | FE | ✅ EXISTS |
| CEO Clarity Residual | `CEO_Clarity_Residual` | Residual | ✅ EXISTS |
