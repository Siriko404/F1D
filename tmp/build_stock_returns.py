"""STOCK_RETURNS = quarterly buy-and-hold return from CRSP daily RET.
Table 1 Panel A: N=67,226 mean=0.03 SD=0.24 p50=0.02"""
import pandas as pd, numpy as np
from pathlib import Path

ROOT = Path(".")
DSF_DIR = ROOT / "inputs" / "CRSP_DSF"
CCM_PATH = ROOT / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet"

# ── 1. Load CRSP daily returns (2009-2016, PERMNO+date+RET only) ────────
frames = []
for year in range(2009, 2017):
    for q in range(1, 5):
        f = DSF_DIR / f"CRSP_DSF_{year}_Q{q}.parquet"
        if f.exists():
            df = pd.read_parquet(f, columns=["PERMNO", "date", "RET"])
            frames.append(df)
crsp = pd.concat(frames, ignore_index=True)
del frames

crsp["date"] = pd.to_datetime(crsp["date"])
crsp["RET"] = pd.to_numeric(crsp["RET"], errors="coerce")

# Calendar quarter
crsp["cal_yr_qtr"] = crsp["date"].dt.year * 10 + crsp["date"].dt.quarter

# Quarterly buy-and-hold: ∏(1+RET) - 1 per (PERMNO, cal_yr_qtr)
crsp["one_plus_r"] = 1 + crsp["RET"].fillna(0)  # missing RET treated as zero return
bhr = crsp.groupby(["PERMNO", "cal_yr_qtr"])["one_plus_r"].prod() - 1
sret = bhr.reset_index()
sret.columns = ["PERMNO", "cal_yr_qtr", "STOCK_RETURNS_raw"]
del crsp, bhr

# ── 2. CCM link: PERMNO → gvkey ────────────────────────────────────────
ccm = pd.read_parquet(CCM_PATH, columns=["gvkey", "LPERMNO", "LINKDT", "LINKENDDT", "LINKTYPE", "LINKPRIM"])
ccm["gvkey"] = ccm["gvkey"].astype(str).str.zfill(6)
ccm = ccm[ccm["LINKTYPE"].isin(["LU", "LC"])]
ccm = ccm[ccm["LINKPRIM"].isin(["P", "C"])]
ccm["LINKDT"] = pd.to_datetime(ccm["LINKDT"], errors="coerce")
ccm["LINKENDDT"] = pd.to_datetime(ccm["LINKENDDT"], errors="coerce")
ccm["LINKENDDT"] = ccm["LINKENDDT"].fillna(pd.Timestamp("2099-12-31"))
ccm = ccm[(ccm["LINKENDDT"] >= pd.Timestamp("2010-01-01")) & (ccm["LINKDT"] <= pd.Timestamp("2016-12-31"))]
ccm["LPERMNO"] = pd.to_numeric(ccm["LPERMNO"], errors="coerce").astype("Int64")
ccm = ccm.dropna(subset=["LPERMNO"])

# Build quarter-end dates for merge range check
def qtr_end_date(yq):
    yr, qtr = divmod(yq, 10)
    month = qtr * 3
    return pd.Timestamp(year=int(yr), month=month, day=1) + pd.offsets.MonthEnd(0)

sret["qtr_end"] = sret["cal_yr_qtr"].apply(qtr_end_date)

# Merge PERMNO → gvkey: link valid if LINKDT <= qtr_end <= LINKENDDT
merged = sret.merge(ccm, left_on="PERMNO", right_on="LPERMNO")
merged = merged[(merged["LINKDT"] <= merged["qtr_end"]) & (merged["qtr_end"] <= merged["LINKENDDT"])]
merged = merged[["gvkey", "cal_yr_qtr", "STOCK_RETURNS_raw"]]
del ccm, sret

# Deduplicate: keep first link per (gvkey, cal_yr_qtr)
merged = merged.drop_duplicates(subset=["gvkey", "cal_yr_qtr"], keep="first")

# ── 3. Winsorize at 1% ──────────────────────────────────────────────────
lo, hi = merged["STOCK_RETURNS_raw"].quantile(0.01), merged["STOCK_RETURNS_raw"].quantile(0.99)
merged["STOCK_RETURNS"] = merged["STOCK_RETURNS_raw"].clip(lo, hi)

# Filter to 2010-2015 for Table 1
merged = merged[(merged["cal_yr_qtr"] >= 20101) & (merged["cal_yr_qtr"] <= 20154)]

# ── 4. Merge with Compustat filtered sample ──────────────────────────────
comp = pd.read_parquet("inputs/comp_na_daily_all/comp_na_daily_all.parquet",
                        columns=["gvkey","datadate","fyearq","fqtr","sic","curcdq","fic","atq","saleq"])
for c in ["atq","saleq"]:
    comp[c] = pd.to_numeric(comp[c], errors="coerce")
comp = comp[(comp["fyearq"]>=2010)&(comp["fyearq"]<=2015)]
comp = comp[comp["fqtr"].isin([1,2,3,4])]
comp = comp[(comp["curcdq"]=="USD")&(comp["fic"]=="USA")]
comp = comp[(comp["atq"]>0)&(comp["saleq"]>0)]
csic = pd.to_numeric(comp["sic"], errors="coerce")
comp = comp[~(csic.between(6000,6999)|csic.between(4900,4999))]
comp = comp[comp["atq"]>10]
comp["cal_yr_qtr"] = comp["fyearq"].astype(int)*10 + comp["fqtr"].astype(int)

# Merge: keep only gvkey-quarters in Compustat sample
merged["gvkey"] = merged["gvkey"].astype(str).str.zfill(6)
comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
final = merged.merge(comp[["gvkey","cal_yr_qtr"]].drop_duplicates(),
                      on=["gvkey","cal_yr_qtr"])
del comp, merged

# ── 5. Compare to paper ──────────────────────────────────────────────────
paper = {"N":67226, "mean":0.03, "SD":0.24, "p50":0.02}
our = {"N":len(final), "mean":final["STOCK_RETURNS"].mean(),
       "SD":final["STOCK_RETURNS"].std(), "p50":final["STOCK_RETURNS"].median()}

print("--- STOCK_RETURNS vs Paper (Table 1 Panel A) ---")
for k in ["N","mean","SD","p50"]:
    p, o = paper[k], our[k]
    pct = (o-p)/p*100 if p!=0 else float("nan")
    flag = " ***" if abs(pct)>15 else ""
    print(f"  {k:>6s}: ours={o:>10.4f}  paper={p:>10.4f}  d={pct:+.1f}%{flag}")
