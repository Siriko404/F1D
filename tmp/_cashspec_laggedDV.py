#!/usr/bin/env python3
"""Sina's test: CashRatio is sticky -> add its own lag (Lagged_DV) so the
pre-announce coefficient tracks the CHANGE, not the level. Re-estimate the
cash-stock cash-build difference WITH vs WITHOUT CashRatio_lag, on both samples.

Caveat being tested empirically: the event study shows cash already elevated at
t-2 (+0.0065*), so the lag may be a BAD CONTROL that absorbs the build. Numbers
decide. Read-only; writes nothing to docs/."""
from __future__ import annotations
import importlib.util
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
warnings.filterwarnings("ignore")
from linearmodels.panel import PanelOLS
from scipy.stats import norm

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


emp = load("_emp", "scripts/gen_empire_did_table.py")
cs = load("_cs", "src/f1d/econometric/empire_cashspec_interaction.py")
CTRL = emp.CTRL

# build CashRatio_lag (true one-quarter within-firm lag) on the base panel
p = emp.base_panel().sort_values(["gvkey", "cq"]).copy()
p["CashRatio_lag"] = p.groupby("gvkey")["CashRatio"].shift(1)
prev_cq = p.groupby("gvkey")["cq"].shift(1)
p.loc[prev_cq != p["cq"] - 1, "CashRatio_lag"] = np.nan   # only consecutive-quarter lags
s, m = emp.sdc(), emp.manifest()
q, n_cash, n_stk = cs.build_pooled(p, s, m)


def run(dv, restrict_uncres, add_lag):
    need = [dv, "PreAnn_cash", "PreAnn_stock"] + CTRL + (["CashRatio_lag"] if add_lag else [])
    if restrict_uncres and "UncResCEO" not in need:
        need = ["UncResCEO"] + need
    d = q.replace([np.inf, -np.inf], np.nan).dropna(subset=need).copy()
    d = d.set_index(["gvkey", "cq"])
    extra = " + CashRatio_lag" if add_lag else ""
    f = f"{dv} ~ 1 + PreAnn_cash + PreAnn_stock + " + " + ".join(CTRL) + extra + " + EntityEffects + TimeEffects"
    mod = PanelOLS.from_formula(f, data=d, drop_absorbed=True).fit(cov_type="clustered", cluster_entity=True)
    par, se, pv, V = mod.params, mod.std_errors, mod.pvalues, mod.cov
    i, j = "PreAnn_cash", "PreAnn_stock"
    diff = float(par[i] - par[j])
    sed = float(V.loc[i, i] + V.loc[j, j] - 2 * V.loc[i, j]) ** 0.5
    pd2 = 2 * norm.sf(abs(diff / sed))
    lagc = float(par["CashRatio_lag"]) if add_lag and "CashRatio_lag" in par.index else None
    return {"n": int(mod.nobs), "cash": (float(par[i]), float(se[i]), float(pv[i])),
            "stock": (float(par[j]), float(se[j]), float(pv[j])),
            "diff": (diff, sed, pd2), "lagcoef": lagc}


def star(p2):
    return "***" if p2 < .01 else "**" if p2 < .05 else "*" if p2 < .10 else "ns"


def show(label, r):
    cb, cse, cp = r["cash"]; sb, sse, sp = r["stock"]; db, dse, dp = r["diff"]
    lc = f"  [lag coef={r['lagcoef']:+.3f}]" if r["lagcoef"] is not None else ""
    print(f"\n{label}  (N={r['n']:,}){lc}")
    print(f"   cash  : {cb:+.5f} (se {cse:.5f}) {star(cp)}")
    print(f"   stock : {sb:+.5f} (se {sse:.5f}) {star(sp)}  [2-tail]")
    print(f"   DIFF  : {db:+.5f} (se {dse:.5f}) p2={dp:.3f} {star(dp)}  <-- decider")


for samp, restrict in [("MATCHED (call universe)", True), ("FULL panel", False)]:
    print("=" * 74 + f"\nCashRatio cash-build  |  {samp}\n" + "=" * 74)
    show("  WITHOUT lagged DV (current spec)", run("CashRatio", restrict, add_lag=False))
    show("  WITH    lagged DV (Sina's spec) ", run("CashRatio", restrict, add_lag=True))
