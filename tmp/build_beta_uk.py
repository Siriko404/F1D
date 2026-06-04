"""beta^UK_i per equation (13): vol(r_it) = alpha_i + beta^UK_i * vol(FTSE100_t)
   + theta1 * vol(SP500_t) + theta2 * vol(FX$_t) + eps_it
Monthly 2010:M1-2014:M12. Firm-by-firm OLS.
Validates against paper: 449 treated (beta>0.68), 360 control (beta<0.28)
"""
import pandas as pd, numpy as np
from pathlib import Path

ROOT = Path(".")
MIN_DAYS = 15  # min trading days/month for valid monthly vol
MIN_MONTHS = 24  # min monthly obs/firm for regression

# ── 1. Monthly realized volatility from CRSP daily returns ──────────────
def monthly_rv(df, ret_col, date_col="date", permno_col="PERMNO"):
    """Monthly realized vol = std(daily returns) * sqrt(21) within month"""
    df = df.copy()
    df["year_month"] = df[date_col].dt.to_period("M")
    grp = df.groupby([permno_col, "year_month"])
    n_days = grp[ret_col].count()
    rv = grp[ret_col].std() * np.sqrt(21)
    rv = rv[n_days >= MIN_DAYS]
    return rv.reset_index()

# 1a. Firm returns from CRSP DSF
frames = []
for year in range(2010, 2015):
    for q in range(1, 5):
        f = ROOT / "inputs" / "CRSP_DSF" / f"CRSP_DSF_{year}_Q{q}.parquet"
        if f.exists():
            df = pd.read_parquet(f, columns=["PERMNO", "date", "RET", "sprtrn"])
            frames.append(df)
crsp = pd.concat(frames, ignore_index=True)
crsp["date"] = pd.to_datetime(crsp["date"])
crsp["RET"] = pd.to_numeric(crsp["RET"], errors="coerce")

firm_rv = monthly_rv(crsp, "RET")
firm_rv.columns = ["PERMNO", "year_month", "vol_r"]
print(f"Firm monthly vols: {len(firm_rv):,}")

# 1b. SP500 vol from sprtrn (same for all stocks each day — take unique date values)
crsp_sp = crsp[["date", "sprtrn"]].drop_duplicates()
crsp_sp["sprtrn"] = pd.to_numeric(crsp_sp["sprtrn"], errors="coerce")
crsp_sp["year_month"] = crsp_sp["date"].dt.to_period("M")
sp_grp = crsp_sp.groupby("year_month")
sp500_vol = sp_grp["sprtrn"].std() * np.sqrt(21)
sp500_vol = sp500_vol[sp_grp["sprtrn"].count() >= MIN_DAYS].reset_index()
sp500_vol.columns = ["year_month", "vol_SP500"]
print(f"SP500 monthly vols: {len(sp500_vol):,}")

del crsp

# ── 2. FTSE100 monthly realized vol ─────────────────────────────────────
ftse = pd.read_csv(ROOT / "inputs" / "Brexit_replication" / "Yahoo_FTSE100" / "FTSE100_yfinance_daily.csv")
ftse["Date"] = pd.to_datetime(ftse["Date"])
ftse = ftse[(ftse["Date"] >= "2010-01-01") & (ftse["Date"] <= "2014-12-31")]
# Compute daily log returns
ftse = ftse.sort_values("Date")
ftse["log_ret"] = np.log(ftse["Close"] / ftse["Close"].shift(1))
ftse["year_month"] = ftse["Date"].dt.to_period("M")
ftse_grp = ftse.groupby("year_month")
ftse_vol = ftse_grp["log_ret"].std() * np.sqrt(21)
ftse_vol = ftse_vol[ftse_grp["log_ret"].count() >= MIN_DAYS].reset_index()
ftse_vol.columns = ["year_month", "vol_FTSE100"]
print(f"FTSE100 monthly vols: {len(ftse_vol):,}")

# ── 3. FX monthly realized vol ──────────────────────────────────────────
fx = pd.read_csv(ROOT / "inputs" / "Brexit_replication" / "BoE" / "USD_GBP_daily_2008-2018.csv")
fx["DATE"] = pd.to_datetime(fx["DATE"], dayfirst=True)
fx = fx[(fx["DATE"] >= "2010-01-01") & (fx["DATE"] <= "2014-12-31")]
fx = fx.sort_values("DATE")
fx["log_ret"] = np.log(fx["XUDLUSS"] / fx["XUDLUSS"].shift(1))
fx["year_month"] = fx["DATE"].dt.to_period("M")
fx_grp = fx.groupby("year_month")
fx_vol = fx_grp["log_ret"].std() * np.sqrt(21)
fx_vol = fx_vol[fx_grp["log_ret"].count() >= MIN_DAYS].reset_index()
fx_vol.columns = ["year_month", "vol_FX"]
print(f"FX monthly vols: {len(fx_vol):,}")

