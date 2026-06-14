# Record §2.2 v2 into the ledger from the marker-split draft. Multi-line final_prose (body + quote block).
# Fail-closed: dash-free ('---' and '--') per segment + advisor-fix presence + formal-math presence. NOT ratified.
import json
DRAFT = "tmp/draft_2_2_full.tex"
LED = "docs/Thesis/rewrite/section2.2_paragraph_ledger.json"

parts = open(DRAFT, encoding="utf-8").read().split("%%")   # markers are %%NAME%%; '%%' appears only in markers
names, texts = parts[1::2], parts[2::2]
md = dict(zip(names, texts))
order = ["FUNNEL", "H1", "H1a", "H1b", "FLAG"]
segs = {k: md[k].strip() for k in order}

# --- dash ban (mandatory): NO '---' or '--' anywhere in the prose segments ---
for k, v in segs.items():
    assert "---" not in v, f"{k}: em-dash '---' present"
    assert "--" not in v, f"{k}: en-dash '--' present"
# --- advisor fixes present ---
assert "faces questions that bear on it but can neither address nor deny" in segs["H1"], "P2 'must field' overclaim fix missing"
assert "for cash acquirers, unless a deal-type superscript" in segs["FUNNEL"], "theta default-cash note missing"
# --- formal math present (set-off hypotheses) ---
assert r"\begin{quote}" in segs["H1"] and r"$\theta_{-1}>0$" in segs["H1"]
assert r"\theta_{-1}^{\,\mathrm{cash}}>\theta_{-1}^{\,\mathrm{stock}}" in segs["H1a"]
assert r"\theta_{\mathrm{gap}}=0" in segs["H1b"] and r"\kappa_{\mathrm{gap}}>0" in segs["H1b"]

d = json.load(open(LED, encoding="utf-8"))
P = d["paragraphs"]
NR = ("DRAFTED-IN-LEDGER 2026-06-13 v2 (hypotheses SET OFF informal+formal; dash-free; advisor-cleared; "
      "pushed to .tex for PDF review; NOT ratified -- gate locked until user ratifies from the PDF)")
for pk, mk in [("P1","FUNNEL"),("P2","H1"),("P3","H1a"),("P4","H1b"),("P5","FLAG")]:
    P[pk]["final_prose"] = segs[mk]
    P[pk]["prose_status"] = NR
open(LED, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
json.load(open(LED, encoding="utf-8"))
print("recorded 2.2 v2 -> ledger (5 paragraphs; dash-free; hypotheses set off; NOT ratified).")
