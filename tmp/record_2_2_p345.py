# Record §2.2 P3/P4/P5 prose into the ledger FROM the draft file, with fail-closed DRIFT GUARDS.
# NOT flagged ratified (user reads the PDF first). P1/P2 in the ledger are canonical + untouched.
# Drift guards: the draft's P1/P2/P3 MUST byte-match their canonical JSON sources, else ABORT
# (that mismatch would be exactly the hand-transcription hallucination we are preventing).
import json

LED = "docs/Thesis/rewrite/section2.2_paragraph_ledger.json"
RES = "docs/Thesis/rewrite/_RESUME_STATE.json"
DRAFT = "tmp/draft_2_2_full.tex"

d = json.load(open(LED, encoding="utf-8"))
res = json.load(open(RES, encoding="utf-8"))
P = d["paragraphs"]

# extract the 5 prose paragraphs = non-empty lines that are not comments (%) and not LaTeX commands (\)
prose = [ln.rstrip("\n") for ln in open(DRAFT, encoding="utf-8")
         if ln.strip() and not ln.lstrip().startswith("%") and not ln.lstrip().startswith("\\")]
assert len(prose) == 5, f"expected 5 prose lines, got {len(prose)}"

# --- DRIFT GUARDS: the draft must match the canonical sources for P1/P2/P3 ---
assert prose[0] == P["P1"]["final_prose"], "DRIFT: draft P1 != ledger P1 -- ABORT (hand-copy drifted)"
assert prose[1] == P["P2"]["final_prose"], "DRIFT: draft P2 != ledger P2 -- ABORT"
assert prose[2] == res["prose_progress_2026_06_13"]["P3_draft_pending_advisor"], "DRIFT: draft P3 != parked resume P3 -- ABORT"
# advisor fixes must be present in the NEW paragraphs we are recording
assert "largely mechanical" in prose[3] and "most discriminating" in prose[3], "P4 advisor edits missing"
assert "without establishing the disclosure mechanism" in prose[4], "P5 advisor edit missing"

# --- record P3/P4/P5 final_prose; explicitly NOT ratified (gates left locked) ---
NOT_RATIFIED = "DRAFTED-IN-LEDGER 2026-06-13 (advisor-cleared; pushed to .tex for PDF review; NOT ratified -- gate stays locked until user ratifies from the PDF)"
for k, txt in [("P3", prose[2]), ("P4", prose[3]), ("P5", prose[4])]:
    assert P[k]["final_prose"] == "", f"{k} final_prose not empty: {P[k]['final_prose'][:40]!r}"
    P[k]["final_prose"] = txt
    P[k]["prose_status"] = NOT_RATIFIED
    # gates intentionally NOT unlocked (not ratified)

open(LED, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
json.load(open(LED, encoding="utf-8"))
print("DRIFT GUARDS PASSED (draft P1/P2/P3 byte-match canonical JSON). Recorded P3/P4/P5 into ledger (NOT ratified).\n")
print("P4 recorded:\n" + prose[3] + "\n")
print("P5 recorded:\n" + prose[4])
