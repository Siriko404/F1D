# Record §2.5 (P1-P5) into the ledger from the marker-split draft. Numbers bible-verbatim; F1 no-persistent;
# scrutiny verdict held to 4.1; cites verified; hoberg2010/fluidity dropped; dash-free. NOT ratified.
import json
DRAFT = "tmp/draft_2_5_full.tex"
LED = "docs/Thesis/rewrite/section2.5_paragraph_ledger.json"
parts = open(DRAFT, encoding="utf-8").read().split("%%")
md = dict(zip(parts[1::2], parts[2::2]))
order = ["P1", "P2", "P3", "P4", "P5"]
segs = {k: md[k].strip() for k in order}

for k, v in segs.items():
    assert "---" not in v and "--" not in v, f"{k}: banned dash"
    assert "DWZ" not in v, f"{k}: bare DWZ"
    assert "hoberg2010" not in v and "fluidity" not in v, f"{k}: hoberg2010/fluidity must be dropped"
# convergent (C5)
assert "consistent with" in segs["P2"] and r"\citet{hassan2020}" in segs["P2"] and "0.0124" in segs["P2"] and "0.0181" in segs["P2"], "P2 convergent missing"
# discriminant (C3) + N fix + F1
assert "0.0304" in segs["P3"] and "0.0008" in segs["P3"] and "12{,}728" in segs["P3"] and "18{,}492" in segs["P3"], "P3 numbers missing"
assert "smaller residual sample" in segs["P3"], "P3 N-fix wording missing"
assert r"\citet{hoberg2016}" in segs["P3"], "hoberg2016 cite missing"
assert "persistent" not in segs["P3"], "F1: competition must NOT be called 'persistent'"
# scrutiny construct (C4 validity only; verdict -> 4.1)
assert "0.7530" in segs["P4"] and "0.8519" in segs["P4"], "C4 validity numbers missing"
assert "behaves as intended" in segs["P4"], "P4.2 'behaves as intended' wording missing"

d = json.load(open(LED, encoding="utf-8"))
P = d["paragraphs"]
NR = ("DRAFTED-IN-LEDGER 2026-06-13 (numbers bible-verbatim incl. P3 N-fix; 'consistent with' verbatim; F1 no 'persistent'; "
      "scrutiny verdict->4.1; cites verified; hoberg2010/fluidity dropped; dash-free; pushed to .tex for PDF review; NOT ratified)")
for k in order:
    P[k]["final_prose"] = segs[k]
    P[k]["prose_status"] = NR
open(LED, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
json.load(open(LED, encoding="utf-8"))
print("recorded 2.5 (P1-P5) -> ledger; numbers bible-verbatim; dash-free; NOT ratified.")
