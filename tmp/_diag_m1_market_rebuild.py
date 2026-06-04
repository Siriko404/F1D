"""Supervisor M1-M3: Market arm rebuild — P-only CCM + step1-filtered terciles.

Two fixes vs current step2/step3:
  1. LINKPRIM='P' only (drop 'C') — same fix textual side already got
  2. Tercile cutpoints on in_step1-filtered nonneg pool (paper Table C1 step-9 order)
Binary-tercile DiD with T8 DV. C.2 Panel A group means.
"""
from __future__ import annotations

import importlib.util, json, sys
from datetime import datetime
from pathlib import Path

import numpy as np, pandas as pd, pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
sys.path.insert(0, str(ROOT/"scripts"/"campello_rebuild"))

from step7_fullpanel_hypothesis import (
    FIRM_BUILDERS, POST_Q, _build, _calendar_lag1, _latest, _prev_q,
)

COMP = ROOT/"inputs"/"comp_na_daily_all"/"comp_na_daily_all.parquet"
BUFFER_LO = pd.Timestamp("2008-01-01"); WIN_HI_DATE = pd.Timestamp("2016-12-31")

_p = ROOT/"scripts"/"campello_rebuild"/"_build_final_did_statsum_consensus.py"
_s = importlib.util.spec_from_file_location("_fin", _p); _fin = importlib.util.module_from_spec(_s)
_s.loader.exec_module(_fin); _statsum_meanest_z = _fin._statsum_meanest_z

try: sys.stdout.reconfigure(encoding="utf-8")
except: pass

# ═══════════════════════════════════════════════════════════════════════════
# FIX 1: P-only CCM (not P/C)
# ═══════════════════════════════════════════════════════════════════════════

def _load_ccm_p_only() -> pd.DataFrame:
    ccm = pd.read_parquet(
        ROOT/"inputs"/"CRSPCompustat_CCM"/"CRSPCompustat_CCM.parquet",
        columns=["gvkey","LPERMNO","LINKPRIM","LINKTYPE","LINKDT","LINKENDDT"])
    ccm = ccm[ccm["LINKPRIM"].eq("P") & ccm["LINKTYPE"].isin(["LU","LC"])].copy()
    ccm["LPERMNO"] = pd.to_numeric(ccm["LPERMNO"], errors="coerce")
    ccm = ccm.dropna(subset=["LPERMNO"])
    ccm["LPERMNO"] = ccm["LPERMNO"].astype("int64")
    ccm["gvkey"] = ccm["gvkey"].astype(int).astype(str).str.zfill(6)
    ccm["LINKDT"] = pd.to_datetime(ccm["LINKDT"], errors="coerce")
    ccm["LINKENDDT"] = pd.to_datetime(
        ccm["LINKENDDT"].astype(str).replace({"E":"2099-12-31"}), errors="coerce")
    return ccm


# ═══════════════════════════════════════════════════════════════════════════
# STEP 2 REBUILD: β^UK with P-only CCM
# ═══════════════════════════════════════════════════════════════════════════

WIN_START = pd.Timestamp("2010-01-01"); WIN_END = pd.Timestamp("2014-12-31")
MIN_DAYS = 15; MIN_MONTHS = 24

def _ym(s):
    dt = pd.to_datetime(s)
    return (dt.dt.year*100+dt.dt.month).astype("int64")

def _monthly_vol(daily, ret_col, by_cols):
    g = daily.groupby(by_cols+["ym"])[ret_col]
    out = g.agg(_n="count", _sd=lambda x: x.std(ddof=1)).reset_index()
    out = out[out["_n"]>=MIN_DAYS].copy()
    return out.rename(columns={"_sd":f"vol_{ret_col}"}).drop(columns="_n")


print("="*72)
print("M1-M3: Market arm rebuild — P-only CCM + step1-filtered terciles")
print("="*72)

