# Examiner Question Forecast

**Request ID:** `deck-audit-examiner-v1`  
**Status:** COMPLETE  
**Basis:** Source-closed review of the attached thesis excerpts, committee profiles, deck text, and rendered 13-page deck.

## Ranked questions by damage if unprepared

### 1. What evidence do you have that the CEO actually knew about, or was constrained by, this acquisition when the PRE1 earnings call occurred?

- **Most likely examiner:** Dutta
- **Prompted by:** Slide 2 states, "The firm holds potentially material deal information that investors do not yet have," while slides 4, 8, and 9 define the measured window only as the quarter before announcement.
- **Damage if unprepared:** Severe
- **Does the thesis answer it?** No
- **Best honest answer:** The study does not observe negotiation start dates or the CEO's knowledge at the call. PRE1 is an anticipatory event-time window before announcement, so the result is a correlational language pattern around later announced deals, not proof that every PRE1 call occurred after the CEO learned of the deal.
- **Source:** _intro_body(1).tex, paragraphs 1 to 7, supplies the withholding framework; sec34_body_from_ledgers(2).tex, Data and Sample and Main Analysis 1, defines PRE1 as the single quarter before announcement. The attached thesis excerpts provide no negotiation-start or CEO-knowledge measure.
- **Preparation route:** `concede`

### 2. Why should I believe UncResCEO is measuring meaningful spoken uncertainty rather than context-free dictionary usage, residual-model error, or a generated-regressor artifact?

- **Most likely examiner:** Zhang
- **Prompted by:** Slide 7 says raw uncertainty is residualized to "isolate call-specific uncertainty" and reports a two-step measurement limitation; slide 12 calls the word count an imperfect proxy.
- **Damage if unprepared:** Severe
- **Does the thesis answer it?** Partial
- **Best honest answer:** The measure applies the finance-specific Loughran-McDonald uncertainty list to CEO answers and removes persistent CEO style, prepared-language uncertainty, analyst-question uncertainty, call tone, performance, market conditions, and time effects. The thesis does not validate the construct with human labels or a contextual language model, and it does not present a correction that eliminates generated-regressor uncertainty, so those remain limitations.
- **Source:** sec34_body_from_ledgers(2).tex, Data, Sample, and Variable Construction, describes tokenization, the fixed uncertainty list, and the residual construction; _conclusion_body(1).tex, limitations, states that the count abstracts from context and is not a direct reading of CEO knowledge; deck slide 7 acknowledges two-step estimation uncertainty.
- **Preparation route:** `appendix`

### 3. Why is the run-up stronger for cash deals than for stock deals? What mechanism does your thesis actually establish?

- **Most likely examiner:** Dutta
- **Prompted by:** Slides 3, 10, 11, and 13 make payment method central, including "Relatively cleaner window onto the disclosure state" and "Stronger in cash."
- **Damage if unprepared:** Severe
- **Does the thesis answer it?** No
- **Best honest answer:** The thesis motivates cash as a cleaner comparison because stock acquirers use equity as transaction currency and may manage the pre-deal narrative, but it does not identify that mechanism or a cash-accumulation channel. The defensible claim is only that the pattern concentrates in cash deals in the sample.
- **Source:** _intro_body(1).tex, paragraphs 11 and 15, labels the stock-narrative explanation as motivation rather than identification; sec34_body_from_ledgers(2).tex, Main Analysis 3, states that the war-chest mechanism is not established; _conclusion_body(1).tex, limitations, says the cash concentration is motivated but not identified.
- **Preparation route:** `concede`

### 4. Your cash-minus-stock test has p = .039 and the stock coefficient is imprecisely negative. How fragile is the payment-method result?

- **Most likely examiner:** Dutta
- **Prompted by:** Slide 10 reports the direct Wald difference of 0.0983 with SE 0.0476 and p = .039, and explicitly notes that the result is supported but fragile.
- **Damage if unprepared:** Severe
- **Does the thesis answer it?** Yes
- **Best honest answer:** The first-deal pooled contrast clears the five-percent level, but part of the gap comes from a noisy negative stock estimate, so the thesis says concentration, not strict cash specificity. The all-deals stacked robustness strengthens the Wald difference to 0.1056 with p about .013, while the mechanism remains unestablished.
- **Source:** sec34_body_from_ledgers(2).tex, Main Analysis 3, reports the first-deal Wald result and its fragility; Robustness: The Main Findings Without the First-Deal Restriction reports the stronger all-deals Wald result.
- **Preparation route:** `appendix`

### 5. What is identified by this design, and what time-varying omitted variable could still generate the same pattern?

