#!/usr/bin/env python3
"""Phase 3 final test — top-N=449 match (Campello count, not tercile).

Diagnostic: tests if F1D's gap is distribution-shape (tercile cuts too low)
vs sample-composition (firm-pool too wide).

If top-N=449 match closes the gap → distribution-shape (F1D top tercile = β≥0.53
is too generous; Campello's "top tercile" effectively cuts at β≥0.86 in their
tighter universe).

If still NS / β << +0.231 → sample composition is the real bottleneck.
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
    _fit_one,
    KEY_IV_BETA_UK,
    MACRO_CONTROLS,
    FIRM_CONTROLS_NAMES,
    FIRM_CONTROLS_LAG1,
    EPS_CONTROL_LAG1,
    WINDOW_START_YQ,
    WINDOW_END_YQ,
    FE_LADDER,
)
from run_brexit_compustat_universe import (  # type: ignore
    load_compustat_universe_panel,
    assemble_panel_compustat,
)


def build_topn_high_beta_uk(root: Path, n_treated: int = 449, n_control: int = 449) -> pd.DataFrame:
    """Match Campello sample size: top-N + bottom-N of nonneg β^UK."""
    bu_dir = get_latest_output_dir(
        root / "outputs" / "variables" / "brexit_treatment_beta_uk",
        required_file="beta_uk_per_firm.parquet",
    )
    df = pd.read_parquet(bu_dir / "beta_uk_per_firm.parquet")
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)
    nn = df[df["beta_uk"] >= 0].sort_values("beta_uk")
    print(f"  Nonneg β^UK pool: {len(nn):,}")
    bottom = nn.head(n_control)["gvkey"].tolist()
    top = nn.tail(n_treated)["gvkey"].tolist()
    print(f"  Bottom-{n_control}: β range [{nn.head(n_control)['beta_uk'].min():.4f}, {nn.head(n_control)['beta_uk'].max():.4f}]")
    print(f"  Top-{n_treated}: β range [{nn.tail(n_treated)['beta_uk'].min():.4f}, {nn.tail(n_treated)['beta_uk'].max():.4f}]")
    out = pd.DataFrame({"gvkey": list(bottom) + list(top),
                        "HIGH_BETA_UK": [0.0]*len(bottom) + [1.0]*len(top)})
    return out


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    t0 = datetime.now()
    root = Path.cwd()

    print("=" * 80)
    print("PHASE 3 FINAL: Compustat universe + Top-N=449 β^UK match (Campello count)")
    print("=" * 80)
    print()

    universe = load_compustat_universe_panel(root)
    gvkeys_keep = set(universe["gvkey"].unique())
    raw_comp = load_compustat_raw(root, gvkeys_keep, WINDOW_START_YQ - 1, WINDOW_END_YQ)
    builders = load_brexit_builders(root)

    topn = build_topn_high_beta_uk(root, n_treated=449, n_control=449)
    print(f"  Top-N override: {(topn['HIGH_BETA_UK']==1).sum()} treated + {(topn['HIGH_BETA_UK']==0).sum()} control")
    # Override beta_uk builder's HIGH_BETA_UK column. Keep beta_uk col for reference.
    bu_orig = builders["beta_uk"].drop(columns=["HIGH_BETA_UK"], errors="ignore")
    builders["beta_uk"] = bu_orig.merge(topn, on="gvkey", how="left")

    panel = assemble_panel_compustat(universe, raw_comp, builders)

    print("\n  --- Cash regression with top-N=449 match ---")
    exog_cols = MACRO_CONTROLS + FIRM_CONTROLS_LAG1 + [EPS_CONTROL_LAG1, "Post_brexit"]
    model, meta = _fit_one(panel, "cash_brexit_dv", KEY_IV_BETA_UK, exog_cols, "campello_exact")
    print(f"  DV=cash treat=DiD_BetaUK n={meta.get('n_obs',0):,} "
          f"beta={meta.get('beta',np.nan):+.4f} se={meta.get('se',np.nan):.4f} "
          f"p_one={meta.get('p_one',np.nan):.3f}")

    print(f"\nDuration: {(datetime.now() - t0).total_seconds():.1f}s")
    print()
    print("=" * 80)
    print("VERDICT")
    print("=" * 80)
    print(f"  Campello target:        β = +0.231***  (n = 17,170)")
    print(f"  Top-tercile verbatim:   β = +0.0334    (n = 14,568)  prior run")
    print(f"  Top-N=449 match:        β = {meta.get('beta',np.nan):+.4f}    (n = {meta.get('n_obs',0):,})  THIS RUN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
