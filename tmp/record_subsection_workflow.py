# Record the WORKFLOW CHANGE: write/show/approve/record unit = WHOLE SUBSECTION (was paragraph).
# Advisor-vetted; review = chat prose + compile-at-END; .tex push stays batched. Fail-closed asserts.
import json
r = "docs/Thesis/rewrite/_RESUME_STATE.json"
d = json.load(open(r, encoding="utf-8"))

assert "subsection_loop_workflow_2026_06_13" not in d, "already recorded (idempotency)"
assert d["hard_rules"][1].startswith("ONE PARAGRAPH AT A TIME"), d["hard_rules"][1]
assert "advisor-check the §2.2 P3" in d["NEXT_ACTION"]
assert d["prose_progress_2026_06_13"]["_workflow_LEDGER_FIRST"].startswith("Draft each paragraph")

d["updated"] = ("2026-06-13 (PROSE PHASE -- SUBSECTION-LOOP: write/show/approve/record a whole subsection at a time; "
    ".tex push batched at end; building 2.2)")

d["where_we_are"] = ("[2026-06-13] §2 rewrite, PROSE PHASE. WORKFLOW CHANGE: the unit is now a WHOLE SUBSECTION "
    "(write/show/approve/record), advisor-vetted; .tex push batched at END; review = chat prose, compile-at-end (user "
    "choice). See subsection_loop_workflow_2026_06_13. All four plans RATIFIED. 2.2 P1+P2 recorded, P3 drafted (its "
    "advisor-check folds into 2.2's subsection advisor pass). CURRENT: building SUBSECTION 2.2 as one unit (draft P4+P5, "
    "then advisor on the whole 2.2, then show you). thesis_draft.tex still 2.1-only.")

d["hard_rules"][1] = ("UNIT = WHOLE SUBSECTION for write/show/approve/record (user 2026-06-13; SUPERSEDES the earlier "
    "'one paragraph at a time'). Per-paragraph RIGOR is preserved INSIDE the loop: each paragraph still honors its own "
    "propositions/guardrails/boundary and gets the overclaim scan. See subsection_loop_workflow_2026_06_13.")

d["subsection_loop_workflow_2026_06_13"] = {
  "_what": ("WORKFLOW CHANGE (user 2026-06-13): the WRITE/READ/APPROVE/RECORD unit is now a WHOLE SUBSECTION, not a "
    "paragraph. Advisor-vetted. Per-paragraph RIGOR preserved INSIDE; only the show/approve granularity changed."),
  "review_decision": ("Chat prose, compile at END (user choice). Show each subsection as prose IN CHAT; user approves; "
    "record to ledgers. The .tex push + PDF compile happens ONCE at the very end -- keeps the standing 'do not push .tex yet'."),
  "loop_per_subsection": [
    "A VERIFY (the safety gate -- where 'accurate' lives): resolve ALL the subsection's WRITE_TIME_FLAGS -- NLM-verify each NEW cite OR take its PRE-SET fallback (NEVER improvise prose around an unverified cite); bible cross-check EVERY number vs _tables_from_bible.tex (Catch-3 procedure); confirm callbacks land. Gate: all green or pre-set fallback taken.",
    "B DRAFT every paragraph to the thin-claim ceiling, honoring each P's intent/boundary/guardrails. Apply the WORDING-rule flags HERE (e.g. 2.5 P4.2 'tracks cash' not bald 'valid'; 'rises ahead of' not 'around').",
    "C SELF-SCAN per-paragraph: overclaim (motive/intent/intensity words unbacked) + boundary (no reaching) + uncited-connective accuracy.",
    "D ADVISOR on the full drafted subsection: per-paragraph overclaim + accuracy + cross-paragraph coherence/seams. Fix all.",
    "E SHOW the whole subsection to the user (chat prose); user approves (or asks changes -> loop D/E).",
    "F RECORD each paragraph's final_prose programmatically (set prose_status + gates); commit. NO .tex push."
  ],
  "order": ("Finish 2.2 (whole P1-P5; folds the parked P3 advisor-check into 2.2 Phase D) -> 2.3 -> 2.4 -> 2.5 -> FINAL "
    "whole-§2 advisor + the single .tex push/compile."),
  "phase_A_owed_by_subsection": {
    "2.2": "NONE -- all cites are CALLBACKS (thewissen P6 / harford P5 / matsumoto P2, verified in 2.1) + NO numbers (predictions only). Phase A already GREEN from this session's audit -> straight to draft.",
    "2.3": "pagan1984 (NLM-verify or fallback); DWZ-isolation span provisional -> bare-hedge fallback; eq-2/eq-4 already Catch-3-closed.",
    "2.4": "opler1999/bates2009/petersen2009/cameron2011 (NLM-verify or drop); equations transcribed from file:line; C1/C2/C6 framing only.",
    "2.5": "hoberg2010+'fluidity' (verify or DROP -- our var = hoberg2016 total similarity); Hassan cite-year; BIBLE cross-check C3/C4/C5 numbers; davis2016 provisional fold-as-is; variable_ledger L188 'persistent'."
  },
  "first_tex_push_baggage": ("At the END push: carries subsection scaffolding (\\subsection{} headers) + the 2.1-P7 "
    "softening that rides along (cut 'and we do not try'; KEEP 'Our design cannot distinguish them.'; remove the P7 TODO "
    "comment) + any new \\bibitem from verified cites. Seed in tmp/write_2_2_p1.py (NOT run). Compile = pdflatex x2, manual \\thebibliography.")
}