- **Most likely examiner:** Zhang
- **Prompted by:** Slides 4, 8, 9, 10, 11, and 12 repeatedly describe within-firm fixed-effect comparisons while disclaiming causality.
- **Damage if unprepared:** Severe
- **Does the thesis answer it?** Partial
- **Best honest answer:** The design identifies a within-firm association after firm controls, firm fixed effects, calendar year-quarter fixed effects, and firm-clustered inference; PRE2 is flat and the timing analysis uses matched rows. It does not identify a causal effect or rule out time-varying omitted conditions that coincide with acquisition preparation.
- **Source:** sec34_body_from_ledgers(2).tex, Main Analyses 1 and 2, describes the fixed-effect design, matched sample, and PRE2 validity check; _conclusion_body(1).tex, limitations, states that the design supports no causal identification and establishes no mechanism.
- **Preparation route:** `speaker_notes`

### 6. Why is a deal classified as cash or stock at the fifty-percent cutoff, and do your results survive alternative cutoffs or a continuous payment-share specification?

- **Most likely examiner:** Dutta
- **Prompted by:** Slide 6 defines the cash and stock arms using at least 50 percent of consideration, and slide 10 builds the formal contrast on those arms.
- **Damage if unprepared:** Severe
- **Does the thesis answer it?** No
- **Best honest answer:** The thesis uses the fifty-percent rule as its operational classification, but the attached thesis material gives no tested sensitivity to alternative thresholds or a continuous payment-share model. The honest answer is that this boundary is untested and limits the strength of the cash-versus-stock claim.
- **Source:** sec34_body_from_ledgers(2).tex, Data, Sample, and Variable Construction, defines the fifty-percent arms; _conclusion_body(1).tex, limitations, explicitly states that cutoff sensitivity is not tested.
- **Preparation route:** `concede`

### 7. Does the market detect or price this language signal, or is it only statistically visible to the researcher after the fact?

- **Most likely examiner:** Zhang
- **Prompted by:** Slide 5 contrasts language with prices, while slides 11 and 13 call the pattern "readable" and "anticipatory."
- **Damage if unprepared:** Moderate
- **Does the thesis answer it?** Partial
- **Best honest answer:** The thesis does not show that investors can trade on the acquisition-specific signal. Its post-call analysis finds UncResCEO unrelated to the bid-ask spread, while uncertainty in the scripted presentation is contemporaneously positively associated with the spread; the conclusion draws no investor prescription.
- **Source:** sec34_body_from_ledgers(2).tex, Outsider Reactions: The Bid-Ask Spread, reports the residual null and scripted-presentation association; _conclusion_body(1).tex, paragraph 4, states that no prescription is drawn from the correlational pattern.
- **Preparation route:** `appendix`

### 8. Could harder analyst questions, private meetings, leaks, or another information channel be producing the pre-announcement pattern rather than the disclosure bind you describe?

- **Most likely examiner:** Dutta
- **Prompted by:** Slide 2 attributes the trace to the CEO's disclosure bind, and slide 7 removes analyst-question uncertainty but the main deck omits the direct analyst-scrutiny analysis.
- **Damage if unprepared:** Moderate
- **Does the thesis answer it?** Partial
- **Best honest answer:** The direct cash-scrutiny test shows that the PRE1 coefficient survives scrutiny and its interaction, so cash-question volume does not account for this run-up. The thesis does not rule out private meetings, leaks, media transfer, or other unobserved channels, and it cannot distinguish compliance-constrained silence from strategic reticence.
- **Source:** sec34_body_from_ledgers(2).tex, Assessing the Analyst-Scrutiny Alternative, reports the scrutiny validation, joint model, and narrow conclusion; _conclusion_body(1).tex, limitations, states that compliance-constrained and strategic silence remain observationally equivalent; COMMITTEE_PROFILES.md links Dutta's private-meeting and insider-trading work to this concern.
- **Preparation route:** `appendix`

### 9. Your cash equation includes lagged cash with firm fixed effects. How do you address dynamic-panel bias, and does the timing result survive without the lag?

- **Most likely examiner:** Zhang
- **Prompted by:** Slide 9 reports a lagged-cash coefficient of 0.7547 in the matched timing model.
- **Damage if unprepared:** Moderate
- **Does the thesis answer it?** Yes
- **Best honest answer:** The thesis acknowledges Nickell bias and re-estimates the cash path with static firm fixed effects, removing the lag. The qualitative timing survives: cash does not fall at announcement and falls after completion, so the conclusion does not depend on the dynamic term.
- **Source:** sec34_body_from_ledgers(2).tex, Robustness: The Cash Result Without the Dynamic Term, explains the bias concern and reports the static fixed-effect timing check.
- **Preparation route:** `appendix`

