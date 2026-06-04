"""Step 1.4: Complete-case merge — all 7 variables + beta_uk + POST + HIGH_beta + FIC.
Then compare our stats vs paper Table 1 Panel A for all variables."""
import pandas as pd, numpy as np, zipfile, io
from pathlib import Path

ROOT = Path(".")
CSV = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"

# ── 1. Load Compustat base with all needed columns ──────────────────────
comp_cols = ["gvkey","datadate","fyearq","fqtr","sic","curcdq","fic",
             "atq","saleq","cheq","oibdpq","cshoq","prccq","ceqq","txditcq","capxy"]
comp = pd.read_parquet(CSV, columns=comp_cols)
for c in ["atq","saleq","cheq","oibdpq","cshoq","prccq","ceqq","txditcq","capxy"]:
    comp[c] = pd.to_numeric(comp[c], errors="coerce")
comp["txditcq"] = comp["txditcq"].fillna(0)
comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)

# Filters 1-5
comp = comp[(comp["fyearq"]>=2009)&(comp["fyearq"]<=2016)]
comp = comp[comp["fqtr"].isin([1,2,3,4])]
comp = comp[(comp["curcdq"]=="USD")&(comp["fic"]=="USA")]
comp = comp[(comp["atq"]>0)&(comp["saleq"]>0)]
csic = pd.to_numeric(comp["sic"], errors="coerce")
comp = comp[~(csic.between(6000,6999)|csic.between(4900,4999))]
comp = comp[comp["atq"]>10]
comp["cal_yr_qtr"] = comp["fyearq"].astype(int)*10 + comp["fqtr"].astype(int)
print(f"Compustat base (2009-2016): {len(comp):,} obs, {comp['gvkey'].nunique():,} firms")

# ── 2. CASH = cheq / atq_lag1 ───────────────────────────────────────────
comp = comp.sort_values(["gvkey","datadate"])
comp["atq_lag1"] = comp.groupby("gvkey")["atq"].shift(1)
comp["CASH_raw"] = comp["cheq"] / comp["atq_lag1"]
cash = comp[comp["fyearq"].between(2010,2015)][["gvkey","cal_yr_qtr","CASH_raw"]].dropna()
lo, hi = cash["CASH_raw"].quantile(0.01), cash["CASH_raw"].quantile(0.99)
cash["CASH"] = cash["CASH_raw"].clip(lo, hi)
print(f"CASH: {len(cash):,} obs")

# ── 3. SIZE = ln(atq) ───────────────────────────────────────────────────
size_df = comp[comp["fyearq"].between(2010,2015)][["gvkey","cal_yr_qtr","atq"]].dropna()
size_df["SIZE_raw"] = np.log(size_df["atq"])
lo, hi = size_df["SIZE_raw"].quantile(0.01), size_df["SIZE_raw"].quantile(0.99)
size_df["SIZE"] = size_df["SIZE_raw"].clip(lo, hi)
size_df = size_df[["gvkey","cal_yr_qtr","SIZE"]]
print(f"SIZE: {len(size_df):,} obs")

# ── 4. CASH_FLOW = oibdpq / atq_lag1 ────────────────────────────────────
comp["CF_raw"] = comp["oibdpq"] / comp["atq_lag1"]
cf = comp[comp["fyearq"].between(2010,2015)][["gvkey","cal_yr_qtr","CF_raw"]].dropna()
lo, hi = cf["CF_raw"].quantile(0.01), cf["CF_raw"].quantile(0.99)
cf["CASH_FLOW"] = cf["CF_raw"].clip(lo, hi)
print(f"CASH_FLOW: {len(cf):,} obs")

# ── 5. TOBIN_Q = (cshoq*prccq + atq - ceqq + txditcq) / atq ─────────────
comp["Q_raw"] = (comp["cshoq"]*comp["prccq"] + comp["atq"] - comp["ceqq"] + comp["txditcq"]) / comp["atq"]
tq = comp[comp["fyearq"].between(2010,2015)][["gvkey","cal_yr_qtr","Q_raw"]].dropna()
lo, hi = tq["Q_raw"].quantile(0.01), tq["Q_raw"].quantile(0.99)
tq["TOBIN_Q"] = tq["Q_raw"].clip(lo, hi)
print(f"TOBIN_Q: {len(tq):,} obs")

