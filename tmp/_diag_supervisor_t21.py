"""Supervisor Task 21: Winsorize FINAL T8 ratio at varying levels.

We already winsorize the final T8 ratio at 1% within quarter. σ stays at 1.17.
Test: sweep winsorization levels (1%, 2%, 5%) on the final T8 CASH ratio.
Gate: does σ→~0.25 AND δ→0.357 together?

Also test: winsorize cheq and denom BEFORE forming the ratio (component winsorization),
which is the paper's standard approach for ratio variables.
"""
from __future__ import annotations

import importlib.util, json, sys
from datetime import datetime
from pathlib import Path

import numpy as np, pandas as pd, pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "campello_rebuild"))

from step7_fullpanel_hypothesis import (
    FIRM_BUILDERS, POST_Q, WINSOR, _build, _calendar_lag1, _latest, _prev_q,
)

COMP = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
BUFFER_LO = pd.Timestamp("2008-01-01")
WIN_HI_DATE = pd.Timestamp("2016-12-31")

_p = ROOT / "scripts" / "campello_rebuild" / "_build_final_did_statsum_consensus.py"
_s = importlib.util.spec_from_file_location("_fin", _p); _fin = importlib.util.module_from_spec(_s)
_s.loader.exec_module(_fin); _statsum_meanest_z = _fin._statsum_meanest_z

try: sys.stdout.reconfigure(encoding="utf-8")
except: pass


def _cash_dv_t8_raw():
    """Raw T8 ratio WITHOUT any winsorization."""
    df = pq.read_table(COMP, columns=["gvkey","datadate","curcdq","loc","consol","indfmt","datafmt","atq","cheq"]).to_pandas()
    df["datadate"] = pd.to_datetime(df["datadate"], errors="coerce")
    df = df[(df["datadate"]>=BUFFER_LO)&(df["datadate"]<=WIN_HI_DATE)]
    df = df[(df["curcdq"]=="USD")&(df["loc"]=="USA")&(df["consol"]=="C")&(df["indfmt"]=="INDL")&(df["datafmt"]=="STD")].copy()
    for c in ("atq","cheq"): df[c] = pd.to_numeric(df[c], errors="coerce")
    df["gvkey"] = df["gvkey"].astype("int64").astype(str).str.zfill(6)
    df["cal_yr_qtr"] = (df["datadate"].dt.year*10+df["datadate"].dt.quarter).astype("int64")
    df = df.sort_values(["gvkey","cal_yr_qtr","datadate"], kind="stable").drop_duplicates(["gvkey","cal_yr_qtr"], keep="last")
    src = df[["gvkey","cal_yr_qtr","atq","cheq"]].rename(columns={"cal_yr_qtr":"_pq","atq":"atq_l1","cheq":"cheq_l1"})
    df["_pq"] = df["cal_yr_qtr"].map(_prev_q).astype("int64")
    df = df.merge(src, on=["gvkey","_pq"], how="left").drop(columns="_pq")
    df = df[df["cheq"].notna()].copy()
    # Drop rows where lagged values are NaN (match original _cash_dv_t8 behavior)
    df["denom"] = df["atq_l1"] - df["cheq_l1"]
    df = df[df["cheq"].notna() & (df["denom"]>0)].copy()
    df["CASH"] = df["cheq"] / df["denom"]
    return df[["gvkey","cal_yr_qtr","CASH","cheq","atq_l1","cheq_l1","denom"]]


def _cash_dv_t8_component_winsor(w: float):
    """Winsorize cheq, cheq_l1, denom BEFORE forming the ratio (final also winsor at w)."""
    df = _cash_dv_t8_raw()
    for col in ["cheq","cheq_l1","denom"]:
        df[col] = df.groupby("cal_yr_qtr", observed=True)[col].transform(
            lambda s: s.clip(s.quantile(w), s.quantile(1-w)))
    df["CASH"] = df["cheq"] / df["denom"]
    df["CASH"] = df.groupby("cal_yr_qtr", observed=True)["CASH"].transform(
        lambda s: s.clip(s.quantile(w), s.quantile(1-w)))
    return df[["gvkey","cal_yr_qtr","CASH"]]


def _cash_dv_t8_ratio_winsor(w: float):
    """Form the T8 ratio FIRST, then winsorize at level w."""
    df = _cash_dv_t8_raw()
    df["CASH"] = df.groupby("cal_yr_qtr", observed=True)["CASH"].transform(
        lambda s: s.clip(s.quantile(w), s.quantile(1-w)))
    return df[["gvkey","cal_yr_qtr","CASH"]]


