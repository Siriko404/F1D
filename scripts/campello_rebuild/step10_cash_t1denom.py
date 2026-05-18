"""STEP 10 — DV-fix TEST: step7 clone, CASH denominator = Table-1 plain.

Sina-authorized 2026-05-17 ("GO"). Systematic-debugging Phase 3/4:
ONE change vs step7 — the CASH denominator. Everything else byte-identical
(sample, full panel, POST(2016Q3-Q4), 5 firm controls lagged 1Q +
cons_fwd, FIRM FE + FIC100×qtr FE, double-clustered SE, winsor within
cal_yr_qtr, coefficient persistence). Non-destructive: canonical step7
(Table-8 net-of-cash denom) is left intact and committed.

HYPOTHESIS (programmatic moment fingerprint, _diag_moment_fingerprint.py):
the variable Campello actually analyzed has the **Table-1** distribution
  CASH_t = cheq_t / atq_{t-1}            (Table 1 verbatim, jrnl p.3198)
not the Table-8-caption net-of-cash form
  CASH_t = cheq_t / (atq_{t-1} − cheq_{t-1})   (our step7, Sina-ratified)
Table-1 denom reproduced Campello CASH on 6 moments (univ mean/SD/med +
treated-med + control-med); Table-8 denom gave mean 0.61/SD 1.65 (fail).

DECISIVE READ:
  δ̂ → ≈ +0.231  ⇒ DV denominator WAS the root cause (leg closed)
  δ̂ ≈ −0.033 still ⇒ DV necessary-not-sufficient ⇒ βᵁᴷ stage in play
Factual test only. NOT a replication verdict (gated on Sina). Off-ramp
forbidden.

Output: outputs/campello_rebuild/step10_cash_t1denom/<ts>/
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
POST_Q = [20163, 20164]
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


def _cash_dv_t1() -> pd.DataFrame:
    """CASH_t = cheq_t / atq_{t-1}  — Table-1 plain denominator (THE ONLY
    change vs step7 `_cash_dv`, which used atq_{t-1} − cheq_{t-1})."""
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
    src = df[["gvkey", "cal_yr_qtr", "atq"]].rename(
        columns={"cal_yr_qtr": "_pq", "atq": "atq_l1"})
    df["_pq"] = df["cal_yr_qtr"].map(_prev_q).astype("int64")
    df = df.merge(src, on=["gvkey", "_pq"], how="left").drop(columns="_pq")
    df = df[df["cheq"].notna() & (df["atq_l1"] > 0)].copy()   # <-- Table-1
    df["CASH"] = df["cheq"] / df["atq_l1"]                     # <-- Table-1
    return df[["gvkey", "cal_yr_qtr", "CASH"]]


def main() -> None:
    print("=== STEP 10 — DV-fix TEST: step7 clone, CASH = cheq/atq_l1 "
          "(Table-1 denom) ===\n")
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
    print(f"βᵁᴷ-tercile firms: {len(tc):,} "
          f"(T={int((tc.HIGH_UK_EXPOSURE==1).sum()):,}, "
          f"C={int((tc.HIGH_UK_EXPOSURE==0).sum()):,})")

    panel = s1.merge(tc[["gvkey", "HIGH_UK_EXPOSURE"]], on="gvkey",
                     how="inner")
    panel["POST"] = panel["cal_yr_qtr"].isin(POST_Q).astype(int)

    cash = _cash_dv_t1()
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
                  on=["gvkey", "cal_yr_qtr"], how="left")

    df["CASH"] = df.groupby("cal_yr_qtr", observed=True)["CASH"].transform(
        lambda s: s.clip(s.quantile(WINSOR), s.quantile(1 - WINSOR)))
    df["POST_x_HIGH"] = (df["POST"] * df["HIGH_UK_EXPOSURE"]).astype(float)
    df["indqtr_code"] = ((df["fic100_industry_id"].astype("int64").astype(str)
                          + "_" + df["cal_yr_qtr"].astype(str))
                         .astype("category").cat.codes)

    cols = ["POST_x_HIGH"] + firm_cols + ["cons_fwd"]
    sub = df.dropna(subset=["CASH", "indqtr_code"] + cols).copy()
    cm = sub["CASH"]
    print(f"\nCASH (Table-1 denom, winsor) moments on estimation sample: "
          f"mean {cm.mean():+.4f}  SD {cm.std():.4f}  med {cm.median():+.4f}"
          f"  N {len(cm):,}")
    print("  >> Campello Table 1 CASH: mean +0.220 SD 0.250 med +0.120")

    pdat = sub.set_index(["gvkey", "cal_yr_qtr"]).sort_index()
    res = PanelOLS(pdat["CASH"], pdat[cols], entity_effects=True,
                   other_effects=pdat["indqtr_code"], drop_absorbed=True
                   ).fit(cov_type="clustered", cluster_entity=True,
                         cluster_time=True)
    b = float(res.params["POST_x_HIGH"])
    se = float(res.std_errors["POST_x_HIGH"])
    t = float(res.tstats["POST_x_HIGH"])
    p = float(res.pvalues["POST_x_HIGH"])
    coefs = [{"name": c, "coef": float(res.params[c]),
              "se": float(res.std_errors[c]), "t": float(res.tstats[c]),
              "pvalue": float(res.pvalues[c])} for c in res.params.index]
    print("\n--- eq-(14) δ̂ [DV=CASH Table-1 denom, FULL PANEL] ---")
    print(f"  δ̂(POST·HIGH) = {b:+.5f}  SE {se:.5f}  t {t:+.3f}  p {p:.4f}"
          f"  N {int(res.nobs):,}  firms {sub['gvkey'].nunique():,}  "
          f"R²w {float(res.rsquared_within):.4f}")
    print(f"  step7 Table-8 denom (committed): δ̂ −0.03288 NS  N 18,632")
    print(f"  Campello Table 8 CASH (verbatim): +0.231*** SE 0.059 N 17,170")
    print("  [Factual test. NOT a replication verdict — gated on Sina.]")

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    odir = ROOT / "outputs" / "campello_rebuild" / "step10_cash_t1denom" / ts
    odir.mkdir(parents=True, exist_ok=True)
    sub[["gvkey", "cal_yr_qtr", "POST", "HIGH_UK_EXPOSURE", "CASH"] + cols
        ].to_parquet(odir / "panel.parquet", index=False)
    (odir / "summary.json").write_text(json.dumps({
        "test": "step7 clone; ONLY change = CASH denominator → cheq/atq_l1 "
                "(Table-1 plain, jrnl p.3198) vs step7 net-of-cash "
                "(Table-8 caption). Sina-authorized 2026-05-17.",
        "cash_moments_estimation_sample": {
            "mean": float(cm.mean()), "sd": float(cm.std()),
            "median": float(cm.median()), "n": int(len(cm))},
        "campello_table1_cash": {"mean": 0.22, "sd": 0.25, "median": 0.12},
        "model": "eq-14 PanelOLS; FULL panel + POST(2016Q3-Q4); FIRM FE + "
                 "INDUSTRY(FIC100)×QUARTER FE; double-clustered firm×qtr",
        "results": [{
            "tag": "FULL_PANEL_CASH_T1DENOM",
            "delta_hat": b, "se": se, "t": t, "pvalue": p,
            "nobs": int(res.nobs), "n_firms": int(sub["gvkey"].nunique()),
            "rsquared_within": float(res.rsquared_within),
            "controls": cols, "coefficients": coefs,
            "consensus_variant": "cons_fwd"}],
        "step7_table8_ref": {"delta": -0.03288, "n": 18632},
        "campello_reference": {"cash_delta": 0.231, "se": 0.059, "n": 17170,
                               "rsquared": 0.21, "stars": "***",
                               "source": "Campello et al. 2022 JFQA, "
                               "Table 8 col.1, journal p.3208 (verbatim)",
                               "note": "reference only; NOT a tuning "
                               "target; no replication verdict (gated)"},
        "step1_dir": s1_dir.name, "step3_dir": s3_dir.name,
        "verdict_gated_on_sina": True,
    }, indent=2), encoding="utf-8")
    print(f"\nwritten → {odir}")


if __name__ == "__main__":
    main()
