# Financial V3: Advanced Interaction Variables (H9)

## Purpose and Scope

This folder contains advanced variable construction scripts for V3 hypotheses, specifically H9 (PRisk x CEO Style -> Abnormal Investment). These scripts build upon V1/V2 foundations by adding external risk measures (Political Risk) and CEO style persistence measures.

**Version:** V3 (Active - H9 testing complete)
**Status:** COMPLETE - H9 NOT SUPPORTED (interaction p=0.76)
**Prerequisites:** V1 financial controls, V2 text variables
**Outputs:** `4_Outputs/5_Financial_V3/`

---

## Hypothesis H9: PRisk x CEO Style -> Abnormal Investment

**Research Question:** Does the interaction between political risk (PRisk) and CEO vagueness style predict abnormal investment behavior?

**Result:** H9 NOT SUPPORTED - interaction term insignificant (p=0.76)

---

## Scripts Overview

| Script | Purpose | Key Outputs |
|--------|---------|-------------|
| `5.8_H9_StyleFrozen.py` | Construct CEO style frozen measures | CEO Clarity scores by firm-year |
| `5.8_H9_PRiskFY.py` | Aggregate political risk to fiscal year | PRisk measures at firm-year level |
| `5.8_H9_AbnormalInvestment.py` | Calculate absolute abnormal investment | Biddle residuals and absolute deviations |
| `5.8_H9_FinalMerge.py` | Merge all H9 variables for regression | Final analysis dataset |

---

## Variable Construction

### CEO Style Frozen (5.8_H9_StyleFrozen.py)

Constructs persistent CEO communication style measures:

| Variable | Description | Source |
|----------|-------------|--------|
| StyleFrozen | CEO Clarity score (standardized) | V2 ClarityCEO measures |
| CEO_ID | Unique CEO identifier | Entity linking results |
| n_calls | Number of calls by CEO in sample | Transcript metadata |
| first_call_date | First call date for CEO | Transcript metadata |

**Freezing Constraint:**
- CEO style assigned to firm-years where `start_date <= fy_end`
- Prevents look-ahead bias (no future information used)
- Dominant CEO per firm-year selected by max calls

**Output:** `style_frozen.parquet` (7,125 firm-years, 493 firms, 471 CEOs)

### Political Risk Fiscal Year (5.8_H9_PRiskFY.py)

Aggregates Hassan et al. political risk measures to fiscal year:

| Variable | Description | Source |
|----------|-------------|--------|
| PRiskFY | Political risk (fiscal year aggregate) | Hassan et al. PRisk data |
| PRisk_count | Number of articles in fiscal year | PRisk data |
| PRisk_avg | Average PRisk score | PRisk data |
| PRisk_max | Maximum PRisk score | PRisk data |

**Aggregation Method:**
- Daily PRisk measures matched to fiscal year periods
- PRiskFY = mean(PRisk) over fiscal year
- Requires minimum 100 days of PRisk coverage

**Output:** `prisk_fy.parquet` (65,664 firm-years, 7,869 firms)

### Abnormal Investment (5.8_H9_AbnormalInvestment.py)

Calculates Biddle (2009) investment residuals:

| Variable | Formula | Description |
|----------|---------|-------------|
| Investment | (CapEx + R&D + Acq - AssetSales) / lag(AT) | Total investment rate |
| InvestmentResidual | Residual from first-stage regression | Abnormal investment |
| AbsAbInv | |Absolute value of InvestmentResidual| | Absolute abnormal investment |

**First-Stage Specification:**
```
Investment_{i,t} ~ TobinQ_{i,t-1} + SalesGrowth_{i,t-1}
```
Run by (FF48 industry, fiscal year) cells with N >= 30.

**Output:** `abs_ab_inv.parquet` (80,048 firm-years, 11,256 firms)

### Final Merge (5.8_H9_FinalMerge.py)

Merges all H9 variables for regression:

