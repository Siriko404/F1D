"""T/C firm-count forensics — why ours is 478/478 vs Campello 449/360.

Tests Sina's proposed ordering against Campello's proven mechanism, and the
β-completeness (microcap-noise) lever, reporting unique treated/control firm
counts at each attrition stage. Read-only; reuses the runner's EXACT panel
build (mirrors _build_and_fit lines 118-153) so counts are faithful.

Three questions:
  (A) Sina's order : drop negatives -> equal-count tercile survivors ->
                     complete-case attrition. (= current step3 drop-first.)
  (B) cut-then-drop: equal-count tercile the FULL pool (incl neg) ->
                     treated=top third, control=bottom third MINUS negatives.
                     (Campello's mechanism; 449/360 gap = 89 = neg count.)
  (C) neg-fraction by β completeness: nobs >= 24/36/48/60 months. Does
      requiring fuller return history collapse 39% neg toward Campello's ~7%?

For (A) and (B): report unique-firm T/C at
  S0 assigned -> S1 in DiD panel (CASH present) -> S2 complete cases (listwise).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "campello_rebuild"))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

_rp = ROOT / "src" / "f1d" / "econometric" / "run_h1_5_brexit_did.py"
_rs = importlib.util.spec_from_file_location("_runner", _rp)
_runner = importlib.util.module_from_spec(_rs)
_rs.loader.exec_module(_runner)

from step7_fullpanel_hypothesis import (
    FIRM_BUILDERS, POST_Q, _build, _calendar_lag1, _latest,
)

WINSOR = 0.01


def _beta_step1_pool() -> pd.DataFrame:
    """step1-matched estimated β^UK (gvkey, beta_uk, nobs) — the DiD pool."""
    s2 = _latest("step2_beta_uk")
    b = pd.read_parquet(s2 / "beta_uk_step1_matched.parquet",
                        columns=["gvkey", "beta_uk", "nobs"])
    b["gvkey"] = b["gvkey"].astype(str).str.zfill(6)
    return b


def _assign_drop_first(b: pd.DataFrame) -> pd.DataFrame:
    """Drop negatives, then equal-count terciles of survivors (= current)."""
    nn = b[b["beta_uk"] >= 0]
    q33 = nn["beta_uk"].quantile(1 / 3)
    q67 = nn["beta_uk"].quantile(2 / 3)
    out = []
    for _, r in b.iterrows():
        v = r["beta_uk"]
        if v < 0:
            continue
        if v >= q67:
            out.append((r["gvkey"], 1))
        elif v <= q33:
            out.append((r["gvkey"], 0))
    return pd.DataFrame(out, columns=["gvkey", "HIGH_UK_EXPOSURE"])


def _assign_cut_then_drop(b: pd.DataFrame) -> pd.DataFrame:
    """Equal-count terciles of FULL pool (incl neg); treated=top third,
    control=bottom third MINUS negatives. Campello's 89=neg mechanism."""
    q33 = b["beta_uk"].quantile(1 / 3)
    q67 = b["beta_uk"].quantile(2 / 3)
    out = []
    for _, r in b.iterrows():
        v = r["beta_uk"]
        if v >= q67:
            out.append((r["gvkey"], 1))
        elif v <= q33 and v >= 0:           # bottom third, drop negatives
            out.append((r["gvkey"], 0))
    return pd.DataFrame(out, columns=["gvkey", "HIGH_UK_EXPOSURE"]), q33, q67


