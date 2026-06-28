# -*- coding: utf-8 -*-
"""Drop ONLY the 7th wire: the §3.4-PARA4 serves pointer. Assert everything else
byte-identical (statements, other paras, the OTHER two §3.4 wires PARA1/PARA3). WRITE arg to apply."""
import json,sys,copy
from pathlib import Path
P=Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D-phase3\docs\Thesis\rewrite\_final\section3.4_paragraph_ledger.json")
WRITE=len(sys.argv)>1 and sys.argv[1]=="WRITE"
TARGET="Across all deals in §4.5 the war-chest CAUSE stays insignificant (0.0071 n.s.; mechanism-open preserved); see 4.5-PARA3."
KEEP1="Robustified across all deals in §4.5 (descriptive cash/stock asymmetry holds; see 4.5-PARA2)."   # PARA1
KEEP3="Robustified across all deals in §4.5 (formal cash-minus-stock Wald holds and is larger, 0.1056**; see 4.5-PARA3)."  # PARA3

d=json.load(open(P,encoding="utf-8")); pre=copy.deepcopy(d)
def stmts(x): return {pr["prop_id"]:pr["statement"] for pa in x["paragraphs"] for pr in pa["proposition_chain"]}
by={pa["para_id"]:pa for pa in d["paragraphs"]}
p4=by["3.4-PARA4"]
fails=[]
def ck(n,ok):
    print(f"  [{'PASS' if ok else 'FAIL'}] {n}");  fails.append(n) if not ok else None

ck("target pointer present before", TARGET in p4["serves"])
before_len=len(p4["serves"])
p4["serves"]=[s for s in p4["serves"] if s!=TARGET]
ck("exactly one element removed", len(p4["serves"])==before_len-1)
ck("target gone after", TARGET not in p4["serves"])
ck("PARA4 original serves still there", "delivers the failing CAUSE leg; keeps the war-chest mechanism open (mechanism-open lock)" in p4["serves"])
ck("other §3.4 wire PARA1 still present", KEEP1 in by["3.4-PARA1"]["serves"])
ck("other §3.4 wire PARA3 still present", KEEP3 in by["3.4-PARA3"]["serves"])
ck("all statements byte-identical", stmts(d)==stmts(pre))
# only PARA4 serves changed; every other paragraph fully identical
preby={pa["para_id"]:pa for pa in pre["paragraphs"]}
for pid,pa in by.items():
    if pid=="3.4-PARA4":
        ck("PARA4: only serves changed", {k:v for k,v in pa.items() if k!="serves"}=={k:v for k,v in preby[pid].items() if k!="serves"})
    else:
        ck(f"{pid}: untouched", pa==preby[pid])
print("="*46)
if fails: print("FAILED",fails); sys.exit(1)
print("GATE PASSED. 1 element removed; 6 wires remain.")
if WRITE:
    json.dump(d,open(P,"w",encoding="utf-8"),indent=2,ensure_ascii=False)
    raw=P.read_text(encoding="utf-8")
    print("WRITTEN. target absent:",TARGET not in raw,"| §ok:", "§4.5" in raw and "�" not in raw)
else: print("dry-run")
