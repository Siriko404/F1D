"""Rebuild β^UK using VIX as SP500-vol control (instead of realized SP500 vol)."""
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

# Load VIX
vix = yf.download("^VIX", start="2009-12-01", end="2015-02-01", progress=False, auto_adjust=False)
if isinstance(vix.columns, pd.MultiIndex):
    vix.columns = vix.columns.get_level_values(0)
vix = vix.reset_index()
vix["Date"] = pd.to_datetime(vix["Date"])
vix = vix[(vix["Date"] >= START) & (vix["Date"] <= END)].sort_values("Date")
vix["ym"] = vix["Date"].dt.year * 100 + vix["Date"].dt.month
# Monthly mean and monthly end-of-month VIX
vix_mean = vix.groupby("ym")["Close"].mean().reset_index().rename(columns={"Close": "VIX_mean"})
vix_eom = vix.groupby("ym")["Close"].last().reset_index().rename(columns={"Close": "VIX_eom"})
vix_m = vix_mean.merge(vix_eom, on="ym")
print(f"VIX monthly: {len(vix_m)} months  mean={vix_m['VIX_mean'].mean():.2f}  range={vix_m['VIX_mean'].min():.2f}-{vix_m['VIX_mean'].max():.2f}")

# Load FTSE
ftse = pd.read_csv(ROOT / "inputs" / "Brexit_replication" / "Yahoo_FTSE100" / "FTSE100_yfinance_daily.csv")
ftse["Date"] = pd.to_datetime(ftse["Date"])
ftse = ftse[(ftse["Date"] >= START) & (ftse["Date"] <= END)].sort_values("Date")
ftse["ret"] = ftse["Close"].pct_change()
ftse = ftse.dropna(subset=["ret"])
ftse["ym"] = ftse["Date"].dt.year * 100 + ftse["Date"].dt.month
ftse_vol = ftse.groupby("ym")["ret"].std().reset_index().rename(columns={"ret": "vol_FTSE"})

# Load FX
fx = pd.read_csv(ROOT / "inputs" / "Brexit_replication" / "BoE" / "USD_GBP_daily_2008-2018.csv")
fx["DATE"] = pd.to_datetime(fx["DATE"], format="%d %b %Y", errors="coerce")
fx = fx[(fx["DATE"] >= START) & (fx["DATE"] <= END)].sort_values("DATE")
fx["ret"] = fx["XUDLUSS"].pct_change()
fx = fx.dropna(subset=["ret"])
fx["ym"] = fx["DATE"].dt.year * 100 + fx["DATE"].dt.month
fx_vol = fx.groupby("ym")["ret"].std().reset_index().rename(columns={"ret": "vol_FX"})

market = ftse_vol.merge(vix_m, on="ym").merge(fx_vol, on="ym")
print(f"Market panel: {len(market)} months")
print(f"FTSE vol mean: {market['vol_FTSE'].mean():.4f}")
print(f"VIX mean: {market['VIX_mean'].mean():.2f}")
print(f"Correlation FTSE vol vs VIX_mean: {market[['vol_FTSE','VIX_mean']].corr().iloc[0,1]:.4f}")
print(f"Correlation FTSE vol vs VIX_eom: {market[['vol_FTSE','VIX_eom']].corr().iloc[0,1]:.4f}")

# Load CRSP firm returns
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

# Firm-month vol
firm_vol = crsp.groupby(["PERMNO", "ym"])["RET"].agg(["std", "count"]).reset_index()
firm_vol = firm_vol[firm_vol["count"] >= 10].rename(columns={"std": "vol_r"})
firm_vol = firm_vol.merge(market, on="ym")

# CCM
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
ccm["LPERMNO"] = pd.to_numeric(ccm["LPERMNO"], errors="coerce").astype("Int64").dropna()
ccm["LPERMNO"] = ccm["LPERMNO"].astype(int)

