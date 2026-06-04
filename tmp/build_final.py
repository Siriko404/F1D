"""Step 1.4 final: fresh beta_uk + all 7 vars + STOCK_RETURNS + POST + HIGH_beta + FIC → CC merge"""
import pandas as pd, numpy as np, zipfile, io
from pathlib import Path

ROOT = Path(".")
CSV = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
MIN_DAYS, MIN_MONTHS = 15, 24

print("="*60)
print("1. BETA_UK (Bloom 2009: monthly SD of daily returns)")
print("="*60)

# Firm daily returns → monthly realized vol
frames = []
for y in range(2010, 2015):
    for q in range(1, 5):
        f = ROOT/"inputs"/"CRSP_DSF"/f"CRSP_DSF_{y}_Q{q}.parquet"
        if f.exists(): frames.append(pd.read_parquet(f, columns=["PERMNO","date","RET"]))
crsp = pd.concat(frames, ignore_index=True)
crsp["date"] = pd.to_datetime(crsp["date"]); crsp["RET"] = pd.to_numeric(crsp["RET"], errors="coerce")
crsp["ym"] = crsp["date"].dt.to_period("M")
grp = crsp.groupby(["PERMNO","ym"])
rv = grp["RET"].std()  # Bloom 2009: monthly SD, NO annualization
rv = rv[grp["RET"].count() >= MIN_DAYS].reset_index()
rv.columns = ["PERMNO","ym","vol_r"]

# SP500 from same CRSP (sprtrn)
frames2 = []
for y in range(2010, 2015):
    for q in range(1, 5):
        f = ROOT/"inputs"/"CRSP_DSF"/f"CRSP_DSF_{y}_Q{q}.parquet"
        if f.exists(): frames2.append(pd.read_parquet(f, columns=["PERMNO","date","RET","sprtrn"]))
crsp2 = pd.concat(frames2, ignore_index=True)
crsp2["date"] = pd.to_datetime(crsp2["date"]); crsp2["sprtrn_n"] = pd.to_numeric(crsp2["sprtrn"], errors="coerce")
crsp2["ym"] = crsp2["date"].dt.to_period("M")
sp = crsp2[["date","sprtrn_n","ym"]].drop_duplicates()
spg = sp.groupby("ym")
sp500 = spg["sprtrn_n"].std()
sp500 = sp500[spg["sprtrn_n"].count() >= MIN_DAYS].reset_index()
sp500.columns = ["ym","vol_SP500"]
del crsp, crsp2, sp

# FTSE100 daily → monthly realized vol
ftse = pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"Yahoo_FTSE100"/"FTSE100_yfinance_daily.csv")
ftse["Date"] = pd.to_datetime(ftse["Date"])
ftse = ftse[(ftse["Date"]>="2010-01-01")&(ftse["Date"]<="2014-12-31")].sort_values("Date")
ftse["lr"] = np.log(ftse["Close"]/ftse["Close"].shift(1))
ftse["ym"] = ftse["Date"].dt.to_period("M")
fg = ftse.groupby("ym"); ftse_v = fg["lr"].std()
ftse_v = ftse_v[fg["lr"].count() >= MIN_DAYS].reset_index(); ftse_v.columns = ["ym","vol_FTSE100"]

# FX volatility
fx = pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"BoE"/"USD_GBP_daily_2008-2018.csv")
fx["DATE"] = pd.to_datetime(fx["DATE"], dayfirst=True)
fx = fx[(fx["DATE"]>="2010-01-01")&(fx["DATE"]<="2014-12-31")].sort_values("DATE")
fx["lr"] = np.log(fx["XUDLUSS"]/fx["XUDLUSS"].shift(1))
fx["ym"] = fx["DATE"].dt.to_period("M")
fgg = fx.groupby("ym"); fx_v = fgg["lr"].std()
fx_v = fx_v[fgg["lr"].count() >= MIN_DAYS].reset_index(); fx_v.columns = ["ym","vol_FX"]

