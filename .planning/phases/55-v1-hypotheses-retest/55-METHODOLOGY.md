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

### Data Sources

#### Summary of Data Requirements

| Data Category | Source | File/Database | Key Variables | Status |
|---------------|--------|---------------|---------------|--------|
| **Speech Uncertainty** | V2 Pipeline | 4_Outputs/2_Textual_Analysis/2.2_Variables/ | Manager_QA_Uncertainty_pct, CEO_QA_Uncertainty_pct, Manager_Pres_Uncertainty_pct, CEO_Pres_Uncertainty_pct | Available |
| **Stock Data** | CRSP Daily | 1_Inputs/CRSP/DSF/ | RET, VOL, PRC, SHROUT, BID, ASK | Available |
| **Financial Data** | Compustat Annual | 1_Inputs/Compustat/ | AT, DLTT, DLC, IB, CEQ, ACT, LCT | Available |
| **Sample Manifest** | V2 Pipeline | 4_Outputs/1_Sample/ | master_sample_manifest.parquet | Available |

#### CRSP Daily Stock File (DSF)

**Purpose:** Calculate Amihud illiquidity, Roll spread, bid-ask spread

**Key Fields:**
```
PERMNO  - Permanent security identifier (CRSP)
GVKEY   - Link to Compustat (via CCM)
date    - Trading date (YYYY-MM-DD format)
RET     - Daily return (decimal, adjusted)
VOL     - Daily trading volume (shares)
PRC     - Closing price (can be negative for bid/ask average)
SHROUT  - Shares outstanding (thousands)
BID     - Bid price (if available)
ASK     - Ask price (if available)
BIDLO   - Low bid or low price (depends on exchange)
ASKHI   - High ask or high price (depends on exchange)
```

**Data Access Notes:**
- Use CCM link to merge CRSP PERMNO with Compustat GVKEY
- Linktype: 'LU' (historical link) or 'LN' (primary link)
- Primary link selection: LINKPRIM='P' or 'L' in CCM

#### Compustat Annual Fundamentals

**Purpose:** Control variables (Size, Leverage, ROA, MTB, Current Ratio)

**Key Fields:**
```
GVKEY   - Global company key (Compustat identifier)
FYEAR   - Fiscal year
DATADATE - Fiscal year-end date
AT      - Total assets
DLTT    - Long-term debt
DLC     - Debt in current liabilities
IB      - Income before extraordinary items
CEQ     - Common equity
ACT     - Current assets
LCT     - Current liabilities
SALE    - Net sales
```

**Fiscal Year Convention:**
- Use FYEAR as primary time identifier
- Match speech uncertainty to fiscal year of earnings call
- Align with market data using calendar year closest to fiscal year-end

#### V2 Textual Analysis Outputs

**Purpose:** Independent variable (speech uncertainty measures)

**Location:** `4_Outputs/2_Textual_Analysis/2.2_Variables/`

**Available Variables:**
```
File: textual_variables_firmyear.parquet

Columns:
- gvkey       : Firm identifier
- fyear       : Fiscal year
- Manager_QA_Uncertainty_pct
- CEO_QA_Uncertainty_pct
- Manager_Pres_Uncertainty_pct
- CEO_Pres_Uncertainty_pct
- [Plus 20+ other textual measures from LM dictionary]
```

**Aggregation Level:** Already at firm-year level
- V2 pipeline averaged across all calls in each firm-year
- Separate calculations for QA vs Presentation contexts
- Separate calculations for speaker roles (CEO, CFO, Manager)

### Sample Construction

#### Starting Point: V2 Sample Manifest

**Source:** `4_Outputs/1_Sample/master_sample_manifest.parquet`

**V2 Sample Characteristics (from STATE.md):**
- Period: 2001-2018
- Firms: ~2,500+ unique firms
- Observations: ~30,000+ firm-years
- Exclusions already applied in V2

**Sample Selection Rationale:**
- Use V2 sample as base (already cleaned and validated)
- V2 sample includes firms with earnings call transcripts
- V2 sample excludes extreme outliers and invalid observations

#### Sample Construction Steps

**Step 1: Start from V2 sample manifest**
```python
# Load V2 sample
manifest = pd.read_parquet('4_Outputs/1_Sample/master_sample_manifest.parquet')
sample_firms = manifest[['gvkey', 'fyear']].drop_duplicates()
```

**Step 2: Merge CRSP daily stock data**
```python
# Load CRSP via CCM link
# CCM provides GVKEY -> PERMNO mapping
ccm = pd.read_sas('1_Inputs/CRSP/CCM.sas7bdat')

# Filter for valid links
ccm = ccm[(ccm['linktype'].isin(['LU', 'LN'])) &
          (ccm['linkprim'].isin(['P', 'C']))]

# Merge CRSP daily data
crsp_daily = pd.read_parquet('1_Inputs/CRSP/DSF_daily.parquet')
```

**Step 3: Calculate illiquidity measures at firm-year level**
```python
# For each firm-year:
# 1. Filter to trading days in fiscal year
# 2. Calculate Amihud ILLIQ
# 3. Calculate Roll spread
# 4. Require minimum trading days

def calculate_amihud(group):
    returns = abs(group['RET'])
    dollar_volume = abs(group['PRC']) * group['VOL']
    illiq = (returns / dollar_volume).mean()
    return illiq * 1e6  # Scale for interpretability

# Apply by firm-year
illiquidity = crsp_daily.groupby(['gvkey', 'fyear']).apply(calculate_amihud)
```

**Step 4: Merge Compustat financial data**
```python
# Load Compustat annual
compustat = pd.read_parquet('1_Inputs/Compustat/annual.parquet')

# Calculate control variables
compustat['Size'] = np.log(compustat['PRCC_F'] * compustat['CSHO'] * 1000)
compustat['Leverage'] = (compustat['DLTT'] + compustat['DLC']) / compustat['AT']
compustat['ROA'] = compustat['IB'] / compustat['AT']
compustat['MTB'] = (compustat['PRCC_F'] * compustat['CSHO']) / compustat['CEQ']
compustat['CurrentRatio'] = compustat['ACT'] / compustat['LCT']
```

**Step 5: Merge V2 uncertainty measures**
```python
# Load V2 textual variables
textual = pd.read_parquet('4_Outputs/2_Textual_Analysis/2.2_Variables/textual_variables_firmyear.parquet')

# Select uncertainty measures
uncertainty_vars = textual[['gvkey', 'fyear',
                            'Manager_QA_Uncertainty_pct',
                            'CEO_QA_Uncertainty_pct',
                            'Manager_Pres_Uncertainty_pct',
                            'CEO_Pres_Uncertainty_pct']]
```

**Step 6: Apply sample exclusions**

**Industry Exclusions:**
```python
# Exclude financial firms (SIC 6000-6999)
sample = sample[~sample['sic'].between(6000, 6999)]

# Exclude utilities (SIC 4900-4999)
sample = sample[~sample['sic'].between(4900, 4999)]
```

**Rationale:** Financial firms and utilities have different liquidity dynamics
- Financial firms: Balance sheet liquidity is business model
- Utilities: Regulated, less affected by information asymmetry

**Data Quality Filters:**
```python
# Require positive assets
sample = sample[sample['AT'] > 0]

# Require minimum trading days
sample = sample[sample['trading_days'] >= 50]  # For illiquidity calculation

# Require valid market cap
sample = sample[sample['MarketCap'] > 0]
```

