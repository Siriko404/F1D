# Phase 42: H6 SEC Scrutiny (CCCL) Reduces Manager Speech Uncertainty - Context

**Gathered:** 2026-02-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Test whether SEC scrutiny through Conference Call Comment Letters (CCCL) causes managers to speak with less uncertainty. Uses shift-share identification design: firm-level CCCL exposure = Industry CCCL Intensity × Firm Size Share.

**Primary Hypothesis (H6-A):** Higher CCCL exposure predicts lower managerial speech uncertainty in subsequent periods.

**Secondary Hypothesis (H6-B):** CCCL exposure has stronger effects on spontaneous Q&A speech than on scripted Presentation remarks.

**Tertiary Hypothesis (H6-C):** CCCL exposure reduces the Q&A-Presentation uncertainty gap (makes disclosure more consistent).

</domain>

<decisions>
## Implementation Decisions

### Shift-Share Construction

**Primary Instrument:**
- Use all 6 pre-computed variants from `instrument_shift_intensity_2005_2022.parquet`
- **Primary:** `shift_intensity_mkvalt_ff48` (FF48 industry × market value)
- **Robustness:** FF48/Sales, FF12/Market Value, FF12/Sales, SIC2/Market Value, SIC2/Sales

**Treatment Functional Form:**
- **Primary:** Continuous (0-1 normalized)
- **Robustness:** Quartiles (tests for non-linearity, threshold effects)

**Treatment Timing:**
- **Primary:** Lagged (t-1 predicts t) — CCCL exposure at t-1 predicts speech uncertainty at t
- **Rationale:** Avoids reverse causality (CCCLs respond to past speech, not future)
- **Robustness:** Contemporaneous specification to test immediate effects

**Fixed Effects Strategy:**
- **Primary:** Firm FE + Year FE
- **NO Industry × Year FE** — Would absorb the shift-share treatment variation
- **Robustness:** Industry FE + Year FE (cross-industry variation instead of within-firm)

### Timing and Treatment Granularity

**Data Aggregation:**
- **Primary:** Quarterly aggregation of speech measures
- **Rationale:** 4x sample size vs annual, allows quarter FE for seasonality
- **Standard Errors:** Cluster at firm-year level (accounts for 4 quarters sharing same CCCL exposure)

**Fiscal/Calendar Alignment:**
- Use calendar year as proxy for fiscal year (consistent with H1-H5 convention)
- **Rationale:** 96% of observations unaffected; CCCL instrument already fiscal-year based

**Multiple Calls Per Quarter:**
- **Approach:** Mean aggregation (consistent with H5 implementation)
- **Incidence:** Only 3.7% of firm-quarters have multiple calls
- **Rationale:** Represents "average communication style" for the quarter

**Identification Strategy:**
- **Primary:** Cross-sectional treatment intensity with Firm FE + Year FE
- **Interpretation:** Within-firm changes in CCCL exposure predict within-firm changes in speech uncertainty
- **Robustness:** Event study with leads/lags to test for pre-trends

### Control Strategy

**Primary Specification (Minimal):**
- Firm Fixed Effects (absorbs time-invariant firm traits)
- Year Fixed Effects (absorbs macro shocks)
- NO additional time-varying controls

**Rationale for minimal controls:**
- Firm size is PART of the treatment (shift-share construction)
- Leverage may be a mediator, not just confounder
- Within-firm identification addresses most endogeneity concerns

**Robustness Controls (test and report):**
1. **Firm-specific linear trends:** For firms with >= 10 years (tests dynamic selection)
2. **Time-varying firm controls:** Size, leverage, ROA (addresses obvious confounders)
3. **Lagged DV:** Level vs. change specification (addresses Nickell bias, serial correlation)

**Literature-Based Controls (when testing Q&A effects):**
- **Presentation uncertainty:** Control for Manager_Pres_Uncertainty_pct (per vague talkers literature)
- **Analyst uncertainty:** Control for Analyst_QA_Uncertainty_pct (per Price et al. 2012)
- **Rationale:** Isolates Q&A-specific effect from scripted and analyst-driven variation

### Speech Uncertainty DV Selection

**Primary Dependent Variables (6-measure suite):**

| Priority | Measure | Type | Rationale |
|----------|---------|------|-----------|
| **Primary** | Manager_QA_Uncertainty_pct | General uncertainty in Q&A | Broadest, most established in literature, best sample coverage |
| **Secondary** | Manager_QA_Weak_Modal_pct | Hedging verbs in Q&A | Strategic hedging, voluntary uncertainty |
| **Robustness** | CEO_QA_Uncertainty_pct | CEO-only general uncertainty | Tests if scrutiny targets top executives |
| **Robustness** | CEO_QA_Weak_Modal_pct | CEO-only hedging | CEO-specific strategic response |
| **Robustness** | Manager_Pres_Uncertainty_pct | General uncertainty in Presentation | Tests if scrutiny affects scripted remarks |
| **Robustness** | CEO_Pres_Uncertainty_pct | CEO-only Presentation uncertainty | CEO-specific scripted effects |

