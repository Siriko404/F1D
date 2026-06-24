"""
Table 5.3 (matched round-trip event study, two clocks) rebuilt for ALL payment types.
Two designs:
  (A) FIRST deal of any type sets the clock (mirrors 5.3's first-deal design).
  (B) ALL deals stacked: every acquisition is its own event; a firm-quarter claimed by
      two deals' windows is dropped (pre3-contaminated dropped).
Outcomes: UncResCEO (col 1) + CashRatio (col 2, +lag), matched sample (both present).
Supervisor artifact -- NOT in the thesis.
"""
import glob, importlib.util, json
import numpy as np, pandas as pd
from pathlib import Path
ROOT = Path(".").resolve()
def _imp(n, rel):
    sp=importlib.util.spec_from_file_location(n, ROOT/rel); mod=importlib.util.module_from_spec(sp); sp.loader.exec_module(mod); return mod
edt = _imp("edt","src/f1d/econometric/empire_drop_test.py")
edm = _imp("edm","src/f1d/econometric/empire_drop_matched_universe.py")
BINS, CTRL, POST_CAP = edt.BINS, edt.CTRL, 4
def st(p): return "***" if p<.01 else ("**" if p<.05 else ("*" if p<.10 else ""))
def C(b,p):
    s=st(p); return (r"\textbf{"+f"{b:.4f}"+r"}$^{"+s+r"}$") if s else f"{b:.4f}"

p = edt.base_panel().sort_values(["gvkey","cq"])
p["CashRatio_lag"] = p.groupby("gvkey")["CashRatio"].shift(1)
_pcq = p.groupby("gvkey")["cq"].shift(1)
p.loc[_pcq != p["cq"]-1, "CashRatio_lag"] = np.nan
m = edt.manifest(); s = edt.sdc()
ALL = pd.Series(True, index=s.index)            # all payment types

# deals of ANY type per firm, with close/withdraw qtrs
cd = s[s["known"] & ALL].copy()
cd["dq"]=edt._qtr(cd["da"]); cd["ceq"]=edt._qtr(cd["de"]); cd["wq"]=edt._qtr(cd["dw"])
cd.loc[cd["ceq"]<cd["dq"],"ceq"]=np.nan
cd = cd.merge(m, on="c6", how="inner")
deals={}
for g,dq,ceq,wq,stat in zip(cd["gvkey"],cd["dq"],cd["ceq"],cd["wq"],cd["status"]):
    deals.setdefault(g,[]).append((int(dq),(None if pd.isna(ceq) else int(ceq)),(None if pd.isna(wq) else int(wq)),stat))

def claim(cq, dl):
    dq,ceq,wq,stat=dl; e=cq-dq
    if e==-2: return "PRE2"
    if e==-1: return "PRE1"
    if 0<=e<=POST_CAP:
        if stat=="Withdrawn" and wq is not None and cq>=wq: return None
        return "POST" if (ceq is not None and cq>=ceq) else "GAP"
    return None

def run_design(panel):
    need=["UncResCEO","CashRatio","CashRatio_lag"]+BINS+CTRL
    d=panel.replace([np.inf,-np.inf],np.nan).dropna(subset=need).copy()
    res={dv:edm.run_on(d,dv,add_cash_lag=(dv=="CashRatio")) for dv in ("UncResCEO","CashRatio")}
    return res, len(d), int(d["gvkey"].nunique())

# (A) FIRST deal of any type
qa,_ = edt.build_event(p, s, m, ALL)
resA,nA,fA = run_design(qa)

# (B) ALL deals stacked, drop quarters claimed by 2+ deals
cls=[]
for g,cq in zip(p["gvkey"],p["cq"]):
    cl=[c for c in (claim(cq,dl) for dl in deals.get(g,[])) if c]
    # 1 claim -> that bin; 2+ -> contaminated drop; else baseline UNLESS post-completion of any deal
    if len(cl)==1: cls.append(cl[0])
    elif len(cl)>=2: cls.append("DROP")
    elif any(dl[1] is not None and cq>=dl[1] for dl in deals.get(g,[])): cls.append("DROP")
    else: cls.append("BASE")
qb=p.copy(); qb["cls"]=cls; qb=qb[qb["cls"]!="DROP"].copy()
for b in BINS: qb[b]=(qb["cls"]==b).astype(float)
resB,nB,fB = run_design(qb)

