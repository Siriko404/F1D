# PHASE 3 — CONCLUSION: the why-cash framework + evidence lock   (2026-06-25, fork `phase3/propositions`)

> **Status: LOCKED 2026-06-25** (Sina ratified; self-audited in lieu of the down advisor — 3 overclaims fixed: no "lower bound", thewissen-distance flagged, unpriced/managed tension resolved). Companions: `_PHASE3_STATE.md`, `style_profiles/_PHASE3_KICKOFF.md`. Next: execute the proposition tweaks (Phase-4 rewrite), ratified per section.

## DECISION
**KEEP cash.** The supervisor's "the cash dimension's motivation is not justified" is answered — with **no new tests and no new citations**, by connecting evidence already in the thesis. The cash focus has an **ex-ante rationale**: a *masking asymmetry* between stock and cash acquirers. Plan-B (downgrade) is dropped.

## THE FRAMEWORK (motivation, NOT a tested mechanism)
1. **Base bind (symmetric).** A CEO withholding a pending deal cannot confirm or deny it (basic1988 / rule10b5; verrecchia1983 / dye1985; hollander2010) → uncertainty can surface in the unscripted Q&A. This binds cash and stock **equally** → predicts a run-up for *any* withheld deal. Confirmed: the anticipatory timing holds for **all** payment types (alltypes PRE1 0.0533***).
2. **Why it concentrates in CASH (the motivation — NOT a tested channel).** Stock bidders have a documented incentive to **manage their pre-deal narrative upward** — inflating disclosure *tone* ~15% in the year before a *stock-for-stock* deal to protect the equity **currency** they pay with (thewissen2024). Cash bidders have no currency to protect. We read this as the **ex-ante reason** the run-up **concentrates in cash** (C6 Wald cash−stock 0.0983**, p=.039) — a motivation, not a detected channel. *Distance to flag:* thewissen is positive *tone* in *press releases*; ours is *uncertainty* in the *unscripted Q&A* — the inference crosses dimension and medium, so it motivates, it does not prove.
3. **Why cash CEOs let it show (costless) — and why stock's stays lower.** The residual is **unpriced** (DWZ 2021; our §4.2: residual null on the post-call spread, all 12 specs), so **nobody targets it directly.** Cash CEOs have no reason to perform confidence → the strain surfaces. Stock CEOs, performing optimism broadly for the *priced* currency motive, keep it lower as a **byproduct** (global confidence is not channel-selective) — not by managing the unpriced residual itself.
4. **Read:** cash is the (relatively) **unmanaged** read of the disclosure state. **Our data show this as cash rising (+0.0461\*\*\*), stock flat (−0.0429 n.s.) — we do NOT detect stock suppression.** The stock-management leg is thewissen-grounded *reasoning*, not our result. (No "lower bound" claim.)

## REGISTER (unchanged — honesty guardrails)
- The masking asymmetry is **MOTIVATION** (an ex-ante reason to focus on cash), **NOT** a tested mechanism. We do not identify it.
- STAYS: correlational · no-identification · concentration-not-strict-specificity · supportive-not-definitive.
- **mechanism-open STAYS for the uncertainty *source*** (compliance-strain vs real reticence, still observationally equivalent). The masking explains the cash-vs-stock **gap**, not the source.
- **NO umbrella-term rescue, NO untested bridge-claim** (per `feedback_literature_drives_hypotheses`). thewissen *tests* stock tone-inflation; our Wald *tests* the gap; the link between them is stated as **interpretation**, not a new result.
- **What our data show vs do NOT:** the cash–stock gap (C6) is driven by **cash rising**; stock is a noisy flat null. We do **not** observe stock suppressing uncertainty in either channel (residual −0.0429 n.s.; scripted UncPre +0.031 n.s., tested 2026-06-25). "Stock manages" is thewissen-grounded **motivation**, never our finding.

## EVIDENCE DOSSIER

