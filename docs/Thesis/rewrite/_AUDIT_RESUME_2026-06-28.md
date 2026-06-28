# FINAL AUDIT -- RESUME (2026-06-28, mid-flight at compaction)

## STATE
Final referee-proof audit of the submission-ready thesis is RUNNING. Design = 1 panel x 7 opus referees,
each reads ONLY one self-contained flat file and writes its OWN findings file GRADUALLY (1 JSONL line per
finding via `cat >> file <<'J'`), identify-only, NEVER fix. Merge is programmatic.

- 5/7 DONE (durable on disk, committed): numbers, honesty, coherence, citations, style.
- 2/7 RE-RUNNING: methodology + completeness. They stalled mid-stream on opus-MAX (150k-tok long streams);
  re-running on opus + HIGH effort via the dedicated script `audit_rerun.js` (task wuw6g5fnw / run
  wf_c9aac417-d39). A 5-min health-check wakeup is armed to merge when they land.

## HOW TO FINISH (post-compaction)
0. If neither a task-notification nor the wakeup fired, PROACTIVELY check task wuw6g5fnw + the report dir.
1. The MOMENT methodology_A.jsonl + completeness_A.jsonl land, `git add` + COMMIT them immediately, before
   anything else (~340k tokens; uncommitted = LOST on the next compaction). Confirm both exist in
   `_phase5_harness/_audit_reports/`. If they FAILED AGAIN (stalled): re-run on effort 'medium' (edit audit_rerun.js).
2. `cd _phase5_harness && python _audit/merge_jsonl.py`  -> writes `_AUDIT_REPORT.{json,md}` (all 7).
3. ADJUDICATE each finding YOURSELF against the flat file `_uottawa_rewrite/_thesis_AUDIT.tex`. The merged
   JSON LOOKS authoritative but is NOT -- re-derive every number from its actual table cell and every claim
   from its sentence; do NOT rubber-stamp (this session caught real errors only by re-deriving). Accept/reject
   each with evidence; the advisor MUST see your accept/reject calls, not a cleaned summary. NEVER auto-apply a fix.
4. Present the vetted fix-plan to Sina. Fixes (if approved) go via the generator transforms like Issues 1-3,
   then RE-RUN Layer-0 + re-audit touched sections (applying fixes re-opens the audit).

## FINDINGS SO FAR (5/7 -- NOT an all-clear)
0 high-severity ON THE 5 DONE, ~79 findings. But methodology + completeness -- the 2 dimensions that most
often raise FATAL examiner objections -- are STILL PENDING; methodology's failed partial already floated
"claim stronger than design supports" and "construct-validity vs central interpretation". Do not call the
thesis clean until those two land and are adjudicated.
- numbers: ALL 21 tables' cited cells, economic effects, bin drops, Wald=beta_c-beta_s RECONCILE. Only med:
  one prose line mislabels Table 5.2's two-tailed note as "one-tailed" reporting convention.
- honesty: a causal verb slipped into a gloss ("the reason for the deal RAISES uncertainty"); "Ruling Out"/
  "we rule it out" overclaims a null. (floor breaches to soften.)
- coherence: FirmMat & EarnVol used in tables but DEFINED NOWHERE (note claims all vars defined); scrutiny
  rule-out tests the volume measure while naming incidence as the confound. abstract<->body<->concl sound.
- citations: "Dzielinski" spelling inconsistent (Table 5.21); References list not alphabetical; +24
  external-attribution checklist items (verify vs source papers -- the named residual); FF12/Nickell uncited.
- style: $p=0.0074$ vs $p=.0074$ (leading-zero); spaced "--" vs unspaced "---" dashes; UncR/UncRes abbrev drift.
- methodology (from the FAILED max run, partial, will be replaced): bid-ask Table 5.12 set portrait at
  scriptsize -> ~3-4pt unreadable (the PDF-layout risk); winsorization undocumented; generated-regressand
  (Pagan) SE correction named-not-run; "readable signal" vs near-zero forward fit.

## HARNESS FILES (all in `_phase5_harness/`)
- audit_workflow.js (full 7-referee panel) | audit_rerun.js (the 2-only rerun, hardcoded -- args.only filter
  on Workflow SILENTLY FAILED, do NOT rely on args for subsets) | _audit/merge_jsonl.py (merge the *.jsonl)
- _audit/number_audit.py (Layer-0 deterministic: provenance to the cited table + recompute derived %; clean)
- _audit/floor_inventory.py (floor-element counts) | _uottawa_rewrite/_thesis_AUDIT.tex (the ONE file agents
  read = flat thesis + audit-aids header; rebuild via _audit/build_audit_input.py after `flatten.py`)
- _FINAL_AUDIT_HARNESS_DESIGN.md (the design + the advisor-hardened additions)

## GOTCHAS (cost real time this session)
- opus-MAX stalls mid-stream on broad dimensions (150k tok) -> use HIGH for those.
- Workflow `agentType:'Explore'` = haiku-default AND "doesn't audit" -> use the DEFAULT workflow agent.
- Workflow `args.only` did not reach the script -> for subsets, write a dedicated hardcoded script.
- Each agent must write its own file GRADUALLY (append per finding) -> avoids the max_tokens that killed the
  first 2 runs.

## THESIS STATE (the audited artifact)
Issues 1-3 DONE + committed (stars->compact p; table notes + DWZ bold; de-hedge). Canonical PDF =
`_uottawa_rewrite/thesis_draft_uottawa.pdf` (70pp, 0/0). Originals untouched. Commits: c084ed52, 3d3bc11e,
a8bf95a8, c5ba1c68. Generator = `build_uottawa_rewrite.py` (single source of truth).
