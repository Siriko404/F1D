# Phase 40: H5 Speech Uncertainty Predicts Financial Outcome Uncertainty - Context

**Gathered:** 2026-02-05
**Status:** DRAFT - Discussion In Progress

<domain>
## Phase Boundary

Test whether managerial speech uncertainty predicts analyst forecast dispersion (disagreement). 
This tests the "variance-to-variance" relationship: Vague speech (Variance in signal) → Analyst Disagreement (Variance in belief).

**Primary Hypothesis (H5-A):** Higher speech uncertainty in Q&A predicts higher analyst forecast dispersion in the *next* quarter.
**Secondary Hypothesis (H5-B):** The gap between spontaneous (Q&A) and scripted (Presentation) uncertainty adds incremental predictive power.

</domain>

<decisions>
## Implementation Decisions

### Dependent Variable: Analyst Forecast Dispersion
- **Metric:** `STDEV / |MEANEST|` (Coefficient of Variation)
- **Target Period:** Next fiscal quarter (t+1). Speech at Q_t earnings call predicts dispersion of forecasts for Q_{t+1}.
- **Filtering:** 
  - `NUMEST` ≥ 3 (standard literature threshold to reduce noise)
  - `|MEANEST|` ≥ 0.05 (to prevent explosion of the ratio)
- **Winsorization:** 1% / 99% to handle extreme outliers.

### Independent Variables (The "Uncertainty" Measures)
- **Primary Measures:**
  1. `Manager_QA_Uncertainty_pct` (Spontaneous, comprehensive)
  2. `Manager_QA_Weak_Modal_pct` (Novel measure: hedging verbs like may/might/could)
- **Robustness Measures (Appendix):**
  - `CEO_QA_Uncertainty_pct` (CEO specific)
  - `CEO_Pres_Uncertainty_pct` (Scripted baseline)
- **Novel "Gap" Variable (H5-B):**
  - `Uncertainty_Gap = Manager_QA_Uncertainty_pct - Manager_Pres_Uncertainty_pct`
  - Gap > 0 implies spontaneous uncertainty revealed real risk hidden in script.

### Study Design
- **Unit of Analysis:** Firm-Quarter
- **Timing:** Lead-Lag (Speech_t predicts Dispersion_{t+1})
- **Sample:** Intersection of IBES, Compustat, and Transcripts (2002-2018)

### Pending Decisions (To Be Resumed)
- **Control Variables:**
  - *Current Status:* Analyzing Diether, Malloy & Scherbina (2002) controls.
  - *Candidates:* Size (log ME), Book-to-Market, Momentum, Turnover (Volume), Earnings Surprise, Prior Dispersion.
  - *Decision Needed:* Final parsimonious list that ensures causality without over-controlling.
- **Econometric Specification:**
  - *Decision Needed:* Panel FE (Firm+Year) vs Fama-MacBeth (standard in asset pricing). Given our project uses Panel FE for H1-H3, likely stick to Panel FE for consistency, but need to confirm.

</decisions>

<specifics>
## Specific Ideas

- "Go for the win" — focus on the hypothesis with highest probability of significance (Dispersion).
- "Weak Modal" is a key novel contribution — distinct from just replicating Loughran/McDonald.
- Q&A vs Presentation Gap is the secondary "novel" angle.

</specifics>

<deferred>
## Deferred Ideas

- Shannon Entropy of word distribution (Novel, theoretically sound, but higher effort/risk. Deferred to future exploratory work if primary H5 fails).
- Stock Return Volatility (Established literature, less novel. Backup if Dispersion fails).

</deferred>

---

*Phase: 40-h5-speech-uncertainty-predicts-financial-outcome-uncertainty*
*Context gathered: 2026-02-05*
