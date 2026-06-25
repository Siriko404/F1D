# Phase-2 REWRITE — PROGRESS LEDGER (durable, 100% compaction-safe)  2026-06-24

> **SINGLE SOURCE OF RESUME TRUTH.** After any compaction, read THIS first, then `_PHASE2_PLAN.md` (design + locked decisions 1–7).
> **Status now: scaffold COMPLETE · 0 / 16 rewritten · awaiting Sina's explicit "go" on the abstract.**
> **Branch: `debug/campello-did-supervisor-interrogation`** (commit Phase-2 work here, NOT master).

---

## HOW TO RESUME (post-compaction) — do this exactly
1. Read this file, then `_PHASE2_PLAN.md` (locked rules).
2. Find the first row **not fully RATIFIED** (order FIXED, top to bottom). If that row has partial ✅ (e.g. rewritten ✅ but ratified ☐), RESUME AT ITS FIRST ☐ step — the in-flight draft is in that row's diff file; do NOT redo completed steps.
3. **Do NOT start/continue without Sina's explicit "go".** One subsection at a time. HARD STOP at each ratify.
4. Run the decision-2 **v2** cycle (CONTENT-WORD LOCK is the drift block):
   `READ PROPS → extract claim-words → READ old prose + analyses → WRITE (claim-words VERBATIM, structure-only) → write into CLONE → BY-HAND GATE (numbers + guardrail phrases + claim-words all survive) → INDEPENDENT advisor semantic check → Sina RATIFY → commit`.

## LOCKED RULES (recap — full text in `_PHASE2_PLAN.md`)
- **No scripts** for the gate — by hand (Sina: "scripts are worst").
- **Clone is the write target; the ORIGINAL ledger is FROZEN** (spine source-of-truth + rollback).
- **Keep key jargon** ("residual", "information asymmetry", "bid-ask spread", …). Simplify sentence STRUCTURE only.
- **Per-subsection ratify** = the MANUAL abstract model ONLY. **SUPERSEDED for the automated phase (subsections 2–16):** the harness red-team is the per-unit authority; Sina reviews the FINAL output (see `_PHASE2_HARNESS_DESIGN.md` principle 6).
- **Constrained edit**: remove named anti-pattern, keep every proposition + protected string; splits ok; NO reorder / merge / add / drop.
- **Nothing touches the thesis prose** until Sina's final approval; rewrites live in the clones + diff files.

## THE 4 FILES PER SUBSECTION (the only inputs needed — 100% safe set)
1. **original** `docs/Thesis/rewrite/section*_paragraph_ledger.json` — FROZEN spine (props / number_audit / guardrails) + OLD prose.
2. **clone** `docs/Thesis/rewrite/_rewrite_working/section*_paragraph_ledger.json` — same spine, blank prose = write target.
3. **style profile** `docs/Thesis/rewrite/style_profiles/<type>_profile.json` — anti-patterns (filter by `para_id`).
4. **`_PHASE2_PLAN.md`** — workflow + by-hand gate + jargon rule + NEVER-traps.

⚠️ **Regen script `_rewrite_working/_clone_clean_ledgers.py` = FULL RESET. Safe ONLY before any rewrite exists.** It blanks ALL 16 clones' `final_prose` unconditionally — re-running after a clone holds ratified prose WIPES that rewrite ("originals untouched" is true, but the CLONES are the output). Once any clone is rewritten, NEVER re-run it. To roll back ONE clone: `git restore <clone path>` (or `git checkout <SHA> -- <clone path>`).

---

## STATUS — 16 subsections (FIXED order). ☐ = todo · ✅ = done
Profile column: resolve at PULL by `para_id` — a finding belongs to subsection X if its `our_quotes[].para_id` starts with X's prefix (e.g. `abstract-P1`, `1-P6`, `4.2-…`). 8 section-level profiles span 16 subsections; confirm coverage per row. Props counted at PULL.

