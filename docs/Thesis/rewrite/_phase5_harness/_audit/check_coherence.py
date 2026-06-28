# Deterministic coherence sweep over the integrated uOttawa thesis clone.
# Checks: table refs (broken/orphan/dup/hardcoded), citations (undefined/orphan bibitem),
# internal section+appendix refs, and prose-number-in-cited-table (the desync class).
import re
from pathlib import Path
C = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D-phase3\docs\Thesis\_uottawa_rewrite")
TABLE_FILES = ["_tables_from_bible.tex", "_robustness_tables.tex", "_dwz_replication.tex"]
PROSE_FILES = ["thesis_draft_uottawa.tex", "_intro_body.tex", "_abstract_body.tex", "_conclusion_body.tex", "sec34_body_from_ledgers.tex"]
APP_FILES = ["appendix_I_cash_scrutiny.tex", "appendix_II_controls.tex"]
rd = lambda f: (C / f).read_text(encoding="utf-8") if (C / f).exists() else ""
tables = "\n".join(rd(f) for f in TABLE_FILES)
prose = "\n".join(rd(f) for f in PROSE_FILES + APP_FILES)
full = tables + "\n" + prose
def hdr(s): print("\n" + "=" * 4 + " " + s + " " + "=" * 4)

# ---------- A. TABLES ----------
hdr("A. TABLE REFERENCES")
labels = re.findall(r"\\label\{(tab:[A-Za-z0-9_]+)\}", tables)
refs = set(re.findall(r"\\ref\{(tab:[A-Za-z0-9_]+)\}", full))
print("broken refs (ref, no label):", sorted(refs - set(labels)) or "none")
print("orphan tables (label, never ref'd):", sorted(set(labels) - refs) or "none")
print("duplicate labels:", [l for l in set(labels) if labels.count(l) > 1] or "none")
hard = re.findall(r"Table~?\s*\d+\.?\d*", prose)
print("hardcoded 'Table N' in prose (should be \\ref):", hard or "none")

# ---------- B. CITATIONS ----------
hdr("B. CITATIONS")
biblabels = set(re.findall(r"\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}", full))
cites = set()
for g in re.findall(r"\\cite[tp]?(?:author)?\{([^}]+)\}", full):
    cites |= {k.strip() for k in g.split(",")}
print("cite keys with NO bibitem (undefined):", sorted(cites - biblabels) or "none")
print("bibitems never cited (orphan refs):", sorted(biblabels - cites) or "none")

# ---------- C. INTERNAL SECTION / APPENDIX REFS ----------
hdr("C. INTERNAL REFS")
sec_defined = set(re.findall(r"\\section\{", prose))  # count only
chap = re.findall(r"\\chapter\{([^}]+)\}", prose)
secs = re.findall(r"\\section\{([^}]+)\}", prose)
print("chapters:", len(chap), "| sections:", len(secs))
secrefs = sorted(set(re.findall(r"Sections?~?(\d+(?:\.\d+)?)", prose)), key=lambda x: [int(p) for p in x.split(".")])
print("section numbers referenced in prose:", secrefs)
apprefs = sorted(set(re.findall(r"Appendix~?([IVX]+)", prose)))
print("appendix refs:", apprefs, "| appendix files present:", [f for f in APP_FILES if (C / f).exists()])

# ---------- D. PROSE NUMBER -> CITED TABLE (desync class) ----------
hdr("D. NUMBER vs CITED TABLE  (flags = possible desync, eyeball)")
# build label -> that table's text block (label position to next label)
pos = sorted([(m.start(), m.group(1)) for m in re.finditer(r"\\label\{(tab:[A-Za-z0-9_]+)\}", tables)])
block = {}
for i, (p, lab) in enumerate(pos):
    end = pos[i + 1][0] if i + 1 < len(pos) else len(tables)
    block[lab] = tables[p:end]
sents = re.split(r"(?<=[.])\s+(?=[A-Z(])", prose)
flags = 0
for s in sents:
    rs = set(re.findall(r"\\ref\{(tab:[A-Za-z0-9_]+)\}", s))
    if len(rs) != 1:
        continue                                   # skip 0- or multi-table sentences (ambiguous)
    lab = next(iter(rs))
    if lab not in block:
        continue
    nums = set(re.findall(r"\d\.\d{3,4}", s))       # 3-4 dp coefficients / SEs
    miss = [n for n in nums if n not in block[lab]]
    if miss:
        flags += 1
        txt = re.sub(r"\s+", " ", s)[:140]
        print("  [%s] missing %s :: %s..." % (lab.replace("tab:", ""), miss, txt))
print("-- %d sentence(s) with a number not found in the single table they cite --" % flags)
