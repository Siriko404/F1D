# -*- coding: utf-8 -*-
"""WIRE step 2: append a §4.5 forward-pointer to each target paragraph's `serves`.
Never touches any `statement` or any other field. Format B serves=list (append element);
Format A (§2.4) serves=string (append clause). GATE asserts statements + all non-serves
content byte-identical. Pass 'WRITE' to write. dry-run default."""
import json, sys, copy
from pathlib import Path
FIN = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D-phase3\docs\Thesis\rewrite\_final")
WRITE = len(sys.argv) > 1 and sys.argv[1] == "WRITE"

# Format-B targets: file -> {para_id: pointer-string-to-append-to-serves-list}
FB = {
 "section3.2": {"3.2-PARA2": "Robustified across all deals in §4.5 (run-up survives; see 4.5-PARA1)."},
 "section3.3": {
   "3.3-PARA3": "Robustified across all deals in §4.5 (matched-universe round-trip survives; see 4.5-PARA2).",
   "3.3-PARA4": "Robustified across all deals in §4.5 (round-trip magnitude survives; see 4.5-PARA2).",
   "3.3-PARA5": "Robustified across all deals in §4.5 (cash-arm round-trip survives; see 4.5-PARA2).",
 },
 "section3.4": {
   "3.4-PARA1": "Robustified across all deals in §4.5 (descriptive cash/stock asymmetry holds; see 4.5-PARA2).",
   "3.4-PARA3": "Robustified across all deals in §4.5 (formal cash-minus-stock Wald holds and is larger, 0.1056**; see 4.5-PARA3).",
   "3.4-PARA4": "Across all deals in §4.5 the war-chest CAUSE stays insignificant (0.0071 n.s.; mechanism-open preserved); see 4.5-PARA3.",
 },
}
# Format-A target: §2.4 paragraph 'P5' serves is a STRING -> append clause
FA_FILE = "section2.4"; FA_PARA = "P5"
FA_CLAUSE = (" The first-deal contamination threat disclosed here (P5.2) is addressed by the all-deals "
             "robustness in §4.5, where the run-up, timing, and cash-concentration results survive "
             "dropping the first-deal restriction.")

FORBID = ["suppress","dampen","strict specificity","detect "]
fails=[]
def ck(n,ok,det=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {n}"+(f" -- {det}" if det and not ok else ""))
    if not ok: fails.append(n)

def statements_of(d):
    out={}
    pl=d["paragraphs"]; items = pl.items() if isinstance(pl,dict) else [(p["para_id"],p) for p in pl]
    for pid,pa in items:
        for pr in (pa.get("propositions") or pa.get("proposition_chain") or []):
            out[pr.get("prop_id")] = pr.get("statement")
    return out

print("== WIRE GATE (append §4.5 forward-pointer to serves)"+(" + WRITE" if WRITE else " dry-run")+" ==\n")
edits=[]  # (file, para, before, after)
to_write={}

# ---- Format B ----
for fname, targets in FB.items():
    p = FIN/f"{fname}_paragraph_ledger.json"
    d = json.load(open(p,encoding="utf-8"))
    before_stmts = statements_of(d)
    pre = copy.deepcopy(d)
    by = {pa["para_id"]: pa for pa in d["paragraphs"]}
    for pid, ptr in targets.items():
        ck(f"{fname} {pid} exists", pid in by)
        if pid not in by: continue
        pa = by[pid]
        ck(f"{fname} {pid} serves is a list", isinstance(pa.get("serves"), list))
        ck(f"{fname} {pid} pointer not already present", ptr not in pa["serves"])
        for w in FORBID: ck(f"{fname} {pid} no FORBID '{w}'", w not in ptr.lower())
        b = list(pa["serves"]); pa["serves"] = b + [ptr]
        edits.append((fname, pid, b, pa["serves"]))
    # invariants
    ck(f"{fname}: all statements byte-identical", statements_of(d)==before_stmts)
    # every paragraph: only serves may differ; non-target paras fully identical
    by_pre={pa["para_id"]:pa for pa in pre["paragraphs"]}
    for pid,pa in by.items():
        if pid in targets:
            pre_no = {k:v for k,v in by_pre[pid].items() if k!="serves"}
            now_no = {k:v for k,v in pa.items() if k!="serves"}
            ck(f"{fname} {pid}: only serves changed", pre_no==now_no)
        else:
            ck(f"{fname} {pid}: untouched", by_pre[pid]==pa)
    to_write[p]=d

# ---- Format A (§2.4 P5, serves is string) ----
p = FIN/f"{FA_FILE}_paragraph_ledger.json"
d = json.load(open(p,encoding="utf-8"))
before_stmts = statements_of(d); pre=copy.deepcopy(d)
pa = d["paragraphs"][FA_PARA]
ck(f"{FA_FILE} {FA_PARA} serves is a string", isinstance(pa.get("serves"), str))
ck(f"{FA_FILE} {FA_PARA} clause not already present", FA_CLAUSE.strip() not in pa.get("serves",""))
for w in FORBID: ck(f"{FA_FILE} no FORBID '{w}'", w not in FA_CLAUSE.lower())
b = pa["serves"]; pa["serves"] = b + FA_CLAUSE
edits.append((FA_FILE, FA_PARA, [b], [pa["serves"]]))
ck(f"{FA_FILE}: all statements byte-identical", statements_of(d)==before_stmts)
for pid in d["paragraphs"]:
    if pid==FA_PARA:
        pre_no={k:v for k,v in pre["paragraphs"][pid].items() if k!="serves"}
        now_no={k:v for k,v in d["paragraphs"][pid].items() if k!="serves"}
        ck(f"{FA_FILE} {pid}: only serves changed", pre_no==now_no)
    else:
        ck(f"{FA_FILE} {pid}: untouched", pre["paragraphs"][pid]==d["paragraphs"][pid])
to_write[p]=d

# ---- show before->after ----
print("\n--- exact serves edits (before -> after) ---")
for fname,pid,b,a in edits:
    print(f"\n  [{fname} {pid}] serves:")
    if isinstance(b,list) and isinstance(a,list) and len(a)==len(b)+1 and fname!=FA_FILE:
        print(f"    + APPEND: {a[-1]}")
    else:
        print(f"    BEFORE: {b[0][:120]}...")
        print(f"    AFTER : ...{a[0][-180:]}")

print("\n"+"="*52)
if fails:
    print(f"GATE FAILED ({len(fails)}): {fails}\nNO WRITE."); sys.exit(1)
print(f"GATE PASSED. 8 serves-appends across 4 files; 0 statements touched.")
if WRITE:
    for p,d in to_write.items():
        json.dump(d, open(p,"w",encoding="utf-8"), indent=2, ensure_ascii=False)
    print("WRITTEN.")
else:
    print("Dry-run only. Re-run with WRITE.")
