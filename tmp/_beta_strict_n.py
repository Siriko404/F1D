"""Test β with stricter min_n requirements. Microcaps often have CRSP gaps.
Spec: paper-verbatim 3-ctrl (vol_FTSE + vol_SP500 + vol_FX), 2010M1-2014M12.
Sweep min_n = 24, 36, 48, 60.
"""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd
import shutil
from datetime import datetime

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT/"outputs"/"campello_v2"
def latest(fname):
    return sorted([d for d in OUT.iterdir() if d.is_dir() and (d/fname).exists()], reverse=True)[0]

START = pd.Timestamp("2010-01-01"); END = pd.Timestamp("2014-12-31")

ftse = pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"Yahoo_FTSE100"/"FTSE100_yfinance_daily.csv")
ftse["Date"] = pd.to_datetime(ftse["Date"])
ftse = ftse[(ftse["Date"]>=START)&(ftse["Date"]<=END)].sort_values("Date")
ftse["ret"] = ftse["Close"].pct_change(); ftse["ym"]=ftse["Date"].dt.year*100+ftse["Date"].dt.month
ftse_vol = ftse.dropna(subset=["ret"]).groupby("ym")["ret"].std().reset_index().rename(columns={"ret":"vol_FTSE"})

fx = pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"BoE"/"USD_GBP_daily_2008-2018.csv")
fx["DATE"] = pd.to_datetime(fx["DATE"], format="%d %b %Y", errors="coerce")
fx = fx[(fx["DATE"]>=START)&(fx["DATE"]<=END)].sort_values("DATE")
fx["ret"] = fx["XUDLUSS"].pct_change(); fx["ym"]=fx["DATE"].dt.year*100+fx["DATE"].dt.month
fx_vol = fx.dropna(subset=["ret"]).groupby("ym")["ret"].std().reset_index().rename(columns={"ret":"vol_FX"})

crsp = pd.concat([pd.read_parquet(ROOT/f"inputs/CRSP_DSF/CRSP_DSF_{y}_Q{q}.parquet",
                                   columns=["PERMNO","date","RET","sprtrn"])
                  for y in range(2010,2015) for q in (1,2,3,4)], ignore_index=True)
crsp["date"] = pd.to_datetime(crsp["date"]); crsp["RET"]=pd.to_numeric(crsp["RET"],errors="coerce")
crsp = crsp.dropna(subset=["RET"]); crsp["ym"]=crsp["date"].dt.year*100+crsp["date"].dt.month
sp_vol = crsp.drop_duplicates(["date"]).groupby("ym")["sprtrn"].std().reset_index().rename(columns={"sprtrn":"vol_SP500"})

market = ftse_vol.merge(sp_vol, on="ym").merge(fx_vol, on="ym")
fv = crsp.groupby(["PERMNO","ym"])["RET"].agg(["std","count"]).reset_index()
fv = fv[fv["count"]>=10].rename(columns={"std":"vol_r"}).merge(market, on="ym")

panel = pd.read_parquet(latest("variables_panel.parquet")/"variables_panel.parquet")
sample_gv = set(panel["gvkey"].unique())
ccm = pd.read_parquet(ROOT/"inputs"/"CRSPCompustat_CCM"/"CRSPCompustat_CCM.parquet",
                      columns=["gvkey","LPERMNO","LINKDT","LINKENDDT","LINKTYPE","LINKPRIM"])
