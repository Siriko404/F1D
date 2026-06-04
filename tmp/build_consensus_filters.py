"""Test: does applying Table C1 filters 6+7 shift CONSENSUS_EPS distribution?"""
import pandas as pd, numpy as np, zipfile
from pathlib import Path

ROOT = Path(".")

# ── Load IBES, merge to gvkey (same pipeline as before) ────────────────
with zipfile.ZipFile(ROOT/"inputs"/"tr_ibes"/"ibes_statsum.zip") as z:
    with z.open(z.namelist()[0]) as f:
        ibes = pd.read_csv(f, usecols=["TICKER","CUSIP","OFTIC","STATPERS","MEASURE",
            "FISCALP","FPI","MEANEST","FPEDATS","USFIRM","CURCODE","ACTUAL","STDEV"],
            dtype={"TICKER":"str","CUSIP":"str","OFTIC":"str"}, low_memory=False)
ibes["FPI_n"] = pd.to_numeric(ibes["FPI"], errors="coerce")
ibes = ibes[(ibes["MEASURE"]=="EPS")&(ibes["FISCALP"]=="QTR")&(ibes["FPI_n"]==6)&(ibes["CURCODE"]=="USD")&(ibes["USFIRM"]==1)]
ibes["STATPERS"] = pd.to_datetime(ibes["STATPERS"]); ibes["FPEDATS"] = pd.to_datetime(ibes["FPEDATS"])
ibes = ibes[(ibes["FPEDATS"]>="2010-01-01")&(ibes["FPEDATS"]<="2017-03-31")]
ibes = ibes[ibes["STATPERS"] < ibes["FPEDATS"]]
ibes = ibes.sort_values(["TICKER","FPEDATS","STATPERS"])
ibes = ibes.drop_duplicates(subset=["TICKER","FPEDATS"], keep="last")
for c in ["ACTUAL","MEANEST","STDEV"]:
    ibes[f"{c}_n"] = pd.to_numeric(ibes[c], errors="coerce")
ibes["STDEV_n"] = ibes["STDEV_n"].where(ibes["STDEV_n"]>=0.01)
fpe_yq = ibes["FPEDATS"].dt.year*10 + ibes["FPEDATS"].dt.quarter
yr, qtr = fpe_yq//10, fpe_yq%10
prev_qtr = np.where(qtr==1, 4, qtr-1); prev_yr = np.where(qtr==1, yr-1, yr)
ibes["cal_yr_qtr"] = (prev_yr*10 + prev_qtr).astype(np.int64)

comp_map = pd.read_parquet(ROOT/"inputs"/"comp_na_daily_all"/"comp_na_daily_all.parquet",
    columns=["gvkey","tic","cusip","datadate"])
comp_map["gvkey"] = comp_map["gvkey"].astype(str).str.zfill(6)
comp_map["datadate"] = pd.to_datetime(comp_map["datadate"])
comp_map = comp_map[(comp_map["datadate"]>="2010-01-01")&(comp_map["datadate"]<="2017-03-31")]
comp_map["cal_yr_qtr"] = (comp_map["datadate"].dt.year*10+comp_map["datadate"].dt.quarter).astype(np.int64)
comp_map["cusip8"] = comp_map["cusip"].astype(str).str[:8]

ibes["CUSIP8"] = ibes["CUSIP"].astype(str).str[:8]
comp_cusip = comp_map[["gvkey","cusip8","cal_yr_qtr"]].drop_duplicates()
via_cusip = ibes.merge(comp_cusip, left_on=["CUSIP8","cal_yr_qtr"], right_on=["cusip8","cal_yr_qtr"], how="inner")
via_tic = ibes.merge(comp_map[["gvkey","tic","cal_yr_qtr"]].drop_duplicates(),
                      left_on=["OFTIC","cal_yr_qtr"], right_on=["tic","cal_yr_qtr"], how="inner")
merged = pd.concat([via_cusip[["gvkey","cal_yr_qtr","MEANEST_n","ACTUAL_n","STDEV_n"]],
                     via_tic[["gvkey","cal_yr_qtr","MEANEST_n","ACTUAL_n","STDEV_n"]]], ignore_index=True)
merged = merged.drop_duplicates(subset=["gvkey","cal_yr_qtr"], keep="first")
merged["gvkey"] = merged["gvkey"].astype(str).str.zfill(6)

# ── Load full Compustat with key variables ─────────────────────────────
comp = pd.read_parquet(ROOT/"inputs"/"comp_na_daily_all"/"comp_na_daily_all.parquet",
    columns=["gvkey","datadate","fyearq","fqtr","sic","curcdq","fic","atq","saleq",
             "capxy","oibdpq","cshoq","prccq","ceqq","txditcq"])
for c in ["atq","saleq","capxy","oibdpq","cshoq","prccq","ceqq","txditcq"]:
    comp[c] = pd.to_numeric(comp[c], errors="coerce")
comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)

