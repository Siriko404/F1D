# Financial V2: Hypothesis Variable Construction

> **Note:** This folder contains legacy V2 scripts kept for reference. The active versions have been migrated to `src/f1d/financial/v2/` as part of the v6.1 architecture standard. New development should use the `f1d.financial.*` namespace imports.

## Purpose and Scope

This folder contains variable construction scripts for the three main hypotheses (H1, H2, H3) in the F1D v2.0 hypothesis testing pipeline. These scripts extend the v1.0 financial controls pipeline (Step 3) by creating dependent variables, moderators, and additional controls specifically needed for empirical testing of the relationship between speech uncertainty and corporate financial decisions.

The scripts in this folder are **Step 3.1, 3.2, and 3.3** in the execution order, following Step 2 (Text Processing) and Step 3 (Financial Controls). They consume outputs from both prior steps - speech uncertainty measures from `4_Outputs/2_Text_Processing/` and standard firm controls from `4_Outputs/3_Financial/` - to construct the specialized variables required for panel regression analysis.

**Status:** LEGACY - Migrated to src/f1d/financial/v2/

---

## Hypothesis 1: Cash Holdings Variables

**Script:** `3.1_H1Variables.py`

### Research Question
Do managers with vague language patterns maintain higher cash holdings (precautionary motive), and does firm leverage moderate this effect (debt discipline hypothesis)?

### Expected Sign
- β₁ > 0: Vagueness increases cash holdings
- β₃ < 0: Leverage attenuates the uncertainty-cash relationship

### Variables

#### Dependent Variable

| Variable Name | Formula | Compustat Fields | Description |
|--------------|---------|------------------|-------------|
| CashHoldings | CHE / AT | CHE, AT | Cash and Cash Equivalents scaled by Total Assets |

#### Moderator Variable

| Variable Name | Formula | Compustat Fields | Description |
|--------------|---------|------------------|-------------|
| Leverage | (DLTT + DLC) / AT | DLTT, DLC, AT | Total Debt (Long-term + Current) scaled by Total Assets |

#### Interaction Term

| Variable Name | Construction | Notes |
|--------------|--------------|-------|
| Uncertainty×Leverage | Speech_Uncertainty × (Leverage - mean(Leverage)) | Mean-centered leverage to avoid multicollinearity |

#### Control Variables

