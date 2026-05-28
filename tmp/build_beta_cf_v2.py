"""RA Round 4 action #4: Proper beta^UK_i,CF via Vuolteenaho (2002) decomposition.
Key improvements over build_beta_cf.py:
1. Longer history: 2002-2018 quarterly (up to 64 quarters per firm)
2. Require >=30 quarters for VAR estimation
3. Proper monthly vol construction for CF news in eq (13)
4. Annual baseline beta for internal validation

Target: rank corr ~0.8 with baseline beta, ~86% top-tercile overlap."""
import pandas as pd, numpy as np, zipfile, io
from pathlib import Path

ROOT = Path(".")
CSV = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
RHO_Q = 0.99  # quarterly discount (annual ~0.96 => quarterly ~0.99)
MIN_Q_VAR = 30  # minimum quarterly obs per firm for VAR
MIN_MONTHS_BETA = 24  # minimum monthly obs for eq (13)

# ============================================================
# 1. Build quarterly firm data (returns, ROE, BM): 2002-2018
# ============================================================
print("=" * 60)
print("1. Quarterly data 2002-2018")
print("=" * 60)

# Returns from CRSP (quarterly)
frames_ret = []
for y in range(2002, 2019):
    for q in range(1, 5):
        f = ROOT / "inputs" / "CRSP_DSF" / f"CRSP_DSF_{y}_Q{q}.parquet"
        if f.exists():
            frames_ret.append(pd.read_parquet(f, columns=["PERMNO", "date", "RET"]))
cr = pd.concat(frames_ret, ignore_index=True)
cr["date"] = pd.to_datetime(cr["date"]); cr["RET"] = pd.to_numeric(cr["RET"], errors="coerce")
cr["yq"] = cr["date"].dt.year * 10 + cr["date"].dt.quarter
cr["lr"] = np.log(1 + cr["RET"].fillna(0))
qr = cr.groupby(["PERMNO", "yq"])["lr"].sum().reset_index()
qr.columns = ["PERMNO", "yq", "r_q"]
print(f"CRSP quarterly returns: {len(qr):,} obs")

# ROE and BM from Compustat
comp = pd.read_parquet(CSV, columns=["gvkey", "datadate", "fyearq", "fqtr", "sic", "curcdq", "fic",
    "atq", "oibdpq", "cshoq", "prccq", "ceqq", "txditcq"])
for c in ["atq", "oibdpq", "cshoq", "prccq", "ceqq", "txditcq"]:
    comp[c] = pd.to_numeric(comp[c], errors="coerce")
comp["txditcq"] = comp["txditcq"].fillna(0); comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
comp = comp[(comp["fyearq"] >= 2001) & (comp["fyearq"] <= 2018)]  # need lag, so start 2001
comp = comp[comp["fqtr"].isin([1, 2, 3, 4])]
comp = comp[(comp["curcdq"] == "USD") & (comp["fic"] == "USA")]
comp = comp[(comp["atq"] > 0)]
comp["yq"] = comp["fyearq"].astype(int) * 10 + comp["fqtr"].astype(int)
comp = comp.sort_values(["gvkey", "yq"])

# ROE = OIBDPQ / lagged book equity
comp["be"] = comp["ceqq"] + comp["txditcq"]
comp["be_lag"] = comp.groupby("gvkey")["be"].shift(1)
comp["roe"] = comp["oibdpq"] / comp["be_lag"]
comp["roe"] = comp["roe"].clip(-1, 1)

# Book-to-market
comp["mktcap"] = comp["cshoq"] * comp["prccq"]
comp["bm"] = comp["be"] / comp["mktcap"]
comp["bm"] = comp["bm"].clip(1e-6, 100)

# Log transforms for ROE (log(1+ROE)) and BM (log(BM))
comp["roe_log"] = np.log(1 + comp["roe"].clip(-0.99, 10))
comp["bm_log"] = np.log(comp["bm"])

comp_vars = comp[["gvkey", "yq", "roe_log", "bm_log"]].dropna()
print(f"Compustat quarterly: {len(comp_vars):,} obs, {comp_vars['gvkey'].nunique():,} firms")

# CCM merge
ccm = pd.read_parquet(ROOT / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet",
    columns=["gvkey", "LPERMNO", "LINKDT", "LINKENDDT", "LINKTYPE", "LINKPRIM"])
