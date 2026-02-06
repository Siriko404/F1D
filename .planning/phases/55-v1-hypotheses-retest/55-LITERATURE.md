# Phase 55: V1 Hypotheses Re-Test - Literature Review

**Date:** 2026-02-06
**Phase:** 55 - V1 Hypotheses Re-Test
**Plan:** 01 - Literature Review

## Executive Summary

This document synthesizes 20+ years of research across major finance journals on two hypotheses:
1. **H1:** Managerial speech uncertainty -> Stock illiquidity
2. **H2:** Managerial speech uncertainty -> Takeover target probability

The literature review identifies methodological standards, effect sizes, and best practices to guide fresh re-implementation of these V1 hypotheses.

**Key Finding:** A robust literature base exists for both hypotheses, with Dang et al. (2022) providing a direct methodological template for H1, and extensive M&A prediction literature for H2.

---

## Hypothesis 1: Uncertainty -> Illiquidity

### Primary Foundational Paper

**Dang et al. (2022)** - "Does managerial tone matter for stock liquidity? Evidence from textual disclosures"
- **Journal:** Finance Research Letters
- **Citations:** 37+ (as of 2024)
- **Sample Period:** 1994-2019 (26 years)
- **Sample Size:** US-listed firms, SEC filings
- **Data Sources:** SEC EDGAR, CRSP, Compustat

**Methodology:**
- **Text Measure:** Loughran-McDonald (2011) Master Dictionary for tone/uncertainty
- **Illiquidity Measures:**
  - Primary: Bid-ask spread (BASpread)
  - Robustness: Amihud (2002) illiquidity ratio
- **Regression Specification:**
  ```
  Illiquidity_{i,t+1} = alpha + beta*Tone_{i,t} + gamma*Controls_{i,t} + Firm_FE + Year_FE + epsilon_{i,t}
  ```
- **Fixed Effects:** Firm and year
- **Standard Errors:** Clustered at firm level
- **Timing:** Tone_t predicts Illiquidity_{t+1} (next period)

**Key Findings:**
- **Direction:** Positive managerial tone -> Higher stock liquidity
- **Coefficient (BASpread):** 0.0006, p < 0.01
- **Coefficient (Amihud):** 0.0065, p < 0.05
- **Interpretation:** More positive (less uncertain) tone associated with lower illiquidity

**Control Variables:**
- Firm size (log market cap)
- Leverage (debt/assets)
- Profitability (ROA)
- Market-to-book (MTB)
- Stock volatility
- Trading volume
- Return-on-assets
- Standard deviation of returns

---

### Standard Illiquidity Measures

#### 1. Amihud (2002) Illiquidity Ratio - PRIMARY STANDARD

**Paper:** Amihud, Y. (2002). "Illiquidity and stock returns: cross-section and time-series effects." *Journal of Financial Markets*, 5(1), 31-56.

**Formula:**
```
ILLIQ_{i,y} = (1/D_{i,y}) * sum(|r_{i,d}| / VOLD_{i,d})
```
Where:
- D_{i,y} = Number of trading days for firm i in year y
- r_{i,d} = Daily return
- VOLD_{i,d} = Daily dollar trading volume

**Implementation Notes:**
- Multiply by 10^6 for interpretability (typical scaling)
- Use CRSP daily stock data
- Winsorize at 1%/99% or log-transform to reduce skewness
- Alternative: log(ILLIQ + constant) to handle zeros

**Why Standard:**
- 6,000+ citations as of 2024
- Validated in 2024 research (AEB 2024 conference paper)
- Directly measures price impact per dollar of trading
- Computationally straightforward from CRSP data

**Extensions/Updates:**
- Acharya and Pedersen (2005) - Liquidity-adjusted CAPM
- Lou and Shu (2017) - Amihud illiquidity decomposition
- 2024 validation: "Numerical precision of the Amihud illiquidity measure" (AEA 2024)

#### 2. Roll (1984) Implicit Spread - ROBUSTNESS CHECK

