# Push §2.3 into thesis_draft.tex PROGRAMMATICALLY from the ledger JSON (after 2.2, before bib). Fail-closed.
import json
LED = "docs/Thesis/rewrite/section2.3_paragraph_ledger.json"
TEX = "docs/Thesis/thesis_draft.tex"
d = json.load(open(LED, encoding="utf-8"))
P = d["paragraphs"]
paras = [P[k]["final_prose"] for k in ["P1", "P2", "P3"]]
for k, t in zip(["P1","P2","P3"], paras):
    assert t.strip(), f"{k} final_prose empty"

tex = open(TEX, encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in tex else "\n"
assert "subsection{Estimation of the Main Variable}" not in tex, "2.3 already in .tex (idempotency)"
assert "subsection{Hypothesis Development}" in tex, "2.2 not in .tex -- push 2.2 first"
anchor = next(a for a in [
    "% References — every entry verbatim-verified against the paper's own first/title page",
    "\\begin{thebibliography}",
] if a in tex)
assert tex.count(anchor) == 1, "anchor not unique"

block_lines = ["\\subsection{Estimation of the Main Variable}", ""]
for t in paras:
    block_lines.append(t); block_lines.append("")
block = nl.join(block_lines) + nl
new = tex.replace(anchor, block + anchor)
assert new.count("subsection{Estimation of the Main Variable}") == 1 and new != tex
open(TEX, "w", encoding="utf-8", newline="").write(new)
print("pushed §2.3 (P1-P3) into thesis_draft.tex from ledger JSON.")
