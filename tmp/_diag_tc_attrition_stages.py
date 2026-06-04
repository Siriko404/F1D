"""Diagnostic: where do treated/control firm counts diverge in the market arm?

Tests Sina's hypothesis (2026-05-31): Campello's asymmetric 449/360 are unique
firms surviving the FULL filter chain (F10), not counts at tercile assignment
(F9, where equal-count terciles force symmetry = 478/478).

Reuses the EXACT runner machinery (run_h1_5_brexit_did) — same builders, same
calendar-lag, same statsum consensus — and reports unique treated/control firm
counts at each completeness gate:

  S0  assignment (step3 treated/control, in_step1)           [F9]
  S1  + present in step1 full-period panel
  S2  + CRSP control present (brexit_stock_return, lagged)
  S3  + IBES control present (cons_fwd statsum, lagged)       [≈ F10]
  S4  + all Compustat controls present (lagged)
  S5  + CASH DV present                                       [full estimation]

No fitting, no winsor (irrelevant to counts). Read-only. Prints a table.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "campello_rebuild"))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# Pull the runner's machinery verbatim.
import importlib.util
_rp = ROOT / "src" / "f1d" / "econometric" / "run_h1_5_brexit_did.py"
_rs = importlib.util.spec_from_file_location("_runner", _rp)
_runner = importlib.util.module_from_spec(_rs)
_rs.loader.exec_module(_runner)

from step7_fullpanel_hypothesis import (
    FIRM_BUILDERS, POST_Q, _build, _calendar_lag1, _latest,
)

_cash_dv_t8 = _runner._cash_dv_t8
_statsum_meanest_z = _runner._statsum_meanest_z
_load_market_treatment = _runner._load_market_treatment


def _counts(df: pd.DataFrame, mask: pd.Series) -> tuple[int, int]:
    sub = df[mask]
    t = int(sub[sub["HIGH_UK_EXPOSURE"] == 1]["gvkey"].nunique())
    c = int(sub[sub["HIGH_UK_EXPOSURE"] == 0]["gvkey"].nunique())
    return t, c


def main() -> None:
    print("=" * 70)
    print("MARKET ARM — T/C attrition by completeness gate (unique firms)")
    print("=" * 70)

    # --- S0: assignment ---
    mkt = _load_market_treatment()
    t0 = int((mkt.HIGH_UK_EXPOSURE == 1).sum())
    c0 = int((mkt.HIGH_UK_EXPOSURE == 0).sum())

    # --- build full-period panel exactly like the runner ---
    s1 = pd.read_parquet(_latest("step1_sample") / "sample.parquet",
                         columns=["gvkey", "cal_yr_qtr", "atq",
                                  "fic100_industry_id"])
    s1["gvkey"] = s1["gvkey"].astype(str).str.zfill(6)
    mkt2 = mkt.copy(); mkt2["gvkey"] = mkt2["gvkey"].astype(str).str.zfill(6)
    panel = s1.merge(mkt2[["gvkey", "HIGH_UK_EXPOSURE"]], on="gvkey", how="inner")
    panel["POST"] = panel["cal_yr_qtr"].isin(POST_Q).astype(int)

    df = panel.merge(_cash_dv_t8(), on=["gvkey", "cal_yr_qtr"], how="left")
    df = df[df["atq"] > 0].copy()
    df["log_assets"] = np.log(df["atq"])

    # firm controls (lagged 1Q) — same builders/order as runner
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

    # CRSP control = brexit_stock_return; Compustat ctrls = tobinsq/cf/sg/logassets
    crsp_col = "brexit_stock_return"
    compu_cols = [c for c in firm_cols if c != crsp_col]

    # --- gates (firm-quarter level; unique-firm count = >=1 surviving fq) ---
    in_panel = pd.Series(True, index=df.index)
    g_crsp = in_panel & df[crsp_col].notna()
    g_ibes = g_crsp & df["cons_fwd"].notna()
    g_compu = g_ibes & df[compu_cols].notna().all(axis=1)
    g_cash = g_compu & df["CASH"].notna()

    rows = [
        ("S0  assignment (step3, in_step1)            [F9]", t0, c0),
        ("S1  + in step1 full-period panel",          *_counts(df, in_panel)),
        ("S2  + CRSP ctrl present (stock_return)",     *_counts(df, g_crsp)),
        ("S3  + IBES ctrl present (cons_fwd)     [~F10]", *_counts(df, g_ibes)),
        ("S4  + all Compustat ctrls present",          *_counts(df, g_compu)),
        ("S5  + CASH DV present       [full estim.]",  *_counts(df, g_cash)),
    ]

    print(f"\n{'gate':<48} {'T':>6} {'C':>6}  {'T-C':>6}  dir")
    print("-" * 70)
    for label, t, c in rows:
        d = t - c
        direction = "T>C" if d > 0 else ("C>T" if d < 0 else "T=C")
        print(f"{label:<48} {t:>6,} {c:>6,}  {d:>+6}  {direction}")
    print("-" * 70)
    print(f"{'CAMPELLO target (F10 unique firms)':<48} "
          f"{449:>6,} {360:>6,}  {449-360:>+6}  T>C")
    print("\nNotes: S3 ~ Campello F10 (drop missing CRSP & IBES controls).")
    print("       Campello reports T>C (449>360). Watch the 'dir' column for")
    print("       where/if our asymmetry flips.")


if __name__ == "__main__":
    main()
