# Resume: 2.2 ratified+committed; 2.3 pushed-to-PDF (pending ratification); 2.4 in progress; pagan flag.
import json
r = "docs/Thesis/rewrite/_RESUME_STATE.json"
d = json.load(open(r, encoding="utf-8"))
pp = d["prose_progress_2026_06_13"]
pp["status"] = {
  "2.2 (whole, v2)": "RATIFIED 2026-06-13 (user, from PDF) + COMMITTED ac87c8c. In thesis_draft.tex. Hypotheses set off (informal + formal theta/kappa), dash-free.",
  "2.3 (whole)": "DRAFTED + pushed to thesis_draft.tex + compiled to PDF (6pp) for user review. NOT ratified (gate locked). eq-2/eq-4 verbatim from the verified source; dash-free; pagan held out.",
  "2.4 (whole)": "IN PROGRESS: drafting now (Phase A verify -> B draft -> C scan -> D advisor), to PARK until 2.3 is ratified.",
  "2.5 (whole)": "not drafted."
}
pp["_v2_note"] = "2.2 was rebuilt v2 (hypotheses set off + dash-free) per user 2026-06-13; the old v1 P3_draft_pending_advisor below is SUPERSEDED (kept as history)."
fl = d["PENDING_EDITS_unapplied"]["WRITE_TIME_FLAGS"]
if not any("pagan1984 (2.3 P3) OMITTED" in x for x in fl):
    fl.append("pagan1984 (2.3 P3) OMITTED from prose (unverified + not in bib; no bibitem from memory). When NLM-verified: our UncRes is a generated REGRESSAND (dependent var); Pagan's classic SE result concerns generated REGRESSORS -> frame the two-step-SE point as the regressand case, do NOT conflate (advisor). Add the bibitem only after NLM verify.")
d["where_we_are"] = ("[2026-06-13] §2 PROSE, subsection-loop. 2.2 RATIFIED + committed (ac87c8c). 2.3 pushed to PDF (6pp), awaiting user "
  "ratification (UNCOMMITTED -> commit imminently). 2.4 being drafted now (park until 2.3 ratified). thesis_draft.tex = 2.1 + 2.2 + 2.3.")
d["NEXT_ACTION"] = ("=== Drafting 2.4 (park). AWAIT user ratification of 2.3 from the PDF. ON '2.3 ratified': flip 2.3 gate + commit; then "
  "push 2.4 -> compile -> open PDF. If user requests 2.3 EDITS: edit draft -> re-record -> re-push -> recompile. THEN 2.5 (last subsection). "
  "Each subsection: Phase A verify FIRST. 2.4 Phase A = NLM-verify opler1999/bates2009/petersen2009/cameron2011 OR drop; equations "
  "transcribed from file:line; NO number preview (C1/C2/C6 framing only). DISCIPLINE: programmatic transfer w/ drift+dash asserts; NLM sole "
  "paper authority; numbers bible-verbatim; SHOW/ratify in PDF; hypotheses set off; no '---'/'--'.")
open(r, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
json.load(open(r, encoding="utf-8"))
print("resume updated: 2.2 ratified/committed; 2.3 pushed-pending; 2.4 in progress; pagan flag.")
