import sys, numpy as np, pandas as pd
from pathlib import Path
from scipy import stats
sys.path.insert(0, str(Path("scripts").resolve()))
import gen_empire_did_table as G
from linearmodels.panel import PanelOLS

p, s, m = G.base_panel(), G.sdc(), G.manifest()
AFT = 3

def deal_q(mask):
    cd = s[s["known"] & mask].copy()
    cd["dq"]=cd["da"].dt.year*4+(cd["da"].dt.quarter-1)
    cd=cd.merge(m,on="c6",how="inner")
    return cd.groupby("gvkey")["dq"].apply(lambda x: sorted(set(x))).to_dict()

cashD = deal_q(s["pc"]>=50)
stockD = deal_q(s["ps"]>=50)

def pre(D,g,cq):    # clean e=-1 to an arm deal: deal next qtr, no same-arm deal in cq-2..cq
    Dg=D.get(g)
    if not Dg: return False
    return ((cq+1) in Dg) and not any((cq-2)<=d<=cq for d in Dg)
def after(g,cq):    # within AFT qtrs of ANY deal (cash or stock)
    return any(0<=cq-d<=AFT for d in (cashD.get(g,[])+stockD.get(g,[])))

rows=[]
for g,cq in zip(p["gvkey"],p["cq"]):
    cpre,spre,aft = pre(cashD,g,cq), pre(stockD,g,cq), after(g,cq)
    if cpre and spre: rows.append("drop")
    elif cpre and not aft: rows.append("cash")
    elif spre and not aft: rows.append("stock")
    elif aft: rows.append("drop")
    else: rows.append("base")
p=p.copy(); p["cls"]=rows
q=p[p["cls"]!="drop"].copy()
q["PreAnnCash"]=(q["cls"]=="cash").astype(float)
q["PreAnnStock"]=(q["cls"]=="stock").astype(float)

# ---- single stock arm (all clean stock deals) ----
def run_arm(col):
    need=[ "UncResCEO", col]+G.CTRL
    d=q.replace([np.inf,-np.inf],np.nan).dropna(subset=need).set_index(["gvkey","cq"])
    f=f"UncResCEO ~ 1 + {col} + "+" + ".join(G.CTRL)+" + EntityEffects + TimeEffects"
    mod=PanelOLS.from_formula(f,data=d,drop_absorbed=True).fit(cov_type="clustered",cluster_entity=True)
    return mod, float(mod.params[col]), float(mod.std_errors[col]), float(mod.pvalues[col])

ms,bs,ses,ps_ = run_arm("PreAnnStock")
print(f"STOCK arm (all clean stock deals): beta={bs:+.5f} se={ses:.5f} p2={ps_:.3f} n_treat={int(q['PreAnnStock'].sum())}")

# ---- pooled: both treatments, Wald beta_c - beta_s > 0 ----
need=["UncResCEO","PreAnnCash","PreAnnStock"]+G.CTRL
d=q.replace([np.inf,-np.inf],np.nan).dropna(subset=need).set_index(["gvkey","cq"])
f="UncResCEO ~ 1 + PreAnnCash + PreAnnStock + "+" + ".join(G.CTRL)+" + EntityEffects + TimeEffects"
mod=PanelOLS.from_formula(f,data=d,drop_absorbed=True).fit(cov_type="clustered",cluster_entity=True)
bc,bsk=float(mod.params["PreAnnCash"]),float(mod.params["PreAnnStock"])
V=mod.cov
vc,vs=float(V.loc["PreAnnCash","PreAnnCash"]),float(V.loc["PreAnnStock","PreAnnStock"])
cov=float(V.loc["PreAnnCash","PreAnnStock"])
diff=bc-bsk; se_d=np.sqrt(vc+vs-2*cov); z=diff/se_d
p1=stats.norm.sf(z); p2=2*stats.norm.sf(abs(z))
print(f"\nPOOLED all-deals:")
print(f"  cash  beta={bc:+.5f} p2={float(mod.pvalues['PreAnnCash']):.3f}")
print(f"  stock beta={bsk:+.5f} p2={float(mod.pvalues['PreAnnStock']):.3f}")
print(f"  WALD cash-stock diff={diff:+.5f} se={se_d:.5f} z={z:.2f} p1(one-tail)={p1:.3f} p2={p2:.3f}")
print(f"  N={int(mod.nobs):,} firms={d.reset_index()['gvkey'].nunique()}")