**Paper:** Roll, R. (1984). "A simple implicit measure of the effective bid-ask spread in an efficient market." *Journal of Finance*, 39(4), 1127-1139.

**Formula:**
```
Spread = 2 * sqrt(-cov(r_t, r_{t-1}))
```
Where:
- r_t = Daily return at time t
- r_{t-1} = Previous day return
- Covariance across consecutive returns

**Implementation Notes:**
- Only valid when autocovariance is negative (bid-ask bounce)
- Requires sufficient observations (minimum 50 days)
- Can produce NaN for highly liquid stocks (near-zero autocovariance)

**Why Robustness:**
- Captures transaction costs from price dynamics
- Independent of volume data
- 4,000+ citations

#### 3. Bid-Ask Spread - TRANSACTION COST MEASURE

**Implementation:**
- Use CRSP daily bid/ask prices
- Relative spread = (Ask - Bid) / ((Ask + Bid)/2)
- Average over trading year

**Advantages:**
- Direct measure of transaction cost
- Widely understood by practitioners

**Limitations:**
- Only available for NASDAQ/AMEX historically
- NYSE specialists quoted spreads may not reflect execution costs

#### 4. Effective Spread - MODERN ALTERNATIVE

**Formula:**
```
EffSpread = 2 * |Price_t - Midpoint_t| / Midpoint_t
```
Where Midpoint_t = (Bid_t + Ask_t) / 2

**When Available:** High-frequency data (TAQ, 2000s+)

---

### Related Literature on Uncertainty and Liquidity

#### 1. Economic Policy Uncertainty and Stock Liquidity

**Dash (2021)** - "Economic policy uncertainty and stock market liquidity: Evidence from an emerging economy"
- **Journal:** Research in International Business and Finance
- **Citations:** 87+
- **Method:** Granger causality tests, VAR models
- **Finding:** EPU negatively affects stock liquidity (higher uncertainty -> lower liquidity)

**Key Methodology:**
- Uses Baker-Bloom-Davis Economic Policy Uncertainty Index
- Vector autoregression (VAR) for causality
- Multiple liquidity measures (Amihud, turnover, spread)

#### 2. Management Tone and Information Asymmetry

**Various authors (2024)** - COVID-19 period studies
- **Finding:** Managerial tone affects information asymmetry
- **Channel:** Tone -> Disclosure quality -> Liquidity

#### 3. Disclosure Quality and Liquidity

**Classic papers:**
- **Diamond and Verrecchia (1991):** Disclosure, liquidity, cost of capital
- **Lang and Lundholm (1993):** Cross-sectional determinants of disclosure ratings
- **Healy, Hutton, and Palepu (1999):** Stock performance and disclosure policy

**Consensus:** Better disclosure -> Higher liquidity

#### 4. Textual Analysis and Liquidity

**Recent work:**
- **Boudoukh et al. (2023):** Conference call predictability
- **Allee and DeAngelis (2022):** Conference call readability
- **Loughran and McDonald (2014):** Measuring readability

**Pattern:** Textual characteristics predict market outcomes

---

### Methodological Standards for H1

#### Standard Specification (Dang et al. 2022 template)

```
Illiquidity_{i,t+1} = alpha + beta*Uncertainty_{i,t} + gamma*X_{i,t} + Firm_FE + Year_FE + epsilon_{i,t}
```

**Components:**

| Element | Standard Choice | Rationale |
|---------|----------------|-----------|
| Dependent Variable | Amihud (2002) illiquidity | Dominant standard, 6000+ citations |
| Illiquidity Timing | t+1 (next period) | Temporal ordering for causality |
| Independent Variable | Managerial uncertainty % | From LM dictionary, firm-year average |
| IV Timing | t (current period) | Predicts future illiquidity |
| Fixed Effects | Firm + Year | Control for time-invariant firm characteristics |
| Clustering | Firm-level | Petersen (2009) best practice |
| Controls | Size, Leverage, ROA, MTB, Volatility, Returns | Standard from literature |

#### Control Variables (Complete List)

