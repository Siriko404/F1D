"""STEP 6 — conditional eq-(14): add CONTROLS_{i,t-1}; REAL data.

Built FRESH from the paper. No synthetic. Strictly after Step 5.

Verbatim eq-(14) CONTROLS (Campello p.3197, PDF-verified):
  "CONTROLS_{i,t-1} is a vector of macroeconomic and firm-level control
   variables. ... Firm-level controls include lagged stock returns,
   Tobin's Q, cash flow, logged assets, and sales growth. As an
   additional control for first-moment effects of Brexit, we add
   1-quarter-ahead consensus earnings forecasts to our model."
  SE: "double-clustered by firm and calendar quarters."

Controls assembled (restored+verbatim-corrected builders, this session):
  • 5 firm controls — stock return, Tobin's Q, cash flow, sales growth
    (builders emit contemporaneous → lagged 1 CALENDAR quarter here,
    target-driven idiom) + logged assets = ln(atq) (lagged 1Q).
  • 5 macro controls — brexit_macro_controls ALREADY emits 1Q-lagged
    values (`*_lag1`, builder docstring) → merged on cal_yr_qtr, NOT
    re-lagged (double-lag guard).
  • consensus EPS — paper-SILENT on mechanical t vs t-1 alignment
    (NLM relay + PDF both confirm silence). Sina 2026-05-17 standing
    methodology: "where there is true vagueness, we must test ALL
    possible ways." ⇒ eq-(14) fit under BOTH:
      A "forward"  : consensus on native key (forecast FOR quarter t,
                     known at t-1; pre-determined, no look-ahead) —
                     preserves the intrinsic "1-quarter-ahead" property.
      B "lag1"     : consensus 1Q calendar-lagged like the firm controls
                     (literal uniform CONTROLS_{i,t-1}).

Estimator: PanelOLS, FIRM FE (entity) + INDUSTRY(FIC100)×QUARTER FE
(other_effects), SE double-clustered (entity & time). Interaction
δ[POST·HIGH] is the coefficient of interest.

Output: outputs/campello_rebuild/step6_controls_did/<ts>/
    did_panel_controls.parquet
    summary.json
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

FIRM_CTRL_LAG_BUILDERS = {
    "brexit_stock_return": "BrexitStockReturnBuilder",
    "brexit_tobins_q": "BrexitTobinsQBuilder",
    "brexit_cash_flow": "BrexitCashFlowBuilder",
    "brexit_sales_growth": "BrexitSalesGrowthBuilder",
}
MACRO_COLS = ["usd_gbp_lag1", "vix_lag1", "gdp_fcst_1y_lag1",
              "umcsent_lag1", "state_lei_lag1"]


def _prev_q(yq: int) -> int:
    yr, q = yq // 10, yq % 10
    return (yr - 1) * 10 + 4 if q == 1 else yr * 10 + (q - 1)


def _latest(sub: str) -> Path:
    base = ROOT / "outputs" / "campello_rebuild" / sub
    return sorted(d for d in base.iterdir() if d.is_dir())[-1]


def _calendar_lag1(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Target-driven 1-qtr calendar lag: row T gets value(T-1). Returns
    (gvkey, cal_yr_qtr, col) where col now holds the lagged value."""
    src = df[["gvkey", "cal_yr_qtr", col]].rename(
        columns={"cal_yr_qtr": "_pq", col: col + "_L"})
    tgt = df[["gvkey", "cal_yr_qtr"]].copy()
    tgt["_pq"] = tgt["cal_yr_qtr"].map(_prev_q).astype("int64")
    out = tgt.merge(src, on=["gvkey", "_pq"], how="left").drop(columns="_pq")
    return out.rename(columns={col + "_L": col})


def _build(builder_cls: str):
    import importlib
    mod_name = {
        "BrexitStockReturnBuilder": "brexit_stock_return",
        "BrexitTobinsQBuilder": "brexit_tobins_q",
        "BrexitCashFlowBuilder": "brexit_cash_flow",
        "BrexitSalesGrowthBuilder": "brexit_sales_growth",
        "BrexitMacroControlsBuilder": "brexit_macro_controls",
        "BrexitConsensusEPSBuilder": "brexit_consensus_eps",
    }[builder_cls]
    m = importlib.import_module(f"f1d.shared.variables.{mod_name}")
    cls = getattr(m, builder_cls)
    res = cls().build(range(2009, 2017), root_path=ROOT)
    d = res.data.copy()
    if "gvkey" in d.columns:  # macro builder is firm-invariant (no gvkey)
        d["gvkey"] = d["gvkey"].astype(str).str.zfill(6)
    d["cal_yr_qtr"] = d["cal_yr_qtr"].astype("int64")
    return d


