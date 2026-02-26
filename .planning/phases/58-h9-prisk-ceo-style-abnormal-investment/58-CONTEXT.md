# Phase 58: H9 PRisk x CEO Style -> Abnormal Investment - Context

**Created:** 2026-02-10
**Status:** Ready for execution

---

## Phase Boundary

Test whether Hassan PRisk (political risk) has a STRONGER effect on Biddle-style abnormal investment when the CEO has a persistently vague communication style. This is a moderation hypothesis where CEO communication style (a persistent personal trait from Phase 56) interacts with political risk exposure to predict abnormal investment.

---

## Hypothesis Statement

**H9:** The effect of Hassan PRisk on abnormal investment is MODERATED by CEO communication clarity. Specifically, CEOs with persistently vague communication styles will show a stronger (weaker) relationship between PRisk and abnormal investment compared to clear-speaking CEOs.

**Regression Model:**
```
AbsAbInv_{i,t+1} = β0 + β1*PRiskFY_{i,t} + β2*StyleFrozen_{i,t}
                + β3*(PRiskFY_{i,t} × StyleFrozen_{i,t})
                + γ'*Controls_{i,t}
                + FirmFE_i + YearFE_t + ε
```

**Key Coefficient:** β3 (interaction term)
- β3 > 0: Vaguer CEOs show STRONGER PRisk -> abnormal investment relationship
- β3 < 0: Vaguer CEOs show WEAKER PRisk -> abnormal investment relationship
- β3 ≈ 0: CEO style does NOT moderate (meaningful null possible)

---

## Theoretical Foundation

### Hassan et al. (2019) - Aggregate News and Political Risk
- PRisk captures firm-level exposure to political-related economic uncertainty
- Measured from firm-specific 10-K filings using text analysis
- Higher PRisk associated with reduced investment, hiring, and R&D

### Dzieliński, Wagner, Zeckhauser (2020) - CEO Communication Style
- CEO speech patterns are persistent personal traits (ClarityCEO)
- Vague CEOs use more uncertainty words, independent of firm characteristics
- CEO style extracted via fixed effects regression (Phase 56)

### Biddle et al. (2009) - Investment Efficiency
- Abnormal investment measures deviation from expected investment given growth opportunities
- Expected investment modeled as function of sales growth by industry-year
- Large |AbInv| indicates inefficient investment (over- or under-investment)

### H9 Contribution
Tests whether CEO communication style interacts with political risk to produce abnormal investment patterns. Vague CEOs may:
- Overreact to political risk (under-invest more when PRisk high)
- Under-react (if vagueness masks true risk exposure)
- Show no difference (if investment decisions driven by fundamentals, not style)

---

## Implementation Decisions

### Wave Structure (4 Plans)

**Wave 1: Variable Construction (3 plans in parallel)**
- 58-01: Construct StyleFrozen (CEO vagueness at firm-year level)
- 58-02: Construct PRiskFY (fiscal-year PRisk from quarterly)
- 58-03: Construct AbsAbInv + Controls (Biddle abnormal investment)

**Wave 2: Merge and Regression (1 plan)**
- 58-04: Merge FINAL_PANEL and run H9 regression

### Key Input Data Sources

1. **CEO Clarity Scores (Phase 56):**
   - Path: `4_Outputs/4.1.1_CeoClarity_CEO_Only/2026-01-22_230058/ceo_clarity_scores.parquet`
   - Columns: ceo_id, gamma_i, ClarityCEO_raw, ClarityCEO, n_calls, ceo_name
   - ClarityCEO is time-invariant per CEO (standardized to mean=0, SD=1)
   - Negative values = more vague (higher uncertainty word usage)

2. **Hassan PRisk Data:**
   - Path: `1_Inputs/FirmLevelRisk/firmquarter_2022q1.csv`
   - Columns: gvkey, date (e.g., "2002q1"), PRisk, NPRisk, PSentiment
   - Quarterly format, need to aggregate to fiscal years
   - PRisk values range 0-1000+ typically

