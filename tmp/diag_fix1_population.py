"""Fix 1 only: restrict beta estimation to Compustat-surviving firms (F1-F8 + FIC).
Compare firm counts before/after. Paper: 449 treated, 360 control."""
import pandas as pd, numpy as np, zipfile, io
from pathlib import Path

ROOT = Path(".")
CSV = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
MIN_DAYS, MIN_MONTHS = 15, 24
T_TOP, T_BOT = 0.68, 0.28

print("=" * 60)
print("FIX 1: Restrict beta pool to Compustat F1-F8 survivors")
print("=" * 60)

# --- BUILD COMPUSTAT SURVIVOR LIST (F1-F8 + FIC) ---
comp = pd.read_parquet(CSV, columns=["gvkey","datadate","fyearq","fqtr","sic","curcdq","fic",
    "atq","saleq","oibdpq","cshoq","prccq","ceqq","txditcq","capxy"])
for c in ["atq","saleq","oibdpq","cshoq","prccq","ceqq","txditcq","capxy"]:
    comp[c] = pd.to_numeric(comp[c], errors="coerce")
comp["txditcq"] = comp["txditcq"].fillna(0)
comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)

# F1: 2010-2016 Q1-Q4
comp = comp[(comp["fyearq"] >= 2010) & (comp["fyearq"] <= 2016)]
comp = comp[comp["fqtr"].isin([1,2,3,4])]
print(f"F1 Raw COMPUSTAT 2010-2016: {len(comp):,} obs, {comp['gvkey'].nunique():,} firms")

# F2: non-US
comp = comp[(comp["curcdq"] == "USD") & (comp["fic"] == "USA")]
print(f"F2 Non-US: {len(comp):,} obs, {comp['gvkey'].nunique():,} firms")

# F3: negative fundamentals
comp = comp[(comp["atq"] > 0) & (comp["saleq"] > 0)]
print(f"F3 Neg fundamentals: {len(comp):,} obs, {comp['gvkey'].nunique():,} firms")

# F4: financials & utilities
csic = pd.to_numeric(comp["sic"], errors="coerce")
comp = comp[~(csic.between(6000, 6999) | csic.between(4900, 4999))]
print(f"F4 Fin+Util: {len(comp):,} obs, {comp['gvkey'].nunique():,} firms")

# F5: ASSETS or MKT_CAP >= $10M
comp["mktcap"] = comp["cshoq"] * comp["prccq"]
comp = comp[(comp["atq"] >= 10) & (comp["mktcap"] >= 10)]
print(f"F5 $10M: {len(comp):,} obs, {comp['gvkey'].nunique():,} firms")

# F6: missing key vars
comp["atq_l1"] = comp.groupby("gvkey")["atq"].shift(1)
comp["saleq_l4"] = comp.groupby("gvkey")["saleq"].shift(4)
has_inv = comp["capxy"].notna() & comp["atq_l1"].notna()
has_at = comp["atq"].notna()
has_cf = comp["oibdpq"].notna() & comp["atq_l1"].notna()
has_q = comp["cshoq"].notna() & comp["prccq"].notna() & comp["atq"].notna() & comp["ceqq"].notna()
has_sg = comp["saleq"].notna() & comp["saleq_l4"].notna()
comp = comp[has_inv & has_at & has_cf & has_q & has_sg]
print(f"F6 Key vars: {len(comp):,} obs, {comp['gvkey'].nunique():,} firms")

