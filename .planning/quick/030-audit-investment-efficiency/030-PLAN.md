---
phase: 030-audit-investment-efficiency
plan: 030
type: execute
wave: 1
depends_on: []
files_modified: []
autonomous: true

must_haves:
  truths:
    - "Investment variable formula matches Biddle (2009) specification exactly"
    - "First-stage regression uses correct predictors (TobinQ_lag, SalesGrowth_lag)"
    - "Industry-year regressions enforce minimum 20 observations per cell"
    - "Winsorization thresholds are 1%/99% by year"
    - "Output variables have correct names and data types"
    - "Regression script uses InvestmentResidual as dependent variable correctly"
  artifacts:
    - path: "2_Scripts/3_Financial_V3/4.1_H2_BiddleInvestmentResidual.py"
      provides: "Investment residual construction"
      contains: "construct_investment", "run_first_stage_regressions"
    - path: "INVESTMENT_EFFICIENCY_METHODOLOGY.md"
      provides: "Biddle (2009) methodology specification"
      contains: "Investment", "SalesGrowth", "first-stage", "winsorize"
    - path: "2_Scripts/4_Econometric_V3/4.3_H2_PRiskUncertainty_Investment.py"
      provides: "H2 regression using InvestmentResidual"
      contains: "InvestmentResidual", "PRIMARY_SPEC"
  key_links:
    - from: "4.1_H2_BiddleInvestmentResidual.py"
      to: "INVESTMENT_EFFICIENCY_METHODOLOGY.md"
      via: "Variable construction formulas"
      pattern: "construct_investment.*capx.*xrd.*aqc.*sppe"
    - from: "4.1_H2_BiddleInvestmentResidual.py"
      to: "run_first_stage_regressions"
      via: "Industry-year OLS regression call"
      pattern: "groupby.*ff48_code.*fyear"
    - from: "4.3_H2_PRiskUncertainty_Investment.py"
      to: "InvestmentResidual"
      via: "Dependent variable usage"
      pattern: "'dependent': 'InvestmentResidual'"
---

<objective>
Audit the Phase 53 investment efficiency implementation (Biddle 2009) against the methodology specification to verify 100% implementation integrity.

Purpose: Ensure the H2 hypothesis test (PRisk x Uncertainty -> Investment Efficiency) uses the correctly constructed investment residual per Biddle et al. (2009), with no deviations from the specification that could invalidate results.

Output: Audit report documenting any deviations, missing elements, or inconsistencies between methodology and implementation.
</objective>

<execution_context>
@C:\Users\sinas\.claude\get-shit-done\workflows\execute-plan.md
@C:\Users\sinas\.claude\get-shit-done\templates\summary.md
</execution_context>

<context>
@.planning/INVESTMENT_EFFICIENCY_METHODOLOGY.md
@.planning/phases/53-h2-prisk-uncertainty-investment/53-RESEARCH.md
@2_Scripts/3_Financial_V3/4.1_H2_BiddleInvestmentResidual.py
@2_Scripts/4_Econometric_V3/4.3_H2_PRiskUncertainty_Investment.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Audit Investment Variable Construction Formula</name>
  <files>2_Scripts/3_Financial_V3/4.1_H2_BiddleInvestmentResidual.py</files>
  <action>
    Compare the Investment variable construction in 4.1_H2_BiddleInvestmentResidual.py against the methodology specification:

    **Methodology Specification (INVESTMENT_EFFICIENCY_METHODOLOGY.md):**
    - Investment_{t+1} = 100 * (XRD_{t+1} + CAPX_{t+1} + AQC_{t+1} - SPPE_{t+1}) / AT_{t}
    - Use lagged total assets (AT_t) in denominator
    - Compustat items: XRD (46), CAPX (128), AQC (129), SPPE (107), AT (6)

    **Implementation to Verify:**
    - Locate construct_investment() function (lines ~290-346)
    - Verify formula: investment_components = capx + xrd + aqc - sppe
    - Verify denominator: at_lag (lagged assets via groupby().shift(1))
    - Verify scaling: Is 100x scaling applied or omitted consistently?
    - Verify handling of missing components (AQC, SPPE) - should use simplified measure if missing
    - Verify positive assets filter applied before computation

    **Audit Checklist:**
    - [ ] Numerator includes: CapEx + R&D + Acquisitions - AssetSales
    - [ ] Denominator is lagged total assets (AT_{t-1})
    - [ ] Scaling factor (100x) either applied consistently or omitted with documentation
    - [ ] Missing AQC/SPPE handled gracefully (simplified measure)
    - [ ] Positive assets filter applied
  </action>
  <verify>Search for "def construct_investment" and verify formula components match specification exactly</verify>
  <done>Investment variable formula is verified to match Biddle (2009) specification with documented handling of missing components</done>
</task>

