"""Test alternative β^UK constructions to find one matching paper's +0.231.

Variants:
  A. Baseline (current): vol_r = α + β·vol(FTSE) + θ1·vol(SP500) + θ2·vol(FX) + ε
  B. No SP500 control:   vol_r = α + β·vol(FTSE) + θ2·vol(FX) + ε
  C. No FX control:       vol_r = α + β·vol(FTSE) + θ1·vol(SP500) + ε
  D. Univariate:          vol_r = α + β·vol(FTSE) + ε
  E. Log-returns vol:     vol computed on log(1+R) instead of R
  F. Realized variance:   use sum of squared daily returns (RV) instead of std
  G. Sum-abs returns:     use sum of |daily returns| within month
"""
import warnings
warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT / "outputs" / "campello_v2"

def latest(fname):
    runs = sorted([d for d in OUT.iterdir() if d.is_dir() and (d / fname).exists()], reverse=True)
    return runs[0] / fname

START = pd.Timestamp("2010-01-01")
END = pd.Timestamp("2014-12-31")

def vol_std(rets):
    return rets.std()

def vol_var(rets):
    return (rets ** 2).sum()  # realized variance

def vol_abs(rets):
    return rets.abs().sum()  # sum absolute returns

def monthly_agg(daily_rets, dates, fn):
    df = pd.DataFrame({"ret": daily_rets.values, "date": pd.to_datetime(dates).values})
    df["ym"] = df["date"].dt.year * 100 + df["date"].dt.month
    grp = df.groupby("ym")["ret"]
    out = pd.DataFrame({"vol": grp.apply(fn), "count": grp.count()}).reset_index()
    out = out[out["count"] >= 10]
    return out[["ym", "vol"]]

# Load FTSE
ftse = pd.read_csv(ROOT / "inputs" / "Brexit_replication" / "Yahoo_FTSE100" / "FTSE100_yfinance_daily.csv")
ftse["Date"] = pd.to_datetime(ftse["Date"])
ftse = ftse[(ftse["Date"] >= START) & (ftse["Date"] <= END)].sort_values("Date").reset_index(drop=True)
ftse["ret"] = ftse["Close"].pct_change()
ftse["log_ret"] = np.log(ftse["Close"] / ftse["Close"].shift(1))
ftse = ftse.dropna(subset=["ret"])

# Load FX
fx = pd.read_csv(ROOT / "inputs" / "Brexit_replication" / "BoE" / "USD_GBP_daily_2008-2018.csv")
fx["DATE"] = pd.to_datetime(fx["DATE"], format="%d %b %Y", errors="coerce")
fx = fx[(fx["DATE"] >= START) & (fx["DATE"] <= END)].sort_values("DATE")
fx["ret"] = fx["XUDLUSS"].pct_change()
fx["log_ret"] = np.log(fx["XUDLUSS"] / fx["XUDLUSS"].shift(1))
fx = fx.dropna(subset=["ret"])

# Load CRSP for SP500 + firm returns
crsp_frames = []
for year in range(2010, 2015):
    for q in (1, 2, 3, 4):
        f = ROOT / "inputs" / "CRSP_DSF" / f"CRSP_DSF_{year}_Q{q}.parquet"
        if f.exists():
            df = pd.read_parquet(f, columns=["PERMNO", "date", "RET", "sprtrn"])
            crsp_frames.append(df)
crsp = pd.concat(crsp_frames, ignore_index=True)
crsp["date"] = pd.to_datetime(crsp["date"])
crsp["RET"] = pd.to_numeric(crsp["RET"], errors="coerce")
crsp["sprtrn"] = pd.to_numeric(crsp["sprtrn"], errors="coerce")
crsp = crsp.dropna(subset=["RET"])
crsp["log_RET"] = np.log(1 + crsp["RET"])

print(f"CRSP loaded: {len(crsp):,} obs, {crsp['PERMNO'].nunique():,} permnos")

# Load CCM links
ccm = pd.read_parquet(ROOT / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet",
                      columns=["gvkey", "LPERMNO", "LINKDT", "LINKENDDT", "LINKTYPE", "LINKPRIM"])
ccm["gvkey"] = ccm["gvkey"].astype(str).str.zfill(6)
panel = pd.read_parquet(latest("variables_panel.parquet"))
sample_gv = set(panel["gvkey"].unique())
ccm = ccm[ccm["gvkey"].isin(sample_gv)]
ccm = ccm[ccm["LINKTYPE"].isin(["LU", "LC"])]
ccm = ccm[ccm["LINKPRIM"].isin(["P", "C"])]
ccm["LINKDT"] = pd.to_datetime(ccm["LINKDT"], errors="coerce")
ccm["LINKENDDT"] = pd.to_datetime(ccm["LINKENDDT"], errors="coerce").fillna(pd.Timestamp("2099-12-31"))
ccm = ccm[(ccm["LINKENDDT"] >= START) & (ccm["LINKDT"] <= END)]
ccm["LPERMNO"] = pd.to_numeric(ccm["LPERMNO"], errors="coerce").astype("Int64")
ccm = ccm.dropna(subset=["LPERMNO"])