# Merge macro
macro = sp500.merge(ftse_v, on="ym").merge(fx_v, on="ym")
rv["ym"] = rv["ym"].astype(str); macro["ym"] = macro["ym"].astype(str)
merged = rv.merge(macro, on="ym", how="inner")

# OLS per firm
results = []
for permno, grp in merged.groupby("PERMNO"):
    grp = grp.dropna(subset=["vol_r","vol_FTSE100","vol_SP500","vol_FX"])
    if len(grp) < MIN_MONTHS: continue
    y = grp["vol_r"].values
    X = np.column_stack([np.ones(len(y)), grp["vol_FTSE100"], grp["vol_SP500"], grp["vol_FX"]])
    try:
        b = np.linalg.lstsq(X, y, rcond=None)[0]
        yhat = X @ b; ssr = np.sum((y-yhat)**2); sst = np.sum((y-y.mean())**2)
        results.append({"PERMNO":permno,"beta_uk":b[1],"n":len(grp),"r2":1-ssr/sst if sst>0 else 0})
    except: continue
betas = pd.DataFrame(results)

# CCM
ccm = pd.read_parquet(ROOT/"inputs"/"CRSPCompustat_CCM"/"CRSPCompustat_CCM.parquet",
    columns=["gvkey","LPERMNO","LINKDT","LINKENDDT","LINKTYPE","LINKPRIM"])
ccm["gvkey"] = ccm["gvkey"].astype(str).str.zfill(6)
ccm = ccm[ccm["LINKTYPE"].isin(["LU","LC"])]; ccm = ccm[ccm["LINKPRIM"].isin(["P","C"])]
ccm["LINKDT"] = pd.to_datetime(ccm["LINKDT"], errors="coerce"); ccm["LINKENDDT"] = pd.to_datetime(ccm["LINKENDDT"], errors="coerce")
ccm["LINKENDDT"] = ccm["LINKENDDT"].fillna(pd.Timestamp("2099-12-31"))
ccm = ccm[(ccm["LINKENDDT"]>=pd.Timestamp("2010-01-01"))&(ccm["LINKDT"]<=pd.Timestamp("2014-12-31"))]
ccm["LPERMNO"] = pd.to_numeric(ccm["LPERMNO"], errors="coerce").astype("Int64"); ccm = ccm.dropna(subset=["LPERMNO"])
betas = betas.merge(ccm[["gvkey","LPERMNO"]].drop_duplicates(), left_on="PERMNO", right_on="LPERMNO", how="inner")
betas = betas.drop_duplicates(subset=["gvkey"], keep="first")
betas["gvkey"] = betas["gvkey"].astype(str).str.zfill(6)
print(f"beta_uk: {len(betas):,} firms (CRSP+CCM)")

# Terciles on nonnegative
bpos = betas[betas["beta_uk"]>=0]
t2, t1 = bpos["beta_uk"].quantile(2/3), bpos["beta_uk"].quantile(1/3)
betas["HIGH"] = (betas["beta_uk"]>=t2).astype(int)
betas["LOW"] = (betas["beta_uk"]<=t1).astype(int)
# Paper thresholds for comparison
at_paper_t = (bpos["beta_uk"]>0.68).sum()
at_paper_c = (bpos["beta_uk"]<0.28).sum()
print(f"  Tercile thresholds: {t1:.4f} / {t2:.4f} (paper: 0.28 / 0.68)")
print(f"  HIGH (>={t2:.2f}): {betas['HIGH'].sum():,} firms (paper: 449)")
print(f"  LOW (<={t1:.2f}): {betas['LOW'].sum():,} firms (paper: 360)")
print(f"  At paper thresholds: >0.68={at_paper_t}, <0.28={at_paper_c}")

betas[["gvkey","beta_uk","HIGH","LOW","n","r2"]].to_parquet("tmp/beta_uk_final.parquet", index=False)

print(f"\n{'='*60}")
print(f"2. STOCK_RETURNS (quarterly BHR from daily CRSP)")
print(f"{'='*60}")

frames3 = []
for y in range(2009, 2017):
    for qq in range(1, 5):
        f = ROOT/"inputs"/"CRSP_DSF"/f"CRSP_DSF_{y}_Q{qq}.parquet"
        if f.exists(): frames3.append(pd.read_parquet(f, columns=["PERMNO","date","RET"]))
