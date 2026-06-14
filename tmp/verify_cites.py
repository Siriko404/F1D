# Cross-reference integrity check: every \cite key resolves to a \bibitem; flag orphans.
# Programmatic (regex on the .tex), not eyeballed. Firm evidence for "structurally safe".
import re, pathlib
tex = pathlib.Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\docs\Thesis\thesis_draft.tex").read_text(encoding="utf-8")
i = tex.index(r"\begin{thebibliography}")
prose, bib = tex[:i], tex[i:]
cites = set()
for m in re.finditer(r"\\cite[a-z]*\*?(?:\[[^\]]*\])?\{([^}]+)\}", prose):
    for k in m.group(1).split(","):
        cites.add(k.strip())
bibs = [k for k in re.findall(r"\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}", bib)]
bibset = set(bibs)
print("CITED keys (%d): %s" % (len(cites), sorted(cites)))
print("BIBITEM keys (%d): %s" % (len(bibs), sorted(bibs)))
print("DUP bibitem keys:", [k for k in bibset if bibs.count(k) > 1])
print("UNDEFINED (cited, no bibitem):", sorted(cites - bibset))
print("ORPHAN (bibitem, never cited in sec2):", sorted(bibset - cites))
# the 5 names I wrongly flagged:
for k in ("pagan1984","opler1999","bates2009","petersen2009","cameron2011"):
    print("  present?", k, "->", k in tex)
