#!/usr/bin/env python3
"""
================================================================================
STAGE 4b-ext: H1.5 Campello Brexit DiD on UncResCEO — FULL grid
              {continuous, binary} x {normal, PSM} x {beta^UK tercile, textual}
================================================================================
ID: econometric/run_h1_5_brexit_did_uncres_ext
Description: Extends run_h1_5_brexit_did_uncres.py (which gave UncResCEO continuous,
             unmatched, 2 arms only) to the full 8-cell grid Sina asked for:

               DV kind   x  matching  x  treatment arm
               --------     --------     -------------
               continuous   normal       beta^UK tercile
               continuous   PSM          textual (Sec 1+7)
               binary       normal
               binary       PSM

             - continuous = UncResCEO (DWZ Eq.4 CEO Q&A residual, firm-qtr mean).
             - binary     = 1[UncResCEO >= pooled median of the arm's estimation
                            sample]  (LPM via PanelOLS). Threshold computed ONCE
                            per arm on the unmatched estimation sample and reused
                            for the PSM fit (one fixed cutoff per arm).
             - normal     = unmatched eq-(14) clone (identical to the existing
                            run_h1_5_brexit_did_uncres -> sanity-reproduces its
                            continuous-normal deltas).
             - PSM        = 3-NN with replacement on the 6 eq-(14) controls
                            (logit, StandardScaler, pre-POST firm means), weighted
                            eq-(14) on the matched sub-panel -- the SAME machinery
                            as run_h1_5_brexit_did_psm (matcher imported verbatim).

ZERO drift: panel construction copies the canonical UncResCEO panel from the
existing uncres runner; the PSM matcher (_match_3nn_replacement) and all building
blocks (_uncres_dv, treatment loaders, consensus, step7 helpers) are IMPORTED
from the two production runners, not re-implemented. No production file edited.

Novel extension — Campello Table 8 has no UncResCEO benchmark; no verdict.

Outputs: outputs/econometric/h1_5_brexit_did_uncres_ext/<timestamp>/summary.json
================================================================================
"""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "campello_rebuild"))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Single source of truth: pull every building block from the two prod runners.
_UNC = _load(ROOT / "src" / "f1d" / "econometric" / "run_h1_5_brexit_did_uncres.py",
             "_unc_prod")
_PSM = _load(ROOT / "src" / "f1d" / "econometric" / "run_h1_5_brexit_did_psm.py",
             "_psm_prod")

FIRM_BUILDERS = _UNC.FIRM_BUILDERS
POST_Q = _UNC.POST_Q
_build = _UNC._build
_calendar_lag1 = _UNC._calendar_lag1
_latest = _UNC._latest
_uncres_dv = _UNC._uncres_dv
_statsum_meanest_z = _UNC._statsum_meanest_z
_load_market_treatment = _UNC._load_market_treatment
_load_textual_treatment = _UNC._load_textual_treatment
_match_3nn_replacement = _PSM._match_3nn_replacement
N_NEIGHBORS = _PSM.N_NEIGHBORS
PRE_POST_MAX = _PSM.PRE_POST_MAX  # firm covariate window = cal_yr_qtr < 2016Q3

SUITE_ID = "H1.5.brexit_did_uncres_ext"
SUITE_DIR_NAME = "h1_5_brexit_did_uncres_ext"


# ==============================================================================
# Canonical UncResCEO eq-(14) panel (copied from _unc._build_and_fit, pre-fit)
# ==============================================================================

