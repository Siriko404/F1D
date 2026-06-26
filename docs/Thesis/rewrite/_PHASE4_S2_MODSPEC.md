# PHASE 4 — Section 2 proposition-chain modification spec (pre-advisor)   2026-06-26

> # ⛔ SUPERSEDED IN PART — READ `_PHASE4_HARNESS_HANDOFF.md` §5 BEFORE IMPLEMENTING
> This file is **v1 (pre-advisor)**. Three things below are WRONG/INCOMPLETE and were fixed by the advisor:
> 1. **P5.4 / §2.2-P3.3** must use **attenuation-not-suppression** (stock = smaller/noisier, NOT suppressed) + the **cross-channel bridge** (cites = scripted channels; our DV nets out scripted, §2.3 P2.5 → we read the hardest-to-manage channel = a STRENGTH). The P5.4 drafted below is the BROKEN version (silent on stock → unmotivated differential). Do NOT implement it.
> 2. **§2.1-P4** and **§2.2-P2.thin_claim** ARE changed (placebo → comparison; "isolates" → "motivates concentration") — they are wrongly listed UNTOUCHED below.
> 3. Open-Qs are RESOLVED in the handoff (Harford keep+demote+relocate; thewissen split + 1-clause P5 pointer; genre-jump = the bridge).
> The corrected, complete spec = `_PHASE4_HARNESS_HANDOFF.md` §5–§6 + the reference application `tmp/apply_s2_1_mods.py`.

> Scope: redesign the §2 proposition CHAIN for the masking why-cash framing. Design-level (purpose + propositions), NOT paragraph allocation. Source of the old chain: the 5 `section2.x_paragraph_ledger.json` (verbatim-dumped). Decision + cite lock: `_PHASE3_CONCLUSION.md` (EVIDENCE DOSSIER §C).

## Locked constraints (do not violate)
- KEEP cash. Masking = **MOTIVATION**, not a tested mechanism. Register locks UNCHANGED: correlational · no-identification · concentration-not-strict-specificity · mechanism-open · supportive-not-definitive.
- **NEVER "stock suppressed."** Data: cash rises (+0.0461***), stock flat-null (−0.0429 n.s.). We claim a GAP (cash rising); we do NOT detect stock suppression. Interpret, not detect.
- Cite stack (NLM-verified): **Shleifer-Vishny 2003** (currency MOTIVE) · **Louis 2004** (pre-deal earnings BEHAVIOR) · **thewissen 2024** (TONE, preprint). Cite S-V/Louis as EARNINGS/VALUATION, NOT tone.
- §2.1-P5 / §2.2-P3 = REAL re-derivation (payment-method premise stays; visible-cash-position rationale goes), not a word-swap.
- C1 (timing) carries the paper independent of masking.

## The masking logic (the new why-cash)
Stock acquirers pay with **equity** (a currency whose price matters) → incentive to keep valuation high (S-V) → manage perceptions up pre-deal (Louis: earnings; thewissen: tone). Cash acquirers pay with **cash** → no currency to protect → no such incentive → cash is the **(relatively) unmanaged window** where the disclosure-strain surfaces → run-up should **concentrate** in cash (motivates H1a). Boundary: motivates FOCUSING on cash; predicts NO stock suppression; the gap is realized as cash rising.

---

## CHANGES (exhaustive)

### §2.1 P5 (cash dimension) — SUBSTANTIVE re-derivation
- **P5.1** [harford1999] — DEMOTE to background (payment-method premise, cash side): *"A cash purchase draws on an accumulated cash position, whereas a stock exchange is paid in the acquirer's own equity."* No longer the why-cash. **OPEN Q for advisor: keep demoted, or drop Harford entirely?**
- **P5.2** [NEW · shleifer_vishny2003]: *"A stock acquirer pays with its own equity, whose market value is the deal currency; acquirers have an incentive to keep that valuation high — overvalued equity is used as acquisition currency, and relative valuation drives the cash-vs-stock payment choice."* (MOTIVE; cite as valuation, not tone.)
- **P5.3** [NEW · louis2004]: *"Consistent with that incentive, stock acquirers manage perceptions upward ahead of the deal: they overstate reported earnings in the quarter before a stock-swap announcement."* (Published BEHAVIOR, EARNINGS; the tone analogue thewissen is positioned in P6.)
- **P5.4** [NEW · framing-nonverifiable]: *"A cash acquirer pays in cash, not equity, so it has no comparable currency to protect and no analogous incentive to manage pre-deal perceptions upward. Cash is therefore the (relatively) unmanaged setting in which the disclosure-strain can surface as unscripted uncertainty language — the ex-ante reason to expect the run-up to concentrate in cash. Offered as MOTIVATION for focusing on cash, not a tested mechanism; it predicts no active suppression of stock's uncertainty (the cash-vs-stock gap is realized as cash rising, not stock falling)."* (MASKING INFERENCE + honesty boundary.)
- **P5.5** [NEW · framing-nonverifiable, register]: *"The stock deal is thus a managed COMPARISON, not a placebo: the same disclosure bind, but carrying a currency-management incentive that cash lacks. The contrast remains one of concentration, not strict specificity; the asymmetry motivates the cash focus and is not an identification claim."* (placebo→comparison + register; mechanism-open preserved.)
- The two-clocks content in P5 prose (info clock vs transaction clock) — UNCHANGED.

