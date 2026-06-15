# Referee Audit — Findings Ledger (2026-06-15)

Source: `referee_audit_workflow.js` run `wf_64d11b87` (5 aspect teams x [3 finders + 1 culling red-team]).
Read-only audit. Nothing applied. 19 confirmed findings: **5 MAJOR, 14 MINOR.** Deduped across aspects.

Every fix below is **prose** (no econometrics) except where a robustness number is already banked
(`robustness_drop_sec43_44.py`, commit c95ad72a). Fix all via the **ledger -> reassemble -> recompile**
pipeline; do them in ONE pass after this triage.

---

## MAJOR (5)

| # | Aspect | Location | Issue | Fix | Origin |
|---|---|---|---|---|---|
| M1 | coherence | intro roadmap L18 + abstract + concl + contribution list | Section 4.2 (spread) is a full results section but is named **nowhere** in front/back matter; roadmap says Section 4 = singular "the additional analysis". Sibling 4.1 IS threaded everywhere. | Thread 4.2 through abstract/intro-preview/contribution-list/roadmap/conclusion (or cut). Keep-vs-cut = scope decision. | **this session** (§4.2 add) |
| M2 | logic | §4.2 PARA3 (L76) | Self-contradiction: attributes to DWZ "presentation, not residual, is the segment outsiders respond to" while PARA2 says DWZ found **no** presentation effect on price/volume + tested no liquidity outcome. (Citation team corroborates: no admissible span either.) | Drop the DWZ clause; attribute the presentation->spread direction to **bgt2018 alone** (PARA4 already does). | **this session** |
| M3 | logic | §4.2 PARA4 (L78) | "different audiences / an asymmetry" = drawing a **difference** from one coef significant + one insignificant = Gelman-Stern, which the house register forbids (only a Wald/interaction is a difference test). | Downgrade to per-component, same-regression wording (UncPre positively assoc.; UncRes not detectably assoc.); state no between-component test was run. | **this session** |
| M4 | weaknesses | §2.4 L238 + cash/EPU tables | Lagged-DV + firm-FE (**Nickell** bias) never disclosed, though the generated-regressand caveat IS disclosed in the same sentence. Referee seed. | **One disclosure sentence** (T large ~68 -> bias O(1/T) negligible; focal coef is the treatment/IV, not the lag). **NOW also backed by the §4.4 static-FE robustness** (drop lag -> drop intact, +0.0305***). | pre-existing |
| M5 | weaknesses | §3.3 L38 + tab:empire_drop_matched | POST = completed deals only + post-withdrawal rows dropped (undisclosed) -> the PRE1->POST "round-trip" / "persists to completion" legs condition on a post-treatment outcome (which deals complete). **The resolution-at-announcement PRE1-GAP leg is unaffected.** | Disclose the withdrawn-drop + completed-only POST; foreground the PRE1-GAP leg. **NOW also backed by the §4.3 resolution robustness** (withdrawal in POST -> drop survives +0.0687***, N adds 28 firms). | pre-existing |

---

## MINOR (14)

**Citation (6)** — all UNVERIFIABLE (no admissible `cited_text` span; substance not contradicted):
- C1 §4.2 PARA3: DWZ "presentation is segment outsiders respond to" — span lives in NLM *answer*-prose only. (= M2.)
- C2 §4.2 PARA1/2/4: DWZ price/volume-null + "explains little of the market reaction" — answer-prose only; the section4.2 ledger's "VERBATIM" tag is itself inadmissible.
- C3 §4.2 PARA1: bgt2018 "25 trading days" window — answer-prose only.
- C4 §2.5: DWZ replication figures 0.093 / 0.054 / 0.31 — no span (the `eq4_estimation` capture has empty `references`); user PDF-confirmed but not span-logged.
- C5 §2.1: legal cites basic1988 / rule10b5 — no NLM span possible (court opinion + CFR rule). Accept as legal authority.
- C6 §2.1: thewissen2024 "lifting share price to reduce issuance cost" **purpose** clause — facts span-backed, the purpose gloss is not. (Intro version already avoids it.)

**Logic (3):**
- L1 §4.2 PARA4: causal verbs "moves / widening" on a one-tailed correlational coef. (dedups with W1.)
- L2 §3.3 PARA5: "independent corroboration on a second sample" — placebo cash arm is a ~95% near-superset of the matched universe, not independent. Drop "independent".
- L3 §3.3 PARA4: 0.0723 is PRE1->POST (peak-to-completion), but the clause "once the information is public" describes PRE1->GAP (=0.0455**). Cite the GAP drop there.

**Cohesion (2):**
- H1 §1 intro: "previewed in four parts" but only 3 ordinal markers (First/Second/Finally); 4th folded under "Finally".
- H2 §2.1 L164 / §2.3 L212: residual called "call-level" vs the dominant "call-varying" — one construct, two names.

**Weaknesses (3):**
- W1 §4.2 PARA4: causal verbs outrun the column-level fragility (UncPre fades to n.s. under industry-FE + extended controls). (dedups with L1; the in-section hedge caps it MINOR.)
- W2 §3.1/§2.4: cash/stock arms use overlapping weak inequalities (>=50%), so a 50/50 deal qualifies for both; no tie-break or threshold-sensitivity disclosed.
- W3 §2.2/§2.1: "anticipatory / private-to-public" presumes MNPI existed at e=-1, but the clock is anchored to the public announcement, not deal initiation — an unflagged interpretive assumption.

---

## Fix plan (one pass, all prose)

1. **§4.2 cluster (M1, M2, M3, L1/W1, C1-C3)** — the bulk; all from this session's spread addition. Fix the PARA3 DWZ clause, the PARA4 difference-claim + causal verbs, then thread 4.2 through the front/back matter.
2. **Disclosures (M4, M5, L2, L3, W2, W3)** — short sentences; M4/M5 now also carry the §4.3/§4.4 robustness numbers.
3. **Cohesion (H1, H2)** — trivial wording.
4. **Citation (C4, C5, C6)** — C4 = log the user's PDF-confirmed DWZ numbers as ground truth (or re-capture a span); C5 = accept legal; C6 = trim the purpose gloss.
5. **New robustness sections §4.3 (resolution) + §4.4 (static-FE)** — write after the above, calibrated: §4.3 "consistent with (N=28 withdrawn firms)", §4.4 "result does not depend on the dynamic term" (keep the lag in the main spec).
