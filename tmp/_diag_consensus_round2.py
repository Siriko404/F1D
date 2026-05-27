"""Round 2 diagnostic: try annual FPI values + all candidate fields/transforms."""
import zipfile, os
import numpy as np
import pandas as pd

ROOT = r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D"

with zipfile.ZipFile(f"{ROOT}/inputs/tr_ibes/ibes_statsum.zip") as z:
    name = z.namelist()[0]
    with z.open(name) as f:
        ibes = pd.read_csv(f, dtype={"TICKER": "str", "OFTIC": "str"}, low_memory=False)

ibes["STATPERS"] = pd.to_datetime(ibes["STATPERS"])
ibes["FPEDATS"] = pd.to_datetime(ibes["FPEDATS"])
ibes["FPI_n"] = pd.to_numeric(ibes["FPI"], errors="coerce")

# common filters
base = ibes[
    (ibes["MEASURE"] == "EPS")
    & (ibes["CURCODE"] == "USD")
    & (ibes["USFIRM"] == 1)
    & (ibes["FPEDATS"] >= "2010-01-01")
    & (ibes["FPEDATS"] <= "2017-03-31")
    & (ibes["STATPERS"] < ibes["FPEDATS"])
]

# Load sample-gvkey filter setup
comp_tic = pd.read_parquet(f"{ROOT}/inputs/comp_na_daily_all/comp_na_daily_all.parquet",
                            columns=["gvkey", "tic", "datadate"])
comp_tic["gvkey"] = comp_tic["gvkey"].astype(str).str.zfill(6)
comp_tic["datadate"] = pd.to_datetime(comp_tic["datadate"])
comp_tic = comp_tic[(comp_tic["datadate"] >= "2010-01-01") & (comp_tic["datadate"] <= "2017-03-31")]
comp_tic["cal_yr_qtr"] = (comp_tic["datadate"].dt.year * 10
                            + comp_tic["datadate"].dt.quarter).astype(np.int64)
comp_tic = comp_tic[["gvkey", "tic", "cal_yr_qtr"]].drop_duplicates()

runs = sorted([d for d in os.listdir(f"{ROOT}/outputs/campello_v2")
                if os.path.exists(f"{ROOT}/outputs/campello_v2/{d}/variables_panel.parquet")], reverse=True)
panel = pd.read_parquet(f"{ROOT}/outputs/campello_v2/{runs[0]}/variables_panel.parquet")
sample_gvkeys = set(panel["gvkey"].unique())

def process(df, label, value_col=None, transform=None):
    df = df.sort_values(["TICKER", "FPEDATS", "STATPERS"]).drop_duplicates(
        subset=["TICKER", "FPEDATS"], keep="last")
    yr = df["FPEDATS"].dt.year
    qtr = df["FPEDATS"].dt.quarter
    prev_qtr = np.where(qtr == 1, 4, qtr - 1)
    prev_yr = np.where(qtr == 1, yr - 1, yr)
    df = df.assign(cal_yr_qtr=(prev_yr * 10 + prev_qtr).astype(np.int64))
    m = df.merge(comp_tic, left_on=["OFTIC", "cal_yr_qtr"],
                  right_on=["tic", "cal_yr_qtr"], how="inner")
    m = m.drop_duplicates(subset=["gvkey", "cal_yr_qtr"], keep="first")
    m = m[m["gvkey"].isin(sample_gvkeys)]
    if transform:
        s = transform(m).dropna()
    else:
        s = pd.to_numeric(m[value_col], errors="coerce").dropna()
    if len(s) < 100:
        print(f"  {label:<55} N={len(s):,} (too few)")
        return
    lo, hi = s.quantile(0.01), s.quantile(0.99)
    s_w = s.clip(lo, hi)
    iqr = s_w.quantile(.75) - s_w.quantile(.25)
    print(f"  {label:<55} N={len(s_w):,}  mean={s_w.mean():.3f}  "
          f"sd={s_w.std():.3f}  median={s_w.median():.3f}  IQR={iqr:.3f}")

print(f"  {'ANCHOR (Table 1 Panel A CONSENSUS_EARNINGS_FORECAST):':<55} N=42,031  mean=0.07   sd=3.51   median=0.09   IQR=2.05")
print()

# Try ANNUAL forecasts at various horizons
for fpi_val, label in [(1, "FPI=1 annual FY+0"), (2, "FPI=2 annual FY+1"),
                       (3, "FPI=3 annual FY+2"), (4, "FPI=4 annual FY+3")]:
    d = base[(base["FISCALP"] == "ANN") & (base["FPI_n"] == fpi_val)]
    process(d, f"ANN {label} raw MEANEST", value_col="MEANEST")

print()
# Quarterly horizons
for fpi_val, label in [(6, "FPI=6 Q+1"), (7, "FPI=7 Q+2"), (8, "FPI=8 Q+3"), (9, "FPI=9 Q+4")]:
    d = base[(base["FISCALP"] == "QTR") & (base["FPI_n"] == fpi_val)]
    process(d, f"QTR {label} raw MEANEST", value_col="MEANEST")

print()
# Quarterly: try transformations on FPI=6
d6 = base[(base["FISCALP"] == "QTR") & (base["FPI_n"] == 6)]
process(d6, "Q+1 ACTUAL (realized EPS for Q+1)", value_col="ACTUAL")
process(d6, "Q+1 MEDEST",                       value_col="MEDEST")
process(d6, "Q+1 HIGHEST",                      value_col="HIGHEST")
process(d6, "Q+1 LOWEST",                       value_col="LOWEST")
process(d6, "Q+1 NUMEST (analysts)",            value_col="NUMEST")
process(d6, "Q+1 HIGHEST - LOWEST (range)",
        transform=lambda m: pd.to_numeric(m["HIGHEST"], errors="coerce")
                              - pd.to_numeric(m["LOWEST"], errors="coerce"))

print()
# Annual FPI=2 transformations (most likely if "1-quarter-ahead" = mis-labelled for "1-year-ahead")
d2 = base[(base["FISCALP"] == "ANN") & (base["FPI_n"] == 2)]
process(d2, "ANN FY+1 MEDEST",  value_col="MEDEST")
process(d2, "ANN FY+1 ACTUAL",  value_col="ACTUAL")
process(d2, "ANN FY+1 (ACTUAL - MEANEST)",
        transform=lambda m: pd.to_numeric(m["ACTUAL"], errors="coerce")
                              - pd.to_numeric(m["MEANEST"], errors="coerce"))
