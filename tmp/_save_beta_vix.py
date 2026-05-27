"""Save β^UK with VIX as SP500 vol control to outputs dir."""
import warnings; warnings.filterwarnings("ignore")
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd
import yfinance as yf

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT / "outputs" / "campello_v2"

def latest(fname):
    runs = sorted([d for d in OUT.iterdir() if d.is_dir() and (d / fname).exists()], reverse=True)
    return runs[0] / fname

START = pd.Timestamp("2010-01-01")
END = pd.Timestamp("2014-12-31")

vix = yf.download("^VIX", start="2009-12-01", end="2015-02-01", progress=False, auto_adjust=False)
if isinstance(vix.columns, pd.MultiIndex):
    vix.columns = vix.columns.get_level_values(0)
vix = vix.reset_index()
vix["Date"] = pd.to_datetime(vix["Date"])
vix = vix[(vix["Date"] >= START) & (vix["Date"] <= END)].sort_values("Date")
vix["ym"] = vix["Date"].dt.year * 100 + vix["Date"].dt.month
vix_eom = vix.groupby("ym")["Close"].last().reset_index().rename(columns={"Close": "VIX"})

ftse = pd.read_csv(ROOT / "inputs" / "Brexit_replication" / "Yahoo_FTSE100" / "FTSE100_yfinance_daily.csv")
ftse["Date"] = pd.to_datetime(ftse["Date"])
ftse = ftse[(ftse["Date"] >= START) & (ftse["Date"] <= END)].sort_values("Date")
ftse["ret"] = ftse["Close"].pct_change()
ftse = ftse.dropna(subset=["ret"])
ftse["ym"] = ftse["Date"].dt.year * 100 + ftse["Date"].dt.month
ftse_vol = ftse.groupby("ym")["ret"].std().reset_index().rename(columns={"ret": "vol_FTSE"})

fx = pd.read_csv(ROOT / "inputs" / "Brexit_replication" / "BoE" / "USD_GBP_daily_2008-2018.csv")
fx["DATE"] = pd.to_datetime(fx["DATE"], format="%d %b %Y", errors="coerce")
fx = fx[(fx["DATE"] >= START) & (fx["DATE"] <= END)].sort_values("DATE")
fx["ret"] = fx["XUDLUSS"].pct_change()
fx = fx.dropna(subset=["ret"])
fx["ym"] = fx["DATE"].dt.year * 100 + fx["DATE"].dt.month
fx_vol = fx.groupby("ym")["ret"].std().reset_index().rename(columns={"ret": "vol_FX"})

market = ftse_vol.merge(vix_eom, on="ym").merge(fx_vol, on="ym")

crsp_frames = []
for year in range(2010, 2015):
    for q in (1, 2, 3, 4):
        f = ROOT / "inputs" / "CRSP_DSF" / f"CRSP_DSF_{year}_Q{q}.parquet"
        if f.exists():
            df = pd.read_parquet(f, columns=["PERMNO", "date", "RET"])
            crsp_frames.append(df)
crsp = pd.concat(crsp_frames, ignore_index=True)
crsp["date"] = pd.to_datetime(crsp["date"])
crsp["RET"] = pd.to_numeric(crsp["RET"], errors="coerce")
crsp = crsp.dropna(subset=["RET"])
crsp["ym"] = crsp["date"].dt.year * 100 + crsp["date"].dt.month

firm_vol = crsp.groupby(["PERMNO", "ym"])["RET"].agg(["std", "count"]).reset_index()
firm_vol = firm_vol[firm_vol["count"] >= 10].rename(columns={"std": "vol_r"})
firm_vol = firm_vol.merge(market, on="ym")

panel = pd.read_parquet(latest("variables_panel.parquet"))
sample_gv = set(panel["gvkey"].unique())
ccm = pd.read_parquet(ROOT / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet",
                      columns=["gvkey", "LPERMNO", "LINKDT", "LINKENDDT", "LINKTYPE", "LINKPRIM"])
