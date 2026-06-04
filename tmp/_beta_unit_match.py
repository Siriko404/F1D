"""Test unit-matched β specifications:
- E: vol_r_annual ~ VFTSE_annual (both annualized) + annualized SP,FX
- F: vol_r_monthly ~ VFTSE_monthly (both monthly) — VFTSE/sqrt(12)
- G: Spec A but with vol_FTSE realized included alongside VFTSE
"""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT / "outputs" / "campello_v2"
START = pd.Timestamp("2013-01-01"); END = pd.Timestamp("2014-12-31")

vftse = pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"VFTSE"/"VFTSE_weeklyspliced_2010_2014.csv")
vftse["Date"] = pd.to_datetime(vftse["Date"])
vftse = vftse[(vftse["Date"]>=START)&(vftse["Date"]<=END)]
vftse["ym"] = vftse["Date"].dt.year*100+vftse["Date"].dt.month
v = vftse.groupby("ym")["VFTSE"].mean().reset_index()
v["VFTSE_ann"] = v["VFTSE"]/100.0          # decimal, annualized
v["VFTSE_mo"]  = v["VFTSE_ann"]/np.sqrt(12) # decimal, monthly-equivalent

fx = pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"BoE"/"USD_GBP_daily_2008-2018.csv")
fx["DATE"] = pd.to_datetime(fx["DATE"], format="%d %b %Y", errors="coerce")
fx = fx[(fx["DATE"]>=START)&(fx["DATE"]<=END)]
fx["ret"] = fx["XUDLUSS"].pct_change()
fx["ym"] = fx["DATE"].dt.year*100+fx["DATE"].dt.month
fx_d = fx.dropna(subset=["ret"]).groupby("ym")["ret"].std().reset_index().rename(columns={"ret":"vol_FX_d"})

crsp_frames = [pd.read_parquet(ROOT/f"inputs/CRSP_DSF/CRSP_DSF_{y}_Q{q}.parquet",
                               columns=["PERMNO","date","RET","sprtrn"])
               for y in range(2013,2015) for q in (1,2,3,4)]
crsp = pd.concat(crsp_frames, ignore_index=True)
crsp["date"] = pd.to_datetime(crsp["date"]); crsp["RET"] = pd.to_numeric(crsp["RET"],errors="coerce")
crsp = crsp.dropna(subset=["RET"]); crsp["ym"] = crsp["date"].dt.year*100+crsp["date"].dt.month
sp_v = crsp.drop_duplicates(["date"]).groupby("ym")["sprtrn"].std().reset_index().rename(columns={"sprtrn":"vol_SP_d"})

# Build market panel in MULTIPLE units
market = v[["ym","VFTSE_ann","VFTSE_mo"]].merge(sp_v, on="ym").merge(fx_d, on="ym")
# Daily-scale → monthly std assuming ~21 days: scale_factor = sqrt(21)
market["vol_SP_mo"] = market["vol_SP_d"]*np.sqrt(21)
market["vol_FX_mo"] = market["vol_FX_d"]*np.sqrt(21)
market["vol_SP_ann"] = market["vol_SP_d"]*np.sqrt(252)
market["vol_FX_ann"] = market["vol_FX_d"]*np.sqrt(252)

firm_vol = crsp.groupby(["PERMNO","ym"])["RET"].agg(["std","count"]).reset_index()
firm_vol = firm_vol[firm_vol["count"]>=10].rename(columns={"std":"vol_r_d"})
firm_vol["vol_r_mo"] = firm_vol["vol_r_d"]*np.sqrt(21)
firm_vol["vol_r_ann"] = firm_vol["vol_r_d"]*np.sqrt(252)
firm_vol = firm_vol.merge(market, on="ym")

panel = pd.read_parquet(sorted(OUT.glob("*/variables_panel.parquet"))[-1])
sample_gv = set(panel["gvkey"].unique())
ccm = pd.read_parquet(ROOT/"inputs"/"CRSPCompustat_CCM"/"CRSPCompustat_CCM.parquet",
                      columns=["gvkey","LPERMNO","LINKDT","LINKENDDT","LINKTYPE","LINKPRIM"])
ccm["gvkey"] = ccm["gvkey"].astype(str).str.zfill(6)
ccm = ccm[ccm["gvkey"].isin(sample_gv)]
ccm = ccm[ccm["LINKTYPE"].isin(["LU","LC"]) & ccm["LINKPRIM"].isin(["P","C"])]
ccm["LINKDT"] = pd.to_datetime(ccm["LINKDT"], errors="coerce")
ccm["LINKENDDT"] = pd.to_datetime(ccm["LINKENDDT"], errors="coerce").fillna(pd.Timestamp("2099-12-31"))
ccm = ccm[(ccm["LINKENDDT"]>=START) & (ccm["LINKDT"]<=END)]
ccm["LPERMNO"] = pd.to_numeric(ccm["LPERMNO"], errors="coerce").astype("Int64").dropna().astype(int)
ccm_s = ccm[["gvkey","LPERMNO","LINKDT","LINKENDDT"]].rename(columns={"LPERMNO":"PERMNO"})

