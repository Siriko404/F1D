# Stage 3/4 Rewrite Plan: New Architecture for Variables and Econometric Pipeline

**Date Updated:** 2026-02-19
**Status:** Phase 1 COMPLETE (Manager Clarity) - Ready for Phase 2 (Remaining V1 Tests)

---

## Executive Summary

The current Stage 3 (financial) and Stage 4 (econometric) architecture has significant issues:
- Inconsistent variable definitions across scripts
- Bugs and code quality issues
- No standardized output format

We are rewriting the pipeline with a new clean architecture:
- **Stage 3 → "variables"**: Panel building scripts using shared variable modules
- **Stage 4 → "econometric"**: One script per test, outputs Accounting Review style LaTeX
- **Shared variable modules**: One file per variable, ensuring consistent definitions

**IMPORTANT: This document covers ONLY V1 econometric tests. V2 hypothesis tests (H1-H9) are a separate project.**

---

## V1 TESTS STATUS

### Completed

| Test | Old Script | New Script | Status |
|------|------------|------------|--------|
| 4.1 Manager Clarity | `v1/4.1_EstimateManagerClarity.py` | `test_manager_clarity.py` | ✅ COMPLETE |

### Remaining V1 Tests to Rewrite

| Test | Script | Description | Method | Status |
|------|--------|-------------|--------|--------|
| 4.1.1 CEO Clarity | `v1/4.1.1_EstimateCeoClarity.py` | CEO fixed effects (CEO speech only) | Panel OLS with FE | 🔴 Pending |
| 4.1.2 CEO Clarity Extended | `v1/4.1.2_EstimateCeoClarity_Extended.py` | Extended CEO clarity models | Panel OLS with FE | 🔴 Pending |
| 4.1.3 CEO Clarity Regime | `v1/4.1.3_EstimateCeoClarity_Regime.py` | CEO clarity with regime changes | Panel OLS with FE | 🔴 Pending |
| 4.1.4 CEO Tone | `v1/4.1.4_EstimateCeoTone.py` | Net sentiment as CEO trait | Panel OLS with FE | 🔴 Pending |
| 4.2 Liquidity | `v1/4.2_LiquidityRegressions.py` | Communication effects on liquidity | OLS + 2SLS IV | 🔴 Pending |
| 4.3 Takeover Hazards | `v1/4.3_TakeoverHazards.py` | Clarity predicts takeover | Cox PH + Fine-Gray | 🔴 Pending |
| 4.4 Summary Stats | `v1/4.4_GenerateSummaryStats.py` | Descriptive statistics | Descriptive | 🔴 Pending |

---

## PILOT IMPLEMENTATION: Manager Clarity (4.1) ✅ COMPLETE

**Commit:** `91ec198`

**Model Specification:**
```
Manager_QA_Uncertainty_pct ~ C(ceo_id) + C(year) +
    Manager_Pres_Uncertainty_pct +
    Analyst_QA_Uncertainty_pct +
    Entire_All_Negative_pct +
    StockRet + MarketRet + EPS_Growth + SurpDec
```

**Results:**
| Sample | N Obs | N Managers | R-squared |
|--------|-------|------------|-----------|
| Main | 56,060 | 2,539 | 0.4105 |
| Finance | 12,852 | 548 | 0.3052 |
| Utility | 2,950 | 134 | 0.2172 |

**Run Commands:**
```bash
python -m f1d.variables.build_manager_clarity_panel
python -m f1d.econometric.test_manager_clarity
```

---

## Architecture Design

### Folder Structure

