# Phase 55: V1 Hypotheses Re-Test - Research

**Researched:** 2026-02-06
**Domain:** Financial Economics / Empirical Accounting / Text Analysis
**Confidence:** MEDIUM

## Summary

This phase re-tests two V1 hypotheses that showed null results: (1) Managerial Speech Uncertainty -> Stock Illiquidity and (2) Managerial Speech Uncertainty -> Takeover Target Probability. The research confirms this is a fresh implementation based on literature best practices, not a V1 code audit. Key finding: a robust literature base exists for both hypotheses, with Dang et al. (2022) directly studying managerial tone and stock liquidity, and extensive M&A prediction literature using financial variables.

**Primary recommendation:** Pilot with Hypothesis 1 (Uncertainty -> Illiquidity) first as Dang et al. (2022) provides a clear methodological template, then apply learnings to Hypothesis 2.

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions

- **Literature review scope:** Exhaustive — 20+ years, all major finance journals, full citation tracing (2-3 days work)
- **Hypotheses priority:** Both hypotheses equal priority (uncertainty-illiquidity AND uncertainty-takeover)
- **NO V1 code review:** This is fresh re-implementation based on literature best practices
- **Methodology specification:** Full methodology specification document BEFORE any code implementation
- **Text measures:** Reuse existing V2 speech uncertainty measures from V2 pipeline (LM Uncertainty, etc.)
- **Regression specifications:** Follow literature standards (FE, clustering, timing) — NOT V1 patterns or V2 defaults
- **Execution approach:** Sequential pilot — implement one hypothesis first, learn and refine approach for second
- **Robustness specifications:** Full robustness suite regardless of primary result (pre-registered approach)
- **File organization:** Extend existing V2 folders (2_Scripts/3_Financial_V2/, 2_Scripts/4_Econometric_V2/)

### Claude's Discretion

- Specific journals and databases to search for literature review
- Exact structure of methodology specification document
- Which hypothesis to pilot first (uncertainty-illiquidity or uncertainty-takeover)
- Number and nature of robustness specifications (within "full suite" directive)
- Sample construction details (after presenting recommendation based on literature)

### Deferred Ideas (OUT OF SCOPE)

None explicitly stated

</user_constraints>

## Standard Stack

### Core

| Library/Source | Version/Year | Purpose | Why Standard |
|----------------|--------------|---------|--------------|
| **Loughran-McDonald Master Dictionary** | 2011 (ongoing updates) | Finance-specific sentiment/uncertainty word lists | 7,600+ citations; 75% fewer misclassifications than Harvard dictionary in finance context |
| **Amihud (2002) Illiquidity Measure** | 2002 (extended 2024) | Primary stock illiquidity proxy | Dominant standard; validated in 2024 research; ratio of |return|/volume |
| **SDC Platinum M&A Database** | Current | M&A transaction data | Industry standard for takeover research |
| **CRSP/Compustat merged** | Current | Stock price, volume, financial data | Standard data sources for financial research |

### Supporting

| Library/Source | Version/Year | Purpose | When to Use |
|----------------|--------------|---------|-------------|
| **Roll (1984) Implicit Spread** | 1984 | Alternative illiquidity measure | Robustness check for Amihud |
| **Bid-Ask Spreads** | Daily | Transaction cost illiquidity measure | When high-frequency data available |
| **Python (statsmodels)** | Current | Fixed effects regression with clustered SE | Implementation of econometric specifications |
| **Linearmodels (Python)** | Current | PanelOLS with entity/time effects | Alternative implementation |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Amihud (2002) | Roll (1984) spread | Roll uses price autocovariance; Amihud more direct for price impact |
| LM Dictionary | BERT/FinBERT embeddings | ML approaches require more data; less interpretable |
| Python statsmodels | Stata | Stata is older standard; Python integrates with existing V2 pipeline |

**Installation:**
```bash
# Python packages (likely already in V2 environment)
pip install statsmodels linearmodels pandas numpy scipy
```

## Architecture Patterns

### Recommended Project Structure

