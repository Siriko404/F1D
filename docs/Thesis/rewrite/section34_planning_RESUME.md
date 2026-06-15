# Section 3/4 Proposition-Planning — Workflow Design + Resume State

**Created 2026-06-14.** Read this FIRST when resuming Section 3/4 planning (after the §2 work).

---

## 🆕 LATEST STATUS (2026-06-15) — Intro/Conclusion/Abstract + DWZ replication + Phase D  ← READ FIRST

This session extended past §3/§4 (those are done; their audit trail is below).

### DONE + COMMITTED this session
- **Intro / Conclusion / Abstract — full pipeline, now in the PDF (56 pp).**
  - A→B→C mirrored the §3/§4 workflow: `rewrite/introconcl_phase{A,B,C}_workflow.js` (3 opus planners + 1 opus red-team each).
  - Phase A → `rewrite/section_abstract/section1/section5_subsection_plan.json` (abstract 8 / intro 14 / conclusion 7 props). Phase B → `…_paragraph_ledger.json`.
  - **Inline expansion** (skipped re-running A/B, saved ~50 min): intro 6→9 ¶, conclusion 3→7 ¶ via `tmp/build_introconcl_expanded.py` — every verified prop kept VERBATIM; 5 new "filler" props added (significance, contributions, implications-by-audience, measurement-limits, future) per the NLM verbose menu. The 2 ceiling-breach props (contributions, implications) hand-hedged + advisor-checked.
  - Phase C → final prose, gate-clean: **QUALITATIVE** (NO coefficients in intro/concl/abstract — user rule), dash-free, reason+evidence atomic. Filled into `final_prose`.
  - **Phase D** → `tmp/build_introconcl_body.py` → `_abstract_body.tex/_intro_body.tex/_conclusion_body.tex` → wired into `thesis_draft_uottawa.tex` (Abstract env, Ch1, Ch5). Compiles 56 pp, all cites resolved.
  - Commits: `620b5eaf`(scripts)→`566ac2e9`(A)→`19321a84`(B)→`698b64ce`(expand)→`8983eac5`(C-prompt)→`7de45a41`(C-prose)→`e5d9d1da`(D).
