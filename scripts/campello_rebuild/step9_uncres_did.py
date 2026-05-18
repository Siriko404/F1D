"""STEP 9 — eq-(14) clone with CEO residual uncertainty (UncResCEO) as DV.

Sina 2026-05-17 final step: the CANONICAL full-sample-period eq-(14)
(identical to step7_fullpanel_hypothesis.py) with the DEPENDENT VARIABLE
swapped from CASH to UncResCEO (DWZ Eq.4 CEO Q&A call-level residual).
Novel extension — no Campello Table 8 benchmark exists for this DV
(Table 8 = CASH / NWC / PROFITS). NOT a replication; factual output only,
no verdict (gated on Sina).

Clone fidelity: sample (step1 ∩ step3 βᵁᴷ-tercile), full panel + POST
dummy (2016Q3-Q4), 5 firm controls lagged 1Q + cons_fwd, FIRM FE +
INDUSTRY(FIC100)×QUARTER FE, double-clustered SE — ALL identical to
step7. ONLY the DV differs.

DV build (Sina-locked decisions 2026-05-17):
  - UncResCEO source: outputs/econometric/ceo_clarity_extended/{latest}/
    ceo_clarity_residual.parquet (file_name, UncResCEO), via
    ClarityResidualEngine (reuse, not reinvented).
  - file_name→gvkey bridge: existing validated H1 panel
    outputs/variables/h1_cash_holdings/{latest}/h1_cash_holdings_panel.parquet
    (file_name, gvkey, start_date). Universe = H1-cash calls ∩ Campello
    βᵁᴷ-tercile firms (accepted constraint).
  - call→quarter: calendar quarter of start_date (cal_yr_qtr =
    year*10 + quarter — identical to step7 _cash_dv).
  - aggregate: mean UncResCEO per (gvkey, cal_yr_qtr).
  - NO winsorization (residual pre-cleaned; CEOClarityResidualBuilder
    sets _skip_winsorization=True).

Output: outputs/campello_rebuild/step9_uncres_did/<ts>/
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
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


def _uncres_dv() -> pd.DataFrame:
    """UncResCEO per (gvkey, cal_yr_qtr); NO winsorization (pre-cleaned).

    Reuses the existing ClarityResidualEngine + the validated H1 panel as
    the file_name->gvkey bridge (Sina-locked 2026-05-17).
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


def main() -> None:
    print("=== STEP 9 — eq-(14) clone, DV = UncResCEO (CEO residual unc.) ===\n")
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

    panel = s1.merge(tc[["gvkey", "HIGH_UK_EXPOSURE"]], on="gvkey",
                     how="inner")
    panel["POST"] = panel["cal_yr_qtr"].isin(POST_Q).astype(int)
    print(f"FULL-panel firm-quarters: {len(panel):,} / "
          f"{panel['gvkey'].nunique():,} firms; "
          f"qtr range {int(panel.cal_yr_qtr.min())}–"
          f"{int(panel.cal_yr_qtr.max())}")

    dv = _uncres_dv()
    print(f"UncResCEO DV (mean per gvkey×cal_yr_qtr, NOT winsorized): "
          f"{len(dv):,} firm-qtrs")
    df = panel.merge(dv, on=["gvkey", "cal_yr_qtr"], how="inner")
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

    # NO winsorization of UNCRES (pre-cleaned residual; Sina 2026-05-17).
    df["POST_x_HIGH"] = (df["POST"] * df["HIGH_UK_EXPOSURE"]).astype(float)
    df["indqtr_code"] = ((df["fic100_industry_id"].astype("int64").astype(str)
                          + "_" + df["cal_yr_qtr"].astype(str))
                         .astype("category").cat.codes)

    cols = ["POST_x_HIGH"] + firm_cols + ["cons_fwd"]
    sub = df.dropna(subset=["UNCRES", "indqtr_code"] + cols).copy()
    pdat = sub.set_index(["gvkey", "cal_yr_qtr"]).sort_index()
    print(f"\nestimation sample (full panel ∩ UncResCEO ∩ controls): "
          f"{len(sub):,} fq / {sub['gvkey'].nunique():,} firms")

    res = PanelOLS(pdat["UNCRES"], pdat[cols], entity_effects=True,
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
    print("\n--- eq-(14) δ̂ [DV=UncResCEO, FULL PANEL, POST=2016Q3-Q4] ---")
    print(f"  δ̂(POST·HIGH) = {b:+.5f}  SE {se:.5f}  t {t:+.3f}  p {p:.4f}"
          f"  N {int(res.nobs):,}  firms {sub['gvkey'].nunique():,}  "
          f"R²w {float(res.rsquared_within):.4f}")
    print("  [No Campello benchmark for UncResCEO — novel extension. "
          "NOT a replication verdict — gated on Sina.]")

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    odir = ROOT / "outputs" / "campello_rebuild" / "step9_uncres_did" / ts
    odir.mkdir(parents=True, exist_ok=True)
    sub[["gvkey", "cal_yr_qtr", "POST", "HIGH_UK_EXPOSURE", "UNCRES"] + cols
        ].to_parquet(odir / "uncres_panel.parquet", index=False)
    (odir / "summary.json").write_text(json.dumps({
        "dv": "UncResCEO (DWZ Eq.4 CEO Q&A call-level residual); mean per "
              "(gvkey,cal_yr_qtr); NOT winsorized (pre-cleaned residual)",
        "dv_bridge": "file_name->gvkey via h1_cash_holdings_panel.parquet; "
                     "call->quarter = calendar qtr of start_date "
                     "(Sina-locked 2026-05-17)",
        "model": "eq-14 PanelOLS (CLONE of step7); FULL sample-period panel "
                 "+ POST(2016Q3-Q4) dummy; FIRM FE + INDUSTRY(FIC100)xQUARTER "
                 "FE; SE double-clustered firm x calendar-qtr; macro absorbed "
                 "by IND x QTR FE; consensus = forward",
        "results": [{
            "tag": "FULL_PANEL_UNCRES",
            "delta_hat": b, "se": se, "t": t, "pvalue": p,
            "nobs": int(res.nobs), "n_firms": int(sub["gvkey"].nunique()),
            "rsquared_within": float(res.rsquared_within),
            "controls": cols, "coefficients": coefs,
            "consensus_variant": "cons_fwd",
        }],
        "campello_reference": None,
        "campello_note": "Campello Table 8 has NO UncResCEO benchmark "
                         "(CASH/NWC/PROFITS only) - novel extension, not a "
                         "replication; no verdict (gated on Sina)",
        "step1_dir": s1_dir.name, "step3_dir": s3_dir.name,
        "verdict_gated_on_sina": True,
    }, indent=2), encoding="utf-8")
    print(f"\nwritten → {odir}")


if __name__ == "__main__":
    main()