### 10. You anchor the event clock on the first qualifying deal and define POST by completion. Do the main results survive repeat acquirers and withdrawn deals?

- **Most likely examiner:** either
- **Prompted by:** Slide 6 calls the focal sample the "First Cash-Deal Test," and slide 9 defines POST after completion.
- **Damage if unprepared:** Moderate
- **Does the thesis answer it?** Yes
- **Best honest answer:** Yes, the run-up, timing round trip, and cash concentration survive when all deals are stacked. Treating withdrawal as a resolution event also leaves the round trip in place, although the withdrawal check adds very little data and is supportive rather than decisive.
- **Source:** sec34_body_from_ledgers(2).tex, Robustness: Withdrawal as a Resolution Event and Robustness: The Main Findings Without the First-Deal Restriction, reports both checks and their limits.
- **Preparation route:** `appendix`

## Dutta-specific pressure points

Dutta's published work places him directly at the intersection of method of payment, M&A, private information channels, insider trading, and textual analysis. The most examiner-specific questions are ranks 1, 3, 4, 6, 8, and 10.

- **Deal knowledge and private channels:** Rank 1 tests whether the event clock actually observes the private-information state; rank 8 asks whether analyst scrutiny, private meetings, leaks, or other channels can mimic the pattern.
- **Method of payment:** Ranks 3, 4, and 6 test the mechanism, fragility, and fifty-percent classification behind the cash-versus-stock result.
- **M&A event design:** Rank 10 tests the first-deal restriction and treatment of withdrawals.

Attribution basis: `COMMITTEE_PROFILES.md` lists Dutta's work on payment method, private in-house meetings, insider trading around private meetings, M&A, and textual analysis.

## Zhang-specific pressure points

Zhang's published work and teaching place the strongest weight on alternative-data measurement, machine learning, disclosure, uncertainty in prices, and empirical identification. The most examiner-specific questions are ranks 2, 5, 7, and 9.

- **Measurement pipeline:** Rank 2 asks whether a fixed dictionary residual is a valid construct and whether generated-regressor uncertainty is handled.
- **Identification:** Rank 5 asks what the fixed-effect design identifies and what it cannot exclude.
- **Market relevance:** Rank 7 asks whether outside investors detect or price the signal.
- **Panel specification:** Rank 9 asks whether the cash timing result survives removal of the lagged dependent variable.

Attribution basis: `COMMITTEE_PROFILES.md` lists Zhang's work on alternative data, data analytics, disclosure, parameter uncertainty, and capital markets, with a quasi-experimental orientation.

## Questions with no good thesis answer

### 1. How do you know the acquisition was already under discussion and known to the CEO at the PRE1 call?

- **Why unanswerable:** The event clock observes announcement timing, not negotiation start, internal commitment, or the CEO's knowledge date.
- **Best concession:** I do not observe when negotiations began or when the CEO learned of the deal. PRE1 is an anticipatory window before announcement, so I interpret the result as a correlational pattern around later announced acquisitions, not as proof of the CEO's deal knowledge on every call.

### 2. What causal mechanism explains why the pattern concentrates in cash deals?

- **Why unanswerable:** The thesis motivates payment-method differences but does not identify stock-narrative management, deliberate cash accumulation, compliance-constrained silence, or strategic reticence as the cause.
- **Best concession:** The data establish concentration in cash deals, not the reason for it. The mechanism remains open and would require a different design.

### 3. Would the result survive different cash and stock thresholds or a continuous payment-share treatment?

- **Why unanswerable:** The cash and stock arms use a fifty-percent cutoff, and the thesis explicitly states that cutoff sensitivity is not tested.
- **Best concession:** I did not test alternative cutoffs or a continuous payment-share specification. That is a real limitation on how strongly the payment-method contrast can be generalized.

### 4. Has the uncertainty measure been validated against human coding, contextual embeddings, or a modern language model?

- **Why unanswerable:** The thesis uses a finance-specific fixed word list and residual decomposition, but the attached material reports no human-label or contextual-model validation.
- **Best concession:** No contextual or human-coded validation is reported. The measure is a transparent, replicable word-list operationalization, but it abstracts from context and should not be treated as a direct reading of what the CEO knows.

### 5. Do standard errors corrected for first-stage estimation uncertainty leave the main inference unchanged?

- **Why unanswerable:** Slide 7 acknowledges two-step estimation uncertainty, but the attached thesis excerpts do not provide a corrected-inference result.
- **Best concession:** The thesis treats generated-regressor uncertainty as a limitation and does not show a correction that settles whether the reported second-stage inference changes.

