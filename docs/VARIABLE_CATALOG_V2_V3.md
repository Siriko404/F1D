# V2/V3 Variable Catalog

**Purpose:** Document all hypothesis-specific variables constructed for H1-H9 testing. Unlike V1 variables (documented in README), V2/V3 variables require script analysis to extract variable definitions, formulas, and output locations.

**Scope:** Financial V2 (H1-H8) and Financial V3 (H9) hypothesis variables constructed from 2002-2018 earnings call data.

---

## Variable Construction Summary

| Hypothesis | Variables | Source Script | Output File | Sample Size | Period |
|------------|------------|----------------|-------------|-------------|---------|
| H1 Cash Holdings | 5 | 3.1_H1Variables.py | H1_CashHoldings.parquet | ~15,000 firm-years | 2002-2018 |
| H2 Investment Efficiency | 4 | 3.2_H2Variables.py | H2_InvestmentEfficiency.parquet | ~26,000 firm-years | 2002-2018 |
| H3 Payout Policy | 6 | 3.3_H3Variables.py | H3_PayoutPolicy.parquet | ~26,000 firm-years | 2002-2018 |
| H5 Dispersion | 4 | 3.5_H5Variables.py | H5_Dispersion.parquet | ~258,000 observations | 2002-2018 |
| H6 CCCL | 4 | 3.6_H6Variables.py | H6_CCCL.parquet | ~21,900 observations | 2006-2018 |
| H7 Illiquidity | 6 | 3.7_H7IlliquidityVariables.py | H7_Illiquidity.parquet | ~26,000 observations | 2002-2018 |
| H8 Takeover | 4 | 3.8_H8TakeoverVariables.py | H8_Takeover.parquet | ~26,000 observations | 2002-2018 |
| V3 H9 StyleFrozen | 6 | 5.8_H9_StyleFrozen.py, 5.8_H9_FinalMerge.py | H9_StyleFrozen.parquet | ~5,300 firm-years | 2003-2017 |

**Total V2/V3 Variables:** ~39 unique hypothesis-specific variables

---

## Data Lineage and Deterministic Construction

All V2/V3 variables are **deterministically constructed** from source data:

- **Source Data:** Compustat fundamentals, CRSP daily stock data, IBES analyst forecasts, SDC M&A database, Hassan political risk index
- **Construction Scripts:** Version-controlled Python scripts in `2_Scripts/3_Financial_V2/` and `2_Scripts/4_Econometric_V2/`

**Note:** V3 scripts were consolidated into V2 in Phase 64 (2026-02-12). H9 scripts are now located at:
- `2_Scripts/3_Financial_V2/3.11_H9_StyleFrozen.py`, `3.12_H9_PRiskFY.py`, `3.13_H9_AbnormalInvestment.py`
- `2_Scripts/4_Econometric_V2/4.11_H9_Regression.py`
- **Reproducibility:** Timestamp-based output directories ensure full reproducibility
- **Winsorization:** 1%/99% winsorization applied to all continuous variables

---

## V1 Control Variables Used in V2/V3

| V1 Variable | Type | Hypotheses Using | Purpose |
|-------------|-------|------------------|---------|
| ClarityCEO | Continuous (std) | H1, H2, H3, H5, H6, H7, H8 | CEO clarity as primary independent variable |
| Size | Log-transformed | All (H1-H9) | Firm size control (log assets or market cap) |
| BM | Continuous | H1, H2, H3, H9 | Book-to-market ratio control |
| Lev | Continuous | H1, H2, H3, H7, H9 | Leverage control |
| ROA | Continuous | H1, H2, H3, H9 | Return on assets control |
| CashHoldings | Continuous | H2 (DV), H3 | Cash holdings ratio |
| Manager_QA_Uncertainty_pct | Continuous (0-100) | H5, H7, H8 | Manager QA uncertainty measure |
| CEO_QA_Uncertainty_pct | Continuous (0-100) | H5, H7, H8 | CEO QA uncertainty measure |
| StockRet | Continuous (%) | H1, H2, H3, H7, H8 | Annual stock return |
| Volatility | Continuous (%) | H1, H7, H8 | Stock return volatility |

---

## Hypothesis Variable Details

### H1: Cash Holdings (V2)

