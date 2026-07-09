# DEFENSE LEDGER (single source of truth for defense prep; append-only, commit after every chunk)

Governing rules:
- NO DELEGATION (Sina 2026-07-09): all research/analysis done by the main session, recorded here as learned.
- Every claim carries a source (URL or file:line). Unverified = marked UNVERIFIED.
- Honesty floor (handoff Sec 3) binds every answer drafted here.
- Nothing goes on a slide or in the talk script without Sina ratification (status column).
- Companion index: `_DEFENSE_PREP_STATE.md` (pipeline + slide ratification grid).

---

## A. COMMITTEE INTEL

### A1. Dr. Shantanu Dutta (Telfer)
(pending; researched by main session, sources recorded per fact)

### A2. Dr. Rengong (Alex) Zhang (Telfer)
(pending)

### A3. Supervisors' known positions
- Dr. Ali Akyol, Dr. Harshit Rajaiya: co-advisors; approved the thesis register. (No dossier needed; they are allies. Intel from Sina welcome.)

---

## B. QUESTION BANK (attack matrix)

Schema: | Q-ID | Question (as examiner would say it) | Lens/source | Threat (H/M/L) | Honest answer (floor-compliant) | Grounding | Backup slide | Status |

Seed set from handoff Sec 5 (to be expanded by my own lens passes + committee intel):

| Q-ID | Question | Lens | Threat | Answer sketch | Grounding | Backup | Status |
|---|---|---|---|---|---|---|---|
| Q1 | Where is your identification? This is all correlation. | econometrics | H | Concede by design: descriptive within-firm regularity; thesis never claims causality; contribution is characterizing the pattern. | thesis 2.4, 3.1; floor | S14 | drafted |
| Q2 | UncResCEO is a generated regressand; your SEs are wrong. | econometrics | H | Residual is the DEPENDENT variable, not a regressor: no coefficient bias; first-stage noise inflates outcome noise, biasing AGAINST finding the run-up; focal tests two-tailed and survive. | thesis 2.3-2.4 (E1 rule); B6 | B6 | drafted |
| Q3 | Cash is starred, stock is not: that difference itself may not be significant (Gelman-Stern). | econometrics | H | Exactly why MA3 exists: pooled Wald on the difference, 0.0983, p=.039 two-tailed; we never argue from side-by-side stars. | tab:empire_cashspec | B7 | drafted |
| Q4 | Your stock arm is underpowered; the "concentration" may be noise. | econometrics | M | Conceded in thesis: imprecise stock arm (SE 0.0436 vs 0.0185); wording kept at "concentration", test "supportive rather than definitive". | 3.4 prose L308 | B7/B8 | drafted |
| Q5 | Why would cash acquirers hide but not stock acquirers? | M&A | M | Masking asymmetry is MOTIVATION only (stock acquirer defends its currency, manages narrative); thesis does not identify the channel. | 2.1-2.2; floor | B8 | drafted |
| Q6 | Is 15% of a residual SD economically meaningful? | M&A | M | Thesis words it "material but modest" (3.2); the claim is a readable trace, not a tradable signal; contribution is characterizing, not recommending action. | 3.2 prose L280 | S7 | drafted |

(Q7+ to be added from my committee-sim passes below.)

---

## C. NARRATIVE DESIGN (plant -> ask -> answer)

Goal (Sina, verbatim intent 2026-07-09): design the story so the committee is guided
to questions we have the answer to; they ask, we answer well, repeat. Reverse-engineer
the story AND the scrutiny.

Schema per core slide: | job | claim on screen | question it PLANTS | where answered |

(pending: filled by my slide-by-slide lens passes, then ratified as the Phase 1 message map)

---

## D. DECISIONS (Sina rulings, dated)

- 2026-07-09: Beamer / 20 min / ~15 core / paper order / generated figures. (scope AskUserQuestion)
- 2026-07-09: 5-phase pipeline approved; tiered walkthrough (7 deep: S2,S3,S7,S8,S9,S10,S14; rest batched).
- 2026-07-09: Phase 0 = committee research AND narrative reverse-engineering, both careful.
- 2026-07-09: NO DELEGATION; main session does everything; ledger-first durability.
- Talk length = 20 min confirmed; date unknown.

---

## E. LEARNING LOG (process, as-learned)

- 2026-07-09: Ledger conflation caught during slide build: 0.7530/0.8519 belong to CashRatio (validity cols 1-2, one-tailed), NOT HighCash (0.1754/0.1921, cols 3-4). Slides corrected before commit. Lesson: never quote a ledger number without opening the table.
- 2026-07-09: Two-way clustering note (C6, p=.043) exists ONLY in claim ledger `_open_decisions_resolved`, NOT in thesis prose: deliberately not claimed on slides. If an examiner asks about clustering, it exists as a private rerun (tmp/cashspec_twoway_cluster.py, holds at 5%) but IS NOT in the defended document; answer must flag that distinction.
- 2026-07-09: Subagent delegation for defense prep banned by Sina; all analysis in-session, recorded incrementally.
