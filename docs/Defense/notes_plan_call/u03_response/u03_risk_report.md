# U03 Examiner Attack Map

**Status: PARTIAL.** Slide 10 is resolved. One newly found design ambiguity—the handling of exactly 50/50 deals—cannot be settled from the supplied files.

## Inventory

| File | Bytes | Read in full | Pages |
|---|---:|:---:|---:|
| PROMPT_2026-07-22_133056.md | 4,040 | yes |  |
| DEFENSE_LEDGER.md | 25,898 | yes |  |
| SPEAKER_NOTES_BUDGET.md | 7,290 | yes |  |
| WEB_RESPONSE_SCHEMA.json | 6,880 | yes |  |
| WEB_REVIEW_REQUEST.json | 6,524 | yes |  |
| audit_findings.md | 20,284 | yes |  |
| rev22_deck.pdf | 190,140 | yes | 13 |
| rev22_slide_text.md | 16,035 | yes |  |
| rev22audit_response.json | 24,809 | yes |  |
| thesis_flat.tex | 162,954 | yes |  |
| thesis_robustness_tables.tex | 13,671 | yes |  |
| thesis_tables.tex | 39,922 | yes |  |
| u01_claim_ledger.md | 14,294 | yes |  |

## Direct answers

### Q1

Slide 9 carries the most dangerous unexamined claim: “becomes indistinguishable from baseline at announcement.” The significant PRE1-to-GAP drop supports a decline, but the nonsignificant GAP coefficient is not an equivalence test proving the signal is gone. It survived because the phrase comes from the thesis’s own central narrative, so prior reviews challenged PRE2 and onset timing but did not apply the same null-versus-equivalence discipline to GAP.

### Q2

The likeliest question that neither the thesis nor the ledger can answer quantitatively is: “How accurate is CEO speaker attribution and Q&A segmentation?” This committee is documented as likely to drill the data pipeline, and the thesis contains no validation rate or sensitivity analysis. The 2018 endpoint is also unexplained, but attribution is more likely to threaten the measured outcome directly.

### Q3

Yes. The full attenuation and PRE2 rebuttals are correctly held for Q&A. Together they take about 129 words, roughly seventy seconds, while slide 12 has only about 120 words. The podium should still use safe result wording: no detected PRE2 elevation, and PRE1 is announcement-anchored proxy exposure. The conditional bias-sign and power arguments belong only in answers to an actual challenge.

### Q4

Slide 10 reconciles. The “drop post-announcement quarters” sentence applies to MA1, the single-indicator run-up test. The slide’s left panels are the separate cash and stock disclosure-window event studies from Table empire_drop_placebo, which explicitly use PRE2, PRE1, GAP, and POST. The right panel is MA3, the pooled pre-announcement Wald test from Table empire_cashspec. Section 7 of the ledger treated an MA1 sample rule as though it governed both displays.

### Q5

Yes. Two of the three unapplied slide-12 findings become more dangerous aloud. “Tracks the point” invites the presenter to claim raw uncertainty and exact timing, and the negotiation-onset sentence invites the unsafe “therefore conservative” attenuation answer. “Imperfect instruments” is less substantive but can still trigger an unnecessary IV and exclusion-restriction question. Narration should say residual, quarterly disclosure states, announcement-anchored proxy, and measurement/comparison limits.

### Q6

Q13, speaker attribution, is answered worst. The defense ledger’s draft says misattribution adds noise and attenuates toward zero, but the supplied prompt correctly forbids that unsigned-bias claim. The thesis provides role and segment parsing but no measured accuracy. Q16 on the 2018 endpoint is unanswered, yet Q13 is worse because the current prepared answer is not merely incomplete; its central bias claim is invalid without nondifferential-error assumptions.

## Slide-by-slide sweep

### Slide 1 — CLEAN

Checked: Title, subtitle, candidate and advisor labels against the thesis title page. No independent result claim is made unless the title is orally upgraded into verified negotiation exposure.

No independent finding beyond the stated carryover boundary.

### Slide 2 — CLEAN_WITH_EXISTING_BOUNDARY

