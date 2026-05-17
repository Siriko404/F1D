"""STEP 5 — eq-(14) DiD estimator on REAL data (Campello et al. 2022, Table 8).

Built FRESH from the paper. NO synthetic (Sina 2026-05-17: synthetic
proofs validate machinery, not fidelity — last rebuild's synthetic passed
while a real Step-1 data-prep bug went uncaught). Real cash DV, real FE,
real δ̂. CONTROLS_{i,t-1} are added at Step 6 (strictly sequential) — this
step is the UNCONDITIONAL real DiD.

Verbatim DV (Table 8 caption, jrnl p.3208, Sina-ratified 2026-05-17 over the
Table 1 descriptive-stats note — the table's own caption governs its
regression):
  "CASH is defined as total cash holdings divided by lagged total assets
   net of cash holdings."
      CASH_{i,t} = cheq_t / (atq_{t-1} − cheq_{t-1})
  cheq = Compustat quarterly cash & short-term investments. Both
  denominator terms lagged one CALENDAR quarter (target-driven idiom —
  the verified brexit_cash_flow pattern; NOT the inverted keying fixed in
  step1 `e7a219b`). 1% winsorization within cal_yr_qtr (verbatim Table 1:
  "All variables are winsorized at the 1% level").

Verbatim eq-(14) (Sina-pasted):
  Y_{i,t} = α + δ[POST_t·HIGH_UK_EXPOSURE_i] + θ·CONTROLS_{i,t-1}
            + Σ_i FIRM_i + Σ_j Σ_t INDUSTRY_j×QUARTER_t + ε_{i,t}

This step: δ on the interaction ONLY. POST (time) is absorbed by the
quarter side of INDUSTRY×QUARTER FE; HIGH (firm-invariant) is absorbed by
FIRM FE; only POST·HIGH carries identifying within-firm-over-time
variation. Hard-guard: exactly one regressor (the interaction). SE
unadjusted here — double-clustering (firm × calendar-qtr) is Step 6/7.

Output: outputs/campello_rebuild/step5_did/<ts>/
    did_panel.parquet   (gvkey, cal_yr_qtr, POST, HIGH_UK_EXPOSURE, CASH,
                          fic100_industry_id)
    summary.json
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
COMP = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
BUFFER_LO = pd.Timestamp("2008-01-01")
WIN_HI_DATE = pd.Timestamp("2016-12-31")
WINSOR = 0.01


def _prev_q(yq: int) -> int:
    yr, q = yq // 10, yq % 10
    return (yr - 1) * 10 + 4 if q == 1 else yr * 10 + (q - 1)


def _latest(sub: str) -> Path:
    base = ROOT / "outputs" / "campello_rebuild" / sub
    return sorted(d for d in base.iterdir() if d.is_dir())[-1]


def _build_cash_dv() -> pd.DataFrame:
    """CASH_t = cheq_t / (atq_{t-1} − cheq_{t-1}); calendar-lag, target-driven."""
    df = pq.read_table(
        COMP, columns=["gvkey", "datadate", "curcdq", "loc", "consol",
                        "indfmt", "datafmt", "atq", "cheq"]
    ).to_pandas()
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
    df = df.sort_values(["gvkey", "cal_yr_qtr", "datadate"], kind="stable")
    df = df.drop_duplicates(["gvkey", "cal_yr_qtr"], keep="last")

    # target-driven 1-qtr calendar lag (row T joins source whose
    # cal_yr_qtr == _prev_q(T)) ⟹ lag(T) = value(T−1).
    src = df[["gvkey", "cal_yr_qtr", "atq", "cheq"]].rename(
        columns={"cal_yr_qtr": "_pq", "atq": "atq_l1", "cheq": "cheq_l1"})
    df["_pq"] = df["cal_yr_qtr"].map(_prev_q).astype("int64")
    df = df.merge(src, on=["gvkey", "_pq"], how="left").drop(columns="_pq")

    df["denom"] = df["atq_l1"] - df["cheq_l1"]
    df = df[df["cheq"].notna() & (df["denom"] > 0)].copy()
    df["CASH"] = df["cheq"] / df["denom"]
    return df[["gvkey", "cal_yr_qtr", "CASH"]]


def main() -> None:
    print("=== STEP 5 — eq-(14) DiD on REAL data (no synthetic) ===\n")

    s1_dir = _latest("step1_sample")
    s4_dir = _latest("step4_timeline")
    fic = pd.read_parquet(s1_dir / "sample.parquet",
                          columns=["gvkey", "cal_yr_qtr", "fic100_industry_id"])
    fic["gvkey"] = fic["gvkey"].astype(str).str.zfill(6)
    panel = pd.read_parquet(s4_dir / "panel.parquet")
    panel["gvkey"] = panel["gvkey"].astype(str).str.zfill(6)
    print(f"Step-1: {s1_dir.name}   Step-4: {s4_dir.name}")
    print(f"Step-4 panel: {len(panel):,} fq / {panel['gvkey'].nunique():,} firms")

    cash = _build_cash_dv()
    print(f"CASH DV built (cheq/(atq_l1−cheq_l1), winsor pending): "
          f"{len(cash):,} firm-qtrs")

    d = (panel.merge(cash, on=["gvkey", "cal_yr_qtr"], how="inner")
              .merge(fic, on=["gvkey", "cal_yr_qtr"], how="inner"))
    d = d.dropna(subset=["CASH", "fic100_industry_id"])
    # 1% winsorize CASH within cal_yr_qtr (verbatim: all vars winsorized 1%).
    d["CASH"] = d.groupby("cal_yr_qtr", observed=True)["CASH"].transform(
        lambda s: s.clip(s.quantile(WINSOR), s.quantile(1 - WINSOR)))
    print(f"merged DiD rows (panel ∩ CASH ∩ fic): {len(d):,}; "
          f"firms {d['gvkey'].nunique():,}")

    cell = d.groupby(["POST", "HIGH_UK_EXPOSURE"])["CASH"].agg(["count", "mean"])
    print("\n--- raw cell means (pre-FE, descriptive) ---")
    print(cell.rename(index={0: "PRE", 1: "POST"}).to_string())
    # naive 2×2 DiD (descriptive only; FE estimate is the real one):
    m = d.groupby(["POST", "HIGH_UK_EXPOSURE"])["CASH"].mean()
    naive = (m.get((1, 1)) - m.get((0, 1))) - (m.get((1, 0)) - m.get((0, 0)))
    print(f"naive 2×2 DiD (no FE/controls, descriptive): {naive:+.5f}")

    # --- eq-(14) PanelOLS: interaction only, FIRM FE + IND×QTR FE -----
    from linearmodels.panel import PanelOLS

    d["POST_x_HIGH"] = (d["POST"] * d["HIGH_UK_EXPOSURE"]).astype(float)
    d["indqtr"] = (d["fic100_industry_id"].astype("int64").astype(str)
                   + "_" + d["cal_yr_qtr"].astype(str))
    d["indqtr_code"] = d["indqtr"].astype("category").cat.codes
    pdat = d.set_index(["gvkey", "cal_yr_qtr"]).sort_index()

    exog = pdat[["POST_x_HIGH"]]
    assert list(exog.columns) == ["POST_x_HIGH"], \
        f"INTERACTION-ONLY GUARD violated: {list(exog.columns)}"

    mod = PanelOLS(pdat["CASH"], exog, entity_effects=True,
                   other_effects=pdat["indqtr_code"], drop_absorbed=True)
    res = mod.fit()  # unadjusted SE (clustering = Step 6/7)
    b = float(res.params["POST_x_HIGH"])
    se = float(res.std_errors["POST_x_HIGH"])
    t = float(res.tstats["POST_x_HIGH"])
    p = float(res.pvalues["POST_x_HIGH"])

    print("\n--- eq-(14) δ̂  (REAL data, FIRM FE + IND×QTR FE, "
          "interaction-only, NO controls, unadj SE) ---")
    print(f"  δ̂ (POST·HIGH) = {b:+.5f}   SE {se:.5f}   t {t:+.3f}   "
          f"p {p:.4f}")
    print(f"  N = {int(res.nobs):,}   firms = {d['gvkey'].nunique():,}   "
          f"R²(within) = {float(res.rsquared_within):.4f}")
    print(f"  Campello Table 8 cash anchor (reference, NOT a target): "
          f"+0.231*** SE 0.059 N 17,170")
    print("  [Step-5 = unconditional; CONTROLS_{i,t-1} added Step 6. "
          "NOT a replication verdict — gated on Sina.]")

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    odir = ROOT / "outputs" / "campello_rebuild" / "step5_did" / ts
    odir.mkdir(parents=True, exist_ok=True)
    d[["gvkey", "cal_yr_qtr", "POST", "HIGH_UK_EXPOSURE", "CASH",
       "fic100_industry_id"]].to_parquet(odir / "did_panel.parquet", index=False)
    summary = {
        "dv": "CASH = cheq_t / (atq_{t-1} − cheq_{t-1})  [Table 8 caption, "
              "Sina-ratified 2026-05-17]; 1% winsor within cal_yr_qtr",
        "model": "eq-14 PanelOLS, interaction-only (POST·HIGH); FIRM FE "
                 "(entity) + INDUSTRY(FIC100)×QUARTER FE (other_effects); "
                 "unadjusted SE (clustering = Step 6/7); NO controls",
        "delta_hat": b, "se": se, "t": t, "pvalue": p,
        "nobs": int(res.nobs), "n_firms": int(d["gvkey"].nunique()),
        "rsquared_within": float(res.rsquared_within),
        "naive_2x2_did": float(naive),
        "campello_reference": {"cash_delta": 0.231, "se": 0.059, "n": 17170,
                               "note": "reference only; NOT a tuning target; "
                               "no replication verdict (gated on Sina)"},
        "step1_dir": s1_dir.name, "step4_dir": s4_dir.name,
        "no_synthetic": "Sina 2026-05-17 — real data only",
    }
    (odir / "summary.json").write_text(json.dumps(summary, indent=2),
                                       encoding="utf-8")
    print(f"\nwritten → {odir}")


if __name__ == "__main__":
    main()
