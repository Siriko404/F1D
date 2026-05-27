"""Final DiD test matrix:
- Spec A: Linear β, FULL panel (paper Table 8 col 1 setup)
- Spec B: Binary β tercile, FULL panel
- Spec C: Linear β, 8Q window
- Spec D: Binary β, MATCHED sample (Table C.3 PSM)
"""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from linearmodels.panel import PanelOLS

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT / "outputs" / "campello_v2"
beta_dir = OUT / "20260527_010458"

panel = pd.read_parquet(beta_dir / "variables_panel.parquet")
beta = pd.read_parquet(beta_dir / "beta_uk.parquet")
sret = pd.read_parquet(beta_dir / "stock_returns.parquet")
ceps = pd.read_parquet(beta_dir / "consensus_eps.parquet")

panel = panel.merge(sret, on=["gvkey","cal_yr_qtr"], how="left")
panel = panel.merge(ceps, on=["gvkey","cal_yr_qtr"], how="left")
panel = panel.merge(beta[["gvkey","beta_uk"]], on="gvkey", how="left")

# Treatment
nonneg = beta[beta["beta_uk"]>=0]
t1 = nonneg["beta_uk"].quantile(1/3); t2 = nonneg["beta_uk"].quantile(2/3)
panel["HIGH_UK"] = (panel["beta_uk"]>t2).astype(float)
panel["LOW_UK"] = ((panel["beta_uk"]>=0)&(panel["beta_uk"]<t1)).astype(float)

POST_Q = [20163,20164]
panel["POST"] = panel["cal_yr_qtr"].isin(POST_Q).astype(float)
panel["POST_BETA"] = panel["POST"] * panel["beta_uk"]
panel["TREAT_POST"] = panel["HIGH_UK"] * panel["POST"]

# Lag controls
panel = panel.sort_values(["gvkey","cal_yr_qtr"])
ctrl = ["STOCK_RETURNS","TOBIN_Q","CASH_FLOW","SIZE","SALES_GROWTH","CONSENSUS_EPS"]
for c in ctrl:
    panel[f"{c}_lag1"] = panel.groupby("gvkey")[c].shift(1)

# CASH_T8
comp = pd.read_parquet(ROOT/"inputs"/"comp_na_daily_all"/"comp_na_daily_all.parquet",
                       columns=["gvkey","datadate","atq","cheq"])
comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
comp["datadate"] = pd.to_datetime(comp["datadate"])
for c in ["atq","cheq"]: comp[c] = pd.to_numeric(comp[c], errors="coerce")
comp = comp.drop_duplicates(["gvkey","datadate"], keep="last")
panel = panel.merge(comp[["gvkey","datadate","cheq"]], on=["gvkey","datadate"], how="left")
panel = panel.sort_values(["gvkey","cal_yr_qtr"])
panel["atq_l1"] = panel.groupby("gvkey")["atq"].shift(1)
panel["cheq_l1"] = panel.groupby("gvkey")["cheq"].shift(1)
denom = panel["atq_l1"]-panel["cheq_l1"]
panel["CASH_T8"] = np.where((denom.notna())&(denom>0), panel["cheq"]/denom, np.nan)
for q, idx in panel.groupby("cal_yr_qtr").groups.items():
    v = panel.loc[idx,"CASH_T8"]
    if v.notna().sum()<10: continue
    lo, hi = v.quantile(0.01), v.quantile(0.99); panel.loc[idx,"CASH_T8"] = v.clip(lo, hi)

# Build PSM matched sample
pre = panel[(panel["cal_yr_qtr"]<=20154) & ((panel["HIGH_UK"]==1)|(panel["LOW_UK"]==1))].copy()
pre["treated"] = pre["HIGH_UK"]
firm_avg = pre.groupby("gvkey").agg({"treated":"max", **{c:"mean" for c in ctrl[:-1]}, "STOCK_RETURNS":"mean"}).reset_index()
covars = ["STOCK_RETURNS","TOBIN_Q","CASH_FLOW","SIZE","SALES_GROWTH"]
# Add CONSENSUS_EPS
firm_avg_ceps = pre.groupby("gvkey")["CONSENSUS_EPS"].mean().reset_index()
firm_avg = firm_avg.merge(firm_avg_ceps, on="gvkey")
covars = covars + ["CONSENSUS_EPS"]
firm_avg = firm_avg.dropna(subset=covars)
np.random.seed(42)
sc = StandardScaler(); Xz = sc.fit_transform(firm_avg[covars].values)
lr = LogisticRegression(max_iter=1000, random_state=42); lr.fit(Xz, firm_avg["treated"].astype(int))
firm_avg["pscore"] = lr.predict_proba(Xz)[:,1]
t_i = firm_avg.index[firm_avg["treated"]==1].tolist()
c_i = firm_avg.index[firm_avg["treated"]==0].tolist()
nbrs = NearestNeighbors(n_neighbors=3); nbrs.fit(firm_avg.loc[c_i,["pscore"]])
_, idx_c = nbrs.kneighbors(firm_avg.loc[t_i,["pscore"]])
matched_t = set(firm_avg.loc[t_i,"gvkey"])
matched_c = set(firm_avg.loc[[c_i[i] for row in idx_c for i in row],"gvkey"])

specs = [
    ("A: Linear β,    FULL panel", panel, "POST_BETA", None),
    ("B: Binary β,    FULL panel (T/C tercile)", panel[(panel["HIGH_UK"]==1)|(panel["LOW_UK"]==1)], "TREAT_POST", None),
    ("C: Linear β,    8Q (2015 vs 2016)", panel[panel["cal_yr_qtr"].between(20151, 20164)], "POST_BETA", None),
    ("D: Binary β,    MATCHED PSM, 8Q window", panel[(panel["cal_yr_qtr"].between(20151,20164))&(panel["gvkey"].isin(matched_t|matched_c))], "TREAT_POST", None),
    ("E: Binary β,    MATCHED PSM, FULL panel", panel[(panel["HIGH_UK"]==1)|(panel["LOW_UK"]==1)][lambda x: x["gvkey"].isin(matched_t|matched_c)], "TREAT_POST", None),
]

print(f"{'Spec':<48}{'CASH_T1':<35}{'CASH_T8':<35}")
print("="*120)
for name, sub_p, treat_col, _ in specs:
    line = f"{name:<48}"
    for dv in ["CASH","CASH_T8"]:
        sub = sub_p.dropna(subset=[dv, treat_col]+[f"{c}_lag1" for c in ctrl]).set_index(["gvkey","cal_yr_qtr"])
        exog = sub[[treat_col]+[f"{c}_lag1" for c in ctrl]]
        try:
            mod = PanelOLS(sub[dv], exog, entity_effects=True, time_effects=True)
            res = mod.fit(cov_type="clustered", cluster_entity=True, cluster_time=True)
            b=res.params[treat_col]; p=res.pvalues[treat_col]
            sig="***" if p<0.01 else "**" if p<0.05 else "*" if p<0.10 else ""
            line += f"δ={b:+.4f}{sig:<3} p={p:.3f} N={res.nobs:<6,}  "
        except Exception as e:
            line += f"FAIL                                "
    print(line)
print(f"\nPaper Table 8 col 1 CASH:  δ=+0.231*** N=17,170")