d["NEXT_ACTION"] = ("=== SUBSECTION-LOOP (user 2026-06-13): write/show/approve/record a WHOLE SUBSECTION at a time; .tex "
    "push BATCHED at the very end (see subsection_loop_workflow_2026_06_13). === IMMEDIATE: SUBSECTION 2.2. Phase A is "
    "GREEN (all callbacks, no numbers). Phase B: draft P4 (H1b two-clocks) + P5 (scrutiny FLAG) -- P1/P2 already recorded, "
    "P3 drafted (prose_progress_2026_06_13.P3_draft_pending_advisor). Assemble full P1-P5 -> C self-scan (overclaim) -> D "
    "advisor on the WHOLE 2.2 (ABSORBS the parked P3 check) -> E show user the whole 2.2 -> F record all + commit. THEN "
    "2.3 -> 2.4 -> 2.5 (each: Phase A verify its owed cites/numbers FIRST per phase_A_owed_by_subsection). After 2.5 "
    "recorded -> FINAL whole-§2 advisor + the single .tex push/compile (+2.1-P7 softening). DISCIPLINE: NLM sole paper "
    "authority; numbers bible-verbatim; PRE-SET fallback if a cite fails; programmatic transfer; SHOW-first; per-paragraph "
    "overclaim scan; ignore mempalace auto-recall.")

d["prose_progress_2026_06_13"]["_workflow_LEDGER_FIRST"] = ("LEDGER-FIRST + SUBSECTION-UNIT (updated 2026-06-13): draft a "
    "whole subsection's paragraphs into their section2.X ledger final_prose; the unit of SHOW/APPROVE is the SUBSECTION "
    "(see subsection_loop_workflow_2026_06_13), not a paragraph. Per-subsection rhythm: Phase A verify -> draft all "
    "paragraphs -> self-scan -> advisor on the whole subsection -> SHOW the whole subsection -> RECORD all programmatically "
    "+ commit. .tex push BATCHED at the very end.")

d["prose_progress_2026_06_13"]["status"]["2.2 P3 (H1a concentration)"] = ("DRAFTED (prose_progress.P3_draft_pending_advisor); "
    "its advisor-check now FOLDS into 2.2's subsection Phase-D advisor pass (no separate round).")
d["prose_progress_2026_06_13"]["status"]["2.2 P4 (H1b two-clocks) + P5 (scrutiny FLAG)"] = "to draft in 2.2 Phase B (this is the immediate work)."

open(r, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
json.load(open(r, encoding="utf-8"))
assert "subsection_loop_workflow_2026_06_13" in json.load(open(r, encoding="utf-8"))
print("resume updated: SUBSECTION-LOOP workflow recorded; P3 draft + all history preserved.")
