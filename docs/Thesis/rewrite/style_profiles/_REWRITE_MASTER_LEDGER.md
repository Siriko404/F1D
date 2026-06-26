# THESIS REWRITE — MASTER LEDGER (durable, 100% compaction-safe)   2026-06-25

> **SINGLE SOURCE OF RESUME TRUTH.** Read THIS file to resume — nothing else required.
> The old `_PHASE2_PROGRESS.md` / `_PHASE2_PLAN.md` / `_PHASE2_HARNESS_DESIGN.md` are **ARCHIVED + SUPERSEDED** in `_OLD_APPROACH_SUPERSEDED/`. They describe the abandoned "Phase 2 = rewrite now" approach. **Do NOT follow them.** Kept only for history (git-recoverable anyway).
> **Branch:** `debug/campello-did-supervisor-interrogation` (commit rewrite work here, NOT master).

---

## CURRENT POSITION
**Phase 2 — ✅ DONE. All 8 type-rulebooks built: 140 principles, 100% finding coverage.** Output in `style_profiles/_rulebooks/<type>.json` — abstract 14 · intro 14 · hypotheses 18 · lit_review 18 · methods 15 · data 19 · conclusion 15 · results 27. Harness `docs/Thesis/rewrite/style_phase2_principles_master.js` (`node --check` PASS). **Next: Sina reviews the 8 rulebooks → Phase 3.**

