#!/usr/bin/env python3
"""Phase 3 FINAL — Campello-sample-match Brexit DiD.

Replicates Campello et al. 2022 JFQA sample exactly:
- Compustat 2010Q1-2016Q4 quarterly
- Drop SIC 4900-4999 (utility) + 6000-6999 (financial)
- fic=USA AND loc=USA AND curcdq=USD (US-domestic only)
- Exchanges: NYSE (11) + AMEX (12) + NASDAQ (14)
- stko=0 (common stock only)
- $10M filter on mkvaltq AND atq
- 7 key vars non-NaN (atq, cheq, mkvaltq, oibdpq, saleq, prccq, cshoq)
- BALANCED panel: 28 quarters complete coverage per firm

Probe yielded 40,068 cells (vs Campello 41,630 — 96% match). Tests whether
sample-match recovers Campello β AND significance simultaneously.
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

import numpy as np
import pandas as pd

sys.path.insert(0, "src")
sys.path.insert(0, "tmp")

from f1d.shared.path_utils import get_latest_output_dir  # type: ignore
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
)
from run_brexit_compustat_universe import (
    assemble_panel_compustat,
)


def load_campello_sample_panel(root: Path, require_balanced: bool = True) -> pd.DataFrame:
    """Build Campello-exact sample selection."""
    import pyarrow.parquet as pq
    from datetime import datetime as _dt
    cpath = root / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
    print(f"  Loading Compustat with Campello filters: {cpath}")

    table = pq.read_table(
        cpath,
        columns=["gvkey", "datadate", "sic", "fic", "loc", "curcdq", "exchg", "stko",
                 "atq", "mkvaltq", "cheq", "oibdpq", "saleq", "prccq", "cshoq"],
        filters=[("datadate", ">=", _dt(2010, 1, 1)),
                 ("datadate", "<",  _dt(2017, 1, 1))],
    )
    df = table.to_pandas()
    df["datadate"] = pd.to_datetime(df["datadate"])
    df["cal_yr_qtr"] = (df["datadate"].dt.year * 10 + df["datadate"].dt.quarter).astype("int64")
    df["gvkey"] = df["gvkey"].astype(int).astype(str).str.zfill(6)
    for c in ["atq", "mkvaltq", "cheq", "oibdpq", "saleq", "prccq", "cshoq"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["sic_int"] = pd.to_numeric(df["sic"], errors="coerce")
    df["stko_n"] = pd.to_numeric(df["stko"], errors="coerce")

    pre = len(df)
    # Industry exclusions.
    df = df[(df["sic_int"] < 4900) | (df["sic_int"] > 4999)]
    df = df[(df["sic_int"] < 6000) | (df["sic_int"] > 6999)]
    # US-domestic only.
    df = df[(df["fic"] == "USA") & (df["loc"] == "USA") & (df["curcdq"] == "USD")]
    # Exchange filter.
    df = df[df["exchg"].isin([11, 12, 14])]
    # Common stock only.
    df = df[df["stko_n"] == 0]
    print(f"  Standard Compustat filters: {len(df):,} cells (dropped {pre - len(df):,})")

    # $10M filter.
    df = df[(df["mkvaltq"].fillna(0) >= MIN_MV_OR_BA_MILLIONS) & (df["atq"] >= MIN_MV_OR_BA_MILLIONS)]
    print(f"  $10M filter: {len(df):,} cells")
    # Require 7 key vars present.
    df = df.dropna(subset=["atq", "cheq", "mkvaltq", "oibdpq", "saleq", "prccq", "cshoq"])
    print(f"  7-key-var non-NaN: {len(df):,} cells | {df['gvkey'].nunique():,} gvkeys")

    if require_balanced:
        n_qtrs = df.groupby("gvkey")["cal_yr_qtr"].nunique()
        keep = n_qtrs[n_qtrs >= 28].index
        df = df[df["gvkey"].isin(keep)]
        print(f"  Balanced 28-Q panel: {len(df):,} cells | {df['gvkey'].nunique():,} gvkeys")
        print(f"  Campello sample target: 41,630 cells")

    df = df.sort_values(["gvkey", "cal_yr_qtr"], kind="stable").drop_duplicates(
        subset=["gvkey", "cal_yr_qtr"], keep="last"
    ).reset_index(drop=True)
    return df[["gvkey", "cal_yr_qtr", "sic_int"]]


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    t0 = datetime.now()
    root = Path.cwd()

    print("=" * 80)
    print("PHASE 3 FINAL: Campello-sample-match Brexit DiD")
    print("=" * 80)
    print()

    universe = load_campello_sample_panel(root, require_balanced=True)
    gvkeys_keep = set(universe["gvkey"].unique())
    raw_comp = load_compustat_raw(root, gvkeys_keep, WINDOW_START_YQ - 1, WINDOW_END_YQ)
    builders = load_brexit_builders(root)

    # IMPORTANT FIX: re-compute β^UK terciles WITHIN the balanced sample.
    # Original builder computed cuts on full 3,781-firm pool; under balanced
    # sample restriction, that biased the assignment.
    bu = builders["beta_uk"][["gvkey", "beta_uk"]].copy()
    bu_in_sample = bu[bu["gvkey"].isin(gvkeys_keep)]
    nn = bu_in_sample[bu_in_sample["beta_uk"] >= 0]["beta_uk"]
    if len(nn) >= 3:
        p33 = float(nn.quantile(1/3))
        p67 = float(nn.quantile(2/3))
        print(f"  In-sample β^UK terciles (nonneg n={len(nn)}): p33={p33:.4f} p67={p67:.4f}")
        high = pd.Series(np.nan, index=bu_in_sample.index)
        high[(bu_in_sample["beta_uk"] >= 0) & (bu_in_sample["beta_uk"] <= p33)] = 0.0
        high[(bu_in_sample["beta_uk"] >= 0) & (bu_in_sample["beta_uk"] >= p67)] = 1.0
        bu_in_sample = bu_in_sample.assign(HIGH_BETA_UK=high)
        n_t = int((bu_in_sample["HIGH_BETA_UK"]==1).sum())
        n_c = int((bu_in_sample["HIGH_BETA_UK"]==0).sum())
        print(f"  In-sample: TREATED={n_t} CONTROL={n_c}  Campello: 449/433")
    builders["beta_uk"] = bu_in_sample[["gvkey", "beta_uk", "HIGH_BETA_UK"]]

    panel = assemble_panel_compustat(universe, raw_comp, builders)
    print(f"  Post-assembly: {len(panel):,} cells | {panel['gvkey'].nunique():,} gvkeys")

    print()
    print("  --- Cash specs under Campello-exact FE ---")
    print(f"  {'Treatment':<14} {'n_obs':>7} {'r2':>7} {'beta':>10} {'se':>10} {'t':>8} {'p_two':>8} {'p_one':>8}")
    print("  " + "-" * 80)
    exog_cols = MACRO_CONTROLS + FIRM_CONTROLS_LAG1 + [EPS_CONTROL_LAG1, "Post_brexit"]
    for treatment in [KEY_IV_BETA_UK, KEY_IV_10K]:
        model, meta = _fit_one(panel, "cash_brexit_dv", treatment, exog_cols, "campello_exact")
        b = meta.get('beta', np.nan); se = meta.get('se', np.nan); t = meta.get('t', np.nan)
        p1 = meta.get('p_one', np.nan); p2 = meta.get('p_two', np.nan)
        r2 = meta.get('r2', np.nan); n = meta.get('n_obs', 0)
        print(f"  {treatment:<14} {n:>7,} {r2:>7.4f} {b:>+10.4f} {se:>10.4f} {t:>8.3f} {p2:>8.3f} {p1:>8.3f}")

    print(f"\nDuration: {(datetime.now() - t0).total_seconds():.1f}s")
    print()
    print("=" * 80)
    print("CAMPELLO TARGETS (Table 8)")
    print("=" * 80)
    print("  DiD_BetaUK   β = +0.231***  SE 0.059  n = 17,170  R² = 0.21")
    print("  DiD_10K      β = +0.357***  SE 0.062  n = 24,195  R² = 0.24")
    return 0


if __name__ == "__main__":
    sys.exit(main())
