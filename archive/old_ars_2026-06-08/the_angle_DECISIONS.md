# The Angle — Decisions & Spec

**The angle** = anticipatory call-uncertainty around undisclosed cash deals (disclosure-window event study).

D32 and D28 below are byte-exact slices of the archived ledger `archive/old_precautionary_angle_2026-06-08/v7_DECISIONS.md`, programmatically extracted 2026-06-08 (NOT retyped). Companion ARS docs in this tree: `ars_artifacts/plan_2026-06-06/chapter_plan.md`, `ars_artifacts/litcheck/litcheck_VERDICT.md`, `DraftTemplate.txt`. Reusable verbatim citations (DWZ measure; PRisk / US-EPU / GEPU; Spread; CCCL) live in that archived ledger, Beats 2 / 4 / 5.

---

### D32 — 2026-06-06 — Thesis headline RE-ANCHORED to the angle (anticipatory call-uncertainty around undisclosed cash deals); novelty lit-check PASSED
**Repositions the D4 narrative anchor as the HEADLINE.** After the empire/reverse-causality verification (drop test + matched-universe differential timing + formal cash-specificity) and a clean restart of ars-plan Step 1, the paper's headline is re-anchored from the forward precautionary-cash claim (D4 / Beat 1) to the reverse/disclosure-state finding. The forward precautionary result is repositioned as complementary/context, **NOT gutted**; full §I–V reconciliation is the NEXT step (not done in this entry).

**Locked headline claim:**
> CEO earnings-call residual uncertainty (UncResCEO) has an anticipatory, cash-deal-concentrated component: it rises in the quarter(s) before an undisclosed cash acquisition and resolves at announcement — tracking the deal's disclosure state, not the firm's cash balance or analyst scrutiny. Mechanism (constrained MNPI disclosure / strategic silence) is a hedged interpretation, not a claimed identification.

