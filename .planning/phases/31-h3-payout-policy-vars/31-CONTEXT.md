# Phase 31: H3 Payout Policy Variables - Context

**Gathered:** 2026-02-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Construct all dependent variables (Dividend Policy Stability, Payout Flexibility) and control variables (Earnings Volatility, FCF Growth, Firm Maturity) for the H3 (Speech Uncertainty & Payout Policy) hypothesis. Standard controls (Firm Size, ROA, Tobin's Q, Cash Holdings) are reused from H1/H2 outputs.

**Requirements covered:** H3-01, H3-02, H3-03, H3-04, H3-05

</domain>

<decisions>
## Implementation Decisions

All variable definitions are specified in `F1DV2 Hypothesis List.txt` and are **LOCKED**. No discretionary choices exist for the core methodology.

### DV1: Dividend Policy Stability (H3-01)
- **Formula:** `-StdDev(ΔDPS) / Mean(DPS)` over trailing 5 years
- **Source fields:** `dvpspq` (Dividends per Share - Pay Date - Quarter) from Compustat quarterly
- **Calculation:** Compute ΔDPS = DPS_t - DPS_{t-1} for each fiscal year, then rolling 5-year window
- **Sign:** Negative of coefficient of variation (higher = more stable)
- **Coverage:** 796,354 non-null observations in Compustat for dvpspq

### DV2: Payout Flexibility (H3-02)
- **Formula:** `% of years with |ΔDPS| > 5% of prior DPS` over 5-year window
- **Threshold:** 5% of prior year DPS (relative change, not absolute)
- **Coverage check:** Years with meaningful DPS changes (cuts, increases, omissions)
- **Interpretation:** Higher flexibility = more volatile/discretionary payout behavior

### Earnings Volatility Control (H3-03)
- **Formula:** `StdDev(EPSPX)` over trailing 5 years
- **Source field:** `epspxq` (EPS Basic - Excluding Extraordinary Items - Quarterly)
- **Annualize:** Sum quarterly EPS to annual before computing volatility
- **Coverage:** 735,715 non-null observations for epspxq

### FCF Growth Control (H3-03)
- **Formula:** `Annual growth in (OANCF - CAPX) / AT`
- **Source fields:** `oancfy` (Operating Activities NCF - Annual), `capxy` (CapEx - Annual), `atq`
- **Calculation:** FCF_t = (oancfy - capxy) / atq, then growth = (FCF_t - FCF_{t-1}) / |FCF_{t-1}|
- **Coverage:** 699,483 observations with annual cash flow data

### Firm Maturity Control (H3-03)
- **Selected proxy:** DeAngelo et al. Retained Earnings / Total Equity (RE/TE)
- **Rationale:** The specification offers `ln(firm age)` OR dividend history dummy. IPO date (ipodate) has only 41% coverage (395,048/956,229). Retained Earnings (req) has 2,428/2,429 sample firms (99.96% coverage).
- **Formula:** `req / seqq` (Retained Earnings / Stockholders Equity - Quarterly)
- **Interpretation:** Higher RE/TE = more mature firm (retained more earnings over time)

### Standard Controls (from H1/H2)
- **Reuse:** Firm_Size, ROA, Tobin's Q already computed in H1 output
- **Cash Holdings:** Already computed in H1 as CHE/AT
- **Implementation:** Merge from existing H1_CashHoldings.parquet or recompute to maintain independence

### Data Unavailable (Skip)
- **Institutional Ownership:** Thomson Reuters 13F data not present in 1_Inputs
- **Board Independence:** ISS governance data not present in 1_Inputs
- **Specification fallback:** "proxy with firm size if absent" - firm_size already included

### Trailing Window Handling
- **Requirement:** 5-year trailing window for stability/flexibility/volatility
- **Missing data:** Firms with <5 years data use available years (minimum 2 years required)
- **First valid year:** 2006 (first year with complete 5-year trailing window from 2002)

### Sample Scope
- **Dividend payers only:** Filter to firms with DPS > 0 in at least one year of the 5-year window
- **Rationale:** Stability/flexibility undefined for never-payers
- **Non-payers handling:** Can be flagged separately for robustness checks in Phase 36

</decisions>

<specifics>
## Specific Ideas

### From Hypothesis Specification
- "Dividend Policy Stability = Negative of (Standard Deviation of ΔDPS / Mean DPS) over trailing 5 years"
- "Payout Flexibility = Percentage of years with dividend change (cut, omission, or increase) / 5-year window"
- "Changes defined as |ΔDPS| > 5% of prior DPS"
- "Firm_Maturity = Natural log of firm age (years since incorporation) or dummy for dividend history (>5 years of payments)"

### Variable Naming Convention
Following H1/H2 patterns:
- `div_stability` - DV1 (higher = more stable)
- `payout_flexibility` - DV2 (higher = more flexible/volatile)
- `earnings_volatility` - StdDev of annual EPS
- `fcf_growth` - Year-over-year FCF/AT growth
- `firm_maturity` - RE/TE ratio (DeAngelo proxy)

### Output Structure
- File: `4_Outputs/3_Financial_V2/{timestamp}/H3_PayoutPolicy.parquet`
- Stats: `4_Outputs/3_Financial_V2/{timestamp}/stats.json`
- Columns: gvkey, fiscal_year, div_stability, payout_flexibility, earnings_volatility, fcf_growth, firm_maturity, plus standard controls

</specifics>

<deferred>
## Deferred Ideas

None - discussion stayed within phase scope. All implementation details are specified in the hypothesis methodology document.

</deferred>

---

*Phase: 31-h3-payout-policy-vars*
*Context gathered: 2026-02-05*
