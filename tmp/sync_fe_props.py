# -*- coding: utf-8 -*-
"""Sync the FE result into the merged §4.5 logit props (RU-2=PARA1-b, CC-2=PARA3-b).
Mechanical append only (number + 'survives'/'keeps sign, n.s.'); interpretation -> FRAMING-TODO.
Re-runs the §4.5 placement GATE + asserts the FE numbers landed."""
import json, copy, re, sys
from pathlib import Path
RW = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D-phase3\docs\Thesis\rewrite")
F = RW/"_final"/"_proposals"/"section4.5_MERGED.json"
M = json.load(open(F, encoding="utf-8"))
def props(d): return [pr for p in d["paragraphs"] for pr in p.get("proposition_chain",[])]
byid = {pr["prop_id"]: pr for pr in props(M)}

RU2_ADD_ST = " It survives firm and year-quarter fixed effects: LPM 0.0078*** (SE 0.00275, N 39,557)."
RU2_ADD_N  = "0.0078*** (FE-LPM, Firm + Year-Qtr FE; fe_results.json TEST_A; SE 0.00275, N 39,557, firms 1,422)"
CC2_ADD_ST = " Under firm and year-quarter fixed effects the coefficient keeps its sign but is insignificant: LPM 0.0644 (SE 0.05076, n.s.)."
CC2_ADD_N  = "0.0644 n.s. (FE-LPM, Firm + Year-Qtr FE; fe_results.json TEST_B; SE 0.05076, p .205, N 1,063, firms 563)"

ru2, cc2 = byid["4.5-PARA1-b"], byid["4.5-PARA3-b"]
assert "0.0078" not in ru2["statement"], "RU-2 already synced"
ru2["statement"] = ru2["statement"].rstrip() + RU2_ADD_ST
ru2["numbers"] = list(ru2.get("numbers", [])) + [RU2_ADD_N]
cc2["statement"] = cc2["statement"].rstrip() + CC2_ADD_ST
cc2["numbers"] = list(cc2.get("numbers", [])) + [CC2_ADD_N]

# ---- GATE ----
ORDER=["prop_id","statement","role_in_paragraph","type","numbers","register_locks","evidence","depends_on"]
live=set()
for f in (RW/"_final").glob("section*_paragraph_ledger.json"):
    d=json.load(open(f,encoding="utf-8")); pc=d.get("paragraphs"); it=pc.values() if isinstance(pc,dict) else (pc or [])
    for pa in it:
        if isinstance(pa,dict):
            for pr in (pa.get("propositions") or pa.get("proposition_chain") or []):
                if isinstance(pr,dict) and pr.get("prop_id"): live.add(pr["prop_id"])
P=props(M); fails=[]
def ck(c,ok,msg):
    print(f"  [{'PASS' if ok else 'FAIL'}] {c}: {msg}")
    if not ok: fails.append(c)
ck("6 props", len(P)==6, f"{len(P)}")
ck("field-order", all(list(pr.keys())==ORDER for pr in P), "exact 8-key")
ck("final_prose empty", all(p.get('final_prose','')=='' for p in M['paragraphs']), "all empty")
ck("FE landed", "0.0078" in ru2["statement"] and "0.0644" in cc2["statement"], "RU-2 0.0078*** + CC-2 0.0644 n.s.")
unres=[(pr['prop_id'],x) for pr in P for x in (pr.get('depends_on') or []) if x not in live]
ck("depends_on resolves", not unres, f"{len(unres)} unresolved")
bad=re.compile(r'suppress|dampen|sits lower|below baseline',re.I); intp=re.compile(r'\bbecause\b|\bproves\b|\bmotivat',re.I)
hv=[pr['prop_id'] for pr in P if bad.search(pr['statement'])]; iv=[pr['prop_id'] for pr in P if intp.search(pr['statement'])]
ck("honesty/interp", not hv and not iv, f"honesty={hv} interp={iv}")
if fails: print("ABORT:",fails); sys.exit(1)
json.dump(M, open(F,"w",encoding="utf-8"), indent=2, ensure_ascii=False)
print("\nWROTE synced MERGED. RU-2 + CC-2 now carry the FE result.")
print("RU-2:", ru2["statement"][-95:])
print("CC-2:", cc2["statement"][-105:])
