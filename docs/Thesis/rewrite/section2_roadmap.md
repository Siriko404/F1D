# Section 2 Rewrite Roadmap — the Thesis Backbone

**Created 2026-06-12.** Section II ("Conceptual Framework and Empirical Strategy") is, practically, the thesis's literature review + theoretical engine. This file is the binding plan for rewriting its five subsections diligently, coherently, to the locked thin claim.

---

## 0. Governing constraints (locked, do not violate)

- **The claim (ceiling):** ONE signal, TWO dimensions — **anticipatory** (timing: present pre-announcement, gone at announcement) **×** **cash-concentrated** (cash, not stock). Both supported. The **what** is solid; the **why** (mechanism: compliance-constrained disclosure vs strategic silence) stays **open**. Correlational, no identification. Source: `claim_findings_ledger.json`.
- **Structure (supervisor template, binding):** §2 is the COMBINED "Conceptual Framework and Empirical Strategy" with five fixed subsections 2.1–2.5. No standalone Literature Review section. Data stays in §3.1. Do NOT restructure.
- **Lit review is DISTRIBUTED, not a section:** theoretical lit → §2.1; empirical (per-hypothesis) lit → §2.2; measurement/methods/validity lit → §2.3–2.5.
- **Theory is BOUNDED:** develop disclosure framing only enough to MOTIVATE the descriptive question; never claim a tested mechanism (the cause leg fails — ledger C6).
- **Develop, don't inflate:** rich apparatus (literature, math, justification), thin claim. Build on the existing accurate spine; expand; keep every verified number/equation; no sentence without new info.
- **Citation integrity:** every NEW citation is verification-gated — confirmed against the actual paper (NLM notebook / PDF title page) BEFORE it enters the draft. Real-but-unverified is not allowed (the everhart/gokkaya lesson).

## 1. The §2 arc (one coherent build, no overlap)

```
2.1 concept  ->  2.2 predictions  ->  2.3 measure  ->  2.4 designs  ->  2.5 validation
 (why the        (formal, falsifiable   (define+justify   (3 estimating    (earn trust in
  signal          hypotheses, lit-       the DV: DWZ        eqs + identi-    the construct
  exists)         grounded)              residual)         fication)        before results)
```
Each subsection feeds the next; none repeats another. This arc is the backbone.

---

## 2. Per-subsection mandate

### §2.1 Conceptual Framework — *the theoretical lit review + the lens*
- **Purpose:** establish the disclosure-state lens; derive, as theoretical expectations, the two dimensions (anticipatory × cash-concentrated).
- **Must do (paragraph-level):**
  1. Disclosure-state premise: a pending-but-undisclosed deal is MNPI; the CEO is barred from discussing it yet must host the call -> a bind. Ground in disclosure-withholding theory + the MNPI/Reg FD institutional setting.
  2. Mechanism -> ANTICIPATORY dimension: under the bind, unscripted answers turn hedged/imprecise -> uncertainty-word elevation, present while undisclosed, gone at announcement (information clock). Frame conservatively (imprecision mode, not silence -> the effect is if anything lower-bounded).
  3. Why CASH sharpens it -> CASH-CONCENTRATED dimension: cash deals sit on a visible, accumulated balance-sheet position; stock deals leave no comparable footprint (the placebo). CAUTION: frame cash via the *visible material position under the gag*, NOT via "analysts ask more" — the analyst-scrutiny channel is ruled out in §4.1.
  4. Two readings (compliance-constrained vs strategic silence) are observationally equivalent -> the framework predicts a PATTERN, claims NO mechanism, NO identification. Position in the 2x2 vs the nearest work.
