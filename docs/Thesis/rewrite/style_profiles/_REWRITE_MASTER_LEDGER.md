# THESIS REWRITE — MASTER LEDGER (durable, 100% compaction-safe)   2026-06-25

> **SINGLE SOURCE OF RESUME TRUTH.** Read THIS file to resume — nothing else required.
> The old `_PHASE2_PROGRESS.md` / `_PHASE2_PLAN.md` / `_PHASE2_HARNESS_DESIGN.md` are **ARCHIVED + SUPERSEDED** in `_OLD_APPROACH_SUPERSEDED/`. They describe the abandoned "Phase 2 = rewrite now" approach. **Do NOT follow them.** Kept only for history (git-recoverable anyway).
> **Branch:** `debug/campello-did-supervisor-interrogation` (commit rewrite work here, NOT master).

---

## CURRENT POSITION
**Phase 2 — brainstorming the principles-harness internals.**
Next concrete step: lock Phase-2 SUCCESS CRITERIA (below) with Sina → then topology falls out → then write the harness spec.

---

## THE 5-PHASE MAP (Sina, 2026-06-25 — replaces the old "rewrite 16 subsections now" plan)
| Ph | What | Status | Writes prose? |
|---|---|---|---|
| 1 | **Style analysis** — 8 profiles, 157 findings (writing weaknesses vs corp-fin convention) | ✅ DONE | no |
| 2 | **Principles harness** — analyse the Phase-1 analyses → the MINIMAL, most-effective writing-principles-per-section to abide by | ◀ IN PROGRESS (design) | **no → SAFE** |
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

## PHASE 2 — SUCCESS CRITERIA (PROPOSED, advisor-backed — pending Sina's lock)
Phase 2's job: turn 157 style findings → a minimal per-section ruleset. Lock these BEFORE choosing topology (topology falls out of them — Karpathy goal-driven).
- **COVERAGE** — every Phase-1 finding maps to ≥1 principle (nothing dropped silently).
- **GROUNDING** — every principle cites the finding ID(s) it comes from. No orphan/invented rules.
- **MINIMALITY** — the SMALLEST ruleset that achieves coverage. Hard target, not nice-to-have (Sina: "minimal of rules per section which is most effective").
- **Phase-2 failure modes to defend against:** (1) INVENTION — a rule grounded in no finding; (2) BLOAT — 157 rules instead of the minimal set; (3) OVER-GENERALIZATION — "max 20 words" when one 45-word sentence was flagged.
- **The Phase-2 check = grounding + minimality, NOT claim-fidelity.** Grounding is partly MECHANICAL (does finding-ID X exist? does it say what the rule claims?).
- ⛔ **Do NOT port the Phase-4 meaning machinery** (writer×3 → redteam×3 → judge). That defends meaning-drift, which cannot occur in Phase 2. Dead weight here.

## PHASE 2 — TOPOLOGY (CANDIDATE, not locked — brainstorm in progress)
Likely shape (falls out of the criteria above): **per-profile extractor → synthesis that dedupes → one grounding+coverage pass.** No 3-way meaning red-team. Reuse Phase-1 mechanics where they fit (TOOL_LOCK, forced StructuredOutput, describe-only checker-by-reference).

## PHASE 2 — INPUTS (the only files the harness needs)
- **8 style profiles** — `style_profiles/<type>_profile.json` (157 findings total; filter by `our_quotes[].para_id`).
- **16 spine ledgers** — `section*_paragraph_ledger.json` (guardrails / register context per section).
- **Corp-fin convention** — `DraftTemplate.txt` (the convention the findings were scored against).

---

## STILL LOAD-BEARING (carry across all phases)
- **Spine frozen** — 16 original `section*_paragraph_ledger.json` untouched (source-of-truth + rollback).
- **Keep jargon** — academic corp-fin paper. "residual", "information asymmetry", "bid-ask spread", "placebo" STAY. Simplify STRUCTURE, not vocabulary.
- **Propositions beat old prose** on any conflict.
- **NO SCRIPTS as a meaning/quality checker** (they overfit — false-passed both abstract fouls). Mechanical file ops (clone, blank, JSON edits) ARE fine — Sina authorized programmatic cleaning.

**Phase-4-ONLY rules** (not relevant in Phase 2 — recorded so they survive to Ph4):
- Clones in `_rewrite_working/` = the write target; originals frozen.
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
- _(this overhaul commit: 5-phase map + master ledger + abstract deleted + trio archived — to be appended)_
