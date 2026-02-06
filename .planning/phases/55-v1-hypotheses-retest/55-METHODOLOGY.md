# Phase 55: V1 Hypotheses Re-Test - Methodology Specification

**Document Version:** 1.0
**Date:** 2026-02-06
**Phase:** 55 - V1 Hypotheses Re-Test
**Plan:** 02 - Methodology Specification

---

## Document Purpose

This document specifies the complete research design for re-testing two V1 hypotheses based on literature best practices. This methodology specification is created BEFORE any code implementation and serves as the blueprint for all subsequent implementation work.

**Key Principle:** Follow literature standards, NOT V1 code patterns. V1 suspected implementation flaws are addressed through rigorous methodology design from first principles.

---

## Literature Foundation

This methodology is grounded in the following foundational papers:

- **Dang et al. (2022)** - "Does managerial tone matter for stock liquidity?" *Finance Research Letters* - Direct methodological template for H1
- **Amihud (2002)** - "Illiquidity and stock returns" *J of Financial Markets* - Standard illiquidity measure (6000+ citations)
- **Roll (1984)** - "A simple implicit measure of the effective bid-ask spread" *J of Finance* - Robustness measure
- **Cameron & Miller (2015)** - "A practitioner's guide to cluster-robust inference" *J of Human Resources* - Clustering standards
- **Petersen (2009)** - "Estimating standard errors in finance panel data" *Review of Financial Studies* - Panel data standards
- **Ambrose (1990)** - M&A prediction using logistic regression
- **Meghouar (2024)** - Modern M&A prediction methods
- **Loughran & McDonald (2011)** - Finance dictionary for text analysis

---

## Hypothesis 1: Managerial Speech Uncertainty -> Stock Illiquidity

### Hypothesis Statement

**H7a:** Higher managerial speech uncertainty predicts HIGHER stock illiquidity (worse liquidity).

**Directional Prediction:**
- beta_Uncertainty > 0 (uncertainty increases illiquidity measure)
- More uncertain speech -> less informed trading -> higher price impact -> worse liquidity

**Theoretical Mechanism:**
1. Managerial uncertainty increases information asymmetry
2. Higher information asymmetry reduces informed trading
3. Reduced informed trading increases adverse selection
4. Higher adverse selection widens bid-ask spreads
5. Result: Higher illiquidity measures

**Counter-Hypothesis (Null):**
- No relationship between speech uncertainty and illiquidity
- Any observed correlation is due to omitted variables or sampling variation

### Dependent Variables

#### Primary: Amihud (2002) Illiquidity Ratio

**Formula:**
```
ILLIQ_{i,t} = (1/D_{i,t}) * sum_{d=1}^{D} (|r_{i,t,d}| / VOLD_{i,t,d})
```

**Where:**
- i = firm identifier
- t = year
- d = trading day
- D_{i,t} = Number of trading days for firm i in year t
- r_{i,t,d} = Daily return (percentage)
- VOLD_{i,t,d} = Daily dollar trading volume

**Implementation Details:**

1. **Data Source:** CRSP Daily Stock File (DSF)
   - Returns: RET field
   - Volume: VOL field (shares)
   - Price: PRC field
   - shares outstanding: SHROUT field

2. **Dollar Volume Calculation:**
   ```
   VOLD_{i,t,d} = |PRC_{i,t,d}| * VOL_{i,t,d}
   ```
   Use absolute value of price (CRSP codes negative prices)

3. **Return Calculation:**
   ```
   r_{i,t,d} = RET_{i,t,d} * 100  [convert to percentage]
   ```
   CRSP returns are already percentage-adjusted

4. **Aggregation Level:** Firm-year
   - Calculate ILLIQ separately for each firm-year
   - Average over all trading days with non-missing data

5. **Transform Options:**
   ```
   Option A (Standard): ILLIQ_raw * 10^6  [scale for interpretability]
   Option B (Log): log(1 + ILLIQ_raw * 10^6)  [reduce skewness]
   Option C (Winsorize): Winsorize at 1%/99% then scale
   ```
   **Primary Choice:** Option A (scaled raw) following Amihud (2002)
   **Robustness:** Option B (log-transformed) to handle extreme values

6. **Minimum Observations:** Require at least 50 trading days per year
   - Prevents illiquidity measures from noisy data
   - Aligns with Roll (1984) requirements

**Why Amihud (2002) as Primary:**
- 6000+ citations - dominant standard in liquidity literature
- Directly measures price impact per dollar of trading
- Computationally straightforward from CRSP data
- Validated in 2024 research (AEA conference papers)
- Dang et al. (2022) uses as robustness check