Checked: Framework sequence, legal non-misleading constraint, less-scripted Q&A venue, and hypothesis register. The only live boundary is the already-known fact that PRE1 does not verify negotiation or knowledge onset.

No independent finding beyond the stated carryover boundary.

### Slide 3 — FINDING

Checked: Two-clock motivation, cash-versus-stock rationale, prior-work role, and whether “cleaner” could be narrated as identification.

**U03-F03 — MINOR — new**

- Visible text: Cash: No equity currency to protect. Relatively cleaner window onto the disclosure state.
- Natural oral overstatement: Cash deals provide a clean counterfactual, or the cash-stock contrast identifies the effect of the disclosure bind rather than selection into payment method.
- Thesis ceiling: Prior literature motivates cash as a relatively less-managed setting, but the thesis explicitly treats this as motivation, not identification, and calls stock an imperfect counterfactual.
- Evidence: thesis_flat.tex: “Here the point is motivation, not identification, and the source of the cash uncertainty stays open.”
- Safe claim form: Cash is the relatively cleaner motivating setting; it is not a clean counterfactual, and payment-method selection remains unresolved.

### Slide 4 — CLEAN

Checked: All three roadmap equations, fixed effects, controls, direct Wald contrast, descriptive register, and the fact that the equations are schematic rather than full specifications.

No independent finding beyond the stated carryover boundary.

### Slide 5 — CLEAN

Checked: Nearest-work objects and venues, the restored “To our knowledge” qualifier, and the distinction among tone, vocabulary, prices, and residual CEO Q&A uncertainty.

No independent finding beyond the stated carryover boundary.

### Slide 6 — FINDINGS

Checked: All sample counts, data links, deal screen, sample-selection note, the funnel’s implied attrition story, and mutual exclusivity of the payment thresholds.

**U03-F04 — MINOR — new**

- Visible text: 88,205 calls → CEO identity + five calls → 44,900 calls.
- Natural oral overstatement: CEO matching and the five-call rule alone explain the fall from 88,205 to 44,900 calls.
- Thesis ceiling: The residual sample also depends on Execucomp coverage and complete availability of the variables required by the first-stage decomposition. The supplied thesis does not provide a filter-by-filter attrition reconciliation to 44,900.
- Evidence: thesis_flat.tex: “We also restrict the panel to firms that Execucomp covers” and “The count N varies from row to row, because each variable is summarized only on the calls for which it is available (its complete cases).”
- Safe claim form: The 44,900 calls are the complete-case residual sample after CEO identification, the minimum-call rule, Execucomp coverage, and required first-stage inputs.

**U03-F05 — MINOR — new**

- Visible text: Cash arm: at least 50% cash. Stock comparison: at least 50% stock.
- Natural oral overstatement: The two treatment arms are necessarily mutually exclusive under the stated thresholds.
- Thesis ceiling: The thesis states both thresholds but does not say how an exactly 50/50 deal is assigned, whether such deals occur, or whether they can be eligible for both indicators.
- Evidence: thesis_flat.tex: “Deals that are at least 50% cash form the cash arm; deals that are at least 50% stock form the stock comparison arm.”
- Safe claim form: The thesis uses the two at-least-half thresholds; exact 50/50 classification is not documented in the supplied files and should not be improvised.

### Slide 7 — FINDING

Checked: Raw measure, first-stage controls, CEO fixed effect, generated-regressand caveat, sample counts, and whether residualization “isolates” the construct.

**U03-F02 — MAJOR — new**

- Visible text: Raw CEO-answer uncertainty is residualized to isolate call-specific uncertainty.
- Natural oral overstatement: The first stage isolates true call-specific uncertainty, deal-related uncertainty, or what the CEO privately knows.
- Thesis ceiling: UncResCEO is the residual left unexplained by the specified first-stage model. It is an operationalization or proxy, and can retain omitted call-level influences and measurement error.
- Evidence: thesis_flat.tex: “the residual is one operationalization of call-specific uncertainty rather than a direct reading of what a chief executive knows.”
- Safe claim form: UncResCEO is the unexplained residual from the specified first stage, used as a proxy for call-specific answer uncertainty after modeled components are removed.

