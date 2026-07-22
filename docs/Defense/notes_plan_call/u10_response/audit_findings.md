# U10 speaker-notes evidence audit

**Status:** COMPLETE  
**Slides audited:** 1–13  
**Spoken sentences classified:** 209  
**Findings:** 16 (8 major, 8 minor)  
**Present as is:** No.

The audit accepted the supplied deterministic gates for arithmetic and surface form. It tested meaning: whether each spoken sentence stays inside the thesis and locked-deck ceiling, whether cross-slide references reconcile, and whether null results are narrated as detection limits rather than absence.

## Inventory

| Filename | Bytes | Read in full | Pages |
|---|---:|:---:|---:|
| `PROMPT_2026-07-22_142032.md` | 4,268 | yes |  |
| `speaker_notes_evidence_audit_u10_inputs.zip` | 282,955 | yes |  |
| `DEFENSE_LEDGER.md` | 25,898 | yes |  |
| `rev22_deck.pdf` | 190,140 | yes | 13 |
| `rev22_slide_text.md` | 16,035 | yes |  |
| `SPEAKER_NOTES.md` | 12,507 | yes |  |
| `SPEAKER_NOTES_BUDGET.md` | 7,290 | yes |  |
| `thesis_flat.tex` | 162,954 | yes |  |
| `thesis_robustness_tables.tex` | 13,671 | yes |  |
| `thesis_tables.tex` | 39,922 | yes |  |
| `u01_claim_ledger.md` | 14,294 | yes |  |
| `u03_response.json` | 28,611 | yes |  |
| `u03_risk_report.md` | 22,704 | yes |  |
| `WEB_RESPONSE_SCHEMA.json` | 8,850 | yes |  |
| `WEB_REVIEW_REQUEST.json` | 7,640 | yes |  |

## Verdict

The scripts should not be presented unchanged. The most dangerous sentence is the untested non-tradability claim on slide 13. The most important structural gap is slide 2's claim that deflection is the “only move,” despite the thesis expressly allowing silence and non-answers. The most important internal consistency failure is slide 9: it applies null-versus-absence discipline to residual uncertainty and then violates it for cash.

## Findings

### U10-F01 — Slide 1 — MINOR

**Defective sentence:** “Not the prepared script: the unrehearsed part.”

**What is wrong:** Calling the Q&A “unrehearsed” is stronger than the thesis. The thesis distinguishes it from the prepared script but says it is less scripted and cannot be fully prepared, not that executives do no rehearsal or preparation.

**Source ceiling:** The Q&A is less scripted than prepared remarks and cannot be fully staged in advance.

**Supporting quote — `thesis_flat.tex`:** “its question-and-answer (Q&A) session is far less scripted than the prepared remarks that open it.”

**Replacement:** “Not the prepared script: the less-scripted Q&A.”

**Word delta:** +1 (7 → 8)

### U10-F02 — Slide 2 — MAJOR

**Defective sentence:** “In the United States there is no rule forcing it to announce merger talks.”

**What is wrong:** “No rule” is an absolute legal claim. The thesis deliberately states the narrower proposition that there is no general duty to disclose confidential merger talks.

**Source ceiling:** A firm generally may remain silent about confidential merger talks, but speaking triggers the duty not to mislead.

**Supporting quote — `thesis_flat.tex`:** “A firm has no general duty to disclose confidential merger talks, so staying silent is permitted; but once it speaks, it may not mislead”

**Replacement:** “In the United States there is generally no duty to announce confidential merger talks.”

**Word delta:** +0 (14 → 14)

### U10-F03 — Slide 2 — MAJOR

**Defective sentence:** “The only move left is to answer around the question.”

**What is wrong:** The sentence makes deflection the only available response and omits the ordinary option of declining to comment or remaining silent. That omission is especially exposed because the thesis itself treats silence and non-answers as deliberate, informative choices.

**Source ceiling:** The firm may stay silent. If it chooses to answer, it cannot confirm the undisclosed deal or make a misleading denial; deflection is one possible response, not the only one.

**Supporting quote — `thesis_flat.tex`:** “managers make deliberate disclosure-and-silence choices during conference calls, and ... a non-answer or a silence is itself informative to the market”

**Replacement:** “It may decline comment; if it answers, it cannot confirm or mislead.”

**Word delta:** +2 (10 → 12)

### U10-F04 — Slide 5 — MINOR

**Defective sentence:** “One distinction runs through all of it.”

