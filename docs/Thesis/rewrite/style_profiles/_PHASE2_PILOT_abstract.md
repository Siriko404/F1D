# Phase-2 REWRITE — pilot on the Abstract (2026-06-24)

**Status: PROPOSED diff. NOT applied to the thesis. Awaiting Sina's ratification.**

## Locked design (advisor-shaped 2026-06-24)
- Unit: **constrained edit of flagged sentences** (splits allowed; merging across propositions + reordering forbidden — spine-freeze already bans reordering).
- Rewriter input = the sentence + its proposition + protected numbers/phrases + the *named* anti-pattern. Output = same proposition, anti-pattern removed, nothing else moved.
- **Number-gate (mechanical):** every `number_audit` value survives verbatim. Abstract's only number = "2002 to 2018".
- **Guardrail-gate (Sina's eye for now):** guardrails are concept-notes, not exact strings, until the guardrail-completeness pass. Checked by eye here.
- **Meaning gate = Sina.** Any LLM meaning-check is advisory only.
- Review batched per paragraph (this is 1 unit).
- Pilot first; scale only after the cadence is right + guardrail-completeness pass done.

## Protected items for the abstract
- **Number:** `2002 to 2018` (verbatim).
- **No** citations / author names / notation / coefficients (abstract convention).
- **Guardrails:** C1 lead with "indistinguishable from zero" (never "falls/unwound"); C6 "formal pooled test" (not Gelman-Stern), concentration-not-specificity; C4 = does not account for THIS run-up; bid-ask = two per-component facts, not a tested difference; ceiling implicit ("correlational … not a tested mechanism").

---

## Sentence-by-sentence diff

**S1** · anti-pattern: 34-word two-clause; "a window into" metaphor; "chief executive"→CEO
- OLD: Firms host quarterly earnings calls and field analysts' unscripted questions, and the language a chief executive uses in answering is increasingly read as a window into what they know but have not yet disclosed.
- NEW: Firms hold earnings calls every quarter, where analysts ask unscripted questions. How a CEO answers is increasingly read as a signal of what the firm knows but has not yet disclosed.

**S2** · anti-pattern: 3 stacked subordinate clauses; "the one development that matters" drama; passive "has not been characterized"
- OLD: When a firm is privately committed to an acquisition it has not yet announced, the executive holds the routine call unable to confirm or deny the one development that matters, and whether the spoken record tracks that withholding has not been characterized.
- NEW: Sometimes a firm has privately agreed to an acquisition but not yet announced it. The CEO must still hold the routine call, yet cannot confirm or deny the deal. Whether their words reveal this withholding has not been studied.

**S3** · already plain · PROTECTED number "2002 to 2018"
- OLD: We study United States public firms' earnings-call transcripts and acquisition records from 2002 to 2018.
- NEW: We study earnings-call transcripts and acquisition records for United States public firms from 2002 to 2018. *(unchanged in substance; number preserved)*

**S4** · anti-pattern: compound-noun pile-up "residual measure of chief-executive question-and-answer uncertainty"; mid-sentence appositive · PROTECTED: residual concept, persistent-style removal, cash-vs-stock placebo
- OLD: From this language we construct a residual measure of chief-executive question-and-answer uncertainty, the component that remains once each executive's persistent speaking style is removed, and we track it around firms' cash acquisitions against stock acquisitions as a placebo.
- NEW: From this language we build a measure of how uncertain the CEO sounds when answering questions. We remove each CEO's usual speaking style, keeping only what changes from one call to the next. We then track this measure around cash acquisitions, using stock acquisitions as a placebo comparison.
- ⚠️ FLAG: drops the literal word "residual" (replaced by its plain definition "what changes from one call to the next"). Abstract names the measure descriptively only, so this is allowed — but it's a judgment call. Keep "residual" if you prefer the link to UncResCEO visible.

**S5** · light · C2 · PROTECTED: cash-before / no-stock-rise
- OLD: This residual uncertainty is elevated in the quarter before a cash acquisition, relative to the firm's own other quarters, with no comparable rise before stock acquisitions.
- NEW: This uncertainty rises in the quarter before a cash acquisition, compared with the same firm's other quarters. There is no similar rise before stock acquisitions.

**S6** · C1 · GUARDRAIL: lead "indistinguishable from zero", never "falls/unwound"
- OLD: It becomes indistinguishable from zero once the deal is announced, even before completion, while the cash that funds the purchase persists on the balance sheet until the deal closes.
- NEW: Once the deal is announced, this uncertainty is indistinguishable from zero — even before the deal closes. The cash that funds the purchase, by contrast, stays on the balance sheet until closing.

**S7** · C6 · GUARDRAIL: "formal pooled test", concentration-not-specificity
- OLD: The elevation concentrates in cash acquisitions rather than stock acquisitions, a difference that survives a formal pooled test.
- NEW: This rise is concentrated in cash acquisitions, not stock — a difference that holds up under a formal pooled test.

**S8** · light · C4
- OLD: This pattern is not explained by analysts devoting more of the call to cash questions.
- NEW: This pattern is not explained by analysts simply asking more cash questions on the call.

**S9** · anti-pattern: nominalization "relating to the outside information environment in different ways"; appositive; "consistent with" rider · PROTECTED (P1-i): residual unrelated to spread; presentation positive; two facts, not a tested difference
- OLD: The residual is also unrelated to the firm's post-call bid-ask spread, a standard gauge of information asymmetry, while the scripted presentation is positively associated with it, consistent with the two parts of the call relating to the outside information environment in different ways.
- NEW: Our measure is also unrelated to the firm's bid-ask spread after the call — a standard gauge of how unevenly information is spread among investors. The scripted presentation, by contrast, is positively linked to that spread. The two parts of the call seem to reach the outside market in different ways.

**S10** · anti-pattern: metaphor "tracking the deal's passage"; nominalization · GUARDRAIL: ceiling "correlational … not a tested mechanism"
- OLD: We read these patterns as call language tracking the deal's passage from private to public, a within-firm correlational regularity rather than a tested mechanism.
- NEW: We read these patterns as the call's language following a deal as it moves from private to public. This is a within-firm correlation, not a tested mechanism.

---

## Gate results
- **Number-gate:** ✅ "2002 to 2018" preserved verbatim (S3). No coefficient introduced.
- **Guardrail (eye):** ✅ C1 leads "indistinguishable from zero" (S6); C6 "formal pooled test" (S7); C4 = this run-up (S8); bid-ask = two facts (S9); ceiling "correlation, not a tested mechanism" (S10); no citations/names/notation.
- **Open judgment for Sina:** the S4 "residual" wording (see ⚠️).

## Length
OLD abstract = 10 sentences. NEW = ~17 (splits). Plainer, shorter sentences; same content.
