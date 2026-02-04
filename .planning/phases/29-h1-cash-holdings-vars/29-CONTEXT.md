# Phase 29: H1 Cash Holdings Variables - Context

**Gathered:** 2026-02-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Construct all dependent, moderator, and control variables for H1 (Cash Holdings) hypothesis. Output is a single dataset with computed variables ready for Phase 33 regression.

**Variable scope:**
- Dependent: Cash Holdings (CHE/AT)
- Moderator: Leverage ((DLTT+DLC)/AT)
- Control: Operating Cash Flow Volatility (5-year trailing StdDev of OANCF/AT)
- Controls: Current Ratio (ACT/LCT), Tobin's Q, ROA, Capex/AT, Dividend Payer, Firm Size

**Input:** Existing Compustat data from Step 3 (already merged with sample)
**Output:** `4_Outputs/3_Financial_V2/2.1_H1Variables.parquet` with accompanying stats.json

</domain>

<decisions>
## Implementation Decisions

### Variable Definitions
No special requirements — follow standard Compustat field formulas as specified in ROADMAP.md:
- Cash Holdings = CHE / AT
- Leverage = (DLTT + DLC) / AT
- Cash Flow Volatility = StdDev of (OANCF / AT) over trailing 5 fiscal years
- Current Ratio = ACT / LCT
- Tobin's Q = (AT + Market Equity - CEQ) / AT
- ROA = NI / AT
- Capex = CAPX / AT
- Dividend Payer = indicator(DVC > 0)
- Firm Size = log(AT)

### Data Treatment
**OpenCode's Discretion** — Researcher/planner should propose standard approaches:
- Missing Compustat field handling (drop obs vs require complete data)
- Outlier winsorization (typical: 1st/99th percentile)
- Minimum observations for volatility calculation (typical: 3+ years of data)
- Fiscal year alignment for trailing windows

</decisions>

<specifics>
## Specific Ideas

No specific requirements — open to standard econometric approaches.

Key reference for reviewer: H1-01 through H1-05 requirements define exact specifications.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 29-h1-cash-holdings-vars*
*Context gathered: 2026-02-04*
