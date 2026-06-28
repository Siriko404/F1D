# ⛳ PHASE-5 PROSE HARNESS — SPAWN RESUME (next-session entry point) 2026-06-28

## THE ONE NEXT ACTION: SPAWN THE HARNESS
The harness is BUILT · gate-tested 11/11 · advisor-signed-off. Nothing else is built first.
Sina has OPTED IN to multi-agent orchestration (he designed + ratified this harness; the run is authorized).

### Exact spawn steps
```
1. REBUILD (regenerates harness.mjs from sources; must print "wrap-check passed"):
   python docs/Thesis/rewrite/_phase5_harness/build_harness.py
2. SPAWN via the Workflow tool. harness.mjs is ~935 KB > the 524 KB `script` limit -> MUST use scriptPath:
   Workflow({ scriptPath: "C:\\...\\F1D-phase3\\docs\\Thesis\\rewrite\\_phase5_harness\\harness.mjs" })
     - no args  -> runs all 17 sections
     - args:{only:["section4.5"]} -> runs just that section (use to re-run any BLOCKED section)
   Runs in background (~1 hr); you get a completion notification. READ the full returned object (lessons Sec.8).
3. SAVE the Workflow's returned object to:  _phase5_harness/harness_result.json
4. python docs/Thesis/rewrite/_phase5_harness/finalize.py
     -> writes ONE json per section into _phase5_harness/output/ (the diligent trail: drafts+audits+final);
        prints N OK / N BLOCKED. Re-run BLOCKED sections via args.only, then finalize again.
5. python docs/Thesis/rewrite/_phase5_harness/finalize.py --place
     -> splices each OK section's final_prose into its _final/<section>_paragraph_ledger.json
```

## ARCHITECTURE (Sina's final design — do NOT re-litigate)
```
WRITE     3 thematic teams, PARALLEL, per section (the ONLY place sections are separate)
            T1=Sec.2.1-2.5 · T2=Sec.3.1-3.4+4.1-4.5 · T3=abstract+Sec.1+Sec.5
            per section: 3 paraphrased writers -> GATE -> 1 editor merges -> GATE
  -- BARRIER (all prose written first) --
RED-TEAM  3 agents read the WHOLE thesis -> flags (adversarial, propose-only)
AUDIT     honesty x3 (with verbatim source quotes) + 5 lanes (numbers/rulebook/citation/flow/completeness),
            each reads the WHOLE thesis. 2 SEQUENTIAL panels (stagger spawns -> no rate-limit ban).
BOSS      reads WHOLE thesis + ALL reports -> writes the FINAL, SECTION BY SECTION (step by step,
            edits each section's current draft by minimal edit). GATE per paragraph on every output.
```
Every post-write agent sees the entire thesis (Opus 1M ctx). Only the boss TYPES one section at a time.
Agents are schema-forced (deliver JSON, never free text); they RETURN data, the harness writes files
(no two agents touch one file). Each section -> its own output/ json.

## THE GATES (the deterministic spine — gates.mjs, 11/11)
number-trace (SECTION-level set; back-references pass; a rounded figure FLAGS not blocks; extra-stars BLOCKS;
foreign number BLOCKS) · honesty-FORBID (suppress/dampen/detect/strict-specificity/...) · cite-whitelist
(full 22-key bib set; mis-cite caught by the audit lane) · bijection (every prop rendered) · LaTeX-lint.
Run BETWEEN every layer; a blocked paragraph cannot move forward. `node gates.test.mjs` -> 11/11.

## FILES (all committed; harness.mjs + _wrapcheck.cjs + output/ + harness_result.json are gitignored build/run artifacts)
- gates.mjs (+ gates.test.mjs 11/11)         — the spine
- pack_briefs.py -> briefs.json              — per-section briefs (props+rulebook+locks+closed number/cite sets)
- harness.template.mjs + build_harness.py -> harness.mjs   — the workflow (ASCII-sanitized, wrap-checked)
- finalize.py                                — materialize per-section json + --place into ledgers

## PRE-RUN FACTS (verified this session — do NOT redo)
- 16/16 sections number-verified vs source (verify_45_claims.py 69/69 §4.5; verify_all_sections.py 0 real errors for the rest).
- theory verbatim NLM quotes RE-ATTACHED to §2.1/§2.2 (21 props) — honesty audit checks claims against them.
- 11 missing bibitems supplemented (docs/Thesis/_bibitems_supplement.tex; 2 stubbed "SINA VERIFY": ragozzino2024, thewissen2024).
- plumbing proven: thesis_draft.tex compiles to a 23-page PDF; a stub Sec.4.5 + its 2 new cites compile.

## POST-RUN PIPELINE — NOT YET BUILT (build after the prose run succeeds)
1. ASSEMBLER: generalize push_2_1_to_tex.py -> push all ledgers' final_prose into body tex -> master
   thesis_draft(_uottawa).tex \inputs them + tables + bib -> pdflatex -> PDF. (push_2_1 is the template; compile proven.)
2. HONESTY DIGEST: extract the ~12-15 load-bearing sentences (register-locked props + honesty-audit-flagged) into one
   short list for the 5-minute human skim.

## THE HUMAN BACKSTOP (non-negotiable, before SUBMISSION not before the run)
The run produces an audited DRAFT, not a hands-off thesis. A smooth causal sentence built from ALLOWED words can pass
every gate + slip the 3 honesty auditors. The ONLY 100% catch = Sina reads the ~15 load-bearing sentences before
submitting. "drafted != shipped." Do not submit without it.

## RESIDUALS (advisor said ACCEPT, do NOT build a 4th pass)
- cross-section fix-consistency: the boss sees other sections' WRITER drafts, not their bossed versions -> a global
  rename could be applied slightly differently. The red-team/audit state the exact fix to keep them aligned. Caught by the skim.
- semantic honesty: the irreducible residual above.

## DECISIONS (defaulted; Sina can veto anytime)
BIMODAL GO (agents write ALL prose) · L4 bounded single-fix + flag residual · §2.3-2.5 -> methods rulebook ·
§4.5 prose written as part of the run (its chain was 69/69-verified) · honesty skim pre-submission.

## RATE-LIMIT DESIGN (don't re-worry)
3 teams (peak ~9 writers) · audit in 2 sequential panels · boss sequential (one section at a time). Peak well under
the 16 concurrency cap. The engine has NO sleep/timer (Date.now throws) — staggering is done by sequential awaits.

Broader thesis state (the 17 _final ledgers, the audit) is in _AUDIT_RESUME_2026-06-27.md and
_ROBUSTNESS_45_RESUME_2026-06-28.md. The harness design rationale is in _PHASE5_PROSE_HARNESS_DESIGN_PROPOSAL.md.