**Source Script:** `2_Scripts/3_Financial_V2/3.1_H1Variables.py`

**Output File:** `outputs/3_Financial_V2/{timestamp}/H1_CashHoldings.parquet`

**Variables:**

| Variable | Type | Formula | Data Source | Description |
|----------|------|---------|-------------|-------------|
| CHE | Continuous | cheq (Compustat) | Compustat Quarterly | Cash and short-term investments |
| AT | Continuous | atq (Compustat) | Compustat Quarterly | Total assets |
| CashHoldings | Ratio | CHE / AT | Constructed | Cash-to-assets ratio (DV) |
| log_CashHoldings | Continuous | log(CashHoldings) | Constructed | Log-transformed cash holdings |
| ClarityCEO | Continuous | Phase 4 output | V2 linguistic | CEO clarity (IV) |
| ClarityCEO_x_Size | Interaction | ClarityCEO * Size | Constructed | CEO clarity * size interaction |

**Control Variables (from V1):** Size, BM, Lev, ROA

**Sample Characteristics:**
- Period: 2002-2018
- Firms: ~2,500 unique gvkeys
- Observations: ~15,000 firm-years
- Exclusions: Financial firms (SIC 6000-6999), utilities (SIC 4900-4999)

**Hypothesis Context:** H1 tests whether CEO clarity affects cash holdings policy. Higher clarity CEOs may hold more cash due to better communication with capital providers.

**Regression Specification:**
```
CashHoldings = beta0 + beta1*ClarityCEO + beta2*Size + beta3*BM + beta4*Lev + beta5*ROA + FE
```

---

### H2: Investment Efficiency (V2)

**Source Script:** `2_Scripts/3_Financial_V2/3.2_H2Variables.py`

**Output File:** `outputs/3_Financial_V2/{timestamp}/H2_InvestmentEfficiency.parquet`

**Variables:**

| Variable | Type | Formula | Data Source | Description |
|----------|------|---------|-------------|-------------|
| Capex | Continuous | capxy (Compustat) | Compustat Quarterly | Capital expenditures |
| AT | Continuous | atq (Compustat) | Compustat Quarterly | Total assets |
| Investment | Ratio | Capex / AT_lag1 | Constructed | Investment rate |
| Biddle_residual | Continuous | Residual from Biddle (2013) model | Constructed | Abnormal investment (DV) |
| Overinvestment | Dummy | Biddle_residual > top quintile | Constructed | Overinvestment indicator |
| Underinvestment | Dummy | Biddle_residual < bottom quintile | Constructed | Underinvestment indicator |
| Efficiency_Score | Continuous | -|Biddle_residual| | Investment efficiency score |
| PRisk | Continuous | Hassan (2019) index | V2 political risk | Political risk (IV) |
| PRisk_x_Uncertainty | Interaction | PRisk * Uncertainty | Constructed | Interaction term |

**Biddle (2013) Investment Model:**
```
Investment = beta0 + beta1*Size_lag + beta2*BM_lag + beta3*Lev_lag + beta4*Cash_lag + beta5*StockRet_lag + beta6*Investment_lag + FE + epsilon
```

**Sample Characteristics:**
- Period: 2002-2018
- Firms: ~3,000 unique gvkeys
- Observations: ~26,000 firm-years
- Exclusions: Financial firms, utilities

**Hypothesis Context:** H2 tests whether political risk moderates the relationship between CEO uncertainty and investment efficiency.

**Regression Specification:**
```
|Biddle_residual| = beta0 + beta1*Uncertainty + beta2*PRisk + beta3*Uncertainty*PRisk + Controls + FE
```

---

### H3: Payout Policy (V2)

**Source Script:** `2_Scripts/3_Financial_V2/3.3_H3Variables.py`

**Output File:** `outputs/3_Financial_V2/{timestamp}/H3_PayoutPolicy.parquet`

**Variables:**

