"""Test β^UK estimation windows: full (2010-2014), pre-Brexit (2010-2013),
post-crisis (2011-2014). See which makes treated firms more divestiture-heavy."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd
import yfinance as yf

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT / "outputs" / "campello_v2"

def latest(fname):
    runs = sorted([d for d in OUT.iterdir() if d.is_dir() and (d / fname).exists()], reverse=True)
    return runs[0] / fname

vix = yf.download("^VIX", start="2009-12-01", end="2015-02-01", progress=False, auto_adjust=False)
if isinstance(vix.columns, pd.MultiIndex):
    vix.columns = vix.columns.get_level_values(0)
vix = vix.reset_index()
vix["Date"] = pd.to_datetime(vix["Date"])
vix["ym"] = vix["Date"].dt.year * 100 + vix["Date"].dt.month

ftse = pd.read_csv(ROOT / "inputs" / "Brexit_replication" / "Yahoo_FTSE100" / "FTSE100_yfinance_daily.csv")
ftse["Date"] = pd.to_datetime(ftse["Date"])
ftse["ret"] = ftse["Close"].pct_change()
ftse = ftse.dropna(subset=["ret"])
ftse["ym"] = ftse["Date"].dt.year * 100 + ftse["Date"].dt.month

fx = pd.read_csv(ROOT / "inputs" / "Brexit_replication" / "BoE" / "USD_GBP_daily_2008-2018.csv")
fx["DATE"] = pd.to_datetime(fx["DATE"], format="%d %b %Y", errors="coerce")
fx["ret"] = fx["XUDLUSS"].pct_change()
fx = fx.dropna(subset=["ret"])
fx["ym"] = fx["DATE"].dt.year * 100 + fx["DATE"].dt.month

# Load CRSP once
crsp_frames = []
for year in range(2010, 2015):
    for q in (1, 2, 3, 4):
        f = ROOT / "inputs" / "CRSP_DSF" / f"CRSP_DSF_{year}_Q{q}.parquet"
        if f.exists():
            crsp_frames.append(pd.read_parquet(f, columns=["PERMNO", "date", "RET", "sprtrn"]))
crsp = pd.concat(crsp_frames, ignore_index=True)
crsp["date"] = pd.to_datetime(crsp["date"])
crsp["RET"] = pd.to_numeric(crsp["RET"], errors="coerce")
crsp = crsp.dropna(subset=["RET"])
crsp["ym"] = crsp["date"].dt.year * 100 + crsp["date"].dt.month

# CCM linkage
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
ccm["LPERMNO"] = pd.to_numeric(ccm["LPERMNO"], errors="coerce").astype("Int64").dropna().astype(int)
ccm_simple = ccm[["gvkey", "LPERMNO", "LINKDT", "LINKENDDT"]].rename(columns={"LPERMNO": "PERMNO"})

def fit_beta(start, end, label):
    vix_w = vix[(vix["Date"] >= start) & (vix["Date"] <= end)]
    vix_eom = vix_w.groupby("ym")["Close"].last().reset_index().rename(columns={"Close":"VIX"})
    ftse_w = ftse[(ftse["Date"] >= start) & (ftse["Date"] <= end)]
    ftse_vol = ftse_w.groupby("ym")["ret"].std().reset_index().rename(columns={"ret":"vol_FTSE"})
    fx_w = fx[(fx["DATE"] >= start) & (fx["DATE"] <= end)]
    fx_vol = fx_w.groupby("ym")["ret"].std().reset_index().rename(columns={"ret":"vol_FX"})
    crsp_w = crsp[(crsp["date"] >= start) & (crsp["date"] <= end)]
    sp_realized = crsp_w.drop_duplicates(subset=["date"]).groupby("ym")["sprtrn"].std().reset_index().rename(columns={"sprtrn":"vol_SP500"})
    market = ftse_vol.merge(vix_eom, on="ym").merge(fx_vol, on="ym").merge(sp_realized, on="ym")

    firm_vol = crsp_w.groupby(["PERMNO","ym"])["RET"].agg(["std","count"]).reset_index()
    firm_vol = firm_vol[firm_vol["count"] >= 10].rename(columns={"std":"vol_r"})
    firm_vol = firm_vol.merge(market, on="ym")
    firm_vol["ym_date"] = pd.to_datetime((firm_vol["ym"]//100).astype(str) + "-" +
                                          (firm_vol["ym"]%100).astype(str).str.zfill(2) + "-15")
    m = firm_vol.merge(ccm_simple, on="PERMNO")
    m = m[(m["ym_date"] >= m["LINKDT"]) & (m["ym_date"] <= m["LINKENDDT"])]
    m = m.drop_duplicates(subset=["gvkey","ym"], keep="first")

    results = {}
    for gv, gr in m.groupby("gvkey"):
        g = gr.dropna(subset=["vol_r","vol_FTSE","vol_SP500","VIX","vol_FX"])
        if len(g) < 18:
            continue
        X = np.column_stack([np.ones(len(g)), g["vol_FTSE"], g["vol_SP500"], g["VIX"], g["vol_FX"]])
        y = g["vol_r"].values
        try:
            b, *_ = np.linalg.lstsq(X, y, rcond=None)
            results[gv] = b[1]
        except:
            pass
    df = pd.DataFrame([{"gvkey":k, "beta_uk":v} for k,v in results.items()])
    b = df["beta_uk"]; pos = b[b>=0]
    print(f"\n[{label}] N={len(df):,}  mean={b.mean():.4f}  sd={b.std():.4f}  %neg={(b<0).mean()*100:.1f}%")
    print(f"  nonneg terciles: t1={pos.quantile(1/3):.4f}  t2={pos.quantile(2/3):.4f}  (paper 0.28/0.68)")
    return df

# Test 4 windows
df_full = fit_beta(pd.Timestamp("2010-01-01"), pd.Timestamp("2014-12-31"), "Full 2010-2014 [current]")
df_pre  = fit_beta(pd.Timestamp("2010-01-01"), pd.Timestamp("2013-12-31"), "Pre 2010-2013")
df_pre2 = fit_beta(pd.Timestamp("2011-01-01"), pd.Timestamp("2014-12-31"), "Recent 2011-2014")
df_pre3 = fit_beta(pd.Timestamp("2010-01-01"), pd.Timestamp("2015-12-31"), "Long 2010-2015")