ccm["gvkey"] = ccm["gvkey"].astype(str).str.zfill(6)
ccm = ccm[ccm["LINKTYPE"].isin(["LU", "LC"])]; ccm = ccm[ccm["LINKPRIM"].isin(["P", "C"])]
ccm["LINKDT"] = pd.to_datetime(ccm["LINKDT"], errors="coerce")
ccm["LINKENDDT"] = pd.to_datetime(ccm["LINKENDDT"], errors="coerce")
ccm["LINKENDDT"] = ccm["LINKENDDT"].fillna(pd.Timestamp("2099-12-31"))
ccm = ccm[(ccm["LINKENDDT"] >= pd.Timestamp("2002-01-01")) & (ccm["LINKDT"] <= pd.Timestamp("2018-12-31"))]
ccm["LPERMNO"] = pd.to_numeric(ccm["LPERMNO"], errors="coerce").astype("Int64")
ccm = ccm.dropna(subset=["LPERMNO"])

# Match CRSP to Compustat via CCM
qr = qr.merge(ccm[["gvkey", "LPERMNO"]].drop_duplicates(), left_on="PERMNO", right_on="LPERMNO", how="inner")
qr = qr.drop_duplicates(subset=["gvkey", "yq"], keep="first")
qr["gvkey"] = qr["gvkey"].astype(str).str.zfill(6)

# Merge
qdf = comp_vars.merge(qr[["gvkey", "yq", "r_q"]], on=["gvkey", "yq"], how="inner")
qdf = qdf.sort_values(["gvkey", "yq"])
print(f"Merged quarterly: {len(qdf):,} obs, {qdf['gvkey'].nunique():,} firms")

# ============================================================
# 2. Firm-level VAR(1) and CF news extraction
# ============================================================
print(f"\n{'='*60}")
print("2. VAR(1) + CF news (>= {MIN_Q_VAR} quarters)")
print("=" * 60)

results = []
n_var_done = 0
for gk, grp in qdf.groupby("gvkey"):
    grp = grp.sort_values("yq")
    Z = grp[["r_q", "roe_log", "bm_log"]].values
    if len(Z) < MIN_Q_VAR:
        continue

    # VAR(1): Z_{t+1} = Gamma * Z_t + u_{t+1}
    Z_lag = Z[:-1]
    Z_lead = Z[1:]
    try:
        Gamma = np.linalg.lstsq(Z_lag, Z_lead, rcond=None)[0].T  # 3x3
    except:
        continue

    # Check stationarity (eigenvalues < 1)
    eigvals = np.linalg.eigvals(Gamma)
    if np.max(np.abs(eigvals)) >= 0.999:
        continue

    # CF news: e1' * inv(I - rho*Gamma) * u_t
    I_mat = np.eye(3)
    try:
        inv_term = np.linalg.inv(I_mat - RHO_Q * Gamma)
    except:
        continue

    e1 = np.array([1.0, 0.0, 0.0])
    cf_coeff = e1 @ inv_term  # 1x3

    # Innovations: u_t = Z_t - Gamma * Z_{t-1}
    U = Z[1:] - (Gamma @ Z[:-1].T).T

    # Quarterly CF news
    cf_news_q = U @ cf_coeff

    # Store: map to monthly
    for t_idx, cf_val in enumerate(cf_news_q):
        yq = grp["yq"].iloc[t_idx + 1]
        yr, qq = yq // 10, yq % 10
        month_start = (qq - 1) * 3 + 1
        for m in range(month_start, month_start + 3):
            ym = f"{yr}-{m:02d}"
            results.append({"gvkey": gk, "ym": ym, "cf_news": cf_val, "yq": yq})

    n_var_done += 1

cf_df = pd.DataFrame(results)
print(f"VAR estimated: {n_var_done:,} firms")
print(f"CF news obs: {len(cf_df):,}, firms: {cf_df['gvkey'].nunique():,}")

# Monthly vol = |CF_news| (absolute CF news at monthly frequency)
cf_df["vol_cf"] = np.abs(cf_df["cf_news"])
cf_monthly = cf_df.groupby(["gvkey", "ym"])["vol_cf"].mean().reset_index()
print(f"Monthly CF vol: {len(cf_monthly):,} obs, {cf_monthly['gvkey'].nunique():,} firms")

