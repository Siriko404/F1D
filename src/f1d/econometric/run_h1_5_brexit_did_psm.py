#!/usr/bin/env python3
"""
================================================================================
STAGE 4b: H1.5 Campello Brexit DiD on CASH — PSM-matched robustness branch
================================================================================
ID: econometric/run_h1_5_brexit_did_psm
Description: Propensity-score-matched version of the eq-(14) cash DiD
             (run_h1_5_brexit_did). Robustness analogue of Campello et al.
             (2022 JFQA) Supplementary Tables C.2/C.3.

             Campello run their PSM (Table C.3) on INVESTMENT / EMPLOYMENT /
             R&D / DIVESTITURES — NOT on cash. Applying PSM to the CASH DV is
             OUR extension (the paper's main cash result, Table 8, is unmatched
             eq-14). Flag accordingly in any write-up.

PSM SPEC (verbatim disclosure, JFQA Supplementary Tables C.2/C.3 notes):
    - propensity = f(lagged STOCK_RETURNS, 1q-ahead CONSENSUS_EARNINGS_FORECAST,
      TOBIN_Q, CASH_FLOW, SALES_GROWTH, SIZE)   ← exactly our 6 eq-14 controls
    - each treated firm matched to 3 control firms (nearest neighbour) WITH
      replacement
    - "nonparametric"; logit/probit link, caliper, and the covariate
      measurement date are NOT STATED in the paper.

OUR underdetermined choices (paper-silent → flagged, easy to vary):
    - propensity link: sklearn LogisticRegression (logit), StandardScaler on the
      6 covariates (same convention as the existing Chen PSM builder).
    - covariate measurement: each firm's PRE-POST mean (all quarters strictly
      before 2016Q3) of the lagged eq-14 controls. Pre-treatment firm summary,
      consistent with eq-14's CONTROLS_{t-1}.
    - matched sample = all treated firms (weight 1) + every control firm matched
      ≥1× (weight = number of treated firms it was matched to, honouring
      3-NN-with-replacement multiplicity). eq-14 then run WEIGHTED on that
      sub-panel; everything else (DV, FE, SE, winsor) identical to the main
      runner via its _build_and_fit panel construction, re-implemented here so
      the production runner stays untouched.

Outputs:
    - outputs/econometric/h1_5_brexit_did_psm/<timestamp>/summary.json
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
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "campello_rebuild"))

from step7_fullpanel_hypothesis import (  # noqa: E402
    FIRM_BUILDERS, POST_Q, _build, _calendar_lag1, _latest, _prev_q,
)

COMP = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
BUFFER_LO = pd.Timestamp("2008-01-01")
WIN_HI_DATE = pd.Timestamp("2016-12-31")

# Reuse the production runner's DV + treatment loaders + consensus (no fork).
_pp = ROOT / "src" / "f1d" / "econometric" / "run_h1_5_brexit_did.py"
_ps = importlib.util.spec_from_file_location("_prod_brexit", _pp)
_prod = importlib.util.module_from_spec(_ps)
_ps.loader.exec_module(_prod)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

WINSOR = 0.01
N_NEIGHBORS = 3        # Campello: "matched to 3 control firms"
PRE_POST_MAX = min(POST_Q)  # firm covariate window = cal_yr_qtr < 2016Q3

SUITE_ID = "H1.5.brexit_did_psm"
SUITE_DIR_NAME = "h1_5_brexit_did_psm"


# ==============================================================================
# Panel build (covariates merged, pre-regression) — mirrors _build_and_fit
# ==============================================================================

def _cash_t1() -> pd.DataFrame:
    """CASH_T1 = cheq_t / atq_{t-1} (Campello Table 1 / Table C.2 summary-stat
    definition — gross cash over lagged assets; distinct from the Table-8
    regression DV). For the matched-summary CASH comparison only."""
    df = pq.read_table(COMP, columns=["gvkey", "datadate", "curcdq", "loc",
                       "consol", "indfmt", "datafmt", "atq", "cheq"]).to_pandas()
    df["datadate"] = pd.to_datetime(df["datadate"], errors="coerce")
    df = df[(df["datadate"] >= BUFFER_LO) & (df["datadate"] <= WIN_HI_DATE)]
    df = df[(df["curcdq"] == "USD") & (df["loc"] == "USA") & (df["consol"] == "C")
            & (df["indfmt"] == "INDL") & (df["datafmt"] == "STD")].copy()
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
    df = df[df["cheq"].notna() & (df["atq_l1"] > 0)].copy()
    df["CASH_T1"] = df["cheq"] / df["atq_l1"]
    return df[["gvkey", "cal_yr_qtr", "CASH_T1"]]


def _build_panel(treatment_df: pd.DataFrame):
    """Return (df, firm_cols, reg_cols): eq-14 panel with all 6 lagged controls
    merged, winsorized CASH, POST_x_HIGH and indqtr_code, BEFORE regression."""
    s1 = pd.read_parquet(_latest("step1_sample") / "sample.parquet",
                         columns=["gvkey", "cal_yr_qtr", "atq",
                                  "fic100_industry_id"])
    s1["gvkey"] = s1["gvkey"].astype(str).str.zfill(6)

    tt = treatment_df.copy(); tt["gvkey"] = tt["gvkey"].astype(str).str.zfill(6)
    panel = s1.merge(tt[["gvkey", "HIGH_UK_EXPOSURE"]], on="gvkey", how="inner")
    panel["POST"] = panel["cal_yr_qtr"].isin(POST_Q).astype(int)
    df = panel.merge(_prod._cash_dv_t8(), on=["gvkey", "cal_yr_qtr"], how="inner")
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

    cons = _prod._statsum_meanest_z()
    df = df.merge(_calendar_lag1(cons, "cons_fwd"),
                  on=["gvkey", "cal_yr_qtr"], how="left")
    # pooled 1% winsor (production parity, commit 59fb6b6)
    df["CASH"] = df["CASH"].clip(df["CASH"].quantile(WINSOR),
                                 df["CASH"].quantile(1 - WINSOR))
    df["POST_x_HIGH"] = (df["POST"] * df["HIGH_UK_EXPOSURE"]).astype(float)
    df["indqtr_code"] = ((df["fic100_industry_id"].astype("int64").astype(str)
                          + "_" + df["cal_yr_qtr"].astype(str))
                         .astype("category").cat.codes)
    # CASH_T1 for matched-summary comparison only (NOT used in regression)
    df = df.merge(_cash_t1(), on=["gvkey", "cal_yr_qtr"], how="left")
    reg_cols = ["POST_x_HIGH"] + firm_cols + ["cons_fwd"]
    return df, firm_cols, reg_cols


# ==============================================================================
# PSM: firm-level propensity + 3-NN with replacement
# ==============================================================================

def _firm_propensity(df: pd.DataFrame, cov_cols: list[str]) -> pd.DataFrame:
    """Pre-POST firm mean of the 6 covariates → logit propensity score.
    Returns firm-level frame (gvkey, HIGH_UK_EXPOSURE, *cov_cols, p_score)."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler

    pre = df[df["cal_yr_qtr"] < PRE_POST_MAX]
    # CASH (T8) + CASH_T1 carried for matched-summary only (NOT covariates)
    firm = (pre.groupby("gvkey", as_index=False)
               .agg({"HIGH_UK_EXPOSURE": "first", "CASH": "mean",
                     "CASH_T1": "mean", **{c: "mean" for c in cov_cols}}))
    firm = firm.dropna(subset=cov_cols).reset_index(drop=True)

    X = StandardScaler().fit_transform(firm[cov_cols].to_numpy(dtype=float))
    y = firm["HIGH_UK_EXPOSURE"].astype(int).to_numpy()
    lr = LogisticRegression(max_iter=2000, solver="lbfgs", C=1.0)
    lr.fit(X, y)
    firm["p_score"] = lr.predict_proba(X)[:, 1]
    return firm


