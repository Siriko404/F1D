#!/usr/bin/env python3
"""The clean comparison Sina asked for. Pooled model (cash + stock pre-announce
dummies in ONE regression so the cash-stock difference is a formal Wald), run on:
  - MATCHED sample (UncResCEO and CashRatio both present, N~25.6k)  [= table 21]
  - FULL panel     (drop the UncResCEO restriction, N~67k)          [NEW column]
For CashRatio (the 'cause') on both samples, and UncResCEO (the 'effect', matched
only -- it needs UncRes present). EVERYTHING two-tailed, including the stock arm
(no one-tailed placebo star). The cash-stock difference is the number that decides
whether the cash-build is cash-specific. Read-only; writes nothing to docs/."""
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

p, s, m = emp.base_panel(), emp.sdc(), emp.manifest()
q, n_cash, n_stk = cs.build_pooled(p, s, m)


def star(p2):
    return "***" if p2 < .01 else "**" if p2 < .05 else "*" if p2 < .10 else " ns"


def run(dv, restrict_uncres):
    need = ["CashRatio", "PreAnn_cash", "PreAnn_stock"] + CTRL
    if restrict_uncres or dv == "UncResCEO":
        need = ["UncResCEO"] + need
    d = q.replace([np.inf, -np.inf], np.nan).dropna(subset=need).copy()
    d = d.set_index(["gvkey", "cq"])
    f = f"{dv} ~ 1 + PreAnn_cash + PreAnn_stock + " + " + ".join(CTRL) + " + EntityEffects + TimeEffects"
    mod = PanelOLS.from_formula(f, data=d, drop_absorbed=True).fit(cov_type="clustered", cluster_entity=True)
    par, se, pv, V = mod.params, mod.std_errors, mod.pvalues, mod.cov
    i, j = "PreAnn_cash", "PreAnn_stock"
    diff = float(par[i] - par[j])
    sed = float(V.loc[i, i] + V.loc[j, j] - 2 * V.loc[i, j]) ** 0.5
    pd2 = 2 * norm.sf(abs(diff / sed))
    return {
        "n": int(mod.nobs),
        "cash": (float(par[i]), float(se[i]), float(pv[i])),
        "stock": (float(par[j]), float(se[j]), float(pv[j])),
        "diff": (diff, sed, pd2),
    }


def show(label, r):
    cb, cse, cp = r["cash"]
    sb, sse, sp = r["stock"]
    db, dse, dp = r["diff"]
    print(f"\n{label}   (N={r['n']:,})")
    print(f"   cash  pre-announce : {cb:+.5f}  (se {cse:.5f})  p2={cp:.3f} {star(cp)}")
    print(f"   stock pre-announce : {sb:+.5f}  (se {sse:.5f})  p2={sp:.3f} {star(sp)}   [TWO-TAILED]")
    print(f"   CASH - STOCK (diff): {db:+.5f}  (se {dse:.5f})  p2={dp:.3f} {star(dp)}   <-- the decider")


print("=" * 80)
print("THE 'CAUSE' : CashRatio cash-build, two samples")
print("=" * 80)
show("CashRatio  | MATCHED (UncRes present, = table 21)", run("CashRatio", restrict_uncres=True))
show("CashRatio  | FULL panel (UncRes restriction DROPPED)", run("CashRatio", restrict_uncres=False))

print("\n" + "=" * 80)
print("THE 'EFFECT': UncResCEO uncertainty, matched only (needs UncRes present)")
print("=" * 80)
show("UncResCEO  | MATCHED", run("UncResCEO", restrict_uncres=True))
