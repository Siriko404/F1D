#!/usr/bin/env python3
"""
================================================================================
STAGE 4: H1.5 Campello Brexit DiD on CASH — Campello et al. (2022 JFQA) verbatim
================================================================================
ID: econometric/run_h1_5_brexit_did
Description: Difference-in-differences replicating Campello et al. (2022) JFQA
             Table 8 columns 1-2. Two treatment arms on the SAME eq-(14) panel:

             (1) MARKET arm: β^UK tercile (top vs bottom of nonnegative β^UK_i)
                 — eq(13) firm-by-firm OLS vol(r_it) on vol(FTSE100)+vol(SP500)+vol(FX)
                 — nonnegative rank tercile per paper: T=449, C=360 (asymmetric)
             (2) TEXTUAL arm: 10-K §1+7 Brexit keyword count (>5 vs ==0)
                 — 9 Campello keywords verbatim (3 body + 6 fn14)
                 — Item 1 (Business) + Item 7 (MD&A) per Campello App.-E convention

DV: CASH = cheq_t / (atq_{t-1} - cheq_{t-1}) — Table 8 caption "net of cash holdings"
Panel: 2010Q1-2016Q4 full sample-period, POST=2016Q3-Q4
FEs: FIRM + INDUSTRY(FIC100)×QUARTER
SE: double-clustered (firm × calendar-quarter)
Controls: Stock_Return, Tobin's_Q, Cash_Flow, Sales_Growth, log(Assets) — lagged 1Q
Consensus: IBES statsum MEANEST 1Q-ahead, pooled z-score (§G.8/G.9 ratified)
Winsor: 1% within cal_yr_qtr on final CASH ratio

Inputs:
    - outputs/campello_rebuild/step1_sample/<latest>/sample.parquet
    - outputs/campello_rebuild/step3_treatment/<latest>/treatment.parquet (market)
    - outputs/campello_rebuild/step3b3_textual_treatment_sec17/<latest>/treatment_textual.parquet (textual)
    - inputs/comp_na_daily_all/comp_na_daily_all.parquet (CASH DV source)
    - inputs/IBES_Summary_Statsum_Unadjusted/<IBES statsum files> (consensus)

Outputs:
    - outputs/econometric/h1_5_brexit_did/<timestamp>/summary.json
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

from step7_fullpanel_hypothesis import (
    FIRM_BUILDERS, POST_Q, _build, _calendar_lag1, _latest, _prev_q,
)

COMP = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
BUFFER_LO = pd.Timestamp("2008-01-01")
WIN_HI_DATE = pd.Timestamp("2016-12-31")
WINSOR = 0.01

# statsum MEANEST consensus (§G.8/G.9 ratified)
_p = ROOT / "scripts" / "campello_rebuild" / "_build_final_did_statsum_consensus.py"
_s = importlib.util.spec_from_file_location("_fin", _p)
_fin = importlib.util.module_from_spec(_s)
_s.loader.exec_module(_fin)
_statsum_meanest_z = _fin._statsum_meanest_z

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SUITE_ID = "H1.5.brexit_did"
SUITE_DIR_NAME = "h1_5_brexit_did"
SUITE_TITLE = (
    "Campello Brexit Referendum Difference-in-Differences: CASH Holdings "
    "(Campello et al. 2022 JFQA Table 8 cols.1-2 verbatim)"
)
SUITE_LABEL = "tab:h1_5_brexit_did"


# ==============================================================================
# T8 Net-of-Cash DV (Table 8 caption verbatim)
# ==============================================================================

def _cash_dv_t8() -> pd.DataFrame:
    """CASH = cheq_t / (atq_{t-1} - cheq_{t-1})."""
    df = pq.read_table(COMP, columns=["gvkey","datadate","curcdq","loc","consol",
                       "indfmt","datafmt","atq","cheq"]).to_pandas()
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
    return df[["gvkey","cal_yr_qtr","CASH"]]


# ==============================================================================
# DiD Runner (shared machinery — eq(14))
# ==============================================================================

def _build_and_fit(treatment_df, label: str) -> dict:
    """Build eq(14) panel, run PanelOLS, return result dict."""
    from linearmodels.panel import PanelOLS

    s1 = pd.read_parquet(_latest("step1_sample")/"sample.parquet",
                         columns=["gvkey","cal_yr_qtr","atq","fic100_industry_id"])
    s1["gvkey"] = s1["gvkey"].astype(str).str.zfill(6)

    tt = treatment_df.copy(); tt["gvkey"] = tt["gvkey"].astype(str).str.zfill(6)
    panel = s1.merge(tt[["gvkey","HIGH_UK_EXPOSURE"]], on="gvkey", how="inner")
    panel["POST"] = panel["cal_yr_qtr"].isin(POST_Q).astype(int)
    df = panel.merge(_cash_dv_t8(), on=["gvkey","cal_yr_qtr"], how="inner")
    df = df[df["atq"]>0].copy(); df["log_assets"] = np.log(df["atq"])

    firm_cols = []
    for cls in FIRM_BUILDERS:
        b = _build(cls); col = [c for c in b.columns if c not in ("gvkey","cal_yr_qtr")][0]
        df = df.merge(_calendar_lag1(b, col), on=["gvkey","cal_yr_qtr"], how="left")
        firm_cols.append(col)
    df = df.merge(_calendar_lag1(
        df[["gvkey","cal_yr_qtr","log_assets"]], "log_assets").rename(
        columns={"log_assets":"log_assets_l1"}), on=["gvkey","cal_yr_qtr"], how="left")
    firm_cols.append("log_assets_l1")

    cons = _statsum_meanest_z()
    df = df.merge(_calendar_lag1(cons, "cons_fwd"),
                  on=["gvkey","cal_yr_qtr"], how="left")
    # Winsorize 1% POOLED across all firm-quarters (Sina-ratified 2026-05-31).
    # Was within-cal-quarter, which clipped the post-Brexit (2016Q3-Q4) treated
    # cash spikes inside that quarter and FLIPPED the market arm sign negative
    # (diagnostic tmp/_diag_winsor_did.py: within −0.013 → pooled +0.018). Paper
    # is SILENT on the winsor dimension; pooled is the standard finance default.
    df["CASH"] = df["CASH"].clip(df["CASH"].quantile(WINSOR),
                                 df["CASH"].quantile(1 - WINSOR))
    df["POST_x_HIGH"] = (df["POST"]*df["HIGH_UK_EXPOSURE"]).astype(float)
    df["indqtr_code"] = ((df["fic100_industry_id"].astype("int64").astype(str)
                          +"_"+df["cal_yr_qtr"].astype(str)).astype("category").cat.codes)

    reg_cols = ["POST_x_HIGH"] + firm_cols + ["cons_fwd"]
    sub = df.dropna(subset=["CASH","indqtr_code"]+reg_cols).copy()
    pdat = sub.set_index(["gvkey","cal_yr_qtr"]).sort_index()
    nf = sub["gvkey"].nunique()

    res = PanelOLS(pdat["CASH"], pdat[reg_cols], entity_effects=True,
                   other_effects=pdat["indqtr_code"], drop_absorbed=True
                   ).fit(cov_type="clustered", cluster_entity=True, cluster_time=True)

    b = float(res.params["POST_x_HIGH"]); se = float(res.std_errors["POST_x_HIGH"])
    t = float(res.tstats["POST_x_HIGH"]); p = float(res.pvalues["POST_x_HIGH"])
    coefs = [{"name": c, "coef": float(res.params[c]), "se": float(res.std_errors[c]),
              "t": float(res.tstats[c]), "pvalue": float(res.pvalues[c])}
             for c in res.params.index]

    nT_est = int(sub[sub["HIGH_UK_EXPOSURE"]==1]["gvkey"].nunique())
    nC_est = int(sub[sub["HIGH_UK_EXPOSURE"]==0]["gvkey"].nunique())
    nT_treat = int((treatment_df["HIGH_UK_EXPOSURE"]==1).sum())
    nC_treat = int((treatment_df["HIGH_UK_EXPOSURE"]==0).sum())

    return {"label": label, "delta_hat": b, "se": se, "t": t, "pvalue": p,
            "nobs": int(res.nobs), "n_firms": int(nf),
            "rsquared_within": float(res.rsquared_within),
            "nT_treat": nT_treat, "nC_treat": nC_treat,
            "nT_est": nT_est, "nC_est": nC_est,
            "controls": reg_cols, "coefficients": coefs,
            "consensus_variant": "cons_fwd"}


# ==============================================================================
# Treatment Loading
# ==============================================================================

def _load_market_treatment() -> pd.DataFrame:
    """β^UK tercile treatment — step1-filtered, treated + control only."""
    trt = pd.read_parquet(_latest("step3_treatment")/"treatment.parquet",
                          columns=["gvkey","group","in_step1"])
    trt["gvkey"] = trt["gvkey"].astype(str).str.zfill(6)
    tc = trt[trt["in_step1"] & trt["group"].isin(["treated","control"])].copy()
    tc["HIGH_UK_EXPOSURE"] = (tc["group"]=="treated").astype(int)
    return tc


def _load_textual_treatment() -> pd.DataFrame:
    """§1+7 textual treatment — >5/==0 rule, Campello house convention."""
    tt = pd.read_parquet(_latest("step3b3_textual_treatment_sec17")/"treatment_textual.parquet")
    tt["gvkey"] = tt["gvkey"].astype(str).str.zfill(6)
    tt = tt[tt["group"].isin(["treated","control"])].copy()
    return tt


# ==============================================================================
# Main
# ==============================================================================

def main() -> int:
    print("="*64)
    print("H1.5 — Campello Brexit DiD on CASH (Table 8 cols.1-2)")
    print("="*64)

    results = []

    # --- MARKET ARM (β^UK-tercile) ---
    print("\n── MARKET arm (β^UK-tercile treatment) ──")
    mkt = _load_market_treatment()
    print(f"  T={int((mkt.HIGH_UK_EXPOSURE==1).sum()):,}  "
          f"C={int((mkt.HIGH_UK_EXPOSURE==0).sum()):,}  "
          f"src=step3_treatment")
    r_mkt = _build_and_fit(mkt, "CASH_buk_tercile")
    results.append(r_mkt)
    print(f"  δ={r_mkt['delta_hat']:+.5f}  SE={r_mkt['se']:.5f}  "
          f"t={r_mkt['t']:+.3f}  p={r_mkt['pvalue']:.4f}  "
          f"N={r_mkt['nobs']:,}  firms={r_mkt['n_firms']:,}  "
          f"R²w={r_mkt['rsquared_within']:.4f}")

    # --- TEXTUAL ARM (§1+7) ---
    print("\n── TEXTUAL arm (§1+7, >5/==0) ──")
    txt = _load_textual_treatment()
    print(f"  T={int((txt.HIGH_UK_EXPOSURE==1).sum()):,}  "
          f"C={int((txt.HIGH_UK_EXPOSURE==0).sum()):,}  "
          f"src=step3b3_textual_treatment_sec17")
    r_txt = _build_and_fit(txt, "CASH_textual_sec17")
    results.append(r_txt)
    print(f"  δ={r_txt['delta_hat']:+.5f}  SE={r_txt['se']:.5f}  "
          f"t={r_txt['t']:+.3f}  p={r_txt['pvalue']:.4f}  "
          f"N={r_txt['nobs']:,}  firms={r_txt['n_firms']:,}  "
          f"R²w={r_txt['rsquared_within']:.4f}")

    # --- WRITE OUTPUTS ---
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_dir = ROOT / "outputs" / "econometric" / SUITE_DIR_NAME / ts
    out_dir.mkdir(parents=True, exist_ok=True)

    # Campello paper benchmarks (programmatic extraction from table8_pdfpage31.txt)
    camp_buk = {"cash_delta": 0.231, "se": 0.047, "n": 17170, "rsquared": 0.21,
                "stars": "***", "source": "Campello Table 8 col.1 (β^UK-tercile CASH)"}
    camp_txt = {"cash_delta": 0.357, "se": 0.062, "n": 24195, "rsquared": 0.24,
                "stars": "***", "source": "Campello Table 8 col.2 (textual CASH)"}

    # Treatment counts for the summary
    mkt_counts = {"treated": int((mkt["HIGH_UK_EXPOSURE"]==1).sum()),
                  "control": int((mkt["HIGH_UK_EXPOSURE"]==0).sum())}
    txt_counts = {"treated": int((txt["HIGH_UK_EXPOSURE"]==1).sum()),
                  "control": int((txt["HIGH_UK_EXPOSURE"]==0).sum())}
    camp_mkt_ref = {"treated": 449, "control": 360}
    camp_txt_ref = {"treated": 807, "control": 433}

    summary = {
        "suite_id": SUITE_ID,
        "title": SUITE_TITLE,
        "dv": "CASH = cheq_t / (atq_{t-1} - cheq_{t-1}) — Table 8 net-of-cash",
        "dv_tex": r"$cheq_t/(atq_{t-1} - cheq_{t-1})$ (Table-8 net-of-cash)",
        "model": "eq-(14): POST×HIGH_UK_EXPOSURE + 5 controls + FIRM FE + IND×QTR FE",
        "panel": "2010Q1-2016Q4 full sample-period, POST=2016Q3-Q4",
        "se": "double-clustered firm × calendar-quarter",
        "results": results,
        "campello_reference_buk": camp_buk,
        "campello_reference_textual": camp_txt,
        "treatment_counts": {
            "market": {"rebuild": mkt_counts, "campello": camp_mkt_ref,
                       "src": "step3_treatment asymmetric tercile (nonneg β^UK)"},
            "textual": {"rebuild": txt_counts, "campello": camp_txt_ref,
                        "src": "step3b3_textual_treatment_sec17 (§1+7, >5/==0)"},
        },
        "verdict_gated_on_sina": True,
    }

    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\n→ {out_dir / 'summary.json'}")
    print(f"\n  MARKET  β^UK-tercile  δ={r_mkt['delta_hat']:+.4f}  "
          f"({r_mkt['se']:.4f})  N={r_mkt['nobs']:,}  "
          f"Paper {camp_buk['cash_delta']:+.3f}{camp_buk['stars']}  N={camp_buk['n']:,}")
    print(f"  TEXTUAL §1+7          δ={r_txt['delta_hat']:+.4f}  "
          f"({r_txt['se']:.4f})  N={r_txt['nobs']:,}  "
          f"Paper {camp_txt['cash_delta']:+.3f}{camp_txt['stars']}  N={camp_txt['n']:,}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
