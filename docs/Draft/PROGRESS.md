# Thesis Draft — Progress Tracker

**Purpose:** persistent memory for Claude across context compactions. Claude updates this file as work progresses. Read at start of every draft session.

**Current phase:** **Phase 5 audit — philosophy-framed, dialogue-based. 10 / 37 suites audited + RE-CATALOGUED under rule 24. Q1 CLUSTER COMPLETE: H1 + H4a + H4b + H12 + H12b + H13 + H17 + H19b KEEP; H16 DROP-flagged (revisit), H20b DROP. Narrative discipline locked mid-audit. Rules 21-24 added 2026-04-15. Rule 24 shifted §4.2 cataloguing format to full-row; Q1 retroactive REVERSED same day; all 10 §4.2 blocks now full-row format. Next cluster: Q2 (channel/mechanism, 6 suites). Next suite = H1.1.**

**Last updated:** 2026-04-15 (post-Q1 re-catalogue under rule 24)

---

## First read for any new session (MANDATORY)

Before touching any suite, read in order:

1. `docs/Draft/DECISIONS.md` — full. §1 philosophy, §2 how, §3 audit order by Q-cluster, §4 per-suite record shape + empty blocks, §5 cross-cutting observations.
2. `docs/Draft/PROGRESS.md` — this file, full.
3. `memory/project_phase5_audit_progress.md` — live audit tracker (suites audited so far, current position).
4. `memory/feedback_phase5_philosophy.md` — the core rule (reader-question + dialogue + no rubrics).
5. `memory/feedback_phase5_methodology.md` — discipline rules still in force (read-linear, no Grep, concise, etc.).
6. `memory/feedback_ceo_noisy_mgr_central.md` — UncAnsMgr is sole hypothesis channel; CEO/Pre are secondary.
7. `memory/feedback_audit_first_no_narrative.md` — no rescue narratives during audit.

These reads are non-negotiable. Skipping them produced the 2026-04-14 grounding-gap incident.

---

## Protocol (locked)

1. **Every kept suite maps to a named reader-question** a skeptical committee member will genuinely ask. Six baseline questions in `DECISIONS.md §1.3`; new questions can be named during dialogue if justified.
2. **No rubrics.** No numeric thresholds like "N/M significant cells". Verdicts rest on the argument that cells honestly answer the reader-question, not on counting stars.
3. **Per-suite dialogue, not report-and-approve.** 5 steps per suite: (i) I read cells plain, (ii) I name the reader-question, (iii) I argue both sides honestly, (iv) user pushes back adversarially, (v) we converge on KEEP / DROP / REFRAME.
4. **UncAnsMgr is the sole hypothesis channel.** CEO / UncPreMgr / UncPreCEO are secondary. Aligned-weak → 1-line cite. Contradicting → "measurement concerns" flag. No rescue narratives.
5. **Read-tool-linear only.** No Grep / pattern search / shortcut on `outputs/all_tables.tex` or runner source. Read every line.
6. **No mid-audit narrative building.** Cell facts only during reading. Interpretation happens in dialogue step (iii) and is LOCAL to the suite, not cross-family theory-building.
7. **Advisor calls at phase boundaries only**, never mid-family. Mid-review advisor calls caused the 2026-04-13 rebuild loop.
8. **Concise by default.** Lead with the answer. Tables over prose paragraphs.
9. **Pre-audit canonical reads mandatory** — see "First read for any new session" above.

---

## Audit order (locked)

Walk Q-clusters in order: Q1 → Q2 → Q3 → Q4. Within each cluster, suites audited in listed order. Cluster assignment is provisional — if cells in a suite clearly answer a different Q, re-cluster with explicit argument.

- **Q1 (direct outcomes, 10 suites)**: H1 → H4a → H4b → H12 → H12b → H13 → H16 → H17 → H19b → H20b
- **Q2 (channel / mechanism, 6 suites)**: H1.1 → H1.1b → H1.2 → H13.1 → H13.2 → H22
- **Q3 (information content, 14 suites)**: H5 → H7 → H7b → H7c → H7d → H7e → H14 → H14b → H14c → H14d → H14e → H18 → H18b → H21
- **Q4 (construct validation / reverse direction, 7 suites)**: H11 → H11-Lag1 → H11-Lag2 → H23 → H24 → H24b → H25
- **Q5 + Q6 (cross-cutting)**: handled at end of audit, not per-suite.

