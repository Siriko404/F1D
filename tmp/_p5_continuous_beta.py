"""P5-continuous: continuous beta_UK DiD on fully-audited pipeline.
Imports step7 helpers (calendar-prev-Q lags, T8 CASH, IndustryxQtr FE).
Includes ALL beta_UK values (not just tercile treated/control).
Treatment = POST * beta_uk (continuous, relaxed per Campello p.3193)."""

import json, sys, numpy as np, pandas as pd, pyarrow.parquet as pq
from pathlib import Path
from datetime import datetime
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "campello_rebuild"))

import importlib.util
_step7_path = ROOT / "scripts" / "campello_rebuild" / "step7_fullpanel_hypothesis.py"
_step7_spec = importlib.util.spec_from_file_location("step7_fullpanel_hypothesis", _step7_path)
_step7 = importlib.util.module_from_spec(_step7_spec)
_step7_spec.loader.exec_module(_step7)

_prev_q = _step7._prev_q
_latest  = _step7._latest
_calendar_lag1 = _step7._calendar_lag1
_build = _step7._build
POST_Q = _step7.POST_Q
WINSOR = _step7.WINSOR
COMP = _step7.COMP
BUFFER_LO = _step7.BUFFER_LO
WIN_HI_DATE = _step7.WIN_HI_DATE
FIRM_BUILDERS = _step7.FIRM_BUILDERS

from linearmodels.panel import PanelOLS

# -- T8 CASH (verbatim from step7, already audited) --
def _cash_dv_t8():
    df = pq.read_table(COMP, columns=["gvkey","datadate","curcdq","loc","consol","indfmt","datafmt","atq","cheq"]).to_pandas()
    df["datadate"] = pd.to_datetime(df["datadate"], errors="coerce")
    df = df[(df["datadate"] >= BUFFER_LO) & (df["datadate"] <= WIN_HI_DATE)]
    df = df[(df["curcdq"]=="USD") & (df["loc"]=="USA") & (df["consol"]=="C") & (df["indfmt"]=="INDL") & (df["datafmt"]=="STD")].copy()
    for c in ("atq","cheq"): df[c] = pd.to_numeric(df[c], errors="coerce")
    df["gvkey"] = df["gvkey"].astype("int64").astype(str).str.zfill(6)
    df["cal_yr_qtr"] = (df["datadate"].dt.year * 10 + df["datadate"].dt.quarter).astype("int64")
    df = df.sort_values(["gvkey","cal_yr_qtr","datadate"], kind="stable")
    df = df.drop_duplicates(["gvkey","cal_yr_qtr"], keep="last")
    src = df[["gvkey","cal_yr_qtr","atq","cheq"]].rename(columns={"cal_yr_qtr":"_pq","atq":"atq_l1","cheq":"cheq_l1"})
    df["_pq"] = df["cal_yr_qtr"].map(_prev_q).astype("int64")
    df = df.merge(src, on=["gvkey","_pq"], how="left").drop(columns="_pq")
    df["denom"] = df["atq_l1"] - df["cheq_l1"]
    df = df[df["cheq"].notna() & df["cheq_l1"].notna() & (df["denom"] > 0)].copy()
    df["CASH"] = df["cheq"] / df["denom"]
    return df[["gvkey","cal_yr_qtr","CASH"]]


print("=== P5-continuous: beta_UK x POST (relaxed, ALL beta values) ===\n")

# -- Load audited step1 + step3 --
s1 = pd.read_parquet(_latest("step1_sample") / "sample.parquet",
                     columns=["gvkey","cal_yr_qtr","atq","fic100_industry_id"])
s1["gvkey"] = s1["gvkey"].astype(str).str.zfill(6)

trt = pd.read_parquet(_latest("step3_treatment") / "treatment.parquet",
                      columns=["gvkey","group","in_step1","beta_uk"])
trt["gvkey"] = trt["gvkey"].astype(str).str.zfill(6)

# Continuous: ALL in_step1 firms (not just treated+control)
# Paper: "relax this restriction and include all values of beta_UK_i"
tc = trt[trt["in_step1"]].copy()
print(f"All step1 firms: {tc['gvkey'].nunique():,}")
print(f"  nonneg: {int((tc['beta_uk']>=0).sum()):,}")
print(f"  negative: {int((tc['beta_uk']<0).sum()):,}")

# Panel merge
panel = s1.merge(tc[["gvkey","beta_uk"]], on="gvkey", how="inner")
panel["POST"] = panel["cal_yr_qtr"].isin(POST_Q).astype(int)
panel["POST_x_BETA"] = panel["POST"] * panel["beta_uk"]
print(f"Panel firm-quarters: {len(panel):,} / {panel['gvkey'].nunique():,} firms")