### §2.1 P6 (nearest-work / gap) — LIGHT
- P6.1 (thewissen, tone) — UNCHANGED as the nearest LANGUAGE neighbor. Optional ONE clause: position thewissen's managed tone as the language analogue of the P5 asymmetry.
- P6.2 (ragozzino), P6.3 (keown), **P6.4 gap** ("to our knowledge no prior work reads unmanaged uncertainty language before cash deals") — UNCHANGED.

### §2.2 P2 (H1) — LIGHT
- **P2.1 (H1 statement) — UNCHANGED.**
- P2.2 [callback] — broaden the callback to the fuller stock-management evidence now in §2.1 P5/P6 (S-V, Louis, thewissen); H1 still predicts the opposite register (unmanaged uncertainty before cash). P2.3 UNCHANGED.

### §2.2 P3 (H1a) — SUBSTANTIVE re-derivation (mirror of §2.1 P5)
- **P3.1 (H1a statement) — UNCHANGED:** run-up stronger for cash than stock.
- **P3.2** [callback] NEW: *"Stock acquirers pay with equity and have a documented incentive to manage pre-deal perceptions upward to protect that currency (callback §2.1 P5: Shleifer-Vishny motive, Louis behavior); cash acquirers lack it, making cash the relatively unmanaged window where the run-up should concentrate. The stock deal is a managed COMPARISON, not a placebo."* (was: Harford war-chest placebo.)
- **P3.3** AUGMENT: keep EFFECT-not-CAUSE + concentration-not-specificity; ADD *"and predicts no active suppression of stock's uncertainty — the differential is realized as the cash run-up, read as motivation, not identification."*

### §2.4 P2.3 (MA2) — MECHANICAL (1 word)
- *"...run for cash acquirers and, as a **comparison** [was: placebo], for stock acquirers..."* Rest (two-tailed) UNCHANGED.

### Bibliography
- ADD 2 `\bibitem` in `thesis_draft.tex`: `shleifer_vishny2003`, `louis2004` (compile requirement; undefined-citation risk if missed).

### Register
- ADD lock: "masking = MOTIVATION not mechanism; no stock-suppression claim; interpret-not-detect." Governs the new §2.1-P5 / §2.2-P3 props.

---

## UNTOUCHED (exhaustive)
- **§2.1:** P1 (P1.1–1.4 bind) · P2 (venue) · P3 (mechanism) · P4 (P4.1–4.3 locate, incl. residual-unpriced) · P7 (scope/mechanism-open).
- **§2.2:** P1 (funnel) · P2.1 (H1) · P2.3 · P4 (H1b two clocks) · P5 (scrutiny rival).
- **§2.3:** ALL (P1, P2, P3 — measurement). *Optional dovetail (NOT proposed): P2.5 "residual net of scripted presentation = the unmanaged read" reinforces masking — left untouched to avoid genre-jump confusion.*
- **§2.4:** P1 (MA1) · P2.1, P2.2 · P3 (MA3 Wald — mechanism-agnostic linear restriction, no change) · P4 · P5 (incl. P5.4 "cash by-product not war-chest" — different topic, no conflict).
- **§2.5:** ALL (validity + scrutiny side-test).

## Logic-flow check (intact end to end)
1. §2.1: bind symmetric (P1) → venue (P2) → anticipatory mechanism (P3) → locate in residual (P4) → **cash is the unmanaged window (P5 masking)** → positioning/gap (P6) → mechanism-open (P7).
2. §2.2: funnel (P1) → H1 run-up (P2) → **H1a concentration via masking (P3)** → H1b two clocks (P4) → scrutiny rival (P5).
3. §2.3 measurement · §2.4 designs (MA2 comparison rename; MA3 Wald unchanged) · §2.5 validity — all hold.
- Stress tests: P5(stock manages) vs P1(bind symmetric) → consistent (bind binds all; readability differs). P5 vs data(stock flat) → P5.4 boundary (no suppression claim). P5 vs §2.4-P5.4(no war-chest) → different topic. thewissen P5/P6 → split (P5 = earnings/motive published; P6 = tone neighbor) avoids double-use.

## OPEN QUESTIONS for advisor
1. Keep Harford (P5.1) demoted, or drop it (orphaned once the visible-position why-cash is removed)?
2. Is the P5/P6 thewissen split clean (motive-earnings in P5; tone-neighbor in P6), or should thewissen's tone sit in P5 with the motive?
3. Does the genre-jump (S-V/Louis = earnings/valuation → our Q&A uncertainty) need an explicit bridging caveat in P5.4, or does "motivation not mechanism" cover it?