| Variable | Type | Formula | Data Source | Description |
|----------|------|---------|-------------|-------------|
| Dividend_Payout | Ratio | DVC / NI | Constructed | Dividend payout ratio (DV) |
| Dividend_Yield | Ratio | DPS / Price | Constructed | Dividend yield |
| Payout_Stability | Continuous | std(Dividend_Payout, 3y) | Constructed | 3-year payout stability |
| Payout_Flexibility | Continuous | NI - Dividends | Constructed | Retained earnings (flexibility) |
| Repurchases | Ratio | Repurchase / AT | Constructed | Share repurchase intensity |
| Total_Payout | Ratio | (Dividends + Repurchases) / AT | Constructed | Total payout ratio |
| ClarityCEO | Continuous | Phase 4 output | V2 linguistic | CEO clarity (IV) |

**Components:**
- DVC: Common dividends (Compustat: dvcq)
- DPS: Dividends per share (Compustat: dvy)
- NI: Net income (Compustat: niq)
- Price: Stock price (CRSP: PRC)
- Repurchase: Share repurchases (Compustat: prstkcq)

**Sample Characteristics:**
- Period: 2002-2018
- Firms: ~2,800 unique gvkeys
- Observations: ~26,000 firm-years

**Hypothesis Context:** H3 tests whether CEO clarity affects payout policy. Clearer CEOs may have more predictable dividend policies.

**Regression Specification:**
```
Dividend_Payout = beta0 + beta1*ClarityCEO + Controls + FE
```

---

### H5: Analyst Forecast Dispersion (V2)

**Source Script:** `2_Scripts/3_Financial_V2/3.5_H5Variables.py`

**Output File:** `outputs/3_Financial_V2/{timestamp}/H5_Dispersion.parquet`

**Variables:**

| Variable | Type | Formula | Data Source | Description |
|----------|------|---------|-------------|-------------|
| STDEV | Continuous | std(Analyst forecasts) | IBES Detail | Standard deviation of EPS forecasts |
| MEANEST | Continuous | mean(Analyst forecasts) | IBES Detail | Mean EPS forecast |
| Analyst_Dispersion | Ratio | STDEV / |MEANEST| | Constructed | Forecast dispersion (DV) |
| Forecast_Count | Count | count(Forecasts) | IBES Detail | Number of analysts |
| Manager_QA_Weak_Modal_pct | Continuous | Phase 4 output | V2 linguistic | Manager weak modal language (IV) |
| Manager_Pres_Weak_Modal_pct | Continuous | Phase 4 output | V2 linguistic | Manager presentation weak modal (IV) |
| CEO_QA_Weak_Modal_pct | Continuous | Phase 4 output | V2 linguistic | CEO QA weak modal (IV) |
| Uncertainty_Gap | Continuous | QA_Uncertainty - Pres_Uncertainty | Constructed | QA-Presentation gap (IV) |

**IBES Detail File Fields:**
- ACTUALS: Actual EPS
- MEANEST: Mean forecast
- STDEV: Standard deviation
- NUMEST: Number of estimates

**Sample Characteristics:**
- Period: 2002-2018
- Firms: ~2,400 unique gvkeys
- Observations: ~258,000 firm-analyst observations
- Source: IBES Detail file

**Hypothesis Context:** H5 tests whether hedging language (weak modals) and uncertainty gap predict analyst forecast dispersion.

**Regression Specification (H5-A):**
```
Dispersion = beta0 + beta1*WeakModal + beta2*Uncertainty + Controls + FE
```

**Regression Specification (H5-B):**
```
Dispersion = beta0 + beta1*(QA_Uncertainty - Pres_Uncertainty) + Controls + FE
```

---

### H6: SEC Scrutiny - CCCL (V2)

**Source Script:** `2_Scripts/3_Financial_V2/3.6_H6Variables.py`

**Output File:** `outputs/3_Financial_V2/{timestamp}/H6_CCCL.parquet`

**Variables:**

| Variable | Type | Formula | Data Source | Description |
|----------|------|---------|-------------|-------------|
| shift_share | Continuous | Shift-share instrument | Constructed | Shift-share IV for CCCL exposure |
| CCCL_exposure | Dummy | firm_has_cccl = 1 | Constructed | CCCL treatment indicator |
| CCCL_intensity | Continuous | sales_exposure * cccl_severity | Constructed | CCCL exposure intensity |
| CCCL_exposure_regional | Dummy | regional_cccl = 1 | Constructed | Regional CCCL variant |
| CCCL_industry | Continuous | industry_cccl_index | Constructed | Industry-level CCCL |
| Manager_QA_Uncertainty_pct | Continuous | Phase 4 output | V2 linguistic | Manager QA uncertainty (DV) |
| CEO_QA_Uncertainty_pct | Continuous | Phase 4 output | V2 linguistic | CEO QA uncertainty (DV) |

