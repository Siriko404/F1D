"""Check CCM linking quality + survivorship-biased sample."""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = ROOT / "outputs" / "campello_v2"

def latest(fname):
    runs = sorted([d for d in OUT.iterdir() if d.is_dir() and (d / fname).exists()], reverse=True)
    return runs[0] / fname

# Check CCM duplicates and ambiguous mappings
ccm = pd.read_parquet(ROOT / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet")
print(f"CCM total rows: {len(ccm):,}")
print(f"CCM columns: {ccm.columns.tolist()}")
print(f"\nLINKTYPE values:\n{ccm['LINKTYPE'].value_counts()}")
print(f"\nLINKPRIM values:\n{ccm['LINKPRIM'].value_counts()}")

# Filter as in my beta_uk.py
panel = pd.read_parquet(latest("variables_panel.parquet"))
sample_gv = set(panel["gvkey"].unique())
ccm["gvkey"] = ccm["gvkey"].astype(str).str.zfill(6)
ccm = ccm[ccm["gvkey"].isin(sample_gv)]

print(f"\nCCM in sample: {len(ccm):,} rows, {ccm['gvkey'].nunique():,} unique gvkeys")
ccm_pri = ccm[ccm["LINKTYPE"].isin(["LU", "LC"])]
ccm_pri = ccm_pri[ccm_pri["LINKPRIM"].isin(["P", "C"])]
print(f"After LU/LC + P/C filter: {len(ccm_pri):,} rows, {ccm_pri['gvkey'].nunique():,} unique gvkeys")

# How many gvkeys have >1 PERMNO link?
multi = ccm_pri.groupby("gvkey")["LPERMNO"].nunique().value_counts()
print(f"\nGvkeys with N distinct permnos:\n{multi.head()}")

# Verify a few firm mappings sanity-check
# Sample top β^UK firms and check their CCM linkage
beta = pd.read_parquet(latest("beta_uk.parquet"))
print(f"\n--- Sample β^UK top 10 firms with their CCM links ---")
top = beta.nlargest(10, "beta_uk")
for _, r in top.iterrows():
    gv = r["gvkey"]
    links = ccm_pri[ccm_pri["gvkey"] == gv][["LPERMNO", "LINKDT", "LINKENDDT", "LINKTYPE", "LINKPRIM"]]
    print(f"\n  gvkey={gv}  β={r['beta_uk']:+.3f}  r2={r['r2']:.2f}")
    print(links.to_string(index=False))

# --- Survivorship-restricted β^UK ---
# Only firms with continuous Compustat coverage 2010-2014 AND 2015Q3-2016Q4
print("\n\n" + "=" * 80)
print("Survivorship-restricted β^UK test")
print("=" * 80)

# Firms present in ALL quarters of 2010Q1-2014Q4 (estimation window)
est_qs = []
for y in range(2010, 2015):
    for q in range(1, 5):
        est_qs.append(y*10 + q)
all_est = set(est_qs)
# Firms present in ALL key DiD quarters
did_qs = {20153, 20154, 20163, 20164}

firm_qs = panel.groupby("gvkey")["cal_yr_qtr"].apply(set)
firms_est_all = set(firm_qs[firm_qs.apply(lambda s: all_est.issubset(s))].index)
firms_did_all = set(firm_qs[firm_qs.apply(lambda s: did_qs.issubset(s))].index)
firms_both = firms_est_all & firms_did_all
print(f"Firms with full 2010-2014 coverage: {len(firms_est_all):,}")
print(f"Firms with full 2015Q3-2016Q4 coverage: {len(firms_did_all):,}")
print(f"Firms with both: {len(firms_both):,}")

# How does β^UK look on this subset?
b_sub = beta[beta["gvkey"].isin(firms_both)]
print(f"\nβ^UK on continuous firms (N={len(b_sub):,}):")
b = b_sub["beta_uk"]
print(f"  mean={b.mean():.3f}  sd={b.std():.3f}")
print(f"  p33pos: {b[b>=0].quantile(1/3):.3f}  p67pos: {b[b>=0].quantile(2/3):.3f}")
print(f"  paper: t1=0.28, t2=0.68")

# DiD test on continuous-coverage subsample
nonneg = b_sub[b_sub["beta_uk"] >= 0]
t1 = nonneg["beta_uk"].quantile(1/3)
t2 = nonneg["beta_uk"].quantile(2/3)
print(f"\n--- DiD restricted to continuous-coverage firms ---")
print(f"  My terciles: t1={t1:.3f}, t2={t2:.3f}")

sret = pd.read_parquet(latest("stock_returns.parquet"))
ceps = pd.read_parquet(latest("consensus_eps.parquet"))
comp = pd.read_parquet(ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet",
                      columns=["gvkey", "datadate", "atq", "cheq"])
comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
comp["datadate"] = pd.to_datetime(comp["datadate"])
comp["atq"] = pd.to_numeric(comp["atq"], errors="coerce")
comp["cheq"] = pd.to_numeric(comp["cheq"], errors="coerce")
comp = comp.drop_duplicates(subset=["gvkey", "datadate"], keep="last")

p = panel[panel["gvkey"].isin(firms_both)].merge(sret, on=["gvkey", "cal_yr_qtr"], how="left")
p = p.merge(ceps, on=["gvkey", "cal_yr_qtr"], how="left")
p = p.merge(comp[["gvkey", "datadate", "cheq"]], on=["gvkey", "datadate"], how="left",
            suffixes=("_p", ""))
p = p.merge(b_sub[["gvkey", "beta_uk"]], on="gvkey", how="left")
p = p.sort_values(["gvkey", "cal_yr_qtr"])
p["atq_lag1_q"] = p.groupby("gvkey")["atq"].shift(1)
p["cheq_lag1_q"] = p.groupby("gvkey")["cheq"].shift(1)
denom = p["atq_lag1_q"] - p["cheq_lag1_q"]
p["CASH_T8"] = np.where(denom.notna() & (denom > 0), p["cheq"] / denom, np.nan)
p["CASH_T8"] = p["CASH_T8"].replace([np.inf, -np.inf], np.nan)
nv = pd.Series(np.nan, index=p.index)
for q, idx in p.groupby("cal_yr_qtr").groups.items():
    v = p.loc[idx, "CASH_T8"]
    if v.notna().sum() >= 10:
        lo, hi = v.quantile(0.01), v.quantile(0.99)
        nv.loc[idx] = v.clip(lo, hi)
    else:
        nv.loc[idx] = v
p["CASH_T8"] = nv

p["HIGH_UK"] = (p["beta_uk"] > t2).astype(float)
p["LOW_UK"] = ((p["beta_uk"] >= 0) & (p["beta_uk"] < t1)).astype(float)

ctrl_cols = ["STOCK_RETURNS", "TOBIN_Q", "CASH_FLOW", "SIZE", "SALES_GROWTH", "CONSENSUS_EPS"]
for c in ctrl_cols:
    p[f"{c}_lag1"] = p.groupby("gvkey")[c].shift(1)

p = p[(p["HIGH_UK"] == 1) | (p["LOW_UK"] == 1)]
p = p[p["cal_yr_qtr"].isin([20153, 20154, 20163, 20164])]
p["POST"] = p["cal_yr_qtr"].isin([20163, 20164]).astype(float)
p["TREAT_POST"] = p["HIGH_UK"] * p["POST"]
required = ["CASH_T8"] + [f"{c}_lag1" for c in ctrl_cols]
p = p.dropna(subset=required)

print(f"\n  N obs: {len(p):,}  N firms: {p['gvkey'].nunique():,}")
print(f"  N treated firms: {p[p['HIGH_UK']==1]['gvkey'].nunique()}")
print(f"  N control firms: {p[p['LOW_UK']==1]['gvkey'].nunique()}")

# Group means
for grp_label, mask in [("Treat PRE", (p["HIGH_UK"]==1) & (p["POST"]==0)),
                         ("Treat POST", (p["HIGH_UK"]==1) & (p["POST"]==1)),
                         ("Ctrl PRE", (p["LOW_UK"]==1) & (p["POST"]==0)),
                         ("Ctrl POST", (p["LOW_UK"]==1) & (p["POST"]==1))]:
    sub = p[mask]
    print(f"  {grp_label:<14} N={len(sub):>5}  mean CASH_T8={sub['CASH_T8'].mean():.4f}")

raw_dd = (p[(p['HIGH_UK']==1) & (p['POST']==1)]['CASH_T8'].mean() -
          p[(p['HIGH_UK']==1) & (p['POST']==0)]['CASH_T8'].mean()) - \
         (p[(p['LOW_UK']==1) & (p['POST']==1)]['CASH_T8'].mean() -
          p[(p['LOW_UK']==1) & (p['POST']==0)]['CASH_T8'].mean())
print(f"  Raw DiD (means difference): {raw_dd:+.4f}")

from linearmodels import PanelOLS
p["firm_id"] = p["gvkey"].astype("category").cat.codes
p["time_id"] = p["cal_yr_qtr"]
p["sic2"] = p["sic"].fillna(-1).astype(int) // 100
p["ind_qtr"] = p["sic2"].astype(str) + "_" + p["cal_yr_qtr"].astype(str)
p_idx = p.set_index(["firm_id", "time_id"])
y = p_idx["CASH_T8"]
X_cols = ["TREAT_POST"] + [f"{c}_lag1" for c in ctrl_cols]
iq_dum = pd.get_dummies(p_idx["ind_qtr"], prefix="iq", drop_first=True).astype(float)
X = pd.concat([p_idx[X_cols], iq_dum], axis=1)
m = PanelOLS(y, X, entity_effects=True, drop_absorbed=True)
res = m.fit(cov_type="clustered", cluster_entity=True, cluster_time=True)
d = res.params["TREAT_POST"]
pv = res.pvalues["TREAT_POST"]
print(f"\n  Regression δ = {d:+.4f}  p={pv:.3f}  N={int(res.nobs):,}")
