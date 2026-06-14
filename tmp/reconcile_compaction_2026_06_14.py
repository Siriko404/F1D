# Bounded reconcile (advisor): stamp the few LIVE-STALE status fields the field-named sweep missed,
# so no post-compaction reader hits a status contradicting "everything ratified + FB filled".
# JSON-level edits (load/modify/dump); fail-closed asserts; re-validate.
import json

CUR25 = ("[2026-06-14 CURRENT -- read FIRST; everything below is SUPERSEDED history] 2.5 prose RATIFIED "
         "(provisional, user 'consider everything ratified for now') + in thesis_draft.tex; competition DROPPED; "
         "FB FILLED in P2; 5 table refs added; all 11 tables wired. || ")
CUR23 = ("[2026-06-14 CURRENT -- read FIRST; everything below is SUPERSEDED history] 2.3 prose RATIFIED "
         "(provisional, user) + in thesis_draft.tex; DWZ eq (2)/(4)/(5) natbib-cited; dash-free. || ")

# ---- 2.5 ledger ----
p = "docs/Thesis/rewrite/section2.5_paragraph_ledger.json"
d = json.load(open(p, encoding="utf-8"))
a = "FB magnitude is a PLACEHOLDER"
assert a in d["_plan"]["validity_papers_status"], "2.5 validity_papers_status FB string moved"
d["_plan"]["validity_papers_status"] = d["_plan"]["validity_papers_status"].replace(
    a, "FB magnitude FILLED 2026-06-14 (1-SD -> ~5%/1.5%/2.2% of residual SD; all-universe summary stats built)")
b = "FB economic-effect = PLACEHOLDER (summary stats disregarded as wrong)"
assert b in d["_COMPETITION_DROPPED_2026_06_14"], "2.5 _COMPETITION_DROPPED FB string moved"
d["_COMPETITION_DROPPED_2026_06_14"] = d["_COMPETITION_DROPPED_2026_06_14"].replace(
    b, "FB economic-effect FILLED 2026-06-14 (all-universe summary stats built; ~5%/1.5%/2.2% of residual SD)")
if not d["next_action"].startswith("[2026-06-14 CURRENT"):
    d["next_action"] = CUR25 + d["next_action"]
open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
json.load(open(p, encoding="utf-8"))

# ---- 2.3 ledger ----
p = "docs/Thesis/rewrite/section2.3_paragraph_ledger.json"
d = json.load(open(p, encoding="utf-8"))
if "next_action" in d and not d["next_action"].startswith("[2026-06-14 CURRENT"):
    d["next_action"] = CUR23 + d["next_action"]
open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
json.load(open(p, encoding="utf-8"))

# ---- resume: reframe the two _note blocks ----
RS = "docs/Thesis/rewrite/_RESUME_STATE.json"
r = json.load(open(RS, encoding="utf-8"))
pe = r["PENDING_EDITS_unapplied"]
pe["_note"] = ("[2026-06-14] PROSE NOW WRITTEN + RATIFIED (provisional); full §2 + all 11 tables in the draft; FB FILLED. "
    "The WRITE_TIME_FLAGS below are now POST-RATIFICATION VERIFICATION OWED before final submission (NLM-verify the "
    "pagan1984 / opler1999 / bates2009 / petersen2009 / cameron2011 cites that are already in the prose + bibliography; "
    "reconcile the Hassan cite-year vs the .bib; confirm the MNPI expansion) -- these are checks, NOT blockers, and the "
    "compile already shows 0 undefined cites. " + pe["_note"])
rp = r["ratification_progress_2026_06_13"]
rp["_note"] = rp["_note"] + (" [2026-06-14] PROSE now ALSO RATIFIED (provisional, user 'consider everything ratified for "
    "now'); this block records the earlier 06-13 PLAN ratification -- see where_we_are / prose_progress for the prose, "
    "tables, refs, and FB status.")
open(RS, "w", encoding="utf-8", newline="\n").write(json.dumps(r, indent=2, ensure_ascii=False) + "\n")
json.load(open(RS, encoding="utf-8"))

print("OK: reconciled 2.5 FB-placeholder notes + 2.3/2.5 next_action stamps + resume _note blocks. JSON valid.")