```
src/f1d/
├── shared/
│   ├── variables/                    # ✅ IMPLEMENTED
│   │   ├── __init__.py
│   │   ├── base.py                   # VariableBuilder, VariableStats, VariableResult
│   │   ├── manager_qa_uncertainty.py
│   │   ├── manager_pres_uncertainty.py
│   │   ├── analyst_qa_uncertainty.py
│   │   ├── negative_sentiment.py
│   │   ├── stock_return.py
│   │   ├── market_return.py
│   │   ├── eps_growth.py
│   │   ├── earnings_surprise.py
│   │   └── manifest_fields.py
│   ├── latex_tables_accounting.py   # ✅ IMPLEMENTED
│   └── ...
│
├── variables/                        # ✅ IMPLEMENTED (pilot)
│   ├── __init__.py
│   └── build_manager_clarity_panel.py
│
├── econometric/
│   ├── test_manager_clarity.py       # ✅ IMPLEMENTED
│   ├── v1/                           # ACTIVE - remaining tests to rewrite
│   │   ├── 4.1.1_EstimateCeoClarity.py
│   │   ├── 4.1.2_EstimateCeoClarity_Extended.py
│   │   ├── 4.1.3_EstimateCeoClarity_Regime.py
│   │   ├── 4.1.4_EstimateCeoTone.py
│   │   ├── 4.2_LiquidityRegressions.py
│   │   ├── 4.3_TakeoverHazards.py
│   │   └── 4.4_GenerateSummaryStats.py
│   └── v2/                           # SEPARATE PROJECT - H1-H9 tests
│
├── sample/                           # ✅ RENAMED
├── text/                             # ✅ RENAMED
└── financial/
    ├── build_*.py                    # ✅ MOVED from v1/
    └── v2/                           # SEPARATE PROJECT
```

---

## NEXT STEPS: Remaining V1 Tests

### Priority Order

1. **4.1.1 CEO Clarity** - Similar to Manager Clarity, uses CEO-only speech
2. **4.1.4 CEO Tone** - Uses sentiment variables (Positive - Negative)
3. **4.4 Summary Stats** - Simple descriptive statistics
4. **4.2 Liquidity** - Requires IV/2SLS support
5. **4.3 Takeover Hazards** - Requires survival analysis (lifelines)
6. **4.1.2 CEO Clarity Extended** - Extended models
7. **4.1.3 CEO Clarity Regime** - Regime change models

---

## 4.1.1: CEO Clarity

**Source Script:** `src/f1d/econometric/v1/4.1.1_EstimateCeoClarity.py`

**Description:** Estimate CEO "Clarity" using CEO Q&A uncertainty (CEO speech only). Similar to Manager Clarity but isolates CEO's own speech.

**Model Specification:**
```
CEO_QA_Uncertainty_pct ~ C(ceo_id) + C(year) +
    CEO_Pres_Uncertainty_pct +
    Analyst_QA_Uncertainty_pct +
    Entire_All_Negative_pct +
    StockRet + MarketRet + EPS_Growth + SurpDec
```

**Key Difference from Manager Clarity:**
- Uses `CEO_QA_Uncertainty_pct` (CEO only) instead of `Manager_QA_Uncertainty_pct` (all managers)
- Uses `CEO_Pres_Uncertainty_pct` instead of `Manager_Pres_Uncertainty_pct`

**Variables Required:**

| Variable | Type | New Builder Needed? |
|----------|------|---------------------|
| `CEO_QA_Uncertainty_pct` | Dependent | ✅ Yes - `ceo_qa_uncertainty.py` |
| `CEO_Pres_Uncertainty_pct` | Control | ✅ Yes - `ceo_pres_uncertainty.py` |
| `Analyst_QA_Uncertainty_pct` | Control | ❌ Reuse existing |
| `Entire_All_Negative_pct` | Control | ❌ Reuse existing |
| `StockRet`, `MarketRet`, `EPS_Growth`, `SurpDec` | Controls | ❌ Reuse existing |
| `ceo_id`, `gvkey`, `ff12_code`, `start_date` | ID | ❌ Reuse existing |

**Files to Create:**
1. `src/f1d/shared/variables/ceo_qa_uncertainty.py`
2. `src/f1d/shared/variables/ceo_pres_uncertainty.py`
3. `src/f1d/variables/build_ceo_clarity_panel.py`
4. `src/f1d/econometric/test_ceo_clarity.py`

**Config Updates:**
```yaml
variables:
  ceo_qa_uncertainty:
    stage: 2
    source: "outputs/2_Textual_Analysis/2.2_Variables"
    file_pattern: "linguistic_variables_{year}.parquet"
    column: "CEO_QA_Uncertainty_pct"

  ceo_pres_uncertainty:
    stage: 2
    source: "outputs/2_Textual_Analysis/2.2_Variables"
    file_pattern: "linguistic_variables_{year}.parquet"
    column: "CEO_Pres_Uncertainty_pct"
```