# Also compute quarterly CF vol for annual baseline comparison
cf_quarterly = cf_df.groupby(["gvkey", "yq"])["cf_news"].agg(["std", "mean"]).reset_index()
cf_quarterly["vol_cf_q"] = cf_quarterly["std"].fillna(np.abs(cf_quarterly["mean"]))
print(f"Quarterly CF vol: {len(cf_quarterly):,} obs")

# ============================================================
# 3. Build macro vol series (monthly 2010-2014, same as baseline)
# ============================================================
print(f"\n{'='*60}")
print("3. Macro vol series")
print("=" * 60)

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
ftse["Date"] = pd.to_datetime(ftse["Date"])
ftse = ftse[(ftse["Date"] >= "2010-01-01") & (ftse["Date"] <= "2014-12-31")]
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
print(f"Macro monthly: {len(macro_m):,} obs")

# ============================================================
# 4. Run eq (13) with CF vol as LHS → beta^UK_i,CF
# ============================================================
print(f"\n{'='*60}")
print("4. beta^UK_i,CF via eq(13) with CF vol")
print("=" * 60)

# Restrict to 2010:M1-2014:M12
cf_data = cf_monthly.merge(macro_m, on="ym", how="inner")
cf_data = cf_data[(cf_data["ym"] >= "2010-01") & (cf_data["ym"] <= "2014-12")]
print(f"CF vol merged with macro: {len(cf_data):,} obs, {cf_data['gvkey'].nunique():,} firms")

cf_betas = []
for gk, grp in cf_data.groupby("gvkey"):
    grp = grp.dropna(subset=["vol_cf", "vol_FTSE100", "vol_SP500", "vol_FX"])
    if len(grp) < MIN_MONTHS_BETA:
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
if len(betas_cf) > 0:
    print(f"  mean={betas_cf['beta_cf'].mean():.4f}, SD={betas_cf['beta_cf'].std():.4f}")
    npos = len(betas_cf[betas_cf["beta_cf"] >= 0])
    print(f"  Nonneg: {npos:,}, Neg: {len(betas_cf) - npos:,}")

# ============================================================
# 5. Build BASELINE beta^UK_i at MONTHLY frequency (same macro, firm vol)
# ============================================================
print(f"\n{'='*60}")
print("5. Baseline beta^UK_i (monthly, same 2010-2014 window)")
print("=" * 60)

# Build firm monthly vol from CRSP (same as baseline)
frames_ret2 = []
for y in range(2010, 2015):
    for q in range(1, 5):
        f = ROOT / "inputs" / "CRSP_DSF" / f"CRSP_DSF_{y}_Q{q}.parquet"
        if f.exists():
            frames_ret2.append(pd.read_parquet(f, columns=["PERMNO", "date", "RET"]))
cr2 = pd.concat(frames_ret2, ignore_index=True)
cr2["date"] = pd.to_datetime(cr2["date"]); cr2["RET"] = pd.to_numeric(cr2["RET"], errors="coerce")
cr2["ym"] = cr2["date"].dt.to_period("M").astype(str)
g = cr2.groupby(["PERMNO", "ym"])
firm_vol = g["RET"].std()
firm_vol = firm_vol[g["RET"].count() >= 15].reset_index()
firm_vol.columns = ["PERMNO", "ym", "vol_r"]
firm_vol = firm_vol.merge(ccm[["gvkey", "LPERMNO"]].drop_duplicates(), left_on="PERMNO", right_on="LPERMNO", how="inner")
firm_vol = firm_vol.drop_duplicates(subset=["gvkey", "ym"], keep="first")
firm_vol["gvkey"] = firm_vol["gvkey"].astype(str).str.zfill(6)

fv_data = firm_vol.merge(macro_m, on="ym", how="inner")
fv_data = fv_data[(fv_data["ym"] >= "2010-01") & (fv_data["ym"] <= "2014-12")]
print(f"Firm vol merged: {len(fv_data):,} obs, {fv_data['gvkey'].nunique():,} firms")

level_betas = []
for gk, grp in fv_data.groupby("gvkey"):
    grp = grp.dropna(subset=["vol_r", "vol_FTSE100", "vol_SP500", "vol_FX"])
    if len(grp) < MIN_MONTHS_BETA:
        continue
    yv = grp["vol_r"].values
    X = np.column_stack([np.ones(len(yv)), grp["vol_FTSE100"], grp["vol_SP500"], grp["vol_FX"]])
    try:
        b = np.linalg.lstsq(X, yv, rcond=None)[0]
        yh = X @ b; ssr = np.sum((yv - yh) ** 2); sst = np.sum((yv - yv.mean()) ** 2)
        level_betas.append({"gvkey": gk, "beta_uk": b[1], "n": len(grp), "r2": 1 - ssr / sst if sst > 0 else 0})
    except:
        continue

