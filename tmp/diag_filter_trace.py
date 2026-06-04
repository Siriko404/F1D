"""Diagnostic: trace N at each Table C.1 filter step. Compare our counts to paper."""
import pandas as pd, numpy as np, zipfile, io
from pathlib import Path

ROOT = Path(".")
CSV = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"

print("=" * 70)
print("TABLE C.1 FILTER TRACE — CAMPELLO ET AL. (2022)")
print("=" * 70)

# Step 0: Raw COMPUSTAT 2010:Q1-2016:Q4
comp = pd.read_parquet(CSV, columns=["gvkey","datadate","fyearq","fqtr","sic","curcdq","fic",
    "atq","saleq","cheq","oibdpq","cshoq","prccq","ceqq","txditcq","capxy"])
for c in ["atq","saleq","cheq","oibdpq","cshoq","prccq","ceqq","txditcq","capxy"]:
    comp[c] = pd.to_numeric(comp[c], errors="coerce")
comp["txditcq"] = comp["txditcq"].fillna(0)
comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
comp = comp[(comp["fyearq"] >= 2010) & (comp["fyearq"] <= 2016)]
comp = comp[comp["fqtr"].isin([1,2,3,4])]

print(f"\n{'Step':<6} {'Description':<60} {'N (firm-qtrs)':>14} {'Paper N':>10} {'Delta':>8}")
print("-" * 100)

N0 = len(comp)
print(f"{'0':<6} {'Raw COMPUSTAT 2010:Q1-2016:Q4':<60} {N0:>14,} {'262,412':>10} {N0-262412:>+8,}")

# Step 1: Drop non-US (USD + US HQ + no dups)
comp_s1 = comp[(comp["curcdq"] == "USD") & (comp["fic"] == "USA")].copy()
N1 = len(comp_s1)
print(f"{'1':<6} {'Drop non-US (USD + USA + no dups)':<60} {N1:>14,} {'160,254':>10} {N1-160254:>+8,}")

# Step 2: Drop negative fundamentals (ASSETS and SALES)
comp_s2 = comp_s1[(comp_s1["atq"] > 0) & (comp_s1["saleq"] > 0)].copy()
N2 = len(comp_s2)
print(f"{'2':<6} {'Drop negative fundamentals (ATQ>0 & SALEQ>0)':<60} {N2:>14,} {'158,312':>10} {N2-158312:>+8,}")

# Step 3: Drop financials (SIC 6000-6999) and utilities (SIC 4900-4999)
csic = pd.to_numeric(comp_s2["sic"], errors="coerce")
comp_s3 = comp_s2[~(csic.between(6000, 6999) | csic.between(4900, 4999))].copy()
N3 = len(comp_s3)
print(f"{'3':<6} {'Drop financials (6000-6999) & utilities (4900-4999)':<60} {N3:>14,} {'112,939':>10} {N3-112939:>+8,}")

# Step 4: Drop if ASSETS or MARKET_CAP < $10M
comp_s3["mktcap"] = comp_s3["cshoq"] * comp_s3["prccq"]
comp_s4 = comp_s3[(comp_s3["atq"] >= 10) & (comp_s3["mktcap"] >= 10)].copy()
N4 = len(comp_s4)
print(f"{'4':<6} {'Drop ASSETS or MKT_CAP < $10M':<60} {N4:>14,} {'93,011':>10} {N4-93011:>+8,}")

# Also show: our current code (atq>10 only, no mktcap check)
comp_s4_ours = comp_s3[comp_s3["atq"] > 10].copy()
N4_ours = len(comp_s4_ours)
print(f"{'4b':<6} {'OUR CODE: atq>10 only (NO mktcap check)':<60} {N4_ours:>14,} {'93,011':>10} {N4_ours-93011:>+8,}")

# Step 5: Drop if missing key variables (INVESTMENT, ASSETS, CASH_FLOW, TOBIN_Q, SALES_GROWTH)
# Paper definition: INVESTMENT=capxy/atq_lag, ASSETS=atq, CASH_FLOW=oibdpq/atq_lag, TOBIN_Q, SALES_GROWTH
comp_s4["atq_l1"] = comp_s4.groupby("gvkey")["atq"].shift(1)
comp_s4["saleq_l4"] = comp_s4.groupby("gvkey")["saleq"].shift(4)
# Paper key variables: INVESTMENT (needs capxy, atq_l1), ASSETS (atq), CASH_FLOW (oibdpq, atq_l1),
# TOBIN_Q (cshoq, prccq, atq, ceqq, txditcq), SALES_GROWTH (saleq, saleq_l4)
has_inv = comp_s4["capxy"].notna() & comp_s4["atq_l1"].notna()
has_at = comp_s4["atq"].notna()
has_cf = comp_s4["oibdpq"].notna() & comp_s4["atq_l1"].notna()
has_q = comp_s4["cshoq"].notna() & comp_s4["prccq"].notna() & comp_s4["atq"].notna() & comp_s4["ceqq"].notna()
has_sg = comp_s4["saleq"].notna() & comp_s4["saleq_l4"].notna()
comp_s5 = comp_s4[has_inv & has_at & has_cf & has_q & has_sg].copy()
N5 = len(comp_s5)
print(f"{'5':<6} {'Drop missing key vars (INV, AT, CF, Q, SG)':<60} {N5:>14,} {'75,013':>10} {N5-75013:>+8,}")

