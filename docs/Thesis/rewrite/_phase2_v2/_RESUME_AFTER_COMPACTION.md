# Resume After Compaction — single source of truth

## FIRST ACTION on resume
1. Read `docs/Thesis/rewrite/_phase2_v2/HARNESS_DESIGN_LESSONS.md` **in full** (the next session is another harness design).
2. Then wait for the user to specify the new harness's task. Do NOT auto-start anything.

## WHERE WE ARE — Phase 2 (v2) is DONE ✅
Redone from scratch this session (the user did not trust the old Phase-2). Approach: extract **writing-STYLE principles per section-type DIRECTLY from the corp-fin exemplar papers** (never our thesis prose).

- **Deliverable:** 8 rulebooks, **62 principles** in `docs/papers/style_exemplars/_rulebooks_v2/`
  - abstract 8 · intro 9 · lit_review 8 · hypotheses 7 · data 9 · methods 7 · results 7 · conclusion 7
  - Each principle = `{device, principle, why, evidence:[{paper, para_idx, quote}]}`; every quote verbatim, ≥2 distinct papers.
- **Sanity pass: PASS** — all real style devices, evidence supports each, no content-as-style, no vague rules, no fabricated thresholds, red-team scrutiny fired (rejected coarse rules in intro + results).
- **Known blind spot** (harness self-flagged in every type): macro/paragraph structure, sentence rhythm, active-vs-passive tension were not examined.
- **By design (not a bug):** ~4 universal devices recur across types (first-person voice, signposting/enumeration, hedging, concede-then-refute) — cross-type dedup is FORBIDDEN, so they correctly repeat.

## ARTIFACTS
- Harness (proven v2): `docs/Thesis/rewrite/style_phase2_v2_principles.js`
- Build/embed: `_phase2_v2/build_v2.py` · prep-all-types: `prep_all.py` · materialize: `finalize_v2.py`
- Runnable embeds: `_phase2_v2/_run/phase2_v2_<type>.js`
- Source paper bank (WE pre-extracted): `docs/papers/style_exemplars/bundles/<type>.json` (`exemplars[]`) + `.../extracted/<paper>.json`
- Lessons: `_phase2_v2/HARNESS_DESIGN_LESSONS.md`

## GIT
- Branch: `debug/campello-did-supervisor-interrogation`
- Phase-2-v2 deliverable commit: `3a833a13`
- Pre-existing unrelated uncommitted file: `docs/Thesis/rob_ALL.pdf` (NOT ours — leave it).

## 5-PHASE REWRITE MAP (context)
1 style analysis ✅ · 2 principles harness ✅ (this, v2) · 3 propositions redesign ⏸ · 4 rewrite harness ⏸ · 5 audit harness ⏸.
(Next session = a NEW harness design the user will describe — may or may not be one of these phases.)

## NON-NEGOTIABLE CONSTRAINTS (carry into next session)
- Ultra-terse replies. Literal obedience. TIME is the budget — minimize runs; smoke before any real run.
- NO examples in agent prompts (anchors/kills neurodiversity). NO external audit/grading scripts (`.js` harness ≠ audit script).
- Validate ONE hard unit + READ its full `.output` before firing all units.
