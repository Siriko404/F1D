# Trim thesis_draft.tex to ONLY the locked content: preamble+title, the section-2 heading + 2.1
# (Conceptual Framework), and the full bibliography. Remove abstract, intro, stale 2.2-2.5, 3, 4, 5,
# and the appendices. Line-slice = the locked 2.1 prose + verbatim-verified bib are copied byte-exact
# (never retyped). Reversible via git (full draft preserved at commit 81efc78). Fail-closed on boundaries.
src = "docs/Thesis/thesis_draft.tex"
lines = open(src, encoding="utf-8").read().split("\n")  # file line N == lines[N-1]

# --- fail-closed boundary asserts (abort if the file's line numbers drifted) ---
assert lines[23].strip() == "\\maketitle", f"L24 != maketitle: {lines[23]!r}"
assert "Conceptual Framework and Empirical Strategy" in lines[49], f"L50 != sec2: {lines[49]!r}"
assert lines[51].strip() == "\\subsection{Conceptual Framework}", f"L52 != 2.1 head: {lines[51]!r}"
assert "Two readings of this prediction" in lines[66], f"L67 != P7: {lines[66][:60]!r}"
assert lines[68].strip() == "\\subsection{Hypothesis Development}", f"L69 != stale 2.2: {lines[68]!r}"
assert "thebibliography}{10}" in lines[205], f"L206 != bib start: {lines[205]!r}"
assert lines[273].strip() == "\\end{thebibliography}", f"L274 != bib end: {lines[273]!r}"
assert lines[348].strip() == "\\end{document}", f"L349 != end doc: {lines[348]!r}"

kept = []
kept += lines[0:24]        # L1-24   preamble + \begin{document} + \maketitle
kept += [""]
kept += lines[49:67]       # L50-67  \section{Conceptual Framework...} + \subsection{Conceptual Framework} (P1-P7) [LOCKED]
kept += [""]
kept += lines[203:274]     # L204-274 References provenance comments + full \begin{thebibliography}...\end{thebibliography}
kept += [""]
kept += ["\\end{document}", ""]

open(src, "w", encoding="utf-8", newline="\n").write("\n".join(kept))

# validation summary
print(f"trimmed: {len(lines)} -> {len(kept)} lines")
print("first kept:", repr(kept[0]))
print("last non-empty kept:", repr([l for l in kept if l.strip()][-1]))
import re
heads = [l for l in kept if re.match(r"\\(section|subsection)\b", l)]
print("section/subsection headings remaining:")
for h in heads:
    print("  ", h)
