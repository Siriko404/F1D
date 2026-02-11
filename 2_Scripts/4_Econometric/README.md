# Econometric V1: Original Regression Analyses

## Purpose and Scope

This folder contains the original econometric regression scripts for v1.0 analyses. These scripts test hypotheses about CEO communication clarity (linguistic uncertainty) and financial outcomes using firm fixed effects models with various robustness checks.

**Version:** V1 (Stable - no longer modified)
**Status:** COMPLETE - V1 analyses concluded, results published in thesis
**Prerequisites:** V1 financial variables, V2 text variables
**Outputs:** `4_Outputs/4_Econometric/`

---

## Scripts Overview

| Script | Purpose | Key Outputs |
|--------|---------|-------------|
| `4.1_EstimateCeoClarity.py` | Estimate CEO clarity effects | CEO clarity regression results |
| `4.1.1_EstimateCeoClarity_CeoSpecific.py` | CEO-specific clarity estimates | CEO fixed effects |
| `4.1.2_EstimateCeoClarity_Extended.py` | Extended clarity specification | Robustness checks |
| `4.1.3_EstimateCeoClarity_Regime.py` | Regime-specific clarity | Subperiod analyses |
| `4.1.4_EstimateCeoTone.py` | CEO tone (sentiment) analysis | Tone regression results |
| `4.2_LiquidityRegressions.py` | Stock liquidity regressions | Bid-ask spread results |
| `4.3_TakeoverHazards.py` | Takeover hazard models | Hazard rate estimates |
| `4.4_GenerateSummaryStats.py` | Generate summary statistics | Descriptive statistics tables |

---

## Model Specifications

### CEO Clarity Regressions (4.1_EstimateCeoClarity.py)

Tests whether CEO linguistic clarity affects financial outcomes.

**Model:**
```
Outcome_{i,t} = beta_0 + beta_1 * CEO_Clarity_{i,t}
                 + Controls_{i,t}
                 + Firm_FE + Year_FE + epsilon_{i,t}
```

**Where:**
- `Outcome`: Financial outcome (liquidity, volatility, etc.)
- `CEO_Clarity`: Standardized clarity score from text analysis
- `Controls`: Firm size, leverage, ROA, Tobin's Q, etc.
- `Firm_FE`: Firm fixed effects
- `Year_FE`: Year fixed effects

**Expected Sign:**
- `beta_1 > 0`: Higher clarity improves outcomes

### CEO Tone Regressions (4.1.4_EstimateCeoTone.py)

Tests whether CEO sentiment (positive/negative tone) affects outcomes.

**Model:**
```
Outcome_{i,t} = beta_0 + beta_1 * CEO_Tone_{i,t}
                 + Controls_{i,t}
                 + Firm_FE + Year_FE + epsilon_{i,t}
```

**Where:**
- `CEO_Tone`: Loughran-McDonald sentiment score

### Liquidity Regressions (4.2_LiquidityRegressions.py)

Tests whether CEO communication affects stock market liquidity.

**Model:**
```
Liquidity_{i,t} = beta_0 + beta_1 * CEO_Clarity_{i,t}
                  + Controls_{i,t}
                  + Firm_FE + Year_FE + epsilon_{i,t}
```

**Where:**
- `Liquidity`: Bid-ask spread or Amihud illiquidity measure

### Takeover Hazards (4.3_TakeoverHazards.py)

Tests whether CEO communication affects takeover probability.

**Model:**
```
Hazard(Takeover)_{i,t} = f(beta_0 + beta_1 * CEO_Clarity_{i,t}
                           + Controls_{i,t}
                           + Year_FE + epsilon_{i,t})
```

**Estimation:** Cox proportional hazards or logistic regression

---

## Key Variables

### Dependent Variables

| Variable | Description | Source |
|----------|-------------|--------|
| Spread | Bid-ask spread (Roll measure) | CRSP |
| ILLIQ | Amihud illiquidity measure | CRSP |
| Volatility | Stock return volatility | CRSP |
| Takeover | Takeover indicator (binary) | SDC |
| HazardRate | Takeover hazard rate | Estimated |

### Independent Variables

| Variable | Description | Source |
|----------|-------------|--------|
| CEO_Clarity | Standardized clarity score | Text analysis |
| CEO_Tone | LM sentiment score | Text analysis |
| Uncertainty | Linguistic uncertainty | Text analysis |
| WeakModal | Hedging (may/might/could) | Text analysis |

### Control Variables