**Step 7: Create lagged dependent variable**
```python
# Sort by firm and year
sample = sample.sort_values(['gvkey', 'fyear'])

# Create lagged illiquidity (t -> t+1)
sample['Illiquidity_lag1'] = sample.groupby('gvkey')['Illiquidity'].shift(-1)

# Final regression sample: match Uncertainty_t with Illiquidity_{t+1}
regression_sample = sample.dropna(subset=['Illiquidity_lag1'])
```

#### Final Sample Size Targets

**Expected Sample Size (based on V2):**
| Metric | Target | Rationale |
|--------|--------|-----------|
| **Firms** | 1,500 - 2,000 | After exclusions and data availability |
| **Firm-years** | 15,000 - 25,000 | After lag construction |
| **Time period** | 2002-2018 | V2 period minus first year for lag |

**Minimum Acceptable Sample:**
- 1,000+ firms (for panel FE estimation)
- 10,000+ firm-years (for power >80%)

**Power Analysis:**
- Based on V2 power analysis (99%+ for all hypotheses)
- Effect size detection: Cohen's d ~0.1 (small effects)
- With 15,000 obs: Power >90% for beta = 0.01 (small practical effect)

### Sample Descriptive Statistics

**Tables to Produce:**

**Table 1: Sample Composition**
| Year | N (Firms) | N (Obs) | Mean Illiquidity | SD Illiquidity |
|------|-----------|---------|------------------|----------------|
| 2002 | XXX | XXX | X.XXX | X.XXX |
| ... | ... | ... | ... | ... |
| 2018 | XXX | XXX | X.XXX | X.XXX |
| **Total** | **XXXX** | **XXXX** | **X.XXX** | **X.XXX** |

**Table 2: Variable Summary Statistics**
| Variable | N | Mean | SD | Min | 25th | 50th | 75th | Max |
|----------|---|------|----|-----|------|------|------|-----|
| Amihud Illiquidity | XXX | X.XXX | X.XXX | 0 | X.XXX | X.XXX | X.XXX | X.XXX |
| Manager_QA_Uncertainty_pct | XXX | X.XXX | X.XXX | X.XXX | X.XXX | X.XXX | X.XXX | X.XXX |
| CEO_QA_Uncertainty_pct | XXX | X.XXX | X.XXX | X.XXX | X.XXX | X.XXX | X.XXX | X.XXX |
| Size (log MCap) | XXX | X.XXX | X.XXX | X.XXX | X.XXX | X.XXX | X.XXX | X.XXX |
| Leverage | XXX | X.XXX | X.XXX | 0 | X.XXX | X.XXX | X.XXX | X.XXX |
| ROA | XXX | X.XXX | X.XXX | -X.XXX | X.XXX | X.XXX | X.XXX | X.XXX |
| MTB | XXX | X.XXX | X.XXX | -X.XXX | X.XXX | X.XXX | X.XXX | X.XXX |
| Volatility | XXX | X.XXX | X.XXX | 0 | X.XXX | X.XXX | X.XXX | X.XXX |

**Table 3: Correlation Matrix (Selected Variables)**
| Variable | 1 | 2 | 3 | 4 | 5 | 6 |
|----------|---|---|---|---|---|---|
| 1. Illiquidity | 1.00 | | | | | |
| 2. Uncertainty | r_12 | 1.00 | | | | |
| 3. Size | r_13 | r_23 | 1.00 | | | |
| 4. Leverage | r_14 | r_24 | r_34 | 1.00 | | |
| 5. ROA | r_15 | r_25 | r_35 | r_45 | 1.00 | |
| 6. Volatility | r_16 | r_26 | r_36 | r_46 | r_56 | 1.00 |

### Power Analysis

#### Statistical Power Calculation

**Based on V2 Power Analysis (Phase 41-03):**

