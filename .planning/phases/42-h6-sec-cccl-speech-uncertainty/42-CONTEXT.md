# Phase 42: H6 SEC Scrutiny (CCCL) - Context

**Gathered:** 2026-02-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Test whether SEC scrutiny through Conference Call Comment Letters (CCCL) exposure causes managers to speak with less uncertainty. Uses a shift-share identification design where Industry CCCL Intensity × Firm Size Share predicts speech vagueness.

This reverses the typical "uncertainty is bad" framing — here scrutiny disciplines vague speech.

</domain>

<decisions>
## Implementation Decisions

### Exposure Construction (The "Treatment")
- **Primary Instrument:** `shift_intensity_mkvalt_ff48` from `1_Inputs/CCCL instrument/`
  - Logic: FF48 Industry Shift (CCCL Count) × Firm Share (Market Value)
  - Market value based share reflects regulatory visibility/importance better than sales
- **Alternative Instrument:** `shift_intensity_sale_ff48` (for robustness check)
- **Data Source:** Pre-calculated in `instrument_shift_intensity_2005_2022.parquet`

### Dependent Variable Scope
- **Primary Measures:**
  - `Manager_QA_Uncertainty_pct` (Spontaneous uncertainty)
  - `Manager_QA_Weak_Modal_pct` (Hedging/evasiveness - from H5)
- **Secondary Measures:**
  - `Manager_Pres_Uncertainty_pct` (Scripted uncertainty)
- **Speaker Role:** Manager Composite (CEO + CFO)

### Control Strategy
- **Fixed Effects:** Firm + Year
- **Standard Controls:** Size (Log Market Cap), ROA, Tobin's Q, Leverage, Loss Dummy, Earnings Volatility
- **Design-Specific Controls:**
  - Must control for the "Share" main effect (`share_lag_mkvalt_ff48`) to isolate the interaction
  - Control for `Analyst_Coverage` (Log NUMEST) as scrutiny can also come from analysts

### Timing & Lag Structure
- **Matching:** Match `year` in instrument file to `year` in speech file
- **Lag:** The instrument is already constructed using lagged values (`fyearq + 1` logic in reference), so concurrent matching represents $Scrutiny_{t-1} \rightarrow Speech_t$

### OpenCode's Discretion
- Exact output table formatting (LaTeX/JSON)
- Winsorization levels (default 1%/99% per standard)
- Handling of missing control variables (drop or impute)

</decisions>

<specifics>
## Specific Ideas

- "Reverses the typical framing" -> Expected Sign: Beta < 0 (More scrutiny = Less uncertainty)
- Use `linearmodels` for high-dimensional fixed effects (same as H1-H3)
- Check for "Spillover" effect: Does scrutiny on *peers* affect the firm? (The shift-share design implicitly captures this by using industry-level shift).

</specifics>

<deferred>
## Deferred Ideas

- Testing effect on positive/negative sentiment (Phase 43?)
- Textual similarity analysis between comment letters and transcripts
- Sentiment analysis of the comment letters themselves

</deferred>

---

*Phase: 42-h6-sec-cccl-speech-uncertainty*
*Context gathered: 2026-02-05*