**First suite**: H1 (cash holdings).

---

## Per-suite record shape (locked)

Each audited suite produces (a) one row in the summary table at `DECISIONS.md §4.1` (7 columns: `suite_id`, `DV`, `N_range`, `reader_Q`, `key_cell_fact`, `verdict`, `rationale`) and (b) one block in `DECISIONS.md §4.2+` with fuller per-suite detail (template in §4.2). Dialogue transcript (arguments + pushback) lives in chat + git log, NOT in the record.

---

## Workflow phases (historical — code-fix phases complete)

- [x] Phase 1 — Diagnose + protocol (2026-04-13)
- [x] Phase 2.5 — Clustering methodology (uniform firm-only + macro exception)
- [x] Phase 3 — Pipeline bug fixes applied
- [x] Phase 4 — Full 35-suite rerun + table regeneration
- [x] Architectural rewrite (Phases 0-8) — zero-hardcoded-state pipeline complete, 8 LaTeX-audit bugs fixed. Commits c46e655 → bf9f366.
- [ ] **Phase 5 audit/synthesis — IN PROGRESS.** Philosophy + design finalized 2026-04-14. **10 / 37 suites audited — Q1 cluster COMPLETE.** H1 + H4a + H4b + H12 + H12b + H13 + H17 + H19b KEEP; **H16 DROP-flagged** (revisit if strong reason emerges); **H20b DROP** ("findings not clean, headache"). Q1 was reworded at H1 boundary, then narrative discipline locked mid-audit: no more Q rewording; final Q wording and narrative frame decided post-audit after all 37 suites are read. **Rules 21-24 added 2026-04-15** (rule 21: provisional Q is placeholder, not filter; rule 22: null coefficient signs are noise, not signal; rule 23: significance pattern is the audit signal, not effect magnitudes; **rule 24: read/verdict/record are three different scopes — record is broader than verdict; every variable in the table catalogued in §4.2, not just the IVs; Q1 records frozen with controls-cataloguing gap per user decision; Q2 onward uses full-row format**). See `docs/Draft/DECISIONS.md §1.3` (Q1 revision history), §4.2 (H1/H4a/H4b/H12/H12b/H13/H16/H17/H19b/H20b blocks), §5.1-5.12 (cross-cutting flags: §5.5 UncPreMgr cross-sectional spans 3 DVs, §5.6 PayoutRatio_q low persistence, §5.7 H13 cross-IV FE-strata split, §5.8 first complete-null H16, §5.9 H17 breaks §5.5 UncPreMgr generalization, §5.10 H19b+H20b negative-persistence DV class, **§5.12 Q1-frozen-with-gap methodology shift**). Tracker: `memory/project_phase5_audit_progress.md`. **Next cluster: Q2 (channel/mechanism, 6 suites). Next suite: H1.1.**

---

## Session state — 2026-04-14 (audit design finalized, /clear handoff)

**What happened this session:**

