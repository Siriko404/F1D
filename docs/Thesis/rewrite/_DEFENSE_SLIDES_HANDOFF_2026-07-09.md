# HANDOFF — Thesis Defense Slides (written 2026-07-09, read after /clear)

**NEW TASK: prepare slides for the thesis defense.** Nothing has been started on slides.
This file is your initial knowledge context. Everything below was verified in the
writing session against primary sources; where a claim needs re-checking, the source
path is given. Treat THIS file as notes — verify numbers against the ledgers/tables
before putting them on a slide.

---

## 1. The thesis (finished, committed)

- **Title:** "Cash Got Your Tongue? CEO Language-Uncertainty Around Undisclosed Cash Acquisitions"
- **Candidate:** Sina Soleimanipour, MSc in Management (Thesis based), Finance, Telfer School of Management, uOttawa. Student #300446572.
- **Supervisors (co-advisors):** Dr. Ali Akyol, Dr. Harshit Rajaiya (both Telfer).
- **Examiners (committee, from the uOttawa List-of-Examiners form, Master's):**
  - Dr. Shantanu Dutta, Telfer School of Management
  - Dr. Rengong (Alex) Zhang, Telfer School of Management
- **Expected submission date on the form:** 2026-07-03.
- **FINAL PDF (the document to defend):**
  `F1D-phase3\docs\Thesis\_uottawa_rewrite\thesis_draft_uottawa.pdf` — 71 pages, compiles clean (undefined refs/cites = 0, overfull hbox = 0).
- **Repo:** the `F1D-phase3` git tree (NOT the F1D data tree; primary working dir of the session may open in F1D — the thesis lives in F1D-phase3). Branch `phase4/masking-rewrite-harness`, HEAD at handoff time = `4d8cb986` ("thesis(frontmatter): fill Examining Committee with the two examiners"). Baseline tag `baseline-before-examiners` = `88e637e2`.

## 2. What the thesis says (the defense content, all verified this session)

**Research question:** does residual CEO Q&A uncertainty (UncResCEO) track a deal's
passage from private to public — elevated while a cash acquisition is withheld,
receding once announced?

**Setting/sample:** U.S. public, non-financial, non-utility firms' earnings calls,
2002–2018 (Capital IQ transcripts + SDC deals; 88,205 calls / 1,884 firms).

**Measure:** UncResCEO = call-varying residual of CEO Q&A uncertainty after netting
out each executive's persistent speaking style (DWZ decomposition, Dzielinski et al. 2021).
Constructed in Ch.2 (§2.3, equations eq:uncans + eq:dwz); estimating equations in §2.4
(eq:ma1, ma2, ma3).

**Hypotheses → analyses mapping (from §2.4; each Main-Analysis section opens by
naming its hypothesis — added this session, commit 88e637e2):**

| Hypothesis | Section | Finding | Key cells (claim_findings_ledger.json) |
|---|---|---|---|
| H1 run-up | §3.2 (MA1) | Supported: cash pre-announcement quarter elevation, modest, correlational | C2: cash 0.0461*** (two-tailed p=.0074, tab:empire_building_did col 2); stock −0.0429 n.s. (col 6) |
| H1b timing | §3.3 (MA2) | Supported — THE STRONGEST RESULT: elevation is anticipatory, indistinguishable from zero at announcement (GAP), while the funding cash persists to completion ("two clocks") | C1: PRE1 0.0473***, GAP 0.0018 n.s.; PRE1−GAP 0.0455** (tab:empire_drop_matched col 1); CashRatio GAP−POST 0.0210*** (col 2) |
| H1a cash-specificity | §3.4 (MA3) | Supported but fragile: formal pooled Wald cash−stock difference clears 5%, read as concentration NOT strict specificity | C6: diff 0.0983** p=.039 (tab:empire_cashspec col 1); cause leg 0.0064 n.s. (col 2) |

**Additional analyses (Ch.4):**
- §4.1 scrutiny rule-out (C4): run-up survives analyst CashScrutiny + interaction
  (0.0413***, interaction −0.0056 n.s., tab:reason_gating); hedge: "does not account
  for THIS run-up," never "scrutiny never matters."
- §4.2 bid-ask channel: residual unrelated to post-call spread (n.s. all 12 specs,
  tab:h14c_ceo2_decomp); scripted presentation positively associated. Two per-component
  facts — the between-component difference was NEVER tested directly.
- §4.3/§4.4 robustness: withdrawal-as-resolution, dropping the cash equation's dynamic
  term, all-deals (no first-deal restriction), logit; plus 4 robustness tables + 2 logit
  tables in `_robustness_tables.tex`.

**Contributions (intro enumerates FOUR, each descriptive):** (1) reads residual Q&A
uncertainty in the anticipatory window (prior work: tone/vocabulary/prices);
(2) documents cash-vs-stock concentration surviving a formal pooled test; (3) reads the
unscripted Q&A as tracking private→public, bridging withholding theory and
transaction-anticipation evidence; (4) the bid-ask channel split.

**Key variable defs (verified against actual code this session):**
- `HighCash` = 1[CashRatio ≥ p67] — top TERCILE of winsorized (1/99) CashRatio;
  code: `scripts/gen_cash_scrutiny_validity_table.py:79-82`; used as regressor ONLY in
  tab:cash_scrutiny_validity (cols 3–4: 0.1754***/0.1921***) + summary stats (mean 0.3333).
- `HighCashScrutiny` = 1[CashScrutiny > median]; median is 0, so it flags ANY cash
  scrutiny (~11% of calls; mean 0.1127). DO NOT conflate the two.
- `CashRatio` = cheq/atq.

## 3. HONESTY FLOOR — locked register (bright lines; slides MUST respect these)

Slides are prose too. A slide that hardens or drops a hedge is INVALID:
- Correlational, within-firm; NO causal identification; NO mechanism established.
- Stock arm = noisy flat null (−0.0429 n.s.) — NEVER "stock suppressed"; the gap is CASH RISING.
- Cash-specificity = "concentration, not strict specificity"; the cash-accumulation
  CAUSE stays open (cause leg n.s.).
- Source of uncertainty (compliance-constrained vs strategic reticence) = observationally equivalent, open.
- Masking incentive (stock acquirers manage narrative) = MOTIVATION, not identification.
- Novelty always "to our knowledge" (positioning claim).
- §3.3 timing: "indistinguishable from zero once announced" — NEVER "falls/reverses/unwound"; do not over-read the negative POST.
- Bid-ask: never claim a tested between-component difference.
- QUALITATIVE in preview contexts; when numbers appear they must match table sign/significance exactly.

## 4. Ground-truth sources (verify slide content against THESE, not memory)

All under `F1D-phase3\docs\Thesis\`:
- `_uottawa_rewrite\thesis_draft_uottawa.pdf` + `.tex` — the final document (clone; REGENERATED every build — never hand-edit).
- `rewrite\_final\section*_paragraph_ledger.json` — canonical proposition chains per section (claims + grounding + register_locks + table cells). 17 sections: abstract, 1, 2.1–2.5, 3.1–3.4, 4.1–4.5, 5.
- `rewrite\claim_findings_ledger.json` — the claim→finding→table-cell registry (C1, C2, C4, C6...).
- `variable_ledger.json` — every variable's definition + generating code line.
- `_uottawa_rewrite\_tables_from_bible.tex` — all regression/summary tables (byte-exact from docs/Draft bible).
- `docs\Draft\thesis_tables.pdf` / `.tex` (in the F1D data tree for some outputs; the bible for tables).
- Build pipeline: `rewrite\_phase5_harness\build_uottawa_rewrite.py` (single source of truth;
  clones docs/Thesis/*.tex → _uottawa_rewrite, regenerates prose from phaseB_result.json,
  compiles 3× pdflatex). Audit gates: `_audit\floor_inventory.py --counts` (locked hedge grid
  12/15/11/13/9/18/6/2/1), `_audit\number_audit.py` (A=0/B=0), `_audit\destars_verify.py`,
  `_audit\orphan.py`.
- Examiner form: `C:\Users\sinas\Downloads\02-PhD-_-MSc-List-of-examiners-_Thesis_.pdf`.

## 5. Slide-prep guidance (task not yet scoped — ASK SINA FIRST)

Not yet known (ask, one AskUserQuestion, before building):
- Defense length / slide count target; department norms for MSc Telfer defense.
- Format: Beamer vs PowerPoint vs Quarto (repo has skills for all: `econ-beamer`,
  `research-beamer-deck`, `pptx`, `research-quarto-deck`, `slide-excellence`, `dataviz`).
  No existing slide deck found — greenfield.
- Whether he wants figures generated from data (none exist in the thesis — it is tables-only)
  or table screenshots/re-typeset table fragments.
- Talk narrative preference (paper order vs findings-first).

Natural deck skeleton (from the thesis structure; a starting proposal, not a decision):
title/committee → motivation (disclosure bind: may stay silent, may not mislead) →
question + measure (UncResCEO residual) → data (2002–2018, 88,205 calls) → H1 run-up →
H1b two-clocks round trip (STAR SLIDE — strongest result) → H1a cash concentration →
rule-outs (scrutiny; bid-ask) → robustness → contributions (4) → limitations
(honesty floor: correlational, mechanism open) → Q&A backup slides (tables, DWZ details,
HighCash/HighCashScrutiny defs, withdrawal robustness).

Anticipated examiner attack surfaces (for backup slides): causality/identification
(answer: floor concedes it — descriptive by design); generated-regressand SEs
(handled in 2.3/2.4, E1 rule); why cash not stock (masking motivation, kept as
motivation); power of the stock arm (noisy null, underpowered caveat); Gelman-Stern
(that's WHY the formal pooled test exists — never compare side-by-side significance).

## 6. Working rules with Sina (persistent, non-negotiable)

- ULTRA-TERSE replies; ≤6–10 lines; he is mentally exhausted; caveman mode active.
- DO EXACTLY AS SAID — literal instruction > your judgment. Never substitute a "better" approach.
- Don't ask open questions in prose; use AskUserQuestion for preference choices; don't ask at all when the answer is derivable from files.
- Verify EVERYTHING against primary sources (ledgers → actual code → actual tables) before claiming; memory/ledgers are Claude-authored notes, not truth.
- Atomic commits per logical change, verbose audit-trail messages, with trailers:
  `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>` + `Claude-Session: <url>`.
- Never edit the `_uottawa_rewrite` clone by hand (regenerated); thesis prose changes go through generator transforms — but SLIDES ARE A NEW ARTIFACT, put them in a NEW directory (suggest `docs/Defense/`), do not touch the thesis build.
- Never kill msedge (his browser) — only dedicated PDF readers (Acrobat/Sumatra/Foxit) before builds.
- PDF-open trap: if a viewer locks thesis_draft_uottawa.pdf, pdflatex silently writes stale output; verify `pdf -nt tex` after any build.
- Em-dash task on the thesis is PARKED by explicit order ("its not safe") — do not resume; also avoid em-dashes in new slide prose (he wants zero).
- Paragraph/content edits must be content-aware; semantic flow > cosmetic balance.

## 7. State at handoff (nothing in flight)

- Thesis: DONE and committed (4d8cb986). All gates green. Examiners inserted, verified nothing else changed (no-op-rebuild determinism proof + line-level diff).
- A verbatim intro read-through/verify with Sina was in progress (¶1–¶3 of 9 verified TRUE) — SUPERSEDED by this new slides task unless he asks to resume.
- No slide files exist yet. First action: confirm scope (Section 5 questions) via ONE AskUserQuestion, then propose the skeleton.
