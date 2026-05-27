"""Check CASH_T8 for one treated firm."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT / "outputs" / "campello_v2"
runs = sorted([d for d in OUT.iterdir() if d.is_dir() and (d/"beta_uk.parquet").exists()], reverse=True)
d = runs[0]

beta = pd.read_parquet(d/"beta_uk.parquet")
panel = pd.read_parquet(d/"variables_panel.parquet")
comp = pd.read_parquet(ROOT/"inputs"/"comp_na_daily_all"/"comp_na_daily_all.parquet",
    columns=["gvkey","datadate","atq","cheq"])
comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
comp["datadate"] = pd.to_datetime(comp["datadate"])
for c in ["atq","cheq"]:
    comp[c] = pd.to_numeric(comp[c], errors="coerce")
comp = comp.drop_duplicates(["gvkey","datadate"], keep="last")

nn = beta[beta["beta_uk"]>=0]
t2 = nn["beta_uk"].quantile(2/3)
top_gv = list(nn[nn["beta_uk"]>t2]["gvkey"].head(5))

for gv in top_gv:
    p = panel[panel["gvkey"]==gv].sort_values("cal_yr_qtr")
    c = comp[comp["gvkey"]==gv].sort_values("datadate")
    m = p.merge(c[["gvkey","datadate","cheq"]], on=["gvkey","datadate"], how="left")
    m = m.sort_values("cal_yr_qtr")
    m["atq_l1"] = m["atq"].shift(1)
    m["cheq_l1"] = m["cheq"].shift(1)
    den = m["atq_l1"] - m["cheq_l1"]
    m["T8"] = np.where((den.notna())&(den>0), m["cheq"]/den, np.nan)

    print(f"\n--- gvkey={gv} ---")
    for _, r in m[m["cal_yr_qtr"].isin([20153,20154,20163,20164])].iterrows():
        print(f"  Q={r['cal_yr_qtr']}:  CASH_T1={r['CASH']:.3f}  "
              f"atq={r['atq']:.0f}  cheq={r['cheq']:.0f}  "
              f"atq_l1={r['atq_l1']:.0f}  cheq_l1={r['cheq_l1']:.0f}  "
              f"denom={den.loc[r.name]:.0f}  CASH_T8={r['T8']:.3f}")
