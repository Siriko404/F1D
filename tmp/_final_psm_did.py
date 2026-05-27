"""Bundle latest files, run PSM, then DiD on both CASH definitions."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import shutil, numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT / "outputs" / "campello_v2"

def latest(fname):
    runs = sorted([d for d in OUT.iterdir() if d.is_dir() and (d / fname).exists()], reverse=True)
    return runs[0]

# Force variant F dir (realized vol β, exact tercile match)
beta_dir = OUT / "20260527_010458"
print(f"Using: {beta_dir}")

print(f"Using: {beta_dir}")

panel = pd.read_parquet(beta_dir / "variables_panel.parquet")
beta = pd.read_parquet(beta_dir / "beta_uk.parquet")
sret = pd.read_parquet(beta_dir / "stock_returns.parquet")
ceps = pd.read_parquet(beta_dir / "consensus_eps.parquet")

panel = panel.merge(sret, on=["gvkey","cal_yr_qtr"], how="left")
panel = panel.merge(ceps, on=["gvkey","cal_yr_qtr"], how="left")
panel = panel.merge(beta[["gvkey","beta_uk"]], on="gvkey", how="left")

PRE_BREXIT_END = 20154
nonneg = beta[beta["beta_uk"]>=0]
t1 = nonneg["beta_uk"].quantile(1/3); t2 = nonneg["beta_uk"].quantile(2/3)
panel["treated"] = (panel["beta_uk"]>t2).astype(float)
panel["control_pool"] = ((panel["beta_uk"]>=0)&(panel["beta_uk"]<t1)).astype(float)
panel = panel[(panel["treated"]==1)|(panel["control_pool"]==1)].copy()

# ---- PSM ----
pre = panel[panel["cal_yr_qtr"] <= PRE_BREXIT_END].copy()
pre = pre.sort_values(["gvkey","cal_yr_qtr"])
pre["STOCK_RETURNS_lag1"] = pre.groupby("gvkey")["STOCK_RETURNS"].shift(1)
covariates = ["STOCK_RETURNS_lag1","CONSENSUS_EPS","TOBIN_Q","CASH_FLOW","SALES_GROWTH","SIZE"]
firm_avg = pre.groupby("gvkey").agg({"treated":"max","sic":"first",
    **{c:"mean" for c in covariates}}).reset_index().dropna(subset=covariates)

np.random.seed(42)
X = firm_avg[covariates].values; y = firm_avg["treated"].values.astype(int)
scaler = StandardScaler()
logreg = LogisticRegression(max_iter=1000, random_state=42)
logreg.fit(scaler.fit_transform(X), y)
firm_avg["pscore"] = logreg.predict_proba(scaler.transform(X))[:,1]

t_idx = firm_avg.index[firm_avg["treated"]==1].tolist()
c_idx = firm_avg.index[firm_avg["treated"]==0].tolist()
nbrs = NearestNeighbors(n_neighbors=min(3,len(c_idx)))
nbrs.fit(firm_avg.loc[c_idx,["pscore"]])

dist, idx_in_c = nbrs.kneighbors(firm_avg.loc[t_idx,["pscore"]])
matched_t = firm_avg.loc[t_idx, "gvkey"].values
matched_c = firm_avg.loc[[c_idx[i] for row in idx_in_c for i in row], "gvkey"].values

print(f"\nMatched: {len(matched_t)}T / {len(set(matched_c))}C unique")

# ---- Matched-sample comparison ----
pre_comp = pre.copy()
t_obs = pre_comp[pre_comp["gvkey"].isin(set(matched_t))]
c_obs = pre_comp[pre_comp["gvkey"].isin(set(matched_c))]

anchor = {"INVESTMENT":(0.020,0.012),"R&D":(0.030,0.016),"DIVESTITURES (×100)":(0.129,0.088),
    "CASH":(0.175,0.164),"NON_CASH_WORKING_CAPITAL":(0.058,0.086),"TOBIN_Q":(1.948,1.928),
    "CASH_FLOW":(0.016,0.032),"SIZE (Log Assets)":(6.677,7.205),"SALES_GROWTH":(0.195,0.105),
    "CONSENSUS_EPS":(0.023,0.025),"STOCK_RETURNS_lag1":(0.021,0.038)}
var_map = {"INVESTMENT":"INVESTMENT","R&D":"RD","DIVESTITURES (×100)":"DIVESTITURES",
    "CASH":"CASH","NON_CASH_WORKING_CAPITAL":"NWC","TOBIN_Q":"TOBIN_Q",
    "CASH_FLOW":"CASH_FLOW","SIZE (Log Assets)":"SIZE","SALES_GROWTH":"SALES_GROWTH",
    "CONSENSUS_EPS":"CONSENSUS_EPS","STOCK_RETURNS_lag1":"STOCK_RETURNS_lag1"}

print(f"\n=== Table C.2 Panel A (Market-Based) — Matched Sample ===")
print(f"{'Variable':<28}{'TREATED (mine/paper)':<28}{'CONTROL (mine/paper)'}")
print("-"*84)
pass_count = 0
for label, (pt,pc) in anchor.items():
    col = var_map.get(label); mult = 100 if "×100" in label else 1
    tm = t_obs[col].mean()*mult; cm = c_obs[col].mean()*mult
    def ft(m,p):
        d = abs(m-p)
        if abs(p)<0.5: return "✓" if d<0.05 else "✗"
        return "✓" if d/abs(p)*100<15 else "✗"
    t_ok = ft(tm,pt)=="✓"; c_ok = ft(cm,pc)=="✓"
    if t_ok: pass_count += 1
    if c_ok: pass_count += 1
    print(f"{label:<28} {tm:.3f}/{pt:.3f} {ft(tm,pt):<3}            {cm:.3f}/{pc:.3f} {ft(cm,pc)}")
print(f"Total: {pass_count}/22")

# ---- DiD on BOTH CASH defs (FULL sample) ----
# Add CASH_T8 via raw Compustat
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
denom = panel["atq_l1"] - panel["cheq_l1"]
panel["CASH_T8"] = np.where((denom.notna())&(denom>0), panel["cheq"]/denom, np.nan)
for q, idx in panel.groupby("cal_yr_qtr").groups.items():
    v = panel.loc[idx,"CASH_T8"];
    if v.notna().sum()<10: continue
    lo, hi = v.quantile(0.01), v.quantile(0.99)
    panel.loc[idx,"CASH_T8"] = v.clip(lo, hi)

PRE_Q=[20153,20154]; POST_Q=[20163,20164]
did_panel = panel[panel["cal_yr_qtr"].isin(PRE_Q+POST_Q)].copy()
did_panel["POST"] = did_panel["cal_yr_qtr"].isin(POST_Q).astype(float)
did_panel["TREAT_POST"] = did_panel["treated"] * did_panel["POST"]

# Lag controls
did_panel = did_panel.sort_values(["gvkey","cal_yr_qtr"])
ctrl_cols = ["STOCK_RETURNS","TOBIN_Q","CASH_FLOW","SIZE","SALES_GROWTH","CONSENSUS_EPS"]
for c in ctrl_cols:
    did_panel[f"{c}_lag1"] = did_panel.groupby("gvkey")[c].shift(1)

from linearmodels.panel import PanelOLS
for dv,label in [("CASH","CASH_T1"),("CASH_T8","CASH_T8")]:
    sub = did_panel.dropna(subset=[dv]+[f"{c}_lag1" for c in ctrl_cols]).copy()
    sub_di = sub.set_index(["gvkey","cal_yr_qtr"])
    tp = sub[(sub["treated"]==1)&(sub["POST"]==1)][dv].mean()
    tb = sub[(sub["treated"]==1)&(sub["POST"]==0)][dv].mean()
    cp = sub[(sub["treated"]==0)&(sub["POST"]==1)][dv].mean()
    cb = sub[(sub["treated"]==0)&(sub["POST"]==0)][dv].mean()
    did_raw = (tp-tb)-(cp-cb)
    print(f"\n--- {label} DiD (full treated+control sample) ---")
    print(f"  Tpre={tb:.4f} Tpost={tp:.4f} Cpre={cb:.4f} Cpost={cp:.4f} RawDiD={did_raw:.4f}")
    try:
        exog = sub_di[["TREAT_POST"]+[f"{c}_lag1" for c in ctrl_cols]]
        mod = PanelOLS(sub_di[dv], exog, entity_effects=True, time_effects=True)
        res = mod.fit(cov_type="clustered", cluster_entity=True, cluster_time=True)
        print(f"  δ={res.params['TREAT_POST']:.4f} SE={res.std_errors['TREAT_POST']:.4f} t={res.tstats['TREAT_POST']:.2f} p={res.pvalues['TREAT_POST']:.4f} N={res.nobs:,}")
    except Exception as e:
        print(f"  PanelOLS: {e}")
    print(f"  Paper δ=+0.231*** N=17,170")
