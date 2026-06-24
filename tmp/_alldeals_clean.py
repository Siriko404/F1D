import sys, numpy as np, pandas as pd
from pathlib import Path
sys.path.insert(0, str(Path("scripts").resolve()))
import gen_empire_did_table as G

p, s, m = G.base_panel(), G.sdc(), G.manifest()

# all cash-deal quarters per firm (gvkey)
cd = s[s["known"] & (s["pc"]>=50)].copy()
cd["dq"]=cd["da"].dt.year*4+(cd["da"].dt.quarter-1)
cd=cd.merge(m,on="c6",how="inner")
deals = cd.groupby("gvkey")["dq"].apply(lambda x: sorted(set(x))).to_dict()

AFT = 3   # quarters of post-announcement aftermath to drop (deal qtr + 3)
def classify(g, cq):
    D = deals.get(g)
    if not D:
        return "base"                       # never-acquirer -> baseline
    is_pre = (cq+1) in D                     # e=-1 for some deal
    aftermath = any(0 <= cq-d <= AFT for d in D)   # within a deal's aftermath
    # pre-window e=-3..-1 of deal (cq+1) polluted by a DIFFERENT earlier deal in {cq-2..cq}
    contam = any((cq-2) <= d <= cq for d in D)
    if is_pre and not contam:
        return "treat"
    if aftermath:
        return "drop"                        # contaminated post / aftermath
    if is_pre and contam:
        return "drop"                        # contaminated run-up -> drop the event
    return "base"

p = p.copy()
p["cls"] = [classify(g, cq) for g, cq in zip(p["gvkey"], p["cq"])]
q = p[p["cls"] != "drop"].copy()
q["PreAnnounceQtr"] = (q["cls"]=="treat").astype(float)

n_treat = int(q["PreAnnounceQtr"].sum())
# how many treatment EVENTS exist all-in vs dropped as contaminated
all_pre = sum(1 for g,D in deals.items() for d in D)   # rough event count
print(f"clean treatment quarters kept : {n_treat}")
print(f"rows dropped (aftermath/contam): {(p['cls']=='drop').sum()}")
r = G.run(q, "UncResCEO")
print(f"\nALL cash deals, drop contaminated pre-window:")
print(f"  beta={r['beta']:+.5f}  se={r['se']:.5f}  p2={r['p2']:.3f}  N={r['n']:,}  firms={r['n_firms']}")
print(f"\n(compare) first-deal-only main: beta=+0.04609 p2=0.007 N=27,622")