def build_beta(vol_fn, returns_col, label):
    """Build β^UK with given vol function and returns column."""
    # Compute market vols
    vol_ftse_df = monthly_agg(ftse[returns_col], ftse["Date"], vol_fn).rename(columns={"vol": "vol_FTSE"})
    vol_fx_df = monthly_agg(fx[returns_col], fx["DATE"], vol_fn).rename(columns={"vol": "vol_FX"})
    sp = crsp[["date", "sprtrn" if returns_col == "ret" else "sprtrn"]].dropna().drop_duplicates(subset=["date"]).sort_values("date")
    if returns_col == "log_ret":
        sp["v"] = np.log(1 + sp["sprtrn"])
    else:
        sp["v"] = sp["sprtrn"]
    vol_sp_df = monthly_agg(sp["v"], sp["date"], vol_fn).rename(columns={"vol": "vol_SP500"})

    market = vol_ftse_df.merge(vol_sp_df, on="ym").merge(vol_fx_df, on="ym")

    # Firm vols
    crsp_col = "RET" if returns_col == "ret" else "log_RET"
    crsp_v = crsp[["PERMNO", "date"]].copy()
    crsp_v["v"] = crsp[crsp_col]
    crsp_v["ym"] = crsp_v["date"].dt.year * 100 + crsp_v["date"].dt.month
    grp2 = crsp_v.groupby(["PERMNO", "ym"])["v"]
    g = pd.DataFrame({"vol_r": grp2.apply(vol_fn), "count": grp2.count()}).reset_index()
    g = g[g["count"] >= 10]

    # Link to gvkey
    ccm_s = ccm[["gvkey", "LPERMNO", "LINKDT", "LINKENDDT"]].rename(columns={"LPERMNO": "PERMNO"})
    ccm_s["PERMNO"] = ccm_s["PERMNO"].astype(int)
    g = g.merge(market, on="ym")
    g["ym_date"] = pd.to_datetime((g["ym"] // 100).astype(str) + "-" +
                                    (g["ym"] % 100).astype(str).str.zfill(2) + "-15")
    g = g.merge(ccm_s, on="PERMNO")
    g = g[(g["ym_date"] >= g["LINKDT"]) & (g["ym_date"] <= g["LINKENDDT"])]
    g = g.drop_duplicates(subset=["gvkey", "ym"], keep="first")

    return g

def run_ols_per_firm(panel_df, controls):
    """controls = list of column names: subset of ['vol_FTSE','vol_SP500','vol_FX']."""
    results = {}
    for gv, gr in panel_df.groupby("gvkey"):
        g = gr.dropna(subset=["vol_r"] + controls)
        if len(g) < 24:
            continue
        X = np.column_stack([np.ones(len(g))] + [g[c].values for c in controls])
        y = g["vol_r"].values
        try:
            b, *_ = np.linalg.lstsq(X, y, rcond=None)
            yp = X @ b
            ss_res = ((y - yp) ** 2).sum()
            ss_tot = ((y - y.mean()) ** 2).sum()
            r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
            results[gv] = (b[1], len(g), r2)  # b[1] = β on first control = vol_FTSE
        except np.linalg.LinAlgError:
            continue
    return pd.DataFrame([{"gvkey": k, "beta_uk": v[0], "n_months": v[1], "r2": v[2]}
                         for k, v in results.items()])

# Build firm-vol panels for each vol function + return col
panels = {}
for (vfn, vlabel) in [(vol_std, "std"), (vol_var, "var"), (vol_abs, "abs")]:
    for retcol in ["ret", "log_ret"]:
        key = f"{vlabel}_{retcol}"
        print(f"Building {key}...")
        panels[key] = build_beta(vfn, retcol, key)

# Run DiD setup
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

def run_did(beta_df, label):
    from linearmodels import PanelOLS
    if len(beta_df) < 100:
        print(f"  {label:<50}  SKIP (too few β estimates: {len(beta_df)})")
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
    if len(df) < 50:
        print(f"  {label:<50}  SKIP (too few obs: {len(df)})")
        return
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
    print(f"  {label:<50}  δ={d:+.4f} {sig:<3}  p={pv:.3f}  Nβ={len(beta_df)}  t1={t1:.3f} t2={t2:.3f}  N={int(res.nobs):,}")

print("\n" + "=" * 100)
print("Alt β^UK specifications: vol formula × control set × return type")
print("=" * 100)

for key, panel_df in panels.items():
    # 4 control combos
    for controls, clabel in [
        (["vol_FTSE", "vol_SP500", "vol_FX"], "ALL3"),
        (["vol_FTSE", "vol_SP500"], "noFX"),
        (["vol_FTSE", "vol_FX"], "noSP500"),
        (["vol_FTSE"], "uniFTSE"),
    ]:
        bdf = run_ols_per_firm(panel_df, controls)
        run_did(bdf, f"{key:<14}  {clabel}")