# ── Load CRSP daily ──
print("\n── Loading CRSP daily (2010-2014) ──")
dsf = ROOT/"inputs"/"CRSP_DSF"
frames = []
for yr in range(2010,2015):
    for q in range(1,5):
        d = pd.read_parquet(dsf/f"CRSP_DSF_{yr}_Q{q}.parquet",
                            columns=["PERMNO","date","RET","sprtrn"])
        frames.append(d)
fd = pd.concat(frames, ignore_index=True)
fd["date"] = pd.to_datetime(fd["date"])
fd = fd[(fd["date"]>=WIN_START)&(fd["date"]<=WIN_END)]
for c in ("RET","sprtrn"): fd[c] = pd.to_numeric(fd[c], errors="coerce")
fd["PERMNO"] = pd.to_numeric(fd["PERMNO"], errors="coerce")
fd = fd.dropna(subset=["PERMNO"]); fd["PERMNO"] = fd["PERMNO"].astype("int64")
fd["ym"] = _ym(fd["date"])
fd = fd[fd["RET"].notna()&(fd["RET"]>-1.0)]
print(f"  {len(fd):,} daily rows, {fd['PERMNO'].nunique():,} PERMNOs")

# ── Firm monthly vol ──
firm_vol = _monthly_vol(fd[["PERMNO","ym","RET"]], "RET", ["PERMNO"]).rename(
    columns={"vol_RET":"vol_r"})
print(f"  firm-months: {len(firm_vol):,}")

# ── Market monthly vols ──
sp = fd[["date","sprtrn","ym"]].dropna(subset=["sprtrn"]).drop_duplicates(
    subset=["date"]).sort_values("date")
sp_vol = _monthly_vol(sp, "sprtrn", [])

ft = pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"Yahoo_FTSE100"/"FTSE100_yfinance_daily.csv")
ft["date"] = pd.to_datetime(ft["Date"])
ft = ft[(ft["date"]>=WIN_START)&(ft["date"]<=WIN_END)].sort_values("date")
ft["ftse_ret"] = pd.to_numeric(ft["Close"], errors="coerce").pct_change()
ft = ft.dropna(subset=["ftse_ret"]); ft["ym"] = _ym(ft["date"])
ft_vol = _monthly_vol(ft, "ftse_ret", [])

fx = pd.read_csv(ROOT/"inputs"/"Brexit_replication"/"BoE"/"USD_GBP_daily_2008-2018.csv")
fx["date"] = pd.to_datetime(fx["DATE"], format="%d %b %Y")
fx = fx[(fx["date"]>=WIN_START)&(fx["date"]<=WIN_END)].sort_values("date")
fx["fx_ret"] = pd.to_numeric(fx["XUDLUSS"], errors="coerce").pct_change()
fx = fx.dropna(subset=["fx_ret"]); fx["ym"] = _ym(fx["date"])
fx_vol = _monthly_vol(fx, "fx_ret", [])

mkt = ft_vol.merge(sp_vol,on="ym").merge(fx_vol,on="ym").rename(
    columns={"vol_ftse_ret":"vol_ftse","vol_sprtrn":"vol_sp500","vol_fx_ret":"vol_fx"})
print(f"  market months: {len(mkt):,}")

# ── P-only CCM link ──
fm = firm_vol.merge(mkt, on="ym", how="inner")
ccm = _load_ccm_p_only()
yy = fm["ym"]//100; mm = fm["ym"]%100
fm["mend"] = pd.to_datetime(dict(year=yy, month=mm, day=1))+pd.offsets.MonthEnd(0)
m = fm.merge(ccm, left_on="PERMNO", right_on="LPERMNO", how="left")
m = m[(m["LINKDT"]<=m["mend"])&(m["mend"]<=m["LINKENDDT"])].copy()
m = m.sort_values("LINKDT").drop_duplicates(subset=["PERMNO","ym"], keep="first")
# Share-class dedup: keep PERMNO with most firm-months per gvkey
pick = (m.groupby(["gvkey","PERMNO"]).size().reset_index(name="cnt")
         .sort_values("cnt", ascending=False)
         .drop_duplicates("gvkey", keep="first")[["gvkey","PERMNO"]])
