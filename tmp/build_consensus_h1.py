"""H1: Industry-quarter demeaned forward earnings yield (pp).
CEF = (MEANEST / PRC_lag) * 100 - mean_{industry×quarter}[(MEANEST/PRC)*100]
Table 1 Panel A: N=42031 mean=0.07 SD=3.51 p50=0.09
"""
import pandas as pd, numpy as np, zipfile
from pathlib import Path

ROOT = Path(".")

# ── 1. IBES (skip SUE; just need MEANEST) ──────────────────────────────
with zipfile.ZipFile(ROOT/"inputs"/"tr_ibes"/"ibes_statsum.zip") as z:
    with z.open(z.namelist()[0]) as f:
        ibes = pd.read_csv(f, usecols=["TICKER","CUSIP","OFTIC","STATPERS","MEASURE",
            "FISCALP","FPI","MEANEST","FPEDATS","USFIRM","CURCODE"],
            dtype={"TICKER":"str","CUSIP":"str","OFTIC":"str"}, low_memory=False)

ibes["FPI_n"] = pd.to_numeric(ibes["FPI"], errors="coerce")
ibes = ibes[(ibes["MEASURE"]=="EPS")&(ibes["FISCALP"]=="QTR")&(ibes["FPI_n"]==6)
            &(ibes["CURCODE"]=="USD")&(ibes["USFIRM"]==1)]
ibes["STATPERS"] = pd.to_datetime(ibes["STATPERS"])
ibes["FPEDATS"] = pd.to_datetime(ibes["FPEDATS"])
ibes = ibes[(ibes["FPEDATS"]>="2010-01-01")&(ibes["FPEDATS"]<="2017-03-31")]
ibes = ibes[ibes["STATPERS"] < ibes["FPEDATS"]]
ibes = ibes.sort_values(["TICKER","FPEDATS","STATPERS"])
ibes = ibes.drop_duplicates(subset=["TICKER","FPEDATS"], keep="last")
ibes["MEANEST_n"] = pd.to_numeric(ibes["MEANEST"], errors="coerce")

# cal_yr_qtr: forecast for Q+1, attach to Q
fpe_yq = ibes["FPEDATS"].dt.year*10 + ibes["FPEDATS"].dt.quarter
yr, qtr = fpe_yq//10, fpe_yq%10
prev_qtr = np.where(qtr==1, 4, qtr-1)
prev_yr = np.where(qtr==1, yr-1, yr)
ibes["cal_yr_qtr"] = (prev_yr*10 + prev_qtr).astype(np.int64)

# ── 2. Get quarter-end stock price from CRSP ────────────────────────────
# Load CCM + CRSP to get price per gvkey per quarter
ccm = pd.read_parquet(ROOT/"inputs"/"CRSPCompustat_CCM"/"CRSPCompustat_CCM.parquet",
    columns=["gvkey","LPERMNO","LINKDT","LINKENDDT","LINKTYPE","LINKPRIM"])
ccm["gvkey"] = ccm["gvkey"].astype(str).str.zfill(6)
ccm = ccm[ccm["LINKTYPE"].isin(["LU","LC"])]
ccm = ccm[ccm["LINKPRIM"].isin(["P","C"])]
ccm["LINKDT"] = pd.to_datetime(ccm["LINKDT"], errors="coerce")
ccm["LINKENDDT"] = pd.to_datetime(ccm["LINKENDDT"], errors="coerce")
ccm["LINKENDDT"] = ccm["LINKENDDT"].fillna(pd.Timestamp("2099-12-31"))
ccm = ccm[(ccm["LINKENDDT"]>=pd.Timestamp("2009-01-01"))&(ccm["LINKDT"]<=pd.Timestamp("2016-12-31"))]
ccm["LPERMNO"] = pd.to_numeric(ccm["LPERMNO"], errors="coerce").astype("Int64")
ccm = ccm.dropna(subset=["LPERMNO"])

# Load CRSP daily: PERMNO, date, PRC (absolute price)
frames = []
for year in range(2009, 2017):
    for q in range(1, 5):
        f = ROOT/"inputs"/"CRSP_DSF"/f"CRSP_DSF_{year}_Q{q}.parquet"
        if f.exists():
            df = pd.read_parquet(f, columns=["PERMNO","date","PRC"])
            frames.append(df)
crsp = pd.concat(frames, ignore_index=True)
crsp["date"] = pd.to_datetime(crsp["date"])
crsp["PRC"] = pd.to_numeric(crsp["PRC"], errors="coerce")
# CRSP: negative PRC = bid/ask avg flag, use abs. Filter to plausible range
crsp["PRC"] = crsp["PRC"].abs()
crsp = crsp[(crsp["PRC"] >= 1) & (crsp["PRC"] <= 10000)]  # $1-$10K plausible

