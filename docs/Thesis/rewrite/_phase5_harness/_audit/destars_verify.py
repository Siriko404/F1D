# Issue-2 verifier: every coefficient that carried a significance STAR in the raw phaseB prose must, in the
# regenerated thesis prose, now carry a p-marker -- either the threshold matching its star count ($p<.01$
# for ***, $p<.05$ for **, $p<.10$ for *) or an exact p ($p=...$) the prose already gave. Echoes (repeat
# mentions) may stay bare as long as ONE mention carries the marker. Catches the "star stripped, p lost" case
# that the global no-star assert cannot. Read-only; run after build_uottawa_rewrite.py.
import json, re
from pathlib import Path

H = Path(__file__).resolve().parents[1]                 # _phase5_harness
SRC = H.parents[1]                                      # docs/Thesis
CLONE = SRC / "_uottawa_rewrite"
RES = json.load(open(H / "phaseB_result.json", encoding="utf-8"))
SEC = {s["section"]: s for s in RES["sections"]}
PMAP = {1: ".10", 2: ".05", 3: ".01"}

regen = (CLONE / "sec34_body_from_ledgers.tex").read_text(encoding="utf-8") + "\n" + \
        (CLONE / "thesis_draft_uottawa.tex").read_text(encoding="utf-8")

# 1. no significance star may survive in the regenerated PROSE (wrapper \inputs tables by filename, so the
#    table bodies are not in this text -- only prose is).
leftover = re.findall(r"\^\{\*+\}", regen)
print("stars left in regen prose : %d" % len(leftover))

# 2. every starred coef in raw phaseB -> must have a p-marker in regen
ids = ["2.5", "3.1", "3.2", "3.3", "3.4", "4.1", "4.2", "4.3", "4.4", "4.5"]
seen = {}
for sid in ids:
    raw = "\n".join(p["final_prose"] for p in SEC[sid]["paragraphs"])
    for m in re.finditer(r"\$(-?\d+\.\d+)\^\{(\*+)\}\$", raw):
        seen[(m.group(1), len(m.group(2)))] = seen.get((m.group(1), len(m.group(2))), 0) + 1

problems = []
for (val, st), cnt in sorted(seen.items()):
    pthr = "$p<%s$" % PMAP[st]
    ok = False
    for mm in re.finditer(re.escape("$" + val + "$"), regen):
        ctx = regen[mm.start(): mm.start() + 64]
        if pthr in ctx or "$p=" in ctx or "$p\\approx" in ctx:
            ok = True
            break
    if not ok:
        problems.append((val, st, PMAP[st], cnt))

print("distinct starred coefs     : %d" % len(seen))
print("coefs missing p-marker     : %d" % len(problems))
for val, st, thr, cnt in problems:
    print("   MISSING  $%s$  (%s stars -> p<%s, %d mention(s) in raw)" % (val, "*" * st, thr, cnt))
print("VERIFY %s" % ("PASS" if not leftover and not problems else "FAIL"))