**Calibrations locked (advisor + lit-check):**
- Headline rests on the SOLID run-up (UncResCEO +0.046, t≈2.7) plus the UncResCEO-vs-CashRatio timing contrast (uncertainty gone by announcement while cash holds to completion). The absolute PRE1−GAP "collapse" is SUGGESTIVE only (two-tailed p≈.05–.09) — not labelled solid.
- "Cash-CONCENTRATED" (stock placebo null), NOT "formally cash-specific" (the pooled cash−stock Wald p=.039 is supported-but-fragile; not a headline pillar).
- Analyst scrutiny is REJECTED as the channel/driver of the run-up (amended 2026-06-06 per Table 18 reason-gating interrogation; supersedes the prior "underpowered null, not falsified" wording). Evidence: the conditional effect of scrutiny on UncResCEO is a conditional (within-model) zero (Table 17 channel CashScrutiny -0.0000, SE .0013, N=41,512; Table 18 col-1 CashScrutiny 0.0000, SE .0018), and the operative CashScrutiny x PreAnnounceQtr interaction is ns (-0.0056, SE .0111) while the run-up itself stays 0.0413*** in the same model. Both scrutiny and uncertainty rise UNCONDITIONALLY in cash calls (Table 16: CashRatio->CashScrutiny 0.7530***), but the conditional link is zero — the analyst-grilling artifact story is not supported. GUARDRAIL (keep in print): this is a failure-to-find PLUS a within-model dissociation, NOT a powered equivalence test (the interaction CI is roughly [-0.027, +0.016] against a ~0.041 run-up); 89% of calls have zero scrutiny and Gelman-Stern applies to the significant-vs-ns contrast. So the register is "scrutiny does not account for THIS run-up / reject the scrutiny channel," NOT "precisely-estimated zero" and NOT "scrutiny is irrelevant to uncertainty everywhere." (Note for register discipline: Tables 17/18 are not new data — they pre-existed the original wording; what changed is reading the interaction in isolation. A correct reframing can move the conclusion, but the verb must keep the thesis's hedge register so draft_writer does not inflate it.)
- Framing = (B) positive information-content ("call language anticipates undisclosed material events"); methodological-caution (A) = a one-paragraph implication, not the headline.
- Scope stated as "components we identify," explicitly NOT claimed exhaustive.
- The DWZ residual is the measurement TOOL, not a novelty pillar (DWZ = ≤19-citer working paper).

**Table architecture locked:**
- Headline (UncResCEO): empire run-up + drop-matched (differential timing) + drop-placebo (cash vs stock) + cashspec (formal, hedged).
- Support (UncResCEO): PRisk / US-EPU / GEPU (measure tracks real uncertainty — construct validity); analyst-scrutiny ×3 (validity + channel + reason-gating) as FALSIFICATION that scrutiny drives the run-up.
- Optional (UncPreCEO, presentation side — a different component): CCCL (presentation-uncertainty → SEC conference-call comment letters; weakly sig; novel) + Bid-ask Spread (sig, fades with full controls; precedent BGT 2018 not DWZ — frame as contrast).

**Novelty lit-check PASSED** (OpenAlex/pyalex forward-citation screen of 5 call-language seeds, ~2,600 citers → 67 M&A-citers all screened; 4 closest read in full; record = `tmp/litcheck_VERDICT.md`):
- DWZ residual measure never applied to deals; no prior shows the anticipatory pre-announcement uncertainty-then-collapse in call language.
- Adjacent cluster to cite-and-distinguish (none a scoop): Ragozzino & Reuer 2024 *LRP* (M&A → volume of corporate-strategy keywords on calls); Everhart-Kravet-McVay-Warren 2025 (M&A → earnings-guidance precision); Gokkaya-Liu-Stulz 2025 (publicly-disclosed acquisition plans → market reaction); **Thewissen et al 2024** (stock-for-stock bidders inflate earnings-PRESS-RELEASE TONE pre-announcement).
- Thewissen = mirror image, verified by full 62-page read: TONE not uncertainty, press releases (conference calls excluded), STOCK deals only (cash explicitly null on tone). Clean 2×2 — stock×tone (Thewissen) vs cash×uncertainty (us); we fill the empty cell.
- Writeup obligations: cite all four; state the stock placebo as "clean for the uncertainty channel" (Thewissen shows stock is NOT clean for tone); add a tone control in the cash run-up robustness.

**Open (next):** reconcile the new headline with the existing v7 precautionary-cash draft (§I–V); ars-plan Step 2 (chapter-by-chapter). Prose carries from prior: "differential timing" not "double dissociation"; two-tailed visible; withdrawn-null limit kept; stock placebo = "no comparable positive run-up."

---

### D28 — 2026-04-30 — Per-unit approval for thesis design + prose
**Trigger:** Step 3 unilateral 6-beat write-up triggered user pushback; advisor flagged beat decomposition itself as unapproved content; user clarified scope: "the design and the architecture of the draft also. the entire writing process must keep me in the loop closely."
**Decision:** All thesis-related substantive work requires per-unit user approval before I write to file or commit. Includes:
- Prose content (sentences, paragraphs, abstract, headlines)
- Section/subsection structure (ordering, naming, titling)
- Decomposition units (e.g., 5-beat vs 3-beat narrative anchor)
- Scaffold/architecture (LaTeX file organization, layouts)
- Workflow/process changes affecting writing

**Pattern:** I draft 1-2 candidates + D-anchors → user picks/modifies/rejects via AskUserQuestion → only approved content written → next unit.

**Out of scope (no per-unit approval needed):** trivial maintenance edits only — marking [x] in process tracker, updating tracker line text, fixing typos within already-approved prose, transcribing user picks already made via AskUserQuestion into v7_DECISIONS.md, recording new D-decisions whose substance the user has already articulated in chat.

**Scope refs:** "all future prose work" + "draft writing ONLY, should be with my one by one approval" + "design and architecture of the draft also. the entire writing process must keep me in the loop closely" (user pick chain 2026-04-30).
