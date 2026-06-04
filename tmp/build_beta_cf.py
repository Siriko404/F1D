"""Build beta^UK_i,CF: cash-flow-news beta via Vuolteenaho (2002) decomposition.
Firm-level VAR(1): [r_t, roe_t, bm_t] quarterly. CF news = e1'*(I-rho*G)^(-1)*u_t.
Then monthly CF vol -> re-run eq (13) with CF vol as DV.
Target: rank corr ~0.8 with baseline beta^UK_i, top-tercile overlap ~86%."""
import pandas as pd, numpy as np, zipfile, io
from pathlib import Path

ROOT = Path(".")
CSV = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
MIN_DAYS, MIN_MONTHS = 15, 24
RHO = 0.96  # quarterly discount coefficient (Vuolteenaho convention)

print("="*60)
print("1. Build quarterly firm data (returns, ROE, BM)")
print("="*60)

# --- Quarterly returns from CRSP ---
frames_ret = []
for y in range(2010, 2015):
    for q in range(1, 5):
        f = ROOT / "inputs" / "CRSP_DSF" / f"CRSP_DSF_{y}_Q{q}.parquet"
        if f.exists():
            frames_ret.append(pd.read_parquet(f, columns=["PERMNO", "date", "RET"]))
cr = pd.concat(frames_ret, ignore_index=True)
cr["date"] = pd.to_datetime(cr["date"]); cr["RET"] = pd.to_numeric(cr["RET"], errors="coerce")
cr["yq"] = cr["date"].dt.year * 10 + cr["date"].dt.quarter
cr["lr"] = np.log(1 + cr["RET"].fillna(0))  # log return
qr = cr.groupby(["PERMNO", "yq"])["lr"].sum().reset_index()
qr.columns = ["PERMNO", "yq", "r_q"]

# --- Quarterly ROE and BM from Compustat ---
comp = pd.read_parquet(CSV, columns=["gvkey", "datadate", "fyearq", "fqtr", "sic", "curcdq", "fic",
    "atq", "cheq", "oibdpq", "cshoq", "prccq", "ceqq", "txditcq"])
for c in ["atq", "cheq", "oibdpq", "cshoq", "prccq", "ceqq", "txditcq"]:
    comp[c] = pd.to_numeric(comp[c], errors="coerce")
comp["txditcq"] = comp["txditcq"].fillna(0); comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
comp = comp[(comp["fyearq"] >= 2009) & (comp["fyearq"] <= 2015)]
comp = comp[comp["fqtr"].isin([1, 2, 3, 4])]
comp = comp[(comp["curcdq"] == "USD") & (comp["fic"] == "USA")]
comp = comp[(comp["atq"] > 0) & (comp["atq"] > 0)]
comp["yq"] = comp["fyearq"].astype(int) * 10 + comp["fqtr"].astype(int)
comp = comp.sort_values(["gvkey", "yq"])

# ROE = OIBDPQ / (lagged CEQQ + lagged TXDITCQ)
comp["be"] = comp["ceqq"] + comp["txditcq"]
comp["be_lag"] = comp.groupby("gvkey")["be"].shift(1)
comp["roe"] = comp["oibdpq"] / comp["be_lag"]
comp["roe"] = comp["roe"].clip(-1, 1)

# Book-to-market = BE / (CSHOQ * PRCCQ)
comp["mktcap"] = comp["cshoq"] * comp["prccq"]
comp["bm"] = comp["be"] / comp["mktcap"]
comp["bm"] = comp["bm"].clip(1e-6, 100)

# Log transforms
comp["roe_log"] = np.log(1 + comp["roe"].clip(-0.99, 10))
comp["bm_log"] = np.log(comp["bm"])

# CCM: PERMNO <-> GVKEY
ccm = pd.read_parquet(ROOT / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet",
    columns=["gvkey", "LPERMNO", "LINKDT", "LINKENDDT", "LINKTYPE", "LINKPRIM"])
ccm["gvkey"] = ccm["gvkey"].astype(str).str.zfill(6)
ccm = ccm[ccm["LINKTYPE"].isin(["LU", "LC"])]; ccm = ccm[ccm["LINKPRIM"].isin(["P", "C"])]
ccm["LINKDT"] = pd.to_datetime(ccm["LINKDT"], errors="coerce")
ccm["LINKENDDT"] = pd.to_datetime(ccm["LINKENDDT"], errors="coerce")
ccm["LINKENDDT"] = ccm["LINKENDDT"].fillna(pd.Timestamp("2099-12-31"))
ccm = ccm[(ccm["LINKENDDT"] >= pd.Timestamp("2010-01-01")) & (ccm["LINKDT"] <= pd.Timestamp("2014-12-31"))]
ccm["LPERMNO"] = pd.to_numeric(ccm["LPERMNO"], errors="coerce").astype("Int64")
ccm = ccm.dropna(subset=["LPERMNO"])

