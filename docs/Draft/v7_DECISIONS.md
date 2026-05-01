# v7 Thesis Draft — Decisions Ledger

**Started:** 2026-04-29
**Workflow:** big-picture → small-picture, branch-by-branch, step-by-step
**Existing draft:** to be archived (not deleted) inside `docs/Draft/`. New v7 draft built parallel.

---

## Process / current step

- [x] Step 0a — open decisions ledger
- [x] Step 0b — read template + extract structure constraints
- [x] Step 1 — lock thesis structure (D1-D27 below)
- [x] Step 2C — Lerman pub year verification (lerman2024 → lerman2026, commit e6aba60)
- [x] Step 2B — disclosures inventory (now 11 active + 13 dropped + 2 retired after D25-D27)
- [x] Step 2D — §III.E endogeneity scrub (D25-D27 dropped Death DiD + DWZ FD + Lewbel IV; SUPERSEDED by D29+D30+D31 — §III.E populated with H1.2 + H1.3 two-trigger modus-tollens close)
- [x] Step 2E — endo research brief written for ChatGPT Deep Research outsourcing (`docs/Draft/v7_ENDO_RESEARCH_BRIEF.md`, commit bbf147b; red-team audited, all 10 priority edits applied)
- [x] Step 2F — endo strategy selection (CLOSED 2026-05-01 per D29+D30+D31; AJCA dropped via DFF 2011 NLM session 17c2f9fc; ACLW 2012 dropped via NLM session a1a6268f; §III.E = H1.2 Unrated × UncResCEO + H1.3 CFvol × UncPreCEO two precautionary triggers + limitation paragraph; no DiD/IV pursued)
- [ ] Step 2A — per-subsection claim cards (~12-15 cards → v7_CLAIM_CARDS.md) — paused mid-tutorial; needs full restart given §III.E reframe
- [x] Step 3 — lock narrative anchor (COMPLETE 2026-05-01; all 6 beats locked: Beat 1 headline / Beat 2 DWZ method / Beat 3 two triggers / Beat 4 construct validity / Beat 5 outsider reaction / Beat 6 endogeneity; 7 NLM verbatim verification calls used; D28 per-unit approval honored throughout)
- [x] Step 4 — archive v6 → `docs/Draft/_archived_v6_2026_04_29/` (2026-04-30; 24 renames via git mv: main.tex/main.pdf/sections/* + 7 v6 design+audit md files; nested `_archived_2026_04_22/` consolidated; build artifacts removed)
- [ ] Step 5 — scaffold blank v7 LaTeX set (two-column top-journal per template)
- [ ] Step 6 — populate prose big-picture-first
- [ ] Step 7 — wire generated tables + variable definitions appendix + bibliography
- [ ] Step 8 — compile + audit + commit

## Pre-compaction state (2026-04-29 LATE×12)

**Branch:** master at `d33bde9` (5 commits ahead of pre-compact origin).

**Durable artifacts on disk:**
- `docs/Draft/v7_DECISIONS.md` — this file (D1-D24 ledger)
- `docs/Draft/v7_DISCLOSURES_INVENTORY.md` — 26 honest disclosures inventoried with v7 home assignments
- `tmp/suite_spec_index.json` — per-cell β/p/n for 15 body-cited suites

**Memory handoff:** `project_session_2026_04_29_v7_pre_compact.md` (newest CURRENT STATE entry in MEMORY.md).

**User's last instruction before pause:** "your explanation is too long, and too hard to understand. pause here. record EVERYTHING and prepare for compaction thoroughly". Future endogeneity tutorials in Step 2A walkthrough must be SHORTER + simpler step-by-step. User does not know endogeneity well.

---

## Template — read 2026-04-29

**Source:** `docs/Draft/DraftTemplate.txt`

**Style mandate (line 1):**
> two column style mandatory with traditional styling, according to fin/econ traditional top journal design.

**Roman-numeral section convention** (I. II. III. IV. V.).

**Structure outline (per template):**

| Section | Subsections (template guides) |
|---|---|
| Title block + abstract | Title / Authors / Affiliations / Abstract / Keywords / JEL |
| **I. Introduction** | (single block in template — sub-structure thesis-author choice) |
| **II. Conceptual Framework and Empirical Strategy** | (5 subsections suggested) Conceptual Framework / [Theory + Main Construct + Research Logic] / [Estimation of Main Variable(s)] / [Methodology / Empirical Design] / [Specification and Measurement of Key Constructs] |
| **III. Main Empirical Analyses** | (4 subsections suggested) Data / Sample / Variable Construction / Main Analysis 1 / Main Analysis 2 / Main Analysis 3 |
| **IV. Additional Analyses** | (2 subsections suggested) Additional Analysis 1 / Additional Analysis 2 |
| **V. Conclusion** | (single block) |
| **References** | apacite |
| **Appendix: Variable Definition and Measurement** | Dependent Variables / Independent Variables |
| **Tables** | T1 Summary Stats + 8 main tables T2-T9 |

**Implications for v7 structure:**
- Tighter than v6 (v6 had §2.1 Pre-Commitment + §3.5 Robustness Notes + §4.3.5 Asymmetry that don't map to template subsections)
- Template suggests 4 main analyses in §III not 5 (collapse §3.5 robustness into §3.1 setup; collapse HC + HFC + CFvol into 3 main analyses)
- Template suggests 2 additional-analysis blocks in §IV not 3 (collapse drivers + reaction + endogeneity into 2 blocks, OR keep as 3)
- Tables: 9 max suggested. Currently we have 14+ body suite tables. Demands prioritization.

---

## Decisions log (chronological)

### D31 — 2026-05-01 — §III.E closed with two precautionary triggers (H1.2 Unrated + H1.3 CFvol); DiD search abandoned; rest acknowledged as limitation
**Trigger:** After 6 endo strategies dropped (Death/DWZ-FD/Lewbel/Weather/AJCA/ACLW) and a survey of remaining DiD candidates (Hassan 2019 QJE political-risk text, Brexit, 9/11 geographic, hurricanes) showed each likely fails the dual-mechanism contamination test — requirement 2 of the DiD requirement set: shock must operate through speech as a narrow channel, not in parallel with a direct-on-cash mechanism — user closed the endo search.

User: "no need. we will close the endo section with the two precautionary triggers we found significant and recognize the rest as limitation."

**Decision:** §III.E body presents two pre-existing modus-tollens precautionary triggers as the endogeneity defense:

- **H1.2 Unrated × UncResCEO** — financing-constraint precautionary trigger anchored Acharya-Almeida-Campello (ACW) 2004 cash-flow sensitivity asymmetry. Empirical: UncAnsMgr_c × Unrated contemp 4/4 + lead 4/4 cells significant p<0.05 (β +0.004 to +0.011); UncAnsCEO_c × Unrated robustness contemp 4/4 sig (`_partition_findings.csv`).
- **H1.3 CFvol × UncPreCEO** — cash-flow-volatility precautionary trigger anchored Han-Qiu 2007 16-quarter CV(CF). Empirical: UncPreCEO_c × HighCFvol contemp β=0.0048 p=0.026 sig (`outputs/econometric/h1_3_cfvol_moderation/2026-04-29_142744/regression_results_col5.txt`); UncResCEO × HighCFvol null (β=0.0004, p=0.86).

The two triggers cover the two load-bearing components of the DWZ 2021 speech-uncertainty decomposition: H1.2 forward-direction defense on the **Residual** component (UncResCEO) via constraint amplification; H1.3 forward-direction defense on the **Presentation** component (UncPreCEO) via volatility amplification. Together, the construct's two empirical pieces each carry a separate forward-direction sign-test under modus tollens.

**No DiD test pursued.** Remaining candidates (Hassan 2019 QJE, Brexit, 9/11, hurricanes) are NOT NLM-verified, and the dual-mechanism risk on each is high enough that further search is judged not cost-effective.

**Limitation language (load-bearing for §III.E body or §V.2 Limitations):**
- Forward speech→cash direction is identified via cross-sectional modus tollens on two pre-registered precautionary triggers, not via an exogenous-shock DiD or external instrument.
- Six DiD/IV designs were considered and dropped: Death DiD [D25], DWZ first-difference [D26], Lewbel heteroskedasticity-IV [D27], weather-shock, AJCA repatriation [D29], ACLW long-term-debt-maturity [D30]; each failed for design-specific reasons documented in those D-entries.
- Any future-work DiD-as-IV defense compatible with our forward identification must satisfy the full requirement set: (i) exogenous to firm cash policy, (ii) narrow speech channel — not parallel with a separate direct-on-cash mechanism, (iii) direction-compatibility on any non-speech channels, (iv) first-stage on speech actually fires, (v) cross-sectional intensity variation, (vi) parallel trends on cash AND speech, (vii) top-tier anchor (JF/JFE/RFS/AER/JPE/QJE/JAR/JAE/RAST/CAR/ReStud/JoE/JBES/ReStat/ManSci), (viii) adequate treated-firm count.
- Hassan-Hollander-vanLent-Tahoun 2019 *QJE* political-risk text data × 2016 election interaction is the strongest a-priori remaining candidate but is not pursued in this paper.

**Implications:**
- §III.E body prose draft requires Beat-6 narrative anchor + per-unit approval before writing (per D28).
- D15 ("§III.E EMPTY pending new design") superseded LATE×16 (revised entry below).
- v7_DISCLOSURES_INVENTORY.md disclosure #13 reframes once more: "Forward direction identified via cross-sectional modus tollens on two precautionary triggers; no DiD or IV pursued; six candidate designs dropped during search."
- Step 2F closed in process tracker (above).

**Memory:** `project_session_2026_04_30_endo_h1_2_locked.md` updated post-decision; `MEMORY.md` index entry refreshed.

### D30 — 2026-04-30 — ACLW 2012 long-term-debt-maturity DiD dropped (dual-mechanism contamination)
**Trigger:** ChatGPT Deep Research returned Almeida-Campello-Laranjeira-Weisbenner (ACLW) 2012 *Critical Finance Review* "Corporate Debt Maturity and the Real Effects of the 2007 Credit Crisis" as a top DiD candidate after AJCA fell. NotebookLM verification (session a1a6268f) closed against ACLW.

**Verbatim findings:**
- §2.3: "In our base experiment, the outcome variable is the change in firm investment... Investment is defined as the ratio of quarterly capital expenditures (capxy) to the lag of quarterly property, plant and equipment (ppentq)." Cash holdings (cheq) is NOT a regression outcome — only used as a matching control.
- Figure 4 ("How Did Treated Firms Pay Off Their Debt?"): treated firms REDUCED cash holdings during the post-shock window (Q1-Q3 2008 vs Q1-Q3 2007) to pay maturing long-term debt.
- §4.3.1 + Table 6: parallel trends evidence is on INVESTMENT only — not on cash or speech uncertainty.
- Treated definition (§2.3): dd1/(dd1+dltt) > 20% (15%/25% robustness). 86 treated, 79 unique controls. Pre = Q1-Q3 2007, Post = Q1-Q3 2008, cutoff = Q4 2007 (BNP Paribas SIV run, August 2007).

**Decision:** ACLW 2012 design dropped from v7 endo strategy search.

**Rationale:** Our forward story is precautionary cash hoarding (speech↑ → cash↑). ACLW shock simultaneously (a) raises CEO speech uncertainty via refinancing pressure AND (b) FORCES cash deployment via the SEPARATE channel of paying maturing debt. Cash moves OPPOSITE the predicted precautionary direction; the two channels run in opposite directions through SEPARATE mechanisms — refinancing-pressure effect on language vs forced-deployment effect on balance sheet. Adapting ACLW for our question contaminates the speech→cash identification with a non-speech channel pulling cash the other way. Additionally: CFR is not in the stated top-tier list (JF/JFE/RFS/AER/JPE/QJE/JAR/JAE/RAST/CAR/ReStud/JoE/JBES/ReStat/ManSci) — yellow flag preceding the verbatim finding.

**Memory references:** `reference_almeida_campello_laranjeira_weisbenner_2012_verbatim.md`; NLM session a1a6268f.

### D29 — 2026-04-30 — AJCA 2004 repatriation tax shock dropped (DFF 2011 cash null)
**Trigger:** ChatGPT Deep Research returned the American Jobs Creation Act 2004 (HIA §965) repatriation tax holiday as a top-tier endo candidate (top-tier anchor: Dharmapala-Foley-Forbes 2011 *Journal of Finance*). User asked NLM verification on the cash-response question. NotebookLM session 17c2f9fc on DFF 2011 "Watch What I Do, Not What I Say" closed against AJCA.

**Verbatim findings:**
- §V.A Footnote 26: cash holdings did NOT increase in 2005 alone post-AJCA, in either the full sample or the financially-constrained subsample.
- §V.B Footnote 30: three-year average 2005-2007 cash holdings showed NO increase post-AJCA in either subsample (full or financially-constrained).

**Decision:** AJCA dropped from v7 endo strategy search.

**Rationale:** Forward story (CEO speech uncertainty → cash) requires the shock to MOVE cash holdings post-treatment so a first stage can identify the speech→cash arrow. DFF 2011 — the load-bearing public-finance paper on AJCA outcomes — verbatim shows cash did not move at any horizon (single-year or three-year) in any subsample. No cash response = no first stage available = AJCA cannot identify the speech→cash arrow even in principle.

**Memory references:** NLM session 17c2f9fc; locked memory `project_session_2026_04_30_endo_h1_2_locked.md`.

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

### D27 — 2026-04-29 LATE×15 — Lewbel IV dropped entirely; §III.E empty pending new design
**Trigger:** during teacher-mode walkthrough of remaining endo suite (Lewbel) following D25 + D26. User accepted my honest adversarial assessment: Wu-Hausman p=0.24 fails to reject OLS-consistency; Lewbel's identifying assumption (heteroskedasticity exogenous to cash equation) was not formally validated; the same unobserved factors driving endogeneity in our setting plausibly drive residual heteroskedasticity, which would invalidate the design. Plus: 5× point-estimate gap between OLS and 2SLS not statistically separable from sampling noise.

**Decision:** Lewbel IV removed from v7 entirely. §III.E empty pending new design selection.

**User direction:** "we must look for one real and solid endo test, which addresses the reverse causality problem. the theory needs to be extremely solid, regardless of its findings."

**Implications:**
- §III.E is empty pending new design choice. Three options live: (a) ARJOA 2004 repatriation cash-shock DiD on speech outcome (tests reverse direction directly), (b) Granger-Sims temporal-precedence VAR test, (c) drop §III.E entirely and rely on main-panel FE ladder + lead-DV.
- 4 disclosures DROPPED: #8 (Sargan col 3 fail), #9 (Stock-Yogo borderline weak), #10 (Wu-Hausman fail-to-reject), #11 (5× attenuation pattern).
- Disclosure #21 (Lewbel + Bates not stat-distinguishable) DROPPED.
- Disclosure #13 RETIRED entirely (no §III.E threats package framing applicable if §III.E empty).
- Code/data preserved on disk: `src/f1d/econometric/run_h_lewbel_iv_*.py` (or actual filename), `outputs/econometric/h_lewbel_iv_cash/`, `docs/Draft/per_suite/h_lewbel_iv_table.tex`. Bib entry `lewbel2012` STAYS pending decision.
- `config/suite_render_order.yaml` — `H.lewbel.iv` removed from both `suites:` and `thesis_suites:` lists with comment.

**v7 endo defense after D25 + D26 + D27 (current state):**
- Main panel: firm FE absorbs time-invariant U + lagged DV + lead DV (4-step FE ladder)
- §III.E: EMPTY — pending new design proposal
- Selection threat orphaned (settled in lit)

### D26 — 2026-04-29 LATE×14 — DWZ FD dropped entirely from v7
**Trigger:** during teacher-mode walkthrough of remaining endo suites (DWZ FD + Lewbel) following D25's Death DiD drop. User identified the same redundancy pattern that killed Death DiD: DWZ FD addresses "time-invariant unmeasured firm traits" — a threat that firm FE in the main panel ALREADY mathematically absorbs. Within-firm transformation (firm FE) and first-difference produce equivalent identification of β under classical assumptions. No reviewer would credit FD as an endogeneity defense for a threat firm FE already handles.

**Decision:** DWZ FD removed from v7 entirely. No body §III.E panel. No robustness paragraph in §III.B. No future-work mention. Like Death DiD: "as if it never existed."

**Implications:**
- §III.E becomes single-suite Lewbel IV (see D15 revision). Not a composite table anymore — a regular regression table.
- 3 disclosures DROPPED from v7_DISCLOSURES_INVENTORY.md: #5 (FD identifies ClarityCEO only), #6 (FD design deviations FF12/intangibles/Main), #7 (FD applied to cash → endogeneity stronger than Tobin's Q).
- Disclosures #12 (ID-asymmetry across designs) and #13 (multi-threats package) become OBSOLETE — only one design remains. #12 retired entirely. #13 reframes from "2-threats" → "Lewbel addresses one specific threat: speech-direction reverse causality + measurement error + time-varying confounders, complementing main-panel firm FE coverage of time-invariant U."
- Code/data preserved on disk: `src/f1d/econometric/run_h_dwz_fd_cash.py` (or whatever the runner is named), `outputs/econometric/h_dwz_fd_cash/`, `docs/Draft/per_suite/h_dwz_fd_table.tex`. NOT cited in v7. Bib entry `dzielinski2021` STAYS — heavily cited elsewhere as our anchor paper.
- `config/suite_render_order.yaml` — `H.dwz.fd` removed from both `suites:` and `thesis_suites:` lists with comment.

**v7 endo defense after D25 + D26:**
- Main panel: firm FE + lagged DV + lead DV (the 4-step ladder is itself the primary endo defense)
- §III.E: Lewbel IV (single suite) — addresses speech-direction reverse causality + measurement error + time-varying confounders
- Selection threat (firms self-selecting CEOs): orphaned, acknowledged settled in lit
- Time-invariant firm U: handled by firm FE in main panel (not by §III.E)

### D25 — 2026-04-29 LATE×13 — Death DiD dropped entirely from v7
**Trigger:** user pushed back during teacher-mode tutorial. Chain of audit:
1. Initial framing claimed Death DiD "kills reverse causality." User challenged.
2. Conceded: Death DiD on cash measures CEO-identity → cash, NOT speech-uncertainty → cash arrow direction.
3. Reframed as "tests CEO-autonomy prerequisite." User: "OF COURSE CEO AFFECTS CASH! NOBODY WOULD POINT THAT AS AN ERROR!"
4. User correct — CEO-autonomy is settled (Bertrand-Schoar 2003 onward). Testing settled question with weak design (n=8, pre-trend mean reversion, can't isolate speech, can't kill within-CEO reverse stories like cash→scrutiny→speech) = filler.

**Decision:** Death DiD removed from v7 entirely. No body §III.E panel. No footnote. No future-work mention. Like it never existed in the v7 paper.

**Implications:**
- §III.E becomes 2-panel composite (DWZ FD + Lewbel IV) — see D15 revision.
- 5 disclosures DROPPED from v7_DISCLOSURES_INVENTORY.md: #1 (pre-trend mean reversion), #2 (lagged-DV exclusion BMD 2004), #3 (16-cluster threshold), #4 (heterogeneity infeasible at n=8), #19 (Death power-limited in §V Limitations). Disclosure #12 (ID-asymmetry across designs) revised to 2-design package. Disclosure #13 reframed: 2-threat package (omitted-variable + reverse-direction-via-Lewbel).
- Code/data preserved on disk: `src/f1d/econometric/run_ceo_death_did_cash.py`, `outputs/econometric/ceo_death_did_cash/`, `data/raw/ceo_death_events/`. NOT cited in v7. Available if larger-sample extension is ever revisited.
- `config/suite_render_order.yaml` — `H.death.did` removed from both `suites:` and `thesis_suites:` lists with comment.
- Bibliography: `bennedsen2020` and `ghafoor2023` cite-keys orphaned in v7 prose; bib entries stay (low cost).

**Cleaner threat coverage in v7:**
- DWZ FD: time-invariant unobserved firm traits (omitted-variable from constant-per-firm sources)
- Lewbel IV: speech → cash direction (kills reverse causality including user-named scrutiny + empire-building mechanisms; also addresses measurement error and time-varying confounders)
- Selection threat (firms self-selecting CEOs based on cash needs): NOT addressed. Acknowledged as open in §V.2 Limitations if needed; settled in literature so likely no referee push-back.

### D24 — 2026-04-29 — Pre-Commitment Statement formally killed
**Decision:** v6 §2.1 Pre-Commitment Statement removed entirely from v7. Pre-registration framing absorbed into §II.2 Hypothesis Development (each hypothesis has its formal statement + theoretical anchors + tail direction stated explicitly).
**Rationale:** v6 §2.1 was empirical filler — every load-bearing claim was restated in §2.4 (now §II.2) or §1.4 (now §I).

### D23 — 2026-04-29 — Wide regression tables = sidewaystable* (landscape pages)
**Decision:** Standard JF/JFE/RFS practice for 12-column regression tables. Body in two-column; wide tables on dedicated landscape pages with content upright.

### D22 — 2026-04-29 — §V Conclusion structure = 3 subsections (Summary / Limitations / Future Work)
**Decision:** Deviation from template's single-block §V (template line 94-96). Three subsections give navigable structure for committee/referee review.

### D21 — 2026-04-29 — Tables placement = end of document (after refs + appendix)
**Decision:** Per template line 116. Standard for top-journal submission.

### D20 — 2026-04-29 — Variable Definitions appendix = 4 sections (DV / IV / Controls / Moderators)
**Decision:** Top-journal navigability beats template's 2-section minimum. DV (Cash, Lead Cash, Spread, CCCL); IV (ClarityCEO, UncResCEO, UncPreCEO, drivers); Controls (Bates base + extended); Moderators (Unrated, HighCFvol).

### D19 — 2026-04-29 — Hypothesis statement format = bold label + italicized declarative
**Format example:** **Hypothesis 1.** *An increase in CEO speech uncertainty during an earnings call is associated with a higher cash-to-assets ratio at the firm.*

### D18 — 2026-04-29 — §IV.B title = "Disclosure-Insufficiency Channel: CCCL"
**Verbatim source:** Lerman, Steffen, Zhang (2026?, NLM session 3f2ff407). Abstract: "the SEC primarily references these voluntary disclosures to illustrate **insufficiencies** and, less commonly, **inconsistencies** in mandatory filings". §3.2: 80% of CCCLs flag insufficient disclosure; 15% flag inconsistent info; 3% concern call disclosures themselves.
**Decision:** §IV.B subsection title = "Disclosure-Insufficiency Channel: Conference-Call Comment Letter (CCCL)". Mechanism: SEC reviewers reference the call to flag gaps in mandatory filings.
**Variable form:** binary indicator, linear probability model. Sample 2005-2018 AA, n=13,808 / 3,902 firms.
**v6 framing correction:** v6 §4.2.2 said "we measure SEC scrutiny via CCCL" — empirically loose. CCCL doesn't measure scrutiny generically; it measures specifically whether SEC references the call to flag disclosure-gap (80% of CCCLs).

### D17 — 2026-04-29 — §II.5 drivers = 1 composite table
**Decision:** Single §II.5 construct-validity table with 4 driver coefficients side-by-side as columns (PRisk + US-EPU + GEPU + TSIMM). Top-journal standard.

### D16 — 2026-04-29 — §I Introduction = single flowing block (no subsections)
**Decision:** Per template line 32-34. One coherent intro narrative — motivation → gap → approach → findings → contributions → roadmap, all in one §I.
**Implication:** v6 §I had 6 subsections; v7 collapses to one block.

### D15 — 2026-04-29 — §III.E Endogeneity = H1.2 + H1.3 two precautionary triggers (REVISED per D25 + D26 + D27 + D29 + D30 + D31)
**Original decision:** 3 panels (Death DiD + DWZ FD + Lewbel IV).
**Revised LATE×13 per D25:** 2 panels (DWZ FD + Lewbel IV). Death DiD dropped.
**Revised LATE×14 per D26:** Single Lewbel IV suite. DWZ FD dropped (redundant with firm FE).
**Revised LATE×15 per D27:** EMPTY. Lewbel dropped (Wu-Hausman fail; identifying assumption unverified). §III.E pending new design selection per user direction "one real and solid endo test addressing reverse causality with extremely solid theory."
**Revised 2026-05-01 LATE×16 per D29 + D30 + D31:** §III.E populated with H1.2 Unrated × UncResCEO (ACW 2004 modus tollens; Res-component forward-direction defense) + H1.3 CFvol × UncPreCEO (Han-Qiu 2007 modus tollens; Pre-component forward-direction defense). Two precautionary triggers cover the two load-bearing components of the DWZ speech-uncertainty decomposition. No DiD or IV pursued; six candidate DiD/IV designs dropped during search (D25-D27 + Weather + D29 + D30); limitation language explicit in body. Step 2F closed.

### D14 — 2026-04-29 — §IV.A title = "Market Information-Asymmetry Channel: Post-Call Bid-Ask Spread"
**Decision:** §IV.A subsection title locks mechanism-first naming (BGT 2018 + Amihud 2002 anchor).

### D13 — 2026-04-29 — §IV = two distinct channels (H2 market info-asymmetry + H3 disclosure-insufficiency)
**Decision:** §IV.A = H2 (market info-asymmetry channel: Spread). §IV.B = H3 (disclosure-insufficiency channel: CCCL). Two different parties (traders vs SEC reviewers) + two different processes (price formation vs disclosure-gap detection) = genuinely distinct channels.

### D12 — 2026-04-29 — §II.1 + §II.2 lit-review structure: precautionary motive + 2 triggers + specific papers
**Decision:**
- §II.1 Conceptual Framework: precautionary motive overview (OPSW 1999 + Bates 2009 anchor); points at the two testable amplification triggers
- §II.2 Hypothesis Development: full theoretical anchors for H1 + H1a + H1b
  - H1 anchor: OPSW 1999 + Bates 2009 (precautionary cash motive); DWZ 2021 (speech-uncertainty as real-time signal); BS 2003 (CEO-trait channel)
  - H1a anchor: FP 2006 (binary rated/unrated, "credit constrained") + ACW 2004 §II.D (macro-shock asymmetry)
  - H1b anchor: Han-Qiu 2007 (CFvol → cash; CV(CF) 16-quarter)
- Drop "two channels" framing; write "two triggers of the same precautionary channel"
**Each hypothesis paragraph cites its specific anchor papers explicitly.**

### D11 — 2026-04-29 — §II.2 hypothesis labels = H1 + H1a/H1b
**Decision:** H1 (main cash response) + H1a (financing-friction trigger amplification) + H1b (CF-volatility trigger amplification). Sub-letter notation reflects parent-child structure: H1a/H1b are amplification predictions UNDER H1's precautionary channel.
**Rationale:** standard top-journal practice for nested channel decomposition (cf. ACW 2004 use sub-numbered constraint tests).

### D10 — 2026-04-29 — Single precautionary channel with two triggers (supersedes D6, D9)
**Trigger:** user correction — both HFC and CFvol are SAME precautionary channel, different triggers. Not two distinct channels.
**Evidence:** Han-Qiu 2007 paper title is "Corporate Precautionary Cash Holdings" — explicitly precautionary. FP 2006 + ACW 2004 mechanism (Unrated firms hoard cash because no debt-market access) is also precautionary. The difference is what STRESS triggers the precautionary response: financing-friction trigger vs CF-volatility trigger.
**Decision:**
- §II.2 Hypothesis Development states ONE precautionary channel; H1 main effect; H1a + H1b = two amplification predictions under different stress triggers
- §III.C subtitle: "Precautionary Amplification: External-Financing-Friction Trigger" (FP+ACW)
- §III.D subtitle: "Precautionary Amplification: Cash-Flow-Volatility Trigger" (Han-Qiu)
- Drop "two channels" framing in v7 prose. Use "two triggers of the same precautionary channel".
**Implications for §IV (Spread + CCCL):** distinct from §III precautionary channel — outsider channels operate via information-asymmetry / regulatory-review mechanisms. §IV is genuinely a different mechanism, NOT a third trigger of the precautionary channel.

### D9 — SUPERSEDED by D10 — kept for audit trail
~~5-subsection §III separating HFC and CFvol as distinct "channels"~~. Subsection layout retained, but framing changes from "two channels" to "two triggers of one precautionary channel".

### D8 — 2026-04-29 — §IV.B regulatory channel terminology = CCCL not SEC
**Trigger:** user correction.
**Decision:** §IV.B variable is "Conference-Call Comment Letter (CCCL) indicator" per Lerman et al. paper title and v6 prose §4.2.2 line 44 ("conference-call-comment-letter (CCCL) indicator"). Drop "SEC Comment Letter" as the channel name in v7. Use "CCCL" or "Regulatory Channel: CCCL" as subsection title.
**Verification COMPLETE 2026-04-29:** Lerman paper publication metadata (per user-provided paper masthead): Received July 5, 2023; Revised October 1, 2024 + June 11, 2025; Accepted July 30, 2025; **Published Online in Articles in Advance January 30, 2026**. Cite key updated `lerman2024` → `lerman2026`; year updated `{2024}` → `{2026}`. Bib note now reads "Articles in Advance, Published online January 30, 2026". 3 v6 prose files updated to `\citeA{lerman2026}`.
**File reference:** `docs/Draft/references.bib` line 291.

### D7 — 2026-04-29 — §IV layout = 2 subsections (Spread + CCCL)
**Decision:** §IV.A Market Channel: Post-Call Bid-Ask Spread. §IV.B Regulatory Channel: CCCL. Matches template's 2-block §IV.

### D6 — 2026-04-29 — §III layout = HC → constraint amplification (combined) → endogeneity
**Decision:**
- §III.A Data, Sample, Variable Construction
- §III.B Cash Holdings (HC) — primary cash result
- §III.C Constraint Amplification (Unrated + CFvol combined in single subsection — ACW asymmetry test through two proxies)
- §III.D Endogeneity (Death DiD + DWZ FD + Lewbel pulled into §III as endogeneity package)
**Implications:** §IV becomes outsider-reaction-only (Spread + CCCL).

### D5 — 2026-04-29 — Drivers (PRisk + US-EPU + GEPU + TSIMM) → §II construct validity
**Decision:** Move 4 driver suites from §IV into §II.5 Specification and Measurement of Key Constructs (template's slot for measurement-construct validation). Drivers shown as construct-validity tests of CEO speech-uncertainty measure against external uncertainty drivers. 4 suites → 1 composite table or appendix table (final granularity TBD).
**Rationale:** (i) clears §IV to fit template's 2-block structure; (ii) drivers are validation of measurement, not outcome tests, so §II is theoretically correct location; (iii) reduces total table count.

### D4 — 2026-04-29 — Narrative anchor = precautionary-cash main + DWZ-extension secondary
**Decision:** Primary contribution framing is precautionary-cash (real-time CEO speech-uncertainty signal predicts firm precautionary cash holdings, anchored on OPSW + Bates). Secondary framing is DWZ-extension (the measurement architecture is borrowed and extended from DWZ 2021's three-component decomposition; we apply their architecture to a financing-policy outcome class their paper does not test).
**Implication for prose:** lead with the precautionary-cash result, follow with "we use DWZ 2021's architecture as the measurement tool, extending its application to firm financing-policy outcomes". Insider-outsider asymmetry is a third-order observation, not the headline.

### D1 — 2026-04-29 — Discard v6 paragraph-by-paragraph audit; rewrite v7 from scratch
**Trigger:** §2.1 audit revealed §2.1 = filler; §3.1 audit revealed HC/HFC/CFvol naming asymmetry. Two data points + user observation that "all of it is useless".
**Decision:** Build v7 LaTeX set fresh. Old v6 preserved in archive folder. v7 follows `DraftTemplate.txt`.
**Workflow:** big-picture → small-picture, step-by-step, branch-by-branch.
**Rationale:** v6 prose has structural cruft inherited from v5 (Mgr-pool, capex appendix, BelowIG three-tier). Audit-and-edit becomes whack-a-mole. Rewrite from locked structure faster.
**Risk:** lose 7+ honest disclosures embedded in v6 prose. Mitigation: old draft preserved; cherry-pick disclosures during v7 population.

### D2 — 2026-04-29 — Section order matches template
**Decision:** Roman-numeral sections (I-V) + Abstract + References + Appendix + Tables, exact template order.
**Rationale:** Template is mandatory — top-journal fin/econ style requirement.

### D3 — 2026-04-29 — All decisions recorded here
**Decision:** Every structural decision, scope decision, finding-include/exclude decision, narrative decision logged in this file with date + rationale.
**Rationale:** Cross-session durability; future reference; audit trail.

---

## Pending decisions (to lock in Step 1-3)

### PD1 — §III subsection count
Template suggests 4 (Data + 3 analyses). Current empirical body fits 3 main analyses (HC + HFC + CFvol) → matches template. **Lock as 1 + 3 = 4 subsections.**

### PD2 — §IV subsection count
Template suggests 2. Current §4 has 3 sub-blocks (drivers + outsider reaction + endogeneity). Three options:
- (a) Collapse to 2: e.g., "Construct Validity and Outsider Reaction" + "Identification" — drops driver/reaction asymmetry framing
- (b) Stretch to 3: keep current granularity, deviate from template's 2-suggested
- (c) Restructure: drivers move to §II (construct validity); §IV is reaction + endogeneity (=2 blocks per template)
→ NEEDS DECISION

### PD3 — Hypothesis labels (HC / HFC / CFvol)
v6 has HC + HFC formal labels in §2.4; CFvol no formal label.
Options:
- (a) Promote: H1 (HC) / H2 (HFC) / H3 (HCFvol)
- (b) Demote: drop HC/HFC labels; just use "Hypothesis 1/2/3" with descriptive subsection titles
- (c) Verbatim hypothesis statements: write each hypothesis as a numbered, italicized declarative sentence
→ NEEDS DECISION

### PD4 — Pre-Commitment Statement (v6 §2.1)
v6 §2.1 = filler per audit. Options:
- (a) Drop entirely; absorb pre-registration framing into §2.4 Hypothesis Development
- (b) Keep as 1-paragraph block at end of §II (compressed to ~80 words)
→ NEEDS DECISION

### PD5 — Empirical findings inventory — what makes the cut
v7 §III + §IV must report a tight subset. Currently 14+ suite tables exist. Template suggests 9 max. Need to lock:
- Body tables (HC main / HFC main / CFvol main) — clear KEEP
- §IV.drivers (4 drivers: PRisk + US-EPU + GEPU + TSIMM) — KEEP / DROP / which?
- §IV.reaction (Spread + SEC) — KEEP / DROP / which?
- §IV.endogeneity (Death DiD + DWZ FD + Lewbel) — KEEP / DROP / which?
→ NEEDS DECISION

### PD6 — Narrative anchor / story arc
Three candidates:
- (a) DWZ-extension thesis: "we extend DWZ 2021 from market/governance to firm financing-policy" (current v6 framing)
- (b) Insider-outsider asymmetry thesis: "two segments of the call carry signals to two audiences" (current v6 secondary framing)
- (c) Precautionary-cash thesis: "earnings-call CEO speech uncertainty is a real-time precautionary-cash signal" (closer to OPSW/Bates roots)
→ NEEDS DECISION

### PD7 — Two-column body width: text vs tables
Template mandates two-column traditional fin/econ design. Tables are wide (12 cols × bordered). Use `sidewaystable*` (current v6 approach) or condense tables to fit two-column? Top journals (JF, JFE, RFS) use sidewaystable for wide regression results — KEEP `sidewaystable*` is current default and template-compatible.
→ Recommended LOCK: keep `sidewaystable*` for body regression tables.

---

## Empirical findings inventory (Step 2 — pending)

(populated when we walk through suite_spec_index.json subsection by subsection)

---

## Narrative anchor (Step 3 — COMPLETE 2026-05-01)

### Beat 1 — Headline contribution sentence (APPROVED 2026-04-30; Option A)

> We document that within-firm increases in CEO speech uncertainty during earnings calls predict higher precautionary cash holdings, identifying a real-time signal of firm financing-policy adjustment grounded in the precautionary cash motive (Opler, Pinkowitz, Stulz, and Williamson, 1999; Bates, Kahle, and Stulz, 2009).

**Reuse target:** opening sentence of §I Introduction; minor tightening permitted for Abstract.

### Decomposition (APPROVED 2026-04-30 — 5 beats; user pick via AskUserQuestion)

- Beat 1 — Headline (LOCKED above; Option A).
- Beat 2 — Methodological provenance (DWZ 2021 extension framing).
- Beat 3 — Two-trigger amplification (single precautionary channel).
- Beat 4 — Construct validity (external uncertainty drivers).
- Beat 5 — Outsider reaction (market + regulatory channels).
- Beat 6 — Endogeneity defense (PENDING Step 2F).

Each remaining beat (2 through 6) requires individual approval per D28 before its sentence content is written below.

### Beat 2 — Methodological provenance (APPROVED 2026-05-01; "method" version)

> Our measurement is built on the CEO speech-uncertainty method of Dzielinski, Wagner, and Zeckhauser (2021), which we extend from market reactions, analyst behavior, firm performance, and governance outcomes to firm financing-policy outcomes.

**Reuse target:** second sentence of §I Introduction; same wording acceptable in Abstract.

**NLM verbatim verified 2026-05-01** (2 calls, F1D notebook):
- Call 1 (outcome scope) — DWZ tests 9 outcomes (ACAR01, AbnVol, AnResp, CAR01, CAR260, ∆Tobin's Q, ∆ROA, ∆MedRec, ∆Comp) covering market reactions / analyst behavior / firm performance / governance/CEO-compensation. Financing-policy outcomes (cash, leverage, capex, R&D, dividends, repurchases, debt issue, equity issue, working capital, hedging) NOT tested as DV AND not used as controls. Future-work in DWZ §6 anticipates ML/psychology/behavioral directions, NOT firm-policy applications.
- Call 2 (architecture verbatim) — DWZ §1 verbatim: "Our analysis is the first to explicitly decompose an important feature of CEO communication into TWO components: personal style and the potentially strategic component (the residual)". DWZ describes UncPreCEO as a CONTROL variable in Eq. 4, NOT as a third decomposition component. DWZ uses "method", "approach", "procedure" verbatim. DWZ invites extension §1 verbatim: "Our method can be employed to study the existence and relevance of style in other speech characteristics."

**Drift caught 2026-05-01:** prior locked memory (`project_dwz_anchored_framing_locked_2026_04_27.md` line 38) used "three-component" framing — author paraphrase, NOT DWZ verbatim. Beat 2 wording switched from "decomposition" to "method" to align with DWZ's own architecture language. Memory note pending update.

**UncResCEO honest-disclosure obligations** (load-bearing for §III.E + §V.2 Limitations downstream — NOT Beat 2 itself):
- §1 verbatim: "residual use of uncertainty words... explains little of the market reaction".
- §5.2 verbatim: "neither UncPreCEO nor UncResCEO is significantly associated with stock price or volume responses".
- §5.3 verbatim: "no corresponding effect for the interactions with UncPreCEO and UncResCEO".

**Methodological-extension disclosure pending §II.3:** UncPreCEO is repurposed from DWZ's control to our IV. To disclose in Estimation of Main Variables.

### Beat 3 — Two-trigger amplification (APPROVED 2026-05-01; Option A)

> The cash response amplifies under both financing-friction and cash-flow-volatility stress, consistent with a single precautionary channel triggered by two distinct stress conditions (Almeida, Campello, and Weisbach, 2004; Han and Qiu, 2007).

**Reuse target:** third sentence of §I Introduction; can be tightened for Abstract.

**NLM verbatim verified 2026-05-01** (3 calls, F1D notebook):
- ACW 2004 authors verified — **Almeida, Campello, and Weisbach** (NOT Acharya). Title "The Cash Flow Sensitivity of Cash". Theoretical prediction §I.C verbatim: positive cash-flow sensitivity of cash for constrained firms; null for unconstrained. Recession asymmetry §Intro verbatim. Constraint schemes #1-#5 (payout / size / bond ratings / commercial paper / KZ index) — our Unrated proxy = Scheme #3.
- Han-Qiu 2007 — Title "Corporate precautionary cash holdings". §1 verbatim: "This precautionary motive of cash holding creates a positive relationship between cash holdings and cash flow volatility... for a financially constrained firm." CFvol construction §3 verbatim: 16-quarter coefficient of variation = StdDev(OCF) / |Mean(OCF)|.
- Bates-Kahle-Stulz 2009 — §I verbatim ANCHORS our two-trigger framing: "OPSW find that firms with riskier cash flows AND poor access to external capital hold more cash." Bates explicitly bundles BOTH drivers under the SAME precautionary motive. OPSW 1999 cited as foundational anchor (§I + §IV + §VII verbatim).

**Drift caught 2026-05-01:** prior endo-handoff prose (`project_session_2026_04_30_endo_h1_2_locked.md`) used "Acharya, Almeida, Campello (ACW) 2004" — author drift. Correct authors are **Almeida, Campello, and Weisbach (2004 JF)**. Reference filename in memory was correct; only prose abbreviation drifted. Memory note pending update.

**Verbatim caveat:** ACW 2004 does NOT use "precautionary" verbatim — uses synonyms ("safeguard against future investment needs"; "hedging future cash flows"; "hoarding cash under financial constraints"). The "precautionary channel" framing in Beat 3 anchors on Bates 2009 + Han-Qiu 2007 (both verbatim "precautionary"); ACW 2004 anchors the constrained-vs-unconstrained ASYMMETRY/TRIGGER, not the precautionary label itself.

**Beat 1 retroactive verification:** Bates 2009 NLM Call 3 confirms OPSW 1999 + Bates 2009 are valid precautionary anchors for Beat 1 headline.

### Beat 4 — Construct validity (APPROVED 2026-05-01; Option A)

> External uncertainty drivers covary with the speech-uncertainty measure in the predicted directions, supporting its construct validity.

**Reuse target:** fourth sentence of §I Introduction; can be tightened for Abstract.

**NLM verbatim verified 2026-05-01** (5 calls cumulative; Calls 4 + 5 covered driver anchors):
- Hassan, Hollander, van Lent, and Tahoun (2019 QJE; print 2020 Vol. 135) — "Firm-Level Political Risk: Measurement and Effects". §III.A verbatim PRisk formula. §III verbatim: "this measure can be interpreted as a proxy for the political risk and **uncertainty** individual firms face." Validation outcomes (firm-level): stock return volatility, investment cuts, capex cuts, hiring cuts, political donations + lobbying.
- Baker, Bloom, and Davis (2016 QJE Vol. 131 Issue 4) — "Measuring Economic Policy Uncertainty". Abstract verbatim: "We develop a new index of economic policy **uncertainty** (EPU) based on newspaper coverage frequency."
- Davis (2016 NBER WP 22740, single author) — "An Index of Global Economic Policy Uncertainty". §III verbatim: "GDP-weighted average of the 16 national EPU index values."
- Hoberg and Phillips (2016 JPE Vol. 124 No. 5) — "Text-Based Network Industries and Endogenous Product Differentiation". §III verbatim TNIC product-cosine-similarity formula. Verbatim characterization of measure as capturing **competition** and **rivals**: "this result suggests that information in the text-based network classification is informative regarding the presence of firms that managers themselves perceive to actually be **rivals**."

**No in-line citations in Beat 4 §I sentence** — anchors deferred to §II.5 Specification and Measurement of Key Constructs (per D5: drivers live in §II.5 construct-validity slot). All 4 anchors above are NLM-verbatim verified for §II.5 prose population (Step 6).

**Citation drift caught 2026-05-01:** locked memory `project_dwz_anchored_framing_locked_2026_04_27.md` line 58 listed "Hassan et al. 2020" — defensible (print year) but endo handoff used 2019 (online year). Standardize to **2019** for consistency with QJE convention. Memory note pending update.

### Beat 5 — Outsider reaction (APPROVED 2026-05-01; Option A)

> Outsider-reaction tests show that post-call bid-ask spreads widen and SEC conference-call comment letters reference the same speech signal, corroborating the precautionary interpretation through market information-asymmetry and disclosure-insufficiency channels (Lerman, Steffen, and Zhang, 2026).

**Reuse target:** fifth sentence of §I Introduction; can be tightened for Abstract.

**NLM verbatim verified 2026-05-01** (7 calls cumulative; Calls 6 + 7):
- Bushee, Gow, and Taylor (2018) "Linguistic Complexity in Firm Disclosures: Obfuscation or Information?" — *Journal of Accounting Research* 56(1), March 2018. §3.3 verbatim 25-day post-call illiquidity window: "the period starting the day of the call and ending 25 trading days subsequent to the call." §1 Introduction verbatim presentation-vs-Q&A asymmetry: "we separately examine the presentation and the response portions of the call" + "positive relation between managerial Fog in the presentation and information asymmetry. However, we find a negative relation between managerial Fog in the response and information asymmetry." Uses Amihud (2002) illiquidity construct verbatim §3.3.
- Lerman, Steffen, and Zhang (2026) "Earnings Conference Calls and the SEC Comment Letter Process" — *Management Science*, Articles in Advance January 30, 2026. §3.2 verbatim CCCL classification breakdown: 80% insufficient disclosure; 15% inconsistent information; 3% disclosure in conference call itself; 2% both filing and call. §4.4.3 verbatim: "Receiving a CCCL constitutes a shock to a firm's perceptions of how the SEC scrutinizes its voluntary disclosure choices." §5 Conclusion verbatim: "this type of regulatory scrutiny has a material impact on the filing review process, firms' future mandatory disclosures, and the information environment."

**Methodology disclosure pending §IV.A:** BGT 2018 uses Amihud illiquidity; our pipeline uses bid-ask spread (related but distinct microstructure proxy). We adopt BGT's 25-day post-call window + Pres-vs-Q&A asymmetry framework but substitute bid-ask spread for Amihud illiquidity. To disclose in §IV.A.

**Page-number policy from 2026-05-01 onward:** NLM aggregates page numbers across multiple sources in F1D notebook → unreliable. Section refs only in verification notes; no page numbers cited from NLM responses. (Page numbers stripped from earlier Beat 2-4 + §III.E verification notes 2026-05-01 cleanup.)

### Beat 6 — Endogeneity defense (APPROVED 2026-05-01; Option B)

> Reverse causality is addressed via cross-sectional modus tollens on the two precautionary triggers (Almeida, Campello, and Weisbach, 2004; Han and Qiu, 2007), with the limitation that no exogenous-shock identification is pursued.

**Reuse target:** sixth sentence of §I Introduction; Abstract may compress further or omit.

**Anchors verified earlier in session:** ACW 2004 + Han-Qiu 2007 NLM-verified (Beat 3 verification block).

**Substantive content fully governed by D29 + D30 + D31 (decisions log):**
- D31: §III.E body = H1.2 Unrated × UncResCEO (financing-friction trigger; ACW 2004) + H1.3 HighCFvol × UncPreCEO (CF-volatility trigger; Han-Qiu 2007). Six DiD/IV designs dropped during search (Death/DWZ-FD/Lewbel/Weather/AJCA/ACLW).
- D29: AJCA dropped (DFF 2011 verbatim — cash unchanged post-shock; no first stage).
- D30: ACLW 2012 dropped (dual-mechanism contamination — treated firms reduced cash to pay debt while speech rose via refinancing pressure).

**§III.E + §V.2 Limitations expansions (downstream):** the 6-dropped-design list + 8-element future-DiD requirement set + Hassan 2019 QJE flag are §III.E body / §V.2 Limitations content per D31, NOT compressed into §I Beat 6 itself.

**Methodological disclosure pending §III.D:** Han-Qiu 2007 prediction requires double-conditioning (HighCFvol × constrained firm). Our H1.3 conditions only on CFvol (no constraint interaction) — to disclose in §III.D.

---

## Archive plan

When approved (Step 4):
- New folder: `docs/Draft/_archived_v6_2026_04_29/`
- Move into it: all `sections/*.tex` v6, `main.tex` v6 backup, `THESIS_SKELETON.md` v6, `appendix_c_robustness.tex` v6, `abstract.tex` v6, plus `_archived_2026_04_22/` (already there) consolidated as nested
- KEEP at top of `docs/Draft/`: `references.bib`, `variable_definitions.tex` (will be revised), `per_suite/` auto-tables, `summary_stats.tex` auto, generation scripts, this `v7_DECISIONS.md`, `CANONICAL_FACT_SHEET.md`
- New v7 files in `docs/Draft/sections/` after archive

---

## Reference resources locked at Phase 0

| Asset | Path | Purpose |
|---|---|---|
| Per-cell numbers | `tmp/suite_spec_index.json` | every β/p/n for 15 suites; never retype |
| Suite summary | `docs/Draft/CANONICAL_FACT_SHEET.md` | sig-count summary table; programmatic |
| Theoretical anchors | `~/.claude/projects/.../memory/reference_*_verbatim.md` | DWZ + ACW + ACW2007 + BS + FP + OPSW + Bates verbatim |
| Locked framings | `~/.claude/projects/.../memory/project_dwz_anchored_framing_locked_2026_04_27.md` + `project_h1_h2_theoretical_framing_locked_2026_04_28.md` | story-arc constraints |
| Generated tables | `docs/Draft/per_suite/*_table.tex` | auto from generate_all_tables.py |
| Bibliography | `docs/Draft/references.bib` | apacite-keyed |