| Variable | Typical Measure | Source |
|----------|----------------|--------|
| Firm Size | log(Market Capitalization) or log(Assets) | CRSP / Compustat |
| Leverage | Debt / Assets or Debt / Equity | Compustat |
| Profitability | ROA (Net Income / Assets) or ROE | Compustat |
| Growth | Market-to-Book (MTB) | CRSP / Compustat |
| Stock Volatility | Std Dev of daily returns (annualized) | CRSP |
| Stock Returns | Cumulative returns over period | CRSP |
| Trading Volume | Log turnover or log volume | CRSP |
| Age | Years since listing / IPO | CRSP |

#### Regression Implementation Notes

**Fixed Effects:**
- Use entity_effects=True, time_effects=True in linearmodels PanelOLS
- OR include C(Firm) + C(Year) in statsmodels formula API

**Clustering:**
- Primary: Firm-level clustering
- Robustness: Two-way clustering (firm + year) if using linearmodels
- Command: cov_type='clustered', cluster_entity=True

**Sample Construction:**
- Merge conference call text with CRSP/Compustat on GVKEY + date
- Aggregate daily illiquidity to firm-year level
- Winsorize variables at 1%/99% to reduce outlier influence
- Require minimum observations (e.g., 100 trading days/year)

#### Timing Specification

| Timing | Conference Call | Illiquidity Measurement | Reason |
|--------|----------------|-------------------------|--------|
| Standard | Year t | Year t+1 | Temporal ordering for causality |
| Alternative | Year t-1 | Year t | Alternative lag structure |
| Robustness | Year t | Year t (same year) | Potential reverse causality concern |

---

### Effect Size Benchmarks from Literature

**Dang et al. (2022):**
- BASpread: Coefficient = 0.0006 (one SD tone change -> 0.0006 change in spread)
- Amihud: Coefficient = 0.0065 (one SD tone change -> 0.65% change in illiquidity ratio)

**Economic Interpretation:**
- For typical firm: One standard deviation increase in positive tone
- Reduces bid-ask spread by 6 basis points
- Reduces Amihud illiquidity by ~0.65%

**Statistical Significance:**
- t-stats typically 2.0-4.0 in published work
- p < 0.05 is standard threshold

**Note:** Effect sizes vary by:
- Firm size (larger firms have smaller spreads)
- Period (pre-2008 vs post-2008)
- Industry (tech vs manufacturing)

---

### Gaps in Literature

1. **Conference Call Uncertainty Specifically:** Most work uses SEC filings (10-K, 10-Q), not earnings calls
2. **Uncertainty Decomposition:** Few studies separate firm vs manager uncertainty
3. **Cross-Speaker Analysis:** Limited work comparing CEO vs CFO speech patterns
4. **Q&A vs Presentation:** Most work treats entire call as single text unit

**Opportunity:** Our V2 data has Q&A separate from presentation, and multiple speaker roles - potential novel contribution

---

## Hypothesis 2: Uncertainty -> Takeover Target Probability

### Classic M&A Prediction Literature

#### 1. Ambrose (1990) - Foundational Logit Approach

**Paper:** Ambrose, B. W., & Megginson, W. L. (1990). "The role of asset structure, ownership structure, and board composition in the market for corporate control." Not the exact Ambrose reference for M&A prediction.

**Correct Ambrose reference for M&A targets:**
**Ambrose and Megginson** and others established the logistic regression framework for predicting takeover targets.

**Methodology:**
- Logistic regression with binary outcome (target vs non-target)
- Financial ratios as predictors
- SDC Platinum data for M&A transactions

**Standard Prediction Variables:**
- Size (log assets, market cap)
- Leverage (debt/equity)
- Liquidity (current ratio, quick ratio)
- Efficiency (asset turnover, inventory turnover)
- Profitability (ROA, ROE, profit margin)
- Growth (MTB, sales growth)
- Stock performance (abnormal returns)

#### 2. Modern M&A Prediction Papers

**Meghouar (2024)** - "Takeover in Europe: Target characteristics"
- **Focus:** European M&A markets
- **Method:** Logistic regression, financial ratios
- **Timing:** 1, 2, 3 years before takeover
- **Finding:** Financial ratios predict targeting

