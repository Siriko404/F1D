# Thesis Draft — Decisions Log

**Current phase:** Phase 5 audit — philosophy-framed, dialogue-based. Hard reset 2026-04-14. Audit design finalized; 0 suites audited under the new approach. Starts at H1 (Q1 cluster).

---

## 1. Philosophy of the audit

### 1.1 What the thesis is actually arguing

Thesis: "Uncertainty in Language and Corporate Outcomes." Novel IV = speech uncertainty measured from earnings-call language (Manager Q&A primarily, via `UncAnsMgr`). Claim: this measure carries information about corporate behavior and outcomes beyond what standard financial controls capture.

### 1.2 The central risk

The central risk is NOT statistical significance. With 112,968 calls across 2,429 firms (2002-2018), p-values are cheap. The central risk is **"so what?"** A skeptical committee reader's default is:

> "Cheap p-values on a noisy linguistic measure, hand-picked hypotheses, publication-bias machine, no mechanism, nothing load-bearing for how we understand firms."

The audit exists to defend against that default. Every kept suite must earn its place by answering a question a skeptical reader will genuinely ask. Not because it's significant. Not because it was in some prior canonical list. Because without it the thesis has a gap a committee member will point at.

### 1.3 Reader-questions the thesis must defend against

| # | Question | Role |
|---|---|---|
| Q1 | Does speech uncertainty actually predict what firms DO? | Foundation. Without direct-outcome evidence, thesis fails at step 1. |
| Q2 | Does the effect run through a plausible channel, or is it black-box correlation? | Mechanism. Without channel evidence the effect is a curiosity, not a contribution. |
| Q3 | Is the market actually listening / using the information? | Information content. If market ignores it, the measure is noise. |
| Q4 | Is the IV just a proxy for macro conditions / business cycle? | Construct validation + endogeneity. If macro EPU drives it, we're measuring macro not firms. |
| Q5 | Does the effect matter economically, not just statistically? | Magnitude. Cross-cutting sweep, addressed at end of audit, not per-suite. |
| Q6 | Is this cherry-picking / fishing? | Transparency. Addressed via honest reporting of boundaries, nulls, and CEO/Pre parallel measures inside each Q1-Q4 suite. Not a separate cluster. |

Every kept suite maps to exactly **one** of Q1-Q4 (or a new Q7+ named and justified during dialogue). Q5 + Q6 are cross-cutting and addressed differently.

### 1.4 The audit verdict types

- **KEEP** — maps to a reader-question, the cells honestly answer that question, no other suite answers it better.
- **DROP** — no reader-question it uniquely answers, or question is already answered elsewhere, or cells don't support the claimed answer. Lives in fishing deck / future work.
- **REFRAME** — cells answer a different question than originally framed; the new question is still load-bearing; keep with adjusted narrative role.

---

## 2. How the audit runs

### 2.1 Not a rubric

A rubric-based audit ("N/12 sig + firm FE + extended controls = Main-tier") produces mechanical verdicts that collapse under adversarial questioning. A committee member asks "why that threshold?" and the edifice wobbles. Rubrics are what I reach for because they look defensible, not because they actually defend anything. The thesis does NOT need rubrics.

### 2.2 Per-suite dialogue (5 steps)

For each suite in the audit order:

1. **I read cells plain.** LaTeX cell facts only. No interpretive labels.
2. **I name the reader-question** the suite is proposed to answer (from §1.3 Q1-Q4, or a new Q7+ justified on the spot).
3. **I argue honestly** whether the cells actually answer that Q, including the adversarial counter-argument a skeptic would raise against KEEP.
4. **User pushes back** adversarially: "that's not what a skeptic would ask", "Q already answered elsewhere", "cells answer a weaker version", "sample restriction kills external validity", etc.
5. **We converge** on KEEP / DROP / REFRAME. If we can't converge, the suite is flagged for advisor review at the phase boundary.

### 2.3 The only non-generic principle

**Every KEEP verdict must have a named reader-question and an honest argument that the cells answer it.** Everything else is per-suite judgment informed by cell facts, the thesis's epistemic structure, and what a skeptical reader would genuinely ask.

### 2.4 Discipline carry-overs (still in force)

- **UncAnsMgr is the sole hypothesis channel.** CEO / UncPreMgr / UncPreCEO are secondary measures reported in tables but NOT positive hypothesis channels. Aligned secondary → 1-line supportive cite. Contradicting → "measurement concerns" flag, no rescue narrative. (`feedback_ceo_noisy_mgr_central.md`)
- **No rescue narratives.** Contradictions logged, never rescued with sub-theories. (`feedback_audit_first_no_narrative.md`)
- **Read-tool-linear only.** No Grep / pattern search / shortcut on `outputs/all_tables.tex` or runner source. (`feedback_phase5_methodology.md` rule 6)
- **Pre-audit canonical reads mandatory** before touching any suite: `DECISIONS.md` + `PROGRESS.md` + `memory/project_phase5_audit_progress.md` + `memory/feedback_phase5_philosophy.md` + `memory/feedback_phase5_methodology.md` + `memory/feedback_ceo_noisy_mgr_central.md` + `memory/feedback_audit_first_no_narrative.md`.
- **Concise default.** Lead with the answer. Tables over prose paragraphs. (`feedback_concise_default.md`)
- **No mid-audit rubric creation.** If I catch myself inventing a threshold to justify a verdict, stop — the verdict must rest on the reader-question argument, not a number.

