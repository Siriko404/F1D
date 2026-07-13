# CODEX HANDOFF — Thesis Defense Slide Prep (written 2026-07-12 by the Claude session that built deck v1)

You are joining mid-task. Read this file fully, then the ledger, then the thesis.
Everything below was verified against primary sources; where something is a note,
it says so. Your job: continue defense preparation with Sina, exactly where the
ratification walkthrough stopped (Section 8).

---

## 1. THE TASK

Sina defends his MSc thesis (Telfer, uOttawa) in a 20-minute talk + Q&A.
Deliverables being built, in order:
1. Ratified story arc + message map (IN PROGRESS, Act 3c pending)
2. Ratified slide deck (v1 EXISTS, frozen until walkthrough)
3. Q&A attack matrix with ratified spoken answers (16 questions banked, 1 ratified)
4. Timed talk script + mock defense

NOTHING goes on a slide or into a spoken script without Sina's explicit sign-off.
He presents; he must own every word.

## 2. FILES (all paths absolute; base = F1D-phase3 git tree)

Base: `C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D-phase3`

### The thesis (the document being defended)
| File | What it is |
|---|---|
| `docs\Thesis\_uottawa_rewrite\thesis_draft_uottawa.pdf` | THE defended document, 71 pp, Jul 3 build |
| `docs\Thesis\_uottawa_rewrite\thesis_draft_uottawa.tex` | Its source. Ch1-2 prose inline; bodies via \input (map at its lines 122-353) |
| `docs\Thesis\_uottawa_rewrite\_thesis_FLAT.tex` | One-file flattened version. CONVENIENT READ, but a Jun-28 SNAPSHOT: STALE in spots (known: run-up table note said "placebo", final says "comparison"). Read it for orientation; VERIFY any quote against the Jul-3 files below before use |
| `docs\Thesis\_uottawa_rewrite\_abstract_body.tex`, `_intro_body.tex`, `sec34_body_from_ledgers.tex`, `_conclusion_body.tex` | The Jul-3 prose bodies (TRUTH for ch1/3/4/5 prose) |
| `docs\Thesis\_uottawa_rewrite\_tables_from_bible.tex` | ALL tables, byte-exact. TRUTH for every number |
| `docs\Thesis\_uottawa_rewrite\_robustness_tables.tex`, `_dwz_replication.tex`, `appendix_I_cash_scrutiny.tex`, `appendix_II_controls.tex` | Robustness/appendix tables |

### Defense prep (your working directory: `docs\Defense\`)
| File | What it is |
|---|---|
| `docs\Defense\_DEFENSE_LEDGER.md` | SINGLE SOURCE OF TRUTH for prep. Sections: A committee intel, B question bank, C narrative design + ratified story acts (verbatim), D Sina rulings, E process learnings, F 15 defensive assets from full-thesis read, G walkthrough progress. READ IT ALL |
| `docs\Defense\_DEFENSE_PREP_STATE.md` | Pipeline + slide ratification grid |
| `docs\Defense\defense_slides.tex` / `.pdf` | Deck v1: 15 core + 10 backups, Beamer metropolis 16:9, pgfplots figures. Every number verified. FROZEN until Phase-2 walkthrough |
| `docs\Thesis\rewrite\_DEFENSE_SLIDES_HANDOFF_2026-07-09.md` | The original handoff (title/committee/honesty floor origin) |

### Supporting ledgers (Claude-authored notes; verify before quoting)
| File | What it is |
|---|---|
| `docs\Thesis\rewrite\claim_findings_ledger.json` | Claim->finding->table-cell registry (C1,C2,C4,C6...) with referee-proofing analysis |
| `docs\Thesis\rewrite\_final\section*_paragraph_ledger.json` | Per-section proposition chains (17 sections) |
| `docs\Thesis\variable_ledger.json` | Variable definitions + generating code lines |

## 3. HONESTY FLOOR (bright lines; a slide or answer that crosses one is INVALID)

- Correlational, within-firm. NO causal identification. NO mechanism established.
- Stock arm = noisy flat null (-0.0429 n.s.). NEVER "stock suppressed"; the gap is CASH RISING.
- Cash-specificity = "concentration, not strict specificity"; cause leg n.s.; mechanism OPEN.
- Uncertainty source (compliance-constrained vs strategic) = observationally equivalent, open.
- Masking incentive (stock acquirers manage narrative) = MOTIVATION, not identification.
- Novelty always "to our knowledge".
- Timing: "indistinguishable from zero once announced". NEVER "falls/reverses/unwound".
  Do not over-read the negative POST (-0.0250*).