def _match_3nn_replacement(firm: pd.DataFrame) -> pd.DataFrame:
    """Each treated firm → 3 nearest control firms by |p_score|, WITH
    replacement. Returns firm-level (gvkey, role, weight) for the matched
    sample: treated weight 1; control weight = times matched."""
    t = firm[firm["HIGH_UK_EXPOSURE"] == 1]
    c = firm[firm["HIGH_UK_EXPOSURE"] == 0]
    cp = c["p_score"].to_numpy()
    cg = c["gvkey"].to_numpy()

    counts: dict[str, int] = {}
    for p in t["p_score"].to_numpy():
        nn = np.argsort(np.abs(cp - p))[:N_NEIGHBORS]
        for j in nn:
            counts[cg[j]] = counts.get(cg[j], 0) + 1

    rows = [{"gvkey": g, "role": "treated", "weight": 1.0}
            for g in t["gvkey"]]
    rows += [{"gvkey": g, "role": "control", "weight": float(w)}
             for g, w in counts.items()]
    return pd.DataFrame(rows)


def _balance(firm: pd.DataFrame, matched: pd.DataFrame,
             cov_cols: list[str]) -> list[dict]:
    """Standardized mean difference (treated − control)/pooled-sd, before vs
    after matching (weighted), per covariate."""
    def smd(sub_t, sub_c, w_c=None):
        mt = sub_t.mean()
        if w_c is None:
            mc = sub_c.mean(); sc = sub_c.std()
        else:
            mc = np.average(sub_c, weights=w_c)
            sc = np.sqrt(np.average((sub_c - mc) ** 2, weights=w_c))
        sp = np.sqrt(0.5 * (sub_t.std() ** 2 + sc ** 2))
        return float((mt - mc) / sp) if sp > 0 else 0.0

    mt_firm = firm.set_index("gvkey")
    m = matched.merge(firm, on="gvkey", how="left")
    mt = m[m["role"] == "treated"]
    mc = m[m["role"] == "control"]
    out = []
    for col in cov_cols:
        pre = smd(mt_firm[mt_firm.HIGH_UK_EXPOSURE == 1][col],
                  mt_firm[mt_firm.HIGH_UK_EXPOSURE == 0][col])
        post = smd(mt[col], mc[col], w_c=mc["weight"].to_numpy())
        out.append({"covariate": col, "smd_prematch": round(pre, 4),
                    "smd_postmatch": round(post, 4)})
    return out


