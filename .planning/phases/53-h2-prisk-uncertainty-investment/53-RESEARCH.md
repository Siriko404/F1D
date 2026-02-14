# Phase 53: H2 PRisk x Uncertainty -> Investment Efficiency - Research

**Phase:** 53-h2-prisk-uncertainty-investment
**Research Date:** 2026-02-06
**Status:** Ready for Planning

---

## Executive Summary

This research document covers what you need to know to PLAN Phase 53 well. Phase 53 tests whether **compound uncertainty** (the interaction of Hassan PRisk and Managerial Linguistic Uncertainty) predicts decreased investment efficiency, measured via the correct Biddle et al. (2009) investment residual methodology.

**Key Finding:** Phase 30's `roa_residual` is **INCORRECT** for this hypothesis. Phase 53 must implement the correct Biddle (2009) specification from scratch.

**Critical Implementation Decision:**
- **DO NOT** reuse Phase 30's `roa_residual` - it regresses Delta ROA on CapEx (tests investment -> profitability)
- **DO** implement the correct Biddle specification: Regress Investment on Tobin's Q and Sales Growth by industry-year

---

## 1. What This Phase Tests (Hypothesis Specification)

### H2: PRisk x Uncertainty -> Decreased Investment Efficiency

**Plain English:** When firms face both high political risk (external) and high managerial speech uncertainty (internal) simultaneously, their investment allocation becomes less efficient. Compound uncertainty from multiple sources creates amplified decision-making friction.

**Predicted Sign:** Negative (-) on the interaction term

**Primary Model:**
```
InvestmentResidual_i,t = alpha + beta1*(PRisk_std x Uncertainty_std)_i,t
                        + beta2*PRisk_std_i,t
                        + beta3*Uncertainty_std_i,t
                        + Sum(gamma_j*Controls_j,i,t)
                        + Firm_FE + Year_FE + epsilon_i,t
```

**Key Requirements:**
1. Both PRisk and Uncertainty must be **standardized** (z-score) before interaction
2. Firm + Year fixed effects (tests within-firm variation)
3. Two-way clustered standard errors (firm, year) per Petersen (2009)
4. Controls from Biddle (2009): Cash Flow, Size, Leverage, Tobin's Q, Sales Growth

---

## 2. The Dependent Variable: Correct Biddle (2009) Investment Residual

### The Critical Error in Phase 30

Phase 30's `roa_residual` is **incorrect** for testing investment efficiency. Here's why:

**Phase 30 Implementation (WRONG):**
```python
# Regresses Delta ROA on CapEx
Y: delta_roa_t2 = ROA(t+2) - ROA(t)
X: capex_at, tobins_q
```
This tests whether **investment leads to profitability** - a different question.

**Correct Biddle (2009) Specification (Phase 53 must implement):**
```python
# Regresses Investment on expected investment drivers
Y: Investment_i,t = (CapEx + R&D + Acquisitions - Asset Sales) / lagged(Assets)
X: Tobin's_Q_i,t-1, Sales_Growth_i,t-1
```
The residual represents deviation from expected investment given growth opportunities.

### Implementation Steps for First-Stage Regressions

**1. Construct Investment Variable:**
```python
Investment_i,t = (CapEx_t + R&D_t + Acquisitions_t - AssetSales_t) / Assets_t-1
```

**2. Construct Predictors (lagged):**
```python
Tobin's_Q_i,t-1 = (Assets + MarketEquity - BookEquity) / Assets
Sales_Growth_i,t-1 = (Sales_t-1 - Sales_t-2) / |Sales_t-2|
```

**3. Run Industry-Year Regressions:**
- Group by FF48 industry x fiscal year
- For each cell with >= 20 observations:
  ```
  Investment = beta0 + beta1*Tobin's_Q + beta2*Sales_Growth + epsilon
  ```
- Residual epsilon = InvestmentResidual (inefficiency measure)

**4. Interpret Residuals:**
- Positive (>0): Overinvestment (investing more than expected given opportunities)
- Negative (<0): Underinvestment (investing less than expected)
- Absolute value |epsilon|: Magnitude of inefficiency

### Data Requirements from Compustat