- Bid-ask: two per-component facts; the between-component difference was NEVER tested.
- Numbers on slides must match table sign/significance exactly; previews stay qualitative.
- No em-dashes in any new prose (Sina's standing order).

## 4. VERIFIED NUMBER SET (all byte-exact vs _tables_from_bible.tex, 2026-07-09)

| Fact | Value | Table |
|---|---|---|
| Sample | 88,205 calls / 1,884 firms / 2002-2018; cash-ratio panel 2,232 firms | abstract + tab:summary_stats |
| UncResCEO SD (all-universe basis) | 0.3010 (N=44,900) | tab:summary_stats Panel B |
| H1 run-up, cash | 0.0461*** (SE 0.0172; two-tailed p=.0074) ~15.3% of SD | tab:empire_building_did col 2 |
| H1 stock arm | -0.0429 n.s. (SE 0.0307) | col 6 |
| Event time (matched, N=28,102/1,320) | PRE2 0.0068 n.s.; PRE1 0.0473*** (0.0178); GAP 0.0018 n.s. (0.0187); POST -0.0250* (0.0130) | tab:empire_drop_matched col 1 |
| Drops | PRE1-GAP 0.0455**; PRE1-POST 0.0723*** | same |
| CashRatio clock | PRE1 0.0061**; POST -0.0155***; GAP-POST 0.0210***; GAP level 0.0055 n.s. (persistence = absence of decline) | col 2 |
| Cash-specificity (MA3) | cash 0.0459**; stock -0.0524 n.s.; diff 0.0983** (SE 0.0476, p=.039) | tab:empire_cashspec col 1 |
| Cause leg | 0.0064 n.s. matched; 0.0092* full panel | cols 2-3 |
| Scrutiny gating | PreAnnounceQtr 0.0413***/0.0439**; interaction -0.0056 n.s. (SE 0.0111) | tab:reason_gating |
| Scrutiny validity | CashRatio 0.7530***/0.8519*** (ONE-TAILED, cash coef); HighCash 0.1754***/0.1921*** — do NOT conflate | tab:cash_scrutiny_validity |
| HighCashScrutiny | mean 0.1127 (~11% of calls); HighCash = top tercile winsorized CashRatio, mean 0.3333 | summary stats |
| All-deals cashspec (STRONGER) | diff 0.1056, p~.013 | tab:rob_cashspec |

Two-way clustering rerun for the cashspec diff (p=.043) exists ONLY as a private rerun
note in claim_findings_ledger.json — it is NOT in the thesis. Do not claim it on slides;
if asked about clustering, disclose that distinction.

## 5. COMMITTEE (reverse-engineering results; details in ledger section A)

- Supervisors (allies): Dr. Ali Akyol, Dr. Harshit Rajaiya.
- Examiner Dr. Shantanu Dutta: M&A + textual/NLP + private-meetings/insider-trading
  disclosure. The closest domain expert. Likely attacks: payment-method endogeneity,
  private-communication channels, media, why-word-list-not-ML. Sina intel: likes QUICK
  defenses -> tight 20 min, results fast.
- Examiner Dr. Rengong (Alex) Zhang: accounting, big-data/ML, disclosure, uncertainty+prices.
  Likely attacks: data pipeline (speaker attribution), lexicon vs ML, "why no price reaction".

## 6. STRATEGY (Sina's design goal, his words)

The defense is a STORY. Reverse-engineer it: each slide PLANTS a question the next
beat answers gloriously; plant -> ask -> answer, repeatedly. Feared questions get
pre-emptive concessions (slide 14 concedes causality BEFORE Q&A) or backup slides.
The full per-slide plant->answer map is ledger section C.

## 7. WORKING RULES WITH SINA (non-negotiable; violating these is the top failure mode)

1. DO EXACTLY AS SAID. Literal instruction beats your judgment. Never substitute a
   "better" approach.
2. ULTRA-TERSE chat. He is mentally exhausted. Lead with the point. Short sentences.
   Many small titled sections. Lists over prose. One idea per chunk, then STOP and
   check ("Got it? y/n") before the next.
3. NO ANALOGIES when explaining. Explain the ACTUAL case in simple language. (Radio/
   scale analogies failed; actual-case walkthroughs landed.)
4. Ratify EVERYTHING: one decision per stop. Never batch decisions. Never edit slides
   without his explicit sign-off. He caught and stopped two "proceeding too fast" drifts.
5. Record verbatim to `_DEFENSE_LEDGER.md` AS YOU GO; commit after every chunk
   (atomic, verbose audit-trail message). Durability is mandatory: any finding not in
   the ledger is considered lost.
6. Do the work YOURSELF. He banned delegation to subagents for this task.
7. Verify every number/quote against the PRIMARY file (tables tex / Jul-3 bodies /
   generating code) before it goes anywhere. Ledgers and this handoff are notes.
8. NEVER touch the thesis build or anything in `_uottawa_rewrite` (regenerated files;
   the thesis is DONE and submitted-track). Slides live ONLY in `docs\Defense\`.
9. Never kill msedge. If a PDF viewer locks defense_slides.pdf, builds silently go stale.
10. Frustration signals ("no!", "you're not getting it"): STOP, diagnose with ONE
    focused question, fix cause, then resume.

## 8. STATE: EXACTLY WHERE WE STOPPED

Story-arc ratification walkthrough, act by act (verbatim records in ledger C2):
- Act 1 (bind, S2-S3): RATIFIED
- Act 2a (measure, S4): RATIFIED
- Act 2b (data + unprompted selection concession, S5): RATIFIED
- Act 2c (design, S6): RATIFIED
- Act 3a (first result, S7): RATIFIED
- Act 3b (reveal figure, S8): RATIFIED
- **Act 3c (two clocks, S9): PRESENTED, AWAITING his y/n** <- RESUME HERE
- Act 4 (discipline: S10 formal test, S11 rule-outs, S12 robustness, S13 contributions,
  S14 limitations-as-shield): not yet presented
- Close (S15): not yet presented

Then remaining, in ratified pipeline order:
1. Finish Act 3c + Act 4 + Close ratification.
2. Traps T1-T5 rulings (ledger section C): RQ wording alignment; add law/Reg-FD backup?;
   add unobserved-channels backup (private meetings + media)?; DWZ-novelty line on B4;
   timing budget note T6.
3. Phase 2: slide-by-slide walkthrough (tiered: S2,S3,S7,S8,S9,S10,S14 deep one-at-a-time;
   rest batched). Only THEN edit defense_slides.tex per his rulings.
4. Phase 3: Q&A war-game. Bank has Q1-Q16; Q1 RATIFIED (spoken script in ledger);
   Q13 + Q16 flagged NEEDS-VERIFY (speaker-attribution detail; why sample ends 2018 —
   thesis states no rationale; ASK SINA).
5. Phase 4: timed script (20 min; S8+S9 get ~4 min; S4-S6 ~60s each) + mock defense.

## 9. BUILD INSTRUCTIONS (deck)

- `cd docs\Defense && pdflatex -interaction=nonstopmode defense_slides.tex` (run twice).
- MiKTeX present; theme metropolis installed; palette #2166AC (cash/uncertainty) /
  #E08214 (stock/cash-ratio), CVD-validated.
- Visual check: render pages to PNG via
  `"C:\Program Files\MiKTeX\miktex\bin\x64\mgs.exe" -dNOPAUSE -dBATCH -sDEVICE=png16m -r110 -dFirstPage=N -dLastPage=N -sOutputFile=out.png defense_slides.pdf`
  and INSPECT for overflow after any edit (4 slides needed overflow fixes in v1).
- Clean aux files after; do not commit build logs.

## 10. KNOWN PITFALLS (learned the hard way; do not repeat)

- claim_findings_ledger.json conflated 0.7530/0.8519 as HighCash coefficients; they
  belong to CashRatio. Always open the table before quoting any ledger number.
- The scrutiny-validity cash coefficients are ONE-TAILED (table note); disclose when quoted.
- _thesis_FLAT.tex is stale (Jun 28). Truth = Jul-3 build files (Section 2 table).
- Sina's ratified defense lines (Q1 script, act carrier lines) are VERBATIM assets in
  the ledger. Reuse them exactly; do not paraphrase them back to him differently.
