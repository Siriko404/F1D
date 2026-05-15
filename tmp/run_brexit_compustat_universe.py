#!/usr/bin/env python3
"""Phase 3 test #1 — Compustat-universe parallel runner.

Goal: isolate deviation #1 (call-panel universe restriction) from main Brexit
runner. Replace load_h1_panel() with direct Compustat universe load. Exclude
SIC 4900-4999 (utility) + 6000-6999 (financial) per Campello §1G verbatim.
Cash-only (no speech DV; no call panel = no UncResCEO).

Compares cash β to Campello +0.231***. If matches → universe deviation
confirmed dominant. If still flips/null → eliminate universe; test next
deviation (Tobin's Q fix).

Everything else IDENTICAL to production runner (load_compustat_raw,
load_brexit_builders, _fit_one, winsorize_within, constants).
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

sys.path.insert(0, "src")
from f1d.econometric.run_h1_5_brexit_did import (  # type: ignore
    load_compustat_raw,
    load_brexit_builders,
    winsorize_within,
    _fit_one,
    KEY_IV_BETA_UK,
    KEY_IV_10K,
    MACRO_CONTROLS,
    FIRM_CONTROLS_NAMES,
    FIRM_CONTROLS_LAG1,
    EPS_CONTROL_LAG1,
    WINDOW_START_YQ,
    WINDOW_END_YQ,
    POST_START_YQ,
    MIN_MV_OR_BA_MILLIONS,
    WINSOR_PCT,
    FE_LADDER,
    CLUSTERING,
)


# ==============================================================================
# Compustat-universe panel construction
# ==============================================================================

def load_compustat_universe_panel(root: Path) -> pd.DataFrame:
    """Build Compustat-universe (gvkey, cal_yr_qtr) frame.

    Replaces production runner's load_h1_panel() — which restricts to the
    F1D call-panel firm-quarters. Here: all gvkeys in Compustat with
    valid SIC, Brexit window.
    """
    cpath = root / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
    print(f"  Loading Compustat universe with SIC: {cpath}")
    import pyarrow.parquet as pq
    from datetime import datetime as _dt

    yr_min = WINDOW_START_YQ // 10
    yr_max = WINDOW_END_YQ // 10 + 1

    table = pq.read_table(
        cpath,
        columns=["gvkey", "datadate", "sic"],
        filters=[("datadate", ">=", _dt(yr_min, 1, 1)),
                 ("datadate", "<",  _dt(yr_max, 1, 1))],
    )
    df = table.to_pandas()
    del table

    df["datadate"] = pd.to_datetime(df["datadate"])
    df["cal_yr_qtr"] = df["datadate"].dt.year * 10 + df["datadate"].dt.quarter
    df["gvkey"] = df["gvkey"].astype(int).astype(str).str.zfill(6)
    df = df[(df["cal_yr_qtr"] >= WINDOW_START_YQ) & (df["cal_yr_qtr"] <= WINDOW_END_YQ)]

    # Drop utility (SIC 4900-4999) + financial (SIC 6000-6999) per Campello §1G.
    df["sic_int"] = pd.to_numeric(df["sic"], errors="coerce")
    pre = len(df)
    df = df[~((df["sic_int"] >= 4900) & (df["sic_int"] <= 4999))]
    df = df[~((df["sic_int"] >= 6000) & (df["sic_int"] <= 6999))]
    print(f"  SIC drop util+fin: {len(df):,} (dropped {pre - len(df):,})")

    df = df.sort_values(["gvkey", "cal_yr_qtr"], kind="stable").drop_duplicates(
        subset=["gvkey", "cal_yr_qtr"], keep="last"
    ).reset_index(drop=True)
    print(f"  Compustat-universe Brexit window: {len(df):,} firm-quarters ({df['gvkey'].nunique():,} gvkeys)")
    return df[["gvkey", "cal_yr_qtr", "sic_int"]]


def assemble_panel_compustat(
    universe: pd.DataFrame,
    raw_comp: pd.DataFrame,
    builders: Dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Build (gvkey, cal_yr_qtr) panel from Compustat universe.

    Identical control + DV construction to production runner. Differences:
    - Universe is full Compustat (this function's input), not call-panel.
    - No UncResCEO_c (no call panel → no DWZ residual).
    - No FF12 filter (already SIC-filtered upstream).
    """
    print("\n  --- Panel assembly (Compustat universe) ---")
    cell = universe.merge(raw_comp, on=["gvkey", "cal_yr_qtr"], how="inner")
    print(f"  After Compustat merge: {len(cell):,} cells")

    # Cash DV with calendar-prev-Q lag (matches production fix).
    def _prev_yq(yq: int) -> int:
        yr, q = yq // 10, yq % 10
        if q == 1:
            return (yr - 1) * 10 + 4
        return yr * 10 + (q - 1)

    cell["prev_qtr_id"] = cell["cal_yr_qtr"].map(_prev_yq)
    lag_src = raw_comp.rename(columns={"atq": "atq_lag1", "cheq": "cheq_lag1"})[
        ["gvkey", "cal_yr_qtr", "atq_lag1", "cheq_lag1"]
    ].rename(columns={"cal_yr_qtr": "prev_qtr_id"})
    cell = cell.merge(lag_src, on=["gvkey", "prev_qtr_id"], how="left")
    cell["denom"] = cell["atq_lag1"] - cell["cheq_lag1"]
    cell = cell[cell["denom"] > 0]
    cell["cash_brexit_dv"] = cell["cheq"] / cell["denom"]
    cell = cell.drop(columns=["prev_qtr_id"])

    # $10M filter (AND-keep, matches production).
    pre = len(cell)
    cell = cell[(cell["mkvaltq"].fillna(0) >= MIN_MV_OR_BA_MILLIONS) & (cell["atq"] >= MIN_MV_OR_BA_MILLIONS)]
    print(f"  $10M MV/BA filter: {len(cell):,} (dropped {pre - len(cell):,})")

    # Treatments.
    bu = builders["beta_uk"][["gvkey", "HIGH_BETA_UK"]]
    tk = builders["treat_10k"][["gvkey", "HIGH_10K"]]
    cell = cell.merge(bu, on="gvkey", how="left")
    cell = cell.merge(tk, on="gvkey", how="left")
    print(f"  HIGH_BETA_UK non-null: {cell['HIGH_BETA_UK'].notna().sum():,}; "
          f"in {{0,1}}: {cell['HIGH_BETA_UK'].isin([0.0, 1.0]).sum():,}")
    print(f"  HIGH_10K     non-null: {cell['HIGH_10K'].notna().sum():,}; "
          f"in {{0,1}}: {cell['HIGH_10K'].isin([0.0, 1.0]).sum():,}")

    # POST + DiD interactions.
    cell["Post_brexit"] = (cell["cal_yr_qtr"] >= POST_START_YQ).astype(int)
    cell[KEY_IV_BETA_UK] = cell["HIGH_BETA_UK"].fillna(np.nan) * cell["Post_brexit"]
    cell[KEY_IV_10K] = cell["HIGH_10K"].fillna(np.nan) * cell["Post_brexit"]

    # Macros (already 1Q-lagged in builder).
    cell = cell.merge(builders["macro"], on="cal_yr_qtr", how="left")

    # Firm controls.
    for col, key in [("brexit_tobins_q", "tobins_q"),
                     ("brexit_sales_growth", "sales_growth"),
                     ("brexit_stock_return", "stock_return"),
                     ("brexit_cash_flow", "cash_flow")]:
        sub = builders[key][["gvkey", "cal_yr_qtr", col]]
        cell = cell.merge(sub, on=["gvkey", "cal_yr_qtr"], how="left")
    cell["ln_atq"] = np.log(cell["atq"].clip(lower=1.0))

    # 1Q lag firm controls via CALENDAR-prev-Q merge (NOT row-order shift) —
    # row-order shift(1) picks wrong reference for firms with quarter gaps.
    def _prev_yq(yq: int) -> int:
        yr, q = yq // 10, yq % 10
        if q == 1: return (yr - 1) * 10 + 4
        return yr * 10 + (q - 1)
    cell["prev_qtr_id"] = cell["cal_yr_qtr"].map(_prev_yq)
    for c in FIRM_CONTROLS_NAMES:
        lag_src = cell[["gvkey", "cal_yr_qtr", c]].rename(
            columns={"cal_yr_qtr": "prev_qtr_id", c: c + "_lag1"}
        )
        cell = cell.merge(lag_src, on=["gvkey", "prev_qtr_id"], how="left")

    # Consensus EPS lag (also calendar-prev-Q).
    eps = builders["eps"][["gvkey", "cal_yr_qtr", "consensus_eps_z"]]
    cell = cell.merge(eps, on=["gvkey", "cal_yr_qtr"], how="left")
    eps_lag_src = cell[["gvkey", "cal_yr_qtr", "consensus_eps_z"]].rename(
        columns={"cal_yr_qtr": "prev_qtr_id", "consensus_eps_z": EPS_CONTROL_LAG1}
    )
    cell = cell.merge(eps_lag_src, on=["gvkey", "prev_qtr_id"], how="left")
    cell = cell.drop(columns=["prev_qtr_id"])

    # FIC100 industry per (gvkey, year).
    cell["year"] = cell["cal_yr_qtr"] // 10
    fic = builders["fic100"][["gvkey", "year", "fic100_industry_id"]]
    cell = cell.merge(fic, on=["gvkey", "year"], how="left")
    fic_cov = cell["fic100_industry_id"].notna().mean()
    print(f"  FIC100 coverage: {fic_cov:.1%}")

    cell["fic100_qtr_id"] = (
        cell["fic100_industry_id"].astype("Int64").astype(str) + "_" + cell["cal_yr_qtr"].astype(str)
    )

    # Winsorize 1% within cal_yr_qtr on vars created here.
    for c in ["cash_brexit_dv", "ln_atq", EPS_CONTROL_LAG1]:
        if c in cell.columns:
            cell = winsorize_within(cell, c, "cal_yr_qtr")

    print(f"  Final panel: {len(cell):,} cells ({cell['gvkey'].nunique():,} gvkeys)")
    return cell


