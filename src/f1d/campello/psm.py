"""Phase 4a: PSM matching — replicate Campello Table C.2 footnote.

> "Each treated firm is matched to 3 control firms (with replacement) which
>  are its nearest neighbors in terms of treatment propensity. The propensity
>  score is a function of lagged STOCK_RETURNS, 1-quarter-ahead
>  CONSENSUS_EARNINGS_FORECAST, TOBIN_Q, CASH_FLOW, SALES_GROWTH, and SIZE."

Treated: β^UK > top-tercile cutoff (within β^UK >= 0)
Control: β^UK < bottom-tercile cutoff (within β^UK >= 0)
Negative β^UK firms: excluded from treated/control assignment (paper § IV.C.1)
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


PRE_BREXIT_END = 20154  # 2015Q4 — last pre-Brexit quarter


def _latest_run(out_root: Path, fname: str) -> Path:
    runs = sorted([d for d in out_root.iterdir()
                   if d.is_dir() and (d / fname).exists()], reverse=True)
    if not runs:
        raise FileNotFoundError(f"No {fname} found in {out_root}")
    return runs[0] / fname


def build_psm(root: Path) -> dict:
    out_root = root / "outputs" / "campello_v2"
    vars_path = _latest_run(out_root, "variables_panel.parquet")
    beta_path = _latest_run(out_root, "beta_uk.parquet")
    sret_path = _latest_run(out_root, "stock_returns.parquet")
    ceps_path = _latest_run(out_root, "consensus_eps.parquet")

    logger.info("Loading variables: %s", vars_path)
    panel = pd.read_parquet(vars_path)
    beta = pd.read_parquet(beta_path)[["gvkey", "beta_uk"]]
    sret = pd.read_parquet(sret_path)
    ceps = pd.read_parquet(ceps_path)

    # Merge STOCK_RETURNS + CONSENSUS_EPS into firm-quarter panel
    panel = panel.merge(sret, on=["gvkey", "cal_yr_qtr"], how="left")
    panel = panel.merge(ceps, on=["gvkey", "cal_yr_qtr"], how="left")
    panel = panel.merge(beta, on="gvkey", how="left")
    logger.info("Panel after merge: %s obs, %s firms", f"{len(panel):,}",
                 f"{panel['gvkey'].nunique():,}")

    # ---- treated/control assignment (per paper §IV.C.1 + STEP 29) ----
    # Use nonneg-β^UK only; terciles within nonneg range
    nonneg = beta[beta["beta_uk"] >= 0].copy()
    t1 = nonneg["beta_uk"].quantile(1/3)
    t2 = nonneg["beta_uk"].quantile(2/3)
    logger.info("Nonneg β^UK terciles: t1=%.3f, t2=%.3f", t1, t2)

    panel["treated"] = (panel["beta_uk"] > t2).astype(float)
    panel["control_pool"] = ((panel["beta_uk"] >= 0) & (panel["beta_uk"] < t1)).astype(float)
    # Drop firms not in treated OR control (middle tercile + negative β)
    panel = panel[(panel["treated"] == 1) | (panel["control_pool"] == 1)].copy()

    n_treated = panel[panel["treated"] == 1]["gvkey"].nunique()
    n_control = panel[panel["control_pool"] == 1]["gvkey"].nunique()
    logger.info("Treated firms: %s | Control pool firms: %s", n_treated, n_control)
    logger.info("Paper benchmark: treated=449, control=360")

    # ---- aggregate pre-Brexit covariates per firm (static PSM) ----
    pre = panel[panel["cal_yr_qtr"] <= PRE_BREXIT_END].copy()
    # Lag STOCK_RETURNS by 1 quarter per paper (§IV.C.3): "lagged stock returns"
    pre = pre.sort_values(["gvkey", "cal_yr_qtr"])
    pre["STOCK_RETURNS_lag1"] = pre.groupby("gvkey")["STOCK_RETURNS"].shift(1)

    # PAPER VERBATIM (supplementary Table C.3): "lagged STOCK_RETURNS,
    # 1-quarter-ahead CONSENSUS_EARNINGS_FORECASTS, TOBIN_Q, CASH_FLOW,
    # SALES_GROWTH, SIZE"
    covariates = ["STOCK_RETURNS_lag1", "CONSENSUS_EPS", "TOBIN_Q", "CASH_FLOW",
                  "SALES_GROWTH", "SIZE"]
    firm_avg = pre.groupby("gvkey").agg({
        "treated": "max",  # firm is treated if any obs is
        "sic": "first",
        **{c: "mean" for c in covariates},
    }).reset_index()
    firm_avg = firm_avg.dropna(subset=covariates)
    firm_avg["sic2"] = pd.to_numeric(firm_avg["sic"], errors="coerce").fillna(-1).astype(int) // 100
    logger.info("Firms with all covariates: %s", len(firm_avg))

    # ---- fit propensity model ----
    X = firm_avg[covariates].values
    y = firm_avg["treated"].values.astype(int)
    scaler = StandardScaler()
    X_z = scaler.fit_transform(X)
    logreg = LogisticRegression(max_iter=1000)
    logreg.fit(X_z, y)
    firm_avg["pscore"] = logreg.predict_proba(X_z)[:, 1]
    logger.info("Logistic regression fit. Treated rate: %.3f",
                 firm_avg["treated"].mean())

    # 3-NN with replacement (paper verbatim Table C.2/C.3 — NO SIC2 stratification)
    treated_idx = firm_avg.index[firm_avg["treated"] == 1].tolist()
    control_idx = firm_avg.index[firm_avg["treated"] == 0].tolist()
    if not treated_idx or not control_idx:
        raise RuntimeError("Empty treated or control group")
    nbrs = NearestNeighbors(n_neighbors=3)
    nbrs.fit(firm_avg.loc[control_idx, ["pscore"]].values)
    dist, idx_in_ctrl = nbrs.kneighbors(firm_avg.loc[treated_idx, ["pscore"]].values)
    matched_control_firm_idx = np.array([[control_idx[i] for i in row] for row in idx_in_ctrl])

    # Build matched-sample list: each treated firm + 3 matched control firms (with replacement)
    matched_treated_gvkeys = firm_avg.loc[treated_idx, "gvkey"].values
    matched_control_gvkeys = firm_avg.loc[matched_control_firm_idx.flatten(), "gvkey"].values

    logger.info("Matched: %s treated → %s control matches (3-NN replacement)",
                 len(matched_treated_gvkeys), len(matched_control_gvkeys))

    # Save match table
    match_table = pd.DataFrame({
        "treated_gvkey": np.repeat(matched_treated_gvkeys, 3),
        "control_gvkey": matched_control_gvkeys,
        "match_rank": np.tile([1, 2, 3], len(treated_idx)),
        "distance": dist.flatten(),
    })
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = root / "outputs" / "campello_v2" / ts
    out_dir.mkdir(parents=True, exist_ok=True)
    match_table.to_parquet(out_dir / "psm_matches.parquet", index=False)
    logger.info("Saved match table to %s", out_dir / "psm_matches.parquet")

    return {
        "out_dir": out_dir,
        "panel": panel,
        "firm_avg": firm_avg,
        "match_table": match_table,
        "treated_gvkeys": set(matched_treated_gvkeys),
        "control_gvkeys": set(matched_control_gvkeys),
        "covariates": covariates,
    }


def compare_table_c2_panel_a(psm_result: dict) -> None:
    """Compute matched-sample means and compare against Table C.2 Panel A."""
    panel = psm_result["panel"]
    treated_gv = psm_result["treated_gvkeys"]
    control_gv = psm_result["control_gvkeys"]

    # Restrict to pre-Brexit period for summary stats (matching paper convention)
    pre = panel[panel["cal_yr_qtr"] <= PRE_BREXIT_END].copy()
    pre["STOCK_RETURNS_lag1"] = pre.sort_values(
        ["gvkey", "cal_yr_qtr"]).groupby("gvkey")["STOCK_RETURNS"].shift(1)

    treated_obs = pre[pre["gvkey"].isin(treated_gv)]
    control_obs = pre[pre["gvkey"].isin(control_gv)]

    # Anchor (Table C.2 Panel A — Market-Based)
    anchor = {
        "INVESTMENT":                (0.020, 0.012),
        "R&D":                       (0.030, 0.016),
        "DIVESTITURES (×100)":       (0.129, 0.088),
        "CASH":                      (0.175, 0.164),
        "NON_CASH_WORKING_CAPITAL":  (0.058, 0.086),
        "TOBIN_Q":                   (1.948, 1.928),
        "CASH_FLOW":                 (0.016, 0.032),
        "SIZE (Log Assets)":         (6.677, 7.205),
        "SALES_GROWTH":              (0.195, 0.105),
        "CONSENSUS_EPS":             (0.023, 0.025),
        "STOCK_RETURNS_lag1":        (0.021, 0.038),
    }
    var_map = {
        "INVESTMENT": "INVESTMENT",
        "R&D": "RD",
        "DIVESTITURES (×100)": "DIVESTITURES",
        "CASH": "CASH",
        "NON_CASH_WORKING_CAPITAL": "NWC",
        "TOBIN_Q": "TOBIN_Q",
        "CASH_FLOW": "CASH_FLOW",
        "SIZE (Log Assets)": "SIZE",
        "SALES_GROWTH": "SALES_GROWTH",
        "CONSENSUS_EPS": "CONSENSUS_EPS",
        "STOCK_RETURNS_lag1": "STOCK_RETURNS_lag1",
    }

    print("\n=== Table C.2 Panel A (Market-Based) — Matched Sample Comparison ===")
    print(f"{'Variable':<28} {'TREATED (mine/paper)':<28} {'CONTROL (mine/paper)':<28}")
    print("-" * 90)
    for label, (paper_t, paper_c) in anchor.items():
        col = var_map[label]
        if col not in treated_obs.columns:
            print(f"{label:<28} (column not in panel)")
            continue
        t_mean = treated_obs[col].mean()
        c_mean = control_obs[col].mean()
        # display multiplier for DIVESTITURES
        mult = 100 if "×100" in label else 1
        t_mean *= mult
        c_mean *= mult

        def fmt(mine, paper):
            diff = abs(mine - paper)
            if abs(paper) < 0.5:
                mark = "✓" if diff < 0.05 else "✗"
            else:
                pct = diff / abs(paper) * 100
                mark = "✓" if pct < 15 else "✗"
            return f"{mine:.3f}/{paper:.3f} {mark}"

        print(f"{label:<28} {fmt(t_mean, paper_t):<28} {fmt(c_mean, paper_c):<28}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    rp = Path(__file__).resolve().parent.parent.parent.parent
    res = build_psm(rp)
    compare_table_c2_panel_a(res)
