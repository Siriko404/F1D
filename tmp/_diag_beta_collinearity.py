"""Is our 39%-negative β^UK driven by multicollinearity in eq-13?

eq-13: vol(firm) = a + b*vol(FTSE) + t1*vol(SP500) + t2*vol(FX).
vol(FTSE) and vol(SP500) co-move (global risk). If collinear, OLS can't
separate them and b=β^UK goes noisy/negative for many firms — even with
perfect data (user verified FTSE prices are sound).

Test: per firm, estimate β^UK under 4 specs and report the NEGATIVE fraction:
  S_full   : FTSE + SP500 + FX   (paper eq-13, our current)
  S_noSP   : FTSE + FX           (drop SP500)
  S_noctrl : FTSE only           (simple regression)
  S_FTSE_SP: FTSE + SP500        (drop FX)
Also report pairwise correlations of the 3 monthly vol series.

If negative-fraction collapses from ~39% (full) toward Campello's ~7% as
controls are removed, collinearity is the cause. Reuses step2 data loaders
verbatim (no drift). Read-only.
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

import step2_beta_uk as s2

MIN_MONTHS = s2.MIN_MONTHS_PER_FIRM


def _beta_negfrac(g: pd.DataFrame, xcols: list) -> tuple[float, int]:
    """Return (beta_on_ftse, nobs) for OLS vol_r ~ 1 + xcols; nan if rank-def."""
    y = g["vol_r"].to_numpy(float)
    X = np.column_stack([np.ones(len(g))] + [g[c].to_numpy(float) for c in xcols])
    n, k = X.shape
    if n < MIN_MONTHS or np.linalg.matrix_rank(X) < k:
        return (np.nan, n)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return (float(beta[1]), n)  # beta[1] = coef on vol_ftse (first xcol)


def main() -> None:
    print("Loading CRSP daily + market vols (reusing step2 loaders)...")
    fd = s2._firm_daily_returns()
    fd = fd[fd["RET"].notna() & (fd["RET"] > -1.0)]
    firm_vol = s2._monthly_vol(fd[["PERMNO", "ym", "RET"]], "RET", by=["PERMNO"]) \
        .rename(columns={"vol_RET": "vol_r"})
    mkt = s2._market_monthly_vol(fd)
    print(f"market months: {len(mkt)}")

    # --- collinearity of the 3 vol regressors ---
    print("\n=== monthly vol correlations (the collinearity check) ===")
    cc = mkt[["vol_ftse", "vol_sp500", "vol_fx"]].corr()
    print(cc.round(3).to_string())

    fm = firm_vol.merge(mkt, on="ym", how="inner")
    fm = s2._permno_month_to_gvkey(fm)
    pick = (fm.groupby(["gvkey", "PERMNO"]).size().reset_index(name="cnt")
              .sort_values("cnt", ascending=False)
              .drop_duplicates("gvkey", keep="first")[["gvkey", "PERMNO"]])
    fm = fm.merge(pick, on=["gvkey", "PERMNO"], how="inner")

    specs = {
        "S_full   FTSE+SP500+FX": ["vol_ftse", "vol_sp500", "vol_fx"],
        "S_noSP    FTSE+FX":      ["vol_ftse", "vol_fx"],
        "S_FTSE_SP FTSE+SP500":   ["vol_ftse", "vol_sp500"],
        "S_noctrl  FTSE only":    ["vol_ftse"],
    }
    results = {k: [] for k in specs}
    for gv, g in fm.groupby("gvkey", sort=False):
        for name, xcols in specs.items():
            b, n = _beta_negfrac(g, xcols)
            if np.isfinite(b):
                results[name].append(b)

    print("\n=== β^UK negative fraction by spec ===")
    print(f"  {'spec':<24} {'n_firms':>8} {'%neg':>7} {'mean':>7} {'median':>7}")
    print("  " + "-" * 56)
    for name, betas in results.items():
        b = np.array(betas)
        print(f"  {name:<24} {len(b):>8,} {100*(b<0).mean():>6.1f}% "
              f"{b.mean():>7.3f} {np.median(b):>7.3f}")
    print("\n  Campello implied: ~7% negative (89/1347).")
    print("  Read: does %neg collapse toward 7% as SP500/FX controls are dropped?")


if __name__ == "__main__":
    main()
