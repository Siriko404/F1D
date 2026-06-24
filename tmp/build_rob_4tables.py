"""
Robustness PDF: thesis Tables 5.2/5.3/5.4/5.5 rebuilt, each with THESIS columns +
ALL-DEALS columns side by side, in the thesis table format. Supervisor artifact (not in thesis).

Thesis numbers READ from each suite's summary.json. All-deals numbers computed by stacking
EVERY qualifying deal as an event (run-up: single e=-1; event studies: PRE2/PRE1/GAP/POST per
deal) and dropping any firm-quarter claimed by >1 deal's window (contamination), plus same-arm
contaminated run-ups. Reuses the thesis generators' own run/estimation functions.

Run: python tmp/build_rob_4tables.py
"""
import glob, json, importlib.util
import numpy as np, pandas as pd
from pathlib import Path
from scipy import stats
ROOT = Path(".").resolve()

def _imp(name, rel):
    sp = importlib.util.spec_from_file_location(name, ROOT/rel); mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod); return mod
import sys; sys.path.insert(0, str(ROOT/"scripts"))
import gen_empire_did_table as G
cx  = _imp("cx",  "src/f1d/econometric/empire_cashspec_interaction.py")
edt = _imp("edt", "src/f1d/econometric/empire_drop_test.py")
edm = _imp("edm", "src/f1d/econometric/empire_drop_matched_universe.py")

BINS, CTRL = edt.BINS, edt.CTRL
POST_CAP = 4
def latest(p): return sorted(glob.glob(str(ROOT/p)))[-1]
def J(p): return json.load(open(p, encoding="utf-8"))
def st(p): return "***" if p<.01 else ("**" if p<.05 else ("*" if p<.10 else ""))
def C(b,p):
    s=st(p); return (r"\textbf{"+f"{b:.4f}"+r"}$^{"+s+r"}$") if s else f"{b:.4f}"
def bget(d): return d["b"] if "b" in d else d["beta"]   # edm uses 'b', edt uses 'beta'

# ---------------- base panels ----------------
pe = edt.base_panel()                          # file/gvkey/cq/CashRatio/CTRL/UncResCEO
pe = pe.sort_values(["gvkey","cq"])
pe["CashRatio_lag"] = pe.groupby("gvkey")["CashRatio"].shift(1)
_pcq = pe.groupby("gvkey")["cq"].shift(1)
pe.loc[_pcq != pe["cq"]-1, "CashRatio_lag"] = np.nan
m = edt.manifest(); s = edt.sdc()

def deals_for(mask):
    cd = s[s["known"] & mask].copy()
    cd["dq"] = edt._qtr(cd["da"]); cd["ceq"] = edt._qtr(cd["de"]); cd["wq"] = edt._qtr(cd["dw"])
    cd.loc[cd["ceq"] < cd["dq"], "ceq"] = np.nan
    cd = cd.merge(m, on="c6", how="inner")
    d = {}
    for g, dq, ceq, wq, statrow in zip(cd["gvkey"], cd["dq"], cd["ceq"], cd["wq"], cd["status"]):
        d.setdefault(g, []).append((int(dq), (None if pd.isna(ceq) else int(ceq)),
                                    (None if pd.isna(wq) else int(wq)), statrow))
    return d

cashD, stockD = deals_for(s["pc"]>=50), deals_for(s["ps"]>=50)

def claim(cq, deal):
    dq, ceq, wq, status = deal
    e = cq - dq
    if e == -2: return "PRE2"
    if e == -1: return "PRE1"
    if 0 <= e <= POST_CAP:
        if status == "Withdrawn" and wq is not None and cq >= wq: return None
        if ceq is not None and cq >= ceq: return "POST"
        return "GAP"
    return None

def stacked_event(panel, D):
    """assign each firm-qtr to a bin from the NEAREST claiming deal; drop if 2+ deals claim it."""
    cls = []
    for g, cq in zip(panel["gvkey"], panel["cq"]):
        claims = [c for c in (claim(cq, dl) for dl in D.get(g, [])) if c]
        if len(claims) == 1: cls.append(claims[0])
        elif len(claims) >= 2: cls.append("DROP")
        # would-be baseline: drop if on/after ANY deal's COMPLETION (no post-completion quarter in baseline)
        elif any(dl[1] is not None and cq >= dl[1] for dl in D.get(g, [])): cls.append("DROP")
        else: cls.append("BASE")
    out = panel.copy(); out["cls"] = cls
    out = out[out["cls"] != "DROP"].copy()
    for b in BINS: out[b] = (out["cls"] == b).astype(float)
    return out