betas_level = pd.DataFrame(level_betas)
print(f"Level betas: {len(betas_level):,} firms")
if len(betas_level) > 0:
    print(f"  mean={betas_level['beta_uk'].mean():.4f}, SD={betas_level['beta_uk'].std():.4f}")
    npos = len(betas_level[betas_level["beta_uk"] >= 0])
    print(f"  Nonneg: {npos:,}, Neg: {len(betas_level) - npos:,}")

# ============================================================
# 6. Compare
# ============================================================
print(f"\n{'='*60}")
print("6. beta^UK_i vs beta^UK_i,CF — comparison")
print("=" * 60)

common_g = set(betas_level["gvkey"]) & set(betas_cf["gvkey"])
if len(common_g) == 0:
    # Try via PERMNO
    print("No common gvkeys via direct match. Trying CCM bridge...")
    betas_cf_pn = betas_cf.merge(ccm[["gvkey", "LPERMNO"]].drop_duplicates(), on="gvkey", how="inner")
    betas_level_pn = betas_level.merge(ccm[["gvkey", "LPERMNO"]].drop_duplicates(), on="gvkey", how="inner")
    common_pn = set(betas_cf_pn["LPERMNO"]) & set(betas_level_pn["LPERMNO"])
    common_g = set(betas_cf_pn[betas_cf_pn["LPERMNO"].isin(common_pn)]["gvkey"]) & set(betas_level_pn[betas_level_pn["LPERMNO"].isin(common_pn)]["gvkey"])

common_g = set(betas_level["gvkey"]) & set(betas_cf["gvkey"])
print(f"Common firms: {len(common_g):,}")

if len(common_g) >= 20:
    b_lvl = betas_level[betas_level["gvkey"].isin(common_g)].set_index("gvkey")["beta_uk"]
    b_cf = betas_cf[betas_cf["gvkey"].isin(common_g)].set_index("gvkey")["beta_cf"]

    rank_corr = b_lvl.rank().corr(b_cf.rank())
    pearson_corr = b_lvl.corr(b_cf)

    # Top-tercile overlap
    b_lvl_pos = b_lvl[b_lvl >= 0]; b_cf_pos = b_cf[b_cf >= 0]
    if len(b_lvl_pos) >= 3 and len(b_cf_pos) >= 3:
        t1_lvl, t2_lvl = b_lvl_pos.quantile(1/3), b_lvl_pos.quantile(2/3)
        t1_cf, t2_cf = b_cf_pos.quantile(1/3), b_cf_pos.quantile(2/3)
        high_lvl = set(b_lvl_pos[b_lvl_pos >= t2_lvl].index)
        high_cf = set(b_cf_pos[b_cf_pos >= t2_cf].index)
        union = high_lvl | high_cf
        overlap = len(high_lvl & high_cf) / max(len(union), 1) if union else 0

        print(f"\n  Common firms: {len(common_g):,}")
        print(f"  Nonneg (level): {len(b_lvl_pos):,}, Nonneg (CF): {len(b_cf_pos):,}")
        print(f"  Rank correlation: {rank_corr:.4f} (paper: ~0.80)")
        print(f"  Pearson correlation: {pearson_corr:.4f}")
        print(f"  Top-tercile overlap: {overlap:.4f} ({overlap*100:.1f}%) (paper: ~86%)")
        print(f"  Level cutpoints: T1={t1_lvl:.4f}, T2={t2_lvl:.4f}")
        print(f"  CF cutpoints: T1={t1_cf:.4f}, T2={t2_cf:.4f}")

        # Check if this meets the pass criteria
        if rank_corr >= 0.7 and overlap >= 0.75:
            print(f"\n  *** PASS: Internal validation successful! ***")
        elif rank_corr >= 0.5:
            print(f"\n  PARTIAL: Improvement over previous 0.14, but below 0.8 target")
        else:
            print(f"\n  FAIL: Rank correlation too low. CF news construction likely still problematic.")
    else:
        print(f"  Not enough nonnegative betas for tercile comparison")
else:
    print(f"  Too few common firms for comparison (< 20)")

print(f"\n{'='*60}")
print("Done.")
