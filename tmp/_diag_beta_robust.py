"""Test β^UK robustness: collinearity, filtering, alt vol definitions."""
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

beta = pd.read_parquet(latest("beta_uk.parquet"))

# --- Reload market vols and check correlation ---
START = pd.Timestamp("2010-01-01")
END = pd.Timestamp("2014-12-31")

def monthly_vol(daily, date):
    df = pd.DataFrame({"ret": daily.values, "date": pd.to_datetime(date).values})
    df["ym"] = df["date"].dt.year * 100 + df["date"].dt.month
    g = df.groupby("ym")["ret"].agg(["std", "count"]).reset_index()
    g = g[g["count"] >= 10].rename(columns={"std": "vol"})
    return g[["ym", "vol"]]

ftse = pd.read_csv(ROOT / "inputs" / "Brexit_replication" / "Yahoo_FTSE100" / "FTSE100_yfinance_daily.csv")
ftse["Date"] = pd.to_datetime(ftse["Date"])
ftse = ftse[(ftse["Date"] >= START) & (ftse["Date"] <= END)].sort_values("Date")
ftse["ret"] = ftse["Close"].pct_change()
ftse = ftse.dropna(subset=["ret"])
vol_ftse = monthly_vol(ftse["ret"], ftse["Date"]).rename(columns={"vol": "vol_FTSE"})

fx = pd.read_csv(ROOT / "inputs" / "Brexit_replication" / "BoE" / "USD_GBP_daily_2008-2018.csv")
fx["DATE"] = pd.to_datetime(fx["DATE"], format="%d %b %Y", errors="coerce")
fx = fx[(fx["DATE"] >= START) & (fx["DATE"] <= END)].sort_values("DATE")
fx["ret"] = fx["XUDLUSS"].pct_change()
fx = fx.dropna(subset=["ret"])
vol_fx = monthly_vol(fx["ret"], fx["DATE"]).rename(columns={"vol": "vol_FX"})

# SP500 from one CRSP year (just to get sprtrn)
crsp_2010 = pd.read_parquet(ROOT / "inputs" / "CRSP_DSF" / "CRSP_DSF_2010_Q1.parquet", columns=["date", "sprtrn"])
crsp_years = []
for year in range(2010, 2015):
    for q in (1, 2, 3, 4):
        f = ROOT / "inputs" / "CRSP_DSF" / f"CRSP_DSF_{year}_Q{q}.parquet"
        if f.exists():
            df = pd.read_parquet(f, columns=["date", "sprtrn"])
            crsp_years.append(df)
crsp = pd.concat(crsp_years, ignore_index=True)
crsp["date"] = pd.to_datetime(crsp["date"])
crsp = crsp[["date", "sprtrn"]].dropna().drop_duplicates(subset=["date"]).sort_values("date")
vol_sp = monthly_vol(crsp["sprtrn"], crsp["date"]).rename(columns={"vol": "vol_SP500"})

market = vol_ftse.merge(vol_sp, on="ym").merge(vol_fx, on="ym")
print("--- Market vols correlation matrix (monthly, 2010-2014) ---")
print(market[["vol_FTSE", "vol_SP500", "vol_FX"]].corr().round(3))
print()
print(f"vol_FTSE: mean={market['vol_FTSE'].mean():.4f}  sd={market['vol_FTSE'].std():.4f}")
print(f"vol_SP500: mean={market['vol_SP500'].mean():.4f}  sd={market['vol_SP500'].std():.4f}")
print(f"vol_FX: mean={market['vol_FX'].mean():.4f}  sd={market['vol_FX'].std():.4f}")

# Distribution of β^UK after filtering noisy estimates
print()
print("=" * 80)
print("β^UK distribution after filtering noisy estimates")
print("=" * 80)