- **Literature (anchors, VERIFY each):** disclosure-withholding — Verrecchia (1983), Dye (1985), Verrecchia (2001 survey); MNPI/Reg FD setting; strategic silence on calls — Hollander, Pronk & Roelofsen (2010); cash-for-acquisitions / cash visibility — Harford (1999), Opler et al. (1999), Bates, Kahle & Stulz (2009); nearest M&A-disclosure work — thewissen2024, ragozzino2024, everhart2025, gokkaya2025 (already cited).
- **Equations:** none (conceptual).
- **Serves:** the lens that makes every later choice make sense; produces the two dimensions §2.2 formalizes.
- **Boundary (must NOT):** no formal model, no tested mechanism, no causal claim; don't define the measure (§2.3) or estimator (§2.4).
- **Thin-claim discipline:** state descriptive/correlational/mechanism-open UP FRONT; cash-concentration framed via the visible-position bind, not the ruled-out scrutiny channel.

### §2.2 Hypothesis Development — *the empirical lit review (per hypothesis)*
- **Purpose:** convert the framework into formal, falsifiable, empirically-grounded predictions.
- **Must do:**
  1. Funnel from §2.1 to three hypotheses; each states prediction (direction, where/when) + mechanism-to-prediction logic + the prior empirical finding that makes it non-obvious.
  2. **H1 (run-up / anticipatory):** residual Q&A uncertainty elevated in the pre-announcement quarter for cash acquirers vs own other quarters. Ground vs thewissen2024 (managed tone before stock deals — we predict the opposite register: unmanaged uncertainty, before cash deals).
  3. **H1a (cash-concentration):** stronger for cash than stock. Ground vs cash-acquisitiveness (Harford 1999). Frame as CONCENTRATION, not strict specificity.
  4. **H1b (differential timing):** uncertainty on the information clock (resolves at announcement); cash on the transaction clock (persists to completion). Distinguish from price run-up/leakage (Keown-Pinkerton 1981) — we track LANGUAGE, not price.
  5. State the competing **analyst-scrutiny** reading formally here as the hypothesis §4.1 tests/rules out (gives the rule-out a home).
- **Literature (VERIFY):** thewissen2024, ragozzino2024 (contrast); Harford (1999); Keown-Pinkerton (1981); analyst Q&A behavior (e.g., Matsumoto, Pronk & Roelofsen 2011).
- **Equations:** none; define estimands precisely (PreAnnounceQtr = 1[e=-1]).
- **Serves:** falsifiable claims with stakes; the bridge to the designs (§2.4 maps each design to a hypothesis).
- **Boundary:** predictions about WHERE/WHEN, never WHY; don't define the measure (§2.3) or estimator (§2.4).
- **Thin-claim:** H1a = concentration not specificity; no hypothesis asserts a cause; the scrutiny alternative is a real competing hypothesis, not a strawman.

