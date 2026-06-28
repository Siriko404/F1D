# Layer-0 DETERMINISTIC number audit (the fatal dimension; advisor must-fix #1). Three certain checks:
#   A. PROVENANCE -- every prose coefficient sitting next to ONE \ref{tab:X} must appear in THAT table
#      (not just some table). Econ-effect sentences (which mix a coef + a base + a %) are handled in B, not A.
#   B. RECOMPUTE -- every "X% of a ... SD / of the mean" claim must be reproduced by a pair of numbers stated
#      in the same sentence (coef/base*100 == X%, within 0.25pp). This resolves the old "2 false positives".
#   C. CONSTANTS -- the key reused constants (residual SD 0.3010, mean cash ratio 0.1708) are stated consistently.
# Read-only. No agent. Run on the clone prose + table files.
import re
from pathlib import Path
C = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D-phase3\docs\Thesis\_uottawa_rewrite")
PROSE = ["thesis_draft_uottawa.tex", "_intro_body.tex", "_abstract_body.tex", "_conclusion_body.tex", "sec34_body_from_ledgers.tex"]
TABLES = ["_tables_from_bible.tex", "_robustness_tables.tex", "_dwz_replication.tex"]
rd = lambda f: (C / f).read_text(encoding="utf-8") if (C / f).exists() else ""
prose = "\n".join(rd(f) for f in PROSE)
tables = "\n".join(rd(f) for f in TABLES)

pos = sorted((m.start(), m.group(1)) for m in re.finditer(r"\\label\{(tab:[A-Za-z0-9_]+)\}", tables))
block = {}
for i, (p, lab) in enumerate(pos):
    block[lab] = tables[p:(pos[i + 1][0] if i + 1 < len(pos) else len(tables))]

NUM = re.compile(r"-?\d\.\d{2,5}")
ECON = re.compile(r"standard deviation|of a residual|of the mean|percent|\\%|fifteen|third of")
sents = re.split(r"(?<=[.])\s+(?=[A-Z(\\])", prose)

print("== A. PROVENANCE: prose coefficient vs the SINGLE table it cites ==")
provA = 0
for s in sents:
    rs = set(re.findall(r"\\ref\{(tab:[A-Za-z0-9_]+)\}", s))
    if len(rs) != 1:
        continue
    lab = next(iter(rs))
    if lab not in block or ECON.search(s):     # econ-effect sentences -> checked in B
        continue
    for n in set(re.findall(NUM, s)):
        if n not in block[lab]:
            provA += 1
            print("  [%s] %s NOT in cited table :: %s" % (lab.replace("tab:", ""), n, re.sub(r"\s+", " ", s)[:130]))
print("  -- %d prose coefficient(s) not found in the single table they cite (0 = clean) --" % provA)

print("\n== B. RECOMPUTE: every X%% econ-effect claim reproduced by a stated pair ==")
okB = badB = 0
for i, s in enumerate(sents):
    if not re.search(r"standard deviation|of the mean|residual standard", s):
        continue
    pcts = re.findall(r"(\d{1,2}\.\d)\\?%", s)
    window = (sents[i - 1] + " " + s) if i > 0 else s      # the coef may sit in the PRIOR sentence (e.g. the Wald 0.0983 -> 32.7%)
    vals = [float(x) for x in re.findall(NUM, window)]
    for p in pcts:
        claimed = float(p)
        hit = [(a, b) for a in vals for b in vals if b and a != b and abs(a) < abs(b) and abs(claimed - a / b * 100) < 0.25]
        if hit:
            okB += 1
            print("  OK   %s%% == %s/%s*100 (=%.2f)" % (p, hit[0][0], hit[0][1], hit[0][0] / hit[0][1] * 100))
        else:
            badB += 1
            print("  FAIL %s%% NOT reproduced by any stated pair :: %s" % (p, re.sub(r"\s+", " ", s)[:140]))
print("  -- %d reproduced, %d UNREPRODUCED (0 = clean) --" % (okB, badB))

print("\n== C. KEY-CONSTANT CONSISTENCY ==")
for nm, v in [("residual SD", "0.3010"), ("mean cash ratio", "0.1708"), ("HighCashScrutiny mean", "0.1127")]:
    print("  %-22s $%s$ appears %d time(s) in prose" % (nm, v, prose.count("$" + v + "$")))
print("\nVERDICT: provenance + recompute clean iff A=0 and B-unreproduced=0.")