# Get quarter-end price: last trading day of each (PERMNO, cal_yr_qtr)
crsp["cal_yr_qtr"] = crsp["date"].dt.year*10 + crsp["date"].dt.quarter
crsp = crsp.sort_values(["PERMNO","cal_yr_qtr","date"])
qe_price = crsp.groupby(["PERMNO","cal_yr_qtr"])["PRC"].last().reset_index()
qe_price.columns = ["PERMNO","cal_yr_qtr","PRC_qend"]
del crsp

# ── 3. Map PERMNO -> gvkey, merge quarter-end price ─────────────────────
ccm_sub = ccm[["gvkey","LPERMNO"]].drop_duplicates()
qe_price = qe_price.merge(ccm_sub, left_on="PERMNO", right_on="LPERMNO", how="inner")
qe_price["gvkey"] = qe_price["gvkey"].astype(str).str.zfill(6)
# Deduplicate: one gvkey per quarter
qe_price = qe_price.sort_values(["gvkey","cal_yr_qtr","PRC_qend"], ascending=[True,True,False])
qe_price = qe_price.drop_duplicates(subset=["gvkey","cal_yr_qtr"], keep="first")
print(f"Quarter-end prices: {len(qe_price):,} gvkey-quarters")

# Lag price by 1 quarter
qe_price = qe_price.sort_values(["gvkey","cal_yr_qtr"])
qe_price["PRC_lag1"] = qe_price.groupby("gvkey")["PRC_qend"].shift(1)

# ── 4. Map IBES to gvkey via CUSIP-8 ────────────────────────────────────
comp_map = pd.read_parquet(ROOT/"inputs"/"comp_na_daily_all"/"comp_na_daily_all.parquet",
    columns=["gvkey","tic","cusip","datadate"])
comp_map["gvkey"] = comp_map["gvkey"].astype(str).str.zfill(6)
comp_map["datadate"] = pd.to_datetime(comp_map["datadate"])
comp_map = comp_map[(comp_map["datadate"]>="2010-01-01")&(comp_map["datadate"]<="2017-03-31")]
comp_map["cal_yr_qtr"] = (comp_map["datadate"].dt.year*10+comp_map["datadate"].dt.quarter).astype(np.int64)
comp_map["cusip8"] = comp_map["cusip"].astype(str).str[:8]

ibes["CUSIP8"] = ibes["CUSIP"].astype(str).str[:8]
comp_cusip = comp_map[["gvkey","cusip8","cal_yr_qtr"]].drop_duplicates()
via_cusip = ibes.merge(comp_cusip, left_on=["CUSIP8","cal_yr_qtr"],
                        right_on=["cusip8","cal_yr_qtr"], how="inner")
comp_tic2 = comp_map[["gvkey","tic","cal_yr_qtr"]].drop_duplicates()
via_tic = ibes.merge(comp_tic2, left_on=["OFTIC","cal_yr_qtr"],
                      right_on=["tic","cal_yr_qtr"], how="inner")
merged = pd.concat([via_cusip[["gvkey","cal_yr_qtr","MEANEST_n"]],
                     via_tic[["gvkey","cal_yr_qtr","MEANEST_n"]]], ignore_index=True)
merged = merged.drop_duplicates(subset=["gvkey","cal_yr_qtr"], keep="first")
print(f"IBES->gvkey: {len(merged):,}")

# ── 5. Merge price ──────────────────────────────────────────────────────
merged["gvkey"] = merged["gvkey"].astype(str).str.zfill(6)
merged = merged.merge(qe_price[["gvkey","cal_yr_qtr","PRC_qend","PRC_lag1"]],
                       on=["gvkey","cal_yr_qtr"], how="left")
merged = merged.dropna(subset=["PRC_lag1"])
merged = merged[merged["PRC_lag1"].abs() > 1]  # sanity filter
print(f"With price: {len(merged):,}")

# ── 6. Forward EPS yield = (MEANEST / lagged_price) * 100 ────────────────
# Filter extreme MEANEST first (split-unadjusted IBES garbage)
merged = merged[(merged["MEANEST_n"].abs() < 50) & (merged["MEANEST_n"].notna())]
merged["FEY"] = (merged["MEANEST_n"] / merged["PRC_lag1"]) * 100
# Filter FEY to plausible range
merged = merged[merged["FEY"].abs() < 200]