1. **Hard reset of prior audit state.** Wiped `DECISIONS.md §3/§4/§5`, `PROGRESS.md` Phase 2 + Session-state blocks, `memory/project_phase5_audit_progress.md`. All prior reading/audit work from earlier sessions removed — the reset was user-ordered because "nothing is done" and the prior work had misaligned goals.
2. **Attempted H1 re-audit under old approach.** Read `outputs/all_tables.tex` lines 11-270 (H1 family block), read `run_h1_cash_holdings.py` + 3 moderation runners + `build_h1_cash_holdings_panel.py` + `_compustat_engine.py`. Wrote cell facts + 15-row metadata verification + KEEP/DROP proposals for H1 family into `DECISIONS.md §4`. All of that was wiped in the subsequent philosophy reset.
3. **Process-design discussion via 3-round AskUserQuestion protocol.** Started Round 1 (pain / end-state / record content). User flagged "goal not optimally designed for our needs". Pivoted. Round 2 covered interaction shape / granularity / writes. User then asked "what are the principles for deciding?". I drafted 8 generic principles. User rejected as "almost all dumb and useless and generic".
4. **Philosophy discussion (load-bearing).** Landed on: novel IV + skeptic's "so what?" default is the central risk. 6 reader-questions (Q1-Q6) the thesis must defend against. Audit verdict per suite: KEEP / DROP / REFRAME, with the ONLY non-generic principle being "every kept suite must have a named reader-question + an honest argument that cells answer it." No rubrics. Per-suite dialogue (5 steps) against the skeptic.
5. **Advisor review.** Advisor flagged (a) my 18-column table was a rubric in disguise, (b) cluster audit order needs provisional Q-map done up front, (c) stop designing, start doing, (d) format choice (single wide table vs per-suite blocks + summary) matters.
6. **Design finalized**: 7-column summary table + per-suite blocks in `DECISIONS.md §4`, provisional Q-cluster map locked (Q1 10, Q2 6, Q3 14, Q4 7 = 37 suites), cluster-walk audit order, first suite = H1.
7. **Hard reset of `docs/Draft/` files** (this write) to capture the finalized design cleanly for `/clear` handoff.

**Next session entry point (after /clear):**

1. Read the 7 canonical docs listed under "First read for any new session" above, in order.
2. **Clarify one open question with the user BEFORE starting**: the Read-tool-linear / no-Grep rule (rule 5) was originally the user's verbatim directive about `outputs/all_tables.tex` specifically. It extends cleanly to audit targets that need cell-by-cell reading. But runner source files read for metadata-header verification (HYP_DIR / CLUSTERING / TAIL / MODEL_SPECS blocks — typically lines 80-160 of each runner) arguably fall outside the intent of that rule. Applying no-Grep to ~37 runners = ~7000 lines of Read-tool calls for metadata that's in structured constant blocks. Ask the user: "Does the no-Grep rule cover runner source metadata verification, or only `all_tables.tex` cell reading?" Default to stricter interpretation (no Grep anywhere in audit) unless user clarifies otherwise.
3. Confirm: "Design locked. First suite H1 (Q1 cluster). Ready to start the 5-step dialogue?"
4. On confirmation, begin H1 dialogue step (i): Read-tool-linear on `outputs/all_tables.tex` from line 11 (H1 block). Report cells plain. Name Q1. Argue both sides. Wait for user pushback.
5. Populate the 7-column summary row + per-suite block in `DECISIONS.md §4` only at dialogue step (v).

**Deleted 2026-04-14 (do NOT look for these):**
- `outputs/findings.txt` + `scripts/findings_template.txt` + `scripts/generate_findings.py` — chronic staleness source.
- CFO/MgrV2 plan files (`~/.claude/plans/compressed-scribbling-diffie.md`, `memory/project_cfo_mgrv2_plan_v2.md`, `memory/project_manager_classifier_audit_and_plan.md`) — abandoned direction.
- Pre-reset `draft.tex` + `draft.pdf` — polluted scaffold.

**Uncommitted working tree going into /clear:**
- Modified: `docs/Draft/DECISIONS.md`, `docs/Draft/PROGRESS.md`, `memory/MEMORY.md`, `memory/project_phase5_audit_progress.md`, `memory/feedback_phase5_methodology.md` (possibly), `memory/feedback_phase5_philosophy.md` (new file).
- Consider `git add -A && git commit` before `/clear` for a clean restore point.

**Sources of truth during audit:**
- `outputs/all_tables.tex` — cell facts, plain LaTeX, matches PDF verbatim.
- `outputs/econometric/*/latest/suite_spec_*.json` — authoritative values / N / R² / tail / metadata.
- `src/f1d/econometric/run_h*.py` — runner source.
- `src/f1d/variables/build_h*_panel.py` — panel construction.
- `src/f1d/shared/variables/_compustat_engine.py` + siblings — variable formulas.