filters = [
    ("All", beta),
    ("r² >= 0.10", beta[beta["r2"] >= 0.10]),
    ("r² >= 0.20", beta[beta["r2"] >= 0.20]),
    ("r² >= 0.30", beta[beta["r2"] >= 0.30]),
    ("|β| < 2", beta[beta["beta_uk"].abs() < 2]),
    ("|β| < 1.5", beta[beta["beta_uk"].abs() < 1.5]),
    ("n_months = 60 (full)", beta[beta["n_months"] == 60]),
    ("n_months >= 48", beta[beta["n_months"] >= 48]),
]
print(f"{'Filter':<25}{'N':>8}{'mean':>10}{'sd':>8}{'%β<0':>10}{'p33pos':>10}{'p67pos':>10}")
for name, b in filters:
    pos = b[b["beta_uk"] >= 0]["beta_uk"]
    t1 = pos.quantile(1/3) if len(pos) else np.nan
    t2 = pos.quantile(2/3) if len(pos) else np.nan
    print(f"{name:<25}{len(b):>8,}{b['beta_uk'].mean():>10.3f}{b['beta_uk'].std():>8.2f}"
          f"{(b['beta_uk']<0).mean()*100:>9.1f}%{t1:>10.3f}{t2:>10.3f}")

# --- Now run DiD with various filters and see if sign flips ---
print()
print("=" * 80)
print("DiD with β^UK filters — does sign change?")
print("=" * 80)

panel = pd.read_parquet(latest("variables_panel.parquet"))
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
p = p.merge(beta[["gvkey", "beta_uk", "r2", "n_months"]], on="gvkey", how="left")
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

def did(p, filter_mask, label):
    from linearmodels import PanelOLS
    df = p.copy()
    df = df[filter_mask(df)]
    pos = df[df["beta_uk"] >= 0]["beta_uk"].dropna()
    if len(pos) < 10:
        return
    t1, t2 = pos.quantile(1/3), pos.quantile(2/3)
    df["HIGH_UK"] = (df["beta_uk"] > t2).astype(float)
    df["LOW_UK"] = ((df["beta_uk"] >= 0) & (df["beta_uk"] < t1)).astype(float)
    df = df[(df["HIGH_UK"] == 1) | (df["LOW_UK"] == 1)]
    df = df[df["cal_yr_qtr"].isin([20153, 20154, 20163, 20164])]
    df["POST"] = df["cal_yr_qtr"].isin([20163, 20164]).astype(float)
    df["TREAT_POST"] = df["HIGH_UK"] * df["POST"]
    required = ["CASH_T8"] + [f"{c}_lag1" for c in ctrl_cols]
    df = df.dropna(subset=required)
    if len(df) < 50:
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
    n_t = df["gvkey"][df["HIGH_UK"] == 1].nunique()
    n_c = df["gvkey"][df["LOW_UK"] == 1].nunique()
    sig = "***" if pv < 0.01 else "**" if pv < 0.05 else "*" if pv < 0.10 else ""
    print(f"  {label:<35}  δ={d:+.4f} {sig:<3}  p={pv:.3f}  N={int(res.nobs):>5,}  Ntr={n_t:>4} Nctl={n_c:>4}  t1={t1:.2f} t2={t2:.2f}")

did(p, lambda d: pd.Series(True, index=d.index), "Baseline (no filter)")
did(p, lambda d: d["r2"] >= 0.10, "r² >= 0.10")
did(p, lambda d: d["r2"] >= 0.20, "r² >= 0.20")
did(p, lambda d: d["r2"] >= 0.30, "r² >= 0.30")
did(p, lambda d: d["beta_uk"].abs() < 2, "|β^UK| < 2")
did(p, lambda d: d["beta_uk"].abs() < 1.5, "|β^UK| < 1.5")
did(p, lambda d: d["n_months"] == 60, "n_months = 60 (full window)")
did(p, lambda d: d["n_months"] >= 48, "n_months >= 48")
did(p, lambda d: (d["r2"] >= 0.20) & (d["beta_uk"].abs() < 2), "r²>=0.20 AND |β|<2")
did(p, lambda d: (d["r2"] >= 0.30) & (d["beta_uk"].abs() < 2) & (d["n_months"] >= 48), "Triple filter")
