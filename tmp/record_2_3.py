# Record §2.3 (P1-P3) into the ledger from the marker-split draft. Multi-line + DASH-FREE asserts. NOT ratified.
import json
DRAFT = "tmp/draft_2_3_full.tex"
LED = "docs/Thesis/rewrite/section2.3_paragraph_ledger.json"

parts = open(DRAFT, encoding="utf-8").read().split("%%")   # '%%' appears only in %%NAME%% markers
md = dict(zip(parts[1::2], parts[2::2]))
order = ["P1", "P2", "P3"]
segs = {k: md[k].strip() for k in order}

for k, v in segs.items():
    assert "---" not in v, f"{k}: em-dash '---' present"
    assert "--" not in v, f"{k}: en-dash '--' present"
# equations verbatim (primary-source forms) + key framing present
assert r"\frac{\mathrm{UnctWordsAnsCEO}}{\mathrm{WordsAnsCEO}}" in segs["P1"], "eq-2 missing"
assert r"\gamma_i\,\mathrm{CEO}_{i,t}" in segs["P2"] and r"\mathrm{UncResCEO}=\varepsilon_{i,t}" in segs["P2"], "eq-4 missing"
assert "DWZ themselves construct this residual and use it" in segs["P2"], "Catch-1 gloss missing"
assert "two-step" in segs["P3"], "generated-regressand framing missing"

d = json.load(open(LED, encoding="utf-8"))
P = d["paragraphs"]
NR = ("DRAFTED-IN-LEDGER 2026-06-13 (eq-2/eq-4 verbatim from verified source; dash-free; advisor-clean; pushed to "
      ".tex for PDF review; NOT ratified -- gate locked until user ratifies from the PDF)")
for k in order:
    P[k]["final_prose"] = segs[k]
    P[k]["prose_status"] = NR
open(LED, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
json.load(open(LED, encoding="utf-8"))
print("recorded 2.3 (P1-P3) -> ledger; dash-free; NOT ratified.")
