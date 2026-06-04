"""β^UK per paper-verbatim eq (13):
  vol(r_it) = α_i + β^UK · vol(FTSE100_t) + θ·[vol(SP500), vol(FX£)] + ε_it
Window: monthly 2010:M1 - 2014:M12  (line 370 var_13 lockin)
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

# FTSE 100 realized vol
ftse = pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"Yahoo_FTSE100"/"FTSE100_yfinance_daily.csv")
ftse["Date"] = pd.to_datetime(ftse["Date"])
ftse = ftse[(ftse["Date"]>=START)&(ftse["Date"]<=END)].sort_values("Date")
ftse["ret"] = ftse["Close"].pct_change()
ftse["ym"]  = ftse["Date"].dt.year*100 + ftse["Date"].dt.month
ftse_vol = ftse.dropna(subset=["ret"]).groupby("ym")["ret"].std().reset_index().rename(columns={"ret":"vol_FTSE"})

# FX £-$ vol
fx = pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"BoE"/"USD_GBP_daily_2008-2018.csv")
fx["DATE"] = pd.to_datetime(fx["DATE"], format="%d %b %Y", errors="coerce")
fx = fx[(fx["DATE"]>=START)&(fx["DATE"]<=END)].sort_values("DATE")
fx["ret"] = fx["XUDLUSS"].pct_change()
fx["ym"]  = fx["DATE"].dt.year*100 + fx["DATE"].dt.month
fx_vol = fx.dropna(subset=["ret"]).groupby("ym")["ret"].std().reset_index().rename(columns={"ret":"vol_FX"})

# CRSP 2010-2014
crsp = pd.concat([pd.read_parquet(ROOT/f"inputs/CRSP_DSF/CRSP_DSF_{y}_Q{q}.parquet",
                                   columns=["PERMNO","date","RET","sprtrn"])
                  for y in range(2010,2015) for q in (1,2,3,4)], ignore_index=True)
crsp["date"] = pd.to_datetime(crsp["date"]); crsp["RET"] = pd.to_numeric(crsp["RET"], errors="coerce")
crsp = crsp.dropna(subset=["RET"]); crsp["ym"] = crsp["date"].dt.year*100+crsp["date"].dt.month
sp_vol = crsp.drop_duplicates(["date"]).groupby("ym")["sprtrn"].std().reset_index().rename(columns={"sprtrn":"vol_SP500"})

market = ftse_vol.merge(sp_vol, on="ym").merge(fx_vol, on="ym")
print(f"Market panel: {len(market)} months ({market['ym'].min()}–{market['ym'].max()})")

firm_vol = crsp.groupby(["PERMNO","ym"])["RET"].agg(["std","count"]).reset_index()
firm_vol = firm_vol[firm_vol["count"]>=10].rename(columns={"std":"vol_r"})
firm_vol = firm_vol.merge(market, on="ym")

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

firm_vol["ym_date"] = pd.to_datetime((firm_vol["ym"]//100).astype(str)+"-"+
                                     (firm_vol["ym"]%100).astype(str).str.zfill(2)+"-15")
m = firm_vol.merge(ccm_s, on="PERMNO")
m = m[(m["ym_date"]>=m["LINKDT"]) & (m["ym_date"]<=m["LINKENDDT"])]
m = m.drop_duplicates(["gvkey","ym"], keep="first")

# β regression — 3 ctrls only
ctrls = ["vol_FTSE","vol_SP500","vol_FX"]
results = {}
for gv, gr in m.groupby("gvkey"):
    g = gr.dropna(subset=["vol_r"]+ctrls)
    if len(g) < 24: continue
    X = np.column_stack([np.ones(len(g))] + [g[c].values for c in ctrls])
    y = g["vol_r"].values
    try:
        b,*_ = np.linalg.lstsq(X, y, rcond=None)
        yp = X@b; ssr=((y-yp)**2).sum(); sst=((y-y.mean())**2).sum()
        results[gv] = (b[1], len(g), 1-ssr/sst if sst>0 else np.nan)
    except: pass
df = pd.DataFrame([{"gvkey":k,"beta_uk":v[0],"n_months":v[1],"r2":v[2]} for k,v in results.items()])
b = df["beta_uk"]; pos = b[b>=0]
print(f"\nβ^UK paper-verbatim [3 ctrls: vol_FTSE, vol_SP500, vol_FX]:")
print(f"  N={len(df):,}  mean={b.mean():.4f}  sd={b.std():.4f}  %neg={(b<0).mean()*100:.1f}%")
print(f"  pos terciles: 30%={pos.quantile(0.30):.4f}  70%={pos.quantile(0.70):.4f}  (paper 0.28/0.68)")
print(f"  pos terciles: 1/3 ={pos.quantile(1/3):.4f}  2/3 ={pos.quantile(2/3):.4f}")
print(f"  HARD: T(β>0.68) = {(df['beta_uk']>0.68).sum():,}  (paper 449)")
print(f"  HARD: C(0≤β<0.28) = {((df['beta_uk']>=0)&(df['beta_uk']<0.28)).sum():,}  (paper 360)")

ts = datetime.now().strftime("%Y%m%d_%H%M%S")
od = OUT/ts; od.mkdir(parents=True, exist_ok=True)
df.to_parquet(od/"beta_uk.parquet", index=False)
for fn in ["variables_panel.parquet","stock_returns.parquet","consensus_eps.parquet"]:
    shutil.copy(str(latest(fn)/fn), str(od/fn))
print(f"\nSaved: {od}")
