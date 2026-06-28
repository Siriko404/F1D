# -*- coding: utf-8 -*-
"""Mechanical merge: B = base; apply A's 2 named patches (TI-2 depends_on, honest meta), GATE.
NOT a hand-blend. caveat-iii is FRAMING (not JSON). NO depends_on union. Then §4.5 placement GATE."""
import json, copy, re, sys
from pathlib import Path
RW = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D-phase3\docs\Thesis\rewrite")
PROP = RW/"_final"/"_proposals"
A = json.load(open(PROP/"section4.5_agentA.json", encoding="utf-8"))
B = json.load(open(PROP/"section4.5_agentB.json", encoding="utf-8"))
def props(d): return [pr for p in d["paragraphs"] for pr in p.get("proposition_chain",[])]
def byid(d): return {pr["prop_id"]: pr for pr in props(d)}

# ---- INSPECT (per-prop depends_on + CC-1 cause check) ----
print("== per-prop depends_on ==")
for pid in [pr["prop_id"] for pr in props(B)]:
    print(f"  {pid:12} A={byid(A).get(pid,{}).get('depends_on')}  B={byid(B).get(pid,{}).get('depends_on')}")
cc1 = byid(B)["4.5-PARA3-a"]
cc1_cites_cause = ("0.0071" in json.dumps(cc1.get("numbers",[])) or "0.0071" in cc1.get("statement",""))
print(f"\n  CC-1 (PARA3-a) cites the cause 0.0071? {cc1_cites_cause}")

# ---- BUILD: B base + named patches ----
M = copy.deepcopy(B)
Mid = byid(M)
# patch 1: TI-2 (PARA2-b) depends_on <- A's (Table 5.4's real arm-homes: 3.3-PARA5-a cash + 3.4-PARA1-a stock)
Mid["4.5-PARA2-b"]["depends_on"] = list(byid(A)["4.5-PARA2-b"]["depends_on"])
# CC-1 cause anchor: keep 3.4-PARA4-a ONLY if CC-1 actually cites the cause; else drop (advisor)
if not cc1_cites_cause and "3.4-PARA4-a" in (Mid["4.5-PARA3-a"].get("depends_on") or []):
    Mid["4.5-PARA3-a"]["depends_on"].remove("3.4-PARA4-a")
# patch 2: honest meta <- A's
M["_derived_from"] = A["_derived_from"]
for i,p in enumerate(M["paragraphs"]):
    p["prose_gate"]   = copy.deepcopy(A["paragraphs"][i]["prose_gate"])
    p["prose_status"] = A["paragraphs"][i]["prose_status"]

# ---- collect LIVE prop_ids (for depends_on resolution) ----
live=set()
for f in (RW/"_final").glob("section*_paragraph_ledger.json"):
    d=json.load(open(f,encoding="utf-8"))
    pc=d.get("paragraphs"); it=pc.values() if isinstance(pc,dict) else (pc or [])
    for pa in it:
        if isinstance(pa,dict):
            for pr in (pa.get("propositions") or pa.get("proposition_chain") or []):
                if isinstance(pr,dict) and pr.get("prop_id"): live.add(pr["prop_id"])

# ---- §4.5 PLACEMENT GATE ----
ORDER=["prop_id","statement","role_in_paragraph","type","numbers","register_locks","evidence","depends_on"]
P=props(M); fails=[]
def add(c,ok,msg):
    print(f"  [{'PASS' if ok else 'FAIL'}] {c}: {msg}");
    if not ok: fails.append(c)
add("Format-B", isinstance(M.get("paragraphs"),list) and M.get("section_id")=="4.5", f"section_id={M.get('section_id')}, paragraphs=list")
add("6 props", len(P)==6, f"{len(P)} props")
add("field-order", all(list(pr.keys())==ORDER for pr in P), "exact 8-key order")
add("final_prose empty", all(p.get('final_prose','')=='' for p in M['paragraphs']), "all empty")
HEAD={"0.0391","0.0086","0.0352","0.0401","0.1056","0.0613"}
got=set(m.group(0) for pr in P for n in [(pr.get('numbers') or [''])[0]] for m in [re.search(r'-?0\.\d{4}',n)] if m)
add("numbers==.tex", got==HEAD, f"headline set {'==' if got==HEAD else '!='} verified  {sorted(got)}")
deps=[(pr['prop_id'],x) for pr in P for x in (pr.get('depends_on') or [])]
unres=[(pid,x) for pid,x in deps if x not in live]
add("depends_on resolves", len(unres)==0, f"{len(unres)} unresolved in LIVE ledgers" + (f" {unres}" if unres else ""))
bad=re.compile(r'suppress|dampen|sits lower|below baseline',re.I); intp=re.compile(r'\bbecause\b|\bproves\b|\bmotivat',re.I)
hv=[pr['prop_id'] for pr in P if bad.search(pr.get('statement',''))]; iv=[pr['prop_id'] for pr in P if intp.search(pr.get('statement',''))]
add("honesty/interp", not hv and not iv, f"honesty={hv} interp={iv}")
add("meta honest", "74b7a0f8" not in M.get("_derived_from",""), f"_derived_from has no false provenance")

print("\n== PATCHED depends_on (final) ==")
for pr in P: print(f"  {pr['prop_id']:12} {pr.get('depends_on')}")

if fails:
    print("\nABORT — GATE FAILED:", fails); sys.exit(1)
json.dump(M, open(PROP/"section4.5_MERGED.json","w",encoding="utf-8"), indent=2, ensure_ascii=False)
print("\nGATE ALL PASS → wrote section4.5_MERGED.json")