---

## 3. Audit order — by reader-question cluster

Walk Q1 → Q2 → Q3 → Q4. Within each cluster, suites are audited in the order below. Cluster assignment is provisional — if cells in a suite clearly answer a different Q, the suite is re-clustered during dialogue with an explicit argument.

### Q1 cluster — direct outcomes (10 suites)

Does speech uncertainty predict what firms DO?

H1 (cash) → H4a (book leverage) → H4b (debt-to-capital) → H12 (payout ratio) → H12b (payer dummy) → H13 (capex) → H16 (R&D) → H17 (repurchases) → H19b (Chang external funding) → H20b (Chang debt choice)

First in audit order.

### Q2 cluster — channel / mechanism (6 suites)

Does the effect run through a plausible channel?

H1.1 (TSIMM × cash) → H1.1b (binary TSIMM × cash) → H1.2 (rating constraint × cash) → H13.1 (TSIMM × capex) → H13.2 (capex lead horizon) → H22 (Hoberg-Maksimovic equity delay constraint)

### Q3 cluster — information content / market listening (14 suites)

Is the market actually listening?

H5 (analyst dispersion) → H7 / H7b / H7c / H7d / H7e (Amihud illiquidity, 5 suites) → H14 / H14b / H14c / H14d / H14e (bid-ask spread, 5 suites) → H18 (CCCL LPM) → H18b (CCCL Logit) → H21 (SEC letters fwd count)

### Q4 cluster — construct validation / reverse direction (7 suites)

Is the IV just a macro proxy?

H11 (PRisk contemp) → H11-Lag1 / H11-Lag2 (PRisk lags) → H23 (TSIMM firm-year) → H24 (US EPU) → H24b (Global EPU) → H25 (GPR)

**7 suites.**

### Totals

Q1 (10) + Q2 (6) + Q3 (14) + Q4 (7) = **37 suites** matching GAT entries. Q5 + Q6 cross-cutting, handled at end.

### Edge-case flags (decide during dialogue)

- **H5 (dispersion)**: provisionally Q3 (info content via analyst channel). Alternative: Q1 (direct outcome on analyst disagreement). Decide when H5 dialogue opens.
- **H22 (equity delay constraint)**: provisionally Q2 (constraint channel). Alternative: Q1 (direct outcome on a financial-structure variable). Decide when H22 dialogue opens.
- **H19b / H20b (financing-mix)**: provisionally Q1 (direct outcome). Alternative: Q3 (information content via financing decisions reflecting market awareness). Decide at audit time.

---

## 4. Per-suite audit records

### 4.0 Shape

Each audited suite produces **two things**:

**(a) One row** in the summary table below (§4.1) — 7 columns, populated at dialogue step (v).

**(b) One block** (§4.2+) — the fuller narrative per suite: DV, N, FE ladder, tail, cluster, key cell facts, reader-question argument, verdict, rationale. Dialogue transcript (adversarial counter-arguments, user pushback) lives in chat history + git log, NOT in the block.

### 4.1 Summary table (7 columns)

| suite_id | DV | N_range | reader_Q | key_cell_fact | verdict | rationale |
|---|---|---|---|---|---|---|
| _pending_ | | | | | | |

### 4.2 Per-suite blocks

_Populated during audit. One block per suite, template:_

```
### H<id> — <title>

- **DV**: <name>
- **N**: <range>
- **FE ladder**: <ind/firm/YQ combinations>
- **Tail**: <one-tailed β<direction> / two-tailed>
- **Cluster**: <firm-only / two-way>
- **Key cell fact**: <the single most load-bearing observation>
- **Reader-question**: Q<n> — <short restatement>
- **Argument**: <1-2 sentence honest case that cells answer the Q>
- **Verdict**: KEEP / DROP / REFRAME
- **Rationale**: <final 1-2 sentence reasoning after dialogue>
```

---

## 5. Cross-cutting observations

_Empty. Populated when patterns emerge across multiple suites that affect how subsequent suites are read. Examples of what belongs here (not yet populated):_

- UncAnsMgr robustness pattern across the Q1 cluster — where firm-FE survives, where it dies.
- CEO/Pre contradiction pattern (e.g., suites where UncPreMgr flips sign between related DVs — flagged per `feedback_ceo_noisy_mgr_central.md`).
- Sample-size bands and what they imply for generalizability (H22 annual, H5 IBES Detail, H20b Chang sample).
- Q5 economic magnitude sweep (cross-cutting, at end of audit).

---

## Appendix A. Carry-over pipeline bug list (code fixes already applied, historical reference)

Recorded in git commits c46e655 → bf9f366 (2026-04-14 architectural rewrite + LaTeX audit fixes). Detailed record in `memory/project_draft_playing_it_safe.md` and `memory/project_completed_milestones.md`. Not reproduced here — the audit proceeds assuming these are stable.
