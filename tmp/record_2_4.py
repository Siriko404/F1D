# Record §2.4 (P1-P5) into the ledger from the marker-split draft. Multi-line + DASH-FREE asserts. NOT ratified.
import json
DRAFT = "tmp/draft_2_4_full.tex"
LED = "docs/Thesis/rewrite/section2.4_paragraph_ledger.json"
parts = open(DRAFT, encoding="utf-8").read().split("%%")
md = dict(zip(parts[1::2], parts[2::2]))
order = ["P1", "P2", "P3", "P4", "P5"]
segs = {k: md[k].strip() for k in order}

for k, v in segs.items():
    assert "---" not in v and "--" not in v, f"{k}: banned dash"
assert r"\beta\,\mathrm{PreAnnounceQtr}_{it}" in segs["P1"] and r"estimates the pre-announcement shift $\theta_{-1}$" in segs["P1"], "P1 MA1/theta missing"
assert r"\beta_{\mathrm{PRE1}}-\beta_{\mathrm{GAP}}>0" in segs["P2"] and "largely mechanical" in segs["P2"], "P2 Wald/mechanical missing"
assert r"\beta_c\,\mathrm{PreAnnCash}_{it}" in segs["P3"] and r"\theta_{-1}^{\,\mathrm{cash}}-\theta_{-1}^{\,\mathrm{stock}}" in segs["P3"], "P3 MA3/theta missing"
assert "stock-only acquirers sit among the controls" in segs["P4"], "P4 SEAM-D missing"
assert "at least five calls" in segs["P5"], "P5 calls phrasing missing"

d = json.load(open(LED, encoding="utf-8"))
P = d["paragraphs"]
NR = ("DRAFTED-IN-LEDGER 2026-06-13 (MA1/MA2/MA3 verified vs code file:line; beta<->theta/kappa bridges; advisor-clean; "
      "dash-free; NO numbers; pushed to .tex for PDF review; NOT ratified)")
for k in order:
    P[k]["final_prose"] = segs[k]
    P[k]["prose_status"] = NR
open(LED, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
json.load(open(LED, encoding="utf-8"))
print("recorded 2.4 (P1-P5) -> ledger; dash-free; NOT ratified.")
