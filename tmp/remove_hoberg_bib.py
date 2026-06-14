# Remove the hoberg2010 + hoberg2016 \bibitem blocks -- ONLY after asserting no surviving \cite{hoberg}. Fail-closed.
TEX = "docs/Thesis/thesis_draft.tex"
tex = open(TEX, encoding="utf-8", newline="").read()
assert "\\citet{hoberg" not in tex and "\\citep{hoberg" not in tex and "\\cite{hoberg" not in tex, "hoberg still CITED -- abort bib removal"
nl = "\r\n" if "\r\n" in tex else "\n"
lines = tex.split(nl)
out, i, removed = [], 0, 0
while i < len(lines):
    ln = lines[i]
    if ln.lstrip().startswith("\\bibitem") and ("{hoberg2010}" in ln or "{hoberg2016}" in ln):
        i += 1                                   # skip the \bibitem line
        while i < len(lines) and lines[i].strip() != "":
            i += 1                               # skip the entry body line(s)
        if i < len(lines) and lines[i].strip() == "":
            i += 1                               # skip the trailing blank line
        removed += 1
        continue
    out.append(ln); i += 1
new = nl.join(out)
assert "hoberg2010" not in new and "hoberg2016" not in new, "hoberg bibitem still present"
assert removed == 2, f"expected 2 bibitems removed, got {removed}"
open(TEX, "w", encoding="utf-8", newline="").write(new)
print(f"removed {removed} hoberg bibitems (no surviving \\cite).")