ccm["gvkey"] = ccm["gvkey"].astype(str).str.zfill(6)
ccm = ccm[ccm["gvkey"].isin(sample_gv)]
ccm = ccm[ccm["LINKTYPE"].isin(["LU","LC"]) & ccm["LINKPRIM"].isin(["P","C"])]
ccm["LINKDT"] = pd.to_datetime(ccm["LINKDT"], errors="coerce")
ccm["LINKENDDT"] = pd.to_datetime(ccm["LINKENDDT"], errors="coerce").fillna(pd.Timestamp("2099-12-31"))
ccm = ccm[(ccm["LINKENDDT"]>=START)&(ccm["LINKDT"]<=END)]
ccm["LPERMNO"] = pd.to_numeric(ccm["LPERMNO"], errors="coerce").astype("Int64").dropna().astype(int)
ccm_s = ccm[["gvkey","LPERMNO","LINKDT","LINKENDDT"]].rename(columns={"LPERMNO":"PERMNO"})
fv["ym_date"] = pd.to_datetime((fv["ym"]//100).astype(str)+"-"+
                               (fv["ym"]%100).astype(str).str.zfill(2)+"-15")
m = fv.merge(ccm_s, on="PERMNO")
m = m[(m["ym_date"]>=m["LINKDT"]) & (m["ym_date"]<=m["LINKENDDT"])]
m = m.drop_duplicates(["gvkey","ym"], keep="first")

ctrls = ["vol_FTSE","vol_SP500","vol_FX"]
def estimate(min_n):
    res = {}
    for gv, gr in m.groupby("gvkey"):
        g = gr.dropna(subset=["vol_r"]+ctrls)
        if len(g) < min_n: continue
        X = np.column_stack([np.ones(len(g))]+[g[c].values for c in ctrls])
        y = g["vol_r"].values
        try:
            b,*_ = np.linalg.lstsq(X,y,rcond=None)
            res[gv] = (b[1], len(g))
        except: pass
    return pd.DataFrame([{"gvkey":k,"beta_uk":v[0],"n_months":v[1]} for k,v in res.items()])

comp_n = pd.read_parquet(ROOT/"inputs"/"comp_na_daily_all"/"comp_na_daily_all.parquet",
                          columns=["gvkey","conm"])
comp_n["gvkey"] = comp_n["gvkey"].astype(str).str.zfill(6)
comp_n = comp_n.drop_duplicates(["gvkey"], keep="last")

print(f"{'min_n':>6} {'N':>6} {'mean':>8} {'sd':>8} {'%neg':>6} {'t1/3':>8} {'t2/3':>8} {'T(>0.68)':>10} {'C(<0.28)':>10}")
results_by_n = {}
for mn in [24, 36, 48, 54, 58, 60]:
    df = estimate(mn)
    if len(df)==0: continue
    results_by_n[mn] = df
    b = df["beta_uk"]; pos = b[b>=0]
    t1 = pos.quantile(1/3) if (pos>0).sum()>10 else np.nan
    t2 = pos.quantile(2/3) if (pos>0).sum()>10 else np.nan
    tT = (df["beta_uk"]>0.68).sum()
    tC = ((df["beta_uk"]>=0)&(df["beta_uk"]<0.28)).sum()
    print(f"{mn:>6} {len(df):>6} {b.mean():>8.4f} {b.std():>8.4f} {(b<0).mean()*100:>6.1f} {t1:>8.4f} {t2:>8.4f} {tT:>10} {tC:>10}")
print(f"  paper: t1/3≈0.28  t2/3≈0.68  T=449  C=360")

# For best-matched min_n, save + check known firms
print(f"\n=== known UK firms by min_n ===")
known = ["FORD MOTOR","GENERAL MOTORS","MCDONALD","PROCTER","JOHNSON & JOHNSON","PFIZER",
        "MICROSOFT","WAL-MART","EXXON","CHEVRON","COCA-COLA","PEPSICO","BOEING","INTEL",
        "IBM","JPMORGAN","CITIGROUP","HONEYWELL","CATERPILLAR","UNITED TECHNOLOGIES",
        "3M CO","DUPONT","DOW CHEMICAL","HEWLETT-PACKARD","ORACLE","CISCO","DELL"]
for mn in [24, 48, 60]:
    if mn not in results_by_n: continue
    df = results_by_n[mn].merge(comp_n, on="gvkey", how="left")
    in_top = 0; tot = 0
    for kw in known:
        hits = df[df["conm"].str.contains(kw, case=False, na=False)]
        for _, r in hits.head(1).iterrows():
            tot += 1
            if r["beta_uk"]>0.68: in_top += 1
    print(f"  min_n={mn}: known-UK firms in HARD-T set: {in_top}/{tot}")
