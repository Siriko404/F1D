# FIX PLAN 2 — readability pass (Sina 2026-06-28). 4 items. All via generator transforms; clone never hand-edited.

Mechanism = new transform fns in build_uottawa_rewrite.py (same assert-guarded pattern as fix_*).
Order = 4 -> 2 -> 1 -> 3 (cheapest/safest first; dashes last, biggest+riskiest). Commit per item.
Floor UNTOUCHED (no number/coef/hedge moves). Verify after each: PDF OK pages~70 0/0; floor_inventory grid
unchanged; number_audit A=0/B=0; destars PASS; orphan 0. Item-specific gates below.

## ITEM 4 — number the equations (LOW risk)
- 5 display eqs, all `\[ ... \]` in Ch2: phaseB 2.3 (x2: UncAnsCEO ratio; DWZ decomposition),
  2.4 (x3: MA1, MA2, MA3). Confirmed count=5, nowhere else.
- Fix: transform on sid 2.3/2.4: `\[ X \]` -> `\begin{equation}\label{eq:KEY} X \end{equation}`.
  Labels: eq:uncans, eq:dwz (2.3); eq:ma1, eq:ma2, eq:ma3 (2.4). Assert 2 in 2.3, 3 in 2.4.
- book class -> numbers render (2.1)..(2.5). Trailing comma inside `\[...,\]` stays (econ convention).
- OPEN Q: number-only (literal ask) vs also wire `\eqref` cross-refs (prose says "the Section 2.4 equation",
  "their equation (2)"). REC: number-only (minimal, safe).
- Gate: 5 numbered eqs in PDF; undefined-ref=0; no Overfull from eqs.

## ITEM 2 — non-standard (rhetorical-Q) openers (LOW risk)
- 4 clear openers -> declarative, meaning+floor preserved, assert-guarded exact replace:
  1. 2.1 "Where does this leave our paper relative to the nearest work?"
  2. 2.3 "Why a residual at all?"
  3. 3.2 "How large are these effects?"
  4. 4.4 "How should we read the two side by side?"
- OPEN Q: also convert 2.5 "We ask three things... First...? Second...? Third...?" enumeration + sweep
  conversational openers ("So", "Now"-initial)? REC: do the 2.5 enumeration; skip So/Now sweep unless asked.

## ITEM 1 — paragraph balance (LOW-MED risk)
- median 138w. Split Ch2 monsters at natural topic boundaries -> target <=~230w:
  ch2[0]291, ch2[4]438, ch2[13]435, ch2[19]337(First..Fifth threats), ch2[21]292, ch2[23]293.
  Optional 244w: ch2[16], sec34[12], sec34[40], sec34[3].
- Fix: transform inserting `\n\n` at ONE asserted sentence boundary per split.
- Abstract (320w, single para) LEFT (single-paragraph convention).
- Gate: re-run measure.py -> max prose para <~250w.

## ITEM 3 — em-dashes -> 0 (MED-HIGH risk; biggest)
- 127 prose `---` (ch2 59, sec34 65, intro 1, abstr 2, concl 0). Scope = EM-DASH ONLY.
  NOT touched: hyphens (pre-announcement, within-firm), numeric/ref ranges (2002--2018, 35--65,
  Sections~2.2 and~2.4), math minus. Table caption/note em-dashes = SEPARATE optional batch.
- Grammarly-correct, context-aware (NOT blind comma -> would make comma-splices + list ambiguity):
  * paired `X---Y---Z`, Y contains a comma (list)        -> parentheses  X (Y) Z
  * paired `X---Y---Z`, Y no internal comma              -> commas       X, Y, Z
  * single `X---Y` (appositive/continuation)             -> comma        X, Y
  * single where Y summarizes / is independent clause    -> colon or period (manual override)
- Build: transform applies structural rules -> emit FULL diff (all 127 old->new w/ context) ->
  I review -> add exact-string overrides for colon/period cases -> apply.
- Also DROP line 325 `body.replace(" -- ","---")` (it CREATES em-dashes); dash-killer handles " -- " too.
- Gate (hard): `---` count in all 5 prose files == 0 after; no em-dash introduced; number_audit clean;
  full diff manually reviewed; advisor check.
- OPEN Q: grammarly-correct context-aware (REC) vs fast comma-default. + include table captions/notes?

## DECISIONS (fill after Sina)
- #4 cross-refs: ____
- #2 extra openers: ____
- #3 quality bar: ____   #3 tables too: ____
