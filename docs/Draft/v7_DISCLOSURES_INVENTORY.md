# v7 Honest-Disclosures Inventory

**Built:** 2026-04-29 (Step 2B)
**Revised:** 2026-04-29 LATE×13 — Death DiD dropped entirely per D25. Disclosures #1, #2, #3, #4, #19 DROPPED. #12 revised 3-design → 2-design. #13 revised 3-threats → 2-threats.
**Revised again:** 2026-04-29 LATE×14 — DWZ FD ALSO dropped entirely per D26 (firm FE in main panel mathematically absorbs the same time-invariant-firm-trait threat). Disclosures #5, #6, #7 DROPPED. #12 RETIRED entirely (only one design remains; nothing to compare). #13 revised again: Lewbel covers one specific threat (speech-direction reverse causality + measurement error + time-varying confounders); main-panel firm FE covers time-invariant U. Coverage table updated.
**Source:** v6 prose grep + locked memory verbatim
**Purpose:** preserve every honest disclosure from v6 across the rewrite, with an explicit v7 home assignment for each. Per advisor blocker B1.

**Format per disclosure:** name → 1-line summary → verbatim v6 source → v7 subsection home → status.

**Status legend:**
- **KEEP** — port verbatim or near-verbatim into v7 prose
- **ADAPT** — rewrite for v7 framing (e.g., D10 single-channel reframing)
- **GAP** — disclosure has no obvious v7 home; structural review needed

---

## Endogeneity (§III.E composite-table notes)

### 1. Death DiD pre-trend = mean reversion, not parallel — **DROPPED per D25**
**1-line:** Pre-period placebo positive both 4q (β=+0.027) and 8q (β=+0.021); post-event ATT negative; pattern consistent with mean reversion not a clean parallel-trends pass.
**v6 source:** `section_4_additional.tex` line 72: "The pattern is consistent with mean reversion rather than a clean parallel-trends pass; we describe it as such rather than claim 'parallel trends pass.'"
**v7 home:** §III.E Endogeneity — Death DiD panel notes (or composite table footnote)
**Status:** KEEP

### 2. Death DiD lagged-DV exclusion (Bertrand-Mullainathan-Duflo 2004) — **DROPPED per D25**
**1-line:** DiD specifications omit lagged DV per Bertrand-Mullainathan-Duflo 2004 standard practice (cash highly persistent → including lagged DV mechanically absorbs ATT).
**v6 source:** `section_4_additional.tex` line 72: "The Phase E specifications omit the lagged dependent variable that is otherwise required in Section…\ref{sec:main}, following the standard DiD practice of \citeA{bertrand2004}…"
**v7 home:** §III.E Endogeneity — Death DiD panel notes
**Status:** KEEP

### 3. Death DiD: 16 firm clusters below 30 conventional asymptotic threshold — **DROPPED per D25**
**1-line:** With 16 unique firm clusters (8 treated + 8 controls), cluster-robust SEs are below conventional asymptotic-validity threshold (~30); reported with disclosure.
**v6 source:** `section_4_additional.tex` line 72: "With sixteen unique firm clusters (eight treated plus eight matched controls), cluster-robust standard errors are below the conventional asymptotic-validity threshold of approximately thirty…"
**v7 home:** §III.E Endogeneity — Death DiD panel notes
**Status:** KEEP

### 4. Death DiD: pre-event UncResCEO heterogeneity test infeasible — **DROPPED per D25**
**1-line:** n=8 events doesn't allow median-split heterogeneity on pre-event UncResCEO (would yield 4/cell). Pooled ATT only; speech-channel-specific decomposition future work.
**v6 source:** `section_4_additional.tex` line 72: "The originally proposed heterogeneity test on pre-event UncResCEO is not feasible at this sample size…"
**v7 home:** §III.E Endogeneity — Death DiD panel notes + §V.3 Future Work
**Status:** KEEP

### 5. DWZ FD identifies ClarityCEO only (not UncResCEO) — **DROPPED per D26**
**1-line:** First-difference annihilates UncResCEO by OLS first-order conditions (within-CEO mean = 0 by construction); FD spec identifies ClarityCEO only.
**v6 source:** `section_4_additional.tex` line 81: "The first-difference does not identify the UncResCEO effect because the within-CEO mean of UncResCEO is zero by construction…"
**v7 home:** §III.E Endogeneity — DWZ FD panel notes + ID-asymmetry framing
**Status:** KEEP