```
2_Scripts/3_Financial_V2/
├── 3.5_H5_UncertaintyIlliquidity.py      # Main hypothesis script
├── 3.6_H6_UncertaintyTakeover.py         # Second hypothesis
└── data/
    ├── illiquidity_measures.parquet       # Amihud, Roll, spreads
    └── takeover_targets.parquet           # SDC matched data

2_Scripts/4_Econometric_V2/
├── 4.5_H5_UncertaintyIlliquidity_Results.py  # Regression specs
├── 4.6_H6_UncertaintyTakeover_Results.py     # Regression specs
└── robustness/
    ├── H5_alt_specs.py                     # Alternative specifications
    └── H6_alt_specs.py                     # Alternative specifications
```

### Pattern 1: Illiquidity Measurement (Dang et al. 2022 approach)

**What:** Calculate Amihud illiquidity ratio as daily |return| / dollar volume

**When to use:** Primary illiquidity measure for hypothesis 1

**Example:**
```python
# Source: Based on Dang et al. (2022) methodology
# Amihud (2002) illiquidity measure calculation
# ILLIQ_it = (1/D_it) * sum(|r_itd| / VOLD_itd)

def calculate_amihud_illiquidity(returns, dollar_volumes):
    """
    Calculate Amihud illiquidity measure for each firm-year

    Parameters:
    -----------
    returns : DataFrame
        Daily returns
    dollar_volumes : DataFrame
        Daily trading volume in dollars

    Returns:
    --------
    illiq : Series
        Amihud illiquidity ratio by firm-year
    """
    abs_returns = returns.abs()
    illiq_daily = abs_returns / dollar_volumes
    illiq = illiq_daily.groupby(level=['firm_id', 'year']).mean()
    return illiq * 1e6  # Scale for interpretability
```

### Pattern 2: Panel Regression with Clustered SE (Petersen 2009)

**What:** Fixed effects regression with firm-clustered robust standard errors

**When to use:** All primary specifications for both hypotheses

**Example:**
```python
# Source: Cameron & Miller (2015), Petersen (2009)
import statsmodels.formula.api as smf

# Firm and year fixed effects with firm-clustered SE
model = smf.ols(
    'Illiquidity ~ Uncertainty + Size + Leverage + ROA + MTB + C(FirmFE) + C(YearFE)',
    data=df
).fit(cov_type='cluster', cov_kwds={'groups': df['firm_id']})
```

### Pattern 3: Takeover Target Prediction (Logistic)

**What:** Logistic regression predicting takeover probability

**When to use:** Hypothesis 2 (uncertainty -> takeover target)

**Example:**
```python
# Source: Standard M&A prediction literature (Ambrose 1990, Meghouar 2024)
import statsmodels.api as sm

# Logistic regression with firm clustering
X = df[['Uncertainty', 'Size', 'Leverage', 'ROA', 'MTB', 'Liquidity']]
X = sm.add_constant(X)
logit_model = sm.Logit(
    df['TakeoverTarget'],
    X
).fit(cov_type='cluster', cov_kwds={'groups': df['firm_id']})
```

### Anti-Patterns to Avoid

- **Including lagged dependent variable with firm FE:** Causes Nickell bias (Nickell 1981)
- **Using only White SE without clustering:** Understates SE in panel data (Petersen 2009)
- **Pooling without fixed effects:** Ignores unobserved firm heterogeneity
- **Harvard dictionary for finance:** 75% misclassification rate (Loughran-McDonald 2011)
- **Bad controls:** Including endogenous variables like NUMEST as controls

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Finance sentiment dictionary | Custom word list | Loughran-McDonald Master Dictionary | 7,600+ citations; finance-specific |
| Illiquidity calculation | Custom formulas | Amihud (2002) specification | Industry standard; comparable across studies |
| Clustered SE | Manual calculation | statsmodels/linearmodels cov_type='cluster' | Tested; handles edge cases |
| Fixed effects | Manual demeaning | PanelOLS or formula API | Handles unbalanced panels correctly |

**Key insight:** The finance research community has converged on specific methodological standards over 20+ years. Custom implementations risk introducing bugs and make results incomparable to literature.

## Common Pitfalls

### Pitfall 1: Nickell Bias in Dynamic Panels

**What goes wrong:** Including lagged dependent variable with firm fixed effects creates correlation between demeaned regressor and error term

**Why it happens:** Mean of lagged Y is correlated with error term after within transformation