# F7: consecutive quarters
comp = comp.sort_values(["gvkey", "fyearq", "fqtr"])
comp["cal_yr_qtr"] = comp["fyearq"].astype(int) * 10 + comp["fqtr"].astype(int)
res_rows = []
for gk, grp in comp.groupby("gvkey"):
    grp = grp.sort_values("cal_yr_qtr")
    runs, cur = [], []
    for _, row in grp.iterrows():
        if not cur:
            cur = [row.name]
        else:
            pq = grp.loc[cur[-1], "cal_yr_qtr"]
            tq = row["cal_yr_qtr"]
            exp = pq + 1
            if pq % 10 == 4:
                exp = (pq // 10 + 1) * 10 + 1
            if tq == exp:
                cur.append(row.name)
            else:
                runs.append(cur)
                cur = [row.name]
    runs.append(cur)
    if runs:
        best = max(runs, key=len)
        if len(best) >= 12:
            res_rows.append(grp.loc[best])
comp = pd.concat(res_rows, ignore_index=True) if res_rows else pd.DataFrame()
print(f"F7 Consecutive >=12q: {len(comp):,} obs, {comp['gvkey'].nunique():,} firms")

# F8: FIC
with zipfile.ZipFile(ROOT / "inputs" / "Brexit_replication" / "HobergPhillips_FIC" / "FIC_Data.zip") as zf:
    with zf.open("fic_data.txt") as f:
        fic = pd.read_csv(io.BytesIO(f.read()), sep="\t", usecols=["gvkey", "year", "icode100"])
fic["gvkey"] = fic["gvkey"].astype(str).str.zfill(6)
comp["year"] = comp["cal_yr_qtr"] // 10
comp = comp.merge(fic, on=["gvkey", "year"], how="inner")
survivor_gvkeys = set(comp["gvkey"].unique())
print(f"F8 FIC: {len(comp):,} obs, {len(survivor_gvkeys):,} firms")

print(f"\nCompustat survivor gvkeys: {len(survivor_gvkeys):,}")

# --- BUILD BETA ONLY FOR SURVIVORS ---
print(f"\n{'='*60}")
print("BETA_UK (restricted to survivor PERMNOs)")
print(f"{'='*60}")

# CCM: survivor gvkeys -> PERMNOs
ccm = pd.read_parquet(ROOT / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet",
    columns=["gvkey", "LPERMNO", "LINKDT", "LINKENDDT", "LINKTYPE", "LINKPRIM"])
ccm["gvkey"] = ccm["gvkey"].astype(str).str.zfill(6)
ccm = ccm[ccm["LINKTYPE"].isin(["LU", "LC"])]
ccm = ccm[ccm["LINKPRIM"].isin(["P", "C"])]
ccm["LINKDT"] = pd.to_datetime(ccm["LINKDT"], errors="coerce")
ccm["LINKENDDT"] = pd.to_datetime(ccm["LINKENDDT"], errors="coerce")
ccm["LINKENDDT"] = ccm["LINKENDDT"].fillna(pd.Timestamp("2099-12-31"))
ccm = ccm[(ccm["LINKENDDT"] >= pd.Timestamp("2010-01-01")) & (ccm["LINKDT"] <= pd.Timestamp("2014-12-31"))]
ccm["LPERMNO"] = pd.to_numeric(ccm["LPERMNO"], errors="coerce").astype("Int64")
ccm = ccm.dropna(subset=["LPERMNO"])
ccm = ccm[ccm["gvkey"].isin(survivor_gvkeys)]
survivor_permnos = set(ccm["LPERMNO"].unique())
print(f"Survivor PERMNOs (via CCM): {len(survivor_permnos):,}")

# CRSP daily returns (only survivor PERMNOs)
frames, frames2 = [], []
for y in range(2010, 2015):
    for q in range(1, 5):
        f = ROOT / "inputs" / "CRSP_DSF" / f"CRSP_DSF_{y}_Q{q}.parquet"
        if f.exists():
            df_ret = pd.read_parquet(f, columns=["PERMNO", "date", "RET"])
            df_ret = df_ret[df_ret["PERMNO"].isin(survivor_permnos)]
            if len(df_ret) > 0:
                frames.append(df_ret)
            df_sp = pd.read_parquet(f, columns=["PERMNO", "date", "RET", "sprtrn"])
            df_sp = df_sp[df_sp["PERMNO"].isin(survivor_permnos)]
            if len(df_sp) > 0:
                frames2.append(df_sp)

crsp = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
crsp["date"] = pd.to_datetime(crsp["date"])
crsp["RET"] = pd.to_numeric(crsp["RET"], errors="coerce")
crsp["ym"] = crsp["date"].dt.to_period("M")
g = crsp.groupby(["PERMNO", "ym"])
rv = g["RET"].std()
rv = rv[g["RET"].count() >= MIN_DAYS].reset_index()
rv.columns = ["PERMNO", "ym", "vol_r"]

cr2 = pd.concat(frames2, ignore_index=True) if frames2 else pd.DataFrame()
cr2["date"] = pd.to_datetime(cr2["date"])
cr2["sprtrn"] = pd.to_numeric(cr2["sprtrn"], errors="coerce")
cr2["ym"] = cr2["date"].dt.to_period("M")
sp = cr2[["date", "sprtrn", "ym"]].drop_duplicates()
spg = sp.groupby("ym")
sp500 = spg["sprtrn"].std()
sp500 = sp500[spg["sprtrn"].count() >= MIN_DAYS].reset_index()
sp500.columns = ["ym", "vol_SP500"]
del crsp, cr2, sp

# FTSE100
ftse = pd.read_csv(ROOT / "inputs" / "Brexit_replication" / "Yahoo_FTSE100" / "FTSE100_yfinance_daily.csv")
ftse["Date"] = pd.to_datetime(ftse["Date"])
ftse = ftse[(ftse["Date"] >= "2010-01-01") & (ftse["Date"] <= "2014-12-31")].sort_values("Date")
ftse["lr"] = np.log(ftse["Close"] / ftse["Close"].shift(1))
ftse["ym"] = ftse["Date"].dt.to_period("M")
fg = ftse.groupby("ym")
ftv = fg["lr"].std()
ftv = ftv[fg["lr"].count() >= MIN_DAYS].reset_index()
ftv.columns = ["ym", "vol_FTSE100"]

# FX
fx = pd.read_csv(ROOT / "inputs" / "Brexit_replication" / "BoE" / "USD_GBP_daily_2008-2018.csv")
fx["DATE"] = pd.to_datetime(fx["DATE"], dayfirst=True)
fx = fx[(fx["DATE"] >= "2010-01-01") & (fx["DATE"] <= "2014-12-31")].sort_values("DATE")
fx["lr"] = np.log(fx["XUDLUSS"] / fx["XUDLUSS"].shift(1))
fx["ym"] = fx["DATE"].dt.to_period("M")
fgg = fx.groupby("ym")
fxv = fgg["lr"].std()
fxv = fxv[fgg["lr"].count() >= MIN_DAYS].reset_index()
fxv.columns = ["ym", "vol_FX"]

# Merge macro + OLS per firm
macro = sp500.merge(ftv, on="ym").merge(fxv, on="ym")
rv["ym"] = rv["ym"].astype(str)
macro["ym"] = macro["ym"].astype(str)
mg = rv.merge(macro, on="ym", how="inner")

res = []
for pn, grp in mg.groupby("PERMNO"):
    grp = grp.dropna(subset=["vol_r", "vol_FTSE100", "vol_SP500", "vol_FX"])
    if len(grp) < MIN_MONTHS:
        continue
    y_vals = grp["vol_r"].values
    X_mat = np.column_stack([np.ones(len(y_vals)), grp["vol_FTSE100"], grp["vol_SP500"], grp["vol_FX"]])
    try:
        b = np.linalg.lstsq(X_mat, y_vals, rcond=None)[0]
        yhat = X_mat @ b
        ssr = np.sum((y_vals - yhat) ** 2)
        sst = np.sum((y_vals - y_vals.mean()) ** 2)
        res.append({"PERMNO": pn, "beta_uk": b[1], "n": len(grp), "r2": 1 - ssr / sst if sst > 0 else 0})
    except:
        continue
betas = pd.DataFrame(res)

# Merge to gvkey
betas = betas.merge(ccm[["gvkey", "LPERMNO"]].drop_duplicates(), left_on="PERMNO", right_on="LPERMNO", how="inner")
betas = betas.drop_duplicates(subset=["gvkey"], keep="first")
betas["gvkey"] = betas["gvkey"].astype(str).str.zfill(6)

# HIGH/LOW using paper thresholds
betas["HIGH"] = (betas["beta_uk"] > T_TOP).astype(int)
betas["LOW"] = ((betas["beta_uk"] >= 0) & (betas["beta_uk"] < T_BOT)).astype(int)
bpos = betas[betas["beta_uk"] >= 0]
t2, t1 = bpos["beta_uk"].quantile(2 / 3), bpos["beta_uk"].quantile(1 / 3)

print(f"\n  beta_uk firms: {len(betas):,} (was 5,714)")
print(f"  Nonnegative: {len(bpos):,} (was 3,726)")
print(f"  Tercile thresholds: {t1:.4f} / {t2:.4f}")
print(f"  HIGH (>0.68): {betas['HIGH'].sum():,} (paper: 449, was: 1,162)")
print(f"  LOW (0<=b<0.28): {betas['LOW'].sum():,} (paper: 360, was: 1,396)")
print(f"  DiD total: {betas['HIGH'].sum() + betas['LOW'].sum():,} (paper: 809)")
print(f"  MIDDLE: {len(bpos[(bpos['beta_uk']>=0.28)&(bpos['beta_uk']<=0.68)]):,}")
print(f"  NEGATIVE: {len(betas[betas['beta_uk']<0]):,}")