def _build_panel(treatment_df: pd.DataFrame):
    """Mirror runner _build_and_fit 118-153; return df (DV present) + reg_cols
    BEFORE the complete-case dropna, so we can stage attrition."""
    s1 = pd.read_parquet(_latest("step1_sample") / "sample.parquet",
                         columns=["gvkey", "cal_yr_qtr", "atq", "fic100_industry_id"])
    s1["gvkey"] = s1["gvkey"].astype(str).str.zfill(6)
    tt = treatment_df.copy(); tt["gvkey"] = tt["gvkey"].astype(str).str.zfill(6)
    panel = s1.merge(tt[["gvkey", "HIGH_UK_EXPOSURE"]], on="gvkey", how="inner")
    panel["POST"] = panel["cal_yr_qtr"].isin(POST_Q).astype(int)
    df = panel.merge(_runner._cash_dv_t8(), on=["gvkey", "cal_yr_qtr"], how="inner")
    df = df[df["atq"] > 0].copy(); df["log_assets"] = np.log(df["atq"])

    firm_cols = []
    for cls in FIRM_BUILDERS:
        bb = _build(cls); col = [c for c in bb.columns if c not in ("gvkey", "cal_yr_qtr")][0]
        df = df.merge(_calendar_lag1(bb, col), on=["gvkey", "cal_yr_qtr"], how="left")
        firm_cols.append(col)
    df = df.merge(_calendar_lag1(
        df[["gvkey", "cal_yr_qtr", "log_assets"]], "log_assets").rename(
        columns={"log_assets": "log_assets_l1"}), on=["gvkey", "cal_yr_qtr"], how="left")
    firm_cols.append("log_assets_l1")
    cons = _runner._statsum_meanest_z()
    df = df.merge(_calendar_lag1(cons, "cons_fwd"), on=["gvkey", "cal_yr_qtr"], how="left")
    df["POST_x_HIGH"] = (df["POST"] * df["HIGH_UK_EXPOSURE"]).astype(float)
    df["indqtr_code"] = ((df["fic100_industry_id"].astype("int64").astype(str)
                          + "_" + df["cal_yr_qtr"].astype(str)).astype("category").cat.codes)
    reg_cols = ["POST_x_HIGH"] + firm_cols + ["cons_fwd"]
    return df, reg_cols


def _tc(df: pd.DataFrame) -> tuple[int, int]:
    t = df[df["HIGH_UK_EXPOSURE"] == 1]["gvkey"].nunique()
    c = df[df["HIGH_UK_EXPOSURE"] == 0]["gvkey"].nunique()
    return t, c


def _stage_counts(name: str, treatment_df: pd.DataFrame) -> None:
    t0, c0 = _tc(treatment_df)
    df, reg_cols = _build_panel(treatment_df)
    t1, c1 = _tc(df)                                   # DV present
    sub = df.dropna(subset=["CASH", "indqtr_code"] + reg_cols)
    t2, c2 = _tc(sub)                                  # complete cases
    print(f"\n  {name}")
    print(f"    S0 assigned        T={t0:>4}  C={c0:>4}  (gap {t0 - c0:+d})")
    print(f"    S1 in DiD panel    T={t1:>4}  C={c1:>4}  (gap {t1 - c1:+d})")
    print(f"    S2 complete cases  T={t2:>4}  C={c2:>4}  (gap {t2 - c2:+d})")


def main() -> None:
    b = _beta_step1_pool()
    n = len(b)
    print("=" * 68)
    print("T/C COUNT FORENSICS — step1-matched β pool")
    print("=" * 68)
    print(f"pool firms: {n:,}   negatives: {(b['beta_uk'] < 0).sum():,} "
          f"({(b['beta_uk'] < 0).mean():.1%})   Campello implied ~7%")

    # (C) neg-fraction by β completeness
    print("\n--- (C) neg-fraction by β estimation completeness (nobs) ---")
    print(f"  {'min months':>10} {'firms':>7} {'%neg':>7}")
    for thr in (24, 36, 48, 60):
        sub = b[b["nobs"] >= thr]
        if len(sub):
            print(f"  {thr:>10} {len(sub):>7,} {(sub['beta_uk'] < 0).mean():>6.1%}")
    print("  Read: does %neg fall toward 7% as fuller history is required?")

    # (A) Sina's order = drop-first
    print("\n--- (A) Sina's order: drop-neg -> tercile -> complete-case ---")
    a = _assign_drop_first(b)
    _stage_counts("drop-first (current step3)", a)

    # (B) cut-then-drop (Campello mechanism)
    print("\n--- (B) cut-then-drop: tercile FULL -> drop neg from control ---")
    bt, q33, q67 = _assign_cut_then_drop(b)
    print(f"  full-pool cuts p33/p67 = {q33:.4f} / {q67:.4f}  "
          f"(Campello 0.28 / 0.68)")
    _stage_counts("cut-then-drop (Campello)", bt)

    print("\n" + "=" * 68)
    print("Read: which ordering's S2 lands near 449/360? Does (C) show the")
    print("39% is a microcap-noise artifact fixable by a completeness gate?")


if __name__ == "__main__":
    main()
