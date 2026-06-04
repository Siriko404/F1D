#!/usr/bin/env python3
"""
================================================================================
STAGE 4b: H1.5 Campello Brexit DiD on UncResCEO — Campello et al. (2022 JFQA)
          eq-(14) clone with CEO residual uncertainty as DV
================================================================================
ID: econometric/run_h1_5_brexit_did_uncres
Description: CLONE of run_h1_5_brexit_did.py — same canonical eq-(14) panel,
             same controls, same FEs, same SE clustering. ONLY the DV differs:
             UncResCEO (DWZ Eq.4 CEO Q&A call-level residual) instead of CASH.
             Novel extension — no Campello Table 8 benchmark exists for this DV
             (Table 8 = CASH / NWC / PROFITS). NOT a replication; factual output
             only, no verdict (gated on Sina).

             Two treatment arms on the SAME eq-(14) panel:

             (1) MARKET arm: beta^UK tercile (top vs bottom of nonnegative beta^UK_i)
                 — eq(13) firm-by-firm OLS vol(r_it) on vol(FTSE100)+vol(SP500)+vol(FX)
                 — nonnegative rank tercile per paper: T=449, C=360 (asymmetric)
             (2) TEXTUAL arm: 10-K Sec 1+7 Brexit keyword count (>5 vs ==0)
                 — 9 Campello keywords verbatim (3 body + 6 fn14)
                 — Item 1 (Business) + Item 7 (MD&A) per Campello App.-E convention

DV: UncResCEO = DWZ Eq.4 CEO Q&A call-level residual, mean per (gvkey, cal_yr_qtr)
    Bridged via H1 panel (file_name -> gvkey). NO winsorization (pre-cleaned residual).
Panel: 2010Q1-2016Q4 full sample-period, POST=2016Q3-Q4
FEs: FIRM + INDUSTRY(FIC100)xQUARTER
SE: double-clustered (firm x calendar-quarter)
Controls: Stock_Return, Tobin's_Q, Cash_Flow, Sales_Growth, log(Assets) — lagged 1Q
Consensus: IBES statsum MEANEST 1Q-ahead, pooled z-score (Sec G.8/G.9 ratified), lagged 1Q

Inputs:
    - outputs/campello_rebuild/step1_sample/<latest>/sample.parquet
    - outputs/campello_rebuild/step3_treatment/<latest>/treatment.parquet (market)
    - outputs/campello_rebuild/step3b3_textual_treatment_sec17/<latest>/treatment_textual.parquet (textual)
    - outputs/econometric/ceo_clarity_extended/<latest>/ceo_clarity_residual.parquet (UncResCEO)
    - outputs/variables/h1_cash_holdings/<latest>/h1_cash_holdings_panel.parquet (bridge)
    - inputs/IBES_Summary_Statsum_Unadjusted/<IBES statsum files> (consensus)

Outputs:
    - outputs/econometric/h1_5_brexit_did_uncres/<timestamp>/summary.json
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

from step7_fullpanel_hypothesis import (
    FIRM_BUILDERS, POST_Q, _build, _calendar_lag1, _latest, _prev_q,
)

# statsum MEANEST consensus (Sec G.8/G.9 ratified) — same as CASH runner
_p = ROOT / "scripts" / "campello_rebuild" / "_build_final_did_statsum_consensus.py"
_s = importlib.util.spec_from_file_location("_fin", _p)
_fin = importlib.util.module_from_spec(_s)
_s.loader.exec_module(_fin)
_statsum_meanest_z = _fin._statsum_meanest_z

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SUITE_ID = "H1.5.brexit_did_uncres"
SUITE_DIR_NAME = "h1_5_brexit_did_uncres"
SUITE_TITLE = (
    "Campello Brexit Referendum Difference-in-Differences: CEO Residual "
    "Uncertainty (DWZ Eq.4) — Campello et al. (2022 JFQA) eq-(14) clone, "
    "novel extension (no Campello benchmark)"
)
SUITE_LABEL = "tab:h1_5_brexit_did_uncres"


# ==============================================================================
# UncResCEO DV — ClarityResidualEngine + H1 bridge
# ==============================================================================

def _uncres_dv() -> pd.DataFrame:
    """UncResCEO per (gvkey, cal_yr_qtr); NO winsorization (pre-cleaned residual).

    Reuses ClarityResidualEngine (cached) + validated H1 panel as
    file_name->gvkey bridge (Sina-locked 2026-05-17).
    """
    from f1d.shared.variables._clarity_residual_engine import get_engine
    from f1d.shared.path_utils import get_latest_output_dir

    resid = get_engine().get_ceo_residuals(ROOT)[
        ["file_name", "UncResCEO"]].copy()
    print(f"  ceo_clarity_residual: {len(resid):,} calls")

    panel_dir = get_latest_output_dir(
        ROOT / "outputs" / "variables" / "h1_cash_holdings",
        required_file="h1_cash_holdings_panel.parquet")
    bridge = pd.read_parquet(panel_dir / "h1_cash_holdings_panel.parquet",
                             columns=["file_name", "gvkey", "start_date"])
    print(f"  H1 bridge: {panel_dir.name}  ({len(bridge):,} rows)")

    df = bridge.merge(resid, on="file_name", how="inner")
    df = df[df["UncResCEO"].notna()].copy()
    df["gvkey"] = (pd.to_numeric(df["gvkey"], errors="coerce")
                   .astype("Int64").astype(str).str.zfill(6))
    df = df[df["gvkey"] != "<NA>"]
    df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
    df = df[df["start_date"].notna()]
    df["cal_yr_qtr"] = (df["start_date"].dt.year * 10
                        + df["start_date"].dt.quarter).astype("int64")
    out = (df.groupby(["gvkey", "cal_yr_qtr"], observed=True)["UncResCEO"]
             .mean().reset_index().rename(columns={"UncResCEO": "UNCRES"}))
    return out[["gvkey", "cal_yr_qtr", "UNCRES"]]


# ==============================================================================
# DiD Runner (shared machinery — eq(14) clone)
# ==============================================================================

def _build_and_fit(treatment_df, label: str) -> dict:
    """Build eq(14) panel, run PanelOLS with UncResCEO DV, return result dict."""
    from linearmodels.panel import PanelOLS

    s1 = pd.read_parquet(_latest("step1_sample")/"sample.parquet",
                         columns=["gvkey","cal_yr_qtr","atq","fic100_industry_id"])
    s1["gvkey"] = s1["gvkey"].astype(str).str.zfill(6)

    tt = treatment_df.copy(); tt["gvkey"] = tt["gvkey"].astype(str).str.zfill(6)
    panel = s1.merge(tt[["gvkey","HIGH_UK_EXPOSURE"]], on="gvkey", how="inner")
    panel["POST"] = panel["cal_yr_qtr"].isin(POST_Q).astype(int)
    df = panel.merge(_uncres_dv(), on=["gvkey","cal_yr_qtr"], how="inner")
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

    # NO winsorization on UNCRES (pre-cleaned residual)
    df["POST_x_HIGH"] = (df["POST"]*df["HIGH_UK_EXPOSURE"]).astype(float)
    df["indqtr_code"] = ((df["fic100_industry_id"].astype("int64").astype(str)
                          +"_"+df["cal_yr_qtr"].astype(str)).astype("category").cat.codes)

    reg_cols = ["POST_x_HIGH"] + firm_cols + ["cons_fwd"]
    sub = df.dropna(subset=["UNCRES","indqtr_code"]+reg_cols).copy()
    pdat = sub.set_index(["gvkey","cal_yr_qtr"]).sort_index()
    nf = sub["gvkey"].nunique()

    res = PanelOLS(pdat["UNCRES"], pdat[reg_cols], entity_effects=True,
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
# Treatment Loading (identical to CASH runner)
# ==============================================================================

def _load_market_treatment() -> pd.DataFrame:
    """beta^UK tercile treatment — step1-filtered, treated + control only."""
    trt = pd.read_parquet(_latest("step3_treatment")/"treatment.parquet",
                          columns=["gvkey","group","in_step1"])
    trt["gvkey"] = trt["gvkey"].astype(str).str.zfill(6)
    tc = trt[trt["in_step1"] & trt["group"].isin(["treated","control"])].copy()
    tc["HIGH_UK_EXPOSURE"] = (tc["group"]=="treated").astype(int)
    return tc


def _load_textual_treatment() -> pd.DataFrame:
    """Sec 1+7 textual treatment — >5/==0 rule, Campello house convention."""
    tt = pd.read_parquet(_latest("step3b3_textual_treatment_sec17")/"treatment_textual.parquet")
    tt["gvkey"] = tt["gvkey"].astype(str).str.zfill(6)
    tt = tt[tt["group"].isin(["treated","control"])].copy()
    return tt


# ==============================================================================
# Main
# ==============================================================================

def main() -> int:
    print("="*64)
    print("H1.5 — Campello Brexit DiD on UncResCEO (eq-14 clone, novel extension)")
    print("="*64)

    results = []

    # --- MARKET ARM (beta^UK-tercile) ---
    print("\n── MARKET arm (beta^UK-tercile treatment) ──")
    mkt = _load_market_treatment()
    print(f"  T={int((mkt.HIGH_UK_EXPOSURE==1).sum()):,}  "
          f"C={int((mkt.HIGH_UK_EXPOSURE==0).sum()):,}  "
          f"src=step3_treatment")
    r_mkt = _build_and_fit(mkt, "UNCRES_buk_tercile")
    results.append(r_mkt)
    print(f"  d={r_mkt['delta_hat']:+.5f}  SE={r_mkt['se']:.5f}  "
          f"t={r_mkt['t']:+.3f}  p={r_mkt['pvalue']:.4f}  "
          f"N={r_mkt['nobs']:,}  firms={r_mkt['n_firms']:,}  "
          f"R2w={r_mkt['rsquared_within']:.4f}")

    # --- TEXTUAL ARM (Sec 1+7) ---
    print("\n── TEXTUAL arm (Sec 1+7, >5/==0) ──")
    txt = _load_textual_treatment()
    print(f"  T={int((txt.HIGH_UK_EXPOSURE==1).sum()):,}  "
          f"C={int((txt.HIGH_UK_EXPOSURE==0).sum()):,}  "
          f"src=step3b3_textual_treatment_sec17")
    r_txt = _build_and_fit(txt, "UNCRES_textual_sec17")
    results.append(r_txt)
    print(f"  d={r_txt['delta_hat']:+.5f}  SE={r_txt['se']:.5f}  "
          f"t={r_txt['t']:+.3f}  p={r_txt['pvalue']:.4f}  "
          f"N={r_txt['nobs']:,}  firms={r_txt['n_firms']:,}  "
          f"R2w={r_txt['rsquared_within']:.4f}")

    # --- WRITE OUTPUTS ---
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_dir = ROOT / "outputs" / "econometric" / SUITE_DIR_NAME / ts
    out_dir.mkdir(parents=True, exist_ok=True)

    # Treatment counts for the summary
    mkt_counts = {"treated": int((mkt["HIGH_UK_EXPOSURE"]==1).sum()),
                  "control": int((mkt["HIGH_UK_EXPOSURE"]==0).sum())}
    txt_counts = {"treated": int((txt["HIGH_UK_EXPOSURE"]==1).sum()),
                  "control": int((txt["HIGH_UK_EXPOSURE"]==0).sum())}

    summary = {
        "suite_id": SUITE_ID,
        "title": SUITE_TITLE,
        "dv": "UncResCEO (DWZ Eq.4 CEO Q&A call-level residual); mean per "
              "(gvkey,cal_yr_qtr); NOT winsorized (pre-cleaned residual)",
        "dv_tex": (r"UncResCEO (DWZ Eq.4 CEO Q\&A residual, "
                   r"file-name$\rightarrow$gvkey via H1 panel, "
                   r"firm-quarter mean, not winsorized)"),
        "dv_bridge": "file_name->gvkey via h1_cash_holdings_panel.parquet; "
                     "call->quarter = calendar qtr of start_date "
                     "(Sina-locked 2026-05-17)",
        "model": "eq-(14) clone: POSTxHIGH_UK_EXPOSURE + 5 controls + FIRM FE + INDxQTR FE",
        "panel": "2010Q1-2016Q4 full sample-period, POST=2016Q3-Q4",
        "se": "double-clustered firm x calendar-quarter",
        "results": results,
        "campello_note": "Campello Table 8 has NO UncResCEO benchmark "
                         "(CASH/NWC/PROFITS only) — novel extension, not a "
                         "replication; no verdict (gated on Sina)",
        "treatment_counts": {
            "market": {"rebuild": mkt_counts,
                       "src": "step3_treatment asymmetric tercile (nonneg beta^UK)"},
            "textual": {"rebuild": txt_counts,
                        "src": "step3b3_textual_treatment_sec17 (Sec 1+7, >5/==0)"},
        },
        "verdict_gated_on_sina": True,
    }

    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\n-> {out_dir / 'summary.json'}")
    print(f"\n  MARKET  beta^UK-tercile  d={r_mkt['delta_hat']:+.4f}  "
          f"({r_mkt['se']:.4f})  N={r_mkt['nobs']:,}  "
          f"firms={r_mkt['n_firms']:,}")
    print(f"  TEXTUAL Sec 1+7          d={r_txt['delta_hat']:+.4f}  "
          f"({r_txt['se']:.4f})  N={r_txt['nobs']:,}  "
          f"firms={r_txt['n_firms']:,}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