m = m.merge(pick, on=["gvkey","PERMNO"], how="inner")
print(f"  P-only CCM: {len(m):,} firm-months, {m['gvkey'].nunique():,} gvkeys")

# ── β^UK OLS per firm ──
recs = []
for gv, g in m.groupby("gvkey", sort=False):
    y = g["vol_r"].to_numpy(float)
    X = np.column_stack([np.ones(len(g)), g["vol_ftse"].to_numpy(float),
                          g["vol_sp500"].to_numpy(float), g["vol_fx"].to_numpy(float)])
    n, k = X.shape
    if n < MIN_MONTHS or np.linalg.matrix_rank(X) < k:
        continue
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X@beta
    dof = n - k
    sigma2 = float(resid@resid)/dof
    xtx_inv = np.linalg.inv(X.T@X)
    se = float(np.sqrt(sigma2*xtx_inv[1,1]))
    b = float(beta[1])
    recs.append((gv, b, se, b/se if se>0 else np.nan, n))

beta = pd.DataFrame(recs, columns=["gvkey","beta_uk","se","t","nobs"])
print(f"\n  β^UK estimated: {len(beta):,} firms (P-only CCM)")
print(f"  nonneg: {(beta['beta_uk']>=0).sum():,}  neg: {(beta['beta_uk']<0).sum():,}  "
      f"mean: {beta['beta_uk'].mean():.4f}  median: {beta['beta_uk'].median():.4f}")

# ═══════════════════════════════════════════════════════════════════════════
# FIX 2: STEP 3 REBUILD — terciles on in_step1-filtered nonneg pool
# ═══════════════════════════════════════════════════════════════════════════

s1 = pd.read_parquet(_latest("step1_sample")/"sample.parquet",
                     columns=["gvkey","cal_yr_qtr","atq","fic100_industry_id"])
s1["gvkey"] = s1["gvkey"].astype(str).str.zfill(6)
s1_gv = set(s1["gvkey"].unique())
print(f"\n  step1 firms: {len(s1_gv):,}")

# Filter to in_step1 FIRST, then compute terciles on nonneg
beta["in_step1"] = beta["gvkey"].isin(s1_gv)
step1_beta = beta[beta["in_step1"]].copy()
step1_nn = step1_beta[step1_beta["beta_uk"]>=0].copy()
q33 = float(step1_nn["beta_uk"].quantile(1/3))
q67 = float(step1_nn["beta_uk"].quantile(2/3))

print(f"  in_step1 β^UK firms: {len(step1_beta):,}  "
      f"nonneg: {len(step1_nn):,}  neg: {(step1_beta['beta_uk']<0).sum():,}")
print(f"  NEW cutpoints (on step1-filtered nonneg): p33={q33:.4f}  p67={q67:.4f}")
print(f"  OLD cutpoints (on full universe):         p33=0.2394  p67=0.6261")
print(f"  Paper cutpoints (reference):              0.28 / 0.68")

def _grp(b):
    if b < 0: return "excluded_negative"
    if b >= q67: return "treated"
    if b <= q33: return "control"
    return "middle"

step1_beta["group"] = step1_beta["beta_uk"].apply(_grp)
ct = step1_beta["group"].value_counts().to_dict()
for g in ("treated","control","middle","excluded_negative"):
    print(f"  {g:>18}: {ct.get(g,0):,}")
print(f"  Paper (assignment-equivalent, pre-step-10): ~449 treated / ~360 control "
      f"(after full DiD merge attrition)")