crsp3 = pd.concat(frames3, ignore_index=True)
crsp3["date"] = pd.to_datetime(crsp3["date"]); crsp3["RET"] = pd.to_numeric(crsp3["RET"], errors="coerce")
crsp3["cal_yr_qtr"] = crsp3["date"].dt.year*10 + crsp3["date"].dt.quarter
crsp3["one_plus_r"] = 1 + crsp3["RET"].fillna(0)
bhr = crsp3.groupby(["PERMNO","cal_yr_qtr"])["one_plus_r"].prod() - 1
sret = bhr.reset_index(); sret.columns = ["PERMNO","cal_yr_qtr","SR_raw"]

# CCM merge
sret = sret.merge(ccm[["gvkey","LPERMNO"]].drop_duplicates(), left_on="PERMNO", right_on="LPERMNO", how="inner")
sret = sret.drop_duplicates(subset=["gvkey","cal_yr_qtr"], keep="first")
sret["gvkey"] = sret["gvkey"].astype(str).str.zfill(6)
# Winsorize 1%
lo, hi = sret["SR_raw"].quantile(0.01), sret["SR_raw"].quantile(0.99)
sret["STOCK_RETURNS"] = sret["SR_raw"].clip(lo, hi)
sret = sret[(sret["cal_yr_qtr"]>=20101)&(sret["cal_yr_qtr"]<=20164)]  # include 2016
sret = sret[["gvkey","cal_yr_qtr","STOCK_RETURNS"]]
del crsp3, bhr
print(f"STOCK_RETURNS: {len(sret):,} obs")

print(f"\n{'='*60}")
print(f"3. ALL COMPUSTAT VARS")
print(f"{'='*60}")

comp = pd.read_parquet(CSV, columns=["gvkey","datadate","fyearq","fqtr","sic","curcdq","fic",
    "atq","saleq","cheq","oibdpq","cshoq","prccq","ceqq","txditcq"])
for c in ["atq","saleq","cheq","oibdpq","cshoq","prccq","ceqq","txditcq"]:
    comp[c] = pd.to_numeric(comp[c], errors="coerce")
comp["txditcq"] = comp["txditcq"].fillna(0)
comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
comp = comp[(comp["fyearq"]>=2009)&(comp["fyearq"]<=2016)]
comp = comp[comp["fqtr"].isin([1,2,3,4])]
comp = comp[(comp["curcdq"]=="USD")&(comp["fic"]=="USA")]
comp = comp[(comp["atq"]>0)&(comp["saleq"]>0)]
csic = pd.to_numeric(comp["sic"], errors="coerce")
comp = comp[~(csic.between(6000,6999)|csic.between(4900,4999))]
comp = comp[comp["atq"]>10]
comp["cal_yr_qtr"] = comp["fyearq"].astype(int)*10 + comp["fqtr"].astype(int)
comp = comp.sort_values(["gvkey","datadate"])
comp["atq_lag1"] = comp.groupby("gvkey")["atq"].shift(1)
comp["saleq_lag4"] = comp.groupby("gvkey")["saleq"].shift(4)

filt = comp["fyearq"].between(2010, 2016)  # include 2016 for DiD

# CASH
comp["CASH_raw"] = comp["cheq"] / comp["atq_lag1"]
cash = comp.loc[filt, ["gvkey","cal_yr_qtr","CASH_raw"]].dropna()
lo_c, hi_c = cash["CASH_raw"].quantile(0.01), cash["CASH_raw"].quantile(0.99)
cash = cash.copy(); cash["CASH"] = cash["CASH_raw"].clip(lo_c, hi_c)
cash = cash[["gvkey","cal_yr_qtr","CASH"]]

# SIZE
sz = comp.loc[filt, ["gvkey","cal_yr_qtr","atq"]].dropna().copy()
sz["SIZE_raw"] = np.log(sz["atq"])
lo_sz, hi_sz = sz["SIZE_raw"].quantile(0.01), sz["SIZE_raw"].quantile(0.99)
sz["SIZE"] = sz["SIZE_raw"].clip(lo_sz, hi_sz); sz = sz[["gvkey","cal_yr_qtr","SIZE"]]

