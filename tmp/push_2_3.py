# Push/REPLACE §2.3 in thesis_draft.tex from the ledger JSON. If 2.3 already present, replace its block
# (title -> next subsection or bib anchor); else insert before the bib. Programmatic, fail-closed.
import json
LED = "docs/Thesis/rewrite/section2.3_paragraph_ledger.json"
TEX = "docs/Thesis/thesis_draft.tex"
d = json.load(open(LED, encoding="utf-8"))
P = d["paragraphs"]
paras = [P[k]["final_prose"] for k in ["P1", "P2", "P3"]]
for k, t in zip(["P1","P2","P3"], paras):
    assert t.strip(), f"{k} empty"
    assert "DWZ" not in t, f"{k} still has bare DWZ"

tex = open(TEX, encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in tex else "\n"
title = "\\subsection{Estimation of the Main Variable}"
assert "subsection{Hypothesis Development}" in tex, "2.2 missing -- abort"
block_lines = [title, ""]
for t in paras:
    block_lines.append(t); block_lines.append("")
block = nl.join(block_lines) + nl

if title in tex:
    start = tex.index(title)
    cands = [tex.find("\\subsection{", start + len(title)), tex.find("% References", start), tex.find("\\begin{thebibliography}", start)]
    end = min(c for c in cands if c != -1)
    new = tex[:start] + block + tex[end:]
else:
    anchor = next(a for a in ["% References — every entry verbatim-verified against the paper's own first/title page", "\\begin{thebibliography}"] if a in tex)
    new = tex.replace(anchor, block + anchor)
assert new.count(title) == 1 and new != tex
open(TEX, "w", encoding="utf-8", newline="").write(new)
print("pushed/replaced §2.3 in thesis_draft.tex from ledger JSON.")
