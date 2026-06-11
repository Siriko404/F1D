# Endogeneity Strategy Search — Research Brief

## 1. Paper context (brief)

Paper extends Dzielinski-Wagner-Zeckhauser (2021) three-component CEO speech-uncertainty decomposition to firm cash holdings. Headline construct: **UncResCEO** = residual from CEO fixed-effect regression on Q&A-segment uncertainty share (DWZ 2021 method). Headline finding: UncResCEO loads positively on cash-to-assets in 12 of 12 specifications at one-tailed p<0.10 (positive direction predicted by precautionary theory) under two construction methods (Full + QtrExp); two-tailed pass rate is 7/12 (Full) and 4/12 (QtrExp), with QtrExp signal concentrated in lead-DV cells. Our panel (2002–2018) extends DWZ 2021's original 2003–2015 window.

Theoretical claim: precautionary cash motive (OPSW 1999; Bates-Kahle-Stulz 2009). High CEO speech uncertainty → firm hoards cash as precaution.

## 2. THE endogeneity problem (the focus)

**Reverse-causality threat.** Cash hoarding may CAUSE CEO speech uncertainty rather than be caused by it. Multiple plausible reverse mechanisms exist; your task includes enumerating them comprehensively as Step 1 of your analysis.

**The bar.** Strategy must meet the standard finance-identification bar via modus tollens — empirical rejection of the reverse pattern + structural theoretical argument + corroborating heterogeneity tests. Dharmapala-Foley-Forbes (2011 JF) style. Random-assignment / RCT-style designs are not feasible in observational call-transcript data; they are out of scope.

**Strategy classes accepted (any of these):**
- (i) Instruments for speech uncertainty (first-stage on X, exclusion to outcome).
- (ii) Reverse-causality falsification — known cash shocks regressed on speech uncertainty, finding null effects.
- (iii) Modus-tollens heterogeneity tests — reverse story implies an empirical pattern that, if contradicted in data, falsifies it.

**Channel-isolation requirement (post-hoc property, not design property).** Each candidate strategy must be COMPATIBLE with a planned heterogeneity-test plan that, if confirmed, isolates the precautionary channel. Examples: effect concentrates in financially-constrained firms (Faulkender-Petersen 2006 binary rated/unrated), in high cash-flow-volatility firms (Han-Qiu 2007), in firms with limited credit-line access. Each candidate must propose 1–2 such heterogeneity tests as the channel-isolation step.

**What WON'T pass.**
- Designs that change CEO IDENTITY (turnover, sudden death, M&A-induced replacement) — they pool speech, strategy, risk-tolerance, and other CEO traits into one effect; channel mismatch.
- Designs whose significance kills only ONE specific reverse mechanism while leaving others alive — the strategy must rule out the dominant 2–3 mechanisms identified in your Step-1 enumeration.
- Designs that address only time-invariant firm traits — already absorbed by main-panel firm fixed effects.

## 3. Setup

- **Construction panel.** 2,429 US firms, 2002–2018, quarterly. ~112,968 firm-quarter observations (start_date 2002-01-16 to 2018-12-22, calendar dates).
- **Operative regression sample.** After Bates-Kahle-Stulz 2009 sector exclusions, lagged-DV requirement, and firm-FE singleton drops: **n ≈ 43,333 firm-quarter observations across 1,376 firms** (or n ≈ 41,108 / 1,321 in lead-DV specifications). Calibrate feasibility judgments to the operative sample, not the construction panel.
- **Y.** Cash-to-assets ratio (Bates-Kahle-Stulz 2009 form: `cheq/atq`).
- **X (headline IV).** UncResCEO — residual from CEO fixed-effect regression on Q&A-segment speech uncertainty share (DWZ 2021 method).
- **Other speech components.** ClarityCEO (negative CEO fixed effect from a Q&A-segment uncertainty regression on presentation-segment uncertainty plus firm-time controls — DWZ 2021); UncPreCEO (presentation-segment uncertainty share).
- **Bates 2009 base controls.** Leverage, lnAssets, TobinsQ, ROA, Capex, DivDummy, sCFO, Lagged_DV.
- **Existing main-panel structure.** Headline robustness grid is a 2×2×2 design varying along three dimensions: entity FE (industry FE in cols 1, 3, 5, 7, 9, 11; firm FE in cols 2, 4, 6, 8, 10, 12), time FE (calendar-year vs calendar-year-quarter), and DV horizon (cash at t vs cash at t+1, where t+1 specs use lead-DV as outcome not as control). Lagged-DV is a control in t-cells only.