def run_did(treatment_df, dv_fn, w_label, dv_label):
    from linearmodels.panel import PanelOLS
    s1 = pd.read_parquet(_latest("step1_sample")/"sample.parquet", columns=["gvkey","cal_yr_qtr","atq","fic100_industry_id"])
    s1["gvkey"] = s1["gvkey"].astype(str).str.zfill(6)
    tt = treatment_df.copy(); tt["gvkey"] = tt["gvkey"].astype(str).str.zfill(6)
    panel = s1.merge(tt[["gvkey","HIGH_UK_EXPOSURE"]], on="gvkey", how="inner")
    panel["POST"] = panel["cal_yr_qtr"].isin(POST_Q).astype(int)
    df = panel.merge(dv_fn, on=["gvkey","cal_yr_qtr"], how="inner")
    df = df[df["atq"]>0].copy(); df["log_assets"] = np.log(df["atq"])
    firm_cols = []
    for cls in FIRM_BUILDERS:
        b = _build(cls); col = [c for c in b.columns if c not in ("gvkey","cal_yr_qtr")][0]
        df = df.merge(_calendar_lag1(b, col), on=["gvkey","cal_yr_qtr"], how="left"); firm_cols.append(col)
    df = df.merge(_calendar_lag1(df[["gvkey","cal_yr_qtr","log_assets"]], "log_assets").rename(columns={"log_assets":"log_assets_l1"}), on=["gvkey","cal_yr_qtr"], how="left")
    firm_cols.append("log_assets_l1")
    df = df.merge(_statsum_meanest_z(), on=["gvkey","cal_yr_qtr"], how="left")
    # NOTE: dv_fn already handles winsorization. Don't re-winsorize.
    df["POST_x_HIGH"] = (df["POST"]*df["HIGH_UK_EXPOSURE"]).astype(float)
    df["indqtr_code"] = ((df["fic100_industry_id"].astype("int64").astype(str)+"_"+df["cal_yr_qtr"].astype(str)).astype("category").cat.codes)
    cols = ["POST_x_HIGH"] + firm_cols + ["cons_fwd"]
    sub = df.dropna(subset=["CASH","indqtr_code"]+cols).copy()
    pdat = sub.set_index(["gvkey","cal_yr_qtr"]).sort_index(); nf = sub["gvkey"].nunique()
    res = PanelOLS(pdat["CASH"], pdat[cols], entity_effects=True, other_effects=pdat["indqtr_code"], drop_absorbed=True).fit(cov_type="clustered", cluster_entity=True, cluster_time=True)
    b = float(res.params["POST_x_HIGH"]); se = float(res.std_errors["POST_x_HIGH"])
    t = float(res.tstats["POST_x_HIGH"]); p = float(res.pvalues["POST_x_HIGH"])
    cash_mean = float(sub["CASH"].mean()); cash_sd = float(sub["CASH"].std())
    cash_pcts = {q: float(sub["CASH"].quantile(q)) for q in [0.01,0.05,0.25,0.50,0.75,0.95,0.99]}
    return {"label": w_label, "dv": dv_label, "delta": b, "se": se, "t": t, "p": p,
            "nobs": int(res.nobs), "nfirms": int(nf), "r2w": float(res.rsquared_within),
            "cash_mean": cash_mean, "cash_sd": cash_sd, "cash_pcts": cash_pcts}


