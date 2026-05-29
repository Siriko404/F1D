"""Supervisor Task 22: Shared-machinery DiD — both treatments (market + textual).

22a: 4-quarter window (2015:Q3-Q4 pre, 2016:Q3-Q4 post)
22b: Drop Consensus_EPS, then Tobin's Q

Runs on BOTH treatments with T8 DV. Goal: find shared lever that scales
BOTH δ's (market: +0.231*** target, textual: +0.357*** target).
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

# 4-quarter window quarters
Q4_PRE = [20153, 20154]; Q4_POST = [20163, 20164]


def _cash_dv_t8():
    df = pq.read_table(COMP, columns=["gvkey","datadate","curcdq","loc","consol",
                       "indfmt","datafmt","atq","cheq"]).to_pandas()
    df["datadate"] = pd.to_datetime(df["datadate"], errors="coerce")
    df = df[(df["datadate"]>=BUFFER_LO)&(df["datadate"]<=WIN_HI_DATE)]
    df = df[(df["curcdq"]=="USD")&(df["loc"]=="USA")&(df["consol"]=="C")
            &(df["indfmt"]=="INDL")&(df["datafmt"]=="STD")].copy()
    for c in ("atq","cheq"): df[c] = pd.to_numeric(df[c], errors="coerce")
    df["gvkey"] = df["gvkey"].astype("int64").astype(str).str.zfill(6)
    df["cal_yr_qtr"] = (df["datadate"].dt.year*10+df["datadate"].dt.quarter).astype("int64")
    df = df.sort_values(["gvkey","cal_yr_qtr","datadate"], kind="stable")
    df = df.drop_duplicates(["gvkey","cal_yr_qtr"], keep="last")
    src = df[["gvkey","cal_yr_qtr","atq","cheq"]].rename(
        columns={"cal_yr_qtr":"_pq","atq":"atq_l1","cheq":"cheq_l1"})
    df["_pq"] = df["cal_yr_qtr"].map(_prev_q).astype("int64")
    df = df.merge(src, on=["gvkey","_pq"], how="left").drop(columns="_pq")
    df["denom"] = df["atq_l1"] - df["cheq_l1"]
    df = df[df["cheq"].notna()&(df["denom"]>0)].copy()
    df["CASH"] = df["cheq"]/df["denom"]
    return df[["gvkey","cal_yr_qtr","CASH"]]


def _load_treatment(kind: str):
    """Load treatment assignment. kind='market' or 'textual'."""
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
        # already has HIGH_UK_EXPOSURE
    return t, td.name


def _build_panel(treatment_df, restrict_4q: bool):
    """Build DiD panel, optionally restricted to 4-quarter window."""
    s1 = pd.read_parquet(_latest("step1_sample")/"sample.parquet",
                         columns=["gvkey","cal_yr_qtr","atq","fic100_industry_id"])
    s1["gvkey"] = s1["gvkey"].astype(str).str.zfill(6)
    if restrict_4q:
        s1 = s1[s1["cal_yr_qtr"].isin(Q4_PRE + Q4_POST)]

    tt = treatment_df.copy(); tt["gvkey"] = tt["gvkey"].astype(str).str.zfill(6)
    panel = s1.merge(tt[["gvkey","HIGH_UK_EXPOSURE"]], on="gvkey", how="inner")
    panel["POST"] = panel["cal_yr_qtr"].isin(Q4_POST if restrict_4q else POST_Q).astype(int)
    df = panel.merge(_cash_dv_t8(), on=["gvkey","cal_yr_qtr"], how="inner")
    df = df[df["atq"]>0].copy(); df["log_assets"] = np.log(df["atq"])

    firm_cols = []
    for cls in FIRM_BUILDERS:
        b = _build(cls); col = [c for c in b.columns if c not in ("gvkey","cal_yr_qtr")][0]
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
    return df, firm_cols


def _fit(df, reg_cols):
    from linearmodels.panel import PanelOLS
    sub = df.dropna(subset=["CASH","indqtr_code"]+reg_cols).copy()
    if len(sub)==0: return None
    pdat = sub.set_index(["gvkey","cal_yr_qtr"]).sort_index()
    nf = sub["gvkey"].nunique()
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
            "nobs": int(res.nobs), "nfirms": int(nf),
            "r2w": float(res.rsquared_within)}


if __name__ == "__main__":
    print("="*72)
    print("TASK 22: Shared-machinery DiD — both treatments")
    print("="*72)

    all_results = []

    for kind, label in [("market", "Market (β^UK)"), ("textual", "Textual §1+7")]:
        t_df, t_src = _load_treatment(kind)
        nT = int((t_df["HIGH_UK_EXPOSURE"]==1).sum())
        nC = int((t_df["HIGH_UK_EXPOSURE"]==0).sum())
        print(f"\n── {label}  T={nT:,} C={nC:,}  src={t_src} ──")

        # 22a: Full panel + 4q window
        for restrict_4q, wlabel in [(False, "full-panel"), (True, "4q-window")]:
            df, fc = _build_panel(t_df, restrict_4q)
            r = _fit(df, ["POST_x_HIGH"]+fc+["cons_fwd"])
            r["treatment"] = kind; r["variant"] = wlabel; r["controls"] = "full"
            all_results.append(r)
            if r and "error" not in r:
                print(f"  {wlabel}: δ={r['delta']:+.5f} SE={r['se']:.5f} "
                      f"t={r['t']:+.3f} p={r['p']:.4f} N={r['nobs']:,} "
                      f"firms={r['nfirms']:,} R²w={r['r2w']:.4f}")
            else:
                print(f"  {wlabel}: ERROR={r}")

        # 22b: Drop controls (full panel only)
        df_full, fc = _build_panel(t_df, restrict_4q=False)
        base_cols = ["POST_x_HIGH"] + fc + ["cons_fwd"]

        # no Consensus_EPS
        no_cons = [c for c in base_cols if c != "cons_fwd"]
        r = _fit(df_full, no_cons)
        r["treatment"] = kind; r["variant"] = "no-Consensus"; r["controls"] = "no-cons"
        all_results.append(r)
        if r and "error" not in r:
            print(f"  no-Consensus: δ={r['delta']:+.5f} SE={r['se']:.5f} "
                  f"t={r['t']:+.3f} p={r['p']:.4f} N={r['nobs']:,}")

        # no Tobin's Q (keep Consensus)
        no_q = [c for c in base_cols if "tobins_q" not in c.lower()]
        r_q = _fit(df_full, no_q)
        if r_q:
            r_q["treatment"] = kind; r_q["variant"] = "no-TobinQ"; r_q["controls"] = "no-q"
            all_results.append(r_q)
            if "error" not in r_q:
                print(f"  no-TobinQ: δ={r_q['delta']:+.5f} SE={r_q['se']:.5f} "
                      f"t={r_q['t']:+.3f} p={r_q['p']:.4f} N={r_q['nobs']:,}")

    # ── SIDE-BY-SIDE ──────────────────────────────────────────────────
    print(f"\n{'='*80}")
    print("SIDE-BY-SIDE — BOTH TREATMENTS")
    print(f"{'='*80}")
    print(f"{'Treatment':<14} {'Variant':<14} {'δ':>10} {'SE':>8} {'t':>7} {'p':>7} {'N':>8} {'firms':>6} {'R²w':>6}")
    print("-"*79)
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