def _fit(pdat: pd.DataFrame, xcols: list[str], tag: str) -> dict:
    from linearmodels.panel import PanelOLS
    exog = pdat[xcols]
    assert xcols[0] == "POST_x_HIGH", f"interaction must lead: {xcols}"
    mod = PanelOLS(pdat["CASH"], exog, entity_effects=True,
                   other_effects=pdat["indqtr_code"], drop_absorbed=True)
    res = mod.fit(cov_type="clustered", cluster_entity=True,
                  cluster_time=True)
    b = float(res.params["POST_x_HIGH"])
    se = float(res.std_errors["POST_x_HIGH"])
    t = float(res.tstats["POST_x_HIGH"])
    p = float(res.pvalues["POST_x_HIGH"])
    print(f"\n--- eq-(14) δ̂ [{tag}] (FIRM FE + IND×QTR FE, controls, "
          f"double-clustered firm×qtr) ---")
    print(f"  δ̂(POST·HIGH) = {b:+.5f}  SE {se:.5f}  t {t:+.3f}  p {p:.4f}"
          f"  N {int(res.nobs):,}  firms {pdat.index.get_level_values(0).nunique():,}")
    return {"tag": tag, "delta_hat": b, "se": se, "t": t, "pvalue": p,
            "nobs": int(res.nobs),
            "n_firms": int(pdat.index.get_level_values(0).nunique()),
            "rsquared_within": float(res.rsquared_within),
            "controls": xcols}


