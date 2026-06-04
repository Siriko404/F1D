"""CONSENSUS_EPS — test standardization vs winsorization order.
Table 1 Panel A: N=42,031 mean=0.07 SD=3.51 p50=0.09"""
import pandas as pd, numpy as np
from pathlib import Path
import zipfile

ROOT = Path(".")

# ── 1. Load I/B/E/S statsum ─────────────────────────────────────────────
zpath = ROOT / "inputs" / "tr_ibes" / "ibes_statsum.zip"
with zipfile.ZipFile(zpath) as z:
    with z.open(z.namelist()[0]) as f:
        ibes = pd.read_csv(f,
            usecols=["TICKER","CUSIP","OFTIC","STATPERS","MEASURE",
                     "FISCALP","FPI","MEANEST","FPEDATS","USFIRM",
                     "CURCODE","ACTUAL","STDEV"],
            dtype={"TICKER":"str","CUSIP":"str","OFTIC":"str"}, low_memory=False)

ibes["FPI_n"] = pd.to_numeric(ibes["FPI"], errors="coerce")
ibes = ibes[(ibes["MEASURE"]=="EPS") & (ibes["FISCALP"]=="QTR") & (ibes["FPI_n"]==6)
            & (ibes["CURCODE"]=="USD") & (ibes["USFIRM"]==1)]
ibes["STATPERS"] = pd.to_datetime(ibes["STATPERS"])
ibes["FPEDATS"] = pd.to_datetime(ibes["FPEDATS"])
ibes = ibes[(ibes["FPEDATS"]>="2010-01-01") & (ibes["FPEDATS"]<="2017-03-31")]
ibes = ibes[ibes["STATPERS"] < ibes["FPEDATS"]]
ibes = ibes.sort_values(["TICKER","FPEDATS","STATPERS"])
ibes = ibes.drop_duplicates(subset=["TICKER","FPEDATS"], keep="last")

for c in ["ACTUAL","MEANEST","STDEV"]:
    ibes[f"{c}_n"] = pd.to_numeric(ibes[c], errors="coerce")
ibes.loc[ibes["STDEV_n"] < 0.01, "STDEV_n"] = np.nan

# SUE = (ACTUAL - MEANEST) / STDEV
ibes["SUE"] = (ibes["ACTUAL_n"] - ibes["MEANEST_n"]) / ibes["STDEV_n"]
ibes["SUE"] = ibes["SUE"].replace([np.inf, -np.inf], np.nan)

# ── 2. cal_yr_qtr of the forecast (1Q ahead -> map to prior quarter) ─────
fpe_yq = ibes["FPEDATS"].dt.year*10 + ibes["FPEDATS"].dt.quarter
yr, qtr = fpe_yq//10, fpe_yq%10
prev_qtr = np.where(qtr==1, 4, qtr-1)
prev_yr = np.where(qtr==1, yr-1, yr)
ibes["cal_yr_qtr"] = (prev_yr*10 + prev_qtr).astype(np.int64)

# ── 3. Map to gvkey via CUSIP-8 ─────────────────────────────────────────
comp_map = pd.read_parquet(ROOT/"inputs"/"comp_na_daily_all"/"comp_na_daily_all.parquet",
                            columns=["gvkey","tic","cusip","datadate"])
comp_map["gvkey"] = comp_map["gvkey"].astype(str).str.zfill(6)
comp_map["datadate"] = pd.to_datetime(comp_map["datadate"])
comp_map = comp_map[(comp_map["datadate"]>="2010-01-01")&(comp_map["datadate"]<="2017-03-31")]
comp_map["cal_yr_qtr"] = (comp_map["datadate"].dt.year*10+comp_map["datadate"].dt.quarter).astype(np.int64)
comp_map["cusip8"] = comp_map["cusip"].astype(str).str[:8]

ibes["CUSIP8"] = ibes["CUSIP"].astype(str).str[:8]
comp_cusip = comp_map[["gvkey","cusip8","cal_yr_qtr"]].drop_duplicates()
merged = ibes.merge(comp_cusip, left_on=["CUSIP8","cal_yr_qtr"],
                     right_on=["cusip8","cal_yr_qtr"], how="inner")
comp_tic = comp_map[["gvkey","tic","cal_yr_qtr"]].drop_duplicates()
via_tic = ibes.merge(comp_tic, left_on=["OFTIC","cal_yr_qtr"],
                      right_on=["tic","cal_yr_qtr"], how="inner")
merged = pd.concat([merged[["gvkey","cal_yr_qtr","SUE"]],
                     via_tic[["gvkey","cal_yr_qtr","SUE"]]], ignore_index=True)
merged = merged.drop_duplicates(subset=["gvkey","cal_yr_qtr"], keep="first")
print(f"Mapped obs: {len(merged):,}")

# ── 4. Apply Compustat filters to get sample gvkeys ──────────────────────
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
print(f"Sample-filtered obs: {len(merged):,}")

# ── 5. Test variants ─────────────────────────────────────────────────────
def report(label, series):
    s = series.dropna()
    print(f"\n{label}:")
    print(f"  N={len(s):,} mean={s.mean():.4f} SD={s.std():.4f} p50={s.median():.4f}")
    print(f"  Paper: N=42031 mean=0.07 SD=3.51 p50=0.09")

# Variant A: winsorize THEN demean (existing code sequence)
sue = merged["SUE"].copy()
lo, hi = sue.quantile(0.01), sue.quantile(0.99)
sue_w = sue.clip(lo, hi)
# per-quarter demean (skip groups with <10 obs)
for q, idx in merged.groupby("cal_yr_qtr").groups.items():
    if len(idx) < 10:
        continue
    v = sue_w.loc[idx]
    sue_w.loc[idx] = v - v.mean()
merged["A_winsor_then_demean"] = sue_w
report("A: winsorize(1%) -> per-qtr demean", merged["A_winsor_then_demean"])

# Variant B: demean THEN winsorize (user's hypothesis)
sue2 = merged["SUE"].copy()
for q, idx in merged.groupby("cal_yr_qtr").groups.items():
    if len(idx) < 10:
        continue
    v = sue2.loc[idx]
    sue2.loc[idx] = v - v.mean()
lo2, hi2 = sue2.quantile(0.01), sue2.quantile(0.99)
merged["B_demean_then_winsor"] = sue2.clip(lo2, hi2)
report("B: per-qtr demean -> winsorize(1%)", merged["B_demean_then_winsor"])

# Variant C: winsorize only, no demean
merged["C_winsor_only"] = sue.clip(lo, hi)
report("C: winsorize(1%) only, no demean", merged["C_winsor_only"])

# Variant D: raw MEANEST/STDEV (forecast level, not error) - skip (merge bug)

# Variant E: raw SUE, no processing
report("E: raw SUE, no winsor/no demean", merged["SUE"])