---

## 4.1.4: CEO Tone

**Source Script:** `src/f1d/econometric/v1/4.1.4_EstimateCeoTone.py`

**Description:** Estimate CEO "Tone" (Net Sentiment = Positive - Negative) as a persistent communication trait.

**Model Specification:**
```
NetSentiment ~ C(ceo_id) + C(year) + controls
```

**Three Models:**
- ToneAll: CEO FE on all manager speech
- ToneCEO: CEO FE on CEO's own speech only
- ToneRegime: CEO FE on non-CEO manager speech only

**Variables Required:**

| Variable | Type | Description |
|----------|------|-------------|
| `Entire_All_Positive_pct` | Sentiment | Positive sentiment % |
| `Entire_All_Negative_pct` | Sentiment | Negative sentiment % |
| NetSentiment (derived) | Dependent | Positive - Negative |

**Files to Create:**
1. `src/f1d/shared/variables/positive_sentiment.py`
2. `src/f1d/variables/build_ceo_tone_panel.py`
3. `src/f1d/econometric/test_ceo_tone.py`

---

## 4.4: Summary Stats

**Source Script:** `src/f1d/econometric/v1/4.4_GenerateSummaryStats.py`

**Description:** Generate comprehensive descriptive statistics for the sample.

**Output:** Summary tables with:
- N observations
- Mean, Std, Min, Max
- Percentiles (p25, p50, p75)
- By sample (Main, Finance, Utility)

**Files to Create:**
1. `src/f1d/econometric/generate_summary_stats.py`

---

## 4.2: Liquidity Regressions

**Source Script:** `src/f1d/econometric/v1/4.2_LiquidityRegressions.py`

**Description:** Test whether CEO/Manager communication affects market liquidity using IV regression.

**Models:**
1. First Stage: Q&A Uncertainty ~ CCCL Instrument
2. OLS Regressions (no instrument)
3. 2SLS Regressions (Q&A Uncertainty instrumented)

**Key Variables:**
- `ClarityRegime`: CEO fixed effect from 4.1 (EXOGENOUS)
- `ClarityCEO`: CEO fixed effect from 4.1.1 (EXOGENOUS)
- `Manager_QA_Uncertainty_pct`: Time-varying (ENDOGENOUS, instrumented)
- `shift_intensity_sale_ff48`: FF48 sales-weighted CCCL instrument

**Special Requirements:**
- 2SLS IV regression support
- CCCL instrument data

**Dependencies:**
- Requires 4.1 (Manager Clarity) scores
- Requires 4.1.1 (CEO Clarity) scores

---

## 4.3: Takeover Hazards

**Source Script:** `src/f1d/econometric/v1/4.3_TakeoverHazards.py`

**Description:** Analyze how CEO Clarity and Q&A Uncertainty predict takeover probability using survival analysis.

**Models:**
1. Cox Proportional Hazards (All Takeovers)
2. Fine-Gray Competing Risks (Uninvited: Hostile + Unsolicited)
3. Fine-Gray Competing Risks (Friendly: Friendly + Neutral)

**Key Variables:**
- `ClarityRegime`: CEO Fixed Effect (time-invariant)
- `ClarityCEO`: CEO-specific Fixed Effect
- `Manager_QA_Uncertainty_pct`: Call-level vagueness

**Special Requirements:**
- `lifelines` library for survival analysis
- SDC M&A data (`inputs/SDC/sdc-ma-merged.parquet`)

**Dependencies:**
- Requires 4.1 (Manager Clarity) scores

---

## 4.1.2 & 4.1.3: CEO Clarity Extended/Regime

**Source Scripts:**
- `src/f1d/econometric/v1/4.1.2_EstimateCeoClarity_Extended.py`
- `src/f1d/econometric/v1/4.1.3_EstimateCeoClarity_Regime.py`

**Description:** Extended models and regime change variations of CEO Clarity.

**Status:** Lower priority - implement after core tests are complete.

---

## Implementation Checklist (For Each Test)

