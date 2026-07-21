# Deck audit register

One place for every finding, whoever found it. Updated as passes return.

## Pass status

| Pass | Exchange | State | Exceptions |
|---|---|---|---|
| Numbers | 2026-07-21_153445_deck_audit_numbers | COMPLETE | 0 |
| Claims | 2026-07-21_154520_deck_audit_claims | COMPLETE | 4 |
| Visual | 2026-07-21_155031_deck_audit_visual | INCOMPLETE, content accepted | 0 |
| Language and citations | 2026-07-21_155539_deck_audit_language | COMPLETE | 9 |
| Examiner exposure | 2026-07-21_155943_deck_audit_examiner | COMPLETE | 10 questions |

The visual exchange validates INCOMPLETE for a delivery-format reason only: the
returned main JSON listed itself inside its own `artifacts_manifest`, which no
file can hash correctly. Its content is complete and is accepted. The companion
now names that failure specifically instead of calling it a hash mismatch.

## Verdict

No blocker. No major defect in the deck itself.

Numbers are clean, verified twice. The visual pass found nothing across all 13
pages. No slide asserts causation, claims an established mechanism, or reads the
payment-method result as strict cash specificity. Every citation exists, carries
the right year, and is used for the proposition the thesis uses it for.

What remains is a short list of small wording defects, and one substantial
exposure in the question period that is not a deck problem at all.

## The one thing that matters most

An examiner can ask: **what evidence is there that the CEO knew about the
acquisition at the time of the pre-announcement call?** The event clock is
anchored on the announcement date, not on when negotiations began or when the
chief executive learned of the deal. The thesis has no answer, because it has no
data on either. This is the highest-damage question the deck will draw, it is
entirely fair, and the only defensible response is a clean concession.

Nothing on the deck should change because of it. It belongs in preparation.

## Numbers: closed clean

136 substantive items across slides 6 to 13, zero exceptions. Verified twice and
independently: mechanically by the operator against `_tables_from_bible.tex`, and
by the numbers pass against the same tables plus the main-analysis prose.

Operator spot-checks that agreed: slide 10 against `tab:empire_drop_placebo` cell
by cell, all eight coefficients and both sample sizes; the slide 8 interval
`0.0461 +/- 1.96 x 0.0172 = [0.012, 0.080]`; the effect ratio
`0.0461 / 0.3010 = 15.3%`; the slide 10 Wald interval `[0.005, 0.192]`.

## Chart geometry: closed clean, measured not eyeballed

This was the audit's one real hole. The numbers pass claimed the geometry was
clean but judged it from a rendered image, which is exactly what that channel
cannot do reliably, and the visual pass was deliberately forbidden from
measuring. So nobody had actually checked that a plotted point sits where its
coefficient says it should.

Measured directly from the PDF drawing objects. For each panel the four dot
centres were fitted against their four printed coefficients and the residual from
a straight line recorded.

| Panel | Scale | Worst deviation from linear |
|---|---|---|
| Slide 8, pre-announcement estimate | 313.84 pt per unit | 0.01 pt |
| Slide 9, residual CEO uncertainty | 428.0 pt per unit | 0.003 pt |
| Slide 9, cash ratio | 1712.1 pt per unit | 0.000 pt |
| Slide 10, cash acquirers | 269.8 pt per unit | 0.005 pt |
| Slide 10, stock acquirers | 269.8 pt per unit | 0.004 pt |

Every point sits within a hundredth of a point of where its coefficient puts it.
At 300 dpi that is under a twentieth of a pixel.

Slide 8 was measured against the drawn axis ticks at y = 245.43, 339.89, and
434.36, which are symmetric to 0.01 pt. Anchoring instead to the centres of the
tick *labels* produces a spurious 2 pt error, because text centres sit below the
rules they annotate. That trap is worth recording: it would have been reported as
a real defect by anyone measuring from the rendered image. The whisker on the
same slide runs from 314.79 to 336.13, against 314.84 to 336.00 for the exact
95% interval, so both endpoints land within 0.13 pt.

Two structural results fall out of the scales:

- **Slide 10's two panels are on an identical scale**, 269.8 against 269.8, a
  difference of 0.00%. The slide invites the eye to compare the cash and stock
  traces directly, and that comparison is honest.
- **Slide 9's two panels are on deliberately different scales**, and the ratio is
  exactly 4.00. The uncertainty axis spans 0.16 units and the cash axis spans
  0.04 across the same physical height. Different units are therefore never
  compared by height, which is what the ledger's own lesson requires.