# Filters 1-5
comp = comp[(comp["fyearq"]>=2010)&(comp["fyearq"]<=2015)]
comp = comp[comp["fqtr"].isin([1,2,3,4])]
comp = comp[(comp["curcdq"]=="USD")&(comp["fic"]=="USA")]
comp = comp[(comp["atq"]>0)&(comp["saleq"]>0)]
csic = pd.to_numeric(comp["sic"], errors="coerce")
comp = comp[~(csic.between(6000,6999)|csic.between(4900,4999))]
comp = comp[comp["atq"]>10]

print(f"Filters 1-5: N={len(comp):,} firms={comp['gvkey'].nunique():,}")

# ── Filter 6: drop missing key variables ───────────────────────────────
comp["cal_yr_qtr"] = comp["fyearq"].astype(int)*10 + comp["fqtr"].astype(int)

# Tobin's Q (needed for filter 6 check)
comp["txditcq"] = comp["txditcq"].fillna(0)
comp["has_q"] = comp[["cshoq","prccq","ceqq"]].notna().all(axis=1)

# Sales growth (need YoY)
comp = comp.sort_values(["gvkey","datadate"])
comp["saleq_lag4"] = comp.groupby("gvkey")["saleq"].shift(4)
comp["has_sg"] = comp["saleq_lag4"].notna()

key_vars = ["capxy","atq","oibdpq"]
comp["key_ok"] = comp[key_vars].notna().all(axis=1) & comp["has_q"] & comp["has_sg"]

comp_f6 = comp[comp["key_ok"]].copy()
print(f"After F6 (missing key vars): N={len(comp_f6):,} firms={comp_f6['gvkey'].nunique():,}")

# ── Filter 7: longest consecutive run >= 12 quarters ────────────────────
def keep_longest_run(df):
    df = df.sort_values(["gvkey","cal_yr_qtr"])
    result = []
    for gvkey, grp in df.groupby("gvkey"):
        grp = grp.sort_values("cal_yr_qtr")
        grp["gap"] = grp["cal_yr_qtr"].diff().fillna(1)
        # Mark run breaks (gap > 1 quarter, handling year boundary)
        grp["new_run"] = (grp["gap"] > 1) & (grp["gap"] != 1)  # not perfect but quick
        # Simpler: find longest contiguous stretch
        runs = []
        current = []
        for _, row in grp.iterrows():
            if not current:
                current = [row.name]
            else:
                prev_q = grp.loc[current[-1], "cal_yr_qtr"]
                this_q = row["cal_yr_qtr"]
                # consecutive if (yr*10+qtr) diff = 1 (within year) or 10-4+1=7 (year boundary, Q4->Q1)
                expected = prev_q + 1
                if prev_q % 10 == 4:
                    expected = (prev_q // 10 + 1) * 10 + 1
                if this_q == expected:
                    current.append(row.name)
                else:
                    runs.append(current)
                    current = [row.name]
        runs.append(current)
        if runs:
            longest = max(runs, key=len)
            if len(longest) >= 12:
                result.append(grp.loc[longest])
    if result:
        return pd.concat(result, ignore_index=True)
    return pd.DataFrame(columns=df.columns)

comp_f7 = keep_longest_run(comp_f6)
print(f"After F7 (consecutive >=12q): N={len(comp_f7):,} firms={comp_f7['gvkey'].nunique():,}")

# ── Merge CONSENSUS_EPS and check distribution at each filter stage ─────
for label, comp_stage in [("F5", comp), ("F6", comp_f6), ("F7", comp_f7)]:
    sample_gvkeys = set(comp_stage["gvkey"].unique())
    m = merged[merged["gvkey"].isin(sample_gvkeys)].copy()

    # SUE construction
    m["SUE"] = (m["ACTUAL_n"] - m["MEANEST_n"]) / m["STDEV_n"]
    m["SUE"] = m["SUE"].replace([np.inf,-np.inf], np.nan)

    # Winsorize per quarter
    for q, idx in m.groupby("cal_yr_qtr").groups.items():
        v = m.loc[idx, "SUE"]
        if v.notna().sum() < 10: continue
        lo, hi = v.quantile(0.01), v.quantile(0.99)
        m.loc[idx, "SUE_w"] = v.clip(lo, hi)

    # Demean per quarter
    for q, idx in m.groupby("cal_yr_qtr").groups.items():
        v = m.loc[idx, "SUE_w"]
        if v.notna().sum() < 10: continue
        m.loc[idx, "CEF"] = v - v.mean()

    s = m["CEF"].dropna()
    print(f"\n{label}: N={len(s):,} mean={s.mean():.4f} SD={s.std():.4f} p50={s.median():.4f}")
    if label in ["F6","F7"]:
        # Also try: no demeaning
        s2 = m["SUE_w"].dropna()
        print(f"  {label} (no demean): N={len(s2):,} mean={s2.mean():.4f} SD={s2.std():.4f} p50={s2.median():.4f}")

print(f"\nPaper: N=42031 mean=0.07 SD=3.51 p50=0.09")
