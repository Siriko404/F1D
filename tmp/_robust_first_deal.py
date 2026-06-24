import sys, glob, numpy as np, pandas as pd
from pathlib import Path
sys.path.insert(0, str(Path("scripts").resolve()))
import gen_empire_did_table as G

p, s, m = G.base_panel(), G.sdc(), G.manifest()

# identify cash firms with a 2nd cash deal, and gap to 2nd
cd = s[s["known"] & (s["pc"]>=50)].copy()
cd["dq"]=cd["da"].dt.year*4+(cd["da"].dt.quarter-1)
cd=cd.merge(m,on="c6",how="inner")
gq=cd.groupby("gvkey")["dq"].apply(lambda x:sorted(set(x)))
multi=set(gq[gq.apply(len)>=2].index)                       # any 2nd cash deal
near8=set(gq[gq.apply(lambda x: len(x)>=2 and (x[1]-x[0])<=8)].index)  # 2nd within 8q

def run_cash(restrict=None, label=""):
    q,n = G.build(p, s, m, s["pc"]>=50)
    if restrict is not None:
        q = q[~q["gvkey"].isin(restrict)].copy()
    r = G.run(q, "UncResCEO")
    print(f"{label:38} beta={r['beta']:+.5f} se={r['se']:.5f} p2={r['p2']:.3f} N={r['n']:,} firms={r['n_firms']}")
    return r

print("=== H1 cash run-up on UncResCEO -- robustness to second deals ===")
run_cash(None,                "(1) main (all treated cash firms)")
run_cash(multi,               "(2) drop ANY firm w/ 2nd cash deal")
run_cash(near8,               "(3) drop firms w/ 2nd deal within 8q")