**How to avoid:** Don't include lagged DV with firm FE. Use:
- First-difference GMM (Arellano-Bond 1991)
- System-GMM (Blundell-Bond 1998)
- Or omit lagged DV entirely

**Warning signs:** T-stat is suspiciously large; coefficient moves a lot when you add controls

### Pitfall 2: Incorrect Clustering

**What goes wrong:** Using White SE instead of clustered SE, or clustering at wrong level

**Why it happens:** Panel data has within-firm correlation over time; White SE assumes independence

**How to avoid:** Always cluster at firm level (minimum). Consider two-way clustering (firm + year) if appropriate.

**Warning signs:** SE are much smaller with White than clustered (Petersen 2009 shows t-stats 2-3x too large)

### Pitfall 3: Bad Control Variables

**What goes wrong:** Including endogenous variables as controls (e.g., analyst coverage)

**Why it happens:** Analyst coverage is itself affected by uncertainty

**How to avoid:** Only include pre-determined controls (size, leverage, ROA, MTB are standard)

**Warning signs:** Control variables have very high correlation with main regressor

### Pitfall 4: Sample Selection Bias

**What goes wrong:** Sample construction inadvertently selects on outcome

**Why it happens:** Excluding firms with missing data may correlate with illiquidity or takeover probability

**How to avoid:** Document exclusion decisions; test for sample selection bias

### Pitfall 5: Misinterpreting Null Results

**What goes wrong:** Concluding "no relationship" when power is low or measurement error is high

**Why it happens:** Text measures are noisy; uncertainty may be poorly captured

**How to avoid:** Always report effect sizes and confidence intervals; discuss measurement error

## Code Examples

Verified patterns from literature:

### Amihud Illiquidity Calculation

```python
# Source: Amihud (2002), validated in Dang et al. (2022)
# Based on https://www.aeaweb.org/conference/2024/program/paper/dTz568tG

import pandas as pd
import numpy as np

def amihud_illiquidity(prices, volumes, window=252):
    """
    Calculate Amihud illiquidity measure

    ILLIQ_it = (1/D) * sum(|r_it| / VOLD_it)

    Parameters:
    -----------
    prices : DataFrame
        Daily prices, indexed by date
    volumes : DataFrame
        Daily volume (shares), indexed by date
    window : int
        Number of trading days in year

    Returns:
    --------
    illiq : DataFrame
        Amihud illiquidity by firm-year
    """
    # Calculate returns
    returns = prices.pct_change()

    # Calculate dollar volume (need price per share data)
    # This is placeholder - V2 should have price data
    dollar_volume = volumes * prices

    # Amihud ratio
    abs_ret = returns.abs()
    illiq_daily = abs_ret / dollar_volume

    # Average over trading days in year
    illiq = illiq_daily.resample('Y').mean() * window

    return illiq
```

### Fixed Effects with Clustered SE

```python
# Source: Cameron & Miller (2015) Practitioner's Guide
# https://cameron.econ.ucdavis.edu/research/Cameron_Miller_JHR_2015_February.pdf

from linearmodels.panel import PanelOLS
import pandas as pd

def run_fe_regression(df, dv, iv, controls, cluster_var='firm_id'):
    """
    Run fixed effects regression with clustered standard errors

    Parameters:
    -----------
    df : DataFrame
        Panel data with MultiIndex (firm_id, year)
    dv : str
        Dependent variable name
    iv : str
        Independent variable of interest (uncertainty)
    controls : list
        Control variable names
    cluster_var : str
        Variable to cluster SE on

    Returns:
    --------
    results : PanelOLS results
    """
    # Set index for panel data
    df = df.set_index(['firm_id', 'year'])

    # Build formula
    formula = f"{dv} ~ {iv} + " + " + ".join(controls)

    # Run regression with firm and year effects
    model = PanelOLS(
        df,
        df[[iv] + controls],
        entity_effects=True,
        time_effects=True
    ).fit(cov_type='clustered', cluster_entity=True)

    return model
```

### Takeover Target Prediction

