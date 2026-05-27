"""Bundle latest files to VFTSE β dir, run PSM."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import shutil

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT / "outputs" / "campello_v2"

def latest(fname):
    runs = sorted([d for d in OUT.iterdir() if d.is_dir() and (d / fname).exists()], reverse=True)
    return runs[0] / fname

# All files co-located in beta_uk dir
beta_dir = latest("beta_uk.parquet").parent
for fn in ["variables_panel.parquet", "stock_returns.parquet", "consensus_eps.parquet"]:
    src = latest(fn)
    if src.parent != beta_dir:
        shutil.copy(src, beta_dir / fn)
        print(f"Copied {fn} -> {beta_dir / fn}")
    else:
        print(f"Already co-located: {fn}")

# Now run PSM using the bundled dir
# Build a temp PSM that reads from the specific dir
import logging
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

PRE_BREXIT_END = 20154

panel = pd.read_parquet(beta_dir / "variables_panel.parquet")
beta = pd.read_parquet(beta_dir / "beta_uk.parquet")[["gvkey", "beta_uk"]]
sret = pd.read_parquet(beta_dir / "stock_returns.parquet")
ceps = pd.read_parquet(beta_dir / "consensus_eps.parquet")

panel = panel.merge(sret, on=["gvkey", "cal_yr_qtr"], how="left")
panel = panel.merge(ceps, on=["gvkey", "cal_yr_qtr"], how="left")
panel = panel.merge(beta, on="gvkey", how="left")

nonneg = beta[beta["beta_uk"] >= 0]
t1 = nonneg["beta_uk"].quantile(1/3)
t2 = nonneg["beta_uk"].quantile(2/3)
logger.info("terciles: t1=%.4f t2=%.4f", t1, t2)

panel["treated"] = (panel["beta_uk"] > t2).astype(float)
panel["control_pool"] = ((panel["beta_uk"] >= 0) & (panel["beta_uk"] < t1)).astype(float)
panel = panel[(panel["treated"] == 1) | (panel["control_pool"] == 1)].copy()

n_t = panel[panel["treated"]==1]["gvkey"].nunique()
n_c = panel[panel["control_pool"]==1]["gvkey"].nunique()
logger.info("Treated firms: %s | Control: %s", n_t, n_c)

pre = panel[panel["cal_yr_qtr"] <= PRE_BREXIT_END].copy()
pre = pre.sort_values(["gvkey", "cal_yr_qtr"])
pre["STOCK_RETURNS_lag1"] = pre.groupby("gvkey")["STOCK_RETURNS"].shift(1)

covariates = ["STOCK_RETURNS_lag1", "CONSENSUS_EPS", "TOBIN_Q", "CASH_FLOW", "SALES_GROWTH", "SIZE"]
firm_avg = pre.groupby("gvkey").agg({"treated":"max","sic":"first",
    **{c:"mean" for c in covariates}}).reset_index()
firm_avg = firm_avg.dropna(subset=covariates)
logger.info("Firms with all covariates: %s", len(firm_avg))

X = firm_avg[covariates].values
y = firm_avg["treated"].values.astype(int)
scaler = StandardScaler()
X_z = scaler.fit_transform(X)
logreg = LogisticRegression(max_iter=1000)
logreg.fit(X_z, y)
firm_avg["pscore"] = logreg.predict_proba(X_z)[:, 1]

treated_idx = firm_avg.index[firm_avg["treated"] == 1].tolist()
control_idx = firm_avg.index[firm_avg["treated"] == 0].tolist()
nbrs = NearestNeighbors(n_neighbors=min(3, len(control_idx)))
nbrs.fit(firm_avg.loc[control_idx, ["pscore"]].values)
dist, idx_in_ctrl = nbrs.kneighbors(firm_avg.loc[treated_idx, ["pscore"]].values)

matched_t_gv = firm_avg.loc[treated_idx, "gvkey"].values
matched_c_gv = firm_avg.loc[[control_idx[i] for row in idx_in_ctrl for i in row], "gvkey"].values
logger.info("Matched: %s treated → %s control matches", len(matched_t_gv), len(matched_c_gv))

# Compare
pre = panel[panel["cal_yr_qtr"] <= PRE_BREXIT_END].copy()
pre["STOCK_RETURNS_lag1"] = pre.sort_values(["gvkey","cal_yr_qtr"]).groupby("gvkey")["STOCK_RETURNS"].shift(1)

treated_obs = pre[pre["gvkey"].isin(set(matched_t_gv))]
control_obs = pre[pre["gvkey"].isin(set(matched_c_gv))]

anchor = {
    "INVESTMENT": (0.020, 0.012), "R&D": (0.030, 0.016),
    "DIVESTITURES (×100)": (0.129, 0.088), "CASH": (0.175, 0.164),
    "NON_CASH_WORKING_CAPITAL": (0.058, 0.086), "TOBIN_Q": (1.948, 1.928),
    "CASH_FLOW": (0.016, 0.032), "SIZE (Log Assets)": (6.677, 7.205),
    "SALES_GROWTH": (0.195, 0.105), "CONSENSUS_EPS": (0.023, 0.025),
    "STOCK_RETURNS_lag1": (0.021, 0.038),
}
var_map = {"INVESTMENT":"INVESTMENT","R&D":"RD","DIVESTITURES (×100)":"DIVESTITURES",
    "CASH":"CASH","NON_CASH_WORKING_CAPITAL":"NWC","TOBIN_Q":"TOBIN_Q",
    "CASH_FLOW":"CASH_FLOW","SIZE (Log Assets)":"SIZE","SALES_GROWTH":"SALES_GROWTH",
    "CONSENSUS_EPS":"CONSENSUS_EPS","STOCK_RETURNS_lag1":"STOCK_RETURNS_lag1"}

print(f"\n=== Table C.2 Panel A — Matched Sample ===")
print(f"{'Variable':<28}{'TREATED (mine/paper)':<28}{'CONTROL (mine/paper)':<28}")
print("-" * 84)
for label, (paper_t, paper_c) in anchor.items():
    col = var_map.get(label, label)
    if col not in treated_obs.columns:
        continue
    t_mean = treated_obs[col].mean()
    c_mean = control_obs[col].mean()
    mult = 100 if "×100" in label else 1
    t_mean *= mult; c_mean *= mult
    def fmt(mine, paper):
        diff = abs(mine - paper)
        if abs(paper) < 0.5:
            mark = "✓" if diff < 0.05 else "✗"
        else:
            pct = diff / abs(paper) * 100
            mark = "✓" if pct < 15 else "✗"
        return f"{mine:.3f}/{paper:.3f} {mark}"
    print(f"{label:<28} {fmt(t_mean, paper_t):<28} {fmt(c_mean, paper_c):<28}")