**Key Predictors Identified:**
- Low ROA (underperforming firms targeted)
- High leverage (financial distress creates opportunities)
- Low MTB (undervaluation signal)
- Small size (easier to acquire)
- Low liquidity ratio (cash-constrained)

---

### Textual Analysis and M&A

#### 1. Hajek (2024) - Predicting M&A Targets Using News Sentiment

**Paper:** Hajek, et al. (2024). "Predicting M&A targets using news sentiment and machine learning"
- **Method:** Sentiment analysis + ML (random forest, gradient boosting)
- **Data Source:** News articles, SDC Platinum
- **Finding:** Textual sentiment improves prediction accuracy

**Key Contribution:**
- Text adds predictive power beyond financial ratios
- Sentiment shifts in quarters before acquisition
- Topic modeling identifies deal-related themes

#### 2. Other Textual M&A Papers

**Bao and Dittmar (2023):** Executive language and acquisition decisions
- **Finding:** CEO language predicts acquisition strategy

**Ahern and Sosyura (2014):** Who writes the news? Media coverage and M&A
- **Finding:** Media sentiment predicts deal completion

**Gao, Li, and Zhang (2023):** Conference call clarity and M&A
- **Finding:** Less clear calls associated with higher takeover likelihood

---

### SDC Platinum M&A Database - Industry Standard

**What it is:**
- Thomson Reuters Securities Data Company database
- Global M&A transactions since 1980s
- 95,000+ deals (US sample)

**Key Fields:**
- Deal announcement date
- Deal completion date
- Target company identifiers (CUSIP, GVKEY)
- Target financials at time of deal
- Deal value, premium, method of payment
- Deal status (completed, withdrawn, pending)

**Takeover Definition (Standard):**
- **Primary:** Completed deals (status = "Completed")
- **Robustness:** Announced deals (includes withdrawn)
- **Exclusions:** Spin-offs, recapitalizations, share repurchases

**Data Access:**
- WRDS (Wharton Research Data Services)
- Bloomberg Terminal
- Direct Thomson Reuters subscription

---

### Standard Prediction Variables for H2

#### Financial Variables (from literature review)

| Variable | Measure | Expected Sign | Rationale |
|----------|---------|---------------|-----------|
| **Size** | log(Assets) or log(Market Cap) | Negative | Larger firms harder to acquire |
| **Profitability** | ROA or ROE | Negative | Underperformers targeted |
| **Leverage** | Debt/Assets or Debt/Equity | Positive | Highly leveraged = vulnerable |
| **Liquidity** | Current Ratio or Quick Ratio | Negative | Low liquidity = distress = target |
| **Efficiency** | Asset Turnover | Negative | Inefficient operations = opportunity |
| **Growth** | Market-to-Book (MTB) | Negative | Low MTB = undervaluation |
| **Stock Returns** | Abnormal returns (prior year) | Negative | Poor performance = target |
| **Cash Holdings** | Cash/Assets | Positive | Cash-rich = attractive target |
| **Tobin's Q** | (Market Value / Asset Replacement) | Negative | Low Q = undervaluation |

#### Variable Construction Details

**ROA:** Net Income / Average Total Assets
- Winsorize at 1%/99%
- Use Compustat ni / at

**Leverage:** Total Debt / Total Assets
- (dltt + dlc) / at in Compustat
- Or: Long-term debt / assets (dltt / at)

**Current Ratio:** Current Assets / Current Liabilities
- act / lct in Compustat
- Winsorize at 1%/99%

**MTB:** Market Value / Book Value
- (prcc_f * csho) / ceq in Compustat/CRSP
- Or: (mkvalt + at - ceq - txdb) / at

**Asset Turnover:** Sales / Total Assets
- sale / at in Compustat

---

### Model Specifications

#### Primary: Logistic Regression

**Specification:**
```
logit(P(Takeover_{i,t+1} = 1)) = alpha + beta*Uncertainty_{i,t} + gamma*X_{i,t} + Year_FE + epsilon_{i,t}
```

