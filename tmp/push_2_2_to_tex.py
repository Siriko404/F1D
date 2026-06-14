# Push §2.2 into thesis_draft.tex PROGRAMMATICALLY from the ledger JSON (final_prose P1..P5).
# Zero hand-typing. Inserted between 2.1 P7 and the bibliography. Idempotent + fail-closed.
import json

LED = "docs/Thesis/rewrite/section2.2_paragraph_ledger.json"
TEX = "docs/Thesis/thesis_draft.tex"

d = json.load(open(LED, encoding="utf-8"))
P = d["paragraphs"]
paras = [P[k]["final_prose"] for k in ["P1", "P2", "P3", "P4", "P5"]]
for k, t in zip(["P1","P2","P3","P4","P5"], paras):
    assert t.strip(), f"{k} final_prose empty -- cannot push"

tex = open(TEX, encoding="utf-8", newline="").read()        # newline="" preserves original EOLs
nl = "\r\n" if "\r\n" in tex else "\n"
assert "subsection{Hypothesis Development}" not in tex, "2.2 already in .tex -- abort (idempotency)"

ANCHOR = "% References --- every entry verbatim-verified".replace("---", "—")  # the em-dash in the file
# fall back to a robust anchor substring actually present
anchor = next(a for a in [
    "% References — every entry verbatim-verified against the paper's own first/title page",
    "\\begin{thebibliography}",
] if a in tex)
assert tex.count(anchor) == 1, f"anchor not unique: {anchor!r} ({tex.count(anchor)})"

block_lines = [
    "\\subsection{Hypothesis Development}",
    "% 2.2 DRAFT pushed for PDF review 2026-06-13 -- NOT ratified (user ratifies from the PDF); ledger gate locked.",
    "",
]
for i, t in enumerate(paras):
    block_lines.append(t)
    block_lines.append("")
block = nl.join(block_lines) + nl

new_tex = tex.replace(anchor, block + anchor)
assert new_tex.count("subsection{Hypothesis Development}") == 1
assert new_tex != tex

open(TEX, "w", encoding="utf-8", newline="").write(new_tex)
print(f"pushed §2.2 (P1-P5) into {TEX} from ledger JSON. EOL={'CRLF' if nl=='\\r\\n' else 'LF'}. anchor={anchor[:40]!r}")