#### Robustness 1: Roll (1984) Implicit Spread

**Formula:**
```
SPRD_{i,t} = 2 * sqrt(-cov(r_t, r_{t-1}))
```

**Where:**
- r_t = Daily return at time t
- r_{t-1} = Previous day return
- cov(r_t, r_{t-1}) = Autocovariance of consecutive returns

**Implementation Details:**

1. **Calculation Steps:**
   - Calculate first-order autocovariance for each firm-year
   - If autocovariance >= 0: SPRD = NaN (no bid-ask bounce)
   - If autocovariance < 0: SPRD = 2 * sqrt(-autocovariance)

2. **Data Requirements:**
   - Minimum 50 trading days (to estimate autocovariance)
   - Only valid for stocks with bid-ask bounce

3. **When to Use:**
   - Primary robustness check for Amihud measure
   - Independent validation from different methodology
   - Captures transaction costs from price dynamics

**Why Roll (1984) as Robustness:**
- 4000+ citations
- Based on different mechanism than Amihud (price dynamics vs volume)
- Does not require volume data
- Provides independent validation

#### Robustness 2: Bid-Ask Spread

**Formula:**
```
BAS_{i,t} = (1/D) * sum((ASK_{i,t,d} - BID_{i,t,d}) / ((ASK_{i,t,d} + BID_{i,t,d})/2))
```

**Implementation Details:**

1. **Data Source:** CRSP Daily Stock File
   - Bid: BID field (if available)
   - Ask: ASK field (if available)

2. **Calculation:**
   - Calculate relative spread for each trading day
   - Average over all days with valid bid/ask

3. **Limitations:**
   - Not available for all exchanges historically
   - NYSE quoted spreads may not reflect execution costs
   - Use as secondary robustness if data available

#### Robustness 3: Effective Spread (Alternative)

**Formula:**
```
EffSpread_{i,t} = (2/D) * sum(|PRC_{i,t,d} - MID_{i,t,d}| / MID_{i,t,d})
```

**Where MID_{i,t,d} = (BID_{i,t,d} + ASK_{i,t,d}) / 2**

**When Available:** Only with high-frequency data (TAQ, 2000s+)
**Status:** Optional - use if data access available

### Independent Variables

#### Primary: Managerial Speech Uncertainty Measures

Reuse V2 uncertainty measures (per CONTEXT decision):

**V2 Uncertainty Variables Available:**
```
Manager_QA_Uncertainty_pct     - Manager uncertainty in Q&A context
CEO_QA_Uncertainty_pct         - CEO uncertainty in Q&A context
Manager_Pres_Uncertainty_pct   - Manager uncertainty in Presentation context
CEO_Pres_Uncertainty_pct       - CEO uncertainty in Presentation context
```

**Source:** V2 Textual Analysis Pipeline
- Path: `4_Outputs/2_Textual_Analysis/2.2_Variables/`
- Method: Loughran-McDonald (2011) Master Dictionary - Uncertainty category
- Aggregation: Annual average at firm-year level

**Variable Construction:**
1. For each call in year t:
   - Count uncertainty words (LM dictionary)
   - Count total words
   - Calculate: Uncertainty_pct = (Uncertainty words / Total words) * 100

2. For each firm-year:
   - Average Uncertainty_pct across all calls in year
   - Separately for: Manager_QA, CEO_QA, Manager_Pres, CEO_Pres

**Uncertainty Word Examples (LM Dictionary):**
- uncertain, uncertainty, unclear, ambiguous, contingency
- depend, varies, fluctuate, volatile, unpredictable
- risk, risky, hazard, exposure, vulnerable

#### Alternative Independent Variables

For robustness testing:
```
QA_Uncertainty_pct             - Combined Q&A uncertainty (all speakers)
Pres_Uncertainty_pct           - Combined Presentation uncertainty
Uncertainty_Gap                - QA_Uncertainty - Pres_Uncertainty
CEO_Uncertainty_Avg            - CEO uncertainty across both contexts
```

**Timing Specification:**
- Uncertainty measured at year t (speech during fiscal year t)
- Predicts illiquidity at year t+1 (forward-looking)
- Ensures temporal ordering for causal interpretation

### Control Variables

#### Required Controls (from Dang et al. 2022 + literature)

