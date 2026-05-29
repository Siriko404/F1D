"""Supervisor Tasks 14+15: Textual DiD with T8 net-of-cash DV + §1+7 variant.

Task 14: full-filing textual (3,037T/278C) DiD with T8 DV cheq/(atq_l1 - cheq_l1)
Task 15: §1+7 textual (1,458T/465C) DiD with same T8 DV
Also runs T1 DV for both variants as comparison.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "campello_rebuild"))

from step7_fullpanel_hypothesis import (
    FIRM_BUILDERS, POST_Q, WINSOR, _build, _calendar_lag1, _latest, _prev_q,
)

COMP = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
BUFFER_LO = pd.Timestamp("2008-01-01")
WIN_HI_DATE = pd.Timestamp("2016-12-31")

# Consensus
_p = ROOT / "scripts" / "campello_rebuild" / "_build_final_did_statsum_consensus.py"
_s = importlib.util.spec_from_file_location("_fin", _p)
_fin = importlib.util.module_from_spec(_s)
_s.loader.exec_module(_fin)
_statsum_meanest_z = _fin._statsum_meanest_z

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ═══════════════════════════════════════════════════════════════════════
# DV BUILDERS
# ═══════════════════════════════════════════════════════════════════════

def _cash_dv_t1() -> pd.DataFrame:
    """T1 DV: CASH = cheq_t / atq_{t-1} (Table 1 / step7 canonical)."""
    df = pq.read_table(COMP, columns=["gvkey","datadate","curcdq","loc",
                       "consol","indfmt","datafmt","atq","cheq"]).to_pandas()
    df["datadate"] = pd.to_datetime(df["datadate"], errors="coerce")
    df = df[(df["datadate"] >= BUFFER_LO) & (df["datadate"] <= WIN_HI_DATE)]
    df = df[(df["curcdq"]=="USD") & (df["loc"]=="USA") & (df["consol"]=="C")
            & (df["indfmt"]=="INDL") & (df["datafmt"]=="STD")].copy()
    for c in ("atq","cheq"): df[c] = pd.to_numeric(df[c], errors="coerce")
    df["gvkey"] = df["gvkey"].astype("int64").astype(str).str.zfill(6)
    df["cal_yr_qtr"] = (df["datadate"].dt.year*10+df["datadate"].dt.quarter).astype("int64")
    df = df.sort_values(["gvkey","cal_yr_qtr","datadate"], kind="stable")
    df = df.drop_duplicates(["gvkey","cal_yr_qtr"], keep="last")
    src = df[["gvkey","cal_yr_qtr","atq"]].rename(columns={"cal_yr_qtr":"_pq","atq":"atq_l1"})
    df["_pq"] = df["cal_yr_qtr"].map(_prev_q).astype("int64")
    df = df.merge(src, on=["gvkey","_pq"], how="left").drop(columns="_pq")
    df = df[df["cheq"].notna() & (df["atq_l1"]>0)].copy()
    df["CASH"] = df["cheq"] / df["atq_l1"]
    return df[["gvkey","cal_yr_qtr","CASH"]]


def _cash_dv_t8() -> pd.DataFrame:
    """T8 DV: CASH = cheq_t / (atq_{t-1} - cheq_{t-1}) (Table 8 caption, step5)."""
    df = pq.read_table(COMP, columns=["gvkey","datadate","curcdq","loc",
                       "consol","indfmt","datafmt","atq","cheq"]).to_pandas()
    df["datadate"] = pd.to_datetime(df["datadate"], errors="coerce")
    df = df[(df["datadate"] >= BUFFER_LO) & (df["datadate"] <= WIN_HI_DATE)]
    df = df[(df["curcdq"]=="USD") & (df["loc"]=="USA") & (df["consol"]=="C")
            & (df["indfmt"]=="INDL") & (df["datafmt"]=="STD")].copy()
    for c in ("atq","cheq"): df[c] = pd.to_numeric(df[c], errors="coerce")
    df["gvkey"] = df["gvkey"].astype("int64").astype(str).str.zfill(6)
    df["cal_yr_qtr"] = (df["datadate"].dt.year*10+df["datadate"].dt.quarter).astype("int64")
    df = df.sort_values(["gvkey","cal_yr_qtr","datadate"], kind="stable")
    df = df.drop_duplicates(["gvkey","cal_yr_qtr"], keep="last")
    # lag BOTH atq and cheq for denominator
    src = df[["gvkey","cal_yr_qtr","atq","cheq"]].rename(
        columns={"cal_yr_qtr":"_pq","atq":"atq_l1","cheq":"cheq_l1"})
    df["_pq"] = df["cal_yr_qtr"].map(_prev_q).astype("int64")
    df = df.merge(src, on=["gvkey","_pq"], how="left").drop(columns="_pq")
    df["denom"] = df["atq_l1"] - df["cheq_l1"]
    df = df[df["cheq"].notna() & (df["denom"]>0)].copy()
    df["CASH"] = df["cheq"] / df["denom"]
    return df[["gvkey","cal_yr_qtr","CASH"]]


# ═══════════════════════════════════════════════════════════════════════
# RUN DiD
# ═══════════════════════════════════════════════════════════════════════

def run_did(treatment_dir: str, dv_fn, dv_label: str, label: str):
    """Run eq-(14) DiD for given treatment source and DV builder."""
    from linearmodels.panel import PanelOLS

    s1 = pd.read_parquet(_latest("step1_sample") / "sample.parquet",
                         columns=["gvkey","cal_yr_qtr","atq","fic100_industry_id"])
    s1["gvkey"] = s1["gvkey"].astype(str).str.zfill(6)

    s3 = _latest(treatment_dir)
    tt = pd.read_parquet(s3 / "treatment_textual.parquet")
    tt["gvkey"] = tt["gvkey"].astype(str).str.zfill(6)
    tt = tt[tt["group"].isin(["treated","control"])].copy()
    tt["HIGH_UK_EXPOSURE"] = (tt["group"]=="treated").astype(int)
    nT = int((tt.HIGH_UK_EXPOSURE==1).sum())
    nC = int((tt.HIGH_UK_EXPOSURE==0).sum())

    panel = s1.merge(tt[["gvkey","HIGH_UK_EXPOSURE"]], on="gvkey", how="inner")
    panel["POST"] = panel["cal_yr_qtr"].isin(POST_Q).astype(int)
    df = panel.merge(dv_fn(), on=["gvkey","cal_yr_qtr"], how="inner")
    df = df[df["atq"]>0].copy()
    df["log_assets"] = np.log(df["atq"])

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

    # Winsorize CASH within quarter
    df["CASH"] = df.groupby("cal_yr_qtr", observed=True)["CASH"].transform(
        lambda s: s.clip(s.quantile(WINSOR), s.quantile(1-WINSOR)))
    df["POST_x_HIGH"] = (df["POST"]*df["HIGH_UK_EXPOSURE"]).astype(float)
    df["indqtr_code"] = ((df["fic100_industry_id"].astype("int64").astype(str)
                          +"_"+df["cal_yr_qtr"].astype(str)).astype("category").cat.codes)

    cols = ["POST_x_HIGH"] + firm_cols + ["cons_fwd"]
    sub = df.dropna(subset=["CASH","indqtr_code"]+cols).copy()
    pdat = sub.set_index(["gvkey","cal_yr_qtr"]).sort_index()
    nf = sub["gvkey"].nunique()

    res = PanelOLS(pdat["CASH"], pdat[cols], entity_effects=True,
                   other_effects=pdat["indqtr_code"], drop_absorbed=True
                   ).fit(cov_type="clustered", cluster_entity=True,
                         cluster_time=True)
    b = float(res.params["POST_x_HIGH"])
    se = float(res.std_errors["POST_x_HIGH"])
    t = float(res.tstats["POST_x_HIGH"])
    p = float(res.pvalues["POST_x_HIGH"])

    cash_mean = float(sub["CASH"].mean())
    cash_sd = float(sub["CASH"].std())

    return {
        "label": label, "dv": dv_label,
        "treatment": treatment_dir, "src": s3.name,
        "nT": nT, "nC": nC,
        "delta": b, "se": se, "t": t, "p": p,
        "nobs": int(res.nobs), "nfirms": int(nf),
        "r2w": float(res.rsquared_within),
        "cash_mean": cash_mean, "cash_sd": cash_sd,
    }


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("="*72)
    print("TASKS 14+15: T8 net-of-cash DV | full-filing + §1+7 textual DiD")
    print("="*72)

    results = []

    # Task 14: full-filing, T8 DV
    print("\n── Task 14: full-filing × T8 DV ──")
    r = run_did("step3b_textual_treatment", _cash_dv_t8,
                "T8: cheq/(atq_l1-cheq_l1)", "full-filing T8")
    results.append(r)
    print(f"  δ={r['delta']:+.5f}  SE={r['se']:.5f}  t={r['t']:+.3f}  "
          f"p={r['p']:.4f}  N={r['nobs']:,}  firms={r['nfirms']:,}  "
          f"R²w={r['r2w']:.4f}  CASH_μ={r['cash_mean']:.4f}  σ={r['cash_sd']:.4f}")

    # Full-filing, T1 DV (comparison)
    print("\n── Comparison: full-filing × T1 DV ──")
    r = run_did("step3b_textual_treatment", _cash_dv_t1,
                "T1: cheq/atq_l1", "full-filing T1")
    results.append(r)
    print(f"  δ={r['delta']:+.5f}  SE={r['se']:.5f}  t={r['t']:+.3f}  "
          f"p={r['p']:.4f}  N={r['nobs']:,}  firms={r['nfirms']:,}  "
          f"R²w={r['r2w']:.4f}  CASH_μ={r['cash_mean']:.4f}  σ={r['cash_sd']:.4f}")

    # Task 15: §1+7, T8 DV
    print("\n── Task 15: §1+7 × T8 DV ──")
    r = run_did("step3b3_textual_treatment_sec17", _cash_dv_t8,
                "T8: cheq/(atq_l1-cheq_l1)", "§1+7 T8")
    results.append(r)
    print(f"  δ={r['delta']:+.5f}  SE={r['se']:.5f}  t={r['t']:+.3f}  "
          f"p={r['p']:.4f}  N={r['nobs']:,}  firms={r['nfirms']:,}  "
          f"R²w={r['r2w']:.4f}  CASH_μ={r['cash_mean']:.4f}  σ={r['cash_sd']:.4f}")

    # §1+7, T1 DV (comparison)
    print("\n── Comparison: §1+7 × T1 DV ──")
    r = run_did("step3b3_textual_treatment_sec17", _cash_dv_t1,
                "T1: cheq/atq_l1", "§1+7 T1")
    results.append(r)
    print(f"  δ={r['delta']:+.5f}  SE={r['se']:.5f}  t={r['t']:+.3f}  "
          f"p={r['p']:.4f}  N={r['nobs']:,}  firms={r['nfirms']:,}  "
          f"R²w={r['r2w']:.4f}  CASH_μ={r['cash_mean']:.4f}  σ={r['cash_sd']:.4f}")

    # ═══════════════════════════════════════════════════════════════════
    # SIDE-BY-SIDE
    # ═══════════════════════════════════════════════════════════════════
    print(f"\n{'='*72}")
    print("SIDE-BY-SIDE")
    print(f"{'='*72}")
    print(f"{'Variant':<22} {'DV':<28} {'δ':>8} {'SE':>8} {'t':>7} {'p':>7} {'N':>8} {'firms':>6} {'R²w':>6}")
    print("-"*106)
    for r in results:
        print(f"{r['label']:<22} {r['dv']:<28} {r['delta']:>+8.5f} {r['se']:>8.5f} "
              f"{r['t']:>+7.3f} {r['p']:>7.4f} {r['nobs']:>8,} {r['nfirms']:>6,} {r['r2w']:>6.4f}")
    print(f"{'Paper (T8 col.2)':<22} {'?':<28} {+0.357:>+8.3f} {0.062:>8.3f} {'?':>7} {'***':>7} {24195:>8,} {'?':>6} {0.24:>6.2f}")

    # Write results
    od = ROOT / "outputs" / "campello_rebuild" / "_diag_t14_t15"
    od.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    (od / f"results_{ts}.json").write_text(json.dumps(results, indent=2, default=str))
    print(f"\nwritten → {od / f'results_{ts}.json'}")