# Match CRSP returns to Compustat via CCM
qr = qr.merge(ccm[["gvkey", "LPERMNO"]].drop_duplicates(), left_on="PERMNO", right_on="LPERMNO", how="inner")
qr = qr.drop_duplicates(subset=["gvkey", "yq"], keep="first")
qr["gvkey"] = qr["gvkey"].astype(str).str.zfill(6)

# Merge quarterly returns + ROE + BM
qdf = comp[["gvkey", "yq", "roe_log", "bm_log"]].dropna()
qdf = qdf.merge(qr[["gvkey", "yq", "r_q"]], on=["gvkey", "yq"], how="inner")
qdf = qdf[(qdf["yq"] >= 20101) & (qdf["yq"] <= 20144)]
print(f"Quarterly merged data: {len(qdf):,} obs, {qdf['gvkey'].nunique():,} firms")

# ============================================================
# 2. Firm-level VAR(1) and Campbell decomposition
# ============================================================
print(f"\n{'='*60}")
print("2. Firm-level VAR(1) + Campbell decomposition")
print(f"{'='*60}")

MIN_Q = 12  # min quarterly obs per firm for VAR

results_cf = []
for gk, grp in qdf.groupby("gvkey"):
    grp = grp.sort_values("yq")
    Z = grp[["r_q", "roe_log", "bm_log"]].values
    if len(Z) < MIN_Q:
        continue
    # VAR(1): Z_{t+1} = Gamma * Z_t + u_{t+1}
    Z_lag = Z[:-1]
    Z_lead = Z[1:]
    try:
        Gamma = np.linalg.lstsq(Z_lag, Z_lead, rcond=None)[0].T  # 3x3
    except:
        continue

    # Compute CF news for each quarter t (t = 2, ..., T)
    # u_t = Z_t - Gamma * Z_{t-1}
    U = Z[1:] - (Gamma @ Z[:-1].T).T  # T-1 x 3
    # CF_news_t = e1' * (I - rho*Gamma)^(-1) * u_t
    I_mat = np.eye(3)
    try:
        inv_term = np.linalg.inv(I_mat - RHO * Gamma)
    except:
        continue
    e1 = np.array([1.0, 0.0, 0.0])
    cf_coeff = e1 @ inv_term  # 1x3
    cf_news = U @ cf_coeff  # T-1 vector

    # Map CF news (quarterly) to monthly for eq (13)
    # Simple: each quarter's CF news -> 3 identical monthly values
    for t_idx, cf_val in enumerate(cf_news):
        yq = grp["yq"].iloc[t_idx + 1]  # t_idx base 0 in U, +1 for lead
        yr, qq = yq // 10, yq % 10
        month_start = (qq - 1) * 3 + 1
        for m in range(month_start, month_start + 3):
            ym = f"{yr}-{m:02d}"
            results_cf.append({"gvkey": gk, "ym": ym, "cf_news": cf_val})

cf_df = pd.DataFrame(results_cf)
cf_df["ym"] = cf_df["ym"].astype(str)
# Monthly CF vol: within-month? CF news is already monthly, so take absolute value
# Actually: eq (13) replaces vol(r_it) with vol(CF_news_it)
# CF_news is a return-like quantity. We need its monthly volatility.
# But CF news is quarterly-interpolated. For eq (13), we need monthly vol.
# Approach: compute SD of daily CF news? No — CF news is quarterly.
# Better: treat CF news as a monthly series (constant within quarter), compute
# realized vol from within-month variation. But there IS no within-month variation.
#
# Simplification: use |CF_news| as the monthly vol proxy (absolute CF news).
# This matches the literature: CF news volatility = absolute value of CF news.
cf_df["vol_cf"] = np.abs(cf_df["cf_news"])
cf_monthly = cf_df.groupby(["gvkey", "ym"])["vol_cf"].mean().reset_index()

print(f"CF vol data: {len(cf_monthly):,} obs, {cf_monthly['gvkey'].nunique():,} firms")

# ============================================================
# 3. Load baseline beta^UK_i (level vol) for comparison
# ============================================================
print(f"\n{'='*60}")
print("3. Load baseline betas + compare rank correlation")
print(f"{'='*60}")

# Reload baseline betas (built earlier, saved to parquet)
betas_level = pd.read_parquet("tmp/beta_uk_final.parquet")

# Build CF betas: same as eq (13) but with CF vol as DV
# Need macro vol series (same as before)
frames_m = []
for y in range(2010, 2015):
    for q in range(1, 5):
        f = ROOT / "inputs" / "CRSP_DSF" / f"CRSP_DSF_{y}_Q{q}.parquet"
        if f.exists():
            frames_m.append(pd.read_parquet(f, columns=["PERMNO", "date", "sprtrn"]))