# ================= 5.3 MATCHED (cash arm, UncRes + CashRatio, shared sample) =================
q53 = stacked_event(pe, cashD)
need = ["UncResCEO","CashRatio","CashRatio_lag"] + BINS + CTRL
d53 = q53.replace([np.inf,-np.inf],np.nan).dropna(subset=need).copy()
ad53 = {dv: edm.run_on(d53, dv, add_cash_lag=(dv=="CashRatio")) for dv in ("UncResCEO","CashRatio")}
ad53_n, ad53_f = len(d53), int(d53["gvkey"].nunique())

# ================= 5.4 PLACEBO (cash + stock arms, UncRes) =================
def run_arm_bins(D):
    q = stacked_event(pe, D)
    return edt.run_bins(q, "UncResCEO")
ad54 = {"cash:UncResCEO": run_arm_bins(cashD), "stock:UncResCEO": run_arm_bins(stockD)}

# ================= 5.5 CASHSPEC (pooled both arms) =================
def pooled_all():
    af = lambda g,cq: any(dl[1] is not None and cq>=dl[1] for dl in (cashD.get(g,[])+stockD.get(g,[])))
    def cpre(D,g,cq):
        Dg=D.get(g); return bool(Dg) and ((cq+1) in [dl[0] for dl in Dg]) and not any((cq-2)<=dl[0]<=cq for dl in Dg)
    rows=[]
    for g,cq in zip(pe["gvkey"],pe["cq"]):
        c,st_,a = cpre(cashD,g,cq), cpre(stockD,g,cq), af(g,cq)
        if c and st_: rows.append("drop")
        elif c and not a: rows.append("cash")
        elif st_ and not a: rows.append("stock")
        elif a: rows.append("drop")
        else: rows.append("base")
    q=pe.copy(); q["cls"]=rows; q=q[q["cls"]!="drop"].copy()
    q["PreAnn_cash"]=(q["cls"]=="cash").astype(float); q["PreAnn_stock"]=(q["cls"]=="stock").astype(float)
    return q
q55 = pooled_all()
ad55 = {"UncResCEO": cx.run(q55,"UncResCEO",restrict_uncres=True),
        "CashRatio_matched": cx.run(q55,"CashRatio",restrict_uncres=True,add_cash_lag=True),
        "CashRatio_full": cx.run(q55,"CashRatio",restrict_uncres=False,add_cash_lag=True)}

# ================= 5.2 RUN-UP (single e=-1, cash+stock arms, 4 DVs) =================
def runup_arm(D):
    af = lambda g,cq: any(dl[1] is not None and cq>=dl[1] for dl in D.get(g,[]))
    def cpre(g,cq):
        Dg=D.get(g); return bool(Dg) and ((cq+1) in [dl[0] for dl in Dg]) and not any((cq-2)<=dl[0]<=cq for dl in Dg)
    rows=[("treat" if cpre(g,cq) else ("drop" if af(g,cq) else "base")) for g,cq in zip(pe["gvkey"],pe["cq"])]
    q=pe.copy(); q["cls"]=rows; q=q[q["cls"]!="drop"].copy()
    q["PreAnnounceQtr"]=(q["cls"]=="treat").astype(float)
    return q
# run-up needs the score-based DVs (CashScrutiny) from G.base_panel; merge them in
gp = G.base_panel()[["file_name","CashScrutiny","HighCashScrutiny"]]
pe2 = pe.merge(gp, on="file_name", how="left")
def runup_arm2(D):
    af = lambda g,cq: any(dl[1] is not None and cq>=dl[1] for dl in D.get(g,[]))
    def cpre(g,cq):
        Dg=D.get(g); return bool(Dg) and ((cq+1) in [dl[0] for dl in Dg]) and not any((cq-2)<=dl[0]<=cq for dl in Dg)
    rows=[("treat" if cpre(g,cq) else ("drop" if af(g,cq) else "base")) for g,cq in zip(pe2["gvkey"],pe2["cq"])]
    q=pe2.copy(); q["cls"]=rows; q=q[q["cls"]!="drop"].copy()
    q["PreAnnounceQtr"]=(q["cls"]=="treat").astype(float)
    return q