**What is wrong:** The absolute claim that answers are not written in advance exceeds the construct boundary. Executives can prepare likely Q&A topics and talking points even though the exchange is not a prepared script.

**Source ceiling:** The analyst discussion is less scripted than the prepared presentation and cannot be fully prepared in advance.

**Supporting quote — `thesis_flat.tex`:** “the unscripted Q&A, the call segment managers cannot fully prepare in advance”

**Replacement:** “The answers are less scripted, and the answers are where I look.”

**Word delta:** +5 (7 → 12)

### U10-F05 — Slide 5 — MAJOR

**Defective sentence:** “What I did not find was work reading the uncertainty in a chief executive's unscripted answers, in the specific window when an acquisition is agreed but not yet announced.”

**What is wrong:** The sentence presents the observed pre-announcement quarter as a verified period in which the acquisition is already agreed. The data observe announcement-relative quarters, not agreement, negotiation, materiality, or CEO-knowledge onset.

**Source ceiling:** The study examines an announcement-anchored anticipatory window before the deal becomes public; actual negotiation or agreement onset is unobserved.

**Supporting quote — `rev22_slide_text.md`:** “The data mark the announcement date, not when negotiations began.”

**Replacement:** “What I did not find was work reading uncertainty in a chief executive's less-scripted answers in the announcement-anchored window before an acquisition becomes public.”

**Word delta:** -5 (29 → 24)

### U10-F06 — Slide 6 — MINOR

**Defective sentence:** “What survives tilts toward larger, better-covered firms with stable leadership.”

**What is wrong:** “Stable leadership” is not an established sample characteristic. The five-call rule establishes repeated observations for a CEO, not a validated construct of leadership stability.

**Source ceiling:** The residual sample skews toward larger, better-covered firms and requires CEOs with at least five calls.

**Supporting quote — `thesis_flat.tex`:** “We drop any CEO with fewer than five calls, because with so few calls we cannot estimate a speaking style”

**Replacement:** “What survives tilts toward larger, better-covered firms and CEOs with repeated calls.”

**Word delta:** +2 (10 → 12)

### U10-F07 — Slide 6 — MINOR

**Defective sentence:** “The smallest firms are not in here at all.”

**What is wrong:** The categorical statement that the smallest firms are entirely absent is not demonstrated by the thesis. Execucomp coverage is described as roughly the S&P 1500, and the thesis states a generalizability boundary rather than a verified zero count for every smallest-firm category.

**Source ceiling:** The sample may not extend to smaller firms outside the better-covered sample.

**Supporting quote — `thesis_flat.tex`:** “the sample ... approximately the S&P 1500, may not extend to ... the smaller firms outside it.”

**Replacement:** “Many smaller firms fall outside this sample.”

**Word delta:** -2 (9 → 7)

### U10-F08 — Slide 7 — MINOR

**Defective sentence:** “The problem is that people differ.”

**What is wrong:** The sentence creates a false dichotomy: persistent speaking style can affect the word count, but the thesis does not establish that such variation is purely personality and contains no information.

**Source ceiling:** Some observed uncertainty reflects persistent personal speaking style, which must be separated from call-varying language.

**Supporting quote — `thesis_flat.tex`:** “Some of the uncertainty in how a manager speaks is simply persistent personal style.”

**Replacement:** “That can reflect persistent style rather than call-specific information.”

**Word delta:** +3 (6 → 9)

### U10-F09 — Slide 7 — MINOR

**Defective sentence:** “If I compare across people, I am mostly measuring personality.”

**What is wrong:** “Mostly” is a quantitative dominance claim that the thesis does not estimate here. The comparison would mix persistent style with call-specific variation, but the share attributable to each is not established in the talk.

**Source ceiling:** Cross-person comparisons confound call-specific uncertainty with persistent executive speaking style.

**Supporting quote — `thesis_flat.tex`:** “Call language is no exception. ... [there is] a persistent, manager-specific component ... and a time-varying, call-level residual”

**Replacement:** “Comparing across people would mix call-specific uncertainty with persistent speaking style.”

**Word delta:** +1 (10 → 11)

### U10-F10 — Slide 7 — MAJOR

**Defective sentence:** “What remains is the residual: the part of this call's uncertainty that the speaker's usual style does not account for.”

**What is wrong:** The definition makes the residual sound style-only. The first-stage residual also removes prepared-presentation uncertainty, analyst-question uncertainty, call negativity, firm-performance variables, market returns, and year effects. Since the slide says everything downstream depends on the measure, this omission materially misdefines the estimand.

