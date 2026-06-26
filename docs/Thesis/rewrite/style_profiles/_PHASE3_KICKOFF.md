# PHASE 3 — FORK KICKOFF (you are the Phase-3 parallel session)   2026-06-25

**YOU ARE THE PHASE-3 FORK** — a git worktree running in PARALLEL with the Phase-2 session. Read this first.

**RESUME POINTER (2026-06-25):** the live state — work done, the cash KEEP/DOWNGRADE fork, the power verdict, next step — is in `docs/Thesis/rewrite/_PHASE3_STATE.md`. Read THAT first to resume.

## Your scope (ONLY this)
Redesign + insert NEW proposition chains for each section, into `docs/Thesis/rewrite/section*_paragraph_ledger.json` (the spine — the `proposition_chain` arrays).
Sina's verbatim intent (from the master ledger): *"we redesign and insert the new propositions (since we have some more robustness checks, and also we may need to change courses from cash deals to all deal types ... idk im just thinking out loud here."*
→ He was thinking out loud. **Phase 3 is a COLLABORATIVE redesign — START by discussing scope with Sina** (which new robustness checks? the cash→all-deal-types decision?). Do NOT autonomously rewrite the spine.

## Isolation rules (DO NOT BREAK — two sessions share one repo lineage)
- Work ONLY in this worktree: `../F1D-phase3`, branch `phase3/propositions`.
- **Do NOT touch `style_profiles/*`** (the 8 style profiles, the Phase-2 harness `style_phase2_principles_master.js`, the rulebooks) — that is the Phase-2 session's exclusive domain.
- **Do NOT run the Phase-2 harness** or its dry-run.
- **Do NOT edit `_REWRITE_MASTER_LEDGER.md`** (the one file both sessions share). Keep YOUR status in `_PHASE3_*.md` files only → zero merge conflict.
- Merge `phase3/propositions` back into `debug/campello-did-supervisor-interrogation` when done.

## Context to read first
1. The exported convo history (full Phase-2 design + the whole 5-phase map + why Phase 2/3 are independent).
2. `_REWRITE_MASTER_LEDGER.md` → "THE 5-PHASE MAP" + "DEFERRED — SINA'S VERBATIM THOUGHTS" (Phase 3) + "STILL LOAD-BEARING".
3. The spine you will edit: `docs/Thesis/rewrite/section*_paragraph_ledger.json` (`proposition_chain`, `guardrails`, `_phaseC_audit`).

## Safety
- HIGH blast-radius: propositions drive the Phase-4 rewrite. Move carefully; **ratify with Sina per section** before committing.
- Commit per section, verbose messages. All reversible via git.
- Keep the existing guardrails/register-locks intact unless Sina explicitly changes a claim.
