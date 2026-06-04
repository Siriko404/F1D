"""Phase 4b: CASH DiD on matched sample — eq (14) of method lockin.

Equation (14) verbatim from lockin STEP 40:
  Y_i,t = α + δ(POST_t × HIGH_UK_EXPOSURE_i)
        + θ CONTROLS_i,t-1
        + Σ FIRM_i + Σ INDUSTRY_j × QUARTER_t
        + ε_i,t

For CASH (Table 8 regression):
  - Outcome: CASH (Table 1 def)
  - Treatment window per STEP 39:
        Pre  = 2015Q3, 2015Q4
        Post = 2016Q3, 2016Q4
  - POST = 1 if cal_yr_qtr ∈ {20163, 20164}
  - HIGH_UK_EXPOSURE = 1 if treated (β^UK > t2), 0 if control (β^UK < t1, β>=0)
  - Controls (lagged): STOCK_RETURNS, TOBIN_Q, CASH_FLOW, SIZE, SALES_GROWTH, CONSENSUS_EPS
  - FE: firm + cal_yr_qtr (we approximate industry×quarter with just quarter FE)
  - SE: double-clustered by firm and cal_yr_qtr (STEP 45)
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

PRE_Q = [20153, 20154]
POST_Q = [20163, 20164]


def _latest_run(out_root: Path, fname: str) -> Path:
    runs = sorted([d for d in out_root.iterdir()
                   if d.is_dir() and (d / fname).exists()], reverse=True)
    return runs[0] / fname


def run_did(root: Path, sample: str = "matched") -> None:
    """Run CASH DiD on full sample or matched sample.

    Args:
        sample: 'matched' (PSM matched) or 'full' (treated + control pool).
    """
    out_root = root / "outputs" / "campello_v2"
    vars_panel = pd.read_parquet(_latest_run(out_root, "variables_panel.parquet"))
    beta = pd.read_parquet(_latest_run(out_root, "beta_uk.parquet"))[["gvkey", "beta_uk"]]
    sret = pd.read_parquet(_latest_run(out_root, "stock_returns.parquet"))
    ceps = pd.read_parquet(_latest_run(out_root, "consensus_eps.parquet"))
    matches = pd.read_parquet(_latest_run(out_root, "psm_matches.parquet"))

    # Merge
    panel = vars_panel.merge(sret, on=["gvkey", "cal_yr_qtr"], how="left")
    panel = panel.merge(ceps, on=["gvkey", "cal_yr_qtr"], how="left")
    panel = panel.merge(beta, on="gvkey", how="left")

    # ---- compute Table 8 CASH = cheq / (atq_lag1 − cheq_lag1) ----
    # Paper Section V.C / Table 8 uses this denom (variable lockin VAR_05 caveat)
    if "cheq" not in panel.columns:
        comp = pd.read_parquet(
            root / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet",
            columns=["gvkey", "datadate", "atq", "cheq"]
        )
        comp["gvkey"] = comp["gvkey"].astype(str).str.zfill(6)
        comp["datadate"] = pd.to_datetime(comp["datadate"])
        comp["atq"] = pd.to_numeric(comp["atq"], errors="coerce")
        comp["cheq"] = pd.to_numeric(comp["cheq"], errors="coerce")
        comp = comp.drop_duplicates(subset=["gvkey", "datadate"], keep="last")
        panel = panel.merge(comp[["gvkey", "datadate", "cheq"]],
                              on=["gvkey", "datadate"], how="left")

    panel = panel.sort_values(["gvkey", "cal_yr_qtr"])
    panel["atq_lag1_qf"] = panel.groupby("gvkey")["atq"].shift(1)
    panel["cheq_lag1_qf"] = panel.groupby("gvkey")["cheq"].shift(1)
    denom_t8 = panel["atq_lag1_qf"] - panel["cheq_lag1_qf"]
    panel["CASH_T8"] = np.where(
        denom_t8.notna() & (denom_t8 > 0),
        panel["cheq"] / denom_t8,
        np.nan,
    )
    panel["CASH_T8"] = panel["CASH_T8"].replace([np.inf, -np.inf], np.nan)
    # winsorize CASH_T8 at 1%/99% per cal_yr_qtr
    new_cash = pd.Series(np.nan, index=panel.index)
    for _q, idx in panel.groupby("cal_yr_qtr").groups.items():
        v = panel.loc[idx, "CASH_T8"]
        if v.notna().sum() < 10:
            new_cash.loc[idx] = v
            continue
        lo, hi = v.quantile(0.01), v.quantile(0.99)
        new_cash.loc[idx] = v.clip(lo, hi)
    panel["CASH_T8"] = new_cash

    # Recompute terciles
    nonneg = beta[beta["beta_uk"] >= 0]
    t1 = nonneg["beta_uk"].quantile(1/3)
    t2 = nonneg["beta_uk"].quantile(2/3)

    panel["HIGH_UK"] = (panel["beta_uk"] > t2).astype(float)
    panel["LOW_UK"] = ((panel["beta_uk"] >= 0) & (panel["beta_uk"] < t1)).astype(float)
    panel = panel[(panel["HIGH_UK"] == 1) | (panel["LOW_UK"] == 1)].copy()

    # Restrict to DiD window
    panel = panel[panel["cal_yr_qtr"].isin(PRE_Q + POST_Q)].copy()
    panel["POST"] = panel["cal_yr_qtr"].isin(POST_Q).astype(float)
    panel["TREAT_POST"] = panel["HIGH_UK"] * panel["POST"]

    # Restrict to matched sample
    if sample == "matched":
        matched_gvkeys = set(matches["treated_gvkey"].unique()) | set(
            matches["control_gvkey"].unique())
        panel = panel[panel["gvkey"].isin(matched_gvkeys)].copy()
        logger.info("Matched sample: %s obs, %s firms", f"{len(panel):,}",
                     panel["gvkey"].nunique())

    # Lagged controls (1-quarter lag per paper)
    panel = panel.sort_values(["gvkey", "cal_yr_qtr"])
    ctrl_cols = ["STOCK_RETURNS", "TOBIN_Q", "CASH_FLOW", "SIZE",
                  "SALES_GROWTH", "CONSENSUS_EPS"]
    for c in ctrl_cols:
        panel[f"{c}_lag1"] = panel.groupby("gvkey")[c].shift(1)

    # For lag1 to work in 2015Q3/Q4 + 2016Q3/Q4, we need prior-quarter data.
    # If we only kept these quarters, lag1 will all be NaN. Re-merge from FULL panel.
    full_panel = vars_panel.merge(sret, on=["gvkey", "cal_yr_qtr"], how="left")
    full_panel = full_panel.merge(ceps, on=["gvkey", "cal_yr_qtr"], how="left")
    full_panel = full_panel.sort_values(["gvkey", "cal_yr_qtr"])
    for c in ctrl_cols:
        full_panel[f"{c}_lag1"] = full_panel.groupby("gvkey")[c].shift(1)
    lag_data = full_panel[["gvkey", "cal_yr_qtr"] + [f"{c}_lag1" for c in ctrl_cols]]
    panel = panel.drop(columns=[f"{c}_lag1" for c in ctrl_cols])
    panel = panel.merge(lag_data, on=["gvkey", "cal_yr_qtr"], how="left")

    # Drop obs missing CASH or any lagged control
    required = ["CASH_T8"] + [f"{c}_lag1" for c in ctrl_cols]
    panel = panel.dropna(subset=required)
    logger.info("Post-filter for non-missing CASH+lagged controls: %s obs, %s firms",
                 f"{len(panel):,}", panel["gvkey"].nunique())

    # Diagnostics
    pre_t = panel[(panel["HIGH_UK"] == 1) & (panel["POST"] == 0)]
    post_t = panel[(panel["HIGH_UK"] == 1) & (panel["POST"] == 1)]
    pre_c = panel[(panel["HIGH_UK"] == 0) & (panel["POST"] == 0)]
    post_c = panel[(panel["HIGH_UK"] == 0) & (panel["POST"] == 1)]
    print(f"\n--- CASH means by group (matched sample if sample='matched') ---")
    print(f"  Treated PRE  (2015Q3-Q4):  N={len(pre_t):,}  mean CASH_T8={pre_t['CASH_T8'].mean():.4f}")
    print(f"  Treated POST (2016Q3-Q4):  N={len(post_t):,}  mean CASH_T8={post_t['CASH_T8'].mean():.4f}")
    print(f"  Control PRE  (2015Q3-Q4):  N={len(pre_c):,}  mean CASH_T8={pre_c['CASH_T8'].mean():.4f}")
    print(f"  Control POST (2016Q3-Q4):  N={len(post_c):,}  mean CASH_T8={post_c['CASH_T8'].mean():.4f}")
    raw_dd = (post_t["CASH_T8"].mean() - pre_t["CASH_T8"].mean()) \
             - (post_c["CASH_T8"].mean() - pre_c["CASH_T8"].mean())
    print(f"  Raw DiD (means difference): {raw_dd:+.4f}")

    # Regression via PanelOLS
    try:
        from linearmodels import PanelOLS
    except ImportError:
        logger.error("linearmodels not installed. Try: pip install linearmodels")
        return

    panel["firm_id"] = panel["gvkey"].astype("category").cat.codes
    panel["time_id"] = panel["cal_yr_qtr"]
    # SIC 2-digit × quarter FE as FIC100×quarter proxy (Hoberg-Phillips not loaded)
    panel["sic2"] = (panel["sic"].fillna(-1).astype(int) // 100)
    panel["ind_qtr"] = panel["sic2"].astype(str) + "_" + panel["cal_yr_qtr"].astype(str)
    panel_indexed = panel.set_index(["firm_id", "time_id"])

    y = panel_indexed["CASH_T8"]
    X_cols = ["TREAT_POST"] + [f"{c}_lag1" for c in ctrl_cols]
    # Add SIC2×quarter dummies
    ind_qtr_dummies = pd.get_dummies(panel_indexed["ind_qtr"], prefix="iq", drop_first=True).astype(float)
    X = pd.concat([panel_indexed[X_cols], ind_qtr_dummies], axis=1)

    # Firm FE (entity) + industry × quarter dummies in X
    model = PanelOLS(y, X, entity_effects=True, drop_absorbed=True)
    res = model.fit(cov_type="clustered",
                    cluster_entity=True, cluster_time=True)

    print(f"\n--- CASH DiD Eq (14) — Firm FE + SIC2×Quarter FE, clustered by firm+time ---")
    # Only show non-dummy params
    keep = [c for c in res.params.index if not c.startswith("iq_")]
    print(res.params[keep].to_string())
    print()
    print(res.tstats[keep].to_string())
    print()
    delta = res.params["TREAT_POST"]
    se = res.std_errors["TREAT_POST"]
    t_stat = res.tstats["TREAT_POST"]
    p_val = res.pvalues["TREAT_POST"]
    print(f"  δ (TREAT_POST) = {delta:+.4f}  SE={se:.4f}  t={t_stat:.2f}  p={p_val:.3f}")
    print(f"  N obs={int(res.nobs):,}  R²(within)={res.rsquared_within:.4f}")
    print(f"\nPaper benchmark (Table 8 CASH, Market-Based, eq 14):")
    print(f"  δ ≈ +0.231 *** (significant positive CASH response to Brexit treatment)")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    rp = Path(__file__).resolve().parent.parent.parent.parent
    run_did(rp, sample="matched")
    print("\n" + "=" * 80)
    print("Now running FULL sample (treated + control pool, no PSM):")
    print("=" * 80)
    run_did(rp, sample="full")