**Additional Tests:**
- **Uncertainty_Gap:** Manager_QA_Uncertainty_pct - Manager_Pres_Uncertainty_pct
- **Interpretation:** Does scrutiny make disclosure more consistent across prepared/spontaneous speech?

**Multiple Testing Correction:**
- Apply False Discovery Rate (FDR) correction (Benjamini-Hochberg) across 6 measures
- Report both raw and FDR-adjusted p-values
- Significance determined by FDR-corrected thresholds

**Sample Coverage Considerations:**
- Manager measures: ~27,500 observations
- CEO measures: ~20,000 observations (27% missing due to CEO identification)
- Primary analysis uses Manager measures for power; CEO measures as robustness

</decisions>

<specifics>
## Specific Ideas

**Expected Results Pattern:**
- Strongest effects in Q&A (spontaneous speech)
- Weaker/null effects in Presentation (scripted, already vetted)
- CEO measures may show stronger effects if scrutiny targets leadership
- Gap reduction indicates improved disclosure consistency

**Mechanism Interpretation:**
- Negative β on general uncertainty: Scrutiny disciplines vague language
- Negative β on weak modals: Scrutiny reduces strategic hedging
- Negative β on gap: Scrutiny makes prepared/spontaneous speech more consistent

**Comparison to H1-H3:**
- H1-H3 tested speech → financial outcomes (null results)
- H6 tests external shock → speech (shift-share identification)
- Different mechanism may yield different results despite nulls before

**Identification Validation:**
- Pre-trends analysis crucial: Were high-exposure firms already on uncertainty trajectories?
- If leads (t-2, t-1) are significant → dynamic selection threat
- If only contemporaneous/lagged significant → supports causal interpretation

</specifics>

<deferred>
## Deferred Ideas

**Future Phase Candidates:**

1. **Shannon Entropy of Word Distribution:** Information-theoretic measure of disclosure quality. Theoretically sound but requires new computation; defer to exploratory work.

2. **Stock Return Volatility as Alternative DV:** Established in literature but less novel than speech uncertainty. Consider if speech analysis shows null results.

3. **Bid-Ask Spread as DV:** Microstructure measure of information asymmetry. Requires TAQ data not currently available.

4. **Analyst Forecast Accuracy as DV:** Different mechanism (precision vs. disagreement). Consider for future phase on information environment.

5. **Cross-Sectional Heterogeneity:** Test if CCCL effects vary by firm characteristics (size, complexity, litigation risk). Interesting but adds complexity; defer to robustness phase.

**None of these deferred ideas belong in Phase 42 scope.**

</deferred>

<design_summary>
## Design Summary for Planning

### Data Sources
- **Treatment:** `1_Inputs/CCCL instrument/instrument_shift_intensity_2005_2022.parquet` (145K firm-years)
- **Outcome:** `4_Outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_*.parquet` (2002-2018)
- **Merge Key:** gvkey + fiscal_year + fiscal_quarter

### Sample Construction
- **Overlap Period:** 2005-2018 (CCCL starts 2005, speech available through 2018)
- **Aggregation:** Quarterly speech measures; annual CCCL mapped to all 4 quarters
- **Coverage:** ~18K firms, ~200-400K firm-quarter observations expected

### Primary Regression Specification
```
Speech_Uncertainty_iqt = β × CCCL_Exposure_i,t-1 
                        + γ × Pres_Uncertainty_iqt      [when testing Q&A]
                        + δ × Analyst_Uncertainty_iqt   [when testing Q&A]
                        + Firm_FE_i + Year_FE_t + ε_iqt

Cluster SE at firm-year level
```

### Expected Outputs
1. **Primary results table:** 6 uncertainty measures × FDR-corrected significance
2. **Robustness tables:** Alternative FE, controls, lagged DV, firm trends
3. **Pre-trends test:** Leads of CCCL exposure
4. **Gap analysis:** Uncertainty_Gap as outcome
5. **stats.json:** Full regression outputs, diagnostics, sample characteristics

### Success Criteria
- At least 1/6 measures significant after FDR correction (primary hypothesis supported)
- Q&A effects stronger than Presentation effects (mechanism validated)
- No significant pre-trends (identification credible)

</design_summary>

---

*Phase: 42-h6-sec-scrutiny-cccl-reduces-manager-speech-uncertainty*
*Context gathered: 2026-02-05*