- **DWZ Eq-4 construct-validity replication.**
  - Table `tab:dwz_replication` (`docs/Thesis/_dwz_replication.tex`, after the bible tables): DWZ Table 3(2) | our CEO Baseline | our CEO Extended. Paragraph = **§2.5 first validity check** ("We begin with the measure's construction…"). Commits `c50824d3`(table)+`d4bb56e2`(¶).
  - **Numbers verified (NOT memory):** DWZ col = paper Table 3 col 2, **user-confirmed vs the PDF** + NLM (`tmp/nlm_dwz_repl_numbers.json`). Ours = canonical run `outputs/econometric/ceo_clarity_extended/2026-04-29_141644/ceo_clarity_extended_table.tex`.
  - **Verified fact:** DWZ Eq-4 is **CEO-level** (CEO = main; CFO = DWZ's separate analysis we never use). Our spec = DWZ Eq-4 variable-for-variable. UncPreCEO 0.089 (ours) vs 0.093 (DWZ); total R² 0.369 ≈ DWZ 0.31 base + 0.054 incr.
  - **Honest caveats (in notes + ¶):** 3 SPEECH controls (UncPreCEO/UncQue/NegCall) RAW in both → comparable; 4 FIRM controls standardized in ours (`run_h0_3_ceo_clarity_extended.py` L344-357) → sign-comparable only; DWZ 2003-2015 vs ours 2002-2018 non-fin/non-util, smaller N.
- **NLM section conventions** → `DraftTemplate.txt` (abstract 5-element; intro verbose 6-9¶; conclusion implications/limits/future). Receipts: `tmp/nlm_*_structure*.json`, `tmp/nlm_verbose_intro_conclusion.json`.

### DEFERRED — the one open task (user: "leave additional analyses for later review")
- **Additional measure-study analyses** = "the residual must also behave like X", as the paragraphs FOLLOWING the DWZ ¶ in **§2.5** (placement = §2 measurement validity, NOT §4 — user corrected firmly).
- **CCCL** = confirmed candidate (user): SEC comment-letters flag a firm's *presentation* disclosure, NOT the CEO Q&A residual → residual orthogonal to regulatory attention. **Marginal significance → HEDGE.** Table `tab:h18_ceo2_decomp` exists (`docs/Draft/thesis_tables.tex` ~L557-621; CCCL var marked DROPPED 2026-06-14 in variable_ledger — reviving for this).
- **TODO:** finish surveying the arsenal (`docs/Draft/thesis_tables.tex` = curated; more in `outputs/econometric/`), pick checks DISTINCT from §2.5's existing convergent validity (PRisk/EPU already used), least-friction → write §2.5 verification ¶(s) + wire tables, hedged.

### OPEN ITEMS / caveats
- **QA-gap (pre-submission):** the new intro/concl/abstract prose is gate-verified (prose↔chain) but NOT human-domain-read sentence-by-sentence. Same as the §3/§4 QA item — a human read is the real pre-submission step.
- **DWZ §2.5 ¶** authored INLINE (not the verify pipeline); numbers verified vs the canonical run + user-confirmed DWZ Table 3.
- **Canonical-run dependency:** DWZ table + empire tables both source `UncResCEO` from `ceo_clarity_extended` via `_latest` (gen_empire_did_table.py:67). Consistent now; if a NEWER ceo_clarity_extended run appears, re-verify both still point to the same run.

---

## STATUS (2026-06-14)

- **🎉 FULL PIPELINE A→B→C→D COMPLETE + user-approved (2026-06-14).** §3 + §4 were proposition-planned (A), paragraph-allocated (B), prose-drafted (C) — all on opus, each gate-verified — and assembled into the uOttawa-convention PDF (D). Live state + remaining polish = **NEXT ACTION items 4-7**. Everything below this line (manifest, blocker, per-phase) is the audit trail.
- **Manifest RATIFIED** (8 units, below). **Both flagged input-fixes DONE + committed:**
  - `93a39904` — variable_ledger refreshed to the live 11-table / 5-subsection scope (stale summary-stats moments stripped -> table authority; 3 dropped tables + 12 dead-only vars marked; anchors verified current).
  - `08b27919` — SD-basis verified (§2.5 FB safe under both UncRes SDs 0.3010/0.3072) + an additive `_sd_basis_note_2026_06_14` recorded in `claim_findings_ledger.json` for §3.2.
- **Workflow design SETTLED** (below). **✅ BLOCKER RESOLVED + CONFIRMED** (cause = the `CLAUDE_CODE_SUBAGENT_MODEL` env pin; removed it; post-restart probe + the Phase-A fleet both ran `claude-opus-4-8`). See BLOCKER section.
- **✅ PHASE A COMPLETE (run `wf_7fca1f54-86c`, 4 opus agents, 839K tokens).** 3 opus planners + 1 opus red-team. Outputs written to `docs/Thesis/rewrite/`: `section{3.1,3.2,3.3,3.4,4.1}_subsection_plan.json` (the synthesized, red-teamed chains), `section34_phaseA_redteam.json` (flaws_found 0C/2Ma/5Mi all fixed + coverage_matrix), `section34_phaseA_planners_raw.json` (3 raw planners). reason+evidence atomic on EVERY purpose+proposition (0 missing). Coverage matrix: C1/C2/C4/C6 each homed once; H1/H1a/H1b paid off; 2.5-P4 promise → 4.1; C3/C7 correctly homeless; C5 stays in 2.5. **AWAITING USER RATIFICATION = the GATE before Phase B.**

---

## ✅ BLOCKER — opus subagent model (CAUSE FOUND + FIX APPLIED 2026-06-14; one restart + probe left)

- **ROOT CAUSE (settled — user was right, opus IS spawnable):** `~/.claude/settings.json` `env` block pinned `"CLAUDE_CODE_SUBAGENT_MODEL": "claude-sonnet-4-6"`. Per the resolution-order reference (below), this env var is **priority 1** — it overrides per-call `model:'opus'` AND subagent frontmatter, and a blocked override **silently falls back** (no error). That is why all 6 probes ran sonnet despite `model:'opus'`.
- **Reference that diagnosed it:** `C:\Users\sinas\Downloads\claude-code-opus-agents-stepbystep.md` (§1.2 = the #1 silent culprit; §6 = precedence: env var > per-call param > frontmatter > inherit). Pre-flight was otherwise clean: v2.1.177, no `availableModels` block, `ANTHROPIC_MODEL=claude-opus-4-8`.
- **FIX APPLIED (this session):** removed the `CLAUDE_CODE_SUBAGENT_MODEL` line from `~/.claude/settings.json` (user chose "remove the pin" over "force all → opus"). Effect after restart: per-call `model:'opus'` resolves to opus; plugin agents with their own frontmatter model stay cheap; frontmatter-less ones inherit the opus session. To REVERT: re-add `"CLAUDE_CODE_SUBAGENT_MODEL": "claude-sonnet-4-6"` to the `env` block.
- **WHY A RESTART IS REQUIRED:** the var was injected into THIS session's process env at launch (priority 1) — it cannot be overridden in-session, so the fix only takes effect in a NEW session.
- **REMAINING STEPS (post-restart):**
  1. Probe: spawn ONE trivial agent (Agent tool, `model:'opus'`), then read its `subagents/agent-*.jsonl` → confirm the `type:assistant` line's `model` reads `claude-opus-*` (NOT sonnet). `env | grep CLAUDE_CODE_SUBAGENT_MODEL` should now return nothing.
  2. If confirmed → launch Phase A from `sec34_phaseA_workflow.js` with the planners on opus.
  3. If somehow STILL sonnet → fall back to: Opus main loop (you) plans the 5 subsection chains directly + advisor (Opus) red-teams. Never fan out on sonnet.

---

## THE WORKFLOW DESIGN (8 agents, 2 spawns, user-shaped)

```
SPAWN 1 (Phase A — subsection proposition chains):  3 identical planners  +  1 red-team   = 4
        each reads the FULL manifest, plans independently      reads same manifest,
                                                                scrutinizes all 3, synthesizes best
   -> GATE: I write 5 per-subsection plan files + commit + SHOW user -> ratify
SPAWN 2 (Phase B — paragraph allocation + per-paragraph chains):  3 planners + 1 red-team = 4
   -> I write the 5 paragraph ledgers + commit + SHOW per subsection
TOTAL = 8 agents.
```

- **Phase A** per subsection: (1) identify the **PURPOSE** (what it delivers 100%); (2) design the **PROPOSITION CHAIN** that delivers it completely (ordered atomic props). NO paragraph allocation.
- **Phase B** per subsection: allocate the chain into **paragraphs**; give each paragraph an **atomic purpose**; plan each paragraph's **proposition chain**.
- **MOST IMPORTANT (user):** every agent (planners AND red-team) records `reason` (WHY) + `evidence` (manifest pointers it is BASED ON) **atomically** on every purpose, proposition, and red-team verdict. This is what makes the plan auditable.
- **Planners are IDENTICAL** (same task, same manifest, same diligence) — reliability by independent replication, NOT diverse lenses (user override of an earlier idea).
- **Who writes JSON:** agents RETURN schema-validated JSON; the MAIN loop writes the files (drift-guard + commit). (Workflow scripts cannot write files anyway.)
- **Saved Phase-A script (the COMPLETE artifact — verbatim prompts + schemas + rubric):** committed at `docs/Thesis/rewrite/sec34_phaseA_workflow.js`. It ran on SONNET (Workflow tool); re-use it once opus spawning is confirmed, OR read it as the spec for the Opus-main-loop fallback. Do NOT re-author from the summary above (drift risk) — use this file.

### Schemas (baked into the script)
- **SUBSECTION_PLAN_SET** = `{ subsections: [ { subsection_id, title, purpose{statement,reason,evidence}, delivers_claims[], tables_referenced[], hypotheses_paid_off[], pays_off_section2[], proposition_chain:[ {prop_id, statement, role, type(result-number|design-method|definitional|framing|external-NLM|callback-verified), reason, evidence[], numbers[](each token WITH its table source), register_locks[], depends_on[]} ], coverage{purpose_fully_delivered, gaps[]}, open_decisions[] } ], global_notes[] }`
- **REDTEAM_OUTPUT** = SUBSECTION_PLAN_SET + `redteam_report:[ {subsection_id, planners_compared[], flaws_found:[{flaw,severity(CRITICAL|MAJOR|MINOR),which_planner,reason,evidence[]}], synthesis_decisions:[{decision,reason,evidence[]}]} ]` + `coverage_matrix:[{claim,subsection,tables[],status}]`.

### Red-team rubric (10-point)
1 thin-claim ceiling · 2 register locks · 3 number-traceability (every number -> a named table cell; NEVER memory) · 4 C-traps (C6 keep formal Wald, NO Gelman-Stern; C4 NULL-only don't-strengthen; C1 don't-over-read POST -0.0250*) · 5 boundary (defs belong to 2.3/2.5/Appendix; 3.1 = construction+sample) · 6 coverage matrix (every live claim+table one home; H1/H1a/H1b paid off; 2.5-P4 promise delivered in 4.1) · 7 E-lessons (E1 NO Pagan re-insert; E2 cite executable line) · 8 purpose-completeness · 9 reason+evidence soundness · 10 open-decisions surfaced.

---

## THE 8-UNIT READING MANIFEST (ratified; every planner + red-team reads all)

1. `docs/Thesis/thesis_draft.tex` — locked §2 prose (2.1 framework, 2.2 H1/H1a/H1b, 2.3 UncResCEO/DWZ eq-4, 2.4 three estimating eqs, 2.5 convergent validity + scrutiny) + 20-entry bib.
2. `docs/Thesis/_tables_from_bible.tex` — the 11 result tables byte-exact (THE numbers).
3. `docs/Thesis/rewrite/claim_findings_ledger.json` — C1-C7 -> finding -> thinnest claim + register locks + RERUN risks + `_sd_basis_note`.
4. `docs/Thesis/rewrite/section2.1..2.5_paragraph_ledger.json` (5) — read the SUBSTANCE (_plan, paragraph intent/serves/boundary/thin_claim/guardrails, propositions{statement,type,verdict}, final_prose, next_action); SKIP the verbatim NLM receipt blocks (verification.{answer,quotes,located,span_pin}). 2.2 doubles as the Phase-B schema template.
5. `docs/Thesis/rewrite/section2_roadmap.md` — §2 backbone + coherence flags.
6. `docs/Thesis/variable_ledger.json` — var -> def -> construction file:line (refreshed; ignore DROPPED entries).
7. `docs/Thesis/DraftTemplate.txt` (structure) + `tmp/old_draft_81efc78.tex` lines ~97-176 (the COMPLETE prior §3/§4 prose — structural+numerical REFERENCE, NOT ratified, ceiling overrides; carries stale SDs + the dropped §4.2). REGENERATE if missing: `git show 81efc78:docs/Thesis/thesis_draft.tex > tmp/old_draft_81efc78.tex`.
8. `docs/Thesis/_archive/audit_20260612/AUDIT_PROTOCOL.md` (E1-E7) + `PROPOSITION_RULES.md` + `docs/Thesis/rewrite/paragraph_workflow.json` — discipline + taxonomy + verify-then-write pipeline.

---

## §3/§4 CONTENT SCAFFOLD (verified ground truth — 5 subsections; §4.2/C7 DROPPED)

| Sub | Purpose | Claim -> tables | Register cautions |
|---|---|---|---|
| 3.1 | Data, sample, variable construction; Table 1; defs POINT BACK to 2.3/2.5/Appendix | summary_stats | boundary: no re-deriving defs |
| 3.2 | Run-up exists: residual uncertainty elevated pre-announce for cash, not stock | C2 -> empire_building_did | correlational/within-firm; SD-basis decision |
| 3.3 | Round-trip: uncertainty resolves at announcement, cash persists | C1 (strongest) -> empire_drop_matched + _placebo | don't over-read negative POST |
| 3.4 | Cash-specificity: formal Wald diff 0.0983** (effect); cause 0.0064 n.s. (mechanism open) | C6 -> empire_cashspec + _placebo | NO Gelman-Stern; supportive-not-definitive |
| 4.1 | Rule out analyst scrutiny (promised 2.2-P5/2.5-P4) | C4 -> reason_gating + cash_scrutiny_validity + _channel | NULL-only, underpowered; don't strengthen |

## OPEN DECISIONS — ALL RESOLVED 2026-06-14 (recorded in claim_findings_ledger `_open_decisions_resolved_2026_06_14`)
- **SD-basis -> 0.3010** (all-universe Table-1 Panel B); 0.3072 retired; apply across 3.2/3.3/3.4. [user]
- **Orphan bibitems DROPPED** from thesis_draft.tex (bushee2018/everhart2025/gokkaya2025/lerman2026); verified 0 `\cite` usage first. [user]
- **Appendix I** already titled + `\input` (thesis_draft.tex L198); no rename needed; content edits still pending (unspecified). [user]
- **C6 two-way clustering rerun DONE** (tmp/cashspec_twoway_cluster.py): EFFECT diff 0.0983, firm-clustered p=.039** vs two-way p=.043** -> HOLDS at 5%, no strengthen/no damage. Keep locked firm-clustered table; optional one-line robustness note. [user run-and-see]

---

## NEXT ACTION
1. **Phase A ✅ DONE + verified + ratified** (run `wf_7fca1f54-86c`). 5 plans in `section{3.1,3.2,3.3,3.4,4.1}_subsection_plan.json`; red-team audit in `section34_phaseA_redteam.json`.
2. **Phase B ✅ DONE + gate PASSED** (`wf_d47aa9b8-235`; 4 opus agents, 850K tok). Wrote `section{3.1,3.2,3.3,3.4,4.1}_paragraph_ledger.json` + `section34_phaseB_redteam.json` + `_planners_raw`. Gate via `tmp/write_phaseB_ledgers.py` (mechanical, advisor): **27/27 Phase-A props homed exactly once** (0 orphan/dup), **0 invented numbers, 0 dropped register-locks**, `final_prose` force-empty + `prose_status` BLOCKED. AWAITING user ratification, then Phase C. (Original extraction-gate spec kept for the record:)
   - **(a) FILENAME LOCK — CRITICAL:** name the 5 output files EXACTLY `section{3.1,3.2,3.3,3.4,4.1}_paragraph_ledger.json` (NOT `_paragraph_plan` — Phase C's manifest + the §2 `section2.X_paragraph_ledger.json` convention both require `_paragraph_ledger`). If you pick another name, fix the Phase C manifest to match and verify all 5 paths resolve before launching C.
   - (b) set-completeness: collect every Phase-A `prop_id` from the 5 subsection plans; assert each is covered by some `from_phaseA_prop`; review any covered >once (legit split vs dup bug).
   - (c) force `final_prose=""` + `prose_status` BLOCKED on every paragraph (schema doesn't enforce it); flag any non-empty (planner went off-task).
   - (d) per-prop fidelity diff: sampled paragraph props' `numbers` + `register_locks` match their `from_phaseA_prop` source verbatim.
   - Then write the 5 ledgers, commit, SHOW user, ratify.
3. **Phase C ✅ DONE + gate PASSED** (`sec34_phaseC_workflow.js`; run `wf_4e9f1c0c-f53`; 4 opus agents, 690K tok). `final_prose` filled into all 5 `section{N}_paragraph_ledger.json` (prose_status = DRAFTED, gate-passed, pending .tex). Gate via `tmp/write_phaseC_prose.py`: **0 dash violations, 0 empty, 0 prop-coverage gaps, 0 invented numbers** (the only decimal-not-in-plan was 0.0094 = correct Table-1 PreAnnounceQtr mean, Panel A, in the Table-1 paragraph). Readable prose in `sec34_prose_preview.md`. Audit: `section34_phaseC_redteam.json` (+ `_drafters_raw`). User VERIFIED + approved the prose ("seems good", 2026-06-14).
4. **Phase D ✅ DONE** — §3/§4 prose assembled from the paragraph ledgers into the draft. `tmp/build_sec34_body.py` regenerates `docs/Thesis/sec34_body_from_ledgers.tex` (AUTO; source-of-truth = the `*_paragraph_ledger.json` final_prose; do NOT hand-edit) which the uOttawa draft `\input`s. **The whole A→B→C→D pipeline is COMPLETE + user-approved ("seems good", 2026-06-14).** To change wording: edit the ledger → rerun `build_sec34_body.py` → recompile.
5. **uOttawa draft = `docs/Thesis/thesis_draft_uottawa.tex`** (CLONE of `thesis_draft.tex`; original untouched). `book` class + uOttawa front matter (title / committee / declaration / abstract-placeholder / acknowledgements / dedication / TOC / List-of-Tables) + 1in+gutter margins; KEPT our conventions (author-year `natbib`, `newtx`, manual `\bibitem`). Chapters: 1 Intro (ph) · 2 Framework (§2 prose) · 3 Main Analyses (3.1-3.4) · 4 Additional (4.1) · 5 Conclusion (ph) · References · Appendix I · Tables. Each `\section` starts a new page (`titlesec`). **COMPILE:** kill Acrobat → `pdflatex ×2` (manual bib, no bibtex). The `uo-ethesis/` template + `.zip` + build artifacts are gitignored.
6. **Data-source fixes (3.1):** ExecuComp added as the 5th source (CEO identity → the eq-4 manager FE; VERIFIED `src/f1d/sample/build_tenure_map.py` Step 1.3, input `comp_execucomp.parquet`). S&P-1500 sample bound disclosed; user confirmed it is the WHOLE sample (2026-06-14), so wording widened residual→"the sample". **CAVEAT (unverified, carry forward):** prose now says ExecuComp coverage is *approximately* the S&P 1500 — VERIFIED only that ExecuComp is the CEO source, NOT that its coverage equals the S&P 1500 (ExecuComp ≈ S&P1500 + legacy firms). For a referee-grade claim, verify the coverage universe from the data before tightening the wording.
7. **Remaining open items:** Appendix-I content edits (still unspecified); title-page `[Examiner]` placeholders; abstract + Intro/Conclusion chapters still placeholders; original `thesis_draft.tex` still has the un-hyphenated `\title` (uOttawa version = "CEO Language-Uncertainty") — sync only if asked. Done already: orphan bibitems removed; C6 two-way-clustering evaluated (table stays firm-clustered); SD-basis 0.3010.
8. **QA GAP (advisor — the real remaining work before final submission):** the Phase-C gate verifies prose↔ledger FIDELITY (dash scan, number-trace, prop-coverage) but CANNOT catch ledger-level OMISSIONS or domain errors. ExecuComp was exactly that — a real source missing from the plan, caught only because the USER read 3.1. I domain-read only 3.4's prose myself; 3.1/3.2/3.3/4.1 passed the mechanical gate but never got a sentence-level domain read by me. Gates ≠ content review. Pre-submission QA = a human/domain read of ALL 5 subsections' actual sentences.
