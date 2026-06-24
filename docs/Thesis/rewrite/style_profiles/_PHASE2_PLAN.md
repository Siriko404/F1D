# Phase 2 — REWRITE (language simplification). PLAN + compaction-safe state. 2026-06-24

## Goal
Ask-1 (supervisor): rewrite every sentence into SIMPLE corp-finance register ("so plain his mother could read it"). **SPINE FROZEN** — propositions, numbers, guardrails, paragraph allocation unchanged; only sentence WORDING changes.

## LOCKED DECISIONS (Sina, 2026-06-24)
1. **Inline rewrite, NOT a multi-agent harness.** Sina skeptical of the fan-out; the harness's meaning-safety relied on an LLM-verifier that failed 3× this session, and relays add drift. The main agent rewrites directly, holding the full spine in context. The deterministic gate (the real safety) is approach-agnostic.
2. **NO microreview from Sina.** He reviews ONCE, at the very end, over the complete diff. The harness/agent must be trustworthy enough that he is not pinged per-paragraph.
3. **Constrained edit, not from-scratch.** Each flagged sentence: remove ONLY the named anti-pattern; keep the proposition; keep every protected string. Allowed: word-swap, sentence SPLIT. Forbidden: reorder, merge across propositions, add/drop any claim.
4. **Rewriter = Opus with a clean, accurate, constraint-explicit prompt** (Sina: a well-engineered prompt is followed carefully).
5. Nothing is applied to the thesis prose during rewriting — proposed diffs live in per-subsection diff files until Sina's final approval.

## Method, per paragraph (deterministic where possible)
1. PREP (one-time per paragraph): from the ledger pull (a) `final_prose`, (b) the propositions, (c) `number_audit` values, (d) the load-bearing **protected phrases** named by the guardrails (e.g. "indistinguishable from zero", "formal pooled test", "to our knowledge", "correlational ... not a tested mechanism"), (e) the Phase-1 findings naming each fancy sentence's anti-pattern.
2. REWRITE the flagged sentences (constrained edit). Plain sentences pass through untouched.
3. **GATE (deterministic script):** every `number_audit` value AND every protected phrase survives **verbatim** in the new prose; sentence count may only rise (splits) or hold; no proposition text dropped. FAIL → redo that sentence.
4. Save old→new diff to the subsection's diff file.

## GATE SCRIPT spec (to build)
Input: ledger paragraph + proposed new prose. Checks: (1) each number_audit value ∈ new prose; (2) each protected phrase ∈ new prose; (3) no new digit/number introduced; (4) #sentences_new ≥ #sentences_old. Output: PASS / FAIL+which. Pure string ops, no LLM.

## Open prerequisite (blocks the guardrail half of the gate)
**Guardrail-completeness pass:** guardrails are concept-notes, not exact strings. Before the gate can mechanically check guardrails, extract the exact **protected phrase list per paragraph** from each ledger's guardrails. (Numbers gate works now; guardrail gate needs this list.) Until done, protected phrases are pulled by careful read.

## ORDER (16 subsection ledgers)
abstract · 1 · 2.1 · 2.2 · 2.3 · 2.4 · 2.5 · 3.1 · 3.2 · 3.3 · 3.4 · 4.1 · 4.2 · 4.3 · 4.4 · 5

## PROGRESS (compaction-safe resume table)
| subsection | rewrite | gate | diff file |
|---|---|---|---|
| abstract | DRAFTED (pilot) | not yet scripted | `_PHASE2_PILOT_abstract.md` |
| (all others) | not started | — | — |

> RESUME: read this file + `_PHASE2_PILOT_abstract.md`. Next action = decide whether the abstract pilot register is the target (Sina to confirm at end), build the gate script, then proceed subsection by subsection writing `_PHASE2_diff_<id>.md` per subsection. Spine ledgers are the source of truth for protected items.

## Standing constraints
- No thesis-prose edit without Sina's final approval. Diffs are proposals.
- Spine frozen (props/numbers/guardrails/allocation). Only wording changes.
- End-review is the ONLY human gate → the final diff artifact must be clean + complete + protected-items-highlighted so that one review is effective.
