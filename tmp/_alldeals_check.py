import sys, numpy as np, pandas as pd
from pathlib import Path
sys.path.insert(0, str(Path("scripts").resolve()))
import gen_empire_did_table as G

p, s, m = G.base_panel(), G.sdc(), G.manifest()
AFT=3
cd = s[s["known"] & (s["pc"]>=50)].copy()
cd["dq"]=cd["da"].dt.year*4+(cd["da"].dt.quarter-1)
cd=cd.merge(m,on="c6",how="inner")
deals=cd.groupby("gvkey")["dq"].apply(lambda x:sorted(set(x))).to_dict()

def classify(g,cq):
    D=deals.get(g)
    if not D: return "base_never"
    is_pre=(cq+1) in D
    aft=any(0<=cq-d<=AFT for d in D)
    contam=any((cq-2)<=d<=cq for d in D)
    if is_pre and not contam: return "treat"
    if aft: return "drop"
    if is_pre and contam: return "drop"
    # baseline for an acquirer firm: is it BEFORE first deal or AFTER (re-included post)?
    return "base_pre" if cq < D[0] else "base_post"

p=p.copy()
p["cls"]=[classify(g,cq) for g,cq in zip(p["gvkey"],p["cq"])]
vc=p["cls"].value_counts()
print("Row classes (all-deals design):")
for k in ["treat","base_never","base_pre","base_post","drop"]:
    print(f"  {k:11}: {int(vc.get(k,0)):,}")

# Check 2: mean UncResCEO of re-included POST baseline vs PRE/never baseline
u=p.dropna(subset=["UncResCEO"])
for k in ["base_never","base_pre","base_post","treat"]:
    sub=u[u["cls"]==k]["UncResCEO"]
    print(f"  mean UncResCEO [{k:11}] = {sub.mean():+.5f}  (n={len(sub):,})")
