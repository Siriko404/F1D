# Apply ratified §2 coherence fixes H, I, G (prose: tex + 2.5 ledger) and J (2.1 ledger status).
# K = no change (user kept H1b as-is). Count + drift + dash guarded.
import json
import pathlib

ROOT = pathlib.Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
TEX = ROOT / "docs" / "Thesis" / "thesis_draft.tex"
L25 = ROOT / "docs" / "Thesis" / "rewrite" / "section2.5_paragraph_ledger.json"
L21 = ROOT / "docs" / "Thesis" / "rewrite" / "section2.1_paragraph_ledger.json"

# (paragraph in 2.5 ledger, OLD, NEW)
EDITS = [
    ("P1", "established measures of uncertainty, and, separately,",
           "established measures of uncertainty and risk, and, separately,"),          # H
    ("P4", "is reported in the Appendix)",
           "is reported in Appendix~I)"),                                              # I
    ("P5", "of the decomposition, are catalogued in the Appendix.",
           "of the decomposition, are defined where each is introduced."),            # G
]
for _, _, new in EDITS:
    assert "--" not in new, f"dash in {new!r}"

# 1. .tex
tex = TEX.read_text(encoding="utf-8")
for _, old, new in EDITS:
    assert tex.count(old) == 1, f"TEX: expected 1 occ of {old!r}, got {tex.count(old)}"
    tex = tex.replace(old, new)
TEX.write_text(tex, encoding="utf-8")

# 2. 2.5 ledger final_prose (JSON-aware) + drift check
d = json.loads(L25.read_text(encoding="utf-8"))
tex_now = TEX.read_text(encoding="utf-8")
for para, old, new in EDITS:
    fp = d["paragraphs"][para]["final_prose"]
    assert old in fp, f"2.5 {para}: OLD not in final_prose"
    d["paragraphs"][para]["final_prose"] = fp.replace(old, new)
    assert d["paragraphs"][para]["final_prose"] in tex_now, f"DRIFT: 2.5 {para} not verbatim in .tex"
L25.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

# 3. J: 2.1 ledger P3-P7 prose_status DRAFTED -> provisional-ratified
RAT = "RATIFIED 2026-06-14 (provisional, user 'consider everything ratified for now'; in LOCKED thesis_draft.tex)"
d21 = json.loads(L21.read_text(encoding="utf-8"))
flipped = []
for k in ("P3", "P4", "P5", "P6", "P7"):
    if d21["paragraphs"][k].get("prose_status") == "DRAFTED":
        d21["paragraphs"][k]["prose_status"] = RAT
        flipped.append(k)
L21.write_text(json.dumps(d21, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

print(f"OK: tex H/I/G applied (3); 2.5 ledger synced (P1/P4/P5); 2.1 status flipped {flipped}.")