## Questions answered by thesis material omitted from the main deck

1. **Could analyst cash questioning produce the run-up?** The analyst-scrutiny analysis validates the scrutiny measure, enters scrutiny and its PRE1 interaction in the same model, and finds that the PRE1 coefficient survives while scrutiny and the interaction are null. This supports the narrow answer that cash-question volume does not account for this run-up. Source: `sec34_body_from_ledgers(2).tex`, Assessing the Analyst-Scrutiny Alternative.

2. **Does the outside market react to UncResCEO?** The post-call bid-ask analysis finds no association between UncResCEO and the spread across twelve specifications, while uncertainty in the scripted presentation is positively associated with the contemporaneous spread in several specifications. Source: `sec34_body_from_ledgers(2).tex`, Outsider Reactions: The Bid-Ask Spread.

3. **Does completion conditioning create the round trip?** Treating withdrawal as a resolution event leaves the uncertainty round trip in place, but the check adds only 89 firm-quarters and one firm, so it is supportive rather than decisive. Source: `sec34_body_from_ledgers(2).tex`, Robustness: Withdrawal as a Resolution Event.

4. **Does the cash timing result depend on the lagged dependent variable?** A static firm-fixed-effect specification without lagged cash preserves the timing pattern: no fall at announcement and a fall after completion. Source: `sec34_body_from_ledgers(2).tex`, Robustness: The Cash Result Without the Dynamic Term.

5. **Does the first-deal restriction drive the results?** Stacking all deals preserves the run-up and timing result and strengthens the pooled cash-minus-stock Wald difference from 0.0983 with p = .039 to 0.1056 with p about .013. Source: `sec34_body_from_ledgers(2).tex`, Robustness: The Main Findings Without the First-Deal Restriction.

6. **Is the residual associated with a deal next quarter or with cash payment in binary models?** The all-deals section reports linear-probability and logit forms. Higher residual uncertainty is associated with a deal next quarter, and among PRE1 deal observations it is associated with cash rather than stock in the pooled binary models; the cash-versus-stock linear-probability coefficient loses significance with firm and year-quarter fixed effects. Source: `sec34_body_from_ledgers(2).tex`, final robustness section.

## Avoidable invitations on the deck

### Slide 1: Title phrase "Undisclosed Cash Acquisitions"

- **Question it invites:** How do you know the deal was already undisclosed information known to the CEO at the call?
- **Why avoidable:** The empirical clock observes a call in the quarter before announcement, not the start of negotiations or the CEO's knowledge. Wording tied to "before announced cash acquisitions" would match the measured window more exactly.

### Slide 2: "The firm holds potentially material deal information that investors do not yet have."

- **Question it invites:** Where is the evidence that the firm and CEO held this information on each PRE1 call?
- **Why avoidable:** The sentence presents the latent disclosure state as observed. Conditional wording would preserve the framework while avoiding the implication that deal knowledge is measured.

### Slide 3: "Cash position persists until completion" and "Cash is paid"

- **Question it invites:** Are you claiming deliberate cash accumulation or a war-chest mechanism?
- **Why avoidable:** The thesis establishes timing, not deliberate accumulation. Wording in terms of observed coefficients, no PRE1-to-GAP decline and a GAP-to-POST decline, would avoid inviting a mechanism question.

### Slide 5: "No prior work occupies this exact cell."

- **Question it invites:** Can you prove that no paper has examined this exact combination?
- **Why avoidable:** The thesis itself uses the qualified phrase "To our knowledge." Restoring that qualifier would preserve the positioning claim and reduce an unnecessary absolute-literature challenge.

### Slide 7: "Raw CEO-answer uncertainty is residualized to isolate call-specific uncertainty."

- **Question it invites:** What validates the residual as true uncertainty rather than unexplained dictionary usage?
- **Why avoidable:** Calling it a residual proxy or an operational measure would preserve the construction without implying that the latent construct has been isolated.

### Slide 13: "a readable, anticipatory trace"

- **Question it invites:** Can an investor observe or trade on this signal in real time?
- **Why avoidable:** The thesis documents an in-sample association and draws no investor prescription. Wording that says "a pre-announcement sample pattern" would avoid suggesting demonstrated real-time predictability.

## Three questions the committee is most likely to ask

1. What evidence do you have that the CEO actually knew about, or was constrained by, this acquisition when the PRE1 earnings call occurred?
2. Why use a fixed uncertainty word list and residualization instead of a contextual language model, and how do you validate the measure?
3. Why is the run-up stronger for cash deals than for stock deals? What mechanism does your thesis actually establish?