**Shift-Share Instrument Construction:**
```
shift_intensity_mkvalt_ff48_lag = (initial_ind_share * national_cccl_intensity)
```

**Sample Characteristics:**
- Period: 2006-2018 (CCCL enacted 2007)
- Firms: ~2,300 unique gvkeys
- Observations: ~21,900 observations
- 2SLS Estimation with shift-share instrument

**Hypothesis Context:** H6 tests whether SEC CCCL scrutiny reduces CEO speech uncertainty. Uses shift-share instrument for causal identification.

**Regression Specification (2SLS):**
```
First stage:   CCCL_exposure = pi0 + pi1*shift_share + Controls + FE
Second stage:  Uncertainty = beta0 + beta1*CCCL_exposure_pred + Controls + FE
```

**Pre-trends Test:**
```
Uncertainty = beta0 + beta1*CCCL_t + beta2*CCCL_t+1 + beta3*CCCL_t+2 + Controls + FE
```

---

### H7: Stock Illiquidity (V2)

**Source Script:** `2_Scripts/3_Financial_V2/3.7_H7IlliquidityVariables.py`

**Output File:** `outputs/3_Financial_V2/{timestamp}/H7_Illiquidity.parquet`

**Variables:**

| Variable | Type | Formula | Data Source | Description |
|----------|------|---------|-------------|-------------|
| Amihud | Continuous | mean(|RET| / Volume) * 1e6 | CRSP Daily | Amihud illiquidity (primary DV) |
| log_Amihud | Continuous | log(Amihud + 1) | Constructed | Log Amihud |
| Amihud_lag1 | Continuous | Amihud_t+1 | Constructed | Forward Amihud (t+1) |
| Roll_spread | Continuous | 2 * sqrt(-autocov(RET)) | CRSP Daily | Roll spread (robustness DV) |
| Roll_spread_lag1 | Continuous | Roll_spread_t+1 | Constructed | Forward Roll spread (t+1) |
| Volatility | Continuous | std(RET) * sqrt(252) * 100 | CRSP Daily | Annualized stock volatility |
| StockRet | Continuous | ((1+RET).prod() - 1) * 100 | CRSP Daily | Annual stock return |
| trading_days | Count | count(valid_days) | CRSP Daily | Trading days per year |
| Manager_QA_Uncertainty_pct | Continuous | Phase 4 output | V2 linguistic | Manager QA uncertainty (IV) |
| CEO_QA_Uncertainty_pct | Continuous | Phase 4 output | V2 linguistic | CEO QA uncertainty (IV) |

**Amihud (2002) Formula:**
```
ILLIQ_{i,y} = (1/D) * sum(|r_{d}| / VOLD_{d}) * 1e6
```
- D: Trading days in year
- r_d: Daily return
- VOLD_d: Daily dollar volume (|PRC| * VOL)

**Roll (1984) Formula:**
```
SPREAD = 2 * sqrt(-cov(r_t, r_{t-1}))
```

**Sample Characteristics:**
- Period: 2002-2018
- Firms: ~3,000 unique gvkeys
- Observations: ~26,000 firm-years
- Minimum trading days: 50 per year
- Source: CRSP Daily Stock File (DSF)

**Hypothesis Context:** H7 tests whether CEO speech uncertainty increases stock illiquidity. Uses forward-looking DV (t+1) for causal interpretation.

**Regression Specification:**
```
Illiquidity_t+1 = beta0 + beta1*Uncertainty_t + Controls_t + FE
```

---

### H8: Takeover Probability (V2)

**Source Script:** `2_Scripts/3_Financial_V2/3.8_H8TakeoverVariables.py`

**Output File:** `outputs/3_Financial_V2/{timestamp}/H8_Takeover.parquet`

**Variables:**