## Findings

### Operator findings

**OPS-01. Slide 5 states a universal negative that the thesis hedges.**
Severity `note`. Not a deck defect; route to examiner preparation.
The deck reads `No prior work occupies this exact cell.` The thesis reads
`To our knowledge no prior work reads uncertainty language in the unscripted
question-and-answer session in the anticipatory window before a withheld deal;
we offer this as a positioning claim about where the contribution sits, not as a
tested mechanism` (`_intro_body.tex`). The deck drops `To our knowledge`, but it
prints the claim under a `POSITIONING CLAIM` header, which reproduces the
thesis's own framing. The exposure is the question, not the slide.

**OPS-02. Event-stage charts connect categorical stages with a line.**
Severity `note`. Slides 9 and 10. The ledger lesson bans letting a graphic
*silently* imply a continuous equal-duration series. It is not silent here:
stages are individually labelled and defined, `POST` is marked `<= 4 qtrs`, and
dashed separators mark announcement and completion. Recorded so a later pass
flagging it does not read as new.

**OPS-04. Slide 12 uses two dash-based sentence constructions.**
Severity `minor`, but it is the one objective violation of an explicit rule.
The ledger states: avoid em dashes and dash-based sentence constructions in
audience-facing wording. Slide 12 reads `A within-firm regularity around
disclosure - no more, and no less.` and `WHAT IT DOES NOT SHOW - AND WHERE IT
MAY NOT CARRY`. Character scan confirms the deck contains no em dash and no en
dash anywhere; the only U+2212 uses are mathematical and correct. The fix is a
pure text edit with no reflow risk: `around disclosure, no more and no less`.
**This is a decision for Sina at merge:** does the no-dash rule justify a
surgical reopen of a locked slide, or does it ship as is? Do not decide it here.

**OPS-05. Slide 5 mixes ampersands and the word `and` in the same citations.**
Severity `minor`. The body prints `Ragozzino & Reuer 2024` and `Keown &
Pinkerton 1981`; the source footer on the same slide prints `Ragozzino and Reuer
(2024)` and `Keown and Pinkerton (1981)`. The thesis uses `and`.

**OPS-06. Slide 4 uses the event-stage names before slide 9 defines them.**
Severity `minor`. Slide 4 prints `Uncertainty and cash = PRE1 + GAP + POST`.
`PRE1`, `GAP`, and `POST` are not defined until slide 9. Slide 3 uses the plain
words `UNANNOUNCED`, `ANNOUNCEMENT`, and `COMPLETION`, not these tokens. Slide 4
does gloss the intent immediately below: `uncertainty should drop from PRE1 to
GAP; cash should drop only after completion`.

**OPS-07. Citations verified complete and correct.** Closed clean.
All twelve references printed on the deck exist in the thesis reference list with
matching years: Verrecchia 1983, Dye 1985, Basic 1988, Rule 10b-5, Matsumoto et
al. 2011, Hollander et al. 2010, Harford 1999, Shleifer and Vishny 2003, Louis
2004, Thewissen et al. 2024, Ragozzino and Reuer 2024, Keown and Pinkerton 1981.
An earlier suspicion that Shleifer and Vishny was uncited was a false alarm
caused by the operator's search pattern; the entry exists under the key
`shleifer_vishny2003`. Rule 10b-5 is printed without a year on the deck and
carries 2014 in the reference list, which is not a mismatch.

**OPS-03. The ledger disagrees with the shipped deck about section labels.**
Severity `note`. Not a deck defect. `visual_system.slide_8_inheritance` says to
use `MESSAGE` as the section label; the shipped slide 8 says `FINDING 1`. The
approved artifact is the authority and the inheritance note is pre-production.
Do not edit the slide to match the ledger.

### Findings returned by the passes

Candidate edits, all small. None forces a reopen on its own.

**CLM-002. Slide 13 states the closing claim more flatly than the thesis.**
Severity `minor`. Found by the claims pass; the operator missed it.
The deck reads `Unscripted CEO Q&A carries a readable, anticipatory trace of a
deal's passage from private to public.` The thesis reads `Taken together, these
patterns suggest that the unscripted language of earnings calls carries a
readable, anticipatory trace...` (`_conclusion_body.tex`). The operator had
checked this sentence and confirmed the phrase matched word for word, but missed
that the deck drops the framing verb `suggest`. It is the last sentence the
committee reads, and it is the deck's strongest form of its own claim.

