# Section 3/4 Proposition-Planning — Workflow Design + Resume State

**Created 2026-06-14.** Read this FIRST when resuming Section 3/4 planning (after the §2 work).

---

## STATUS (2026-06-14)

- **Manifest RATIFIED** (8 units, below). **Both flagged input-fixes DONE + committed:**
  - `93a39904` — variable_ledger refreshed to the live 11-table / 5-subsection scope (stale summary-stats moments stripped -> table authority; 3 dropped tables + 12 dead-only vars marked; anchors verified current).
  - `08b27919` — SD-basis verified (§2.5 FB safe under both UncRes SDs 0.3010/0.3072) + an additive `_sd_basis_note_2026_06_14` recorded in `claim_findings_ledger.json` for §3.2.
- **Workflow design SETTLED** (below). Phase A was launched once but **ran SONNET** and the user killed it.
- **⛔ BLOCKER: opus-subagent spawn is DISPUTED. Resolve BEFORE re-spawning the fleet.**

---

## ⛔ BLOCKER — opus subagent model (DISPUTED — resolve first, do NOT spend the fleet until confirmed)

- **My probes (firm evidence):** subagents spawned via BOTH the Workflow tool AND the Agent tool (with `model:'opus'` OR omitted) recorded `"model":"claude-sonnet-4-6"` on the **assistant** message.
  - `subagents/workflows/wf_484fca33-0e3/agent-*.jsonl` (Phase-A planners) — sonnet on lines 4,5,6,9,10,12.
  - `subagents/workflows/wf_31962b68-29a/...` (probe, model omitted) — sonnet.
  - `subagents/agent-abb1768162511d230.jsonl` (Agent tool, model:'opus') — line 4 = `"type":"assistant"` + `"model":"claude-sonnet-4-6"`. (`"advisorModel":"claude-opus-4-8"` on the same line is a SEPARATE config field, not the run model.)
- **USER DISPUTES (strong prior — likely I am missing something):** "you CAN spawn opus agents, I've done it a thousand times."
- **UNRESOLVED.** Before re-spawning, TRY in order and CONFIRM the assistant-message model is opus on a fresh probe:
  1. `model: 'claude-opus-4-8'` (the FULL id, not the `'opus'` alias) on `agent()` / Agent tool.
  2. A `subagent_type` / `agentType` whose frontmatter pins opus.
  3. Check `/model` state + the ultracode / fast-mode interaction (these may set the spawn model).
  4. Re-probe a trivial agent, grep its transcript for the `type:assistant` line's `model` — must read `claude-opus-*` before proceeding.
- **DO NOT** re-run the 4-agent Phase-A fleet until opus is confirmed on the actual run model.

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
- **Saved Phase-A script (SONNET — needs the opus fix):** `<session>/.claude/.../workflows/scripts/sec34-phasea-subsection-chains-wf_484fca33-0e3.js` (re-author with the opus fix; the schemas + prompts + rubric are all in it).

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

## OPEN DECISIONS for the planners to SURFACE (not solve)
- 3.2 SD-basis: estimation-sample 0.3072 (N=27,622) vs all-universe Table-1 0.3010 (N=44,900); magnitude (~15%) robust either way; old §3 "Table 1 Panel B" pointer is stale. See `_sd_basis_note`.
- Orphan bibitems after the §4.2 drop: `lerman2026`, `bushee2018`, `everhart2025`, `gokkaya2025` -> cite-or-remove.
- Appendix I (cash word-list) pending user edits.

---

## NEXT ACTION (post-compaction)
1. **RESOLVE the opus-spawn blocker** (full model id / subagent_type / re-probe + confirm assistant-message model = opus). Discuss with user.
2. Once opus confirmed: re-author + run Phase A (the saved script + the opus fix).
3. GATE: write the 5 subsection-plan files (`docs/Thesis/rewrite/section3.1_subsection_plan.json` ... `section4.1_...`), commit, SHOW user, ratify.
4. Phase B (paragraphs).