def _build_panel_uncres(treatment_df: pd.DataFrame):
    s1 = pd.read_parquet(_latest("step1_sample") / "sample.parquet",
                         columns=["gvkey", "cal_yr_qtr", "atq",
                                  "fic100_industry_id"])
    s1["gvkey"] = s1["gvkey"].astype(str).str.zfill(6)

    tt = treatment_df.copy(); tt["gvkey"] = tt["gvkey"].astype(str).str.zfill(6)
    panel = s1.merge(tt[["gvkey", "HIGH_UK_EXPOSURE"]], on="gvkey", how="inner")
    panel["POST"] = panel["cal_yr_qtr"].isin(POST_Q).astype(int)
    df = panel.merge(_uncres_dv(), on=["gvkey", "cal_yr_qtr"], how="inner")
    df = df[df["atq"] > 0].copy(); df["log_assets"] = np.log(df["atq"])

    firm_cols = []
    for cls in FIRM_BUILDERS:
        b = _build(cls)
        col = [c for c in b.columns if c not in ("gvkey", "cal_yr_qtr")][0]
        df = df.merge(_calendar_lag1(b, col), on=["gvkey", "cal_yr_qtr"], how="left")
        firm_cols.append(col)
    df = df.merge(_calendar_lag1(
        df[["gvkey", "cal_yr_qtr", "log_assets"]], "log_assets").rename(
        columns={"log_assets": "log_assets_l1"}),
        on=["gvkey", "cal_yr_qtr"], how="left")
    firm_cols.append("log_assets_l1")

    cons = _statsum_meanest_z()
    df = df.merge(_calendar_lag1(cons, "cons_fwd"),
                  on=["gvkey", "cal_yr_qtr"], how="left")
    # NO winsorization on UNCRES (pre-cleaned residual).
    df["POST_x_HIGH"] = (df["POST"] * df["HIGH_UK_EXPOSURE"]).astype(float)
    df["indqtr_code"] = ((df["fic100_industry_id"].astype("int64").astype(str)
                          + "_" + df["cal_yr_qtr"].astype(str))
                         .astype("category").cat.codes)
    reg_cols = ["POST_x_HIGH"] + firm_cols + ["cons_fwd"]
    return df, firm_cols, reg_cols