V2 analysis confirmed 99%+ power for all hypotheses. This means:
- Sample size is NOT a limitation
- Null results from H1-H6 are NOT due to low power
- Small effects (Cohen's d ~0.1) are detectable

**Effect Size Benchmarks:**

| Effect Type | Cohen's d | Practical Significance | Detectable with V2 Sample |
|-------------|-----------|------------------------|---------------------------|
| Tiny | 0.01 | Negligible | Yes (>99% power) |
| Small | 0.10 | Minor economic impact | Yes (>99% power) |
| Medium | 0.30 | Moderate economic impact | Yes (>99% power) |
| Large | 0.50 | Substantial economic impact | Yes (>99% power) |

**Power Calculation Formula:**

For panel regression with Firm FE:
```
Power = P(reject H0 | H1 true)
      = 1 - beta

where:
beta = P(Type II error)
```

**Required Sample Size for 80% Power:**

With effect size f^2 = 0.02 (small), alpha = 0.05:
- Required N ~ 4,000 observations
- Our N ~ 20,000 observations
- Power > 99%

**Conclusion:** Sample size is sufficient. Any null result is NOT due to insufficient power.

### Robustness Specifications

#### Primary Specification (Spec 1)

**Model:** Panel OLS with Firm + Year FE
**Clustering:** Firm-level
**Timing:** Uncertainty_t -> Illiquidity_{t+1}
**IV:** Manager_QA_Uncertainty_pct
**DV:** Amihud illiquidity (scaled by 1e6)

```python
model = PanelOLS(
    Illiquidity_lag1 ~ Uncertainty + Size + Leverage + ROA + MTB +
    Volatility + Returns + CurrentRatio + Volume,
    entity_effects=True,
    time_effects=True
)
results = model.fit(cov_type='clustered', cluster_entity=True)
```

#### Specification 2: Firm FE Only

**Model:** Panel OLS with Firm FE (no Year FE)
**Clustering:** Firm-level
**Purpose:** Test if year effects absorb uncertainty variation

```python
model = PanelOLS(
    Illiquidity_lag1 ~ Uncertainty + Size + Leverage + ROA + MTB +
    Volatility + Returns + CurrentRatio + Volume,
    entity_effects=True,
    time_effects=False  # No year FE
)
results = model.fit(cov_type='clustered', cluster_entity=True)
```

#### Specification 3: Pooled OLS (No FE)

**Model:** Pooled OLS (no Firm FE, no Year FE)
**SE:** White robust SE (Newey-West for autocorrelation)
**Purpose:** Test between-firm variation (cross-sectional)

```python
import statsmodels.api as sm

X = df[['Uncertainty', 'Size', 'Leverage', 'ROA', 'MTB',
        'Volatility', 'Returns', 'CurrentRatio', 'Volume']]
X = sm.add_constant(X)
model = sm.OLS(df['Illiquidity_lag1'], X)
results = model.fit(cov_type='HAC', cov_kwds={'maxlags': 1})
```

#### Specification 4: Two-Way Clustering

**Model:** Panel OLS with Firm + Year FE
**Clustering:** Firm + Year (two-way)
**Purpose:** Robustness to correlation within firms and within years

```python
# Note: linearmodels doesn't support two-way clustering
# Use clustered_se from statsmodels
# Or manual two-way clustering adjustment
```

#### Specification 5: Alternative Dependent Variables

**5A: Roll Spread**
```python
model = PanelOLS(
    RollSpread_lag1 ~ Uncertainty + Size + Leverage + ROA + MTB +
    Volatility + Returns + CurrentRatio + Volume,
    entity_effects=True,
    time_effects=True
)
results = model.fit(cov_type='clustered', cluster_entity=True)
```

**5B: Log-Transformed Amihud**
```python
model = PanelOLS(
    log_Illiquidity_lag1 ~ Uncertainty + Size + Leverage + ROA + MTB +
    Volatility + Returns + CurrentRatio + Volume,
    entity_effects=True,
    time_effects=True
)
results = model.fit(cov_type='clustered', cluster_entity=True)
```

**5C: Bid-Ask Spread (if available)**
```python
model = PanelOLS(
    BidAskSpread_lag1 ~ Uncertainty + Size + Leverage + ROA + MTB +
    Volatility + Returns + CurrentRatio + Volume,
    entity_effects=True,
    time_effects=True
)
results = model.fit(cov_type='clustered', cluster_entity=True)
```

#### Specification 6: Alternative Independent Variables

**6A: CEO-only measures**
```python
# CEO_QA_Uncertainty_pct instead of Manager_QA_Uncertainty_pct
model = PanelOLS(
    Illiquidity_lag1 ~ CEO_QA_Uncertainty + controls,
    entity_effects=True,
    time_effects=True
)
```

**6B: Presentation-only measures**
```python
# Manager_Pres_Uncertainty_pct (prepared speech)
model = PanelOLS(
    Illiquidity_lag1 ~ Manager_Pres_Uncertainty + controls,
    entity_effects=True,
    time_effects=True
)
```

**6C: Uncertainty Gap (QA - Pres)**
```python
# Tests spontaneous vs prepared speech difference
df['Uncertainty_Gap'] = df['QA_Uncertainty'] - df['Pres_Uncertainty']
model = PanelOLS(
    Illiquidity_lag1 ~ Uncertainty_Gap + controls,
    entity_effects=True,
    time_effects=True
)
```

#### Specification 7: Alternative Timing

**7A: Same-year (Uncertainty_t -> Illiquidity_t)**
```python
# Tests reverse causality
model = PanelOLS(
    Illiquidity ~ Uncertainty + controls,
    entity_effects=True,
    time_effects=True
)
```

**7B: Two-year lag (Uncertainty_{t-1} -> Illiquidity_t)**
```python
# Tests persistence
df['Uncertainty_lag1'] = df.groupby('gvkey')['Uncertainty'].shift(1)
model = PanelOLS(
    Illiquidity ~ Uncertainty_lag1 + controls,
    entity_effects=True,
    time_effects=True
)
```

#### Robustness Summary Table

| Spec | DV | IV | FE | Clustering | Timing | Purpose |
|------|-----|-----|----|------------|--------|---------|
| 1 (Primary) | Amihud | Manager_QA | Firm+Year | Firm | t -> t+1 | Main test |
| 2 | Amihud | Manager_QA | Firm only | Firm | t -> t+1 | Year effects sensitivity |
| 3 | Amihud | Manager_QA | None | White | t -> t+1 | Between-firm variation |
| 4 | Amihud | Manager_QA | Firm+Year | Firm+Year | t -> t+1 | Two-way clustering |
| 5A | Roll | Manager_QA | Firm+Year | Firm | t -> t+1 | Alternative DV |
| 5B | log(Amihud) | Manager_QA | Firm+Year | Firm | t -> t+1 | Transform robustness |
| 6A | Amihud | CEO_QA | Firm+Year | Firm | t -> t+1 | CEO-only IV |
| 6B | Amihud | Manager_Pres | Firm+Year | Firm | t -> t+1 | Prepared speech |
| 6C | Amihud | Uncertainty_Gap | Firm+Year | Firm | t -> t+1 | Spontaneity effect |
| 7A | Amihud | Manager_QA | Firm+Year | Firm | t -> t | Reverse causality |
| 7B | Amihud | Manager_QA_lag1 | Firm+Year | Firm | t-1 -> t | Persistence |

**Total Robustness Specifications:** 11 specifications
**Primary Reporting:** Spec 1
**Full Reporting:** All 11 specs (pre-registered approach)

---

## Hypothesis 2: Managerial Speech Uncertainty -> Takeover Target Probability

### Hypothesis Statement

**H8a:** Higher managerial speech uncertainty predicts HIGHER takeover target probability.

**Directional Prediction:**
- beta_Uncertainty > 0 in logit model (uncertainty increases takeover odds)
- More uncertain speech -> signals weakness -> attracts acquirers

**Theoretical Mechanism:**
1. Managerial uncertainty increases perceived information asymmetry
2. High uncertainty signals managerial weakness or lack of clarity
3. Perceived weakness makes firm vulnerable to acquisition
4. Acquirers target firms with undervalued assets or poor management
5. Result: Higher takeover probability

**Counter-Hypothesis (Null):**
- No relationship between speech uncertainty and takeover probability
- Any observed correlation is due to omitted variables or sampling variation

### Dependent Variables

#### Primary: Binary Takeover Indicator

**Definition:**
```
TakeoverTarget_{i,t+1} = 1  if firm i is target in completed deal in year t+1
                         = 0  otherwise (non-target firm)
```

**Data Source:** SDC Platinum M&A Database
- Location: `1_Inputs/SDC/`
- Primary table: M&A transactions
- Target identification: Company-level matching

**Key Fields (SDC):**
```
DealID       - Unique deal identifier
TargetGVKEY  - Target company identifier (if available)
TargetCUSIP  - Target CUSIP
TargetName   - Target company name
AnnounceDate - Deal announcement date
CompleteDate - Deal completion date
DealStatus   - Completed, Withdrawn, Pending
DealValue    - Transaction value (USD)
```

**Takeover Definition (Primary):**
1. **Completed deals only** (DealStatus = "Completed")
2. **Target identification:** Match on GVKEY via CUSIP
3. **Timing:** Deal announcement/completion in year t+1
4. **Exclusions:**
   - Spin-offs, recapitalizations, share repurchases
   - Private deals (no public target data)
   - Partial acquisitions (<50% ownership)

**Rationale for Completed Deals:**
- Only completed deals represent actual change of control
- Withdrawn deals may reflect failed negotiations (different mechanism)
- Aligns with standard M&A literature (Ambrose 1990, Meghouar 2024)

#### Robustness 1: Announced Deals

**Definition:**
```
TakeoverTarget_{i,t+1} = 1  if firm i is target in announced deal (completed or withdrawn)
                         = 0  otherwise
```

**Purpose:**
- Tests if uncertainty predicts deal initiation (not just completion)
- Includes deals that were announced but not completed
- May capture different mechanism (uncertainty -> deal interest)

#### Robustness 2: Hostile Deals Only

**Definition:**
```
TakeoverTarget_{i,t+1} = 1  if firm i is target in hostile deal in year t+1
                         = 0  otherwise
```

**Purpose:**
- Tests if uncertainty specifically predicts hostile takeovers
- Hostile deals may be more sensitive to perceived weakness
- Smaller sample but stronger mechanism

#### Robustness 3: Time-to-Event (Cox Proportional Hazards)

**Definition:**
```
Survival time = Time from observation to takeover (or censoring)
```

**Model:**
```
h(t|X) = h0(t) * exp(beta1*Uncertainty + gamma*Controls)
```

**Where:**
- h(t|X) = Hazard rate at time t
- h0(t) = Baseline hazard
- beta1 = Log hazard ratio for uncertainty

**Censoring:**
- Event: Takeover completion
- Censored: End of sample period without takeover
- Censored: Delisting not due to M&A

**Purpose:**
- Uses time-to-event information more efficiently
- Handles varying time horizons across firms
- Standard survival analysis approach

**Implementation:**
```python
from lifelines import CoxPHFitter

# Prepare data: each row is a firm-year observation
df['time_to_takeover'] = ...  # Calculate time until takeover or censoring
df['takeover_event'] = ...     # 1 if takeover, 0 if censored

# Fit Cox model
cph = CoxPHFitter()
cph.fit(df, duration_col='time_to_takeover', event_col='takeover_event',
        covariates=['Uncertainty', 'Size', 'Leverage', 'ROA', 'MTB', 'Liquidity', 'Efficiency', 'Returns'])
```

### Independent Variables

#### Primary: Managerial Speech Uncertainty Measures

Same as Hypothesis 1 (H7):

**V2 Uncertainty Variables:**
```
Manager_QA_Uncertainty_pct     - Manager uncertainty in Q&A context
CEO_QA_Uncertainty_pct         - CEO uncertainty in Q&A context
Manager_Pres_Uncertainty_pct   - Manager uncertainty in Presentation context
CEO_Pres_Uncertainty_pct       - CEO uncertainty in Presentation context
```

**Timing Specification:**
- Uncertainty measured at year t (speech during fiscal year t)
- Predicts takeover status at year t+1 (forward-looking)
- Ensures temporal ordering for causal interpretation

#### Alternative Independent Variables

For robustness testing:
```
QA_Uncertainty_pct             - Combined Q&A uncertainty (all speakers)
Pres_Uncertainty_pct           - Combined Presentation uncertainty
Uncertainty_Gap                - QA_Uncertainty - Pres_Uncertainty
CEO_Uncertainty_Avg            - CEO uncertainty across both contexts
Uncertainty_Change             - Change in uncertainty from t-1 to t
```

**Uncertainty Change Specification:**
```python
# Test if increasing uncertainty predicts takeover
df['Uncertainty_Change'] = df.groupby('gvkey')['Manager_QA_Uncertainty_pct'].diff()
```

### Control Variables

#### Required Controls (from M&A prediction literature)

| Variable | Measure | Compustat Field | Expected Sign | Rationale |
|----------|---------|----------------|---------------|-----------|
| **Size** | log(Assets) | log(AT) | Negative | Larger firms harder to acquire |
| **Leverage** | Total Debt / Assets | (DLTT + DLC) / AT | Positive | Highly leveraged = vulnerable |
| **ROA** | Return on Assets | IB / AT | Negative | Underperformers targeted |
| **MTB** | Market-to-Book | (PRC * CSHO) / CEQ | Negative | Low MTB = undervaluation |
| **Liquidity** | Current Ratio | ACT / LCT | Negative | Low liquidity = distress = target |
| **Efficiency** | Asset Turnover | SALE / AT | Negative | Inefficient operations = opportunity |
| **Stock Returns** | Abnormal returns | Calculation from CRSP | Negative | Poor performance = target |
| **R&D Intensity** | R&D / Assets | XRD / AT | Ambiguous | Innovation attracts or protects |

#### Control Variable Construction Details

**Firm Size:**
```
Size_{i,t} = log(AT_{i,t})
```
Use log of total assets (book value)
Larger firms require more capital to acquire -> less likely targets

**Leverage:**
```
Leverage_{i,t} = (DLTT_{i,t} + DLC_{i,t}) / AT_{i,t}
```
Winsorize at 1%/99%
High leverage -> financial distress -> acquisition target

**ROA (Return on Assets):**
```
ROA_{i,t} = IB_{i,t} / AT_{i,t}
```
Winsorize at 1%/99%
Low ROA -> underperformance -> acquisition target

**MTB (Market-to-Book):**
```
MTB_{i,t} = (PRC_{i,t} * CSHO_{i,t}) / CEQ_{i,t}
```
Low MTB -> undervalued assets -> acquisition target

**Liquidity (Current Ratio):**
```
Liquidity_{i,t} = ACT_{i,t} / LCT_{i,t}
```
Winsorize at 1%/99%
Low liquidity -> cash-constrained -> vulnerable

**Efficiency (Asset Turnover):**
```
Efficiency_{i,t} = SALE_{i,t} / AT_{i,t}
```
Winsorize at 1%/99%
Low efficiency -> operational improvement opportunity

**Stock Returns:**
```
Returns_{i,t} = product_{d=1}^{D}(1 + RET_{i,t,d}) - 1 - MarketReturn_{i,t}
```
Calculate abnormal returns (market-adjusted)
Negative abnormal returns -> poor performance -> target

**R&D Intensity:**
```
RD_Intensity_{i,t} = XRD_{i,t} / AT_{i,t}
```
Set to 0 if missing (many firms don't report R&D)
Interpretation: High R&D may attract (innovation value) or protect (complexity)

### Primary Regression Equation

#### Specification 1 (Primary): Logit with Firm + Year FE, Firm-Clustered SE

**Equation:**
```
logit(P(TakeoverTarget_{i,t+1}=1)) = beta0 + beta1*Uncertainty_{i,t}
                                     + gamma1*Size_{i,t}
                                     + gamma2*Leverage_{i,t}
                                     + gamma3*ROA_{i,t}
                                     + gamma4*MTB_{i,t}
                                     + gamma5*Liquidity_{i,t}
                                     + gamma6*Efficiency_{i,t}
                                     + gamma7*Returns_{i,t}
                                     + gamma8*RD_Intensity_{i,t}
                                     + alpha_i
                                     + delta_t
                                     + epsilon_{i,t}
```

**Where:**
- alpha_i = Firm fixed effects (controls for time-invariant firm characteristics)
- delta_t = Year fixed effects (controls for macroeconomic M&A waves)
- epsilon_{i,t} = Error term
- SE clustered at firm level

**Implementation (statsmodels):**
```python
import statsmodels.api as sm
import statsmodels.formula.api as smf

# Logit regression with firm clustering
formula = ('TakeoverTarget_lag1 ~ Uncertainty + Size + Leverage + ROA + MTB + '
           'Liquidity + Efficiency + Returns + RD_Intensity + '
           'C(firm_id) + C(fyear)')

# Note: statsmodels doesn't directly support FE in Logit
# Use conditional logit or include firm dummies manually
# Alternative: Use firm-clustering without FE

# Primary specification (with clustering)
model = sm.Logit(
    df['TakeoverTarget_lag1'],
    sm.add_constant(df[['Uncertainty', 'Size', 'Leverage', 'ROA', 'MTB',
                        'Liquidity', 'Efficiency', 'Returns', 'RD_Intensity',
                        'fyear_dummies']])
)

results = model.fit(
    cov_type='cluster',
    cov_kwds={'groups': df['gvkey']}
)
```

**Note on Firm FE in Logit:**
- Traditional logit with firm dummies suffers from incidental parameters problem
- Alternatives:
  1. Conditional logit (clogit) - handles firm effects correctly
  2. No firm FE, include firm-level controls
  3. Random effects logit

**Recommended Approach:**
- Primary: Year FE only, firm-clustered SE
- Robustness: Conditional logit for firm effects

**Hypothesis Test:**
- H0: beta1 = 0 (no effect of uncertainty on takeover probability)
- H1: beta1 > 0 (uncertainty increases takeover probability)
- Test: One-tailed z-test (directional hypothesis)
- Significance: p < 0.05 (primary), FDR-corrected for multiple IVs

#### Timing Justification

**Why Uncertainty_t -> Takeover_{t+1}:**

1. **Causal Ordering:** Speech in year t cannot affect takeover decisions in same year
2. **Deal Timing:** M&A transactions take time to negotiate and complete
3. **Information Incorporation:** Acquirers gradually assess target quality
4. **Alignment with Literature:** Standard prediction framework uses t -> t+1

**Alternative Timings (for robustness):**
- Uncertainty_t -> Takeover_t (same-year) - concurrent relationship
- Uncertainty_{t-1} -> Takeover_t (longer lag) - persistence
- Uncertainty_t -> Takeover_{t+2} (two-year horizon) - longer prediction window

### Data Sources

#### Summary of Data Requirements for H2

| Data Category | Source | File/Database | Key Variables | Status |
|---------------|--------|---------------|---------------|--------|
| **Speech Uncertainty** | V2 Pipeline | 4_Outputs/2_Textual_Analysis/2.2_Variables/ | Manager_QA_Uncertainty_pct, etc. | Available |
| **M&A Data** | SDC Platinum | 1_Inputs/SDC/ | DealID, TargetGVKEY, AnnounceDate, CompleteDate, DealStatus | Need verification |
| **Financial Data** | Compustat Annual | 1_Inputs/Compustat/ | AT, DLTT, DLC, IB, CEQ, ACT, LCT, SALE, XRD | Available |
| **Stock Data** | CRSP Daily | 1_Inputs/CRSP/DSF/ | RET, PRC, CSHO (for abnormal returns) | Available |

#### SDC Platinum M&A Database

**Purpose:** Identify takeover targets

**Data Access:**
- WRDS (Wharton Research Data Services)
- Bloomberg Terminal
- Thomson Reuters direct subscription

**Key Fields for Matching:**
```
DealID          - Unique deal identifier
TargetNation    - Target country (filter = "United States")
TargetPrimarySICCode - Target SIC industry
TargetCUSIP     - Target CUSIP (6-digit or 8-digit)
TargetName      - Target company name
AnnounceDate    - Deal announcement date
EffectiveDate   - Deal completion date
DealStatus      - "Completed", "Withdrawn", "Pending"
DealValue       - Transaction value (millions USD)
AcquisitionFlag - "A" for asset acquisition, "S" for stock acquisition
PublicTarget    - "Y" if target is public company
```

**Matching Procedure:**

**Step 1: Load SDC data**
```python
sdc = pd.read_sas('1_Inputs/SDC/SDC_M&A.sas7bdat')

# Filter to relevant deals
sdc = sdc[
    (sdc['TargetNation'] == 'United States') &
    (sdc['PublicTarget'] == 'Y') &
    (sdc['DealStatus'].isin(['Completed', 'Withdrawn'])) &
    (sdc['DealValue'] > 1000000)  # Exclude micro-deals
]
```

**Step 2: Match to GVKEY via CUSIP**
```python
# Use CUSIP-Compustat link table
cusip_link = pd.read_sas('1_Inputs/Compustat/cusip_link.sas7bdat')

# Merge SDC with Compustat via CUSIP
sdc['TargetCUSIP6'] = sdc['TargetCUSIP'].str[:6]
sdc = sdc.merge(cusip_link, left_on='TargetCUSIP6', right_on='CUSIP', how='left')
sdc_gvkey = sdc[sdc['GVKEY'].notna()]
```

**Step 3: Create takeover indicator**
```python
# Extract announcement year
sdc_gvkey['announcement_year'] = pd.to_datetime(sdc_gvkey['AnnounceDate']).dt.year

# Create target indicator
takeovers = sdc_gvkey[['GVKEY', 'announcement_year', 'DealID', 'DealStatus']].drop_duplicates()
takeovers['TakeoverTarget'] = 1
```

**Step 4: Merge with sample**
```python
# Merge takeover indicator to firm-year data
df = df.merge(
    takeovers[['GVKEY', 'announcement_year', 'TakeoverTarget', 'DealStatus']],
    left_on=['gvkey', 'fyear'],
    right_on=['GVKEY', 'announcement_year'],
    how='left'
)

# Set non-targets to 0
df['TakeoverTarget'] = df['TakeoverTarget'].fillna(0)

# Create lagged takeover indicator (Uncertainty_t -> Takeover_{t+1})
df['TakeoverTarget_lag1'] = df.groupby('gvkey')['TakeoverTarget'].shift(-1)
```

### Sample Construction

#### Starting Point: Same as H1

**Source:** V2 sample manifest
**Period:** 2002-2018
**Firms:** ~2,500+ unique firms
**Observations:** ~30,000+ firm-years

#### Sample Construction Steps

**Step 1: Start from H1 sample**
- Use the same sample construction as Hypothesis 1
- Already includes firms with speech uncertainty data
- Already merged with CRSP and Compustat

**Step 2: Merge SDC takeover data**
- Follow matching procedure above
- Match on GVKEY + year
- Keep both completed and announced deals (for robustness)

**Step 3: Apply M&A-specific exclusions**
```python
# Exclude deals where target is not our sample firms
# (some SDC deals may be outside our V2 sample)

# Require deal value >= $1M (exclude micro-deals)
sdc = sdc[sdc['DealValue'] >= 1000000]

# Exclude spin-offs and recapitalizations
sdc = sdc[~sdc['DealType'].isin(['Spinoff', 'Recapitalization'])]
```

**Step 4: Create target and non-target samples**
```python
# Targets: Firms with takeover in t+1
targets = df[df['TakeoverTarget_lag1'] == 1]

# Non-targets: Firms without takeover in t+1
non_targets = df[df['TakeoverTarget_lag1'] == 0]

# Optional: Match targets to non-targets by industry + size
# (for case-control matching)
```

**Step 5: Final regression sample**
```python
# Combine targets and non-targets
regression_sample = pd.concat([targets, non_targets])

# Require all controls available
regression_sample = regression_sample.dropna(
    subset=['Uncertainty', 'Size', 'Leverage', 'ROA', 'MTB',
            'Liquidity', 'Efficiency', 'Returns']
)
```

#### Final Sample Size Targets

**Expected Sample Size (based on V2 + SDC):**
| Metric | Target | Rationale |
|--------|--------|-----------|
| **Firms** | 2,000 - 2,500 | V2 sample with SDC matching |
| **Firm-years** | 25,000 - 35,000 | Before takeover indicator |
| **Takeover events** | 200 - 400 | ~1-2% annual takeover rate |
| **Non-target obs** | 24,000 - 34,000 | Remaining observations |

**Takeover Rate Assumptions:**
- Historical M&A activity: ~1-2% of public firms per year
- With 2,000 firms over 15 years: 300-600 expected events
- Sufficient for logistic regression (rule of thumb: 10 events per predictor)
- We have 8-9 predictors: need ~80-100 events minimum

**Power Analysis:**
- Based on logistic regression power calculations
- With 300 events and 25,000 non-events
- Power >90% to detect odds ratio of 1.15 (15% increase per SD)
- Small effects (OR < 1.10) may be underpowered

### Robustness Specifications

#### Specification 1 (Primary): Logit with Year FE, Firm-Clustered SE

**Model:** Logistic regression
**FE:** Year dummies (no firm FE due to incidental parameters)
**Clustering:** Firm-level
**Timing:** Uncertainty_t -> Takeover_{t+1}
**IV:** Manager_QA_Uncertainty_pct
**DV:** Binary takeover indicator (completed deals)

```python
import statsmodels.api as sm

# Add year dummies
year_dummies = pd.get_dummies(df['fyear'], prefix='Y', drop_first=True)
X = pd.concat([
    df[['Uncertainty', 'Size', 'Leverage', 'ROA', 'MTB',
        'Liquidity', 'Efficiency', 'Returns', 'RD_Intensity']],
    year_dummies
], axis=1)
X = sm.add_constant(X)

# Logit with firm clustering
model = sm.Logit(df['TakeoverTarget_lag1'], X)
results = model.fit(cov_type='cluster', cov_kwds={'groups': df['gvkey']})
```

#### Specification 2: Pooled Logit (No FE)

**Model:** Logistic regression without fixed effects
**SE:** Firm-clustered
**Purpose:** Test sensitivity to FE inclusion

```python
model = sm.Logit(df['TakeoverTarget_lag1'],
                 sm.add_constant(df[['Uncertainty', 'Size', 'Leverage', 'ROA', 'MTB',
                                     'Liquidity', 'Efficiency', 'Returns', 'RD_Intensity']]))
results = model.fit(cov_type='cluster', cov_kwds={'groups': df['gvkey']})
```

#### Specification 3: Cox Proportional Hazards

**Model:** Survival analysis (time-to-event)
**Purpose:** Uses time information more efficiently

```python
from lifelines import CoxPHFitter

# Prepare survival data
survival_df = df.copy()
survival_df['duration'] = ...  # Time to takeover or censoring
survival_df['event'] = ...     # 1 if takeover, 0 if censored

cph = CoxPHFitter()
cph.fit(survival_df, duration_col='duration', event_col='event',
        covariates=['Uncertainty', 'Size', 'Leverage', 'ROA', 'MTB',
                    'Liquidity', 'Efficiency', 'Returns'])
```

#### Specification 4: Conditional Logit (Firm Effects)

**Model:** Conditional logistic regression with firm effects
**Purpose:** Properly handles firm fixed effects in logit

```python
from statsmodels.discrete.conditional_models import ConditionalLogit

# Conditional logit handles firm effects correctly
# Requires grouping by firm
clogit = ConditionalLogit(
    df['TakeoverTarget_lag1'],
    df[['Uncertainty', 'Size', 'Leverage', 'ROA', 'MTB',
        'Liquidity', 'Efficiency', 'Returns', 'RD_Intensity']],
    groups=df['gvkey']
)
results = clogit.fit()
```

#### Specification 5: Alternative Dependent Variables

**5A: Announced Deals**
```python
# Include withdrawn deals as takeover targets
model = sm.Logit(df['TakeoverAnnounced_lag1'], X)
results = model.fit(cov_type='cluster', cov_kwds={'groups': df['gvkey']})
```

**5B: Hostile Deals Only**
```python
# Subset to hostile deals
hostile = df[df['DealAttitude'] == 'Hostile']
model = sm.Logit(hostile['TakeoverTarget_lag1'],
                 sm.add_constant(hostile[covariates]))
results = model.fit(cov_type='cluster', cov_kwds={'groups': hostile['gvkey']})
```

**5C: Deal Value (Continuous)**
```python
# For targets only: log(DealValue)
# OLS regression for transaction value
targets_only = df[df['TakeoverTarget_lag1'] == 1]
model = sm.OLS(
    np.log(targets_only['DealValue']),
    sm.add_constant(targets_only[['Uncertainty', 'Size', 'Leverage', ...]])
)
results = model.fit(cov_type='cluster', cov_kwds={'groups': targets_only['gvkey']})
```

#### Specification 6: Alternative Independent Variables

**6A: CEO-only measures**
```python
# CEO_QA_Uncertainty_pct instead of Manager_QA_Uncertainty_pct
X = df[['CEO_QA_Uncertainty', 'Size', 'Leverage', ...]]
```

**6B: Presentation-only measures**
```python
# Manager_Pres_Uncertainty_pct (prepared speech)
X = df[['Manager_Pres_Uncertainty', 'Size', 'Leverage', ...]]
```

**6C: Uncertainty Change**
```python
# Change in uncertainty from t-1 to t
df['Uncertainty_Change'] = df.groupby('gvkey')['Uncertainty'].diff()
X = df[['Uncertainty_Change', 'Size', 'Leverage', ...]]
```

#### Specification 7: Alternative Timing

**7A: Same-year (Uncertainty_t -> Takeover_t)**
```python
# Tests concurrent relationship
model = sm.Logit(df['TakeoverTarget'], X)
```

**7B: Two-year horizon (Uncertainty_t -> Takeover_{t+2})**
```python
# Longer prediction window
df['TakeoverTarget_lag2'] = df.groupby('gvkey')['TakeoverTarget'].shift(-2)
model = sm.Logit(df['TakeoverTarget_lag2'], X)
```

#### Robustness Summary Table

| Spec | DV | IV | FE | Clustering | Timing | Purpose |
|------|-----|-----|----|------------|--------|---------|
| 1 (Primary) | Completed (binary) | Manager_QA | Year | Firm | t -> t+1 | Main test |
| 2 | Completed (binary) | Manager_QA | None | Firm | t -> t+1 | No FE sensitivity |
| 3 | Time-to-event | Manager_QA | None | - | Duration | Cox PH model |
| 4 | Completed (binary) | Manager_QA | Firm | Firm | t -> t+1 | Conditional logit |
| 5A | Announced (binary) | Manager_QA | Year | Firm | t -> t+1 | Deal initiation |
| 5B | Hostile (binary) | Manager_QA | Year | Firm | t -> t+1 | Hostile deals |
| 5C | Deal Value (cont) | Manager_QA | Year | Firm | t -> t+1 | Transaction economics |
| 6A | Completed (binary) | CEO_QA | Year | Firm | t -> t+1 | CEO-only IV |
| 6B | Completed (binary) | Manager_Pres | Year | Firm | t -> t+1 | Prepared speech |
| 6C | Completed (binary) | Uncertainty_Change | Year | Firm | t -> t+1 | Change in uncertainty |
| 7A | Completed (binary) | Manager_QA | Year | Firm | t -> t | Concurrent |
| 7B | Completed (binary) | Manager_QA | Year | Firm | t -> t+2 | Longer horizon |

**Total Robustness Specifications:** 12 specifications
**Primary Reporting:** Spec 1
**Full Reporting:** All 12 specs (pre-registered approach)

---

## Implementation Plan

### Sequential Execution Strategy

**Decision:** Implement H1 (Illiquidity) first, then apply learnings to H2 (Takeover).

**Rationale:**
1. **Dang et al. (2022) provides clear template** for H1 - direct methodological guidance
2. **Data availability is simpler** - CRSP data already integrated, no SDC access needed initially
3. **Stronger literature base** - Amihud (2002) is dominant standard vs more fragmented M&A literature
4. **Learnings transfer to H2** - Panel regression approach, data merging, variable construction all applicable
5. **Risk mitigation** - If issues arise, easier to debug on continuous DV (illiquidity) than binary DV (takeover)

### Phase 1: Hypothesis 1 (Illiquidity) Implementation

#### Plan 55-03: Construct H1 Variables

**Script:** `2_Scripts/3_Financial_V2/3.5_H7IlliquidityVariables.py`

**Steps:**
1. Load V2 sample manifest
2. Load CRSP daily stock data via CCM link
3. Calculate Amihud illiquidity ratio for each firm-year:
   - Daily dollar volume = |PRC| * VOL
   - Daily illiquidity = |RET| / dollar volume
   - Annual illiquidity = mean(daily illiquidity) * 1e6
4. Calculate Roll spread for each firm-year:
   - First-order autocovariance of returns
   - SPRD = 2 * sqrt(-autocovariance) if negative
5. Calculate bid-ask spread (if data available)
6. Merge Compustat financial data for controls
7. Merge V2 uncertainty measures
8. Apply sample exclusions:
   - Financial firms (SIC 6000-6999)
   - Utilities (SIC 4900-4999)
   - Positive assets requirement
   - Minimum 50 trading days
9. Winsorize continuous variables at 1%/99%
10. Create lagged dependent variable (t -> t+1)
11. Output: `4_Outputs/3_Financial_V2/H7_Illiquidity_Sample.parquet`

**Output Variables:**
```
gvkey, fyear
Illiquidity_Amihud           - Primary DV
Illiquidity_Roll             - Robustness DV 1
Illiquidity_BidAsk           - Robustness DV 2 (if available)
Manager_QA_Uncertainty_pct   - Primary IV
CEO_QA_Uncertainty_pct       - Alternative IV
Manager_Pres_Uncertainty_pct - Alternative IV
CEO_Pres_Uncertainty_pct     - Alternative IV
Size                         - Control: log(Market Cap)
Leverage                     - Control: Debt/Assets
ROA                          - Control: Return on Assets
MTB                          - Control: Market-to-Book
Volatility                   - Control: Stock return volatility
Returns                      - Control: Cumulative returns
CurrentRatio                 - Control: Current Assets/Current Liabilities
Volume                       - Control: Log trading volume
```

#### Plan 55-04: Run H1 Primary Regression

**Script:** `2_Scripts/4_Econometric_V2/4.7_H7IlliquidityRegression.py`

**Steps:**
1. Load H1 sample from 55-03 output
2. Verify data quality (missing values, outliers)
3. Generate descriptive statistics
4. Run primary regression (Spec 1):
   - PanelOLS with Firm + Year FE
   - Firm-clustered SE
   - DV: Amihud illiquidity at t+1
   - IV: Manager_QA_Uncertainty_pct at t
5. Extract coefficients, standard errors, p-values
6. Calculate FDR-corrected p-values (4 IVs)
7. Output: `4_Outputs/4_Econometric_V2/H7_Primary_Results.parquet`

**Output Tables:**
```
Table 1: Descriptive Statistics
Table 2: Correlation Matrix
Table 3: Primary Regression Results (Firm+Year FE)
Table 4: FDR-Corrected Results
```

#### Plan 55-05: Run H1 Robustness Suite

**Script:** `2_Scripts/4_Econometric_V2/4.7_H7IlliquidityRegression.py` (continued)

**Steps:**
1. Run all 10 robustness specifications (Specs 2-7)
2. Collect results for each specification
3. Generate comparison table across all specs
4. Assess consistency of uncertainty coefficient across specs
5. Output: `4_Outputs/4_Econometric_V2/H7_Robustness_Results.parquet`

**Robustness Output:**
```
Table 5: Robustness Comparison (All 11 Specs)
Figure 1: Coefficient Plot (Uncertainty beta across specs)
Figure 2: t-stat Plot (Statistical significance across specs)
```

### Phase 2: Hypothesis 2 (Takeover) Implementation

#### Plan 55-06: Construct H2 Variables

**Script:** `2_Scripts/3_Financial_V2/3.6_H8TakeoverVariables.py`

**Steps:**
1. Load H1 sample as base (already has uncertainty and controls)
2. Load SDC Platinum M&A data
3. Match SDC to sample via CUSIP -> GVKEY
4. Create takeover indicators:
   - TakeoverTarget_Completed: 1 if target in completed deal
   - TakeoverTarget_Announced: 1 if target in announced deal
   - TakeoverTarget_Hostile: 1 if target in hostile deal
5. Create lagged takeover indicators (t -> t+1)
6. Calculate additional controls:
   - Asset Turnover (SALE/AT)
   - R&D Intensity (XRD/AT, 0 if missing)
   - Abnormal returns (market-adjusted)
7. Merge with H1 sample
8. Apply M&A-specific exclusions
9. Output: `4_Outputs/3_Financial_V2/H8_Takeover_Sample.parquet`

**Output Variables (in addition to H1):**
```
TakeoverTarget_lag1          - Primary DV (completed deals)
TakeoverAnnounced_lag1       - Robustness DV (announced deals)
TakeoverHostile_lag1         - Robustness DV (hostile deals)
DealValue                    - Transaction value (for robustness)
Efficiency                   - Control: Asset Turnover
RD_Intensity                 - Control: R&D/Assets
AbnormalReturns              - Control: Market-adjusted returns
```

#### Plan 55-07: Run H2 Primary Regression

**Script:** `2_Scripts/4_Econometric_V2/4.8_H8TakeoverRegression.py`

**Steps:**
1. Load H2 sample from 55-06 output
2. Verify takeover rate (~1-2% expected)
3. Generate descriptive statistics (targets vs non-targets)
4. Run primary regression (Spec 1):
   - Logit with Year FE
   - Firm-clustered SE
   - DV: Binary takeover indicator at t+1
   - IV: Manager_QA_Uncertainty_pct at t
5. Extract coefficients, standard errors, p-values
6. Calculate odds ratios
7. Calculate FDR-corrected p-values
8. Output: `4_Outputs/4_Econometric_V2/H8_Primary_Results.parquet`

**Output Tables:**
```
Table 6: Takeover Descriptive Statistics
Table 7: Target vs Non-Target Comparison
Table 8: Primary Logit Results (Year FE, Firm-Clustered)
Table 9: Odds Ratios
```

#### Plan 55-08: Run H2 Robustness Suite

**Script:** `2_Scripts/4_Econometric_V2/4.8_H8TakeoverRegression.py` (continued)

**Steps:**
1. Run all 11 robustness specifications (Specs 2-7)
2. Run Cox proportional hazards model (Spec 3)
3. Run conditional logit (Spec 4)
4. Collect results for each specification
5. Generate comparison table across all specs
6. Assess consistency of uncertainty coefficient across specs
7. Output: `4_Outputs/4_Econometric_V2/H8_Robustness_Results.parquet`

**Robustness Output:**
```
Table 10: Robustness Comparison (All 12 Specs)
Figure 3: Odds Ratio Plot (Uncertainty OR across specs)
Figure 4: Hazard Ratio (Cox PH model)
```

#### Plan 55-09: Synthesis and Reporting

**Script:** `2_Scripts/4_Econometric_V2/4.9_H7H8_Synthesis.py`

**Steps:**
1. Load H1 and H2 results
2. Compare to V1 null results
3. Generate summary tables
4. Create final report
5. Output: `4_Outputs/4_Econometric_V2/H7H8_Final_Report.parquet`

**Final Report:**
```
- Executive Summary
- Methodology Summary
- H1 Results (Primary + Robustness)
- H2 Results (Primary + Robustness)
- Comparison to Literature (Dang 2022, etc.)
- Comparison to V1 Results
- Conclusions and Implications
```

### Implementation Checklist

**Phase 1 (H1):**
- [ ] Construct Amihud illiquidity variable
- [ ] Construct Roll spread variable
- [ ] Merge CRSP, Compustat, V2 text data
- [ ] Apply sample exclusions
- [ ] Generate descriptive statistics
- [ ] Run primary regression (Firm+Year FE)
- [ ] Run 10 robustness specifications
- [ ] Compare results across specifications
- [ ] Document H1 findings

**Phase 2 (H2):**
- [ ] Load and merge SDC data
- [ ] Create takeover indicators
- [ ] Create additional controls (Efficiency, R&D)
- [ ] Generate takeover descriptive statistics
- [ ] Run primary logit regression
- [ ] Run Cox PH model
- [ ] Run conditional logit
- [ ] Run 8 additional robustness specs
- [ ] Document H2 findings

**Phase 3 (Synthesis):**
- [ ] Compare H1/H2 to V1 results
- [ ] Compare to literature benchmarks
- [ ] Generate final report
- [ ] Update STATE.md
- [ ] Archive outputs

---

## Success Criteria

### For Each Hypothesis

#### Implementation Success

**Code Execution:**
- [ ] Scripts execute without errors
- [ ] All variables constructed per specification
- [ ] Regressions run with correct FE and clustering
- [ ] Output files generated successfully

**Data Quality:**
- [ ] Sample size meets targets (>15,000 obs for H1, >25,000 for H2)
- [ ] Descriptive statistics reasonable (no extreme outliers)
- [ ] Correlation matrix shows no perfect multicollinearity
- [ ] Missing data <5% for all variables

**Methodology Adherence:**
- [ ] All regression equations match specification
- [ ] All controls included as specified
- [ ] Fixed effects implemented correctly
- [ ] Clustering implemented correctly
- [ ] Timing (t -> t+1) implemented correctly

**Robustness Execution:**
- [ ] All robustness specifications executed
- [ ] Results comparable across specifications
- [ ] FDR correction applied to multiple IVs
- [ ] Diagnostic statistics generated

#### Scientific Success

**Primary Criterion (Any One):**
1. **Statistical Significance:**
   - Uncertainty coefficient significant at p < 0.05 (one-tailed, FDR-corrected)
   - Consistent direction across specifications
   - Economically meaningful magnitude

2. **Consistent Direction:**
   - Uncertainty coefficient has expected sign in >70% of specifications
   - Even if not significant, consistent direction suggests pattern
   - Narrow confidence intervals suggest precise estimates

3. **Precise Estimates:**
   - Confidence intervals exclude zero in some specifications
   - Effect size within literature benchmarks
   - Statistical power sufficient (>80%)

**All Outcomes Valued:**
- **Null Result:** No significant effect, but precisely estimated (narrow CI)
- **Mixed Result:** Significant in some specs, not others (interesting pattern)
- **Significant Result:** Clear support for hypothesis (ideal outcome)

**Interpretation Guidelines:**
- Null result with precise estimates = "No evidence of relationship" (valid finding)
- Null result with wide CIs = "Inconclusive" (power limitation)
- Mixed result = "Relationship depends on specification" (novel finding)
- Significant result = "Hypothesis supported" (publishable)

### For H1 (Illiquidity) Specifically

**Implementation Success:**
- Amihud illiquidity calculated correctly (verified against formula)
- Roll spread calculated for valid observations
- Minimum 50 trading days filter applied
- Industry exclusions (financial, utilities) applied
- Winsorization at 1%/99% applied
- Lagged DV construction correct (t -> t+1)

**Scientific Success Benchmarks:**
- **Dang et al. (2022) coefficient:** 0.0065 for Amihud
- **Expected direction:** beta > 0 (uncertainty increases illiquidity)
- **Economic magnitude:** 0.1-1.0 increase in illiquidity per SD uncertainty
- **Statistical significance:** t-stat > 1.645 (one-tailed 5%)

**Success Interpretation:**
- |beta| > 0.005, p < 0.05: **Strong support** (matches literature magnitude)
- |beta| > 0.001, p < 0.05: **Moderate support** (smaller effect)
- beta > 0, p > 0.05: **Weak support** (right direction, not significant)
- beta < 0: **No support** (wrong direction)

### For H2 (Takeover) Specifically

**Implementation Success:**
- SDC data merged correctly (takeover rate ~1-2%)
- Takeover indicator defined correctly (completed deals)
- Year fixed effects implemented in logit
- Firm clustering implemented
- Additional controls (Efficiency, R&D) calculated

**Scientific Success Benchmarks:**
- **Expected odds ratio:** OR > 1.10 (10% increase in takeover odds per SD uncertainty)
- **Statistical significance:** z-stat > 1.645 (one-tailed 5%)
- **Literature benchmarks:** Meghouar (2024) ORs 1.05-1.20 for significant predictors

**Success Interpretation:**
- OR > 1.20, p < 0.05: **Strong support** (economically meaningful)
- OR > 1.10, p < 0.05: **Moderate support** (small effect)
- OR > 1.00, p > 0.05: **Weak support** (right direction, not significant)
- OR < 1.00: **No support** (wrong direction - uncertainty reduces takeover risk)

### Overall Phase Success

**Minimum Requirements:**
1. Both hypotheses tested with full robustness suites
2. Implementation verified (code works, methodology correct)
3. Results documented with comparison to V1 and literature
4. No unresolved blockers or data issues

**Ideal Outcome:**
- At least one hypothesis shows significant effect
- Results consistent across robustness specs
- Effect sizes comparable to literature
- Clear contribution to knowledge (novel finding or confirmation)

**Acceptable Outcome (Null Results):**
- Precisely estimated null effects
- Robustness confirms null across specifications
- Conclusive that no relationship exists
- Publishable as "no evidence of relationship"

**Unacceptable Outcome:**
- Inconclusive due to data limitations
- Implementation errors preventing analysis
- Unable to complete robustness suite
- No clear conclusion possible

---

## Comparison to V1 Implementation

### V1 Suspected Flaws

Based on Phase 55-01 literature review and V2 null results, V1 may have had:

1. **Incorrect Illiquidity Calculation:**
   - V1 may have used wrong formula or aggregation
   - May not have scaled correctly (1e6 multiplier)
   - May not have required minimum trading days

2. **Wrong Fixed Effects:**
   - V1 may have omitted Firm FE (between-firm only)
   - V1 may have included Industry FE (redundant with Firm FE)
   - V1 may not have clustered SE correctly

3. **Incorrect Timing:**
   - V1 may have used contemporaneous timing (t -> t)
   - May not have created proper lag structure

4. **Missing Controls:**
   - V1 may have omitted important control variables
   - May not have winsorized outliers

5. **Takeover Definition Issues:**
   - V1 may have used incorrect takeover definition
   - May not have matched SDC correctly

### V2 Improvements

This methodology addresses all suspected V1 flaws:

| Suspected V1 Flaw | V2 Solution | Rationale |
|------------------|-------------|-----------|
| Wrong illiquidity formula | Amihud (2002) exact formula | Literature standard |
| No minimum trading days | Require 50+ days | Prevents noisy measures |
| Missing Firm FE | PanelOLS with entity_effects | Controls for firm heterogeneity |
| Redundant Industry FE | Omitted | Collinear with Firm FE |
| No clustering | Firm-clustered SE | Petersen (2009) standard |
| Wrong timing | t -> t+1 lag | Causal ordering |
| Missing controls | Full literature-based controls | Dang et al. (2022) template |
| Takeover definition | Completed deals via SDC | Standard M&A literature |

### Expected Differences from V1

If V1 had implementation flaws, V2 may find:
- **Different coefficients** (if V1 formula wrong)
- **Different significance** (if V1 SE wrong)
- **Different sample size** (if V1 exclusions wrong)
- **Any significant effect** (if V1 null due to error)

If V1 was correctly implemented:
- **Similar coefficients** (replication)
- **Same null results** (confirmation of no effect)
- **Confidence in null findings** (methodology verified)

---

## Final Notes

### Pre-Registration

This methodology specification serves as pre-registration:
- All hypotheses specified before implementation
- All regression equations defined
- All robustness tests enumerated
- Success criteria established

**No p-hacking:** Results will be reported regardless of outcome.
**No specification searching:** Primary specification is pre-specified.
**Full disclosure:** All robustness specs will be reported.

### Reproducibility

All code will be:
- Version controlled (git)
- CLI-accessible with --help and --dry-run
- Self-contained (all imports and dependencies)
- Documented with inline comments
- Output timestamps for provenance

### Reporting

Results will be reported in:
- SUMMARY.md files (internal documentation)
- STATE.md updates (project status)
- Research report (final deliverable)
- Comparison to V1 results
- Comparison to literature benchmarks

---

**Document Status:** COMPLETE
**Last Updated:** 2026-02-06
**Phase:** 55-02 (Methodology Specification)
**Total Lines:** 1,600+
**Ready for Implementation:** YES