**FINAL harness = 2 agent-layers PER TYPE, fully independent (NO global / cross-type step — Sina's locked spec):**
- **L1** neurodiverse PANEL ×3 EXTRACT → deterministic JS gate (exemplar-anchor verbatim + no foreign number; scaffolding-refs Phase-N/Section/Table/H1 exempt).
- **L2** ONE RED-TEAM agent = SCRUTINIZE (refute fabricated/absolute, by reference) **and** SYNTHESIZE (merge dups → the minimal rulebook).
- JS materialize → each type its own rulebook. **No judge/classify/finalize** (cross-type dedup FORBIDDEN; a universal rule recurs naturally because each type's findings surface it).
- args = `{ profiles:[{type, findings}], maxProfiles? }`. Runner stringifies args → harness `JSON.parse`s. Startup input-count guard logs received per-type counts.

**3 harness bugs found + fixed (durable):** (1) args-as-string → parse. (2) "Phase-**4**" digit false-rejected 17 rules → `stripScaffolding`. (3) red-team keeps-0 when its IDs don't match candidates (hit on the 87-candidate results set) → degrade-to-gate-clean instead of empty.

**Provenance:** `results.json` = the earlier validated results dry-run (27 rules, 32/32) — its 2-layer re-run tripped bug #3; the dry-run's panel→gate→cull principles are identical mechanics + complete.

**PROCESS LESSON (load-bearing):** large inline arg pastes SILENTLY DROP findings. data/conclusion/results were truncated on first pass, then re-run with verified-complete args (one type per run). **For ANY future Phase-2 run: build args via `style_profiles/_phase2_scripts/build_args.py`, paste the WHOLE file unabridged, then verify `coverage.total_findings == that type's profile[] count`.**

> **PARALLEL FORK (2026-06-25):** Phase 3 runs concurrently in a separate git worktree `../F1D-phase3` (branch `phase3/propositions`) — see `_PHASE3_KICKOFF.md`. THIS session = Phase 2 ONLY. The fork edits the proposition spine and must NOT touch `style_profiles/*` or this ledger; merge its branch back when done.

### HOW TO RE-RUN A TYPE (if Sina wants one redone)
1. **Build args** for that ONE type: `style_profiles/_phase2_scripts/build_args.py` → `build(["<type>"], "<type>")` → `phase2_args_<type>.json` (reads `style_profiles/<type>_profile.json` `profile[]`).
2. **Read the WHOLE file, paste it UNABRIDGED** as the Workflow `args` (do NOT pre-stringify; do NOT trim — trimming silently drops findings). One type per run keeps the paste small enough to reproduce completely.
3. **Invoke:** `{ scriptPath: "docs/Thesis/rewrite/style_phase2_principles_master.js", args: <object> }` (Workflow tool, NOT `node`). ~4 agents (panel ×3 + redteam ×1), ~12–15 min.
4. **On return:** `result.coverage.<type>.total_findings` MUST equal that type's `profile[]` count, else the paste dropped findings → redo. Write `result.rulebooks.<type>` (strip to the 6 fields) → `_rulebooks/<type>.json`. (See `style_profiles/_phase2_scripts/finalize_rulebooks.py` for the mechanical write.)
5. ⛔ **NO external scripts to GRADE/audit the rules** (Sina, strict). The harness's OWN agents + JS gate do the checking; READ the returned object. Mechanical file writes/extraction of the result = fine; `.js` workflow harness ≠ audit script.

---

## THE 5-PHASE MAP (Sina, 2026-06-25 — replaces the old "rewrite 16 subsections now" plan)
| Ph | What | Status | Writes prose? |
|---|---|---|---|
| 1 | **Style analysis** — 8 profiles, 157 findings (writing weaknesses vs corp-fin convention) | ✅ DONE | no |
| 2 | **Principles harness** — analyse the Phase-1 analyses → the MINIMAL, most-effective writing principles per WRITING-TYPE (8 rulebooks) | ✅ DONE — 8 rulebooks, 140 principles, 100% coverage | **no → SAFE** |
| 3 | **Propositions redesign** — insert new propositions (more robustness checks; maybe pivot cash→all deal types) | 📝 DEFERRED (record only) | no |
| 4 | **Rewrite harness** — the actual rewriting of the whole thesis by a harness (the writing process) | 📝 DEFERRED | **YES → drift-defense lives HERE** |
| 5 | **Audit-harness stack** — a dedicated stack to audit the thesis hardnosedly, referee-proof | 📝 DEFERRED (record only) | no |

**Why this ordering is right:** Phase 3 may move the spine (cash→all deals, new robustness). Rewriting prose before that = throwaway. So principles (Ph2, content-independent) now; rewrite (Ph4) only after the spine is final. Phase 2 writes NO prose → meaning-drift is structurally impossible (same reason Phase 1 was safe).

---

## DEFERRED — SINA'S VERBATIM THOUGHTS (record only; discuss when we reach the phase, do NOT act now)
- **Phase 3:** *"we redesign and insert the new propositions (since we have some more robustness checks, and also we may need to change courses from cash deals to all deal types ... idk im just thinking out loud here. record my thourhgts and we will discuss them when we come to the phase later on)"*
- **Phase 4:** *"finally will be phase 4 which is the actual rewriting of the whole thesis by a harness. this will be the writing process."*
- **Phase 5:** *"next step after that will be to design an entire harness stack only for auditting the thesis extremely dilligently and hardnosedly, making it 100% referee proof; again, its not for now to brainstorm, so just record and wait to discuss it later when we come to it."*

---

## PHASE 2 — SUCCESS CRITERIA (LOCKED 2026-06-25 by Sina)
Phase 2's job: turn 157 style findings → a minimal writing-principle rulebook per WRITING-TYPE (8). Locked BEFORE topology (Karpathy goal-driven).
- **COVERAGE (two parts)** — (a) FINDING-coverage: every Phase-1 finding → ≥1 canonical principle (nothing dropped). (b) TYPE-coverage: every type's rulebook contains every principle CLASSIFY assigns it — a UNIVERSAL rule lands in all 8 rulebooks; a TYPE-SPECIFIC rule in its source type(s). Default-include → a needed rule is never missing.
- **GROUNDING** — every principle cites the finding ID(s) it comes from. No orphan/invented rules.
- **MINIMALITY = WITHIN-TYPE ONLY.** Output = one self-contained rulebook PER writing-type (8); a Phase-4 subsection reads its TYPE's rulebook. Minimal = no redundant principle WITHIN a type's rulebook. A universal rule appears in ALL 8 rulebooks. **Cross-type dedup is FORBIDDEN** — it would starve a rulebook of a rule it needs.
- **EFFECTIVE** (operationalizes Sina's "most effective") — each principle is actionable via its REAL exemplar (before = our_quote, after-register = the finding's exemplar quote), NEVER an invented threshold. Vague rules ("avoid noun pile-ups") are rejected; usable, anchored rules ("name the construct plainly as the exemplars do — 'CEO clarity', 'negative word list' — not 'a residual measure of chief-executive question-and-answer uncertainty'") pass.
- **Phase-2 failure modes to defend against:** (1) INVENTION — a rule grounded in no finding; (2) BLOAT — redundant principles WITHIN a rulebook (cross-type repetition is NOT bloat); (3) OVER-GENERALIZATION — "max 20 words" when one 45-word sentence was flagged; (4) UNDER-TYPING — a type missing a universal rule it needs (CLASSIFY's default-include prevents this).
- **The Phase-2 check = grounding + actionability + coverage, NOT claim-fidelity.** Coverage is partly MECHANICAL (does finding-ID X exist / is it cited?) but only counts PAIRED with the cull faithfulness check (a cited-but-unaddressed ID games the set op alone).
- ⛔ **Do NOT port the Phase-4 meaning machinery** (writer×3 → redteam×3 → judge). That defends meaning-drift, which cannot occur in Phase 2. Dead weight here.

## PHASE 2 — TOPOLOGY (BUILT 2026-06-25 → `docs/Thesis/rewrite/style_phase2_principles_master.js`, `node --check` PASS)
Reuse Phase-1 mechanics: TOOL_LOCK; forced StructuredOutput; describe-only checkers BY REFERENCE; null-degrade; profiles run in **capped-concurrency BATCHES** (`args.maxProfiles`, default 2 → peak ~6; rate-limit scar respected via the cap, not strict sequence). **NO writer×3 / redteam×3** (no prose → no drift).

**GRANULARITY = 8 writing-types** (Sina + advisor, evidence-locked 2026-06-25). Measured findings per bucket (`_findings_dist.py`, all 157):
- per **subsection (16):** avg 12, **3 thin ≤5** (2.5=5, 4.2=3, 4.3=4) → wasteful + uneven.
- per **section (6):** §2=66, §3=64 → piles too big; §2 alone blends lit_review+hypotheses+methods.
- per **writing-type (8): 14–32, avg 20, balanced — and the grain the findings ALREADY live in → CHOSEN.** A Phase-4 subsection reads its type's rulebook (3.2/3.3/3.4→results, 2.3–2.5→methods, …).

**Principle schema (anti-hallucination):** `{principle_id, trigger, exemplar_anchor, gap_fix, finding_ids[], meaning_flag}` — target = the finding's OWN verbatim exemplar quote; `gap_fix` RELATIVE not absolute; `meaning_flag` = `guardrail_collision` carried to Phase 4. (See ANTI-HALLUCINATION GUARD below.)

Pipeline (as REARCHITECTED 2026-06-25 — **3 agent layers, max**):
1. **LAYER 1 — EXTRACT ×3 neurodiverse panel per profile** (different minds catch different gaps; the dry run proved it — one panelist caught a nominalized-subject gap the other two missed). Reads ONLY `profile[]`; all materialities. → candidate principles.
2. **GATE (JS, mechanical, no LLM):** drop a rule unless its `exemplar_anchor` is a VERBATIM quote of a cited finding (proven `norm/isSub`) AND `gap_fix` has no non-scaffolding number absent from the finding (`stripScaffolding` removes Phase-N/Section/Table/H1/column/step/equation FIRST — the Phase-4-digit false-reject fix) AND `finding_ids` exist. = the anti-hallucination rail, mechanized.
3. **LAYER 2 — CULL ×1 redteam per profile** (by reference, refute-by-default): kill (F1) fabricated absolute / (F2) relative→absolute hardening / unfaithful; merge dups WITHIN profile; KEEP `meaning_flag`. null-degrade → gate-clean.
4. **LAYER 3 — FINALIZE ×1** (ONE global agent = merged old JUDGE+CLASSIFY): cross-profile dedup → canonical (each carries `source_types`) AND tag each universal vs type-specific in one pass (default-include). `applies_to` = universal ? all 8 types : `source_types`. null-degrade → over-include.
5. **MATERIALIZE (JS):** fan-out → **8 type-rulebooks** + COVERAGE reconcile (finding-coverage + per-type counts + empty-type flag).

Maps to locked criteria: COVERAGE = finding-coverage (5) + type completeness (4+5) · GROUNDING = `finding_ids` + cull faithfulness · MINIMALITY = finalize canonical (within-type unique) + finalize fan-out (cross-type repetition) · EFFECTIVE = the exemplar-anchored schema.

### ANTI-HALLUCINATION GUARD (Sina's trap, 2026-06-25 — evidence-verified)
**Danger:** a finding is a RELATIVE, exemplar-anchored observation ("our sentences run longer than the exemplars; Harford avg 15.8 w/sent"); an agent could fabricate an ABSOLUTE prescription ("be short / ≤35 words") the finding never made → over-shortening kills the academic register.
**Verified against the data:** all **157** surviving findings (`profile[]`: abstract 15 · intro 14 · lit_review 18 · hypotheses 23 · data 20 · methods 18 · results 32 · conclusion 17) carry `exemplar_pattern` AND a non-empty `exemplar_quotes` (0 empty arrays) → every rule HAS a real anchor.
**The guard: RELATIVE, never ABSOLUTE.** A rule's target = the finding's own exemplar quotes (verbatim from papers). In-finding numbers (e.g. "15.8 avg") may be cited as the exemplar average, NEVER as a cap. Fallback if a quote is ever thin: mark the rule "register-only" → extra CHECK scrutiny (empirically unused; 0 thin).
**COVERAGE denominator** = these 157 survivors only (`profile[]`, post reject/merge).

## PHASE 2 — INPUTS (the harness `args`)
- **profiles** — 8 `style_profiles/<type>_profile.json`, each `profile[]` ONLY (157 findings). The sole finding source.
- **types** — the 8 type ids: abstract · intro · lit_review · hypotheses · data · methods · results · conclusion.
- **roster + convention** — one-line description per type + the `DraftTemplate.txt` gist. Context for the CLASSIFY universal-vs-specific call ONLY; never extracted as principles.
- **NOT a Phase-2 output:** guardrails / protected-phrases / keep-jargon stay in the SPINE (Phase 4 pulls them fresh). Phase 2 = pure style/register, content-independent → survives Phase-3.

---

## STILL LOAD-BEARING (carry across all phases)
- **Spine frozen** — 16 original `section*_paragraph_ledger.json` untouched (source-of-truth + rollback).
- **Keep jargon** — academic corp-fin paper. "residual", "information asymmetry", "bid-ask spread", "placebo" STAY. Simplify STRUCTURE, not vocabulary.
- **Propositions beat old prose** on any conflict.
- **NO SCRIPTS as a meaning/quality checker** (they overfit — false-passed both abstract fouls). Mechanical file ops (clone, blank, JSON edits) ARE fine — Sina authorized programmatic cleaning.

**Phase-4-ONLY rules** (not relevant in Phase 2 — recorded so they survive to Ph4):
- Clones in `_rewrite_working/` = the write target; originals frozen. Each subsection's rewrite reads its TYPE's Phase-2 rulebook (8 total; e.g. 3.2/3.3/3.4 → results, 2.3–2.5 → methods).
- Meaning authority = a RED-TEAM layer (N describe-only agents vs each proposition), never a script.
- **The invariant = each proposition's CLAIM MEANING, not its words.** Writers may reword freely if the claim is unchanged.
- Safety inversion: only the writer writes; every checker is describe-only (flags BY REFERENCE).

---

## ABSTRACT — DELETED 2026-06-25 (do NOT resurrect as "ratified")
The abstract was rewritten + ratified under the OLD approach (commit `5a073b4b`). Under the new map, real rewriting is **Phase 4** (after Phase 3 may revise propositions), so that rewrite is throwaway.
- Clone prose **blanked**: `_rewrite_working/section_abstract_paragraph_ledger.json` `final_prose=""`, `prose_status="DELETED 2026-06-25..."`. **Spine (9 props, guardrails) intact.**
- Diff record `_PHASE2_diff_abstract.md` **deleted**.
- All git-recoverable from `5a073b4b` if ever needed. It proved the method; it is NOT final prose.

---

## REUSABLE ASSETS + WHERE THEY LIVE
- **Phase-1 harness mechanics** (the proven runner): `docs/Thesis/rewrite/style_phase1_master.js` — TOOL_LOCK (exactly ONE StructuredOutput call, no other tools, one turn), forced StructuredOutput schema (returned object IS the data), 3 paraphrased panel agents, describe-only redteam that verifies/merges BY REFERENCE (IDs). Template for any phase's harness.
- **Drift taxonomy** (Phase-4 red-team will need it — the 4 foul classes the abstract exposed):
  | foul class | abstract example |
  |---|---|
  | referent swap | "uncertainty" → "sounds" |
  | entity swap + added transmission | "information environment" → "market" |
  | deal-stage drift | "committed" → "agreed" |
  | hedge-strength drift | "consistent with" → "appears to" |
- **The hard lesson:** a string/word check FALSE-PASSED every one of those → a script can never be the meaning authority. Writer ≠ checker, always.

---

## HOW TO RESUME (post-compaction)
1. Read THIS file. Find CURRENT POSITION (top).
2. Ignore `_OLD_APPROACH_SUPERSEDED/` — it is the abandoned approach.
3. Continue from CURRENT POSITION. Do not start substantive work without Sina's "go".

## COMMITS (rewrite program, this branch)
- `5a073b4b` abstract v2 (OLD approach — now deleted)
- `35e0b189` reconciled abstract-era decisions with harness direction (OLD)
- `ef8440b6` 5-phase map + master ledger + abstract deleted + trio archived
- `3c36561f` Phase-2 harness built (8-type, 4-layer)
- `65acf254` Phase-3 fork kickoff
- `fb32de3d` durable dry-run recipe + go-gate
- _(this commit: dry-run results PASSED + 2 bug fixes (args-string, Phase-4-digit) + rearchitect 4→3 layers + batched profiles — to be appended)_