# ==============================================================================
# Weighted eq-14 fit on the matched sub-panel
# ==============================================================================

def _fit_matched(df: pd.DataFrame, reg_cols: list[str],
                 matched: pd.DataFrame, label: str) -> dict:
    from linearmodels.panel import PanelOLS

    w = matched.set_index("gvkey")["weight"]
    sub = df[df["gvkey"].isin(w.index)].copy()
    sub["w"] = sub["gvkey"].map(w).astype(float)
    sub = sub.dropna(subset=["CASH", "indqtr_code", "w"] + reg_cols).copy()
    pdat = sub.set_index(["gvkey", "cal_yr_qtr"]).sort_index()

    res = PanelOLS(pdat["CASH"], pdat[reg_cols], entity_effects=True,
                   other_effects=pdat["indqtr_code"], weights=pdat["w"],
                   drop_absorbed=True
                   ).fit(cov_type="clustered", cluster_entity=True,
                         cluster_time=True)

    b = float(res.params["POST_x_HIGH"]); se = float(res.std_errors["POST_x_HIGH"])
    coefs = [{"name": c, "coef": float(res.params[c]),
              "se": float(res.std_errors[c]), "t": float(res.tstats[c]),
              "pvalue": float(res.pvalues[c])} for c in res.params.index]
    return {"label": label, "delta_hat": b, "se": se,
            "t": float(res.tstats["POST_x_HIGH"]),
            "pvalue": float(res.pvalues["POST_x_HIGH"]),
            "nobs": int(res.nobs), "n_firms": int(sub["gvkey"].nunique()),
            "rsquared_within": float(res.rsquared_within),
            "coefficients": coefs,
            "nT_firms": int((matched["role"] == "treated").sum()),
            "nC_firms": int((matched["role"] == "control").sum()),
            "control_weight_sum": float(
                matched.loc[matched.role == "control", "weight"].sum())}


