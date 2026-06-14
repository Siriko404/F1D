# Replace §2.5 in thesis_draft.tex from the ledger (keys P1/P2/P4/P5 -- P3 dropped). Fail-closed.
import json
LED = "docs/Thesis/rewrite/section2.5_paragraph_ledger.json"
TEX = "docs/Thesis/thesis_draft.tex"
d = json.load(open(LED, encoding="utf-8"))
P = d["paragraphs"]
keys = ["P1", "P2", "P4", "P5"]
paras = [P[k]["final_prose"] for k in keys]
for k, t in zip(keys, paras):
    assert t.strip(), f"{k} empty"
    assert "hoberg" not in t.lower() and "competition" not in t.lower(), f"{k} competition residue"
tex = open(TEX, encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in tex else "\n"
title = "\\subsection{Specification and Measurement of Key Constructs}"
assert "subsection{Methodology and Empirical Design}" in tex, "2.4 missing"
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
print("pushed/replaced §2.5 (P1/P2/P4/P5) in thesis_draft.tex.")