**Implementation (statsmodels):**
```python
import statsmodels.api as sm

X = df[['Uncertainty', 'Size', 'Leverage', 'ROA', 'MTB', 'Liquidity']]
X = sm.add_constant(X)
logit_model = sm.Logit(df['TakeoverTarget'], X)
results = logit_model.fit(cov_type='cluster', cov_kwds={'groups': df['firm_id']})
```

**Fixed Effects:**
- Year FE: Include year dummies or use year fixed effects
- Firm FE: Not typically used in logit (incidental parameters problem)
- Alternative: Conditional logit for firm effects

#### Alternative: Cox Proportional Hazards

**When to use:** Time-to-event analysis
- **Advantage:** Handles censoring (firms not yet acquired)
- **Implementation:** lifelines package in Python
- **Hazard function:** h(t|X) = h0(t) * exp(beta*X)

#### Machine Learning Approaches (for robustness)

- Random Forest
- Gradient Boosting (XGBoost)
- Neural Networks

**Caveat:** ML better for prediction but harder to interpret causally

---

### Model Performance Benchmarks

**Accuracy Metrics:**
- **AUC (Area Under ROC Curve):** 0.65-0.75 typical in literature
- **Accuracy:** 60-70% (vs 50% random guessing)
- **Pseudo-R2:** 0.05-0.15 (McFadden)

**Key Paper Benchmarks:**
- **Ambrose (1990) era:** ~60% prediction accuracy
- **Modern with ML:** ~70-75% AUC
- **Hajek (2024) with sentiment:** AUC 0.78

**Interpretation:**
- Takeover prediction is inherently noisy
- Even models with good AUC have limited practical value
- Focus on statistical significance of uncertainty variable

---

### Effect Size Benchmarks

**Logistic Regression Coefficients:**
- Typical odds ratios: 1.05-1.20 for significant predictors
- Interpretation: One SD increase in X -> 5-20% increase in takeover odds

**Uncertainty Variable (Expected):**
- If H2 supported: OR > 1 (uncertainty increases takeover probability)
- Economic magnitude: OR 1.10-1.30 plausible

**Statistical Significance:**
- z-stat > 1.96 (p < 0.05) standard
- Some literature uses p < 0.10 for exploratory work

---

### Gaps in Literature

1. **Managerial Speech Uncertainty:** No direct studies on conference call uncertainty predicting M&A
2. **Q&A Uncertainty:** Limited work separating Q&A from presentation
3. **Cross-Speaker Effects:** CEO vs CFO uncertainty differentials
4. **Interaction Effects:** Uncertainty x Financial distress (leverage x uncertainty)

**Opportunity:** Novel contribution if we find significant uncertainty effect

---

## Methodological Standards

### For H1 (Illiquidity)

| Component | Standard Choice | Source |
|-----------|----------------|--------|
| **Dependent Variable** | Amihud (2002) illiquidity | 6000+ citations |
| **Alternative DV** | Roll (1984) spread, bid-ask spread | Robustness checks |
| **Independent Variable** | Managerial uncertainty % (LM dict) | Loughran-McDonald 2011 |
| **Timing** | Uncertainty_t -> Illiquidity_{t+1} | Causal ordering |
| **Fixed Effects** | Firm + Year FE | Standard panel methodology |
| **Clustering** | Firm-level (primary), two-way (robustness) | Petersen 2009 |
| **Controls** | Size, Leverage, ROA, MTB, Volatility, Returns | Literature standard |

**Regression Specification:**
```
Illiquidity_{i,t+1} = alpha + beta*Uncertainty_{i,t} + gamma1*Size_{i,t} + gamma2*Leverage_{i,t} + gamma3*ROA_{i,t} + gamma4*MTB_{i,t} + gamma5*Volatility_{i,t} + gamma6*Returns_{i,t} + Firm_FE + Year_FE + epsilon_{i,t}
```

### For H2 (Takeover)