ad52, cnt52 = {}, {}
for arm,D in (("cash",cashD),("stock",stockD)):
    q=runup_arm2(D); cnt52[arm]=int(q.loc[q["PreAnnounceQtr"]==1,"gvkey"].nunique())
    for dv in G.DVS:
        mu="UncResCEO" if dv in ("CashScrutiny","HighCashScrutiny") else None
        ad52[(arm,dv)]=G.run(q, dv, match=mu, add_cash_lag=(dv=="CashRatio"))

# ---------------- thesis numbers from json ----------------
th52 = J(latest("outputs/econometric/empire_building_did/*/summary.json"))["results"]
th53 = J(latest("outputs/econometric/empire_drop_matched/*/summary.json"))["specs"]["post_cap_4"]
th54 = J(latest("outputs/econometric/empire_drop_test/*/summary.json"))["specs"]["post_cap_4"]["results"]
th55 = J(latest("outputs/econometric/empire_cashspec/*/summary.json"))["results"]

# ============================ RENDER ============================
DVS=G.DVS
def runup_table():
    def row(label, get):
        cells=[]
        for src in ("th","ad"):
            for arm in ("cash","stock"):
                for dv in DVS:
                    r = (th52[f"{arm}:{dv}"] if src=="th" else ad52[(arm,dv)])
                    cells.append(get(r))
        return label+" & "+" & ".join(cells)+r" \\"
    L=[r"\begin{table}[H]\centering",
       r"\caption{Table 5.2 --- Pre-Announcement Run-Up: Thesis (first deal) vs.\ All Deals (stacked)}",
       r"\scriptsize\begin{adjustbox}{max width=\linewidth}\begin{tabular}{l"+"c"*16+"}",
       r"\toprule",
       r" & \multicolumn{8}{c}{\textbf{Thesis (first deal)}} & \multicolumn{8}{c}{\textbf{All deals (stacked)}} \\",
       r"\cmidrule(lr){2-9}\cmidrule(lr){10-17}",
       r" & \multicolumn{4}{c}{Cash} & \multicolumn{4}{c}{Stock} & \multicolumn{4}{c}{Cash} & \multicolumn{4}{c}{Stock} \\",
       r"\cmidrule(lr){2-5}\cmidrule(lr){6-9}\cmidrule(lr){10-13}\cmidrule(lr){14-17}",
       r" & "+" & ".join(["CshR","UncR","CshSc","HiSc"]*4)+r" \\", r"\midrule",
       row("PreAnnounceQtr", lambda r: C(r["beta"],r["p2"])),
       row("", lambda r: f"({r['se']:.4f})"), r"\midrule"]
    for ct in CTRL:
        L.append(row(ct, lambda r,ct=ct: C(r["ctrls"][ct]["beta"],r["ctrls"][ct]["p2"]) if ct in r.get("ctrls",{}) else "---"))
        L.append(row("", lambda r,ct=ct: f"({r['ctrls'][ct]['se']:.4f})" if ct in r.get("ctrls",{}) else ""))
    L+=[r"\midrule", row("Firms", lambda r: f"{r['n_firms']:,}"), row("N", lambda r: f"{r['n']:,}"),
        r"\bottomrule\end{tabular}\end{adjustbox}",
        r"\begin{minipage}{\linewidth}\vspace{2pt}\scriptsize\textit{Notes:} $^{*}p<.10$,$^{**}p<.05$,$^{***}p<.01$ (two-tailed); SE clustered by firm. CshR=CashRatio(+lag), UncR=UncResCEO, CshSc=CashScrutiny, HiSc=HighCashScrutiny.\end{minipage}\end{table}"]
    return "\n".join(L)