| Variable | Measure | Compustat/CRSP Field | Expected Sign | Rationale |
|----------|---------|---------------------|---------------|-----------|
| **Size** | log(Market Cap) | log(PRC * CSHO) | Negative | Larger firms more liquid |
| **Leverage** | Total Debt / Assets | (DLTT + DLC) / AT | Positive | Higher debt -> more risk -> less liquid |
| **ROA** | Return on Assets | IB / AT | Negative | More profitable -> more liquid |
| **MTB** | Market-to-Book | (PRC * CSHO) / CEQ | Negative | Growth firms more liquid |
| **Volatility** | Stock return volatility | std(RET) annualized | Positive | Volatile stocks less liquid |
| **Stock Returns** | Cumulative returns | product(1+RET) - 1 | Negative | Good performance -> more liquid |
| **Current Ratio** | Current Assets / Current Liabilities | ACT / LCT | Positive | Higher liquidity ratio -> more liquid |
| **Trading Volume** | Log turnover | log(VOL * PRC) | Negative | More volume -> more liquid |

#### Control Variable Construction Details

**Firm Size:**
```
Size_{i,t} = log(MarketCap_{i,t})
MarketCap_{i,t} = PRC_{i,t} * CSHO_{i,t} * 1000  [in millions]
```
Use market cap at fiscal year-end

**Leverage:**
```
Leverage_{i,t} = (DLTT_{i,t} + DLC_{i,t}) / AT_{i,t}
```
Winsorize at 1%/99%

**ROA (Return on Assets):**
```
ROA_{i,t} = IB_{i,t} / AT_{i,t}
```
Winsorize at 1%/99%

**MTB (Market-to-Book):**
```
MTB_{i,t} = (PRC_{i,t} * CSHO_{i,t}) / CEQ_{i,t}
```
Use negative if book equity negative (flag in analysis)

**Volatility:**
```
Volatility_{i,t} = std(RET_{i,t,d}) * sqrt(252)  [annualized]
```
Calculate from daily returns in year t

**Stock Returns:**
```
Returns_{i,t} = product_{d=1}^{D}(1 + RET_{i,t,d}) - 1
```
Buy-and-hold return over year t

**Current Ratio:**
```
CurrentRatio_{i,t} = ACT_{i,t} / LCT_{i,t}
```
Winsorize at 1%/99%

**Trading Volume:**
```
Volume_{i,t} = log(mean(VOL_{i,t,d} * PRC_{i,t,d}))
```
Average daily dollar volume (logged)

### Primary Regression Equation

#### Specification 1 (Primary): Firm + Year FE, Firm-Clustered SE

**Equation:**
```
Illiquidity_{i,t+1} = beta0 + beta1*Uncertainty_{i,t}
                     + gamma1*Size_{i,t}
                     + gamma2*Leverage_{i,t}
                     + gamma3*ROA_{i,t}
                     + gamma4*MTB_{i,t}
                     + gamma5*Volatility_{i,t}
                     + gamma6*Returns_{i,t}
                     + gamma7*CurrentRatio_{i,t}
                     + gamma8*Volume_{i,t}
                     + alpha_i
                     + delta_t
                     + epsilon_{i,t}
```

**Where:**
- alpha_i = Firm fixed effects (controls for time-invariant firm characteristics)
- delta_t = Year fixed effects (controls for macroeconomic trends)
- epsilon_{i,t} = Error term
- SE clustered at firm level (Petersen 2009 standard)

**Implementation (linearmodels):**
```python
from linearmodels.panel import PanelOLS

# Set panel index
df = df.set_index(['gvkey', 'fyear'])

# Primary specification
model = PanelOLS(
    Illiquidity_lag1 ~ Uncertainty + Size + Leverage + ROA + MTB +
    Volatility + Returns + CurrentRatio + Volume,
    entity_effects=True,    # Firm FE
    time_effects=True       # Year FE
)

# Fit with firm-clustered SE
results = model.fit(
    cov_type='clustered',
    cluster_entity=True
)
```

**Hypothesis Test:**
- H0: beta1 = 0 (no effect of uncertainty on illiquidity)
- H1: beta1 > 0 (uncertainty increases illiquidity)
- Test: One-tailed t-test (directional hypothesis)
- Significance: p < 0.05 (primary), FDR-corrected for multiple IVs

#### Timing Justification

**Why Uncertainty_t -> Illiquidity_{t+1}:**

1. **Causal Ordering:** Speech in year t cannot affect liquidity in same year (reverse causality protection)
2. **Information Diffusion:** Market incorporates uncertainty gradually over time
3. **Alignment with Literature:** Dang et al. (2022) uses t -> t+1 timing
4. **Economic Intuition:** Managerial uncertainty affects future liquidity, not contemporaneous

**Alternative Timings (for robustness):**
- Uncertainty_t -> Illiquidity_t (same-year) - tests reverse causality
- Uncertainty_{t-1} -> Illiquidity_t (longer lag) - tests persistence