# ── 6. SALES_GROWTH = saleq / saleq_lag4 - 1 ────────────────────────────
comp["saleq_lag4"] = comp.groupby("gvkey")["saleq"].shift(4)
comp["SG_raw"] = comp["saleq"] / comp["saleq_lag4"] - 1
sg = comp[comp["fyearq"].between(2010,2015)][["gvkey","cal_yr_qtr","SG_raw"]].dropna()
lo, hi = sg["SG_raw"].quantile(0.01), sg["SG_raw"].quantile(0.99)
sg["SALES_GROWTH"] = sg["SG_raw"].clip(lo, hi)
print(f"SALES_GROWTH: {len(sg):,} obs")

del comp  # free memory

# ── 7. STOCK_RETURNS (from CRSP, built earlier) ─────────────────────────
sret = pd.read_parquet("tmp/stock_returns_built.parquet") if Path("tmp/stock_returns_built.parquet").exists() else None
if sret is None:
    # Quick rebuild — just load the CRSP BHR we computed
    print("Need to rebuild STOCK_RETURNS — skipping for now")
    sret = pd.DataFrame(columns=["gvkey","cal_yr_qtr","STOCK_RETURNS"])

# ── 8. CONSENSUS_EPS (1.5% per-qtr winsor, per-qtr demean) ──────────────
print("Building CONSENSUS_EPS...")
with zipfile.ZipFile(ROOT/"inputs"/"tr_ibes"/"ibes_statsum.zip") as z:
    with z.open(z.namelist()[0]) as f:
        ibes = pd.read_csv(f, usecols=["TICKER","CUSIP","OFTIC","STATPERS","MEASURE",
            "FISCALP","FPI","MEANEST","FPEDATS","USFIRM","CURCODE"],
            dtype={"TICKER":"str","CUSIP":"str","OFTIC":"str"}, low_memory=False)
ibes["FPI_n"] = pd.to_numeric(ibes["FPI"], errors="coerce")
ibes = ibes[(ibes["MEASURE"]=="EPS")&(ibes["FISCALP"]=="QTR")&(ibes["FPI_n"]==6)&(ibes["CURCODE"]=="USD")&(ibes["USFIRM"]==1)]
ibes["STATPERS"] = pd.to_datetime(ibes["STATPERS"]); ibes["FPEDATS"] = pd.to_datetime(ibes["FPEDATS"])
ibes = ibes[(ibes["FPEDATS"]>="2010-01-01")&(ibes["FPEDATS"]<="2017-03-31")]
ibes = ibes[ibes["STATPERS"] < ibes["FPEDATS"]]
ibes = ibes.sort_values(["TICKER","FPEDATS","STATPERS"])
ibes = ibes.drop_duplicates(subset=["TICKER","FPEDATS"], keep="last")
ibes["M"] = pd.to_numeric(ibes["MEANEST"], errors="coerce")
fpe_yq = ibes["FPEDATS"].dt.year*10 + ibes["FPEDATS"].dt.quarter
yr, qtr = fpe_yq//10, fpe_yq%10
ibes["cal_yr_qtr"] = (np.where(qtr==1, yr-1, yr)*10 + np.where(qtr==1, 4, qtr-1)).astype(np.int64)

comp_map = pd.read_parquet(CSV, columns=["gvkey","tic","cusip","datadate"])
comp_map["gvkey"] = comp_map["gvkey"].astype(str).str.zfill(6)
comp_map["datadate"] = pd.to_datetime(comp_map["datadate"])
comp_map = comp_map[(comp_map["datadate"]>="2010-01-01")&(comp_map["datadate"]<="2017-03-31")]
comp_map["cal_yr_qtr"] = (comp_map["datadate"].dt.year*10+comp_map["datadate"].dt.quarter).astype(np.int64)
comp_map["cusip8"] = comp_map["cusip"].astype(str).str[:8]
ibes["CUSIP8"] = ibes["CUSIP"].astype(str).str[:8]
comp_cusip = comp_map[["gvkey","cusip8","cal_yr_qtr"]].drop_duplicates()
vc = ibes.merge(comp_cusip, left_on=["CUSIP8","cal_yr_qtr"], right_on=["cusip8","cal_yr_qtr"], how="inner")
vt = ibes.merge(comp_map[["gvkey","tic","cal_yr_qtr"]].drop_duplicates(),
                left_on=["OFTIC","cal_yr_qtr"], right_on=["tic","cal_yr_qtr"], how="inner")
