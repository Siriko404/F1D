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

## Results

### Complete Results Table

| Variable | Coefficient | Std.Error | t-stat | p-value | Significant? |
|---|---|---|---|---|---|
| **PRiskFY** (β₁) | 0.0000 | 0.0001 | 0.42 | 0.6713 | No |
| **StyleFrozen** (β₂) | -0.2245 | 0.1063 | -2.11 | 0.0348 | **Yes** |
| **PRiskFY × StyleFrozen** (β₃) | -0.0000 | 0.0000 | -0.31 | 0.7574 | No |

### Model Fit

| Statistic | Value |
|---|---|
| **N** | 5,295 |
| **Firms** | 432 |
| **CEOs** | 418 |
| **R² (overall)** | 0.0056 |
| **R² (within)** | 0.0089 |

### Sample Construction

| Dataset | Observations | Firms |
|---|---|---|
| StyleFrozen | 7,125 | 493 |
| PRiskFY | 65,664 | 7,869 |
| AbsAbInv | 80,048 | 11,256 |
| **Final Merged** | **5,295** | **432** |

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

**Note:** This hypothesis was originally H9 in the pipeline but is documented as H8 for consistency with the hypothesis numbering scheme (H8 takeover was removed from documentation).