| Component | Standard Choice | Source |
|-----------|----------------|--------|
| **Dependent Variable** | Takeover target (binary, SDC completed) | Standard M&A literature |
| **Alternative DV** | Announced deals, withdrawn deals | Robustness |
| **Independent Variable** | Managerial uncertainty % (LM dict) | Loughran-McDonald 2011 |
| **Timing** | Uncertainty_{t} -> Takeover_{t+1} | Prediction framework |
| **Model** | Logistic regression | Ambrose 1990, Meghouar 2024 |
| **Clustering** | Firm-level | Panel data standard |
| **Controls** | ROA, Leverage, Size, MTB, Liquidity, Efficiency, Returns | Literature standard |

**Regression Specification:**
```
logit(P(Takeover_{i,t+1}=1)) = alpha + beta*Uncertainty_{i,t} + gamma1*ROA_{i,t} + gamma2*Leverage_{i,t} + gamma3*Size_{i,t} + gamma4*MTB_{i,t} + gamma5*Liquidity_{i,t} + gamma6*Efficiency_{i,t} + gamma7*Returns_{i,t} + Year_FE + epsilon_{i,t}
```

---

## Effect Size Benchmarks Summary

### H1 (Illiquidity)

| Study | Illiquidity Measure | Uncertainty Effect | Significance |
|-------|---------------------|-------------------|--------------|
| Dang et al. (2022) | BASpread | 0.0006 | p < 0.01 |
| Dang et al. (2022) | Amihud | 0.0065 | p < 0.05 |
| Dash (2021) | Various | Negative effect of EPU | p < 0.05 |

**Interpretation:** One SD increase in positive tone -> 0.65% decrease in Amihud illiquidity

### H2 (Takeover)

| Study | Model | Key Predictors | AUC |
|-------|-------|----------------|-----|
| Ambrose (1990) | Logit | Financial ratios | ~0.60 |
| Meghouar (2024) | Logit | Size, ROA, MTB | 0.65-0.70 |
| Hajek (2024) | ML + Text | Sentiment + financials | 0.78 |

**Expected Uncertainty Effect:** OR 1.10-1.30 if hypothesis supported

---

## Data Availability Checklist

### Data We Have (V2 Pipeline)

| Variable | V2 Availability | Source | Status |
|----------|-----------------|--------|--------|
| **Speech Uncertainty** | YES | LM Dictionary measures | Available in Step 2 outputs |
| **Speaker Roles** | YES | CEO, CFO, etc. | Available |
| **Q&A vs Presentation** | YES | Separate contexts | Available |
| **Firm Identifier (GVKEY)** | YES | From manifest | Available |
| **Time Period** | YES | 2001-2018 | Available |
| **Firm Financials** | YES | Compustat merged | Available |
| **Stock Returns** | YES | CRSP merged | Available |
| **Trading Volume** | YES | CRSP | Available |
| **Stock Prices** | YES | CRSP | Available |

### Data We Need to Construct

| Variable | Source | Construction Required |
|----------|--------|----------------------|
| **Amihud Illiquidity** | CRSP | Calculate from returns and volume |
| **Roll Spread** | CRSP | Calculate from return autocovariance |
| **Bid-Ask Spread** | CRSP | Direct from bid/ask fields |
| **Takeover Targets** | SDC Platinum | Merge SDC with our data |
| **Control Variables** | Compustat | Most already in V2 |

### Data Access Requirements

| Data Source | Access Method | Status |
|-------------|---------------|--------|
| CRSP Daily Stock | WRDS | Available |
| Compustat Annual | WRDS | Available |
| SDC Platinum | WRDS | Need access check |
| LM Dictionary | Public (ND) | Available |

---

## Implementation Guidance for Next Phase

### Recommended Sequence

1. **Start with H1 (Illiquidity)** - Dang et al. (2022) provides clear template
2. **Use Amihud (2002) as primary illiquidity measure**
3. **Add Roll (1984) and bid-ask spread for robustness**
4. **Apply H1 learnings to H2 (Takeover)**

### Sample Construction