ceps = pd.concat([vc[["gvkey","cal_yr_qtr","M"]], vt[["gvkey","cal_yr_qtr","M"]]], ignore_index=True)
ceps = ceps.drop_duplicates(subset=["gvkey","cal_yr_qtr"], keep="first")
ceps["gvkey"] = ceps["gvkey"].astype(str).str.zfill(6)

# Sample filter
comp_filt = pd.read_parquet(CSV, columns=["gvkey","fyearq","fqtr","sic","curcdq","fic","atq","saleq"])
for c in ["atq","saleq"]: comp_filt[c] = pd.to_numeric(comp_filt[c], errors="coerce")
comp_filt = comp_filt[(comp_filt["fyearq"]>=2010)&(comp_filt["fyearq"]<=2015)]
comp_filt = comp_filt[comp_filt["fqtr"].isin([1,2,3,4])]
comp_filt = comp_filt[(comp_filt["curcdq"]=="USD")&(comp_filt["fic"]=="USA")]
comp_filt = comp_filt[(comp_filt["atq"]>0)&(comp_filt["saleq"]>0)]
csic2 = pd.to_numeric(comp_filt["sic"], errors="coerce")
comp_filt = comp_filt[~(csic2.between(6000,6999)|csic2.between(4900,4999))]
comp_filt = comp_filt[comp_filt["atq"]>10]
comp_filt["gvkey"] = comp_filt["gvkey"].astype(str).str.zfill(6)
ceps = ceps[ceps["gvkey"].isin(set(comp_filt["gvkey"].unique()))]

# Per-qtr winsor 1.5% -> per-qtr demean
ceps["M_qw"] = np.nan
for qt, idx in ceps.groupby("cal_yr_qtr").groups.items():
    v = ceps.loc[idx, "M"]
    if v.notna().sum() < 10: continue
    lo, hi = v.quantile(0.015), v.quantile(0.985)
    ceps.loc[idx, "M_qw"] = v.clip(lo, hi)
ceps["CONSENSUS_EPS"] = np.nan
for qt, idx in ceps.groupby("cal_yr_qtr").groups.items():
    v = ceps.loc[idx, "M_qw"]
    if v.notna().sum() < 10: continue
    ceps.loc[idx, "CONSENSUS_EPS"] = v - v.mean()
ceps = ceps[["gvkey","cal_yr_qtr","CONSENSUS_EPS"]].dropna()
print(f"CONSENSUS_EPS: {len(ceps):,} obs")

# ── 9. Load beta_uk ─────────────────────────────────────────────────────
beta = pd.read_parquet("outputs/campello_v2/20260526_235149/beta_uk.parquet")
beta["gvkey"] = beta["gvkey"].astype(str).str.zfill(6)
print(f"beta_uk: {len(beta):,} firms")

# ── 10. POST_t ──────────────────────────────────────────────────────────
# POST=1 for 2016:Q3-Q4; the DiD compares 2016:Q3-Q4 vs 2015:Q3-Q4
quarters = pd.DataFrame({"cal_yr_qtr": [20153,20154,20163,20164]})
quarters["POST"] = quarters["cal_yr_qtr"].isin([20163,20164]).astype(int)

# ── 11. HIGH_beta_UK = top tercile of nonnegative beta ──────────────────
bpos = beta[beta["beta_uk"] >= 0].copy()
t2 = bpos["beta_uk"].quantile(2/3)
beta["HIGH_beta_UK"] = (beta["beta_uk"] >= t2).astype(int)
# Control group: bottom tercile of nonnegative beta
t1 = bpos["beta_uk"].quantile(1/3)
beta["LOW_beta_UK"] = (beta["beta_uk"] <= t1).astype(int)
print(f"  Top tercile (beta > {t2:.4f}): {beta['HIGH_beta_UK'].sum():,} firms")
print(f"  Bot tercile (beta < {t1:.4f}): {beta['LOW_beta_UK'].sum():,} firms")
print(f"  Paper: treated=449 (beta>0.68), control=360 (beta<0.28)")

