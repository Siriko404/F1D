# Verify each §2.2 final_prose (multi-line) is a VERBATIM substring of the .tex + dash-free. Fail-closed.
import json
d = json.load(open("docs/Thesis/rewrite/section2.2_paragraph_ledger.json", encoding="utf-8"))
tex = open("docs/Thesis/thesis_draft.tex", encoding="utf-8").read()
for k in ["P1", "P2", "P3", "P4", "P5"]:
    fp = d["paragraphs"][k]["final_prose"]
    assert fp.strip(), f"{k} empty"
    assert fp in tex, f"{k} final_prose is NOT a verbatim substring of the .tex"
    assert "---" not in fp and "--" not in fp, f"{k} contains a banned dash"
print("VERIFIED: all 5 §2.2 final_prose are verbatim substrings of the .tex; dash-free.")