# Build treatment dataframe for DiD
tc = step1_beta[step1_beta["group"].isin(["treated","control"])].copy()
tc["HIGH_UK_EXPOSURE"] = (tc["group"]=="treated").astype(int)
nT = int((tc["HIGH_UK_EXPOSURE"]==1).sum())
nC = int((tc["HIGH_UK_EXPOSURE"]==0).sum())
print(f"\n  DiD treatment: T={nT:,}  C={nC:,}  (pre-DiD-merge)")

# ═══════════════════════════════════════════════════════════════════════════
# T8 CASH DV
# ═══════════════════════════════════════════════════════════════════════════

print("\n── Building T8 CASH DV ──")
cash = pq.read_table(COMP, columns=["gvkey","datadate","curcdq","loc","consol",
    "indfmt","datafmt","atq","cheq"]).to_pandas()
cash["datadate"] = pd.to_datetime(cash["datadate"], errors="coerce")
cash = cash[(cash["datadate"]>=BUFFER_LO)&(cash["datadate"]<=WIN_HI_DATE)]
cash = cash[(cash["curcdq"]=="USD")&(cash["loc"]=="USA")&(cash["consol"]=="C")
            &(cash["indfmt"]=="INDL")&(cash["datafmt"]=="STD")].copy()
for c in ("atq","cheq"): cash[c] = pd.to_numeric(cash[c], errors="coerce")
cash["gvkey"] = cash["gvkey"].astype("int64").astype(str).str.zfill(6)
cash["cal_yr_qtr"] = (cash["datadate"].dt.year*10+cash["datadate"].dt.quarter).astype("int64")
cash = cash.sort_values(["gvkey","cal_yr_qtr","datadate"], kind="stable")
cash = cash.drop_duplicates(["gvkey","cal_yr_qtr"], keep="last")
src = cash[["gvkey","cal_yr_qtr","atq","cheq"]].rename(
    columns={"cal_yr_qtr":"_pq","atq":"atq_l1","cheq":"cheq_l1"})
cash["_pq"] = cash["cal_yr_qtr"].map(_prev_q).astype("int64")
cash = cash.merge(src, on=["gvkey","_pq"], how="left").drop(columns="_pq")
cash["denom"] = cash["atq_l1"] - cash["cheq_l1"]
cash = cash[cash["cheq"].notna()&(cash["denom"]>0)].copy()
cash["CASH"] = cash["cheq"]/cash["denom"]
cash_t8 = cash[["gvkey","cal_yr_qtr","CASH"]].copy(); del cash
print(f"  {len(cash_t8):,} firm-qtrs")

# ═══════════════════════════════════════════════════════════════════════════
# DiD PANEL
# ═══════════════════════════════════════════════════════════════════════════

print("\n── Building DiD panel ──")
panel = s1.merge(tc[["gvkey","HIGH_UK_EXPOSURE","beta_uk","group"]],
                 on="gvkey", how="inner")
panel["POST"] = panel["cal_yr_qtr"].isin(POST_Q).astype(int)
df = panel.merge(cash_t8, on=["gvkey","cal_yr_qtr"], how="inner")
df = df[df["atq"]>0].copy(); df["log_assets"] = np.log(df["atq"])

firm_cols = []
for cls in FIRM_BUILDERS:
    b = _build(cls)
    col = [c for c in b.columns if c not in ("gvkey","cal_yr_qtr")][0]
    df = df.merge(_calendar_lag1(b, col), on=["gvkey","cal_yr_qtr"], how="left")
    firm_cols.append(col)
df = df.merge(_calendar_lag1(
    df[["gvkey","cal_yr_qtr","log_assets"]], "log_assets").rename(
    columns={"log_assets":"log_assets_l1"}), on=["gvkey","cal_yr_qtr"], how="left")
firm_cols.append("log_assets_l1")

df = df.merge(_statsum_meanest_z(), on=["gvkey","cal_yr_qtr"], how="left")
df["CASH"] = df.groupby("cal_yr_qtr", observed=True)["CASH"].transform(
    lambda s: s.clip(s.quantile(0.01), s.quantile(0.99)))
