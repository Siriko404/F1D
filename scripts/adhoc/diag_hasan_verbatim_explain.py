"""Diagnostic: investigate why our Hasan-verbatim replication flipped sign.

Loads the same panel as run_h1_6_test5_full_compustat.py with current
Hasan-verbatim settings (--hasan18 --movers-only), then breaks down:

1. Treated +1/0/-1 distribution within the final 496-firm sample
2. Per-firm pre/post mean cash by Treated level (sign-flip diagnostic)
3. Sample size by year (window narrowing test)
4. Cashflow-formula-required data availability (which firms drop)

Writes a tabular report to stdout. No regression run.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import sys
sys.path.insert(0, "src")
from f1d.econometric.run_h1_6_test5_full_compustat import (
    build_full_compustat_panel,
    attach_redist_treatment,
    filter_hasan_18,
    filter_movers_only,
    HASAN_18_STATES,
)


def main():
    print("=" * 80)
    print("HASAN-VERBATIM SIGN-FLIP DIAGNOSTIC")
    print("=" * 80)

    root = Path(".").resolve()

    # Build panel + attach treatment (same as runner)
    panel = build_full_compustat_panel(root)
    panel = attach_redist_treatment(panel, root)

    # Restrict to treated-labelled
    panel = panel.dropna(subset=["Treated_redist"]).copy()
    print(f"\n[A] Treated-labelled panel rows: {len(panel):,} ({panel['gvkey'].nunique():,} firms)")

    # Apply Hasan-18 filter
    panel = filter_hasan_18(panel, root)
    print(f"[B] After Hasan-18: {len(panel):,} ({panel['gvkey'].nunique():,} firms)")

    # Apply movers-only
    panel = filter_movers_only(panel)
    print(f"[C] After movers-only: {len(panel):,} ({panel['gvkey'].nunique():,} firms)")

    # ── Treated +1/0/-1 distribution at firm level ──
    print("\n" + "=" * 80)
    print("[1] TREATED +1/0/-1 DISTRIBUTION WITHIN MOVERS")
    print("=" * 80)
    firm_treated = panel.groupby("gvkey")["Treated_redist"].first()
    n_pos = int((firm_treated == 1).sum())
    n_zero = int((firm_treated == 0).sum())
    n_neg = int((firm_treated == -1).sum())
    n_total = len(firm_treated)
    print(f"  Treated = +1:  {n_pos:,} firms ({n_pos/n_total*100:.1f}%)")
    print(f"  Treated =  0:  {n_zero:,} firms ({n_zero/n_total*100:.1f}%)")
    print(f"  Treated = -1:  {n_neg:,} firms ({n_neg/n_total*100:.1f}%)")
    print(f"  Total:         {n_total:,} firms")
    print(f"  Active (±1):   {n_pos+n_neg:,} firms ({(n_pos+n_neg)/n_total*100:.1f}%)")
    print(f"\n  Hasan benchmark: 941 movers, all with Treated label (+1/0/-1).")
    print(f"  If most of our 'movers' have Treated=0, identification weakens.")

    # ── Pre/post mean Cash by Treated level (sign-flip diagnostic) ──
    print("\n" + "=" * 80)
    print("[2] PRE/POST MEAN CASH BY TREATED LEVEL")
    print("=" * 80)
    panel["period"] = np.where(panel["year"] > 2011, "post", "pre")
    cash_table = (
        panel.groupby(["Treated_redist", "period"])["CashRatio"]
        .agg(["mean", "count"]).reset_index()
    )
    print(cash_table.to_string(index=False))

    # Compute simple DiD-like differences manually
    print("\n  Hand-calculated DiD-like differences:")
    for treated_val in (1.0, 0.0, -1.0):
        try:
            pre_mean = panel[
                (panel["Treated_redist"] == treated_val) &
                (panel["period"] == "pre")
            ]["CashRatio"].mean()
            post_mean = panel[
                (panel["Treated_redist"] == treated_val) &
                (panel["period"] == "post")
            ]["CashRatio"].mean()
            print(f"  Treated={treated_val:+.0f}:  pre={pre_mean:.4f}  post={post_mean:.4f}  Δ={post_mean-pre_mean:+.4f}")
        except Exception as e:
            print(f"  Treated={treated_val}: error {e}")

    # ── Sample size by year ──
    print("\n" + "=" * 80)
    print("[3] FIRM-QUARTER COUNT BY YEAR (window distribution)")
    print("=" * 80)
    yearly = panel.groupby("year").size().reset_index(name="n_obs")
    yearly["n_firms"] = panel.groupby("year")["gvkey"].nunique().values
    print(yearly.to_string(index=False))

    # ── Cashflow data availability ──
    print("\n" + "=" * 80)
    print("[4] CASHFLOW-FORMULA REQUIRED FIELDS NaN RATE")
    print("=" * 80)
    for col in ("CashRatio", "Leverage", "lnAssets", "TobinsQ", "Capex", "DivDummy",
                "RDSales", "CashFlowAt", "NWC", "Acquisition", "IndustrySigma"):
        if col not in panel.columns:
            continue
        n_nan = panel[col].isna().sum()
        pct = n_nan / len(panel) * 100
        print(f"  {col:18s}: NaN={n_nan:>7,} ({pct:>5.1f}%)")

    print("\n" + "=" * 80)
    print("DIAGNOSTIC DONE")
    print("=" * 80)


if __name__ == "__main__":
    main()