### A. Ours (results — all already in the thesis)
- **C2 run-up:** cash UncResCEO **+0.0461\*\*\*** (SE .0172, t=2.68, p=.0074 two-tailed); stock −0.0429 n.s. — `tab:empire_building_did`. *(re-validated 2026-06-25 via the production harness.)*
- **C6 cash-specificity:** cash +0.0459**, stock −0.0524 n.s., **Wald diff 0.0983\*\* (z=2.06, p=.039 two-tailed)**; CAUSE (cash build-up) diff 0.0064 n.s. → EFFECT cash-specific, CAUSE not — `tab:empire_cashspec`.
- **C1 timing (strongest):** PRE1 0.0473***, GAP 0.0018 n.s., PRE1−GAP 0.0455**; the cash that funds it persists to completion (POST −0.0155***) — `tab:empire_drop_matched`.
- **Timing = the base bind, not cash:** holds across all payment types — alltypes PRE1 0.0533***, PRE1−GAP 0.0374*.
- **Three nulls (so the cash gap is NOT these):** cash-accumulation diff 0.0064 n.s.; analyst-scrutiny interaction −0.0056 n.s.; deal size PRE1×ln(Mag) n.s.
- **§4.2 residual is UNPRICED:** UncResCEO null on the 25-day post-call bid-ask spread, all 12 specs (baseline −0.0594, SE .1068); presentation UncPreCEO positive — `tab:h14c_ceo2_decomp`.

### B. Literature (verbatim; all already cited)
- **thewissen2024** (ssrn-4900453; our §2.1 neighbor): *"in the year before the M&A announcement, stock bidders manipulate the narrative content of corporate disclosures by inflating the tone of earnings press releases in order to curtail the target acquisition cost"*; *"a significant surge of 15.32% in the tone of earnings press releases during the pre-merger period"*; stronger for larger deals, weaker performance, weaker monitoring. **[full text verified 2026-06-25]** *Distance from our setting: positive TONE (not uncertainty) in PRESS RELEASES (not Q&A) for STOCK-FOR-STOCK (not ≥50%) deals — it establishes the asymmetric incentive, not a link to our measure.*
- **DWZ 2021** (dwz2021; `tmp/nlm_dwz_reactions.json`): *"neither UncPreCEO nor UncResCEO is significantly associated with stock price or volume responses"*; the residual *"explains little of the market reaction."* → residual unpriced.
- **Base bind:** verrecchia1983 + dye1985 (a withholding state is itself informative); basic1988 + rule10b5 (a pending merger can be material; firm may stay silent but not mislead → can neither confirm nor deny); hollander2010 (silence speaks; ~6/10 calls withhold requested information).
- **keown1981:** *"approximately half of the market reaction occurs before the first public announcement date"* (p.866) — the **price** run-up; our signal is the **language** analogue.

## PROPOSITION TWEAKS (small — the dots are already in the prose)
- **§2.1 P6** — thewissen already cited (the "+15%" line); the gap (P6.4) already reads *"unmanaged uncertainty language before cash deals."* TWEAK: one clause elevating thewissen's stock tone-inflation from a *contrast* neighbor to the *motivating asymmetry* (stock managed ⇒ cash is the unmanaged read).
- **§2.2 (H1a statement)** — add the ex-ante rationale (masking asymmetry) ahead of the formal Wald.
- **§1 intro** — 1-P4-b (cash/stock placebo): name *why* cash (currency-management asymmetry); 1-P6-a (cash concentration): motivate; **1-P8-a / IN.13:** change *"leaves open why uncertainty concentrates in cash"* → *"the concentration is consistent with stock acquirers' documented pre-deal tone management (thewissen), which cash acquirers lack — offered as motivation, not identification."*
- **Abstract** — one clause motivating the cash focus (currency-management asymmetry), citation-free per abstract convention.
- **§4.1 scrutiny** — unaffected (rule-out stays).
- **Register locks — UNCHANGED.**

## PROVENANCE (the in-sample test behind the honesty floor)
`tmp/test_masking_continuous.py` — validation: cash UncResCEO reproduces **+0.0461\*\*\*** (production harness `gen_empire_did_table.G.run`); keystone: stock UncPreCEO **+0.031 n.s.** (scripted tone NOT managed down). `tmp/test_masking_binary.py` — the binary LPM+logit variant. Run from the **F1D** worktree (data + `f1d` package live there). These produced the "cash rises, stock flat — no detected stock suppression" floor.

## NEXT
Execute the per-section proposition tweaks (Phase-4 rewrite), ratified per section; register locks unchanged → merge `phase3/propositions` into `debug/campello-did-supervisor-interrogation`.
