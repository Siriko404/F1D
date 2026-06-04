"""Diligent magnitude attack on the Campello Brexit DiD residual gap.

After pooled-winsor fix both arms are positive but undershoot ~3-5x:
  MARKET +0.018 vs paper 0.231 ; TEXTUAL +0.076 vs paper 0.357.

A DiD coefficient on a ratio DV is governed by (a) DV scale and (b) how much
FE/controls absorb the treatment variation. This sweeps:

  FE variants (PanelOLS):
    F1  firm + quarter                 (additive, lightest)
    F2  firm + industry + quarter      (additive industry)
    F3  firm + industry×quarter        (interacted — CURRENT runner)
  Control variants:
    C0  none (POST_x_HIGH only)
    C1  full (5 firm controls + consensus)  [CURRENT]

12 fits per arm. Also reports the DV scale (mean/SD treated vs control) to see
if our net-of-cash CASH level matches Campello Table 1 (treated gross mean
~0.20; net-of-cash should be higher).

Panel build copies the runner _build_and_fit body (pooled winsor, as committed).
Read-only.
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

_cash_dv_t8 = _runner._cash_dv_t8
_statsum_meanest_z = _runner._statsum_meanest_z
WINSOR = 0.01


def build_panel(treatment_df) -> tuple[pd.DataFrame, list]:
    s1 = pd.read_parquet(_latest("step1_sample") / "sample.parquet",
                         columns=["gvkey", "cal_yr_qtr", "atq", "fic100_industry_id"])
    s1["gvkey"] = s1["gvkey"].astype(str).str.zfill(6)
    tt = treatment_df.copy(); tt["gvkey"] = tt["gvkey"].astype(str).str.zfill(6)
    panel = s1.merge(tt[["gvkey", "HIGH_UK_EXPOSURE"]], on="gvkey", how="inner")
    panel["POST"] = panel["cal_yr_qtr"].isin(POST_Q).astype(int)
    df = panel.merge(_cash_dv_t8(), on=["gvkey", "cal_yr_qtr"], how="inner")
    df = df[df["atq"] > 0].copy(); df["log_assets"] = np.log(df["atq"])

    firm_cols = []
    for cls in FIRM_BUILDERS:
        b = _build(cls); col = [c for c in b.columns if c not in ("gvkey", "cal_yr_qtr")][0]
        df = df.merge(_calendar_lag1(b, col), on=["gvkey", "cal_yr_qtr"], how="left")
        firm_cols.append(col)
    df = df.merge(_calendar_lag1(
        df[["gvkey", "cal_yr_qtr", "log_assets"]], "log_assets").rename(
        columns={"log_assets": "log_assets_l1"}), on=["gvkey", "cal_yr_qtr"], how="left")
    firm_cols.append("log_assets_l1")

    cons = _statsum_meanest_z()
    df = df.merge(_calendar_lag1(cons, "cons_fwd"), on=["gvkey", "cal_yr_qtr"], how="left")
    df["CASH"] = df["CASH"].clip(df["CASH"].quantile(WINSOR), df["CASH"].quantile(1 - WINSOR))
    df["POST_x_HIGH"] = (df["POST"] * df["HIGH_UK_EXPOSURE"]).astype(float)
    df["ind_code"] = df["fic100_industry_id"].astype("int64").astype("category").cat.codes
    df["indqtr_code"] = ((df["fic100_industry_id"].astype("int64").astype(str)
                          + "_" + df["cal_yr_qtr"].astype(str)).astype("category").cat.codes)
    return df, firm_cols


def fit(df, firm_cols, fe: str, ctrl: str) -> dict:
    from linearmodels.panel import PanelOLS
    reg = ["POST_x_HIGH"] + (firm_cols + ["cons_fwd"] if ctrl == "full" else [])
    need = ["CASH"] + reg
    if fe in ("F2",):
        need += ["ind_code"]
    if fe in ("F3",):
        need += ["indqtr_code"]
    sub = df.dropna(subset=need).copy()
    pdat = sub.set_index(["gvkey", "cal_yr_qtr"]).sort_index()
    kw = dict(entity_effects=True, drop_absorbed=True)
    if fe == "F1":
        kw["time_effects"] = True
    elif fe == "F2":
        kw["time_effects"] = True
        kw["other_effects"] = pdat["ind_code"]
    elif fe == "F3":
        kw["other_effects"] = pdat["indqtr_code"]
    try:
        res = PanelOLS(pdat["CASH"], pdat[reg], **kw).fit(
            cov_type="clustered", cluster_entity=True, cluster_time=True)
        return {"b": float(res.params["POST_x_HIGH"]),
                "se": float(res.std_errors["POST_x_HIGH"]),
                "p": float(res.pvalues["POST_x_HIGH"]), "n": int(res.nobs)}
    except Exception as e:
        return {"err": str(e)[:30]}


def main() -> None:
    arms = [("MARKET", _runner._load_market_treatment(), 0.231),
            ("TEXTUAL", _runner._load_textual_treatment(), 0.357)]
    fe_labels = {"F1": "firm+qtr", "F2": "firm+ind+qtr", "F3": "firm+ind×qtr(CUR)"}

    for arm, trt, target in arms:
        df, firm_cols = build_panel(trt)
        print("=" * 72)
        print(f"{arm} arm — magnitude sweep   (paper target δ={target:+.3f})")
        print("=" * 72)
        # DV scale
        for grp, val in (("treated", 1), ("control", 0)):
            c = df[df["HIGH_UK_EXPOSURE"] == val]["CASH"]
            print(f"  CASH(net-of-cash) {grp:<8} mean={c.mean():.3f} "
                  f"SD={c.std():.3f} med={c.median():.3f}")
        print(f"  {'FE':<20} {'ctrl':<6} {'δ̂':>9} {'SE':>7} {'p':>7} {'N':>8} {'×short':>7}")
        print("  " + "-" * 64)
        for fe in ("F1", "F2", "F3"):
            for ctrl in ("none", "full"):
                r = fit(df, firm_cols, fe, ctrl)
                if "err" in r:
                    print(f"  {fe_labels[fe]:<20} {ctrl:<6}  ERR: {r['err']}")
                else:
                    xs = target / r["b"] if r["b"] > 0 else float("nan")
                    print(f"  {fe_labels[fe]:<20} {ctrl:<6} {r['b']:>+9.4f} "
                          f"{r['se']:>7.4f} {r['p']:>7.4f} {r['n']:>8,} {xs:>7.1f}")
        print()
    print("Read: which FE/ctrl layer recovers magnitude toward the target?")
    print("      F1→F3 shows FE absorption; none→full shows control absorption.")


if __name__ == "__main__":
    main()