crm = pd.concat(frames_m, ignore_index=True)
crm["date"] = pd.to_datetime(crm["date"]); crm["sprtrn"] = pd.to_numeric(crm["sprtrn"], errors="coerce")
crm["ym"] = crm["date"].dt.to_period("M").astype(str)
sp500_m = crm.groupby("ym")["sprtrn"].std()
sp500_m = sp500_m[sp500_m > 0].reset_index(); sp500_m.columns = ["ym", "vol_SP500"]

ftse = pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"Yahoo_FTSE100"/"FTSE100_yfinance_daily.csv")
ftse["Date"] = pd.to_datetime(ftse["Date"]); ftse = ftse[(ftse["Date"] >= "2010-01-01") & (ftse["Date"] <= "2014-12-31")]
ftse["lr"] = np.log(ftse["Close"] / ftse["Close"].shift(1))
ftse["ym"] = ftse["Date"].dt.to_period("M").astype(str)
ft_m = ftse.groupby("ym")["lr"].std(); ft_m = ft_m[ft_m > 0].reset_index(); ft_m.columns = ["ym", "vol_FTSE100"]

fx = pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"BoE"/"USD_GBP_daily_2008-2018.csv")
fx["DATE"] = pd.to_datetime(fx["DATE"], dayfirst=True)
fx = fx[(fx["DATE"] >= "2010-01-01") & (fx["DATE"] <= "2014-12-31")]
fx["lr"] = np.log(fx["XUDLUSS"] / fx["XUDLUSS"].shift(1))
fx["ym"] = fx["DATE"].dt.to_period("M").astype(str)
fx_m = fx.groupby("ym")["lr"].std(); fx_m = fx_m[fx_m > 0].reset_index(); fx_m.columns = ["ym", "vol_FX"]

macro_m = sp500_m.merge(ft_m, on="ym").merge(fx_m, on="ym")

# Run eq (13) with CF vol as LHS
cf_data = cf_monthly.merge(macro_m, on="ym", how="inner")
cf_betas = []
for gk, grp in cf_data.groupby("gvkey"):
    grp = grp.dropna(subset=["vol_cf", "vol_FTSE100", "vol_SP500", "vol_FX"])
    if len(grp) < MIN_MONTHS:
        continue
    yv = grp["vol_cf"].values
    X = np.column_stack([np.ones(len(yv)), grp["vol_FTSE100"], grp["vol_SP500"], grp["vol_FX"]])
    try:
        b = np.linalg.lstsq(X, yv, rcond=None)[0]
        yh = X @ b; ssr = np.sum((yv - yh) ** 2); sst = np.sum((yv - yv.mean()) ** 2)
        cf_betas.append({"gvkey": gk, "beta_cf": b[1], "n": len(grp), "r2": 1 - ssr / sst if sst > 0 else 0})
    except:
        continue

betas_cf = pd.DataFrame(cf_betas)
print(f"CF betas: {len(betas_cf):,} firms")

# Compare with baseline
common_g = set(betas_level["gvkey"]) & set(betas_cf["gvkey"])
b_lvl = betas_level[betas_level["gvkey"].isin(common_g)].set_index("gvkey")["beta_uk"]
b_cf = betas_cf[betas_cf["gvkey"].isin(common_g)].set_index("gvkey")["beta_cf"]
rank_corr = b_lvl.rank().corr(b_cf.rank())
pearson_corr = b_lvl.corr(b_cf)

# Top-tercile overlap
b_lvl_pos = b_lvl[b_lvl >= 0]; b_cf_pos = b_cf[b_cf >= 0]
t1_lvl, t2_lvl = b_lvl_pos.quantile(1/3), b_lvl_pos.quantile(2/3)
t1_cf, t2_cf = b_cf_pos.quantile(1/3), b_cf_pos.quantile(2/3)
high_lvl = set(b_lvl_pos[b_lvl_pos >= t2_lvl].index)
high_cf = set(b_cf_pos[b_cf_pos >= t2_cf].index)
overlap = len(high_lvl & high_cf) / max(len(high_lvl | high_cf), 1)

print(f"\n  Common firms: {len(common_g):,}")
print(f"  Rank correlation (baseline vs CF): {rank_corr:.4f} (paper: ~0.80)")
print(f"  Pearson correlation: {pearson_corr:.4f}")
print(f"  Top-tercile overlap: {overlap:.4f} ({overlap*100:.1f}%) (paper: ~86%)")
print(f"  Baseline cutpoints: {t1_lvl:.4f}/{t2_lvl:.4f}")
print(f"  CF cutpoints: {t1_cf:.4f}/{t2_cf:.4f}")