| Variable | Compustat Field | Description |
|----------|-----------------|-------------|
| CapEx | CAPX / CAPXY | Capital expenditures |
| R&D | XRD / XRDQ | Research and development expenses |
| Acquisitions | AQCY | Acquisitions (if available) |
| Asset Sales | SPPEY / SPPEQ | Sale of property, plant, equipment |
| Assets | AT / ATQ | Total assets (lagged for scaling) |
| Tobin's Q | Construction | (AT + MKVALT - CEQ) / AT |
| Sales Growth | SALE / SALEQ | (Sale_t - Sale_t-1) / |Sale_t-1| |

**Note:** Acquisitions data (AQCY) may be sparse. If missing, use:
```
Investment = (CapEx + R&D - AssetSales) / lagged(Assets)
```

---

## 3. The Independent Variable: PRisk x Uncertainty Interaction

### PRisk Data (Hassan et al. measure)

**Location:** `1_Inputs/FirmLevelRisk/firmquarter_2022q1.csv`

**Key Columns:**
- `gvkey`: Firm identifier (zero-pad to 6 digits)
- `date`: Quarter in format "YYYYqQ" (e.g., "2002q1")
- `PRisk`: Political risk score (continuous)
- `NPRisk`: Negative political risk (optional alternative)
- Additional columns: Risk, Sentiment, topic-specific PRisk

**Data Characteristics:**
- 354,518 observations, 2002-2022
- 13,149 unique firms
- Tab-separated format (not comma-separated)

**Loading Approach:**
```python
prisk = pd.read_csv(
    "1_Inputs/FirmLevelRisk/firmquarter_2022q1.csv",
    sep="\t",
    usecols=["gvkey", "date", "PRisk"]
)
# Convert date format "2002q1" to fiscal year-quarter
prisk["year"] = prisk["date"].str[:4].astype(int)
prisk["quarter"] = prisk["date"].str[-1].astype(int)
```

### Managerial Uncertainty (LM Dictionary)

**Location:** Earnings call measures from Step 2 outputs

**Recommended Primary Measure:** `Manager_QA_Uncertainty_pct`

**Alternative Measures:**
- CEO_QA_Uncertainty_pct
- Manager_Pres_Uncertainty_pct
- CEO_Pres_Uncertainty_pct

**Construction:** Uncertainty word count / Total word count (from LM 2024 dictionary)

**Source:** `4_Outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_*.parquet`

### Interaction Term Construction

**CRITICAL: Standardize Before Interaction**

```python
# Step 1: Standardize both components (z-score)
df["PRisk_std"] = (df["PRisk"] - df["PRisk"].mean()) / df["PRisk"].std()
df["Uncertainty_std"] = (df["Manager_QA_Uncertainty_pct"] - df["Manager_QA_Uncertainty_pct"].mean()) / df["Manager_QA_Uncertainty_pct"].std()

# Step 2: Create interaction
df["PRisk_x_Uncertainty"] = df["PRisk_std"] * df["Uncertainty_std"]
```

**Why Standardization (Not Mean-Centering)?**
- Standardization yields interpretable coefficients (one SD change)
- Mean-centering does NOT reduce multicollinearity for interaction terms
- Hypothesis specification (52-HYPOTHESIS-SPECIFICATIONS.md) explicitly requires standardization

---

## 4. Sample Construction and Merge Strategy

### Step 1: Load Earnings Call Sample (Base)

```python
manifest = pd.read_parquet(
    "4_Outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet"
)
# 112,968 observations, 2002-2018
# Columns: gvkey, start_date, year, call_id, ...
```

### Step 2: Load PRisk and Merge

```python
prisk = pd.read_csv("1_Inputs/FirmLevelRisk/firmquarter_2022q1.csv", sep="\t")
prisk["gvkey"] = prisk["gvkey"].astype(str).str.zfill(6)

# Aggregate to firm-year level (mean across quarters)
prisk_annual = prisk.groupby(["gvkey", "year"])["PRisk"].mean().reset_index()

# Merge with manifest
sample = manifest.merge(prisk_annual, on=["gvkey", "year"], how="inner")
```

**Expected Intersection:** ~30,000 firm-year observations, ~3,000 firms

### Step 3: Load Uncertainty Measures and Merge

```python
uncertainty = pd.concat([
    pd.read_parquet(f"4_Outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_{y}.parquet")
    for y in range(2002, 2019)
])

# Aggregate call-level to firm-year level
uncertainty_fy = uncertainty.groupby(["gvkey", "year"])["Manager_QA_Uncertainty_pct"].mean().reset_index()

# Merge
sample = sample.merge(uncertainty_fy, on=["gvkey", "year"], how="left")
```