### 6. DWZ FD design deviations (FF12 vs FF48; intangibles omitted; Main industries) — **DROPPED per D26**
**1-line:** Three documented deviations from DWZ §6 spec: FF12 not FF48; intangibles-ratio omitted; Main industries only.
**v6 source:** `section_4_additional.tex` line 81: "Three deviations from the \citeauthor{dzielinski2021} Section 6 specification are documented in Appendix~\ref{app:vardefs}: (i) industry fixed effects use the Fama-French 12 partition rather than \citeauthor{dzielinski2021}'s Fama-French 48 (panel-infrastructure constraint); (ii) the intangibles-ratio control is omitted because it is not constructed in our panel; (iii) the sample restricts to F1D Main industries…"
**v7 home:** §III.E DWZ FD panel notes + Appendix Variable Definitions
**Status:** KEEP

### 7. DWZ FD applied to cash → endogeneity concern stronger than DWZ Tobin's Q — **DROPPED per D26**
**1-line:** Cash is CEO-discretion choice variable; endogeneity concern stronger than in DWZ's Tobin's Q application.
**v6 source:** `section_4_additional.tex` line 81: "Cash is also a CEO-discretion choice variable, which makes endogeneity more concerning here than in \citeauthor{dzielinski2021}'s Tobin's Q application. We treat this design as a robustness companion to the Phase E sudden-death DiD rather than as primary identification."
**v7 home:** §III.E DWZ FD panel notes
**Status:** KEEP

### 8. Lewbel col 3 over-id rejected (Sargan p=0.009)
**1-line:** Col 3 (extended-instrument set) Sargan p=0.009 — over-id rejected. Col 2 (six-instrument set, Sargan p=0.92) treated as primary.
**v6 source:** `section_4_additional.tex` line 90: "The Sargan over-identification test fails to reject the joint-validity null in col 2 (p=0.92) but rejects it at p<0.05 in col 3 (p=0.009); we accordingly treat col 2 as the primary specification…"
**v7 home:** §III.E Lewbel panel notes
**Status:** KEEP

### 9. Lewbel col 2 first-stage borderline weak (Stock-Yogo)
**1-line:** Cragg-Donald F=20.4 in col 2 above F=10 weak-IV threshold but below Stock-Yogo 10%-maximal-IV-size threshold ≈23 → borderline weak.
**v6 source:** `section_4_additional.tex` line 90: "the col 2 statistic is below the more demanding Stock-Yogo 10%-maximal-IV-size threshold of approximately 23 for one endogenous regressor with six instruments, so we disclose the col 2 first-stage as borderline weak under the Stock-Yogo criterion."
**v7 home:** §III.E Lewbel panel notes
**Status:** KEEP

### 10. Lewbel Wu-Hausman = failure to reject (NOT evidence FOR OLS)
**1-line:** Wu-Hausman p=0.24 in col 2 — failure to reject OLS-consistency null; treat as failure-to-reject, not evidence-in-favor.
**v6 source:** `section_4_additional.tex` line 90: "The Wu-Hausman test of OLS-consistency under exogeneity does not reject the null in col 2 (p=0.24); we treat this as a failure to reject rather than evidence in favor of OLS-consistency."
**v7 home:** §III.E Lewbel panel notes
**Status:** KEEP

### 11. Lewbel 2SLS ≈ 5× OLS (consistent with measurement-error attenuation)
**1-line:** 2SLS-Lewbel β ≈ 5× OLS β. Consistent with classical ME attenuation in OLS. Not statistically distinguishable at conventional thresholds given wider 2SLS SE.
**v6 source:** `section_4_additional.tex` line 90: "The 2SLS-Lewbel point estimate is approximately five times the OLS estimate, a magnitude consistent with classical measurement-error attenuation in OLS; the 2SLS-Lewbel and OLS point estimates are not statistically distinguishable from each other at conventional thresholds given the wider 2SLS standard error."
**v7 home:** §III.E Lewbel panel notes
**Status:** KEEP

