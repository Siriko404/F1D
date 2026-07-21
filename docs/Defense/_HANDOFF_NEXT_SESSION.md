# HANDOFF — Thesis Defense, next session (written 2026-07-16)

## 1. Task

Sina defends his MSc thesis (Telfer, uOttawa). The 13-slide main deck is FINISHED,
approved, and production-locked. The next deliverable is the **indexed Q&A appendix**
(architecture approved, ~39 slides, content not yet designed).

## 2. Canonical work: the REV21 package

`C:\Users\sinas\Downloads\THESIS_DEFENSE_PROJECT_LOCKED_REV21.zip` (79 files)

This package, built in a separate workstream, is the AUTHORITY for the presentation.
Read its ledger FIRST and follow its `assistant_operating_contract` exactly.

| Inside the zip | What it is |
|---|---|
| `THESIS_DEFENSE_CONTINUITY_LEDGER_REV21.json` | THE control document: operating contract, 38 approved decisions, architecture, visual system, slide artifacts, QA risk register, 18 open decisions, current state, do-not-repeat lessons |
| `production/thesis_defense_main_deck_slides_01-13_standardized_v2.pdf` / `.html` | The LOCKED main deck (13 pages, 1152x648) |
| `production/individual_pages/` | Per-slide PDF + 300dpi PNG |
| `provenance/` | Pre-standardization inputs, older ledger REV20, assets. Provenance ONLY, never production |
| `source/_thesis_FLAT(2).tex` | The thesis source shipped with the package |
| `scripts/`, `manifest/SHA256SUMS.txt` | Assembly script, migration script, integrity sums |

**Its stated next action:** resume the approved indexed Q&A appendix architecture
(A navigation index, B theory/literature, C data/sample, D measurement/validity,
E econometric designs, F full main results, G additional analyses/robustness,
H threats/limitations, plus one more category). Authoring format: HTML/CSS, rendered
to PDF, inspected before locking.

**Its hard rules:** do not alter any standardized-v2 main-deck slide unless Sina
explicitly reopens it; provenance artifacts are not the deck; academic content comes
only from the authoritative thesis; target 18 minutes with a 2-minute buffer.

## 3. Thesis sources (verification truth)

Base: `C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D-phase3\docs\Thesis\_uottawa_rewrite\`

| File | Use |
|---|---|
| `thesis_draft_uottawa.pdf` / `.tex` | The defended document (71 pp, Jul 3 build) |
| `_abstract_body.tex`, `_intro_body.tex`, `sec34_body_from_ledgers.tex`, `_conclusion_body.tex` | Jul-3 prose bodies: TRUTH for quotes |
| `_tables_from_bible.tex` | All tables byte-exact: TRUTH for every number |
| `_robustness_tables.tex`, `_dwz_replication.tex`, `appendix_I_cash_scrutiny.tex`, `appendix_II_controls.tex` | Robustness + appendix tables (appendix source material) |
| `_thesis_FLAT.tex` | Convenient one-file read, but a Jun-28 snapshot, STALE in places. Verify quotes against the Jul-3 files above |

Never edit anything in `_uottawa_rewrite` (regenerated build files).

## 4. What this repo session adds (not in the REV21 ledger)

`docs\Defense\_DEFENSE_LEDGER.md` — carry these forward:

**A. Committee intel.** REV21 lists committee composition as an OPEN decision. It is known:
- Supervisors: Dr. Ali Akyol, Dr. Harshit Rajaiya.
- Examiner Dr. Shantanu Dutta: M&A, method-of-payment, media, textual/NLP, private
  in-house meetings and insider trading. Closest domain expert on this thesis.
  Sina intel: he likes QUICK defenses.
- Examiner Dr. Rengong (Alex) Zhang: accounting, big data/ML, disclosure,
  uncertainty and prices (PEAD). Expect data-pipeline and "why no price reaction" angles.

**B. Question bank, 16 rows** (ledger section B), examiner-reverse-engineered: identification,
generated regressand, Gelman-Stern, stock-arm power, payment-method endogeneity (Dutta's own
paper), private-communication channels, media leakage, lexicon vs modern NLP, speaker
attribution, window-searching, economic magnitude, deal-quality follow-ups.
Q1 has a RATIFIED spoken answer, verbatim in the ledger. Two rows need Sina input:
speaker-attribution detail, and why the sample stops in 2018 (the thesis gives no rationale).

**C. Fifteen defensive assets found in the full thesis** (ledger section F): the Pagan-1984
flag with the bootstrap named, the scripted-versus-unscripted firewall argument, the
conservative-floor argument, the DWZ replication numbers, the all-deals robustness that
STRENGTHENS cash concentration (0.1056, p about .013), withdrawal and static-FE checks,
the GAP-cash caution, and the exact hedged phrases the thesis uses. This maps directly onto
appendix categories D, G, and H.

## 5. Superseded, do not use

`docs\Defense\defense_slides.tex` / `.pdf` (a 15-slide Beamer draft built here on 07-09) and
`_CODEX_HANDOFF_2026-07-12.md` are SUPERSEDED by the REV21 deck. Their story-arc records in
the ledger reference the dead 15-slide numbering. Keep for history only.

## 6. Working rules with Sina (non-negotiable)

1. Do exactly as said. Literal instruction beats your judgment.
2. Ultra-terse chat. Short sentences, small titled sections, lists over prose.
3. One decision at a time. Never batch. Never produce a finished artifact before its
   content is approved. He has stopped this session twice for moving too fast.
4. When explaining: no analogies. Explain the actual case in plain words, one idea per
   chunk, then stop and check.
5. Do the work yourself; he banned subagent delegation for this task.
6. Verify every number and quote against the primary file before it is used.
7. No em-dashes in any audience-facing wording.
8. Record decisions as they happen and commit; anything unrecorded is lost.

## 7. First actions in the new session

1. Extract the zip to a working directory and read `THESIS_DEFENSE_CONTINUITY_LEDGER_REV21.json`
   in full, especially `assistant_operating_contract`, `current_state`, `appendix_architecture`,
   `visual_system`, `production_and_qa_workflow`, and `do_not_repeat_lessons`.
2. Open the locked 13-slide PDF so appendix design matches its visual system.
3. Report state back to Sina in a few lines and ask which appendix category to design first
   (the ledger's own protocol: one slide at a time, approval before locking).
