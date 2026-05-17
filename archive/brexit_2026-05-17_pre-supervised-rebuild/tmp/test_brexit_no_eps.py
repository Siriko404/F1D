#!/usr/bin/env python3
"""Test Brexit DiD WITHOUT consensus EPS control.

IBES coverage strips 5,409 of 7,060 cells (76% of loss). Test whether dropping
EPS control brings n closer to Campello 17,170 + improves significance.

Campello: 'Drop if missing CRSP and I/B/E/S controls' → he applies the filter,
yet retains 41,630 cells. We apply via dropna; lose more cells. Possibly his
IBES coverage was broader (different vintage / older paper period overlap).

Per Sina decision 2026-05-14 'Pragmatic 100%': test this sensitivity.
"""
from __future__ import annotations

import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, "src")

from f1d.econometric.run_h1_5_brexit_did import (  # type: ignore
    load_h1_panel, load_compustat_raw, load_brexit_builders, assemble_panel,
    MACRO_CONTROLS, FIRM_CONTROLS_LAG1, EPS_CONTROL_LAG1,
    KEY_IV_BETA_UK, WINDOW_START_YQ, WINDOW_END_YQ, _fit_one,
)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    root = Path.cwd()

    universe, _ = load_h1_panel(root)
    gvkeys_keep = set(universe["gvkey"].unique())
    raw_comp = load_compustat_raw(root, gvkeys_keep, WINDOW_START_YQ - 1, WINDOW_END_YQ)
    builders = load_brexit_builders(root)
    panel = assemble_panel(universe, raw_comp, builders)

    print("=" * 80)
    print("BREXIT EPS-DROP SENSITIVITY")
    print("=" * 80)
    print(f"{'Spec':40s} {'n':>7s} {'beta':>10s} {'se':>10s} {'t':>8s} {'p_one':>8s} {'r2w':>7s}")
    print("-" * 92)

    # Variant A: current spec (5 macros + 5 firm + EPS)
    exog_full = MACRO_CONTROLS + FIRM_CONTROLS_LAG1 + [EPS_CONTROL_LAG1, "Post_brexit"]
    _, meta = _fit_one(panel, "cash_brexit_dv", KEY_IV_BETA_UK, exog_full, "campello_exact")
    print(f"{'A: current (5 macro + 5 firm + EPS)':40s} {meta['n_obs']:>7,} {meta['beta']:>+10.4f} {meta['se']:>10.4f} {meta['t']:>8.3f} {meta['p_one']:>8.3f} {meta['r2_within']:>7.3f}")

    # Variant B: drop EPS
    exog_no_eps = MACRO_CONTROLS + FIRM_CONTROLS_LAG1 + ["Post_brexit"]
    _, meta = _fit_one(panel, "cash_brexit_dv", KEY_IV_BETA_UK, exog_no_eps, "campello_exact")
    print(f"{'B: drop EPS':40s} {meta['n_obs']:>7,} {meta['beta']:>+10.4f} {meta['se']:>10.4f} {meta['t']:>8.3f} {meta['p_one']:>8.3f} {meta['r2_within']:>7.3f}")

    # Variant C: macros only (drop ALL firm controls)
    exog_macro = MACRO_CONTROLS + ["Post_brexit"]
    _, meta = _fit_one(panel, "cash_brexit_dv", KEY_IV_BETA_UK, exog_macro, "campello_exact")
    print(f"{'C: macros only':40s} {meta['n_obs']:>7,} {meta['beta']:>+10.4f} {meta['se']:>10.4f} {meta['t']:>8.3f} {meta['p_one']:>8.3f} {meta['r2_within']:>7.3f}")

    # Variant D: no controls (treatment + FE only)
    _, meta = _fit_one(panel, "cash_brexit_dv", KEY_IV_BETA_UK, ["Post_brexit"], "campello_exact")
    print(f"{'D: treatment + Post + FE only':40s} {meta['n_obs']:>7,} {meta['beta']:>+10.4f} {meta['se']:>10.4f} {meta['t']:>8.3f} {meta['p_one']:>8.3f} {meta['r2_within']:>7.3f}")

    print()
    print(f"  Campello target: β = +0.231***  SE = 0.059  n = 17,170  R² = 0.21")
    return 0


if __name__ == "__main__":
    sys.exit(main())
