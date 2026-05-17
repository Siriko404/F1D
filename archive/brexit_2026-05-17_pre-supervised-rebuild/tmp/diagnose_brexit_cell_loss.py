#!/usr/bin/env python3
"""Diagnose cell-loss chain in Brexit DiD pipeline.

Per Sina decision 2026-05-14 "Pragmatic 100%": identify which control or filter
strips the most cells from the regression sample. Compare Wave 3 result
(n=7,104) against Campello's reported n=17,170.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "src")

from f1d.econometric.run_h1_5_brexit_did import (  # type: ignore
    load_h1_panel, load_compustat_raw, load_brexit_builders, assemble_panel,
    MACRO_CONTROLS, FIRM_CONTROLS_LAG1, EPS_CONTROL_LAG1,
    KEY_IV_BETA_UK, WINDOW_START_YQ, WINDOW_END_YQ,
)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    root = Path.cwd()

    print("=" * 80)
    print("DIAGNOSE: Brexit panel cell-loss chain")
    print("=" * 80)

    universe, _ = load_h1_panel(root)
    gvkeys_keep = set(universe["gvkey"].unique())
    raw_comp = load_compustat_raw(root, gvkeys_keep, WINDOW_START_YQ - 1, WINDOW_END_YQ)
    builders = load_brexit_builders(root)
    panel = assemble_panel(universe, raw_comp, builders)

    print(f"\nFull panel after assembly: {len(panel):,} cells ({panel['gvkey'].nunique():,} gvkeys)")

    # Restrict to HIGH_BETA_UK ∈ {0,1}
    df = panel[panel["HIGH_BETA_UK"].isin([0.0, 1.0])].copy()
    print(f"After HIGH_BETA_UK ∈ {{0,1}}: {len(df):,} cells ({df['gvkey'].nunique():,} gvkeys)")

    # NaN per column among regression inputs
    cols = ["cash_brexit_dv", KEY_IV_BETA_UK, "HIGH_BETA_UK", "Post_brexit"] + MACRO_CONTROLS + FIRM_CONTROLS_LAG1 + [EPS_CONTROL_LAG1]
    print(f"\nNaN count per column (in {len(df):,} HIGH_BETA_UK-restricted cells):")
    for c in cols:
        if c in df.columns:
            n_nan = df[c].isna().sum()
            pct = 100 * n_nan / len(df) if len(df) else 0
            print(f"  {c:30s} NaN={n_nan:>6,}  ({pct:5.1f}%)")
        else:
            print(f"  {c:30s} MISSING from panel")

    # Cumulative dropna by adding columns
    print("\nCumulative dropna (in order of adding column):")
    keep = df.copy()
    print(f"  start                          n={len(keep):>6,}")
    for c in cols:
        if c in keep.columns:
            before = len(keep)
            keep = keep.dropna(subset=[c])
            dropped = before - len(keep)
            print(f"  drop NaN {c:25s}  n={len(keep):>6,}  Δ={-dropped:>6,}")

    print(f"\nFinal cells after all dropna: {len(keep):,}")
    print(f"Campello target:               17,170")
    print(f"Gap:                           {17170 - len(keep):,} cells")

    # Cells-per-firm distribution
    n_cells_per_firm = keep.groupby("gvkey").size()
    print(f"\nCells per firm distribution in final sample:")
    print(f"  mean: {n_cells_per_firm.mean():.2f} (Campello implied: ~21)")
    print(f"  median: {n_cells_per_firm.median():.1f}")
    print(f"  min: {n_cells_per_firm.min()}, max: {n_cells_per_firm.max()}")
    print(f"  n unique firms in final sample: {len(n_cells_per_firm):,}")

    # Distribution of Qs per firm
    print(f"\n  firms with full 28 Qs: {(n_cells_per_firm == 28).sum():,}")
    print(f"  firms with ≥21 Qs (Campello avg): {(n_cells_per_firm >= 21).sum():,}")
    print(f"  firms with ≥12 Qs (Campello filter): {(n_cells_per_firm >= 12).sum():,}")
    print(f"  firms with <12 Qs: {(n_cells_per_firm < 12).sum():,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
