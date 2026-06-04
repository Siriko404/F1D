"""CONSENSUS_EPS — test all construction variants with correct pipeline.
Table 1 Panel A: N=42031 mean=0.07 SD=3.51 p50=0.09"""
import pandas as pd, numpy as np, zipfile
from pathlib import Path

ROOT = Path(".")

# ── 1. IBES stats loaded + filtered ─────────────────────────────────────
with zipfile.ZipFile(ROOT/"inputs"/"tr_ibes"/"ibes_statsum.zip") as z:
    with z.open(z.namelist()[0]) as f:
        ibes = pd.read_csv(f, usecols=["TICKER","CUSIP","OFTIC","STATPERS","MEASURE",
            "FISCALP","FPI","MEANEST","FPEDATS","USFIRM","CURCODE","ACTUAL","STDEV"],
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

for c in ["ACTUAL","MEANEST","STDEV"]:
    ibes[f"{c}_n"] = pd.to_numeric(ibes[c], errors="coerce")
ibes["STDEV_n"] = ibes["STDEV_n"].where(ibes["STDEV_n"]>=0.01)  # drop near-zero dispersion

# ── 2. cal_yr_qtr (forecast for Q+1, attach to Q) ──────────────────────
fpe_yq = ibes["FPEDATS"].dt.year*10 + ibes["FPEDATS"].dt.quarter
yr, qtr = fpe_yq//10, fpe_yq%10
prev_qtr = np.where(qtr==1, 4, qtr-1)
prev_yr = np.where(qtr==1, yr-1, yr)
ibes["cal_yr_qtr"] = (prev_yr*10 + prev_qtr).astype(np.int64)

# ── 3. Map to gvkey ─────────────────────────────────────────────────────
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
merged = pd.concat([via_cusip[["gvkey","cal_yr_qtr","MEANEST_n","ACTUAL_n","STDEV_n"]],
                     via_tic[["gvkey","cal_yr_qtr","MEANEST_n","ACTUAL_n","STDEV_n"]]],
                    ignore_index=True)
merged = merged.drop_duplicates(subset=["gvkey","cal_yr_qtr"], keep="first")
print(f"IBES mapped: {len(merged):,}")

# ── 4. Filter to Compustat sample gvkeys ────────────────────────────────
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

# ── 5. Test variants ─────────────────────────────────────────────────────
def winsor_by_qtr(df, col, lo_pct=0.01, hi_pct=0.99):
    """Winsorize per cal_yr_qtr"""
    result = pd.Series(np.nan, index=df.index, dtype="float64")
    for q, idx in df.groupby("cal_yr_qtr").groups.items():
        v = df.loc[idx, col]
        if v.notna().sum() < 10:
            result.loc[idx] = v
            continue
        lo, hi = v.quantile(lo_pct), v.quantile(hi_pct)
        result.loc[idx] = v.clip(lo, hi)
    return result

def report(label, series):
    s = series.dropna()
    print(f"  {label:40s}: N={len(s):>6,}  mean={s.mean():>8.4f}  SD={s.std():>8.4f}  p50={s.median():>8.4f}")

print("\nPaper: N=42031 mean=0.07 SD=3.51 p50=0.09\n")

# V1: raw MEANEST (forecast level, no scaling)
merged["V1"] = merged["MEANEST_n"]
report("V1 raw MEANEST", merged["V1"])

# V2: raw MEANEST, |value|<100, winsorized
merged["V2"] = np.where(merged["MEANEST_n"].abs()<100, merged["MEANEST_n"], np.nan)
merged["V2_w"] = winsor_by_qtr(merged.dropna(subset=["V2"]), "V2")
report("V2 |MEANEST|<100, qtr-winsor", merged["V2_w"])

# V3: SUE = (ACTUAL - MEANEST) / STDEV, winsorized, cross-sectional demean
merged["SUE"] = (merged["ACTUAL_n"] - merged["MEANEST_n"]) / merged["STDEV_n"]
merged["SUE"] = merged["SUE"].replace([np.inf,-np.inf], np.nan)
merged["SUE_w"] = winsor_by_qtr(merged.dropna(subset=["SUE"]), "SUE")
# Demean
merged["SUE_wd"] = np.nan
for q, idx in merged.groupby("cal_yr_qtr").groups.items():
    v = merged.loc[idx, "SUE_w"]
    if v.notna().sum() < 10:
        continue
    merged.loc[idx, "SUE_wd"] = v - v.mean()
report("V3 SUE winsor+demean", merged["SUE_wd"])

# V4: SUE winsor only, no demean
report("V4 SUE winsor only", merged["SUE_w"])

# V5: MEANEST/STDEV (forecast scaled by precision), winsorized
merged["MEANEST_over_STDEV"] = merged["MEANEST_n"] / merged["STDEV_n"]
merged["MEANEST_over_STDEV"] = merged["MEANEST_over_STDEV"].replace([np.inf,-np.inf], np.nan)
merged["MOS_w"] = winsor_by_qtr(merged.dropna(subset=["MEANEST_over_STDEV"]), "MEANEST_over_STDEV")
report("V5 MEANEST/STDEV winsor", merged["MOS_w"])

# V6: MEANEST/STDEV, |raw MEANEST|<100, winsorized
merged["MOS2"] = np.where(merged["MEANEST_n"].abs()<100,
    merged["MEANEST_n"]/merged["STDEV_n"], np.nan)
merged["MOS2"] = merged["MOS2"].replace([np.inf,-np.inf], np.nan)
merged["MOS2_w"] = winsor_by_qtr(merged.dropna(subset=["MOS2"]), "MOS2")
report("V6 |M|<100, M/STDEV winsor", merged["MOS2_w"])

# V7: Same as V6 but + cross-sectional demean
merged["MOS2_wd"] = np.nan
for q, idx in merged.groupby("cal_yr_qtr").groups.items():
    v = merged.loc[idx, "MOS2_w"]
    if v.notna().sum() < 10:
        continue
    merged.loc[idx, "MOS2_wd"] = v - v.mean()
report("V7 |M|<100, M/STDEV winsor+demean", merged["MOS2_wd"])