def event_table(caption, thes, allr, keys, klabels, n_th, f_th, n_ad, f_ad, with_lag=False, lagkey="lag"):
    # thes/allr: dict keyed by `keys` (column labels) -> result dict with bins/drops/controls
    ncol=2*len(keys)
    head_th=" & ".join(klabels); head_ad=" & ".join(klabels)
    L=[r"\begin{table}[H]\centering", r"\caption{"+caption+r"}",
       r"\scriptsize\begin{adjustbox}{max width=\linewidth}\begin{tabular}{l"+"c"*ncol+"}",
       r"\toprule",
       rf" & \multicolumn{{{len(keys)}}}{{c}}{{\textbf{{Thesis}}}} & \multicolumn{{{len(keys)}}}{{c}}{{\textbf{{All deals (stacked)}}}} \\",
       rf"\cmidrule(lr){{2-{1+len(keys)}}}\cmidrule(lr){{{2+len(keys)}-{1+2*len(keys)}}}",
       " & "+head_th+" & "+head_ad+r" \\", r"\midrule"]
    drow=lambda get: " & ".join(get(thes[k]) for k in keys)+" & "+" & ".join(get(allr[k]) for k in keys)
    for b in BINS:
        L.append(edt.BINS and "" or "")  # noop
    for b in BINS:
        L.append(f"{b} & "+drow(lambda r,b=b: C(bget(r['bins'][b]), r['bins'][b]['p2']))+r" \\")
        L.append(" & "+drow(lambda r,b=b: f"({r['bins'][b]['se']:.4f})")+r" \\")
    L.append(r"\midrule")
    DROPS=[("pre1_gap","drop_pre1_gap","Drop: PRE1 $-$ GAP"),("gap_post","drop_gap_post","Drop: GAP $-$ POST"),("pre1_post","drop_pre1_post","Drop: PRE1 $-$ POST")]
    for k1,k2,lab in DROPS:
        keyname = k1 if k1 in thes[keys[0]] else k2
        L.append(f"{lab} & "+drow(lambda r,kn=keyname: C(r[kn]['diff'], r[kn]['p2']))+r" \\")
        L.append(" & "+drow(lambda r,kn=keyname: f"({r[kn]['se']:.4f})")+r" \\")
    L.append(r"\midrule\multicolumn{"+str(ncol+1)+r"}{l}{\textit{Controls}} \\")
    for ct in CTRL:
        L.append(f"{ct} & "+drow(lambda r,ct=ct: C(bget(r['controls'][ct]), r['controls'][ct]['p2']) if ct in r.get('controls',{}) else "---")+r" \\")
        L.append(" & "+drow(lambda r,ct=ct: f"({r['controls'][ct]['se']:.4f})" if ct in r.get('controls',{}) else "")+r" \\")
    if with_lag:
        L.append(r"CashRatio$_{t-1}$ (partial adj.) & "+drow(lambda r: C(bget(r[lagkey]),r[lagkey]['p2']) if lagkey in r else "---")+r" \\")
        L.append(" & "+drow(lambda r: f"({r[lagkey]['se']:.4f})" if lagkey in r else "")+r" \\")
    L+=[r"\midrule",
        "N & "+drow(lambda r: f"{r['n']:,}")+r" \\",
        "Firms & "+drow(lambda r: f"{r['n_firms']:,}")+r" \\",
        r"\bottomrule\end{tabular}\end{adjustbox}",
        r"\begin{minipage}{\linewidth}\vspace{2pt}\scriptsize\textit{Notes:} $^{*}p<.10$, $^{**}p<.05$, $^{***}p<.01$ (two-tailed); SE clustered by firm.\end{minipage}\end{table}"]
    return "\n".join(L)

# 5.3 matched: thes keyed UncResCEO/CashRatio
t53 = event_table(r"Table 5.3 --- Matched Universe Event Study: Thesis vs.\ All Deals (stacked)",
                  {"UncResCEO":th53["results"]["UncResCEO"],"CashRatio":th53["results"]["CashRatio"]},
                  {"UncResCEO":ad53["UncResCEO"],"CashRatio":ad53["CashRatio"]},
                  ["UncResCEO","CashRatio"], ["UncRes","CashR"],
                  th53["n"], th53["n_firms"], ad53_n, ad53_f, with_lag=True)
# 5.4 placebo: keyed cash/stock
t54 = event_table(r"Table 5.4 --- Event Study by Payment Type (placebo): Thesis vs.\ All Deals (stacked)",
                  {"cash":th54["cash:UncResCEO"],"stock":th54["stock:UncResCEO"]},
                  {"cash":ad54["cash:UncResCEO"],"stock":ad54["stock:UncResCEO"]},
                  ["cash","stock"], ["Cash","Stock"],
                  th54_n:=J(latest("outputs/econometric/empire_drop_test/*/summary.json"))["specs"]["post_cap_4"].get("n",0),
                  0, 0, 0)

