# Expand every \input{...} in the uOttawa thesis into ONE self-contained .tex --
# the single file that holds everything the PDF reader sees (prose + all tables + bib + appendices).
import re
from pathlib import Path
C = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D-phase3\docs\Thesis\_uottawa_rewrite")

def flatten(path, depth=0):
    txt = path.read_text(encoding="utf-8")
    def repl(m):
        name = m.group(1).strip()
        if not name.endswith(".tex"):
            name += ".tex"
        f = C / name
        if f.exists():
            return "\n%% <<<<< begin %s >>>>>\n%s\n%% <<<<< end %s >>>>>\n" % (name, flatten(f, depth + 1), name)
        return m.group(0)
    return re.sub(r"\\input\{([^}]+)\}", repl, txt)

flat = flatten(C / "thesis_draft_uottawa.tex")
out = C / "_thesis_FLAT.tex"
out.write_text(flat, encoding="utf-8")

# verify it holds everything
tabs = len(re.findall(r"\\label\{tab:", flat))
bib = len(re.findall(r"\\bibitem", flat))
chaps = len(re.findall(r"\\chapter\{", flat))
secs = len(re.findall(r"\\section\{", flat))
apps = len(re.findall(r"Variable Definitions|Cash-Scrutiny Measure", flat))
inputs_left = re.findall(r"\\input\{([^}]+)\}", flat)
print("wrote %s : %d chars (%d KB)" % (out.name, len(flat), len(flat) // 1024))
print("tables(label):%d  bibitems:%d  chapters:%d  sections:%d  appendix-markers:%d" % (tabs, bib, chaps, secs, apps))
print("unexpanded \\input left (want none):", inputs_left or "none")
