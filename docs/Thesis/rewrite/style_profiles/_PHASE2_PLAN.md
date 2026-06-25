# Phase 2 — REWRITE (language simplification). PLAN + compaction-safe state. 2026-06-24

## Goal
Ask-1 (supervisor): rewrite every sentence into SIMPLE corp-finance register ("so plain his mother could read it"). **SPINE FROZEN** — propositions, numbers, guardrails, paragraph allocation unchanged; only sentence WORDING changes.

## LOCKED DECISIONS (Sina, 2026-06-24)
1. **Inline rewrite, NOT a multi-agent harness.** Sina skeptical of the fan-out; the harness's meaning-safety relied on an LLM-verifier that failed 3× this session, and relays add drift. The main agent rewrites directly, holding the full spine in context. The deterministic gate (the real safety) is approach-agnostic.
2. **PER-SUBSECTION workflow v2 (Sina, 2026-06-24 — drift-proofed after the abstract foul). NO SCRIPTS.** Meaning-first. The real block on drift is the **CONTENT-WORD LOCK** (the abstract fouls were synonym swaps of claim words the string-gate didn't protect). For EACH subsection:
   - (a) **READ PROPOSITIONS first** → extract each proposition's CLAIM-BEARING WORDS = the per-prop LOCK LIST: measure name, direction words (elevated / positive / concentrated), relation verbs (relating-to / unrelated-to / tracks), object nouns (bid-ask spread, information environment, cash/stock acquisitions), deal-stage words (committed / announced / completion / closes), and HEDGES (e.g. "consistent with" / "appears to" / "suggests" — a hedge swap silently changes claim STRENGTH; both the v1 and v2 abstract fouls fell through here, so extract the exact hedge every time).
   - (b) **READ OLD prose**, then **READ analyses** (the named anti-patterns).
   - (c) **WRITE — minimal edit.** Remove ONLY the anti-pattern a finding names (long → split; metaphor → drop; nominalization → verb). **KEEP every claim-bearing word VERBATIM — NEVER swap a claim word for a "plainer" synonym** (uncertainty≠sounds, information environment≠market, committed≠agreed). Light non-claim verbs (host→hold, field→take) ok. No reorder/merge/add/drop. **PROPOSITION beats old prose on any conflict.**
   - (d) **WRITE the new prose into the CLONE `final_prose`** (durable, before any check).
   - (e) **GATE — BY HAND.** Confirm VERBATIM survival of: every `number_audit` value + every guardrail phrase + **every claim-bearing word**; no new digit; sentence count holds/rises.
   - (f) **INDEPENDENT SEMANTIC CHECK (advisor, NOT me — I am the anchored author).** Per proposition, only the residue strings can't catch: polarity/negation flip, direction, hedge strength, clause re-attachment, added causation/transmission, scope/quantifier, entity swap.
   - (g) **RATIFY** — present to Sina; he approves each subsection individually (NOT one approval for all 16). On approval: commit clone + diff + ledger row.
3. **Constrained edit, not from-scratch.** Each flagged sentence: remove ONLY the named anti-pattern; keep the proposition; keep every protected string. Allowed: word-swap, sentence SPLIT. Forbidden: reorder, merge across propositions, add/drop any claim.
4. **Rewriter = Opus with a clean, accurate, constraint-explicit prompt** (Sina: a well-engineered prompt is followed carefully).
5. Nothing is applied to the thesis prose during rewriting — proposed diffs live in per-subsection diff files until Sina's final approval.
6. **CLONE-AND-CLEAN architecture (Sina, 2026-06-24).** The 16 ORIGINAL `section*_paragraph_ledger.json` stay FROZEN as the source-of-truth spine. Working copies live in `docs/Thesis/rewrite/_rewrite_working/` (cloned by `scratchpad/clone_clean_ledgers.py`, which blanked every `final_prose` — 79 fields — and flagged `prose_status`, keeping props/number_audit/guardrails/allocation intact; all 16 originals verified byte-identical afterward). New prose is written into the CLONE's `final_prose`; the original is never edited during rewriting. The clone is the rewrite target; the original is the spine reference + rollback.
7. **KEEP KEY JARGON (Sina, 2026-06-24).** This is an academic corporate-finance paper. The rewrite simplifies SENTENCE STRUCTURE (length, clause-stacking, metaphor, nominalization), it does NOT strip technical terms. "residual", "information asymmetry", "bid-ask spread", "placebo", etc. STAY. Plain register ≠ dejargoned. (This reverses the pilot's drop of "residual"/"information asymmetry".)

## Method, per paragraph (= decision 2, expanded)
1. PREP: from the ledger pull (a) `final_prose` (OLD prose, from the FROZEN original), (b) the propositions, (c) `number_audit` values, (d) the load-bearing **protected phrases** named by the guardrails (e.g. "indistinguishable from zero", "formal pooled test", "correlational ... not a tested mechanism"), (e) the Phase-1 findings naming each fancy sentence's anti-pattern.
2. REWRITE the flagged sentences (constrained edit; jargon kept — decision 7). Plain sentences pass through untouched.
3. **GATE — BY HAND, NO SCRIPT (Sina: "scripts are worst").** By careful read confirm: every `number_audit` value survives verbatim; every protected phrase survives verbatim; no new digit introduced; sentence count only holds or rises; no proposition dropped. FAIL → redo that sentence. Recorded in the diff file so it is auditable.
4. ADVISOR closed-checklist (props present + NEVER-traps absent), then Sina ratifies, then write the new prose into the CLONE + commit.

## Protected phrases — pulled by careful read (NO completeness script)
Guardrails are concept-notes, not exact strings. Per subsection, the protected-phrase list is extracted by careful read of that ledger's guardrails at PREP time (step 1d). There is no completeness script — the by-hand gate reads the guardrails directly.

## ORDER (16 subsection ledgers)
abstract · 1 · 2.1 · 2.2 · 2.3 · 2.4 · 2.5 · 3.1 · 3.2 · 3.3 · 3.4 · 4.1 · 4.2 · 4.3 · 4.4 · 5

## PROGRESS (compaction-safe resume table)
| subsection | status |
|---|---|
| abstract | NOT STARTED — scaffold ready (clone blank, 4 files pulled), awaiting Sina's "go" |
| (all 15 others) | not started |

> RESUME: read this file + the abstract's 4 files (frozen original ledger, clone in `_rewrite_working/`, `abstract_profile.json`, this plan). Next action = on Sina's "go", run the decision-2 cycle for the abstract (pull → rewrite → by-hand gate → advisor → ratify), then write into the clone + commit. ONE subsection at a time, HARD STOP at each ratify. The earlier `_PHASE2_PILOT_abstract.md` is SUPERSEDED (it stripped jargon; see decision 7).

## Standing constraints
- No thesis-prose edit without Sina's final approval. Diffs are proposals.
- Spine frozen (props/numbers/guardrails/allocation). Only wording changes.
- Sina ratifies EACH subsection (decision 2e) — NOT one end-review. Each diff artifact must be clean + protected-items-highlighted so per-subsection review is effective.