| # | subsection | original ledger | profile (confirm by para_id) | rewritten | gated | advisor | RATIFIED | diff file | commit |
|---|---|---|---|---|---|---|---|---|---|
| 1 | abstract | `section_abstract` | `abstract` (9 props) | ✅ v2 | ✅ | ✅ | ✅ Sina 2026-06-24 | `_PHASE2_diff_abstract.md` | `5a073b4b` |
| 2 | 1 — intro | `section1` | `intro` | ☐ | ☐ | ☐ | ☐ | — | — |
| 3 | 2.1 | `section2.1` | `lit_review` / `hypotheses` | ☐ | ☐ | ☐ | ☐ | — | — |
| 4 | 2.2 | `section2.2` | `hypotheses` | ☐ | ☐ | ☐ | ☐ | — | — |
| 5 | 2.3 | `section2.3` | `lit_review` / `hypotheses` | ☐ | ☐ | ☐ | ☐ | — | — |
| 6 | 2.4 | `section2.4` | `lit_review` / `hypotheses` | ☐ | ☐ | ☐ | ☐ | — | — |
| 7 | 2.5 | `section2.5` | `lit_review` / `hypotheses` | ☐ | ☐ | ☐ | ☐ | — | — |
| 8 | 3.1 | `section3.1` | `data` | ☐ | ☐ | ☐ | ☐ | — | — |
| 9 | 3.2 | `section3.2` | `results` / `methods` | ☐ | ☐ | ☐ | ☐ | — | — |
| 10 | 3.3 | `section3.3` | `results` / `methods` | ☐ | ☐ | ☐ | ☐ | — | — |
| 11 | 3.4 | `section3.4` | `results` / `methods` | ☐ | ☐ | ☐ | ☐ | — | — |
| 12 | 4.1 | `section4.1` | `results` | ☐ | ☐ | ☐ | ☐ | — | — |
| 13 | 4.2 | `section4.2` | `results` | ☐ | ☐ | ☐ | ☐ | — | — |
| 14 | 4.3 | `section4.3` | `results` | ☐ | ☐ | ☐ | ☐ | — | — |
| 15 | 4.4 | `section4.4` | `results` | ☐ | ☐ | ☐ | ☐ | — | — |
| 16 | 5 — conclusion | `section5` | `conclusion` | ☐ | ☐ | ☐ | ☐ | — | — |
| 17 | **FINAL ASSEMBLY** (terminal, after all 16 ratified) | — | — | — | — | — | ☐ | assemble 16 ratified clones → thesis draft, compile, Sina final read | — |

**RATIFIED invariant:** a row's `ratified ✅` is valid ONLY with Sina's explicit approval AND a commit SHA in that row (commit happens right after ratify). `ratified ✅` with commit `—` = INVALID → treat as not-ratified, re-confirm with Sina.

**NEXT ACTION:** on Sina's "go" → run the abstract (row 1). Note: `_PHASE2_diff_abstract.md` holds a PRE-GO draft (jargon-stripped, superseded) — the fresh cycle OVERWRITES it; do not present it as a head-start.

## NEXT (NOT started) — AUTOMATE via an opus-agent HARNESS. Design carefully; run NOTHING until airtight.
> **Design state lives in `_PHASE2_HARNESS_DESIGN.md`** (principles decided; structure = CANDIDATE). Brainstorm PAUSED 2026-06-24 — Sina said "change approach completely" (scope unspecified). Resume there next session (Opus 4.8, max effort): re-decide approach with Sina, then spec it. Studied the proven Phase-1 harness `style_phase1_master.js`.

Constraints (Sina 2026-06-24, after manually ratifying the abstract):
- Manual per-subsection is too costly (reading 16× by hand is unsustainable). Automate the rewrite.
- **NO script as the MEANING checker.** The string / claim-word check FALSE-PASSED both abstract fouls (v1 synonym swaps + v2 hedge) → it overfits to "word present" and misses meaning. Keep the claim-word list ONLY as an INPUT to the red team — never a pass/fail gate.
- **MEANING authority = a RED-TEAM LAYER:** N independent opus agents each compare NEW prose ↔ the propositions for fidelity (foul-classes: polarity/negation · direction · hedge strength · clause re-attachment · added causation/transmission · scope/quantifier · entity swap); synthesize; ANY foul → fix. (= the proven Phase-1 panel→redteam pattern, re-aimed at meaning, not style.)
- Sina reviews only the FINAL output, not each paragraph.
- Still load-bearing: spine frozen (originals untouched), clones are the write target, keep jargon, propositions beat old prose on conflict.

## SCAFFOLD INVENTORY (what exists, committed)
- 16 clones + `_README.md` + `_clone_clean_ledgers.py` in `_rewrite_working/`.
- `_PHASE2_PLAN.md` (design, reconciled), this ledger, `_PHASE2_diff_abstract.md` (pre-go draft).
- 16 originals FROZEN (verified byte-identical after cloning).
