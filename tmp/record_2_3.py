# Re-record §2.3 (P1-P3) from the marker-split draft after the DWZ-citing fixes. Fail-closed.
# Enforces: NO bare 'DWZ' initialism; exact-equation citations (eq 2 raw / eq 4 residual / eq 5 their-use);
# 'published residuals' cut; dash-free; eq math verbatim. NOT ratified.
import json
DRAFT = "tmp/draft_2_3_full.tex"
LED = "docs/Thesis/rewrite/section2.3_paragraph_ledger.json"
parts = open(DRAFT, encoding="utf-8").read().split("%%")
md = dict(zip(parts[1::2], parts[2::2]))
order = ["P1", "P2", "P3"]
segs = {k: md[k].strip() for k in order}

for k, v in segs.items():
    assert "---" not in v and "--" not in v, f"{k}: banned dash"
    assert "DWZ" not in v, f"{k}: bare 'DWZ' initialism present (use natbib cites)"
assert r"Equation~(2) of \citet{dwz}" in segs["P1"], "P1: eq-(2) citation missing"
assert r"\frac{\mathrm{UnctWordsAnsCEO}}{\mathrm{WordsAnsCEO}}" in segs["P1"], "P1: eq-2 math missing"
assert r"Equation~(4) of \citet{dwz}" in segs["P2"], "P2: eq-(4) citation missing"
assert r"\mathrm{UncResCEO}=\varepsilon_{i,t}" in segs["P2"], "P2: residual definition missing"
assert "published residuals" not in segs["P2"], "P2: 'published residuals' must be cut"
assert "The authors themselves construct this residual and use it" in segs["P2"], "P2: Catch-1 phrasing missing"
assert r"their Equation~(5)" in segs["P2"], "P2: eq-(5) (their regressor use) citation missing"
assert r"\citeauthor{dwz}" in segs["P3"], "P3: author citation missing"

d = json.load(open(LED, encoding="utf-8"))
P = d["paragraphs"]
NR = ("DRAFTED-IN-LEDGER 2026-06-13 v2 (bare 'DWZ'->natbib cites; eq (2)/(4)/(5) cited; 'published residuals' cut; "
      "eq verbatim-verified; dash-free; pushed to .tex for PDF review; NOT ratified)")
for k in order:
    P[k]["final_prose"] = segs[k]
    P[k]["prose_status"] = NR
open(LED, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
json.load(open(LED, encoding="utf-8"))
print("re-recorded 2.3 v2 (no bare DWZ; eq (2)/(4)/(5) cited; published-residuals cut) -> ledger.")
