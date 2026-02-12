# H8: PRisk × CEO Communication Style → Abnormal Investment

---

## Model Specification

### Regression Equation

$$
\text{AbsAbInv}_{i,t+1} = \beta_0 + \beta_1 \cdot \text{PRiskFY}_{i,t} + \beta_2 \cdot \text{StyleFrozen}_{i,t} + \beta_3 \cdot (\text{PRiskFY}_{i,t} \times \text{StyleFrozen}_{i,t}) + \boldsymbol{\gamma} \cdot \text{Controls}_{i,t} + \alpha_i + \delta_t + \varepsilon_{i,t+1}
$$

**Hypothesis H8:** $\beta_3 \neq 0$ (CEO style moderates PRisk → abnormal investment relationship)

**Estimation:** PanelOLS with Firm + Year FE, firm-clustered SE, Sample: 2003-2017

**Variable Construction:**
- **AbsAbInv:** Absolute value of Biddle (2009) abnormal investment residual
- **PRiskFY:** Hassan fiscal-year policy risk (mean of 2-5 quarters in 366-day window)
- **StyleFrozen:** CEO communication clarity score (frozen constraint: only data up to fiscal year-end)

---

## Regression Results

### Table 1: H8 PRisk × CEO Style → Abnormal Investment

| Variable | (1) |
|----------|---------|
| | **PRisk × CEO Style** |
| | |
| **Key Variables** | |
| PRiskFY (β₁) | 0.0000 |
| | (0.0001) |
| StyleFrozen (β₂) | -0.2245** |
| | (0.1063) |
| PRiskFY × StyleFrozen (β₃) | -0.0000 |
| | (0.0000) |
| | |
| **Control Variables** | |
| Firm size (ln_at) | 0.0005 |
| | (0.0014) |
| Leverage | 0.0002 |
| | (0.0030) |
| Cash | -0.0048 |
| | (0.0108) |
| ROA | -0.0102 |
| | (0.0140) |
| Market-to-book | 0.0000 |
| | (0.0003) |
| Sales growth | 0.0000 |
| | (0.0000) |
| | |
| **Fixed Effects** | Firm+Year |
| **Observations** | 5,295 |
| **R² (overall)** | 0.0056 |
| **R² (within)** | 0.0089 |

### Table 2: Sample Construction

| Dataset | Firm-Year Obs. | Unique Firms |
|---|---|---|
| StyleFrozen (CEO clarity) | 7,125 | 493 |
| PRiskFY (policy risk) | 65,664 | 7,869 |
| AbsAbInv (abnormal investment) | 80,048 | 11,256 |
| **Final merged sample** | **5,295** | **432** |

**Notes:**
- *** p < 0.01, ** p < 0.05, * p < 0.10
- Dependent variable: AbsAbInv (t+1) - absolute value of Biddle (2009) abnormal investment residual
- Standard errors clustered at firm level in parentheses
- H8 tests β₃ ≠ 0: interaction term essentially zero (p = 0.7574)
- β₂ (StyleFrozen/CEO vagueness) has a significant negative direct effect on abnormal investment
- Full coefficient results available in: `4_Outputs/5.8_H9_FinalMerge/2026-02-10_160505/h9_regression_results.csv`

**Outcome:** H8 NOT SUPPORTED (interaction β₃ = -0.0000, p = 0.7574)

---

## Control Variables

| Variable | Description | Source |
|----------|-------------|---------|
| ln_at_t | Log(total assets) - Firm size | Compustat |
| lev_t | Debt-to-assets ratio - Leverage | Compustat |
| cash_t | Cash-to-assets ratio - Financial slack | Compustat |
| roa_t | Return on assets - Profitability | Compustat |
| mb_t | Book-to-market ratio - Investment opportunities | Compustat |
| SalesGrowth_t | Sales growth - Growth prospects | Compustat |

**Variable Construction Notes:**
- **AbsAbInv (DV)**: Absolute value of Biddle (2009) abnormal investment residual
- **PRiskFY**: Hassan (2019) policy risk index, averaged over fiscal year (366-day window)
- **StyleFrozen**: CEO communication clarity score, constructed using frozen constraint (no look-ahead bias)
- **Frozen Constraint**: Only calls with start_date ≤ fiscal_year-end are included for each firm-year

**All control variables are winsorized at 1%/99% and lagged appropriately for causal identification.**
