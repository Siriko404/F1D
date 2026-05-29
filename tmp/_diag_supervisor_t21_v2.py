"""Supervisor Task 21 v2: Vectorized winsorization sweep.
Build DiD panel ONCE, swap CASH column per variant. Memory-aware.
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


def _build_did_panel():
    """Build full DiD panel ONCE. Returns (sub_dropped, nT, nC)."""
    from linearmodels.panel import PanelOLS

    s1 = pd.read_parquet(_latest("step1_sample")/"sample.parquet",
                         columns=["gvkey","cal_yr_qtr","atq","fic100_industry_id"])
    s1["gvkey"] = s1["gvkey"].astype(str).str.zfill(6)

    s3b = _latest("step3b3_textual_treatment_sec17")
    tt = pd.read_parquet(s3b/"treatment_textual.parquet")
    tt["gvkey"] = tt["gvkey"].astype(str).str.zfill(6)
    tt = tt[tt["group"].isin(["treated","control"])].copy()
    tt["HIGH_UK_EXPOSURE"] = (tt["group"]=="treated").astype(int)

    panel = s1.merge(tt[["gvkey","HIGH_UK_EXPOSURE"]], on="gvkey", how="inner")
    panel["POST"] = panel["cal_yr_qtr"].isin(POST_Q).astype(int)
    panel = panel[panel["atq"]>0].copy()
    panel["log_assets"] = np.log(panel["atq"])

    firm_cols = []
    for cls in FIRM_BUILDERS:
        b = _build(cls); col = [c for c in b.columns if c not in ("gvkey","cal_yr_qtr")][0]
        panel = panel.merge(_calendar_lag1(b, col), on=["gvkey","cal_yr_qtr"], how="left")
        firm_cols.append(col)
    panel = panel.merge(_calendar_lag1(
        panel[["gvkey","cal_yr_qtr","log_assets"]], "log_assets").rename(
        columns={"log_assets":"log_assets_l1"}), on=["gvkey","cal_yr_qtr"], how="left")
    firm_cols.append("log_assets_l1")

    panel = panel.merge(_statsum_meanest_z(), on=["gvkey","cal_yr_qtr"], how="left")
    panel["POST_x_HIGH"] = (panel["POST"]*panel["HIGH_UK_EXPOSURE"]).astype(float)
    panel["indqtr_code"] = ((panel["fic100_industry_id"].astype("int64").astype(str)
                             +"_"+panel["cal_yr_qtr"].astype(str)).astype("category").cat.codes)

    # Drop rows where controls/consensus missing (before CASH merge)
    reg_cols = ["POST_x_HIGH"] + firm_cols + ["cons_fwd"]
    panel = panel.dropna(subset=["indqtr_code"]+reg_cols)
    return panel, reg_cols, int((panel["HIGH_UK_EXPOSURE"]==1).sum()), int((panel["HIGH_UK_EXPOSURE"]==0).sum())


def _cash_raw():
    """Read Compustat once, build raw T8 ratio (no winsor)."""
    df = pq.read_table(COMP, columns=["gvkey","datadate","curcdq","loc",
                       "consol","indfmt","datafmt","atq","cheq"]).to_pandas()
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
    return df[["gvkey","cal_yr_qtr","CASH","cheq","cheq_l1","denom"]]


def _apply_winsor_and_fit(panel, reg_cols, cash_df, w_level, variant_label):
    """Merge CASH (with winsor variant), run PanelOLS. Returns result dict."""
    from linearmodels.panel import PanelOLS

    df = panel.merge(cash_df[["gvkey","cal_yr_qtr","CASH"]], on=["gvkey","cal_yr_qtr"], how="inner")
    sub = df.dropna(subset=["CASH"]).copy()
    pdat = sub.set_index(["gvkey","cal_yr_qtr"]).sort_index()
    nf = sub["gvkey"].nunique()

    res = PanelOLS(pdat["CASH"], pdat[reg_cols], entity_effects=True,
                   other_effects=pdat["indqtr_code"], drop_absorbed=True
                   ).fit(cov_type="clustered", cluster_entity=True, cluster_time=True)
    b = float(res.params["POST_x_HIGH"]); se = float(res.std_errors["POST_x_HIGH"])
    t = float(res.tstats["POST_x_HIGH"]); p = float(res.pvalues["POST_x_HIGH"])
    cash_mean = float(sub["CASH"].mean()); cash_sd = float(sub["CASH"].std())
    pcts = {q: float(sub["CASH"].quantile(q)) for q in [0.01,0.05,0.25,0.50,0.75,0.95,0.99]}
    return {"label": variant_label, "winsor": f"{w_level*100:.0f}%",
            "delta": b, "se": se, "t": t, "p": p, "nobs": int(res.nobs),
            "nfirms": int(nf), "r2w": float(res.rsquared_within),
            "cash_mean": cash_mean, "cash_sd": cash_sd, "cash_pcts": pcts}


if __name__ == "__main__":
    print("="*64)
    print("TASK 21 v2: Vectorized winsorization sweep")
    print("="*64)

    # ── Build ONCE ─────────────────────────────────────────────────────
    print("\n── Building DiD panel (once) ──")
    panel, reg_cols, nT, nC = _build_did_panel()
    print(f"  panel: {len(panel):,} rows, {panel['gvkey'].nunique():,} firms  "
          f"T={nT:,} C={nC:,}")

    print("\n── Reading Compustat (once) ──")
    cash_raw = _cash_raw()
    print(f"  raw T8: {len(cash_raw):,} firm-qtrs  "
          f"μ={float(cash_raw['CASH'].mean()):.2f}  σ={float(cash_raw['CASH'].std()):.2f}  "
          f"p50={float(cash_raw['CASH'].median()):.4f}")

    results = []

    # ── FINAL-RATIO WINSOR SWEEP ───────────────────────────────────────
    for w in [0.01, 0.02, 0.05]:
        cash = cash_raw.copy()
        cash["CASH"] = cash.groupby("cal_yr_qtr", observed=True)["CASH"].transform(
            lambda s: s.clip(s.quantile(w), s.quantile(1-w)))
        r = _apply_winsor_and_fit(panel, reg_cols, cash, w, f"ratio-w{w*100:.0f}%")
        results.append(r)
        print(f"  {r['label']}: CASH σ={r['cash_sd']:.4f}  p99={r['cash_pcts'][0.99]:.4f}  "
              f"δ={r['delta']:+.5f}  SE={r['se']:.5f}  t={r['t']:+.3f}  "
              f"p={r['p']:.4f}  N={r['nobs']:,}")

    # ── COMPONENT WINSOR ────────────────────────────────────────────────
    cash = cash_raw.copy()
    for col in ["cheq","cheq_l1","denom"]:
        cash[col] = cash.groupby("cal_yr_qtr", observed=True)[col].transform(
            lambda s: s.clip(s.quantile(0.01), s.quantile(0.99)))
    cash["CASH"] = cash["cheq"]/cash["denom"]
    cash["CASH"] = cash.groupby("cal_yr_qtr", observed=True)["CASH"].transform(
        lambda s: s.clip(s.quantile(0.01), s.quantile(0.99)))
    r = _apply_winsor_and_fit(panel, reg_cols, cash, 0.01, "comp-w1%+ratio-w1%")
    results.append(r)
    print(f"  {r['label']}: CASH σ={r['cash_sd']:.4f}  p99={r['cash_pcts'][0.99]:.4f}  "
          f"δ={r['delta']:+.5f}  SE={r['se']:.5f}  t={r['t']:+.3f}  "
          f"p={r['p']:.4f}  N={r['nobs']:,}")

    # ── SIDE-BY-SIDE ────────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print("SIDE-BY-SIDE")
    print(f"{'='*70}")
    print(f"{'Variant':<22} {'σ':>8} {'p50':>7} {'p99':>7} {'δ':>10} {'SE':>8} {'t':>7} {'p':>7} {'N':>8}")
    print("-"*83)
    for r in results:
        print(f"{r['label']:<22} {r['cash_sd']:>8.4f} {r['cash_pcts'][0.50]:>7.4f} "
              f"{r['cash_pcts'][0.99]:>7.4f} {r['delta']:>+10.5f} {r['se']:>8.5f} "
              f"{r['t']:>+7.3f} {r['p']:>7.4f} {r['nobs']:>8,}")
    print(f"{'Paper T1 (Table 1)':<22} {0.25:>8.2f} {0.12:>7.2f} {'—':>7} "
          f"{'+0.357':>10} {0.062:>8} {'***':>7} {'—':>7} {24195:>8,}")

    od = ROOT/"outputs"/"campello_rebuild"/"_diag_t21"
    od.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    (od/f"results_{ts}.json").write_text(json.dumps(results, indent=2, default=str))
    print(f"\n→ {od/f'results_{ts}.json'}")