**Source ceiling:** UncResCEO is answer uncertainty left unexplained by CEO fixed effects, other call-language measures, firm-performance and return controls, and year effects.

**Supporting quote — `thesis_flat.tex`:** “It nets out two things at once: the persistent style ... and observable call-level factors -- the prepared-presentation uncertainty, the analysts' question uncertainty, call negativity, contemporaneous performance, and the year.”

**Replacement:** “What remains is answer uncertainty unexplained by modeled speaking style, call language, performance, returns, and year.”

**Word delta:** -4 (20 → 16)

### U10-F11 — Slide 9 — MAJOR

**Defective sentence:** “Cash does not fall at announcement.”

**What is wrong:** This repeats the exact null-versus-absence error the script correctly avoids for residual uncertainty. The PRE1-minus-GAP cash contrast is small and statistically insignificant; that supports no detected decline, not proof that cash does not fall.

**Source ceiling:** No statistically significant cash decline is detected between PRE1 and GAP; the significant cash decline occurs from GAP to POST.

**Supporting quote — `thesis_tables.tex`:** “Drop: PRE1 - GAP ... 0.0006 ... (0.0039); Drop: GAP - POST ... 0.0210 ... (0.0042)”

**Replacement:** “No cash decline is statistically detected at announcement.”

**Word delta:** +2 (6 → 8)

### U10-F12 — Slide 9 — MINOR

**Defective sentence:** “Information settles when it becomes public.”

**What is wrong:** The measured object is residual answer language, not “information” itself. The wording silently upgrades a language estimate into a statement about the latent information state.

**Source ceiling:** The residual language estimate declines after public announcement; the study does not directly measure whether information has settled.

**Supporting quote — `thesis_flat.tex`:** “the language moves with the information and settles when the information comes out.”

**Replacement:** “The residual language estimate falls when the deal becomes public.”

**Word delta:** +4 (6 → 10)

### U10-F13 — Slide 11 — MAJOR

**Defective sentence:** “This puts a residual uncertainty measure inside the specific window where a deal is agreed and not yet public.”

**What is wrong:** The contribution statement again treats agreement as observed inside the focal quarter. This conflicts with slide 12's correct admission that negotiation onset is unknown.

**Source ceiling:** The contribution places residual uncertainty in an announcement-anchored pre-public window, not in a verified post-agreement interval.

**Supporting quote — `u03_risk_report.md`:** “Event time is announcement-anchored. Negotiation onset, materiality onset, and CEO-knowledge onset are not observed”

**Replacement:** “This puts a residual uncertainty measure in the announcement-anchored quarter before a deal becomes public.”

**Word delta:** -4 (19 → 15)

### U10-F14 — Slide 12 — MINOR

**Defective sentence:** “The second is who it describes.”

**What is wrong:** The limitation slide repeats the unsupported “stable leadership” characterization. Repetition does not convert the five-call construction rule into evidence of leadership stability.

**Source ceiling:** The evidence describes larger, better-covered firms and CEOs observed on enough calls to estimate a speaking style.

**Supporting quote — `thesis_flat.tex`:** “the residual is estimated only for chief executives with enough calls to fix a speaking style, which skews the language sample toward larger, more heavily covered firms”

**Replacement:** “Larger, better-covered firms and CEOs with repeated calls, in one country and one period.”

**Word delta:** +8 (6 → 14)

### U10-F15 — Slide 13 — MAJOR

**Defective sentence:** “When an acquisition moves from private to public, the unscripted part of the earnings call carries a trace of it, and that trace is readable.”

**What is wrong:** The closing converts an aggregate, hedged empirical interpretation into a categorical statement about what happens when an acquisition moves public. It drops the thesis's load-bearing “patterns suggest” qualifier and can be heard as a per-deal trace.

**Source ceiling:** Taken together, the estimated patterns suggest an aggregate, readable anticipatory language trace around the private-to-public transition.

**Supporting quote — `thesis_flat.tex`:** “Taken together, these patterns suggest that the unscripted language of earnings calls carries a readable, anticipatory trace of a deal's passage from private to public”

**Replacement:** “These patterns suggest that less-scripted earnings-call answers carry a readable trace around a deal's move from private to public.”

**Word delta:** -6 (25 → 19)

### U10-F16 — Slide 13 — MAJOR

**Defective sentence:** “It is not a mechanism, and it is not something anyone could trade on.”

**What is wrong:** The thesis does not test whether anyone could trade on the pattern. “No prescription” and a correlational design do not establish non-tradability; the sentence makes an impossibility claim beyond the evidence.