### Step 4: Load Compustat and Compute Investment Variables

```python
compustat = pd.read_parquet("1_Inputs/comp_na_daily_all/comp_na_daily_all.parquet")

# Filter to sample firms and years
compustat = compustat[compustat["gvkey"].isin(sample["gvkey"])]

# Compute investment and control variables
# (See Section 5 for detailed specifications)
```

### Sample Filters

**Apply standard finance filters:**
1. Exclude financial firms (SIC 6000-6999)
2. Exclude utilities (SIC 4900-4999)
3. Require positive total assets
4. Winsorize continuous variables at 1% and 99% by year

**Primary Sample Period:** 2002-2018 (intersection of datasets)

**Robustness Subsample:** 2006-2018 (excludes sparse early years)

---

## 5. Control Variables (Biddle 2009 Baseline)

All controls should be computed at firm-year level and winsorized.

| Variable | Construction | Compustat Fields |
|----------|-------------|------------------|
| **Cash Flow** | Operating Cash Flow / Assets | OANCFY / AT |
| **Firm Size** | log(Total Assets) | log(AT) |
| **Leverage** | Market Leverage = (DLTT + DLC) / (DLTT + DLC + MKVALT) | (DLTT + DLC) / Total Market Value |
| **Tobin's Q** | (AT + MKVALT - CEQ) / AT | Construction |
| **Sales Growth** | (SALE_t - SALE_t-1) / \|SALE_t-1\| | (SALE - lag(SALE)) / \|lag(SALE)\| |

**Implementation Reference:** Phase 30 (`3_Financial_V2/3.2_H2Variables.py`) has similar control construction. Reuse patterns where applicable.

---

## 6. Regression Infrastructure (Existing)

### Shared Modules Available

**Location:** `2_Scripts/shared/`

| Module | Function | Purpose |
|--------|----------|---------|
| `panel_ols.py` | `run_panel_ols()` | Panel regression with Firm/Year FE, clustering |
| `centering.py` | `center_continuous()` | Mean-centering for interactions |
| `diagnostics.py` | `compute_vif()` | Multicollinearity checks (VIF < 5) |
| `regression_helpers.py` | Various helpers | Standardized regression output |

**Key Features of `run_panel_ols()`:**
- Handles firm + year fixed effects
- Supports double clustering (firm, year) per Petersen (2009)
- VIF computation and diagnostics
- Formatted coefficient output with significance stars
- Returns model, coefficients, summary, diagnostics, warnings

### Example Usage Pattern

```python
from shared.panel_ols import run_panel_ols

result = run_panel_ols(
    df=regression_df,
    dependent="InvestmentResidual",
    exog=["PRisk_x_Uncertainty", "PRisk_std", "Uncertainty_std", "CashFlow", "Size", "Leverage", "TobinQ", "SalesGrowth"],
    entity_col="gvkey",
    time_col="year",
    entity_effects=True,
    time_effects=True,
    cov_type="clustered",
    cluster_cols=["gvkey", "year"],  # Double-clustering
    check_collinearity=True,
    vif_threshold=5.0
)
```

---

## 7. File Structure and Script Organization

### Recommended Script Locations

**Primary Script:**
```
2_Scripts/4_Econometric_V3/4.3_H2_PRiskUncertainty_Investment.py
```

**Following V3 naming convention:**
- V2: Linguistic uncertainty measures (Speech -> Finance outcomes)
- V3: External risk measures (PRisk -> Finance outcomes, interactions)

**Alternative (if V3 not created):**
```
2_Scripts/4_Econometric_V2/4.3_H2_PRiskUncertainty_Investment.py
```

### Output Locations

```
4_Outputs/4_Econometric_V3/4.3_H2_PRiskUncertainty_Investment/{timestamp}/
    - H2_PRiskUncertainty_Investment.parquet  # Regression results
    - H2_InvEfficiency_FirstStage.parquet     # Investment residuals
    - stats.json                               # Summary statistics
    - H2_RESULTS.md                            # Human-readable summary

3_Logs/4_Econometric_V3/4.3_H2_PRiskUncertainty_Investment/{timestamp}.log
```

### Dependencies from Prior Phases