df["POST_x_HIGH"] = (df["POST"]*df["HIGH_UK_EXPOSURE"]).astype(float)
df["indqtr_code"] = ((df["fic100_industry_id"].astype("int64").astype(str)
    +"_"+df["cal_yr_qtr"].astype(str)).astype("category").cat.codes)

reg_cols = ["POST_x_HIGH"]+firm_cols+["cons_fwd"]
sub = df.dropna(subset=["CASH","indqtr_code"]+reg_cols).copy()
nT_est = int(sub[sub["HIGH_UK_EXPOSURE"]==1]["gvkey"].nunique())
nC_est = int(sub[sub["HIGH_UK_EXPOSURE"]==0]["gvkey"].nunique())
print(f"  DiD panel: {len(sub):,} obs, {sub['gvkey'].nunique():,} firms")
print(f"  Estimation T={nT_est:,}  C={nC_est:,}")
print(f"  Paper:      T=449  C=360  (post-step-10 merge)")

# ═══════════════════════════════════════════════════════════════════════════
# DiD ESTIMATION
# ═══════════════════════════════════════════════════════════════════════════

print("\n── DiD estimation ──")
from linearmodels.panel import PanelOLS

pdat = sub.set_index(["gvkey","cal_yr_qtr"]).sort_index()
res = PanelOLS(pdat["CASH"], pdat[reg_cols], entity_effects=True,
               other_effects=pdat["indqtr_code"], drop_absorbed=True
               ).fit(cov_type="clustered", cluster_entity=True, cluster_time=True)

b = float(res.params["POST_x_HIGH"])
se = float(res.std_errors["POST_x_HIGH"])
t = float(res.tstats["POST_x_HIGH"])
p = float(res.pvalues["POST_x_HIGH"])
p_one = p/2 if b>0 else 1-p/2

print(f"\n  {'='*56}")
print(f"  BINARY-TERCILE DiD (T8 CASH DV)")
print(f"  {'='*56}")
print(f"  POST×HIGH_βᵁᴷ  δ = {b:+.5f}  SE = {se:.5f}  t = {t:+.3f}")
print(f"  p(two) = {p:.4f}  p(one) = {p_one:.4f}  {'*' if p_one<0.10 else ''}{'*' if p_one<0.05 else ''}{'*' if p_one<0.01 else ''}")
print(f"  N = {res.nobs:,}  firms = {sub['gvkey'].nunique():,}")
print(f"  R²w = {res.rsquared_within:.4f}")
print(f"  Paper T8 col.1: δ = +0.231***  SE = 0.047  N = 17,170")

# ═══════════════════════════════════════════════════════════════════════════
# C.2 PANEL A — Group means
# ═══════════════════════════════════════════════════════════════════════════

print(f"\n── Table C.2 Panel A: Group means ──")
# Compute means on the estimation sample (pre-DV only, use firm-level means of time-varying vars)
# C.2 reports means of firm characteristics for treated vs control groups
# Variables: CASH (T1), SIZE, TOBIN_Q, SALES_GROWTH, CASH_FLOW
# Paper reports these at the FIRM level (averaged over the pre-period)

# T1 CASH = cheq_t / atq_{t-1}
df["CASH_T1"] = df["cheq"]/df.groupby("gvkey")["atq"].shift(1) if "cheq" in df.columns else np.nan

# Compute firm-level means in the pre-Brexit period (2010Q1-2015Q2)
pre = df[df["cal_yr_qtr"]<20163].copy()
# Map control column names to C.2 labels
ctrl_map = {
    "brexit_stock_return": "STOCK_RETURN",
    "brexit_tobins_q": "TOBIN_Q",
    "brexit_cash_flow": "CASH_FLOW",
    "brexit_sales_growth": "SALES_GROWTH",
    "log_assets": "SIZE",
}
paper_c2 = {
    "CASH": (0.175, 0.164),
    "SIZE": (6.677, 7.205),
    "TOBIN_Q": (1.948, 1.928),
    "SALES_GROWTH": (0.195, 0.105),
    "CASH_FLOW": (0.016, 0.032),
}