# CASH T8
df = panel.merge(_cash_dv_t8(), on=["gvkey","cal_yr_qtr"], how="inner")
df = df[df["atq"] > 0].copy()
df["log_assets"] = np.log(df["atq"])

# 5 firm controls (lagged 1Q)
firm_cols = []
for cls in FIRM_BUILDERS:
    b = _build(cls)
    col = [c for c in b.columns if c not in ("gvkey","cal_yr_qtr")][0]
    firm_cols.append(col)
    df = df.merge(_calendar_lag1(b, col), on=["gvkey","cal_yr_qtr"], how="left")
df = df.merge(_calendar_lag1(df[["gvkey","cal_yr_qtr","log_assets"]], "log_assets")
              .rename(columns={"log_assets":"log_assets_l1"}),
              on=["gvkey","cal_yr_qtr"], how="left")
firm_cols.append("log_assets_l1")

# Consensus EPS (lagged 1Q)
cons_cls = _build("BrexitConsensusEPSBuilder")
cons = cons_cls.sort_values(["gvkey","cal_yr_qtr"], kind="stable")
cons = cons.drop_duplicates(["gvkey","cal_yr_qtr"], keep="last")
ccol = [c for c in cons.columns if c not in ("gvkey","cal_yr_qtr")][0]
con_lagged = _calendar_lag1(cons, ccol).rename(columns={ccol: "cons_fwd"})
df = df.merge(con_lagged, on=["gvkey","cal_yr_qtr"], how="left")

# Winsorize + FE
df["CASH_w"] = df.groupby("cal_yr_qtr", observed=True)["CASH"].transform(
    lambda s: s.clip(s.quantile(WINSOR), s.quantile(1 - WINSOR)))
df["indqtr_code"] = ((df["fic100_industry_id"].astype("int64").astype(str)
                      + "_" + df["cal_yr_qtr"].astype(str))
                     .astype("category").cat.codes)

cols = ["POST_x_BETA"] + firm_cols + ["cons_fwd"]
sub = df.dropna(subset=["CASH_w","indqtr_code"] + cols).copy()
pdat = sub.set_index(["gvkey","cal_yr_qtr"]).sort_index()
nf = sub["gvkey"].nunique()
print(f"\nEstimation sample: {len(sub):,} fq / {nf:,} firms")

# DiD
res = PanelOLS(pdat["CASH_w"], pdat[cols], entity_effects=True,
               other_effects=pdat["indqtr_code"], drop_absorbed=True
               ).fit(cov_type="clustered", cluster_entity=True, cluster_time=True)

b  = float(res.params["POST_x_BETA"])
se = float(res.std_errors["POST_x_BETA"])
t  = float(res.tstats["POST_x_BETA"])
p  = float(res.pvalues["POST_x_BETA"])

print(f"\n  d(POST * beta_UK) = {b:+.5f}  SE {se:.5f}  t {t:+.3f}  p {p:.4f}  "
      f"N {int(res.nobs):,}  firms {nf:,}  R2w {float(res.rsquared_within):.4f}")
print(f"\n  Paper (continuous beta, relaxed): sign reproduced per prior session "
      f"(+0.099, p~0.09 on pre-fix pipeline)")
print(f"  This run: {b:+.4f}, p={p:.3f} on FULLY AUDITED pipeline "
      f"(T8 CASH, P-only betas, correct terciles, all controls lagged 1Q)")

# Save
ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
odir = ROOT / "outputs" / "campello_rebuild" / "step7_continuous_beta" / ts
odir.mkdir(parents=True, exist_ok=True)
(odir / "summary.json").write_text(json.dumps({
    "spec": "continuous beta_UK x POST (relaxed, ALL beta values per p.3193)",
    "dv": "CASH = cheq_t / (atq_{t-1} - cheq_{t-1}) (T8 net-of-cash)",
    "fe": "Firm + Industry(FIC100) x calendar-Quarter",
    "se": "two-way clustered (firm + calendar-quarter)",
    "controls": cols,
    "result": {"delta": b, "se": se, "t": t, "pvalue": p,
               "nobs": int(res.nobs), "n_firms": int(nf),
               "r2w": float(res.rsquared_within)},
    "coefficients": [{"name": c, "coef": float(res.params[c]),
                      "se": float(res.std_errors[c]),
                      "t": float(res.tstats[c]),
                      "pvalue": float(res.pvalues[c])} for c in res.params.index],
}, indent=2), encoding="utf-8")
print(f"\nwritten -> {odir}")
