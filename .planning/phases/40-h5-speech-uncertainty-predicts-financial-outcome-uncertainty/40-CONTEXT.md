# Phase 40: H5 Speech Uncertainty Predicts Analyst Forecast Dispersion - Context

**Gathered:** 2026-02-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Test whether managerial hedging language (weak modal verbs) predicts analyst forecast dispersion beyond what general uncertainty words predict. This is a variance-to-variance relationship: Vague speech → Analyst Disagreement.

**Primary Hypothesis (H5-A):** Hedging language (weak modal verbs: may, might, could) in Q&A predicts higher analyst forecast dispersion in the next quarter, even after controlling for general uncertainty words.

**Secondary Hypothesis (H5-B):** The gap between spontaneous (Q&A) and scripted (Presentation) uncertainty has incremental predictive power beyond the level of scripted uncertainty.

**Literature Position:**
- General uncertainty → dispersion is ESTABLISHED (Loughran & McDonald 2011, Price et al. 2012)
- Our contribution: Does **hedging language** (weak modals) add beyond general uncertainty?
- Secondary contribution: Does **spontaneous-scripted gap** reveal hidden uncertainty?

</domain>

<decisions>
## Implementation Decisions

### Dependent Variable: Analyst Forecast Dispersion
- **Metric:** `STDEV / |MEANEST|` (Coefficient of Variation)
- **Target Period:** Next fiscal quarter (t+1). Speech at Q_t earnings call predicts dispersion of forecasts for Q_{t+1}.
- **Filtering:** 
  - `NUMEST` ≥ 3 (standard literature threshold; STDEV with 2 analysts is just range/√2)
  - `|MEANEST|` ≥ 0.05 (prevents ratio explosion when consensus near zero)
- **Winsorization:** 1% / 99% to handle extreme outliers

### Independent Variables (Revised After Red-Team)

**Primary IV (Novel):**
- `Manager_QA_Weak_Modal_pct` — Hedging verbs (may/might/could). LM separates these from uncertainty words. Rarely tested directly as primary IV.

**Control for Established Effect:**
- `Manager_QA_Uncertainty_pct` — General uncertainty words. Including this as CONTROL ensures Weak Modal effect is INCREMENTAL.

**Secondary IV (H5-B Gap Analysis):**
- `Uncertainty_Gap = Manager_QA_Uncertainty_pct - Manager_Pres_Uncertainty_pct`
- Gap > 0: Manager more uncertain in spontaneous speech (revealing hidden risk)
- Gap < 0: Manager more uncertain in prepared remarks (deliberate signaling)
- Include `Manager_Pres_Uncertainty_pct` as control to isolate the gap effect

**Robustness IVs:**
- `CEO_QA_Weak_Modal_pct` (CEO-specific hedging)
- `CEO_QA_Uncertainty_pct` (CEO-specific uncertainty)
- Presentation-only variants (should show weaker effects, confirming Q&A more informative)

### Control Variables (Post Red-Team Analysis)

| Control | Include | Rationale |
|---------|---------|-----------|
| `Prior_Dispersion` (lagged DV) | ✅ | Dispersion is highly persistent (~0.6-0.8 autocorrelation). Essential for causal interpretation. |
| `Earnings_Surprise` | ✅ | |actual - meanest| / |meanest|. Determined BEFORE speech, so confounder not mediator. |
| `Analyst_Coverage` (NUMEST) | ✅ | Standard control. Run robustness without it (potential "bad control"). |
| `Firm_Size` (log assets) | ✅ | Larger firms have more public info → lower dispersion. Standard. |
| `Earnings_Volatility` | ✅ | Volatile earnings harder to forecast. Key determinant (BKLS model). |
| `Loss_Dummy` | ✅ | NI < 0. Loss firms have fundamentally different dispersion dynamics. |
| `Tobins_Q` | ✅ | Growth opportunities affect forecast difficulty. |
| `Leverage` | ✅ | Already computed. Higher leverage → higher financial risk. |
| `Manager_QA_Uncertainty_pct` | ✅ | **Critical:** Control for established effect to show Weak Modal is incremental. |

**Excluded (with rationale):**
- `Book_to_Market`: Redundant with Tobin's Q (inverse relationship)
- `Momentum`: Not standard for dispersion-as-DV studies; requires CRSP merge
- `Cash_Holdings`: Not theoretically linked to dispersion; over-controlling risk
- `ROA`: Only include if VIF < 5; may be redundant with Loss_Dummy + Earnings_Volatility

### Econometric Specification

**Primary Model:**
```
Dispersion_{i,t+1} = β₁·Weak_Modal_QA_{i,t} 
                   + β₂·Uncertainty_QA_{i,t}      # Control for established effect
                   + β₃·Prior_Dispersion_{i,t}
                   + β₄·Earnings_Surprise_{i,t}
                   + β₅·Analyst_Coverage_{i,t}
                   + β₆·Firm_Size_{i,t}
                   + β₇·Earnings_Volatility_{i,t}
                   + β₈·Loss_Dummy_{i,t}
                   + β₉·Tobins_Q_{i,t}
                   + β₁₀·Leverage_{i,t}
                   + Firm_FE + Year_FE
                   + ε_{i,t+1}
```

