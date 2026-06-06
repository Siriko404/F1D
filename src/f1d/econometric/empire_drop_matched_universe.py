#!/usr/bin/env python3
"""Comparability check: run UncResCEO and CashRatio on the IDENTICAL sample.

The pooled drop test runs each DV on its own complete-case set -> UncRes on the
~29k call-quarter universe (residual only exists where there's a CEO Q&A), Cash on
the ~77k all-quarter universe. So the 'differential timing' (UncRes falls at announce,
cash falls at close) could be a SAMPLE artifact (different firms/quarters), not a real
within-firm timing split.

Fix: require UncResCEO AND CashRatio AND controls all non-missing -> one shared sample.
Run BOTH DVs on those exact rows. If cash still stays-high-at-GAP / drops-at-POST on the
UncRes universe, the timing split is real. If it weakens, the dissociation was an artifact.

Also prints the correct per-DV post-dropna bin counts (the pooled script printed
pre-dropna pops, ~2.4x inflated). Reuses _empire_drop_test helpers. Read-only; prints.
Run: python tmp/_drop_matched_universe.py
"""
from __future__ import annotations
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("_edt", Path(__file__).resolve().parent / "empire_drop_test.py")
edt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(edt)
CTRL, BINS = edt.CTRL, edt.BINS


def run_on(d: pd.DataFrame, dv: str) -> dict:
    dd = d.set_index(["gvkey", "cq"])
    f = f"{dv} ~ 1 + " + " + ".join(BINS) + " + " + " + ".join(CTRL) \
        + " + EntityEffects + TimeEffects"
    mod = PanelOLS.from_formula(f, data=dd, drop_absorbed=True).fit(
        cov_type="clustered", cluster_entity=True)
    par, se, pv, V = mod.params, mod.std_errors, mod.pvalues, mod.cov

    def one(n):
        b, p2 = float(par[n]), float(pv[n])
        return {"b": b, "se": float(se[n]), "p1": p2 / 2 if b > 0 else 1 - p2 / 2}

    def wald(i, j):
        diff = float(par[i] - par[j])
        var = float(V.loc[i, i] + V.loc[j, j] - 2 * V.loc[i, j])
        se_ = var ** 0.5
        t = diff / se_
        p2 = 2 * norm.sf(abs(t))
        return {"diff": diff, "t": t, "p1": p2 / 2 if diff > 0 else 1 - p2 / 2, "p2": p2}

    return {"bins": {b: one(b) for b in BINS if b in par.index},
            "pre1_gap": wald("PRE1", "GAP"), "pre1_post": wald("PRE1", "POST"),
            "n": int(mod.nobs)}


def main():
    p, s, m = edt.base_panel(), edt.sdc(), edt.manifest()
    for cap in (4, 8):
        edt.POST_CAP = cap
        q, n_tr = edt.build_event(p, s, m, s["pc"] >= 50)   # cash arm
        # ONE shared sample: both DVs + bins + ctrl all present
        need = ["UncResCEO", "CashRatio"] + BINS + CTRL
        d = q.replace([np.inf, -np.inf], np.nan).dropna(subset=need).copy()
        pops = {b: int(d[b].sum()) for b in BINS}
        print(f"\n###### CASH arm | +{cap} | SHARED universe N={len(d):,} "
              f"firms={d['gvkey'].nunique():,} (vs cash-only ~77k) ######")
        print(f"  post-dropna bin counts: " + "  ".join(f"{b}={pops[b]:,}" for b in BINS))
        for dv in ("UncResCEO", "CashRatio"):
            r = run_on(d, dv)
            print(f"  --- {dv} (N={r['n']:,}) ---")
            for b in BINS:
                if b in r["bins"]:
                    v = r["bins"][b]
                    print(f"      {b:5} b={v['b']:+.5f} se={v['se']:.5f} p1={v['p1']:.3f}")
            for k, lab in (("pre1_gap", "PRE1-GAP"), ("pre1_post", "PRE1-POST")):
                w = r[k]
                print(f"      DROP {lab} = {w['diff']:+.5f} t={w['t']:+.2f} "
                      f"p1={w['p1']:.3f} p2={w['p2']:.3f}")


if __name__ == "__main__":
    main()
