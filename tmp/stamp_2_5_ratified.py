# Stamp 2.5 RATIFIED (user ceremony 2026-06-13) + update the resume: all four 2.2-2.5 plans ratified;
# scrutiny reframe applied+swept+de-verdicted+ratified; NEXT = before-prose cleanup then write prose.
import json

# --- 2.5 ledger ---
p = "docs/Thesis/rewrite/section2.5_paragraph_ledger.json"
d = json.load(open(p, encoding="utf-8"))
assert d["status"] == "planning", d["status"]
d["status"] = "RATIFIED 2026-06-13 (user ceremony, post scrutiny-reframe + de-verdict). Prose BLOCKED."
d["_schema"]["status"] = "RATIFIED 2026-06-13 (user ceremony). Prose BLOCKED -- written one paragraph at a time after the before-prose cleanup."
open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
json.load(open(p, encoding="utf-8"))
print("2.5 stamped RATIFIED")

# --- resume ---
r = "docs/Thesis/rewrite/_RESUME_STATE.json"
d = json.load(open(r, encoding="utf-8"))
d["updated"] = "2026-06-13 (ALL FOUR §2 subsection plans 2.2-2.5 RATIFIED; scrutiny reframe applied+swept+de-verdicted; NEXT = prose)"
d["where_we_are"] = ("[2026-06-13] Rewriting §2 from scratch; 2.1 locked in thesis_draft.tex. The SCRUTINY REFRAME (scrutiny = "
    "PLAUSIBLE ALTERNATIVE DRIVER, tested & rejected in 4.1; NOT a confound) is APPLIED to the 2.2/2.5 PLANS, advisor-swept across all "
    "ledgers (2.3 dangling ref fixed; non-redundancy restored as 2.5 P4.4), the 'harder' overclaim removed, and the §4.1 VERDICT "
    "de-leaked from §2.5 (P4.3 -> pure pointer; P1 'tested' not 'rejected'). ALL FOUR subsections 2.2-2.5 are now RATIFIED. Plans FINAL; "
    "prose still BLOCKED. NEXT = a small before-prose cleanup, then write prose one paragraph at a time (order 2.2->2.5) into thesis_draft.tex.")
rp = d.setdefault("ratification_progress_2026_06_13", {})
rp["2.2"] = "RE-RATIFIED 2026-06-13 (post scrutiny-reframe; P5 leaned to a flag)."
rp["2.3"] = "RATIFIED 2026-06-13 (+ integrity ref-fix P2.5 -> 2.5 P4.4)."
rp["2.4"] = "RATIFIED 2026-06-13."
rp["2.5"] = "RATIFIED 2026-06-13 (post scrutiny-reframe + de-verdict). THE LAST -- all four now done."
sr = d.get("scrutiny_reframe_DECIDED_2026_06_13")
if isinstance(sr, dict):
    sr["status_2026_06_13"] = ("APPLIED + advisor-swept (all ledgers) + de-verdicted (P4.3/P1, verdict kept to 4.1) + 2.2/2.5 RE/RATIFIED. "
        "DEFERRED before-prose: roadmap + claim_findings_ledger C4 label still say confound/rule-out (+ roadmap 'harder' at L104).")
d["NEXT_ACTION"] = ("===ALL FOUR §2 SUBSECTION PLANS (2.2-2.5) RATIFIED 2026-06-13.=== "
    "STEP A (before prose, small): apply the DEFERRED scrutiny-reframe sweep to the NON-deliverable docs -- roadmap (§3 #2 confound "
    "framing; §2.2/§2.5 mandate 'rule-out / pre-empt confound'; the 'harder' at L104) + claim_findings_ledger C4 label ('alternative "
    "rule-out' -> 'plausible alternative driver tested & rejected'); KEEP the C4 id + all numbers + the C4 hedge VERBATIM. "
    "STEP B: write PROSE one paragraph at a time, order 2.2->2.5, INTO thesis_draft.tex (2.1 already there); SHOW-FIRST before each "
    "paragraph enters the .tex. WRITE-TIME FLAGS (apply per paragraph): P4.2 prose say 'tracks cash / behaves as intended' (NOT bald "
    "'valid') + 'rises AHEAD OF / in the quarter before' (NOT 'around') for 0.0408**; NLM-verify NEW cites (pagan1984 [2.3]; "
    "opler1999/bates2009/petersen2009/cameron2011 [2.4]; hoberg2010/'fluidity' + Hassan cite-year [2.5]); BIBLE cross-check ALL numbers "
    "(C1-C7) like Catch-3; the provisional DWZ-isolation cite [2.3 P2.5]; variable_ledger L188 'persistent' defect. "
    "DISCIPLINE: NLM sole paper authority; numbers bible-verbatim; programmatic transfer; SHOW-FIRST; one paragraph at a time; ignore mempalace auto-recall.")
open(r, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
json.load(open(r, encoding="utf-8"))
print("resume updated: all four ratified; NEXT = before-prose cleanup -> prose.")