| Phase | Output | Usage |
|-------|--------|-------|
| 1.4 | `master_sample_manifest.parquet` | Base sample (112K calls) |
| 2.2 | `linguistic_variables_*.parquet` | Manager Uncertainty measure |
| 30 | `H2_InvestmentEfficiency.parquet` | Control variables (reference, not reuse for DV) |
| 32 | `shared.panel_ols`, `shared.diagnostics` | Regression infrastructure |

---

## 8. Robustness Checks (Required)

### 1. Alternative Fixed Effects Specifications

**Primary:** Firm + Year FE (tests within-firm variation)

**Robustness:** Industry FF48 + Year FE (tests between-firm effects)
- Rationale: Matches Biddle (2009) first-stage approach
- Allows comparison of within vs. between variation

### 2. Alternative Dependent Variable

**Primary:** Signed InvestmentResidual (tests direction: over vs. under)

**Robustness:** |InvestmentResidual| (tests magnitude of inefficiency)

### 3. Lag Structure

**Primary:** Contemporaneous (t)
- PRisk_t x Uncertainty_t predicts InvestmentEfficiency_t
- Rationale: Earnings calls quarterly; investment responds to current information

**Robustness:** One-year lag (t-1)
- PRisk_t-1 x Uncertainty_t-1 predicts InvestmentEfficiency_t
- Rationale: Address reverse causality concerns

### 4. Subsample Analysis

**Primary:** Full sample 2002-2018

**Robustness:** 2006-2018 (excludes sparse early years)

**Robustness:** High/Low political exposure industries
- Split by FF48 industries with high/low government dependence
- Tests heterogeneity of treatment effect

### 5. Alternative PRisk Measures

**Primary:** PRisk (Hassan main measure)

**Robustness:** NPRisk (Negative political risk)
**Robustness:** Topic-specific PRisk (e.g., PRiskT_tax, PRiskT_trade)

---

## 9. Hypothesis Testing and Success Criteria

### Primary Hypothesis

**H2:** beta1 < 0 (PRisk x Uncertainty interaction decreases investment efficiency)

**One-tailed test:** If coefficient < 0, p_one_tailed = p_two_tailed / 2

**Success Criteria:**
- **Primary:** beta1 < 0 at p < 0.05 (one-tailed)
- **Interpretation if supported:** Compound uncertainty creates amplified real effects on capital allocation
- **Interpretation if null:** Political and managerial uncertainty operate through independent channels

### Statistical Power

**Estimated Power:** >99% for small effect (f2 = 0.02)

**Sample Size Calculation:**
- N ≈ 30,000 firm-year observations
- ~3,000 firms
- Average 10 observations per firm
- Effect size: 0.02 (small)
- alpha: 0.05 (one-tailed)
- Power: >0.99

---

## 10. Implementation Checklist

### Data Preparation
- [ ] Load PRisk data (firmquarter_2022q1.csv)
- [ ] Aggregate PRisk to firm-year level
- [ ] Load linguistic uncertainty measures
- [ ] Aggregate uncertainty to firm-year level
- [ ] Load Compustat data for investment variables
- [ ] Merge datasets on gvkey-year