if __name__ == "__main__":
    print("="*72)
    print("TASK 21: Winsorization sweep — final T8 ratio at varying levels")
    print("="*72)

    # Load treatment (Compustat P-only §1+7, best match to paper's counts)
    s3b = _latest("step3b3_textual_treatment_sec17")
    tt = pd.read_parquet(s3b / "treatment_textual.parquet")
    tt["gvkey"] = tt["gvkey"].astype(str).str.zfill(6)
    tt = tt[tt["group"].isin(["treated","control"])].copy()
    tt["HIGH_UK_EXPOSURE"] = (tt["group"]=="treated").astype(int)
    print(f"Treatment: T={int((tt.HIGH_UK_EXPOSURE==1).sum()):,}  "
          f"C={int((tt.HIGH_UK_EXPOSURE==0).sum()):,}  src={s3b.name}")

    results = []

    # Check: show raw T8 distribution before ANY winsorization
    raw = _cash_dv_t8_raw()
    raw_stats = {q: float(raw["CASH"].quantile(q)) for q in [0.01,0.05,0.25,0.50,0.75,0.95,0.99]}
    print(f"\n── RAW T8 (no winsor) ──")
    print(f"  μ={float(raw['CASH'].mean()):.4f}  σ={float(raw['CASH'].std()):.4f}")
    print(f"  p1={raw_stats[0.01]:.4f}  p5={raw_stats[0.05]:.4f}  p25={raw_stats[0.25]:.4f}  "
          f"p50={raw_stats[0.50]:.4f}  p75={raw_stats[0.75]:.4f}  "
          f"p95={raw_stats[0.95]:.4f}  p99={raw_stats[0.99]:.4f}")

    # VARYING FINAL-RATIO WINSOR LEVELS
    for w, wlabel in [(0.01, "ratio-w1%"), (0.02, "ratio-w2%"), (0.05, "ratio-w5%")]:
        print(f"\n── {wlabel} ──")
        dv = _cash_dv_t8_ratio_winsor(w)
        r = run_did(tt, dv, wlabel, f"T8 ratio winsor {w*100:.0f}%")
        results.append(r)
        print(f"  CASH: μ={r['cash_mean']:.4f}  σ={r['cash_sd']:.4f}  "
              f"p50={r['cash_pcts'][0.50]:.4f}  p99={r['cash_pcts'][0.99]:.4f}")
        print(f"  δ={r['delta']:+.5f}  SE={r['se']:.5f}  t={r['t']:+.3f}  "
              f"p={r['p']:.4f}  N={r['nobs']:,}  firms={r['nfirms']:,}  "
              f"R²w={r['r2w']:.4f}")

    # COMPONENT WINSOR: winsorize cheq, atq_l1, cheq_l1, denom at 1% BEFORE ratio
    print(f"\n── component-w1% (winsor components then form ratio, final winsor 1%) ──")
    dv = _cash_dv_t8_component_winsor(0.01)
    r = run_did(tt, dv, "comp-w1%", "Components winsor 1% then ratio")
    results.append(r)
    print(f"  CASH: μ={r['cash_mean']:.4f}  σ={r['cash_sd']:.4f}  "
          f"p50={r['cash_pcts'][0.50]:.4f}  p99={r['cash_pcts'][0.99]:.4f}")
    print(f"  δ={r['delta']:+.5f}  SE={r['se']:.5f}  t={r['t']:+.3f}  "
          f"p={r['p']:.4f}  N={r['nobs']:,}  firms={r['nfirms']:,}  "
          f"R²w={r['r2w']:.4f}")

    # BASELINE (existing: ratio winsor 1%, what we already have)
    dv_base = _cash_dv_t8_ratio_winsor(0.01)
    r_base = run_did(tt, dv_base, "baseline-1%", "T8 ratio winsor 1% (current)")
    results.append(r_base)

    # Side-by-side
    print(f"\n{'='*72}")
    print("SIDE-BY-SIDE — CASH σ vs δ")
    print(f"{'='*72}")
    print(f"{'Method':<22} {'winsor':>7} {'CASH_μ':>8} {'CASH_σ':>8} {'p50':>7} {'p99':>7} {'δ':>10} {'SE':>8} {'t':>7} {'p':>7} {'N':>8}")
    print("-"*106)
    paper_s = {"CASH_μ":0.22, "CASH_σ":0.25, "p50":0.12}
    for r in results:
        print(f"{r['label']:<22} {r['dv']:>7} {r['cash_mean']:>8.4f} {r['cash_sd']:>8.4f} "
              f"{r['cash_pcts'][0.50]:>7.4f} {r['cash_pcts'][0.99]:>7.4f} "
              f"{r['delta']:>+10.5f} {r['se']:>8.5f} {r['t']:>+7.3f} "
              f"{r['p']:>7.4f} {r['nobs']:>8,}")
    print(f"{'Paper Table 1 (T1 DV)':<22} {'—':>7} {paper_s['CASH_μ']:>8.2f} {paper_s['CASH_σ']:>8.2f} "
          f"{paper_s['p50']:>7.2f} {'—':>7} "
          f"{'+0.357':>10} {'0.062':>8} {'***':>7} {'—':>7} {'24,195':>8}")

    od = ROOT / "outputs" / "campello_rebuild" / "_diag_t21"
    od.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    (od / f"results_{ts}.json").write_text(json.dumps(results, indent=2, default=str))
    print(f"\nwritten → {od / f'results_{ts}.json'}")