### 12. ID-asymmetry across endogeneity designs — **RETIRED per D26 (only Lewbel remains; nothing to compare)**
**Status:** Retired entirely. With DWZ FD dropped per D26 and Death DiD dropped per D25, only Lewbel IV remains. There is no longer a multi-design package to compare ID-asymmetry across. Disclosure not applicable.
**Original 1-line (pre-D25):** 3 designs target different speech components by construction: Death DiD + DWZ FD identify ClarityCEO only; Lewbel identifies UncResCEO. Coverage gap reflects underlying statistical structure of two components, not a design weakness.
**Post-D25 1-line (pre-D26):** 2 designs target different speech components by construction: DWZ FD identifies ClarityCEO only; Lewbel identifies UncResCEO.
**v6 source:** `section_4_additional.tex` line 95: "The three designs target different speech components by construction. The Phase E and DWZ first-difference designs identify ClarityCEO via cross-CEO-pair variation around turnover events; neither identifies UncResCEO, because the residual of a CEO-fixed-effect regression has within-CEO mean exactly zero by OLS first-order conditions… The asymmetry across designs reflects the underlying statistical structure of the two speech components, not a coverage gap in the endogeneity package."
**v7 home:** §III.E framing paragraph (intro to composite endogeneity table)
**Status:** KEEP

### 13. Endogeneity defense narrow scope — **REVISED AGAIN per D26 (two-threats → single-threat at §III.E)**
**1-line (current per D26):** Main panel firm FE absorbs time-invariant unmeasured firm traits. §III.E Lewbel IV addresses one specific additional threat: speech-direction reverse causality plus measurement error plus time-varying confounders. Together they cover the threats relevant to our setup. Selection threat (firms self-selecting CEOs based on cash needs) is acknowledged as orphaned but settled in the literature.
**Post-D25 1-line (pre-D26):** Endogeneity package framed as covering two orthogonal identification threats with two pre-specified designs (DWZ FD for time-invariant unobserved heterogeneity; Lewbel IV for reverse causality and time-varying confounders), not as convergence on a single point estimate.
**Original 1-line (pre-D25):** Endogeneity package framed as covering three orthogonal identification threats with three pre-specified designs, not as convergence on a single point estimate.
**v6 source:** `section_2_framework.tex` line 24 + `section_4_additional.tex` line 63: "The endogeneity package is framed as covering three orthogonal identification threats with three pre-specified designs, not as convergence on a single point estimate."
**v7 home:** §III.E framing paragraph + §V.2 Limitations
**Status:** KEEP

---

## Hypothesis Development (§II.2)

### 14. ClarityCEO direction interpretive (not pre-registered)
**1-line:** BS 2003 anchor predicts existence-of-channel only, not specific sign for ClarityCEO. Observed negative direction reported as empirical pattern, not pre-registered theoretical prediction.
**v6 source:** `section_2_framework.tex` line 18 (¶1 enumerate item 2): "Channel-of-existence pre-registered; specific direction interpretive… anchoring the existence of a CEO-trait → cash channel without committing ex ante to a particular sign for our ClarityCEO construct." + line 49: "The ClarityCEO direction observed in Section…\ref{sec:main:hc} is interpretive rather than pre-registered."
**v7 home:** §II.2 H1 anchor (ClarityCEO existence vs direction)
**Status:** ADAPT — D10 reframing keeps the existence-vs-direction distinction; rewrite for new hypothesis labels (H1 not HC)

### 15. ACW asymmetry → within-call-shock = hypothesis-development extension
**1-line:** ACW 2004's anchor is macro-shock asymmetry; our extension to within-call CEO speech uncertainty as the shock signal is a hypothesis-development extension, not a pre-existing theoretical result.
**v6 source:** `section_2_framework.tex` line 49: "The H2 amplification anchor is \citeauthor{almeida2004}'s macro-shock asymmetry; our extension to within-call CEO speech uncertainty as the shock signal is a hypothesis-development extension, not a pre-existing theoretical result."
**v7 home:** §II.2 H1a anchor (financing-friction trigger) — explicitly disclose macro→within-call extension
**Status:** KEEP (load-bearing for H1a referee defense)

### 16. UncPreCEO → cash null is low-confidence prediction
**1-line:** UncPreCEO null on cash is a low-confidence claim relying on DWZ's control-variable role assignment, not an independent theoretical prediction.
**v6 source:** `section_2_framework.tex` line 49: "The UncPreCEO → cash null we predict is a low-confidence claim relying on the control-variable role \citeauthor{dzielinski2021} assign to the presentation segment."
**v7 home:** §II.2 H1 measurement detail
**Status:** KEEP