### Variable Construction
- [ ] Construct Investment = (CapEx + R&D + Acquisitions - AssetSales) / lag(Assets)
- [ ] Construct Tobin's Q (lagged)
- [ ] Construct Sales Growth (lagged)
- [ ] Assign FF48 industry classifications
- [ ] Run first-stage regressions by industry-year (min 20 obs)
- [ ] Extract InvestmentResidual
- [ ] Construct controls (Cash Flow, Size, Leverage, Tobin's Q, Sales Growth)
- [ ] Standardize PRisk and Uncertainty
- [ ] Create interaction term

### Sample Filters
- [ ] Exclude financial firms (SIC 6000-6999)
- [ ] Exclude utilities (SIC 4900-4999)
- [ ] Require positive assets
- [ ] Apply winsorization (1%, 99% by year)

### Regression Execution
- [ ] Primary: Firm + Year FE, double-clustered SE
- [ ] Robustness: Industry + Year FE
- [ ] Robustness: |InvestmentResidual| as DV
- [ ] Robustness: Lagged IVs
- [ ] Robustness: Subsample 2006-2018

### Output Generation
- [ ] Regression results parquet (coefficients, SEs, p-values)
- [ ] stats.json with hypothesis test outcomes
- [ ] H2_RESULTS.md with human-readable summary
- [ ] First-stage residual output (for verification)

---

## 11. Potential Issues and Solutions

### Issue 1: Missing Investment Components

**Problem:** Compustat may lack Acquisitions (AQCY) or Asset Sales (SPPEY)

**Solution:** Use simplified investment measure:
```python
Investment = (CapEx + R&D) / lag(Assets)
```
Document any simplification in research notes.

### Issue 2: Thin Industry-Year Cells

**Problem:** Some FF48-year cells may have < 20 observations for first-stage regression

**Solution:** Follow Phase 30 pattern:
- Fall back to FF12 industry classification
- Require minimum 20 observations
- Skip cells that don't meet threshold (document count)

### Issue 3: GVKEY Matching Inconsistencies

**Problem:** PRisk gvkey may have different formatting (leading zeros)

**Solution:**
```python
df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)
```
Apply to all datasets before merging.

### Issue 4: Temporal Alignment (Quarterly vs. Annual)

**Problem:** PRisk is quarterly, earnings calls are quarterly, but investment measures are often annual

**Solution:**
- Aggregate PRisk to annual (mean of 4 quarters)
- Match fiscal year from earnings call start_date
- Use Compustat quarterly fields (suffixed with Q) where available

### Issue 5: Multicollinearity in Interaction Model

**Problem:** Interaction term correlated with main effects

**Solution:** Standardization (not mean-centering) reduces this issue. VIF check will detect if still problematic. If VIF > 10:
- Document multicollinearity concern
- Present both main effects and interaction model
- Center robustness checks on interaction coefficient

---

## 12. References and Prior Work

### Biddle et al. (2009) - Investment Efficiency

**Citation:** Biddle, G. C., Hilary, G., & Verdi, R. S. (2009). How does financial reporting quality relate to investment efficiency? Journal of Accounting and Economics, 48(2-3), 112-131.

**Key Methodology:**
- First stage: Investment = f(Tobin's Q, Sales Growth) by industry-year
- Residual = deviation from expected investment
- Negative residual = underinvestment, Positive = overinvestment

### Hassan et al. (2019) - Political Risk

**Citation:** Hassan, T. A., Hollander, A. C., van Lent, L., & Tahoun, A. (2019). Firm-level political risk: Measurement and effects. Unpublished working paper.

**Key Methodology:**
- Text-based measure from earnings calls
- Captures firm-specific political risk exposure
- Validated against real outcomes (investment, hiring, stock returns)

### Loughran & McDonald (2011) - Linguistic Uncertainty

**Citation:** Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. Journal of Finance, 66(1), 35-65.

**Key Methodology:**
- Finance-specific word lists
- Uncertainty category (335 words in 2024 version)
- Percent of total words as measure

### Petersen (2009) - Standard Error Clustering

**Citation:** Petersen, M. A. (2009). Estimating standard errors in finance panel data sets: Comparing approaches. Review of Financial Studies, 22(1), 435-480.

**Key Recommendation:**
- Two-way clustering (firm, time) for panel regressions
- Adjusts for both firm-level and time-series correlation

---

## 13. Summary: What You Need to Know

### The Critical Path

1. **DO NOT use Phase 30's roa_residual** - it's the wrong specification
2. **DO implement correct Biddle (2009)** - Investment on Q and Sales Growth
3. **Standardize before interaction** - PRisk and Uncertainty both to z-scores
4. **Use FF48 for first-stage** - Industry-year regressions with min 20 obs
5. **Firm + Year FE, double-clustered SE** - Modern standard for investment efficiency tests

### Data Availability (Confirmed)

| Source | File | Observations | Period |
|--------|------|-------------|--------|
| Earnings calls | master_sample_manifest.parquet | 112,968 | 2002-2018 |
| PRisk | firmquarter_2022q1.csv | 354,518 | 2002-2022 |
| Uncertainty | linguistic_variables_*.parquet | ~112K | 2002-2018 |
| Compustat | comp_na_daily_all.parquet | Millions | Full |

### Expected Sample After Merges

- **N ≈ 30,000** firm-year observations
- **Firms ≈ 3,000** unique firms
- **Years 2002-2018** (17 years)
- **Power >99%** for small effects

### Implementation Order

1. Create data loading and merge script
2. Implement investment residual construction (first-stage)
3. Implement primary regression with interaction term
4. Run robustness checks
5. Generate outputs and summary

---

**End of Research Document**

Next Step: Create execution plan (53-01-PLAN.md) with detailed tasks and verification criteria.