**L-005. The control set is labelled differently on slide 8 than on slides 9
and 10.** Severity `minor`. Slide 8 says `size` and `dividends`; slides 9 and 10
say `ln(assets)` and `dividend indicator`. Same variables, three different names.
An examiner comparing specifications could reasonably ask whether the controls
changed between analyses.

**L-008. Slide 9 on the lag: downgraded to `note` after checking the source.**
The language pass called `Cash adds its own lag: 0.7547` technically wrong. It is
compressed, not wrong. The thesis says `the cash equation carries a
partial-adjustment lag` and, for this analysis, `The cash leg ... uses the same
well-behaved partial-adjustment specification as MA1, with a lagged-cash
coefficient of 0.7547`. On the deck, `Cash` names the cash leg, not the variable.
This was the only finding in the audit asserting the deck says something
technically false, and it does not survive the source.

**L-009. Slide 11 compares unlike things.** Severity `minor`.
`concentrates in cash acquisitions rather than stock` compares acquisitions with
stock. The thesis compares cash acquisitions with stock acquisitions.

**L-002. Slide 2 lists legal authority among academic papers.** Severity `minor`.
The footer runs `Verrecchia (1983); Dye (1985); Basic (1988); Rule 10b-5;
Matsumoto et al. (2011); Hollander et al. (2010)` as one undifferentiated list,
and shortens a court decision to an author-style `Basic (1988)`. The claim that
a firm may stay silent but may not mislead rests on the legal authority, not on
the disclosure-theory papers.

**Downgraded on review.** The claims pass rated slide 5 `major` (CLM-001, the
same finding as OPS-01) and slide 13's omitted fragility qualifier `minor`
(CLM-003). Both are recorded as `note`. Slide 5 prints the claim under a
`POSITIONING CLAIM` header, which carries the thesis's own framing. Slide 13
omits a final boundary note by an explicit approved decision, D035, which the
pass could not see because the ledger was deliberately withheld from it.

The language pass also flagged `SD`, `SE`, `CI`, and `ns` as undefined
(L-004, L-006). Recorded as `note`. The audience is four finance and accounting
academics.

## Cross-cutting concerns routed to the examiner pass

Questions a defensible deck still has to answer. None is a deck defect. They are
collected here so five passes do not each surface them separately.

| Id | Concern | Origin | Found by the blind examiner pass? |
|---|---|---|---|
| X-01 | How do you know no prior work occupies this cell? | OPS-01, slide 5 | Yes, as an avoidable invitation on slide 5 |
| X-02 | The fifty-percent cash/stock cutoff, whose sensitivity the thesis says it does not test | `_conclusion_body.tex` | Yes, ranked 6 and listed as unanswerable |
| X-03 | Why does the stock panel hold more firm-quarters than the cash panel? | slide 10 | **No** |
| X-04 | Why is the sample cut at 2018? | prior session ledger | **No** |
| X-05 | How is the CEO speaker identified in the transcripts? | prior session ledger | **No** |
| X-06 | Why a finance word list rather than a modern language model? | committee profiles | Yes, ranked 2 and in the top three |
| X-07 | Is 15.3% of a residual standard deviation economically meaningful? | slide 8 | **No** |

**The union matters.** The examiner pass was run blind, without this list, so that
its coverage would be independent evidence rather than an echo. The price of that
choice is that four concerns here did not reappear in its output. Blind
independence buys confidence in what it *did* find; it buys nothing about what it
missed. The examiner surface is therefore the union of its ten ranked questions,
its five unanswerable ones, and X-03, X-04, X-05, and X-07 above. None of the
four is a deck defect and none is hard to answer, except X-04, where the thesis
states no rationale at all and a concession is the only honest route.

Answers already established for two of them: X-03 is answered by the notes to
`tab:empire_drop_placebo`, which state that each arm is estimated on its own
complete-case universe. X-07 is answered by the thesis's own wording, which calls
the magnitudes `material but modest`.

### The examiner pass's own highest-damage finding, which this list did not have

The single most dangerous question is not on the list above and the operator did
not anticipate it: **what evidence is there that the CEO knew about the
acquisition at the pre-announcement call?** The event clock is anchored on the
announcement date. The thesis observes neither when negotiations began nor when
the chief executive learned of the deal. It is unanswerable and the only route is
a clean concession. That question alone justified running the pass blind.
