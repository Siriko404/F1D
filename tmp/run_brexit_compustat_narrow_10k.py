#!/usr/bin/env python3
"""Phase 3 test #2 — narrow 10-K keyword tally on Compustat universe.

Builds HIGH_10K from narrow_total_count = total_count - n_uncertainty - n_uncertain
(brings F1D HIGH_10K from 2,847 → 994 per prior memory; Campello target 807).

Reuses Phase-3-test-#1 Compustat-universe panel, overrides only the
HIGH_10K treatment merge. Tests whether narrowing closes the 10-K-arm gap
(prior universe-only run produced β=+0.0091 ≈ zero).
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
    KEY_IV_10K,
    KEY_IV_BETA_UK,
    MACRO_CONTROLS,
    FIRM_CONTROLS_NAMES,
    FIRM_CONTROLS_LAG1,
    EPS_CONTROL_LAG1,
    WINDOW_START_YQ,
    WINDOW_END_YQ,
    POST_START_YQ,
    MIN_MV_OR_BA_MILLIONS,
    FE_LADDER,
)
from run_brexit_compustat_universe import (  # type: ignore
    load_compustat_universe_panel,
    assemble_panel_compustat,
)


def build_narrow_high_10k(root: Path) -> pd.DataFrame:
    """Compute HIGH_10K from total_count - n_uncertainty - n_uncertain."""
    base = root / "outputs" / "intermediate" / "brexit_10k_keyword_counts"
    latest = get_latest_output_dir(base, required_file="keyword_counts_per_filing.parquet")
    df = pd.read_parquet(latest / "keyword_counts_per_filing.parquet")
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)
    df = df.sort_values(["gvkey", "filing_date"], kind="stable").drop_duplicates(
        subset=["gvkey"], keep="last"
    ).reset_index(drop=True)

    df["narrow_total"] = df["total_count"] - df["n_uncertainty"] - df["n_uncertain"]
    high = pd.Series(np.nan, index=df.index)
    high[df["narrow_total"] > 5] = 1.0
    high[df["narrow_total"] == 0] = 0.0
    df["HIGH_10K"] = high
    n_t = int((df["HIGH_10K"] == 1).sum())
    n_c = int((df["HIGH_10K"] == 0).sum())
    n_mid = int(df["HIGH_10K"].isna().sum())
    print(f"  Narrow HIGH_10K: treated(>5)={n_t:,}; control(=0)={n_c:,}; mid(1-5,dropped)={n_mid:,}")
    print(f"  Campello target: treated=807; control=433")
    return df[["gvkey", "narrow_total", "HIGH_10K"]]


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    t0 = datetime.now()
    root = Path.cwd()

    print("=" * 80)
    print("PHASE 3 TEST #2: Compustat-universe + narrow 10-K keywords")
    print("=" * 80)
    print("  Narrow tally = total - n_uncertainty - n_uncertain (7 keywords kept)")
    print()

    universe = load_compustat_universe_panel(root)
    gvkeys_keep = set(universe["gvkey"].unique())
    raw_comp = load_compustat_raw(root, gvkeys_keep, WINDOW_START_YQ - 1, WINDOW_END_YQ)
    builders = load_brexit_builders(root)

    # Override treat_10k builder with narrow tally.
    narrow_10k = build_narrow_high_10k(root)
    builders["treat_10k"] = narrow_10k.rename(columns={"narrow_total": "total_count"})

    panel = assemble_panel_compustat(universe, raw_comp, builders)

    print("\n  --- Running cash specs with narrow 10-K (β^UK + 10-K) ---")
    results: List[Dict[str, Any]] = []
    col = 0
    for treatment in [KEY_IV_BETA_UK, KEY_IV_10K]:
        for fe in FE_LADDER:
            col += 1
            exog_cols = MACRO_CONTROLS + FIRM_CONTROLS_LAG1 + [EPS_CONTROL_LAG1, "Post_brexit"]
            model, meta = _fit_one(panel, "cash_brexit_dv", treatment, exog_cols, fe)
            meta["col"] = col
            results.append({"model": model, "meta": meta})
            print(f"  Col ({col:>2d}) treat={treatment:12s} n={meta.get('n_obs', 0):>6,} "
                  f"beta={meta.get('beta', np.nan):+.4f} se={meta.get('se', np.nan):.4f} "
                  f"p_one={meta.get('p_one', np.nan):.3f}")

    print(f"\nDuration: {(datetime.now() - t0).total_seconds():.1f}s")
    print()
    print("=" * 80)
    print("VERDICT")
    print("=" * 80)
    print(f"  Prior 10-K (full tally):  β=+0.0091 n=34,521  Campello +0.357***")
    for r in results:
        m = r["meta"]
        target = "+0.231" if m["treatment"] == KEY_IV_BETA_UK else "+0.357"
        print(f"  {m['treatment']:12s} β = {m.get('beta', np.nan):+.4f}  (Campello {target})  "
              f"n = {m.get('n_obs', 0):,}  p_one = {m.get('p_one', np.nan):.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