firm_vol["ym_date"] = pd.to_datetime((firm_vol["ym"]//100).astype(str)+"-"+
                                    (firm_vol["ym"]%100).astype(str).str.zfill(2)+"-15")
m = firm_vol.merge(ccm_s, on="PERMNO")
m = m[(m["ym_date"]>=m["LINKDT"]) & (m["ym_date"]<=m["LINKENDDT"])]
m = m.drop_duplicates(["gvkey","ym"], keep="first")

comp = pd.read_parquet(ROOT/"inputs"/"comp_na_daily_all"/"comp_na_daily_all.parquet",
                       columns=["gvkey","conm"])
comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
comp = comp.drop_duplicates(["gvkey"], keep="last")
known = ["BP P.L.C","BARCLAYS","GLAXO","ASTRAZENECA","UNILEVER","DIAGEO","VODAFONE","HSBC",
         "FORD MOTOR","GENERAL MOTORS","MCDONALD","PROCTER","JOHNSON & JOHNSON",
         "PFIZER","MICROSOFT","WAL-MART","EXXON","CHEVRON","COCA-COLA","PEPSICO",
         "BOEING","HONEYWELL","CATERPILLAR","CITIGROUP","JPMORGAN","GOLDMAN","INTEL","IBM"]

def reg(df, ycol, xcols, min_n=18):
    res = {}
    for gv, gr in df.groupby("gvkey"):
        g = gr.dropna(subset=[ycol]+xcols)
        if len(g) < min_n: continue
        X = np.column_stack([np.ones(len(g))]+[g[c].values for c in xcols])
        y = g[ycol].values
        try:
            b,*_ = np.linalg.lstsq(X,y,rcond=None)
            res[gv] = b[1]
        except: pass
    return pd.DataFrame([{"gvkey":k,"beta_uk":v} for k,v in res.items()])

def report(name, df):
    df2 = df.merge(comp, on="gvkey", how="left")
    b = df["beta_uk"]; pos = b[b>=0]
    print(f"\n=== {name} ===")
    print(f"  N={len(df):,} mean={b.mean():.4f} sd={b.std():.4f}")
    if (pos>0).sum() > 10:
        t30 = pos.quantile(0.30); t70 = pos.quantile(0.70)
        print(f"  pos terciles: 30%={t30:.4f} 70%={t70:.4f}  (paper 0.28/0.68)")
    df2_s = df2.sort_values("beta_uk", ascending=False)
    t70_val = pos.quantile(0.70) if (pos>0).sum()>10 else b.quantile(0.70)
    in_top = 0; total = 0
    for kw in known:
        match = df2_s[df2_s["conm"].str.contains(kw, case=False, na=False)]
        for _, r in match.head(1).iterrows():
            total += 1
            if r["beta_uk"] >= t70_val: in_top += 1
    print(f"  known UK firms TOP tercile: {in_top}/{total}")
    print(f"  TOP 10: {[(r[0][:30],round(r[1],3)) for r in df2_s.head(10)[['conm','beta_uk']].values.tolist()]}")

# E: annualized both sides
E = reg(m, "vol_r_ann", ["VFTSE_ann","vol_SP_ann","vol_FX_ann"])
report("E: annualized vol both sides", E)

# F: monthly both sides (VFTSE/sqrt(12))
F = reg(m, "vol_r_mo", ["VFTSE_mo","vol_SP_mo","vol_FX_mo"])
report("F: monthly-converted vol both sides", F)

# G: annualized + with realized vol_FTSE alongside VFTSE
ftse = pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"Yahoo_FTSE100"/"FTSE100_yfinance_daily.csv")
ftse["Date"] = pd.to_datetime(ftse["Date"])
ftse = ftse[(ftse["Date"]>=START)&(ftse["Date"]<=END)]
ftse["ret"] = ftse["Close"].pct_change()
ftse["ym"] = ftse["Date"].dt.year*100+ftse["Date"].dt.month
ftse_v = ftse.dropna(subset=["ret"]).groupby("ym")["ret"].std().reset_index().rename(columns={"ret":"vol_FTSE_d"})
ftse_v["vol_FTSE_ann"] = ftse_v["vol_FTSE_d"]*np.sqrt(252)
m2 = m.merge(ftse_v[["ym","vol_FTSE_ann"]], on="ym")
G = reg(m2, "vol_r_ann", ["vol_FTSE_ann","vol_SP_ann","vol_FX_ann"])
report("G: realized FTSE vol (not VFTSE) — annualized", G)
