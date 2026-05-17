#!/usr/bin/env python3
"""Sensitivity: top-N=449/449 vs Campello-absolute (0.68/0.28) on POST-SIC pool.

Per advisor 2026-05-14 8:00pm: SIC-pre-filter fix yields β=+0.117 (51% Campello)
with top-N=449/449 cuts at 0.72/0.22. Discriminating check: re-run with
Campello-verbatim absolute cuts 0.68/0.28 to verify classifier mode is
second-order. If β stable within ±0.02, lock top-N=449/449. If β moves
materially, switch.
"""
from __future__ import annotations

import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, "src")

from f1d.shared.variables.brexit_treatment_beta_uk import (  # type: ignore
    _load_sic_keep_gvkeys, _assign_terciles_nonneg, _assign_top_n_match,
)
from f1d.shared.path_utils import get_latest_output_dir
from f1d.econometric.run_h1_5_brexit_did import (  # type: ignore
    load_h1_panel, load_compustat_raw, load_brexit_builders, assemble_panel,
    MACRO_CONTROLS, FIRM_CONTROLS_LAG1, EPS_CONTROL_LAG1,
    KEY_IV_BETA_UK, WINDOW_START_YQ, WINDOW_END_YQ, _fit_one,
)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    root = Path.cwd()

    print("=" * 80)
    print("SENSITIVITY: classifier mode on POST-SIC pool")
    print("=" * 80)

    # Load latest beta_uk (already post-SIC top-N=449/449)
    bu_dir = get_latest_output_dir(
        root / "outputs" / "variables" / "brexit_treatment_beta_uk",
        required_file="beta_uk_per_firm.parquet",
    )
    bu = pd.read_parquet(bu_dir / "beta_uk_per_firm.parquet")
    print(f"  Loaded β^UK builder output: {len(bu):,} firms ({bu_dir.name})")

    # Post-SIC pool (Campello §1G universe)
    sic_keep = _load_sic_keep_gvkeys(root)
    bu_sic = bu[bu["gvkey"].astype(str).str.zfill(6).isin(sic_keep)].copy()
    print(f"  Post-SIC pool: {len(bu_sic):,} firms")
    nonneg = bu_sic[bu_sic["beta_uk"] >= 0]
    print(f"  Nonneg β^UK in post-SIC pool: {len(nonneg):,}")

    # Mode A: current — top-N=449/449
    high_topn, bp_topn = _assign_top_n_match(bu_sic["beta_uk"])
    n_top_topn = int((high_topn == 1).sum())
    n_bot_topn = int((high_topn == 0).sum())
    print(f"\n  [A] Top-N=449/449 cuts:")
    print(f"      top threshold: {bp_topn['top_threshold_beta_uk']:.4f}")
    print(f"      bot threshold: {bp_topn['bottom_threshold_beta_uk']:.4f}")
    print(f"      TREATED: {n_top_topn:,}; CONTROL: {n_bot_topn:,}")

    # Mode B: Campello-absolute 0.28/0.68
    high_abs, bp_abs = _assign_terciles_nonneg(bu_sic["beta_uk"], use_campello_absolute=True)
    n_top_abs = int((high_abs == 1).sum())
    n_bot_abs = int((high_abs == 0).sum())
    print(f"\n  [B] Campello-absolute 0.28/0.68 cuts:")
    print(f"      TREATED (β^UK > 0.68): {n_top_abs:,}")
    print(f"      CONTROL (β^UK < 0.28): {n_bot_abs:,}")

    # Build panel for each mode
    print(f"\n  Loading panel infrastructure (one-time)...")
    universe, _ = load_h1_panel(root)
    gvkeys_keep = set(universe["gvkey"].unique())
    raw_comp = load_compustat_raw(root, gvkeys_keep, WINDOW_START_YQ - 1, WINDOW_END_YQ)
    builders = load_brexit_builders(root)

    print(f"\n{'Mode':35s} {'n':>7s} {'beta':>10s} {'se':>10s} {'p_one':>8s}")
    print("-" * 75)

    for label, high_series, bu_subset in [
        ("[A] top-N=449/449 (current canonical)", high_topn, bu_sic),
        ("[B] Campello-absolute 0.28/0.68",       high_abs,  bu_sic),
    ]:
        # Inject HIGH into a copy of bu
        bu_copy = bu.copy()
        bu_copy["HIGH_BETA_UK"] = np.nan
        bu_copy.loc[bu_subset.index, "HIGH_BETA_UK"] = high_series.values
        builders_copy = dict(builders)
        builders_copy["beta_uk"] = bu_copy[["gvkey", "HIGH_BETA_UK"]]

        panel = assemble_panel(universe, raw_comp, builders_copy)
        exog = MACRO_CONTROLS + FIRM_CONTROLS_LAG1 + [EPS_CONTROL_LAG1, "Post_brexit"]
        _, meta = _fit_one(panel, "cash_brexit_dv", KEY_IV_BETA_UK, exog, "campello_exact")
        print(f"{label:35s} {meta['n_obs']:>7,} {meta['beta']:>+10.4f} {meta['se']:>10.4f} {meta['p_one']:>8.3f}")

    print()
    print(f"  Campello target:                     17,170    +0.2310     0.0590    <0.01")
    return 0


if __name__ == "__main__":
    sys.exit(main())
