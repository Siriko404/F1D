import re
from pathlib import Path
C = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D-phase3\docs\Thesis\_uottawa_rewrite")
labels = set()
for f in ["_tables_from_bible.tex", "_robustness_tables.tex", "_dwz_replication.tex"]:
    labels |= set(re.findall(r"\\label\{(tab:[A-Za-z0-9_]+)\}", (C / f).read_text(encoding="utf-8")))
prose = ""
for f in ["thesis_draft_uottawa.tex", "_intro_body.tex", "_abstract_body.tex", "_conclusion_body.tex", "sec34_body_from_ledgers.tex"]:
    prose += (C / f).read_text(encoding="utf-8")
used = set(re.findall(r"\\ref\{(tab:[A-Za-z0-9_]+)\}", prose))
print("TABLES THAT EXIST: %d" % len(labels))
print("REFERENCED in prose: %d" % len(used))
print("\nORPHANED (exist but NEVER referenced) = dropped content:")
for t in sorted(labels - used):
    print("   ", t)
print("\nbroken refs (ref to missing table):", sorted(used - labels) or "none")