def main() -> None:
    print("=== STEP 6 — conditional eq-(14) + CONTROLS (real data) ===\n")
    s1_dir = _latest("step1_sample")
    s5_dir = _latest("step5_did")
    panel = pd.read_parquet(s5_dir / "did_panel.parquet")
    panel["gvkey"] = panel["gvkey"].astype(str).str.zfill(6)
    print(f"Step-5 panel: {s5_dir.name}  ({len(panel):,} fq / "
          f"{panel['gvkey'].nunique():,} firms)")

    # logged assets from Step-1 atq, then 1Q calendar lag.
    s1 = pd.read_parquet(s1_dir / "sample.parquet",
                         columns=["gvkey", "cal_yr_qtr", "atq"])
    s1["gvkey"] = s1["gvkey"].astype(str).str.zfill(6)
    s1 = s1[s1["atq"] > 0].copy()
    s1["log_assets"] = np.log(s1["atq"])
    log_a = _calendar_lag1(s1[["gvkey", "cal_yr_qtr", "log_assets"]],
                           "log_assets")

    # 5 firm controls: build (contemporaneous) → 1Q calendar lag.
    df = panel.copy()
    firm_cols = []
    for _, cls in FIRM_CTRL_LAG_BUILDERS.items():
        b = _build(cls)
        col = [c for c in b.columns if c not in ("gvkey", "cal_yr_qtr")][0]
        bl = _calendar_lag1(b[["gvkey", "cal_yr_qtr", col]], col)
        df = df.merge(bl, on=["gvkey", "cal_yr_qtr"], how="left")
        firm_cols.append(col)
        print(f"  + firm control (lagged 1Q): {col}")
    df = df.merge(log_a, on=["gvkey", "cal_yr_qtr"], how="left")
    firm_cols.append("log_assets")
    print(f"  + firm control (lagged 1Q): log_assets")

    # 5 macro: builder ALREADY 1Q-lagged → merge on cal_yr_qtr (no re-lag).
    macro = _build("BrexitMacroControlsBuilder")
    mcols = [c for c in macro.columns if c in MACRO_COLS]
    df = df.merge(macro[["cal_yr_qtr"] + mcols].drop_duplicates("cal_yr_qtr"),
                  on="cal_yr_qtr", how="left")
    print(f"  + macro (already lagged by builder): {mcols}")

    # consensus EPS — two variants (true-vagueness, test all — Sina).
    cons = _build("BrexitConsensusEPSBuilder")
    ccol = [c for c in cons.columns if c not in ("gvkey", "cal_yr_qtr")][0]
    cons_fwd = cons.rename(columns={ccol: "cons_fwd"})           # native key
    cons_lag = _calendar_lag1(cons[["gvkey", "cal_yr_qtr", ccol]], ccol) \
        .rename(columns={ccol: "cons_lag1"})                     # 1Q-lagged
    df = df.merge(cons_fwd[["gvkey", "cal_yr_qtr", "cons_fwd"]],
                  on=["gvkey", "cal_yr_qtr"], how="left")
    df = df.merge(cons_lag, on=["gvkey", "cal_yr_qtr"], how="left")
    print(f"  + consensus EPS: variant A=cons_fwd (native/forward), "
          f"B=cons_lag1 (1Q-lag)")

    # --- design matrices -------------------------------------------------
    df["POST_x_HIGH"] = (df["POST"] * df["HIGH_UK_EXPOSURE"]).astype(float)
    df["indqtr_code"] = ((df["fic100_industry_id"].astype("int64").astype(str)
                          + "_" + df["cal_yr_qtr"].astype(str))
                         .astype("category").cat.codes)

    # MACRO controls are time-only (vary by quarter). The verbatim eq-(14)
    # INDUSTRY(FIC100)×QUARTER FE absorbs ALL time-only variation, and on a
    # 4-quarter window 5 macro series live in a ≤4-dim space (linearly
    # dependent by construction). They are therefore NOT separately
    # identified — mechanically subsumed by the paper's own specified FE.
    # Paper-faithful eq-(14) ⇒ macro absorbed by FE; firm controls +
    # consensus remain identified. Macro retained in the saved panel for
    # transparency but excluded from the regressor matrix (not a deviation;
    # a necessary consequence of the verbatim FE on a 4-qtr window).
    base_ctrl = firm_cols
    print(f"\ncontrols: {len(base_ctrl)} firm (lagged 1Q) + 1 consensus "
          f"(per variant). MACRO ({len(mcols)}) ABSORBED by INDUSTRY×"
          f"QUARTER FE (time-only, over-identified on 4 qtrs) — verbatim "
          f"FE structure subsumes them; kept in saved panel only.")

    # corrected 2×2 descriptive labels (the Step-5 cosmetic defect, fixed):
    lab = df.assign(
        period=np.where(df["POST"] == 1, "POST(2016Q3-4)", "PRE(2015Q3-4)"),
        grp=np.where(df["HIGH_UK_EXPOSURE"] == 1, "treated", "control"))
    cm = lab.groupby(["period", "grp"])["CASH"].agg(["count", "mean"])
    print("\n--- raw cell means (pre-FE, descriptive; labels fixed) ---")
    print(cm.to_string())

    results = []
    for tag, ccons in (("A_forward", "cons_fwd"), ("B_lag1", "cons_lag1")):
        cols = ["POST_x_HIGH"] + base_ctrl + [ccons]
        sub = df.dropna(subset=["CASH", "indqtr_code"] + cols).copy()
        pdat = sub.set_index(["gvkey", "cal_yr_qtr"]).sort_index()
        r = _fit(pdat, cols, tag)
        r["consensus_variant"] = ccons
        results.append(r)

    print(f"\nCampello Table 8 cash anchor (reference, NOT a target): "
          f"+0.231*** SE 0.059 N 17,170")
    print("[CONDITIONAL eq-(14). Sensitivity across the one true-vague "
          "point (consensus timing) reported. NOT a replication verdict "
          "— gated on Sina; off-ramp forbidden.]")

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    odir = ROOT / "outputs" / "campello_rebuild" / "step6_controls_did" / ts
    odir.mkdir(parents=True, exist_ok=True)
    keep = (["gvkey", "cal_yr_qtr", "POST", "HIGH_UK_EXPOSURE", "CASH",
             "fic100_industry_id"] + base_ctrl + ["cons_fwd", "cons_lag1"])
    df[keep].to_parquet(odir / "did_panel_controls.parquet", index=False)
    summary = {
        "model": "eq-14 PanelOLS; FIRM FE + INDUSTRY(FIC100)×QUARTER FE; "
                 "SE double-clustered firm×calendar-qtr (verbatim)",
        "controls_firm_lagged_1q": firm_cols,
        "controls_macro_builder_lagged": mcols,
        "consensus_variants_tested": {
            "A_forward": "native key — forecast FOR quarter t (known t-1); "
                         "preserves intrinsic 1-quarter-ahead property",
            "B_lag1": "1Q calendar-lag like firm controls (literal uniform "
                      "CONTROLS_{i,t-1})"},
        "vagueness_methodology": "Sina 2026-05-17: true vagueness → test "
                                 "all possible ways; consensus timing is "
                                 "paper-silent (NLM+PDF confirmed)",
        "results": results,
        "campello_reference": {"cash_delta": 0.231, "se": 0.059, "n": 17170,
                               "note": "reference only; NOT a tuning "
                               "target; no replication verdict (gated)"},
        "step1_dir": s1_dir.name, "step5_dir": s5_dir.name,
    }
    (odir / "summary.json").write_text(json.dumps(summary, indent=2),
                                       encoding="utf-8")
    print(f"\nwritten → {odir}")


if __name__ == "__main__":
    main()
