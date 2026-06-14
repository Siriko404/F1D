# Post-edit gate: thesis_draft.tex competition-free; 2.5 P1/P2/P4/P5 verbatim; FB placeholder present; cross-ref targets survive.
import json
tex = open("docs/Thesis/thesis_draft.tex", encoding="utf-8").read()
low = tex.lower()
for w in ["hoberg", "competition", "discriminant", "tnic", "fluidity"]:
    assert w not in low, f"'{w}' still in thesis_draft.tex"
d = json.load(open("docs/Thesis/rewrite/section2.5_paragraph_ledger.json", encoding="utf-8"))
assert list(d["paragraphs"]) == ["P1", "P2", "P4", "P5"], list(d["paragraphs"])
for k in ["P1", "P2", "P4", "P5"]:
    fp = d["paragraphs"][k]["final_prose"]
    assert fp.strip() and fp in tex, f"2.5 {k} not verbatim in .tex"
    assert "---" not in fp and "--" not in fp, f"2.5 {k} dash"
assert "PLACEHOLDER-FB" in tex, "FB placeholder lost from .tex"
# cross-ref targets that 2.2 P5 / 2.3 P2.5 point to must still exist
assert "P4" in d["paragraphs"] and "P5" in d["paragraphs"], "2.5 P4/P5 cross-ref targets missing"
# bib + roadmap clean
assert "hoberg" not in tex.lower()
rm = open("docs/Thesis/rewrite/section2_roadmap.md", encoding="utf-8").read().lower()
for w in ["hoberg", "discriminant", "competition"]:
    assert w not in rm, f"roadmap still has '{w}'"
print("POST-GATE PASS: .tex + roadmap competition-free; 2.5 P1/P2/P4/P5 verbatim + dash-free; FB placeholder present; P4/P5 targets intact.")
