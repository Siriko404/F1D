# Phase 30: H2 Investment Efficiency Variables - Context

**Gathered:** 2026-02-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Construct all dependent and control variables for H2 (Investment Efficiency) hypothesis testing. This includes:
- Overinvestment Dummy (Capex/Depreciation > 1.5 AND Sales Growth < industry-year median)
- Underinvestment Dummy (Capex/Depreciation < 0.75 AND Tobin's Q > 1.5)
- Efficiency Score DV (1 - % inefficient years over 5-year window)
- Alternative DV: ROA Residual per Biddle et al. (2009) methodology
- Controls: Tobin's Q, Cash Flow Volatility, Industry CapEx Intensity, Analyst Dispersion, Firm Size, ROA, FCF, Earnings Volatility

Output: `4_Outputs/3_Financial_V2/{timestamp}/H2_InvestmentEfficiency.parquet` with `stats.json`

</domain>

<decisions>
## Implementation Decisions

### FF48 Industry Classification
- Build SIC-to-FF48 mapping from `1_Inputs/Siccodes48.txt`
- Firms with missing/invalid SIC codes assigned to "Other" (FF48 #48)
- Industry-year medians require minimum 5 firms per FF48-year cell
- If FF48 cell is thin (< 5 firms), fall back to FF12 industry classification
- Also build FF12 mapping from `1_Inputs/Siccodes12.zip` for fallback

### 5-Year Efficiency Window
- Use trailing 5-year window (t-4 to t, inclusive of current year)
- Require minimum 3 years of valid data in the window
- Efficiency Score = 1 - (# inefficient years / # years in window)
- Over/underinvestment flags are mutually exclusive per year (cannot be both)

### Biddle ROA Residual Methodology
- Run industry-year cross-sectional regressions (one OLS per FF48-year cell)
- Dependent variable: Delta-ROA = ROA(t+2) - ROA(t)
- Regressors: Capex/AT, Tobin's Q, Cash Holdings, Leverage (as per README)
- Minimum 20 firms required per FF48-year regression
- If FF48 cell has < 20 firms, fall back to FF12 grouping for regression
- Residual = actual Delta-ROA minus predicted Delta-ROA
- Positive residual = efficient investment; negative = inefficient

### IBES Analyst Dispersion
- Formula: Analyst_Dispersion = STDEV / |MEANEST| (coefficient of variation)
- Require minimum 2 analysts (NUMEST >= 2) for meaningful dispersion
- Firms not in IBES: mark dispersion as missing (NA)
- Near-zero mean (|MEANEST| < 0.01): mark dispersion as missing to avoid extreme CV
- Match IBES to Compustat via CUSIP or ticker-based linking

### OpenCode's Discretion
- Exact implementation of SIC-to-FF48 parsing logic
- IBES-to-Compustat linking methodology (CUSIP vs ticker)
- Winsorization levels (1%/99% consistent with H1)
- Variable naming conventions (follow H1 pattern)
- Error handling for edge cases

</decisions>

<specifics>
## Specific Ideas

- Follow the `3.1_H1Variables.py` script pattern for consistency (PyArrow schema inspection, DualWriter logging, stats.json output)
- README in `2_Scripts/3_Financial_V2/` already documents the exact formulas and Compustat fields
- Use `get_latest_output_dir()` pattern for reading prerequisite outputs
- Sort final output by gvkey + fiscal_year for determinism

</specifics>

<deferred>
## Deferred Ideas

None - discussion stayed within phase scope

</deferred>

---

*Phase: 30-h2-investment-efficiency*
*Context gathered: 2026-02-05*
