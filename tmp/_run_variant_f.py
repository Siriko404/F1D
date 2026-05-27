"""Variant F: realized FTSE vol + realized SP500 vol + VIX + vol_FX → β^UK."""
import warnings; warnings.filterwarnings("ignore")
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd
import yfinance as yf
import shutil

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT / "outputs" / "campello_v2"
def latest(fname):
    runs = sorted([d for d in OUT.iterdir() if d.is_dir() and (d / fname).exists()], reverse=True)
    return runs[0] / fname

START = pd.Timestamp("2010-01-01"); END = pd.Timestamp("2014-12-31")

# Market data
vix = yf.download("^VIX", start="2009-12-01", end="2015-02-01", progress=False, auto_adjust=False)
if isinstance(vix.columns, pd.MultiIndex): vix.columns = vix.columns.get_level_values(0)
vix = vix.reset_index(); vix["Date"] = pd.to_datetime(vix["Date"])
vix = vix[(vix["Date"]>=START)&(vix["Date"]<=END)].sort_values("Date")
vix["ym"] = vix["Date"].dt.year*100+vix["Date"].dt.month
vix_eom = vix.groupby("ym")["Close"].last().reset_index().rename(columns={"Close":"VIX"})

ftse = pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"Yahoo_FTSE100"/"FTSE100_yfinance_daily.csv")
ftse["Date"] = pd.to_datetime(ftse["Date"])
ftse = ftse[(ftse["Date"]>=START)&(ftse["Date"]<=END)].sort_values("Date")
ftse["ret"] = ftse["Close"].pct_change(); ftse = ftse.dropna(subset=["ret"])
ftse["ym"] = ftse["Date"].dt.year*100+ftse["Date"].dt.month
ftse_vol = ftse.groupby("ym")["ret"].std().reset_index().rename(columns={"ret":"vol_FTSE"})

fx = pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"BoE"/"USD_GBP_daily_2008-2018.csv")
fx["DATE"] = pd.to_datetime(fx["DATE"], format="%d %b %Y", errors="coerce")
fx = fx[(fx["DATE"]>=START)&(fx["DATE"]<=END)].sort_values("DATE")
fx["ret"] = fx["XUDLUSS"].pct_change(); fx = fx.dropna(subset=["ret"])
fx["ym"] = fx["DATE"].dt.year*100+fx["DATE"].dt.month
fx_vol = fx.groupby("ym")["ret"].std().reset_index().rename(columns={"ret":"vol_FX"})

# Realized SP500 vol from CRSP
crsp_sp = pd.concat([pd.read_parquet(ROOT/f"inputs/CRSP_DSF/CRSP_DSF_{year}_Q{q}.parquet",
                                     columns=["date","sprtrn"])
                     for year in range(2010,2015) for q in (1,2,3,4)], ignore_index=True)
crsp_sp["date"] = pd.to_datetime(crsp_sp["date"])
crsp_sp = crsp_sp.dropna(subset=["sprtrn"]).drop_duplicates(subset=["date"]).sort_values("date")
crsp_sp["ym"] = crsp_sp["date"].dt.year*100+crsp_sp["date"].dt.month
sp_real = crsp_sp.groupby("ym")["sprtrn"].std().reset_index().rename(columns={"sprtrn":"vol_SP500"})

market = ftse_vol.merge(vix_eom, on="ym").merge(fx_vol, on="ym").merge(sp_real, on="ym")

# CRSP
crsp_frames = [pd.read_parquet(ROOT/f"inputs/CRSP_DSF/CRSP_DSF_{year}_Q{q}.parquet",
                                columns=["PERMNO","date","RET"])
               for year in range(2010,2015) for q in (1,2,3,4)]
crsp = pd.concat(crsp_frames, ignore_index=True)
crsp["date"] = pd.to_datetime(crsp["date"]); crsp["RET"] = pd.to_numeric(crsp["RET"],errors="coerce")
crsp = crsp.dropna(subset=["RET"]); crsp["ym"] = crsp["date"].dt.year*100+crsp["date"].dt.month