## 4. Research question

**Step 1 — enumerate.** Identify all plausible reverse-causality mechanisms (cash → speech uncertainty) that could explain our headline finding under the null of no forward effect. Be comprehensive; do not restrict to obvious mechanisms. Flag the dominant 2–3 mechanisms based on theoretical plausibility and empirical relevance.

**Step 2 — find top 3 identification strategies** that satisfy ALL of the following:

1. Meet the modus-tollens bar (Section 2) for the dominant 2–3 reverse mechanisms from Step 1.
2. Compatible with at least one planned heterogeneity test that isolates the precautionary channel.
3. Anchored in top-tier journals — application papers in: JF, JFE, RFS, AER, JPE, QJE, ReStud, JAR, JAE, RAST, CAR. Methodological-justification papers may additionally be in: JoE, JBES, ReStat, ManSci.
4. Feasible within our 2002–2018 quarterly panel; no panel extension required.

**Expected candidate count.** 5–15 strategies in the published literature meet these constraints. A thin output of 3–4 candidates is consistent with the literature, not a search failure.

**No suggested classes — search broadly.** Do not let any framing prejudge the design space. Consider IV instruments, reverse-falsification tests, heterogeneity-based modus tollens, structural shocks, and any other class consistent with the bar.

## 5. Output format

### A. Reverse-mechanism enumeration (from Step 1)

Bullet list of 4–8 named plausible reverse mechanisms with 1-sentence description each. Mark the dominant 2–3 that the strategies in Section C target.

### B. Comparison table

| Strategy | Anchor citation | Strategy class (i/ii/iii) | Reverse-mechanism(s) it falsifies | Feasibility within 2002–2018 quarterly panel |
|---|---|---|---|---|

### C. Per-strategy 1-page brief (×3)

For each strategy:

1. **Name + anchor citation.** Paper, journal, year, DOI. Multiple anchors permitted (e.g., application paper + methodological paper).
2. **Identification mechanism in plain language.** What is exogenously varied (or what reverse-pattern is tested); how; why exogenous.
3. **Logic chain — predictions.**
   - Under forward story (speech → cash via precautionary channel): what is observed empirically?
   - Under each named reverse mechanism (from Step 1): what is observed empirically?
   - How does the test discriminate between them?
4. **Channel-isolation plan.** One or two heterogeneity tests that, if confirmed, isolate the precautionary channel specifically (vs. investor-sentiment, analyst-pressure, board-monitoring, agency-cost, free-cash-flow, or other channels).
5. **Known caveats** from the foundational paper and follow-up literature.
6. **Strongest reviewer objections + verdict.** Address ALL of the following objection classes for the proposed design, not just one:
   - (a) Exclusion-restriction violation (for IV designs)
   - (b) SUTVA / spillover
   - (c) Anticipation effects
   - (d) Measurement error in X (UncResCEO has finite-sample residual error from CEO fixed-effect estimation)
   - (e) Heterogeneous-effects reinterpretation

   For each: state SURVIVES (defensible response exists, citing the response) or TOLERATES (no clean response — disclosure is the only handling).
7. **Bar-meeting transparency.** Which aspects of the modus-tollens bar this strategy meets, which it misses (if any).

### D. Ranking justification

1-paragraph justification for the chosen ranking. Address: (i) theoretical solidity of the anchor, (ii) feasibility in the operative regression sample (~43k firm-quarter observations across ~1,400 firms), (iii) comparison to standard-bar alternatives in the published literature.

---

End of brief.
