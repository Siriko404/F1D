# Verify §2.3 P1-P3 are verbatim substrings of the .tex + dash-free, AND §2.2 is still intact. Fail-closed.
import json
tex = open("docs/Thesis/thesis_draft.tex", encoding="utf-8").read()
d3 = json.load(open("docs/Thesis/rewrite/section2.3_paragraph_ledger.json", encoding="utf-8"))
for k in ["P1", "P2", "P3"]:
    fp = d3["paragraphs"][k]["final_prose"]
    assert fp.strip() and fp in tex, f"2.3 {k} NOT verbatim in .tex"
    assert "---" not in fp and "--" not in fp, f"2.3 {k} banned dash"
d2 = json.load(open("docs/Thesis/rewrite/section2.2_paragraph_ledger.json", encoding="utf-8"))
for k in ["P1", "P2", "P3", "P4", "P5"]:
    assert d2["paragraphs"][k]["final_prose"] in tex, f"2.2 {k} disappeared from .tex"
print("VERIFIED: 2.3 P1-P3 verbatim + dash-free; 2.2 still intact.")