### 17. HFC adopts FP binary verbatim — NOT three-tier IG/BelowIG/Unrated extension
**1-line:** Binary rated-vs-unrated scheme adopted directly from FP 2006 (no three-tier IG/BelowIG/Unrated extension).
**v6 source:** `appendix_c_robustness.tex` line 13: "The binary scheme follows \citeauthor{faulkender2006} verbatim and is consistent with the macro-shock asymmetry framing of \citeA{almeida2004} §II.D. We do not estimate a three-tier IG/BelowIG/Unrated specification…"
**v7 home:** §II.2 H1a operational disclosure or §III.C subsection notes
**Status:** KEEP — but simpler in v7 since v6 had earlier three-tier extension we already dropped; now just clean FP-binary disclosure

---

## Cash-Flow-Volatility (§III.D — H1b)

### 18. UncPreCEO × HighCFvol = NOT pre-registered finding
**1-line:** UncPreCEO interaction with HighCFvol shows 4 of 8 cells significant at p<0.10 (post-hoc, not pre-registered). Base UncPreCEO is null but the HighCFvol-tail interaction activates a presentation-segment cash-amplification channel.
**v6 source:** `section_3_main.tex` line 63: "A second interaction surfaces a finding not pre-registered. The presentation-segment uncertainty share interacted with HighCFvol… We treat this finding as robustness-extending, not channel-redirecting…"
**v7 home:** §III.D H1b results paragraph — explicit "not pre-registered" disclosure with the post-hoc interpretation
**Status:** KEEP — important post-hoc disclosure must NOT be lost

---

## Conclusion / Limitations (§V.2)

### 19. Death DiD power limitation — **DROPPED per D25**
**1-line:** Sudden-death sample of 8 viable events below conventional power thresholds; 4 specifications negative in predicted direction but none significant at p<0.10.
**v6 source:** `section_5_conclusion.tex` line 31 (combined with disclosure 1-4): "the Phase E sudden-death sample size of eight viable events is below conventional power thresholds; the four DiD specifications report negative point estimates in the predicted direction but none statistically significant at p<0.10 one-tailed…"
**v7 home:** §V.2 Limitations
**Status:** KEEP

### 20. OPSW log-cash-to-net-assets robustness not estimated
**1-line:** Body specification = linear cash-to-assets (Bates form). OPSW log-form flagged as planned extension; not estimated in present draft.
**v6 source:** `section_3_main.tex` line 68 + `appendix_c_robustness.tex` C.2: "the linear cash-to-assets dependent variable of \citeauthor{bates2009} is the body specification; an OPSW log-of-cash-to-net-assets robustness is flagged as a planned extension in Section~\ref{sec:conclusion} but is not estimated in the present draft."
**v7 home:** §V.2 Limitations + §V.3 Future Work
**Status:** KEEP

### 21. Lewbel and Bates point estimates not stat-distinguishable
**1-line:** Lewbel 2SLS β ≈ 5× OLS β, but with wider SE → Wu-Hausman fails to reject OLS-consistency. Treat as failure to reject rather than evidence FOR OLS.
**v6 source:** `section_5_conclusion.tex` line 31: "the \citeA{lewbel2012} heteroskedasticity-based estimator delivers a 2SLS point estimate approximately five times the OLS estimate but with wider standard errors; the Wu-Hausman test does not reject OLS-consistency, and we treat this as a failure to reject rather than evidence in favor of OLS-consistency."
**v7 home:** §V.2 Limitations (composite endogeneity disclosure)
**Status:** KEEP — overlaps disclosure 10 + 11 but at conclusion level

---

## Mechanism / Framing (§II / §IV / §V)

### 22. Insider-outsider asymmetry NOT imposed; emerges within DWZ structure
**1-line:** Asymmetry between Q&A-driven cash response (§III) and Pres-driven outsider reaction (§IV) sits cleanly on DWZ's own scripted-vs-improvised theoretical structure for the two segments.
**v6 source:** `section_5_conclusion.tex` line 19: "The asymmetry sits cleanly on \citeauthor{dzielinski2021}'s own theoretical structure for the two segments of the call… We document the asymmetry within \citeauthor{dzielinski2021}'s theoretical scaffolding rather than impose it."
**v7 home:** §V.1 Summary (synthesis paragraph)
**Status:** ADAPT — D4 narrative now treats this as third-order observation, not headline; keep but de-emphasize