# ── 12. FIC 100 ─────────────────────────────────────────────────────────
with zipfile.ZipFile(ROOT/"inputs"/"Brexit_replication"/"HobergPhillips_FIC"/"FIC_Data.zip") as zf:
    with zf.open("fic_data.txt") as f:
        fic = pd.read_csv(io.BytesIO(f.read()), sep="\t", usecols=["gvkey","year","icode100"])
fic["gvkey"] = fic["gvkey"].astype(str).str.zfill(6)
fic = fic[(fic["year"]>=2010)&(fic["year"]<=2016)]
print(f"FIC: {len(fic):,} obs")

# ── 13. MERGE ALL ───────────────────────────────────────────────────────
panel = pd.DataFrame({
    "gvkey": sorted(set(
        list(cash["gvkey"]) + list(size_df["gvkey"]) + list(cf["gvkey"]) +
        list(tq["gvkey"]) + list(sg["gvkey"]) + list(ceps["gvkey"])
    ))
})
# Cross with quarters
quarters_list = [20153, 20154, 20163, 20164]
all_quarters = pd.DataFrame({"cal_yr_qtr": quarters_list})
panel["_key"] = 1; all_quarters["_key"] = 1
panel = panel.merge(all_quarters, on="_key").drop("_key", axis=1)

# Merge variables one by one
panel = panel.merge(cash[["gvkey","cal_yr_qtr","CASH"]], on=["gvkey","cal_yr_qtr"], how="left")
panel = panel.merge(size_df, on=["gvkey","cal_yr_qtr"], how="left")
panel = panel.merge(cf[["gvkey","cal_yr_qtr","CASH_FLOW"]], on=["gvkey","cal_yr_qtr"], how="left")
panel = panel.merge(tq[["gvkey","cal_yr_qtr","TOBIN_Q"]], on=["gvkey","cal_yr_qtr"], how="left")
panel = panel.merge(sg[["gvkey","cal_yr_qtr","SALES_GROWTH"]], on=["gvkey","cal_yr_qtr"], how="left")
panel = panel.merge(ceps, on=["gvkey","cal_yr_qtr"], how="left")
panel = panel.merge(beta[["gvkey","beta_uk","HIGH_beta_UK","LOW_beta_UK"]], on="gvkey", how="left")
panel = panel.merge(quarters, on="cal_yr_qtr", how="left")

# Map year for FIC
panel["year"] = panel["cal_yr_qtr"] // 10
panel = panel.merge(fic, on=["gvkey","year"], how="left")

print(f"\nFull panel: {len(panel):,} obs, {panel['gvkey'].nunique():,} firms")

# Complete-case: drop NaN in any variable
vars_list = ["CASH","SIZE","CASH_FLOW","TOBIN_Q","SALES_GROWTH","CONSENSUS_EPS","beta_uk","icode100"]
cc = panel.dropna(subset=vars_list)
print(f"Complete-case (all {len(vars_list)} vars): {len(cc):,} obs")
# DiD sample: only TREATED or CONTROL (drop middle tercile)
did = cc[(cc["HIGH_beta_UK"]==1)|(cc["LOW_beta_UK"]==1)].copy()
did["TREATED"] = did["HIGH_beta_UK"]
print(f"DiD sample (high+low tercile only): {len(did):,} obs, {did['gvkey'].nunique():,} firms")
print(f"  Treated: {did['TREATED'].sum():,} obs, {did[did['TREATED']==1]['gvkey'].nunique():,} firms")
print(f"  Control: {(did['TREATED']==0).sum():,} obs, {did[did['TREATED']==0]['gvkey'].nunique():,} firms")
print(f"\n  POST=1 obs: {(did['POST']==1).sum():,}")
print(f"  POST=0 obs: {(did['POST']==0).sum():,}")
