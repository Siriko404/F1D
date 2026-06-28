# -*- coding: utf-8 -*-
"""Advisor's 2 verifications: (1) within-R2 of both FE-LPMs; (2) TRUE dual-arm firm count
(firms with >=1 cash AND >=1 stock deal) — the load-bearing 'make both' figure for B."""
import sys, json, warnings
warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np, pandas as pd, os
ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
sys.path.insert(0, str(ROOT/"scripts")); os.chdir(ROOT)
import gen_empire_did_table as G
CTRL=G.CTRL; RHS=["UncResCEO"]+CTRL
FE=json.loads(Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D-phase3\tmp\fe_results.json").read_text())

print("== (1) within-R2 of FE-LPMs ==")
print(f"  TEST A (deal-next):  within-R2 = {FE['TEST_A']['r2_within']:.5f}")
print(f"  TEST B (cash/stock): within-R2 = {FE['TEST_B']['r2_within']:.5f}")

# rebuild TEST B panel to count dual-arm firms
p, s, m = G.base_panel(), G.sdc(), G.manifest()
d = s[s["known"]].copy(); d["dq"]=d["da"].dt.year*4+(d["da"].dt.quarter-1)
d = d.merge(m,on="c6",how="inner"); d["arm"]=np.where(d["pc"]>=50,"cash",np.where(d["ps"]>=50,"stock","other"))
alld=d[d["arm"].isin(["cash","stock"])][["gvkey","dq","arm"]]
b=p.merge(alld,on="gvkey",how="inner"); b=b[b["cq"]==b["dq"]-1].copy()
b=b[~(b.groupby(["gvkey","cq"])["arm"].transform("nunique")>1)].copy()
b["cash"]=(b["arm"]=="cash").astype(float)
bB=b.replace([np.inf,-np.inf],np.nan).dropna(subset=["cash"]+RHS).copy()

g=bB.groupby("gvkey")["cash"]
has_cash=g.max()==1; has_stock=g.min()==0
dual=(has_cash & has_stock)
ntot=bB["gvkey"].nunique(); ndual=int(dual.sum())
print("\n== (2) TRUE dual-arm firms (>=1 cash AND >=1 stock deal) ==")
print(f"  firms total: {ntot}")
print(f"  dual-arm (both cash & stock): {ndual}  ({ndual/ntot:.1%})")
print(f"  -> these are the ONLY firms that identify B within-firm; the prose '~9% make both' is {'CORRECT' if abs(ndual/ntot-0.09)<0.02 else 'OFF -> fix to '+f'{ndual/ntot:.0%}'}")