def run_cash_only_specs(panel: pd.DataFrame) -> List[Dict[str, Any]]:
    """2 cells = cash_brexit_dv × {DiD_BetaUK, DiD_10K} × campello_exact FE."""
    results: List[Dict[str, Any]] = []
    col = 0
    for treatment in [KEY_IV_BETA_UK, KEY_IV_10K]:
        for fe in FE_LADDER:
            col += 1
            exog_cols = MACRO_CONTROLS + FIRM_CONTROLS_LAG1 + [EPS_CONTROL_LAG1, "Post_brexit"]
            model, meta = _fit_one(panel, "cash_brexit_dv", treatment, exog_cols, fe)
            meta["col"] = col
            results.append({"model": model, "meta": meta})
            msg = (f"  Col ({col:>2d}) DV=cash_brexit_dv treat={treatment:12s} FE={fe:14s} "
                   f"n={meta.get('n_obs', 0):>6,} beta={meta.get('beta', np.nan):+.4f} "
                   f"se={meta.get('se', np.nan):.4f} p_one={meta.get('p_one', np.nan):.3f}")
            if meta.get("skipped"):
                msg += f"  SKIPPED({meta['skipped']})"
            print(msg)
    return results


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    t0 = datetime.now()
    root = Path.cwd()

    print("=" * 80)
    print("PHASE 3 TEST #1: Compustat-universe parallel Brexit DiD (cash only)")
    print("=" * 80)
    print(f"Window:    2010Q1-2016Q4  POST: >= {POST_START_YQ}")
    print(f"Universe:  Compustat (all gvkeys) — exclude SIC 4900-4999 + 6000-6999")
    print(f"Target:    Campello Table 8 cash β^UK = +0.231***  /  10-K = +0.357***")
    print()

    universe = load_compustat_universe_panel(root)
    gvkeys_keep = set(universe["gvkey"].unique())
    raw_comp = load_compustat_raw(root, gvkeys_keep, WINDOW_START_YQ - 1, WINDOW_END_YQ)
    builders = load_brexit_builders(root)

    panel = assemble_panel_compustat(universe, raw_comp, builders)

    print("\n  --- Running 2 cash-only specs (β^UK + 10-K under Campello-exact FE) ---")
    results = run_cash_only_specs(panel)

    print(f"\nDuration: {(datetime.now() - t0).total_seconds():.1f}s")
    print()
    print("=" * 80)
    print("VERDICT")
    print("=" * 80)
    for r in results:
        m = r["meta"]
        target = "+0.231" if m["treatment"] == KEY_IV_BETA_UK else "+0.357"
        print(f"  {m['treatment']:12s} β = {m.get('beta', np.nan):+.4f}  (Campello {target})  "
              f"n = {m.get('n_obs', 0):,}  p_one = {m.get('p_one', np.nan):.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