**Source ceiling:** The thesis offers no investor prescription and does not evaluate the pattern as a tradable signal.

**Supporting quote — `thesis_flat.tex`:** “We draw no prescription for investors, managers, or regulators ... the contribution is to characterize a regularity, not to recommend acting on it.”

**Replacement:** “It is not a mechanism, and it is not tested here as a tradable signal.”

**Word delta:** +1 (14 → 15)


## Cross-slide checks

| From slide | Cross-slide claim | Holds? | Explanation |
|---:|---|:---:|---|
| 9 | The PRE1 rise is qualitatively the same pattern as slide 8 but is a different estimate from a matched sample and specification. | yes | Sentences 9.9–9.10 explicitly correct the prior error: they say “same rise,” not same coefficient, and identify the 28,102 matched firm-quarter sample. |
| 9 | The detection-versus-absence discipline applied to residual uncertainty is also applied to cash. | no | Slide 9 correctly says a nonsignificant language estimate is a failure to detect, then says categorically that cash “does not fall” despite a nonsignificant PRE1–GAP cash contrast. This is U10-F11. |
| 11 | The focal quarter is a known interval after agreement and before publicity. | no | Slide 11 says the deal is agreed in the window, while slide 12 correctly says negotiation onset is unknown and the quarter is only an announcement-anchored proxy. This is U10-F13. |
| 10 | The cash-versus-stock conclusion is based on a direct pooled difference rather than significance on one side only. | yes | The narration accurately distinguishes the direct Wald test from comparing separate significance labels and preserves the “concentration, not cash-only” ceiling. |
| 12 | The stock comparison limitation refers back to the payment-choice cautions on slide 3. | yes | Slide 3 says payment choice is nonrandom and the comparison motivates rather than identifies; slide 12's reference is consistent with that boundary. |
| 13 | The closing detection sentence is consistent with slide 9's null-versus-equivalence boundary. | yes | “No longer detectable” states a statistical detection boundary rather than asserting that the underlying trace is absent or exactly zero. |
| 13 | The closing cash-versus-stock statement stays inside slide 10's direct-comparison result. | yes | “Stronger for cash deals than for stock deals” is supported by the significant direct cash-minus-stock Wald contrast and does not say cash-only. |

## Hunt target: slide 13 closing

**Survives the challenge:** Yes.

Yes. “It is no longer detectable” is already the safe statistical form: it describes what the design fails to distinguish from baseline after announcement and does not equate nondetection with absence. An examiner can still ask about power or equivalence, but the sentence itself concedes that boundary. The problem in the closing is the separate tradability sentence, not this one.

Optional same-length tightening: “It is not statistically detectable after the deal becomes public.”

## Hunt target: slide 2 no-comment policy

**Defeats the whole argument:** No.  
**Classification:** narration hole.

A standing no-comment policy defeats the script's claim that deflection is the only available move, but it does not defeat the empirical premise. The thesis itself allows silence and strategic reticence, treats a non-answer as informative, and does not require a legal duty to answer every question. The prediction is best understood conditionally: when the firm proceeds with the routine call and the executive engages, constrained or strategic withholding may appear in answer language. The study tests an aggregate language pattern, not whether every CEO is forced to answer a deal rumor.

**What to say if asked:** “A no-comment policy is a real alternative, so I should not say deflection is the only move. The firm may remain silent or refuse the premise. My prediction is conditional on the routine call continuing and the executive engaging: once the firm speaks, it cannot confirm the confidential deal or mislead, and silence or a non-answer is itself part of the withholding behavior. The evidence tests the aggregate language pattern, not a legal necessity to answer every rumor.”

## Explicit answers

### Q1

Sentence 13.7 is most likely to lose marks: “It is not a mechanism, and it is not something anyone could trade on.” The thesis never tests tradability, so an examiner can defeat the claim with one question—where is that test? Replace the second clause with “it is not tested here as a tradable signal.”

### Q2

Yes. The notes say, “It is not a mechanism, and it is not something anyone could trade on.” The thesis says only, “We draw no prescription for investors, managers, or regulators ... the contribution is to characterize a regularity, not to recommend acting on it.” No prescription is not evidence of non-tradability. The categorical smallest-firm and stable-leadership statements also exceed the supplied source.

### Q3

Yes. Slide 11 says the measure sits in a window “where a deal is agreed and not yet public,” but slide 12 correctly says the data do not reveal when talks began and PRE1 is only a proxy window. Slide 9 also contradicts its own detection discipline: it refuses to infer absence from a nonsignificant language estimate, then says cash “does not fall” on a nonsignificant cash contrast. The slide 9 versus slide 8 estimate identity, slide 10 direct comparison, and slide 13 detection wording otherwise reconcile.

