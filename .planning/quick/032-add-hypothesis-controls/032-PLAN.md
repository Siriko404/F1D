# Quick Task 032: Add Control Variables to Hypothesis Documentation

**Date:** 2026-02-11
**Status:** COMPLETE

## Description

Add control variables and results sections to all hypothesis documentation files (H1-H8).

**Important Note:** H8 documentation now refers to H9 (PRisk × CEO Style → Abnormal Investment) per the user's request to rename H9 to H8 in documentation. The original H8 (Takeover) hypothesis has been removed from documentation. This renaming applies ONLY to documentation files - the pipeline naming remains unchanged (H8 takeover scripts remain as 4.8_H8TakeoverRegression.py).

## Changes Made

### H1 (Cash Holdings)
- Added Control Variables section with 7 control variables:
  - firm_size (Log total assets)
  - tobins_q (Tobin's Q)
  - roa (Return on assets)
  - capex_at (Capital expenditures / Total assets)
  - dividend_payer (Dividend payer dummy)
  - ocf_volatility (Operating cash flow volatility)
  - current_ratio (Current ratio)
  - leverage (Debt / Total assets)

### H2 (Investment Efficiency)
- Added Control Variables section with 8 control variables for efficiency_score DV:
  - tobins_q (Tobin's Q)
  - cf_volatility (Cash flow volatility)
  - industry_capex_intensity (Industry capital expenditure intensity)
  - analyst_dispersion (Analyst forecast dispersion)
  - firm_size (Log total assets)
  - roa (Return on assets)
  - fcf (Free cash flow)
  - earnings_volatility (Earnings volatility)
- Note: Same controls used for roa_residual DV

### H3 (Payout Policy)
- Added Control Variables section with 8 control variables:
  - earnings_volatility (Earnings volatility)
  - fcf_growth (Free cash flow growth)
  - firm_maturity (Firm age/lifecycle stage)
  - firm_size (Log total assets)
  - roa (Return on assets)
  - tobins_q (Tobin's Q)
  - cash_holdings (Cash-to-assets ratio)
  - leverage (Debt-to-assets ratio)

### H4 (Leverage Discipline)
- Added Control Variables section with 9 control variables:
  - analyst_qa_uncertainty (Analyst Q&A uncertainty)
  - firm_size (Log total assets)
  - tobins_q (Tobin's Q)
  - roa (Return on assets)
  - cash_holdings (Cash-to-assets ratio)
  - dividend_payer (Dividend payer dummy)
  - firm_maturity (Firm age/lifecycle stage)
  - earnings_volatility (Earnings volatility)
  - leverage_lag1 (Lagged leverage - key IV)
  - presentation_uncertainty (Presentation uncertainty control for QA DVs)

### H5 (Analyst Dispersion)
- Added Control Variables section with 9 control variables:
  - prior_dispersion (Lagged analyst dispersion)
  - earnings_surprise (Earnings surprise)
  - analyst_coverage (Number of analysts, log-transformed)
  - loss_dummy (Negative earnings dummy)
  - firm_size (Log total assets)
  - leverage (Debt-to-assets ratio)
  - earnings_volatility (Earnings volatility)
  - tobins_q (Tobin's Q)
  - manager_qa_uncertainty_pct (General uncertainty control)
  - manager_pres_uncertainty_pct (Prepared speech control)
- Added Robustness Controls section documenting alternative specifications:
  - no_lagged_dv (excludes prior_dispersion)
  - no_numest (excludes analyst_coverage)
  - ceo_only (CEO-specific measures)

### H6 (SEC Scrutiny/CCCL)
- Added Control Variables section documenting the shift-share instrument:
  - Primary instrument: shift_intensity_mkvalt_ff48_lag (FF48 × market value, lagged)
  - 6 CCCL instrument variants for robustness (FF48/FF12/SIC2 × market value/sales)
  - Note: H6 uses 2SLS with shift-share instrument, no additional control variables in primary specification

### H7 (Stock Illiquidity)
- Added Control Variables section with 2 control variables:
  - Volatility (Stock return volatility, annualized)
  - StockRet (Annual stock return)
- Added Alternative Dependent Variables (Robustness):
  - Roll (1984) spread (implicit bid-ask spread)
  - Log Amihud (Log-transformed illiquidity)
- Added Alternative Independent Variables (Robustness):
  - CEO only (CEO_QA_Uncertainty_pct, CEO_Pres_Uncertainty_pct)
  - Presentation only (Manager_Pres_Uncertainty_pct, CEO_Pres_Uncertainty_pct)
  - QA only (Manager_QA_Uncertainty_pct, CEO_QA_Uncertainty_pct)

### H8 (PRisk × CEO Style → Abnormal Investment)
- Added Control Variables section with 6 control variables:
  - ln_at_t (Log total assets - Firm size)
  - lev_t (Debt-to-assets ratio - Leverage)
  - cash_t (Cash-to-assets ratio - Financial slack)
  - roa_t (Return on assets - Profitability)
  - mb_t (Book-to-market ratio - Investment opportunities)
  - SalesGrowth_t (Sales growth - Growth prospects)
- Added Variable Construction Notes explaining:
  - AbsAbInv DV construction (Biddle residual)
  - PRiskFY construction (Hassan index, 366-day window)
  - StyleFrozen construction (frozen constraint, no look-ahead bias)
  - Note: This hypothesis was H9 in pipeline, documented as H8 for consistency

## Files Modified

**Round 1 - Control Variables Descriptions:**
- `4_Outputs/4_Econometric_V2/H1_Hypothesis_Documentation.md`
- `4_Outputs/4_Econometric_V2/H2_Hypothesis_Documentation.md`
- `4_Outputs/4_Econometric_V2/H3_Hypothesis_Documentation.md`
- `4_Outputs/4_Econometric_V2/H4_Hypothesis_Documentation.md`
- `4_Outputs/4_Econometric_V2/H5_Hypothesis_Documentation.md`
- `4_Outputs/4_Econometric_V2/H6_Hypothesis_Documentation.md`
- `4_Outputs/4_Econometric_V2/H7_Hypothesis_Documentation.md`
- `4_Outputs/4_Econometric_V2/H8_Hypothesis_Documentation.md`

**Round 2 - Control Variable Coefficient Results:**
- `4_Outputs/4_Econometric_V2/H1_Hypothesis_Documentation.md`
- `4_Outputs/4_Econometric_V2/H2_Hypothesis_Documentation.md`
- `4_Outputs/4_Econometric_V2/H3_Hypothesis_Documentation.md`
- `4_Outputs/4_Econometric_V2/H4_Hypothesis_Documentation.md`
- `4_Outputs/4_Econometric_V2/H5_Hypothesis_Documentation.md`
- `4_Outputs/4_Econometric_V2/H6_Hypothesis_Documentation.md`
- `4_Outputs/4_Econometric_V2/H7_Hypothesis_Documentation.md`
- `4_Outputs/4_Econometric_V2/H8_Hypothesis_Documentation.md`

## Git Commit

Commit: `c70147e`
Message: `docs(hypothesis): add control variables to H1-H8 documentation`

## Notes

All control variables are consistently:
- Winsorized at 1%/99%
- Lagged appropriately for causal identification
- Sourced from Compustat, CRSP, IBES, or Phase 4 outputs as appropriate