### Slide 8 — FINDING

Checked: Estimate, SE, p-value, derived interval, sample, fixed effects, economic magnitude denominator, and the existing announcement-onset boundary behind “final private quarter.”

**U03-F06 — MINOR — new**

- Visible text: About 15% of the usual spread.
- Natural oral overstatement: The coefficient is 15% of a typical CEO’s within-person variation or of the within-firm variation used for identification.
- Thesis ceiling: The denominator is the pooled all-universe standard deviation of UncResCEO across available calls, not a within-CEO or within-firm standard deviation.
- Evidence: thesis_flat.tex: “roughly 15.3%, taking 0.0461 against the all-universe standard deviation of 0.3010.”
- Safe claim form: The estimate is about 15% of the pooled cross-call standard deviation of UncResCEO.

### Slide 9 — FINDINGS

Checked: Every bin, both Wald tests, matched rows, cash lag, baseline, quarterly timing, non-significance versus equivalence, and completion-bin precision.

**U03-F01 — MAJOR — new**

- Visible text: Two clocks: residual uncertainty becomes indistinguishable from baseline at announcement; cash falls only at completion.
- Natural oral overstatement: The signal is proven to be gone, equal to baseline, or fully resolved at announcement.
- Thesis ceiling: The average GAP coefficient is near zero and not statistically significant, and the PRE1-to-GAP Wald decline is significant. That supports a decline after announcement, not statistical equivalence to zero or proof that the signal fully disappears.
- Evidence: thesis_flat.tex: “the residual spikes at PRE1 to 0.0473 ... and then falls to insignificance ... with a GAP coefficient of 0.0018 ... not significant. The drop from PRE1 to GAP is itself significant, 0.0455 ...”
- Safe claim form: The GAP estimate is near zero and no longer statistically different from baseline, while the PRE1-to-GAP decline is significant; this is a decline result, not an equivalence result.

**U03-F07 — MINOR — new**

- Visible text: Cash falls only at completion. / Cash ratio decline appears after completion.
- Natural oral overstatement: The regression identifies the exact closing-date response or proves no cash decline occurs before that date.
- Thesis ceiling: The cash ratio is lower in a quarterly POST bin covering quarters after completion, and the GAP-to-POST contrast is significant. The design is quarterly and the persistence leg is partly mechanical.
- Evidence: thesis_flat.tex: “POST covers the quarters after the deal has completed” and “We cap the post-window at four quarters.”
- Safe claim form: The cash ratio is lower in the post-completion bin; the design does not pinpoint an exact closing-date response.

### Slide 10 — CLEAN

Checked: All coefficients and samples, separate-panel versus pooled-test logic, formal Wald interpretation, fragility language, source tables, and the apparent GAP/POST discrepancy. The discrepancy resolves.

No independent finding beyond the stated carryover boundary.

### Slide 11 — CLEAN

Checked: Each of the three selected descriptive contributions against the thesis contribution paragraph and conclusion; omission of the bid-ask contribution does not make the stated three false.

No independent finding beyond the stated carryover boundary.

### Slide 12 — FINDINGS

Checked: Causal boundary, generalizability, announcement-onset limitation, measurement and stock-comparison limits, plus the three prior-audit findings left unapplied.

**U03-F08 — MINOR — previously known**

- Visible text: CEO Q&A uncertainty tracks the point when an acquisition moves from private to public.
- Natural oral overstatement: Raw CEO uncertainty identifies the exact point at which the deal or the CEO’s knowledge changes state.
- Thesis ceiling: The estimated object is residual CEO-answer uncertainty observed on quarterly calls and grouped into announcement-relative states. It is not raw uncertainty and not an exact timestamp.
- Evidence: thesis_flat.tex: “the residual is one operationalization of call-specific uncertainty rather than a direct reading of what a chief executive knows.”
- Safe claim form: Residual CEO Q&A uncertainty differs between the final pre-announcement and announced-not-closed states.

**U03-F09 — MINOR — previously known**

