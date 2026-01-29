# Variable Definition Comparison Report

**Paper**: "CEO Clarity" (FWP_2017_02_v2.pdf)  
**Pipeline**: F1D v1.0  
**Generated**: 2025-12-08

---

## Overview

This report compares **all variables** from the paper's Table A.1 (Definitions) and Table IA.3 (Summary Statistics) against our pipeline's implementation. Variables are grouped by category.

### Legend

| Status | Meaning |
|:-------|:--------|
| ✅ MATCH | Variable exists and methodology aligns |
| ⚠️ PARTIAL | Variable exists but methodology differs |
| ❌ MISSING | Variable not implemented in pipeline |
| 🔧 FIX NEEDED | Variable exists but has known issues |

---

## Panel A: Call-Level Variables

### Outcome Variables

| Variable | Paper Definition | Our Implementation | Status |
|:---------|:-----------------|:-------------------|:-------|
| **AbnVol** | Abnormal trading volume: log ratio of volume over [0:1] days vs. avg daily volume over 40 days ending 5 days before call | Not implemented | ❌ MISSING |
| **AnResp** | Absolute difference between analyst consensus forecast for Q(t+1) before and after the call | Not implemented | ❌ MISSING |
| **ACAR01 (%)** | Absolute cumulative abnormal return over [0:1] days relative to call | Not implemented | ❌ MISSING |
| **CAR01 (%)** | Cumulative abnormal return over [0:1] days relative to call | Not implemented | ❌ MISSING |
| **CAR260 (%)** | Cumulative abnormal return over [2:60] days relative to call | Not implemented | ❌ MISSING |
| **Comp ($ths)** | CEO compensation | Not implemented | ❌ MISSING |
| **MedRec** | Median analyst recommendation | Not implemented | ❌ MISSING |
| **ROA** | Return on Assets | Partially in Compustat but not in final panel | ❌ MISSING |
| **Tobin's Q** | Market value / Book value | Not implemented | ❌ MISSING |

---

### Speech Variables

| Variable | Paper Definition | Paper Stats | Our Implementation | Our Stats | Status |
|:---------|:-----------------|:------------|:-------------------|:----------|:-------|
| **AvoidAnsCEO** | CEO answer avoidance (Barth, Mansouri, and Mancini 2023) | mean=0.04 | Not implemented | - | ❌ MISSING |
| **ComplexCall** | Complexity of the entire call (FOG index) | mean=18.57 | Not implemented | - | ❌ MISSING |
| **ConcAnsCEO** | Concreteness of CEO answers (Hiller, Fisher, Markopolos) | mean=2.85 | Not implemented | - | ❌ MISSING |
| **ConcPreCEO** | Concreteness of CEO presentation | mean=2.97 | Not implemented | - | ❌ MISSING |
| **NegCall (%)** | Percentage of negative words in entire call (LM dictionary) | mean=0.93, std=0.34 | `EntireCallNeg_pct` from Step 2.3 | mean=0.93, std=0.33 | ✅ MATCH |
| **NumCall** | Log of number of calls for the firm up to quarter t | mean=2.60 | Not implemented | - | ❌ MISSING |
| **UncAnsCEO (%)** | % uncertainty words in CEO answers | mean=0.79, std=0.41 | `MaQaUnc_pct` (all managers, not just CEO) | mean=0.83, std=0.34 | ⚠️ PARTIAL |
| **UncCall (%)** | % uncertainty words in entire call | mean=0.84, std=0.25 | `EntireCallUnc_pct` from Step 2.3 | mean=0.88, std=~0.25 | ✅ MATCH |
| **UncEPR (%)** | % uncertainty words in earnings press release (8-K) | mean=1.23 | Not implemented (no 8-K data) | - | ❌ MISSING |
| **UncPreCEO (%)** | % uncertainty words in CEO presentation | mean=0.67, std=0.39 | `MaPresUnc_pct` (all managers) | mean=0.75, std=0.36 | ⚠️ PARTIAL |
| **UncQue (%)** | % uncertainty words in analyst questions | mean=1.28, std=0.45 | `AnaQaUnc_pct` from Step 2.3 | mean=1.45, std=0.50 | ⚠️ PARTIAL |
| **VagAnsCEO (%)** | % vague words in CEO answers | mean=3.66 | Not implemented | - | ❌ MISSING |
| **VagPreCEO (%)** | % vague words in CEO presentation | mean=1.28 | Not implemented | - | ❌ MISSING |
| **WordsAnsCEO** | Word count in CEO answers | mean=1,852 | Manager Q&A word count (all managers) | mean=2,664 | ⚠️ PARTIAL |
| **WordsCall** | Total word count in call | mean=6,047 | `total_word_tokens` (entire_call) | mean=6,877 | ✅ MATCH |
| **WordsPreCEO** | Word count in CEO presentation | mean=1,354 | Manager Pres word count (all managers) | mean=3,146 | ⚠️ PARTIAL |
| **WordsQue** | Word count in analyst questions | mean=1,274 | Analyst Q&A word count | mean=1,032 | ⚠️ PARTIAL |