**Gap Model (H5-B):**
```
Dispersion_{i,t+1} = β₁·Uncertainty_Gap_{i,t} 
                   + β₂·Manager_Pres_Uncertainty_{i,t}  # Control for base level
                   + β₃·Prior_Dispersion_{i,t}
                   + [Other Controls]
                   + Firm_FE + Year_FE
                   + ε_{i,t+1}
```

**Fixed Effects:** Firm + Year (consistent with H1-H4; absorbs time-invariant firm traits and market-wide shocks)

**Standard Errors:** Clustered at firm level (robust to within-firm autocorrelation)

**Expected Signs:**
- β₁ (Weak_Modal) > 0: More hedging → more dispersion
- β₂ (Uncertainty) > 0: Confirms established literature
- β₁ significant AFTER controlling for β₂: **Novel contribution**

### Robustness Checks Required

1. **Without lagged DV** — Eliminates Nickell bias concern (T=17 is borderline; bias ≈ 6%)
2. **Without NUMEST** — Eliminates "bad control" concern (coverage is endogenous)
3. **CEO-only measures** — Test if CEO vs Manager aggregation matters
4. **Presentation-only measures** — Confirm Q&A is more informative (Pres should be weaker)
5. **Double-clustering (Firm + Year)** — More conservative SEs
6. **Alternative dispersion scaling** — Scale by stock price if available (addresses |MEANEST| near zero concern differently)

### Interpretation Framework

| Result | Interpretation | Contribution |
|--------|----------------|--------------|
| β₁(Weak_Modal) sig, β₂(Uncertainty) sig | Hedging adds INCREMENTAL info beyond uncertainty | **Primary novel finding** |
| β₁(Weak_Modal) insig, β₂(Uncertainty) sig | Hedging doesn't add beyond uncertainty | Confirms LM distinction; still publishable |
| Both insignificant | Speech doesn't predict dispersion in our sample | Null finding (check specification) |
| Gap (β₁) sig in H5-B | Spontaneous-scripted difference reveals hidden info | **Secondary novel finding** |

### Data Requirements

**Already Available:**
- Speech measures: Manager_QA_Uncertainty_pct, Manager_QA_Weak_Modal_pct, Pres variants (from Step 2)
- Firm controls: firm_size, leverage, tobins_q, earnings_volatility (from H1-H3)
- Analyst dispersion: analyst_dispersion (from H2, but needs refinement with NUMEST ≥ 3)

**Need to Compute:**
- `Prior_Dispersion`: Lag analyst_dispersion by 1 quarter
- `Earnings_Surprise`: |actual - meanest| / |meanest| from IBES
- `Loss_Dummy`: 1 if NI < 0 from Compustat
- `Uncertainty_Gap`: Manager_QA_Uncertainty_pct - Manager_Pres_Uncertainty_pct

</decisions>

<specifics>
## Specific Ideas

- **Framing matters:** "Does hedging language predict analyst disagreement beyond general uncertainty?" — this is novel even though uncertainty → dispersion is established.
- **Weak Modal is the key differentiator** — LM explicitly separates these from uncertainty words; most studies use uncertainty, not weak modal.
- **Q&A vs Presentation gap** — Literature shows Q&A is more informative, but the GAP as IV is novel.
- **Interpretation if Weak Modal insignificant:** "Hedging verbs do not add information beyond uncertainty words for analyst forecasts" — still a contribution that clarifies the LM taxonomy.

</specifics>

<deferred>
## Deferred Ideas

- **Shannon Entropy of word distribution:** Theoretically sound (information theory), but requires new computation and may correlate highly with existing measures. Defer to future exploratory work.
- **Stock Return Volatility as DV:** Established in literature (less novel). Use as backup if dispersion analysis fails.
- **Bid-Ask Spread as DV:** Requires TAQ data not currently available.
- **Analyst Forecast Accuracy as DV:** Different mechanism (precision vs disagreement). Consider for future phase.

</deferred>

<red_team_notes>
## Red Team Assessment (2026-02-05)

### Addressed Concerns

1. **Novelty Concern:** General uncertainty → dispersion is established. Addressed by making Weak Modal primary IV and controlling for Uncertainty.

2. **Nickell Bias:** T=17 is borderline. Addressed by including robustness without lagged DV.

3. **Bad Control (NUMEST):** Analyst coverage is endogenous. Addressed by including robustness without it.

4. **Earnings Surprise Mediator Concern:** Resolved — surprise is determined BEFORE speech (it's the announced results), so it's a confounder, not mediator.

5. **Dispersion Scaling:** |MEANEST| ≥ 0.05 threshold addresses near-zero denominator concern.

### Remaining Risks

1. **Sample Size:** Intersection of IBES, Compustat, and Transcripts with NUMEST ≥ 3 may reduce sample significantly. Monitor N in results.

2. **Multicollinearity:** Weak_Modal and Uncertainty may be correlated. Check VIF; if VIF > 5, report models with each separately.

3. **Publication Bias:** If null on Weak Modal, frame as "hedging does not add beyond uncertainty" — still contributes.

</red_team_notes>

---

*Phase: 40-h5-speech-uncertainty-predicts-financial-outcome-uncertainty*
*Context gathered: 2026-02-05*