- Visible text: The data mark the announcement date, not when negotiations began.
- Natural oral overstatement: PRE1 is known exposure to negotiations or withholding, or any timing error must attenuate the estimate.
- Thesis ceiling: Event time is announcement-anchored. Negotiation onset, materiality onset, and CEO-knowledge onset are not observed, so PRE1 is only a proxy for a possible withholding window and the direction of timing-error bias cannot be signed.
- Evidence: audit_findings.md: “The supplied thesis does not observe negotiation onset, materiality onset, or knowledge onset.”
- Safe claim form: Event time is anchored on announcement; negotiation onset is unobserved, so PRE1 is a proxy for a possible withholding window, not verified exposure.

**U03-F10 — NIT — previously known**

- Visible text: Imperfect instruments.
- Natural oral overstatement: The design uses instrumental variables or has an exclusion restriction to defend.
- Thesis ceiling: The box contains a measurement limitation and a comparison-group limitation, not instruments in the econometric sense.
- Evidence: thesis_flat.tex: “Uncertainty is captured by applying a finance-specific word list ...” and “The stock-financed comparison ... is an imperfect counterfactual.”
- Safe claim form: Call these measurement and comparison limits; do not use the word instruments aloud.

### Slide 13 — CLEAN_WITH_CARRYOVER_BOUNDARY

Checked: The “suggest” hedge, private-to-public conclusion, cash-stock formal contrast, and whether “fades” is narrated as a decline/non-detection rather than equivalence. U03-F01 governs the oral form.

No independent finding beyond the stated carryover boundary.

## Slide 10 discrepancy

**Resolved: yes.**

The ledger’s apparent contradiction comes from applying an MA1 sentence to every cash-versus-stock regression. The sentence about dropping post-announcement quarters describes MA1, the single-indicator pre-announcement run-up test in Table empire_building_did. Slide 10’s left side is not MA1: it is the four-bin MA2-style disclosure-window event study in Table empire_drop_placebo, rerun separately for cash and stock and therefore legitimately showing PRE2, PRE1, GAP, and POST. Slide 10’s right side is MA3, the pooled pre-announcement cash-minus-stock test in Table empire_cashspec, which uses the pre-deal treatment indicators. Thus the left panel contains post-announcement bins and the right panel does not; both are correctly sourced on the slide.

Settling text:

> thesis_flat.tex: “Our first main analysis (MA1) ... For treated firms we drop the quarters after the announcement, so the design sees only the run-up into the deal.” Also: “We begin descriptively, rerunning the event study side by side on the stock comparison arm, using the stock column of Table empire_drop_placebo...” thesis_tables.tex: “Disclosure-window event study estimated separately for cash acquirers and ... stock acquirers ... Bins and baseline as in the matched event study.” 

## Podium versus Q&A