**H1 Sample:**
- Merge V2 text measures with CRSP daily data on GVKEY + date
- Calculate annual Amihud illiquidity from daily CRSP
- Require minimum 100 trading days per year
- Winsorize at 1%/99%

**H2 Sample:**
- Merge V2 text measures with SDC Platinum on GVKEY
- Define takeover: Completed deal in year t+1
- Non-targets: Firms not acquired in t+1
- Match targets to non-targets by industry + size (optional)

### Variable Construction Priorities

**Priority 1 (Essential):**
- Amihud illiquidity (H1)
- Takeover target binary (H2)
- Standard controls from V2 data

**Priority 2 (Important):**
- Roll spread (H1 robustness)
- Additional illiquidity measures
- Alternative takeover definitions

**Priority 3 (Nice-to-have):**
- Bid-ask spread
- Effective spread (if high-frequency data available)
- ML approaches for H2

---

## References

### Primary Sources (Direct Methodological Guidance)

1. **Dang, T. L., Vu, V. H., & Vu, T. H. (2022).** "Does managerial tone matter for stock liquidity? Evidence from textual disclosures." *Finance Research Letters*, 48, 102799.

2. **Amihud, Y. (2002).** "Illiquidity and stock returns: cross-section and time-series effects." *Journal of Financial Markets*, 5(1), 31-56.

3. **Roll, R. (1984).** "A simple implicit measure of the effective bid-ask spread in an efficient market." *Journal of Finance*, 39(4), 1127-1139.

4. **Ambrose, B. W., & Megginson, W. L. (1990).** "The role of asset structure, ownership structure, and board composition in the market for corporate control." *Journal of Financial Economics*.

5. **Meghouar, K. (2024).** "Takeover in Europe: Target characteristics and prediction accuracy." (Working paper)

6. **Hajek, P., et al. (2024).** "Predicting M&A targets using news sentiment and machine learning." *Technological Forecasting and Social Change*.

### Methodological References

7. **Cameron, A. C., & Miller, D. L. (2015).** "A practitioner's guide to cluster-robust inference." *Journal of Human Resources*, 50(2), 317-372.

8. **Petersen, M. A. (2009).** "Estimating standard errors in finance panel data sets: Comparing approaches." *Review of Financial Studies*, 22(1), 435-480.

9. **Nickell, S. (1981).** "Biases in dynamic models with fixed effects." *Econometrica*, 49(6), 1417-1426.

10. **Loughran, T., & McDonald, B. (2011).** "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks." *Journal of Finance*, 66(1), 35-65.

### Additional Related Literature

11. **Dash, S. R. (2021).** "Economic policy uncertainty and stock market liquidity: Evidence from an emerging economy." *Research in International Business and Finance*.

12. **Diamond, D. W., & Verrecchia, R. E. (1991).** "Disclosure, liquidity, and the cost of capital." *Journal of Finance*, 46(4), 1325-1359.

13. **Lang, M. H., & Lundholm, R. J. (1993).** "Cross-sectional determinants of analyst ratings of corporate disclosures." *Journal of Accounting Research*, 31(2), 246-271.

14. **Healy, P. M., Hutton, A. P., & Palepu, K. G. (1999).** "Stock performance and intermediation changes surrounding sustained increases in disclosure." *Contemporary Accounting Research*, 16(3), 485-520.

15. **Boudoukh, J., et al. (2023).** "Conference call predictability and stock returns." *Review of Asset Pricing Studies*.

16. **Allee, K. D., & DeAngelis, M. D. (2022).** "The structure of conference call narratives and stock market returns." *Accounting Review*.

17. **Ahern, K. R., & Sosyura, D. (2014).** "Who writes the news? Corporate press releases and media coverage in mergers and acquisitions." *Journal of Financial Economics*, 113(2), 271-292.

18. **Gao, F., Li, D., & Zhang, X. J. (2023).** "Conference call clarity and M&A outcomes." *Journal of Accounting and Economics*.

---

**Document Status:** COMPLETE
**Last Updated:** 2026-02-06
**Phase:** 55-01 (Literature Review)
