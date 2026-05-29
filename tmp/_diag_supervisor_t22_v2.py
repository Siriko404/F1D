"""Supervisor Task 22 v2: Shared-machinery DiD — both treatments.
MEMORY-AWARE: reads step1 + Compustat once, builds base panel once, splits by treatment.
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
Q4_PRE = [20153, 20154]; Q4_POST = [20163, 20164]; FULL_POST = POST_Q

_p = ROOT/"scripts"/"campello_rebuild"/"_build_final_did_statsum_consensus.py"
_s = importlib.util.spec_from_file_location("_fin", _p); _fin = importlib.util.module_from_spec(_s)
_s.loader.exec_module(_fin); _statsum_meanest_z = _fin._statsum_meanest_z

try: sys.stdout.reconfigure(encoding="utf-8")
except: pass


# ═══════════════════════════════════════════════════════════════════════
# READ ALL LARGE FILES ONCE
# ═══════════════════════════════════════════════════════════════════════

print("── Reading step1 sample (once) ──")
s1 = pd.read_parquet(_latest("step1_sample")/"sample.parquet",
    columns=["gvkey","cal_yr_qtr","atq","fic100_industry_id"])
s1["gvkey"] = s1["gvkey"].astype(str).str.zfill(6)
print(f"  {len(s1):,} rows, {s1['gvkey'].nunique():,} firms")

print("── Computing T8 CASH (once) ──")
cash_df = pq.read_table(COMP, columns=["gvkey","datadate","curcdq","loc","consol",
    "indfmt","datafmt","atq","cheq"]).to_pandas()
cash_df["datadate"] = pd.to_datetime(cash_df["datadate"], errors="coerce")
cash_df = cash_df[(cash_df["datadate"]>=BUFFER_LO)&(cash_df["datadate"]<=WIN_HI_DATE)]
cash_df = cash_df[(cash_df["curcdq"]=="USD")&(cash_df["loc"]=="USA")&(cash_df["consol"]=="C")
          &(cash_df["indfmt"]=="INDL")&(cash_df["datafmt"]=="STD")].copy()
for c in ("atq","cheq"): cash_df[c] = pd.to_numeric(cash_df[c], errors="coerce")
cash_df["gvkey"] = cash_df["gvkey"].astype("int64").astype(str).str.zfill(6)
cash_df["cal_yr_qtr"] = (cash_df["datadate"].dt.year*10+cash_df["datadate"].dt.quarter).astype("int64")
cash_df = cash_df.sort_values(["gvkey","cal_yr_qtr","datadate"], kind="stable")
cash_df = cash_df.drop_duplicates(["gvkey","cal_yr_qtr"], keep="last")
src = cash_df[["gvkey","cal_yr_qtr","atq","cheq"]].rename(
    columns={"cal_yr_qtr":"_pq","atq":"atq_l1","cheq":"cheq_l1"})
cash_df["_pq"] = cash_df["cal_yr_qtr"].map(_prev_q).astype("int64")
cash_df = cash_df.merge(src, on=["gvkey","_pq"], how="left").drop(columns="_pq")
cash_df["denom"] = cash_df["atq_l1"] - cash_df["cheq_l1"]
cash_df = cash_df[cash_df["cheq"].notna()&(cash_df["denom"]>0)].copy()
cash_df["CASH"] = cash_df["cheq"]/cash_df["denom"]
cash_t8 = cash_df[["gvkey","cal_yr_qtr","CASH"]].copy(); del cash_df
print(f"  {len(cash_t8):,} firm-qtrs")

print("── Building controls (once) ──")
# Build controls on full step1 sample
base = s1.merge(cash_t8, on=["gvkey","cal_yr_qtr"], how="inner")
del cash_t8
base = base[base["atq"]>0].copy()
base["log_assets"] = np.log(base["atq"])
firm_cols = []
for cls in FIRM_BUILDERS:
    b = _build(cls); col = [c for c in b.columns if c not in ("gvkey","cal_yr_qtr")][0]
    base = base.merge(_calendar_lag1(b, col), on=["gvkey","cal_yr_qtr"], how="left")
    firm_cols.append(col)
base = base.merge(_calendar_lag1(
    base[["gvkey","cal_yr_qtr","log_assets"]], "log_assets").rename(
    columns={"log_assets":"log_assets_l1"}), on=["gvkey","cal_yr_qtr"], how="left")
firm_cols.append("log_assets_l1")
base = base.merge(_statsum_meanest_z(), on=["gvkey","cal_yr_qtr"], how="left")
print(f"  base panel: {len(base):,} rows, {base['gvkey'].nunique():,} firms")

# FE codes (shared)
base["indqtr_code"] = ((base["fic100_industry_id"].astype("int64").astype(str)
    +"_"+base["cal_yr_qtr"].astype(str)).astype("category").cat.codes)

# ═══════════════════════════════════════════════════════════════════════
# TREATMENT LOADING
# ═══════════════════════════════════════════════════════════════════════

def _load_treatment(kind: str):
    if kind == "market":
        td = _latest("step3_treatment")
        t = pd.read_parquet(td/"treatment.parquet")
        t["gvkey"] = t["gvkey"].astype(str).str.zfill(6)
        t = t[t["group"].isin(["treated","control"])].copy()
        t["HIGH_UK_EXPOSURE"] = (t["group"]=="treated").astype(int)
    else:
        td = _latest("step3b3_textual_treatment_sec17")
        t = pd.read_parquet(td/"treatment_textual.parquet")
        t["gvkey"] = t["gvkey"].astype(str).str.zfill(6)
    return t, td.name


# ═══════════════════════════════════════════════════════════════════════
# VARIANT RUNNER
# ═══════════════════════════════════════════════════════════════════════

def _fit(df, reg_cols):
    from linearmodels.panel import PanelOLS
    sub = df.dropna(subset=["CASH","indqtr_code"]+reg_cols).copy()
    if len(sub)==0: return None
    pdat = sub.set_index(["gvkey","cal_yr_qtr"]).sort_index()
    try:
        res = PanelOLS(pdat["CASH"], pdat[reg_cols], entity_effects=True,
                       other_effects=pdat["indqtr_code"], drop_absorbed=True
                       ).fit(cov_type="clustered", cluster_entity=True, cluster_time=True)
    except Exception as e:
        return {"error": str(e)}
    return {"delta": float(res.params["POST_x_HIGH"]),
            "se": float(res.std_errors["POST_x_HIGH"]),
            "t": float(res.tstats["POST_x_HIGH"]),
            "p": float(res.pvalues["POST_x_HIGH"]),
            "nobs": int(res.nobs), "nfirms": sub["gvkey"].nunique(),
            "r2w": float(res.rsquared_within)}


def make_subset(base_panel, treatment_df, post_quarters, pre_quarters=None):
    """Merge treatment, subset to relevant quarters, winsorize CASH."""
    tt = treatment_df.copy(); tt["gvkey"] = tt["gvkey"].astype(str).str.zfill(6)
    df = base_panel.merge(tt[["gvkey","HIGH_UK_EXPOSURE"]], on="gvkey", how="inner")
    if pre_quarters is not None:
        df = df[df["cal_yr_qtr"].isin(pre_quarters + post_quarters)]
    df["POST"] = df["cal_yr_qtr"].isin(post_quarters).astype(int)
    # Winsorize CASH within quarter on this sample
    df["CASH"] = df.groupby("cal_yr_qtr", observed=True)["CASH"].transform(
        lambda s: s.clip(s.quantile(0.01), s.quantile(0.99)))
    df["POST_x_HIGH"] = (df["POST"]*df["HIGH_UK_EXPOSURE"]).astype(float)
    return df


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

print(f"\n{'='*72}\nTASK 22: Shared-machinery DiD — both treatments\n{'='*72}")

all_results = []

for kind, label in [("market", "Market (β^UK)"), ("textual", "Textual §1+7")]:
    t_df, t_src = _load_treatment(kind)
    nT = int((t_df["HIGH_UK_EXPOSURE"]==1).sum()); nC = int((t_df["HIGH_UK_EXPOSURE"]==0).sum())
    print(f"\n── {label}  T={nT:,} C={nC:,}  src={t_src} ──")

    # 22a: Full panel
    df = make_subset(base, t_df, FULL_POST)
    r = _fit(df, ["POST_x_HIGH"]+firm_cols+["cons_fwd"])
    for kk in ["treatment","variant","controls"]: r[kk] = ""
    r["treatment"] = kind; r["variant"] = "full-panel"; r["controls"] = "full"
    all_results.append(r)
    if r and "error" not in r:
        print(f"  full-panel: δ={r['delta']:+.5f} SE={r['se']:.5f} "
              f"t={r['t']:+.3f} p={r['p']:.4f} N={r['nobs']:,}")

    # 22a: 4-quarter window
    df4 = make_subset(base, t_df, Q4_POST, Q4_PRE)
    r = _fit(df4, ["POST_x_HIGH"]+firm_cols+["cons_fwd"])
    r["treatment"] = kind; r["variant"] = "4q-window"; r["controls"] = "full"
    all_results.append(r)
    if r and "error" not in r:
        print(f"  4q-window: δ={r['delta']:+.5f} SE={r['se']:.5f} "
              f"t={r['t']:+.3f} p={r['p']:.4f} N={r['nobs']:,}")

    # 22b: no-Consensus (full panel)
    no_cons = [c for c in (["POST_x_HIGH"]+firm_cols+["cons_fwd"]) if c != "cons_fwd"]
    r = _fit(df, no_cons)
    r["treatment"] = kind; r["variant"] = "no-Consensus"; r["controls"] = "no-cons"
    all_results.append(r)
    if r and "error" not in r:
        print(f"  no-Consensus: δ={r['delta']:+.5f} SE={r['se']:.5f} "
              f"t={r['t']:+.3f} p={r['p']:.4f} N={r['nobs']:,}")

    # 22b: no-TobinQ (full panel, keep consensus)
    no_q = [c for c in (["POST_x_HIGH"]+firm_cols+["cons_fwd"]) if "tobins_q" not in c.lower()]
    r = _fit(df, no_q)
    r["treatment"] = kind; r["variant"] = "no-TobinQ"; r["controls"] = "no-q"
    all_results.append(r)
    if r and "error" not in r:
        print(f"  no-TobinQ: δ={r['delta']:+.5f} SE={r['se']:.5f} "
              f"t={r['t']:+.3f} p={r['p']:.4f} N={r['nobs']:,}")

# ── SIDE-BY-SIDE ──────────────────────────────────────────────────────
print(f"\n{'='*78}")
print("SIDE-BY-SIDE — BOTH TREATMENTS")
print(f"{'='*78}")
print(f"{'Treatment':<14} {'Variant':<14} {'δ':>10} {'SE':>8} {'t':>7} {'p':>7} {'N':>8} {'firms':>6} {'R²w':>6}")
print("-"*77)
for r in all_results:
    if r and "error" not in r:
        print(f"{r['treatment']:<14} {r['variant']:<14} {r['delta']:>+10.5f} {r['se']:>8.5f} "
              f"{r['t']:>+7.3f} {r['p']:>7.4f} {r['nobs']:>8,} {r['nfirms']:>6,} {r['r2w']:>6.4f}")
print(f"{'Paper market':<14} {'T8 col.1':<14} {+0.231:>+10.3f} {0.047:>8.3f} {'***':>7} {'—':>7} {17170:>8,} {'—':>6} {'—':>6}")
print(f"{'Paper textual':<14} {'T8 col.2':<14} {+0.357:>+10.3f} {0.062:>8.3f} {'***':>7} {'—':>7} {24195:>8,} {'—':>6} {'—':>6}")

od = ROOT/"outputs"/"campello_rebuild"/"_diag_t22"
od.mkdir(parents=True, exist_ok=True)
ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
(od/f"results_{ts}.json").write_text(json.dumps(all_results, indent=2, default=str))
print(f"\n→ {od / f'results_{ts}.json'}")