print(f"  {'Variable':<16} {'Rebuild T':>10} {'Rebuild C':>10} "
      f"{'Paper T':>10} {'Paper C':>10}")
print(f"  {'-'*60}")

# For each variable, compute firm-level mean in pre-period, then group mean
for col, label in ctrl_map.items():
    if col in pre.columns:
        fm = pre.dropna(subset=[col]).groupby(["gvkey","HIGH_UK_EXPOSURE"])[col].mean()
        t_mean = fm.xs(1, level="HIGH_UK_EXPOSURE").mean() if 1 in fm.index.get_level_values("HIGH_UK_EXPOSURE") else np.nan
        c_mean = fm.xs(0, level="HIGH_UK_EXPOSURE").mean() if 0 in fm.index.get_level_values("HIGH_UK_EXPOSURE") else np.nan
        pt, pc = paper_c2.get(label, (np.nan, np.nan))
        print(f"  {label:<16} {t_mean:>10.3f} {c_mean:>10.3f} {pt:>10.3f} {pc:>10.3f}")

# CASH (T1) separately
if "cheq" in df.columns and "atq" in df.columns:
    pre_t1 = pre.copy()
    pre_t1["atq_l1"] = pre_t1.groupby("gvkey")["atq"].shift(1)
    pre_t1["CASH_T1"] = pre_t1["cheq"]/pre_t1["atq_l1"]
    pre_t1 = pre_t1.dropna(subset=["CASH_T1"])
    fm_t1 = pre_t1.groupby(["gvkey","HIGH_UK_EXPOSURE"])["CASH_T1"].mean()
    t1_t = fm_t1.xs(1, level="HIGH_UK_EXPOSURE").mean() if 1 in fm_t1.index.get_level_values("HIGH_UK_EXPOSURE") else np.nan
    t1_c = fm_t1.xs(0, level="HIGH_UK_EXPOSURE").mean() if 0 in fm_t1.index.get_level_values("HIGH_UK_EXPOSURE") else np.nan
    print(f"  {'CASH (T1)':<16} {t1_t:>10.3f} {t1_c:>10.3f} {0.175:>10.3f} {0.164:>10.3f}")

# Save results
od = ROOT/"outputs"/"campello_rebuild"/"_diag_m1"
od.mkdir(parents=True, exist_ok=True)
ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
out = {
    "fixes": ["LINKPRIM=P_only", "terciles_on_step1_filtered_nonneg"],
    "ccm": "P-only (LU+LC)",
    "cutpoints": {"p33": q33, "p67": q67, "paper_p33": 0.28, "paper_p67": 0.68},
    "counts_at_assignment": {k: int(v) for k, v in ct.items()},
    "counts_pre_did_merge": {"treated": nT, "control": nC},
    "counts_estimation": {"treated": nT_est, "control": nC_est,
                          "paper_treated": 449, "paper_control": 360},
    "did": {"delta": b, "se": se, "t": t, "p_two": p, "p_one": p_one,
            "nobs": int(res.nobs), "n_firms": int(sub["gvkey"].nunique()),
            "r2w": float(res.rsquared_within),
            "paper_delta": 0.231, "paper_se": 0.047, "paper_n": 17170},
    "nonneg_pool_size": len(step1_nn),
    "beta_summary": {"n_total": len(beta), "n_nonneg": int((beta["beta_uk"]>=0).sum()),
                     "mean": float(beta["beta_uk"].mean()),
                     "median": float(beta["beta_uk"].median())},
}
(od/f"results_{ts}.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
print(f"\n→ {od / f'results_{ts}.json'}")
print("Done.")
