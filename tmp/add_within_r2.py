# -*- coding: utf-8 -*-
"""Advisor fix: add the verified within-R2 number to the FE entries of PARA1-b (0.003)
and PARA3-b (0.059). Pure mechanical number, no interpretation. Edit BOTH placed + MERGED
identically; assert within-R2 present, MERGED==placed, nothing else changed. WRITE to apply."""
import json, sys
from pathlib import Path
FIN=Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D-phase3\docs\Thesis\rewrite\_final")
DST=FIN/"section4.5_paragraph_ledger.json"; SRC=FIN/"_proposals"/"section4.5_MERGED.json"
WRITE=len(sys.argv)>1 and sys.argv[1]=="WRITE"
# verify the numbers vs fe_results.json first
F=json.load(open(FIN.parent.parent.parent/"tmp"/"fe_results.json",encoding="utf-8")) if (FIN.parent.parent.parent/"tmp"/"fe_results.json").exists() else json.load(open(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D-phase3\tmp\fe_results.json",encoding="utf-8"))
assert round(F["TEST_A"]["r2_within"],3)==0.003, F["TEST_A"]["r2_within"]
assert round(F["TEST_B"]["r2_within"],3)==0.059, F["TEST_B"]["r2_within"]

EDITS=[  # (find, replace) -- applied to both files
 ("It survives firm and year-quarter fixed effects: LPM 0.0078*** (SE 0.00275, N 39,557).",
  "It survives firm and year-quarter fixed effects: LPM 0.0078*** (SE 0.00275, N 39,557; within-R2 0.003)."),
 ("0.0078*** (FE-LPM, Firm + Year-Qtr FE; fe_results.json TEST_A; SE 0.00275, N 39,557, firms 1,422)",
  "0.0078*** (FE-LPM, Firm + Year-Qtr FE; fe_results.json TEST_A; SE 0.00275, N 39,557, firms 1,422; within-R2 0.003)"),
 ("Under firm and year-quarter fixed effects the coefficient keeps its sign but is insignificant: LPM 0.0644 (SE 0.05076, n.s.).",
  "Under firm and year-quarter fixed effects the coefficient keeps its sign but is insignificant: LPM 0.0644 (SE 0.05076, n.s.; within-R2 0.059)."),
 ("0.0644 n.s. (FE-LPM, Firm + Year-Qtr FE; fe_results.json TEST_B; SE 0.05076, p .205, N 1,063, firms 563)",
  "0.0644 n.s. (FE-LPM, Firm + Year-Qtr FE; fe_results.json TEST_B; SE 0.05076, p .205, N 1,063, firms 563; within-R2 0.059)"),
]
def apply(path):
    raw=path.read_text(encoding="utf-8")
    n=0
    for f,r in EDITS:
        c=raw.count(f); assert c==1, f"expected 1 occurrence, got {c}: {f[:50]}"
        raw=raw.replace(f,r); n+=1
    json.loads(raw)  # still valid
    return raw,n
draw,na=apply(DST); sraw,nb=apply(SRC)
print(f"placed edits={na} merged edits={nb}")
print("within-R2 0.003 in placed:", "within-R2 0.003" in draw, "| 0.059:", "within-R2 0.059" in draw)
print("MERGED==placed after edit:", draw==sraw)
assert draw==sraw, "MERGED != placed!"
if WRITE:
    DST.write_text(draw,encoding="utf-8"); SRC.write_text(sraw,encoding="utf-8")
    print("WRITTEN both.")
else:
    print("dry-run.")