```markdown
## {TEST_ID} Implementation Checklist

### Step 1: Analysis
- [ ] Read existing V1 script for model specification
- [ ] Identify required variables
- [ ] Check if new variable builders needed

### Step 2: Variable Builders (if needed)
- [ ] Create new variable builders in `src/f1d/shared/variables/`
- [ ] Update `src/f1d/shared/variables/__init__.py`
- [ ] Update `config/variables.yaml`

### Step 3: Stage 3 Panel Builder
- [ ] Create `src/f1d/variables/build_{test}_panel.py`
- [ ] Test panel output

### Step 4: Stage 4 Test Script
- [ ] Create `src/f1d/econometric/test_{test}.py`
- [ ] Implement regression function
- [ ] Generate LaTeX table output

### Step 5: Verification
- [ ] Compare results with original V1 script
- [ ] Verify coefficient values match within tolerance
```

---

## Implementation Order (Recommended)

1. **4.1.1 CEO Clarity**
   - Most similar to completed Manager Clarity
   - Only 2 new variable builders needed
   - No special methods required

2. **4.1.4 CEO Tone**
   - Uses existing sentiment variables
   - Requires derived NetSentiment variable

3. **4.4 Summary Stats**
   - Simple, no regressions
   - Quick win

4. **4.2 Liquidity**
   - Requires IV/2SLS infrastructure
   - Depends on 4.1.1

5. **4.3 Takeover Hazards**
   - Requires survival analysis
   - Depends on 4.1

6. **4.1.2 & 4.1.3**
   - Variations of CEO Clarity
   - Lower priority

---

## Critical Reminders for AI Implementer

1. **NEVER hardcode timestamp directories** - Use `resolve_source_dir()` from base.py

2. **Follow the established patterns** - `test_manager_clarity.py` is the template

3. **Read V1 scripts carefully** - They contain exact model specifications

4. **Test incrementally** - Run Stage 3 before Stage 4

5. **Update config first** - Add new variables to `config/variables.yaml`

6. **V1 and V2 are separate** - This document is ONLY for V1 tests

7. **LaTeX format is strict** - Two columns per model (Est., t-value), no stars

---

## Files Reference

### Created Files (Pilot)
| File | Purpose |
|------|---------|
| `src/f1d/shared/variables/__init__.py` | Package init, exports |
| `src/f1d/shared/variables/base.py` | Base classes |
| `src/f1d/shared/variables/manager_qa_uncertainty.py` | Variable builder |
| `src/f1d/shared/variables/manager_pres_uncertainty.py` | Variable builder |
| `src/f1d/shared/variables/analyst_qa_uncertainty.py` | Variable builder |
| `src/f1d/shared/variables/negative_sentiment.py` | Variable builder |
| `src/f1d/shared/variables/stock_return.py` | Variable builder |
| `src/f1d/shared/variables/market_return.py` | Variable builder |
| `src/f1d/shared/variables/eps_growth.py` | Variable builder |
| `src/f1d/shared/variables/earnings_surprise.py` | Variable builder |
| `src/f1d/shared/variables/manifest_fields.py` | Variable builder |
| `src/f1d/variables/__init__.py` | Package init |
| `src/f1d/variables/build_manager_clarity_panel.py` | Stage 3 script |
| `src/f1d/econometric/test_manager_clarity.py` | Stage 4 script |
| `src/f1d/shared/latex_tables_accounting.py` | LaTeX generator |
| `config/variables.yaml` | Variable configuration |

### Remaining V1 Scripts (Active, to be rewritten)
| Script | Purpose |
|--------|---------|
| `src/f1d/econometric/v1/4.1.1_EstimateCeoClarity.py` | CEO clarity (CEO-only speech) |
| `src/f1d/econometric/v1/4.1.2_EstimateCeoClarity_Extended.py` | Extended CEO clarity |
| `src/f1d/econometric/v1/4.1.3_EstimateCeoClarity_Regime.py` | CEO clarity regime |
| `src/f1d/econometric/v1/4.1.4_EstimateCeoTone.py` | CEO tone (net sentiment) |
| `src/f1d/econometric/v1/4.2_LiquidityRegressions.py` | IV/2SLS liquidity |
| `src/f1d/econometric/v1/4.3_TakeoverHazards.py` | Survival analysis |
| `src/f1d/econometric/v1/4.4_GenerateSummaryStats.py` | Descriptive stats |

---

*End of Document*