def _firm_propensity_uncres(df: pd.DataFrame, cov_cols: list[str]) -> pd.DataFrame:
    """Pre-POST firm mean of the 6 covariates -> logit propensity score.

    Mirrors _psm._firm_propensity EXACTLY (StandardScaler + logit lbfgs C=1.0,
    cal_yr_qtr < PRE_POST_MAX firm means); only the CASH/CASH_T1 carry columns
    (used solely for the C.2 matched-summary, not the score) are dropped."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler

    pre = df[df["cal_yr_qtr"] < PRE_POST_MAX]
    firm = (pre.groupby("gvkey", as_index=False)
               .agg({"HIGH_UK_EXPOSURE": "first", **{c: "mean" for c in cov_cols}}))
    firm = firm.dropna(subset=cov_cols).reset_index(drop=True)
    X = StandardScaler().fit_transform(firm[cov_cols].to_numpy(dtype=float))
    y = firm["HIGH_UK_EXPOSURE"].astype(int).to_numpy()
    lr = LogisticRegression(max_iter=2000, solver="lbfgs", C=1.0)
    lr.fit(X, y)
    firm["p_score"] = lr.predict_proba(X)[:, 1]
    return firm


def _fit(sub: pd.DataFrame, reg_cols: list[str], dv: str,
         weights_col: str | None = None) -> dict:
    from linearmodels.panel import PanelOLS
    pdat = sub.set_index(["gvkey", "cal_yr_qtr"]).sort_index()
    kw = {}
    if weights_col is not None:
        kw["weights"] = pdat[weights_col]
    res = PanelOLS(pdat[dv], pdat[reg_cols], entity_effects=True,
                   other_effects=pdat["indqtr_code"], drop_absorbed=True, **kw
                   ).fit(cov_type="clustered", cluster_entity=True,
                         cluster_time=True)
    b = float(res.params["POST_x_HIGH"]); se = float(res.std_errors["POST_x_HIGH"])
    coefs = [{"name": c, "coef": float(res.params[c]),
              "se": float(res.std_errors[c]), "t": float(res.tstats[c]),
              "pvalue": float(res.pvalues[c])} for c in res.params.index]
    return {"delta_hat": b, "se": se, "t": float(res.tstats["POST_x_HIGH"]),
            "pvalue": float(res.pvalues["POST_x_HIGH"]), "nobs": int(res.nobs),
            "n_firms": int(sub["gvkey"].nunique()),
            "rsquared_within": float(res.rsquared_within),
            "controls": reg_cols, "coefficients": coefs,
            "consensus_variant": "cons_fwd"}


def _run_arm(treatment_df: pd.DataFrame, arm: str) -> list[dict]:
    df, firm_cols, reg_cols = _build_panel_uncres(treatment_df)
    cov_cols = firm_cols + ["cons_fwd"]

    sub = df.dropna(subset=["UNCRES", "indqtr_code"] + reg_cols).copy()
    med = float(sub["UNCRES"].median())                       # pooled per-arm median
    sub["UNCRES_bin"] = (sub["UNCRES"] >= med).astype(float)
    print(f"  [{arm}] est-sample N={len(sub):,} firms={sub['gvkey'].nunique():,} "
          f"UncRes median={med:+.5f} (bin rate {sub['UNCRES_bin'].mean():.3f})")

    # PSM weights (firm-level), reused for both continuous and binary PSM fits.
    firm = _firm_propensity_uncres(df, cov_cols)
    matched = _match_3nn_replacement(firm)
    w = matched.set_index("gvkey")["weight"]
    subm = sub[sub["gvkey"].isin(w.index)].copy()
    subm["w"] = subm["gvkey"].map(w).astype(float)
    subm = subm.dropna(subset=["w"]).copy()

    out = []
    for dv_kind, dvcol in [("cont", "UNCRES"), ("bin", "UNCRES_bin")]:
        for method, frame, wcol in [("normal", sub, None), ("psm", subm, "w")]:
            r = _fit(frame, reg_cols, dvcol, weights_col=wcol)
            r.update({"label": f"UNCRES_{dv_kind}_{method}_{arm}",
                      "dv_kind": dv_kind, "method": method, "arm": arm,
                      "median_threshold": med if dv_kind == "bin" else None})
            print(f"    {dv_kind:4s} {method:6s}: d={r['delta_hat']:+.5f} "
                  f"se={r['se']:.5f} p={r['pvalue']:.4f} N={r['nobs']:,} "
                  f"firms={r['n_firms']:,}")
            out.append(r)
    return out


def main() -> int:
    print("=" * 64)
    print("H1.5 — Brexit DiD UncResCEO FULL GRID "
          "{cont,bin} x {normal,PSM} x {buk,textual}")
    print("=" * 64)

    results: list[dict] = []
    print("\n-- MARKET arm (beta^UK tercile) --")
    results += _run_arm(_load_market_treatment(), "buk")
    print("\n-- TEXTUAL arm (Sec 1+7, >5/==0) --")
    results += _run_arm(_load_textual_treatment(), "textual")

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_dir = ROOT / "outputs" / "econometric" / SUITE_DIR_NAME / ts
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "suite_id": SUITE_ID,
        "title": ("Campello Brexit DiD on CEO residual uncertainty — full grid "
                  "{continuous, binary} x {normal, PSM} x {beta^UK tercile, textual}"),
        "dv_continuous": "UncResCEO (DWZ Eq.4 CEO Q&A residual; firm-qtr mean; not winsorized)",
        "dv_binary": "1[UncResCEO >= pooled per-arm median of the unmatched estimation sample]; LPM",
        "model": "eq-(14) clone: POSTxHIGH + 5 controls + FIRM FE + IND(FIC100)xQTR FE",
        "psm_method": ("3-NN with replacement on the 6 eq-14 controls (logit, "
                       "StandardScaler, pre-POST firm means); weighted eq-14 on "
                       "matched sub-panel; matcher imported verbatim from "
                       "run_h1_5_brexit_did_psm"),
        "se": "double-clustered firm x calendar-quarter",
        "panel": "2010Q1-2016Q4 full sample-period, POST=2016Q3-Q4",
        "results": results,
        "campello_note": "No Campello Table 8 benchmark for UncResCEO — novel "
                         "extension, not a replication; no verdict (gated on Sina)",
        "verdict_gated_on_sina": True,
        "timestamp": ts,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2),
                                          encoding="utf-8")
    print(f"\n-> {out_dir / 'summary.json'}  ({len(results)} cells)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