# Step 6: Drop if non-consecutive quarters or <12 quarters
comp_s5 = comp_s5.sort_values(["gvkey", "fyearq", "fqtr"])
comp_s5["cal_yr_qtr"] = comp_s5["fyearq"].astype(int) * 10 + comp_s5["fqtr"].astype(int)
res_rows = []
n_firms_before_f6 = comp_s5["gvkey"].nunique()
for gk, grp in comp_s5.groupby("gvkey"):
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
comp_s6 = pd.concat(res_rows, ignore_index=True) if res_rows else pd.DataFrame()
N6 = len(comp_s6)
n_firms_after_f6 = comp_s6["gvkey"].nunique() if N6 > 0 else 0
print(f"{'6':<6} {'Drop non-consecutive or <12 qtrs':<60} {N6:>14,} {'56,081':>10} {N6-56081:>+8,}")
print(f"{'':<6} {'  (firms: ' + str(n_firms_before_f6) + ' -> ' + str(n_firms_after_f6) + ')':<60}")

# Step 7: Drop if missing FIC
with zipfile.ZipFile(ROOT / "inputs" / "Brexit_replication" / "HobergPhillips_FIC" / "FIC_Data.zip") as zf:
    with zf.open("fic_data.txt") as f:
        fic = pd.read_csv(io.BytesIO(f.read()), sep="\t", usecols=["gvkey", "year", "icode100"])
fic["gvkey"] = fic["gvkey"].astype(str).str.zfill(6)
fic = fic[(fic["year"] >= 2010) & (fic["year"] <= 2016)]
comp_s6["year"] = comp_s6["cal_yr_qtr"] // 10
comp_s7 = comp_s6.merge(fic, on=["gvkey", "year"], how="inner")
N7 = len(comp_s7)
n_firms_s7 = comp_s7["gvkey"].nunique()
print(f"{'7':<6} {'Drop missing FIC (Hoberg-Phillips)':<60} {N7:>14,} {'49,107':>10} {N7-49107:>+8,}")
print(f"{'':<6} {'  (firms: ' + str(n_firms_s7) + ')':<60}")

# Step 8: Drop if missing β^UK_i
# Build beta_uk the same way run_did.py does
MIN_DAYS, MIN_MONTHS = 15, 24
T_TOP, T_BOT = 0.68, 0.28

frames = []
for y in range(2010, 2015):
    for q in range(1, 5):
        f = ROOT / "inputs" / "CRSP_DSF" / f"CRSP_DSF_{y}_Q{q}.parquet"
        if f.exists():
            frames.append(pd.read_parquet(f, columns=["PERMNO", "date", "RET"]))
crsp = pd.concat(frames, ignore_index=True)
crsp["date"] = pd.to_datetime(crsp["date"])
crsp["RET"] = pd.to_numeric(crsp["RET"], errors="coerce")
crsp["ym"] = crsp["date"].dt.to_period("M")
g = crsp.groupby(["PERMNO", "ym"])
rv = g["RET"].std()
rv = rv[g["RET"].count() >= MIN_DAYS].reset_index()
rv.columns = ["PERMNO", "ym", "vol_r"]

frames2 = []
for y in range(2010, 2015):
    for q in range(1, 5):
        f = ROOT / "inputs" / "CRSP_DSF" / f"CRSP_DSF_{y}_Q{q}.parquet"
        if f.exists():
            frames2.append(pd.read_parquet(f, columns=["PERMNO", "date", "RET", "sprtrn"]))
cr2 = pd.concat(frames2, ignore_index=True)
cr2["date"] = pd.to_datetime(cr2["date"])
cr2["sprtrn"] = pd.to_numeric(cr2["sprtrn"], errors="coerce")
cr2["ym"] = cr2["date"].dt.to_period("M")
sp = cr2[["date", "sprtrn", "ym"]].drop_duplicates()
spg = sp.groupby("ym")
sp500 = spg["sprtrn"].std()
sp500 = sp500[spg["sprtrn"].count() >= MIN_DAYS].reset_index()
sp500.columns = ["ym", "vol_SP500"]
del crsp, cr2, sp