| Variable | Type | Formula | Data Source | Description |
|----------|------|---------|-------------|-------------|
| takeover_fwd | Dummy | max(takeover_t+1) | SDC Platinum | Forward takeover indicator (DV) |
| takeover_target | Dummy | deal_status = Completed | SDC Platinum | Takeover target (current year) |
| takeover_acquirer | Dummy | acquirer_flag = 1 | SDC Platinum | Takeover acquirer |
| deal_value | Continuous | deal_value_usd | SDC Platinum | Deal value (USD millions) |
| takeover_announced_fwd | Dummy | max(announced_t+1) | SDC Platinum | Announced takeover (robustness) |
| takeover_hostile_fwd | Dummy | max(hostile_t+1) | SDC Platinum | Hostile takeover (robustness) |
| Manager_QA_Uncertainty_pct | Continuous | Phase 4 output | V2 linguistic | Manager QA uncertainty (IV) |
| CEO_QA_Uncertainty_pct | Continuous | Phase 4 output | V2 linguistic | CEO QA uncertainty (IV) |

**SDC Platinum Fields:**
- Target 6-digit CUSIP: Target identifier
- Date Announced: Announcement date
- Deal Status: Completed/Pending/Withdrawn
- Deal Attitude: Friendly/Hostile/Unsolicited
- Deal Value (USD Millions): Transaction value

**CUSIP-GVKEY Mapping:** Uses CRSP-Compustat CCM link table

**Sample Characteristics:**
- Period: 2002-2018
- Firms: ~3,000 unique gvkeys
- Observations: ~26,000 firm-years
- Takeover rate: ~2-3% annually
- Source: SDC Platinum M&A database

**Hypothesis Context:** H8 tests whether CEO speech uncertainty predicts takeover probability. Uses forward-looking DV (t+1).

**Regression Specification (Logit):**
```
logit(P(Takeover_t+1)) = beta0 + beta1*Uncertainty_t + Controls_t + FE
```

**M&A Control Variables:** Size, Leverage, ROA, MTB, Liquidity, R&D Intensity, Stock Returns

---

### H9: CEO Style and Political Risk Interaction (formerly V3, now in V2)

**Source Scripts (consolidated to V2 in Phase 64):**
- `2_Scripts/3_Financial_V2/3.11_H9_StyleFrozen.py`
- `2_Scripts/3_Financial_V2/3.12_H9_PRiskFY.py`
- `2_Scripts/3_Financial_V2/3.13_H9_AbnormalInvestment.py`
- `2_Scripts/4_Econometric_V2/4.11_H9_Regression.py`

**Output File:** `outputs/5_Financial_V2/{timestamp}/H9_StyleFrozen.parquet` (via 4.11_H9_Regression)

**Variables:**

| Variable | Type | Formula | Data Source | Description |
|----------|------|---------|-------------|-------------|
| StyleFrozen | Continuous | ClarityCEO (persistent trait) | Phase 56 | CEO vagueness style at firm-year |
| PRiskFY | Continuous | mean(PRisk quarters in 366-day window) | Hassan index | Fiscal-year political risk |
| AbsAbInv | Continuous | |Biddle_residual| | Constructed | Absolute abnormal investment (DV) |
| PRiskFY_x_StyleFrozen | Interaction | PRiskFY * StyleFrozen | Constructed | Political risk * CEO style |
| gvkey | Categorical | Compustat identifier | Compustat | Firm identifier |
| fyear | Integer | Fiscal year | Compustat | Fiscal year |
| Size | Continuous | log(AT) | Compustat | Firm size control |
| BM | Continuous | Book / Market | Constructed | Book-to-market control |
| Lev | Continuous | Debt / Assets | Constructed | Leverage control |
| ROA | Continuous | NI / AT | Constructed | Profitability control |
| CashHoldings | Continuous | CHE / AT | Constructed | Cash holdings control |

**StyleFrozen Construction (Frozen Constraint):**
```
For each firm-year (gvkey, fyear):
1. Filter calls where start_date <= fy_end (no look-ahead)
2. Count calls by CEO in fiscal year
3. Select CEO with MAX calls (dominant CEO)
4. Assign CEO's ClarityCEO score (time-invariant trait)
5. Tiebreaker: Earlier first_call_date
```

**PRiskFY Construction:**
```
PRiskFY = mean(PRisk_q for q in quarters where call_date in [fy_end - 366, fy_end])
```
- Fiscal-year political risk index
- Uses all quarters within 366-day window ending on fiscal year-end
- Hassan political risk index at state-month level