# ── 7. Get Hoberg-Phillips FIC100 for industry ──────────────────────────
import io
fic_path = ROOT/"inputs"/"Brexit_replication"/"HobergPhillips_FIC"/"FIC_Data.zip"
with zipfile.ZipFile(fic_path) as zf:
    with zf.open("fic_data.txt") as f:
        fic = pd.read_csv(io.BytesIO(f.read()), sep="\t", usecols=["gvkey","year","icode100"])
fic["gvkey"] = fic["gvkey"].astype(str).str.zfill(6)
fic = fic[(fic["year"]>=2010)&(fic["year"]<=2016)]
# Map cal_yr_qtr -> year for industry lookup
merged["year"] = merged["cal_yr_qtr"] // 10
merged = merged.merge(fic, on=["gvkey","year"], how="left")
del fic

# ── 8. Filter to Compustat sample ───────────────────────────────────────
comp_filt = pd.read_parquet(ROOT/"inputs"/"comp_na_daily_all"/"comp_na_daily_all.parquet",
    columns=["gvkey","fyearq","fqtr","sic","curcdq","fic","atq","saleq"])
for c in ["atq","saleq"]:
    comp_filt[c] = pd.to_numeric(comp_filt[c], errors="coerce")
comp_filt = comp_filt[(comp_filt["fyearq"]>=2010)&(comp_filt["fyearq"]<=2015)]
comp_filt = comp_filt[comp_filt["fqtr"].isin([1,2,3,4])]
comp_filt = comp_filt[(comp_filt["curcdq"]=="USD")&(comp_filt["fic"]=="USA")]
comp_filt = comp_filt[(comp_filt["atq"]>0)&(comp_filt["saleq"]>0)]
csic = pd.to_numeric(comp_filt["sic"], errors="coerce")
comp_filt = comp_filt[~(csic.between(6000,6999)|csic.between(4900,4999))]
comp_filt = comp_filt[comp_filt["atq"]>10]
comp_filt["gvkey"] = comp_filt["gvkey"].astype(str).str.zfill(6)
sample_gvkeys = set(comp_filt["gvkey"].unique())
merged = merged[merged["gvkey"].isin(sample_gvkeys)]
print(f"Sample-filtered: {len(merged):,}")

# ── 9. Industry×Quarter demean ───────────────────────────────────────────
merged["ind_qtr"] = merged["icode100"].astype(str) + "_" + merged["cal_yr_qtr"].astype(str)
iq_mean = merged.groupby("ind_qtr")["FEY"].transform("mean")
merged["CEF_raw"] = merged["FEY"] - iq_mean

# Drop if industry missing
merged = merged.dropna(subset=["icode100"])

# ── 10. Winsorize at 1% ─────────────────────────────────────────────────
lo, hi = merged["CEF_raw"].quantile(0.01), merged["CEF_raw"].quantile(0.99)
merged["CEF"] = merged["CEF_raw"].clip(lo, hi)

# ── Report ───────────────────────────────────────────────────────────────
paper = {"N":42031, "mean":0.07, "SD":3.51, "p50":0.09}
our = {"N":len(merged), "mean":merged["CEF"].mean(),
       "SD":merged["CEF"].std(), "p50":merged["CEF"].median()}

print(f"\n--- H1: Industry-Quarter Demeaned Forward EPS Yield (pp) ---")
for k in ["N","mean","SD","p50"]:
    p, o = paper[k], our[k]
    pct = (o-p)/p*100 if p!=0 else float("nan")
    flag = " ***" if abs(pct)>20 else ""
    print(f"  {k}: ours={o:>10.4f}  paper={p:>10.4f}  d={pct:+.1f}%{flag}")

# Also test H2: calendar-quarter demean only
merged["CEF_qtr_raw"] = merged["FEY"] - merged.groupby("cal_yr_qtr")["FEY"].transform("mean")
lo2, hi2 = merged["CEF_qtr_raw"].quantile(0.01), merged["CEF_qtr_raw"].quantile(0.99)
merged["CEF_qtr"] = merged["CEF_qtr_raw"].clip(lo2, hi2)
our2 = {"N":len(merged), "mean":merged["CEF_qtr"].mean(),
        "SD":merged["CEF_qtr"].std(), "p50":merged["CEF_qtr"].median()}
print(f"\n--- H2: Calendar-Quarter Demeaned Forward EPS Yield (pp) ---")
for k in ["N","mean","SD","p50"]:
    p, o = paper[k], our2[k]
    pct = (o-p)/p*100 if p!=0 else float("nan")
    flag = " ***" if abs(pct)>20 else ""
    print(f"  {k}: ours={o:>10.4f}  paper={p:>10.4f}  d={pct:+.1f}%{flag}")
