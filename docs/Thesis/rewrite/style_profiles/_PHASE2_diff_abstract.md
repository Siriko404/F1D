# Phase-2 REWRITE — Abstract (subsection 1 of 16) — v2 (claim-word locked)

**Status: prose WRITTEN into clone `_rewrite_working/section_abstract_paragraph_ledger.json` (durable). GATE PASS. Independent advisor check next, then Sina ratify.**
v2 redo after the v1 foul (synonym swaps of claim words). Workflow = decision-2 v2 (CONTENT-WORD LOCK).

## CLAIM-WORD LOCK LIST (per proposition — all confirmed verbatim in new prose)
- a: CEO · answers · **managers** · disclosed · earnings calls · unscripted questions
- b: **privately committed** · acquisition · not yet announced · confirm or deny · track · withholding
- c: United States public firms · earnings-call transcripts · acquisition records · 2002 to 2018
- d: residual measure · **uncertainty** · persistent speaking style · cash acquisitions · stock acquisitions · placebo
- e: residual uncertainty · **elevated** · quarter before · no comparable rise · stock acquisitions
- f: indistinguishable from zero · announced · even before completion · cash that funds the purchase · persists on the balance sheet · until the deal closes
- g: elevation · concentrates · cash acquisitions · stock acquisitions · difference · survives · formal pooled test
- h: not explained by analysts devoting more of the call to cash questions · call language · tracking · from private to public · within-firm · correlation · not a tested mechanism
- i: residual · unrelated to · post-call bid-ask spread · information asymmetry · scripted presentation · **positively associated** · **outside information environment** · in different ways · **HEDGE "consistent with"** (advisor catch — hedge is claim-bearing; "appear to" was a strengthening)

## v1 FOULS now fixed
| was (v1 foul) | now (v2, claim-word kept) |
|---|---|
| "how uncertain a CEO **sounds**" | "the **uncertainty** in a CEO's answers to questions" |
| "appear to reach the **outside market**" | "appear to relate to the **outside information environment**" |
| "privately **agreed**" | "privately **committed**" |
| "rises" (change) | "is **elevated**" (level) |
| "simply spending" (editorial) | "devoting more of the call to cash questions" |

## Sentence-by-sentence (OLD → NEW), anti-pattern fixed — claim-words VERBATIM
**S1** · a · fixes long two-clause (a2-f1), "window into" metaphor (a1-f2), chief executive→CEO (a2-f4)
- OLD: Firms host quarterly earnings calls and field analysts' unscripted questions, and the language a chief executive uses in answering is increasingly read as a window into what they know but have not yet disclosed.
- NEW: Firms hold earnings calls every quarter and take unscripted questions from analysts. How a CEO answers is increasingly read as a sign of what managers know but have not yet disclosed.

**S2** · b · fixes 3 stacked clauses (a3-f2), drama (a1-f4), abstract passive gap (a2-f5)
- OLD: When a firm is privately committed to an acquisition it has not yet announced, the executive holds the routine call unable to confirm or deny the one development that matters, and whether the spoken record tracks that withholding has not been characterized.
- NEW: Sometimes a firm has privately committed to an acquisition it has not yet announced. The CEO must still hold the routine call, but cannot confirm or deny the deal. Whether the words on these calls track that withholding has not been studied.

**S3** · c · plain · number "2002 to 2018"
- OLD: We study United States public firms' earnings-call transcripts and acquisition records from 2002 to 2018.
- NEW: We study earnings-call transcripts and acquisition records for United States public firms from 2002 to 2018.

**S4** · d · fixes compound pile-up (a2-f3), inline appositive (a1-f5/a3-f3)
- OLD: From this language we construct a residual measure of chief-executive question-and-answer uncertainty, the component that remains once each executive's persistent speaking style is removed, and we track it around firms' cash acquisitions against stock acquisitions as a placebo.
- NEW: From this language we build a residual measure of the uncertainty in a CEO's answers to questions. It is the part that remains once we remove each CEO's persistent speaking style. We then track this measure around firms' cash acquisitions, using stock acquisitions as a placebo.

**S5** · e · fixes length (a2-f1), adds short beat (a2-f2)
- OLD: This residual uncertainty is elevated in the quarter before a cash acquisition, relative to the firm's own other quarters, with no comparable rise before stock acquisitions.
- NEW: This residual uncertainty is elevated in the quarter before a cash acquisition, compared with the firm's own other quarters. There is no comparable rise before stock acquisitions.

**S6** · f · GUARDRAIL C1 lead "indistinguishable from zero", never falls/unwound
- OLD: It becomes indistinguishable from zero once the deal is announced, even before completion, while the cash that funds the purchase persists on the balance sheet until the deal closes.
- NEW: Once the deal is announced, this uncertainty becomes indistinguishable from zero, even before completion. The cash that funds the purchase, by contrast, persists on the balance sheet until the deal closes.

**S7** · g · GUARDRAIL C6 "formal pooled test"
- OLD: The elevation concentrates in cash acquisitions rather than stock acquisitions, a difference that survives a formal pooled test.
- NEW: This elevation concentrates in cash acquisitions rather than stock acquisitions, a difference that survives a formal pooled test. *(near-unchanged; already plain + faithful)*

**S8** · h-part1 · GUARDRAIL C4
- OLD: This pattern is not explained by analysts devoting more of the call to cash questions.
- NEW: This pattern is not explained by analysts devoting more of the call to cash questions. *(unchanged)*

**S9** · i · HIGHEST-RISK · fixes bundling (a3-f5) · two facts, never a tested difference
- OLD: The residual is also unrelated to the firm's post-call bid-ask spread, a standard gauge of information asymmetry, while the scripted presentation is positively associated with it, consistent with the two parts of the call relating to the outside information environment in different ways.
- NEW: The residual is also unrelated to the firm's post-call bid-ask spread, a standard gauge of information asymmetry. The scripted presentation, by contrast, is positively associated with that spread. This is consistent with the two parts of the call relating to the outside information environment in different ways.

**S10** · h-part2 · fixes "tracking the deal's passage" metaphor (a1-f6); kept claim verb "tracking"
- OLD: We read these patterns as call language tracking the deal's passage from private to public, a within-firm correlational regularity rather than a tested mechanism.
- NEW: We read these patterns as call language tracking the deal's move from private to public — a within-firm correlation, not a tested mechanism.

## GATE (by hand) — PASS
- Claim-words: ALL survive verbatim (per-prop list above; string-checked). ✅
- v1 fouls: ALL absent (sounds / privately agreed / outside market / reach the outside / simply spending). ✅
- NEVER-traps: unwound / reverses / falls / "scrutiny never" all absent. ✅
- Number "2002 to 2018" present; no new digit. ✅
- Sentences 10 → 19 (splits only). ✅
- JSON valid, 9 props + number_audit + 8 guardrails intact. ✅

## For the independent advisor check (residue strings can't catch)
Per proposition: polarity/negation flip · direction · hedge strength · clause re-attachment · added causation/transmission · scope/quantifier · entity swap (note S1 uses "managers" per prop a, not "CEO").