# 5.5 cashspec full (cash/stock/Wald + controls + lag), 6 cols
def cs_full():
    cols=["UncResCEO","CashRatio_matched","CashRatio_full"]; hl=["UncRes","CashR(m)","CashR(f)"]
    def line(get):
        return " & ".join(get(th55[c]) for c in cols)+" & "+" & ".join(get(ad55[c]) for c in cols)
    L=[r"\begin{table}[H]\centering",
       r"\caption{Table 5.5 --- Formal Cash-Specificity (pooled Wald): Thesis (matched) vs.\ All Deals (stacked)}",
       r"\scriptsize\begin{adjustbox}{max width=\linewidth}\begin{tabular}{lcccccc}",
       r"\toprule",
       r" & \multicolumn{3}{c}{\textbf{Thesis (matched)}} & \multicolumn{3}{c}{\textbf{All deals (stacked)}} \\",
       r"\cmidrule(lr){2-4}\cmidrule(lr){5-7}",
       " & "+" & ".join(hl)+" & "+" & ".join(hl)+r" \\", r"\midrule",
       "Pre-announce qtr, Cash & "+line(lambda r:C(r["cash"]["b"],r["cash"]["p2"]))+r" \\",
       " & "+line(lambda r:f"({r['cash']['se']:.4f})")+r" \\",
       "Pre-announce qtr, Stock & "+line(lambda r:C(r["stock"]["b"],r["stock"]["p2"]))+r" \\",
       " & "+line(lambda r:f"({r['stock']['se']:.4f})")+r" \\", r"\midrule",
       r"Cash $-$ Stock (Wald) & "+line(lambda r:C(r["wald"]["diff"],r["wald"]["p2"]))+r" \\",
       " & "+line(lambda r:f"({r['wald']['se']:.4f})")+r" \\", r"\midrule",
       r"\multicolumn{7}{l}{\textit{Controls}} \\"]
    for ct in CTRL:
        L.append(f"{ct} & "+line(lambda r,ct=ct:C(r["controls"][ct]["b"],r["controls"][ct]["p2"]) if ct in r.get("controls",{}) else "---")+r" \\")
        L.append(" & "+line(lambda r,ct=ct:f"({r['controls'][ct]['se']:.4f})" if ct in r.get("controls",{}) else "")+r" \\")
    L.append(r"CashRatio$_{t-1}$ (partial adj.) & "+line(lambda r:C(r["lag"]["b"],r["lag"]["p2"]) if "lag" in r else "---")+r" \\")
    L.append(" & "+line(lambda r:f"({r['lag']['se']:.4f})" if "lag" in r else "")+r" \\")
    L+=[r"\midrule",
        "N & "+" & ".join(f"{th55[c]['n']:,}" for c in cols)+" & "+" & ".join(f"{ad55[c]['n']:,}" for c in cols)+r" \\",
        "Firms & "+" & ".join(f"{th55[c]['n_firms']:,}" for c in cols)+" & "+" & ".join(f"{ad55[c]['n_firms']:,}" for c in cols)+r" \\",
        r"\bottomrule\end{tabular}\end{adjustbox}",
        r"\begin{minipage}{\linewidth}\vspace{2pt}\scriptsize\textit{Notes:} $^{*}p<.10$, $^{**}p<.05$, $^{***}p<.01$ (two-tailed); SE clustered by firm.\end{minipage}\end{table}"]
    return "\n".join(L)
t55 = cs_full()

doc=[r"\documentclass[11pt]{article}",
     r"\usepackage[letterpaper,margin=0.5in,landscape]{geometry}",
     r"\usepackage{newtxtext,newtxmath}\usepackage{booktabs,amsmath,adjustbox,float}",
     r"\begin{document}\pagestyle{empty}",
     runup_table(), r"\clearpage", t53, r"\clearpage", t54, r"\clearpage", t55,
     r"\end{document}"]
out = ROOT/"outputs"/"econometric"/"firstdeal_robustness"
_dirs = [d for d in glob.glob(str(out/"*/")) if Path(d).is_dir()]
outp = Path(sorted(_dirs)[-1]) if _dirs else out
(outp/"rob_4tables.tex").write_text("\n".join(doc), encoding="utf-8")
print("wrote", outp/"rob_4tables.tex")
# quick verify
print("5.3 all-deals PRE1: UncRes", round(ad53["UncResCEO"]["bins"]["PRE1"]["b"],4), "| CashRatio", round(ad53["CashRatio"]["bins"]["PRE1"]["b"],4))
print("5.4 all-deals PRE1: cash", round(ad54["cash:UncResCEO"]["bins"]["PRE1"]["beta"],4), "| stock", round(ad54["stock:UncResCEO"]["bins"]["PRE1"]["beta"],4))
print("5.5 all-deals Wald UncRes:", round(ad55["UncResCEO"]["wald"]["diff"],4), "p", round(ad55["UncResCEO"]["wald"]["p2"],3))