| Risk | Placement | Cost | Displaces |
|---|---|---|---|
| Slide 9 non-significance being narrated as equivalence or complete resolution | PODIUM | About 12–18 words to say “near zero and no longer statistically detected; PRE1-to-GAP falls significantly.” The cost is small and prevents the central result from becoming an unsupported equivalence claim. | A redundant description of the POST dip or a repeated axis label on slide 9. |
| Residualization being narrated as isolation of true or deal-specific uncertainty | PODIUM | About 8–12 words to call UncResCEO an unexplained residual or operationalization. Without it, the method claim invites a construct-validity attack. | One example from the long list of first-stage controls on slide 7. |
| Cash as a clean counterfactual and payment-method endogeneity | BOTH | A short podium boundary—motivation, not identification—costs roughly 8–10 words. The selection argument and observable arm differences stay for Q&A. | One sentence of literature motivation on slide 3, not a result. |
| The 88,205-to-44,900 funnel being attributed only to CEO identity and five calls | PODIUM | Adding “complete-case residual sample” costs three words and prevents a false attrition account. | Nothing material. |
| Exactly 50/50 deals under two at-least-half thresholds | QA | Putting this edge case on the podium would interrupt the sample story and cannot be answered from the supplied files. Holding it requires checking the classification code or transaction-level counts before the defense. | If volunteered, it would consume sample-screen time without a settled answer. |
| The 15% magnitude being heard as within-CEO variation | PODIUM | One qualifier—“pooled”—is enough. No meaningful time cost. | Nothing. |
| Quarterly POST bin being narrated as an exact closing-date response | PODIUM | Saying “post-completion bin” instead of “at completion” is cost-neutral and preserves the timing resolution actually estimated. | Nothing. |
| Unobserved negotiation onset and the sign of timing-error bias | BOTH | The podium should spend roughly 12–16 words naming PRE1 as announcement-anchored proxy exposure. The conditional bias analysis stays in Q&A; speaking it unprompted would consume much of slide 12. | A repeated causal disclaimer on slide 12; the full attenuation rebuttal displaces too much and should not be spoken. |
| PRE2 being used to claim no pre-trend or tight timing | QA | No extra podium words are needed if the presenter says only “no statistically detected PRE2 elevation.” The full power/equivalence qualification is held cold for Q&A. | Speaking the full rebuttal would take result-walking time from slide 9. |
| The attenuation and PRE2 rebuttals as a pair | QA | The measured pair is about 129 words, roughly 70 seconds at the hedged rate. Slide 12 has about 120 words total, so podium placement would consume the entire limitations slide and force cuts to the conclusion. | Most of slide 12 or a substantial part of slides 11–13. |
| The phrase “Imperfect instruments” inviting an IV question | PODIUM | Call the box “measurement and comparison limits” aloud. This is cost-neutral and avoids an exclusion-restriction detour. | Nothing. |
| Generated-regressand standard errors and the unsafe “only adds noise” answer | BOTH | A short podium acknowledgment that first-stage uncertainty is not propagated costs roughly 10–14 words; bootstrap details and any bias discussion stay in Q&A. | One lower-priority control example on slide 7. |
| Speaker-attribution accuracy | QA | Volunteering an unvalidated accuracy issue would invite a data-pipeline attack and has no quantitative resolution. Holding it requires a precise concession and no claim that errors merely add noise. | If volunteered, it would consume method time without supplying evidence. |
| Why the sample ends in 2018 | QA | The thesis supplies no rationale, so podium discussion can only advertise an unanswered question. Holding it requires a direct concession and a scope boundary. | Sample-description time on slide 6. |
| “Readable” being heard as tradable or usable in real time | QA | No podium expansion is needed because the deck already frames the result as descriptive. The presenter must be ready to distinguish panel detectability from a live prediction or investment signal. | A future-work or investor-prescription detour that is outside the thesis. |

## The two silences

### Why does the sample end in 2018?

**Best honest boundary:** The submitted thesis fixes the study window at 2002–2018 but gives no rationale for the endpoint. No data-coverage, licensing, pre-registration, or structural-break explanation should be invented. The defensible boundary is that the evidence applies to that period; whether it extends to later years is untested here. A candidate-specific production reason may be stated only if it is actually known and clearly distinguished from an ex ante research-design rationale.

**Likely next question:** Was 2018 chosen before seeing the results; could later Capital IQ, Execucomp, and SDC data be added; did disclosure practice or transcript coverage change after 2018; and would the result survive a post-2018 replication?

### How accurate is CEO speaker attribution and Q&A segmentation?

**Best honest boundary:** The thesis states that Capital IQ transcripts are parsed by role and segment and that Execucomp identifies the CEO, but it reports no hand-validation rate, confusion matrix, error bound, or sensitivity analysis. Accuracy is therefore unquantified in this study. The direction of any resulting bias cannot be signed without assumptions about whether attribution errors vary with event time, payment method, call structure, or language.

**Likely next question:** Show a manually coded validation sample; report false-positive and false-negative rates; rerun on high-confidence or unambiguous calls; and explain whether any misclassification is differential around PRE1 or across cash and stock deals.

## Limitations

- The supplied files do not document how exactly 50/50 payment deals are classified under the two “at least 50%” thresholds, or whether any such observations exist. The transaction-classification code or deal-level frequency table would settle this; status is therefore PARTIAL.
- The thesis contains no rationale for the 2018 endpoint and no quantified speaker-attribution validation. The response gives defensible boundaries, not empirical resolutions.
- No speaker notes or prepared answer scripts were written, in accordance with the request; only safe claim forms and podium/Q&A placement were produced.