def _matched_summary(firm: pd.DataFrame, matched: pd.DataFrame,
                     cov_cols: list[str]) -> list[dict]:
    """C.2-style matched-sample means: treated vs weighted matched-control,
    per covariate + CASH (our units; see table notes for CASH/consensus)."""
    m = matched.merge(firm, on="gvkey", how="left")
    t = m[m["role"] == "treated"]
    c = m[m["role"] == "control"]

    def _wmean(s: pd.Series, w: pd.Series) -> float:
        ok = s.notna().to_numpy()
        return float(np.average(s.to_numpy()[ok], weights=w.to_numpy()[ok]))

    out = []
    for col in cov_cols + ["CASH", "CASH_T1"]:
        out.append({"variable": col,
                    "ours_treated": float(t[col].mean()),
                    "ours_control": _wmean(c[col], c["weight"])})
    return out


def _run_arm(treatment_df: pd.DataFrame, label: str) -> dict:
    df, firm_cols, reg_cols = _build_panel(treatment_df)
    cov_cols = firm_cols + ["cons_fwd"]
    firm = _firm_propensity(df, cov_cols)
    matched = _match_3nn_replacement(firm)
    res = _fit_matched(df, reg_cols, matched, label)
    res["balance"] = _balance(firm, matched, cov_cols)
    res["matched_summary"] = _matched_summary(firm, matched, cov_cols)
    res["n_treated_scored"] = int((firm["HIGH_UK_EXPOSURE"] == 1).sum())
    res["n_control_scored"] = int((firm["HIGH_UK_EXPOSURE"] == 0).sum())
    return res


# ==============================================================================
# Main
# ==============================================================================

def main() -> int:
    print("=" * 64)
    print("H1.5 — Campello Brexit DiD on CASH, PSM-matched (3-NN w/ replacement)")
    print("=" * 64)

    arms = [
        ("MARKET (β^UK-tercile)", _prod._load_market_treatment(),
         "CASH_psm_buk_tercile"),
        ("TEXTUAL (§1+7, >5/==0)", _prod._load_textual_treatment(),
         "CASH_psm_textual_sec17"),
    ]
    results = []
    for name, trt, lab in arms:
        print(f"\n── {name} ──")
        print(f"  pre-match T={int((trt.HIGH_UK_EXPOSURE==1).sum()):,}  "
              f"C={int((trt.HIGH_UK_EXPOSURE==0).sum()):,}")
        r = _run_arm(trt, lab)
        results.append(r)
        print(f"  matched: T_firms={r['nT_firms']:,}  "
              f"C_firms={r['nC_firms']:,} (Σw={r['control_weight_sum']:.0f})")
        print(f"  δ={r['delta_hat']:+.5f}  SE={r['se']:.5f}  "
              f"t={r['t']:+.3f}  p={r['pvalue']:.4f}  N={r['nobs']:,}  "
              f"R²w={r['rsquared_within']:.4f}")
        print("  balance (SMD pre→post):")
        for bd in r["balance"]:
            print(f"    {bd['covariate']:<16} {bd['smd_prematch']:+.3f} → "
                  f"{bd['smd_postmatch']:+.3f}")

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_dir = ROOT / "outputs" / "econometric" / SUITE_DIR_NAME / ts
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "suite_id": SUITE_ID,
        "dv": "CASH = cheq_t / (atq_{t-1} - cheq_{t-1}) — Table 8 net-of-cash",
        "method": ("PSM 3-NN with replacement on 6 eq-14 controls "
                   "(logit, StandardScaler), pre-POST firm means; "
                   "weighted eq-14 on matched sub-panel"),
        "psm_spec_source": "JFQA Supplementary Tables C.2/C.3 notes (verbatim)",
        "extension_note": ("Campello PSM (C.3) is on investment/employment/R&D/"
                           "divestitures, NOT cash; PSM-on-cash is our extension"),
        "n_neighbors": N_NEIGHBORS,
        "covariate_window": f"cal_yr_qtr < {PRE_POST_MAX} firm mean (paper-silent)",
        "campello_reference_buk": {"cash_delta": 0.231, "se": 0.047,
            "stars": "***", "note": "Table 8 col.1 UNMATCHED (no cash PSM in paper)"},
        "campello_reference_textual": {"cash_delta": 0.357, "se": 0.062,
            "stars": "***", "note": "Table 8 col.2 UNMATCHED (no cash PSM in paper)"},
        "results": results,
        "verdict_gated_on_sina": True,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2),
                                          encoding="utf-8")
    print(f"\n→ {out_dir / 'summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