### Q4

Yes. “It is no longer detectable once the deal is public” survives because it states a detection result, not that the underlying phenomenon is absent or exactly zero. The same-length, even more explicit form is: “It is not statistically detectable after the deal becomes public.”

### Q5

No. A no-comment policy breaks slide 2's “only move” narration, not the whole empirical argument. The firm may remain silent, and the thesis explicitly treats silence and non-answers as informative choices. The defensible premise is conditional: when the call proceeds and the executive engages, the firm cannot confirm the confidential deal or make a misleading denial, and the resulting withholding may appear in answer language.

### Q6

Yes, the full attenuation and PRE2 rebuttals should remain in Q&A. The podium already uses the correct minimal forms—PRE2 is “no detected elevation,” and PRE1 is a proxy because onset is unobserved. The longer bias-direction and power arguments would consume the limitation slide and invite side disputes before anyone raises them. One podium correction is still required: cash must also be described as “no detected decline” at announcement.

### Q7

The defensive voice is strongest in “this is the one I would push on if I were you,” “Be careful how I say,” “I would rather state it now than defend it later,” and “I will not claim one.” Some defense is useful because it marks real inferential ceilings, but the examiner-role play and anticipated combat make the presenter sound as though he is litigating objections before explaining the evidence. Keep the substantive boundaries; cut the adversarial framing first when rehearsing for time.

### Q8

Delete exactly the 100 words in sentences 8.3, 8.4, and 8.12–8.17: the spoken coefficient/standard-error definitions, the confidence-interval explanation and derivation, and the sample-count sentence. The slide already displays those items, while the remaining script still states the result, p-value, effect size, clustering, within-firm comparison, and causal boundary. What breaks is oral provenance for the derived interval and verbal repetition of the estimate, standard error, and sample size; nothing load-bearing in the substantive argument breaks.


## Exact 100-word cut

Delete sentences **8.3, 8.4, and 8.12–8.17**. Under the audit tokenizer, the deleted text is exactly 100 words:

> The coefficient, which is the estimated size of that shift, is plus 0.0461. Its standard error is 0.0172, and the standard error is how uncertain the estimate itself is. One caution on the bar you can see on the slide. That is an approximate 95 percent range, and a confidence interval is a plausible range around the estimate. The slide says derived, and it means it. I computed it from the estimate and its standard error. The thesis prints the estimate and the standard error, not the range. The sample is 27,622 firm-quarters from 1,248 firms.

The visible slide retains the estimate, standard error, interval, sample, and clustering. The remaining narration retains the p-value, effect size, within-firm comparison, and causal boundary. What is lost is oral repetition and interval provenance, not a load-bearing substantive claim.

## Clean dimensions

- **Slide 9 versus slide 8 estimate identity:** Every sentence referring back to slide 8 was checked against MA1 and MA2. The notes now correctly say the qualitative rise is similar but the coefficient, sample, and specification are different.
- **Cash-versus-stock inferential form:** Slides 3, 4, 10, 12, and 13 were checked for payment-choice endogeneity, separate-significance fallacy, direct Wald testing, and cash-only wording. Apart from the unrelated sample-language findings, the direct-comparison narrative stays within the thesis.
- **Causal and mechanism boundaries:** All thirteen scripts were searched sentence by sentence for causal verbs, mechanism claims, and war-chest claims. The talk repeatedly states descriptive scope and no identified mechanism; no war-chest mechanism is introduced.
- **Slide 13 detection-versus-absence wording:** The exact closing sentence was compared with the PRE1–GAP result, the prior examiner audit, and every nearby paraphrase. It says nondetection rather than disappearance or equivalence and is clean.
- **Appendix-only analysis leakage:** Every substantive sentence was checked for robustness, scrutiny, bid-ask, withdrawal, stacked-deal, logit, or other appendix results not displayed in the main deck. None is introduced as a podium result.
- **Numerical surface:** Not re-audited by design. The request states that all deck numerals, coefficient/standard-error pairs, and spoken-number-to-slide traces already passed deterministic checks; this audit checked only what each number was said to mean.

## Census files

`sentence_census.csv` contains all 209 spoken sentences, one row per sentence, with primary classification, source basis, support status, and finding linkage. `safe_wordings.csv` contains every defective sentence, its replacement, and the measured word delta.