print("=== ALL-TYPES round-trip (5.3 design) ===")
for lab,res,n,f in (("A first-deal",resA,nA,fA),("B all-deals stacked",resB,nB,fB)):
    r=res["UncResCEO"]
    print(f"{lab:22} N={n:,} firms={f}  PRE1={r['bins']['PRE1']['b']:+.4f}({st(r['bins']['PRE1']['p2'])}) "
          f"GAP={r['bins']['GAP']['b']:+.4f} PRE1-GAP={r['pre1_gap']['diff']:+.4f}({st(r['pre1_gap']['p2'])}) "
          f"PRE1-POST={r['pre1_post']['diff']:+.4f}({st(r['pre1_post']['p2'])})")

# ---------- render: 5.3 format, 4 cols (A UncRes/CashR | B UncRes/CashR) ----------
def line(get):
    return " & ".join([get(resA["UncResCEO"]),get(resA["CashRatio"]),get(resB["UncResCEO"]),get(resB["CashRatio"])])
L=[r"\documentclass[11pt]{article}",
   r"\usepackage[letterpaper,margin=0.8in]{geometry}\usepackage{newtxtext,newtxmath}\usepackage{booktabs,amsmath,float}",
   r"\begin{document}\pagestyle{empty}",
   r"\begin{table}[H]\centering",
   r"\caption{Round-Trip Event Study --- All Payment Types}",
   r"\small\begin{tabular}{lcccc}",
   r"\toprule",
   r" & \multicolumn{2}{c}{\textbf{(A) First deal, any type}} & \multicolumn{2}{c}{\textbf{(B) All deals stacked, any type}} \\",
   r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}",
   r" & UncResCEO & CashRatio & UncResCEO & CashRatio \\", r"\midrule"]
LBL={"PRE2":r"PRE2 ($t{-}2$, pre-trend)","PRE1":r"PRE1 ($t{-}1$, pre-announce)","GAP":r"GAP (announced, pre-close)","POST":r"POST (completed)"}
for b in BINS:
    L.append(f"{LBL[b]} & "+line(lambda r,b=b: C(r['bins'][b]['b'],r['bins'][b]['p2']))+r" \\")
    L.append(" & "+line(lambda r,b=b: f"({r['bins'][b]['se']:.4f})")+r" \\")
L.append(r"\midrule")
for k,lab in (("pre1_gap",r"Drop: PRE1 $-$ GAP"),("gap_post",r"Drop: GAP $-$ POST"),("pre1_post",r"Drop: PRE1 $-$ POST")):
    L.append(f"{lab} & "+line(lambda r,k=k: C(r[k]['diff'],r[k]['p2']))+r" \\")
    L.append(" & "+line(lambda r,k=k: f"({r[k]['se']:.4f})")+r" \\")
L.append(r"\midrule\multicolumn{5}{l}{\textit{Controls}} \\")
for c in CTRL:
    L.append(f"{c} & "+line(lambda r,c=c: C(r['controls'][c]['b'],r['controls'][c]['p2']) if c in r.get('controls',{}) else "---")+r" \\")
    L.append(" & "+line(lambda r,c=c: f"({r['controls'][c]['se']:.4f})" if c in r.get('controls',{}) else "")+r" \\")
L.append(r"CashRatio$_{t-1}$ (partial adj.) & "+line(lambda r: C(r['lag']['b'],r['lag']['p2']) if 'lag' in r else "---")+r" \\")
L.append(" & "+line(lambda r: f"({r['lag']['se']:.4f})" if 'lag' in r else "")+r" \\")
L+=[r"\midrule",
    f"N & {nA:,} & {nA:,} & {nB:,} & {nB:,} \\\\",
    f"Firms & {fA:,} & {fA:,} & {fB:,} & {fB:,} \\\\",
    r"\bottomrule\end{tabular}",
    r"\begin{minipage}{\linewidth}\vspace{3pt}\footnotesize\textit{Notes:} $^{*}p<.10$, $^{**}p<.05$, $^{***}p<.01$ (two-tailed); SE clustered by firm.\end{minipage}",
    r"\end{table}", r"\end{document}"]
out = Path(sorted([d for d in glob.glob(str(ROOT/"outputs/econometric/firstdeal_robustness/*/")) if Path(d).is_dir()])[-1])
(out/"alltypes_53.tex").write_text("\n".join(L), encoding="utf-8")
print("wrote", out/"alltypes_53.tex")