firm_vol = crsp.groupby(["PERMNO","ym"])["RET"].agg(["std","count"]).reset_index()
firm_vol = firm_vol[firm_vol["count"]>=10].rename(columns={"std":"vol_r"})
firm_vol = firm_vol.merge(market, on="ym")

panel = pd.read_parquet(latest("variables_panel.parquet"))
sample_gv = set(panel["gvkey"].unique())
ccm = pd.read_parquet(ROOT/"inputs"/"CRSPCompustat_CCM"/"CRSPCompustat_CCM.parquet",
                      columns=["gvkey","LPERMNO","LINKDT","LINKENDDT","LINKTYPE","LINKPRIM"])
ccm["gvkey"] = ccm["gvkey"].astype(str).str.zfill(6); ccm = ccm[ccm["gvkey"].isin(sample_gv)]
ccm = ccm[ccm["LINKTYPE"].isin(["LU","LC"])]; ccm = ccm[ccm["LINKPRIM"].isin(["P","C"])]
ccm["LINKDT"] = pd.to_datetime(ccm["LINKDT"], errors="coerce")
ccm["LINKENDDT"] = pd.to_datetime(ccm["LINKENDDT"], errors="coerce").fillna(pd.Timestamp("2099-12-31"))
ccm = ccm[(ccm["LINKENDDT"]>=START)&(ccm["LINKDT"]<=END)]
ccm["LPERMNO"] = pd.to_numeric(ccm["LPERMNO"],errors="coerce").astype("Int64").dropna().astype(int)
ccm_s = ccm[["gvkey","LPERMNO","LINKDT","LINKENDDT"]].rename(columns={"LPERMNO":"PERMNO"})
firm_vol["ym_date"] = pd.to_datetime((firm_vol["ym"]//100).astype(str)+"-"+
                                       (firm_vol["ym"]%100).astype(str).str.zfill(2)+"-15")
merged = firm_vol.merge(ccm_s, on="PERMNO")
merged = merged[(merged["ym_date"]>=merged["LINKDT"])&(merged["ym_date"]<=merged["LINKENDDT"])]
merged = merged.drop_duplicates(subset=["gvkey","ym"], keep="first")

# Regression: vol_FTSE real + vol_SP500 real + VIX + vol_FX
ctrls = ["vol_FTSE","vol_SP500","VIX","vol_FX"]
results = {}
for gv, gr in merged.groupby("gvkey"):
    g = gr.dropna(subset=["vol_r"]+ctrls)
    if len(g) < 24: continue
    X = np.column_stack([np.ones(len(g))]+[g[c].values for c in ctrls])
    y = g["vol_r"].values
    try:
        b,*_ = np.linalg.lstsq(X,y,rcond=None)
        yp = X@b; ssr=((y-yp)**2).sum(); sst=((y-y.mean())**2).sum()
        results[gv] = (b[1],len(g),1-ssr/sst if sst>0 else np.nan)
    except: pass
df = pd.DataFrame([{"gvkey":k,"beta_uk":v[0],"n_months":v[1],"r2":v[2]} for k,v in results.items()])
b = df["beta_uk"]; pos = b[b>=0]
print(f"\nβ^UK [Variant F: FTSE_real+SP500_real+VIX+FX]:")
print(f"  N={len(df):,}  mean={b.mean():.6f}  sd={b.std():.6f}  %neg={(b<0).mean()*100:.1f}%")
print(f"  terciles: t1={pos.quantile(1/3):.4f}  t2={pos.quantile(2/3):.4f}  (paper t1≈0.28)")

ts = datetime.now().strftime("%Y%m%d_%H%M%S")
out_dir = OUT/ts; out_dir.mkdir(parents=True, exist_ok=True)
df.to_parquet(out_dir/"beta_uk.parquet", index=False)
for fn in ["variables_panel.parquet","stock_returns.parquet","consensus_eps.parquet"]:
    shutil.copy(latest(fn), out_dir/fn)
print(f"\nSaved to {out_dir}")