**AbsAbInv Construction:**
```
1. Estimate Biddle (2009) investment model (same as H2)
2. Extract residuals: Biddle_residual
3. AbsAbInv = |Biddle_residual| (absolute value)
4. Create t+1 version for regression: AbsAbInv_t+1
```

**Sample Characteristics:**
- Period: 2003-2017 (restricted by data availability)
- Firms: 432 unique gvkeys (final merged)
- CEOs: 418 unique ceo_ids
- Observations: 5,295 firm-years
- Coverage: ~6% of Compustat universe (requires StyleFrozen + PRiskFY + AbsAbInv)

**Hypothesis Context:** H9 tests whether CEO communication style moderates the relationship between political risk and abnormal investment. Uses persistent CEO trait (StyleFrozen) rather than time-varying clarity.

**Regression Specification:**
```
AbsAbInv_t+1 = beta0 + beta1*PRiskFY_t + beta2*StyleFrozen_t + beta3*(PRiskFY_t * StyleFrozen_t) + Controls_t + FE + epsilon_t+1
```

**Hypothesis:** beta3 != 0 (CEO style moderates PRisk -> abnormal investment)

**CEO Selection Logic:**
- StyleFrozen is a CEO trait, not firm-specific
- Same ceo_id may appear with multiple gvkeys over time
- CEO Clarity derived from Phase 56 (CEO-firm random effects model)
- Frozen constraint prevents look-ahead bias

---

## Deterministic Construction Properties

All V2/V3 variables are constructed with **deterministic scripts**:

1. **Reproducibility:** Same inputs + same script = identical outputs
2. **Version Control:** All scripts in `2_Scripts/` with git history
3. **Timestamped Outputs:** Output directories use `{timestamp}` for traceability
4. **Input Validation:** Scripts validate input files and versions
5. **Checksums:** stats.json files record input/output file checksums
6. **Logging:** All scripts write detailed logs to `3_Logs/`

**To Reconstruct V2/V3 Variables:**
```bash
# Example: Reconstruct H1 Cash Holdings
cd 2_Scripts/3_Financial_V2
python 3.1_H1Variables.py
```

Output will be written to `outputs/3_Financial_V2/{timestamp}/H1_CashHoldings.parquet`

---

## Variable Sources by Data Provider

| Provider | Variables | Access | Notes |
|----------|------------|--------|-------|
| **Compustat** | CHE, AT, Capex, NI, DVC, DPS, Debt, Book Equity | Wharton WRDS | Quarterly fundamentals |
| **CRSP** | RET, VOL, PRC, ASKHI, BIDLO | Wharton WRDS | Daily stock data |
| **IBES** | STDEV, MEANEST, NUMEST, ACTUALS | Wharton WRDS | Analyst forecasts |
| **SDC Platinum** | Deal status, deal value, deal attitude | Wharton WRDS | M&A transactions |
| **Hassan (2019)** | PRisk index by state-month | Author data | Political risk |
| **Phase 4 (V2)** | ClarityCEO, Uncertainty_pct, Weak_Modal_pct | Local output | Linguistic variables |
| **Phase 56 (V3)** | ClarityCEO (CEO trait) | Local output | CEO clarity scores |

---

## Related Documentation

- **V1 Variables:** `README.md` (base firm controls and linguistic variables)
- **Hypothesis Results:** `outputs/4_Econometric_V2/H*_Hypothesis_Documentation.md`
- **Script Documentation:** `docs/SCRIPT_DOCSTANDARD.md`
- **Sample Construction:** `.planning/phases/28-v2-structure-setup/`

---

## Variable Catalog Maintenance

**Last Updated:** 2026-02-11

**Update Procedure:**
1. When adding new hypothesis variables, update this catalog
2. Document: source script, output file, formula, sample characteristics
3. Add entry to summary table
4. Update total variable count
5. Commit with message: `docs(61-04): update V2/V3 variable catalog`

**Verification:**
- All scripts follow `SCRIPT_DOCSTANDARD.md` conventions
- Output files include `stats.json` with variable statistics
- Hypothesis documentation includes sample sizes and periods