# ── 4. Merge macro vols ─────────────────────────────────────────────────
macro = sp500_vol.merge(ftse_vol, on="year_month").merge(fx_vol, on="year_month")
print(f"Macro panel: {len(macro):,} months")

# ── 5. Per-firm OLS ─────────────────────────────────────────────────────
firm_rv["year_month"] = firm_rv["year_month"].astype(str)
macro["year_month"] = macro["year_month"].astype(str)
merged = firm_rv.merge(macro, on="year_month", how="inner")

results = []
for permno, grp in merged.groupby("PERMNO"):
    grp = grp.dropna(subset=["vol_r", "vol_FTSE100", "vol_SP500", "vol_FX"])
    if len(grp) < MIN_MONTHS:
        continue
    y = grp["vol_r"].values
    X = np.column_stack([grp["vol_FTSE100"].values,
                         grp["vol_SP500"].values,
                         grp["vol_FX"].values])
    X = np.column_stack([np.ones(len(y)), X])
    try:
        beta = np.linalg.lstsq(X, y, rcond=None)[0]
        yhat = X @ beta
        ss_res = np.sum((y - yhat)**2)
        ss_tot = np.sum((y - y.mean())**2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
        results.append({"PERMNO": permno, "alpha": beta[0],
                        "beta_uk": beta[1], "beta_sp500": beta[2],
                        "beta_fx": beta[3], "n_months": len(grp), "r2": r2})
    except np.linalg.LinAlgError:
        continue

betas = pd.DataFrame(results)
print(f"\nFirms with beta: {len(betas):,}")

# ── 6. Map PERMNO -> gvkey via CCM ──────────────────────────────────────
ccm = pd.read_parquet(ROOT / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet",
    columns=["gvkey", "LPERMNO", "LINKDT", "LINKENDDT", "LINKTYPE", "LINKPRIM"])
ccm["gvkey"] = ccm["gvkey"].astype(str).str.zfill(6)
ccm = ccm[ccm["LINKTYPE"].isin(["LU", "LC"])]
ccm = ccm[ccm["LINKPRIM"].isin(["P", "C"])]
ccm["LINKDT"] = pd.to_datetime(ccm["LINKDT"], errors="coerce")
ccm["LINKENDDT"] = pd.to_datetime(ccm["LINKENDDT"], errors="coerce")
ccm["LINKENDDT"] = ccm["LINKENDDT"].fillna(pd.Timestamp("2099-12-31"))
ccm = ccm[(ccm["LINKENDDT"] >= pd.Timestamp("2010-01-01")) &
          (ccm["LINKDT"] <= pd.Timestamp("2014-12-31"))]
ccm["LPERMNO"] = pd.to_numeric(ccm["LPERMNO"], errors="coerce").astype("Int64")
ccm = ccm.dropna(subset=["LPERMNO"])

betas = betas.merge(ccm[["gvkey", "LPERMNO"]].drop_duplicates(),
                     left_on="PERMNO", right_on="LPERMNO", how="inner")
betas = betas.drop_duplicates(subset=["gvkey"], keep="first")  # one beta per firm
print(f"After CCM merge: {len(betas):,} firms")

# ── 7. Terciles (nonnegative range only) ─────────────────────────────────
bpos = betas[betas["beta_uk"] >= 0].copy()
top_thresh = bpos["beta_uk"].quantile(2/3)
bot_thresh = bpos["beta_uk"].quantile(1/3)
treated = bpos[bpos["beta_uk"] >= top_thresh]
control = bpos[bpos["beta_uk"] <= bot_thresh]

print(f"\n--- beta^UK_i Results ---")
print(f"Total firms: {len(betas):,}")
print(f"Nonnegative range: {len(bpos):,}")
print(f"Top tercile threshold: {top_thresh:.4f}")
print(f"Bottom tercile threshold: {bot_thresh:.4f}")
print(f"Treated (beta > {top_thresh:.2f}): {len(treated):,}")
print(f"Control (beta < {bot_thresh:.2f}): {len(control):,}")
print(f"\nPaper targets:")
print(f"  Treated: 449 firms, beta > 0.68")
print(f"  Control: 360 firms, beta < 0.28")
print(f"beta_uk mean={betas['beta_uk'].mean():.4f} SD={betas['beta_uk'].std():.4f}")
print(f"beta_uk (nonneg) mean={bpos['beta_uk'].mean():.4f} SD={bpos['beta_uk'].std():.4f}")