| Variable | Description |
|----------|-------------|
| gvkey | Firm identifier |
| fyear | Fiscal year |
| StyleFrozen | CEO clarity (frozen) |
| PRiskFY | Political risk (fiscal year) |
| AbsAbInv | Absolute abnormal investment |
| Interaction | StyleFrozen x PRiskFY |
| Controls | Biddle controls (CashFlow, Size, Leverage, TobinQ, SalesGrowth) |

**Output:** `h9_final_dataset.parquet` (5,295 firm-years for regression)

---

## Input/Output Mapping

### Inputs

| Source | Location | Content |
|--------|----------|---------|
| V2 Text Variables | `4_Outputs/2_Text/` | CEO Clarity scores |
| V1 Financial Controls | `4_Outputs/3_Financial/` | Compustat controls |
| Hassan PRisk | `1_Inputs/prisk/` | Political risk data |
| Compustat | `1_Inputs/compustat/` | Investment data |

### Outputs

```
4_Outputs/5_Financial_V3/
├── 5.8_H9_StyleFrozen/
│   └── style_frozen.parquet
├── 5.8_H9_PRiskFY/
│   └── prisk_fy.parquet
├── 5.8_H9_AbnormalInvestment/
│   └── abs_ab_inv.parquet
├── 5.8_H9_FinalMerge/
│   └── h9_final_dataset.parquet
└── stats.json
```

---

## Sample Construction

### StyleFrozen Sample

| Metric | Value |
|--------|-------|
| Firm-years | 7,125 |
| Firms | 493 |
| CEOs | 471 |
| Period | 2002-2018 |
| % of Compustat | 2.0% |

### PRiskFY Sample

| Metric | Value |
|--------|-------|
| Firm-years | 65,664 |
| Firms | 7,869 |
| Period | 2002-2018 |

### Final H9 Regression Sample

| Metric | Value |
|--------|-------|
| Observations | 5,295 |
| Firms | 1,121 |
| Period | 2003-2017 (after lag) |

---

## H9 Regression Results

**Primary Result:**
- Interaction coefficient: +0.0002
- SE: 0.0006
- p-value (one-tailed): 0.76
- **Conclusion:** H9 NOT SUPPORTED

**Interpretation:** Political risk and CEO communication style affect investment through independent channels, not multiplicatively. The meaningful null suggests no compound uncertainty effect.

---

## Relationship to V1/V2

### V3 vs V1/V2

| Aspect | V1 (3_Financial/) | V2 (3_Financial_V2/) | V3 (this folder) |
|--------|-------------------|----------------------|------------------|
| Purpose | General controls | H1-H8 variables | H9 interaction variables |
| External Data | Compustat, CRSP | Compustat, CRSP | Hassan PRisk |
| CEO Measures | None | Clarity (time-varying) | StyleFrozen (persistent) |
| Investment | Basic measures | Efficiency scores | Biddle residuals |
| Status | STABLE | STABLE | COMPLETE |

---

## Execution Notes

### Execution Order

1. **5.8_H9_StyleFrozen.py** - CEO style frozen construction
2. **5.8_H9_PRiskFY.py** - Political risk fiscal year aggregation
3. **5.8_H9_AbnormalInvestment.py** - Abnormal investment calculation
4. **5.8_H9_FinalMerge.py** - Merge all variables for regression

Scripts 1-3 can run in parallel.

### Dependencies

- **V2 Text Variables:** Required for CEO Clarity scores
- **V1 Financial Controls:** Required for Compustat inputs
- **Hassan PRisk Data:** Required for political risk measures
- **Compustat Quarterly:** Required for investment data

---

## References

- **Biddle (2009):** Investment residuals and accounting quality
- **Hassan et al.:** Political risk text analysis measures
- **Dzieliński (2018):** CEO vagueness as persistent style

---

## Contact and Replication

For replication questions:
- Phase 58 plans: `58-CONTEXT.md`, `58-RESEARCH.md`
- H9 specification: `H9 spec.txt`
- Regression output: `4_Outputs/4_Econometric_V3/4.3_H2_PRiskUncertainty_Investment/`

---

*Last updated: 2026-02-11*
*Phase: 60-code-organization*
*Version: v3.0 H9 Variables*