3. **Compustat Data:**
   - Path: `1_Inputs/comp_na_daily_all/comp_na_daily_all.parquet`
   - For investment construction (capx, xrd, aqc, sppe, at, sale)
   - For controls (dltt, dlc, che, oibdp/ni, prcc_f, csho)
   - For fiscal year alignment (datadate, fyear, sic)

4. **Manifest (Call-Level CEO Assignments):**
   - Path: `4_Outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet`
   - Columns: file_name, gvkey, start_date, ceo_id, ceo_name
   - Links each earnings call to its firm and CEO
   - Enables frozen constraint (no future information)

### StyleFrozen Construction Details

**Frozen Constraint:** Use only CEO-firm assignments observable as of fiscal year-end
- Filter: call.start_date <= fiscal_year.datadate
- Prevents look-ahead bias (no future calls used)

**CEO Selection per Firm-Year:**
- Firms may have CEO turnover within a fiscal year
- Strategy: Select CEO with MOST calls in that fiscal year
- Tiebreaker: Earlier first_call_date (longer tenure)

**CEO Moves Between Firms:**
- Same ceo_id may appear with multiple gvkeys over time
- CEO Clarity is a personal trait, not firm-specific
- Each firm-year gets the serving CEO's style score

### PRiskFY Construction Details

**Fiscal Year Aggregation:**
- For each firm-year with fiscal year-end date (fy_end = datadate):
  - Collect PRisk quarters where: fy_end - 366 days < cal_q_end <= fy_end
  - This captures approximately 4 calendar quarters (may be 3-4 depending on fiscal year-end)

**Minimum Quarters Rule:**
- Require >= 2 quarters in window
- If < 2: PRiskFY = missing, DROP
- If 2-4: Take mean of available quarters
- NO forward-filling or interpolation

**Calendar Quarter-End Dates:**
- Q1: March 31
- Q2: June 30
- Q3: September 30
- Q4: December 31

### AbsAbInv Construction Details (Biddle 2009)

**Total Investment Definition:**
```
TotalInv_{t+1} = (capx_{t+1} + xrd_{t+1} + aqc_{t+1} - sppe_{t+1}) / at_t
```
- capx_{t+1}: CAPEX required (non-missing)
- xrd_{t+1}: R&D, set to 0 if missing
- aqc_{t+1}: Acquisitions, set to 0 if missing
- sppe_{t+1}: Asset sales, set to 0 if missing
- at_t: Assets at time t (denominator)

**First-Stage Expected Investment:**
```
TotalInv_{t+1} = a_{ind2,t} + b_{ind2,t} * SalesGrowth_t + e
```
- Run by (ind2, fyear) cells
- Require N >= 30 observations per cell
- Fallback to ind1 if ind2 cell too small
- AbsAbInv = |e| (absolute residual)

**Controls (all at time t):**
- ln_at_t: log(assets) - size
- lev_t: (dltt + dlc) / at_t - leverage
- cash_t: che / at_t - cash holdings
- roa_t: oibdp / at_t (or ni / at_t) - profitability
- mb_t: (prcc_f * csho) / at_t - market-to-book
- SalesGrowth_t: (sale_t - sale_{t-1}) / sale_{t-1}

**Winsorization:**
- All variables winsorized at 1%/99% by fyear
- Applied after first-stage regression

### Regression Specification

**Model:**
```
AbsAbInv_{i,t+1} = β0 + β1*PRiskFY_t + β2*StyleFrozen_t
                + β3*(PRiskFY_t × StyleFrozen_t)
                + γ1*ln_at_t + γ2*lev_t + γ3*cash_t + γ4*roa_t + γ5*mb_t + γ6*SalesGrowth_t
                + FirmFE_i + YearFE_t + ε
```

**Fixed Effects:**
- Firm FE: One dummy per gvkey (controls for time-invariant firm characteristics)
- Year FE: One dummy per fyear (controls for aggregate time trends)

**Standard Errors:**
- Clustered by gvkey (firm level)
- Allows for arbitrary serial correlation within firms