ftse = pd.read_csv(ROOT / "inputs" / "Brexit_replication" / "Yahoo_FTSE100" / "FTSE100_yfinance_daily.csv")
ftse["Date"] = pd.to_datetime(ftse["Date"])
ftse = ftse[(ftse["Date"] >= "2010-01-01") & (ftse["Date"] <= "2014-12-31")].sort_values("Date")
ftse["lr"] = np.log(ftse["Close"] / ftse["Close"].shift(1))
ftse["ym"] = ftse["Date"].dt.to_period("M")
fg = ftse.groupby("ym")
ftv = fg["lr"].std()
ftv = ftv[fg["lr"].count() >= MIN_DAYS].reset_index()
ftv.columns = ["ym", "vol_FTSE100"]

fx = pd.read_csv(ROOT / "inputs" / "Brexit_replication" / "BoE" / "USD_GBP_daily_2008-2018.csv")
fx["DATE"] = pd.to_datetime(fx["DATE"], dayfirst=True)
fx = fx[(fx["DATE"] >= "2010-01-01") & (fx["DATE"] <= "2014-12-31")].sort_values("DATE")
fx["lr"] = np.log(fx["XUDLUSS"] / fx["XUDLUSS"].shift(1))
fx["ym"] = fx["DATE"].dt.to_period("M")
fgg = fx.groupby("ym")
fxv = fgg["lr"].std()
fxv = fxv[fgg["lr"].count() >= MIN_DAYS].reset_index()
fxv.columns = ["ym", "vol_FX"]

macro = sp500.merge(ftv, on="ym").merge(fxv, on="ym")
rv["ym"] = rv["ym"].astype(str)
macro["ym"] = macro["ym"].astype(str)
mg = rv.merge(macro, on="ym", how="inner")

res = []
for pn, grp in mg.groupby("PERMNO"):
    grp = grp.dropna(subset=["vol_r", "vol_FTSE100", "vol_SP500", "vol_FX"])
    if len(grp) < MIN_MONTHS:
        continue
    y = grp["vol_r"].values
    X = np.column_stack([np.ones(len(y)), grp["vol_FTSE100"], grp["vol_SP500"], grp["vol_FX"]])
    try:
        b = np.linalg.lstsq(X, y, rcond=None)[0]
        yh = X @ b
        ssr = np.sum((y - yh) ** 2)
        sst = np.sum((y - y.mean()) ** 2)
        res.append({"PERMNO": pn, "beta_uk": b[1], "n": len(grp), "r2": 1 - ssr / sst if sst > 0 else 0})
    except:
        continue
betas = pd.DataFrame(res)

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
betas = betas.merge(ccm[["gvkey", "LPERMNO"]].drop_duplicates(), left_on="PERMNO", right_on="LPERMNO", how="inner")
betas = betas.drop_duplicates(subset=["gvkey"], keep="first")
betas["gvkey"] = betas["gvkey"].astype(str).str.zfill(6)

# Assign HIGH/LOW using paper thresholds
betas["HIGH"] = (betas["beta_uk"] > T_TOP).astype(int)  # STRICT > per paper
betas["LOW"] = ((betas["beta_uk"] >= 0) & (betas["beta_uk"] < T_BOT)).astype(int)  # STRICT < per paper
# Nonnegative tercile thresholds
bpos = betas[betas["beta_uk"] >= 0]
t2, t1 = bpos["beta_uk"].quantile(2/3), bpos["beta_uk"].quantile(1/3)
print(f"\n  beta_uk: {len(betas):,} firms total, {len(bpos):,} nonnegative")
print(f"  Our tercile thresholds: {t1:.4f} / {t2:.4f}")
print(f"  Paper thresholds: 0.28 / 0.68")
print(f"  HIGH (>0.68): {betas['HIGH'].sum():,} firms (paper: 449)")
print(f"  LOW (0<=b<0.28): {betas['LOW'].sum():,} firms (paper: 360)")
print(f"  MIDDLE (0.28<=b<=0.68): {len(bpos[(bpos['beta_uk']>=0.28)&(bpos['beta_uk']<=0.68)]):,} firms")
print(f"  NEGATIVE (b<0): {len(betas[betas['beta_uk']<0]):,} firms")
print(f"  HIGH (>t2={t2:.4f}): {(betas['beta_uk']>t2).sum():,} firms (our tercile)")
print(f"  LOW (0<=b<t1={t1:.4f}): {((betas['beta_uk']>=0)&(betas['beta_uk']<t1)).sum():,} firms (our tercile)")
# Distribution diagnostics
print(f"\n  BETA DISTRIBUTION (nonnegative, N={len(bpos):,}):")
for pct in [1, 5, 10, 25, 33.3, 50, 66.7, 75, 90, 95, 99]:
    print(f"    P{pct:5.1f}: {bpos['beta_uk'].quantile(pct/100):.4f}")
