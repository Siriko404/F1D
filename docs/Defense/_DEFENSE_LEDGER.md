# DEFENSE LEDGER (single source of truth for defense prep; append-only, commit after every chunk)

Governing rules:
- NO DELEGATION (Sina 2026-07-09): all research/analysis done by the main session, recorded here as learned.
- Every claim carries a source (URL or file:line). Unverified = marked UNVERIFIED.
- Honesty floor (handoff Sec 3) binds every answer drafted here.
- Nothing goes on a slide or in the talk script without Sina ratification (status column).
- Companion index: `_DEFENSE_PREP_STATE.md` (pipeline + slide ratification grid).

---

## A. COMMITTEE INTEL

### A1. Dr. Shantanu Dutta (Telfer) — researched 2026-07-09 (main session)

Profile: Full Professor of finance, Ian Telfer Fellowship in Global Finance. Research: M&A,
media coverage + financial decisions, corporate governance, market efficiency, dividend policy,
ML/NLP in financial decisions. [https://telfer.uottawa.ca/en/directory/shantanu-dutta/]

Key papers (Google Scholar v9T9-D0AAAAJ + Telfer directory):
- Long-term performance of acquiring firms, JBF 2009 (298 cites)
- Does payment method matter in cross-border acquisitions? IREF 2013 — METHOD-OF-PAYMENT paper
- Inside the "black box" of private in-house meetings, RAS 2018 (191 cites) — selective disclosure
- Does governance quality influence insider trading around private meetings? Acct Horizons 2023
- Does media coverage affect credit rating change decisions? JBF 2022
- Using 10-K text to gauge COVID-related corporate disclosure, PLOS ONE 2024 — textual analysis
- CEO power + M&A (JMFM 2011); CEO tenure + M&A (FRL 2020); Are good performers bad acquirers? (FM 2012)
- Do say-on-pay votes affect M&A decisions? JCF 2025

Methodological taste: event studies, panel corporate finance, TEXTUAL ANALYSIS + NLP/ML
(active interest), media data, insider-trading data. He knows earnings-call/disclosure
literature first-hand (private meetings work).

READ: He is the closest thing to a domain expert on this thesis's intersection
(M&A x textual disclosure x private information flows). Expect informed, specific questions,
not generic ones. UNVERIFIED: no direct statement of his causality standards found.

### A2. Dr. Rengong (Alex) Zhang (Telfer) — researched 2026-07-09 (main session)

Profile: joined Telfer 2024 (accounting; directory now shows Associate Professor), PhD
U Alberta, ex-City University of Hong Kong. Research: big data / alternative data,
workplace safety + labor ESG, capital markets. Certified fintech / big-data / ESG.
[https://telfer.uottawa.ca/en/directory/rengong-alex-zhang/]

Key papers:
- Does Sunlight Kill Germs? Stock Market Listing and Workplace Safety, JFQA 2023 (listing
  status -> monitoring; quasi-experimental taste)
- Short-Selling Pressure and Workplace Safety, Organization Science 2023
- Media Co-coverage and Overreaction in Cross-Industry Information Transfers, EAR 2024
- Post-Earnings-Announcement Drift and Parameter Uncertainty, RQFA 2020 — UNCERTAINTY + PRICES
- Voluntary Risk Disclosures of Entrepreneurial Firms (OTC), 2025 preprint — DISCLOSURE
- Competition and Slack, JOM 2022
Teaches Data Analytics in Accounting.

READ: alt-data/ML methodologist + disclosure/information-transfer interests. Expect
data-pipeline drilling (speaker attribution, lexicon choice vs modern ML), media/information
-transfer confounds, and price-based "does the market see it?" questions (his PEAD +
parameter-uncertainty paper makes the bid-ask/returns angle personal).

### A2b. Sina-sourced intel (not web; higher trust)
- Dutta LIKES QUICK DEFENSES (grad-office hearsay, 2026-07-09). STRATEGIC IMPLICATION:
  hit 20 min cleanly or under; no meandering; lead to results fast; do not over-explain
  setup; have crisp answers ready so Q&A does not drag. This favors a tight, findings-
  forward talk track. RATIFIED as a planning constraint 2026-07-09.

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

Examiner-derived (from A1/A2 dossiers, drafted 2026-07-09):

| Q-ID | Question | Lens | Threat | Answer sketch | Grounding | Backup | Status |
|---|---|---|---|---|---|---|---|
| Q7 | Payment method is endogenous (his IREF 2013): firms CHOOSE cash vs stock. Isn't your "concentration" just selection into payment method? | Dutta/M&A | H | Concede: no identification claimed; arms differ observably and thesis discloses it. Firm FE absorb time-invariant selection; comparison is "managed" (>=half definitions); claim is a within-firm descriptive contrast, cause leg n.s. keeps even the cash build-up non-specific. The pattern is worth documenting whichever way selection runs. | 2.2, 3.4, floor | B8 | drafted |
| Q8 | Your own committee member showed firms hold private in-house meetings (RAS 2018). Private communication could drive both scrutiny and the residual. | Dutta/disclosure | M | Unobserved channel, concede openly: we cannot rule out private communication; the finding stands on the PUBLIC record: the run-up is in the public call regardless of what happens privately; mechanism explicitly open. | floor; 4.1 | B9 | drafted |
| Q9 | Does the language run-up line up with price run-up or insider trading before announcement? | Dutta/M&A | M | Not tested; scope is the spoken record. Bid-ask result suggests the residual is NOT priced contemporaneously; we claim a readable trace ex post, never a tradable signal. Natural extension. | 4.2; 5 | S11 | drafted |
| Q10 | Why a word list (LM) instead of modern NLP/embeddings/LLMs? Both examiners work with ML. | Dutta+Zhang/ML | M | Comparability (DWZ decomposition is the anchor), transparency, replicability; the innovation is the RESIDUALIZATION, not the lexicon; embedding-based rescoring is a clean extension that reuses the same design. | 2.3 | B4 | drafted |
| Q11 | Does pre-announcement uncertainty predict deal quality or long-run acquirer performance (his JBF 2009)? | Dutta/M&A | L | Not tested; descriptive scope; would require outcome data joins; flagged as future work. | 5 | none | drafted |
| Q12 | Media leaks deals (Zhang EAR 2024 co-coverage; Dutta media-JBF 2022): is the elevation just RUMORED deals, where the market already knows? | Zhang+Dutta/media | M | Not controlled, concede. Partial comfort: analyst cash-scrutiny (the in-call reflection of outside attention) rises pre-announcement yet does not carry the run-up; and if rumor made the deal effectively public, the sharp PRE1->GAP announcement contrast should be attenuated, not sharp. But no media data in the thesis: open. | tab:reason_gating; 3.3 | B9 | drafted |
| Q13 | How reliable is CEO speaker attribution in Capital IQ transcripts? Tagging errors contaminate the measure. | Zhang/data | M | TO VERIFY in 2.3/appendix before ratifying: describe attribution procedure; generic answer: misattribution adds noise to the outcome, attenuating toward zero; >=5-call filter stabilizes the style FE. | 2.3 (VERIFY) | B4 | NEEDS-VERIFY |
| Q14 | If the residual carries information, why doesn't the bid-ask spread react? Isn't that a contradiction (his RQFA 2020 is prices+uncertainty)? | Zhang/prices | M | Not a contradiction under the thesis reading: the trace is statistically readable in panel data ex post, not necessarily detected/priced call-by-call in real time; scripted presentation (the managed, expected channel) does relate. Two per-component facts, no between-component test claimed. | 4.2 | S11 | drafted |
| Q15 | Did you search event windows until one worked? Why is PRE1 the window? | Zhang/multiple-testing | M | Windows are the deal's institutional states (PRE2/PRE1/GAP/POST), not a search grid; PRE2 null is the pre-trend check; the design was fixed by the private->public framing. | 2.4; tab:empire_drop_matched | B2 | drafted |
| Q16 | Why 2002-2018? Why stop in 2018? | either | L | TO VERIFY: state thesis's data-coverage rationale from 3.1/2.3 before ratifying. | 3.1 (VERIFY) | S5 | NEEDS-VERIFY |

---

## C. NARRATIVE DESIGN (plant -> ask -> answer)

Goal (Sina, verbatim intent 2026-07-09): design the story so the committee is guided
to questions we have the answer to; they ask, we answer well, repeat. Reverse-engineer
the story AND the scrutiny.

Schema per core slide: | job | claim on screen | question it PLANTS | where answered |

Slide-by-slide map (drafted 2026-07-09, main session, three lenses: econometrics / M&A / disclosure).
This IS the Phase-1 message-map draft; each row needs Sina ratification.

| Slide | Job | Question it PLANTS | Answered where | Glorious? |
|---|---|---|---|---|
| S1 title | 4-word thesis: "Cash Got Your Tongue?" | what does that mean? | S2-S3 | - |
| S2 bind | Establish organizing primitive (may stay silent / may not mislead) | "so does the language show it?" | whole deck | YES: the hook |
| S3 this paper | RQ + 3-finding preview | "how do you MEASURE that?" | S4 | yes |
| S4 measure | Style vs state; residual logic | "is the residual valid / generated-regressand?" | B4 + B6 | yes (Q2, Q10) |
| S5 data | Scope + disclosed selection | "5-call filter selection?" | inline + S14 | yes |
| S6 design | 3 analyses, one primitive | "why these windows?" | S8 | yes (Q15) |
| S7 H1 | First result: cash rises, stock noisy-null | "is stock REALLY null? size meaningful?" | S10 + B7/B8; inline 15% | yes (Q4, Q6) |
| S8 event-time | STAR figure: the round trip | "why gone at announcement but before closing?!" | S9 | YES: THE plant |
| S9 two clocks | The reading: information vs transaction clock | "is cash persistence mechanical?" | conceded inline | yes |
| S10 H1a | Formal pooled test | "Gelman-Stern? cause?" | B7 preempts; mechanism-open inline | yes (Q3) |
| S11 rule-outs | Scrutiny + bid-ask honesty | "underpowered null? market doesn't price it?" | conceded inline; Q14 answer | yes |
| S12 robustness | Pattern is not fragile | "withdrawn deals?" | B10 | yes |
| S13 contributions | 4 descriptive, to-our-knowledge | "what's new vs DWZ 2021?" | B4 + talk track | needs crisp verbal answer |
| S14 limitations | PREEMPT the causality attack before Q&A | "(defuses Q1 before it's asked)" | - | YES: the shield |
| S15 takeaways | 3 lines they remember | - | - | - |

Narrative traps found (fix candidates for Phase 1 ratification):
- T1: S3 RQ line says "receding once announced" as part of the QUESTION. As a question it does
  not violate the floor (the CLAIM slides all say "indistinguishable from zero"), but consider
  aligning the RQ wording to the floor verbatim to remove any over-reading risk. DECIDE.
- T2: No backup slide on securities-law / Reg-FD / quiet-period institutions; S2 leans on
  Basic v. Levinson + 10b-5, which invites an institutional question the deck cannot answer
  deeply. Candidate: new backup "Institutional detail: what the law does and does not require."
  DECIDE.
- T3: No backup for unobserved-channel questions (Q8 private meetings, Q12 media rumors).
  Candidate: new backup "Channels we do not observe" that concedes both openly and points to
  the scrutiny rule-out as the measurable slice. DECIDE.
- T4: Q13 (speaker attribution) + Q16 (why 2002-2018) need verification against thesis 2.3/3.1
  before their answers are ratified. VERIFY NEXT SESSION.
- T5: "What exactly is new vs DWZ?" has no single slide; the answer lives in contribution 1
  phrasing. Candidate: one line added to B4 ("DWZ decompose; we take the residual to a place
  it has not been read: the anticipatory window"). DECIDE.
- T6: 20-min timing: 15 core slides = ~80 s/slide; S8+S9 (the star) deserve 4+ min combined,
  so S4-S6 must run tight (~60 s each). Timing budget to be set in Phase 4 script. NOTE.

---

## D. DECISIONS (Sina rulings, dated)

- 2026-07-09: Beamer / 20 min / ~15 core / paper order / generated figures. (scope AskUserQuestion)
- 2026-07-09: 5-phase pipeline approved; tiered walkthrough (7 deep: S2,S3,S7,S8,S9,S10,S14; rest batched).
- 2026-07-09: Phase 0 = committee research AND narrative reverse-engineering, both careful.
- 2026-07-09: NO DELEGATION; main session does everything; ledger-first durability.
- Talk length = 20 min confirmed; date unknown.

---

## F. FULL-THESIS READ (2026-07-09, main session; entire _thesis_FLAT.tex lines 1-580 prose + previously verified tables)

SOURCE-OF-TRUTH RULE (discovered): `_thesis_FLAT.tex` is a Jun-28 SNAPSHOT and is STALE in
places (run-up table note said "placebo"; final build says "comparison"; only remaining
"placebo" in the defended doc = internal label tab:empire_drop_placebo + the deliberate
prose "managed comparison rather than an inert placebo"). VERIFY PROSE AGAINST
`thesis_draft_uottawa.tex` (Jul 3 build) from now on.

Defensive assets the thesis ALREADY contains (use these verbatim in answers):
1. Q2 generated regressand: 2.3 cites Pagan (1984) explicitly, flags two-step SEs +
   the bootstrap that would address it, notes DWZ themselves use the residual two-step.
   2.4 repeats the caveat for every design. Answer = "flagged in the thesis, with the fix named."
2. FIREWALL argument (2.2): documented pre-deal management (Louis accruals, Thewissen tone)
   operates on SCRIPTED artifacts; our DV is the unscripted Q&A, hardest to stage-manage.
   The signal is not an artifact of the tone-management literature. Strength, not gap.
3. CONSERVATIVE FLOOR (2.3): if anticipation leaks into the vetted script, the residual
   (net of UncPreCEO) UNDERSTATES the signal. Measure is a floor, not a ceiling.
4. DWZ REPLICATION (2.5, tab:dwz_replication): rebuilt their decomposition on our data:
   UncPre loading 0.089 vs their 0.093; R2 0.369 vs their ~0.36. Construct validity carries over.
5. Q15 window-searching: bins ARE the deal's institutional states; PRE2 = pre-trend check
   (0.0068 n.s. / 0.0008 n.s.); "we impose no ordering across bins, every coefficient two-tailed."
6. Q13 speaker attribution: Capital IQ transcripts "parsed so that we know each speaker's
   role and whether a turn falls in the scripted presentation or Q&A" (3.1); CEO identity from
   Execucomp monthly tenure panel; sample restricted to Execucomp coverage (~S&P 1500).
   Partial answer only: parsing accuracy itself not quantified in the thesis.
7. Sample frame: S&P1500/Execucomp restriction is DISCLOSED (3.1) and echoed in conclusion
   ("may not extend to... smaller firms outside it"). Q16 (why stop 2018): NO stated rationale
   in thesis; need Sina/production answer before ratifying.
8. All-deals robustness STRENGTHENS cash-concentration: Wald 0.1056 (p~.013) vs 0.0983
   (p=.039) first-deal (4.5, tab:rob_cashspec). Logit A: high residual -> deal next quarter
   (0.3233, p=.0008); Logit B: at e=-1, residual -> cash vs stock deal (0.7478, p=.028;
   n.s. under firm FE, disclosed).
9. Withdrawal-as-resolution numbers: peak-to-resolved 0.0687***, peak-to-gap 0.0457**
   (vs 0.0455** main); only +89 firm-quarters, power-bounded, "consistent, not independent test."
10. Static-FE cash check: no fall at announcement (-0.0012 n.s.), fall at completion
   (GAP-to-POST 0.0318***); timing conclusion survives without the dynamic term (Nickell guard).
11. Bid-ask (4.2): residual inert in ALL 12 specs; UncPre positive contemporaneous in 4/6
   (incl. all 3 firm-FE cols), one-tailed; ClarityCEO null throughout; "we do not test the
   between-segment difference directly"; interpretation payoff: run-up unlikely to be an
   artifact of OUTSIDER reaction -> read as insider-side signal ("supportive, not proof").
12. Hedged register lines worth SPEAKING verbatim: "we interpret, and we do not detect"
   (H1a); "silence speaks" (Hollander hook); "the empty cell is where this paper sits" (2.1
   positioning); "material but modest" (magnitudes); "a failure to find, not a powered
   equivalence test" (scrutiny).
13. GAP cash caution (3.3): cash persistence rests on ABSENCE of PRE1->GAP decline
   (GAP level 0.0055 n.s. by itself). Do not overstate "cash stays elevated."
14. Cash-arm corroboration on second sample (tab:empire_drop_placebo col 1): PRE1 0.0486***,
   GAP 0.0058 n.s., drop 0.0428*; stock arm PRE1 -0.0404 n.s., PRE1-GAP -0.0756* "we do not
   read as directional."
15. Convergent validity honesty (2.5): PRisk assoc. economically trivial (R2~0.003); EPU/GEPU
   identified only by within-year aggregate co-movement; "supportive but weak."

## E. LEARNING LOG (process, as-learned)

- 2026-07-09: Ledger conflation caught during slide build: 0.7530/0.8519 belong to CashRatio (validity cols 1-2, one-tailed), NOT HighCash (0.1754/0.1921, cols 3-4). Slides corrected before commit. Lesson: never quote a ledger number without opening the table.
- 2026-07-09: Two-way clustering note (C6, p=.043) exists ONLY in claim ledger `_open_decisions_resolved`, NOT in thesis prose: deliberately not claimed on slides. If an examiner asks about clustering, it exists as a private rerun (tmp/cashspec_twoway_cluster.py, holds at 5%) but IS NOT in the defended document; answer must flag that distinction.
- 2026-07-09: Subagent delegation for defense prep banned by Sina; all analysis in-session, recorded incrementally.
- 2026-07-09 STALENESS AUDIT (Sina asked "are your docs outdated?"): NO.
  (a) Slide numbers were verified against _tables_from_bible.tex (Jul 3, current) — safe.
  (b) All 5 slide prose quotes (sample line, fifteen-percent magnitude, contributions
  enumeration, "concentrated", "indistinguishable once announced") re-verified PRESENT in
  the Jul 3 body files (_abstract_body/_intro_body/sec34_body_from_ledgers/_conclusion_body).
  (c) FLAT's staleness delta was confined to table-note wording (placebo->comparison),
  which the slides never used. (d) Ledger Q&A answers predate the full read -> not wrong,
  but B-section answers should be UPGRADED with section-F assets before ratification.
  Build structure noted: thesis_draft_uottawa.tex inlines ch1-2 prose and \inputs the
  abstract/intro/sec34/conclusion bodies + tables (input map at its lines 122-353).