# CASH_FLOW
comp["CF_raw"] = comp["oibdpq"] / comp["atq_lag1"]
cf2 = comp.loc[filt, ["gvkey","cal_yr_qtr","CF_raw"]].dropna().copy()
lo_cf, hi_cf = cf2["CF_raw"].quantile(0.01), cf2["CF_raw"].quantile(0.99)
cf2["CASH_FLOW"] = cf2["CF_raw"].clip(lo_cf, hi_cf); cf2 = cf2[["gvkey","cal_yr_qtr","CASH_FLOW"]]

# TOBIN_Q
comp["Q_raw"] = (comp["cshoq"]*comp["prccq"]+comp["atq"]-comp["ceqq"]+comp["txditcq"])/comp["atq"]
tq2 = comp.loc[filt, ["gvkey","cal_yr_qtr","Q_raw"]].dropna().copy()
lo_q, hi_q = tq2["Q_raw"].quantile(0.01), tq2["Q_raw"].quantile(0.99)
tq2["TOBIN_Q"] = tq2["Q_raw"].clip(lo_q, hi_q); tq2 = tq2[["gvkey","cal_yr_qtr","TOBIN_Q"]]

# SALES_GROWTH
comp["SG_raw"] = comp["saleq"] / comp["saleq_lag4"] - 1
sg2 = comp.loc[filt, ["gvkey","cal_yr_qtr","SG_raw"]].dropna().copy()
lo_sg, hi_sg = sg2["SG_raw"].quantile(0.01), sg2["SG_raw"].quantile(0.99)
sg2["SALES_GROWTH"] = sg2["SG_raw"].clip(lo_sg, hi_sg); sg2 = sg2[["gvkey","cal_yr_qtr","SALES_GROWTH"]]

del comp

comp_f = pd.read_parquet(CSV, columns=["gvkey","fyearq","fqtr","sic","curcdq","fic","atq","saleq"])
for c in ["atq","saleq"]: comp_f[c] = pd.to_numeric(comp_f[c], errors="coerce")
comp_f["gvkey"] = comp_f["gvkey"].astype(str).str.zfill(6)
comp_f = comp_f[(comp_f["fyearq"]>=2010)&(comp_f["fyearq"]<=2016)]  # include 2016 for DiD
comp_f = comp_f[comp_f["fqtr"].isin([1,2,3,4])]
comp_f = comp_f[(comp_f["curcdq"]=="USD")&(comp_f["fic"]=="USA")]
comp_f = comp_f[(comp_f["atq"]>0)&(comp_f["saleq"]>0)]
csic2 = pd.to_numeric(comp_f["sic"], errors="coerce")
comp_f = comp_f[~(csic2.between(6000,6999)|csic2.between(4900,4999))]
comp_f = comp_f[comp_f["atq"]>10]
sample_gvkeys = set(comp_f["gvkey"].unique())

# CONSENSUS_EPS (per-qtr winsor 1.5% -> per-qtr demean)
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
comp_map2 = pd.read_parquet(CSV, columns=["gvkey","tic","cusip","datadate"])
comp_map2["gvkey"] = comp_map2["gvkey"].astype(str).str.zfill(6)
comp_map2["datadate"] = pd.to_datetime(comp_map2["datadate"])
comp_map2 = comp_map2[(comp_map2["datadate"]>="2010-01-01")&(comp_map2["datadate"]<="2017-03-31")]
comp_map2["cal_yr_qtr"] = (comp_map2["datadate"].dt.year*10+comp_map2["datadate"].dt.quarter).astype(np.int64)
comp_map2["cusip8"] = comp_map2["cusip"].astype(str).str[:8]
ibes["CUSIP8"] = ibes["CUSIP"].astype(str).str[:8]
cm = comp_map2[["gvkey","cusip8","cal_yr_qtr"]].drop_duplicates()
vc = ibes.merge(cm, left_on=["CUSIP8","cal_yr_qtr"], right_on=["cusip8","cal_yr_qtr"], how="inner")
vt = ibes.merge(comp_map2[["gvkey","tic","cal_yr_qtr"]].drop_duplicates(),
                left_on=["OFTIC","cal_yr_qtr"], right_on=["tic","cal_yr_qtr"], how="inner")
