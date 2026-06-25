# Phase-2 HARNESS — DESIGN STATE (durable, compaction-safe)  2026-06-24

> **STATUS: brainstorm PAUSED. Sina said "change approach completely" — the STRUCTURE below is a CANDIDATE, NOT locked. The PRINCIPLES are decided. Next session (Opus 4.8, max effort): re-decide the approach with Sina, then write the spec.**
> Goal: automate the Phase-2 rewrite so Sina reviews only the FINAL output, with nothing able to drift meaning.

---

## DECIDED PRINCIPLES (these survived the whole brainstorm — treat as locked)
1. **Reuse the proven Phase-1 harness mechanics** (from `style_phase1_master.js`):
   - **TOOL_LOCK** on every agent — exactly ONE StructuredOutput call, NO other tools (no advisor/web/read/write/bash), ONE turn, reason silently. (This fixed the wandering/idle-timeout deaths.)
   - **Forced StructuredOutput schema** — the returned object IS the data, no free prose.
   - **Paraphrased agents, identical task** — diversity via 3 reworded prompts.
   - **Describe-only checkers** + **redteam verifies/merges BY REFERENCE (IDs), invents nothing** — the main loop copies kept items verbatim.
2. **THE SAFETY INVERSION (why writing can be safe):** Phase-1 wrote NO prose → meaning-leak impossible. Phase-2 must write. So **ONLY the writer writes; EVERY checker is describe-only (flags BY REFERENCE, never rewrites).** A checker that cannot write cannot drift.
3. **THE INVARIANT TO PRESERVE = each PROPOSITION's CLAIM MEANING, not its words** (Sina, explicit). Claim-WORDS are NOT the target. The red-team judges semantic fidelity: same direction · same strength/hedge · same scope · nothing added / dropped / flipped / no added causation. Writers may reword freely for simplicity AS LONG AS the proposition's claim is unchanged.
4. **NO SCRIPTS anywhere** (Sina, repeatedly — "scripts are worst", "are you dumb? no scripts"). No string gate, no claim-word survival check. Scripts overfit to "word present" and FALSE-PASSED both abstract fouls. The red-team agents do all checking.
5. **Spine frozen** (16 originals untouched) · **clones = write target** · **keep jargon** · **propositions beat old prose on any conflict**.
6. **Sina reviews ONLY the final assembled output** — the red-team is the per-unit authority (replaces per-subsection ratify).

## CANDIDATE STRUCTURE (NOT locked — Sina called for a complete approach change)
Unit = paragraph (79 total), run as a wave. Per paragraph:
```
WRITER ×3   (paraphrased, TOOL_LOCK) — simplify, PRESERVE each proposition's claim (meaning)
     ▼
RED-TEAM ×3 (describe-only, TOOL_LOCK) — per proposition: does the candidate assert the SAME claim?
     ▼            (direction · strength/hedge · scope · nothing added/dropped/flipped) — flag BY REFERENCE
   JUDGE — pick the zero-foul candidate
     │ all fouled ─► writer repairs ONLY the flagged claim → re-red-team (max 3 → ESCALATE to Sina)
     ▼
   winner ─► clone
     ▼
   all 79 paragraphs done ─► Sina reads the final ONCE
```

## OPEN (re-decide next session — Sina wants to change approach)
- "Change approach completely" — scope unspecified. Re-open: writer count (1 vs 3), judge necessity, fix-loop vs regenerate, wave vs sequential, paragraph vs subsection unit, how the red-team is told the propositions, escalation rule.
- The abstract proved the KERNEL by hand: 1 writer (me) + 1 independent checker (advisor) + fix-loop caught both fouls. The harness automates this kernel; the open question is how much redundancy around it.

## SOURCE FILES TO STUDY (the proven Phase-1 harness)
- `docs/Thesis/rewrite/style_phase1_master.js` — the real prompts (TOOL_LOCK, panelPrompt ×3, redteamPrompt, schemas, the in-script gate we will NOT reuse).
- `docs/Thesis/rewrite/style_phase1_pilot.js` — template.
- `tmp/run_wave_*.js` — wave runners. `tmp/build_master.py` + `tmp/embed_master.py` — regenerate a wave deterministically.

## WHAT THE ABSTRACT (done by hand, ratified `5a073b4b`) TAUGHT US
- Drift = synonym swaps of a proposition's claim (uncertainty→sounds, information environment→market, committed→agreed, "consistent with"→"appear to" [hedge]).
- A string/word check FALSE-PASSED both v1 and v2 fouls → cannot be the meaning authority.
- The INDEPENDENT checker caught what the anchored author missed → writer ≠ checker, always.
- Hedge strength is claim-bearing (a hedge swap silently changes the claim).
