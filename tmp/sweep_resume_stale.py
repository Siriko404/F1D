# Advisor catch: the compaction script only updated forward fields; backward fields rotted again.
# Sweep EVERY stale field to current reality (reframe APPLIED + all four RATIFIED + prose underway),
# and de-dupe write-time flags (canonical = PENDING_EDITS_unapplied.WRITE_TIME_FLAGS).
import json
r = "docs/Thesis/rewrite/_RESUME_STATE.json"
d = json.load(open(r, encoding="utf-8"))

# 1) mission -- was "currently applying the reframe before any prose"
assert d["mission"].startswith("Rewrite thesis Section 2")
d["mission"] = ("Rewrite thesis Section 2 (Conceptual Framework and Empirical Strategy) paragraph-by-paragraph to a thin, "
    "referee-proof, COMPLETE claim, from scratch. 2.1 (7-paragraph framework) is LOCKED in thesis_draft.tex. The 2.2-2.5 PLANS are "
    "ALL RATIFIED (incl. the scrutiny-driver reframe, applied + swept). NOW in the PROSE phase: drafting each paragraph into its "
    "ledger's final_prose (LEDGER-FIRST; .tex push deferred). See prose_progress_2026_06_13 + NEXT_ACTION.")

# 2) PENDING_EDITS_unapplied._note -- was "scrutiny reframe is the ACTIVE unapplied work" (now false)
pe = d["PENDING_EDITS_unapplied"]
pe["_note"] = ("DONE: the yardstick-AUDIT edits (F1-F5, EDITS_APPLIED_2026_06_13) AND the SCRUTINY-DRIVER REFRAME "
    "(scrutiny_reframe_DECIDED_2026_06_13) are ALL applied + swept, and the 2.2-2.5 plans RE/RATIFIED. The ONLY remaining unapplied "
    "items are the WRITE_TIME_FLAGS below -- applied PER-PARAGRAPH at prose time. THIS is the CANONICAL write-time-flags list "
    "(prose_progress_2026_06_13.write_time_flags points here; do not duplicate).")
# add the 2 NEW overclaim tightenings from the de-verdict advisor pass (not in the old list)
pe["WRITE_TIME_FLAGS"].append(
    "2.5 P4.2 prose: say 'tracks cash / behaves as intended', NOT a bald 'valid'; and 'rises AHEAD OF / in the quarter before' "
    "(0.0408**), NOT 'around' (advisor de-verdict pass 2026-06-13).")

# 3) EDITS_APPLIED_2026_06_13._superseded_in_part -- re-ratification is done
d["EDITS_APPLIED_2026_06_13"]["_superseded_in_part"] = ("The SCRUTINY-DRIVER reframe landed ON TOP of these F1-F5 edits and is now "
    "APPLIED + advisor-swept; 2.2 + 2.5 RE-RATIFIED 2026-06-13. All done -- no further action on this block (historical record).")

# 4) ratification_progress._note -- reframe+re-ratify done
d["ratification_progress_2026_06_13"]["_note"] = ("Ratifies the LEDGER PLANS for the from-scratch 2.2-2.5 rewrite. ALL FOUR RATIFIED "
    "2026-06-13 (2.2 re-ratified after the scrutiny reframe; 2.5 the last). DONE -- now in the prose phase.")

# 5) scrutiny_reframe block -- _what (was 'NOT yet applied'), advisor_status (was 'RE-ADVISOR before re-ratify'), NLM_GATE (non-blocker)
sr = d["scrutiny_reframe_DECIDED_2026_06_13"]
sr["_what"] = ("MAJOR framing correction (user, emphatic, evidence-grounded). APPLIED + advisor-swept + 2.2/2.5 RE-RATIFIED 2026-06-13 "
    "(see status_2026_06_13). This block is the HISTORICAL record of the reframe; every change_list item below is DONE.")
sr["advisor_status"] = ("DONE -- change-list advisor-validated AND the applied reframe advisor-swept (caught + fixed: the 2.3 dangling "
    "ref -> 2.5 P4.4, the 2.5 P1 confound-leftover, and the §4.1 verdict leak in P4.3). 2.2/2.5 re-ratified.")
sr["NLM_GATE"] = ("(NICE-TO-HAVE, NOT a blocker -- the reframe is APPLIED resting on our OWN co-movements 0.7530***/0.0408**; matsumoto "
    "only refines an OPTIONAL lit anchor + the 2.1-P2 seed question.) " + sr["NLM_GATE"])

# 6) de-dupe prose_progress.write_time_flags -> pointer to the canonical list
d["prose_progress_2026_06_13"]["write_time_flags"] = ("CANONICAL list = PENDING_EDITS_unapplied.WRITE_TIME_FLAGS (single source of truth; "
    "do not duplicate here). Apply the relevant flag per-paragraph when that paragraph's prose draws on it.")

open(r, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
json.load(open(r, encoding="utf-8"))
# coherence self-check: no field should still claim the reframe is unapplied / re-ratify pending
blob = json.dumps(d)
for bad in ["ACTIVE unapplied", "NOT yet applied to any doc", "then RE-RATIFY those two", "before re-ratifying 2.2/2.5", "the reframe is the next layer"]:
    assert bad not in blob, f"STALE STILL PRESENT: {bad!r}"
print("resume swept: 6 stale/dup fields reconciled; no 'reframe unapplied / re-ratify pending' strings remain.")