### §2.3 Estimation of the Main Variable — *the measurement heart*
- **Purpose:** define and JUSTIFY the dependent variable, UncResCEO (the DWZ residual).
- **Must do:**
  1. **Write DWZ eq-4** (primary-source verified): `UncAnsCEO_ic = a + CEO-FE_i + X_ic*g + e_ic`; `UncResCEO = e-hat_ic`. Define every first-stage regressor (UncPreCEO, analyst-Q&A uncertainty, negative tone, firm controls, year effects).
  2. Justify WHY the residual: an anticipatory, deal-tracking signal must appear/disappear within a CEO's tenure -> it can only live in the call-varying residual, not the persistent style (CEO FE). Load-bearing justification.
  3. **OWN the UncPre over-control issue** (advisor mandate + evidence): UncPreCEO is a first-stage control, yet §4.2 shows prepared-remarks uncertainty carries signal, and tab:h23 shows UncPre -> UncRes = 0.0111**/0.0230** (significant). Reconcile: argue prepared remarks are drafted/vetted in advance (don't carry the live-Q&A shock), and/or show robustness to dropping UncPre, and/or disclose as a limitation. Do NOT leave it hanging.
  4. **OWN the generated-regressand issue** (Pagan 1984): UncResCEO is a first-stage residual used as the downstream DV; state why inference holds or flag the two-step-SE concern.
  5. Justify the primitive: LM "uncertainty" dictionary (lm2011, 1993–2024); word-share; CEO Q&A vs presentation split.
- **Literature (VERIFY):** DWZ (2021, cited); managerial style / manager-FE — Bertrand & Schoar (2003); LM dictionary (lm2011, cited); generated regressors — Pagan (1984).
- **Equations:** DWZ eq-4 (residual generator) + eq-1 (raw UncPre share). PRIMARY-SOURCE verified before writing.
- **Serves:** makes the core construct credible + reproducible; the DV every design uses.
- **Boundary:** defines the MAIN var only (UncResCEO + inputs UncAnsCEO / UncPreCEO / CEO-FE / ClarityCEO). Other constructs -> §2.5/§3.1. Construction MECHANICS (tokenize, match) -> §3.1.
- **Thin-claim:** disclose generated-regressand + UncPre honestly; validity asserted as an empirical question answered in §2.5, not assumed.

### §2.4 Methodology and Empirical Design — *the design spine*
- **Purpose:** lay out the three estimating equations + identification logic.
- **Must do:**
  1. **Write the main estimating equation** (primary-source verified): `Y_it = b*PreAnnounceQtr_it + g'X_it + a_i + t_t + e_it`. Define b as the estimand per (outcome Y, treated set).
  2. **Write the event-study spec** (MA2): replace PreAnnounceQtr with the four event-time bins (PRE2, PRE1, GAP, POST).
  3. **Write the pooled interacted spec** (MA3): PreAnn_cash + PreAnn_stock + the formal cash-minus-stock linear-restriction (Wald) test.
  4. State each design's ESTIMAND + descriptive identifying assumptions: within-firm; never-acquirers as FE baseline; post-quarters dropped (so b = pre-window mean shift); PRE2 pre-trend as the validity device; NO parallel-trends causal claim. Map design -> hypothesis (run-up->H1, timing->H1b, pooled->H1a).
  5. **OWN the homeless items:** deal-timing endogeneity + first-deal-only-sets-the-clock contamination (other deals pollute the baseline); inference — clustering (firm vs two-way firm x quarter), one-tailed -> two-tailed, multiple testing; functional form (levels, share-not-count, the cash-equation partial-adjustment lag). Disclose / justify / flag-for-rerun.
- **Literature (VERIFY):** determinants of cash for the cash equation ("standard cash regression") — Opler et al. (1999), Bates, Kahle & Stulz (2009); panel SEs/clustering — Petersen (2009), Cameron, Gelbach & Miller (2011, two-way).
- **Equations:** the three estimating equations. PRIMARY-SOURCE verified before writing.
- **Serves:** exactly how each prediction hits the data + what must hold.
- **Boundary:** estimators + identification only. Variable DEFINITIONS -> §2.3/§2.5/Appendix. Data/sample-build -> §3.1. No results preview.
- **Thin-claim:** descriptive estimand, no identification; honest about the never-acquirer baseline, first-deal contamination, inference choices.

### §2.5 Specification and Measurement of Key Constructs — *the validity gate*
- **Purpose:** validate the construct (convergent + discriminant) and pre-empt the scrutiny confound.
- **Must do:**
  1. State the two demands: the residual must (a) move with real uncertainty, (b) not be a scrutiny artifact.
  2. **Convergent validity:** residual loads on political risk (hassan2020) + policy uncertainty (baker2016/davis2016). HONEST: "consistent with" — one-tailed, PRisk economically trivial, US-EPU marginal. Do not oversell.
  3. **Discriminant validity (the decisive evidence):** product-market competition (hoberg2010/hoberg2016) loads on the presentation, NOT the residual (0.0304*** vs 0.0008 n.s.). Lead with this — it is the clean result.
  4. **Pre-register the scrutiny rule-out** (§4.1 forward-ref): define CashScrutiny/HighCashScrutiny + the three-step logic; frame as "doesn't account for THIS run-up."
  5. Define remaining KEY constructs (CashRatio, PreAnnounceQtr, CashScrutiny); controls -> Appendix.
- **Literature (VERIFY new):** validity benchmarks hassan2020, baker2016, davis2016, hoberg2010/2016 — already cited, now ENGAGED not merely data-sourced.
- **Equations:** the validity regression form (light; logic is the focus).
- **Serves:** earns trust the residual measures what's claimed BEFORE results.
- **Boundary:** validity + scrutiny construct + key non-main constructs. MAIN var -> §2.3. Scrutiny RESULTS -> §4.1. Controls -> Appendix.
- **Thin-claim:** convergent = "consistent with" (weak, disclosed); discriminant = decisive; scrutiny = "doesn't account for THIS run-up," not "never matters."

---

## 3. Cross-cutting coherence flags (the diligent catches)

1. **"Empire-Building" table captions vs the disclosure framing.** Captions say "Empire-Building Run-Up Test," which invokes Jensen (1986) free-cash-flow/agency — a theory the paper does NOT make (its story is disclosure-state uncertainty). Either reframe the caption language (pre-announcement cash run-up) or lightly ground the cash build-up in the cash-for-acquisitions literature (Harford 1999) WITHOUT the value-destroying-agency connotation. **Decision needed before §2.1.**
2. **Cash-concentration mechanism vs the ruled-out scrutiny channel.** §2.1/§2.2 must motivate cash-concentration via the *visible material position under the gag*, NOT via "analysts ask harder cash questions" — because §4.1 rules the scrutiny channel out. Internal contradiction risk if framed wrongly.
3. **Intro 2x2 vs §2.1 2x2 redundancy.** Division of labor: intro = brief gap/promise; §2.1 = the developed positioning. Avoid verbatim duplication.
4. **Downstream ripple (bounded).** After §2 is rewritten, intro/abstract/§5 need a coherence pass to preview/pay-off §2's developed-but-bounded framing. Bounded theory keeps this small, not a cascade.

## 4. Per-unit writing cycle (every subsection)

1. **Source gate** — assemble the subsection's literature; VERIFY every new cite vs the actual paper. No unverified cite enters.
2. **Equation gate** (2.3, 2.4) — transcribe equations from primary source (bible spec pages + `src/f1d/econometric/*` + DWZ paper); verify before writing.
3. **Skeleton** — paragraph-level plan; user ratifies.
4. **Write** — to the thin-claim ceiling; build on the accurate spine; develop with lit + math + justification; no sentence without new info.
5. **Advisor check** (main agent) — coherence, thin-claim, no-overclaim, cross-section redundancy.
6. **Compile + verify** — `verify_draft_numbers.py` (regression check; §2 is mostly prose) + compile x2.
7. **Ledger log.**

## 5. Write order + final gate

**Order:** 2.1 -> 2.2 -> 2.3 -> 2.4 -> 2.5 (template + dependency order).
**Final gate (after §2):** cross-section coherence pass — intro/abstract/§5 preview/pay-off §2; confirm the two-dimensional thin claim reads consistently everywhere.

---

## 6. Session updates (2026-06-12) — durability

- **Resume after compaction: read `docs/Thesis/rewrite/_RESUME_STATE.json` FIRST.**
- **All table notes/captions are JUNK — to be removed and rewritten** (user). The "empire-building caption" flag (§3 #1) is therefore MOOT. Relevant at §3/§4 prose.
- **Line anchors drift:** locate every subsection by its `\subsection{...}` heading, NOT by line number, once rewriting begins.
- **Ignore mempalace auto-recall hits** — Claude-authored, unverified, user-declared useless; verify against primary source.
- **§2.1 is now a 7-paragraph plan** (the main literature review). See `section2.1_paragraph_ledger.json`.