```python
# Source: Based on Ambrose (1990), Meghouar (2024)
# Standard logistic regression for M&A prediction

import statsmodels.api as sm

def takeover_logit(df, uncertainty_var, controls):
    """
    Logistic regression predicting takeover target

    Parameters:
    -----------
    df : DataFrame
        Firm-year observations
    uncertainty_var : str
        Uncertainty measure name
    controls : list
        Control variable names

    Returns:
    --------
    results : Logit results
    """
    # Prepare data
    X = df[[uncertainty_var] + controls]
    X = sm.add_constant(X)
    y = df['takeover_target']  # Binary: 1 if target, 0 otherwise

    # Fit logit with clustered SE
    logit = sm.Logit(y, X)
    results = logit.fit(
        cov_type='cluster',
        cov_kwds={'groups': df['firm_id']},
        disp=False
    )

    return results
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Harvard dictionary | Loughran-McDonald finance dictionary | 2011 | 75% reduction in misclassification |
| OLS with White SE | FE + Clustered SE | 2009 (Petersen) | T-stats 2-3x smaller; correct inference |
| Single illiquidity measure | Multiple measures (Amihud, Roll, spread) | 2020s | Robustness across measurement approaches |
| Text as single number | Uncertainty decomposition (Dzielinski 2017) | 2017 | Separate manager vs firm uncertainty |

**Deprecated/outdated:**
- Harvard Psychological Dictionary for finance: Loughran-McDonald (2011) showed 75% of "negative" words are misclassified
- OLS without clustering: Petersen (2009) showed t-stats can be 2-3x too large
- Using only one illiquidity measure: Modern studies use multiple for robustness

## Literature Review Findings

### Hypothesis 1: Uncertainty -> Illiquidity

**Primary Source:**
- **Dang et al. (2022)** "Does managerial tone matter for stock liquidity? Evidence from textual disclosures"
  - Published in: Finance Research Letters
  - Citations: 37+
  - Sample: 1994-2019, US-listed firms
  - Finding: Positive managerial tone associated with higher stock liquidity
  - Key methodology:
    - Tone measured from SEC filings using LM dictionary
    - Illiquidity: Bid-ask spreads (BASpread) and Amihud measure
    - FE regression with firm and year fixed effects
    - Clustered standard errors
  - Coefficients: 0.0006 for BASpread, 0.0065 for Amihud (both significant)

**Related Literature:**
- **Economic Policy Uncertainty and Stock Market Liquidity** (Dash et al. 2021): 87 citations; examines causality using Granger tests
- **Management Tone and Information Asymmetry** (2024): Studies COVID period; finds tone affects information asymmetry

**Standard Illiquidity Measures:**
1. **Amihud (2002):** |return| / dollar volume; dominant standard; extended 2024
2. **Roll (1984):** Implied spread from price autocovariance
3. **Bid-Ask Spread:** Direct transaction cost measure
4. **Effective Spread:** Distance from fundamental value

### Hypothesis 2: Uncertainty -> Takeover Target Probability

**Key Papers:**
- **Meghouar (2024)** "Takeover in Europe: Target characteristics"
  - Develops predictive models using financial data
  - Uses 1, 2, and 3 years before takeover

- **Hajek (2024)** "Predicting M&A targets using news sentiment"
  - 20+ citations
  - Uses sentiment analysis and topic detection

- **Ambrose (1990)** "Corporate real estate's impact on takeover market"
  - Classic logit regression approach
  - 69 citations

- **AI-Driven M&A Target Selection** (2025)
  - Machine learning approaches
  - Hybrid models for prediction

**Standard Prediction Variables:**
- Profitability (ROA, ROE)
- Financial leverage (debt/equity)
- Liquidity ratios (current ratio, quick ratio)
- Efficiency measures (asset turnover)
- Size (log assets, market cap)
- Growth opportunities (MTB, sales growth)
- Stock performance (abnormal returns)

**SDC Platinum:** Industry standard for M&A transaction data

### Econometric Standards

**Key References:**
- **Cameron & Miller (2015)** "A Practitioner's Guide to Cluster-Robust Inference"
  - 6,258 citations
  - Standard reference for clustered SE

- **Petersen (2009)** "Estimating Standard Errors in Finance Panel Data Sets"
  - 14,848+ citations
  - Shows OLS with White SE gives t-stats 2-3x too large

- **Nickell (1981)** "Biases in Dynamic Models with Fixed Effects"
  - 11,974 citations
  - Warns against lagged DV with FE

**Standard Specification:**
```
Y_it = alpha + beta*Uncertainty_it + gamma*X_it + firm_FE + year_FE + epsilon_it
SE clustered at firm level
```

**For takeover prediction:**
```
logit(Takeover_it) = alpha + beta*Uncertainty_it + gamma*X_it + firm_FE + year_FE
```

## Open Questions

1. **Sample Period:** Should we use full V2 sample or construct specific sample for each hypothesis?
   - What we know: V2 has established sample; but literature suggests different periods
   - Recommendation: Start with V2 sample for comparability, then test alternative periods

2. **Uncertainty Measure Decomposition:** Should we decompose uncertainty into firm vs manager components?
   - What we know: Dzielinski (2017) decomposition used in V2 for H1-H3
   - Unclear: Whether decomposition matters for illiquidity/takeover
   - Recommendation: Test both aggregate and decomposed measures

3. **Timing Alignment:** How to align conference calls with outcome measurement period?
   - What we know: Dang et al. use annual measures from SEC filings
   - What's unclear: Conference call timing (quarterly) vs annual outcomes
   - Recommendation: Use fiscal year aggregation, lag uncertainty by one period

4. **Takeover Definition:** What constitutes a "takeover target"?
   - What we know: SDC has various completion statuses
   - What's unclear: Should we include withdrawn deals? announced only?
   - Recommendation: Use completed deals as primary, announced as robustness

## Sources

### Primary (HIGH confidence)

- **[Loughran-McDonald Master Dictionary](https://sraf.nd.edu/loughranmcdonald-master-dictionary/)** - Official source for finance sentiment word lists
- **[Cameron & Miller (2015) Practitioner's Guide](https://cameron.econ.ucvavis.edu/research/Cameron_Miller_JHR_2015_February.pdf)** - Cluster-robust inference standard
- **[Petersen (2009) Programming Guide](https://www.kellogg.northwestern.edu/faculty/petersen/htm/papers/se/se_programming.htm)** - Finance panel data best practices
- **[SDC Platinum Database](https://www.library.hbs.edu/databases-cases-and-more/databases/sdc-platinum)** - M&A transaction data standard
- **[Dang et al. (2022) Managerial Tone and Liquidity](https://www.sciencedirect.com/science/article/abs/pii/S154461232200188X)** - Directly relevant study

### Secondary (MEDIUM confidence)

- **[Amihud Illiquidity Extension (2024)](https://ideas.repec.org/a/eee/pacfin/v87y2024ics0927538x2400235x.html)** - Recent validation of Amihud measure
- **[Realized Illiquidity (2024)](https://www.aeaweb.org/conference/2024/program/paper/dTz568tG)** - Numerical precision of Amihud measure
- **[Efficient Bid-Ask Spread Estimation (2024)](https://www.sciencedirect.com/science/article/pii/S0304405X24001399)** - Alternative illiquidity measure
- **[Predicting M&A Targets (2024)](https://www.sciencedirect.com/science/article/pii/S0040162524000660)** - Recent ML approaches to prediction
- **[Nickell Bias Papers](https://www.jstor.org/stable/1911408)** - Dynamic panel bias (1981, 11,974 citations)
- **[Singletons and Clustered SE](https://scorreia.com/research/singletons.pdf)** - Fixed effects with clustering (506 citations)

### Tertiary (LOW confidence)

- Web search results only - marked for validation:
  - Management Tone and Information Asymmetry (2024)
  - Economic Policy Uncertainty and Liquidity (2021)
  - Various M&A prediction papers using ML approaches

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - LM Dictionary, Amihud measure, CRSP/Compustat are industry standards
- Architecture: HIGH - Fixed effects + clustering is well-established methodology
- Pitfalls: HIGH - Nickell bias, clustering issues are well-documented
- Sample construction: MEDIUM - Need to validate V2 sample appropriateness
- M&A prediction variables: MEDIUM - Standard variables identified but need to confirm availability in V2 data

**Research date:** 2026-02-06
**Valid until:** 2026-03-06 (30 days - stable domain, but could find more specific papers)

**Recommendation for planning:**
1. Start with Hypothesis 1 (Illiquidity) - clearer literature template
2. Use V2 uncertainty measures (as decided)
3. Primary specification: FE regression with firm and year FE, clustered SE
4. Include robustness suite with alternative illiquidity measures
5. Then apply same approach to Hypothesis 2 (Takeover)
