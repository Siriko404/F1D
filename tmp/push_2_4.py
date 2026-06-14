# Push §2.4 into thesis_draft.tex from the ledger JSON (after 2.3, before the bib). Programmatic, fail-closed.
import json
LED = "docs/Thesis/rewrite/section2.4_paragraph_ledger.json"
TEX = "docs/Thesis/thesis_draft.tex"
d = json.load(open(LED, encoding="utf-8"))
P = d["paragraphs"]
paras = [P[k]["final_prose"] for k in ["P1", "P2", "P3", "P4", "P5"]]
for k, t in zip(["P1","P2","P3","P4","P5"], paras):
    assert t.strip(), f"{k} empty"

tex = open(TEX, encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in tex else "\n"
title = "\\subsection{Methodology and Empirical Design}"
assert title not in tex, "2.4 already in .tex (idempotency)"
assert "subsection{Estimation of the Main Variable}" in tex, "2.3 missing -- push 2.3 first"
anchor = next(a for a in ["% References — every entry verbatim-verified against the paper's own first/title page", "\\begin{thebibliography}"] if a in tex)
block_lines = [title, ""]
for t in paras:
    block_lines.append(t); block_lines.append("")
block = nl.join(block_lines) + nl
new = tex.replace(anchor, block + anchor)
assert new.count(title) == 1 and new != tex
open(TEX, "w", encoding="utf-8", newline="").write(new)
print("pushed §2.4 (P1-P5) into thesis_draft.tex from ledger JSON.")
