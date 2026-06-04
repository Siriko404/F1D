"""Test 2-stage β^UK: residualize firm-vol on US uncertainty first."""
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

START = pd.Timestamp("2010-01-01")
END = pd.Timestamp("2014-12-31")

# Load market vols (same as before)
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

# CRSP realized SP500 vol
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
sp_realized = crsp_sp.groupby("ym")["sprtrn"].std().reset_index().rename(columns={"sprtrn": "vol_SP500"})

market = ftse_vol.merge(sp_realized, on="ym").merge(vix_eom, on="ym").merge(fx_vol, on="ym")
print(f"Market panel: {len(market)} months")

# Firm vol
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

# CCM merge
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

# Variant G: 2-stage residualization
# Stage 1: vol_r = α + γ·VIX + ε (residualize on US uncertainty)
# Stage 2: ε = β^UK·vol_FTSE + θ·vol_FX + e
# β^UK from stage 2 captures UK-specific vol response
results_g = {}
for gv, gr in merged.groupby("gvkey"):
    g = gr.dropna(subset=["vol_r", "vol_FTSE", "VIX", "vol_FX"])
    if len(g) < 24:
        continue
    # Stage 1
    X1 = np.column_stack([np.ones(len(g)), g["VIX"].values])
    b1, *_ = np.linalg.lstsq(X1, g["vol_r"].values, rcond=None)
    resid = g["vol_r"].values - X1 @ b1
    # Stage 2
    X2 = np.column_stack([np.ones(len(g)), g["vol_FTSE"].values, g["vol_FX"].values])
    b2, *_ = np.linalg.lstsq(X2, resid, rcond=None)
    yp = X2 @ b2
    ss_res = ((resid - yp) ** 2).sum()
    ss_tot = ((resid - resid.mean()) ** 2).sum()
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
    results_g[gv] = (b2[1], len(g), r2)

df_g = pd.DataFrame([{"gvkey": k, "beta_uk": v[0], "n_months": v[1], "r2": v[2]}
                      for k, v in results_g.items()])
print(f"\n[G: 2-stage (resid on VIX, then on FTSE+FX)] β^UK: N={len(df_g):,}")
b = df_g["beta_uk"]
print(f"  mean={b.mean():.3f}  sd={b.std():.3f}  %β<0={(b<0).mean()*100:.1f}%")
pos = b[b >= 0]
print(f"  nonneg terciles: t1={pos.quantile(1/3):.3f}  t2={pos.quantile(2/3):.3f}")

# Variant H: 2-stage with SP500_real (paper's exact specification but in 2 stages)
results_h = {}
for gv, gr in merged.groupby("gvkey"):
    g = gr.dropna(subset=["vol_r", "vol_FTSE", "vol_SP500", "vol_FX"])
    if len(g) < 24:
        continue
    X1 = np.column_stack([np.ones(len(g)), g["vol_SP500"].values])
    b1, *_ = np.linalg.lstsq(X1, g["vol_r"].values, rcond=None)
    resid = g["vol_r"].values - X1 @ b1
    X2 = np.column_stack([np.ones(len(g)), g["vol_FTSE"].values, g["vol_FX"].values])
    b2, *_ = np.linalg.lstsq(X2, resid, rcond=None)
    yp = X2 @ b2
    ss_res = ((resid - yp) ** 2).sum()
    ss_tot = ((resid - resid.mean()) ** 2).sum()
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
    results_h[gv] = (b2[1], len(g), r2)

df_h = pd.DataFrame([{"gvkey": k, "beta_uk": v[0], "n_months": v[1], "r2": v[2]}
                      for k, v in results_h.items()])
print(f"\n[H: 2-stage (resid on SP500_real, then on FTSE+FX)] β^UK: N={len(df_h):,}")
b = df_h["beta_uk"]
print(f"  mean={b.mean():.3f}  sd={b.std():.3f}  %β<0={(b<0).mean()*100:.1f}%")
pos = b[b >= 0]
print(f"  nonneg terciles: t1={pos.quantile(1/3):.3f}  t2={pos.quantile(2/3):.3f}")

# Now test DiD with these
sret = pd.read_parquet(latest("stock_returns.parquet"))
ceps = pd.read_parquet(latest("consensus_eps.parquet"))
comp = pd.read_parquet(ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet",
                      columns=["gvkey", "datadate", "atq", "cheq"])
comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
comp["datadate"] = pd.to_datetime(comp["datadate"])
comp["atq"] = pd.to_numeric(comp["atq"], errors="coerce")
comp["cheq"] = pd.to_numeric(comp["cheq"], errors="coerce")
comp = comp.drop_duplicates(subset=["gvkey", "datadate"], keep="last")

p = panel.merge(sret, on=["gvkey", "cal_yr_qtr"], how="left")
p = p.merge(ceps, on=["gvkey", "cal_yr_qtr"], how="left")
p = p.merge(comp[["gvkey", "datadate", "cheq"]], on=["gvkey", "datadate"], how="left",
            suffixes=("_p", ""))
p = p.sort_values(["gvkey", "cal_yr_qtr"])
p["atq_lag1_q"] = p.groupby("gvkey")["atq"].shift(1)
p["cheq_lag1_q"] = p.groupby("gvkey")["cheq"].shift(1)
denom = p["atq_lag1_q"] - p["cheq_lag1_q"]
p["CASH_T8"] = np.where(denom.notna() & (denom > 0), p["cheq"] / denom, np.nan)
p["CASH_T8"] = p["CASH_T8"].replace([np.inf, -np.inf], np.nan)
nv = pd.Series(np.nan, index=p.index)
for q, idx in p.groupby("cal_yr_qtr").groups.items():
    v = p.loc[idx, "CASH_T8"]
    if v.notna().sum() >= 10:
        lo, hi = v.quantile(0.01), v.quantile(0.99)
        nv.loc[idx] = v.clip(lo, hi)
    else:
        nv.loc[idx] = v
p["CASH_T8"] = nv

ctrl_cols = ["STOCK_RETURNS", "TOBIN_Q", "CASH_FLOW", "SIZE", "SALES_GROWTH", "CONSENSUS_EPS"]
for c in ctrl_cols:
    p[f"{c}_lag1"] = p.groupby("gvkey")[c].shift(1)

def did(bdf, label):
    from linearmodels import PanelOLS
    nonneg = bdf[bdf["beta_uk"] >= 0]
    t1 = nonneg["beta_uk"].quantile(1/3)
    t2 = nonneg["beta_uk"].quantile(2/3)
    df = p.merge(bdf[["gvkey", "beta_uk"]], on="gvkey", how="left")
    df["HIGH_UK"] = (df["beta_uk"] > t2).astype(float)
    df["LOW_UK"] = ((df["beta_uk"] >= 0) & (df["beta_uk"] < t1)).astype(float)
    df = df[(df["HIGH_UK"] == 1) | (df["LOW_UK"] == 1)]
    df = df[df["cal_yr_qtr"].isin([20153, 20154, 20163, 20164])]
    df["POST"] = df["cal_yr_qtr"].isin([20163, 20164]).astype(float)
    df["TREAT_POST"] = df["HIGH_UK"] * df["POST"]
    required = ["CASH_T8"] + [f"{c}_lag1" for c in ctrl_cols]
    df = df.dropna(subset=required)
    df["firm_id"] = df["gvkey"].astype("category").cat.codes
    df["time_id"] = df["cal_yr_qtr"]
    df["sic2"] = df["sic"].fillna(-1).astype(int) // 100
    df["ind_qtr"] = df["sic2"].astype(str) + "_" + df["cal_yr_qtr"].astype(str)
    df_idx = df.set_index(["firm_id", "time_id"])
    y = df_idx["CASH_T8"]
    X_cols = ["TREAT_POST"] + [f"{c}_lag1" for c in ctrl_cols]
    iq_dum = pd.get_dummies(df_idx["ind_qtr"], prefix="iq", drop_first=True).astype(float)
    X = pd.concat([df_idx[X_cols], iq_dum], axis=1)
    m = PanelOLS(y, X, entity_effects=True, drop_absorbed=True)
    res = m.fit(cov_type="clustered", cluster_entity=True, cluster_time=True)
    d = res.params["TREAT_POST"]
    pv = res.pvalues["TREAT_POST"]
    sig = "***" if pv < 0.01 else "**" if pv < 0.05 else "*" if pv < 0.10 else ""
    print(f"  {label:<50}  δ={d:+.4f} {sig:<3}  p={pv:.3f}  t1={t1:.3f} t2={t2:.3f}  N={int(res.nobs):,}")

print("\n=== DiD on CASH_T8 ===")
did(df_g, "G: 2-stage (VIX → FTSE+FX)")
did(df_h, "H: 2-stage (SP500_real → FTSE+FX)")
print("\nPaper: δ ≈ +0.231 ***")
