# BATTLE-TESTED HARNESS PRINCIPLES — distilled from 9 F1D workflow scripts   2026-06-25

> Source: `style_phase1_master.js` (read directly) + agent study of `style_phase1_pilot.js`, `sec34_phaseA/B/C_workflow.js`, `introconcl_phaseA/B/C_workflow.js`, `referee_audit_workflow.js`. The proven-pattern library to ground ANY new harness (Phase 2 / 4 / 5).

## THREE harness families (pick per task)
| Family | Files | Shape | Checker authority |
|---|---|---|---|
| **Style** | `style_phase1_{master,pilot}` | panel → **deterministic JS gate** → **by-reference** redteam | only POINTS (IDs); script copies kept verbatim |
| **Chain-pipeline** | `sec34_*`, `introconcl_*` (6) | panel → **re-authoring** redteam synthesis; phases ratify-LOCKed | RE-WRITES the synthesis |
| **Audit/referee** | `referee_audit_workflow` | partitioned skeptic lanes → **culling** redteam → separate **judge** | CULLS (refute-by-default) |

**Authority gradient of the checker** is the deepest design axis: by-reference (style) → re-author (chain) → cull-then-judge (referee).

## Recurring principles (all families)
- **P1 — Panel-of-3 producers + 1 checker.** Diversity by *paraphrase* (style: 3 reworded heads) OR by *independent sampling* (chain/referee: identical prompt). 3 = recall; 1 checker = precision.
- **P2 — Two parallelism levels:** redundancy (3 do the whole job) vs work-partition (wave across types / 5 aspect lanes). Keep orthogonal.
- **P3 — Forced StructuredOutput on every agent; "the returned object IS the data, not a message."** No free prose trusted.
- **P4 — Schema-AS-gate when no JS gate exists.** Required fields force checkable evidence (`number_audit`, `coverage_matrix`, `allocation_matrix`, `direction_audit`). "No JS gate" ≠ "no discipline."
- **P5 — Evidence-or-it-doesn't-exist, copied VERBATIM.** style enforces in JS (`isSub` after `norm()`); referee by agent ("can't reproduce the quote verbatim → INADMISSIBLE"); chain by rubric ("every number → a named table cell, NO memory numbers").
- **P6 — Claim-ceiling / register locks bind every unit** (correlational · no-identification · concentration-not-strict-specificity · mechanism-open · supportive-not-definitive) + named C-traps/E-lessons. Referee inverts: flag only their *violation* (over-claiming), never the hedge itself.
- **P7 — Stay-in-your-lane isolation** (referee: 5 exclusive aspects "so two teams never report the same issue"); cross-lane dups collapsed only at a final pass.
- **P8 — Null-guard + count-interpolation degrade, never crash.** `.filter(Boolean)`; `${planners.length}/3` flows surviving count into the checker; empty-set early return.
- **P9 — Read-only / describe-only separation** of observe from act. "DESCRIBE ONLY — THIS IS THE LOAD-BEARING RULE… a self-certified 'meaning unchanged' is exactly the failure this removes." Rewrite is always a separate human-gated phase.
- **P10 — Escalation to human via FLAGS, never auto-fix.** `guardrail_collision`/`side_notes`/`open_items` kept for humans. **No automated repair loop exists anywhere.**

## Patterns BEYOND master.js (net-new options)
- **B1 — Multi-phase ratify-LOCK pipeline** (chain). Plan → human ratifies → LOCKED → allocate → LOCKED → draft. Each phase reads prior ratified JSON as immutable. **Resume granularity = ratified disk artifacts** (no in-script resume).
- **B2 — Redteam-as-SYNTHESIZER (re-author)** vs by-reference. Chain trusts the checker to WRITE the best version; style forbids it ("you invent nothing"). Decision point per harness.
- **B3 — Refute-by-default CULLING redteam + verdict enum** `CONFIRMED / UNVERIFIABLE / FALSE_POSITIVE`; `culled[]` + `why_killed`. Subtractive, not additive.
- **B4 — Separate cross-cutting JUDGE** (referee chief-editor): dedups ACROSS lanes, severity-ranks one ledger, "invents no new findings." Chain folds judge into redteam; only referee separates.
- **B5 — SEQUENTIAL team batching for rate-limit.** referee line 178: "Teams run SEQUENTIALLY to avoid the server rate-limit burst: firing all 5 at once = 15 finders concurrently → trips 'Server is temporarily limiting requests' and kills the run. One team at a time caps peak concurrency at 3." (line 167 "concurrently" is a STALE comment — trust the code.)
- **B6 — Inter-phase verification sequencing.** Verify a claim (external lit/NLM) BETWEEN phases, "so a refutation costs a chain edit, not a re-allocation." Verify cheap before building.
- **B7 — null-degrade is an evolution scar:** pilot lacks it, master ADDED `if(!decisions){ degrade to gate-clean … 're-run this type' }`. Wide concurrent waves make a dead checker likely → guard required.
- **B8 — Anti-redundancy / novelty scar.** Near-neighbor paragraphs each state their angle ONCE; "NEVER harden to 'we are the first to' (the everhart/gokkaya scar)."

## Meaning vs mechanical split (the guiding rule)
**Scripts do the mechanically-decidable & cheap** (substring equality, set cardinality, prop→paragraph bijection). **Agents do meaning** (direction, soundness, register). Style pushes the boundary furthest toward the script, which is *why* its redteam can be safely demoted to ID-only.

## ABSENT in all 9 (verified) — net-new if needed
No `resumeFromRunId` / journaling / cache · no automated fix-loop (producer-repairs→re-check) · no max-retry counter · no budget loop. Resume = phase-granularity via ratified JSON a human re-feeds. **An in-script fix-loop with retry+escalation has NO template here.**

---

## → PHASE-2 MAPPING (which proven pattern each stage uses)
| Phase-2 stage | Proven pattern |
|---|---|
| EXTRACT ×3 panel per profile | P1 paraphrased panel (style) |
| GATE (exemplar-anchor verbatim + no-foreign-number) | P5 deterministic `norm/isSub` gate (style) — this is the anti-hallucination guard, mechanized |
| REDTEAM cull-by-default | B3 referee culling + verdict enum |
| JUDGE dedup → canonical library | B4 referee chief-editor, by-reference (P9 invents nothing) |
| SCOPE ×3 panel (rule→sections) | P1 panel applied to the NEW stage; reason-per-assignment = P4 schema-as-gate; default-INCLUDE reconcile |
| MATERIALIZE + COVERAGE | JS fan-out + set op (mechanical) |
| Execution | B5 SEQUENTIAL teams (peak 3) · P8 null-degrade · B1 phase artifacts on disk = resume |
| NOT used | B2 re-author checker (we can mechanize the anchor, so stay by-reference) · auto-fix-loop (unproven) → flag→human/re-run instead |