ccm["gvkey"] = ccm["gvkey"].astype(str).str.zfill(6)
ccm = ccm[ccm["gvkey"].isin(sample_gv)]
ccm = ccm[ccm["LINKTYPE"].isin(["LU", "LC"])]
ccm = ccm[ccm["LINKPRIM"].isin(["P", "C"])]
ccm["LINKDT"] = pd.to_datetime(ccm["LINKDT"], errors="coerce")
ccm["LINKENDDT"] = pd.to_datetime(ccm["LINKENDDT"], errors="coerce").fillna(pd.Timestamp("2099-12-31"))
ccm = ccm[(ccm["LINKENDDT"] >= START) & (ccm["LINKDT"] <= END)]
ccm["LPERMNO"] = pd.to_numeric(ccm["LPERMNO"], errors="coerce").astype("Int64").dropna().astype(int)

ccm_simple = ccm[["gvkey", "LPERMNO", "LINKDT", "LINKENDDT"]].rename(columns={"LPERMNO": "PERMNO"})
firm_vol["ym_date"] = pd.to_datetime((firm_vol["ym"] // 100).astype(str) + "-" +
                                       (firm_vol["ym"] % 100).astype(str).str.zfill(2) + "-15")
merged = firm_vol.merge(ccm_simple, on="PERMNO")
merged = merged[(merged["ym_date"] >= merged["LINKDT"]) & (merged["ym_date"] <= merged["LINKENDDT"])]
merged = merged.drop_duplicates(subset=["gvkey", "ym"], keep="first")

# Also load realized SP500 vol from CRSP for 4-control variant F
crsp_sp_frames = []
for year in range(2010, 2015):
    for q in (1, 2, 3, 4):
        f = ROOT / "inputs" / "CRSP_DSF" / f"CRSP_DSF_{year}_Q{q}.parquet"
        if f.exists():
            df = pd.read_parquet(f, columns=["date", "sprtrn"])
            crsp_sp_frames.append(df)
crsp_sp = pd.concat(crsp_sp_frames, ignore_index=True)
crsp_sp["date"] = pd.to_datetime(crsp_sp["date"])
crsp_sp = crsp_sp.dropna(subset=["sprtrn"]).drop_duplicates(subset=["date"]).sort_values("date")
crsp_sp["ym"] = crsp_sp["date"].dt.year * 100 + crsp_sp["date"].dt.month
sp_realized = crsp_sp.groupby("ym")["sprtrn"].std().reset_index().rename(columns={"sprtrn": "vol_SP500_real"})
merged = merged.merge(sp_realized, on="ym", how="left")

# Variant F: 4-control regression (vol_FTSE + vol_SP500_real + VIX_eom + vol_FX)
results = {}
for gv, gr in merged.groupby("gvkey"):
    g = gr.dropna(subset=["vol_r", "vol_FTSE", "vol_SP500_real", "VIX", "vol_FX"])
    if len(g) < 24:
        continue
    X = np.column_stack([np.ones(len(g)),
                          g["vol_FTSE"].values,
                          g["vol_SP500_real"].values,
                          g["VIX"].values,
                          g["vol_FX"].values])
    y = g["vol_r"].values
    try:
        b, *_ = np.linalg.lstsq(X, y, rcond=None)
        yp = X @ b
        ss_res = ((y - yp) ** 2).sum()
        ss_tot = ((y - y.mean()) ** 2).sum()
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
        results[gv] = (b[1], len(g), r2)
    except:
        pass

beta_df = pd.DataFrame([{"gvkey": k, "beta_uk": v[0], "n_months": v[1], "r2": v[2]}
                        for k, v in results.items()])
print(f"β^UK with VIX_eom: N={len(beta_df):,}")
b = beta_df["beta_uk"]
print(f"  mean={b.mean():.3f}  sd={b.std():.3f}  %β<0={(b<0).mean()*100:.1f}%")
pos = b[b >= 0]
print(f"  nonneg terciles: t1={pos.quantile(1/3):.3f}  t2={pos.quantile(2/3):.3f}")

# Save to new output dir (mimics beta_uk.parquet structure)
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
out_dir = OUT / ts
out_dir.mkdir(parents=True, exist_ok=True)
beta_df.to_parquet(out_dir / "beta_uk.parquet", index=False)
print(f"\nSaved to {out_dir / 'beta_uk.parquet'}")

# Copy other latest files into this dir so PSM finds them
for fn in ["variables_panel.parquet", "stock_returns.parquet", "consensus_eps.parquet"]:
    src = latest(fn)
    import shutil
    shutil.copy(src, out_dir / fn)
    print(f"  Copied {fn}")