<task type="auto">
  <name>Task 2: Audit First-Stage Regression Specification</name>
  <files>2_Scripts/3_Financial_V3/4.1_H2_BiddleInvestmentResidual.py</files>
  <action>
    Compare the first-stage regression specification against the methodology:

    **Methodology Specification:**
    - For each industry-year (FF48) with >= 20 observations:
    - Investment_{i,t+1} = b_0 + b_1 * SalesGrowth_{i,t} + epsilon_{i,t+1}
    - NOTE: Methodology shows SalesGrowth only, but RESEARCH.md specifies TobinQ_lag + SalesGrowth_lag

    **Implementation to Verify:**
    - Locate run_first_stage_regressions() function (lines ~509-632)
    - Verify grouping: ff48_code and fyear (not ff48 and year)
    - Verify minimum observation threshold: min_obs parameter (default 20)
    - Verify regression predictors: X should contain [TobinQ_lag, SalesGrowth_lag]
    - Verify OLS execution: sm.OLS(Y, X).fit()
    - Verify residual computation: residuals = Y - predicted
    - Verify handling of thin cells (< min_obs): should skip, not merge

    **Key Decision Check:**
    - Methodology document specifies SalesGrowth only
    - Research document (53-RESEARCH.md) specifies TobinQ_lag + SalesGrowth_lag
    - Implementation should follow RESEARCH.md (more complete specification)
    - Document any deviation as intentional or requires correction

    **Audit Checklist:**
    - [ ] Grouping by FF48 industry-year (ff48_code, fyear)
    - [ ] Minimum 20 observations enforced
    - [ ] Predictors: TobinQ_lag + SalesGrowth_lag (per RESEARCH.md)
    - [ ] OLS regression with constant term
    - [ ] Residuals computed correctly (actual - fitted)
    - [ ] Thin cells skipped (not merged or extrapolated)
  </action>
  <verify>Search for "run_first_stage_regressions" and verify regression model matches RESEARCH.md specification</verify>
  <done>First-stage regression specification verified: FF48-year grouping, min_obs=20, TobinQ_lag + SalesGrowth_lag predictors</done>
</task>

<task type="auto">
  <name>Task 3: Audit Winsorization, Sample Construction, and Regression Usage</name>
  <files>2_Scripts/3_Financial_V3/4.1_H2_BiddleInvestmentResidual.py, 2_Scripts/4_Econometric_V3/4.3_H2_PRiskUncertainty_Investment.py</files>
  <action>
    Verify additional implementation details:

    **Part A: Winsorization (Methodology: 1%/99% by year)**
    - Locate winsorization in construct_investment(), construct_tobins_q(), construct_sales_growth(), construct_biddle_controls()
    - Verify threshold: .quantile(0.01) and .quantile(0.99)
    - Verify grouping: by fyear for year-specific winsorization
    - Check if InvestmentResidual itself is winsorized (should NOT be - defeats OLS property)

    **Part B: Sample Construction**
    - Verify financial firms excluded (SIC 6000-6999) - should be in merge script or here
    - Verify utilities excluded (SIC 4900-4999) - should be in merge script or here
    - Verify positive assets required (df[df["at"] > 0])
    - Verify deduplication: quarterly to annual (keep='last' on gvkey-fyear)

    **Part C: Regression Usage**
    - Locate 4.3_H2_PRiskUncertainty_Investment.py PRIMARY_SPEC
    - Verify dependent variable: 'InvestmentResidual' (signed residual)
    - Verify controls: CashFlow, Size, Leverage, TobinQ, SalesGrowth
    - Verify interaction term: PRisk_x_Uncertainty (standardized)
    - Verify fixed effects: Firm + Year FE
    - Verify clustering: Double-clustered (firm, year)

    **Audit Checklist:**
    - [ ] Winsorization at 1%/99% by year applied to inputs, NOT residuals
    - [ ] Sample filters applied (financial/utilities excluded, positive assets)
    - [ ] Deduplication correct (quarterly -> annual, keep last)
    - [ ] Regression uses InvestmentResidual as DV (not absolute value in primary spec)
    - [ ] Controls match Biddle (2009) baseline
    - [ ] Clustering and FE match research specification
  </action>
  <verify>Search for "winsorize", "clip", "quantile" to verify thresholds; check PRIMARY_SPEC in regression script</verify>
  <done>Winsorization, sample construction, and regression usage all verified against methodology and research specifications</done>
</task>

</tasks>

<verification>
After completing all tasks, create an audit report with:
- Summary of audit findings (PASS/FAIL/PARTIAL for each dimension)
- List of any deviations discovered with severity (CRITICAL/MAJOR/MINOR)
- Recommendation on whether results are valid or require re-implementation
- If deviations found: specific line numbers and suggested corrections
</verification>

<success_criteria>
Audit is complete when:
- [ ] Investment variable formula compared line-by-line with methodology
- [ ] First-stage regression specification verified
- [ ] Winsorization thresholds and grouping verified
- [ ] Sample construction filters verified
- [ ] Regression usage (DV, controls, FE, clustering) verified
- [ ] Audit report created with clear PASS/FAIL determination
</success_criteria>

<output>
After completion, create `.planning/quick/030-audit-investment-efficiency/030-AUDIT-REPORT.md`
</output>
