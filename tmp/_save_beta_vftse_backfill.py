"""β^UK regression with VFTSE_backfilled + VIX + vol_FX.

Per Bloom (2014) framework + Campello eq (13): vol(r_it) = α + β^UK*VFTSE
  + θ1*VIX + θ2*vol(FX$£) + ε.

VFTSE = calibrated 2010-Aug 2012 (park_5d), actual Aug 2012-Dec 2014."""
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

START = pd.Timestamp("2010-01-01")
END = pd.Timestamp("2014-12-31")

# 1. Load backfilled VFTSE
vftse = pd.read_csv(ROOT / "inputs" / "Brexit_replication" / "VFTSE" / "VFTSE_backfilled_2010_2014.csv")
vftse["Date"] = pd.to_datetime(vftse["Date"])
vftse["ym"] = vftse["Date"].dt.year * 100 + vftse["Date"].dt.month
vftse_eom = vftse.groupby("ym")["VFTSE"].last().reset_index().rename(columns={"VFTSE": "VFTSE_eom"})
vftse_mean = vftse.groupby("ym")["VFTSE"].mean().reset_index().rename(columns={"VFTSE": "VFTSE_mean"})
print(f"VFTSE: {len(vftse_eom)} months, eom_range=[{vftse_eom['VFTSE_eom'].min():.2f}, {vftse_eom['VFTSE_eom'].max():.2f}]")

# 2. VIX
vix = yf.download("^VIX", start="2009-12-01", end="2015-02-01", progress=False, auto_adjust=False)
if isinstance(vix.columns, pd.MultiIndex):
    vix.columns = vix.columns.get_level_values(0)
vix = vix.reset_index()
vix["Date"] = pd.to_datetime(vix["Date"])
vix = vix[(vix["Date"] >= START) & (vix["Date"] <= END)].sort_values("Date")
vix["ym"] = vix["Date"].dt.year * 100 + vix["Date"].dt.month
vix_eom = vix.groupby("ym")["Close"].last().reset_index().rename(columns={"Close": "VIX_eom"})
vix_mean = vix.groupby("ym")["Close"].mean().reset_index().rename(columns={"Close": "VIX_mean"})

# 3. FX realized vol
fx = pd.read_csv(ROOT / "inputs" / "Brexit_replication" / "BoE" / "USD_GBP_daily_2008-2018.csv")
fx["DATE"] = pd.to_datetime(fx["DATE"], format="%d %b %Y", errors="coerce")
fx = fx[(fx["DATE"] >= START) & (fx["DATE"] <= END)].sort_values("DATE")
fx["ret"] = fx["XUDLUSS"].pct_change()
fx = fx.dropna(subset=["ret"])
fx["ym"] = fx["DATE"].dt.year * 100 + fx["DATE"].dt.month
fx_vol = fx.groupby("ym")["ret"].std().reset_index().rename(columns={"ret": "vol_FX"})

market = vftse_eom.merge(vftse_mean, on="ym").merge(vix_eom, on="ym").merge(vix_mean, on="ym").merge(fx_vol, on="ym")
print(f"\nMarket panel: {len(market)} months")
print(f"  VFTSE_eom: mean={market['VFTSE_eom'].mean():.2f}  sd={market['VFTSE_eom'].std():.2f}")
print(f"  VIX_eom: mean={market['VIX_eom'].mean():.2f}  sd={market['VIX_eom'].std():.2f}")
print(f"  vol_FX: mean={market['vol_FX'].mean():.5f}  sd={market['vol_FX'].std():.5f}")
print(f"  Corr(VFTSE_eom, VIX_eom): {market[['VFTSE_eom','VIX_eom']].corr().iloc[0,1]:.4f}")

# 4. CRSP firm vol
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
print(f"\nFirm-vol obs after market merge: {len(firm_vol):,}")

# 5. CCM linkage
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
print(f"After CCM: {len(merged):,} firm-months, {merged['gvkey'].nunique():,} firms")

def run_ols(ctrls, label):
    results = {}
    for gv, gr in merged.groupby("gvkey"):
        g = gr.dropna(subset=["vol_r"] + ctrls)
        if len(g) < 24:
            continue
        X = np.column_stack([np.ones(len(g))] + [g[c].values for c in ctrls])
        y = g["vol_r"].values
        try:
            b, *_ = np.linalg.lstsq(X, y, rcond=None)
            yp = X @ b
            ss_res = ((y - yp) ** 2).sum()
            ss_tot = ((y - y.mean()) ** 2).sum()
            r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
            results[gv] = (b[1], len(g), r2)
        except:
            continue
    df = pd.DataFrame([{"gvkey": k, "beta_uk": v[0], "n_months": v[1], "r2": v[2]} for k, v in results.items()])
    b = df["beta_uk"]
    pos = b[b >= 0]
    print(f"\n[{label}] N={len(df):,}  mean={b.mean():.4f}  sd={b.std():.4f}  %β<0={(b<0).mean()*100:.1f}%")
    print(f"  nonneg terciles: t1={pos.quantile(1/3):.4f}  t2={pos.quantile(2/3):.4f}")
    print(f"  Paper anchor: t1=0.28, t2=0.68")
    return df

# Primary: VFTSE_eom + VIX_eom + vol_FX (paper eq 13 with all-implied for FTSE+SP500)
df_primary = run_ols(["VFTSE_eom", "VIX_eom", "vol_FX"], "VFTSE_eom + VIX_eom + vol_FX [PRIMARY]")

# Alt: monthly means
df_mean = run_ols(["VFTSE_mean", "VIX_mean", "vol_FX"], "VFTSE_mean + VIX_mean + vol_FX")

# Alt: VFTSE only (no VIX) — pure UK uncertainty
df_uk_only = run_ols(["VFTSE_eom", "vol_FX"], "VFTSE_eom + vol_FX (no VIX)")

# Save PRIMARY
print("\nSaving VFTSE_eom + VIX_eom + vol_FX β^UK as primary...")
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
out_dir = OUT / ts
out_dir.mkdir(parents=True, exist_ok=True)
df_primary.to_parquet(out_dir / "beta_uk.parquet", index=False)
for fn in ["variables_panel.parquet", "stock_returns.parquet", "consensus_eps.parquet"]:
    shutil.copy(latest(fn), out_dir / fn)
print(f"Saved to {out_dir}")
