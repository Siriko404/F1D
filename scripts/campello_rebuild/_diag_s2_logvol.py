"""DIAG (read-only): test the LOG-VOL eq-13 spec vs the current LEVEL spec.

systematic-debugging Phase 3 — single hypothesis, one variable.

HYPOTHESIS
  Campello "Following Bloom (2014)"; Bloom's operational anchor is
  Baker&Bloom(2013), whose volatility series is taken IN LOGS (NLM relay,
  memory L26). step2_beta_uk.py logs the returns INSIDE vol (std of daily
  LOG returns) but regresses the resulting monthly sigma series in LEVELS
  (Y and the FTSE/SP500/FX vols all in levels). The textually-implied
  reading is a LOG-LOG eq-13: regress log(sigma_r) on log(sigma_FTSE),
  log(sigma_SP500), log(sigma_FX). This is a DIFFERENT ESTIMATOR (an
  elasticity), not a monotone squash of betaUK, so the prior
  "log REJECTED (monotonic)" verdict does NOT cover it.

A-PRIORI SUCCESS CRITERIA (declared before running — not post-hoc):
  Anchor 1 (counts, Campello §IV.A.2 L1850-54):
      n(betaUK > 0.68) ~= 449  AND  n(betaUK < 0.28) ~= 360
  Anchor 2 (precision):
      pos-fraction >= ~70%  (current level spec ~59%)
      AND %|t|>1.96 materially above 5%
  Anchor 3 (only checked downstream if 1&2 pass): cash delta-hat sign+sig.
  Spec hitting 3 but missing 1&2 = suspicious. 1&2 together = promote to
  step3->7 propagation. This script ONLY adjudicates anchors 1&2.

Reuses step2's EXACT data loaders + OLS (no estimator re-implementation).
Writes NOTHING; prints only. Does not perturb the pipeline's latest dir.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from step2_beta_uk import (  # noqa: E402
    BETA_UK_COL,
    N_MONTHS,
    build_macro_vol,
    firm_monthly_vol,
    latest_step1_sample,
    load_ccm,
    ols_beta_uk,
)

EPS = 1e-8                       # log floor guard; sigma >> EPS expected
CUT_HI, CUT_LO = 0.68, 0.28      # Campello absolute betaUK cuts (L1850-54)
TGT_HI, TGT_LO = 449, 360        # Campello realized treated / control


def _build_panel():
    """Faithful re-use of step2.main()'s Y/X construction."""
    s1 = latest_step1_sample()
    g = pq.read_table(s1, columns=["gvkey"]).to_pandas()
    step1_gvkeys = set(g["gvkey"].astype(str).str.zfill(6).unique())
    macro = build_macro_vol()
    ccm = load_ccm()
    fm = firm_monthly_vol(step1_gvkeys, ccm)
    wide = fm.pivot(index="gvkey", columns="year_month", values="vol_r")
    months = macro["year_month"].tolist()
    wide = wide.reindex(columns=months)
    balanced = wide.dropna(how="any")
    Xm = macro.set_index("year_month").loc[
        months, ["vol_ftse", "vol_sp500", "vol_fx"]].to_numpy(float)
    Y = balanced.to_numpy(float)
    return balanced.index.to_numpy(), Y, Xm, macro


def _corr_vif(Xm: np.ndarray, label: str) -> None:
    df = pd.DataFrame(Xm, columns=["ftse", "sp500", "fx"])
    print(f"  [{label}] design corr:")
    print(df.corr().round(3).to_string().replace("\n", "\n   "))

    def vif(d, c):
        y = d[c].to_numpy()
        Z = np.column_stack([np.ones(len(d)), d.drop(columns=[c]).to_numpy()])
        coef, *_ = np.linalg.lstsq(Z, y, rcond=None)
        r2 = 1 - ((y - Z @ coef) ** 2).sum() / ((y - y.mean()) ** 2).sum()
        return float("inf") if r2 >= 1 else 1.0 / (1.0 - r2)

    vs = "  ".join(f"VIF[{c}]={vif(df, c):.2f}" for c in df.columns)
    Xs = (df - df.mean()) / df.std()
    print(f"  [{label}] {vs}  cond(std)={np.linalg.cond(Xs.to_numpy()):.2f}")


