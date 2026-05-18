"""STEP 8 — PLACEBO / pre-trend identification test (advisor-recommended).

Sina 2026-05-17 ("test all ways"); advisor: the highest discriminator
between "genuine rebuild outcome" and "unidentified contrast" — run
BEFORE any interpretive verdict. Paper-faithful (Campello's own Figure 5
is a parallel-trends exhibit). NOT an off-ramp.

DESIGN: identical to the confirmed full-panel Step 7 (same βᵁᴷ-tercile
treated+control firms, same HIGH_UK_EXPOSURE, same CASH DV, same 5 firm
controls lagged 1Q + macro absorbed + consensus, same FIRM FE + IND×QTR
FE, same double-clustered SE) — but the event is RELOCATED to a fully
pre-Brexit placebo date and the real event window is EXCLUDED:
  • panel restricted to cal_yr_qtr ≤ 2015Q4 (drops 2016 entirely, so the
    real Brexit window cannot contaminate the placebo)
  • PLACEBO POST dummy = 1 iff cal_yr_qtr ∈ {2014Q3, 2014Q4}
    (a fake "event" with NO Brexit present; same seasonal Q3–Q4 contrast)

DECISION RULE (advisor):
  • δ̂_placebo ≈ −0.03 (≈ the real −0.033) ⇒ identification BROKEN
    (pre-existing βᵁᴷ-correlated trend); real-window "effect" not cleanly
    identified — "non-replication" would not be the right framing.
  • δ̂_placebo ≈ 0 (NS) ⇒ identification CLEAN; the real-window −0.033 NS
    is data-driven; gap to Campello +0.231*** is a real spec/measurement
    question (βᵁᴷ proxy quality + 30% firm-count surplus vs 809).

Real full-panel (Step 7): δ̂ ≈ −0.033 NS, N 18,632 ≈ Campello 17,170.
Factual test only — NOT a replication verdict (gated on Sina; off-ramp
forbidden).

Everything else identical to verified Step 6/7 (CASH DV =
Table-8-caption cheq_t/(atq_{t-1}−cheq_{t-1}); 5 firm controls lagged 1Q;
macro absorbed by IND×QTR FE; consensus immaterial → forward variant;
FIRM FE + IND×QTR FE; SE double-clustered firm×qtr). ONLY the panel
restriction + placebo POST differ.

Output: outputs/campello_rebuild/step8_placebo/<ts>/
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
COMP = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
BUFFER_LO = pd.Timestamp("2008-01-01")
WIN_HI_DATE = pd.Timestamp("2016-12-31")
WINSOR = 0.01
POST_Q = [20143, 20144]      # PLACEBO fake event: 2014Q3-Q4 (no Brexit)
PRE_BREXIT_MAX_Q = 20154     # restrict panel ≤2015Q4 (exclude real event)
FIRM_BUILDERS = ["BrexitStockReturnBuilder", "BrexitTobinsQBuilder",
                 "BrexitCashFlowBuilder", "BrexitSalesGrowthBuilder"]


def _prev_q(yq: int) -> int:
    yr, q = yq // 10, yq % 10
    return (yr - 1) * 10 + 4 if q == 1 else yr * 10 + (q - 1)


def _latest(sub: str) -> Path:
    base = ROOT / "outputs" / "campello_rebuild" / sub
    return sorted(d for d in base.iterdir() if d.is_dir())[-1]


def _calendar_lag1(df: pd.DataFrame, col: str) -> pd.DataFrame:
    src = df[["gvkey", "cal_yr_qtr", col]].rename(
        columns={"cal_yr_qtr": "_pq", col: col + "_L"})
    tgt = df[["gvkey", "cal_yr_qtr"]].copy()
    tgt["_pq"] = tgt["cal_yr_qtr"].map(_prev_q).astype("int64")
    return (tgt.merge(src, on=["gvkey", "_pq"], how="left").drop(columns="_pq")
            .rename(columns={col + "_L": col}))


def _build(cls_name: str) -> pd.DataFrame:
    import importlib
    mod = {
        "BrexitStockReturnBuilder": "brexit_stock_return",
        "BrexitTobinsQBuilder": "brexit_tobins_q",
        "BrexitCashFlowBuilder": "brexit_cash_flow",
        "BrexitSalesGrowthBuilder": "brexit_sales_growth",
        "BrexitConsensusEPSBuilder": "brexit_consensus_eps",
    }[cls_name]
    m = importlib.import_module(f"f1d.shared.variables.{mod}")
    d = getattr(m, cls_name)().build(range(2009, 2017), root_path=ROOT).data.copy()
    if "gvkey" in d.columns:
        d["gvkey"] = d["gvkey"].astype(str).str.zfill(6)
    d["cal_yr_qtr"] = d["cal_yr_qtr"].astype("int64")
    return d


def _cash_dv() -> pd.DataFrame:
    df = pq.read_table(COMP, columns=["gvkey", "datadate", "curcdq", "loc",
                       "consol", "indfmt", "datafmt", "atq", "cheq"]).to_pandas()
    df["datadate"] = pd.to_datetime(df["datadate"], errors="coerce")
    df = df[(df["datadate"] >= BUFFER_LO) & (df["datadate"] <= WIN_HI_DATE)]
    df = df[(df["curcdq"] == "USD") & (df["loc"] == "USA")
            & (df["consol"] == "C") & (df["indfmt"] == "INDL")
            & (df["datafmt"] == "STD")].copy()
    for c in ("atq", "cheq"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["gvkey"] = df["gvkey"].astype("int64").astype(str).str.zfill(6)
    df["cal_yr_qtr"] = (df["datadate"].dt.year * 10
                        + df["datadate"].dt.quarter).astype("int64")
    df = (df.sort_values(["gvkey", "cal_yr_qtr", "datadate"], kind="stable")
            .drop_duplicates(["gvkey", "cal_yr_qtr"], keep="last"))
    src = df[["gvkey", "cal_yr_qtr", "atq", "cheq"]].rename(
        columns={"cal_yr_qtr": "_pq", "atq": "atq_l1", "cheq": "cheq_l1"})
    df["_pq"] = df["cal_yr_qtr"].map(_prev_q).astype("int64")
    df = df.merge(src, on=["gvkey", "_pq"], how="left").drop(columns="_pq")
    df["denom"] = df["atq_l1"] - df["cheq_l1"]
    df = df[df["cheq"].notna() & (df["denom"] > 0)].copy()
    df["CASH"] = df["cheq"] / df["denom"]
    return df[["gvkey", "cal_yr_qtr", "CASH"]]


def main() -> None:
    print("=== STEP 7 — HYPOTHESIS: eq-(14) on FULL sample-period panel ===\n")
    from linearmodels.panel import PanelOLS

    s1_dir = _latest("step1_sample")
    s3_dir = _latest("step3_treatment")
    s1 = pd.read_parquet(s1_dir / "sample.parquet",
                         columns=["gvkey", "cal_yr_qtr", "atq",
                                  "fic100_industry_id"])
    s1["gvkey"] = s1["gvkey"].astype(str).str.zfill(6)
    trt = pd.read_parquet(s3_dir / "treatment.parquet",
                          columns=["gvkey", "group", "in_step1"])
    trt["gvkey"] = trt["gvkey"].astype(str).str.zfill(6)
    tc = trt[trt["in_step1"] & trt["group"].isin(["treated", "control"])].copy()
    tc["HIGH_UK_EXPOSURE"] = (tc["group"] == "treated").astype(int)
    print(f"βᵁᴷ-tercile firms (treated+control): {len(tc):,} "
          f"(T={int((tc.HIGH_UK_EXPOSURE==1).sum()):,}, "
          f"C={int((tc.HIGH_UK_EXPOSURE==0).sum()):,})")

    # PLACEBO panel: same firms, but PRE-BREXIT ONLY (≤2015Q4 — real event
    # window 2016Q3-Q4 excluded so it cannot contaminate the placebo);
    # fake POST = 2014Q3-Q4.
    panel = (s1.merge(tc[["gvkey", "HIGH_UK_EXPOSURE"]], on="gvkey",
                      how="inner"))
    panel = panel[panel["cal_yr_qtr"] <= PRE_BREXIT_MAX_Q].copy()
    panel["POST"] = panel["cal_yr_qtr"].isin(POST_Q).astype(int)
    print(f"PLACEBO panel (pre-Brexit ≤2015Q4) firm-quarters: {len(panel):,} / "
          f"{panel['gvkey'].nunique():,} firms; "
          f"qtr range {int(panel.cal_yr_qtr.min())}–{int(panel.cal_yr_qtr.max())}; "
          f"fake POST=2014Q3-Q4 ({int(panel['POST'].sum()):,} fq)")

    cash = _cash_dv()
    df = panel.merge(cash, on=["gvkey", "cal_yr_qtr"], how="inner")
    df = df[df["atq"] > 0].copy()
    df["log_assets"] = np.log(df["atq"])

    firm_cols = []
    for cls in FIRM_BUILDERS:
        b = _build(cls)
        col = [c for c in b.columns if c not in ("gvkey", "cal_yr_qtr")][0]
        df = df.merge(_calendar_lag1(b, col), on=["gvkey", "cal_yr_qtr"],
                      how="left")
        firm_cols.append(col)
    df = df.merge(_calendar_lag1(df[["gvkey", "cal_yr_qtr", "log_assets"]],
                                 "log_assets").rename(
                  columns={"log_assets": "log_assets_l1"}),
                  on=["gvkey", "cal_yr_qtr"], how="left")
    firm_cols.append("log_assets_l1")

    cons = _build("BrexitConsensusEPSBuilder")
    cons = (cons.sort_values(["gvkey", "cal_yr_qtr"], kind="stable")
                .drop_duplicates(["gvkey", "cal_yr_qtr"], keep="last"))
    ccol = [c for c in cons.columns if c not in ("gvkey", "cal_yr_qtr")][0]
    df = df.merge(cons.rename(columns={ccol: "cons_fwd"}),
                  on=["gvkey", "cal_yr_qtr"], how="left")  # immaterial variant

    df["CASH"] = df.groupby("cal_yr_qtr", observed=True)["CASH"].transform(
        lambda s: s.clip(s.quantile(WINSOR), s.quantile(1 - WINSOR)))
    df["POST_x_HIGH"] = (df["POST"] * df["HIGH_UK_EXPOSURE"]).astype(float)
    df["indqtr_code"] = ((df["fic100_industry_id"].astype("int64").astype(str)
                          + "_" + df["cal_yr_qtr"].astype(str))
                         .astype("category").cat.codes)

    cols = ["POST_x_HIGH"] + firm_cols + ["cons_fwd"]
    sub = df.dropna(subset=["CASH", "indqtr_code"] + cols).copy()
    pdat = sub.set_index(["gvkey", "cal_yr_qtr"]).sort_index()
    print(f"\nestimation sample (full panel ∩ CASH ∩ controls): "
          f"{len(sub):,} fq / {sub['gvkey'].nunique():,} firms")

    res = PanelOLS(pdat["CASH"], pdat[cols], entity_effects=True,
                   other_effects=pdat["indqtr_code"], drop_absorbed=True
                   ).fit(cov_type="clustered", cluster_entity=True,
                         cluster_time=True)
    b = float(res.params["POST_x_HIGH"]); se = float(res.std_errors["POST_x_HIGH"])
    t = float(res.tstats["POST_x_HIGH"]); p = float(res.pvalues["POST_x_HIGH"])
    print(f"\n--- eq-(14) δ̂ [PLACEBO: fake POST=2014Q3-Q4, pre-Brexit only] ---")
    print(f"  δ̂_placebo(POST·HIGH) = {b:+.5f}  SE {se:.5f}  t {t:+.3f}  "
          f"p {p:.4f}  N {int(res.nobs):,}  firms {sub['gvkey'].nunique():,}  "
          f"R²w {float(res.rsquared_within):.4f}")
    print(f"\n  Real full-panel (Step 7): δ̂ ≈ −0.033 NS  N 18,632")
    print(f"  Campello Table 8 (verified): +0.231*** SE 0.059 N 17,170")
    near_real = abs(b - (-0.033)) < 0.02
    sig = p < 0.10
    if near_real or sig:
        verdict = ("IDENTIFICATION SUSPECT — placebo δ̂ is non-trivial / "
                   "≈ real-window δ̂ ⇒ pre-existing βᵁᴷ-correlated trend; "
                   "real-window estimate NOT cleanly identified")
    else:
        verdict = ("IDENTIFICATION CLEAN — placebo δ̂ ≈ 0 NS ⇒ no pre-trend; "
                   "the real-window −0.033 NS is data-driven; gap to "
                   "Campello +0.231 is a real spec/measurement question")
    print(f"  → DECISION RULE: {verdict}.")
    print(f"  [Diagnostic only — NOT a replication verdict (gated on Sina; "
          f"off-ramp forbidden).]")

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    odir = ROOT / "outputs" / "campello_rebuild" / "step8_placebo" / ts
    odir.mkdir(parents=True, exist_ok=True)
    sub[["gvkey", "cal_yr_qtr", "POST", "HIGH_UK_EXPOSURE", "CASH"] + cols
        ].to_parquet(odir / "placebo.parquet", index=False)
    (odir / "summary.json").write_text(json.dumps({
        "design": "PLACEBO — full-panel Step-7 spec, pre-Brexit only "
                  "(≤2015Q4), fake POST=2014Q3-Q4 (real 2016 window "
                  "excluded). Advisor-recommended pre-trend test.",
        "delta_hat_placebo": b, "se": se, "t": t, "pvalue": p,
        "nobs": int(res.nobs), "n_firms": int(sub["gvkey"].nunique()),
        "rsquared_within": float(res.rsquared_within),
        "real_fullpanel_ref": {"delta": -0.033, "n": 18632},
        "campello_ref": {"delta": 0.231, "se": 0.059, "n": 17170},
        "decision": verdict,
        "verdict_gated_on_sina": True,
    }, indent=2), encoding="utf-8")
    print(f"\nwritten → {odir}")


if __name__ == "__main__":
    main()