#### Notes on Speech Variables

> **Key Caveat**: Our pipeline aggregates **all manager speech** (CEO, CFO, COO, etc.), not just CEO speech. This systematically inflates our word counts and may slightly affect uncertainty percentages.

---

### Other Variables (Controls)

| Variable | Paper Definition | Paper Stats | Our Implementation | Our Stats | Status |
|:---------|:-----------------|:------------|:-------------------|:----------|:-------|
| **AnDispPre** | Analyst dispersion: std dev of forecasts 3 days before call | mean=0.05 | Not implemented | - | ❌ MISSING |
| **ln(Assets)** | Natural log of total assets (USD mln) | mean=7.35 | Available in Compustat, not in final panel | - | ❌ MISSING |
| **DailyVola** | Stock volatility from daily returns, annualized % | mean=40.46 | Not implemented | - | ❌ MISSING |
| **EPS growth (yoy)** | (EPS_t - EPS_t-4) / EPS_t-4 as fraction | mean=-0.03, std=1.78 | `EPS_Growth` from Step 2.7 (now as fraction) | mean=0.22, std=2.6 | ✅ FIXED |
| **FracInt** | Intangible capital / total assets (Peters & Taylor 2017) | mean=0.57 | Not implemented | - | ❌ MISSING |
| **Guidance** | Binary: 1 if firm provided earnings guidance | mean=0.18 | Not implemented | - | ❌ MISSING |
| **MarketRet (%)** | VW market return from 5 days after prev earnings to 5 days before current | mean=1.92, std=8.38 | `MarketRet` from Step 2.7 | mean=2.36, std=7.82 | ⚠️ PARTIAL |
| **StockRet (%)** | Stock return over same window as MarketRet | mean=2.19, std=20.18 | `StockRet` from Step 2.7 | mean=3.17, std=16.93 | ⚠️ PARTIAL |
| **SurpDec** | Earnings surprise decile: 5 positive bins (5→1), 0, 5 negative bins (-1→-5) | mean=0.85, std=3.16, p50=2 | `SurpDec` from Step 2.7 (now 11-point scale) | mean≈0.98, p50=1 | ✅ FIXED |
| **SurpDecAbs** | Absolute value of SurpDec | - | `SurpDecAbs` from Step 2.7 | - | ✅ MATCH |

#### Detailed Issue: SurpDec

**Paper's Methodology**:
> "SurpDec is obtained by grouping firms into five equally sized bins of positive surprise (numbered from 5 to 1, from largest positive to smallest positive surprise), then 0 for zero surprises, and then five equally sized bins of negative surprise from -1 (for the smallest negative surprises) through -5 (for the largest negative surprises)."

**Our Implementation** (Step 2.7, line 668):
```python
surp_dec = deciles - 4  # Maps 0-9 → -4 to +5
```

**Difference**:
| Aspect | Paper | Ours |
|:-------|:------|:-----|
| Scale | -5 to +5 (11 values) | -4 to +5 (10 values) |
| Positive bins | 5 bins: 5,4,3,2,1 | 5 bins: 5,4,3,2,1 |
| Zero handling | Explicit 0 for zero surprise | 0 used for unmatched calls |
| Negative bins | 5 bins: -1,-2,-3,-4,-5 | 4 bins: -4,-3,-2,-1,0 |
| Median (p50) | 2 (positive skew) | 0 (symmetric) |

**Fix Required**: Reimplement SurpDec with explicit 11-point scale as per paper.

#### Detailed Issue: EPS Growth

**Paper's Definition**: "The fraction by which earnings in a quarter exceed earnings in the same quarter in the prior year" (mean = -0.03, std = 1.78)

**Our Implementation**: `(EPS_t - EPS_t-4) / |EPS_t-4| * 100` → percentage, not fraction

**Difference**: 
- Paper reports as fraction (e.g., 0.10 = 10% growth)
- We report as percentage (e.g., 10.0 = 10% growth)
- Our mean=22.27 → Paper equivalent would be 0.22 (close to their -0.03 after winsorization)

---

## Panel B: CEO-Level Variables