def _report(label: str, b: np.ndarray, se: np.ndarray) -> None:
    b = pd.Series(b)
    t = (pd.Series(b) / pd.Series(se)).abs()
    n = len(b)
    n_hi = int((b > CUT_HI).sum())
    n_lo = int((b < CUT_LO).sum())
    nn = b[b >= 0]
    p33 = nn.quantile(1 / 3) if len(nn) else float("nan")
    p67 = nn.quantile(2 / 3) if len(nn) else float("nan")
    # nonneg EQUAL-WIDTH terciles (resolved D1 mechanism) for consistency
    if len(nn):
        lo_w, hi_w = nn.min(), nn.max()
        w = (hi_w - lo_w) / 3.0
        ew_lo, ew_hi = lo_w + w, lo_w + 2 * w
        ew_treated = int((nn >= ew_hi).sum())
        ew_control = int((nn <= ew_lo).sum())
    else:
        ew_treated = ew_control = 0
    print(f"\n=== {label}  (n={n}) ===")
    print(f"  beta: mean={b.mean():.4f} sd={b.std():.4f} "
          f"min={b.min():.3f} max={b.max():.3f}")
    print(f"  q10={b.quantile(.1):.3f} q25={b.quantile(.25):.3f} "
          f"q50={b.quantile(.5):.3f} q75={b.quantile(.75):.3f} "
          f"q90={b.quantile(.9):.3f}")
    print(f"  pos-fraction = {(b >= 0).mean()*100:.1f}%   "
          f"neg = {(b < 0).sum()} ({(b < 0).mean()*100:.1f}%)")
    print(f"  precision: median|t|={t.median():.3f}  "
          f"%|t|>1.65={ (t > 1.65).mean()*100:.1f}%  "
          f"%|t|>1.96={ (t > 1.96).mean()*100:.1f}%")
    print(f"  ANCHOR-1 absolute cuts {CUT_HI}/{CUT_LO}: "
          f"n(b>{CUT_HI})={n_hi}  n(b<{CUT_LO})={n_lo}   "
          f"[target ~{TGT_HI}/~{TGT_LO}]")
    print(f"  ANCHOR-1b nonneg equal-width tercile: "
          f"treated={ew_treated} control={ew_control}")
    print(f"  (nonneg quantile p33={p33:.4f} p67={p67:.4f})")


def main() -> None:
    print("DIAG s2 log-vol — LOG-LOG eq-13 vs current LEVEL eq-13\n")
    gvk, Y, Xm, macro = _build_panel()
    print(f"balanced-{N_MONTHS} firms: {len(gvk):,}")
    print(f"sigma floor check: min(Y)={Y.min():.3e} "
          f"min(Xmacro)={Xm.min():.3e}  (EPS={EPS:.0e}) "
          f"-> {'OK, EPS immaterial' if min(Y.min(), Xm.min()) > 1e-5 else 'WARN: near floor'}")

    # --- LEVEL baseline (current step2 spec) ---
    Xl = np.column_stack([np.ones(len(Xm)), Xm])
    b_lvl, se_lvl = ols_beta_uk(Y, Xl)
    _corr_vif(Xm, "LEVEL")
    _report("LEVEL  (current spec — baseline)",
            b_lvl[:, BETA_UK_COL], se_lvl[:, BETA_UK_COL])

    # --- LOG-LOG variant (the one-variable change under test) ---
    Ylg = np.log(Y + EPS)
    Xmg = np.log(Xm + EPS)
    Xlg = np.column_stack([np.ones(len(Xmg)), Xmg])
    b_log, se_log = ols_beta_uk(Ylg, Xlg)
    _corr_vif(Xmg, "LOG")
    _report("LOG-LOG  (B&B 'volatility in logs' — HYPOTHESIS)",
            b_log[:, BETA_UK_COL], se_log[:, BETA_UK_COL])

    print("\n--- A-PRIORI VERDICT GUIDE (declared pre-run) ---")
    print("  PASS anchors 1&2  => propagate LOG-LOG step3->7, check delta-hat")
    print("  miss 1&2          => log-vol is NOT the recipe; next hypothesis")
    print("  Anchor1: n(b>0.68)~449 AND n(b<0.28)~360")
    print("  Anchor2: pos-frac>=~70% AND %|t|>1.96 materially >5%")


if __name__ == "__main__":
    main()