ceps = pd.concat([vc[["gvkey","cal_yr_qtr","M"]], vt[["gvkey","cal_yr_qtr","M"]]], ignore_index=True)
ceps = ceps.drop_duplicates(subset=["gvkey","cal_yr_qtr"], keep="first")
ceps["gvkey"] = ceps["gvkey"].astype(str).str.zfill(6)
ceps = ceps[ceps["gvkey"].isin(sample_gvkeys)]
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

# FIC
with zipfile.ZipFile(ROOT/"inputs"/"Brexit_replication"/"HobergPhillips_FIC"/"FIC_Data.zip") as zf:
    with zf.open("fic_data.txt") as f:
        fic = pd.read_csv(io.BytesIO(f.read()), sep="\t", usecols=["gvkey","year","icode100"])
fic["gvkey"] = fic["gvkey"].astype(str).str.zfill(6)

print(f"{'='*60}")
print(f"4. COMPLETE-CASE MERGE")
print(f"{'='*60}")

# Panel: all gvkey × DiD quarters
gvkeys = sorted(sample_gvkeys)
panel = pd.DataFrame({"gvkey": np.repeat(gvkeys, 4),
                       "cal_yr_qtr": [20153,20154,20163,20164]*len(gvkeys)})

panel = panel.merge(cash, on=["gvkey","cal_yr_qtr"], how="left")
panel = panel.merge(sz, on=["gvkey","cal_yr_qtr"], how="left")
panel = panel.merge(cf2, on=["gvkey","cal_yr_qtr"], how="left")
panel = panel.merge(tq2, on=["gvkey","cal_yr_qtr"], how="left")
panel = panel.merge(sg2, on=["gvkey","cal_yr_qtr"], how="left")
panel = panel.merge(ceps, on=["gvkey","cal_yr_qtr"], how="left")
panel = panel.merge(sret, on=["gvkey","cal_yr_qtr"], how="left")
panel = panel.merge(betas[["gvkey","beta_uk","HIGH","LOW"]], on="gvkey", how="left")
panel["POST"] = panel["cal_yr_qtr"].isin([20163,20164]).astype(int)
panel["year"] = panel["cal_yr_qtr"]//10
panel = panel.merge(fic, on=["gvkey","year"], how="left")

vars_list = ["CASH","SIZE","CASH_FLOW","TOBIN_Q","SALES_GROWTH","STOCK_RETURNS","CONSENSUS_EPS","beta_uk","icode100"]
cc = panel.dropna(subset=vars_list).copy()
cc["interaction"] = cc["POST"] * cc["HIGH"]

print(f"Full panel: {len(panel):,}")
print(f"Complete-case: {len(cc):,} obs, {cc['gvkey'].nunique():,} firms")
print(f"  POST=1: {cc['POST'].sum():,}  POST=0: {(cc['POST']==0).sum():,}")
print(f"  HIGH=1: {cc['HIGH'].sum():,}  LOW=1: {cc['LOW'].sum():,}")
print(f"  Interaction=1: {cc['interaction'].sum():,}")
print(f"  POST=1 & HIGH=1: {len(cc[(cc['POST']==1)&(cc['HIGH']==1)]):,}")
print(f"  POST=0 & HIGH=1: {len(cc[(cc['POST']==0)&(cc['HIGH']==1)]):,}")
print(f"  POST=1 & LOW=1: {len(cc[(cc['POST']==1)&(cc['LOW']==1)]):,}")
print(f"  POST=0 & LOW=1: {len(cc[(cc['POST']==0)&(cc['LOW']==1)]):,}")
print(f"  Total DiD (HIGH|LOW): {len(cc[(cc['HIGH']==1)|(cc['LOW']==1)]):,}")