| Variable Name | Formula | Compustat Fields | Description |
|--------------|---------|------------------|-------------|
| OCF_Volatility | StdDev(OANCF/AT) over trailing 5 years | OANCF, AT | Operating Cash Flow volatility |
| Current_Ratio | ACT / LCT | ACT, LCT | Current ratio (liquidity measure) |
| Tobins_Q | (AT + ME - CEQ) / AT | AT, ME, CEQ | Market-to-book proxy (Tobin's Q) |
| ROA | IB / AT | IB, AT | Return on Assets |
| Capex_AT | CAPX / AT | CAPX, AT | Capital expenditure intensity |
| Dividend_Payer | Dummy = 1 if DVC > 0 | DVC | Dividend payer dummy |
| Firm_Size | log(AT) | AT | Natural log of total assets |

### Regression Specification

```
CashHoldings_{i,t+1} = β₀ + β₁·Uncertainty_{i,t} + β₂·Leverage_{i,t} + β₃·(Uncertainty×Leverage)_{i,t} 
                        + γ·Controls_{i,t} + Firm_FE + Year_FE + Industry_FE + ε_{i,t}
```

Standard errors clustered at the firm level.

---

## Hypothesis 2: Investment Efficiency Variables

**Script:** `3.2_H2Variables.py`

### Research Question
Does speech vagueness correlate with investment inefficiency—specifically, do vague managers tend to overinvest in low-growth periods and underinvest despite high growth opportunities?

### Expected Sign
- β₁ < 0: Vagueness lowers investment efficiency
- β₃ > 0: Leverage improves efficiency (debt disciplines investment)

### Variables

#### Dependent Variable - Option 1: Efficiency Score

| Variable Name | Formula | Compustat Fields | Description |
|--------------|---------|------------------|-------------|
| Overinvest_Dummy | 1 if (CAPX/DP > 1.5) AND (SalesGrowth < Industry-Year Median) | CAPX, DP, SALE | Overinvestment indicator |
| Underinvest_Dummy | 1 if (CAPX/DP < 0.75) AND (Tobins_Q > 1.5) | CAPX, DP, Q | Underinvestment indicator |
| Efficiency_Score | 1 - (%Overinvest + %Underinvest) over 5-year window | — | Investment efficiency index [0,1] |

**Notes:**
- SalesGrowth = (SALE_t - SALE_{t-1}) / SALE_{t-1}
- Industry-year median calculated within Fama-French 48 industry × year cells
- 5-year window requires minimum 3 years of data

#### Dependent Variable - Option 2: ROA Residual (Biddle et al. 2009)

| Variable Name | Construction | Compustat Fields | Description |
|--------------|--------------|------------------|-------------|
| ROA_Residual | Residual from: ΔROA_{t+2} ~ Capex_t/AT + Controls | ROA, CAPX, AT | Investment efficiency residual |

**Regression for residual extraction:**
```
ΔROA_{i,t+2} = α + β₁·(CAPX/AT)_{i,t} + β₂·Tobins_Q_{i,t} + β₃·CashHoldings_{i,t} 
               + β₄·Leverage_{i,t} + Year_FE + Industry_FE + ε_{i,t}
```

Positive residuals indicate efficient investment (high future returns given current investment); negative residuals indicate inefficiency.

#### Control Variables

| Variable Name | Formula | Compustat Fields | Description |
|--------------|---------|------------------|-------------|
| Tobins_Q | (AT + ME - CEQ) / AT | AT, ME, CEQ | Investment opportunities proxy |
| CF_Volatility | StdDev(CFO/AT) over trailing 5 years | CFO, AT | Cash flow volatility |
| Industry_CapEx_Intensity | Mean(CAPX/AT) by FF48 industry-year | CAPX, AT | Industry investment norms |
| Analyst_Dispersion | StdDev(forecasts) / |mean(forecasts)| | — | Earnings forecast dispersion |
| Firm_Size | log(AT) | AT | Natural log of total assets |
| ROA | IB / AT | IB, AT | Return on Assets |
| FCF | (OANCF - CAPX) / AT | OANCF, CAPX, AT | Free cash flow |
| Earnings_Volatility | StdDev(EPS) over trailing 5 years | EPS | Earnings uncertainty |

### Regression Specification

```
Efficiency_{i,t+1} = β₀ + β₁·Uncertainty_{i,t} + β₂·Leverage_{i,t} + β₃·(Uncertainty×Leverage)_{i,t}
                     + γ·Controls_{i,t} + Firm_FE + Year_FE + Industry_FE + ε_{i,t}
```

Standard errors clustered at the firm level. Run separately for Efficiency_Score and ROA_Residual.

---

## Hypothesis 3: Payout Policy Variables

**Script:** `3.3_H3Variables.py`

### Research Question
Do managers who use vague language maintain less stable dividend policies? Does leverage promote payout smoothing?

### Expected Sign
- For Stability (DV 1): β₁ < 0, β₃ < 0 (vagueness reduces stability, leverage doesn't help)
- For Flexibility (DV 2): β₁ > 0, β₃ > 0 (vagueness increases flexibility, leverage also increases flexibility)

### Variables

#### Dependent Variable 1: Dividend Policy Stability

| Variable Name | Formula | Compustat Fields | Description |
|--------------|---------|------------------|-------------|
| Dividend_Stability | -StdDev(ΔDPS / mean(DPS)) over trailing 5 years | DVC, csho | Negative of coefficient of variation in DPS changes |

**Calculation:**
1. Compute annual ΔDPS_t = (DPS_t - DPS_{t-1}) / DPS_{t-1} for each year
2. Take mean of |ΔDPS| over the 5-year window
3. Stability = -1 × StdDev(ΔDPS) / mean(|ΔDPS|)

Higher values (less negative) indicate more stable dividend policies.

#### Dependent Variable 2: Payout Flexibility

| Variable Name | Formula | Compustat Fields | Description |
|--------------|---------|------------------|-------------|
| Payout_Flexibility | % years where |ΔDPS| > 5% over 5-year window | DVC, csho | Proportion of years with material dividend changes |

**Calculation:**
1. For each year in 5-year window, check if |(DPS_t - DPS_{t-1}) / DPS_{t-1}| > 0.05
2. Flexibility = count(years with |ΔDPS| > 5%) / total_years

Higher values indicate more flexible (volatile) dividend policies.

#### Control Variables

| Variable Name | Formula | Compustat Fields | Description |
|--------------|---------|------------------|-------------|
| Earnings_Volatility | StdDev(EPS) over trailing 5 years | EPS | Earnings uncertainty |
| FCF_Growth | (FCF_t - FCF_{t-1}) / |FCF_{t-1}| | OANCF, CAPX, AT | Free cash flow growth rate |
| Firm_Maturity | log(1 + FirmAge) | — | Log of firm age since first appearance |
| Firm_Size | log(AT) | AT | Natural log of total assets |
| ROA | IB / AT | IB, AT | Return on Assets |
| Tobins_Q | (AT + ME - CEQ) / AT | AT, ME, CEQ | Investment opportunities |
| Cash_Holdings | CHE / AT | CHE, AT | Cash holdings (from H1) |

### Regression Specifications

**Model 1: Dividend Stability**
```
Stability_{i,t+1} = β₀ + β₁·Uncertainty_{i,t} + β₂·Leverage_{i,t} + β₃·(Uncertainty×Leverage)_{i,t}
                    + γ·Controls_{i,t} + Firm_FE + Year_FE + Industry_FE + ε_{i,t}
```

**Model 2: Payout Flexibility**
```
Flexibility_{i,t+1} = β₀ + β₁·Uncertainty_{i,t} + β₂·Leverage_{i,t} + β₃·(Uncertainty×Leverage)_{i,t}
                      + γ·Controls_{i,t} + Firm_FE + Year_FE + Industry_FE + ε_{i,t}
```

Standard errors clustered at the firm level. Both DVs tested independently.

---

## Input/Output Mapping

### Inputs

| Source | Location | Content |
|--------|----------|---------|
| Text Processing Outputs | `4_Outputs/2_Text_Processing/latest/` | Speech uncertainty measures (fuzzy ratios, modal counts, etc.) |
| Financial Controls | `4_Outputs/3_Financial/latest/` | Compustat-based firm controls (Tobin's Q, ROA, Size, etc.) |
| Sample Manifest | `4_Outputs/1_Cleaned_Metadata/latest/` | Master sample with firm identifiers and fiscal year mapping |

### Outputs

All scripts output to timestamped directories:

```
4_Outputs/3_Financial_V2/YYYY-MM-DD_HHMMSS/
├── H1_CashHoldings.parquet       # H1 variables (CashHoldings, Leverage, interactions)
├── H2_InvestmentEfficiency.parquet # H2 variables (Efficiency scores, residuals)
├── H3_PayoutPolicy.parquet       # H3 variables (Stability, Flexibility)
├── stats.json                    # Variable distributions and diagnostics
└── schema.yaml                   # Column definitions and data types
```

### Logs

Execution logs written to:
```
3_Logs/3_Financial_V2/YYYY-MM-DD_HHMMSS_H1.log
3_Logs/3_Financial_V2/YYYY-MM-DD_HHMMSS_H2.log
3_Logs/3_Financial_V2/YYYY-MM-DD_HHMMSS_H3.log
```

---

## Script Numbering Convention

Following the `{step}.{substep}_{PascalCase}.py` pattern per `CONVENTIONS.md`:

| Script | Step | Purpose |
|--------|------|---------|
| `3.1_H1Variables.py` | 3.1 | Cash Holdings variable construction (H1) |
| `3.2_H2Variables.py` | 3.2 | Investment Efficiency variable construction (H2) |
| `3.3_H3Variables.py` | 3.3 | Payout Policy variable construction (H3) |

### Execution Order

**Prerequisites:**
- Step 2 (Text Processing) must be complete → provides speech uncertainty measures
- Step 3 (Financial Controls) must be complete → provides standard Compustat controls

**Parallelization:**
- H1, H2, and H3 scripts have **no dependencies** between them
- Can run in parallel after prerequisites met

**Downstream:**
- Outputs feed into Step 4 Econometric_V2 regression scripts
- Each hypothesis script produces separate .parquet file
- Econometric scripts merge as needed for specific regressions

---

## Data Requirements and Constraints

### Minimum Data Requirements

All scripts require:
- Compustat Annual (funda) with fiscal year alignment
- Minimum 3 years of history for rolling standard deviations
- Fama-French 48 industry classifications
- Speech uncertainty measures matched by (gvkey, fiscal_year)

### Sample Restrictions

- Exclude financial firms (SIC 6000-6999)
- Exclude regulated utilities (SIC 4900-4999)
- Require positive total assets (AT > 0)
- Winsorize continuous variables at 1st and 99th percentiles

### Variable Centering

**Critical:** All continuous variables entering interaction terms must be mean-centered to avoid multicollinearity:

```python
# Example: Center leverage before creating interaction
df['Leverage_centered'] = df['Leverage'] - df['Leverage'].mean()
df['Uncertainty_x_Leverage'] = df['Uncertainty'] * df['Leverage_centered']
```

---

## References (Implementation Notes)

While academic citations belong in the individual scripts, the following methodological sources inform these constructions:

- **Cash holdings:** Opler, Pinkowitz, Stulz, and Williamson (1999) - determinants of cash holdings
- **Investment efficiency:** Biddle, Hilary, and Verdi (2009) - accounting quality and investment efficiency
- **Payout policy:** Leary and Michaely (2011) - determinants of dividend smoothing
- **Fixed effects:** Petersen (2009) - standard error clustering in panel data
- **Interaction terms:** Dalal and Zickar (2012) - mean-centering to reduce multicollinearity

---

## Contact and Replication

For replication questions, refer to:
- `README.md` (root): Project overview and execution guide
- `CLAUDE.md`: Coding conventions and project standards
- Individual script headers: Specific implementation details

---

*Last updated: 2026-02-14*
*Phase: 78-documentation-synchronization*
*Version: v2.0 Hypothesis Testing Suite*