| Variable | Description | Source |
|----------|-------------|--------|
| Size | log(total assets) | Compustat |
| Leverage | Total debt / Total assets | Compustat |
| ROA | Return on assets | Compustat |
| TobinsQ | Market-to-book ratio | Compustat |
| CashFlow | Operating cash flow / AT | Compustat |
| MB | Market-to-book | Compustat |

---

## Input/Output Mapping

### Inputs

| Source | Location | Content |
|--------|----------|---------|
| V1 Financial Controls | `4_Outputs/3_Financial/` | Firm controls |
| V2 Text Variables | `4_Outputs/2_Text/` | CEO clarity, tone, uncertainty |
| Sample Manifest | `4_Outputs/1_Sample/` | GVKEY-year mapping |

### Outputs

```
4_Outputs/4_Econometric/
├── 4.1_EstimateCeoClarity/
│   ├── results.parquet
│   ├── coefficients.json
│   └── regression_report.md
├── 4.1.1_EstimateCeoClarity_CeoSpecific/
├── 4.1.2_EstimateCeoClarity_Extended/
├── 4.1.3_EstimateCeoClarity_Regime/
├── 4.1.4_EstimateCeoTone/
├── 4.2_LiquidityRegressions/
├── 4.3_TakeoverHazards/
└── 4.4_GenerateSummaryStats/
```

---

## Methodology

### Fixed Effects Estimation

- **Firm FE:** Controls for time-invariant firm heterogeneity
- **Year FE:** Controls for macroeconomic time trends
- **Clustered SE:** Standard errors clustered at firm level

### 2SLS (Two-Stage Least Squares)

For addressing endogeneity of CEO communication:

**First Stage:**
```
CEO_Clarity_{i,t} = gamma_0 + gamma_1 * Instrument_{i,t}
                    + Controls + Firm_FE + Year_FE + v_{i,t}
```

**Instruments:**
- CEO's prior-firm clarity (if CEO moved between firms)
- Industry-peer average clarity

**Second Stage:**
Use predicted clarity from first stage.

**Validation:**
- First-stage F-statistic > 10 (weak instrument test)
- Hansen J test for instrument validity

### Robustness Checks

1. **Alternative specifications:** Different control sets
2. **Subsample analysis:** High/low leverage, growth/value firms
3. **Placebo tests:** Falsification outcomes
4. **Alternative IVs:** Different instrument combinations

---

## Sample Construction

**Sample Period:** 2002-2018
**Firms:** ~1,500 firms
**Observations:** ~12,000 firm-year observations

**Inclusion Criteria:**
- Non-financial firms (SIC 6000-6999 excluded)
- Non-missing CEO clarity/tone measures
- Non-missing control variables
- Sufficient observations for fixed effects estimation

---

## Relationship to V2/V3

### V1 vs V2 Econometric

| Aspect | V1 (this folder) | V2 (4_Econometric_V2/) |
|--------|------------------|------------------------|
| Purpose | General clarity effects | H1-H9 hypothesis testing |
| Scripts | 4.1-4.4 (exploratory) | 4.1-4.9 (hypothesis-specific) |
| Models | OLS, 2SLS, Hazards | PanelOLS, Logit, Cox PH |
| Status | STABLE | STABLE |

### V3 Econometric (4_Econometric_V3/)

Advanced regressions for H9:
- Interaction effects (PRisk x Uncertainty)
- Biddle residual specifications
- Industry-year fixed effects

---

## Execution Notes

### Execution Order

1. **4.1_EstimateCeoClarity.py** - Main CEO clarity regressions
2. **4.1.1-4.1.3** - CEO-specific robustness (can parallelize)
3. **4.1.4_EstimateCeoTone.py** - Tone analysis
4. **4.2_LiquidityRegressions.py** - Liquidity outcomes
5. **4.3_TakeoverHazards.py** - Takeover models
6. **4.4_GenerateSummaryStats.py** - Summary statistics

Scripts 4.1.1-4.1.3 can run in parallel after 4.1 completes.

### Dependencies

- **V1 Financial Controls:** Required for regression inputs
- **V2 Text Variables:** Required for independent variables
- **Sample Manifest:** Required for firm-year matching

---

## References

Methodology follows standard econometric practices:

- **Fixed effects:** Petersen (2009) - standard error clustering
- **2SLS:** Wooldridge (2010) - instrumental variables
- **Hazard models:** Cox (1972) - proportional hazards
- **Event studies:** MacKinlay (1997) - event study methodology

---

## Contact and Replication

For replication questions:
- `README.md` (root): Project overview
- `CLAUDE.md`: Coding conventions
- Individual script headers: Implementation details

---

*Last updated: 2026-02-11*
*Phase: 60-code-organization*
*Version: v1.0 Econometric Analyses*
