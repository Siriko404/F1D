# Phase-2 REWRITE — Abstract (subsection 1 of 16)

**Status: PROPOSED. NOT applied to thesis.** Jargon KEPT (decision 7). Clone target: `_rewrite_working/section_abstract_paragraph_ledger.json`.
Spine: `section_abstract_paragraph_ledger.json` (9 props a..i). Analysis: `abstract_profile.json` (15 findings).

---

## Sentence-by-sentence (OLD → NEW), anti-pattern each fixes — JARGON KEPT

**S1** · prop a · fixes a2-f1 (34-word two-clause), a1-f2 ("a window into" metaphor), a2-f4 (chief executive→CEO)
- OLD: Firms host quarterly earnings calls and field analysts' unscripted questions, and the language a chief executive uses in answering is increasingly read as a window into what they know but have not yet disclosed.
- NEW: Firms hold earnings calls every quarter and take unscripted questions from analysts. How a CEO answers is increasingly read as a signal of what the CEO knows but has not yet disclosed.
- (advisor catch: keeps "the CEO knows", not "the firm knows" — preserves manager-as-knower.)

**S2** · prop b · fixes a3-f2 (3 stacked clauses), a1-f4 (dramatized "the one development that matters"), a2-f5 (abstract passive gap)
- OLD: When a firm is privately committed to an acquisition it has not yet announced, the executive holds the routine call unable to confirm or deny the one development that matters, and whether the spoken record tracks that withholding has not been characterized.
- NEW: Sometimes a firm has privately agreed to an acquisition but not yet announced it. The CEO must still hold the routine call, but cannot confirm or deny the deal. Whether the words on these calls track that withholding has not been studied.

**S3** · prop c · already plain · PROTECTED number "2002 to 2018"
- OLD: We study United States public firms' earnings-call transcripts and acquisition records from 2002 to 2018.
- NEW: We study earnings-call transcripts and acquisition records for United States public firms from 2002 to 2018.

**S4** · prop d · fixes a2-f3 (compound-noun pile-up), a1-f5/a3-f3 (dense inline appositive) · JARGON KEPT: "residual measure", "persistent speaking style", "placebo"
- OLD: From this language we construct a residual measure of chief-executive question-and-answer uncertainty, the component that remains once each executive's persistent speaking style is removed, and we track it around firms' cash acquisitions against stock acquisitions as a placebo.
- NEW: From this language we build a residual measure of how uncertain a CEO sounds when answering questions: we strip out each CEO's persistent speaking style and keep only what changes from one call to the next. We then track this measure around firms' cash acquisitions, using stock acquisitions as a placebo.

**S5** · prop e (C2 run-up) · fixes a2-f1 (length), adds short beat (a2-f2)
- OLD: This residual uncertainty is elevated in the quarter before a cash acquisition, relative to the firm's own other quarters, with no comparable rise before stock acquisitions.
- NEW: This residual uncertainty rises in the quarter before a cash acquisition, compared with the same firm's other quarters. There is no similar rise before stock acquisitions.

**S6** · prop f (C1, strongest) · GUARDRAIL C1: lead "indistinguishable from zero"; NEVER "falls/unwound/reverses"
- OLD: It becomes indistinguishable from zero once the deal is announced, even before completion, while the cash that funds the purchase persists on the balance sheet until the deal closes.
- NEW: Once the deal is announced, this uncertainty is indistinguishable from zero, even before the deal closes. The cash that funds the purchase, by contrast, stays on the balance sheet until closing.

**S7** · prop g (C6) · GUARDRAIL C6: "formal pooled test"; concentration-not-specificity
- OLD: The elevation concentrates in cash acquisitions rather than stock acquisitions, a difference that survives a formal pooled test.
- NEW: This rise is concentrated in cash deals rather than stock, a difference that holds up in a formal pooled test.

**S8** · prop h-part1 (C4 rule-out) · GUARDRAIL C4: does not account for THIS run-up; never "scrutiny never matters"
- OLD: This pattern is not explained by analysts devoting more of the call to cash questions.
- NEW: This pattern is not explained by analysts simply spending more of the call on cash questions.

**S9** · prop i (bid-ask) · HIGHEST-RISK · fixes a3-f5 (bundled), a1-f8 (vague "in different ways") · JARGON KEPT: "residual", "post-call bid-ask spread", "information asymmetry" · GUARDRAIL: two per-component facts, NEVER a tested between-component difference
- OLD: The residual is also unrelated to the firm's post-call bid-ask spread, a standard gauge of information asymmetry, while the scripted presentation is positively associated with it, consistent with the two parts of the call relating to the outside information environment in different ways.
- NEW: The residual is also unrelated to the firm's post-call bid-ask spread, a standard gauge of information asymmetry. The scripted presentation, by contrast, is positively related to that spread. The two parts of the call appear to reach the outside market in different ways.

**S10** · prop h-part2 (contribution + ceiling) · fixes a1-f6 ("tracking the deal's passage" metaphor) · GUARDRAIL: ceiling implicit, "correlation … not a tested mechanism"
- OLD: We read these patterns as call language tracking the deal's passage from private to public, a within-firm correlational regularity rather than a tested mechanism.
- NEW: We read these patterns as the call's language following a deal as it moves from private to public — a within-firm correlation, not a tested mechanism.

---

## Step (c) HAND-GATE — mechanical, by eye, no code

**Numbers:** `2002 to 2018` → S3 ✅. No new digit introduced ✅.

**Protected phrases survive verbatim:**
| phrase | ✅ | where |
|---|---|---|
| "indistinguishable from zero" (C1) | ✅ | S6 |
| "formal pooled test" (C6) | ✅ | S7 |
| "placebo" | ✅ | S4 |
| "residual" (jargon) | ✅ | S4, S5, S9 |
| "information asymmetry" (jargon) | ✅ | S9 |
| "bid-ask spread" (jargon) | ✅ | S9 |
| "not a tested mechanism" (ceiling) | ✅ | S10 |

**NEVER-traps absent:** C1 "falls/unwound/reverses" ✅absent · C6 Gelman-Stern side-by-side ✅absent · bid-ask as tested difference ✅absent (two facts, "by contrast") · citations/names/notation/coefficients ✅absent · C4 "scrutiny never matters" ✅absent.

**Props present:** all 9 — a=S1 b=S2 c=S3 d=S4 e=S5 f=S6 g=S7 h=S8+S10 i=S9 ✅
**Sentence count:** 10 → ~17 (splits only), rises ✅

**HAND-GATE: PASS.** Word-choice flags from the pilot (residual / information asymmetry) RESOLVED by decision 7 (keep jargon). S1 manager-vs-firm corrected. Bid-ask confirmed two-facts by advisor.
