# RESUME — Proposition-Redesign Harness (canonical Phase 3)   2026-06-26

> SINGLE ENTRY POINT. Last handoff failed: it carried the CONTENT but not the HARNESS-BUILD references → the harness session had no idea HOW to build, wasted ~1h, failed. This fixes that: read BOTH halves (A = how, B = what). Treat all memory as UNVERIFIED; the files are truth.

## READ ON RESUME — in this order
**0. THE HARNESS DESIGN BRIEF — richest single doc, read FIRST:** `F1D-phase3\docs\Thesis\rewrite\_PHASE4_FORK_PROMPT_1.md`. AUTHORITATIVE on the harness DESIGN: the locked agent topology (PANEL-1 propose ×3 → PANEL-2 scrutinize+fix ×3 → RED-TEAM synthesize ×1), the data-model two-levels warning, the 5 traps, the open design Qs. **Its §5 OVERRIDES my handoff/modspec:** Panel-1 *decides* what+how to change (NOT fed a recipe); `_PHASE4_S2_MODSPEC.md` + `tmp\apply_s2_1_mods.py` = **validation ORACLE for §2.1 only**, NEVER a Panel-1 input. So below, A = harness mechanics, B = content/oracle — the *design* is the fork-prompt's.

**A. HARNESS HOW-TO (already written — DO NOT rewrite, just follow):**
1. `F1D\docs\Thesis\rewrite\_phase2_v2\HARNESS_DESIGN_LESSONS.md` — read **FULL**. 9 battle-scar lessons. §1–5 = extraction-pattern; **§6–9 UNIVERSAL** (Workflow gotchas, input integrity, process, collab).
2. `F1D\docs\Thesis\rewrite\_phase2_v2\_RESUME_AFTER_COMPACTION.md` — Phase-2 status + the proven reference-impl paths.
3. Reference harness to copy: `F1D\docs\Thesis\rewrite\style_phase2_v2_principles.js` (+ `_phase2_v2\{build_v2,prep_all,finalize_v2}.py`, `_phase2_v2\_run\phase2_v2_<type>.js`).

**B. THE CONTENT TO REDESIGN (my work this session — all in the FORK):**
4. `F1D-phase3\docs\Thesis\rewrite\_PHASE4_HARNESS_HANDOFF.md` — **AUTHORITATIVE on content**: decision, honesty floor, cite stack, the §2 mod-set + the 2 advisor fixes, done/pending, isolation. (Filename says "phase4" — misnomer; see naming reconcile below.)
5. `_PHASE3_CONCLUSION.md` (EVIDENCE DOSSIER §C = the locked cite stack) · `tmp\nlm_masking_cites.json` (NLM-verified S-V + Louis, verbatim) · `NLM_QUERY_GUIDE.md` (any NEW cite goes through this) · `section2_roadmap.md` (§2 per-subsection mandates).
6. Originals to redesign (PRISTINE — edit CLONES only): `section2.{1,2,3,4,5}_paragraph_ledger.json`. Chain tooling: `tmp\extract_spine.py` (strip NLM-evidence noise → compact chain), `tmp\dump_props.py` (verbatim prop dump), `tmp\apply_s2_1_mods.py` (§2.1 reference application — encodes both fixes; path points to the DELETED clone, repoint before running).

## THE TASK (one sentence)
Build a **proposition-redesign harness** (canonical Phase-3 execution tool; sibling of the Phase-2 principles harness) that applies the masking mods to the §2 proposition chains **verifiably**, instead of by hand (manual = too slow → why the fork is being concluded).

- **Shape is DIFFERENT from Phase-2's extraction harness — this is rewrite/transform.** Per LESSONS §8: re-judge §1–5, but §6–9 apply unchanged. Likely shape: PROPOSE mods (panel, heavily-paraphrased, NO examples) → adversarial VERIFY (red-team) → deterministic APPLY to clone.
- **The VERIFY gates = the honesty floor (handoff §3), made mechanical/red-team:** no-"stock-suppressed" · attenuation-correct (stock smaller/noisier, never below baseline) · cite-as-earnings/valuation-NOT-tone · register-locks intact · logic end-to-end · exhaustiveness (no missed `placebo`/why-cash site).
- Design the harness, advisor-vet it BEFORE the expensive run, validate on ONE hard subsection (§2.1 or §2.2 — they carry the real re-derivation), READ its full output, THEN release the rest.

## NAMING RECONCILE (a real source of confusion — fix it)
Canonical 5-phase map (phase-2 resume): 1 style ✅ · 2 principles-harness ✅ · **3 propositions-redesign ⏸ ← ALL my work** · 4 rewrite-harness · 5 audit-harness. My files named `_PHASE3_*` (analysis) + `_PHASE4_*` (redesign) are **all canonical Phase 3**. The `_PHASE4_` prefix is a misnomer; do not read it as the canonical "Phase 4 rewrite harness."

## DONE / PENDING
- DONE → see handoff §7: cite hunt→NLM-verify→LOCK (S-V + Louis + thewissen); §2 ALL 5 subsections read; mod-set written + advisor-vetted (2 fixes); §2.1 applied to a clone then clone DELETED (recoverable via `apply_s2_1_mods.py`).
- PENDING → see handoff §8: BUILD the harness; apply masking mods to §2.1/2.2/2.4 clones; then downstream §1 intro/abstract/§3.1–3.4/§5 (**§3 = ~60 placebo hits in RESULTS prose, NOT a mechanical mirror — suppression can sneak in**); rewrite blocked `final_prose`; retire originals only when 100% safe; +2 `\bibitem` (S-V, Louis).

## TREES / GIT (the cross-tree split that helped sink the last run)
| | tree | branch | holds |
|---|---|---|---|
| Phase-2 harness infra | `…\F1D` | `debug/campello-did-supervisor-interrogation` | lessons, reference impl, source banks |
| My Phase-3 content | `…\F1D-phase3` (worktree) | `phase3/propositions` (HEAD `00e78b5e`) | masking decision, cite stack, mod-set, handoff, tooling |
⚠ **Harness HOW and content WHAT are on DIFFERENT branches/trees.** Both on disk. **RECOMMENDED first resume step (needs Sina's OK): merge `phase3/propositions` → `debug/campello…` so the harness can read everything in one tree (`F1D`).** Until merged, the harness (run from F1D cwd) cannot see the fork's `_phase4_s2_clone`-style edits unless pointed at `…\F1D-phase3\…`. Data + `f1d` pkg live ONLY in F1D → any compute runs from F1D.

## NON-NEGOTIABLES
→ LESSONS §9 + handoff §10. In one line: ultra-terse · literal obedience · TIME=budget (smoke before any real run; minimize runs) · **NO examples in agent prompts** · validate ONE hard unit + READ its `.output` before firing all · **NO external audit/grading scripts** (a `.js` harness ≠ an audit script) · NLM = sole paper authority · read `.tex` not summary JSONs · edit CLONES only, originals pristine · advisor-vet before the expensive run AND before declaring done.

## WHY THE LAST HANDOFF FAILED (so it never repeats)
`_PHASE4_HARNESS_HANDOFF.md` was complete on CONTENT but **never pointed at `HARNESS_DESIGN_LESSONS.md` / the reference impl**, and never reconciled the naming or the cross-tree split. The harness session had the WHAT but not the HOW. This resume exists to bind both. Always hand off BOTH halves.