ccm_simple = ccm[["gvkey", "LPERMNO", "LINKDT", "LINKENDDT"]].rename(columns={"LPERMNO": "PERMNO"})
firm_vol["ym_date"] = pd.to_datetime((firm_vol["ym"] // 100).astype(str) + "-" +
                                       (firm_vol["ym"] % 100).astype(str).str.zfill(2) + "-15")
merged = firm_vol.merge(ccm_simple, on="PERMNO")
merged = merged[(merged["ym_date"] >= merged["LINKDT"]) & (merged["ym_date"] <= merged["LINKENDDT"])]
merged = merged.drop_duplicates(subset=["gvkey", "ym"], keep="first")
print(f"\nFirm-month obs after CCM: {len(merged):,}")

# Run OLS per firm: vol_r = α + β·vol_FTSE + θ1·VIX_mean + θ2·vol_FX + ε
def run_ols(panel_df, ftse_col="vol_FTSE", sp_col="VIX_mean", fx_col="vol_FX", label=""):
    results = {}
    for gv, gr in panel_df.groupby("gvkey"):
        g = gr.dropna(subset=["vol_r", ftse_col, sp_col, fx_col])
        if len(g) < 24:
            continue
        X = np.column_stack([np.ones(len(g)), g[ftse_col].values, g[sp_col].values, g[fx_col].values])
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
    print(f"\n[{label}] β^UK: N={len(df):,}  mean={df['beta_uk'].mean():.3f}  sd={df['beta_uk'].std():.3f}  "
          f"%β<0={(df['beta_uk']<0).mean()*100:.1f}%")
    pos = df[df["beta_uk"] >= 0]["beta_uk"]
    if len(pos):
        print(f"  nonneg terciles: t1={pos.quantile(1/3):.3f}  t2={pos.quantile(2/3):.3f}")
    return df

# Variant A: my current (vol_FTSE + vol_SP500_realized + vol_FX) — for reference, compute sp realized too
crsp_sp_frames = []
for year in range(2010, 2015):
    for q in (1, 2, 3, 4):
        f = ROOT / "inputs" / "CRSP_DSF" / f"CRSP_DSF_{year}_Q{q}.parquet"
        if f.exists():
            df = pd.read_parquet(f, columns=["date", "sprtrn"])
            crsp_sp_frames.append(df)
crsp_sp = pd.concat(crsp_sp_frames, ignore_index=True)
crsp_sp["date"] = pd.to_datetime(crsp_sp["date"])
crsp_sp = crsp_sp[["date", "sprtrn"]].dropna().drop_duplicates(subset=["date"]).sort_values("date")
crsp_sp["ym"] = crsp_sp["date"].dt.year * 100 + crsp_sp["date"].dt.month
sp_realized = crsp_sp.groupby("ym")["sprtrn"].std().reset_index().rename(columns={"sprtrn": "vol_SP500_real"})

merged_a = merged.merge(sp_realized, on="ym")
df_a = run_ols(merged_a, ftse_col="vol_FTSE", sp_col="vol_SP500_real", fx_col="vol_FX",
                label="A: vol_FTSE + vol_SP500_realized + vol_FX (BASELINE)")

# Variant B: replace SP500 realized with VIX_mean
df_b = run_ols(merged, ftse_col="vol_FTSE", sp_col="VIX_mean", fx_col="vol_FX",
                label="B: vol_FTSE + VIX_mean + vol_FX")

# Variant C: VIX_eom instead
df_c = run_ols(merged, ftse_col="vol_FTSE", sp_col="VIX_eom", fx_col="vol_FX",
                label="C: vol_FTSE + VIX_eom + vol_FX")

# Now run DiD with each β
print("\n" + "=" * 80)
print("DiD on CASH using each β^UK variant")
print("=" * 80)

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

def run_did_with_beta(beta_df, label):
    from linearmodels import PanelOLS
    if len(beta_df) < 100:
        return
    nonneg = beta_df[beta_df["beta_uk"] >= 0]
    t1 = nonneg["beta_uk"].quantile(1/3)
    t2 = nonneg["beta_uk"].quantile(2/3)
    df = p.copy()
    df = df.merge(beta_df[["gvkey", "beta_uk"]], on="gvkey", how="left")
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
    print(f"  {label:<55}  δ={d:+.4f} {sig:<3}  p={pv:.3f}  Ntr={int((df['HIGH_UK']==1).sum())}  N={int(res.nobs):,}")

run_did_with_beta(df_a, "A: SP500_realized")
run_did_with_beta(df_b, "B: VIX_mean")
run_did_with_beta(df_c, "C: VIX_eom")

# Variant D: VIX_mean/100 (rescale to fraction)
merged_d = merged.copy()
merged_d["VIX_div100"] = merged_d["VIX_mean"] / 100.0
df_d = run_ols(merged_d, ftse_col="vol_FTSE", sp_col="VIX_div100", fx_col="vol_FX",
                label="D: vol_FTSE + VIX_mean/100 + vol_FX")
run_did_with_beta(df_d, "D: VIX_mean/100")

# Variant E: monthly std of daily VIX changes (vol of VIX, makes VIX into "shocks")
crsp_sp_frames = []
for year in range(2010, 2015):
    for q in (1, 2, 3, 4):
        f = ROOT / "inputs" / "CRSP_DSF" / f"CRSP_DSF_{year}_Q{q}.parquet"
        if f.exists():
            df = pd.read_parquet(f, columns=["date", "sprtrn"])
            crsp_sp_frames.append(df)

# Variant F: vol(FTSE) AND realized SP500 vol AND VIX (3 controls)
def run_ols_4ctrl(panel_df, ctrls):
    results = {}
    for gv, gr in panel_df.groupby("gvkey"):
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
    return pd.DataFrame([{"gvkey": k, "beta_uk": v[0], "n_months": v[1], "r2": v[2]} for k, v in results.items()])

merged_a_full = merged.merge(sp_realized, on="ym")
df_f = run_ols_4ctrl(merged_a_full, ["vol_FTSE", "vol_SP500_real", "VIX_eom", "vol_FX"])
print(f"\n[F: vol_FTSE + vol_SP500_realized + VIX_eom + vol_FX] β^UK: N={len(df_f):,}  mean={df_f['beta_uk'].mean():.3f}  sd={df_f['beta_uk'].std():.3f}")
pos_f = df_f[df_f["beta_uk"] >= 0]["beta_uk"]
print(f"  nonneg terciles: t1={pos_f.quantile(1/3):.3f}  t2={pos_f.quantile(2/3):.3f}")
run_did_with_beta(df_f, "F: SP500_real + VIX_eom (4 ctrls)")

print("\nPaper benchmark: δ ≈ +0.231 ***")