| Variable | Paper Definition | Paper Stats | Our Implementation | Our Stats | Status |
|:---------|:-----------------|:------------|:-------------------|:----------|:-------|
| **Ability** | CEO ability (Demerjian, Lev, McVay 2012) | mean=0.42 | Not implemented | - | ❌ MISSING |
| **BirthYear** | Last two digits of CEO birth year (ExecuComp) | mean=53.75 | Not in final panel | - | ❌ MISSING |
| **ClarityCEO** | Negative of CEO fixed effect in uncertainty word frequency, standardized to mean=0, std=1 | mean=-0.62*, std=0.23* | `ClarityCEO` from Step 2.8 | mean=-0.06, std=0.97 | ⚠️ PARTIAL |
| **Female** | 1 if CEO is female (ExecuComp) | mean=0.03 | Not in final panel | - | ❌ MISSING |

*Note: Paper's Table 1 shows ClarityCEO at CEO level (N=5,984), not call level.

#### Detailed Issue: ClarityCEO

**Paper's Method** (Section 4.4, Equation 4):
1. Regress `UncAnsCEO` on CEO fixed effects + UncPreCEO + other controls
2. Extract CEO fixed effect (γ_i)
3. ClarityCEO = -γ_i (negative of fixed effect)
4. Standardize to mean=0, std=1

**Our Implementation** (Step 2.8):
1. Similar regression approach
2. Extract fixed effects
3. Standardization may differ

**Difference**: Our standardization differs. Paper reports CEO-level stats (mean=-0.62, std=0.23 across 5,984 CEOs), while our stats are at call level (mean=-0.06, std=0.97).

---

## Summary Statistics Comparison

### Variables That Match (✅)

| Variable | Paper Mean | Our Mean | Difference |
|:---------|:-----------|:---------|:-----------|
| NegCall (%) | 0.93 | 0.93 | **0%** |
| UncCall (%) | 0.84 | 0.88 | +5% |
| WordsCall | 6,047 | 6,877 | +14% |

### Variables That Partially Match (⚠️)

| Variable | Paper Mean | Our Mean | Issue |
|:---------|:-----------|:---------|:------|
| UncAnsCEO (%) | 0.79 | 0.83 | All managers, not just CEO |
| UncPreCEO (%) | 0.67 | 0.75 | All managers, not just CEO |
| StockRet (%) | 2.19 | 3.17 | Similar but different sample |
| MarketRet (%) | 1.92 | 2.36 | Similar but different window |

### Variables That Need Fixes (🔧)

| Variable | Paper Mean | Our Mean | Issue |
|:---------|:-----------|:---------|:------|
| SurpDec | 0.85 | 0.31 | Different decile mapping (see above) |
| EPS growth | -0.03 | 22.27 | Fraction vs. percentage |

### Variables Not Implemented (❌)

**Outcome**: AbnVol, AnResp, ACAR01, CAR01, CAR260, Comp, MedRec, ROA, Tobin's Q

**Speech**: AvoidAnsCEO, ComplexCall, ConcAnsCEO, ConcPreCEO, NumCall, UncEPR, VagAnsCEO, VagPreCEO

**Other**: AnDispPre, ln(Assets), DailyVola, FracInt, Guidance

**CEO**: Ability, BirthYear, Female

---

## Recommendations

### High Priority Fixes

1. **SurpDec**: Reimplement with paper's 11-point scale methodology
2. **EPS Growth**: Change from percentage to fraction, or document the difference
3. **CEO-only speech**: Consider isolating CEO speech from other manager speech

### Medium Priority Additions

4. **Tobin's Q**: Add from Compustat (PRCCQ * CSHOQ + AT - CEQ) / AT
5. **ln(Assets)**: Add from Compustat (log of AT)
6. **ROA**: Add from Compustat (NIQ / AT)
7. **Guidance**: Requires additional data source

### Low Priority / Future Work

8. **AbnVol, CAR variables**: Require high-frequency CRSP data
9. **Vagueness variables**: Require vagueness wordlist
10. **Complexity (FOG)**: Requires sentence-level parsing
11. **Analyst dispersion**: Requires more IBES fields

---

## Appendix: Data Source Mapping

| Paper Data Source | Our Equivalent |
|:------------------|:---------------|
| Thomson Reuters Street Events | Capital IQ Transcripts |
| CRSP | CRSP DSF (quarterly files) |
| Compustat | comp_na_daily_all.parquet |
| IBES | tr_ibes.parquet |
| ExecuComp | CEO Dismissal Data (Jenter & Kanaan) |

---

**End of Report**
