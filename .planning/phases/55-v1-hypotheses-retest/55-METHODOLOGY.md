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
