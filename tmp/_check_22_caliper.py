"""PSM with multi-dim NN (use ALL covariates in NN, not just pscore)."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

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

nn = beta[beta["beta_uk"]>=0]
t1 = nn["beta_uk"].quantile(0.30); t2 = nn["beta_uk"].quantile(0.70)
t_gv_set = set(nn[nn["beta_uk"]>=t2]["gvkey"])
c_gv_set = set(nn[nn["beta_uk"]<t1].nlargest(360, "beta_uk")["gvkey"])
panel["treated"] = panel["gvkey"].isin(t_gv_set).astype(float)
panel["control_pool"] = panel["gvkey"].isin(c_gv_set).astype(float)
panel = panel[(panel["treated"]==1)|(panel["control_pool"]==1)].copy()

PRE_BREXIT_END = 20154
pre = panel[panel["cal_yr_qtr"]<=PRE_BREXIT_END].copy()
pre = pre.sort_values(["gvkey","cal_yr_qtr"])
pre["STOCK_RETURNS_lag1"] = pre.groupby("gvkey")["STOCK_RETURNS"].shift(1)
covars = ["STOCK_RETURNS_lag1","CONSENSUS_EPS","TOBIN_Q","CASH_FLOW","SALES_GROWTH","SIZE"]
firm_avg = pre.groupby("gvkey").agg({"treated":"max", **{c:"mean" for c in covars}}).reset_index()
firm_avg = firm_avg.dropna(subset=covars)

# CALIPER: only match within CONSENSUS_EPS strata
np.random.seed(42)
# Discretize CONSENSUS_EPS into bins for hard matching
firm_avg["ceps_bin"] = pd.qcut(firm_avg["CONSENSUS_EPS"], q=5, labels=False, duplicates='drop')

other_covars = ["STOCK_RETURNS_lag1","TOBIN_Q","CASH_FLOW","SALES_GROWTH","SIZE"]
sc = StandardScaler()
firm_avg_z = firm_avg.copy()
firm_avg_z[other_covars] = sc.fit_transform(firm_avg[other_covars].values)

m_t_list, m_c_list = [], []
for ceps_bin in sorted(firm_avg["ceps_bin"].dropna().unique()):
    sub = firm_avg_z[firm_avg_z["ceps_bin"]==ceps_bin]
    t_sub = sub[sub["treated"]==1]
    c_sub = sub[sub["treated"]==0]
    if len(t_sub)==0 or len(c_sub)==0:
        continue
    n_neigh = min(3, len(c_sub))
    nbrs = NearestNeighbors(n_neighbors=n_neigh, metric="euclidean")
    nbrs.fit(c_sub[other_covars].values)
    _, idx = nbrs.kneighbors(t_sub[other_covars].values)
    m_t_list.extend(t_sub["gvkey"].tolist())
    for row in idx:
        m_c_list.extend(c_sub.iloc[row]["gvkey"].tolist())

m_t = set(m_t_list); m_c = set(m_c_list)
print(f"Caliper-stratified matched: {len(m_t)}T / {len(m_c)}C unique")

# Stats
t_obs = pre[pre["gvkey"].isin(m_t)]
c_obs = pre[pre["gvkey"].isin(m_c)]

anchor = {"INVESTMENT":(0.020,0.012),"R&D":(0.030,0.016),"DIVESTITURES (×100)":(0.129,0.088),
    "CASH":(0.175,0.164),"NON_CASH_WORKING_CAPITAL":(0.058,0.086),"TOBIN_Q":(1.948,1.928),
    "CASH_FLOW":(0.016,0.032),"SIZE (Log Assets)":(6.677,7.205),"SALES_GROWTH":(0.195,0.105),
    "CONSENSUS_EPS":(0.023,0.025),"STOCK_RETURNS_lag1":(0.021,0.038)}
var_map = {"INVESTMENT":"INVESTMENT","R&D":"RD","DIVESTITURES (×100)":"DIVESTITURES",
    "CASH":"CASH","NON_CASH_WORKING_CAPITAL":"NWC","TOBIN_Q":"TOBIN_Q",
    "CASH_FLOW":"CASH_FLOW","SIZE (Log Assets)":"SIZE","SALES_GROWTH":"SALES_GROWTH",
    "CONSENSUS_EPS":"CONSENSUS_EPS","STOCK_RETURNS_lag1":"STOCK_RETURNS_lag1"}

n_pass = 0
print(f"\n{'Var':<28}{'TREATED':<25}{'CONTROL'}")
print("-"*76)
for label,(pt,pc) in anchor.items():
    col = var_map[label]; mult = 100 if "×100" in label else 1
    tm = t_obs[col].mean()*mult; cm = c_obs[col].mean()*mult
    def ok(m,p):
        d=abs(m-p)
        return d<0.05 if abs(p)<0.5 else d/abs(p)*100<15
    t_ok = ok(tm,pt); c_ok = ok(cm,pc)
    n_pass += int(t_ok) + int(c_ok)
    print(f"{label:<28} {tm:.3f}/{pt:.3f} {'✓' if t_ok else '✗':<10}  {cm:.3f}/{pc:.3f} {'✓' if c_ok else '✗'}")
print(f"\nTotal: {n_pass}/22")