### 23. Two mechanisms (firm-side cash + outsider reaction) hold simultaneously, no causal bridge
**1-line:** Firm-side response anchored on precautionary motive (OPSW + Bates); outsider response on info-asymmetry + regulatory review (BGT + Lerman). Both mechanisms hold simultaneously; we do NOT claim a causal bridge.
**v6 source:** `section_5_conclusion.tex` line 24: "the Section~\ref{sec:main} firm-side cash response and the Section~\ref{sec:additional:reaction} outsider-reaction responses operate through theoretically distinct mechanisms; we do not claim a causal bridge between them."
**v7 home:** §V.1 Summary or §V.2 Limitations
**Status:** KEEP

---

## v7-Specific (D18 / D24)

### 24. CCCL framing v6→v7 correction
**1-line:** v6 §4.2.2 said "we measure SEC scrutiny via CCCL" — empirically loose. CCCL specifically captures DISCLOSURE-INSUFFICIENCY (80% per Lerman §3.2), not generic regulatory scrutiny.
**v6 source:** v6 framing was loose; D18 logged the correction.
**v7 home:** §IV.B opening paragraph — explicit Lerman verbatim grounding
**Status:** ADAPT — write fresh v7 prose with Lerman 80%/15%/3% breakdown

### 25. Single precautionary channel, two triggers (not two channels)
**1-line:** HFC and CFvol are NOT two distinct channels; they are two stress triggers of the SAME precautionary channel (financing-friction trigger + CF-volatility trigger).
**v6 source:** v6 framed them as separate channels; D10 corrected.
**v7 home:** §II.2 framing paragraph + §III.C/D subsection openings
**Status:** ADAPT (NEW v7 framing per D10)

### 26. H1 nested vs H2/H3 flat — explain WHY
**1-line:** H1 has nested H1a/H1b sub-hypotheses because both triggers test the SAME precautionary channel. H2 and H3 are flat because they're mechanistically distinct outsider channels (different parties, different processes).
**v6 source:** N/A (v7-specific structural decision per advisor F1)
**v7 home:** §II.2 framing paragraph (must explicitly explain the asymmetric labeling)
**Status:** ADAPT (new v7 prose, no v6 source)

---

## Coverage summary — REVISED per D25 + D26 (Death DiD + DWZ FD both dropped)

| v7 home subsection | Disclosures count |
|---|---|
| §II.2 Hypothesis Development | 5 (#14, #15, #16, #25, #26) |
| §II.2 + §III.C | 1 (#17) |
| §III.D H1b results | 1 (#18) |
| §III.E Endogeneity table notes (Lewbel IV only) | 4 (#8, #9, #10, #11) |
| §III.E framing | 1 (#13 revised: narrow scope, single-threat) |
| §IV.B opening | 1 (#24) |
| §V.1 Summary | 1 (#22) |
| §V.2 Limitations | 3 (#20, #21, #23) |
| §V.3 Future Work | 0 |

Active total: 17 disclosures.
Dropped per D25: 5 (#1, #2, #3, #4, #19).
Dropped per D26: 3 (#5, #6, #7).
Retired per D26: 1 (#12 — no multi-design comparison applicable).
Revised per D25 then D26: 1 (#13 — successively narrowed to single-threat scope).
All retired/dropped entries kept above for audit trail with **DROPPED** or **RETIRED** banners.

## Pre-D25 totals (audit trail)
Total: 26 disclosures (some span multiple subsections). 5 disclosures retired entirely + 2 disclosures revised = 7 affected by D25.

## Structural-gap flags (advisor F1 check)

**No v7 home gap.** All 26 disclosures map to a v7 subsection. The audit successfully forced consideration of v7 §IV.B (CCCL) framing fix (#24), which was loose in v6 — the advisor's "lose disclosures during Step 6" risk has been preempted.

**Adapt count = 4** (#14, #22, #24, #25, #26): these need rewriting for v7 framing (D4 + D10 + D18 reframings).

**Keep verbatim count = 22.**
