# Verify 2.2 + 2.3(v2) + 2.4 are all verbatim substrings of the .tex, dash-free, and 2.3 has no bare DWZ.
import json
tex = open("docs/Thesis/thesis_draft.tex", encoding="utf-8").read()
for sec, keys in [("section2.2", ["P1","P2","P3","P4","P5"]),
                  ("section2.3", ["P1","P2","P3"]),
                  ("section2.4", ["P1","P2","P3","P4","P5"])]:
    d = json.load(open(f"docs/Thesis/rewrite/{sec}_paragraph_ledger.json", encoding="utf-8"))
    for k in keys:
        fp = d["paragraphs"][k]["final_prose"]
        assert fp.strip() and fp in tex, f"{sec} {k} NOT verbatim in .tex"
        assert "---" not in fp and "--" not in fp, f"{sec} {k} banned dash"
d3 = json.load(open("docs/Thesis/rewrite/section2.3_paragraph_ledger.json", encoding="utf-8"))
for k in ["P1","P2","P3"]:
    assert "DWZ" not in d3["paragraphs"][k]["final_prose"], f"2.3 {k} still has bare DWZ"
print("VERIFIED: 2.2 + 2.3(no bare DWZ) + 2.4 all verbatim in .tex; dash-free.")