print(f"    mean: {bpos['beta_uk'].mean():.4f}  std: {bpos['beta_uk'].std():.4f}")
print(f"    min: {bpos['beta_uk'].min():.6f}  max: {bpos['beta_uk'].max():.4f}")
print(f"    firms > 1.0: {(bpos['beta_uk']>1.0).sum():,}")
print(f"    firms > 2.0: {(bpos['beta_uk']>2.0).sum():,}")
print(f"    firms > 5.0: {(bpos['beta_uk']>5.0).sum():,}")

comp_s8 = comp_s7.merge(betas[["gvkey", "beta_uk", "HIGH", "LOW"]], on="gvkey", how="inner")
N8 = len(comp_s8)
n_firms_s8 = comp_s8["gvkey"].nunique()
print(f"\n{'8':<6} {'Drop missing beta_UK':<60} {N8:>14,} {'43,025':>10} {N8-43025:>+8,}")
print(f"{'':<6} {'  (firms: ' + str(n_firms_s8) + ')':<60}")

# Step 9: Drop if missing CRSP and I/B/E/S controls
# This requires building stock_returns and consensus_eps...
# For now, skip and show the pre-CRSP/IBES count
print(f"\n{'9':<6} {'Drop missing CRSP + I/B/E/S controls (SKIPPED)':<60}")
print(f"{'':<6} {'  Pre-filter N=' + str(N8) + ' (paper says -> 41,630)':<60}")

# Now show where our final DiD sample comes from
print(f"\n{'='*70}")
print("OUR DiD SAMPLE FLOW (run_did.py path)")
print(f"{'='*70}")

print(f"\n  After F7+FIC (our code):")
print(f"  comp_s7 (paper filter 7+8): {N7:,} obs, {n_firms_s7:,} firms")
print(f"  Paper after filter 8 (FIC): 49,107 obs")

print(f"\n  After beta_uk merge (our code):")
print(f"  comp_s8 (paper filter 9): {N8:,} obs, {n_firms_s8:,} firms")
print(f"  Paper after filter 9 (beta): 43,025 obs")

print(f"\n  Paper final baseline (filter 10): 41,630 obs")
print(f"  Paper Table 8 col 1: 17,170 obs, 449T/360C firms")

# Show the gap: our total beta firms vs paper
print(f"\n{'='*70}")
print("FIRM COUNT DIAGNOSIS")
print(f"{'='*70}")
n_total_beta = len(betas)
n_nonneg = len(bpos)
n_high_paper = betas["HIGH"].sum()
n_low_paper = betas["LOW"].sum()
n_high_ours = (betas["beta_uk"] > t2).sum()
n_low_ours = ((betas["beta_uk"] >= 0) & (betas["beta_uk"] < t1)).sum()

print(f"\n  beta_uk firms (CRSP+CCM): {n_total_beta:,}")
print(f"  Nonnegative beta: {n_nonneg:,}")
print(f"  Using PAPER thresholds (0.68/0.28):")
print(f"    HIGH (>0.68): {n_high_paper:,} (paper: 449)")
print(f"    LOW (0<=β<0.28): {n_low_paper:,} (paper: 360)")
print(f"    DiD total: {n_high_paper + n_low_paper:,} (paper: 809)")
print(f"  Using OUR tercile thresholds ({t1:.4f}/{t2:.4f}):")
print(f"    HIGH (>t2): {n_high_ours:,}")
print(f"    LOW (0<=β<t1): {n_low_ours:,}")
print(f"    DiD total: {n_high_ours + n_low_ours:,}")

# KEY CHECK: are we using the right comparison operators?
# Paper says: treated = β > 0.68 (strict), control = β < 0.28 (strict)
# Our code: HIGH = beta_uk >= 0.68 (inclusive), LOW = beta_uk <= 0.28 (inclusive)
n_high_strict = (betas["beta_uk"] > 0.68).sum()
n_low_strict = ((betas["beta_uk"] >= 0) & (betas["beta_uk"] < 0.28)).sum()
n_high_inclusive = (betas["beta_uk"] >= 0.68).sum()
n_low_inclusive = ((betas["beta_uk"] >= 0) & (betas["beta_uk"] <= 0.28)).sum()
at_exact_68 = (betas["beta_uk"] == 0.68).sum()
at_exact_28 = (betas["beta_uk"] == 0.28).sum()
print(f"\n  COMPARISON OPERATOR CHECK:")
print(f"    Exact β=0.68: {at_exact_68} firms")
print(f"    Exact β=0.28: {at_exact_28} firms")
print(f"    HIGH strict (>0.68): {n_high_strict}  vs inclusive (>=0.68): {n_high_inclusive}")
print(f"    LOW strict (<0.28): {n_low_strict}  vs inclusive (<=0.28): {n_low_inclusive}")