**Sample Period:**
- Primary: 2002-2018 (full V2 sample)
- PRisk data availability may limit end year

---

## Expected Outcomes

### Potential Findings

1. **β3 > 0 (significant):**
   - Vague CEOs show STRONGER PRisk -> abnormal investment relationship
   - Interpretation: Vague communication amplifies political risk effects on investment
   - Possible mechanism: Vague CEOs overreact to uncertainty or signal more risk

2. **β3 < 0 (significant):**
   - Vague CEOs show WEAKER PRisk -> abnormal investment relationship
   - Interpretation: Vague communication dampens political risk effects
   - Possible mechanism: Vagueness masks true risk, markets discount vague speech

3. **β3 ≈ 0 (null):**
   - CEO style does NOT moderate PRisk -> abnormal investment
   - Interpretation: political risk effects operate through channels other than CEO communication
   - Could be meaningful: Investment decisions driven by fundamentals, not CEO style

### Power Considerations

- Sample size: Expected ~5,000-15,000 firm-years
- Number of firms: ~1,000-2,000
- Number of CEOs: ~500-1,000
- Interaction effect typically requires larger sample
- May have limited power to detect small interaction effects

---

## Validation Checklist

Before marking Phase 58 complete, verify:

- [ ] StyleFrozen correctly assigned using frozen constraint (no future calls)
- [ ] CEO turnover handled via max calls selection
- [ ] CEO moves between firms tracked correctly
- [ ] PRiskFY computed with 366-day window and >=2 quarters rule
- [ ] AbsAbInv computed per Biddle (2009) specification
- [ ] All controls constructed and winsorized
- [ ] FINAL_PANEL has no missing values
- [ ] Interaction term created correctly
- [ ] Regression includes Firm FE + Year FE
- [ ] Standard errors clustered by firm
- [ ] β3 interpreted in economic terms
- [ ] Sanity checks documented

---

## Deferred Ideas

**Robustness Checks (if time permits):**
- Alternative abnormal investment measures (e.g., Chen et al. residual)
- Alternative CEO style measures (e.g., presentation clarity only)
- Subsample analysis by industry (high vs low policy sensitivity)
- Alternative clustering (two-way firm-year)

**Alternative Specifications:**
- Include industry-by-year fixed effects instead of firm FE
- Use NPRisk or PSentiment instead of PRisk
- Lag PRiskFY to t-1 for additional causality

**Extensions:**
- Test triple interaction: PRisk × Style × IndustryPolicyExposure
- Examine nonlinear effects (quadratic terms)
- Separate over-investment vs under-investment (sign of residual)

---

## Outputs

### 1. StyleFrozen Dataset
- **File:** `style_frozen.parquet`
- **Columns:** gvkey, fyear, style_frozen, ceo_id, ceo_name, n_calls_fy
- **Coverage:** ~10,000-30,000 firm-years

### 2. PRiskFY Dataset
- **File:** `priskfy.parquet`
- **Columns:** gvkey, fyear, PRiskFY, n_quarters_used
- **Coverage:** ~5,000-15,000 firm-years

### 3. Abnormal Investment Dataset
- **File:** `abnormal_investment.parquet`
- **Columns:** gvkey, fyear, AbsAbInv, TotalInv, SalesGrowth, controls
- **Coverage:** ~10,000-20,000 firm-years

### 4. Final Panel
- **File:** `final_panel.parquet`
- **Columns:** All merged variables
- **Coverage:** ~5,000-15,000 firm-years (complete cases)

### 5. Regression Results
- **File:** `h9_regression_results.csv`
- **Content:** Coefficients, t-stats, p-values for all variables
- **Key:** β3 (PRiskFY × StyleFrozen)

### 6. Summary Reports
- **Files:** `report_step58_01.md` through `report_step58_04.md`
- **Content:** Sample stats, methodology documentation, findings interpretation

---

*Phase: 58-h9-prisk-ceo-style-abnormal-investment*
*Context: 2026-02-10*
*Blueprint: Based on H9 spec.txt*
