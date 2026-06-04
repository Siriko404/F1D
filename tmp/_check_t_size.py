"""Compare SIZE distribution of our T(β>0.68) firms vs paper anchor mean=6.677."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
bdir = ROOT/"outputs"/"campello_v2"/"20260527_023553"

beta = pd.read_parquet(bdir/"beta_uk.parquet")
panel = pd.read_parquet(bdir/"variables_panel.parquet")

t_gv = set(beta.loc[beta["beta_uk"]>0.68,"gvkey"])
c_gv = set(beta.loc[(beta["beta_uk"]>=0)&(beta["beta_uk"]<0.28),"gvkey"])
print(f"T(β>0.68)={len(t_gv):,}  C(0≤β<0.28)={len(c_gv):,}  (paper 449/360)")

# Pre-Brexit mean SIZE per firm
pre = panel[panel["cal_yr_qtr"]<=20154].copy()
size_by_firm = pre.groupby("gvkey")["SIZE"].mean().reset_index()
size_by_firm["group"] = np.where(size_by_firm["gvkey"].isin(t_gv),"T",
                         np.where(size_by_firm["gvkey"].isin(c_gv),"C","X"))
print(f"\nSIZE (mean log assets) by group:")
for g, gr in size_by_firm[size_by_firm["group"]!="X"].groupby("group"):
    print(f"  {g}: N={len(gr):,}  mean={gr['SIZE'].mean():.3f}  median={gr['SIZE'].median():.3f}  p10={gr['SIZE'].quantile(0.10):.3f}  p90={gr['SIZE'].quantile(0.90):.3f}")
print(f"  paper anchor: T mean=6.677, C mean=7.205")

# Check: what if we trim T to "large" firms only (size >= 5)?
print(f"\nSize-cut diagnostic — what % of our T meets paper-size threshold?")
for sz_min in [3.0, 4.0, 5.0, 5.5, 6.0]:
    n_t = ((size_by_firm["group"]=="T") & (size_by_firm["SIZE"]>=sz_min)).sum()
    n_c = ((size_by_firm["group"]=="C") & (size_by_firm["SIZE"]>=sz_min)).sum()
    print(f"  size_min={sz_min:>4.1f}: T_left={n_t:,}  C_left={n_c:,}")

# Show actual top by β + their sizes
comp_n = pd.read_parquet(ROOT/"inputs"/"comp_na_daily_all"/"comp_na_daily_all.parquet",
                          columns=["gvkey","conm"])
comp_n["gvkey"] = comp_n["gvkey"].astype(str).str.zfill(6)
comp_n = comp_n.drop_duplicates(["gvkey"], keep="last")
merged = beta.merge(comp_n, on="gvkey").merge(size_by_firm[["gvkey","SIZE"]], on="gvkey", how="left")
merged = merged.sort_values("beta_uk", ascending=False)
print(f"\nTOP 20 by β with SIZE:")
print(merged[["conm","beta_uk","SIZE"]].head(20).to_string(index=False))
